---
status: accepted
date: '2026-08-05'
decision-makers: dfch
id: e369ee2e-3353-4f92-991c-6367d76d832e
version: 1.0.0
---

# Organize development artifacts in `.specmgr` with feature-driven work units

## Context and Problem Statement

The project maintains two documentation folders with an unclear split: `docs/` — published, generated documentation (API docs, ADRs, specifications), which reflects the current state of the project — and `doc/` — development progress notes, planning artifacts, research, which has no clear ongoing purpose once this ADR's structure exists. As part of adopting this ADR's outcome, `doc/` is dissolved: its content is migrated (manually, see Consequences) into the new structure below, and the `doc/` folder is retired. Development artifacts (plans, progress tracking, work-unit status) need a structured, agent-friendly location that is: (1) separate from published documentation (`docs/`); (2) organized by feature/work-unit for easy agent reference; (3) generic enough to serve as a template for future projects using specmgr as a toolkit.

## Decision Drivers

- Agent-friendly reference paths: agents should reference specific feature paths inline (e.g., "See `.specmgr/feat/feat-001-adr-toc/README.md`"), keeping agent instructions lean and focused
- Toolkit reusability: structure should be generic enough for future projects adopting specmgr as a toolkit — the folder name itself (`.specmgr/`) is chosen for this reason, following the convention of tool-named dotfolders like `.github/`, `.vscode/`, `.docker/`
- Clear separation of concerns: development artifacts must be distinct from published documentation
- Version control and auditability: development progress should be tracked in git with full history

## Considered Options

- Single README.md per feature containing both plan and progress
- Separate README.md (plan) and progress.md (status) per feature

## Decision Outcome

**Chosen option: "Option 1: .specmgr structure"** — a single `README.md` per feature combining plan and progress, with an optional sibling `history.md` for rotating out older `Recent Updates` entries. Every feature `README.md` also carries a minimal YAML frontmatter block (`id`, `version`, `status`, `created`, `updated` — see that option's "Frontmatter" note for details). There is no separate `GitHub Issue` field or body line: the issue number is the `NNN` infix already embedded in `id` (the folder name, `feat-NNN-slug`) itself.

This is preferred over Option 2 (separate `README.md`/`progress.md`) for its simplicity: one file per feature, no cross-file cross-referencing needed to see the full feature story, and the single canonical Task List (status inline per task) removes the Implementation Plan/Execution Plan duplication that Option 2 still carries. See "Pros and Cons of the Options" below for the full tradeoff analysis, and that option's "Open Questions" for points intentionally left open for later decisions.

### Consequences

**Positive:**
- Agents can reference specific feature paths inline, keeping instructions lean and focused
- Clear separation: agents only read what's relevant to their task
- Structure is reusable for future projects adopting specmgr as a toolkit
- Development progress is version-controlled and auditable
- The `.specmgr/` folder (and its `feat/` work units) is committed to git like any other tracked path in the repo — no `.gitignore` exclusion — so history and review apply to it the same way they do to `docs/` and source code

**Negative:**
- Adds another top-level folder to the repo structure
- Requires discipline to keep progress sections updated (hand-maintained, not auto-generated)
- Migrating `doc/`'s existing content (e.g. `doc/adr-tool-plan.md`, `doc/refactor-domain.md`) into the new structure is done manually, one file at a time, once this ADR is adopted — no automated migration tooling is planned

**Numbering convention:**
- `feat-NNN-slug` — `NNN` is the GitHub issue number for feature work tied to an issue. There is no separate `github_issue` frontmatter field or body line: `id` (the folder name itself) is the single source of truth for the issue number, read by parsing its `NNN` infix.
- Work started without a GitHub issue yet uses `feat-0-slug` (issue number `0`) until/unless an issue is later opened for it

**ADR vs. feature-level "Decisions Made" log:**
A decision belongs in a full ADR (under `docs/adr/`) if it: (a) is architecture/structure-level and affects more than one feature or the repo as a whole, (b) would be relevant to someone joining the project later trying to understand why something is the way it is, or (c) reverses/supersedes a previous ADR. A decision belongs in the feature's own "Decisions Made" log instead if it: (a) is scoped entirely to that one feature's implementation details, (b) wouldn't need to be found by searching ADRs later, and (c) doesn't constrain future features. Tie-breaker: if in doubt, write the ADR — it is cheap to write and already indexed by `adr-toc`, so overuse is low-cost, while under-use risks losing a decision in a feature folder no one will grep later.

### Confirmation

For now, confirmation that new `feat-NNN-slug/README.md` files follow the chosen structure/template is done manually via PR review. Automated enforcement (e.g. a `specmgr feat-*` validation tool mirroring `validate_adr`) is deferred to future work, consistent with the other deferred-tooling items noted in the chosen option's Open Questions.

## Pros and Cons of the Options

### Option 1: .specmgr structure

```
.specmgr/
├── feat/                          # Feature work units
│   └── feat-NNN-slug/             # One folder per GitHub issue
│       ├── README.md              # Feature plan + progress (mandatory)
│       └── history.md             # Archived older "Recent Updates" entries (optional)
└── (other dirs as needed)
```

**File purposes:**
- `README.md` — Single file containing both the feature plan (requirements, acceptance criteria, task list, scope, dependencies, design notes) and progress tracking (current state, blockers, decisions made during implementation, links to related ADRs or PRs)
- `history.md` — Optional sibling file. Holds older `Recent Updates` entries once `README.md` grows too long; `README.md` keeps only recent entries and links back to this file for anything older.

**Frontmatter:** Every feature `README.md` carries a YAML frontmatter block, mandatory fields `id` (the `feat-NNN-slug` folder name itself, not a generated UUID — unlike ADR frontmatter's server-generated `id`), `version` (semver, starts at `1.0.0`), `status` (`planning` | `in-progress` | `review` | `done`), and `created`/`updated` (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no separate `GitHub Issue` field, in frontmatter or body: the issue number is the `NNN` infix already embedded in `id` (i.e. the folder name, `feat-NNN-slug`) — `0` means no issue yet — so it is derived by reading `id`, never duplicated as its own field.

**Pros:**
- Single file to maintain
- Simpler structure: one file per feature
- Plan and progress are always together in one document
- Easier to see the full feature story (what was planned vs. what happened) in one place
- Requirements and acceptance criteria are co-located with clear traceability
- Single Task List: no separate Implementation/Execution Plan pair to keep in sync — status is a property of each task line, not a duplicated list, so there is nothing to drift
- Auditability of "what was planned vs. what actually happened" comes from git history on this one file, not from a hand-maintained duplicate
- `Recent Updates` growth is bounded by rotating older entries into an optional `history.md`, keeping `README.md` itself lean
- Frontmatter `id`/`version`/`status`/`created`/`updated` gives each feature folder a compact, machine-readable header, mirroring the ADR frontmatter's `status` field for consistency across both document types
- No `GitHub Issue` duplication: the issue number is already encoded in `id`'s `NNN` infix, so there is nothing to keep in sync between a frontmatter/body field and the folder name itself

**Cons:**
- File grows over time as progress updates (Recent Updates, Decisions Made) accumulate, even with rotation available
- Plan and progress are intermingled, making it harder to extract just the plan for reference
- No clear separation between "contract" (what we committed to) and "journal" (what actually happened) — relies on git history to reconstruct the original plan instead of a preserved, separate copy
- Still hand-maintained/free-text: nothing currently enforces that a task's status field, or the frontmatter `status`/`updated` fields, are kept in sync with reality, or that `history.md` rotation actually happens
- Deriving the GitHub issue number from `id`'s `NNN` infix requires parsing the folder name rather than reading a dedicated field — acceptable since `feat-NNN-slug` is already a fixed, documented convention

**Open Questions:**
- Archival/lifecycle rule for the file once `status: done` (stay in place / archive / prune) — intentionally left undecided here; treated as a separate future project decision, not a gap in this ADR.
- Rotation strategy for `Recent Updates`: rotating older entries into `history.md` is documented here as an available option; the exact trigger (manual vs. a fixed entry-count rule) and mechanics are left to the user/agent maintaining the feature folder to decide at the time, not prescribed by this ADR.
- Template location: **resolved** — the canonical feature template/example is now the packaged data behind the `get_feat_template` / `get_feat_example` feature tools (files under `src/biz/dfch/specmgr/feat/data/`). The hand-copied `.specmgr/_template/v1/README.md` copy was removed (feat-93); see the note at the end of this ADR.
- Whether to add further frontmatter fields later (e.g. `decision_makers`, `related_adrs`, `tags`) is left open; the current five-field frontmatter (`id`, `version`, `status`, `created`, `updated`) is a deliberate, minimal starting point, not a ceiling.
- Recommendation (not yet built, non-blocking): a dedicated MCP tool (analogous to this project's `update_section`/`option_update` for ADRs) that flips one task's status field, or the frontmatter `status`, atomically, instead of relying on an agent/human to locate and hand-edit the right line.

### Option 2: .specmgr structure with separate README.md (plan) and progress.md (status)

```
.specmgr/
├── feat/                          # Feature work units
│   └── feat-NNN-slug/             # One folder per GitHub issue
│       ├── README.md              # Feature plan (mandatory)
│       └── progress.md            # Status tracking (mandatory)
└── (other dirs as needed)
```

**File purposes:**
- `README.md` — Contains the complete feature plan: requirements, acceptance criteria, implementation plan, scope, dependencies, design notes, any pre-implementation research. Treated as immutable once work begins (except Implementation Plan, which may be refined during execution).
- `progress.md` — Hand-maintained status log: execution plan (tracking actual progress), current state, blockers, decisions made during implementation, links to related ADRs or PRs. Updated throughout the feature lifecycle.

**Pros:**
- Clear separation of concerns: README.md is the immutable "contract" (what we committed to), progress.md is the mutable "journal" (what actually happened)
- Auditability: you can see what was promised vs. what was delivered by comparing the two files
- Plan stays clean and focused: not cluttered with progress updates
- Easier to reference just the plan without scrolling through progress history
- Requirements and acceptance criteria are co-located with clear traceability
- Implementation Plan lives in README.md (single source of truth for the plan)
- Execution Plan lives in progress.md (single source of truth for actual progress)

**Cons:**
- Two files to maintain — requires reading both to get the full picture
- More complex structure
- Requires discipline to keep progress.md updated (hand-maintained, not auto-generated)
- Agents need to read both files to understand plan + current status
- Implementation Plan and Execution Plan are in separate files (requires cross-referencing)

**Open Questions:**
- Not chosen — this option was not carried forward with the same scrutiny/refinement pass as Option 1, since Option 1 was selected as the Decision Outcome. Retained here for reference only.
- Still has the original Implementation Plan / Execution Plan split (across two files, no less), i.e. the sync-burden issue identified and resolved in Option 1 via a single Task List with inline status was never addressed here.
- No `history.md`-equivalent or rotation mechanism for `progress.md`'s `Recent Updates` growth.
- Template-location ambiguity applies here too — no separate reusable template files, only what's embedded in this ADR.
- To be answered later, if this option is ever revisited: same open items as Option 1 (archival/lifecycle rule, template versioning path, potential atomic status-update tooling).

## More Information

- specmgr repository: https://github.com/anomalyco/biz.dfch.SpecMgr

> **Note (feat-93, 2026-09-04):** The verbatim fenced copies of the feature
> `README.md` template above are retained for historical reference only. The
> up-to-date, canonical feature template/example is the packaged data behind the
> `get_feat_template` / `get_feat_example` MCP tools (files under
> `src/biz/dfch/specmgr/feat/data/`) — see `get_feat_template` and
> `get_feat_example`. The on-disk `.specmgr/_template/v1/README.md` copy was
> removed (feat-93).
