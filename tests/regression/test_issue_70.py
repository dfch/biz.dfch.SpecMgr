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

"""feat-67-70-71 Phase 3 (REQ-003/ACC-002): end-to-end regression test locking in that a bare
``<word>``-shaped token outside backticks in a heading or list item -- parsed as raw HTML by the
shared ``models/md`` tokenizer -- already produces a fully actionable ``wrap_tool_errors``
message, not a bare ``Error executing tool``.

This is a **regression-test-only** phase, not a fix: Phase 1 (this feature's own README, Design
Notes) and Phase 1b (a follow-up literal-reproduction deep dive) both conclusively found no gap
-- even reproducing the exact literal reported heading text
(``#### Phase N: Per-domain create_<d> tools``) at document sizes up to 175 lines, with multiple
simultaneous violations, at various positions in the document, through ``Feature.from_text``,
the in-process ``validate_feat`` tool (since retired in favor of the generic ``validate`` tool,
feat-81-83-validation Phase 2), and a real MCP client over a real ``stdio`` transport. The
orchestrator/user accepted that "no gap found" verdict, so Task 3.1's conditional code fix in
``models/md/_markdown.py`` was skipped entirely -- this file exists purely to catch a *future*
regression of today's already-correct behavior.

The offending check (``models/md/_markdown.py::_assert_no_raw_html``/``parse()``) lives in the
markdown parser every domain shares, so ACC-002 asks for coverage across "every affected
domain," not just ``feat`` (the domain issue #70 was literally filed against). This file covers
three domains with deliberately different body shapes, to exercise the shared parser through
different structural paths rather than just one:

1. **``feat``** -- the literal issue #70 reproduction: the bad token sits in a `` #### Phase N: ``
   ``Task List`` heading, using the issue's own literal wording
   (``Per-domain create_<d> tools``), inside a folder-per-document, nested-container schema.
2. **``req``** -- the bad token sits in a bullet list item inside a free-form ``## Description``
   prose section, inside a flat, single-file, WHILE/THE-grammar schema.
3. **``dec``** -- the bad token sits in a bullet list item inside a free-form
   ``## Context and Problem Statement`` prose section, inside a flat, single-file, MADR-style
   schema.

Each domain is driven through both the generic ``validate`` tool (disk-free dry run) and
``create_<d>`` (actual create, asserted to write nothing to disk on failure) -- the two
surfaces ACC-002 names. Since feat-81-83-validation Phase 2, ``validate`` never raises for a
content-validation failure -- it returns ``{valid: False, errors: [{message: str}]}`` instead,
so the ``validate``-tool tests below assert against ``result.errors[0].message`` rather than a
raised exception.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR, doc_base_dir
from biz.dfch.specmgr.general.tools.validate import validate
from biz.dfch.specmgr.req.tools.create_req import create_req

#: The cause + fix-hint substrings every one of this test's bad bodies must surface (REQ-003),
#: taken from `models/md/_markdown.py::_raw_html_message`'s own message shape. `"at line"` checks
#: for the 1-based line-number reference; the other three check for the token-kind/content naming
#: and the two documented remedies.
_EXPECTED_SUBSTRINGS = (
    "raw HTML is not permitted",
    "at line",
    "wrap it in a code span",
    "write it as an HTML comment",
)


def _assert_actionable_message(message: str) -> None:
    """Assert ``message`` names the cause, a line, and both fix hints -- not a bare message.

    Parameters
    ----------
    message:
        The ``str(exception)`` a failed ``create_<d>`` call raised, or a failed generic
        ``validate`` call's ``result.errors[0].message``.
    """
    assert isinstance(message, str), type(message)

    for substring in _EXPECTED_SUBSTRINGS:
        assert substring in message, f"expected {substring!r} in message, got: {message!r}"


# ---------------------------------------------------------------------------
# feat: the literal issue #70 repro -- a bare `<word>`-shaped token in a
# `#### Phase N: ...` Task List heading, using the issue's own literal wording.
# ---------------------------------------------------------------------------

_FEAT_BAD_BODY = textwrap.dedent(
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

    #### Phase 3: Per-domain create_<d> tools

    - [x] Task 3.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


# ---------------------------------------------------------------------------
# req: a bare `<word>`-shaped token in a bullet list item inside `## Description`.
# ---------------------------------------------------------------------------

_REQ_BAD_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    - Legacy documentation referred to this check as <legacy-temp-check>, not TISBA.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)


# ---------------------------------------------------------------------------
# dec: a bare `<word>`-shaped token in a bullet list item inside
# `## Context and Problem Statement`.
# ---------------------------------------------------------------------------

_DEC_BAD_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    - The old <legacy-store> cannot scale further either.

    ## Decision Outcome

    We chose the document store.
    """
)


class TestIssue70FeatBareHtmlTokenRegression(unittest.TestCase):
    """The literal issue #70 repro (a bad `#### Phase N: ...` heading), for `feat`."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def test_validate_surfaces_an_actionable_message(self) -> None:
        result = validate(type="feat", content=_FEAT_BAD_BODY)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        _assert_actionable_message(result.errors[0].message)

    def test_create_feat_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_feat(_FEAT_BAD_BODY)

        _assert_actionable_message(str(ctx.exception))

        # Validation happens before the create lock/base-dir creation (create_feat's own
        # docstring), so nothing at all should exist on disk after a failed create.
        self.assertFalse(feat_base_dir().exists())


class TestIssue70ReqBareHtmlTokenRegression(unittest.TestCase):
    """A bare `<word>`-shaped token in a `## Description` list item, for `req`."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_validate_surfaces_an_actionable_message(self) -> None:
        result = validate(type="req", content=_REQ_BAD_BODY)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        _assert_actionable_message(result.errors[0].message)

    def test_create_req_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_req(_REQ_BAD_BODY)

        _assert_actionable_message(str(ctx.exception))

        req_dir = doc_base_dir("req")
        self.assertEqual([], list(req_dir.glob("*.md")) if req_dir.exists() else [])


class TestIssue70DecBareHtmlTokenRegression(unittest.TestCase):
    """A bare `<word>`-shaped token in a `## Context and Problem Statement` list item, for `dec`."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_validate_surfaces_an_actionable_message(self) -> None:
        result = validate(type="dec", content=_DEC_BAD_BODY)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        _assert_actionable_message(result.errors[0].message)

    def test_create_dec_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_dec(_DEC_BAD_BODY)

        _assert_actionable_message(str(ctx.exception))

        dec_dir = doc_base_dir("dec")
        self.assertEqual([], list(dec_dir.glob("*.md")) if dec_dir.exists() else [])


if __name__ == "__main__":
    unittest.main()
