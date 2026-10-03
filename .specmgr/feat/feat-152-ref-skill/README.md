---
classification: null
created: '2026-10-03T07:27:21.033+02:00'
id: feat-152-ref-skill
status: review
type: feat
updated: '2026-10-03T15:07:49.504+02:00'
version: 1.0.0
---

# Feature: Agent-Initiated Cross-Reference Retrieval via opencode Skill (specmgr-refs)

## Plan

### Overview

feat-144-ref-artifact shipped the specmgr cross-reference retrieval stack: the generic `list_references` MCP tool, the project-local `/refs` opencode command, and the read-only `ref-finder` subagent. Two gaps remain for agents that need to retrieve references while working: (1) trigger asymmetry — `/refs` is user-initiated and only fires when a human types the command, so an agent mid-task has no context-triggered way to discover the convention and the tool; an opencode skill, whose description is always present in the agent's system prompt and loads itself when the task matches, closes exactly this gap. (2) single-document scope — the command and subagent only answer "what does document X reference?"; workflows that compose `list_references` (multi-hop graph traversal, batch resolution validation across the registry, reverse lookup of "which documents reference X") are codified nowhere, so an agent asked any of these improvises the loops, pagination, dedup, and presentation every time. This feature adds a thin project-local opencode skill (`.opencode/skills/specmgr-refs/SKILL.md`) that acts as a router, not a re-implementation: single-document requests go to `list_references` directly (or delegate to `ref-finder` / `/refs`), graph/batch/reverse requests follow codified composition workflows, and the skill keeps the read-only posture and reporting conventions of the existing `ref-finder` agent.

### Requirements

- REQ-001: A new project-local opencode skill `.opencode/skills/specmgr-refs/SKILL.md` exists, with a description matching specmgr cross-reference retrieval task phrasings so the agent loads it mid-task without user initiation.
- REQ-002: The skill acts as a router, not a re-implementation: single-document reference retrieval is delegated to the existing `list_references` tool (or the `ref-finder` subagent / `/refs` command), and the skill body never copies `ref-finder`'s workflow narrative (pointer, not duplication).
- REQ-003: The skill codifies a multi-hop graph traversal workflow (e.g. "show me this sysrs's reference graph, two levels deep"): per-level `list_references` calls, seen-set dedup, pagination while `truncated`, **NOT FOUND** flagging, and tabular reporting.
- REQ-004: The skill codifies a batch resolution validation workflow (e.g. "do all cross-references across the registry resolve on disk?"): iterate `list_<d>` over the whole-body domains (the `list_references` source-domain enum additionally accepts `adr` — deliberately excluded here, see Design Notes), run `list_references` per document, aggregate per-domain and overall `total`/`error_count`, and flag every unresolvable reference.
- REQ-005: The skill codifies a reverse lookup workflow (e.g. "which documents reference REQ `<uuid>`?"): scan candidate documents via paged `list_<d>` plus per-document `list_references`, match on the target `(type, id)`, and report the referencing documents with `type`/`id`/`title`/`path`.
- REQ-006: The skill preserves `ref-finder`'s read-only posture (no edit/write/commit) and reporting conventions (`type`/`id`/`title`/`path` per reference, **NOT FOUND** prefix for unresolvable references, stated `total` and `error_count`).
- REQ-007: Registration and documentation: `AGENTS.md` registers the skill in its `list_references` tool entry (following the existing `repair`-skill registration pattern), the root `README.md` documents it in its `## Referencing Artifacts` section alongside the `/refs` command and the `ref-finder` subagent, `CHANGELOG.md` records the addition, and the skill file conforms to the project-local `.opencode` skill conventions (same shape as the existing `repair` and `feat-numbering` skills).
- REQ-008: A drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py` (structure per `tests/opencode/test_skill_feat_numbering.py`) pins the skill's load-bearing wording so it cannot silently drift from the feat-144 contract: the file location; frontmatter exactly `name`/`description` with `name` equal to the containing folder and a third-person `description` carrying the trigger keywords; the inherited reporting vocabulary (**NOT FOUND** prefix, `type`/`id`/`title`/`path` row fields, stated `total`/`error_count`/`truncated`); and the single-document delegation pointer naming `list_references`/`ref-finder`/`/refs`.

### Acceptance Criteria

- [x] ACC-001: The skill's description matches reference-retrieval phrasings (e.g. "which documents reference X", "show me the reference graph", "do all cross-references resolve") well enough that the agent loads the skill unprompted in matching mid-task contexts. The locked description carries all five ACC-001 example phrasings ("what does document X reference", "list the references of X", "show me the reference graph", "do all cross-references resolve", "which documents reference X") as case-insensitive substrings, verified in Phase 120's description match check and pinned by `TestSkillFrontmatter::test_description_carries_trigger_keywords`; the residual (a fresh opencode session loading the skill unprompted) is flagged for review-time confirmation.
- [x] ACC-002: The single-document, graph, batch, and reverse workflows are each covered by exactly one codified path in the skill, with no overlapping or contradictory instructions. The skill's "Route by task shape" table maps each of the four task shapes to exactly one path (single-document → the delegation pointer; graph/batch/reverse → their own single numbered workflows), and the one deliberate divergence (compositions page every call to completion, overriding the single-document interactive page-when-asked default) is explicitly scoped in the skill body so no instruction overlaps or contradicts — cross-checked in Phase 100's Task 100.120 (recorded outcome: pass).
- [x] ACC-003: The skill body contains no narrative duplication of `ref-finder`'s workflow — single-document handling is a pointer/delegation, not a copy. The single-document section is a pointer naming the `list_references` tool / `ref-finder` subagent / `/refs` command and re-tells none of `ref-finder`'s workflow narrative (Phase 100 cross-check, recorded in the plan); the drift-guard test pins the phrase "is a pointer to the existing stack, never a copy of it" plus all three stack names.
- [x] ACC-004: All four workflows execute successfully against live specmgr documents in this repository (smoke exercise), reporting expected rows with **NOT FOUND** flagging. Phase 120 smoke-exercised all four workflows against this repository's live registry — single-document `feat feat-144-ref-artifact` (`total=5`, `error_count=0`, all five ADRs resolve) and `feat feat-152-ref-skill` (`total=1`, `error_count=0`); the **NOT FOUND** path proven via a throwaway temp source per feat-144's recorded precedent (`total=6`, `error_count=1`, the all-zero-uuid ADR row with null `title`/`path`, temp dir removed); graph from `feat feat-144-ref-artifact` at the default N=2 (level 1 `total=5`, level-2 aggregate `total=9`, 0 errors, 11 unique documents seen); batch across the 12 whole-body domains (overall `total=173`, `error_count=1` — the one **NOT FOUND** row is an illustrative placeholder uuid quoted in `feat feat-135-related-artifacts-risks`'s own plan text, the accepted feat-144 regex-extraction caveat; six pre-existing null-id `parse_failures` tallied, not scanned); reverse for `adr e369ee2e-3353-4f92-991c-6367d76d832e` (13 hits, `feat feat-152-ref-skill` among them). Closing note on the self-referential dynamic: the Phase 120 progress entry quotes the smoke's uuids verbatim, so under the same accepted caveat the live registry's feat-152 document is itself a reference source on any fresh batch re-run (the orchestrator's independent re-run reported overall `total=180`, `error_count=3`) — correct behavior, recorded so reviewers are not surprised.
- [x] ACC-005: The REQ-008 consistency test exists, pins the location, frontmatter, trigger keywords, reporting vocabulary, and delegation pointer as listed, and passes under the repository quality gate's `pytest` run (the mechanical counterpart of REQ-002/REQ-006). `tests/opencode/test_skill_specmgr_refs.py` exists (nine tests, five classes) and pins exactly what the ACC lists — the file location, the frontmatter (exactly `name`/`description`, `name` equal to the containing folder, third-person description carrying the eight locked trigger keywords), the inherited reporting vocabulary (**NOT FOUND**, `type`/`id`/`title`/`path`, `total`/`error_count`/`truncated`), and the single-document delegation pointer (locked phrase plus `list_references`/`ref-finder`/`/refs`) — and it passed in the Phase 110/120 quality-gate `pytest` runs (4025 passed, the nine included).

### Scope

#### Included

- The skill file `.opencode/skills/specmgr-refs/SKILL.md` (description + router body)
- The codified workflows: single-document, multi-hop graph traversal, batch resolution validation, reverse lookup
- Read-only posture and `ref-finder` reporting conventions preserved in the skill
- The drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py`
- Documentation: `AGENTS.md` registration + root `README.md` `## Referencing Artifacts` mention + `CHANGELOG.md` entry
- This feature's plan folder (`.specmgr/feat/feat-152-ref-skill/`)

#### Explicitly Out Of Scope

- New MCP capabilities (e.g. `reverse`/`depth` parameters on `list_references`) — client-agnostic feature work, its own issue if pursued
- Changes to the `list_references` tool, the `/refs` command, or the `ref-finder` subagent (beyond pure pointer/reference fixes)
- Packaging or distribution outside the repository (the skill lives in the project-local `.opencode` tree; no PyPI impact)
- Non-opencode client support (the skill is opencode-specific; the MCP tools remain the client-agnostic surface)
- ADR-inclusive batch validation (iterating `list_adr` for the REQ-004 workflow) — recorded deliberate scoping decision, see Design Notes

### Dependencies

#### Depends On

- feat-144-ref-artifact (done) — the skill routes to its `list_references` tool, `/refs` command, and `ref-finder` subagent

#### Blocks

- none

### Design Notes

- Router, not re-implementation: the skill's body is a decision table over task shape. Single-document retrieval is a pointer to the existing `list_references` tool / `ref-finder` subagent / `/refs` command (no narrative copy, so the two do not drift apart). Graph, batch, and reverse are the only three compositions codified, each as one numbered workflow (loops + seen-set dedup + pagination while `truncated` + **NOT FOUND** flagging + tabular reporting with stated `total`/`error_count`).
- Trigger mechanism: the skill's description is the always-present surface (opencode lists it in the agent's system prompt and loads the skill when the task matches); it is written to match reference-retrieval phrasings, not implementation vocabulary.
- Layering: project-local `.opencode` tree (like feat-144's command + agent), config not `src/` — no packaging, no PyPI, no CI impact; the client-agnostic surface stays the MCP tools.
- Read-only posture: the skill instructs retrieval and reporting only — no edit/write/commit — consistent with `ref-finder`'s denied-permission model.
- Directory choice: the skill lives at the plural `.opencode/skills/specmgr-refs/` path, following the `feat-numbering` precedent (the repo's newest skill, feat-163); OpenCode discovers both singular and plural project skill directories, and the first skill (`repair`, feat-150) uses the singular `.opencode/skill/` — the newest-skill precedent wins.
- Batch workflow scoping (REQ-004): the batch validation iterates the 12 whole-body domains only. The `list_references` source-domain enum additionally accepts `adr`, and ADR documents can carry outbound `<TYPE> <uuid>` references — the exclusion is deliberate, since `adr` is slated for removal (GitHub issue #46) and the workflow targets the whole-body registry; an ADR-inclusive registry-wide check would add a `list_adr` iteration and is out of scope here.
- Reverse lookup cost (REQ-005): the reverse lookup is an O(registry-size) scan — paged `list_<d>` over the 12 whole-body domains plus one `list_references` call per document — and no domain can be pre-filtered, because the extractor regex-scans every body for the 11-tag reference vocabulary (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS/FEAT). The skill body states this cost expectation so an implementer does not "optimize" the scan by skipping domains.

#### Locked design (Phase 100)

Phase 100 (Tasks 100.100–100.130) locks the design; Phase 110 executes it mechanically without re-deciding anything. Four artifacts are locked below: (1) the skill description string (Task 100.100), (2) the full `SKILL.md` file draft, frontmatter and body (Task 100.110), (3) the consistency-test pin list (Task 100.130), and (4) the Task 100.120 cross-check outcome against `.opencode/agent/ref-finder.md`. The choices that go beyond the plan's existing wording (frontmatter shape, tag vocabulary count, default graph depth, placement anchors) are recorded in the `### Decisions Made` entry of the same date.

**(1) Locked description string (Task 100.100)** — the single-line `description` value of the skill frontmatter, verbatim (the frontmatter is exactly `name`/`description`, single-line plain YAML scalar, no `>-` block — see the `### Decisions Made` entry for the shape decision):

```
Use when resolving or retrieving specmgr cross-references -- single-document requests ("what does document X reference", "list the references of X"), reference-graph requests ("show me the reference graph"), batch-resolution requests ("do all cross-references resolve"), and reverse-lookup requests ("which documents reference X") -- by routing single-document retrieval to the `list_references` MCP tool (or the `ref-finder` subagent / `/refs` command) and following the codified graph, batch, and reverse workflows.
```

**(2) Full `SKILL.md` file draft (Task 100.110)** — Phase 110 writes the fenced content below byte-for-byte to `.opencode/skills/specmgr-refs/SKILL.md` (frontmatter and body together; the file carries no code block of a ruff-supported language, so `ruff format --check` leaves it untouched):

```
---
name: specmgr-refs
description: Use when resolving or retrieving specmgr cross-references -- single-document requests ("what does document X reference", "list the references of X"), reference-graph requests ("show me the reference graph"), batch-resolution requests ("do all cross-references resolve"), and reverse-lookup requests ("which documents reference X") -- by routing single-document retrieval to the `list_references` MCP tool (or the `ref-finder` subagent / `/refs` command) and following the codified graph, batch, and reverse workflows.
---

# SpecMgr Cross-Reference Router

You are a router over the specmgr cross-reference retrieval stack
(feat-144-ref-artifact): the `list_references` MCP tool, the read-only
`ref-finder` subagent (`.opencode/agent/ref-finder.md`), and the `/refs`
command (`.opencode/command/refs.md`). Single-document reference retrieval
already has a home there -- you point to it, you never re-implement it. What
you codify are the three compositions that have nowhere else: multi-hop
graph traversal, batch resolution validation, and reverse lookup.

You are read-only: you never edit, write, create, or delete any document,
and you never commit. Your only actions of consequence are calling
`list_references` and the paged `list_<d>` scans the batch and reverse
workflows need.

## Route by task shape

| Task shape | Example phrasing | Path |
| --- | --- | --- |
| Single document | "what does document X reference?" / "list the references of X" | Delegate -- the pointer, below |
| Multi-hop graph | "show me the reference graph, two levels deep" | The graph workflow, below |
| Batch validation | "do all cross-references resolve?" | The batch workflow, below |
| Reverse lookup | "which documents reference REQ `<uuid>`?" | The reverse workflow, below |

If the task does not name a specmgr `<type> <id>` pair (or a registry-wide
request), ask for one rather than guessing.

## Single-document: delegate, do not re-tell

A single-document request ("what does `<type> <id>` reference?") is a
pointer to the existing stack, never a copy of it:

- **Prefer delegation.** If the host can launch subagents (a `task` tool is
  available) and `ref-finder` is among them, delegate the `<type> <id>` pair
  to the `ref-finder` subagent; it owns the single-document workflow and
  reports its own rows.
- **The `/refs` command already routes to `ref-finder`.** If the user typed
  `/refs <type> <id>`, let it run.
- **Otherwise, call the tool directly:** `list_references(type, id)`,
  reported per the reporting conventions below.
- Do not re-tell `ref-finder`'s workflow in the skill or in the report --
  that narrative stays in `.opencode/agent/ref-finder.md`, and the two must
  not drift apart.

## Graph workflow (multi-hop traversal)

Use for "show me the reference graph of `<type> <id>`, N levels deep".

1. Parse the source `<type> <id>` pair and the requested depth N. If the
   user did not state a depth, use N = 2 and say so in the report.
2. Initialize the seen-set with the source's own `(type, id)` pair.
3. **Level 1**: call `list_references(type, id)` for the source and page to
   completion (while `truncated` is true, call again with a higher `offset`
   in steps of `max_results`).
4. **Level k+1**: expand only the level-k rows that resolved on disk -- a
   **NOT FOUND** row has no body to scan, and `list_references` raises for
   a missing source. For each resolvable row, call
   `list_references(row.type, row.id)` and page to completion. Add every
   row's `(type, id)` to the seen-set; a pair already seen at an earlier
   level is reported once, at the level it first appeared, and is never
   expanded again.
5. Stop at level N, or early when a level yields no new `(type, id)` pair.
6. **Report** one table per level -- columns Level, `type`, `id`, `title`,
   `path` -- with **NOT FOUND** prefixed to every row whose `error` is set
   (its `title`/`path` are null), stating each level's `total` and
   `error_count`, plus an overall summary: depth reached, unique documents
   seen, total references, total errors.

In the compositions below (graph, batch, reverse), page every
`list_references` and `list_<d>` call to completion: the interactive
"report the first page and offer to continue" default of the single-document
path does not apply, because a partial level or a partial registry breaks
dedup, traversal, and aggregation.

## Batch workflow (resolution validation)

Use for "do all cross-references across the registry resolve on disk?".

1. **Iterate the 12 whole-body domains in canonical order:**
   req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs. The `adr` exclusion is
   deliberate and must not be "fixed": `list_references`'s source enum
   accepts `adr` and ADR documents can carry outbound references, but `adr`
   is slated for removal (GitHub issue #46) and this workflow targets the
   whole-body registry.
2. **Per domain,** page `list_<d>` to completion (while `truncated`, a
   higher `offset`). A row whose `id` is null (a `<failed to parse>` row)
   cannot be scanned -- `list_references` needs a source id -- so count it
   in a separate per-domain `parse_failures` tally, listing the row's
   `path` and `error`; it is not a reference row.
3. **Per scannable document,** call `list_references(<domain>, id)` and
   page to completion. Aggregate per domain: documents scanned, `total` (the
   sum of each document's own `total`), `error_count` (the sum of each
   document's own `error_count`), and every **NOT FOUND** row.
4. **Report** one table per domain (columns: domain, documents scanned,
   `parse_failures`, `total`, `error_count`), then one overall table with
   the same columns summed, and list every unresolvable reference with its
   source document (the referencing `type`/`id`/`title`/`path`) and the
   **NOT FOUND** row (the referenced `type`/`id` and `error`). A registry
   where every reference resolves is the report: overall `error_count` 0
   and no **NOT FOUND** rows.

## Reverse workflow ("which documents reference X?")

Use for "which documents reference REQ `<uuid>`?" -- any target `<type>
<id>` pair, including `feat feat-NNN-slug`.

1. **Parse the target** `<type> <id>` pair.
2. **State the cost before running:** this is an O(registry-size) scan --
   every candidate document's body must be read, because the
   `list_references` extractor regex-scans every body for the 11-tag
   reference vocabulary (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS/FEAT;
   case-insensitive tag, space/tab/dash separator, anywhere in a line). No
   domain can be pre-filtered by the target's type and no document can be
   skipped; do not "optimize" the scan by dropping domains.
3. **Scan:** for each of the 12 whole-body domains (req/uc/tsk/qa/prb/gol/
   rsk/dec/sop/feat/vcr/sysrs -- the same deliberate `adr` exclusion as the
   batch workflow), page `list_<d>` to completion and, for every scannable
   document (null-id `<failed to parse>` rows are counted as
   `parse_failures`, not scanned), call `list_references(<domain>, id)` and
   page to completion.
4. **Match:** a document is a hit when one of its rows matches the target on
   `(type, id)` -- the target type case-insensitively, and the target id
   exactly -- except that a `feat` target given as the full `feat-NNN-slug`
   also matches a row carrying the target's bare `feat-NNN` number prefix,
   since a feature can be referenced by either spelling and the row's `id`
   stays the spelling as it appeared in the referencing body.
5. **Report** one row per hit, naming the referencing document's
   `type`/`id`/`title`/`path` (from the domain's own `list_<d>` row) plus
   the number of matching reference rows in it. A document with no matching
   row is not a hit and is not listed. If the target document itself is a
   hit (a self-reference), report it like any other hit and mark it as one.

## Reporting conventions (every workflow)

Every report you produce -- including the direct single-document call --
uses the `ref-finder` vocabulary, verbatim:

- One row per reference: `type`, `id`, `title`, `path`.
- A row whose `error` is set (the referenced document was not found on
  disk; its `title`/`path` are null) is prefixed with **NOT FOUND**.
- State the `total` reference count and the `error_count` for every
  `list_references` result you rely on, and `truncated` whenever a result
  page was not consumed to completion.
- Report a tool error (a `ValueError` for a bad `type`/`id`, a domain
  not-found error for a missing source) verbatim and stop -- do not paper
  over it with an empty list.
- Retrieving references never modifies, creates, or deletes any document.
```

**(3) Locked test pin list (Task 100.130)** — `tests/opencode/test_skill_specmgr_refs.py` (Phase 110, Task 110.120) mirrors `tests/opencode/test_skill_feat_numbering.py`: the same AGPL copyright header, the same module constants (`_REPO_ROOT`, `_SKILL_DIR = _REPO_ROOT / ".opencode" / "skills" / "specmgr-refs"`, `_SKILL_PATH = _SKILL_DIR / "SKILL.md"`, `_SKILL_NAME = "specmgr-refs"`), the same `_skill_text`/`_split_frontmatter`/`_parse_frontmatter`/`_normalize_whitespace` helpers verbatim (the single-line frontmatter shape keeps the naive line-based parser working — no yaml dependency), and mandatory type hints plus `result` naming per `.specmgr/conventions.md`. All pins are mechanical (string presence, whitespace-normalized where noted); no semantic assertions:

- `TestSkillFileLocation` (pin a): `.opencode/skills/specmgr-refs/` is a directory and `SKILL.md` is a file inside it.
- `TestSkillFrontmatter` (pin b): the frontmatter has exactly the keys `name`/`description`; `name` equals the containing folder name (`specmgr-refs`), is lowercase, and is at most 64 characters; `description` is non-empty and does not start with a first/second-person subject (`"I "`, `"I'm"`, `"We "`, `"You "`); `description` (lowercased) contains every keyword of the locked trigger tuple (case-insensitive).
- `TestSkillReportingVocabulary` (pin c): every reporting token below occurs in the body as a literal substring (backticks included — the skill's reporting conventions name them backticked).
- `TestSkillDelegationPointer` (pin d): the whitespace-normalized body contains the locked delegation phrase; the body names all three of the existing stack.
- `TestSkillReadOnlyPosture` (pin e): the whitespace-normalized body contains both locked read-only phrases.

```python
_TRIGGER_KEYWORDS: tuple[str, ...] = (
    "specmgr",
    "cross-reference",
    "list_references",
    "what does document X reference",
    "list the references of X",
    "show me the reference graph",
    "do all cross-references resolve",
    "which documents reference X",
)
_REPORTING_TOKENS: tuple[str, ...] = (
    "**NOT FOUND**",
    "`type`",
    "`id`",
    "`title`",
    "`path`",
    "`total`",
    "`error_count`",
    "`truncated`",
)
_DELEGATION_PHRASE = "is a pointer to the existing stack, never a copy of it"
_DELEGATION_NAMES: tuple[str, ...] = ("list_references", "ref-finder", "/refs")
_READONLY_PHRASES: tuple[str, ...] = ("never edit, write, create, or delete", "never commit")
```

**(4) Cross-check against `.opencode/agent/ref-finder.md` (Task 100.120) — outcome: pass.**

- Pointer, not copy (REQ-002/ACC-003): the draft's single-document section names the `ref-finder` subagent, the `/refs` command, and the `list_references` tool as the delegation targets and re-tells none of `ref-finder`'s workflow steps (its input parsing, its call, its page-only-when-asked default, its one-message report) — the only overlap is the shared reporting vocabulary, which REQ-006 mandates. The one deliberate divergence is the compositions' page-to-completion rule, explicitly scoped in the draft so it cannot be read as contradicting `ref-finder`'s interactive default.
- Reporting vocabulary (REQ-006): identical — per-row `type`/`id`/`title`/`path`, the **NOT FOUND** prefix on rows whose `error` is set (their `title`/`path` null), stated `total`/`error_count`, plus `truncated` wherever a page is not consumed.
- Read-only posture (REQ-006): preserved — "you never edit, write, create, or delete any document, and you never commit", tool errors reported verbatim and stopped (not papered over with an empty list), mirroring `ref-finder`'s own notes.

### Related Decisions

- ADR e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts in `.specmgr` with feature-driven work units (this plan folder follows it)
- feat-144-ref-artifact planning decision: opencode-specific surface (command + agent) lives under the project-local `.opencode` tree — this skill adopts the same layering

### Task List

#### Phase 100: Design

- [x] Task 100.100: Lock the skill description wording against reference-retrieval phrasings (trigger match)
- [x] Task 100.110: Draft the router body: single-document delegation + the codified graph, batch, and reverse workflows
- [x] Task 100.120: Cross-check the draft against `ref-finder` conventions (pointer not copy; reporting vocabulary)
- [x] Task 100.130: Draft the consistency-test pin list (location, frontmatter, trigger keywords, reporting vocabulary, delegation pointer)

#### Phase 110: Implementation

- [x] Task 110.100: Create `.opencode/skills/specmgr-refs/SKILL.md`
- [x] Task 110.110: Register the skill in `AGENTS.md` and the root `README.md` `## Referencing Artifacts` section, and record it in `CHANGELOG.md`
- [x] Task 110.120: Create `tests/opencode/test_skill_specmgr_refs.py` per the Task 100.130 pin list

#### Phase 120: Verification

- [x] Task 120.100: Smoke-exercise the single-document, graph, batch, and reverse workflows against live documents
- [x] Task 120.110: Verify the skill loads unprompted in a matching context (description match check)
- [x] Task 120.120: Run the repository quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, doc drift checks)

#### Phase 130: Closeout

- [x] Task 130.100: Update this feature's Progress (check off ACCs, advance status via the generic `set_status`)

## Progress

### Current Status

**As of 2026-10-03**: Phase 130 (Closeout) complete — all four phases of the plan are done. Phase 100 locked the skill design (the description string, the full `SKILL.md` draft, the consistency-test pin list, and the `ref-finder` cross-check with recorded outcome: pass); Phase 110 wrote `.opencode/skills/specmgr-refs/SKILL.md`, landed the three doc registrations (`AGENTS.md`, the root `README.md` `## Referencing Artifacts` section, and `CHANGELOG.md`), and created the nine-test drift-guard `tests/opencode/test_skill_specmgr_refs.py`; Phase 120 smoke-exercised all four workflows live against this repository's registry and re-ran the full quality gate; Phase 130 ticked all five acceptance criteria with inline evidence in `### Acceptance Criteria`, ticked Task 130.100, and advanced the feature's status. All five acceptance criteria are met, and the full repository quality gate is green (Phase 120: `ruff format --check` with 1790 files already formatted, `ruff check`, `vulture` clean, `pytest -n auto` 4025 passed, `specmgr docs` / `specmgr mcp-docs` / `specmgr coverage-badge` all no-drift), re-confirmed by Phase 130's own gate run after its progress-record-only edit. The feature is at status `review`, pending the PR and the post-implementation feat-reviewer pass; the one residual — a fresh opencode session loading the skill unprompted — is flagged for review-time confirmation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T13:01:57.058Z - Phase 130: closeout — ACCs ticked with evidence, status advanced to review

Task 130.100 closed out the feature. All five acceptance criteria are ticked in `### Acceptance Criteria` with inline evidence: ACC-001 (the locked description carries all five example phrasings as case-insensitive substrings, verified in Phase 120's description match check and pinned by the drift-guard test, with the fresh-session unprompted-load residual flagged for review-time confirmation), ACC-002 (the `Route by task shape` table maps each of the four task shapes to exactly one path, and the one deliberate compositions divergence is explicitly scoped in the skill body, per the Phase 100 Task 100.120 cross-check with recorded outcome pass), ACC-003 (the single-document section is a pointer naming the `list_references` tool, the `ref-finder` subagent, and the `/refs` command, re-telling none of `ref-finder`'s workflow narrative), ACC-004 (Phase 120 smoke-exercised all four workflows live against this repository's registry with the recorded totals and error counts, the **NOT FOUND** path proven via a throwaway temp source, and the self-referential dynamic noted), and ACC-005 (the nine-test, five-class drift-guard exists, pins exactly what the ACC lists, and passed in the Phase 110/120 quality-gate `pytest` runs). `### Current Status` is rewritten as the final closeout narrative, Task 130.100 is ticked, and the feature's status advances from `progress` to `review` via the generic `set_status` tool (`type="feat"`) — deliberately not `done`, since the PR and the post-implementation feat-reviewer pass still follow. The one residual for review time is confirming that a fresh opencode session loads the skill unprompted in a matching mid-task context. The sole repository change in this phase is this progress record, and the full quality gate was re-run against it and is green.

#### 2026-10-03T11:57:11.927Z - Phase 120: verification complete — four workflows smoke-exercised live, description match check green, full quality gate green

Implemented Tasks 120.100–120.120 (verification only — no src/ or MCP-registration change; the sole edit is this progress record). (1) Task 120.100 — live smoke of all four workflows exactly as the skill's codified paths prescribe, run as throwaway uv scripts under /tmp/opencode/ against this repository's own registry (default base dirs, cwd = worktree root). Single-document: list_references(type='feat', id='feat-144-ref-artifact') returns total=5, error_count=0, truncated=False, with all five ### Related Decisions ADRs resolving on disk (36905d5b, 1af6787b, bfd76370, ece4554b, ec9f5262) — matching feat-144's own closeout record — and list_references(type='feat', id='feat-152-ref-skill') returns total=1, error_count=0 (adr e369ee2e-3353-4f92-991c-6367d76d832e resolves). NOT FOUND demonstration (feat-144's recorded precedent, "Not-found smoke-test method"): a throwaway copy of feat-144's README at /tmp/opencode/feat152-notfound/feat-0-notfound/README.md (frontmatter id renamed to match the temp folder, plus one extra bullet - ADR 00000000-0000-0000-0000-000000000000: does not exist in ### Related Decisions), with SPECMGR_FEAT_DIR pointed at the temp dir via os.environ before import/call — list_references('feat', 'feat-0-notfound') returns total=6, error_count=1, with exactly one row carrying title=None, path=None, and the ADR not-found message in error (what the skill reports as **NOT FOUND**) while the other five ADR references resolve; the temp dir was removed afterwards (confirmed absent) and the repo gains no fixture. Graph (root feat feat-144-ref-artifact, default N = 2 since the user stated no depth, seen-set dedup, NOT FOUND rows not expanded): level 1 is the five ADRs (total=5, error_count=0); level 2 expands the five resolved level-1 rows with per-source totals 3/3/1/0/2 (aggregate total=9, error_count=0), yielding five new unique rows (33c5ab08, 71fd95d7, ddfb1109, 8cf940c5, 7531106b — all resolved); overall summary: depth reached 2 of 2, 11 unique documents seen (10 excluding the root), 14 total references as the sum of every call's own total, 10 unique reference rows reported across both levels, 0 total errors. Batch (the 12 whole-body domains in canonical order req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs — the deliberate adr exclusion; every `list_<d>` and `list_references` call paged to completion): per-domain (list_total / docs_scanned / parse_failures / total / error_count) — req 14/14/0/18/0, uc 0/0/0/0/0, tsk 4/4/0/1/0, qa 1/1/0/0/0, prb 0/0/0/0/0, gol 2/2/0/1/0, rsk 0/0/0/0/0, dec 0/0/0/0/0, sop 1/1/0/0/0, feat 70/65/5/129/1, vcr 0/0/0/0/0, sysrs 2/1/1/24/0; overall 94/88/6/173/1. The six parse_failures (null-id rows, not scanned — no source id) are feat-132-prb-update, feat-177-list-ref-feat, feat-29-dec-source-roles, feat-5-md-model-parser, and feat-50-confluence (all feat) plus the sysrs appendix document (raw HTML `<domain>` inline at body line 362). The single **NOT FOUND** reference row: req 00000000-0000-4000-8000-000000000001, sourced from feat feat-135-related-artifacts-risks — that uuid is an illustrative placeholder quoted in that plan's own Updates entry (narrating the template-example bullets it wrote), i.e. exactly the accepted feat-144 regex-extraction caveat (a reference-shaped string quoted as a literal example is picked up and reported), so the workflow flagging it is correct behavior, not a defect. Reverse (target adr e369ee2e-3353-4f92-991c-6367d76d832e, cost stated before running per the skill's step 2: an O(registry-size) scan, the 11-tag vocabulary regex-scans every body, no pre-filtering or skipping possible): 88 list_references calls over the 88 scannable documents (the same six parse_failures not scanned), 13 hits each with exactly one matching row — feat feat-4-use-cases, feat-6-requirement-artifact, feat-7-various-improvements, feat-12-qa-artifact, feat-13-list-paging, feat-14-qa-v2-adjacent-qa, feat-31-feature, feat-48-feat-id, feat-150-mcp-lifecycle-commands, feat-152-ref-skill, feat-163-feat-numbering, feat-167-mcp-lifecycle-commands-2, and sysrs 8d752304-b076-4bad-89af-f8032158dd21; feat feat-152-ref-skill is confirmed among the hits (its plan names this ADR in ### Related Decisions); matching is on (type, id) — target type case-insensitively, target id exactly (the bare feat-NNN exception does not apply to an adr target). (2) Task 120.110 — description match check: the nine drift-guard tests of tests/opencode/test_skill_specmgr_refs.py all pass (location; frontmatter exactly name/description with name == specmgr-refs == the containing folder, lowercase, at most 64 characters; non-empty third-person description carrying the eight locked trigger keywords; the nine reporting tokens verbatim in the body; the locked delegation phrase plus all three stack names; both locked read-only phrases), and the discovery prerequisites hold mechanically (the file sits at the plural project-skill path .opencode/skills/specmgr-refs/SKILL.md). Every ACC-001 example phrasing — "which documents reference X", "show me the reference graph", "do all cross-references resolve" — plus both single-document phrasings — "what does document X reference", "list the references of X" — occurs in the description as a case-insensitive substring (verified with the test's own naive frontmatter parser via a throwaway script). The residual is stated honestly: final proof of unprompted loading is a fresh opencode session observing the skill in its system prompt and loading it on a matching task — review-time confirmation (the feat-reviewer pass), not machine-verifiable in this phase. (3) Task 120.120 — full quality gate from the worktree root: uv run --frozen ruff format --check (1790 files already formatted, exit 0); uv run --frozen ruff check (all checks passed, exit 0); uv run --frozen vulture src/ whitelist.py --min-confidence 60 (clean, exit 0); uv run --frozen pytest -n auto --cov=src --cov-report= (4025 passed in 65.38 s, exit 0); and the doc drift checks all no-drift — uv run --frozen specmgr docs followed by git diff --exit-code -- docs/api docs/GENERATED.md clean, uv run --frozen specmgr mcp-docs followed by git diff --exit-code -- docs/MCP.md clean, and uv run --frozen specmgr coverage-badge followed by git diff --exit-code -- docs/coverage.svg clean; git status --short shows only this plan README modified (the throwaway scripts live under /tmp/opencode/ and touch nothing in the repo). No defects found in the skill wording, the test, or the docs; the ACCs are left for the closeout phase (130) to tick with this evidence.

#### 2026-10-03T10:29:57.962Z - Phase 110: implementation landed

Phase 110 (Tasks 110.100–110.120) executed the Phase 100 locked design mechanically: (1) `.opencode/skills/specmgr-refs/SKILL.md` was written byte-for-byte from the Locked-design block (2) draft — frontmatter `name: specmgr-refs` plus the single-line locked `description` (verified to equal the block (1) string exactly) and the router body that delegates single-document retrieval to the `list_references` tool / `ref-finder` subagent / `/refs` command and codifies the graph, batch, and reverse workflows — in the plural `.opencode/skills/` directory per the locked directory choice; (2) all three doc registrations landed at the locked anchors — the `AGENTS.md` `list_references` entry now names the OpenCode-native counterparts (the `ref-finder` subagent `.opencode/agent/ref-finder.md`, the `/refs <type> <id>` command `.opencode/command/refs.md` with `agent: ref-finder`, and the self-triggering `specmgr-refs` OpenCode Skill `.opencode/skills/specmgr-refs/SKILL.md`, feat-152, GitHub issue #152) in one sentence appended after its final line, following the `repair`-skill registration pattern; the root `README.md` `## Referencing Artifacts` section gained one new final paragraph documenting the skill as the agent-initiated surface; and `CHANGELOG.md`'s `[Unreleased]` `### Added` list gained one appended bullet; (3) the drift-guard test `tests/opencode/test_skill_specmgr_refs.py` was created per the Task 100.130 pin list — five classes covering pins a–e (file location, frontmatter, reporting vocabulary, delegation pointer, read-only posture), mirroring `test_skill_feat_numbering.py`'s header, constants, and helpers, all nine tests passing. Quality gate green: `ruff format --check` (1790 files already formatted) and `ruff check` pass, `vulture` is clean, the full suite passes 4025 tests, `specmgr docs` bumped `docs/GENERATED.md`'s test-file count from 380 to 381 with no other `docs/` drift, `specmgr coverage-badge` left `docs/coverage.svg` byte-identical (the new test imports nothing from `src/`), and `specmgr mcp-docs` was a no-op on `docs/MCP.md`. Phase 120 (Verification) is next.

#### 2026-10-03T09:27:33.848Z - Phase 100: design locked

Phase 100 (Tasks 100.100–100.130) locked the skill design in `### Design Notes`'s new `#### Locked design (Phase 100)` block: (1) the verbatim single-line `description` string (its eight-keyword trigger tuple is pinned by the locked test design); (2) the full `SKILL.md` file draft — frontmatter plus a router body with the single-document delegation pointer (no narrative copy of `ref-finder`) and the codified graph, batch, and reverse workflows carrying `ref-finder`'s reporting vocabulary; (3) the mechanical pin list for `tests/opencode/test_skill_specmgr_refs.py` (location, frontmatter, trigger keywords, reporting vocabulary, delegation pointer, read-only posture); (4) the Task 100.120 cross-check against `.opencode/agent/ref-finder.md` — outcome: pass (pointer not copy, identical reporting vocabulary, read-only posture preserved). The `### Decisions Made` entry of the same date records the choices beyond the plan's wording (single-line frontmatter shape; tag-vocabulary count 11, verified against `general/tools/_references.py` — the stale '10-tag' phrasing in the reverse-lookup-cost Design Note is corrected in this same edit; default graph depth N = 2; and the Phase 110 placement anchors in `AGENTS.md`, the root `README.md`, and `CHANGELOG.md`). Phase 110 (Implementation) not started.

#### 2026-10-03T06:30:34.899Z - Plan revised after review pass

Plan review pass (feat-reviewer) findings folded in: REQ-004 records the deliberate `adr` source-domain exclusion (new Out-Of-Scope bullet + Design Note); REQ-007's registration anchors corrected — `AGENTS.md`'s `list_references` entry per the existing `repair`-skill pattern, and the root `README.md` `## Referencing Artifacts` section added to the doc scope (the "alongside `/refs` and `ref-finder` in `AGENTS.md`" premise was inaccurate); ACC-004 trimmed of its trivially-true plan-folder clause; new REQ-008/ACC-005 + Tasks 100.130/110.120 add the drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py` (feat-163 precedent); Design Notes record the directory-choice and reverse-lookup-cost rationale; the Created entry heading re-synced to the frontmatter `created` timestamp.

#### 2026-10-03T05:27:21.033Z - Created

Feature plan created for GitHub issue #152 (agent-initiated specmgr cross-reference retrieval via an opencode skill), routing on the feat-144-ref-artifact stack.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T09:27:33.848Z - Phase 100 locked design decisions

Choices made in Phase 100 that go beyond the plan's existing wording: (1) Frontmatter shape — exactly `name`/`description`, with `description` a single-line plain YAML scalar (no `>-` block): the locked test reuses `test_skill_feat_numbering.py`'s naive line-based `_split_frontmatter`/`_parse_frontmatter` helpers verbatim, each of whose frontmatter lines must be `key: value` — a `>-` continuation line would break that parser; the single-line shape also matches the `feat-numbering` precedent in the winning plural `.opencode/skills/` directory (the `repair` skill's `>-` block lives in the superseded singular `.opencode/skill/` directory), and the locked description carries no `: ` sequence, so the plain scalar is unambiguous YAML. (2) Description string — locked verbatim in `### Design Notes`'s Locked-design block (1); the test pins its eight trigger keywords (the locked `_TRIGGER_KEYWORDS` tuple), not the full string, so the wording may be refined without breaking the trigger as long as the keywords survive. (3) Tag-vocabulary count — 11 tags (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS/FEAT), verified against `general/tools/_references.py`'s `REFERENCE_TYPES` (the 10 UUID tags plus `feat`, added by feat-177); the reverse-lookup-cost Design Note's stale '10-tag' phrasing is corrected in the same edit. (4) Placement anchors for Phase 110 — `AGENTS.md`: extend the `general/tools/` bullet's `list_references` entry immediately after its final sentence (the one ending 'identical to `get_<d>`.'), following the `repair` skill's own registration pattern (naming the OpenCode-native counterparts in one sentence), naming the `ref-finder` subagent (`.opencode/agent/ref-finder.md`), the `/refs <type> <id>` command (`.opencode/command/refs.md`, `agent: ref-finder`), and the `specmgr-refs` OpenCode skill (`.opencode/skills/specmgr-refs/SKILL.md`, feat-152) that routes single-document requests to `list_references` and codifies the graph/batch/reverse workflows; root `README.md`: a new final paragraph in the `## Referencing Artifacts` section (after the `/refs` paragraph, before `## Development`); `CHANGELOG.md`: a bullet appended to `[Unreleased]`'s `### Added`. (5) Default graph depth — N = 2 when the user states no depth, stated in the report. (6) Batch/reverse handling of `<failed to parse>` rows — their null `id` makes them unscannable by `list_references` (which needs a source id), so they are tallied in a separate per-domain `parse_failures` count with the row's `path`/`error`, not reported as reference rows. (7) Reverse-workflow `feat` matching — a target given as the full `feat-NNN-slug` also matches rows carrying the bare `feat-NNN` number prefix (a feature is referenceable by either spelling; the row's `id` stays the spelling as it appeared in the referencing body).

### Related PRs / Commits

- GitHub issue #152 — https://github.com/dfch/biz.dfch.SpecMgr/issues/152 (the feature request this plan tracks)
