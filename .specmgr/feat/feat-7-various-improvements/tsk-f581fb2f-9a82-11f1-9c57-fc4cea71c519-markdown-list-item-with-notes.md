---
created: '2026-08-17'
id: f581fb2f-9a82-11f1-9c57-fc4cea71c519
status: done
type: tsk
updated: '2026-08-17T23:29:21.797621'
version: 1.0.0
---

# Add MarkdownListItemWithNotes for Continuation Paragraph Capture

<!-- Task list tracking the implementation of MarkdownListItemWithNotes, which adds a declared notes field so continuation paragraphs inside list items appear in model_dump()/JSON output instead of being lost to Pydantic's private-attribute invisibility. -->

- [x] Task 1: Add `MarkdownListItemWithNotes` class to `markdown_list_item.py` with a new `notes: list[MarkdownParagraph] | None = None` field.

    The class must derive from `MarkdownListItem`, declare only this single notes field (represents continuation paragraphs inside a loose-list item, zero or more; the leading paragraph text is already accessible via `.text` on the parent), and delegate `get_extent()`, `from_text()`, and `__str__()` to inherited `MarkdownListItem` (no new extent logic needed because `MarkdownStr.process_list_field()` iterates items by `get_extent()` and the field-distribution loop picks up remaining text). Add a short docstring mirroring `ExtensionItem`'s one noting it adds `notes` for captured continuation paragraphs.

    depends on: none — status: completed

- [x] Task 2: Update `req/models/v1/body.py`'s `Characteristics.items` to use `MarkdownListItemWithNotes`, and add test fixture data.

    Change the field type annotation from `list[MarkdownListItem]` to `list[MarkdownListItemWithNotes]`. The existing `min_length=1` validator is inherited and does not need adjustment. Create a new test fixture `docs/req/test-loose-list-with-continuation.md` containing a `## Characteristics` loose list of 2 list items, where the 1st list item has one continuation paragraph indented 4 spaces (a blank line, then the indented paragraph), and the 2nd item has no continuation paragraph. Verify parse round-trip works by loading this fixture and asserting 2 items in `characteristics.items`, with the first item's `.text == "Reliability"` and `.notes` containing exactly one `MarkdownParagraph`, and the second item's `.notes` is `None`.

    depends on: Task 1 — status: completed

- [x] Task 3: Update `uc/models/v2/use_case.py`'s `ExtensionItem` to derive from `MarkdownListItemWithNotes`.

    Replace the existing `notes: list[MarkdownParagraph] | None = None` field with inheritance from `MarkdownListItemWithNotes` (identical type and semantics). The class becomes simply: `class ExtensionItem(MarkdownListItemWithNotes): """One action taken while handling an extension's alternate flow, with any continuation text that clarifies it."""`. Re-run the existing `tests/uc/models/v2/test_extensions_parsing.py` suite unchanged (they already capture continuation paragraphs via notes) to confirm `.notes` still works correctly through inheritance, and update the class docstring.

    depends on: Task 1 — status: completed

- [x] Task 4: Add `tests/models/md/test_markdown_list_item_with_notes.py`.

    Cover these cases: tight list item without notes (`notes` is None, `model_dump()` omits/null), loose list item with one continuation paragraph (`notes` has one `MarkdownParagraph`, JSON shows it), loose list item with two continuation paragraphs (`notes` has two entries), compact item (no blank line → no notes), and `str(parsed)` round-trips match raw source for all scenarios. Additionally, add a REQ-domain test (in `tests/req/models/v1/test_body.py` or equivalent) confirming that a bare `Characteristics.items` entry with a continuation paragraph correctly serializes `.notes` via `model_dump_json()` (i.e. the continuation text is no longer silently dropped, using the `docs/req/test-loose-list-with-continuation.md` fixture from Task 2).

    depends on: Tasks 1, 2, 3 — status: completed

- [x] Task 5: Run full verify step.

    Execute `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence=60`, and the full `unittest` suite. Additionally run all configured pre-commit hooks (`uv run --frozen pre-commit run --all-files`) and ensure they pass. Ensure no regressions in REQ, UC, TSK domains.

    depends on: Task 4 — status: completed

- [x] Task 6: Update README with completion summary; mark task list done.

    Update `.specmgr/feat/feat-7-various-improvements/README.md` Recent Updates section with a concise completion entry for Task 0.17, mark Feature README's Task 0.17 and this TSK's status from `draft` to `done`.

    depends on: Task 5 — status: completed

## Recent Updates

### 2026-08-17 - Created

Created as the implementation plan for `.specmgr/feat/feat-7-various-improvements/README.md`'s Task 0.17: "Add a `MarkdownListItemWithNotes` class to `markdown_list_item.py` that introduces a notes field for captured continuation paragraphs inside list items."

### 2026-08-17 - Clarified scope with user

Confirmed with user before implementation: (1) Task 2's test fixture `docs/req/test-loose-list-with-continuation.md` is a new file to create, containing a loose list of 2 items where the 1st item has one continuation paragraph indented 4 spaces; (2) Task 4 additionally covers a REQ-domain test verifying `Characteristics.items` correctly serializes `.notes` via `model_dump_json()`; (3) Task 3 explicitly re-runs (not just assumes-passes) the existing `tests/uc/models/v2/test_extensions_parsing.py` suite; (4) Task 5 additionally runs all configured pre-commit hooks before considering the task done.
