---
name: c4-modeling
description: Use when the task is making C4 modeling decisions for a software architecture -- deciding which C4 level an element belongs to, what counts as a container and what does not (libraries, data stores, third-party services), how to model an external system, and how to name elements and label relationships -- for example when asked to "create a C4 model", "decide what is a container", "model an external system", "C4 levels", or "label these relationships". It explains the modeling decisions only and does not itself produce any files.
---

# C4 Modeling

You are making the modeling decisions for a C4 architecture model — which
abstraction level each element belongs to, what a container is (and what
one is not), how to model external and third-party systems, and how to
name elements and label relationships. How to write the DSL text is the
`structurizr-dsl-authoring` skill's task, and the parse/validate/inspect
loop is the `structurizr-validate-loop` skill's task.

## The decisions

The decisions a model gets wrong most often, in the order the questions
come up:

1. **Pick the abstraction level first.** Person (a user or role), Software
   System (Level 1), Container (Level 2), Component (Level 3), Code
   (Level 4) — each level has a precise meaning; do not conflate them.
2. **A container is a runtime boundary** — a separately running process
   or a data store (a web app, a service, a database, a queue). A
   library, a JAR, a module, or a package is NOT a container: code that
   runs inside another element's process is not its own element. A C4
   container is not a Docker container. When several elements share or
   embed a library, the library is STILL no element — no container, no
   component, and no "embeds" relationship to it; name the library in
   the sharing elements' descriptions instead.
3. **External and third-party systems are top-level, tagged
   `External`.** Something you do not own or operate is a top-level
   `softwareSystem` (or `element`) with the `External` tag — never a
   container inside your system. In this DSL version there is no
   `externalSystem` keyword.
4. **Name and describe every element.** A 1–2 sentence description of its
   responsibility; containers and components carry a technology label.
5. **Label every relationship with its intent and a technology.**
   Unidirectional; "sends notification emails to", never a vague "uses",
   "connects to" or "interacts with"; EVERY relationship names a protocol
   or technology — including person→container relationships (e.g.
   "HTTPS/JSON"); a relationship without a technology is incomplete.
6. **Split containers on runtime boundaries** (independent deployment,
   scaling, technology, availability) — not on code modules. Add
   components only when a container's internal structure is
   architecturally significant.

The full rules — the levels, the notation, the workflow, and the common
mistakes — live in `references/levels-and-notation.md` and
`references/modeling-decisions.md`. Read the file that matches the
decision you are making.

## Checking the result

Before you finish, check the workspace text with the structurizr MCP
`validate` tool and fix every error it reports. Keep re-running it on the
fixed text until it answers `OK` — do not finish while `validate` is
still reporting errors, and make sure the file on disk is the exact text
you last validated. A model whose workspace does not validate is not
done. Your host prefixes the MCP tool names (for example
`structurizr_validate`; the in-harness server name is `structurizr`), so
call whichever prefixed variant your host exposes. The full
parse/validate/inspect loop with finding triage is the
`structurizr-validate-loop` skill's task — this skill decides what to
model; that skill proves the text is right.

## The MCP limits

The Structurizr MCP tools have hard limits; keep the workspace within
them:

- **DSL text only, single file.** The tools work on the workspace's DSL
  text given as one input; there is no multi-file workspace. Inline
  everything into the one file; `!include` and `!docs` are refused
  (expected under the MCP limits — do not use them).
- **No image rendering.** The MCP cannot produce image files (PNG/SVG);
  its export tools emit diagram source only — PlantUML, C4-PlantUML, or
  Mermaid text. If images are requested, say so.

## When the MCP is absent

If the Structurizr MCP tools are not available in the host, validation is
not possible. State that in the final answer and never describe a DSL
result as validated — a result the tools could not check is
unvalidated, no matter how well it looks.
