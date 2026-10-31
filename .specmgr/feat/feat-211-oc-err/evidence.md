# Evidence: feat-211-oc-err (OpenCode 2.0.32 and 2.2.5)

Status: COMPLETE for both images (2.0.32 and the newest published 2.x, 2.2.5): both server variants, 5 rows, 3 valid runs per cell, plus the Inspector baselines.

## Environment

- Date: 2026-10-31. Host: Linux x86_64, docker 29.1.3, uv/uvx 0.12.5, node v24.22.2, npx 11.19.1.
- OpenCode images (REQ-001): (a) `ghcr.io/anomalyco/opencode:2.0.32` (opencode v2.0.32), digest `sha256:02998f912cc8bf84ce20ff9d9faa33225406c52f9d13f8f86b376490f1e28813` (the local baseline); (b) `ghcr.io/anomalyco/opencode:2.2.5` (opencode v2.2.5), digest `sha256:1690aad69864d2f6714772d1e040918feebc6df5286d2bd7e181fbb35d12d4a9`, pulled on 2026-10-31 as the newest published 2.x tag (the registry lists 3362 tags; highest semver is 2.2.5; there is no non-semver 2.x tag). The two digests differ, so these are two distinct images. The `latest` tag is NOT 2.x: it is v1.19.5 (digest `sha256:f4cfe16d91efbbfca01a51c44094fba4cf82e15c7fa17de5f11f9059699b1e6e`) and was not tested. 
- Variant `dev`: this repo's checkout at commit `4ebdc6c` (specmgr 0.37.0, `mcp` 2.3.0), command `uv run --frozen --extra cli --extra mcp --directory <checkout> specmgr mcp`.
- Variant `old`: published `biz-dfch-specmgr[mcp]==0.23.0` with `--with mcp==2.0.0`, command `uvx --from 'biz-dfch-specmgr[mcp]==0.23.0' --with mcp==2.0.0 specmgr mcp` (resolved: specmgr 0.23.0, mcp 2.0.0; also confirmed to start under musl in the container via `uv tool run`).
- Both servers ran with `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`/`SPECMGR_ADR_DIR` pointing at a sandbox holding one requirement document, `UUID` = `b43aafc7-6ad3-4587-90d1-1a7ad9936716`, `SPECMGR_SIMILARITY_DISABLED=1`, `SPECMGR_FEAT_WARMUP_DISABLED=1`.
- Baseline tool: `npx -y @modelcontextprotocol/inspector --cli <server command> --method tools/call --tool-name <tool> --tool-arg k=v ... ` run on the host, stdout JSON stored unmodified (stderr discarded).

## Inspector baselines (raw `content[0].text` and `isError`)

### dev (specmgr 0.37.0, mcp 2.3.0, feat-221 shim)

Row 1: `get_req(id="./non-existing-file.txt")`

- isError: `true`
- text:

```text
id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected
```

Row 2: `set_status(id=UUID, type="req", status="bogus-status")`

- isError: `false`
- text:

```text
{
  "valid": false,
  "type": "req",
  "status": "bogus-status",
  "allowed_values": [
    "accepted",
    "deprecated",
    "draft",
    "implemented",
    "proposed",
    "rejected",
    "superseded"
  ],
  "message": "Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"
}
```

Row 3: `set_status(id="deadbeef-dead-dead-dead-deadbeefdead", type="req", status="draft")`

- isError: `true`
- text:

```text
no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').
```

Row 4: `set_status(id="./non-existing-file.txt", type="req", status="draft")`

- isError: `true`
- text:

```text
id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected
```

Row 5: `set_status(id=UUID, type="req", status="draft", superseded_by="x")`

- isError: `true`
- text:

```text
superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'
```

### old (specmgr 0.23.0, mcp 2.0.0)

Row 1: `get_req(id="./non-existing-file.txt")`

- isError: `true`
- text:

```text
Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected
```

Row 2: `set_status(id=UUID, type="req", status="bogus-status")`

- isError: `false`
- text:

```text
{
  "valid": false,
  "type": "req",
  "status": "bogus-status",
  "allowed_values": [
    "accepted",
    "deprecated",
    "draft",
    "implemented",
    "proposed",
    "rejected",
    "superseded"
  ],
  "message": "Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"
}
```

Row 3: `set_status(id="deadbeef-dead-dead-dead-deadbeefdead", type="req", status="draft")`

- isError: `true`
- text:

```text
Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').
```

Row 4: `set_status(id="./non-existing-file.txt", type="req", status="draft")`

- isError: `true`
- text:

```text
Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected
```

Row 5: `set_status(id=UUID, type="req", status="draft", superseded_by="x")`

- isError: `true`
- text:

```text
Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'
```

Baseline check (REQ-003): for both variants rows 1, 3, 4 and 5 carry the full server message with `isError: true`; row 2 is `isError: false` (control). The `old` variant adds the `Error executing tool <name>: ` prefix, the `dev` variant does not (feat-221 / ADR 80305c52). Both baselines are valid.

## OpenCode runs on 2.0.32 (image a)

- Image: `ghcr.io/anomalyco/opencode:2.0.32` (opencode v2.0.32), digest as above. Command per run: `docker run --rm --network host -w /proj <mounts> ghcr.io/anomalyco/opencode:2.0.32 run --standalone --auto --format json -m vllm/qwen3.8-27b-bf16-896k <prompt>`.
- Provider/model: a custom OpenAI-compatible provider (`@ai-sdk/openai-compatible`, `baseURL` pointing at a local endpoint) on a local vLLM instance (model `qwen3.8-27b-bf16-896k`, `Qwen/Qwen3.8-27B`, server fingerprint `vllm-0.26.0-tp2`), not the built-in `opencode/zen` provider (its free quota was exhausted, see the end of this file). The model's non-determinism is the reason for 3 runs per cell.
- Project config: `opencode.json` with `mcp.servers.specmgr` (`type: local`, `command`, `environment`) in the 2.x shape, `dev` and `old` as defined above; the `old` server ran through `uv tool run --from 'biz-dfch-specmgr[mcp]==0.23.0' --with mcp==2.0.0 specmgr mcp` with a musl `uv` mounted into the image.
- Prompt per run (one prompt shape, only the tool call differs): do exactly two `execute` calls, one at a time, with the given code and no changes. Call 1 is `return JSON.stringify(search({ query: "<tool>", namespace: "specmgr" }).items.map(i => i.path));` (tool discovery). Call 2 is `try { const r = await tools.specmgr.<tool>(<literal args>); return "RESULT: " + JSON.stringify(r); } catch (e) { return "ERROR: " + e.message; }`. No retry, no changed argument, then reply `done`.
- Capture: the `execute` tool part's `state.output` from the `--format json` event stream (raw tool result as the code sandbox received it), plus the nested call's `status` in `metadata.toolCalls[]`. The model's prose is not used.
- Valid run: exactly one nested call to the target tool reached the server. Pass rule (REQ-005): the baseline's full `content[].text` of the same variant is contained verbatim in the captured output (exactly, or after the `Error executing tool <name>: ` prefix). Row 2 is the control and is excluded from the rule.

Result: rows 1, 3, 4 and 5 = 24 of 24 valid runs pass (12 per variant); row 2 control = 6 of 6 runs completed with `isError`-false structured result (`InvalidStatusResult`, not an error).

Runs that did not reach the server (model mistakes, not client behavior) were excluded and rerun: `dev` row 5 run 2 twice (first: the model escaped the quotes and the code failed to parse, `Expecting Unicode escape sequence \uXXXX`; second attempt also produced no call) and `old` row 1 run 1 (the model skipped call 2). The raw streams are kept outside the repository. A first attempt with a different prompt and the built-in provider reached the server in only 3 of 30 runs (the model never discovered `tools.specmgr.*`); that attempt is superseded and carries no weight.

### Matrix on 2.0.32 (captured `execute` output)

#### dev

- row 1 run 1: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 2: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 3: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 2 run 1: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 2: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 3: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`

- row 3 run 1: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 2: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 3: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`

- row 4 run 1: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 2: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 3: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 5 run 1: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 2: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 3: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`

#### old

- row 1 run 1: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 2: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 3: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 2 run 1: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 2: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 3: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`

- row 3 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`

- row 4 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 5 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`

## OpenCode runs on 2.2.5 (image b, the newest published 2.x)

Same harness, same provider and model (a local vLLM instance, `qwen3.8-27b-bf16-896k`), same project config (`mcp.servers` shape), same two-step prompt and the same capture and pass rule as for 2.0.32; only the image tag changed (`ghcr.io/anomalyco/opencode:2.2.5`). The config shape, the `--standalone --auto --format json` flags and the `execute`-sandbox tool access all worked unchanged on 2.2.5.

Result: rows 1, 3, 4 and 5 = 24 of 24 valid runs pass (12 per variant); row 2 control = 6 of 6 completed with the structured `InvalidStatusResult` result.

One run did not reach the server and was excluded and rerun: `old` row 4 run 2 (the model escaped the quotes and the code failed to parse: `SyntaxError: Expecting Unicode escape sequence \uXXXX`); the rerun passed. A model mistake, not client behavior.

### Matrix on 2.2.5 (captured `execute` output)

#### dev

- row 1 run 1: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 2: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 3: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 2 run 1: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 2: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 3: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`

- row 3 run 1: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 2: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 3: nested status `error`; output: `ERROR: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`

- row 4 run 1: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 2: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 3: nested status `error`; output: `ERROR: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 5 run 1: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 2: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 3: nested status `error`; output: `ERROR: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`

#### old

- row 1 run 1: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 2: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 1 run 3: nested status `error`; output: `ERROR: Error executing tool get_req: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 2 run 1: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 2: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`
- row 2 run 3: nested status `completed`; output: `RESULT: {"result":{"valid":false,"type":"req","status":"bogus-status","allowed_values":["accepted","deprecated","draft","implemented","proposed","rejected","superseded"],"message":"Invalid status 'bogus-status' for type 'req'. Allowed values: accepted, deprecated, draft, implemented, proposed, rejected, superseded"}}`

- row 3 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`
- row 3 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: no requirement found with id 'deadbeef-dead-dead-dead-deadbeefdead'. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not 'req-<uuid>').`

- row 4 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`
- row 4 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: id './non-existing-file.txt' contains a path separator or a '..' traversal sequence; a bare id is expected`

- row 5 run 1: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 2: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`
- row 5 run 3: nested status `error`; output: `ERROR: Error executing tool set_status: superseded_by is only accepted for type='adr' (the "superseded by X" pattern is ADR-specific), got type='req' with superseded_by='x'`

## Verdict (REQ-005 rule)

Rule: a cell passes if the OpenCode-visible tool error for each `isError: true` row (1, 3, 4, 5) contains the Inspector baseline's full `content[].text` verbatim, exactly or after the `Error executing tool <name>: ` prefix; the defect counts as fixed only if every cell passes for both server variants.

Outcome: 48 of 48 valid runs pass (2 images x 2 variants x 4 rows x 3 runs); no valid run failed. Under the rule, the defect from anomalyco/opencode#47740 (a bare `Error executing tool <name>`, real text dropped) did NOT reproduce on OpenCode 2.0.32 or on the newest published 2.x image, 2.2.5, for either server variant.

Caveats that bound this: one local open-weight model; the error text is observed as the `message` of the exception thrown inside the `execute` code sandbox (the 2.x way to call MCP tools), so this does not cover any other way a client could surface a failed MCP call; and the retirement of the non-raising workaround chain is a separate question (other MCP clients, Python-level contracts), assessed separately.

## Why the built-in provider was not used

After about 40 runs on the built-in `opencode` provider it returned `provider.quota`, `Free usage limit reached` (HTTP 429) for `opencode/big-pickle`, `opencode/glm-5.3-flash-free` and `opencode/deepseek-v4.1-flash-free`; `opencode/nemotron-3-ultra-free` returned `Model is unavailable`. The matrix was then run on the local vLLM instance. This is not a client defect finding.

## Limits of this evidence

- Two images were tested (2.0.32 and 2.2.5); any later 2.x release is untested.
- The model is a local open-weight model, not a production OpenCode provider model. The tool-result path under test is the client's, not the model's, but this is a different model than the plan's default.
- In 2.x the error text reaches the model as the `message` of an exception thrown inside the `execute` code sandbox. The test shows that this text is complete; it does not show how a model would see the failure if it called MCP tools some other way.
