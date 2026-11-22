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

"""feat-253-md-line-offset ACC-004: the issue's `dec` `## Decision Outcome` repro (GitHub issue #253).

The packaged `dec/data/dec_example.md`, with its `## Decision Outcome` lead
paragraph followed by a second paragraph and a block quote: feat-247's relaxed
rule accepts the second paragraph as `further_blocks` but not the block quote,
so `parse_dec` fails with "text left over after processing all fields". The
message must name the block quote's line in the normalized body that
`parse_dec_body` builds (`format_text` of the frontmatter-stripped content).
The expected line is computed from that body (the first line that starts
with `> `), not taken from the issue.
"""

from __future__ import annotations

import unittest
from importlib.resources import files

import frontmatter

from biz.dfch.specmgr.dec.models.v1.parser import parse_dec
from biz.dfch.specmgr.models.md._markdown import format_text

#: The last line of `dec_example.md`'s `## Decision Outcome` lead paragraph.
_LEAD_END = "and two home-working days per week.\n"

#: The second paragraph and the block quote added after the lead paragraph.
_ADDED_BLOCKS = "\nA second paragraph of the outcome.\n\n> A block quote inside the outcome.\n"


def _repro_text() -> str:
    """Return `dec_example.md` with a second paragraph and a block quote added to `## Decision Outcome`.

    Returns:
        The complete document text, frontmatter included.
    """
    text = files("biz.dfch.specmgr.dec.data").joinpath("dec_example.md").read_text(encoding="utf-8")
    assert text.count(_LEAD_END) == 1, f"{_LEAD_END!r} must occur exactly once in dec_example.md."
    result = text.replace(_LEAD_END, _LEAD_END + _ADDED_BLOCKS)
    return result


class TestDecisionOutcomeLeftOverLineReference(unittest.TestCase):
    """ACC-004: the "text left over" line of the issue's repro is the block quote's normalized-body line."""

    def test_text_left_over_reports_the_block_quote_line(self) -> None:
        text = _repro_text()
        body = format_text(frontmatter.loads(text).content)
        expected_line = next(index for index, line in enumerate(body.splitlines(), start=1) if line.startswith("> "))

        with self.assertRaises(AssertionError) as ctx:
            parse_dec(text)

        message = str(ctx.exception)
        self.assertTrue(message.startswith("Decision > DecisionOutcome: text left over"), message)
        self.assertIn(f"starting at line {expected_line} of the normalized body", message)


if __name__ == "__main__":
    unittest.main()
