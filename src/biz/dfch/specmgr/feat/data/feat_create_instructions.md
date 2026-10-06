You are drafting a new Feature (FEAT) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_feat` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_feat` builds
type/status/created/updated/version automatically -- `status="planning"`
always (never caller-supplied on create), and the current date+time
timestamp for `created`/`updated`. The `feat-NNN-slug` id, however, is
partly yours to choose: `create_feat` accepts an optional `id` parameter
carrying a full, well-formed `feat-NNN-slug` value -- pass it explicitly
when you already know the GitHub issue number this feature tracks (`NNN`
is meant to be that issue number). When `id` is omitted, it now defaults
to `feat-0-<slug-from-title>` -- **not** an auto-incrementing number --
where `feat-0-...` signals "no issue yet". If the issue number becomes
known later, rename the feature via the `set_feat_id` tool instead of
recreating it (see step 5).

Make a todo list and use the question tool.

## 0. Check for an existing feature on this topic first

Call the `list_feat` tool before creating anything. If a feature with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_feat` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new feature.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# Feature: {title}` -- H1, mandatory, free-form title after the fixed
  `Feature: ` prefix.
- `## Plan` -- mandatory container, no own text:
  - `### Overview` -- mandatory prose: what this feature is and why it
    exists.
  - `### Requirements` -- mandatory bullet list, at least one item, each
    line `REQ-NNN: {text}`.
  - `### Acceptance Criteria` -- mandatory checklist, at least one item,
    each line `- [ ] ACC-NNN: {text}` (or `- [x] ...` once verified).
  - `### Scope` -- mandatory container, no own text, holding two
    mandatory leaves: `#### Included` and `#### Explicitly Out Of Scope`.
  - `### Dependencies` -- optional container, no own text, holding two
    independently optional leaves: `#### Depends On` and `#### Blocks`.
  - `### Design Notes` -- optional prose.
  - `### Related Decisions` -- optional free-form cross-reference list;
    entries may reference an ADR id, a dec id, or any other decision
    record.
  - `### Task List` -- mandatory container, no own text, holding at
    least one `#### Phase NNN: {title}` entry (3-digit zero-padded phase
    number, e.g. "Phase 100"), each with its own flat checklist of at
    least one `- [ ] Task NNN.MMM: {text}` (or `- [x] Task NNN.MMM:
    {text}` once done) task item.
    Task List numbering scheme: phases carry 3-digit zero-padded numbers
    starting at 100, step 10 (`Phase 100`, `Phase 110`, `Phase 120`,
    ...); each task line is `- [ ] Task NNN.MMM: {text}` (or `- [x] ...`
    once done), where `NNN` is the enclosing phase's number and `MMM` is
    a 3-digit zero-padded task number starting at 100, step 10, within
    its phase (`Task 100.100`, `Task 100.110`, ...). The schema enforces
    only the number SHAPES -- `#### Phase NNN: {title}` and the
    `Task NNN.MMM: ` prefix -- not the step-10 increments, not
    uniqueness, and not the match between a task's `NNN` and its
    enclosing phase's number: those are authoring conventions. Gaps are
    deliberate: to insert a new phase or task, pick the number between
    its neighbours (e.g. `Phase 105`, `Task 100.105`) so existing numbers
    never renumber; once assigned, a number is permanent, and removals
    leave gaps.
- `## Progress` -- mandatory container, no own text:
  - `### Current Status` -- mandatory prose: where things stand today.
  - `### Blockers` -- optional free-form list of open blockers.
  - `### Updates` -- mandatory, an optional leading HTML comment (e.g. an
    ordering hint) followed by at least one
    `#### {timestamp} ( - | : ) {title}` entry, newest-first, where
    `{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.SSS` +
    `Z` or `±HH:mm` (the date/time separator may be `T` or a space; a
    date-only timestamp is rejected), joined to the title by `" - "` or
    `" : "` (the em-dash separator is rejected), each with the entry's own
    update/decision text directly under the H4 heading (any markdown
    content -- multiple paragraphs, lists, code blocks, block quotes, not
    just a single paragraph), which is mandatory.
  - `### Decisions Made` -- optional, same shape as `### Updates` (same
    timestamp format, same newest-first ordering, at least one entry once
    the section is present at all).
  - `### Related PRs / Commits` -- optional freeform list.
  - `### More Information` -- optional freeform supplementary text.

Section order is binding, exactly as listed above. There is no
`update_feat`/`set_status_feat` tool of its own -- later changes go
through the generic `update`/`set_status` tools with `type="feat"` (see
step 5).

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `Overview`,
`Requirements`, `Acceptance Criteria`, `Scope` (both `Included` and
`Explicitly Out Of Scope`), `Task List`, `Current Status`, `Updates`, and
each optional section (`Dependencies`, `Design Notes`,
`Related Decisions`, `Blockers`, `Decisions Made`,
`Related PRs / Commits`, `More Information`). Then use the `question`
tool to elicit the mandatory fields first, then each optional field in
turn, explicitly telling the user they may skip any optional field they
cannot or do not want to answer yet.

## 3. Use the template/example/schema as references

Fetch `specmgr://feat/template` or `specmgr://feat/example` as a
starting point/style reference, then check `specmgr://feat/schema` (the
generated JSON Schema) to confirm field names and constraints before
drafting the body. Do not invent field names or section headings that
are not present there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_feat(content, id="feat-42-my-slug")` if the GitHub issue
   number is already known, or `create_feat(content)` otherwise -- the
   latter defaults the id to `feat-0-<slug-from-title>` (no
   max+1 auto-generation). `content` is body markdown only; the rest of
   the frontmatter is always built automatically. This raises `ValueError`
   before any write if a caller-supplied `id` does not match the
   `feat-NNN-slug` shape, and raises `FileExistsError` before any write if
   the resulting id/folder (given or defaulted) already exists -- in
   either failure case nothing is written. A structural or field
   validation failure on `content` likewise raises uncaught and nothing is
   written.
3. Optionally call `validate(type="feat", content=content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_feat`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this feature should go through the `update_feat`
prompt (or directly through the generic `update(id, type="feat", content)`,
`set_status(id, type="feat", status)`, and
`set_classification(id, type="feat", classification)` tools), not by
re-running this prompt. A change to the feature's own id specifically --
e.g. renumbering a `feat-0-...` default to `feat-NNN-...` once the GitHub
issue number is known -- goes through neither of those: use the dedicated
`set_feat_id(id, new_id)` tool instead, which renames the containing
folder and rewrites the frontmatter `id` in one atomic operation (never a
hand-edit).
