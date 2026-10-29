---
classification: null
created: '2026-10-28T09:42:29.469+01:00'
id: feat-229-txt
status: progress
type: feat
updated: '2026-10-29T04:53:38.000+01:00'
version: 1.0.0
---

# Feature: Add artifact type "Free-Form Text" (TXT)

## Plan

### Overview

New whole-body document-type domain `txt`: a generic, minimally structured catch-all for unstructured markdown text that does not warrant a dedicated domain (ad hoc notes, meeting minutes, review/audit write-ups, scratch analysis). It is deliberately not a report and not a formal notes type: no enforced internal structure beyond a free-form body and a mandatory update log. Tracked by GitHub issue #229 (originally titled "generic 'doc' artifact type"; the name, scope and structure were resolved in the planning discussion, see Decisions Made and the issue comment).

Document shape (everything between the H1 and `## Updates` is opaque to the parser, including any H2 to H6 headings):

```
---
{frontmatter: id, version, status (draft|progress|done), type: txt, created, updated, classification?}
---

# {Title}

{any markdown, mandatory, may contain H2..H6 headings}

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### {timestamp} ( - | : ) {title}

{any markdown}
```

The domain follows the domain-first hierarchy and is dispatch-only from day one (generic `update`/`edit`/`set_status`/`set_classification`/`delete`/`validate`, no per-domain mutation tools), patterned on the `vcr` domain (`.specmgr/feat/feat-33-vcr/README.md`). `txt` is also added to the reference-tag vocabulary (as source and as target) and to the reference-graph palette.

### Requirements

- REQ-001: A `txt` document consists of frontmatter, a single `# {Title}` H1, a mandatory free-form body, and a mandatory `## Updates` section that is the last H2 of the document.
- REQ-002: The body is mandatory and opaque: any markdown (paragraphs, lists, code blocks, H2 to H6 headings) is accepted verbatim; a document whose H1 is followed directly by `## Updates`, or by only whitespace, is rejected by the engine's existing mandatory-field error; a comment-only body is accepted (current parser behaviour, no extra validator).
- REQ-003: The body ends at the first top-level (not inside a code fence or other block) H2 whose text is `Updates`; a second `## Updates`, or any H2 after `## Updates`, is rejected by the engine's existing trailing-completeness error.
- REQ-004: `## Updates` is mandatory and holds at least one `### {timestamp} ( - | : ) {title}` entry, newest first, using the same entry heading regex, computed `timestamp`/`title` fields and shared `validate_newest_first` helper as `vcr`/`dec`/`sop`; entry content is any markdown and mandatory.
- REQ-005: Frontmatter `status` is the closed three-value vocabulary `draft` / `progress` / `done`; the frontmatter carries `type: txt` and the standard fields (`id`, `version`, `created`, `updated`, optional free-text `classification`).
- REQ-006: The body's text is reachable through `model_dump()`/`model_dump_json()` via a `text` computed field, like every other opaque leaf in this engine.
- REQ-007: `txt` is registered once in `WHOLE_BODY_DOMAINS` (appended after `sysrs`) and is served by the generic `update`, `edit`, `set_status`, `set_classification`, `delete`, `validate`, `find_related`, `find_similar_text` and `list_references` tools by registration only, with no per-domain `update_txt`/`set_status_txt`/`validate_txt`/`delete_txt` tools.
- REQ-008: The domain exposes `create_txt`, `parse_txt`, `list_txt`, `get_txt` (with `raw`/`offset`/`limit`/`numbered`), `get_txt_example`, `get_txt_template` and `get_txt_schema`; resources `specmgr://txt/example` and `specmgr://txt/template` (no `specmgr://txt/{id}`, no `specmgr://txt/list`); prompts `create_txt` and `update_txt`; the non-raising `ValidateResult`/`ParseFailureResult` channels behave like every other whole-body domain.
- REQ-009: `txt` is both a reference source and a reference target: `TXT <uuid>` is added to the tag vocabulary of `list_references`/`get_reference_diagram`, resolved by a `_load_txt` target resolver (title = the document's H1), and a free-floating `REQ <uuid>` (or any other known tag) in a `txt` body is picked up by the existing regex scan.
- REQ-010: The frozen reference-graph palette gains a `TXT` entry coloured `LightGrey` (inserted after `SYSRS`, before `UNRESOLVED`; 14 entries become 15), with the `specmgr://reference-graph` rulebook amended with a dated note and the golden fixtures and pinned counts updated in the same change.
- REQ-011: The engine's default parse error messages are kept unchanged; the packaged template and example are the structural documentation (no custom cause/fix-hint wrapping for the leftover-text or missing-`Updates` errors).
- REQ-012: All cross-cutting registrations and generated artifacts are complete and drift-free: `server.py`, the `specmgr://config` resource, `commands/schema.py`, both `txt_schema.json` copies, `pyproject.toml` package data, `.pre-commit-config.yaml`, CI, `server.json`/`README.md`/`AGENTS.md`/`CHANGELOG.md`/`docs/MCP.md`/`docs/api/`, and the agent/skill text that enumerates domains.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001, REQ-002, REQ-003 -- a parser test matrix over `tests/txt/models/v1/` covers: text-only body, body with free H2/H3 and lists, fenced `## Updates` inside the body (accepted), empty body (rejected), whitespace-only body (rejected), comment-only body (accepted), missing `## Updates` (rejected), duplicate `## Updates` (rejected), H2 after `## Updates` (rejected).
- [x] ACC-002: Verifies REQ-004 -- tests cover entry heading shape (both `-` and `:` separators, `T` and space date separators, `Z` and offset timezones), out-of-order entries rejected, equal timestamps accepted, zero entries rejected, empty entry content rejected, and the computed `timestamp`/`title` fields.
- [x] ACC-003: Verifies REQ-005, REQ-006 -- `TxtFrontmatter` accepts exactly `draft`/`progress`/`done` and rejects other statuses; a parsed document's `model_dump()` surfaces the body text and a full-document round-trip is byte-stable.
- [x] ACC-004: Verifies REQ-007 -- `test__domains.py`, `test_update.py`, `test_edit.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py` and `test_validate.py` (and their sibling similarity/`list_references` tests) include `txt` cases, and no per-domain `*_txt` mutation tool exists.
- [x] ACC-005: Verifies REQ-008 -- `tests/txt/` covers every tool, both resources and both prompts, including the `get_txt(raw=True, numbered=True)` windowing and the `ParseFailureResult` channel for a broken document.
- [ ] ACC-006: Verifies REQ-009 -- `test__references.py` and `test_list_references.py` cover `TXT <uuid>` extraction, a `_load_txt` resolution (found and not-found rows), and a `txt` source document listing a free-floating `REQ <uuid>`; the import-time `_SOURCE_LOADERS`/`ALL_DOMAINS` assert holds.
- [ ] ACC-007: Verifies REQ-010 -- the palette tuple, the rulebook (`general_reference_graph.md`) with its dated amendment note, `test_reference_graph.py`/`test__reference_graph.py`/`test_reference_graph_subset.py`/`test_get_reference_diagram.py` and the golden fixtures all agree on 15 entries with `("TXT", "LightGrey")` (the 15-entry agreement is confined to these artifacts -- the `plantuml/` structure checker and the UC rulebook carry no palette expectations), and a diagram containing a TXT node passes `validate_plantuml`.
- [ ] ACC-008: Verifies REQ-011 -- no `txt`-specific error-message wrapping exists beyond the shared `wrap_tool_errors` context, and the packaged `txt_template.md`/`txt_example.md` parse and validate green through `validate(type="txt", full=True)`.
- [ ] ACC-009: Verifies REQ-012 -- `specmgr schema`, `specmgr docs`, `specmgr mcp-docs` and the config-golden test show no drift, `tests/test_envregistry_*`, `tests/test_schema_surface_registration.py`, `tests/test_agent_facing_wording.py` and `tests/opencode/test_skill_specmgr_refs.py` pass, and `server.py`'s docstring lists every new tool/resource/prompt.
- [ ] ACC-010: The full test suite passes after every phase below, not just at the end.
- [ ] ACC-011: `ruff format --check`, `ruff check` and `vulture` all pass against the final state.

### Scope

#### Included

- The `txt/` domain package: `models/v1/` (frontmatter, body, document, parser, summary), `tools/`, `resources/`, `prompts/`, `data/`.
- Generic-tool registration (`_domains.py` plus one adapter each in `update`, `edit`, `set_status`, `set_classification`, `delete`, `validate`), the similarity corpus, and `list_references` source loader.
- The `TXT` reference tag, its target resolver and the reference-graph palette/rulebook amendment.
- All cross-cutting registration and generated documentation listed in REQ-012.

#### Explicitly Out Of Scope

- Any structured section beyond title/body/`## Updates` (no `## Related Artifacts`, `## Tags`, `## Source`, `## More Information`); references are free-floating tokens in the body.
- Query-ability across `txt` instances (accepted v1 trade-off, as stated in issue #229); a specific recurring shape would be promoted to its own domain later.
- Custom cause/fix-hint wording for the engine's leftover-text and missing-section errors (REQ-011).
- A policy rejecting comment-only or whitespace-only-after-comment bodies beyond the current parser behaviour.
- Any change to the shared `models/md` engine (the one boundary override lives in `txt/models/v1/body.py`).
- A formal notes (`not`/`nte`) or report (`rpt`) domain.

### Dependencies

#### Depends On

- ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy).
- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic type-dispatched `update`/`set_status`; new domains are dispatch-only).
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc (single source of truth for the domain-name set in `_domains.py`).
- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads) and ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool).
- `.specmgr/feat/feat-33-vcr/README.md` as the closest from-scratch-domain precedent (`UpdateEntry`/`Updates` shape, registration checklist).
- `.specmgr/feat/feat-207-reference-graph/README.md` for the frozen palette and rulebook amendment convention (dated notes).

#### Blocks

- Nothing.

### Design Notes

#### Parser (verified by an in-memory spike against the real engine)

Root `Txt(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`, plain (not `MarkdownSection1WithComment`), declaring in order `body: TxtBody` (mandatory) and `updates: Updates` (mandatory). A plain opaque `MarkdownStr` body fails every document, because the base `MarkdownStr.get_extent` consumes all remaining text including `## Updates`. The one required addition is a boundary `get_extent` on the body class:

```python
class TxtBody(MarkdownStr):
    @classmethod
    def get_extent(cls, text: str) -> int:
        toks = parse(text)
        for i, tok in enumerate(toks):
            if (
                tok.type == "heading_open"
                and tok.tag == "h2"
                and tok.level == 0
                and toks[i + 1].content.strip() == "Updates"
            ):
                return tok.map[0]
        return super().get_extent(text)
```

`Updates(MarkdownSection2WithComment)` and `UpdateEntry(MarkdownSection3)` are copied from `vcr` (heading regex, computed `timestamp`/`title`, `_validate_newest_first` via the shared helper), each domain owning its concrete leaf classes per the domain-first convention.

Spike results (plain body / boundary override): happy path fails / OK; empty body fails / rejected once `body` is mandatory; missing `## Updates` fails / rejected; duplicate `## Updates` fails / rejected as "text left over" at the second heading; H2 after `## Updates` fails / rejected as "text left over"; fenced `## Updates` in the body fails / OK (the fence yields no `heading_open` token); bad entry heading fails / rejected with the entry alias error. With a plain root a leading HTML comment stays inside the body (comment-only body parses); a `WithComment` root would take it as the root `comment` and leave the body empty, which is why the root is plain.

The Phase 100 tests are the real version of the spike and must reproduce each row; if the real `Txt` class diverges from the spike, the divergence is a defect to resolve, not a design change.

#### Why no `## Updates` collision handling

The first top-level `## Updates` is the boundary by construction. A duplicate or trailing H2 is then left over after the `Updates` field and rejected by the engine's own trailing-completeness check, so no extra rule or custom error is needed.

#### Directory and id

Documents live flat under the shared docs root as `docs/txt/txt-{uuid}-{slug}.md`, using the shared `SPECMGR_DOCS_DIR`-rooted default like `req`/`vcr` (verified: `vcr`/`sysrs` delegate to the shared `doc_base_dir` -- `SPECMGR_DOCS_DIR` only, no per-domain variable -- so no `SPECMGR_TXT_DIR` is introduced and no `_envregistry` entry is added; the `tests/test_envregistry_*` variable count stays green). ids are server-generated UUIDs.

#### Palette

`TXT` is `LightGrey` (a PlantUML-recognised colour name, not used by any of the existing 14 entries: LightYellow, LightBlue, Pink, Honeydew, LemonChiffon, LightCoral, Lavender, Orange, LightGreen, PowderBlue, PaleTurquoise, Khaki, Thistle, DarkRed). The colour is fixed here so implementation never stops to confirm it. Verified 2026-10-28 by rendering the frozen 15-entry palette probe (the renderer's own structure: skinparam block, domain groups, bracketed aliases, one edge) through the running `plantuml-cli` docker container (plantuml 1.2026.8): the `TXT` node renders `fill="#D3D3D3"` (canonical lightgray) and the `Thistle` control node renders `fill="#D8BFD8"`, no warnings.

#### Cross-cutting touchpoints (from a grep for `sysrs`/`vcr` outside the domain package)

`general/tools/`: `__init__.py` (module docstring hand-lists the 12-domain `type` vocabulary several times plus the "all 13 domains" line for `get_reference_diagram_all`), `_domains.py`, `_references.py`, `list_references.py`, `_path_safety.py`, `_listing.py`, `_doc_paths.py`, `_similarity_corpus.py`, `update.py`, `edit.py`, `set_status.py`, `set_classification.py`, `delete.py`, `validate.py`, `find_related.py`, `find_similar_text.py`, `get_reference_diagram.py`, `get_reference_diagram_all.py` (docstring's "13 domains" claim), `_reference_graph.py`; `general/models/`: `reference_graph.py`, `reference.py`, `similarity_hit.py`, `update_result.py`, `parse_failure_result.py`; `general/data/general_reference_graph.md`, `general_repair_instructions.md`; `general/prompts/repair.py`; `general/resources/config.py`, `models/config_info.py`; `commands/schema.py`, `commands/diagram.py`; `models/md/` docstrings that enumerate domains; `server.py`; `pyproject.toml`; `server.json`; `.pre-commit-config.yaml`; `.github/workflows/ci.yml`; `whitelist.py` (vulture; the vcr/sysrs precedent entries for (de)serialization-only domain-model fields); `README.md`; `AGENTS.md`; `CHANGELOG.md`; `.specmgr/conventions.md`; `.opencode/skill/repair/SKILL.md`, `.opencode/skills/specmgr-refs/SKILL.md` (its "12 whole-body domains" enumerations, the hand-listed 12-domain list and the "13 vs 12" reconciliation note all shift once `txt` joins), `.opencode/agent/ref-finder.md`, `.opencode/agent/doc-repairer.md`, `.opencode/command/refs.md`, `.opencode/command/repair.md`, `tests/opencode/test_skill_specmgr_refs.py` (pins those skill strings). The task list below groups them; before editing, re-run the grep to catch drift since this plan was written.

### Related Decisions

- ADR ece4554b-725c-4f76-bc04-5d2b760363d2: domain-first hierarchy for tools/prompts/resources.
- ADR 36905d5b-8057-4294-8665-c7eed5534db0: generic type-dispatched update/status tools; new domains register, not add tools.
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc: single source of truth for the document-type domain-name set.
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: per-domain content-hash-validated doc cache; the new domain gets its own `tools/_cache.py` singleton.

### Task List

#### Phase 100: Models and parser

- [x] Task 100.100: Create the `txt/` package skeleton (`__init__.py`, `models/v1/`, `tools/`, `resources/`, `prompts/`, `data/`) and `tests/txt/` mirroring `vcr/`
- [x] Task 100.110: Implement `TxtFrontmatter` (`type: txt`, status `draft`/`progress`/`done`, standard fields, optional `classification`)
- [x] Task 100.120: Implement `TxtBody` with the boundary `get_extent` and the `text` computed field
- [x] Task 100.130: Implement `UpdateEntryContent`, `UpdateEntry`, `Updates` (copied from `vcr`, shared `validate_newest_first`)
- [x] Task 100.140: Implement the root `Txt(MarkdownSection1)` (plain root, mandatory `body` and `updates`), `TxtDocument`, `parse_txt`/`render` and the `TxtSummary`
- [x] Task 100.150: Write the parser test matrix from ACC-001 to ACC-003 (the 9 structural cases, the entry cases, frontmatter, round-trip, `model_dump`)
- [x] Task 100.160: Phase-end gate: `ruff format --check`, `ruff check`, `vulture` (extend `whitelist.py` with the `txt` entries following the vcr/sysrs precedent -- the root `body`/`updates` fields and `UpdateEntry`'s computed `timestamp`/`title`), full `pytest`

#### Phase 110: Tools

- [x] Task 110.100: Add `txt/tools/` support modules (`_paths.py`, `_io.py`, `_lock.py`, `_cache.py`, `_write.py`) following `vcr`
- [x] Task 110.110: Implement `create_txt` and `parse_txt` with the non-raising `ValidateResult` channel
- [x] Task 110.120: Implement `list_txt` (paged, inline failed rows with resolved `path`) and `get_txt` (`raw`/`offset`/`limit`/`numbered`, `ParseFailureResult`)
- [x] Task 110.130: Implement `get_txt_example`, `get_txt_template`, `get_txt_schema`
- [x] Task 110.140: Write `tests/txt/tools/` for every tool, including the broken-document and path-safety cases
- [x] Task 110.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 120: Data, resources and prompts

- [x] Task 120.100: Author `txt_template.md` and `txt_example.md` (the example demonstrates free H2/H3 in the body, a free-floating `REQ <uuid>` reference and two ordered update entries)
- [x] Task 120.110: Generate `txt_schema.json` (packaged copy) via `specmgr schema --type txt`
- [x] Task 120.120: Implement `specmgr://txt/example` and `specmgr://txt/template` resources
- [x] Task 120.130: Author `txt_create_instructions.md`/`txt_update_instructions.md` and implement the `create_txt`/`update_txt` prompts (`create_txt` checks `list_txt` for a near-duplicate; `update_txt` names the generic `update`/`edit`/`set_status` tools with `type="txt"`)
- [x] Task 120.140: Write `tests/txt/resources/` and `tests/txt/prompts/`
- [x] Task 120.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 130: Generic tool registration

- [x] Task 130.100: Append `txt` to `WHOLE_BODY_DOMAINS` and add its `WholeBodyDomain` adapter in `general/tools/_domains.py` (update `_domains.py`'s own module docstring -- the "12-domain tuple" wording and the hand-listed names -- in the same edit; this grows `ALL_DOMAINS`, so every import-time domain-set assert table must land in this phase -- see 130.110 to 130.130)
- [x] Task 130.110: Add the `txt` adapter to each of `update`, `edit`, `set_status` (both `_ADAPTERS` and `_ALLOWED_STATUSES_BY_TYPE` -- the latter has its own import-time assert against `ALL_DOMAINS` and needs `txt`'s `draft`/`progress`/`done` -- plus the `TxtFrontmatter` member of the `_SetStatusFrontmatter` return union), `set_classification`, `delete`, `validate`
- [x] Task 130.120: Wire `txt` into `_path_safety`, `_listing`, `_doc_paths` (docstrings/messages), the similarity corpus, `find_related`/`find_similar_text`, and write-path cache warming; add the `txt` source-loader entries to `list_references.py::_SOURCE_LOADERS` and to `_reference_graph.py::_SOURCE_LOADERS`/`_SCAN_READERS` (all three tables carry import-time asserts against `ALL_DOMAINS`, so they must land with the domain-set growth, not in Phases 140/150; they need only the Phase 110 `txt_base_dir`/`load_txt_by_id`/`read_txt` artifacts)
- [x] Task 130.130: Extend the generic-tool tests (`test__domains.py`, `test_update.py`, `test_edit.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py`, `test_validate.py`, `test_doc_cache_write_wiring.py`, similarity tests) with `txt` cases, plus the `txt` entry in `tests/test_mcp_output_schema_satisfiability.py::_GET_TOOLS` (its import-time assert against `WHOLE_BODY_DOMAINS` must hold for this phase's full-`pytest` gate to pass)
- [x] Task 130.140: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 140: Reference type

- [ ] Task 140.100: Add `"txt"` to `_UUID_REFERENCE_TYPES`, implement `_load_txt` and its `_TARGET_RESOLVERS` entry in `general/tools/_references.py`, and update the module docstring's tag-vocabulary text
- [ ] Task 140.110: Update `ReferenceRow`/related docstrings in `list_references.py` (the `txt` source-loader entry already landed in Task 130.120 with the domain-set growth)
- [ ] Task 140.120: Update `test__references.py`, `test_list_references.py` and any drift test pinning the tag list; add a `txt` source document test with a free-floating `REQ <uuid>`
- [ ] Task 140.130: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 150: Reference-graph palette

- [ ] Task 150.100: Add `("TXT", "LightGrey")` to `_PALETTE` (after `SYSRS`, before `UNRESOLVED`) and `txt` to the graph domain tuple in `general/models/reference_graph.py`, and wire `get_reference_diagram` (docstring) and `commands/diagram.py` (the `_reference_graph.py` source-loader/scan-reader entries already landed in Task 130.120)
- [ ] Task 150.110: Amend `general/data/general_reference_graph.md` (palette table, entry count 14 to 15, dated amendment note); the 15-entry agreement is confined to `general/models/reference_graph.py`, this rulebook, the general tests and the golden fixtures (the `plantuml/` structure checker and the `specmgr://uc/plantuml` rulebook carry no palette expectations -- nothing to keep consistent there)
- [ ] Task 150.120: Update `test_reference_graph.py`, `test__reference_graph.py`, `test_reference_graph_subset.py`, `test_get_reference_diagram.py` (its `ALL_DOMAINS`-enum test, the "13-domain" docstrings and the source-type loop all go stale once `txt` joins `ALL_DOMAINS`) and the golden fixtures; add a diagram test containing a TXT node validated by `validate_plantuml`
- [ ] Task 150.130: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 160: Server and build registration

- [ ] Task 160.100: Register the `txt` package in `server.py` (last-line import, module docstring listing of every new tool/resource/prompt); update `general/tools/__init__.py`'s module docstring (its hand-listed 12-domain `type`-vocabulary lines and the "all 13 domains" line) and `get_reference_diagram_all.py`'s docstring (its "13 domains" claim)
- [ ] Task 160.110: Add `txt` to the `specmgr://config` resource and `models/config_info.py`, and refresh the config golden under `tests/fixtures/config-golden/`
- [ ] Task 160.120: Add `generate_txt_schema` and the `"txt"` entry to `commands/schema.py`; generate `docs/txt_schema.json` and `txt/data/txt_schema.json`
- [ ] Task 160.130: Add `biz.dfch.specmgr.txt` package data to `pyproject.toml`, widen the shared `files:` regex to include `txt/models/v1` in every existing occurrence (13: the shared `specmgr-schema` hook plus the 12 per-domain `-package` hooks -- verify the count before and after, the feat-31 precedent) and add one new `specmgr-schema-txt-package` hook (the 14th occurrence of the widened regex, mirroring `specmgr-schema-sysrs-package`, placed last per the insertion-order convention), and the matching CI steps in `.github/workflows/ci.yml`
- [ ] Task 160.140: Update domain lists in `server.json` and `_doc_paths.py` env-var descriptions (keep `tests/test_envregistry_*` green)
- [ ] Task 160.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 170: Documentation and agent text

- [ ] Task 170.100: Add the `txt` bullet to `AGENTS.md` (domain list, generic-tool `type` enumerations, reference-tag vocabulary, palette count) and update `.specmgr/conventions.md` if it enumerates domains
- [ ] Task 170.110: Update `README.md` (domain list, Environment Variables section if affected) and add a `CHANGELOG.md` `[Unreleased]` entry
- [ ] Task 170.120: Update the agent/skill/command text that enumerates domains (`repair` skill and `doc-repairer`/`ref-finder` agents, the `specmgr-refs` skill -- its "12 whole-body domains" enumerations, the hand-listed 12-domain list and the "13 vs 12" reconciliation note go to 13/14 -- and its pin test `tests/opencode/test_skill_specmgr_refs.py`, `/refs` and `/repair` commands, `general_repair_instructions.md`, `general/prompts/repair.py`)
- [ ] Task 170.130: Regenerate `docs/api/`, `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); confirm `tests/test_schema_surface_registration.py` and `tests/test_agent_facing_wording.py` pass
- [ ] Task 170.140: Final gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`, `specmgr docs`/`schema`/`mcp-docs` drift checks, and set this feature's status to `review`

## Progress

### Current Status

**As of 2026-10-29**: Phase 130 (Generic tool registration) complete -- `txt` is registered once in `WHOLE_BODY_DOMAINS` (appended after `sysrs`, the 13th whole-body domain) with its `WholeBodyDomain` adapter (`txt_base_dir`/`iter_doc_paths`/`load_txt_by_id`/`parse_txt`), and is served by registration only by the generic `update`/`edit`/`set_status`/`set_classification`/`delete`/`validate` tools (one `_update_txt`/`_edit_txt`/`_set_status_txt`/`_set_classification_txt`/`_delete_txt`/`_validate_txt` adapter each, the `set_status` tables `_ADAPTERS` + `_ALLOWED_STATUSES_BY_TYPE["txt"]` (its own `draft`/`progress`/`done` set), and the return-union `TxtFrontmatter` members), the similarity corpus (`find_related`/`find_similar_text` now enumerate and rank `txt` documents), `list_references`'s `txt` source-loader, and the reference-graph builders' `txt` source/scan legs -- all import-time domain-set asserts hold. The 7 txt tools, 2 resources and 2 prompts became live on the `mcp` singleton at the `_domains` import edge (`txt/__init__.py`'s vcr-precedent `from . import prompts, resources, tools` line), so `tests/txt/conftest.py`'s throwaway-`mcp` isolation was deleted in this phase (the recorded Phase 160 removal mandate triggers earlier than written -- see Decisions Made), and the surface pins moved 115→122 tools and 37→39 resources. `get_txt` now validates ids through the shared `validate_id("txt", ...)` dispatcher (the recorded Phase 110 switch; its path-safety tests pass unmodified). Two gate-forced table fixes outside `general/tools/` landed alongside: `general/resources/config.py`'s `domains` dict + the config golden fixture, and `general/models/reference_graph.py`'s `_DOMAIN_ORDER` append (see Decisions Made). ACC-004 is satisfied (every named generic-tool test carries `txt` cases; no per-domain `*_txt` mutation tool exists). Full `pytest` 5024 passed / 18 skipped; `ruff format --check`/`ruff check`/`vulture` green; `specmgr docs` + `specmgr mcp-docs` regenerated and idempotent (drift-free tree). Next step: Phase 140 (Reference type: the `TXT <uuid>` tag in `_references.py`, the `_load_txt` target resolver).

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-29 03:53:38.000Z - Phase 130 complete (generic tool registration, Tasks 130.100-130.140)

Implemented Tasks 130.100-130.140. (1) Registration (130.100): `txt` appended to `WHOLE_BODY_DOMAINS` + its `WholeBodyDomain` adapter in `general/tools/_domains.py` (`txt_base_dir`/`load_txt_by_id`/`parse_txt` imports, shared flat-file `iter_doc_paths`), module docstring updated in the same edit ("12-domain tuple" → "13-domain tuple", `txt` in the canonical-order list). The import edge is the load-bearing fact of the phase: importing `txt.tools._io` first runs `txt/__init__.py`'s vcr-precedent `from . import prompts, resources, tools` line, so every process that imports the server now registers all 7 txt tools + 2 resources + 2 prompts on the live `mcp` singleton (measured: 115/37/33 → 122/39/35) ahead of Phase 160's `server.py` line -- Consequence A; the Consequence-A handling is the `tests/txt/conftest.py` deletion (its collection-time guard assert would fire the moment `txt.tools` is in `sys.modules`, which the edge now guarantees) and the `test_schema_surface_registration.py` pin moves 115→122 (tools, as predicted) and 37→39 (resources -- the "stays 37" prediction is contradicted by the committed `txt/__init__.py`, see Decisions Made). (2) Adapters (130.110): `_update_txt`/`_edit_txt`/`_set_status_txt`/`_set_classification_txt`/`_delete_txt`/`_validate_txt` added file-for-file over the vcr/sysrs shapes (non-raising `ParseFailureResult`/`ValidateResult` channels, `assert_within` defense-in-depth, write-path `read_txt` cache warm on every success path), the `txt` entry in each `_ADAPTERS` table, `set_status`'s `_ALLOWED_STATUSES_BY_TYPE["txt"]` (txt's own `{draft, progress, done}` frozenset from `txt/models/v1/frontmatter.py`) and the `TxtFrontmatter` member of all four return unions (`UpdateFrontmatter` in `general/models/update_result.py`, `_EditFrontmatter`, `_SetStatusFrontmatter`, `_SetClassificationFrontmatter`). (3) Wiring (130.120): `txt` source-loader entries in `list_references.py::_SOURCE_LOADERS` and `_reference_graph.py::_SOURCE_LOADERS`/`_SCAN_READERS` (all three import-time `ALL_DOMAINS` asserts hold); docstring/message updates in `_path_safety`/`_listing`/`_similarity_corpus`/`find_related`/`find_similar_text` (`_doc_paths.py`'s env-registry description stays stale until Task 160.140 by the plan's own sequencing -- see Decisions Made); `get_txt`'s path safety switched from the interim `assert_no_traversal` + `assert_uuid` composition to the shared `validate_id("txt", id)` dispatcher per the recorded Phase 110 decision (interim wording removed; behaviour identical for every id -- its two path-safety tests pass unmodified). (4) Tests (130.130): `txt` cases added to `test__domains.py` (the 13-tuple), `test_update.py` (full `_Case` incl. the `Updates` newest-first field-error channel, `_PARSE_FAILURE_CASES`, `_INJECTION_CASES`), `test_edit.py` (multi-occurrence + deletion + field-error cases, enum-length pin 12→13), `test_set_status.py` (allowed statuses incl. rejection of `accepted`), `test_set_classification.py`, `test_delete.py`, `test_validate.py` (body/full/malformed/out-of-order-entries cases), `test_doc_cache_write_wiring.py` (`_SET_STATUS_TARGETS_BY_DOMAIN["txt"] = "progress"` -- its import-time assert is the tripwire), `test_mcp_output_schema_satisfiability.py::_GET_TOOLS` (`get_txt` entry; import-time assert holds), and the similarity tests (`seed_txt` helper over a vocabulary-controlled `_TXT_TEMPLATE`; txt candidates in `find_related`'s default-target-set test and in `find_similar_text`'s `target_types` test, incl. `target_types=["txt"]` restriction); `tests/txt/conftest.py` deleted; `test_agent_facing_wording.py`'s G1 pins narrowed to the 13-file shared core (txt's splice-skip variant names `edit` -- see Decisions Made). (5) Gate (130.140): `uv run --frozen ruff format --check` green (2203 files), `uv run --frozen ruff check` green, `uv run --frozen vulture src/ whitelist.py --min-confidence 60` green with exit 0 (no new whitelist entries needed -- `invalidate_txt_cache`/`reconcile_txt_cache` now have production callers via the generic `delete`/`list_txt` wiring), full `uv run --frozen pytest -n auto --cov=src --cov-report=` **5024 passed, 18 skipped** (first full run after the source changes; no import-time tripwire fired), and `uv run --frozen specmgr docs` + `uv run --frozen specmgr mcp-docs` regenerated (15 doc files; a second run is byte-identical -- the tree is drift-free; `docs/MCP.md` now lists all 7 txt tools and the 13-domain `type` enums).

#### 2026-10-28 21:16:40.000Z - Phase 120 complete (data, resources and prompts, Tasks 120.100-120.150)

Implemented Tasks 120.100-120.150. (1) Data files (120.100): the Phase 110 `txt_example.md`/`txt_template.md` were re-verified in memory against every plan content requirement -- the example parses green through `parse_txt`, demonstrates free H2 (`## Findings`) and H3 (`### Root Cause`) headings in the body, carries the free-floating `REQ deaddead-beef-beef-beef-deaddeadbeef:` reference line, and holds two newest-ordered `## Updates` entries (`Review complete` 2026-10-24 >= `Initial draft created` 2026-10-20); the template is blind-text (the `Level 1 Heading is the Title of the Free-Form Text Document` H1, `Blind text` body/list items, `## Blind H2 Heading`, `### Blind H3 Heading`, the `REQ c0ffeec0-...` reference) and parses green with status `draft`. **No content changes were made** -- both files already met the plan, and the Phase 110 byte-stability pins (`test_get_txt_example.py`/`test_get_txt_template.py`'s parse->re-render tests) pass unmodified. (2) Schema (120.110): the on-disk `txt/data/txt_schema.json` was re-generated in memory through the exact mechanism `commands/schema.py` uses for every domain (`TxtDocument.model_json_schema()` + `schema_dict["$schema"] = GenerateJsonSchema.schema_dialect` + `schema_dict["$comment"] = SCHEMA_COMMENT_VERSION` + `json.dumps(..., indent=2, sort_keys=True) + "\n"`) and confirmed **byte-identical** (the literal `specmgr schema --type txt` CLI entry cannot run yet -- Task 160.120 adds `generate_txt_schema`; see Decisions Made). (3) Resources (120.120): `txt/resources/txt_example.py` + `txt_template.py` (`@mcp.resource()` for `specmgr://txt/example` / `specmgr://txt/template`, `text/markdown`, `read_packaged_text("txt", ...)` -- the same packaged files the Phase 110 tools read, no cross-import between `txt.tools` and `txt.resources`) and the re-exporting `txt/resources/__init__.py`, all file-for-file over the `vcr`/`sysrs` precedent. (4) Prompts (120.130): the two packaged instruction files `txt/data/txt_create_instructions.md` / `txt_update_instructions.md` (the `vcr` instruction-file shape, `string.Template` `$topic` / `$id`+`$instructions` placeholders) plus `txt/prompts/create_txt.py` (checks `list_txt` for a near-duplicate in step 0, narrates the mandatory H1/free-form-body/`## Updates` shape including the first-top-level-`## Updates` boundary rule and the no-optional-sections fact, `create_txt(content)` call, later-revisions pointer to the `update_txt` prompt and the generic `update`/`set_status`/`set_classification` tools with `type="txt"`) and `txt/prompts/update_txt.py` (read-first `get_txt(id)`, the line-range `get_txt(id, raw=True, numbered=True)` flow, the surgical `edit(id, type="txt", old_str, new_str)` flow, `set_status(id, type="txt", status)` as separate optional follow-up with the TXT `draft`/`progress`/`done` vocabulary, the boundary rule), with the re-exporting `txt/prompts/__init__.py`. (5) Tests (120.140): `tests/txt/resources/` (6+6 tests mirroring `tests/vcr/resources/`: real-file shape, byte-for-byte equality with the packaged file, tool/resource equality, parse-and-exercise-shape / round-trip, fresh-read, FileNotFoundError) and `tests/txt/prompts/` (12+16 tests mirroring `tests/vcr/prompts/`: substitution, packaged-file provenance, the `list_txt` duplicate check, todo/question narration, the boundary rule, tool-sequence ordering, the generic-tool naming incl. the `edit` call shape, fresh-read, FileNotFoundError) -- 40 new tests total. (6) Conftest: `tests/txt/conftest.py`'s throwaway-`mcp` pre-import now covers `txt.prompts`/`txt.resources`/`txt.tools` (extended `sys.modules` guard + postcondition asserts pinning the 7 tool names, the 2 resource URIs, and the 2 prompt names on the throwaway and their absence on the real singleton); the Phase 160 removal mandate stays in place, now worded over all three sub-packages. `txt/__init__.py`'s state paragraph updated to the Phase 120 state. Gate (120.150): `ruff format --check` (2200 files), `ruff check`, `vulture src/ whitelist.py --min-confidence 60` (no new flags, `whitelist.py` unchanged), `pytest -n auto --cov=src --cov-report=` (**5024 passed, 18 skipped**, +40 over Phase 110), and `specmgr docs` (regenerated `docs/api/` + `docs/GENERATED.md`; diff confined to the six new txt module entries, four new per-module API files, the index, and the test-file count 453 -> 457; a second `specmgr docs` run is drift-free). `tests/test_schema_surface_registration.py` (115 tools / 37 resources against the live singleton) passes both alone and combined with `tests/txt/` in either collection order.

#### 2026-10-28 20:20:26.000Z - Phase 110 verification pass: two forward-looking mandates tracked (no behaviour change)

Orchestrator verification of the Phase 110 state found it functionally green and required two documentation/consistency fixes, both applied without any source-behaviour change or new tests. (1) `tests/txt/conftest.py`'s module docstring now carries an explicit **Phase 160 removal mandate**: once Phase 160 registers `txt` on `server.py`'s bottom-of-file domain-import line, the entire file MUST BE DELETED (the throwaway pre-import would then rebind the tool modules to a dead instance — in every xdist worker the top-level `tests/test_*.py` modules that import `biz.dfch.specmgr.server` are collected before `tests/txt/`, so `txt.tools` is already in `sys.modules` bound to the real singleton); the conftest's collection-time guard assert is the deliberate loud tripwire for that moment (a collection-time `AssertionError` naming it means the file was not removed, not a runtime bug), and no phase may "fix" the assert by weakening it. The same mandate was appended to the Phase 110 conftest entry in Decisions Made. (2) A new Decisions Made entry ("Phase 130 must switch `get_txt`'s path safety to `validate_id`") tracks that Task 130.120's `_path_safety` wiring includes switching `get_txt`'s interim direct `assert_no_traversal` + `assert_uuid` composition to the shared `validate_id("txt", ...)` dispatcher (behaviour-identical for every id value; pins consistency with `get_vcr`; protects against future composition drift) — no `get_txt` source change in this phase. Re-verified after the edits: `ruff format --check` and `ruff check` green, and this README still parses green through `parse_feat`.

#### 2026-10-28 19:08:28.000Z - Phase 110 complete (tools, Tasks 110.100-110.150)

Implemented Tasks 110.100-110.150. (1) Support modules in `txt/tools/` mirroring `vcr/tools/` file-for-file: `_paths.py` (`TXT_TYPE_NAME`, `TxtNotFoundError`, `txt_base_dir`/`ensure_txt_base_dir` delegating to the shared `SPECMGR_DOCS_DIR`-rooted `doc_base_dir("txt")` -- no `SPECMGR_TXT_DIR`, no `_envregistry` entry, per the plan's "Directory and id" note; `iter_txt_paths`, cache-backed `find_txt_path`), `_cache.py` (the per-domain `DocCache` singleton: `read_txt`/`invalidate_txt_cache`/`reconcile_txt_cache`/`reset_txt_cache`), `_io.py` (`load_by_id` with the vanished-file second-read guard, `read_txt` re-export), `_lock.py` (`txt_lock`), `_write.py` (`write_txt_file`). (2) Tool wrappers: `create_txt` (body-only input, code-built frontmatter, filename `txt-{uuid}-{slug}.md`, non-raising `ValidateResult` on a content-validation failure, nothing written), `parse_txt` (thin over `txt.models.v1.parser.parse_txt`, non-raising `ValidateResult` for an existing-but-broken file, `OSError`-family still raised for a truly-absent/unreadable path), `list_txt` (paged default 25/cap 100 clamp-not-error, `error_count`, inline failed rows with resolved `path`, the feat-200-list `glob` id-filter), `get_txt` (`raw`/`offset`/`limit`/`numbered` over the shared `body_text`/`window_body`/`validate_read_args` helpers, non-raising `ParseFailureResult` with the byte-identical-error property vs `list_txt`'s failed row). Path safety: `get_txt` applies `assert_no_traversal` + `assert_uuid` from `general.tools._path_safety` -- the exact composition `validate_id` applies to every UUID-shaped domain -- because `"txt"` only joins the `validate_id` dispatch table with the Phase 130 `_domains` registration (see Decisions Made). `txt/__init__.py` now imports `prompts`/`resources`/`tools` per the vcr/qa/sysrs precedent (Phase 120 will fill the two still-empty sub-packages; the `server.py` import stays Phase 160). (3) Packaged data files (created in this phase by the recorded ordering decision, re-verified/finalized in Phase 120): `txt/data/txt_example.md` (complete valid sample: `type: txt`, placeholder UUID id, `status: done`, free body with a free `## Findings` H2 + `### Root Cause` H3 + a loose list + a free-floating `REQ deaddead-beef-...` reference line, `## Updates` with the anchor comment and two newest-first entries), `txt/data/txt_template.md` (blind-text placeholder, `deaddead-face-...` id, `status: draft`, one placeholder update entry), `txt/data/txt_schema.json` (generated from `TxtDocument.model_json_schema()` with `commands/schema.py`'s exact formatting: `$schema` = `GenerateJsonSchema.schema_dialect`, `$comment` = `SCHEMA_COMMENT_VERSION`, `json.dumps(..., indent=2, sort_keys=True) + "\n"`). Both markdown files parse green through `txt.models.v1.parser.parse_txt` and are byte-stable under parse -> re-render (`str(doc.body) == format_text(frontmatter.loads(text).content)`), pinning the mdformat-clean property in the tool tests. (4) Tests in `tests/txt/tools/` (82 new, one module per vcr counterpart: `test_create_txt.py`, `test_parse_txt.py`, `test_list_txt.py`, `test_list_txt_glob.py`, `test_get_txt.py`, `test_get_txt_example.py`, `test_get_txt_template.py`, `test_get_txt_schema.py`, `test__paths.py`, `test__io.py`, `test__lock.py`, `test__write.py`, `test_integration.py`), isolating via `SPECMGR_DOCS_DIR` exactly as `tests/vcr/tools/` does. The two vcr splice-indexing tests are adapted to pin the same raw/splice invariant against the shared `body_text`/`window_body` helpers directly (the generic `update` tool does not know `type="txt"` yet); the integration lifecycle stops before the generic tools for the same reason. (5) `tests/txt/conftest.py` (new): collection-time MCP-registration isolation -- pytest imports it before any `tests/txt` test module, and it pre-imports `txt.tools` with `server.mcp` temporarily swapped for a throwaway `MCPServer`, so the seven `@mcp.tool()` decorators bind the throwaway instead of the process-wide singleton (which `txt/__init__.py`'s vcr-precedent `from . import prompts, resources, tools` makes reachable from even the Phase 100 model tests' `import biz.dfch.specmgr.txt.models.v1`). Without it, `tests/test_schema_surface_registration.py::test_tool_total_is_115` failed in every xdist worker collecting `tests/txt` (122 != 115); with it the pinned surface is untouched in this phase (the seven tools join the real surface with the Phase 160 `server.py` registration). (6) Gate: `ruff format --check` (2176 files), `ruff check`, `vulture --min-confidence 60` (no new whitelist entries needed -- the `__all__` exports cover `txt_lock`/`invalidate_txt_cache` until Phase 130 consumes them), full `pytest -n auto --cov=src` (4984 passed, 18 skipped = the 4902 Phase-100 baseline + 82 new), and `specmgr docs` (539 module pages + `docs/GENERATED.md` regenerated drift-free, incl. the new `PagedResult[TxtSummary]` section in the `paged_result` page).

#### 2026-10-28 14:18:58.000Z - Phase 100 complete (models and parser, ACC-001..ACC-003)

Implemented Tasks 100.100-100.160. (1) Skeleton: `src/biz/dfch/specmgr/txt/` with `__init__.py` (docstring-only placeholder, no imports -- the `qa` first-phase precedent, so importing the package never forces the `mcp` extra), `models/` (`__init__.py` + `v1/`), and empty `tools/`/`resources/`/`prompts/`/`data/` sub-packages (license-header-only `__init__.py`s; `data/` is on disk but untracked by git until Phase 120's first data file lands) plus `tests/txt/` (`__init__.py`s mirroring `tests/vcr/`). (2) Models in `txt/models/v1/` mirroring `vcr` file-for-file: `frontmatter.py` (`TxtFrontmatter`, `type: txt`, closed three-value status `draft`/`progress`/`done` + the feat-189 C13 `json_schema_extra` `enum`), `body.py` (`TxtBody(MarkdownStr)` with the plan's verbatim boundary `get_extent` -- first top-level H2 whose text is `Updates` -- and the `text` computed field per the `UpdateEntryContent`/`IntroductionBody` idiom; `UpdateEntryContent`/`UpdateEntry`/`Updates` copied from `vcr`'s own classes, same entry heading regex, same computed `timestamp`/`title`, `Updates._validate_newest_first` delegating to the shared `models.md._ordering.validate_newest_first`; root `Txt(MarkdownSection1)` plain -- not `WithComment` -- with mandatory `body` then `updates`, `@alias(value=".+", type=AliasType.REGEX)`), `document.py` (`TxtDocument`), `parser.py` (model-level `parse_txt` + `_stringify_metadata`, `domain="txt"`; render is the engine's own `MarkdownStr.__str__` re-emission, as in every other whole-body domain -- `vcr/models/v1/parser.py` carries no `render` function of its own, per the plan's disambiguation), `summary.py` (`TxtSummary`, field-for-field `DocSummary` subclass like `VcrSummary`), `_util.py` (`SCHEMA_COMMENT_VERSION`). No engine change; no `txt` import anywhere outside `txt/` itself and its tests; no custom error wrapping (REQ-011). (3) Tests in `tests/txt/models/v1/`: `test_body.py` (44 tests/22 subtests -- the nine ACC-001 spike rows S1..S9 each a dedicated test, plus a block-quote-nested `## Updates` row pinning the `tok.level == 0` half of the boundary, the ACC-002 entry matrix, `model_dump` surfacing, and the full reference-body round-trip), `test_frontmatter.py` (14/18 subtests -- ACC-003: exactly `draft`/`progress`/`done` accepted, vcr-only/dec-only/feat-only statuses rejected), `test_parser.py` (19 tests -- ACC-003 document round-trips: `str(document.body)` byte-equal to the normalized body and parse->render->re-parse byte-stability, `model_dump` surfacing the body text, value + structural violations at document level). Every spike row reproduces: the implementation was validated against the real engine before the files were written, and the tests assert the engine's own default messages (REQ-011). (4) Gate: `ruff format --check` (2135 files formatted), `ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean -- `whitelist.py` gained a `txt (feat-229 Phase 1)` block; see the new Decisions Made entry on which of the four plan-named fields get new name lines), full `pytest -n auto --cov=src --cov-report=`: **4902 passed, 18 skipped** (the 18 skips pre-existing). Files: `src/biz/dfch/specmgr/txt/{__init__.py,models/__init__.py,models/v1/{__init__,_util,frontmatter,body,document,parser,summary}.py,tools/__init__.py,resources/__init__.py,prompts/__init__.py}`, `tests/txt/{__init__.py,models/__init__.py,models/v1/{__init__,test_body,test_frontmatter,test_parser}.py}`, `whitelist.py`.

#### 2026-10-28 13:30:00.000Z - Plan refined (feat-refiner pass, all findings applied)

The feat-refiner refinement pass found and this edit fixes: E1 -- the import-time domain-set asserts now land atomically in Phase 130 (the `list_references`/`_reference_graph` source-loader entries moved from Tasks 140.110/150.100 into 130.120, the `_GET_TOOLS` test entry into 130.130, and 140.110/150.100 re-scoped); G1-G4 -- the `specmgr-refs` skill + its pin test, `whitelist.py`, `test_get_reference_diagram.py` and the `general/tools/__init__.py`/`get_reference_diagram_all.py` docstrings added to the touchpoints and the owning tasks; D1 -- Task 160.130 reworded to the repo's real hook shape (the shared `files:` regex widened across the 13 existing occurrences + one new `specmgr-schema-txt-package` hook, not "the two `specmgr-schema-txt` hooks"); D2 -- the phantom `plantuml/`/UC-rulebook palette pin dropped from ACC-007 and Task 150.110; I1-I4 -- `set_status`'s second table + return-union member named, the env-var design note stated as a verified fact, the `LightGrey` colour pre-verified (see Palette note) and `_domains.py`'s own module docstring folded into Task 130.100. No task numbers added or renumbered.

#### 2026-10-28 12:00:00.000Z - Created

Plan drafted from the name/structure discussion and the parser spike. Reuses the existing open issue #229 instead of opening a duplicate; the domain key is `txt`, not the `doc` of the issue title.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-29 03:53:38.000Z - Phase 130: `tests/txt/conftest.py` deleted ahead of the recorded Phase 160 mandate (Consequence A's true trigger)

The Phase 110/120 recorded mandate said `tests/txt/conftest.py` "MUST BE DELETED in Phase 160, once Phase 160 registers `txt` on `server.py`'s bottom-of-file domain-import line". The actual trigger is earlier and does not depend on Phase 160 at all: the conftest's collection-time guard assert fires the moment any `biz.dfch.specmgr.txt.tools/resources/prompts` module is already in `sys.modules`, and this phase's own Task 130.100 registration (`general/tools/_domains.py`'s module-level `from ...txt.tools._io import load_by_id` / `from ...txt.tools._paths import txt_base_dir`) guarantees exactly that in every test process -- importing a submodule first executes `txt/__init__.py`'s vcr-precedent `from . import prompts, resources, tools` line, so by the time any conftest could run, the txt decorators have already registered on the REAL singleton and the throwaway pre-import would either trip the guard assert (workers that import the server before collecting `tests/txt`) or be a dead rebinding (the reverse worker order). The file was therefore deleted in Phase 130, with the assert left intact (weakening it remains forbidden -- the file simply does not exist any more). Consequences: (a) the live surface grows to 122 tools / 39 resources / 35 prompts immediately (measured 115/37/33 → 122/39/35 by importing the server with and without the edge); (b) Phase 160's `server.py` bottom-line `txt` import is a no-op re-import; (c) the conftest-removal note inside Phase 160's task text becomes moot (documented here rather than renumbered). This entry supersedes the Phase 160 removal mandate recorded on 2026-10-28.

#### 2026-10-29 03:53:38.000Z - Phase 130: surface pins move 115→122 (tools) and 37→39 (resources) via the `_domains` import edge

Per the orchestrator's prediction, `test_schema_surface_registration.py::test_tool_total_is_115` moved to `test_tool_total_is_122` (115 + the 7 txt tools) with the docstring extended by the import-edge rationale: once `_domains.py` imports `txt.tools._io`/`txt.tools._paths`, every process that imports `biz.dfch.specmgr.server` registers the 7 tools on the live `mcp` singleton ahead of Phase 160's own `server.py` line. The accompanying prediction that `test_resource_total_is_37` "STAYS 37 in this phase (txt's 2 resources + 2 prompts are not in any import chain until Phase 160's server.py import line)" is contradicted by the committed code: `txt/__init__.py`'s `from . import prompts, resources, tools` (the vcr/qa/sysrs precedent this feature's own Phase 110 decision adopted) pulls `txt.resources` in with `txt.tools` on the very same import edge -- which is exactly how the other 12 domains' resources already sit inside today's 37 (e.g. `specmgr://vcr/example` arrives via `_domains.py`'s existing `vcr.tools._io` import). Empirically, the edge adds 2 resources (`specmgr://txt/example`, `specmgr://txt/template`) and 2 prompts (`create_txt`, `update_txt`; no prompt-total pin exists). `test_resource_total_is_37` therefore moved to `test_resource_total_is_39`, with the same import-edge rationale recorded in its docstring. ACC-006 (the `server.py` bottom-line registration itself) stays unticked until Phase 160.

#### 2026-10-29 03:53:38.000Z - Phase 130: two domain-set asserts outside `general/tools/` forced early table fixes (config resource + reference-graph order)

Two hand-maintained tables are pinned against `ALL_DOMAINS` by asserts that fire at import/collection time, so their growth cannot wait for the phase the plan sequences them into -- leaving them stale would break ACC-010 (full suite green after every phase) the moment `txt` joins `ALL_DOMAINS`. (1) `general/resources/config.py`'s `domains` dict (module-scope `assert set(domains) == set(ALL_DOMAINS)` -- fires at `server.py` import, i.e. in every test process): the `txt` `DomainConfig` entry (shared `SPECMGR_DOCS_DIR`, `env_var_set=docs_dir_set`, no new env var) landed in Phase 130, and the txt block was added to `tests/fixtures/config-golden/specmgr-config.pre-migration.json` in the same edit (the golden's byte-identity test re-derives both temp-dir prefixes from the payloads themselves, so the addition is mechanical); the `config_info()` docstring's shared-env-var domain list gained `txt`. Phase 160's Task 160.110 is thereby narrowed to the README/server.json half of its env-registry coverage check. (2) `general/models/reference_graph.py`'s `_DOMAIN_ORDER` (the import-free module's one hand-listed constant, drift-pinned by `tests/general/models/test_reference_graph.py::test_domain_order_constant_matches_all_domains` against `ALL_DOMAINS`): `"txt"` was appended in Phase 130 (comment updated to 14-domain, noting the rulebook's palette amendment follows in Phase 150). The `("TXT", "LightGrey")` `_PALETTE` entry, the `specmgr://reference-graph` rulebook amendment, and the 15-entry agreement all stay in Phase 150: no Phase 130 test seeds a `txt` document into any diagram corpus, so no TXT node is ever rendered and every golden fixture stays byte-identical (verified by the full suite).

#### 2026-10-29 03:53:38.000Z - Phase 130: G1 instruction pins narrowed to the 13-file shared core; `_doc_paths.py` env description deferred to Task 160.140

(1) Once `test_agent_facing_wording.py`'s G1 tests iterate the grown `WHOLE_BODY_DOMAINS`, they check `txt/data/txt_update_instructions.md` (a Phase 120 artifact, outside this phase's allowed change set) against the shared pins. The file spells the local-splice-skip sentence in its own variant -- "Skip the schema fetch for a local splice (a line-range replace **or an `edit`**), where the raw body is already in context: `update` and `edit` both validate the result as a whole document before writing anything, so the skip is safe." -- so the old two-line pins (which assume the 12 other files' "`update` still validates the spliced result" wording) match only 12 of the 13 files. The pins were narrowed to the shared core across all 13 files: `_UPDATE_LOCAL_SPLICE_SKIP = "local splice (a line-range replace"`, a new `_UPDATE_RAW_BODY_IN_CONTEXT = "where the raw body is already in context"`, and `_UPDATE_SKIP_IS_SAFE = "whole document before writing anything, so the skip is safe"` -- the same documented-variant convention the file already uses for vcr's "Skip the schema fetch" vs "Skip the fetch" wording (both variants recorded in the constants' comments). The heading and `get_<d>_schema` pins needed no change (txt matches them verbatim); the G2 clause pins pass for txt's tool/prompt descriptions as written in Phase 110/120. (2) Task 130.120's "wire txt into `_doc_paths` (docstrings/messages)" resolves to nothing in this phase: the only domain enumeration in `_doc_paths.py` is the `_envregistry`-registered `SPECMGR_DOCS_DIR` description, which the plan itself sequences into Task 160.140 (alongside `server.json` and the README Environment-Variables section, keeping `tests/test_envregistry_*` green). Updating it in Phase 130 would break that coverage check early (it pins the description against the still-12-domain README/server.json text), so it stays stale until Phase 160 by design.

#### 2026-10-28 21:16:40.000Z - Phase 120: data files verified unchanged; schema re-verified in memory (the CLI entry is a Phase 160 artifact)

Both Phase-120 ordering nuances resolved without content changes. (1) Tasks 120.100's "author" verb: `txt_example.md`/`txt_template.md` already existed from Phase 110 (the "Packaged data files created in Phase 110" decision), and in-memory verification against every plan content requirement (free H2/H3 in the example body, the free-floating `REQ <uuid>` line, two newest-ordered update entries; the template's blind-text convention vs `vcr/data/vcr_template.md`) found all requirements met -- so Phase 120 **finalized them as-is, with zero byte changes**, deliberately keeping the Phase 110 byte-stability pins (`test_get_txt_example.py`/`test_get_txt_template.py`) unmodified rather than moving them. (2) Task 120.110's "via `specmgr schema --type txt`": that CLI entry does not exist until Phase 160 (Task 160.120 adds `generate_txt_schema` to `commands/schema.py`), so Phase 120 re-ran the generation through the **same in-memory mechanism** every `commands/schema.py` per-domain generator uses (`TxtDocument.model_json_schema()` + the `$schema`/`$comment` injections + `json.dumps(..., indent=2, sort_keys=True) + "\n"`) and confirmed the on-disk `txt/data/txt_schema.json` is **byte-identical** to it (independently of the already-existing `test_get_txt_schema.py::test_output_matches_regenerated_schema` pin). Phase 160's CLI run must reproduce the same bytes; if it does not, the defect is in the Phase 160 wiring, not the packaged file.

#### 2026-10-28 20:20:26.000Z - Phase 130 must switch `get_txt`'s path safety to `validate_id`

Phase 110's `get_txt` applies `assert_no_traversal` + `assert_uuid` from `general.tools._path_safety` directly (the documented composition above) because `validate_id("txt", ...)` cannot dispatch until Phase 130 registers `txt` in `general/tools/_domains.py`. For the Phase 130 implementer: **Task 130.120's own `_path_safety` wiring includes switching `get_txt`'s direct `assert_no_traversal` + `assert_uuid` composition to the shared `validate_id("txt", ...)` dispatcher call**, mirroring `get_vcr`'s own `validate_id("vcr", id)` call. The switch is behaviour-identical for every id value (`validate_id` composes exactly those two guards, in that order, for UUID-shaped domains), and it pins `txt` to the shared dispatcher so a future change to `validate_id`'s composition cannot silently bypass `txt`. No `get_txt` source change happens in Phase 110 or 120; `get_txt.py`'s own module docstring marks the two-primitive form as interim until that registration.

#### 2026-10-28 19:08:28.000Z - Packaged data files created in Phase 110 (ordering decision)

The plan places the data-file authoring in Phase 120 (Tasks 120.100/120.110), but the Phase 110 packaged-data tools (`get_txt_example`/`get_txt_template`/`get_txt_schema`) cannot be implemented or tested without the packaged files existing -- vcr's own history created its data files before its tools. So `txt_example.md`, `txt_template.md` and `txt_schema.json` are created in Phase 110 as valid, tested files (parse green through `txt.models.v1.parser.parse_txt`, byte-stable under parse -> re-render; the schema generated from `TxtDocument.model_json_schema()` with `commands/schema.py`'s exact formatting, byte-identity pinned in `test_get_txt_schema.py`), and Phase 120 re-verifies/finalizes them per Tasks 120.100/120.110 (and Phase 160's `generate_txt_schema` CLI entry must reproduce `txt_schema.json` byte-for-byte).

#### 2026-10-28 19:08:28.000Z - `get_txt` path safety via the two `_path_safety` primitives, not `validate_id("txt", ...)`

The plan says `get_txt` applies "the same `general/tools/_path_safety` guards as vcr (invalid id -> ValueError before any filesystem access)". VCR's `get_vcr` calls `validate_id("vcr", id)`, whose dispatch table (`general.tools._domains.UUID_DOMAINS`) does not contain `"txt"` until the Phase 130 registration -- calling `validate_id("txt", ...)` now would reject every id (even a valid UUID) with the unknown-type error, breaking the Phase 110 tool and its tests. `get_txt` therefore applies the two primitive guards `validate_id` composes for every UUID-shaped domain -- `assert_no_traversal(id)` plus `assert_uuid(id)`, in that order, both raised before any filesystem access -- which is byte-for-byte the same id-validation behaviour for every id value; once Phase 130 appends `"txt"` to `WHOLE_BODY_DOMAINS`, `validate_id("txt", ...)` becomes equivalent to it (and Task 130.120's "wire txt into `_path_safety`" is exactly that dispatch-table growth).

#### 2026-10-28 19:08:28.000Z - `tests/txt/conftest.py`: collection-time throwaway-`mcp` registration isolation

`txt` is not imported by `server.py` yet (Phase 160), but `txt/__init__.py` follows the vcr/qa/sysrs precedent of `from . import prompts, resources, tools`, so any import of any `biz.dfch.specmgr.txt` sub-package (the Phase 100 model tests import `biz.dfch.specmgr.txt.models.v1`) pulls `txt.tools` in at pytest collection time and its `@mcp.tool()` decorators register seven tools on the process-wide `server.mcp` singleton. That inflated the pinned surface in `tests/test_schema_surface_registration.py` from 115 to 122 tools (the test failed in the first full-suite run). `tests/txt/conftest.py` (imported by pytest before any `tests/txt` test module) pre-imports `txt.tools` with `server.mcp` temporarily swapped for a throwaway `MCPServer` instance (restored in `try`/`finally`), so the decorators bind the throwaway and the real singleton keeps the exact 115-tool surface until Phase 160 registers `txt` in `server.py`. The tool functions remain plain callables for the tests (the mcp SDK's `tool()` decorator returns the function unchanged). Phase 120 extends the same pre-import to `txt.resources`/`txt.prompts` when those sub-packages first register decorators (the pinned resource/prompt totals would otherwise inflate the same way). **Phase 160 removal mandate:** once Phase 160 registers `txt` on `server.py`'s bottom-of-file domain-import line, `tests/txt/conftest.py` **MUST BE DELETED** in that same phase — the throwaway pre-import would then be not just unnecessary but actively wrong (in every xdist worker the top-level `tests/test_*.py` modules that import `biz.dfch.specmgr.server` are collected before `tests/txt/`, so `txt.tools` is already in `sys.modules` bound to the real singleton, and the swap would rebind the tool modules to a dead instance, keeping `txt`'s tools off the real server surface). The conftest's collection-time guard assert is the deliberate loud tripwire for that moment: a collection-time `AssertionError` naming it in a Phase 160 run means the file was not removed, not a runtime bug — and no phase may "fix" the assert by weakening it instead of deleting the file (the mandate is stated in the conftest's own module docstring as well).

#### 2026-10-28 19:08:28.000Z - `txt/__init__.py` gains the vcr-precedent `from . import prompts, resources, tools`

Phase 100 left `txt/__init__.py` a docstring-only placeholder (the `qa` first-phase precedent). The vcr/qa/sysrs package-level precedent -- `from . import prompts, resources, tools  # noqa: F401`, so `import biz.dfch.specmgr.<domain>` registers everything the domain exposes -- is what `server.py`'s Phase 160 last-line import will rely on, and `qa` gained exactly this line in its own tools phase (Phase 4). Adopting it now (the two still-empty sub-packages import harmlessly and register nothing) means Phase 160 needs no `txt/__init__.py` change; the import-behaviour consequence (importing `biz.dfch.specmgr.txt` forces the `mcp` extra, like `vcr`/`qa`/`sysrs` do today) is identical to the precedent, and the `tests/txt/conftest.py` isolation above contains the one test-visible side effect (see that entry).

#### 2026-10-28 14:18:58.000Z - whitelist.py: new name lines only for `body`/`title` of the four plan-named txt fields

Task 100.160 names four fields for the `txt` whitelist block (root `body`/`updates`, `UpdateEntry`'s computed `timestamp`/`title`). Verified against vulture before adding anything: with the whitelist removed entirely, none of the four names is flagged in `src/` -- `updates` and `timestamp` are already listed once (lines from the shared block and the `sop` block), and `body`/`title` are incidentally marked used by unrelated references (the `body` local in every domain parser's `parse_<d>`, the `title=` MCP tool-decorator kwargs -- the same mechanism the file's own `config`/`base_dir` note documents). Re-listing `updates`/`timestamp` would violate the file's "each name is listed once" convention, so the new `txt (feat-229 Phase 1)` block adds `body` and `title` only, with a comment pinning all four fields' (de)serialization-only nature; vulture stays green with or without the two new lines (checked both ways).

#### 2026-10-28 12:00:00.000Z - Palette colour LightGrey for TXT

`LightGrey` is a valid PlantUML colour name not used by any existing palette entry; fixed in the plan so implementation does not pause to ask. Inserted after `SYSRS`, before `UNRESOLVED`.

#### 2026-10-28 11:55:00.000Z - txt is a reference source and a reference target

`TXT <uuid>` is added to the tag vocabulary, with a `_load_txt` resolver, so a `txt` can be referenced and shown as a graph node; a generic catch-all that nothing can point to would be of limited use. Requires the palette amendment.

#### 2026-10-28 11:50:00.000Z - Mandatory body, engine-default errors, no extra policies

The body is mandatory (an empty `txt` makes no sense) and `## Updates` is mandatory (it anchors the "last H2" boundary). Comment-only and whitespace-only-after-comment bodies follow current parser behaviour with no extra validator. Newest-first ordering is enforced exactly as for the other types (shared helper), and the engine's default error messages are kept; the template and example document the structure.

#### 2026-10-28 11:40:00.000Z - Layout: free body with H2..H6, `## Updates` last, one H1

Chosen over a second `# Updates` H1 (convention break, new non-heading root) and over a "last H2 must be Updates" check (larger override, fence edge cases). The first top-level `## Updates` is the body boundary; duplicates and trailing H2s fall out of the engine's leftover-text check. The root is a plain `MarkdownSection1`, not the `WithComment` variant.

#### 2026-10-28 11:30:00.000Z - Status vocabulary draft / progress / done

Lighter than `vcr`'s four-value lifecycle, suited to an unstructured catch-all document.

#### 2026-10-28 11:20:00.000Z - Domain key txt

`doc` clashes with `docs/` and the shared `Doc*` infrastructure names, `md` with `models/md/`, `not` is a Python keyword (the package could not be imported), `rpt` implies a report. `txt` fits the three-letter style and collides with nothing; the `.md` content versus "txt" mismatch is accepted as cosmetic.

#### 2026-10-28 11:10:00.000Z - Reuse issue #229, no QA, no DEC

The open point in #229 (narrow review/audit scope versus general catch-all) is resolved as general catch-all. A QA interview is skipped because the design space is small and was settled directly; no DEC is recorded for the name. The earlier from-scratch domains (`sop`, `vcr`) likewise went straight to a feature plan.

### Related PRs / Commits

- [Issue #229](https://github.com/dfch/biz.dfch.SpecMgr/issues/229): tracking issue (originally "Add a generic 'doc' artifact type"), with the resolved-decisions comment.

### More Information

Closest precedents: `.specmgr/feat/feat-33-vcr/README.md` (domain shape, `Updates`), `.specmgr/feat/feat-30-sop/README.md` (from-scratch dispatch-only domain), `.specmgr/feat/feat-114-qa-introduction-any-markdown/README.md` and `.specmgr/feat/feat-180-updates/README.md` (opaque any-markdown leaves), `.specmgr/feat/feat-207-reference-graph/README.md` (palette and rulebook amendments).
