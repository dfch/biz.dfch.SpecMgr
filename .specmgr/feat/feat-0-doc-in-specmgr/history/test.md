---
status: rejected
date: '2026-08-03'
decision-makers: Platform Engineering Team
id: deaddead-dead-dead-dead-deaddeaddead
version: 1.0.0
---

# Choice of Python Minor Version (3.11 vs 3.13)

## Context and Problem Statement

Our projects need a standard Python minor version to ensure consistency and simplify dependency resolution. Choosing between Python 3.11 and 3.13 involves trade-offs: 3.11 offers broad library support and maturity, while 3.13 provides newer features and performance gains at the risk of narrower ecosystem readiness.

Key considerations include CI/CD tooling compatibility (GitHub Actions, GitLab CI), cloud deployment targets (AWS Lambda runtimes, Google Cloud Run), third-party library version minimums, and team familiarity with new features like exception group chaining and F-string enhancements.

## Decision Drivers

- Compatible library and framework support (all transitive dependencies must work)
- Performance gains from newer interpreter releases
- Longest remaining support window for security fixes
- Ecosystem maturity for data-science / scientific packages
- CI/CD pipeline compatibility
- Cloud deployment target requirements
- Avoiding future upgrade cycles (migrating 3.11 -> 3.13 in 2 years)
- Access to newer language features and syntax improvements

## Considered Options

Python 3.11 vs Python 3.13 vs Python 3.14

Python 3.11 is the mature, broadly compatible choice with security fixes until October 2027; it has no option to disable the GIL. Python 3.13 is the current latest stable release adopted by the team, with longer support (until ~2029) and newer performance optimizations; it ships an experimental, opt-in free-threaded (no-GIL) build (PEP 703), but the GIL is still enabled by default and most C-extension packages don't yet support the free-threaded variant. Python 3.14 was also evaluated as the newest stable release, but is not yet viable for this project because key dependencies (spaCy, CUDA/PyTorch-based ML tooling) do not yet support it.

Key considerations include CI/CD tooling compatibility, cloud deployment targets, third-party library version minimums (Django, FastAPI, NumPy, Pillow, spaCy, PyTorch/CUDA release notes), GIL/free-threading status, and team familiarity with new features.

## Decision Outcome

Chosen option: Python 3.13.

All new projects will use Python 3.13. Existing projects will be upgraded to Python 3.13. Python 3.11 will continue to be supported for projects that have not yet migrated, until Python 3.11 reaches its own end-of-life in October 2027; after that date, all remaining 3.11 projects must have migrated to 3.13 (or whatever version is current at that time, pending a future ADR).

### Consequences

- Good: CI tooling will pin to a single interpreter major.minor for all new work
- Good: lockfiles (uv.lock / poetry.lock) can reference the chosen version explicitly
- Bad risk: if 3.13 is picked too early, key dependencies may not be compatible
- Neutral: both versions share the same typing and packaging standards
- Neutral: migration back to an older version would require another ADR process
- Neutral: 3.11 and 3.13 must be supported side by side until October 2027, meaning CI matrices and dependency compatibility checks for not-yet-migrated projects must keep covering both versions until then

### Confirmation

Adoption is confirmed by:

1. Verifying all project dependencies declare compatibility with Python 3.13 (checking PyPI classifiers).
2. Running CI pipelines on a pilot repo.
3. Confirming cloud provider / deployment targets support the 3.13 runtime.

## Pros and Cons of the Options

### Option 1: Python 3.11

[Python 3.11](https://peps.python.org/pep-0704/) is the mature, broadly compatible choice. Released October 2023 · **EOL: October 2027**.

Pros:
- Widely adopted by virtually all Python libraries and frameworks
- Security fix support until October 2027 (4 years from release)
- Well-tested in production by the broader community — fewer edge-case bugs
- Lower risk for data-science packages with complex native dependencies (GDAL, CUDA bindings)
- Established tutorials, Stack Overflow answers, and blog posts cover common issues

Cons:
- Will reach end-of-life sooner than 3.13 (~2029) — only ~3 years of remaining support from today
- Less performance per-line than 3.13 due to missing optimizations from 3.12+ (exception grouping, improved F-string parsing)
- Requires another version migration within 2-3 years
- No option to disable the GIL at all — CPU-bound multi-threaded code cannot use multiple cores natively, forcing workarounds via multiprocessing or async I/O

### Option 2: Python 3.13

[Python 3.13](https://peps.python.org/pep-0719/) is the current latest stable release. Released October 2024 · **EOL: October 2029**.

Pros:
- Longest remaining support window — until approximately October 2029 (6 years from today)
- Newest performance optimizations and language features (exception groups, F-string enhancements, improved GIL handling)
- Avoids future upgrade fatigue — no need to migrate from 3.11 to 3.13 within 2 years
- All performance improvements from previous releases included at baseline

Cons:
- Some dependencies may not yet declare full 3.13 compatibility (risk manageable via PyPI classifier checking)
- Fewer tutorials and community resources for edge-case issues compared to 3.11
- Will also reach EOL by October 2029 — but that's still ~5 years longer than starting on 3.11
- The free-threaded (no-GIL) build introduced by PEP 703 is experimental and opt-in in 3.13, not the default interpreter; the standard build still ships with the GIL enabled, and most C-extension packages (NumPy, spaCy, PyTorch) don't yet support the free-threaded variant

### Option 3: Python 3.14

[Python 3.14](https://peps.python.org/pep-0745/) is the current latest stable release. Released October 2025 · **EOL: October 2030**. It was evaluated as a candidate to eventually replace 3.13 as the team's standard version.

Pros:
- Longest remaining support window of the three candidates (security fixes into October 2030)
- Latest interpreter performance optimizations and language features
- Deferred annotation evaluation by default (PEP 749), improved error messages, and further maturity of the free-threaded (no-GIL) build option

Cons:
- Not yet compatible with the spaCy NLP library at this time — this is a key dependency and currently blocks adoption
- Not yet compatible with most CUDA/PyTorch-based workflows — GPU/ML tooling has not caught up with 3.14 wheels
- Ecosystem readiness is generally narrower than 3.13's, mirroring the pattern seen when 3.13 itself was new

## More Information

Reference: https://devguide.python.org/versions/

Python 3.14 was evaluated (see "Python 3.14" option above) but is not adopted at this time: spaCy and most CUDA/PyTorch-based workflows do not yet support it. Revisit this decision once spaCy and major PyTorch/CUDA wheel builds declare 3.14 compatibility, or if a significant share of repositories have critical blockers on 3.13.
