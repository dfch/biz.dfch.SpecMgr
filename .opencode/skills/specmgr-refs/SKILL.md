---
name: specmgr-refs
description: Use when resolving or retrieving specmgr cross-references -- single-document requests ("what does document X reference", "list the references of X"), reference-graph requests ("show me the reference graph"), batch-resolution requests ("do all cross-references resolve"), and reverse-lookup requests ("which documents reference X") -- by routing single-document retrieval to the `list_references` MCP tool (or the `ref-finder` subagent / `/refs` command) and following the codified graph, batch, and reverse workflows.
---

# SpecMgr Cross-Reference Router

You are a router over the specmgr cross-reference retrieval stack
(feat-144-ref-artifact): the `list_references` MCP tool, the read-only
`ref-finder` subagent (`.opencode/agent/ref-finder.md`), and the `/refs`
command (`.opencode/command/refs.md`). Single-document reference retrieval
already has a home there -- you point to it, you never re-implement it. What
you codify are the three compositions that have nowhere else: multi-hop
graph traversal, batch resolution validation, and reverse lookup.

You are read-only: you never edit, write, create, or delete any document,
and you never commit. Your only actions of consequence are calling
`list_references` and the paged `list_<d>` scans the batch and reverse
workflows need.

## Route by task shape

| Task shape | Example phrasing | Path |
| --- | --- | --- |
| Single document | "what does document X reference?" / "list the references of X" | Delegate -- the pointer, below |
| Multi-hop graph | "show me the reference graph, two levels deep" | The graph workflow, below |
| Batch validation | "do all cross-references resolve?" | The batch workflow, below |
| Reverse lookup | "which documents reference REQ `<uuid>`?" | The reverse workflow, below |

If the task does not name a specmgr `<type> <id>` pair (or a registry-wide
request), ask for one rather than guessing.

## Single-document: delegate, do not re-tell

A single-document request ("what does `<type> <id>` reference?") is a
pointer to the existing stack, never a copy of it:

- **Prefer delegation.** If the host can launch subagents (a `task` tool is
  available) and `ref-finder` is among them, delegate the `<type> <id>` pair
  to the `ref-finder` subagent; it owns the single-document workflow and
  reports its own rows.
- **The `/refs` command already routes to `ref-finder`.** If the user typed
  `/refs <type> <id>`, let it run.
- **Otherwise, call the tool directly:** `list_references(type, id)`,
  reported per the reporting conventions below.
- Do not re-tell `ref-finder`'s workflow in the skill or in the report --
  that narrative stays in `.opencode/agent/ref-finder.md`, and the two must
  not drift apart.

## Graph workflow (multi-hop traversal)

Use for "show me the reference graph of `<type> <id>`, N levels deep".

1. Parse the source `<type> <id>` pair and the requested depth N. If the
   user did not state a depth, use N = 2 and say so in the report.
2. Initialize the seen-set with the source's own `(type, id)` pair.
3. **Level 1**: call `list_references(type, id)` for the source and page to
   completion (while `truncated` is true, call again with a higher `offset`
   in steps of `max_results`).
4. **Level k+1**: expand only the level-k rows that resolved on disk -- a
   **NOT FOUND** row has no body to scan, and `list_references` raises for
   a missing source. For each resolvable row, call
   `list_references(row.type, row.id)` and page to completion. Add every
   row's `(type, id)` to the seen-set; a pair already seen at an earlier
   level is reported once, at the level it first appeared, and is never
   expanded again.
5. Stop at level N, or early when a level yields no new `(type, id)` pair.
6. **Report** one table per level -- columns Level, `type`, `id`, `title`,
   `path` -- with **NOT FOUND** prefixed to every row whose `error` is set
   (its `title`/`path` are null), stating each level's `total` and
   `error_count`, plus an overall summary: depth reached, unique documents
   seen, total references, total errors.

In the compositions below (graph, batch, reverse), page every
`list_references` and `list_<d>` call to completion: the interactive
"report the first page and offer to continue" default of the single-document
path does not apply, because a partial level or a partial registry breaks
dedup, traversal, and aggregation.

## Batch workflow (resolution validation)

Use for "do all cross-references across the registry resolve on disk?".

1. **Iterate the 12 whole-body domains in canonical order:**
   req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs. The `adr` exclusion is
   deliberate and must not be "fixed": `list_references`'s source enum
   accepts `adr` and ADR documents can carry outbound references, but `adr`
   is slated for removal (GitHub issue #46) and this workflow targets the
   whole-body registry.
2. **Per domain,** page `list_<d>` to completion (while `truncated`, a
   higher `offset`). A row whose `id` is null (a `<failed to parse>` row)
   cannot be scanned -- `list_references` needs a source id -- so count it
   in a separate per-domain `parse_failures` tally, listing the row's
   `path` and `error`; it is not a reference row.
3. **Per scannable document,** call `list_references(<domain>, id)` and
   page to completion. Aggregate per domain: documents scanned, `total` (the
   sum of each document's own `total`), `error_count` (the sum of each
   document's own `error_count`), and every **NOT FOUND** row.
4. **Report** one table per domain (columns: domain, documents scanned,
   `parse_failures`, `total`, `error_count`), then one overall table with
   the same columns summed, and list every unresolvable reference with its
   source document (the referencing `type`/`id`/`title`/`path`) and the
   **NOT FOUND** row (the referenced `type`/`id` and `error`). A registry
   where every reference resolves is the report: overall `error_count` 0
   and no **NOT FOUND** rows.

## Reverse workflow ("which documents reference X?")

Use for "which documents reference REQ `<uuid>`?" -- any target `<type>
<id>` pair, including `feat feat-NNN-slug`.

1. **Parse the target** `<type> <id>` pair.
2. **State the cost before running:** this is an O(registry-size) scan --
   every candidate document's body must be read, because the
   `list_references` extractor regex-scans every body for the 11-tag
   reference vocabulary (GOL/PRB/QA/UC/REQ/RSK/DEC/ADR/VCR/SYSRS/FEAT;
   case-insensitive tag, space/tab/dash separator, anywhere in a line). No
   domain can be pre-filtered by the target's type and no document can be
   skipped; do not "optimize" the scan by dropping domains.
3. **Scan:** for each of the 12 whole-body domains (req/uc/tsk/qa/prb/gol/
   rsk/dec/sop/feat/vcr/sysrs -- the same deliberate `adr` exclusion as the
   batch workflow), page `list_<d>` to completion and, for every scannable
   document (null-id `<failed to parse>` rows are counted as
   `parse_failures`, not scanned), call `list_references(<domain>, id)` and
   page to completion.
4. **Match:** a document is a hit when one of its rows matches the target on
   `(type, id)` -- the target type case-insensitively, and the target id
   exactly -- except that a `feat` target given as the full `feat-NNN-slug`
   also matches a row carrying the target's bare `feat-NNN` number prefix,
   since a feature can be referenced by either spelling and the row's `id`
   stays the spelling as it appeared in the referencing body.
5. **Report** one row per hit, naming the referencing document's
   `type`/`id`/`title`/`path` (from the domain's own `list_<d>` row) plus
   the number of matching reference rows in it. A document with no matching
   row is not a hit and is not listed. If the target document itself is a
   hit (a self-reference), report it like any other hit and mark it as one.

## Reporting conventions (every workflow)

Every report you produce -- including the direct single-document call --
uses the `ref-finder` vocabulary, verbatim:

- One row per reference: `type`, `id`, `title`, `path`.
- A row whose `error` is set (the referenced document was not found on
  disk; its `title`/`path` are null) is prefixed with **NOT FOUND**.
- State the `total` reference count and the `error_count` for every
  `list_references` result you rely on, and `truncated` whenever a result
  page was not consumed to completion.
- Report a tool error (a `ValueError` for a bad `type`/`id`, a domain
  not-found error for a missing source) verbatim and stop -- do not paper
  over it with an empty list.
- Retrieving references never modifies, creates, or deletes any document.
