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

"""Tool-level language-variant tests for ``txt`` (feat-229-txt Phase 180, review findings E1/G3).

The parametrized ``tests/general/tools/test_i18n_all_domains.py`` drives the packaged example/template only; these
tests add what it cannot see for the opaque ``txt`` body: a variant whose *free* body headings collide with
heading-table keys keeps them verbatim through ``create_txt``/``get_txt``/``list_txt`` and the generic ``update``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.txt.models.v1 import TxtDocument
from biz.dfch.specmgr.txt.tools.create_txt import create_txt
from biz.dfch.specmgr.txt.tools.get_txt import get_txt
from biz.dfch.specmgr.txt.tools.list_txt import list_txt

_EN_BODY = """# Review Notes

## Summary

Some prose.

## Updates

### 2026-08-31 00:00:00.000Z - Created

Initial draft.
"""

_DE_BODY = """# Review-Notizen

## Zusammenfassung

Etwas Prosa.

### Quelle

Ein freier Absatz.

## Aktualisierungen

### 2026-08-31 00:00:00.000Z - Angelegt

Erster Entwurf.
"""


class TestTxtLanguageVariant(unittest.TestCase):
    """A ``de`` variant of a ``txt`` document keeps its free body headings verbatim."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        self.id = create_txt(_EN_BODY).id
        create_txt(_DE_BODY, language="de", id=self.id)

    def test_get_txt_parsed_model_keeps_free_headings(self) -> None:
        result = get_txt(self.id, language="de")

        self.assertIsInstance(result, TxtDocument)
        rendered = str(result.body)
        self.assertIn("## Zusammenfassung", rendered)
        self.assertIn("### Quelle", rendered)
        self.assertNotIn("## Summary", rendered)
        self.assertNotIn("### Source", rendered)
        self.assertEqual(len(result.body.updates.updates), 1)

    def test_get_txt_raw_returns_the_variant_body_verbatim(self) -> None:
        result = get_txt(self.id, raw=True, language="de")

        self.assertIsInstance(result, str)
        self.assertIn("## Zusammenfassung", result)
        self.assertIn("## Aktualisierungen", result)

    def test_list_txt_lists_the_variant(self) -> None:
        result = list_txt(language="de")

        self.assertEqual(result.total, 1)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.results[0].id, self.id)

    def test_update_with_free_headings_in_a_variant_is_accepted_and_persisted_verbatim(self) -> None:
        new_body = _DE_BODY.replace("Etwas Prosa.", "Mehr Prosa.\n\n## Beschreibung\n\nText.")

        update(self.id, "txt", new_body, language="de")
        result = get_txt(self.id, raw=True, language="de")

        self.assertIsInstance(result, str)
        self.assertIn("## Beschreibung", result)
        self.assertNotIn("## Description", result)

    def test_variant_without_the_translated_updates_heading_is_rejected_without_a_write(self) -> None:
        before = get_txt(self.id, raw=True, language="de")
        broken = _DE_BODY.replace("## Aktualisierungen", "## Zusammenfassung zwei")

        result = update(self.id, "txt", broken, language="de")

        self.assertFalse(getattr(result, "valid", True))
        self.assertEqual(get_txt(self.id, raw=True, language="de"), before)

    def test_broken_variant_surfaces_as_parse_failure_result(self) -> None:
        path = next((self.docs_root / "txt" / "de").glob("*.md"))
        path.write_text(path.read_text().replace("## Aktualisierungen", "## Nope"))

        result = get_txt(self.id, language="de")

        self.assertIsInstance(result, ParseFailureResult)


if __name__ == "__main__":
    unittest.main()
