# Contributing to biz.dfch.SpecMgr

Thank you for your interest in contributing to **biz.dfch.SpecMgr**!  
This document describes how to propose changes, report bugs, and submit patches.

The project is licensed under the **Affero GNU General Public License v3.0 (AGPLv3)**.  
By contributing, you agree that your contributions will be licensed under the
same license as the project.

To contribute, clone the repository, create a branch, develop your changes and
then create a pull request.

---

## 1. Code of Conduct

Please be respectful and constructive in all interactions.

This project has a `CODE_OF_CONDUCT.md`, you must follow it.

---

## 2. How to Ask Questions and Report Bugs

- **Bug reports**: Open an issue in the GitHub issue tracker:
  - URL: `https://github.com/dfch/biz.dfch.SpecMgr/issues`
  - Include:
    - Steps to reproduce
    - Expected behavior
    - Actual behavior
    - Environment details (OS, Python version, biz-dfch-specmgr version)
    - Relevant logs, stack traces, or screenshots where appropriate

- **Feature requests / ideas**: Also use the issue tracker, marking them as
  feature requests or enhancements.

Before opening a new issue, please **search existing issues** to avoid duplicates.

---

## 3. Development Setup

### 3.1. Prerequisites

- Python **3.11** and Python **3.12** and Python **3.13**
- `git`
- [`uv`](https://docs.astral.sh/uv/)
- Recommended: `unittest`

### 3.2. Clone and install dependencies

```bash
git clone https://github.com/dfch/biz.dfch.SpecMgr.git
cd biz.dfch.SpecMgr

uv sync --all-extras
```

---

## 4. Running Linters and Tests

```bash
uv run --frozen ruff format --check
uv run --frozen ruff check
uv run --frozen pylint $(git ls-files '*.py')
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
```

`ruff` is the enforced linter/formatter; CI runs `pylint` advisory only
(`|| true`), so treat its findings as suggestions, not blockers.

---

## 5. Commit Messages and Pull Requests

- Follow [Conventional Commits](https://www.conventionalcommits.org/) for
  commit messages (e.g. `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`).
- Keep pull requests focused on a single change; unrelated changes should be
  separate PRs.
- Make sure linters and tests pass locally (see section 4) before opening a
  pull request.
- Update `CHANGELOG.md` (`[Unreleased]` section) for any user-facing change.
- Reference the related issue number in the PR description, if one exists.
