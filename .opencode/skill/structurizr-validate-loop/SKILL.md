---
name: structurizr-validate-loop
description: Use when the task is checking or validating a Structurizr DSL model with the Structurizr MCP tools -- running the loop of the parse, validate, and inspect tools until validate answers OK and every inspect finding is triaged (fix, expected under the MCP limits, or reported in the final answer) -- for example when asked to "validate a Structurizr workspace", "check the DSL", "inspect findings", or to answer "is my model valid". It checks DSL text only and does not itself produce any files.
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
same rule as the repo's own PlantUML validation chain (DEC
7a626b12-b189-4561-a51d-ffb2e9e193b4): a structure-only check is not a
pass.

## How to call the tools

Your host may expose the MCP only through Code Mode: `execute` blocks
that call `tools.<server>.<tool>({ ... })` (discover the server name
first with `tools.opencode.list_mcp_resources()`; in the harness it is
`structurizr`). Four rules keep the loop verifiable:

1. **One MCP call per block, with the raw answer.** Never bundle
   `parse` + `validate` + `inspect` in one block (no `Promise.all`/
   `allSettled`), and never wrap even a single answer: the block
   `return`s the tool's own answer. For a clean `validate` that is
   exactly the two letters `OK`, so write
   `return await tools.structurizr.validate({ dsl: ... });` — not
   `return { validate: result }`. A bundled or wrapped answer hides
   the `OK` and the loop is not done.
2. **No filesystem in Code Mode.** The sandbox has no `fs`, no
   `require`, no `import('node:fs')` and no network: every call takes
   the workspace text inline.
3. **The final `validate` inlines the exact file text as a plain
   literal** — not a variable, not a shorthand:

   ```javascript
   return await tools.structurizr.validate({
     dsl: `workspace "Bookshop" "A simple online bookshop" {
         model { ... }
     }
   `
   });
   ```

   The backtick literal may span lines; it must contain no backslashes
   and no `${` (C4 models do not). Treat `workspace.dsl` as the single
   source of truth: after every edit, the next call inlines the
   file's new text. The `workspace.dsl` on disk must be
   byte-identical to the final literal — same characters, same
   trailing newline: write the file first, then inline exactly what
   the file holds (re-read it right before the final call when in
   doubt). The block answers the two letters `OK` for that exact text
   and only that text; if the file changes afterwards, the loop runs
   again. Never end the task with text that only existed inside a
   code block: the file on disk is the result.
4. **Fix the named error, not a guess.** Parse/validate messages name
   the line and the problem — change exactly that and re-run. Do not
   build experiment harnesses to isolate what the message already said.

## What the two tools answer

`validate` answers "will this parse into a workspace?" — it is
blocking, and its `OK` is the only green light this skill has.
`inspect` answers "does this follow C4 and Structurizr
recommendations?" — its findings are recommendations, never a failed
validate. See `references/validate-vs-inspect.md` for the side-by-side
table and the common findings with their triage.

## Triage and the final answer

Triage every finding of the last `inspect` with one of the three
labels, and end with an answer in this shape — quoting each finding's
exact text:

    Validation: `validate` answered OK on the exact text now in workspace.dsl.
    Findings (triaged):
    - fix: "<the finding's exact text>" — what you changed
    - expected: "<the finding's exact text>" — the MCP refuses `!docs`/`!adrs`
    - reported: "<the finding's exact text>"
    MCP limits: <any limit that shaped the result; name `!include`/`!docs` when relevant>

Only the missing-documentation and missing-decisions findings are
**expected** (the MCP refuses `!docs`/`!adrs` — do not add them).
Everything you fixed is **fix**; everything you left is **reported**.

## The MCP limits

The Structurizr MCP tools have hard limits; state them in the final
answer whenever they affect the result:

- **DSL text only, single file.** The tools work on the workspace's
  DSL text given as one input; there is no multi-file workspace.
- **`!include`, `!docs`, and `!adrs` are refused.** They answer, for
  example, `!include <file> is not permitted (feature
  structurizr.feature.dsl.filesystem is not enabled)` or `!docs is not
  permitted (feature ... documentation is not enabled)`. At most one
  attempt: if the multi-file workspace the task asks for gets that
  refusal, stop trying multi-file shapes and fall back to a single
  file — inline everything into `workspace.dsl` (no `!include`,
  `!docs`, or `!adrs` in the final text), run the loop on that file,
  and keep any `docs/` folder on disk for the CLI workflow; the final
  `workspace.dsl` simply does not reference it. Never use a `!theme`
  with a URL (offline validation cannot fetch it). In the final answer,
  name `!include` and `!docs` and say why the single file deviates.
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
on every relationship, flat identifiers, and explicit view keys.
