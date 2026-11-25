# C4-PlantUML export gotchas

A short reference note (the spike's Finding 4) for when a view's export
source is C4-PlantUML. The C4-PlantUML export has behaviours that a parser
check cannot catch — the source is valid and the export succeeds, but the
diagram is not what the model says:

- **Custom elements are silently dropped.** An element created with the
  `element` keyword (no C4 type) does not appear in the C4-PlantUML output
  — no warning. If a view carries custom elements, the C4-PlantUML export
  of that view is incomplete; use the Structurizr-flavour export for it.
- **`include *`-pulled elements can be dropped too.** Elements the view
  pulled in by a wildcard include have been silently omitted by the C4
  export (the spike lost two wildcard-included elements this way). Keep C4
  views on explicit include lists, and treat a rendered C4 diagram missing
  expected elements as an export gap, not a model gap.
- **Tags and styles are off by default.** The default C4 export drops tags
  and styles (`$tags=""`); the view properties `c4plantuml.tags "true"` and
  `c4plantuml.elementProperties "true"` restore tags, colours and element
  properties.
- **The default `Element` tag needs an explicit background colour.** With
  tags on, every element carries the default `Element` tag; without an
  explicit background colour for it, the render is valid but unreadable —
  white text on white. Give the `Element` tag (and the other default tags
  you rely on) explicit colours in the styles.

The MCP itself emits this export *source* text only — it renders no image
(see `SKILL.md`, the MCP limits), so none of the gotchas is visible in
what the MCP returns; they only matter when the source is rendered
downstream.
