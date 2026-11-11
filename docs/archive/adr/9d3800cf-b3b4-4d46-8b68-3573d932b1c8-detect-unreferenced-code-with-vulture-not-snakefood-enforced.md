---
status: accepted
decision-makers: dfch
id: 9d3800cf-b3b4-4d46-8b68-3573d932b1c8
version: 1.0.0
---

# Detect unreferenced Python Code

## Context and Problem Statement

Refactors and abandoned experiments leave behind functions, classes, and variables that no caller ever exercises. Without automated detection, this unreferenced code accumulates silently, adding maintenance burden and cognitive load, and is only ever found by chance during manual review. We need a tool that (1) finds unreferenced Python symbols across the codebase, (2) can be enforced automatically in both local pre-commit hooks and CI so findings can't silently drift between the two, (3) offers a way to suppress known framework-driven false positives (Pydantic validators, MCP resource/tool registration, Typer's callback pattern) without hiding genuine findings, and (4) lets us separately identify production code that is exercised only by the test suite, never by a real caller -- a signal that a symbol may not actually be needed outside of tests.

## Decision Drivers

Automated, low-maintenance tooling that fits the existing uv/ruff/pylint/pytest toolchain; an actively maintained project; per-symbol usage analysis, not just module-level import graphing; ability to distinguish genuine unreferenced code from framework-invoked false positives without silencing true findings; ability to flag code whose only caller is the test suite itself.

## Considered Options

snakefood, vulture

## Decision Outcome

Chosen option: "vulture", because it performs real per-symbol static usage analysis via Python's `ast` module, is actively maintained, and integrates trivially into the existing `uv`-managed toolchain -- unlike snakefood, which only builds module-level import/dependency graphs and cannot find an unreferenced function, class, or variable at all, and appears unmaintained. `vulture` was added to the `test` extra in `pyproject.toml`, wired into a local `vulture` hook in `.pre-commit-config.yaml`, and mirrored as a step in `.github/workflows/ci.yml` across the full Python 3.11/3.12/3.13 matrix -- both run the identical `uv run --frozen vulture src/ whitelist.py --min-confidence 60` command so pre-commit and CI can never drift apart. Known framework-driven false positives (Pydantic `@field_validator`/`@model_validator` methods and `model_config`, MCP `@mcp.resource()`/`@mcp.tool()` entry points, Typer's `_callback` pattern) are suppressed through a hand-curated, comment-grouped `whitelist.py` at the repo root, kept deliberately narrow -- a name is only added after confirming by inspection that it's a genuine framework false positive, not real unreferenced code, which is removed instead. Separately, production code exercised only by the test suite is surfaced via `specmgr unused-code --test`: a CLI command that scans `src/` alone versus `src/` together with `tests/` and diffs the two finding sets; names that vanish once tests are included are referenced exclusively from test code and are worth manual review as a possible orphaned public surface. The same command without `--test` is a friendlier wrapper around the enforced pre-commit/CI invocation, sparing contributors from remembering the raw `vulture src/ whitelist.py --min-confidence 60` call.

### Consequences

Good, because unreferenced symbols are now caught automatically at commit time and again in CI, instead of relying on occasional manual review. Good, because the whitelist keeps false-positive noise from framework decorators from drowning out genuine findings, and documents *why* each suppressed name is safe, not just that it is. Good, because the test-only-usage technique gives an additional, previously unavailable signal for auditing whether the test suite is the sole reason a symbol is still considered used, and `specmgr unused-code --test` makes it a repeatable, documented command instead of an ad hoc shell one-liner. Bad, because the whitelist requires ongoing manual curation -- a new Pydantic validator or MCP entry point needs a deliberate whitelist addition, or it will fail the pre-commit hook and CI. Neutral, because the test-only-usage comparison (`specmgr unused-code --test`) is not wired into pre-commit/CI by default -- it supports an opt-in `--strict` flag for that, but enforcing it automatically would require deciding how to handle its false positives (Pydantic fields set only via keyword construction, legitimate public API surface only exercised so far from tests) first, the same way `whitelist.py` does for the default mode.

### Confirmation

`uv run --frozen vulture src/ whitelist.py --min-confidence 60` exits 0 on a clean tree; `uv run --frozen pre-commit run vulture --all-files` passes; CI's "Check for unreferenced code with vulture" step (see `.github/workflows/ci.yml`) is green across the 3.11/3.12/3.13 matrix; introducing a genuinely unreferenced function locally and committing without removing or justifiably whitelisting it is blocked by the pre-commit hook.

## Pros and Cons of the Options

### Option 1: snakefood

* Bad, because it only builds module-level import/dependency graphs -- it cannot find an unreferenced function, class, method, or variable within a module at all, which is the actual requirement here.
* Bad, because it appears unmaintained: no meaningful release activity in well over a decade, and it originally targeted an earlier Python major version.
* Neutral, because it could still be useful later for a separate concern (visualizing the module dependency graph or catching circular imports), just not for this decision.

### Option 2: vulture

* Good, because it performs real per-symbol static usage analysis via Python's `ast` module, directly matching the requirement.
* Good, because it is actively maintained and trivially installable via `uv` alongside the existing `ruff`/`pylint`/`mypy` toolchain.
* Good, because it assigns a confidence score per finding and supports a whitelist mechanism, letting genuine framework false positives be suppressed individually and explicitly instead of raising the confidence threshold globally and losing real findings.
* Neutral, because it is still name-based, not type-aware, static analysis -- every finding (and every whitelist addition) still needs a brief manual confirmation before code is deleted or suppressed.

## More Information

See `whitelist.py` for the categorized list of suppressed false positives and the policy note at its top. The pre-commit hook and CI step intentionally run the identical command to avoid drift between local and CI enforcement (see also the ADR "Enforce doc generation, lint, and tests locally via pre-commit hook, not just CI" for the broader rationale behind local+CI enforcement). Test-only-usage detection: `uv run --frozen specmgr unused-code --test` (`src/biz/dfch/specmgr/commands/unused_code.py`), which internally compares a `vulture` scan of `src/` alone against a scan of `src/` together with `tests/`, diffed by extracted symbol name; the same command without `--test` reports the default, enforced-in-CI findings.
