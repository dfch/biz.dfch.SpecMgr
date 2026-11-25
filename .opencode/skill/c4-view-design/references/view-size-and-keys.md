# View size and explicit keys

The two mechanical rules that keep a set of views readable, and why.

## The size rule: about 20 elements per view

A view is a diagram; a diagram is only readable up to a size. The
practical bound is about 20 elements per view — a 150-element view
validated and exported fine, but its SVG was 29,664 pixels wide and
unusable as a diagram (the spike's scale finding).

What counts as an element of a view: everything the view's include
statements bring in. For a container view with a bare `include *`, that is
the system's containers plus every element linked to them (the people, the
other systems, the custom elements); the scoped system itself is not
counted. An explicit include list carries exactly what you list — nothing
else.

Consequences:

- A model with more than about 20 elements does NOT get one `include *`
  view of everything. It gets several views, each with an explicit include
  list of the elements it needs, each within the bound.
- The same element may appear on several views; the split follows the
  audience questions (front office / risk and compliance / data and
  batch), not the code layout.
- A filtered view renders a subset of its base view, so it cannot be
  bigger than the base — filtering narrows, it does not fix, an over-bound
  base.

## Explicit view keys

Give every view an explicit key. The constraint: `a-zA-Z0-9_-`, no
spaces. A view without a key gets an auto-generated one — the exporter
names it `<Kind>-NNN` (`Container-001`, `SystemContext-001`, ...) and
marks the exported view `generatedKey: true`. Auto-generated keys are not
guaranteed to be stable over time, manual layout information is lost when
they move, and the CLI `inspect` reports each of them as a `views.view.key`
finding, in its own words:

```
The view with key "Container-001" has an automatically generated view key
and this is not guaranteed to be stable over time.
```

Pick keys that name the view's question (`CustomerContext`, `FrontOffice`,
`RiskCompliance`), and keep them once chosen — they are the stable handle
of a view.
