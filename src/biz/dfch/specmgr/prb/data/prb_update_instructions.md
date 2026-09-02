You are revising an existing Problem Statement (PRB) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_prb(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which of the 7 questions are already answered

Show the user which of the 7 5W2H questions under `## Current State`
already have answers (`### What Is the Problem?`,
`### Why Is It a Problem?`, `### Where Is the Problem Observed?`,
`### Who Is Impacted?`, `### When Was the Problem First Observed?`,
`### How Is the Problem Observed?`,
`### How Often Is the Problem Observed?`) and which are still
empty/absent. Use the `question` tool to ask which ones (if any) they
want to add to or revise.

## 4. Elicit the new/revised answers

For each question selected in step 3, use the `question` tool to elicit
the new or revised text.

## 5. Regenerate the Summary from the complete, current set of answers

Regenerate `### Summary` from the *complete* current set of 5W2H answers
(the ones carried forward unchanged plus whatever was just revised) --
this is a full re-synthesis, not an append of the new text onto the old
`Summary`.

## 6. Re-draft and confirm the Gap

Re-draft `## Gap` the same way as the `create_prb` prompt's own step 4
(an expected-vs-actual/measurable-difference formula), based on the
now-current-state answers. Show this draft to the user and use the
`question` tool to confirm or refine it before finalizing.

## 7. Optionally revise Impact/Future State/References/More Information

Use the `question` tool to ask whether the user wants to revise
`## Impact`, `## Future State`, `## References`, or `## More Information`.
Leave any section the user does not want to change exactly as read in
step 1.

## 8. Map the requested change to the right tool

- A change to the body -- any of the above -- -> the generic `update`
  tool called with `type="prb"`, either as a **line-range replace** for
  a localized change or a **whole-body replace** otherwise. `content`
  is body markdown only (no frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_prb(id, raw=True)` to see the exact
    body text, identify the 1-based line to start at and how many lines
    to replace -- `offset` is the first body line, `limit` the number of
    lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="prb", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="prb", content)`
    with no `offset`/`limit` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="prb", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, active, resolved, cancelled. Mention this as a
  separate, optional follow-up once `Future State` has genuinely been
  reached
  (`resolved`) or the problem statement is abandoned (`cancelled`) -- do
  not call `set_status` unless the user actually asks for a status
  change.
- A change to `classification` ->
  `set_classification(id, type="prb", classification)` instead --
  `update` never accepts or changes `classification`. Fully free-text;
  a blank or whitespace-only value clears it back to `None`/absent.

## 9. Check the schema, and validate before writing if useful

Fetch `specmgr://prb/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_prb(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
