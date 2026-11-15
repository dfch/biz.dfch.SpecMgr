# Source map

Every adapted passage of this skill, mapped to its source file at the
pinned commit. A passage marked "ideas only" copies no text and therefore
carries no attribution line — the notice and this map stay consistent:
adapted text exists in exactly the one file `NOTICE.md` lists.

Sources:

- `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`
  (MIT, "Copyright (c) 2026 Georges Martin"); source path
  `skills/c4-model/SKILL.md` (single-file skill).
- `structurizr/structurizr.github.io` @
  `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (MIT); source paths under
  `docs/dsl/cookbook/` (the view pages) and `docs/dsl/03-basics.md`
  (the view-key rule).

"Observed" passages quote the pinned Structurizr CLI
(`structurizr/structurizr:2026.10.26-noble`) or this repo's spike TXT
4a09922d-bc32-4c03-86ba-d30ebc34e0b8 — facts from this repo's harness and
planning record, not text of either source, and marked ideas only.

## `SKILL.md` — ideas only

| Passage | Source | Notes |
|---|---|---|
| The trigger description + the intro's create-flow hook | — | Ideas only: the create-flow framing ("for a C4 model being built in Structurizr DSL", "the views are part of the deliverable: design them in the same pass", the fifth trigger phrase) is this repo's iteration-2 trigger-surface fix (iteration 1 measured 0/5 loads on the CREATE prompt); no source text |
| The five rules | upstream `Diagram Types` / `Diagram Selection Guide` (structure) + this repo's REQ-004 | Ideas only: one line per rule in this repo's wording; rule 2's size bound and the 150-element/29,664-px fact are the spike's Finding 8; rule 3's key constraint is the Phase 110 observed fact (docs `03-basics.md` view-key rule, restated); rule 4's External fact is the pinned DSL's observed shape (the Phase 130 precedent); rule 5 is the docs' groups/filtered content (restated) |
| "Designing the views of a large model" | the spike's Suggestion 3 | Ideas only: the split strategy (several views, explicit include lists instead of a bare wildcard) is this repo's restatement of the spike's "explicit include lists instead of `include *`"; the single-pass bullet is this repo's iteration-3 efficiency fix |
| "Checking the result" | — | Ideas only: the light validate pointer is this repo's (REQ-006/REQ-011); the routing to the `structurizr-validate-loop` skill is this repo's split (REQ-003 vs REQ-004); the single-pass write and the validate-only scope note ("not needed here") are this repo's iteration-3 efficiency fix (iteration 2 measured the furthest trials killed at the 1200 s timeout after 22 steps incl. 9 parse + 4 inspect round trips) |
| "The MCP limits" | the spike's Finding 3 (the MCP's surface) | Ideas only: the no-image-rendering rule and the single-file rule are this repo's (REQ-006 — the limits this skill depends on); the pointer to the C4-PlantUML gotchas is this repo's |
| "When the MCP is absent" | — | Ideas only: REQ-011 (view design is still possible without the MCP — it is model structure; the MCP-based checking is not) |

No passage in `SKILL.md` copies text; it has no attribution line in
`NOTICE.md`.

## `references/view-selection.md`

| Passage | Source | Adaptation |
|---|---|---|
| "Diagram Types" (the Core Diagrams + Supporting Diagrams tables) | upstream `skills/c4-model/SKILL.md` "Diagram Types" | near-verbatim (no change) |
| "Diagram Selection Guide" (the two questions + the audience/question mappings) | upstream "Diagram Selection Guide" | near-verbatim (no change) |
| "The view kinds of the Structurizr DSL" (the per-kind list) | docs `docs/dsl/cookbook/{system-context-view,container-view,component-view,dynamic-view,deployment-view,filtered-view,custom-view}/index.md` | restated (ideas only); the filtered-view base-hiding fact is the docs' own wording restated; the custom-view restriction (custom elements only) is the observed pinned-CLI parser error, verified at Task 140.100 |
| "Keeping a view readable" (groups, filtered views, several-small-views) | docs `docs/dsl/cookbook/{groups,filtered-view}/index.md` | restated (ideas only); the view-DSL syntax the notes refer to stays in the `structurizr-dsl-authoring` skill (the locked scope cut) |

## `references/view-size-and-keys.md` — ideas only + observed

| Passage | Source | Notes |
|---|---|---|
| The about-20-elements bound, the 150-element / 29,664-px fact | the spike's Finding 8 (Suggestion 3) | Ideas only: restated from this repo's spike, no external text |
| What counts as an element of a view (the include-list scoping) | observed pinned-CLI export JSON (Task 140.100 verification) | Ideas only: a view's exported `elements` list is the scoped containers/components plus every linked element (people, other systems, custom elements), the scoped system itself not counted; an explicit include list carries exactly the listed elements |
| The explicit-key rule, the `<Kind>-NNN` format, the `generatedKey` mark, the `views.view.key` finding text | observed pinned CLI (export + `inspect` over a keyless view) + docs `03-basics.md` view-key rule | The finding text is the pinned CLI's own output; the "not guaranteed to be stable over time" phrasing is the docs' rule restated |

## `references/c4-plantuml-gotchas.md` — observed

| Passage | Source | Notes |
|---|---|---|
| Custom elements silently dropped | the spike's Finding 4 | Ideas only: restated from this repo's spike |
| `include *`-pulled elements dropped | the spike's Finding 4 | Ideas only |
| The `$tags=""` default, the `c4plantuml.tags "true"` + `c4plantuml.elementProperties "true"` view properties | the spike's Finding 4 | Ideas only; the property names are the DSL's own (observed) |
| The default `Element` tag white-on-white trap | the spike's Finding 4 (Suggestion 3) | Ideas only |

## Dropped upstream content (no local passage)

- The upstream `c4-model` skill's "C4 Abstractions" (Levels 1–4),
  "Notation Rules", "Workflow: Adding Elements to a Model" (Steps 1–4),
  "Common Modeling Decisions", "Common Mistakes" and "Diagram Staleness"
  — all owned by the `c4-modeling` skill (Phase 130).
- The entire Erlang/Elixir/OTP Modeling Guide and every Elixir/Phoenix/
  Ash/Oban pattern and relationship-label table (the locked removals).
- The Docker-CLI "Validation" section (`$RUNTIME`/podman/container, the
  pinned dated image, the inspect-as-CI-gate advice) — replaced by the
  light MCP-validate pointer in `SKILL.md` (the full loop stays the
  `structurizr-validate-loop` skill's single task).
- The "Related Skills" section (points at the upstream's own
  `structurizr-dsl`/`c4-review`/`c4-deployment` skills).
- The upstream frontmatter's `metadata`/`license` fields (this skill's
  frontmatter is exactly `name` + `description`).
- The docs' DSL code examples on every view page (the view block grammar
  is the `structurizr-dsl-authoring` skill's `references/views-and-styles.
  md` — the locked scope cut), the element-styles page (the styles recipes
  belong there too), and the image-view content (out of scope).
