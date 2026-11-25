# Element checklist

Walk every element in the model against these criteria. Judge the DSL text
itself — the names, descriptions, tags, and placement of each element — not a
rendered picture.

## People / actors

- [ ] Every person has a clear, specific name (not "User" unless truly generic).
- [ ] Every person has a description stating their role or goal.
- [ ] No duplicate people representing the same role.
- [ ] External vs internal actors are distinguished (via tags or naming).

## Software systems

- [ ] The system being modeled has a name and a description.
- [ ] External systems are clearly identified — tagged `External` or similar.
  A third-party thing operated by a different organization must be a
  top-level element carrying that tag; a top-level element for a third party
  without the tag is a **Warning**: readers cannot tell owned from external.
  A top-level `element` (or `softwareSystem`) with the `External` tag is the
  correct representation of a third party — do not flag such an element for
  not being a `softwareSystem`.
- [ ] Each external system has a description explaining what it provides.
- [ ] No system is modeled that should actually be a container (e.g. a
  database you own).
- [ ] System names are unique and unambiguous.

## Containers

- [ ] Every container represents a **runtime boundary** (a separately
  running process or a data store).
- [ ] No libraries, modules, or packages modeled as containers. A shared
  rules library, a JAR, a module, or a package is code-level: it runs inside
  another element's process and is not an element of its own. Finding one
  modeled as a container is an **Error** — name the container and say what
  level it actually belongs at.
- [ ] Every container has a technology specified.
- [ ] Every container has a meaningful description (not just restating the
  name, and not a bare list of technology names — "Technology Soup" is a
  description that is just technology names, where the description should
  state the responsibility).
- [ ] Database containers use the "Database" tag for the cylinder shape.
- [ ] No containers that should be external systems (services you don't own
  or deploy).

## Components (if present)

- [ ] Components represent architecturally significant groupings, not just
  folder structure (the "Code Structure Mirror" — components that exactly
  match package or module structure model code organization, not
  architecture).
- [ ] Every component has a technology specified.
- [ ] Components are within a single container (not spanning containers).
- [ ] The component view adds genuine value (if not, recommend removing it —
  a stale component diagram that no longer matches the code is worse than
  none).

## Completeness

- [ ] A missing relationship is a finding only when the model's own
  descriptions claim it (a description that names a counterpart the model has
  no edge to). Do not invent communication paths the model does not claim.
- [ ] No orphaned elements — elements with no relationships. The MCP
  `inspect` tool reports these as disconnected elements and as elements not
  included on any views; an orphan is a **Warning** (it is either dead weight
  or a relationship the model forgot) — name the element and say what is
  missing.
- [ ] A system context view and a container view exist at minimum (the
  "Missing Middle" — a system context view with no container view jumps
  straight to components).

## Anti-patterns worth flagging

- **The "Docker Confusion"** — Docker containers modeled as C4 containers,
  or C4 containers modeled as Docker containers. C4 containers are runtime
  boundaries; Docker is a deployment mechanism (it belongs in the deployment
  view).
- **The "Technology Soup"** — element descriptions that are just technology
  names, where the description should state the responsibility.
