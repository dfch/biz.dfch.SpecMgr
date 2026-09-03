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

"""feat-67-70-71 Phase 4 (REQ-004/ACC-003): end-to-end regression test locking in that a
malformed ``#### {timestamp}`` heading in ``Updates``/``Decisions Made`` -- one that does not
match `feat`'s `#### {timestamp} ( - | : ) {title}` alias, e.g. issue #71's own literal report of
a date with no time-of-day, then a parenthetical, then `` - title`` -- already produces a fully
actionable ``wrap_tool_errors``/pydantic message, not a bare ``Error executing tool``. This file
also covers the closely related newest-first-ordering failure mode documented in this feature's
own Design Notes (a third sub-case discovered during this feature's own drafting session, folded
into Phase 1's investigation as Task 1.6).

This is a **regression-test-only** phase, not a fix, for both sub-cases:

- Phase 1 and Phase 1b (this feature's own README, Design Notes) both conclusively found no gap
  for the malformed-heading case -- even reproducing the exact literal reported heading text
  (``#### 2026-09-02 (Phase 1) - Some Title``) through ``Feature.from_text``, the in-process
  ``validate_feat``/``update`` tools, and a real MCP client over a real ``stdio`` transport,
  *including* the generic ``update`` tool's real ``offset``/``limit`` line-range splice path (the
  exact call shape issue #71 was filed against), not just whole-document validation.
- Task 1.6 found no gap for the newest-first-ordering case either: ``Updates``/
  ``DecisionsMade``'s ``_validate_newest_first`` raises a plain ``AssertionError`` from inside a
  ``@model_validator(mode="after")``, which Pydantic wraps into a ``pydantic.ValidationError`` --
  one of the three channels ``wrap_tool_errors`` already handles, and it does, correctly.

The orchestrator/user accepted both "no gap found" verdicts, so Task 4.1's conditional code fix
in ``models/md/markdown_section.py``/``markdown_str.py`` was skipped entirely -- this file exists
purely to catch a *future* regression of today's already-correct behavior for both sub-cases.

ACC-003 explicitly names three surfaces: ``create_<d>``, ``validate_<d>``, and the generic
``update`` tool. Both test classes below exercise all three for ``feat`` (the domain issue #71
was literally filed against, and the domain the newest-first-ordering case was found in) -- the
``update`` coverage is the one Phase 1b's own literal repro specifically called out as untested
by Phase 1's first pass, since it drives the tool's real re-read/splice/validate-whole path
(``general/tools/update.py::_update_feat`` + ``general/tools/_splice.py::splice_body``), not a
shortcut around it.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

import pydantic

from biz.dfch.specmgr.feat.tools._io import load_by_id
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.validate_feat import validate_feat
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update


def _line_number(text: str, needle: str) -> int:
    """Return the 1-based line number of the first line of ``text`` equal to ``needle``.

    Parameters
    ----------
    text:
        The body text to search (its ``splitlines()`` result).
    needle:
        The exact line to find.

    Returns
    -------
    int
        The 1-based line number.

    Raises
    ------
    AssertionError
        ``needle`` is not a line of ``text`` (a test-fixture bug, not the
        behavior under test).
    """
    for index, line in enumerate(text.splitlines(), start=1):
        if line == needle:
            return index
    raise AssertionError(f"fixture line {needle!r} not found in text {text!r}")


# ---------------------------------------------------------------------------
# A minimal, valid `feat` body with one `### Decisions Made` entry, used as
# the scratch document `create_feat` writes before the `update` tool splices
# a bad fragment into it (both sub-cases below reuse this same base body).
# ---------------------------------------------------------------------------

_FEAT_VALID_BASE_BODY = textwrap.dedent(
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

    #### Phase 1: Placeholder Phase

    - [ ] Task 1.1: A short description.

    ## Progress

    ### Current Status

    **As of 2026-09-03**: free-form narrative.

    ### Updates

    <!-- Newest entry first -- prepend new entries directly below this comment. -->

    #### 2026-09-03 10:00:00.000Z - Created

    Free-form prose.

    ### Decisions Made

    <!-- Newest entry first -- prepend new entries directly below this comment. -->

    #### 2026-09-03 09:00:00.000Z - Chose the widget's render budget

    Settled on a 200ms render budget after profiling similar widgets.
    """
)

#: The existing `### Decisions Made` heading line in `_FEAT_VALID_BASE_BODY`, used to compute
#: the `update` tool's splice `offset` (insert immediately before it, as a pure insert).
_EXISTING_DECISION_HEADING = "#### 2026-09-03 09:00:00.000Z - Chose the widget's render budget"


# ---------------------------------------------------------------------------
# Sub-case 1 (issue #71 itself): a malformed `#### {timestamp}` heading --
# issue #71's own literal report: a date with no time-of-day at all, then a
# parenthetical, then " - title".
# ---------------------------------------------------------------------------

_MALFORMED_HEADING = "#### 2026-09-02 (Phase 1) - Some Title"

#: `_FEAT_VALID_BASE_BODY` with its one `### Decisions Made` entry's heading replaced by the
#: malformed heading, for the whole-document `validate_feat`/`create_feat` tests.
_FEAT_MALFORMED_HEADING_BODY = _FEAT_VALID_BASE_BODY.replace(_EXISTING_DECISION_HEADING, _MALFORMED_HEADING)

#: The splice fragment the `update`-tool test inserts as a pure insert (`limit=0`) immediately
#: before the existing decision entry, so the spliced-whole document ends up with the malformed
#: heading as its newest `### Decisions Made` entry.
_MALFORMED_HEADING_FRAGMENT = f"{_MALFORMED_HEADING}\n\nA malformed heading inserted for regression testing.\n\n"

#: Cause + path/line/snippet substrings every malformed-heading failure message must carry
#: (empirically confirmed in Phase 4, matching Phase 1b's own report verbatim), taken from
#: `models/md`'s alias/`get_extent`-matching "no further item found" -> "leftover text" path
#: (`markdown_str.py::process_list_field`/`_no_match_message`/`_leftover_text_message`).
_MALFORMED_HEADING_SUBSTRINGS = (
    "Feature > Progress > DecisionsMade > DecisionEntry",
    "found no match",
    "remaining text starts at line",
    _MALFORMED_HEADING,
)


# ---------------------------------------------------------------------------
# Sub-case 2 (Task 1.6, this feature's own drafting-session discovery): two
# `### Decisions Made` entries out of newest-first order, due to the exact
# `+02:00`/`Z` offset-arithmetic mistake documented in Design Notes: an entry
# timestamped `09:52:07.318+02:00` (UTC 07:52:07.318) was mistakenly written
# *first* (assumed newest), ahead of one timestamped `10:41:29.955Z` (UTC
# 10:41:29.955) -- but the first entry is actually the *older* of the two
# once both are compared as aware datetimes, violating newest-first order.
# ---------------------------------------------------------------------------

_ORDER_MISTAKEN_NEWEST_HEADING = "#### 2026-09-03 09:52:07.318+02:00 - Assumed newest due to an offset mistake"
_ORDER_ACTUAL_NEWEST_HEADING = "#### 2026-09-03 10:41:29.955Z - Actually the more recent decision"

#: `_FEAT_VALID_BASE_BODY` with its one `### Decisions Made` entry replaced by just the
#: chronologically-actual-newest heading -- a valid, single-entry scratch document the
#: `update`-tool test creates, then splices the mistaken-newest heading into (immediately
#: before it), reproducing the out-of-order pair via the real splice path.
_FEAT_ORDER_BASE_BODY = _FEAT_VALID_BASE_BODY.replace(_EXISTING_DECISION_HEADING, _ORDER_ACTUAL_NEWEST_HEADING)

#: The two `### Decisions Made` entries in document order exactly as Design Notes describes the
#: mistake: the mistaken-newest entry listed first, followed by the actually-newest entry --
#: i.e. the first entry's timestamp is chronologically *older* than the second's, violating
#: newest-first order. Used by the whole-document `validate_feat`/`create_feat` tests.
_FEAT_ORDER_VIOLATION_BODY = _FEAT_VALID_BASE_BODY.replace(
    _EXISTING_DECISION_HEADING,
    f"{_ORDER_MISTAKEN_NEWEST_HEADING}\n\nSome decision text.\n\n{_ORDER_ACTUAL_NEWEST_HEADING}",
)

#: The splice fragment the `update`-tool test inserts as a pure insert (`limit=0`) immediately
#: before `_FEAT_ORDER_BASE_BODY`'s one existing (actually-newest) entry, so the spliced-whole
#: document ends up with the same out-of-order pair, in the same document order, as
#: `_FEAT_ORDER_VIOLATION_BODY` above.
_ORDER_VIOLATION_FRAGMENT = f"{_ORDER_MISTAKEN_NEWEST_HEADING}\n\nSome decision text.\n\n"

#: The field name + both offending timestamps every ordering-violation failure message must
#: carry (empirically confirmed in Phase 4, matching Task 1.6's own report verbatim), taken from
#: `feat.models.v1.body.DecisionsMade._validate_newest_first`'s own `AssertionError`, wrapped by
#: Pydantic into a `pydantic.ValidationError`.
_ORDER_VIOLATION_SUBSTRINGS = (
    "DecisionsMade: entries must be newest-first",
    "'2026-09-03 09:52:07.318+02:00' precedes '2026-09-03 10:41:29.955Z'",
)


def _assert_actionable(message: str, tool_prefix: str, expected_substrings: tuple[str, ...]) -> None:
    """Assert ``message`` names the tool boundary, the field/path, and every expected detail.

    Parameters
    ----------
    message:
        The ``str(exception)`` a failed ``validate_feat``/``create_feat``/``update`` call
        raised.
    tool_prefix:
        The domain/tool/channel prefix `wrap_tool_errors` adds (e.g. ``"feat validate_feat
        (body):"``, ``"feat create_feat (body):"``, ``"feat update (body):"``).
    expected_substrings:
        The cause/field/line/snippet substrings the message must also carry.
    """
    assert isinstance(message, str), type(message)
    assert tool_prefix in message, f"expected {tool_prefix!r} in message, got: {message!r}"

    for substring in expected_substrings:
        assert substring in message, f"expected {substring!r} in message, got: {message!r}"


class TestIssue71MalformedHeadingRegression(unittest.TestCase):
    """Issue #71's literal repro: a `#### {timestamp} ... - {title}` heading with no time-of-day.

    Covers all three surfaces ACC-003 names: `validate_feat`, `create_feat` (both whole-document),
    and the generic `update` tool's real line-range splice path.
    """

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def test_validate_feat_surfaces_an_actionable_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            validate_feat(_FEAT_MALFORMED_HEADING_BODY)

        _assert_actionable(str(ctx.exception), "feat validate_feat (body):", _MALFORMED_HEADING_SUBSTRINGS)

    def test_create_feat_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_feat(_FEAT_MALFORMED_HEADING_BODY)

        _assert_actionable(str(ctx.exception), "feat create_feat (body):", _MALFORMED_HEADING_SUBSTRINGS)

        # Validation happens before the create lock/base-dir creation (create_feat's own
        # docstring), so nothing at all should exist on disk after a failed create.
        self.assertFalse(feat_base_dir().exists())

    def test_generic_update_tool_splice_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        # Reproduces issue #71's own literal call shape (Phase 1b): create a scratch feature,
        # then splice the malformed heading in via the generic `update` tool's real
        # offset/limit line-range path -- not a whole-document shortcut around it.
        frontmatter = create_feat(_FEAT_VALID_BASE_BODY)
        assert frontmatter.id is not None, "create_feat always assigns an id"
        feat_id = frontmatter.id
        base_dir = feat_base_dir()
        path, _existing = load_by_id(base_dir, feat_id)
        before = body_text(path)
        offset = _line_number(before, _EXISTING_DECISION_HEADING)

        with self.assertRaises(AssertionError) as ctx:
            update(id=feat_id, type="feat", content=_MALFORMED_HEADING_FRAGMENT, offset=offset, limit=0)

        _assert_actionable(str(ctx.exception), "feat update (body):", _MALFORMED_HEADING_SUBSTRINGS)

        # Nothing was persisted: the on-disk body is byte-identical to before the failed splice.
        self.assertEqual(before, body_text(path))


class TestIssue71NewestFirstOrderingRegression(unittest.TestCase):
    """Task 1.6's newest-first-ordering sub-case: two `### Decisions Made` entries out of order.

    Reproduces the exact `+02:00`/`Z` offset-arithmetic mistake documented in this feature's own
    Design Notes. Covers `validate_feat`, `create_feat` (both whole-document), and the generic
    `update` tool's real line-range splice path, matching the malformed-heading test's coverage
    breadth.
    """

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))

    def test_validate_feat_surfaces_an_actionable_message(self) -> None:
        with self.assertRaises(pydantic.ValidationError) as ctx:
            validate_feat(_FEAT_ORDER_VIOLATION_BODY)

        _assert_actionable(str(ctx.exception), "feat validate_feat (body):", _ORDER_VIOLATION_SUBSTRINGS)

    def test_create_feat_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        with self.assertRaises(pydantic.ValidationError) as ctx:
            create_feat(_FEAT_ORDER_VIOLATION_BODY)

        _assert_actionable(str(ctx.exception), "feat create_feat (body):", _ORDER_VIOLATION_SUBSTRINGS)

        self.assertFalse(feat_base_dir().exists())

    def test_generic_update_tool_splice_surfaces_an_actionable_message_and_writes_nothing(self) -> None:
        # Reproduces this feature's own drafting-session scenario (Task 1.6/Phase 1): create a
        # scratch feature whose one existing `### Decisions Made` entry is the chronologically
        # actual-newest one, then splice the mistaken-newest heading in immediately before it
        # via the generic `update` tool's real offset/limit line-range path -- reproducing the
        # out-of-order pair exactly as Design Notes describes.
        frontmatter = create_feat(_FEAT_ORDER_BASE_BODY)
        assert frontmatter.id is not None, "create_feat always assigns an id"
        feat_id = frontmatter.id
        base_dir = feat_base_dir()
        path, _existing = load_by_id(base_dir, feat_id)
        before = body_text(path)
        offset = _line_number(before, _ORDER_ACTUAL_NEWEST_HEADING)

        with self.assertRaises(pydantic.ValidationError) as ctx:
            update(id=feat_id, type="feat", content=_ORDER_VIOLATION_FRAGMENT, offset=offset, limit=0)

        _assert_actionable(str(ctx.exception), "feat update (body):", _ORDER_VIOLATION_SUBSTRINGS)

        # Nothing was persisted: the on-disk body is byte-identical to before the failed splice.
        self.assertEqual(before, body_text(path))


if __name__ == "__main__":
    unittest.main()
