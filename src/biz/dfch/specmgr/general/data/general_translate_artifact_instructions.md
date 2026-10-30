You are translating a `$type` document into another language, or bringing
an existing translation up to date.

Target:
- type: `$type`
- id: $id
- source language: `$source_language`
- target language: `$language`

Scope: only the eleven i18n-eligible domains (`req`, `uc`, `tsk`, `qa`,
`prb`, `gol`, `rsk`, `dec`, `sop`, `vcr`, `sysrs`). `feat` and `adr` are
always English and are out of scope: they have no language variants, and
this flow never touches them.

Make a todo list and use the `question` tool whenever something is
ambiguous -- do not guess. Use only the existing specmgr tools for every
read and write. You translate the text yourself; no specmgr tool translates.
Never commit, never write the English document, and never change a
document's frontmatter `id` or `status` (a new variant starts with the
domain's own create status; change a status only if the user asks).

## 1. Read the guidance first

Read the `specmgr://i18n` resource before anything else. It defines the
directory layout, the heading tables, the per-domain never-translate list,
the create-versus-update decision, and the error semantics. Where anything
below and that resource differ, the resource wins.

## 2. Check that the language pair is usable

- The target language must not be `en`: English is the canonical source
  language and is never written by this flow. If the target is `en`, stop
  and report.
- The target and the source language must differ. If they are equal, stop
  and report.
- If any tool call or resource read (including the heading-table read of
  step 5) raises a `ValueError` saying there is no heading-mapping table for
  a language, stop and report: a table file
  `general/data/headings/<language>.json` must be added to the package
  first. Do not invent a table, and do not write untranslated or partly
  translated content as a workaround.

## 3. Read the source document

Call `get_$type` with `id` = $id, `raw=True` and `language="$source_language"`.
This returns the source body text exactly as stored on disk (the text you
translate).

- A truly-absent id raises the domain's not-found error: stop and report
  (use the `question` tool to ask for the right id, or scan `list_$type()`).
- If the call returns a `ParseFailureResult` (`error`/`path`/`id`), the
  source exists but fails to parse. Stop and report the `error` and `path`.
  For an English source, name the `repair` prompt as the way to fix it
  first. Never translate a broken source.
- A variant can only exist next to its English source. If the source
  language is not `en`, the English document with the same id must also
  exist; if a later write reports the English source as missing, stop and
  report.

## 4. Decide create or update

Call `get_$type` with `id` = $id, `raw=True` and `language="$language"`:

- **Not-found error:** the target variant does not exist. You will **create**
  it in step 7 with `create_$type(content, language="$language", id=$id)`.
- **A document is returned:** the variant exists. You will **update** it in
  step 7. Read this text carefully: it is the existing translation. Keep its
  wording wherever the source did not change, and change only what the
  source now says differently (this keeps the translation stable).
- **A `ParseFailureResult`:** the target variant exists but fails to parse.
  Stop and report its `error` and `path`; do not overwrite it.

## 5. Load the heading table

Read the target language's heading table from the resource
`specmgr://i18n/headings/$language`. It returns the table as JSON: a flat
object mapping `<translated heading text>` to `<canonical English heading
text>`. If the source language is not `en`, also read
`specmgr://i18n/headings/$source_language` and map the source's headings
back to canonical English through it first. To translate a canonical heading,
find the entry whose **value** is that heading; the entry's **key** is the
text to write.

A read that raises the no-table `ValueError` is a stop condition (step 2).
Only if your host cannot read MCP resources at all, fall back to reading the
JSON file `general/data/headings/$language.json` in the specmgr package with
your host's file tools (in a source checkout:
`src/biz/dfch/specmgr/general/data/headings/$language.json`). If you cannot
obtain the table either way, do not guess heading translations: keep every
heading canonical English (this is valid, merely untranslated) and say so in
the final report.

## 6. Translate

Produce the full target body text.

**Translate:**
- free-form prose (paragraphs, list-item prose, block-quote questions and
  their answers, update-entry titles and bodies, option, step, extension,
  and criterion names), the H1 title (`sysrs`: only the part after its fixed
  prefix, see below), and the prose inside HTML comments
  (keep the `<!--` and `-->` delimiters);
- the heading text of fixed-text headings, **only** with the table's text
  for that canonical heading (section 5).

**Never translate (closed vocabulary and schema constants, REQ-010).** Copy
these from the source exactly:
- the YAML frontmatter is not part of the body you write; never add one;
- `req`: the `## Level` value (`MUST`, `SHOULD`, `MUST NOT`, `SHOULD NOT`,
  `MAY`) and the numeric `## Priority` value; keep the `## Characteristics`
  bullets (ISO/IEC 25010:2023 names) and `## Tags` bullets canonical;
- `gol`: the numeric `## Priority` value; keep `## Tags` bullets canonical;
- `rsk`: the `## Strategy` word (`transfer`, `accept`, `reduce`, `avoid`)
  and the `### Probability N` / `### Impact N` heading tokens;
- `vcr`: the `## Coverage` word (`full`, `partial`, `none`), the
  `### AC-NNN (Method): ...` heading tokens (`AC-NNN` and the DTAIS method
  word `Demonstration`, `Test`, `Analysis`, `Inspection`, `Special`; only
  the text after the colon is translated), and the `## Verifies` line;
- `dec`: the `### Option N: ...` heading token (only the name after the
  colon is translated);
- `sop`: the `### Step N: ...` heading token (only the name is translated);
- `uc`: the `### Extension Na. ...` and `### Step N: ...` heading tokens
  (only the text after them is translated); keep the `### Level` word
  (`Summary`, `User Goal`, `Subfunction`) canonical;
- `qa`: the `**<d>.<NNNN>**: ` question prefix of every question and the
  `TODO: answer pending` placeholder line of an unanswered question;
- `tsk`: the `[ ]` / `[x]` markers and each item's checked state;
- `prb`: the `problem_statement` lead paragraph under the H1 (the one
  sentence `[Current state] is causing [specific issue], for [stakeholder]
  because [underlying cause].`) stays canonical English in every language
  (ADR 38efdb66 item 11): copy it byte for byte; its translation would be
  rejected by the schema;
- `sysrs`: the H1 prefix `System Requirements Specification: ` (translate
  only the title after it) and the type-tagged cross-reference bullets;
- every domain: cross-reference lines `<TAG> <uuid>: <title>` (the tag, the
  uuid, and the title text; only the paraphrase paragraph under a
  reference is translated), update-entry heading timestamps and their
  separator (` - ` or ` : `), uuids, numbers, URLs, code spans, and fenced
  code blocks.
- Headings that carry data tokens have no table entry: keep the token part
  and translate only the free-text part.

**Preserve the structure exactly:** the same headings in the same order and
at the same levels, the same blank-line layout, the same list structure.
Do not add, drop, or reorder sections. Do not soft-wrap a list item: each
list item stays on one physical line, as in the source (a wrapped list item
is rejected).

## 7. Write, with bounded retries

You cannot dry-run a translated body: the generic `validate` tool is
English/canonical-only and has no `language` parameter. The write tools
validate the body themselves, so call the write tool and read its result:

- **Create:** `create_$type` with `content` = the translated body,
  `language="$language"`, `id` = $id.
- **Update:** whole-body `update` with `type="$type"`, `id` = $id,
  `content` = the translated body, `language="$language"`. For a small
  change you may use `edit` (`old_str` must match the variant's on-disk
  text byte for byte, including its translated headings, and be unique).

A **non-raising `ValidateResult` with `valid=False`** means nothing was
written. Read `errors[0].message` (field path, 1-based line, cause): the
usual cause is a translated closed-vocabulary token, a heading that is
neither canonical nor in the table, or a changed structure. Fix exactly
that, and retry. Make at most 3 write attempts; if the third still fails,
stop and report the last message together with your translated text. A
raised `ValueError` (no heading table, bad `language`, a missing or
misused `id`) or `FileExistsError` is not retryable by editing the text:
stop and report it (a `FileExistsError` means the variant exists: go back
to step 4 and update instead).

## 8. Verify against what is on disk

- Call `get_$type` with `id` = $id and `language="$language"`. It must
  return the parsed document (not an `error`-carrying result).
- Re-read the variant with `raw=True` and check that every
  never-translate token from step 6 is identical to the source.
- Find the written file's path: `list_$type(language="$language")` returns
  one row per variant, each with its `path`.

## 9. Report

Report: the document's `type`, `id`, source and target language, whether
you created or updated the variant, the written `path`, the number of write
attempts and any `ValidateResult` message you had to fix, every `question`
you asked and its answer, and anything left untranslated on purpose (for
example headings kept canonical because the table was unreadable). The
translation is done only once step 8's read of the real file succeeded. Do
not commit, do not write the English document, and do not touch any other
file.
