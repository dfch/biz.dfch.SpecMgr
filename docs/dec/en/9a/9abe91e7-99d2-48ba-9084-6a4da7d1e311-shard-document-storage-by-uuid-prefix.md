---
classification: null
created: '2026-11-23T02:50:15.039+01:00'
id: 9abe91e7-99d2-48ba-9084-6a4da7d1e311
status: accepted
type: dec
updated: '2026-11-23T02:50:15.208+01:00'
version: 1.0.0
---

# Shard document storage by uuid prefix

## Context and Problem Statement

The thirteen UUID whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `vcr`, `sysrs`, `txt`, `set`) stored every document flat in one per-type directory (`docs/<type>/<type>-<uuid>-<slug>.md`, language variants in `docs/<type>/<language>/`). A flat per-type directory bounds nothing as the corpus grows: a cold per-id resolution parses every file of the domain before it can rule the target out (the same cold-scan class `feat-187-list-feat-timeout` fixed for `list_feat`), and directory-level operations (git, glob, OS listings) degrade with the file count. GitHub issue #245, tracked as FEAT feat-245-shard-docs, settles the layout change.

## Decision Drivers

- Cold per-id scans must be bounded (from O(N-domain) parses to O(N/256)).
- Directory-level operations must stay fast for arbitrarily large corpora.
- The language-variant convention (DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772) must keep one unambiguous path per (type, language, id) without depth- or table-based disambiguation.
- The `specmgr-lint` gate (feat-218) must fail loudly on a misplaced document, since a misplaced document is invisible to every MCP read tool.

## Considered Options

- Keep the flat per-type layout (status quo; no bound on scan or directory cost).
- Shard by the first two hex digits of the document uuid into `docs/<type>/<lang>/<id[:2]>/<uuid>-<slug>.md`, one uniform layout for every language including EN, shard-only reads (hard cut-over), the lint layout-violation gate, and a one-off in-repo migration (chosen).

## Decision Outcome

We shard all thirteen UUID whole-body domains -- `feat` (folder-per-document, non-uuid ids) stays excluded -- into `docs/<type>/<lang>/<id[:2]>/<uuid>-<slug>.md`: 256 shard subdirectories named by the first two hex digits of the document's uuid, one uniform layout for every language including EN (retiring DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772 item 1's flat-EN special case), prefix-less file names (extending DEC's existing `<uuid>-<slug>.md` convention to the other twelve sharded domains), shard-only reads as a hard cut-over, the `specmgr-lint` layout-violation gate (exit 2 naming the correct path), and a one-off in-repo migration of the 76 existing documents into `en/<shard>/` in the same change.

### Consequences

- Bad (BREAKING): downstream users with pre-existing flat trees find their documents invisible to every MCP read path until moved under `<lang>/<shard>/` (accepted; no dual-layout compatibility, no migration CLI).
- Bad (churn): `ref` values change from `<type>-<uuid>-<slug>` to `<uuid>-<slug>`, and file names lose the `<type>-` prefix in the twelve non-DEC domains (documentation churn only: `ref` stays opaque and is never an input to `get_<d>`).
- Bad: English moves from `docs/<type>/` into `docs/<type>/en/`; the flat-EN location is retired.
- Good: cold per-id resolution drops from O(N-domain) to O(N/256) parses per language; directory-level operations stay bounded at ~N/256 files per shard.
- Good: a two-hex shard cannot collide with a domain name (every two-character domain name contains a non-hex letter), and the shard/language collision is structurally impossible -- languages and shards sit at different path levels, so no directory ever plays two roles and no disambiguation heuristic exists.

### Confirmation

Confirmed by the feature's acceptance criteria and the full test suite in FEAT feat-245-shard-docs (create placement for all thirteen domains, shard-only visibility, wrong-shard fallback resolution, the four lint violation shapes, the migrated in-repo corpus linting clean, and the uniform-layout i18n round-trip), and by `specmgr lint --all` over the migrated tree.

## Roles and Responsibilities

### Accountable

Ronald Rink (d-fens GmbH) -- owner of the specmgr codebase and of this decision.

### Responsible

- The feat-245-shard-docs implementation phases (layout core, write path, lint gate, test sweep, migration, docs).

## Source

GitHub issue #245 (https://github.com/dfch/biz.dfch.SpecMgr/issues/245), tracked as FEAT feat-245-shard-docs (`.specmgr/feat/feat-245-shard-docs/README.md`).

## Related Artifacts

### Decisions

- DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772: Multi-language artifact variants: directory layout, heading-mapping table, and language vocabulary
