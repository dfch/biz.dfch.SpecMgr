---
status: accepted
date: '2026-09-22'
decision-makers: OpenCode agent + user decision
id: c4efbde6-fd19-4aa8-8668-95316ed62dcc
version: 1.0.0
---

# Single source of truth for the document-type domain-name set

## Context and Problem Statement

At least 23 places across `src/` and `tests/` independently hand-maintain a literal tuple/list/frozenset/`Literal[...]`/dict-key-set of the document-type domain names -- the whole-body domains `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`, optionally plus `adr` -- and none of them derived from a shared constant. Confirmed drift already observed: `tests/general/tools/test__path_safety.py`'s `_UUID_DOMAINS` was missing `sysrs` while `src/biz/dfch/specmgr/general/tools/_path_safety.py`'s own `_UUID_TYPES` included it, so the `assert_uuid` test loop silently never exercised the `sysrs` domain; `general/tools/delete.py`'s `_DELETE_TYPES` and `general/tools/validate.py`'s `_VALIDATE_TYPES` were dead code duplicating each file's own live `_ADAPTERS` dict and `Literal[...]` signature; two doc-cache test files each hand-listed a byte-identical duplicate of the non-`feat` domain set; and each of the generic tools' `_ADAPTERS` dict-key list and `Literal[...]` signature was hand-maintained independently, with inconsistent ordering between the two even within the same file (`feat` before `sop` in the `update`/`set_status`/`set_classification` dicts, after everywhere else). Two further instances of the same drift vector in miniature: the local `_TYPE_ADR = "adr"` singleton in `set_status.py` (6 use sites) and the local `_TYPE_FEAT = "feat"` singleton in `_path_safety.py` (2 use sites).

This is the "phase 2" of the same root problem feat-122-docstring-comments fixed in prose -- no single source of truth for "which domains exist" -- but here the drift manifests in code (type hints, dispatch tables, test coverage), not just prose. GitHub issue #125.

## Decision Drivers

- One registration point for a new domain: the domain name is written exactly once, in one shared source, and every other site derives from it -- a new domain should never again touch ~5-6 independent hand-copies.
- No more enum/description/prose drift: the generic tools' MCP-registered `type` enums, their decorator descriptions, and their runtime error messages all derive from the same source, so a future domain addition touches no prose copy.
- Zero behavior change: a pure refactor -- no tools added/removed/renamed, no new error paths, no change to id resolution/lock/cache/dispatch semantics.
- Fail loudly at import time on future drift: the existing natural dispatch tables are guarded by module-level set-equality asserts (the repo's assert-for-invariants convention), so a future adapter add/remove that forgets the shared source -- or vice versa -- surfaces as an actionable import-time `AssertionError`, not a silent mismatch.

## Considered Options

1. A single shared `general/tools/_domains.py` module with `WHOLE_BODY_DOMAINS` as the only hand-listed tuple and everything else derived from it; the generic tools' public `type` signatures re-derived via PEP 692 unpacking (`Literal[*WHOLE_BODY_DOMAINS]`/`Literal[*ALL_DOMAINS]`); the `_ADAPTERS` dispatch tables and `set_status`'s `_ALLOWED_STATUSES_BY_TYPE` reordered to the canonical key order and guarded by module-level set-equality asserts; the decorator descriptions and the two runtime error messages derived from the shared source. Chosen.
2. No shared source: keep the hand-listed copies (status quo).
3. Derive everything, including the `_ADAPTERS` dispatch tables, via comprehensions over the shared source (no separate key list to guard at all).
4. Put the shared constants in the models layer (`models/`) instead of the tools layer.

## Decision Outcome

Option 1: `src/biz/dfch/specmgr/general/tools/_domains.py` is the single source of truth for the document-type domain names. `WHOLE_BODY_DOMAINS` is the only hand-listed tuple in the module -- the whole-body domains in the canonical order `req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, `sysrs` (AGENTS.md's bullet order, already the dominant ordering in the repo) -- and every other artifact is computed from it, never hand-listed a second time: `WHOLE_BODY_NO_FEAT_DOMAINS` (the whole-body domains without `feat`), `UUID_DOMAINS` (those plus `adr`), `ALL_DOMAINS` (`adr` prefixed to the whole-body domains), and the `ADR`/`FEAT` name singletons. The generic tools' public `type` signatures are PEP 692 unpackings -- `update`/`set_classification`/`delete`/`validate` annotate `Literal[*WHOLE_BODY_DOMAINS]`, `set_status` annotates `Literal[*ALL_DOMAINS]` -- so every MCP-registered `type` enum is set-equal to the pre-feature one; only `set_status`'s enum value ordering changes, with `adr` moving to the front (JSON-schema enum ordering is non-normative, no test pins it, and `adr` is slated for deprecation anyway). Each `_ADAPTERS` table is reordered to the canonical key order (fixing the `feat`-before-`sop` deviation) and carries a module-level `assert set(_ADAPTERS) == set(<shared tuple>)` with an actionable message naming the shared source and the fix; the same assert covers `set_status`'s `_ALLOWED_STATUSES_BY_TYPE` and `general/resources/config.py`'s `config_info()` `domains` dict (against `ALL_DOMAINS`, insertion order unchanged: `adr` first). The decorator descriptions of the generic tools and the `specmgr://config` resource, plus the two runtime error messages (`_path_safety.validate_id`'s unknown-type message and `validate`'s unsupported-type message -- neither pinned by any test), are f-string-derived via `", ".join(...)` from the shared source. The dead `_DELETE_TYPES`/`_VALIDATE_TYPES` constants are removed, and every test-side hand-listed domain set imports the shared name instead. This ADR refines ADR 36905d5b-8057-4294-8665-c7eed5534db0's future-domain convention without superseding it: a new domain now also registers its name in `general/tools/_domains.py`'s `WHOLE_BODY_DOMAINS` (in canonical position) in addition to the existing dispatch entries.

### Consequences

- Good: a new domain registers its name once, in `WHOLE_BODY_DOMAINS`, and every derived tuple, public signature, registered enum, description, error message, and dispatch-table guard picks it up by construction -- the ~5-6 independent hand-copies a future domain addition used to require are gone.
- Good: future drift between any dispatch table and the shared source fails loudly at import time (actionable `AssertionError`), instead of as a silently inconsistent tool description, a missing enum value, or a dead duplicate constant.
- Good: the confirmed `sysrs` test-coverage gap in `test__path_safety.py`'s `assert_uuid` loop is closed by construction -- the loop iterates the shared `UUID_DOMAINS`.
- Bad/neutral (accepted): the PEP 692 annotation renders as the raw `Literal[*WHOLE_BODY_DOMAINS]` text in the `docs/api` signature headings rather than an expanded value list; `set_status`'s registered enum reorders `adr` to the front, visible in the MCP tool list and in `docs/MCP.md`; and the two derived error messages change the separator between domain names from `/` to `, `.
- Explicitly ruled as staying hand-maintained (the feat-125 sweep classification): `server.py`'s `from . import adr, dec, feat, ...` line (Python import statements cannot be built from a runtime list) and the function docstrings' prose domain lists (the `specmgr docs` generator requires string literals, and the feat-122 Docstring Style rule sanctions explicit prose lists). The remaining hand-listed `tests/` sites are likewise explicitly kept: the per-domain `_Case`/`_InjectionCase` dataclass rows are per-domain fixture data, not sets; `test_mcp_docs.py`'s enum value is a render fixture, not a domain list; and the inline single-domain comparisons are single-name, not set-level.

### Confirmation

- The full test suite passes on the pinned stack (3365 passed), including the registration tests whose expected `type` enums now derive from `list(WHOLE_BODY_DOMAINS)` instead of hand-typed literals -- they are the plan's drift canaries.
- The import-time guards were verified by temporarily breaking one side during development: dropping an `_ADAPTERS` entry failed the module import with the actionable `AssertionError` naming the shared `general.tools._domains` source and the fix, and was restored to a clean re-import.
- `specmgr docs`, `specmgr mcp-docs`, `specmgr schema`, and `specmgr adr-toc` all regenerate with zero residual diff.

## Pros and Cons of the Options

### Option 1: The shared _domains.py module with everything derived

Good: a single registration point for a new domain (one name in one tuple, in canonical position); the public enums, descriptions, and error messages can no longer drift from the dispatch tables, which are themselves guarded at import time by set-equality asserts; zero behavior change (every registered enum stays set-equal to today's); the `sysrs` test-coverage gap is closed by construction; every domain-name artifact in the repo shares one canonical ordering.

Bad: the PEP 692 annotation renders as raw source text (`Literal[*WHOLE_BODY_DOMAINS]`) in the `docs/api` signature headings rather than an expanded value list; `set_status`'s registered enum visibly reorders (`adr` to the front), a harmless but real change to the emitted schema; and adding a domain now has one extra step (the `_domains.py` registration) on top of ADR 36905d5b's existing dispatch entries.

### Option 2: No shared source, keep the hand-listed copies

Good: no new module, no new registration step, no visible enum reorder, zero diff.

Bad: the drift vector is already demonstrated in the tree -- the missing `sysrs` test coverage, the dead duplicate constants, the byte-identical duplicate list, the inconsistent key ordering, and the two miniature singletons; every future domain addition touches ~5-6 independent hand-copies again, and the same silent test-coverage gap would recur. Rejected.

### Option 3: Derive the dispatch tables via comprehensions over the shared source

Good: maximal derivation -- no second hand-maintained key list anywhere in the tool files, so there is nothing to guard with an assert.

Bad: the per-domain adapter function values must be enumerated anyway (a comprehension re-derives the keys, not the values), so the dispatch tables lose their readability as natural maps of domain to adapter; and the repo's assert-for-invariants convention prefers a natural table tied to the shared source by an explicit, actionable assert over a derived construction. Rejected.

### Option 4: A models-layer location for the constants

Good: `models/` is the shared top-level package, so importing the constants would be short and stable from any domain.

Bad: the domain names are a tool-layer concern (the `type` dispatch of the generic tools and `_path_safety`'s id-format dispatch); the models layer carries no domain-name vocabulary today, and `general/resources/config.py` already imports from `general/tools`, so the dependency direction is established. Rejected.

## More Information

- GitHub issue #125 ("Consolidate the ~23 independently hand-maintained domain-list constants into a shared source of truth").
- Feature plan and progress: `.specmgr/feat/feat-125-domain-lists/README.md`.
- ADR 36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and status-change tools into generic type-dispatched tools"): the dispatch-only convention this ADR refines (not supersedes) -- a new domain now also registers its name in `general/tools/_domains.py` in addition to the existing dispatch entries.
- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d ("Replace domain-specific delete tools with a generic type-dispatched delete tool"): the path-safety guards whose `_UUID_TYPES` constant now derives from the shared source.
- feat-122-docstring-comments: the prose counterpart of this feature; its `.specmgr/conventions.md` Docstring Style rule sanctions the explicitly-kept docstring prose lists recorded in this ADR's Consequences, and this feature adds the companion "Domain-List Constants" rule for code constants.
