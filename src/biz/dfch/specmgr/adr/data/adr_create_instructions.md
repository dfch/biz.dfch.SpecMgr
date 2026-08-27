You are drafting a new Architecture Decision Record (ADR) about: $topic

Follow this MADR 4.0.0-based structure and tool sequence exactly. Do not
write raw markdown yourself -- every change to the document goes through
the specmgr MCP tools listed below.

## 0. Check for an existing ADR on this topic first
Call the `list_adr` tool before creating anything. If an
ADR with a similar title or topic already exists, tell the user about it
and ask whether they want to revise that one (via the `update_adr`
prompt) instead of creating a duplicate. Only proceed to step 1 if this is
genuinely a new decision.

## 1. Structure recap
- `# {title}` -- H1, mandatory.
- `## Context and Problem Statement` -- mandatory.
- `## Decision Drivers` -- optional.
- `## Considered Options` -- mandatory, a freeform bullet list of option
  names (kept independent of the `Option` sub-sections in step 3 -- no
  consistency check is enforced between them, but keep them aligned in
  practice).
- `## Decision Outcome` -- mandatory: the chosen option and why.
- `### Consequences` -- optional, under Decision Outcome.
- `### Confirmation` -- optional, under Decision Outcome.
- `## Pros and Cons of the Options` -- derived automatically from whatever
  `Option` sub-sections exist; never write it directly.
- `## More Information` -- optional, always last.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the context/problem
statement, decision drivers (if any), the list of considered options, the
chosen outcome and its rationale, and optionally decision-makers/
consulted/informed.

## 3. Tool call sequence
1. Call `create_adr(frontmatter, body)` first:
   - `frontmatter.status` = `"draft"` or `"proposed"` (never invent an
     `id` -- it is always server-assigned).
   - `body.title`, `body.context_and_problem_statement`,
     `body.considered_options`, `body.decision_outcome` are mandatory and
     must be non-blank; `body.decision_drivers`/`consequences`/
     `confirmation`/`more_information` are optional.
   - Leave `body.options` empty at this point.
2. For each considered option worth writing up in detail, call
   `option_create(id, partial_title, value)` once per option -- write
   `value` as a short intro paragraph followed by
   `- Good, because ...` / `- Bad, because ...` / `- Neutral, because ...`
   bullets. Option numbering is assigned automatically, is never reused,
   and is never renumbered.
3. If the decision is being finalized now rather than left as a draft,
   call `set_status(id, type="adr", status="accepted")` (or
   `status="rejected"`, or `status="proposed"`, as appropriate) -- the
   generic status-change tool, always called with `type="adr"` for an
   ADR.
4. Always finish by calling `validate_adr(id)` to self-correct before
   reporting success back to the user.

## 4. Later revisions
Any later change to this ADR should go through the `update_adr` prompt
(or directly through `update_section`/`update_frontmatter`/`option_*`),
not by re-running this prompt.

Decision-makers: $decision_makers
Consulted: $consulted
Informed: $informed
