# Root-Cause Analysis: Why Agents Skip the Schema (feat-128, Task 100.100 / REQ-001, ACC-001)

Issue #128 question 1: *why* do agents take several round-trips to create
or update specmgr artifacts without querying the domain JSON schema
(`specmgr://<domain>/schema`) first? This analysis answers it from 8
controlled agent runs (methodology and raw evidence in
`round-trip-baseline.md` and `evidence/`), structured against the feature
README's Design Notes hypotheses (a)-(d), plus the concrete instruction
gaps the runs expose.

## Methodology in one paragraph

Fresh, non-interactive `opencode run` sessions (opencode v1.18.34, model
pinned `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`) in bare temp
directories (no AGENTS.md, no repo skills, no git) with only the
published specmgr MCP server (0.34.0 via `uvx`) available. Two domains
(tsk simple, prb complex) x two operations (create, update) x two
conditions (the domain's create/update prompt pre-invoked by the harness
versus not). Update runs were seeded with a parseable document whose id
the agent was never told -- discovery is part of the measured round trip.
Every instruction string, event stream, seed, and verdict is captured in
`evidence/manifest.md`.

## Headline observation

**2 of 8 runs fetched the schema; all 6 without the prompt fetched it
zero times.** The schema fetch occurred exactly when the prompt's
instruction was in the agent's context **and** the operation was a
create (2/2 prompt-create runs fetched it; 0/4 noprompt runs and 0/2
prompt-update runs did). Meanwhile the agents' actual authoring
reference in the noprompt runs was the `get_<d>_template` /
`get_<d>_example` **tools** (fetched in all 4 create runs, 0 update
runs) -- the template/example content, not the schema, is what the
agents reach for when they reach for anything.

## Hypothesis (a): the schema's actionable content lives only in prose; template/example carry more actionable guidance

**Partially confirmed.**

- Confirmed behavior: every create run (all 4) fetched the template and
  (in 3 of 4) the example before drafting; the schema was fetched by
  none of the noprompt runs. The agents treated template/example as the
  primary authoring reference.
- Confirmed insufficiency: the template/example resources do **not**
  carry all the closed-form rules. The prb template and example each
  show one *filled-in* lead sentence ("The current process is causing
  delays, for users because of missing automation." / "The migration
  tool's lack of a rollback step is causing widgets to become
  half-migrated, for the on-call platform engineer because ...") but
  neither shows the bracketed frame
  `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- that frame exists only in the schema's
  prose descriptions (never fetched) and in the `create_prb` prompt body
  (step 9; never invoked in the noprompt condition). Consequence,
  observed: `prb-create-noprompt`'s first `create_prb` attempt failed
  opaquely (`Error executing tool create_prb`); the agent then called
  `validate` to find the issue, and the frame message below is verbatim
  that subsequent `validate` call's output (truncated at feat-110's
  300-char cap) -- "problem_statement must match the template '\[Current
  state\] is causing ...', got 'Onboarding a new build server currently
  takes...'" -- two extra calls over the minimum path (the failed first
  `create_prb` and the `validate` that revealed the frame) before the
  successful retry. The prb prompt run composed the correct lead
  sentence on the first try (the schema fetch + prompt step 9 both
  carry the frame).
- So (a) is right that template/example are more *actionable* in
  practice (agents use them) but wrong to imply they are a sufficient
  substitute: the guidance is **split across three artifacts**
  (template/example for shape, schema prose for closed-form rules,
  prompt for the process), and a flow that sees only one of them
  (noprompt tool-direct: template/example only) can fail the rules it
  never saw. The tsk analogue is milder: the tsk template's leading
  comment "Number the tasks so that they are easier to track" steered
  `tsk-create-noprompt` to write `- [ ] Task 1: Provision the machine`
  instead of the exact task strings requested -- template content
  actively shaped authoring, including a deviation from the task text.

## Hypothesis (b): the prompt already contains a dedicated schema step, so the gap is discoverability / perceived cost / compliance, not a missing instruction

**Confirmed -- with a create/update split in compliance.**

- Prompt-create runs: 2/2 complied (fetched `specmgr://tsk/schema`
  (tsk-create-prompt, call 6 of 9) and `specmgr://prb/schema`
  (prb-create-prompt, call 5 of 9), in both cases *after*
  `list_mcp_resources` discovery and the template read, matching the
  prompts' own step 3 (tsk) / step 10 (prb) ordering).
- Prompt-update runs: **0/2 complied** -- neither tsk-update-prompt nor
  prb-update-prompt fetched the schema despite the prompts' explicit
  "Check the schema" step 4 (tsk) / step 9 (prb). Both update changes
  were single-line/local, and both agents read the current body
  (`get_<d>(raw=True)`) before editing -- for a local splice the
  already-in-context document body subsumes what "confirm field names
  and constraints" promises, so the agents rationally dropped the step.
  The prompt's schema step is **context-insensitive**: it prescribes the
  same fetch for a one-line change as for a whole-document rewrite.
- The prompt runs also show the *compliance cost*: both prompt-create
  runs needed `list_mcp_resources` (resource discovery) +
  `read_mcp_resource` per resource = 2 hops per fetch, versus 1 hop for
  the equivalent `get_<d>_template`/`get_<d>_example` tools the noprompt
  runs used directly. Perceived cost on this host is therefore both the
  12-53 KB payload **and** an extra discovery round-trip, against prose
  that (hypothesis (a)) mostly restates the prompt's own structure recap.

## Hypothesis (c): no `create_<d>`/`update` tool description mentions the schema, so tool-direct flows get zero pointers

**Confirmed, and it is the primary cause in the noprompt condition.**

- The noprompt runs' tool sequences contain zero resource-layer calls
  (0 `list_mcp_resources`, 0 `read_mcp_resource` across all 4) -- the
  schema was not merely *not fetched*, it was *not known to exist as a
  fetchable thing*. The agents' world was the 94-tool `tools/list`;
  inside it, the only authoring-guidance affordances are the
  `get_<d>_template`/`get_<d>_example` tools (which is exactly what they
  used).
- Verbatim capture (published 0.34.0 surface): `create_tsk`,
  `create_prb`, `get_tsk`, `get_prb`, `list_tsk`, `list_prb`, `update`,
  `validate` descriptions contain no mention of `specmgr://<d>/schema`,
  `/template`, or `/example` (full strings in `schema-audit.md`,
  "Tool descriptions"). The create tools' only cross-reference is "use
  the corresponding `get_<d>` tool to fetch the full document
  afterward" -- a read pointer, not an authoring pointer.
- The always-in-context metadata (tool descriptions) and the
  pull-based guidance (prompts) are disjoint: whichever surface the
  agent uses, the other is invisible. In the noprompt condition the
  schema's discoverability is structurally zero.

## Hypothesis (d): the schema describes parsed-JSON shape, not markdown; the prompt conflation and pull-based delivery make the schema's value ambiguous

**Confirmed (pull-based delivery); partially confirmed (impedance).**

- Pull-based: the probe run (`evidence/run-promptprobe.json`) shows a
  fresh opencode session **cannot invoke MCP prompts at all** (agent
  reply: `NO_PROMPT_TOOL`, zero tool calls) -- prompts are not in the
  tool surface, and in this host they are not otherwise reachable. So
  in any tool-direct flow the prompts' schema instructions are
  architecturally invisible, exactly as (d) states; the harness had to
  fetch the prompt text out-of-band for the `-prompt` condition.
- Impedance: the one prompt-create run whose final text discusses the
  schema says "The schema matches the structure of the prompt (required
  leading sentence template, `## Current State` with a mandatory
  `### Summary` and 7 optional 5W2H headings, `## Gap`/`## Impact`/
  `## Future State`)" (prb-create-prompt) -- the agent used the schema
  to *verify the prompt's markdown claims against the JSON property
  tree*, not to learn markdown it did not already have. The schema's
  markdown-relevant payload is its `description` prose; its structure is
  the parsed document (frontmatter/body/properties like
  `problem_statement`, `current_state`). For an authoring task the
  actionable half (prose) and the machine-checkable half (constraints:
  zero `enum`, two timestamp `pattern`s, `properties: {}` leaves -- see
  `schema-audit.md`) are decoupled, which is why the update agents
  found nothing to gain and the create agents used it only as a
  cross-check.

## Synthesis: why the agent skips the schema

Ranked by the evidence:

1. **Discoverability (primary, noprompt condition).** The schema is a
   resource, not a tool; nothing in the agent's always-in-context
   surface (94 tool descriptions) names it; the prompts that do name it
   are pull-based and, on this host, not even invocable as tools. An
   agent that never invokes the prompt cannot know the schema exists
   (0/4 noprompt runs made any resource-layer call).
2. **Perceived cost vs. marginal value (primary, prompt-update
   condition).** A fetch costs 2 round-trips (discovery + read) and
   12-53 KB of mostly-parser-internals prose on this host; for a local
   update the document body is already in context and subsumes the
   "confirm field names" value. The agents' skip is a rational value
   judgment, not ignorance -- they *could* have fetched it (the prompt
   told them to) and chose not to.
3. **Compliance tracks value, not instruction presence.** The same
   "Check the schema" wording is obeyed 2/2 when the operation is a
   create (where it cross-checks the draft) and obeyed 0/2 on updates.
   Instructions alone do not produce the fetch.
4. **Impedance mismatch limits the value even when fetched.** The schema
   is the parsed-JSON shape with zero closed-vocabulary constraints
   (no `enum`, `properties: {}` leaves); its only authoring-grade
   content is description prose that duplicates the prompt/template.
   The one rule that actually mattered (prb lead-sentence frame) rides
   in that prose and in the validate error message -- the noprompt agent
   learned it from the *error*, after failing.

**Concrete instruction gaps (ACC-001 citations)**

1. `create_tsk`/`create_prb` (and all `create_<d>`, the generic
   `update`, `validate`) tool descriptions -- the only always-in-context
   metadata -- are silent about the schema/template/example resources
   (verbatim strings in `schema-audit.md`); the resource's own
   title/description is provenance-oriented and only ever seen if the
   agent discovers the resource layer at all.
2. The `update_task`/`update_prb` prompts' "Check the schema" step
   (step 4 / step 9) is unconditional and context-insensitive --
   prescribed identically for a one-line splice (observed skipped 2/2)
   and a whole-body rewrite; it promises "confirm field names and
   constraints" while the schema carries no constraints to confirm
   (zero `enum`).
3. The prb lead-sentence fixed template (and every closed-form rule:
   TSK checkbox, RSK TARA/5x5, VCR DTAIS/AC-NNN, status sets -- full
   list in `schema-audit.md`) is absent from both the
   template/example resources (filled-in instances only) and the schema
   machine-readable layer (prose only) -- a noprompt create agent can
   only learn it from a failed `create_prb`/`validate` error, which is
   exactly what `prb-create-noprompt` did (+2 round-trips).
4. On the opencode host, MCP prompts are not invocable tools (probe:
   `NO_PROMPT_TOOL`) and resources cost a discovery hop
   (`list_mcp_resources` before `read_mcp_resource`): the two
   guidance-bearing surfaces are each one extra round-trip away from
   the tool surface the agent actually works in.

## What this means for question 3 (input to Phase 110)

The fetch can be increased (fix discoverability: tool-description
pointers, usage-oriented resource metadata, 1-hop schema access) or the
*need* for the fetch can be reduced (fold the closed-form rules into
the markdown-level artifacts agents already fetch -- template/example --
and/or into the validate error channel they already trust, demoting the
schema to constraint discovery). The baseline numbers for either
direction are in `round-trip-baseline.md` ("What Phase 110 may use").
