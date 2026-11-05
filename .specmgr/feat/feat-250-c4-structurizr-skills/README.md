---
classification: null
created: '2026-11-01T14:10:53.141+01:00'
id: feat-250-c4-structurizr-skills
status: progress
type: feat
updated: '2026-11-05T23:17:03.000+01:00'
version: 1.0.0
---

# Feature: Agent Skills for C4 Modeling with Structurizr

## Plan

### Overview

Agents need guidance to build C4 architecture models with Structurizr DSL. This feature adds five generic OpenCode skills under `.opencode/skill/`: C4 concepts, DSL authoring, a mandatory validate loop over the Structurizr MCP's `parse`, `validate` and `inspect` tools, view design, and model review. The skills are bound to the Structurizr MCP tools and say what to do when that MCP is not present. They build on the spike findings in TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8.

The skills are not written from scratch where good MIT-licensed sources exist. They are adapted from those sources and then measured. A reproducible container harness runs an OpenCode agent with and without the skills against a local model, and each skill is iterated in its own phase until it meets its stop rule.

### Requirements

- REQ-001: A `c4-modeling` skill explains the C4 levels, what counts as a container, naming and description rules, and the common modeling mistakes.
- REQ-002: A `structurizr-dsl-authoring` skill covers the Structurizr DSL syntax and its known gotchas.
- REQ-003: A `structurizr-validate-loop` skill requires every DSL result to pass the MCP's `parse` and `validate` tools before it is returned, and to be checked with `inspect`. "Checked" means that each `inspect` finding is triaged as fix, expected under the MCP limits of REQ-006 (for example no documentation and no decisions, which need `!docs` and `!adrs`), or reported to the user. A finding that cannot be cleared under the MCP never blocks the result.
- REQ-004: A `c4-view-design` skill explains which views to create and how to keep each view readable (about 20 elements per view, explicit view keys, the C4-PlantUML export gotchas of the spike as a short reference note).
- REQ-005: A `c4-model-review` skill gives a read-only quality checklist for an existing model and reports findings without editing.
- REQ-006: Every skill that depends on the MCP states its limits, at least that the MCP works on DSL text only, refuses `!include` and `!docs`, and cannot render images. `structurizr-dsl-authoring` and `structurizr-validate-loop` state all of them, and `c4-view-design` and `c4-model-review` state the ones they depend on.
- REQ-007: Each skill has a trigger `description` that names its one task and the phrases that should load it, and the long reference material sits in files next to a thin `SKILL.md`. Every file next to a `SKILL.md`, including reference files and license notices, is markdown, so that the harness bundle carries it.
- REQ-008: The effectiveness of the skills is measured with a reproducible harness that runs OpenCode in an isolated container against the model `qwen3.8-27b-bf16-896k` on sys0, one trial at a time. Reproducible means that all versions, the sampling parameters and the random-order seed are recorded.
- REQ-009: Each skill is built in its own phase and measured against its comparison condition. The phase ends under a fixed stop rule: not worse than the comparison condition within a stated margin, not worse than `none`, at most 3 iterations, and one held-out case that runs only at the end.
- REQ-010: Text adapted from an external source keeps that source's license notice next to the skill. A skill that is fully rewritten carries no attribution.
- REQ-011: When the Structurizr MCP tools are not available in the host, each skill says that validation is not possible and the agent must not describe a DSL result as validated.

### Acceptance Criteria

- [ ] ACC-001: The five skills exist under `.opencode/skill/` and each `SKILL.md` has a `name` equal to its folder name and a trigger `description`.
- [ ] ACC-002: `structurizr-validate-loop` forbids returning DSL that has not passed `validate`, requires `parse` and `inspect`, and defines the triage of `inspect` findings.
- [ ] ACC-003: The MCP limits of REQ-006 are stated in every skill that depends on them, and in full in `structurizr-dsl-authoring` and `structurizr-validate-loop`.
- [ ] ACC-004: `c4-model-review` does not edit any file or model.
- [ ] ACC-005: `specmgr harness-bundle` is regenerated at the end of every skill phase whose stop rule has passed, the bundle contains every markdown file next to each `SKILL.md`, and the harness-bundle drift check passes.
- [ ] ACC-006: The harness graders split a known-good from a known-bad workspace, proven by unit tests that need no model call. The tests use pre-exported JSON fixtures, and tests that need the Structurizr CLI are skipped when Docker is missing.
- [ ] ACC-007: The results for the conditions `none`, `upstream` and `skill` are committed under `evals/c4-skills/results/`, with the recorded versions of OpenCode, Structurizr, the MCP, the model, the upstream commit SHA and the skill variants.
- [ ] ACC-008: On the full case set, `skill` is not worse than its comparison condition: the pass rate over the phase's cases is not more than 10 percentage points lower, and no single case is clearly worse (a difference of 2 or more trials out of 5). Wilson intervals are reported but do not gate.
- [ ] ACC-009: Each skill phase records its iterations and the result of its held-out case. A clear held-out failure (0 of 5 trials passing, or below `none`) marks the phase "accepted with caveat".
- [ ] ACC-010: Every adapted passage has its license notice next to the skill, a per-skill source map (passage to source) matches the notice, and no skill without adapted text carries a notice.
- [ ] ACC-011: Each skill has a test `tests/opencode/test_skill_<name>.py` that pins the `name`, the description keywords, the MCP-limit wording, the read-only wording of `c4-model-review` and the presence of the notice files.
- [ ] ACC-012: Each skill is not worse than `none` on its own cases (pass rate not lower), and the results state for which gates it is better.
- [ ] ACC-013: Each case discriminates: `none` does not pass all 5 trials, and at least one condition passes at least one trial. A case that does not is hardened or replaced before the skill is written.
- [ ] ACC-014: The final phase checks ACC-001 to ACC-014 in a traceability list.

### Scope

#### Included

- The five skills `c4-modeling`, `structurizr-dsl-authoring`, `structurizr-validate-loop`, `c4-view-design` and `c4-model-review`.
- Reference files next to each `SKILL.md`, where needed, all in markdown.
- The measurement harness under `evals/c4-skills/` (Python, standard library only), its unit tests under `tests/evals/`, the cases and the committed results.
- The skill pinning tests under `tests/opencode/`.
- Regeneration of the packaged harness bundle at the end of each skill phase that passed its stop rule.
- The repository housekeeping that a new top-level `evals/` directory needs (`.gitignore`, lint and test treatment, `AGENTS.md`, `CHANGELOG.md`, `NOTICE`).

#### Explicitly Out Of Scope

- The C4-based Architecture Description (ARC) artifact (issue 228).
- A `/c4-*` command or a dedicated subagent.
- Links from models to specmgr artifacts (REQ, DEC, ADR).
- Workflow skills (elicitation, reverse engineering, model evolution, export) and specialised skills (deployment, dynamic views, styling, multi-workspace).
- Automatic generation of DSL from specmgr artifacts.
- Shipping the harness: it is development-only and is not part of the harness bundle or the wheel.
- Other models, thinking variants and parallel trials. They can be added later as further axes.

### Dependencies

#### Depends On

- The `structurizr` MCP server (`structurizr_parse`, `structurizr_validate`, `structurizr_inspect` and the export tools). The tool name prefix depends on the MCP server name in the host configuration.
- The vLLM server on sys0 that serves `qwen3.8-27b-bf16-896k` (MTP, 5 speculative tokens, `--max-num-seqs 2`).
- Docker, the `ghcr.io/anomalyco/opencode` image and the `structurizr/structurizr` and `structurizr/mcp` images.

#### Blocks

- Later workflow and specialised C4 skills.

### Design Notes

Keep each `SKILL.md` thin. A trigger description names exactly one task and lists the phrases that should load the skill, and a skill must not trigger on a request that only names another skill's task (the `no-trigger` case measures this). Keep the skills separate: `c4-modeling` and `structurizr-validate-loop` are loaded almost every time, the others only when needed. See TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8 for the MCP and PlantUML findings. ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4 sets the precedent that a structure-only PlantUML check is not a pass, and the skills apply the same rule: a DSL result that was only parsed, and not validated, is not a pass.

#### Sources and Licensing

- Adapted, MIT: `jrjsmrtn/c4-skills` (`c4-model`, `structurizr-dsl`, `c4-review`), `passionsplay/structurizr-skill` (the validate-versus-inspect table and the DSL gotchas, adapted in `structurizr-validate-loop`) and the Structurizr documentation (`structurizr/structurizr.github.io`, adapted in `structurizr-dsl-authoring`). The license of each source is verified in Task 100.190 before any text is adapted. A source whose license cannot be confirmed moves to "ideas only".
- Concepts only, CC BY 4.0: c4model.com. Attribute it where text is reused.
- Ideas only, never copied, because the repositories carry no license: `allensanborn/skills`, `bitsmuggler/c4-skill` and `fedemagnani/structurizr-dsl`.
- Remove everything specific to Elixir, OTP, Phoenix and Ash, all Docker-CLI validation steps, and any advice to use `!docs`, `!adrs` or `!include`, because the MCP refuses them.
- Provenance: a table in the results records, for each adapted source, the commit, the license file, the license type and the check date. Each skill has a source map (passage to source) that the pinning test compares with the notice file.
- Where the adapted text is replaced during iteration, the attribution is dropped. The license notice sits per skill, in a markdown file next to its `SKILL.md`, and the root `NOTICE` file lists the adapted sources. specmgr is AGPL-3.0-or-later and the adapted sources are MIT, so the MIT notice must be kept for every passage that remains.

#### Measurement

- **Model:** `qwen3.8-27b-bf16-896k`, provider `vllm-sys0`, MTP with 5 speculative tokens, default thinking variant. A preflight records the endpoint, the provider id, the model id, the vLLM model revision, the speculative configuration and the sampling parameters (temperature, seed, top_p) with every run.
- **Isolation:** one fresh work directory and one fresh OpenCode container per trial. The container has no host OpenCode config, no `AGENTS.md`, and no skills except those of the condition. `webfetch` and `websearch` are denied, so a baseline cannot download the upstream skills. The configuration is injected through `OPENCODE_CONFIG_CONTENT`, and the run uses `opencode run --format json`.
- **MCP:** the harness starts its own pinned `structurizr/mcp` sidecar. The development MCP is bound to `127.0.0.1` and is not used.
- **Pinning:** the `upstream` skills are fetched on the host at run time from a pinned commit SHA of `jrjsmrtn/c4-skills` and mounted into the container, so nothing is vendored and no upstream notice is committed. The image tags or digests of OpenCode, `structurizr/mcp` and `structurizr/structurizr`, the Python and `jq` versions and the SHA form the version tuple. Each skill variant has a content hash as its stable identifier. The MCP and CLI images are pinned to a matching pair because the spike found a six-month skew.
- **Conditions:** `none` (MCP only), `upstream` (`jrjsmrtn/c4-skills` unmodified, the baseline to beat) and `skill` (the adapted skills). `upstream` is deliberately not patched. Its Docker-CLI advice cannot work in the container, which makes it a harsh comparison, and the results write-up says so. This is why every phase also has to beat `none` (ACC-012). The comparison condition per phase is fixed: validate-loop and view-design compare against `none` because no upstream skill matches, and dsl-authoring, c4-modeling and model-review compare against `upstream` and `none`.
- **Trials:** k=5 per case and condition, one trial at a time (`-j 1`), per-trial timeout about 1200 s, conditions interleaved in random order within the trials that are actually run (cached conditions are not reordered). The order seed is recorded. A timed-out trial counts as a failure and is flagged separately.
- **Budget:** 6 cases and 3 conditions at k=5 are 90 trials for a full run. At the timeout, that is up to about 30 hours. The expected cost per phase and in total is recorded in Task 100.170 from the measured time per trial.
- **Shared server:** the vLLM server is shared and has only two sequence slots. The runner refuses to start when vLLM already reports running requests, and it checks again between trials. A trial that ran while another client was active is flagged, and the runner pauses until the server is idle.
- **Caching:** results for `none` and `upstream` are cached per case and per version tuple, and rerun only when a case, a grader or a version changes. Iterations of `skill` then cost about a third of a full run.
- **Metrics:** gates (pass or fail) come from the real Structurizr CLI (`export -format json` plus `jq`-style queries), not from grepping the DSL. Tracked metrics: `validated_before_return` (the returned DSL is the exact text that got "OK" from `validate`), skills loaded, calls to `parse`/`validate`/`inspect`, `inspect_findings` and their triage, technology coverage of relationships, steps, tokens and wall time. Steps, tool calls and tokens are the comparable metrics. Wall time is informational because the server is shared.
- **Statistics:** the gate uses the pass-rate point estimate with the margins of ACC-008 and ACC-012. Wilson intervals and pass^k are reported for information only, because k=5 gives very wide intervals.
- **Cases:** `create-system`, `fix-dsl`, `mcp-limits`, `design-views`, `review-model` and `no-trigger` are the shared cases, and each skill phase adds one `modeling` or skill-specific case and one held-out case. The case-to-phase map is: `create-system` and `mcp-limits` belong to Phase 110 and are reused in Phase 120, `fix-dsl` to Phase 120, `modeling-decisions` to Phase 130, `design-views` to Phase 140, `review-model` to Phase 150, and `no-trigger` to every phase as the negative trigger case. The positive trigger is measured by the skills-loaded metric on each phase's primary case. The held-out cases are `heldout-validate`, `heldout-dsl`, `heldout-modeling`, `heldout-views` and `heldout-review`. A case is replaced or hardened if `none` passes all 5 trials, or if no condition passes any trial.
- **Reference design:** `passionsplay/structurizr-skill` (`evals/`) for the layout of cases, gates and metrics. Its `fix-forward-reference` case did not discriminate, so `fix-dsl` must be harder.

#### Stop Rule per Skill Phase

A skill phase ends when the skill clears its own gates, is not worse than `none` (pass rate not lower), and is not worse than its comparison condition: the pass rate over the phase's cases is not more than 10 percentage points lower, and no case is clearly worse (2 or more trials out of 5 fewer). Wilson intervals are reported only. At most 3 iterations are allowed, and each is a recorded variant measured on the same cases.

One held-out case is never used while tuning and runs once at the end. Its result never selects a variant. A clear held-out failure (0 of 5 trials passing, or a pass rate below `none`) marks the phase "accepted with caveat", and the caveat is rechecked in Phase 160 and stated in the results. If no variant clears the gates after 3 iterations and none beats `none`, the phase fails and the plan is revised before the next phase starts. If the gates are missed but a variant beats `none`, the phase may be accepted with a recorded caveat. Cumulative regression across all skills runs only in the final phase.

### Related Decisions

- TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8: Structurizr and C4 for specmgr: Spike Findings and Design Suggestions
- ADR 7a626b12-b189-4561-a51d-ffb2e9e193b4: Add an in-package, import-free plantuml package with a strict first-set-wins validation-source chain

### Task List

#### Phase 100: Measurement Harness

- [x] Task 100.100: Create the harness package `evals/c4-skills/` (Python, standard library only) with the run entry point, decide how `evals/` is made importable, and record that decision (an ADR if it is structure-level, otherwise the Updates log).
- [x] Task 100.110: Build the trial container and the injected OpenCode configuration (provider `vllm-sys0`, MCP sidecar, denied web access, condition-specific skills, the `upstream` skills fetched at the pinned SHA).
- [x] Task 100.120: Start and pin the `structurizr/mcp` sidecar and the Structurizr CLI image used by the graders as a matching pair, and pin the OpenCode image, the Python and `jq` versions and the `jrjsmrtn/c4-skills` commit SHA. Define the version tuple and the skill-variant content hash.
- [x] Task 100.130: Write the runner: sequential trials, random condition order with a recorded seed, per-trial timeout, the refusal to start on a busy vLLM, the re-check between trials, the recording of all versions, and the result cache for `none` and `upstream`.
- [x] Task 100.140: Write the parser for the `--format json` event stream and the metrics, including `validated_before_return` and the calls to `parse`, `validate` and `inspect`.
- [x] Task 100.150: Write the report: pass rates, the gate margins of ACC-008 and ACC-012, the per-case rule, Wilson intervals and pass^k as information, per-gate failures.
- [x] Task 100.160: Write unit tests under `tests/evals/` for the parser, the metrics, the intervals and the graders, using fixed known-good and known-bad workspaces and pre-exported JSON fixtures, with no model call. Tests that need the Structurizr CLI are skipped when Docker is missing.
- [x] Task 100.170: Run `none` against `upstream` on a small smoke case, record the real time per trial, and record the expected cost per phase and in total against the budget in Measurement.
- [x] Task 100.180: Write the preflight that records the vLLM endpoint, provider id, model id, speculative configuration and sampling parameters, and checks that the server is idle.
- [x] Task 100.190: Verify the licenses of `jrjsmrtn/c4-skills`, `passionsplay/structurizr-skill` and `structurizr/structurizr.github.io`, and record the provenance table (commit, license file, license type, check date). Move any source with an unconfirmed license to "ideas only".
- [x] Task 100.200: Add the repository housekeeping for `evals/`: `.gitignore` entries for trial work directories and cache, the treatment of `evals/` by ruff and pylint, the pytest import path, and a note that the pre-commit pytest hook is scoped to `src/` and `tests/` changes.

#### Phase 110: Skill structurizr-validate-loop

- [x] Task 110.100: Write the cases and graders for the loop (`create-system`, `mcp-limits`, `no-trigger` and `heldout-validate`), including the triage of `inspect` findings.
- [x] Task 110.110: Prove the graders against `none`, and check that each case discriminates (ACC-013).
- [x] Task 110.120: Write the skill v1 from TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8 and the MCP limits of REQ-006, adapting the validate-versus-inspect table and the DSL gotchas from `passionsplay/structurizr-skill`, and state the behavior when the MCP is absent (REQ-011).
- [x] Task 110.130: Measure against `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [x] Task 110.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [x] Task 110.150: Check the attribution and the source map, write `tests/opencode/test_skill_structurizr_validate_loop.py`, and run `specmgr harness-bundle` once the stop rule has passed.

#### Phase 120: Skill structurizr-dsl-authoring

- [ ] Task 120.100: Write the cases and graders for DSL authoring (`fix-dsl`, made harder than `fix-forward-reference`, and `heldout-dsl`), reusing `create-system` and `mcp-limits`.
- [ ] Task 120.110: Prove the graders against `none` and `upstream`, and check that each case discriminates (ACC-013).
- [ ] Task 120.120: Adapt skill v1 from `structurizr-dsl` of `jrjsmrtn/c4-skills` and the Structurizr documentation, with a thin `SKILL.md` and markdown reference files, the MCP limits, the gotchas of the spike and the behavior when the MCP is absent.
- [ ] Task 120.130: Measure against `upstream` and `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [ ] Task 120.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [ ] Task 120.150: Check the attribution and the source map, write `tests/opencode/test_skill_structurizr_dsl_authoring.py`, and run `specmgr harness-bundle` once the stop rule has passed.

#### Phase 130: Skill c4-modeling

- [ ] Task 130.100: Write the cases and graders for modeling decisions (`modeling-decisions`: container versus library, external systems, the common mistakes) and `heldout-modeling`.
- [ ] Task 130.110: Prove the graders against `none` and `upstream`, and check that each case discriminates (ACC-013).
- [ ] Task 130.120: Adapt skill v1 from `c4-model` of `jrjsmrtn/c4-skills` and remove the Elixir and OTP content. State the MCP limits where the skill depends on them, and the behavior when the MCP is absent.
- [ ] Task 130.130: Measure against `upstream` and `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [ ] Task 130.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [ ] Task 130.150: Check the attribution and the source map, write `tests/opencode/test_skill_c4_modeling.py`, and run `specmgr harness-bundle` once the stop rule has passed.

#### Phase 140: Skill c4-view-design

- [ ] Task 140.100: Write the cases and graders for view design (`design-views`: about 20 elements per view, explicit keys) and `heldout-views`.
- [ ] Task 140.110: Prove the graders against `none`, the comparison condition of this phase because no upstream skill matches, and check that each case discriminates (ACC-013).
- [ ] Task 140.120: Adapt skill v1 from the diagram-selection and view content of the sources, add the view-size rule of the spike, and add a short reference note on the C4-PlantUML export gotchas of the spike (`include *` drops custom elements, the default `Element` tag needs an explicit colour). State the MCP limits and the behavior when the MCP is absent.
- [ ] Task 140.130: Measure against `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [ ] Task 140.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [ ] Task 140.150: Check the attribution and the source map, write `tests/opencode/test_skill_c4_view_design.py`, and run `specmgr harness-bundle` once the stop rule has passed.

#### Phase 150: Skill c4-model-review

- [ ] Task 150.100: Write the cases and graders for review (`review-model` with seeded defects, a clean control, a check that no file changed) and `heldout-review`.
- [ ] Task 150.110: Prove the graders against `none` and `upstream`, and check that each case discriminates (ACC-013).
- [ ] Task 150.120: Adapt skill v1 from `c4-review` of `jrjsmrtn/c4-skills`, made read-only and based on the MCP tools. State the MCP limits and the behavior when the MCP is absent.
- [ ] Task 150.130: Measure against `upstream` and `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [ ] Task 150.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [ ] Task 150.150: Check the attribution and the source map, write `tests/opencode/test_skill_c4_model_review.py`, and run `specmgr harness-bundle` once the stop rule has passed.

#### Phase 160: Cumulative Regression and Results

- [ ] Task 160.100: Run all five skills on all cases against `none` and `upstream`, and recheck the phases that were accepted with a caveat.
- [ ] Task 160.110: Write the results under `evals/c4-skills/results/`, including the provenance table, the note on the Docker-CLI handicap of `upstream`, and the gates for which each skill is better than `none`.
- [ ] Task 160.120: Check ACC-001 to ACC-014 in a traceability list, and run the final `specmgr harness-bundle` drift check.
- [ ] Task 160.130: Update `AGENTS.md` (the skill surface and the `evals/` directory), `CHANGELOG.md` and the root `NOTICE` file with the adapted sources.

## Progress

### Current Status

**As of 2026-11-05**: Phase 110 (Skill `structurizr-validate-loop`) is done: the stop rule passed at iteration 2 of 3 — `skill` 4/15 vs `none` 0/15 on the phase's cases (`create-system` 2/5, `mcp-limits` 2/5, `no-trigger` 0/5 as designed), the wins being exactly the loop-delta gates — and the held-out case passed cleanly at 4/5 vs 0/5 (no caveat, so the phase is not "accepted with caveat"). The skill lives at `.opencode/skill/structurizr-validate-loop/` (the iteration-2 winner, variant hash `927d6c3fc039…`), the harness gained two corrections found in the prove run (Code Mode MCP-call detection; the egress-blocking private network — new version tuple hash `f22635f6…103662`), the pinning test is committed (`tests/opencode/test_skill_structurizr_validate_loop.py`, 24 tests), and the harness bundle and `docs/GENERATED.md` are regenerated (test-file count 492 → 496). Phase 120 can start.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-05 22:17:03.000Z - Phase 110 (Skill structurizr-validate-loop) complete — stop rule PASS at iteration 2

Tasks 110.100–110.150 are done; the quality gates are green (ruff format/check, vulture, full pytest suite 5949 passed / 18 skipped — the 24 new tests are the pinning test, `specmgr lint` on this README, `specmgr docs` + `specmgr harness-bundle` regenerated). The skill lives at `.opencode/skill/structurizr-validate-loop/` (the iteration-2 winner, variant `927d6c3fc039…`); the pinning test is `tests/opencode/test_skill_structurizr_validate_loop.py`; no committed record under `results/` was modified, only new run directories were added.

**Harness corrections (the p110-prove findings).** The first prove run surfaced two harness defects, both fixed before any skill was written. (1) Code Mode: opencode 2.2.5 (the pinned trial image) exposes the pinned `type: remote` MCP server to the model only through Code Mode (`execute` blocks calling `tools.structurizr.<tool>`) — diagnostics proved no config shape (the deprecated `mcp.<name>` or the current `mcp.servers` + `codemode: false`) yields native remote-MCP tools, while the sidecar itself is protocol-healthy — so the stream metrics gained a Code Mode detection layer (`c4_skills/codemode.py` + the normalized MCP-call view in `metrics.py`) with locked conservative attribution (a Code Mode `validate` entry answers `OK` only for a single-reference completed block whose output strips to `OK`; the `dsl` counts only as a plain inline literal; unattributable calls can only fail to flip a gate, never pass one; native semantics byte-identical, pinned as regression tests). (2) Egress: the `--network host` trials allowed shell egress — in p110-prove, 3/5 no-trigger baseline trials rendered real PNGs via `kroki.io` (verified in the committed streams: valid PNG signature + `IEND` terminator) — violating the locked "no external network unless explicitly configured" directive. Trials now run on a per-run `docker network create --internal c4eval-<run_id>` (canaries prove DNS + bare-IP egress fail from inside: `plantuml.com`/`kroki.io` unresolvable, `wget` "bad address"), the sidecar sits on that network at fixed container port 8181, the grader CLI containers run `--network none` (a CLI theme fetch fails with "Temporary failure in name resolution" — the offline block proven live), and vLLM access is conditional (option C: the stdlib TCP forwarder at `<gateway>:8081` preferred — the committed trials show `baseURL: http://172.21.0.1:8081/v1`; on EADDRINUSE — the shared vLLM answers on `0.0.0.0:8081` (verified `ss -tlnp`), correcting the stale pin comment — strict version+model verification, then direct access; the trial URL is mode-invariant). The version tuple gained `network_mode: "internal-bridge"` (new hash `f22635f6ba9b…103662`), invalidating every cached baseline by design.

**Campaigns (in order).** `p110-prove` (run `p110-prove-2026-11-03T162909Z`, seed 721183, 20 fresh trials): `none` 0/5 on all four cases under the pre-fix harness (7/20 timeouts) — superseded, kept as history. → the harness corrections above. → `p110-prove2` (run `p110-prove2-2026-11-04T200612Z`, seed 448993): the canonical `none` baseline, 0/5×4 — the baseline calls `validate` and gets `OK` (the Code Mode flips proven live: `validate_ok_called` 5/5 on `create-system` and `heldout-validate`) but never `parse`/`inspect`/triage (that is the skill's delta); window median 272.1 s, 3/20 timeouts; its 6 cached hits are the byte-identical trials of the aborted first attempt (`p110-prove2-2026-11-04T174854Z`). → `p110-iter1` (run `p110-iter1-2026-11-05T023333Z`, seed 671615, variant `c3d8bffee5ef…` = v1, 15 fresh skill trials): skill 0/15 — the stop rule's "clears its own gates" clause failed (wrapped/bundled/variable Code Mode MCP calls, unquoted findings, 10/15 timeouts in a degraded solo window, 1 contended), and v1's description organic clause ("…whether surfaced by an explicit request or organically while working with Structurizr DSL text that must be validated before it is returned") loaded the skill on 4/5 no-trigger render requests — the trap broken. → `p110-iter2` (run `p110-iter2-2026-11-05T143241Z`, seed 865648, variant `927d6c3fc039…`, 15 fresh skill trials): skill 4/15 — `create-system` 2/5, `mcp-limits` 2/5, `no-trigger` 0/5 as designed; `margin.ok` true (+26.67 pp over `none`, no clearly-worse case); ACC-012 per-gate wins — `create-system`: `parse_called` 0→5, `inspect_called` 0→5, `triage_complete` 0→2, `validated_before_return` 0→5; `mcp-limits`: `validate_ok_called` 0→4, `triage_complete` 2→5, `validated_before_return` 0→4, `limits_acknowledged` 2→4, plus the model-shape gates as a side effect of the single-file fallback (`cli_valid` 0→3, `cli_export` 1→4, `has_system` 1→4, `has_person` 1→4, `has_view` 0→4, `two_containers` 1→3, `relationship_technology` 0→4); `no-trigger` level (0/0 — see the known limitation below). **Stop rule PASS at iteration 2 of 3.** → `p110-heldout` (run `p110-heldout-2026-11-05T203735Z`, seed 743505, 5 fresh skill trials, `none` all cached from prove2): skill 4/5 vs `none` 0/5 — a clean pass under the hybrid rule, no caveat; the single failure a genuine `triage_complete` miss (4 of 8 findings untriaged) in a healthy window. The aborted attempts are kept as window-degradation history (committed without `run.json`): `p110-iter1-2026-11-04T231448Z` (degraded solo window — 4 fresh skill trials, all 1200 s timeouts) and `p110-iter2-2026-11-05T102925Z` (the 3609 s idle-wait abort under a sustained external vLLM client); the resumed runs' `none` halves are cache hits throughout.

**Cost vs the Phase 100 estimate.** The ≈21–45 min/variant healthy-window estimate did not hold — the shared-server windows dominated: iter1 4.19 h fresh model time (10/15 timeouts), iter2 2.47 h (4/15 timeouts, 2 contended), held-out ≈5 min (0 timeouts, one 370.4 s idle wait on a cached trial). Total fresh model trials across the phase: 79 (20 prove + 6 aborted-prove2-first + 14 prove2 + 4 aborted-iter1 + 15 iter1 + 15 iter2 + 5 held-out) ≈ 13.6 h of fresh model wall time — within the 30 h full-run budget.

**Known no-trigger limitation.** With egress blocked, neither `none` nor a correctly non-loading skill trial can produce images, and the limitation is stated in phrasings the locked loose `mcp_limit_stated` matcher does not cover (verified near-misses in the committed streams: "no local renderer", "can't rasterize", …) — `no-trigger` lands 0/5 for both conditions, and ACC-013's clause 2 is structurally unmeetable for this case in this environment. Accepted as a documented deviation (the case still does its job as the trigger trap — see Decisions Made).

#### 2026-11-03 08:51:17.000Z - Phase 100 review cycle 1: apply D1–D5 and I1–I9 from the post-implementation review

A post-implementation review of the committed Phase 100 work found 5 doc/narrative discrepancies and 9 improvements; all are applied now. The harness stays green (ruff format/check, vulture, the full pytest suite, `specmgr lint` on this README), no committed measurement result under `results/` was touched, and no model trial was run — verification is unit-level (the container layer is mocked).

**Doc/narrative (D1–D5).** `events.py`'s module docstring named a fixture that does not exist (D1); the `EVENT_FILE_COMMIT_LIMIT` docstring described a summarize-and-keep behavior the code never implemented — over-limit streams are now kept in the gitignored work dir, excluded from the committed results dir, and flagged in the trial record via the additive `event_file_bytes` / `event_file_committed` fields (D2, the behavior decision is recorded in Decisions Made); the OpenCode image pin's comment attributed digest integrity to the runner — it is the preflight's local-image `RepoDigests` check (D3); the "auto-generated views for every workspace" claim was overstated — generation happens only when the DSL defines no views at all (D4); the cost paragraph's "healthy-window median of ~100 s / 25–45 min" is now stated precisely from the recorded per-trial times (D5). The Phase 100 smoke-run paragraph also discloses that the canonical run's two `none` trials were re-measured because run 2's `none` cache entry (two degraded-window timeouts) had been removed beforehand (I3a).

**Runner robustness (I1, I2, I3b, I4, I6, I7, I8, I9).** The sidecar's free-port selection is now racy-safe: on a failed attempt the container's `docker logs` are inspected for a bind/port-in-use failure, and the start retries with a fresh port (up to 3 attempts; a non-collision failure aborts immediately with the container log tail; the aborting error names every colliding port and the log evidence; the residual window is documented) (I1). The event stream is no longer captured with a `docker logs -f --tail 0` started after the container began — it is taken from a single non-following `docker logs <name>` after the container stops (no start-gap loss; the trial's exit code still comes from `docker inspect`, the same value `docker wait` reports), and its first event type is cheaply checked (a suspect capture warns, never fails the trial) (I2). `run.json` records the per-trial cache hit/miss reason (`cache_reason`: `hit` / `miss:file-absent` / `miss:key-mismatch` / `miss:file-unparseable` / `miss:trial-absent` / `n/a` — additive; pre-existing records parse via defaults) (I3b). The CLI's exit-code contract is now enforced in `main`: `KeyError`/`ValueError`/`AssertionError` (usage-shaped: an unknown case, `k <= 0`, a missing/misplaced `--skills-dir`, `report` on a dir without `run.json`) → 2; `RuntimeError`/`OSError` (runtime-shaped) → 1; any other exception type stays a raw traceback (a harness bug) — recorded in `cli.py`'s module docstring and the harness README (I4). `EDIT_TOOL_NAMES` now also counts the command-execution tools the committed smoke streams show agents using to mutate files (`shell` with a `command` input, `execute` with a `code` input); it remains a coarse, informational triage signal that never gates (I6). The synthetic `tool-stream.ndjson` fixture's top-level token is now the real opencode 2.2.5 `tool_use` (a fidelity test pins it) (I7). The pre-commit pytest hook's file pattern is now `^(src|tests|evals)/.*\.py$`, so a harness-code change alone also triggers the local suite (I8; this supersedes the Phase 100 entry's housekeeping note about the old `src/`+`tests/` scoping). The two 126/122-char lines in `graders.py`/`preflight.py` are wrapped to ≤ 120 chars, matching the sibling multi-line call style (I9).

**Phase-110 readiness (I5).** The `skill` condition is now functional: `run` takes `--skills-dir <path>` (one skill folder, or a root of skill folders — `load_skill_source` verifies it and a usage error otherwise), the variant is hashed with the existing `skill_variant_hash` (recorded in `run.json` as `skill_variant_hash`; the single-folder and root shapes of the same content hash equally), and the files are copied into each skill trial's work dir at `.opencode/skills/<name>/` BEFORE the container starts (the old branch could only ever see externally pre-placed skills). `skill` trials stay non-cacheable (the existing assert), and the `none`/`upstream` cache-key composition is byte-identical (existing cache entries and committed runs remain valid).

New unit tests (no model call, no Docker): `tests/evals/test_runner_robustness.py`, `tests/evals/test_sidecar.py`, `tests/evals/test_cli_main.py`, plus additions to the metrics, events, and pins/cache suites (63 → 107 tests).

#### 2026-11-02 08:13:42.000Z - Phase 100 (Measurement Harness) complete

Tasks 100.100-100.200 are done; the quality gates are green (ruff format/check, vulture, full pytest suite 5702 passed / 18 skipped, `specmgr lint` on this README).

**Harness and importability.** `evals/c4-skills/` holds the standard-library-only harness: inner importable package `c4_skills/` + the thin launcher `run.py` (the hyphenated folder name is not a legal package name); `tests/evals/conftest.py` does the same `sys.path` insertion for the 63 unit tests. Nothing is added to the wheel or the harness bundle; `pyproject.toml` is untouched. Decision recorded in Decisions Made (not an ADR: feature-scoped, development-only infrastructure).

**Pins and version tuple.** `ghcr.io/anomalyco/opencode:2.2.5` (digest `sha256:1690aad6…`), the spike-verified matching pair `structurizr/mcp:2026.04.20` + `structurizr/structurizr:2026.10.26-noble` (digests recorded), vLLM 0.26.0 serving `qwen3.8-27b-bf16-896k` at `http://127.0.0.1:8081/v1` (max_model_len 917504), host Python 3.13.13 (the uv project Python), jq 1.6, upstream `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b` (re-verified against the GitHub API). The version tuple is the canonical JSON of these pins plus the injected sampling parameters (temperature 0.0, top_p 1.0, seed 1337); its sha256 is `0de1ba9850e9d7e426a2f12a852cf17d25b2f2f5d0d12f528ce3b4cb2395a7b4`. Skill-variant content hash = sha256 over the sorted (relative path, sha256 of content) pairs of the condition's skill files; `none` hashes the empty set (`4f53cda1…61202b945`). The preflight re-checks the mutable values (vLLM version/model, image digests, Python, jq) with every run and aborts on a mismatch; the speculative configuration (MTP, 5 tokens) is recorded as "as deployed, not externally verifiable" (vLLM 0.26.0 exposes no external metric for it).

**Trial container and networking.** Trials run in `ghcr.io/anomalyco/opencode:2.2.5` with `--network host` (vLLM and the sidecar are bound to 127.0.0.1; there is no bridge route to them), a fresh work dir per trial, no host OpenCode config, no `AGENTS.md`, skills only from the condition (mounted at `.opencode/skills/<name>/` inside the work dir), and the injected `OPENCODE_CONFIG_CONTENT` denying `webfetch`/`websearch`/`question`. The harness starts its own pinned `structurizr/mcp` sidecar on a free ephemeral host port (health-checked with a real MCP initialize + tools/list round trip; the dev MCP on port 3000 is never used) and tears it down after the run. Trial and CLI containers run as the host uid:gid so work-dir files stay host-owned. The event-stream schema was verified empirically (a probe trial capture is committed at `results/probe-schema-3/` and pinned as a test fixture).

**Smoke run (Task 100.170).** The canonical record is `results/smoke-2026-11-02T065731Z/` (k=2, seed 602651): `none` 1/2 (none-k0 PASS 83.0 s, none-k1 TIMEOUT at 1200 s with a valid on-disk workspace — the 06:57-07:17 UTC window ran under external shared-GPU load), `upstream` 2/2 (180.0 s and 42.6 s, the `structurizr-dsl` skill loaded in both). Two earlier runs are kept as history: `smoke-2026-11-01T224901Z` (first end-to-end proof: `none` k0 PASS in 27.5 s; its `none` k1 trial hit the 1200 s timeout, and killing the `docker run` client on timeout orphaned that trial's container — opencode 2.x starts a managed service on a random host-network port, and the next trial's container picked the same port and exited 1 before any model call. Fixed by running the trial container detached under a name, `docker kill`-ing the container (never just the client) on timeout, and sweeping stray `c4eval-trial-*` containers at run start) and `smoke-2026-11-02T053217Z` (a degraded-server window, ~10x slower per token: both `none` trials timed out at 1200 s, both `upstream` trials passed in 180.0 s / 42.6 s once the window passed; its `upstream` results are the ones the canonical run reused from the result cache, with the event streams copied over). The canonical run re-ran both `none` trials even though run 2 had cached them: the `none` cache entry — whose two trials were the degraded-window 1200 s timeouts — had been removed before the canonical run, so the `none` baseline would be freshly measured in a healthy window (only the healthy-window `upstream` cache entry survived into it; the canonical run's own `none` results now hold the cache). No trial was contended-flagged in the canonical run (the runner's idle-wait absorbed the other clients; waits are recorded per trial, 0-556 s).

**Cost vs budget (Measurement).** Measured per-trial times in the healthy windows: 27.5 s, 83.0 s, 42.6 s, 180.0 s, plus run 1's verbose upstream trial at 608 s (10 steps, 185k input tokens — the agent iterated on the model without ever calling the MCP). The canonical run's report estimates the full 90-trial run at 16.0 h at the observed median (641.9 s, dominated by one timeout) and 30.0 h worst case at the 1200 s timeout — both within the ~30 h budget. With `none`/`upstream` cached per (case, condition, version tuple, grader hash, skill variant hash), a skill phase pays only its `skill` trials plus uncached baselines: at the healthy-window median of 83.0 s (62.8 s excluding the verbose 608 s trial), a 3-case phase's 15 skill trials take ≈ 21 min of model time at the median, up to ≈ 45 min if every trial ran at the 180.0 s healthy-window maximum.

**Licenses (Task 100.190).** All three adaptation sources are confirmed MIT at the pinned commits (provenance table at `results/provenance.md`): `jrjsmrtn/c4-skills` `e86d8a91…` (LICENSE, "Copyright (c) 2026 Georges Martin"), `passionsplay/structurizr-skill` `5e45154e…` (LICENSE, "Copyright (c) 2026 Benjamin Turner"), `structurizr/structurizr.github.io` `530a9645…` (LICENSE, MIT per the GitHub API; boilerplate copyright "2022 just-the-docs" from the Jekyll theme). Nothing moved to "ideas only".

**Housekeeping (Task 100.200).** `.gitignore` now covers `evals/c4-skills/work/`, `evals/c4-skills/cache/` and `evals/c4-skills/.upstream/` (raw trial work dirs, the result cache, the fetched upstream checkout — never committed); committed run records under `results/` stay small (KB-scale event streams, capped at 2 MB per trial). ruff lints `evals/` from the repo root (enforced, green); pylint (advisory, `git ls-files '*.py'`) sees the files once committed; the pytest import path is the `tests/evals/conftest.py` `sys.path` insertion. The pre-commit pytest hook is scoped to `src/`+`tests/` changes, so the new `tests/evals/` tests run in pre-commit and CI. See `evals/c4-skills/README.md` for the layout and run instructions.

#### 2026-11-01 15:40:00.000Z - Plan refined after review

A review of the plan found 3 errors, 13 gaps and 7 discrepancies, and all of them are addressed. The skills are now bound to the Structurizr MCP tools instead of being tool-agnostic, and REQ-011 covers the no-MCP case. REQ-003 defines "checked" as triage of `inspect` findings. All files next to a `SKILL.md` must be markdown so that the harness bundle carries them. The gate now uses a point estimate with a 10 percentage point margin and requires each skill to be not worse than `none`, with Wilson intervals reported only. A held-out failure never selects a variant, and a clear failure marks the phase "accepted with caveat". The `upstream` skills are fetched at a pinned commit SHA at run time instead of being vendored. New tasks cover the preflight, license verification, the `evals/` housekeeping, the skill pinning tests and the final traceability check. The improvements for an ADR on `evals/`, the budget, bundle timing and the C4-PlantUML export gotchas were folded in.

#### 2026-11-01 14:28:19.000Z - Plan extended with measurement and one phase per skill

The plan now reuses MIT-licensed sources (adapted, with attribution only where adapted text remains) and adds a Python container harness that runs OpenCode against `qwen3.8-27b-bf16-896k` on sys0 with `-j 1`. There is one phase per skill (validate-loop, dsl-authoring, c4-modeling, view-design, model-review), each with a stop rule: not worse than its comparison condition, at most 3 iterations, one held-out case. Cumulative regression runs only in Phase 160. The harness-bundle task moved into each skill phase.

#### 2026-11-01 13:10:53.141Z - Created

The plan is created from GitHub issue 250.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-05 22:17:03.000Z - Phase 110 decisions

All feature-scoped, development-only (nothing in `src/`, nothing shipped) — the same placement rule as the Phase 100 entries.

- **Locked 2026-11-03 planning decisions**: the no-trigger case shape (a render-to-image prompt over a seeded valid workspace; it stays valid in Phases 120–150 because a review- or view-flavored prompt would trigger the *correct* later skill and fail the case there); the `parse_called` hard gate on the `create-system` family (the loop discipline is not optional — a DSL result that was never parsed is not a pass); the prove-run scope (the held-out case's `none` baseline IS measured in the prove run, since no skill variant exists yet and nothing is tuned with it, so the final held-out run costs only 5 fresh skill trials); the gate sets (13 gates on `create-system`/`heldout-validate`, 14 on `mcp-limits` — 13 + `limits_acknowledged` — and 4 on `no-trigger`: `no_mounted_skill_loaded`, `file_untouched`, `cli_valid`, `mcp_limit_stated`); the per-skill `NOTICE.md` naming (a markdown file next to the `SKILL.md`, so the harness bundle carries it).
- **ACC-013 reading (user-ruled 2026-11-04)**: plan-literal. The locked expectation was "none strictly between 0/5 and 5/5"; the data gave 0/5×4, consistent with the locked prompt design (the baseline deliberately lacks the parse/inspect/triage discipline — that is the skill's delta). Clause 1 holds (none never passes all 5); clause 2 ("≥1 condition passes ≥1") is confirmed by the skill condition in 110.130. The harden-and-reprove contingency was not applied: lifting none into 1–4/5 would require removing the skill-delta gates, contradicting the locked gate sets and REQ-003.
- **Code Mode detection (user-ruled 2026-11-04)**: opencode 2.2.5 (the pinned trial image) exposes `type: remote` MCP servers to the model ONLY through Code Mode (`execute` → `tools.<server>.<tool>`); diagnostics proved no config shape (the deprecated `mcp.<name>` or the current `mcp.servers` + `codemode: false`) yields native remote-MCP tools, and the MCP server itself is protocol-healthy (sidecar round trip). The detection layer (`c4_skills/codemode.py` + the normalized MCP-call view in `metrics.py`) counts native AND Code Mode invocations with locked conservative attribution: a Code Mode validate entry answers OK only for a single-reference completed block whose output strips to `OK`; the `dsl` counts only as a plain inline literal (no interpolation/variables/shorthand); unattributable calls can only fail to flip a gate, never pass one. Native semantics byte-identical (pinned as regression tests).
- **Egress blocking (user-ruled 2026-11-04)**: the agent under test may reach only the explicitly configured endpoints (vLLM + the MCP sidecar); nothing external. Implemented as a per-run `docker network create --internal c4eval-<run_id>` (Docker-enforced no-route-to-outside; canaries prove DNS + bare-IP egress fail from inside), the sidecar on that network at fixed container port 8181 (host health check via the container IP; the obsolete host-port-collision retry machinery removed — ports are per-netns), trial containers on it (own netns — the smoke-run-1 managed-service host-port collision class is gone), grader CLI containers on `--network none`. vLLM access is conditional (option C): the stdlib TCP forwarder bound to `<gateway>:8081` is the preferred path; on EADDRINUSE — the shared vLLM answers on `0.0.0.0:8081` (verified `ss -tlnp`; the pin comment claiming a 127.0.0.1 bind was stale and is corrected) — the run falls back to direct access ONLY after strict host-side verification that the pinned server (exact version 0.26.0 + model id) answers there, else it aborts before any trial. The trial's vLLM URL is mode-invariant. The version tuple gained `network_mode: "internal-bridge"` → new `version_tuple_hash f22635f6…103662` → every cached baseline invalidated by design; p110-prove is superseded history, p110-prove2 is the canonical none baseline.
- **no-trigger known limitation (accepted 2026-11-05)**: with egress blocked, the baseline (and any correctly NON-loading skill trial) cannot produce images and states the limitation in phrasings the locked loose `mcp_limit_stated` matcher does not cover (verified near-misses: "no local renderer", "can't rasterize", …) — so no-trigger lands 0/5 for BOTH `none` and `skill`, and ACC-013's clause 2 is structurally unmeetable for this one case in this environment. Accepted as a documented deviation: the case still does its job as a trigger TRAP (`no_mounted_skill_loaded` is the live gate — it caught iter1's over-broad description, 4/5 loads; iter2's fixed wording 0/5), the stop rule is not distorted (0 vs 0 = not worse), and the re-prove/iteration data confirm the failure is the wording gate only (3/4 gates pass per trial). Revisit in Phase 160 (matcher coverage vs the agents' natural phrasings).
- **iter2 trigger-surface change**: the v1 description's trailing organic clause ("whether surfaced by an explicit request or organically while working with Structurizr DSL text that must be validated before it is returned") loaded the skill on 4/5 no-trigger render requests (trap broken, measured). iter2 replaces it with the negative clause "It checks DSL text only and does not itself produce any files" (kept: all four positive trigger phrases, single-task naming); measured 0/5 loads. Pinned by the new pinning test.
- **Aborted runs kept as history** (Phase 100 smoke-run precedent): the two aborted p110-iter attempts are committed without `run.json` (partial records, window-degradation evidence); the p110-prove2 first attempt's 6 trials are the cache source of the canonical run's 6 hits (byte-identical verified).

#### 2026-11-03 08:51:17.000Z - Phase 100 review cycle 1 decisions

All feature-scoped, development-only (nothing in `src/`, nothing shipped) — the same placement rule as the Phase 100 entry below.

- **D2 — over-limit event streams**: kept, never summarized and never deleted, in the gitignored work dir (debugging material; the dir is never committed), excluded from the committed results dir, and flagged in the trial record with the additive fields `event_file: null` + `event_file_committed: false` + `event_file_bytes: <size>`. The stream is captured into a sibling of the trial's mounted work dir (never inside it — the agent would see it there), and the metrics always parse the captured stream, over-limit or not.
- **I1 — sidecar port retry**: a bounded loop of up to 3 attempts; a retry happens ONLY when the failed container's logs evidence a bind/port-in-use failure (any other failure aborts immediately, with the container log tail in the error); the aborting error names every colliding port and the log evidence. Residual window (the port taken after the log check, before the retry's bind) is documented: the same retry logic absorbs it on the next attempt.
- **I2 — event capture**: the canonical stream is a single non-following `docker logs <name>` taken after the container has stopped (no start-gap loss, no follow process to terminate); the trial's exit code stays `docker inspect`'s `{{.State.ExitCode}}` (the same value `docker wait` would report, so a killed trial keeps `exit_code: null` + `timeout: true`); a cheap first-event-type check (`step_start`/`error` expected — a lone `error` is a legitimate shape, the smoke run 1 port collision produced it) warns on a suspect capture without failing the trial.
- **I4 — CLI exit-code mapping**: `KeyError`/`ValueError`/`AssertionError` → 2 (usage-shaped: an unknown case, an invalid argument like `k <= 0`, a missing/misplaced `--skills-dir`, a caller precondition on an artifact the command needs, e.g. a missing `run.json`); `RuntimeError`/`OSError` → 1 (runtime-shaped: pins, preflight, sidecar, containers, I/O); any other exception type propagates as a raw traceback (a harness bug, never papered over by an exit code). Recorded in `cli.py`'s module docstring and `evals/c4-skills/README.md`.
- **I5 — skill variant source**: `run --skills-dir <path>`; `<path>` is either one skill folder (carries a `SKILL.md`) or a root of skill folders (direct subfolders carrying a `SKILL.md`), verified by `load_skill_source` (a `ValueError` otherwise → exit 2). Files are hashed relative to the containing skills root with the existing `skill_variant_hash` — the single-folder and root shapes of the same content hash equally — copied into each skill trial's work dir at `.opencode/skills/<name>/` before the container starts, and recorded in `run.json` as `skill_variant_hash` (None for runs without the skill condition). `skill` trials remain non-cacheable (the existing `CacheKey.make` assert), and the `none`/`upstream` cache-key composition is unchanged.

#### 2026-11-02 08:13:42.000Z - Phase 100 harness decisions

Recorded per the AGENTS.md criteria: all of these are feature-scoped, development-only infrastructure (nothing in `src/`, nothing shipped), so they live here, not in ADRs.

- **Importability (Task 100.100)**: `evals/c4-skills/` is not a legal package name (hyphen), so the harness keeps an inner importable package `c4_skills/` plus the thin launcher `evals/c4-skills/run.py`; `tests/evals/conftest.py` performs the same `sys.path` insertion for the unit tests. No `pyproject.toml` change, nothing in the wheel, nothing imported from `src/`.
- **Trial networking**: `--network host` for trial containers (vLLM at `127.0.0.1:8081` and the harness sidecar are loopback-bound; the default bridge network has no route to them). "Isolation" stays the plan's filesystem/config isolation (fresh work dir, no host OpenCode config, condition-only skills, web denied) — not network isolation.
- **Container user + timeout semantics**: trial and grader-CLI containers run as the host uid:gid (work-dir files stay host-owned; root-owned files in the gitignored work roots would need docker to clean up). On a per-trial timeout the harness `docker kill`s the trial container by name — killing only the `docker run` client orphans the container, and opencode 2.x's managed service keeps a random host-network port bound (this collided with the next trial in smoke run 1); a stray-container sweep runs at every start.
- **Sidecar**: the harness starts its own `structurizr/mcp` sidecar per run on a free ephemeral host port (never 3000/9797, the dev services' ports), health-checked with a real MCP `initialize` + `tools/list` round trip against the pinned six-tool set, torn down in a `finally`.
- **Skill mount + discovery**: condition skills are copied into the trial work dir at `.opencode/skills/<name>/` (opencode 2.x's project location, plural `skills/`; the singular `skill/` remains supported for backwards compatibility). A live probe verified discovery and loading (the `skill` tool takes the identifier as `id`).
- **Gates over the export JSON**: the `has_view` gate counts only user-defined views — the JSON exporter auto-generates `generatedKey` default views (one container view per system, a system context view, a system landscape view) only when the DSL defines no views at all (the exporter logs `no views defined; creating default views`; the `good` fixture defines one view and exports zero generated ones). `relationship_technology` and every element count work on the deduplicated model relationships (view-scoped linked copies, carrying `linkedRelationshipId`, are excluded).
- **jq-style queries in pure Python**: the stdlib-only constraint rules out shelling to `jq` inside the grader, so the queries are implemented as pure functions over the parsed `export -format json` document (unit-testable on pre-exported fixtures, ACC-006); the host `jq` 1.6 is still pinned and recorded because ad-hoc verification of exports uses it.
- **Sampling parameters**: injected through the documented provider model `options` block (`temperature` 0.0, `topP` 1.0, `seed` 1337) and recorded in every preflight; their server-side application is not independently verified (the shared vLLM's throughput varies under external load, and the plan only requires recording what the harness injects).
- **Canonical Phase 100 record**: `results/smoke-2026-11-02T065731Z/` (seed 602651); the two earlier smoke runs are kept as shared-server history (one healthy-window proof, one degraded window). A trial that timed out under a slow window is a flagged failure per the plan, not re-scored.
