---
status: accepted
decision-makers: dfch
id: ddd038f0-ae16-4f4b-beef-df06f7ed226f
version: 1.0.0
---

# Prompt surface: narrated guidance plus step-gated test variants

## Context and Problem Statement

LLMs need guidance on which tools to call, in what order, to draft or revise an ADR. Guidance can be delivered through multiple channels: (1) plain prompt text returned by @mcp.prompt(), which the LLM reads and follows, or (2) real MCP elicitation (client-side support to show the LLM a form/questionnaire, not yet wired up in this project), or (3) tool-side Pydantic validation (which only catches malformed/blank values, not well-formed but fabricated content). A secondary question: should there be one prompt style, or multiple variants for A/B testing?

## Decision Drivers

Reliable sequencing of tool calls without requiring tool-side validation alone; ability to test different prompt styles (narrated vs. step-gated) side-by-side; support for future real MCP elicitation without breaking existing prompts.

## Considered Options

Prompt-text guidance alone vs. tool-side Pydantic validation vs. real MCP elicitation; single narrated prompt style vs. narrated + step-gated test variants for A/B comparison.

## Decision Outcome

Implement two primary `@mcp.prompt()`s: `create_adr(topic, decision_makers?, consulted?, informed?)` and `update_adr(id, instructions?)` return plain instructional text (not tool calls). This text guides the LLM through the tool sequence: for create_adr, first read `specmgr://adr/list` to check for duplicates, then call `create_adr(frontmatter, body)`, then `option_create` for each option, optionally `set_status`, always `validate_adr` last. Additionally, register step-gated test variants (`create_adr_test`, `update_adr_test`) with hard numbered `GATE 0..GATE N` blocks, explicit exit conditions, and standing "never fabricate a value" instructions. These variants exist purely for A/B comparison of prompt compliance and do not replace the narrated originals.

### Consequences

Clear, narrated guidance helps LLMs follow the intended sequence. Step-gated variants allow testing whether numbered gates + explicit exit conditions improve compliance vs. narration alone. Both variants share the same underlying tool surface; neither is preferred or deprecated. Future real MCP elicitation (when client support is added) can layer on top without breaking these prompts. Trade-off: two prompt styles require maintenance of two parallel texts; developers must ensure both stay in sync.

## More Information

Primary prompts: adr/prompts/create_adr.py, adr/prompts/update_adr.py. Test variants: adr/prompts/create_adr_test.py, adr/prompts/update_adr_test.py. All four are registered via adr/__init__.py.
