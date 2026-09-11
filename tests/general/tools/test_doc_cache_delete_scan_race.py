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

"""ACC-016/ACC-017/ACC-018 regression tests for the generic delete/scan race (feat-107-doc-cache Phase 8).

A separate, sibling file to ``test_doc_cache_structural.py`` (per Task 8.4's
own instructions) rather than folding these in: that file's own docstring
scopes it narrowly to ACC-008's *existence*-of-routing claim, while this
file covers three distinct races the generic ``delete`` tool's per-id-lock
(not whole-domain-lock) unlink can trigger against a concurrent, by-design
lock-free ``get_*``/``list_*`` call (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3).

**ACC-016**: ``general.tools._doc_paths.find_doc_path_by_id``'s per-file
scan loop must skip (not propagate) a ``FileNotFoundError`` raised by
``read_fn`` for a file that vanishes between the scan's directory-listing
snapshot and that file's own turn in the loop -- table-driven across the 11
non-``feat`` domains, exercising the generic function directly (mirroring
``test_doc_cache_structural.py``'s own "why ``find_doc_path_by_id`` directly"
rationale).

**ACC-017**: each of the 11 non-``feat`` domains' own
``<domain>.tools._io.load_by_id`` must translate a ``FileNotFoundError``
from its own second, independent ``read_<domain>(path)`` call (the one
right after ``find_<domain>_path`` already resolved and read the same path
once) into that domain's own ``<Domain>NotFoundError`` -- table-driven,
mirroring ``feat.tools._io.load_by_id``'s already-shipped ACC-014 test
(``tests/feat/tools/test__io.py``) exactly, including patching the ``_io``
module's own bound ``read_<domain>`` name (not ``_paths.py``'s separate,
unaffected reference) so only this second read is simulated to fail.

**ACC-018**: each of the 11 non-``feat`` domains' own ``list_<domain>`` tool
must silently omit (not report as a failed entry, not propagate an uncaught
error) a path whose ``README.md``/``*.md`` vanishes between the
directory-listing snapshot and this tool's own per-path read call --
table-driven here for the 11 non-``feat`` domains. ``feat``'s own coverage
of the identical case lives in
``tests/feat/tools/test_list_feat.py::TestListFeat::test_acc018_a_folder_vanishing_mid_scan_is_silently_omitted_not_reported_as_a_failed_entry``
(the renamed, rewritten former ACC-014 sub-test, per Task 8.2/ACC-018) --
not duplicated here, since ``feat``'s folder-per-document addressing needs
its own bespoke fixture shape (``create_feat``/``SPECMGR_FEAT_DIR``) that
would not fit this file's shared, flat-file fixture helpers.

**Fixture strategy**: identical to ``test_doc_cache_structural.py``'s own
-- each non-``feat`` domain's packaged *template* file
(``general.tools._packaged_data.read_packaged_text(domain, "template")``)
is reused as a guaranteed-valid document fixture, with only its
frontmatter ``id: ...`` line substituted via :func:`_with_id`.
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR, find_doc_path_by_id
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: The 11 non-``feat`` generic whole-body domains, all wired identically
#: through the shared ``general.tools._doc_paths.find_doc_path_by_id``.
_NON_FEAT_DOMAINS = ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs"]

#: Every ``*.md`` packaged template's frontmatter ``id: ...`` line, unquoted, own line.
_ID_LINE_PATTERN = re.compile(r"^id: .+$", re.MULTILINE)


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


def _io_module(domain: str) -> Any:
    """Import and return ``biz.dfch.specmgr.{domain}.tools._io``."""
    result = import_module(f"biz.dfch.specmgr.{domain}.tools._io")
    return result


def _paths_module(domain: str) -> Any:
    """Import and return ``biz.dfch.specmgr.{domain}.tools._paths``."""
    result = import_module(f"biz.dfch.specmgr.{domain}.tools._paths")
    return result


def _list_module(domain: str) -> Any:
    """Import and return ``biz.dfch.specmgr.{domain}.tools.list_{domain}``."""
    result = import_module(f"biz.dfch.specmgr.{domain}.tools.list_{domain}")
    return result


def _reset_all_non_feat_caches() -> None:
    for domain in _NON_FEAT_DOMAINS:
        getattr(_cache_module(domain), f"reset_{domain}_cache")()


class TestAcc016FindDocPathByIdSkipsAFileThatVanishesMidScan(unittest.TestCase):
    """ACC-016: a file vanishing between the directory-listing snapshot and its own turn in
    ``find_doc_path_by_id``'s per-file scan loop must not propagate an uncaught
    ``FileNotFoundError`` -- the scan must instead skip it and keep looking for the target id.
    """

    def setUp(self) -> None:
        _reset_all_non_feat_caches()

    def tearDown(self) -> None:
        _reset_all_non_feat_caches()

    def test_scan_skips_the_vanished_file_and_still_resolves_a_different_valid_id(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                cache_module = _cache_module(domain)
                real_read_fn = getattr(cache_module, f"read_{domain}")
                reconcile_fn = getattr(cache_module, f"reconcile_{domain}_cache")

                with tempfile.TemporaryDirectory() as tmp_dir:
                    base_dir = Path(tmp_dir)
                    template_text = read_packaged_text(domain, "template")
                    target = base_dir / "a-target.md"
                    victim = base_dir / "b-victim.md"
                    target.write_text(_with_id(template_text, "target-id"), encoding="utf-8")
                    victim.write_text(_with_id(template_text, "victim-id"), encoding="utf-8")

                    def _vanish_then_read(path: Path, _victim: Path = victim, _real: Any = real_read_fn) -> Any:
                        if path == _victim:
                            raise FileNotFoundError(f"simulated delete/scan race for {path}")
                        return _real(path)

                    resolved = find_doc_path_by_id(
                        base_dir, "target-id", _vanish_then_read, _get_id, reconcile_fn=reconcile_fn
                    )
                    self.assertEqual(resolved, target)


class TestAcc017LoadByIdTranslatesAVanishedSecondRead(unittest.TestCase):
    """ACC-017: each non-``feat`` domain's own ``load_by_id`` must translate a ``FileNotFoundError``
    from its own second, independent ``read_<domain>(path)`` call (the one performed right after
    ``find_<domain>_path`` already resolved and read the same path once) into that domain's own
    ``<Domain>NotFoundError`` -- mirroring ``feat.tools._io.load_by_id``'s already-shipped ACC-014
    test for the identical race.
    """

    def setUp(self) -> None:
        _reset_all_non_feat_caches()

    def tearDown(self) -> None:
        _reset_all_non_feat_caches()

    def test_second_read_racing_a_concurrent_delete_raises_the_domains_own_not_found_error(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                io_module = _io_module(domain)
                paths_module = _paths_module(domain)
                not_found_error = getattr(paths_module, f"{domain.capitalize()}NotFoundError")

                with tempfile.TemporaryDirectory() as tmp_dir:
                    base_dir = Path(tmp_dir)
                    template_text = read_packaged_text(domain, "template")
                    path = base_dir / "a.md"
                    path.write_text(_with_id(template_text, "target-id"), encoding="utf-8")

                    with mock.patch.object(io_module, f"read_{domain}", side_effect=FileNotFoundError("vanished")):
                        with self.assertRaises(not_found_error) as ctx:
                            io_module.load_by_id(base_dir, "target-id")
                    self.assertIn("could not be read", str(ctx.exception))


class TestAcc018ListDomainSilentlyOmitsAVanishedFile(unittest.TestCase):
    """ACC-018: each non-``feat`` domain's own ``list_<domain>`` tool must silently omit -- not
    report as a failed entry, not propagate an uncaught error -- a path whose ``read_<domain>``
    call raises ``FileNotFoundError`` because it vanished between the directory-listing snapshot
    and this tool's own per-path read call. ``feat``'s own coverage of the identical case lives in
    ``tests/feat/tools/test_list_feat.py``'s renamed, rewritten former ACC-014 sub-test (Task 8.2).
    """

    def setUp(self) -> None:
        _reset_all_non_feat_caches()

    def tearDown(self) -> None:
        _reset_all_non_feat_caches()

    def test_a_file_vanishing_mid_scan_is_silently_omitted_for_every_non_feat_domain(self) -> None:
        for domain in _NON_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                list_module = _list_module(domain)
                real_read_fn = getattr(list_module, f"read_{domain}")

                with tempfile.TemporaryDirectory() as tmp_dir:
                    docs_root = Path(tmp_dir)
                    with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(docs_root)}):
                        base_dir = docs_root / domain
                        base_dir.mkdir(parents=True)
                        template_text = read_packaged_text(domain, "template")
                        kept = base_dir / "a-kept.md"
                        vanished = base_dir / "b-vanished.md"
                        kept.write_text(_with_id(template_text, "kept-id"), encoding="utf-8")
                        vanished.write_text(_with_id(template_text, "vanished-id"), encoding="utf-8")

                        def _vanish_then_read(path: Path, _vanished: Path = vanished, _real: Any = real_read_fn) -> Any:
                            if path == _vanished:
                                raise FileNotFoundError(f"simulated delete/scan race for {path}")
                            return _real(path)

                        with mock.patch.object(list_module, f"read_{domain}", side_effect=_vanish_then_read):
                            list_fn = getattr(list_module, f"list_{domain}")
                            sut = list_fn()

                        self.assertEqual(sut.total, 1)
                        self.assertEqual(sut.error_count, 0)
                        ids = {summary.id for summary in sut.results}
                        self.assertEqual(ids, {"kept-id"})


if __name__ == "__main__":
    unittest.main()
