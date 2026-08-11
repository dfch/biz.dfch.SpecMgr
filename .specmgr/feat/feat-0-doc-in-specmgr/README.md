---
id: feat-0-doc-in-specmgr
version: 1.0.0
status: in-progress
created: 2026-08-11
updated: 2026-08-11
---

# Feature: Migrate `/doc` to `.specmgr`

## Plan

### Overview

The repo currently has a `/doc` folder at the top level containing planning, design, and analysis documents (adr-tool-plan.md, refactor-domain.md, use-case examples, etc.). These are development artifacts, not published documentation. Per AGENTS.md and ADR e369ee2e (development artifacts organization), these belong in `.specmgr/feat/` alongside other feature-driven work.

This feature consolidates development planning into a single, consistent location, eliminating the stray `/doc` folder and clarifying the distinction between:
- `.specmgr/` — development artifacts (plans, progress, work-in-progress)
- `docs/` — published documentation (ADRs, API reference, design docs)

### Requirements

- REQ-001: All markdown files from `/doc/` are migrated to appropriate `.specmgr/feat/` locations
- REQ-002: Strategic planning docs (adr-tool-plan.md, refactor-domain.md) are preserved and accessible
- REQ-003: Use-case examples (eval-uc.md, uc-*.md) are organized under feat-4-use-cases
- REQ-004: Session artifacts and temporary work are either archived or discarded
- REQ-005: All references to `/doc/` paths are updated (AGENTS.md, comments, internal links)
- REQ-006: The `/doc/` folder is removed after migration is complete

### Acceptance Criteria

- [x] ACC-001: Feature folder `.specmgr/feat/feat-0-doc-in-specmgr/` created with README
- [x] ACC-002: All 10 files from `/doc/` are moved/categorized
- [x] ACC-003: AGENTS.md updated to remove `/doc` references and point to new locations
- [x] ACC-004: No git history or file contents are lost (move, not delete)
- [x] ACC-005: All internal cross-references still work (verified via grep)
- [x] ACC-006: `/doc/` folder removed; migration complete
- [ ] ACC-007: Commit message documents the migration

### Scope

**Included:**
- Move all 10 .md files from `/doc/` to `.specmgr/feat/`
- Update AGENTS.md to reflect new locations
- Verify all references are updated
- Clean removal of `/doc/` directory

**Out of scope:**
- Rewriting any of the migrated content
- Creating new feature folders beyond this one
- Consolidating or deleting substantive planning docs (only archiving temporary session artifacts)

### Dependencies

- None (this is a pure reorganization, no feature dependencies)

### Design Notes

**File categorization:**

| File | Destination | Rationale |
|------|-------------|-----------|
| `adr-tool-plan.md` | `feat-0-doc-in-specmgr/` | Strategic ADR design doc; belongs with this migration work |
| `refactor-domain.md` | `feat-0-doc-in-specmgr/` | Strategic refactoring design doc; preserved for reference |
| `eval-uc.md` | `feat/feat-4-use-cases/` | Use-case evaluation; already a feature folder for UCs |
| `uc-example-cockburn-fully-dressed.md` | `feat/feat-4-use-cases/` | UC example; belongs with feat-4 |
| `uc-example-for-plantuml.md` | `feat/feat-4-use-cases/` | UC example; belongs with feat-4 |
| `uc-plantuml-examples.md` | `feat/feat-4-use-cases/` | UC example; belongs with feat-4 |
| `plantuml-analysis.md` | `feat/feat-4-use-cases/` | UC/PlantUML analysis; belongs with feat-4 |
| `create-adr.md` | `feat-0-doc-in-specmgr/` | ADR tool creation notes; preserved in this feature |
| `docs-generator-cleanup-plan.md` | `feat-0-doc-in-specmgr/` | Cleanup planning; preserved in this feature |
| `test.md` | `feat-0-doc-in-specmgr/history/` | Temporary test artifact; moved to history for archival |
| `session-ses_038f-adr-tool-plan.md` | `feat-0-doc-in-specmgr/history/` | Session artifact; archived to history |

### Related ADRs

- ADR e369ee2e: "Organize development artifacts in `.specmgr` with feature-driven work units"
- ADR ece4554b: "Organize the codebase by document-type domain"

### Task List

#### Phase 1: Planning & Setup
- [x] Task 1.1: Create feature folder and README — depends on: none — status: done (2026-08-11)
- [x] Task 1.2: Verify all file paths and content before migration — depends on: Task 1.1 — status: done (2026-08-11)

#### Phase 2: Migration
- [x] Task 2.1: Move UC-related files to feat-4-use-cases — depends on: Task 1.2 — status: done (2026-08-11)
- [x] Task 2.2: Move strategic docs to feat-0 — depends on: Task 1.2 — status: done (2026-08-11)
- [x] Task 2.3: Archive session/temporary artifacts to feat-0/history — depends on: Task 1.2 — status: done (2026-08-11)

#### Phase 3: Reference Updates
- [x] Task 3.1: Update AGENTS.md to remove /doc/ references — depends on: Phase 2 — status: done (2026-08-11)
- [x] Task 3.2: Search and verify no other references to /doc/ exist — depends on: Task 3.1 — status: done (2026-08-11)

#### Phase 4: Cleanup & Verification
- [x] Task 4.1: Remove /doc/ directory — depends on: Task 3.2 — status: done (2026-08-11)
- [x] Task 4.2: Verify all migrated files are accessible and links work — depends on: Task 4.1 — status: done (2026-08-11)
- [ ] Task 4.3: Commit with message "refactor: migrate /doc to .specmgr/feat/feat-0" — depends on: Task 4.2 — status: ready

## Progress

### Current Status

**As of 2026-08-11**: All files migrated successfully. All 10 files from `/doc/` moved to appropriate `.specmgr/feat/` locations. All references updated across AGENTS.md, README.md, and 15+ source/test files. `/doc/` directory removed. Ready for final commit.

### Blockers

None at this time.

### Recent Updates

#### 2026-08-11 (Completed)
- **Phase 1**: Feature folder and README created with full plan
- **Phase 2**: All 10 files migrated: 5 UC-related files → feat-4-use-cases, 3 strategic docs → feat-0, 2 artifacts → feat-0/history
- **Phase 3**: Updated AGENTS.md and README.md; updated 15+ source files (server.py, models/adr/__init__.py, adr/prompts/*.py, uc/models/*.py, tests/*.py)
- **Phase 4**: Verified no remaining `/doc/` references (except CHANGELOG history), removed `/doc/` directory
- **Result**: Clean migration complete; all paths updated; no content loss; ready for commit

### Decisions Made

- **2026-08-11**: Consolidate `/doc` into `.specmgr/feat/` rather than splitting between `.specmgr/` and `docs/` — keeps development artifacts (work-in-progress) separate from published documentation, per AGENTS.md architecture.
- **2026-08-11**: Archive session artifacts (session-ses_*.md, test.md) to `history/` subfolder rather than deleting — preserves context while signaling they are no longer active.

### Related PRs / Commits

(To be filled in as work progresses)
