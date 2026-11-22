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

"""feat-253-md-line-offset ACC-003 (rsk part): a `self._line`-based `rsk` message reports the true line.

`rsk/models/v1/tara.py`'s `QuadrantItem.strategy` builds its message from
`self._line`, which the shared `models/md` engine sets. The packaged
`rsk/data/rsk_tara.md` (the real TARA guidance document behind
`specmgr://rsk/tara`) with one quadrant bullet's strategy word un-backticked
fails that check, and the message must name the bullet's line in the
normalized text that `parse_tara` parses (`format_text` of the document).

The `Probability`/`Impact` messages of `assessment.py` are not used here: the
heading `@alias` rejects a bad heading at parse time first, so their
`self._line` messages cannot be reached through the engine.
"""

from __future__ import annotations

import unittest
from importlib.resources import files

import pydantic
import pytest

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1 import parse_tara

#: The quadrant bullet whose strategy word is un-backticked.
_VALID_BULLET = "- **High probability / high impact → `avoid`**"

#: The same bullet with the strategy word un-backticked, which `QuadrantItem.strategy` rejects.
_INVALID_BULLET = "- **High probability / high impact → avoid**"


class TestTaraQuadrantItemLineReference(unittest.TestCase):
    """ACC-003 (rsk part): `QuadrantItem.strategy`'s message names the bullet's normalized-body line."""

    @pytest.mark.xfail(strict=True, reason="feat-253: fixed in Phase 110")
    def test_invalid_quadrant_bullet_reports_its_normalized_body_line(self) -> None:
        source = files("biz.dfch.specmgr.rsk.data").joinpath("rsk_tara.md").read_text(encoding="utf-8")
        assert source.count(_VALID_BULLET) == 1, f"{_VALID_BULLET!r} must occur exactly once in rsk_tara.md."
        text = source.replace(_VALID_BULLET, _INVALID_BULLET)
        lines = format_text(text).splitlines()
        expected_line = lines.index(_INVALID_BULLET) + 1

        with self.assertRaises(pydantic.ValidationError) as ctx:
            parse_tara(text)

        self.assertIn(f"Tara > WhenToApply > QuadrantItem (line {expected_line}): ", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
