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

"""Unit tests for the domain-agnostic embedding-input text extraction (feat-134, Phase 2, Task 2.2).

Covers the REQ-005/REQ-009 extraction contract: the title (first H1), the
frontmatter fields minus the bookkeeping keys (only ``classification``
survives across the whole-body domains), and the raw frontmatter-stripped body
for a parseable document; and the ``FAILED_TO_PARSE_MARKER`` degradation
(full raw text, ``id = None``) for an unparseable one.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER
from biz.dfch.specmgr.general.tools._similarity_text import (
    BOOKKEEPING_FRONTMATTER_KEYS,
    SimilarityText,
    compose_embedding_text,
    failed_similarity_text,
    first_h1,
)


class TestFirstH1(unittest.TestCase):
    """The first level-1 ATX heading's title is the document title."""

    def test_returns_first_h1_title(self) -> None:
        body = "# My Title\n\nSome prose.\n\n## Section\n\nMore."

        result = first_h1(body)

        self.assertEqual(result, "My Title")

    def test_h2_does_not_match(self) -> None:
        body = "## Only a level-two heading\n\nProse."

        result = first_h1(body)

        self.assertIsNone(result)

    def test_no_heading_returns_none(self) -> None:
        result = first_h1("Just prose, no headings at all.")

        self.assertIsNone(result)

    def test_first_h1_wins_over_later_headings(self) -> None:
        body = "Intro line.\n\n# Real Title\n\n# Later H1\n\n## Section"

        result = first_h1(body)

        self.assertEqual(result, "Real Title")

    def test_trailing_whitespace_stripped(self) -> None:
        result = first_h1("# Padded Title   \n\nBody.")

        self.assertEqual(result, "Padded Title")


class TestBookkeepingKeys(unittest.TestCase):
    """REQ-005: the excluded frontmatter key set is exactly the bookkeeping keys (incl. ``status``)."""

    def test_exact_key_set(self) -> None:
        expected = frozenset({"id", "type", "version", "created", "updated", "status"})

        self.assertEqual(BOOKKEEPING_FRONTMATTER_KEYS, expected)

    def test_status_is_excluded(self) -> None:
        self.assertIn("status", BOOKKEEPING_FRONTMATTER_KEYS)


class TestComposeEmbeddingText(unittest.TestCase):
    """REQ-005: title + surviving frontmatter fields + raw body, joined by newlines."""

    def test_keeps_only_non_bookkeeping_non_none_fields(self) -> None:
        frontmatter = {
            "id": "some-uuid",
            "type": "req",
            "version": "1.0.0",
            "created": "2026-01-01 00:00:00.000Z",
            "updated": "2026-01-02 00:00:00.000Z",
            "status": "draft",
            "classification": "confidential",
            "something_none": None,
        }

        result = compose_embedding_text("The Title", frontmatter, "The body text.")

        expected = "The Title\nclassification: confidential\nThe body text."
        self.assertEqual(result, expected)

    def test_no_surviving_fields_is_title_plus_body(self) -> None:
        frontmatter = {"id": "x", "type": "req", "status": "draft"}

        result = compose_embedding_text("T", frontmatter, "B")

        self.assertEqual(result, "T\nB")

    def test_title_is_not_deduplicated_against_body(self) -> None:
        # The deliberate double weighting of the title signal: it appears both as its own
        # line and again wherever the body repeats it.
        result = compose_embedding_text("T", {}, "T again in the body")

        self.assertEqual(result, "T\nT again in the body")

    def test_fields_keep_mapping_order(self) -> None:
        frontmatter = {"b": 2, "a": 1}

        result = compose_embedding_text("T", frontmatter, "B")

        self.assertEqual(result, "T\nb: 2\na: 1\nB")


class TestFailedSimilarityText(unittest.TestCase):
    """REQ-009: an unparseable document degrades to the marker row with its full raw text."""

    def test_marker_fields_and_full_raw_text(self) -> None:
        raw = "---\nid: [broken\n---\n\n# Broken\n\nProse."

        result = failed_similarity_text(raw)

        self.assertIsInstance(result, SimilarityText)
        self.assertEqual(result.embedding_text, raw)  # the full raw file text, not a frontmatter split
        self.assertEqual(result.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(result.status, FAILED_TO_PARSE_MARKER)
        self.assertIsNone(result.id_)


if __name__ == "__main__":
    unittest.main()
