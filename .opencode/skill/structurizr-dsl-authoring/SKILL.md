---
name: structurizr-dsl-authoring
description: Use when the task is authoring or fixing Structurizr DSL workspace text -- writing a new workspace.dsl, editing or repairing existing DSL, looking up DSL syntax, or fixing DSL parse errors -- for example when asked to "write a Structurizr DSL workspace", "author or edit workspace.dsl", "DSL syntax", or "fix a DSL parse error". It describes how to write DSL text only and does not itself produce any files.
---

# Structurizr DSL Authoring

You are writing or repairing Structurizr DSL — the text format for C4
architecture workspaces. The workspace is a single file (in practice
`workspace.dsl`); everything below is about that file's text.

## The authoring rules

The rules whose violations surface as parse errors, missing model facts,
or misleading diagrams. The full reference is `references/gotchas.md`
with the exact error strings; the short list:

1. **Declare elements before the relationships that use them.** The DSL
   is parsed top to bottom, so a forward reference fails with
   `The destination element "x" does not exist` — the same error as a
   typo. Check the identifier first, then the order.
2. **Quote every value that contains spaces** — names, descriptions,
   technologies, custom-element metadata. Quotes are optional only for a
   single token; an unquoted phrase with more tokens than the statement
   has left over fails with `Too many tokens, expected: ...`. To skip an
   optional property you want to leave empty, use `""`.
3. **Braces:** the opening `{` sits on the same line as the statement;
   the closing `}` sits on a line of its own.
4. **Identifiers are flat and unique** across the whole workspace by
   default (characters `a-zA-Z_0-9`); a second declaration of the same
   identifier fails with `The identifier "x" is already in use`. Rename
   it — do not delete the element.
5. **Every relationship gets a description and a technology:**
   `a -> b "Reads orders from" "HTTPS/JSON"`. Between the same pair, the
   description is the relationship's identity — two relationships with
   the same description are a duplicate.
6. **Every element gets a description** (a custom `element`'s second
   string is its metadata).
7. **Give every view an explicit key** (characters `a-zA-Z0-9_-`, no
   spaces).

## Where the syntax lives

- `references/syntax.md` — the syntax reference: workspace structure,
  elements (person, softwareSystem, container, component, group, custom
  `element`), relationships and their uniqueness, identifiers (flat and
  hierarchical), constants and variables.
- `references/views-and-styles.md` — views (system landscape/context,
  container, component, dynamic, deployment, filtered), include/exclude
  expressions, styles and the standard C4 recipe, themes, terminology,
  configuration, and the small pattern set.
- `references/gotchas.md` — the error table and the rule behind each
  error, declaration order, implied relationships, and the MCP notes.

Read the reference file that matches the construct you are writing or
fixing; do not guess syntax from memory.

## Checking the result

Before you finish, check the workspace text with the structurizr MCP
`validate` tool and fix every error it reports — a DSL file that does
not validate is not done. Your host prefixes the MCP tool names (for
example `structurizr_validate`; the in-harness server name is
`structurizr`), so call whichever prefixed variant your host exposes. The
full parse/validate/inspect loop with finding triage is the
`structurizr-validate-loop` skill's task — that skill is for validating a
model, not for authoring its text.

## The MCP limits

The Structurizr MCP tools have hard limits; keep the workspace within
them:

- **DSL text only, single file.** The tools work on the workspace's DSL
  text given as one input; there is no multi-file workspace. Inline
  everything into the one file.
- **`!include`, `!docs`, and `!adrs` are refused.** They answer, for
  example, `!include <file> is not permitted (feature
  structurizr.feature.dsl.filesystem is not enabled)` or `!docs is not
  permitted (feature ... documentation is not enabled)`. That is expected
  under the MCP limits: do not use them in the text. If the task asks
  for a multi-file layout, say so in the final answer and deliver the
  single file instead.
- **No image rendering.** The MCP cannot produce image files (PNG/SVG);
  its export tools emit diagram source only — PlantUML, C4-PlantUML, or
  Mermaid text. If images are requested, say so.
- **Never a `!theme` with a URL** (offline validation cannot fetch it);
  `theme default` and the built-in cloud themes are fine.

## When the MCP is absent

If the Structurizr MCP tools are not available in the host, validation is
not possible. State that in the final answer and never describe a DSL
result as validated — a result the tools could not check is unvalidated,
no matter how well it looks.
