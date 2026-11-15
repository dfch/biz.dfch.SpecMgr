# View selection: which views to create

Which views a model needs — the audience and the question first, then the
view kind. The view block grammar and the include expressions themselves
are the `structurizr-dsl-authoring` skill's territory (`references/
views-and-styles.md` there); this file is about the selection.

## Diagram Types

### Core Diagrams (the "4 Cs")

| Diagram | Scope | Shows | Audience | Recommended? |
|---------|-------|-------|----------|-------------|
| System Context | One software system | System + users + external systems | Everyone | Yes, always |
| Container | One software system | Containers inside the system | Technical staff | Yes, always |
| Component | One container | Components inside the container | Developers | Only if valuable |
| Code | One component | Classes/modules/tables | Developers | No, generate if needed |

### Supporting Diagrams

| Diagram | Scope | Shows | When to Use |
|---------|-------|-------|-------------|
| System Landscape | Enterprise/org | All systems and their connections | Large organizations, enterprise views |
| Dynamic | Feature/use case | Runtime interactions with numbered sequence | Complex interaction flows, specific scenarios |
| Deployment | One+ systems in one environment | Infrastructure, nodes, deployed instances | Infrastructure documentation, ops audience |

## Diagram Selection Guide

**"Who is the audience?"**
- Everyone (including business) → System Context or System Landscape
- Technical staff → Container or Deployment
- Developers → Component (sparingly) or Dynamic

**"What question does the diagram answer?"**
- "What does the system do and who uses it?" → System Context
- "What are the main technical building blocks?" → Container
- "How is container X structured internally?" → Component
- "How does feature Y work at runtime?" → Dynamic
- "Where does it run?" → Deployment
- "What systems exist across the organization?" → System Landscape

## The view kinds of the Structurizr DSL

Which kind exists, and when each is the right one:

- **System Landscape** — all the software systems of an organization and
  the connections between them; the enterprise-level context, before
  zooming into one system.
- **System Context** — one system in the centre, surrounded by its users
  and the other systems it interacts with; the good starting point for
  diagramming and documenting a software system.
- **Container** — zoom into one system: the applications and data stores
  (what C4 calls its containers) that reside inside it, and the people
  and external systems they touch.
- **Component** — zoom into one container: the components that reside
  inside it; only when the container's internal structure matters.
- **Dynamic** — a subset of the elements of the model and the ordered
  sequence of relationships between them, showing how one use case, story
  or feature works at runtime.
- **Deployment** — how software systems and containers are deployed: the
  mapping of container instances onto deployment nodes in one environment.
- **Filtered** — a view on top of another view, narrowed to (or excluding)
  the elements and relationships carrying given tags. The base view is
  hidden from the diagram list when a filtered view exists — to keep
  showing it, add a filtered view that includes everything.
- **Custom** — an ad hoc diagram over the same model+view engine, for
  content that is not C4. A custom view can contain custom elements only —
  the pinned parser refuses to add containers, components, people or
  software systems to it.

## Keeping a view readable

- **Groups** — a named boundary around the elements of a view, for
  organisational or ownership grouping. A group organises what a view
  already carries; it never adds elements.
- **Filtered views** — when a view is too big for one audience, do not
  copy it: filter it. Tag the elements that matter to that audience and
  derive a filtered view from the base by those tags.
- **Several small views beat one big one** — the element bound and the
  split strategy are in `references/view-size-and-keys.md`.
