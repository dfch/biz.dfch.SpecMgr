---
description: Repair a specmgr document that fails to parse -- $1 is the domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; ADR is out of scope), optional $2 is the document id.
agent: doc-repairer
---

Repair a failing specmgr document. My input:

- `$1` (required): the document's domain -- one of the whole-body domains
  `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`.
  ADR is out of scope: `validate_adr` re-reads the ADR from disk by id and
  the repair loop is not defined for it.
- `$2` (optional): the failing document's id (a lowercase-hex uuid, or a
  `feat-NNN-slug` for `feat`). When absent, discover the failing document
  via `list_<type>()`'s `<failed to parse>` row instead.

1. Parse the pair from my input. If `$1` is missing or is not one of the
   whole-body domains above (or is `adr`), or if `$2` is present but
   malformed for its domain, ask me for a clean pair with the `question`
   tool rather than guessing.
2. Apply your own workflow (discover, raw read, fix only what the error
   addresses, loop `validate` with `full=True`, raw write-back, post-write
   confirmation) to this `<type> [id]` pair.
3. Report the document's `path`, the original error, the fix you applied,
   and the post-write confirmation outcome -- the repair counts as done
   only once `get_<type>(id)` (or `list_<type>()` again) parses the file
   as it now exists on disk. Do not commit, and do not touch any other
   file.
