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

"""ACC-008 structural test: cache routing exists for every generic whole-body domain (feat-107-doc-cache Phase 4, Task 4.2).

ACC-008's own claim (``.specmgr/feat/feat-107-doc-cache/README.md``) is
narrow: "a structural test enumerates every generic whole-body domain and
confirms each one's ``read_<domain>`` helper and ``find_doc_path_by_id``
scan are routed through that domain's cache instance." This is deliberately
*not* a re-implementation of every domain's own ACC-001..ACC-006 suite (that
would be enormous and redundant with ``req``'s dedicated
``tests/req/tools/test_doc_cache_wiring.py``, Phase 3, Task 3.6) -- it only
targets the mechanical *existence* of the routing, table-driven across every
domain, so a future domain that forgets to wire its own ``_cache.py`` in is
caught by one shared test rather than needing its own bespoke wiring test.

**Fixture strategy.** Rather than hand-writing a minimal valid body per
domain (a different schema per domain), every non-``feat`` domain's own packaged
*template* file (``general.tools._packaged_data.read_packaged_text(domain,
"template")`` -- the same file backing that domain's ``get_<domain>_template``
tool) is reused as a guaranteed-valid document fixture, with only its
frontmatter ``id: ...`` line substituted via :func:`_with_id` -- ``id`` is a
free-form string on the shared ``models.md.frontmatter.MarkdownFrontmatter``
base (no format constraint at the pydantic-model level for any of these
domains), so substituting it is always safe and never risks
invalidating the rest of the document. ``feat`` is handled separately (its
own template's id ``must`` equal the containing folder name, and its
lifecycle is exercised through the real ``create_feat``/``set_feat_id``
tools instead of a bare temp-file write, since ``set_feat_id`` is the whole
point of testing it).

**Why ``find_doc_path_by_id`` directly, not each domain's own
``find_<domain>_path``.** Calling the generic function directly with a
domain's own ``read_<domain>``/``reconcile_<domain>_cache`` (rather than
going through e.g. ``uc.tools._paths.find_uc_path``) needs only a bare
``base_dir`` argument -- no ``SPECMGR_DOCS_DIR``/env-var setup per domain --
while still exercising the exact same routing every domain's own
``find_<domain>_path`` wraps around it.
"""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, README_FILENAME, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id
from biz.dfch.specmgr.general.tools._doc_paths import find_doc_path_by_id
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: The non-``feat`` generic whole-body domains, all wired identically
#: through the shared ``general.tools._doc_paths.find_doc_path_by_id``.
_NON_FEAT_DOMAINS = ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs"]

#: Every ``*.md`` packaged template's frontmatter ``id: ...`` line, unquoted, own line.
_ID_LINE_PATTERN = re.compile(r"^id: .+$", re.MULTILINE)

_FEAT_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: ACC-008 Structural Test Fixture

    ## Plan

    ### Overview

    A minimal, valid feature body used only by the ACC-008 structural cache-routing test.

    ### Requirements

    - REQ-001: Not a real requirement.

    ### Acceptance Criteria

    - [ ] ACC-001: Not a real acceptance criterion.

    ### Scope

    #### Included

    - Nothing real.

    #### Explicitly Out Of Scope

    - Everything else.

    ### Task List

    #### Phase 0: N/A

    - [ ] Task 0.1: Not a real task.

    ## Progress

    ### Current Status

    **As of 2026-09-10**: fixture only.

    ### Updates

    #### 2026-09-10 00:00:00.000Z - Created

    Fixture only.
    """
)


def _with_id(template_text: str, new_id: str) -> str:
    """Return ``template_text`` with its frontmatter ``id: ...`` line replaced by ``new_id``."""
    result, count = _ID_LINE_PATTERN.subn(f"id: {new_id}", template_text, count=1)
    assert count == 1, "expected exactly one 'id: ...' frontmatter line in the packaged template"
    return result


def _get_id(doc: Any) -> str | None:
    """A domain-agnostic ``get_id_fn`` for :func:`find_doc_path_by_id` -- every domain's frontmatter has ``.id``."""
    result = doc.frontmatter.id
    return result


def _cache_module(domain: str) -> Any:
    """Import and return ``biz.dfch.specmgr.{domain}.tools._cache``."""
    result = import_module(f"biz.dfch.specmgr.{domain}.tools._cache")
    return result


class TestAcc008NonFeatDomainsExposeTheExpectedCacheApi(unittest.TestCase):
    """ACC-008 (part 1): every one of the non-``feat`` domains' ``_cache.py`` exposes the expected API."""

    def test_every_domain_cache_module_has_the_four_expected_functions(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                module = _cache_module(domain)
                self.assertTrue(callable(getattr(module, f"read_{domain}", None)))
                self.assertTrue(callable(getattr(module, f"invalidate_{domain}_cache", None)))
                self.assertTrue(callable(getattr(module, f"reconcile_{domain}_cache", None)))
                self.assertTrue(callable(getattr(module, f"reset_{domain}_cache", None)))


class TestAcc008FeatCacheModuleExposesTheExpectedApi(unittest.TestCase):
    """ACC-008 (part 1, feat): ``feat.tools._cache`` exposes the expected API, plus the feat-only ``move_*``."""

    def test_feat_cache_module_has_the_five_expected_functions(self) -> None:
        module = _cache_module("feat")
        for attr in (
            "read_feat",
            "invalidate_feat_cache",
            "reconcile_feat_cache",
            "reset_feat_cache",
            "move_feat_cache_entry",
        ):
            with self.subTest(attr=attr):
                self.assertTrue(callable(getattr(module, attr, None)))


class TestAcc008ReadFnIsCacheBackedForEveryNonFeatDomain(unittest.TestCase):
    """ACC-008 (part 2): each non-``feat`` domain's ``read_<domain>`` is cache-backed (calls ``parse_<domain>`` once)."""

    def setUp(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            getattr(_cache_module(domain), f"reset_{domain}_cache")()

    def tearDown(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            getattr(_cache_module(domain), f"reset_{domain}_cache")()

    def test_second_read_of_an_unchanged_file_does_not_reinvoke_the_real_parse_fn(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                module = _cache_module(domain)
                read_fn: Callable[[Path], Any] = getattr(module, f"read_{domain}")
                real_parse_fn = getattr(module, f"parse_{domain}")

                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = Path(tmp_dir) / "a.md"
                    path.write_text(_with_id(read_packaged_text(domain, "template"), "id-1"), encoding="utf-8")

                    with mock.patch.object(module, f"parse_{domain}", wraps=real_parse_fn) as spy:
                        read_fn(path)
                        read_fn(path)
                        self.assertEqual(spy.call_count, 1)


class TestAcc008FindDocPathByIdReconcilesForEveryNonFeatDomain(unittest.TestCase):
    """ACC-008 (part 3): ``find_doc_path_by_id``'s scan routes through each non-``feat`` domain's own cache."""

    def setUp(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            getattr(_cache_module(domain), f"reset_{domain}_cache")()

    def tearDown(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            getattr(_cache_module(domain), f"reset_{domain}_cache")()

    def test_scan_warms_both_entries_then_reconcile_drops_the_deleted_one(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                module = _cache_module(domain)
                read_fn: Callable[[Path], Any] = getattr(module, f"read_{domain}")
                reconcile_fn: Callable[[Any], None] = getattr(module, f"reconcile_{domain}_cache")
                cache_singleton = module._cache  # pylint: disable=protected-access

                with tempfile.TemporaryDirectory() as tmp_dir:
                    base_dir = Path(tmp_dir)
                    template_text = read_packaged_text(domain, "template")
                    kept = base_dir / "kept.md"
                    dropped = base_dir / "dropped.md"
                    kept.write_text(_with_id(template_text, "id-1"), encoding="utf-8")
                    dropped.write_text(_with_id(template_text, "id-2"), encoding="utf-8")

                    # Scanning for "id-1" must still touch every candidate file (both are
                    # warmed), reconciling against the freshly materialized live listing first.
                    resolved = find_doc_path_by_id(base_dir, "id-1", read_fn, _get_id, reconcile_fn=reconcile_fn)
                    self.assertEqual(resolved, kept)
                    entries = cache_singleton._entries  # pylint: disable=protected-access
                    self.assertIn(kept, entries)
                    self.assertIn(dropped, entries)

                    # Bypass every specmgr tool: delete one file directly on disk.
                    dropped.unlink()

                    # The next scan must reconcile the cache against the live listing.
                    find_doc_path_by_id(base_dir, "id-1", read_fn, _get_id, reconcile_fn=reconcile_fn)
                    entries = cache_singleton._entries  # pylint: disable=protected-access
                    self.assertIn(kept, entries)
                    self.assertNotIn(dropped, entries)


class TestAcc008FeatFindPathByIdIsCacheBackedAndSetFeatIdMovesTheEntry(unittest.TestCase):
    """ACC-008 (part 4, feat): ``find_feat_path_by_id``'s own parse is cache-backed, and ``set_feat_id`` moves the entry."""

    def setUp(self) -> None:
        _cache_module("feat").reset_feat_cache()
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def tearDown(self) -> None:
        _cache_module("feat").reset_feat_cache()

    def test_find_feat_path_by_id_reads_through_the_cache(self) -> None:
        from biz.dfch.specmgr.feat.tools._paths import find_feat_path_by_id  # noqa: PLC0415

        create_feat(_FEAT_MINIMAL_BODY, id="feat-1-acc008-fixture")
        module = _cache_module("feat")
        real_parse_feat = module.parse_feat
        module.reset_feat_cache()  # discard create_feat's own write-path warming; start genuinely cold

        with mock.patch.object(module, "parse_feat", wraps=real_parse_feat) as spy:
            find_feat_path_by_id(self.feat_root, "feat-1-acc008-fixture")
            find_feat_path_by_id(self.feat_root, "feat-1-acc008-fixture")
            # find_feat_path_by_id's own single-file read is cache-backed (Task 4.1a's
            # double-parse fix): a second lookup of the same, unchanged file re-invokes
            # parse_feat zero additional times.
            self.assertEqual(spy.call_count, 1)

    def test_set_feat_id_moves_the_cache_entry_from_old_path_to_new_path(self) -> None:
        create_feat(_FEAT_MINIMAL_BODY, id="feat-1-acc008-rename-src")
        old_path = feat_base_dir() / "feat-1-acc008-rename-src" / README_FILENAME
        module = _cache_module("feat")
        cache_singleton = module._cache  # pylint: disable=protected-access
        self.assertIn(old_path, cache_singleton._entries)  # pylint: disable=protected-access

        set_feat_id("feat-1-acc008-rename-src", "feat-2-acc008-rename-dst")

        new_path = feat_base_dir() / "feat-2-acc008-rename-dst" / README_FILENAME
        entries = cache_singleton._entries  # pylint: disable=protected-access
        self.assertNotIn(old_path, entries)
        self.assertIn(new_path, entries)


if __name__ == "__main__":
    unittest.main()
