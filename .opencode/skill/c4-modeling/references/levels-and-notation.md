# Levels, notation, and workflow

The C4 model defines four levels of abstraction. Each has a precise
meaning — do not conflate them.

## Level 1: Software System

- The highest level. Delivers value to its users (human or not).
- Typically owned by a single team, deployed together, lives in one repo.
- Is NOT: a product domain, bounded context, business capability, or team
  structure.
- Its standard diagram is the system context diagram: the system, its
  users, and the external systems it interacts with.

## Level 2: Container

- A separately running process or data store required for the system to
  work.
- A **runtime boundary** — not a code-organization unit.
- Examples: server-side web app, SPA (client-side), mobile app, database,
  message queue, serverless function, shell script, file/blob storage.
- **NOT containers**: JARs, DLLs, assemblies, libraries, modules — these
  are code-level constructs.
- **NOT Docker containers** — the name is coincidental.
- A single-page app is TWO containers: the server delivering the static
  files, and the client-side app running in the browser.
- Cloud services you own (S3 buckets, RDS instances) are containers, not
  external systems.

## Level 3: Component

- A grouping of related functionality behind a well-defined interface,
  within a single container.
- All components share the same process space — they are NOT separately
  deployable.
- Language-dependent: classes (OOP), modules (JS), grouped functions
  (FP), files in a directory (C).
- NOT the same as packages, namespaces, or folder structures.
- Focus on architecturally significant groupings. Exclude utility classes
  and data models initially.

## Level 4: Code

- Classes, interfaces, functions, database tables.
- Almost always generated from code, never maintained manually.

## Notation Rules

Every C4 diagram must follow these rules:

### Required Elements

- **Title**: Every diagram has a title stating its type and scope
- **Legend/key**: Every diagram has a key explaining the notation
- **Element types**: Every element explicitly states its type (Person,
  Software System, Container, Component)
- **Descriptions**: Short descriptions (1-2 sentences) conveying key
  responsibilities

### Technology Labels

- All containers must specify their technology (e.g., "Python/FastAPI",
  "PostgreSQL 16")
- All components must specify their technology (e.g., "React Component",
  "Java Service")
- Every relationship includes a protocol/technology (e.g., "JSON/HTTPS",
  "JDBC", "gRPC") — including person→container relationships; a
  relationship without a technology is incomplete

### Relationship Lines

- Unidirectional only
- Every line labeled with intent matching the direction
- Avoid vague labels: "Uses" is almost always wrong
- Good: "sends customer update events to", "reads credentials from",
  "queries"
- Bad: "Uses", "Connects to", "Interacts with", "Talks to",
  "Communicates with"

### Visual Consistency

- Colors must be consistent within and across diagrams
- Consider B&W printing and color blindness
- Acronyms must be understandable to the audience or explained in the
  legend

## Workflow: Adding Elements to a Model

### Step 1: Identify the Abstraction Level

Before adding anything, determine what you're modeling:

- Is it a separately running process? → Container
- Is it a logical grouping within a process? → Component
- Is it an external system you don't own? → Software System (external)
- Is it a user or role? → Person

### Step 2: Define the Element

For each new element, determine:

1. **Name**: Clear, unambiguous (unique within scope)
2. **Description**: 1-2 sentences on its responsibility
3. **Technology**: What it's built with (containers and components)
4. **Tags**: For styling (e.g., "Database", "Web", "External")

### Step 3: Define Relationships

For each relationship:

1. **Direction**: Source → Destination (who initiates?)
2. **Description**: What is the intent? (not "uses" — be specific)
3. **Technology**: Protocol or mechanism — on every relationship,
   including person→container

Which views to create, and how to keep each of them readable, is the
`c4-view-design` skill's task — not part of the element workflow.
