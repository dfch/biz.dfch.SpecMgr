# DSL gotchas and errors

The failure modes of `workspace.dsl` text, the rule behind each one, and
how to write the DSL so it does not fail. The error strings are the
pinned Structurizr CLI's own output. Adapted from the Troubleshooting
table of the `structurizr-dsl` skill of `jrjsmrtn/c4-skills` (MIT, see
`NOTICE.md`) and the Structurizr documentation (`structurizr/
structurizr.github.io`, MIT); see `source-map.md` for the
passage-by-passage mapping.

## Error table

| Error | Cause | Fix |
|---|---|---|
| `Too many tokens, expected: person <name> [description] [tags]` | An unquoted value with spaces, or more tokens than the statement still has | Quote the value (`"..."`), or skip the property with `""` |
| `The identifier "x" is already in use at line N` | Duplicate flat identifier (a second element reusing `x`) | Rename the second identifier — never delete the element |
| `The destination element "x" does not exist at line N` | Forward reference (the element is declared later) or a typo | Check the identifier first, then move the declaration above its first use. `The source element "x" does not exist` is the same error for the left side |
| `Unexpected token ... at line N` | `{` on its own line, or unbalanced braces | Move the `{` to the same line as the statement; close on a line of its own |
| `Relationships cannot be added between parents and children at line N` | A relationship from an element to its own child (system to its container) | Relate at the same level instead (person to container, container to container) |
| Implied relationship unwanted | Default behavior | Add `!impliedRelationships false` |
| View is empty | Elements not included | Add `include *` or specific `include` expressions |
| Duplicate relationship | Same source, destination and description | Give each relationship a unique description |
| `View keys can only contain the following characters: a-zA-Z0-9_-` | A view key with spaces or other characters | Use a plain camelCase key (`SystemContext`, `Containers`) — explicit keys only |

## Declaration order

The DSL is parsed top to bottom: it is imperative, not declarative — the
model is built step by step in the order the lines appear (the DSL is a
wrapper over an imperative modeling library, and nothing is hoisted). An
element must be declared before any relationship that references it. A
forward reference fails with `The destination element "x" does not
exist at line N` — the same error as a typo, so check the identifier
first, then the order. Declare all elements first, then the
relationships.

Where a relationship must cross blocks (for example from an element
inside `a` to the element in scope inside `b`), the special `this`
keyword refers to the element in scope — write the relationship where
both ends are already declared, or use `this` on the near end.

## Quoting

Quotes are optional only for a single token without spaces. Every name,
description, technology and metadata value that contains spaces must be
quoted; an unquoted phrase pushes its extra words into the following
positional properties, and once those are filled the parser fails with
`Too many tokens, expected: ...`. To leave an earlier optional property
empty while filling a later one, use `""` as its placeholder.

## Relationship description and technology

Give every relationship both a description and a technology:
`a -> b "Reads orders from" "HTTPS/JSON"`.

- The description is a verb phrase from the source's point of view:
  "Reads orders from", "Publishes events to". Avoid "Uses" and "Calls".
- The technology answers "what would I edit or configure?":
  "Express Router", "Kafka topic orders.v1", "PostgreSQL 16" — not
  "JavaScript".
- A relationship without a technology (or without a description) still
  parses: `validate` answers cleanly, so this is authoring knowledge,
  not an error message — check it when you write or fix a relationship.

Between the same source and destination, the description is the
relationship's identity: two relationships with the same description are
a duplicate, and the only way to model two links between a pair is two
different descriptions.

## Element descriptions

Give every element a description — people, systems, containers,
components and custom elements alike. A missing description also parses
cleanly (for a person or container it surfaces as an `inspect` finding,
for a custom element it does not surface at all), so it is authoring
knowledge, not an error message. For a custom `element`, the second
string is its **metadata** — that is where the human description goes.

## Flat identifiers

Prefer flat identifiers. Skip `!identifiers hierarchical` unless two
elements would otherwise share an identifier — with hierarchical
identifiers every reference must spell out the full path
(`system.api`), and mistakes produce the same "element does not exist"
error as a typo. With flat identifiers, every identifier must be unique
across the whole workspace: a second `api` container in a second system
fails with `The identifier "api" is already in use`. When a fix means
renaming an identifier, rename every reference to it in the same pass.

## Implied relationships

By default the DSL creates "implied relationships" automatically: a
relationship from a person to a container inside a software system
implies a relationship from the person to the software system (and
similarly for the other parent/child combinations). You never write the
implied relationship — it appears in the model and in views
automatically. `!impliedRelationships false` disables the creation;
there is also a strategy setting (`!impliedRelationships
com.structurizr.model.CreateImpliedRelationshipsUnlessSameRelationship
ExistsStrategy`) for finer control.

## Explicit view keys

Give every view an explicit key: `systemContext bookshop "SystemContext"
{ ... }`. The key may only contain `a-zA-Z0-9_-` — no spaces:
`"System Context"` fails with `View keys can only contain the following
characters: a-zA-Z0-9_-`. A view without a key gets an auto-generated
one that `inspect` flags, and that is not guaranteed to be stable over
time (you will likely lose manual layout information); a plain
camelCase key (`SystemContext`, `Containers`) avoids both.

## Under the MCP

- The MCP works on the workspace's DSL text as a single input: no
  `!include`, no `!docs`, no `!adrs` — they are refused
  (`feature ... is not enabled`). Inline everything into the one file;
  that is expected under the MCP limits, not a defect to work around.
- The MCP cannot render images; its export tools emit PlantUML,
  C4-PlantUML or Mermaid **source** only.
- Never reference a theme by URL — offline validation cannot fetch it.
- Check the result with the MCP `validate` tool before you finish; a
  file that does not validate is not done.
