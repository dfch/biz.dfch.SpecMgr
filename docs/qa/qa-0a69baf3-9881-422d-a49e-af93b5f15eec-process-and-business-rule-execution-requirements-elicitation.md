---
classification: null
created: '2026-10-06T15:11:18.090+02:00'
id: 0a69baf3-9881-422d-a49e-af93b5f15eec
status: draft
type: qa
updated: '2026-10-06T15:11:18.090+02:00'
version: 1.0.0
---

# Process and Business Rule Execution — Requirements Elicitation

## General

### Introduction

This Q&A session documents the initial scoping conversation for the
"Process and Business Rule Execution" initiative, held on 2026-10-06. It
began as a plan-mode exploration: the ten raw requirements below were
captured first, followed by a research pass over controlled-natural-language
(CNL) approaches and FOSS rule/process engines, then a first round of
clarifying questions answered directly by the initiator. That round is
recorded under `Elicitation Context` below. The nine ISO/IEC 25010:2023
quality-characteristic sections that follow record the deeper, still
largely open, architecture questions this initiative must resolve before
any implementation work starts. This interview backs the companion goal,
GOL 361a523d-bd30-4585-adac-3f6f3800aece.

### Raw Requirements

The following ten points were provided verbatim by the initiator at the
start of the conversation and are preserved here for traceability:

1. A user can define business rules as text in (controlled) natural
   language.
2. The agent uses a skill/agent to check the text and convert it to
   machine-readable syntax.
3. The agent uses a library/deterministic parser that validates the
   syntax.
4. The agent visualizes the rules.
5. The rules can be loaded into a rule engine and executed by a user.
6. A common type system is wanted: a core type system (similar to normal
   programming languages) plus a custom, user-specified type system
   (example given: based on e-CH-0278), understood by the agent, the
   parser, and the rule engine together, so that an agent/other component
   can validate that transitions between rule steps are possible.
7. Standards should be used. DMN and BPMN were suggested as candidates,
   with the question left open for other suggestions, or a complete
   custom DSL instead.
8. FOSS is mandatory for all components.
9. A bidirectional mechanism is needed to sync from CNL to executable
   code and back.
10. A subset of the chosen standard(s) might be used, rather than the
    full standard.

## Elicitation Context

<!-- First clarifying round, held in plan mode on 2026-10-06, before any document was written. -->

> **0.0010**: Where should the planning artifacts (GOL/QA/REQ/ADR/SYSRS)
> for this initiative live?

In this same specmgr instance's existing `docs/` tree (not a new sibling
repository), reusing the GOL/QA/REQ/ADR/SYSRS domains directly.

> **0.0020**: What is the v1 scope: full BPMN process orchestration plus
> DMN decisions together, or decisions/rules only first?

BPMN process orchestration and DMN decision logic together, from day one;
not a decisions-only v1.

> **0.0030**: Which FOSS engine should be prototyped first?

Left open for further discussion. GoRules `zen-engine` was confirmed
(during research) to be a decision/rules engine only, with no BPMN/process
orchestration support, so it cannot alone satisfy a combined BPMN+DMN v1.
Drools was raised as sounding like "the most complete solution." The two
realistic, single-engine, standards-complete FOSS candidates identified so
far are Flowable (Apache-2.0, one coherent BPMN+CMMN+DMN product) and
Apache Kie (Drools+jBPM, Apache Software Foundation-governed since its
2023 incubation). See `More Information` for the full comparison; this
remains an open ADR-level decision pending a short spike/prototype.

> **0.0040**: Is eCH-0278 (the Swiss E-Tax NP data model) the real,
> concrete first domain to target, or just an illustrative example?

Just an illustrative example. The real target domain is open; the type
system must stay generically pluggable rather than being built around
Swiss tax law specifically.

> **0.0050**: Who authors the controlled-natural-language rule text?

Both humans and the agent. Whenever a human edits CNL text (new or
existing), the agent normalizes/canonicalizes it before the deterministic
parser validates it -- the agent is not only a free-text-to-CNL converter,
but also a CNL-to-CNL normalizer on every human edit.

> **0.0060**: What is the preferred implementation stack for the new
> rule-engine/CNL project?

Python is preferred but not required, because the engine will likely be
implemented in a new/different MCP server rather than inside
`biz.dfch.SpecMgr` itself.

TODO: check again

> **0.0070**: Is there a concrete pain point driving this initiative (so
> that a Problem Statement should be written), or is this purely proactive
> capability-building?

TODO: answer pending

> **0.0080**: Who else should be consulted (legal/compliance subject-matter
> experts, prospective business-rule authors, downstream engine
> integrators) before the architecture decisions below are finalized?

TODO: answer pending

## Functional Suitability

<!-- The end-to-end pipeline implied by raw requirements 1-5 and 9. -->

> **1.0010**: Can you walk through the exact pipeline end-to-end: free
> text to agent conversion, to deterministic parser, to visualization, to
> engine execution? Where exactly does the agent's CNL-normalization pass
> (confirmed in Elicitation Context 0.0050) sit relative to the
> deterministic parser -- always immediately before it, on every save, or
> only on demand?

TODO: answer pending

> **1.0020**: What, concretely, counts as "the agent visualizes the
> rules" (raw requirement 4) -- a static, generated diagram export (for
> example, mirroring this repository's own UC-to-PlantUML pipeline), or
> an interactive, editable graph canvas (for example, a JDM-editor-style
> tool)?

TODO: answer pending

> **1.0030**: What does "the rules can be loaded into a rule engine and
> executed by a user" (raw requirement 5) mean operationally: an
> interactive single-decision query tool, a batch run over a dataset, or
> an embedded call from another host application?

TODO: answer pending

> **1.0040**: Must every executed decision/process instance produce an
> audit trail (inputs, matched rules, outputs, timestamps) for
> traceability or compliance, or is that out of scope for v1?

TODO: answer pending

> **1.0050**: Should individual business rules or process steps be
> versioned independently, so that one rule can change without touching
> unrelated rules?

TODO: answer pending

## Performance Efficiency

> **2.0010**: What throughput/latency does the system need: interactive
> (sub-second, a human waiting for an answer), batch (for example,
> nightly runs over large datasets), or both?

TODO: answer pending

> **2.0020**: What is the expected scale of a typical rule set: a handful
> of rules, dozens, or hundreds?

TODO: answer pending

## Compatibility

> **3.0010**: Must the system export and import standards-conformant
> DMN/BPMN XML, for portability and to avoid lock-in to one engine's
> native format, even if the chosen engine's internal format differs?

TODO: answer pending

> **3.0020**: Does this system need to interoperate with any existing
> BPMN/DMN assets already authored in another tool, or is everything
> authored fresh through the new CNL pipeline?

TODO: answer pending

## Interaction Capability

> **4.0010**: Besides the initiator, who else authors CNL rule text in
> practice: developers only, business/legal domain experts without a
> coding background, or both equally?

TODO: answer pending

> **4.0020**: Is an interactive visual graph/decision-table editor (for
> example, a JDM-editor-style tool) a v1 requirement, or is CNL text plus
> generated, read-only diagrams sufficient for v1?

TODO: answer pending

## Reliability

> **5.0010**: When the deterministic parser cannot unambiguously validate
> a piece of CNL (the whole purpose of raw requirement 3), must it refuse
> and report the exact problem rather than silently guessing -- is
> "fail loud, never fail silent" a hard requirement?

TODO: answer pending

> **5.0020**: If the agent's CNL-normalization pass (Elicitation Context
> 0.0050) changes the meaning of what a human wrote, should the system
> always show a diff for human confirmation before accepting it?

TODO: answer pending

## Security

> **6.0010**: Are there any data-classification or confidentiality
> requirements on the rules themselves, or on the data they operate over,
> that the architecture must account for from the start?

TODO: answer pending

> **6.0020**: Who is authorized to deploy a validated rule set into the
> executing engine: the same person who authored it, or a separate
> review/approval step?

TODO: answer pending

## Maintainability

> **7.0010**: Should each business rule be independently unit-testable
> with its own scenario-based test cases (mirroring this repository's own
> verification-case-record artifact type), separate from testing the
> process/decision graph as a whole?

TODO: answer pending

> **7.0020**: Should there be a formal traceability link from a specmgr
> requirement/verification-case-record artifact in this repository to a
> concrete rule/process asset id in the new engine, so that a question
> like "which rule implements this requirement?" is answerable?

TODO: answer pending

## Flexibility

> **8.0010**: How pluggable must the custom type system be: must it
> support several independent domain type packs active at once (for
> example, a tax domain pack and a health-insurance domain pack in the
> same deployment), or is one domain pack per deployment acceptable?

TODO: answer pending

> **8.0020**: For the DMN/BPMN "subset" (raw requirement 10), which
> concrete elements are must-have for v1 (for example, exclusive/parallel
> gateways, the Business Rule Task, simple decision tables), and which
> are explicitly out of scope (for example, timer events, sub-processes,
> multi-instance activities, the full S-FEEL expression language)?

TODO: answer pending

## Safety

> **9.0010**: Are any of the business rules/processes this system will
> eventually run expected to be safety- or legally-critical (for example,
> automated decisions with direct financial, legal, or regulatory
> consequences for a person), requiring mandatory human sign-off before
> execution?

TODO: answer pending

> **9.0020**: If the chosen FOSS engine or its governance changes
> unfavorably in the future (as happened when Camunda moved from the
> Apache-2.0-licensed Camunda 7 to the commercially licensed Camunda 8),
> what is the organization's tolerance for migrating to a different
> engine? Must the canonical-model-plus-renderers architecture (raw
> requirement 9) make engine swaps cheap by design?

TODO: answer pending

## More Information

A first research pass, done before this document was created, compared:

- **Controlled natural language approaches**: Attempto Controlled English
  (ACE, FOSS since 1995, University of Zurich, with the deterministic APE
  parser producing first-order-logic discourse representation structures)
  and OMG SBVR (Semantics of Business Vocabulary and Business Rules, the
  closest formal standard to "CNL in, formal rules out," though its FOSS
  tooling is thin).
- **Standards**: OMG DMN (decision tables, Decision Requirements Diagrams,
  the FEEL expression language, Item Definitions as a lightweight custom
  type mechanism; the cDMN extension adds typed predicates/constraint
  reasoning) and OMG BPMN (process orchestration; its Business Rule Task
  is the documented integration point with DMN).
- **FOSS rule/process engines**:
  - GoRules `zen-engine` (MIT, Rust core with Python/Node/Go/Java/.NET
    bindings) is a decision/rules engine only -- it has no BPMN/process
    orchestration. Its newest ("Policy documents" plus "workspace
    analysis": static type checking across policies and graphs, type
    flow, exhaustiveness checking) is the closest existing proof-of-concept
    of raw requirement 6 found anywhere, and is worth studying as a
    reference design even if not adopted as the engine. Its contribution
    model is centrally controlled by GoRules Inc. despite the MIT license.
  - Drools, now part of Apache Kie (Apache-2.0, donated to the Apache
    Software Foundation's Incubator in 2023), is a mature Java rules
    engine; BPMN/process orchestration is covered by the sibling jBPM
    project under the same Apache Kie umbrella.
  - Flowable (Apache-2.0, Java) is one coherent product combining BPMN,
    CMMN, and DMN engines, stably open source for over a decade.
  - Operaton (Apache-2.0, Java) is a 2024/2025 community fork of Camunda
    7's BPMN 2.0 + DMN 1.3 engine, created specifically in reaction to
    Camunda's commercial pivot to Camunda 8; youngest of the four, with
    the smallest track record.

  No engine has been selected; Elicitation Context 0.0030 and Safety
  9.0020 both bear on this choice, which should be an ADR following a
  short spike/prototype comparing at least Flowable and Apache Kie.

- **Architecture pattern reuse from this repository**: this repository's
  own ADR on the parse-validate-render pipeline (no AST-preserving
  round-trip) is a direct precedent for raw requirement 9's bidirectional
  CNL/executable sync -- never text-diff two generated artifacts against
  each other; keep one canonical model as the single source of truth, and
  treat both the CNL text and the DMN/BPMN export as projections
  (renderers) of that one model. This repository's UC-to-PlantUML diagram
  pipeline is a similar precedent for raw requirement 4 (visualization as
  a generated projection, not a hand-drawn diagram).
