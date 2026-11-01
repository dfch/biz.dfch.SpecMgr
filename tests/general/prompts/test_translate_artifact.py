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

"""Tests for the ``translate_artifact`` ``@mcp.prompt()`` (feat-197-i18n, Phase 130, REQ-011).

``translate_artifact`` is narration-only text (it returns instructions, it never translates or writes anything
itself), so these tests assert what the rendered instructions say: the load-bearing steps of the flow, the
closed-vocabulary never-translate list (REQ-010, incl. the ``prb`` ``problem_statement`` exemption), the argument
validation, and the registration. The deterministic surface the flow relies on is proven end to end, without an LLM,
in ``test_translate_artifact_flow.py``.
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.prompts import translate_artifact
from biz.dfch.specmgr.general.prompts.translate_artifact import translate_artifact as translate_fn
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS

_ID = "11111111-2222-3333-4444-555555555555"


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces (assertions span wrapped lines)."""
    result = " ".join(text.split())
    return result


class TestTranslateArtifactRendering(unittest.TestCase):
    """The rendered instructions carry the flow's load-bearing steps."""

    def test_arguments_are_interpolated(self):
        result = translate_fn("vcr", _ID, "de")
        self.assertIn("`vcr`", result)
        self.assertIn(_ID, result)
        self.assertIn("target language: `de`", result)
        self.assertIn("source language: `en`", result)
        self.assertIn("get_vcr", result)
        self.assertIn("create_vcr", result)
        self.assertIn("list_vcr", result)
        self.assertNotIn("$", result)  # every placeholder substituted

    def test_type_and_language_are_case_insensitive(self):
        self.assertEqual(translate_fn("Dec", _ID, "DE"), translate_fn("dec", _ID, "de"))

    def test_source_language_defaults_to_en_and_can_be_overridden(self):
        self.assertEqual(translate_fn("dec", _ID, "de"), translate_fn("dec", _ID, "de", "en"))
        # only `de` ships a table today, so the table probe is stubbed to exercise a non-default source language
        with mock.patch(
            "biz.dfch.specmgr.general.prompts.translate_artifact.resolve_heading_table", return_value={}
        ) as probe:
            result = translate_fn("dec", _ID, "de", "FR")
        self.assertIn("source language: `fr`", result)
        self.assertIn("target language: `de`", result)
        self.assertEqual([call.args[0] for call in probe.call_args_list], ["de", "fr"])

    def test_reads_the_i18n_resource_first(self):
        result = translate_fn("dec", _ID, "de")
        self.assertIn("## 1. Read the guidance first", result)
        self.assertIn("specmgr://i18n", result)
        self.assertLess(result.index("specmgr://i18n"), result.index("get_dec"))
        self.assertLess(result.index("## 1."), result.index("## 3."))

    def test_source_read_is_raw_with_language_and_a_parse_failure_stops_the_flow(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("Call `get_dec` with `id` = " + _ID + ', `raw=True` and `language="en"`', result)
        self.assertIn("`ParseFailureResult`", result)
        self.assertIn("Stop and report the `error` and `path`", result)
        self.assertIn("name the `repair` prompt", result)
        self.assertIn("Never translate a broken source", result)

    def test_create_versus_update_decision(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("## 4. Decide create or update", result)
        self.assertIn("`get_dec` with `id` = " + _ID + ', `raw=True` and `language="de"`', result)
        self.assertIn("**create**", result)
        self.assertIn(f'`create_dec(content, language="de", id={_ID})`', result)
        self.assertIn("**update**", result)
        self.assertIn("whole-body `update`", result)
        self.assertIn("`edit`", result)
        self.assertIn("do not overwrite it", result)
        self.assertIn("`FileExistsError` means the variant exists", result)

    def test_heading_table_step_reads_the_resource_first_with_the_file_only_as_fallback(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("## 5. Load the heading table", result)
        self.assertIn("from the resource `specmgr://i18n/headings/de`", result)
        self.assertIn("whose **value** is that heading", result)
        self.assertLess(result.index("specmgr://i18n/headings/de"), result.index("general/data/headings/de.json"))
        self.assertIn("Only if your host cannot read MCP resources at all, fall back to reading the JSON file", result)
        self.assertIn("general/data/headings/de.json", result)
        self.assertIn("keep every heading canonical English", result)
        # step 5 does not depend on host file tools for the happy path
        self.assertNotIn("Read the target language's heading table: the JSON file", result)

    def test_non_en_source_reads_the_source_table_through_the_resource_too(self):
        with mock.patch("biz.dfch.specmgr.general.prompts.translate_artifact.resolve_heading_table", return_value={}):
            result = _one_line(translate_fn("dec", _ID, "de", "fr"))
        self.assertIn("`specmgr://i18n/headings/de`", result)
        self.assertIn("also read `specmgr://i18n/headings/fr`", result)

    def test_a_failing_table_resource_read_is_a_stop_condition(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("any tool call or resource read (including the heading-table read of step 5)", result)
        self.assertIn("no heading-mapping table", result)
        self.assertIn("A read that raises the no-table `ValueError` is a stop condition (step 2)", result)

    def test_never_translate_list_is_complete(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("Never translate (closed vocabulary and schema constants, REQ-010)", result)
        for token in (
            "`MUST`",
            "`SHOULD NOT`",
            "`MAY`",
            "## Priority",
            "`transfer`",
            "`accept`",
            "`reduce`",
            "`avoid`",
            "### Probability N",
            "### Impact N",
            "`full`",
            "`partial`",
            "`none`",
            "### AC-NNN (Method)",
            "`Demonstration`",
            "`Inspection`",
            "`Special`",
            "### Option N:",
            "### Step N:",
            "### Extension Na.",
            "`Subfunction`",
            "**<d>.<NNNN>**: ",
            "TODO: answer pending",
            "`[ ]` / `[x]`",
            "<TAG> <uuid>: <title>",
            "timestamps",
        ):
            with self.subTest(token=token):
                self.assertIn(token, result)

    def test_prb_problem_statement_exemption_is_stated(self):
        result = _one_line(translate_fn("prb", _ID, "de"))
        self.assertIn("`problem_statement` lead paragraph", result)
        self.assertIn("stays canonical English in every language", result)
        self.assertIn("byte for byte", result)
        self.assertIn("ADR 38efdb66 item 11", result)

    def test_structure_and_soft_wrap_rules(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("same headings in the same order", result)
        self.assertIn("Do not soft-wrap a list item", result)

    def test_write_step_retries_on_a_non_raising_validate_result_and_never_dry_runs(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("generic `validate` tool is English/canonical-only and has no `language` parameter", result)
        self.assertIn("non-raising `ValidateResult` with `valid=False`", result)
        self.assertIn("nothing was written", result)
        self.assertIn("Make at most 3 write attempts", result)
        self.assertIn("`create_dec` with `content` = the translated body", result)
        self.assertIn('whole-body `update` with `type="dec"`', result)

    def test_verification_and_report_steps(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("## 8. Verify against what is on disk", result)
        self.assertIn("`get_dec` with `id` = " + _ID + ' and `language="de"`', result)
        self.assertIn('`list_dec(language="de")` returns one row per variant, each with its `path`', result)
        self.assertIn("## 9. Report", result)

    def test_no_table_stops_the_flow_without_inventing_one(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("no heading-mapping table", result)
        self.assertIn("Do not invent a table", result)
        self.assertIn("general/data/headings/<language>.json", result)

    def test_never_commit_never_english_never_frontmatter(self):
        result = _one_line(translate_fn("dec", _ID, "de"))
        self.assertIn("Never commit, never write the English document", result)
        self.assertIn("never change a document's frontmatter `id` or `status`", result)
        self.assertIn("Do not commit, do not write the English document", result)

    def test_scope_statement_excludes_feat_and_adr(self):
        result = _one_line(translate_fn("req", _ID, "de"))
        self.assertIn("`feat` and `adr` are always English and are out of scope", result)

    def test_question_tool_and_todo_list(self):
        result = translate_fn("req", _ID, "de")
        self.assertIn("todo list", result)
        self.assertIn("`question` tool", result)

    def test_no_reference_to_unimplemented_tools(self):
        result = translate_fn("req", _ID, "de").lower()
        self.assertNotIn("drift", result)
        self.assertNotIn("list_languages", result)

    def test_renders_for_every_language_aware_domain(self):
        for domain in LANGUAGE_AWARE_DOMAINS:
            with self.subTest(domain=domain):
                result = translate_fn(domain, _ID, "de")
                self.assertIn(f"get_{domain}", result)
                self.assertIn(f"create_{domain}", result)
                self.assertNotIn("$", result)


class TestTranslateArtifactValidation(unittest.TestCase):
    """The argument validation fails fast (ValueError) before any text is rendered."""

    def test_feat_is_rejected_as_always_english(self):
        with self.assertRaises(ValueError) as ctx:
            translate_fn("feat", "feat-1-x", "de")
        self.assertIn("feat", str(ctx.exception))
        self.assertIn("always English", str(ctx.exception))

    def test_adr_is_rejected_as_always_english(self):
        with self.assertRaises(ValueError) as ctx:
            translate_fn("adr", _ID, "de")
        self.assertIn("adr", str(ctx.exception))
        self.assertIn("always English", str(ctx.exception))

    def test_unknown_type_is_rejected_with_the_allowed_domains_named(self):
        with self.assertRaises(ValueError) as ctx:
            translate_fn("bogus", _ID, "de")
        self.assertIn("bogus", str(ctx.exception))
        for domain in LANGUAGE_AWARE_DOMAINS:
            self.assertIn(domain, str(ctx.exception))

    def test_blank_id_is_rejected(self):
        with self.assertRaises(ValueError):
            translate_fn("dec", "   ", "de")

    def test_english_target_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            translate_fn("dec", _ID, "en")
        self.assertIn("never", str(ctx.exception))

    def test_same_source_and_target_is_rejected(self):
        with self.assertRaises(ValueError):
            translate_fn("dec", _ID, "de", "de")

    def test_malformed_language_is_rejected_by_the_path_safety_shape_guard(self):
        for bad in ("../../etc", "d", "deu", "d3", ""):
            with self.subTest(language=bad):
                with self.assertRaises(ValueError):
                    translate_fn("dec", _ID, bad)
        with self.assertRaises(ValueError):
            translate_fn("dec", _ID, "de", "../x")

    def test_language_without_a_heading_table_is_rejected_actionably(self):
        with self.assertRaises(ValueError) as ctx:
            translate_fn("dec", _ID, "fr")
        self.assertIn("no heading-mapping table", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx2:
            translate_fn("dec", _ID, "de", "fr")
        self.assertIn("no heading-mapping table", str(ctx2.exception))


class TestTranslateArtifactPackagedInstructions(unittest.TestCase):
    """The text comes from the packaged data file, read fresh on every call."""

    def test_instructions_loaded_from_packaged_data_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "general_translate_artifact_instructions.md"
            instructions_path.write_text("first $type / $id / $language / $source_language", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = translate_fn("req", _ID, "de")
                instructions_path.write_text("second $type", encoding="utf-8")
                second = translate_fn("req", _ID, "de")

            self.assertEqual(first, f"first req / {_ID} / de / en")
            self.assertEqual(second, "second req")

    def test_raises_file_not_found_when_instructions_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    translate_fn("req", _ID, "de")


class TestTranslateArtifactRegistration(unittest.TestCase):
    """The ``general.prompts`` package exposes the prompt and the live ``mcp`` registration carries it."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_exposed_in_package_all(self):
        import biz.dfch.specmgr.general.prompts as general_prompts

        self.assertIn("translate_artifact", general_prompts.__all__)
        self.assertIs(general_prompts.translate_artifact, translate_artifact)

    def test_registered_on_mcp_server_exactly_once_with_the_right_arguments(self):
        matching = [p for p in self._prompts if p.name == "translate_artifact"]
        self.assertEqual(len(matching), 1)
        arguments = {argument.name: argument.required for argument in (matching[0].arguments or [])}
        self.assertEqual(arguments, {"type": True, "id": True, "language": True, "source_language": False})

    def test_description_names_the_load_bearing_points(self):
        matching = [p for p in self._prompts if p.name == "translate_artifact"]
        description = _one_line(matching[0].description or "")
        for phrase in (
            "specmgr://i18n",
            "feat and adr are always English",
            "ValidateResult",
            "problem_statement",
            "Never commits",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, description)

    def test_no_translating_tool_was_registered(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name for tool in asyncio.run(mcp.list_tools())}
        # `check_translation_drift` (feat-197-i18n Phase 140) is the one read-only tool whose name mentions
        # translation: it compares a variant with its source and never translates, writes, or calls an LLM.
        self.assertEqual({name for name in tools if "translat" in name.lower()}, {"check_translation_drift"})


if __name__ == "__main__":
    unittest.main()
