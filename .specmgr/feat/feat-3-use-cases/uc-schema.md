# Use Case Schema — Cockburn-based, Markdown + YAML frontmatter

## 1. Goal

Define a Markdown-plus-YAML-frontmatter schema for use cases, based on
Alistair Cockburn's "fully dressed" template
(https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm), that is both
human-readable and machine-parseable into a Pydantic model
(`uc/models/v1/`). This mirrors the ADR feature's own schema doc
(`doc/adr-tool-plan.md`), but stays local to `.specmgr/feat/feat-3-use-cases/`
for now rather than under top-level `doc/`, since the whole feature is still
mid-flight (Task 1.4 of the feature plan, see `README.md`).

## 2. Source documents

- **`uc_schema.json`** — the canonical, machine-readable field-level
  specification: every field's type, format, enum, pattern, and
  required/optional status. This document explains the *shape* of the
  Markdown source that produces that data; `uc_schema.json` remains the
  source of truth for exact constraints (patterns, enums, `minItems`, ...).
- **`uc_example.md`** — a complete worked example ("Buy Goods"), referenced
  throughout below instead of restating every field.
- **`uc_class.puml`** — the class diagram matching the Pydantic models
  1:1 (`uc/models/v1/*.py`).

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
## Extensions                                       H2, always present (DEC-005)
### {stepRef}. {condition}                          H3, dynamic collection
## Sub-Variations                                   H2, always present (DEC-005)
### Step {N}: {label}                               H3, dynamic collection
## Open Issues                                      H2, always present (DEC-005)
## Related Information                              H2, always present (DEC-005)
### Notes                                            H3, optional
### Assumptions                                      H3, optional
```

Max heading depth is H1–H3; no H4+ anywhere. See `uc_example.md` for every
section populated, and `uc_class.puml` for how this maps onto Pydantic
classes.

**`" (required)"` / `" (optional)"` heading suffix:** `uc_example.md`
annotates each heading this way as an authoring aid. The parser
(`uc/models/v1/parser.py`) strips this suffix before matching against its
fixed title tables — it is a documentation convention only, not itself
validated. New use case documents are not required to include it, though
following the example's convention is recommended for consistency.

## 4. Frontmatter

Five required keys, no optional ones and no extras allowed
(`additionalProperties: false` in `uc_schema.json`, `extra: "forbid"` on
`UseCaseFrontmatter`):

| Key | Format | Notes |
|---|---|---|
| `id` | `^uc-[0-9]+$` | e.g. `uc-001` |
| `version` | `^[0-9]+\.[0-9]+\.[0-9]+$` | schema-instance version, semver |
| `status` | enum: `draft`, `proposed`, `accepted`, `deprecated`, `superseded` | |
| `created` | ISO 8601 date | per ADR 23a14195-339c-48af-99d2-97c9964041ae |
| `updated` | ISO 8601 date | same format as `created` |

Unlike ADR's frontmatter, there is currently no server-assigned `id` /
`version`-round-trip distinction here — both are plain author-supplied
fields (no MCP tool layer exists yet for this domain; see feature plan
Phase 3).

## 5. Characteristic Information

One H2 holding all of Cockburn's per-use-case metadata as H3 subsections.
Two subsection "kinds":

- **text** — a single free-text block (`Goal in Context`, `Scope`, `Level`,
  `Primary Actor`, `Trigger`, `Frequency`, `Priority`,
  `Performance Target`)
- **list** — a bullet list, one item per line (`Preconditions`,
  `Success End Condition`, `Failed End Condition`, `Secondary Actors`,
  `Channels to Primary Actor`, `Channels to Secondary Actors`)

`Level` is additionally constrained to the enum `Summary`, `Primary task`,
`Subfunction` (Cockburn's three scope levels).

**Related Use Cases** is a special-cased H3: two labeled bullets,
`- Superordinate: {name}` (single value) and
`- Subordinate: {name1}, {name2}, ...` (comma-separated list) — see
`uc_example.md` lines 85–86. Both are optional; the whole `Related Use Cases`
H3 itself is optional.

Required H3s: `Goal in Context`, `Scope`, `Level`, `Preconditions`,
`Success End Condition`, `Primary Actor`, `Trigger`. Everything else under
`Characteristic Information` is optional.

## 6. Main Success Scenario

The happy path: an ordered numbered Markdown list, one step per line
(`1. Buyer calls in...`, `2. Company captures...`, ...). At least one step
is required.

**Step numbering is enforced, not just parsed:** `MainSuccessScenario`'s
`model_validator` requires steps to be numbered contiguously 1, 2, 3, ...
with no gaps, duplicates, or out-of-order entries — a cross-item invariant
JSON Schema draft-07 cannot express (it can only constrain each step's
`number` individually via `minimum: 1`), so it lives in
`uc/models/v1/main_success_scenario.py` instead.

A numbered-list line may be followed by non-list indented continuation
lines (free text); the parser joins these onto the preceding item's
description with a single space (see `uc_example.md` line 92–93, step 3's
"This will use our trusty IBM OS/390 green screen application" aside).

## 7. Extensions

Alternative flows that still result in success. Always present per
DEC-005 (may be empty/placeholder if none apply). Each extension is its own
H3, headed `### {stepRef}. {condition}` — e.g.
`### 3a. Company is out of one of the ordered items` — where `stepRef`
matches `^[0-9]+[a-z]?$` (a main-scenario step number, optionally suffixed
with a lowercase letter for multiple extensions off the same step, e.g.
`10a`, `10b`, `10c` in `uc_example.md`).

Under each extension heading, a numbered list of **compound-numbered**
actions: `3a1. Company informs buyer...`, `3a2. Buyer chooses to...`, where
each action's `number` matches `^[0-9]+[a-z]?[0-9]+$` (the extension's
`stepRef` prefix plus a sequential digit suffix).

**Two more cross-item invariants enforced beyond JSON Schema:**
- `Extension.actions` must be numbered `{step_reference}1`,
  `{step_reference}2`, ... sequentially, no gaps/duplicates/out-of-order —
  enforced on `Extension` itself (`uc/models/v1/extension.py`).
- Every extension's `step_reference` must resolve to an actual
  `main_success_scenario` step number, and no `step_reference` may repeat
  across the `extensions` collection — enforced at the `UseCase` level
  (`uc/models/v1/use_case.py`), since it needs both sibling sections at
  once.

An extension's actions may end with `Return to step {N}` or
`Continue to step {N}` (free text, not itself a modeled field — see
`uc_example.md` lines 110, 117, 123) to indicate where control resumes in
the main scenario; this is documentation convention only, not parsed or
validated as a reference.

## 8. Sub-Variations

Different technologies/methods for accomplishing a *single* step (as
opposed to Extensions, which branch the flow). Always present per DEC-005.
Each sub-variation is its own H3, headed `### Step {N}: {label}` — e.g.
`### Step 1: Buyer may use` — where `{N}` matches `^[0-9]+$` (no letter
suffix, unlike Extensions: a sub-variation always attaches to exactly one
main-scenario step, never to an extension action). `{label}` is descriptive
only, not itself a modeled field.

Under each heading, a plain bullet list of variation descriptions
(`- Phone call`, `- Fax`, ...); at least one variation is required per
sub-variation entry.

Like Extensions, every sub-variation's `step_reference` must resolve to an
existing `main_success_scenario` step number, with no duplicates within the
`sub_variations` collection — same `UseCase`-level check as §7.

## 9. Open Issues

A single flat bullet list of open questions (`uc_example.md` lines
187–192). Always present per DEC-005; the list itself may be empty.

## 10. Related Information

Two optional H3 bullet lists, `Notes` and `Assumptions`. Always present at
the H2 level per DEC-005; both H3s (and the bullets within) are optional.

## 11. DEC-005: always render optional H2 sections

Even when empty, `Extensions`, `Sub-Variations`, `Open Issues`, and
`Related Information` are always included as H2 headings (with a
placeholder like "(None identified)" when there is no content). This keeps
structure consistent across every use case document, makes clear these
aspects were *considered* even when empty, simplifies parsing, and keeps
git diffs clean when content is later added. See feature plan `README.md`
DEC-005 for the full rationale.

## 12. What is enforced where

Three places carry validation, deliberately split by what each can express:

1. **`uc_schema.json`** (JSON Schema draft-07) — per-field shape: types,
   patterns, enums, `minLength`/`minItems`, required/optional, and
   `additionalProperties: false`. Documents the schema in a
   language/tool-agnostic form; does not itself run against any file yet.
2. **Pydantic field declarations** (`uc/models/v1/*.py`) — the runtime
   mirror of (1): `Field(..., pattern=..., min_length=...)`, per-field
   `field_validator`s (e.g. `level`/`status` enum checks).
3. **Pydantic `model_validator`s** — cross-field/cross-item invariants that
   (1)/(2) cannot express on a single field in isolation:
   - `MainSuccessScenario`: step numbers contiguous 1, 2, 3, ...
   - `Extension`: action numbers `{step_reference}1`, `{step_reference}2`, ...
   - `UseCase`: every `Extension`/`SubVariation.step_reference` resolves to
     a real `main_success_scenario` step, no duplicate references within
     either collection

Unlike ADR's deliberate choice *not* to cross-check
`Considered Options` prose against the `Option` sub-section collection
(`doc/adr-tool-plan.md` §7 — accepted drift, no validator), the use case
schema's Task 1.3 was explicitly scoped to include "step numbering", so (3)
above is enforced rather than left as a known gap (see DEC-008).

## 13. Parsing

`uc/models/v1/parser.py`'s `parse_uc(text: str) -> UseCase` mirrors ADR's
own `models/adr/v1/parser.py` heading-outline-tree approach (build a nesting
tree of headings via `markdown-it-py`, then walk it), extended with:

- numbered/bulleted Markdown **list** parsing (main-scenario steps,
  extension actions, most `list[str]` fields) — ADR's schema has no
  equivalent, since none of its sections are numbered/bulleted lists;
- compound-heading parsing for the two dynamic H3 collections
  (`### {stepRef}. {condition}` for Extensions,
  `### Step {N}: {label}` for Sub-Variations).

Two distinct error channels, same split as ADR's parser:

- **`UcParseError`** — the Markdown *structure* doesn't fit this schema: an
  unrecognized/duplicate/misplaced heading, a heading level this schema
  doesn't define, a malformed list line, or stray content before the first
  H1. These never even reach a Pydantic field.
- **`pydantic.ValidationError`** — the structure is fine, but a field's
  value (or one of §12.3's cross-field invariants) is invalid once
  `UseCase(...)` is constructed. Not caught or wrapped by `parse_uc`.

`parse_uc` round-trips the full `uc_example.md` correctly (see
`tests/uc/models/v1/test_parser.py`).

## 14. Not yet built

Per the feature plan `README.md` task list, this document covers Phase 1
(schema + models + parser + validators) only. Not yet built:

- A renderer (`UseCase` → canonical Markdown) — ADR has one
  (`models/adr/v1/renderer.py`); no `uc` equivalent exists yet.
- PlantUML UC/Sequence diagram generation (Phase 2).
- MCP tools/prompts/resources and CLI integration (Phase 3).

Don't assume any of the above exist — check the feature plan's task list
for current status before relying on this document for anything beyond
schema shape.
