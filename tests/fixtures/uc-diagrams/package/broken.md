---
created: '2026-10-04T00:00:00.000Z'
id: 44444444-4444-4444-8444-444444444444
status: draft
type: uc
updated: '2026-10-04T00:00:00.000Z'
version: 1.0.0
---

# Broken Fixture

## Characteristic Information

### Goal in Context

This fixture document is deliberately broken: it lacks the required
sections, so it fails `parse_uc` (an existing-but-broken document — the
`PackageDocument(id, None)` slot of rulebook §2.7, skipped as a node; any
reference to it takes the §2.8 unresolvable-note path).
