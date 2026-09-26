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

"""Table-driven write-path cache-wiring tests for every whole-body domain (issue #123, the feat-107-doc-cache follow-up).

feat-107-doc-cache shipped the per-domain, content-hash-validated read cache
and wired it into every write path (post-create and post-update/post-
set_status/post-set_classification cache warming, eager delete invalidation,
and list reconcile-on-scan) across all 12 whole-body domains, but only
``req`` ever got tests proving that its own call sites actually fire
(``tests/req/tools/test_doc_cache_wiring.py``) -- the other 11 domains are
pinned only by the narrow, existence-of-routing structural test (``tests/
general/tools/test_doc_cache_structural.py``), which never executes a write.
A future refactor that silently drops one of those cache-wiring call sites
for any one of those 11 domains would therefore ship unnoticed. This file
closes that gap: one test class per wiring row type, table-driven across
every whole-body domain, so the exact domain row whose call site was dropped
is the one that fails.

**The seven row types.** create-warm (``create_<d>`` invokes the caller-
bound ``read_<d>`` with the just-written path), update-warm whole-body and
update-warm range-splice (the generic ``update`` invokes the caller-bound
``read_<d>`` with the written path, once per branch), set_status-warm (a
real, non-no-op transition per domain), set_classification-warm (a real
``internal`` write -- the packaged templates ship without a
``classification`` field, so setting one is a real write for every domain),
delete-invalidate (the generic ``delete`` invokes the caller-bound
``invalidate_<d>_cache`` with the deleted path AND the path is absent from
the domain's own ``_cache`` entries immediately after), and list-reconcile
(``list_<d>`` invokes the caller-bound ``reconcile_<d>_cache`` with the live
path listing). That is 12 domains x 7 row types = 84 subtest rows.

**Mocking discipline (REQ-007).** Each row patches the CALLER module's OWN
bound name of the cache helper (``read_<d>`` as bound into the domain's own
``create_<d>`` module, into ``general.tools.update``, into ``general.tools.
set_status``, and into ``general.tools.set_classification``;
``invalidate_<d>_cache`` as bound into ``general.tools.delete``;
``reconcile_<d>_cache`` as bound into the domain's own ``list_<d>`` module)
with ``mock.patch.object(..., wraps=<the very function bound there>)`` --
never the definition site in any ``_cache.py``/``_io.py`` -- so the real
write path executes end-to-end (the file is genuinely written, parsed, and
cached) while the spy records whether the documented call site fired,
exactly how often, and with which path.

**Fixture shapes (REQ-008).** Two distinct shapes, reusing the packaged
templates the way ``tests/general/tools/test_doc_cache_structural.py`` does:
the create rows pass each domain's own packaged template with its frontmatter
block stripped (``create_<d>`` builds its own frontmatter and rejects a
submitted one); every other row writes the FULL template with only its
frontmatter ``id`` line substituted by a fresh canonical lowercase-hex UUID
(the id shape the generic tools' ``validate_id`` requires) directly to disk
under the per-domain-subdir ``SPECMGR_DOCS_DIR`` layout, then invokes the
real tool by id. Every class resets every flat domain's own ``_cache``
singleton in BOTH ``setUp`` and ``tearDown`` (the feat classes reset the
feat one), so no test observes another test's cached state under
``pytest-xdist``.

**Flat/feat split (REQ-009).** The six flat table classes iterate the shared
``general.tools._domains.WHOLE_BODY_NO_FEAT_DOMAINS`` source of truth (never
a hand-listed tuple) with ``self.subTest(domain=...)``, so a future 13th
flat domain is picked up by construction; the six dedicated feat classes use
``SPECMGR_FEAT_DIR`` plus the real ``create_feat`` lifecycle instead,
mirroring the structural test's own flat/feat split.

**Per-row ``set_status`` targets.** Each row transitions the fixture from its
own starting status (the packaged template's frontmatter ``status`` --
``draft`` for the ten flat templates, ``open`` for ``rsk``; ``planning`` for
``feat``, which ``create_feat`` always writes) to the first member of the
domain's own closed status vocabulary (in the domain's own
``_ALLOWED_STATUSES`` source-literal order) other than that starting value --
derived in Phase 1 (Task 1.2). Every row re-checks the target against the
shared ``general.tools.set_status`` ``_ALLOWED_STATUSES_BY_TYPE`` mapping
plus the fixture's own status, so a vocabulary drift fails the row loudly
instead of sending a no-op (zero-spy-call) status.

**Per-domain H1 splice content.** The update range-splice rows replace the
body's line 1 (the H1 -- verified to be line 1 of every packaged template's
``body_text()``) with the domain's own valid H1 carrying a `` (updated)``
suffix: ``# {title} (updated)`` for the ten free-H1 flat domains,
``# System Requirements Specification: {title} (updated)`` for ``sysrs``
(its body model mandates the prefix -- the Phase-1-corrected fact in this
feature's Decisions Made entry), and ``# Feature: {title} (updated)`` for
``feat``.
"""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
import uuid
from importlib import import_module
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, README_FILENAME, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.models import InvalidStatusResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR, doc_base_dir
from biz.dfch.specmgr.general.tools._domains import FEAT, WHOLE_BODY_NO_FEAT_DOMAINS
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import _ALLOWED_STATUSES_BY_TYPE  # pylint: disable=protected-access
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update

#: The generic-tool caller modules whose OWN bound names the spies patch (REQ-007) -- resolved
#: via ``import_module`` because ``general.tools.__init__`` re-exports the tool FUNCTIONS under
#: the same names, so a plain ``from ...tools import update`` would bind the function, not the module.
_DELETE_MODULE = import_module("biz.dfch.specmgr.general.tools.delete")
_SET_CLASSIFICATION_MODULE = import_module("biz.dfch.specmgr.general.tools.set_classification")
_SET_STATUS_MODULE = import_module("biz.dfch.specmgr.general.tools.set_status")
_UPDATE_MODULE = import_module("biz.dfch.specmgr.general.tools.update")

#: Every packaged ``*.md`` template's frontmatter ``id: ...`` line, unquoted, on its own line.
_ID_LINE_PATTERN = re.compile(r"^id: .+$", re.MULTILINE)

#: Every packaged ``*.md`` template's frontmatter ``status: ...`` line, unquoted, on its own line.
_STATUS_LINE_PATTERN = re.compile(r"^status: (.+)$", re.MULTILINE)

#: The leading YAML frontmatter block of a packaged template (``---`` ... ``---``), inclusive.
_FRONTMATTER_BLOCK_PATTERN = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)

#: The H1 prefix a domain's own body model mandates on the H1 line (the empty default is the
#: free-H1 shape): ``sysrs`` and ``feat`` enforce their own literal prefix -- a bare
#: ``# {title}`` fails parsing for both (the ``sysrs`` entry is the Phase-1-corrected fact).
_H1_PREFIX_BY_DOMAIN: dict[str, str] = {
    FEAT: "Feature: ",
    "sysrs": "System Requirements Specification: ",
}

#: The per-domain set_status row target status: the first member of the domain's own closed
#: vocabulary (its ``_ALLOWED_STATUSES`` source-literal order) other than the fixture's own
#: starting status -- Phase 1 (Task 1.2) derivation, re-checked on every row (see the module
#: docstring). A future 13th domain must add its own entry here (and, if it mandates one, its
#: own ``_H1_PREFIX_BY_DOMAIN`` entry) -- the missing entry fails the row loudly, not silently.
_SET_STATUS_TARGETS_BY_DOMAIN: dict[str, str] = {
    "req": "proposed",
    "uc": "proposed",
    "tsk": "active",
    "qa": "active",
    "prb": "active",
    "gol": "proposed",
    "rsk": "mitigating",
    "dec": "proposed",
    "sop": "review",
    FEAT: "progress",
    "vcr": "progress",
    "sysrs": "review",
}

#: The set_classification rows' uniformly-real classification value.
_CLASSIFICATION_VALUE = "internal"

#: A minimal, valid feat body for the feat rows' fixtures (the feat counterpart of the flat
#: rows' packaged-template fixture source -- ``create_feat`` builds its own frontmatter).
_FEAT_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: Write-Path Cache-Wiring Test Fixture

    ## Plan

    ### Overview

    A minimal, valid feature body used only by the issue #123 write-path cache-wiring tests.

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

    **As of 2026-09-26**: fixture only.

    ### Updates

    #### 2026-09-26 00:00:00.000Z - Created

    Fixture only.
    """
)


def _with_id(template_text: str, new_id: str) -> str:
    """Return ``template_text`` with its frontmatter ``id: ...`` line replaced by ``new_id``."""
    result, count = _ID_LINE_PATTERN.subn(f"id: {new_id}", template_text, count=1)
    assert count == 1, "expected exactly one 'id: ...' frontmatter line in the packaged template"
    return result


def _template_body(domain: str) -> str:
    """Return the domain's packaged template with its leading frontmatter block stripped (the create rows' body fixture)."""
    result, count = _FRONTMATTER_BLOCK_PATTERN.subn("", read_packaged_text(domain, "template"), count=1)
    assert count == 1, f"expected a leading frontmatter block in the {domain} packaged template"
    return result.lstrip("\n")


def _template_status(domain: str) -> str:
    """Return the domain's packaged template's own frontmatter ``status`` (the non-create rows' fixture starting status)."""
    match = _STATUS_LINE_PATTERN.search(read_packaged_text(domain, "template"))
    assert match is not None, f"expected a 'status: ...' frontmatter line in the {domain} packaged template"
    result = match.group(1).strip()
    return result


def _cache_module(domain: str) -> Any:
    """Import and return ``biz.dfch.specmgr.{domain}.tools._cache``."""
    result = import_module(f"biz.dfch.specmgr.{domain}.tools._cache")
    return result


def _reset_cache(domain: str) -> None:
    """Clear ``domain``'s own module-level ``_cache`` singleton (test isolation under ``pytest-xdist``)."""
    getattr(_cache_module(domain), f"reset_{domain}_cache")()


def _changed_h1(domain: str, body: str) -> str:
    """Return a valid, visibly changed H1 line for ``domain``: the body's own H1 with a `` (updated)`` suffix."""
    h1_line = body.splitlines()[0]
    assert h1_line.startswith("# "), f"expected the body's first line to be the H1, got {h1_line!r}"
    prefix = _H1_PREFIX_BY_DOMAIN.get(domain, "")
    title = h1_line[2:].removeprefix(prefix)
    result = f"# {prefix}{title} (updated)"
    return result


def _body_with_changed_h1(domain: str, body: str) -> str:
    """Return ``body`` with its own H1 line replaced by :func:`_changed_h1`'s (the whole-body update rows' content)."""
    lines = body.splitlines()
    lines[0] = _changed_h1(domain, body)
    result = "\n".join(lines)
    return result


class _FlatDomainWiringTestCase(unittest.TestCase):
    """Shared setup for every flat-domain row class: per-domain cache resets plus the temp ``SPECMGR_DOCS_DIR``."""

    def setUp(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            _reset_cache(domain)
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def tearDown(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            _reset_cache(domain)

    def _write_flat_fixture(self, domain: str, fixture_id: str) -> Path:
        """Write ``domain``'s FULL packaged template (only its frontmatter ``id`` line substituted) to disk; return its path."""
        base_dir = doc_base_dir(domain)
        base_dir.mkdir(parents=True, exist_ok=True)
        path = base_dir / f"{domain}-{fixture_id}.md"
        path.write_text(_with_id(read_packaged_text(domain, "template"), fixture_id), encoding="utf-8")
        return path


class _FeatWiringTestCase(unittest.TestCase):
    """Shared setup for every feat row class: the feat cache reset plus the temp ``SPECMGR_FEAT_DIR``."""

    def setUp(self) -> None:
        _reset_cache(FEAT)
        self.feat_root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def tearDown(self) -> None:
        _reset_cache(FEAT)

    def _create_feat_fixture(self, fixture_id: str) -> Path:
        """Create the feat fixture through the real ``create_feat`` tool; return its ``README.md`` path."""
        created = create_feat(_FEAT_MINIMAL_BODY, id=fixture_id)
        self.assertEqual(created.id, fixture_id)
        path = feat_base_dir() / fixture_id / README_FILENAME
        self.assertTrue(path.exists())
        return path


class TestAcc001CreateWarmForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-001 (flat): a real ``create_<domain>`` invokes its caller-bound ``read_<domain>`` exactly once with the written path."""

    def test_create_invokes_the_caller_bound_read_exactly_once_with_the_written_path(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                create_module = import_module(f"biz.dfch.specmgr.{domain}.tools.create_{domain}")
                create_fn = getattr(create_module, f"create_{domain}")
                real_read = getattr(create_module, f"read_{domain}")

                with mock.patch.object(create_module, f"read_{domain}", wraps=real_read) as spy:
                    created = create_fn(_template_body(domain))

                doc_id = created.id
                assert isinstance(doc_id, str)  # every create tool always assigns an id
                written = self._sole_written_path(domain, doc_id)
                spy.assert_called_once_with(written)

    def _sole_written_path(self, domain: str, doc_id: str) -> Path:
        """The sole ``*.md`` carrying ``doc_id`` in the domain's base dir -- the create row's written path."""
        base_dir = doc_base_dir(domain)
        matches = [path for path in base_dir.glob("*.md") if doc_id in path.name]
        self.assertEqual(len(matches), 1)
        return matches[0]


class TestAcc002UpdateWarmForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-002 (flat, update): a real ``update`` invokes its caller-bound ``read_<domain>`` exactly once, on both paths."""

    def test_update_invokes_the_caller_bound_read_exactly_once_on_both_paths(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain, mode="whole-body"):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                whole_body = _body_with_changed_h1(domain, _template_body(domain))
                real_read = getattr(_UPDATE_MODULE, f"read_{domain}")

                with mock.patch.object(_UPDATE_MODULE, f"read_{domain}", wraps=real_read) as spy:
                    updated = update(id=fixture_id, type=domain, content=whole_body)

                self.assertEqual(updated.id, fixture_id)
                spy.assert_called_once_with(path)

            with self.subTest(domain=domain, mode="range-splice"):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                new_h1 = _changed_h1(domain, _template_body(domain))
                real_read = getattr(_UPDATE_MODULE, f"read_{domain}")

                with mock.patch.object(_UPDATE_MODULE, f"read_{domain}", wraps=real_read) as spy:
                    updated = update(id=fixture_id, type=domain, content=new_h1, offset=1, limit=1)

                self.assertEqual(updated.id, fixture_id)
                spy.assert_called_once_with(path)


class TestAcc003SetStatusWarmForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-002 (flat, set_status): a real, non-no-op ``set_status`` invokes its caller-bound ``read_<domain>`` exactly once."""

    def test_set_status_invokes_the_caller_bound_read_exactly_once(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                starting = _template_status(domain)
                target = _SET_STATUS_TARGETS_BY_DOMAIN[domain]
                self.assertIn(target, _ALLOWED_STATUSES_BY_TYPE[domain])
                self.assertNotEqual(target, starting)
                real_read = getattr(_SET_STATUS_MODULE, f"read_{domain}")

                with mock.patch.object(_SET_STATUS_MODULE, f"read_{domain}", wraps=real_read) as spy:
                    result = set_status(id=fixture_id, type=domain, status=target)

                self.assertNotIsInstance(result, InvalidStatusResult)
                self.assertEqual(result.status, target)
                spy.assert_called_once_with(path)


class TestAcc004SetClassificationWarmForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-002 (flat, set_classification): a real ``set_classification`` invokes its caller-bound ``read_<domain>`` exactly once."""

    def test_set_classification_invokes_the_caller_bound_read_exactly_once(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                real_read = getattr(_SET_CLASSIFICATION_MODULE, f"read_{domain}")

                with mock.patch.object(_SET_CLASSIFICATION_MODULE, f"read_{domain}", wraps=real_read) as spy:
                    result = set_classification(id=fixture_id, type=domain, classification=_CLASSIFICATION_VALUE)

                self.assertEqual(result.classification, _CLASSIFICATION_VALUE)
                spy.assert_called_once_with(path)


class TestAcc005DeleteInvalidatesForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-003 (flat): a real ``delete`` invokes its caller-bound ``invalidate_<domain>_cache`` exactly once and drops the entry."""

    def test_delete_invokes_the_caller_bound_invalidate_exactly_once_and_drops_the_entry(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                cache_module = _cache_module(domain)
                real_invalidate = getattr(_DELETE_MODULE, f"invalidate_{domain}_cache")

                with mock.patch.object(_DELETE_MODULE, f"invalidate_{domain}_cache", wraps=real_invalidate) as spy:
                    deleted = delete(id=fixture_id, type=domain)

                self.assertEqual(deleted, str(path))
                spy.assert_called_once_with(path)
                # The delete's own load_by_id scan read the target through the domain cache before the
                # unlink, so the entry exists at invalidation time: with the invalidate call site dropped,
                # it would remain, and this behavioral assertion -- beyond the spy count -- is what makes
                # the row bite (no pre-warming step is needed).
                entries = cache_module._cache._entries  # pylint: disable=protected-access
                self.assertNotIn(path, entries)
                self.assertFalse(path.exists())


class TestAcc006ListReconcilesForEveryFlatDomain(_FlatDomainWiringTestCase):
    """ACC-004 (flat): a real ``list_<domain>`` invokes its caller-bound ``reconcile_<domain>_cache`` exactly once, with the live listing."""

    def test_list_invokes_the_caller_bound_reconcile_exactly_once_with_the_live_listing(self) -> None:
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                fixture_id = str(uuid.uuid4())
                path = self._write_flat_fixture(domain, fixture_id)
                list_module = import_module(f"biz.dfch.specmgr.{domain}.tools.list_{domain}")
                list_fn = getattr(list_module, f"list_{domain}")
                real_reconcile = getattr(list_module, f"reconcile_{domain}_cache")

                with mock.patch.object(list_module, f"reconcile_{domain}_cache", wraps=real_reconcile) as spy:
                    result = list_fn()

                self.assertEqual(result.total, 1)
                # The fixture dir holds exactly one document, so the live path listing is that single path.
                spy.assert_called_once_with([path])


class TestAcc001CreateWarmForFeat(_FeatWiringTestCase):
    """ACC-001 (feat): a real ``create_feat`` invokes its caller-bound ``read_feat`` exactly once with the written ``README.md`` path."""

    def test_create_feat_invokes_the_caller_bound_read_exactly_once_with_the_written_path(self) -> None:
        with self.subTest(domain=FEAT):
            create_module = import_module("biz.dfch.specmgr.feat.tools.create_feat")
            real_read = getattr(create_module, "read_feat")
            fixture_id = "feat-0-ww-create"

            with mock.patch.object(create_module, "read_feat", wraps=real_read) as spy:
                created = create_feat(_FEAT_MINIMAL_BODY, id=fixture_id)

            self.assertEqual(created.id, fixture_id)
            written = feat_base_dir() / fixture_id / README_FILENAME
            spy.assert_called_once_with(written)


class TestAcc002UpdateWarmForFeat(_FeatWiringTestCase):
    """ACC-002 (feat, update): a real ``update`` (type='feat') invokes its caller-bound ``read_feat`` exactly once, on both paths."""

    def test_update_invokes_the_caller_bound_read_exactly_once_on_both_paths(self) -> None:
        with self.subTest(domain=FEAT, mode="whole-body"):
            path = self._create_feat_fixture("feat-0-ww-update-whole")
            whole_body = _body_with_changed_h1(FEAT, _FEAT_MINIMAL_BODY)
            real_read = getattr(_UPDATE_MODULE, "read_feat")

            with mock.patch.object(_UPDATE_MODULE, "read_feat", wraps=real_read) as spy:
                updated = update(id=path.parent.name, type=FEAT, content=whole_body)

            self.assertEqual(updated.id, path.parent.name)
            spy.assert_called_once_with(path)

        with self.subTest(domain=FEAT, mode="range-splice"):
            path = self._create_feat_fixture("feat-0-ww-update-range")
            new_h1 = _changed_h1(FEAT, _FEAT_MINIMAL_BODY)
            real_read = getattr(_UPDATE_MODULE, "read_feat")

            with mock.patch.object(_UPDATE_MODULE, "read_feat", wraps=real_read) as spy:
                updated = update(id=path.parent.name, type=FEAT, content=new_h1, offset=1, limit=1)

            self.assertEqual(updated.id, path.parent.name)
            spy.assert_called_once_with(path)


class TestAcc003SetStatusWarmForFeat(_FeatWiringTestCase):
    """ACC-002 (feat, set_status): a real, non-no-op ``set_status`` (planning -> progress) invokes its caller-bound ``read_feat`` once."""

    def test_set_status_invokes_the_caller_bound_read_exactly_once(self) -> None:
        with self.subTest(domain=FEAT):
            path = self._create_feat_fixture("feat-0-ww-set-status")
            starting = "planning"  # create_feat always writes planning (create_feat.py's own frontmatter construction)
            target = _SET_STATUS_TARGETS_BY_DOMAIN[FEAT]
            self.assertIn(target, _ALLOWED_STATUSES_BY_TYPE[FEAT])
            self.assertNotEqual(target, starting)
            real_read = getattr(_SET_STATUS_MODULE, "read_feat")

            with mock.patch.object(_SET_STATUS_MODULE, "read_feat", wraps=real_read) as spy:
                result = set_status(id=path.parent.name, type=FEAT, status=target)

            self.assertNotIsInstance(result, InvalidStatusResult)
            self.assertEqual(result.status, target)
            spy.assert_called_once_with(path)


class TestAcc004SetClassificationWarmForFeat(_FeatWiringTestCase):
    """ACC-002 (feat, set_classification): a real ``set_classification`` (type='feat') invokes its caller-bound ``read_feat`` exactly once."""

    def test_set_classification_invokes_the_caller_bound_read_exactly_once(self) -> None:
        with self.subTest(domain=FEAT):
            path = self._create_feat_fixture("feat-0-ww-set-classification")
            real_read = getattr(_SET_CLASSIFICATION_MODULE, "read_feat")

            with mock.patch.object(_SET_CLASSIFICATION_MODULE, "read_feat", wraps=real_read) as spy:
                result = set_classification(id=path.parent.name, type=FEAT, classification=_CLASSIFICATION_VALUE)

            self.assertEqual(result.classification, _CLASSIFICATION_VALUE)
            spy.assert_called_once_with(path)


class TestAcc005DeleteInvalidatesForFeat(_FeatWiringTestCase):
    """ACC-003 (feat): a real ``delete`` (type='feat') invokes its caller-bound ``invalidate_feat_cache`` exactly once and drops the entry."""

    def test_delete_invokes_the_caller_bound_invalidate_exactly_once_and_drops_the_entry(self) -> None:
        with self.subTest(domain=FEAT):
            path = self._create_feat_fixture("feat-0-ww-delete")
            cache_module = _cache_module(FEAT)
            real_invalidate = getattr(_DELETE_MODULE, "invalidate_feat_cache")

            with mock.patch.object(_DELETE_MODULE, "invalidate_feat_cache", wraps=real_invalidate) as spy:
                deleted = delete(id=path.parent.name, type=FEAT)

            # feat deletes the whole <base>/<id>/ folder; the cache entry is keyed by the README.md path.
            self.assertEqual(deleted, str(path.parent))
            spy.assert_called_once_with(path)
            # create_feat's own write-path warming populated the entry before the delete, so with the
            # invalidate call site dropped it would remain -- the behavioral assertion is what bites.
            entries = cache_module._cache._entries  # pylint: disable=protected-access
            self.assertNotIn(path, entries)
            self.assertFalse(path.exists())


class TestAcc006ListReconcilesForFeat(_FeatWiringTestCase):
    """ACC-004 (feat): a real ``list_feat`` invokes its caller-bound ``reconcile_feat_cache`` exactly once, with the live listing."""

    def test_list_invokes_the_caller_bound_reconcile_exactly_once_with_the_live_listing(self) -> None:
        with self.subTest(domain=FEAT):
            path = self._create_feat_fixture("feat-0-ww-list")
            list_module = import_module("biz.dfch.specmgr.feat.tools.list_feat")
            list_fn = getattr(list_module, "list_feat")
            real_reconcile = getattr(list_module, "reconcile_feat_cache")

            with mock.patch.object(list_module, "reconcile_feat_cache", wraps=real_reconcile) as spy:
                result = list_fn()

            self.assertEqual(result.total, 1)
            # The fixture dir holds exactly one feature folder, so the live path listing is that single path.
            spy.assert_called_once_with([path])


if __name__ == "__main__":
    unittest.main()
