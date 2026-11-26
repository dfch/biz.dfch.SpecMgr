# Session Prompt Template and Measurement Protocol (Task 100.100 / REQ-001)

The shared neutral prompt for the Phase 100 baseline sessions, the fixed task it poses, and the scoring
protocol. The neutral prompt is everything the sessions received; the scoring protocol is for the
investigator only and was never part of it.

## Neutral prompt (sent verbatim to every session)

````text
You are drafting a new entry for the `## Recent Updates` section of a Task List (TSK) document managed by the specmgr artifact manager. Each entry in that section is introduced by an H3 heading that carries a timestamp.

The project documentation describes the entry heading format (quoted verbatim from `src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md`, lines 27-29, with the lines' leading indentation removed):

```text
`### {timestamp} ( - | : ) {title}` entry, newest-first, where
`{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.fff` +
`Z` or `±HH:mm` (e.g. `### 2026-08-19 05:42:00.000+02:00 - Created`),
```

The docstring of the frontmatter `created`/`updated` fields describes the same shape (quoted verbatim from `src/biz/dfch/specmgr/models/md/frontmatter.py`, lines 96-99, with the lines' leading indentation removed):

```text
The required shape is ``yyyy-MM-dd`` + (``T`` or space) +
``HH:mm:ss.fff`` + ``Z``/``±HH:mm``; the machine-written canonical
form is the ``T``-separated one (the MCP is the only writer of
frontmatter). The generated JSON Schema carries a ``pattern`` key
```

If a timestamp does not match that shape, the validator raises this error at runtime (the exact message from the same file, lines 186-187, with the offending value shown as `<value>`):

```text
created/updated '<value>' must be the date+time variant 'yyyy-MM-dd' + 'T' or space + 'HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset
```

Now suppose it is Tuesday, 2026-10-06, and the current local time in the UTC+02:00 time zone is 07:52:14.

Following the timestamp format described above, write the full date+time timestamp you would use for this new entry, now.

Reply with:
1. the exact timestamp string you would use, on a single line;
2. one sentence explaining how you filled in each part of the string from the format descriptions above.

Answer directly from the format descriptions above; no file or codebase lookup is needed.
````

The three quoted snippets are today's unmodified wording as of HEAD 25c7f13be4571a5af635a69eb37dcd3bdfb30025,
reproduced byte-for-byte with only the lines' leading indentation removed:

- `src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md` lines 27-29 (entry-heading format, including
  the concrete `e.g.` line);
- `src/biz/dfch/specmgr/models/md/frontmatter.py` lines 96-99 (the `created`/`updated` docstring shape
  description);
- `src/biz/dfch/specmgr/models/md/frontmatter.py` lines 186-187 (the rendered runtime error message, with
  the offending value shown as `<value>`).

The prompt poses one fixed timestamp task: given today = Tuesday 2026-10-06 and the current local time =
07:52:14 in UTC+02:00, produce the full date+time timestamp for a new entry "now" following the quoted
format, as reply item 1 (the exact string) and item 2 (a one-sentence derivation).

## Scoring protocol (investigator only; the same protocol Task 110.100 applies to candidate notations)

- (a) Misread: the response carries the literal `fff` in the millisecond field (e.g. `...:14.fff+02:00`).
- (b) Correct substitution: a syntactically valid full date+time timestamp with exactly three millisecond
  digits in the placeholder field (\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}));
  the chosen digits, the `T`/space separator, and the `Z`/`±HH:mm` zone variant are all acceptable and not
  scored.
- (c) Other: no parseable full date+time timestamp, a missing/2/4/6-digit fractional field, a date-only
  value, or a malformed zone -- described in the session file.
- Baseline rate = (b) count / total trials, one fixed task per session.

## Mechanism and trial log

Each trial is one independent, fresh-context session of the built-in `explore` subagent (read-only;
`question` denied); the Phase 100 baseline trials ran on the
`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2` endpoint and the nine Phase 110 candidate trials
(recorded in the Phase 110 section below) on the `vllm-sys0-mtp-1/qwen3.8-27b-bf16-896k-mtp-1`
endpoint. The implementing agent's own
`task` tool is denied by its config, so each trial ran as a headless `opencode run` session whose primary
agent invoked the `task` tool exactly once with `subagent_type="explore"` and the template above verbatim,
and then relayed the subagent's final answer unchanged. From each trial's raw JSON event stream, the
relayed `prompt` argument was verified byte-identical to this template (trailing newline aside) and the
recorded response is the subagent's own `task_result`, cross-checked against the relay's final text. No
instruction file, docstring, or error message was modified before or during the trials. Consequence of
the endpoint difference: every trial (baseline and all candidates) scored identically -- 3/3 correct
substitutions, zero verbatim copies -- so the endpoint difference cannot have changed any pass/fail
outcome; identical underlying weights across the two endpoints are assumed from the endpoints' naming,
not verified.

| Trial | Subagent session | Date (UTC) | Score |
|---|---|---|---|
| `session-01.md` | `ses_ef01a9760ffe0QzpdFn4C8oW9g` | 2026-10-06T06:27:35Z | (b) correct substitution |
| `session-02.md` | `ses_ef01661beffeDG0RPF2LRKADFd` | 2026-10-06T06:32:11Z | (b) correct substitution |
| `session-03.md` | `ses_ef014e4bcffeUh7V0m5xCj7fAK` | 2026-10-06T06:33:48Z | (b) correct substitution |

**Baseline `fff` correct-substitution rate: 3/3 (100%)** -- zero verbatim placeholder copies across the
three trials. Phase 110's pass bar (Task 110.100) additionally requires a candidate to reach at least
this rate.

One early trial run was discarded: its relay passed a stale draft of the template (the docstring quote
cut at line 98). The trial was re-run with the final template, and only the re-run is logged above.

## Phase 110 candidate prompt variants (Task 110.110)

Each variant is the Phase 100 neutral template with one mechanical substitution: `fff` replaced by the
candidate token in exactly its three quoted-notation occurrences (the tsk instruction quote, the
docstring quote, the error-message quote); everything else is byte-identical to the Phase 100 template
above (round-trip proven: substituting the token back to `fff` reproduces the template), and the fixed
task (date 2026-10-06, time 07:52:14 UTC+02:00) is unchanged. Each variant was sent verbatim to three
independent, fresh-context `explore` sessions exactly as the Phase 100 template was. For these trials,
scoring protocol (a) above is read with `fff` replaced by the candidate token -- a verbatim copy of the
candidate's own placeholder is what counts as a misread.

### Candidate `SSS` -- sessions 04 through 06

Grounding: the pattern-letter convention of the notation itself (like `HH`/`mm`/`ss`/`yyyy`) -- `S` names the millisecond field (the established Java SimpleDateFormat / moment.js / Android pattern letter) and the triple letter marks the slot as exactly three digits.

````text
You are drafting a new entry for the `## Recent Updates` section of a Task List (TSK) document managed by the specmgr artifact manager. Each entry in that section is introduced by an H3 heading that carries a timestamp.

The project documentation describes the entry heading format (quoted verbatim from `src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md`, lines 27-29, with the lines' leading indentation removed):

```text
`### {timestamp} ( - | : ) {title}` entry, newest-first, where
`{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.SSS` +
`Z` or `±HH:mm` (e.g. `### 2026-08-19 05:42:00.000+02:00 - Created`),
```

The docstring of the frontmatter `created`/`updated` fields describes the same shape (quoted verbatim from `src/biz/dfch/specmgr/models/md/frontmatter.py`, lines 96-99, with the lines' leading indentation removed):

```text
The required shape is ``yyyy-MM-dd`` + (``T`` or space) +
``HH:mm:ss.SSS`` + ``Z``/``±HH:mm``; the machine-written canonical
form is the ``T``-separated one (the MCP is the only writer of
frontmatter). The generated JSON Schema carries a ``pattern`` key
```

If a timestamp does not match that shape, the validator raises this error at runtime (the exact message from the same file, lines 186-187, with the offending value shown as `<value>`):

```text
created/updated '<value>' must be the date+time variant 'yyyy-MM-dd' + 'T' or space + 'HH:mm:ss.SSS' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset
```

Now suppose it is Tuesday, 2026-10-06, and the current local time in the UTC+02:00 time zone is 07:52:14.

Following the timestamp format described above, write the full date+time timestamp you would use for this new entry, now.

Reply with:
1. the exact timestamp string you would use, on a single line;
2. one sentence explaining how you filled in each part of the string from the format descriptions above.

Answer directly from the format descriptions above; no file or codebase lookup is needed.
````

### Candidate `ms` -- sessions 07 through 09

Grounding: the ISO 31-2 unit symbol for milliseconds -- the slot is labelled by the unit its content carries, so the token reads as a field label for a number rather than value text to copy.

````text
You are drafting a new entry for the `## Recent Updates` section of a Task List (TSK) document managed by the specmgr artifact manager. Each entry in that section is introduced by an H3 heading that carries a timestamp.

The project documentation describes the entry heading format (quoted verbatim from `src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md`, lines 27-29, with the lines' leading indentation removed):

```text
`### {timestamp} ( - | : ) {title}` entry, newest-first, where
`{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.ms` +
`Z` or `±HH:mm` (e.g. `### 2026-08-19 05:42:00.000+02:00 - Created`),
```

The docstring of the frontmatter `created`/`updated` fields describes the same shape (quoted verbatim from `src/biz/dfch/specmgr/models/md/frontmatter.py`, lines 96-99, with the lines' leading indentation removed):

```text
The required shape is ``yyyy-MM-dd`` + (``T`` or space) +
``HH:mm:ss.ms`` + ``Z``/``±HH:mm``; the machine-written canonical
form is the ``T``-separated one (the MCP is the only writer of
frontmatter). The generated JSON Schema carries a ``pattern`` key
```

If a timestamp does not match that shape, the validator raises this error at runtime (the exact message from the same file, lines 186-187, with the offending value shown as `<value>`):

```text
created/updated '<value>' must be the date+time variant 'yyyy-MM-dd' + 'T' or space + 'HH:mm:ss.ms' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset
```

Now suppose it is Tuesday, 2026-10-06, and the current local time in the UTC+02:00 time zone is 07:52:14.

Following the timestamp format described above, write the full date+time timestamp you would use for this new entry, now.

Reply with:
1. the exact timestamp string you would use, on a single line;
2. one sentence explaining how you filled in each part of the string from the format descriptions above.

Answer directly from the format descriptions above; no file or codebase lookup is needed.
````

### Candidate `sss` -- sessions 10 through 12

Grounding: ISO 8601's own fractional-seconds placeholder notation (lowercase s-family, triple letter = three digits); noted drawback: it sits directly after the `ss` seconds field (`ss.sss`).

````text
You are drafting a new entry for the `## Recent Updates` section of a Task List (TSK) document managed by the specmgr artifact manager. Each entry in that section is introduced by an H3 heading that carries a timestamp.

The project documentation describes the entry heading format (quoted verbatim from `src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md`, lines 27-29, with the lines' leading indentation removed):

```text
`### {timestamp} ( - | : ) {title}` entry, newest-first, where
`{timestamp}` is the full date+time form `yyyy-MM-dd[T ]HH:mm:ss.sss` +
`Z` or `±HH:mm` (e.g. `### 2026-08-19 05:42:00.000+02:00 - Created`),
```

The docstring of the frontmatter `created`/`updated` fields describes the same shape (quoted verbatim from `src/biz/dfch/specmgr/models/md/frontmatter.py`, lines 96-99, with the lines' leading indentation removed):

```text
The required shape is ``yyyy-MM-dd`` + (``T`` or space) +
``HH:mm:ss.sss`` + ``Z``/``±HH:mm``; the machine-written canonical
form is the ``T``-separated one (the MCP is the only writer of
frontmatter). The generated JSON Schema carries a ``pattern`` key
```

If a timestamp does not match that shape, the validator raises this error at runtime (the exact message from the same file, lines 186-187, with the offending value shown as `<value>`):

```text
created/updated '<value>' must be the date+time variant 'yyyy-MM-dd' + 'T' or space + 'HH:mm:ss.sss' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset
```

Now suppose it is Tuesday, 2026-10-06, and the current local time in the UTC+02:00 time zone is 07:52:14.

Following the timestamp format described above, write the full date+time timestamp you would use for this new entry, now.

Reply with:
1. the exact timestamp string you would use, on a single line;
2. one sentence explaining how you filled in each part of the string from the format descriptions above.

Answer directly from the format descriptions above; no file or codebase lookup is needed.
````

## Phase 110 mechanism and trial log (Task 110.110)

Same mechanism as Phase 100 (above): the implementing agent's own `task` tool is denied by its config,
so each trial ran as a headless `opencode run` session whose primary agent invoked the `task` tool
exactly once with `subagent_type="explore"` and the candidate variant verbatim, then relayed the
subagent's final answer unchanged. The nine trials ran as three parallel batches of three, one batch
per candidate (independent fresh-context sessions). From each trial's raw JSON event stream, the
relayed `prompt` argument was verified byte-identical to the candidate variant (trailing newline aside --
the prompt's final newline sits directly before the END-PROMPT marker line, exactly as in Phase 100),
and the recorded response is the subagent's own `task_result`, cross-checked against the relay's final
text. No instruction file, docstring, or error message was modified before or during the trials.

| Trial | Subagent session | Date (UTC) | Score |
|---|---|---|---|
| `session-04.md` | `ses_eedbf147dffemL87Um64saQDOq` | 2026-10-06T17:26:46Z | (b) correct substitution |
| `session-05.md` | `ses_eedbe385affetHw2ySZUf7u2FX` | 2026-10-06T17:27:43Z | (b) correct substitution |
| `session-06.md` | `ses_eedbf4edaffe2N5GH9YxRndOZA` | 2026-10-06T17:26:31Z | (b) correct substitution |
| `session-07.md` | `ses_eedb70d98ffe90mGtL0K6fpseQ` | 2026-10-06T17:35:32Z | (b) correct substitution |
| `session-08.md` | `ses_eedb78f8cffe7T6xsnejUMnMLR` | 2026-10-06T17:34:59Z | (b) correct substitution |
| `session-09.md` | `ses_eedb67594ffeZMVLIfTIDarNGJ` | 2026-10-06T17:36:11Z | (b) correct substitution |
| `session-10.md` | `ses_eedae7f1effe58WE4PFVfsAaZD` | 2026-10-06T17:44:53Z | (b) correct substitution |
| `session-11.md` | `ses_eedae96b8ffexMOjTK1Xh37Wv4` | 2026-10-06T17:44:47Z | (b) correct substitution |
| `session-12.md` | `ses_eedaf1bc7ffeg7RH0kL12rYo4r` | 2026-10-06T17:44:13Z | (b) correct substitution |

**Pass bar (restated, defined up front per Task 110.100):** at least three independent fresh-context
sessions per candidate under the identical neutral prompt; a "correct substitution" is a syntactically
valid full date+time timestamp with exactly three millisecond digits in the placeholder field; pass =
zero verbatim copies of the candidate token AND a correct-substitution rate of at least two-thirds of
the trials AND at least as high as the `fff` baseline rate (3/3, measured with the same protocol in
Phase 100) -- i.e. here, 3/3 with zero verbatim copies.

**Per-candidate computation:**

- `SSS`: 3/3 (b) (sessions 04-06), zero verbatim `SSS` copies -> rate 3/3 >= 2/3 and >= baseline 3/3:
  **PASS**.
- `ms`: 3/3 (b) (sessions 07-09), zero verbatim `ms` copies -> rate 3/3 >= 2/3 and >= baseline 3/3:
  **PASS**.
- `sss`: 3/3 (b) (sessions 10-12), zero verbatim `sss` copies -> rate 3/3 >= 2/3 and >= baseline 3/3:
  **PASS**.

Selection among the three passing candidates per Task 110.115 is recorded in this README's
`##### Chosen Notation and Rationale (ACC-002)` subsection.

## G1 follow-up: example-free paired trial (round-2 review)

Phase 100/110's protocol was example-anchored: every prompt carried the concrete
`e.g. ### 2026-08-19 05:42:00.000+02:00` line, so the one exposure path the root cause
identifies as the actual misreading mechanism -- the notation *alone*, notably the
example-free runtime error message -- was never measured quantitatively (round-1 review
finding G1; recorded in this README's ACC-002 limitation sentence). This section defines
and logs the follow-up measurement: a paired BEFORE/AFTER comparison on the example-free
path. It is explicitly **outside the Phase 110 pass bar** -- no pass/fail gate; the
outcome is reported as an observed BEFORE->AFTER delta with a small-N interpretation.

### Shared variant template (both arms)

The runtime error message is the *only* format source in this variant -- no `e.g.` anchor
line, no instruction-file quote, no docstring quote: exactly the exposure an agent gets
when a timestamp it wrote is rejected at runtime. The fixed task and the reply format are
byte-identical to Phases 100/110.

````text
You are drafting a new entry for the `## Recent Updates` section of a Task List (TSK) document managed by the specmgr artifact manager. Each entry in that section is introduced by an H3 heading that carries a timestamp.

You previously wrote an entry whose timestamp was rejected by the validator, which raised this error (the exact message from `src/biz/dfch/specmgr/models/md/frontmatter.py`, lines 186-187, with the offending value shown as `<value>`):

```text
created/updated '<value>' must be the date+time variant 'yyyy-MM-dd' + 'T' or space + 'HH:mm:ss.{TOKEN}' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset
```

Now suppose it is Tuesday, 2026-10-06, and the current local time in the UTC+02:00 time zone is 07:52:14.

Following the timestamp format described by that error message, write the full date+time timestamp you would use for this new entry, now.

Reply with:
1. the exact timestamp string you would use, on a single line;
2. one sentence explaining how you filled in each part of the string from the format description above.

Answer directly from the error message above; no file or codebase lookup is needed.
````

### Arm derivation and quote sources

Each arm is the template with `{TOKEN}` filled by exactly one mechanical substitution;
round-trip proven: substituting one arm's token to the other's reproduces the other arm's
variant byte-for-byte.

- **BEFORE arm (`fff`), `{TOKEN}` = `fff`:** the error line quoted byte-for-byte from
  `src/biz/dfch/specmgr/models/md/frontmatter.py` lines 186-187 **as of base commit
  `25c7f13be4571a5af635a69eb37dcd3bdfb30025`** (the pre-rollout wording), with the
  offending value shown as `<value>` exactly as Phase 100's template rendered it.
- **AFTER arm (`SSS`), `{TOKEN}` = `SSS`:** the same lines **at HEAD** (the post-rollout
  wording); the two quotes differ in exactly the one token.

### Scoring

The existing (a)/(b)/(c) protocol from above, (a) read per arm -- a verbatim copy of the
arm's own placeholder (`fff` in the BEFORE arm, `SSS` in the AFTER arm) counts as a
misread; (b) a syntactically valid full date+time timestamp with exactly three
millisecond digits in the placeholder field (chosen digits, `T`/space separator, and
`Z`/`±HH:mm` zone variant all acceptable and not scored); (c) anything else. Per arm:
three independent, fresh-context `explore` sessions (the same neutral-agent discipline as
Phases 100/110), numbering continued: `session-13.md`-`session-15.md` = BEFORE `fff`,
`session-16.md`-`session-18.md` = AFTER `SSS`.

### Mechanism and trial log

Each trial ran as one independent, fresh-context `explore` subagent session via the
reviewing agent's own `task` tool with `subagent_type="explore"` and the arm's variant
verbatim (unlike the original implementing agent, whose config denied `task` and forced
the headless `opencode run` relay of Phases 100/110; no relay was needed this round). All
six trials ran on the single endpoint
`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`, so the Phase 110 two-endpoint caveat does
not apply. No instruction file, docstring, or error message was modified before or during
the trials. `Date (UTC)` is each trial's start time.

| Trial | Arm | Subagent session | Date (UTC) | Score |
|---|---|---|---|---|
| `session-13.md` | BEFORE `fff` | `ses_eeb046753ffe9P5NiEEc4b3R1b` | 2026-10-07T06:09:48Z | (b) correct substitution |
| `session-14.md` | BEFORE `fff` | `ses_eeb029161ffeSbTURZJo1zeF95` | 2026-10-07T06:11:49Z | (b) correct substitution |
| `session-15.md` | BEFORE `fff` | `ses_eeb017cf8ffe9T5FWzcqh8478e` | 2026-10-07T06:12:59Z | (b) correct substitution |
| `session-16.md` | AFTER `SSS` | `ses_eeb0021d6ffehZTbucGNf3PGTS` | 2026-10-07T06:14:15Z | (b) correct substitution |
| `session-17.md` | AFTER `SSS` | `ses_eeafe6ca9ffeacLANoI3OTZuQ0` | 2026-10-07T06:16:20Z | (b) correct substitution |
| `session-18.md` | AFTER `SSS` | `ses_eeafc8aacffeLQmAAk0dHtoySA` | 2026-10-07T06:18:23Z | (b) correct substitution |

**Per-arm computation:**

- BEFORE `fff`: 3/3 (b) (sessions 13-15), zero verbatim `fff` copies.
- AFTER `SSS`: 3/3 (b) (sessions 16-18), zero verbatim `SSS` copies.

**Observed BEFORE->AFTER delta: none.** Both arms scored identically (3/3 correct
substitutions, zero verbatim placeholder copies) on the example-free path at N=3 per arm; all six
sessions derived the three-digit millisecond field from the error message alone (the BEFORE arm's
derivation sentences read `.fff` as "the mandatory 3-digit" field, "zero millisecond fractional
part", and "a required 3-digit millisecond field"; the AFTER arm's as "the required 3-digit
millisecond field", ".000 appended because no millisecond value was specified", and "the format
mandates three sub-second digits"). Honest small-N interpretation: at 3 trials per arm, this
measurement surfaces an arm-wide verbatim-copy failure mode (the one issue #183 reports as
repeated) and would very likely have surfaced a per-trial misread rate of ~1/3 or higher (such a
rate has a ~70% chance of yielding at least one verbatim copy in 3 trials), but it cannot exclude
smaller per-trial rates, and the fresh-context `explore` population is a best-available proxy for
the unnamed, non-reproduced agent population behind the reported misreads. Consequence for the
record: `SSS`'s selection rationale for the example-free path stands on the token's
self-descriptiveness (it marks the digit slot by the notation's own convention -- the recorded
root-cause defect of `fff`) rather than on a measured delta; the path is now measured, and the
measurement's honest result is "no observable difference at this N on this population".
