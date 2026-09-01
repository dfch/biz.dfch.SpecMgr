<!--
DISCUSSION DRAFT — REV 5 of `example.md` — not a schema, not wired into
any tool/resource/model. `example.md` (REV 1) through `example.v4.md`
(REV 4) are left untouched for comparison — each reviewed round gets its
own new numbered file, never edited in place.

Purpose: give a concrete artifact to react to for Tasks 0.3.1/0.3.2
(finalizing the `sysrs` `## H2` section list and organizing principle
— see README.md → Task List). Sketches a tailored-not-verbatim
ISO/IEC/IEEE 29148 SyRS shape, informed by the domain-to-source mapping
table and MITRE SEG findings already captured in this feature's
README.md → Design Notes.

REV 5 changelog (a cross-check pass against the now-locally-available
full ISO/IEC/IEEE 29148:2018 text (`ISO_29148.md`) and the sibling
`feat-33-vcr` (Verification Case Record) domain, which shipped its
Phase 1 models/parser concurrently with this draft — see
`.specmgr/feat/feat-33-vcr/README.md`):

1. **Cross-reference ids switched to `vcr`'s now-settled real-id shape,
   and every bullet finally shows an actual title.** REV 4 wrote
   hyphenated, truncated pseudo-ids (`GOL-4b1e2c9a-...`) and, despite its
   own changelog claiming "every cross-reference bullet ... carries `+
   title`," every single bullet across the whole document literally
   spelled out the four characters `+ title` as dead placeholder text
   instead of an actual title — a bug in the draft, not a demonstrated
   shape. `feat-33-vcr`'s `## Verifies` field settled on
   `"REQ|UC <uuid>: <title>"` (type tag, space, a real 8-4-4-4-12 hex
   UUID, colon, title) after an explore-agent audit found the
   `gol`/`dec`-style `GOL-0007`-ish codes are illustrative-only,
   structurally unenforced text with no real meaning (real ids are bare
   UUIDs). Every cross-reference bullet below now uses that same
   `<TYPE> <uuid>: <title>` shape, with a real (if fictional) title
   filled in — closing REQ-003's still-open "exact field shape" question
   using precedent that didn't exist when REV 1-4 were drafted.
2. **`## Verification and Test Planning` replaced by `## Verification`,
   now a cross-reference list to `vcr`.** `feat-33-vcr` exists
   specifically to fill this gap (its own README: "Fills a gap identified
   during `feat-32-sysrs` planning ... no existing specmgr domain models
   ISO/IEC/IEEE 29148's ... 'Verification/Test and Evaluation' concept,"
   and lists this feature as a dependent it blocks) and its Phase 1
   (models + parser) is already complete. `## Verification` is now shaped
   exactly like every other cross-reference-only section — single list,
   no `### <Name>` sub-heading — closing Task 0.3.3's three-way open
   question in favor of option (a)-turned-real-domain rather than a
   permanent free-text stand-in. `## Systems Integration` is unaffected —
   no domain covers it, so it stays a free-text placeholder with its
   three options still open (Task 0.3.4).
3. **`## Updates` now mirrors DEC's/VCR's actual shipped shape, not
   `feat`'s.** REV 1-4 asserted `## Updates` "reuses `feat.Updates`/
   `feat.UpdateEntry` ... exactly": a *mandatory*, `field_validator`-
   regex-enforced `{ISO8601 date+time+millis+offset} — {title}` heading
   with a newest-first `model_validator`. Reading the actual code showed
   two things: (a) literal reuse is impossible anyway — `feat`'s classes
   are `MarkdownSection3WithComment`/`MarkdownSection4`, not the
   `MarkdownSection2WithComment`/`MarkdownSection3` shape an H2-level
   `## Updates` needs; (b) `dec/models/v1/body.py` (already shipped, and
   already at the right H2/H3 level) uses a **free-form-title**
   `UpdateEntry` (`@alias(value=".+")`, no timestamp regex, no ordering
   check) and makes `Updates` **optional as a whole**, and
   `feat-33-vcr` — built concurrently, at the exact same H2/H3 nesting
   sysrs needs — explicitly evaluated this and followed DEC's shape, not
   `feat`'s ("Mirrors DEC's `UpdateEntry` shape," `vcr/models/v1/
   body.py:313`). `## Updates` below now uses a free-form, date-led
   (convention, not enforced) heading and is treated as optional, for
   consistency with both the existing and in-flight sibling domains at
   this heading level.
4. **New inline open questions, informed by reading the primary sources
   directly:**
   - `## System Requirements`'s categorization question now also
     references ISO/IEC/IEEE 29148 §9.5's own much richer 19-subclause
     requirement-category taxonomy (functional, usability, performance,
     interface, operations, modes/states, physical, environmental,
     security, information management, policy/regulation, life-cycle
     sustainment, packaging, verification, assumptions/dependencies) —
     a different, more granular scheme than INCOSE's five-word
     "function, fit, form, quality, and compliance," and one this
     feature's Design Notes had not directly cross-checked before REV 5
     (the previously recorded 29148 SyRS outline summary did not match
     §9.5's actual content once the full standard text became available
     locally — see README Task List, new Task 0.10).
   - `## Traceability`'s options now cite ISO/IEC/IEEE 29148's own
     "Requirements Traceability Matrix" (RTM) as a named, standard
     concept (confirmed at §6.4.3 and elsewhere in `ISO_29148.md`), not
     just an implicit property of per-section cross-reference lists —
     concrete grounding for option (b) below.
5. No other content changes from REV 4 — all REV 2/REV 3/REV 4 changelog
   items (H1 title regex, mandatory-unrestricted `## Overview`, no bold
   pseudo-heading, dropped redundant single-list H3s, the
   `## References`/`## More Information` additions) carry over unchanged.
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

<!-- Mapping: 29148 BRS (§9.3, business rationale) + INCOSE mission
     framing. Note: §9.3's actual normative content is far richer than
     the three H3s below (major stakeholders, business environment,
     business model, information environment, business processes,
     operational policies/modes/quality, business structure, high-level
     operational concept/scenarios, project constraints, ...) —
     deliberately tailored down, not an oversight; flag if any of that
     detail should surface here instead of staying implicit. -->

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

- GOL 0e15c5de-4ac9-4279-aa75-53249a3e43e4: Reduce Partner Integration Onboarding Time

  Ties the platform to a measurable business KPI: reduces onboarding
  time for new partner integrations from 6+ weeks to under 1 week.

- GOL 6761c7d8-59b9-4589-a2b2-0596ea460d61: Consolidate Legacy Billing Systems

  Justifies replacing three legacy billing systems with one
  consolidated platform — the "existing system being replaced"
  rationale MITRE SEG's CONOPS article calls for.

<!-- Q: `gol` only, or also pull in `prb` here since problem framing
     often sits right next to business rationale? Current mapping table
     puts `prb` in its own section below — open to merging them. -->

<!-- Yes, we will have "Problem Statement" as H3 -->

### Problem Statement

<!-- Mapping: 29148/MITRE's "existing system being replaced,
     justification for a new/modified system" CONOPS component; specmgr
     already has a dedicated `prb` domain for this (Six-Sigma-style
     5W2H), so referencing rather than duplicating. -->

- PRB 7166b565-ddb2-4a91-924c-d36d0e02d7aa: Partner API Onboarding Takes Too Long

  Quantifies the pain point the Business Context goals above respond
  to: partner API onboarding takes 6+ weeks.

## Stakeholder Needs and Elicitation

<!-- Mapping: 29148 StRS (§9.4) via `qa`'s requirements-elicitation
     interviews. Single list — no `### <Name>` sub-heading needed. -->

- QA c79bc330-6795-4dd3-9b79-c0936d4ae7f9: Partner Integration Team Requirements Interview

  Surfaces the top 5 pain points prioritized by the Partner
  Integration Team interview.

<!-- Q: is a `qa` reference even useful at the sysrs level, or is `qa`
     too far upstream / too raw to aggregate here? Could drop this
     section entirely and let `req`/`gol` absorb everything qa already
     fed into. (No existing specmgr domain cross-references `qa` today —
     checked `gol`/`req`/`dec`'s shipped examples — so there is no
     codebase precedent to lean on either way; this is a genuinely novel
     call.) -->

## Operational Concept and Scenarios

<!-- Mapping: 29148 ConOps/OpsCon (§5.4, Annex A/B), endorsed by MITRE
     SEG via IEEE 1362-1998 — "scenarios of system use in the user's
     environment." Note: 29148's own StRS content clause (§9.4.16/
     9.4.17, "Operational concept"/"Operational scenarios") already
     overlaps with the dedicated ConOps/OpsCon annexes — that redundancy
     is inherent to the standard itself, not introduced by folding both
     into `uc` here. Single list — no `### <Name>` sub-heading needed. -->

- UC 88ed67cd-0b3b-4846-a827-530c12695936: Partner Registers and Activates a New API Key

  The primary end-to-end scenario driving most of the functional
  requirements below: partner registers and activates a new API key.

- UC b3b37a97-36ca-41c1-9545-2355f5d07c31: Support Agent Revokes a Compromised API Key

  The exception-path scenario for the security requirements below:
  support agent revokes a compromised API key.

## System Requirements

<!-- Mapping: 29148 SyRS core (§9.5) + INCOSE's requirement
     categorization (Function/Performance, Fit/Operational, Form,
     Quality, Compliance) — confirmed independently by MITRE SEG's
     "System-Level Requirements Checklist." Single list — no
     `### <Name>` sub-heading needed. -->

<!--
Q: does specmgr's `req` domain already carry a `category`/`type` field
   that maps onto Function/Performance/Fit/Form/Quality/Compliance? If
   not, do we (a) group the list below under `#### <Category>`
   sub-headings, (b) rely on each `req`'s own metadata and just list
   flatly (as drafted here), or (c) not attempt categorization at the
   sysrs level at all? Also note ISO/IEC/IEEE 29148 §9.5 itself defines
   a different, more granular 19-subclause requirement-category scheme
   (functional/usability/performance/interface/operations/modes/
   physical/environmental/security/information-management/policy/
   sustainment/packaging/verification/assumptions) than INCOSE's
   five-word scheme above — worth deciding whether either, both, or
   neither should drive grouping here (see README Task List, new
   Task 0.10).
-->

- REQ 64265c7a-144c-46d5-9bd7-13750254bc54: API Key Issuance Latency

  Performance requirement traceable to UC 88ed67cd-0b3b-4846-a827-530c12695936:
  system shall issue an API key within 2s of registration submission.

- REQ 779b8275-beb8-4428-9e90-962929a42af7: API Key Revocation Latency

  Performance requirement traceable to UC b3b37a97-36ca-41c1-9545-2355f5d07c31:
  system shall support revoking a key within 1s of agent action.

- REQ b19c5446-4e11-466e-b517-7763c586f63e: OAuth 2.1 Compliance

  Compliance requirement, no direct scenario trace: system shall
  comply with OAuth 2.1.

## Architecture and Design Decisions

<!-- Mapping: 29148's implicit "design constraints" plus specmgr's own
     `dec`/`adr` domains — architecture/design choices made in service
     of the requirements above. Single list — no `### <Name>`
     sub-heading needed. -->

<!-- This section's own example entries below are deliberately `dec`-only
     (not `adr`), as an illustration convention for this discussion
     draft — real `sysrs` documents may still cross-reference either
     `dec` or `adr` ids; no decision has been made to deprecate the
     `adr` domain itself. -->

- DEC 60b1e331-4fe4-4d41-8c50-d0bd6227c472: Use an API Gateway for Key Issuance and Revocation

  Use an API gateway for key issuance and revocation — chosen to meet
  the sub-2s performance requirements above without duplicating logic
  per service.

- DEC 365bcab7-b086-4205-84f9-eb1654ff8410: Rate-Limit Key Issuance Per Partner

  Rate-limit key issuance per partner, not globally — operational
  decision, not architecture-level, kept in `dec` rather than a full
  ADR.

## Risks

<!-- Mapping: not a dedicated 29148 section, but INCOSE/MITRE both treat
     risk as a first-class SE artifact; specmgr already has `rsk`.
     Single list — no `### <Name>` sub-heading needed. -->

- RSK c1b33b41-d976-4191-a2c5-6f3c09441eb3: Partner-Side API Key Leakage

  Partner-side key leakage via insecure storage. Initial: Probability
  3 / Impact 4 (High); mitigated by the revocation-within-1s
  requirement above; Residual: Probability 2 / Impact 4 (Medium) —
  Strategy: reduce.

<!-- Q: the initial/residual probability-impact coordinates and
     strategy are now folded into the notes paragraph's prose (as
     above) rather than a separate inline suffix — does that read
     clearly enough, or is structured/tabular data like this a case
     where an inline suffix (or even a small embedded table) would be
     clearer than prose despite REQ-003's "no full-content embedding"
     preference? -->

## Verification

<!-- Mapping: 29148 §9.5.18 says verification content should be given
     "in a parallel manner with the information elements in 9.5.5 to
     9.5.17" — i.e. interleaved per requirement category, not modeled as
     its own document artifact — while INCOSE/MITRE SEG both confirmed
     "Verification/Test and Evaluation" as a life-cycle stage with no
     existing specmgr domain (Task 0.6/0.9 findings). That gap is now
     filled by the sibling `vcr` ("Verification Case Record") domain,
     feat-33 (`.specmgr/feat/feat-33-vcr/README.md`) — Phase 1
     (models + parser) already complete. Single list — no `### <Name>`
     sub-heading needed, same shape as every other section above. -->

- VCR ee8672f3-af06-4f53-bc2a-80b5a581399b: API Key Issuance Latency Verification

  Verifies REQ 64265c7a-144c-46d5-9bd7-13750254bc54 above (`vcr`'s own
  `## Verifies` field points back at it) via a `Test`-method acceptance
  criterion measuring issuance time against the 2s threshold. Full
  coverage.

- VCR 4584b5e0-6fe2-47e1-ab7d-0c67835e7df0: API Key Revocation Latency Verification

  Verifies REQ 779b8275-beb8-4428-9e90-962929a42af7 above via a
  `Test`-method acceptance criterion measuring revocation time against
  the 1s threshold. Full coverage.

<!-- Q: `vcr`'s own tools/resources (Phase 2/3/4) don't exist yet as of
     this revision, so this section is a placeholder shape only — falls
     back to REV 4's free-text prose if `vcr` isn't ready by the time
     `sysrs` reaches its own Phase 1. Also: should every `req`/`uc` above
     be expected to have a matching `vcr` entry (a completeness check),
     or is partial verification coverage normal/acceptable for a
     work-in-progress `sysrs` document? -->

## Systems Integration

Same status as Verification in REV 1-4 — MITRE SEG names it as a
distinct life-cycle stage, no specmgr domain exists (unlike Verification
above, `vcr` does not cover this).

> Draft placeholder: integration sequence/dependencies across
> subsystems, interface control points.

<!-- Q: same three options as Verification had before REV 5 — keep as
     free text, omit, or stub as "not yet available"? -->

## Traceability

Not a 29148 section by that name, but ISO/IEC/IEEE 29148 does name a
"Requirements Traceability Matrix" (RTM) as a real, standard artifact
(§6.4.3 and elsewhere in `ISO_29148.md`), and INCOSE/MITRE SEG both call
out bidirectional traceability (needs → requirements → design →
verification) as a first-class concern, not just an implicit property of
the other sections' cross-references.

<!--
Q: is a dedicated `## Traceability` section even needed if every other
   section already carries a cross-reference list pointing at its
   upstream source (uc -> req -> dec -> rsk -> vcr, now via the
   notes-paragraph prose rather than a formal field)? Candidate options:
   (a) drop this section — traceability already lives implicitly in the
       per-section lists above;
   (b) keep it as a single consolidated table/matrix view for readers
       who don't want to walk every section — this is exactly what
       29148 calls an RTM, so there is now a named standard concept to
       model it against instead of inventing an ad hoc shape;
   (c) keep it, but only for chains that skip sections (e.g. a `req`
       with no traceable `uc`, or now, no traceable `vcr`, flagged as a
       gap).
-->

## References

Free text / external links only (standards cited, external docs) —
mirrors 29148's own "5 References" section. Not a cross-reference list
since it points outside specmgr.

<!-- Loose bullet list, no structured per-item model — mirrors `feat`'s
     `#### Depends On`/`#### Blocks` (plain `MarkdownSection4`, free
     markdown text containing a bullet list, no `items: list[X]`),
     since a reference has no specmgr `id` to extract. -->

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life
  cycle processes — Requirements engineering*
- MITRE Systems Engineering Guide (2014 ed.), "Develop System-Level
  Technical Requirements"

## More Information

<!-- Free-form optional supplementary text, no fixed format — mirrors
     `dec`/`vcr`'s own `## More Information` (`MarkdownSection2`)
     directly, at the same H2 level (not a level-shift from `req`'s/
     `feat`'s H3 `### More Information`, as REV 1-4 described it). -->

## Updates

<!-- Dynamic list of free-form-titled entries tracking changes to this
     specification document itself over time — mirrors DEC's/VCR's own
     `Updates`/`UpdateEntry` shape (a free-form H3 title, convention is
     date-led like `2026-08-30 — Created` but not enforced by regex),
     not `feat`'s stricter, mandatory, timestamp-enforced variant — see
     REV 5 changelog item 3. Optional as a whole, and the last section of
     the document if present. -->

### 2026-08-30 — Initial draft created

Initial `sysrs` document drafted from the linked Goals/Problem
Statement/Scenarios; no Requirements or Decisions cross-referenced yet.

______________________________________________________________________

<!--
Overall open questions for discussion, beyond the inline ones above:

1. Section count/order above (14 H2s incl. Overview/References/More
   Information/Updates) is deliberately generous — which of these
   merge, split, become optional-only, or get cut entirely?
2. Should every section be present-but-empty when no artifacts exist
   yet (like REQ/UC do), or should absent sections omit their heading
   entirely (like ADR's optional sections)?
3. Is per-domain grouping (one H2 per source domain, as drafted) the
   right shape, or should sysrs instead group by SE life-cycle stage
   (Concept Development / Requirements Engineering / Architecture /
   Design / Integration / Test) per MITRE SEG's process view, with each
   stage pulling from whichever domains are relevant? (This is now
   tracked as Task 0.3.1, a prerequisite for the rest, and is still not
   started as of REV 5.)
4. Now that `## Verification` is a `vcr` cross-reference list, should
   `sysrs`'s own Phase 1 formally *depend on* `feat-33-vcr` shipping its
   tools/resources first, or can `sysrs` ship with `## Verification`
   modeled the same way (free cross-reference bullets, no live
   `get_vcr`-backed validation) regardless of `vcr`'s own tooling
   progress?
-->
