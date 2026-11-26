---
classification: null
created: '2026-11-26T18:48:28.901+01:00'
id: feat-277-agent-test
status: planning
type: feat
updated: '2026-11-26T18:48:28.901+01:00'
version: 1.0.0
---

# Feature: Pre-Release Agent Acceptance Test of specmgr in a Container

## Plan

### Overview

Today a new specmgr version is tested by hand only after it is published to TestPyPI (SOP 98537416-0e6e-4a02-925f-974a17bfa10a, "Perform a release of biz.dfch.specmgr"). At that point the version is already tagged and on an index, so defects are found late. This feature adds a pre-release agent acceptance test: an agent tests all specmgr functions in an isolated container against a not-yet-released commit, before anything is published. Addresses GitHub issue #277. The requirements come from the interview QA aed61f42-d131-4188-ac58-66de3cfcf9b8; the question numbers in brackets (e.g. [QA 1.0030]) point into it.

The test has two parts. The Claude Code part (`claude -p`) is the functional test of the whole surface. The OpenCode part (an oc-farm instance with the local vLLM model) only checks that the specmgr surface and the installed harness files are visible to an OpenCode agent.

### Requirements

- REQ-001: The test runs specmgr from a clean checkout of a given commit or branch, started with `uv run --directory <checkout>`; no wheel is built and nothing is uploaded to an index [QA 0.0020, 0.0030, 0.0040].
- REQ-002: The functional test is driven by Claude Code, run headless with `claude -p` in its own container, authenticated with a token created by `claude setup-token` [QA 1.0010, 3.0030].
- REQ-003: The tested surface is read at run time from the server's registration (`list_tools`, `list_resources`, `list_resource_templates`, `list_prompts`) and from the CLI (`specmgr --help` recursively); a post-run coverage check fails the run if a registered item was never exercised [QA 1.0020, 1.0030].
- REQ-004: The test covers every MCP tool, resource and prompt and every CLI command, including the `similarity` extra (fastembed model), a real PlantUML backend (jar, binary or server, not only the structure-only floor) and the SSE transport in addition to stdio [QA 1.0020, 1.0070].
- REQ-005: The scripted test plan exercises, per whole-body domain, the full lifecycle (create, get, list, update/edit, set_status through the FSM, set_classification, validate, delete), plus i18n variants, references and diagrams, and the main non-raising error results and raising usage errors [QA 1.0040].
- REQ-006: The run has two passes: a fixed, step-by-step scripted test plan committed in the repository (expected result per step), then an exploratory pass in which the agent designs its own tests from the registered surface; exploratory findings are advisory and never fail the run [QA 5.0010, 7.0020].
- REQ-007: The verdict combines the agent's per-function report with deterministic post-run checks (coverage, files on disk, `specmgr lint` over the created documents, expected step results); the run passes only if both agree [QA 1.0060].
- REQ-008: Every run starts from an empty, isolated data directory (`SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR` and every other base-dir variable); the repository's own `docs/` and `.specmgr/` are never read or changed [QA 5.0020].
- REQ-009: The OpenCode part runs in an oc-farm instance (dfch/biz.dfch.LlmOps feat-11, current branch state) started with `launch --mcp-variant test` and the read-only `github-ro` profile, with the local vLLM model `qwen3.8-27b-bf16-896k`; it only checks that the specmgr tools, resources and prompts and the installed commands, agents and skills exist, and invokes nothing [QA 1.0050, 1.0090, 3.0030, 3.0040].
- REQ-010: The Claude token is the only secret in any test container; it is passed with `--env-file` from a `chmod 600` file on the host outside the repository, never as a command-line argument and never baked into an image; no GitHub push token and no PyPI/TestPyPI token is in any test container [QA 6.0010, 9.0010].
- REQ-011: Claude Code runs with `--dangerously-skip-permissions`; the container is the isolation boundary, with an egress allowlist (Anthropic API, PyPI, GitHub, the `sys0` vLLM endpoint, the fastembed model host, and the PlantUML server if one is used) and the hardening `--cap-drop ALL`, `--security-opt no-new-privileges` and memory/CPU/pids limits [QA 6.0020, 6.0030].
- REQ-012: The run produces a terminal pass/fail summary with a non-zero exit code on failure, a `report.md` and a `report.json` per run directory, the full `stream-json` transcript (kept, not committed), and a run record that is committed to compare releases [QA 0.0050, 5.0030].
- REQ-013: The run compares the registered surface with the last PyPI release and lists removed or renamed tools, resources, prompts and CLI commands in the report; a difference never fails the run [QA 1.0080].
- REQ-014: The test is started by hand with a `specmgr` CLI command that is only available when a new dev extra is installed, never in a normal install; it takes the commit or branch to test [QA 0.0010, 4.0010, 7.0010, 7.0030].
- REQ-015: The command has an option to run a single area or domain, streams live progress to the terminal, has no fixed time or cost limit, and records wall time and token usage [QA 2.0010, 2.0020, 4.0020].
- REQ-016: The test works under rootless Docker, with Python 3.13 in the container [QA 3.0010, 3.0020].
- REQ-017: The runner keeps the agent behind one interface, so another agent or model can replace Claude Code later without a redesign [QA 8.0010].

### Acceptance Criteria

- [ ] ACC-001: `specmgr agent-test --ref <commit>` on the dev host (rootless Docker) clones exactly that commit into the container, starts specmgr from it with `uv run --directory`, and the report records the commit SHA and `specmgr://version` of the server under test (REQ-001, REQ-016).
- [ ] ACC-002: In a normal install (`uv sync --extra cli --extra mcp`), `specmgr agent-test` does not exist; with the dev extra it does (REQ-014).
- [ ] ACC-003: The report lists every registered tool, resource, resource template, prompt and CLI command with its result; if one item is removed from the scripted plan, the coverage check fails the run and names that item (REQ-003, REQ-004).
- [ ] ACC-004: The scripted plan covers the lifecycle of all 14 whole-body domains, i18n for the 13 language-aware domains, references and diagrams, and the error results named in REQ-005; the report shows one result per step with expected and actual values (REQ-005, REQ-006).
- [ ] ACC-005: A run against a commit with a deliberately injected defect (e.g. a broken `set_status` transition) fails, and the report names the failing step, the agent's finding and the deterministic check that confirmed it (REQ-007).
- [ ] ACC-006: After a run, the host repository's `docs/` and `.specmgr/` are byte-unchanged, and every document the agent created is in the run's own data directory (REQ-008).
- [ ] ACC-007: The OpenCode part reports the presence of the specmgr tools, resources and prompts and of every installed command, agent and skill of the harness bundle, and records zero tool invocations of the model (REQ-009).
- [ ] ACC-008: `docker inspect` of every test container shows no secret in the command line or the image, only the Claude token in the environment, `CapDrop: [ALL]`, `no-new-privileges` and the resource limits; a request to a host outside the allowlist fails from inside the container (REQ-010, REQ-011).
- [ ] ACC-009: A run writes `report.md`, `report.json` and the transcript, prints the summary, and exits 0 on pass and non-zero on fail; the committed run record contains no transcript and no secret (REQ-012).
- [ ] ACC-010: The report contains the surface diff against the last PyPI release; a run where the diff is not empty still passes if every check passes (REQ-013).
- [ ] ACC-011: `--area <name>` (e.g. one domain, or `cli`) runs only that area and its coverage check; progress lines appear in the terminal while the agent runs; the report records wall time and token usage (REQ-015).
- [ ] ACC-012: The agent driver is one module behind a documented interface; a stub driver used in the unit tests runs the full pipeline without Claude (REQ-017).

### Scope

#### Included

- The `specmgr agent-test` CLI command and the new dev extra that enables it.
- A small Claude Code container image (Python 3.13, uv, Claude Code, PlantUML backend, fastembed model cache) and its egress allowlist.
- The scripted test plan files (per area), the exploratory pass prompt, the surface discovery, the coverage check, the release diff, the deterministic checks, and the report.
- The OpenCode existence check through an oc-farm instance.
- Unit tests with a stub agent driver; one recorded end-to-end run against `dev` HEAD.

#### Explicitly Out Of Scope

- Integration into the release SOP (SOP 98537416) or CI [QA 0.0010, 8.0020].
- Testing the built wheel or sdist; packaging defects stay covered by the TestPyPI check [QA 0.0040].
- Python 3.11 and 3.12; CI covers them with the unit tests [QA 3.0010].
- Rootful Docker and Podman as tested targets (rootful is expected to work, but is not a criterion).
- Changes to oc-farm itself (dfch/biz.dfch.LlmOps feat-11).
- Functional testing through OpenCode; the OpenCode part is an existence check only.

### Dependencies

#### Depends On

- dfch/biz.dfch.LlmOps feat-11 (oc-farm): the image `oc-farm:2.2.5`, `launch --mcp-variant test`, the `github-ro` profile, as on its branch `feat-11` (commit `ff3deb6`); no wait for its merge or Phase 170 [QA 3.0040].
- The local vLLM endpoint on `sys0` for the OpenCode part.
- A Claude subscription token from `claude setup-token`.

#### Blocks

- A later release-SOP or CI integration of this test (not planned).

### Design Notes

Requirements source: QA aed61f42-d131-4188-ac58-66de3cfcf9b8.

Patterns to reuse, not code to import: `evals/c4-skills/` (feat-250, feat-274) for preflight, container user flags under rootless Docker (`--user 0:0`), sequential trials, NDJSON event parsing and the `report.md`/`report.json` split; oc-farm REQ-010/REQ-012/REQ-023 for secrets, mounts and hardening.

Claude Code part, one run: clone `--ref` into a fresh run directory; start the container with the run directory as the only mount; inside, `uv sync --frozen --all-extras` in the checkout, write an MCP config with one `specmgr` stdio entry (`uv run --frozen --directory <checkout> specmgr mcp`) plus one SSE entry, set every `SPECMGR_*_DIR` to an empty directory under the run directory, then `claude -p --output-format stream-json --dangerously-skip-permissions --mcp-config ...` with the scripted plan, then a second call with the exploratory prompt. The host side tees the stream to the terminal (live progress) and to the transcript file, then runs the deterministic checks over the run directory.

Surface discovery: a small MCP client step (stdlib plus the `mcp` package of the checkout) lists the registered surface before the agent runs; the CLI surface comes from `specmgr --help` per command group. The coverage check matches the transcript's tool calls and the plan's step results against that list.

Release diff: the same discovery against the last PyPI release (`uvx --from biz-dfch-specmgr[mcp]==<last>`), run in the container; names only, no result-shape comparison.

Egress allowlist under rootless Docker: firewall rules inside the container need `NET_ADMIN`, which conflicts with `--cap-drop ALL`. The Phase 100 spike decides the mechanism (e.g. an HTTP(S) proxy sidecar on an internal network, with the test container on an `--internal` network).

Dev extra: an extra cannot add or remove modules from a wheel. The command module ships in the wheel, but registers in `cli.py` only when the dev extra's marker dependency is importable (to be decided in Phase 100, see D1/D2).

Open decisions:

- D1 [QA 7.0030]: Where the committed run record goes. A command in the installed package does not know where the repository is, so it cannot pick a committed location by itself. Proposal: `--out` with the default `evals/agent-test/results/` relative to the current directory, and the command refuses to run unless the current directory is a specmgr checkout (a `pyproject.toml` with `name = "biz-dfch-specmgr"`).
- D2: Which dependency the dev extra carries so that its presence can be detected (e.g. `docker` SDK, or no dependency and an explicit environment flag).

### Related Decisions

- DEC e369ee2e-3353-4f92-991c-6367d76d832e: feature folders under `.specmgr/feat/`.
- DEC 9c687bb1-8ee7-41c8-84ec-07606356bc73: local enforcement via pre-commit; this test is manual and not a hook.

### Task List

#### Phase 100: Spike (verify the open facts before building)

- [ ] Task 100.100: Verify `claude -p` headless in a container with the `claude setup-token` token from an env file (variable name, stream-json event shape, MCP config flag, `--dangerously-skip-permissions`), under rootless Docker.
- [ ] Task 100.110: Verify the egress allowlist mechanism under rootless Docker together with `--cap-drop ALL` (proxy sidecar on an `--internal` network or an alternative); record the chosen mechanism.
- [ ] Task 100.120: Verify an oc-farm instance with `launch --mcp-variant test` and the `github-ro` profile on a clone of a given specmgr commit, and how the existence check can list tools, resources, prompts, commands, agents and skills without a model tool call.
- [ ] Task 100.130: Verify the PlantUML backend in the container (jar, binary or server) and the fastembed model download/cache, and the SSE transport reachable from Claude Code in the container.
- [ ] Task 100.140: Decide D1 and D2 with the owner; record them in Decisions Made.

#### Phase 110: Command skeleton and dev extra

- [ ] Task 110.100: Add the dev extra to `pyproject.toml` and the gated registration of `specmgr agent-test` in `cli.py`; normal installs do not show the command (ACC-002).
- [ ] Task 110.110: Implement the options (`--ref`, `--area`, `--out`, `--token-file`) and the preflight (Docker mode, image presence, token file mode `600`, checkout detection per D1), recorded in the run record.
- [ ] Task 110.120: Define the agent driver interface and a stub driver for the unit tests (ACC-012).

#### Phase 120: Claude Code container and runner

- [ ] Task 120.100: Write the Claude Code image (Python 3.13, uv, Claude Code, PlantUML backend, fastembed cache) and its build step.
- [ ] Task 120.110: Implement the run: fresh clone of `--ref`, the single run-directory mount, the empty data directories, the MCP config (stdio and SSE), hardening flags and the egress mechanism from Task 100.110 (ACC-001, ACC-006, ACC-008).
- [ ] Task 120.120: Implement the Claude Code driver: `claude -p --output-format stream-json`, live progress to the terminal, transcript file, wall time and token usage (ACC-011).

#### Phase 130: Surface discovery, coverage and release diff

- [ ] Task 130.100: Implement the surface discovery of the server under test (tools, resources, resource templates, prompts) and the CLI (ACC-003).
- [ ] Task 130.110: Implement the coverage check over the transcript and the step results; a missing item fails the run and is named (ACC-003).
- [ ] Task 130.120: Implement the advisory surface diff against the last PyPI release (ACC-010).

#### Phase 140: Test plan and exploratory pass

- [ ] Task 140.100: Write the scripted test plan files per area (one per whole-body domain, i18n, references/diagrams, general tools, resources, prompts, CLI, similarity, PlantUML, SSE) with an expected result per step and a machine-readable step-result format (ACC-004).
- [ ] Task 140.110: Write the exploratory pass prompt; its findings are reported as advisory (REQ-006).
- [ ] Task 140.120: Implement `--area` selection over the plan files and the coverage check (ACC-011).

#### Phase 150: Verdict and report

- [ ] Task 150.100: Implement the deterministic checks (step results against expectations, files in the run data directory, `specmgr lint` over the created documents, host `docs/` and `.specmgr/` unchanged) and their combination with the agent's report (ACC-005, ACC-006).
- [ ] Task 150.110: Write `report.md`, `report.json`, the terminal summary and the exit code; write the committed run record without transcript or secret (ACC-009).

#### Phase 160: OpenCode existence check

- [ ] Task 160.100: Implement the oc-farm part: launch the instance on the same clone, run the existence check, collect its result into the report, remove the instance (ACC-007).

#### Phase 170: Quality gate, documentation and end-to-end run

- [ ] Task 170.100: Unit tests for every module with the stub driver and mocked Docker; ruff, vulture and the full pytest suite green; `specmgr docs` regenerated.
- [ ] Task 170.110: Document the command (README, AGENTS.md, CHANGELOG `[Unreleased]`), including the token setup and the oc-farm prerequisite.
- [ ] Task 170.120: Run end to end against `dev` HEAD and commit the run record (ACC-001, ACC-003, ACC-004, ACC-007, ACC-008, ACC-009, ACC-010, ACC-011).
- [ ] Task 170.130: Run against a commit with an injected defect and confirm the run fails with the expected finding (ACC-005).

## Progress

### Current Status

**As of 2026-11-26**: Plan created from QA aed61f42-d131-4188-ac58-66de3cfcf9b8 and GitHub issue #277. Nothing is started. Start with Phase 100 (spike). Open decisions D1 and D2 are decided in Task 100.140.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 17:50:00.000Z - Created

Plan created from the requirements interview QA aed61f42-d131-4188-ac58-66de3cfcf9b8 (eight rounds, 2026-11-26) and GitHub issue #277.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 17:50:00.000Z - Feature id feat-277-agent-test

The owner chose the short name `agent-test`; the issue number 277 is the `NNN` infix.

### Related PRs / Commits

- None yet.

### More Information

Interview: `docs/qa/qa-aed61f42-d131-4188-ac58-66de3cfcf9b8-pre-release-agent-acceptance-test-of-specmgr-in-a-container.md`.
