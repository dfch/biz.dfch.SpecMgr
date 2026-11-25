# Source map

Every adapted passage of this skill, mapped to its source file at the
pinned commit. A passage marked "ideas only" copies no text and therefore
carries no attribution line — the notice and this map stay consistent:
adapted text exists in exactly the two files `NOTICE.md` lists.

Sources:

- `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`
  (MIT, "Copyright (c) 2026 Georges Martin"); source path
  `skills/c4-model/SKILL.md` (single-file skill).

"Observed" passages quote the pinned Structurizr DSL/CLI/MCP's own
behavior — facts from this repo's harness (the pinned DSL has no
`externalSystem` keyword, verified in Phase 120 and re-verified against
the pinned documentation clone), not text of the source, and are marked
ideas only.

## `SKILL.md` — ideas only

| Passage | Source | Notes |
|---|---|---|
| The six decisions | upstream "C4 Abstractions", "Notation Rules", "Common Modeling Decisions", "Common Mistakes" #2/#3/#4/#5 | Ideas only: one line per decision in this repo's wording; the shared/embedded-library trap sentence (decision 2), the technology-on-every-relationship rule (decision 5) and the validate-until-OK wording ("Checking the result") are this repo's, measured against the Phase 130 iteration-1 data. |
| The pinned-DSL external-system fact ("In this DSL version there is no `externalSystem` keyword") | — | Ideas only / observed: the pinned DSL fact, restated. |
| "Checking the result" section | — | Ideas only: the light validate pointer is this repo's (REQ-006/REQ-011); the routing to the `structurizr-validate-loop` skill is this repo's split (REQ-001 vs REQ-003). The upstream Docker-CLI "Validation" section is dropped wholesale. |
| "The MCP limits" section | — | Ideas only: REQ-006, the observed MCP refusal facts. |
| "When the MCP is absent" section | — | Ideas only: REQ-011. |

No passage in `SKILL.md` copies text; it has no attribution line in
`NOTICE.md`.

## `references/levels-and-notation.md`

| Passage | Source | Adaptation |
|---|---|---|
| "C4 Abstractions" intro + "Level 1: Software System" | upstream "C4 Abstractions → Level 1" | near-verbatim; the system-context line is added (ideas only, the one line the abstraction level needs) |
| "Level 2: Container" | upstream "C4 Abstractions → Level 2" | near-verbatim (no change) |
| "Level 3: Component" | upstream "C4 Abstractions → Level 3" | near-verbatim; the "Elixir" mention in the language-dependent bullet dropped (locked removal) |
| "Level 4: Code" | upstream "C4 Abstractions → Level 4" | near-verbatim (no change) |
| "Notation Rules → Required Elements" | upstream "Notation Rules → Required Elements" | near-verbatim (no change) |
| "Notation Rules → Technology Labels" | upstream "Notation Rules → Technology Labels" | adapted: the component example "Elixir GenServer" replaced by a generic one; the inter-container-only technology rule widened to every relationship (ideas-only extension, Phase 130 iteration-1 data) |
| "Notation Rules → Relationship Lines" | upstream "Notation Rules → Relationship Lines" | near-verbatim; the bad-label list extended with "Talks to"/"Communicates with" (the locked gate set's additions) |
| "Notation Rules → Visual Consistency" | upstream "Notation Rules → Visual Consistency" | near-verbatim (no change) |
| "Workflow: Adding Elements to a Model" Steps 1–3 | upstream "Workflow" Steps 1–3 | near-verbatim; Step 3's technology item widened to every relationship (ideas-only extension) |

## `references/modeling-decisions.md`

| Passage | Source | Adaptation |
|---|---|---|
| "When to Split a Container" | upstream "Common Modeling Decisions → When to Split a Container" | near-verbatim (no change) |
| "When to Add Components" | upstream "Common Modeling Decisions → When to Add Components" | near-verbatim (no change) |
| "When to Model External Systems" criteria | upstream "Common Modeling Decisions → When to Model External Systems" | near-verbatim (no change) |
| The pinned-DSL external-system passage (no `externalSystem` keyword; top-level `softwareSystem`/`element` with the `External` tag; the example declaration; the `externalSystems` export section never populated) | — | Ideas only / observed: the pinned DSL fact with the `External` tag from upstream's Step 2 example tags ("Database", "Web", "External") |
| "Common Mistakes" #1–9 | upstream "Common Mistakes" | near-verbatim; #10–13 (Elixir/OTP-specific) dropped; #2 extended with the shared/embedded-library trap (ideas-only, Phase 130 iteration-1 data) |
| "Diagram Staleness" table | upstream "Diagram Staleness" | near-verbatim (no change) |

## Dropped upstream content (no local passage)

- The entire "Erlang/Elixir/OTP Modeling Guide" section and every
  Elixir/Phoenix/Ash/Oban pattern and relationship-label table, incl.
  the Elixir/OTP-specific common mistakes #10–13 and the "Elixir"
  mentions inside the C4 Abstractions and Notation Rules.
- The "Diagram Types" and "Diagram Selection Guide" sections — the
  locked scope cut: REQ-001 scopes this skill to the C4 levels, what
  counts as a container, naming/description/label rules and the common
  mistakes; "which views to create" is the `c4-view-design` skill's
  single task (REQ-004, REQ-007 single-task separation).
- The Docker-CLI "Validation" section (`$RUNTIME`/podman/container,
  the `structurizr/structurizr:2026.09.19` commands, the project-root
  mount advice) — replaced by the light MCP-validate pointer in
  `SKILL.md` (the full loop stays the `structurizr-validate-loop`
  skill's single task).
- The `!adrs`/`!docs` symlink note (mount the project root so the
  symlinks resolve) — the MCP refuses `!docs`/`!adrs`/`!include`.
- The "Related Skills" section (points at the upstream's own
  `structurizr-dsl`/`c4-review`/`c4-deployment` skills).
- The upstream frontmatter's `metadata`/`license` fields (this skill's
  frontmatter is exactly `name` + `description`).
