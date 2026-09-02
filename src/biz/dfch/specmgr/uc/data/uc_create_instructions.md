You are drafting a new Use Case (UC) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_uc` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_uc` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing use case first
Call the `list_uc` tool before creating anything. If a use case with a
similar title or topic already exists, tell the user about it and ask
whether they want to revise that one (via the `update_uc` prompt)
instead of creating a duplicate. Only proceed to step 1 if this is
genuinely a new use case.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {title}` -- H1, mandatory, the use case name.
- `## Characteristic Information` -- mandatory container for the
  sub-sections below.
  - `### Goal in Context` -- mandatory prose: what the primary actor
    wants to achieve, in the context of the surrounding business
    process.
  - `### Scope` -- mandatory prose: the system/process being designed
    (the black box under design).
  - `### Level` -- mandatory prose: the use case's altitude in
    Cockburn's goal hierarchy (e.g. Summary, User Goal, Subfunction).
  - `### Preconditions` -- mandatory bullet list, at least one item.
  - `### Success End Condition` -- mandatory bullet list, at least one
    item.
  - `### Failed End Condition` -- optional bullet list.
  - `### Primary Actor` -- mandatory prose naming the actor who
    initiates the use case.
  - `### Secondary Actors` -- optional bullet list.
  - `### Trigger` -- mandatory prose: the event that starts the use
    case.
  - `### Frequency` -- optional prose.
  - `### Priority` -- optional prose.
  - `### Performance Target` -- optional prose.
  - `### Channels to Primary Actor` -- optional bullet list.
  - `### Channels to Secondary Actors` -- optional bullet list.
  - `### Related Use Cases` -- optional bullet list of cross-references.
- `## Main Success Scenario` -- mandatory numbered list of steps, the
  "everything goes right" path.
- `## Extensions` -- optional. An optional introductory paragraph
  followed by zero or more `### Extension {step}{letter}. {condition}`
  sub-sections (e.g. `### Extension 3a. Company is out of stock`), each
  headed by which main-scenario step it branches from and holding its
  own numbered list of actions. The `{step}` digits must resolve to a
  real `Main Success Scenario` step number, and no two Extensions may
  share the same `{step}{letter}` reference.
- `## Sub-Variations` -- optional. Zero or more `### Step {N}:
  {description}` sub-sections (e.g. `### Step 1: Buyer may use`), each
  holding a bullet list of variant ways to carry out that one step.
  `{N}` must resolve to a real `Main Success Scenario` step number, and
  no two Sub-Variations may reference the same step.
- `## Open Issues` -- optional bullet list of unresolved questions.
- `## Related Information` -- optional container.
  - `### Notes` -- optional bullet list.
  - `### Assumptions` -- optional bullet list.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the use case title, its
goal in context, scope, level, at least one precondition, at least one
success end condition, the primary actor, and the trigger. Optionally
gather the failed end condition, secondary actors, frequency, priority,
performance target, channels, related use cases, the main success
scenario steps, extensions, sub-variations, open issues, notes, and
assumptions.

## 3. Use the template/example/schema as references
Fetch `specmgr://uc/template` or `specmgr://uc/example` as a starting
point/style reference, then check `specmgr://uc/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not
present there.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_uc(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_uc(content, full=False)` first if you want
   to dry-run the body without writing anything -- `create_uc` already
   performs the same validation internally, so this step is never
   required, only a convenience.

## 5. Later revisions
Any later change to this use case should go through the `update_uc` prompt
(or directly through the generic `update(id, type="uc", content)`,
`set_status(id, type="uc", status)`, and
`set_classification(id, type="uc", classification)` tools), not by
re-running this prompt.
