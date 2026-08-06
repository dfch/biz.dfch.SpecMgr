---
id: feat-3-md-str-constraints
version: 1.0.0
status: planning
created: 2026-08-06
updated: 2026-08-06
---

# Feature: Implement Markdown string type with content constraints for specmgr

## Plan

### Overview

Create a reusable Markdown string type (`MdStr`) for specmgr models that can contain constrained Markdown content. This type will validate that only allowed Markdown elements are present, preventing structural problems (headings, code blocks, nested lists) while preserving rich text capabilities (bold, emphasis, bullets, paragraphs). 

This feature is the basis for the feature "feat-4-use-cases".

### Requirements

- REQ-001: Define a `MdStr` Pydantic model type with a `value: str` field
- REQ-002: Implement a Markdown content validator that checks for disallowed elements (ATX headings, Setext headings, fenced code blocks, indented code blocks)
- REQ-003: Add per-field constraint decorators to limit allowed Markdown types (e.g., `no_headings=True`, `no_code_blocks=True`, `allow_nested_lists=False`)
- REQ-004: Create validation functions for different constraint combinations (name vs description style)
- REQ-005: Document the `MdStr` type usage patterns with examples
- REQ-006: Add comprehensive test suite covering all constraint scenarios and edge cases

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `MdStr` model accepts any string value but validates structure through constraint decorators
- [ ] ACC-002: Verifies REQ-002 — Validator rejects ATX-style headings (``# Title``, ``## Subtitle``), Setext headings (``Title\n====``), and fenced code blocks (``````python code`````)
- [ ] ACC-003: Verifies REQ-003 — Field-level constraints like `md_str.no_headings=True` successfully prevent invalid content
- [ ] ACC-004: Verifies REQ-004 — Different constraint sets work for distinct use cases (name: `*`/`_`/`**` only; description: `*`/`_`/`**`/paragraphs)
- [ ] ACC-005: Verifies REQ-005 — Documentation shows usage examples and best practices
- [ ] ACC-006: Verifies REQ-006 — Test coverage >= 95% with cases for all allowed/forbidden Markdown types

### Scope

**Included in this feature:**
- `src/biz/dfch/specmgr/md_str/models.py` — Core `MdStr` Pydantic model with constraint decorators
- `src/biz/dfch/specmgr/md_str/validators.py` — Markdown content validation functions and regular expressions
- `src/biz/dfch/specmgr/md_str/docs.py` — Usage documentation and examples
- Tests in `tests/md_str/` — All acceptance criteria test suites

**Explicitly out of scope:**
- Converting `MdStr` values to/from PlantUML format
- Integration with existing UC/ADR models (this is a foundational type for future use)
- Supporting all possible Markdown features (tables, blockquotes, task lists, etc.)
- Runtime Markdown rendering to HTML (validation only, not conversion)

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy)
- Blocks: `feat-4-use-cases` (UC Use Case models refactoring to use `MdStr`)
- External: None

### Design Notes

**Markdown Content Validation Strategy:**

1. **AST-based validation** (preferred): Use `markdown-it` to parse Markdown and check token types
2. **Regex-based validation** (fallback): Pattern matching against common Markdown syntax (simpler, less error-prone)

Decision: Start with **regex-based validation** for simplicity and speed, since we only need to check for a few specific patterns (headings, code blocks). If validation needs to become more sophisticated later (checking nesting, nesting depth, etc.), switch to AST-based.

**Constraint Combinations:**

| Field Type | Allowed Elements | Disallowed | Rationale |
|------------|------------------|------------|-----------|
| `name` | `*`, `_`, `**`, basic text | Headings, code blocks, bullet lists, paragraphs, nested lists | Short title field should be concise and list-free |
| `description` | `*`, `_`, `**`, paragraphs (double newlines), basic text | Headings, code blocks | Can contain sub-bullets and paragraphs but not structural heading markers |

**Validator Patterns:**

- ATX headings: `^(#{1,6}\s+.+)$`
- Setext headings: `^(.+)\n=+$` and `^(.+)\n-+$`
- Fenced code blocks: `^````\s*(?:\w+\s*)?$` and `^````\s*$`
- Nested lists: `^\s*[\*\-]\s+[\*\-]\s+` (indented bullets)

**Error Messages:**

- Clear, actionable error messages that show exactly what's invalid and why
- Example of valid content for the field type

**Integration with Pydantic:**

- Use `model_validator` to validate after field assignment
- Provide clean error messages through `ValidationError` with `loc` path pointing to the field

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the task itself — there is no separate "planned" vs. "executed" list to keep in sync; a task's line *is* its current status. Update it in place as work progresses (edit, don't duplicate).

#### Phase 1: Core Markdown String Type
- [ ] Task 1.1: Define `MdStr` Pydantic model with field and validator infrastructure — depends on: none — status: not-started
- [ ] Task 1.2: Implement regex-based Markdown content validators (no_headings, no_code_blocks) — depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: Add field-level constraint decorators for common patterns (name vs description) — depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: Write comprehensive documentation with usage examples — depends on: Task 1.3 — status: not-started

#### Phase 2: Testing and Validation
- [ ] Task 2.1: Create test suite for basic `MdStr` functionality — depends on: Task 1.1 — status: not-started
- [ ] Task 2.2: Add tests for all constraint combinations (no_headings, no_code_blocks, etc.) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: Test edge cases (empty string, whitespace, all-allowed/all-forbidden content) — depends on: Task 2.2 — status: not-started
- [ ] Task 2.4: Run full test suite and ensure 95%+ coverage — depends on: Task 2.3 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place; rely on git history (`git log -p` on this file) to recover what was originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-06**: Feature planning complete. No work started.

(Note: Once Phase 1 or Phase 2 begins, update this section with brief status summaries.)

### Blockers

- [ ] None identified at this time.

(Remove this section if no blockers.)

### Recent Updates

If this section grows too long, move older entries to `history.md` in this same folder and leave a pointer here, e.g.:
`See history.md for updates before YYYY-MM-DD.`

### Decisions Made

- **[2026-08-06]**: Use regex-based validation instead of AST-based for simplicity and performance — we only need to check for a few specific patterns (headings, code blocks), and regex is well-tested and fast. If future validation needs become more sophisticated, we can switch to markdown-it-based AST validation.

### Related PRs / Commits

- [Issue #3](https://github.com/dfch/biz.dfch.SpecMgr/issues/3): Feature request: Implement Markdown string type with content constraints for specmgr
- [PR #NNN](link): [description]
- [Commit hash](link): [description]

## Technical Debt

(No technical debt identified yet for this feature.)