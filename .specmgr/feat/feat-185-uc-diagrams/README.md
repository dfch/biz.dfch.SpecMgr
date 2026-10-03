---
classification: null
created: '2026-10-03T09:46:57.279+02:00'
id: feat-185-uc-diagrams
status: planning
type: feat
updated: '2026-10-03T09:46:57.279+02:00'
version: 1.0.0
---

# Feature: Formalised UC → PlantUML Diagram Pipeline

## Plan

### Overview

Specmgr UC artifacts (Cockburn-style use cases, `uc/models/v2`) currently become PlantUML use-case and sequence diagrams only through ad-hoc agent instructions per project — no stable mapping, no template, no validation. This feature formalises that pipeline as a versioned part of the package, in three layers plus host artifacts:

1. **Library (pure, tested):** deterministic renderers for use-case diagrams (per-UC + multi-UC package), a sequence-diagram *skeleton* (everything deterministic — participants, trigger, notes, `alt` fragment structure; only sender attribution is left to the agent), and the import-free, stdlib-only `plantuml/` package (PlantUML `~1` URL encoder, two-mode structure checker, validation backends and strict chain).
2. **MCP (ships per project with the package):** tools for the renderers, the validation chain, the packaged PlantUML template/example, and the encode utility; the rulebook resource `specmgr://uc/plantuml`; the `generate_uc_sequence_diagram` prompt (the agent attributes step senders by understanding the free-form text and MUST ask the user via the `question` tool when not confident).
3. **CLI (supporting, thin):** `specmgr diagram uc`, `specmgr plantuml-check`, `specmgr plantuml-encode` — reuse library functions, no new logic.
4. **OpenCode host:** a thin self-triggering `uc-diagram` skill (+ optional `/uc-diagram` command) following the `repair` trio pattern; the skill stays thin and points at the prompt + rulebook.

The sequence diagram is deliberately *not* a pure function of the document: "who sends message N" requires understanding. Everything else is.

### Requirements

- REQ-001: A per-UC use-case diagram (one `usecase` node labelled by title + level stereotype, one `actor` node per distinct cleaned actor label, plain associations) renders deterministically from a parsed v2 `UseCase`.
- REQ-002: A package-level use-case diagram (one node per document, deduplicated actor union, `<<include>>`/`<<extend>>` edges from `Related Use Cases` with resolved `UC <uuid>` references, deterministic `note` for unresolvable references) renders deterministically from N parsed v2 `UseCase` documents.
- REQ-003: A sequence-diagram skeleton renders deterministically: participants = cleaned actors + system from `Scope`, `Trigger` as first message, `Preconditions`/end-condition notes, each `Extension {N}{a}.` as an `alt` fragment anchored at its structurally validated step reference, each `SubVariation Step {N}:` as a note; main-scenario steps pre-filled as messages when the step's first word matches a participant label, otherwise emitted as `' UNATTRIBUTED step N: <text>` markers.
- REQ-004: The canonical agent workflow (MCP prompt + OpenCode skill) attributes each UNATTRIBUTED step by understanding the free-form text, MUST ask the user via the `question` tool whenever not confident, and writes the `.puml` file only after `validate_plantuml` returns green at the highest configured layer with zero UNATTRIBUTED markers remaining.
- REQ-005: Validation source selection is strict and configuration-driven: the first of `SPECMGR_PLANTUML_JAR`, `SPECMGR_PLANTUML_BIN`, `SPECMGR_PLANTUML_URL` that is **set** is the *only* source used. No fall-through to any other source on misconfiguration (a misconfigured JAR with a set public URL must never contact the public server), no PATH auto-discovery, no public default. A set-but-unavailable source is a hard validation failure: no file write, report with exact reason + fix hint. Only the all-unset state degrades to the structure-only floor (file written with a `' validated: structure-only` header).
- REQ-006: The URL backend uses a single endpoint, `GET {base}/svg/~1{enc}`, classified by the frozen matrix (Design Notes §5): 200 + real-diagram-SVG = VALID and RENDERED; 400 + "Welcome to PlantUML!" placeholder = SYNTAX INVALID; 200 + placeholder = REQUEST ERROR (size limit / undecodable / no diagram); 200 + "bad URL" explanatory = ENCODE ERROR; any unknown combination = INCONCLUSIVE → one retry → persistent = source state. An unrecognised response is never classified as INVALID.
- REQ-007: The structure checker (pure Python, stdlib-only, in `plantuml/`) returns actionable errors (1-based line + cause + fix hint, the feat-27 convention) in two modes: *preflight* (parser-verified lenient cases are non-blocking warnings) and *standalone* (they are promoted to errors). The checker must never reject what the real parser accepts (the verified lenient set).
- REQ-008: A packaged PlantUML template + example ship like every other artifact type (`uc/data/`, tool + resource pair): the template is a skeleton with placeholder participants and mapping comments; the example is the complete usecase + sequence PlantUML for the packaged "Buy Goods" example UC. Both must pass the structure checker in both modes.
- REQ-009: Supporting CLI: `specmgr diagram uc [ids|all] --out <dir>` (writes deterministic diagrams; `--check` regenerates and diffs for CI), `specmgr plantuml-check <path...>` (validates arbitrary `.puml` through the chain), `specmgr plantuml-encode <path|->` (prints a renderable `~1` URL; works fully offline, no Java).
- REQ-010: Real-parser tests run only when a validation source resolves (env-gated, skip with reason); on GitHub CI (no source configured) they skip cleanly while the rest of the suite (renderer goldens, checker tests, offline URL-dialect tests on recorded byte fixtures) runs.
- REQ-011: The rulebook resource `specmgr://uc/plantuml` freezes the mapping spec, the validation chain semantics, the URL protocol matrix, the env-var table, the platform-adapter reference snippets, and production deployment guidance.
- REQ-012: Every phase is delivered as a single commit (code + tests + docs + Progress update) gated by the full pre-commit hook suite (ruff format/check, vulture, `specmgr docs`/`adr-toc`/drift checks, full `pytest -n auto`, coverage-badge). No intermediate commits.

### Acceptance Criteria

- [ ] ACC-001: The three renderers produce byte-stable golden output for the packaged example UC (plus a multi-UC package fixture), and every renderer output passes the structure checker (both modes where applicable).
- [ ] ACC-002: The prompt flow run against the example UC produces a complete sequence diagram (zero `UNATTRIBUTED` markers) that validates green at the configured source; at least one deliberately ambiguous step triggers the `question` tool in the walkthrough record.
- [ ] ACC-003: With `SPECMGR_PLANTUML_JAR` set to a non-existent path and `SPECMGR_PLANTUML_URL` set to the public plantuml.com, `validate_plantuml` fails with a diagnostic naming the JAR and the test proves zero HTTP requests were made (mocked transport).
- [ ] ACC-004: With a resolvable local source (dev machine: jetty URL or jar), a valid diagram returns `valid=true`, `rendered=true`, `checked_by` = that source; the canonical `aass` error fixture returns `valid=false`.
- [ ] ACC-005: All verified lenient cases (unclosed `alt` at EOF, missing `@enduml`, bare `@end`, dangling arrow) are accepted by the checker in preflight mode (warnings at most) and rejected in standalone mode.
- [ ] ACC-006: `specmgr plantuml-encode` on the example file prints a URL that round-trips (decode test) and, env-gated, renders on the configured server.
- [ ] ACC-007: On a checkout with no `SPECMGR_PLANTUML_*` set, the full suite passes with the real-parser tests skipped (reason reported via `-rs`); on the dev machine with a source configured, the same suite runs them.
- [ ] ACC-008: In each phase commit: `server.py` docstring, `docs/MCP.md` (regenerated), and `AGENTS.md` are consistent with the registered surface; `specmgr docs` and `specmgr mcp-docs` drift checks pass.

### Scope

#### Included

- `uc` domain only: renderers, sequence skeleton, prompt, skill/command, PlantUML template/example data, rulebook resource
- Cross-cutting `src/biz/dfch/specmgr/plantuml/` package: `~1` encoder, two-mode structure checker, jar/bin/url backends, strict chain resolver, result model — import-free, stdlib-only, deliberately extractable
- MCP tools/resources/prompt as listed in the Requirements
- Supporting CLI commands (`diagram uc`, `plantuml-check`, `plantuml-encode`)
- Env-gated real-parser test machinery (`tests/conftest.py` dotenv load, source-availability gate, recorded URL-dialect fixtures)
- `.specmgr/conventions.md` authoring section (attribution style, diagram file layout)
- Docs: `server.py` docstring, `docs/MCP.md`, `AGENTS.md`

#### Explicitly Out Of Scope

- Any UC schema change (`### Level` stays free text; no per-step actor fields)
- Activity diagrams, state diagrams, or other diagram types (the v1-era analysis is reference only)
- Multi-UC combined sequence diagrams (one sequence diagram per UC document)
- Diagrams for any domain other than `uc` (the `plantuml/` package is designed to be reused by future domains; that is follow-up work)
- Dependency on `plantuml-mcp` (MVP, only `plantuml_version` today; watch item noted in the skill)
- Docker/k8s backends inside specmgr (platform adapters are the user's own executables behind `SPECMGR_PLANTUML_BIN` — reference snippets only)
- Inline SVG/PNG payloads in tool results (local render proof uses temp files; the URL backend's SVG is classified, not returned)
- Network access when no source is configured (the default state is fully offline)

### Dependencies

#### Depends On

- None new: the `uc/models/v2` schema, the `general.tools._packaged_data` helper, and the pre-commit suite are in place; the dev machine's docker plantuml stack (jetty server + CLI container) is optional, used only for local real-parser tests

#### Blocks

- Future diagram features for other domains (they will reuse the `plantuml/` package and the chain semantics)

### Design Notes

**§1 Layering and artifact map**

| Layer | Artifacts |
|---|---|
| Library | `uc/models/v2/renderer.py` (3 pure renderers); `plantuml/` package: `encode.py`, `structure.py`, `backends.py` (jar+bin), `url.py`, `chain.py` (+ result model) |
| MCP tools | `get_uc_diagram`, `get_use_case_package_diagram`, `get_uc_sequence_skeleton`, `validate_plantuml`, `get_uc_plantuml_template`, `get_uc_plantuml_example`, `plantuml_encode` |
| MCP resources | `specmgr://uc/plantuml` (rulebook), `specmgr://uc/plantuml-template`, `specmgr://uc/plantuml-example`; `specmgr://config` gains a `plantuml` section |
| MCP prompt | `uc/prompts/generate_uc_sequence_diagram` |
| CLI | `specmgr diagram uc`, `specmgr plantuml-check`, `specmgr plantuml-encode` |
| Host | `.opencode/skill/uc-diagram/SKILL.md` (+ optional `.opencode/command/uc-diagram.md`) |
| Data | `uc/data/plantuml_template.md`, `uc/data/plantuml_example.md` |

**§2 Mapping spec (frozen in the rulebook, Phase 100)**

- Participants/actors: port the v1 `_actor_label` cleaning (first double-quoted substring > drop trailing parenthetical > as-is); system participant from `Scope` (first sentence, same cleaning).
- Level: normalise case-insensitively against `summary` / `user goal` / `subfunction` → `<<stereotype>>` on usecase nodes; unrecognisable → no stereotype, never a failure (no schema change).
- Attribution (sequence): first-word match against participant labels = deterministic pre-fill; otherwise the agent decides by understanding; low confidence → `question` tool; UNATTRIBUTED markers are the hand-off between the deterministic skeleton and the agent.
- Fragments: `Extension {N}{a}.` → `alt` anchored at step N (the v2 schema already validates the reference structurally, `uc/models/v2/use_case.py:372`); the extension's condition text labels the first branch; "Return to step N" / "Continue to step N" → close the fragment + resumption note.
- Sub-variations: `Step {N}:` → `note` on that step.
- Preconditions → note at top; Success/Failed End Conditions → final notes; Trigger → first message into the system.
- Package edges: `Related Use Cases` bullets carry the relationship in free text (authoring practice: `Subordinate: X (…)`, `Superordinate: Y (…)`); `UC <uuid>` references resolve via the existing 10-tag reference vocabulary. **Defaults to freeze in Task 100.100:** `Subordinate:` → `<<include>>` from this UC to the referenced UC; `Superordinate:` → edge only when both documents are in the package (superordinate → this UC); explicit `<<extend>>` / `Extension:` keyword → `<<extend>>`; unresolvable reference → deterministic `note`.
- Label sanitisation (default: embedded `"` → `#quot;`); package layout (default: `left to right direction`).
- File layout in consuming projects (default): `<project>/diagrams/uc/<id>.usecase.puml`, `<id>.sequence.puml`, `package.puml` — git-tracked, regenerable.
- Subfunction judgment rule: a `Subfunction`-level UC gets its own sequence diagram only when the agent (or the user, via `question`) judges it adds interactions beyond its user goal's diagram.

**§3 Validation chain (frozen after design review)**

- Env vars — exactly three, no defaults, no PATH discovery, no opt-in flags:
  1. `SPECMGR_PLANTUML_JAR` — path to `plantuml.jar`; invoked as `java -jar <jar> <args>`.
  2. `SPECMGR_PLANTUML_BIN` — path to an executable speaking the plantuml CLI contract (distro binary, or the user's own platform adapter: docker/k8s/… — reference snippets in the rulebook, *yours to deploy*).
  3. `SPECMGR_PLANTUML_URL` — base URL of a PlantUML server, prefix included (`http://localhost:8080` for the self-hosted jetty image; `https://www.plantuml.com/plantuml` for the public one — the public URL is used only if a user types it).
- Selection: first **set** variable wins; it is the *only* source. Set-but-unavailable (bad path, missing `java`, unreachable URL, failed canary) → hard failure: `source_state` = `misconfigured`/`unavailable`, `reason` + `fix_hint`, **no write, no call to any other source, no network**. All unset → the designed structure-only state.
- Canary probe (also base-URL/diagnosis): a known-valid mini-diagram round-trip; e.g. an HTTP 404 ⇒ fix hint "check the base URL path prefix (bare vs `/plantuml`)".
- Result model (non-raising structured result, the ADR 519d1206 chain precedent): `{structure_ok: bool, valid: bool|None, rendered: bool|None, checked_by: "jar"|"bin"|"url"|"structure", errors: [{line, message, fix_hint}], warnings: [...], source_state: "ok"|"misconfigured"|"unavailable"|"inconclusive"|"none", available: bool, reason: str|None, fix_hint: str|None}`.
- Prompt contract: structure pre-flight always (red ⇒ fix before any parser call — also keeps known-broken content off the network); then the authoritative source; green at the highest available layer + zero UNATTRIBUTED = precondition for writing; `source_state ≠ ok` with a source set ⇒ report + do not write; all-unset ⇒ write with the `' validated: structure-only` header comment.

**§4 Local (jar/bin) invocation contract**

- One unified invocation shape, all stdin/stdout: check = `--check-syntax --no-error-image -pipe` (fallback `-checkonly` when the flag is absent, auto-detected); verdict = **exit code** (0 valid / 200 syntax error on current releases; legacy builds report -1 — any non-zero is invalid, message parsed from the byte stream); error message = the text block `ERROR / <line> / Syntax Error? (Assumed diagram type: …)` scanned from raw output bytes (stdout is binary-contaminated: a placeholder PNG is emitted even for *valid* `-pipe` checks — verified).
- Render proof = `--svg --no-error-image -pipe`: exit 0 + output starts with `<svg` ⇒ rendered; the SVG is written to a temp file, its path optionally reported.
- subprocess list form (never a shell), path/container values charset-validated, 60 s timeout (constant, documented).
- Verified against `plantuml/plantuml:latest` (1.2026.8) including the `--version` probe.

**§5 URL protocol (frozen matrix — single endpoint `GET {base}/svg/~1{enc}`)**

| Status | Body | Classification | Verified |
|---|---|---|---|
| 200 | real diagram SVG (no placeholder markers) | VALID + RENDERED (body = proof) | both servers |
| 400 | "Welcome to PlantUML!" placeholder | SYNTAX INVALID | both (jetty 6260 B; plantuml.com 20073 B) |
| 200 | "Welcome to PlantUML!" placeholder | REQUEST ERROR (exceeds deployment size limit / undecodable / no `@startuml`) | jetty (5377 B, all three cases) |
| 200 | "…generated a bad URL" explanatory | ENCODE ERROR (our payload rejected; should be impossible — client bug/transport) | plantuml.com (2985 B) |
| anything else | — | INCONCLUSIVE → one retry → persistent ⇒ source state | — |

- `~1` URL-header encoding is mandatory (bare-deflate payloads are rejected by the public server with the explanatory SVG — verified).
- Deployment-specific size limit: the dev jetty runs `PLANTUML_LIMIT_SIZE=8192` (decoded) — a 25 KB diagram returns the 200-placeholder (REQUEST ERROR) there while the public server renders the same diagram fine; the client must surface this as a request error with a fix hint, never as INVALID.
- The `/check/` endpoint is **not** used: the self-hosted text dialect (`"(2 participants)"` / `"(Error)"` / `"(Empty)"`) requires stats parsing the review rejected ("(2 participants)" is not stable), and the public PNG-asset dialect (69 B OK / 68 B error assets) is a byte contract against a third party and unsound for undecodable payloads (returns the OK asset — verified). `/svg/` alone gives the same verdicts plus the render proof, identically on both servers.
- Recorded byte fixtures for the dialect tests (offline suite): the placeholder SVGs, the explanatory SVG, the two PNG check assets (retained as documentation fixtures, not used by the protocol).

**§6 Structure checker (`plantuml/structure.py`)**

- Line-oriented subset linter (not a grammar engine): declaration table (actor/participant/usecase, quoted labels, `as` aliases, stereotypes), association/include/extend edges, sequence messages (`->`, `-->`, self), fragment stack (`alt`/`opt`/`loop`/`group`/`box`/`rectangle`/`package`; implicit close at EOF), quote/label sanitisation, comment lines (`'`), `@startuml`/`@enduml` presence, UNATTRIBUTED-marker detection.
- Errors: 1-based line + cause + fix hint (feat-27 convention). Modes: *preflight* (authoritative source available: lenient set ⇒ warnings) and *standalone* (no source: lenient set ⇒ errors).
- The parser-lenient set (all verified to render OK against the real parser — the checker must accept them in preflight mode): unclosed `alt` at EOF, missing `@enduml`, bare `@end`, dangling `A -->`, undeclared participant in a sequence message (auto-created). Missing `@startuml` is an **error** in both modes (the server classifies it as nothing-extractable; the CLI exits "no diagram found").
- Placement: `src/biz/dfch/specmgr/plantuml/`, import-free (no specmgr imports), stdlib-only — deliberately extractable; not a separate PyPI library (the contract is specmgr's emitted subset; consuming projects already depend on specmgr; one published artifact).

**§7 PlantUML ecosystem facts (verified 2026-10-03)**

- plantuml-mcp (github.com/plantuml/plantuml-mcp): **MVP — single `plantuml_version` tool**; syntax validation/rendering explicitly "to be added". Watch item, documented in the skill ("if your host configures a plantuml MCP server with a check/render tool, prefer it"); no dependency.
- plantuml.com `/check/~1…`: PNG assets (OK 69 B sha256 `9cfe511e…`, error 68 B sha256 `cf9a9dfe…`) — recorded, unused by the protocol.
- Canonical error fixture (from PlantUML's own docs): `participant "Famous Bob" aass Bob` → `ERROR / 1 / Syntax Error? (Assumed diagram type: sequence)`, exit 200 on 1.2026.8.
- `docker exec` has no `-T` flag (use `-i` for stdin); the dev stack: `plantuml-server:jetty` on 8080 (bare-path protocol) + `plantuml-cli` (`sleep infinity` entrypoint, `~/src:/data` volume, jar at `/opt/plantuml.jar`) — used only via `SPECMGR_PLANTUML_URL` and/or the user's own `..._BIN` adapter; `plantuml.sh` in that directory is **not** relied upon (render-only, writes next to inputs, no check/pipe contract).
- Parser leniencies per §6; level vocabulary (Cockburn): Summary / User Goal / Subfunction.

**§8 Platform adapters (rulebook reference snippets — user-owned, not specmgr)**

- Docker CLI container (dev): `#!/sh\nexec docker exec -i plantuml-cli java -jar /opt/plantuml.jar "$@"` (+ optional `docker start` guard) behind `SPECMGR_PLANTUML_BIN`; stdin-only use means no volume mapping is needed.
- Kubernetes: `kubectl exec` analogue behind `..._BIN`, or a `plantuml-server` deployment behind `..._URL`.
- CI/prod (recommended): pinned `plantuml.jar` (Maven Central / plantuml.com download) + JDK behind `SPECMGR_PLANTUML_JAR`; fully offline and version-pinnable.
- Air-gapped + authoritative without a JVM: self-hosted `plantuml/plantuml-server` container behind `SPECMGR_PLANTUML_URL`.

**§9 Test strategy**

- `tests/conftest.py`: load the gitignored root `.env` (mirrors `cli.py:_load_default_dotenv`; `.env` is already gitignored) — the local config surface for `SPECMGR_PLANTUML_*`.
- Real-parser tests: `skipif` on source availability (canary probe at collection); run locally whenever a source resolves (dev: jetty URL and/or jar), skip cleanly on GitHub (nothing configured) — no `ci.yml` changes, no marker/addopts change (deliberate inverse of the `embedding_model` opt-in precedent: included by default, excluded only when the environment is absent).
- Offline everywhere: renderer goldens, checker tests (both modes + lenient set), encoder round-trip + vectors, URL-dialect classifier tests against **recorded** byte fixtures, chain no-fall-through test with a mocked transport (ACC-003).

**§10 Phase execution rule**

Each phase ends in exactly one commit containing all of the phase's code + tests + docs (`server.py` docstring, `docs/MCP.md` regen, `AGENTS.md`) + the Progress update for that phase. The pre-commit hook suite (ruff format/check, vulture, `specmgr docs`/`adr-toc`/drift, full `pytest -n auto` — including the env-gated real-parser tests when a source resolves — and coverage-badge) is the gate; a red hook is fixed within the same phase before committing. No intermediate commits, no amend of a failed commit.

### Related Decisions

- Precedent, repair trio: MCP prompt + OpenCode skill + command pattern (`general/prompts/repair`, `.opencode/skill/repair/`, `.opencode/command/repair.md`)
- Precedent, actionable validation errors: feat-27 (`models/md/_errors.wrap_tool_errors`)
- Precedent, non-raising structured results: the ADR 519d1206 chain (`validate`, `set_status` invalid-status, `get_<d>` parse-failure)
- Precedent, environment-dependent tests: feat-134 `embedding_model` marker (inverted here: availability-gated, not opt-in)
- Precedent, domain-knowledge resource shape: `specmgr://rsk/tara`, `specmgr://dtais`
- Precedent, the v1 diagram renderer being ported: `uc/models/v1/uc_diagram.py` (`_actor_label`, alias pattern) — `render_uc_diagram` was explicitly "not yet ported" in the v2 package docstring
- Pending (Task 100.120): ADR vs feature-level decision for the `plantuml/` package placement + validation-chain policy (leaning ADR: the package is cross-cutting by design)

### Task List

#### Phase 100: Mapping spec and frozen validation protocol

- [ ] Task 100.100: Author the rulebook content: mapping spec (§2) freezing the open defaults (include/extend keyword map, `#quot;` label sanitisation, left-to-right package layout, file layout, Subfunction judgment rule)
- [ ] Task 100.110: Author the rulebook content: validation chain (§3–§5) — env-var table, strict selection / no-fall-through semantics, local invocation contract, URL protocol matrix with verified fixtures, size-limit note
- [ ] Task 100.120: Decide ADR vs feature decision for `plantuml/` placement + chain policy; create the ADR if architecture-level
- [ ] Task 100.130: Author platform-adapter reference snippets (§8) + production guidance in the rulebook; confirm no wrapper ships in the repo
- [ ] Task 100.140: Register `specmgr://uc/plantuml` resource + `server.py` docstring + `specmgr mcp-docs` regen; Phase 100 quality gate (single commit, full pre-commit suite)

#### Phase 110: `plantuml/` package, renderers, data files

- [ ] Task 110.100: `tests/conftest.py` dotenv load (mirror `cli._load_default_dotenv`) + source-availability gate helper + gated smoke test (clean skip on unconfigured checkouts)
- [ ] Task 110.110: `plantuml/encode.py` — `~1` URL text encoding + decode round-trip, tested against the verified vectors
- [ ] Task 110.120: `uc/data/plantuml_template.md` + `uc/data/plantuml_example.md` (Buy Goods usecase + sequence; mapping comments; both pass the checker in both modes)
- [ ] Task 110.130: `plantuml/structure.py` — two-mode checker with actionable errors, lenient-set acceptance (verified cases as golden tests), template/example pass tests
- [ ] Task 110.140: `plantuml/backends.py` — jar + bin backends: unified `-pipe` invocation, flag auto-detect, exit-code verdict, byte-safe error-text scan, canary probe, subprocess contract; env-gated real-parser tests
- [ ] Task 110.150: `plantuml/url.py` — single-endpoint `/svg/` matrix classifier, one retry, INCONCLUSIVE handling, recorded byte-fixture tests (offline)
- [ ] Task 110.160: `plantuml/chain.py` + result model — strict first-set selection, no fall-through, `source_state`/`fix_hint`; no-fall-through privacy test (ACC-003, mocked transport)
- [ ] Task 110.170: `uc/models/v2/renderer.py` — `render_uc_diagram`, `render_use_case_package`, `render_uc_sequence_skeleton` + golden tests; v2 `__init__.py` docstring update
- [ ] Task 110.180: Phase 110 quality gate (single commit, full pre-commit suite incl. env-gated real-parser tests when a source resolves)

#### Phase 120: MCP surface

- [ ] Task 120.100: Tools `get_uc_diagram`, `get_use_case_package_diagram`, `get_uc_sequence_skeleton` (read-only, cache-aware, `_path_safety`-guarded) + tests
- [ ] Task 120.110: Tools `validate_plantuml` (chain wrapper, non-raising result), `get_uc_plantuml_template`, `get_uc_plantuml_example`, `plantuml_encode` + `specmgr://config` plantuml section + tests
- [ ] Task 120.120: Resources `specmgr://uc/plantuml-template`, `specmgr://uc/plantuml-example` (packaged-data pair, unversioned URIs) + tests
- [ ] Task 120.130: Prompt `generate_uc_sequence_diagram` — narrated flow: TodoWrite, read UC, skeleton, attribution + `question` contract, UNATTRIBUTED-zero rule, validate loop (green at highest layer before write), structure-only header, never commit
- [ ] Task 120.140: `server.py` docstring, `specmgr mcp-docs` → `docs/MCP.md`, `AGENTS.md` uc bullet update
- [ ] Task 120.150: Phase 120 quality gate (single commit, full pre-commit suite)

#### Phase 130: Supporting CLI

- [ ] Task 130.100: `specmgr diagram uc [ids|all] --out <dir>` (+ `--check` regenerate-and-diff) + tests
- [ ] Task 130.110: `specmgr plantuml-check <path...>` (chain, exit codes mirroring the tool) + tests
- [ ] Task 130.120: `specmgr plantuml-encode <path|->` (offline `~1` URLs) + tests
- [ ] Task 130.130: Phase 130 quality gate (single commit, full pre-commit suite)

#### Phase 140: Host artifacts, conventions, end-to-end

- [ ] Task 140.100: OpenCode skill `.opencode/skill/uc-diagram/SKILL.md` (thin, self-triggering, trio pattern; plantuml-mcp watch note) + optional `/uc-diagram` command
- [ ] Task 140.110: `.specmgr/conventions.md` section (attribution authoring style: steps start with the participant label; diagram file layout; structure-only header) + optional `create_uc`/`update_uc` prompt nudge
- [ ] Task 140.120: End-to-end walkthrough on the example UC (prompt → file → green at the configured source; ambiguous step → `question` record) + docs consistency pass (rulebook links, AGENTS.md, README pointers)
- [ ] Task 140.130: Phase 140 quality gate (single commit, full pre-commit suite)

## Progress

### Current Status

**As of 2026-10-03**: Design review complete — the plan, mapping spec, validation chain (3 env vars, strict selection, single-endpoint URL matrix), and phase structure are frozen. No implementation started; Phase 100 is next.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03 08:05:00.000Z - Created

Feature created from the design conversation: formalised UC → PlantUML pipeline (renderers, sequence skeleton + agent attribution, strict 3-source validation chain, structure-checker floor, template/example, supporting CLI, host skill). GitHub issue #185.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03 08:05:00.000Z - Strict source selection, no fall-through

First-set-wins over `SPECMGR_PLANTUML_JAR` → `SPECMGR_PLANTUML_BIN` → `SPECMGR_PLANTUML_URL`; a set-but-misconfigured source is a hard failure (no write, no call to any other source). Rationale: a typo in a local source must never silently phone the diagram content out to the public plantuml.com. No PATH auto-discovery, no public default — the all-unset state is the only designed degradation (structure-only).

#### 2026-10-03 08:05:00.000Z - URL protocol: single `/svg/` endpoint, `/check/` dropped

The frozen matrix (200+real = valid+rendered; 400+welcome = invalid; 200+welcome = request error; 200+bad-URL = encode error; unknown = inconclusive → retry → source state) gives both servers one protocol, verified empirically. Rationale: the self-hosted `/check/` text dialect needs stats parsing the review rejected ("(2 participants)" is not stable), and the public PNG-asset dialect is a flimsy byte contract that is unsound for undecodable payloads (returns the OK asset). `/svg/` alone is strictly more informative (verdict + render proof).

#### 2026-10-03 08:05:00.000Z - Backends are jar/bin/url only; platforms adapt via user-owned `..._BIN` scripts

No docker/k8s backend inside specmgr (whack-a-mole; each is just an executable behind `..._BIN`). Rationale: specmgr abstracts plantuml, not platforms; reference adapter snippets ship in the rulebook, deployment is the user's. The dev jetty container needs no adapter at all (`..._URL=http://localhost:8080`).

#### 2026-10-03 08:05:00.000Z - Structure checker: two modes, never stricter than the parser

Preflight mode treats the verified parser-lenient cases (unclosed `alt` at EOF, missing `@enduml`, bare `@end`, dangling arrow, auto-declared participant) as warnings; standalone mode (no source configured) promotes them to errors. Rationale: an authoritative gate available ⇒ false reds would break the agent's repair loop and tempt "fixes" that change valid diagrams; no gate ⇒ stricter is safe and desirable. All real errors are caught early in both modes with line + cause + fix hint.

#### 2026-10-03 08:05:00.000Z - Sequence diagrams: deterministic skeleton + agent attribution + `question`

The renderer emits everything deterministic (participants, trigger, notes, `alt` structure from structurally validated step references, first-word pre-fill); the agent assigns remaining senders by understanding the free text and MUST ask the user when not confident. Rationale: steps are free-form sentences — full determinism would require a breaking UC schema change; the design review requires explicit clarification over guessing.

#### 2026-10-03 08:05:00.000Z - `plantuml/` lives in-package (import-free, stdlib-only), not as a separate PyPI library

Rationale: the checker's contract is specmgr's emitted subset; consuming projects already depend on specmgr; one published artifact. Written import-free so extraction stays cheap if ever needed.

#### 2026-10-03 08:05:00.000Z - One commit per phase, pre-commit suite as the quality gate

Each phase ships as a single commit (code + tests + docs + Progress update); the full pre-commit hook suite (ruff, vulture, doc drift, full pytest incl. env-gated real-parser tests when a source resolves, coverage-badge) gates it. Real-parser tests run only where a `SPECMGR_PLANTUML_*` source is configured — i.e. on developer machines, never on GitHub CI (no source configured there).
