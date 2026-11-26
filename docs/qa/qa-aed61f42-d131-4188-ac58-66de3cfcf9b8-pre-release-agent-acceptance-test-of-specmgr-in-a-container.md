---
classification: null
created: '2026-11-26T17:44:26.354+01:00'
id: aed61f42-d131-4188-ac58-66de3cfcf9b8
status: draft
type: qa
updated: '2026-11-26T18:46:04.997+01:00'
version: 1.0.0
---

# Pre-Release Agent Acceptance Test of specmgr in a Container — Requirements Interview

## General

### Introduction

Requirements interview with the specmgr maintainer, started 2026-11-26.

Today a new specmgr version is tested by hand after it is published to TestPyPI (the *Publish to TestPyPI* job in `.github/workflows/publish.yml`, step of SOP 98537416-0e6e-4a02-925f-974a17bfa10a "Perform a release of biz.dfch.specmgr"). Defects found at that point are found late: the version is already tagged and on an index.

The goal is an agent that tests all specmgr functions in an isolated container against the new, not-yet-released version, before anything is published. This interview collects the requirements for that test. The answers will be the input for a FEAT plan.

### Raw Requirements

From the maintainer, verbatim: "Now, I want an agent to test all functions of the specmgr in a container with the new version BEFORE it is released."

Related existing assets found in the repository and on the host:

- `evals/c4-skills/` (feat-250): a container harness that runs an OpenCode agent in an isolated container, records preflight/run/report artifacts, and grades the result with real tools. Rootless-Docker fix in feat-274 (`--user 0:0`).
- `.specmgr/feat/feat-196-container-sandbox/` (planning): devcontainer sandbox, clone-from-origin, scoped token via environment variable.
- `~/docker/opencode/.config/opencode/opencode.json`: a (commented-out) `specmgr` MCP entry that starts the server from a local checkout with `uv run --directory <checkout> --extra mcp --extra similarity specmgr mcp` — no wheel needed.
- `specmgr://harness-bundle`: the install protocol plus every `.opencode/{agent,command,skill}/` file.
- `biz.dfch.LlmOps`, `feat-11-opencode-container-fleet-parallel-sessions-in-docker` — the OpenCode container fleet ("oc-farm"). State on the upstream branch `origin/feat-11` (commit `ff3deb6`, plan updated 2026-11-26; the local `dev` checkout is outdated). Checked on `sys0` (via `jsys0`) on 2026-11-26: the local `feat-11` branch is at the same commit `ff3deb6`, the image `oc-farm:2.2.5` exists (image id `sha256:01c36052675a…`, built 2026-11-26 02:12), the host CLI is installed at `~/.local/bin/oc-farm`, and no `oc-` container is running. Plan state: status `review`, Phases 100 to 160 complete, Phase 170 (fleet validation, on `sys1`) open, PR to `dev` pending. It ships a typer uv project `oc-farm` (`launch`, `attach`, `ctl`, `archive`/`ingest`/`stats`, `rm`, `gc`), the image `oc-farm:2.2.5` from `docker/Dockerfile.farm` (OC 2.2.5, sha256-checked; published `specmgr`/`asdste100` installed as uv tools), a golden OC config in `config/golden/` (provider `vllm-sys0` → `host.docker.internal:8081`, model `qwen3.8-27b-bf16-896k`), git-host profiles in `config/profiles/` (incl. a read-only `github-ro` profile with an invalid pushurl), a runbook `docs/runbook.md`, and `farm.db` with token usage and tool calls per session. Directly relevant: `config/golden/mcp-test.json` already defines a `specmgr-test` entry (`uv run --frozen --directory /home/oc/src/biz.dfch.SpecMgr specmgr mcp`), enabled by `launch --mcp-variant test` — exactly the pre-release setup. Requirements of its design that match this test: REQ-002 (opt-in `launch --mcp-variant test` adds a `specmgr-test` MCP entry that points into the clone — exactly the pre-release case), REQ-004 (fresh clone per instance, no worktree), REQ-008/REQ-013 (golden OC config, host OC directories never mounted), REQ-010 (secrets only in a `chmod 600` env file or `secrets/` file, never CLI arguments or baked into the image), REQ-012 (only the instance's own run directory is mounted), REQ-018 (OC version pinned, sha256-checked), REQ-019 (`--user`, cf. feat-274's rootless `--user 0:0`), and REQ-023 (resource limits, `--cap-drop ALL`, `no-new-privileges`).

## Elicitation Context

<!-- Elicited 2026-11-26 in the first interview round. -->

> **0.0010**: Who triggers the test, and is it a release gate?

Manual start for now. It is not part of a release SOP yet; integration into the release SOP (SOP 98537416) may come later and is out of scope for this round.

> **0.0020**: Which build of specmgr is the test run against?

The MCP server is loaded with `uv`/`uvx` from a local directory (see the `specmgr` entry in `~/docker/opencode/.config/opencode/opencode.json`), so no wheel and no TestPyPI upload are needed.

> **0.0030**: Is the source directory the developer's working tree (bind mount, possibly with uncommitted changes), or a clean checkout of a given commit/tag/branch (e.g. the release-candidate commit on `dev`)?

<!-- Elicited 2026-11-26 in the second interview round. -->

A clean checkout of a given commit/branch (e.g. the release-candidate commit on `dev`), so uncommitted local changes can neither hide nor cause a defect.

> **0.0040**: Should the test also cover the packaged form (built wheel/sdist installed with `uvx --from <wheel>`), to catch packaging defects such as missing package data (`data/headings/*.json`, harness bundle, templates) that a source-directory run cannot see?

No. Source directory only; packaging defects stay covered by the later TestPyPI check.

> **0.0050**: Who reads the result, and in what form (terminal summary, Markdown report, JSON, a specmgr TXT/VCR document)?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

All of: a terminal pass/fail summary with a non-zero exit code on failure; `report.md` and `report.json` per run directory (as in `evals/c4-skills`); the full agent transcript (`claude -p --output-format stream-json`), kept but not committed; and the run record committed to compare releases (see 5.0030).

## Functional Suitability

<!-- Elicited 2026-11-26 in the first interview round. -->

> **1.0010**: Which agent drives the test?

Claude Code in a Docker container, run headless with `claude -p`, authenticated with a token created by `claude setup-token`.

> **1.0020**: What does "all functions" cover?

All four areas: every MCP tool, every MCP resource and prompt, every CLI command, and the harness install (installing the `.opencode` agents/commands/skills from `specmgr://harness-bundle` into a fresh setup).

> **1.0030**: How is "all" determined and kept complete as the surface grows — derived at run time from the server's own registration (e.g. `list_tools`/`list_resources`/`list_prompts`, `docs/MCP.md`), with a coverage check that fails if a registered tool was never called?

<!-- Elicited 2026-11-26 in the third interview round. -->

From the registration: the surface is read at run time from the server (`list_tools`/`list_resources`/`list_prompts`) and from the CLI (`specmgr --help`). A post-run check fails if a registered item was never exercised.

> **1.0040**: What depth per function: a smoke call per tool, or scenario-based lifecycle tests per domain (create → get → list → update/edit → set_status through the FSM → set_classification → validate → delete), plus i18n variants, references/diagrams, and error paths (invalid id, not-found, `ParseFailureResult`, `ValidateResult`, `InvalidStatusTransitionResult`)?

Lifecycle plus error paths: per domain the full lifecycle (create → get → list → update/edit → set_status through the FSM → set_classification → validate → delete), plus i18n variants, references/diagrams, and the main non-raising error results and raising usage errors.

> **1.0050**: The harness bundle installs OpenCode files (`.opencode/agent`, `command`, `skill`), but the driving agent is Claude Code. How should the harness install be tested: also run OpenCode in the container for that part, only verify the installed files (paths, sha256), or something else?

<!-- Elicited 2026-11-26 in the second interview round. -->

Also run OpenCode in the container, with a free model, to check that the specmgr tools, resources, and the installed commands and skills are available to an OpenCode agent.

> **1.0060**: How is a pass/fail verdict decided: by the agent's own judgment, by deterministic checks after the run (files on disk, `specmgr lint`, expected outputs), or both?

Both: the agent reports a per-function result, and deterministic post-run checks (coverage of the registered surface, files on disk, `specmgr lint`) confirm it.

> **1.0090**: Which free model does the OpenCode part use (e.g. an OpenCode-hosted free model, or the local vLLM model on sys0), and what is the minimum check: tools/resources listed, or one command and one skill actually invoked?

<!-- Elicited 2026-11-26 in the fourth interview round. -->

The local vLLM model `qwen3.8-27b-bf16-896k` on `sys0`, as in the oc-farm golden config: no cost, no external account.

<!-- Elicited 2026-11-26 in the fifth interview round. -->

The OpenCode part must only identify that the specmgr tools and resources, and the installed commands, agents, and skills, exist. Nothing is invoked; the functional test is the Claude Code part.

> **1.0070**: Should optional features be tested too: the `similarity` extra (`find_related`/`find_similar_text`, needs the fastembed model download), PlantUML validation with a jar/bin/server backend, and the SSE transport of `specmgr mcp`?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

All three are in scope: the `similarity` extra with the fastembed model, a real PlantUML backend (jar, binary, or server — not only the structure-only floor), and the SSE transport in addition to stdio.

> **1.0080**: Should the agent compare against the previous released version (e.g. detect a removed or renamed tool, changed result shape) and report it as a breaking change?

Yes, as advisory: the run compares the registered surface with the last PyPI release and lists removed or renamed tools, resources, prompts, and CLI commands in the report. A difference does not fail the run.

## Performance Efficiency

> **2.0010**: What is the acceptable wall time and cost (Claude usage) for one full run?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

No fixed limit: the run goes to completion. Wall time and token usage are recorded in the report.

> **2.0020**: Should the run be splittable (e.g. one domain or one area at a time) so a failed part can be repeated alone?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

Yes: a run option selects a single area or domain (e.g. one domain, or only the CLI) to repeat after a failure.

## Compatibility

> **3.0010**: Which Python versions must be tested in the container (3.11 only as the minimum, 3.13 as the dev default, or the full 3.11–3.13 CI matrix)?

<!-- Elicited 2026-11-26 in the fifth interview round. -->

Python 3.13 only, the dev default and the oc-farm image version. CI already covers 3.11–3.13 with the unit tests.

> **3.0020**: Must the container run under rootless Docker (as on the dev host, see feat-274), rootful Docker, or both? Is Podman in scope?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

It must work under rootless Docker, as on the dev host (see feat-274). Podman was not requested.

> **3.0030**: Which base image: reuse `~/docker/opencode/Dockerfile` (Alpine, OpenCode, uv), the LlmOps feat-11 oc-farm image `oc-farm:2.2.5` (built, feat-11 in `review`), a new image in this repo, or the feat-196 devcontainer? If oc-farm: is a `launch --mcp-variant test` instance with the read-only `github-ro` profile the OpenCode part of this test, and does Claude Code (`claude -p`) get added to the oc-farm image, or run in a second image? Should this test wait for feat-11 to be merged and its Phase 170 to pass?

<!-- Elicited 2026-11-26 in the fourth interview round. -->

oc-farm for the OpenCode part: an instance started with `launch --mcp-variant test` and the read-only `github-ro` profile. Claude Code (`claude -p`) runs in a second, small image of its own; the oc-farm image is not changed.

> **3.0040**: Does this test wait for feat-11 to be merged and its Phase 170 (fleet validation) to pass, or may it use the `feat-11` branch state as it is now?

<!-- Elicited 2026-11-26 in the fifth interview round. -->

It uses the current `feat-11` branch state and image now; it does not wait for the merge or for Phase 170. The pre-release test needs one instance, not the fleet that Phase 170 validates.

## Interaction Capability

> **4.0010**: How is the run started — a script in this repo (e.g. `scripts/prerelease-test.sh`), a `specmgr` CLI command, or an OpenCode/Claude command?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

A `specmgr` CLI command, started by hand with the commit/branch to test.

> **4.0020**: Should progress be visible during the run (streamed agent output), or only the final report?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

Live progress: the agent's progress is streamed to the terminal while it runs, in addition to the final report.

## Reliability

> **5.0010**: Agent runs are not deterministic. How should flaky results be handled — retries, several trials, or a deterministic test plan the agent only executes?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

Scripted plus exploratory: first a fixed, step-by-step test plan in the repository (expected result per step), which the agent executes and records; deterministic checks verify it afterwards. Then an exploratory pass in which the agent designs its own tests from the registered surface; its findings are advisory.

> **5.0020**: Must each run start from an empty, isolated specmgr data directory (`SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`), so that the repository's own `docs/` and `.specmgr/` are never read or changed?

<!-- Elicited 2026-11-26 in the third interview round. -->

Yes. Every run starts from an empty, isolated data directory; the agent creates every test document itself.

> **5.0030**: Should the run results be kept (committed, like `evals/c4-skills/results/`) to compare releases over time?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

Yes. The run record (report, verdicts, environment) is committed; the full transcript is not.

## Security

> **6.0010**: How is the `claude setup-token` token passed into the container (environment variable, Docker secret, file mount), and where is it stored on the host?

<!-- Elicited 2026-11-26 in the fourth interview round. -->

As oc-farm REQ-010: a `chmod 600` env file on the host, outside the repository, passed with `--env-file`. The token is never a command-line argument and never baked into an image.

> **6.0020**: Which network access does the container get — only the Anthropic API, plus PyPI for `uv` dependency resolution, plus the fastembed model download? Should egress be restricted (as in feat-196's optional restricted mode)?

Egress is restricted to an allowlist: the Anthropic API, PyPI (`uv` resolution), GitHub (clone), the `sys0` vLLM endpoint, and the fastembed model host. The container also gets the oc-farm REQ-023 hardening: `--cap-drop ALL`, `--security-opt no-new-privileges`, and memory/CPU/pids limits.

> **6.0030**: Is the agent allowed to run with all permissions inside the container (e.g. `--dangerously-skip-permissions`), given that the container is the isolation boundary?

Yes. Claude Code runs with `--dangerously-skip-permissions`; the container is the isolation boundary.

## Maintainability

> **7.0010**: Where does the test live — next to `evals/c4-skills/` (e.g. `evals/prerelease/`), sharing its preflight/report code, or as a separate tool?

<!-- Elicited 2026-11-26 in the sixth interview round. -->

As a `specmgr` CLI command in the package (see also 4.0010 and 7.0030).

> **7.0030**: A CLI command ships to every user of the wheel. Should it be hidden or marked dev-only, which extra does it need (it needs Docker and the oc-farm image, which users do not have), and where do the committed results go — e.g. `evals/prerelease/results/` or `.specmgr/`?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

A separate dev extra: the command is only present when that new extra is installed, never in a normal install. Where the committed results go is still open.

> **7.0020**: Is the agent's test plan a fixed prompt file in the repository, generated from the registered surface, or both (a fixed scenario part plus a generated coverage part)?

<!-- Elicited 2026-11-26; derived from 1.0030 and 5.0010. -->

Both: a fixed scenario plan in the repository (5.0010) plus the coverage list generated at run time from the registered surface (1.0030).

## Flexibility

> **8.0010**: Should the same harness later be able to run with another agent/model (OpenCode with the local vLLM model on sys0), or is Claude Code the only target?

<!-- Elicited 2026-11-26 in the seventh interview round. -->

Claude Code is the only target now, but the runner is designed so that another agent/model can replace it later.

> **8.0020**: Should the harness later be callable from the release SOP and from CI without redesign?

<!-- Elicited 2026-11-26 in the eighth interview round. -->

Out of scope.

## Safety

> **9.0010**: Must the test be guaranteed never to publish, tag, push, or change anything outside the container (no PyPI/TestPyPI/GitHub credentials in the container)?

<!-- Elicited 2026-11-26 in the fourth interview round. -->

Yes. No GitHub push token and no PyPI/TestPyPI token are in any test container; the clone uses a read-only or public URL. The only secret in the container is the Claude token.

## More Information

Seven interview rounds on 2026-11-26. Still open: 7.0030 (where the committed results go — a dev extra inside the package cannot hold them) and 8.0020 (later use from the release SOP and CI; out of scope now per 0.0010). Next step: a FEAT plan built from this QA.
