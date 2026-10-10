---
classification: null
created: '2026-10-09T08:16:24.927+02:00'
id: feat-207-reference-graph
status: planning
type: feat
updated: '2026-10-10T08:01:22.119+02:00'
version: 1.0.0
---

# Feature: PlantUML Reference Graph Diagrams

## Plan

### Overview

GitHub issue #207: specmgr artifacts already carry deterministic cross-references (the 11-tag `<TYPE> <id>` vocabulary behind the `list_references` tool, `general/tools/_references.py`), but there is no way to *visualize* the resulting dependency network. `list_references` is single-document and outgoing-only, and both reverse lookup and graph construction were explicitly deferred: by feat-144-ref-artifact ("Reverse references (finding documents that reference a given artifact)") and by feat-152-ref-skill ("New MCP capabilities (e.g. `reverse`/`depth` parameters on `list_references`) -- client-agnostic feature work, its own issue if pursued"). This feature is that issue.

This feature renders the network as a deterministic PlantUML component diagram: one node per artifact (label = the document title, truncated by the `SPECMGR_DIAGRAM_MAX_TITLE` env var, default 40), a stereotype + colour per artifact type (a frozen 14-entry palette via a `skinparam component { backgroundColor<<TYPE>> ... }` block), nodes grouped into per-domain `package` blocks, one edge per unique reference `{src} --> {dst} : refers to` (the referenced item carries the incoming arrow), every edge that lies on a cycle (SCC-based; self-loops included) drawn with a red arrow, and every reference whose target cannot be resolved on disk drawn as a top-level `<<UNRESOLVED>>` node. FEAT artifacts can be excluded wholesale via an `include_feat` switch (MCP) / `--no-feat` flag (CLI). The diagram title is overridable; defaults: the source document's H1 (source-centred) or `Reference Graph` (registry-wide).

It reuses the feat-185-uc-diagrams PlantUML stack almost as-is (the import-free `plantuml/` package, the strict validation chain, the golden-pinning + rulebook + CLI + host-surface discipline) and ships on that precedent's four layers: a pure library (graph model + deterministic renderer + builders), the spec (a `specmgr://reference-graph` rulebook + one dated structure-checker amendment), the MCP surface (`get_reference_diagram` / `get_reference_diagram_all`), and the CLI (`specmgr diagram refs`) + a thin host surface (a `specmgr-refs` skill row + `/ref-graph` command).

### Requirements

- REQ-001: A pure, stdlib-only `general/models/reference_graph.py` holding the frozen dataclasses `GraphNode` (`type`, `id`, `title | None`), `GraphEdge` (`source_type`, `source_id`, `target_type`, `target_id`) and `ReferenceGraph` (`title`, `nodes`, `edges`), plus `render_reference_graph(graph, *, max_label: int = 40) -> str` emitting the frozen layout of Design Notes §2 -- deterministic and byte-stable, no `mcp`/tools-layer imports (the import-free bar of the `plantuml/` package).
- REQ-002: A `general/tools/_reference_graph.py` holding `build_source_graph(source_type, source_id, *, depth=1, reverse=False, include_feat=True) -> ReferenceGraph` and `build_registry_graph(*, include_feat=True) -> ReferenceGraph`, reusing `find_references`/`resolve_reference` and the `list_references` source-scan legs (the per-domain cache-aware read paths for the 12 whole-body domains; the never-cached adr leg, `adr` being permanently DocCache-excluded per ADR bfd76370), with the Design Notes §3 construction semantics; the builders never raise for target-side content (a dangling target becomes an unresolved node) while a missing source raises the source domain's `XNotFoundError` and an existing-but-broken source raises the domain's parse error (the tool layer converts it to `ParseFailureResult`).
- REQ-003: Cycle detection in the renderer: an edge is on a cycle iff it is a self-loop or both endpoints are in the same strongly connected component of size ≥ 2 (iterative Tarjan, stdlib, deterministic node order; Design Notes §4 carries the exact characterization and proof sketch); on-cycle edges render with the red-arrow syntax frozen by the Phase 100 real-parser gate (candidate `-[#red]->`), off-cycle edges render with plain `-->`.
- REQ-004: MCP tool `get_reference_diagram(type: WholeBodyOrAdrType, id: str, depth: int = 1, reverse: bool = False, include_feat: bool = True, title: str | None = None) -> str | ParseFailureResult` -- `type` is the `_domains.py` `WholeBodyOrAdrType` alias (the `set_status` tool's own spelling, not a re-unpacked `Literal[ALL_DOMAINS]`); the `_path_safety.validate_id` guard (a `ValueError` before any filesystem access -- for `type="feat"` a bare `feat-NNN` is a wrong-format id, not a normalization candidate, the `get_feat`/`list_references` parity; the rulebook and the tool docstring point at `list_feat` to discover the exact id); a missing source raises the source domain's `XNotFoundError`; an existing-but-broken source returns the non-raising `ParseFailureResult` (the feat-150 precedent); `depth` outside 1..5 is a `ValueError` (pre-filesystem, the §7 guard order); `reverse=True` is additive (the forward expansion to `depth` plus the direct incoming edges to the source, Design Notes §3); the success return is the byte-stable PlantUML source (title default: the source's H1).
- REQ-005: MCP tool `get_reference_diagram_all(include_feat: bool = True, title: str | None = None) -> str` -- the registry-wide graph; it never raises for content (broken documents are skipped); title default `Reference Graph`.
- REQ-006: A dated structure-checker amendment (Design Notes §6), landing in one commit with the rulebook note: (a) `component` added to `_DECLARATION_PATTERN`'s keyword set; (b) the alias grammar (frozen shapes + legacy walk) accepts a bracketed alias `[<no whitespace, no brackets>]`, recorded in the declared set unbracketed; (c) `_strip_operand` also unwraps a fully-bracketed token; (d) the dated note in `uc/data/uc_plantuml.md` §6.1; (e) the `plantuml/structure.py` module docstring's frozen-grammar enumeration updated (the declaration keyword list gains `component`, the alias grammar the bracketed shape); (f) the real-parser gate (env-gated) verifying the full emitted subset renders valid; (g) the negative controls still error; the existing UC renderers' output stays byte-identical (regression-pinned by the existing goldens).
- REQ-007: The rulebook: packaged `general/data/general_reference_graph.md` served as `specmgr://reference-graph` (raw markdown passthrough, the `specmgr://dtais`/`specmgr://rasci` style), freezing the palette, the node/alias/label/sanitisation rules, the title override + defaults, the truncation rule + the env var, the FEAT-exclusion semantics, the bare-`feat-NNN` source-id rejection (with the `list_feat` discovery pointer), the cycle rule + red syntax, the construction semantics, and the file layout -- and pointing at the UC rulebook §3-§6 for the validation chain reused as-is.
- REQ-008: The `SPECMGR_DIAGRAM_MAX_TITLE` env var (int, default 40) read by a shared helper `general/tools/_diagram_config.py` (the `plantuml/chain.py` `ENV_VAR_*` + `os.environ.get` idiom; the int parse with fallback + validity flag is new) used by both MCP tools and the CLI; a set-but-invalid value (empty, non-int, or < 1) falls back to 40 with a validity flag surfaced by `specmgr://config`; truncation applies to the resolved-node H1 labels only -- the `@startuml` diagram title is sanitized but never truncated, and unresolved ids stay verbatim; the renderer takes `max_label` as a plain parameter, keeping it pure.
- REQ-009: The CLI: `specmgr diagram refs <type> <id> [--depth N] [--reverse] [--no-feat] [--title T] [--out diagrams/refs] [--check]` writing `<id>.refs.puml`, and `specmgr diagram refs all [--no-feat] [--title T] [--out diagrams/refs] [--check]` writing `reference-graph.puml`, extending the existing `diagram` Typer group; the lazy mcp-extra import (missing extra ⇒ exit 1, the `diagram uc` precedent); exit codes 0 written/no-diff, 1 `--check` diff, 2 usage-or-resolution error (wrong-format id / missing source / depth out of range / `all` combined with a source); written artifacts carry no structure-only header (checker-clean by construction); `plantuml-check`/`plantuml-encode` work on the files unchanged.
- REQ-010: `specmgr://config` gains a static `diagram` section (`SPECMGR_DIAGRAM_MAX_TITLE`: `set` / `valid` / `default` 40 / `resolved` -- `resolved` is the effective int the helper returns (40 when unset or invalid), the `base_dir`/`cache_dir` resolved-value precedent; the raw env value is never disclosed, the resource's presence-only contract intact) in `models/config_info.py` + `general/resources/config.py` + the resource's own description updated to name `resolved` as a derived value (the `similarity`/`plantuml` section precedent).
- REQ-011: The host surface: a fifth workflow row in `.opencode/skills/specmgr-refs/SKILL.md` (diagram / visualize / PlantUML requests → `get_reference_diagram`/`get_reference_diagram_all` or `specmgr diagram refs`, then `specmgr plantuml-check`/`validate_plantuml` for the verdict; notes the env var, the red-cycle semantics, and the FEAT switch; carries the explicit 13-domain (diagram surface, adr included) vs 12-domain (the skill's text workflows, adr excluded by design -- adr slated for removal, ADR bfd76370) reconciliation note; frozen disambiguation: rendered/diagram/PlantUML/`.puml` phrasing routes to this row, the bare "show me the reference graph[, N levels deep]" phrasing stays with the existing multi-hop text-traversal row, and the skill's own `description` frontmatter gains the diagram phrasing) plus a new `/ref-graph` command (`.opencode/command/ref-graph.md`); the load-bearing wording drift-pinned by tests (the `test_skill_specmgr_refs.py` pattern + a new command test).
- REQ-012: `SPECMGR_DIAGRAM_MAX_TITLE` documented in every required place: `server.json` `environmentVariables` (name + description + default 40 -- `tests/test_server_json.py`'s drift test enforces manifest coverage of every `SPECMGR_*` read in `src/`, so the entry must land in the same commit as the first read site), the root `README.md` `### Environment Variables` bullet, the `specmgr://config` `diagram` section, the `specmgr://reference-graph` rulebook, the tool/CLI docstrings (flowing into `docs/MCP.md` via `specmgr mcp-docs` and `docs/api/` via `specmgr docs`), `AGENTS.md`, and the `CHANGELOG.md` `[Unreleased]` entry.
- REQ-013: One commit per phase; every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches).

### Acceptance Criteria

- [ ] ACC-001: (REQ-001/002/003/008) Byte-stable goldens under `tests/fixtures/reference-graphs/` -- pure renderer over hand-built `ReferenceGraph`s and builders over a synthetic seeded registry covering at least: a 2-node cycle (both edges red), a self-loop (red), a dangling reference (top-level `<<UNRESOLVED>>` node, id verbatim), feat dual spellings (two distinct nodes), a depth-2 chain (depth 1 vs 2 differ), a reverse hit (the additive union: the forward neighborhood plus the direct incoming edges, incl. a `depth=2` reverse call where only the forward part grows), the `include_feat=False` drop semantics (source exception), the registry-wide + `include_feat=False` combination with a non-feat→feat reference (the feat target must not appear as a node or edge), registry-wide, title override + both defaults, and truncation at the default 40 and a custom value (word-boundary cut, hard cut, exactly-N no-op) alongside an untruncated diagram title at a >40-char scoped H1; every golden passes `check_structure` in both modes with zero findings.
- [ ] ACC-002: (REQ-006) The amended checker accepts the full emitted subset with zero findings in both modes (env-gated real-parser verification green where a source is configured; the existing UC goldens byte-identical); the negative controls (a bracketed alias containing whitespace, an unbalanced stereotype) still error in both modes.
- [ ] ACC-003: (REQ-004/005) The error contract: `ValueError` for malformed `type`/`id`/`depth` before any filesystem access; the source domain's `XNotFoundError` for a missing source; the non-raising `ParseFailureResult` for an existing-but-broken source; `get_reference_diagram_all` never raises for content.
- [ ] ACC-004: (REQ-009) The CLI exit codes 0/1/2 pinned by test, the missing-mcp-extra path exits 1, and `--check` detects a diff including a missing output file.
- [ ] ACC-005: (REQ-011) The skill row and the `/ref-graph` command wording are drift-pinned by tests.
- [ ] ACC-006: (REQ-007/012/013) Docs consistency: the `server.json` entry present in the same commit as the first read site (drift test green), the README env bullet, the `specmgr://config` section, the `specmgr://reference-graph` resource serving the packaged rulebook (frozen palette, alias/label/truncation rules, the red syntax, the construction semantics), the `server.py` docstring, `docs/MCP.md` + `docs/api/` + `docs/GENERATED.md` regenerated, `AGENTS.md` + `CHANGELOG.md` updated; the full suite green at every phase end.

### Scope

#### Included

- The structure-checker amendment (`component` declaration + bracketed alias) and the dated UC rulebook §6.1 note.
- The reference-graph rulebook + `specmgr://reference-graph` resource.
- The pure library: `general/models/reference_graph.py` (model + renderer + SCC cycle marking) and `general/tools/_reference_graph.py` (builders) + `general/tools/_diagram_config.py` (env helper).
- The two MCP tools + registration (`general/tools/__init__.py`, `server.py` docstring) + the `specmgr://config` `diagram` section.
- The CLI `diagram refs` (+ `all`).
- The host surface: the `specmgr-refs` skill row + the `/ref-graph` command + the drift tests.
- The env-var documentation in every required place (REQ-012).
- Tests + goldens (ACC-001..005).

#### Explicitly Out Of Scope

- Per-type edge labels -- a uniform `: refers to` is frozen (the 11 tag types carry no consistently defined semantics).
- Transitive reverse (multi-hop incoming expansion) -- `reverse` is additive and direct-only on the incoming side: the graph is the forward expansion (to `depth`) plus the direct incoming edges to the requested source; `depth` governs the forward part only and is never a no-op.
- Semantic (embedding-based) edges -- `find_related`/`find_similar_text` are a separate, probabilistic mechanism; this feature is the deterministic tag vocabulary only.
- New reference tag types -- `tsk`/`sop` remain out of the 11-tag vocabulary (`_references.py`); a future addition flows through `REFERENCE_TYPES` automatically and needs no change to this feature's code paths.
- Template/example `.puml` packaged data files -- the rulebook carries the worked example (there is no agent-attribution step for a fully deterministic diagram, unlike the UC sequence flow).
- A dedicated subagent -- the flow is deterministic; the skill row + command suffice (the `uc-diagram` trio precedent, minus the prompt flow).
- Diagram size caps / pagination of the graph itself -- the registry-wide mode renders the whole parseable registry (readability is the consumer's concern; per-domain packages mitigate).
- Any change to the reference-extraction semantics -- the `_references.py` code-fence caveat and the feat dual-spelling behaviour are inherited verbatim.
- Any rendering target other than a PlantUML component diagram.

### Dependencies

#### Depends On

- FEAT feat-144-ref-artifact: the `_references.py` vocabulary + `ReferenceRow` + the `list_references` guard contract.
- FEAT feat-177-list-ref-feat: the `FEAT` tag + its dual id shape (full `feat-NNN-slug` or bare `feat-NNN`).
- FEAT feat-185-uc-diagrams: the `plantuml/` package, the structure checker, the validation chain, and the golden-pinning + rulebook + CLI + host-surface discipline.
- FEAT feat-126-server-json-env-drift: the `server.json` env-var manifest drift test that REQ-012 couples to. (Dependency is code-merged in this tree -- `tests/test_server_json.py` present; the feature doc's own `status` is still `review`, no gate impact.)
- FEAT feat-150-mcp-lifecycle-commands: the `ParseFailureResult` non-raising precedent (case 3 of the ADR 519d1206 chain). (Code-merged -- the precedent is in the tree; the feature doc's `status` is still `review`.)
- FEAT feat-152-ref-skill: the `specmgr-refs` skill this feature extends; it deferred exactly this capability.

#### Blocks

- None known. (GitHub issue #145's per-domain batched-resolution follow-up would speed the registry-wide/reverse paths but is not required.)

### Design Notes

**Emission layout (frozen; §2).** The renderer emits exactly this shape (one trailing newline; blank lines as shown; `…` = repetition):

```
@startuml {title}

skinparam component {
  backgroundColor<<ADR>> LightYellow
  backgroundColor<<REQ>> LightBlue
  backgroundColor<<UC>> Pink
  backgroundColor<<TSK>> Honeydew
  backgroundColor<<QA>> LemonChiffon
  backgroundColor<<PRB>> LightCoral
  backgroundColor<<GOL>> Lavender
  backgroundColor<<RSK>> Orange
  backgroundColor<<DEC>> LightGreen
  backgroundColor<<SOP>> PowderBlue
  backgroundColor<<FEAT>> PaleTurquoise
  backgroundColor<<VCR>> Khaki
  backgroundColor<<SYSRS>> Thistle
  backgroundColor<<UNRESOLVED>> DarkRed
}

left to right direction

component "{id}" as [REQ-{uuid}] <<UNRESOLVED>>
(… one top-level line per unresolved node, sorted by alias …)

package "REQ"
component "{label}" as [REQ-{uuid}] <<REQ>>
(… nodes sorted by id …)
end package
(… one package per non-empty domain, in ALL_DOMAINS order …)

[REQ-{uuid}] --> [DEC-{uuid}] : refers to
[REQ-{uuid}] -[#red]-> [UC-{uuid}] : refers to
(… edges deduped + sorted by (source_type, source_id, target_type, target_id);
    the red form only for on-cycle edges -- the exact syntax is frozen by the Phase 100 parser gate …)
@enduml
```

- Title: the sanitized (single-line, `#quot;`) `title` argument, else the source's H1 (scoped) / `Reference Graph` (all).
- Alias: bracketed. `[TYPE-{uuid}]` for the 12 UUID domains (every domain except `feat` -- `_domains.py`'s `UUID_DOMAINS`; uppercase type, verbatim lowercase uuid); the verbatim `feat-NNN-slug` id for feat (already type-prefixed and registry-unique). Uniqueness of the (type, id) key ⇒ collision-free.
- Label: a resolved node = its H1, sanitized and truncated per §5; an unresolved node = the verbatim id (uuid or feat id), never truncated.
- Palette (frozen 14): as in the block above -- the user-confirmed four (REQ LightBlue, DEC LightGreen, RSK Orange, UC Pink) plus UNRESOLVED DarkRed.
- The skinparam block is always emitted in full (all 14 entries, in the block's order) regardless of which types appear.
- Unresolved nodes are top-level (outside packages), sorted by alias, before the first package.
- A source document with zero edges renders as a single node (scoped) -- a valid, deterministic diagram.

**Graph construction semantics (frozen; §3).**
- Forward (scoped): BFS over outgoing references; level 0 = the source; a level-k node is expanded only if k < depth and it resolved to an existing document (its body read through the domain's read path -- the cache-aware leg for the 12 whole-body domains, the never-cached leg for adr); each unique (type, id) reference adds one edge + one node (the node title via `resolve_reference`; a dangling target = title None).
- `depth` validated 1..5 (default 1).
- Reverse: a paged full scan (all pages, the `_list_uc_all_rows` precedent) of all 13 source domains (ALL_DOMAINS -- adr included; the similarity search's adr exclusion, issue #46, does not apply to reference scanning, and the `specmgr-refs` skill's 12-domain text-workflow exclusion is a separate deliberate workflow-scope decision -- adr slated for removal, ADR bfd76370 -- reconciled by the Phase 140 skill note, not by narrowing this scan), reusing the `list_references` source-scan legs (the per-domain cache-aware reads; the never-cached adr leg); a scanned document becomes a node + an incoming edge iff it carries a reference matching the source on (type, id) -- with the feat dual-spelling rule: a full `feat-NNN-slug` source also matches a bare `feat-NNN` reference. Reverse is additive with the forward expansion (the graph is the union; `depth` governs the forward part only) and direct-only on the incoming side (no transitive expansion).
- Registry-wide: the same 13-domain scan; every successfully parsed document is a node; every extracted reference is an edge; a target not present as a scanned document gets its title via `resolve_reference` (dangling ⇒ unresolved node).
- Broken documents in any scan are skipped (never a node, never an edge source; the render never fails -- the `get_use_case_package_diagram` precedent); a broken *source* of a scoped call is a tool-level `ParseFailureResult` (the builder raises the domain's parse error, the tool converts).
- FEAT exclusion (`include_feat=False`): ONE rule in all three modes, applied last after the full graph is built -- drop every FEAT node except the explicitly requested source, then drop every edge touching a dropped node. Skipping the feat-domain scan is an allowed optimization only if it ALSO suppresses feat-targeted references (a feat target must not surface as a node in any mode -- the post-hoc drop is the definition, the scan-omission is not).
- Cycle-safety: every build runs over a visited (type, id) set -- reference cycles terminate by construction; they affect only rendering (§4).
- Inherited caveats (documented, not fixed): the extractor scans fenced code blocks (a quoted reference becomes an edge, usually a dangling one -- the accepted v1 tradeoff pinned by feat-144), and feat dual spellings are two distinct nodes (parity with the pinned `list_references` rows).

**Cycle detection + red arrows (frozen; §4).** An edge lies on a cycle iff it is a self-loop (src == dst) or both endpoints belong to the same strongly connected component of size ≥ 2 -- exact characterization: within an SCC every pair of nodes is mutually reachable, so any internal edge (u→v) plus a v→…→u path forms a cycle containing it; conversely, every node on a cycle is mutually reachable with the rest, so a cycle's nodes form (a subset of) one SCC. Computed by an iterative Tarjan (stdlib, deterministic node order) inside the renderer -- the model stays pure facts. On-cycle edges render with the red arrow; the exact syntax (`-[#red]->` is the candidate) is frozen by the Phase 100 real-parser gate before the rulebook ships (the gate is env-gated with a clean skip where no source is configured: on a skip the rulebook's dated note + a Progress entry record the verdict "skipped -- candidate `-[#red]->` retained, re-verify where a source is configured", and Phase 100 commits with the candidate). A `-[#red]->`-shaped line and a `skinparam` line are outside the checker's frozen line grammar and are silently accepted (verified by trace) -- ACC-002 pins the zero-finding property.

**Env var (frozen; §5).** `SPECMGR_DIAGRAM_MAX_TITLE` -- int, default 40, read by `general/tools/_diagram_config.py` (`ENV_VAR_DIAGRAM_MAX_TITLE` constant + `diagram_max_title() -> tuple[int, bool]` returning the effective value + a validity flag; the env read follows the `plantuml/chain.py` `ENV_VAR_*` + `os.environ.get` idiom -- the int parse with fallback + validity flag is new); a set-but-invalid value (empty, non-int, or < 1) ⇒ `(40, False)`. Truncation (renderer, applied to the resolved-node H1 labels only -- the `@startuml` diagram title is sanitized but never truncated): if `len(label) > N`: `candidate = label[:N-1]`, cut at the last space within `candidate` if any (else hard cut), append `…`; the result is ≤ N characters. Exactly-N labels are untouched. The `specmgr://config` `diagram` section reports set/valid/default/resolved -- `resolved` is the effective value from `diagram_max_title()` (the `base_dir`/`cache_dir` resolved-value precedent; the raw env value is never disclosed, the resource's presence-only contract intact).

**Checker amendment scope (frozen; §6).** Three code changes in `plantuml/structure.py` (plus its module docstring's frozen-grammar enumeration) + one rulebook note, one commit: (a) `_DECLARATION_PATTERN` (line 220) keyword set gains `component`; (b) the alias grammar -- `_AS_ALIAS_PATTERN` (229), `_QUOTED_DECLARATION_SHAPE` (253), `_BARE_DECLARATION_SHAPE` (252) -- also accepts a bracketed token `[<no whitespace, no brackets>]`, the declared name recorded unbracketed; (c) `_strip_operand` (232) also unwraps a fully-bracketed token, so declaration and edge operands compare identically. `uc/data/uc_plantuml.md` §6.1 gains the dated amendment note (citing this feature). The existing UC subset + goldens must stay byte-identical (regression-pinned). No amendment is needed for the skinparam lines or the red-arrow lines (both fall into the checker's silent-accept path -- verified by trace, pinned by ACC-002's zero-finding assertion), nor for the named `end package` close (the checker accepts a kind-matching named close silently; a bare `end` on a `package` fragment is a hard error in both modes -- `_BARE_END_CLOSEABLE` holds alt/opt/loop/group only), which is why the frozen §2 layout closes packages with the named form.

**Error contract (frozen; §7).** Scoped tool: `validate_id` + `depth` check (both pure input validation -- a `ValueError` before any fs access, so a malformed `type`/`id`/`depth` never reaches the filesystem; for `type="feat"` a bare `feat-NNN` is a wrong-format `id` under `validate_id`, not a normalization candidate) → source load (missing ⇒ the domain's `XNotFoundError`; broken ⇒ `ParseFailureResult`) → build (never raises for target-side content) → render (pure). `get_reference_diagram_all`: no id guards, never raises for content. CLI: the same guards mapped to exit 2; missing mcp extra ⇒ exit 1; a `--check` diff / missing output file ⇒ exit 1; a clean write / no diff ⇒ exit 0.

**Test strategy (§8).** Fixtures under `tests/fixtures/reference-graphs/` (the synthetic registry of ACC-001's scenario matrix) + golden `.puml` files; isolated `SPECMGR_*_DIR` tmp dirs (the `tests/commands/test_diagram.py` precedent); env-gated real-parser tests (the `tests/conftest.py` `plantuml_source()` machinery -- a clean skip, reported via `pytest -rs`, where no source is configured); host-wording drift tests (the `tests/opencode/` pattern).

**Phase execution rule (standing user requirement, the identical text carried by feat-150/feat-167/feat-204 as instances; §9).** Every phase ends with the full quality gate (ruff format/check, vulture, the full pytest suite, and every doc-drift check the phase touches: `specmgr docs`, `specmgr mcp-docs`, the `server.json` drift test) and exactly one Conventional Commit. The `server.json` entry must travel with the first read site (Phase 110) or the Phase 110 gate fails the drift test.

**Tool and data-file contracts (frozen; §10).** Signatures: `render_reference_graph(graph, *, max_label=40) -> str`; `build_source_graph(source_type, source_id, *, depth=1, reverse=False, include_feat=True) -> ReferenceGraph`; `build_registry_graph(*, include_feat=True) -> ReferenceGraph`; `get_reference_diagram(type, id, depth=1, reverse=False, include_feat=True, title=None) -> str | ParseFailureResult`; `get_reference_diagram_all(include_feat=True, title=None) -> str`. Data file: `general/data/general_reference_graph.md` via the existing `read_packaged_text` convention (the `biz.dfch.specmgr.general` `data/*.md` wildcard covers it -- no pyproject change). Resources: `specmgr://reference-graph` (raw markdown, `text/markdown`). Model: the `ConfigInfo.diagram` section in `models/config_info.py` + the read in `general/resources/config.py`. CLI filenames: `<id>.refs.puml` / `reference-graph.puml` under `--out` (default `diagrams/refs/`).

### Related Decisions

- ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4: the import-free, stdlib-only `plantuml/` cross-cutting package this feature reuses (validation chain, structure checker, encoder).
- ADR 519d1206-4d2a-4500-9046-6db635209996 (and its extensions: ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c, and ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f): the non-raising structured-result chain -- this feature's broken-source branch is case 3's precedent (`ParseFailureResult`).
- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: local pre-commit enforcement -- the per-phase full quality gate this plan runs.
- ADR bfd76370-b59b-4d65-b550-a969f6c93c9d: the DocCache adr exclusion (adr permanently outside the per-domain read cache) -- the reason the 13-domain source scan carries its own never-cached adr leg, and the rationale half of the 13-domain (tool) vs 12-domain (skill text workflows) reconciliation; adr is slated for removal, so the scan's adr inclusion is a completeness choice, not a bet on adr's longevity.
- FEAT feat-144-ref-artifact: the reference vocabulary + `ReferenceRow` + the `list_references` guard contract; its Explicitly Out Of Scope defers this feature's reverse/graph capability.
- FEAT feat-152-ref-skill: the `specmgr-refs` skill this feature extends; its Explicitly Out Of Scope defers "new MCP capabilities (e.g. `reverse`/`depth` parameters)" as its own issue -- this feature is that issue.
- FEAT feat-185-uc-diagrams: the four-layer precedent (rulebook + renderers + tools + CLI + host surface), the golden discipline, the dated rulebook-amendment pattern (its Phase 125/145/150/160), and the `diagram uc` CLI exit-code contract.
- FEAT feat-126-server-json-env-drift: the `server.json` env-var manifest drift test that REQ-012/ACC-006 couple to.
- FEAT feat-150-mcp-lifecycle-commands: the `ParseFailureResult` + the exists-but-broken recovery precedent.

### Task List

#### Phase 100: Spec freeze + structure-checker amendment

- [ ] Task 100.100: Author the reference-graph rulebook `general/data/general_reference_graph.md` (the frozen emission layout + palette + alias/label/truncation + title override/defaults + FEAT-exclusion + the bare-`feat-NNN` source-id rejection with the `list_feat` discovery pointer + cycle rule + construction semantics + file layout of Design Notes §2-§5) with a pointer to the UC rulebook §3-§6 for the reused validation chain.
- [ ] Task 100.110: Register the `specmgr://reference-graph` resource (`general/resources/reference_graph.py`, raw markdown passthrough) + the `general/resources/__init__.py` import.
- [ ] Task 100.120: Real-parser gate (env-gated): verify the candidate emission subset -- `component "..." as [alias] <<ST>>` declarations, the 14-entry skinparam colour block, `-->` / red-arrow edges with the `: refers to` label, self-loops, `package ... end package` groups, top-level unresolved nodes -- and freeze the exact red-arrow syntax in the rulebook; record the verdict (on a clean skip: "skipped -- candidate `-[#red]->` retained, re-verify where a source is configured", noted in the rulebook's dated entry + a Progress entry).
- [ ] Task 100.130: Implement the checker amendment in `plantuml/structure.py`: `component` in `_DECLARATION_PATTERN`; the bracketed-alias grammar (frozen shapes + legacy walk, declared unbracketed); the `_strip_operand` bracket unwrap; the module docstring's frozen-grammar enumeration updated.
- [ ] Task 100.140: The dated amendment note in `uc/data/uc_plantuml.md` §6.1 (citing this feature).
- [ ] Task 100.150: Amendment tests: a component declaration registers its label + alias; a zero-finding assertion over the emitted subset in both modes; the negative controls (a bracketed alias containing whitespace, an unbalanced stereotype) still error; the existing UC goldens byte-identical.
- [ ] Task 100.160: Phase-end gate (including the doc-drift checks the phase touches), then exactly one Conventional Commit for the phase.

#### Phase 110: Library (model + renderer + builder + env helper)

- [ ] Task 110.100: `general/models/reference_graph.py` -- the frozen `GraphNode`/`GraphEdge`/`ReferenceGraph` dataclasses + the pure `render_reference_graph(graph, *, max_label=40) -> str` (frozen layout, alias rule, truncation, the SCC cycle marking + red edges, ordering, the single trailing newline).
- [ ] Task 110.110: `general/tools/_reference_graph.py` -- `build_source_graph` (the BFS depth, the direct reverse, the visited-set cycle safety) + `build_registry_graph` (the 13-domain scan, the skip-broken), reusing `find_references`/`resolve_reference` + the `list_references` source-scan legs (the per-domain cache-aware reads; the never-cached adr leg); the FEAT-exclusion drop rule applied last.
- [ ] Task 110.120: `general/tools/_diagram_config.py` -- the `ENV_VAR_DIAGRAM_MAX_TITLE` constant + `diagram_max_title() -> tuple[int, bool]` (default 40; set-but-invalid ⇒ `(40, False)`).
- [ ] Task 110.130: The `server.json` `environmentVariables` entry for `SPECMGR_DIAGRAM_MAX_TITLE` (name + description + default 40) -- same commit as the first read site (the drift-test coupling, REQ-012).
- [ ] Task 110.140: The synthetic-registry fixtures under `tests/fixtures/reference-graphs/` (the ACC-001 scenario matrix) + the golden `.puml` files.
- [ ] Task 110.150: Tests: the renderer unit goldens (pure, hand-built graphs incl. the truncation edge cases + the SCC characterization cases: a 2-cycle, a self-loop, a larger SCC, an off-cycle edge between SCC neighbours) + the builder integration tests (depth 1 vs 2, the reverse hit + the dual-spelling match, the `include_feat` drop semantics + the source exception, the registry-wide + `include_feat=False` feat-target suppression, the registry-wide, the skip-broken).
- [ ] Task 110.160: Phase-end gate (including the `server.json` drift test), then exactly one Conventional Commit for the phase.

#### Phase 120: MCP surface

- [ ] Task 120.100: `general/tools/get_reference_diagram.py` -- the tool (the guard order per Design Notes §7; the `ParseFailureResult` branch; the depth validation).
- [ ] Task 120.110: `general/tools/get_reference_diagram_all.py` -- the tool (never raises for content).
- [ ] Task 120.120: Registration: the `general/tools/__init__.py` imports + `__all__` + module docstring entry; the `server.py` module docstring (the authoritative registration list).
- [ ] Task 120.130: The `specmgr://config` `diagram` section: the `ConfigInfo.diagram` model (`models/config_info.py`) + the `general/resources/config.py` read (set/valid/default/resolved) + the resource description naming `resolved` as a derived value (the presence-only contract intact).
- [ ] Task 120.140: The root `README.md` `### Environment Variables` bullet for `SPECMGR_DIAGRAM_MAX_TITLE` (the section's own format).
- [ ] Task 120.150: Tests: tool registration + the error contract (ACC-003) + the config section + the byte-stable return over the fixtures; regenerate `docs/MCP.md` (`specmgr mcp-docs`) + `docs/api/` + `docs/GENERATED.md` (`specmgr docs`).
- [ ] Task 120.160: Phase-end gate (including the doc-drift checks), then exactly one Conventional Commit for the phase.

#### Phase 130: CLI

- [ ] Task 130.100: Extend `commands/diagram.py` with the `refs` member: `specmgr diagram refs <type> <id> [--depth N] [--reverse] [--no-feat] [--title T] [--out diagrams/refs] [--check]` writing `<id>.refs.puml` (the lazy mcp-extra import + the exit codes per REQ-009).
- [ ] Task 130.110: The `specmgr diagram refs all [...]` writing `reference-graph.puml` mode (the usage error for `all` combined with a source).
- [ ] Task 130.120: Tests: the exit codes 0/1/2 (ACC-004), the `--check` diff (incl. a missing file), the missing-mcp-extra path (exit 1), the isolated `SPECMGR_*_DIR` fixture runs.
- [ ] Task 130.130: The CLI help/docstring mentions (the env var, the defaults) + the `docs/api/` regeneration.
- [ ] Task 130.140: Phase-end gate, then exactly one Conventional Commit for the phase.

#### Phase 140: Host surface + closeout

- [ ] Task 140.100: The fifth workflow row in `.opencode/skills/specmgr-refs/SKILL.md` (the diagram/visualize/PlantUML routing: the tool vs the CLI, the `plantuml-check` verdict, the env-var + red-cycle + FEAT-switch notes, the 13-domain (diagram surface, adr included) vs 12-domain (text workflows, adr excluded by design) reconciliation note, the frozen disambiguation -- rendered/diagram/PlantUML/`.puml` phrasing → this row, bare "show me the reference graph[, N levels deep]" → the existing multi-hop row) + the skill `description` trigger update (the diagram phrasing).
- [ ] Task 140.110: The `.opencode/command/ref-graph.md` command (`/ref-graph <type> <id> [depth] [--reverse] [--no-feat] | all`; runs the deterministic CLI; reports the written path + the check verdict; never edits, writes, or commits).
- [ ] Task 140.120: The drift tests (extending `tests/opencode/test_skill_specmgr_refs.py` + a new `tests/opencode/test_command_ref_graph.py`); ACC-005.
- [ ] Task 140.130: The root `README.md` `## Reference Graph Diagrams` how-to section (+ the TOC entry; the placement immediately after feat-185's `## UC → PlantUML Diagrams` section, so the TOC order is `## CLI Usage` → `## UC → PlantUML Diagrams` → `## Reference Graph Diagrams` → `## MCP Server`).
- [ ] Task 140.140: The `AGENTS.md` updates (the `general/` bullet: the two tools + the `diagram refs` CLI + the rulebook resource + the env var; the `plantuml/` bullet: the checker's declaration grammar now includes `component` + the bracketed alias).
- [ ] Task 140.150: The `CHANGELOG.md` `[Unreleased]` entry.
- [ ] Task 140.160: Walk every ACC-001..006 with concrete evidence; run the full quality gate end-to-end one last time; update the Progress section; set the feature status to `done`.

## Progress

### Current Status

**As of 2026-10-09**: Feature created from GitHub issue #207 via the planning conversation; no implementation started. Phase 100 (spec freeze + structure-checker amendment) is the next actionable step, starting with Task 100.100.

### Blockers

- None

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-10T08:00:13.081+02:00 - Plan refined: second refiner pass applied (4 design decisions + 8 mechanical fixes)

Second `refine-feature` pass findings applied after user decisions (recorded in `### Decisions Made`): G1 -- `reverse` frozen as ADDITIVE and direct-only on the incoming side (the graph is the forward expansion to `depth` plus the direct incoming edges to the source; `depth` governs the forward part only and is never a no-op; out-of-scope line, REQ-004, §3, and the ACC-001 reverse golden updated). G2 -- a bare `feat-NNN` as the *source* id is REJECTED (the `validate_id` strictness, the `get_feat`/`list_references` parity); documented in REQ-004, the rulebook freeze list (REQ-007, Task 100.100), and §7, with the `list_feat` discovery pointer. D1 -- the §7 guard order corrected: `validate_id` + the `depth` check are both pure pre-filesystem input validation (ACC-003 now literally true). D2 -- the 13-domain (adr-inclusive) tool scan kept; REQ-011 + Task 140.100 now carry the explicit reconciliation note against the `specmgr-refs` skill's deliberate 12-domain text workflows (adr slated for removal), and a Related Decisions bullet names ADR bfd76370. Mechanical fixes: G3 (the `list_references` source-scan legs named, incl. the never-cached adr leg -- `adr` permanently DocCache-excluded), D4 (the three extension ADRs on the Related Decisions line now each carry their own `ADR <uuid>` tag, so the extractor sees all six), I1 (the `WholeBodyOrAdrType` alias in REQ-004's signature instead of a re-unpacked `Literal[ALL_DOMAINS]`), I2 (truncation disambiguated: the `@startuml` diagram title is sanitized but never truncated, pinned by a >40-char-H1 golden in ACC-001), I3 (the `plantuml/structure.py` module docstring's grammar enumeration named in REQ-006 + Task 100.130), I4 (the two `status: review` dependencies recorded as code-merged), I5 (the root-README section slot pinned: after `## UC → PlantUML Diagrams`, before `## MCP Server`), I6 (the H1's `(#207)` suffix dropped -- the issue number is already the id's NNN infix). The D3 false-positive is closed in feat-177's own README (its ACC-001's literal fixture mention reworded so the tag and the id are no longer adjacent; `list_references` on feat-177 now returns zero error rows).

#### 2026-10-09T13:29:37.895+02:00 - Plan refined per feat-refiner pass

Refinement of the plan (no implementation touched): the frozen §2 layout's package close corrected to the named `end package` (a bare `end` on a `package` fragment is a hard checker error in both modes); the alias rule corrected to the 12 UUID domains (`_domains.py`'s `UUID_DOMAINS`, not 10); the dead `_confluence_config.py` citation re-pointed at the live `plantuml/chain.py` `ENV_VAR_*` + `os.environ.get` idiom; the `specmgr://config` `diagram` section reshaped to set/valid/default/`resolved` (the raw env value stays undisclosed per the resource's presence-only contract); REQ-007 gained ACC coverage via ACC-006 (the `specmgr://reference-graph` resource + the packaged rulebook); the Phase 100 real-parser gate's clean-skip fallback stated (record the verdict, commit with the candidate); the skill-row disambiguation frozen (rendered/diagram phrasing → the new row, bare "show me the reference graph" stays with the multi-hop row); FEAT exclusion unified to ONE post-hoc rule in all three modes + a new ACC-001 golden for the registry-wide feat-target suppression; "All tool" spelled out as `get_reference_diagram_all`. The three refinement decisions are recorded in `### Decisions Made`.

#### 2026-10-09T08:10:40.369+02:00 - Created from planning conversation

Feature drafted from GitHub issue #207 -- the deterministic reference-graph visualization deferred by feat-144-ref-artifact ("Reverse references") and feat-152-ref-skill ("New MCP capabilities (e.g. `reverse`/`depth` parameters)"), rendered on the feat-185-uc-diagrams PlantUML stack. Plan locked in this session: 13 requirements, 6 acceptance criteria, 5 phases (100 spec freeze + checker amendment, 110 library, 120 MCP surface, 130 CLI, 140 host surface + closeout). Key locked decisions: recorded in the `### Decisions Made` section (the plan-locked entry of this timestamp).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-10T08:00:13.081+02:00 - Second refinement decisions (user-confirmed)

Four decisions locked for the second refiner pass: (1) `reverse` is ADDITIVE and direct-only on the incoming side -- the graph is the forward expansion (to `depth`) plus the direct incoming edges to the requested source; `depth` governs the forward part only and is never a no-op (alternatives considered: exclusive reverse; rejecting the `reverse` + explicit-`depth` combination, which would have required a `depth: int | None` signature against the frozen §10 `depth=1`). (2) A bare `feat-NNN` as a *source* id is REJECTED -- `validate_id` keeps its strictness (full `feat-NNN-slug` only, `ValueError` before any fs access, the `get_feat`/`list_references` parity); the bare-spelling diagram nodes are extracted reference rows (inherited verbatim), not an addressing invitation; the rulebook + tool docstring point at `list_feat` (alternative considered: normalizing the source id like the FEAT reference-resolution rule -- rejected as a source-side path no other id-addressing surface has). (3) The §7 guard order is `validate_id` + `depth` check FIRST (both pure `ValueError`, before any filesystem access), then source load -- making ACC-003 literally true (alternative considered: keeping the old order and softening ACC-003 to 'when the source is present'). (4) The tool's 13-domain scan KEEPS adr -- an ADR doc referencing a REQ is a real edge, and narrowing would make ADR nodes receive-only, never emit; the Phase 140 skill update reconciles explicitly (diagram surface includes adr source documents; the skill's text workflows stay 12-domain, adr slated for removal, ADR bfd76370; the two surfaces intentionally differ) (alternatives considered: narrowing the tool to 12 domains; extending the skill to 13 against its own deliberate-exclusion wording).

#### 2026-10-09T13:29:37.895+02:00 - Plan refinement decisions (feat-refiner pass)

Three decisions locked in this refinement: (1) the `specmgr://config` `diagram` section reports set/valid/default/`resolved` -- `resolved` is the effective int from `diagram_max_title()` (40 when unset or invalid), following the `base_dir`/`cache_dir` resolved-value precedent, so the resource's presence-only contract (never the raw env value) stays intact; (2) FEAT exclusion is ONE post-hoc rule in all three modes -- drop every FEAT node except the explicitly requested source, then drop every edge touching a dropped node -- with the registry/reverse scan-omission of the feat domain an allowed optimization only if it also suppresses feat-targeted references; (3) the Phase 100 real-parser gate's clean skip (no source configured) records the verdict "skipped -- candidate retained, re-verify where a source is configured" in the rulebook's dated note + a Progress entry, and Phase 100 commits with the candidate.

#### 2026-10-09T08:10:40.369+02:00 - Plan locked from planning conversation

The uniform `: refers to` edge with the incoming arrow on the referenced item; the per-type colour palette via a frozen 14-entry skinparam block (user-confirmed REQ LightBlue / DEC LightGreen / RSK Orange / UC Pink / UNRESOLVED DarkRed); the SCC-based red cycle edges (the exact red-arrow syntax parser-gated in Phase 100); the top-level `<<UNRESOLVED>>` dangling node (label = the verbatim missing id); the `include_feat` switch / `--no-feat` flag (drop every FEAT node except the explicitly requested source, then drop every edge touching a dropped node); the title override with the source-H1 / `Reference Graph` defaults; `component "..." as [bracketed-alias]` declarations (the structure-checker amendment covers the `component` keyword + the bracketed-alias grammar + the `_strip_operand` bracket unwrap); and the `SPECMGR_DIAGRAM_MAX_TITLE` env var (int, default 40, word-boundary truncation + `…`, documented in every required place including the drift-test-coupled `server.json` entry that must land with the first read site).

### More Information

References from GitHub issue #207:

- FEAT feat-144-ref-artifact (the deterministic reference vocabulary this feature renders).
- FEAT feat-152-ref-skill (the skill extended in Phase 140; it deferred this feature as "its own issue").
- FEAT feat-185-uc-diagrams (the four-layer + PlantUML stack precedent reused almost as-is).
- https://github.com/dfch/biz.dfch.SpecMgr/issues/207
