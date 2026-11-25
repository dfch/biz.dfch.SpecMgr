# Views, styles and patterns

The view, style, theme and configuration syntax of `workspace.dsl`.
Adapted from the `structurizr-dsl` skill of `jrjsmrtn/c4-skills` (MIT,
see `NOTICE.md`); see `source-map.md` for the passage-by-passage
mapping.

## Views

Every view should carry an **explicit key** (characters `a-zA-Z0-9_-`,
no spaces) — a view without a key gets an auto-generated one that is not
guaranteed to be stable over time, and you will likely lose manual
layout information.

### System Landscape

```dsl
systemLandscape [key] [description] {
    include *
    autoLayout [tb|bt|lr|rl] [rankSep] [nodeSep]
    title "Title"
    description "..."
}
```

### System Context

```dsl
systemContext <systemId> [key] [description] {
    include *
    autoLayout
    title "System Context for X"
}
```

### Container View

```dsl
container <systemId> [key] [description] {
    include *
    autoLayout
    title "Containers for X"
}
```

### Component View

```dsl
component <containerId> [key] [description] {
    include *
    autoLayout
    title "Components of X"
}
```

### Dynamic View

```dsl
dynamic <scope> [key] [description] {
    # scope: * (people/systems), systemId (+ containers), containerId (+ components)
    <source> -> <destination> [description] [technology]
    <source> -> <destination> [description] [technology]
    autoLayout
    title "Feature Y Flow"
}
```

Interactions are automatically numbered in order. To set explicit
ordering:

```dsl
dynamic <scope> [key] [description] {
    1: user -> system.api "submits order" "HTTPS"
    2: system.api -> system.db "persists order" "SQL"
    3: system.api -> system.queue "publishes event" "AMQP"
}
```

### Deployment View

```dsl
deployment <systemId|*> <environment> [key] [description] {
    include *
    autoLayout
    title "Production Deployment"
}
```

### Filtered View

```dsl
filtered <baseViewKey> <include|exclude> <tags> [key] [description]
```

Creates a view on top of another, filtering elements by tags. The base
view is hidden when a filtered view exists.

### AutoLayout

```dsl
autoLayout [direction] [rankSeparation] [nodeSeparation]
# direction: tb (default), bt, lr, rl
# default separations: 300px each
```

### Include/Exclude with Expressions

Element expressions:

```dsl
include element.type==Container
include element.tag==Database
include element.tag!=External
include element.parent==<id>
include element.technology==PostgreSQL
include ->system.api->                 # elements connected to system.api (both directions)
include ->system.api                   # elements that depend on system.api (afferent)
include system.api->                   # elements system.api depends on (efferent)
```

Combine with `&&` (AND) and `||` (OR):

```dsl
include element.type==Container && element.tag!=External
```

Relationship expressions:

```dsl
include * -> *                         # all relationships between included elements
include user -> *                      # all relationships from user
include * -> system.db                 # all relationships to database
include relationship.tag==Async
include relationship==system.api->system.db
```

The reluctant wildcard includes everything `*` does, minus orphaned
elements (elements with no relationships in the view):

```dsl
include *?
```

`exclude` takes the same expressions.

## Styles

### Element Styles

```dsl
styles {
    element <tag> {
        shape <shape>                  # see shapes below
        icon <file|url>
        width <int>
        height <int>
        background <#rrggbb>
        color <#rrggbb>               # text color (alias: colour)
        stroke <#rrggbb>              # border color
        strokeWidth <1-10>
        fontSize <int>
        border <solid|dashed|dotted>
        opacity <0-100>
        metadata <true|false>          # show/hide metadata line
        description <true|false>       # show/hide description
    }
}
```

**Shapes**: `Box`, `RoundedBox`, `Circle`, `Ellipse`, `Hexagon`,
`Diamond`, `Cylinder`, `Pipe`, `Person`, `Robot`, `Folder`,
`WebBrowser`, `Window`, `Terminal`, `MobileDevicePortrait`,
`MobileDeviceLandscape`, `Component`

### Relationship Styles

```dsl
styles {
    relationship <tag> {
        thickness <int>
        color <#rrggbb>
        style <solid|dashed|dotted>
        routing <Direct|Orthogonal|Curved>
        fontSize <int>
        width <int>
        position <0-100>               # label position along line
        opacity <0-100>
    }
}
```

### Styling All Elements/Relationships

Use the default tags:

```dsl
styles {
    element "Element" { ... }           # applies to ALL elements
    relationship "Relationship" { ... } # applies to ALL relationships
}
```

### Light/Dark Mode

```dsl
styles {
    light {
        element "Person" { background #08427B; color #ffffff }
    }
    dark {
        element "Person" { background #1a6bc4; color #ffffff }
    }
}
```

### Standard Style Recipe

```dsl
styles {
    element "Person" {
        shape Person
        background #08427B
        color #ffffff
    }
    element "Software System" {
        background #1168BD
        color #ffffff
    }
    element "External" {
        background #999999
        color #ffffff
    }
    element "Container" {
        background #438DD5
        color #ffffff
    }
    element "Component" {
        background #85BBF0
        color #000000
    }
    element "Database" {
        shape Cylinder
    }
    element "Web" {
        shape WebBrowser
    }
    element "Queue" {
        shape Pipe
    }
    relationship "Relationship" {
        routing Orthogonal
    }
    relationship "Async" {
        style dashed
    }
}
```

## Themes

```dsl
views {
    theme default                      # Structurizr default theme
}
```

Built-in cloud themes (by name, no URL needed):
`amazon-web-services-2020.04.30`, `microsoft-azure-2021.01.26`,
`google-cloud-platform`, `kubernetes`. Custom styles override theme
defaults. Never reference a theme by URL — offline validation cannot
fetch it.

## Terminology

Customize C4 terminology for your organization:

```dsl
views {
    terminology {
        person "Actor"
        softwareSystem "Application"
        container "Service"
        component "Module"
        deploymentNode "Server"
        relationship "Dependency"
    }
}
```

## Configuration

```dsl
configuration {
    scope <landscape|softwaresystem|none>
    visibility <private|public>
    users {
        "user@example.com" read
        "admin@example.com" write
    }
}
```

## Directives for existing elements

Modify elements or relationships defined elsewhere:

```dsl
!element <identifier> {
    description "Updated description"
    tags "NewTag"
}
```

Bulk operations:

```dsl
!elements element.tag==Container {
    tags "Monitored"
    properties { "team" "platform" }
}

!relationships relationship.tag==Async {
    tags "EventDriven"
}
```

## Common patterns

### Tagging for Filtered Views

```dsl
model {
    system = softwareSystem "System" {
        api = container "API" "REST API" "Go" "Service,v2"
        legacyApi = container "Legacy API" "Old REST API" "Java" "Service,v1,Deprecated"
    }
}
views {
    container system "AllContainers" { include * }
    filtered "AllContainers" exclude "Deprecated" "CurrentContainers"
}
```

### Async/Sync Relationship Distinction

```dsl
model {
    system.api -> system.db "queries" "SQL"
    system.api -> system.queue "publishes order events to" "AMQP" "Async"
    system.worker -> system.queue "consumes order events from" "AMQP" "Async"
}
views {
    styles {
        relationship "Async" { style dashed }
    }
}
```
