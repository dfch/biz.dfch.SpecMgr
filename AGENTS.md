# AGENTS.md

Quick reference for OpenCode agents working on **biz.dfch.SpecMgr** — an artifact manager for system specifications.

## Status: domain packages implemented (the per-domain bullets below are the live enumeration)

Each package below follows the domain-first layout from ADR
ece4554b-725c-4f76-bc04-5d2b760363d2 ("Organize the codebase by
document-type domain: domain-first hierarchy for tools/prompts/resources,
shared versioned models") — one bullet per implemented package, document
type or cross-cutting:

- **`adr/`** (Architecture Decision Records) — the original, most complete
  domain. `adr/tools/` has 11 `@mcp.tool()` wrappers (`get_adr`, `list_adr`,
  `create_adr`, `update_frontmatter`, `update_section`,
  `option_list`/`option_create`/`option_read`/`option_update`/
  `option_delete`, `validate_adr`); ADR status changes go through the
  generic `set_status` tool in `general/tools/` (called with
  `type="adr"`, ADR-only `superseded_by`); `adr/resources/` exposes
  `specmgr://adr/{id}` only — no `specmgr://adr/list` (listing is the
  `list_adr` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13);
  `adr/prompts/` has
  narrated `create_adr`/`update_adr` prompts plus step-gated
  `create_adr_test`/`update_adr_test` A/B variants (see
  `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §11). Its Pydantic
  schema uniquely lives under the shared top-level `models/adr/` (not
  `adr/models/`) — see the "models location" note below.
- **`req/`** (Requirements) — `req/tools/` (`create_req`, `parse_req`,
  `list_req`, `delete_req` stub, `validate_req`); whole-body and line-range
  updates go through the generic `update` tool in `general/tools/`
  (`type="req"`), status changes through the generic `set_status` tool
  (`type="req"`); `req/resources/` (`specmgr://req/schema`,
  `specmgr://req/example`, `specmgr://req/template`; no `specmgr://req/{id}`
  — id-based reads are `get_req`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://req/list` —
  listing is the `list_req` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `req/prompts/`
  (`create_req`/`update_req`). Its schema lives at `req/models/v1/`, inside
  the domain package itself, not under top-level `models/`.
- **`uc/`** (Use Cases) — same tools/resources/prompts shape as `req/` but
  for use cases (`create_uc`, `parse_uc`,
  `list_uc`, `get_uc`, `get_uc_example`, `get_uc_template`, `delete_uc` stub,
  `validate_uc`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="uc"`), status changes through
  the generic `set_status` tool (`type="uc"`), and the `get_uc` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); no
  `specmgr://uc/{id}` resource for the same reason as
  REQ, and no `specmgr://uc/list` resource either — listing is the
  `list_uc` tool (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). Schema at
  `uc/models/v1/` (legacy) and `uc/models/v2/` (current),
  inside the domain package, not `models/uc/`.
- **`tsk/`** (Task Lists) — same shape again (`create_tsk`,
  `parse_tsk`, `list_tsk`, `get_tsk`, `get_tsk_example`,
  `get_tsk_template`, `delete_tsk` stub, `validate_tsk`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="tsk"`), status changes through the generic
  `set_status` tool (`type="tsk"`), and the `get_tsk` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); plus a distinct
  `implement_task` prompt (reads a task list via `get_tsk`, builds a
  `TodoWrite` list from its items, and uses the `question` tool to resolve
  ambiguity). Its resources are the usual `specmgr://tsk/schema`/
  `specmgr://tsk/example`/`specmgr://tsk/template` only — no
  `specmgr://tsk/{id}` and no `specmgr://tsk/list` resource (listing is
  the `list_tsk` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). Schema
  at `tsk/models/v1/`, inside the domain package.
- **`qa/`** (Question and Answer) — same tools/resources/prompts shape as
  `req/`/`tsk/` but for requirements-elicitation Q&A interviews (`create_qa`,
  `parse_qa`, `list_qa`, `get_qa`, `get_qa_example`,
  `get_qa_template`, `delete_qa` stub, `validate_qa`); whole-body and
  line-range updates go through the generic `update` tool in
  `general/tools/` (`type="qa"`), status changes through the generic
  `set_status` tool (`type="qa"`), and the `get_qa` tool takes
  `raw: bool = False` — `raw=True` returns the frontmatter-stripped body
  text as-is (the text `update`'s `begin`/`end` index into); `qa/resources/`
  (`specmgr://qa/schema`, `specmgr://qa/example`,
  `specmgr://qa/template`; no `specmgr://qa/{id}` — id-based reads are
  `get_qa`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://qa/list` — listing is the `list_qa` tool, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `qa/prompts/`
  (`create_qa`/`update_qa`, plus `refine`). Schema at `qa/models/v2/`,
  inside the domain package, not `models/qa/` — QA is a single-schema
  (v2-only) domain: every question/answer category holds zero or more
  adjacent, un-headed pairs (`<!-- optional comment -->` + `> {question}`
  block quote + free-form answer prose) directly inside a category section,
  no heading of its own per pair, plus a `## Elicitation Context` section
  (structurally identical to, but not one of, the 9 ISO/IEC 25010:2023
  characteristic sections) between `## General` and
  `## Functional Suitability`. An earlier `qa/models/v1/` schema (one
  `### {heading}` H3 per question/answer pair) existed alongside v2 during
  feat-14 and was removed entirely once every QA MCP tool/resource/prompt
  was repointed at v2 (feat-14 Phase 8) — there is no version-gate or
  dual-schema read support: a document shaped for the removed v1 schema
  fails v2 parsing with a structural
  `AssertionError`/`pydantic.ValidationError`, not a migration-specific
  error.
- **`prb/`** (Problem Statement) — same tools/resources/prompts shape as
  `req/`/`tsk`/`qa` but for Six-Sigma-style problem statements
  (`create_prb`, `parse_prb`, `list_prb`,
  `get_prb`, `get_prb_example`, `get_prb_template`, `delete_prb` stub,
  `validate_prb`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="prb"`), status changes through
  the generic `set_status` tool (`type="prb"`), and the `get_prb` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `prb/resources/` (`specmgr://prb/schema`,
  `specmgr://prb/example`, `specmgr://prb/template`; no
  `specmgr://prb/{id}` — id-based reads are `get_prb`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://prb/list` — listing
  is the `list_prb` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13);
   `prb/prompts/` (`create_prb`/`update_prb`, narrated `TodoWrite` +
   `question`-tool-driven 5W2H interview flows). Schema at
   `prb/models/v1/`, inside the domain package, not top-level
   `models/`.
- **`gol/`** (Goal) — same tools/resources/prompts shape as
  `req/`/`prb/` but for high-level business goals (the strategic
  "what the organization wants to achieve" level that sits above
  individual requirements) (`create_gol`,
  `parse_gol`, `list_gol`, `get_gol`,
  `get_gol_example`, `get_gol_template`, `delete_gol` stub,
  `validate_gol`); whole-body and line-range updates go through the generic
  `update` tool in `general/tools/` (`type="gol"`), status changes through
  the generic `set_status` tool (`type="gol"`), and the `get_gol` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `gol/resources/` (`specmgr://gol/schema`,
  `specmgr://gol/example`, `specmgr://gol/template`; no
  `specmgr://gol/{id}` — id-based reads are `get_gol`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://gol/list` —
  `list_gol` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `gol/prompts/`
  (`create_gol`/`update_gol`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_gol` first checks
   `list_gol` for a near-duplicate goal). Its schema lives at
   `gol/models/v1/`, inside the domain package, not top-level
   `models/`. The body mirrors REQ minus the `## Characteristics`
  and `## Level` sections (see `.specmgr/feat/feat-18-goal/README.md`).
- **`rsk/`** (Risk) — same tools/resources/prompts shape as
  `req/`/`prb/` but for risk-register entries (the scenario decomposed
  into `## Cause`/`## Trigger`/`## Consequence`, a 5x5 probability/impact
  assessment BEFORE mitigation (`## Initial Assessment`) and the same 5x5
  AFTER mitigation (`## Residual Assessment`) with the value in the H3
  heading itself (`### Probability {1..5}` / `### Impact {1..5}`, regex
  `@alias`-constrained, derived zone `level` always computed from the
  product), and a TARA response strategy `## Strategy` (closed 4-value set
  `transfer`/`accept`/`reduce`/`avoid`))
  (`parse_rsk`, `get_rsk`, `list_rsk`, `get_rsk_example`,
  `get_rsk_template`, `create_rsk`,
  `delete_rsk` stub, `validate_rsk`); whole-body and line-range updates
  go through the generic `update` tool in `general/tools/`
  (`type="rsk"`), status changes through the generic `set_status` tool
  (`type="rsk"`), and the `get_rsk` tool takes `raw: bool = False` —
  `raw=True` returns the frontmatter-stripped body text as-is (the text
  `update`'s `begin`/`end` index into); `rsk/resources/`
  (`specmgr://rsk/schema`, `specmgr://rsk/example`,
  `specmgr://rsk/template`, plus two static domain-knowledge resources
  `specmgr://rsk/tara` — what TARA is and when/how to apply each of the
  four words — and `specmgr://rsk/risk-matrix` — the 5x5 scale anchors,
  zone table, and product thresholds; no `specmgr://rsk/{id}` — id-based
  reads are `get_rsk`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://rsk/list` — `list_rsk` ships as a paged tool from day one,
  ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, and its `RskSummary` lines
  carry the residual-risk coordinates so a register-wide risk-matrix view
  can be built from the listing alone); `rsk/prompts/`
   (`create_risk`/`update_risk` — the issue's literal wording, not the
   `rsk`-prefixed convention the tools/resources use). Its schema lives at
   `rsk/models/v1/`, inside the domain package, not top-level
   `models/`.
- **`dec/`** (Decision) — same tools/resources/prompts shape as
  `req/`/`prb/` but for decisions in general (not architecture-only)
  (`parse_dec`, `get_dec`, `list_dec`, `get_dec_example`,
  `get_dec_template`, `create_dec`, `delete_dec` stub,
  `validate_dec`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="dec"`), status
  changes through the generic `set_status` tool (`type="dec"`), and
  the `get_dec` tool takes `raw: bool = False` — `raw=True` returns
  the frontmatter-stripped body text as-is (the text `update`'s
  `begin`/`end` index into); `dec/resources/`
  (`specmgr://dec/schema`, `specmgr://dec/example`,
  `specmgr://dec/template`; no `specmgr://dec/{id}` — id-based reads
  are `get_dec`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://dec/list` — `list_dec` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `dec/prompts/`
  (`create_dec`/`update_dec`, narrated `TodoWrite` +
  `question`-tool-driven interview flows; `create_dec` first checks
  `list_dec` for a near-duplicate decision). Its schema lives at
  `dec/models/v1/`, inside the domain package, not top-level
  `models/`. A DEC keeps the ADR's general structure (MADR-style
  headings, `Options` collection) but is built on the generic
  `models/md` parser with the GOL/RSK/QA simple surface — no
  fine-grained mutation tools, no renderer: writes persist the
  caller's raw validated body byte-for-byte.
- **`feat/`** (Feature) — formalizes the ad hoc `.specmgr/feat/<id>/
  README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e) into a
  real, schema-backed domain, and is the one domain in this codebase whose
  own addressing genuinely deviates from every other domain's precedent
  (ADR 8cf940c5-3100-485c-a12d-14b59b631712): `id` is a chosen
  `feat-NNN-slug` — the containing folder's own name, not a
  server-generated UUID — and documents live one-per-folder as
  `<base>/<id>/README.md` (a fixed filename), not flat files directly
  under the base directory. This bespoke, folder-per-document addressing
  is hand-rolled in `feat/tools/_paths.py` (ADR-style, like `adr/tools/
  _paths.py`), **not** built on the shared flat-file
  `general/tools/_doc_paths.py` every other whole-body domain uses;
  `SPECMGR_FEAT_DIR` overrides the base directory (mandatory-in-spirit
  test-isolation env var, same as every other domain's own equivalent).
  All 8 tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`,
  `get_feat_example`, `get_feat_template`, `delete_feat` stub,
  `validate_feat`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="feat"`), status
  changes through the generic `set_status` tool (`type="feat"`) — no
  `update_feat`/`set_status_feat` of its own — and the `get_feat` tool
  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
  body text as-is (the text `update`'s `begin`/`end` index into);
  `feat/resources/` (`specmgr://feat/schema`, `specmgr://feat/example`,
  `specmgr://feat/template`; no `specmgr://feat/{id}` — id-based reads
  are `get_feat`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
  `specmgr://feat/list` — `list_feat` ships as a paged tool from day
  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `feat/prompts/`
  (`create_feat`/`update_feat`, narrated instruction flows; `create_feat`
  first checks `list_feat` for a near-duplicate feature). Its schema
  lives at `feat/models/v1/`, inside the domain package, not top-level
  `models/`. `FeatSummary` adds one extra field beyond every other
  domain's summary, `path: str` (the real filesystem path to the
  document's `README.md`) — a deliberate divergence, since direct
  hand/agent editing of `.specmgr/feat/<id>/README.md` remains the
  domain's own normal, sanctioned workflow even after its MCP tools
  exist, unlike every other domain's summary, whose `ref` field is
  deliberately *not* a path. See
  `.specmgr/feat/feat-31-feature/README.md` for the full design.
- **`vcr/`** (Verification Case Record) — same tools/resources/prompts
  shape as `req/`/`prb/`/`dec/` but for how a single REQ/UC is verified: a
  `## Verifies` single-value cross-reference (exactly one mandatory
  `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase, not a
  bullet list — a single-value field is structurally incapable of holding
  more than one reference), a `## Coverage` closed-vocabulary outcome
  signal (`full`/`partial`/`none`, mirroring RSK's `## Strategy` idiom),
  and a `## Acceptance Criteria` collection of `### AC-NNN (Method): ...`
  entries (3-digit zero-padded number, DEC-`Option`-style numbered H3, no
  per-AC mutation tools; `Method` is a closed **DTAIS** vocabulary —
  Demonstration, Test, Analysis, Inspection, Special — parsed from the
  heading itself via regex, RSK `Probability`/`Impact`-style; each entry
  optionally carries a free-form `description` paragraph and/or a
  `#### Test Steps` numbered procedure; a `model_validator` rejects
  duplicate `AC-NNN` numbers), plus optional `## More Information`/
  `## Updates` (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`,
  `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
  `validate_vcr`); whole-body and line-range updates go through the
  generic `update` tool in `general/tools/` (`type="vcr"`), status
  changes through the generic `set_status` tool (`type="vcr"`), and the
  `get_vcr` tool takes `raw: bool = False` — `raw=True` returns the
  frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
  index into); `vcr/resources/` (`specmgr://vcr/schema`,
  `specmgr://vcr/example`, `specmgr://vcr/template`; no
  `specmgr://vcr/{id}` — id-based reads are `get_vcr`-only, ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://vcr/list` —
  `list_vcr` ships as a paged tool from day one, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); `vcr/prompts/`
  (`create_vcr`/`update_vcr`). Its schema lives at `vcr/models/v1/`,
  inside the domain package, not top-level `models/`. The closed DTAIS
  method vocabulary its `## Acceptance Criteria` depends on is documented
  by the cross-cutting `specmgr://dtais` resource, which lives in
  `general/resources/`, not `vcr/resources/`, since it is domain-knowledge
  other document types may also want to reference (mirroring RSK's
  `specmgr://rsk/tara` shape). See `.specmgr/feat/feat-33-vcr/README.md`
  for the full design.
  - **`general/`** — cross-cutting, non-domain-specific package:
    `general/tools/` (`mdformat`, formats a markdown file in place while
    preserving YAML frontmatter blocks; `update`, the generic whole-body
    *and* line-range replace for the ten whole-body domains — `type` is
    one of req/uc/tsk/qa/prb/gol/rsk/dec/feat/vcr, optional 1-based inclusive
    body-line
    `begin`/`end` with the `N+1` end-of-body sentinel, splice-then-
    validate-whole; `set_status`, the generic status change for all eleven
    domains incl. adr — `superseded_by` is ADR-only, composing
    `"superseded by X"`), `general/resources/`
   (`specmgr://version`, `specmgr://iso25010` — the ISO/IEC 25010:2023
   quality model, `specmgr://dtais` — the DTAIS verification-method
   vocabulary VCR's `## Acceptance Criteria` depends on, kept here rather
   than under `vcr/resources/` since it is domain-knowledge other document
   types may also want to reference), and `general/prompts/` (`compact_history` — rotates
    older `Recent Updates` entries out of any feature folder's `README.md`
    into a sibling `history.md`). The ten `get_<d>` tools additionally
    take a `raw: bool = False` parameter — `raw=True` returns the
    frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
    index into).

**Models location — a real, intentional divergence, not an oversight**:
the rule is domain-first — every document type keeps its schema inside
its own domain package (`<domain>/models/vN/`); building a new document
type requires no edit to this paragraph. The single exception is ADR:
its schema (`AdrFrontmatter`, `AdrBody`, `AdrOption`, `Adr`, `parse_adr`,
`render_adr`) stays under the shared top-level `models/adr/` package
because it predates the domain-first refactor and has no dependency on
`mcp`/`tools`/`resources`/`prompts`. Top-level `models/` therefore holds
`adr/` (the exception) plus only shared cross-domain modules —
`iso25010.py`, `md/` (markdown-section building blocks), and
`version_info.py` — don't assume any other doc type's schema lives there.

`server.py`'s own module docstring is the single most authoritative,
currently-maintained list of every resource/tool/prompt this MCP server
registers — read it before consulting this file for specifics, and update
it whenever you add/remove/rename a resource, tool, or prompt.
`docs/MCP.md` is the auto-generated (via `specmgr mcp-docs`), user-facing
mirror of that same registration and must never be hand-edited.

Still genuinely missing / not yet done (don't assume otherwise):
- No `validate_adr` (or `validate_req`/`validate_uc`/`validate_tsk`/
  `validate_qa`/`validate_prb`/`validate_gol`/`validate_rsk`/
  `validate_dec`/`validate_feat`/`validate_vcr`) tool runs
  over the repo's
  own documents yet via pre-commit or CI. (ADR
  9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
  locally via pre-commit hook, not just CI")
- `delete_req`/`delete_uc`/`delete_tsk`/`delete_qa`/`delete_prb`/
  `delete_gol`/`delete_rsk`/`delete_dec`/`delete_feat`/`delete_vcr` are
  stubs, not yet implemented.
- No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
  docstring already reserving a spot for it ("... and later `ac`") — the
  convention for adding it (or any future domain) is fixed by ADR
  36905d5b-8057-4294-8665-c7eed5534db0: one dispatch entry to each of the
  two generic tools in `general/tools/` (`update`'s `type`,
  `set_status`'s `type`) plus a `raw` parameter on the new `get_<d>` tool
  — not new `update_<d>`/`set_status_<d>` tools.
- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`feat`/`vcr` each register
  `tools`, `resources`, and `prompts`; `uc` registers `tools` and
  `resources` only — it has no `prompts` sub-package yet.

`.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §10 ("Next steps") tracks per-item done/not-done
status for the ADR feature specifically and should be kept in sync with
`src/` as this evolves; treat it as current-state tracking, not just a
historical design doc. Don't assume any domain package exists beyond the
per-domain bullets in the Status section above (each with its respective
`tools`/`prompts`/`resources` sub-packages, per the exceptions noted
there), or anything in `general/resources/` beyond `version`/`iso25010` —
check first.

## Project Shape

- **Type**: Python library + optional CLI + optional MCP server, in one repo
- **Namespace**: `biz.dfch.specmgr` in `src/biz/dfch/specmgr/` — `biz`/`biz/dfch`
  are implicit namespace packages (no `__init__.py` in those two dirs; only the
  leaf `specmgr/` has one)
- **Package manager**: `uv` (not pip) — lockfile is committed, use `--frozen`
- **Python**: `requires-python = ">=3.11"` (3.11–3.13 tested in CI); local dev
  defaults to 3.13 via `.python-version` — two separate settings, keep in
  sync intentionally, not by accident

## Development Artifacts (`.specmgr/`)

Per ADR e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development
artifacts in `.specmgr` with feature-driven work units"), development
planning/progress artifacts live under `.specmgr/`, separate from published
documentation in `docs/`:

```
.specmgr/
├── _template/
│   └── v1/
│       └── README.md              # Versioned feature template (plan + progress)
└── feat/
    └── feat-NNN-slug/              # One folder per GitHub issue
        ├── README.md               # Feature plan + progress (mandatory)
        └── history.md              # Archived older "Recent Updates" entries (optional)
```

- **Naming convention**: `feat-NNN-slug`, where `NNN` is the GitHub issue
  number. Work started without an issue yet uses `feat-0-slug` (issue number
  `0`) until/unless an issue is later opened for it.
- **Single `README.md` per feature** combines the plan (requirements,
  acceptance criteria, scope, dependencies, design notes) and progress
  (current status, blockers, recent updates, decisions made) — there is no
  separate `progress.md`; status lives inline on each task line, edited in
  place rather than duplicated.
- **Template**: `.specmgr/_template/v1/README.md` is the versioned,
  reusable template (copy it when starting a new feature folder). It is
  hand-copied, not scaffolded by any tool — no automation exists for this
  yet, and none is currently planned.
- **Frontmatter**: every feature `README.md` starts with a minimal YAML
  frontmatter block — `id` (the `feat-NNN-slug` folder name itself, not a
  generated UUID), `version` (semver, starts at `1.0.0`), `status`
  (`planning` | `in-progress` | `review` | `done`), and `created`/`updated`
  (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no
  separate `GitHub Issue` field/body-line: the issue number is the `NNN`
  infix already embedded in `id`/the folder name (`feat-NNN-slug`) — `0`
  means no issue yet — so it is never duplicated elsewhere in the file. See
  ADR e369ee2e-3353-4f92-991c-6367d76d832e's Option 1 for the full
  rationale.
- **`doc/` has been migrated** into this structure — development planning docs
   now live in `.specmgr/feat/` with their respective feature folders.
- **No CI/pre-commit enforcement** exists for `.specmgr/` content — unlike
  `docs/adr/`, there is no `validate_adr`-equivalent check and no `adr-toc`-
  equivalent generation step wired into hooks or CI for feature folders.
- **ADR vs. feature-level "Decisions Made" log**: a decision belongs in a
  full ADR (`docs/adr/`) if it's architecture/structure-level, affects more
  than one feature or the repo as a whole, or reverses/supersedes a previous
  ADR. It belongs in the feature's own "Decisions Made" log instead if it's
  scoped entirely to that feature's implementation details. When in doubt,
  write the ADR.
- Existing feature folders: `.specmgr/feat/feat-9-doc-in-specmgr/`
   (development artifacts migration), `.specmgr/feat/feat-4-use-cases/` (use-case
   modeling and examples), `.specmgr/feat/feat-5-md-model-parser/` (markdown
   parsing infrastructure).

## Developer Commands

```bash
uv sync --all-extras                                                   # install deps
uv run --frozen pre-commit install                                     # one-time: enable pre-commit hooks
uv run --frozen ruff format --check && uv run --frozen ruff check      # lint (enforced)
uv run --frozen pylint $(git ls-files '*.py')                          # lint (advisory only; CI runs it with `|| true`)
uv run --frozen vulture src/ whitelist.py --min-confidence 60          # dead-code check (enforced)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"  # tests
uv run --frozen specmgr docs                                           # regenerate docs/api/ + docs/GENERATED.md
uv run --frozen specmgr adr-toc                                        # regenerate docs/adr/README.md (ADR table of contents)
uv run --frozen specmgr unused-code                                    # report unused code in src/ (same check as the vulture hook)
uv run --frozen specmgr unused-code --test                             # report symbols only referenced from tests/, never src/
uv run --frozen specmgr version                                        # run the CLI
```

### Using a different Python version

The project defaults to Python 3.13 (see `.python-version`). To use a different version (e.g., 3.12), add `--python X.Y` to **both** `uv sync` and `uv run` commands, and include `--all-extras` on the `uv run` call:

```bash
uv sync --all-extras --frozen --python 3.12
uv run --frozen --all-extras --python 3.12 specmgr docs
```

Without `--all-extras` on `uv run`, only base dependencies are installed, causing `ModuleNotFoundError` for CLI/MCP extras like `typer`.

`pylint` only sees files tracked by git (`git ls-files`) — new files must be
`git add`ed before it will lint them, both locally and in CI.

`pre-commit install` is one-time per clone (see `.pre-commit-config.yaml`):
runs `ruff format`/`ruff check`, the full `unittest` suite (scoped to
`src/**/*.py`/`tests/**/*.py` changes), a local `specmgr docs` hook (scoped to
`src/**/*.py` changes), and a local `specmgr adr-toc` hook (scoped to
`docs/adr/**/*.md` changes) before every commit, so a broken test or drift in
`docs/api/`/`docs/GENERATED.md`/`docs/adr/README.md` gets caught locally instead
of failing later in CI. (ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests locally via pre-commit hook, not just CI")

## Extras split (base library has no CLI/MCP deps)

`dependencies` in `pyproject.toml` is only `pydantic` + `python-dotenv`, so the
library is usable standalone. `typer`/`rich` live in the `cli` extra, `mcp` in
the `mcp` extra. **Never** import `cli.py` or `server.py` from
`src/biz/dfch/specmgr/__init__.py` — that would force those extras onto every
consumer of the base library.

## CLI (`cli.py`)

- Typer app, entry point `specmgr` (`pyproject.toml` `[project.scripts]`);
  `python -m biz.dfch.specmgr` (`__main__.py`) runs the same Typer `app()`.
- **Gotcha**: with only one `@app.command()` registered, Typer collapses to a
  single top-level command and drops subcommand dispatch (`specmgr version`
  would fail with "unexpected extra argument"). An explicit `@app.callback()`
  (see `_callback` in `cli.py`) forces Typer to keep treating it as a command
  group — keep that callback even after a second command is added, don't
  assume it becomes dead code to remove.

## MCP server (`server.py`)

- Builds the `MCPServer` instance (`mcp` object) and a no-op `_lifespan`,
  then imports every domain package (`adr`, `dec`, `feat`, `general`,
  `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`, `vcr`) as its last line
  purely for the side effect of
  running their `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` decorators.
  When adding a new domain, add its import to that same last line —
  forgetting it means the new tools/resources/prompts silently never
  register.
- **`specmgr mcp`** (`commands/mcp.py`) *does* start the server —
  `mcp_server.run(transport="stdio")` by default, or
  `mcp_server.run(transport="sse", host=..., port=...)` via
  `--transport sse`/`-t sse`. `python -m biz.dfch.specmgr mcp` and
  `uvx --from "biz-dfch-specmgr[mcp]" specmgr mcp` both work identically
  (see `README.md`'s "Add to OpenCode" section) — don't assume the server
  has no working entry point.

## CI / Release

- Branches: `dev` (default, feature work) → `main` (stable) → tag.
- `.github/workflows/ci.yml`: ruff + pylint (`|| true`) + vulture + unittest
  run on matrix 3.11/3.12/3.13 via `uv sync --frozen --all-extras`, but
  `specmgr docs` and `specmgr adr-toc` drift checks run **only on Python
  3.13** (pinned, since different Python versions generate different
  docstring formatting in the API docs, and we want consistent ADR TOC
  generation).
- `.github/workflows/publish.yml` exists and has shipped `v0.1.0`, `v0.2.0`,
  `v0.2.1` to PyPI/the MCP Registry, triggered on `v*` tags.
- Version bumps: update `version` in `pyproject.toml` (single source) and
  move `CHANGELOG.md`'s `[Unreleased]` into a dated section, same commit.

## Coding Standards

See `.specmgr/conventions.md` for detailed coding requirements and conventions:
- Python version and type notation
- Assert statement guidelines
- Variable naming (use `result` for return values)
- Comparison constants
- Mandatory type hints
- Documentation requirements for classes, attributes, and functions

- Formatter/linter: `ruff` (enforced, not black), line length 120.
- `pylint` is advisory fallback only (see pylint caveat above).

## Generated Documentation

See [`docs/GENERATED.md`](docs/GENERATED.md), auto-generated by `specmgr
docs` (implemented-domain list, per-module docstrings, and test-file count).
This pointer is permanent and hand-written — it is never regex-spliced or
otherwise auto-edited; only `docs/GENERATED.md` itself is regenerated.
