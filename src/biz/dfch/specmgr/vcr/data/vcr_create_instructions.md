You are drafting a new Verification Case Record (VCR) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_vcr` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_vcr` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing verification case record on this topic first

Call the `list_vcr` tool before creating anything. If a verification
case record for the same REQ/UC (or a similar title/topic) already
exists, tell the user about it and ask (via the `question` tool)
whether they want to revise that one (via the `update_vcr` prompt)
instead of creating a duplicate. Only proceed to step 1 if this is
genuinely a new verification case record.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- `## Verifies` -- mandatory: an optional leading HTML comment giving
  context, then a single-line value in the exact form
  `REQ|UC <uuid>: <title>` (a standard 8-4-4-4-12 hex UUID; `REQ` or
  `UC` is a literal type tag naming which domain the id belongs to),
  followed by a mandatory one-paragraph `notes` paraphrase of why this
  REQ/UC is verified here.
- `## Coverage` -- mandatory: a single-line closed-vocabulary value,
  exactly one of `full`, `partial`, or `none`. No other content is
  allowed in this section.
- `## Acceptance Criteria` -- mandatory, at least one
  `### AC-NNN (Method): <criterion text>` entry (a 3-digit
  zero-padded number starting at `001`; gaps are allowed, e.g. AC-001
  then AC-003, but no two entries may share the same number). `Method`
  is one of the closed DTAIS set, spelled exactly as shown and
  case-sensitive: `Demonstration`, `Test`, `Analysis`, `Inspection`,
  `Special` -- see `specmgr://dtais` for what each word means and when
  to use it. Each entry may optionally carry a free-form descriptive
  paragraph directly under the heading, and/or a `#### Test Steps`
  numbered procedure list -- both are independently optional (an entry
  may have neither, either, or both).
- `## More Information` -- optional freeform supplementary text.
- `## Updates` -- optional, and the last section if present: an
  optional leading HTML comment (conventionally "Newest entry first"),
  then dated `### {title}` entries (e.g. `2026-08-31 — Created`), each
  with a mandatory lead paragraph.

Section order is binding: Verifies -> Coverage -> Acceptance Criteria
-> More Information -> Updates.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `## Verifies`,
`## Coverage`, and `## Acceptance Criteria`, and each optional section
(`## More Information`, `## Updates`). Then use the `question` tool to
elicit the mandatory fields first -- the REQ/UC reference and
paraphrase, the coverage assessment, and at least one acceptance
criterion with its DTAIS method -- then each optional section in turn,
explicitly telling the user they may skip any optional section they
cannot or do not want to answer yet -- a freshly created verification
case record may have zero optional sections.

## 3. Use the template/example/schema as references

Fetch `specmgr://vcr/template` or `specmgr://vcr/example` as a
starting point/style reference, then check `specmgr://vcr/schema` (the
generated JSON Schema) to confirm field names and constraints before
drafting the body. Fetch `specmgr://dtais` if you or the user are
unsure which DTAIS method word applies to a given criterion. Do not
invent field names, section headings, or method words that are not
present there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_vcr(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_vcr(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_vcr`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this verification case record should go through
the `update_vcr` prompt (or directly through the generic
`update(id, type="vcr", content)` and `set_status(id, type="vcr", status)`
tools), not by re-running this prompt.
