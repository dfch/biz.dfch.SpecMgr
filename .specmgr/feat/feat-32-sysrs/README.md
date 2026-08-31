---
created: 2026-08-30
id: feat-32-sysrs
status: planning
updated: 2026-09-01
version: 1.0.0
---

# Feature: Add artifact type "System Specification" (SYSRS)

## Plan

### Overview

New aggregator domain for a **System Specification** document: a
document-type that ties together already-existing specmgr artifacts
(`gol`, `prb`, `uc`, `req`, `rsk`, `dec`/`adr`, `qa`) into one coherent,
navigable specification, rather than duplicating their content. Follows
the domain-first hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and
is expected to land on the "simple surface" used by GOL/RSK/QA/DEC/SOP
(generic `update`/`set_status` dispatch from day one, per ADR
36905d5b-8057-4294-8665-c7eed5534db0 — no per-domain mutation tools).

Domain key: `sysrs` (decided 2026-08-30 — see Decisions Made).

### Requirements

- REQ-001 (research, done): Survey existing external standards/templates
  for system-level specification documents to ground the new schema's
  section outline instead of inventing one from scratch. Sources
  reviewed: ISO/IEC/IEEE 29148:2018 (SyRS/StRS/SRS/BRS/OpsCon templates),
  INCOSE (SE Handbook v5, Needs and Requirements Manual, Guide to Writing
  Requirements — requirement categorization: Function/Performance,
  Fit/Operational, Form, Quality, Compliance; **primary-source-verified
  wording differs, see Design Notes item 2**), MIL-STD-961E (System/
  Subsystem Specification format — recalled from training, not freshly
  verified against a primary source), MITRE's system-specification
  writing guide (not accessible for verification over the web; a local
  copy of MITRE's Systems Engineering Guide was added to this folder and
  is being converted to markdown for direct reading — see Task 0.5),
  HERMES 2022 (Swiss PM method — confirmed to be process/role-oriented,
  not a content-outline source), NASA SE Handbook (specification-tree
  concept, no fixed template of its own).
- REQ-002 (decided 2026-08-31): The final section outline for the
  `sysrs` body is `example.v7.md` (REV 7, user-approved): 29148 §9.5
  clause structure with the BRS/StRS content borrowed up front,
  `## Requirements` grouped by the nine ISO/IEC 25010:2023
  characteristics (canonical names/order), `## Other Characteristics`
  for 29148's non-25010 requirement categories (§9.5.11–9.5.17), plus
  `## Appendix`/`## Definitions and Acronyms`; per-section mandatory/optional
  flags and content types are approved in that file (18 H2s, 22 H3s).
  See Decisions Made (2026-08-31, REV 6/7 entries).
- REQ-003 (decided): Cross-references to other domains carry **id,
  title, and a very short (one-line) agent-generated paraphrase**, not
  embedded full content — mirrors GOL/DEC/SOP's `RelatedArtifacts`
  bullet-list shape, with an added short-summary field per entry. Exact
  field shape (plain text suffix vs. a structured sub-field) still to be
  designed in Phase 1.
- REQ-004 (not started): Everything else a from-scratch domain needs,
  patterned on `sop`'s precedent (`.specmgr/feat/feat-30-sop/README.md`):
  `sysrs/models/v1/` schema, parser, 8 standard tools (`create_sysrs`,
  `parse_sysrs`, `list_sysrs`, `get_sysrs(raw=False)`,
  `get_sysrs_example`, `get_sysrs_template`, `delete_sysrs` stub,
  `validate_sysrs`), 3 resources (`schema`/`example`/`template`, no
  `/{id}`, no `/list`), prompts, generic `update`/`set_status` dispatch
  entries, packaged data, cross-cutting registration
  (`server.py`/`AGENTS.md`/`README.md`/CI/pre-commit).

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — this README's Design Notes section
  documents the outline of every reviewed source (29148, INCOSE, MIL-
  STD-961E, MITRE, HERMES, NASA) with an explicit confidence note on
  which were freshly verified vs. recalled from training.
- [x] ACC-002: Verifies REQ-002 — user has reviewed and approved a
  concrete `## H2` section list for `sysrs` (not just the tailored-SyRS
  direction): `example.v7.md` (REV 7), approved 2026-08-31 — all
  per-section mandatory/optional flags accepted, `## Appendix`/
  `## Definitions and Acronyms` added.
- [ ] ACC-003: Verifies REQ-003 — the exact `RelatedArtifacts`-with-
  summary field shape is written down in Design Notes and validated
  against the `models/md` engine (mirroring `sop`'s pre-implementation
  empirical-verification discipline) before Phase 1 starts.
- [ ] ACC-004: Verifies REQ-004 — full domain implementation, once
  REQ-002/003 are locked, following `sop`'s task-list shape.

### Scope

Included (this planning pass):

- External-standard research and source-to-domain mapping.
- Recording the three decisions already made (reference-by-id +
  paraphrase; SyRS-tailored-not-verbatim direction; domain key =
  `sysrs`).
- Converting the locally-supplied MITRE Systems Engineering Guide PDF
  and INCOSE Systems Engineering Handbook 5e (2023) PDF to markdown so
  each can be read/searched directly during planning.
- Discussion-draft document outlines (`example.md`, `example.v2.md`,
  ..., this folder, one file per reviewed revision so every version
  stays comparable side by side — never edited/overwritten in place) —
  illustrative markdown only, not a schema, not wired into any tool.
- One filled-in reference example (`sysrs-example.md`, added
  2026-09-01) — the approved REV 7 outline instantiated with actual
  (fictional) content for the same case; illustrative markdown only,
  not a schema, not wired into any tool.

Explicitly out of scope (this planning pass — deferred to later
phases/README updates):

- Final section-by-section schema (REQ-002 still open).
- Any code, models, tools, or tests.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic
  `update`/`set_status` dispatch — new domains use it from day one), ADR
  ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
  resource); `.specmgr/feat/feat-30-sop/README.md` as the most recent
  from-scratch-domain precedent to copy tooling/registration shape from;
  `.specmgr/feat/feat-33-vcr/README.md` (sibling feature, its own
  worktree/branch) — the `vcr` ("Verification Case Record") domain it
  builds fills the "Verification/Test and Evaluation" gap this feature's
  own research identified (Task 0.6/0.9), and its Phase 1
  (`vcr/models/v1/`) is already implemented; `sysrs`'s `## Verification`
  section (see `example.v5.md`) is now designed as a cross-reference list
  to `vcr`, so this feature depends on `vcr` existing (at least its
  schema) before its own Phase 1 can finalize that section's shape.
- Blocks: nothing known.

### Design Notes

**External source outlines reviewed (REQ-001):**

1. **ISO/IEC/IEEE 29148:2018** (verified via a live example document) —
   defines 5 related templates (BRS/StRS/OpsCon/SyRS/SRS). SyRS/SRS
   outline:

   - 1 Introduction (Purpose, Scope, Product perspective incl. system/
     user/hardware/software/communications interfaces, memory
     constraints, operations, site adaptation; Product functions; User
     characteristics; Limitations; Assumptions/dependencies;
     Definitions; Acronyms)
   - 2 Requirements (External interfaces, Functions, Usability,
     Performance, Logical database, Design constraints, Standards
     compliance, System attributes)
   - 3 Verification
   - 4 Supporting information
   - 5 References

   **Correction (2026-08-31, Task 0.10, done)**: the outline above was
   recorded before the actual ISO/IEC/IEEE 29148:2018 standard text was
   available locally ("verified via a live example document" meant an
   example SyRS instance, not the standard itself) and **does not match**
   the standard's real normative SyRS content clause. The user has since
   added `ISO_29148.md` (full converted standard text) and
   `ISO_24765.md` (ISO/IEC/IEEE 24765:2017, *Systems and software
   engineering — Vocabulary*) to this folder. Reading `ISO_29148.md`
   directly (§8.4 "System requirements specification" — general
   description and example-outline pointer; §9.5 "System requirements
   specification (SyRS) content" — the actual normative clause) shows
   the true structure is **19 sub-clauses**, not 5: 9.5.1 SyRS overview,
   9.5.2 System purpose, 9.5.3 System scope, 9.5.4 System overview
   (9.5.4.1 System context, 9.5.4.2 System functions, 9.5.4.3 User
   characteristics), 9.5.5 Functional requirements, 9.5.6 Usability
   requirements, 9.5.7 Performance requirements, 9.5.8 System interface
   requirements, 9.5.9 System operations (9.5.9.1 Human system
   integration, 9.5.9.2 Maintainability, 9.5.9.3 Reliability, 9.5.9.4
   Other quality requirements), 9.5.10 System modes and states, 9.5.11
   Physical characteristics (9.5.11.1 Physical, 9.5.11.2 Adaptability),
   9.5.12 Environmental conditions, 9.5.13 System security requirements,
   9.5.14 Information management requirements, 9.5.15 Policy and
   regulation requirements, 9.5.16 System life cycle sustainment
   requirements, 9.5.17 Packaging/handling/shipping/transportation
   requirements, 9.5.18 Verification, 9.5.19 Assumptions and
   dependencies. §9.5.18 (Verification) itself says verification content
   should be given "in a parallel manner with the information elements in
   9.5.5 to 9.5.17" — i.e. interleaved per requirement category, not a
   separate document artifact — which is additional supporting evidence
   for modeling `sysrs`'s own `## Verification` as a cross-reference to
   `vcr` entries rather than a monolithic free-text section (see
   `example.v5.md`). §5.4 also confirms exactly **six** named information
   items overall — BRS, StRS, SyRS, SRS, ConOps, OpsCon — and that
   ConOps/OpsCon are themselves interdependent with StRS's own
   operational-concept sub-clauses (§9.4.16/9.4.17), i.e. the overlap
   `sysrs` has between `## Stakeholder Needs and Elicitation` (`qa`) and
   `## Operational Concept and Scenarios` (`uc`) is inherent to the
   standard, not introduced by specmgr's own tailoring. §6.4.3 confirms
   the standard **4** verification methods (inspection, analysis or
   simulation, demonstration, test) MITRE SEG/INCOSE also describe —
   direct primary-source support for `vcr`'s own "DTAIS adds a 5th method
   deliberately" framing. The still-open question is now Task 0.3.2's:
   whether/how the richer 19-subclause §9.5 categorization (vs. INCOSE's
   five-word scheme) should drive `## System Requirements`'s grouping —
   see `example.v5.md`'s updated inline `<!-- Q: ... -->` there. `ISO_24765.md` (the vocabulary standard) is not yet referenced by any
    design decision here — candidate use: grounding a future `## Definitions`/
    `## Acronyms` section (mirroring 29148 §9.2.3/9.2.5) if/when one is
    added; flagged, not yet actioned.

    **Resolution (2026-08-31, REV 6/7)**: the still-open grouping
    question above is settled by the user in `example.v6.md`/
    `example.v7.md`: `## Requirements` is grouped by the nine ISO/IEC
    25010:2023 product-quality characteristics (canonical names and
    model order, per the `specmgr://iso25010` resource) instead of
    29148's per-subclause categories or INCOSE's five-word scheme, and
    29148's remaining non-25010 requirement categories (§9.5.11–9.5.17)
    sit under `## Other Characteristics`. The full 29148 §9.5 → section
    mapping (incl. 9.5.8 → Compatibility/Interoperability and the
    9.5.9.4 absorption note) and the REQ placement rule (first `##
    Characteristics` item of the REQ document, no `req`-domain change)
    are recorded in `example.v7.md`'s header comment.

2. **INCOSE** (SEBoK, SE Handbook v5, Needs and Requirements Manual,
   Guide to Writing Requirements) — process-oriented, not a fixed
   template; contributes a requirement **categorization** scheme and two
   artifacts every system spec should carry: a requirement tree
   (parent/child allocation) and bidirectional traceability to needs,
   verification, and design.

   **Verified against the primary source (Task 0.9, done)**: the user
   supplied a local copy of *INCOSE Systems Engineering Handbook, 5th
   Edition (2023)* (`INCOSE Systems Engineering Handbook 5e 2023.pdf`,
   370 pages), converted to `incose-se-handbook-5e-2023.md` (Task 0.8,
   same `pdftotext`+`pandoc` pipeline as the MITRE guide — see
   "Conversion method" below), and read directly (via a delegated
   sub-agent research pass, since the converted file is ~5,900 lines/
   1.2MB). Findings:

   - **The categorization scheme's exact wording differs from what was
     recalled above.** The Handbook's actual, verbatim text (Section
     2.3.5.3 "System Requirements Definition", ~line 2232): *"The
     system requirements must address **function, fit, form, quality,
     and compliance** with stakeholder and business needs."* — five
     bare words, not the "Function/**Performance**, Fit/**Operational**"
     slash-compounds used above; those extra qualifiers are not
     supported by this primary source and are likely a conflation with
     the Guide to Writing Requirements/Needs and Requirements Manual
     (cited alongside but not present in this converted file) — treat
     as unverified until GtWR/NRM are checked directly. **The bullet
     above is being kept as originally recorded for history, but any
     future schema/prompt wording should use the Handbook's own five
     words, not the slash-compound version.**
   - **No document-outline/SyRS artifact exists in this Handbook at
     all**: `SyRS`/"System Requirements Specification" do not appear
     anywhere in the text (confirmed by full-text search). The
     Handbook's IPO ("Typical Outputs") lists for the Stakeholder
     Needs/Requirements Definition (2.3.5.2) and System Requirements
     Definition (2.3.5.3) processes are granular data items
     ("stakeholder needs and requirements", "traceability mapping", a
     "report") — never a single consolidated specification document.
     Appendices D (N2 diagram legend) and E (input/output glossary)
     looked like the most likely place for a document template but
     turned out to be a process-dependency map and a flat one-line
     glossary respectively — useful for precise term definitions, not
     a section outline.
   - **29148 is cited ~12 times**, always for term/method definitions
     (e.g. the four verification methods, the ConOps definition) —
     never for document structure; the Handbook does not defer to
     29148's document shape, it just borrows some of its vocabulary.
   - **Traceability (Section 3.2.3)** confirms the
     bidirectional/vertical/horizontal traceability concepts and the
     need→stakeholder-req→system-req→architecture/design→verification/
     validation chain, but gives no concrete matrix/table structure —
     conceptual only.
   - **Verification (2.3.5.9) and Systems Integration (2.3.5.8)** are
     both real, well-developed processes with their own IPO
     input/output lists, but neither yields a ready section-content
     checklist — same "confirmed gap, no template" conclusion already
     reached from the MITRE guide, not a new one.
   - **Overall**: this primary-source read corroborated rather than
     extended the secondhand INCOSE knowledge already captured above
     (aside from tightening the categorization wording) — it did not
     surface any new candidate structure for `sysrs`'s section outline.
     29148 (tailored) and the MITRE SEG's life-cycle view remain the
     primary structural sources; INCOSE stays a corroborating/
     terminology source, not an outline source.

3. **MIL-STD-961E** (recalled from training — DTIC/primary source was
   unreachable during this research pass, re-verify before relying on
   it structurally) — classic System/Subsystem Specification (SSS)
   shape: 1 Scope, 2 Applicable Documents, 3 Requirements, 4
   Verification (1:1 traceable to Section 3), 5 Packaging, 6 Notes, plus
   appendices.

4. **MITRE Systems Engineering Guide** (2014 ed., ~726 pages) — a local
   PDF (`se-guide-book-interactive.pdf`) supplied by the user in this
   folder (web fetches of MITRE's site returned 403 during the initial
   research pass) was converted to `se-guide-book-interactive.md` (Task
   0.5 — see Design Notes' "Conversion method" for the pipeline used)
   and read directly (Task 0.6). Confirmed content, directly relevant to
   the outline decision:

   - Organizes its "SE Life-Cycle Building Blocks" section as a V-model:
     **Concept Development** (Operational Needs Assessment → Concept of
     Operations → Operational Requirements → High-Level Conceptual
     Definition) → **Requirements Engineering** (Eliciting/Collecting/
     Developing Requirements → Analyzing and Defining Requirements →
     Prototyping/Experimentation for uncertainty) → **System
     Architecture** (Architectural Frameworks/Models/Views → Approaches
     to Architecture Development → Architectural Patterns) → **System
     Design and Development** (Develop System-Level Technical
     Requirements → Develop Top-Level System Design → Assess the
     Design's Ability to Meet the System Requirements) → **Systems
     Integration** → **Test and Evaluation** → **Implementation,
     Operations and Maintenance, and Transition**. This is a *process*
     view (mirrors INCOSE's), not a document-section outline, but it
     independently confirms our gol→uc→req→dec→rsk/verification chain
     mapping and flags **Test and Evaluation / verification** and
     **Systems Integration** as life-cycle stages with no current
     specmgr domain.
   - Its "Concept of Operations" article endorses **IEEE Std
     1362-1998** and lists CONOPS' critical components: the existing
     system being replaced, justification for a new/modified system, a
     description of the proposed system, and scenarios of system use in
     the user's environment — this maps directly onto `gol` (existing-
     system/justification) + `uc` (scenarios).
   - Its "Develop System-Level Technical Requirements" article
     explicitly names the deliverable a **"system specification
     document"** using formal "shall"/"should" statements, and gives a
     "System-Level Requirements Checklist" (traceable to user
     requirements; describes a function/performance/constraint/
     reference; appropriate level of detail; legal/regulatory
     constraints; enterprise-architecture constraints; environmental
     design requirements; all external interfaces; quantifiable/
     testable/verifiable performance; avoid "shall not" and vague words
     like "maximize"; use ranges not single-point values; distinguish
     threshold vs. objective requirements) — independently confirms
     INCOSE's Function/Performance, Fit/Operational, Form, Quality,
     Compliance categorization from a second source (**note**: the
     INCOSE Handbook's own primary-source wording, verified in Task
     0.9, is the plainer five words "function, fit, form, quality, and
     compliance" — see Design Notes item 2; this MITRE bullet has not
     itself been re-verified against MITRE's primary text for the
     slash-compound wording).
   - Its "Assess the Design's Ability to Meet the System Requirements"
     article confirms the traceability chain explicitly: mission/needs
     → operational requirements → functional/system requirements →
     design → performance verification — the same chain our candidate
     domain-to-source mapping table already reflects.

   > **Note — Task 0.7 replaced (2026-08-30):** a second, narrower
   > MITRE technical report, *Guide for Writing System Specifications*
   > (MITRE Product/Case No. PR 14-3372), was originally slated for
   > Task 0.7 as likely more directly relevant to `sysrs`'s document
   > structure than the broader SEG book above. It could never be
   > fetched over the web (`403 Forbidden` from both
   > `https://www.mitre.org/sites/default/files/publications/pr-14-3372-guide-for-writing-system-specifications.pdf`
   > and the MITRE SEG landing page tried as a fallback), and the user
   > has not supplied a local copy. **Per explicit user instruction,
   > Task 0.7 now targets a different, already-supplied document
   > instead**: INCOSE's own *Guide for Writing Requirements* (2019
   > revision, `INCOSE Guide for Writing Requirements 2019.pdf`, ~132
   > pages, owner-read-only permissions on disk). Converted to
   > `incose-guide-writing-requirements-2019.md` (1,437 lines/~319 KB)
   > via a delegated sub-agent, same `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none` pipeline as the two
   > prior conversions — this PDF needed **no** control-character
   > stripping at all (unlike the MITRE SEG guide's `\f`/`\x07` or the
   > INCOSE Handbook's wider `\x08`/`\x1e`/`\x1f` set), and the
   > ordered-list-marker-corruption spot-check passed cleanly (several
   > mid-sentence `(NNN)`-style parentheticals like `(2014)`/`(1)`/`(2)`
   > all remained plain inline text, zero renumbering). **Not yet
   > read** — this document is very plausibly the "Guide to Writing
   > Requirements" (GtWR) the INCOSE Handbook cites alongside the Needs
   > and Requirements Manual for the "Function/Performance,
   > Fit/Operational, Form, Quality, Compliance" categorization wording
   > that Design Notes item 2 flagged as unverified against the
   > Handbook's own plainer "function, fit, form, quality, and
   > compliance" (Task 0.9) — reading it (mirroring Task 0.6/0.9's
   > treatment) is a natural, high-value next step, tracked as a new
   > Task 0.7b below, but has not been done yet as part of this
   > conversion.

5. **HERMES 2022** (Swiss federal PM method) — a project-management
   method (roles/scenarios/results), not a requirements-content
   standard; could not confirm current result/document names from the
   site during this pass. Weak fit for section-outline purposes; may be
   more relevant later for a process/role model.

6. **NASA SE Handbook** — discusses a "specification tree"
   (System/Segment/Subsystem specs derived from the ConOps) but defers
   to 29148/MIL-STD-961-style content rather than defining its own
   outline.

**Domain-to-source mapping (candidate, not yet final):**

| Concept (29148/INCOSE) | Existing specmgr domain |
|---|---|
| Business/mission rationale (BRS) | `gol` |
| Stakeholder needs (StRS) | `gol` / `qa` |
| Operational concept/scenarios (OpsCon) | `uc` |
| System requirements (SyRS), incl. categories | `req` |
| Risk identification | `rsk` |
| Design/architecture decisions | `dec` / `adr` |
| Problem framing | `prb` |
| Verification planning / Test & Evaluation | `vcr` (feat-33, Phase 1 complete — closes the gap below, updated 2026-08-31) |
| Systems Integration | no dedicated domain yet (confirmed gap by MITRE SEG too) |
| Traceability / requirement tree | `RelatedArtifacts`-style cross-refs; ISO/IEC/IEEE 29148 itself names this a "Requirements Traceability Matrix" (RTM, §6.4.3) — a real standard concept, not just an ad hoc shape (added 2026-08-31) |

**Decisions made so far (see Decisions Made log):**

- Aggregation model: reference by id + title, plus a very short (one
  line) agent-paraphrased summary per reference — not full-content
  embedding.
- Section outline: lean toward a **tailored** (not verbatim) ISO/IEC/
  IEEE 29148 SyRS shape; exact section list still open, to be refined
  after reading MITRE's Systems Engineering Guide directly.
- (from your review comments on `example.md`, applied in `example.v2.md`)
  H1 title: mandatory, constrained to
  `^System Specification: .+$` (regex fullmatch against the heading
  text, same convention as `uc`'s `Extension N.`/`Step N:` and `sop`'s
  `Step N:` `@alias` regexes).
- (from your review comments on `example.md`, applied in `example.v2.md`)
  `## Overview`: mandatory, any
  markdown content — not restricted to a single paragraph.
- (from your review comments on `example.md`, applied in `example.v2.md`)
  No bold pseudo-heading (e.g.
  `**RelatedArtifacts:**`) for cross-reference lists anywhere in
  `sysrs` — use a real `### <Name>` heading instead, named for what it
  holds (`### Goals`, `### Problems`, `### Scenarios`, ...). Unlike
  `gol`'s `## Related Artifacts` wrapper (needed there because a
  goal's own H1 isn't domain-specific), `sysrs` needs no such wrapper
  H2 since every `sysrs` H2 is already domain-specific — its
  `### <Name>` list sits directly under it.
- (decided 2026-08-30, applied in `example.v3.md`) When an H2 holds
  exactly one cross-reference list, drop the `### <Name>` sub-heading
  entirely — the list sits directly under the H2. Keep the `### <Name>`
  sub-heading rule only for H2s that genuinely hold more than one
  distinct list or a mix of free text and a list (today: only
  `## Business Context and Goals`, which keeps its three H3s). Applied
  to `## Stakeholder Needs and Elicitation`, `## Operational Concept and Scenarios`, `## System Requirements`, `## Architecture and Design Decisions`, and `## Risks`, which in `example.v2.md` each had a
  redundant single H3 that just repeated (or barely reworded) its own
  H2's name (`## Risks` → `### Risks`, `## Architecture and Design Decisions` → `### Decisions`).
- (decided 2026-08-30, applied in `example.v4.md`) Cross-reference
  bullets show the title inline (`GOL-<id> + title`), reversing
  `example.v2.md`'s "id-only, no inline title" draft shape — applied
  uniformly to every cross-reference list in the document (`gol`/`prb`/
  `qa`/`uc`/`req`/`dec`/`rsk`), not just some. Matches how `gol`/`dec`'s
  own existing `### Requirements`/`### Goals`/etc. lists already show
  `"GOL-0007: <title>"` inline today. Closes the "Not yet decided" item
  from `example.v2.md`'s changelog.
- (decided 2026-08-30) `## Architecture and Design Decisions`'s example
  entries in `example.v3.md`/`example.v4.md` are `dec`-only, as a
  discussion-draft illustration convention — **not** a decision to
  deprecate the `adr` domain itself. Real `sysrs` documents may still
  cross-reference either `dec` or `adr` ids; any future decision to
  phase out `adr` repo-wide would need its own README/ADR entry.
- (decided 2026-08-30, applied in `example.v4.md`; **superseded
  2026-08-31, see below**) `## Updates` — a new
  mandatory section tracking changes to the `sysrs` document itself
  over time, added alongside `## More Information` (mirrors `req`'s/
  `feat`'s `### More Information`, level-shifted to H2). `## Updates`
  reuses `feat.Updates`/`feat.UpdateEntry` (`feat/models/v1/body.py`)
  exactly — entry heading `{ISO8601 date+time+millis+offset} — {title}`
  (em dash included) and newest-first ordering — one nesting level
  shallower than `feat`'s own `## Progress` → `### Updates` →
  `#### {timestamp} — {title}` since `sysrs` has no Plan/Progress
  split.
- (decided 2026-08-31, applied in `example.v5.md`) `## Updates` corrected
  to mirror `dec`'s/`vcr`'s actual shipped shape instead of `feat`'s —
  literal reuse of `feat.Updates`/`UpdateEntry` was never possible
  (different heading-level base classes), and reading the code showed
  `dec` (already shipped, already at the right H2/H3 level) and
  `feat-33-vcr` (built concurrently at the same level, explicitly
  choosing to mirror `dec` rather than `feat`) both use a **free-form**
  H3 title (`@alias(value=".+")`, no timestamp regex, no ordering
  validator) and treat `## Updates` as **optional as a whole**, not
  mandatory. `sysrs` now follows that same precedent instead of being the
  only H2-level domain with a stricter, mandatory, `feat`-style
  variant.
- (decided 2026-08-31, applied in `example.v5.md`) Cross-reference
  bullets switched from the `gol`/`dec`-style illustrative, hyphenated,
  truncated pseudo-id (`GOL-4b1e2c9a-...`) to `feat-33-vcr`'s now-settled
  real-id shape: `<TYPE> <uuid>: <title>` (type tag, space, a real
  8-4-4-4-12 hex UUID, colon, title) — `vcr`'s own `## Verifies` field
  uses exactly this pattern (`_VERIFIES_PATTERN` in
  `vcr/models/v1/body.py`) after an explore-agent audit found the
  `GOL-0007`-style codes shipped in `gol`/`dec`'s own examples are
  illustrative-only, structurally unenforced text with no relation to
  real (bare-UUID) ids. Also fixed a latent bug found while making this
  change: every cross-reference bullet in `example.v4.md` literally
  spelled out the four characters `+ title` as placeholder text instead
  of an actual title, despite that revision's own changelog claiming
  every bullet "carries `+ title`" (i.e. an inline title) — REV 4 never
  actually demonstrated the shape it described. `example.v5.md` fills in
  a real (fictional) title on every bullet.
- (decided 2026-08-31, applied in `example.v5.md`) `## Verification and Test Planning` renamed to `## Verification` and reshaped from a
  three-way-undecided free-text placeholder into a cross-reference list
  to `vcr` ids — same shape as every other section — now that the
  sibling `vcr` domain (feat-33) exists specifically to fill this gap
  and has completed its Phase 1 (models + parser). `## Systems Integration` is unaffected (no domain covers it yet).
- (from your review comments on `example.md`, applied in `example.v2.md`
  as a draft — see "Not yet decided" below
  for the still-open confirmation) Cross-reference entry shape: a
  bullet holding *only* the id, followed by a blank line and an
  indented "notes" paragraph carrying the paraphrase (title is not
  shown inline; resolvable via the referenced domain's own `get_<d>`
  tool on demand). Empirically maps directly onto `models/md`'s
  existing `MarkdownListItemWithNotes` class (already used by `gol`'s
  `Tags` section) — no new parser mechanics needed, which materially
  de-risks ACC-003's "validated against the `models/md` engine"
  requirement.

**Not yet decided:**

- Exact `## H2` section list and which are mandatory vs. optional.
- Whether dropping the inline title from cross-reference bullets
  (relying on id-based lookup, per the draft shape above) is
  acceptable, or the title should still appear (e.g. as the notes
  paragraph's first line) — `gol`/`dec`'s own existing
  `### Requirements`/`### Goals`/etc. lists use an inline
  `"GOL-0007: <title>"` shape today, so this is a deliberate departure
  pending confirmation.
- Whether `## Business Context` (free markdown, no fixed template)
  should be agent-drafted from linked Goals or simply omitted when
  empty.
- Whether `rsk` entries' initial/residual probability-impact
  coordinates and strategy belong in the notes paragraph's prose (as
  currently drafted) or need a more structured field/table.
- Whether/how a `## Verification` section (no existing domain covers
  this today) should be modeled.
- Whether HERMES-style role/process framing is wanted at all, or fully
  dropped given its weak fit for a content outline.
- Whether "Systems Integration" becomes its own `## H2` section in
  `sysrs` (free text, since no domain models it yet) or is deferred
  entirely to a later feature/domain — independently confirmed as a gap
  by INCOSE and MITRE SEG. **Verification is no longer part of this open
  question** (resolved 2026-08-31): the sibling `vcr` domain (feat-33)
  fills that gap, so `sysrs`'s `## Verification` is now designed as a
  `vcr` cross-reference list (`example.v5.md`), the same shape as every
  other section — see the updated Domain-to-source mapping table and
  Dependencies.
- Whether ISO/IEC/IEEE 29148 §9.5's own 19-subclause requirement-category
  taxonomy (vs. INCOSE's five-word scheme) should inform `## System Requirements`'s grouping, and whether `ISO_24765.md` (the vocabulary
  standard, added alongside the full `ISO_29148.md` text) should ground a
  future `## Definitions`/`## Acronyms` section — both added 2026-08-31,
  see Design Notes item 1's correction and Task 0.10/0.11.

**Conversion method used for the MITRE guide (Task 0.5) and the INCOSE
SE Handbook (Task 0.8), for reproducibility:** `pandoc` cannot read PDF
directly (`pandoc --list-input-formats` has no `pdf` entry), so the
pipeline was
`pdftotext se-guide-book-interactive.pdf raw.txt` (poppler-utils; the
PDF only restricts editing, not copy/print, so no password was needed) →
strip non-printable control characters (`\f` page breaks, stray `\x07`
bytes) with `tr` → `pandoc -f markdown-fancy_lists -t gfm --wrap=none`
to normalize into clean GFM. The `-fancy_lists` extension is explicitly
disabled: pandoc's default `markdown` reader treats a line like `(781) 271-2000` as an ordered-list marker `(781)` and **silently renumbers
it** on the next such line (verified: a two-line repro turned `(703)`
into `782)`), which would corrupt numbers throughout the body text.
Quality spot-checked against the "Develop System-Level Technical
Requirements" and "Concept of Operations" articles — prose reads
cleanly and a real table of contents is preserved; page-number/header/
footer noise from the original layout remains interspersed (expected,
not worth cleaning further for a read-only research reference). An
`pdftohtml`-based alternative was tried first and rejected: it emits
almost no real `<hN>` heading tags (one `<h1>` in a 30-page test) and
wraps everything in absolutely-positioned `<div>`s that produce far
noisier markdown than the plain-text route.

**Task 0.8 (INCOSE SE Handbook) run notes:** same pipeline, applied to
`INCOSE Systems Engineering Handbook 5e 2023.pdf` (370 pages, not
password-protected) → `incose-se-handbook-5e-2023.md`. This PDF had a
wider set of stray control bytes than the MITRE guide's: besides `\f`/
`\x07`, found 154 `\x08` (backspace) artifacts — all inside the table
of contents, where a run of dot-leader characters collapsed to a single
backspace between a TOC entry title and its page number — plus one each
of `\x1e`/`\x1f` inside a single cost-effectiveness formula (`CE = SE / (IC × SC)`, Blanchard 1967), where `pdftotext` mis-decoded a
math/multiplication-symbol glyph from the PDF's embedded font as a
control byte; all four were stripped the same way (`tr -d`). No
ordered-list-marker corruption found on spot-check (verified the
"History of Changes" version table's `1.0`/`2.0`/`2.0A`/`3.0`/`3.1`
sequence round-tripped intact, and the "What Is Systems Engineering?"
body prose in Section 1.1 reads cleanly with citations intact). As with
the MITRE guide, no real `#`/`##` heading tags are produced (plain-text
input carries no font-size/bold signal for pandoc to infer headings
from) — this is expected and acceptable for a read-only research
reference, not a document meant to be parsed structurally.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: No `/{id}` resources for
  id-based reads (tool-only `get_<d>`)
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Paged `list_<domain>` tool
  instead of a `/list` resource
- 36905d5b-8057-4294-8665-c7eed5534db0: Generic `update`/`set_status`
  dispatch tools — new domains use these from day one, no per-domain
  mutation tools

No new ADR is anticipated yet; revisit once the aggregation-model and
schema decisions above are finalized — if the "reference + AI-paraphrase"
pattern turns out to generalize beyond this one domain, it may warrant
its own ADR rather than living only in this feature's Design Notes.

### Task List

#### Phase 0: Research and outline definition

- [x] Task 0.1: Survey external standards/templates (29148, INCOSE,
  MIL-STD-961E, MITRE, HERMES, NASA SE Handbook) — depends on: none —
  status: done (2026-08-30)
- [x] Task 0.2: Capture research + open questions in this README —
  depends on: Task 0.1 — status: done (2026-08-30)
- [x] Task 0.5: Convert the locally-supplied
  `se-guide-book-interactive.pdf` (MITRE Systems Engineering Guide) to
  markdown via `pdftotext` + `pandoc` (see Design Notes' "Conversion
  method") for direct reading — output: `se-guide-book-interactive.md`
  in this folder — depends on: none — status: done (2026-08-30)
- [x] Task 0.6: Read the converted MITRE guide's system-specification-
  relevant sections and fold findings into this README's Design Notes —
  depends on: Task 0.5 — status: done (2026-08-30)
- [x] Task 0.3.1: Decide `sysrs`'s organizing principle for the section
  list — one `## H2` per source domain (as drafted in `example.v2.md`,
  the latest reviewed revision; see `example.md` for the first
  reviewed revision) vs.
  grouping by MITRE SE life-cycle stage (Concept Development →
  Requirements Engineering → Architecture → Design → Integration →
  Test) — this is a prerequisite for 0.3.2–0.3.5 below — depends on:
  Task 0.2, Task 0.6 — status: done (2026-08-31, REV 6/7: neither
  option — 29148 §9.5 clause structure with the BRS/StRS content
  borrowed up front, and `## Requirements` grouped by the nine
  ISO/IEC 25010:2023 product-quality characteristics; see
  `example.v7.md` and Decisions Made)
- [ ] Task 0.3.2: Decide the concrete `## H2` section list and which
  sections are mandatory vs. optional, walking through `example.v2.md`
  section by section (incl. whether Business Context and Problem
  Statement merge, whether a `qa` reference belongs at the sysrs level
  at all, whether requirements get grouped by INCOSE category, and
  whether a dedicated `## Traceability` section is needed or is
  redundant with per-section cross-reference lists) — depends on: Task
  0.3.1 — status: done (2026-08-31: the user approved the concrete
  H2/H3 list in `example.v7.md` (REV 7) — all PROPOSED
  mandatory/optional flags accepted (annotated "-- > OK"), plus
  `## Appendix` and `## Definitions and Acronyms` added as OPTIONAL free-form
  H2s; ACC-002 checked. Settled within it: Business Context + Problem
  Statement merge (H3s under one H2), `qa` belongs (Stakeholder Needs
  and Elicitation), requirements grouped by 25010:2023 characteristics
  (not INCOSE), no dedicated `## Traceability` (implicit via
  per-section cross-refs))
- [x] Task 0.3.3: Decide whether/how to model Verification and Test &
  Evaluation — free-text `## H2` now, omitted from `sysrs` v1 entirely,
  or stubbed as "not yet available" pending a future dedicated domain
  (see `example.v2.md`'s three options under that section) — depends on:
  Task 0.3.2 — status: done (2026-08-31, superseded by feat-33-vcr:
  `## Verification` is now a `vcr` cross-reference list, see
  `example.v5.md` and Decisions Made; formal sign-off still tracked via
  ACC-002)
- [x] Task 0.3.4: Decide whether Systems Integration gets its own
  `## H2` section or is deferred — same three options as Task 0.3.3,
  decided independently since Verification and Systems Integration may
  land on different answers — depends on: Task 0.3.2 — status: done
  (2026-08-31, REV 6: no own H2 — folded under `## System Overview` as
  `### System Integration`, free text, PROPOSED optional in
  `example.v7.md`)
- [x] Task 0.3.5: Decide whether HERMES-style role/process framing is
  wanted anywhere in `sysrs`, or dropped entirely given its weak fit as
  a content-outline source (per Design Notes item 5) — depends on: Task
  0.3.1 — status: done (2026-08-31: closed as dropped — no HERMES-style
  role/process framing in `sysrs`; the approved outline is
  29148/25010-based, and HERMES was already confirmed process/role-
  oriented rather than a content-outline source, Design Notes item 5)
- [x] Task 0.3.6: Decide the exact `RelatedArtifacts`-with-paraphrase
  cross-reference field shape — plain-text suffix on the existing
  bullet vs. a distinct structured sub-field — and whether any domain
  (e.g. `rsk`'s initial/residual probability-impact coordinates) may
  surface extra inline data without crossing into "full-content
  embedding" (REQ-003) — depends on: Task 0.2, Task 0.6 — status: done
  (2026-08-31 — already recorded in Decisions Made: bullets use
  `<TYPE> <uuid>: <title>` + a notes-paragraph paraphrase, `rsk`
  coordinates fold into the notes prose; this task line lagged behind
  those entries, corrected now)
- [x] Task 0.4: Re-verify MIL-STD-961E's structure against a primary
  source (currently unreachable) if it ends up informing the final
  outline — depends on: Task 0.3.2 — status: done (2026-08-31: closed
  as dropped — the approved outline (REV 7) does not draw on
  MIL-STD-961E, so there is nothing left to re-verify; the recalled
  notes stay flagged as such in Design Notes)
- [x] Task 0.7: ~~Fetch/convert/read MITRE's *Guide for Writing System
  Specifications* (PR 14-3372)~~ **replaced 2026-08-30, per explicit
  user instruction** — see Design Notes' note under item 4. MITRE
  PR 14-3372 remains unobtainable (403 over the web, no local copy
  supplied) and is no longer being pursued for this task slot. Instead:
  convert the user-supplied `INCOSE Guide for Writing Requirements 2019.pdf` to markdown via a delegated sub-agent, same `pdftotext` +
  `pandoc` pipeline as Tasks 0.5/0.8 — output:
  `incose-guide-writing-requirements-2019.md` in this folder — depends
  on: none — status: done (2026-08-30, conversion only; see Task 0.7b
  for reading it)
- [x] Task 0.7b: Read the converted INCOSE *Guide for Writing
  Requirements* (2019)'s relevant sections and fold findings into
  Design Notes item 2 (mirrors Task 0.6/0.9's treatment for the MITRE
  SEG guide/INCOSE Handbook) — in particular, check whether this is
  the "Guide to Writing Requirements" (GtWR) the Handbook cites for
  the "Function/Performance, Fit/Operational, Form, Quality,
  Compliance" categorization wording still flagged as unverified there
  — depends on: Task 0.7 — status: done (2026-08-31: skipped per user —
  "not needed at this time"; the approved outline (REV 7) groups
  requirements by 25010:2023 characteristics, so the INCOSE
  categorization question it was meant to settle is moot)
- [x] Task 0.8: Convert the user-supplied `INCOSE Systems Engineering Handbook 5e 2023.pdf` (370 pages) to markdown via `pdftotext` +
  `pandoc` (see Design Notes' "Conversion method" → "Task 0.8 run
  notes") for direct reading — output:
  `incose-se-handbook-5e-2023.md` in this folder — depends on: none —
  status: done (2026-08-30)
- [x] Task 0.9: Read the converted INCOSE SE Handbook's
  system-specification-relevant sections (mirrors Task 0.6 for the
  MITRE guide; delegated to a sub-agent given the file's size, ~5,900
  lines) and fold findings into Design Notes item 2 (INCOSE) —
  depends on: Task 0.8 — status: done (2026-08-30)
- [x] Task 0.10: Re-verify Design Notes item 1's ISO/IEC/IEEE 29148 SyRS
  outline directly against the now-locally-available full standard text
  (`ISO_29148.md`), correcting it if it doesn't match (mirrors Task 0.9's
  treatment for INCOSE) — depends on: none — status: done (2026-08-31;
  outline did not match — corrected, see Design Notes item 1's
  "Correction" note, §8.4/9.5/5.4/6.4.3 cited directly)
- [ ] Task 0.11: Decide whether/how `ISO_24765.md` (ISO/IEC/IEEE
  24765:2017, *Systems and software engineering — Vocabulary*, added to
  this folder alongside `ISO_29148.md`) grounds a future `## Definitions`/
  `## Acronyms` section (mirroring 29148 §9.2.3/9.2.5), or stays an
  unused reference — depends on: Task 0.3.2 — status: not-started

#### Phase 1+: Schema, tools, resources, prompts, registration

Not planned yet — Phase 0 is now complete (all tasks done; Task 0.11
is the only leftover and is non-blocking), so the next step is to
break this down (mirroring `.specmgr/feat/feat-30-sop/README.md`'s
phase structure; the `vcr` domain, now on this branch via the 2026-08-31
dev merge, is the newest from-scratch precedent, `feat-30-sop` the
dispatch-only one). The approved section list is `example.v7.md` (REV
7).

## Progress

### Current Status

**As of 2026-08-31**: Research done, outline defined, still Phase 0 —
no schema or code written yet. All six primary sources are surveyed
and, where primary text was available, directly read (29148/24765 via
`ISO_29148.md`/`ISO_24765.md`, MITRE SEG via
`se-guide-book-interactive.md`, INCOSE SE Handbook — findings in
Design Notes items 1–2 with confidence notes; the INCOSE source PDF
and its conversion were intentionally deleted afterward, the recorded
findings stand as-is). Local `dev` was merged into this branch on
2026-08-31: the sibling `feat-33-vcr` domain is now **fully shipped**
(models, parser, tools, resources, prompts — not just Phase 1), and
the `specmgr://iso25010`/`specmgr://dtais`/`specmgr://rasci`
resources plus staged release automation (v0.15.0) are on this branch
— `sysrs`'s `## Verification` cross-reference design now has its
dependency in place for real. Seven discussion-draft outline
revisions exist: `example.md` (REV 1) through `example.v7.md` (REV 7,
latest), plus one filled-in reference example with actual (fictional)
content for the same case, `sysrs-example.md` (added 2026-09-01) —
the document the future `get_sysrs_example` tool/resource is expected
to return. REV 1–4 were user-reviewed rounds; REV 5 a self-directed
cross-check pass; **REV 6 (user hand-edits) reorganized the outline
into its final shape** — 29148 §9.5 clause structure with the BRS/StRS
content borrowed up front, `## Requirements` grouped by the nine
ISO/IEC 25010:2023 characteristics, `### System Integration` folded
under `## System Overview`, `## References` restored, `## Overview`/
`## Traceability` dropped — settling Task 0.3.1 (organizing
principle) and Task 0.3.4 (Systems Integration). REV 7 applied the
2026-08-31 decisions (H1 prefix `^System Requirements Specification:
.+$`, no clause numbers in headings, canonical 25010 names/order,
title-case headings) and added a mandatory/optional flag + content-type
comment after every heading — **all approved by the user the same day**
(annotated "-- > OK"), with two further OPTIONAL free-form H2s added
(`## Appendix`, `## Definitions and Acronyms`) — closing Task 0.3.2 and ACC-002.
Tasks 0.3.5 (HERMES framing), 0.4 (MIL-STD-961E re-verification), and
0.7b (INCOSE GtWR read) were closed the same day as dropped/skipped, so
**Phase 0 is complete** (Task 0.11 — ISO_24765 → `## Definitions and Acronyms`
grounding — is the only non-blocking leftover). Four ISO 29148 outline
examples for the sibling document types (BRS/StRS/SyRS/SRS per
§9.3–9.6, committed in `bf0e703`) serve as reference material for the
borrowed-section content.

### Handoff to next session (read this first if you are a new session)

- **You are here for a reason**: this feature moved out of the shared
  main checkout into its own `git worktree` because another agent was
  concurrently working on `feat-30-sop` directly on `dev` in the main
  checkout (`/home/user/src/biz.dfch.SpecMgr`). Do **not** `cd` back into
  that main checkout and run git commands there on this feature's
  behalf — it's a different agent's live working directory. (This
  concern may be stale by now — re-check whether `feat-30-sop` has
  since merged — but don't assume the main checkout is free to use
  without checking first.)
- **Where you are**: worktree
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs`, branch
  `feat-32-sysrs`, originally branched from local `dev` (rebuilt clean
  at `4a4fc62`); local `dev` was merged in on 2026-08-31 (`0f2794d`,
  vcr fully shipped + v0.15.0 + release automation — 2,704 tests OK
  after the merge), so the branch now contains the full current dev
  tree plus this feature's docs. **Run `git status`/`git log
  --oneline` yourself before trusting any commit list** — as of this
  update the uncommitted state is: untracked `example.v6.md` (the
  user's hand-edited REV 6, not yet committed) and `example.v7.md`
  (REV 7, written this round), plus this README's modifications.
  Nobody has been asked to commit any of this yet — per this repo's
  "only commit when explicitly requested" norm.
- **Folder history**: this feature folder was originally created as
  `feat-0-sysrs` (no GitHub issue yet) in the main checkout, then
  renamed to `feat-32-sysrs` and moved into this worktree/branch per
  explicit user instruction (branch name and folder name both use issue
  number 32). If you see any stray reference to `feat-0-sysrs` anywhere
  outside this README's own history, it's stale — the folder's live
  name is `feat-32-sysrs`.
- **INCOSE PDF/conversion — confirmed gone on purpose, not a bug**:
  `INCOSE Systems Engineering Handbook 5e 2023.pdf` and
  `incose-se-handbook-5e-2023.md` do **not** exist anywhere in this
  worktree or in git history (`git log --all` on both paths returns
  nothing) — this was discovered and confirmed with the user during
  this session's wrap-up: **intentional deletion**, not lost work. The
  findings already folded into Design Notes item 2 (INCOSE) stand as
  recorded and are not expected to be re-verified against the primary
  source again. Don't spend time searching for these files or asking
  the user to re-supply them unless something *new* about INCOSE needs
  checking.
- **Session transcripts**: two exist, both already committed/staged —
  `session-ses_fac9-feat-32-00-design.md` (first session: initial
  research, MITRE SEG conversion, worktree-move discussion — committed
  at `ad9e12f`) and `session-ses_fac6-feat-32-01-design.md` (second
  session: domain-key decision, Task 0.3 split, `example.md`/
  `example.v2.md` review rounds, INCOSE conversion/read — currently
  staged, not yet committed, see above). **This third session (H3
  sub-heading decision, REV 3/REV 4 example review, the ADR/DEC and
  Updates/More Information decisions, this wrap-up) has no separate
  transcript export** — this README's Recent Updates log is the only
  record of it, same as every other session gap so far. If the user
  exports one later, move it into this folder following the same
  `session-ses_*-feat-32-NN-*.md` naming/`git check-ignore`-at-nested-
  path pattern already used twice.
- **Immediate next action**: **break down Phase 1** (schema/models/
  parser, then tools/resources/prompts/registration) now that the
  section list is approved (`example.v7.md`, REV 7) and Phase 0 is
  complete — mirror `.specmgr/feat/feat-30-sop/README.md`'s phase
  structure; `vcr` (on this branch via the 2026-08-31 dev merge) is
  the newest from-scratch precedent, `feat-30-sop` the dispatch-only
  one. Before writing any Pydantic model, empirically verify the
  approved section shapes against the `models/md` engine (mirrors
  `feat-30-sop`'s pre-implementation discipline) — in particular the
  `MarkdownListItemWithNotes` cross-reference bullets (REQ-003 shape,
  worked example in `example.v7.md`'s Requirements answer comment) and
  the DEC/VCR-style `Updates` shape (worked example in that file's
  trailing answer comment). Non-blocking leftover: Task 0.11 (ISO_24765
   → `## Definitions and Acronyms` grounding). Use `example.v7.md` (the approved
   section list) and `sysrs-example.md` (the filled-in reference
   content for the same case) as the reference artifacts; REV 1–6 are
   kept for comparison.
- **Still open / unresolved**: Task 0.11 (whether/how `ISO_24765.md`
  grounds the new `## Definitions and Acronyms` section or stays an unused
  reference — non-blocking; the approved section is free-form text
  either way); the Phase 1 breakdown itself (immediate next action);
  optional cleanup of the `req` docstring's pre-2023 example
  characteristic names (noted in `example.v7.md`'s header, out of
  scope). **Settled and closed this round**: Task 0.3.2 + ACC-002
  (approved list in `example.v7.md` — all M/O flags accepted,
  Appendix/Abbreviations added), Task 0.3.5 (HERMES framing dropped),
  Task 0.4 (MIL-STD-961E re-verification dropped — the outline doesn't
  use it), Task 0.7b (INCOSE GtWR read skipped — not needed at this
  time). Also settled earlier this day: organizing principle (Task
  0.3.1 — 29148 clause structure + 25010 categories), Systems
  Integration placement (Task 0.3.4 — `### System Integration` under
  `## System Overview`), `## Traceability`/`## Overview` (dropped),
  cross-reference field shape (Task 0.3.6, `<TYPE> <uuid>: <title>` +
  notes paraphrase).

### Blockers

None currently open. (Former Task 0.7 blocker — MITRE's *Guide for
Writing System Specifications*, PR 14-3372, unreachable over the web —
was resolved 2026-08-30 by replacing that task's source document
entirely, per explicit user instruction, rather than continuing to
wait on it; see Task List Task 0.7/Design Notes item 4's note.)

### Recent Updates

#### Update 2026-09-01 (sysrs-example.md added — filled-in reference example with actual content)

- Completed: At the user's request, wrote `sysrs-example.md` — the
  first filled-in `sysrs` document: the approved REV 7 section list
  (`example.v7.md`) instantiated with actual (fictional) content for
  the same "Example Widget Platform" case used by `example.md` …
  `example.v5.md` and the `iso-29148-*` companion examples. No
  discussion-draft comments, no MANDATORY/OPTIONAL flags: real
  frontmatter (`created`/`updated` consistent with its own `## Updates`
  entries) + body — H1, all 18 H2s in approved order, all 22 H3s
  present and filled,
  cross-reference bullets in the settled `<TYPE> <uuid>: <title>` +
  one-line notes-paragraph shape (REV 5's already-established UUIDs
  reused verbatim where the same artifact is referenced; the rest
  newly invented, all fictional), and DEC/VCR-style `## Updates`
  carrying the two entries from REV 7's own worked example. Serves as
  the reference artifact for Phase 1 — the document the future
  `get_sysrs_example` tool/resource is expected to return, and the
  concrete worked input for the `models/md` empirical verification.
  Scope, Current Status, and Handoff updated to point at it.
- Next: unchanged — break down Phase 1 and empirically verify the
  approved section shapes against the `models/md` engine, using
  `sysrs-example.md` as the worked input.

#### Update 2026-08-31 (example.v7.md approved — section list final, ACC-002; Tasks 0.3.5/0.4/0.7b closed)

- Completed: The user reviewed `example.v7.md`, approved all 38
  PROPOSED mandatory/optional flags (annotated "-- > OK" on each —
  normalized to bare MANDATORY/OPTIONAL comments in the file), and
  added two new OPTIONAL free-form H2s (`## Appendix`,
  `## Definitions and Acronyms`, with purpose comments) — closing Task 0.3.2 and
  ACC-002 (REQ-002 decided; the approved 18-H2/22-H3 list in
  `example.v7.md` is the schema's basis for Phase 1). Answered the
  file's two inline TODOs: the exact REQ cross-reference format
  (`- REQ <uuid>: <title>` bullet + optional indented notes-paragraph
  paraphrase, with worked examples) under `## Requirements`, and the
  `## Updates` shape (H3 entries with free-form date-led titles +
  prose, with a two-entry worked example) at the end of the file.
  Closed per user direction: Task 0.3.5 (HERMES framing dropped),
  Task 0.4 (MIL-STD-961E re-verification dropped — the outline doesn't
  use it), Task 0.7b (INCOSE GtWR read skipped — not needed at this
  time). **Phase 0 is now complete** (only non-blocking leftover:
  Task 0.11, ISO_24765 → Abbreviations grounding). Current Status,
  Handoff (immediate next action = break down Phase 1), Task List,
  Decisions Made, and the v7 header all updated to record the
  approval.
- Next: break down Phase 1 (models/parser, then tools/resources/
  prompts/registration) mirroring `feat-30-sop`'s phase structure with
  `vcr` (now on this branch) as the newest precedent; empirically
  verify the section shapes against the `models/md` engine before
  writing Pydantic models.

#### Update 2026-08-31 (example.v7.md added — REV 6 reviewed, organizing principle settled, concrete section list with proposed mandatory/optional comments)

- Completed: Reviewed the user's hand-edited `example.v6.md` (REV 6)
  against REV 5, the recorded decisions, 29148 §9.5, and the
  `specmgr://iso25010` resource, and wrote `example.v7.md` (REV 7, new
  file per the never-edit-in-place convention) applying the decisions
  agreed in review: H1 prefix now `^System Requirements
  Specification: .+$` (supersedes REV 2's `^System Specification:
  .+$`); the `(9.5.x)` clause numbers removed from the headings
  (traceability annotations only, mapping table in v7's header); the
  nine Requirements H3s ordered per the canonical ISO/IEC 25010:2023
  model (resolves REV 6's TODO); heading casing normalized to title
  case. REV 6's structural changes carried over as-is: `### System
  Integration` folded under `## System Overview`, `## Other Quality
  Requirements` renamed to `## Other Characteristics`, `## References`
  restored, `## Overview`/`## Traceability` dropped. Every heading in
  v7 now carries a PROPOSED: MANDATORY/OPTIONAL + content-type comment
  for the user to pick from, plus the agreed rules: optional
  cross-reference sections (GOL/PRB/QA/UC/DEC/ADR/RSK/REQ/VCR) must
  have ≥ 1 item when present, and a REQ's placement under a 25010/
  Other-Characteristics H3 is determined by the FIRST item of that
  REQ's own `## Characteristics` section (free text in the shipped
  `req` schema — no `req` change, near-names resolved by the agent).
  Settled as a result: Task 0.3.1 (organizing principle — 29148 clause
  structure + 25010 categories), Task 0.3.4 (Systems Integration →
  `### System Integration` under System Overview), Task 0.3.6
  (task line synced with the already-recorded decision); Task 0.3.2
  now in-progress with the user's M/O pick as the only remaining step.
  Design Notes item 1 gained a Resolution note; Current Status and
  Handoff rewritten to the new state.
- Next: the user's pick on `example.v7.md`'s PROPOSED comments (see
  Handoff → Immediate next action), then ACC-002 sign-off and Phase 1
  planning.

#### Update 2026-08-31 (dev merged — vcr fully shipped, v0.15.0, release automation)

- Completed: Merged local `dev` (= `origin/dev` @ `9eb7e8a`) into
  `feat-32-sysrs` (merge commit `0f2794d`; the uncommitted README edits
  were stashed across the merge and restored). 14 commits landed:
  `feat(33)` — the VCR domain **complete** (models, parser, all 8
  tools, resources, prompts, tests; not just Phase 1), `feat(30)` SOP
  domain, the `specmgr://iso25010`/`specmgr://dtais`/`specmgr://rasci`
  general resources, staged release automation (`scripts/release.sh`,
  `/release` command, release SOP), v0.15.0 version bump, CI/
  pre-commit updates. Post-merge: `uv sync --all-extras --frozen`
  (env now 0.15.0) and the full test suite — 2,704 tests OK.
- Next: `sysrs`'s `## Verification` cross-reference design now has its
  `vcr` dependency fully in place on this branch; Phase 1 can model
  against `vcr`'s shipped `<TYPE> <uuid>: <title>` id shape for real.

#### Update 2026-08-31 (ISO 29148 outline examples added — BRS/StRS/SyRS/SRS per §9.3–9.6)

- Completed: Added four new discussion-draft examples, one per
  specification document type the ISO/IEC/IEEE 29148:2018 norm gives a
  normative content outline for: `iso-29148-brs-example.md` (§9.3, 18
  sections), `iso-29148-strs-example.md` (§9.4, 18),
  `iso-29148-syrs-example.md` (§9.5, 18 + 9 nested under System
  overview / System operations / Physical characteristics), and
  `iso-29148-srs-example.md` (§9.6, 19 + 9 nested under Product
  perspective). Convention in all four: section names are verbatim
  from the standard (the norm's mandatory outline, clause number in
  each heading); the standard's descriptive text is paraphrased into
  HTML guidance comments, never quoted verbatim (the full standard
  text stays gitignored); and the section bodies carry concrete
  fictional example content — all four form one consistent BRS → StRS
  → SyRS → SRS chain for the same "Example Widget Platform" case used
  by `example.md`…`example.v5.md`, with the SRS zooming onto the Key
  Issuance Service product. The §x.x.1 "overview" subclauses are
  omitted (meta-text about the clause, not document content).
- Next: use these as filled-in reference examples when finalizing the
  tailored `sysrs` outline (Tasks 0.3.1/0.3.2) — §9.5's actual 18+
  subclause content is now available as a worked example, not just as
  the summarized taxonomy in `example.v5.md`'s changelog.

#### Update 2026-08-31 (example-example-inc.md added — data-grounded companion example from an external project)

- Completed: At the user's request, examined `~/src/example-acme` (an
  external, already-populated specmgr-style project: example-inc, the
  planned replacement for the legacy production-control system
  "example-inc" used by the Example Inc) to judge
  whether a "fully fledged" `sysrs` example could be built from real
  data, then wrote `example-example-inc.md` doing exactly that. Judgment:
  partially — `example-acme` has real, specmgr-authored `qa` (1 large
  document), `uc` (54 documents, mostly still stubs), and `req` (80
  short documents) artifacts, but **no `gol`/`prb`/`dec`/`rsk`/`vcr`
  artifacts at all**. Populated the corresponding H2 sections
  (Goals/Problem Statement/Architecture and Design Decisions/Risks/
  Verification) from real narrative source material in that project
  (`Ausschreibungsgegenstand.md`'s Ziel/Nutzen/Ausgangslage,
  `Bewertungregeln.md`'s real TS/ZK acceptance methodology,
  `summary-example-acme.md`'s make-or-buy/risk analysis,
  `img/jwt-flow-1.plantuml`'s OIDC flow) but cross-referenced with
  illustrative, obviously-fake ids for those five domains, clearly
  flagged as such throughout. Discovered mid-task that `example.v5.md`
  had landed concurrently in this same folder (a different session's
  work) — rebased `example-example-inc.md` from `example.v4.md`
  conventions onto REV 5's (real `<TYPE> <uuid>: <title>`
  cross-reference shape, `vcr`-backed `## Verification`, DEC/VCR-style
  `## Updates`) before finalizing, to avoid shipping an already-stale
  illustration.
- Next: get the user's reaction to `example-example-inc.md`, in
  particular whether the "real ids for qa/uc/req, illustrative-flagged
  ids for gol/prb/dec/rsk/vcr" approach is an acceptable way to handle
  a source project with partial domain coverage, and whether this kind
  of external-data cross-check should become a standard step before
  Task 0.3.1/0.3.2 are finalized. Does not itself resolve Task 0.3.1
  (still the actual next priority, unchanged).

#### Update 2026-08-31 (example.v5.md added — cross-checked against ISO_29148.md/ISO_24765.md and feat-33-vcr's shipped code)

- Completed: At the user's request, examined `example.v4.md` for gaps,
  inconsistencies, and improvements, considering both the now-locally-
  available full ISO/IEC/IEEE 29148:2018 standard text (`ISO_29148.md`,
  plus `ISO_24765.md`, the vocabulary standard — both added to this
  folder since the last research pass) and the sibling `feat-33-vcr`
  ("Verification Case Record") feature, which is being built concurrently
  in its own worktree/branch and has already shipped its Phase 1
  (`vcr/models/v1/`, schema + parser + tests). Read `feat-33-vcr`'s
  README and actual model source (not just its plan text) directly.
  Findings, all folded into Design Notes/Decisions Made/Task List/Not
  yet decided above and applied to a new `example.v5.md`:
  - Design Notes item 1's recorded ISO/IEC/IEEE 29148 SyRS outline (a
    5-part "Introduction/Requirements/Verification/Supporting
    information/References" shape) does **not** match the standard's
    actual normative SyRS content clause (§9.5, 19 sub-clauses) — it was
    recorded before the full standard text was available locally.
    Corrected with exact clause citations (new Task 0.10, done).
  - `feat-33-vcr` exists specifically to fill the "Verification/Test and
    Evaluation" gap this feature's own research identified, and its
    Phase 1 is complete — `## Verification and Test Planning` renamed to
    `## Verification` and reshaped into a `vcr` cross-reference list
    (closes Task 0.3.3; `## Systems Integration`/Task 0.3.4 is
    unaffected, still open).
  - `example.v4.md`'s cross-reference bullets used the same
    illustrative, unenforced, hyphenated pseudo-id style already shipped
    in `gol`/`dec`'s own examples (`GOL-0007`-ish codes); `feat-33-vcr`
    independently audited this exact question for its own `## Verifies`
    field and settled on a real, regex-enforced `<TYPE> <uuid>: <title>`
    shape — adopted here too, closing REQ-003. Also discovered and fixed
    a REV 4 bug in the process: every cross-reference bullet's "inline
    title" was literally the placeholder text `+ title`, never an actual
    title, despite REV 4's own changelog claiming otherwise.
  - `## Updates`'s plan ("reuses `feat.Updates`/`UpdateEntry` exactly")
    was never actually achievable (different heading-level base classes)
    and, more importantly, both `dec` (shipped) and `feat-33-vcr`
    (in-flight, same H2/H3 level as `sysrs`) independently use a
    free-form-title, optional-as-a-whole shape instead of `feat`'s
    stricter one — `sysrs` now follows that precedent instead.
  - Minor: `## More Information`'s precedent citation corrected from "a
    level-shift from `req`/`feat`'s H3" to "`dec`/`vcr`'s own H2 shape
    directly" (the closer, already-correct-level precedent).
  - New open questions added: whether/how 29148 §9.5's own richer
    requirement-category taxonomy should inform `## System Requirements`'s grouping (alongside INCOSE's five-word scheme); how
    `ISO_24765.md` might ground a future Definitions/Acronyms section
    (new Task 0.11); `## Traceability`'s options, now with 29148's named
    "Requirements Traceability Matrix" (RTM) concept as concrete
    grounding for a matrix-view option.
- **`example.v5.md` has not yet been reviewed by the user** — unlike REV
  2/REV 4 (which applied specific user review comments), REV 5 is a
  self-directed cross-check pass done at the user's request to "find
  gaps, inconsistencies and improvements," not a response to inline
  annotations on a prior revision. Flagged prominently in Handoff.
- Next: get the user's reaction to `example.v5.md`, in particular
  whether the `## Verification`-as-`vcr`-cross-reference approach and
  the `<TYPE> <uuid>: <title>` id-format switch are acceptable, then
  continue with Task 0.3.1 (still the actual next priority, unchanged).

#### Update 2026-08-30 (Task 0.7 replaced — INCOSE Guide for Writing Requirements converted)

- Completed: Per explicit user instruction, replaced Task 0.7's source
  document. The old target, MITRE's *Guide for Writing System
  Specifications* (PR 14-3372), stays unobtainable (403 over the web,
  no local copy ever supplied) and is no longer being pursued for this
  task slot. The user supplied a local copy of INCOSE's own *Guide for
  Writing Requirements* (2019 revision) in this folder instead
  (`INCOSE Guide for Writing Requirements 2019.pdf`, owner-read-only
  permissions). Converted it to `incose-guide-writing-requirements-2019.md`
  (1,437 lines/~319 KB) via a delegated sub-agent, using the same
  `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none`
  pipeline as the two prior conversions in this folder. This PDF
  needed **no** control-character stripping at all (a first — the
  MITRE SEG guide needed `\f`/`\x07` stripped, the INCOSE Handbook
  needed a wider `\x08`/`\x1e`/`\x1f` set); the ordered-list-marker-
  corruption spot-check passed cleanly. Marked Task 0.7 done
  (conversion only) and split off a new Task 0.7b (not started) to
  actually read it and fold findings into Design Notes item 2 —
  flagged that this document is plausibly the "Guide to Writing
  Requirements" (GtWR) the INCOSE Handbook cites for the still-
  unverified "Function/Performance, Fit/Operational, Form, Quality,
  Compliance" categorization wording (vs. the Handbook's own plainer
  "function, fit, form, quality, and compliance", confirmed in Task
  0.9). Cleared the former Task 0.7 entry from Blockers.
- Next: Task 0.7b (read the new conversion, fold findings in) is
  available whenever wanted, but is not itself blocking Task 0.3.1,
  which remains the actual next priority (see Handoff).

#### Update 2026-08-30 (session wrap-up — context limit reached)

- Completed (this session, full arc): explained the H3-sub-heading
  pattern in `example.v2.md`, then applied the user's "drop it when
  there's exactly one list" decision as `example.v3.md`; explained the
  ISO/IEC/IEEE 29148 "Verification" section and the four verification
  methods (Inspection/Analysis/Demonstration/Test — flagged as recalled
  from training, no single standardized acronym, not re-verified this
  session); reviewed the user's own edits to `example.v3.md` (inline
  titles, ADR→DEC rename, `## References`/`## More Information`/
  `## Updates` additions), resolved the open points interactively, and
  snapshotted the result as `example.v4.md` (restoring the "never edit
  in place" convention `example.v3.md` had broken for one round). All
  decisions recorded in Decisions Made/Design Notes. During wrap-up,
  discovered and confirmed with the user that the INCOSE PDF/`.md`
  conversion were intentionally deleted (not lost work) — Current
  Status and Handoff updated accordingly.
- **This session is being wrapped up here due to context-window
  limits, not because the work is done** — Task 0.3.1 is still the
  immediate next action (unchanged from before this session started;
  this session was all groundwork/example-review, not the organizing-
  principle decision itself). See "Handoff to next session" above for
  the full current git-status picture (staged vs. further-modified vs.
  untracked) before doing anything else — don't assume the summary
  there is still accurate without running `git status` yourself first,
  the same caveat every prior wrap-up has carried.
- Next: a new session should (1) run `git status` to confirm the
  handoff summary above, (2) decide with the user how to split the
  accumulated uncommitted changes across commits (nothing has been
  committed since `ad9e12f`, across two full sessions now), then
  (3) proceed with Task 0.3.1 interactively using `example.v4.md`.
  Optional hygiene suggestion, carried over from the previous wrap-up
  and still not acted on: "Recent Updates" has accumulated many entries
  all dated the same day — consider running the `compact_history`
  prompt (`general/prompts/`) to rotate older ones into a sibling
  `history.md`.

#### Update 2026-08-30 (example.v4.md added — inline titles, dec-only illustration, Updates/More Information sections)

- Completed: `example.v3.md` was edited in place (breaking the "new
  file per reviewed round" convention) to add `+ title` to some
  cross-reference bullets, rename an `ADR-...` example entry to
  `DEC-...`, and sketch new `## References`/`## More Information`/
  `## Updates` sections. Reviewed the edit with the user and resolved
  the open points: (1) inline titles apply to **every** cross-reference
  bullet, not just some — reverses `example.v2.md`'s "id-only" draft
  shape; (2) the ADR→DEC rename is a `sysrs`-example-illustration
  convention only, **not** a decision to deprecate the `adr` domain
  repo-wide; (3) `## Updates`'s entry heading reuses
  `feat.Updates`/`feat.UpdateEntry` (`feat/models/v1/body.py`) exactly
  — `{timestamp} — {title}` with em dash and newest-first ordering,
  one nesting level shallower than `feat`'s own `## Progress` →
  `### Updates` → `#### {timestamp} — {title}`; (4) restored the
  "never edit in place" convention by snapshotting the resolved state
  into a fresh `example.v4.md`, leaving `example.v3.md` untouched for
  history. Also clarified `## References`'s "loose bullet list" intent:
  a plain unstructured bullet list (no per-item id model), mirroring
  `feat`'s `#### Depends On`/`#### Blocks` (`MarkdownSection4`, free
  markdown text, no `items: list[X]`), since references point outside
  specmgr and have no `id` to extract. Recorded all four decisions in
  Decisions Made/Design Notes.
- Next: continue Task 0.3.1/0.3.2 with the user using `example.v4.md`
  (the flagged-for-confirmation `## Related Artifacts` wrapper-drop
  question from `example.v2.md`'s changelog is still open).

#### Update 2026-08-30 (example.v3.md added — H3 sub-heading redundancy resolved)

- Completed: Walked through `example.v2.md` with the user, who flagged
  that several sections had a `### <Name>` sub-heading that just
  repeated (or barely reworded) their own H2's name (`## Risks` →
  `### Risks`, `## Architecture and Design Decisions` →
  `### Decisions`), since REV 2 had applied "every cross-reference list
  gets a named H3" uniformly without checking whether the name added
  information. Decided: drop the `### <Name>` sub-heading whenever an
  H2 holds exactly one list; keep it only where an H2 genuinely holds
  more than one distinct list or a mix of free text and a list (today,
  only `## Business Context and Goals`, which keeps its three H3s).
  Wrote `example.v3.md` applying this to `## Stakeholder Needs and Elicitation`, `## Operational Concept and Scenarios`,
  `## System Requirements`, `## Architecture and Design Decisions`, and
  `## Risks` — no other content changes from REV 2. Recorded the
  decision in Decisions Made and Design Notes.
- Next: continue Task 0.3.1/0.3.2 with the user using `example.v3.md`
  (the flagged-for-confirmation items from REV 2's changelog — the
  `## Related Artifacts` wrapper drop and the inline-title omission —
  are still open).

#### Update 2026-08-30 (session wrap-up — context limit reached)

- Completed (this session, full arc): domain key decided (`sysrs`);
  MITRE SEG and INCOSE SE Handbook both converted to markdown and read
  directly (Tasks 0.5/0.6, 0.8/0.9); Task 0.3 split into Tasks
  0.3.1–0.3.6; two discussion-draft outline revisions written and
  reviewed (`example.md` REV 1 with the user's inline comments,
  `example.v2.md` applying them — each new revision gets its own file,
  never edited in place, after an earlier in-session mistake overwrote
  `example.md` and had to be recovered from conversation history, see
  the "example.v2.md added" entry below). Design Notes, Decisions Made,
  and "Not yet decided" are all current as of this update.
- **This session is being wrapped up here due to context-window limits
  in the conversation, not because the work is done** — Task 0.3.1 is
  still the immediate next action (see "Handoff to next session"
  above), and there are real uncommitted changes on disk (this README
  plus the four new files listed in "Where you are" above) that a new
  session must not lose track of.
- Next: a new session should (1) confirm the uncommitted-files
  situation above is still accurate (`git status`), deciding whether to
  commit before or after further work, (2) read this README's Design
  Notes/Decisions Made/Not-yet-decided in full for context (no separate
  session-transcript export exists for this stretch of work, unlike the
  earlier worktree-move session — this README plus the on-disk files
  are the only record), then (3) proceed with Task 0.3.1 interactively
  with the user, using `example.v2.md`. Optional hygiene suggestion,
  not required: "Recent Updates" below has accumulated ~10 entries all
  dated the same day — consider running the `compact_history` prompt
  (`general/prompts/`) to rotate the older ones into a sibling
  `history.md` if this file's length becomes a problem for a future
  session's own context budget.

#### Update 2026-08-30 (INCOSE SE Handbook read — Task 0.9 done)

- Completed: Delegated a read of `incose-se-handbook-5e-2023.md`
  (~5,900 lines/1.2MB, no real markdown headings) to a research
  sub-agent, targeting six specific questions: whether Sections 2.3.5.2/
  2.3.5.3 name a concrete "System Requirements Specification"/SyRS
  output artifact; whether Appendices D/E (N2 diagram legend,
  input/output glossary) give document-content guidance; whether/how
  INCOSE cross-references 29148 for document structure; whether
  Section 3.2.3 gives a concrete traceability-matrix structure;
  whether Verification (2.3.5.9)/Integration (2.3.5.8) yield a
  document-content checklist for the two MITRE-identified gaps; and
  verifying the exact wording of the requirement categorization scheme.
  Findings folded into Design Notes item 2 (INCOSE) and into REQ-001's
  source list and the MITRE-guide bullet that had cited the same
  categorization: **no** SyRS/document-outline artifact exists anywhere
  in the Handbook (confirmed by full-text search); Appendices D/E are a
  process-dependency legend and a flat glossary, not a template;
  29148 is cited ~12 times but only for term/method definitions, never
  document structure; traceability guidance (bidirectional/vertical/
  horizontal, Section 3.2.3) is conceptual only, no matrix template;
  Verification/Integration processes have IPO output lists but no
  section-content checklist (same "confirmed gap" as MITRE, not new);
  and the categorization scheme's *verbatim* wording (Section 2.3.5.3,
  ~line 2232) is the plainer "function, fit, form, quality, and
  compliance" — the "Function/**Performance**, Fit/**Operational**"
  slash-compounds used elsewhere in this README are not supported by
  this primary source and are flagged as unverified (possibly
  conflated with the Guide to Writing Requirements/Needs and
  Requirements Manual, neither of which is in this converted file).
  Net effect: this primary-source read corroborated rather than
  extended prior secondhand INCOSE knowledge — it does not change the
  structural direction (29148-tailored + MITRE SEG life-cycle view
  remain the outline sources), but it does correct one piece of
  previously-unverified wording.
- Next: proceed with Tasks 0.3.1–0.3.6 using `example.v2.md`; no
  further action needed on INCOSE unless the GtWR/NRM sources
  mentioned above are later supplied for direct verification of the
  slash-compound categorization wording.

#### Update 2026-08-30 (INCOSE SE Handbook 5e 2023 converted)

- Completed: User supplied a local copy of the *INCOSE Systems
  Engineering Handbook, 5th Edition (2023)* (`INCOSE Systems Engineering Handbook 5e 2023.pdf`, 370 pages) in this feature folder
  — the actual primary source behind Design Notes item 2's INCOSE
  bullet points, which until now reflected recalled/secondary knowledge
  only. Converted it to `incose-se-handbook-5e-2023.md` (Task 0.8) via
  the same `pdftotext` + `pandoc -f markdown-fancy_lists -t gfm --wrap=none` pipeline used for the MITRE guide (see Design Notes'
  "Conversion method"). This PDF needed a wider control-character strip
  than the MITRE guide (`\x08`/`\x1e`/`\x1f` in addition to `\f`/
  `\x07` — see "Task 0.8 run notes" for what each artifact was).
  Quality spot-checked: no ordered-list-marker corruption (verified via
  the "History of Changes" version table and Section 1.1's opening
  prose), full 370-page range converted through to the closing Index.
  Not yet read section-by-section.
- Next: Task 0.9 — read the converted handbook's
  system-specification-relevant sections and fold findings into Design
  Notes item 2, same treatment as Task 0.6 did for the MITRE guide;
  then continue with Tasks 0.3.1–0.3.6.

#### Update 2026-08-30 (example.v2.md added — first user review of example.md)

- Completed: User reviewed `example.md` and left inline comments
  resolving several open points: H1 title is mandatory with prefix
  regex `^System Specification: .+$`; `## Overview` is mandatory but
  unrestricted markdown (not one paragraph); no bold pseudo-heading for
  cross-reference lists anywhere (`**RelatedArtifacts:**` banned, real
  `### <Name>` headings used instead, no `## Related Artifacts` wrapper
  needed since sysrs's H2s are already domain-specific); and a concrete
  cross-reference bullet shape (id-only bullet + loose "notes"
  paragraph carrying the paraphrase, title omitted). Wrote a **new**
  file, `example.v2.md`, applying all of the above, generalized
  consistently to every section (not just the one the user annotated) —
  `example.md` itself (REV 1, with the user's original inline comments)
  is left untouched on disk precisely so every reviewed revision stays
  independently comparable; this is now the standing convention for
  this artifact (new numbered file per round, never edit-in-place).
  Note: an earlier pass in this same session had mistakenly overwritten
  `example.md` in place with the REV 2 content, losing the user's
  original comments from disk (the file was never committed, so git
  history didn't help either) — recovered only because this
  conversation's own tool-call history still held the exact REV 1 text,
  which was rewritten back to `example.md` verbatim before `example.v2.md`
  was created. Also discovered that the new cross-reference shape maps
  directly onto `models/md`'s existing `MarkdownListItemWithNotes` class
  (already used by `gol`'s `Tags` section) — no new parser mechanics
  needed. Folded the resolved items into this README's Decisions
  Made/Design Notes, and added new "Not yet decided" items for the
  parts `example.v2.md` explicitly flags for confirmation
  (title-omission generalization, `## Business Context` sourcing,
  `rsk` coordinate placement, the `## Related Artifacts` wrapper drop).
- Next: get the user's reaction to `example.v2.md`, in particular the
  flagged-for-confirmation items in its changelog comment (points 3
  and 4), then continue resolving the remaining open questions (Tasks
  0.3.1–0.3.6).

#### Update 2026-08-30 (Task 0.3 split into Tasks 0.3.1–0.3.6)

- Completed: Split the remaining Task 0.3 work into six sequenced
  sub-tasks in the Task List: 0.3.1 (organizing principle — per-domain
  vs. MITRE life-cycle-stage grouping, prerequisite for the rest), 0.3.2
  (concrete `## H2` section list and mandatory/optional flags), 0.3.3
  (Verification/Test & Evaluation modeling), 0.3.4 (Systems Integration
  modeling), 0.3.5 (HERMES role/process framing), 0.3.6
  (`RelatedArtifacts`-with-paraphrase field shape). Task 0.4 now depends
  on Task 0.3.2 instead of the old singular Task 0.3. Updated all
  current-state references to the old Task 0.3 elsewhere in this README
  (Current Status, Handoff, Blockers) to point at the relevant
  sub-task(s); left dated historical Recent Updates entries from before
  the split untouched.
- Next: work through the sub-tasks in order with the user, starting
  with Task 0.3.1, using `example.md` as the discussion artifact for
  0.3.1/0.3.2.

#### Update 2026-08-30 (domain key decided; discussion-draft outline added)

- Completed: Decided the domain key is `sysrs` (dropping `sys`/`spec`/
  `sss` candidates) — recorded in Decisions Made. Wrote a discussion-draft
  document outline to `example.md` in this folder (not a schema, not
  wired into any tool/resource) to give the user a concrete artifact to
  react to for Task 0.3's section-list decision — sketches H2 sections
  tailored from the 29148/INCOSE/MITRE-SEG mapping table already in
  Design Notes, including `RelatedArtifacts`-style cross-references to
  `gol`/`prb`/`qa`/`uc`/`req`/`dec`/`adr`/`rsk`, and free-text stand-ins
  for the confirmed Verification and Systems Integration gaps.
- Next: walk through `example.md` with the user, section by section;
  fold agreed changes back into Design Notes/this README and, once
  approved, close ACC-002 and move to the cross-reference field shape
  (ACC-003).

#### Update 2026-08-30 (moved to dedicated worktree/branch; session wrap-up)

- Completed: Discovered another agent was concurrently working on
  `feat-30-sop` directly on `dev` in the shared main checkout
  (`/home/user/src/biz.dfch.SpecMgr`) — modified
  `general/tools/set_status.py`/`update.py`/`sop/tools/__init__.py`
  plus ~20 new untracked files under `sop/tools/`/`tests/sop/tools/`.
  No file overlap was found with this feature's own untracked additions
  (`.specmgr/feat/feat-0-sysrs/` at the time), but working directly in
  the shared checkout risked future collisions and made branch-level
  git operations unsafe (any `checkout`/`stash`/`reset` there would have
  disrupted the other agent's live work). Per explicit user instruction:
  created a new `git worktree` at
  `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-32-sysrs` on a new
  branch `feat-32-sysrs` (`git worktree add ... -b feat-32-sysrs dev`,
  based on local `dev` at `d2fa3e4`) — this command alone never touches
  the main checkout's HEAD/index/files. Moved (not copied) the
  then-`feat-0-sysrs` folder's contents into the new worktree, renamed
  it to `feat-32-sysrs` per the user's chosen branch/folder name
  (matching this repo's `feat-NNN-slug` convention, issue 32), updated
  the README frontmatter `id` to match, and committed
  (`87f53c3`) inside the new worktree only. Verified afterward that the
  main checkout was completely unaffected: still on `dev` at `d2fa3e4`,
  same pending file count as before the move, zero remaining `sysrs`
  references there.
- Next: this session is being wrapped up here; a new session will
  continue from this README's "Handoff to next session" section above,
  in this worktree, on this branch. Outstanding handoff item: move the
  user's session-transcript export (created on `dev`, not yet present as
  of this update) into this folder once it exists.

#### Update 2026-08-30 (session transcript moved in; session wrap-up complete)

- Completed: The user exported this session's transcript to the main
  checkout's repo root as `session-ses_fac9-feat-32-00-design.md`
  (gitignored there by design, per `.gitignore`'s root-anchored
  `/session-ses_*.md` pattern — the repo's normal export location).
  Moved it (not copied) into this worktree at
  `.specmgr/feat/feat-32-sysrs/session-ses_fac9-feat-32-00-design.md`
  (confirmed not ignored at this nested path), matching the naming
  convention already used by other feature folders, and committed it on
  `feat-32-sysrs`. Updated the "Handoff to next session" section above
  to mark this item resolved. This closes out the outstanding item from
  the previous update — the session wrap-up is now complete.
- Next: a new session should read this README's "Handoff to next
  session" section, then the session transcript for full narrative
  context, then proceed with Task 0.3.

#### Update 2026-08-30 (MITRE guide converted and read)

- Completed: Converted the user-supplied
  `se-guide-book-interactive.pdf` (MITRE Systems Engineering Guide, 726
  pages) to `se-guide-book-interactive.md` via `pdftotext` +
  `pandoc -f markdown-fancy_lists -t gfm` (pandoc has no native PDF
  reader; `-fancy_lists` disabled to prevent silent number corruption —
  see Design Notes for the full reproducible pipeline and why an
  `pdftohtml`-based alternative was rejected). Read the "Concept
  Development", "Requirements Engineering", "System Design and
  Development" sections directly and folded findings into Design Notes:
  MITRE's SE life-cycle building blocks (Concept Development →
  Requirements Engineering → System Architecture → System Design and
  Development → Systems Integration → Test and Evaluation →
  Implementation/O&M/Transition), IEEE 1362-1998 CONOPS critical
  components, the "System-Level Requirements Checklist", and the
  mission→operational→functional/system-requirements→design→
  verification traceability chain.
- Next: Task 0.3 — finalize domain key, concrete section list, and the
  cross-reference-with-paraphrase field shape with the user.

#### Update 2026-08-30 (MITRE guide added)

- Completed: User supplied a local copy of MITRE's Systems Engineering
  Guide (`se-guide-book-interactive.pdf`) in this feature folder, to be
  converted to markdown via `pandoc` so it can be read directly instead
  of relying on training recall or blocked web fetches.
- Next: Task 0.5 (pandoc conversion), then Task 0.6 (read + fold findings
  in), then Task 0.3 (finalize outline/domain key with the user).

#### Update 2026-08-30 (initial research)

- Completed: Surveyed ISO/IEC/IEEE 29148, INCOSE (SEBoK/NRM/GtWR),
  MIL-STD-961E (recalled, not freshly verified), MITRE (inaccessible over
  the web), HERMES (inaccessible/weak fit), NASA SE Handbook. Mapped
  concepts to existing specmgr domains. Captured two user decisions on
  aggregation model and outline direction.
- Next: Task 0.5/0.6 — read MITRE's guide directly; then Task 0.3 — nail
  down the concrete section list and domain key with the user.

### Decisions Made

- **2026-08-31**: The concrete `sysrs` section list is FINAL — the
  user approved `example.v7.md` (REV 7): all 38 per-heading
  MANDATORY/OPTIONAL flags accepted as written (user-annotated "-- >
  OK"; normalized to bare flags in the file), plus two new OPTIONAL
  free-form H2s added by the user (`## Appendix`, `## Definitions and Acronyms`);
  the file's two inline TODOs were answered in place (REQ
  cross-reference format + worked example under `## Requirements`;
  `## Updates` shape + worked example at the end). Closes Task 0.3.2
  and ACC-002, decides REQ-002; the approved 18-H2/22-H3 shape is the
  schema's basis for Phase 1.
- **2026-08-31**: Closed three Phase 0 tasks without doing their work,
  per user direction — Task 0.3.5 (HERMES-style framing dropped
  entirely from `sysrs`), Task 0.4 (MIL-STD-961E re-verification
  dropped — the approved outline does not draw on it), Task 0.7b
  (INCOSE *Guide for Writing Requirements* read skipped — "not needed
  at this time"; moot anyway, since the 25010:2023 grouping replaces
  the INCOSE categorization question). Phase 0 is now complete (Task
  0.11 is the only leftover, non-blocking).
- **2026-08-31** (REV 6/7 review): Section shape decisions for the
  `sysrs` outline — (a) mandated H1 prefix is `^System Requirements
  Specification: .+$`, superseding the REV 2 decision (`^System
  Specification: .+$`); the "(SyRS)" abbreviation stays out of the
  title; (b) the `(9.5.x)` clause numbers are traceability
  annotations only — schema section names are bare (real documents
  don't carry standard-internal numbering); (c) `## Requirements` is
  grouped by the nine ISO/IEC 25010:2023 product-quality
  characteristics in canonical model order (Functional Suitability,
  Performance Efficiency, Compatibility, Interaction Capability,
  Reliability, Security, Maintainability, Flexibility, Safety),
  replacing both 29148's per-subclause categories (§9.5.5–9.5.9) and
  INCOSE's five-word scheme; 29148's non-25010 requirement categories
  (§9.5.11–9.5.17) sit under the `## Other Characteristics` umbrella
  (user's REV 6 rename of "Other Quality Requirements"); §9.5.8
  (interfaces) lands in Compatibility/Interoperability, §9.5.9.4's
  content is absorbed into Compatibility/Flexibility; (d) dropped
  `## Traceability` (traceability lives implicitly in the per-section
  cross-reference lists — REV 1's option (a)) and `## Overview`
  (absorbed by `## System Purpose` up front + `## System Overview`
  later); `## References` restored; Systems Integration has no own H2
  — `### System Integration` under `## System Overview` (free text);
  (e) every OPTIONAL section whose content is a cross-reference list
  (GOL/PRB/QA/UC/DEC/ADR/RSK/REQ/VCR) must carry ≥ 1 item when
  present; (f) a REQ bullet's placement under a 25010/
  Other-Characteristics H3 is determined by the FIRST item of that
  REQ's own `## Characteristics` section — no change to the shipped
  `req` domain (its Characteristics list is free text); placement
  vocabulary = the nine canonical 25010:2023 names + the six
  Other-Characteristics clause names, case-insensitive exact match,
  near-names resolved by the agent (e.g. "Performance" → Performance
  Efficiency, "Portability" → Flexibility); rationale for (f): the
  user's words — "we live with that and hope the agent will handle
  that". All recorded in `example.v7.md`'s header comment; the
  PROPOSED mandatory/optional flags per heading in that file await
  the user's pick (Task 0.3.2).
- **2026-08-31**: `## Verification and Test Planning` renamed to
  `## Verification`, reshaped into a `vcr` cross-reference list —
  rationale: the sibling `feat-33-vcr` domain now exists specifically to
  model verification/test-and-evaluation content (a confirmed gap this
  feature's own research identified), and its Phase 1 (schema + parser)
  is complete, so there is no longer a reason for `sysrs` to carry a
  free-text stand-in for this section.
- **2026-08-31**: Cross-reference bullets use `<TYPE> <uuid>: <title>`
  (feat-33-vcr's settled real-id shape), not the `gol`/`dec`-style
  illustrative hyphenated pseudo-id — rationale: the old style was
  audited and found to be unenforced, meaningless illustrative text; the
  new shape matches the one real id format an explore-agent search
  actually found precedent for, and closes REQ-003's exact-field-shape
  question.
- **2026-08-31**: `## Updates` reshaped to mirror `dec`'s/`vcr`'s
  free-form-title, optional-as-a-whole shape instead of `feat`'s
  mandatory, timestamp-regex-enforced one — rationale: literal reuse of
  `feat.Updates`/`UpdateEntry` was never possible (different heading
  levels), and both the existing (`dec`) and in-flight (`vcr`) sibling
  domains at `sysrs`'s own H2/H3 nesting level independently chose the
  free-form/optional shape, not `feat`'s.
- **2026-08-30**: Cross-references to other domains will carry id +
  title + a very short agent-generated paraphrase, not embedded full
  content — rationale: avoids content drift between the System
  Specification and its source documents while still giving readers a
  quick sense of what's referenced without opening each document.
- **2026-08-30**: Section outline will be based on ISO/IEC/IEEE 29148's
  SyRS shape but tailored to specmgr's existing domains, not copied
  verbatim — rationale: 29148 is the actively maintained standard (vs.
  superseded IEEE 830/1233), and a verbatim import would include
  sections (e.g., "Logical database requirements", "Memory constraints")
  that don't map cleanly onto anything specmgr already models.
- **2026-08-30**: Domain key is `sysrs` (not `sys`/`spec`/`sss`) —
  rationale: keeps the "System Requirements Specification"/SyRS lineage
  visible in the key itself, consistent with how other domains'
  short keys map back to their source concept (e.g. `adr`, `rsk`), and
  avoids the genericness of `sys`/`spec` colliding in meaning with
  unrelated future domains.
- **2026-08-30**: Drop the `### <Name>` cross-reference sub-heading
  when an H2 holds exactly one list; keep it only where an H2 holds
  more than one distinct list (or a mix of free text and a list) —
  rationale: `example.v2.md` applied "every list gets a named H3"
  uniformly to every section, which produced sub-headings that just
  repeated their own H2's name with no added information (e.g. `## Risks` → `### Risks`); the rule now only earns its keep where it
  actually disambiguates multiple things under one H2 (currently just
  `## Business Context and Goals`).
- **2026-08-30**: Cross-reference bullets keep an inline title
  (`GOL-<id> + title`) after all, reversing `example.v2.md`'s draft
  "id-only" shape — rationale: consistent with `gol`/`dec`'s own
  existing `### Requirements`/`### Goals`/etc. lists, which already
  show the title inline today; dropping it would have been a
  regression in readability for no offsetting benefit once the
  `MarkdownListItemWithNotes` shape already accommodates a title
  in the lead line.
- **2026-08-30**: `## Architecture and Design Decisions`'s example
  entries reference `dec` only, not `adr` — scoped to this
  discussion-draft document's own illustrations, not a decision to
  deprecate the `adr` domain repo-wide (see Design Notes for the
  distinction).
- **2026-08-30**: Add `## Updates` (mandatory, newest-first,
  timestamped) and `## More Information` (optional, free text) as new
  `sysrs` sections, reusing `feat.Updates`/`feat.UpdateEntry`'s exact
  heading format and ordering validator rather than inventing a new
  shape — rationale: no reason to duplicate an already-built,
  already-tested class when `sysrs` needs the same "track changes to
  this document over time" capability `feat` already has.

### Related PRs / Commits

None yet.
