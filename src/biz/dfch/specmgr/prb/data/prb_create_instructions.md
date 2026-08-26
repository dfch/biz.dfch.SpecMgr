You are drafting a new Problem Statement (PRB) document about: $topic

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

No `## Root Cause` section exists in this schema, and none should be
added: a problem statement stays free of assumed causes by design --
root-cause analysis is a separate, later activity.

## 2. Build a todo list, then gather the 7 answers one at a time

Build a todo list with one entry per: `Summary`, each of the 7 5W2H
questions, `Gap`, `Impact`, and `Future State`. Then use the `question`
tool to elicit each of the 7 5W2H answers in turn (What/Why/Where/
Who/When/How/How Often), explicitly telling the user they may skip any
question they cannot or do not want to answer yet -- a freshly created
problem statement may have zero questions answered.

## 3. Synthesize the Summary

Once you have gathered whichever answers the user chose to give, draft a
`Summary` paragraph synthesizing them into a coherent, factual
description of the current state. If zero questions were answered,
write a short placeholder `Summary` instead (it is mandatory and must
always carry some text).

## 4. Draft and confirm the Gap

Draft a candidate `Gap` statement from the collected current-state
answers, following an expected-vs-actual/measurable-difference formula
(e.g. "X happens in N% of cases; the expected behavior is Y"). Show this
draft to the user and use the `question` tool to confirm or refine it
before finalizing -- do not finalize `Gap` without this confirmation
step.

## 5. Optionally ask for Impact

Use the `question` tool to ask whether the user wants to record an
`Impact` (the business/cost/safety consequence of the gap). Skip this
section entirely if they decline.

## 6. Ask for Future State

Use the `question` tool to ask for the desired/target condition once the
problem is resolved. `Future State` is mandatory.

## 7. Optionally ask for References/More Information

Use the `question` tool to ask whether the user wants to add
`References` (cross-references to other artifacts/tickets) or
`More Information`. Skip either section entirely if they decline.

## 8. Use the template/example/schema as references

Fetch `specmgr://prb/template` or `specmgr://prb/example` as a starting
point/style reference, then check `specmgr://prb/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 9. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the answers gathered in steps 2-7.
2. Call `create_prb(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_prb(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_prb` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 10. Later revisions

Any later change to this problem statement should go through the
`update_prb` prompt (or directly through `update_prb`/`set_status_prb`),
not by re-running this prompt.
