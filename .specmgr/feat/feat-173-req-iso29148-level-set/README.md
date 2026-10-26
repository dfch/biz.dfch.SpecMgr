---
classification: null
created: '2026-10-26T09:06:20.846+01:00'
id: feat-173-req-iso29148-level-set
status: planning
type: feat
updated: '2026-10-26T09:06:20.846+01:00'
version: 1.0.0
---

# Feature: REQ ISO 29148 Requirement Level (and deferred SET artifact type)

## Plan

### Overview

Issue #173 has two work packages. This feature's Phases 110-170 implement the first: REQ's `## Level` field becomes the ISO/IEC/IEEE 29148:2018 requirement-specification kind (closed set `BRS`, `StRS`, `SyRS`, `SRS` — the standard's own §3.2 abbreviations), the RFC 2119 obligation keywords are dropped from the REQ schema entirely (obligation is carried by the requirement statement's phrasing, EARS), a new cross-cutting `specmgr://iso29148` domain-knowledge resource is added, and the 14 in-repo REQ documents are migrated in the same commit. The change is breaking by construction (mandatory field, new value set) and follows the feat-132-prb-update precedent of in-place `models/v1` schema evolution. The second work package — the new `SET` artifact type — is deferred to Phase 180 of this same feature until its open design questions are resolved.

### Requirements

- REQ-001: REQ's `## Level` is a mandatory single-line closed-value field whose value is exactly one of `BRS`, `StRS`, `SyRS`, `SRS` (ISO/IEC/IEEE 29148:2018 §3.2 abbreviations), enforced in `req/models/v1` via `_LEVEL_PATTERN` (in-place schema evolution, no v2).
- REQ-002: No RFC 2119 obligation field (MUST/SHOULD/MUST NOT/SHOULD NOT/MAY) exists in the REQ schema; obligation is carried by the requirement statement's phrasing (EARS, `specmgr://ears`).
- REQ-003: A new cross-cutting resource `specmgr://iso29148` documents the standard's four requirement specifications — the §3.2 abbreviations, the §5.4 mapping sentence (verbatim), the §6.2-6.4 processes, the §8.2-8.5 example outlines, the §9.3-9.6 content clauses — plus the mapping to specmgr document types and the §5.2.6 "Characteristics of a set of requirements" list (input to the deferred SET phase). Served as raw markdown with a fail-fast parse model (the `specmgr://ears` shape, ADR 356d8781).
- REQ-004: The `create_req` prompt reads `specmgr://iso29148` first (the SOP `specmgr://rasci` pattern) and elicits the ISO 29148 kind; the `update_req` prompt carries a present-tense recovery directive for documents failing to parse on a legacy `## Level` value. All prompt text describes the current structure in the present tense — no change-history phrasing.
- REQ-005: The 14 in-repo REQ documents (`docs/req/`) are migrated to `## Level: SRS` in the same commit as the schema change; the packaged `req_example.md` is migrated to `## Level: SyRS`.
- REQ-006: Packaged `req_template.md`/`req_schema.json`, generated `docs/api/` + `docs/MCP.md` + `docs/GENERATED.md`, the `server.py` docstring, the AGENTS.md `req`/`general` bullets, and the `tests/req` suite stay in sync with the schema change (schema regenerated via `specmgr schema`; pre-commit drift checks green).
- REQ-007: A new `SET` artifact domain groups one or more items of the same artifact type via forward references only (no backward reference from artifacts to a set), contains items of a single type, and carries guidance for examining a requirement set per ISO 29148 §5.2.6 (Complete, Consistent, Feasible, Comprehensible, Able to be validated) — deferred to Phase 180, issue #173 part 2.

### Acceptance Criteria

- [ ] ACC-001: `parse_req` accepts each of `BRS`, `StRS`, `SyRS`, `SRS` as the `## Level` value and rejects `MUST`, `SHOULD`, `MUST NOT`, `SHOULD NOT`, `MAY`, lowercase variants, and values with extra whitespace — the rejection error carries the new pattern (the feat-27 actionable-message shape).
- [ ] ACC-002: The packaged template and example parse via `parse_req` (drift-guard tests green); `req/data/req_schema.json` is byte-identical to the `specmgr schema` output (the `specmgr-schema-req-package` pre-commit hook green).
- [ ] ACC-003: `specmgr://iso29148` returns the packaged markdown verbatim; the drift-guard model parses it; a structural edit of the packaged file fails the tests (mirroring the ears/dtais test shapes).
- [ ] ACC-004: After the migration, `list_req` reports `error_count == 0` over the 14 `docs/req/` documents and the full `pytest` suite is green.
- [ ] ACC-005: No change-history phrasing (no "previously", "now contains", "instead of") appears in `req/data/req_create_instructions.md`, `req/data/req_update_instructions.md`, the `req/models/v1/body.py` `Level`/`Requirement` docstrings, the template comment, or the resource markdown (review gate over the final diff).
- [ ] ACC-006: `ruff format --check`, `ruff check`, `vulture`, and the `specmgr docs`/`specmgr mcp-docs` drift checks are all green on the final commit.

### Scope

#### Included

- The in-place `req/models/v1` schema evolution (`## Level` value set), its docstrings, and its tests.
- The new cross-cutting `specmgr://iso29148` resource (data file, parse model, registration, tests).
- The `create_req`/`update_req` prompt instruction rewrites (present-tense only).
- The packaged `req_template.md`/`req_example.md` updates and `req_schema.json` regeneration.
- The same-commit migration of the 14 in-repo REQ documents.
- Housekeeping: `server.py` docstring, AGENTS.md, `docs/api/`, `docs/MCP.md`, `docs/GENERATED.md`, CHANGELOG, version bump.

#### Explicitly Out Of Scope

- Implementing the `SET` artifact domain (issue #173 part 2) — planned in Phase 180, after its open design questions are resolved.
- Changing `ReqSummary`/`list_req` output (it stays minimal: id/title/status/ref/path).
- Re-wording obligation phrasing inside requirement statements during the migration (value replacement only).
- New domains, new tools, or resources other than `specmgr://iso29148`.
- Migrating external (out-of-repo) REQ documents — they recover via the actionable parse error plus the `update_req` recovery directive instead.

### Dependencies

#### Depends On

- None — the work builds on the existing `req` domain, the `general/resources` packaged-data pattern, and the feat-132 in-place breaking schema-evolution precedent.

#### Blocks

- Issue #173 part 2 (the `SET` domain) — the later phase of this same feature.

### Design Notes

**Terminology (verified against the ISO/IEC/IEEE 29148:2018 full text, 2026-10-26).** The standard has no single collective word for the four; each is a *requirements specification* (a requirement information item): §3.2 "Abbreviated terms" defines `BRS`/`StRS`/`SyRS`/`SRS`; §6.2-6.4 are the processes (business or mission analysis; stakeholder needs and requirements definition; system [system/software] requirements definition); §8.2-8.5 give the "example outlines"; §9.3-9.6 give the normative content. The standard's own mapping sentence (§5.4, p. 19) reads: "The business requirements specification (BRS), the stakeholder requirements specification (StRS), the system requirements specification (SyRS) and the software requirements specification (SRS) are intended to represent different sets of requirement information items. The specifications correspond to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - Software Requirements." "Level" appears in the standard descriptively in that mapping, alongside the defined term "level of abstraction" (§3.1) and the note "Requirements exist at different levels in the system structure." Consequence: keep the section name `## Level` (the issue title's own wording; consistent with UC's `### Level` Cockburn-altitude usage; `LEVEL` is STE100-approved; "kind" is a rejected STE100 word). The resource text does not overclaim: "level" is specmgr's name for the field, mirroring the standard's mapping.

**Option decision (2026-10-26, user).** Option 3 of the design discussion: repurpose `## Level` to the ISO 29148 kind and drop the RFC 2119 keywords entirely — this overrides the issue body's "renamed" wording (recorded in Decisions Made). The field is mandatory; the evolution is in-place on `req/models/v1` per the feat-132-prb-update precedent (existing documents fail to parse until migrated; the `update_req` prompt guides recovery; no dual-schema read support per repo convention). `ReqSummary`/`list_req` stay minimal (user decision). Migration values: all 14 in-repo documents are software requirements on the specmgr tool itself → `SRS`; the packaged example (a vehicle-engine temperature requirement) → `SyRS`.

**Schema mechanics.** `_LEVEL_PATTERN = r"^(BRS|StRS|SyRS|SRS)$"` replaces the RFC 2119 pattern in `req/models/v1/body.py`. `Level` keeps its `MarkdownSection2WithComment` base (the optional `<!-- comment -->` prefix stays legal). Per the feat-189 note, the closed set lives in the `value` Field description, not a schema `enum` (the MCP SDK validates `structuredContent` payloads against the generated output schema; an object-typed `MarkdownParagraph` can never equal a string enum member). The `field_validator` keeps its shape (re.fullmatch against `value.text`). The mixed-case values are deliberate — the standard's own §3.2 spellings.

**Resource shape (mirrors `specmgr://ears`).** `general/data/general_iso29148.md` (packaged markdown) + `general/models/iso29148.py` (`Iso29148` + `parse_iso29148`, parsed on every resource call purely to fail fast on structural drift, result discarded) + `general/resources/iso29148.py` (`@mcp.resource("specmgr://iso29148", ...)`, raw text, `text/markdown`) + registration in `general/resources/__init__.py` and `general/models/__init__.py`. No pyproject change needed — the `biz.dfch.specmgr.general` package-data entry already covers `data/*.md`. Content sections: H1; intro; `## The four requirement specifications` (closed list: abbreviation, full name, standard clause refs, one-line content summary each); `## When to use each` (same order, strict ordered cross-check per the `ears.py` pattern); `## Mapping to specmgr document types` (StRS ↔ `qa` elicitation, SyRS ↔ the `sysrs` aggregator — a REQ with `## Level: SyRS` belongs in a SYSRS `## Requirements` list, SRS ↔ software, BRS ↔ business level, `gol`-adjacent); `## Requirement obligation` (statement phrasing, `specmgr://ears`, the ISO "shall" convention); `## Characteristics of a set of requirements` (the §5.2.6 list, for the deferred SET phase).

**Prompt style rule.** All prompt/data/docstring text describes the current structure in the present tense. Change-history phrasing (e.g. "Level now contains the ISO 29148 kinds and not the RFC 2119 keywords as previously") is forbidden in prompts, the template comment, docstrings, and the resource. Change history lives in the CHANGELOG and this feature README only. The one migration-aware text is the `req_update_instructions.md` recovery directive, written as a present-tense instruction: if `get_req` returns a parse failure naming the `## Level` value, read `specmgr://iso29148` and replace the value with one of BRS/StRS/SyRS/SRS.

**Migration procedure.** For each of the 14 `docs/req/` documents: `get_req(id, raw=True, numbered=True)` → locate the `## Level` value line → generic `update(id, type="req", content, offset, limit)` line-range replace with `SRS` → verify. The packaged example and template are edited as files (`req/data/req_example.md`, `req/data/req_template.md`: comment line + value).

**Touchpoint list (non-exhaustive).** `src/biz/dfch/specmgr/req/models/v1/body.py`; `src/biz/dfch/specmgr/req/data/{req_template.md, req_example.md, req_schema.json, req_create_instructions.md, req_update_instructions.md}`; `src/biz/dfch/specmgr/general/{data,models,resources}`; `src/biz/dfch/specmgr/server.py` (docstring); `tests/req/**` (parser tests, ~12 files carrying `## Level` boilerplate, prompt/template/schema/resource tests); `AGENTS.md`; `docs/api/**`, `docs/GENERATED.md`, `docs/MCP.md`; `CHANGELOG.md`; `pyproject.toml` (version); `docs/req/*.md` (14 files).

**Verification commands.**
- `uv run --frozen ruff format --check && uv run --frozen ruff check`
- `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
- `uv run --frozen pytest -n auto --cov=src --cov-report=`
- `uv run --frozen specmgr schema` (regenerates `docs/req_schema.json` + the `req/data/` package copy)
- `uv run --frozen specmgr docs && uv run --frozen specmgr mcp-docs`

### Related Decisions

- GitHub issue #173 ("REQ: add 'ISO 29148 Requirement Level' and add new SET artifact type") — the source issue for this feature.
- feat-132-prb-update — the in-place breaking `models/v1` evolution precedent (mandatory content added, pre-existing documents fail to parse until repaired, the update prompt guides recovery).
- feat-189 Phase 135 — the closed set lives in the Field description, not a schema `enum` (MCP SDK `structuredContent` validation rationale).
- ADR 356d8781-e446-4c26-917a-eda85648ce9d — raw-markdown cross-cutting resources with model-backed drift guards (the `specmgr://ears`/`specmgr://dtais` shape this resource follows).
- ADR ece4554b-725c-4f76-bc04-5d2b760363d2 — the domain-first layout; the resource lives under `general/` because the ISO 29148 kinds are cross-cutting domain knowledge, not owned by the `req` schema.
- ADR 36905d5b-8057-4294-8665-c7eed5534db0 — the dispatch-only domain convention the deferred SET phase will follow.
- feat-32-sysrs — the existing `sysrs` aggregator (ISO 29148 §9.5) and the source of this repo's prior 29148 clause citations.

### Task List

#### Phase 100: Plan and bookkeeping

- [x] Task 100.100: Design discussion with the user — options 1-3, section naming, mandatoriness, migration values, and terminology verified against the 29148:2018 full text.
- [x] Task 100.110: Author this feat-173 plan — issue #173 reused (no new issue), both work packages kept in this feature, SET deferred to Phase 180.
- [x] Task 100.120: Record the final decisions in the Progress section (including that the drop-RFC-2119 decision overrides the issue body's "renamed" wording).

#### Phase 110: Schema (in-place req/models/v1 evolution)

- [ ] Task 110.100: `req/models/v1/body.py` — `_LEVEL_PATTERN` to `^(BRS|StRS|SyRS|SRS)$`; rewrite the `Level` docstring and the `value` Field description (closed set in the description, ISO 29148 §3.2/§5.4/§9.3-9.6 references, present-tense only); update the `Requirement.level` parameter doc.
- [ ] Task 110.110: `tests/req/models/v1/test_parser.py` — accept the four values; reject MUST/SHOULD/MUST NOT/SHOULD NOT/MAY, lowercase variants, and extra-whitespace values (assert the error carries the pattern).
- [ ] Task 110.120: Update the `## Level` boilerplate in the ~12 `tests/req` tool-test files (test__io, test__paths, test_list_req, test_list_req_glob, test__write, test_doc_cache_wiring, test__cache, test_parse_req, test_create_req, test_get_req) to a valid value.

#### Phase 120: Packaged data

- [ ] Task 120.100: `req/data/req_template.md` — the `## Level` comment names the four kinds; the placeholder value becomes `SyRS`.
- [ ] Task 120.110: `req/data/req_example.md` — `## Level` becomes `SyRS` (the statement is unchanged — its obligation is already in the phrasing).
- [ ] Task 120.120: Regenerate `req/data/req_schema.json` via `specmgr schema` (plus the package-copy pre-commit hook); the schema drift test is green.

#### Phase 130: specmgr://iso29148 resource

- [ ] Task 130.100: Author `general/data/general_iso29148.md` per the Design Notes content section list (the §5.4 mapping sentence and the §5.2.6 list verbatim; the standard clause references; present-tense only).
- [ ] Task 130.110: `general/models/iso29148.py` — `Iso29148` + `parse_iso29148` (the `ears.py` shape: closed-vocabulary list items, strict ordered cross-check).
- [ ] Task 130.120: `general/resources/iso29148.py` + registration in `general/resources/__init__.py` and `general/models/__init__.py` (docstrings updated).
- [ ] Task 130.130: Tests under `tests/general` (the model drift guard and the resource's verbatim return), mirroring the ears/dtais test shapes.

#### Phase 140: Prompts

- [ ] Task 140.100: `req/data/req_create_instructions.md` — the present-tense structure recap (`## Level` = one of BRS/StRS/SyRS/SRS); the `specmgr://iso29148` read-first step; eliciting the kind; obligation in the statement phrasing (the EARS pointer).
- [ ] Task 140.110: `req/data/req_update_instructions.md` — the present-tense recovery directive for a legacy `## Level` value (read `specmgr://iso29148`, replace the value).
- [ ] Task 140.120: `tests/req/prompts/test_create_req.py` (and the update-prompt test, if present) — update the section-name assertions.

#### Phase 150: Migration (same commit as Phases 110-140)

- [ ] Task 150.100: Migrate the 14 `docs/req/` documents `## Level` → `SRS` via generic `update` line-range replaces (coordinates from `get_req(id, raw=True, numbered=True)`).
- [ ] Task 150.110: Verify `list_req` reports `error_count == 0` and all 14 documents parse.

#### Phase 160: Housekeeping

- [ ] Task 160.100: `server.py` docstring (register `specmgr://iso29148`; the req description updated) + AGENTS.md (the `req` bullet's `## Level` meaning; the `general` bullet's resource list).
- [ ] Task 160.110: Regenerate `docs/api/` + `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); both drift checks clean.
- [ ] Task 160.120: `CHANGELOG.md` `[Unreleased]` entry (breaking) + the `pyproject.toml` version bump per the release convention.

#### Phase 170: Quality gate

- [ ] Task 170.100: `ruff format --check` + `ruff check`, `vulture`, full `pytest -n auto --cov=src`, the schema/mcp-docs drift checks — all green; the ACC-005 review gate (no change-history phrasing) over the final diff.

#### Phase 180: SET artifact type (deferred — issue #173 part 2)

- [ ] Task 180.100: Resolve the issue's open design questions with the user (does a SET aggregate its elements or only list them; an owner/responsibility field; the shape of the set-examination resource per §5.2.6).
- [ ] Task 180.110: Design the SET domain per ADR 36905d5b (register in `general/tools/_domains.py`, the generic `update`/`set_status`/`set_classification`/`delete`/`edit`/`validate` dispatch entries, the `set/data/` packaged pair, prompts, tests).
- [ ] Task 180.120: Implement SET (schema, tools, resources, prompts, docs, housekeeping) following the SOP dispatch-only-from-day-one precedent.

## Progress

### Current Status

**As of 2026-10-26**: Plan written; the direction is settled (option 3 — repurpose `## Level` to the ISO 29148 kind, drop RFC 2119, mandatory, in-place v1 evolution, SRS x14 + SyRS example, the `specmgr://iso29148` resource). Implementation (Phases 110-170) not started — awaiting the go-ahead. Phase 180 (SET) is deferred pending its design questions.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26 07:53:18.000Z - Created

Plan written from the 2026-10-26 design discussion. Issue #173 is reused (no new issue created); the REQ ISO 29148 level work is Phases 110-170 and the SET artifact type is deferred to Phase 180 of this same feature. The terminology was verified against the 29148:2018 full text: the standard has no collective word for the four, so `## Level` stands as specmgr's name for the field (see Design Notes).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-26 07:53:18.000Z - Option 3: repurpose ## Level, drop RFC 2119

User decision from the design discussion. This overrides the issue body's wording that the RFC 2119 level "must be renamed": the RFC 2119 keywords are dropped from the schema entirely, and obligation is carried by the requirement statement's phrasing (EARS / `specmgr://ears`). The rejected alternatives: option 1 (keep both, rename RFC 2119 to a dedicated section) and option 2 (keep `## Level` for RFC 2119, add a second section) — option 2 was ruled out mainly because the new section had no non-colliding name (`Type` collides with the frontmatter `type`, `Kind` is a rejected STE100 word, `Category` sits too close to `## Characteristics`).

#### 2026-10-26 07:53:18.000Z - Mandatory field, in-place v1 evolution, same-commit migration

Breaking by construction (mandatory field, new value set). Follows the feat-132-prb-update precedent: in-place `req/models/v1` evolution (no v2, no dual-schema read support per repo convention), the 14 in-repo documents migrated in the same commit, and external documents recovering via the actionable parse error plus the `update_req` recovery directive. The optional-field non-breaking variant was discussed and rejected by the user (mandatory was wanted).

#### 2026-10-26 07:53:18.000Z - Migration values: SRS x14, SyRS for the packaged example

All 14 in-repo REQ documents are software requirements on the specmgr tool itself, so they get `SRS`. The packaged example (a vehicle-engine temperature requirement) gets `SyRS`.

#### 2026-10-26 07:53:18.000Z - ReqSummary/list_req stay minimal

User decision: `list_req` output is unchanged (id/title/status/ref/path only); the ISO 29148 kind is not exposed in the listing, unlike RSK's summary strategy/zone fields.

#### 2026-10-26 07:53:18.000Z - Prompt style: present tense, no change-history phrasing

User instruction: rewritten prompts, the template comment, docstrings, and the resource text describe the current structure only — no phrasing of the form "Level now contains X and not the RFC 2119 keywords as previously". Change history lives in the CHANGELOG and this feature README only. The one migration-aware text is the present-tense recovery directive in `req_update_instructions.md`.

#### 2026-10-26 07:53:18.000Z - Keep both work packages of issue #173 in feat-173

The SET artifact type stays a later phase (180) of this same feature folder rather than a separate feat — one GitHub issue = one feat folder, per the naming convention. Its open design questions (aggregation vs. listing, owner, the §5.2.6 examination resource) are recorded in the Scope/Task List.
