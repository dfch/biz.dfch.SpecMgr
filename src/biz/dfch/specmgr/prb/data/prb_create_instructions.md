You are drafting a new Problem Statement (PRB) document about: $topic

Linked QA document id (optional): $qa_id

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
    literal `TODO: answer pending` placeholder QA uses for a question
    nobody has answered yet), treat that sub-question as *not*
    pre-filled -- do not carry over a non-answer.
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
