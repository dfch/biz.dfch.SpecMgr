---
classification: null
created: '2026-10-26T07:16:20.020+01:00'
id: feat-218-in-tree-spec-artifact-parseability-gate
status: planning
type: feat
updated: '2026-10-26T07:16:20.020+01:00'
version: 1.0.0
---

# Feature: In-Tree Spec Artifact Parseability Gate

## Plan

### Overview

This repo keeps its own planning documents as specmgr FEAT artifacts — one README.md per feature folder under .specmgr/feat/ (88 as of this writing) — and every FEAT document must be parseable: its frontmatter and full body are checked against the feat schema by the model-level parser (biz.dfch.specmgr.feat.models.v1.parse_feat). Nothing on the commit path performs that full parse. A body-level defect in any in-tree document is therefore invisible by default: list_feat reads only frontmatter+H1 (the dirty stage, by design — ADR 3982712a's time-qualification) and keeps reporting the document healthy, while every full-parse consumer (the get_feat read path, the reference-graph builders, similarity search) either returns a parse failure or silently drops the document. This was demonstrated in the wild by feat-214 itself: its plan document shipped unparseable in three consecutive commits (f578e69 through 6714117) because its Decisions Made section had been authored as dated bullet lines, which the schema's H4 date-entry form rejects, and the defect surfaced only as an indirect symptom — the document missing from every live reference-graph diagram — during the Phase 130 CLI walkthrough. This feature closes that defect class: a full-parseability gate over the repo's own in-tree FEAT corpus, enforced locally (a pre-commit hook scoped to .specmr/**.md) and in CI (a plain test in the existing suite, which runs on every commit).

### Requirements

- REQ-001: A new test in the existing suite runs the model-level full parse (biz.dfch.specmgr.feat.models.v1.parse_feat) over every .specmgr/feat/*/README.md of this repo, and fails — reporting every unparseable document (file path + parse error), not just the first.

- REQ-002: The test resolves the in-tree corpus by globbing .specmgr/feat/*/README.md under the repo root, where the repo root is derived from the test file's own location (__file__), and never from the SPECMGR_FEAT_DIR base directory, so fixture-pointing test environments cannot divert or empty the sweep.

- REQ-003: The gate must do full parses; it must not be a list_feat-based or frontmatter+H1-only check — that is precisely the masking mechanism (the dirty stage) that hid the feat-214 defect.

- REQ-004: A new local pre-commit hook in .pre-commit-config.yaml runs the sweep test (targeted, no coverage, no xdist) on any commit touching a file matching ^\.specmgr/.*\.md$, placed ahead of the broad pytest hook in the configuration.

- REQ-005: The sweep stays cheap: the full 88-document corpus parses in seconds, and the hook's targeted run adds only that few-seconds cost to the commit path.

- REQ-006: CI coverage requires no workflow change: the new test runs in the existing build job's "Run unit tests with coverage" step on every push/PR, on all three matrix Python versions.

### Acceptance Criteria

- [ ] ACC-001: A deliberately broken document in the feat-214 failure shape (a Decisions Made entry authored as a dated bullet line) makes the new test fail with the offending file named and its parse error reported, both under the targeted local run and the full suite.

- [ ] ACC-002: The new test passes against the current corpus (all 88 .specmgr/feat/*/README.md full-parse cleanly) on Python 3.11, 3.12, and 3.13 in CI.

- [ ] ACC-003: In a clean local repo, committing a change to any in-tree feature README.md under .specmgr/feat/ triggers the new pre-commit hook, which runs the sweep in seconds and blocks the commit when any corpus document fails to parse; a commit touching neither .specmgr/**.md nor src/tests is unaffected by the new hook.

- [ ] ACC-004: Running the test with SPECMGR_FEAT_DIR pointed at an empty temporary directory still sweeps the in-tree corpus (proof the sweep is immune to fixture diversion).

- [ ] ACC-005: On this feature's merge commit, CI's build job runs the new test as part of the existing suite step (visible in the job log, no new workflow step or job).

### Scope

#### Included

- The new full-parse sweep test over the in-tree FEAT corpus (tests/test_in_tree_feat_parse.py).

- A negative-test pin proving the gate catches the feat-214 failure shape, against a temporary fixture corpus (the in-tree corpus is never mutated by tests).

- The new local pre-commit hook in .pre-commit-config.yaml (scoped to ^\.specmgr/.*\.md$, running the sweep test targeted) and its documentation in AGENTS.md's pre-commit paragraph.

- Close-out: the in-tree corpus green under the new gate at merge, including this feature's own README.md.

#### Explicitly Out Of Scope

- The ADR corpus (docs/adr/*.md): it carries the same defect class (specmgr adr-toc silently skips unparseable ADRs), but full-parse gating of ADRs is a follow-up candidate, not part of this feature.

- Auto-discovery of future in-tree corpora: the sweep's corpus is the fixed glob .specmgr/feat/*/README.md.

- Other specmgr document types not currently kept in-tree (req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs exist in this repo only as test fixtures).

- Repairing any currently unparseable in-tree document (the corpus is green today; if the gate ever catches a document, the repair goes through the existing repair flow).

- Changes to the list_feat dirty/clean two-stage design, to the feat schema, or to parse_feat itself.

- A dedicated CI workflow step or job (CI coverage comes free from the existing build job's suite run).

- Any new ADR (feature-level decisions only, per the planning decision recorded under Decisions Made).

### Dependencies

#### Depends On

- feat-214-rel-invalid-diag (done, PR #216): the feature whose own plan document demonstrated the defect — three unparseable commits — and which recorded issue #218 as this follow-up.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (list_feat dirty/clean time-qualification): documents the masking mechanism that REQ-003 works around.

### Design Notes

Why full parses, never listing: list_feat's request path resolves each folder from a frontmatter+H1-only dirty-stage parse by design (ADR 3982712a), so a listing-based check would reproduce exactly the masking that hid the feat-214 defect for three commits. The gate must call the parser on the file's full text.

Corpus resolution: the test derives the repo root from its own __file__ (tests/ -> repo root, two levels up) and globs .specmgr/feat/*/README.md under it directly. It deliberately does NOT honor SPECMGR_FEAT_DIR or call the domain's base-dir resolver: other tests point that variable at temporary fixtures, and the xdist suite runs in parallel processes, so an env-derived corpus could be diverted or emptied. The sweep helper takes the corpus root as a parameter; the in-tree test passes the real repo root, and the negative test passes a temporary fixture root.

Which parser: the model-level biz.dfch.specmgr.feat.models.v1.parse_feat (base library — pydantic only, no mcp extra), not the MCP tool. The MCP wrapper adds wrap_tool_errors context and a non-raising ValidateResult shape that a corpus gate does not want; the gate wants the raw parse failure, caught per file and aggregated.

Failure reporting: the sweep collects every failing (path, error) pair across the whole corpus and asserts on the aggregate, so one run reports the entire broken set instead of one defect at a time (the errors already carry the feat-27 actionable field-path + line + fix-hint shape).

The hook: a new local hook in .pre-commit-config.yaml — id specmgr-in-tree-feat-parse, files ^\.specmgr/.*\.md$, pass_filenames: false, entry uv run --frozen pytest tests/test_in_tree_feat_parse.py -q (targeted: no --cov, no -n auto) — mirroring the specmgr-adr-toc precedent (a file-scoped local hook for a markdown corpus). It is placed ahead of the broad pytest hook, which is scoped to ^(src|tests)/.*\.py$ and would never fire on a docs-only commit — the exact gap this feature closes. Cost: the full 88-document corpus parses in seconds (84 measured at issue time), so the hook adds a few seconds to doc-touching commits only.

### Related Decisions

- feat-214-rel-invalid-diag (feature, done) + PR #216: the follow-up whose own plan demonstrated the defect and which recorded issue #218.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44: list_feat dirty/clean time-qualification — the masking mechanism the full-parse requirement works around.

- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI" — grounds the hook half of the gate.

- AGENTS.md, "Still genuinely missing / not yet done": the standing note that no validate-equivalent check runs over the repo's own documents via pre-commit or CI — this feature closes its FEAT half (the ADR half remains open, see Explicitly Out Of Scope).

### Task List

#### Phase 100: Sweep Test

- [ ] Task 100.100: Implement the sweep: a tests/test_in_tree_feat_parse.py whose helper takes a corpus root (default: repo root derived from __file__), globs .specmgr/feat/*/README.md, runs the model-level parse_feat on each file's text, and fails with an aggregate report of every (path, parse error) pair.

- [ ] Task 100.110: Add the negative pin: a temporary fixture corpus containing a document in the feat-214 failure shape (Decisions Made authored as dated bullet lines) fails the sweep with the offending file named; verify the in-tree corpus is never mutated.

- [ ] Task 100.120: Verify under the full suite (uv run --frozen pytest -n auto) on Python 3.13, confirming xdist-parallel safety and env immunity (SPECMGR_FEAT_DIR pointed at an empty temp dir).

#### Phase 110: Pre-commit Hook

- [ ] Task 110.100: Add the specmgr-in-tree-feat-parse local hook to .pre-commit-config.yaml (files ^\.specmgr/.*\.md$, pass_filenames false, targeted pytest entry, placed ahead of the broad pytest hook) and document it in AGENTS.md's pre-commit paragraph.

- [ ] Task 110.110: Local walkthrough: (a) a healthy .specmgr/feat README change commits with the hook running in seconds; (b) a feat-214-shape defect introduced in a scratch feature README blocks the commit with the file + error reported; (c) revert; (d) a src-only commit does not trigger the hook. Record the outcome under Updates.

#### Phase 120: CI Backstop + Close-out

- [ ] Task 120.100: Open the PR and confirm the build job runs the new test in the existing "Run unit tests with coverage" step on all three matrix versions with no workflow change (ACC-005), and confirm ACC-001 through ACC-004.

- [ ] Task 120.110: Close out: mark all tasks done, update Current Status, and self-check that this feature's own README.md full-parses under the new gate before setting the status to done.

## Progress

### Current Status

**As of 2026-10-26**: Planning complete. Issue #218 analyzed; no existing feature covers this topic (checked against all 88 in-tree feature documents). The planning decisions are recorded under Decisions Made (corpus = in-tree FEAT plans only; gate = suite test + scoped pre-commit hook; no ADR). Implementation not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26T05:42:45.913Z - Created

Feature plan drafted from issue #218: a full-parseability gate over the repo's own in-tree FEAT corpus (.specmgr/feat/*/README.md, 88 documents), enforced by a plain test in the existing suite (CI backstop on every commit, no workflow change) and by a new pre-commit hook scoped to .specmr/**.md (local enforcement for docs-only commits, which the broad src/tests-scoped pytest hook skips). The defect class was demonstrated in the wild by feat-214's own plan shipping unparseable in three consecutive commits (f578e69 through 6714117).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26T05:42:45.913Z - Planning decisions (issue #218)

Four planning decisions made while drafting this feature: (1) Corpus = feature plans only — the ADR corpus (docs/adr/*.md) carries the same defect class (specmgr adr-toc silently skips unparseable ADRs) but is explicitly out of scope here, recorded as a follow-up candidate; (2) Gate = suite test + scoped pre-commit hook — the plain test runs in CI on every commit via the existing build job, and the new hook (files ^\.specmgr/.*\.md$) enforces locally on docs-only commits that the broad pytest hook (scoped to src/tests) never sees, per ADR 9c687bb1's "locally via pre-commit hook, not just CI"; (3) No ADR — the decisions stay feature-level; (4) Title/id = "In-Tree Spec Artifact Parseability Gate" / feat-218-in-tree-spec-artifact-parseability-gate.

### Related PRs / Commits

- Issue #218: https://github.com/dfch/biz.dfch.SpecMgr/issues/218 — the tracking issue for this feature.

- PR #216: https://github.com/dfch/biz.dfch.SpecMgr/pull/216 — feat-214, the follow-up that recorded issue #218.

- Commits f578e69 through 6714117 — the three consecutive commits in which feat-214's own plan document shipped unparseable (the demonstration case).

### More Information

How the defect hid (three symptoms, all observed on feat-214's plan): (1) list_feat reported the document healthy throughout, because its request path resolves each folder from a frontmatter+H1-only dirty-stage parse — exactly the masking the dirty/clean two-stage design documents (ADR 3982712a); (2) the reference-graph builders' full-parse scan legs silently skipped the document (rulebook §3.4), dropping feat-214 from every live diagram — a symptom noticed only during the Phase 130 CLI walkthrough; (3) CI runs the test suite, but no test or step runs parse_feat over the repo's own in-tree .specmgr/ corpus. Cost: the full feat corpus parses in seconds (84 documents at issue time; 88 now), so the gate is negligible in CI and a few seconds in the hook. Note: .specmgr/conventions.md and the .specmgr/conventions/ directory are hand-authored documentation, not specmgr-managed artifacts — they are outside the corpus by construction of the glob. Sibling-class framing: feat-214 fixed a gate that existed but was env-gated and unconfigured on the commit path (the PlantUML real-parser); this feature fixes the case where the gate does not exist at all.
