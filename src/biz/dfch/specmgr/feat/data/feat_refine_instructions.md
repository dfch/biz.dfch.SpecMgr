You are reviewing a planned Feature (FEAT) document for implementation
readiness, id: $id

This is a pre-implementation review: the plan is not built yet, and you
have two jobs -- (1) assess the plan against the readiness checklist
below, and (2) apply the improvements the user approves to the plan
itself. Follow this review-and-edit sequence exactly. Every read and
every write of the document goes through the specmgr MCP tools named
below: host file tools appear only in the final "Fallback" section, for
hosts that cannot reach those tools.

Make a todo list (one entry per checklist area below), and use the
`question` tool whenever a finding needs a user decision -- do not guess
at design decisions the plan leaves open.

## 1. Read the plan

- Call `get_feat($id)` (the parsed document) to see the frontmatter
  fields -- `id`/`type`/`status`/`created`/`updated`/`version` (plus
  `classification` when set) -- which step 5's re-check reuses, and to
  see which of the sections are present.
- Call `get_feat($id, raw=True)` for the frontmatter-stripped body --
  the exact text the `update` tool's `offset`/`limit` address. Never
  assume prior state: the on-disk `.specmgr/feat/$id/README.md` file is
  the source of truth and may have been hand-edited since you last saw
  it (direct hand/agent editing of the plan is the sanctioned workflow
  for this domain, not just an MCP-tool convenience).

## 2. Assess plan readiness

Apply the four checklist areas below to the plan you just read, and
collect a finding for every defect you see (each citing the area, the
section, and the 1-based body line):

- **Testable acceptance criteria**: every `ACC-NNN` must be objectively
  checkable -- a pass/fail you could verify without reading anyone's
  mind. Vague criteria ("should be good", "works well", "is ready") are
  findings; so is an ACC no task in the Task List actually covers.
- **Phase ordering and dependencies**: the phases must run in the order
  they are listed -- no phase or task may depend on a phase listed after
  it, or on a phase that does not exist at all. The numbering must
  follow the `Phase NNN` / `Task NNN.MMM` scheme (3-digit numbers,
  phases and tasks starting at 100, step 10, gap-friendly, permanent
  once assigned).
- **Scope clarity**: every `Included` item must map to at least one
  task, no task may do anything listed under `Explicitly Out Of Scope`,
  and every phase must state what makes it done (its own gate).
- **Unresolved decisions**: an open `[NEEDS DECISION]` flag, a
  contradiction between the Requirements, the Acceptance Criteria, and
  the Task List, or an instruction an implementer would have to guess at
  is a finding.

## 3. Present the findings and ask

Show the user the findings (area, section, line, and the fix you would
apply). Use the `question` tool to ask which findings to apply -- apply
only what the user approves. If a finding needs a decision only the user
can make (rather than a wording or ordering fix), report it as such
instead of guessing. If there are no findings, say so, report that the
plan is ready to implement, and stop.

## 4. Apply the approved fixes with the generic `update` tool

Apply each approved fix with the generic `update` tool called with
`type="feat"`. A **line-range replace** is the preferred form, so
unchanged regions of the plan stay byte-identical:

- Get the edit coordinates only from a `get_feat($id, raw=True,
  numbered=True)` read -- every line prefixed with its 1-based
  body-line number, so a number seen in the output can be fed straight
  into `update`'s `offset`. Never from a raw file read of
  `.specmgr/feat/$id/README.md`: the YAML frontmatter block is
  variable-length, so a raw file's line numbers are never body-line
  coordinates. And never feed the `numbered=True` output back verbatim
  as `content` -- strip the `"<n>: "` prefix from each line first.
- Call `update($id, type="feat", content=<the replacement lines>,
  offset=<the first body line>, limit=<the number of lines>)` passing
  only the replacement lines. The server splices the fragment into the
  current on-disk body and validates the result as a whole document
  before writing anything.
- After each `update`, re-read with `get_feat($id, raw=True,
  numbered=True)` before the next edit -- the body has changed, so every
  line number you had before is stale.
- Use a **whole-body replace** (`update($id, type="feat",
  content=<the full replacement body>)` with no `offset`/`limit`) only
  when a single fix spans most of the document -- carry forward every
  section you are not intentionally changing, or it will be dropped.
- Never renumber an existing phase or task: insertions take a new number
  between their neighbours, and once assigned a number is permanent.
- Do not change the plan's `status` or `id` as part of a readiness
  review: those are the generic `set_status` tool's and the
  `set_feat_id` tool's jobs, not yours.

## 5. Re-check the edited plan

Call the generic `validate` MCP tool with `type="feat"`, `content` set
to the plan's full text, and `full=True` (i.e.
`validate(type="feat", content=<the full document text>, full=True)`).
The full text is the YAML frontmatter block -- the fields `id`/`type`/
`status`/`created`/`updated`/`version`, plus `classification` when set,
each taken verbatim from a fresh parsed `get_feat($id)` read after the
last edit -- followed by a blank line and the current body from a fresh
`get_feat($id, raw=True)` read. While `validate` returns `valid: false`,
read the enriched `errors[].message` (field path, 1-based line,
cause/fix hint) and fix it under step 4's rules. Finish with one more
parsed `get_feat($id)` read: the refinement counts as done only if the
real file on disk parses.

## 6. Report

Return: the findings, which of them the user approved, the edits
applied (per finding, the line before and the line after), and the
final re-check outcome. Do not commit, and do not touch any file other
than the plan's own README.

## Fallback: hosts without the specmgr tools

If your host cannot reach the specmgr MCP tools (`get_feat`, the
generic `update`, and the generic `validate` are all unavailable),
degrade to your host's own file tools: read
`.specmgr/feat/$id/README.md` with your host's own file-read tool, apply
the same user-approved fixes with your host's own file `edit`/`write`
tools (coordinates from the raw file itself, the frontmatter block in
mind), and re-check by re-reading the file in full and, where the host
offers one, running the document's own parser over the full text. The
checklist (step 2) and the user-approval rule (step 3) are unchanged.
