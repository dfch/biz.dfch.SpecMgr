---
created: '2026-08-18 09:29:03.936Z'
id: 602740af-0445-48d8-bcc3-18df541dad72
status: draft
type: tsk
updated: '2026-08-18 09:29:03.936Z'
version: 1.0.0
---

# Fix MarkdownListItem.get_extent for Numbered Lists

<!-- Implementation plan for feat-7-various-improvements Task 0.18: fix `MarkdownListItem.get_extent` to correctly handle continuation paragraphs in loose numbered lists (e.g. `1.`, `2.`). Currently, `mdformat` renders loose numbered lists differently from bullet lists: the `list_item_open` token's `.map` only spans the first paragraph, leaving continuation paragraphs as separate tokens outside the list item. This breaks `get_extent` for numbered lists with continuation paragraphs (e.g. REQ's `Characteristics` section). -->

- [ ] Task 1: Fix `MarkdownListItem.get_extent` in `src/biz/dfch/specmgr/models/md/markdown_list_item.py` to handle numbered list continuation paragraphs

    Analyze token structure difference: for bullet lists, `list_item_open.map[1]` spans entire item including continuation paragraphs; for numbered lists, it only covers the first paragraph. The fix must detect `ordered_list_open` and scan for trailing `paragraph_open` tokens after `list_item_close` but before the next `list_item_open` or list close, extending the extent accordingly. Mirror existing bullet list behavior.

- [ ] Task 2: Add numbered list test cases to `tests/models/md/test_markdown_list_item_with_notes.py`

    Add test methods covering: tight numbered item (no notes), loose numbered item with one continuation paragraph, loose numbered item with two continuation paragraphs, round-trip for all cases. Ensure existing bullet list tests still pass.

- [ ] Task 3: Verify REQ domain integration works with numbered lists containing continuation paragraphs

    Run `tests/req/tools/test_get_req.py::TestGetReq::test_returns_matching_document` with its original `_MINIMAL_BODY` (which uses a numbered list with a continuation paragraph). Should pass after the fix. Also verify `Characteristics.from_text` works with numbered list continuation paragraphs.

- [ ] Task 4: Run full verification

    Execute `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite. Run pre-commit hooks (`uv run --frozen pre-commit run --all-files`). Ensure no regressions in REQ, UC, TSK domains.

- [ ] Task 5: Update feature README and mark task list done

    Update `.specmgr/feat/feat-7-various-improvements/README.md` Task 0.18 status to completed, add entry to Recent Updates. Mark this TSK status as `done`.

## Recent Updates

### 2026-08-18 - Created

Created as the implementation plan for `.specmgr/feat/feat-7-various-improvements/README.md`'s Task 0.18: "Fix `MarkdownListItem.get_extent` for numbered lists".
