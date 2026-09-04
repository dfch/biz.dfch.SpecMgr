---
created: '2026-09-04 00:00:00.000Z'
id: feat-92-resources
status: planning
type: feat
updated: '2026-09-04 00:00:00.000Z'
version: 1.0.0
---

# Feature: Expose Cross-Cutting Reference Resources as Markdown with Model-Backed Drift-Guard Tests, Add EARS

## Plan

### Overview

Change how the cross-cutting reference resources (`specmgr://iso25010`,
`specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`,
`specmgr://rasci`) are exposed and validated, and add a new one
(`specmgr://ears`). Every current consumer of these resources is an LLM
reading prose via an MCP prompt instruction, never programmatic code
indexing into a parsed structure -- so validation moves from "structured
JSON returned on every call" (`iso25010` today) or "ad hoc regex
cross-check in the resource's own test" (`dtais`/`tara`/`risk-matrix`
today) to a uniform pattern: raw markdown output, backed by a dedicated
internal Pydantic model that is (a) parsed on every resource call purely
to fail fast on structural drift, with the parsed result discarded and
the raw text returned, and (b) covered by its own
`tests/models/test_*.py` drift-guard suite. See GitHub issue #92.

### Requirements

- REQ-001: `specmgr://iso25010` returns raw markdown (`text/markdown`) instead of a structured `Iso25010` JSON object, and still calls `parse_iso25010()` on every read to fail fast on structural drift.
- REQ-002: A dedicated `general/models/dtais.py` model parses the DTAIS guidance document's structure (5 method words, matching "when to apply" list, 3-value coverage list).
- REQ-003: A dedicated `rsk/models/v1/tara.py` model parses the TARA guidance document's structure (4 strategy words, "when to apply" quadrant list, mitigation-interaction list, 6-value status list).
- REQ-004: A dedicated `rsk/models/v1/risk_matrix.py` model parses only the "Product thresholds" list (4 entries), leaving the visual 5x5 table unmodeled.
- REQ-005: A dedicated `general/models/rasci.py` model parses the 5 RASCI roles and their descriptions.
- REQ-006: A new `specmgr://ears` resource documents the EARS requirement-phrasing templates, backed by a `general/models/ears.py` model and a new packaged `general/data/general_ears.md`.
- REQ-007: An ADR documents the repo-wide convention established here (reference resource = markdown + model-backed unittest, not structured JSON).

### Acceptance Criteria

- [x] ACC-001: `specmgr://iso25010`'s `mime_type` is `text/markdown` and its test asserts fail-fast behavior on a malformed packaged file.
- [ ] ACC-002: `tests/models/test_dtais.py` fails if `general_dtais.md`'s 5+3-item structure is broken.
- [ ] ACC-003: `tests/models/test_tara.py` fails if `rsk_tara.md`'s 4+4+6-item structure is broken.
- [ ] ACC-004: `tests/models/test_risk_matrix.py` fails if `rsk_risk_matrix.md`'s 4-item threshold list is broken.
- [ ] ACC-005: `tests/models/test_rasci.py` fails if `general_rasci.md`'s 5-role structure is broken.
- [ ] ACC-006: `specmgr://ears` is registered, documented in `server.py`'s module docstring, and covered by a model + resource test.
- [x] ACC-007: An ADR exists documenting the convention.

### Scope

#### Included

- The five existing resources' output-shape/validation changes.
- One new resource (`ears`) and its packaged data, authored from scratch.
- New models, each with dedicated structural tests.
- One ADR.

#### Explicitly Out Of Scope

- Any change to how `req`/`gol`/`sysrs`/`vcr` *consume* EARS/ISO25010
  guidance (no prompt rewiring beyond what already references these
  resources).
- Adding a general-purpose markdown-table parsing primitive to
  `models/md` (deliberately avoided per Design Notes below).

### Dependencies

#### Depends On

- None.

#### Blocks

- None known yet.

### Design Notes

- **List-item modeling pattern**: `dtais`/`tara`/`ears`'s closed-vocabulary
  bullets are modeled as `MarkdownListItem` subclasses with a
  `@computed_field` that regex-extracts the leading keyword from `.text`,
  reusing the exact precedent already established by
  `feat.RequirementItem`/`tsk.TaskItem` -- no new shared `models/md`
  primitive is needed.
- **`risk_matrix` avoids table parsing entirely**: the visual 5x5 table
  and the "Product thresholds" list encode the same information; only the
  4-item threshold list is modeled. The visual table stays unvalidated
  prose (residual drift risk accepted, optionally covered by a
  lightweight regex-only test assertion, not a model field).
- **Model placement**: `general/models/` for `dtais`/`rasci`/`ears`
  (cross-cutting, same domain-first precedent as `paged_result.py`/
  `summary.py`); `rsk/models/v1/` for `tara`/`risk_matrix` (RSK-owned,
  alongside `Strategy`/`level_from_product`).
- **`iso25010` validation timing**: parse-and-discard at request time
  (fail fast in production) *and* a CI-time drift-guard test -- not
  test-only validation.

### Related Decisions

- ADR (to be created in Phase 0): formalizes this feature's central
  convention repo-wide.

### Task List

#### Phase 0: ADR

- [x] Task 0.1: Write and merge the ADR (REQ-007).

#### Phase 1: `iso25010`

- [x] Task 1.1: Switch `general/resources/iso25010.py` to markdown output with parse-and-discard validation.
- [x] Task 1.2: Update `dtais.py`'s stale docstring cross-reference.
- [x] Task 1.3: Broaden `tests/models/test_iso25010.py`; rewrite `tests/general/resources/test_iso25010.py`.

#### Phase 2: `dtais` model

- [ ] Task 2.1: Add `general/models/dtais.py` and `tests/models/test_dtais.py`.

#### Phase 3: `tara` model

- [ ] Task 3.1: Add `rsk/models/v1/tara.py` and `tests/models/test_tara.py`.

#### Phase 4: `risk_matrix` model

- [ ] Task 4.1: Add `rsk/models/v1/risk_matrix.py` and `tests/models/test_risk_matrix.py`.

#### Phase 5: `rasci` model

- [ ] Task 5.1: Add `general/models/rasci.py` and `tests/models/test_rasci.py`.

#### Phase 6: `ears` resource

- [ ] Task 6.1: Author `general/data/general_ears.md`.
- [ ] Task 6.2: Add `general/models/ears.py`, `general/resources/ears.py`, and tests.

#### Phase 7: Wrap-up

- [ ] Task 7.1: Regenerate docs, update `server.py`'s docstring, add a CHANGELOG entry, run the full lint/test pass.

## Progress

### Current Status

**As of 2026-09-04**: Phase 0 (ADR) and Phase 1 (`iso25010`) done. ADR
356d8781-e446-4c26-917a-eda85648ce9d accepted, documenting the repo-wide
convention; `specmgr://iso25010` now follows it (raw markdown,
parse-and-discard). Phases 2-7 not started yet.

### Blockers

None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 00:00:00.000Z - Phase 1 (`iso25010`) complete

Switched `general/resources/iso25010.py`'s `iso25010()` resource function
from returning a structured `Iso25010` JSON object (`mime_type="application/json"`)
to returning the packaged `general/data/general_iso25010.md` raw markdown
text (`mime_type="text/markdown"`), per ADR
356d8781-e446-4c26-917a-eda85648ce9d: it still
calls `parse_iso25010()` on every call to fail fast on structural drift,
discarding the parsed result and returning the original raw text. Fixed
stale "`specmgr://iso25010`'s structured parse is the precedent for
machine-readable reference data" cross-references in
`general/resources/dtais.py`, `general/resources/rasci.py`, and
`rsk/resources/tara.py`'s docstrings (Task 1.2), and one similarly stale
"unlike `iso25010` (parsed into a structured model)" line in `rasci.py`'s
function docstring. Broadened `tests/models/test_iso25010.py` with a new
`test_raises_on_malformed_text` fail-fast/drift-guard test (a
deliberately-truncated 2-of-9-characteristic document). Rewrote
`tests/general/resources/test_iso25010.py` to match the new raw-markdown
contract, mirroring `tests/general/resources/test_dtais.py`/
`tests/rsk/resources/test_tara.py`'s established pattern: real packaged
content assertions, fresh-read-per-call
(`mock.patch.object(_packaged_data, "packaged_data_path", ...)`),
`FileNotFoundError` propagation on a missing file, and (ACC-001) a new
`test_raises_on_structural_drift` test that patches the packaged file to
malformed content and asserts the resource raises. Regenerated
`docs/api/`/`docs/GENERATED.md` via `specmgr docs` (docstring-only diff,
`server.py`'s own module docstring intentionally left describing the old
JSON behavior for now -- that's Phase 7's Task 7.1). Full quality gate
(ruff format --check, ruff check, vulture, full unittest suite: 3322
tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 0 (ADR) complete

Created and accepted ADR
`docs/adr/356d8781-e446-4c26-917a-eda85648ce9d-expose-cross-cutting-reference-resources-as-raw-markdown-wit.md`
("Expose cross-cutting reference resources as raw markdown with
model-backed drift-guard tests, not structured JSON") via the `create_adr`
MCP tool, covering all three considered options (chosen: uniform raw
markdown + model-backed drift-guard tests; rejected: uniform structured
JSON; rejected: uniform raw markdown with ad hoc regex tests only) and
cross-referencing `specmgr://iso25010`/`dtais`/`rsk/tara`/`rsk/risk-matrix`/
`rasci`/the new `ears`, plus GitHub issue #92 and this feature's README in
"More Information". Regenerated `docs/adr/README.md` via
`specmgr adr-toc`. Full quality gate (ruff format --check, ruff check,
vulture, full unittest suite: 3318 tests) passed.

#### 2026-09-04 00:00:00.000Z - Created

Feature folder created for GitHub issue #92, capturing the plan discussed
and agreed with the user.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 00:00:00.000Z - EARS resource placement

`specmgr://ears` lives under `general/resources/` (cross-cutting), not
`req/resources/`, mirroring `dtais`'s cross-domain placement rationale.

#### 2026-09-04 00:00:00.000Z - Model scope for regex-cross-checked resources

Dedicated models are added for all three of `dtais`, `tara`, and
`risk_matrix` (not just `risk_matrix`), replacing their existing ad hoc
regex-based drift-guard tests.

#### 2026-09-04 00:00:00.000Z - iso25010 validation approach

Kept runtime validate-then-discard (parse via `parse_iso25010` to fail
fast, return raw text) rather than test-only validation.

### Related PRs / Commits

- GitHub issue #92: https://github.com/dfch/biz.dfch.SpecMgr/issues/92

### More Information

None.
