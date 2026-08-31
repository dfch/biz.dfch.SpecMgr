<!--
DISCUSSION DRAFT — REV 7 of `example.md` — not a schema, not wired into
any tool/resource/model. `example.md` (REV 1) through `example.v6.md`
(REV 6) are left untouched for comparison — each reviewed round gets
its own new numbered file, never edited in place.

Purpose: the concrete `## H2`/`### H3` section list for the `sysrs`
body (Task 0.3.2 / ACC-002 — APPROVED 2026-08-31, see below). REV 6
(hand-edited by the user)
is the structural base; REV 7 applies the decisions agreed 2026-08-31
without changing the structure, and adds a mandatory/optional flag +
content-type comment after every heading.

Approval (2026-08-31, user): ALL per-heading MANDATORY/OPTIONAL flags
approved as written (user-annotated "-- > OK" on each; normalized to
bare flags below), plus two new OPTIONAL free-form H2s added by the
user (`## Appendix`, `## Definitions and Acronyms`), and the two inline TODO
answers (under `## Requirements` and after `## Updates`). This file is
now the APPROVED section list — Task 0.3.2 done, ACC-002 satisfied.

REV 6 -> REV 7 changes:

1. All `(9.5.x)` clause numbers removed from the headings — they were
   traceability annotations only (decided 2026-08-31); the mapping to
   ISO/IEC/IEEE 29148:2018 §9.5 is recorded in the table below instead.
   Real `sysrs` documents carry bare section names.
2. The nine `## Requirements` H3s are now in canonical ISO/IEC
   25010:2023 product-quality model order (resolves REV 6's TODO):
   Functional Suitability, Performance Efficiency, Compatibility,
   Interaction Capability, Reliability, Security, Maintainability,
   Flexibility, Safety.
3. Remaining heading casing normalized to title case (e.g.
   "User characteristics" -> "User Characteristics").
4. A MANDATORY/OPTIONAL + content-type comment added after every
   heading — proposed in REV 7, all approved by the user 2026-08-31.
5. This header added (purpose, §9.5 mapping table, REQ placement
   rule, list rule).

REV 6 changes carried over as-is: H1 without the "(SyRS)" suffix;
`### System Integration` folded under `## System Overview` (no own H2);
the `## Other Quality Requirements` umbrella renamed to `## Other
Characteristics`; "Interaction Capabilities" corrected to "Interaction
Capability"; `## References` restored after `## Verification`.

29148 §9.5 -> sysrs section mapping (29148's own clause order is
deliberately not followed for the first sections: the BRS/StRS content
borrowed into this document sits up front, and §9.5.19's assumptions
are read before the requirements they qualify — 29148 §9.5.1
explicitly allows the order/section structure to vary per project
policy):

| 29148 clause | sysrs section |
|---|---|
| 9.5.2 System purpose | ## System Purpose |
| 9.5.3 System scope | ## System Scope |
| 9.5.4.1 System context | ### System Context |
| 9.5.4.2 System functions | ### System Functions |
| 9.5.4.3 User characteristics | ### User Characteristics |
| 9.5.5 Functional requirements | ## Requirements -> ### Functional Suitability |
| 9.5.6 Usability requirements | ### Interaction Capability |
| 9.5.7 Performance requirements | ### Performance Efficiency |
| 9.5.8 System interface requirements | ### Compatibility (Interoperability sub-characteristic) |
| 9.5.9.1 Human system integration | ### Interaction Capability |
| 9.5.9.2 Maintainability requirements | ### Maintainability |
| 9.5.9.3 Reliability requirements | ### Reliability |
| 9.5.9.4 Other quality requirements | absorbed into ### Compatibility / ### Flexibility |
| 9.5.10 System modes and states | ## System Modes and States |
| 9.5.11 Physical characteristics | ### Physical Characteristics |
| 9.5.12 Environmental conditions | ### Environmental Conditions |
| 9.5.13 System security requirements | ### Security |
| 9.5.14 Information management requirements | ### Information Management |
| 9.5.15 Policy and regulation requirements | ### Policy and Regulation |
| 9.5.16 System life cycle sustainment requirements | ### System Life Cycle Sustainment |
| 9.5.17 Packaging, handling, shipping and transportation requirements | ### Packaging, Handling, Shipping and Transportation |
| 9.5.18 Verification | ## Verification |
| 9.5.19 Assumptions and dependencies | ## Assumptions and Dependencies |

Borrowed from BRS (§9.3) / StRS (§9.4), per this feature's intent to
fold them into the SyRS: `## Business Context and Goals` (BRS 9.3.2
purpose / 9.3.7 mission-goals-objectives; StRS 9.4.2/9.4.7),
`## Stakeholder Needs and Elicitation` (StRS 9.4.5 stakeholders /
9.4.15 user requirements), `## Operational Concept and Scenarios`
(StRS 9.4.16/9.4.17; 29148 §5.4 ConOps/OpsCon + Annex A).

Not 29148 §9.5 sections (specmgr/INCOSE/MITRE additions): `## Decisions`,
`## Risks`, `### System Integration`, `## References`, `## More
Information`, `## Appendix`, `## Definitions and Acronyms`, `## Updates`.

REQ placement rule (no change to the shipped `req` domain): a REQ
bullet under `## Requirements` or `## Other Characteristics` is placed
under the H3 named by the FIRST item of the REQ's own `##
Characteristics` section (the `req` schema mandates at least one item;
the list is free text, max 9). Placement vocabulary = the nine
canonical ISO/IEC 25010:2023 characteristic names + the six
Other-Characteristics clause names (Physical characteristics,
Environmental conditions, Information management, Policy and
regulation, System life cycle sustainment, Packaging, handling,
shipping and transportation). Matching is case-insensitive exact match;
near-names are resolved by the agent (e.g. "Performance" -> Performance
Efficiency, "Usability"/"User Interaction" -> Interaction Capability,
"Portability" -> Flexibility — the 25010:2023 rename). Convention only,
not enforced by any schema (decided 2026-08-31: we live with that and
hope the agent will handle it). Note: the `req` docstring's example
list predates the 2023 rename — optional future cleanup, out of scope.

List rule (decided 2026-08-31): every OPTIONAL section whose content is
a cross-reference list (GOL/PRB/QA/UC/DEC/ADR/RSK/REQ/VCR) must carry
at least 1 item when present.
-->

# System Requirements Specification: Example Widget Platform

<!-- Mandated H1 prefix: ^System Requirements Specification: .+$
     (supersedes REV 2's '^System Specification: .+$', decided
     2026-08-31). -->

## System Purpose

<!-- MANDATORY. Free text. The reason the system is being
     developed or modified (29148 §9.5.2). Also serves as the
     document's lead-in, replacing REV 1-5's separate ## Overview
     (dropped by decision, 2026-08-31). -->

## System Scope

<!-- MANDATORY. Free text. What the system will and will not
     do; results of the earlier needs analysis (29148 §9.5.3). -->

## Business Context and Goals

<!-- MANDATORY. Umbrella for the BRS/StRS content borrowed
     into this document (BRS 9.3.2/9.3.7; StRS 9.4.2/9.4.7). -->

### Business Context

<!-- OPTIONAL. Free text, no fixed template. May not exist at
     creation time; the agent can suggest a draft derived from the
     linked Goals (REV 5 open point, still standing). -->

### Goals

<!-- MANDATORY, at least 1 item. Cross-reference list to
     `gol` (GOL <uuid>: <title> + one-line paraphrase, REQ-003 shape). -->

### Problem Statement

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `prb` — not every system has a formal problem statement. -->

## Stakeholder Needs and Elicitation

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `qa` (StRS 9.4.5/9.4.15). Elicitation artifacts may not
     exist yet at first drafting. -->

## Operational Concept and Scenarios

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `uc` (StRS 9.4.16/9.4.17; ConOps/OpsCon §5.4/Annex A). -->

## Decisions

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `dec`/`adr` — architecture/design choices made in service
     of the requirements below. No 29148 clause (specmgr addition). -->

## Risks

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `rsk`. INCOSE/MITRE treat risk as first-class — consider
     MANDATORY. No 29148 clause. -->

## Assumptions and Dependencies

<!-- OPTIONAL. Free text (list). Assumptions/dependencies to
     take into account when allocating and deriving lower-level
     requirements (29148 §9.5.19). Placed up front by REV 6 (deliberate
     deviation from clause order; the standard allows it). -->

## System Overview

<!-- MANDATORY. Umbrella for the system's context, functions,
     users, and integration (29148 §9.5.4). -->

### System Context

<!-- MANDATORY. Free text (diagram recommended). Major
     elements incl. human elements and all significant interfaces
     crossing the system boundary (29148 §9.5.4.1). -->

### System Functions

<!-- MANDATORY. Free text. Major system capabilities,
     conditions, constraints (29148 §9.5.4.2). -->

### User Characteristics

<!-- OPTIONAL. Free text. Roles / user-operator-maintainer
     classes, numbers, nature of use (29148 §9.5.4.3; REV 6's "Roles"
     hint). -->

### System Integration

<!-- OPTIONAL. Free text. Integration sequence/dependencies
     across subsystems, interface control points. No 29148 clause;
     REV 5's ## Systems Integration content, folded under System
     Overview by REV 6 (closes Task 0.3.4). -->

## System Modes and States

<!-- OPTIONAL. Free text. The standard itself is
     conditional: "if the system can exist in various operational modes
     or states, define these" (29148 §9.5.10). -->

## Requirements

<!-- MANDATORY (section), with at least one of the nine H3s
     present. The document's reason for existing. The nine H3s are the
     ISO/IEC 25010:2023 product-quality characteristics in canonical
     model order; each is a cross-reference list to `req`, grouped by
     the REQ's first `## Characteristics` item (placement rule, header
     above). 29148's per-subclause requirement categories (§9.5.5-
     9.5.9) are replaced by this scheme; §9.5.8 (interfaces) lands in
     Compatibility. -->

<!-- ANSWER (2026-08-31) — exact format of a single REQ cross-reference
     (same shape as every other cross-reference list in this document;
     Decisions Made 2026-08-31, `<TYPE> <uuid>: <title>` + notes):

       - REQ 64265c7a-144c-46d5-9bd7-13750254bc54: API Key Issuance Latency

         System shall issue an API key within 2 s of registration
         acceptance; drives scenario UC 88ed67cd-0b3b-4846-a827-530c12695936.

     Bullet line: `- REQ ` + the req document's full UUID (8-4-4-4-12)
     + `: ` + the req's H1 title verbatim. The indented notes paragraph
     (the `MarkdownListItemWithNotes` shape) carries a one-line
     agent-generated paraphrase (REQ-003) — optional per bullet, but
     recommended. The bullet sits under the H3 named by the req's FIRST
     `## Characteristics` item (placement rule, header above). A bare
     bullet without notes is also valid:

       - REQ b19c5446-4e11-466e-b517-7763c586f63e: OAuth 2.1 Compliance

     The UUID/title must match the referenced req document; like every
     other domain's cross-references today, the reference is text in
     v1 — live validation comes with the Phase 1+ tooling. -->

### Functional Suitability

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.5 functional). -->

### Performance Efficiency

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.7). -->

### Compatibility

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.8 interfaces -> Interoperability;
     §9.5.9.4 other quality). -->

### Interaction Capability

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.6 usability; §9.5.9.1 human system
     integration). -->

### Reliability

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.9.3). -->

### Security

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.13). -->

### Maintainability

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.9.2). -->

### Flexibility

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.9.4; the 25010:2023 rename of
     Portability). -->

### Safety

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (no 29148 §9.5 clause; 25010:2023 addition). -->

## Other Characteristics

<!-- OPTIONAL (whole umbrella; omit if none of the six apply,
     e.g. no packaging for cloud-hosted software). Umbrella for 29148
     §9.5.11-9.5.17 — the requirement categories that are NOT 25010
     characteristics (REV 6 name; not the §9.5.9.4 clause itself — that
     one is absorbed into Compatibility/Flexibility above). Each H3 is
     a REQ cross-reference list. -->

### Physical Characteristics

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.11). -->

### Environmental Conditions

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.12). -->

### Information Management

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.14). -->

### Policy and Regulation

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.15). -->

### System Life Cycle Sustainment

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.16). -->

### Packaging, Handling, Shipping and Transportation

<!-- OPTIONAL, at least 1 item when present. REQ cross-
     reference list (29148 §9.5.17). -->

## Verification

<!-- OPTIONAL, at least 1 item when present. Cross-reference
     list to `vcr` (Verification Case Records; REV 6's hint). 29148
     §9.5.18 wants verification given in parallel with the requirements
     above; `vcr` is fully shipped (on dev since 2026-08-31), so the
     references can be validated. An early document may legitimately
     have no VCRs yet. -->

## References

<!-- OPTIONAL. Free-form bullet list of external standards/
     documents (no specmgr ids) — mirrors 29148's own "5 References".
     Restored by REV 6. -->

## More Information

<!-- OPTIONAL. Free-form supplementary text, no fixed format
     — mirrors `dec`/`vcr`'s own ## More Information (REV 5 decision). -->

## Appendix

<!-- OPTIONAL. Free-form text. Supplementary material that does not
     belong in any other section — e.g. large diagrams, worked
     examples, extended interface descriptions. No 29148 clause (user
     addition, 2026-08-31). -->

## Definitions and Acronyms

<!-- OPTIONAL. Free-form text. List of abbreviations used in this
     document (e.g. KIS, SLA, KMS). No 29148 clause (user addition,
     2026-08-31); whether/how ISO_24765 grounds it is Task 0.11 (still
     open, non-blocking — the section is free-form either way). -->

## Updates

<!-- OPTIONAL, last section when present. H3 entries with
     free-form, date-led titles — mirrors DEC's/VCR's
     Updates/UpdateEntry shape, not `feat`'s enforced variant (REV 5
     decision). -->

<!-- ANSWER (2026-08-31, about ## Updates): `## Updates` is a change
     log for THIS specification document — it records revisions to the
     sysrs itself, not changes to the system it specifies. Each entry
     is an H3 with a free-form, date-led title
     (`### YYYY-MM-DD — <short description>`; date-led is convention,
     not regex-enforced — mirrors DEC's/VCR's UpdateEntry, which has
     no ordering validator). The body is free-form prose: what changed
     and why. Recommended convention: newest first. Filled in, it
     looks like:

       ### 2026-09-14 — Added Security requirements

       Two Security requirements added (see ### Security below) after
       the partner security review flagged unencrypted key storage;
       System Context diagram updated to show the KMS boundary.

       ### 2026-08-30 — Initial draft created

       Initial system specification drafted from the linked
       Goals/Problem Statement/Scenarios; no Requirements or Decisions
       cross-referenced yet. -->
