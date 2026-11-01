---
classification: null
created: '2026-11-01T14:10:53.141+01:00'
id: feat-250-c4-structurizr-skills
status: planning
type: feat
updated: '2026-11-01T15:45:39.084+01:00'
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

- [ ] Task 100.100: Create the harness package `evals/c4-skills/` (Python, standard library only) with the run entry point, decide how `evals/` is made importable, and record that decision (an ADR if it is structure-level, otherwise the Updates log).
- [ ] Task 100.110: Build the trial container and the injected OpenCode configuration (provider `vllm-sys0`, MCP sidecar, denied web access, condition-specific skills, the `upstream` skills fetched at the pinned SHA).
- [ ] Task 100.120: Start and pin the `structurizr/mcp` sidecar and the Structurizr CLI image used by the graders as a matching pair, and pin the OpenCode image, the Python and `jq` versions and the `jrjsmrtn/c4-skills` commit SHA. Define the version tuple and the skill-variant content hash.
- [ ] Task 100.130: Write the runner: sequential trials, random condition order with a recorded seed, per-trial timeout, the refusal to start on a busy vLLM, the re-check between trials, the recording of all versions, and the result cache for `none` and `upstream`.
- [ ] Task 100.140: Write the parser for the `--format json` event stream and the metrics, including `validated_before_return` and the calls to `parse`, `validate` and `inspect`.
- [ ] Task 100.150: Write the report: pass rates, the gate margins of ACC-008 and ACC-012, the per-case rule, Wilson intervals and pass^k as information, per-gate failures.
- [ ] Task 100.160: Write unit tests under `tests/evals/` for the parser, the metrics, the intervals and the graders, using fixed known-good and known-bad workspaces and pre-exported JSON fixtures, with no model call. Tests that need the Structurizr CLI are skipped when Docker is missing.
- [ ] Task 100.170: Run `none` against `upstream` on a small smoke case, record the real time per trial, and record the expected cost per phase and in total against the budget in Measurement.
- [ ] Task 100.180: Write the preflight that records the vLLM endpoint, provider id, model id, speculative configuration and sampling parameters, and checks that the server is idle.
- [ ] Task 100.190: Verify the licenses of `jrjsmrtn/c4-skills`, `passionsplay/structurizr-skill` and `structurizr/structurizr.github.io`, and record the provenance table (commit, license file, license type, check date). Move any source with an unconfirmed license to "ideas only".
- [ ] Task 100.200: Add the repository housekeeping for `evals/`: `.gitignore` entries for trial work directories and cache, the treatment of `evals/` by ruff and pylint, the pytest import path, and a note that the pre-commit pytest hook is scoped to `src/` and `tests/` changes.

#### Phase 110: Skill structurizr-validate-loop

- [ ] Task 110.100: Write the cases and graders for the loop (`create-system`, `mcp-limits`, `no-trigger` and `heldout-validate`), including the triage of `inspect` findings.
- [ ] Task 110.110: Prove the graders against `none`, and check that each case discriminates (ACC-013).
- [ ] Task 110.120: Write the skill v1 from TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8 and the MCP limits of REQ-006, adapting the validate-versus-inspect table and the DSL gotchas from `passionsplay/structurizr-skill`, and state the behavior when the MCP is absent (REQ-011).
- [ ] Task 110.130: Measure against `none` and iterate, at most 3 iterations, and record each variant by its content hash.
- [ ] Task 110.140: Run the held-out case once and record the result under the hybrid rule of the stop rule.
- [ ] Task 110.150: Check the attribution and the source map, write `tests/opencode/test_skill_structurizr_validate_loop.py`, and run `specmgr harness-bundle` once the stop rule has passed.

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

**As of 2026-11-01**: Planning. The plan is refined after review (tool binding, triage of `inspect` findings, gate margins, held-out rule, pinning, licensing and housekeeping). Implementation has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-01 15:40:00.000Z - Plan refined after review

A review of the plan found 3 errors, 13 gaps and 7 discrepancies, and all of them are addressed. The skills are now bound to the Structurizr MCP tools instead of being tool-agnostic, and REQ-011 covers the no-MCP case. REQ-003 defines "checked" as triage of `inspect` findings. All files next to a `SKILL.md` must be markdown so that the harness bundle carries them. The gate now uses a point estimate with a 10 percentage point margin and requires each skill to be not worse than `none`, with Wilson intervals reported only. A held-out failure never selects a variant, and a clear failure marks the phase "accepted with caveat". The `upstream` skills are fetched at a pinned commit SHA at run time instead of being vendored. New tasks cover the preflight, license verification, the `evals/` housekeeping, the skill pinning tests and the final traceability check. The improvements for an ADR on `evals/`, the budget, bundle timing and the C4-PlantUML export gotchas were folded in.

#### 2026-11-01 14:28:19.000Z - Plan extended with measurement and one phase per skill

The plan now reuses MIT-licensed sources (adapted, with attribution only where adapted text remains) and adds a Python container harness that runs OpenCode against `qwen3.8-27b-bf16-896k` on sys0 with `-j 1`. There is one phase per skill (validate-loop, dsl-authoring, c4-modeling, view-design, model-review), each with a stop rule: not worse than its comparison condition, at most 3 iterations, one held-out case. Cumulative regression runs only in Phase 160. The harness-bundle task moved into each skill phase.

#### 2026-11-01 13:10:53.141Z - Created

The plan is created from GitHub issue 250.
