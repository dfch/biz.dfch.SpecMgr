# View checklist

Walk each view in the model. The review judges the views as recorded in the
DSL — which views exist, how they are keyed, and what they carry — never a
rendered picture (the MCP cannot produce one; see "The MCP limits" in
`SKILL.md`). The design rules for choosing and splitting views are the
`c4-view-design` skill's task; here you only judge the views that exist
against the criteria below.

## Existence and scope

- [ ] A system context view exists (required for all projects), showing the
  system at the centre with its users and external systems, without internal
  containers, components, or technology detail.
- [ ] A container view exists (required for all projects), showing the
  containers within the system boundary plus the people and external systems
  that interact with them, without deployment detail.
- [ ] A component view (if present) is scoped to a single container and only
  created where the internal structure matters.
- [ ] A dynamic view (if present) is scoped to one feature or use case with
  numbered interactions, and carries only the elements involved in that flow.
- [ ] A deployment view (if present) is scoped to one environment and shows
  deployment nodes, not just containers.

## Keys and size

- [ ] Every view has an explicit key (characters `a-zA-Z0-9_-`, no spaces).
  A view whose DSL omits the key is assigned an auto-generated key
  (`Container-001` style) that is not guaranteed to be stable over time —
  the MCP `inspect` tool reports it as a `views.view.key` finding. An
  auto-generated key is a **Warning**: name the view and say the key should
  be explicit.
- [ ] Every view stays readable in size — about 20 elements per view is the
  practical bound (a far larger single view exports to an unusable diagram).
  A view that carries more is a **Warning**: name the view and state how
  many elements it carries (do not list the elements themselves), and say it
  should be split into several smaller views with explicit include lists
  (the split itself is the `c4-view-design` skill's job — you only report
  the problem).
- [ ] A view that includes everything by wildcard (`include *`) over a large
  model is the usual cause of the size problem above.

## Content

- [ ] The views include the elements their audience needs, and no view mixes
  abstraction levels (e.g. a system context view showing containers).
- [ ] Every element on a view carries the description and label it needs
  there — the element and relationship checklists above apply to what each
  view shows, not only to the model.
