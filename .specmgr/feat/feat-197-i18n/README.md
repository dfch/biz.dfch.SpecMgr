---
classification: null
created: '2026-10-29T11:14:24.992+01:00'
id: feat-197-i18n
status: progress
type: feat
updated: '2026-10-30T13:35:28.000+01:00'
version: 1.0.0
---

# Feature: I18n: Multi-Language Support of the Same Artifact

## Plan

### Overview

Most specmgr whole-body artifacts live as a single file per id under `./docs/{type}/`, holding content in exactly one (implicitly English) language. This feature adds first-class support for multiple language variants of the *same* artifact: the same uuid is reused across every language copy, the document schema (frontmatter fields and body section structure) stays identical regardless of language, and only the prose content is translated. English (EN) remains the default/primary language and keeps its existing, unchanged location (`./docs/{type}/`); other languages are added as `./docs/{type}/{language}/` subfolders. The feature also adds command/skill/agent support for translating an artifact into a new language, detecting drift between a translation and its EN source (structural and staleness), and listing the languages available for a given artifact.

`feat` is explicitly excluded from all of the above: FEAT documents are always EN-only (no translation, no `language` parameter, no `{language}` subfolder). This is a deliberate decision, not an oversight -- `feat`'s folder-per-id addressing (`<base>/<id>/README.md`, `SPECMGR_FEAT_DIR`, hand-rolled `feat/tools/_paths.py`) does not fit the `./docs/{type}/{language}/{id}.md` convention this feature introduces for the other eleven whole-body domains, and feature-planning documents have no translation need. "Every whole-body domain" throughout this plan therefore means the eleven domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs, not all twelve.

### Requirements

- REQ-001: For every whole-body domain except `feat` (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs), a language variant of an artifact is stored at `./docs/{type}/{language}/`, using the exact same filename/id as its EN source (working assumption, to be confirmed in Task 100.100); the existing `./docs/{type}/` location and its contents remain unchanged and continue to mean the default (EN) language. `feat` does not participate in this convention at all -- see REQ-002.

- REQ-002: `feat` is permanently single-language (EN only): no `./docs/feat/{language}/` (or `<base>/<id>/{language}/`) path convention is introduced, no `feat` tool/resource/prompt accepts a `language` parameter, and no `feat` document is ever a translation target or source.

- REQ-003: All language variants of the same artifact share the same `id` (uuid); the `id` is never language-qualified.

- REQ-004: The YAML frontmatter schema and the document's body section headings/order are structurally identical across every language variant of a given domain; only free-form prose content (and, where unavoidable, the literal heading text itself) differs between languages.

- REQ-005: A per-language heading-mapping table resolves a translated section heading back to its canonical English schema key, so parsers/validators keep working against one canonical key set regardless of the file's language.

- REQ-006: `get_<d>`/`list_<d>` (every whole-body domain except `feat`: req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs) accept an optional `language` parameter (default `"en"`); omitting it preserves today's exact behavior and output.

- REQ-007: `create_<d>`/`update`/`edit`/`set_status`/`set_classification`/`delete` (same eleven domains as REQ-006) accept the same optional `language` parameter, writing to (or acting on) the correct `./docs/{type}/{language}/` path for a non-default language while leaving the default-EN behavior unchanged when `language` is omitted. This explicitly includes the generic `edit` tool (surgical exact-match body replacement) alongside `create_<d>`/`update`/`set_status`/`set_classification`/`delete`.

- REQ-008: A caller-supplied `language` value is validated by `general/tools/_path_safety` (or an equivalent new guard) before it becomes part of a resolved filesystem path, using the same path-injection/confinement discipline already applied to `id`, so a malicious or malformed `language` value cannot escape the domain's base directory.

- REQ-009: ADR is explicitly excluded from this feature's scope; no `adr`-domain tool/resource is modified to accept a `language` parameter, and no ADR document is a translation target or source. (ADR's general exclusion from other generic cross-cutting mechanisms in this codebase is inconsistent -- e.g. ADR *is* included in `set_status`, `get_reference_diagram(_all)`, and `list_references` -- so this requirement stands on its own i18n-specific rationale, not on a claimed blanket ADR-exclusion pattern.)

- REQ-010: Closed-vocabulary and schema-constant tokens are never translated and always remain in their canonical English form, regardless of a document's language. This includes (non-exhaustively): frontmatter `status`/`classification` values, RSK's `## Strategy` words (`transfer`/`accept`/`reduce`/`avoid`) and `### Probability {1..5}`/`### Impact {1..5}` `@alias` tokens, VCR's `### AC-NNN (Method): ...` DTAIS method words, and SOP's approval/effectivity lifecycle values. Only free-form prose (and, per REQ-004/REQ-005, section heading text) is in scope for translation. This requirement also extends to regex/`fullmatch()`-pattern-locked English prose fields validated by a code-level `field_validator` rather than treated as free-form text -- e.g. PRB's mandatory `problem_statement` lead paragraph (`prb/models/v1/body.py`): a naive literal translation of such a field would fail its own domain's Pydantic schema, breaking REQ-004's "same schema" guarantee, so each such field needs a documented resolution (a per-language template variant the validator also accepts, or an explicit exemption keeping the field in English) before translation support covers that domain; tracked in Task 100.150.

- REQ-011: A new command/skill/agent provides a translation workflow: given an artifact's `type`/`id` and a target `language`, it produces a new (or updates an existing) language variant from the current EN (or other source-language) content.

- REQ-012: A new command/skill/agent (or tool) lists the languages currently available for a given artifact `type`/`id`.

- REQ-013: Semantic-similarity search (`find_related`/`find_similar_text`) and the cross-reference tools (`list_references`, `get_reference_diagram(_all)`) operate on EN content only for this feature; non-EN language variants are not separately indexed or searched, and a reference resolved by these tools always resolves to the EN variant's path.

- REQ-014: A new command/skill/agent (or tool) detects drift between a translated variant and its EN source: (a) structural drift -- a missing/extra/reordered section relative to the canonical EN schema, and (b) staleness -- the EN source's `updated` timestamp is newer than the translation's own `updated` timestamp.

### Acceptance Criteria

- [ ] ACC-001: For each of the eleven i18n-eligible domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs), creating/reading a non-EN language variant resolves to `./docs/{type}/{language}/{id}.md` (or the domain's existing filename convention under that subfolder), while EN continues to resolve to the existing `./docs/{type}/{id}.md` path, unchanged. `feat` is not exercised by this AC (see ACC-002).

- [ ] ACC-002: No `feat` tool, resource, or prompt accepts a `language` parameter; `get_feat`/`list_feat`/`create_feat`/`set_feat_id` behave identically before and after this feature ships, and no `./docs/feat/{language}/`-shaped (or `<base>/<id>/{language}/`-shaped) path is ever created or read.

- [ ] ACC-003: Two language variants of the same artifact have identical `id` values in their frontmatter.

- [ ] ACC-004: A translated document's section headings, even if rendered in the target language, resolve via the heading-mapping table to the same canonical schema keys the EN parser uses (REQ-004/REQ-005).

- [ ] ACC-005: Calling `get_<d>(id, language="de")` for the pilot domain (`dec`, Task 100.140) returns the German variant's content; calling `get_<d>(id)` (no `language`) is unaffected and still returns the EN content exactly as before this feature.

- [ ] ACC-006: Calling, for the pilot domain (`dec`) with `language="de"`, each of `create_<d>`, `update`, `edit`, `set_status`, `set_classification`, and `delete` writes to (or acts on) the German variant's path only, leaving the EN variant's file content and `updated` timestamp untouched; this AC is satisfied only once all six tools have been exercised this way, not just one of them.

- [ ] ACC-007: Calling `list_<d>(language="de")` (or equivalent) for the pilot domain (`dec`) lists only the German variants that exist, and omitting `language` continues to list the EN variants exactly as before this feature; writing or reading a translation never duplicates or changes the shared `id`.

- [ ] ACC-008: A new command/skill/tool reports the set of `language` codes currently available for a given artifact `type`/`id` (REQ-012), including at least `"en"`.

- [ ] ACC-009: A drift-detection tool run against a deliberately out-of-sync translation reports both the structural mismatch and the staleness condition.

- [ ] ACC-010: A translation command run against an EN artifact produces a new, schema-valid language variant sharing the same id.

- [ ] ACC-011: A translated document validates against the exact same Pydantic schema as its EN counterpart for that domain (split out of the former compound ACC-004, REQ-004).

- [ ] ACC-012: Closed-vocabulary/schema-constant field values and tokens (REQ-010) remain in canonical English in a translated document (split out of the former compound ACC-004, REQ-010).

- [ ] ACC-013: A `language` value containing a path-traversal or path-injection payload (e.g. `../../etc`) is rejected before it becomes part of a resolved filesystem path, by the same `_path_safety`-style guard already applied to `id` (REQ-008).

- [ ] ACC-014: `find_related`/`find_similar_text`/`list_references`/`get_reference_diagram`/`get_reference_diagram_all` never resolve, enumerate, or index a `{language}` subfolder entry; every reference/similarity hit continues to resolve to the EN variant's path only (REQ-013).

- [ ] ACC-015: No `adr` tool, resource, or prompt accepts a `language` parameter; `adr` document behavior is unchanged before and after this feature ships (REQ-009, mirrors ACC-002 for `feat`).

### Scope

#### Included

- Directory convention `./docs/{type}/{language}/` for non-default languages; EN stays at `./docs/{type}/`.

- Shared-uuid, shared-schema multi-language model for every whole-body domain except `feat` (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs).

- Per-language section-heading mapping table resolving translated headings to canonical schema keys.

- `language` parameter plumbed through the relevant read tools (`get_<d>`, `list_<d>`) and write tools (`create_<d>`, `update`, `edit`, `set_status`, `set_classification`, `delete`) for the same eleven domains.

- Path-injection/confinement validation of the `language` value (REQ-008), alongside the existing `id` validation in `general/tools/_path_safety`.

- A translation command/skill/agent.

- A drift-detection command/skill/agent (structural + staleness).

- A language-listing command/skill/agent (or tool) for a given artifact.

#### Explicitly Out Of Scope

- The `feat` domain: FEAT documents are permanently EN-only. No `language` parameter, no `{language}` subfolder, no translation/drift/listing support for `feat` -- see REQ-002/ACC-002.

- The `adr` domain: ADR stays single-language and out of scope for this feature specifically (REQ-009); this is an independent, i18n-specific decision, not a restatement of a general ADR-exclusion pattern -- ADR does participate in other generic cross-cutting mechanisms (e.g. `set_status`, `get_reference_diagram(_all)`, `list_references`) that this feature does not touch.

- Any guarantee of machine-translation quality, fluency, or semantic accuracy -- this feature provides the mechanism/plumbing, not a translation-quality assurance.

- RTL layout or any UI/rendering-level localization concern -- this is document-content i18n, not UI localization.

- Translation of closed-vocabulary/schema-constant tokens (REQ-010) -- these always stay in canonical English.

- Multi-language indexing/search for semantic similarity or cross-reference resolution (REQ-013) -- `find_related`/`find_similar_text`/`list_references`/`get_reference_diagram(_all)` continue to operate on EN content only.

### Dependencies

#### Depends On

- None.

### Design Notes

Open design questions to resolve during Phase 100 below:

- Exact on-disk filename for a language variant (same basename as EN, just under the `{language}` subfolder, is the working assumption; confirmed/finalized in Task 100.100).
- Exact shape and storage location of the per-language heading-mapping table (e.g. one mapping file per language under a shared config location, vs. embedded per-domain).
- Whether `language` codes follow a fixed vocabulary (e.g. ISO 639-1 two-letter codes) or are free-form.
- How `list_<d>` should behave when asked to list across all languages at once vs. a single language.
- Pilot domain for Phase 110-130/ACC-005 through ACC-007: **`dec`**, chosen for its dispatch-only architecture (no per-domain `update_dec`/`set_status_dec`/`validate_dec` tools to special-case) and its simple `models/md`-based body, recorded here per Task 100.140.
- Whether `feat`'s bespoke dual `DocCache` (clean/dirty, `feat/tools/_cache.py`) needs any change at all given `feat` is out of scope for this feature (current assumption: no change, since `feat` never gains a `language` parameter) -- confirm explicitly in Task 100.100 rather than leaving it implicit.
- Closed-vocabulary/schema-constant tokens (REQ-010) are never translated; confirm this decision is reflected consistently in the heading-mapping-table design (Task 100.110) and the translation workflow (Phase 140), since a naive heading-text translation must not also translate values inside those headings (e.g. VCR's `(Method)` suffix, RSK's `{1..5}` values).
- `general/tools/_doc_paths.py`'s `iter_doc_paths` performs a non-recursive `base_dir.glob("*.md")` scan; as long as `{language}` variants live in a nested subfolder, this existing flat scan (used by every domain's own `list_<d>`/`find_doc_path_by_id`, plus `list_references`/`find_related`/`get_reference_diagram(_all)`) will not descend into it, preserving REQ-013's EN-only behavior "for free" by directory-layout choice alone. This must be explicitly confirmed (not just assumed) and pinned by a test in Task 100.100/Task 150.100 so a future switch to a recursive glob cannot silently break REQ-013.
- `DocCache` already keys every entry by the resolved `Path`, not by bare `id` (`general/tools/_doc_cache.py`); since a language variant necessarily lives at a distinct path once Task 100.100/110.100 make path resolution language-aware, two languages of the same id already get independent, non-colliding cache entries without any `DocCache` code change. Task 120.110 is scoped as a confirmation/test of this, not a `DocCache` code change, unless Phase 100 design turns up a reason that assumption doesn't hold.
- `sysrs` (and potentially other domains) may have non-`.md` sibling assets in the same base directory (e.g. an appendix PDF next to a `.md` file). Whether/how such sibling assets participate in the `{language}` subfolder convention is out of scope for this feature unless Task 100.100 finds an existing convention that depends on it; default assumption is that this feature only ever creates/reads `.md` files, and non-`.md` siblings are untouched and unaffected.

### Related Decisions

- ADR 38efdb66-8025-45c5-bbe8-45b25fc7a772 ("Multi-language artifact variants: directory layout, heading-mapping table, and language vocabulary"): captures the Phase 100 design -- the `docs/{type}/{language}/` subfolder convention with the EN source's exact basename as the single filename authority, the per-language JSON heading-mapping table (format, storage, closed domain, and the pre-parse resolution algorithm), the ISO 639-1-shaped language vocabulary and its `_path_safety` validation, the single-language-per-call `list_<d>` semantics, and the confirmed design facts (non-recursive scan keeps REQ-013 true by layout, `DocCache` Path keying needs no change, `feat`/`adr` unchanged, the `prb` `problem_statement` English exemption).

### Task List

#### Phase 100: Design -- Directory Layout, Heading-Mapping Table, Language Vocabulary

- [x] Task 100.100: Finalize the on-disk filename/path convention for a language variant (`./docs/{type}/{language}/{id}.md`) and confirm it against the eleven i18n-eligible domains' existing path-resolution code (`general/tools/_doc_paths.py`); explicitly confirm and record that `feat/tools/_paths.py` and `feat/tools/_cache.py` need no change, since `feat` is permanently out of scope for this feature (REQ-002).

- [x] Task 100.110: Design the per-language heading-mapping table format and storage location, and how a parser resolves a translated heading back to its canonical schema key; explicitly confirm that closed-vocabulary/schema-constant tokens embedded in or alongside headings (REQ-010, e.g. VCR's `(Method)` suffix, RSK's `Probability`/`Impact`/`{1..5}` tokens) are excluded from translation and the mapping table only ever maps heading *text*, never those tokens.

- [x] Task 100.120: Decide the language-code vocabulary (e.g. ISO 639-1) and where it is validated.

- [x] Task 100.130: Write an ADR capturing the directory-layout and heading-mapping-table design decisions.

- [x] Task 100.140: Record `dec` as the pilot domain for Phases 110-130 and ACC-005/ACC-006/ACC-007 (decision already made; see Design Notes).

- [x] Task 100.150: For each i18n-eligible domain, identify every regex/`fullmatch()`-pattern-locked English prose field (e.g. PRB's `problem_statement` lead paragraph) and document its resolution per REQ-010: either a per-language template variant the validator accepts, or an explicit exemption keeping the field in English in every language.

#### Phase 110: Path Resolution & Read-Side Plumbing (Pilot Domain: `dec`)

- [x] Task 110.100: Extend `general/tools/_doc_paths.py` to resolve a document path given `type`/`id`/optional `language`, and extend `general/tools/_path_safety` to validate the `language` value (REQ-008) with the same path-injection/confinement discipline already applied to `id`; confirm `iter_doc_paths`'s non-recursive scan does not descend into `{language}` subfolders (ACC-014).

- [x] Task 110.110: Add the optional `language` parameter to `get_dec`/`list_dec`, defaulting to `"en"` with unchanged behavior when omitted.

- [x] Task 110.120: Extend the markdown parser layer to apply the heading-mapping table when parsing a non-EN document, exercised against `dec`.

#### Phase 120: Write-Side Plumbing (Pilot Domain: `dec`)

- [x] Task 120.100: Add the optional `language` parameter to `create_dec` and the generic `update`, `edit`, `set_status`, `set_classification`, and `delete` tools, exercised against `dec` (ACC-006 requires all six tools, not just one).

- [x] Task 120.110: Confirm (do not implement unless proven necessary) that `DocCache`'s existing `Path`-keyed cache entries already keep different languages of the same `dec` id from colliding once Task 100.100/110.100 make path resolution language-aware; add a `DocCache` code change only if this verification finds a real collision.

- [x] Task 120.120: Test (REQ-003 end-to-end) that writing/reading a `dec` translation never changes or duplicates the shared `id`, and that the EN variant's content/`updated` timestamp is untouched by a write to a non-default language.

#### Phase 125: Read/Write Plumbing -- Remaining Domains

- [ ] Task 125.100: Add the optional `language` parameter to `get_<d>`/`list_<d>` for the remaining ten i18n-eligible domains (req, uc, tsk, qa, prb, gol, rsk, sop, vcr, sysrs).

- [ ] Task 125.110: Add the optional `language` parameter to `create_<d>` for the remaining ten i18n-eligible domains; the generic `update`/`edit`/`set_status`/`set_classification`/`delete` tools already cover every domain from Task 120.100 (they are dispatch-based, not per-domain).

- [ ] Task 125.120: Confirm the Task 120.110 `DocCache` collision analysis generalizes to every remaining domain without per-domain changes; add any domain-specific fixes found. Also apply each domain's Task 100.150 resolution (template variant or exemption) for any regex-pattern-locked prose fields found in that domain's schema.

#### Phase 130: Translation Command/Skill/Agent

- [ ] Task 130.100: Design and implement the translation command/skill (or MCP tool) that produces/updates a target-language variant from a source document; explicitly exclude closed-vocabulary/schema-constant tokens (REQ-010) from translation.

- [ ] Task 130.110: Add an OpenCode skill and/or command surface for the translation workflow.

#### Phase 140: Drift Detection & Language Listing

- [ ] Task 140.100: Implement structural drift detection (missing/extra/reordered sections vs. the canonical EN schema).

- [ ] Task 140.110: Implement staleness detection (EN `updated` timestamp newer than the translation's `updated`).

- [ ] Task 140.120: Implement a language-listing tool/command for a given artifact `type`/`id` (REQ-012).

- [ ] Task 140.130: Add an OpenCode skill and/or command surface for drift-detection and language-listing.

#### Phase 150: Tests & Documentation

- [ ] Task 150.100: Unit tests for path resolution, read/write `language` plumbing, path-safety validation of `language` (ACC-013), and cache behavior across `dec`, then extended to every remaining i18n-eligible domain; include a regression test confirming no `feat` tool/resource/prompt gained a `language` parameter (ACC-002) and no `adr` tool/resource/prompt gained a `language` parameter (ACC-015).

- [ ] Task 150.110: Unit tests for the translation, drift-detection, and language-listing workflows, including a test that closed-vocabulary/schema-constant tokens are never translated (REQ-010, ACC-012) and a test that a translated document validates against its domain's exact EN schema (ACC-011).

- [ ] Task 150.115: Unit tests confirming `find_related`/`find_similar_text`/`list_references`/`get_reference_diagram`/`get_reference_diagram_all` never resolve or index a `{language}` subfolder entry and always resolve references to the EN variant's path (REQ-013, ACC-014).

- [ ] Task 150.120: Update `AGENTS.md`, `README.md`, and generated docs (`specmgr docs`) to describe the new `language` parameter and i18n workflows, explicitly noting `feat`'s permanent exclusion.

## Progress

### Current Status

**As of 2026-10-30**: Phase 120 (write-side plumbing) complete for the pilot domain `dec` -- `create_dec` (optional `language` + `id` of the EN source) and the generic `update`/`edit`/`set_status`/`set_classification`/`delete` tools (optional `language`, default `"en"`) act on a `docs/dec/{language}/` variant file only, leaving the EN file's bytes and `updated` timestamp untouched (ACC-006, all six tools); every other type (and `feat`/`adr` permanently) rejects a non-default `language` before any filesystem access; the shared id is never changed or duplicated (REQ-003); `DocCache` needed no code change (Task 120.110 confirmed). EN behavior is byte-identical. Phase 125 (remaining ten domains) is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-30T13:35:28.000+01:00 - Phase 120 (write-side plumbing) complete: `create_dec` + generic `update`/`edit`/`set_status`/`set_classification`/`delete` honor `language` for `dec`

Implemented ADR 38efdb66's write-side contract for the pilot domain `dec` (Tasks 120.100/120.110/120.120). Write side only: no other domain's `create_<d>`, no `feat`/`adr` module, no `validate`/similarity/reference tool was touched.

- **Generic tools (Task 120.100, ACC-006/ACC-013):** `update`, `edit`, `set_status`, `set_classification`, and `delete` gained an optional `language: str = "en"` (appended last). A new shared guard `general/tools/_language_guard.guard_language(type, language)` runs right after `validate_id`, before any filesystem access and before dispatch: `assert_language` shape guard first (for *every* type and value, also on the rejection paths), then default-language pass-through, then -- for `dec` -- the heading-table resolve (fail-fast for a shape-valid code without a table, e.g. `fr`), and for every other type a `ValueError`: *permanent* wording for `feat`/`adr` ("`feat` documents are always English", REQ-002/REQ-009) and "language 'de' is not yet supported for type 'req'" for the ten domains Phase 125 will enable. The default language dispatches through the unchanged `_ADAPTERS` table with the unchanged argument shape (byte-identical); a non-default language goes through a new per-tool `_LANGUAGE_ADAPTERS` table (today `{"dec"}`, asserted equal to `LANGUAGE_AWARE_DOMAINS` so guard and dispatch cannot drift).
- **`dec` adapters:** each takes `language` and resolves `dec_base_dir(language)`, so the id-scan, the parse-failure probe, and `assert_within` all run against the variant's own directory (the basename is never re-derived, ADR item 2); only that one variant file is written/unlinked. Content validation of a variant goes through the new `parse_dec_body(content, *, language=None)` (in `dec/models/v1/parser.py`, the body-only half of `parse_dec`, which now delegates to it), so translated headings are accepted exactly as the read side accepts them while the persisted text stays the caller's raw body byte-for-byte; with the language omitted it is byte-identical to the former `Decision.from_text(format_text(content))`. The `ParseFailureResult` / `ValidateResult` / `InvalidStatusResult` non-raising channels and their guard order are unchanged for the language path; a truly-absent DE id raises `DecNotFoundError` even when the EN document exists.
- **`create_dec` variant mode (Task 120.100):** new optional `language` (default `"en"`) and `id` parameters. EN: `id` must be omitted (a fresh id is assigned, flat file -- byte-identical). Non-default language: `id` -- the *shared id of the EN source* -- is required (REQ-003: a variant never gets a fresh id), the EN source must exist (`DecNotFoundError` with an actionable "a language variant requires its 'en' source" message), the variant is written to `docs/dec/{language}/` under the EN source's exact basename (ADR item 2) with `status="draft"` and fresh `created`/`updated`, the body is validated through the language's table and persisted verbatim, and an existing variant is never overwritten (`FileExistsError`). Missing/misused `id`, malformed `language`, or a table-less language are `ValueError`s before any filesystem access; content-validation failure stays the non-raising `ValidateResult`. See Decisions Made.
- **Locks (Task 120.100):** `dec/tools/_lock.dec_lock_key(id, language=None)` returns the bare id for EN (exactly today's key) and `"<id>/<language>"` for a variant, so the language variants of one id lock independently and never collide with an id key; every `dec` adapter and `create_dec` wrap their sequence in `dec_lock(dec_lock_key(id_, language))`. `dec_lock` itself keeps its single-argument signature.
- **`DocCache` (Task 120.110) -- confirmed, no code change:** entries are keyed by the resolved `Path` and a variant lives at a distinct path, so write-warming (`read_dec(path)` after each write, path-derived language), invalidation (`invalidate_dec_cache(path)` on delete) and the domain-wide reconcile (Phase 110) already keep EN and DE independent. No real collision was found; pinned by tests (one entry per path; interleaved reads/writes never cross-leak; a write to one language leaves the other's cache entry object identical; delete of DE leaves EN cached and readable; scanning one language does not evict the other).
- **Tests (Task 120.120, REQ-003):** an end-to-end test creates EN, creates the DE variant, updates/edits/sets-status the DE variant and reads both through `get_dec`/`list_dec`: the id is identical, each language directory lists exactly that one id, the file basenames match, and the EN bytes and `updated` are untouched after every step.
- **Quality gate:** full suite green (4974 passed / 18 skipped; +60 new tests, no existing test modified); `ruff format --check`, `ruff check`, `vulture` clean; `specmgr docs` + `specmgr mcp-docs` regenerated; `specmgr schema` (+ the 12 per-domain package copies) all unchanged.

#### 2026-10-30T09:47:00.000+01:00 - Phase 110 (read-side plumbing) complete: guard, path resolution, heading table, and `get_dec`/`list_dec` `language` for `dec`

Implemented ADR 38efdb66's read-side contract for the pilot domain `dec` (Tasks 110.100/110.110/110.120). Read side only: `get_dec`/`list_dec` gained the optional `language` parameter (default `"en"`, unchanged behavior when omitted); `parse_dec` derives the language from the file's path position. No write tool, no other domain, and no `feat`/`adr` surface was touched.

- **Language guard (Task 110.100, REQ-008/ACC-013):** `general.tools._path_safety.assert_language` (+ module constants `LANGUAGE_PATTERN` `^[a-z]{2}$` and `DEFAULT_LANGUAGE` `"en"`) validates a caller-supplied `language` by fullmatch before any filesystem access, in the same pre-guard position as `id`. Shape-only (open set); the closed set (table existence) is enforced separately at parse/write time. A payload like `"../../etc"`, `"de/x"`, `""`, or `"DE"` is rejected with an actionable `ValueError`.
- **Path resolution (Task 110.100, ADR items 1/2):** `general.tools._doc_paths.doc_base_dir`/`ensure_doc_base_dir` take an optional `language` -- omitted/`"en"` resolves to today's flat `docs/{type}/` byte-identically, any other validated code to `docs/{type}/{language}/`. New `language_for_doc_path` recovers the language a document path is encoded by (its position), and `iter_doc_paths_all_languages` yields the domain-wide live listing (flat + every shape-valid `{language}` subdirectory) for cache reconcile. `iter_doc_paths` stays non-recursive and never descends into `{language}` subfolders (ACC-014, pinned by a new unit test).
- **Heading-mapping table (Task 110.120, ADR items 3/4/5):** the packaged `general/data/headings/de.json` (114 entries) maps German fixed-text headings to canonical English. The closed set was derived systematically from the eleven i18n-eligible domains' document models (every `MarkdownSection` alias that is LITERAL, SPACE_SEPARATED, or a REGEX with no free-text group; data-carrying headings like `Option {N}:`/`Step {N}:`/`AC-{NNN}`/timestamp-led entries carry no entry, REQ-010). New `general.models.heading_table` provides the lazy once-per-process loader (rejects non-pairwise-distinct values and a missing table with an actionable error; no file for `en`), the omitted/EN-aware `resolve_heading_table`, and the fence-aware (``` / ~~~) line-based `normalize_heading_lines` pre-pass.
- **Parser wiring (Task 110.120, ADR item 5):** the pre-pass is wired at `dec`'s text-to-model parse boundary (`dec.models.v1.parse_dec` gained an optional `language` keyword) -- after mdformat normalization, before the unchanged `models/md` engine. `dec.tools._cache.read_dec` derives the effective language from the file's own position, so every reader (get/list/parse) parses a variant with its table with no signature change, and `DocCache`'s path-keyed entries keep languages independent (ADR item 9 -- no cache code change). The generic disk-free `validate` tool gains no `language` parameter (stays EN/canonical-only).
- **`get_dec`/`list_dec` (Task 110.110, ADR items 5/6/7):** both take `language: str = "en"`. Omitted/`"en"` is byte-identical to today. A non-default `language` is shape-guarded and its table resolved up front (before any filesystem access); `get_dec` reads the variant (raw returns the on-disk body verbatim, structured parses through the table to canonical keys), and the `ParseFailureResult` byte-identity contract holds for a broken DE variant against `list_dec(language="de")`. `list_dec(language="de")` lists only the DE variants; the row shape is unchanged (no language column).
- **Package data:** `pyproject.toml`'s `biz.dfch.specmgr.general` package-data glob extended from `data/*.md` to also ship `data/headings/*.json`.
- **Quality gate:** full suite green (4912 passed / 18 skipped, up from the pre-phase baseline, no test modified except where a signature change strictly required it -- none did); `ruff format --check`, `ruff check`, `vulture` clean; `specmgr docs` + `specmgr mcp-docs` regenerated; `specmgr schema` all 12 domains unchanged.

#### 2026-10-29T21:06:25.512+01:00 - Phase 100 (design) complete: layout, mapping table, and language vocabulary settled in ADR 38efdb66

- **Filename/basename rule (Task 100.100):** a language variant lives at `docs/{type}/{language}/<type>-<uuid>-<slug>.md` under the EN source's *exact* basename -- the slug always derives from the EN title (`slugify(EN title)`), never from a variant's translated title; a non-default-language `create_<d>` therefore requires the EN source (same `id`) to exist on disk first, while the other write tools only id-scan the language subfolder (no basename re-derivation); `find_parse_failure`'s stem matching (`-{id}-` in the stem / `{id}-` prefix) works unchanged for every language. Confirmed, recorded in the ADR: `feat/tools/_paths.py` and `feat/tools/_cache.py` need **no** change (REQ-002 -- `feat`'s folder-per-document addressing is unreachable by the `{language}` convention), and only `.md` files participate in the convention (non-`.md` siblings, e.g. the `.pdf` files next to the `.md` under `docs/sysrs`, are untouched).
- **Heading-mapping table (Task 100.110):** one flat JSON object per language mapping `<translated heading text> -> <canonical English heading text>`, stored in shared cross-domain package data at `general/data/headings/<language>.json` (not per-domain -- shared headings like `## More Information`, `## Tags`, `## Source`, `## Updates`, the RASCI H3s, and the cross-reference H3s recur across 4+ domains). The table's domain is closed and machine-derivable: exactly the fixed-text heading aliases (LITERAL / SPACE_SEPARATED / REGEX-without-free-text-group) of the i18n-eligible domains; data-carrying regex headings (`Option {N}:`, `Step {N}:`, `AC-{NNN} ({Method})`, `Extension {N}.`, timestamp-led update entries, RSK's `Probability {1..5}`/`Impact {1..5}`) hold no entry -- their schema-constant tokens are never translated (REQ-010) and stay canonical in the variant file itself, while their free-text data (option/step/criterion/update titles) matches the alias's own `.+` group in any language. Resolution algorithm: a fence-aware, line-based heading-normalization pre-pass at each domain's parse boundary (`normalized = table.get(heading_text, heading_text)` per heading line, outside fenced code blocks) before the *unchanged* `models/md` engine runs; the parsed model holds canonical heading text (ACC-011), the on-disk file keeps its translation (`raw=True` reads return it verbatim); the loader rejects duplicate values (two canonical headings must not translate to the same string); a Phase 150 drift test pins each table against the model-derived closed set; a language with no table file is shape-valid but unusable (actionable error at parse/write time).
- **Language vocabulary (Task 100.120):** ISO 639-1-shaped lowercase two-letter codes (`^[a-z]{2}$`), validated by a new guard in `general/tools/_path_safety.py` (alongside `validate_id`) before any filesystem access -- REQ-008/ACC-013, the same path-injection/confinement discipline as `id`; the set is OPEN at the guard level (any shape-valid code passes) and closed at the table level (codes without a table are rejected at parse/write time), so adding a language means adding one JSON file, no code or guard change; every `language` parameter defaults to `"en"`, and explicit `"en"` is allowed, resolving to the flat `docs/{type}/` directory (EN is the only language without a subfolder).
- **`list_<d>` semantics:** single language per call -- omitted / `"en"` = today's exact behavior (scans the flat directory), `language="xx"` = lists only the existing `xx` variants (ACC-007); deliberately NO "all languages" mode (`DocSummary` rows carry no language column and would repeat ids; per-artifact language discovery is REQ-012's dedicated tool, Phase 140, ACC-008).
- **Task 100.150 inventory:** exactly **one** regex-locked English prose field across all i18n-eligible domains -- `prb`'s mandatory `problem_statement` lead paragraph (`prb/models/v1/body.py`, `_PROBLEM_STATEMENT_PATTERN`) -- resolved as **(b) explicit exemption**: it stays in canonical English in every language variant (the translation workflow must not touch it; drift detection must ignore it); every other domain: none found (all other regex-locked tokens are closed vocabulary, cross-reference structure, heading text, language-neutral data, or UC-diagram-renderer-only). See the Decisions Made table below.
- **Confirmed design facts (ADR items 8-10):** `general/tools/_doc_paths.py`'s `iter_doc_paths` non-recursive `*.md` glob never descends into `{language}` subfolders, so every EN-only consumer (each domain's `list_<d>`/`find_doc_path_by_id`, plus `list_references`, `find_related`/`find_similar_text`, `get_reference_diagram(_all)`) preserves REQ-013 "for free" by directory layout -- to be pinned by a Phase 150 regression test (Task 100.100/150.100); `DocCache` keys entries by the resolved `Path` (never bare `id`), so two languages of the same id already get independent non-colliding entries with **no** `DocCache` code change (Tasks 120.110/125.120 are confirmation/test tasks); `adr` stays unchanged (REQ-009/ACC-015).
- **ADR written (Task 100.130):** 38efdb66-8025-45c5-bbe8-45b25fc7a772, "Multi-language artifact variants: directory layout, heading-mapping table, and language vocabulary" (`docs/adr/38efdb66-8025-45c5-bbe8-45b25fc7a772-multi-language-artifact-variants-directory-layout-heading-ma.md`, created via the `create_adr` MCP tool per ADR 898bfcd0, `specmgr adr-toc` regenerated).

#### 2026-10-29T13:00:00.000+01:00 - Second refinement pass: E/G/D/I findings applied

Applied a second `refine-feature` review's findings: reframed Task 120.110 from a
`DocCache` code change to a confirmation/test task, since `DocCache` already keys by
resolved `Path`, not bare `id` (E1); extended REQ-010 to cover regex/`fullmatch()`-
pattern-locked English prose fields (e.g. PRB's `problem_statement`) and added Task
100.150 to resolve each one per-domain (G1); split the former compound ACC-004 into
ACC-004/ACC-011/ACC-012, and added ACC-013 (REQ-008 path-safety), ACC-014 (REQ-013
EN-only similarity/cross-reference), and ACC-015 (REQ-009 ADR-exclusion regression,
mirroring ACC-002) (G2, G6, I2); documented the non-recursive `iter_doc_paths` glob
scan as the mechanism that keeps REQ-013 true "for free," with an explicit
confirmation/test in Task 100.100/150.100 (G3); documented the `sysrs` non-`.md`
sibling-asset question in Design Notes with a default "untouched" assumption (G4);
reworded ACC-006 to require all six write tools, not just one (per "or" phrasing)
(G5); resolved the REQ-001-vs-Design-Notes filename discrepancy by marking the
filename convention a working assumption pending Task 100.100 confirmation in both
places (D1); trimmed Dependencies > Depends On back to a plain "None" and moved the
phased-rollout rationale into Design Notes/Task List context only (I1); resolved the
pilot domain to `dec` (dispatch-only architecture) in Design Notes and Task 100.140,
and propagated the concrete domain name through Phase 110/120/125 task titles and
text in place of "the pilot domain" indirection (I3).

#### 2026-10-29T12:00:00.000+01:00 - Refinement pass: feat excluded, scope/task fixes applied

Applied a `refine-feature` review's Errors/Gaps/Discrepancies/Improvements findings:
`feat` is now explicitly and permanently excluded from this feature (REQ-002/ACC-002 --
FEAT documents stay EN-only, no `language` parameter anywhere in the `feat` domain); REQ-001/
REQ-006/REQ-007 domain lists corrected to the eleven i18n-eligible domains (not twelve);
REQ-007 now explicitly includes the generic `edit` tool; added REQ-008 (`language`
path-injection validation via `_path_safety`), REQ-010 (closed-vocabulary/schema-constant
tokens are never translated), REQ-013 (similarity/cross-reference tools stay EN-only); REQ-009's
ADR-exclusion rationale corrected (ADR is not uniformly excluded from other generic mechanisms);
added ACC-002, ACC-006, ACC-007, ACC-008 closing the AC gaps around `feat` exclusion,
write-tool coverage, and language-listing; Scope/Design Notes/Dependencies/Related Decisions
updated to match; Task List gained Task 100.140 (pilot-domain decision), a new Phase 125
(remaining-domains rollout, split out of the former all-at-once Phase 110/120 tasks), and
explicit path-safety/`edit`-tool/REQ-003-end-to-end tasks.

#### 2026-10-29 11:14:24.992+01:00 - Created

Feature drafted from GitHub issue #197 ("I18n: multi-language support of the same artifact"). Directory layout `./docs/{type}/{language}/` locked in (EN unchanged at `./docs/{type}/`); shared-uuid/shared-schema model confirmed; ADR excluded from scope; translation, drift-detection (structural + staleness), and language-listing all confirmed in scope for this feature, with both read- and write-side `language` parameter support.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-30T13:35:28.000+01:00 - Phase 120 implementation decisions (write-side plumbing for `dec`)

Implementation-level decisions made while executing Phase 120, all within the ADR 38efdb66 contract (no deviations):

| decision | choice | rationale |
| --- | --- | --- |
| `create_dec` shared-id mechanism (REQ-003) | New optional `id` parameter = the shared id of the EN source; required with a non-default `language`, rejected (`ValueError`) with the default language | `create_dec` today assigns a fresh server-side id, which a variant must never get; reusing the established `id` parameter name (same meaning as in every other tool: "the document's identifier, shared across languages") is the minimal explicit mechanism -- no id inference, no id embedded in the submitted body, EN create stays byte-identical because `id` is forbidden there |
| Variant frontmatter | Fresh `created`/`updated`, `status="draft"`, `type="dec"`, current schema `version`, no `classification` -- the EN frontmatter is not copied | Matches every other create (status never caller-supplied on create; the translation workflow of Phase 130 can set status/classification afterwards via the generic tools); copying EN's status would silently claim a translation is as reviewed as its source |
| Order of checks in `create_dec` | Language/`id` argument guards and the table resolve (all pre-filesystem `ValueError`s) -> body validation (non-raising `ValidateResult`) -> EN-source lookup (`DecNotFoundError`) -> existing-variant guard (`FileExistsError`) | The `create_feat` precedent: "first in execution order wins" with content validation ahead of the filesystem-dependent guards; every pure-argument error is raised before any filesystem access |
| Existing-variant guard | `FileExistsError` under the variant's own lock, checked after the EN source lookup | A variant must never be overwritten (use `update`/`edit` with the language instead); holding the per-language lock makes check-and-write atomic against concurrent mutation of that variant |
| Missing-EN-source error | `DecNotFoundError` (the domain's established not-found exception) with an actionable message | The id the caller supplied does not resolve to any (parseable) EN document -- exactly the not-found condition `DecNotFoundError` already means; a message naming ADR item 2's "variant requires its EN source" makes the cause explicit |
| Body-only validation helper | `parse_dec_body(content, *, language=None)` in `dec/models/v1/parser.py`; `parse_dec` delegates to it | One body-validation choke point shared by `create_dec` and the generic `update`/`edit` adapters (and the read side), so the write side accepts translated headings exactly as the read side does; the default path is byte-identical to `Decision.from_text(format_text(content))` |
| Guard module | New `general/tools/_language_guard.py` (`guard_language`, `LANGUAGE_AWARE_DOMAINS`) shared by the five generic tools | One place for the shape-guard-then-support-then-table order and for the permanent (`feat`/`adr`) vs temporary (not-yet-enabled) wording; Phase 125 enables a domain by adding it to `LANGUAGE_AWARE_DOMAINS` and the per-tool `_LANGUAGE_ADAPTERS` (an import-time assert keeps the two in sync) |
| Dispatch shape | Default language -> the unchanged `_ADAPTERS` table with the pre-i18n arguments; non-default -> per-tool `_LANGUAGE_ADAPTERS` with the language as the last argument | Keeps the EN path literally untouched (existing tests that spy on adapters/locks stay green) instead of threading a `language` argument through all twelve adapters of five tools; Phase 125 can collapse the two tables once every domain is enabled |
| Per-language lock | `dec_lock_key(id, language)`: bare id for EN, `"<id>/<language>"` for a variant; `dec_lock` keeps its one-argument signature | The variants of one id are distinct files, so they should neither race with nor block on each other, and the EN lock key stays exactly today's (an existing test spies on `dec_lock(id)`); an id never contains `/`, so keys cannot collide |
| Task 120.110 -- `DocCache` | **No `DocCache` code change.** Confirmed by test: path-keyed entries, write-warming via the path-deriving `read_dec`, `invalidate_dec_cache(path)` on delete, and the Phase 110 domain-wide reconcile already isolate languages | The verification found no real collision, which is the plan's condition for making no change; the tests pin the property so a future keying change cannot silently break it |

#### 2026-10-30T09:47:00.000+01:00 - Phase 110 implementation decisions (read-side plumbing for `dec`)

Implementation-level decisions made while executing Phase 110, all within the ADR 38efdb66 contract (no deviations):

| decision | choice | rationale |
| --- | --- | --- |
| Guard home + constants | `assert_language` + `LANGUAGE_PATTERN` (`^[a-z]{2}$`) + `DEFAULT_LANGUAGE` (`"en"`) in `general/tools/_path_safety.py` (alongside `validate_id`) | The plan/ADR name `_path_safety` as the guard's home; keeping the vocabulary's single source (pattern + default) there means the path-resolution module and the table loader both import from one place |
| Language derivation for the parse chain | `read_dec` derives the effective language from the file's own position (`language_for_doc_path`), not from a caller argument | The location *is* the language encoding (ADR item 1), so every reader (get/list/parse, the generic tools' dec adapters) parses a variant with its table with zero signature changes; the `DocCache` path-keyed entry then stays correct per language (ADR item 9) |
| Table-resolution fail-fast | `get_dec`/`list_dec` resolve the table (shape guard first) *before* any filesystem access | A shape-valid-but-unusable language (no table file) is a caller error and should be reported even when the file is absent or the directory empty -- the same guard-before-IO discipline as `id` |
| Reconcile scope with subfolders | `dec`'s reconcile-on-scan (in `list_dec` and `find_dec_path`) now uses the domain-wide union (`iter_doc_paths_all_languages`: flat + every shape-valid `{language}` subdir) instead of the single scanned directory | With variants in subfolders, a scan of one language no longer covers the whole domain; reconciling against it alone would evict the other languages' cached entries (ADR item 9's "no `DocCache` code change" holds -- only the argument passed to the domain's existing `reconcile` wrapper changed) |
| Heading-table module home | `general/models/heading_table.py` (new), eagerly exported from `general/models/__init__.py` | It is shared cross-domain data machinery (like `general/models/dtais.py`/`ears.py` for the packaged `general/data` files); its only `general.*` import is the leaf `general/tools/_path_safety`, so the eager import introduces no cycle (verified against the repo's actual import-order traces) |
| Pre-pass location | A pure function (`normalize_heading_lines`) in the table module, applied inside `dec.models.v1.parse_dec` after `format_text` and before `Decision.from_text` | The `models/md` engine stays untouched (ADR item 5); the pass is a byte-identity no-op for any text whose headings the table does not map (including all EN text), so the default parse path is byte-identical |
| `de.json` closed set | 114 entries, derived programmatically from the eleven i18n-eligible domains' document models (body field-tree walk of each `*Document`), translated to German with pairwise-distinct values | The ADR requires the set to be machine-derivable from the models, not hand-guessed; a Phase 150 drift test will re-derive it and assert exact coverage |

#### 2026-10-29T21:00:00.000+01:00 - Task 100.150 resolutions: regex-locked English prose inventory (one field found, resolved (b))

Systematic search of the i18n-eligible domains' models and tools (`field_validator`/`model_validator`, `re.fullmatch`/`re.match` against field content -- closed-vocabulary tokens and heading structure excluded, which are REQ-010's own territory) found exactly one regex-locked English prose field. Resolutions per the plan: (a) = a per-language template variant the validator also accepts; (b) = an explicit exemption keeping the field in English in every language. (Phase 100 documents the resolutions only; Task 125.120 applies the `prb` one during implementation.)

| domain | locked field | resolution | rationale |
| --- | --- | --- | --- |
| req | none found | -- | `Level` value is the RFC-2119 closed set and `Priority` is a number 0-99 -- closed vocabulary / language-neutral (REQ-010), not prose |
| uc | none found | -- | body fields are free prose; the `return|continue to step N` / `subordinate|superordinate|extension:` patterns live in the diagram renderer only and run on EN content only (REQ-013) |
| tsk | none found | -- | the `[ ]`/`[x]` checkbox markers are language-neutral; task descriptions are free text |
| qa | none found | -- | the `**<d>.<NNNN>**: ` question-number prefix is digits/punctuation (language-neutral); question and answer prose is free |
| prb | `problem_statement` lead paragraph (`_PROBLEM_STATEMENT_PATTERN`, `fullmatch` in a `field_validator`) | (b) exemption | (a) would thread the file's language into the Pydantic validator layer (the model does not know it today) plus a new pattern and error message per language, indefinitely, for a single sentence whose enforced joiners are schema-constant in nature (REQ-010); the whole sentence stays canonical English in every language -- the translation workflow must not touch it, drift detection must ignore it |
| gol | none found | -- | `Priority` is a number 0-99 -- language-neutral (REQ-010) |
| rsk | none found | -- | the `Strategy` value is the TARA closed 4-word set; the `Probability`/`Impact` heading values are schema-constant tokens (REQ-010) |
| dec | none found | -- | the `Option {N}:` / timestamp-led `UpdateEntry` heading tokens are schema-constant (REQ-010); all body prose is free |
| sop | none found | -- | the `Step {N}:` / timestamp-led `UpdateEntry` heading tokens are schema-constant (REQ-010); the approval/effectivity lifecycle `status` set is closed frontmatter vocabulary (REQ-010) |
| vcr | none found | -- | `Verifies` is the `<REQ|UC> <uuid>: <title>` cross-reference structure (the title is free data); `Coverage` and the DTAIS method words are closed vocabulary (REQ-010) |
| sysrs | none found | -- | every locked pattern is the `<TAG> <uuid>: <title>` cross-reference structure (the title is free data) |

#### 2026-10-29T20:55:00.000+01:00 - Task 100.140: `dec` is the pilot domain for Phases 110-130 and ACC-005/ACC-006/ACC-007

Recorded per the plan's Design Notes (decision already made there): `dec` is the pilot for the implementation phases because it is dispatch-only (no per-domain `update_dec`/`set_status_dec`/`validate_dec` tools to special-case -- the generic `update`/`edit`/`set_status`/`set_classification`/`delete` tools already cover it), has a simple `models/md`-based body, and a small heading set. Phases 110-130 and ACC-005/ACC-006/ACC-007 are exercised against `dec` first; the remaining ten i18n-eligible domains roll out in Phase 125.

### Related PRs / Commits

- [Issue #197](https://github.com/dfch/biz.dfch.SpecMgr/issues/197): tracking issue for this feature.
