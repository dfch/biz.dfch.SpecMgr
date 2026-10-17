---
classification: null
created: '2026-10-15T11:46:49.911+02:00'
id: feat-214-rel-invalid-diag
status: review
type: feat
updated: '2026-10-17T06:06:08.272+02:00'
version: 1.0.0
---

# Feature: Reference-Graph Diagrams — Parser-Valid Layout, Label-Free Edges, and Reverse Refs in the Agent Flow

## Plan

### Overview

The deterministic reference-graph diagrams shipped by feat-207-reference-graph (`get_reference_diagram` / `get_reference_diagram_all` MCP tools, the `specmgr diagram refs` CLI, and the `specmgr-refs` skill's diagram workflow) have three defects (GitHub issue #214):

1. **Invalid PlantUML syntax** — the frozen per-domain grouping `package "TYPE" … end package` is rejected by the real PlantUML parser: any component declaration inside a braceless `package` block is a syntax error (verified against PlantUML 1.2026.8; the error lands on the first inner component line). The layout shipped unverified because the structure checker (the only validator that actually ran) accepted it with zero findings in both modes, while the env-gated real-parser gate skipped cleanly in Phase 100 (no `SPECMGR_PLANTUML_*` source configured) and its "skipped" verdict was recorded as ship-ready.
2. **Missing reverse references** — the scoped relationship diagram shows only outgoing references by default; the issue requires incoming (reverse) references to be displayed too.
3. **Unwanted edge labels** — every edge carries the uniform `: refers to` label, which was never intentionally approved; the requested form is a plain arrow connector from source to destination with no text.

This feature fixes the frozen emission layout (the `package` blocks become curly-brace `component "TYPE" { … }` domain groups, and edges render label-free), amends the frozen reference-graph rulebook with dated corrections and a recorded real-parser verdict, regenerates every byte-stable golden, adds a structure-checker tripwire for the demonstrated false-negative class, makes the `specmgr-refs` skill's diagram workflow always request `reverse` for scoped diagrams (the builder/tool/CLI API default stays OFF by explicit decision), and closes the root-cause process gap with a CI job that downloads a pinned PlantUML 1.2026.8 jar (URL + SHA-256) and runs the full suite, so the real parser — not just the checker — verifies every frozen emission artifact on every commit.

### Requirements

- REQ-001: The emitted reference-graph layout uses `component "TYPE" { … }` (a curly-brace nested-component group, closed with `}`) for the per-domain node grouping, replacing `package "TYPE" … end package` — one group per non-empty domain, in `ALL_DOMAINS` order, nodes sorted by id inside the group, unresolved nodes still top-level before the first group.
- REQ-002: Edges render label-free: `{src-alias} --> {dst-alias}` off-cycle and `{src-alias} -[#red]-> {dst-alias}` on-cycle — no `: refers to` (or any other) label — uniformly for scoped and registry-wide diagrams.
- REQ-003: The full emission subset (the §2.9 worked example, regenerated for the new layout) parses and renders through the real PlantUML 1.2026.8 parser without a syntax error; a new env-gated golden parser sweep runs every golden under `tests/fixtures/reference-graphs/goldens/` through `chain.validate_plantuml` asserting `valid=True` + `rendered=True` + the render-proof (the SVG body carries a node title and no crash marker); every emitted diagram passes the two-mode structure checker with ZERO findings in both modes.
- REQ-004: The structure checker gains a verified tripwire rule: a `package` fragment containing component declarations (a `component` declaration line or a short-form `[X]` line) must be closed by a `}` line — a named `end package` close (braceless-open or curly-open) or an unclosed such fragment at block end is an error in BOTH modes, with a fix hint naming the curly-brace group form. `package` fragments without component declarations (the UC sequence subset) are unaffected; no existing golden gains a finding.
- REQ-005: The frozen reference-graph rulebook (`specmgr://reference-graph`, `general/data/general_reference_graph.md`) is amended — §2.1 shape, §2.7 (domain groups), §2.8/§2.9 (label-free edges + regenerated worked example) — with dated correction notes in the feat-207 style; §4.3 records the real-parser verdict (PlantUML 1.2026.8, pinned URL + SHA-256) replacing the 2026-10-10 "skipped" verdict; §7.1 records the tripwire amendment and restates the checker contract (a structure-only verdict means "plausible / marker-clean", never "valid" — the real parser is the sole validity authority).
- REQ-006: All byte-stable goldens pinning the old layout are regenerated for the new layout: every file under `tests/fixtures/reference-graphs/goldens/`, the `_EMITTED_SUBSET` constant in `tests/plantuml/test_reference_graph_subset.py`, the rulebook-resource drift pin in `tests/general/resources/test_reference_graph.py`, and the gate test's render-proof assertion (the proof string changes from "refers to" to a node title).
- REQ-007: The `specmgr-refs` skill's diagram workflow requests `reverse` for every SCOPED diagram it produces (MCP `reverse=True`, CLI `--reverse`), states the resulting cost (the scoped diagram includes the full 13-domain scan, O(registry size)), and leaves the registry-wide surface unchanged (its edges already run both ways).
- REQ-008: The API defaults are UNCHANGED: `build_source_graph`, `get_reference_diagram`, and `specmgr diagram refs` keep `reverse=False` as the default (opt-in via the existing parameter/flag) — the reverse-display obligation is met at the agent/skill layer only (planning-session decision for issue #214).
- REQ-009: A CI job (pinned Python 3.13) downloads the pinned PlantUML 1.2026.8 release jar (pinned URL + SHA-256 verified before use), exports `SPECMGR_PLANTUML_JAR`, and runs the full test suite, so the env-gated real-parser tests (all `require_plantuml_source`-gated tests, incl. the reference-graph subset gate and the golden parser sweep) execute and PASS instead of skipping; the job must be green.
- REQ-010: Every documentation surface describing the emission layout, the edge label, or the reverse default (the `get_reference_diagram`/`get_reference_diagram_all` and `diagram_refs` docstrings, the README how-to, `AGENTS.md`, and the regenerated `docs/` incl. `docs/MCP.md`) matches the new behaviour.

### Acceptance Criteria

- [x] ACC-001: The §2.9 worked example (rulebook + `_EMITTED_SUBSET` + the anchor golden) contains no `package "…"`/`end package` lines, uses `component "TYPE" { … }` groups, carries no edge labels, and parses + renders through the real PlantUML 1.2026.8 parser (the env-gated gate passes where a source is configured; the render-proof finds a node title in the SVG body and no crash marker).
- [x] ACC-002: Every regenerated golden under `tests/fixtures/reference-graphs/goldens/` passes the structure checker with ZERO findings in both modes (the existing goldens-directory sweep stays green), and the new golden parser sweep passes for every golden under a configured source (REQ-003's sweep).
- [x] ACC-003: The tripwire rule fires (error, both modes, curly fix hint) on the verified parser-failing shapes (braceless `package` + inner component; curly-open `package` + `end package` close) and on no existing UC/reference golden (zero false positives; sequence-diagram packages with participants unaffected).
- [x] ACC-004: The `specmgr-refs` skill's diagram workflow text mandates `reverse` for scoped diagrams (MCP `reverse=True` / CLI `--reverse`) with the O(registry-size) cost note, while the builder/tool/CLI signatures keep the `reverse=False` default (the existing schema-default pin test stays green unchanged).
- [x] ACC-005: The new CI job verifies the pinned jar's SHA-256, runs the suite, and reports the real-parser gates as PASSED, not skipped — `pytest -rs` under the job shows no `require_plantuml_source` skip reason for the reference-graph subset gate or the golden parser sweep.
- [x] ACC-006: `ruff format --check`, `ruff check`, `vulture`, and the full test suite (`uv run --frozen pytest -n auto --cov=src --cov-report=`) are green with the layout + label fix, tripwire rule, rulebook amendment, regenerated goldens, sweep test, skill change, CI job, and doc updates committed.

### Scope

#### Included

- The renderer layout + label fix in `general/models/reference_graph.py` (curly domain groups, label-free edges) and its docstrings.
- The structure-checker tripwire rule in `plantuml/structure.py` + its control tests, and the dated checker-grammar notes (UC rulebook §6.1 + reference-graph rulebook §7.1) incl. the contract restatement.
- The frozen rulebook amendment (`general/data/general_reference_graph.md`: §2.1, §2.7, §2.8, §2.9, §4.3, §7.1) and the rulebook-resource drift pin.
- Golden regeneration: all 22 files under `tests/fixtures/reference-graphs/goldens/`, the §2.9 anchor, the `_EMITTED_SUBSET` constant, the gate test's render-proof assertion; plus the new env-gated golden parser sweep test.
- Pre-implementation design verification over real registry emissions (render current output — expect parser red — and the mechanically-fixed output — expect green — through the pinned jar, recorded in Progress).
- The `specmgr-refs` skill diagram-workflow change (always request `reverse` for scoped diagrams + cost note + label-free note).
- The new CI job (pinned PlantUML 1.2026.8 jar: pinned URL + SHA-256, `SPECMGR_PLANTUML_JAR`, full suite, gates must pass).
- Doc-surface updates: tool/CLI docstrings, README how-to, `AGENTS.md`, regenerated `docs/` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`).

#### Explicitly Out Of Scope

- Flipping the `reverse` default in the builder / MCP tool / CLI (REQ-008 — planning-session decision: the API stays opt-in).
- The `/ref-graph` command's literal 1:1 flag mapping (it stays user-flag-driven; the layout + label fixes reach it automatically via the CLI renderer).
- The 14-entry skinparam palette, the bracketed aliases, the red on-cycle arrow form, and the label truncation rules (all verified real-parser-valid; unchanged).
- Transitive incoming expansion (`reverse` remains additive and direct-only on the incoming side, rulebook §3.2).
- Registry-wide diagram semantics (it already contains every reference edge in both directions; only its layout and edge labels change).
- Extending the tripwire rule beyond `package` fragments (the demonstrated gap; `box`/`rectangle` grouping of components is unverified and untouched).
- Committing the PlantUML jar to the repository (planning-session decision: pinned download in CI + local `.env` instead).
- Dropping the structure checker (planning-session decision: kept — sourceless floor, actionable diagnostics, UNATTRIBUTED marker detection, pre-flight short-circuit; the contract is restated, not removed).
- Fixing pre-existing, unrelated test failures the newly-enabled gate might surface beyond what is needed for a green gate job (any such finding gets recorded as a new issue, per Task 120.110).

### Design Notes

**Parser-verification evidence (2026-10-15, real PlantUML 1.2026.8 / 149874a, GPL source build, the same version the validation chain's crash matrix documents):**

- The old frozen layout FAILS: the §2.9 worked example answers `ERROR 25 — Syntax Error? (Assumed diagram type: component)`; line 25 is the first component declaration inside the braceless `package "REQ"` block. Isolation: EVERY braceless `package NAME … end package` form fails (bare `component Foo`, quoted component, with/without alias, the short `[Foo]` form — the class-diagram analogue fails too): in this parser a component-diagram package block must open with `{`. A mixed close (`package "REQ" {` … `end package`) also fails. The error line is the first inner component, NOT the package open — the real parser's diagnosis is coarser than the cause (an argument for keeping the checker's actionable findings).
- The fixed layout PASSES: `component "TYPE" { … }` groups (the issue's literal diagnosis — "a 'component' must use curly braces") exit 0 over the full worked example, including the skinparam palette, top-level unresolved nodes, bracketed-alias declarations, and the `-[#red]->` cycle edges.
- Label-free edges PASS: the same subset with `: refers to` removed from every edge line (plain `-->` and red `-[#red]->`) exits 0 in the real parser and yields ZERO structure-checker findings in both modes (the edge operands are declared bracketed aliases, so the association branch emits no undeclared-node warning; the red form is outside the checker's frozen line grammar, silently accepted as today).
- The 14-entry `skinparam component { backgroundColor<<ST>> … }` block is not merely accepted — the rendered SVG carries the palette fills (Pink `#FFC0CB`, PaleTurquoise `#AFEEEE`, LightBlue `#ADD8E6`, DarkRed `#8B0000`) and the red arrow `#F00`, so the colour scheme works as designed.
- **Tripwire rule (REQ-004):** a `package` fragment containing component declarations must close with `}`. Both verified parser-failing shapes are covered: the braceless open + `end package` close (Q1 matrix) and the curly open + `end package` close (R1). The rule is content-conditional, so `package` fragments holding sequence content (participants) — the UC subset, parser-verified in feat-185 — are untouched. The checker's line-oriented fragment stack already tracks `package` openers and named closes; the amendment records the open shape (`{` or not) and whether the fragment collected a component declaration (a `component` keyword line or a short-form `[X]` line), and fires at the named close or the block boundary for an unclosed fragment.
- **Root cause / process gap:** the Phase 100 real-parser gate existed to prevent exactly this, but skipped cleanly (no `SPECMGR_PLANTUML_*` source configured) and the frozen candidate shipped. The structure checker is a line-oriented subset linter, not a parser — here it was MORE permissive than the parser, a gap the "never reject what the parser accepts" invariant does not cover (it forbids false positives, not false negatives). Hence REQ-009: a CI job with a pinned source makes the parser a permanent, always-running authority, and REQ-003's sweep extends parser verification from one synthetic subset to every frozen golden. Convention going forward (recorded in rulebook §4.3): an emission layout is not frozen on a skipped gate.
- **Checker contract restatement (REQ-005, §7.1):** the chain's result model already separates `structure_ok` from `valid`/`rendered` + `checked_by`; the restatement is doc-level discipline: a `valid=True` verdict is a parser verdict only when `checked_by != structure` — structure-only means "plausible / marker-clean", never "valid". The checker keeps every load-bearing role: the sourceless validation floor (incl. the deliberate sourceless pre-commit `SPECMGR_TESTS_NO_DOTENV` re-run), actionable line/cause/fix-hint diagnostics, UNATTRIBUTED marker detection (invisible to the parser — comments), millisecond speed without a JVM, and the pre-flight short-circuit that never invokes the parser on a structure red.
- **Reverse refs at the agent layer (REQ-007/REQ-008):** the builder already implements `reverse` (additive, direct-only, full 13-domain scan) — no builder change. The `specmgr-refs` skill's diagram workflow is the agent path behind the complaint, so it always requests `reverse` for scoped diagrams, with the O(registry-size) cost stated (the same cost the skill's separate reverse workflow already documents). The `/ref-graph` command keeps its 1:1 input-to-flag mapping (it never reinterprets), so CLI users opt in explicitly with `--reverse`.
- **Jar pin (REQ-009):** the PlantUML GitHub release artifact is immutable per tag — pinned URL `https://github.com/plantuml/plantuml/releases/download/v1.2026.8/plantuml-1.2026.8.jar` plus SHA-256 `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462` (the verified 1.2026.8/149874a build), verified in CI before use. The jar is ~28.5 MB of GPL binary — deliberately NOT committed (clone bloat, license artifact, frozen version); a version upgrade is a one-line URL + hash change with an explicit re-verification. Local dev: the gitignored repo-root `.env` (loaded by `tests/conftest.py` at collection) — e.g. `SPECMGR_PLANTUML_JAR=/home/user/plantuml.jar` on this machine — runs the real-parser tests locally with zero repo changes.
- **CI job shape:** pinned to a single Python (3.13, mirroring the existing docs-drift pin), download + hash-verify + export `SPECMGR_PLANTUML_JAR`, then `uv run --frozen pytest -n auto -rs` (full suite, so every env-gated real-parser test runs and its skip/pass state is visible in the report).

### Related Decisions

- FEAT feat-207-reference-graph (`.specmgr/feat/feat-207-reference-graph/README.md`, GitHub issue #207) — the feature whose frozen emission layout and edge-label decision this feature amends.
- The frozen reference-graph rulebook (`specmgr://reference-graph`, `src/biz/dfch/specmgr/general/data/general_reference_graph.md`) — the normative document amended here (§2.1/§2.7/§2.8/§2.9 layout + labels, §3.2 reverse semantics, §4.3 gate verdict, §7.1 checker amendment + contract).
- ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4 — the `plantuml/` package placement + strict first-set-wins chain policy (the gate's chain and the two-mode checker live there).
- The 2026-10-10 structure-checker amendment (reference-graph rulebook §7.1, feat-207 Phase 100) — the `component` keyword + bracketed-alias grammar this layout relies on (unchanged); the tripwire is a NEW dated amendment alongside it.
- The UC rulebook §6.1 (`specmgr://uc/plantuml`) — the shared frozen checker grammar the tripwire amends with a dated note (the UC subset itself stays byte-identical; regression-pinned by the existing UC goldens).
- GitHub issue #214 (this feature) and its planning-session decisions: reverse stays API-default-OFF (agent flow always requests it), `component "TYPE" { }` grouping, label-free edges, jar by pinned download (not in git), checker kept + tripwire.

### Task List

#### Phase 100: Design verification + checker + renderer + rulebook

- [x] Task 100.100: Design verification BEFORE any code change: obtain the current real-registry emissions (the `get_reference_diagram_all(include_feat=False)` MCP tool — read-only source return — plus a few `get_reference_diagram(type, id, reverse=True)` over live documents), save them to /tmp scratch, run the pinned jar (SHA-256-verified 1.2026.8) over each — expect the syntax error; mechanically transform (curly domain groups + label-free edges) and re-run — expect exit 0 + a rendered SVG carrying the palette fills and node titles; record both verdicts in `### Updates`.
- [x] Task 100.110: Implement the structure-checker tripwire (`plantuml/structure.py`): a `package` fragment containing component declarations (a `component` declaration line or a short-form `[X]` line) must close with `}` — a named `end package` close (braceless-open or curly-open) or an unclosed such fragment at block end is an error in BOTH modes with a curly-brace fix hint; content-conditional so sequence packages are untouched; add control tests (the verified parser-failing shapes fire; every existing UC + reference golden stays zero-finding).
- [x] Task 100.120: Update `render_reference_graph` (`general/models/reference_graph.py`): emit `component "{TYPE}" {` / `}` instead of `package "{TYPE}"` / `end package` for the per-domain groups, and label-free edge lines (`{src} --> {dst}` / `{src} -[#red]-> {dst}`, the `_EDGE_LABEL` suffix removed); the top-level unresolved section, edge sorting/dedup, cycle detection, and blank-line layout unchanged; update the module + function docstrings.
- [x] Task 100.130: Amend the rulebook (`general/data/general_reference_graph.md`): §2.1 shape (curly groups, label-free edges), §2.7 rewritten as the curly-brace domain-group rule, §2.8 label-free edge rule, §2.9 worked example regenerated byte-exact, §4.3 verdict replaced (PlantUML 1.2026.8, pinned URL + SHA-256: old layout line-25 failure, new layout + label-free pass, the "not frozen on a skipped gate" convention), §7.1 tripwire amendment + checker-contract restatement — dated correction notes in the feat-207 style; add the matching dated note to the UC rulebook §6.1.
- [x] Task 100.140: Regenerate every golden under `tests/fixtures/reference-graphs/goldens/` (all 22 files) from the updated renderer/builders; update the `_EMITTED_SUBSET` constant in `tests/plantuml/test_reference_graph_subset.py` to the new §2.9 worked example verbatim (the rulebook↔gate drift pin); add the env-gated golden parser sweep test (every reference-graph golden through `chain.validate_plantuml` → `valid=True` + `rendered=True` + render-proof with a node-title proof string); change the gate test's render-proof assertion ("refers to" → a node title); update the rulebook-resource drift pin in `tests/general/resources/test_reference_graph.py`.

#### Phase 110: Skill reverse workflow + docs

- [x] Task 110.100: Update the `specmgr-refs` skill's diagram workflow (`.opencode/skills/specmgr-refs/SKILL.md`): scoped diagrams ALWAYS request `reverse` (MCP `reverse=True`, CLI `--reverse`), the cost note (the scoped diagram includes the full 13-domain scan, O(registry size)) added to the workflow's report notes, the edge-label note updated (label-free arrows, red form on cycles), registry-wide surface unchanged, and the frozen disambiguation rule intact.
- [x] Task 110.110: Update the doc surfaces: the `get_reference_diagram`/`get_reference_diagram_all`/`diagram_refs` docstrings where they describe the emission layout or the `: refers to` label, the README how-to (the tool + CLI paragraphs), the `AGENTS.md` `general/` bullet (the reference-graph layout + edge wording), then regenerate `docs/` (`uv run --frozen specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`) and commit the diff.
- [x] Task 110.120: Confirm the API defaults are untouched: the `reverse=False` schema-default pin in `tests/general/tools/test_get_reference_diagram.py` and every explicit `reverse=True` builder/tool test stay green with NO signature change (REQ-008 evidence).

#### Phase 120: CI real-parser gate job

- [x] Task 120.100: Add the CI job to `.github/workflows/ci.yml` (single pinned Python 3.13, mirroring the docs-drift pin): download `https://github.com/plantuml/plantuml/releases/download/v1.2026.8/plantuml-1.2026.8.jar`, verify SHA-256 `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462` (fail the job on mismatch), export `SPECMGR_PLANTUML_JAR`, and run `uv run --frozen pytest -n auto -rs` so the env-gated real-parser tests execute and their skip/pass state is visible.
- [x] Task 120.110: Make the job green: fix any failure the newly-enabled gate surfaces (none expected — the 10 `require_plantuml_source`-gated files were designed against 1.2026.8); if an unrelated pre-existing failure appears, record it as a new issue and scope this job to the `tests/plantuml/` + reference-graph + UC selections, documenting the reason in the job.
- [x] Task 120.120: Update the rulebook §4.3 verdict and the gate test's docstring: the gate now RUNS in CI (replacing the "skipped — re-verify where a source is configured" wording) and the local `.env` dev flow is documented.

#### Phase 130: Verification + closeout

- [x] Task 130.100: Run the full quality gate: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, and the full suite `uv run --frozen pytest -n auto --cov=src --cov-report=` (ACC-006).
- [x] Task 130.110: Walkthrough evidence with `SPECMGR_PLANTUML_JAR` configured (local `.env`): `specmgr diagram refs <type> <id> --reverse` + `specmgr plantuml-check` (expect `checked_by=jar`, `valid=true`) and `specmgr diagram refs all` rendered to SVG (eyeball the palette + label-free arrows) — recorded in `### Updates`.
- [x] Task 130.120: Closeout: `CHANGELOG.md` `[Unreleased]` entry, mark the verified ACCs `- [x]`, and `set_status(id, type="feat", status="review")`.

## Progress

### Current Status

**As of 2026-10-16**: CLOSED OUT — all four phases complete (Tasks 100.100–130.120); status is `review` (set via the `set_status` MCP tool in Task 130.120). The Task 130.100 quality gate is green (`ruff format --check` / `ruff check` / `vulture` clean; full suite 4687 passed / 4 skipped — all four the URL-matrix skips, ZERO `require_plantuml_source` skips). The Task 130.110 walkthrough confirmed the new layout end-to-end over the real CLI surfaces with the locally configured pinned jar: scoped `specmgr diagram refs feat feat-207-reference-graph --reverse` (16 label-free edges incl. the incoming `[feat-214-rel-invalid-diag] --> [feat-207-reference-graph]`, curly domain groups) → `specmgr plantuml-check` answered `checked_by=jar valid=true rendered=true source_state=ok` (the CLI picks up the gitignored repo-root `.env` — no inline env var needed); registry-wide `specmgr diagram refs all` (8 curly groups, 306 label-free edges) rendered through the pinned jar to a 332 KB SVG carrying the palette fills, 20 red `#F00` cycle-arrow segments, and node titles, with ZERO `refers to` text and no crash marker. Closeout (Task 130.120): `CHANGELOG.md` `[Unreleased]` entry added, ACC-001/002/003/004/006 marked verified — and ACC-005 is now verified and marked too: the first `plantuml-parser` CI run (PR #216, 2026-10-17) executed and passed (SHA-256 step OK; `4693 passed, 4 skipped` with every skip a URL-matrix test — zero `require_plantuml_source` skips), so ALL SIX ACCs are verified (status stays `review`). The walkthrough also surfaced and fixed a LATENT parseability defect in this plan document (the bullet-form `Decisions Made` section introduced in Phase 100 failed `parse_feat` — `list_feat` kept showing it transiently healthy per the ADR 3982712a time-qualification while the reference-graph builders silently skipped it, dropping feat-214 from the live diagrams; see the Phase 130 entry in Decisions Made).

**Phase 120 record (Tasks 120.100–120.120 done).** The `plantuml-parser` CI job is in `.github/workflows/ci.yml` (single pinned Python 3.13.13, mirroring the `build` job's docs-drift pin): it downloads the pinned PlantUML 1.2026.8 release jar to `$RUNNER_TEMP` (kept out of the repo), hash-verifies it in its own step BEFORE any use (the job fails on mismatch), exports `SPECMGR_PLANTUML_JAR`, and runs the FULL suite with `uv run --frozen pytest -n auto -rs` — so every `require_plantuml_source`-gated test (incl. the reference-graph subset gate and the 22-golden parser sweep) runs and passes on the commit path instead of skipping (ACC-005). Local proxy evidence (GitHub Actions itself cannot run here): the workflow YAML parses, the job's exact `sha256sum --check --strict` line passes against the verified local jar and FAILS (rc=1) on a wrong hash, and the job's exact pytest invocation reports 4687 passed / 4 skipped with the ONLY skip reasons the URL-matrix ones (zero `require_plantuml_source` skips). Rulebook §4.3 gained the dated Phase 120 amendment note (the gate now RUNS in CI; the local `.env` dev flow documented) and the gate test's docstrings match; the resource drift pin was extended additively for the note (all pins green). The Task 120.110 scoping branch was NOT needed (no pre-existing failure surfaced).

**Phase 110 record (Tasks 110.100–110.120 done).** The `specmgr-refs` skill's diagram workflow now mandates `reverse` for every scoped diagram (MCP `reverse=True`, CLI `--reverse`) with the O(registry-size) cost in the report notes and the label-free edge note (the registry-wide surface and the frozen disambiguation rule are unchanged; the skill pin test gained the matching new phrases). All doc surfaces matching the new behaviour: the `get_reference_diagram`/`get_reference_diagram_all` tool docstrings + MCP descriptions, the `general/tools` package docstring, the `server.py` registration docstring, the README how-to, and the `AGENTS.md` `general/` bullet — `docs/api/` + `docs/MCP.md` regenerated (`: refers to` / package-grouping wording gone from every generated surface). REQ-008 confirmed: the `reverse=False` MCP schema-default pin and every explicit `reverse=True` builder/tool test stay green with NO signature change (AST-verified identical to HEAD for `get_reference_diagram`, `get_reference_diagram_all`, `diagram_refs`, and both builders).

**Phase 100 record (Tasks 100.100–100.140 done).** The pre-implementation design verification re-confirmed the diagnosis against the live registry (Task 100.100: the four current real-registry emissions all fail the pinned 1.2026.8 parser with the syntax error; the mechanically-transformed emissions + the regenerated §2.9 worked example pass with palette fills, node titles, and red `#F00` arrows in the SVGs). The structure-checker tripwire is implemented with control tests (a `package` fragment collecting component declarations must close with `}` — error in both modes, curly-brace fix hint; sequence packages and the corrected curly form stay zero-finding). The renderer emits the curly `component "TYPE" { … }` domain groups and label-free edges; the rulebook (§2.1/§2.7/§2.8/§2.9/§4.3/§7.1) and the UC rulebook §6.1 carry the dated 2026-10-15 corrections incl. the real-parser verdict and the checker-contract restatement; all 22 goldens are regenerated; the env-gated subset gate + the new golden parser sweep run (not skip) under the locally configured pinned jar and pass.

### Updates

<!-- Newest entry first — prepend new entries directly below this comment. -->

#### 2026-10-17T04:06:08.272Z - PR #216 CI green (dev-merge conflict resolved) — ACC-005 verified and marked

PR #216 (github.com/dfch/biz.dfch.SpecMgr/pull/216) now has its
merge-conflicts resolved against `dev` and its CI is FULLY GREEN. The only
conflict was `CHANGELOG.md`'s `## [Unreleased]` (feat-213 had landed its own
`[Unreleased]` entry meanwhile); it was resolved by consolidating both
sides' entries into single `### Fixed` / `### Added` sections (feat-213's
entry first in Fixed, chronological), no entry dropped or reworded (see the
matching Decisions Made entry). The `plantuml-parser` job added by this
feature RAN on the PR and PASSED (4m15s; CI run 38998130206, job
117295101630, completed 2026-10-17T03:20Z): the SHA-256 verification step
answered `/home/runner/work/_temp/plantuml.jar: OK`, and the final pytest
line was `4693 passed, 4 skipped in 242.54s (0:04:02)` — the `-rs` short
summary lists exactly 4 skips, ALL URL-matrix tests (`tests/commands/
test_plantuml_encode.py:114`, `tests/plantuml/test_encode.py:187`,
`tests/plantuml/test_url.py:332`, `tests/plantuml/test_url.py:347`): ZERO
`require_plantuml_source` skip reasons. The 4693-passed count matches the
local jar-configured run count exactly, so the reference-graph subset gate
and the 22-golden parser sweep executed and passed under the job — the
commit-path evidence ACC-005 required. ACC-005 is therefore VERIFIED and
its checkbox marked `- [x]` (the canonical ACC line text is unchanged); all
six ACCs are now verified. Status stays `review`.

#### 2026-10-16T12:42:04.025Z - Phase 130 complete (quality gate, CLI walkthrough, closeout — status `review`)

**Task 130.100 (quality gate, ACC-006):** all four commands green —
`uv run --frozen ruff format --check` → `2062 files already formatted`;
`uv run --frozen ruff check` → `All checks passed!`; `uv run --frozen
vulture src/ whitelist.py --min-confidence 60` → no output (rc=0); `uv run
--frozen pytest -n auto --cov=src --cov-report=` → `4687 passed, 4 skipped`
(the 4 skips are the URL-matrix tests only — zero `require_plantuml_source`
skips with the jar configured).

**Task 130.110 (walkthrough, jar via the gitignored repo-root `.env` — the
ambient env var was verified UNSET in the shell, so every `checked_by=jar`
below proves the CLI's own dotenv load):**
- `uv run --frozen specmgr diagram refs feat feat-207-reference-graph
  --reverse --out /tmp/feat214-130/refs` → wrote
  `feat-207-reference-graph.refs.puml`: 16 label-free edges (15 outgoing +
  the incoming `[feat-214-rel-invalid-diag] --> [feat-207-reference-graph]`
  from the `--reverse` scan), 2 curly domain groups (`component "ADR" {`,
  `component "FEAT" {`), 2 top-level `<<UNRESOLVED>>` nodes (`feat-42`/
  `feat-43`), zero `: refers to` / zero `end package`.
- `uv run --frozen specmgr plantuml-check
  /tmp/feat214-130/refs/feat-207-reference-graph.refs.puml` →
  `checked_by=jar valid=true rendered=true source_state=ok` (rc=0) — the
  expected verdict.
- `uv run --frozen specmgr diagram refs all --out /tmp/feat214-130/all` →
  wrote `reference-graph.puml` (508 lines): 8 curly domain groups (ADR,
  REQ, TSK, QA, GOL, SOP, FEAT, SYSRS — the non-empty domains, in
  `ALL_DOMAINS` order), 306 label-free edges, zero old-form lines; the
  feat-214 node present with its outgoing edges. NOTE: this registry-wide
  build took 4m18s on this live registry (84 feat READMEs + full target-
  resolution over every reference) — the scoped `--reverse` build with the
  same 13-domain scan is seconds; one-off CLI cost, no action.
- `java -jar /home/user/plantuml.jar -tsvg all/reference-graph.puml -o svg`
  → rc=0, 332,146 B SVG (3408×9960 px). Eyeball greps: palette fills present
  (`#AFEEEE` FEAT, `#ADD8E6` REQ, `#8B0000` UNRESOLVED, `#FFFFE0` ADR — no
  UC/DEC nodes exist in this registry, so Pink/LightGreen are legitimately
  absent), 20 red `stroke:#F00` cycle-arrow segments, node titles present
  ("List Referenced Artifacts", "Use ISO 8601 for all dates and times",
  "Perform a release of biz.dfch.SpecMgr", "Reference-Graph Diagrams"),
  **zero** `refers to` occurrences in the SVG (the label-free render proof),
  zero crash markers. (PlantUML 1.2026.8 named the output
  `all/svg/Reference Graph.svg` after the diagram title and created the
  `-o` dir under the input file's dir — cosmetic, /tmp-only.)
- **Latent defect found + fixed here:** the first scoped run was missing the
  feat-214 incoming edge — the reference-graph builders' full-parse scan
  legs were silently SKIPPING this plan document because its Decisions Made
  section (introduced in Phase 100 as dated bullet lines of the form
  `- **<date> (Phase NNN) — <title>:**`) failed `parse_feat` (the
  `DecisionEntry` heading regex requires a date-prefixed H4, and the bullets
  matched nothing), while `list_feat` kept showing it healthy (the
  dirty-stage frontmatter+H1 parse — the ADR 3982712a time-qualification,
  which is exactly why the builder-level full parse is the authority). The
  section was reformatted to the packaged feat template's
  `#### <ISO8601> - <title>` H4-entry form (11 entries, bodies verbatim,
  newest first + a Phase 130 entry recording the fix); `parse_feat` now
  returns the full document, and the re-run scoped diagram carries the
  incoming edge. The document has therefore been unparseable in its
  committed state since f578e69 — worth a one-line mention for the review
  pass.

**Task 130.120 (closeout):** `CHANGELOG.md` gained the feat-214 entry under
`## [Unreleased]` (`### Fixed`: the parser-invalid layout → curly domain
groups + label-free edges with goldens/rulebook/docs regenerated; the
checker false-negative class → the tripwire rule. `### Added`: the golden
parser sweep + the `plantuml-parser` CI job with the pinned,
hash-verified 1.2026.8 jar; the skill's scoped-diagram reverse mandate with
the API defaults unchanged). ACCs marked verified: ACC-001/002/003/004/006
→ `- [x]`; ACC-005 stays `- [ ]` — it asserts the ACTUAL GitHub Actions run
of `plantuml-parser` (PASSED-not-skipped under the job), which exists only
after the branch is pushed; its local proxy evidence is green (Phase 120
record: YAML parses, sha256 line passes/FAILS correctly, the job's exact
pytest invocation 4687 passed / 4 skipped with zero `require_plantuml_source`
skips) and must be confirmed on the first CI run. Status changed to
`review` via the `set_status` MCP tool (`id=feat-214-rel-invalid-diag`,
`type=feat`) — the document was parseable again by then (the Task 130.110
fix), the tool bumped `updated` and left the body untouched.

#### 2026-10-16T06:15:43.752Z - Phase 120 complete (CI real-parser gate job, §4.3 CI-run amendment, gate docstrings)

**Task 120.100 (the CI job):** the new top-level `plantuml-parser` job was
added to `.github/workflows/ci.yml` (sibling of `build`, running on the same
push/PR triggers). Shape: single pinned Python 3.13.13 (mirroring the
`build` job's docs-drift pin — `setup-uv` + `uv sync --frozen --python
3.13.13 --all-extras`, same pinned action SHAs + `FORCE_JAVASCRIPT_ACTIONS_
TO_NODE24` + `permissions: contents: read` as `build`); a `Verify tools`
preflight (uv/python/`java -version` — the jar needs a JVM, preinstalled on
the GitHub-hosted ubuntu runners); `Download the pinned PlantUML 1.2026.8
release jar` (`curl -fSL --retry 3` from
`https://github.com/plantuml/plantuml/releases/download/v1.2026.8/plantuml-1.2026.8.jar`
to `$RUNNER_TEMP/plantuml.jar` — kept out of the repo, the planning-session
"jar by pinned download, not in git" decision); `Verify the jar's SHA-256
(fail on mismatch)` (the job's exact line: `echo
"5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462  $RUNNER_TEMP/plantuml.jar"
| sha256sum --check --strict` — hash-verified BEFORE any use, non-zero exit
fails the job under `bash -e`); and `Run the full suite with the real
parser configured` with `env: SPECMGR_PLANTUML_JAR: ${{ runner.temp }}/plantuml.jar`
running `uv run --frozen pytest -n auto -rs` (full suite, `-rs` so every
skip reason — incl. any residual `require_plantuml_source` skip — is visible
in the report; ACC-005 expects none).

**Task 120.110 (job green — local proxy evidence, since GitHub Actions
itself cannot run in this session):** (a) the edited workflow parses
(`yaml.safe_load`: jobs = `build`, `plantuml-parser`, 7 steps, the test
step's `env` = `SPECMGR_PLANTUML_JAR: ${{ runner.temp }}/plantuml.jar`);
(b) the job's exact sha256 line, run against the verified local copy of the
pinned jar, answers `OK` (rc=0), and the same line with a wrong hash
answers `FAILED` + `1 computed checksum did NOT match` (rc=1) — the
mismatch branch fails the job, not the suite; (c) the job's exact pytest
invocation, `SPECMGR_PLANTUML_JAR=/home/user/plantuml.jar uv run --frozen
pytest -n auto -rs`, reports **4687 passed, 4 skipped** — the `-rs` short
summary carries ONLY the URL-matrix skip reasons ("the live URL tests apply
only to a selected URL source" ×3, "the selected source is 'jar'; the live
render needs a URL base" ×1): ZERO `require_plantuml_source` skips — the
reference-graph subset gate (`TestReferenceGraphSubsetParserGate`) and the
golden parser sweep (`TestReferenceGraphGoldenParserSweep`) are in the
PASSED set (ACC-005). **The scoping branch was NOT needed** — no
pre-existing, unrelated failure surfaced; the full suite is green as-is, so
the job runs the full suite (no `tests/plantuml/`-only selection) and no
issue was recorded.

**Task 120.120 (docs):** rulebook §4.3 gained a dated amendment note
("§4.3 amended 2026-10-15 (feat-214-rel-invalid-diag Phase 120) — the gate
now RUNS in CI") naming the `plantuml-parser` job (pinned Python 3.13.13,
jar hash-verified before use, full suite with `-rs`, ACC-005's no-
`require_plantuml_source`-skip expectation), stating the 2026-10-10
"skipped — re-verify where a source is configured" outcome is
structurally impossible on the commit path, and documenting the local-dev
flow (gitignored repo-root `.env` loaded by `tests/conftest.py` at
collection — e.g. `SPECMGR_PLANTUML_JAR=/home/user/plantuml.jar` — running
the identical gates locally with zero repo changes; the gates remain
env-gated and skip cleanly off the commit path). The Phase 100 verdict
paragraph itself is preserved verbatim (its three fragments are the
resource drift pin's). The gate test's docstrings were updated to match:
the module docstring (the gates "on the commit path … RUN" via the named
job + the local `.env` flow), `TestReferenceGraphSubsetParserGate` (clean
local skips stay possible; on the commit path the gate RUNS, no
`require_plantuml_source` skip tolerated, ACC-005), and
`TestReferenceGraphGoldenParserSweep` (forward reference to the Phase 120
job turned present-tense). The resource drift pin was extended ADDITIVELY
(new `_PHASE_120_NOTE_FRAGMENTS` tuple + `test_pins_the_phase_120_ci_run_note`
method; the pre-existing `_GATE_VERDICT_FRAGMENTS` pins are untouched) —
all 11 resource tests + all 18 gate/subset tests green.

#### 2026-10-15T21:36:38.842Z - Phase 110 complete (skill reverse mandate, doc surfaces, REQ-008 confirmation)

**Task 110.100 (skill):** the `specmgr-refs` skill's diagram workflow
(`.opencode/skills/specmgr-refs/SKILL.md`) now mandates reverse for every
SCOPED diagram — the MCP bullet reads `get_reference_diagram(type, id,
depth=1, reverse=True, include_feat=True, title=None)` with "**Scoped
diagrams ALWAYS request `reverse=True`**" (the tool's own default stays
`False`, opt-in; only this agent flow opts in), the CLI bullet prescribes
`specmgr diagram refs <type> <id> [--depth N] --reverse …` with "**scoped
diagrams ALWAYS pass `--reverse`**" (the flag stays opt-in in the
signature); the step-4 report notes gained the cost bullet (the reverse
mandate makes the scoped build run the FULL 13-DOMAIN SCAN for the direct
incoming references — O(registry size), the same cost the separate reverse
workflow already states before running) and the edge note now reads "The
edges are LABEL-FREE (no text on the arrow — feat-214)" ahead of the
unchanged red-`-[#red]->`-on-cycle / plain-`-->`-off-cycle sentence. The
registry-wide surface is explicitly unchanged (its edges already run both
ways) and the frozen disambiguation rule is intact. The existing skill pin
test (`tests/opencode/test_skill_specmgr_refs.py`) gained a matching
`_REVERSE_MANDATE_PHRASES` tuple + one new test method (17 passed) — the
pre-existing pins (frontmatter, reporting vocabulary, delegation,
read-only, workflow headings/constants, pin g's routing row /
disambiguation / reconciliation / surface names / diagram facts) all stay
green.

**Task 110.110 (docs):** the emission-layout/edge-label wording was updated
to the new behaviour in every doc surface that carried it: the
`get_reference_diagram` module docstring + `@mcp.tool()` description (curly
component groups, label-free edges, red arrow label-free as well), the
`get_reference_diagram_all` module docstring + description (label-free
edges), the `general/tools` package docstring and the `server.py`
registration docstring (both carried a short "per-domain packages, one
edge per unique reference" summary — now "per-domain curly-brace component
groups, one label-free edge per unique reference"), the README "Reference
Graph Diagrams" how-to layout sentence, and the `AGENTS.md` `general/`
bullet's `get_reference_diagram` layout sentence. The `diagram_refs` CLI
docstrings needed no change (they describe the layout only via the
rulebook pointer, which Phase 100 corrected). `uv run --frozen specmgr
docs` + `specmgr mcp-docs` regenerated `docs/api/` (4 module pages) and
`docs/MCP.md`; a repo-wide sweep shows `: refers to` / "per-domain
packages" no longer appear in any doc surface (the only remaining
occurrences are the rulebook's own dated correction notes, the Phase 100
historical comments in `reference_graph.py`, and the checker-behaviour
tests that feed label-carrying edges as INPUT to the checker grammar — all
deliberate). The `reverse` parameter descriptions keep their existing
semantics (additive, direct-only on the incoming side) untouched.

**Task 110.120 (REQ-008 confirmation):** the `reverse=False` MCP
schema-default pin (`tests/general/tools/test_get_reference_diagram.py`,
`TestGetReferenceDiagramRegistration::test_get_reference_diagram_registered
_with_13_value_type_enum`: `schema["properties"]["reverse"].get("default")
== False`) and every explicit `reverse=True` builder/tool test
(`TestReverseRegistryTool` ×4, `TestReverseFeatSourceRegistryTool`,
`TestWideRegistryTool::test_scoped_reverse_golden`, plus the builder-level
reverse goldens in `tests/general/tools/test__reference_graph.py`) stay
green with NO signature change — an AST comparison of
`get_reference_diagram`, `get_reference_diagram_all`, `diagram_refs`,
`build_source_graph`, and `build_registry_graph` between HEAD and the
working tree reports every signature identical (all five `reverse`
defaults `False` in the tool/CLI layers; the `git diff` of the tool/CLI
files is docstring/description-only).

#### 2026-10-15T16:14:32.540Z - Phase 100 complete (design verification, tripwire, renderer, rulebook, goldens)

**Task 100.100 design verification (live registry, pinned jar — SHA-256 re-verified:
`5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462` matches the
plan's pin):** the four current real-registry emissions — `get_reference_diagram_all
(include_feat=False)` plus `get_reference_diagram(type, id, reverse=True)` over
`feat-207-reference-graph`, the sysrs aggregator, and one REQ source — all FAIL
the pinned PlantUML 1.2026.8 parser: `java -jar /home/user/plantuml.jar -tsvg -pipe`
answers exit 200 + `ERROR <line> — Syntax Error? (Assumed diagram type: component)`
on a component line inside the first braceless `package` block of each emission
(lines 65/32/23/30; the single-component `package "REQ"` block fails at its first
inner component line, exactly as the §2.9 worked example fails at line 25). The
mechanically-transformed emissions (curly `component "TYPE" { … }` domain groups +
label-free edges) all PASS: exit 0, empty stderr, real SVGs (8–115 KB) carrying the
palette fills (`#FFC0CB`/`#AFEEEE`/`#ADD8E6`/`#8B0000` in the §2.9 artifact), the
node titles, and the red `#F00` arrow strokes — no crash marker in any SVG. The
regenerated §2.9 worked example (old layout) reproduces the plan's recorded
`ERROR 25` failure verbatim; its transformed form renders exit 0. The
pre-existing env-gated parser gate, run against the then-old `_EMITTED_SUBSET`
before any code change, was already RED under the locally configured jar
(`valid=False`, `structure_ok=True`) — the false negative this feature closes,
now caught by the gate itself.

**Tasks 100.110–100.140:** the structure-checker tripwire is implemented in
`plantuml/structure.py` (a `package` fragment collecting component declarations —
a `component` keyword line or a short-form `[X]` line — must close with a `}`
line; a named `end package` close after a braceless-open or curly-open and an
unclosed such fragment at a block boundary are errors in BOTH modes with a
curly-brace fix hint; the recorded open shape is named in the diagnostic;
sequence `package` fragments stay untouched) with 9 control tests (the verified
parser-failing shapes fire; every UC + reference golden stays zero-finding — the
22 regenerated goldens pass the amended checker in both modes). The renderer
(`general/models/reference_graph.py`) emits the curly domain groups + label-free
edges (the `_EDGE_LABEL` constant removed; module + function docstrings updated).
The rulebook is amended with dated 2026-10-15 corrections (§2.1 shape, §2.7
rewritten, §2.8 label-free, §2.9 regenerated byte-exact, §4.3 verdict replaced —
old layout line-25 failure / new layout + label-free pass / the "an emission
layout is NOT frozen on a skipped gate" convention — and §7.1 tripwire amendment +
checker-contract restatement); the UC rulebook §6.1 carries the matching dated
note. All 22 goldens under `tests/fixtures/reference-graphs/goldens/` are
regenerated (143 line-level layout changes, nothing else), `_EMITTED_SUBSET` is
the new §2.9 verbatim, the gate's render proof changed from "refers to" to a node
title, and the new env-gated golden parser sweep (all 22 goldens through
`chain.validate_plantuml` → `valid=True` + `rendered=True` + node-title render
proof) PASSES — 18 passed, 0 skipped — under the configured jar, as do the
full plantuml/ + uc/ + reference-graph test selections (530 passed, 3 skipped —
URL-source-only tests, by design).

#### 2026-10-15T09:35:56.438Z - Created

Feature created from GitHub issue #214 ("Relationship diagram creates invalid plantuml"). The planning session verified the diagnosis against the real PlantUML 1.2026.8 parser (the braceless `package` grouping fails at line 25 of the §2.9 worked example; the `component "TYPE" { … }` grouping with label-free edges passes) and recorded the design decisions: the curly-brace component grouping (the issue's own diagnosis), label-free edges (a planning-session addition — the `: refers to` label was never intentionally approved), reverse-ref display via the `specmgr-refs` skill workflow (API default stays OFF), the checker kept + a verified tripwire rule, and a new CI job that downloads the pinned PlantUML 1.2026.8 jar (URL + SHA-256) so the previously-skipped real-parser gate actually runs and every frozen golden is parser-verified.

### Decisions Made

<!-- Newest entry first — prepend new entries directly below this comment. -->

#### 2026-10-17T04:06:08.272Z - PR #216 dev-merge: CHANGELOG `[Unreleased]` conflict resolved by consolidation

The only merge conflict when resolving PR #216 against `dev` was
`CHANGELOG.md`'s `## [Unreleased]` section (feat-213 had landed its own
`[Unreleased]` entry in the meantime). Resolution: both sides' entries were
consolidated into single `### Fixed` / `### Added` subsections (feat-213's
entry first in `### Fixed`, chronological), with no entry dropped or
reworded — both features' changelog records survive verbatim in the merged
file.

#### 2026-10-16T09:36:54.589Z - Phase 130: Decisions Made reformatted to the feat schema's H4 date-entry form

The bullet form this section first carried (`- **<date> (Phase NNN) — <title>:** <body>`) FAILED the feat document's full parse (`parse_feat` error at `Feature > Progress > DecisionsMade > DecisionEntry`: each entry must be an H4 heading matching `^<ISO8601-ms>Z - <title>`, per the packaged feat template) — the defect shipped with the Phase 100 progress update and was only surfaced by the Task 130.110 walkthrough: `list_feat` kept showing feat-214 transiently healthy (the dirty-stage frontmatter+H1 parse, the ADR 3982712a time-qualification), while the reference-graph builders' full-parse scan legs SKIPPED the document — dropping feat-214 from every live diagram (the missing `--reverse` incoming edge to `feat-207-reference-graph`) and would have blocked the closeout's `set_status`. All eleven pre-existing entries were reformatted to the template's `#### <ISO8601> - <title>` form (newest first, bodies verbatim); the section now parses.

#### 2026-10-16T06:15:43.752Z - Phase 120: resource drift pin extended additively

The new §4.3 Phase 120 note is pinned by a NEW `_PHASE_120_NOTE_FRAGMENTS` tuple + `test_pins_the_phase_120_ci_run_note` method in `tests/general/resources/test_reference_graph.py` (the pre-existing `_GATE_VERDICT_FRAGMENTS` pins are untouched and stay green) — the same additive precedent as Phase 110's skill pin extension; a silent removal of the CI-run note now breaks the suite.

#### 2026-10-16T06:15:43.752Z - Phase 120: `java` reliance

The job does NOT install a JDK: the GitHub-hosted ubuntu runners ship Temurin Java preinstalled on PATH, so the jar runs as-is; the `Verify tools` preflight prints `java -version` and fails the job early (with an unmistakable message) if that assumption ever changes.

#### 2026-10-16T06:15:43.752Z - Phase 120: Python pin 3.13.13

"mirroring the docs-drift pin" is taken literally at the PATCH level: `setup-uv`'s `python-version` and `uv sync`/`pytest`'s `--python` are all pinned to `3.13.13` (the exact interpreter the `build` job's docs-drift steps force), not just "3.13" — a single, fully determined Python per the plan's "single pinned Python (3.13)" wording.

#### 2026-10-16T06:15:43.752Z - Phase 120: job name + download location

The new job is named `plantuml-parser` (descriptive: it is the parser-authority half of CI, complementing `build`'s lint/test/docs-drift role) and is a top-level sibling of `build` (independent, parallel — no `needs:`; it re-runs the full suite by design, because its whole purpose is the suite under a real parser). The jar downloads to `$RUNNER_TEMP/plantuml.jar` (the runner's temp dir — keeps the ~28.5 MB binary out of the checkout; the test step references it via the `${{ runner.temp }}` context in `env:`).

#### 2026-10-15T21:36:38.842Z - Phase 110: REQ-008 evidence method

Signature invariance is proven by an AST comparison of `get_reference_diagram` / `get_reference_diagram_all` / `diagram_refs` / `build_source_graph` / `build_registry_graph` between HEAD and the working tree (all identical; every `reverse` default `False` in the tool/CLI layers), in addition to the green `reverse=False` MCP schema-default pin and the explicit `reverse=True` tests.

#### 2026-10-15T21:36:38.842Z - Phase 110: skill pin extension is additive

The new mandate/cost/label-free wording is pinned by a NEW `_REVERSE_MANDATE_PHRASES` tuple + one new test method in `tests/opencode/test_skill_specmgr_refs.py`; the pre-existing pin-g tuples (feat-207's load-bearing diagram facts) are untouched, so the feat-207 wording pins stay as historical regression anchors. The skill's label-free note is phrased "no text on the arrow" (not the literal old label string) so no stale emission wording survives on the skill surface.

#### 2026-10-15T21:36:38.842Z - Phase 110: doc-surface scope

The task named the two tool modules' docstrings/descriptions, the README, and `AGENTS.md`; a sweep found TWO more surfaces carrying the short "per-domain packages, one edge per unique reference" layout summary — the `general/tools` package docstring and the `server.py` registration docstring (the authoritative per AGENTS.md). Both were updated (REQ-010's "every documentation surface describing the emission layout" clause); the `diagram_refs` CLI docstrings were judged to need NO change (they describe the layout only via the rulebook pointer, which Phase 100 corrected).

#### 2026-10-15T16:14:32.540Z - Phase 100: vacuous old-form pins updated in the ripple files

`test_get_reference_diagram_all.py` and `test_diagram_refs.py`'s FEAT-exclusion pins (`assertNotIn('package "FEAT"')`) and no-edge pins (`assertNotIn(": refers to")`) became vacuous under the new layout (no emission contains the old forms any more) and were re-pointed at the new-form equivalents (`assertNotIn('component "FEAT"')`, `assertNotIn("-->")`) to stay meaningful; every POSITIVE old-layout pin in the builder/tool tests was updated to the label-free/curly-group form (the minimal change keeping the suite green — the tool/CLI docstrings themselves still describe the old layout by design and are Phase 110's).

#### 2026-10-15T16:14:32.540Z - Phase 100: render-proof string derivation

The node-title proof for the gate + the golden sweep is the LONGEST ALL-ALPHA word of the FIRST resolved node's label (`#quot;` escapes undone; unresolved `<<UNRESOLVED>>` verbatim-id lines skipped). PlantUML wraps long labels across SVG lines at word boundaries only, so one word is guaranteed present contiguously in the SVG body — verified for all 22 goldens under the jar.

#### 2026-10-15T16:14:32.540Z - Phase 100: tripwire diagnostic names the recorded open shape

The plan's Design Notes record the open shape (`{` or not) on the fragment stack; vulture flagged the field as unread, so the named-close error now names it in the message (`opened at line N, braceless` / `opened at line N, curly-open`) — the diagnostic is richer and the recording is pinned by the control tests.

#### 2026-10-15T16:14:32.540Z - Phase 100: golden regeneration mechanism

The 22 goldens were regenerated by a throwaway `/tmp` script that re-ran the EXACT committed test scenarios (each `tests/general/tools/test__reference_graph.py` seeded-registry test class's `SEEDS` + the same builder call; the hand-built renderer graphs from `tests/general/models/test_reference_graph.py`) against the updated renderer/builders — the repo has no committed generator (the feat-207 precedent regenerated out-of-band and byte-pins via the tests), so the generator deliberately stayed outside the tree (in `/tmp/feat214-100/`). The resulting git diff is 143 pure line-level layout changes across the 22 files.

### More Information

**Reproduction (verified 2026-10-15, PlantUML 1.2026.8 / 149874a, GPL source build, Java):**

The current frozen layout (the rulebook §2.9 worked example — what every scoped/registry-wide diagram emits today) fails the real parser:

```text
$ java -jar plantuml.jar -pipe   # the §2.9 subset piped on stdin
ERROR
25
Syntax Error? (Assumed diagram type: component)
```

Line 25 is the first `component` declaration inside the braceless `package "REQ"` block. Isolation matrix (all variants tested against 1.2026.8):

| Variant | Result |
| --- | --- |
| `package "REQ"` / `component Foo` / `end package` (any inner form: bare, quoted, with/without alias, short `[Foo]`) | Syntax error on the inner component line |
| `package REQ {` / `component Foo` / `}` (curly open AND close) | OK |
| `package "REQ" {` … `end package` (mixed close) | Syntax error |
| `component "REQ" { component "A" as [REQ-uuid] <<REQ>> }` (THE FIX) | OK |
| Full §2.9 subset with `component "TYPE" { … }` groups (skinparam palette, bracketed aliases, `-[#red]->` cycle edges, top-level unresolved node) | OK — renders; the SVG carries the palette fills (Pink `#FFC0CB`, PaleTurquoise `#AFEEEE`, LightBlue `#ADD8E6`, DarkRed `#8B0000`) and the red arrow `#F00` |
| Same, with `: refers to` removed from every edge line (label-free) | OK — parser exit 0 AND structure checker zero findings in both modes |

The structure checker reports zero findings in BOTH modes over the OLD layout (the gap that let it ship: the Phase 100 real-parser gate skipped — no `SPECMGR_PLANTUML_*` source configured — and the checker is a line-oriented subset linter, not a parser).

**Jar pin (the CI job's source + the local dev `.env` value):**

- URL (immutable per tag): `https://github.com/plantuml/plantuml/releases/download/v1.2026.8/plantuml-1.2026.8.jar`
- SHA-256 (verified 1.2026.8/149874a build): `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462`
- Size: ~28.5 MB (29,871,497 bytes) — deliberately NOT committed to the repository
- Local dev: gitignored repo-root `.env` → `SPECMGR_PLANTUML_JAR=/home/user/plantuml.jar` (this machine already carries the verified build)
