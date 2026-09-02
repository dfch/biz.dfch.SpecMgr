---
classification: null
created: '2026-09-03 00:03:19.829+02:00'
id: feat-73-74-76
status: planning
type: feat
updated: '2026-09-03 00:06:13.219+02:00'
version: 1.0.0
---

# Feature: License Audit, sysrs Config Gaps, and Confluence Page Title Fix (issues #73/#74/#76)

## Plan

### Overview

This feature tracks three independent maintenance/quality-gap issues opened on 2026-09-02: (1) auditing NOTICE for correct 3rd-party license info across all direct dependencies, using issue #47/mdformat-simple-breaks as a worked example; (2) closing gaps where the sysrs domain is missing from specmgr://config and possibly other common cross-domain functions other domains already have; and (3) fixing specmgr_confluence_update so it sets the Confluence page title from the markdown's first H1 heading (or leaves the title untouched if there is no H1).

### Requirements

- REQ-001: NOTICE must correctly list license info for every directly used 3rd-party library dependency, verified issue-by-issue against issue #47 as a worked example.

- REQ-002: specmgr://config must expose sysrs alongside every other implemented domain, and any other common cross-domain function missing for sysrs (relative to req/uc/tsk/etc.) must be identified and listed.

- REQ-003: specmgr_confluence_update must set the target Confluence page's title from the first H1 heading of the source markdown file; if the markdown has no H1, the page title must be left unchanged.

### Acceptance Criteria

- [ ] ACC-001: Every direct 3rd-party dependency's license entry in NOTICE is manually verified correct (license type + attribution text) and any discrepancy found is fixed.

- [ ] ACC-002: specmgr://config's output includes a sysrs entry, and a written gap list of missing sysrs functions (vs. other domains) exists in this feature's Design Notes or a follow-up.

- [ ] ACC-003: A markdown file with a first H1 updates the Confluence page title on specmgr_confluence_update; a markdown file with no H1 leaves the existing page title untouched -- both verified by test.

### Scope

#### Included

- NOTICE file audit and correction for all direct 3rd-party library dependencies.

- Gap analysis of specmgr://config and other common cross-domain functions for the sysrs domain, plus fixing the specmgr://config gap itself.

- specmgr_confluence_update: extract first H1 from source markdown and set it as the Confluence page title via the REST API.

#### Explicitly Out Of Scope

- Auditing indirect/transitive dependency licenses (direct dependencies only, per issue #73's wording).

- Implementing any newly discovered missing sysrs functions beyond specmgr://config exposure itself (those become their own follow-up features once identified).

- Any other Confluence page metadata beyond the title (labels, space, permissions, etc.).

### Task List

#### Phase 1: NOTICE License Audit (#73)

- [ ] Task 1.1: List every direct 3rd-party library dependency from pyproject.toml.

- [ ] Task 1.2: For each dependency, verify NOTICE lists the correct license type and attribution text (using #47/mdformat-simple-breaks as the worked example).

- [ ] Task 1.3: Fix any discrepancies found in NOTICE.

#### Phase 2: sysrs Config/Gap Analysis (#74)

- [ ] Task 2.1: Add sysrs to specmgr://config.

- [ ] Task 2.2: Compare sysrs's tools/resources/prompts against every other whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) to find other missing common functions.

- [ ] Task 2.3: Write up the gap list (in Design Notes or a follow-up feature).

- [ ] Task 2.4: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

#### Phase 3: Confluence Page Title Fix (#76)

- [ ] Task 3.1: In specmgr_confluence_update, parse the first H1 heading from the source markdown file.

- [ ] Task 3.2: Set the Confluence page's title field to that H1 text when updating the page body via the REST API.

- [ ] Task 3.3: If no H1 is present, leave the existing page title untouched.

- [ ] Task 3.4: Add/adjust tests covering both the H1-present and no-H1 cases.

- [ ] Task 3.5: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

## Progress

### Current Status

**As of 2026-09-02**: Feature just created to track issues #73, #74, and #76. No implementation work has started yet; all three sub-issues are in the planning/investigation stage.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:06:00.000+02:00 - Added final quality-gate tasks to Phase 2 and Phase 3

Added Task 2.4 and Task 3.5, each requiring a full test-suite run (unittest) plus ruff/vulture checks at the end of the code-touching phases (sysrs config change and Confluence title fix). Phase 1 (NOTICE audit) is documentation-only and was left without a test-run task.

#### 2026-09-02 12:00:00.000Z - Created

Feature created to track GitHub issues #73 (NOTICE license audit), #74 (sysrs config/gap analysis), and #76 (Confluence page title fix). No implementation started yet.
