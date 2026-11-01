# Evidence Manifest -- feat-128 Phase 100 controlled runs (Task 100.100/100.120)

Raw evidence for the 8 controlled `opencode run` experiments plus the
harness smoke/probe runs. Every instruction string is reproduced
verbatim below; event streams are the raw `--format json` output of
each run (one file per run, plus retry attempts).

## Environment

- opencode v1.18.34 (`/home/user/.opencode/bin/opencode`), non-interactive
  `opencode run --dir <run-dir> -m <model> --title <run-id> --format json`.

- Model pin (every run): `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2` (same model as the
  orchestrator session). The pin succeeded on all runs; no fallback
  was needed.

- MCP server: the global opencode config registers `specmgr` as
  `uvx --from "biz-dfch-specmgr[mcp, similarity]" specmgr mcp` -- the
  PUBLISHED package, with the session CWD as the document-base
  directory (no `SPECMGR_*_DIR` set). `asdste100` is also registered;
  the instructions constrain the agent to specmgr MCP tools (no
  asdste100 call appears in any event stream).

- Published version: `uvx --from "biz-dfch-specmgr[mcp, similarity]" specmgr version` -> **0.34.0**, equal to the worktree's
  `pyproject.toml` version (0.34.0) -- but the worktree is
  `v0.34.0-33-g27cbe27` (33 commits past the tag, 99 changed `src/`
  files; material agent-facing deltas: no `numbered` parameter on
  `get_<d>`, `update` returns frontmatter-only instead of the
  `UpdateResult` snippet wrapper, older tsk/prb update instructions,
  and schema diffs in 8 of 12 domains). Full diff in
  `../schema-audit.md`, section "Published-vs-worktree surface diff".

- Live published surface (probe via Python MCP client against the
  uvx server): 94 tools, 32 prompts, 44 resources (full name/title/
  description record committed as `mcp-surface-probe.txt`, reproducible
  via `harness/mcp_probe.py list <bare-dir>`; `specmgr://<d>/schema`
  present for exactly the 12 whole-body domains, none for adr).

- Prompt-pre-invoked mechanism: a probe run (`run-promptprobe.json`)
  proved a fresh opencode session **cannot invoke MCP prompts natively
  at all** (agent reply `NO_PROMPT_TOOL`, zero tool calls -- prompts
  are absent from the tool surface). All four `-prompt` runs therefore
  use the **harness-fetched** mechanism: the prompt was rendered by a
  throwaway Python MCP client (`mcp_probe.py`, `get_prompt` against
  the same uvx server) and prepended to the instruction, wrapped:

  ```text
  Step 0: The specmgr MCP prompt '<name>' was pre-invoked for you; its full rendered output is quoted between the markers below. Follow it as your first guidance, then complete the task given after the markers.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.

  === BEGIN pre-invoked prompt '<name>' output ===
  <rendered prompt text>
  === END pre-invoked prompt '<name>' output ===

  Task:
  <task text>
  ```

  Prompt arguments used at render time (recorded per run below):
  `create_task(topic=...)`, `update_task(id="UNKNOWN", instructions=...)`,
  `create_prb(topic=...)` (no `qa_id`), `update_prb(id="UNKNOWN", instructions=...)`. The update prompts' required `id` argument was
  deliberately filled with the placeholder `UNKNOWN` (never the seed
  UUID) so that document discovery via `list_<d>`/`get_<d>` stays part
  of the measured round trip in both conditions. The rendered prompt
  texts are preserved at `prompts/<name>.rendered.txt`.

## Seeds (update runs)

Before each update run, the harness wrote the seed document directly
into `<run-dir>/docs/<domain>/<uuid>.md` (fresh UUIDs per feature run,
valid frontmatter: version 1.0.0, status `active`, `created`/`updated`
2026-10-01, `type` set). The agent was never told the path or id.
Original (pre-run) seed content:

- `seeds/tsk_seed.md` -- id `5d0d4c60-982a-4db3-9029-61140049d5ec`,
  title "Onboarding the new build server", 3 unchecked tasks.
- `seeds/prb_seed.md` -- id `eddcc0ad-90b0-4239-a07f-eb4df2d15185`,
  title "Build server onboarding takes too long", complete 5W2H with
  Impact stating 1500 EUR per quarter.

Both seeds were verified parseable by the published server
(`list_tsk`/`list_prb` on the seeded dirs: 1 row, real title,
`error_count: 0`).

## Harness incident (discarded attempts, audit trail)

- A first runner attempt started the 8-run sequence correctly
  (`tsk-create-noprompt` 45 s, `tsk-create-prompt` 89 s, both clean)
  but was killed by its launcher's shell timeout mid-run-2; a second
  (mis-built) runner then re-executed `tsk-create-noprompt` and
  `tsk-create-prompt` **into directories that already contained the
  first attempt's created documents**, contaminating those two cells
  (a create run starting with an existing same-title document is not
  the controlled condition). Both contaminated outputs were discarded,
  all 8 run dirs were wiped, seeds re-placed with the same UUIDs, and
  the formal sequence re-run from a clean state (06:23-07:04). The
  discarded event streams were deleted; `runner.log` is git-ignored
  (`*.log`) and therefore not in the PR, so its lines for these cells
  (the four tsk-create executions, 06:13:47/06:15:16/06:25:15/
  06:30:12) are quoted verbatim below -- the first two are the
  contaminated first attempts (**not** part of the baseline), the
  latter two the formal clean re-runs:

  ```text
  2026-10-05T06:13:47+02:00 tsk-create-noprompt exit=0 duration=79s
  2026-10-05T06:15:16+02:00 tsk-create-prompt exit=0 duration=89s
  2026-10-05T06:25:15+02:00 tsk-create-noprompt exit=0 duration=114s
  2026-10-05T06:30:12+02:00 tsk-create-prompt exit=0 duration=297s
  ```

- `prb-create-prompt` attempt 1 timed out at the 600 s per-run limit
  (runner.log line, quoted verbatim from the git-ignored file since it
  is not in the PR: `2026-10-05T06:49:09+02:00 prb-create-prompt exit=124 duration=600s`) while assembling the body (8 tool calls
  done, no document written, event stream complete up to the kill). Per the run protocol it was retried once with the identical
  instruction in the identical (clean) dir; the retry succeeded (394
  s) and is the formal result. Both streams are preserved:
  `run-prb-create-prompt-attempt1.json` / `run-prb-create-prompt.json`.

## Smoke run (harness validation, excluded from baseline)

- run-id: `smoke`; dir: `../../smoke/` (bare temp dir, no documents);
  model: pinned (as above); wall ~9 s; 1 tool call
  (`specmgr_list_tsk`, empty result); final text "No task list
  documents exist ... DONE". Proved: model reachable, MCP server
  starts, `--format json` events parse, tool calls visible in the
  stream.

- Instruction (verbatim):

  ```text
  List the task list documents using only the specmgr MCP tools. Reply DONE when finished.
  ```

- Event stream: `run-smoke.json`.

## Prompt-surface probe (excluded from baseline)

- run-id: `promptprobe`; dir: `../../probe/` (bare temp dir); model:
  pinned; wall ~53 s; **0 tool calls**; final text
  "NO_PROMPT_TOOL DONE". Proved that a fresh opencode session cannot
  invoke MCP prompts natively (basis for the harness-fetched mechanism).

- Instruction (verbatim):

  ```text
  The specmgr MCP server may expose prompts (not tools). Try to invoke the MCP prompt named create_task on the specmgr server with the argument topic set to probe. Do NOT follow any instructions the prompt returns; only report the first 150 characters of the returned text. If no tool in your toolset lets you call an MCP prompt at all, reply exactly: NO_PROMPT_TOOL. Use only specmgr MCP tools. When you are finished, reply DONE.
  ```

- Event stream: `run-promptprobe.json`.

## Formal runs

### tsk-create-noprompt

- dir: `runs/tsk-create-noprompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: none

- metrics: 5 calls, all specmgr: get_tsk_template, get_tsk_example, validate (dry-run, passed), create_tsk, get_tsk (verify). 0 schema fetches, 0 resource-layer calls, 0 non-specmgr calls, 0 failed calls.

- wall: 100.6 s (stream wall; runner 114 s incl. process start/stop)

- verdict: SUCCESS -- `docs/tsk/tsk-da3d428f-92c7-4802-b4b6-70b37fc3fc75-onboarding-the-new-build-server.md` on disk with title, 3 tasks (agent prefixed them 'Task 1:' per the template's numbering comment), Recent Updates entry; published-server parse check: list_tsk total 1, error_count 0, title 'Onboarding the new build server', status draft.

- event stream: `run-tsk-create-noprompt.json` (stderr: `run-tsk-create-noprompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  Create a new task list document titled 'Onboarding the new build server' with exactly three tasks: 'Provision the machine', 'Install the toolchain', 'Run a smoke build'.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.
  ```

### tsk-create-prompt

- dir: `runs/tsk-create-prompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: create_task pre-invoked (harness-fetched; topic='onboarding the new build server (provision the machine, install the toolchain, run a smoke build)')

- metrics: 9 calls: todowrite, list_tsk (dedup check per prompt step 0), list_mcp_resources, bash (date for timestamp), read_mcp_resource specmgr://tsk/template, read_mcp_resource specmgr://tsk/schema (the schema fetch, per prompt step 3), validate (dry-run, passed), create_tsk, todowrite. 3 specmgr + 6 host-level calls, 1 schema fetch, 1 template fetch (resource route = 2 hops), 0 failed calls.

- wall: 284.3 s (runner 297 s)

- verdict: SUCCESS -- `docs/tsk/tsk-35bc9737-14c5-4b9f-a628-3ca3d91e7229-onboarding-the-new-build-server.md` on disk with title, 3 exact tasks, Recent Updates entry; published-server parse check: list_tsk total 1, error_count 0, status draft.

- event stream: `run-tsk-create-prompt.json` (stderr: `run-tsk-create-prompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  Step 0: The specmgr MCP prompt 'create_task' was pre-invoked for you; its full rendered output is quoted between the markers below. Follow it as your first guidance, then complete the task given after the markers.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.

  === BEGIN pre-invoked prompt 'create_task' output ===
  You are drafting a new Task List (TSK) document about: onboarding the new build server (provision the machine, install the toolchain, run a smoke build)

  Follow this structure and tool sequence exactly. Do not write raw
  markdown yourself beyond the body content you pass to `create_tsk` --
  every write to disk goes through the specmgr MCP tools listed below.
  There is no frontmatter for you to draft: `create_tsk` builds
  id/type/status/created/updated/version automatically.

  Make a todo list and use the question tool.

  ## 0. Check for an existing task list on this topic first
  Call the `list_tsk` tool before creating anything. If a
  task list with a similar title or topic already exists, tell the user
  about it and ask whether they want to revise that one (via the
  `update_task` prompt) instead of creating a duplicate. Only proceed to
  step 1 if this is genuinely a new task list.

  ## 1. Structure recap (body markdown only, no frontmatter block)
  - `# {title}` -- H1, mandatory, free-form.
  - `<!-- optional leading comment -->` -- optional HTML comment right
    after the H1, giving context for the task list as a whole.
  - A flat checklist, one `- [ ] ...`/`- [x] ...` entry per line --
    mandatory, at least one item. No phases, no per-item `depends on`/
    `status` metadata -- this is a deliberately lightweight, flat list.
  - `## Recent Updates` -- mandatory H2 section, an optional leading HTML
    comment (e.g. an ordering hint) followed by at least one
    `### {timestamp} ( - | : ) {title}` entry, newest-first, where
    `{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.fff` +
    `Z` or `±HH:mm` (e.g. `### 2026-08-19 05:42:00.000+02:00 - Created`),
    each followed by a short paragraph of update text. The date/time
    separator may be `T` or a space; a date-only timestamp is rejected. A
    freshly drafted task list must include at least one Recent Updates
    entry describing why this list was made --
    `RecentUpdates.updates` requires `min_length>=1`, so an empty section
    (or omitting it) will fail validation. `create_tsk` does not seed
    this entry automatically; you must include it yourself.

  ## 2. Gather information before calling any tool
  Elicit (asking the user if not already given): the checklist items to
  track, and a short description of why this task list is being created
  for the first `## Recent Updates` entry.

  ## 3. Use the template/example/schema as references
  Fetch `specmgr://tsk/template` or `specmgr://tsk/example` as a starting
  point/style reference, then check `specmgr://tsk/schema` (the generated
  JSON Schema) to confirm field names and constraints before drafting the
  body. Do not invent field names or section headings that are not present
  there.

  ## 4. Tool call sequence
  1. Draft the body-only markdown per the structure above, including at
     least one checklist item and at least one `## Recent Updates` entry.
  2. Call `create_tsk(content)` -- `content` is body markdown only; the
     entire frontmatter is built automatically. A structural or field
     validation failure raises uncaught and nothing is written.
  3. Optionally call `validate(type="tsk", content=content, full=False)` first if you want
     to dry-run the body without writing anything -- `create_tsk` already
     performs the same validation internally, so this step is never
     required, only a convenience.

  ## 5. Later revisions
  Any later change to this task list should go through the `update_task`
  prompt (or directly through the generic `update(id, type="tsk", content)`,
  `set_status(id, type="tsk", status)`, and
  `set_classification(id, type="tsk", classification)` tools), not by
  re-running this prompt. To work through the checklist itself, use the
  `implement_task` prompt instead.
  === END pre-invoked prompt 'create_task' output ===

  Task:
  Create a new task list document titled 'Onboarding the new build server' with exactly three tasks: 'Provision the machine', 'Install the toolchain', 'Run a smoke build'.
  ```

### tsk-update-noprompt

- dir: `runs/tsk-update-noprompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: none

- metrics: 5 calls, all specmgr: list_tsk(max_results=100) (discovery), get_tsk(raw=true) (read), edit x2 (surgical: '- [ ] Provision the machine' -> '- [x] ...'; insert '- [ ] Document the setup' after '- [ ] Run a smoke build'), get_tsk(raw=true) (verify). 0 schema/template/example/validate calls, 0 failed calls. Note: the agent chose the generic `edit` tool (exact-match string replace) rather than `update` for both changes.

- wall: 84.5 s (runner 97 s)

- verdict: SUCCESS -- seed document updated in place (`docs/tsk/5d0d4c60-...md`): '- [x] Provision the machine', '- [ ] Document the setup' present, all other lines intact; published-server parse check: list_tsk total 1, error_count 0, status active.

- event stream: `run-tsk-update-noprompt.json` (stderr: `run-tsk-update-noprompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  In the task list document titled 'Onboarding the new build server', mark the task 'Provision the machine' as done and add a new task 'Document the setup'.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.
  ```

### tsk-update-prompt

- dir: `runs/tsk-update-prompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: update_task pre-invoked (harness-fetched; id='UNKNOWN' placeholder, instructions='mark the task Provision the machine as done and add a new task Document the setup')

- metrics: 6 calls: list_tsk (discovery -- the prompt's id was the placeholder, so the agent resolved the id from the title), get_tsk, get_tsk(raw=true), bash (date for the new Recent Updates timestamp), update (WHOLE-BODY replace carrying forward all sections + new newest-first Recent Updates entry), get_tsk(raw=true) (verify). 0 schema fetches despite prompt step 4 'Check the schema'; 0 validate calls; 0 failed calls.

- wall: 161.3 s (runner 174 s)

- verdict: SUCCESS -- seed document updated in place: '- [x] Provision the machine', '- [ ] Document the setup', new '### 2026-10-05 06:33:51.836+02:00 - Updated checklist' entry added newest-first; published-server parse check: list_tsk total 1, error_count 0, status active.

- event stream: `run-tsk-update-prompt.json` (stderr: `run-tsk-update-prompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  Step 0: The specmgr MCP prompt 'update_task' was pre-invoked for you; its full rendered output is quoted between the markers below. Follow it as your first guidance, then complete the task given after the markers.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.

  === BEGIN pre-invoked prompt 'update_task' output ===
  You are revising an existing Task List (TSK) document, id: UNKNOWN

  Requested change: mark the task 'Provision the machine' as done and add a new task 'Document the setup'

  Follow this sequence exactly. Do not write raw markdown yourself beyond
  the body content you pass to `update` -- every change to the document
  goes through the specmgr MCP tools listed below.

  ## 1. Read current state first
  Call `get_tsk(id)` to load the document's current frontmatter and body.
  Never assume prior state -- the on-disk file is always the source of
  truth and may have been hand-edited since you last saw it.

  ## 2. If no change was specified
  If "Requested change" above says "(not given)", ask the user what they
  want to change before calling any write tool.

  ## 3. Map the requested change to the right tool
  - A change to the body -- the checklist items, the leading comment, or
    adding a new `## Recent Updates` entry -- -> the generic `update`
    tool called with `type="tsk"`, either as a **line-range replace** for
    a localized change or a **whole-body replace** otherwise. `content`
    is body markdown only (no frontmatter block) in both cases.
    - **Line-range replace** (a localized change -- one paragraph, field,
      or section): first call `get_tsk(id, raw=True)` to see the exact
      body text, identify the 1-based line to start at and how many lines
      to replace -- `offset` is the first body line, `limit` the number of
      lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
      the last body line, `limit=0` is a pure insert, and the `N+1`
      position is end-of-body: `offset = N+1` appends after the last line
      -- and call `update(id, type="tsk", content, offset=..., limit=...)`
      passing only the replacement lines. The server splices the fragment
      into the current on-disk body and validates the result as a whole
      document before writing anything, so every out-of-range line stays
      byte-identical. Adding a new `## Recent Updates` entry is typically
      a line-range insert directly below the section's optional leading
      comment (or directly below the `## Recent Updates` heading if no
      comment is present) -- new entries go first, since the section is
      newest-first, enforced. Each entry's heading is
      `### {timestamp} ( - | : ) {title}`, where `{timestamp}` is the full
      date+time form `yyyy-MM-dd[T ]HH:mm:ss.fff` + `Z` or `±HH:mm` (the
      date/time separator may be `T` or a space; a date-only timestamp is
      rejected), followed by a short paragraph of update text.
    - **Whole-body replace** (a multi-section change, or whenever you are
      uncertain about the line range): call `update(id, type="tsk", content)`
      with no `offset`/`limit` -- `content` is then the full replacement body:
      read the current body first (step 1) and carry forward every section
      you are not intentionally changing, or it will be dropped.
      `id`/`type`/`status`/`created`/`version` are preserved automatically
      regardless of what you submit; only `updated` changes. In
      particular, `## Recent Updates` requires at least one entry at all
      times -- if you are not adding a new one, carry forward every
      existing entry; removing the last remaining entry would fail
      validation (`RecentUpdates.updates` requires `min_length>=1`).
  - A change to `status` -> `set_status(id, type="tsk", status)` instead
    -- `update` never accepts or changes `status`. `status` must be one
    of: draft, active, done, cancelled.
  - A change to `classification` ->
    `set_classification(id, type="tsk", classification)` instead --
    `update` never accepts or changes `classification`. Fully free-text;
    a blank or whitespace-only value clears it back to `None`/absent.

  ## 4. Check the schema, and validate before writing if useful
  Fetch `specmgr://tsk/schema` to confirm field names and constraints
  before drafting the replacement body. Optionally call
  `validate(type="tsk", content=content, full=False)` beforehand to dry-run the new body
  without writing anything -- `update` already performs the same
  validation internally, so this step is never required, only a
  convenience.

  To actually work through the checklist items themselves (marking them
  done, asking clarifying questions), use the `implement_task` prompt
  instead of this one.
  === END pre-invoked prompt 'update_task' output ===

  Task:
  In the task list document titled 'Onboarding the new build server', mark the task 'Provision the machine' as done and add a new task 'Document the setup'.
  ```

### prb-create-noprompt

- dir: `runs/prb-create-noprompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: none

- metrics: 7 calls, all specmgr: get_prb_template, get_prb_example, create_prb (ATTEMPT 1 -- FAILED opaquely: 'Error executing tool create_prb' -- the agent wrote a natural sentence, not the fixed frame), validate (dry-run of attempt 1 -- the agent's own text says it validated to find the issue; the `validate` error is where it learned the frame, verbatim and truncated at feat-110's 300-char cap: 'prb validate (body): Value error, problem_statement must match the template [Current state] is causing [specific issue], for [stakeholder] because [underlying cause]., got Onboarding a new build server currently takes 3 to 4 working days of manual wo... (truncated)'), validate (dry-run of corrected draft -- passed), create_prb (ATTEMPT 2 -- succeeded), get_prb (verify). 0 schema fetches; 1 validation-failure -> retry cycle (+2 calls over the minimum path); 1 failed call.

- wall: 254.1 s (runner 266 s)

- verdict: SUCCESS -- `docs/prb/prb-a1bb38fe-007a-4b13-854c-6097c9cfe1c6-build-server-onboarding-takes-too-long.md` on disk with title, template-conform lead sentence, all 7 5W2H sections, Summary, Gap, Impact, Future State; published-server parse check: list_prb total 1, error_count 0, status draft.

- event stream: `run-prb-create-noprompt.json` (stderr: `run-prb-create-noprompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  Create a new problem statement document titled 'Build server onboarding takes too long' with the following content. Summary of the current state: onboarding a new build server currently takes 3 to 4 working days of manual work; the steps live in a shared chat thread and in the heads of two engineers, and every new server needs a person to walk through the setup step by step before it can run the first build. What is the problem: provisioning and configuring a new build server is a manual, undocumented process. Why it is a problem: every new server blocks project kickoffs until a senior engineer is available to drive the setup, and knowledge loss has already caused two broken handovers. Where it is observed: in the DevOps build environment, during every build-server addition. Who is impacted: engineering managers planning project start dates and the build teams waiting for usable infrastructure. When it was first observed: during the first build-server handover in March 2026. How it is observed: late project kickoffs and post-handover incidents that trace back to missing setup steps. How often it is observed: once per new build server, which the current plan puts at one to two servers per quarter. Gap: a new build server takes 3 to 4 working days to onboard, while the expected duration is half a day of largely automated setup. Impact: the delay costs the team approximately 1500 EUR per quarter in rework and lost schedule buffer. Future state: a new build server is provisioned, configured, and verified by an automated runbook in under half a day, without a senior engineer driving the setup.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.
  ```

### prb-create-prompt

- dir: `runs/prb-create-prompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: create_prb pre-invoked (harness-fetched; topic='build server onboarding takes too long (3 to 4 days manual setup per new server; expected half a day automated)', no qa_id)

- metrics: ATTEMPT 1 (discarded formal result, timeout): 8 calls -- todowrite, list_prb, get_prb_template, get_prb_example, list_mcp_resources, read_mcp_resource specmgr://prb/schema (schema fetch, per prompt step 10), todowrite, validate (dry-run, passed) -- then timed out at 600 s while assembling the body; no document written. FORMAL (retry, identical instruction/dir): 9 calls -- todowrite, list_prb, list_mcp_resources, read_mcp_resource specmgr://prb/template, read_mcp_resource specmgr://prb/schema (schema fetch), validate (dry-run, passed), create_prb (first-try success -- correct lead sentence 'Manual build server onboarding is causing 3 to 4 working days per new server, for engineering managers and build teams because ...'), get_prb (verify), todowrite. 1 schema fetch, 1 template fetch (resource route), 0 failed calls.

- wall: attempt 1: 600 s (timeout, exit 124); retry (formal): 394.2 s (runner logged 07:03:44)

- verdict: SUCCESS (retry) -- `docs/prb/prb-5d58c9b0-44df-457a-acc5-a8a0177b0057-build-server-onboarding-takes-too-long.md` on disk with title, template-conform lead sentence, Summary + all 7 5W2H sections, Gap, Impact, Future State; published-server parse check: list_prb total 1, error_count 0, status draft.

- event streams: attempt 1 `run-prb-create-prompt-attempt1.json` (stderr `run-prb-create-prompt-attempt1.stderr`, empty); formal retry `run-prb-create-prompt.json` (stderr `run-prb-create-prompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run` for both attempts):

  ```text
  Step 0: The specmgr MCP prompt 'create_prb' was pre-invoked for you; its full rendered output is quoted between the markers below. Follow it as your first guidance, then complete the task given after the markers.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.

  === BEGIN pre-invoked prompt 'create_prb' output ===
  You are drafting a new Problem Statement (PRB) document about: build server onboarding takes too long (3 to 4 days manual setup per new server; expected half a day automated)

  Linked QA document id (optional): (not given -- proceed standalone, asking all 7 5W2H questions)

  Follow this structure and tool sequence exactly. Do not write raw
  markdown yourself beyond the body content you pass to `create_prb` --
  every write to disk goes through the specmgr MCP tools listed below.
  There is no frontmatter for you to draft: `create_prb` builds
  id/type/status/created/updated/version automatically.

  Make a todo list and use the question tool.

  ## 0. Check for an existing problem statement on this topic first

  Call the `list_prb` tool before creating anything. If a problem
  statement with a similar title or topic already exists, tell the user
  about it and ask (via the `question` tool) whether they want to revise
  that one (via the `update_prb` prompt) instead of creating a duplicate.
  Only proceed to step 1 if this is genuinely a new problem statement.

  ## 1. Structure recap (body markdown only, no frontmatter block)

  - `# {title}` -- H1, mandatory, free-form.
  - `<!-- optional leading comment -->` -- optional HTML comment right
    after the H1, giving context for the problem statement as a whole.
  - `{lead sentence}` -- mandatory, no heading of its own, directly under
    the H1 (after the optional comment). Exactly one sentence following
    the fixed template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- the surrounding wording,
    punctuation, and single trailing period must stay verbatim; only the
    four bracketed blanks are filled in. Enforced at the code level by
    `create_prb`/`validate` -- a sentence that does not match the template
    is rejected with an actionable error. See step 9 for how to compose it.
  - `## Current State` -- mandatory.
    - `### Summary` -- mandatory. A free-form synthesis of the current
      state, drawn from whichever of the 7 5W2H questions below are
      actually answered. Must always carry *some* text, even if every
      question below is still unanswered.
    - Seven fixed, optional `### ` 5W2H question headings, each always
      written verbatim (do not rename, reorder, renumber, or omit any of
      them -- an unanswered question is simply left out entirely, not
      written with empty content): `### What Is the Problem?`,
      `### Why Is It a Problem?`, `### Where Is the Problem Observed?`,
      `### Who Is Impacted?`, `### When Was the Problem First Observed?`,
      `### How Is the Problem Observed?`,
      `### How Often Is the Problem Observed?`.
  - `## Gap` -- mandatory. The measurable, actual-vs-expected difference
    between the current and future state. Kept a pure measurement,
    deliberately not conflated with `Impact` (the consequence of the gap).
  - `## Impact` -- optional. The business/cost/safety consequence of the
    gap.
  - `## Future State` -- mandatory. The desired/target condition once the
    problem is resolved.
  - `## References` -- optional freeform cross-references to other
    artifacts/tickets.
  - `## More Information` -- optional freeform supplementary text.

  No `## Root Cause` section exists; the lead sentence carries the
  best-known cause by design (its `because [underlying cause]` clause);
  formal root-cause analysis remains a separate, later activity.

  ## 2. If a QA id was given, fetch it and carry over already-answered questions

  If "Linked QA document id" above is not "(not given -- proceed
  standalone, asking all 7 5W2H questions)", call `get_qa(qa_id)`.

  - **If `get_qa` raises `QaNotFoundError`** (the id does not resolve to
    any QA document): tell the user the lookup failed and why, then use
    the `question` tool to ask whether they want to (a) proceed standalone
    -- all 7 5W2H questions asked fresh, nothing pre-filled -- or
    (b) retry with a corrected QA id. Never silently fall through to
    standalone behavior without telling the user why. If they give a
    corrected id, repeat this step with it.
  - **If `get_qa` succeeds**: scan *every one* of the returned document's
    10 Q&A-holding categories -- `## Elicitation Context` plus all 9
    ISO/IEC 25010:2023 characteristic sections (`Functional Suitability`,
    `Performance Efficiency`, `Compatibility`, `Interaction Capability`,
    `Reliability`, `Security`, `Maintainability`, `Flexibility`, `Safety`)
    -- not only `Elicitation Context`. Each category holds zero or more
    adjacent `> **<d>.<NNNN>**: {question}`
    block-quote-plus-free-prose-answer pairs, with no heading of its own
    per pair. For each pair, judge whether its
    question/answer best matches one of the PRB's 7 5W2H sub-questions
    (What/Why/Where/Who/When/How/How Often). Apply these rules:
    - **One pair, at most one question**: a single QA pair maps to *at
      most one* 5W2H sub-question -- the single best match, never
      duplicated across two sub-questions. Worked example: a QA pair whose
      question is "When does the checkout page time out?" and whose answer
      is "During peak traffic hours, right at the payment confirmation
      step" could plausibly answer both `### When Was the Problem First Observed?` (the "peak traffic hours" timing) and
      `### Where Is the Problem Observed?` (the "payment confirmation
      step" location). Best match only: pick the single sub-question the
      pair's own *question wording* most directly matches -- here, `When`,
      since the QA question literally asks "when" -- and leave the other
      sub-question (`Where`) unanswered rather than copying the same pair
      into both.
    - **Non-committal counts as unanswered**: if the QA pair's answer is
      non-committal (e.g. "unknown", "not yet answered", "TBD", or the
      `TODO: ` placeholder -- `TODO: answer pending` is the convention's
      example form -- QA uses for a question nobody has answered yet),
      treat that sub-question as *not* pre-filled -- do not carry over a
      non-answer.
    - A matched, committal answer is pre-filled directly into the
      corresponding `### {question heading}` under `## Current State`,
      verbatim or lightly cleaned up for standalone readability -- do not
      re-ask it in step 3.

  ## 3. Build a todo list, then gather whichever 5W2H answers remain

  Build a todo list with one entry per: `Summary`, each of the 7 5W2H
  questions still unanswered after step 2, `Gap`, `Impact`,
  `Future State`, and the Problem Statement lead sentence. Then use the
  `question` tool to elicit only whichever of the 7 5W2H answers were
  *not* already pre-filled in step 2 (all 7, if no QA id was given, it did
  not resolve, or nothing pre-filled) -- What/Why/Where/Who/When/How/How
  Often, skipping any already answered -- explicitly telling the user they
  may skip any remaining question they cannot or do not want to answer yet
  -- a freshly created problem statement may have zero questions answered.

  ## 4. Synthesize the Summary

  Once you have the complete set of 5W2H answers (pre-filled plus freshly
  gathered), draft a `Summary` paragraph synthesizing them into a coherent,
  factual description of the current state. If zero questions were
  answered, write a short placeholder `Summary` instead (it is mandatory
  and must always carry some text).

  ## 5. Draft and confirm the Gap

  Draft a candidate `Gap` statement from the collected current-state
  answers, following an expected-vs-actual/measurable-difference formula
  (e.g. "X happens in N% of cases; the expected behavior is Y"). Show this
  draft to the user and use the `question` tool to confirm or refine it
  before finalizing -- do not finalize `Gap` without this confirmation
  step.

  ## 6. Optionally ask for Impact

  Use the `question` tool to ask whether the user wants to record an
  `Impact` (the business/cost/safety consequence of the gap). Skip this
  section entirely if they decline.

  ## 7. Ask for Future State

  Use the `question` tool to ask for the desired/target condition once the
  problem is resolved. `Future State` is mandatory.

  ## 8. Optionally ask for References/More Information

  Use the `question` tool to ask whether the user wants to add
  `References` (cross-references to other artifacts/tickets) or
  `More Information`. Skip either section entirely if they decline.

  ## 9. Compose the Problem Statement lead sentence

  The lead sentence has four blanks: `[Current state]`, `[specific issue]`, `[stakeholder]`, and `[underlying cause]`.

  - **QA-linked mode** (a QA id was given, resolved, and at least one of
    `What`/`Who`/`Why` was pre-filled in step 2): derive a first draft of
    the blanks from those pre-filled answers before asking anything fresh:
    `What` -> both `[Current state]` and `[specific issue]` (a single `What` answer must populate two distinct blanks, so draft your best split of it across the two -- e.g. the underlying condition into `[Current state]`, the concrete symptom into `[specific issue]`); `Who` -> `[stakeholder]`; `Why` -> `[underlying cause]`.
    For any blank with no pre-filled answer to derive from, use the
    `question` tool to ask for it directly. Then show the fully composed
    sentence to the user and use the `question` tool to **confirm** it
    (this confirmation step is what catches a bad `What` split) -- never ask all 4 blanks as fresh questions in this mode.
  - **Standalone mode** (no QA id was given, it did not resolve, or
    nothing was pre-filled): use the `question` tool to elicit all 4
    blanks as fresh questions, then compose and show the sentence for
    confirmation the same way.

  The final sentence must match the template exactly except for the four
  filled-in blanks: `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].`.

  ## 10. Use the template/example/schema as references

  Fetch `specmgr://prb/template` or `specmgr://prb/example` as a starting
  point/style reference, then check `specmgr://prb/schema` (the generated
  JSON Schema) to confirm field names and constraints before drafting the
  body. Do not invent field names or section headings that are not present
  there.

  ## 11. Tool call sequence

  1. Assemble the full body-only markdown per the structure above, from
     the answers gathered in steps 2-9.
  2. Call `create_prb(content)` -- `content` is body markdown only; the
     entire frontmatter is built automatically. A structural or field
     validation failure raises uncaught and nothing is written.
  3. Optionally call `validate(type="prb", content=content, full=False)` first if you want
     to dry-run the body without writing anything -- `create_prb` already
     performs the same validation internally, so this step is never
     required, only a convenience.

  ## 12. Later revisions

  Any later change to this problem statement should go through the
  `update_prb` prompt (or directly through the generic
  `update(id, type="prb", content)`, `set_status(id, type="prb", status)`,
  and `set_classification(id, type="prb", classification)` tools), not by
  re-running this prompt.
  === END pre-invoked prompt 'create_prb' output ===

  Task:
  Create a new problem statement document titled 'Build server onboarding takes too long' with the following content. Summary of the current state: onboarding a new build server currently takes 3 to 4 working days of manual work; the steps live in a shared chat thread and in the heads of two engineers, and every new server needs a person to walk through the setup step by step before it can run the first build. What is the problem: provisioning and configuring a new build server is a manual, undocumented process. Why it is a problem: every new server blocks project kickoffs until a senior engineer is available to drive the setup, and knowledge loss has already caused two broken handovers. Where it is observed: in the DevOps build environment, during every build-server addition. Who is impacted: engineering managers planning project start dates and the build teams waiting for usable infrastructure. When it was first observed: during the first build-server handover in March 2026. How it is observed: late project kickoffs and post-handover incidents that trace back to missing setup steps. How often it is observed: once per new build server, which the current plan puts at one to two servers per quarter. Gap: a new build server takes 3 to 4 working days to onboard, while the expected duration is half a day of largely automated setup. Impact: the delay costs the team approximately 1500 EUR per quarter in rework and lost schedule buffer. Future state: a new build server is provisioned, configured, and verified by an automated runbook in under half a day, without a senior engineer driving the setup.
  ```

### prb-update-noprompt

- dir: `runs/prb-update-noprompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: none

- metrics: 5 calls, all specmgr: list_prb (discovery), get_prb(raw=true) (read), edit (surgical: 'approximately 1500 EUR per quarter' -> 'approximately 2500 EUR per quarter'), get_prb(raw=true, offset=49, limit=3) + get_prb(raw=true, offset=45, limit=4) (windowed verifies). 0 schema/template/example/validate calls, 0 failed calls. The agent chose `edit` again over `update`.

- wall: 100.5 s (runner 118 s)

- verdict: SUCCESS -- seed document updated in place: line 57 now 'The delay costs the team approximately 2500 EUR per quarter in rework and lost schedule buffer.'; all other lines intact; published-server parse check: list_prb total 1, error_count 0, status active.

- event stream: `run-prb-update-noprompt.json` (stderr: `run-prb-update-noprompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  In the problem statement document titled 'Build server onboarding takes too long', change the cost stated in the Impact section from 1500 EUR per quarter to 2500 EUR per quarter.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.
  ```

### prb-update-prompt

- dir: `runs/prb-update-prompt/` (bare temp dir; update runs pre-seeded per above)

- model: pinned (`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`)

- condition: update_prb pre-invoked (harness-fetched; id='UNKNOWN' placeholder, instructions='change the cost stated in the Impact section from 1500 EUR per quarter to 2500 EUR per quarter')

- metrics: 5 calls, all specmgr: list_prb (discovery), get_prb, get_prb(raw=true), update (LINE-RANGE replace: offset=47, limit=1, content='The delay costs the team approximately 2500 EUR per quarter in rework and lost schedule buffer.' -- the agent counted body lines from the raw read, as the published prompt instructs), get_prb(raw=true, offset=45, limit=3) (verify). 0 schema fetches despite prompt step 9 'Check the schema'; 0 validate calls; 0 failed calls.

- wall: 66.9 s (runner 80 s)

- verdict: SUCCESS -- seed document updated in place: line 57 of the file (body line 47) now states 2500 EUR per quarter; published-server parse check: list_prb total 1, error_count 0, status active.

- event stream: `run-prb-update-prompt.json` (stderr: `run-prb-update-prompt.stderr`, empty)

- instruction (verbatim, as passed to `opencode run`):

  ```text
  Step 0: The specmgr MCP prompt 'update_prb' was pre-invoked for you; its full rendered output is quoted between the markers below. Follow it as your first guidance, then complete the task given after the markers.

  Use only the specmgr MCP tools to complete the task. When the document change is complete, reply DONE.

  === BEGIN pre-invoked prompt 'update_prb' output ===
  You are revising an existing Problem Statement (PRB) document, id: UNKNOWN

  Requested change: change the cost stated in the Impact section from 1500 EUR per quarter to 2500 EUR per quarter

  Follow this sequence exactly. Do not write raw markdown yourself beyond
  the body content you pass to `update` -- every change to the document
  goes through the specmgr MCP tools listed below.

  ## 1. Read current state first

  Call `get_prb(id)` to load the document's current frontmatter and body.
  Never assume prior state -- the on-disk file is always the source of
  truth and may have been hand-edited since you last saw it.

  **Old-shape recovery.** If this call fails to parse because the body is
  missing the mandatory lead sentence directly under the H1 (a document
  drafted before that field became mandatory), do not treat this as a
  fatal error:

  1. Re-read the body verbatim via `get_prb(id, raw=True)` -- this never
     parses the body, so it always succeeds even for an old-shape
     document.
  2. Look at the document's own `### What Is the Problem?`,
     `### Who Is Impacted?`, and `### Why Is It a Problem?` answers (if
     present) under `## Current State`. Derive a first draft of the lead
     sentence's 4 blanks from them the same way `create_prb`'s own
     derive-then-confirm flow does: `What` -> both `[Current state]` and `[specific issue]` (a single `What` answer must populate two distinct blanks, so draft your best split of it across the two -- e.g. the underlying condition into `[Current state]`, the concrete symptom into `[specific issue]`); `Who` -> `[stakeholder]`; `Why` -> `[underlying cause]`.
     For any blank with no answer to derive from, use the `question` tool
     to ask for it directly. Then show the fully composed sentence --
     `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- to the user and use
     the `question` tool to confirm or refine it.
  3. Insert the confirmed sentence as its own paragraph directly under the
     H1 title (after any existing leading comment, before `## Current State`) into the raw body text from step 1.
  4. Call `update(id, type="prb", content)` with that spliced body (a
     whole-body replace, since the insertion touches line numbers you have
     not yet re-counted) so the document becomes parseable again, then
     call `get_prb(id)` once more -- it must now succeed -- before
     proceeding to step 2 below with the originally requested change.

  ## 2. If no change was specified

  If "Requested change" above says "(not given)", ask the user what they
  want to change before calling any write tool.

  ## 3. Show which of the 7 questions are already answered

  Show the user which of the 7 5W2H questions under `## Current State`
  already have answers (`### What Is the Problem?`,
  `### Why Is It a Problem?`, `### Where Is the Problem Observed?`,
  `### Who Is Impacted?`, `### When Was the Problem First Observed?`,
  `### How Is the Problem Observed?`,
  `### How Often Is the Problem Observed?`) and which are still
  empty/absent. Use the `question` tool to ask which ones (if any) they
  want to add to or revise.

  ## 4. Elicit the new/revised answers

  For each question selected in step 3, use the `question` tool to elicit
  the new or revised text.

  ## 5. Regenerate the Summary from the complete, current set of answers

  Regenerate `### Summary` from the *complete* current set of 5W2H answers
  (the ones carried forward unchanged plus whatever was just revised) --
  this is a full re-synthesis, not an append of the new text onto the old
  `Summary`.

  ## 6. Re-draft and confirm the Gap

  Re-draft `## Gap` the same way as the `create_prb` prompt's own step 4
  (an expected-vs-actual/measurable-difference formula), based on the
  now-current-state answers. Show this draft to the user and use the
  `question` tool to confirm or refine it before finalizing.

  ## 7. Optionally revise Impact/Future State/References/More Information

  Use the `question` tool to ask whether the user wants to revise
  `## Impact`, `## Future State`, `## References`, or `## More Information`.
  Leave any section the user does not want to change exactly as read in
  step 1.

  ## 8. Map the requested change to the right tool

  - A change to the body -- any of the above -- -> the generic `update`
    tool called with `type="prb"`, either as a **line-range replace** for
    a localized change or a **whole-body replace** otherwise. `content`
    is body markdown only (no frontmatter block) in both cases.
    - **Line-range replace** (a localized change -- one paragraph, field,
      or section): first call `get_prb(id, raw=True)` to see the exact
      body text, identify the 1-based line to start at and how many lines
      to replace -- `offset` is the first body line, `limit` the number of
      lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
      the last body line, `limit=0` is a pure insert, and the `N+1`
      position is end-of-body: `offset = N+1` appends after the last line
      -- and call `update(id, type="prb", content, offset=..., limit=...)`
      passing only the replacement lines. The server splices the fragment
      into the current on-disk body and validates the result as a whole
      document before writing anything, so every out-of-range line stays
      byte-identical.
    - **Whole-body replace** (a multi-section change, or whenever you are
      uncertain about the line range): call `update(id, type="prb", content)`
      with no `offset`/`limit` -- `content` is then the full replacement body:
      read the current body first (step 1) and carry forward every section
      you are not intentionally changing, or it will be dropped.
      `id`/`type`/`status`/`created`/`version` are preserved automatically
      regardless of what you submit; only `updated` changes.
  - A change to `status` -> `set_status(id, type="prb", status)` instead
    -- `update` never accepts or changes `status`. `status` must be one
    of: draft, active, resolved, cancelled. Mention this as a
    separate, optional follow-up once `Future State` has genuinely been
    reached
    (`resolved`) or the problem statement is abandoned (`cancelled`) -- do
    not call `set_status` unless the user actually asks for a status
    change.
  - A change to `classification` ->
    `set_classification(id, type="prb", classification)` instead --
    `update` never accepts or changes `classification`. Fully free-text;
    a blank or whitespace-only value clears it back to `None`/absent.

  ## 9. Check the schema, and validate before writing if useful

  Fetch `specmgr://prb/schema` to confirm field names and constraints
  before drafting the replacement body. Optionally call
  `validate(type="prb", content=content, full=False)` beforehand to dry-run the new body
  without writing anything -- `update` already performs the same
  validation internally, so this step is never required, only a
  convenience.
  === END pre-invoked prompt 'update_prb' output ===

  Task:
  In the problem statement document titled 'Build server onboarding takes too long', change the cost stated in the Impact section from 1500 EUR per quarter to 2500 EUR per quarter.
  ```

## Agent-facing metadata (verbatim, published 0.34.0 surface)

The committed probe output `mcp-surface-probe.txt` -- captured
2026-10-05 by running `harness/mcp_probe.py list <bare-dir>` against
`uvx --from "biz-dfch-specmgr[mcp, similarity]" specmgr mcp`, i.e. the
exact published 0.34.0 surface the Phase 100 agents saw (94 tools, 32
prompts, 44 resources; reproducible from this harness) -- is the source
of the verbatim strings below, which back the claims in
`../schema-audit.md`'s "Agent-facing metadata audit (verbatim)".

### The 12 `specmgr://<d>/schema` resource name/title/description triples

- `specmgr://req/schema` -- `name="req_schema"`, `title="Requirement (REQ) JSON Schema"`
  description (verbatim): "The generated REQ JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://uc/schema` -- `name="uc_schema"`, `title="Use Case (UC) JSON Schema"`
  description (verbatim): "The generated UC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://tsk/schema` -- `name="tsk_schema"`, `title="Task List (TSK) JSON Schema"`
  description (verbatim): "The generated TSK JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://qa/schema` -- `name="qa_schema"`, `title="Question and Answer (QA) JSON Schema"`
  description (verbatim): "The generated QA JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://prb/schema` -- `name="prb_schema"`, `title="Problem Statement (PRB) JSON Schema"`
  description (verbatim): "The generated PRB JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://gol/schema` -- `name="gol_schema"`, `title="Goal (GOL) JSON Schema"`
  description (verbatim): "The generated GOL JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://rsk/schema` -- `name="rsk_schema"`, `title="Risk (RSK) JSON Schema"`
  description (verbatim): "The generated RSK JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://dec/schema` -- `name="dec_schema"`, `title="Decision (DEC) JSON Schema"`
  description (verbatim): "The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://sop/schema` -- `name="sop_schema"`, `title="Standard Operating Procedure (SOP) JSON Schema"`
  description (verbatim): "The generated SOP JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://feat/schema` -- `name="feat_schema"`, `title="Feature (FEAT) JSON Schema"`
  description (verbatim): "The generated FEAT JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://vcr/schema` -- `name="vcr_schema"`, `title="Verification Case Record (VCR) JSON Schema"`
  description (verbatim): "The generated VCR JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."
- `specmgr://sysrs/schema` -- `name="sysrs_schema"`, `title="System Requirements Specification (SYSRS) JSON Schema"`
  description (verbatim): "The generated SYSRS JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document."

### The 24 whole-body create/update prompt name/title/description triples

- `create_req(topic)` -- `title="Create a requirement"`
  description (verbatim): "Guides the LLM through checking for an existing similar requirement, gathering the required information, and driving create_req/validate to author a new REQ document."
- `update_req(id,instructions)` -- `title="Update a requirement"`
  description (verbatim): "Guides the LLM through revising an existing requirement by id: reading current state, applying the requested change with the right tool, and validating."
- `create_uc(topic)` -- `title="Create a use case"`
  description (verbatim): "Guides the LLM through checking for an existing similar use case, gathering the required information, and driving create_uc/validate to author a new UC document."
- `update_uc(id,instructions)` -- `title="Update a use case"`
  description (verbatim): "Guides the LLM through revising an existing use case by id: reading current state, applying the requested change with the right tool, and validating."
- `create_task(topic)` -- `title="Create a task list"`
  description (verbatim): "Guides the LLM through checking for an existing similar task list, gathering the required information, and driving create_tsk/validate to author a new TSK document."
- `update_task(id,instructions)` -- `title="Update a task list"`
  description (verbatim): "Guides the LLM through revising an existing task list by id: reading current state, applying the requested change with the right tool, and validating."
- `create_qa(topic)` -- `title="Create a QA document"`
  description (verbatim): "Guides the LLM through checking for an existing similar QA document, gathering answers to ISO/IEC 25010:2023 characteristic-relevant questions, and driving create_qa/validate to author a new QA document."
- `update_qa(id,instructions)` -- `title="Update a QA document"`
  description (verbatim): "Guides the LLM through revising an existing QA document by id: reading current state, applying the requested change with the right tool, and validating."
- `create_prb(topic,qa_id)` -- `title="Create a problem statement"`
  description (verbatim): "Guides the LLM through checking for an existing similar problem statement, optionally carrying over already-answered 5W2H questions from a linked QA document (qa_id), interviewing the user for whichever 5W2H current-state questions remain, synthesizing the Summary and Gap, composing the mandatory Problem Statement lead sentence, and driving create_prb/validate to author a new PRB document."
- `update_prb(id,instructions)` -- `title="Update a problem statement"`
  description (verbatim): "Guides the LLM through revising an existing problem statement by id: reading current state (recovering an old-shape document missing the mandatory lead sentence via a raw re-read if needed), showing which of the 7 5W2H questions are answered, eliciting revisions, re-synthesizing Summary/Gap, applying the change with the right tool, and validating."
- `create_gol(topic)` -- `title="Create a goal"`
  description (verbatim): "Guides the LLM through checking for an existing similar goal, gathering the required information, and driving create_gol/validate to author a new GOL document."
- `update_gol(id)` -- `title="Update a goal"`
  description (verbatim): "Guides the LLM through revising an existing goal by id: reading current state, showing which sections are present vs. empty, eliciting revisions, applying the change with the right tool, and validating."
- `create_risk(topic)` -- `title="Create a risk"`
  description (verbatim): "Guides the LLM through checking for an existing similar risk, gathering the required information, and driving create_rsk/validate to author a new RSK document."
- `update_risk(id,instructions)` -- `title="Update a risk"`
  description (verbatim): "Guides the LLM through revising an existing risk by id: reading current state, applying the requested change with the right tool, and validating."
- `create_dec(topic)` -- `title="Create a decision"`
  description (verbatim): "Guides the LLM through checking for an existing similar decision, gathering the required information, and driving create_dec/validate to author a new DEC document."
- `update_dec(id,instructions)` -- `title="Update a decision"`
  description (verbatim): "Guides the LLM through revising an existing decision by id: reading current state, applying the requested change with the right tool, and validating."
- `create_sop(topic)` -- `title="Create a standard operating procedure"`
  description (verbatim): "Guides the LLM through checking for an existing similar SOP, gathering the required information, and driving create_sop/validate to author a new SOP document."
- `update_sop(id,instructions)` -- `title="Update a standard operating procedure"`
  description (verbatim): "Guides the LLM through revising an existing standard operating procedure by id: reading current state, applying the requested change with the right tool, and validating."
- `create_feat(topic)` -- `title="Create a feature"`
  description (verbatim): "Guides the LLM through checking for an existing similar feature, gathering the required information, and driving create_feat/validate to author a new FEAT document."
- `update_feat(id,instructions)` -- `title="Update a feature"`
  description (verbatim): "Guides the LLM through revising an existing feature by id: reading current state, applying the requested change with the right tool, and validating."
- `create_vcr(topic)` -- `title="Create a verification case record"`
  description (verbatim): "Guides the LLM through checking for an existing similar verification case record, gathering the required information, and driving create_vcr/validate to author a new VCR document."
- `update_vcr(id,instructions)` -- `title="Update a verification case record"`
  description (verbatim): "Guides the LLM through revising an existing verification case record by id: reading current state, applying the requested change with the right tool, and validating."
- `create_sysrs(topic)` -- `title="Create a system requirements specification"`
  description (verbatim): "Guides the LLM through checking for an existing similar system requirements specification, gathering the required information, and driving create_sysrs/validate to author a new SYSRS document."
- `update_sysrs(id,instructions)` -- `title="Update a system requirements specification"`
  description (verbatim): "Guides the LLM through revising an existing system requirements specification by id: reading current state, applying the requested change with the right tool, and validating."

### The 8 tool descriptions named by the audit

- `create_tsk` (verbatim description):
  "Create a new task list: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the task list base directory. Returns the newly created document's frontmatter only (no body); use the corresponding `get_tsk` tool to fetch the full document afterward."
- `create_prb` (verbatim description):
  "Create a new Problem Statement: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the problem statement base directory. Returns the newly created document's frontmatter only (no body); use the corresponding `get_prb` tool to fetch the full document afterward."
- `get_tsk` (verbatim description):
  "Read, parse, and return a full task list document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. With raw=True, optional read-style `offset`/`limit` window the raw read: `offset` (1-based, default 1) is the first body line to return, `limit` (line count, default through end of body) how many; out-of-range values clamp (`offset > N` returns the empty string), and coordinates with raw=False raise ValueError. A document that exists but fails to parse returns a `ParseFailureResult` (`error`/`path`/`id`) instead of raising; its `error` text carries the same parse defect as the domain's own `list` tool's failed-row `error` for the same file (identical field path and cause, though the trailing pydantic documentation line may differ by read order/cache state; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c, Option B, 2026-09-26 -- the str-faithful reconstruction is tracked as a follow-up issue). An invalid id (path-injection attempt or wrong format) is also a ValueError, raised before any file access."
- `get_prb` (verbatim description):
  "Read, parse, and return a full problem statement document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. With raw=True, optional read-style `offset`/`limit` window the raw read: `offset` (1-based, default 1) is the first body line to return, `limit` (line count, default through end of body) how many; out-of-range values clamp (`offset > N` returns the empty string), and coordinates with raw=False raise ValueError. A document that exists but fails to parse returns a `ParseFailureResult` (`error`/`path`/`id`) instead of raising; its `error` text carries the same parse defect as the domain's own `list` tool's failed-row `error` for the same file (identical field path and cause, though the trailing pydantic documentation line may differ by read order/cache state; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c, Option B, 2026-09-26 -- the str-faithful reconstruction is tracked as a follow-up issue). An invalid id (path-injection attempt or wrong format) is also a ValueError, raised before any file access."
- `list_tsk` (verbatim description):
  "Ids, titles, statuses, and refs of task lists in the configured task list base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_tsk tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored."
- `list_prb` (verbatim description):
  "Ids, titles, statuses, and refs of problem statements in the configured problem statement base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_prb tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored."
- `update` (verbatim description):
  "Whole-body or line-range replace of an existing document's content across the whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs), preserving its id/type/status/created/version; only `updated` changes. With no `offset`/`limit`, `content` is the full replacement body (body markdown only, no frontmatter block). With `offset`, `content` replaces the body line(s) starting at 1-based line `offset` of the current on-disk body: `limit` is the number of lines to replace (`offset`..`offset+limit-1`; `limit` omitted = through the last body line, `limit=0` = pure insert), and `offset=N+1` (one past the last body line) appends after it; the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool. An invalid `id` (path-injection attempt or wrong format for `type`) is a `ValueError` raised before any file access. Returns the updated frontmatter only (no body); use the corresponding `get_<d>` tool to fetch the full document afterward."
- `validate` (verbatim description):
  "Disk-free, id-free dry run validating document content across the whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs; `adr` is not supported -- use `validate_adr` instead). `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). Never raises for a content-validation failure: always returns `{valid: bool, errors: list[{message: str}]}` -- `errors` is empty when `valid` is `True`, and each `message` is truncated to at most `_MAX_VALIDATE_ERROR_CHARS` (300) characters (plus an `"... (truncated)"` suffix when truncation occurred) rather than returned verbatim without limit. A `full`/content-shape mismatch, or an unsupported `type`, is a caller-usage error and still raises `ValueError` before any validation runs. This is the sole validate entry point for these domains -- the former per-domain `validate_<d>` tools are removed; `validate_adr` remains a separate, unchanged, id-based tool."

One published-vs-audit diff, recorded per the audit's instruction not to rewrite its worktree citations: the published `create_qa` and `update_gol` descriptions deviate slightly from the audit's summarized "uniform two-sentence pattern" for the other 20 prompts (create_qa names the ISO/IEC 25010:2023 questions; update_gol adds "showing which sections are present vs. empty"); the four tsk/prb prompt strings and the templated resource description the audit quoted verbatim match the published surface exactly. None of the 8 tool descriptions above mentions the schema/template/example resources, confirming the audit's gap 13 on the live surface.

## Success verification

After all runs, each run dir's documents were read back from disk
(content checks above) and every run dir was listed through the
PUBLISHED server itself (`mcp_probe.py call_tool list_<d> {}`): all 8
formal run dirs each hold exactly one document and report `total: 1, error_count: 0` with the real title (no `<failed to parse>` rows) --
i.e. every success verdict is backed by a parse through the same server
surface the agents used. (The prb-create-prompt attempt-1 + retry pair
share that one dir per the retry protocol; the committed `final-docs/`
tree has exactly 8 subdirectories, one per run dir. The published-
surface probe record is committed as `mcp-surface-probe.txt`; the
per-run `list_<d>` outputs were not preserved; not part of a run.)

## Repo-pollution check

All runs executed in bare dirs under `/tmp/opencode/feat128/`; the
specmgr server resolves base dirs CWD-relative and no `SPECMGR_*_DIR`
env var was set, so nothing wrote outside the run dirs. Final `git status --porcelain` in the worktree shows only the intended Phase 100
files (the three findings docs, `evidence/`, and the README progress
update) -- recorded in `../README.md` Progress and verified at phase end.
