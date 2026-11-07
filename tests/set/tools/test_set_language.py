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

"""Tool-level language-variant tests for ``set`` (feat-173-req-iso29148-level-set Phase 180).

The parametrized ``tests/general/tools/test_i18n_all_domains.py`` drives the packaged example/template only; these
tests add what it cannot see for the opaque ``## Description``: the two table-mapped schema headings
(``## Beschreibung``/``## Elemente``) parse to the canonical keys, a variant whose *free* nested description
headings are not table keys keeps them verbatim through ``create_set``/``get_set``/``list_set`` and the generic
``update``, and a variant missing a translated schema heading is rejected without a write.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.set.models.v1 import SetDocument
from biz.dfch.specmgr.set.tools.create_set import create_set
from biz.dfch.specmgr.set.tools.get_set import get_set
from biz.dfch.specmgr.set.tools.list_set import list_set

_EN_BODY = """# Review Set

## Description

Some prose.

### Hintergrund

A free nested heading.

## Items

- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
"""

_DE_BODY = """# Review-Set

## Beschreibung

Etwas Prosa.

### Hintergrund

Ein freier Absatz.

## Elemente

- REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
"""


class TestSetLanguageVariant(unittest.TestCase):
    """A ``de`` variant of a ``set`` document parses its translated schema headings to canonical keys and keeps
    its free nested description headings verbatim."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))
        self.id = create_set(_EN_BODY).id
        create_set(_DE_BODY, language="de", id=self.id)

    def test_get_set_parsed_model_has_canonical_keys_and_keeps_free_headings(self) -> None:
        result = get_set(self.id, language="de")

        self.assertIsInstance(result, SetDocument)
        self.assertEqual(result.body.text, "Review-Set")
        self.assertEqual(len(result.body.items.items), 1)
        rendered = str(result.body)
        self.assertIn("## Description", rendered)
        self.assertIn("## Items", rendered)
        # the free nested heading (not a table key) stays verbatim in the model
        self.assertIn("### Hintergrund", rendered)

    def test_get_set_raw_returns_the_variant_body_verbatim(self) -> None:
        result = get_set(self.id, raw=True, language="de")

        self.assertIsInstance(result, str)
        self.assertIn("## Beschreibung", result)
        self.assertIn("## Elemente", result)
        self.assertIn("### Hintergrund", result)

    def test_list_set_lists_the_variant(self) -> None:
        result = list_set(language="de")

        self.assertEqual(result.total, 1)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(result.results[0].id, self.id)

    def test_update_with_translated_headings_in_a_variant_is_accepted_and_persisted_verbatim(self) -> None:
        new_body = _DE_BODY.replace("Etwas Prosa.", "Mehr Prosa.")

        update(self.id, "set", new_body, language="de")
        result = get_set(self.id, raw=True, language="de")

        self.assertIsInstance(result, str)
        self.assertIn("Mehr Prosa.", result)
        self.assertIn("## Beschreibung", result)

    def test_variant_without_the_translated_items_heading_is_rejected_without_a_write(self) -> None:
        before = get_set(self.id, raw=True, language="de")
        broken = _DE_BODY.replace("## Elemente", "## Zusammenfassung zwei")

        result = update(self.id, "set", broken, language="de")

        self.assertFalse(getattr(result, "valid", True))
        self.assertEqual(get_set(self.id, raw=True, language="de"), before)

    def test_broken_variant_surfaces_as_parse_failure_result(self) -> None:
        path = next((self.docs_root / "set" / "de").glob("*.md"))
        path.write_text(path.read_text().replace("## Elemente", "## Nope"))

        result = get_set(self.id, language="de")

        self.assertIsInstance(result, ParseFailureResult)


if __name__ == "__main__":
    unittest.main()
