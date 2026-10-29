---
classification: null
created: '2026-10-29T11:14:24.992+01:00'
id: feat-197-i18n
status: planning
type: feat
updated: '2026-10-29T17:19:35.176+01:00'
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

- None yet; an ADR is planned as part of Task 100.130 once the directory-layout and heading-mapping-table design is settled (see Phase 100).

### Task List

#### Phase 100: Design -- Directory Layout, Heading-Mapping Table, Language Vocabulary

- [ ] Task 100.100: Finalize the on-disk filename/path convention for a language variant (`./docs/{type}/{language}/{id}.md`) and confirm it against the eleven i18n-eligible domains' existing path-resolution code (`general/tools/_doc_paths.py`); explicitly confirm and record that `feat/tools/_paths.py` and `feat/tools/_cache.py` need no change, since `feat` is permanently out of scope for this feature (REQ-002).

- [ ] Task 100.110: Design the per-language heading-mapping table format and storage location, and how a parser resolves a translated heading back to its canonical schema key; explicitly confirm that closed-vocabulary/schema-constant tokens embedded in or alongside headings (REQ-010, e.g. VCR's `(Method)` suffix, RSK's `Probability`/`Impact`/`{1..5}` tokens) are excluded from translation and the mapping table only ever maps heading *text*, never those tokens.

- [ ] Task 100.120: Decide the language-code vocabulary (e.g. ISO 639-1) and where it is validated.

- [ ] Task 100.130: Write an ADR capturing the directory-layout and heading-mapping-table design decisions.

- [ ] Task 100.140: Record `dec` as the pilot domain for Phases 110-130 and ACC-005/ACC-006/ACC-007 (decision already made; see Design Notes).

- [ ] Task 100.150: For each i18n-eligible domain, identify every regex/`fullmatch()`-pattern-locked English prose field (e.g. PRB's `problem_statement` lead paragraph) and document its resolution per REQ-010: either a per-language template variant the validator accepts, or an explicit exemption keeping the field in English in every language.

#### Phase 110: Path Resolution & Read-Side Plumbing (Pilot Domain: `dec`)

- [ ] Task 110.100: Extend `general/tools/_doc_paths.py` to resolve a document path given `type`/`id`/optional `language`, and extend `general/tools/_path_safety` to validate the `language` value (REQ-008) with the same path-injection/confinement discipline already applied to `id`; confirm `iter_doc_paths`'s non-recursive scan does not descend into `{language}` subfolders (ACC-014).

- [ ] Task 110.110: Add the optional `language` parameter to `get_dec`/`list_dec`, defaulting to `"en"` with unchanged behavior when omitted.

- [ ] Task 110.120: Extend the markdown parser layer to apply the heading-mapping table when parsing a non-EN document, exercised against `dec`.

#### Phase 120: Write-Side Plumbing (Pilot Domain: `dec`)

- [ ] Task 120.100: Add the optional `language` parameter to `create_dec` and the generic `update`, `edit`, `set_status`, `set_classification`, and `delete` tools, exercised against `dec` (ACC-006 requires all six tools, not just one).

- [ ] Task 120.110: Confirm (do not implement unless proven necessary) that `DocCache`'s existing `Path`-keyed cache entries already keep different languages of the same `dec` id from colliding once Task 100.100/110.100 make path resolution language-aware; add a `DocCache` code change only if this verification finds a real collision.

- [ ] Task 120.120: Test (REQ-003 end-to-end) that writing/reading a `dec` translation never changes or duplicates the shared `id`, and that the EN variant's content/`updated` timestamp is untouched by a write to a non-default language.

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

**As of 2026-10-29**: Feature drafted from GitHub issue #197; design not yet started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

### Related PRs / Commits

- [Issue #197](https://github.com/dfch/biz.dfch.SpecMgr/issues/197): tracking issue for this feature.
