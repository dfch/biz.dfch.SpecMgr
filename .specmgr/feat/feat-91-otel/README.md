---
classification: null
created: '2026-11-15T21:55:15.123+01:00'
id: feat-91-otel
status: planning
type: feat
updated: '2026-11-16T07:58:07.638+01:00'
version: 1.0.0
---

# Feature: Resolve Dependabot Alert #91 — opentelemetry-api 1.45.1 → 1.45.2 (CVE-2026-126360)

## Plan

### Overview

Dependabot security alert #91 (https://github.com/dfch/biz.dfch.SpecMgr/security/dependabot/91, published 2026-11-13) reports a regular-expression denial-of-service (ReDoS, CWE-1333, CVSS 5.3 / medium) in the transitive `opentelemetry-api` dependency locked at `1.45.1` in `uv.lock`. The affected code is `TraceContextTextMapPropagator.extract()`: a crafted `traceparent` value (a trace-context prefix followed by a long whitespace run and an embedded newline) triggers quadratic-time regex backtracking. The advisory explicitly names MCP request metadata (`params._meta`) as a relevant carrier, since OpenTelemetry carriers are not confined to HTTP headers and JSON strings can carry escaped newlines — the MCP SDK's built-in `OpenTelemetryMiddleware` (activated by the telemetry bootstrap landed on the feat-139 branch, not yet merged to `dev`) is one path by which an attacker-controlled `traceparent` could reach the propagator. This feature bumps the transitive lock entry to the first-patched release, `1.45.2` (which rejects `traceparent` values longer than 512 characters before regex matching and removes the overlapping-suffix / trailing-whitespace expressions), via a lock-only `uv lock --upgrade-package` change — the same vehicle feat-232 used for the prior `opentelemetry-api` alert (#75, 1.44.0 → 1.45.1). Dependabot's reachability analysis is disabled for this repository (alert `reachability.verdict = "disabled"`), so the alert stands on the presence of the vulnerable version; the bump is the correct remediation regardless of the current exposure surface.

### Requirements

- REQ-001: The `opentelemetry-api` lock entry in `uv.lock` moves from `1.45.1` to `>= 1.45.2` (first-patched) in a single lock-only `uv lock --upgrade-package opentelemetry-api` change, with the lock diff confined to the `opentelemetry-api` `[[package]]` entry (any resolver-forced collateral move is stopped and recorded as a documented exception, the feat-232 STOP-condition precedent).
- REQ-002: `opentelemetry-api` stays transitive — no `pyproject.toml` manifest change, no pin, no `override-dependencies`; the bump is driven purely by the advisory's first-patched version, not by any in-repo feature request.
- REQ-003: Alert #91 reports as resolved once the fix reaches the monitored branch (`dev`) and Dependabot re-scans; the feature records the expected closure and verifies it after merge.

### Acceptance Criteria

- [ ] ACC-001: `uv.lock` resolves `opentelemetry-api >= 1.45.2` (landed version recorded), and `uv sync --frozen --all-extras`, `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, and the opt-in `uv run --frozen pytest -m embedding_model` similarity test all pass.
- [ ] ACC-002: The `uv.lock` diff is confined to the `opentelemetry-api` `[[package]]` entry (plus any documented, resolver-forced collateral move), with no other package moved, no new `[[package]]` entry, and no manifest-section change.
- [ ] ACC-003: After the wrap-up PR merges to `dev` and Dependabot re-scans, `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open&per_page=100` no longer lists alert #91 as `open`, and the final open-alert state is recorded in Progress.

### Scope

#### Included

- The single lock-only `uv lock --upgrade-package opentelemetry-api` bump to `>= 1.45.2`.
- The standard quality-gate verification (sync + ruff format/check + default pytest suite + the opt-in `embedding_model` similarity test) and the lock-diff confinement check.
- Post-merge Dependabot re-scan verification that alert #91 closes.

#### Explicitly Out Of Scope

- Any `pyproject.toml` change (making `opentelemetry-api` direct, pinning it, or adding an override) — it stays transitive via the MCP SDK.
- Dismissing alert #91 without the version fix.
- The pillow cohort (GitHub issue #235) or any other alert — #91 is the only open alert at drafting time.
- Changes to the feat-139 telemetry implementation or the MCP SDK wiring — this feature only bumps the locked version; it does not alter how trace context is extracted.

### Dependencies

#### Depends On

- None in-repo. The bump is lock-only and independent of feat-139: `dev`'s lock already carries `opentelemetry-api 1.45.1` transitively via the MCP SDK, so the fix is available on `dev` now. When feat-139's telemetry lands on `dev` (after its planned rework), the bumped version carries over — the `uv.lock` merge must keep `>= 1.45.2` (the Design Notes' regression guard) — and the advisory's `params._meta` path is covered by the same lock entry.

### Design Notes

- **Why lock-only, not a manifest change.** `opentelemetry-api` enters the lock transitively via `mcp` (the MCP SDK declares `opentelemetry-api>=1.28.0`); there is no direct import in `src/` or `tests/`. The advisory's remediation is "upgrade to 1.45.2 or later", so `uv lock --upgrade-package opentelemetry-api` is the exact vehicle — the same one feat-232 Phase 105 used for the prior `opentelemetry-api` alert (#75, 1.44.0 → 1.45.1).
- **Collateral-move expectation.** A patch-level `1.45.1 → 1.45.2` move is expected to be collateral-free (unlike feat-232 Phase 105, where a `virtualenv` bump forced `packaging 26.2 → 26.3`). If the resolver does force another package to move, it is stopped and recorded as a documented exception rather than silently absorbed.
- **Gate scope.** Per the user decision 2026-11-15 ("test all"), the gate runs the full default suite plus the opt-in `pytest -m embedding_model` similarity test — mirroring feat-232 Phase 105's gate — even though `opentelemetry-api` is not on the fastembed → huggingface-hub model-cache path (that path is filelock's). The embedding test adds a complete verification pass over the resolved lock at no meaningful cost.
- **Reachability / exposure nuance.** Dependabot reachability analysis is disabled for this repo, so the alert is version-presence-based. On `dev` today the MCP SDK's OTel middleware is present, but its trace-context extraction is only active once a `TracerProvider` is configured (feat-139's bootstrap, not yet merged to `dev`); the advisory nonetheless names MCP `params._meta` as a live carrier, so the bump is applied now as defense-in-depth and to keep the feat-139 telemetry path covered the moment it lands.
- **feat-139 merge regression guard.** feat-139 is to be reworked before it can merge, and its own `uv.lock` still carries `opentelemetry-api 1.45.1` — so its eventual `dev` merge is a plausible lock-conflict site for this bump: the conflict must be resolved keeping `opentelemetry-api >= 1.45.2`, or the entry regresses to `1.45.1` and Dependabot re-opens alert #91 on the next re-scan.
- **Workflow (per the feat-232 house pattern for dependabot bumps).** Each phase ends in one local Conventional Commit (`chore(deps): bump opentelemetry-api`) with no push/PR/merge within the phase; a single wrap-up PR to `dev` is opened at the feature level; "confirm alert closes" is recorded as expected-on-merge + re-scan, then verified in the final phase.

### Related Decisions

- FEAT feat-232-dependabot-security-alerts (GitHub issue #232, "Resolve Dependabot Security Alerts in uv.lock", `done`) — the prior umbrella feature whose Phase 105 establishes the lock-only bump + gate + re-scan-verify pattern this feature reuses for the `opentelemetry-api` line.
- feat-139 ("Logging and Telemetry for the SpecMgr MCP Server", `done` on its branch) — the in-repo consumer whose MCP-SDK `OpenTelemetryMiddleware` makes the advisory's `params._meta` carrier relevant; listed for context, not a hard dependency.

### Task List

#### Phase 100: opentelemetry-api bump (lock-only)

- [ ] Task 100.100: Run `uv lock --upgrade-package opentelemetry-api` and confirm the lock lands on `opentelemetry-api >= 1.45.2` with nothing else moved; if the resolver forces a collateral package move, apply the STOP condition (revert the lock, record it, and raise it for a user-approved documented exception before proceeding) — the feat-232 Phase 105 precedent.
- [ ] Task 100.110: Verify with `uv sync --frozen --all-extras`, `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen pytest -n auto --cov=src --cov-report=`, and `uv run --frozen pytest -m embedding_model`; capture the pass/fail output and the landed version as ACC-001/ACC-002 evidence.
- [ ] Task 100.120: The orchestrator commits `chore(deps): bump opentelemetry-api` (one local Conventional Commit; no push/PR/merge within the phase — see the workflow note in Design Notes) and records in Progress that alert #91's closure is expected on merge + Dependabot re-scan.

#### Phase 110: final verification and close-out

- [ ] Task 110.100: After the wrap-up PR merges to `dev`, re-run `gh api repos/dfch/biz.dfch.SpecMgr/dependabot/alerts?state=open&per_page=100` once Dependabot has re-scanned, confirm alert #91 reports as resolved, and record the final open-alert state in Progress.
- [ ] Task 110.110: The orchestrator commits the close-out and sets the feature `status: done` once ACC-001/ACC-002/ACC-003 are all met.

## Progress

### Current Status

**As of 2026-11-15 (planning)**: Feature planned, not started. Dependabot security alert #91 is open (created 2026-11-14T06:22:38Z; advisory published 2026-11-13). `dev`'s `uv.lock` currently resolves `opentelemetry-api 1.45.1` (transitive via the MCP SDK); the advisory names `1.45.2` as the first-patched release. No repo change has been made — this document is the plan only; the single lock-only bump (Phase 100) is the entire in-repo closure path, and Phase 110 verifies the post-merge re-scan. Implementation has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-16T06:32:03.000Z - Plan refinement (feat-refiner findings)

Applied the read-only feat-refiner pass (no errors or discrepancies; findings G1, I1, I2, I3 — per the user, the I3 ask to record feat-139's status-verification basis is ignored, since feat-139 is to be reworked before it can merge): G1 — the Depends On bullet plus a new Design Notes "feat-139 merge regression guard" now pin the eventual feat-139 `uv.lock` merge conflict to keep `opentelemetry-api >= 1.45.2` (a regression to 1.45.1 would re-open alert #91 on Dependabot's next re-scan); I1 — the feat-232 Related Decisions bullet is retagged as the machine-resolvable feat-232-dependabot-security-alerts reference; I2 — the Overview's "landed in feat-139" reworded to "landed on the feat-139 branch, not yet merged to `dev`", consistent with the Reachability note. Requirements, ACCs, phases, and task numbers unchanged; status stays `planning`.

#### 2026-11-15T20:55:15.123Z - Created

Feat created for Dependabot security alert #91 (`opentelemetry-api` 1.45.1 → 1.45.2, GHSA-mf5v-w3w3-f6cg / CVE-2026-126360, medium, ReDoS in `TraceContextTextMapPropagator.extract()`). Alert metadata captured via `gh api .../dependabot/alerts?state=open` (the `state=all` aggregate returns empty in this environment; #91 is the single open alert). Plan mirrors feat-232 Phase 105's lock-only bump + gate + re-scan-verify pattern; per the user decision 2026-11-15 the gate runs the full default suite plus the opt-in `pytest -m embedding_model` similarity test. Implementation not started (plan only).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-15T20:55:15.123Z - User decisions: stand-alone feature + full "test all" gate

User decisions at drafting (2026-11-15): (a) this is a stand-alone feature (`feat-91-otel`), not a revision of the already-`done` feat-232 umbrella — alert #91 post-dates feat-232's close-out (created 2026-11-14) and is a single, self-contained lock-only bump; the `91` id tracks the Dependabot alert number (the original GitHub issue #91 is deleted/410). (b) The verification gate runs "test all" — the full default suite plus the opt-in `pytest -m embedding_model` similarity test (mirroring feat-232 Phase 105) — rather than the minimal default-only suite the initial proposal offered; `opentelemetry-api` is not on the fastembed/huggingface-hub model-cache path, but the embedding test is included for a complete verification pass.
