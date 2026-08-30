---
created: 2026-08-30
id: feat-31-feature
status: planning
updated: 2026-08-30
version: 1.0.0
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
  `## Plan` composite with mandatory leaf `### Overview`/`### Requirements`/
  `### Acceptance Criteria`/`### Scope`, optional leaf `### Dependencies`/
  `### Design Notes`/`### Related ADRs`, mandatory leaf `### Task List`;
  `## Progress` composite with mandatory leaf `### Current Status`, optional
  leaf `### Blockers`, mandatory composite `### Updates` (ISO8601-timestamped
  `#### {timestamp} — {title}` entries, ≥1), optional leaf
  `### Decisions Made`/`### Related PRs / Commits`).
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
  flat-file `general/tools/_doc_paths.py`): base directory `.specmgr/feat`
  (overridable via `SPECMGR_FEAT_DIR` for test isolation), documents at
  `<base>/<id>/README.md`. Since `id` is the folder name by convention,
  `find_feat_path_by_id` shortcuts straight to `<base>/<id>/README.md` and
  verifies the frontmatter `id` matches (raising `FeatNotFoundError`
  otherwise) instead of a full directory scan. `create_feat` derives the next
  `NNN` by scanning existing `feat-*` folder names under a **global**
  create-lock (distinct from every other domain's per-id lock, since the id
  doesn't exist yet when the lock must be taken).
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
  sections present, ≥2 `### Updates` entries) round-trips through
  `parse_feat` byte-exact; `FeatFrontmatter.status` rejects any value outside
  the 4-set; malformed `#### {timestamp} — {title}` headings raise
  `AssertionError`.
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
- Structured modeling of Task List `#### Phase N` / task-checklist content —
  stays a single opaque leaf section, like `### Design Notes`/
  `### Dependencies`; individual task-checkbox edits are expected to go
  through the generic `update` tool's line-range mode, not a dedicated tool.
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
  ### Requirements                             REQUIRED (leaf)
  ### Acceptance Criteria                      REQUIRED (leaf)
  ### Scope                                    REQUIRED (leaf)
  ### Dependencies                             OPTIONAL (leaf)
  ### Design Notes                             OPTIONAL (leaf)
  ### Related ADRs                             OPTIONAL (leaf)
  ### Task List                                REQUIRED (leaf, opaque)
## Progress                                    REQUIRED (LITERAL alias, composite)
  ### Current Status                           REQUIRED (leaf)
  ### Blockers                                 OPTIONAL (leaf)
  ### Updates                                  REQUIRED (composite, ISO8601)
    #### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}
    {entry prose}
  ### Decisions Made                           OPTIONAL (leaf)
  ### Related PRs / Commits                    OPTIONAL (leaf)
```

**Model classes** (all in `feat/models/v1/body.py`, one
`MarkdownSection1`/`MarkdownSection2`/`MarkdownSection3`/`MarkdownSection4`
subclass per heading; implicit SPACE_SEPARATED aliases unless noted):

- `Feature(MarkdownSection1)` — `@alias(value="^Feature: .+$", type=AliasType.REGEX)`; fields in order: `plan`, `progress`.
- `Plan(MarkdownSection2)` — implicit alias "Plan"; fields in order:
  `overview`, `requirements`, `acceptance_criteria`, `scope`,
  `dependencies | None`, `design_notes | None`, `related_adrs | None`,
  `task_list`.
- `Overview`, `Requirements`, `AcceptanceCriteria`, `Scope`, `Dependencies`,
  `DesignNotes`, `RelatedAdrs`, `TaskList` — bare opaque leaves
  (`MarkdownSection3`), implicit SPACE_SEPARATED aliases (RSK's
  `Cause`/`Trigger`/GOL's `Description` precedent). `TaskList` deliberately
  stays a leaf — the highly variable inline `depends on:`/`status:`/`ETA`
  annotations inside `#### Phase N` sections are not worth structurally
  modeling (see Scope).
- `Progress(MarkdownSection2)` — implicit alias "Progress"; fields in order:
  `current_status`, `blockers | None`, `updates`, `decisions_made | None`,
  `related_prs_commits | None`.
- `CurrentStatus`, `Blockers`, `DecisionsMade`, `RelatedPrsCommits` — bare
  opaque leaves (`MarkdownSection3`), implicit SPACE_SEPARATED aliases
  (`RelatedPrsCommits` → "Related PRs / Commits" needs an explicit
  `@alias(value="Related PRs / Commits", type=AliasType.LITERAL)` — the
  slash/mixed-case breaks the plain SPACE_SEPARATED convention, same
  reasoning as SOP's `SafetyAndPrecautions`).
- `Updates(MarkdownSection3)` — implicit alias "Updates"; `updates: list[UpdateEntry] = Field(min_length=1)`. One heading level deeper than
  `feat-30-sop`'s planned `## Updates` (`MarkdownSection2`), otherwise
  identical shape.
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
- [ ] Task 0.2: Package skeleton — `feat/__init__.py` (`from . import prompts, resources, tools` + registration docstring), empty
  `feat/models/v1/`, `feat/tools/`, `feat/resources/`, `feat/prompts/`,
  `feat/data/` packages, and `tests/feat/` skeleton mirroring `tests/dec/`
  — depends on: Task 0.1 — status: not-started
- [ ] Task 0.3: Add Task 0.31 to `feat-7-various-improvements` (migrate
  existing feature folders once this schema ships) and extend that
  feature's Task 0.30 background note to mention `feat`'s `### Updates`
  shape as a fourth divergent variant — depends on: none — status:
  not-started
- [ ] Task 0.4: Phase-end quality gate + baseline commit + comment the
  commit hash on issue #31 — depends on: Task 0.2, Task 0.3 — status:
  not-started

#### Phase 1: Models + parser (`feat/models/v1/`)

- [ ] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on:
  Task 0.2 — status: not-started
- [ ] Task 1.2: `frontmatter.py` — `FeatFrontmatter(MarkdownFrontmatter)`:
  `type: Literal["feat"] = "feat"`, closed 4-set status validator, default
  `"planning"` — depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: `body.py` — all section classes per Design Notes:
  `Feature` (root), `Plan` + its 8 children (7 leaves + `TaskList` leaf),
  `Progress` + its 5 children (`Updates` composite + `UpdateEntry`, 4
  leaves) — depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: `document.py` (`FeatDocument`), `parser.py` (`parse_feat`
  glue), `summary.py` (`FeatSummary(DocSummary)`), `models/v1/__init__.py`
  - `models/__init__.py` exports — depends on: Task 1.3 — status:
    not-started
- [ ] Task 1.5: Reference fixture `feat_reference.md` exercising every
  field (all optional sections present, ≥2 `### Updates` entries with
  well-formed and it must exercise the ISO8601 regex) — depends on: Task
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

**As of 2026-08-30**: Planning complete. GitHub issue #31 filed, branch
`feat-31-feature` created off `dev`, this plan written and reviewed with the
user across several rounds (body-modeling depth, addressing scheme, frontmatter
`version` semantics, status vocabulary, `Updates` shape/naming, MCP surface
scope, no-migration decision, branch naming, feat-7 backlog entry). Phase 0
scaffolding (package skeleton, feat-7 backlog task) not yet started.

### Blockers

None.

### Recent Updates

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
- **2026-08-30**: Body sections stay mostly opaque leaves (Overview,
  Requirements, Acceptance Criteria, Scope, Dependencies, Design Notes,
  Related ADRs, Task List, Current Status, Blockers, Decisions Made,
  Related PRs/Commits) — only `### Updates` gets real structure (H4 dynamic
  list, ISO8601-enforced heading).
- **2026-08-30**: `### Updates` (not `### Recent Updates`), ISO8601-enforced
  `#### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}` heading regex, copied
  from `feat-30-sop`'s plan one heading level deeper (H3/H4 instead of
  H2/H3, since it sits under `## Progress` not directly under the H1).
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

### Related PRs / Commits

- [Issue #31](https://github.com/dfch/biz.dfch.SpecMgr/issues/31): Formalize
  the Feature artifact type ("feat")
- (Phase 0 baseline commit not yet made)
  </content>
