<!--
DISCUSSION DRAFT — not a schema, not wired into any tool/resource/model.

Purpose: give a concrete artifact to react to for Task 0.3 (finalizing
the `sysrs` `## H2` section list). Sketches a tailored-not-verbatim
ISO/IEC/IEEE 29148 SyRS shape, informed by the domain-to-source mapping
table and MITRE SEG findings already captured in this feature's
README.md → Design Notes.

Every `RelatedArtifacts` bullet below uses the field shape candidate
from README.md REQ-003: `id`, `title`, and a short agent-paraphrase —
shown here as a plain-text suffix on the bullet (one of the two
candidate shapes under "Not yet decided"; the other candidate is a
distinct structured sub-field). Pick whichever you prefer, or propose a
third shape.

Open questions inline as `<!-- Q: ... -->` comments — please react to
each one directly.
-->

# System Specification: Example Widget Platform

<!--
Q: Working title placeholder only. Real documents would presumably
   reuse whatever "system name" convention exists elsewhere (none yet
   in specmgr) — flag if this needs its own frontmatter field.
-->

<!-- This H1 section is mandatory. Want to enforce prefix REGEX "^System Specification: <free text>"? make the correc tregex for this -->

## Overview

One-paragraph, human-authored summary of what this system is and why
this document exists. Not sourced from any other domain — free text,
mirroring how REQ/UC/etc. open with an unstructured intro.

<!-- Q: mandatory or optional H2? Every other domain has some kind of
     free-text lead-in, so leaning mandatory. -->

<!-- This is mandatory. But we will not restrict it to ONE paragraph. We want any markdown in this section. -->

## Business Context and Goals

Maps to 29148's BRS (business rationale) + INCOSE's mission framing.

**RelatedArtifacts:**

- `gol-4b1e...` — "Reduce onboarding time for new partner integrations"
  — paraphrase: *justifies the platform by tying it to a measurable
  business KPI, not a feature list.*
- `gol-9f02...` — "Consolidate three legacy billing systems"
  — paraphrase: *the existing-system-being-replaced rationale MITRE SEG's
  CONOPS article calls for.*

<!-- Q: `gol` only, or also pull in `prb` here since problem framing
     often sits right next to business rationale? Current mapping table
     puts `prb` in its own section below — open to merging them. -->

<!-- We want this structure:

NOTE: We DO NOT WANT a pseudo-heading "**Related Artifacts**".

### Business Context

I am not sure what we should write here. We probably do not have this information here available. Though I see that it is needed.

Therefore we want this section to be any markdown content. We can ask the user later for actual content and the agent can suggest content based on the GOALs. What do you think?

### Goals

This is a bullet list with at least one item. 

- GOL-<uuid>

    Loose md list with paraphrased content.

 -->

## Problem Statement

Maps to 29148/MITRE's "existing system being replaced, justification for
a new/modified system" CONOPS component; specmgr already has a
dedicated `prb` domain for this (Six-Sigma-style 5W2H), so referencing
rather than duplicating.

**RelatedArtifacts:**

- `prb-1a77...` — "Partner API onboarding takes 6+ weeks"
  — paraphrase: *quantifies the pain point the Business Context goals
  above respond to.*

## Stakeholder Needs and Elicitation

Maps to 29148's StRS (stakeholder requirements) via `qa`'s
requirements-elicitation interviews.

**RelatedArtifacts:**

- `qa-77bc...` — "Partner Integration Team interview"
  — paraphrase: *surfaces the top 5 pain points prioritized by the
  partner integration team.*

<!-- Q: is a `qa` reference even useful at the sysrs level, or is `qa`
     too far upstream / too raw to aggregate here? Could drop this
     section entirely and let `req`/`gol` absorb everything qa already
     fed into. -->

## Operational Concept and Scenarios

Maps to 29148's OpsCon, endorsed by MITRE SEG via IEEE 1362-1998 —
"scenarios of system use in the user's environment."

**RelatedArtifacts:**

- `uc-3391...` — "Partner registers and activates a new API key"
  — paraphrase: *the primary end-to-end scenario driving most of the
  functional requirements below.*
- `uc-88ab...` — "Support agent revokes a compromised API key"
  — paraphrase: *the exception-path scenario for the security
  requirements below.*

## System Requirements

Maps to 29148's SyRS core + INCOSE's requirement categorization
(Function/Performance, Fit/Operational, Form, Quality, Compliance) —
confirmed independently by MITRE SEG's "System-Level Requirements
Checklist."

<!--
Q: does specmgr's `req` domain already carry a `category`/`type` field
   that maps onto Function/Performance/Fit/Form/Quality/Compliance? If
   not, do we (a) group RelatedArtifacts under sub-headings here by
   category, (b) rely on each `req`'s own metadata and just list flatly,
   or (c) not attempt categorization at the sysrs level at all?
-->

**RelatedArtifacts:**

- `req-0021...` — "System shall issue an API key within 2s of
  registration submission" — paraphrase: *performance requirement
  traceable to uc-3391.*
- `req-0022...` — "System shall support revoking a key within 1s of
  agent action" — paraphrase: *performance requirement traceable to
  uc-88ab.*
- `req-0030...` — "System shall comply with OAuth 2.1" — paraphrase:
  *compliance requirement, no direct uc trace.*

## Architecture and Design Decisions

Maps to 29148's implicit "design constraints" plus specmgr's own
`dec`/`adr` domains — architecture/design choices made in service of
the requirements above.

**RelatedArtifacts:**

- `adr-5cd1...` — "Use API gateway for key issuance and revocation"
  — paraphrase: *chosen to meet the sub-2s performance requirements
  above without duplicating logic per service.*
- `dec-9e40...` — "Rate-limit key issuance per partner, not globally"
  — paraphrase: *operational decision, not architecture-level, kept in
  `dec` rather than a full ADR.*

## Risks

Maps to 29148's implicit risk handling (not a dedicated 29148 section,
but INCOSE/MITRE both treat risk as a first-class SE artifact); specmgr
already has `rsk`.

**RelatedArtifacts:**

- `rsk-2210...` — "Partner-side key leakage via insecure storage"
  — Initial: Probability 3 / Impact 4 (High); Residual: Probability 2 /
  Impact 4 (Medium) — Strategy: reduce — paraphrase: *mitigated by the
  revocation-within-1s requirement above, residual risk remains
  Medium.*

<!-- Q: worth surfacing the initial/residual probability-impact
     coordinates inline (as sketched above) so a reader gets the risk
     picture without opening rsk-2210, or is that already too close to
     "embedding full content" that REQ-003 explicitly wants to avoid? -->

## Verification and Test Planning

**No existing specmgr domain covers this today** — confirmed gap by
both INCOSE and MITRE SEG (Task 0.6 findings). Sketched here as free
text only, no `RelatedArtifacts` (nothing to reference yet):

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
   section already carries RelatedArtifacts pointing at its upstream
   source (uc -> req -> dec -> rsk)? Candidate options:
   (a) drop this section — traceability already lives implicitly in the
       per-section RelatedArtifacts lists above;
   (b) keep it as a single consolidated table/matrix view for readers
       who don't want to walk every section;
   (c) keep it, but only for chains that skip sections (e.g. a `req`
       with no traceable `uc`, flagged as a gap).
-->

## References

Free text / external links only (standards cited, external docs) —
mirrors 29148's own "5 References" section. Not a `RelatedArtifacts`
list since it points outside specmgr.

---

<!--
Overall open questions for discussion, beyond the inline ones above:

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
   stage pulling from whichever domains are relevant?
-->
