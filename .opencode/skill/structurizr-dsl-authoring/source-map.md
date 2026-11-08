# Source map

Every adapted passage of this skill, mapped to its source file at the
pinned commit. A passage marked "ideas only" copies no text and
therefore carries no attribution line — the notice and this map stay
consistent: adapted text exists in exactly the three files `NOTICE.md`
lists.

Sources:

- `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`
  (MIT, "Copyright (c) 2026 Georges Martin"); source path
  `skills/structurizr-dsl/SKILL.md` (single-file skill).
- `structurizr/structurizr.github.io` @
  `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (MIT); source paths under
  `docs/dsl/`.

"Observed" passages quote the pinned Structurizr CLI
(`structurizr/structurizr:2026.10.26-noble`) or MCP's own output —
facts from this repo's harness, not text of either source, and marked
ideas only.

## `SKILL.md` — ideas only

| Passage | Source | Notes |
|---|---|---|
| The seven authoring rules | upstream `Syntax Fundamentals`, `Relationships`, `Uniqueness`, `Identifiers` + docs `03-basics.md`, `05-identifiers.md`, `07-implied-relationships.md` | Ideas only: one line per rule in this repo's wording; the error strings (`Too many tokens`, `The identifier "x" is already in use`, `The destination element "x" does not exist`) are observed pinned-CLI output, not upstream text (the upstream Troubleshooting table phrases them differently). |
| "Where the syntax lives" section | — | Ideas only: this repo's file layout. |
| "Checking the result" section | — | Ideas only: the light validate pointer is this repo's (REQ-006/REQ-011); the routing to the `structurizr-validate-loop` skill is this repo's split (REQ-002 vs REQ-003). The upstream Docker-CLI "Validation" section is dropped wholesale. |
| "The MCP limits" section | upstream `!include`/`!docs`/`!adrs` Directives + docs `81-parser.md` (feature matrix) | Ideas only: the refusal strings are the pinned MCP's own observed output; the single-file rule, the no-image-rendering rule and the no-`!theme`-URL rule are this repo's (REQ-006). |
| "When the MCP is absent" section | — | Ideas only: REQ-011. |

No passage in `SKILL.md` copies text; it has no attribution line in
`NOTICE.md`.

## `references/syntax.md`

| Passage | Source | Adaptation |
|---|---|---|
| "Syntax fundamentals" bullets | upstream "Syntax Fundamentals" | near-verbatim (the six shared bullets); the `""` placeholder, comma-separated tags and the "braces only with child content" bullets are added from docs `03-basics.md` (facts, restated) |
| "Constants and Variables" | upstream "Constants and Variables" + docs `03-basics.md` ("String constants and variables", "String substitution") | code block near-verbatim; the name-character and substitution facts restated from the docs |
| "Workspace structure" | upstream "Workspace Structure" | near-verbatim (no change) |
| "Model elements" intro (anonymous elements) | docs `05-identifiers.md` (opening) | restated (ideas only) |
| Person / Software System / Container / Component blocks | upstream "Model Elements" | near-verbatim; the `!docs <path>` / `!adrs <path>` lines inside the softwareSystem and container blocks are dropped (MCP refuses them) |
| "Custom element" block | docs `71-language.md` (`## element`) + `dsl/cookbook/custom-elements/` | restated (ideas only); the metadata fact is observed export output |
| "Group" block | upstream "Model Elements → Group" | near-verbatim (no change) |
| "Relationships" block | upstream "Relationships" | near-verbatim (no change) |
| The `this`-identifier and relationship-identifier sentences | docs `71-language.md` (`## relationship`) + `05-identifiers.md` | restated (ideas only) |
| "Uniqueness" paragraph | upstream "Relationships → Uniqueness" | near-verbatim (no change) |
| Parent/child relationship sentence | observed pinned-CLI error (`Relationships cannot be added between parents and children`) | ideas only |
| "Identifiers → Flat (default)" | upstream "Identifiers → Flat" + docs `05-identifiers.md` (the duplicate-`api` example) | near-verbatim; the error string is observed |
| "Identifiers → Hierarchical (recommended)" | upstream "Identifiers → Hierarchical" + docs `05-identifiers.md` (groups caveat, relationship identifiers) | near-verbatim; the trailing caveat restated from the docs |

## `references/views-and-styles.md`

| Passage | Source | Adaptation |
|---|---|---|
| Intro (explicit view keys) | docs `03-basics.md` ("Workspace rules": unique keys, auto-generated keys not stable) + upstream (view keys in the examples) | restated (ideas only) |
| System Landscape / System Context / Container / Component / Dynamic / Deployment / Filtered / AutoLayout blocks | upstream "Views" | near-verbatim (no change) |
| Dynamic view explicit-ordering block | upstream "Views → Dynamic View" | near-verbatim (no change) |
| "Include/Exclude with Expressions" | upstream "Views → Include/Exclude with Expressions" | near-verbatim; the reluctant-wildcard sentence restated from the upstream's `*?` comment; the "exclude takes the same expressions" sentence added from docs `08-expressions.md` (idea only) |
| Element / Relationship Styles blocks + shapes list | upstream "Styles" | near-verbatim (no change) |
| "Styling All" / "Light/Dark Mode" / "Standard Style Recipe" | upstream "Styles" | near-verbatim (no change) |
| "Themes" | upstream "Themes" | adapted: the `themes default "https://..." "file.json"` line is dropped (never a theme with a URL — offline validation cannot fetch it), `theme default` kept, the built-in cloud theme names kept, the no-URL rule stated |
| "Terminology" / "Configuration" | upstream "Terminology" / "Configuration" | near-verbatim (no change) |
| "Directives for existing elements" | upstream "Directives → !element and !relationship", "Bulk Operations" | near-verbatim (no change); the `!include`/`!docs`/`!adrs` directive subsections dropped (MCP refuses them) |
| "Common patterns → Tagging for Filtered Views" / "Async/Sync Relationship Distinction" | upstream "Common Patterns" | near-verbatim (no change); the "Multi-file Organization" pattern dropped (built on `!include`) |

## `references/gotchas.md`

| Passage | Source | Adaptation |
|---|---|---|
| "Error table" | upstream "Troubleshooting" table (skeleton: the same eight failure modes) + observed pinned-CLI output | the upstream's generic strings ("X is not a valid identifier", "X already exists", "Unexpected token") are rewritten to the pinned CLI's exact output (`Too many tokens, expected: ...`, `The identifier "x" is already in use at line N`, `The destination element "x" does not exist at line N`, `Relationships cannot be added between parents and children at line N`); the view-key row is observed pinned-CLI output (the Phase 110 skill's own measured error) |
| "Declaration order" | upstream "Syntax Fundamentals" ("no forward references") + docs `91-faq.md` ("Why doesn't the DSL support forward referencing/hoisting?") | restated (ideas only: the imperative-wrapper explanation, the check-identifier-first advice, and the `this`-keyword sentence); the error string is observed |
| "Quoting" | docs `03-basics.md` ("Double quote characters are optional when a property/expression contains no whitespace", the `""` placeholder) | restated (ideas only); the `Too many tokens` string is observed |
| "Relationship description and technology" | upstream "Relationships" (the `[description] [technology]` grammar) + this repo's authoring rule (REQ-002) | mixed: the grammar is upstream; the verb-phrase/technology guidance and the "still parses — authoring knowledge, not an error message" framing are ideas only (this repo); the identity sentence is near-verbatim from upstream "Uniqueness" |
| "Element descriptions" | this repo's authoring rule (REQ-002) + observed export output | ideas only; the custom-element metadata fact is observed export output |
| "Flat identifiers" | upstream "Identifiers" + docs `05-identifiers.md` | near-verbatim (the two source passages merged); the rename-every-reference advice is ideas only |
| "Implied relationships" | docs `07-implied-relationships.md` | restated (ideas only: the person→container implies person→system example, the `!impliedRelationships false` switch, the strategy class names) |
| "Explicit view keys" | upstream (the view-key constraint in the examples) + observed pinned-CLI output | ideas only + observed error string (same passage the Phase 110 skill pins) |
| "Under the MCP" | — | ideas only: REQ-006/REQ-011, the observed MCP refusal strings |

## Dropped upstream content (no local passage)

- All Elixir/OTP/Phoenix/Ash/Oban/umbrella content: the entire
  "Elixir/OTP Patterns" section (Phoenix application workspace,
  Phoenix with components, Phoenix with Ash, umbrella application,
  event-driven Elixir system, LiveView dynamic view, Oban background
  processing).
- The Docker-CLI "Validation" section (`$RUNTIME`/podman/container, the
  `structurizr/structurizr:2026.09.19` commands, the inspect-as-CI-gate
  advice) — replaced by the MCP-tool note in `SKILL.md` (the full
  parse/validate/inspect loop stays the `structurizr-validate-loop`
  skill's single task).
- The `!include`, `!docs` and `!adrs` directive sections (including the
  `!docs` authoring conventions, the `!adrs` format requirements, and
  the duplicate-identifier restriction of included fragments) — the MCP
  refuses all three.
- "Workspace Extension" (`workspace extends`), "Multiple Workspaces"
  (master/focused layout, sibling stubs, the shared-fragment table,
  Structurizr Lite with multiple workspaces, Simon Brown's shared
  fragment pattern) — all built on multi-file content.
- "Views → Image View" (`plantuml <file|url>`, `mermaid <file|url>`,
  `image <file|url>`) — file/URL references a single-file MCP text
  input cannot resolve; image rendering is an MCP limit anyway.
- The "Related Skills" section (points at the upstream's own
  `c4-model`/`c4-review`/`c4-deployment` skills).
- The upstream frontmatter's `metadata`/`license` fields (this skill's
  frontmatter is exactly `name` + `description`).
