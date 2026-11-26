---
name: specmgr-set
description: Use when bundling or grouping specmgr artifacts together -- "bundle these artifacts", "group these documents", "make a set of ...", "put these documents together", "create a set for the review" -- by creating a `set` document (the specmgr convenience-bundle type) through the `create_set` prompt flow: a `list_set` near-duplicate check first, the mixed-tag `## Items` list, and the grouping rationale in `## Description`.
---

# SpecMgr Set Bundling

You bundle already-existing specmgr artifacts into a `set` document
(feat-173-req-iso29148-level-set, Phase 180). A set is a
convenience bundle: it lists its items by forward reference so a
review, a release, or a workstream can be navigated from one place.

## The invariants (carried by the schema and the prompts)

- **The items remain the source of truth.** A set duplicates nothing --
  each `## Items` bullet is a reference (`<TAG> <uuid>: <title>`) to an
  artifact that owns its own content.
- **Forward references only.** Nothing in an item ever points back to the
  set: `SET` is not a tag of the shared reference vocabulary. Never add a
  back-reference into a bundled artifact while working on a set.
- **Mixed types allowed.** Any of the 11 reference tags (`GOL`, `PRB`,
  `QA`, `UC`, `REQ`, `RSK`, `DEC`, `VCR`, `SYSRS`, `TXT`, `FEAT`)
  may appear in any mix in one `## Items` list; `FEAT` bullets carry a
  `feat-NNN-slug` or bare `feat-NNN` id instead of a uuid. The same
  `(tag, id)` pair appears at most once (a duplicate is rejected).
- **The shape is fixed.** H1 -> `## Description` (mandatory, opaque free
  markdown) -> `## Items` (mandatory flat bullet list, at least one
  bullet, optional per-bullet notes paragraph). No other sections: no
  `## Owner`, no `## Source`, no `## Tags`, no `## More Information`.
- **You never commit**, and you never edit a bundled artifact from this
  skill (those go through their own domains' tools/prompts).

## The workflow

1. **Near-duplicate check first**: call `list_set` and look for an existing
   set on the same topic or with an overlapping item list. If one exists,
   use the `question` tool to ask whether to extend/revise that one (via
   the `update_set` prompt) instead of creating a duplicate.
2. **Gather the items**: take each artifact's reference id from the user or
   from the domain's own `list_<d>` tool (e.g. `list_req`), and use the
   referenced document's own H1 as the bullet's `<title>`. Use the
   `question` tool whenever an id or a grouping is ambiguous -- do not
   guess.
3. **Run the `create_set` prompt flow** (the narrated authoring flow): it
   describes the grouping in `## Description` (why these items belong
   together) and drives `create_set(content)` with the assembled body.
4. **Report**: the created set's id, title, and item list; and -- if the
   bundle is meant for a named review or release -- note that the set's
   own `status` lifecycle is `draft`/`progress`/`done`/`review` (change it
   through the generic `set_status` tool with `type="set"`, only when
   asked).
