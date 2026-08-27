You are implementing the checklist of an existing Task List (TSK)
document, id: $id

Follow this sequence exactly.

## 1. Read the current document
Call `get_tsk(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. Build a TodoWrite list from its items
Create one TodoWrite entry per checklist item in `body.items`, in the
same order:
- An item whose `checked` is already `true` -> mark its TodoWrite entry
  `completed`.
- An item whose `checked` is `false` -> mark its TodoWrite entry
  `pending` (moving it to `in_progress` only once you actually start
  working on it -- keep at most one `in_progress` at a time, per
  TodoWrite's own usage conventions).
Use each item's `description` as the TodoWrite entry's own content.

## 3. Resolve ambiguity before starting an item
Before marking any pending item `in_progress`, check whether its
`description` is clear enough to act on. If its intent or scope is
ambiguous or underspecified, use the `question` tool to ask the user
for clarification first -- do not guess and start working on an
unclear item.

## 4. Work the list
Proceed item by item, updating your TodoWrite list's statuses as you
go (one `in_progress` at a time, then `completed` once genuinely done).

## 5. Persisting completed work back to the document (separate, deliberate step)
Completing TodoWrite entries in-session does **not** update the
underlying `tsk` document -- its checkboxes on disk are left exactly as
they were read in step 1. So, for each entry, you must persist the document
to reflect the work you completed, you must separately call
`update(id, type="tsk", content)` with the updated checklist (`- [x] ...`
for items you completed) -- a whole-body replace, so carry forward every
other section unchanged, including at least one `## Recent Updates`
entry (add a new one summarizing the work, or keep the existing ones --
never end up with zero). This is a distinct, deliberate step: do not
assume finishing the TodoWrite list alone is enough.

Optionally, check `specmgr://tsk/schema` if you need to double-check
the document's structure before drafting the replacement body.
