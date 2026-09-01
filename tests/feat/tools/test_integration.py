# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Live, end-to-end lifecycle exercise for the ``feat`` MCP tool surface (Phase 2, Task 2.5).

Unlike the per-tool unit tests elsewhere under ``tests/feat/tools/``, this
module drives the actual tool functions in a single realistic sequence --
 ``list_feat`` (empty) -> ``create_feat`` -> ``get_feat`` -> ``list_feat`` (1)
 -> ``update`` (whole-body) -> ``update`` (line-range) -> ``set_status``
 (``type="feat"``) -> ``get_feat`` (status changed) -> ``list_feat`` (status
 reflected) -> ``validate_feat`` -> ``delete`` (generic, ``type="feat"``) --
 against a real temporary feature base directory, confirming
 ACC-002/ACC-003/ACC-004's create->get->list->update->set_status->validate
 round-trip requirement with concrete evidence beyond the isolated
 per-tool tests. A separate test class
drives many concurrent ``create_feat`` calls to confirm the global
``feat_create_lock`` prevents two callers from ever deriving the same
``feat-NNN-...`` id (ACC-002).

Isolation follows the exact same pattern as ``test_create_feat.py``'s
``TempFeatDirTestCase``: a fresh ``tempfile.TemporaryDirectory()`` subfolder
is pointed to by ``SPECMGR_FEAT_DIR`` for the duration of each test, so
nothing is ever written to the real, developer-configured
``.specmgr/feat/`` (this very feature's own plan folder).

The packaged-example/template live check some other domains' own
integration tests carry is deliberately not ported here -- ``feat/data/``
does not exist until Phase 3 (see ``test_get_feat_example.py``/
``test_get_feat_template.py``'s own module docstrings).
"""

from __future__ import annotations

import tempfile
import textwrap
import threading
import unittest
from pathlib import Path
from unittest import mock

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1 import FeatDocument
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError, README_FILENAME, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.feat.tools.validate_feat import validate_feat
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

_INITIAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z — Paused for review

    Free-form prose describing what happened in this update.
    """
)

_REVISED_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    - REQ-002: The widget must be keyboard-navigable.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z — Paused for review

    Free-form prose describing what happened in this update.
    """
)


class TempFeatDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the feature base dir via SPECMGR_FEAT_DIR."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))


class TestFeatLifecycleIntegration(TempFeatDirTestCase):
    """Live, end-to-end lifecycle exercise, isolated to a temp base dir (ACC-003/ACC-004)."""

    def test_full_lifecycle_roundtrip(self) -> None:
        """list_feat -> create_feat -> get_feat -> list_feat -> update (whole-body) ->
        update (line-range) -> set_status -> get_feat -> list_feat -> validate_feat ->
        delete (generic, type="feat"), live."""
        # 0. list_feat: an empty base directory must list nothing.
        initial_page = list_feat()
        self.assertEqual(initial_page.total, 0)
        self.assertEqual(initial_page.results, [])

        # 1. create_feat: a freshly created document must be a FeatDocument in status
        #    "planning" (ACC-002/ACC-003: status is fixed, never caller-supplied), with
        #    its file on disk at <base>/feat-1-example-widget/README.md.
        created = create_feat(_INITIAL_BODY)
        self.assertIsInstance(created, FeatDocument)
        self.assertEqual(created.frontmatter.status, "planning")
        self.assertEqual(created.frontmatter.type, "feat")
        self.assertEqual(created.frontmatter.id, "feat-1-example-widget")
        self.assertEqual(created.frontmatter.created, created.frontmatter.updated)
        feat_id = created.frontmatter.id
        assert feat_id is not None
        expected_path = feat_base_dir() / feat_id / README_FILENAME
        self.assertTrue(expected_path.exists())

        # 2. get_feat: must reflect the freshly created document.
        fetched = get_feat(feat_id)
        self.assertEqual(fetched.frontmatter.id, feat_id)
        self.assertEqual(fetched.body.text, "Feature: Example Widget")
        self.assertIsNone(fetched.body.plan.dependencies)

        # 3. list_feat: must reflect the one created document, including the feat-only path field.
        page = list_feat()
        self.assertEqual(page.total, 1)
        self.assertEqual(len(page.results), 1)
        self.assertEqual(page.results[0].id, feat_id)
        self.assertEqual(page.results[0].status, "planning")
        self.assertEqual(page.results[0].title, "Example Widget")
        self.assertEqual(page.results[0].path, str(expected_path))

        # 4. update (type="feat", whole-body): must bump only `updated` (the same
        #    microsecond timestamp format every other domain uses) and preserve
        #    id/type/status/created/version (ACC-004).
        updated = update(feat_id, "feat", _REVISED_BODY)
        self.assertEqual(updated.frontmatter.id, created.frontmatter.id)
        self.assertEqual(updated.frontmatter.type, created.frontmatter.type)
        self.assertEqual(updated.frontmatter.created, created.frontmatter.created)
        self.assertEqual(updated.frontmatter.status, "planning")
        self.assertEqual(updated.frontmatter.version, created.frontmatter.version)
        self.assertRegex(updated.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$")
        self.assertEqual(len(updated.body.plan.requirements.items), 2)

        # 4b. update (type="feat", line-range): a single-line splice must round-trip
        #     through the raw body text exactly like every other domain's own range mode.
        lines = get_feat(feat_id, raw=True).splitlines()
        line_number = lines.index("Short description.") + 1
        update(feat_id, "feat", "Updated short description.", begin=line_number, end=line_number)
        after_range_update = get_feat(feat_id, raw=True).splitlines()
        self.assertEqual(after_range_update[line_number - 1], "Updated short description.")
        self.assertEqual(len(after_range_update), len(lines))

        # 5. set_status (type="feat"): only status/updated may change; the body (already
        #    revised in steps 4/4b) must be carried forward verbatim, untouched.
        in_progress = set_status(feat_id, "feat", "progress")
        self.assertEqual(in_progress.frontmatter.status, "progress")
        self.assertEqual(in_progress.frontmatter.id, updated.frontmatter.id)
        self.assertEqual(in_progress.frontmatter.created, updated.frontmatter.created)
        self.assertRegex(in_progress.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$")
        self.assertEqual(len(in_progress.body.plan.requirements.items), 2)

        # 6. get_feat: must reflect the latest on-disk state.
        fetched_after_status = get_feat(feat_id)
        self.assertEqual(fetched_after_status.frontmatter.status, "progress")
        self.assertEqual(fetched_after_status.frontmatter.id, feat_id)

        # 7. list_feat: must reflect the same document, with the current status/title.
        page_after_status = list_feat()
        matches = [s for s in page_after_status.results if s.id == feat_id]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].status, "progress")
        self.assertEqual(matches[0].title, "Example Widget")

        # 8. validate_feat (ACC-003): the on-disk file must validate as a complete
        #    document (full=True) and its body-only half must validate as body-only.
        on_disk_text = expected_path.read_text(encoding="utf-8")
        self.assertIs(validate_feat(on_disk_text, full=True), True)
        body_only = frontmatter.loads(on_disk_text).content  # type: ignore[union-attr]
        self.assertIs(validate_feat(body_only), True)

        # 9. delete (generic, type="feat"): a real hard delete via the generic tool -- the
        #    returned str must be the seeded <base>/<id>/ folder path, the whole folder must
        #    be gone, and a follow-up get_feat must raise FeatNotFoundError.
        deleted_path = delete(feat_id, type="feat")
        self.assertEqual(deleted_path, str(expected_path.parent))
        self.assertFalse(expected_path.parent.exists())
        with self.assertRaises(FeatNotFoundError):
            get_feat(feat_id)

    def test_set_status_rejects_status_outside_the_closed_four_set(self) -> None:
        """ACC-004: set_status (type="feat") must reject a status outside {planning, progress, review, done}."""
        created = create_feat(_INITIAL_BODY)
        expected_path = feat_base_dir() / created.frontmatter.id / README_FILENAME
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(created.frontmatter.id, "feat", "in-progress")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)

    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
        """ACC-003: validate_feat's body-only/full semantics -- invalid body fails (AssertionError);
        full=True requires a frontmatter block (ValueError)."""
        with self.assertRaises(AssertionError):
            validate_feat("# Title\n\nJust a paragraph, no recognized feature sections.\n")

        with self.assertRaises(ValueError):
            validate_feat(_INITIAL_BODY, full=True)


class TestCreateFeatConcurrencyIntegration(TempFeatDirTestCase):
    """ACC-002: concurrent-create NNN-collision simulation against the full tool surface."""

    def test_many_concurrent_create_feat_calls_never_collide(self) -> None:
        """20 threads hammering create_feat concurrently must all end up with distinct, valid ids."""
        results: list[FeatDocument] = []
        errors: list[BaseException] = []
        lock = threading.Lock()
        thread_count = 20

        def worker(index: int) -> None:
            body = _INITIAL_BODY.replace("Example Widget", f"Concurrent Widget {index:02d}")
            try:
                doc = create_feat(body)
            except BaseException as ex:  # noqa: BLE001 - captured for the assertion below
                with lock:
                    errors.append(ex)
                return
            with lock:
                results.append(doc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(thread_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), thread_count)

        ids = [doc.frontmatter.id for doc in results]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids created: {ids}")

        # Every created id must also be independently resolvable via list_feat/get_feat.
        page = list_feat(max_results=thread_count)
        self.assertEqual(page.total, thread_count)
        listed_ids = {summary.id for summary in page.results}
        self.assertEqual(listed_ids, set(ids))
        for id_ in ids:
            self.assertEqual(get_feat(id_).frontmatter.id, id_)


if __name__ == "__main__":
    unittest.main()
