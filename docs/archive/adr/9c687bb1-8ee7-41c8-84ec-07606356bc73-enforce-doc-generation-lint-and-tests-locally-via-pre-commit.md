---
status: accepted
decision-makers: dfch
id: 9c687bb1-8ee7-41c8-84ec-07606356bc73
version: 1.0.0
---

# Enforce doc generation, lint, and tests locally via pre-commit hook, not just CI

## Context and Problem Statement

Code quality checks (linting, formatting, tests) and documentation generation can be enforced in two places: (1) CI only (GitHub Actions, GitLab CI), which is slow feedback (developers push, then wait for CI to fail), or (2) locally via pre-commit hooks (before the commit is created), which is fast feedback. The trade-off is that CI still needs the same checks as a safety net (in case a developer bypasses hooks).

## Decision Drivers

Fast developer feedback; catching issues locally before pushing; preventing broken commits from reaching the repository; consistency with sibling-project conventions (already using pre-commit for ruff format/check).

## Considered Options

Pre-commit hooks vs. CI-only enforcement.

## Decision Outcome

Register a `.pre-commit-config.yaml` hook that runs before every commit: (1) `ruff format --check` and `ruff check` for style/lint; (2) full `unittest` suite (scoped to changed Python files under src/ and tests/); (3) `specmgr docs` to validate generated documentation is not stale (docs/api/, docs/GENERATED.md). If any check fails, the commit is blocked with a clear error message, and the developer must fix the issue and try committing again. The same checks remain in CI as a final safety net, but local pre-commit enforcement provides immediate feedback during development.

### Consequences

Developers see failures immediately (seconds) instead of waiting for CI (minutes). Broken tests and documentation drift are caught before pushing. Trade-off: developers must fix issues locally; they cannot commit with broken tests or stale docs (by design). The pre-commit hook can be temporarily disabled with `--no-verify` if absolutely necessary, but this is a rare escape hatch, not the default path.

### Confirmation

Verify `.pre-commit-config.yaml` is registered and enabled locally via `pre-commit install` (one-time setup per clone); verify a broken test or linting violation blocks a commit; verify `specmgr docs` drift is caught and blocks commits.

## More Information

.pre-commit-config.yaml defines the hooks and their scope (src/**/*.py, tests/**/*.py changes only). See AGENTS.md for the one-time setup command: `uv run --frozen pre-commit install`.
