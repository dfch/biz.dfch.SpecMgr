---
classification: null
created: '2026-09-03 10:26:29.090+02:00'
id: 678319da-f8e6-4f65-8f98-1096024012af
status: rejected
type: req
updated: '2026-11-07T09:38:39.334+01:00'
version: 1.0.0
---

# Architecture Decision Record Document Management

THE system shall provide Architecture Decision Record document management, including create, read, update-frontmatter, update-section, option management, status-change, and validate operations for MADR-style decision records with a Context/Decision Drivers/Considered Options/Decision Outcome/Pros-and-Cons-of-the-Options structure.

## Description

Rejected per GitHub issue #46 (the decision-record artifact-type removal feature): the Architecture Decision Record artifact type has been removed from the system. The decision-record surface this requirement describes (the per-domain create/read/update-frontmatter/update-section/option-management tools and the dedicated status-change dispatch) no longer exists: the 46 existing decision records were converted to DEC documents that reuse their ids and file names, and decisions of any kind are now managed through the `dec` domain and the generic whole-body tools. The original description's present-tense tool surface and its 28-existing-records count are obsolete as of the removal (2026-11-07).

## Characteristics

1. Functional Suitability

## Level

SRS

## Source

AGENTS.md's Status section (the former decision-record bullet) and the decision-record tool plan in the feat-9-doc-in-specmgr feature folder.

## Related Artifacts

### Goals

- GOL 08666592-a2d2-4309-95c6-3c94248ca342: AI-Agent-Native Specification Artifact Management
