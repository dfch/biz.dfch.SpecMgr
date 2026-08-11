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

- REQ-001: Define a `MdStr` Pydantic `NewPassword` type with a `value: str` field and constraint parameters. See API Contract §1 for the full class/function specification.
- REQ-002: Implement regex-based Markdown content validators that reject disallowed elements (ATX headings, Setext headings, fenced code blocks, indented code blocks). The core validation function is `validate_md_content(value: str, constraints: MdStrConstraints) -> None`. See API Contract §2.
- REQ-003: Add per-field constraint configuration via `MdStrConstraints` class with boolean flags (`no_headings`, `no_code_blocks`, `no_nested_lists`, `single_line`, `allow_paragraphs`). See API Contract §3 and Rule Matrix below.
- REQ-004: Provide pre-built validator functions for common use cases (`is_valid_name`, `is_valid_description`) using sensible defaults for `MdStrConstraints`. See API Contract §4.
- REQ-005: Raise custom validation exception `MdStrValidationError` with field location, violated constraint name, and actionable guidance (list of what is allowed for that constraint type).
- REQ-006: Document the `MdStr` type and validators in module docstrings and this README's Design Notes section. Include doctest-compatible examples.
- REQ-007: Add comprehensive test suite with >= 95% coverage covering all constraints, edge cases, and error message formatting.

#### Class Design

* Class `MdStr` has ctor with text: str
* Class `MdStr` generates md, so that: `text == MdStr(text).to_string()`
 
### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — A class `MdStr` (or alias) exists in `src/biz/dfch/specmgr/md_str/`. Instantiation with a plain string (`MdStr("Hello **world**")`) succeeds. No fields are required beyond `value`.

- [ ] ACC-002: Verifies REQ-002 — The following invalid inputs raise `MdStrValidationError` on a field decorated with the corresponding constraint flag set to `True`:
  - ATX heading: `"# Title"` → `MdStrConstraints(no_headings=True)` rejects
  - Setext heading h1: `"Title\n====\n"` → rejected
  - Setext heading h2: `"Subtitle\n----\n"` → rejected
  - Fenced code block (language): ```"```python\nprint(1)\n```\n"` → `MdStrConstraints(no_code_blocks=True)` rejects
  - Fenced code block (no language): ```"\n```\nprint(1)\n```\n"` → rejected
  - Indented code block: `"    code line"` → `MdStrConstraints(no_code_blocks=True)` rejects

- [ ] ACC-003: Verifies REQ-002 + REQ-003 — Field-level constraints work independently. A single instance of `MdStr` can be validated with different constraint sets in sequence (no mutation of the value). Example:

  ```
  >>> md = MdStr("# Title\n\nSome text")
  >>> # Should raise MdStrValidationError when no_headings is True, pass when False
  ```

- [ ] ACC-004: Verifies REQ-004 — Pre-built validators work as expected:
  - `is_valid_name("My **Element**")` → `True` (allows inline emphasis only)
  - `is_valid_name("# Heading\nName")` → `False` (rejects heading and newline)
  - `is_valid_description("A *longer*\\ndescription with **bold**.")` → `True`
  - `is_valid_description("# Not Valid")` → `False`

- [ ] ACC-005: Verifies REQ-001 + REQ-005 — `MdStrValidationError` contains all three of: `field_name` (str), `constraint_violated` (str, one of the constraint flag names), and `allowed_suggestion` (str listing what the field does allow). Error messages do not expose internal regex patterns.

- [ ] ACC-006: Verifies REQ-003 — Rule Matrix compliance: every cell in the matrix below is covered by at least one passing test case. Tests verify both positive (accepted input → no error) and negative (rejected input → exception raised) paths for each of the 8 Markdown element types × 4 constraint scenarios = 32 combinations, plus edge cases. See Test Scenario Matrix §7.

- [ ] ACC-007: Verifies REQ-007 — Test coverage >= 95% measured by `pytest-cov` or equivalent on `tests/md_str/`. Coverage report includes line coverage per `.py` file in the `md_str` package.

### Rule Matrix (detailed Markdown element rules)

The following matrix defines which Markdown elements are allowed/disallowed under each constraint configuration. These rules govern both `validate_md_content()` and the pre-built validators.

| # | Markdown Element | Syntax Pattern | `no_headings=True` | `no_code_blocks=True` | `no_nested_lists=True` | `single_line=True` | `allow_paragraphs=True` | Notes for False Positives |
|---|------------------|----------------|--------------------|-----------------------|------------------------|--------------------|-------------------------|---------------------------|
| 1 | ATX heading | `#{1,6}\s+.+` at line start | **Reject** | Accept | Accept | Reject (if has newline) | Accept | Line starting with `#x` where x is not a space should not match. E.g., `"mix #hash"` in plain text is OK unless it begins with heading syntax. |
| 2 | Setext heading h1 | `.+` followed by `\n=+` on next line | **Reject** | Accept | Accept | Reject | Accept | A single line of `=====` alone should not match; requires preceding content line. |
| 3 | Setext heading h2 | `.+` followed by `\n-+` on next line | **Reject** | Accept | Accept | Reject | Accept | Dashes in a separator must be all-consecutive (`----`), not interspersed. "Item\n----" should match; "no---dashed" on one line should not. |
| 4 | Fenced code block (lang) | ```^```\w+` followed by closing ```` ``` | Accept | **Reject** | Accept | Reject (multi-line) | Accept | The fence must be on its own line with optional language identifier. Inline backticks like `` `code` `` are NOT fenced blocks and should pass both constraints. |
| 5 | Fenced code block (no lang) | ```^``` + newline` followed by closing ```` ``` | Accept | **Reject** | Accept | Reject (multi-line) | Accept | Same as above — only multi-line fence triggers rejection. |
| 6 | Indented code block | First column has 4+ spaces on a content line | Accept | **Reject** | Accept | Accept | Accept | A single indented line alone is rejected; this is the raw Markdown spec's definition of an indented code block (4-space or tab indent). Do NOT reject lines inside list bullet content where indentation is part of the list structure. |
| 7 | Nested list | Indented `-` or `*` after a parent list item | Accept | Accept | **Reject** | Accept | Accept | A top-level bullet list (`- item`) should PASS `no_nested_lists=True`. Only child items (indented under parent) trigger rejection. Pattern: `\s{1,3}[-*]\s+` following a non-indented `[-*]` line. |
| 8 | Multi-line / paragraph | Content spans multiple lines (newline not inside inline formatting) | Accept | Accept | Accept per REQ definition | **Reject** on any `\n` in value | **Accept** and encouraged | `single_line=True` rejects any string containing a newline character (unless used only within an allowed inline element — but for simplicity, reject on `\n`). `single_line=False + allow_paragraphs=True` accepts multiple paragraphs separated by blank lines. |

### Constraint Flag Reference

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `no_headings` | `bool` | `False` | Reject ATX and Setext heading syntax |
| `no_code_blocks` | `bool` | `True` | Reject fenced and indented code blocks. Enabled by default because code blocks are rarely wanted in field values |
| `no_nested_lists` | `bool` | `True` | Reject bullet list child items. Top-level lists may still be present unless another constraint prevents them |
| `single_line` | `bool` | `False` | Reject any string containing a `\n` character |
| `allow_paragraphs` | `bool` | `False` | When combined with `no_code_blocks=True`, allow blank-line-separated paragraphs. Only takes effect when `single_line=False` |

### Pre-built Validator Defaults

| Validator Function | `no_headings` | `no_code_blocks` | `no_nested_lists` | `single_line` | `allow_paragraphs` | Intended Use |
|--------------------|---------------|------------------|--------------------|---------------|--------------------|--------------|
| `is_valid_name(value)` | `True` | `True` | `True` | `False` | `False` | Short field labels (one or two lines, bold/italic inline only) |
| `is_valid_description(value)` | `True` | `True` | `True` | `False` | `True` | Multi-line descriptions with paragraphs and top-level bullets |

### Scope

**Source file locations:**

- `src/biz/dfch/specmgr/md_str/__init__.py` — Package init; exports public API symbols
- `src/biz/dfch/specmgr/md_str/constraints.py` — Defines `MdStrConstraints` dataclass with all boolean flags and `__post_init__` validation (at least one flag must be `True`)
- `src/biz/dfch/specmgr/md_str/validators.py` — Contains the regex patterns as module-level constants (`RE_ATX_HEADING`, etc.) and the core function `validate_md_content(value: str, constraints: MdStrConstraints) -> None`. Also exports pre-built helpers `is_valid_name()` and `is_valid_description()`.
- `src/biz/dfch/specmgr/md_str/exceptions.py` — Defines custom `MdStrValidationError` exception class with fields: `field_name: str`, `constraint_violated: str`, `value_sample: str` (truncated to 200 chars), `allowed_suggestion: str`
- Tests in `tests/md_str/` — One test module per source file (`test_constraints.py`, `test_validators.py`, `test_exceptions.py`) plus an integration test file if needed

**Explicitly out of scope:**
- Converting `MdStr` values to/from PlantUML format
- Integration with existing UC/ADR models (this is a foundational type for future use)
- Supporting all possible Markdown features (tables, blockquotes, task lists, etc.)
- Runtime Markdown rendering to HTML (validation only, not conversion)
- AST-based parsing libraries (markdown-it, mistune, etc.) — regex is the sole approach

**API Contract:**

#### §1 Core Model Type

```python
class MdStr(constraints: MdStrConstraints | None = None) -> str:
    """Markdown string type for specmgr model fields.

    Wraps a plain ``str`` value and validates it against the provided
    :class:`MdStrConstraints`. When instantiated as a Pydantic field via
    the ``MdStr.Field()`` descriptor, validation runs automatically on
    assignment.

    Parameters (Pydantic Field kwargs):
        value: The Markdown content string.
        constraints: Per-field constraint configuration. If None, uses
            default constraints (equivalent to all-False except
            ``no_code_blocks=True``).

    Raises:
        MdStrValidationError: If the value violates any constraint in
            the active configuration.
    """

    # Usage as a direct type alias
    def __init__(self, value: str) -> None: ...

    # Usage as Pydantic Field descriptor (preferred for model fields)
    class Field:
        """Descriptor to use inside Pydantic models."""
        def __init__(
            self,
            constraints: MdStrConstraints | None = None,
            max_length: int | None = None,
        ) -> None: ...
```

#### §2 Core Validation Function

```python
MdStrValidationError: type[Exception]  # Custom exception, defined in exceptions.py

# Module-level regex constants (not intended as public API but must be importable)
RE_ATX_HEADING: Pattern[str]  # e.g., r"^(#{1,6})\s+"
RE_SETEXT_HEADING_H1: Pattern[str]  # e.g., r"^([^\n]+)\n=+\s*$"
RE_SETEXT_HEADING_H2: Pattern[str]  # e.g., r"^([^\n]+)\n-{2,}\s*$"
RE_FENCED_CODE_BLOCK_START: Pattern[str]  # e.g., r"^```(\w*)\s*$"
RE_FENCED_CODE_BLOCK_END: Pattern[str]  # e.g., r"^```\s*$"
RE_INDENTED_CODE_LINE: Pattern[str]  # e.g., r"^(    |\t)"


def validate_md_content(value: str, constraints: MdStrConstraints) -> None:
    """Validate a Markdown string against the given constraints.

    Raises ``MdStrValidationError`` on any violation. The exception's
    ``constraint_violated`` field contains the name of the flag that
    was violated (e.g. ``"no_headings"``), and ``allowed_suggestion``
    contains a human-readable description of what IS allowed for this
    field type.

    Parameters:
        value: The raw Markdown string to validate.
        constraints: Active constraint configuration.

    Raises:
        MdStrValidationError: On constraint violation.
    """
```

#### §3 Constraint Configuration Class

```python
@dataclass(frozen=True, slots=True)
class MdStrConstraints:
    """Configuration of which Markdown elements are allowed or rejected.

    At least one flag must be ``True``; an all-False configuration is
    considered a programming error and raises ``ValueError`` during
    construction (caught only by the test suite).

    Parameters:
        no_headings: Reject ATX-style (``# Title``) and Setext-style
            headings. Defaults to ``False``.
        no_code_blocks: Reject fenced code blocks (`` ``` ``) and
            indented code blocks (4-space or tab prefix). Defaults to
            ``True`` because code blocks are almost never wanted in
            field values.
        no_nested_lists: Reject bullet list child items (indented
            underneath a top-level ``-`` or ``*`` item). Top-level
            bullets themselves may still appear. Defaults to ``True``.
        single_line: Reject any string containing a newline character
            (``\\n``). When combined with ``allow_paragraphs=False``,
            the value remains strictly one line. Defaults to ``False``.
        allow_paragraphs: When ``single_line=False``, allow multiple
            paragraphs separated by blank lines. Requires that
            ``no_code_blocks=True`` (enforced in ``__post_init__``).
            If both are ``True`` and ``single_line=True``, then
            ``allow_paragraphs`` is ignored. Defaults to ``False``.
    """
```

#### §4 Pre-built Validators

```python
def is_valid_name(value: str) -> bool:
    """Validate a name field using name-style constraints.

    Name fields should be concise (single or two lines maximum), allow
    inline formatting only (bold ``**``, italic ``*``, emphasis via
    underscores ``_``), and reject headings, code blocks, nested lists,
    and multi-paragraph content.

    Parameters:
        value: The Markdown string to validate.

    Returns:
        ``True`` if the value passes all name constraints; ``False``
        otherwise (validation errors are consumed internally).
    """
    constraints: MdStrConstraints = MdStrConstraints(
        no_headings=True,
        no_code_blocks=True,
        no_nested_lists=True,
        single_line=False,
        allow_paragraphs=False,
    )
    try:
        validate_md_content(value, constraints)
        result: bool = True
    except MdStrValidationError:
        result = False
    return result


def is_valid_description(value: str) -> bool:
    """Validate a description field using description-style constraints.

    Description fields may contain multiple paragraphs and top-level
    bullet lists, but must still reject headings, code blocks, and
    nested lists to keep the content well-structured for downstream
    rendering.

    Parameters:
        value: The Markdown string to validate.

    Returns:
        ``True`` if the value passes all description constraints;
        ``False`` otherwise.
    """
    constraints: MdStrConstraints = MdStrConstraints(
        no_headings=True,
        no_code_blocks=True,
        no_nested_lists=True,
        single_line=False,
        allow_paragraphs=True,
    )
    try:
        validate_md_content(value, constraints)
        result: bool = True
    except MdStrValidationError:
        result = False
    return result
```

#### §5 Error Exception Class

```python
class MdStrValidationError(ValueError):
    """Exception raised when a Markdown string violates constraint rules.

    Subclasses ``ValueError`` so it can be caught alongside general Pydantic
    validation errors. The exception carries structured fields for both
    programmatic inspection and human-readable error messages.

    Attributes:
        field_name: The name of the model field that failed validation
            (e.g., ``"title"``, ``"description"``).
        constraint_violated: The name of the specific flag that was
            triggered (one of the ``MdStrConstraints`` attributes, e.g.
            ``"no_headings"``).
        value_sample: A truncated sample (< 200 chars) of the offending
            content for inclusion in log messages or user-facing errors.
        allowed_suggestion: A human-readable description of what IS
            allowed for this field type (e.g., ``"This field allows
            bold and italic text only, no headings or code blocks."``).
    """
```

#### §6 Module Structure Summary

```
src/biz/dfch/specmgr/md_str/
├── __init__.py          # Public exports: MdStr, MdStrConstraints, validate_md_content,
│                         #   is_valid_name, is_valid_description, MdStrValidationError,
│                         #   RE_* constants
├── constraints.py       # MdStrConstraints dataclass
├── validators.py        # RE_* constants, validate_md_content(), pre-built validators
└── exceptions.py        # MdStrValidationError class
```

#### §7 Test Scenario Matrix

Each row in the rule matrix (§ above) is tested with one passing case per constraint configuration that allows it, and one failing case per constraint configuration that rejects it. This guarantees full coverage of all 32 element × constraint combinations. Additional scenarios cover:

| # | Scenario | Expected Result |
|---|----------|-----------------|
| t1 | Empty string `""` with ``MdStrConstraints(no_headings=True)`` | Pass |
| t2 | Whitespace only `"   "` with ``MdStrConstraints(no_headings=True)`` | Pass |
| t3 | Single ATX heading `"# Title"` with ``no_headings=True`` | Fail (heading rejected) |
| t4 | Single ATX heading `"# Title"` with ``no_headings=False`` | Pass |
| t5 | Two levels of setext h1: `"Title\n====="` with ``no_headings=True`` | Fail |
| t6 | Setext h2: `"Subtitle\n-----"` with ``no_headings=True`` | Fail |
| t7 | Fenced code block with language: ```"```python\ncode\n```\n"` with ``no_code_blocks=True`` | Fail |
| t8 | Inline backtick: `` "see `func()` for details" `` with ``no_code_blocks=True`` | Pass (not a fenced block) |
| t9 | 4-space indented line: `"    code here"` with ``no_code_blocks=True`` | Fail |
| t10 | 4-space content in non-code context: `"text\n    more text"` with ``no_code_blocks=True`` | Fail (indented line present) |
| t11 | Top-level bullet list: `"- item1\n- item2"` with ``no_nested_lists=True`` | Pass (top-level only, no nesting) |
| t12 | Nested bullet: ```"- parent\n  - child"` with ``no_nested_lists=True`` | Fail |
| t13 | Nested list: ```"- parent\n  - child"` with ``no_nested_lists=False`` | Pass |
| t14 | Single line `"Hello"` with ``single_line=True`` | Pass |
| t15 | Multi-line `"Hello\nWorld"` with ``single_line=True`` | Fail |
| t16 | Multi-paragraph: `"Para 1.\n\nPara 2."` with ``allow_paragraphs=True``, ``single_line=False`` | Pass |
| t17 | No blank-line separation: `"Paragraph1\nParagraph2"` with ``allow_paragraphs=True`` | Pass (still one paragraph by this definition) |
| t18 | Bold inline: `"**bold text**"` with any constraints | Pass |
| t19 | Italic inline: `"_italic_"` with any constraints | Pass |
| t20 | Mixed formatting: `"The **bold _and_ italic** text"` with ``no_headings=True`` | Pass |
| t21 | Heading-like inline but not a heading: `"Item #42"` (not starting line with `#`) with ``no_headings=True`` | Pass (should NOT be falsely rejected) |
| t22 | Fenced fence only on one end (unclosed): ```"```python\ncode"` (no closing fence) — currently treated as start-only with incomplete block | Reject if partial match is found (first line looks like a fence opening); alternatively pass and leave to user. Decision: reject for safety. Needs test expectation confirmation in code comments. |
| t23 | Max length exceeded via ``MdStr.Field(max_length=50)`` assigned `"x" * 100` | Fail on max_length, not on any Markdown constraint |
| t24 | Constraint with all-False (programmer error): ``MdStrConstraints(False, False, False, False, False)`` | Raise ``ValueError`` at construction time |

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy)
- Blocks: `feat-4-use-cases` (UC Use Case models refactoring to use `MdStr`)
- External: None

### Design Notes

**Markdown Content Validation Strategy:**

1. **AST-based validation** (alternative): Use `markdown-it` to parse Markdown and check token types. Would handle edge cases more accurately but adds a non-standard library dependency.
2. **Regex-based validation** (chosen approach): Pattern matching against common Markdown syntax. Simpler, no extra dependencies, sufficient for the small set of patterns we need to detect.

**Decision:** Start with **regex-based validation** because:
- We only need to check for a narrow set of patterns (headings and code blocks)
- No additional runtime dependency beyond Pydantic
- Regex is predictable and fast for the short strings expected in field values
- Regex can be unit-tested independently with edge case inputs

If future validator needs become more sophisticated (e.g., checking nesting depth, list indentation correctness, or blockquote presence), evaluate upgrading to an AST-based parser then.

**Regex Pattern Stability:**

All regex patterns must be:
- Anchored at line start (`^`) when the pattern only matches at line boundaries
- Case-insensitive where applicable (e.g., fenced code blocks use `` ``` `` which has no case)
- Testable independently (each RE_* constant should have ≥ 1 passing test and 1 failing test)

**Error Message Format:**

Error messages follow this structure:

```
Validation Error: {field_name}: {constraint_violated} violated.
{allowed_suggestion}
Example of valid content for this field type.
```

Do NOT include raw regex patterns in error messages — they are implementation details. Provide examples instead.

**Integration with Pydantic:**

- Use a custom Pydantic `GetCoreSchemaHandler` to integrate `MdStrConstraints` as a validator within the core schema pipeline (Pydantic v2 style)
- When used as a Field descriptor: `field: MdStr = MdStr.Field(constraints=MdStrConstraints(no_headings=True))` — runs validation during model construction and update
- Provide a standalone `validate_md_content()` function for non-Pydantic use cases (e.g., CLI input, migration scripts where no model is present)

**Module Organization:**

Follow the existing `models/adr/v1/` convention:
- Split into small files (one responsibility per file): constraints, validators, exceptions
- Export everything through `__init__.py` for clean public API surface
- Use module-level regex constants (not compiled inside functions) so they are importable and testable independently

**Testing Approach:**

For each of the 8 Markdown element types × 4 active constraint configurations (per the pre-built validators in Pre-built Validator Defaults), write at least one explicit positive test (value should pass) and one explicit negative test (value should fail). Edge cases listed in Test Scenario Matrix cover additional boundary conditions like unclosed fences, heading-like inline content (`#42`), and empty strings.

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

#### Phase 1: Infrastructure (exceptions + constraints)
- [ ] Task 1.1: Create `src/biz/dfch/specmgr/md_str/exceptions.py` — `MdStrValidationError` class with `field_name`, `constraint_violated`, `value_sample`, `allowed_suggestion` attributes — depends on: none — status: not-started
- [ ] Task 1.2: Create `src/biz/dfch/specmgr/md_str/constraints.py` — `MdStrConstraints` frozen dataclass with all 5 flags, ``__post_init__`` enforcing at-least-one-True and allow_paragraphs → no_code_blocks dependency — depends on: none — status: not-started
- [ ] Task 1.3: Write tests for constraints module (``test_constraints.py``) — test __post_init__ validation, attribute access via frozen dataclass semantics, repr(), and at-least-one-True enforcement (t24) — depends on: Task 1.2 — status: not-started

#### Phase 2: Validators + regex patterns
- [ ] Task 2.1: Create `src/biz/dfch/specmgr/md_str/validators.py` with module-level RE_* constants — unit-test each pattern independently against passing and failing examples from Rule Matrix rows 1–8 — depends on: none — status: not-started
- [ ] Task 2.2: Implement `validate_md_content(value, constraints)` core function in validators.py — apply only the regex patterns corresponding to constraint flags set to True; raise MdStrValidationError with structured fields on first violation — depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: Implement pre-built validators `is_valid_name()` and `is_valid_description()` with sensible defaults — depends on: Task 2.2 — status: not-started
- [ ] Task 2.4: Write tests for validators module (``test_validators.py``) — cover all rows in the Test Scenario Matrix (§7); each pattern has ≥1 positive and ≥1 negative test; verify error message format and structured exception fields (ACC-005) — depends on: Task 2.2 — status: not-started

#### Phase 3: Core MdStr model + module organization
- [ ] Task 3.1: Define `MdStr` as a simple wrapper class in its own file or integrated into validators.py — ``__init__(self, value: str, constraints: MdStrConstraints | None = None) -> None`` calling ``validate_md_content(value, self._constraints)``, exposing ``value: str`` property — depends on: Task 2.2 — status: not-started
- [ ] Task 3.2: Implement `MdStr.Field` Pydantic descriptor with optional ``max_length`` parameter — uses ``GetCoreSchemaHandler`` for Pydantic v2 integration — validates during model construction/update — depends on: Task 3.1 — status: not-started
- [ ] Task 3.3: Create `src/biz/dfch/specmgr/md_str/__init__.py` with public exports — all RE_* constants, MdStrConstraints, MdStr, validate_md_content, is_valid_name, is_valid_description, MdStrValidationError — depends on: Task 3.2 — status: not-started
- [ ] Task 3.4: Write integration test for Pydantic model usage (e.g., a small test model class using ``field: MdStr = MdStr.Field(constraints=...)``) — verify that construction with invalid value raises pydantic.ValidationError wrapping MdStrValidationError — depends on: Task 3.2 — status: not-started

#### Phase 4: Test coverage + docs
- [ ] Task 4.1: Run test suite locally and confirm ≥95% line coverage for the md_str package — if below target, identify untested branches and add tests — depends on: Task 3.4 — status: not-started
- [ ] Task 4.2: Verify no dead imports or unused RE_* patterns remain (ruff F401 passes clean) — depends on: Task 3.3 — status: not-started
- [ ] Task 4.3: Update module docstrings (each file in md_str/) with purpose, parameters, and usage examples following conventions.md documentation format — depends on: Task 3.3 — status: not-started

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