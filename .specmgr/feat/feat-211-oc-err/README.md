---
classification: null
created: '2026-10-31T13:32:45.409+01:00'
id: feat-211-oc-err
status: done
type: feat
updated: '2026-10-31T15:54:26.576+01:00'
version: 1.0.0
---

# Feature: Re-verify MCP isError:true Truncation on OpenCode 2.x (anomalyco/opencode#47740)

## Plan

### Overview

GitHub issue #211 tracks a re-verification obligation: [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740) documented that OpenCode 1.x (reported on 1.18.29; the original local reproduction behind ADR 519d1206 was on 1.18.27) drops the content of a failed MCP tool result -- the model only receives a bare `Error executing tool <name>`, discarding the real error text the server put in `content[].text`. This defect is the reason this repo built the non-raising structured-result workaround chain (ADR 519d1206, extended by b399f1ce, 9080b37c, b8c9bfea, f14f125e) instead of simply raising informative exceptions everywhere. Upstream closed #47740 on 2026-10-11 because OpenCode 2.0 shipped and 1.x triage stopped; the closure is a triage action, not a fix, and the maintainers asked for a reopen (or a new issue citing the 2.x version) if the defect still reproduces on 2.0+. This feature re-runs that repro against OpenCode 2.x container images only (OpenCode 1.x is no longer used by this project and is not tested), records the evidence, and acts on the result (comment on upstream and close #211 if fixed; file a new upstream issue if not) -- and separately assesses whether the ADR 519d1206 non-raising workaround chain itself can now be retired.

### Requirements

- REQ-001: Pull and use the newest published `ghcr.io/anomalyco/opencode` 2.x image tag available at run time, and also record the pre-existing local `ghcr.io/anomalyco/opencode:2.0.32` image as a baseline comparison point; record each image's tag and repository digest, and if both resolve to the same digest, treat them as one image and record the equality.

- REQ-002: Run the repro against two MCP server variants: the published `biz-dfch-specmgr[mcp]==0.23.0` package, run with `mcp` pinned to `2.0.0` so that its wire text matches the original #47740 report (0.23.0 only requires `mcp>=2.0.0`, and `mcp` 2.1.0 and later swallow the handler's message before it reaches the wire), and this repo's current dev checkout (which carries the feat-221/ADR 80305c52 `call_tool` seam shim, so its wire text differs from the original report by the missing `Error executing tool <name>: ` prefix). For every variant, record the exact server command line, the resolved `mcp` version, and the server version and commit.

- REQ-003: Re-run all five rows of the #47740 repro table (not just row 1) for each image x server pair, plus a raw MCP Inspector call per server as the ground-truth baseline each OpenCode run is compared against; a baseline for rows 1, 3, 4 and 5 that is not the full server message (for example a bare `Error executing tool <name>`) invalidates that server variant's cells and must be fixed before any verdict is given.

- REQ-004: Drive each OpenCode run headlessly (`opencode run`) inside the container, using the opencode/zen integrated provider (or a recorded fallback provider), and capture the exact commands, image digests, provider and model, and raw outputs as evidence; the captured output is the raw tool result taken from the JSON event stream, not the model's prose.

- REQ-005: Produce a single pass/fail verdict with one fixed rule: a cell passes if the tool error visible to OpenCode for each `isError: true` row (1, 3, 4, 5) contains the Inspector baseline's full `content[].text` message verbatim, either exactly or after an `Error executing tool <name>: ` prefix. The defect counts as fixed only if every cell passes for both server variants; any failing cell means the defect is still present. A verdict against a real image/server pair is required, not an assumption.

- REQ-006: Based on the verdict, perform the appropriate upstream/issue action. anomalyco/opencode#47740 is already closed by a maintainer: if fixed, comment on it with the evidence but do not try to close or reopen it, and close dfch/biz.dfch.SpecMgr#211; if still present, file a new upstream issue citing the tested OpenCode 2.x version and linking #47740 (reopening may not be possible for the author), and keep #211 open.

- REQ-007: Write up a short assessment of whether the ADR 519d1206 non-raising-structured-result workaround chain can now be retired, as input to a separate, later follow-up feature -- this feature does not perform any such retirement itself.

### Acceptance Criteria

- [x] ACC-001: The pulled image's tag and repository digest and the local baseline image's digest are both recorded in this feature's evidence, including the note that the two are one image if their digests are equal.

- [x] ACC-002: A completed 5-row x 2-image x 2-server repro matrix (20 cells, or 10 if the two images are identical) exists, each cell holding the command run and the raw tool result, plus the per-server MCP Inspector baseline output for all five rows.

- [x] ACC-003: The verdict (fixed / still present) is stated explicitly, applies the REQ-005 rule, and is justified by the matrix in ACC-002, not asserted without evidence.

- [x] ACC-004: The appropriate upstream action (comment-only if fixed, new issue if still present) has been taken on or for anomalyco/opencode#47740, and dfch/biz.dfch.SpecMgr#211 has been updated (comment, and closed if fixed), with both links recorded in this feature's Related PRs / Commits.

- [x] ACC-005: A written assessment of whether the ADR 519d1206 chain can be retired is present in this feature's More Information, covering the inputs listed in the Design Notes, including which specific tools/call sites it would affect if retirement were pursued.

- [x] ACC-006: The evidence records, per server variant, the exact server command line, the resolved `mcp` version, the server version and commit, and the Inspector baseline check for rows 1, 3, 4 and 5 (REQ-002, REQ-003).

- [x] ACC-007: The evidence records, per cell, the exact `opencode run` invocation, the OpenCode version, the provider and the model (REQ-004).

### Scope

#### Included

- Pulling/using the newest `ghcr.io/anomalyco/opencode` 2.x image and the existing local 2.0.32 image.

- Configuring and running both named MCP server variants headlessly inside the container, against sandboxed documents only.

- Running and recording the full 5-row repro matrix plus the Inspector baselines.

- Taking the resulting upstream/#211 close-out action.

- Writing the ADR 519d1206 chain retirement assessment (assessment only, no code change).

#### Explicitly Out Of Scope

- Any change to this repo's server code, tools, or the `call_tool` seam shim (feat-221/ADR 80305c52) -- this feature only observes and records behavior.

- Actually retiring any part of the ADR 519d1206 non-raising workaround chain -- tracked as a separate, later follow-up feature if the assessment (REQ-007/ACC-005) recommends it.

- Verifying OpenCode 1.x behavior, including as a positive control: this project no longer uses OpenCode 1.x, and the 1.x behavior is already established and documented by the original #47740 report and FEAT feat-103-set-status-error.

- Testing any MCP server other than this repo's `specmgr` server.

### Dependencies

#### Depends On

- None.

#### Blocks

- A future follow-up feature to retire part or all of the ADR 519d1206 non-raising workaround chain, contingent on this feature's REQ-007/ACC-005 assessment.

### Design Notes

Why the `mcp` pin matters: two different defects produce a similar symptom. The original defect is client-side: the server sends `isError: true` with the full message and OpenCode 1.x drops it before the model sees it. The `mcp` 2.1.0 behavior (upstream #3314, ADR 80305c52) is server-side: the SDK wraps a raised handler exception as `Error executing tool <name>` and discards the handler's message, so the text never goes on the wire. A server on `mcp` 2.1.0 or later without a shim therefore gives a lossy Inspector baseline too, OpenCode would trivially "match" it, and the cell would say nothing about the client. The 0.23.0 variant must therefore pin `mcp==2.0.0` (for example `uvx --from "biz-dfch-specmgr[mcp]==0.23.0" --with mcp==2.0.0 specmgr mcp`, or `--exclude-newer` set to a date before 2.1.0), and the dev-checkout variant is valid because the feat-221 shim restores the message. The `mcp` 2.1.0 change is not a fix of the original defect; whether OpenCode 2.x still drops the text is exactly what this feature measures.

Repro matrix shape: 2 images (`ghcr.io/anomalyco/opencode:2.0.32` baseline, newest published 2.x tag) x 2 MCP server variants (the pinned 0.23.0 package and the dev checkout via `uv run --frozen --extra cli --extra mcp --directory`) x 5 repro rows = 20 OpenCode-run cells, plus one MCP Inspector baseline call per server (2 baselines x 5 rows = 10 reference outputs) that every OpenCode cell is compared against. If the two images share a digest the matrix is 10 cells.

The five repro rows (taken from #47740; `UUID` is the id of a real requirement document created in the sandbox directory beforehand, and the rows use the literal arguments below):

- Row 1: `get_req(id="./non-existing-file.txt")` -- expected `isError: true`.

- Row 2: `set_status(id=UUID, type="req", status="bogus-status")` -- expected `isError: false` (structured `InvalidStatusResult`), the control row; it is excluded from the pass rule.

- Row 3: `set_status(id="deadbeef-dead-dead-dead-deadbeefdead", type="req", status="draft")` -- expected `isError: true` (not found).

- Row 4: `set_status(id="./non-existing-file.txt", type="req", status="draft")` -- expected `isError: true` (invalid id).

- Row 5: `set_status(id=UUID, type="req", status="draft", superseded_by="x")` -- expected `isError: true` (`superseded_by` misuse).

Baseline method: run `npx @modelcontextprotocol/inspector --cli <server command> --method tools/call --tool-name <tool> --tool-arg <k=v> --format json` (the form used in #47740) once per server and row, store the raw JSON unmodified, and judge the baseline by `content[].text` and `isError` in that raw JSON. The Inspector is a reference for what the server put on the wire; it is not the system under test.

Expected-text caveat: the dev-checkout server's wire text is expected to differ from the original 0.23.0 report even on an unfixed OpenCode, because feat-221/ADR 80305c52's `SpecMgrServer.call_tool` seam already re-raises `UnexpectedToolError.__cause__`, which strips the `Error executing tool <name>: ` prefix. The REQ-005 rule therefore compares against each server's own Inspector baseline and tolerates only that prefix, not a byte-for-byte match against the original issue's quoted output.

Headless run approach (verified by a probe on 2.0.32, see Updates): `opencode run --standalone --auto --format json -m opencode/big-pickle "<prompt>"` inside the container. The built-in `opencode` provider needs no login or credentials from inside the container (`opencode models --standalone` lists 12 free `opencode/*` models). `--standalone` is required (a private server instead of the background service) and `--auto` auto-approves the tool permission. The MCP server is attached by a project-level `opencode.json` in the working directory, in the 2.x shape `{"mcp": {"servers": {"<name>": {"type": "local", "command": [...], "environment": {...}}}}}` (not the 1.x `mcp.<name>` shape, which is silently ignored); the `OPENCODE_CONFIG` variable did not attach the server, and `opencode mcp list` reports "No MCP servers configured" even when the server attaches, so neither is a usable check. In 2.x the model does not see MCP tools as individual tools: it calls them from one `execute` code tool as `tools.<server>.<tool>({...})`, and a failed call surfaces as a thrown exception whose `message` is the server's error text. The JSON event stream (`type: "tool_use"`, `part.state`) records the `execute` wrapper's `output` and, in `metadata.toolCalls[]`, only the nested call's `status` (`error`) and `input`, not the error text, so the raw message is observable only through the code the model runs. The prompt therefore must instruct the model to run exactly one `try { await tools.<server>.<tool>({...}) } catch (e) { return "ERROR: " + e.message }` call with the literal arguments, with no retry and no corrected arguments, and the cell records the `execute` `output` and `content[].text` from the stream, not the assistant's prose. Because model behavior is not deterministic, run each cell three times and record all three; a cell passes only if all three runs pass on the REQ-005 rule. Provider and model are recorded per cell; `opencode/big-pickle` is the default, and another free `opencode/*` model is the fallback.

Container prerequisites (verified on 2.0.32): the stock image is Alpine (musl), runs as root and contains none of `uv`, `uvx`, `node`, `npx`, `python3` or `curl`, so the host's glibc `uv` does not run in it. Mount a static musl `uv` (for example `uv-x86_64-unknown-linux-musl` from the `astral-sh/uv` release, which downloads a musl CPython on first run). The Inspector needs Node, so the baseline runs on the host or in a separate container, not in the OpenCode image. The dev-checkout command must be `uv run --frozen --extra cli --extra mcp --directory /work specmgr mcp`, not `--all-extras`: the `similarity` extra pulls `onnxruntime`, which has no musllinux wheel, so `--all-extras` fails to resolve (similarity is disabled anyway through `SPECMGR_SIMILARITY_DISABLED`; `SPECMGR_FEAT_WARMUP_DISABLED` is set too). `specmgr mcp` needs the `cli` extra as well as `mcp`. The editable build writes `egg-info` into the project directory, so mount a throwaway copy of the tracked files (not the worktree, and not read-only) at `/work`. Persist three things in mounted directories, or the venv breaks between container runs: `UV_CACHE_DIR`, `UV_PROJECT_ENVIRONMENT` and `UV_PYTHON_INSTALL_DIR` (the venv's interpreter otherwise lives in the ephemeral `/root/.local/share/uv`, and the server then exits at start with a dangling `/venv/bin/python3`). Both servers run against sandboxed, empty `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`/`SPECMGR_ADR_DIR` directories (with only the one requirement document for rows 2 and 5), so no `set_status` call can touch real documents. Untested so far: the published 0.23.0 variant (`uvx --with mcp==2.0.0`) under musl.

Evidence location and hygiene: the raw matrix, baselines, commands and digests go into a sibling `evidence.md` in this feature folder (thirty or more raw outputs would bloat this README); only this README may cite it, since nothing in `src/`, `tests/` or `AGENTS.md` may cite a feature-folder sibling file. The verdict and the retirement assessment live in this README's More Information. Redact provider tokens, credentials and account identifiers from every captured output. Also record the dev checkout commit SHA (at planning time `4ebdc6c`, server 0.37.0, `mcp` 2.3.0), and the `docker`, `uv`, `uvx` and `npx` versions. The pre-existing local baseline image is `ghcr.io/anomalyco/opencode:2.0.32`, digest `sha256:02998f912cc8bf84ce20ff9d9faa33225406c52f9d13f8f86b376490f1e28813` (confirmed locally at planning time).

Retirement assessment inputs (REQ-007): the sites of the chain -- the generic `validate` tool (ADR 519d1206), `set_status`'s `InvalidStatusResult` (ADR b399f1ce), `get_<d>`'s `ParseFailureResult` (ADR 9080b37c), `update`/`edit`/`set_status`/`set_classification`'s `ParseFailureResult` and `ValidateResult` channels (ADR b8c9bfea), and `create_<d>`/`parse_<d>`'s `ValidateResult` (ADR f14f125e); the raise sites ADR 80305c52 deliberately kept; the Python-level contracts, tests, prompts, skills and `AGENTS.md` text that depend on the structured results; and other MCP clients, since ADR 519d1206 notes the defect is not OpenCode-only, so a verdict on OpenCode 2.x alone is necessary but not sufficient to justify retirement.

### Related Decisions

- ADR 519d1206-4d2a-4500-9046-6db635209996 (Design validate as a non-raising, structured-result tool to work around this exact OpenCode defect): the chain this feature's verdict may allow retiring.

- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (Extend the non-raising workaround to set_status's invalid-status case): part of the same chain.

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (Extend the non-raising workaround to the `get_<d>` parse-failure case): part of the same chain.

- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (Extend the non-raising workaround to update/edit's content-validation case): part of the same chain.

- ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e (Extend the non-raising workaround to the `create_<d>`/`parse_<d>` content-validation case): part of the same chain.

- ADR 80305c52-102e-4833-a233-3468bef29e11 (Preserve caller-visible tool error text across mcp >= 2.1.0 via a call_tool seam): the shim that changes the dev checkout's expected wire text for this repro, and explicitly scoped itself as preserving the status quo on issue #211 rather than resolving it.

### Task List

#### Phase 100: Prepare the Test Environment

- [x] Task 100.100: Pull the newest published `ghcr.io/anomalyco/opencode` 2.x image tag and record its tag and repository digest alongside the pre-existing local `ghcr.io/anomalyco/opencode:2.0.32` image's digest, noting if they are equal (REQ-001, ACC-001).

- [x] Task 100.110: Prepare the container prerequisites and sandboxed `SPECMGR_*_DIR` directories described in the Design Notes, and record the dev checkout commit SHA and the `docker`, `uv`, `uvx` and `npx` versions (REQ-002, ACC-006).

- [x] Task 100.120: Configure the container's OpenCode `mcp` entries for both server variants (published `biz-dfch-specmgr[mcp]==0.23.0` with `mcp==2.0.0` pinned via `uvx`, and this repo's current dev checkout via `uv run --frozen --extra cli --extra mcp --directory`), record the resolved `mcp` version for each, and write the project-level `opencode.json` (2.x `mcp.servers` shape) and the built-in `opencode` provider model (or a recorded fallback) for headless `opencode run --standalone --auto` use (REQ-002, REQ-004, ACC-006, ACC-007).

#### Phase 110: Run and Record the Repro Matrix

- [x] Task 110.100: For each MCP server variant, run the five #47740 repro calls directly via MCP Inspector, record the raw JSON output as the ground-truth baseline, and check that rows 1, 3, 4 and 5 carry the full server message; stop and fix the variant if they do not (REQ-003, ACC-002, ACC-006).

- [x] Task 110.110: For each image x server variant combination (4, or 2 if the images are identical), run `opencode run` headlessly three times for all five repro rows, capturing the raw tool result from the JSON event stream, and record the exact prompt/command, OpenCode version, provider and model for each (REQ-004, ACC-002, ACC-007).

- [x] Task 110.120: Assemble the full matrix plus the 10 baseline rows into this feature's `evidence.md`, with credentials redacted, and state the explicit pass/fail verdict under the REQ-005 rule with justification in More Information (REQ-005, ACC-002, ACC-003).

#### Phase 120: Close Out

- [x] Task 120.100: Based on the verdict, comment with the evidence on anomalyco/opencode#47740 if fixed (comment only; it is already closed), or file a new upstream issue citing the tested 2.x version and linking #47740 if still present (REQ-006, ACC-004).

- [x] Task 120.110: Comment on dfch/biz.dfch.SpecMgr#211 with the verdict and the upstream action taken, closing #211 if the defect is fixed (REQ-006, ACC-004).

- [x] Task 120.120: Write the ADR 519d1206 chain retirement assessment (which tools/call sites would be affected, and whether retirement is recommended) into this feature's More Information, covering the inputs listed in the Design Notes (REQ-007, ACC-005).

## Progress

### Current Status

**As of 2026-10-31**: Phases 100 and 110 are done. The matrix ran on both images, 2.0.32 and the newest published 2.x, 2.2.5, with both server variants, 5 rows and 3 valid runs per cell, on the local vLLM model (accepted for this verdict). Under the REQ-005 rule the defect did not reproduce: 48 of 48 valid runs of the four `isError: true` rows returned the server's full message to OpenCode (verdict in More Information, raw results in `evidence.md`). The close-out is done (comment on anomalyco/opencode#47740, comment on and closure of #211) and the retirement assessment is written (More Information). The feature is done.

### Blockers

- None. All three phases are done; the follow-up feature that would retire part of the chain is not started and is contingent on the assessment in More Information.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 14:54:21.000Z - Close-out done, assessment written, feature done

Posted the verification result with the full `evidence.md` (redacted: no tokens or credentials, internal host name and endpoint removed) as a comment on the already-closed anomalyco/opencode#47740 (comment only). Commented on and closed dfch/biz.dfch.SpecMgr#211. Wrote the retirement assessment (More Information): do not retire the ADR 519d1206 chain on this result alone. Set the feature to `done`.

#### 2026-10-31 14:43:00.000Z - Matrix on the newest 2.x image (2.2.5) complete; defect not reproduced

Pulled the newest published 2.x image, `ghcr.io/anomalyco/opencode:2.2.5` (digest `sha256:1690aad69864d2f6714772d1e040918feebc6df5286d2bd7e181fbb35d12d4a9`; highest semver of 3362 registry tags). `latest` is v1.19.5, a 1.x build, so it is not the newest 2.x and was not tested. The two images have different digests. Reran the full matrix on 2.2.5 with the unchanged harness and model (local vLLM `qwen3.8-27b-bf16-896k`, accepted as the provider): both variants, rows 1 to 5, 3 valid runs per cell. Rows 1, 3, 4, 5 pass in 24 of 24 valid runs and the row 2 control in 6 of 6; one run that never reached the server (a model quoting mistake) was excluded and rerun. Together with 2.0.32 that is 48 of 48 valid passes, so under the REQ-005 rule the defect is not reproduced on either image. No GitHub action has been taken yet. See `evidence.md`.

#### 2026-10-31 14:20:27.000Z - Matrix on 2.0.32 complete: all valid runs pass (partial, not the final verdict)

Ran the full matrix on `ghcr.io/anomalyco/opencode:2.0.32` (opencode v2.0.32) on a local vLLM instance (`qwen3.8-27b-bf16-896k`) as a custom OpenAI-compatible provider, after the built-in provider's free quota ran out. Both server variants (dev checkout with the feat-221 shim; published 0.23.0 with `mcp==2.0.0`), 5 rows, 3 valid runs per cell. Prompt: two separate `execute` calls, discovery then one `try/catch` call; the raw `execute` output is the capture (this fixed the earlier `Unknown tool` failures). Result under the REQ-005 rule: rows 1, 3, 4, 5 pass in 24 of 24 valid runs (the `dev` variant without the `Error executing tool <name>: ` prefix, the `old` variant with it), and the row 2 control returned its structured result in 6 of 6. Three runs that never reached the server were model mistakes and were excluded and rerun, not counted as passes or failures. Limits: only image 2.0.32, one local open-weight model, and the error text is observed as the exception message inside the 2.x `execute` code sandbox. So on this image the defect from #47740 did not reproduce, but the verdict required by the plan (newest 2.x image too) is still open. No GitHub action was taken. See `evidence.md`.

#### 2026-10-31 14:02:38.000Z - Baselines done, matrix blocked (no verdict)

Ran the Inspector baselines for both variants on the host: both are valid (rows 1, 3, 4, 5 carry the full message with `isError: true`, row 2 is `isError: false`; the pinned 0.23.0 variant resolved to specmgr 0.23.0 with `mcp` 2.0.0 and shows the original `Error executing tool <name>: ` prefix, the dev variant does not). The published 0.23.0 variant also starts under musl in the container via `uv tool run`. The OpenCode matrix on 2.0.32 (2 variants x 5 rows x 3 runs, `opencode/big-pickle`) was started but is not usable: only 3 of 30 runs reached the server (all 3 matched their baseline, which is no basis for a verdict), the rest got `Unknown tool 'specmgr.<tool>'` from the code sandbox, and after about 40 runs the built-in provider returned `Free usage limit reached` for every free model. Neither outcome says anything about whether OpenCode 2.x truncates `isError: true` content. Raw baselines and the run notes are in the sibling `evidence.md`. The newest 2.x image was not pulled. The matrix, the verdict and the close-out tasks are still open.

#### 2026-10-31 13:31:49.000Z - Feasibility probe on 2.0.32 (not a verdict)

Probed the local `ghcr.io/anomalyco/opencode:2.0.32` image (opencode v2.0.32, digest `sha256:02998f912cc8bf84ce20ff9d9faa33225406c52f9d13f8f86b376490f1e28813`) to remove the provider blocker. Findings: the built-in `opencode` provider works in the container with no login (model `opencode/big-pickle` answered a test prompt at zero cost); the stock image is Alpine/musl with no `uv`, `node` or `python3`; the dev checkout (specmgr 0.37.0, `mcp` 2.3.0, commit `4ebdc6c`) starts in the container with a mounted musl `uv` and `--extra cli --extra mcp` (not `--all-extras`) and attaches through a project-level `opencode.json` in the 2.x `mcp.servers` shape; the 1.x shape and `OPENCODE_CONFIG` did not attach it. One single-run probe of row 1 (`get_req` with `./non-existing-file.txt`) against the dev server returned the server's full message to the model (`id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`), with the nested call marked `status: error`. This is one run of one cell with no Inspector baseline, and it does not satisfy REQ-003 or REQ-005, so it is not evidence for either outcome. It does show that in 2.x the model calls MCP tools through an `execute` code tool and reads a failure as a thrown exception, which changes the capture method (see Design Notes). The matrix was not run.

#### 2026-10-31 12:53:20.000Z - Plan refined

Plan refined after a review of the plan and its reference graph. The 0.23.0 variant now pins `mcp==2.0.0` (a newer `mcp` swallows the message server-side and would make the test meaningless); the pass rule is a single fixed rule (REQ-005); the #47740 close-out is comment-only or a new issue, since #47740 is already closed; OpenCode 1.x is out of scope, including as a positive control; and the repro rows, baseline and capture methods, container prerequisites, evidence location and retirement-assessment inputs are specified. Implementation has not started.

#### 2026-10-31 00:00:00.000Z - Created

Feature created from dfch/biz.dfch.SpecMgr#211 to re-verify anomalyco/opencode#47740 against the newest OpenCode 2.x container image. Plan covers a 2-image x 2-server x 5-row repro matrix plus Inspector baselines, the resulting upstream/#211 close-out action, and a written assessment of whether the ADR 519d1206 non-raising workaround chain can be retired. Implementation has not started.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 12:53:20.000Z - Pin mcp for the 0.23.0 variant

The published 0.23.0 variant runs with `mcp==2.0.0` pinned, because 0.23.0 only requires `mcp>=2.0.0` and `mcp` 2.1.0 and later swallow the handler's message server-side, which would make the baseline lossy and the OpenCode comparison meaningless.

#### 2026-10-31 12:53:20.000Z - One fixed pass rule

A cell passes if the OpenCode-visible tool error contains the Inspector baseline's full message verbatim, with or without the `Error executing tool <name>: ` prefix; the defect is fixed only if every cell passes for both server variants. The rule is fixed before any run, so the verdict cannot be decided after the fact.

#### 2026-10-31 12:53:20.000Z - OpenCode 1.x not tested

No OpenCode 1.x positive control is run, because this project no longer uses OpenCode 1.x and only the behavior on 2.x matters.

#### 2026-10-31 12:53:20.000Z - Evidence in a sibling file

Raw outputs go into a sibling `evidence.md` in this feature folder, while the verdict and the retirement assessment stay in this README's More Information.

### Related PRs / Commits

- [Issue #211](https://github.com/dfch/biz.dfch.SpecMgr/issues/211): the tracking issue this feature addresses.

- [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740): the original upstream defect report being re-verified (closed by a maintainer on 2026-10-11).

- [Comment on anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740#issuecomment-6544950479): the verification result with the full redacted evidence (comment only; the issue was already closed).

- [Comment on #211](https://github.com/dfch/biz.dfch.SpecMgr/issues/211#issuecomment-6544990729): the verdict and the upstream action; #211 closed with it.

- [Issue #204](https://github.com/dfch/biz.dfch.SpecMgr/issues/204): related non-raising-workaround-chain tracking issue referenced by #211.

- FEAT feat-103-set-status-error: the feature that originally filed anomalyco/opencode#47740.

- FEAT feat-204-create-error: an earlier extension of the non-raising workaround chain.

- FEAT feat-221-mcp-220-error-contract: added the `call_tool` seam shim (ADR 80305c52) that changes this repo's dev-checkout wire text for this repro.

### More Information

#### Verdict (Task 110.120, REQ-005, ACC-003)

**Not reproduced ("fixed" under the REQ-005 rule) on OpenCode 2.0.32 and on the newest published 2.x image, 2.2.5.** The rule: for each `isError: true` row (1, 3, 4, 5) the OpenCode-visible tool error must contain the Inspector baseline's full `content[].text` verbatim, exactly or after the `Error executing tool <name>: ` prefix, for both server variants. Result: 48 of 48 valid runs pass (2 images x 2 variants x 4 rows x 3 runs), none failed; the row 2 control returned its structured result in 12 of 12. Both Inspector baselines were valid first (full message on the wire), so the passes are not trivial matches against a lossy baseline.

What this does not show: it used one local open-weight model (`qwen3.8-27b-bf16-896k`, accepted for this verdict), and in 2.x the error text is observed as the `message` of the exception thrown inside the `execute` code sandbox, the 2.x way to call MCP tools; it says nothing about any other way a client could surface a failed MCP call, or about other MCP clients. The defect reported in #47740 was on OpenCode 1.x, which is out of scope.

#### Retirement assessment of the ADR 519d1206 chain (Task 120.120, REQ-007, ACC-005)

**Recommendation: do not retire the chain on the strength of this result alone.** The result removes the original reason for one client (OpenCode 2.x), but not the other costs and dependencies of removing it. A retirement, if pursued, belongs in a separate follow-up feature.

Sites the chain touches, if retirement were pursued:

- The generic `validate` tool (ADR 519d1206): always returns `{valid, errors}` instead of raising.
- `set_status`'s `InvalidStatusResult` for an out-of-vocabulary status (ADR b399f1ce). Row 2 of the matrix is exactly this site and is the one case that is `isError: false` by design.
- `get_<d>`'s `ParseFailureResult` for the 12 whole-body domains (ADR 9080b37c), and the same result from `update`, `edit`, `set_status` and `set_classification` for a broken existing document (ADR b8c9bfea).
- The non-raising `ValidateResult` from `update`/`edit` content validation (ADR b8c9bfea), and from every `create_<d>` and `parse_<d>` (ADR f14f125e).
- Not affected: the raise sites ADR 80305c52 deliberately kept (invalid ids, not-found errors, `superseded_by` misuse). They already depend on the `call_tool` seam, not on the chain, and rows 1, 3, 4 and 5 test exactly those.

Why not retire now:

- **Other MCP clients.** ADR 519d1206 records the truncation as not OpenCode-only. This feature tested one client family, OpenCode 2.x, with one local model. A pass there says nothing about other clients that may still drop `isError: true` content.
- **OpenCode 1.x.** It is no longer used by this project, but the defect was reported there, and this feature did not retest it.
- **Python-level and documented contracts.** Callers, tests, prompts, skills and `AGENTS.md` rely on the structured results (for example the `repair` flow depends on `ParseFailureResult` from `get_<d>`). Retiring means a breaking change to these return shapes, and it would not be reversible for users who already depend on them.
- **The structured results are useful on their own.** `validate` returning a result is a dry-run, not a workaround, and `ParseFailureResult` carries the `path` and `id` that the repair flow needs. Even a retirement would likely keep some of them by design, not only as a client workaround.
- **What was observed.** The text was seen as the exception message inside the 2.x `execute` code sandbox, so it does not cover other ways a client could surface a failed call.

What would have to be true to reconsider: the supported-client list is decided and every client on it is shown to pass the same matrix; a decision is made on which structured results stay as API by design; and a migration plan exists for the changed return shapes. An ADR superseding ADR 519d1206 would record that decision.

Raw evidence is in the sibling `evidence.md` of this feature folder.
