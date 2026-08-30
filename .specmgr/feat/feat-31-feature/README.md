---
created: 2026-08-30
id: feat-31-feature
status: done
updated: 2026-08-30
version: 1.13.0
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

- [x] ACC-001: Verifies REQ-001/002 — schema documented
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
- [x] ACC-002: Verifies REQ-003/004 — a document whose frontmatter `id`
  doesn't match its containing folder's name is rejected by the tool layer
  (not the model layer); `find_feat_path_by_id` resolves via the direct
  `<base>/<id>/README.md` shortcut, not a directory scan; `create_feat`
  correctly derives the next `NNN` under concurrent-create simulation (global
  lock prevents two callers from picking the same `NNN`).
- [x] ACC-003: Verifies REQ-005 — every listed tool is implemented,
  registered, and callable; a create→get→list→delete(stub)→validate
  round-trip against a temp `SPECMGR_FEAT_DIR` succeeds; `list_feat` returns
  `PagedResult[FeatSummary]` with default page size 25 / cap 100.
- [x] ACC-004: Verifies REQ-006 — `update(type="feat", ...)` and
  `set_status(type="feat", ...)` both work end to end (whole-body, line-range,
  and status-change modes), preserving `id`/`type`/`created`/`version` and
  bumping only `updated`/`status` as appropriate.
- [x] ACC-005: Verifies REQ-007 — every listed resource is implemented and
  registered (no `/{id}`, no `/list`).
- [x] ACC-006: Verifies REQ-008 — both prompts narrate the full
  dedup-check → `TodoWrite` → `question`-tool → tool-call-sequence flow,
  verified by walking both packaged instruction files end to end against a
  real document, not just asserting their static text.
- [x] ACC-007: Verifies REQ-009 — `specmgr schema --type feat` and the
  generic `specmgr schema` both produce an identical, packaged-copy-matching
  `feat_schema.json`.
- [x] ACC-008: Verifies REQ-010 — `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` all report zero drift after implementation; `AGENTS.md`
  reflects the new domain; `feat-7-various-improvements` carries the new
  Task 0.31 and Task 0.30's background note is extended to mention `feat` as
  a fourth divergent `Updates`/`Recent Updates` shape.
- [x] ACC-009: Verifies REQ-011 — full unittest suite green; ruff
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
instead, per user direction. `created`/`updated` use the same
microsecond ISO timestamp (`datetime.now().isoformat(timespec="microseconds")`)
as every other whole-body domain — **this reverses an earlier, deliberate
divergence** (plain `YYYY-MM-DD` dates, matching every one of the 17
pre-existing hand-authored feature files and ADR e369ee2e's own
template), reversed as a Phase 6 follow-up for cross-domain consistency;
see Decisions Made for the rationale. The 17 pre-existing feature files
themselves remain out of scope/unaffected by this change (see Scope) —
this only affects documents created/updated via the `feat` MCP tools
going forward.

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

- [x] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on:
  Task 0.2 — status: completed (2026-08-30)
- [x] Task 1.2: `frontmatter.py` — `FeatFrontmatter(MarkdownFrontmatter)`:
  `type: Literal["feat"] = "feat"`, closed 4-set status validator, default
  `"planning"` — depends on: Task 1.1 — status: completed (2026-08-30)
- [x] Task 1.3: `body.py` — all section classes per Design Notes:
  `Feature` (root), `Plan` + its 8 children (`Overview`/`DesignNotes`/
  `RelatedDecisions` leaves; `Requirements`/`RequirementItem`,
  `AcceptanceCriteria`/`AcceptanceCriterionItem` regex-validated lists;
  `Scope`/`Included`/`ExplicitlyOutOfScope`, `Dependencies`/`DependsOn`/
  `Blocks` composites (all four implicit-alias, no `LITERAL` needed);
  `TaskList`/`Phase` dynamic-list composite reusing
  `tsk.TaskItem`), `Progress` + its 6 children (`CurrentStatus`/`Blockers`/
  `RelatedPrsCommits`/`MoreInformation` leaves; `Updates`/`UpdateEntry`,
  `DecisionsMade`/`DecisionEntry` dynamic-list composites) — depends on:
  Task 1.2 — status: completed (2026-08-30). Added one judgment call not
  spelled out verbatim in Design Notes: `Requirements`/`AcceptanceCriteria`/
  `Phase` each gained their own eager-computed-field-validation
  `model_validator`, mirroring `tsk.models.v1.body.Task._validate_items_eagerly`
  exactly, so a malformed `REQ-\d{3}: .../ACC-\d{3}: .../- [z] ...` item
  raises immediately at parse time instead of only whenever something
  later happens to read the offending computed field — see Decisions Made.
- [x] Task 1.4: `document.py` (`FeatDocument`), `parser.py` (`parse_feat`
  glue), `summary.py` (`FeatSummary(DocSummary)` — adds one extra field,
  `path: str`, beyond the inherited `id`/`title`/`status`/`ref`; see
  Design Notes' Addressing section and Decisions Made for why `feat`
  needs this and every other domain's summary deliberately doesn't),
  `models/v1/__init__.py` - `models/__init__.py` exports — depends on:
  Task 1.3 — status: completed (2026-08-30)
- [x] Task 1.5: Reference fixture `feat_reference.md`, **seeded from this
  feature's own `.specmgr/feat/feat-31-feature/example.md`** (the
  canonical, engine-verified example — see Current Status/Decisions Made;
  do not re-derive the schema from scratch or restart from
  `feat_template.md`) — adjusted only as needed to exercise every field
  (all optional sections present, ≥2 `### Updates` entries and ≥2
  `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`
  entries each with ≥1 task item), all well-formed, exercising the
  ISO8601 regex on both `Updates` and `Decisions Made` — depends on: Task
  1.3 — status: completed (2026-08-30), at
  `tests/feat/models/v1/data/feat_reference.md` (mirroring the
  `tests/models/adr/v1/examples/` file-fixture-on-disk convention, since
  `tests/dec/models/v1/` itself keeps its reference text inline in
  `test_body.py`/`test_parser.py`, not as a separate file — see Decisions
  Made). Two small, content-preserving adjustments were needed beyond
  "seeded from `example.md`": every bullet/checklist list gained a blank
  line between items (a loose list) to sidestep `MarkdownListItem`'s own
  documented tight-list round-trip quirk (`dec`'s own reference text
  already uses the same loose-list workaround), and Task 0.1's item text
  had its trailing `— status: completed (2026-08-30)` suffix dropped so
  the item stays on one physical line (`TaskItem`'s marker regex does not
  span embedded newlines) — see Decisions Made.
- [x] Task 1.6: Tests `tests/feat/models/v1/` — `test_frontmatter.py`
  (4-set status incl. rejection), `test_body.py` (alias acceptance/
  rejection incl. the `### Updates` ISO8601 regex, mandatory-vs-optional
  field combinations), `test_parser.py` (ACC-001 matrix + round-trip) —
  depends on: Task 1.4, Task 1.5 — status: completed (2026-08-30), 99 new
  tests (11 `test_frontmatter.py` + 70 `test_body.py` + 18 `test_parser.py`).
- [x] Task 1.7: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 1.6 — status: completed (2026-08-30) — quality gate
  green; **commit and issue comment left to the orchestrator**, per this
  phase's own task instructions (implementer runs the gate only).

#### Phase 2: Tools (`feat/tools/`) — bespoke addressing

- [x] Task 2.1: `_paths.py` (`feat_base_dir`, `iter_feat_paths`,
  `find_feat_path_by_id`, `FeatNotFoundError`, `FEAT_TYPE_NAME = "feat"`,
  `slugify` reuse) per Design Notes' Addressing section — depends on: Task
  1.4 — status: completed (2026-08-30). Also added `feature_title()` (strips
  the literal `"Feature: "` prefix off `Feature.text`, see Decisions Made)
  and `FEAT_FOLDER_PATTERN`/`README_FILENAME` constants, none spelled out
  verbatim in the task but needed by `create_feat`/`list_feat` in Task 2.3.
- [x] Task 2.2: `_lock.py` (per-id `feat_lock(id_)` + global
  `feat_create_lock()`), `_io.py` (`read_feat`, `load_by_id`), `_write.py`
  (`write_feat_file`, creates the `<id>/` folder if missing) — depends on:
  Task 2.1 — status: completed (2026-08-30). Both locks are in-process
  `threading.Lock` instances (see Decisions Made — the plan's own prose
  mentioning "a single lock file at `<base>/.create.lock`" was not
  followed, for consistency with every other domain's precedent).
- [x] Task 2.3: The 8 tool modules + `tools/__init__.py`: `create_feat`
  (next-`NNN` derivation under the global lock), `parse_feat`, `list_feat`
  (`PagedResult[FeatSummary]`), `get_feat(id, raw=False)`,
  `get_feat_example`/`get_feat_template`, `delete_feat` (stub,
  `structured_output=False`), `validate_feat` — depends on: Task 2.2 —
  status: completed (2026-08-30). `get_feat_example`/`get_feat_template`
  are wired to `read_packaged_text("feat", "example"/"template")` exactly
  like every other domain, but the packaged files themselves don't exist
  until Phase 3 (Task 3.1/3.2) — both tools currently raise
  `FileNotFoundError` when actually called; see Decisions Made.
- [x] Task 2.4: `general/tools/update.py`/`set_status.py` — add
  `_update_feat`/`_set_status_feat` adapters + `"feat"` dispatch table
  entries, built on Task 2.1/2.2's helpers — depends on: Task 2.2 —
  status: completed (2026-08-30). Both adapters bump `updated` to a plain
  `YYYY-MM-DD` date (`datetime.now().date().isoformat()`), not the other
  eight/nine domains' microsecond timestamp, matching `create_feat`'s own
  frontmatter convention. Also updated one pre-existing test
  (`tests/general/tools/test_update.py::TestUpdateRegistration`) whose
  hardcoded 8-value `type` enum assertion needed `"feat"` added, now that
  the live `update` tool's registered schema carries 9 values.
- [x] Task 2.5: Tests `tests/feat/tools/` — one module per tool + helper
  tests + `test_integration.py` (ACC-003/ACC-004, incl. concurrent-create
  `NNN`-collision simulation) — depends on: Task 2.3, Task 2.4 — status:
  completed (2026-08-30), 73 new tests (`test__paths.py`/`test__lock.py`/
  `test__io.py`/`test__write.py`/`test_create_feat.py`/`test_get_feat.py`/
  `test_list_feat.py`/`test_parse_feat.py`/`test_validate_feat.py`/
  `test_delete_feat.py`/`test_get_feat_example.py`/
  `test_get_feat_template.py`/`test_integration.py`), plus the one
  pre-existing test file updated in Task 2.4.
- [x] Task 2.6: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 2.5 — status: completed (2026-08-30) — quality gate
  green; **commit and issue comment left to the orchestrator**, per this
  phase's own task instructions (implementer runs the gate only).

#### Phase 3: Resources + packaged data + schema

- [x] Task 3.1: `feat/data/feat_example.md` (byte-identical copy of
  `feat_reference.md`, DEC/GOL precedent) — depends on: Task 2.6 — status:
  completed (2026-08-30)
- [x] Task 3.2: `feat/data/feat_template.md` — all-sections placeholder
  skeleton, `status: planning`; must round-trip through `parse_feat` —
  depends on: Task 2.6 — status: completed (2026-08-30)
- [x] Task 3.3: `feat/data/feat_create_instructions.md` +
  `feat_update_instructions.md` — depends on: Task 2.6 — status:
  completed (2026-08-30)
- [x] Task 3.4: `commands/schema.py` — `generate_feat_schema()` +
  `_GENERATORS["feat"]`; run `specmgr schema --type feat` (writes
  `docs/feat_schema.json`) and the packaged-copy variant — depends on:
  Task 1.4 — status: completed (2026-08-30), `_GENERATORS` entry inserted
  alphabetically (`dec`, `feat`, `gol`, ...); both invocations produce
  byte-identical output, confirmed via `diff`.
- [x] Task 3.5: `feat/resources/` — `feat_schema.py`, `feat_example.py`,
  `feat_template.py`, `__init__.py` — depends on: Task 3.1, Task 3.2, Task
  3.4 — status: completed (2026-08-30)
- [x] Task 3.6: Tests `tests/feat/resources/` (ACC-005/ACC-007) — depends
  on: Task 3.5 — status: completed (2026-08-30), 20 new tests
  (`test_feat_schema.py`/`test_feat_example.py`/`test_feat_template.py`);
  also replaced the two Phase-2-deferred `FileNotFoundError`-only tests
  (`tests/feat/tools/test_get_feat_example.py`/
  `test_get_feat_template.py`) with real "returns the packaged file"
  happy-path assertions, mirroring `test_get_dec_example.py`/
  `test_get_dec_template.py`.
- [x] Task 3.7: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 3.6 — status: completed (2026-08-30) — quality gate
  green; **commit and issue comment left to the orchestrator**, per this
  phase's own task instructions (implementer runs the gate only).

#### Phase 4: Prompts

- [x] Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`),
  `update_feat.py` (`update_feat(id, instructions=None)`), `__init__.py`
  — depends on: Task 3.3 — status: completed (2026-08-30). Both are thin
  `string.Template` wrappers around the Phase-3 packaged instructions
  files, 1:1 mirrors of `dec.prompts.create_dec`/`update_dec` — neither
  calls `TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/
  `update`/`set_status` itself.
- [x] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
  4.1 — status: completed (2026-08-30), 29 new tests
  (`test_create_feat.py`/`test_update_feat.py`), including a real
  "walk the instructions end to end" test per prompt (ACC-006) against a
  temporary `SPECMGR_FEAT_DIR` — see Decisions Made for the fallback
  string judgment call.
- [x] Task 4.3: Phase-end quality gate + commit + comment on issue #31 —
  depends on: Task 4.2 — status: completed (2026-08-30) — quality gate
  green; **commit and issue comment left to the orchestrator**, per this
  phase's own task instructions (implementer runs the gate only).

#### Phase 5: Cross-cutting registration

- [x] Task 5.1: `server.py` — add `feat` to the domain import line +
  module docstring — depends on: Task 4.3 — status: completed
  (2026-08-30). Alphabetical import order (`adr, dec, feat, general, gol,
  prb, qa, req, rsk, tsk, uc`); the module docstring gained a
  `specmgr://feat/schema`/`/example`/`/template` Resources block (same
  position as `dec`'s own block, right before it in the file), a "FEAT has
  no `specmgr://feat/{id}` ... no `specmgr://feat/list`" sentence appended
  to the "DEC has no ..." paragraph, a new "Feature tools (`feat/tools/`)"
  paragraph in Tools (mirroring "Decision tools", plus one extra sentence
  noting `feat`'s bespoke addressing and its lack of
  `update_feat`/`set_status_feat` of its own), the `update`/`set_status`
  paragraphs' domain counts bumped from eight/nine to nine/ten
  whole-body/total domains (matching `general/tools/update.py`'s/
  `set_status.py`'s own docstrings, both already updated in Phase 2), a
  new "Feature prompts (`feat/prompts/`)" paragraph in Prompts (mirroring
  "Decision prompts"), and `feat` inserted into both domain-enumeration
  sentences ("Modules are grouped domain-first ..." and "Add a new domain
  by ...") plus the final "each register `tools`, `resources`, and
  `prompts`" sentence.
- [x] Task 5.2: `pyproject.toml` package-data entry; `.pre-commit-config.yaml`
  (`feat/models/v1` added to schema-hook globs + new
  `specmgr-schema-feat-package` hook); `.github/workflows/ci.yml` (new
  packaged-copy drift step) — depends on: Task 3.4 — status: completed
  (2026-08-30). `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]`
  added alphabetically between `dec` and `gol`. `feat/models/v1` added to
  the one shared `files:` regex glob in all 9 pre-existing occurrences
  (verified 9 before, 9 after) plus a new 10th occurrence in the new
  `specmgr-schema-feat-package` hook itself (mirroring
  `specmgr-schema-dec-package` verbatim, placed last, matching this
  file's insertion-order — not alphabetical — convention for per-domain
  hooks). CI gained a `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` ``
  drift step, same `if: matrix.python-version == '3.13'` guard and error-
  message format as the `dec` step, placed immediately after it.
- [x] Task 5.3: `AGENTS.md` — new `feat/` bullet documenting the addressing
  deviation explicitly (non-UUID id, folder-per-document, bespoke
  `_paths.py`); update the domain-enumeration sentences; decide (and note)
  whether root `README.md`'s artifact list gains `Feature (FEAT)` — depends
  on: Task 5.1 — status: completed (2026-08-30). New `feat/` bullet added
  between the `dec/` and `general/` bullets, same depth/style as `dec/`'s
  own; the `general/` bullet's domain counts bumped eight→nine/nine→ten;
  `delete_*`/`validate_*` enumeration lists, the domain-register-all-three
  sentence, and the `server.py`-description sentence in "MCP server
  (server.py)" all gained `feat`/`delete_feat`/`validate_feat`. Root
  `README.md`: added `Feature (FEAT)` to the active bulleted list
  (alphabetically between `Decision (DEC)` and `Goal (GOL)`), removed
  `Feature (FTR)` from the commented-out placeholder (wrong abbreviation
  besides being redundant now), and moved `Risk (RSK)` — already a fully
  implemented domain per `AGENTS.md`'s own `rsk/` bullet — from the
  placeholder into the active list as a drive-by fix, leaving only
  `Acceptance Criterium (ACC)` (not yet implemented) commented out. See
  Decisions Made for the full reasoning.
- [x] Task 5.4: Regenerate `docs/MCP.md`/`docs/GENERATED.md`/`docs/api/`/
  `docs/feat_schema.json`; confirm all idempotent on a second run — depends
  on: Task 5.1, Task 5.2 — status: completed (2026-08-30). `specmgr docs`
  changed only `docs/api/biz.dfch.specmgr.server.md` (the Task 5.1
  docstring changes); `specmgr mcp-docs` produced no diff at all (FEAT's
  tools/resources/prompts were already fully registered before this
  phase, so `docs/MCP.md` was already current); `specmgr schema` (all
  types) and `specmgr schema --type feat --output-dir
  src/biz/dfch/specmgr/feat/data` both reported every file "unchanged".
  Every one of the four commands was run a second time immediately after
  and produced byte-identical output/no further `git diff` — confirmed
  idempotent.
- [x] Task 5.5: Final verification pass — walk every ACC-001..009 with
  concrete evidence; full quality gate end to end; set feature status to
  `done` — depends on: Phase 0-4 complete, Task 5.4 — status: completed
  (2026-08-30). Full quality gate green: `ruff format --check` (1286
  files already formatted), `ruff check` (all checks passed), `vulture
  src/ whitelist.py --min-confidence 60` (clean), full `unittest` suite
  (2228 tests, OK; 221 of them under `tests/feat/` specifically), `specmgr
  unused-code` (no unused code found). See Recent Updates for the
  ACC-by-ACC evidence walkthrough. Frontmatter `status` set to `done`.
- [x] Task 5.6: Final commit + comment on issue #31; update this README's
  Progress section — depends on: Task 5.5 — status: **README Progress
  section updated by the implementing agent (2026-08-30); commit and
  issue #31 comment intentionally left to the orchestrator**, per this
  task's own instructions to the implementing agent.

#### Phase 6: Frontmatter timestamp format fix

- [x] Task 6.1: Change `feat` frontmatter's `created`/`updated` fields
  from plain `YYYY-MM-DD` dates to microsecond timestamps
  (`datetime.now().isoformat(timespec="microseconds")`), matching every
  other whole-body domain's own convention (`req`/`uc`/`tsk`/`qa`/`prb`/
  `gol`/`rsk`/`dec`). Affects `feat/tools/create_feat.py` (frontmatter
  construction), `general/tools/update.py`'s `_update_feat` adapter,
  `general/tools/set_status.py`'s `_set_status_feat` adapter, the Design
  Notes' "Frontmatter" section (which currently documents the plain-date
  divergence as deliberate), and any tests asserting the plain-date
  format (`tests/feat/tools/test_create_feat.py`,
  `tests/feat/tools/test_integration.py`, `tests/general/tools/`
  equivalents if any). This reverses this feature's own earlier
  deliberate design decision (see Decisions Made): update the Decisions Made log
  with a new entry explaining why, not just silently change the code —
  depends on: Phase 5 complete — status: completed (2026-08-30). Beyond
  the three enumerated `src` files, also corrected four stale docstring/
  data-file mentions of the old plain-date behavior that would otherwise
  have been left inaccurate: `feat/models/v1/frontmatter.py`'s module
  docstring, `feat/models/v1/body.py`'s `UpdateEntry` docstring (its
  contrast with frontmatter's format, not the body-level ISO8601
  `### Updates`/`### Decisions Made` heading format itself, which is
  unchanged and stays deliberately different), `feat/prompts/create_feat.py`'s
  module docstring, and the packaged `feat/data/feat_create_instructions.md`/
  `feat_update_instructions.md` narrated-instruction text read by the
  `create_feat`/`update_feat` prompts. `docs/feat_schema.json` and the
  packaged `feat/data/feat_schema.json` copy were regenerated
  (`specmgr schema --type feat` both ways) since they embed the changed
  `UpdateEntry` docstring text verbatim; `specmgr docs`/`specmgr mcp-docs`
  were also re-run and confirmed to only touch the expected six
  `docs/api/*.md` files (no further drift).

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-30 (Phase 6 complete — frontmatter timestamp format fix
implemented; feature done again)**: Task 6.1 is implemented and this
feature is **done** again. `feat` frontmatter's `created`/`updated`
fields now use the same microsecond ISO timestamp
(`datetime.now().isoformat(timespec="microseconds")`) as every other
whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`),
reversing this feature's own earlier deliberate plain-`YYYY-MM-DD`-date
divergence. Changed: `feat/tools/create_feat.py` (frontmatter
construction), `general/tools/update.py`'s `_update_feat` adapter,
`general/tools/set_status.py`'s `_set_status_feat` adapter, plus four
stale docstring/data-file mentions of the old format
(`feat/models/v1/frontmatter.py`, `feat/models/v1/body.py`'s
`UpdateEntry` docstring, `feat/prompts/create_feat.py`, and the packaged
`feat_create_instructions.md`/`feat_update_instructions.md`). Two
existing tests updated to assert the new format
(`tests/feat/tools/test_create_feat.py`,
`tests/feat/tools/test_integration.py`) — no new tests added, per this
phase's own no-new-functionality scope. `docs/feat_schema.json` and the
packaged `feat/data/feat_schema.json` copy regenerated (embed the
changed `UpdateEntry` docstring); `specmgr docs`/`specmgr mcp-docs`
re-run, touching only the expected `docs/api/*.md` files for the six
changed `src` modules. Full quality gate green: `ruff format --check`
(1286 files already formatted), `ruff check` (all checks passed),
`vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest`
suite (2228 tests, OK, unchanged from Phase 5 — no new tests added),
`specmgr unused-code` (clean). Frontmatter `status` set back to `done`;
`version` bumped from `1.12.0` to `1.13.0`.

**As of 2026-08-30 (Phase 6 recorded, not started)**: A new `#### Phase
6: Frontmatter timestamp format fix` has been added to the Task List
(Task 6.1, not-started) to reverse this feature's own earlier deliberate
divergence and switch `feat` frontmatter's `created`/`updated` fields
from plain `YYYY-MM-DD` dates to microsecond timestamps, matching every
other whole-body domain. This is planning/recording only — no
`src`/`tests` code has been touched. The feature's frontmatter `status`
has reverted from `done` to `in-progress` to reflect this new,
not-yet-started follow-up work.

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

**As of 2026-08-30 (Phase 1 complete)**: `feat/models/v1/` is fully
implemented per Design Notes — `_util.py`, `frontmatter.py`
(`FeatFrontmatter`), `body.py` (`Feature`/`Plan`/`Progress` and every
child section class), `document.py` (`FeatDocument`), `parser.py`
(`parse_feat`), `summary.py` (`FeatSummary`), plus `models/v1/__init__.py`/
`models/__init__.py` exports. Reference fixture
`tests/feat/models/v1/data/feat_reference.md` seeded from `example.md`
(two small, content-preserving adjustments — loose lists, one shortened
task item — see Task 1.5/Decisions Made). 99 new tests
(`test_frontmatter.py`/`test_body.py`/`test_parser.py`) all green. Full
quality gate green: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean (after adding the new
`feat`-only field names and `_validate_newest_first`/
`_default_blank_status_to_planning` to `whitelist.py`, same pattern as
every other domain's pydantic-field/validator false positives),
`specmgr unused-code` clean, full `unittest` suite green (2106 tests).
Phase 2 (`feat/tools/`) is next.

**As of 2026-08-30 (Phase 2 complete)**: `feat/tools/` is fully
implemented — hand-rolled `_paths.py` (`feat_base_dir`/`ensure_feat_base_dir`,
`iter_feat_paths`, `find_feat_path_by_id`'s no-scan shortcut,
`FeatNotFoundError`, `feature_title()`, `FEAT_FOLDER_PATTERN`), `_lock.py`
(per-id `feat_lock` + global `feat_create_lock`), `_io.py` (`read_feat`,
`load_by_id`), `_write.py` (`write_feat_file`, folder-creating), and all 8
lifecycle tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`,
`get_feat_example`, `get_feat_template`, `delete_feat` stub, `validate_feat`)
plus `tools/__init__.py`. `general/tools/update.py`/`set_status.py` gained
`_update_feat`/`_set_status_feat` adapters and `"feat"` dispatch entries
(REQ-006) — `feat` is now a 9th `update` domain and a 10th `set_status`
domain, both with the same plain-date `updated` divergence `create_feat`
established. A full live create→get→list→update(whole-body)→
update(line-range)→set_status→get→list→validate→delete(stub) round-trip and
a 20-thread concurrent-create collision test both pass
(`tests/feat/tools/test_integration.py`). 73 new tests across
`tests/feat/tools/` (all green), plus one pre-existing test
(`tests/general/tools/test_update.py::TestUpdateRegistration`) updated for
the now-9-value `type` enum. Full quality gate green: `ruff format --check`/
`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean
(no new whitelist entries needed — every new tool function is reachable via
its domain's own `tools/__init__.py` `__all__` export, same as every other
domain), `specmgr unused-code` clean, full `unittest` suite green (2179
tests, up from 2106 after Phase 1). Phase 3 (resources + packaged data +
schema) is next — in
particular, `feat/data/feat_example.md`/`feat_template.md` (Task 3.1/3.2),
which `get_feat_example`/`get_feat_template` are already wired to read but
which don't exist on disk yet (both currently raise `FileNotFoundError`
when actually called; `tests/feat/tools/test_get_feat_example.py`/
`test_get_feat_template.py` document this explicitly and should be revisited
once Phase 3 ships those files).

**As of 2026-08-30 (Phase 3 complete)**: `feat/data/` and `feat/resources/`
are fully implemented — `feat_example.md` (byte-identical copy of
`tests/feat/models/v1/data/feat_reference.md`), `feat_template.md`
(all-sections placeholder skeleton, `status: planning`, round-trips
through `parse_feat`), `feat_create_instructions.md`/
`feat_update_instructions.md` (narrated instruction bodies for the
Phase-4 prompts, tailored to `feat`'s own schema/status set/no-
`update_feat`-of-its-own MCP surface), and `feat_schema.json` (both
`docs/feat_schema.json` and the packaged `feat/data/feat_schema.json`
copy, byte-identical, confirmed via `diff`). `commands/schema.py` gained
`generate_feat_schema()` and a `"feat"` entry in `_GENERATORS` (inserted
alphabetically between `"dec"` and `"gol"`). `feat/resources/` gained
`feat_schema.py`/`feat_example.py`/`feat_template.py`/`__init__.py`,
registering `specmgr://feat/schema`/`specmgr://feat/example`/
`specmgr://feat/template` (no `/{id}`, no `/list`), each a 1:1 mirror of
`dec.resources`' own three modules. The two Phase-2-deferred tool tests
(`tests/feat/tools/test_get_feat_example.py`/
`test_get_feat_template.py`) were updated to assert the real packaged-file
happy path instead of `FileNotFoundError`, now that the packaged files
exist. 20 new tests across `tests/feat/resources/` (all green), including
a byte-exact match between `specmgr://feat/example`'s output and the
Phase-1 reference fixture, a fresh-`generate_feat_schema()` parity check,
and a `parse_feat` structural round-trip for the template. Full quality
gate green: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean (no new whitelist entries needed),
`specmgr unused-code` clean, full `unittest` suite green (2199 tests, up
from 2179 after Phase 2). Phase 4 (`feat/prompts/`) is next.

**As of 2026-08-30 (Phase 4 complete)**: `feat/prompts/` is fully
implemented — `create_feat.py` (`create_feat(topic)`), `update_feat.py`
(`update_feat(id, instructions=None)`), `__init__.py`, each a 1:1 mirror
of `dec.prompts.create_dec`/`update_dec`: thin `string.Template` wrappers
that read the already-existing Phase-3 packaged instructions files
(`feat_create_instructions.md`/`feat_update_instructions.md`) and
substitute `$topic` / `$id`+`$instructions`, never calling
`TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/`update`/
`set_status` themselves. `update_feat`'s missing-`instructions` fallback
is the literal string `"(not given)"` (not DEC's longer
`"(not given -- ask the user before making any change)"`), matching
`feat_update_instructions.md`'s own step 2 check verbatim (`If "Requested
change" above says "(not given)"...`). 29 new tests across
`tests/feat/prompts/` (`test_create_feat.py`/`test_update_feat.py`), all
green: static string-content/ordering assertions mirroring
`tests/dec/prompts/`'s own depth, plus one "walk the instructions end to
end" test per prompt (ACC-006) that drives the real
`create_feat`/`get_feat`/`list_feat`/`update`/`set_status` tools against
a temporary `SPECMGR_FEAT_DIR` — `TestCreateFeatInstructionsWalkthrough`
follows step 0 (dedup check via `list_feat`) and step 4 (`create_feat`)
literally; `TestUpdateFeatInstructionsWalkthrough` creates a real
document, then follows `get_feat` → line-range `update` → whole-body
`update` → `set_status` exactly as the packaged update instructions
narrate, asserting the end state (status `progress`, 2 Requirements
items, id/created preserved). `tests/dec/prompts/` itself does not do
this deeper walk-through (static-text assertions only), so this is new
depth introduced for `feat` specifically, per ACC-006's explicit
requirement. `feat/__init__.py`'s module docstring updated to reflect
Phase 4 completion (only Phase 5 cross-cutting registration remains).
Full quality gate green: `ruff format --check`/`ruff check` clean,
`vulture src/ whitelist.py --min-confidence 60` clean (no new entries
needed), `specmgr unused-code` clean, full `unittest` suite green (2228
tests, up from 2199 after Phase 3). Phase 5 (cross-cutting registration)
is next.

**As of 2026-08-30 (Phase 5 complete — feature done)**: Cross-cutting
registration is complete and this feature is **done**. `server.py` gained
`feat` in the domain import line and a full set of module-docstring
updates (Resources block, "no `/{id}`/no `/list`" sentence, Tools
paragraph, Prompts paragraph, both `update`/`set_status` count bumps,
both domain-enumeration sentences). `pyproject.toml`/
`.pre-commit-config.yaml`/`.github/workflows/ci.yml` all gained their
`feat` entries (package-data, schema-hook globs + new
`specmgr-schema-feat-package` hook, CI drift step). `AGENTS.md` gained a
new `feat/` bullet plus every other domain-enumeration sentence updated;
root `README.md` gained `Feature (FEAT)` in its active artifact list and
(drive-by fix) `Risk (RSK)` moved out of the commented-out placeholder
alongside it, leaving only the not-yet-implemented `Acceptance Criterium
(ACC)` commented out (see Decisions Made). `specmgr docs`/`specmgr
mcp-docs`/`specmgr schema` (both invocations) were each run twice in a
row and confirmed idempotent — only `docs/api/biz.dfch.specmgr.server.md`
changed (from the `server.py` docstring edits themselves); `docs/MCP.md`
had zero diff, since every FEAT tool/resource/prompt was already fully
registered before this phase. Every ACC-001..009 was walked with concrete
evidence (tests, generated docs, live command output — see this update's
own detail below) and all nine are satisfied. Full quality gate green:
`ruff format --check` (1286 files already formatted), `ruff check` (all
checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
full `unittest` suite (2228 tests, OK, unchanged from Phase 4 — Phase 5
touched no `src/biz/dfch/specmgr/feat/` or `tests/feat/` code, only
cross-cutting registration files), `specmgr unused-code` (clean).
Frontmatter `status` set to `done`. **Per this phase's own task
instructions, no commit was made and no comment was posted to issue
#31** — that is the orchestrator's responsibility for this run, not the
implementing agent's.

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

#### Update 2026-08-30 (Phase 6 complete — frontmatter timestamp format fix implemented)

- **Implemented Task 6.1**: `feat` frontmatter's `created`/`updated`
  fields now use `datetime.now().isoformat(timespec="microseconds")`,
  the same microsecond ISO timestamp format every other whole-body
  domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`) already uses —
  reversing this feature's own earlier, deliberate plain-`YYYY-MM-DD`
  divergence.
- **3 `src` files enumerated by the task**, each edited at both the code
  and docstring level:
  - `feat/tools/create_feat.py`: the local `today = datetime.now().date().isoformat()` variable became `now = datetime.now().isoformat(timespec="microseconds")`
    (renamed to match `dec`/`gol`'s own `create_<d>.py` local-variable
    naming, checked first per the task's own instruction), used for both
    `created`/`updated` in the constructed `FeatFrontmatter`. Module
    docstring's "Timestamp format is a deliberate `feat`-only divergence"
    paragraph and the `create_feat()` docstring's "today's plain
    `YYYY-MM-DD` date" line both rewritten to describe the now-matching
    behavior.
  - `general/tools/update.py`'s `_update_feat` adapter: both the
    whole-body and line-range branches' `today = datetime.now().date().isoformat()` became `now = datetime.now().isoformat(timespec="microseconds")`,
    mirroring `_update_dec`'s exact pattern/variable naming. Module
    docstring and `_update_feat()`'s own docstring rewritten so `feat`'s
    only remaining stated divergence is addressing resolution (the
    bespoke `feat.tools._paths` folder-per-document shortcut), not
    timestamp format.
  - `general/tools/set_status.py`'s `_set_status_feat` adapter: same
    `today` → `now`/microsecond-timestamp change, mirroring
    `_set_status_dec`. Module docstring, `_set_status_feat()`'s own
    docstring, and the public `set_status()` docstring's "a plain
    `YYYY-MM-DD` date for `feat`, a microsecond timestamp for the other
    eight" sentence all rewritten to state every domain now shares one
    format.
- **Design Notes' "Frontmatter" section** (`.specmgr/feat/feat-31-feature/README.md`,
  this file) updated: the "`created`/`updated` stay plain `YYYY-MM-DD`
  ... a deliberate divergence" sentence now states `created`/`updated`
  use the same microsecond timestamp as every other domain, reversing
  the earlier stated divergence, with a pointer to this update's own new
  Decisions Made entry for the rationale — the historical context about
  the 17 pre-existing hand-authored feature files (still out of scope,
  unaffected by this change) is preserved, not deleted.
- **New Decisions Made entry added** (see below), explicit that this is
  a reversal of the earlier "`feat` frontmatter timestamps stay plain
  `YYYY-MM-DD`" decision, made as a follow-up after the feature initially
  shipped `done`, not part of the original five design-review rounds.
- **Beyond the task's own enumerated files**, also found and corrected
  four stale docstring/data-file mentions of the old plain-date behavior
  via the task's own suggested final grep
  (`grep -rn "date().isoformat\|YYYY-MM-DD" ...`), none of which were
  explicitly named in Task 6.1 but would otherwise have been left
  factually wrong: `feat/models/v1/frontmatter.py`'s module docstring
  ("the specific `YYYY-MM-DD` convention `feat` uses" → "the specific
  microsecond timestamp convention every domain, including `feat`,
  uses"); `feat/models/v1/body.py`'s `UpdateEntry` class docstring,
  which contrasts the body-level `### Updates`/`### Decisions Made`
  entry-heading ISO8601 format against frontmatter's format (updated the
  frontmatter-format description only — the body-level format itself is
  unchanged and stays deliberately different, per Design Notes); the
  `feat/prompts/create_feat.py` module docstring; and the packaged
  `feat/data/feat_create_instructions.md`/`feat_update_instructions.md`
  narrated-instruction text the `create_feat`/`update_feat` MCP prompts
  read verbatim (these are user/LLM-facing text, not just internal
  comments, so leaving them stale would have actively misled a caller
  following the prompts).
- **Regenerated `docs/feat_schema.json` and the packaged
  `feat/data/feat_schema.json` copy** (`specmgr schema --type feat` both
  ways, confirmed byte-identical via `diff`) since both embed the
  changed `UpdateEntry` docstring text verbatim. Re-ran `specmgr docs`
  (touched exactly the 6 expected `docs/api/*.md` files for the 6
  changed `src` modules, nothing else) and `specmgr mcp-docs` (zero
  further diff — no tool/resource/prompt registration text changed,
  only docstrings already reflected by the Task 5.1-era MCP.md).
- **2 existing tests updated, no new tests added** (per this phase's own
  "format fix, no new functionality" scope):
  `tests/feat/tools/test_create_feat.py`'s
  `test_builds_frontmatter_and_returns_document` regex assertion changed
  from `r"^\d{4}-\d{2}-\d{2}$"` to
  `r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$"`;
  `tests/feat/tools/test_integration.py`'s two equivalent `updated`-field
  regex assertions (whole-body `update` and `set_status` steps) updated
  the same way, plus the explanatory comment above the `update` step
  that referenced "a plain YYYY-MM-DD date, not the other domains'
  microsecond timestamp".
- Full quality gate green: `ruff format --check` (1286 files already
  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest` suite (2228 tests,
  OK — unchanged from Phase 5, since no new tests were added, only
  existing assertions changed), `specmgr unused-code` (clean, no unused
  code found).
- Frontmatter `status` set back to `done` (this was the only remaining
  not-done work); `version` bumped from `1.12.0` to `1.13.0`.
- Per this phase's own task instructions (implementer runs the gate
  only), **no commit was made** — that is the orchestrator's
  responsibility for this run.

#### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)

- Added a new `#### Phase 6: Frontmatter timestamp format fix` to the
  Task List, with one new task, **Task 6.1** (not-started): change
  `feat` frontmatter's `created`/`updated` fields from plain
  `YYYY-MM-DD` dates to microsecond timestamps
  (`datetime.now().isoformat(timespec="microseconds")`), matching every
  other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/
  `dec`) already in use — reversing this feature's own earlier
  deliberate divergence documented in Design Notes' "Frontmatter"
  section and in Decisions Made. The task calls out the affected files
  (`feat/tools/create_feat.py`, `general/tools/update.py`'s
  `_update_feat` adapter, `general/tools/set_status.py`'s
  `_set_status_feat` adapter, the Design Notes prose, and the tests
  asserting the plain-date format) and requires a new Decisions Made
  entry when the reversal is actually implemented, not a silent code
  change.
- Frontmatter `status` reverted from `done` to `in-progress` and
  `version` bumped from `1.11.0` to `1.12.0` to reflect this new,
  not-yet-started follow-up item.
- **This is planning/recording only — no `src`/`tests` code was
  touched.** Task 6.1 remains not-started; implementation is deferred to
  a future session.

#### Update 2026-08-30 (Phase 5 complete — cross-cutting registration; feature done)

- **`server.py` (Task 5.1)**: added `feat` to the domain import line
  (alphabetical: `adr, dec, feat, general, gol, prb, qa, req, rsk, tsk,
  uc`). Module docstring gained: a `specmgr://feat/schema`/`/example`/
  `/template` Resources block placed right after the `dec` block (same
  relative position `feat` occupies in the domain-enumeration
  elsewhere); a "FEAT has no `specmgr://feat/{id}` ... no
  `specmgr://feat/list`" sentence appended to the "DEC has no ..."
  paragraph; a new "Feature tools (`feat/tools/`)" paragraph in Tools
  mirroring "Decision tools" (verified `get_feat` does take
  `raw: bool = False`, matching every other domain, before writing this
  paragraph — checked `feat/tools/get_feat.py` directly per this task's
  own instruction), plus one extra sentence noting `feat`'s bespoke
  `_paths.py` addressing and its lack of `update_feat`/`set_status_feat`
  tools of its own; the `update`/`set_status` paragraphs' domain counts
  bumped from eight/nine to nine/ten whole-body/total domains (both
  `general/tools/update.py` and `set_status.py` had already made this
  exact bump to their own docstrings back in Phase 2, so this brought
  `server.py` in line with code that was already correct); a new
  "Feature prompts (`feat/prompts/`)" paragraph in Prompts mirroring
  "Decision prompts"; and `feat` inserted into both domain-enumeration
  sentences ("Modules are grouped domain-first ..." and "Add a new
  domain by ...") plus the final "each register `tools`, `resources`,
  and `prompts`" sentence.
- **Cross-cutting config (Task 5.2)**: `pyproject.toml` gained
  `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]` alphabetically
  between `dec` and `gol`. `.pre-commit-config.yaml`'s one shared
  `files:` regex glob (`^src/biz/dfch/specmgr/(dec/models/v1|gol/
  models/v1|...)/.*\.py$`) gained `feat/models/v1` between `dec/models/v1`
  and `gol/models/v1` in all 9 pre-existing occurrences (counted 9 before
  the edit, 9 after — a global find/replace, not a manual per-occurrence
  edit, so the count check was mostly a sanity confirmation) plus a new
  10th occurrence in the brand-new `specmgr-schema-feat-package` hook
  itself, which mirrors `specmgr-schema-dec-package` verbatim (id/name/
  description/entry/language/pass_filenames/files) and is placed last,
  matching this file's own insertion-order (not alphabetical) convention
  for per-domain schema-package hooks: `req, uc, tsk, rsk, qa, prb, gol,
  dec, feat`. `.github/workflows/ci.yml` gained a new
  `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` `` drift-check
  step, same `if: matrix.python-version == '3.13'` guard and
  `::error::...` message format as the existing `dec` step, placed
  immediately after it; the `docs/*_schema.json` step's own comment
  prose and the `specmgr-schema` pre-commit hook's description were both
  updated to name `feat` among the registered types.
- **`AGENTS.md`/root `README.md` (Task 5.3)**: added a new `**`feat/`**`
  bullet to `AGENTS.md`'s per-domain enumeration (between `dec/` and
  `general/`), at the same depth/style as `dec/`'s own, spelling out the
  addressing deviation explicitly (non-UUID `id`, folder-per-document,
  bespoke `feat/tools/_paths.py`, mandatory `SPECMGR_FEAT_DIR`, all 8
  tools, generic `update`/`set_status` dispatch, resources, prompts,
  `FeatSummary.path`). Updated every other domain-enumeration sentence in
  `AGENTS.md` that listed all current domains: the `general/` bullet's
  own whole-body/total domain counts (eight→nine, nine→ten) and `type`
  enumeration; the "Still genuinely missing" section's `validate_*`/
  `delete_*` lists and the register-all-three sentence; the "MCP server
  (server.py)" section's own domain-import-line description. Root
  `README.md`: added `Feature (FEAT)` to the active bulleted artifact
  list (alphabetically between `Decision (DEC)` and `Goal (GOL)`),
  removed the `Feature (FTR)` line from the commented-out placeholder
  block (the abbreviation was wrong there too — "FTR", not the actually-
  implemented "FEAT" — on top of being redundant now that FEAT is
  active), and, as a drive-by fix, moved `Risk (RSK)` out of the same
  placeholder into the active list since `AGENTS.md`'s own `rsk/` bullet
  confirms RSK has been a fully implemented, schema-backed domain for
  some time — only the not-yet-implemented `Acceptance Criterium (ACC)`
  stays commented out. Recorded as a new Decisions Made entry below.
- **Regeneration (Task 5.4)**: ran `specmgr docs`, `specmgr mcp-docs`,
  `specmgr schema`, and `specmgr schema --type feat --output-dir
  src/biz/dfch/specmgr/feat/data`, each twice in a row. `specmgr docs`
  changed only `docs/api/biz.dfch.specmgr.server.md` (reflecting the
  Task 5.1 docstring edits) on the first run and produced zero further
  diff on the second. `specmgr mcp-docs` produced no diff on either
  run — every FEAT tool/resource/prompt was already fully registered
  against the live `mcp` instance before this phase (Phases 2-4), so
  `docs/MCP.md` was already current; this phase's `server.py` docstring
  changes only affect `docs/api/`, not `docs/MCP.md`, which is generated
  from the actual tool/resource/prompt registrations, not the module
  docstring. `specmgr schema` (all 9 registered types) and the `feat`-
  only packaged-copy invocation both reported every file "(unchanged)"
  on both runs. Confirmed idempotent across the board.
- **Final verification (Task 5.5)** — ACC-001..009 walked with concrete
  evidence:
  - ACC-001: `tests/feat/models/v1/test_parser.py` exercises the full
    matrix (`TestParseFeatValueViolations`/`TestParseFeatStructuralViolations`)
    — malformed status/hyphenated status/wrong `type`, malformed
    `REQ-\d{3}`/`ACC-\d{3}` items, out-of-order `Updates` entries,
    unknown H2, missing `Requirements`, malformed `Phase`/`UpdateEntry`
    headings, zero-phase/zero-entry composites, leading content before
    H1, a second H1 — all raise, all covered. `docs/feat_schema.json`/
    `specmgr://feat/schema` (via `feat/resources/feat_schema.py`) both
    exist and are exercised by `tests/feat/resources/test_feat_schema.py`.
  - ACC-002: `tests/feat/tools/test__paths.py::TestFindFeatPathById`
    covers the direct-shortcut resolution, the id/folder-name-mismatch
    rejection (tool-layer, not model-layer), and the no-partial-match
    behavior; `tests/feat/tools/test_integration.py::
    TestCreateFeatConcurrencyIntegration::test_many_concurrent_create_feat_calls_never_collide`
    proves the global create-lock prevents two callers picking the same
    `NNN`.
  - ACC-003: all 8 tools exist, are registered (confirmed live in
    `docs/MCP.md`'s Tools section), and are exercised by
    `tests/feat/tools/test_integration.py::TestFeatLifecycleIntegration::
    test_full_lifecycle_roundtrip` (create→get→list→...→delete-stub→
    validate against a temp `SPECMGR_FEAT_DIR`); `list_feat` returns
    `PagedResult[FeatSummary]` per `tests/feat/tools/test_list_feat.py`.
  - ACC-004: the same integration test drives `update(type="feat", ...)`
    in both whole-body and line-range modes and `set_status(type="feat",
    ...)`, asserting `id`/`type`/`created`/`version` are preserved and
    only `updated`/`status` change.
  - ACC-005: `docs/MCP.md`'s Resources section lists exactly
    `specmgr://feat/schema`/`/example`/`/template`, no `/{id}`, no
    `/list`; `tests/feat/resources/` exercises all three live.
  - ACC-006: `tests/feat/prompts/test_create_feat.py::
    TestCreateFeatInstructionsWalkthrough`/`test_update_feat.py::
    TestUpdateFeatInstructionsWalkthrough` drive the real tools following
    the packaged instructions' own narrated steps end to end (not just
    static-text assertions), per this ACC's explicit requirement.
  - ACC-007: `diff`-verified byte-identical `docs/feat_schema.json` and
    `src/biz/dfch/specmgr/feat/data/feat_schema.json` (both freshly
    regenerated this phase); `tests/feat/resources/test_feat_schema.py::
    test_matches_fresh_generate_feat_schema_output` covers the same
    invariant at the test-suite level.
  - ACC-008: `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` all
    report zero drift (see Task 5.4 above); `AGENTS.md` reflects the new
    domain (this update); `feat-7-various-improvements` already carries
    Task 0.31 and its Task 0.30 background note already names `feat` as
    a fourth divergent variant (done in Phase 0, verified still present).
  - ACC-009: full `unittest` suite green (2228 tests, 221 of them under
    `tests/feat/`); `ruff format --check`/`ruff check` clean; `vulture
    src/ whitelist.py --min-confidence 60` clean; `specmgr unused-code`
    clean.
  Full quality gate re-run end to end, all green (see this update's own
  Current Status entry for exact command output). Frontmatter `status`
  set from `in-progress` to `done`.
- Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
- **This feature is now complete.** All 5 phases and all 11 requirements
  (REQ-001..011) are implemented, tested, and cross-registered; all 9
  acceptance criteria (ACC-001..009) are verified with concrete evidence.

#### Update 2026-08-30 (Phase 4 complete — prompts)

- Implemented `feat/prompts/` in full: `create_feat.py`
  (`create_feat(topic)`), `update_feat.py`
  (`update_feat(id, instructions=None)`), `__init__.py` — each a 1:1
  mirror of `dec.prompts.create_dec`/`update_dec`: thin `string.Template`
  wrappers around `general.tools._packaged_data.read_packaged_text`
  reading the already-existing Phase-3 packaged instructions files
  (`feat_create_instructions.md`/`feat_update_instructions.md`),
  substituting `$topic` (create) and `$id`/`$instructions` (update).
  Neither calls `TodoWrite`/`question`/`list_feat`/`get_feat`/
  `create_feat`/`update`/`set_status` themselves — they only narrate that
  sequence, matching every other prompt in this codebase.
- Judgment call: `update_feat`'s fallback for a missing `instructions`
  argument is the literal string `"(not given)"`, not DEC's own longer
  `"(not given -- ask the user before making any change)"` — verified
  `feat_update_instructions.md`'s step 2 checks for the literal substring
  `"(not given)"` (`If "Requested change" above says "(not given)", ask
  the user...`), so the fallback matches that check exactly rather than
  reusing DEC's wording verbatim.
- Updated `feat/prompts/__init__.py` to import and export both prompts
  (mirroring `dec/prompts/__init__.py`'s one-module-per-prompt shape) and
  `feat/__init__.py`'s module docstring to reflect Phase 4 completion
  (only Phase 5 cross-cutting registration remains).
- Wrote 29 new tests across `tests/feat/prompts/`
  (`test_create_feat.py`/`test_update_feat.py`) — all green: static
  string-content/ordering assertions mirroring `tests/dec/prompts/`'s own
  depth (topic/id/instructions substitution, packaged-file provenance,
  tool-call-sequence ordering, missing-file propagation), plus, per
  ACC-006's explicit requirement, one "walk the instructions end to end"
  test per prompt driving the real `create_feat`/`get_feat`/`list_feat`/
  `update`/`set_status` tools against a temporary `SPECMGR_FEAT_DIR`:
  `TestCreateFeatInstructionsWalkthrough` follows step 0 (dedup check via
  `list_feat`) and step 4 (`create_feat`) literally;
  `TestUpdateFeatInstructionsWalkthrough` creates a real document, then
  follows `get_feat` → line-range `update` → whole-body `update` →
  `set_status` exactly as the packaged update instructions narrate,
  asserting the end state. Checked `tests/dec/prompts/` first per this
  phase's own instructions — it only does static-text assertions, so this
  deeper walk-through is new depth introduced specifically for `feat`.
- Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2228
  tests, green, up from 2199 after Phase 3).
- Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
- Next: Phase 5 (cross-cutting registration) — `server.py` domain import,
  `pyproject.toml`/`.pre-commit-config.yaml`/CI wiring, `AGENTS.md`
  updates, regenerated docs, final verification pass, and setting the
  feature status to `done`.

#### Update 2026-08-30 (Phase 3 complete — resources, packaged data, schema)

- Implemented `feat/data/` in full: `feat_example.md` (a byte-identical
  copy of `tests/feat/models/v1/data/feat_reference.md`, confirmed via
  `diff`), `feat_template.md` (all-sections placeholder skeleton --
  `Dependencies` with both `Depends On`/`Blocks`, `Design Notes`,
  `Related Decisions`, `Blockers`, `Decisions Made`, `Related PRs /
  Commits`, `More Information` all present -- `status: planning`,
  round-trips through `parse_feat`), `feat_create_instructions.md`/
  `feat_update_instructions.md` (narrated instruction bodies mirroring
  `dec`'s/`gol`'s own two files, tailored to `feat`'s actual schema, its
  four-value hyphen-free status set, and its no-`update_feat`/
  `set_status_feat`-of-its-own generic-dispatch MCP surface), and
  `feat_schema.json` (both `docs/feat_schema.json` and the packaged
  `feat/data/feat_schema.json` copy, generated via `specmgr schema --type feat` and `specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data`, confirmed byte-identical via
  `diff`).
- `commands/schema.py` gained `generate_feat_schema()` (mirroring
  `generate_dec_schema()` exactly) and a `"feat"` entry in `_GENERATORS`,
  inserted alphabetically between the existing `"dec"` and `"gol"` keys.
- Implemented `feat/resources/`: `feat_schema.py`/`feat_example.py`/
  `feat_template.py`/`__init__.py`, each a 1:1 mirror of
  `dec.resources`' own three modules plus its `__init__.py`, registering
  `specmgr://feat/schema`/`specmgr://feat/example`/
  `specmgr://feat/template` (no `/{id}` -- id-based reads are
  `get_feat`-only; no `/list` -- listing is the `list_feat` tool).
  Updated `feat/__init__.py`'s module docstring to reflect Phase 3
  completion (data/resources populated, only `prompts` still empty).
- Replaced the two Phase-2-deferred tests
  (`tests/feat/tools/test_get_feat_example.py`/
  `test_get_feat_template.py`) with real "returns the packaged file"
  happy-path assertions (mirroring `test_get_dec_example.py`/
  `test_get_dec_template.py`), now that the packaged files they read
  actually exist on disk.
- Wrote 20 new tests across `tests/feat/resources/`
  (`test_feat_schema.py`/`test_feat_example.py`/`test_feat_template.py`)
  -- all green, including: `feat_schema` matches a fresh
  `generate_feat_schema()` output; `feat_example` is byte-identical to
  both the packaged file and the Phase-1 reference fixture, and
  round-trips through `parse_feat` byte-exact (re-verifying ACC-001 at
  this layer too, per this phase's own instructions) while exercising
  every optional section (`Dependencies` with both children,
  `Design Notes`, `Related Decisions`, `Blockers`, `Decisions Made`,
  `Related PRs / Commits`, `More Information`); `feat_template`
  successfully parses via `parse_feat` (structurally valid, `status: planning`) while exercising the same set of optional sections, without
  being required to be a "realistic" document.
- Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2199
  tests, green, up from 2179 after Phase 2).
- Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** -- that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
- Next: Phase 4 (`feat/prompts/`) -- `create_feat.py`
  (`create_feat(topic)`), `update_feat.py`
  (`update_feat(id, instructions=None)`), `__init__.py`, and
  `tests/feat/prompts/` (ACC-006).

#### Update 2026-08-30 (Phase 2 complete — tools, bespoke addressing)

- Implemented `feat/tools/` in full per Design Notes' Addressing section:
  - `_paths.py` — hand-rolled, ADR-style (not built on
    `general/tools/_doc_paths.py`): `feat_base_dir()`/`ensure_feat_base_dir()`
    (`SPECMGR_FEAT_DIR`, falling back to `.specmgr/feat`), `iter_feat_paths(base_dir)` (globs `<base>/*/README.md`), `find_feat_path_by_id(base_dir, id_)` (the no-scan `<base>/<id_>/README.md` shortcut — no partial-id
    matching), `FeatNotFoundError`, plus `feature_title()` (strips the
    literal `"Feature: "` prefix off `Feature.text`, needed because
    `Feature` declares no `title` computed field of its own, unlike
    `Phase`/`UpdateEntry`/`DecisionEntry`) and `FEAT_FOLDER_PATTERN`.
  - `_lock.py` — per-id `feat_lock(id_)` (identical shape to
    `dec_lock`/`adr_lock`) plus the new **global** `feat_create_lock()`
    (a single module-level `threading.Lock`, no per-id registry needed).
  - `_io.py`/`_write.py` — `read_feat`/`load_by_id` (mirrors `dec.tools._io`
    file-for-file) and `write_feat_file` (mirrors `dec.tools._write`, plus
    `path.parent.mkdir(parents=True, exist_ok=True)` since `feat` is
    folder-per-document).
  - The 8 lifecycle tools + `tools/__init__.py`: `create_feat` (derives
    `feat-NNN-slug` under the global create lock, plain-date
    `created`/`updated`), `parse_feat`, `list_feat`
    (`PagedResult[FeatSummary]`, `path`/`ref` populated from the real
    resolved path), `get_feat(id, raw=False)`, `get_feat_example`/
    `get_feat_template` (wired to the shared packaged-data reader, though
    the packaged files themselves are Phase 3's job), `delete_feat` (stub),
    `validate_feat`.
- `general/tools/update.py`/`set_status.py` gained `_update_feat`/
  `_set_status_feat` adapters and `"feat"` dispatch table entries (REQ-006)
  — `feat` is now included in both tools' `type` `Literal`/dispatch table,
  with the same plain-`YYYY-MM-DD`-date `updated` divergence `create_feat`
  established (not the other domains' microsecond timestamp). Updated both
  modules' module-level docstrings' domain-count prose (8→9 for `update`,
  9→10 for `set_status`).
- Updated one pre-existing test,
  `tests/general/tools/test_update.py::TestUpdateRegistration`, whose
  hardcoded 8-value `type` enum assertion against the live `mcp` tool
  registration needed `"feat"` added (now 9 values).
- Wrote 73 new tests across `tests/feat/tools/` (`test__paths.py`,
  `test__lock.py`, `test__io.py`, `test__write.py`, `test_create_feat.py`,
  `test_get_feat.py`, `test_list_feat.py`, `test_parse_feat.py`,
  `test_validate_feat.py`, `test_delete_feat.py`,
  `test_get_feat_example.py`, `test_get_feat_template.py`,
  `test_integration.py`) — all green, including a live full
  create→get→list→update(whole-body)→update(line-range)→set_status→get→
  list→validate→delete(stub) round-trip and a 20-thread concurrent-`create_feat` collision test (ACC-002/ACC-003/ACC-004).
- Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
  needed), `specmgr unused-code` (clean), full `unittest` suite (2179
  tests, green, up from 2106 after Phase 1).
- Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
- Next: Phase 3 (`feat/resources/` + `feat/data/` + schema command) —
  `feat_example.md`/`feat_template.md` (byte-identical copy of
  `feat_reference.md` / all-sections placeholder skeleton),
  `feat_create_instructions.md`/`feat_update_instructions.md`,
  `generate_feat_schema()`, and the three `specmgr://feat/*` resources.
  `get_feat_example`/`get_feat_template` are already wired to read the
  packaged files that Phase 3 ships — no further tool-layer changes needed
  once those files exist, only the two currently-deferred tests
  (`test_get_feat_example.py`/`test_get_feat_template.py`) need their
  "real packaged file" happy-path test added back in.

#### Update 2026-08-30 (Phase 1 complete — models + parser)

- Implemented `feat/models/v1/` in full: `_util.py`
  (`SCHEMA_COMMENT_VERSION = "v1"`), `frontmatter.py` (`FeatFrontmatter`,
  closed 4-set status, `"planning"` default overriding the base's
  `"draft"`, mirroring `rsk.RskFrontmatter`'s `_default_blank_status_to_open`
  pattern), `body.py` (`Feature`/`Plan`/`Progress` and all 20 child section
  classes per Design Notes, including the `RequirementItem`/
  `AcceptanceCriterionItem` computed-field regexes, `Phase`'s
  `number`/`title` computed fields, `UpdateEntry`/`DecisionEntry`'s shared
  ISO8601 `timestamp`/`title` computed fields and `@alias` regex, and the
  newest-first `@model_validator` on `Updates`/`DecisionsMade`),
  `document.py` (`FeatDocument`), `parser.py` (`parse_feat`), `summary.py`
  (`FeatSummary(DocSummary)` + `path: str`), and the `models/v1/__init__.py`/
  `models/__init__.py` exports.
- Verified, live, that the "no `LITERAL` needed" claims in Design Notes for
  `Plan`/`Progress`/`RelatedDecisions`/`ExplicitlyOutOfScope`/`DependsOn`
  all hold against the real `space_separated_name()` engine function before
  writing any code — only `RelatedPrsCommits` needed the documented
  `LITERAL` override.
- Seeded `tests/feat/models/v1/data/feat_reference.md` from
  `.specmgr/feat/feat-31-feature/example.md` per Task 1.5, with two small,
  content-preserving adjustments needed to satisfy the generic `models/md`
  engine's own existing constraints (both recorded as Decisions Made
  entries below, not schema changes): every bullet/checklist list became a
  loose list (blank line between items), and Task 0.1's item text dropped
  its wrapped `— status: completed (2026-08-30)` suffix.
- Added one design decision beyond Design Notes' literal text:
  `Requirements`/`AcceptanceCriteria`/`Phase` each gained an eager-
  computed-field-validation `@model_validator`, mirroring
  `tsk.models.v1.body.Task._validate_items_eagerly` exactly, so a malformed
  item raises immediately at parse time (see Decisions Made).
- Wrote 99 new tests across `test_frontmatter.py` (11)/`test_body.py`
  (70)/`test_parser.py` (18); all green.
- Quality gate: `ruff format --check` (clean), `ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean, after adding
  `feat`'s new pydantic-field/validator names to `whitelist.py`, same
  false-positive pattern already documented there for every other
  domain), `specmgr unused-code` (clean), full `unittest` suite (2106
  tests, green).
- Per this phase's own task instructions, **no commit was made and no
  comment was posted to issue #31** — that is the phase orchestrator's
  responsibility, not the implementing agent's, for this run.
- Next: Phase 2 (`feat/tools/`) — bespoke addressing (`_paths.py`,
  `_lock.py`, `_io.py`, `_write.py`), the 8 MCP tool modules, and the
  generic `update`/`set_status` dispatch adapters.

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
- **2026-08-30 (Phase 1)**: `Requirements`/`AcceptanceCriteria`/`Phase`
  each gained their own eager-computed-field-validation
  `@model_validator`, mirroring `tsk.models.v1.body.Task._validate_items_eagerly`
  exactly, even though Design Notes' text for these three classes only
  says the computed field itself "raises `AssertionError` on a malformed
  item" without spelling out *when* that check fires. Without an eager
  validator, `RequirementItem.description`/`AcceptanceCriterionItem. criterion_description`/`TaskItem.checked` (all `@computed_field`s) would
  only be evaluated lazily, on first access (e.g. during `model_dump()`),
  matching `tsk.TaskItem`'s own well-documented gap before `Task` gained
  its eager validator — letting a malformed item parse silently and only
  fail (if ever) later, which would contradict ACC-001's stated
  requirement that a malformed list item raise immediately. Chosen to
  keep `feat` consistent with the one other domain (`tsk`) that already
  faced this exact tradeoff, rather than leaving `feat` as a second,
  inconsistent instance of the same gap.
- **2026-08-30 (Phase 1)**: `feat_reference.md` needed two small,
  content-preserving adjustments beyond "seeded from `example.md`",
  neither a schema change: (1) every bullet/checklist list in the fixture
  became a loose list (blank line between items) to avoid
  `MarkdownListItem`'s own documented "a tight source list currently
  round-trips to a structurally-equivalent loose list rather than
  byte-exact" limitation — `dec`'s own `_REFERENCE_TEXT` already uses this
  same loose-list workaround, so this isn't a new pattern. (2) Task 0.1's
  item text (`"Create branch and package skeleton — status: completed (2026-08-30)"` in `example.md`) had its trailing `— status: completed (2026-08-30)` suffix dropped, since that text wraps across two physical
  lines after `mdformat` normalization and `TaskItem`'s marker regex
  (`^\[( |x|X)\]\s*(?P<description>.*)$`, no `re.DOTALL`/`re.MULTILINE`)
  does not span an embedded newline — the same reason `tsk`'s own shipped
  `tsk_example.md` keeps every task item to a single physical line. Both
  adjustments are fixture-only; no schema/model code changed to
  accommodate them.
- **2026-08-30 (Phase 1)**: `feat_reference.md` lives at
  `tests/feat/models/v1/data/feat_reference.md` (a real file on disk), not
  inlined as a `format_text("""...""")` string constant the way `tests/dec/ models/v1/test_body.py`'s own `_REFERENCE_TEXT`/`test_parser.py`'s
  `_FULL_DOC` are. Task 1.5 explicitly named this path, and `tests/dec/ models/v1/` genuinely has no separate fixture file to "match exactly"
  (checked first, per the task's own instruction) — but
  `tests/models/adr/v1/examples/*.md` (loaded via
  `Path(__file__).parent / "examples"` in `test_examples.py`/
  `test_renderer.py`) and `tests/fixtures/req/test-loose-list-with- continuation.md` both establish that file-based markdown fixtures are
  an existing, precedented pattern in this codebase, just not one `dec`
  happens to use. `test_body.py`/`test_parser.py` both load the same file
  (`Path(__file__).parent / "data" / "feat_reference.md"`, mirroring the
  ADR examples' own path-resolution shape) rather than duplicating the
  reference text as two separate inline constants.
- **2026-08-30 (Phase 2)**: `feat_create_lock()` is an in-process
  `threading.Lock` (a single module-level instance, mirroring `adr_lock`'s/
  `dec_lock`'s own per-id primitive but with no per-id registry, since
  there is exactly one such shared resource — the base directory's own
  folder listing), **not** an on-disk lock file at `<base>/.create.lock` —
  a deliberate deviation from this plan's own Design Notes prose (Addressing
  section), which literally suggested "a single lock file". Checked the
  actual codebase precedent first (`adr.tools._lock.adr_lock`,
  `dec.tools._lock.dec_lock`, and every other domain's own per-id lock):
  every one of them is in-process only, none uses a real lock file: `feat`
  follows that established precedent for consistency, rather than
  introducing a new on-disk-lock-file mechanism this codebase has never
  used before. This is still process-local only (does not protect against
  a second OS process or a human editor writing concurrently), matching
  every other domain's own stated threat model.
- **2026-08-30 (Phase 2)**: `find_feat_path_by_id`'s shortcut read treats a
  parse failure on the single target file (`AssertionError`/
  `pydantic.ValidationError`) the same as the file not existing at all --
  both raise `FeatNotFoundError`, distinguished only by message text ("does
  not exist" vs. "could not be parsed" vs. "does not match the containing
  folder"). Every other domain's `find_*_path` *scans* multiple files and
  *skips* one that fails to parse so a single broken file never blocks
  finding a different, valid id -- but `feat`'s shortcut only ever reads one
  path, so there is no "different file" to fall back to; a parse failure
  here is exactly as unresolvable as a missing file. Chosen so
  `load_by_id`/`get_feat`/every mutating tool built on this module has one
  single, consistent not-found-shaped error to handle, without needing to
  separately catch `AssertionError`/`ValidationError` themselves --
  verified via `tests/feat/tools/test__paths.py`'s own
  `test_raises_not_found_for_unparseable_folder`/
  `test_raises_not_found_for_id_folder_mismatch` cases.
- **2026-08-30 (Phase 2)**: Added `feature_title()` to `_paths.py` (not
  spelled out in Design Notes) to strip the literal `"Feature: "` prefix
  off `Feature.text` before slugifying (`create_feat`) or populating
  `FeatSummary.title` (`list_feat`) -- `Feature.text` (the heading text a
  composite `MarkdownSection` exposes) always includes the literal prefix,
  since `Feature`'s own `@alias` regex (`"^Feature: .+$"`) matches the
  *whole* heading line and `Feature` declares no `title` computed field of
  its own (unlike `Phase`/`UpdateEntry`/`DecisionEntry`, each of which do).
  Without this, every created folder's slug would carry a redundant
  `feature-` prefix (e.g. `feat-1-feature-example-widget` instead of
  `feat-1-example-widget`), and `FeatSummary.title` would carry the
  `"Feature: "` prefix twice over conceptually — once in the field's own
  intent ("the free-form title") and once literally in the string, per
  `feat/models/v1/summary.py`'s own docstring wording ("the free-form title
  after the `"Feature: "` prefix, i.e. `Feature.text`"), which this
  resolves literally rather than leaving as an unresolved discrepancy
  between that docstring and the model's actual runtime behavior.
- **2026-08-30 (Phase 2)**: `get_feat_example`/`get_feat_template` are
  wired to `read_packaged_text("feat", "example"/"template")` exactly like
  every other domain's equivalent tool, even though `feat/data/ feat_example.md`/`feat_template.md` don't exist until Phase 3 (Task
  3.1/3.2) -- so both tools currently raise `FileNotFoundError` when
  actually called. Chose to write the tools now (per Task 2.3's own
  instruction) rather than defer them entirely, and to defer only their
  "returns the real packaged file" happy-path *test* to Phase 3
  (`tests/feat/tools/test_get_feat_example.py`/
  `test_get_feat_template.py` document this explicitly and assert the
  current, honest `FileNotFoundError` behavior instead) -- this keeps the
  tool surface complete and registrable in Phase 2 while being transparent
  that its two data-backed tools are not yet fully functional until Phase
  3 ships their packaged files.
- **2026-08-30 (Phase 3)**: `feat_template.md`'s placeholder frontmatter
  `id` is `feat-0-template` (a `feat-NNN-slug`-shaped placeholder, `NNN=0`
  since real ids start at `1` per `create_feat`'s own derivation), not a
  UUID-shaped placeholder like GOL's `deaddead-goal-goal-goal-deaddeadgoal`
  or DEC's `deadbeef-dead-dead-dead-deadbeefdead` -- `feat`'s own id
  convention is the folder name, not a UUID (REQ-004), so a UUID-shaped
  placeholder would be actively misleading here; `parse_feat` performs no
  path/folder-name check at the model layer (that invariant is
  tool-layer-only, per REQ-003), so this placeholder id parses without
  needing a matching `feat-0-template/` folder to exist anywhere.
- **2026-08-30 (Phase 3)**: `generate_feat_schema()`'s `_GENERATORS` entry
  was inserted alphabetically between the pre-existing `"dec"` and
  `"gol"` keys (`dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`,
  `uc`) -- confirmed the dict's existing order was alphabetical by
  doc-type name before inserting, rather than assuming insertion-order
  (e.g. "in Task-List/registration order") was the convention.
- **2026-08-30 (Phase 3)**: `feat_template.md` exercises every optional
  section listed in Task 3.2 (`Dependencies` with both `Depends On`/
  `Blocks`, `Design Notes`, `Related Decisions`, `Blockers`,
  `Decisions Made`, `Related PRs / Commits`, `More Information`) with one
  entry each for `Updates`/`Decisions Made` (not two, unlike
  `feat_example.md`/`feat_reference.md`) -- the template's job (per this
  phase's own task description) is to be a structurally-valid, every-
  section-present starting skeleton, not to additionally exercise
  multi-entry newest-first ordering the way the reference fixture/example
  already does; a single entry per dynamic list is enough to prove the
  section round-trips through `parse_feat` while keeping the template
  short, matching DEC's/GOL's own single-entry template precedent.
- **2026-08-30 (Phase 4)**: `update_feat`'s missing-`instructions`
  fallback string is exactly `"(not given)"`, not DEC's own longer
  `"(not given -- ask the user before making any change)"` -- checked
  `feat_update_instructions.md`'s own step 2 wording first (`If "Requested
  change" above says "(not given)", ask the user what they want to
  change before calling any write tool`), which checks for the literal
  substring `"(not given)"`, not DEC's longer phrase. Using DEC's own
  fallback text verbatim would still satisfy that literal check (it
  contains `"(not given"` as a prefix but not the closing `")"`
  immediately after -- DEC's phrase is `"(not given -- ..."`, which does
  **not** contain the exact substring `"(not given)"` with a closing
  paren right after "given"), so DEC's wording would silently fail
  `feat_update_instructions.md`'s own literal check. Chose to match what
  the packaged instructions file actually expects, per this phase's own
  task instructions, rather than blindly copying DEC's prose.
- **2026-08-30 (Phase 4)**: `tests/feat/prompts/` adds a genuine "walk the
  instructions end to end" test per prompt (ACC-006's explicit
  requirement), going beyond `tests/dec/prompts/`'s own static-text-only
  depth -- checked `tests/dec/prompts/test_create_dec.py`/
  `test_update_dec.py` first (per this phase's own task instructions) and
  confirmed neither does this: both are entirely string-content/ordering
  assertions on the returned instructional text, never driving the actual
  `create_dec`/`get_dec`/`update`/`set_status` tools. `feat`'s own
  `TestCreateFeatInstructionsWalkthrough`/
  `TestUpdateFeatInstructionsWalkthrough` instead drive the real tool
  functions (`create_feat`, `get_feat`, `list_feat`, the generic `update`/
  `set_status` with `type="feat"`) against a temporary `SPECMGR_FEAT_DIR`,
  following the packaged instructions' own narrated steps literally, to
  prove the narration is an actually-followable, correct sequence and not
  just plausible text -- new test depth introduced specifically for
  `feat`, not a retroactive change to `dec`'s own test suite (out of
  scope here).
- **2026-08-30 (Phase 5)**: Root `README.md`'s artifact list gains
  `Feature (FEAT)` -- added to the active bulleted list, alphabetically
  between `Decision (DEC)` and `Goal (GOL)` -- because, as of this
  feature's completion, `feat` is a fully schema-backed,
  MCP-tool-addressable artifact type exactly like every other one already
  in that list (8 MCP tools, 3 resources, 2 prompts, a JSON Schema, a
  packaged example/template), not a purely internal/meta concept the way
  the pre-existing placeholder comment implied. The placeholder's
  `Feature (FTR)` line is removed entirely (both because it is now
  redundant with the new active entry, and because "FTR" was never the
  abbreviation actually used anywhere in code/docs -- every tool,
  resource, and this very plan itself use "FEAT"). As a drive-by fix,
  `Risk (RSK)` -- also sitting in that same commented-out placeholder --
  is moved into the active list alongside `Feature (FEAT)`, since
  `AGENTS.md`'s own `rsk/` bullet confirms RSK has been a complete,
  shipped domain (tools/resources/prompts/schema) since `feat-15-add-
  artifact-type-risk`, well before this feature started; leaving it
  commented out any longer would have been stale documentation, not a
  deliberate scoping choice. `Acceptance Criterium (ACC)` stays commented
  out -- `AGENTS.md`'s "Still genuinely missing" section confirms no `ac`
  domain exists yet.
- **2026-08-30 (Phase 6)**: **Reversed** the earlier "`feat` frontmatter
  timestamps stay plain `YYYY-MM-DD`, matching the 17 hand-authored
  files" decision (recorded in Design Notes' "Frontmatter" section and
  implicit in the "Frontmatter `version` becomes schema-version-only"
  entry's era, above). `feat`'s `created`/`updated` now use the same
  microsecond ISO timestamp format
  (`datetime.now().isoformat(timespec="microseconds")`) as every other
  whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`), for
  consistency across the codebase. This was a follow-up decision made
  after the feature initially shipped `done` (Phase 5) -- not part of
  the original five design-review rounds -- prompted by the divergence
  proving more disruptive in practice than anticipated (every generic
  cross-domain tool/adapter and every piece of `feat`-facing narration
  had to carry an explicit "except `feat`, which uses a plain date"
  caveat). The 17 pre-existing hand-authored feature files this
  divergence originally matched remain untouched and out of scope (see
  Scope) -- this reversal only affects documents created/updated via the
  `feat` MCP tools (`create_feat`, the generic `update`/`set_status`
  with `type="feat"`) going forward, not any file already on disk.

### Related PRs / Commits

- [Issue #31](https://github.com/dfch/biz.dfch.SpecMgr/issues/31): Formalize
  the Feature artifact type ("feat")
- (Phase 0 baseline commit not yet made)
  </content>
