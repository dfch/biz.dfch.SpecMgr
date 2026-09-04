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

"""feat-27-validation Task 4.1 (REQ-007/ACC-005): end-to-end regression tests for the two known
triggers that motivated this feature.

1. **GitHub issue #27**'s own reproduction body: a bare ``<domain>``-style token in a `tsk`
   checklist item, parsed as raw HTML by markdown-it. The body used below is the issue's own
   minimal repro code block, verbatim (fetched via ``gh issue view 27 --json body``) -- only the
   trailing ``## Recent Updates`` entry's body text ("repro") is exactly as the reporter wrote
   it; nothing here is paraphrased.
2. **feat-7 Task 0.29**'s trigger: a `Recent Updates` entry paragraph that wraps onto a
   continuation line starting with ``+``. feat-7's own README (Background, Task 0.29) quotes
   only the literal fragment ``"+ group-block style as final..."`` from the original TSK
   document (id ``952d39e5-3b79-4389-bc71-a4fe8ca85cd3``) that first exposed this -- that
   document's full original text is not recorded anywhere in this repo's history, so the body
   below is a realistic reconstruction embedding that exact literal fragment as the offending
   continuation line, not the verbatim original document. This is called out here, not silently
   presented as a full verbatim repro.

Each trigger is reproduced through all three of the generic ``validate`` tool (``type="tsk"``,
disk-free dry run), ``create_tsk`` (create), and the generic ``update`` tool (``type="tsk"``,
whole-body replace of an existing document) -- the three surfaces GitHub issue #27 named as all
affected. Every test asserts the surfaced message contains the cause + fix-hint substrings the
plan's Design Notes describe (REQ-003), not a full exact-string pin -- that pinning job belongs
to ``tests/models/md/test_validation_error_baseline.py`` (Phase 1's Task 1.0/1.8). Since
feat-81-83-validation Phase 2, the generic ``validate`` tool never raises for a content-validation
failure -- it returns ``{valid: False, errors: [{message: str}]}`` instead, so the ``validate``-tool
tests below assert against ``result.errors[0].message`` rather than a raised exception.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.general.tools.validate import validate
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk

# ---------------------------------------------------------------------------
# Trigger 1: GitHub issue #27's own minimal repro body, verbatim (the issue's
# "Reproduction" section's first fenced code block).
# ---------------------------------------------------------------------------

_ISSUE_27_BODY = textwrap.dedent(
    """\
    # Minimal TSK repro

    - [ ] Task 1: item with <domain> angle brackets
    - [ ] Task 2: plain item

    ## Recent Updates

    ### 2026-08-27 - Created

    repro
    """
)

#: A valid seed document for the create-then-update flow below, using the issue's own
#: documented workaround ("Wrap the offending tokens in code spans") so `create_tsk` succeeds
#: and a subsequent `update` can then introduce the offending `_ISSUE_27_BODY` content.
_ISSUE_27_VALID_SEED_BODY = textwrap.dedent(
    """\
    # Minimal TSK repro

    - [ ] Task 1: item with `<domain>` angle brackets
    - [ ] Task 2: plain item

    ## Recent Updates

    ### 2026-08-27 - Created

    repro
    """
)

#: The bare-token cause + fix-hint substrings a caller needs to see (REQ-003), taken from
#: Phase 1's own enrichment of the raw-HTML rejection (`models/md/_markdown.py`).
_ISSUE_27_EXPECTED_SUBSTRINGS = (
    "raw HTML is not permitted",
    "html_inline '<domain>'",
    "wrap it in a code span",
    "write it as an HTML comment",
)

# ---------------------------------------------------------------------------
# Trigger 2: feat-7 Task 0.29's `+`-prefixed continuation-line trigger, reconstructed around
# the one literal fragment feat-7's own README preserves ("+ group-block style as final...").
# ---------------------------------------------------------------------------

_FEAT_7_TASK_0_29_BODY = textwrap.dedent(
    """\
    # Finish persisting the OpenCode + MCP PlantUML sequence diagram

    - [x] Task 1: Persist the sequence diagram to disk

    ## Recent Updates

    ### 2026-08-29 - Diagram persisted

    Persisted the diagram to disk, deciding to keep the diagram's own
    + group-block style as final layout for the sequence.
    """
)

#: A valid seed document for the create-then-update flow below: the same update-entry
#: paragraph, joined onto one line so it never starts a new CommonMark list.
_FEAT_7_TASK_0_29_VALID_SEED_BODY = textwrap.dedent(
    """\
    # Finish persisting the OpenCode + MCP PlantUML sequence diagram

    - [x] Task 1: Persist the sequence diagram to disk

    ## Recent Updates

    ### 2026-08-29 - Diagram persisted

    Persisted the diagram to disk, deciding to keep the diagram's own
    group-block style as final layout for the sequence.
    """
)

#: The stray-list-marker cause + fix-hint substrings a caller needs to see (REQ-003), taken from
#: Phase 1's own enrichment of the "text left over" message (`models/md/markdown_str.py`).
_FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS = (
    "text left over after processing all fields",
    "a line starting with '-', '*', or '+' begins a new",
    "CommonMark list",
    "remove the marker or indent the line",
)


class TempTskDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via ``SPECMGR_DOCS_DIR``."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestIssue27BareDomainTokenRegression(TempTskDirTestCase):
    """GitHub issue #27's own repro body, through the generic ``validate``/``create_tsk``/``update``."""

    def test_validate_surfaces_an_actionable_message(self) -> None:
        result = validate(type="tsk", content=_ISSUE_27_BODY)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        for substring in _ISSUE_27_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)

    def test_create_tsk_surfaces_an_actionable_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_tsk(_ISSUE_27_BODY)

        message = str(ctx.exception)
        for substring in _ISSUE_27_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)

    def test_update_surfaces_an_actionable_message(self) -> None:
        created = create_tsk(_ISSUE_27_VALID_SEED_BODY)

        with self.assertRaises(AssertionError) as ctx:
            update(id=created.id, type="tsk", content=_ISSUE_27_BODY)

        message = str(ctx.exception)
        for substring in _ISSUE_27_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)


class TestFeat7Task029StrayListMarkerRegression(TempTskDirTestCase):
    """feat-7 Task 0.29's `+`-prefixed continuation line, through the same three surfaces."""

    def test_validate_surfaces_an_actionable_message(self) -> None:
        result = validate(type="tsk", content=_FEAT_7_TASK_0_29_BODY)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        for substring in _FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)

    def test_create_tsk_surfaces_an_actionable_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_tsk(_FEAT_7_TASK_0_29_BODY)

        message = str(ctx.exception)
        for substring in _FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)

    def test_update_surfaces_an_actionable_message(self) -> None:
        created = create_tsk(_FEAT_7_TASK_0_29_VALID_SEED_BODY)

        with self.assertRaises(AssertionError) as ctx:
            update(id=created.id, type="tsk", content=_FEAT_7_TASK_0_29_BODY)

        message = str(ctx.exception)
        for substring in _FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)


if __name__ == "__main__":
    unittest.main()
