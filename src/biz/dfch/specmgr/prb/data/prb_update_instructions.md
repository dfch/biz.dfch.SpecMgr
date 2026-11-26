You are revising an existing Problem Statement (PRB) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update`, and every change to the document
goes through the specmgr MCP tools listed below -- with one exception:
the "Old-shape recovery" block in step 1 repairs a document that fails
to parse with the host's own file-read/file-write tools and leaves its
frontmatter block byte-for-byte unchanged.

## 1. Read current state first

Call `get_prb(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

**Old-shape recovery.** If `get_prb(id)` returns a parse failure whose
error names the `problem_statement` field (the body is
missing the mandatory lead sentence directly under the H1, or the first
paragraph does not match the template), do not treat this as a fatal error:

1. No specmgr read returns the body of a document that fails to parse
   (a `raw=True` read of one returns the parse-failure result, never the
   body text) -- read the raw file with the host's own file-read tool at
   the `path` the parse-failure result carries. The raw file text starts
   with the YAML frontmatter block, followed by the body.
2. Look at the document's own `### What Is the Problem?`,
   `### Who Is Impacted?`, and `### Why Is It a Problem?` answers (if
   present) under `## Current State`. If the first paragraph under the H1
   does not match the template, read that existing paragraph as well: it
   is derive input for the same 4 blanks. Derive a first draft of the lead
   sentence's 4 blanks from them the same way `create_prb`'s own
   derive-then-confirm flow does: `What` -> both `[Current state]` and `[specific issue]` (a single `What` answer must populate two distinct blanks, so draft your best split of it across the two -- e.g. the underlying condition into `[Current state]`, the concrete symptom into `[specific issue]`); `Who` -> `[stakeholder]`; `Why` -> `[underlying cause]`.
   For any blank with no answer to derive from, use the `question` tool
   to ask for it directly. Then show the fully composed sentence --
   `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`
   -- to the user and use the `question` tool to confirm or refine it.
3. Put the confirmed sentence into the raw file text from sub-step 1 above:
   - If the lead paragraph is missing:
     Insert the confirmed sentence as its own paragraph directly under the
     H1 title (after any existing leading comment, before
     `## Current State`).
   - If the first paragraph under the H1 does not match the template:
     replace that paragraph with the confirmed sentence. Do not add the
     sentence as a second paragraph above it.
   Leave the frontmatter block byte-for-byte unchanged -- `id`,
   `created`, `status`, `version`, and `updated` included: a repair is
   not an edit.
4. Dry-run the repaired text with
   `validate(type="prb", content=<the full raw file text>, full=True)`
   -- `full=True` because the text includes the frontmatter block, not
   just the body. While it returns `valid: false`, read the
   `errors[].message`, apply the smallest fix, and call `validate`
   again, until it returns `valid: true`.
5. Write the `validate`-green text back to the same `path` with the host's own
   file-write tool -- the generic `update`/`edit` tools re-parse the
   existing document before writing and cannot repair one.
6. Confirm the repair with a real `get_prb(id)` call -- it must parse
   successfully -- before proceeding to `## 2. If no change was specified`
   below with the originally requested change. That change goes through
   `update` as usual, which bumps `updated` itself.

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
    or section): first call `get_prb(id, raw=True, numbered=True)` to
    see the exact body text -- every line prefixed with its 1-based
    body-line number, so no manual counting is needed and a number seen
    can be fed straight back into `update`'s `offset` -- identify the
    1-based line to start at and how many lines to replace -- `offset`
    is the first body line, `limit` the number of lines
    (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="prb", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical. `offset`/`limit` address the frontmatter-stripped
    body, never the raw on-disk `.md` file: the YAML frontmatter block
    is variable-length, so a raw file read's line numbers are never the
    same as body-line coordinates -- and never feed the `numbered=True`
    output back verbatim as `content`: strip the `"<n>: "` prefix from
    each line first.
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

## 9. Check the schema only for structural changes, and validate before writing if useful

Call the `get_prb_schema` tool (the generated JSON Schema) only for a
whole-body rewrite or a structural change -- adding, removing, or
renaming sections, or editing closed-form content -- to confirm field
names and constraints. Skip the fetch for a local splice (a line-range
replace), where the raw body is already in context: `update` still
validates the spliced result as a whole document before writing
anything, so the skip is safe. Optionally call
`validate(type="prb", content=content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
