---
name: c4-view-design
description: Use when the task is designing which C4 views to create for a C4 model being built in Structurizr DSL, and keeping each view readable -- deciding which view kind fits the audience and the question (system context, container, component, dynamic, deployment, filtered, custom), splitting a large model into several small views with explicit include lists, and giving every view a stable explicit key -- for example when asked to "which views to create", "design a container view", "keep a view readable", "view too crowded", or "set up the views for this model". It explains the view design only and does not itself produce any files.
---

# C4 View Design

You are designing the views of a C4 architecture model — which views to
create for which audience, and how to keep each view readable. When you are
writing a fresh workspace from a scenario, the views are part of the
deliverable: design them in the same pass — one system context view plus a
container view per audience question, each within the size bound and
carrying an explicit key (see the rules below). How to write the DSL text
(the view block grammar, the include expressions, the styles) is the
`structurizr-dsl-authoring` skill's task, and the parse/validate/inspect
loop is the `structurizr-validate-loop` skill's task.

## The rules

1. **Pick views by audience and question.** Start with one system context
   view; add a container view per audience question, and the other kinds
   (component, dynamic, deployment, landscape, filtered, custom) only when
   they answer a question the others cannot. The full mapping lives in
   `references/view-selection.md`.
2. **Keep every view to about 20 elements.** A single `include *` view of a
   larger model is not a readable diagram — the spike's 150-element view
   exported a 29,664-pixel-wide SVG. Split it into several views, each with
   an explicit include list, each within the bound.
3. **Give every view an explicit key.** Characters `a-zA-Z0-9_-`, no
   spaces; a view without a key gets an auto-generated one (`Container-001`
   style) that is not guaranteed to be stable — the CLI `inspect` reports
   it as a `views.view.key` finding.
4. **A readable view labels everything it shows.** Every element on a view
   carries a 1–2 sentence description, every relationship on a view carries
   its intent and a technology, and elements you don't own are top-level,
   tagged `External`.
5. **Use groups and filtered views to clarify, not to add.** A group
   boundary organises the elements a view already carries; a filtered view
   is a view on top of another, narrowed by tags — never a reason to draw
   more elements in one diagram.

## Designing the views of a large model

When the model is too big for one view (rule 2), the answer is more views,
not a bigger one:

- One system context view for the "who uses it and what else does it talk
  to" question.
- Several container views, each answering one question (front office, risk
  and compliance, data and batch, ...), each with an explicit include list
  of the elements it needs — not `include *`.
- The same element may appear on several views; a relationship only on the
  views where both its endpoints are included.
- Component, dynamic and deployment views only when their question exists.
- Write the model and all of its views in one pass — the `views` block of
  the same file. A view added in a second write is a round trip you did
  not need.

## Checking the result

Write the whole workspace in one pass — the model and every view in the
single file — then check it with the structurizr MCP `validate` tool and
fix every error it reports. Keep re-running `validate` on the fixed text
until it answers `OK` — do not finish while `validate` is still reporting
errors, and make sure the file on disk is the exact text you last
validated. For this task the `validate` check is the one that matters; the
full parse/validate/inspect loop with finding triage is the
`structurizr-validate-loop` skill's task, and it is not needed here. Your
host prefixes the MCP tool names (for example `structurizr_validate`; the
in-harness server name is `structurizr`), so call whichever prefixed
variant your host exposes.

## The MCP limits

The Structurizr MCP tools have hard limits; keep the workspace within
them:

- **No image rendering.** The MCP cannot produce image files (PNG/SVG);
  its export tools emit diagram source only — PlantUML, C4-PlantUML, or
  Mermaid text. View design is verified through the model and the export
  JSON, never through a rendered picture; the C4-PlantUML export source
  carries its own gotchas — `references/c4-plantuml-gotchas.md`.
- **DSL text only, single file.** The tools work on the workspace's DSL
  text given as one input; there is no multi-file workspace. Inline
  everything into the one file.

## When the MCP is absent

View design is still possible without the MCP — it is model structure, not
tool output. What is not possible is the MCP-based checking: validation is
not possible, and you must never describe a result as validated or
export-checked when the tools are absent.
