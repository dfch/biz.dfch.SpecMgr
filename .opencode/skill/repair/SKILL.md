---
name: repair
description: >-
  Use when you encounter a specmgr document that fails to parse -- a
  `list_<d>` row whose `title`/`status` carry the `<failed to parse>`
  marker (null `id`, populated `ref`/`path`/`error`), or a `get_<d>` call
  that fails with the domain's not-found error wrapping an enriched parse
  error (field path, 1-based line, cause/fix hint) -- whether surfaced by
  an explicit `/repair` request or organically while you are working with
  specmgr documents mid-task. Whole-body domains only (req/uc/tsk/qa/prb/
  gol/rsk/dec/sop/feat/vcr/sysrs); ADR is out of scope.
---

# Repair

A specmgr whole-body document currently fails to parse, and you have
stumbled onto it -- explicitly (via `/repair`) or organically (a
`<failed to parse>` row in a `list_<d>` result, or a wrapped parse error
from a `get_<d>` call). Do not let the failure propagate: repair it, or
report it clearly.

## How

- **Prefer delegation.** If your host can launch subagents (a `task` tool
  is available) and the `doc-repairer` agent is among them, delegate to
  `doc-repairer` with the `<type> [id]` pair. It runs the full loop with
  real file access and reports the post-write confirmation outcome.
- **Otherwise, run the condensed loop yourself** (the same workflow the
  specmgr `repair` MCP prompt narrates):
  1. **Discover**: with an id, `get_<type>(id)` -- read the wrapped
     enriched parse error; without, `list_<type>()` -- find the failed row
     (`<failed to parse>` marker in `title`/`status`, null `id`,
     populated `path`/`error`).
  2. **Raw read**: read the complete file at the row's `path` with your
     own host file-read tool. No specmgr MCP tool can return the raw
     content of a document that fails to parse, and the generic `update`
     tool cannot repair it (its adapters re-parse first and convert the
     failure into the domain's not-found error).
  3. **Fix minimally**: only what the enriched error names (field path,
     1-based line, cause/fix hint). Preserve the frontmatter
     `id`/`created`/`status`/`version` byte-for-byte; leave `updated`
     untouched -- a repair is not an edit.
  4. **Validate loop**: `validate(type="<type>", content=<full raw text>, full=True)` until `valid: true`.
  5. **Write back**: the green text to the same `path` via your own host
     file-write tool -- never via `update`.
  6. **Confirm on disk**: `get_<type>(id)` again (or `list_<type>()`
     again -- the row's marker and `error` must be gone). Only a real
     parse of the real file counts as success.
  7. **Diagnose-only**: if your host has no file read/write tools, do not
     touch the file -- report the error, the fix you would apply, and the
     `path`, then stop.

Ask the user (via your host's question mechanism) rather than guessing
whenever the error does not pin down a unique fix, or when more than one
row is failing and no id was given. Never commit as part of a repair.
