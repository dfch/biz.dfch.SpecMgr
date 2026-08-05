---
status: accepted
date: '2026-08-05'
id: 737858a9-7796-4f01-ae35-5afc1c707818
version: 1.0.0
---

# Use pre-commit hooks for local quality gates

## Context and Problem Statement

Repositories in this organization use a variety of programming languages and toolchains. Before code is committed, it must be built, unit tested, linted, and formatted (where applicable), ideally using the same actions that are executed in CI on the repository server. A decision is needed on whether these checks are enforced locally, before a commit is created, or only remotely once the change reaches CI.

## Considered Options

1. Pre-commit hooks (local enforcement)
2. Without pre-commit hooks (CI-only enforcement)

## Decision Outcome

We decide to use pre-commit hooks, regardless of the programming language used in a given repository. The hooks must run build, unit tests, linters, and formatters where applicable, ideally the same actions that are run in CI on the repository server. For Python repositories, the "pre-commit" framework is used to implement and manage these hooks.

## Pros and Cons of the Options

### Option 1: Pre-commit hooks

#### Pros

- Build/test/lint/format errors are caught locally, before a commit is created, shortening the feedback loop.
- The same checks run locally and in CI (where feasible), reducing surprises at CI time.
- Applies uniformly across repositories regardless of programming language.

#### Cons

- Uses local developer machine resources (CPU, time) on every commit.
- Requires initial setup and ongoing maintenance to stay in sync with CI.

### Option 2: Without pre-commit hooks (CI-only)

#### Pros

- Does not use local developer machine resources.

#### Cons

- Build/test/lint/format errors are caught only in CI, lengthening the feedback loop.
- Developers may push multiple broken commits before noticing failures.

## More Information

https://github.com/pre-commit/pre-commit
