---
classification: null
created: '2026-10-24T08:21:00.912+02:00'
id: feat-232-dependabot-security-alerts
status: planning
type: feat
updated: '2026-10-24T09:35:12.338+02:00'
version: 1.0.0
---

# Feature: Resolve Dependabot Security Alerts in uv.lock (issue #232)

## Plan

### Overview

Resolve the 11 open Dependabot security alerts on `uv.lock` as of 2026-10-24 (9× Pillow, 1× certifi, 1× stale uv).

### Requirements

- REQ-001: The certifi lock entry moves from 2026.7.22 to a release ≥ 2026.10.19 (latest 2026.10.23) in a standalone, lock-only PR.
- REQ-002: The pillow lock entry moves from 12.3.0 to 13.0.0 or later once a fastembed release lifts the `pillow<13.0` cap (upstream PR #830 targets `<14.0`), verified with the full default test suite plus the opt-in `embedding_model` similarity test.
- REQ-003: All 11 alerts in the repo's Dependabot dashboard report as resolved.

### Acceptance Criteria

- [ ] ACC-001: `uv.lock` resolves certifi ≥ 2026.10.19 and `uv sync --frozen --all-extras`, ruff format/check, and the full default pytest suite all pass.
- [ ] ACC-002: `uv.lock` resolves pillow ≥ 13.0.0 together with the unblocking fastembed release, and the default suite plus `pytest -m embedding_model` passes.
- [ ] ACC-003: `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open` returns no alerts.

### Scope

#### Included

- The targeted `uv lock --upgrade-package` bump for certifi, and (later) fastembed + pillow.
- Upstream tracking of qdrant/fastembed PR #830 (raises the pillow cap to `<14.0`).

#### Explicitly Out Of Scope

- Forcing pillow 13 via uv `override-dependencies` (rejected: violates fastembed's declared constraint).
- Any `pyproject.toml` dependency-spec change (certifi and pillow are transitive; uv is already at its fixed version).
- Dismissing alerts without a recorded rationale.

### Dependencies

#### Depends On

- qdrant/fastembed PR #830 merged and released (for REQ-002 only; REQ-001 is independent).

### Task List

#### Phase 100: certifi bump (standalone PR)

- [ ] Task 100.100: Run `uv lock --upgrade-package certifi` and confirm the lock lands on a certifi release ≥ 2026.10.19 (snapshot latest: 2026.10.23) with nothing else moved.
- [ ] Task 100.110: Verify with `uv sync --frozen --all-extras`, `uv run --frozen ruff format --check` + `uv run --frozen ruff check`, and `uv run --frozen pytest -n auto --cov=src --cov-report=`.
- [ ] Task 100.120: Commit `chore(deps): bump certifi`, open the PR, merge, and confirm dashboard alert 29 closes (Dependabot re-scans on its own schedule after a branch update — if it is still open shortly after the merge, re-query the open-alerts API before treating the bump as failed).

#### Phase 110: pillow 13 via fastembed (blocked on upstream)

- [ ] Task 110.100: Track qdrant/fastembed#830 (the `chore(deps): allow pillow 13` PR); optionally comment on qdrant/fastembed#829 (the upstream `[Feature]: Support pillow 13` issue) pointing at the 9 open advisories on 12.3.0.
- [ ] Task 110.110: On release, run `uv lock --upgrade-package fastembed --upgrade-package pillow` and confirm pillow resolves ≥ 13.0.0.
- [ ] Task 110.120: Verify with the default suite plus `uv run --frozen pytest -m embedding_model`, commit `chore(deps): bump fastembed + pillow`, open the PR, and merge.

#### Phase 120: final verification

- [ ] Task 120.100: Run the open-alerts API query (Dependabot re-scans on its own schedule after a branch update — allow for that before treating a still-open alert as a failed bump), confirm all alerts have closed or note which re-scan is pending, and record the final state in Progress.
- [ ] Task 120.110: Confirm which branch(es) Dependabot monitors; alert 28 needs no repo change from this feature (the #226 fix is on dev) and closes once the monitored branch carries it, else record the promotion dependency in Progress.

## Progress

### Current Status

**As of 2026-10-24**: Planning. Phase 100 is ready to execute; Phase 110 is blocked on qdrant/fastembed#830 (open, unmerged as of 2026-10-20).

### Blockers

- qdrant/fastembed#830 (`chore(deps): allow pillow 13`, the cap raise to `<14.0`) is open/unmerged — blocks Phase 110 (REQ-002, ACC-002) only; Phase 100 proceeds independently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T07:35:12.000Z - Plan refined (refiner pass)

A refinement pass over the plan: the two `06:19:13.000Z` log entries are re-dated to `06:21:00.912Z` to match the frontmatter `created` (the create tool's birth stamp is authoritative — the log entries were backdated to the session start); alert 28's closure is now conditioned on the Dependabot-monitored branch (new Task 120.110; softened wording in `### Related PRs / Commits` and `### More Information`); `### Blockers` added; fastembed#829 (the upstream `[Feature]: Support pillow 13` issue) made self-explanatory in Task 110.100; verification commands aligned to AGENTS.md's `uv run --frozen` form; re-scan-wait guidance added to the alert-confirmation tasks; Task 100.100 now matches REQ-001's `≥` flexibility; REQ-002 states the expected `<14.0` cap and REQ-003 carries no reasoning; the risk-accept decision cites its verification command; the title is now descriptive. No task status changes — Phase 100 remains ready to execute.

#### 2026-10-24T06:25:18.000Z - Close-out: triage complete, handoff ready

Session close-out: all 11 open alerts triaged (snapshot plus the fastembed pin rationale in `### More Information`). Phase 100 (certifi) is immediately executable — no upstream dependency. Phase 110 (pillow) is blocked on qdrant/fastembed#830 being merged and released; until then pillow 12.3.0 is risk-accepted (see Decisions Made). No repo change was made this session beyond this feat document; the feat folder is still untracked — commit it before starting Phase 100.

#### 2026-10-24T06:21:00.912Z - Created

Feat created for GitHub issue #232 (dependabot: security alerts): 11 open alerts on `uv.lock` (9× Pillow, 1× certifi, 1× stale uv). The certifi bump goes first as a standalone PR; Pillow is blocked on fastembed's `pillow<13.0` cap.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T06:21:00.912Z - Risk-accept pillow 12.3.0 while waiting on fastembed

Zero PIL imports in `src/`/`tests/` (verified 2026-10-24: `grep -rniE "PIL|pillow" src/ tests/` matches nothing) and fastembed is used strictly as `TextEmbedding` (the only construction site: `src/biz/dfch/specmgr/general/tools/_embedding.py:582`), so the 9 Pillow advisories (all in image-parsing paths: JPEG/TIFF/GIF/PDF/EPS) carry no practical exposure in this codebase. Forcing pillow 13 via a uv override is rejected (it would violate fastembed's declared constraint). Waiting on the upstream cap raise has precedent: fastembed#606 cut 0.7.5 to unblock pillow 12.x under CVE pressure.

### Related PRs / Commits

- dev already carries the uv fix (PR #226, commit `b65d8c3`); dashboard alert 28 closes once the Dependabot-monitored branch carries it (the monitored branch is confirmed in Phase 120, Task 120.110).

### More Information

Open-alert snapshot as of 2026-10-24 (via `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open`; locked versions from `uv.lock`):

- **28 — uv** (direct, `dev` extra): locked 0.13.4, fixed in 0.13.4 (GHSA-hq85-5cpj-mr62, critical — emSign CA compromise in uv's vendored webpki bundle). Already fixed on dev via #226; closes once the Dependabot-monitored branch carries the fix (branch to be confirmed in Phase 120).
- **29 — certifi** (transitive: httpx/requests/httpcore): locked 2026.7.22, fixed in 2026.10.19, latest 2026.10.23 (GHSA-6q48-6c7w-9gw2, critical — emSign root CA with compromised intermediate keys). No pin blocks the bump — Phase 100.
- **30–38 — pillow** (transitive: fastembed): locked 12.3.0, all nine fixed in 13.0.0 (1×critical GHSA-8g5g-8vmr-9782, 6×high, 2×medium — all image-parsing paths: JPEG/TIFF/GIF/PDF/EPS). Blocked by fastembed's `pillow<13.0` cap.

Why fastembed caps pillow at <13.0: a stale major-version upper bound (fastembed caps every dependency: `numpy<2.3`, `onnxruntime<1.24`, `huggingface-hub<2.0`, …), not a known incompatibility — Pillow 13's breaking changes (Python 3.10 EOL, `I`-mode PNG save, `fromarray` mode parameter, `get_child_images()` move, `Image._show` removal, `ImageCms` attr removals, `ExifTags.IFD.Makernote` rename) do not touch fastembed's usage. fastembed's own PR #830 ("chore(deps): allow pillow 13", cap → `<14.0`) reports "image tests pass on Pillow 13.0.0"; as of 2026-10-24 it is open/unmerged (branch `chore/allow-pillow-13`) and the cap is present in 0.8.0 (locked), 0.9.0 (latest), and upstream `main`. Precedent for a release lifting the cap under CVE pressure: fastembed#606 (0.7.5 for pillow 12.x).
