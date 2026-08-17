---
created: 2026-08-17
id: 550e8400-e29b-41d4-a716-446655440000
status: draft
type: tsk
updated: 2026-08-17
version: 1.0.0
---

# Add MarkdownListItemWithNotes for Continuation Paragraph Capture

<!-- Task list tracking the implementation of MarkdownListItemWithNotes, which adds a declared notes field so continuation paragraphs inside list items appear in model_dump()/JSON output instead of being lost to Pydantic's private-attribute invisibility. -->

- [ ] Task 1: Add `MarkdownListItemWithNotes` class to `markdown_list_item.py` with a new `notes: list[MarkdownParagraph] | None = None` field.
    
    The class must derive from `MarkdownListItem`, declare only this single notes field (represents continuation paragraphs inside a loose-list item, zero or more; the leading paragraph text is already accessible via `.text` on the parent), and delegate `get_extent()`, `from_text()`, and `__str__()` to inherited `MarkdownListItem` (no new extent logic needed because `MarkdownStr.process_list_field()` iterates items by `get_extent()` and the field-distribution loop picks up remaining text). Add a short docstring mirroring `ExtensionItem`'s one noting it adds `notes` for captured continuation paragraphs.

    depends on: none — status: not-started

- [ ] Task 2: Update `req/models/v1/body.py`'s `Characteristics.items` to use `MarkdownListItemWithNotes`.
    
    Change the field type annotation from `list[MarkdownListItem]` to `list[MarkdownListItemWithNotes]`. The existing `min_length=1` validator is inherited and does not need adjustment. Verify parse round-trip works by loading `docs/req/test-loose-list-with-continuation.md` and asserting 3 items in `characteristics.items`, with the first item's `.text == "Reliability"` and `.notes` containing one `MarkdownParagraph`.

    depends on: Task 1 — status: not-started

- [ ] Task 3: Update `uc/models/v2/use_case.py`'s `ExtensionItem` to derive from `MarkdownListItemWithNotes`.
    
    Replace the existing `notes: list[MarkdownParagraph] | None = None` field with inheritance from `MarkdownListItemWithNotes` (identical type and semantics). The class becomes simply: `class ExtensionItem(MarkdownListItemWithNotes): """One action taken while handling an extension's alternate flow, with any continuation text that clarifies it."""`. Verify existing UC tests pass (they already capture continuation paragraphs via notes), adjust field references where needed to ensure `.notes` still works through inheritance, and update the class docstring.

- [ ] Task 4: Add `tests/models/md/test_markdown_list_item_with_notes.py`.
    
    Cover these cases: tight list item without notes (`notes` is None, `model_dump()` omits/null), loose list item with one continuation paragraph (`notes` has one `MarkdownParagraph`, JSON shows it), loose list item with two continuation paragraphs (`notes` has two entries), compact item (no blank line → no notes), and `str(parsed)` round-trips match raw source for all scenarios.

    depends on: Tasks 1, 2, 3 — status: not-started

- [ ] Task 5: Run full verify step.
    
    Execute `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence=60`, and the full `unittest` suite. Ensure no regressions in REQ, UC, TSK domains.

    depends on: Task 4 — status: not-started

- [ ] Task 6: Update README with completion summary; mark task list done.
    
    Update `.specmgr/feat/feat-7-various-improvements/README.md` Recent Updates section with a concise completion entry for Task 0.17, mark Feature README's Task 0.17 and this TSK's status from `draft` to `done`.

    depends on: Task 5 — status: not-started

## Recent Updates

### 2026-08-17 - Created

Created as the implementation plan for `.specmgr/feat/feat-7-various-improvements/README.md`'s Task 0.17: "Add a `MarkdownListItemWithNotes` class to `markdown_list_item.py` that introduces a notes field for captured continuation paragraphs inside list items."
