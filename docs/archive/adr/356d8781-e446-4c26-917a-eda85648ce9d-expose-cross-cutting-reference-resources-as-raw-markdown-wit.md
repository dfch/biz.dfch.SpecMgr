---
status: accepted
decision-makers: dfch
id: 356d8781-e446-4c26-917a-eda85648ce9d
version: 1.0.0
---

# Expose cross-cutting reference resources as raw markdown with model-backed drift-guard tests, not structured JSON

## Context and Problem Statement

SpecMgr exposes several cross-cutting, domain-knowledge reference resources over MCP (`specmgr://iso25010`, `specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`, `specmgr://rasci`, and a new `specmgr://ears` being added by feature feat-92-resources). Every one of these resources exists purely to give an LLM domain knowledge via an MCP prompt instruction: an LLM reads the resource's content as prose, directly, while following a `create_*`/`update_*` prompt. None of them is consumed by programmatic code that indexes into a parsed structure. Despite this uniform consumption pattern, the five existing resources follow two different, inconsistent conventions for guarding against content drift (a resource's packaged markdown file silently diverging from the structure a prompt/model assumes it has): `specmgr://iso25010` returns a structured `Iso25010` JSON object built from a dedicated Pydantic model that is parsed on every call, while `specmgr://dtais`, `specmgr://rsk/tara`, and `specmgr://rsk/risk-matrix` return raw markdown text, validated only by ad hoc regex assertions scattered inside each resource's own test file, with no dedicated model at all. Feature feat-92-resources needs to settle, once repo-wide, which single convention every reference resource -- present and future, including the new `specmgr://ears` -- should follow.

## Decision Drivers

- Every current consumer of these resources is an LLM reading prose via an MCP prompt instruction; none is programmatic code indexing into parsed JSON fields, so structured output provides no real benefit to any actual caller.
- Structured JSON output adds a serialization/schema-shape burden and a breaking-change surface on the MCP resource's own output contract, with no corresponding consumer benefit given the driver above.
- Drift protection is still required for correctness: a packaged markdown file can be hand-edited into an invalid/incomplete shape (e.g. a missing DTAIS method word, a renamed RASCI role) without any test noticing.
- Consistency: two different conventions spread across five near-identical resources makes it unclear what convention the sixth (`ears`) or any future reference resource should follow.
- Reuse of already-established precedent: `MarkdownListItem` subclasses with a `@computed_field` regex-extracting a leading keyword, the exact pattern already used by `feat.RequirementItem`/`tsk.TaskItem`, is a good fit for these resources' closed-vocabulary bullet lists without inventing a new shared `models/md` primitive.

## Considered Options

1. Uniform raw markdown: every reference resource returns raw markdown text (`mime_type="text/markdown"`), backed by a dedicated internal Pydantic model that is parsed on every resource call purely to fail fast on structural drift in production (the parsed result is discarded; the raw text is what's returned), and separately covered by its own dedicated `tests/models/test_*.py` drift-guard suite (not an ad hoc regex test living in the resource's own test file). This extends `iso25010`'s existing parse-and-discard timing to all resources, while dropping its structured-JSON output shape.
2. Uniform structured JSON: every reference resource returns a structured JSON object built from a dedicated model, extending `iso25010`'s current output shape to `dtais`/`tara`/`risk-matrix`/`rasci`/`ears` as well.
3. Uniform raw markdown with ad hoc regex tests: every reference resource returns raw markdown text, validated only by ad hoc regex assertions inside each resource's own test file, with no dedicated model -- extending `dtais`/`tara`/`risk-matrix`'s current status quo to `iso25010`/`rasci`/`ears`.

## Decision Outcome

Adopt Option 1. Every reference resource -- the four existing raw-markdown ones (`dtais`, `tara`, `risk-matrix`, and `rasci` once it gains a model), the one existing JSON one (`iso25010`, switched to markdown), and the new `ears` -- returns raw markdown (`mime_type="text/markdown"`) and is backed by a dedicated internal Pydantic model. That model is parsed on every resource call purely to fail fast on structural drift at request time, with the parsed result discarded and the original raw text returned unchanged to the caller; it is additionally covered by its own dedicated `tests/models/test_*.py` drift-guard suite, replacing the ad hoc regex-based drift checks that previously lived inside `dtais`/`tara`/`risk-matrix`'s own resource test files. Model placement follows the existing domain-first precedent: cross-cutting models (`dtais`, `rasci`, `ears`) live in `general/models/`, alongside `general/models/paged_result.py`/`summary.py`; RSK-owned models (`tara`, `risk_matrix`) live in `rsk/models/v1/`, alongside `Strategy`/`level_from_product`. Closed-vocabulary bullet lists (DTAIS method words, TARA strategy words, EARS template keywords) are modeled as `MarkdownListItem` subclasses with a `@computed_field` regex-extracting the leading keyword, reusing `feat.RequirementItem`/`tsk.TaskItem`'s precedent rather than inventing a new shared `models/md` primitive. The visual 5x5 risk matrix table is deliberately left unmodeled (only its accompanying 4-item "Product thresholds" list is parsed), accepting a small residual drift risk on the table itself rather than adding a general-purpose markdown-table-parsing primitive to `models/md` for a single, narrow use.

Why Option 1 wins: the audience for every one of these resources is an LLM reading prose via a prompt instruction, not programmatic code indexing into a parsed structure, so returning structured JSON (Option 2) buys nothing for any actual caller while still paying JSON's schema-shape/serialization cost -- and for `iso25010` specifically, its current JSON shape is itself a breaking-change surface with no consumer to protect. Dropping validation down to ad hoc, resource-test-local regex assertions (Option 3) is strictly worse than a dedicated model: it scales badly (each resource reinvents its own checks), gives no reusable fail-fast guard at request time, and was already producing inconsistency (`iso25010` had a model, its siblings did not). Option 1 keeps the human/LLM-readable raw markdown every consumer actually wants, while still getting drift protection for free via the parse-and-discard pattern plus a dedicated, reusable model test -- unifying the two previously-inconsistent conventions (`iso25010`'s JSON vs. `dtais`/`tara`/`risk-matrix`'s raw-markdown-with-regex-tests) into the one pattern every future reference resource should now follow.

### Consequences

`specmgr://iso25010` changes its resource output shape from a structured `Iso25010` JSON object to raw markdown text -- a breaking change on this pre-1.0 (0.x) codebase, recorded in `CHANGELOG.md` under `[Unreleased]`, but with no real consumer impact since the only consumer is an LLM reading prose. `specmgr://dtais`, `specmgr://rsk/tara`, and `specmgr://rsk/risk-matrix` gain dedicated Pydantic models (`general/models/dtais.py`, `rsk/models/v1/tara.py`, `rsk/models/v1/risk_matrix.py`) and dedicated `tests/models/test_*.py` drift-guard suites, replacing their previous ad hoc regex-based resource tests. `specmgr://rasci` gains a dedicated model (`general/models/rasci.py`) it did not previously have. The new `specmgr://ears` resource is built on this same pattern from day one (`general/models/ears.py`, `general/data/general_ears.md`). Every future cross-cutting reference resource has one clear, established convention to follow instead of having to pick between two inconsistent existing precedents.

## Pros and Cons of the Options

### Option 1: Uniform raw markdown + model-backed drift-guard tests (chosen)

Good: matches the actual consumption pattern (an LLM reading prose via a prompt instruction) with no wasted serialization; still gets fail-fast drift protection via parse-and-discard at request time plus a dedicated, reusable `tests/models/test_*.py` suite; unifies two previously-inconsistent conventions (iso25010's JSON vs. dtais/tara/risk-matrix's ad hoc regex tests) into one; reuses the existing `MarkdownListItem` + `@computed_field` precedent from `feat.RequirementItem`/`tsk.TaskItem`, so no new shared `models/md` primitive is needed; scales cleanly to future reference resources (e.g. `ears`).
Bad: `iso25010`'s resource output shape changes (a breaking change on this pre-1.0 codebase, though with no real consumer impact); every resource still needs its own dedicated model and test, so the per-resource authoring cost is not zero.

### Option 2: Uniform structured JSON output

Good: consistent with `iso25010`'s current shape; a caller that did want to index into fields programmatically could do so without re-parsing markdown.
Bad: no actual consumer benefits from this, since every current caller is an LLM reading prose via a prompt instruction; adds a serialization/schema-shape burden and a breaking-change surface on the resource's own output contract for no corresponding gain; would require inventing a JSON shape for `dtais`/`tara`/`risk-matrix`/`rasci`/`ears` where none currently exists, more work than the chosen option. Rejected.

### Option 3: Uniform raw markdown with ad hoc regex tests, no dedicated model

Good: no new model code to write; matches `dtais`/`tara`/`risk-matrix`'s pre-existing status quo, so it is the least-effort option in the short term.
Bad: scales badly -- each resource reinvents its own regex checks with no shared structure; provides no reusable fail-fast guard at request time (validation is test-only); was already producing the very inconsistency this ADR sets out to resolve, since `iso25010` had a model and its siblings did not; drops `iso25010`'s existing parse-and-discard fail-fast behavior in production rather than extending it. Rejected.

## More Information

- Feature plan: `.specmgr/feat/feat-92-resources/README.md` (GitHub issue #92; REQ-001..REQ-007, ACC-001..ACC-007, Design Notes).
- Affected resources: `specmgr://iso25010`, `specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`, `specmgr://rasci`, and the new `specmgr://ears`.
- Related ADRs: 36905d5b-8057-4294-8665-c7eed5534db0 (generic type-dispatched tool precedent this ADR's "one convention, applied uniformly" reasoning mirrors); 832cd6c1-ef8a-4bfc-990e-a610823f61ae (generic heading-mapped markdown-to-Pydantic parsing -- the `models/md` building blocks these new models are built on); 898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs authored only through MCP structured tools -- this ADR was created with `create_adr`).
