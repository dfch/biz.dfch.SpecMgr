# Multi-Language Artifact Variants (i18n)

How specmgr stores several language variants of the same artifact, and the
rules a translation must follow so the variant stays valid. Read this before
translating or updating a variant (the `translate_artifact` prompt reads it
first).

## 1. Scope

- **In scope (eleven domains):** `req`, `uc`, `tsk`, `qa`, `prb`, `gol`,
  `rsk`, `dec`, `sop`, `vcr`, `sysrs`.
- **Out of scope, permanently:** `feat` (always English, no language
  variants, no `language` parameter on any `feat` surface) and `adr` (always
  English, no `language` parameter on any `adr` surface). A non-default
  `language` passed to a generic tool for either type is a `ValueError`.
- English (`en`) is the default and canonical language. It is the source of
  truth for the document's identity (id, file name) and its closed
  vocabulary.

## 2. Directory layout and basename rule

- **English** stays exactly where it always was: `docs/{type}/<type>-<id>-<slug>.md`.
  An omitted `language` and an explicit `language="en"` both mean this flat
  directory.
- **Every other language `L`** lives in a subfolder:
  `docs/{type}/{L}/<type>-<id>-<slug>.md`.
- **The variant's file name is byte-identical to the EN source's file name.**
  The slug always derives from the EN title, never from the translated
  title. Re-titling or translating a document never moves a variant's file.
- **The `id` is shared.** Every language variant of one artifact carries the
  same `id` in its frontmatter; the id is never language-qualified.
- The language of a variant is encoded by its location only. The frontmatter
  schema (field names, `id`, `type`, `status`, `version`, ...) is the same
  in every language.
- A variant can only be created when its EN source (same `id`) exists.
- Only `.md` files take part. The EN-only consumers (`find_related`,
  `find_similar_text`, `list_references`, `get_reference_diagram`,
  `get_reference_diagram_all`) never see a language subfolder; every
  reference and similarity hit resolves to the EN variant.

## 3. Language vocabulary and heading tables

- A `language` is an ISO 639-1-shaped lowercase two-letter code (`^[a-z]{2}$`,
  for example `de`). The shape is checked before any filesystem access; a
  value such as `../../etc`, `de/x`, `DE`, or an empty string is a
  `ValueError`.
- The shape is an open set. The usable set is closed by the **heading tables**:
  one flat JSON object per language in package data,
  `general/data/headings/<language>.json`, mapping
  `<translated heading text>` -> `<canonical English heading text>`.
  Heading text is the inline text without the `#` markers and without
  surrounding whitespace. A code without a table file is shape-valid but
  unusable: every tool raises an actionable `ValueError`. Adding a language
  means adding one table file; this flow never invents one.
- Resolution happens when a non-EN document is parsed: each heading line
  (outside fenced code blocks) is looked up in the table. A hit is rewritten
  to its canonical English text; a heading without an entry stays as it is.
  The parsed model therefore always holds canonical headings and the same
  canonical keys as the EN parse. The on-disk file keeps its translation
  (`get_<d>(raw=True, language=...)` returns it verbatim).
- Consequence: **a canonical English heading is always valid in a variant**
  (it is just untranslated). A translated heading is valid only if it is
  exactly the table's text for that canonical heading.
- The table is keyed translated -> canonical. To translate a canonical
  heading, find the entry whose **value** is that canonical heading; the
  entry's **key** is the translated text to write.
- **Read a table through the resource template
  `specmgr://i18n/headings/{language}`** (JSON, `application/json`, for
  example `specmgr://i18n/headings/de`): a read-only view of the same table
  the parsers apply, loaded and validated by the same loader, so no host
  file tool is needed. The `language` is shape-checked first; `en` has no
  table (English is the canonical form), and a shape-valid language without
  a table file is a `ValueError` (add `general/data/headings/<language>.json`
  first).

## 4. Tool surface

| operation | tool call |
| --- | --- |
| read a variant (parsed, canonical keys) | `get_<d>(id, language=L)` |
| read a variant's on-disk text verbatim | `get_<d>(id, raw=True, language=L)` (optional `offset`/`limit`/`numbered`) |
| list one language's variants | `list_<d>(language=L)` (single language per call; no "all languages" mode) |
| create a variant of an existing EN document | `create_<d>(content, language=L, id=<shared EN id>)` |
| replace a variant's body | `update(type, id, content, language=L)` |
| surgical change of a variant's body | `edit(type, id, old_str, new_str, language=L)` |
| other generic tools | `set_status`, `set_classification`, `delete` also accept `language=L` and act on the variant only |
| which languages an artifact exists in | `list_languages(type, id)` (read-only; `en` first when the EN source exists) |
| is a variant in sync with its source | `check_translation_drift(type, id, language, source_language="en")` (read-only; structural drift and staleness; no tool translates) |

- The generic dry-run `validate` tool has **no** `language` parameter. It
  validates canonical (English-heading) content only, so a translated body
  cannot be dry-run: the write tools themselves validate it (see section 7).
- Every write to a variant bumps only that variant's own `updated`. The EN
  document is never touched.

## 5. What to translate, and what never to translate

**Translate:** free-form prose (paragraphs, list-item prose, block-quote
questions and their answers, update-entry titles and bodies, option, step,
extension and criterion names), the H1 title (`sysrs`: only the part after its
fixed prefix, see section 5.2), the prose inside HTML comments
(keep the `<!--`/`-->` delimiters), and the heading text of fixed-text
headings (only through the table, section 6).

**Never translate (REQ-010).** These tokens stay in canonical English (and
unchanged) in every language. The first group is enforced by the schema:
translating a token there makes the write tool return a non-raising
`ValidateResult` with `valid=False` and writes nothing. The second group is
kept canonical by convention: the parser would accept a translation, but the
tokens are identifiers other artifacts, tools, or readers depend on.

### 5.1 Common to every domain

- The YAML frontmatter (not part of the body you write; tools manage `id`,
  `type`, `status`, `classification`, `created`, `updated`, `version`).
  Closed-vocabulary `status`/`classification` values are never translated.
- The structure: heading levels (`#` counts), heading order, blank lines,
  list markers, numbered-list numbers.
- Cross-reference lines `<TAG> <uuid>: <title>` with the tags `GOL`, `PRB`,
  `QA`, `UC`, `REQ`, `RSK`, `DEC`, `ADR`, `VCR`, `SYSRS`, `SOP`, `FEAT`:
  the tag word, the uuid, and the `: <title>` text stay exactly as in the
  source (the title is the title of the referenced document). Only the
  paraphrase prose of a reference (the notes paragraph under it) is
  translated. Schema-enforced where a section restricts the tags (the
  cross-reference sections of `req`, `gol`, `dec`, `sop`, `sysrs`, and
  `vcr`'s `## Verifies`).
- Timestamps and the separator in update-entry headings:
  `### 2026-08-31 00:00:00.000Z - <title>` (separator ` - ` or ` : `).
  Schema-enforced; the entry title after the separator and the entry body
  are prose and are translated.
- UUIDs, numbers, URLs, file paths, identifiers, code spans, and fenced code
  blocks.

### 5.2 Closed vocabulary and schema constants, per domain

| domain | schema-enforced (never translate) | canonical by convention |
| --- | --- | --- |
| `req` | `## Level` value: `MUST`, `SHOULD`, `MUST NOT`, `SHOULD NOT`, `MAY` (RFC 2119); `## Priority` value (integer 0-99); the cross-reference tags | `## Characteristics` bullets (the ISO/IEC 25010:2023 characteristic names of `specmgr://iso25010`); `## Tags` bullets (labels used for grouping and filtering) |
| `gol` | `## Priority` value (integer 0-99); the cross-reference tags | `## Tags` bullets |
| `uc` | `### Extension <N><letter>. <text>` heading token (`Extension`, the number, the optional lowercase letter, the dot); `### Step <N>: <text>` sub-variation heading token (`Step`, the number, the colon); numbered-list numbers | `### Level` words (`Summary`, `User Goal`, `Subfunction`); the `Subordinate:`, `Superordinate:`, `Extension:` labels in `### Related Use Cases` bullets and the `return to step N` / `continue to step N` phrases (read by the EN-only diagram renderer); `UC <uuid>` references |
| `tsk` | the `[ ]` / `[x]` checkbox markers (and each item's checked state); the update-entry heading timestamp | |
| `qa` | the question prefix `**<d>.<NNNN>**: ` (single category digit, 4-digit number) of every question block quote; the `> ` block-quote structure | the `TODO: answer pending` placeholder line of an unanswered question (keep it verbatim) |
| `prb` | the `problem_statement` lead paragraph (the one sentence under the H1, template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`): it is **exempt from translation** (ADR 38efdb66 item 11), stays canonical English in every language, copy it from the source byte for byte | |
| `rsk` | `## Strategy` word: `transfer`, `accept`, `reduce`, `avoid` (TARA); the `### Probability <1-5>` and `### Impact <1-5>` heading tokens (the word and the digit) under both `## Initial Assessment` and `## Residual Assessment` | `## Tags` bullets; names of people, roles, and systems in `## Owner` and `## Scope` |
| `dec` | the `### Option <N>: <name>` heading token (`Option`, the number, the colon; the name is prose); the update-entry heading timestamp; the cross-reference tags | `## Tags` bullets |
| `sop` | the `### Step <N>: <name>` heading token (`Step`, the number, the colon; the name is prose); the update-entry heading timestamp; the cross-reference tags | the lifecycle words (approval/effectivity) live in the frontmatter `status` and are never translated |
| `vcr` | `## Coverage` word: `full`, `partial`, `none`; the `### AC-<NNN> (<Method>): <text>` heading token (`AC-`, the 3-digit number, and the DTAIS method word `Demonstration`, `Test`, `Analysis`, `Inspection`, `Special`, see `specmgr://dtais`; the text after the colon is prose); the `## Verifies` line `REQ|UC <uuid>: <title>`; the update-entry heading timestamp | |
| `sysrs` | the H1 prefix `System Requirements Specification: ` (only the title after it is prose and is translated); the type-tagged cross-reference bullets (`GOL`, `PRB`, `QA`, `UC`, `DEC` or `ADR`, `RSK`, `REQ`, `VCR` per section); the update-entry heading timestamp | the acronym term in `## Definitions and Acronyms` bullets (`**AC** -- ...`) |

The fixed-text headings of every domain (for example `## More Information`,
`## Tags`, `## Source`, the RASCI headings `### Accountable`/`### Responsible`/
`### Support`/`### Consulted`/`### Informed`, `#### Test Steps`, the seven
`prb` 5W2H question headings) are translated only through the table, never
freely.

## 6. How to translate headings

1. Take the canonical heading from the EN source (or, for a non-EN source,
   resolve it back to canonical through the source language's table).
2. If the target language's table has an entry whose value is that canonical
   heading, write the entry's key. If it has none, keep the canonical
   English heading (valid, merely untranslated).
3. Headings that carry data tokens (`Option <N>: <name>`, `Step <N>: <name>`,
   `AC-<NNN> (<Method>): <text>`, `Extension <N><letter>. <text>`,
   `Probability <N>`, `Impact <N>`, timestamp-led update entries) have **no**
   table entry. Keep the token part canonical and exactly as in the source;
   translate only the free-text part (the option, step, criterion, extension,
   or update title).
4. Never reorder, add, or drop a heading. Never change a heading's level.
5. The H1 title is free-form: translate it, except for `sysrs`, whose H1 must keep
   the prefix `System Requirements Specification: ` (translate only the title after
   it). The file name does not change.

## 7. Create versus update

- Probe the target with `get_<d>(id, raw=True, language=L)`:
  - not-found error: the variant does not exist, so **create** it with
    `create_<d>(content, language=L, id=<id>)`. The EN source must exist
    (otherwise the domain's not-found error names the missing EN source).
    The new variant starts with the domain's create status (`draft`; `open`
    for `rsk`) and fresh `created`/`updated`, independent of the EN status.
  - a document: the variant exists, so **update** it: whole-body
    `update(type, id, content, language=L)` for a full re-translation, or
    `edit(type, id, old_str, new_str, language=L)` for a small change.
    `old_str` must match the variant's on-disk text byte for byte, and is
    matched against the **translated** headings and prose as stored.
  - a `ParseFailureResult` (`error`/`path`/`id`): the variant exists but
    fails to parse; stop and report.
- An existing variant is never overwritten by `create_<d>` (`FileExistsError`).

## 8. Guard and error semantics

- `language` not of shape `^[a-z]{2}$`: `ValueError`, before any filesystem
  access.
- `language` of valid shape without a heading table: `ValueError`
  ("no heading-mapping table for language ..."); add
  `general/data/headings/<language>.json` first.
- Non-default `language` for `feat` or `adr`: `ValueError` ("always English").
- `create_<d>`: EN requires `id` to be omitted; a non-default language
  requires `id` (the shared EN id; a missing or misused `id` is a
  `ValueError`); a missing EN source is the domain's not-found error; an
  existing variant is `FileExistsError`.
- A body that fails validation (a closed-vocabulary token translated, a
  heading that is neither canonical nor in the table, a broken structure) is
  a **non-raising** `ValidateResult` (`valid=False`, one `errors[].message`
  with the field path, 1-based line, and cause). Nothing is written.
- `update`/`edit` on a truly-absent variant raise the domain's not-found
  error even when the EN document exists; an existing but broken variant
  returns a `ParseFailureResult`.
- `get_<d>(raw=True)` of a variant that fails to parse returns the
  `ParseFailureResult`, never raw text.
