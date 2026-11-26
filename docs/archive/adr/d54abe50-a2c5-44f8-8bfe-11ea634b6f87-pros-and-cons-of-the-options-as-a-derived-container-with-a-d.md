---
status: accepted
decision-makers: dfch
id: d54abe50-a2c5-44f8-8bfe-11ea634b6f87
version: 1.0.0
---

# "Pros and Cons of the Options" as a derived container with a dedicated Option sub-API

## Context and Problem Statement

ADRs document multiple considered options with their trade-offs. MADR renders a "## Pros and Cons of the Options" section with ### Option N: {title} sub-sections. The question is: how should options be managed in the MCP tool surface? Should they be edited through update_section (alongside other body sections), or should they have a dedicated sub-API?

## Decision Drivers

Options are dynamic (created/deleted at different times than other sections); option numbering must be monotonically increasing and never reused; independent management without coupling to the static "Considered Options" prose section.

## Considered Options

Manual editing via update_section (single operation for all options) vs. dedicated API (option_list, option_create, option_read, option_update, option_delete); renumber-on-delete (consecutive 1..N) vs. leave gaps; enforce consistency between "Considered Options" text and Option sub-sections vs. accept drift.

## Decision Outcome

Implement a dedicated Option sub-API with five tools: option_list (returns full titles), option_create (appends new option, returns assigned full title), option_read (returns current content), option_update (full-content replace), option_delete (removes option, returns remaining titles). Options are never individually mandatory (zero options is valid); no deletion sentinel applies to them—removal is exclusively via option_delete. Option numbering is monotonically increasing with a never-reused counter; deleting an option leaves a gap and does not reorder remaining options. Content is an opaque markdown blob (no enforced Good/Bad/Neutral structure). The "Pros and Cons of the Options" heading is auto-rendered if and only if ≥1 Option sub-section exists; otherwise the entire H2 is omitted. Drift between "Considered Options" prose and the Option collection is accepted (no consistency check enforced).

### Consequences

Clear separation of concerns: "Considered Options" is freeform text (updated via update_section); the Option collection is structured (managed via dedicated API). Option numbering gaps prevent confusion about deleted vs. never-created options. Flexibility in content structure (no enforced Good/Bad/Neutral) accommodates diverse writing styles. Trade-off: callers must use two different tool patterns (update_section for prose, option_* for the collection).
