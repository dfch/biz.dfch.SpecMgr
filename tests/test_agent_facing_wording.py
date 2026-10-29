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

"""feat-189 post-implementation review findings G1-G3: central wording pins
for the round-trip-reduction agent-facing surface
(``.specmgr/feat/feat-189-reduce-agent-round-trips/README.md``).

Before this module, the G1-G3 wording was pinned only by the frozen Phase-130
probe file (``evidence/worktree-surface-probe.txt`` and the Phase-100/110
data-file history), not by any test:

- G1: the 12 update instruction files' context-sensitive schema step
  (``<d>/data/<d>_update_instructions.md``) -- nothing asserted the new step
  wording or that the step names the ``get_<d>_schema`` tool;
- G2: the 38 structure-reference description clauses (the 12 ``create_<d>``
  tool descriptions + the generic ``update``/``validate`` tool descriptions +
  the 24 create/update prompt descriptions) plus the ``create_adr``
  deliberate-absence sentence -- nothing asserted the clauses against the
  live tool/prompt metadata;
- G3: the closed-set/comment content folded into the 6 template/example files
  in Phases 100/110 (prb lead-sentence frame, tsk task-text fidelity
  directive, req RFC 2119 set, rsk TARA set + ``specmgr://rsk/`` pointers, qa
  question-prefix rule, vcr coverage set) -- nothing asserted the comment
  content through the domains' own parsers.

Policy: every pin is the LONGEST STABLE PHRASE of its clause, never the
entire description or file -- the pins must survive harmless additions but
fail on a rewording or deletion of the clause itself. All phrases were
verified against the live ``mcp`` metadata and the packaged files on disk
before writing (zero mismatches; see the feature README's 2026-10-19
review-closure entry). Tests/ root placement follows the precedent of
``tests/test_schema_surface_registration.py`` (the other central feat-189
modules).
"""

from __future__ import annotations

import asyncio
import re
import unittest

from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.prb.models.v1 import parse_prb
from biz.dfch.specmgr.req.models.v1 import parse_req
from biz.dfch.specmgr.rsk.models.v1 import parse_rsk
from biz.dfch.specmgr.server import mcp
from biz.dfch.specmgr.tsk.models.v1 import parse_tsk
from biz.dfch.specmgr.vcr.models.v1 import parse_vcr

# ---------------------------------------------------------------------------
# G1 -- the 13 update instruction files' context-sensitive schema step
# ---------------------------------------------------------------------------

#: The context-sensitive schema step's heading -- identical in all 13 files.
_UPDATE_SCHEMA_STEP_HEADING = "Check the schema only for structural changes, and validate before writing if useful"

#: The step's first sentence core, per domain: it names the
#: ``get_<d>_schema`` tool AND carries the structural-change condition.
_UPDATE_SCHEMA_TOOL_CONDITION = (
    "Call the `get_{d}_schema` tool (the generated JSON Schema) only for a whole-body rewrite or a structural change"
)

#: The local-splice skip semantics' common core, per domain. Two wording
#: variants exist across the 13 files: vcr and txt read "Skip the schema
#: fetch for a local splice (a line-range replace ...)" instead of the
#: other 11 files' "Skip the fetch for a local splice (a line-range
#: replace) ...", and txt's splice parenthetical additionally names the
#: ``edit`` tool ("(a line-range replace or an `edit`)") -- the pinned
#: cores below are the shared part (feat-229-txt Phase 130).
_UPDATE_LOCAL_SPLICE_SKIP = "local splice (a line-range replace"
_UPDATE_RAW_BODY_IN_CONTEXT = "where the raw body is already in context"

#: Why the skip is safe -- the generic write tool(s) still validate the
#: spliced/edited result as a whole document before writing. 12 files read
#: "`update` still validates the spliced result as a whole document ...";
#: txt reads "`update` and `edit` both validate the result as a whole
#: document ..." (feat-229-txt Phase 130) -- the pinned core is the shared
#: part.
_UPDATE_SKIP_IS_SAFE = "whole document before writing anything, so the skip is safe"


def _normalized_update_instructions(domain: str) -> str:
    """The packaged ``<d>_update_instructions.md`` text, whitespace-normalized.

    The 13 files soft-wrap at different columns per domain, so every phrase
    pin is matched against single-spaced text.
    """
    result = re.sub(r"\s+", " ", read_packaged_text(domain, "update_instructions"))
    return result


# ---------------------------------------------------------------------------
# G2 -- the tool/prompt description clauses (live ``mcp`` metadata)
# ---------------------------------------------------------------------------

#: The per-domain structure-reference clause -- the 13 ``create_<d>`` tool
#: descriptions and the 26 create/update prompt descriptions all carry it,
#: with the domain prefix swapped.
_CREATE_STRUCTURE_REFERENCE = (
    "The structure reference is the `get_{d}_schema` tool (the generated JSON Schema); the "
    "`get_{d}_template`/`get_{d}_example` tools return the authoring template and a complete sample."
)

#: The generic structure-reference clause -- the ``update`` and ``validate``
#: tool descriptions (one clause covering all 13 domains).
_GENERIC_STRUCTURE_REFERENCE = (
    "Each domain's structure reference is its own `get_<d>_schema` tool (the generated JSON Schema), "
    "with `get_<d>_template`/`get_<d>_example` as the authoring starting points."
)

#: The ``create_adr`` deliberate-absence sentence (REQ-005): no
#: ``specmgr://adr/schema`` resource exists by design.
_CREATE_ADR_EXCLUSION = (
    "There is deliberately no `specmgr://adr/schema` resource -- this tool's own typed input "
    "parameters (`frontmatter`: `AdrFrontmatter`, `body`: `AdrBody`) are the authoritative ADR "
    "structure reference."
)

#: The per-domain prompt name deviations -- rsk and tsk do not follow the
#: ``create_<d>``/``update_<d>`` convention (the prompt files are
#: ``create_risk``/``update_risk`` and ``create_task``/``update_task``).
_PROMPT_NAME_DEVIATIONS: dict[str, tuple[str, str]] = {
    "tsk": ("create_task", "update_task"),
    "rsk": ("create_risk", "update_risk"),
}


def _prompt_names(domain: str) -> tuple[str, str]:
    """The domain's (create prompt name, update prompt name)."""
    result = _PROMPT_NAME_DEVIATIONS.get(domain, (f"create_{domain}", f"update_{domain}"))
    return result


# ---------------------------------------------------------------------------
# G3 -- the closed-set/comment content in the 6 template/example files
# ---------------------------------------------------------------------------

#: The exact bracketed lead-sentence frame -- prb template AND example
#: (REQ-001's T1 structural precondition).
_PRB_LEAD_SENTENCE_FRAME = "[Current state] is causing [specific issue], for [stakeholder] because [underlying cause]."


class TestUpdateInstructionSchemaStep(unittest.TestCase):
    """G1: the 13 update instruction files' context-sensitive schema step."""

    def test_step_heading(self) -> None:
        """Every update instruction file carries the context-sensitive step heading."""
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(_UPDATE_SCHEMA_STEP_HEADING, _normalized_update_instructions(domain))

    def test_step_names_get_d_schema_tool_for_structural_changes_only(self) -> None:
        """The step names the ``get_<d>_schema`` tool AND scopes it to whole-body
        rewrites or structural changes."""
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(
                    _UPDATE_SCHEMA_TOOL_CONDITION.format(d=domain),
                    _normalized_update_instructions(domain),
                )

    def test_step_carries_local_splice_skip_semantics(self) -> None:
        """The step skips the schema fetch for a local splice (the raw body is
        already in context) and states why the skip is safe (the generic
        write tool(s) still validate the result as a whole document)."""
        for domain in WHOLE_BODY_DOMAINS:
            text = _normalized_update_instructions(domain)
            with self.subTest(domain=domain):
                self.assertIn(_UPDATE_LOCAL_SPLICE_SKIP, text)
                self.assertIn(_UPDATE_RAW_BODY_IN_CONTEXT, text)
                self.assertIn(_UPDATE_SKIP_IS_SAFE, text)


class TestStructureReferenceDescriptionClauses(unittest.TestCase):
    """G2: the 41 structure-reference clauses + the ``create_adr`` exclusion,
    pinned against the live ``mcp`` tool/prompt metadata."""

    @classmethod
    def setUpClass(cls) -> None:
        tools = asyncio.run(mcp.list_tools())
        prompts = asyncio.run(mcp.list_prompts())
        cls._tools = {tool.name: tool for tool in tools}
        cls._prompts = {prompt.name: prompt for prompt in prompts}

    def test_create_tool_descriptions_carry_per_domain_clause(self) -> None:
        """Each of the 13 ``create_<d>`` tool descriptions carries the per-domain
        structure-reference clause."""
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(_CREATE_STRUCTURE_REFERENCE.format(d=domain), self._tools[f"create_{domain}"].description)

    def test_update_and_validate_descriptions_carry_generic_clause(self) -> None:
        """The generic ``update`` and ``validate`` tool descriptions carry the
        one generic clause covering all 12 domains."""
        for name in ("update", "validate"):
            with self.subTest(name=name):
                self.assertIn(_GENERIC_STRUCTURE_REFERENCE, self._tools[name].description)

    def test_prompt_descriptions_carry_per_domain_clause(self) -> None:
        """Each of the 26 create/update prompt descriptions carries the
        per-domain structure-reference clause (rsk: ``create_risk``/
        ``update_risk``, tsk: ``create_task``/``update_task``)."""
        for domain in WHOLE_BODY_DOMAINS:
            create_name, update_name = _prompt_names(domain)
            for prompt_name in (create_name, update_name):
                with self.subTest(domain=domain, prompt=prompt_name):
                    self.assertIn(_CREATE_STRUCTURE_REFERENCE.format(d=domain), self._prompts[prompt_name].description)

    def test_create_adr_description_documents_schema_exclusion(self) -> None:
        """The ``create_adr`` tool description carries the deliberate-absence
        sentence (REQ-005: no ``specmgr://adr/schema`` resource by design)."""
        self.assertIn(_CREATE_ADR_EXCLUSION, self._tools["create_adr"].description)


class TestTemplateExampleCommentContent(unittest.TestCase):
    """G3: the closed-set/comment content folded into the 6 template/example
    files in Phases 100/110, parsed through the domains' own parsers where the
    content lives in a parsed structure."""

    def test_prb_template_and_example_carry_lead_sentence_frame(self) -> None:
        """The prb template AND example both carry the exact bracketed
        lead-sentence frame in their own leading comment (``doc.body.comment``)."""
        for kind in ("template", "example"):
            doc = parse_prb(read_packaged_text("prb", kind))
            with self.subTest(kind=kind):
                self.assertIsNotNone(doc.body.comment)
                self.assertIn(_PRB_LEAD_SENTENCE_FRAME, doc.body.comment.text)

    def test_tsk_template_fidelity_directive_without_prefix_inducement(self) -> None:
        """The tsk template directs keeping each task's text exactly as given
        (flat checklist, no prefixes), and the old "Number the tasks"/
        "Task 1:" inducement is gone from the packaged text."""
        raw = read_packaged_text("tsk", "template")
        doc = parse_tsk(raw)
        self.assertIsNotNone(doc.body.comment)
        self.assertIn("Keep each task's text exactly as given by the user", doc.body.comment.text)
        self.assertIn("a flat checklist, one item per line", doc.body.comment.text)
        self.assertNotIn("Number the tasks", raw)
        self.assertNotIn("Task 1:", raw)

    def test_req_template_names_full_rfc2119_set(self) -> None:
        """The req template's ``## Level`` comment names the full RFC 2119 set
        (the five words ``req``'s ``_LEVEL_PATTERN`` enforces)."""
        doc = parse_req(read_packaged_text("req", "template"))
        self.assertIn(
            "RFC 2119 Requirement Keyword: one of MUST, SHOULD, MUST NOT, SHOULD NOT, MAY", doc.body.level.comment.text
        )

    def test_rsk_template_names_tara_set_and_matrix_pointers(self) -> None:
        """The rsk template's leading comment names the TARA 4-word set and
        both ``specmgr://rsk/`` resource pointers (the ``## Strategy`` section
        rejects a leading comment, so both facts live in the document-level
        comment)."""
        doc = parse_rsk(read_packaged_text("rsk", "template"))
        self.assertIsNotNone(doc.body.comment)
        comment = doc.body.comment.text
        self.assertIn("the four TARA words (transfer, accept, reduce, avoid", comment)
        self.assertIn("specmgr://rsk/tara", comment)
        self.assertIn("5x5 risk-matrix coordinates 1-5", comment)
        self.assertIn("specmgr://rsk/risk-matrix", comment)

    def test_qa_template_spells_question_prefix_rule(self) -> None:
        """The qa template's ``## Functional Suitability`` comment spells the
        question-prefix rule (single category digit, 4-digit zero-padded
        per-category sequence)."""
        raw = read_packaged_text("qa", "template")
        self.assertIn("a single category digit", raw)
        self.assertIn("4-digit zero-padded per-category sequence", raw)

    def test_vcr_template_names_coverage_set(self) -> None:
        """The vcr template's leading comment names the ``## Coverage`` closed
        set (``full``/``partial``/``none``)."""
        doc = parse_vcr(read_packaged_text("vcr", "template"))
        self.assertIsNotNone(doc.body.comment)
        self.assertIn("`## Coverage` is one of full, partial, none", doc.body.comment.text)


if __name__ == "__main__":
    unittest.main()
