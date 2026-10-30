---
name: translate-artifact
description: Use when translating a specmgr document into another language or bringing an existing translation up to date -- e.g. "translate this requirement into German", "create a German version of REQ ...", "update the French translation of ..." (the translate_artifact prompt flow -- read the specmgr://i18n guidance, read the source, create or update the language variant, never translate closed-vocabulary tokens) -- whether surfaced by an explicit /translate request or organically while working with specmgr documents and language variants. Whole-body domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs only; feat and adr are always English and out of scope.
---

# Translate Artifact

You are producing, or updating, a language variant of a specmgr document: the
same `id`, the same schema, only the prose (and the fixed-text heading text,
through the language's heading table) differs. Variants live under
`docs/{type}/{language}/` with the EN source's exact file name. Translating is
your judgment work around deterministic specmgr tools; no specmgr tool
translates for you.

## How

1. **Read the guidance first**: `specmgr://i18n` — the directory layout and
   basename rule, the language vocabulary and heading tables, the exact
   never-translate list per domain (closed-vocabulary and schema-constant
   tokens, and `prb`'s `problem_statement`, which stays English), the
   create-versus-update decision, and the guard/error semantics. Do not
   proceed on memory of it; where anything below and the resource differ,
   the resource wins.
2. **Run the `translate_artifact` MCP prompt** for the `<type> <id>
   <language> [source_language]` — the narrated flow: `TodoWrite` plan,
   `get_<d>(id, raw=True, language=...)` for the source (a
   `ParseFailureResult` stops the flow), the create-versus-update probe of the
   target variant, the heading table (read through the
   `specmgr://i18n/headings/{language}` resource template, no host file tool
   needed), the translation (prose and fixed
   heading text only, never the closed-vocabulary tokens), the write with
   bounded retries on a non-raising `ValidateResult` (the generic `validate`
   tool cannot dry-run a translation), verification with
   `get_<d>(id, language=...)`, and the report. This is the only sanctioned
   path for a translation.
3. **Out of scope**: `feat` and `adr` are always English — they have no
   language variants and no `language` parameter. A language without a
   heading table (`general/data/headings/<language>.json`) is unusable: stop
   and report that the table must be added first; never invent one.

Ask the user (via your host's question mechanism) rather than guessing
whenever the source is ambiguous or a token's translatability is unclear.
Never translate a closed-vocabulary or schema-constant token. Never commit as
part of a translation flow.
