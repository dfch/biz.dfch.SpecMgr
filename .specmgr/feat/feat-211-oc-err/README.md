---
classification: null
created: '2026-10-31T13:32:45.409+01:00'
id: feat-211-oc-err
status: planning
type: feat
updated: '2026-10-31T13:32:45.409+01:00'
version: 1.0.0
---

# Feature: Re-verify MCP isError:true Truncation on OpenCode 2.x (anomalyco/opencode#47740)

## Plan

### Overview

GitHub issue #211 tracks a re-verification obligation: [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740) documented that OpenCode (<=1.18.x) drops the content of a failed MCP tool result -- the model only receives a bare `Error executing tool <name>`, discarding the real error text the server put in `content[].text`. This defect is the reason this repo built the non-raising structured-result workaround chain (ADR 519d1206, extended by b399f1ce, 9080b37c, b8c9bfea, f14f125e) instead of simply raising informative exceptions everywhere. Upstream closed #47740 on 2026-10-11 because OpenCode 2.0 shipped and 1.x triage stopped, asking the reporter to reopen it (or file a new issue citing the 2.x version) if the defect still reproduces on 2.0+. This feature re-runs that repro against the newest available OpenCode 2.x container image, records the evidence, and acts on the result (close out upstream and #211 if fixed; reopen/file anew if not) -- and separately assesses whether the ADR 519d1206 non-raising workaround chain itself can now be retired.

### Requirements

- REQ-001: Pull and use the newest published `ghcr.io/anomalyco/opencode` 2.x image tag available at run time, and also record the pre-existing local `ghcr.io/anomalyco/opencode:2.0.32` image as a baseline comparison point.

- REQ-002: Run the repro against two MCP server variants: the published `biz-dfch-specmgr[mcp]==0.23.0` package (the exact version named in the original #47740 report) and this repo's current dev checkout (which already carries the feat-221/ADR 80305c52 `call_tool` seam shim, so its wire text differs from the original report by the missing `Error executing tool <name>: ` prefix).

- REQ-003: Re-run all five rows of the #47740 repro table (not just row 1) for each image x server pair, plus a raw MCP Inspector call per server as the ground-truth baseline each OpenCode run is compared against.

- REQ-004: Drive each OpenCode run headlessly (`opencode run`) inside the container, using the opencode/zen integrated provider, and capture the exact commands, image digests, and raw outputs as evidence.

- REQ-005: Produce a single pass/fail verdict: the defect counts as fixed only if every `isError: true` row (1, 3, 4, 5) returns the server's full error text to the model, matching the Inspector baseline; a verdict against a real image/server pair is required, not an assumption.

- REQ-006: Based on the verdict, perform the appropriate upstream/issue action -- comment on anomalyco/opencode#47740 and close it, and close dfch/biz.dfch.SpecMgr#211, if fixed; otherwise reopen #47740 (or file a new upstream issue citing the OpenCode 2.x version) per the maintainers' request, and keep #211 open.

- REQ-007: Write up a short assessment of whether the ADR 519d1206 non-raising-structured-result workaround chain can now be retired, as input to a separate, later follow-up feature -- this feature does not perform any such retirement itself.

### Acceptance Criteria

- [ ] ACC-001: The pulled image's repository digest and the local baseline image's digest are both recorded in this feature's evidence.

- [ ] ACC-002: A completed 5-row x 2-image x 2-server repro matrix (20 cells) exists, each cell holding the command run and the raw output, plus the per-server MCP Inspector baseline output for all five rows.

- [ ] ACC-003: The verdict (fixed / still present) is stated explicitly and is justified by the matrix in ACC-002, not asserted without evidence.

- [ ] ACC-004: The appropriate upstream action (close-with-comment, or reopen/file-anew) has been taken on anomalyco/opencode#47740, and dfch/biz.dfch.SpecMgr#211 has been updated (comment, and closed if fixed), with both links recorded in this feature's Related PRs / Commits.

- [ ] ACC-005: A written assessment of whether the ADR 519d1206 chain can be retired is present in this feature's Design Notes or More Information, including which specific tools/call sites it would affect if retirement were pursued.

### Scope

#### Included

- Pulling/using the newest `ghcr.io/anomalyco/opencode` 2.x image and the existing local 2.0.32 image.

- Configuring and running both named MCP server variants headlessly inside the container.

- Running and recording the full 5-row repro matrix plus the Inspector baselines.

- Taking the resulting upstream/#211 close-out action.

- Writing the ADR 519d1206 chain retirement assessment (assessment only, no code change).

#### Explicitly Out Of Scope

- Any change to this repo's server code, tools, or the `call_tool` seam shim (feat-221/ADR 80305c52) -- this feature only observes and records behavior.

- Actually retiring any part of the ADR 519d1206 non-raising workaround chain -- tracked as a separate, later follow-up feature if the assessment (REQ-007/ACC-005) recommends it.

- Verifying OpenCode 1.x behavior again -- already established and documented by the original #47740 report and feat-103.

- Testing any MCP server other than this repo's `specmgr` server.

### Dependencies

#### Depends On

- None.

#### Blocks

- A future follow-up feature to retire part or all of the ADR 519d1206 non-raising workaround chain, contingent on this feature's REQ-007/ACC-005 assessment.

### Design Notes

Repro matrix shape: 2 images (`ghcr.io/anomalyco/opencode:2.0.32` baseline, newest published 2.x tag) x 2 MCP server variants (`uvx --from "biz-dfch-specmgr[mcp]==0.23.0" specmgr mcp`, the original #47740 version; and `uv run --frozen --directory` against this repo's checkout, current dev) x 5 repro rows from #47740 (get_req path-like id; set_status bogus status, isError:false control; set_status unknown id; set_status path-like id; set_status superseded_by misuse) = 20 OpenCode-run cells, plus one MCP Inspector baseline call per server (2 baselines x 5 rows = 10 reference outputs) that every OpenCode cell is diffed against.

Expected-text caveat: the dev-checkout server's wire text is expected to differ from the original 0.23.0 report even on an unfixed OpenCode, because feat-221/ADR 80305c52's `SpecMgrServer.call_tool` seam already re-raises `UnexpectedToolError.__cause__`, which strips the `Error executing tool <name>: ` prefix FastMCP/the SDK would otherwise add. So "fixed" must be judged by "does the model receive the real message text" (regardless of the exact prefix), not by a byte-for-byte match against the original issue's quoted output.

Headless run approach: `opencode run` inside the container, driven by a prompt that invokes the relevant tool call directly, with the opencode/zen integrated provider configured so no external provider credentials are needed inside the container.

### Related Decisions

- ADR 519d1206-4d2a-4500-9046-6db635209996 (Design validate as a non-raising, structured-result tool to work around this exact OpenCode defect): the chain this feature's verdict may allow retiring.

- ADR b399f1ce-ed42-4929-b01c-7a57d18e8014 (Extend the non-raising workaround to set_status's invalid-status case): part of the same chain.

- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c (Extend the non-raising workaround to the `get_<d>` parse-failure case): part of the same chain.

- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (Extend the non-raising workaround to update/edit's content-validation case): part of the same chain.

- ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e (Extend the non-raising workaround to the `create_<d>`/`parse_<d>` content-validation case): part of the same chain.

- ADR 80305c52-102e-4833-a233-3468bef29e11 (Preserve caller-visible tool error text across mcp >= 2.1.0 via a call_tool seam): the shim that changes the dev checkout's expected wire text for this repro, and explicitly scoped itself as preserving the status quo on issue #211 rather than resolving it.

### Task List

#### Phase 100: Prepare the Test Environment

- [ ] Task 100.100: Pull the newest published `ghcr.io/anomalyco/opencode` 2.x image tag and record its repository digest alongside the pre-existing local `ghcr.io/anomalyco/opencode:2.0.32` image's digest.

- [ ] Task 100.110: Configure the container's OpenCode `mcp` entries for both server variants (published `biz-dfch-specmgr[mcp]==0.23.0` via `uvx`, and this repo's current dev checkout via `uv run --frozen --directory`), and the opencode/zen integrated provider for headless `opencode run` use.

#### Phase 110: Run and Record the Repro Matrix

- [ ] Task 110.100: For each MCP server variant, run the five #47740 repro calls directly via MCP Inspector and record the raw JSON output as the ground-truth baseline.

- [ ] Task 110.110: For each of the 2 images x 2 server variants (4 combinations), run `opencode run` headlessly for all five repro rows and record the exact prompt/command and the model-visible output for each.

- [ ] Task 110.120: Assemble the full 20-cell matrix plus the 10 baseline rows into this feature's evidence (Design Notes or More Information), and state the explicit pass/fail verdict with justification.

#### Phase 120: Close Out

- [ ] Task 120.100: Based on the verdict, comment on and close anomalyco/opencode#47740 if fixed, or reopen it (or file a new upstream issue citing the tested 2.x version) if still present.

- [ ] Task 120.110: Comment on dfch/biz.dfch.SpecMgr#211 with the verdict and the upstream action taken, closing #211 if the defect is fixed.

- [ ] Task 120.120: Write the ADR 519d1206 chain retirement assessment (which tools/call sites would be affected, and whether retirement is recommended) into this feature's Design Notes or More Information, satisfying REQ-007/ACC-005.

## Progress

### Current Status

**As of 2026-10-31**: Feature planned; no verification has been run yet. The newest published OpenCode image tag, the opencode/zen provider wiring, and the container's network access to pull the image and reach the provider all still need to be confirmed before Phase 100 can start.

### Blockers

- Confirming the opencode/zen integrated provider is reachable and authenticated from inside the OpenCode 2.x container.

- Confirming the container has network egress to pull `ghcr.io/anomalyco/opencode`'s newest 2.x tag.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 00:00:00.000Z - Created

Feature created from dfch/biz.dfch.SpecMgr#211 to re-verify anomalyco/opencode#47740 against the newest OpenCode 2.x container image. Plan covers a 2-image x 2-server x 5-row repro matrix plus Inspector baselines, the resulting upstream/#211 close-out action, and a written assessment of whether the ADR 519d1206 non-raising workaround chain can be retired. Implementation has not started.

### Related PRs / Commits

- [Issue #211](https://github.com/dfch/biz.dfch.SpecMgr/issues/211): the tracking issue this feature addresses.

- [anomalyco/opencode#47740](https://github.com/anomalyco/opencode/issues/47740): the original upstream defect report being re-verified.

- [Issue #204](https://github.com/dfch/biz.dfch.SpecMgr/issues/204): related non-raising-workaround-chain tracking issue referenced by #211.

- feat-103-set-status-error: the feature that originally filed anomalyco/opencode#47740.

- feat-204-create-error: an earlier extension of the non-raising workaround chain.

- feat-221-mcp-220-error-contract: added the `call_tool` seam shim (ADR 80305c52) that changes this repo's dev-checkout wire text for this repro.
