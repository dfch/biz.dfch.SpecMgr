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

"""Tests for the ``create_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import DecDocument, DecFrontmatter, parse_dec
from biz.dfch.specmgr.dec.tools._paths import dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

from ._helpers import MANDATORY_ROLES_AND_SOURCE

_MINIMAL_BODY = (
    textwrap.dedent(
        """\
        # Choose a Document Store

        ## Context and Problem Statement

        The current store cannot serve the dashboard read path.

        ## Decision Outcome

        We chose the document store.
        """
    )
    + MANDATORY_ROLES_AND_SOURCE
)

# Structurally valid, but a field/cross-field failure: two `### Option 1:`
# headings are duplicate option numbers (the `Decision` after-validator's
# `ValidationError` channel).
_BAD_OPTION_BODY = (
    textwrap.dedent(
        """\
        # Choose a Document Store

        ## Context and Problem Statement

        The current store cannot serve the dashboard read path.

        ## Decision Outcome

        We chose the document store.
        """
    )
    + MANDATORY_ROLES_AND_SOURCE
    + textwrap.dedent(
        """\

        ## Pros and Cons

        ### Option 1: Document Store

        Meets the latency budget.

        ### Option 1: Key-Value Store

        Even faster reads.
        """
    )
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized decision sections.\n"

#: The minimal DE body for the variant-create placement test: every fixed-text heading translated per the
#: packaged de table (the only table-closed language, feat-197-i18n), the H1 free in German.
_DE_MINIMAL_BODY = textwrap.dedent(
    """\
    # Dokumentlager w\u00e4hlen

    ## Kontext und Problembeschreibung

    Der aktuelle Store kann den Dashboard-Lesepfad nicht bedienen.

    ## Entscheidungsergebnis

    Wir haben das Dokumentlager gew\u00e4hlt.

    ## Rollen und Verantwortlichkeiten

    ### Endverantwortlich

    Die f\u00fchrende Plattformarchitektin.

    ### Durchf\u00fchrend

    - Das Order-Service-Team.

    ## Quelle

    Die Incident-Review-Meeting zum Dashboard-Latenz-Vorfall.
    """
)


class TempDecDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateDec(TempDecDirTestCase):
    """Tests for the create_dec tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_dec must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_dec(_MINIMAL_BODY)

        self.assertIsInstance(result, DecFrontmatter)
        self.assertNotIsInstance(result, DecDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "dec")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_dec(result.id)
        self.assertEqual(fetched.body.text, "Choose a Document Store")

    def test_writes_expected_filename(self) -> None:
        """create_dec must write the prefix-less f'{id}-{slug}.md' in the id's shard dir under docs/dec/en/,
        leaving nothing directly under docs/dec/ or docs/dec/en/ (feat-245, ACC-001)."""
        result = create_dec(_MINIMAL_BODY)

        expected_path = dec_base_dir("en") / result.id[:2] / f"{result.id}-choose-a-document-store.md"
        self.assertTrue(expected_path.exists())
        self.assertEqual(list((self.docs_root / "dec").glob("*.md")), [])
        self.assertEqual(list((self.docs_root / "dec" / "en").glob("*.md")), [])

    def test_written_file_round_trips_via_parse_dec(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_dec(_MINIMAL_BODY)

        expected_path = dec_base_dir("en") / result.id[:2] / f"{result.id}-choose-a-document-store.md"
        on_disk = parse_dec(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Choose a Document Store")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_dec must create the decision base directory if it does not exist yet."""
        self.assertFalse(dec_base_dir().exists())

        create_dec(_MINIMAL_BODY)

        self.assertTrue(dec_base_dir().is_dir())

    def test_invalid_content_returns_validate_result_and_writes_nothing(self) -> None:
        """A structurally invalid body must return ``ValidateResult(valid=False, ...)`` and write no
        file at all (feat-204-create-error, Phase 110)."""
        result = create_dec(_MALFORMED_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("dec create_dec (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(dec_base_dir().exists())

    def test_field_validation_failure_returns_validate_result_and_writes_nothing(self) -> None:
        """A field-level validation failure (duplicate `### Option 1:` number) must return
        ``ValidateResult(valid=False, ...)`` and write nothing (feat-204-create-error, Phase 110)."""
        result = create_dec(_BAD_OPTION_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("dec create_dec (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(dec_base_dir().exists())


class TestCreateDecVariantShardedPlacement(TempDecDirTestCase):
    """create_dec's variant create (language='de', the table-closed language) writes the sharded variant path
    (feat-245, ACC-008)."""

    def test_variant_is_written_in_the_language_shard_under_the_en_basename(self) -> None:
        """The de variant must live at docs/dec/de/<id[:2]>/<uuid>-<slug>.md -- the EN source's exact basename
        in the language's own shard dir (DEC 38efdb66 item 2) -- leaving nothing directly under docs/dec/de/,
        and the EN source prefix-less in its own shard under docs/dec/en/ (ACC-001, ACC-008)."""
        created = create_dec(_MINIMAL_BODY)
        assert isinstance(created, DecFrontmatter)
        assert created.id is not None
        variant = create_dec(_DE_MINIMAL_BODY, language="de", id=created.id)
        assert isinstance(variant, DecFrontmatter)
        self.assertEqual(variant.id, created.id)

        expected_path = dec_base_dir("de") / created.id[:2] / f"{created.id}-choose-a-document-store.md"
        self.assertTrue(expected_path.exists())
        self.assertEqual(list((self.docs_root / "dec" / "de").glob("*.md")), [])
        en_expected = dec_base_dir("en") / created.id[:2] / f"{created.id}-choose-a-document-store.md"
        self.assertTrue(en_expected.exists())
        self.assertEqual(list((self.docs_root / "dec").glob("*.md")), [])
        self.assertEqual(list((self.docs_root / "dec" / "en").glob("*.md")), [])


if __name__ == "__main__":
    unittest.main()
