You are drafting a new set (SET) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_set` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_set` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing set on this topic first

Call the `list_set` tool before creating anything. If a set for the same
topic (or a similar title, or an overlapping item list) already exists,
tell the user about it and ask (via the `question` tool) whether they
want to revise that one (via the `update_set` prompt) instead of
creating a duplicate. Only proceed to step 1 if this is genuinely a new
set.

## 1. Structure recap (body markdown only, no frontmatter block)

A set is a convenience bundle: it lists one or more already-existing
specmgr artifacts of any (mixed) type, so a design review or a release
can be navigated from one place. The listed items remain the source of
truth for their own content -- the set duplicates nothing, and nothing
in an item ever points back to the set (a set is a reference target for
no one).

- `# {title}` -- H1, mandatory, free-form.
- `## Description` -- mandatory, and opaque: any markdown (paragraphs,
  lists, code blocks, H3 to H6 headings) between the H1 and `## Items`
  is accepted verbatim. Describe what the set bundles and why the items
  belong together here.
- `## Items` -- mandatory, and the last section of the document: a flat
   bullet list with at least one item, in any mix of the 11 reference
   tags (`GOL`, `PRB`, `QA`, `UC`, `REQ`, `RSK`, `DEC`, `VCR`, `SYSRS`,
   `TXT`, `FEAT`). Each bullet is one line:
  `<TAG> <uuid>: <title>` (the `FEAT` tag carries a `feat-NNN-slug` or
  bare `feat-NNN` id instead of a uuid), where `<title>` is the
  referenced document's own H1. A bullet may be followed by an indented
  notes paragraph (a blank line after the bullet line, then the
  paragraph indented under the bullet) saying why this item is in the
  set. Two bullets with the same `<TAG>` and the same id are a
  duplicate and are rejected.

Section order is binding: H1 -> Description -> Items. There are
no other sections: no `## Owner`, no `## Source`, no `## Tags`, no
`## More Information` -- any further H2 is rejected.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the H1 title, the `## Description`
content, and the `## Items` list. Then use the `question` tool to elicit
them in turn:

- The title and the description: ask what the set bundles and why the
  items belong together.
- The items: ask for the artifacts to bundle (any types, in any mix).
  For each artifact, take its reference id from the user or from the
  domain's own `list_<d>` tool (e.g. `list_req`), and use the
  referenced document's own H1 as the bullet's `<title>`. Ask for a
  per-item note only when the user gives one -- the notes paragraph is
  optional.

## 3. Use the template/example tools as references

Call the `get_set_template` and `get_set_example` tools as your
starting point/style reference -- one hop each. Do not invent field
names or section headings that are not present there. Call the
`get_set_schema` tool (the generated JSON Schema) only when you are
structurally uncertain or are resolving a validation error.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_set(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure returns a non-raising `ValidateResult`
   (`valid=False`, with the error message) and nothing is written.
3. Optionally call `validate(type="set", content=content, full=False)`
   first if you want to dry-run the body without writing anything --
   `create_set` already performs the same validation internally, so
   this step is never required, only a convenience.

## 5. Later revisions

Any later change to this set document should go through the `update_set`
prompt (or directly through the generic `update(id, type="set", content)`,
`set_status(id, type="set", status)`, and `set_classification(id, type="set",
classification)` tools), not by re-running this prompt.
