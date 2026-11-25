---
name: c4-model-review
description: Use when the task is reviewing an existing C4 model built in Structurizr DSL for quality -- walking the model's elements, relationships, and views against a read-only C4 checklist and reporting the findings -- for example when asked to "review this C4 model", "check the model for problems", "audit the architecture model", "find quality issues in the model", or "is this model ready to publish". It reports the review findings only; it never edits the model or writes any files.
---

# C4 Model Review

You are reviewing an existing C4 architecture model — judging its elements,
relationships, and views against how C4 models are supposed to be built, and
reporting what you find. This skill is read-only: it reports findings and
never edits the model — no file is changed, created, deleted, or renamed, and
the review is delivered in your final message, not in a file. How to write or
fix DSL text is the `structurizr-dsl-authoring` skill's task, and the
parse/validate/inspect loop with finding triage is the
`structurizr-validate-loop` skill's task; here you only look, judge, and
report.

## The workflow

1. **Read the workspace DSL** with your host's file tool (the path the user
   named, e.g. `workspace.dsl`). Read it once, completely.
2. **Check the structure with the structurizr MCP** — `parse` (does the text
   parse at all), `validate` (does the workspace validate), and `inspect`
   (the Checkstyle-style findings: disconnected elements, elements not on any
   view, generated view keys, ...). If the workspace does not parse or
   validate, that is the first finding — report it with the tool's exact
   message and stop the checklist; do not fix it. Call each tool once; do not
   re-run a tool over text that has not changed. Your host prefixes the MCP
   tool names (for example `structurizr_parse`; the in-harness server name is
   `structurizr`), so call whichever prefixed variant your host exposes.
3. **Walk the checklists** over the DSL text: `references/element-checklist.
   md` (people, systems, containers, components, completeness — incl.
   disconnected elements), `references/relationship-checklist.md` (labels,
   technology, direction), and `references/view-checklist.md` (the views
   exist, are keyed, are sized for reading). Judge every element and
   relationship in the model, not just the ones the tools flag: the tools
   surface some problems (e.g. disconnected elements, generated view keys),
   but the modelling mistakes (a library modeled as a container, a
   third-party element without the `External` tag, a vague relationship
   label, an over-crowded view) are only visible to the checklist.
4. **Report the findings** in your final message, in the format below.

## The report format

Report the review as:

- one line of context: which file was reviewed and that nothing was edited;
- the findings as a list: **one bullet per finding**, each naming the
  element, relationship, or view involved, what is wrong, and why it matters.
  Categorise each finding as **Error** (wrong abstraction or notation — e.g.
  a library modeled as a container), **Warning** (vague label, missing
  description, potential confusion), or **Suggestion** (organisation,
  optional views, clarity);
- a closing line on what you checked and found fine, so the reader knows the
  review was complete — as a line, not a bullet: only problems go in the
  list. If you find nothing, say so in one line.

Name the element, relationship, or view in every finding — a finding that
does not say where the problem is is not a finding. Do not pad the list with
generic advice: only report what is actually wrong in this model. And judge
this model, not a different one: a defensible design choice (what to model,
how to split elements, which technology to name) is not a finding — report
abstraction mistakes, missing or vague descriptions, wrong tags, and
unusable views, not your own architecture opinions. When a finding is about
a view's size, name the view and give the element count — do not list the
elements the view contains.

## The MCP limits

The Structurizr MCP tools have hard limits; keep the review within them:

- **No image rendering.** The MCP cannot produce image files (PNG/SVG); its
  export tools emit diagram source only. The review is over the model
  structure — the DSL text and the MCP facts — never over a rendered
  picture, and it must not claim to have seen one.
- **DSL text only, single file.** The tools work on the workspace's DSL text
  given as one input; the MCP refuses `!include`, `!docs`, and `!adrs`, so a
  multi-file workspace cannot be checked and the documentation/decisions
  findings that `inspect` reports for a single-file workspace are expected
  under the MCP limits — report them as such, not as model mistakes the
  author should fix with `!docs`/`!adrs`.

## When the MCP is absent

The review can still read the DSL text and walk the checklists — that part
is model structure, not tool output. What is not possible without the MCP is
the MCP-based checking: parsing, validation, and `inspect` findings.
Validation is not possible, and you must never describe a review as
validated, parse-checked, or export-checked when the tools are absent — say
plainly that the review is over the DSL text only.
