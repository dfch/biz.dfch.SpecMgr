---
created: '2026-08-16T20:05:16.970313'
id: 266eb332-795b-48c4-9bc0-7115eb209378
status: done
type: tsk
updated: '2026-08-16T20:17:16.186713'
version: 1.0.0
---

# Improve get_adr/get_req/get_uc/get_tsk Not-Found Error Messages

<!-- Tracks feat-7-various-improvements Task 0.13: make the not-found error message raised by get_adr/get_req/get_uc/get_tsk easier to understand. Agents frequently pass a prefixed id (e.g. "req-uuid") instead of the bare uuid expected by find_adr_path/find_req_path/find_uc_path/find_tsk_path in each domain's tools/_paths.py. This list mirrors feat-7's Task 0.13.1 through 0.13.9. -->

- [x] Task 1: Decide and record one standardized error-message wording/template to apply identically across all four `*NotFoundError` classes (`AdrNotFoundError`, `ReqNotFoundError`, `UcNotFoundError`, `TskNotFoundError`) plus the shared `DocNotFoundError` (`general/tools/_doc_paths.py`), explicitly telling the caller the id must be the bare document uuid with no domain prefix
- [x] Task 2: Update `adr/tools/_paths.py`'s `AdrNotFoundError` message to the standardized wording
- [x] Task 3: Update `req/tools/_paths.py`'s `ReqNotFoundError` message to the standardized wording
- [x] Task 4: Update `uc/tools/_paths.py`'s `UcNotFoundError` message to the standardized wording
- [x] Task 5: Update `tsk/tools/_paths.py`'s `TskNotFoundError` message, replacing its existing first-pass hint ("Make sure, that you only use the 'id' without a prefix.") with the standardized wording, fixing its grammar/punctuation along the way
- [x] Task 6: Update `general/tools/_doc_paths.py`'s shared `DocNotFoundError` message to the same standardized wording, for consistency, even though it is currently always caught and re-raised as a domain-specific error by `req`/`uc`/`tsk` before reaching a caller
- [x] Task 7: Add/extend tests asserting on the new message content (not just the exception type) in `tests/adr/tools/test_paths.py`, `tests/req/tools/test__paths.py`, `tests/uc/tools/test__paths.py`, `tests/tsk/tools/test__paths.py`, `tests/general/tools/test__doc_paths.py`, and each domain's `tests/<domain>/tools/test_get_<type>.py`
- [x] Task 8: Update `feat-7-various-improvements/README.md`'s Decisions Made / Recent Updates logs and mark Task 0.13 (and its sub-list) done
- [x] Task 9: Verify — `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite

## Recent Updates

### 2026-08-16 - Created

Created to track feat-7-various-improvements Task 0.13 (make get_adr/get_req/get_uc/get_tsk not-found error messages easier to understand) as a standalone, referenced task list.

### 2026-08-16 - Implemented and verified

Completed all 9 tasks. Decided and recorded a single standardized wording
template (`"no {noun} found with id {id_!r}. The id must be the bare
document UUID, without a domain prefix (use '<uuid>', not
'{prefix}-<uuid>')."`) and applied it identically to `AdrNotFoundError`
(`adr/tools/_paths.py`), `ReqNotFoundError` (`req/tools/_paths.py`),
`UcNotFoundError` (`uc/tools/_paths.py`), and `TskNotFoundError`
(`tsk/tools/_paths.py`, replacing its earlier rough first-pass hint), plus
the shared `DocNotFoundError` (`general/tools/_doc_paths.py`, without the
prefix example since it has no domain context). Extended
`tests/adr/tools/test_paths.py`, `tests/req/tools/test__paths.py`,
`tests/uc/tools/test__paths.py`, `tests/tsk/tools/test__paths.py`,
`tests/general/tools/test__doc_paths.py`, and each domain's
`tests/<domain>/tools/test_get_<type>.py` to assert on the new message
content, not just the exception type. Recorded the decision and marked
Task 0.13 done in `feat-7-various-improvements/README.md`'s Decisions Made
and Recent Updates logs. Verified: `ruff format --check`/`ruff check`
(clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the
full `unittest` suite (980 tests, all passing).
