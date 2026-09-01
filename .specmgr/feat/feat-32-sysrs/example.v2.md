<!--
DISCUSSION DRAFT — REV 2 of `example.md` — not a schema, not wired into
any tool/resource/model. `example.md` (REV 1, with your inline review
comments) is left untouched for comparison.

Purpose: give a concrete artifact to react to for Tasks 0.3.1/0.3.2
(finalizing the `sysrs` `## H2` section list and organizing principle
— see README.md → Task List). Sketches a tailored-not-verbatim
ISO/IEC/IEEE 29148 SyRS shape, informed by the domain-to-source mapping
table and MITRE SEG findings already captured in this feature's
README.md → Design Notes.

REV 2 changelog (applied from your inline comments on REV 1):

1. H1 title: resolved — mandatory, and constrained to a
   `System Specification: <free text>` prefix. Regex (fullmatch against
   the heading text, no `#` marker, same convention as `uc`'s
   `Extension N.`/`Step N:` and `sop`'s `Step N:` `@alias` regexes):

       ^System Specification: .+$

   (`.+` requires at least one character after `": "` so the title
   suffix can't be blank; matches how `sop/models/v1/body.py`'s
   `^Step \d+: .+$` is written.)
2. `## Overview`: resolved — mandatory, but *not* restricted to one
   paragraph; any markdown content is allowed (mirrors how
   `MarkdownSection2`-based sections elsewhere impose no paragraph-count
   limit of their own).
3. Dropped the bold pseudo-heading `**RelatedArtifacts:**` everywhere —
   replaced with a real `### <Name>` heading per section, named for
   what it holds (`### Goals`, `### Problems`, `### Scenarios`, ...)
   rather than a generic "Related Artifacts" label. Unlike `gol`'s own
   `## Related Artifacts` container (which wraps `### Requirements`/
   `### Decisions`/`### Goals`/`### Acceptance Criteria` all under one
   H2, since a goal's own H1 isn't already domain-specific), no extra
   wrapper H2 is needed here — every `sysrs` H2 below is already
   domain/concept-specific, so its `### <Name>` list sits directly
   under it. **Flagging for confirmation**: is dropping the wrapper
   intentional/correct, or did you want a `## Related Artifacts`
   container preserved for consistency with `gol`/`dec`?
4. Cross-reference entries: resolved shape (from your `Business Context
   and Goals` example) — a bullet holding *only* the id (no inline
   title, no inline paraphrase suffix), followed by a blank line and an
   indented "notes" paragraph carrying the paraphrase:

       - GOL-<uuid>

           Loose md list with paraphrased content.

   **Empirically verified against `models/md`**: this is *not* a new
   shape to build — it's exactly what `MarkdownListItemWithNotes`
   (`models/md/markdown_list_item.py`) already models (lead
   paragraph = the item's own marker + first line; `notes: list[
   MarkdownParagraph] | None` = the loose-list continuation
   paragraph(s)), and `gol`'s own `Tags` section already uses this same
   base class. So this satisfies ACC-003's "validated against the
   `models/md` engine" bar essentially for free.
   **Flagging for confirmation**: this *drops the inline title*
   that `gol`/`dec`'s existing `### Goals`/`### Requirements`/etc. lists
   use today (`"GOL-0007: <title>"`) — title becomes resolvable only by
   looking the id up (e.g. via `get_gol`), not visible in `sysrs`
   itself. Intentional (avoids duplicating/staleness-prone titles), or
   should the title still appear, e.g. as the notes paragraph's first
   line? Applied uniformly below to every domain's list, not just
   `Goals`, for consistency — flag if that generalization is wrong and
   some domains should keep an inline title.
5. Applied the REV-1 resolutions above to *every* section below, not
   only `Business Context and Goals`, since you didn't flag the other
   sections as different — shout if some of them need to diverge from
   this pattern (in particular `System Requirements`, which still has
   its own open categorization question below).

Everything else from REV 1 that you did not comment on is carried over
unchanged, including all inline `<!-- Q: ... -->` open questions still
outstanding (Business Context content sourcing, `qa` relevance, `req`
categorization grouping, `rsk` coordinate surfacing, Verification/
Systems Integration modeling options, Traceability need, HERMES
framing, per-domain vs. life-cycle-stage grouping).
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

- GOL-9f02d1aa-...

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
     requirements-elicitation interviews. -->

### Stakeholder Needs

- QA-77bc9d40-...

    Surfaces the top 5 pain points prioritized by the Partner
    Integration Team interview.

<!-- Q: is a `qa` reference even useful at the sysrs level, or is `qa`
     too far upstream / too raw to aggregate here? Could drop this
     section entirely and let `req`/`gol` absorb everything qa already
     fed into. -->

## Operational Concept and Scenarios

<!-- Mapping: 29148 OpsCon, endorsed by MITRE SEG via IEEE 1362-1998 —
     "scenarios of system use in the user's environment." -->

### Scenarios

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
     Checklist." -->

<!--
Q: does specmgr's `req` domain already carry a `category`/`type` field
   that maps onto Function/Performance/Fit/Form/Quality/Compliance? If
   not, do we (a) group the list below under `#### <Category>`
   sub-headings, (b) rely on each `req`'s own metadata and just list
   flatly (as drafted here), or (c) not attempt categorization at the
   sysrs level at all?
-->

### Requirements

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
     of the requirements above. -->

### Decisions

- ADR-5cd1e670-...

    Use an API gateway for key issuance and revocation — chosen to meet
    the sub-2s performance requirements above without duplicating logic
    per service.

- DEC-9e40f781-...

    Rate-limit key issuance per partner, not globally — operational
    decision, not architecture-level, kept in `dec` rather than a full
    ADR.

## Risks

<!-- Mapping: not a dedicated 29148 section, but INCOSE/MITRE both treat
     risk as a first-class SE artifact; specmgr already has `rsk`. -->

### Risks

- RSK-2210ee63-...

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

---

<!--
Overall open questions for discussion, beyond the inline ones above
(unchanged from REV 1, still open):

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
