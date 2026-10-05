# Round-Trip Baseline (feat-128, Task 100.120)

Quantitative baseline for agent round-trips on create/update operations,
captured from 8 controlled `opencode run` sessions (Task 100.100
methodology: tsk + prb x create + update x with/without the create/update
prompt pre-invoked), to ground the ACC-003 measurable target. Per-run
digest, raw event streams, and the exact instruction strings live in
`evidence/` (`evidence/manifest.md` is the index).

**Conditions and controls**

- Host: opencode v1.18.34, non-interactive `opencode run --format json`,
  bare temp dirs (no repo context), model pinned
  `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2` (every run).
- MCP surface: published `biz-dfch-specmgr[mcp, similarity]` 0.34.0 via
  `uvx` (the global opencode config), CWD-relative base dirs.
- `-prompt` condition: the domain's create/update prompt was fetched by
  the harness (opencode does not expose MCP prompts as tools -- probe run
  `NO_PROMPT_TOOL`) via a Python MCP client and prepended to the
  instruction; update prompts were rendered with `id="UNKNOWN"`
  (placeholder, no id leak) so document discovery stayed part of the
  round trip in both conditions.
- Success verdict: the required document change present on disk under
  `<run-dir>/docs/` **and** the document parseable by the published
  server (`list_<d>` row with a real title, `error_count: 0`).

## Per-run results (formal runs)

| run-id | cond. | total calls | specmgr calls | non-specmgr calls | schema fetches | template fetches | example fetches | validate calls | failed calls | wall (s) | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| tsk-create-noprompt | none | 5 | 5 | 0 | 0 | 1 (tool) | 1 (tool) | 1 | 0 | 100.6 | success |
| tsk-create-prompt | create_task | 9 | 3 | 6 | 1 | 1 (resource) | 0 | 1 | 0 | 284.3 | success |
| tsk-update-noprompt | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 84.5 | success |
| tsk-update-prompt | update_task | 6 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 161.3 | success |
| prb-create-noprompt | none | 7 | 7 | 0 | 0 | 1 (tool) | 1 (tool) | 2 | 1 | 254.1 | success |
| prb-create-prompt (attempt 1) | create_prb | 8 | 4 | 4 | 1 | 1 (tool) | 1 (tool) | 1 | 0 | 600 (timeout) | fail (timeout) |
| prb-create-prompt (retry, formal) | create_prb | 9 | 4 | 5 | 1 | 1 (resource) | 0 | 1 | 0 | 394.2 | success |
| prb-update-noprompt | none | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 100.5 | success |
| prb-update-prompt | update_prb | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 66.9 | success |

Notes: "tool" = the `get_<d>_template`/`get_<d>_example` MCP tools;
"resource" = `read_mcp_resource` (which required a preceding
`list_mcp_resources` discovery call, counted in the non-specmgr column).
Non-specmgr calls in the `-prompt` runs are `todowrite` (2 each),
`list_mcp_resources` (1 each), `read_mcp_resource` (1-2 each), and `bash`
(`date` for the Recent Updates timestamp: tsk-create-prompt,
tsk-update-prompt). `prb-create-noprompt`'s single failed call is
`create_prb` (lead-sentence template mismatch), followed by a
validate -> fix -> validate -> create retry cycle (+2 calls over the
minimum path). Attempt 1 of `prb-create-prompt` timed out at 600 s while
assembling the body (8 calls done, no document written); the retry is the
formal result per the run protocol (retry once, record both attempts).

## Per domain x operation aggregate (formal successful runs)

| domain x operation | total tool calls (noprompt / prompt) | median calls to success | schema fetches (noprompt / prompt) | template/example fetches | validation retries | wall (s) noprompt / prompt |
| --- | --- | --- | --- | --- | --- | --- |
| tsk create | 5 / 9 | 5 / 9 (n=1 each) | 0 / 1 | 1+1 / 1+0 | 0 / 0 | 100.6 / 284.3 |
| tsk update | 5 / 6 | 5 / 6 (n=1 each) | 0 / 0 | 0 / 0 | 0 / 0 | 84.5 / 161.3 |
| prb create | 7 / 9 | 7 / 9 (n=1 each) | 0 / 1 | 1+1 / 1+0 | 1 / 0 | 254.1 / 394.2 |
| prb update | 5 / 5 | 5 / 5 (n=1 each) | 0 / 0 | 0 / 0 | 0 / 0 | 100.5 / 66.9 |

Headline facts:

- **Schema fetches: 2 of 8 formal runs (25%).** Both `-noprompt` cells
  fetched the schema **zero** times (0/4); both `-prompt` **create** runs
  fetched it exactly once (2/2); both `-prompt` **update** runs skipped
  the prompt's own "Check the schema" step (0/2).
- **Tool calls per successful create:** tsk 5 (noprompt) vs 9 (prompt);
  prb 7 (noprompt, including the failure-retry cycle) vs 9 (prompt).
  **Per successful update:** tsk 5/6; prb 5/5. The prompt condition
  costs +4 calls on tsk create (todo list, resource discovery, schema +
  template resource reads, bash date) and buys the prb create's clean
  first-try lead sentence.
- **Update runs never fetched template/example/schema** in any condition
  (0/8 update-side fetches); the update round trip is
  `list -> get(raw) -> edit/update -> get(raw, windowed verify)`.
- **Resource fetches are 2 hops on this host** (`list_mcp_resources` +
  `read_mcp_resource`) versus 1 hop for the equivalent tools
  (`get_<d>_template`/`get_<d>_example`): every prompt-driven create run
  paid the extra discovery hop, no noprompt run ever entered the
  resource layer at all (0 `list_mcp_resources` calls across all four
  noprompt runs).
- **Wall clock** tracks context size, not call count: the prb prompt run
  (13 KB prompt + 15 KB schema + 11 KB template/example in context)
  needed 394 s where the noprompt prb create needed 254 s with 2 more
  calls; one prompt prb create attempt exceeded the 600 s timeout.

## Per-domain schema payload size (KB) -- the "perceived cost" input

From the audited `docs/<domain>_schema.json` (worktree; prb byte-identical
to the published copy the agents fetched, tsk differs only in the
`UpdateEntryContent` leaf -- see `schema-audit.md`):

| domain | bytes | KB | domain | bytes | KB |
| --- | ---: | ---: | --- | ---: | ---: |
| tsk | 12,607 | 12.31 | uc | 23,096 | 22.56 |
| prb | 15,574 | 15.21 | qa | 25,406 | 24.81 |
| gol | 16,172 | 15.80 | feat | 28,859 | 28.18 |
| rsk | 18,722 | 18.28 | sop | 33,039 | 32.27 |
| req | 19,986 | 19.52 | dec | 35,296 | 34.47 |
| vcr | 21,318 | 20.82 | sysrs | 53,024 | 51.78 |

Total: 314,014 bytes (~306.66 KB) across the 12 domains. Schema-fetch
counts per session (formal runs): tsk-create-noprompt 0,
tsk-create-prompt 1, tsk-update-noprompt 0, tsk-update-prompt 0,
prb-create-noprompt 0, prb-create-prompt 1 (both attempts),
prb-update-noprompt 0, prb-update-prompt 0.

## What Phase 110 may use as the measurable ACC-003 baseline

With the fixed methodology (n=1 per cell, single pinned model, published
0.34.0 surface), these are the baseline numbers; a measurable target for
the follow-up plan should be stated against them, e.g.:

- "Median tool calls per successful tsk create without prompt: **5**"
  (with prompt: 9).
- "Median tool calls per successful prb create without prompt: **7**
  (including one validation-failure retry cycle); with prompt: 9."
- "Median tool calls per successful tsk update: **5** (noprompt) / **6**
  (prompt); per successful prb update: **5** in both conditions."
- "Schema-fetch rate without prompt: **0/4** runs; with prompt: **2/4**
  (create 2/2, update 0/2)."
- "Validation-failure -> retry cycles per successful create without
  prompt: **1** (prb, lead-sentence template mismatch); 0 (tsk)."
- "Wall clock per successful create: tsk **100.6 s** (noprompt) /
  **284.3 s** (prompt); prb **254.1 s** (noprompt) / **394.2 s**
  (prompt, retry; attempt 1 timed out at 600 s)."

Limitations to carry into Phase 110: single run per cell (no variance
estimate), one model, one host (opencode's 2-hop resource surface), and
the published 0.34.0 surface (the worktree is 33 commits ahead -- see
`schema-audit.md`). A follow-up experiment that repeats cells with n>=3
and on a host with 1-hop resource access would sharpen the perceived-cost
conclusion.
