---
classification: null
created: '2026-10-24T08:21:00.912+02:00'
id: feat-232-dependabot-security-alerts
status: planning
type: feat
updated: '2026-10-24T13:51:54.000+02:00'
version: 1.0.0
---

# Feature: Resolve Dependabot Security Alerts in uv.lock (issue #232)

## Plan

### Overview

Resolve the open Dependabot security alerts on `uv.lock` (62 as of the 2026-10-24 amendment: 41× Pillow, 15× virtualenv, 3× filelock, 1× certifi, 1× opentelemetry-api, 1× stale uv). The original plan captured the 11-alert pre-rescan snapshot (the 2026-10-21 cohort); this morning's 06:04Z Dependabot re-scan added 51 more alerts — 32 additional Pillow (a wave of newly published Pillow advisories), 15 virtualenv, 3 filelock, 1 opentelemetry-api. The pillow cohort stays blocked on qdrant/fastembed#830 (REQ-002); the new non-pillow cohort is lock-only fixable and is added as REQ-004 / Phase 105 (user-approved scope expansion, 2026-10-24).

### Requirements

- REQ-001: The certifi lock entry moves from 2026.7.22 to a release ≥ 2026.10.19 (latest 2026.10.23) in a standalone, lock-only PR.
- REQ-002: The pillow lock entry moves from 12.3.0 to 13.0.0 or later once a fastembed release lifts the `pillow<13.0` cap (upstream PR #830 targets `<14.0`), verified with the full default test suite plus the opt-in `embedding_model` similarity test.
- REQ-003: Every alert in the 2026-10-24 snapshot (62 open) reports as resolved once its fix reaches the monitored branch (`dev`) and Dependabot re-scans: the 41-alert pillow cohort via REQ-002, certifi via REQ-001, virtualenv/filelock/opentelemetry-api via REQ-004, and the stale uv alert (28) with no repo change — `dev` already carries 0.13.4 via merged PR #226.
- REQ-004: The transitive lock entries virtualenv (21.7.13 → ≥ 21.14.9), filelock (3.32.2 → ≥ 4.2.1), and opentelemetry-api (1.44.0 → ≥ 1.45.1) move in a single lock-only `uv lock --upgrade-package` change, verified with the full default test suite plus the opt-in `embedding_model` similarity test (filelock sits on the fastembed → huggingface-hub model-cache path).

### Acceptance Criteria

- [ ] ACC-001: `uv.lock` resolves certifi ≥ 2026.10.19 and `uv sync --frozen --all-extras`, ruff format/check, and the full default pytest suite all pass.
- [ ] ACC-002: `uv.lock` resolves pillow ≥ 13.0.0 together with the unblocking fastembed release, and the default suite plus `pytest -m embedding_model` passes.
- [ ] ACC-003: `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open` returns no alerts. (ultimate bar; not satisfiable within this session while the pillow cohort is blocked on qdrant/fastembed#830 — the Phase 120 recorded state is the interim evidence)
- [ ] ACC-004: `uv.lock` resolves virtualenv ≥ 21.14.9, filelock ≥ 4.2.1, and opentelemetry-api ≥ 1.45.1, and `uv sync --frozen --all-extras`, ruff format/check, and the full default pytest suite plus `pytest -m embedding_model` all pass.

### Scope

#### Included

- The targeted `uv lock --upgrade-package` bump for certifi, and (later) fastembed + pillow.
- Upstream tracking of qdrant/fastembed PR #830 (raises the pillow cap to `<14.0`).
- The single lock-only `uv lock --upgrade-package` bump for virtualenv, filelock, and opentelemetry-api (Phase 105; user-approved scope expansion for the 06:04Z re-scan cohort).

#### Explicitly Out Of Scope

- Forcing pillow 13 via uv `override-dependencies` (rejected: violates fastembed's declared constraint).
- Any `pyproject.toml` dependency-spec change (certifi and pillow are transitive; uv is already at its fixed version).
- Dismissing alerts without a recorded rationale.

### Dependencies

#### Depends On

- qdrant/fastembed PR #830 merged and released (for REQ-002 only; REQ-001 is independent).

### Task List

#### Phase 100: certifi bump (standalone PR)

- [x] Task 100.100: Run `uv lock --upgrade-package certifi` and confirm the lock lands on a certifi release ≥ 2026.10.19 (snapshot latest: 2026.10.23) with nothing else moved.
- [x] Task 100.110: Verify with `uv sync --frozen --all-extras`, `uv run --frozen ruff format --check` + `uv run --frozen ruff check`, and `uv run --frozen pytest -n auto --cov=src --cov-report=`.
- [x] Task 100.120: The orchestrator commits `chore(deps): bump certifi` (one local Conventional Commit; no push/PR/merge within the phase — see the workflow override in Decisions Made) and records in Progress that alert 29's closure is expected on merge + Dependabot re-scan (Dependabot re-scans on its own schedule after a branch update).

#### Phase 105: virtualenv / filelock / opentelemetry-api bump (lock-only)

- [ ] Task 105.100: Run `uv lock --upgrade-package virtualenv --upgrade-package filelock --upgrade-package opentelemetry-api` and confirm the lock lands on virtualenv ≥ 21.14.9, filelock ≥ 4.2.1, opentelemetry-api ≥ 1.45.1 with nothing else moved — except the documented, resolver-forced `packaging` 26.2 → 26.3 move (a new `virtualenv → packaging` edge), required by every virtualenv ≥ 21.14.9's `packaging>=26.3` declaration (user-approved exception, see Decisions Made) (Phase 100's certifi bump is the only prior diff).
- [ ] Task 105.110: Verify with `uv sync --frozen --all-extras`, `uv run --frozen ruff format --check` + `uv run --frozen ruff check`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, and `uv run --frozen pytest -m embedding_model` (filelock 3 → 4 is a major bump on the fastembed → huggingface-hub model-cache path; the real-backend test is the direct exercise of it).
- [ ] Task 105.120: The orchestrator commits `chore(deps): bump virtualenv, filelock, opentelemetry-api` (one local Conventional Commit; no push/PR/merge within the phase — see the workflow override in Decisions Made) and records in Progress that the 19 affected alerts (15 virtualenv, 3 filelock, 1 opentelemetry-api) are expected to close on merge + Dependabot re-scan.

#### Phase 110: pillow 13 via fastembed (blocked on upstream)

- [ ] Task 110.100: Track qdrant/fastembed#830 (the `chore(deps): allow pillow 13` PR); optionally comment on qdrant/fastembed#829 (the upstream `[Feature]: Support pillow 13` issue) pointing at the 9 open advisories on 12.3.0.
- [ ] Task 110.110: On release, run `uv lock --upgrade-package fastembed --upgrade-package pillow` and confirm pillow resolves ≥ 13.0.0.
- [ ] Task 110.120: Verify with the default suite plus `uv run --frozen pytest -m embedding_model`; the orchestrator commits `chore(deps): bump fastembed + pillow` (one local Conventional Commit; no push/merge — see the workflow override in Decisions Made) and records in Progress the expected closure of the 41 pillow alerts on merge + Dependabot re-scan.

#### Phase 120: final verification

- [ ] Task 120.100: Run the open-alerts API query (Dependabot re-scans on its own schedule after a branch update — allow for that before treating a still-open alert as a failed bump), confirm all alerts have closed or note which re-scan is pending, and record the final state in Progress.
- [ ] Task 120.110: Confirm which branch(es) Dependabot monitors; alert 28 needs no repo change from this feature (the #226 fix is on dev) and closes once the monitored branch carries it, else record the promotion dependency in Progress.

## Progress

### Current Status

**As of 2026-10-24**: Phase 100 (certifi) complete — lock resolved certifi 2026.10.23, full gate green (uv sync --frozen --all-extras, ruff format/check, full default pytest suite). Orchestrator commit `chore(deps): bump certifi` follows (uv.lock + this README); alert 29's closure is expected on merge + Dependabot re-scan. Phase 105 is next; Phase 110 remains blocked on qdrant/fastembed#830 (open/unmerged as of 2026-10-24); Phase 120 follows.

### Blockers

- qdrant/fastembed#830 (`chore(deps): allow pillow 13`, the cap raise to `<14.0`) is open/unmerged — blocks Phase 110 (REQ-002, ACC-002) only; Phase 100 proceeds independently.
- Contingency if #830 closes unmerged or goes stale: revisit the risk acceptance (Decisions Made) — propose the cap-raise patch to upstream ourselves, or formally re-record the continued exposure with a dated review. Phase 110 must not become a silent, indefinite parking lot.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T11:51:54.000Z - Plan amendment: Phase 105 documented exception (packaging 26.2 → 26.3, user-approved)

Phase 105's first run hit the plan's STOP condition: `uv lock --upgrade-package virtualenv --upgrade-package filelock --upgrade-package opentelemetry-api` landed all three targets compliant (virtualenv 21.14.13, filelock 4.2.4, opentelemetry-api 1.45.1) but also forced `packaging` 26.2 → 26.3 (a new `virtualenv → packaging` edge — every virtualenv ≥ 21.14.9 declares `packaging>=26.3`; the lock carried 26.2). The subagent applied the STOP condition, reverted the lock, and ran no gate (worktree stayed clean). User decision (Option 1, see Decisions Made): accept the forced move as a documented exception; Task 105.100's wording is amended accordingly and Phase 105 re-runs under the corrected invariant (lock diff confined to the four entries filelock, opentelemetry-api, packaging, virtualenv plus the new edge; full gate including `pytest -m embedding_model`).

#### 2026-10-24T11:08:55.000Z - Phase 100 complete: certifi 2026.7.22 → 2026.10.23 (lock-only)

Phase 100 executed. Task 100.100: `uv lock --upgrade-package certifi` landed certifi at 2026.10.23 (≥ 2026.10.19 per REQ-001; exactly the snapshot's latest release), and the lock diff is confined to the certifi `[[package]]` entry — version + sdist/wheel metadata (`git diff --stat uv.lock`: `uv.lock | 6 +++---`, 1 file changed, 3 insertions(+), 3 deletions(-); no other package moved). Task 100.110: full gate green — `uv sync --frozen --all-extras` exit 0 ("Checked 110 packages", certifi 2026.10.23 installed), `uv run --frozen ruff format --check` exit 0 ("2113 files already formatted"), `uv run --frozen ruff check` exit 0 ("All checks passed!"), `uv run --frozen pytest -n auto --cov=src --cov-report=` exit 0 ("4759 passed, 18 skipped in 48.87s"). Per the workflow override (Decisions Made, 2026-10-24T10:56:48.000Z), the orchestrator commits this phase as `chore(deps): bump certifi` (uv.lock + this README, one local Conventional Commit, no push); alert 29 (certifi, GHSA-6q48-6c7w-9gw2) is expected to close on merge + Dependabot re-scan.

#### 2026-10-24T10:56:48.000Z - Plan amended: scope expansion for the 06:04Z re-scan cohort (user-approved)

The 06:04–06:05Z Dependabot re-scan created 51 new alerts (62 open total): 32 additional pillow alerts (all first-patched 13.0.0, joining the pre-rescan 9 for 41 total), 15 virtualenv (21.7.13; first-patched 21.14.2/21.14.4/21.14.7/21.14.9; 7 high/5 medium/3 low), 3 filelock (3.32.2 → 4.2.1; 1 high/2 low), 1 opentelemetry-api (1.44.0 → 1.45.1; medium). The pre-rescan 11-alert snapshot below (alerts 28–38, the 2026-10-21 cohort) is unchanged and remains the record of the original triage; alert 28 (uv) is confirmed stale — `dev` already carries 0.13.4 via merged PR #226 and this branch's lock resolves uv 0.13.4. The new non-pillow cohort is lock-only fixable: the dependents' declared constraints carry no blocking upper cap (huggingface-hub 1.32.0: `filelock>=3.10.0`; python-discovery 1.6.1: `filelock>=3.15.4`; pre-commit 4.6.1: `virtualenv>=20.10.0`; mcp 2.3.0: `opentelemetry-api>=1.28.0` — verified against PyPI 2026-10-24). User decision (option A): expand — new REQ-004/ACC-004 + Phase 105, workflow override recorded in Decisions Made, no upstream posting on fastembed#829. qdrant/fastembed#830 re-verified open/unmerged 2026-10-24 (Phase 110 stays blocked).

#### 2026-10-24T10:38:00.000Z - Plan refined (second refiner pass)

Second refinement pass over the plan (addressing the findings of a refiner review): alert 28's snapshot line now names the vulnerable monitored-branch version (`0.12.1`, per the alert's own `version_requirement`) instead of the incoherent "locked 0.13.4, fixed in 0.13.4" — dev already carries the 0.13.4 remediation via #226, and the advisory names no first-patched version; the snapshot header now states its locked versions are from **dev**'s `uv.lock`; the "two re-dated entries" in the previous entry are made explicit (the `Created` log entry and the Risk-accept decision entry); the risk acceptance is now bounded with revisit triggers (a)–(c); a #830-stall contingency is added to Blockers; the no-exposure argument gains a verified fact (locked fastembed 0.8.0 has no `PIL`/`pillow` import in its Python source — metadata-only). No task status changes — Phase 100 remains ready to execute.

#### 2026-10-24T07:35:12.000Z - Plan refined (refiner pass)

A refinement pass over the plan: the two `06:19:13.000Z` entries (the `Created` log entry and the Risk-accept decision entry) are re-dated to `06:21:00.912Z` to match the frontmatter `created` (the create tool's birth stamp is authoritative — the log entries were backdated to the session start); alert 28's closure is now conditioned on the Dependabot-monitored branch (new Task 120.110; softened wording in `### Related PRs / Commits` and `### More Information`); `### Blockers` added; fastembed#829 (the upstream `[Feature]: Support pillow 13` issue) made self-explanatory in Task 110.100; verification commands aligned to AGENTS.md's `uv run --frozen` form; re-scan-wait guidance added to the alert-confirmation tasks; Task 100.100 now matches REQ-001's `≥` flexibility; REQ-002 states the expected `<14.0` cap and REQ-003 carries no reasoning; the risk-accept decision cites its verification command; the title is now descriptive. No task status changes — Phase 100 remains ready to execute.

#### 2026-10-24T06:25:18.000Z - Close-out: triage complete, handoff ready

Session close-out: all 11 open alerts triaged (snapshot plus the fastembed pin rationale in `### More Information`). Phase 100 (certifi) is immediately executable — no upstream dependency. Phase 110 (pillow) is blocked on qdrant/fastembed#830 being merged and released; until then pillow 12.3.0 is risk-accepted (see Decisions Made). No repo change was made this session beyond this feat document; the feat folder is still untracked — commit it before starting Phase 100.

#### 2026-10-24T06:21:00.912Z - Created

Feat created for GitHub issue #232 (dependabot: security alerts): 11 open alerts on `uv.lock` (9× Pillow, 1× certifi, 1× stale uv). The certifi bump goes first as a standalone PR; Pillow is blocked on fastembed's `pillow<13.0` cap.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-24T11:51:54.000Z - Phase 105 documented exception: resolver-forced packaging 26.2 → 26.3 (user-approved, Option 1)

Running Task 105.100's command resolves virtualenv/filelock/opentelemetry-api to the compliant versions but forces `packaging` 26.2 → 26.3 (a new `virtualenv → packaging` edge): every virtualenv in REQ-004's compliant range declares `packaging>=26.3` (verified against PyPI 2026-10-24 for 21.14.9 — the floor — and 21.14.13 — the latest —; the lock carried 26.2), so REQ-004 is unsatisfiable without the move. packaging 26.3 is the latest release, is not part of the 62-alert population, adds no new exposure, and the full 120-package graph resolved with zero conflicts (build/onnxruntime/pytest/twine — the packaging dependents — all accept 26.3). User decision (Option 1): accept the forced move as a documented exception to Task 105.100's "nothing else moved" invariant; the lock diff must still be confined to the four entries filelock, opentelemetry-api, packaging, virtualenv (plus the new edge). Option 2 (de-scope virtualenv, leaving the 15 virtualenv alerts — 7 high — open) was rejected.

#### 2026-10-24T10:56:48.000Z - Scope expansion + workflow override (user decision)

(a) Scope: the plan expands from the original 11-alert snapshot to the full 62-alert population created by the 06:04Z re-scan. The 19 new non-pillow alerts (15 virtualenv, 3 filelock, 1 opentelemetry-api) are in scope as Phase 105 (REQ-004/ACC-004): all three packages are transitive-only (no direct import in `src/` or `tests/`, verified 2026-10-24), lock-only fixable, and no dependent's declared constraint caps the fixed version. (b) Workflow: per user instruction, each phase ends in one local Conventional Commit with no push; the plan's per-phase "open the PR, merge" steps are deferred to the feature wrap-up (single PR to `dev`, no merge); "confirm alert closes" becomes "record expected closure on merge + Dependabot re-scan". (c) No posting on upstream qdrant/fastembed#829 (Task 110.100's optional comment is waived).

#### 2026-10-24T06:21:00.912Z - Risk-accept pillow 12.3.0 while waiting on fastembed

Zero PIL imports in `src/`/`tests/` (verified 2026-10-24: `grep -rniE "PIL|pillow" src/ tests/` matches nothing) and fastembed is used strictly as `TextEmbedding` (the only construction site: `src/biz/dfch/specmgr/general/tools/_embedding.py:582`; the locked fastembed 0.8.0 package itself carries no `PIL`/`pillow` import in its Python source — the cap appears only in its `Requires-Dist` metadata), so the 9 Pillow advisories (all in image-parsing paths: JPEG/TIFF/GIF/PDF/EPS) carry no practical exposure in this codebase. Forcing pillow 13 via a uv override is rejected (it would violate fastembed's declared constraint). Waiting on the upstream cap raise has precedent: fastembed#606 cut 0.7.5 to unblock pillow 12.x under CVE pressure. The acceptance is bounded: it holds until the pillow 13 bump lands (REQ-002) and is revisited immediately if (a) fastembed's text-embedding path starts exercising image parsing, (b) this repo gains a direct PIL/pillow import, or (c) qdrant/fastembed#830 closes unmerged or goes stale (see the Blockers contingency).

### Related PRs / Commits

- dev already carries the uv fix (PR #226, commit `b65d8c3`); dashboard alert 28 closes once the Dependabot-monitored branch carries it (the monitored branch is confirmed in Phase 120, Task 120.110).

### More Information

Open-alert snapshot as of 2026-10-24 (via `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open`; locked versions from **dev**'s `uv.lock` — alert 28's vulnerable version is the monitored branch's, per the alert itself):

Note (2026-10-24 amendment): the 11-alert list below is the pre-rescan 2026-10-21 cohort (alerts 28–38). The 06:04Z re-scan added 51 more (62 open total): 32 additional pillow alerts (alerts 43–59 and the pillow-numbered alerts 60–79 — all first-patched 13.0.0), 15 virtualenv (alerts 39–42, 62–64, 77, 81–87), 3 filelock (alerts 80, 88, 89), 1 opentelemetry-api (alert 75). Fixed versions and dependents' constraints are in the Updates entry and REQ-004.

- **28 — uv** (direct, `dev` extra): the alert reports the monitored branch locked at `0.12.1` (vulnerable); dev already carries the fix — 0.13.4 via #226 (GHSA-hq85-5cpj-mr62, critical — emSign CA compromise in uv's vendored webpki bundle; the advisory names no first-patched version, so 0.13.4 is the remediation #226 chose). Closes once the Dependabot-monitored branch carries 0.13.4 (branch to be confirmed in Phase 120).
- **29 — certifi** (transitive: httpx/requests/httpcore): locked 2026.7.22, fixed in 2026.10.19, latest 2026.10.23 (GHSA-6q48-6c7w-9gw2, critical — emSign root CA with compromised intermediate keys). No pin blocks the bump — Phase 100.
- **30–38 — pillow** (transitive: fastembed): locked 12.3.0, all nine fixed in 13.0.0 (1×critical GHSA-8g5g-8vmr-9782, 6×high, 2×medium — all image-parsing paths: JPEG/TIFF/GIF/PDF/EPS). Blocked by fastembed's `pillow<13.0` cap.

Why fastembed caps pillow at <13.0: a stale major-version upper bound (fastembed caps every dependency: `numpy<2.3`, `onnxruntime<1.24`, `huggingface-hub<2.0`, …), not a known incompatibility — Pillow 13's breaking changes (Python 3.10 EOL, `I`-mode PNG save, `fromarray` mode parameter, `get_child_images()` move, `Image._show` removal, `ImageCms` attr removals, `ExifTags.IFD.Makernote` rename) do not touch fastembed's usage. fastembed's own PR #830 ("chore(deps): allow pillow 13", cap → `<14.0`) reports "image tests pass on Pillow 13.0.0"; as of 2026-10-24 it is open/unmerged (branch `chore/allow-pillow-13`) and the cap is present in 0.8.0 (locked), 0.9.0 (latest), and upstream `main`. Precedent for a release lifting the cap under CVE pressure: fastembed#606 (0.7.5 for pillow 12.x).
