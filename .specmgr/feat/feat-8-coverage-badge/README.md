---
created: '2026-08-13 00:00:00.000Z'
id: feat-8-coverage-badge
status: done
updated: '2026-10-07T06:21:40.950Z'
version: 1.0.0
---

# Feature: Add coverage badge with SVG generation and CI/pre-commit enforcement

## Plan

### Overview

Add a self-hosted code coverage badge to the README via a new CLI command (`specmgr coverage-badge`) that generates a static SVG file (`docs/coverage.svg`). The badge is automatically regenerated on every test run and validated for freshness in pre-commit and CI, ensuring it stays in sync with actual coverage measurements without external service dependencies (Codecov, Gist, shields.io dynamic badge, etc.).

### Requirements

- REQ-001: Generate SVG coverage badges locally with no external dependencies
- REQ-002: Measure code coverage as part of the existing test suite (no separate run)
- REQ-003: Badge color reflects coverage threshold (≥90% green, ≥75% yellowgreen, ≥50% yellow, else red)
- REQ-004: CLI command (`specmgr coverage-badge`) reads `.coverage` data and writes `docs/coverage.svg`
- REQ-005: Pre-commit hook enforces badge freshness on every source/test file change
- REQ-006: CI validates badge freshness on Python 3.13 (pinned, like `docs/` and `adr-toc` checks)
- REQ-007: README includes the coverage badge in the existing badge row
- REQ-008: Documentation is updated (API docs, CHANGELOG)

### Acceptance Criteria

- [x] ACC-001: `[tool.coverage.run]` config added to `pyproject.toml` with `source = ["src"]`
- [x] ACC-002: `src/biz/dfch/specmgr/commands/coverage_badge.py` created with SVG rendering logic
- [x] ACC-003: Command functions: `_get_coverage_percentage()`, `_color_for_coverage()`, `_render_svg_badge()`, `coverage_badge()`
- [x] ACC-004: Command registered in `commands/__init__.py` and `cli.py`
- [x] ACC-005: Unit tests written in `tests/commands/test_coverage_badge.py` covering color thresholds, SVG generation, file I/O, error cases
- [x] ACC-006: CI updated: `"Run unit tests"` step changed to `coverage run`, badge validation step added (3.13 only)
- [x] ACC-007: Pre-commit updated: `unittest` hook changed to `coverage run`, new `specmgr-coverage-badge` hook added
- [x] ACC-008: `docs/coverage.svg` generated and committed (96% coverage at completion)
- [x] ACC-009: README badge row includes `![Coverage](docs/coverage.svg)` after CI badge
- [x] ACC-010: CHANGELOG.md `[Unreleased]` entry added describing the feature
- [x] ACC-011: `specmgr docs` regenerated (`docs/api/`, `docs/GENERATED.md` updated)

### Scope

#### Included

- CLI command with SVG badge generation
- Unit tests for all functions
- pyproject.toml coverage config
- README badge integration
- CI and pre-commit hook wiring
- docs generation and CHANGELOG update
- Feature tracking document (this file)

#### Explicitly Out Of Scope

- Supporting coverage badges for specific test files/modules (only overall %)
- Custom color palettes or badge styles
- Integration with external coverage services

### Dependencies

#### Depends On

- `coverage` — already in the `test` extra (no new dependency)
- No changes to existing domain packages (adr, general, uc, models)

### Design Notes

**SVG rendering:**

- Hand-written flat-style SVG (no external library like `genbadge` or `coverage-badge`)
- Single-purpose: label "coverage", value "NN%"
- Colors follow shields.io thresholds for consistency with other metric badges
- No rounded corners or gradients — minimalist design, fast rendering

**Coverage flow:**

1. Tests run via `coverage run -m unittest discover ...` (not plain `python -m unittest`)
2. `.coverage` binary data file is produced as a byproduct
3. `specmgr coverage-badge` reads `.coverage`, calls `Coverage().load()`, invokes `cov.report()` to get percentage
4. SVG is rendered and written to `docs/coverage.svg`
5. Pre-commit hook runs `specmgr coverage-badge` and fails if badge is stale
6. CI (Python 3.13 only) also runs the check, matching `docs/` and `adr-toc` behavior

**Error handling:**

- Missing `.coverage` file → clear error message instructing user to run tests first
- `Coverage.report()` returns `None` → explicit failure with diagnostic message
- Invalid output path → parent directory is created (mkdir -p semantics)

### Related Decisions

None yet. Coverage badge generation and CI/pre-commit integration is implementation-level, not architecture-level.

### Task List

#### Phase 100: Implementation

- [x] Task 100.100: Add `[tool.coverage.run]` config to `pyproject.toml`
- [x] Task 100.110: Create `commands/coverage_badge.py` with full implementation
- [x] Task 100.120: Register command in `commands/__init__.py` and `cli.py`
- [x] Task 100.130: Write comprehensive unit tests (`tests/commands/test_coverage_badge.py`)
- [x] Task 100.140: Update `.github/workflows/ci.yml` to run coverage and validate badge
- [x] Task 100.150: Update `.pre-commit-config.yaml` with coverage hook
- [x] Task 100.160: Add coverage badge to README.md badge row
- [x] Task 100.170: Run `specmgr docs` to regenerate API docs and GENERATED.md
- [x] Task 100.180: Add CHANGELOG.md entry under [Unreleased] → Added
- [x] Task 100.190: Create this feature tracking document

## Progress

### Current Status

**As of 2026-08-15**: Done. All 10 tasks above are complete and the feature was tested locally (96% coverage). GitHub issue #8 was assigned for backfill and the folder renamed from `feat-0-coverage-badge` to `feat-8-coverage-badge`.

### Updates

#### 2026-08-15 00:00:00.000Z - Housekeeping: assigned GitHub issue

Opened and immediately closed [GitHub issue #8](https://github.com/dfch/biz.dfch.SpecMgr/issues/8) (feature was already completed) purely to backfill an issue number; renamed the folder `feat-0-coverage-badge` → `feat-8-coverage-badge` and updated the frontmatter `id` to match.

### Decisions Made

#### 2026-08-13 00:00:00.000Z - No external service

Self-hosted SVG avoids Codecov/Gist/shields.io complexity and secret management.

#### 2026-08-13 00:00:00.000Z - One test run, not two

`coverage run` is used instead of plain `python -m unittest`, so coverage measurement is a free byproduct. No performance penalty.

#### 2026-08-13 00:00:00.000Z - Pinned to Python 3.13 for CI badge check

Matches existing `docs/` and `adr-toc` checks. Ensures single canonical source of truth for badge content (different Python versions might format SVG slightly differently; keeping one version avoids unnecessary churn).

#### 2026-08-13 00:00:00.000Z - Flat-style SVG with minimal dependencies

Hand-written SVG avoids adding a new CLI tool dependency. Simple, auditable, fast.

#### 2026-08-13 00:00:00.000Z - Color thresholds from shields.io

Users familiar with shields.io badge colors will recognize the coverage level at a glance.

### More Information

#### Known Limitations

- **Single overall percentage:** Badge shows total coverage only, not per-module/per-file breakdowns.
- **SVG rendering is simplistic:** No attempt to match shields.io's exact rendering fidelity (fonts, sizing, gradients). The badge is functional and readable, not pixel-perfect.
- **No coverage trend:** Badge shows current coverage, not historical trends or delta from previous commits.
- **Badge is static:** If coverage changes between test runs, the badge must be explicitly regenerated (automatic via pre-commit, or manual `specmgr coverage-badge`).
