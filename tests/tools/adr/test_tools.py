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

"""Tests for the ``@mcp.tool()``-decorated ADR wrappers (plan §8, §9a)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.models.adr import (
    Adr,
    AdrBody,
    AdrFrontmatter,
    AdrOptionNotFoundError,
    AdrSectionError,
    render_adr,
)
from biz.dfch.specmgr.tools.adr._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
from biz.dfch.specmgr.tools.adr.tools import (
    create_adr,
    get_adr,
    option_create,
    option_delete,
    option_list,
    option_read,
    option_update,
    set_status,
    update_frontmatter,
    update_section,
    validate_adr,
)


def _body(**overrides: object) -> AdrBody:
    fields = {
        "title": "A title",
        "context_and_problem_statement": "Context.",
        "considered_options": "Options.",
        "decision_outcome": "Outcome.",
    }
    fields.update(overrides)
    return AdrBody(**fields)


class _TempAdrDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the ADR base dir via SPECMGR_ADR_DIR."""

    def setUp(self):
        self.base_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(self.base_dir)}))

    def _write(self, filename: str, adr: Adr) -> Path:
        path = self.base_dir / filename
        path.write_text(render_adr(adr), encoding="utf-8")
        return path

    def _existing_adr(self, id_: str = "existing-id", **body_overrides: object) -> Adr:
        adr = Adr(frontmatter=AdrFrontmatter(id=id_), body=_body(**body_overrides))
        self._write(f"{id_}.md", adr)
        return adr


class TestGetAdr(_TempAdrDirTestCase):
    """Tests for the get_adr tool."""

    def test_returns_matching_document(self):
        """get_adr must return the parsed document matching the given id."""
        self._existing_adr(id_="my-id")
        result = get_adr("my-id")
        self.assertEqual(result.frontmatter.id, "my-id")
        self.assertEqual(result.body.title, "A title")

    def test_raises_not_found_for_unknown_id(self):
        """get_adr must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            get_adr("no-such-id")


class TestCreateAdr(_TempAdrDirTestCase):
    """Tests for the create_adr tool."""

    def test_assigns_id_and_writes_expected_filename(self):
        """create_adr must assign a fresh id and write f'{id}-{slug}.md' under the base dir."""
        frontmatter = AdrFrontmatter(status="proposed")
        body = _body(title="My New Decision")
        result = create_adr(frontmatter, body)

        self.assertIsNotNone(result.frontmatter.id)
        expected_path = self.base_dir / f"{result.frontmatter.id}-my-new-decision.md"
        self.assertTrue(expected_path.exists())

        on_disk = get_adr(result.frontmatter.id)
        self.assertEqual(on_disk.body.title, "My New Decision")
        self.assertEqual(on_disk.frontmatter.status, "proposed")

    def test_ignores_caller_submitted_id(self):
        """Any id submitted in the frontmatter argument must be overwritten by a fresh one."""
        frontmatter = AdrFrontmatter(id="caller-supplied-id")
        result = create_adr(frontmatter, _body())
        self.assertNotEqual(result.frontmatter.id, "caller-supplied-id")

    def test_creates_base_dir_if_missing(self):
        """create_adr must create the ADR base directory if it does not exist yet."""
        nested = self.base_dir / "nested" / "adr-dir"
        with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(nested)}):
            result = create_adr(AdrFrontmatter(), _body(title="Nested"))
        self.assertTrue(nested.is_dir())
        self.assertTrue((nested / f"{result.frontmatter.id}-nested.md").exists())


class TestUpdateFrontmatter(_TempAdrDirTestCase):
    """Tests for the update_frontmatter tool."""

    def test_replaces_frontmatter_but_preserves_id(self):
        """update_frontmatter must apply the whole-object replace but keep the resolved id."""
        self._existing_adr(id_="keep-me")
        new_frontmatter = AdrFrontmatter(id="attacker-supplied-id", status="accepted")
        result = update_frontmatter("keep-me", new_frontmatter)

        self.assertEqual(result.frontmatter.id, "keep-me")
        self.assertEqual(result.frontmatter.status, "accepted")

        on_disk = get_adr("keep-me")
        self.assertEqual(on_disk.frontmatter.status, "accepted")
        self.assertEqual(on_disk.frontmatter.id, "keep-me")

    def test_raises_not_found_for_unknown_id(self):
        """update_frontmatter must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            update_frontmatter("no-such-id", AdrFrontmatter())


class TestUpdateSection(_TempAdrDirTestCase):
    """Tests for the update_section tool."""

    def test_replaces_section_on_disk(self):
        """update_section must write the new section content back to disk."""
        self._existing_adr(id_="doc-id")
        update_section("doc-id", "decision_drivers", "* A driver")
        on_disk = get_adr("doc-id")
        self.assertEqual(on_disk.body.decision_drivers, "* A driver")

    def test_section_error_propagates_and_does_not_write(self):
        """An AdrSectionError (e.g. removing a mandatory section) must propagate untouched."""
        self._existing_adr(id_="doc-id")
        with self.assertRaises(AdrSectionError):
            update_section("doc-id", "title", "")
        on_disk = get_adr("doc-id")
        self.assertEqual(on_disk.body.title, "A title")

    def test_raises_not_found_for_unknown_id(self):
        """update_section must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            update_section("no-such-id", "decision_drivers", "value")


class TestSetStatus(_TempAdrDirTestCase):
    """Tests for the set_status tool."""

    def test_sets_plain_status_on_disk(self):
        """set_status must write the new status back to disk."""
        self._existing_adr(id_="doc-id")
        set_status("doc-id", "accepted")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "accepted")

    def test_composes_superseded_by_status(self):
        """set_status with superseded_by must compose the 'superseded by ...' string."""
        self._existing_adr(id_="doc-id")
        set_status("doc-id", "accepted", superseded_by="other-id")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "superseded by other-id")

    def test_invalid_status_raises_and_does_not_write(self):
        """An invalid status must fail validation without writing."""
        self._existing_adr(id_="doc-id")
        with self.assertRaises(ValidationError):
            set_status("doc-id", "not-a-real-status")
        self.assertEqual(get_adr("doc-id").frontmatter.status, "draft")


class TestOptionTools(_TempAdrDirTestCase):
    """Tests for option_list/option_create/option_read/option_update/option_delete."""

    def test_option_list_empty_for_fresh_document(self):
        """option_list must return an empty list for a document with no options."""
        self._existing_adr(id_="doc-id")
        self.assertEqual(option_list("doc-id"), [])

    def test_option_create_writes_new_option_and_returns_full_title(self):
        """option_create must append the new option on disk and return its full title."""
        self._existing_adr(id_="doc-id")
        full_title = option_create("doc-id", "First option", "Some content.")
        self.assertEqual(full_title, "Option 1: First option")
        self.assertEqual(option_list("doc-id"), ["Option 1: First option"])
        self.assertEqual(option_read("doc-id", full_title), "Some content.")

    def test_option_update_replaces_content_on_disk(self):
        """option_update must replace the option's content on disk and return the new value."""
        self._existing_adr(id_="doc-id")
        full_title = option_create("doc-id", "First option", "Old content.")
        new_content = option_update("doc-id", full_title, "New content.")
        self.assertEqual(new_content, "New content.")
        self.assertEqual(option_read("doc-id", full_title), "New content.")

    def test_option_update_missing_raises(self):
        """option_update must raise AdrOptionNotFoundError for an unknown full_title."""
        self._existing_adr(id_="doc-id")
        with self.assertRaises(AdrOptionNotFoundError):
            option_update("doc-id", "Option 9: Missing", "value")

    def test_option_read_missing_raises(self):
        """option_read must raise AdrOptionNotFoundError for an unknown full_title."""
        self._existing_adr(id_="doc-id")
        with self.assertRaises(AdrOptionNotFoundError):
            option_read("doc-id", "Option 9: Missing")

    def test_option_delete_removes_option_and_returns_remaining(self):
        """option_delete must remove the option on disk and return the remaining titles."""
        self._existing_adr(id_="doc-id")
        option_create("doc-id", "First option", "content")
        second_title = option_create("doc-id", "Second option", "content")
        remaining = option_delete("doc-id", "Option 1: First option")
        self.assertEqual(remaining, [second_title])
        self.assertEqual(option_list("doc-id"), [second_title])

    def test_option_delete_missing_raises(self):
        """option_delete must raise AdrOptionNotFoundError for an unknown full_title."""
        self._existing_adr(id_="doc-id")
        with self.assertRaises(AdrOptionNotFoundError):
            option_delete("doc-id", "Option 9: Missing")


class TestValidateAdr(_TempAdrDirTestCase):
    """Tests for the validate_adr tool."""

    def test_returns_true_for_valid_document(self):
        """validate_adr must return True for a valid, parseable document."""
        self._existing_adr(id_="doc-id")
        self.assertIs(validate_adr("doc-id"), True)

    def test_raises_not_found_for_unknown_id(self):
        """validate_adr must raise AdrNotFoundError for an unknown id."""
        with self.assertRaises(AdrNotFoundError):
            validate_adr("no-such-id")


if __name__ == "__main__":
    unittest.main()
