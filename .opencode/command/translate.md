---
description: Translate a specmgr document into another language (or update its translation) -- $1 is the domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt; feat and adr are always English), $2 the document id, $3 the target language, optional $4 the source language (default en).
---

Translate a specmgr document. My input:

- `$1` (required): the document's domain -- one of `req`/`uc`/`tsk`/`qa`/
  `prb`/`gol`/`rsk`/`dec`/`sop`/`vcr`/`sysrs`/`txt`. `feat` and `adr` are always
  English and out of scope.
- `$2` (required): the artifact's shared id (a lowercase-hex uuid; the EN
  source's id, which every language variant reuses).
- `$3` (required): the target language, a lowercase two-letter code (for
  example `de`) that has a heading table. `en` is never a target.
- `$4` (optional): the source language; defaults to `en`.

1. If `$1`, `$2`, or `$3` is missing or malformed, or `$1` is `feat`/`adr`,
   ask me for a clean input with the `question` tool rather than guessing.
2. Run the `translate_artifact` MCP prompt flow for `$1 $2 $3 [$4]` exactly
   as narrated: read `specmgr://i18n` first, build the `TodoWrite` plan, read
   the source via `get_<d>` with `raw=True` (a `ParseFailureResult` stops the
   flow), probe the target variant to choose create or update, read the
   heading table via `specmgr://i18n/headings/<language>`, translate prose and fixed heading text only (never the
   closed-vocabulary or schema-constant tokens, nor `prb`'s
   `problem_statement`), write with bounded retries on a non-raising
   `ValidateResult`, and verify with `get_<d>` on the written variant.
3. Report per the flow's step 9: the document's type and id, the languages,
   whether you created or updated the variant, the written path, the write
   attempts and any `ValidateResult` message you fixed, every `question` you
   asked and its answer, and anything left untranslated on purpose. Do not
   commit, do not write the English document, and do not touch any other
   file.
