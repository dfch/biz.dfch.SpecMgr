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

"""Tests for the `specmgr://i18n` resource (`general.resources.i18n.i18n`, feat-197-i18n Phase 130).

The resource serves the packaged i18n guidance (``general/data/general_i18n.md``) as raw markdown (no dedicated
parse model, like ``specmgr://reference-graph``). Because the document is what the ``translate_artifact`` flow reads
first, these tests pin (a) the registration and the verbatim passthrough, (b) that the never-translate list covers
every closed-vocabulary token family REQ-010 names (and the ``prb`` ``problem_statement`` exemption of ADR 38efdb66
item 11), (c) that it describes the implemented layout/vocabulary/guard behavior, and (d) -- against the real models --
that the tokens its "schema-enforced" column lists really are rejected when translated (the full domain matrix lives in
``tests/general/prompts/test_translate_artifact_flow.py``), so the guidance cannot silently drift from the schemas.
"""

import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mcp.server.mcpserver.resources.base import Resource

from biz.dfch.specmgr.general.models.heading_table import load_heading_table, reset_heading_table_cache
from biz.dfch.specmgr.general.resources.i18n import i18n, i18n_headings
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from biz.dfch.specmgr.general.tools._path_safety import LANGUAGE_PATTERN
from biz.dfch.specmgr.server import mcp


def _registered_resource(uri: str) -> Resource:
    """Return the registered Resource model for `uri` from the server's resource manager."""
    result = [resource for resource in mcp._resource_manager.list_resources() if resource.uri == uri]
    assert len(result) == 1, f"expected exactly one registration for {uri}, got {len(result)}"
    return result[0]


def _flat(text: str) -> str:
    """Collapse the hard-wrapped markdown's line breaks to single spaces (phrases may span physical lines)."""
    result = " ".join(text.split())
    return result


def _section(text: str, heading: str) -> str:
    """Return the text of the `## ` / `### ` section starting at `heading` up to the next heading of the same level."""
    level = heading.split(" ", 1)[0]
    start = text.index(heading)
    rest = text[start + len(heading) :]
    match = re.search(rf"(?m)^{re.escape(level)} ", rest)
    result = text[start : start + len(heading) + (match.start() if match else len(rest))]
    return result


class TestI18nResource(unittest.TestCase):
    """Registration, verbatim passthrough, and read-failure behavior."""

    def test_is_registered_with_markdown_mime_type(self):
        resource = _registered_resource("specmgr://i18n")

        self.assertEqual(resource.name, "i18n")
        self.assertEqual(resource.mime_type, "text/markdown")

    def test_returns_the_packaged_data_file_verbatim(self):
        result = i18n()

        on_disk = _packaged_data.packaged_data_path("general", "i18n")
        self.assertIsInstance(result, str)
        self.assertEqual(result, on_disk.read_text(encoding="utf-8"))
        self.assertTrue(result.startswith("# Multi-Language Artifact Variants (i18n)"))

    def test_reads_fresh_on_every_call_and_missing_file_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "general_i18n.md"
            path.write_text("first", encoding="utf-8")
            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=path):
                first = i18n()
                path.write_text("second", encoding="utf-8")
                second = i18n()
            self.assertEqual((first, second), ("first", "second"))
            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=Path(tmp) / "missing.md"):
                with self.assertRaises(FileNotFoundError):
                    i18n()

    def test_is_exposed_in_the_resources_package(self):
        import biz.dfch.specmgr.general.resources as general_resources

        self.assertIn("i18n", general_resources.__all__)


class TestI18nDescribesTheImplementedLayout(unittest.TestCase):
    """The layout, vocabulary, tool surface, and guard text match the implemented behavior."""

    def test_names_all_eleven_domains_in_scope_and_excludes_feat_and_adr(self):
        text = i18n()
        scope = _section(text, "## 1. Scope")

        for domain in LANGUAGE_AWARE_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(f"`{domain}`", scope)
        self.assertEqual(len(LANGUAGE_AWARE_DOMAINS), 11)
        self.assertIn("`feat`", scope)
        self.assertIn("`adr`", scope)
        self.assertIn("always English", scope)

    def test_layout_and_basename_rule(self):
        layout = _section(i18n(), "## 2. Directory layout and basename rule")

        self.assertIn("docs/{type}/<type>-<id>-<slug>.md", layout)
        self.assertIn("docs/{type}/{L}/<type>-<id>-<slug>.md", layout)
        self.assertIn("byte-identical to the EN source's file name", layout)
        self.assertIn("slug always derives from the EN title", layout)
        self.assertIn("same `id`", layout)
        self.assertIn("EN source (same `id`) exists", layout)

    def test_language_vocabulary_matches_the_guard_pattern(self):
        vocabulary = _section(i18n(), "## 3. Language vocabulary and heading tables")

        self.assertEqual(LANGUAGE_PATTERN.pattern, "^[a-z]{2}$")
        self.assertIn("`^[a-z]{2}$`", vocabulary)
        self.assertIn("general/data/headings/<language>.json", vocabulary)
        self.assertIn("<translated heading text>", vocabulary)
        self.assertIn("<canonical English heading text>", vocabulary)
        self.assertIn("a canonical English heading is always valid in a variant", vocabulary)
        flat = _flat(vocabulary)
        self.assertIn("specmgr://i18n/headings/{language}", flat)
        self.assertIn("specmgr://i18n/headings/de", flat)
        self.assertIn("no host file tool is needed", flat)
        self.assertIn("`en` has no table", flat)

    def test_tool_surface_names_every_language_honoring_tool(self):
        surface = _section(i18n(), "## 4. Tool surface")

        for fragment in (
            "get_<d>(id, language=L)",
            "get_<d>(id, raw=True, language=L)",
            "list_<d>(language=L)",
            "create_<d>(content, language=L, id=<shared EN id>)",
            "update(type, id, content, language=L)",
            "edit(type, id, old_str, new_str, language=L)",
            "`set_status`",
            "`set_classification`",
            "`delete`",
            "has **no** `language` parameter",
            "`list_languages(type, id)`",
            'check_translation_drift(type, id, language, source_language="en")',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, surface)

    def test_create_versus_update_and_guard_semantics(self):
        text = i18n()
        decision = _flat(_section(text, "## 7. Create versus update"))
        guard = _section(text, "## 8. Guard and error semantics")

        self.assertIn("**create**", decision)
        self.assertIn("**update**", decision)
        self.assertIn("ParseFailureResult", decision)
        self.assertIn("FileExistsError", decision)
        self.assertIn("`draft`; `open` for `rsk`", decision)
        for fragment in (
            "`ValueError`",
            "no heading-mapping table for language",
            "always English",
            "**non-raising** `ValidateResult`",
            "Nothing is written",
            "not-found",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guard)


class TestI18nNeverTranslateList(unittest.TestCase):
    """REQ-010: every closed-vocabulary token family is named, per domain, plus the `prb` exemption."""

    #: (domain, tokens that its schema-enforced column / row must name)
    _PER_DOMAIN: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "req",
            ("`MUST`", "`SHOULD`", "`MUST NOT`", "`SHOULD NOT`", "`MAY`", "RFC 2119", "`## Priority`", "`## Level`"),
        ),
        ("gol", ("`## Priority`",)),
        ("uc", ("`### Extension <N><letter>. <text>`", "`### Step <N>: <text>`", "`Subfunction`", "`User Goal`")),
        ("tsk", ("`[ ]` / `[x]`",)),
        ("qa", ("`**<d>.<NNNN>**: `", "`TODO: answer pending`")),
        ("prb", ("`problem_statement`", "exempt from translation", "byte for byte")),
        (
            "rsk",
            ("`transfer`", "`accept`", "`reduce`", "`avoid`", "`### Probability <1-5>`", "`### Impact <1-5>`"),
        ),
        ("dec", ("`### Option <N>: <name>`",)),
        ("sop", ("`### Step <N>: <name>`",)),
        (
            "vcr",
            (
                "`full`",
                "`partial`",
                "`none`",
                "`### AC-<NNN> (<Method>): <text>`",
                "`Demonstration`",
                "`Test`",
                "`Analysis`",
                "`Inspection`",
                "`Special`",
                "`REQ|UC <uuid>: <title>`",
            ),
        ),
        ("sysrs", ("type-tagged cross-reference bullets",)),
    )

    def _row(self, domain: str) -> str:
        table = _section(i18n(), "### 5.2 Closed vocabulary and schema constants, per domain")
        rows = [line for line in table.splitlines() if line.startswith(f"| `{domain}` |")]
        self.assertEqual(len(rows), 1, domain)
        return rows[0]

    def test_there_is_exactly_one_row_per_language_aware_domain(self):
        for domain in LANGUAGE_AWARE_DOMAINS:
            with self.subTest(domain=domain):
                self._row(domain)
        self.assertEqual({domain for domain, _ in self._PER_DOMAIN}, set(LANGUAGE_AWARE_DOMAINS))

    def test_every_domain_row_names_its_tokens(self):
        for domain, tokens in self._PER_DOMAIN:
            row = self._row(domain)
            for token in tokens:
                with self.subTest(domain=domain, token=token):
                    self.assertIn(token, row)

    def test_common_group_names_the_cross_cutting_tokens(self):
        common = _section(i18n(), "### 5.1 Common to every domain")

        for fragment in (
            "frontmatter",
            "`status`",
            "`classification`",
            "`<TAG> <uuid>: <title>`",
            "`GOL`",
            "`PRB`",
            "`QA`",
            "`UC`",
            "`REQ`",
            "`RSK`",
            "`DEC`",
            "`ADR`",
            "`VCR`",
            "`SYSRS`",
            "`SOP`",
            "Timestamps",
            "UUIDs",
            "code spans",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, common)

    def test_enforced_versus_convention_split_is_stated(self):
        text = _section(i18n(), "**Never translate (REQ-010).**")

        self.assertIn("enforced by the schema", text)
        self.assertIn("non-raising", text)
        self.assertIn("by convention", text)

    def test_heading_translation_rules(self):
        rules = _flat(_section(i18n(), "## 6. How to translate headings"))

        self.assertIn("whose value is that canonical", rules.replace("**", ""))
        self.assertIn("keep the canonical English heading", rules)
        for token in ("Option <N>: <name>", "Step <N>: <name>", "AC-<NNN> (<Method>): <text>", "Probability <N>"):
            with self.subTest(token=token):
                self.assertIn(token, rules)
        self.assertIn("**no** table entry", rules)
        self.assertIn("The H1 title is free-form", rules)


class TestI18nClaimsMatchTheSchemas(unittest.TestCase):
    """The tokens the resource lists as schema-enforced are really rejected when translated (sampled here; the full
    matrix runs through the write tools in the flow test)."""

    def test_data_carrying_headings_have_no_table_entry(self):
        from biz.dfch.specmgr.general.models.heading_table import load_heading_table

        table = load_heading_table("de")
        for canonical in ("Option 1: x", "Step 1: x", "AC-001 (Test): x", "Probability 3", "Impact 3"):
            with self.subTest(canonical=canonical):
                self.assertNotIn(canonical, table.values())
        self.assertTrue(
            all(not re.match(r"^(Option|Step|AC-|Probability|Impact|Extension) ?\d", v) for v in table.values())
        )

    def test_a_translated_closed_vocabulary_token_is_rejected_by_the_domain_parsers(self):
        from biz.dfch.specmgr.vcr.models.v1 import parse_vcr_body

        vcr_body = (
            "# T\n\n## Verifies\n\nREQ c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee: R\n\nWhy.\n\n## Coverage\n\npartial\n\n"
            "## Acceptance Criteria\n\n### AC-001 (Test): c\n\nd.\n"
        )
        parse_vcr_body(vcr_body)
        with self.assertRaises((AssertionError, ValueError)):
            parse_vcr_body(vcr_body.replace("(Test)", "(Prüfung)"))
        with self.assertRaises((AssertionError, ValueError)):
            parse_vcr_body(vcr_body.replace("\npartial\n", "\nteilweise\n"))


def _registered_template(uri_template: str):
    """Return the registered resource template for `uri_template`."""
    result = [t for t in mcp._resource_manager.list_templates() if t.uri_template == uri_template]
    assert len(result) == 1, f"expected exactly one template registration for {uri_template}, got {len(result)}"
    return result[0]


_DE_TABLE_PATH = Path(__file__).resolve().parents[3] / "src/biz/dfch/specmgr/general/data/headings/de.json"


class TestI18nHeadingsResourceTemplate(unittest.TestCase):
    """`specmgr://i18n/headings/{language}`: a read-only, guarded view of the loader's heading-mapping table."""

    def test_is_registered_as_a_json_template_next_to_the_adr_one(self):
        template = _registered_template("specmgr://i18n/headings/{language}")

        self.assertEqual(template.name, "i18n_headings")
        self.assertEqual(template.mime_type, "application/json")
        self.assertIn("language", template.parameters["properties"])
        self.assertTrue(
            {"specmgr://adr/{id}", "specmgr://i18n/headings/{language}"}
            <= {t.uri_template for t in mcp._resource_manager.list_templates()}
        )

    def test_is_exposed_through_the_resource_module(self):
        import biz.dfch.specmgr.general.resources.i18n as module

        self.assertTrue(callable(module.i18n_headings))

    def test_content_equals_the_packaged_de_table_as_json(self):
        result = i18n_headings("de")

        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), json.loads(_DE_TABLE_PATH.read_text(encoding="utf-8")))
        self.assertEqual(json.loads(result), load_heading_table("de"))
        self.assertEqual(json.loads(result)["Akzeptanzkriterien"], "Acceptance Criteria")
        self.assertIn("Zusammenfassung", result)  # UTF-8 kept unescaped

    def test_the_same_table_is_what_the_parsers_apply(self):
        """Reading a heading through the resource and writing it into a variant parses back to the canonical one."""
        from biz.dfch.specmgr.dec.models.v1 import parse_dec_body

        table = json.loads(i18n_headings("de"))
        reverse = {canonical: translated for translated, canonical in table.items()}
        body = (
            "# T\n\n## Context and Problem Statement\n\nx\n\n## Considered Options\n\ny\n\n"
            "## Decision Outcome\n\nz\n\n## Roles and Responsibilities\n\n### Accountable\n\na\n\n"
            "### Responsible\n\n- b\n\n## Source\n\ns\n"
        )
        translated = body
        for canonical in (
            "Context and Problem Statement",
            "Considered Options",
            "Decision Outcome",
            "Roles and Responsibilities",
            "Accountable",
            "Responsible",
            "Source",
        ):
            translated = translated.replace(f"## {canonical}\n", f"## {reverse[canonical]}\n").replace(
                f"### {canonical}\n", f"### {reverse[canonical]}\n"
            )
        self.assertNotEqual(translated, body)
        self.assertEqual(parse_dec_body(translated, language="de"), parse_dec_body(body))

    def test_path_injection_and_malformed_languages_are_rejected_before_any_filesystem_access(self):
        for bad in ("../../etc", "DE", "de/x", "d", "deu", "", "/abs", "..", "d3"):
            with self.subTest(language=bad):
                with mock.patch(
                    "biz.dfch.specmgr.general.resources.i18n.load_heading_table",
                    side_effect=AssertionError("the loader (filesystem) must not be reached"),
                ):
                    with self.assertRaises(ValueError) as ctx:
                        i18n_headings(bad)
                self.assertIn("two-letter", str(ctx.exception))

    def test_en_is_rejected_with_a_canonical_has_no_table_message(self):
        with mock.patch(
            "biz.dfch.specmgr.general.resources.i18n.load_heading_table",
            side_effect=AssertionError("the loader must not be reached for en"),
        ):
            with self.assertRaises(ValueError) as ctx:
                i18n_headings("en")

        self.assertIn("English is the canonical form", str(ctx.exception))
        self.assertIn("no heading-mapping table", str(ctx.exception))

    def test_a_language_without_a_table_is_the_loaders_actionable_error(self):
        reset_heading_table_cache()
        with self.assertRaises(ValueError) as ctx:
            i18n_headings("fr")

        self.assertIn("no heading-mapping table for language 'fr'", str(ctx.exception))
        self.assertIn("general/data/headings/fr.json", str(ctx.exception))

    def test_the_loaders_own_validation_applies(self):
        """An ambiguous table (two canonical headings -> one translation) surfaces the loader's error unchanged."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "xx.json"
            path.write_text(json.dumps({"A": "One", "B": "One"}), encoding="utf-8")
            reset_heading_table_cache()
            try:
                with mock.patch("biz.dfch.specmgr.general.models.heading_table.heading_table_path", return_value=path):
                    with self.assertRaises(ValueError) as ctx:
                        i18n_headings("xx")
            finally:
                reset_heading_table_cache()

        self.assertIn("ambiguous", str(ctx.exception))

    def test_translating_tool_still_absent(self):
        import asyncio

        tools = {tool.name for tool in asyncio.run(mcp.list_tools())}
        # `check_translation_drift` (feat-197-i18n Phase 140) is the one read-only tool whose name mentions
        # translation: it compares a variant with its source and never translates; no tool serves a heading table.
        self.assertEqual(
            {name for name in tools if "translat" in name.lower() or "heading" in name.lower()},
            {"check_translation_drift"},
        )


if __name__ == "__main__":
    unittest.main()
