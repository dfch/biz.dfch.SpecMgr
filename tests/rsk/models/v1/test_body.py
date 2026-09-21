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

"""Tests for the `Risk` and its section models.

Structural problems (unrecognized headings, missing mandatory sections,
wrong section order) raise `AssertionError` from the engine's
`process_field`/`from_text`; value problems (a `## Strategy` word outside
the TARA closed set, an empty `Scope` list) raise
`pydantic.ValidationError`. The two error channels match `req`/`tsk`'s own
convention.
"""

import unittest
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1.assessment import LEVEL_HIGH, LEVEL_LOW, LEVEL_MEDIUM
from biz.dfch.specmgr.rsk.models.v1.body import Risk, Scope, Strategy

# A complete risk exercising every section (mandatory + optional) with a
# leading comment; the `reduce` scenario of the feature plan's worked
# example (initial 4x3=12 `high` -> residual 2x3=6 `medium`).
_WITH_COMMENT_TEXT = format_text(
    """\
# Untrusted File Uploads Parsed by an Unmaintained Parser Library

<!-- Risk entry for the document-processing subsystem's upload pipeline. -->

## Cause

The parser library has no security updates since 2021.

## Trigger

An uploaded file exploits a known format flaw.

## Consequence

Remote code execution in the document-processing subsystem; other subsystems
unaffected (isolated network zone).

## Scope

- document-processing subsystem

## Initial Assessment

### Probability 4

### Impact 3

## Strategy

reduce

## Mitigation

Replace the parser with a maintained library; restrict uploads to a format
whitelist.

## Residual Assessment

### Probability 2

### Impact 3

## Owner

Ronald Rink

## Tags

- security

- upload pipeline

## Source

The QA interview on 2026-09-17 that elicited this risk.

## More Information

Tracked in the incident-response backlog; revisit at the next library audit.
"""
)

# The minimal shape: only the mandatory sections, no leading comment.
_MINIMAL_TEXT = format_text(
    """\
# R1

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Initial Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 1

### Impact 1

## Source

The QA interview on 2026-09-17 that elicited this risk.
"""
)

#: `_MINIMAL_TEXT` without its `## Source` section -- the derived starting point for the
#: mandatory-`## Source` and `## Source`-position tests below (kept in lockstep with
#: `_MINIMAL_TEXT` by replacement, not a second hand-maintained literal).
_MINIMAL_NO_SOURCE = _MINIMAL_TEXT.replace(
    "\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n", ""
)


class TestRiskWithComment(unittest.TestCase):
    """`Risk` parses and round-trips with a leading comment and every optional section present."""

    def test_parses_and_round_trips(self) -> None:
        sut = Risk.from_text(_WITH_COMMENT_TEXT)

        self.assertIsNotNone(sut.comment)
        self.assertEqual(
            sut.text,
            "Untrusted File Uploads Parsed by an Unmaintained Parser Library",
        )
        self.assertEqual(
            sut.cause.text,
            "## Cause\n\nThe parser library has no security updates since 2021.\n",
        )
        self.assertEqual(
            sut.trigger.text,
            "## Trigger\n\nAn uploaded file exploits a known format flaw.\n",
        )
        self.assertEqual(
            sut.consequence.text,
            "## Consequence\n\nRemote code execution in the document-processing subsystem;"
            " other subsystems\nunaffected (isolated network zone).\n",
        )
        self.assertEqual([item.text for item in sut.scope.items], ["document-processing subsystem"])
        self.assertEqual(sut.initial_assessment.probability.value, 4)
        self.assertEqual(sut.initial_assessment.impact.value, 3)
        self.assertEqual(sut.initial_assessment.level, LEVEL_HIGH)
        self.assertEqual(sut.strategy.value.text, "reduce")
        self.assertEqual(
            sut.mitigation.text,
            "## Mitigation\n\nReplace the parser with a maintained library; restrict uploads to a format\nwhitelist.\n",
        )
        self.assertEqual(sut.residual_assessment.probability.value, 2)
        self.assertEqual(sut.residual_assessment.impact.value, 3)
        self.assertEqual(sut.residual_assessment.level, LEVEL_MEDIUM)
        self.assertEqual(sut.owner.value.text, "Ronald Rink")
        self.assertEqual([item.text for item in sut.tags.items], ["security", "upload pipeline"])
        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertEqual(
            sut.more_information.text,
            "## More Information\n\nTracked in the incident-response backlog; revisit at the next library audit.\n",
        )
        self.assertEqual(str(sut), _WITH_COMMENT_TEXT)


class TestRiskWithoutComment(unittest.TestCase):
    """`Risk` parses and round-trips in its minimal mandatory-only shape (no leading comment)."""

    def test_parses_and_round_trips(self) -> None:
        sut = Risk.from_text(_MINIMAL_TEXT)

        self.assertIsNone(sut.comment)
        self.assertEqual(sut.text, "R1")
        self.assertEqual(sut.initial_assessment.level, LEVEL_LOW)
        self.assertEqual(sut.strategy.value.text, "accept")
        self.assertIsNone(sut.owner)
        self.assertIsNone(sut.tags)
        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertIsNone(sut.more_information)
        self.assertEqual(str(sut), _MINIMAL_TEXT)


class TestRiskFreeFormTitle(unittest.TestCase):
    """`Risk`'s H1 title is free-form (any non-blank text matches its `@alias`)."""

    def test_accepts_arbitrary_titles(self) -> None:
        for title in ("R1", "Untrusted File Uploads Parsed by an Unmaintained Parser Library 42"):
            with self.subTest(title=title):
                text = _MINIMAL_TEXT.replace("# R1", f"# {title}", 1)

                sut = Risk.from_text(text)

                self.assertEqual(sut.text, title)


class TestRiskTaraClosedSet(unittest.TestCase):
    """`## Strategy` accepts exactly the four TARA words (case-sensitive, single line)."""

    def test_accepts_all_four_words(self) -> None:
        for word in ("transfer", "accept", "reduce", "avoid"):
            with self.subTest(word=word):
                sut = Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))

                self.assertEqual(sut.value.text, word)

    def test_rejects_words_outside_the_closed_set(self) -> None:
        for word in ("tolerate", "assign", "recover", "Reduce", "transfers", "reduce avoid"):
            with self.subTest(word=word):
                with self.assertRaises(ValidationError):
                    Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))


class TestRiskSectionOrderEnforced(unittest.TestCase):
    """`Risk`'s field declaration order enforces the markdown section order."""

    def test_rejects_residual_before_initial(self) -> None:
        text = format_text(
            """\
# R2

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Residual Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Initial Assessment

### Probability 1

### Impact 1
"""
        )

        with self.assertRaises(AssertionError):
            Risk.from_text(text)

    def test_rejects_swapped_scenario_sections(self) -> None:
        text = _MINIMAL_TEXT.replace(
            "## Cause\n\nc\n\n## Trigger\n\nt",
            "## Trigger\n\nt\n\n## Cause\n\nc",
            1,
        )

        with self.assertRaises(AssertionError):
            Risk.from_text(text)

    def test_rejects_source_before_tags(self) -> None:
        """`## Source` ahead of `## Tags` (feat-102-133-rsk-tags-source, ACC-003): the optional
        `## Tags` section is skipped over, `## Source` is consumed, and the tag list is left
        over with no declared field to consume it -- a structural failure naming the leftover."""
        text = format_text(
            _MINIMAL_NO_SOURCE
            + "\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n"
            + "\n## Tags\n\n- security\n"
        )

        with self.assertRaises(AssertionError) as ctx:
            Risk.from_text(text)
        message = str(ctx.exception)
        self.assertIn("text left over after processing all fields", message)
        self.assertIn("## Tags", message)

    def test_rejects_source_after_more_information(self) -> None:
        """`## Source` behind `## More Information` (feat-102-133-rsk-tags-source, ACC-003): the
        mandatory `## Source` field is processed before `## More Information` in declaration
        order and finds its heading only behind foreign text -- a structural failure naming
        the expected field and the text it actually found first."""
        text = format_text(
            _MINIMAL_NO_SOURCE
            + "\n## More Information\n\nFree-form supplementary text.\n"
            + "\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n"
        )

        with self.assertRaises(AssertionError) as ctx:
            Risk.from_text(text)
        message = str(ctx.exception)
        self.assertIn("Risk > Source", message)
        self.assertIn("expected Source (heading 'Source')", message)
        self.assertIn("found no match", message)
        self.assertIn("## More Information", message)


class TestRiskSourceMandatory(unittest.TestCase):
    """`## Source` is mandatory on every rsk document (feat-102-133-rsk-tags-source, GitHub issue #102).

    A document carrying `## Source` parses in both relative positions the field
    order allows (between `## Tags` and `## More Information`, and directly
    before `## More Information` when `## Tags` is absent) and the section's
    `value.text` round-trips; a document missing `## Source` fails the parse
    with an actionable `AssertionError` naming the missing field and a 1-based
    line reference (feat-27-validation convention) -- the message content is
    asserted, not just the exception type (REQ-009/ACC-002).
    """

    def test_parses_with_source_between_tags_and_more_information(self) -> None:
        sut = Risk.from_text(_WITH_COMMENT_TEXT)

        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertEqual(str(sut), _WITH_COMMENT_TEXT)

    def test_parses_with_source_directly_before_more_information(self) -> None:
        text = format_text(
            _MINIMAL_NO_SOURCE
            + "\n## Source\n\nThe QA interview on 2026-09-17 that elicited this risk.\n"
            + "\n## More Information\n\nFree-form supplementary text.\n"
        )

        sut = Risk.from_text(text)

        self.assertIsNone(sut.tags)
        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertEqual(sut.more_information.text, "## More Information\n\nFree-form supplementary text.\n")
        self.assertEqual(str(sut), text)

    def test_rejects_missing_source(self) -> None:
        text = format_text(_MINIMAL_NO_SOURCE)

        with self.assertRaises(AssertionError) as ctx:
            Risk.from_text(text)
        message = str(ctx.exception)
        self.assertIn("Risk > Source", message)
        self.assertIn("expected Source (heading 'Source')", message)
        self.assertIn("found no match", message)

    def test_rejects_missing_source_when_more_information_follows(self) -> None:
        """The failure must name `## Source`, not the section that follows the expected position."""
        text = format_text(_MINIMAL_NO_SOURCE + "\n## More Information\n\nFree-form supplementary text.\n")

        with self.assertRaises(AssertionError) as ctx:
            Risk.from_text(text)
        message = str(ctx.exception)
        self.assertIn("Risk > Source", message)
        self.assertIn("expected Source (heading 'Source')", message)
        self.assertIn("found no match", message)
        self.assertIn("## More Information", message)


class TestRiskMissingMandatorySection(unittest.TestCase):
    """Omitting a mandatory `## ` section fails the parse."""

    def test_rejects_missing_mitigation(self) -> None:
        text = _MINIMAL_TEXT.replace("## Mitigation\n\nnone\n\n", "", 1)

        with self.assertRaises(AssertionError):
            Risk.from_text(text)

    def test_rejects_missing_initial_assessment(self) -> None:
        text = _MINIMAL_TEXT.replace("## Initial Assessment\n\n### Probability 1\n\n### Impact 1\n\n", "", 1)

        with self.assertRaises(AssertionError):
            Risk.from_text(text)


class TestRiskScopeRequiresAtLeastOneEntry(unittest.TestCase):
    """`Scope` enforces its >=1 list-entry constraint, in both error channels.

    A `## Scope` heading with zero list items fails the parse (the engine's
    structural `AssertionError`); direct Python construction of
    `Scope(items=[])` fails validation (`min_length=1`).
    """

    def test_from_text_rejects_zero_entries(self) -> None:
        text = _MINIMAL_TEXT.replace("## Scope\n\n- s1\n\n", "## Scope\n\n", 1)

        with self.assertRaises(AssertionError):
            Risk.from_text(text)

    def test_direct_construction_rejects_empty_list(self) -> None:
        with self.assertRaises(ValidationError):
            Scope(items=[])


class TestRiskOptionalSections(unittest.TestCase):
    """Each of `## Owner`/`## Tags`/`## More Information` is independently optional."""

    def test_parses_with_only_owner(self) -> None:
        text = format_text(
            """\
# R1

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Initial Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 1

### Impact 1

## Owner

Ronald Rink

## Source

The QA interview on 2026-09-17 that elicited this risk.
"""
        )

        sut = Risk.from_text(text)

        self.assertEqual(sut.owner.value.text, "Ronald Rink")
        self.assertIsNone(sut.tags)
        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertIsNone(sut.more_information)
        self.assertEqual(str(sut), text)

    def test_parses_with_only_tags(self) -> None:
        text = format_text(
            """\
# R1

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Initial Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 1

### Impact 1

## Tags

- security

## Source

The QA interview on 2026-09-17 that elicited this risk.
"""
        )

        sut = Risk.from_text(text)

        self.assertEqual([item.text for item in sut.tags.items], ["security"])
        self.assertIsNone(sut.owner)
        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertIsNone(sut.more_information)
        self.assertEqual(str(sut), text)

    def test_parses_with_only_more_information(self) -> None:
        text = format_text(
            """\
# R1

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Initial Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 1

### Impact 1

## Source

The QA interview on 2026-09-17 that elicited this risk.

## More Information

Free-form supplementary text.
"""
        )

        sut = Risk.from_text(text)

        self.assertEqual(sut.source.value.text, "The QA interview on 2026-09-17 that elicited this risk.")
        self.assertEqual(sut.more_information.text, "## More Information\n\nFree-form supplementary text.\n")
        self.assertIsNone(sut.owner)
        self.assertIsNone(sut.tags)
        self.assertEqual(str(sut), text)


class TestRiskTagsNotes(unittest.TestCase):
    """`## Tags` items are `MarkdownListItemWithNotes` (issue #133).

    A loose-list continuation paragraph under a tag (blank line, then a
    marker-width-indented paragraph) is captured in the item's `notes` --
    not dropped, not merged into the item text, and not leaked into the
    following section. Plain single-line tags parse unchanged (the existing
    fixtures' `[item.text ...]` assertions still hold), and the document
    round-trips byte-exact.
    """

    def test_loose_continuation_captured_in_notes(self) -> None:
        text = format_text(
            """\
# R1

## Cause

c

## Trigger

t

## Consequence

k

## Scope

- s1

## Initial Assessment

### Probability 1

### Impact 1

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 1

### Impact 1

## Tags

- security

  Additional context on why this tag applies.

## Source

The QA interview on 2026-09-17 that elicited this risk.

## More Information

Tracked in the incident-response backlog.
"""
        )

        sut = Risk.from_text(text)

        self.assertEqual([item.text for item in sut.tags.items], ["security"])
        item = sut.tags.items[0]
        self.assertIsNotNone(item.notes)
        self.assertEqual(len(item.notes), 1)
        self.assertEqual(item.notes[0].text, "Additional context on why this tag applies.")
        self.assertEqual(
            sut.more_information.text, "## More Information\n\nTracked in the incident-response backlog.\n"
        )
        self.assertEqual(str(sut), text)


class TestReferenceDocumentBody(unittest.TestCase):
    """The feature plan's reference document body is exactly what `Risk.from_text` accepts.

    `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md` is
    reserved as Phase 2's parser round-trip fixture; this test pins the
    body-only half of that contract in Phase 1 (the frontmatter is
    validated by `RskFrontmatter` via the parser in Phase 2). The body is
    taken the same way Phase 2's parser will take it:
    `frontmatter.loads` + `format_text`.
    """

    def test_body_round_trips(self) -> None:
        reference_path = (
            Path(__file__).resolve().parents[4]
            / ".specmgr"
            / "feat"
            / "feat-15-add-artifact-type-risk"
            / "rsk_reference.md"
        )
        post = frontmatter.loads(reference_path.read_text(encoding="utf-8"))
        body = format_text(post.content)

        sut = Risk.from_text(body)

        self.assertEqual(sut.initial_assessment.level, LEVEL_HIGH)
        self.assertEqual(sut.residual_assessment.level, LEVEL_MEDIUM)
        self.assertEqual(str(sut), body)


if __name__ == "__main__":
    unittest.main()
