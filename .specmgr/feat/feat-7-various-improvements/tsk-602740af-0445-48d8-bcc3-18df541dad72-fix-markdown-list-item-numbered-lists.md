---
created: '2026-08-18'
id: 602740af-0445-48d8-bcc3-18df541dad72
status: done
type: tsk
updated: '2026-08-18'
version: 1.0.0
---

# Fix MarkdownListItem.get_extent for Numbered Lists

<!-- Implementation plan for feat-7-various-improvements Task 0.18: fix `MarkdownListItem.get_extent` to correctly handle continuation paragraphs in loose numbered lists (e.g. `1.`, `2.`). Currently, `mdformat` renders loose numbered lists differently from bullet lists: the `list_item_open` token's `.map` only spans the first paragraph, leaving continuation paragraphs as separate tokens outside the list item. This breaks `get_extent` for numbered lists with continuation paragraphs (e.g. REQ's `Characteristics` section). -->

- [x] Task 1: Fix `MarkdownListItem.get_extent` in `src/biz/dfch/specmgr/models/md/markdown_list_item.py` to handle numbered list continuation paragraphs

    Analyzed token structure difference: for bullet lists, `list_item_open.map[1]` spans entire item including continuation paragraphs; for numbered lists rendered as single-item ordered lists, it only covers the first paragraph. The fix detects single-item ordered lists (where `ordered_list_open.map[1] == list_item_open.map[1]`) and scans for trailing `paragraph_open` tokens after `ordered_list_close` but before the next `ordered_list_open`, extending the extent accordingly. Mirrors existing bullet list behavior.

- [x] Task 2: Add numbered list test cases to `tests/models/md/test_markdown_list_item_with_notes.py`

    Added test methods covering: tight numbered item (no notes), loose numbered item with one continuation paragraph, loose numbered item with two continuation paragraphs, parsing verification for all cases (round-trip not byte-exact for loose numbered lists due to mdformat stripping indentation, which is documented as an accepted limitation). Ensured existing bullet list tests still pass.

- [x] Task 3: Verify REQ domain integration works with numbered lists containing continuation paragraphs

    Ran `tests/req/tools/test_get_req.py::TestGetReq::test_returns_matching_document` with its original `_MINIMAL_BODY` (which uses a numbered list with a continuation paragraph). Passes after the fix. Also verified `Characteristics.from_text` works with numbered list continuation paragraphs.

- [x] Task 4: Run full verification

    Executed `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite (1013 tests, all passing). Verified no regressions in REQ, UC, TSK domains.

- [x] Task 5: Update feature README and mark task list done

    Updated `.specmgr/feat/feat-7-various-improvements/README.md` Task 0.18 status to completed, added entry to Recent Updates. Marked this TSK status as `done`.

## Recent Updates

### 2026-08-18 - Created

Created as the implementation plan for `.specmgr/feat/feat-7-various-improvements/README.md`'s Task 0.18: "Fix `MarkdownListItem.get_extent` for numbered lists".

### 2026-08-18 - Implementation complete

Completed all 5 tasks. Fixed `MarkdownListItem.get_extent` to correctly handle continuation paragraphs in loose numbered lists by detecting single-item ordered lists and scanning for paragraphs between `ordered_list_close` and the next `ordered_list_open`. Added 6 new test cases for numbered lists (tight, loose with 1-2 continuations, parsing verification). Verified REQ domain integration with `create_req`/`get_req` round-trip. All 1013 tests pass, ruff/vulture clean.
