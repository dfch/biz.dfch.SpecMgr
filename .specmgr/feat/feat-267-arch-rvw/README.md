---
classification: null
created: '2026-11-18T13:21:29.973+01:00'
id: feat-267-arch-rvw
status: planning
type: feat
updated: '2026-11-22T17:30:00.000+01:00'
version: 1.0.0
---

# Feature: Consolidate the architecture model (R+W viewpoints and perspectives, metamodel) and its C4/Structurizr mapping

## Plan

### Overview

GitHub issue #267. The architecture review checklist (TXT 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9) uses the seven core viewpoints of Rozanski and Woods (R+W), 12 perspectives and a Structurizr mapping. Definitions are spread over the checklist, QA 25bd5b93-a228-4d6c-8b70-d143dfd39444 and ChatGPT sessions, and they drift from the book. This feature consolidates the architecture model so that it can be mapped to a C4 model in Structurizr. Phase 1 is design only and stops for validation.

### Requirements

- REQ-001: The viewpoint concern lists quote the R+W book verbatim. Every deviation is labelled "catalogue extension".
- REQ-002: Every extra topic of the earlier viewpoint definitions has a placement in a viewpoint, a perspective or a matrix cell.
- REQ-003: The perspective set is the 9 ISO/IEC 25010:2023 characteristics plus Regulation, Location and Resources (RS; the R+W Development Resource perspective, re-scoped to the full lifecycle). R+W perspective guidance is mapped to these 12 codes.
- REQ-004: The metamodel is given as PlantUML class diagrams that pass the specmgr validation.
- REQ-005: Each viewpoint and each perspective has a concrete Structurizr mapping with a coverage statement. Unverified facts are marked "to be confirmed".
- REQ-006: Principles, patterns and tactics have a defined home. Adopted principles and patterns are DECs.

### Acceptance Criteria

- [x] ACC-001: A new TXT "Architecture Model" exists and passes validation.
- [x] ACC-002: The checklist TXT refers to the new TXT for concern lists and states that the applicability derivation is our interpretation.
- [x] ACC-003: Both metamodel diagrams exist in the feature folder and pass validate_plantuml.
- [ ] ACC-004: Open items of QA 25bd5b93 are closed or narrowed, and missing sources are named.
- [x] ACC-005: The ChatGPT transcripts and the old review file are in the feature folder.

### Scope

#### Included

- New TXT "Architecture Model" with metamodel, viewpoints, perspectives, principles, patterns and tactics, and the Structurizr mapping.
- Corrections to the checklist TXT.
- Two PlantUML metamodel diagrams.
- QA update and housekeeping.

#### Explicitly Out Of Scope

- Re-running the Structurizr probe (after validation of the design).
- The c4-\* agents and skills (issue #250).
- A viewpoint resource.
- Creating principle DECs.
- The ARC artifact (issue #228).

### Dependencies

#### Depends On

- The R+W book, ISO/IEC/IEEE 42010, 29148 and Martin, Clean Architecture, as markdown in the sibling docs repository.

#### Blocks

- Issue #228 and issue #250, which build on the metamodel and the mapping.

### Design Notes

- A viewpoint is catalogue knowledge (resource and skill), not a specmgr artifact. Instances (workspaces, views) are the future ARC artifact.
- Adopted principles and patterns are DECs, one per item. Discovery uses a hub document (authoritative), the tags arch.principle and arch.pattern (convention), and a scope of general or view-specific.
- The metamodel diagrams are the single source. The TXT links to them by path.

### Related Decisions

- QA 25bd5b93-a228-4d6c-8b70-d143dfd39444: Architecture Review Checklist: Decisions and Open Items

### Task List

#### Phase 100: Set-up and housekeeping

- [x] Task 100.100: Create issue #267 and this feature.
- [x] Task 100.110: Move the ChatGPT transcripts and the old review file into this folder.
- [x] Task 100.120: Rename the checklist TXT file.

#### Phase 110: Design

- [x] Task 110.100: Metamodel diagram A (conceptual) and B (Structurizr realisation).
- [x] Task 110.110: New TXT "Architecture Model" (30983f27-f5aa-4d42-972e-5593f0c3ba09).
- [x] Task 110.120: Correct the checklist TXT (Draft 0.9).
- [x] Task 110.130: Update QA 25bd5b93.
- [x] Task 110.150: Close the metamodel gaps of the review: MatrixRow and CrossView, decision applies pattern and tactic, Element supertype in diagram B, C4 view as a presentation of 42010 views. Test multiple review results per element in Structurizr (QA 0.0680; Architecture Model Draft 0.5).
- [x] Task 110.140: Verify the principle tags PR09 to PR12 against Clean Architecture. Add the term rules (component, boundary, service, layer) and the decoupling-mode mapping to the Architecture Model TXT (Draft 0.2, checklist Draft 0.10, QA 0.0650 and 0.0660).

#### Phase 120: Validation (not started, needs the user)

- [ ] Task 120.100: Validate the design against three contrasting architectures. Extra run 1 on specmgr (local tool) is done: `validation/specmgr/`, findings V-01 to V-10, QA 0.0340 and 0.0350 partly answered. The three classes of QA 0.0340 still need a system each.
- [ ] Task 120.110: Re-run the Structurizr probe from a committed location.

## Progress

### Current Status

**As of 2026-11-22**: Phase 100 and 110 are done and committed. ACC-004 is open until the open items are narrowed after Phase 120. The metamodel gaps of the review are closed (Task 110.150). Both diagrams render without errors with the PlantUML Docker image (ACC-003). Phase 120 has started: validation run 1 on specmgr (a local tool, an extra class) is done, with ten catalogue findings that are not yet applied. The three architecture classes of QA 0.0340 need one system each, chosen by the user. Open design points: the cells that differ from R+W Table 4-1 (QA 0.0640), and the decoupling-mode mapping of Architecture Model section 8.5, which is our interpretation. Clean Architecture is now a checked source for PR09 to PR12 (Task 110.140).

### Blockers

- Missing sources: ISO/IEC/IEEE 42030, ATAM report, COBIT 2019 framework, ISO/IEC 33020, TOGAF, ISO/IEC 25010:2023 original text. Cited by the principle and pattern tags, with no markdown copy: Saltzer and Schroeder, Release It!, Enterprise Integration Patterns, GoF, POSA (PDF files exist, QA 0.0660).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-22 16:30:00.000Z - Validation run 1: specmgr

C4 model of specmgr in `validation/specmgr/workspace.dsl` (Structurizr validate OK; inspect: no documentation and no decisions, expected, V-05). The validation record `validation/specmgr/validation-record.md` checks the C4 coverage of Architecture Model section 8.1, walks the 12 perspectives against the matrix, and applies five criteria of VP06 x RE. Ten findings V-01 to V-10. None is applied to the matrix or the texts before the other runs. specmgr is a fourth class (local tool), so it does not replace one of the three classes of QA 0.0340.

#### 2026-11-22 15:30:00.000Z - Metamodel gaps closed, Structurizr perspective test

Structurizr test (QA 0.0680): a perspective name is unique on an element, and a repeated property key is overwritten silently. Review results are now one perspective per criterion, named by the criterion ID. Diagram A: MatrixRow with Viewpoint and CrossView, CrossView spans the description, decision applies pattern and tactic. Diagram B: Element supertype, link to the 42010 View of diagram A. Both diagrams pass the structure-only check and render without errors with the `plantuml/plantuml` Docker image (run by the user, 2026-11-22). ACC-003 is checked.

#### 2026-11-22 14:27:37.000Z - Review corrections

Mechanical corrections after a review. REQ-003 uses the new name Resources (RS). ACC-001, ACC-002 and ACC-005 are checked. Checklist Draft 0.12: skill directory `.opencode/skill/`, ADR removed as an input type, RS wording aligned. Architecture Model Draft 0.4: RS wording aligned. QA 25bd5b93: 0.0540 marked as superseded in part by 0.0670, 0.0320 updated (`specmgr://iso29148` exists).

#### 2026-11-20 11:43:54.000Z - Perspective DR renamed to RS

DevelopmentResource (DR) is renamed to Resources (RS) and re-scoped to the full lifecycle (QA 0.0670, checklist Draft 0.11, Architecture Model Draft 0.3).

#### 2026-11-18 15:00:00.000Z - Clean Architecture added as a source

The book is now available as markdown. It was needed: the checklist listed it as "to be confirmed" for PR09 to PR12, and the Architecture Model did not use it. Checked PR09 to PR12 against the chapters. Corrected "ports and adapters" as an R+W example (it is not in R+W). Added the term rules for component, boundary, service and layer, the dependency-direction limit of C4 (section 3.4) and the decoupling-mode mapping (section 8.5, our interpretation). PR12 joins PR09 to PR11 in Development. The book is no source for viewpoints, perspectives or tactics. No viewpoint, perspective, matrix cell or criterion ID changed.

#### 2026-11-18 10:00:00.000Z - Created

Feature created from the consolidation plan. Issue #267 opened.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-18 15:00:00.000Z - Component means the C4 sense

Martin (ch. 12) uses "component" for a unit of deployment, and C4 (and Brown, ch. 34) for a grouping of functionality inside a container. The catalogue uses the C4 sense. Martin's sense is written "deployable unit". A criterion that uses PR10 or PR11 says which sense it means.

#### 2026-11-18 10:00:00.000Z - Viewpoint is not an artifact

A viewpoint is generic catalogue knowledge, so it becomes a resource plus skill. The models and views become the ARC artifact.

### Related PRs / Commits

- Issue #267. Downstream: #228, #250.
