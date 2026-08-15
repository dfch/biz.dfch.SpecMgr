# Plan: Document SpecMgr Design Decisions as ADRs

## Overview

Capture the key design decisions from `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` and `AGENTS.md` as a set of Architecture Decision Records (ADRs) in the specmgr MCP server itself. Each ADR will be self-contained (no forward-references to plan sections), and the source documents will be back-referenced to point to the corresponding ADRs.

## Phase A: Create 12 ADRs

All ADRs created with:
- `status: "accepted"`
- `decision_makers: "dfch"`
- `consulted`, `informed`, `date`: omitted (blank)
- Self-contained body (no citations of plan §-numbers or `AGENTS.md` line references)
- `Option` sub-sections via `specmgr_option_create` where the source material explicitly weighed alternatives with pros/cons

### ADRs to Create

1. **Base the ADR template on MADR 4.0.0**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §2
   - Context: Need a standard ADR template for the SpecMgr project
   - Decision: Adopt MADR 4.0.0 as the base, with custom Pydantic-enforced extensions (`id`, `version`)
   - Options: MADR 4.0.0 vs. other ADR formats (Y-Statements, other templates)

2. **Author/edit ADRs only through MCP structured tools, never raw markdown**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §1
   - Context: LLM-driven ADR management must be reliable and auditable
   - Decision: Expose only MCP tools (`create_adr`, `update_section`, `option_*`, etc.), never allow the LLM to edit raw markdown directly
   - Options: Raw markdown editing vs. structured MCP tools

3. **Frontmatter extension fields (`id`, `version`) + whole-object full-replace update contract**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §3, §9a
   - Context: Need system-owned metadata and versioning; update semantics must be clear
   - Decision: Extend MADR frontmatter with `id` (server-assigned UUID, system-managed) and `version` (specmgr schema version); use whole-object full-replace for updates, but `id` is re-injected by the tool and never settable by the caller
   - Options: Partial/patch updates vs. whole-object replace; system-owned `id` excluded from user updates vs. trusting caller-submitted `id`

4. **Generic `update_section(key, value)` with deletion sentinel + mandatory-section rejection**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §4
   - Context: Body sections (title, context, drivers, outcome, etc.) must be independently editable with clear semantics for deletion
   - Decision: One generic `update_section(key, value)` tool for all whole-section body edits; empty string / whitespace-only / literal `"REMOVE"` acts as deletion sentinel; mandatory sections (title, context, outcome, considered-options) reject deletion with an error
   - Options: Per-field dedicated tools vs. one generic keyed tool; silent drop vs. explicit deletion sentinel vs. separate delete tool; allow deleting mandatory sections vs. reject with error

5. **"Pros and Cons of the Options" as a derived container with a dedicated Option sub-API**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §5
   - Context: Options need flexible, independent management without coupling to the "Considered Options" prose section
   - Decision: "Pros and Cons" heading is auto-rendered iff ≥1 `Option` sub-section exists; dedicated API (`option_list`, `option_create`, `option_read`, `option_update`, `option_delete`) manages options; no renumbering on delete (monotonic counter leaves gaps); freeform content blob (no enforced Good/Bad/Neutral structure); drift between "Considered Options" text and `Option` collection is accepted
   - Options: Manual editing via `update_section` vs. dedicated `option_*` API; renumber-on-delete vs. leave gaps; enforce consistency vs. accept drift

6. **Domain-tree hierarchy code organization**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §6; `.specmgr/feat/feat-9-doc-in-specmgr/refactor-domain.md` (entire document)
   - Context: Initially, `tools/`, `prompts/`, `resources/` were top-level packages with domain sub-packages (`tools/adr/`, etc.). As more document types are planned (`req`, `uc`, `ac`), this scattered each domain across three unrelated locations
   - Decision: Reorganize as domain-first: `adr/` becomes a top-level package containing `adr/{tools,prompts,resources}/` sub-packages. `models/` stays shared (schema layer: Pydantic models, parser, renderer, mutations—no MCP dependency) with internal domain organization (`models/adr/`, later `models/req/`, etc.) and major-version sub-packages (`models/adr/v1/`, `models/adr/v2/`). Mutation logic lives as pure free functions in `models/adr/v1/mutations.py` (not as Pydantic model methods), taking and returning whole `Adr` objects. Future document types (`req`, `uc`, `ac`) repeat the same layout: domain-top-level with nested `{tools,prompts,resources}/` and shared-`models/` schema layer
   - Options: Interface-layer-first (`tools/adr/`, `prompts/adr/`) vs. domain-first (`adr/{tools,prompts,resources}/`); mutation logic as Pydantic methods vs. pure free functions; full wholesale `vN` duplication per major version vs. minimal diff (only changed classes in `vN`, import unchanged classes from `vN-1`)

7. **Filesystem is the sole source of truth — no in-memory id→document cache**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §7, §9a
   - Context: An MCP server is a long-running process; users may hand-edit ADR files concurrently with LLM tool calls. Caching risks staleness and conflicts
   - Decision: Every tool call re-reads and re-parses current on-disk state before acting. No in-memory cache of parsed `Adr` objects keyed by id. The `.md` file on disk is the sole source of truth
   - Options: Server-side cache (id → `Adr` object) vs. re-read/re-parse/re-render/re-write on every call

8. **id/filename/addressing scheme: server-generated UUID, `{id}-{slug}.md`, directory-scan resolution**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §9a
   - Context: Tools need a stable, unique way to address ADRs. Filenames must be human-readable but not rely on sequential counters
   - Decision: `id` is a server-generated UUID string (created once by `create_adr`, never reassigned). Filename is `{id}-{slug}.md` where `slug` is derived from `title` at creation time. id→path resolution is done via directory scan + frontmatter parse (no cached index) on every call. Base directory is configurable via `SPECMGR_ADR_DIR` environment variable (default `./docs/adr`). Option numbering in the dynamic `Option N` collection is monotonically increasing and never reused; deleting an option leaves a gap
   - Options: Sequential counter filenames vs. UUID-prefixed filenames; cached id→path index vs. fresh directory scan; CLI-arg vs. env-var config

9. **Expose listing/by-id reads as MCP resources in addition to tools**
   - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §8, §9a
   - Context: Different client use cases: explicit tool invocation vs. context-attachment without a round-trip
   - Decision: Implement both `list_adrs` and `get_adr(id)` as tools. Additionally, expose read-only MCP resources: `specmgr://adr/list` (resource) and `specmgr://adr/{id}` (template resource). Resources use the same underlying id-resolution logic as tools (directory scan, no cache), just exposed via the MCP resource interface
   - Options: Tools only vs. tools + resources for the same reads

10. **Parse→validate→render pipeline library choices, no AST-preserving round-trip**
    - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §7
    - Context: Need to split/parse YAML, parse markdown body, validate against schema, and regenerate the complete file
    - Decision: Use `pydantic` for Frontmatter and Body models; `python-frontmatter` for splitting the YAML header; `markdown-it-py` for walking the markdown token stream to locate fixed-heading sections and the dynamic `Option N` collection. Rendering is deterministic template-based (not an AST serializer), which is sufficient because the validator/renderer define the canonical form; arbitrary human formatting outside the schema is not a preservation requirement
    - Options: `pydantic` + `python-frontmatter` + `markdown-it-py` + template rendering vs. `PyYAML` directly + different markdown parsing vs. `remark`-style AST-preserving round-trip

11. **Narrated prompt surface driving the tool sequence, plus step-gated test variants**
    - Source: `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §8, §11
    - Context: LLMs need guidance on which tools to call, in what order, to draft or revise an ADR. Test whether prompt text alone can enforce a fixed sequence without tool-side validation
    - Decision: Implement `@mcp.prompt()` surfaces: `create_adr(topic, decision_makers?, consulted?, informed?)` and `update_adr(id, instructions?)` return plain instructional text guiding the LLM through the tool sequence (never tool calls themselves). Additionally, register step-gated test variants (`create_adr_test`, `update_adr_test`) with hard numbered `GATE 0..GATE N` blocks, explicit exit conditions, and standing "never fabricate a value" instructions for A/B comparison of compliance
    - Options: Prompt-text guidance alone vs. tool-side Pydantic validation vs. real MCP elicitation (client-side support not yet wired up); single narrated prompt vs. narrated + step-gated variants

12. **Enforce doc generation/lint/tests locally via pre-commit hook, not just CI**
    - Source: `AGENTS.md` § "CI / Release"
    - Context: Broken tests, drift in generated docs, and lint failures should be caught locally before pushing, not just in CI
    - Decision: Register a pre-commit hook (via `.pre-commit-config.yaml`) that runs `ruff format`, `ruff check`, full `unittest` suite (scoped to changed Python files), and `specmgr docs` (validate generated docs drift) before every commit. Prevents broken commits from being pushed; catches issues locally where they are faster to fix
    - Options: Pre-commit hooks vs. CI-only enforcement

## Phase B: Back-reference + Cleanup

### Back-reference insertion
Edit `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` and `AGENTS.md` in place: insert a short parenthetical at each relevant paragraph/heading linking to the corresponding ADR. Format: `(ADR <id>: "<title>")`.

### Delete `.specmgr/feat/feat-9-doc-in-specmgr/refactor-domain.md`
Once ADR #6 is written, delete `.specmgr/feat/feat-9-doc-in-specmgr/refactor-domain.md`. Its content is fully captured by the ADR; no back-reference is needed since the file is removed entirely. Before deletion, confirm no other file references `.specmgr/feat/feat-9-doc-in-specmgr/refactor-domain.md`.

## Phase C: Verify

- Run `specmgr_validate_adr` on each of the 12 new ADR ids to ensure they parse and validate cleanly.
- Sanity-check `AGENTS.md` and `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` read cleanly after back-reference insertions.
- Confirm `.specmgr/feat/feat-9-doc-in-specmgr/refactor-domain.md` deletion leaves no dangling references.

## Summary

This process converts implicit design knowledge in planning documents into explicit, versionable Architecture Decision Records stored in the specmgr MCP system itself—the same system they document. The source documents are then updated to reference these ADRs, creating a bidirectional link between design rationale and implementation guidance.
