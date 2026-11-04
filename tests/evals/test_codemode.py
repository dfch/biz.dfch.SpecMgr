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

"""Code Mode detection-layer tests (Phase 110 locked harness fix).

Pure string-level tests over the locked extraction/attribution rules of
`c4_skills.codemode` -- no model call, no Docker. The committed
synthetic stream fixture `codemode-stream.ndjson` models the REAL Code
Mode shapes of the p110-prove run (the pinned opencode 2.2.5 image
exposes the Structurizr MCP only through `execute` blocks invoking
`tools.structurizr.<tool>({...})`): an inline-literal validate answering
exactly `OK`, a variable-`dsl` inspect with a findings-shaped output, a
multi-call `Promise.allSettled` block (no OK attribution), a shorthand
variable-`dsl` validate (no text attribution), an `error`-status block,
a block with no MCP reference, and one native parse call in the same
stream (the ordering coordinate).
"""

from __future__ import annotations

import unittest

from c4_skills.codemode import (
    analyze_execute_block,
    extract_inline_dsl,
    family_of_tool,
    find_references,
    mask_strings_and_comments,
)
from c4_skills.events import parse_events_file
from c4_skills.metrics import normalized_mcp_calls

from .conftest import FIXTURES_DIR

#: A small workspace DSL without backslashes or `${` sequences (the
#: plain-literal shapes the extractor must accept verbatim).
DSL = 'workspace "A" "a" {\n    model {\n        p = person "P" "A person"\n    }\n}\n'

#: The fixture stream's Bookshop DSL (the inline literal of event A and
#: the native parse input of event H) -- kept here so a fixture drift
#: fails this module's tests instead of passing silently.
FIXTURE_DSL = (
    'workspace "Bookshop" "A small online bookshop." {\n'
    "    model {\n"
    '        customer = person "Customer" "Buys books online."\n'
    '        bookshop = softwareSystem "Bookshop" "Sells books to customers." {\n'
    '            web = container "Web Store" "The customer-facing web shop." "Python"\n'
    "        }\n"
    '        customer -> web "Orders books through" "HTTPS"\n'
    "    }\n"
    "}"
)


def _refs(code: str):
    return find_references(code)


def _first_ref(code: str):
    refs = _refs(code)
    assert len(refs) == 1, f"expected exactly one reference, got {refs}"
    return refs[0]


class TestFamilyOfTool(unittest.TestCase):
    """Contract 3: family matching incl. the hyphenated export tools."""

    def test_exact_family_names(self) -> None:
        self.assertEqual(family_of_tool("parse"), "parse")
        self.assertEqual(family_of_tool("validate"), "validate")
        self.assertEqual(family_of_tool("inspect"), "inspect")
        self.assertEqual(family_of_tool("export"), "export")

    def test_hyphenated_export_tools_count_for_the_export_family(self) -> None:
        for tool in ("export-plantuml", "export-c4plantuml", "export-mermaid"):
            self.assertEqual(family_of_tool(tool), "export")

    def test_non_family_tools_are_none(self) -> None:
        for tool in ("list_mcp_resources", "search", "validate2", "parsed", "inspectX", "docs"):
            self.assertIsNone(family_of_tool(tool))


class TestMaskStringsAndComments(unittest.TestCase):
    def test_positions_are_preserved(self) -> None:
        code = 'const s = "tools.x.parse()";\nconst r = await tools.z.inspect({ dsl });\n'

        result = mask_strings_and_comments(code)

        self.assertEqual(len(result), len(code))
        self.assertIn("tools.z.inspect(", result)
        self.assertNotIn("tools.x.parse()", result)
        # the line structure and the untouched code are byte-identical
        self.assertEqual(result.splitlines()[1], code.splitlines()[1])

    def test_string_comment_and_line_comment_mentions_never_count(self) -> None:
        code = (
            'const a = "tools.s1.validate()";\n'
            "const b = 'tools.s2.parse()';\n"
            "// tools.s3.inspect()\n"
            "/* tools.s4.export-plantuml() */\n"
            "const c = await tools.s5.validate({ dsl });\n"
        )

        refs = _refs(code)

        self.assertEqual([ref.server for ref in refs], ["s5"])

    def test_template_literal_with_interpolation_is_masked_whole(self) -> None:
        code = 'const t = `a ${x + "b"} c tools.s1.validate({ dsl }) d`;\nconst r = 1;\n'

        refs = _refs(code)

        self.assertEqual(refs, [])

    def test_nested_backtick_in_interpolation_cannot_move_the_boundary(self) -> None:
        code = "const t = `a ${`inner tools.s1.parse()`} b`;\nconst r = await tools.s2.inspect({});\n"

        refs = _refs(code)

        self.assertEqual([ref.server for ref in refs], ["s2"])


class TestFindReferences(unittest.TestCase):
    def test_single_reference_carries_server_tool_family_and_call_open(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl });\n"

        refs = _refs(code)

        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].server, "structurizr")
        self.assertEqual(refs[0].tool, "validate")
        self.assertEqual(refs[0].family, "validate")
        # the call-site address is the opening parenthesis
        self.assertEqual(code[refs[0].call_open], "(")

    def test_dynamic_bracket_access_is_not_a_reference(self) -> None:
        # the real prove-run export loop shape: unattributable by design
        code = 'for (const tool of ["export-plantuml"]) {\n  await tools.structurizr[tool]({ dsl });\n}\n'

        self.assertEqual(_refs(code), [])

    def test_multiple_references_are_in_text_order(self) -> None:
        code = (
            "const [p, v] = await Promise.allSettled([\n"
            "  tools.structurizr.parse({ dsl }),\n"
            "  tools.structurizr.validate({ dsl }),\n"
            "]);\n"
        )

        refs = _refs(code)

        self.assertEqual([ref.tool for ref in refs], ["parse", "validate"])

    def test_non_family_tool_references_are_returned_too(self) -> None:
        # the OK-attribution rule needs the FULL reference count of a block
        code = "const r1 = await tools.opencode.list_mcp_resources();\nconst r2 = await tools.structurizr.parse({ dsl });\n"

        refs = _refs(code)

        self.assertEqual(len(refs), 2)
        self.assertIsNone(refs[0].family)
        self.assertEqual(refs[1].family, "parse")


class TestExtractInlineDsl(unittest.TestCase):
    """Contract 4: the plain-inline-literal dsl rule (each shape unit-tested)."""

    def test_backtick_template_literal_is_extracted_verbatim(self) -> None:
        code = f"const result = await tools.structurizr.validate({{ dsl: `{DSL}` }});\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertEqual(result, DSL)

    def test_quoted_string_with_escapes_is_unattributable(self) -> None:
        # a backslash inside a quoted string is escape ambiguity -> None
        code = 'const result = await tools.structurizr.validate({ dsl: "workspace \\"A\\" { }" });\n'

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_single_quoted_string_is_extracted(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: 'workspace A { }' });\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertEqual(result, "workspace A { }")

    def test_variable_reference_is_unattributable(self) -> None:
        code = "const dsl = `x`;\nconst result = await tools.structurizr.validate({ dsl: dsl });\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_shorthand_property_is_unattributable(self) -> None:
        # the dominant real prove-run shape: `const dsl = ...; validate({ dsl })`
        code = "const dsl = `x`;\nconst result = await tools.structurizr.validate({ dsl });\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_interpolated_template_literal_is_unattributable(self) -> None:
        code = 'const name = "A";\nconst result = await tools.structurizr.validate({ dsl: `workspace ${name} { }` });\n'

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_backslash_in_template_literal_is_unattributable(self) -> None:
        code = 'const result = await tools.structurizr.validate({ dsl: `workspace \\"A\\" { }` });\n'

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_file_read_value_is_unattributable(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: readFileSync('workspace.dsl') });\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_object_value_is_unattributable(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: { a: 1 } });\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_non_object_argument_is_unattributable(self) -> None:
        code = "const result = await tools.structurizr.validate(`x`);\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertIsNone(result)

    def test_properties_before_dsl_are_skipped(self) -> None:
        code = f"const result = await tools.structurizr.export-plantuml({{ viewKey: 'SC', opts: {{ a: 1 }}, dsl: `{DSL}` }});\n"

        ref = _first_ref(code)
        self.assertEqual(ref.family, "export")

        result = extract_inline_dsl(code, ref.call_open)

        self.assertEqual(result, DSL)

    def test_dsl_after_an_object_property(self) -> None:
        code = f"const result = await tools.structurizr.validate({{ opts: {{ a: 1 }}, dsl: `{DSL}` }});\n"

        result = extract_inline_dsl(code, _first_ref(code).call_open)

        self.assertEqual(result, DSL)


class TestAnalyzeExecuteBlock(unittest.TestCase):
    """Contract 4: the locked OK-attribution rule (each condition unit-tested)."""

    def test_single_completed_validate_answering_ok_is_attributed(self) -> None:
        code = f"const result = await tools.structurizr.validate({{ dsl: `{DSL}` }});\nreturn result;\n"

        entries = analyze_execute_block(code, "completed", "OK")

        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0].ok)
        self.assertEqual(entries[0].family, "validate")
        self.assertEqual(entries[0].dsl, DSL)

    def test_ok_output_is_compared_stripped(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: 'x' });\n"

        entries = analyze_execute_block(code, "completed", "  OK\n")

        self.assertTrue(entries[0].ok)

    def test_multi_call_block_never_attributes_ok(self) -> None:
        # even though the returned object carries "validate": "OK"
        code = (
            "const dsl = `x`;\n"
            "const [parse, validate] = await Promise.allSettled([\n"
            "  tools.structurizr.parse({ dsl }),\n"
            "  tools.structurizr.validate({ dsl }),\n"
            "]);\n"
            "return { validate: validate.status === 'fulfilled' ? validate.value : validate.reason };\n"
        )

        entries = analyze_execute_block(code, "completed", '{\n  "validate": "OK"\n}')

        self.assertEqual([entry.family for entry in entries], ["parse", "validate"])
        self.assertFalse(any(entry.ok for entry in entries))

    def test_second_non_family_reference_disqualifies_ok(self) -> None:
        code = "const r1 = await tools.opencode.list_mcp_resources();\nconst r2 = await tools.structurizr.validate({ dsl: 'x' });\n"

        entries = analyze_execute_block(code, "completed", "OK")

        self.assertEqual(len(entries), 1)
        self.assertFalse(entries[0].ok)

    def test_error_status_never_attributes_ok(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: 'x' });\n"

        entries = analyze_execute_block(code, "error", "OK")

        self.assertFalse(entries[0].ok)

    def test_wrapped_object_output_never_attributes_ok(self) -> None:
        code = "const result = await tools.structurizr.validate({ dsl: 'x' });\n"

        entries = analyze_execute_block(code, "completed", '{\n  "validation": "OK",\n  "dslLength": 842\n}')

        self.assertFalse(entries[0].ok)

    def test_non_family_only_block_emits_no_entries(self) -> None:
        code = "return tools.opencode.list_mcp_resources();\n"

        self.assertEqual(analyze_execute_block(code, "completed", "{}"), [])

    def test_export_reference_is_classified_for_the_export_family(self) -> None:
        code = "const result = await tools.structurizr.export-plantuml({ dsl: 'x', viewKey: 'SC' });\n"

        entries = analyze_execute_block(code, "completed", "@startuml\n@enduml")

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].family, "export")
        self.assertEqual(entries[0].tool, "export-plantuml")
        self.assertFalse(entries[0].ok)


class TestCodemodeStreamFixture(unittest.TestCase):
    """The committed synthetic fixture: the real prove-run shapes end to end."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_events_file(FIXTURES_DIR / "events" / "codemode-stream.ndjson")

    def test_fixture_parses_clean(self) -> None:
        self.assertEqual(dict(self.parsed.unknown_types), {})
        self.assertEqual(len(self.parsed.tool_calls), 8)
        self.assertTrue(self.parsed.finish_seen)

    def test_normalized_view_rows(self) -> None:
        view = normalized_mcp_calls(self.parsed)

        rows = [(entry.position, entry.source, entry.family, entry.status, entry.ok) for entry in view]
        self.assertEqual(
            rows,
            [
                (0, "codemode", "validate", "completed", True),
                (1, "codemode", "inspect", "completed", False),
                (2, "codemode", "parse", "completed", False),
                (2, "codemode", "validate", "completed", False),
                (3, "codemode", "parse", "error", False),
                (5, "codemode", "validate", "completed", True),
                (6, "codemode", "validate", "completed", True),
                (7, "native", "parse", "completed", False),
            ],
        )

    def test_dsl_attribution_per_entry(self) -> None:
        view = normalized_mcp_calls(self.parsed)

        self.assertEqual(view[0].dsl, FIXTURE_DSL)  # inline literal: attributed
        self.assertIsNone(view[1].dsl)  # variable: unattributable
        self.assertIsNone(view[3].dsl)  # multi-call block: variable
        self.assertIsNone(view[5].dsl)  # interpolated template: unattributable
        self.assertIsNone(view[6].dsl)  # shorthand variable: unattributable
        self.assertEqual(view[7].dsl, FIXTURE_DSL)  # native call: the reported input

    def test_native_and_codemode_share_the_call_order(self) -> None:
        view = normalized_mcp_calls(self.parsed)

        self.assertEqual([entry.position for entry in view], [0, 1, 2, 2, 3, 5, 6, 7])
        self.assertLess(
            view[7].position,
            len(self.parsed.tool_calls),
            "the native call's position addresses ParsedTrial.tool_calls",
        )


if __name__ == "__main__":
    unittest.main()
