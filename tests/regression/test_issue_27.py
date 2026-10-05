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

"""feat-27-validation Task 4.1 (REQ-007/ACC-005): end-to-end regression tests for the known
triggers that motivated this feature.

1. **GitHub issue #27**'s own reproduction body: a bare ``<domain>``-style token in a `tsk`
   checklist item, parsed as raw HTML by markdown-it. The body used below is the issue's own
   minimal repro code block, verbatim (fetched via ``gh issue view 27 --json body``) -- only the
   trailing ``## Recent Updates`` entry's body text ("repro") is exactly as the reporter wrote
   it; nothing here is paraphrased.
2. **feat-7 Task 0.29**'s trigger -- a ``+``-prefixed continuation line inside a `## Recent
   Updates` entry -- is **intentionally superseded** by feat-180-updates (GitHub issue #180):
   update/decision entry ``content`` now accepts any markdown, so that input is valid content
   and no longer an error; the former end-to-end tests for it were deleted (user-approved
   decision, 2026-10-02). The same actionable "text left over after processing all fields"
   message with the stray-list-marker hint remains pinned at engine level in
   ``tests/models/md/test_validation_error_baseline.py``
   (``test_list_field_leaves_a_stray_list_marker_line_unconsumed``).

The remaining trigger is reproduced through all three of the generic ``validate`` tool (``type="tsk"``,
disk-free dry run), ``create_tsk`` (create), and the generic ``update`` tool (``type="tsk"``,
whole-body replace of an existing document) -- the three surfaces GitHub issue #27 named as all
affected. Every test asserts the surfaced message contains the cause + fix-hint substrings the
plan's Design Notes describe (REQ-003), not a full exact-string pin -- that pinning job belongs
to ``tests/models/md/test_validation_error_baseline.py`` (Phase 1's Task 1.0/1.8). Since
feat-81-83-validation Phase 2, the generic ``validate`` tool never raises for a content-validation
failure -- it returns ``{valid: False, errors: [{message: str}]}`` instead, so the ``validate``-tool
tests below assert against ``result.errors[0].message`` rather than a raised exception. Since
feat-170 Phase 120 (Bug 2, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f), the generic ``update``
tool never raises for a content-validation failure either -- it returns the same non-raising
``ValidateResult`` shape (the single ``errors[].message`` capped at 300 chars exactly as
``validate``'s is), so the ``update``-tool tests below assert against ``result.errors[0].message``
as well.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
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

    ### 2026-08-27 00:00:00.000Z - Created

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

    ### 2026-08-27 00:00:00.000Z - Created

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
        """Since feat-170 Phase 120 (Bug 2), the generic ``update`` tool no longer raises for this
        content-validation failure -- it returns the non-raising ``ValidateResult`` whose message
        is capped exactly as ``validate``'s is, so assert against
        ``result.errors[0].message`` (the same shape as the ``validate`` test above)."""
        created = create_tsk(_ISSUE_27_VALID_SEED_BODY)

        result = update(id=created.id, type="tsk", content=_ISSUE_27_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        for substring in _ISSUE_27_EXPECTED_SUBSTRINGS:
            self.assertIn(substring, message)


if __name__ == "__main__":
    unittest.main()
