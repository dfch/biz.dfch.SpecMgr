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

"""Tests for the `Txt` body model (ACC-001/ACC-002).

Covers the full ACC-001 structural matrix (the nine rows of the plan's own
Design-Notes spike, reproduced against the real engine): the text-only body,
a body with free H2/H3 headings and lists, a fenced `## Updates` inside the
body (boundary not triggered), the empty/whitespace-only body (the engine's
own mandatory-field error), the comment-only body (accepted), the missing
`## Updates` (rejected), the duplicate `## Updates` and the H2-after-
`## Updates` (both rejected as the engine's own "text left over").

Plus the ACC-002 entry cases: `UpdateEntry`'s heading alias (both ` - `/
` : ` separators, both `T`/space date separators, both `Z`/offset
timezones), `UpdateEntry.content` accepting any markdown, the
`Updates` zero-entry rejection, the shared newest-first ordering
(`ValidationError` channel, equal timestamps allowed), and the computed
`timestamp`/`title` fields.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.txt.models.v1.body import Txt, TxtBody, UpdateEntry, Updates
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md.alias_match import match_alias

# The full reference body, exercising every field: an opaque free-form
# `body` with free H2/H3 headings, a bullet list, and a fenced `## Updates`
# (which must stay in the body -- the boundary only triggers on a top-level
# H2), followed by the mandatory `## Updates` section (with its own leading
# "newest first" anchor comment) carrying two entries in newest-first order.
_REFERENCE_TEXT = format_text(
    """\
# Ad-hoc review notes

## Findings

Some prose about what was found.

- item one

- item two

### Detail

More prose under a free H3.

```
## Updates
```

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-08-27 00:00:00.000Z : Reviewed

The findings were reviewed.

### 2026-08-26 00:00:00.000Z - Created

Initial draft of the review notes.
"""
)


def _updates_section(*, comment: bool = True) -> str:
    """Build a minimal valid `## Updates` section text (one entry)."""
    c = "<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n" if comment else ""
    return format_text(f"## Updates\n\n{c}### 2026-08-26 00:00:00.000Z - Created\n\nSome text.\n")


class TestTxtHeadingAlias(unittest.TestCase):
    """`Txt`'s H1 alias is the free-form `.+` REGEX: any non-empty title matches."""

    def test_txt_matches_any_nonempty_h1_text(self) -> None:
        for heading in ("Ad-hoc review notes", "A TXT", "x"):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(Txt, heading))

    def test_txt_rejects_empty_h1_text(self) -> None:
        self.assertFalse(match_alias(Txt, ""))

    def test_metadata_is_heading_open_h1(self) -> None:
        self.assertEqual(Txt._metadata.get("type"), "heading_open")
        self.assertEqual(Txt._metadata.get("tag"), "h1")


class TestTxtBodyBoundaryACC001(unittest.TestCase):
    """ACC-001 (REQ-001/REQ-002/REQ-003): the nine structural cases of the plan's Design-Notes spike.

    Each test name carries the spike row number (S1..S9) it reproduces; the
    engine's default error messages are asserted on for the rejection rows
    (REQ-011 -- no custom cause/fix-hint wrapping exists).
    """

    def test_s1_text_only_body_accepted(self) -> None:
        """S1: a plain text-only body parses; the body carries exactly the prose between H1 and `## Updates`."""
        sut = Txt.from_text(format_text("# T\n\nSome prose.\n\n" + _updates_section()))

        self.assertEqual(sut.body.text, "Some prose.\n")
        self.assertEqual(len(sut.updates.updates), 1)

    def test_s2_body_with_free_headings_and_lists_accepted(self) -> None:
        """S2: free H2/H3 headings and lists inside the body are accepted verbatim (opaque)."""
        sut = Txt.from_text(
            format_text("# T\n\n## Some Heading\n\nprose\n\n- a\n\n- b\n\n### Sub\n\nmore\n\n" + _updates_section())
        )

        self.assertEqual(sut.body.text, "## Some Heading\n\nprose\n\n- a\n\n- b\n\n### Sub\n\nmore\n")
        self.assertEqual(
            str(sut),
            format_text("# T\n\n## Some Heading\n\nprose\n\n- a\n\n- b\n\n### Sub\n\nmore\n\n" + _updates_section()),
        )

    def test_s3_fenced_updates_heading_stays_in_body(self) -> None:
        """S3: a `## Updates` line inside a code fence yields no `heading_open` token -- it stays in the body."""
        sut = Txt.from_text(format_text("# T\n\n```\n## Updates\n```\n\nprose\n\n" + _updates_section()))

        self.assertIn("```\n## Updates\n```\n", sut.body.text)
        self.assertEqual(sut.body.text, "```\n## Updates\n```\n\nprose\n")

    def test_s4_empty_body_rejected_by_mandatory_field_error(self) -> None:
        """S4: H1 followed directly by `## Updates` -- the mandatory `body` finds no extent (engine default)."""
        with self.assertRaises(AssertionError) as ctx:
            Txt.from_text(format_text("# T\n\n" + _updates_section()))

        self.assertIn("expected TxtBody, found no match", str(ctx.exception))

    def test_s5_whitespace_only_body_rejected_by_mandatory_field_error(self) -> None:
        """S5: whitespace between H1 and `## Updates` normalizes to nothing -- same mandatory-field error."""
        with self.assertRaises(AssertionError) as ctx:
            Txt.from_text(format_text("# T\n\n   \n\n" + _updates_section()))

        self.assertIn("expected TxtBody, found no match", str(ctx.exception))

    def test_s6_comment_only_body_accepted(self) -> None:
        """S6: a comment-only body is accepted (current parser behaviour, no extra validator)."""
        sut = Txt.from_text(format_text("# T\n\n<!-- a comment -->\n\n" + _updates_section()))

        self.assertEqual(sut.body.text, "<!-- a comment -->\n")

    def test_s7_missing_updates_rejected(self) -> None:
        """S7: no `## Updates` at all -- the body consumes everything, the mandatory `updates` finds none."""
        with self.assertRaises(AssertionError) as ctx:
            Txt.from_text(format_text("# T\n\nSome prose.\n"))

        self.assertIn("expected Updates", str(ctx.exception))

    def test_s8_duplicate_updates_rejected_as_text_left_over(self) -> None:
        """S8: a second top-level `## Updates` is left over after the `updates` field (engine default)."""
        text = format_text(
            "# T\n\nprose\n\n## Updates\n\n"
            "### 2026-08-26 00:00:00.000Z - Created\n\nSome text.\n\n"
            "## Updates\n\n"
            "### 2026-08-27 00:00:00.000Z - Second\n\nMore text.\n"
        )

        with self.assertRaises(AssertionError) as ctx:
            Txt.from_text(text)

        self.assertIn("text left over after processing all fields", str(ctx.exception))

    def test_s9_h2_after_updates_rejected_as_text_left_over(self) -> None:
        """S9: any other top-level H2 after `## Updates` is left over after the `updates` field (engine default)."""
        text = format_text(
            "# T\n\nprose\n\n"
            "## Updates\n\n"
            "### 2026-08-26 00:00:00.000Z - Created\n\nSome text.\n\n"
            "## Notes\n\nSome notes text.\n"
        )

        with self.assertRaises(AssertionError) as ctx:
            Txt.from_text(text)

        self.assertIn("text left over after processing all fields", str(ctx.exception))

    def test_blockquote_nested_updates_heading_stays_in_body(self) -> None:
        """A `## Updates` heading nested inside another block (a block quote, level > 0) stays in the body.

        The boundary is the first *top-level* (level 0) H2 -- REQ-003's
        "not inside a code fence or other block" -- so this row pins the
        `tok.level == 0` half of the condition (S3 pins the fence half).
        """
        sut = Txt.from_text(format_text("# T\n\n> ## Updates\n\n> quoted\n\nprose\n\n" + _updates_section()))

        self.assertIn("> ## Updates\n", sut.body.text)


class TestTxtBodyTextComputedField(unittest.TestCase):
    """REQ-006: `TxtBody.text` makes the opaque body reachable through `model_dump()`/`model_dump_json()`."""

    def test_model_dump_surfaces_body_text(self) -> None:
        sut = Txt.from_text(format_text("# T\n\nSome prose.\n\n" + _updates_section()))

        dump = sut.model_dump(mode="json")

        self.assertEqual(dump["body"]["text"], "Some prose.\n")

    def test_model_dump_json_surfaces_body_text(self) -> None:
        import json

        sut = Txt.from_text(format_text("# T\n\nSome prose.\n\n" + _updates_section()))

        dumped = json.loads(sut.model_dump_json())

        self.assertEqual(dumped["body"]["text"], "Some prose.\n")

    def test_unset_body_text_is_empty_string(self) -> None:
        sut = TxtBody()

        self.assertEqual(sut.text, "")


class TestUpdateEntryHeadingAliasACC002(unittest.TestCase):
    """ACC-002 (REQ-004): `UpdateEntry`'s alias accepts the documented heading shapes and rejects the rest."""

    def test_accepts_both_separators(self) -> None:
        for heading in (
            "2026-08-26 14:30:00.000+02:00 - Confirmed",
            "2026-08-26 14:30:00.000+02:00 : Confirmed",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_accepts_both_date_separators(self) -> None:
        for heading in (
            "2026-08-26 14:30:00.000Z - Confirmed",
            "2026-08-26T14:30:00.000Z - Confirmed",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_accepts_both_timezone_forms(self) -> None:
        for heading in (
            "2026-08-26 14:30:00.000Z - Confirmed",
            "2026-08-26 14:30:00.000+02:00 - Confirmed",
            "2026-08-26 14:30:00.000-05:00 : Confirmed",
        ):
            with self.subTest(heading=heading):
                self.assertTrue(match_alias(UpdateEntry, heading))

    def test_rejects_date_only_headings(self) -> None:
        for heading in ("2026-08-26 - Created", "2026-08-26 : Created"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_em_dash_separator(self) -> None:
        self.assertFalse(match_alias(UpdateEntry, "2026-08-26 14:30:00.000Z — Created"))

    def test_rejects_non_timestamp_led_headings(self) -> None:
        for heading in ("A Note", "x", "2026-8-26 - Created", "Created"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_rejects_empty_h3_text(self) -> None:
        self.assertFalse(match_alias(UpdateEntry, ""))

    def test_rejects_heading_without_title(self) -> None:
        for heading in ("2026-08-26 14:30:00.000Z -", "2026-08-26 14:30:00.000Z :"):
            with self.subTest(heading=heading):
                self.assertFalse(match_alias(UpdateEntry, heading))

    def test_metadata_is_heading_open_h3(self) -> None:
        self.assertEqual(UpdateEntry._metadata.get("type"), "heading_open")
        self.assertEqual(UpdateEntry._metadata.get("tag"), "h3")


class TestUpdateEntryComputedFieldsACC002(unittest.TestCase):
    """ACC-002 (REQ-004): the computed `timestamp`/`title` fields are derived verbatim from the heading."""

    def test_parses_timestamp_and_title_t_separator(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-26T14:30:00.000Z - Created\n\nBody.\n"))

        self.assertEqual(sut.timestamp, "2026-08-26T14:30:00.000Z")
        self.assertEqual(sut.title, "Created")

    def test_parses_timestamp_and_title_colon_separator(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-26 14:30:00.000+02:00 : Reviewed the findings\n\nBody.\n"))

        self.assertEqual(sut.timestamp, "2026-08-26 14:30:00.000+02:00")
        self.assertEqual(sut.title, "Reviewed the findings")

    def test_title_keeps_colons_inside_text(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-26 14:30:00.000Z - Time: 14:30\n\nBody.\n"))

        self.assertEqual(sut.timestamp, "2026-08-26 14:30:00.000Z")
        self.assertEqual(sut.title, "Time: 14:30")

    def test_date_only_heading_rejected_at_parse_time(self) -> None:
        for heading in ("### 2026-08-26 - Created", "### 2026-08-26 : Created"):
            with self.subTest(heading=heading):
                with self.assertRaises(AssertionError):
                    UpdateEntry.from_text(format_text(f"{heading}\n\nSome update text.\n"))

    def test_model_dump_surfaces_computed_fields(self) -> None:
        sut = UpdateEntry.from_text(format_text("### 2026-08-26 14:30:00.000Z - Created\n\nBody.\n"))

        dump = sut.model_dump(mode="json")

        self.assertEqual(dump["timestamp"], "2026-08-26 14:30:00.000Z")
        self.assertEqual(dump["title"], "Created")
        self.assertEqual(dump["content"]["text"], "Body.\n")


class TestUpdateEntryContentACC002(unittest.TestCase):
    """ACC-002 (REQ-004): `UpdateEntry.content` accepts any markdown verbatim and is mandatory.

    Every body below is mdformat-stable, so the entry round-trips
    byte-identically and `.content.text` carries the raw body including
    mdformat's canonical single trailing `"\n"`.
    """

    def test_multi_paragraph_content_parses_and_round_trips(self) -> None:
        text = format_text("### 2026-08-26 00:00:00.000Z - Created\n\nFirst paragraph.\n\nSecond paragraph.\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "First paragraph.\n\nSecond paragraph.\n")
        self.assertEqual(str(sut), text)

    def test_bullet_list_content_parses_and_round_trips(self) -> None:
        text = format_text("### 2026-08-26 00:00:00.000Z - Created\n\n- item one\n\n- item two\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "- item one\n\n- item two\n")
        self.assertEqual(str(sut), text)

    def test_fenced_code_block_content_parses_and_round_trips(self) -> None:
        text = format_text(
            "### 2026-08-26 00:00:00.000Z - Created\n\nSome lead prose.\n\n```\ncode block content\n```\n"
        )

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "Some lead prose.\n\n```\ncode block content\n```\n")
        self.assertEqual(str(sut), text)

    def test_block_quote_content_parses_and_round_trips(self) -> None:
        text = format_text("### 2026-08-26 00:00:00.000Z - Created\n\n> A quoted observation.\n")

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.content.text, "> A quoted observation.\n")
        self.assertEqual(str(sut), text)

    def test_blank_content_raises_assertion_error(self) -> None:
        # `content` stays mandatory: a heading with no body (or a whitespace-only
        # body, which mdformat normalizes to nothing) fails the engine's
        # mandatory-field zero-extent check (REQ-004).
        for body in ("", "   \n"):
            with self.subTest(body=body):
                with self.assertRaises(AssertionError):
                    UpdateEntry.from_text(format_text(f"### 2026-08-26 00:00:00.000Z - Created\n{body}"))


class TestUpdatesACC002(unittest.TestCase):
    """ACC-002 (REQ-004): `Updates` requires >=1 entry, newest first (the shared helper)."""

    def test_zero_entries_raises_assertion_error(self) -> None:
        with self.assertRaises(AssertionError):
            Updates.from_text(format_text("## Updates\n"))

    def test_direct_construction_with_empty_list_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Updates(updates=[])

    def test_out_of_order_entries_rejected(self) -> None:
        """An older entry above a newer one fails the shared newest-first check (`ValidationError` channel)."""
        with self.assertRaises(ValidationError) as ctx:
            Updates.from_text(
                format_text(
                    "## Updates\n\n"
                    "### 2026-08-26 00:00:00.000Z - Created\n\nOlder entry first.\n\n"
                    "### 2026-08-27 00:00:00.000Z - Reviewed\n\nNewer entry second.\n"
                )
            )

        self.assertIn("entries must be newest-first", str(ctx.exception))

    def test_equal_timestamps_accepted(self) -> None:
        """Equal timestamps are allowed (the shared helper's non-strict `>=`)."""
        sut = Updates.from_text(
            format_text(
                "## Updates\n\n"
                "### 2026-08-26 00:00:00.000Z - First\n\nSame instant.\n\n"
                "### 2026-08-26T00:00:00.000+00:00 - Second\n\nSame instant again.\n"
            )
        )

        self.assertEqual(len(sut.updates), 2)
        self.assertEqual(sut.updates[0].timestamp, "2026-08-26 00:00:00.000Z")
        self.assertEqual(sut.updates[1].timestamp, "2026-08-26T00:00:00.000+00:00")

    def test_updates_with_leading_comment(self) -> None:
        # `Updates` is `MarkdownSection2WithComment` (mirroring VCR's own) --
        # the permanent "newest first" anchor comment directly under the
        # heading is part of the section, not the entries.
        text = format_text(
            "## Updates\n\n<!-- Newest entry first -- prepend new entries directly below this comment. -->\n\n"
            "### 2026-08-26 00:00:00.000Z - Created\n\nSome text.\n"
        )

        sut = Updates.from_text(text)

        self.assertIsNotNone(sut.comment)
        self.assertEqual(len(sut.updates), 1)
        self.assertEqual(str(sut), text)


class TestTxtReferenceDocumentRoundTrips(unittest.TestCase):
    """The full reference body parses, exposes its fields, and round-trips byte-exact (ACC-001)."""

    def test_round_trips(self) -> None:
        sut = Txt.from_text(_REFERENCE_TEXT)

        self.assertEqual(str(sut), _REFERENCE_TEXT)

    def test_title(self) -> None:
        sut = Txt.from_text(_REFERENCE_TEXT)

        self.assertEqual(sut.text, "Ad-hoc review notes")

    def test_body_is_opaque_verbatim(self) -> None:
        sut = Txt.from_text(_REFERENCE_TEXT)

        self.assertEqual(
            sut.body.text,
            "## Findings\n\nSome prose about what was found.\n\n- item one\n\n- item two\n\n"
            "### Detail\n\nMore prose under a free H3.\n\n```\n## Updates\n```\n",
        )

    def test_updates(self) -> None:
        sut = Txt.from_text(_REFERENCE_TEXT)

        self.assertIsNotNone(sut.updates.comment)
        self.assertEqual(len(sut.updates.updates), 2)
        self.assertEqual(sut.updates.updates[0].timestamp, "2026-08-27 00:00:00.000Z")
        self.assertEqual(sut.updates.updates[0].title, "Reviewed")
        self.assertEqual(sut.updates.updates[0].content.text, "The findings were reviewed.\n")
        self.assertEqual(sut.updates.updates[1].timestamp, "2026-08-26 00:00:00.000Z")
        self.assertEqual(sut.updates.updates[1].title, "Created")
        self.assertEqual(sut.updates.updates[1].content.text, "Initial draft of the review notes.\n")


if __name__ == "__main__":
    unittest.main()
