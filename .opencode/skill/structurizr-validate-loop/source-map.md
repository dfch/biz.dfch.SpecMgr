# Source map

Every adapted passage of this skill, mapped to its source file at the
pinned commit. A passage marked "ideas only" copies no text and
therefore carries no attribution line — the notice and this map stay
consistent: adapted text exists in exactly the two files `NOTICE.md`
lists.

Source: `passionsplay/structurizr-skill` @
`5e45154e1c266e0517d456855b415ba770412f16` (MIT, "Copyright (c) 2026
Benjamin Turner"). Source paths are relative to that repository's root
at the pinned commit.

## `SKILL.md` — ideas only

| Passage | Source | Notes |
|---|---|---|
| The loop ordering (parse/fix, validate until done, inspect, summarize findings without treating them as failures) | `skills/structurizr/SKILL.md`, "Workflow: create or change a model" and "Gotchas" | Ideas only. The upstream steps run Docker via `scripts/structurizr.sh` and are dropped; the MCP tool names, the `OK` contract, the triage labels, the exact-text rule, and the MCP limits are this repo's (spike findings 2, 3, and 8 of TXT `4a09922d-bc32-4c03-86ba-d30ebc34e0b8` plus REQ-003/REQ-006/REQ-011). |
| The MCP facts (stateless tools over DSL text) | `skills/structurizr/references/mcp.md`, opening paragraph; spike Finding 3 | Ideas only. The upstream file's "Run the server" and "Connect an agent" content is dropped (Docker/Claude-specific). |
| "How to call the tools" section (added in iteration 2) | — | Ideas only: the Code Mode call shapes (one call per block, no filesystem in the sandbox, the final `validate` as a plain inline literal, fix-the-named-error) are this repo's harness findings, not upstream passages. |
| "Triage and the final answer" section (added in iteration 2) | — | Ideas only: the final-answer template and the quote-every-finding rule implement REQ-003's triage; the upstream skill has no final-answer template. |
| The `!include`/`!docs` fallback protocol in "The MCP limits" (extended in iteration 2) | — | Ideas only: the refusal strings are the pinned MCP's own output observed in this harness; the single-file fallback and the no-`!theme`-URL warning are this repo's. |

No passage in `SKILL.md` copies text; it has no attribution line in
`NOTICE.md`.

## `references/validate-vs-inspect.md`

All rows of this file adapt `skills/structurizr/references/
validate-vs-inspect.md` unless noted.

| Passage | Source | Adaptation |
|---|---|---|
| Opening "Two tools, two questions…" | opening lines | "commands" → "tools"; otherwise near-verbatim |
| Table row "Question" | table | verbatim |
| Table row "Output on success" | table | the `validate` cell re-stated for the MCP answer `OK` (upstream: "Nothing (exit 0)"); the `inspect` cell verbatim |
| Table row "Output on problems" | table | near-verbatim (both error-shape strings kept) |
| Table row "Blocking?" | table + `skills/structurizr/SKILL.md`, "Gotchas" ("Validate and inspect are different tools") | merged; the upstream exit-code phrasing replaced with "Never treat a finding list like a failed validate" (the MCP has no exit codes) |
| Dropped: table row "Exit code" | table | CLI-only semantics, no MCP counterpart |
| "Common validate errors" table (3 rows) | "## Common validate errors" | near-verbatim (the messages are fixed tool output) |
| "Common inspect findings" rows `workspace.scope`, `model.relationship.technology`, `model.relationship.description`, `views.view.key` / `views.view.layout`, `model.*.description` | "## Common inspect findings" | meaning cells near-verbatim; fix cells kept under a "Triage" header carrying the `fix` label |
| Same table, rows `model.softwaresystem.documentation` and `model.softwaresystem.decisions` | "## Common inspect findings" | **inverted** per the locked adaptation rule: upstream "Add `!docs <folder>` … or ignore" / "Add `!adrs <folder>` … or ignore" becomes "expected under the MCP limits — the MCP refuses `!docs`/`!adrs`; do not add it; report the finding as expected in the final answer" |
| Closing "Report inspect findings grouped by rule id…" | final line | near-verbatim |

## `references/dsl-gotchas.md`

| Passage | Source | Adaptation |
|---|---|---|
| Intro second sentence ("Each rule exists because…") | `skills/structurizr/references/dsl-best-practices.md`, second line | near-verbatim |
| "Declaration order" section | `dsl-best-practices.md` "## Declaration order" + `skills/structurizr/SKILL.md` ("Define elements before relationships that use them") + `validate-vs-inspect.md` (the `The destination element "x" does not exist` error row) | merged; the forward-reference error string names the failure mode |
| "Quoting" section | `validate-vs-inspect.md` ("Unexpected tokens / parse errors" row) + `dsl-best-practices.md` "## Descriptions and technology" (what carries the quoted strings) | rewritten from the two passages |
| "Relationship description and technology" section | `dsl-best-practices.md` "## Descriptions and technology" + `skills/structurizr/SKILL.md` ("Give every relationship a description and a technology") + the inspect finding rows naming the two rule ids | merged; the bullets near-verbatim |
| "Flat identifiers" section | `dsl-best-practices.md` "## Identifiers: flat by default" + `skills/structurizr/SKILL.md` ("Prefer flat identifiers") | merged, near-verbatim |
| "Explicit view keys" section (added in iteration 2) | — | ideas only: the `[a-zA-Z0-9_-]` key constraint and error string are this harness's observed CLI/parse output, not an upstream passage; no attribution line |

## Dropped upstream content (no local passage)

- All Docker-CLI validation advice and every `scripts/structurizr.sh`
  reference: the upstream `skills/structurizr/SKILL.md` command block,
  workflow steps 1–6, and the path/`local`/`.structurizr/`/playwright
  gotchas, the `theme default` / static.structurizr.com note, and the
  Structurizr-Lite note.
- All Claude-specific setup: `skills/structurizr/references/mcp.md`,
  "Run the server" and "Connect an agent".
- The upstream frontmatter's `license`/`compatibility`/`metadata`
  fields (this skill's frontmatter is exactly `name` + `description`).
- The `dsl-best-practices.md` sections outside the locked gotcha set:
  "Relationships at two levels", "Granularity", "Views", "Styling",
  "Groups" (authoring territory, not the validate/inspect loop).
