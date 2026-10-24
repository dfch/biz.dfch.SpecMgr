---
classification: null
created: '2026-10-24T08:21:00.912+02:00'
id: feat-232-dependabot-security-alerts
status: planning
type: feat
updated: '2026-10-24T08:26:47.110+02:00'
version: 1.0.0
---

# Feature: dependabot: security alerts

## Plan

### Overview

Resolve the 11 open Dependabot security alerts on `uv.lock` as of 2026-10-24 (9× Pillow, 1× certifi, 1× stale uv).

### Requirements

- REQ-001: The certifi lock entry moves from 2026.7.22 to a release ≥ 2026.10.19 (latest 2026.10.23) in a standalone, lock-only PR.
- REQ-002: The pillow lock entry moves from 12.3.0 to 13.0.0 or later once a fastembed release lifts the `pillow<13.0` cap, verified with the full default test suite plus the opt-in `embedding_model` similarity test.
- REQ-003: All 11 alerts in the repo's Dependabot dashboard report as resolved; the uv alert (dashboard #28) auto-closes since dev already carries the fix (#226), needing no repo change.

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

- [ ] Task 100.100: Run `uv lock --upgrade-package certifi` and confirm the lock lands on certifi 2026.10.23 (≥ 2026.10.19) with nothing else moved.
- [ ] Task 100.110: Verify with `uv sync --frozen --all-extras`, `ruff format --check` + `ruff check`, and `pytest -n auto --cov=src`.
- [ ] Task 100.120: Commit `chore(deps): bump certifi`, open the PR, merge, and confirm dashboard alert 29 closes.

#### Phase 110: pillow 13 via fastembed (blocked on upstream)

- [ ] Task 110.100: Track qdrant/fastembed#830; optionally comment on fastembed#829 pointing at the 9 open advisories on 12.3.0.
- [ ] Task 110.110: On release, run `uv lock --upgrade-package fastembed --upgrade-package pillow` and confirm pillow resolves ≥ 13.0.0.
- [ ] Task 110.120: Verify with the default suite plus `pytest -m embedding_model`, commit `chore(deps): bump fastembed + pillow`, open the PR, and merge.

#### Phase 120: final verification

- [ ] Task 120.100: Confirm the stale uv alert 28 auto-closed, run the open-alerts API query, and record the final state in Progress.

## Progress

### Current Status

**As of 2026-10-24**: Planning. Phase 100 is ready to execute; Phase 110 is blocked on qdrant/fastembed#830 (open, unmerged as of 2026-10-20).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T06:25:18.000Z - Close-out: triage complete, handoff ready

Session close-out: all 11 open alerts triaged (snapshot plus the fastembed pin rationale in `### More Information`). Phase 100 (certifi) is immediately executable — no upstream dependency. Phase 110 (pillow) is blocked on qdrant/fastembed#830 being merged and released; until then pillow 12.3.0 is risk-accepted (see Decisions Made). No repo change was made this session beyond this feat document; the feat folder is still untracked — commit it before starting Phase 100.

#### 2026-10-24T06:19:13.000Z - Created

Feat created for GitHub issue #232 (dependabot: security alerts): 11 open alerts on `uv.lock` (9× Pillow, 1× certifi, 1× stale uv). The certifi bump goes first as a standalone PR; Pillow is blocked on fastembed's `pillow<13.0` cap.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T06:19:13.000Z - Risk-accept pillow 12.3.0 while waiting on fastembed

Zero PIL imports in `src/`/`tests/` and fastembed is used strictly as `TextEmbedding`, so the 9 Pillow advisories (all in image-parsing paths: JPEG/TIFF/GIF/PDF/EPS) carry no practical exposure in this codebase. Forcing pillow 13 via a uv override is rejected (it would violate fastembed's declared constraint). Waiting on the upstream cap raise has precedent: fastembed#606 cut 0.7.5 to unblock pillow 12.x under CVE pressure.

### Related PRs / Commits

- dev already carries the uv fix (PR #226, commit `b65d8c3`) — dashboard alert 28 is stale and self-closes.

### More Information

Open-alert snapshot as of 2026-10-24 (via `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open`; locked versions from `uv.lock`):

- **28 — uv** (direct, `dev` extra): locked 0.13.4, fixed in 0.13.4 (GHSA-hq85-5cpj-mr62, critical — emSign CA compromise in uv's vendored webpki bundle). Already fixed on dev via #226; stale alert, self-closes.
- **29 — certifi** (transitive: httpx/requests/httpcore): locked 2026.7.22, fixed in 2026.10.19, latest 2026.10.23 (GHSA-6q48-6c7w-9gw2, critical — emSign root CA with compromised intermediate keys). No pin blocks the bump — Phase 100.
- **30–38 — pillow** (transitive: fastembed): locked 12.3.0, all nine fixed in 13.0.0 (1×critical GHSA-8g5g-8vmr-9782, 6×high, 2×medium — all image-parsing paths: JPEG/TIFF/GIF/PDF/EPS). Blocked by fastembed's `pillow<13.0` cap.

Why fastembed caps pillow at <13.0: a stale major-version upper bound (fastembed caps every dependency: `numpy<2.3`, `onnxruntime<1.24`, `huggingface-hub<2.0`, …), not a known incompatibility — Pillow 13's breaking changes (Python 3.10 EOL, `I`-mode PNG save, `fromarray` mode parameter, `get_child_images()` move, `Image._show` removal, `ImageCms` attr removals, `ExifTags.IFD.Makernote` rename) do not touch fastembed's usage. fastembed's own PR #830 ("chore(deps): allow pillow 13", cap → `<14.0`) reports "image tests pass on Pillow 13.0.0"; as of 2026-10-24 it is open/unmerged (branch `chore/allow-pillow-13`) and the cap is present in 0.8.0 (locked), 0.9.0 (latest), and upstream `main`. Precedent for a release lifting the cap under CVE pressure: fastembed#606 (0.7.5 for pillow 12.x).
