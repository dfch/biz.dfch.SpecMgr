# DSL gotchas

The rules whose violations the validate loop most often meets, and how
to write the DSL so they do not. Each rule exists because breaking it
caused a concrete failure or an unhelpful diagram.

## Declaration order

The DSL is parsed top to bottom. An element must be declared before any
relationship that references it. A forward reference fails with
`The destination element "x" does not exist` — the same error as a
typo, so check the identifier first, then the order. Declare all
elements first, then the relationships; put cross-container component
relationships (for example `spa -> authController`) after the closing
brace of the system that contains both containers, not inside the first
container.

## Quoting

Quote every name, description, and technology. Unquoted strings with
spaces and unbalanced braces surface as `Unexpected tokens` / parse
errors in `validate`.

## Relationship description and technology

Give every relationship both a description and a technology:
`a -> b "Reads orders from" "HTTPS/JSON"`.

- The description is a verb phrase from the source's point of view:
  "Reads orders from", "Publishes events to". Avoid "Uses" and "Calls".
- The technology answers "what would I edit or configure?":
  "Express Router", "TypeORM", "Kafka topic orders.v1", "PostgreSQL
  16" — not "JavaScript".
- Between components in one container, `"In-process call"` is an honest
  technology.

A missing technology is the most common inspect finding
(`model.relationship.technology`); a missing description is the other
half of the pair (`model.relationship.description`).

## Flat identifiers

Prefer flat identifiers. Skip `!identifiers hierarchical` unless two
elements would otherwise share an identifier — with hierarchical
identifiers every reference must spell out the full path, and mistakes
produce the same "element does not exist" error as a typo. With flat
identifiers, every identifier must be unique across the whole model,
and flat identifiers validate on the first try more often.

## Explicit view keys

Give every view an explicit key: `systemContext bookshop "SystemContext"
{ ... }`. The key may only contain `a-zA-Z0-9_-` — no spaces:
`"System Context"` fails with `View keys can only contain the following
characters: a-zA-Z0-9_-`. A view without a key gets an auto-generated
one that `inspect` flags; a plain camelCase key (`SystemContext`,
`Containers`) avoids both.
