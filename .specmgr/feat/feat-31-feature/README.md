---
created: 2026-08-30
id: feat-31-feature
status: in-progress
updated: 2026-08-30
version: 1.6.0
---

# Feature: Formalize the Feature artifact type ("feat")

## Plan

### Overview

Formalize the ad hoc `.specmgr/feat/<id>/README.md` convention (ADR
e369ee2e-3353-4f92-991c-6367d76d832e) into a real, schema-backed `feat`
document-type domain — the same kind of markdown-frontmatter, Pydantic-modeled,
MCP-tool-addressable artifact every other document type in this repo already
is. `feat` is deliberately special among domains: it formalizes a convention
that has already been used, by hand, 17+ times before this feature existed,
and its addressing scheme (`id` = a chosen `feat-NNN-slug`, not a
server-generated UUID; one folder per document holding a fixed `README.md`
filename, not a flat file directly under the base directory) is a genuine,
intentional deviation from every other domain's `8cf940c5` precedent. `feat`
follows the domain-first hierarchy (ADR
ece4554b-725c-4f76-bc04-5d2b760363d2) and is built on the generic `models/md`
parsing engine with the simple surface used by GOL/RSK/DEC/(planned)SOP — no
fine-grained mutation tools, no renderer (writes persist the caller's raw
validated body byte-for-byte) — and is the second domain (after the
still-unimplemented `feat-30-sop`) planned to use the post-feat-22 generic
`update`/`set_status` dispatch tools from day one (ADR
36905d5b-8057-4294-8665-c7eed5534db0): there is no `update_feat`/
`set_status_feat` tool of its own.

Implementation happens on a dedicated branch `feat-31-feature`, created off
`dev` before Phase 0 starts (this branch), mirroring every prior "add
artifact type" feature's own branch-per-feature convention (e.g.
`feat-21-decision`, `feat-15-add-artifact-type-risk`).

### Requirements

- REQ-001: Define the `feat` markdown schema — frontmatter (`type="feat"`,
  closed 4-value status set `planning`/`progress`/`review`/`done` with no
  hyphens in any value, default `planning`) and body (H1 `# Feature: {title}`,
  `## Plan` composite with mandatory leaf `### Overview`; mandatory
  regex-validated `### Requirements`/`### Acceptance Criteria` lists (≥1 item
  each, `REQ-\d{3}: ...`/`- [ ] ACC-\d{3}: ...`); mandatory composite
  `### Scope` (mandatory `#### Included`/`#### Explicitly Out Of Scope`
  leaves); optional composite `### Dependencies` (optional
  `#### Depends On`/`#### Blocks` leaves); optional leaf `### Design Notes`/
  `### Related Decisions`; mandatory composite `### Task List` (no own text, only
  `#### Phase N: ...` entries, ≥1, each a regex-validated heading holding its
  own `- [ ] .../- [x] ...` checklist, ≥1 item); `## Progress` composite
  with mandatory leaf `### Current Status`, optional leaf `### Blockers`,
  mandatory composite `### Updates` (optional leading comment,
  ISO8601-timestamped `#### {timestamp} — {title}` entries, ≥1,
  newest-first order enforced), optional composite `### Decisions Made`
  (same shape as `### Updates` — optional leading comment, ISO8601
  timestamps, newest-first order enforced), optional leaf
  `### Related PRs / Commits`, optional leaf `### More Information`).
- REQ-002: Pydantic models under `feat/models/v1/` (frontmatter, body,
  document, parser, summary, `_util.py` with `SCHEMA_COMMENT_VERSION = "v1"`),
  domain-first, mirroring `dec`/`gol`'s exact file shapes. `Updates`/
  `UpdateEntry` copies `feat-30-sop`'s planned ISO8601-enforced shape one
  heading level deeper (`### Updates`/`#### {timestamp} — {title}` instead of
  SOP's `## Updates`/`### {timestamp} — {title}`) — see Design Notes for the
  exact regex. No `models/md` engine changes needed: `MarkdownSection1`
  through `MarkdownSection6` already exist, so the H3→H4 dynamic-list pattern
  is the same generic mechanism TSK's/DEC's H2→H3 `Updates`/`UpdateEntry`
  already exercises, just one level deeper.
- REQ-003: Parse/validate `feat` documents from markdown, mirroring
  `parse_dec`/`parse_gol`'s two-error-channel convention (`AssertionError` for
  structural problems, `pydantic.ValidationError` for field-level problems).
  Additionally: the invariant "frontmatter `id` equals the containing
  folder's name" is enforced at the **tool** layer (`feat/tools/_paths.py`/
  `_io.py`), not the model layer — the model-layer `parse_feat(text: str)`
  has no path/folder-name to check against, matching every other domain's
  pure-text model-layer parser signature.
- REQ-004: Bespoke, folder-per-document addressing (`feat/tools/_paths.py`,
  hand-rolled like ADR's own `adr/tools/_paths.py`, **not** the shared
  flat-file `general/tools/_doc_paths.py`): base directory `.specmgr/feat`,
  documents at `<base>/<id>/README.md`. **`SPECMGR_FEAT_DIR` (mandatory,
  not optional)** overrides the base directory — this is not a `feat`-only
  nicety: every existing domain has an equivalent env var
  (`SPECMGR_ADR_DIR` in `adr/tools/_paths.py`; the shared `SPECMGR_DOCS_DIR`
  in `general/tools/_doc_paths.py`, used by `req`/`uc`/`tsk`/`qa`/`prb`/
  `gol`/`rsk`/`dec`), specifically so tests never read/write the real
  base directory (for `feat`, that would mean the real `.specmgr/feat/`
  — the very folder this plan file itself lives in). Omitting it would
  make `feat` the only domain in the codebase without test isolation for
  its base directory. Since `id` is the folder name by convention,
  `find_feat_path_by_id` shortcuts straight to `<base>/<id>/README.md` and
  verifies the frontmatter `id` matches (raising `FeatNotFoundError`
  otherwise) instead of a full directory scan. `create_feat` derives the next
  `NNN` by scanning existing `feat-*` folder names under a **global**
  create-lock (distinct from every other domain's per-id lock, since the id
  doesn't exist yet when the lock must be taken). No partial-id-match
  support (e.g. resolving a bare `"feat-31"` to `"feat-31-feature"`) —
  considered and rejected, see Decisions Made.
- REQ-005: 8 MCP tools, sop-style generic dispatch (**no**
  `update_feat`/`set_status_feat` — see Overview): `create_feat`,
  `parse_feat`, `list_feat` (paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13), `get_feat(id, raw=False)`,
  `get_feat_example`, `get_feat_template`, `delete_feat` (stub),
  `validate_feat` — plus private `_paths`/`_io`/`_lock`/`_write` helpers per
  REQ-004.
- REQ-006: Add `"feat"` to the generic cross-domain mutation tools —
  `_update_feat`/`_set_status_feat` adapters and `type="feat"` dispatch table
  entries in `general/tools/update.py`/`set_status.py`, built on REQ-004's
  bespoke `_paths`/`_io`/`_lock`/`_write` (same shape as the eight existing
  adapters, just resolving paths differently).
- REQ-007: MCP resources: `specmgr://feat/schema`, `/example`, `/template`
  (no `/list` — REQ-005 covers listing as a tool; no `/{id}` — id-based reads
  are `get_feat`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-008: MCP prompts `create_feat(topic)`/`update_feat(id, instructions=None)` — narrated instruction flows reusing the
  dedup-check-first pattern (`list_feat`) and the `TodoWrite`/`question`-tool
  narration pattern from `gol`/`dec`/`prb`'s prompts; both read their own
  packaged instructions data file (`feat/data/feat_create_instructions.md`/
  `feat_update_instructions.md`), not an inline string.
- REQ-009: `generate_feat_schema()` + `_GENERATORS["feat"]` in
  `commands/schema.py`; packaged `feat/data/feat_schema.json`.
- REQ-010: Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `AGENTS.md`, root `README.md`, regenerated
  docs) and a new backlog task in `feat-7-various-improvements` (Task 0.31)
  tracking the future migration of the 17 pre-existing feature folders into
  this schema — added as part of this feature's own scope, the migration
  itself is explicitly out of scope (see Scope).
- REQ-011: Full test coverage mirroring `tests/dec/`'s layout and depth.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001/002 — schema documented
  (`docs/feat_schema.json`, `specmgr://feat/schema`); a reference
  `feat_reference.md` exercising every field (all mandatory + optional
  sections present, ≥2 `### Updates` entries in newest-first order, ≥2
  `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`
  entries each with ≥1 task item) round-trips through `parse_feat`
  byte-exact; `FeatFrontmatter.status` rejects any value outside the
  4-set; malformed `#### {timestamp} — {title}` headings (both `Updates`
  and `Decisions Made` — identical format) and `#### Phase N: ...`
  (`Task List`) headings all raise `AssertionError`; an out-of-order
  (not newest-first) entry in either `Updates` or `Decisions Made` raises
  `AssertionError`; a malformed `REQ-\d{3}: ...`/`- [ ] ACC-\d{3}: ...`
  list item raises `AssertionError`.
- [ ] ACC-002: Verifies REQ-003/004 — a document whose frontmatter `id`
  doesn't match its containing folder's name is rejected by the tool layer
  (not the model layer); `find_feat_path_by_id` resolves via the direct
  `<base>/<id>/README.md` shortcut, not a directory scan; `create_feat`
  correctly derives the next `NNN` under concurrent-create simulation (global
  lock prevents two callers from picking the same `NNN`).
- [ ] ACC-003: Verifies REQ-005 — every listed tool is implemented,
  registered, and callable; a create→get→list→delete(stub)→validate
  round-trip against a temp `SPECMGR_FEAT_DIR` succeeds; `list_feat` returns
  `PagedResult[FeatSummary]` with default page size 25 / cap 100.
- [ ] ACC-004: Verifies REQ-006 — `update(type="feat", ...)` and
  `set_status(type="feat", ...)` both work end to end (whole-body, line-range,
  and status-change modes), preserving `id`/`type`/`created`/`version` and
  bumping only `updated`/`status` as appropriate.
- [ ] ACC-005: Verifies REQ-007 — every listed resource is implemented and
  registered (no `/{id}`, no `/list`).
- [ ] ACC-006: Verifies REQ-008 — both prompts narrate the full
  dedup-check → `TodoWrite` → `question`-tool → tool-call-sequence flow,
  verified by walking both packaged instruction files end to end against a
  real document, not just asserting their static text.
- [ ] ACC-007: Verifies REQ-009 — `specmgr schema --type feat` and the
  generic `specmgr schema` both produce an identical, packaged-copy-matching
  `feat_schema.json`.
- [ ] ACC-008: Verifies REQ-010 — `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` all report zero drift after implementation; `AGENTS.md`
  reflects the new domain; `feat-7-various-improvements` carries the new
  Task 0.31 and Task 0.30's background note is extended to mention `feat` as
  a fourth divergent `Updates`/`Recent Updates` shape.
- [ ] ACC-009: Verifies REQ-011 — full unittest suite green; ruff
  format/check and vulture clean; `specmgr unused-code` clean.

### Scope

Included:

- `feat/` domain package (models, tools, resources, prompts, data) built on
  the existing `models/md` engine, with its own bespoke folder-per-document
  addressing (`feat/tools/_paths.py` et al. — not the shared
  `general/tools/_doc_paths.py`).
- The frontmatter + body schema in Design Notes below.
- Generic `update`/`set_status` dispatch additions (`type="feat"`), no
  per-domain `update_feat`/`set_status_feat`.
- Cross-cutting registration (server.py, schema command, pyproject,
  pre-commit, CI, AGENTS.md, root README.md, generated docs).
- One new backlog task in `feat-7-various-improvements` (Task 0.31) tracking
  the future migration of existing feature folders.
- Tests mirroring `tests/dec/`'s layout.

Explicitly out of scope:

- **Migrating the 17 existing `.specmgr/feat/*/README.md` files** into the
  new schema (no `type: feat` field, `feat-8`'s `status: completed` left
  as-is). They remain readable as plain markdown but unparseable by
  `parse_feat`/`get_feat` (silently skipped by `list_feat`, matching this
  codebase's universal skip-on-parse-failure convention) until the new
  `feat-7` Task 0.31 does this later. This is a deliberate, user-directed
  decision, not an oversight.
- **Consolidating `Updates`/`Recent Updates` naming/shape across domains**
  (TSK's free-form `## Recent Updates`, DEC's unenforced `## Updates`,
  (planned) SOP's ISO8601-enforced `## Updates`, and now `feat`'s
  ISO8601-enforced `### Updates` one level deeper) — tracked entirely by the
  existing `feat-7-various-improvements` Task 0.30, whose background note
  this feature extends to mention `feat` as a fourth variant. No new task,
  no consolidation performed here.
- Structured modeling of the free-form metadata *inside* each Task List
  checklist item (`depends on:`/`status:`/`ETA` annotations) — `#### Phase N`
  headings and their flat `- [ ] .../- [x] ...` item lists are now
  structurally modeled (see Design Notes), but each item's own text stays an
  unparsed `TaskItem` description; per-task metadata edits are still expected
  to go through the generic `update` tool's line-range mode, not a dedicated
  tool. (Supersedes the earlier "Task List stays a single opaque leaf"
  decision — see Decisions Made.)
- ADR-style granular `update_section`/option-style per-field mutation tools —
  `feat` uses only the generic whole-body/line-range `update` tool.
- Real implementation of `delete_feat` — a stub raising
  `NotImplementedError`, matching every other domain's `delete_*` stub.
- Any changes to the `models/md` engine itself (already supports every shape
  needed — `MarkdownSection1`..`6` all exist; if this turns out wrong during
  implementation, stop and report rather than patching the engine).
- Any changes to any other existing (or planned-but-unimplemented, i.e. sop)
  domain's schema, tools, or data.

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (the governing
  `.specmgr/feat/` convention this feature formalizes), ADR
  ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), ADR
  bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic `MarkdownFrontmatter` base),
  ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
  resource), ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic
  `update`/`set_status` dispatch — `feat` must use these from day one), the
  existing `models/md` engine (feat-5, done) and
  `general/tools/_packaged_data.py`/`_paging.py`/`_splice.py` infrastructure.
  The `### Updates`/`UpdateEntry` ISO8601 shape is copied from
  `feat-30-sop`'s **plan** (not its code — `sop` is not yet implemented, this
  feature independently implements its own copy one heading level deeper).
  ADR 8cf940c5-3100-485c-a12d-14b59b631712 (UUID/flat-file addressing) is
  cited as the precedent this feature *deviates from*, not one it follows.
- Blocks: `feat-7-various-improvements` Task 0.31 (existing-folder
  migration), which cannot start until this feature ships.

### Design Notes

**Document structure** (section order is binding — field declaration order =
markdown order):

```markdown
---
id: feat-NNN-slug       # = containing folder's name; NOT a generated UUID
type: feat               # Literal["feat"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: planning         # closed 4-set, no hyphens
version: 1.0.0
---

# Feature: {Free-form title}                  H1, @alias REGEX "^Feature: .+$"
## Plan                                        REQUIRED (LITERAL alias, composite)
  ### Overview                                 REQUIRED (leaf)
  ### Requirements                             REQUIRED (regex list, ≥1 item)
    - REQ-NNN: {text}                          item @regex "^REQ-\d{3}: .+$"
  ### Acceptance Criteria                      REQUIRED (regex checklist, ≥1 item)
    - [ ] ACC-NNN: {text}                       item description @regex "^ACC-\d{3}: .+$"
  ### Scope                                    REQUIRED (composite, no own text)
    #### Included                               REQUIRED (leaf)
    #### Explicitly Out Of Scope                REQUIRED (leaf)
  ### Dependencies                             OPTIONAL (composite, no own text)
    #### Depends On                             OPTIONAL (leaf)
    #### Blocks                                 OPTIONAL (leaf)
  ### Design Notes                             OPTIONAL (leaf)
  ### Related Decisions                        OPTIONAL (leaf)
  ### Task List                                REQUIRED (composite, no own text)
    #### Phase N: {title}                      ≥1, @regex "^Phase \d+: .+$"
    - [ ] Task N.M: {text}                      ≥1 item per phase, opaque TaskItem
## Progress                                    REQUIRED (LITERAL alias, composite)
  ### Current Status                           REQUIRED (leaf)
  ### Blockers                                 OPTIONAL (leaf)
  ### Updates                                  REQUIRED (composite, opt. comment, ISO8601, newest-first enforced)
    <!-- optional comment, e.g. ordering hint -->
    #### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}   ≥1, newest entry first
    {entry prose}
  ### Decisions Made                           OPTIONAL (composite, opt. comment, ISO8601, newest-first enforced)
    <!-- optional comment, e.g. ordering hint -->
    #### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}   ≥1 (if section present), newest entry first
    {entry prose}
  ### Related PRs / Commits                    OPTIONAL (leaf)
  ### More Information                         OPTIONAL (leaf)
```

**Model classes** (all in `feat/models/v1/body.py`, one
`MarkdownSection1`/`MarkdownSection2`/`MarkdownSection3`/`MarkdownSection4`
subclass per heading; implicit SPACE_SEPARATED aliases unless noted):

- `Feature(MarkdownSection1)` — `@alias(value="^Feature: .+$", type=AliasType.REGEX)`; fields in order: `plan`, `progress`.
- `Plan(MarkdownSection2)` — implicit alias "Plan"; fields in order:
  `overview`, `requirements`, `acceptance_criteria`, `scope`,
  `dependencies | None`, `design_notes | None`, `related_decisions | None`,
  `task_list`.
- `Overview`, `DesignNotes`, `RelatedDecisions` — bare opaque leaves
  (`MarkdownSection3`), implicit SPACE_SEPARATED aliases (RSK's
  `Cause`/`Trigger`/GOL's `Description` precedent).
  `space_separated_name("RelatedDecisions")` derives exactly `"Related Decisions"`, so no `LITERAL` override is needed here (unlike the
  `RelatedAdrs`/`"Related ADRs"` name this replaces, which *did* need
  one — see Decisions Made). Renamed from "Related ADRs" to "Related
  Decisions" per explicit user direction: this codebase intends to phase
  out ADR terminology in favor of `dec` over time, so `feat`'s own new
  schema adopts the forward-looking name rather than perpetuating "ADR"
  in a brand-new document type; entries may still reference either an
  ADR id or a `dec` id (or any other decision record) — the field stays a
  free-form cross-reference list, not restricted to one domain's id
  format.
- `RequirementItem(MarkdownListItem)` — `TaskItem`-style: no declared nested
  fields (leaf), a `@computed_field description: str` re-matching
  `^REQ-\d{3}: (?P<description>.+)$` against `.text` and raising
  `AssertionError` on a malformed item (mirrors `tsk`'s own `TaskItem`
  regex-on-`.text` pattern, just without a checkbox marker).
  `Requirements(MarkdownSection3)` — implicit alias "Requirements";
  `items: list[RequirementItem] = Field(min_length=1)`.
- `AcceptanceCriterionItem(TaskItem)` — reuses `tsk.TaskItem`'s
  `checked`/`description`-from-checkbox split as-is, adding one more
  computed field, `criterion_description: str`, that re-matches
  `^ACC-\d{3}: (?P<description>.+)$` against the inherited `description`
  and raises `AssertionError` on a malformed item.
  `AcceptanceCriteria(MarkdownSection3)` — implicit alias "Acceptance
  Criteria"; `items: list[AcceptanceCriterionItem] = Field(min_length=1)`.
- `Included`, `ExplicitlyOutOfScope` — bare opaque leaves
  (`MarkdownSection4`), implicit SPACE_SEPARATED aliases.
  `space_separated_name("ExplicitlyOutOfScope")` derives exactly
  `"Explicitly Out Of Scope"` — every word capitalized ("Start Case"),
  matching this codebase's own existing multi-word heading style
  ("Acceptance Criteria", "Design Notes"), so no `LITERAL` override is
  needed (the earlier `"Explicitly out of scope"` sentence-case spelling
  — this plan's own pre-existing ad hoc `### Scope` convention — is
  dropped in favor of this, per explicit user direction to minimize
  `LITERAL` use where it doesn't change the meaning). `Scope (MarkdownSection3)` — implicit alias "Scope", no own text; fields in
  order: `included`, `explicitly_out_of_scope` (both mandatory — a
  feature must always state both what is included and what is explicitly
  excluded).
- `Blocks`, `DependsOn` — bare opaque leaves (`MarkdownSection4`),
  implicit SPACE_SEPARATED aliases. `space_separated_name("DependsOn")`
  derives exactly `"Depends On"` (capitalized "On"), so no `LITERAL`
  override is needed (the earlier `"Depends on"` sentence-case spelling
  is dropped in favor of this, same rationale as `ExplicitlyOutOfScope`
  above; reusing the parent's own name, `"Dependencies"`, for this child
  heading was considered and rejected — it would read as a confusing
  tautology, `### Dependencies` containing `#### Dependencies`, and the
  Python field would awkwardly become `Dependencies.dependencies`).
  `Dependencies(MarkdownSection3)` — implicit alias "Dependencies", no
  own text; fields in order: `depends_on | None`, `blocks | None` (both
  optional — a feature may have no dependencies and block nothing else,
  matching `Dependencies` itself already being optional overall).
- `Phase(MarkdownSection4)` — `@alias(value=r"^Phase \d+: .+$", type=AliasType.REGEX)` (unpadded phase numbers, matching this very plan's
  own "Phase 0".."Phase 5" headings); computed fields `number: int`/
  `title: str` extracted from the heading via `^Phase (?P<number>\d+): (?P<title>.+)$` (`UpdateEntry` precedent); `items: list[TaskItem] = Field(min_length=1)` reusing `tsk.models.v1.task_item.TaskItem` as-is for
  each phase's own flat `- [ ] .../- [x] ...` checklist — per-item metadata
  (`depends on:`/`status:`/`ETA`) stays unparsed free text inside each
  item's description (see Scope). `TaskList(MarkdownSection3)` — implicit
  alias "Task List", no own text; `phases: list[Phase] = Field(min_length=1)`.
- `Progress(MarkdownSection2)` — implicit alias "Progress"; fields in order:
  `current_status`, `blockers | None`, `updates`, `decisions_made | None`,
  `related_prs_commits | None`, `more_information | None`.
- `CurrentStatus`, `Blockers`, `RelatedPrsCommits`, `MoreInformation` — bare
  opaque leaves (`MarkdownSection3`), implicit SPACE_SEPARATED aliases
  (`RelatedPrsCommits` → "Related PRs / Commits" needs an explicit
  `@alias(value="Related PRs / Commits", type=AliasType.LITERAL)` — the
  slash/mixed-case breaks the plain SPACE_SEPARATED convention, same
  reasoning as SOP's `SafetyAndPrecautions`; `MoreInformation` mirrors
  `req`'s/ADR's own `## More Information`, one heading level deeper).
- `UpdateEntry(MarkdownSection4)` — `@alias(value=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$", type=AliasType.REGEX)`; `content: MarkdownParagraph` (mandatory lead
  paragraph, TSK/DEC shape); computed fields `timestamp: str`/`title: str`
  extracted from the heading via `^(?P<timestamp>...) — (?P<title>.+)$`
  (DEC `Option`/SOP `Step`/`UpdateEntry` precedent). Format: ISO8601 date +
  space + time + milliseconds + explicit UTC offset (`+02:00`, `-05:00`) or
  `Z` for UTC — deliberately **not** the same format as frontmatter
  `created`/`updated` (plain `YYYY-MM-DD`), matching `feat-30-sop`'s own
  stated rationale (this format is scoped to `### Updates` entry headings
  only, hand/LLM-authored body content, not tool-generated frontmatter).
  Malformed headings raise `AssertionError`.
- `DecisionEntry(MarkdownSection4)` — identical shape to `UpdateEntry`
  (same alias regex, same `timestamp`/`title` computed-field extraction,
  same `content: MarkdownParagraph`) — full ISO8601 timestamp, not
  date-only, so same-day entries stay strictly orderable (see the
  ordering validator below).
- `Updates(MarkdownSection3WithComment)` — implicit alias "Updates";
  inherits an optional `comment: MarkdownComment | None` field (`req`'s
  `Level`/`Priority` precedent) meant to hold a machine-readable ordering
  hint (`feat_template.md`/`feat_example.md` populate it with e.g.
  `<!-- Newest entry first -- prepend new entries directly below this comment. -->`); `updates: list[UpdateEntry] = Field(min_length=1)`. One
  heading level deeper than `feat-30-sop`'s planned `## Updates`
  (`MarkdownSection2`), otherwise identical shape.
- `DecisionsMade(MarkdownSection3WithComment)` — implicit alias "Decisions
  Made", same optional `comment` field as `Updates`; `decisions: list[DecisionEntry] = Field(min_length=1)`, same "non-`Optional`
  `list[X]` implies ≥1 once the section exists" convention as
  `Updates.updates`/`TaskList.phases` (`RecentUpdates` precedent).
  Optionality lives one level up instead: `Progress.decisions_made: DecisionsMade | None = None` — a brand-new feature has no `### Decisions Made` section at all, rather than an empty one.
- **Newest-first ordering, enforced, on both `Updates` and
  `DecisionsMade`**: a `@model_validator(mode="after")` on each class
  asserts consecutive entries' parsed `datetime.fromisoformat(entry. timestamp)` values are non-increasing (each entry's timestamp \<= the
  previous entry's), raising `AssertionError` on the first out-of-order
  pair — extending the existing eager-computed-field-validation pattern
  (`tsk.models.v1.body.Task._validate_items_eagerly`) to a genuine
  cross-item ordering guarantee, not just a documented convention.
  Newest-first (not oldest-first/append) was chosen to match the
  *existing*, already-tool-supported convention for the ad hoc
  `### Recent Updates` this feature formalizes:
  `general/data/general_compact_history_instructions.md` (the
  `compact_history` prompt) already assumes/states "newest first" for
  that section, and prepending new entries at the top keeps the
  always-cut-from-the-bottom rotation-into-`history.md` rule simple.
  (`tsk_example.md`'s own shipped example already happens to be
  newest-first; `dec_example.md`'s is oldest-first — that pre-existing
  cross-domain inconsistency is out of scope here, tracked by
  `feat-7-various-improvements` Task 0.30; `feat`'s own two sections
  define and enforce their own explicit convention instead of inheriting
  the ambiguity.)

**Frontmatter**: `FeatFrontmatter(MarkdownFrontmatter)` — `type: Literal["feat"] = "feat"`; closed status set `frozenset({"planning", "progress", "review", "done"})` (GOL/SOP error-message pattern), default
`"planning"` (overriding the base's `"draft"` default). No hyphens in any
value, per explicit user direction (`"progress"`, not `"in-progress"`).
`version` means schema version only (`CURRENT_SCHEMA_VERSION`,
machine-managed) — the historical hand-bumped "plan revision" meaning
(`feat-4-use-cases` reaching `1.7.0`, `feat-5-md-model-parser` reaching
`1.16.4` by hand) is retired for documents created under this schema;
revision history is tracked via `created`/`updated` plus git history
instead, per user direction. `created`/`updated` stay plain `YYYY-MM-DD`
(not the other domains' microsecond `T`-separator timestamp) — matching
every one of the 17 existing feature files and ADR e369ee2e's own template,
a deliberate divergence from the rest of the codebase's frontmatter
timestamp convention.

**Addressing** (the genuinely novel part — see REQ-004):

- `feat/tools/_paths.py` is hand-rolled (ADR-style), not built on
  `general/tools/_doc_paths.py`: `feat_base_dir()` reads `SPECMGR_FEAT_DIR`,
  falling back to `.specmgr/feat`; `iter_feat_paths()` globs
  `<base>/*/README.md`; `find_feat_path_by_id(base_dir, id_)` shortcuts to
  `<base>/<id_>/README.md` and verifies the parsed frontmatter `id` matches
  (raising `FeatNotFoundError` with a clear message otherwise — no fallback
  full-directory scan, since a mismatch means the folder was renamed/copied
  incorrectly and should be surfaced, not silently worked around).
- `create_feat(content)`: derives the next `NNN` by scanning `feat-*`
  folder names under `feat_base_dir()`, taking the max existing `NNN` + 1
  (or `1` if none exist) under a **global** `feat_create_lock()` (a single
  lock file at `<base>/.create.lock`, distinct from every other domain's
  per-id lock, since the id doesn't exist until the scan completes);
  slugifies the H1 title (reusing `general/tools/_doc_paths.py::slugify`)
  for the folder-name suffix; creates `<base>/feat-<NNN>-<slug>/` and writes
  `README.md` inside it.
- `list_feat`/`get_feat`/`update`/`set_status` (dispatched via
  `type="feat"`) all reuse this same `_paths.py`, plus feat-specific
  `_io.py`/`_lock.py` (per-id lock keyed on the full `id`, e.g. a lock file
  at `<base>/<id>/.lock`) /`_write.py` mirroring the shape (not the
  implementation) of `dec`'s/`gol`'s equivalents.
- No partial-id-match support in `find_feat_path_by_id` — e.g. a bare
  `"feat-31"` does **not** resolve to `"feat-31-feature"`. Considered and
  explicitly rejected (see Decisions Made): an agent that only has a bare
  `"feat-31"` can already resolve the real id for free by calling
  `list_feat` (whose `FeatSummary` entries carry the real `id`) and
  matching the prefix itself, then calling `get_feat` with the resolved
  id — the same "list, then resolve, then act" pattern already used
  elsewhere in this codebase (e.g. `create_dec`/`create_gol`'s own
  dedup-check-first prompts), rather than adding boundary-matching regex,
  a new ambiguous-match error type, and a scan fallback to
  `find_feat_path_by_id` for a need the existing tools already cover.
- `FeatSummary(DocSummary)` adds one extra field beyond the inherited
  `id`/`title`/`status`/`ref`: **`path: str`**, the real filesystem path
  to the document's `README.md` (e.g.
  `.specmgr/feat/feat-31-feature/README.md`; the containing folder is
  trivially `Path(path).parent` for a caller that wants to look at
  sibling files). This is a deliberate divergence from every other
  domain's summary: `DocSummary.ref`'s own docstring states callers "must
  not read this off disk themselves, only pass it to the matching
  domain's `get_<domain>` tool" — `AdrSummary` enforces the identical
  policy, backed by ADR "author and edit ADRs only through MCP structured
  tools, never raw markdown." `feat` is the opposite case: ADR
  e369ee2e's whole governing convention *is* direct hand/agent markdown
  editing of `.specmgr/feat/<id>/README.md`, which remains normal and
  sanctioned even after `feat`'s own MCP tools exist — so hiding the path
  behind `ref` alone would work against the domain's own intended
  workflow. `id`/`ref` stay on `FeatSummary` too (still useful for
  `get_feat`/`update`/`set_status` lookups) — `path` is additive, not a
  replacement.

**Prompts are narrated instructions only** (return a string, auto-wrapped as
a `UserMessage`), same contract as every existing prompt — `create_feat`/
`update_feat` never call `TodoWrite`/`question`/`get_feat`/`create_feat`/
`update`/`set_status` themselves, they only narrate that the calling LLM
should, mirroring `gol`/`dec`/`prb`'s prompts.

**Cross-cutting wiring**: `server.py` (add `feat` to the domain import
line + docstring), `commands/schema.py` (`generate_feat_schema()` +
`_GENERATORS["feat"]`), `pyproject.toml` (package-data entry for
`biz.dfch.specmgr.feat`), `.pre-commit-config.yaml` (`feat/models/v1` added
to the schema-hook globs + new `specmgr-schema-feat-package` hook),
`.github/workflows/ci.yml` (new packaged-copy drift step), `AGENTS.md` (new
`feat/` bullet documenting the addressing deviation explicitly), root
`README.md` (add `Feature (FEAT)` — or omit if this is judged an
internal/meta artifact type rather than a specification artifact; decide
during Phase 5), `general/tools/update.py`/`set_status.py` (`_update_feat`/
`_set_status_feat` adapters + `"feat"` dispatch entries, per REQ-006).

**Backlog housekeeping** (part of REQ-010, done in Phase 0, not deferred):
add Task 0.31 to `feat-7-various-improvements` (migrate the 17 existing
feature folders once this schema exists) and extend that feature's existing
Task 0.30 background note (Updates/Recent Updates consolidation) to mention
`feat`'s new ISO8601-enforced `### Updates` shape as a fourth divergent
variant.

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
  `.specmgr` with feature-driven work units — the convention this feature
  formalizes into a real schema.
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy).
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types.
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
  (`get_feat`), not a resource.
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
  MCP tool (`list_feat`), not a resource.
- 36905d5b-8057-4294-8665-c7eed5534db0: Consolidate whole-body update and
  status-change tools into generic type-dispatched tools — `feat` uses these
  from day one, no `update_feat`/`set_status_feat` of its own.
- 8cf940c5-3100-485c-a12d-14b59b631712: id/filename/addressing scheme —
  cited as the precedent this feature *deviates from* (non-UUID id,
  folder-per-document, fixed filename), not one it follows.

No new ADR is anticipated for the schema/tooling decisions themselves (each
follows an existing ADR's precedent or is scoped to this file's own
Decisions Made log), **except possibly** for the addressing deviation
(REQ-004) if, during implementation, it turns out to have implications
beyond this one domain — flagged here, decided in Phase 1/2 if it comes up.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate). Each phase ends with a mandatory
phase-end task (tests, full quality gate, README Progress update, one
commit), mirroring `feat-21-decision`'s/`feat-30-sop`'s per-phase commit
discipline.

#### Phase 0: Scaffolding

- [x] Task 0.1: File GitHub issue #31, create branch `feat-31-feature` off
  `dev`, write this plan file — depends on: none — status: completed
  (2026-08-30)
- [x] Task 0.2: Package skeleton — `feat/__init__.py` (`from . import prompts, resources, tools` + registration docstring), empty
  `feat/models/v1/`, `feat/tools/`, `feat/resources/`, `feat/prompts/`
  packages, and `tests/feat/` skeleton mirroring `tests/dec/` — depends on:
  Task 0.1 — status: completed (2026-08-30). `feat/data/` deferred to
  Phase 3, which is the first phase that writes anything into it.
- [x] Task 0.3: Add Task 0.31 to `feat-7-various-improvements` (migrate
  existing feature folders once this schema ships) and extend that
  feature's Task 0.30 background note to mention `feat`'s `### Updates`
  shape as a fourth divergent variant — depends on: none — status:
  completed (2026-08-30)
- [x] Task 0.4: Phase-end quality gate + baseline commit + comment the
  commit hash on issue #31 — depends on: Task 0.2, Task 0.3 — status:
  completed (2026-08-30, commit 31c5c30, issue #31 comment posted)

#### Phase 1: Models + parser (`feat/models/v1/`)

- [ ] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on:
  Task 0.2 — status: not-started
- [ ] Task 1.2: `frontmatter.py` — `FeatFrontmatter(MarkdownFrontmatter)`:
  `type: Literal["feat"] = "feat"`, closed 4-set status validator, default
  `"planning"` — depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: `body.py` — all section classes per Design Notes:
  `Feature` (root), `Plan` + its 8 children (`Overview`/`DesignNotes`/
  `RelatedDecisions` leaves; `Requirements`/`RequirementItem`,
  `AcceptanceCriteria`/`AcceptanceCriterionItem` regex-validated lists;
  `Scope`/`Included`/`ExplicitlyOutOfScope`, `Dependencies`/`DependsOn`/
  `Blocks` composites (all four implicit-alias, no `LITERAL` needed);
  `TaskList`/`Phase` dynamic-list composite reusing
  `tsk.TaskItem`), `Progress` + its 6 children (`CurrentStatus`/`Blockers`/
  `RelatedPrsCommits`/`MoreInformation` leaves; `Updates`/`UpdateEntry`,
  `DecisionsMade`/`DecisionEntry` dynamic-list composites) — depends on:
  Task 1.2 — status: not-started
- [ ] Task 1.4: `document.py` (`FeatDocument`), `parser.py` (`parse_feat`
  glue), `summary.py` (`FeatSummary(DocSummary)` — adds one extra field,
  `path: str`, beyond the inherited `id`/`title`/`status`/`ref`; see
  Design Notes' Addressing section and Decisions Made for why `feat`
  needs this and every other domain's summary deliberately doesn't),
  `models/v1/__init__.py` - `models/__init__.py` exports — depends on:
  Task 1.3 — status: not-started
- [ ] Task 1.5: Reference fixture `feat_reference.md`, **seeded from this
  feature's own `.specmgr/feat/feat-31-feature/example.md`** (the
  canonical, engine-verified example — see Current Status/Decisions Made;
  do not re-derive the schema from scratch or restart from
  `feat_template.md`) — adjusted only as needed to exercise every field
  (all optional sections present, ≥2 `### Updates` entries and ≥2
  `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`
  entries each with ≥1 task item), all well-formed, exercising the
  ISO8601 regex on both `Updates` and `Decisions Made` — depends on: Task
  1.3 — status: not-started
- [ ] Task 1.6: Tests `tests/feat/models/v1/` — `test_frontmatter.py`
  (4-set status incl. rejection), `test_body.py` (alias acceptance/
  rejection incl. the `### Updates` ISO8601 regex, mandatory-vs-optional
  field combinations), `test_parser.py` (ACC-001 matrix + round-trip) —
  depends on: Task 1.4, Task 1.5 — status: not-started
- [ ] Task 1.7: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 1.6 — status: not-started

#### Phase 2: Tools (`feat/tools/`) — bespoke addressing

- [ ] Task 2.1: `_paths.py` (`feat_base_dir`, `iter_feat_paths`,
  `find_feat_path_by_id`, `FeatNotFoundError`, `FEAT_TYPE_NAME = "feat"`,
  `slugify` reuse) per Design Notes' Addressing section — depends on: Task
  1.4 — status: not-started
- [ ] Task 2.2: `_lock.py` (per-id `feat_lock(id_)` + global
  `feat_create_lock()`), `_io.py` (`read_feat`, `load_by_id`), `_write.py`
  (`write_feat_file`, creates the `<id>/` folder if missing) — depends on:
  Task 2.1 — status: not-started
- [ ] Task 2.3: The 8 tool modules + `tools/__init__.py`: `create_feat`
  (next-`NNN` derivation under the global lock), `parse_feat`, `list_feat`
  (`PagedResult[FeatSummary]`), `get_feat(id, raw=False)`,
  `get_feat_example`/`get_feat_template`, `delete_feat` (stub,
  `structured_output=False`), `validate_feat` — depends on: Task 2.2 —
  status: not-started
- [ ] Task 2.4: `general/tools/update.py`/`set_status.py` — add
  `_update_feat`/`_set_status_feat` adapters + `"feat"` dispatch table
  entries, built on Task 2.1/2.2's helpers — depends on: Task 2.2 —
  status: not-started
- [ ] Task 2.5: Tests `tests/feat/tools/` — one module per tool + helper
  tests + `test_integration.py` (ACC-003/ACC-004, incl. concurrent-create
  `NNN`-collision simulation) — depends on: Task 2.3, Task 2.4 — status:
  not-started
- [ ] Task 2.6: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 2.5 — status: not-started

#### Phase 3: Resources + packaged data + schema

- [ ] Task 3.1: `feat/data/feat_example.md` (byte-identical copy of
  `feat_reference.md`, DEC/GOL precedent) — depends on: Task 2.6 — status:
  not-started
- [ ] Task 3.2: `feat/data/feat_template.md` — all-sections placeholder
  skeleton, `status: planning`; must round-trip through `parse_feat` —
  depends on: Task 2.6 — status: not-started
- [ ] Task 3.3: `feat/data/feat_create_instructions.md` +
  `feat_update_instructions.md` — depends on: Task 2.6 — status:
  not-started
- [ ] Task 3.4: `commands/schema.py` — `generate_feat_schema()` +
  `_GENERATORS["feat"]`; run `specmgr schema --type feat` (writes
  `docs/feat_schema.json`) and the packaged-copy variant — depends on:
  Task 1.4 — status: not-started
- [ ] Task 3.5: `feat/resources/` — `feat_schema.py`, `feat_example.py`,
  `feat_template.py`, `__init__.py` — depends on: Task 3.1, Task 3.2, Task
  3.4 — status: not-started
- [ ] Task 3.6: Tests `tests/feat/resources/` (ACC-005/ACC-007) — depends
  on: Task 3.5 — status: not-started
- [ ] Task 3.7: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 3.6 — status: not-started

#### Phase 4: Prompts

- [ ] Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`),
  `update_feat.py` (`update_feat(id, instructions=None)`), `__init__.py`
  — depends on: Task 3.3 — status: not-started
- [ ] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
  4.1 — status: not-started
- [ ] Task 4.3: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 4.2 — status: not-started

#### Phase 5: Cross-cutting registration

- [ ] Task 5.1: `server.py` — add `feat` to the domain import line +
  module docstring — depends on: Task 4.3 — status: not-started
- [ ] Task 5.2: `pyproject.toml` package-data entry; `.pre-commit-config.yaml`
  (`feat/models/v1` added to schema-hook globs + new
  `specmgr-schema-feat-package` hook); `.github/workflows/ci.yml` (new
  packaged-copy drift step) — depends on: Task 3.4 — status: not-started
- [ ] Task 5.3: `AGENTS.md` — new `feat/` bullet documenting the addressing
  deviation explicitly (non-UUID id, folder-per-document, bespoke
  `_paths.py`); update the domain-enumeration sentences; decide (and note)
  whether root `README.md`'s artifact list gains `Feature (FEAT)` — depends
  on: Task 5.1 — status: not-started
- [ ] Task 5.4: Regenerate `docs/MCP.md`/`docs/GENERATED.md`/`docs/api/`/
  `docs/feat_schema.json`; confirm all idempotent on a second run — depends
  on: Task 5.1, Task 5.2 — status: not-started
- [ ] Task 5.5: Final verification pass — walk every ACC-001..009 with
  concrete evidence; full quality gate end to end; set feature status to
  `done` — depends on: Phase 0-4 complete, Task 5.4 — status: not-started
- [ ] Task 5.6: Final commit + comment on issue #31; update this README's
  Progress section — depends on: Task 5.5 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-30**: Phase 0 (Scaffolding) committed — GitHub issue #31
filed, branch `feat-31-feature` created off `dev`, this plan written and
reviewed with the user across several rounds (body-modeling depth,
addressing scheme, frontmatter `version` semantics, status vocabulary,
`Updates` shape/naming, MCP surface scope, no-migration decision, branch
naming, feat-7 backlog entry); package skeleton
(`feat/{models/v1,tools,resources,prompts}`, `tests/feat/{models/v1, tools,resources,prompts}`) in place; `feat-7-various-improvements` Task 0.31
added and Task 0.30 extended. Full quality gate green (2007 tests, ruff
format/check clean, vulture clean). Committed as 31c5c30/164182e. **Paused
here, deliberately**: implementation was not what was asked for at this
point — the design (schema, addressing scheme, MCP surface) needs a review
pass by the user first, who may request adjustments, before Phase 1 (or any
further phase) starts. See Blockers.

A second design-review round produced a full worked example of the
proposed document structure, refined through two further review rounds
(ordering/comment/hyperlink questions; LITERAL-alias elimination) into
`.specmgr/feat/feat-31-feature/example.md` — not consumed by any code.
That round's resolved questions are folded into this plan's Design
Notes/Decisions Made above; the Blocker below still applies (no
`src`/`tests` code yet, but the Design Notes themselves have now had
four review passes).

**`.specmgr/feat/feat-31-feature/example.md` is the canonical,
implementation-ready worked example** — every design decision through the
fourth review round is reflected in it, and it has been cross-checked
against the live `models/md` engine (not just eyeballed): every implicit
`SPACE_SEPARATED` heading alias in the design was run through
`space_separated_name()` directly, which is what caught the three
`RelatedAdrs`/`ExplicitlyOutOfScope`/`DependsOn` issues recorded in
Decisions Made above. **Task 1.5 in the Task List explicitly instructs
the implementing agent to seed `feat_reference.md` from this file** —
this is a load-bearing pointer, not just narrative context, since Task
1.5 is what an agent executing Phase 1 actually follows. The two
superseded review-process drafts (`example-initial.md`,
`example-revised.md`) have been removed — this is now the only example
file in this feature's own folder.

**Design review is complete, as of 2026-08-30, after five review
rounds.** The Blocker below is resolved — Phase 1 is authorized to
start. Frontmatter `status` moved from `planning` to `in-progress`
accordingly. **Implementation itself is explicitly deferred to a
separate session/agent (e.g. a Phase-Orchestrator-style agent driving
the Task List phase by phase)** — this design-review session closes
here without touching any `src`/`tests` code; Phase 0's committed
scaffold (`31c5c30`, `164182e`) stays exactly as-is, untouched, ready
for whichever agent picks up Task 1.1 next.

### Blockers

- [x] Design review — resolved 2026-08-30. Reviewed across five rounds
  (body-modeling depth; Task List/Scope/Dependencies/Decisions Made
  structure; ordering/comment/hyperlink questions; LITERAL-alias
  elimination; partial-id-match/env-var/FeatSummary-path questions).
  Approved as final; see Decisions Made for the complete decision log.
  Phase 0's committed scaffold (`31c5c30`, `164182e`) stays as-is — no
  revert/rebase/rewrite performed or needed. No blockers remain; Phase 1
  is authorized to start (by a separate implementing agent/session, not
  as part of this design-review conversation).

### Recent Updates

#### Update 2026-08-30 (design review complete — Blocker resolved, Phase 1 authorized)

- **Design review declared complete** after five rounds spanning
  body-modeling depth, addressing scheme, frontmatter semantics, MCP
  surface scope, ordering/comment/hyperlink questions, LITERAL-alias
  elimination, and partial-match/env-var/FeatSummary-path questions — no
  open questions remain in Design Notes.
- Frontmatter `status` changed from `planning` to `in-progress`; version
  bumped to `1.6.0`.
- Blockers: "Design review pending" marked resolved (`[x]`), recording
  the five-round history and confirming Phase 0's committed scaffold
  (`31c5c30`, `164182e`) stays untouched.
- Recorded as a new Decisions Made entry.
- **Implementation was explicitly not started in this session** —
  user-directed: Phase 1 (and every later phase) is to be carried out by
  a separate implementing session/agent (e.g. a Phase-Orchestrator-style
  agent working through the Task List), not as a continuation of this
  design-review conversation. Nothing under `src`/`tests` was touched.
- Next: a separate agent starts at Task 1.1 (`feat/models/v1/_util.py`).

#### Update 2026-08-30 (fifth design-review round — partial-match rejected, env var confirmed mandatory, FeatSummary gains path)

- Resolved three more follow-up questions and updated Design Notes/Task
  List/Decisions Made accordingly:
  - **Partial-id matching rejected**: verified an agent can already
    resolve a bare `"feat-31"` to the real id via `list_feat` +
    `get_feat` composition, so no boundary-matching/ambiguous-match/scan
    logic is being added to `find_feat_path_by_id`.
  - **`SPECMGR_FEAT_DIR` confirmed mandatory**: checked the actual
    precedent (`adr/tools/_paths.py`'s `SPECMGR_ADR_DIR`,
    `general/tools/_doc_paths.py`'s shared `SPECMGR_DOCS_DIR`) — every
    existing domain has an equivalent env var for test isolation; `feat`
    keeps its own, made explicit in REQ-004/Design Notes rather than
    just a parenthetical.
  - **`FeatSummary` gains `path: str`**: checked `general/models/ summary.py`'s `DocSummary` and confirmed its `ref` field is
    deliberately *not* a path, specifically to discourage direct file
    access (same policy `AdrSummary` enforces, backed by an ADR requiring
    ADRs be edited only through MCP tools). `feat` is the opposite case
    by design — direct hand/agent editing of `.specmgr/feat/<id>/ README.md` is the intended, sanctioned workflow — so `FeatSummary`
    adds a real `path` field alongside the inherited `id`/`ref`, not in
    place of them.
- Nothing under `src`/`tests` was touched.

#### Update 2026-08-30 (removed superseded example drafts; closed the "does Phase 1 know to use it" gap)

- Removed `.specmgr/feat/feat-31-feature/example-initial.md` and
  `example-revised.md` — both superseded review-process drafts, now that
  `example.md` has absorbed everything useful from them across four
  review rounds. `example.md` is the only example file left in this
  feature's folder.
- Caught and fixed a real gap: `example.md` had only ever been marked
  "canonical" in narrative Current Status/Decisions Made/Recent Updates
  text — Task 1.5 (the actionable Task List item an implementing agent
  actually follows in Phase 1) never mentioned it at all. Updated Task
  1.5 to explicitly instruct seeding `feat_reference.md` from
  `example.md`, and updated Current Status to reflect the same.
- Nothing under `src`/`tests` was touched.

#### Update 2026-08-30 (fourth design-review round — eliminated all remaining LITERAL aliases except one)

- Per explicit user direction to minimize `LITERAL` alias use, replaced
  three headings with spellings that match the implicit `SPACE_SEPARATED`
  derivation exactly, eliminating the need for a `LITERAL` override on
  each (verified against the live engine, same as the previous round):
  - `"Related ADRs"` → **`"Related Decisions"`** (`RelatedAdrs` →
    `RelatedDecisions`) — also a deliberate terminology change: phases
    out "ADR" in favor of "Decision"/`dec`, per user direction, since
    this codebase intends to retire ADR terminology over time. Entries
    may still reference either an ADR id or a `dec` id.
  - `"Explicitly out of scope"` → **`"Explicitly Out Of Scope"`**
    (`ExplicitlyOutOfScope` unchanged) — accepted as consistent with this
    codebase's existing Start-Case multi-word headings.
  - `"Depends on"` → **`"Depends On"`** (`DependsOn` unchanged) — reusing
    the parent's own name "Dependencies" for this child was considered
    and rejected (confusing tautology, awkward `Dependencies.dependencies`
    field name).
  - `RelatedPrsCommits`/`"Related PRs / Commits"` keeps its `LITERAL`
    alias — no casing-only fix exists for a heading containing a slash.
- Updated the ASCII diagram, Model classes prose, REQ-001, and Task 1.3
  in Design Notes; recorded as a new Decisions Made entry. `example.md`
  needed no content changes beyond the "Related ADRs" → "Related
  Decisions" heading rename itself.
- Nothing under `src`/`tests` was touched.

#### Update 2026-08-30 (example.md verified and marked canonical)

- Cross-checked every implicit `SPACE_SEPARATED` heading alias in the
  design against the live engine (`models.md.alias_match. space_separated_name`) instead of assuming the derivation matched the
  intended heading text. Found and fixed 3 real bugs that would have
  broken `parse_feat` in Phase 1: `RelatedAdrs` (pre-existing since round
  1), `ExplicitlyOutOfScope`, `DependsOn` — all three now get an explicit
  `@alias(..., type=AliasType.LITERAL)`, added to Design Notes and
  recorded as a new Decisions Made entry. `example.md` itself needed no
  changes (its heading text was already the intended natural-English
  form); only the model-class documentation was wrong.
- Marked `.specmgr/feat/feat-31-feature/example.md` as the canonical,
  implementation-ready worked example in Current Status above.
  `example-initial.md`/`example-revised.md` are superseded review-process
  artifacts — flagged as safe to remove, not yet deleted (awaiting
  explicit confirmation).
- Nothing under `src`/`tests` was touched. Next: remove the two
  superseded example files once confirmed, then this feature is ready to
  come off the design-review Blocker and resume at Phase 1.

#### Update 2026-08-30 (third design-review round — ordering/comment/hyperlink questions)

- Resolved three follow-up design questions and updated the Design Notes/
  Decisions Made accordingly:
  - `### Related PRs / Commits`: confirmed it stays free-form, not
    regex-enforced as hyperlinks (the existing "no PR yet" placeholder
    idiom would otherwise break).
  - `### Updates`/`### Decisions Made` both gain an optional `comment`
    field (`MarkdownSection3WithComment`, `req`'s `Level`/`Priority`
    precedent) to host a machine-readable ordering hint in
    `feat_template.md`/`feat_example.md`, rather than a bare editorial
    comment.
  - `### Decisions Made` entries switch to the same full ISO8601
    timestamp as `### Updates` (not date-only), and both sections gain a
    real `@model_validator`-enforced newest-first ordering invariant —
    discovered along the way that `tsk_example.md` (newest-first) and
    `dec_example.md` (oldest-first) already disagree on direction with no
    enforcement either way; confirmed via
    `general/data/general_compact_history_instructions.md` that
    "newest first" is the existing, already-tool-supported convention for
    the ad hoc `### Recent Updates` this feature formalizes, so that's
    what both new sections enforce.
- Nothing under `src`/`tests` was touched. Next: continue design review,
  or unblock and resume Phase 1 once the user confirms the design is
  final.

#### Update 2026-08-30 (second design-review round — Task List/Scope/Dependencies/Decisions Made structure)

- The user drafted `example-revised.md` (annotated with review comments/
  open questions) building on the first `example.md`. Resolved every open
  question raised in it:
  - `### Requirements`/`### Acceptance Criteria` become regex-validated
    lists (`REQ-\d{3}: ...`/checkbox `ACC-\d{3}: ...`), not opaque leaves.
  - `### Scope` becomes a composite with mandatory `#### Included`/
    `#### Explicitly out of scope` leaves (both required).
  - `### Dependencies` becomes a composite with optional `#### Depends on`/
    `#### Blocks` leaves (both optional).
  - `### Task List` becomes a composite of `#### Phase N: ...` entries
    (regex-validated heading, unpadded numbering), each phase reusing
    `tsk.TaskItem` for its own flat checklist — a partial reversal of the
    original "Task List stays opaque" decision (per-item metadata still
    stays unparsed).
  - `### Decisions Made` becomes a composite of dated
    `#### {yyyy-MM-dd} — {title}` entries, chosen over a formalized-flat-
    list alternative for consistency with `### Updates`.
  - A new optional `### More Information` leaf is added under
    `## Progress`.
  - Recorded all of the above as a new Decisions Made entry, explicitly
    superseding the earlier "mostly opaque leaves"/"Task List stays a
    single opaque leaf" decisions.
- Updated this plan's REQ-001, the Design Notes' ASCII structure diagram
  and "Model classes" prose, Task 1.3, ACC-001, and the Scope section's
  "explicitly out of scope" bullet on Task List to match.
- Nothing under `src`/`tests` was touched — the Blocker (design review
  pending before Phase 1) still applies; this round only revised the
  design itself, per explicit user instruction not to remove/change
  anything else yet.
- Next: continue the design review (any further structural questions),
  then unblock and resume at Phase 1 once the user confirms.

#### Update 2026-08-30 (paused for design review after Phase 0)

- Corrected: implementing Phase 0's package skeleton was premature — the
  user had asked for the design to be planned and reviewed, not for
  implementation to start. Nothing from Phase 0 is reverted (both commits,
  `31c5c30` and `164182e`, stay on the branch as-is); instead, this feature
  is explicitly paused here, recorded as a Blocker above, until the user
  completes a review pass over this plan's Design Notes and either confirms
  it or requests adjustments.
- Also noted and resolved as a non-issue: an earlier "fyi, `sop` is still
  in development and not pushed yet" flag from the user turned out not to
  affect this branch — `git fetch origin dev` confirmed the `feat(sop): …`
  commits this branch's base (`c8f8a87`) sits on are already present on
  `origin/dev`, so `feat-31-feature`'s branch point is clean; no rebase
  needed.
- Next: wait for the user's design review/adjustments before touching any
  further code or advancing the Task List.

#### Update 2026-08-30 (Phase 0: Scaffolding — complete)

- Completed Tasks 0.1–0.4, the final tasks of Phase 0.
  - Task 0.2: package skeleton — `feat/__init__.py` (docstring + `from . import prompts, resources, tools`), empty `feat/models/__init__.py` +
    `feat/models/v1/__init__.py`, `feat/tools/__init__.py`,
    `feat/resources/__init__.py`, `feat/prompts/__init__.py` (each with a
    docstring pointing at the phase that populates it), and the matching
    `tests/feat/{__init__,models/__init__,models/v1/__init__,tools/__init__, resources/__init__,prompts/__init__}.py` (all empty, mirroring
    `tests/dec/`'s exact convention). `feat/data/` deferred to Phase 3.
  - Task 0.3: added Task 0.31 to `feat-7-various-improvements`'s Phase 0
    task list (migrate the 17 existing feature folders once this schema
    ships and Task 0.30's consolidation decision is made) plus a matching
    Recent Updates entry; extended Task 0.30's own background note to name
    `feat`'s planned `### Updates`/`#### {timestamp} — {title}` shape as a
    fourth divergent variant alongside `tsk`/`dec`/`sop`.
  - Task 0.4: full quality gate green (`ruff format --check`/`ruff check`
    clean, `vulture src/ whitelist.py --min-confidence 60` clean, full
    `unittest` suite 2007 tests OK); committed as `31c5c30` ("docs(feat):
    plan the Feature (feat) artifact type feature"); commit hash posted to
    issue #31.
- Next: Phase 1 (models + parser) — `feat/models/v1/{_util,frontmatter, body,document,parser,summary}.py`, `feat_reference.md`, and
  `tests/feat/models/v1/`.
- Notes: `sop` (feat-30) is still unimplemented (planning only, no
  `src/biz/dfch/specmgr/sop/` package exists yet) — this feature's
  `Updates`/`UpdateEntry` design cites `feat-30-sop`'s **plan**, not its
  code, as precedent. `git status` after Task 0.4's commit shows a clean
  tree on branch `feat-31-feature`.

#### Update 2026-08-30 (planning)

- Completed: Full design discussion with the user across two planning
  rounds: (1) extracted the common structure from all 17 existing
  `.specmgr/feat/*/README.md` files plus ADR e369ee2e and the two most
  recent "add artifact type" features (`feat-18-goal`, `feat-21-decision`)
  and the in-flight `feat-30-sop`; (2) resolved every open design question
  (body-modeling depth → mostly opaque leaves with a structured `Updates`
  section; addressing → keep `feat-NNN-slug` + folder + `README.md`,
  bespoke path resolution; `version` semantics → schema-version-only, drop
  the hand-bumped plan-revision meaning; status vocabulary → closed 4-set
  with no hyphens, `planning`/`progress`/`review`/`done`; MCP surface →
  full sop-style generic-dispatch lifecycle; `Updates` naming/shape →
  renamed from "Recent Updates" to "Updates", ISO8601-enforced heading
  regex copied from `feat-30-sop`'s plan one level deeper; migration of
  existing files → explicitly out of scope, tracked as a new
  `feat-7-various-improvements` backlog task instead; implementation
  branch → `feat-31-feature`).
- Filed GitHub issue #31 ("Formalize the Feature artifact type ("feat")"),
  created branch `feat-31-feature` off `dev`, wrote this plan file.
- Next: Phase 0 — package skeleton (`feat/__init__.py` + empty
  `models/v1`/`tools`/`resources`/`prompts`/`data` packages + `tests/feat/`
  skeleton), add Task 0.31 to `feat-7-various-improvements` and extend its
  Task 0.30 background note, then the Phase 0 quality gate + baseline
  commit.
- Notes: `sop` (feat-30) is still unimplemented (planning only, no
  `src/biz/dfch/specmgr/sop/` package exists yet) — this feature's
  `Updates`/`UpdateEntry` design cites `feat-30-sop`'s **plan**, not its
  code, as precedent.

### Decisions Made

- **2026-08-30**: `id` stays `feat-NNN-slug` (the folder name), not a
  server-generated UUID — a deliberate, documented deviation from ADR
  8cf940c5's precedent, confirmed by the user rather than switched to match
  every other domain.
- **2026-08-30**: Frontmatter `version` becomes schema-version-only
  (machine-managed), dropping the historical hand-bumped "plan revision"
  meaning entirely (user chose "drop the hand-bumped counter" over
  "split into two fields" or "keep as-is").
- **2026-08-30**: Closed 4-value status set with **no hyphens** —
  `planning`/`progress`/`review`/`done` (user explicitly rejected
  `in-progress` in favor of `progress`).
- **2026-08-30**: ~~Body sections stay mostly opaque leaves (Overview,
  Requirements, Acceptance Criteria, Scope, Dependencies, Design Notes,
  Related ADRs, Task List, Current Status, Blockers, Decisions Made,
  Related PRs/Commits) — only `### Updates` gets real structure (H4 dynamic
  list, ISO8601-enforced heading).~~ **Superseded 2026-08-30** (see the
  entry directly below) — a second design-review round asked for real
  structure on several more sections.
- **2026-08-30**: Second design-review round — supersedes the "mostly
  opaque leaves"/"Task List stays a single opaque leaf" decisions above,
  based on a revised example the user drafted directly
  (`example-revised.md`): `### Requirements`/`### Acceptance Criteria`
  become regex-validated lists (`REQ-\d{3}: ...`/checkbox
  `ACC-\d{3}: ...`, `TaskItem`-style, zero-padded 3-digit ids matching this
  plan's own numbering); `### Scope` becomes a composite of mandatory
  `#### Included`/`#### Explicitly out of scope` leaves (both required —
  every feature must state both); `### Dependencies` becomes a composite of
  optional `#### Depends on`/`#### Blocks` leaves (both optional, matching
  `Dependencies` itself already being optional); `### Task List` becomes a
  composite holding only `#### Phase N: ...` entries (regex
  `^Phase \d+: .+$`, unpadded, matching this plan's own "Phase 0".."Phase
  5" headings), each phase reusing `tsk.TaskItem` for its own flat
  checklist — per-item metadata (`depends on:`/`status:`/`ETA`) stays
  unparsed free text, so this is a partial, not full, reversal of the
  original "don't structurally model Task List" stance; `### Decisions Made` becomes a composite of dated `#### {...} — {title}` entries
  (format finalized in the entry directly below — chosen over a
  formalized-flat-list alternative for consistency with `### Updates`'s
  own shape); a new optional `### More Information` leaf is added under
  `## Progress`, mirroring `req`'s/ADR's own section one heading level
  deeper. `Overview`/`Design Notes`/`Related ADRs`/`Current Status`/
  `Blockers`/`Related PRs / Commits` remain opaque leaves, unchanged.
- **2026-08-30**: `### Updates` (not `### Recent Updates`), ISO8601-enforced
  `#### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}` heading regex, copied
  from `feat-30-sop`'s plan one heading level deeper (H3/H4 instead of
  H2/H3, since it sits under `## Progress` not directly under the H1).
- **2026-08-30**: Third design-review round — three follow-up questions
  resolved: (1) `### Related PRs / Commits` list items stay free-form, not
  regex-enforced as hyperlinks — the section's own current content
  (`- (Phase 0 baseline commit not yet made)`) is a legitimate non-link
  placeholder idiom that a strict link-only regex would break. (2)
  Confirmed the "comments only belong in an example if they populate a
  real schema-declared field" rule from the entry above by giving it a
  concrete use: `### Updates`/`### Decisions Made` both change from
  `MarkdownSection3` to `MarkdownSection3WithComment`, adding an optional
  `comment: MarkdownComment | None` field (`req`'s `Level`/`Priority`
  precedent) that `feat_template.md`/`feat_example.md` populate with a
  machine-readable ordering hint. (3) `### Decisions Made` entries switch
  from date-only `#### {yyyy-MM-dd} — {title}` (the shape recorded two
  entries above) to the *same* full ISO8601 timestamp format as
  `### Updates` — necessary because a same-day pair of decisions is
  otherwise indistinguishable for ordering purposes; and both
  `### Updates` and `### Decisions Made` gain a real, enforced ordering
  invariant (a `@model_validator` asserting newest-first, i.e. each
  entry's timestamp \<= the previous entry's, raising `AssertionError`
  otherwise) rather than relying on undocumented convention — newest-first
  was chosen (not oldest-first/append) because it matches the *existing*
  `compact_history` prompt's own "newest first" assumption for the ad hoc
  `### Recent Updates` this feature formalizes, and keeps history-rotation
  a simple cut-from-the-bottom operation. This directly resolves a
  concrete, pre-existing gap noticed during this round: `tsk_example.md`'s
  shipped example is newest-first while `dec_example.md`'s is
  oldest-first, with neither domain's model code enforcing (or even
  documenting) either direction — an ambiguity `feat`'s own two sections
  now avoid inheriting (the cross-domain inconsistency itself stays out of
  scope, tracked by `feat-7-various-improvements` Task 0.30).
- **2026-08-30**: The 17 existing feature folders are **not** migrated by
  this feature — tracked as a new `feat-7-various-improvements` Task 0.31
  instead (user-directed).
- **2026-08-30**: `Updates`/`Recent Updates` naming consolidation across
  domains is **not** a new task — the existing `feat-7-various-improvements`
  Task 0.30 already covers it; only its background note is extended to
  mention `feat` as a fourth divergent variant (user-directed: "let the
  existing feat-7 0.30 task handle this consolidation").
- **2026-08-30**: Implementation happens on branch `feat-31-feature`,
  created off `dev` before Phase 0 (user-directed).
- **2026-08-30**: MCP surface is full sop-style generic dispatch (`create_feat`/
  `parse_feat`/`list_feat`/`get_feat`/`get_feat_example`/`get_feat_template`/
  `delete_feat` stub/`validate_feat` + `type="feat"` in the generic
  `update`/`set_status` tools) — no `update_feat`/`set_status_feat` of its
  own (user chose the "full lifecycle, sop-style generic dispatch" option).
- **2026-08-30**: Fixed three implicit-alias bugs found by actually running
  `space_separated_name()` from `models/md/alias_match.py` against every
  implicit-`SPACE_SEPARATED`-alias class name in this design, rather than
  assuming the derivation matched the intended heading text:
  `RelatedAdrs` (would derive `"Related Adrs"`, not `"Related ADRs"` — a
  bug present since round 1, undetected through two subsequent review
  rounds), `ExplicitlyOutOfScope` (would derive `"Explicitly Out Of Scope"`, not `"Explicitly out of scope"`), and `DependsOn` (would
  derive `"Depends On"`, not `"Depends on"`). All three now get an
  explicit `@alias(value=..., type=AliasType.LITERAL)`, the same fix
  already used for `RelatedPrsCommits`. `example.md`'s own heading text
  needed no changes — it already used the intended natural-English
  headings; only the Design Notes' model-class documentation was wrong.
  This verification pass is what qualifies `example.md` as the canonical,
  implementation-ready example (see Current Status) rather than just a
  visually-plausible one.
- **2026-08-30**: Fourth design-review round — eliminated all three
  `LITERAL` aliases added in the entry directly above, per explicit user
  direction to minimize `LITERAL` use wherever a different, still-clear
  spelling makes the implicit `SPACE_SEPARATED` derivation match exactly:
  `RelatedAdrs`/`"Related ADRs"` → `RelatedDecisions`/`"Related Decisions"` (`space_separated_name("RelatedDecisions")` derives this
  exactly) — also a deliberate terminology change, not just a casing fix:
  this codebase intends to phase out ADR in favor of `dec` over time, so
  a brand-new schema adopts the forward-looking name; entries may still
  reference an ADR id, a `dec` id, or any other decision record.
  `ExplicitlyOutOfScope`/`"Explicitly out of scope"` →
  `"Explicitly Out Of Scope"` (matches the derivation exactly; accepted
  as consistent with this codebase's own existing Start-Case multi-word
  headings, e.g. "Acceptance Criteria"). `DependsOn`/`"Depends on"` →
  `"Depends On"` (matches the derivation exactly; reusing the parent's
  own name "Dependencies" for this child was considered and rejected as
  a confusing tautology). `RelatedPrsCommits` keeps its `LITERAL` alias
  — the slash in "Related PRs / Commits" has no casing-only fix, unlike
  the three eliminated here. Updated Design Notes' ASCII diagram, Model
  classes prose, REQ-001, and Task 1.3 to match; `example.md` needs no
  further heading changes since it always used the intended spelling
  (only the `Design Notes` heading text itself and `## Related ADRs`
  cross-reference label conceptually rename to "Related Decisions" — no
  content change needed in the example beyond that heading).
- **2026-08-30**: Fifth design-review round — three more questions
  resolved: (1) **No partial-id-match support** in `find_feat_path_by_id`
  — considered and rejected; an agent that only has a bare `"feat-31"`
  can already resolve the real id for free via `list_feat` (whose
  `FeatSummary` entries carry the real `id`) followed by `get_feat` with
  the resolved id, so adding boundary-matching regex/an ambiguous-match
  error/a scan fallback to the addressing layer would solve a need the
  existing tools already cover. (2) **Confirmed `SPECMGR_FEAT_DIR` is
  mandatory, not optional** — every existing domain has an equivalent env
  var (`SPECMGR_ADR_DIR`, the shared `SPECMGR_DOCS_DIR`), specifically for
  test isolation; omitting it would make `feat` the only domain without
  test isolation for its base directory (and `feat`'s real base directory
  is `.specmgr/feat/`, the very folder this plan file lives in). (3)
  **`FeatSummary(DocSummary)` gains one extra field, `path: str`** (the
  real filesystem path to the document's `README.md`) — a deliberate,
  explained divergence from every other domain's summary, whose `ref`
  field is deliberately *not* a path specifically to discourage direct
  file access; `feat` is the opposite case, since ADR e369ee2e's whole
  governing convention for `.specmgr/feat/` *is* direct hand/agent
  markdown editing, which stays normal and sanctioned even after `feat`'s
  own MCP tools exist. `id`/`ref` stay on `FeatSummary` — `path` is
  additive, not a replacement. Updated REQ-004, the Addressing section,
  and Task 1.4 to match.
- **2026-08-30**: **Design review declared complete** after five rounds —
  no open questions remain in Design Notes (the one documented
  contingency, a possible future ADR for the addressing deviation "if it
  turns out to have implications beyond this one domain," is an
  intentional deferred-not-blocking note, not an open review item).
  Frontmatter `status` moves from `planning` to `in-progress`; the
  Blockers section's "Design review pending" item is marked resolved.
  Phase 1 is authorized to start. **Implementation itself is explicitly
  deferred to a separate implementing session/agent** (e.g. a
  Phase-Orchestrator-style agent driving the Task List phase by phase) —
  user-directed: this design-review conversation closes here without
  touching any `src`/`tests` code, so the next agent picks up cleanly at
  Task 1.1 against Phase 0's untouched committed scaffold.

### Related PRs / Commits

- [Issue #31](https://github.com/dfch/biz.dfch.SpecMgr/issues/31): Formalize
  the Feature artifact type ("feat")
- (Phase 0 baseline commit not yet made)
  </content>
