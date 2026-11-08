# Structurizr DSL syntax

The syntax reference for writing `workspace.dsl` text. Adapted from the
`structurizr-dsl` skill of `jrjsmrtn/c4-skills` (MIT, see `NOTICE.md`)
with details from the Structurizr documentation
(`structurizr/structurizr.github.io`, MIT); see `source-map.md` for the
passage-by-passage mapping.

## Syntax fundamentals

- Lines are processed **sequentially** — no forward references
- Keywords are **case-insensitive** (`softwareSystem` = `softwaresystem`)
- Double quotes are optional for single-word values without spaces
- Opening `{` must be on the **same line** as the statement
- Closing `}` must be on its **own line**
- Opening/closing braces are only required when adding child content
- Use `""` as a placeholder for an earlier optional property that you
  want to skip (for example `person "Name" "" "Tag"` — no description,
  but a tag)
- Tags are comma separated (`"Tag 1,Tag 2,Tag 3"`)
- Comments: `//` or `#` (single-line), `/* ... */` (multi-line)
- Line continuation: `\` as the last character on the line
- Identifier characters: `a-zA-Z_0-9`

### Constants and Variables

```dsl
!const SYSTEM_NAME "My System"        # immutable
!var VERSION "1.0"                    # redefinable
# Reference: ${SYSTEM_NAME}, ${VERSION}
```

Constant and variable names may only contain `a-zA-Z0-9-_.`. String
substitution runs on any token written as `${NAME}`, where `NAME` is a
constant, a variable, or an environment variable; a name that cannot be
found is left unsubstituted.

## Workspace structure

```dsl
workspace [name] [description] {
    !identifiers hierarchical          # recommended for non-trivial models
    !impliedRelationships true         # default: auto-creates parent relationships

    model {
        # people, systems, relationships
    }

    views {
        # diagram definitions, styles, themes
    }

    configuration {
        # scope, visibility, users
    }
}
```

## Model elements

By default every element is **anonymous** — it cannot be referenced from
the DSL. Give an element an identifier where you plan to reference it
(relationships, view include/exclude, ...): `p = person "User"`.

### Person

```dsl
<id> = person <name> [description] [tags]
# or with block:
<id> = person <name> [description] [tags] {
    description "..."
    tags "Tag1" "Tag2"
    url "https://..."
    properties { key value }
    -> <target> [description] [technology] [tags]
}
```

Default tags: `Element`, `Person`

### Software System

```dsl
<id> = softwareSystem <name> [description] [tags] {
    group <name> { ... }
    <id> = container <name> [description] [technology] [tags] { ... }
    -> <target> [description] [technology] [tags]
}
```

Default tags: `Element`, `Software System`

### Container

```dsl
<id> = container <name> [description] [technology] [tags] {
    group <name> { ... }
    <id> = component <name> [description] [technology] [tags] { ... }
    -> <target> [description] [technology] [tags]
}
```

Default tags: `Element`, `Container`

### Component

```dsl
<id> = component <name> [description] [technology] [tags] {
    description "..."
    technology "..."
    tags "..."
    -> <target> [description] [technology] [tags]
}
```

Default tags: `Element`, `Component`

### Custom element

The `element` keyword defines a custom element that sits outside of the
C4 model — hardware, a third-party feed, anything that is not a person,
system, container or component:

```dsl
<id> = element <name> [metadata] [description] [tags]
```

Default tags: `Element`. In the exported model the first optional string
is the element's **metadata** — when in doubt, put the human description
there.

### Group

```dsl
group <name> {
    # elements of the same type
}
```

Style groups with the `Group:Name` tag. For nested groups:

```dsl
model {
    properties {
        "structurizr.groupSeparator" "/"
    }
    group "Organization" {
        group "Department" {
            system = softwareSystem "System"
        }
    }
}
```

## Relationships

```dsl
# Explicit
<source> -> <destination> [description] [technology] [tags]

# Within element block (implicit source = this)
-> <destination> [description] [technology] [tags]

# With properties
<source> -> <destination> [description] [technology] [tags] {
    tags "Async"
    url "https://..."
    properties { key value }
}

# Remove a relationship
<source> -/> <destination>
```

The special `this` identifier refers to the element in scope, so
`a.aa -> this { ... }` inside `b.bb`'s block is the same as
`a.aa -> b.bb { ... }`. Relationships can also be assigned an
identifier: `rel = p -> ss "Uses"`.

Default tags: `Relationship`

### Uniqueness

Relationships between the same source and destination must have
**unique descriptions**. This is the only way the DSL distinguishes
multiple relationships between the same pair.

Relationships run between elements of compatible types (person,
software system, container, component, and custom elements mix freely);
a relationship **from an element to its own child** (for example a
software system to one of its containers) is rejected — relate at the
same level instead (person to container, container to container).

## Identifiers

### Flat (default)

All identifiers are globally scoped. Every identifier must be unique
across the entire workspace — a second `api` container in a second
system fails with `The identifier "api" is already in use`.

### Hierarchical (recommended)

```dsl
!identifiers hierarchical
```

Identifiers are scoped to their parent. Reference as `parent.child`:

```dsl
system = softwareSystem "System" {
    api = container "API"
    db = container "Database"
}
# Reference: system.api, system.db
```

`!identifiers hierarchical` does not apply to groups, and it does not
affect relationship identifiers.
