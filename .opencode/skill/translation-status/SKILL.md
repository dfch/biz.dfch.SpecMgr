---
name: translation-status
description: Use when checking which languages a specmgr document exists in or whether a translation is still in sync with its source -- e.g. "which languages exist for REQ ...", "list the translations of ...", "is the German translation of ... up to date", "check translation drift", "is the German version of this decision stale" (the read-only list_languages and check_translation_drift MCP tools) -- whether surfaced by an explicit /translation-status request or organically while working with specmgr documents and language variants. Whole-body domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt only; feat and adr are always English and out of scope.
---

# Translation Status

You are answering two read-only questions about the language variants of a
specmgr document (the same `id` in `docs/{type}/` for English and in
`docs/{type}/{language}/` for every other language): **which languages exist**
and **whether a translation has drifted from its source**. Both are
deterministic specmgr tools; you only call them and report what they return.

## How

1. **Which languages exist** — call `list_languages(type, id)`. It returns the
   language codes the artifact exists in (`en` first when the English source
   exists, then the others sorted by code) with one entry per language: the
   resolved `path`, `parseable`, and the parse `error` of a variant that exists
   but fails to parse. `en` is never invented: an id with variants but no
   English source lists no `en`. An id that exists in no language raises the
   domain's not-found error.
2. **Is a translation in sync** — call `check_translation_drift(type, id,
   language, source_language="en")`. One run reports both drift kinds in a
   single non-raising result: `structural` (each `missing`, `extra` or
   `reordered` section of the variant against the source's canonical schema,
   or an `unparseable` finding carrying the parse error) and staleness
   (`stale` is true when the source's `updated` timestamp is strictly newer
   than the variant's, with both timestamps and `source_ahead_by_seconds`).
   `in_sync` is true only when there is no structural finding, the variant is
   not stale, and the timestamps could be compared. Prose, wording, frontmatter
   values, and `prb`'s English `problem_statement` are never compared.
3. **Report** the findings as returned (language list, structural findings with
   their heading and positions, the staleness verdict). If drift is found,
   suggest the `/translate` command (the `translate-artifact` skill) to bring
   the variant up to date.

## Boundaries

- No tool translates: translating or updating a variant is the
  `translate-artifact` skill and the `translate_artifact` prompt, not this
  skill. This skill never edits, writes, or commits anything.
- `feat` and `adr` are always English — they have no language variants and the
  two tools reject them with an explanatory error. `en` is never a drift
  `language` (it is the canonical source form).
- A language without a heading table (`general/data/headings/<language>.json`)
  is unusable; report the tool's error as is.
- Ask the user (via your host's question mechanism) rather than guessing when
  the type, id, or language is missing or ambiguous.
