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

"""Tests for the ``create_feat`` ``@mcp.tool()`` wrapper (Task 2.3)."""

from __future__ import annotations

import tempfile
import textwrap
import threading
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1 import FeatDocument, parse_feat
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, README_FILENAME, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

_MINIMAL_BODY = textwrap.dedent(
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

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

# Structurally valid, but a field/cross-field failure: the AcceptanceCriterionItem's
# own computed field re-match against `ACC-\d{3}: ...` fails for this description.
_BAD_ACC_BODY = _MINIMAL_BODY.replace(
    "- [ ] ACC-001: Render time stays below 200ms.",
    "- [ ] Not a valid ACC item at all.",
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized feature sections.\n"


def _body_with_title(title: str) -> str:
    return _MINIMAL_BODY.replace("Example Widget", title)


class TempFeatDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the feature base dir via SPECMGR_FEAT_DIR.

    The configured base dir itself (``.../feat``) is **not** created by this
    fixture -- only its parent temp dir is -- so ``feat_base_dir().exists()``
    genuinely reflects whether ``create_feat``/``ensure_feat_base_dir`` has
    run yet, matching ``dec``'s own ``TempDecDirTestCase`` fixture shape.
    """

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))


class TestCreateFeat(TempFeatDirTestCase):
    """Tests for the create_feat tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_feat must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_feat(_MINIMAL_BODY)

        self.assertIsInstance(result, FeatDocument)
        self.assertEqual(result.frontmatter.id, "feat-0-example-widget")
        self.assertEqual(result.frontmatter.type, "feat")
        self.assertEqual(result.frontmatter.status, "planning")
        self.assertIsNotNone(result.frontmatter.created)
        self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
        self.assertRegex(
            result.frontmatter.created or "", r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$"
        )
        self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(result.body.text, "Feature: Example Widget")

    def test_writes_expected_folder_and_filename(self) -> None:
        """create_feat must write <base>/feat-{NNN}-{slug}/README.md."""
        result = create_feat(_MINIMAL_BODY)

        expected_path = feat_base_dir() / result.frontmatter.id / README_FILENAME
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_feat(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_feat(_MINIMAL_BODY)

        expected_path = feat_base_dir() / result.frontmatter.id / README_FILENAME
        on_disk = parse_feat(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.status, "planning")
        self.assertEqual(on_disk.body.text, "Feature: Example Widget")

    def test_id_defaults_to_feat_0_when_base_dir_is_empty(self) -> None:
        """The first feature created against an empty base dir must default to feat-0-<slug> (REQ-002)."""
        result = create_feat(_MINIMAL_BODY)
        self.assertEqual(result.frontmatter.id, "feat-0-example-widget")

    def test_id_number_stays_0_across_creates_with_distinct_titles(self) -> None:
        """Each default-id create_feat call must derive feat-0-<slug> -- no max+1 auto-increment (REQ-002)."""
        first = create_feat(_body_with_title("Widget One"))
        second = create_feat(_body_with_title("Widget Two"))

        self.assertEqual(first.frontmatter.id, "feat-0-widget-one")
        self.assertEqual(second.frontmatter.id, "feat-0-widget-two")

    def test_id_number_derivation_ignores_other_feat_folders(self) -> None:
        """Other feat-NNN-... folders (even at a would-be-colliding number) must not affect the
        default feat-0-<slug> id -- there is no more max+1 scanning to perturb (REQ-002)."""
        base_dir = feat_base_dir()
        for number in (1, 5):
            folder = base_dir / f"feat-{number}-placeholder"
            folder.mkdir(parents=True)
            (folder / README_FILENAME).write_text("not parseable, name is all that matters", encoding="utf-8")

        result = create_feat(_MINIMAL_BODY)

        self.assertEqual(result.frontmatter.id, "feat-0-example-widget")

    def test_slug_derivation_strips_the_feature_prefix(self) -> None:
        """The folder-name slug must be derived from the free-form title, not the literal 'Feature: ' prefix."""
        result = create_feat(_MINIMAL_BODY)
        self.assertTrue(result.frontmatter.id.endswith("example-widget"))
        self.assertNotIn("feature-example-widget", result.frontmatter.id)

    def test_creates_base_dir_if_missing(self) -> None:
        """create_feat must create the feature base directory if it does not exist yet."""
        self.assertFalse(feat_base_dir().exists())

        create_feat(_MINIMAL_BODY)

        self.assertTrue(feat_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_feat(_MALFORMED_BODY)

        self.assertFalse(feat_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (malformed ACC item) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_feat(_BAD_ACC_BODY)

        self.assertFalse(feat_base_dir().exists())


class TestCreateFeatWithExplicitId(TempFeatDirTestCase):
    """Tests for create_feat's optional caller-chosen ``id`` parameter (feat-48-feat-id Phase 2)."""

    def test_explicit_id_creates_exact_folder_and_id(self) -> None:
        """A caller-supplied id is used verbatim -- the title-derived slug plays no role (ACC-002)."""
        # The title's own slug ("zzz-unrelated-title") deliberately differs from the given id's
        # slug-looking suffix ("get-update"), to prove the given id really is used as-is.
        result = create_feat(_body_with_title("Zzz Unrelated Title"), id="feat-28-get-update")

        self.assertEqual(result.frontmatter.id, "feat-28-get-update")
        expected_path = feat_base_dir() / "feat-28-get-update" / README_FILENAME
        self.assertTrue(expected_path.exists())
        self.assertFalse((feat_base_dir() / "feat-28-zzz-unrelated-title").exists())

        on_disk = parse_feat(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.id, "feat-28-get-update")

    def test_invalid_explicit_id_raises_value_error_and_writes_nothing(self) -> None:
        """A malformed caller-supplied id raises ValueError before any lock/fs access (ACC-004)."""
        malformed_ids = ["not-a-valid-id", "feat-abc-slug", "Feat-1-Slug"]
        for malformed_id in malformed_ids:
            with self.subTest(malformed_id=malformed_id):
                with self.assertRaises(ValueError):
                    create_feat(_MINIMAL_BODY, id=malformed_id)

                self.assertFalse(feat_base_dir().exists())

    def test_explicit_id_collision_raises_and_leaves_existing_untouched(self) -> None:
        """A second create_feat call with an already-taken caller-supplied id raises FileExistsError,
        and the first document is left completely unchanged (ACC-003)."""
        first = create_feat(_body_with_title("First Title"), id="feat-28-get-update")
        expected_path = feat_base_dir() / "feat-28-get-update" / README_FILENAME
        before = expected_path.read_text(encoding="utf-8")

        with self.assertRaises(FileExistsError):
            create_feat(_body_with_title("Second Title"), id="feat-28-get-update")

        self.assertEqual(expected_path.read_text(encoding="utf-8"), before)
        on_disk = parse_feat(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.id, first.frontmatter.id)
        self.assertEqual(on_disk.body.text, "Feature: First Title")

    def test_defaulted_id_collision_raises(self) -> None:
        """When id is omitted, a pre-existing feat-0-<slug> folder for the same title-derived
        slug must also raise FileExistsError before any write (ACC-003)."""
        base_dir = feat_base_dir()
        colliding_folder = base_dir / "feat-0-example-widget"
        colliding_folder.mkdir(parents=True)

        with self.assertRaises(FileExistsError):
            create_feat(_MINIMAL_BODY)

        # Nothing beyond the pre-seeded folder itself must have been written.
        self.assertFalse((colliding_folder / README_FILENAME).exists())


class TestCreateFeatConcurrency(TempFeatDirTestCase):
    """Tests for create_feat's concurrent-create id-collision handling (ACC-002)."""

    def test_concurrent_creates_with_distinct_titles_never_collide(self) -> None:
        """Many threads calling create_feat at once with distinct titles (hence distinct default
        feat-0-<slug> ids) must all get distinct ids -- no max+1 auto-increment is involved anymore
        (REQ-002), but the pre-write existence check + global lock must still prevent any collision."""
        results: list[FeatDocument] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def worker(index: int) -> None:
            try:
                doc = create_feat(_body_with_title(f"Widget {index:02d}"))
            except BaseException as ex:  # noqa: BLE001 - captured for the assertion below
                with lock:
                    errors.append(ex)
                return
            with lock:
                results.append(doc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), 10)

        ids = [doc.frontmatter.id for doc in results]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids created: {ids}")
        self.assertTrue(all(id_.startswith("feat-0-widget-") for id_ in ids), ids)


if __name__ == "__main__":
    unittest.main()
