---
description: Show which languages a specmgr document exists in and, for a given language, whether that translation has drifted from its source -- $1 is the domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt; feat and adr are always English), $2 the document id, optional $3 the language to check.
---

Show the translation status of a specmgr document. My input:

- `$1` (required): the document's domain -- one of `req`/`uc`/`tsk`/`qa`/
  `prb`/`gol`/`rsk`/`dec`/`sop`/`vcr`/`sysrs`/`txt`. `feat` and `adr` are always
  English and out of scope.
- `$2` (required): the artifact's shared id (a lowercase-hex uuid; every
  language variant reuses it).
- `$3` (optional): the language to check for drift, a lowercase two-letter code
  that has a heading table (for example `de`). `en` is never checked (it is
  the canonical source).

1. If `$1` or `$2` is missing or malformed, or `$1` is `feat`/`adr`, ask me for
   a clean input with the `question` tool rather than guessing.
2. Call `list_languages($1, $2)` and report the languages found (`en` first
   when the English source exists), each with its `path` and `parseable`
   flag, flagging any variant that fails to parse together with its `error`.
3. If `$3` is given, call `check_translation_drift($1, $2, $3)` and report both
   drift kinds from the one result: every structural finding (`missing`,
   `extra`, `reordered`, `unparseable`, with the canonical `heading`, `path`,
   and positions), whether the translation is `stale` (both `updated`
   timestamps and `source_ahead_by_seconds`), the `staleness_error` if the
   timestamps could not be compared, and the overall `in_sync` verdict.
4. If drift is found, suggest `/translate $1 $2 $3` to bring the translation
   up to date. Do not translate, edit, write, or commit anything yourself --
   this command only reads and reports.
