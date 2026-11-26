---
status: accepted
date: '2026-08-05'
id: cb5a2d5f-7020-4c6e-b28d-a38d17b23243
version: 1.0.0
---

# Use Conventional Commits for commit messages

## Context and Problem Statement

Commit messages across repositories are currently free-form, with no enforced structure. This makes it hard for tools and AI coding agents to reliably parse commit history (e.g. to determine change type, generate changelogs, or drive automated version bumps), and makes it harder for humans to scan history for the nature and scope of a change. A decision is needed on whether to adopt a standardized commit message format.

## Considered Options

1. Conventional Commits
2. Free-form commit messages (no standard)

## Decision Outcome

We decide to use the Conventional Commits specification for all commit messages, regardless of programming language or repository.

## Pros and Cons of the Options

### Option 1: Conventional Commits

#### Pros

- Tool and agent support: commit messages can be reliably parsed by tooling (e.g. changelog generators, semantic-release, AI coding agents) because the format is machine-readable.
- Enables automated, consistent changelog generation from commit history.
- Enables automated semantic version bumps derived from commit types (e.g. `fix`, `feat`, breaking-change markers).
- Communicates the intent and scope of a change clearly and consistently to human reviewers.
- Encourages more atomic, single-purpose commits, since each commit must be classifiable by a single type.

#### Cons

- Requires contributors to learn and consistently apply the specification, adding friction, especially for infrequent contributors.
- Requires enforcement (e.g. via a commit-msg hook or CI check) to prevent non-conforming messages from being merged.
- Rigid prefixes can be a poor fit for commits that do not cleanly map to a single type or scope.

### Option 2: Free-form commit messages

#### Pros

- No learning curve or format constraints; contributors write commit messages however they prefer.
- No tooling or enforcement needed.

#### Cons

- Commit history cannot be reliably parsed by tooling or AI agents, blocking automated changelog generation and version bumping.
- Inconsistent style across commits and contributors makes history harder to scan.
- Change type and scope must be inferred manually, which is error-prone and time-consuming.

## More Information

https://www.conventionalcommits.org/
