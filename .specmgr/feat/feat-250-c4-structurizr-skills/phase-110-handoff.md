# Phase 110 execution handoff (feat-250, prepared 2026-11-03)

This file is a local working note for the agent executing **Phase 110: Skill
`structurizr-validate-loop`** (tasks 110.100–110.150). The authoritative plan,
requirements, acceptance criteria and stop rule are in `README.md` (same
folder). All design decisions below were made with the user in the 2026-11-03
planning session; they are locked. Record them in the README's Decisions Made
when implementing.

## Starting state (verified 2026-11-03)

- `dev` branch, clean tree. Phase 100 (harness) is complete and committed;
  feat status is `review` (set it to `progress` via the generic `set_status`
  tool, `type="feat"`, when you start).
- Harness: `evals/c4-skills/` (stdlib only). Entry:
  `uv run --frozen python evals/c4-skills/run.py <preflight|probe|run|report>`.
  Only case known: `smoke-create-system`. Only gates known: the 8 pure
  CLI/export gates in `c4_skills/graders.py` (`dsl_written`, `cli_valid`,
  `cli_export`, `has_system`, `has_person`, `two_containers`,
  `relationship_technology`, `has_view`).
- `skill` condition works (review-cycle I5): `run --conditions none,skill
  --skills-dir <path>`; the variant is content-hashed (`run.json →
  skill_variant_hash`) and copied into each trial work dir at
  `.opencode/skills/<name>/` before the container starts; skill trials are
  never cached; `none`/`upstream` are cached per (case, condition, version
  tuple, grader hash, skill variant hash).
- Runtime ready: Docker 29.1.3; pinned images present at pinned digests
  (`ghcr.io/anomalyco/opencode:2.2.5`, `structurizr/mcp:2026.04.20`,
  `structurizr/structurizr:2026.10.26-noble`); vLLM 0.26.0 serving
  `qwen3.8-27b-bf16-896k` at `127.0.0.1:8081` (max_model_len 917504);
  upstream checkout cached (`evals/c4-skills/cache/upstream/`); no stale
  `c4eval-*` containers. The runner idle-waits on the shared vLLM.
- Version tuple hash `0de1ba98…95a7b4`; the `none` skill-variant hash
  (empty set) is `4f53cda1…61202b945`.
- Provenance: all three adaptation sources confirmed MIT, table committed at
  `evals/c4-skills/results/provenance.md`. For this phase:
  `passionsplay/structurizr-skill` @ `5e45154e1c266e0517d456855b415ba770412f16`
  ("Copyright (c) 2026 Benjamin Turner").

## Task 110.100 — cases + graders (harness code, no model)

### Cases (add to `c4_skills/cases/__init__.py` `CASES`; held-out id constant
in `pins.py` per the `SMOKE_CASE` precedent; `FULL_CASES` already carries
`create-system`, `mcp-limits`, `no-trigger`)

Prompt drafts (lock these in code; the create-system prompt is the Phase 100
smoke prompt verbatim — it deliberately mentions only `validate`, never
parse/inspect, because that discipline is what the skill injects):

- `create-system` (bookshop; prompt = smoke prompt in `cases/__init__.py`,
  unchanged).
- `mcp-limits`: multi-file bookshop request that forces the MCP limits:
  "The team's convention is a multi-file workspace: separate files pulled
  together with `!include`, plus a `!docs` documentation folder with a
  Markdown page. Set that up in the current working directory, then check
  the result with the structurizr MCP tools before you finish." (The MCP
  refuses both `!include` and `!docs`; the CLI would accept them — so the
  discriminating fact is the MCP `OK` byte-identity, not the CLI.)
- `no-trigger`: **seeded** valid `workspace.dsl` via `setup_files` (base it
  on the `tests/evals/fixtures/workspaces/good/workspace.dsl` shape; verify
  it validates with the pinned CLI image before committing) + prompt asking
  for a capability **none of the five skills owns** (locked): "The C4 model
  is in `workspace.dsl` in the current directory. Render it to image files:
  one PNG (or SVG) per view, written into the current directory. Tell me
  when the images are ready." This shape stays valid in Phases 120–150
  (a review- or view-flavored prompt would trigger the *correct* skill in
  Phase 150/140 and fail the case there).
- `heldout-validate`: same task shape as create-system, different domain
  (hospital appointment system: a Patient person, an Appointment System, a
  Booking Web App + Scheduling Service container, relationships with
  technology, a system context view; same "check with validate before you
  finish" tail).

### Gate sets (locked)

- `create-system` and `heldout-validate`:
  `(dsl_written, cli_valid, cli_export, has_system, has_person,
  two_containers, relationship_technology, has_view, parse_called,
  validate_ok_called, inspect_called, validated_before_return,
  triage_complete)`
- `mcp-limits`: the same 13 + `limits_acknowledged` (14).
- `no-trigger`: `(no_mounted_skill_loaded, file_untouched, cli_valid,
  mcp_limit_stated)`

New stream-derived gates (all additive; the 8 existing gates keep their
behavior):

- `validated_before_return` — on-disk DSL (or final-DSL) byte-identical to
  the exact text that got `OK` (`events.VALIDATE_OK_MARKER`) from a
  `validate`-suffixed MCP call. Expose the ok-texts set from `metrics.py`
  (currently private `_validated_texts`) for reuse.
- `parse_called` / `validate_ok_called` / `inspect_called` — ≥1 completed
  call (`ParsedTrial.calls_named`).
- `triage_complete` — every merged finding in
  `metrics.inspect_triage` labeled fix/expected/reported (no `untriaged`);
  vacuously true with no findings (`inspect_called` carries the
  requirement).
- `limits_acknowledged` — final text names the refused features
  (`!include` and/or `!docs`); keep the matcher loose, unit-test it on a
  synthetic stream.
- `no_mounted_skill_loaded` — `metrics.skills_loaded ∩ skills_installed`
  is empty (see runner change below).
- `file_untouched` — the DSL file's text equals the case's `setup_files`
  text (compare via the case the gate already receives; no GraderInputs
  change needed).
- `mcp_limit_stated` — final text states that images cannot be produced
  (the MCP has no image rendering; export tools emit PlantUML/C4-PlantUML/
  Mermaid *source*). Offering diagram source in addition must still pass.

### Grader plumbing (the one structural change)

`grade_case(case, inputs)` today receives CLI/work-dir facts only; the new
gates need stream facts. Extend additively: a `GateContext` (or pass both)
carrying `GraderInputs` + `Case` + `ParsedTrial` + `TrialMetrics` (and
`skills_installed`), registry `GATES: name -> gate(ctx)`, old 8 gates
wrapped over `ctx.inputs`. `runner.run_trial` already computes
`compute_metrics(...)` before `grade_case(...)` — wire them together.
Update `tests/evals/test_graders.py` to the new signature.

`runner.py`: capture the return of `_install_skills(...)` (the installed
skill names; `[]` for `none`) into an **additive** `TrialRecord` field
`skills_installed: list[str] = field(default_factory=list)` (old committed
records parse via the default, like the other additive fields).

### Unit tests (ACC-006: no model, no Docker)

New synthetic event-stream fixture(s) under `tests/evals/fixtures/events/`
modeled on `probe-hello.ndjson` (the pinned real schema) +
`tool-stream.ndjson`: a validate call answering `OK` with a `dsl` input, an
inspect call with findings, a skill tool call, post-inspect edit calls, a
final text part. One pass/fail/edge test per new gate. Then: `ruff format
--check && ruff check`, vulture, full pytest green.

## Task 110.110 — prove the graders against `none` (20 model trials)

```bash
uv run --frozen python evals/c4-skills/run.py run \
  --cases create-system,mcp-limits,no-trigger,heldout-validate \
  --conditions none --k 5 --seed <pick+record> --comparison none --label p110-prove
```

- Commit the results dir. **`--comparison none` is mandatory** (the CLI
  default is `upstream`).
- ACC-013 check per case: `none` must be strictly between 0/5 and 5/5 (the
  "≥1 condition passes ≥1" half is confirmed by `skill` in 110.130).
- Locked decision: the held-out case's `none` baseline IS measured here
  (no skill variant exists yet, so nothing is tuned with it); the final
  110.140 run then costs only 5 fresh skill trials.
- If a case does not discriminate, harden gate/prompt and re-prove (the
  grader-hash change invalidates that case's cache by design).

## Task 110.120 — skill v1 (no model)

Layout (all markdown, REQ-007 — the harness bundle only carries `*.md`):

```
.opencode/skill/structurizr-validate-loop/
├── SKILL.md                          # thin; frontmatter EXACTLY {name, description}
├── references/validate-vs-inspect.md # adapted from passionsplay @5e45154e
├── references/dsl-gotchas.md         # adapted (declaration order, quoting,
│                                     #   relationship description+technology,
│                                     #   flat identifiers)
├── NOTICE.md                         # MIT text + "Copyright (c) 2026 Benjamin Turner"
│                                     #   + which files adapt which source files
└── source-map.md                     # passage -> source file @ commit (REQ-010)
```

- `name` == folder name; third-person trigger `description` naming the one
  task (the validate/inspect loop over Structurizr MCP tools) + trigger
  phrases (e.g. "validate a Structurizr workspace", "check the DSL",
  "inspect findings", "is my model valid").
- SKILL.md body: the mandatory loop — parse → fix → validate until `OK` →
  inspect → triage EVERY finding (fix / expected under the MCP / reported
  in the final answer) → return the exact text that last got `OK`; any edit
  after the final validate requires re-validating (a parsed-only or
  reported-only result is NOT a pass — ADR 7a626b12 precedent). Tool names
  referenced prefix-agnostically (the host prefixes them, e.g.
  `structurizr_validate`; the in-harness server name is `structurizr`).
- REQ-006 limits stated in full: MCP works on DSL text only (single file);
  refuses `!include` and `!docs`/`!adrs` ("feature … is not enabled");
  cannot render images (export tools emit PlantUML/C4-PlantUML/Mermaid
  source). REQ-011: when the Structurizr MCP tools are absent, validation is
  not possible and the agent must never describe a DSL result as validated.
- Adaptation rule: the source's `!docs`/`!adrs` "fix" advice is INVERTED to
  "expected under the MCP, do not use them, report as expected"; drop all
  Docker-CLI advice, `scripts/structurizr.sh`, Claude-specific setup.
- The passionsplay source files (fetched at the pinned commit, not
  vendored): `skills/structurizr/references/validate-vs-inspect.md` (the
  table), `skills/structurizr/SKILL.md` (loop workflow),
  `skills/structurizr/references/dsl-best-practices.md` (gotchas),
  `skills/structurizr/references/mcp.md` (MCP facts). Spike input: TXT
  `4a09922d-bc32-4c03-86ba-d30ebc34e0b8` (findings 2, 3, 8: validate vs
  inspect, MCP sandbox, limits).
- If iteration replaces adapted text, drop that passage's attribution (the
  notice + source map must stay consistent, ACC-010).

## Task 110.130 — measure + iterate (≤3 variants)

```bash
uv run --frozen python evals/c4-skills/run.py run \
  --cases create-system,mcp-limits,no-trigger \
  --conditions none,skill --k 5 --seed <pick+record> --comparison none \
  --skills-dir .opencode/skill/structurizr-validate-loop --label p110-iterN
```

- `none` hits the cache from the prove run; only the 15 skill trials are
  fresh. Each variant is recorded by its content hash
  (`run.json → skill_variant_hash`).
- Stop rule = `report.json → skill_margins.margin.ok`: skill pass rate not
  more than 10 pp below the comparison (`none`), no case clearly worse
  (≥2 fewer passes out of 5), and not worse than `none` (with
  comparison=none the binding constraint is skill rate ≥ none rate).
  Wilson/pass^k are information only.
- The per-gate failure breakdown (`report.json → per_condition.*.
  gate_failures`) gives ACC-012's "better on which gates" story — expect
  the gains on `parse_called`/`inspect_called`/`triage_complete`/
  `validated_before_return`.
- If the stop rule fails after 3 iterations: phase fails, revise the plan
  before Phase 120 (per the stop rule). If gates are missed but a variant
  beats `none`: may be accepted with a recorded caveat.

## Task 110.140 — held-out once

```bash
uv run --frozen python evals/c4-skills/run.py run --cases heldout-validate \
  --conditions none,skill --k 5 --seed <pick+record> --comparison none \
  --skills-dir .opencode/skill/structurizr-validate-loop --label p110-heldout
```

- `none` cached from the prove run; 5 fresh skill trials. The result never
  selects a variant. Hybrid rule: 0/5 passing or below `none` → phase
  "accepted with caveat" (rechecked in Phase 160, stated in the results).

## Task 110.150 — attribution, pinning test, bundle, bookkeeping

- ACC-010: every adapted passage has its notice next to the skill; the
  source map matches the notice; adapted text exists ⇒ `NOTICE.md` exists.
- `tests/opencode/test_skill_structurizr_validate_loop.py` following the
  pattern of `tests/opencode/test_skill_uc_diagram.py`: file location
  (singular `.opencode/skill/` dir), frontmatter exactly `{name,
  description}`, `name` == folder, description trigger keywords, the loop
  wording (validate-until-OK, inspect, triage labels fix/expected/reported,
  re-validate-after-edit / exact-text rule), the three REQ-006 limit
  statements, the REQ-011 no-MCP wording, and `NOTICE.md` + `source-map.md`
  presence.
- Regenerate: `uv run --frozen specmgr docs` (GENERATED.md test-file count
  moves), `uv run --frozen specmgr harness-bundle` (once the stop rule has
  passed; the pre-commit hook also regenerates it on commit).
- feat README: tick tasks 110.100–110.150; Updates entry (run ids, seeds,
  variant content hashes, iteration count, stop-rule verdict, held-out
  result, per-gate wins, cost vs the Phase 100 estimate); Current Status;
  Decisions Made (the locked decisions in this file: no-trigger shape,
  `parse_called` hard gate, prove-run scope, the gate set, NOTICE.md
  naming).
- Quality gates before each commit: `uv run --frozen ruff format --check &&
  uv run --frozen ruff check`, vulture, full pytest, `specmgr lint`
  (pre-commit enforces; the pytest hook covers `src|tests|evals` `*.py`).

## Commit strategy (the plan mandates committed results, ACC-007)

Logical commits at task boundaries: (1) harness: cases + graders + tests;
(2) prove-run results; (3) skill files (SKILL.md + references + NOTICE.md +
source-map.md); (4) iteration run results (per variant if >1); (5) held-out
results; (6) pinning test + `specmgr docs` + harness bundle + README
progress. Never commit `evals/c4-skills/work/`, `cache/` or `.upstream/`
(gitignored).

## Cost / risks

- ≈40 fresh model trials for one iteration (20 prove + 15 skill + 5
  held-out), up to ≈55 for three iterations; ~1–2.5 h wall at the
  Phase-100 healthy-window median (83–180 s/trial), plus shared-server
  idle waits. Within the 30 h full-run budget.
- Degraded vLLM windows produce 1200 s timeouts: flagged failures, not
  re-scored. If a skewed `none` baseline materially affects a margin,
  remove the affected cache entry and re-run that baseline in a healthy
  window (Phase 100 precedent: the canonical smoke run), and disclose it in
  the README Updates entry.
- The runner aborts (exit 1) if vLLM is still busy after 1 h of waiting —
  just resume later; completed trials are cached.
- `no-trigger` in later phases: the gate is uniform ("no *mounted* skill
  loaded"), so a later phase fails this case only if its own skill's
  description triggers on a render-to-image request — a REQ-007
  single-task description problem for that phase.
