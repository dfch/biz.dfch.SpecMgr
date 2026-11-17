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

"""Tests for the ``feat`` domain package docstring's prompt enumeration (feat-263-delegation-prompts, Phase 150).

The ``feat`` domain package docstring carries a "Prompts:" sentence
enumerating the domain's MCP prompts; Phase 110 registered
``implement_feat``/``review_feat`` without updating it (the post-done
review's D1), so the stale text propagated into the committed generated
mirror ``docs/api/biz.dfch.specmgr.feat.md``. These tests pin the
enumeration: the five current prompt names must each appear in the
domain package docstring, and every name in
``feat/prompts/__init__.py``'s ``__all__`` must appear there too (the
drift pin -- a future prompt registration that forgets the docstring
fails here).
"""

from __future__ import annotations

import unittest


class TestFeatPackageDocstringPrompts(unittest.TestCase):
    """The ``feat`` domain package docstring's "Prompts:" sentence names every registered prompt."""

    def test_all_five_prompt_names_appear_in_package_docstring(self):
        """create_feat/update_feat/refine_feat/implement_feat/review_feat must all be named in the docstring."""
        import biz.dfch.specmgr.feat as feat_pkg

        doc = feat_pkg.__doc__ or ""
        for name in ("create_feat", "update_feat", "refine_feat", "implement_feat", "review_feat"):
            self.assertIn(name, doc, f"the feat package docstring's prompt enumeration is missing {name!r}")

    def test_every_prompt_all_name_appears_in_package_docstring(self):
        """Every name in feat.prompts.__all__ must appear in the docstring (the drift pin)."""
        import biz.dfch.specmgr.feat as feat_pkg
        import biz.dfch.specmgr.feat.prompts as feat_prompts

        doc = feat_pkg.__doc__ or ""
        for name in feat_prompts.__all__:
            self.assertIn(
                name,
                doc,
                f"the feat package docstring's prompt enumeration is missing {name!r} from feat.prompts.__all__",
            )


if __name__ == "__main__":
    unittest.main()
