<!--
DISCUSSION DRAFT — REV 3 of `example.md` — not a schema, not wired into
any tool/resource/model. `example.md` (REV 1) and `example.v2.md`
(REV 2) are left untouched for comparison — each reviewed round gets
its own new numbered file, never edited in place.

Purpose: give a concrete artifact to react to for Tasks 0.3.1/0.3.2
(finalizing the `sysrs` `## H2` section list and organizing principle
— see README.md → Task List). Sketches a tailored-not-verbatim
ISO/IEC/IEEE 29148 SyRS shape, informed by the domain-to-source mapping
table and MITRE SEG findings already captured in this feature's
README.md → Design Notes.

REV 3 changelog (applied from your review of REV 2):

1. **Drop the `### <Name>` sub-heading when an H2 holds exactly one
   cross-reference list.** REV 2 applied "every list gets a named H3"
   uniformly to every section, which produced redundant headings where
   the H3's name just repeated the H2's own name
   (`## Architecture and Design Decisions` → `### Decisions`,
   `## Risks` → `### Risks`) or added nothing beyond it
   (`## Stakeholder Needs and Elicitation` → `### Stakeholder Needs`,
   `## Operational Concept and Scenarios` → `### Scenarios`,
   `## System Requirements` → `### Requirements`). In REV 3 those five
   sections have the list directly under the H2, no sub-heading. The
   H3 sub-heading rule is now kept **only** where an H2 genuinely holds
   more than one distinct list or a mix of free text and a list — today
   that's just `## Business Context and Goals`, which keeps its three
   H3s (`### Business Context`, `### Goals`, `### Problem Statement`)
   since those really are three different things a reader needs to tell
   apart.
2. No other content changes from REV 2 — all REV 2 changelog items
   (H1 title regex, mandatory-unrestricted `## Overview`, no bold
   pseudo-heading, id-only cross-reference bullet + notes-paragraph
   shape) and all inline `<!-- Q: ... -->` open questions carry over
   unchanged.
-->

# System Specification: Example Widget Platform

<!-- Q: working title placeholder only. Real documents would presumably
     reuse whatever "system name" convention exists elsewhere (none yet
     in specmgr) — flag if this needs its own frontmatter field. -->

## Overview

One-paragraph, human-authored summary of what this system is and why
this document exists. Not sourced from any other domain — free text,
mirroring how REQ/UC/etc. open with an unstructured intro. Mandatory;
any markdown content is allowed, not limited to a single paragraph.

## Business Context and Goals

<!-- Mapping: 29148 BRS (business rationale) + INCOSE mission framing. -->

### Business Context

<!-- Q: we probably won't have this content available up front when a
     `sysrs` is first created — there's no domain that stores "business
     context" prose directly. Proposal: leave this as free markdown with
     no fixed template; the agent can suggest a draft derived from the
     linked Goals below, but a human should confirm/edit it. Agree, or
     should this instead just be omitted when empty rather than drafted
     speculatively? -->

_(free markdown — no fixed template)_

### Goals

<!-- Bullet list, at least one item. -->

- GOL-4b1e2c9a-... + title

    Ties the platform to a measurable business KPI: reduces onboarding
    time for new partner integrations from 6+ weeks to under 1 week.

- GOL-9f02d1aa-... + title

    Justifies replacing three legacy billing systems with one
    consolidated platform — the "existing system being replaced"
    rationale MITRE SEG's CONOPS article calls for.

<!-- Q: `gol` only, or also pull in `prb` here since problem framing
     often sits right next to business rationale? Current mapping table
     puts `prb` in its own section below — open to merging them. -->
<!-- Yes, we will have "Problem STatement" as H3 -->

### Problem Statement

<!-- Mapping: 29148/MITRE's "existing system being replaced,
     justification for a new/modified system" CONOPS component; specmgr
     already has a dedicated `prb` domain for this (Six-Sigma-style
     5W2H), so referencing rather than duplicating. -->

- PRB-1a77f3e0-... + title

    Quantifies the pain point the Business Context goals above respond
    to: partner API onboarding takes 6+ weeks.

## Stakeholder Needs and Elicitation

<!-- Mapping: 29148 StRS (stakeholder requirements) via `qa`'s
     requirements-elicitation interviews. Single list — no `### <Name>`
     sub-heading needed (REV 3 changelog item 1). -->

- QA-77bc9d40-... + title

    Surfaces the top 5 pain points prioritized by the Partner
    Integration Team interview.

<!-- Q: is a `qa` reference even useful at the sysrs level, or is `qa`
     too far upstream / too raw to aggregate here? Could drop this
     section entirely and let `req`/`gol` absorb everything qa already
     fed into. -->

## Operational Concept and Scenarios

<!-- Mapping: 29148 OpsCon, endorsed by MITRE SEG via IEEE 1362-1998 —
     "scenarios of system use in the user's environment." Single list —
     no `### <Name>` sub-heading needed (REV 3 changelog item 1). -->

- UC-3391aa10-...

    The primary end-to-end scenario driving most of the functional
    requirements below: partner registers and activates a new API key.

- UC-88ab5f21-...

    The exception-path scenario for the security requirements below:
    support agent revokes a compromised API key.

## System Requirements

<!-- Mapping: 29148 SyRS core + INCOSE's requirement categorization
     (Function/Performance, Fit/Operational, Form, Quality, Compliance)
     — confirmed independently by MITRE SEG's "System-Level Requirements
     Checklist." Single list — no `### <Name>` sub-heading needed
     (REV 3 changelog item 1). -->

<!--
Q: does specmgr's `req` domain already carry a `category`/`type` field
   that maps onto Function/Performance/Fit/Form/Quality/Compliance? If
   not, do we (a) group the list below under `#### <Category>`
   sub-headings, (b) rely on each `req`'s own metadata and just list
   flatly (as drafted here), or (c) not attempt categorization at the
   sysrs level at all?
-->

- REQ-0021bb30-...

    Performance requirement traceable to UC-3391aa10: system shall
    issue an API key within 2s of registration submission.

- REQ-0022cc41-...

    Performance requirement traceable to UC-88ab5f21: system shall
    support revoking a key within 1s of agent action.

- REQ-0030dd52-...

    Compliance requirement, no direct scenario trace: system shall
    comply with OAuth 2.1.

## Architecture and Design Decisions

<!-- Mapping: 29148's implicit "design constraints" plus specmgr's own
     `dec`/`adr` domains — architecture/design choices made in service
     of the requirements above. Single list — no `### <Name>`
     sub-heading needed (REV 3 changelog item 1); REV 2 had a `###
     Decisions` heading here that just repeated the H2's own name. -->

<!-- We will phase out ADR at a later point. So we only have DEC left. Use only DEC in the examples. -->

- DEC-5cd1e670-... + title

    Use an API gateway for key issuance and revocation — chosen to meet
    the sub-2s performance requirements above without duplicating logic
    per service.

- DEC-9e40f781-... + title

    Rate-limit key issuance per partner, not globally — operational
    decision, not architecture-level, kept in `dec` rather than a full
    ADR.

## Risks

<!-- Mapping: not a dedicated 29148 section, but INCOSE/MITRE both treat
     risk as a first-class SE artifact; specmgr already has `rsk`.
     Single list — no `### <Name>` sub-heading needed (REV 3 changelog
     item 1). -->

- RSK-2210ee63-... + title

    Partner-side key leakage via insecure storage. Initial: Probability
    3 / Impact 4 (High); mitigated by the revocation-within-1s
    requirement above; Residual: Probability 2 / Impact 4 (Medium) —
    Strategy: reduce.

<!-- Q: the initial/residual probability-impact coordinates and
     strategy are now folded into the notes paragraph's prose (as
     above) rather than a separate inline suffix — does that reads
     clearly enough, or is structured/tabular data like this a case
     where an inline suffix (or even a small embedded table) would be
     clearer than prose despite REQ-003's "no full-content embedding"
     preference? -->

## Verification and Test Planning

**No existing specmgr domain covers this today** — confirmed gap by
both INCOSE and MITRE SEG (Task 0.6 findings). Sketched here as free
text only, no cross-reference list (nothing to reference yet):

> Draft placeholder: verification approach per requirement (test /
> analysis / inspection / demonstration), acceptance thresholds,
> environment needed. 29148 gives this its own top-level "3
> Verification" section, 1:1 traceable to "2 Requirements" —
> MIL-STD-961E does the same ("4 Verification", 1:1 traceable to "3
> Requirements").

<!--
Q: three options on the table —
   (a) keep as a free-text `## H2` in sysrs now (no cross-refs, just
       prose), revisit modeling it as its own domain later;
   (b) omit entirely from sysrs v1, defer until/if a `ver`-style domain
       exists;
   (c) treat it as in-scope for a future domain now, and stub the
       section as "not yet available" rather than writing prose.
   README currently leans toward (a) but this is exactly the kind of
   call that should be locked down in this discussion.
-->

## Systems Integration

Same status as Verification above — MITRE SEG names it as a distinct
life-cycle stage, no specmgr domain exists.

> Draft placeholder: integration sequence/dependencies across
> subsystems, interface control points.

<!-- Q: same three options as Verification above — keep as free text,
     omit, or stub as "not yet available"? Could also decide
     Verification and Systems Integration get different answers from
     each other rather than a single blanket choice. -->

## Traceability

Not a 29148 section by that name, but INCOSE/MITRE SEG both call out
bidirectional traceability (needs → requirements → design →
verification) as a first-class artifact, not just an implicit property
of the other sections' cross-references.

<!--
Q: is a dedicated `## Traceability` section even needed if every other
   section already carries a cross-reference list pointing at its
   upstream source (uc -> req -> dec -> rsk, now via the notes-paragraph
   prose rather than a formal field)? Candidate options:
   (a) drop this section — traceability already lives implicitly in the
       per-section lists above;
   (b) keep it as a single consolidated table/matrix view for readers
       who don't want to walk every section;
   (c) keep it, but only for chains that skip sections (e.g. a `req`
       with no traceable `uc`, flagged as a gap).
-->

## References

Free text / external links only (standards cited, external docs) —
mirrors 29148's own "5 References" section. Not a cross-reference list
since it points outside specmgr.

<!-- We want a loose bullet list of references. See FEAT. -->

---

<!--
Overall open questions for discussion, beyond the inline ones above
(unchanged from REV 1/REV 2, still open):

1. Section count/order above (11 H2s incl. Overview/References) is
   deliberately generous — which of these merge, split, become
   optional-only, or get cut entirely?
2. Should every section be present-but-empty when no artifacts exist
   yet (like REQ/UC do), or should absent sections omit their heading
   entirely (like ADR's optional sections)?
3. Is per-domain grouping (one H2 per source domain, as drafted) the
   right shape, or should sysrs instead group by SE life-cycle stage
   (Concept Development / Requirements Engineering / Architecture /
   Design / Integration / Test) per MITRE SEG's process view, with each
   stage pulling from whichever domains are relevant? (This is now
   tracked as Task 0.3.1, a prerequisite for the rest.)
-->

## More Information

<!-- We need a free text section like we already have for other artifact types. -->

## Updates

<!-- We need an updates section. Newest first. See "FEAT" artifact type for sub-sections. -->

### yyyy-MM-dd HH:mm:ss.fff+hh:mm Title ...

<!-- Free text -->
