# Round-Trip Re-Run -- feat-189 Phase 130 (Task 130.110/130.120)

Verification re-run of the feat-128 Phase 100 methodology (8 controlled
fresh-agent cells: tsk + prb x create + update x with/without prompt)
against the **worktree** specmgr server surface, checking the measurable
targets T1-T3 of the plan's ACC-005. Raw evidence for every run is
persisted under `evidence/` (event streams, per-run digests, final
documents, runner status) so the all-n-runs claim stays auditable after
the `/tmp` run dirs are gone.

## Outcome in one line

6 of 8 targets **HOLD** in all n runs of the cell; **T1b**
(prb-create-noprompt) and **T3d** (prb-update-prompt) are **MISSED in one
run each**, and both misses trace to a single **worktree server defect
surfaces by this re-run** -- not to agent authoring behavior: the Phase 120
(C13) class-level `json_schema_extra` singleton `enum`s on prb's
`Question1`..`Question7` (and vcr's `AcceptanceCriterion` DTAIS set) make
the MCP **structured output schema of `get_prb`/`get_vcr` unsatisfiable**
(an object instance is validated against a string `enum`), so every
non-raw structured read of a prb document that carries 5W2H answers fails
with `MCP error -32602`. Corrective tasks added as **Phase 135** (this
phase does not implement the fix, per the plan's Task 130.130).

## Environment

| Item | Value |
| --- | --- |
| opencode binary | `/home/user/.opencode/bin/opencode`, **v1.19.3** |
| opencode version deviation | The baseline ran 1.18.34; the orchestrator preflight recorded 1.18.35; the binary was upgraded by host automation to **1.19.3** (file dir mtime 2026-10-18 08:13) after the preflight. 1.19.3 enforces the provider's static `models` map strictly (see Deviations D3). |
| Model pin (every run) | `vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2` (the F2 re-label of the baseline pin `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`; same endpoint `http://127.0.0.1:8007/v1`, same model name -- the endpoint's `/v1/models` serves exactly `qwen3.8-27b-bf16-896k-mtp-2`) |
| Server surface | **worktree** `.venv/bin/specmgr mcp` (NOT the published uvx server) via a per-run-directory project `opencode.json` (see Method) |
| Worktree-surface probe | **115 tools** / **36 static resources** (plus the `specmgr://adr/{id}` template) / **33 prompts** -- `evidence/worktree-surface-probe.txt`. The 12 `get_<d>_schema` tools are present; the 12 `specmgr://<d>/schema` resources are gone. Baseline for comparison: published 0.34.0 = 94 tools / 44 resources; worktree before Phase 105 = 103 tools. |
| Per-run dirs | `/tmp/opencode/feat189/runs/<run-id>/` (the opencode permission config allows `/tmp/opencode/**`) |
| Timeout / protocol | 600 s per run; retry-once in a fresh clean dir with the identical instruction |

## Method

**Harness reuse + extension** (Task 130.100), all under `evidence/`:

- `evidence/harness/mcp_probe_wt.py` -- the baseline `mcp_probe.py` with
  `CMD = [<worktree>/.venv/bin/specmgr, "mcp"]` only; used for the F6
  surface probe, the prompt re-renders, the seed verification (H7), and
  the post-run parse checks.
- `evidence/harness/parse_events.py` -- the baseline extended per H3:
  schema fetches now count BOTH the baseline resource route
  (`read_mcp_resource` with uri ending `/schema`; 0 in every run) and the
  worktree tool route (any `specmgr_get_<d>_schema` call); reported as
  `schema_fetches_tool` / `schema_fetches_resource`. All other baseline
  metrics unchanged. New: `seed_uuid` field (H5), `create_call_sequence` /
  `create_first_try_success` / `create_failure_retries` (T1 first-try
  checks).
- `evidence/harness/build_prompt_instructions.py` -- splices the
  worktree-rendered prompt output into the **byte-identical** baseline
  wrapper (prefix through the BEGIN line; suffix from after the END line,
  incl. the `Task:` text); asserts the baseline layout assumption for each
  file before writing.
- `evidence/harness/seed_verify.py` + `run_all.sh` -- the baseline runner
  adapted per H6: `ROOT=/tmp/opencode/feat189`, the F2 model pin, 8 cells
  x n=3 = 24 runs, **sequential** (model-endpoint contention would
  confound wall clock -- baseline convention), 600 s timeout, retry-once
  (`<cell>-n<k>-retry`, fresh clean dir, identical instruction, both
  streams kept); resumability via `runner-status.tsv` (run-id, exit,
  duration, seed-uuid, timestamp; a cell/k is skipped on resume iff the
  primary row has exit 0 or a retry row exists); every run's event stream
  + stderr is **immediately** mirrored to `evidence/runs/` and digested
  (never a /tmp-only copy); the final `docs/` tree of each run is copied
  to `evidence/final-docs/<run-id>/` (the baseline `final-docs/`
  convention); before each update run the seed is verified parseable
  through the worktree server (`list_<domain>`: total=1, error_count=0,
  real title) -- H7.
- **Project config** (F4): every run dir carries
  `evidence/runs/smoke-opencode.json`-shaped `opencode.json` overriding
  the global config's `specmgr` mcp entry to
  `["<worktree>/.venv/bin/specmgr", "mcp"]` (server NAME kept, so tool
  calls keep the `specmgr_` prefix). It also carries the `provider`
  registration required by opencode 1.19.3 (Deviations D3). The global
  config was **not** modified.
- **Smoke probe (F5)**: one throwaway run in `/tmp/opencode/feat189/smoke/`
  (`evidence/runs/smoke.json` / `smoke-opencode.json`): exactly 1 tool
  call, `specmgr_get_tsk_template`, completed; the returned template
  carries the Phase-100 worktree comment ("Keep each task's text exactly
  as given") and NOT the old published comment ("Number the tasks...") --
  proving the project config override selected the worktree server.
- **Worktree-surface probe (F6)**: `evidence/worktree-surface-probe.txt`
  (full tools/prompts/resources record, reproducible via
  `mcp_probe_wt.py list <bare-dir>`).

**Instruction identity** (`evidence/instruction-hashes.txt`):

- The 4 NO-PROMPT cells are **byte-identical** to the baseline
  (`cmp` clean; sha256 equal to the baseline files recorded in
  feat-128's manifest): `tsk-create-noprompt` 92be500c...,
  `prb-create-noprompt` 395ba85f..., `tsk-update-noprompt` bf37690e...,
  `prb-update-noprompt` 54c35102...
- The 4 PROMPT cells: identical outer wrapper + BEGIN/END markers +
  `Task:` text (verified byte-identical against the baseline prefix and
  suffix by `build_prompt_instructions.py`), with the embedded rendered
  prompt output **re-fetched from the worktree server**
  (`mcp_probe_wt.py get_prompt`) using the baseline's exact render
  arguments (`create_task(topic='onboarding the new build server (provision
  the machine, install the toolchain, run a smoke build)')`,
  `update_task(id='UNKNOWN', instructions="mark the task 'Provision the
  machine' as done and add a new task 'Document the setup'")`,
  `create_prb(topic='build server onboarding takes too long (3 to 4 days
  manual setup per new server; expected half a day automated)')` with no
  `qa_id`, `update_prb(id='UNKNOWN', instructions='change the cost stated
  in the Impact section from 1500 EUR per quarter to 2500 EUR per
  quarter')`). Rendered texts: `evidence/prompts/<name>.rendered.txt`.
  The re-render is the one sanctioned deviation (the worktree prompts
  carry the Phase 100/110/120 changes: `get_<d>_template`/
  `get_<d>_example` one-hop references, conditional/context-sensitive
  schema steps, `get_<d>_schema` tool naming).

**Seeds**: content byte-identical to the baseline seeds (sha256 in
`evidence/seed-manifest.md`); FRESH UUID per run (12 update runs, 12
UUIDs); each verified parseable through the worktree server before launch.

**Runs**: 24 formal attempts, all exit 0, **0 timeouts, 0 retries
needed** (the retry-once protocol was armed but never triggered).
One harness incident (seed-verify arg-order + heredoc-stdin bug) recorded
below; its 12 spurious exit-3 status rows were removed after root-cause
and the affected cells were re-run clean -- the incident's full audit
trail (tracebacks + `SEED-VERIFY-FAILED` lines) remains in
`evidence/runner.log`.

## Per-cell results

Counts: "calls" = `specmgr_*` tool calls (host-level tools such as
`todowrite`/`bash` are tracked in the digests' `non_specmgr_tools` and are
NOT part of the targets); "schema t/r" = schema fetches via tool /
resource route; "failed" = calls with error status (all 8 failed calls in
the whole matrix are the `get_prb` -32602 server defect, detailed in
Targets > T1b); "create val-fail" = a failed `create_<d>` call (the
T1b validation-failure-retry signal); wall = event-stream wall
(runner-level durations in `evidence/runner-status.tsv`).

### tsk-create-noprompt (T1a; baseline 5 calls, WITH a "Task 1:" prefix deviation)

| run | calls | schema t/r | create val-fail | failed | timeouts | wall | task texts verbatim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 3 | 0/0 | 0 | 0 | 0 | 38.5 s | YES (evidence/final-docs/tsk-create-noprompt-n1) |
| n2 | 4 | 0/0 | 0 | 0 | 0 | 102.5 s | YES |
| n3 | 4 | 0/0 | 0 | 0 | 0 | 110.5 s | YES |

All 3 created documents carry exactly `- [ ] Provision the machine`,
`- [ ] Install the toolchain`, `- [ ] Run a smoke build` -- no "Task N:"
prefix, no rewording. The baseline's observed "Task 1:" deviation (the
inducement Phase 100 removed from the tsk template) did not recur.
Call sequences (digests): n1 `get_tsk_template, create_tsk, get_tsk`;
n2/n3 add `get_tsk_example`. All parse: `list_tsk` total=1,
error_count=0, title "Onboarding the new build server".

### tsk-create-prompt (T2a; baseline 9 calls incl. 1 schema fetch on the 2-hop resource route)

| run | calls | schema t/r | create val-fail | failed | timeouts | wall |
| --- | --- | --- | --- | --- | --- | --- |
| n1 | 4 | 0/0 | 0 | 0 | 0 | 194.2 s |
| n2 | 6 | 0/0 | 0 | 0 | 0 | 150.8 s |
| n3 | 5 | 0/0 | 0 | 0 | 0 | 142.0 s |

Task texts verbatim in all 3 (final-docs). 0 schema fetches on any route
(the baseline's prompt agent fetched `specmgr://tsk/schema` on the
2-hop resource route; the worktree prompt no longer directs that, and the
agent did not go looking).

### tsk-update-noprompt (T3a; baseline 5 calls)

| run | calls | schema t/r | closed-form val-fail | failed | timeouts | wall | seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 5 | 0/0 | 0 | 0 | 0 | 71.8 s | 70a358d9-... |
| n2 | 5 | 0/0 | 0 | 0 | 0 | 69.7 s | 9a4493fb-... |
| n3 | 5 | 0/0 | 0 | 0 | 0 | 79.0 s | 34d1d50e-... |

All 3 seed documents updated in place: `- [x] Provision the machine` and
`- [ ] Document the setup` present, all other lines intact (final-docs).

### tsk-update-prompt (T3b; baseline 6 calls)

| run | calls | schema t/r | closed-form val-fail | failed | timeouts | wall | seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 6 | 0/0 | 0 | 0 | 0 | 119.5 s | 83911645-... |
| n2 | 4 | 0/0 | 0 | 0 | 0 | 155.6 s | 055fb043-... |
| n3 | 5 | 0/0 | 0 | 0 | 0 | 137.3 s | dd96de9d-... |

Same semantic checks pass in all 3 (final-docs).

### prb-create-noprompt (T1b; baseline 7 calls incl. 1 validation-failure -> retry cycle)

| run | calls | schema t/r | create val-fail | failed | timeouts | wall | first-try create_prb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 3 | 0/0 | 0 | 0 | 0 | 219.8 s | YES |
| n2 | 2 | 0/0 | 0 | 0 | 0 | 170.9 s | YES |
| n3 | 6 | **1**/0 | 0 | 1 | 0 | 114.4 s | YES |

`create_prb` **succeeded on the first try in all 3 runs** (the baseline's
validation-failure -> retry cycle never recurred -- the Phase 100
lead-sentence frame in template/example is doing its job; all 3 lead
sentences are template-conform, e.g. n2: "Manual, undocumented
build-server onboarding is causing multi-day delays that block project
kickoffs, for engineering managers and build teams because every new
server requires a senior engineer to drive the setup step by step.").
n1 = `get_prb_template, get_prb_example, create_prb`; n2 =
`get_prb_template, create_prb`. **n3** = `get_prb_template,
get_prb_example, create_prb (success), get_prb (FAILED -32602),
get_prb_schema (diagnosis), get_prb(raw=true)` -- the extra calls and the
single schema fetch are the server-defect diagnosis path, not authoring
behavior (see Targets). All 3 documents parse: `list_prb` total=1,
error_count=0.

### prb-create-prompt (T2b; baseline 9 calls incl. 1 schema fetch; attempt 1 timed out at 600 s)

| run | calls | schema t/r | create val-fail | failed | timeouts | wall | first-try create_prb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 7 | 0/0 | 0 | 1 | 0 | 467.6 s | YES |
| n2 | 5 | 0/0 | 0 | 0 | 0 | 513.9 s | YES |
| n3 | 4 | 0/0 | 0 | 0 | 0 | 139.8 s | YES |

n1's single failed call is again the `get_prb` -32602 defect (the
agent's post-create verification read; recovered via raw read). No
timeouts (the baseline's prb-create-prompt attempt 1 hung to 600 s;
the worst run here was 513.9 s stream wall / 531 s runner). 0 schema
fetches on any route.

### prb-update-noprompt (T3c; baseline 5 calls)

| run | calls | schema t/r | closed-form val-fail | failed | timeouts | wall | seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 4 | 0/0 | 0 | 0 | 0 | 130.3 s | eb2fa65b-... |
| n2 | 4 | 0/0 | 0 | 0 | 0 | 131.8 s | ef5d1a24-... |
| n3 | 4 | 0/0 | 0 | 0 | 0 | 53.9 s | 40bae7ec-... |

All 3 = `list_prb, get_prb(raw=true), edit, get_prb(raw=true)` -- the
agents used **raw** reads for the local splice (as the baseline agents
chose `edit`), so none of them touched the broken structured read path.
All 3 seed documents state 2500 EUR per quarter (1500 gone), rest intact.

### prb-update-prompt (T3d; baseline 5 calls)

| run | calls | schema t/r | closed-form val-fail | failed | timeouts | wall | seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n1 | 5 | 0/0 | 0 | 1 | 0 | 262.5 s | 7b038823-... |
| n2 | **6** | **1**/0 | 0 | 1 | 0 | 133.9 s | 3ff82e63-... |
| n3 | 4 | 0/0 | 0 | 1 | 0 | 127.0 s | 7be8eccd-... |

The prompt's step 1 ("Call `get_prb(id)` to load the document's current
frontmatter and body") is a STRUCTURED read, so all 3 runs hit the -32602
defect on call 2 and recovered via raw read. n2 additionally called
`get_prb_schema` (call 4) to diagnose the error before splicing -- that
one schema fetch plus the failed/diagnostic calls put n2 at 6 > 5. All 3
seed documents state 2500 EUR per quarter, rest intact (final-docs).
`closed-form val-fail` = 0 in all runs: the `update` calls all succeeded
first try.

## Targets (ACC-005; each must hold in ALL n runs of the cell)

**T1a -- tsk-create-noprompt (at most 5 calls, task texts verbatim): HOLDS**
in all 3 runs (3, 4, 4; verbatim in all 3; 0 schema fetches).
Evidence: `evidence/runs/tsk-create-noprompt-n{1,2,3}.{json,digest.txt}`,
`evidence/final-docs/tsk-create-noprompt-n{1,2,3}/`.

**T1b -- prb-create-noprompt (first-try `create_prb` success, at most 5
calls, 0 validation-failure retries, 0 schema fetches): MISSED** --
run n3: 6 calls and 1 schema fetch (tool route). The first-try and
validation-failure-retry sub-targets HOLD in all 3 runs (create_prb
succeeded first try in n1/n2/n3; 0 failed `create_prb` calls anywhere in
the matrix). Evidence: `evidence/runs/prb-create-noprompt-n3.digest.txt`
(`ordered_tool_calls` 3-6) + `prb-create-noprompt-n3.json`. Root cause:
the `get_prb` structured-output defect below, triggered by the agent's
post-create verification read -- not by missing authoring guidance.

**T2a -- tsk-create-prompt (at most 7 calls, 0 schema fetches, 0
timeouts): HOLDS** in all 3 runs (4, 6, 5; 0/0 schema on any route;
runner walls 209/167/158 s < 600 s). Evidence:
`evidence/runs/tsk-create-prompt-n{1,2,3}.{json,digest.txt}`.

**T2b -- prb-create-prompt (at most 7 calls, 0 schema fetches, 0
timeouts): HOLDS** in all 3 runs (7, 5, 4; 0/0 schema; runner walls
484/531/157 s < 600 s -- no recurrence of the baseline's 600 s timeout).
Evidence: `evidence/runs/prb-create-prompt-n{1,2,3}.{json,digest.txt}`.

**T3a -- tsk-update-noprompt (<= baseline 5, 0 schema fetches, 0
closed-form validation failures): HOLDS** in all 3 runs (5, 5, 5).
Evidence: `evidence/runs/tsk-update-noprompt-n{1,2,3}.{json,digest.txt}`,
`evidence/final-docs/`.

**T3b -- tsk-update-prompt (<= baseline 6, 0 schema fetches, 0
closed-form validation failures): HOLDS** in all 3 runs (6, 4, 5).
Evidence: `evidence/runs/tsk-update-prompt-n{1,2,3}.{json,digest.txt}`,
`evidence/final-docs/`.

**T3c -- prb-update-noprompt (<= baseline 5, 0 schema fetches, 0
closed-form validation failures): HOLDS** in all 3 runs (4, 4, 4).
Evidence: `evidence/runs/prb-update-noprompt-n{1,2,3}.{json,digest.txt}`,
`evidence/final-docs/`.

**T3d -- prb-update-prompt (<= baseline 5, 0 schema fetches, 0
closed-form validation failures): MISSED** -- run n2: 6 calls and 1
schema fetch (tool route, `get_prb_schema` diagnosis of the -32602
error); closed-form validation failures stayed 0 in all 3 runs (every
`update` call succeeded first try). Evidence:
`evidence/runs/prb-update-prompt-n2.digest.txt`
(`ordered_tool_calls` 1-6) + `prb-update-prompt-n2.json`.

**Root cause of both misses -- worktree server defect (reproduced and
characterized outside the agent runs):**

- `get_prb` (structured, non-raw) returns the parsed document as MCP
  `structuredContent`, which the SDK validates against the tool's
  declared output schema (derived from the Pydantic models). The Phase
  120 C13 emission (plan judgment calls (a)/(b)) put class-level
  `json_schema_extra` **string `enum`s on object-level `$defs` entries**:
  `prb_schema.json` `$defs.Question1`..`$defs.Question7`
  (`"type": "object"` + `"enum": ["What Is the Problem?"]` etc.) and
  `vcr_schema.json` `$defs.AcceptanceCriterion` (DTAIS 5-value enum). A
  structured `Question1` value is an OBJECT (`{'text': '...'}`), which
  can never equal a string enum member, so the validation ALWAYS fails:
  `jsonschema.exceptions.ValidationError: {'text': '### What Is the
  Problem?\n...'} is not one of ['What Is the Problem?']` /
  `RuntimeError: Invalid structured content returned by tool get_vcr`.
- Live reproduction: `mcp_probe_wt.py call_tool <dir> get_prb '{"id":
  ...}'` on the n3-created doc -> the -32602 error above; the same call
  with `"raw": true` succeeds; `list_prb`/`create_prb` (summaries /
  frontmatter-only returns) are unaffected. `get_vcr` on the packaged
  vcr example reproduces the identical failure class (verified in this
  phase).
- Blast radius: any non-raw structured `get_prb`/`get_vcr` read of a
  document that carries at least one 5W2H answer (prb) / one AC entry
  (vcr). The 8 failed calls in the 24-run matrix are exactly those reads
  (1x in prb-create-noprompt-n3, 1x in prb-create-prompt-n1, 3x in
  prb-update-prompt). tsk is unaffected (its C13 emission is a
  class-level `pattern`, which JSON Schema applies vacuously to objects).
- Parse/validation behavior is unchanged (the enums are inert for
  Pydantic -- C13's own constraint); the defect is purely in the
  agent-visible MCP output-schema layer. It is a regression introduced
  by Phase 120, absent from the published 0.34.0 surface (zero enums
  anywhere -- the feat-128 audit baseline).

## Deviations from the baseline method (each with impact assessment)

- **D1 -- server surface: worktree instead of published 0.34.0** (the
  plan's own documented deviation, Design Notes): exercised via the
  per-run-dir project config; proven by the F5 smoke (worktree template
  text) and the F6 probe (115 tools / 36 resources / 33 prompts).
  Impact: intentional -- the targets are defined against the new surface;
  the surface deltas ARE the thing under test.
- **D2 -- n>=3 per cell** (the plan's own documented deviation): 24
  formal runs instead of 8. Impact: variance estimate per cell; targets
  must hold in ALL 3 runs.
- **D3 -- opencode binary 1.18.34 (baseline) -> 1.19.3 (this run; the
  preflight had recorded 1.18.35, the upgrade landed at 2026-10-18 08:13
  after the preflight).** 1.19.3 enforces the provider's static `models`
  map strictly: the pinned id `qwen3.8-27b-bf16-896k-mtp-2` is absent
  from the global config's `vllm-sys0-2` map (which lists only
  `qwen3.8-27b-bf16-896k`, a model the endpoint rejects with 404), so
  `opencode run` failed with `ProviderModelNotFoundError` until the
  per-run-dir project config registered the id under the same provider
  (same endpoint, same limit values as the sibling entry). Impact: the
  executed model is still exactly the F2 pin on the same endpoint
  (`/v1/models` serves only `qwen3.8-27b-bf16-896k-mtp-2`); the global
  config is untouched; the F5 smoke + every run's event stream confirm
  the model in use. CLI flags (`run --dir -m --title --format json`) and
  the event-stream schema are unchanged between versions (verified
  against the baseline stream).
- **D4 -- model pin label `vllm-sys0-mtp-2/...` -> `vllm-sys0-2/...`**
  (the preflight's F2 re-label; same model, same endpoint). Impact:
  none beyond the string; recorded for completeness.
- **D5 -- the 4 prompt cells' embedded rendered output was re-fetched
  from the worktree server** (sanctioned by the plan/H4: the worktree
  prompts carry the Phase 100/110/120 changes, which is the point of the
  re-run). Wrapper + markers + `Task:` text are byte-identical to the
  baseline (verified). Impact: intentional -- this is the condition under
  test; the no-prompt cells are fully byte-identical and show the
  surface-side effect independently.
- **D6 -- harness incident (seed verification).** The first runner
  launch contained two harness bugs (probe arg order `call_tool <tool>
  <args> <cwd>` instead of `call_tool <cwd> <tool> <args>`; and
  `probe | python3 - <<heredoc` where the heredoc replaced the pipe as
  the parser's stdin). Twelve update-cell attempts (all 4 tsk-update
  cells x primary + retry) aborted at seed-verify with exit 3 before any
  agent ran; their status rows were removed after root-cause (the
  incident's full audit trail -- tracebacks and `SEED-VERIFY-FAILED`
  lines -- remains in `evidence/runner.log`), the harness was fixed
  (`seed_verify.py`), the verify path was re-tested in isolation, and the
  affected cells were re-run clean. Impact: no agent run was contaminated
  (no instruction was ever sent); the 24 formal runs in the tables above
  are all post-fix. A first launch also died to its launcher shell's
  process-group kill mid `tsk-create-noprompt-n2` (before the status row
  existed); the re-launch (setsid-detached) resumed from the status file
  and re-ran that cell in a fresh dir -- n1's result is untouched and
  n2/n3 are the formal ones.

## Success verification

Every created document (12 create runs) was read back from disk and
listed through the WORKTREE server itself (`mcp_probe_wt.py call_tool
<run-dir> list_<d> '{}'`): all 12 report `total: 1, error_count: 0` with
the real title and status `draft` (no `<failed to parse>` rows). Every
updated document (12 update runs) carries the requested change with all
other lines intact (checked in `evidence/final-docs/`). Repo-pollution
check: `git status --porcelain` in the worktree shows only this feature
folder (`evidence/`, this report, the README progress update) -- the
/tmp run dirs wrote nothing into the repo (the server resolves base dirs
CWD-relative to the run dir, as the F5 smoke proved).

## Reproduction

```bash
# surface probe (F6)
.venv/bin/python evidence/harness/mcp_probe_wt.py list <bare-dir>
# one formal run (from a prepared run dir with opencode.json + seed)
timeout 600 /home/user/.opencode/bin/opencode run --dir <run-dir> \
  -m vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2 --title <run-id> \
  --format json "$(cat evidence/instructions/<cell>.txt)"
# metrics
.venv/bin/python evidence/harness/parse_events.py <run-id> <stream.json> <run-dir> [seed-uuid]
```

The full runner (`evidence/harness/run_all.sh`) is resumable via
`evidence/runner-status.tsv`; `evidence/runner.log` carries the
per-attempt audit trail including the D6 incident.

## Phase 135 re-verification (Task 135.110; attempt of 2026-10-18)

**Fix reference:** Task 135.100 (Phase 135, the C13 corrective) removed
exactly the 11 breaking object-node `enum` emissions (req `Level.value`,
rsk `Strategy.value`, vcr `Coverage.value`, vcr `AcceptanceCriterion`
[only the `enum` entry; the `pattern` entry stays], prb
`Question1`..`Question7`); the 21 kept keys (12 status enums + 9 patterns),
every validator/alias/pattern constant, and the instruction/seeds/protocol
are untouched. The fixed surface is proven by the Phase 135 gate's wire
reproduction (`evidence/wire-reproduction-135.txt`): /tmp dirs seeded with
the packaged prb/vcr/req/rsk examples, worktree server
(`.venv/bin/specmgr mcp`, cwd = seed dir) -- `list_<d>` then NON-raw
`get_<d>` for all four domains, **every call succeeds** (before the fix all
four failed `-32602` "Invalid structured content"; prb was the proven one).
This is the R2 sanity check that the runs would hit the FIXED server.

**BLOCKED before any run -- the pinned model is no longer served (environment,
not protocol):** the preflight of 2026-10-18 found the pinned endpoint
(127.0.0.1:8007, the `vllm-sys0-2` provider's baseURL) now serves
`qwen3.8-27b-bf16-896k` instead of the Phase 130 pin
`qwen3.8-27b-bf16-896k-mtp-2`; a chat-completions probe with the pinned name
gets `404 {"error": "The model 'qwen3.8-27b-bf16-896k-mtp-2' does not
exist."}`, and no other local endpoint (8001 down; 8008 non-MTP-only) serves
the MTP model (`evidence/preflight-135.txt` carries the full probe output).
The opencode binary (1.19.3) and the two instruction files (sha256
`395ba85f...`/`53ddec39...`, byte-identical to the Phase 130 copies per
`evidence/instruction-hashes.txt`) are unchanged. Per the Phase 135 hard
rule ("if the model endpoint is down ... STOP and report"), **no formal run
was launched and none is claimed**: `evidence/runner-status-135.tsv` is
header-only (zero attempts), no seed UUID was consumed
(`evidence/phase135-seed-manifest.md`), and there is no per-run table for
the six runs.

**T1b / T3d verdicts:** NOT re-verified (environment-blocked) -- the Phase
130 miss stands on record (T1b n3: 6 calls + 1 schema fetch; T3d n2: 6 calls
+ 1 schema fetch), now root-caused to the server defect that Task 135.100
fixed and wire-reproduction-proven. ACC-005 stays unchecked.

**Re-launch (ready):** `evidence/harness/run_135.sh` -- a minimal delta of
`run_all.sh` (same project-config shape per D3, same seed/verify/digest/
mirror logic; CELLS = the two cells only; run ids `<cell>-135-n<k>`; fresh
/tmp root `/tmp/opencode/feat189-135`; separate `runner-status-135.tsv` /
`runner-135.log` mirrors so the Phase 130 audit trail stays byte-identical;
a pre-launch sha256 check refuses to run on any instruction deviation).
Run it once the MTP endpoint serves `qwen3.8-27b-bf16-896k-mtp-2` again; it
is resumable via the 135 status file. When it completes, append the
per-run tables here, verdict T1b (first-try `create_prb`, at most 5 calls,
0 validation-failure retries, 0 schema fetches in all 3) and T3d (at most 5
calls, 0 schema fetches, 0 closed-form validation failures in all 3), and
check ACC-005 iff both hold.
