---
classification: null
created: '2026-11-05T06:53:20.701+01:00'
id: 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9
status: draft
type: txt
updated: '2026-11-10T09:43:08.413+01:00'
version: 1.0.0
---

# Architecture Review Checklist: Viewpoints x Perspectives

Reusable catalogue of review criteria for assessing a system architecture. It combines three lenses: architecture viewpoints (what is examined, in the sense of ISO/IEC/IEEE 42010, using the seven core viewpoints of Rozanski and Woods), perspectives (which property or constraint is judged: the nine ISO/IEC 25010:2023 product quality characteristics plus three perspectives from Rozanski and Woods), and assessment dimensions AD01 to AD15 (what kind of architectural merit is judged). Criteria are authored against the ISO/IEC/IEEE 29148 characteristics of a good requirement.

This document is the template and catalogue. The criteria are general and indexed by viewpoint. A completed review is a separate document that copies the criteria it uses and records rating, evidence and findings for the views of one specific system. Status of this draft: structure, applicability matrix, one worked example (Reliability x Deployment) and a design proposal for a model generation agent (section 11). The remaining cells are to be expanded later.

## 1. Purpose, Scope and Use

- Purpose: give reviewers a consistent, evidence-based way to assess an architecture description and the architecture it describes.
- Scope: architectures of software-intensive systems. Reviews of code, of single requirements and of project management are out of scope.
- Use: tailor the matrix (section 5) to the review scope, answer the criteria (section 6), rate them (section 7), and record findings and evidence (section 8).
- Generality: a viewpoint is generic and reusable. A view is the viewpoint applied to one system. Criteria stay general. Answers, evidence, targets and findings are specific to the system and belong in the review.
- Reviewers: a reviewer can be a person or an LLM agent. An LLM's reading or judgement of an artefact is never evidence by itself (section 8.2). It finds and interprets evidence. An agent that cannot obtain the evidence records it as missing.
- Authoring state: every statement about an external standard in this draft is marked "to be confirmed" in section 2, unless section 2 states that it was checked against the source text.

## 2. Sources and Provenance

| Source | Used for | Status |
|--------|----------|--------|
| ISO/IEC/IEEE 42010 | Viewpoint concept: concerns, stakeholders, model kinds, correspondences, rationale. Perspectives through shared models | The statement on perspectives is checked against clause 5.6 NOTE 1 of the standard, which cites R+W. The rest is to be confirmed against the standard |
| Rozanski and Woods, Software Systems Architecture, 2nd edition, Addison-Wesley, 2012 (R+W) | The seven core viewpoints (ch. 3 and 15 to 22), the perspective concept (ch. 4), the perspective catalogue (ch. 24 to 29) and the per-view applicability tables of each perspective | Names, definitions, concerns and applicability tables checked against the text of the book. The mapping decisions of this catalogue are our own |
| ISO/IEC 25010:2023 | Nine quality characteristics and their sub-characteristics. They are the first nine perspectives | Characteristic and sub-characteristic names checked against specmgr://iso25010 |
| ISO/IEC/IEEE 29148 | Characteristics of a well-formed requirement and of a requirement set, applied to checklist criteria | To be confirmed; it is a requirements standard and is applied here by analogy |
| ISO/IEC/IEEE 42030 | Architecture evaluation framework, possible alignment | Not yet checked |
| ISO/IEC 33020 (successor of ISO/IEC 15504, SPICE) | Capability levels 0 to 5 for practice criteria and the capability profile | Level names provisional, to be confirmed |
| ISACA COBIT | Possible replacement for the capability level names | Not yet checked; the current version and its level names are to be confirmed |
| Assessment dimensions AD01 to AD12 | Tag on each criterion, plus an architecture-level pass | Draft list collected from several interviews. No single reference. Do not cite as ISO |
| Assessment dimensions AD13 to AD15 | Necessity, economic viability, organisational fit | Added in this catalogue to close gaps in AD01 to AD12. AD14 and AD15 are carried by the DevelopmentResource perspective (section 5) |
| Viewpoint list VP01 to VP07 | The seven core viewpoints of R+W, in the order of the book | Checked against R+W. 42010 defines no viewpoint catalogue. The earlier list VP01 to VP13 (Draft 0.7 and before) was compiled from several practice sources and is mapped in section 4.1 |
| Perspective list FS to DR | The nine ISO/IEC 25010:2023 characteristics plus Regulation, Location and DevelopmentResource from R+W | The three added perspectives are the ones that ISO/IEC 25010 cannot express. Other R+W perspectives are mapped in section 5 |
| Martin, Clean Architecture | Dependency rule, component principles, boundaries | Principle source, to be confirmed |
| POSA, Enterprise Integration Patterns, Release It! | Architecture-level patterns and stability patterns | Pattern source, to be confirmed |
| Gamma et al., Design Patterns (GoF) | Class-level patterns, used only where they shape a seam | Pattern source, limited use |
| Saltzer and Schroeder | Protection design principles | Principle source, to be confirmed |

Note on the 42010 usage: 42010 expects viewpoints to be derived from stakeholder concerns. The viewpoint set in section 4 is therefore a starter set that each review must confirm or adjust. R+W say the same: not all viewpoints apply to every system, and a review can add others.

Note on perspectives: 42010 has no perspective concept. It handles cross-cutting concerns with models shared across views (42010 clause 5.6 NOTE 1, which cites R+W; R+W, ch. 4). This catalogue uses the R+W concept: a viewpoint guides the creation of a view, a perspective guides the design so that the system shows a quality property, and applying a perspective usually changes the views and creates no new ones.

## 3. Review Preconditions

A review cannot start meaningfully without these inputs. If one is missing, record it as a finding against AD01 Completeness and AD07 Verifiability.

- Scope and architecture baseline: name, version and date of what is reviewed.
- Review type: concept, pre-implementation, pre-release, or periodic health check. It decides which cells apply.
- Stakeholders and their concerns, as far as known.
- Constraints and assumptions: technical, organisational, financial, regulatory.
- Quality targets in measurable form, for example quality-attribute scenarios or a utility tree. Without a target, a perspective cannot be rated, so every home cell starts with a criterion that asks for the target (for Regulation and DevelopmentResource: the obligation or constraint).
- Safety relevance declared: yes or no, each with a one-line justification (see section 5).
- Practice evidence for the capability profile (section 7.3), as far as available.
- Review team, reviewers' independence and review date.

## 4. Viewpoints

The viewpoints VP01 to VP07 are the seven core viewpoints of Rozanski and Woods (R+W), in the order of the book. The names are the R+W names. The earlier list of Draft 0.7 and before had thirteen viewpoints (VP01 to VP13). Section 4.1 maps the old IDs to the new ones. The IDs were renumbered once, in Draft 0.8, while the catalogue contained only one worked example.

XV CrossView is not a viewpoint. It is a row of the matrix for criteria that no single view can hold, such as the security target and the threat model, the hazard analysis, the applicable regulations and the resource constraints. It is the home of the deep criteria of Security and Safety, which R+W treat as perspectives and not as viewpoints.

| ID | Viewpoint | Main concerns | Typical stakeholders | Typical model kinds |
|----|-----------|---------------|----------------------|---------------------|
| VP01 | Context | System scope and responsibilities, external entities, external interfaces (identity, nature, contract, partner), external interdependencies, impact of the system on its environment | All stakeholders, especially acquirers, users and developers | Context model (context diagram, actor and interface list), interaction scenarios |
| VP02 | Functional | Functional capabilities, functional elements and their responsibilities, internal structure, layering and dependencies between runtime elements, internal interfaces and connectors, functional design philosophy | All stakeholders, architects, developers | Functional structure model (component and layer diagram, interface catalogue, sequence diagrams, contracts), capability map, use case model |
| VP03 | Information | Information structure and content, ownership, identifiers, storage, flow, consistency, quality, latency and age, archiving and retention | Data architects, developers, compliance | Data model, data flow, ownership matrix |
| VP04 | Concurrency | Task structure (processes and threads), mapping of functional elements to tasks, interprocess communication, state management, synchronisation and integrity, startup and shutdown, task failure, reentrancy | Developers, testers, some administrators | Process model, state model, sequence models |
| VP05 | Development | Module organisation, source-level dependencies, common processing, standardisation of design and testing, instrumentation, codeline organisation, build and test environment | Developers, testers, release engineers, production engineers | Module structure model, common design model, codeline model, build and pipeline description |
| VP06 | Deployment | Runtime platform, hosting and hardware, third-party software, technology stack and compatibility, lock-in, network requirements and capacity, nodes, environments, topology, placement, redundancy, scaling, physical constraints | System administrators, infrastructure engineers, operations | Runtime platform model, network model, technology dependency model, deployment diagram, environment overview |
| VP07 | Operational | Installation and upgrade, functional and data migration, monitoring and control, alerting, logging, configuration management, backup and restore, support, incident handling, change and release, operation in third-party environments | System administrators, production engineers, support, service owners | Installation model, migration model, configuration management model, administration model, support model, runbooks, monitoring design |
| XV | CrossView | Targets, threats, hazards, applicable regulations, cost, time and skill constraints. Anything that spans all views | Security officers, safety engineers, compliance, sponsors, architects | Security target, threat model, hazard analysis, safety concept, regulation register, resource and constraint overview |

Interfaces: the old Integration/Interface viewpoint is split. An interface to an entity outside the system boundary belongs to VP01 Context. An interface between elements inside the system belongs to VP02 Functional. Both viewpoints keep "Interfaces" as a named concern group, so that interface criteria stay easy to find. How the deployment behaves when an external system is unavailable is assessed under VP06 x RE (see VP06-RE-140).

Boundaries between the remaining viewpoints:

- Functional and Development: Functional describes runtime elements. Development describes source modules. The dependency rule and the other source-level dependency principles (PR09 to PR11) are assessed in Development.
- Deployment and Operational: Deployment describes the environment. Operational describes how the system is run in it.
- Concurrency and performance: Concurrency holds the process and thread structure. Load behaviour is assessed under the Performance Efficiency perspective.

Each criterion carries exactly one primary viewpoint to avoid double counting.

Other viewpoints and topics are placed as follows:

- Evolution, Regulation, Privacy and Organisational concerns are perspectives (section 5), not viewpoints.
- Migration is part of VP07 Operational.
- Scenarios are a technique of R+W (ch. 10), used here to state quality targets. They are not a viewpoint.
- Business/Capability is not in the R+W set. VP01 Context holds the scope and responsibilities. A review can add a Business/Capability viewpoint if the concerns exist.

### 4.1 Mapping from the earlier viewpoint list

| Old ID | Old viewpoint | New |
|--------|---------------|-----|
| VP01 | Context | VP01 Context |
| VP02 | Functional | VP02 Functional |
| VP03 | Logical | VP02 Functional (runtime structure and layering), VP05 Development (source-level dependency rule) |
| VP04 | Information/Data | VP03 Information |
| VP05 | Application/Software | VP05 Development |
| VP06 | Integration/Interface | VP01 Context (external interfaces), VP02 Functional (internal interfaces and connectors), VP06 Deployment (behaviour when external systems fail) |
| VP07 | Technology/Infrastructure | VP06 Deployment |
| VP08 | Deployment | VP06 Deployment |
| VP09 | Security | Perspective SE. The deep criteria are in XV x SE |
| VP10 | Operational | VP07 Operational |
| VP11 | Development/Construction | VP05 Development. Team ownership and skills are in perspective DR |
| VP12 | Runtime/Process | VP04 Concurrency. Load behaviour is in perspective PE |
| VP13 | Safety | Perspective SA. The deep criteria are in XV x SA |

## 5. Applicability Matrix (Viewpoint x Perspective)

Status: provisional. The matrix is frozen after it has been validated against three contrasting architectures (see the linked QA).

The matrix separates three things. Perspectives describe which quality properties and constraints are assessed. Viewpoints describe where those properties become architecturally visible. Primary and secondary cells describe the assessment responsibility and depth.

Coordination principle: a perspective can be relevant across several viewpoints, but its assessment is coordinated to avoid duplicated criteria, inconsistent conclusions and gaps in coverage. Primary cells establish assessment responsibility. Secondary cells provide complementary evidence and cross-checks.

### 5.1 Perspectives

There are twelve perspectives. The first nine are the ISO/IEC 25010:2023 quality characteristics. They keep the ISO names, the ISO order and the ISO sub-characteristics. The last three are perspectives of R+W that ISO/IEC 25010 cannot express, because they describe constraints on the system and its environment and not properties of the product.

| Code | Perspective | Basis | Maps to R+W perspective |
|------|-------------|-------|-------------------------|
| FS | Functional Suitability | ISO/IEC 25010 | None. In R+W this is a concern of the Functional viewpoint itself |
| PE | Performance Efficiency | ISO/IEC 25010 | Performance and Scalability, without Scalability |
| CO | Compatibility | ISO/IEC 25010 | None. R+W treat interoperability through the Context and Functional viewpoints, technology compatibility in Deployment, and wide-area interoperability in Location |
| IC | Interaction Capability | ISO/IEC 25010 | Usability and Accessibility, and the language and culture part of Internationalization |
| RE | Reliability | ISO/IEC 25010 | Availability and Resilience |
| SE | Security | ISO/IEC 25010 | Security |
| MA | Maintainability | ISO/IEC 25010 | Evolution, in part |
| FL | Flexibility | ISO/IEC 25010 | Evolution, in part. Scalability of Performance and Scalability. The locale and unit adaptation part of Internationalization |
| SA | Safety | ISO/IEC 25010 | None. R+W mention safety only under Regulation (health and safety law). This is an extension of R+W |
| RG | Regulation | R+W | Regulation |
| LO | Location | R+W | Location |
| DR | DevelopmentResource | R+W | Development Resource |

Concerns in focus of the three added perspectives, from R+W:

- RG Regulation: statutory and industry regulation, privacy and data protection, cross-border legal restrictions, data retention and accountability, compliance with organisational policy. RG carries the assessment dimension AD11 Compliance.
- LO Location: time zones of operation, network link characteristics, resilience to link failure, wide-area interoperability, high-volume remote operations, intercountry concerns, use of the public Internet, physical variations between locations. It applies when elements or interacting systems are physically far from each other. A disaster recovery site counts.
- DR DevelopmentResource: time, cost, required skill sets, available resources, budgets, external dependencies. It covers whether the system can be designed, built, deployed and operated within known constraints of people, budget, time and materials. DR carries the assessment dimensions AD14 Economic viability and AD15 Organisational fit.

Decisions on the other R+W perspectives:

- Usability and Accessibility are part of IC. ISO Interaction Capability has the sub-characteristics Operability, Inclusivity, User Assistance and others.
- Internationalization is not a separate perspective. Language and culture independence of the interaction is assessed under IC (sub-characteristic Inclusivity). Adaptation to other locales, currencies and units is assessed under FL (sub-characteristic Adaptability).
- Scalability stays under Flexibility, as in ISO/IEC 25010. R+W group it with Performance. A review that follows R+W reads FL x Scalability together with PE.
- Evolution is split into MA and FL, as in ISO/IEC 25010.
- Each of RG, LO and DR has no ISO sub-characteristic. In a criterion record the R+W concern takes its place.

Perspective codes follow this order: the nine ISO/IEC 25010:2023 characteristics in ISO order, then RG, LO, DR.

Naming rule: the names of the viewpoints, of the row CrossView and of the perspectives added from R+W are single words without special characters (Concurrency, CrossView, DevelopmentResource), so that they can be used in IDs, tags and tool properties. The nine ISO names are kept as ISO writes them. "Development Resource" is the name in the book.

### 5.2 Matrix

Cell values:

- P: primary assessment responsibility. The cell holds the full set of criteria for the concerns of that viewpoint. It does not mean the whole perspective is assessed again in every primary cell.
- S: secondary assessment responsibility. The cell holds selected cross-check criteria that validate or complement the primary cells.
- X: no default criteria assigned. This is not a statement that the perspective is inapplicable to the system. A reviewer can activate the cell through tailoring.

| Viewpoint | FS | PE | CO | IC | RE | SE | MA | FL | SA | RG | LO | DR |
|-----------|----|----|----|----|----|----|----|----|----|----|----|----|
| VP01 Context | P | S | P | S | S | P | X | S | S | S | S | S |
| VP02 Functional | P | S | P | P | S | S | P | P | S | S | X | S |
| VP03 Information | S | S | P | S | P | P | S | S | S | P | S | S |
| VP04 Concurrency | S | P | S | X | P | S | S | S | S | X | S | S |
| VP05 Development | X | S | S | S | S | S | P | P | S | X | S | P |
| VP06 Deployment | X | P | P | X | P | P | S | P | S | X | P | S |
| VP07 Operational | X | P | S | S | P | S | P | P | S | S | S | P |
| XV CrossView | X | X | X | X | S | P | X | X | P | P | X | P |

Counts: 32 primary cells, 47 secondary cells and 17 cells without default criteria, 96 cells in total (eight rows and twelve columns). Every viewpoint and every perspective has at least one primary cell.

Home cells are the primary cells of the row XV CrossView: XV x SE (Security), XV x SA (Safety), XV x RG (Regulation) and XV x DR (DevelopmentResource). Home cells hold the deep criteria for that topic. Other viewpoints hold short cross-checks, for example Security x Context or Reliability x CrossView.

How the matrix was derived. The starting point was the matrix of Draft 0.7 (nine columns, thirteen rows), merged by the mapping of section 4.1. A mechanical merge, where the highest value wins, would have made VP02 Functional primary in seven of the nine ISO columns. It was not used. Each cell was decided again under the rule "one primary location for each concern". Where R+W give a per-view applicability table for a perspective (R+W Tables 25-1, 26-1, 27-1, 28-1 and 29-1 to 29-6), it was used as the guide: P where the viewpoint is the place where the concern is specified, S where it is a cross-check, X where R+W state little or no impact. FS, CO and SA have no R+W table. Their cells follow the earlier matrix. The cell by cell reasons are in the linked QA.

Rules for tailoring:

- Removing a primary cell needs a written one-line justification in the review record.
- Removing a secondary cell needs no justification, unless the review methodology requires that cross-check.
- Activating a X cell needs no justification. Record the reason if it adds assessment scope.
- Interaction Capability applies wherever the assessed product has user-facing, operator-facing, administrative or maintenance interfaces. If no relevant human interaction exists within the review scope, mark the perspective inapplicable once, with one scope-level justification.
- Location applies where elements or interacting systems are physically far from each other. If all of them are in one place, mark the perspective inapplicable once, with one scope-level justification. Check the disaster recovery site and the external systems first.
- Regulation applies to any system that can be subject to law, regulation or organisational policy. If none applies within the review scope, mark the perspective inapplicable once, with one scope-level justification.
- DevelopmentResource applies to every software project, because R+W state that all of them are constrained by time and cost. Its depth depends on the review type, for example a periodic health check puts more weight on operating capacity than on build constraints.
- Safety gate: the Safety perspective is opt-in. The review scope must state "safety relevant" or "not safety relevant", each with a one-line justification.
  - If safety relevant: the SA column is included, with its home cell XV x SA. Primary and secondary cells are assessed as the matrix shows. Removing an individual primary cell needs a justification.
  - If not safety relevant: the SA column is excluded. The justification is recorded at review-scope level.
  - Safety relevance is not decided only by direct control of physical equipment. Software that influences decisions or actions with possible safety consequences can be safety relevant.
  - A later change of the decision needs a new documented decision.
- The word inapplicable in this section describes a cell or perspective for a review scope. The applicability value Inapplicable (section 7.1) applies to a single criterion.
- Cell counts and markings are a first judgement. They stay provisional until the validation against three architectures is done.

## 6. Criterion Record

### 6.1 Record format

Each criterion is one record with these fields, each on one physical line.

- ID: viewpoint ID (VP01 to VP07, or XV for CrossView), perspective code and a three-digit number, for example VP06-RE-090. Numbers start at 090 and run in steps of 10 within each viewpoint and perspective pair. Numbers are permanent. They are never renumbered or reused. A retired criterion is marked deprecated. The viewpoint IDs themselves were renumbered once, in Draft 0.8 (section 4.1). From then on they are permanent as well.
- Viewpoint and perspective: with the ISO/IEC 25010:2023 sub-characteristic where one applies. For RG, LO and DR the R+W concern takes its place.
- Type: design or practice. A design criterion asks about a property of the architecture or its description. A practice criterion asks how the organisation works, for example how often a failover is tested.
- Primary assessment dimension: one AD tag (AD01 to AD15).
- Principle tags: zero or more PR tags from section 9.
- Question: phrased as "How", "Where" or "Show", not as a yes or no question.
- Expected evidence: the artefact types that answer the question.
- Applicability: Applicable or Inapplicable (section 7.1). Filled in during the review, not in the catalogue.
- Evidence: Sufficient, Insufficient or Missing (section 7.1). The minimum evidence level that makes evidence sufficient is not a field of the criterion. It comes from the policy table in section 8.2. Filled in during the review.
- Outcome: Satisfactory, Partially or Unsatisfactory (section 7.1). Filled in during the review.
- Rating: one word, derived from Applicability, Evidence and Outcome (section 7.1). Filled in during the review.
- Maturity: a capability level from section 7.2. Filled in during the review, for practice criteria only.
- Finding references: filled in during the review.

### 6.2 Authoring rules (ISO/IEC/IEEE 29148 characteristics applied to criteria)

A criterion enters the catalogue only if it passes all of these checks.

| Characteristic | Check for a criterion |
|----------------|-----------------------|
| Necessary | Removing it would leave a real architectural risk unexamined |
| Appropriate | Its level of detail fits the viewpoint and the review type |
| Unambiguous | Two reviewers read the question the same way. Terms such as "appropriate" or "manageable" are replaced by a stated target or a measurable proxy |
| Complete | It names its expected evidence and its pass condition |
| Singular | It asks one thing. Compound questions are split |
| Feasible | A reviewer can answer it with the available evidence and time |
| Verifiable | The answer can be checked against an artefact, a measurement or a test |
| Correct | It reflects a real stakeholder concern or constraint, not a reviewer preference |
| Conforming | It follows this record format and uses the shared tags |

Catalogue-level checks, from the 29148 characteristics of a requirement set, applied by analogy:

| Characteristic | Check for the catalogue |
|----------------|-------------------------|
| Complete | Every primary cell has criteria, and every home cell starts with a target criterion |
| Consistent | No two criteria conflict or restate each other. Each criterion has one primary viewpoint and one primary AD |
| Feasible | The criteria selected for one review type can be worked within the available time |
| Comprehensible | IDs, tags and rating words are defined once, in this document |
| Able to be validated | Each criterion names an evidence type that exists in practice |

Additional authoring rules:

- Do not presuppose a solution. Ask "Which workload and growth targets are stated, and how does the design meet them?" instead of "Is the system horizontally scalable?".
- Place each criterion under the perspective it measures. Scalability is under Flexibility (as in ISO/IEC 25010, although R+W group it with Performance). Load behaviour is under Performance Efficiency. Single points of failure are under Reliability.
- The first criterion of every home cell asks for the measurable target of that perspective. For Regulation it asks which obligations apply. For DevelopmentResource it asks which constraints are stated.
- Keep criteria general. A question that names a product or technology is system-specific and belongs in the review, or in a later technology-specific extension.

### 6.3 Assessment dimensions

The AD list is a draft collected from interviews. AD13 to AD15 were added in this catalogue. Each criterion carries one primary AD tag.

| ID | Dimension | Question |
|----|-----------|----------|
| AD01 | Completeness | Does the architecture address all relevant stakeholder concerns and requirements? |
| AD02 | Consistency | Are architectural elements, decisions and views consistent with each other? |
| AD03 | Correctness | Does the architecture correctly address the intended requirements and constraints? |
| AD04 | Feasibility | Can it be implemented within technical, organisational and financial constraints? |
| AD05 | Appropriateness | Is the solution appropriate for the system's context and complexity? |
| AD06 | Traceability | Can decisions be traced to requirements, concerns and constraints? |
| AD07 | Verifiability | Can architectural properties and claims be objectively verified? |
| AD08 | Modularity | Are responsibilities and components appropriately separated? |
| AD09 | Understandability | Is the architecture understandable to its intended stakeholders? |
| AD10 | Extensibility | Can it accommodate foreseeable changes? |
| AD11 | Compliance | Does it comply with applicable standards, regulations and principles? |
| AD12 | Risk management | Are architectural risks identified and adequately addressed? |
| AD13 | Necessity | Is every significant element and decision needed, with a stakeholder need or constraint behind it? |
| AD14 | Economic viability | Is the architecture economically viable over its life, including build, run and change cost? |
| AD15 | Organisational fit | Does the architecture fit the skills, structure and capacity of the organisation that builds and operates it? |

How the new dimensions differ from existing ones:

- AD13 asks per element and decision whether it is needed. AD05 asks whether the solution as a whole is right-sized. AD06 is the mechanism: an element that traces to nothing is a candidate for removal.
- AD14 asks whether the architecture is worth building and running. AD04 asks only whether it can be built within the constraints.
- AD15 asks whether the organisation can build and operate it. The capability profile (section 7.3) supplies the evidence.

Known issues with the AD list, to resolve in later drafts:

- AD01, AD03 and AD05 share names with the Functional Suitability sub-characteristics. Read them here as properties of the architecture, not of the product functions.
- AD08 Modularity and AD10 Extensibility restate Maintainability (Modularity) and Flexibility.

Relation of the dimensions to the perspectives: a perspective says which property or constraint is judged. A dimension says what kind of merit is judged. They are independent axes. Two dimensions have a natural home perspective: AD11 Compliance in Regulation (RG), and AD14 Economic viability and AD15 Organisational fit in DevelopmentResource (DR). A criterion in another perspective can carry these tags too.

### 6.4 Architecture-level pass

Run this short pass once per review, over the architecture description as a whole. A tag on a criterion cannot test these dimensions. For AD14 and AD15 the DevelopmentResource perspective holds the criteria on single views. This pass checks them once for the whole description.

| Dimension | Check |
|-----------|-------|
| AD01 Completeness | Are stakeholders, concerns and viewpoints identified, and is every concern covered by at least one view? |
| AD02 Consistency | Are correspondences between views recorded, and do names and elements agree across views? |
| AD06 Traceability | Does each significant decision link to a requirement, concern or constraint, and is the rationale recorded? |
| AD07 Verifiability | Does each quality claim name how it will be checked? |
| AD09 Understandability | Can a stakeholder from each audience find and read the views meant for them? |
| AD13 Necessity | Which elements and decisions have no stakeholder need or constraint behind them, and why do they remain? |
| AD14 Economic viability | Where are build cost, run cost, licence cost and cost of change estimated, and compared with the alternatives considered? |
| AD15 Organisational fit | Where are the skills, team ownership, governance and operating capacity needed for this architecture described, and how do they compare with what exists? |

## 7. Rating Scale

### 7.1 Ratings

Each criterion is recorded with three fields. Every value is a single word. The rating is derived from the three fields. It is not recorded separately.

| Field | Value | Meaning |
|-------|-------|---------|
| Applicability | Applicable | The criterion applies to this scope |
| Applicability | Inapplicable | The criterion does not apply to this scope. A one-line justification is mandatory |
| Evidence | Sufficient | Evidence at or above the minimum level of the policy table in section 8.2 exists, and it is current against the review baseline |
| Evidence | Insufficient | An artefact exists, but it is below the minimum level, too old, or not about this baseline |
| Evidence | Missing | No artefact exists. A claim that is only asserted counts as missing |
| Outcome | Satisfactory | The evidence shows that the criterion is met |
| Outcome | Partially | The evidence shows that the criterion is met in part, or met with a gap that is not critical |
| Outcome | Unsatisfactory | The evidence shows that the criterion is not met, or a critical gap exists |

Outcome is recorded only when Applicability is Applicable and Evidence is Sufficient. In all other cases it stays empty.

The rating is one of five words:

| Applicability | Evidence | Outcome | Rating |
|---------------|----------|---------|--------|
| Inapplicable | not recorded | empty | Inapplicable |
| Applicable | Insufficient or Missing | empty | Unassessable |
| Applicable | Sufficient | Satisfactory | Satisfactory |
| Applicable | Sufficient | Partially | Partially |
| Applicable | Sufficient | Unsatisfactory | Unsatisfactory |

Rules:

- Apply the fields in this order: Applicability first, then Evidence, then Outcome.
- Record evidence before the rating (section 8.2).
- A finding is mandatory for the ratings Partially, Unsatisfactory and Unassessable. An Unassessable finding is recorded against AD01 or AD07 and states whether the evidence is insufficient or missing. The severity of a finding does not define the rating.
- Do not average ratings. Ratings are ordinal. Report the count per rating.
- This catalogue does not define knock-out criteria. Which criteria are critical depends on the organisation and the architecture. The final evaluation of a review decides this for its specific environment.
- A criticality weight, if used, is a separate attribute of the criterion and is never built into the rating.

### 7.2 Maturity of practices

The rating says whether a practice meets the criterion today. Maturity says how repeatably the organisation performs it. They are different axes, and both are recorded for practice criteria. Design criteria carry no maturity level.

The level names start with ISO/IEC 33020 and are provisional. The ISACA COBIT level names may replace them once confirmed.

| Level | Name | Meaning |
|-------|------|---------|
| 0 | Incomplete | The practice is not performed, or does not achieve its purpose |
| 1 | Performed | The practice achieves its purpose, informally |
| 2 | Managed | The practice is planned and monitored, and its work products are controlled |
| 3 | Established | The practice follows a defined standard process, tailored to the case |
| 4 | Predictable | The practice operates within measured limits |
| 5 | Innovating | The practice is improved continuously against quantitative objectives |

### 7.3 Capability profile

Each review records one capability profile. It is required. It rates the organisation's practice areas on the 0 to 5 scale of section 7.2, with the evidence behind each level. Do not average the levels. Report the profile as a list. The profile is the main evidence for AD15 Organisational fit.

The practice areas below are a proposal. The final list is to be agreed.

| Practice area | Related viewpoint | Level (0 to 5) | Evidence |
|---------------|-------------------|----------------|----------|
| Architecture governance | XV | | |
| Decision management and decision records | XV | | |
| Traceability from requirements to architecture | XV | | |
| Architecture evaluation and conformance checking | VP05 | | |
| Security engineering practice | XV (SE) | | |
| Operations and incident learning | VP07 | | |
| Change, release and deployment | VP07 | | |
| Skills and ownership | XV (DR) | | |

## 8. Findings and Evidence

### 8.1 Finding record

- ID: unique within the review.
- Type: strength, weakness, risk, recommendation, sensitivity point, trade-off point, assumption, open question, or non-risk.
- Severity: critical, major, minor or info.
- Link: criterion ID, with its viewpoint, perspective and AD tag.
- Description: one or two sentences.
- Risk fields, for type risk: likelihood and impact, linked to AD12. A risk finding can be recorded as a separate risk document.
- Recommendation and owner. A recommendation that is a decision can be recorded as a separate decision document.
- Status: open, accepted, mitigated or closed.

### 8.2 Evidence record

- Evidence level, ordered from weakest to strongest. Each level is one word:
  - Documented: an authored artefact states the fact, for example a diagram, a design document or an ADR.
  - Demonstrated: a result that someone else can reproduce by running the same check or exercise again, for example a prototype, a test of the claim, a failover exercise, or a scripted query over code or configuration.
  - Measured: a result produced by the running system or by automated checks, repeatedly, for example continuous measurements, load test results, or automated conformance tests.
- Asserted only, with nothing to inspect, is not an evidence level. Record it as Evidence Missing (section 7.1).
- A review, an opinion, or the reading of an artefact by a person or an LLM is not a level. A reviewer can use reading to find and interpret evidence. The level of the evidence is the level of the artefact or result that was read.
- Producer: who produced the evidence. Author (the authors of the architecture wrote it), Human (a person ran an exercise or test), Pipeline (an automated process runs it repeatedly), or Tool (a check was run during this review).
  - Documented evidence has the producer Author.
  - Demonstrated evidence has the producer Human or Tool.
  - Measured evidence has the producer Pipeline, or the producer Tool when the check repeats.
  - An LLM agent can reach Demonstrated or Measured only through the producer Tool, with a check that is recorded so that it can be run again, for example a model parse, a dependency graph and cycle check, or a query for nodes with one instance. Such a check supports structure claims only, not quality targets. For evidence from the producer Human or Pipeline, such as a load test, a failover test or a penetration test, the agent only reads the report and checks its provenance.
- Provenance: artefact name, version and date, relative to the review baseline. For the producer Tool, also the command or query and its result.
- Minimum evidence policy. The minimum level that makes Evidence Sufficient depends on the review type (section 3) and on the criterion type (section 6.1). The values are provisional, to be confirmed against real reviews.

| Review type | Design criterion | Practice criterion |
|-------------|------------------|--------------------|
| Concept | Documented | Documented |
| Pre-implementation | Documented | Documented |
| Pre-release | Documented | Demonstrated |
| Periodic health check | Demonstrated | Measured |
- Typical artefacts: architecture diagrams, design documents, ADRs, configuration information, threat models, service level objectives, capacity and load test results, disaster recovery and failover test results, runbooks, dependency graphs and software bills of materials, penetration test reports, architecture conformance tests or fitness functions, measurements.
- Record evidence before the rating. The rating Unassessable depends on it.

## 9. Principle Tags

Principles are tags on criteria, not a separate axis. The original list of twelve principles is merged here, because several overlap.

| Tag | Principle | Origin and note |
|-----|-----------|-----------------|
| PR01 | Separation of concerns, single responsibility, high cohesion | Merges three overlapping items from the original list |
| PR02 | Loose coupling, minimise dependencies | Merges two overlapping items |
| PR03 | Encapsulation, information hiding | Merges two nearly identical items |
| PR04 | Explicit interfaces | Original list |
| PR05 | Design for change | Original list. Counterweight: PR15 |
| PR06 | Defence in depth | Original list |
| PR07 | Fail-safe defaults | Original list, Saltzer and Schroeder |
| PR08 | Least privilege | Original list, Saltzer and Schroeder |
| PR09 | Dependency rule: source dependencies point inward, towards policy | Clean Architecture |
| PR10 | Acyclic dependencies between components | Clean Architecture, component principles |
| PR11 | Stable dependencies and stable abstractions | Clean Architecture. Instability and abstractness metrics give measurable evidence |
| PR12 | Policy separated from detail, independence of frameworks, UI and database | Clean Architecture |
| PR13 | Economy of mechanism, complete mediation | Saltzer and Schroeder |
| PR14 | Stability patterns: timeouts, circuit breaker, bulkhead, idempotency, graceful degradation | Release It! |
| PR15 | Simplicity, no speculative generality | Counterweight to PR05. Tie the tension to AD05 Appropriateness and AD13 Necessity |
| PR16 | Observability | Operational concern |
| PR17 | Single source of truth, explicit data ownership | Data concern |
| PR18 | Project-specific principles | Slot for the organisation's own architecture principles, referenced by AD11 |

Pattern sources by viewpoint, for use as reference points and not as requirements:

- Functional and Development: POSA layers, pipes and filters, microkernel. GoF Adapter, Facade, Strategy, Mediator, Observer only where they shape a seam.
- Context and Functional, for interfaces: Enterprise Integration Patterns, ports and adapters, GoF Adapter and Proxy.
- Deployment and Concurrency: cloud design patterns, Release It! stability patterns.

Anti-pattern checks, used as prompts in the relevant cells: big ball of mud, distributed monolith, shared-database integration, god component, vendor lock-in, golden hammer, pattern overuse.

## 10. Worked Example: Deployment x Reliability (VP06 x RE)

Cell type: primary. Sub-characteristics in focus: Availability, Fault Tolerance, Recoverability. This example replaces the single-point-of-failure question that was originally filed under Performance Efficiency. Criterion numbers start at 090 and run in steps of 10.

### VP06-RE-090 Availability and recovery targets

- Type: design.
- Sub-characteristic: Availability.
- Primary AD: AD07 Verifiability.
- Principle tags: none.
- Question: Where are the availability target and the recovery targets (recovery time and recovery point) stated, and for which operating hours?
- Expected evidence: quality-attribute scenarios, service level objectives, requirements.

### VP06-RE-100 Single points of failure

- Type: design.
- Sub-characteristic: Availability.
- Primary AD: AD12 Risk management.
- Principle tags: PR14.
- Question: Show for each deployment node and shared service what happens to the stated availability target if it fails, and which ones have no redundant counterpart.
- Expected evidence: deployment diagram, failure mode analysis, dependency list.

### VP06-RE-110 Failure domains

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD03 Correctness.
- Principle tags: PR14.
- Question: How are redundant instances placed across independent failure domains such as host, zone and region, and which failure domains are shared?
- Expected evidence: deployment diagram, infrastructure configuration, placement rules.

### VP06-RE-120 Failure detection and failover

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD07 Verifiability.
- Principle tags: PR14, PR16.
- Question: How is a failed node detected, how long does failover take, and where is the failover behaviour defined?
- Expected evidence: health check configuration, failover design, monitoring design.

### VP06-RE-130 Recovery of state and data

- Type: design.
- Sub-characteristic: Recoverability.
- Primary AD: AD03 Correctness.
- Principle tags: PR17.
- Question: Where is state and data kept in the deployment, how is it backed up and restored, and how does the restore time compare with the stated recovery targets?
- Expected evidence: backup and restore design, restore test results, data placement map.

### VP06-RE-140 Dependencies outside the deployment

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD12 Risk management.
- Principle tags: PR14, PR02.
- Question: Which external systems must be available for the system to meet its target, and how does the deployment behave when each one is unavailable?
- Expected evidence: interface catalogue, timeout and retry configuration, degradation design.

### VP06-RE-150 Failure tests

- Type: practice.
- Sub-characteristic: Fault Tolerance and Recoverability.
- Primary AD: AD07 Verifiability.
- Principle tags: none.
- Question: Which failure and recovery scenarios have been tested in a production-like environment, how often, and with what result?
- Expected evidence: failover test report, disaster recovery exercise report, chaos test results.

### Example rating records

Design criterion:

- Criterion: VP06-RE-100.
- Review type: pre-release. The minimum level for a design criterion is Documented.
- Evidence: deployment diagram version 1.4 (Documented, producer Author), no failure mode analysis.
- Applicability: Applicable.
- Evidence field: Sufficient. The diagram meets the minimum level and is current against the baseline.
- Outcome: Partially. The diagram shows two application nodes and one database node without a replica.
- Rating: Partially.
- Finding F-03: weakness, major. The database node is a single point of failure for the stated availability target. Recommendation: add a replica or lower the target and record the decision.
- Finding F-04: open question. No failure mode analysis exists for the shared message broker.

Practice criterion:

- Criterion: VP06-RE-150.
- Review type: pre-release. The minimum level for a practice criterion is Demonstrated.
- Evidence: one failover test report from the last release (Demonstrated, producer Human). No recurring schedule.
- Applicability: Applicable.
- Evidence field: Sufficient. In a periodic health check the minimum level is Measured, and the same evidence would be Insufficient. The rating would then be Unassessable.
- Outcome: Partially. A test was done once. The expected frequency is not met.
- Rating: Partially.
- Maturity: 1 Performed. The practice achieves its purpose, informally.
- Finding F-05: weakness, minor. Failover tests have no schedule and no owner.

## 11. Model Generation Agent (C4 and Structurizr)

This section describes an agent that creates architecture models in the Structurizr DSL (C4 model) from existing source code or from specmgr artifacts. The models are input evidence for a review. Status: design proposal, not implemented. Open items are tracked in the linked QA.

The criteria in sections 6 to 10 stay tool neutral and name no product. Product names appear only in this section.

### 11.1 Scope and Boundary

- The agent creates one or more Structurizr workspaces, a facts file for each, and a gaps report.
- The agent does not review. It records no rating, outcome, finding, maturity or capability profile. A modeler that judges its own model grades itself.
- A separate review agent reads the workspaces and applies sections 6 to 10. It is out of scope here.
- A C4 model is evidence for some viewpoints only. Section 11.6 lists which. The gaps report lists the viewpoints that the model cannot show. For those viewpoints the review agent finds Evidence Missing, so the rating is Unassessable.

### 11.2 Inputs and Outputs

- Input, source code: one or more repository paths.
- Input, specmgr artifacts: one or more artifact IDs, for example a SYSRS and the REQ, UC, DEC, ADR, RSK and GOL documents it references.
- Input, intake answers: the preconditions of section 3 as far as they are known. At least the baseline, the review type, the safety relevance declaration and the stakeholders.
- Output, facts file: one structured file per system. It holds every element and relationship with origin and provenance (section 11.4).
- Output, workspace: one DSL file per workspace.
- Output, gaps report: unmodelled viewpoints, open questions, elements with the origin Inferred or Proposed, and the check results.
- Proposed location: `diagrams/c4/<system>/`. To be confirmed.

### 11.3 Design Principles

- Separate extraction from emission. Both inputs produce the same facts file. One writer turns the facts file into DSL. Two writers would drift apart.
- No element without provenance. No relationship without provenance, unless its origin is Inferred.
- Never fill a gap silently. A missing fact becomes an open question in the gaps report.
- Stay at container level and component level where the evidence allows it. Do not model code level.
- The origin of a model element and the evidence level of a quality claim (section 8.2) are different things. Do not mix them. The origin tells how the element got into the model. The evidence level tells how strongly a claim about the architecture is supported.

### 11.4 Origin and Provenance

Every element and relationship in the facts file carries one origin and one provenance.

| Origin | Meaning |
|--------|---------|
| Extracted | Found directly in a source file or in a specmgr artifact. The provenance names the file and line, or the artifact ID |
| Inferred | Derived by reasoning from several extracted facts. The provenance names those facts and states the reasoning. It needs confirmation |
| Proposed | Not found anywhere. Suggested by the agent to close a structural gap, or derived from a requirement or decision. It is a target, not a fact |

- Elements and relationships with the origin Inferred or Proposed carry a tag in the workspace. A style makes the tag visible in every view.
- A model built from specmgr artifacts consists mostly of Proposed elements, because requirements and decisions describe intent, not structure. The workspace documentation states that it is a target architecture proposal.
- The properties `origin` and `provenance` are set on every element and relationship. A model-level property holds the safety relevance declaration and its justification (section 11.6).

### 11.5 Components

Agents, in `.opencode/agent/`:

| Agent | Task | Access |
|-------|------|--------|
| c4-modeler | Orchestrator. Runs the phases of section 11.7 and writes the workspace and the gaps report | Read and write |
| c4-source-extractor | Source code to facts file. Can run once per container, so a large repository fits in the context | Read only |
| c4-specmgr-extractor | specmgr artifacts to facts file | Read only |
| c4-model-checker | Validates the workspace, runs the inspections and compares a sample of facts with the source | Read only |

Skills, in `.opencode/skills/`. A skill holds knowledge, not behaviour, and loads on demand:

| Skill | Content |
|-------|---------|
| c4-structurizr-dsl | DSL syntax and conventions: identifiers, views, styles, tags, properties, deployment, perspectives, the validation and export tools |
| c4-from-source | How to find containers, components, relationships and external systems in code. Containers come from compose files, Kubernetes manifests, Dockerfiles and build manifests. Relationships come from HTTP, queue and database clients. External systems come from environment variables and SDKs. Where to stop |
| c4-from-specmgr | The mapping from specmgr artifact types to C4 constructs. UC actors become persons. REQ items about interfaces and compatibility become external systems. DEC and ADR become documentation and properties. Everything is Proposed unless an artifact states a structure |
| c4-viewpoint-mapping | The mapping of section 11.6 and the property conventions |
| c4-model-quality | The checks of section 11.8 as modelling rules, including the severity setting per inspection |

Commands, in `.opencode/command/`:

| Command | Effect |
|---------|--------|
| `/c4 source <path...>` | Runs the flow of section 11.7 for source code |
| `/c4 specmgr <id...>` | Runs the flow of section 11.7 for specmgr artifacts |

### 11.6 Viewpoints and C4 Views

The mapping is many to many, because C4 is not based on viewpoints.

| C4 view | Supports |
|---------|----------|
| System context, system landscape | VP01 Context. A landscape view is a candidate for a Business/Capability viewpoint |
| Container | VP02 Functional (runtime elements) and VP06 Deployment (technology), partly VP05 Development |
| Component | VP02 Functional, partly VP05 Development |
| Dynamic | VP04 Concurrency, and sequence evidence for the interfaces of VP01 Context and VP02 Functional |
| Deployment, with instance counts and health checks | VP06 Deployment, partly VP07 Operational |
| Relationship description and technology | Interface catalogue of VP01 Context (external) and VP02 Functional (internal) |
| Groups, tags and properties | Trust boundaries (XV x SE), failure domains (VP06), safety relevance declaration (XV x SA) |

C4 has no native construct for VP03 Information. Functional capabilities (what the system does for its users) are not modelled either, only the structure that provides them. VP05 Development is covered in part only (technology and component structure, not build, test or codeline). VP07 Operational is covered in part only (health checks, infrastructure nodes). The row XV CrossView is not modelled: the security target, the threat model, the hazard analysis, the regulation register and the resource constraints need other evidence. Quality targets, ratings, maturity levels and the capability profile are not modelled. The agent can reference such evidence through properties. It does not create it.

Property conventions, verified with Structurizr 2026.10.26 (see the linked QA):

| Key | Placed on | Note |
|-----|-----------|------|
| `failure.domain.host`, `failure.domain.zone`, `failure.domain.region` | Deployment nodes, infrastructure nodes, container instances | One key per level. Set each key once, on the node of that level. A reader walks the hierarchy, because children do not inherit properties |
| `trust.boundary` | Elements and deployment nodes. Never on a group | A group can hold no properties. The group name is for display only. A check compares the group name with the property |
| `trust.boundary.crossing` | Explicit relationships | Cross-check only. The authoritative crossing is derived from the boundaries of the two endpoints |
| `review.safety.relevant`, `review.safety.justification` | Model | |
| `origin`, `provenance` | Elements and relationships | `origin` has the closed values of section 11.4 |

- Keys use only `[a-z0-9.]` and are case sensitive. Values are never empty.
- Properties appear only in the JSON export. The PlantUML and Mermaid exports drop them. A query script over the JSON export is the authoritative reader.
- Structurizr does not check the values. The check script of section 11.8 reports values that occur once and conflicts between a parent and a child.

### 11.7 Flow

| Phase | Actor | Result | Gate |
|-------|-------|--------|------|
| 1 Intake | c4-modeler | Intake answers, list of workspaces to create | Missing answers are recorded as open questions. They are never guessed |
| 2 Extract | c4-source-extractor or c4-specmgr-extractor | Facts file per system | Every item has origin and provenance |
| 3 Plan | c4-modeler | Workspaces, views, list of viewpoints that the model cannot show | The plan states the review type and the baseline |
| 4 Emit | c4-modeler | Workspace DSL per plan | Inferred and Proposed items are tagged and styled |
| 5 Check | c4-model-checker | Check results | Workspace parses, inspections are run, a sample of facts matches the source. Failures go back to phase 4. After a fixed number of attempts the run stops and reports |
| 6 Report | c4-modeler | Gaps report | Lists unmodelled viewpoints, open questions, Inferred and Proposed items |

Rules for the phases:

- Phase 1: the agent asks the user for the review type, the baseline (name, version, date), the safety relevance with a one-line justification, the stakeholders, and whether one or many workspaces are wanted.
- Phase 2: with source code, extract per container and merge the results. With specmgr artifacts, follow the references of the given IDs and read each artifact once.
- Phase 3: split workspaces by system and team boundary, not by viewpoint. Create one workspace per software system with one owning team. Create a landscape workspace only if there is more than one system. A review overlay is a separate workspace and needs `workspace extends`, which is not yet tested.
- Phase 5: the checker never edits the workspace. It only reports.

### 11.8 Checks and Evidence

The checks of phase 5 support the architecture-level pass of section 6.4. They have the producer Tool (section 8.2). They are recorded with their command and result, so that someone else can run them again. They support structure claims only. They do not support quality targets.

| Check | Supports |
|-------|----------|
| Workspace parses without errors | Evidence for all views is Documented, from a valid model |
| Disconnected element | AD01, AD02 |
| Element in no view | AD13 |
| Software system with containers but no decisions | AD06 |
| Software system or container without documentation | AD09 |
| Container without technology, relationship without description | AD07 |
| Property check over the JSON export: shared failure domains, boundary crossings, unset values, values that occur once, parent and child conflicts, group name against `trust.boundary` | VP06 failure domains, XV x SE trust boundaries, AD02 |
| Sample of facts compared with the source | Correctness of the extraction, not of the architecture |

- The default severity of the inspections is error. Set the severity per inspection before the run.
- A view from a valid model is Documented. A recorded inspection is Demonstrated. An inspection that a pipeline runs repeatedly is Measured.
- A deployment node with an instance count of one and no replica is visible in the model. This supports VP06-RE-100 and VP06-RE-120.

## 12. Related Documents

QA 25bd5b93-a228-4d6c-8b70-d143dfd39444: Architecture Review Checklist: Decisions and Open Items

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-10 08:42:00.000Z - Draft 0.8

Aligned the catalogue with Rozanski and Woods (R+W), checked against the text of the book (2nd edition). Reduced the viewpoints from thirteen to the seven R+W core viewpoints, renumbered VP01 to VP07 with the R+W names: Context, Functional, Information, Concurrency, Development, Deployment, Operational. Security (old VP09) and Safety (old VP13) are no longer viewpoints. They are perspectives, as in R+W. Added the row XV CrossView for criteria that span all views, and made it the home of the deep criteria of Security, Safety, Regulation and DevelopmentResource. Section 4.1 maps the old IDs to the new ones. Renamed the axis "quality characteristic" to "perspective". The nine ISO/IEC 25010:2023 characteristics keep their ISO names and order. Added three R+W perspectives that ISO/IEC 25010 cannot express: Regulation (RG), Location (LO) and DevelopmentResource (DR). Usability and Accessibility are part of IC. Internationalization is covered by IC and FL. Scalability stays under FL. Rebuilt the matrix: 8 rows, 12 columns, 96 cells (32 P, 47 S, 17 X). Every cell was decided again, with the R+W per-view applicability tables as the guide. Home cells are now XV x SE, XV x SA, XV x RG and XV x DR. The Safety gate now switches the SA perspective. AD11, AD14 and AD15 are linked to the perspectives RG and DR. Added R+W to the sources (section 2). The worked example VP08 x RE is now VP06 x RE (criteria VP06-RE-090 to VP06-RE-150). Updated the capability profile, the pattern sources and the C4 mapping. The old viewpoint to new viewpoint table is in section 4.1. The cell by cell reasons are in the linked QA.

### 2026-11-06 07:40:00.000Z - Draft 0.7

Verified the property conventions of section 11.6 with Structurizr 2026.10.26. `trust.boundary` moves from groups to elements and deployment nodes, because a group cannot hold properties. Failure domains use one key per level. Added `trust.boundary.crossing` as a cross-check key and the rules for keys and values. Added the property check to section 11.8. The results are in the linked QA.

### 2026-11-06 07:15:22.000Z - Draft 0.6

Added section 11, a design proposal for a model generation agent that creates Structurizr C4 workspaces from source code or specmgr artifacts: scope and boundary, inputs and outputs, design principles, origin and provenance, agents, skills and commands, viewpoint to C4 view mapping, the six-phase flow, and the checks. Related Documents is now section 12. The version was removed from the title.

### 2026-11-06 07:13:32.411Z - Draft 0.6

Remove draft version from title.

### 2026-11-06 07:10:32.000Z - Draft 0.5

Title version aligned with the update log. Replaced the evidence codes E0 to E3 with the named levels Documented, Demonstrated and Measured. Dropped E0: asserted-only evidence is Evidence Missing. Demonstrated and Measured now require a result that someone else can reproduce. A reading by a person or an LLM is not a level. Added the Producer attribute (Author, Human, Pipeline, Tool) and a statement on what an LLM agent can reach. Removed the per-criterion field "Minimum evidence strength". Added a minimum evidence policy by review type and criterion type in section 8.2. Replaced the single Rating field by Applicability, Evidence and Outcome. The five rating words are derived from them. Removed the dependence of the rating on finding severity. Removed the knock-out rules from section 7.1. Updated the worked example.

### 2026-11-05 07:50:00.000Z - Draft 0.4

Replace "dash" with "X" in matrix and description.

### 2026-11-05 07:45:00.000Z - Draft 0.3

Applied the review of the applicability matrix. The X now means "no default criteria assigned". Redefined P and S. Added removal rules for secondary cells and activation rules for X cells. Replaced the Interaction Capability rule so that operators and administrators count as human interaction. Rewrote the Safety gate. Changed VP11 x SA from a X to S. Added the coordination principle and the provisional status. Added cell counts for secondary cells and X cells (30 P, 68 S, 19 X).

### 2026-11-05 07:12:00.000Z - Draft 0.2

Applied review feedback. Criterion IDs changed to viewpoint-first form (VP08-RE-090, numbers start at 090, step 10). Added AD13 Necessity, AD14 Economic viability and AD15 Organisational fit, and renamed the description-quality pass to the architecture-level pass. Rating words reduced to single words. Added criterion type (design or practice), maturity levels for practice criteria, and a per-review capability profile. Added catalogue-level checks. Moved the open items to the linked QA.

### 2026-11-05 05:53:20.701Z - Created

First draft: structure, viewpoint set, applicability matrix, criterion record format, rating scale, finding and evidence formats, principle tags, and one worked example (Reliability x Deployment).
