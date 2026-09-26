You are repairing a `$type` document that currently fails to parse.

Target:
- type: `$type`
- id: $id

Follow this sequence exactly. The raw read in step 2 and the write-back in
step 5 use YOUR OWN host file read/write tools (e.g. `read`/`write`), not
any specmgr MCP tool: no specmgr MCP tool can return the raw content of a
document that fails to parse -- `get_$type` with `raw=True` and the generic
`update` tool both re-parse the existing document first, and
`update`'s per-domain adapters convert that parse failure into the
domain's not-found error before anything is written -- so a document that
fails to parse is structurally unreachable through the MCP server for both
reading and writing. If your host has no file read/write tools, skip
straight to "Diagnose-only degradation" below and do not attempt any step
that needs them.

Make a todo list and use the `question` tool whenever something is
ambiguous -- do not guess.

## 1. Discover the failing document and its error

- **With an id** (the `id:` line above is a real id, not the literal
  `(not given --` placeholder text): call `get_$type` with that id. A
  document that exists but fails to parse is returned, NOT raised: the
  result carries `error` (the parse-failure message -- field path and
  cause, plus a 1-based line reference and fix hint for structural
  failures -- the same text `list_$type()`'s failed row carries) and
  `path` (the absolute on-disk file you will read in step 2 and write
  back in step 5). That `error` is the defect you will fix. If the id is
  truly absent, `get_$type` raises the domain's not-found error -- in
  that case there is nothing to repair under that id: use the `question`
  tool to ask for the right id (or scan `list_$type()`'s failed rows)
  rather than guessing. If the call instead returns the parsed document
  (it parses cleanly), there is nothing to repair -- report that and
  stop.
- **Without an id**: call `list_$type()` and scan its rows for the failed
  one: its `title` and `status` carry the fixed `<failed to parse>`
  marker, its `id` is `null`, and its `ref`/`path`/`error` are populated.
  Its `error` holds the parse failure (field path and cause -- a 1-based
  line reference and fix hint for structural failures, the violated
  pattern and offending value for closed-vocabulary failures) -- read
  it. Remember the row's `path` (the on-disk file you will read and later
  write) and, if the document carries an id in its frontmatter, its `id`
  as well. If no row carries the `<failed to parse>` marker, nothing is
  failing -- report that and stop. If more than one row does, use the
  `question` tool to ask which document to repair -- do not guess.

## 2. Read the raw file with your own file-read tool

Read the file at the document's on-disk `path` with your host's own
file-read tool, not any specmgr MCP tool (see the note above -- none can
return it). You need the complete raw text -- YAML frontmatter and body
together -- because that is the text `validate` will check with `full=True`
in step 4 and the text you will write back in step 5.

## 3. Fix only what the error addresses

Apply the smallest fix the enriched error names: the field at the given
field path, on the given 1-based line, per the given cause/fix hint. Do
not reformat, rewrap, reorder, or "improve" anything else in the document.
While doing so:
- Preserve the YAML frontmatter's `id`, `created`, `status`, and `version`
  fields byte-for-byte -- do not change their values or their order.
- Leave the frontmatter's `updated` field exactly as it is -- a repair is
  not an edit, and `updated` must not move.
- Change nothing outside the defect the error addresses.
If the error's cause/fix hint does not pin down a unique fix, use the
`question` tool to ask -- do not guess.

## 4. Loop the generic `validate` tool until green

Call the generic `validate` MCP tool with `type="$type"`, `content` set to
the full raw text you are about to write, and `full=True` (i.e.
`validate(type="$type", content=<full raw text>, full=True)`) --
`full=True` because that text includes the frontmatter, not just the body.
While it returns `valid: false`, read the enriched `errors[].message`
(field path, 1-based line, cause/fix hint), apply the smallest fix under
step 3's rules, and call `validate` again. Repeat until it returns
`valid: true`.

## 5. Write the repaired text back with your own file-write tool

Write the final, `validate`-green text -- the complete raw text,
frontmatter and body -- back to the SAME on-disk `path` with your host's
own file-write tool, preserving the file's existing encoding and line
endings. NEVER write it back via the generic `update` MCP tool: `update`
re-parses the existing document first, and for a document that fails to
parse that parse failure becomes the domain's not-found error before any
write happens -- `update` is structurally unable to repair this document.

## 6. Confirm the repair against the file as it now exists on disk

A green `validate` result only proves the in-memory text was well-formed;
it does not prove the bytes your host's file-write tool actually put on
disk (encoding, line-ending, or partial-write differences are all outside
the MCP server's control, since the write itself was host-native, not a
specmgr tool call). So the loop does not end at step 5:
- **With an id**: call `get_$type` with the same id again. The repair
  succeeded only if this call now returns the parsed document (a real
  parse of the real file on disk) rather than a result carrying
  `error`; if it still returns the `error`/`path` result, the on-disk
  file is still broken -- re-read, compare against the validated text,
  fix the difference, and repeat from step 4.
- **Without an id**: call `list_$type()` again. The repair succeeded only
  if the row at the same `path`/`ref` no longer carries the
  `<failed to parse>` marker in its `title`/`status` and its `error` is
  `null` (its `id` is populated only if the document actually carries an
  id in its frontmatter).
Only a real parse of the real file counts as success. If the confirmation
fails, re-read the file with your own file-read tool, compare it against
the text that was validated, fix whatever the host's write put on disk
differently, and repeat from step 4.

## Diagnose-only degradation

If your host has no file read/write tools, you cannot apply the repair at
all: do not touch the file. Report (1) the parse failure you found
in step 1, (2) the exact fix you would apply per step 3, and (3) the file
`path` the human must edit -- then stop.

## Scope

- `type` is one of the whole-body specmgr domains:
  req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs. ADR is explicitly out
  of scope: it is not a whole-body domain and has no generic dry-run
  `validate` tooling of its own (its standalone `validate_adr` re-reads the
  ADR from disk by id), so this repair loop is not defined for it.
