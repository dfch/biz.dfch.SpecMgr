---
classification: null
created: '2026-10-05T18:57:34.444+02:00'
id: 1b36c754-2a57-431f-b0c5-98bcfa2dc535
status: draft
type: tsk
updated: '2026-10-06T06:26:05.955+02:00'
version: 1.0.0
---

# Repair FEAT README Documents That Fail to Parse

<!-- Tracks the feat-\* `.specmgr/feat/<ref>/README.md` documents that fail to parse
against the live `feat` schema, as reported by `specmgr_list_feat`/`specmgr_get_feat`.
Replaces the former sibling trackers tsk-2687d267 and tsk-601e6fa2 (both deleted
2026-10-05): those two parallel TSKs tracked the same underlying repair effort under
different task numbers, drifted out of sync with each other, and both missed two
newly-failing docs (feat-177-list-ref-feat, feat-180-updates) discovered in this
inventory. This is now the single source of truth -- reconcile against a fresh
`specmgr_list_feat` call at the start and end of every session instead of trusting
a stale task count. -->

- [x] Task 1: Repair `feat-132-prb-update`. Known error: a blockquote note (`> **Note (Task 6.2, REQ-017, added 2026-09-19):** ...`) is embedded inside `### Updates`, breaking `UpdateEntry` parsing around body line 331. Fix: strip the `> ` markers, join the note into one prose paragraph, and prepend it to the lead paragraph of the first `### Updates` entry it introduces (the first of the five 2026-09-19 entries), every word preserved.
- [x] Task 2: Repair `feat-177-list-ref-feat`. Known error: a bare, unescaped `<fn>` token in prose is parsed as raw inline HTML and rejected at line 125. Fix: wrap it in a code span (e.g. `` `<fn>` ``) or write it as an HTML comment (e.g. `<!-- <fn> -->`) instead.
- [x] Task 3: `feat-180-updates` -- no document defect; closed as server-version artifact. This doc is the plan for feat-180 itself (which added `UpdateEntryContent`: any-markdown `UpdateEntry` bodies). Its HEAD version parses cleanly under this checkout's current schema (verified via the repo's own `parse_feat`). The live MCP server (v0.34.0 PyPI release; feat-180 still `[Unreleased]` in `dev`) runs the pre-feat-180 single-paragraph schema and reports the false failure. A sub-agent's list->paragraph edit was reverted (`git checkout`). Resolves itself when the server restarts from a post-feat-180 checkout (e.g. enabling the local `specmgr-test` `uv run` config) or 0.35.0 ships.
- [x] Task 4: Repair `feat-29-dec-source-roles`. Known error: a `### Known Limitations` H3 sits in `## Plan` where `### Task List` is expected, around body line 102. Fix: fold its content into `### Design Notes` (keep "Known Limitations" as a bold lead-in), every word preserved.
- [ ] Task 5: Repair `feat-5-md-model-parser`. Known error: `### Requirements` begins with free-form reconciliation prose (a `**Note (2026-08-11 reconciliation):**` paragraph) instead of `REQ-NNN: ...` bullets, around body line 26. Fix: move the note verbatim into `### Design Notes`; also relocate the struck-through `- [x] ~~Task 1.5: ...~~` line and the `- **Note (rescoped 2026-08-11):** ...` line out of the Task List into Design Notes.
- [ ] Task 6: Repair `feat-50-confluence`. Known error: a prose paragraph ("A post-completion, real-instance follow-up test ...") sits inside `#### Phase 100` where only checklist items (`- [ ]`/`- [x] Task N.M: ...`) are expected, around body line 162. Fix: move the paragraph verbatim into `### Design Notes` (or `### More Information`).

## Recent Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-05 00:00:00.000Z - Created

Replaces the deleted sibling trackers tsk-2687d267-b1f7-4bf6-96f1-2bbf70e19b84 and
tsk-601e6fa2-71bb-48a9-a4ad-ab167e93cae4, which had drifted out of sync with each
other and with the live server. Re-inventoried via `specmgr_list_feat` against the
live server (72 feat docs total, `error_count: 6`): the six tasks above are the
full, current failure set. Four of them (feat-132-prb-update, feat-29-dec-source-roles,
feat-5-md-model-parser, feat-50-confluence) carry forward known root causes already
diagnosed by the deleted trackers; the other two (feat-177-list-ref-feat,
feat-180-updates) are newly discovered in this inventory and were not tracked
anywhere before. Verification gate: `specmgr_list_feat` `error_count: 0` across all
docs.
