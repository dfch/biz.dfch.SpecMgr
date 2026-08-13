# Use Case Schema (v2) — Cockburn-based, built on `models/md`

## 1. Goal

Define a Markdown-plus-YAML-frontmatter schema for use cases, based on
Alistair Cockburn's "fully dressed" template
(https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm), machine-parseable
into a Pydantic model tree (`uc/models/v2/`) built on
`feat-5-md-model-parser`'s generic `models/md` engine
(`MarkdownStr`/`MarkdownSection1`..`6`/`MarkdownParagraph`/`MarkdownListItem`/
`MarkdownFrontmatter`).

This document **supersedes `v1/uc-schema.md`** (see the feature README's
Design Notes and DEC-009/DEC-010): v1's hand-written `uc/models/v1` parser and
its compound extension-action numbering (`3a1.`, `3a2.`, ...) are no longer
used. v1's artifacts are kept for historical reference only, not as a current
schema description.

## 2. Source documents

- **`uc_schema.json`** — the canonical, machine-readable field-level
  specification for this v2 shape: every field's type, nesting, and
  required/optional status. This document explains the *shape* of the
  Markdown source that produces that data; `uc_schema.json` remains the
  source of truth for exact structure. (`uc_reference_mdformat_schema.json`
  is a sibling artifact scoped to one specific worked example rather than the
  schema in general — see its own description field.)
- **`uc_reference.md`** / **`uc_reference_mdformat.md`** — complete worked
  examples ("Buy Goods"), the latter mdformat-normalized (project
  convention: use case source is always kept in mdformat's canonical
  formatting).
- **`uc_reference_mdformat_class.puml`** — the class diagram matching the
  `uc/models/v2/*.py` Pydantic models.

## 3. Heading structure

```
--- (YAML frontmatter) ---
# {title}                                          H1, required
## Characteristic Information                      H2, required
### Goal in Context                                 H3, required
### Scope                                           H3, required
### Level                                           H3, required
### Preconditions                                   H3, required
### Success End Condition                           H3, required
### Failed End Condition                            H3, optional
### Primary Actor                                   H3, required
### Secondary Actors                                H3, optional
### Trigger                                          H3, required
### Frequency                                        H3, optional
### Priority                                         H3, optional
### Performance Target                               H3, optional
### Channels to Primary Actor                        H3, optional
### Channels to Secondary Actors                      H3, optional
### Related Use Cases                                H3, optional
## Main Success Scenario                            H2, required
## Extensions                                       H2, optional
### Extension {ref}. {condition}                    H3, dynamic collection
## Sub-Variations                                   H2, optional
### Step {N}: {label}                               H3, dynamic collection
## Open Issues                                      H2, optional
## Related Information                              H2, optional
### Notes                                            H3, optional
### Assumptions                                      H3, optional
```

Max heading depth is H1–H3; no H4+ anywhere. See `uc_reference_mdformat.md`
for every section populated, and `uc_reference_mdformat_class.puml` for how
this maps onto Pydantic classes.

**Optional-H2 handling differs from v1's DEC-005 convention:** v1 always
rendered `Extensions`/`Sub-Variations`/`Open Issues`/`Related Information` as
present (possibly with placeholder text). v2's model fields
(`UseCase.extensions`, `.sub_variations`, `.open_issues`,
`.related_information`) are genuinely `Optional[...] = None` — the generic
`models/md` engine's own absence-detection (`MarkdownSection.get_extent`)
handles a truly missing heading natively, so there is no need for a
placeholder-text convention to keep parsing simple. A document may still
choose to include an empty/placeholder section for the same human-readability
reasons v1 cited; it is just no longer required.

## 4. Frontmatter

`UcFrontmatter` narrows the generic `MarkdownFrontmatter` (`models/md`) rather
than declaring its own fields from scratch:

| Key | Format | Notes |
|---|---|---|
| `id` | any string, optional | Specmgr-assigned identifier once registered; `null`/absent for a hand-authored, not-yet-registered document. Unlike v1's `^uc-[0-9]+$` pattern, no format is enforced — mirrors `AdrFrontmatter.id`'s convention. |
| `type` | `Literal["uc"]`, default `"uc"` | Fixed discriminator; a document omitting `type` entirely still parses as a use case. |
| `version` | `^[0-9]+\.[0-9]+\.[0-9]+$`, default `"1.0.0"` | The `models/md` schema version this frontmatter was written with. |
| `status` | enum: `draft`, `proposed`, `accepted`, `deprecated`, `superseded` | Blank/absent defaults to `"draft"`. |
| `created` | free-form string, optional | Not format-validated (unlike v1's ISO-8601 `format: date`) — `MarkdownFrontmatter.created` is a plain optional string. |
| `updated` | free-form string, optional | Same free-form convention as `created`. |

Unlike v1, `id`/`created`/`updated` are optional rather than mandatory, and
`created`/`updated` are no longer format-validated as ISO 8601 dates — both
changes inherited directly from the generic `MarkdownFrontmatter` base rather
than being use-case-specific decisions.

## 5. Characteristic Information

One H2 holding all of Cockburn's per-use-case metadata as H3 subsections,
each modeled as its own `MarkdownSection3` subclass in `uc/models/v2/use_case.py`.
Two subsection "kinds", matching the generic engine's own field-shape
convention (`body` vs. `items`):

- **`body: list[MarkdownParagraph]`** (prose) — `Goal in Context`, `Scope`,
  `Level`, `Primary Actor`, `Trigger`, `Frequency`, `Priority`,
  `Performance Target`
- **`items: list[MarkdownListItem]`** (bullet list) — `Preconditions`,
  `Success End Condition`, `Failed End Condition`, `Secondary Actors`,
  `Channels to Primary Actor`, `Channels to Secondary Actors`,
  `Related Use Cases`

Unlike v1, `Level` is **not** constrained to an enum (`Summary`,
`Primary task`, `Subfunction`) — the v2 model accepts free-form prose here;
no `field_validator` was ported forward for this field.

**`Related Use Cases`** is a plain, untyped bullet list
(`RelatedUseCases.items: list[MarkdownListItem]`) — unlike v1's typed
`{superordinate: str | None, subordinate: list[str]}` split, v2 does not parse
this list's `Superordinate: ...`/`Subordinate: ...` convention into separate
fields (see the feature README's Task 1.5 "what is still open" note); a
caller wanting that split must parse the raw item strings itself.

Two field-naming exceptions needed an explicit `@alias` to match the
document's exact heading text (found and fixed while building
`uc_reference_mdformat_schema.json`, see the feature README's matching
2026-08-12 entry):

- `GoalInContext` → `"Goal in Context"` (space-separated title case would
  already match; the explicit `@alias(..., AliasType.LITERAL)` here is
  redundant with the default derivation but present for clarity/consistency
  with the two below).
- `ChannelsToPrimaryActor` → `"Channels to Primary Actor"` (lowercase "to";
  the default `space_separated_name` derivation would title-case it to
  "Channels **To** Primary Actor").
- `ChannelsToSecondaryActors` → `"Channels to Secondary Actors"` (same
  lowercase-"to" override).

Required H3s: `Goal in Context`, `Scope`, `Level`, `Preconditions`,
`Success End Condition`, `Primary Actor`, `Trigger`. Everything else under
`Characteristic Information` is optional (`... | None = None` on
`CharacteristicInformation`).

## 6. Main Success Scenario

The happy path: a single, genuine CommonMark ordered list
(`MainSuccessScenario.steps: list[MarkdownListItem]`), one step per list item
in list order — position *is* the step's 1-based number; there is no separate
`number` field (unlike v1's `Step.number`). At least one step is required.

**Step-numbering contiguity is no longer a validated invariant — it is
structurally unnecessary.** v1's `MainSuccessScenario` had a `model_validator`
requiring steps to be numbered contiguously 1, 2, 3, ... because its
`list[Step]` shape *could* represent a gap/duplicate/out-of-order state. v2's
`steps` field is backed by `process_list_field`'s real CommonMark ordered-list
handling, which has no representable invalid state to check against — the
list's own position order is the only "numbering" that exists. (Confirmed
with a dedicated finding during Task 1.6, not just assumed.)

A step's list item may nest a continuation paragraph and/or sub-list beneath
its own leading sentence (e.g. the reference document's step 3); since
`MarkdownListItem` here declares no sub-fields, each `steps[]` entry is the
item's *complete* raw content verbatim, not just its first line.

## 7. Extensions

Alternative flows that still result in success. Optional at the H2 level
(unlike v1's always-present DEC-005 convention — see §3 above). Each
extension is its own H3, headed `### Extension {ref}. {condition}` — e.g.
`### Extension 3a. Company is out of one of the ordered items` — matched via
`Extension`'s regex `@alias` (`^Extension \d+[a-z]?\. .+$`), collected as
`Extensions.extensions: list[Extension] | None`. `{ref}`/`{condition}` are
**not** separate declared Pydantic fields; they are extracted from the
heading's own `.text` on demand (by the cross-reference validator, §9 below),
the same way `SubVariation` does.

Under each extension heading, a genuine CommonMark ordered list of actions
(`Extension.items: list[ExtensionItem]`) — **no compound sub-numbering**,
unlike v1/pre-DEC-010's `3a1.`, `3a2.`, ... An action's own leading paragraph
is `ExtensionItem.text`; an optional block-level continuation paragraph
(a *loose*-list blank line before the next block) is captured separately in
`ExtensionItem.notes: list[MarkdownParagraph] | None` — a same-paragraph soft
line break stays part of `text` instead. This `notes` field has no analogue
in v1.

Cross-references to the main scenario (e.g. "Return to step 4.",
"Continue to step 6.") are expressed as plain prose inside an action's own
`text`/`notes`, never encoded in the list marker or parsed/validated as a
structural reference — this is a deliberate, unchanged documentation
convention from v1 (DEC-010 changed *only* the action-numbering shape, not
this).

**Action-numbering-contiguity is likewise structurally unnecessary now** —
same "real ordered list" argument as §6's Main Success Scenario steps; v1's
separate `Extension`-level `model_validator` for this has no v2 equivalent
(confirmed, not just dropped by oversight — see Task 1.6's own writeup for
the `ExtensionItem.notes` question this raised and resolved).

## 8. Sub-Variations

Different technologies/methods for accomplishing a *single* step (as opposed
to Extensions, which branch the flow). Optional at the H2 level (§3). Each
sub-variation is its own H3, headed `### Step {N}: {label}` — e.g.
`### Step 1: Buyer may use` — matched via `SubVariation`'s regex `@alias`
(`^Step \d+: .+$`), collected as
`SubVariations.sub_variations: list[SubVariation] | None`. `{N}` has no
letter suffix (unlike Extensions' `{ref}`): a sub-variation always attaches
to exactly one main-scenario step, never to an extension action.

Under each heading, a plain bullet list of variation descriptions
(`SubVariation.items: list[MarkdownListItem]`, flat — no `text`/`notes`
split, unlike `Extension.items`); at least one variation is required per
sub-variation entry.

## 9. Cross-field validation: step-reference resolution

The **only** one of v1's three original cross-field `model_validator`s that
still applies (see §6/§7 above for why the other two became structurally
unnecessary): every `Extension`/`SubVariation` heading's reference must
resolve to an existing 1-based position in `main_success_scenario.steps`, and
no reference may repeat within either collection.

Implemented as `UseCase.validate_step_references_resolve_and_are_unique`
(`uc/models/v2/use_case.py`, `model_validator(mode="after")`):

1. Extract `{ref}` (Extensions, e.g. `"3a"`) / `{N}` (Sub-Variations, e.g.
   `"1"`) from each heading's `.text` via a small regex
   (`_EXTENSION_HEADING_PATTERN`/`_SUB_VARIATION_HEADING_PATTERN`), mirroring
   the same-shaped `@alias` patterns declared on `Extension`/`SubVariation`
   themselves.
2. Check the reference's *leading digits* (1-based) fall within
   `1..len(main_success_scenario.steps)`. An `Extension` reference's trailing
   letter (`3a` vs. `3b` vs. `3c`) is **never itself checked** against
   `main_success_scenario.steps` — same behavior as v1's own
   `_validate_unique_and_resolvable`.
3. Reject a duplicate reference within either the `extensions` or
   `sub_variations` collection.

This is the same invariant v1 enforced at the `UseCase` level (DEC-008); only
its extraction mechanism changed (regex over heading text, since v2 has no
dedicated `step_reference` field the way v1's `Extension`/`SubVariation`
models did).

## 10. Open Issues

A single flat bullet list of open questions (`OpenIssues.items`). Optional at
the H2 level (§3); the list itself may be empty if the section is present at
all.

## 11. Related Information

Two optional H3 subsections, `Notes` and `Assumptions`, each wrapping its own
flat `items: list[MarkdownListItem]` (`RelatedInformation.notes: Notes | None`,
`.assumptions: Assumptions | None`). This is one extra level of nesting
compared to v1's flatter `notes`/`assumptions` arrays declared directly on
`RelatedInformation` — a consequence of the generic engine's H3-subsection
convention, not a deliberate schema redesign.

## 12. What is enforced where

Two places carry validation now, one fewer than v1's three (§6/§7 explain why):

1. **`uc_schema.json`** (JSON Schema draft-07) / Pydantic field declarations
   (`uc/models/v2/*.py`) — per-field shape: types, nesting, and
   required/optional status. Unlike v1, no `pattern`/`enum` constraints are
   ported forward for `Level`, and frontmatter's `created`/`updated` are no
   longer date-format-validated (§4).
2. **`UseCase.validate_step_references_resolve_and_are_unique`** — the one
   surviving cross-field invariant (§9): `Extension`/`SubVariation`
   references must resolve to a real `main_success_scenario` step, with no
   duplicates within either collection.

## 13. Parsing

`uc/models/v2/parser.py`'s `parse_uc(text: str) -> UcDocument` (Task 1.8)
mirrors `models.adr.v1.parser.parse_adr`'s own split — a free function, not a
classmethod on `UcDocument` — rather than v1's dedicated
heading-outline-tree walker:

- Frontmatter: `frontmatter.loads(text)` splits the YAML block from the body;
  `UcFrontmatter.model_validate(...)` validates it (with the same
  YAML-native-scalar-to-`str` coercion `parse_adr` needed for date-like
  values).
- Body: `UseCase.from_text(format_text(post.content))` — the generic
  `models/md` engine's own recursive `from_text`, with no use-case-specific
  parsing code at all (unlike v1's dedicated list/compound-heading parsing
  logic).

Unlike v1, there is **no dedicated `UcParseError`.** A malformed
heading/list structure surfaces as the generic engine's own
`AssertionError` (from `MarkdownStr.from_text`/`process_field`); a
structurally-sound document whose field values or §9's cross-field invariant
are invalid raises `pydantic.ValidationError` the normal Pydantic way. Both
are left uncaught, exactly like `parse_adr` leaves its own two error
channels uncaught.

`parse_uc` round-trips the full `uc_reference.md` correctly (see
`tests/uc/models/v2/test_parser.py`).

## 14. Not yet built

Per the feature plan `README.md` task list, this document covers the current
state of Phase 1 (schema + models + parser + the one surviving validator)
only. Not yet built:

- A renderer (`UseCase` → canonical Markdown) — ADR has one
  (`models/adr/v1/renderer.py`); no v2 `uc` equivalent exists yet (v1 had
  none either).
- The `Related Use Cases` superordinate/subordinate typed split (§5) — parsed
  on demand by a caller, not modeled.
- PlantUML UC/Sequence diagram generation against the v2 model shape
  (Phase 2 — Task 2.1's UC diagram generator still targets v1's model).
- The full MCP tools/prompts/resources and CLI integration surface
  (Phase 3 — only a single `parse_uc` `@mcp.tool()` exists so far, ahead of
  Task 3.1's specification).

Don't assume any of the above exist — check the feature plan's task list for
current status before relying on this document for anything beyond schema
shape.
