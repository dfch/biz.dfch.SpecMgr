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
`question` denied) on model `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`. The implementing agent's own
`task` tool is denied by its config, so each trial ran as a headless `opencode run` session whose primary
agent invoked the `task` tool exactly once with `subagent_type="explore"` and the template above verbatim,
and then relayed the subagent's final answer unchanged. From each trial's raw JSON event stream, the
relayed `prompt` argument was verified byte-identical to this template (trailing newline aside) and the
recorded response is the subagent's own `task_result`, cross-checked against the relay's final text. No
instruction file, docstring, or error message was modified before or during the trials.

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
