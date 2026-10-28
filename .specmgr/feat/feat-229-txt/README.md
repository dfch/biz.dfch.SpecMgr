---
classification: null
created: '2026-10-28T09:42:29.469+01:00'
id: feat-229-txt
status: planning
type: feat
updated: '2026-10-28T09:42:29.469+01:00'
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

- [ ] ACC-001: Verifies REQ-001, REQ-002, REQ-003 -- a parser test matrix over `tests/txt/models/v1/` covers: text-only body, body with free H2/H3 and lists, fenced `## Updates` inside the body (accepted), empty body (rejected), whitespace-only body (rejected), comment-only body (accepted), missing `## Updates` (rejected), duplicate `## Updates` (rejected), H2 after `## Updates` (rejected).
- [ ] ACC-002: Verifies REQ-004 -- tests cover entry heading shape (both `-` and `:` separators, `T` and space date separators, `Z` and offset timezones), out-of-order entries rejected, equal timestamps accepted, zero entries rejected, empty entry content rejected, and the computed `timestamp`/`title` fields.
- [ ] ACC-003: Verifies REQ-005, REQ-006 -- `TxtFrontmatter` accepts exactly `draft`/`progress`/`done` and rejects other statuses; a parsed document's `model_dump()` surfaces the body text and a full-document round-trip is byte-stable.
- [ ] ACC-004: Verifies REQ-007 -- `test__domains.py`, `test_update.py`, `test_edit.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py` and `test_validate.py` (and their sibling similarity/`list_references` tests) include `txt` cases, and no per-domain `*_txt` mutation tool exists.
- [ ] ACC-005: Verifies REQ-008 -- `tests/txt/` covers every tool, both resources and both prompts, including the `get_txt(raw=True, numbered=True)` windowing and the `ParseFailureResult` channel for a broken document.
- [ ] ACC-006: Verifies REQ-009 -- `test__references.py` and `test_list_references.py` cover `TXT <uuid>` extraction, a `_load_txt` resolution (found and not-found rows), and a `txt` source document listing a free-floating `REQ <uuid>`; the import-time `_SOURCE_LOADERS`/`ALL_DOMAINS` assert holds.
- [ ] ACC-007: Verifies REQ-010 -- the palette tuple, the rulebook (`general_reference_graph.md`) with its dated amendment note, `test_reference_graph.py`/`test__reference_graph.py`/`test_reference_graph_subset.py`, the golden fixtures and `plantuml/` structure expectations all agree on 15 entries with `("TXT", "LightGrey")`, and a diagram containing a TXT node passes `validate_plantuml`.
- [ ] ACC-008: Verifies REQ-011 -- no `txt`-specific error-message wrapping exists beyond the shared `wrap_tool_errors` context, and the packaged `txt_template.md`/`txt_example.md` parse and validate green through `validate(type="txt", full=True)`.
- [ ] ACC-009: Verifies REQ-012 -- `specmgr schema`, `specmgr docs`, `specmgr mcp-docs` and the config-golden test show no drift, `tests/test_envregistry_*`, `tests/test_schema_surface_registration.py` and `tests/test_agent_facing_wording.py` pass, and `server.py`'s docstring lists every new tool/resource/prompt.
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

Documents live flat under the shared docs root as `docs/txt/txt-{uuid}-{slug}.md`, using the shared `SPECMGR_DOCS_DIR`-rooted default like `req`/`vcr` (no dedicated `SPECMGR_TXT_DIR` variable is introduced unless the `vcr`/`sysrs` precedent turns out to have one, in which case follow that precedent exactly). ids are server-generated UUIDs.

#### Palette

`TXT` is `LightGrey` (a PlantUML-recognised colour name, not used by any of the existing 14 entries: LightYellow, LightBlue, Pink, Honeydew, LemonChiffon, LightCoral, Lavender, Orange, LightGreen, PowderBlue, PaleTurquoise, Khaki, Thistle, DarkRed). The colour is fixed here so implementation never stops to confirm it.

#### Cross-cutting touchpoints (from a grep for `sysrs`/`vcr` outside the domain package)

`general/tools/`: `_domains.py`, `_references.py`, `list_references.py`, `_path_safety.py`, `_listing.py`, `_doc_paths.py`, `_similarity_corpus.py`, `update.py`, `edit.py`, `set_status.py`, `set_classification.py`, `delete.py`, `validate.py`, `find_related.py`, `find_similar_text.py`, `get_reference_diagram.py`, `_reference_graph.py`; `general/models/`: `reference_graph.py`, `reference.py`, `similarity_hit.py`, `update_result.py`, `parse_failure_result.py`; `general/data/general_reference_graph.md`, `general_repair_instructions.md`; `general/prompts/repair.py`; `general/resources/config.py`, `models/config_info.py`; `commands/schema.py`, `commands/diagram.py`; `models/md/` docstrings that enumerate domains; `server.py`; `pyproject.toml`; `server.json`; `.pre-commit-config.yaml`; `.github/workflows/ci.yml`; `README.md`; `AGENTS.md`; `CHANGELOG.md`; `.specmgr/conventions.md`; `.opencode/skill/repair/SKILL.md`, `.opencode/agent/ref-finder.md`, `.opencode/agent/doc-repairer.md`, `.opencode/command/refs.md`, `.opencode/command/repair.md`. The task list below groups them; before editing, re-run the grep to catch drift since this plan was written.

### Related Decisions

- ADR ece4554b-725c-4f76-bc04-5d2b760363d2: domain-first hierarchy for tools/prompts/resources.
- ADR 36905d5b-8057-4294-8665-c7eed5534db0: generic type-dispatched update/status tools; new domains register, not add tools.
- ADR c4efbde6-fd19-4aa8-8668-95316ed62dcc: single source of truth for the document-type domain-name set.
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: per-domain content-hash-validated doc cache; the new domain gets its own `tools/_cache.py` singleton.

### Task List

#### Phase 100: Models and parser

- [ ] Task 100.100: Create the `txt/` package skeleton (`__init__.py`, `models/v1/`, `tools/`, `resources/`, `prompts/`, `data/`) and `tests/txt/` mirroring `vcr/`
- [ ] Task 100.110: Implement `TxtFrontmatter` (`type: txt`, status `draft`/`progress`/`done`, standard fields, optional `classification`)
- [ ] Task 100.120: Implement `TxtBody` with the boundary `get_extent` and the `text` computed field
- [ ] Task 100.130: Implement `UpdateEntryContent`, `UpdateEntry`, `Updates` (copied from `vcr`, shared `validate_newest_first`)
- [ ] Task 100.140: Implement the root `Txt(MarkdownSection1)` (plain root, mandatory `body` and `updates`), `TxtDocument`, `parse_txt`/`render` and the `TxtSummary`
- [ ] Task 100.150: Write the parser test matrix from ACC-001 to ACC-003 (the 9 structural cases, the entry cases, frontmatter, round-trip, `model_dump`)
- [ ] Task 100.160: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 110: Tools

- [ ] Task 110.100: Add `txt/tools/` support modules (`_paths.py`, `_io.py`, `_lock.py`, `_cache.py`, `_write.py`) following `vcr`
- [ ] Task 110.110: Implement `create_txt` and `parse_txt` with the non-raising `ValidateResult` channel
- [ ] Task 110.120: Implement `list_txt` (paged, inline failed rows with resolved `path`) and `get_txt` (`raw`/`offset`/`limit`/`numbered`, `ParseFailureResult`)
- [ ] Task 110.130: Implement `get_txt_example`, `get_txt_template`, `get_txt_schema`
- [ ] Task 110.140: Write `tests/txt/tools/` for every tool, including the broken-document and path-safety cases
- [ ] Task 110.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 120: Data, resources and prompts

- [ ] Task 120.100: Author `txt_template.md` and `txt_example.md` (the example demonstrates free H2/H3 in the body, a free-floating `REQ <uuid>` reference and two ordered update entries)
- [ ] Task 120.110: Generate `txt_schema.json` (packaged copy) via `specmgr schema --type txt`
- [ ] Task 120.120: Implement `specmgr://txt/example` and `specmgr://txt/template` resources
- [ ] Task 120.130: Author `txt_create_instructions.md`/`txt_update_instructions.md` and implement the `create_txt`/`update_txt` prompts (`create_txt` checks `list_txt` for a near-duplicate; `update_txt` names the generic `update`/`edit`/`set_status` tools with `type="txt"`)
- [ ] Task 120.140: Write `tests/txt/resources/` and `tests/txt/prompts/`
- [ ] Task 120.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 130: Generic tool registration

- [ ] Task 130.100: Append `txt` to `WHOLE_BODY_DOMAINS` and add its `WholeBodyDomain` adapter in `general/tools/_domains.py`
- [ ] Task 130.110: Add the `txt` adapter to each of `update`, `edit`, `set_status`, `set_classification`, `delete`, `validate`
- [ ] Task 130.120: Wire `txt` into `_path_safety`, `_listing`, `_doc_paths` (docstrings/messages), the similarity corpus, `find_related`/`find_similar_text`, and write-path cache warming
- [ ] Task 130.130: Extend the generic-tool tests (`test__domains.py`, `test_update.py`, `test_edit.py`, `test_set_status.py`, `test_set_classification.py`, `test_delete.py`, `test_validate.py`, `test_doc_cache_write_wiring.py`, similarity tests) with `txt` cases
- [ ] Task 130.140: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 140: Reference type

- [ ] Task 140.100: Add `"txt"` to `_UUID_REFERENCE_TYPES`, implement `_load_txt` and its `_TARGET_RESOLVERS` entry in `general/tools/_references.py`, and update the module docstring's tag-vocabulary text
- [ ] Task 140.110: Add the `txt` source loader to `list_references.py` (satisfies the import-time `_SOURCE_LOADERS`/`ALL_DOMAINS` assert) and update `ReferenceRow`/related docstrings
- [ ] Task 140.120: Update `test__references.py`, `test_list_references.py` and any drift test pinning the tag list; add a `txt` source document test with a free-floating `REQ <uuid>`
- [ ] Task 140.130: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 150: Reference-graph palette

- [ ] Task 150.100: Add `("TXT", "LightGrey")` to `_PALETTE` (after `SYSRS`, before `UNRESOLVED`) and `txt` to the graph domain tuple in `general/models/reference_graph.py`, and wire `get_reference_diagram`/`_reference_graph.py`/`commands/diagram.py`
- [ ] Task 150.110: Amend `general/data/general_reference_graph.md` (palette table, entry count 14 to 15, dated amendment note) and keep the `specmgr://uc/plantuml` structure-checker expectations consistent
- [ ] Task 150.120: Update `test_reference_graph.py`, `test__reference_graph.py`, `test_reference_graph_subset.py` and the golden fixtures; add a diagram test containing a TXT node validated by `validate_plantuml`
- [ ] Task 150.130: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 160: Server and build registration

- [ ] Task 160.100: Register the `txt` package in `server.py` (last-line import, module docstring listing of every new tool/resource/prompt)
- [ ] Task 160.110: Add `txt` to the `specmgr://config` resource and `models/config_info.py`, and refresh the config golden under `tests/fixtures/config-golden/`
- [ ] Task 160.120: Add `generate_txt_schema` and the `"txt"` entry to `commands/schema.py`; generate `docs/txt_schema.json` and `txt/data/txt_schema.json`
- [ ] Task 160.130: Add `biz.dfch.specmgr.txt` package data to `pyproject.toml`, the `txt/models/v1` path to every `.pre-commit-config.yaml` `files:` regex plus the two `specmgr-schema-txt` hooks, and the matching CI steps in `.github/workflows/ci.yml`
- [ ] Task 160.140: Update domain lists in `server.json` and `_doc_paths.py` env-var descriptions (keep `tests/test_envregistry_*` green)
- [ ] Task 160.150: Phase-end gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`

#### Phase 170: Documentation and agent text

- [ ] Task 170.100: Add the `txt` bullet to `AGENTS.md` (domain list, generic-tool `type` enumerations, reference-tag vocabulary, palette count) and update `.specmgr/conventions.md` if it enumerates domains
- [ ] Task 170.110: Update `README.md` (domain list, Environment Variables section if affected) and add a `CHANGELOG.md` `[Unreleased]` entry
- [ ] Task 170.120: Update the agent/skill/command text that enumerates domains (`repair` skill and `doc-repairer`/`ref-finder` agents, `/refs` and `/repair` commands, `general_repair_instructions.md`, `general/prompts/repair.py`)
- [ ] Task 170.130: Regenerate `docs/api/`, `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); confirm `tests/test_schema_surface_registration.py` and `tests/test_agent_facing_wording.py` pass
- [ ] Task 170.140: Final gate: `ruff format --check`, `ruff check`, `vulture`, full `pytest`, `specmgr docs`/`schema`/`mcp-docs` drift checks, and set this feature's status to `review`

## Progress

### Current Status

**As of 2026-10-28**: Planning complete, nothing implemented. The structure was validated by an in-memory spike against the real `models/md` engine (see Design Notes); all decisions are recorded below and in the comment on issue #229. Next step: Phase 100.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-28 12:00:00.000Z - Created

Plan drafted from the name/structure discussion and the parser spike. Reuses the existing open issue #229 instead of opening a duplicate; the domain key is `txt`, not the `doc` of the issue title.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

tbd
