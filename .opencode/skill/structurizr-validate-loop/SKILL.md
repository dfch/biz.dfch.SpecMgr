---
name: structurizr-validate-loop
description: Use when the task is checking a Structurizr DSL workspace with the Structurizr MCP tools -- running the loop of the parse, validate, and inspect tools until validate answers OK and every inspect finding is triaged (fix, expected under the MCP limits, or reported in the final answer) -- for example to "validate a Structurizr workspace", "check the DSL", "inspect findings", or answer "is my model valid", whether surfaced by an explicit request or organically while working with Structurizr DSL text that must be validated before it is returned.
---

# Structurizr Validate Loop

You are checking Structurizr DSL with the Structurizr MCP server. Your
host prefixes the MCP tool names (for example `structurizr_validate`;
the in-harness server name is `structurizr`), so refer to the tools by
their own names — the `parse`, `validate`, and `inspect` tools of the
Structurizr MCP server — and call whichever prefixed variant your host
exposes.

## The mandatory loop

Every DSL result runs through this loop before it is returned:

1. **Parse.** Run the `parse` tool on the DSL text. Fix every error it
   reports and parse again.
2. **Validate until OK.** Run the `validate` tool. If it reports
   errors, fix them and re-run. Keep going until `validate` answers
   `OK` — do not move on, and do not report the model as done, before
   it does.
3. **Inspect.** Run the `inspect` tool on the validated text.
4. **Triage EVERY finding** into exactly one of the three labels:
   - **fix** — correct the DSL. Any edit after the final validate
     requires re-validating, so the fixed text re-enters the loop at
     step 2.
   - **expected under the MCP limits** — the finding is caused by a
     limit of the MCP (below), not by the model. Do not chase it.
   - **reported in the final answer** — a genuine recommendation that
     is not fixed now; state it in the final answer.

   A finding that cannot be cleared under the MCP never blocks the
   result.
5. **Return the exact text that last got `OK` from `validate`.** Never
   return text that was never validated to `OK`, and never return text
   that changed after the final validate: if anything is edited after
   the final validate, re-run `validate` (and `inspect` on the new
   text) before returning.

A DSL result that was only parsed, and not validated to `OK`, is NOT a
pass — a parsed-only or reported-only result is not a pass. This is the
same rule as the repo's own PlantUML validation chain (ADR
7a626b12-b189-4561-a51d-ffb2e9e133b4): a structure-only check is not a
pass.

## What the two tools answer

`validate` answers "will this parse into a workspace?" — it is
blocking, and its `OK` is the only green light this skill has.
`inspect` answers "does this follow C4 and Structurizr
recommendations?" — its findings are recommendations, never a failed
validate. See `references/validate-vs-inspect.md` for the side-by-side
table and the common findings with their triage.

## The MCP limits

The Structurizr MCP tools have hard limits; state them in the final
answer whenever they affect the result:

- **DSL text only, single file.** The tools work on the workspace's
  DSL text given as one input; there is no multi-file workspace.
- **`!include`, `!docs`, and `!adrs` are refused.** A DSL that uses any
  of them gets a refusal that reads like "feature … is not enabled" —
  the MCP sandbox does not enable those importers. Do not use them,
  and never "fix" a missing-documentation or missing-decisions finding
  by adding `!docs`/`!adrs`: triage that finding as expected under the
  MCP limits and report it as expected in the final answer.
- **No image rendering.** The MCP cannot produce image files (PNG/SVG).
  Its export tools emit diagram source only — PlantUML, C4-PlantUML,
  or Mermaid text. If images are requested, say so.

## When the MCP is absent

If the Structurizr MCP tools are not available in the host, validation
is not possible. State that in the final answer and never describe a
DSL result as validated — a result the tools could not check is
unvalidated, no matter how well it looks.

## Gotchas that surface in the loop

`references/dsl-gotchas.md` collects the DSL rules whose violations the
loop most often meets: declaration order (elements before the
relationships that use them), quoting, a description and a technology
on every relationship, and flat, model-wide-unique identifiers.
