---
classification: null
created: '2026-11-05T06:53:20.701+01:00'
id: 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9
status: draft
type: txt
updated: '2026-11-22T23:30:00.000+01:00'
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
| ISO/IEC/IEEE 42010:2011 | Viewpoint concept: concerns, stakeholders, model kinds, correspondences, rationale. Perspectives through shared models | Checked against the text (2026-11-18): the concepts viewpoint (clause 5.4), view (5.5), model (5.6), correspondence (5.7) and rationale (5.8), the term model kind (definitions), and clause 5.6 NOTE 1 on perspectives, which cites R+W. Annex B.3 cites the 1st edition of R+W (six viewpoints, no Context viewpoint) |
| Rozanski and Woods, Software Systems Architecture, 2nd edition, Addison-Wesley, 2012 (R+W) | The seven core viewpoints (ch. 3 and 15 to 22), the perspective concept (ch. 4), the perspective catalogue (ch. 24 to 29) and the per-view applicability tables of each perspective | Names, order and concern lists of the viewpoints, and the names of the ten perspectives, checked against the text of the book (2026-11-18). The per-view tables of the perspectives (Tables 25-1 to 28-1, 29-1 to 29-6) are prose and hold no ratings. The only rating grid is Table 4-1. The mapping decisions and the P, S, X values of this catalogue are our own interpretation |
| ISO/IEC 25010:2023 | Nine quality characteristics and their sub-characteristics. They are the first nine perspectives | Characteristic and sub-characteristic names checked against specmgr://iso25010. The original standard is not in the docs repository |
| ISO/IEC/IEEE 29148:2018 | Characteristics of a well-formed requirement and of a requirement set, applied to checklist criteria | The nine characteristics of an individual requirement (clause 5.2.5) and the five characteristics of a set (clause 5.2.6) checked against the text (2026-11-18). It is a requirements standard and is applied here by analogy |
| ISO/IEC/IEEE 42030 | Architecture evaluation framework, possible alignment | Missing. The standard is not in the docs repository. It is only cited in the texts of 12207 and 15288 |
| TOGAF 9.1 (The Open Group) | Business Architecture view and its artifacts (ch. 8, 35), architecture compliance reviews and compliance levels (ch. 48), the ACMM maturity model (ch. 51) | Checked against the markdown copy in the sibling docs repository (2026-11-22). Used for the Business/Capability note in section 4, the precondition on requester and sign-off in section 3, and the note in section 7.3 |
| ISACA COBIT 2019 (COBIT 2019 Framework: Introduction and Methodology, section 6.4) | Process capability levels 0 to 5 for practice criteria, focus area maturity levels 0 to 5 for the capability profile, and the achievement rating Fully, Largely, Partially, Not (section 7.2) | Checked against the markdown copy in the sibling docs repository (2026-11-22), Figures 6.2 and 6.3. COBIT states that its scheme largely aligns to and extends CMMI Development V2.0. The CMMI model text itself is not in the docs repository. ISO/IEC 33020 is no longer used |
| Assessment dimensions AD01 to AD12 | Tag on each criterion, plus an architecture-level pass | Draft list collected from several interviews. No single reference. Do not cite as ISO |
| Assessment dimensions AD13 to AD15 | Necessity, economic viability, organisational fit | Added in this catalogue to close gaps in AD01 to AD12. AD14 and AD15 are carried by the Resources perspective (RS, section 5) |
| Viewpoint list VP01 to VP07 | The seven core viewpoints of R+W, in the order of the book | Names and order checked against R+W. The concern lists are the book's and are in the Architecture Model TXT, section 4.1. 42010 defines no viewpoint catalogue. The earlier list VP01 to VP13 (Draft 0.7 and before) was compiled from several practice sources and is mapped in section 4.1 |
| Perspective list FS to RS | The nine ISO/IEC 25010:2023 characteristics plus Regulation, Location and Resources from R+W | The three added perspectives are the ones that ISO/IEC 25010 cannot express. Other R+W perspectives are mapped in section 5 |
| Martin, Clean Architecture, Pearson, 2018 (Martin) | The principle tags PR09 to PR12: the Dependency Rule (ch. 22), the component principles and their metrics (ch. 14), policy and level (ch. 19 and 20), boundaries and details (ch. 17, 18 and 30 to 32). Also treated there: PR01 (ch. 7), PR02 (ch. 14 and 16), PR03 (ch. 8), PR05 (ch. 15 and 16) | Checked against the markdown copy in the sibling docs repository (2026-11-18). The chapter numbers are those of the book. The line references are in the Architecture Model TXT, sections 3.3, 3.4 and 6.1. Martin states the principles as his own approach. They are not part of an ISO standard. His metrics are indicators and not thresholds. The tags PR09 to PR12 are a library and not adopted principles (section 9) |
| POSA, Enterprise Integration Patterns, Release It! | Architecture-level patterns and stability patterns | Pattern source, to be confirmed |
| Gamma et al., Design Patterns (GoF) | Class-level patterns, used only where they shape a seam | Pattern source, limited use |
| Saltzer and Schroeder | Protection design principles | Principle source, to be confirmed |
| IEC 61508, ISO 26262-8, ISO 12100 | Hazard types and tool qualification in the Safety gate (section 5.2) | Missing, to be confirmed |

Note on the 42010 usage: 42010 expects viewpoints to be derived from stakeholder concerns. The viewpoint set in section 4 is therefore a starter set that each review must confirm or adjust. R+W say the same: not all viewpoints apply to every system, and a review can add others.

Note on perspectives: 42010 has no perspective concept. It handles cross-cutting concerns with models shared across views (42010 clause 5.6 NOTE 1, which cites R+W; R+W, ch. 4). This catalogue uses the R+W concept: a viewpoint guides the creation of a view, a perspective guides the design so that the system shows a quality property, and applying a perspective usually changes the views and creates no new ones.

## 3. Review Preconditions

A review cannot start meaningfully without these inputs. If one is missing, record it as a finding against AD01 Completeness and AD07 Verifiability.

- Scope and architecture baseline: name, version and date of what is reviewed. For a product with variants, the baseline also names the variant in scope (hardware or build configuration). A review of a product line names the variants in scope and models one deployment environment for each. If the system ships more than one deployment descriptor (for example Docker Compose and Helm), the scope names the one that is reviewed, or each one is a separate deployment environment.
- System class: local tool, enterprise application, distributed platform, cyber-physical system, or another class with a stated name. The class sets the default tailoring of section 3.1.
- Subject: product or installation. For a product, VP06 and VP07 assess the reference deployment and the deployment capabilities, and target criteria ask for the targets the product supports, not the targets of one operation.
- Intended operating profile: production, production-lite, demonstration or prototype. It does not change a rating. It is the context for the final evaluation (section 7.1).
- Multi-tenant: yes or no. Yes means that one installation serves several tenants whose data, users or capacity must stay separate. If yes, the tenancy criteria of section 10 apply (VP02-SE-090, VP03-SE-090, VP06-PE-090, VP06-RE-170).
- Extension interface: yes or no. Yes means that third-party code (plugins, extensions) runs inside the system's processes. If yes, the extension criteria of section 10 apply (VP02-SE-100, VP02-CO-090, VP05-MA-090).
- Review type: concept, pre-implementation, pre-release, or periodic health check. It decides which cells apply.
- Stakeholders and their concerns, as far as known.
- Constraints and assumptions: technical, organisational, financial, regulatory.
- Quality targets in measurable form, for example quality-attribute scenarios or a utility tree. Without a target, a perspective cannot be rated, so every home cell starts with a criterion that asks for the target (for Regulation and Resources: the obligation or constraint).
- Safety relevance declared: yes or no, each with a one-line justification (see section 5).
- Practice evidence for the capability profile (section 7.3), as far as available.
- Review team, reviewers' independence and review date.
- Requester and objectives of the review, and who accepts the result (sign-off). Following the architecture compliance review process of TOGAF 9.1 (ch. 48).

### 3.1 Default tailoring by system class

The defaults below come from the Phase 120 validation (issue 267). A review can change a default with a one-line justification in the review record. The defaults never remove the target criterion of a home cell.

| System class | Default tailoring |
|--------------|-------------------|
| Local tool | VP06 x RE and VP07 x RE: only the target, state recovery and external dependency criteria (VP06-RE-090, -130, -140). VP06-RE-110 is Inapplicable when the scope has exactly one failure domain by design. LO: inapplicable once, unless the scope includes remote services. Where the runtime calls are the source calls, VP05 holds the MA criteria and VP02 x MA cross-checks only (section 4) |
| Enterprise application | VP03 x MA in full (shared data model). RG applies (personal and financial data). VP06 and VP07 follow the subject: for a product, the reference deployment |
| Distributed platform | Every RE cell applies. VP06 x FL in full (scalability by instances). VP04 x RE in full (delivery guarantees, compensation). Every shipped deployment descriptor is a separate deployment environment |
| Cyber-physical system | Safety gate decided explicitly, usually "safety relevant". The deployment view is mandatory. VP04 x SA is assessed in full. IC includes operator signals on the hardware. LO includes field sites |

## 4. Viewpoints

The viewpoints VP01 to VP07 are the seven core viewpoints of Rozanski and Woods (R+W), in the order of the book. The names are the R+W names. The earlier list of Draft 0.7 and before had thirteen viewpoints (VP01 to VP13). Section 4.1 maps the old IDs to the new ones. The IDs were renumbered once, in Draft 0.8, while the catalogue contained only one worked example.

XV CrossView is not a viewpoint. It is a row of the matrix for criteria that no single view can hold, such as the security target and the threat model, the hazard analysis, the applicable regulations and the resource constraints. It is the home of the deep criteria of Security and Safety, which R+W treat as perspectives and not as viewpoints.

The concerns of each viewpoint are the concerns of the book. They are quoted in TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model), section 4.1, and are not repeated here. The earlier paraphrases in this section differed from the book in six of the seven viewpoints. The topics that they added are placed in section 4.3 of that document. The stakeholder and model kind columns below are working lists of this catalogue. They are not quotations of the book.

| ID | Viewpoint | Typical stakeholders | Typical model kinds |
|----|-----------|----------------------|---------------------|
| VP01 | Context | All stakeholders, especially acquirers, users and developers | Context model (context diagram, actor and interface list), interaction scenarios |
| VP02 | Functional | All stakeholders, architects, developers | Functional structure model (component and layer diagram, interface catalogue, sequence diagrams, contracts), capability map, use case model |
| VP03 | Information | Data architects, developers, compliance | Data model, data flow, ownership matrix |
| VP04 | Concurrency | Developers, testers, some administrators | Process model, state model, sequence models |
| VP05 | Development | Developers, testers, release engineers, production engineers | Module structure model, common design model, codeline model, build and pipeline description |
| VP06 | Deployment | System administrators, infrastructure engineers, operations | Runtime platform model, network model, technology dependency model, deployment diagram, environment overview |
| VP07 | Operational | System administrators, production engineers, support, service owners | Installation model, migration model, configuration management model, administration model, support model, runbooks, monitoring design |
| XV | CrossView | Security officers, safety engineers, compliance, sponsors, architects | Security target, threat model, hazard analysis, safety concept, regulation register, resource and constraint overview |

Interfaces: both VP01 Context and VP02 Functional list interfaces among the book concerns. A criterion has one primary viewpoint. The catalogue rule is: a criterion about the external entity side (identity, responsibilities and nature of the interface to an entity outside the system boundary) belongs to VP01. A criterion about the connectors and the handling of interfaces between elements inside the system belongs to VP02. Both viewpoints keep "Interfaces" as a named concern group, so that interface criteria stay easy to find. How the deployment behaves when an external system is unavailable is assessed under VP06 x RE (see VP06-RE-140). The handling of input from outside the system boundary (authentication, authorisation, validation of input, protection against injection and forgery) is VP02 x SE, a primary cell. An extension interface for third-party code that runs inside the process is VP02, with SE as the deciding perspective.

Boundaries between the remaining viewpoints:

- Functional and Development: Functional describes runtime elements. Development describes source modules. VP02 x MA assesses the coupling of runtime elements: calls, events, dispatch by name, shared data. VP05 x MA assesses source dependencies. Where the runtime calls are the source calls (one process, direct function calls), VP05 holds the MA criteria and VP02 x MA only cross-checks. Where runtime coupling is not visible in the source (dispatch by name, events, shared data), both cells hold criteria. The dependency rule and the other source-level dependency principles (PR09 to PR12) are assessed in Development. This is our interpretation. Martin states the principles for source code and for deployable units, and gives no viewpoint. The assignment of PR12 follows the same reasoning, because Martin treats the separation of policy from detail as a direction of source dependencies (ch. 19 and 22). A C4 model alone is no evidence for PR09 and PR10 (Architecture Model TXT, section 3.4).
- Deployment and Operational: Deployment describes the environment. Operational describes how the system is run in it.
- Concurrency and performance: Concurrency holds the process and thread structure. Load behaviour is assessed under the Performance Efficiency perspective.

Each criterion carries exactly one primary viewpoint to avoid double counting.

Other viewpoints and topics are placed as follows:

- Evolution, Regulation, Privacy and Organisational concerns are perspectives (section 5), not viewpoints.
- Migration is part of VP07 Operational.
- Scenarios are a technique of R+W (ch. 10), used here to state quality targets. They are not a viewpoint.
- Business/Capability is not in the R+W set. VP01 Context holds the scope and responsibilities. A review can add a Business/Capability viewpoint if the concerns exist. TOGAF 9.1 gives a Business Architecture view guideline, not a full viewpoint (ch. 35). Its Phase B artifacts (ch. 8: catalogs, matrices and diagrams such as Functional Decomposition, Business Footprint and Business Service/Information) can serve as the model kinds of such an added viewpoint.

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
| VP11 | Development/Construction | VP05 Development. Team ownership and skills are in perspective RS |
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
| RS | Resources | R+W | Development Resource, re-scoped to the full lifecycle (catalogue extension) |

Concerns in focus of the three added perspectives, from R+W:

- RG Regulation: statutory and industry regulation, privacy and data protection, cross-border legal restrictions, data retention and accountability, compliance with organisational policy. RG carries the assessment dimension AD11 Compliance.
- LO Location: time zones of operation, network link characteristics, resilience to link failure, wide-area interoperability, high-volume remote operations, intercountry concerns, use of the public Internet, physical variations between locations. It applies when elements or interacting systems are physically far from each other. A disaster recovery site counts.
- RS Resources: time, cost, required skill sets, available resources, budgets, external dependencies. It covers whether the system can be designed, built, deployed and operated within known constraints of people, budget, time and materials. The R+W counterpart is the Development Resource perspective, development-view centric in the book; this catalogue re-scopes it to the full lifecycle, which is the catalogue extension recorded in the Architecture Model TXT. RS carries the assessment dimensions AD14 Economic viability and AD15 Organisational fit.

Decisions on the other R+W perspectives:

- Usability and Accessibility are part of IC. ISO Interaction Capability has the sub-characteristics Operability, Inclusivity, User Assistance and others.
- Internationalization is not a separate perspective. Language and culture independence of the interaction is assessed under IC (sub-characteristic Inclusivity). Adaptation to other locales, currencies and units is assessed under FL (sub-characteristic Adaptability).
- Scalability stays under Flexibility, as in ISO/IEC 25010. R+W group it with Performance. A review that follows R+W reads FL x Scalability together with PE.
- Evolution is split into MA and FL, as in ISO/IEC 25010.
- Each of RG, LO and RS has no ISO sub-characteristic. In a criterion record the R+W concern takes its place.

Perspective codes follow this order: the nine ISO/IEC 25010:2023 characteristics in ISO order, then RG, LO, RS.

Naming rule: the names of the viewpoints, of the row CrossView and of the perspectives added from R+W are single words without special characters (Concurrency, CrossView, Resources), so that they can be used in IDs, tags and tool properties. The nine ISO names are kept as ISO writes them. "Development Resource" is the name in the book.

### 5.2 Matrix

Cell values:

- P: primary assessment responsibility. The cell holds the full set of criteria for the concerns of that viewpoint. It does not mean the whole perspective is assessed again in every primary cell.
- S: secondary assessment responsibility. The cell holds selected cross-check criteria that validate or complement the primary cells.
- X: no default criteria assigned. This is not a statement that the perspective is inapplicable to the system. A reviewer can activate the cell through tailoring.

| Viewpoint | FS | PE | CO | IC | RE | SE | MA | FL | SA | RG | LO | RS |
|-----------|----|----|----|----|----|----|----|----|----|----|----|----|
| VP01 Context | P | S | P | S | S | P | X | S | S | S | S | S |
| VP02 Functional | P | S | P | P | S | P | P | P | P | S | X | S |
| VP03 Information | S | S | P | S | P | P | P | S | S | P | S | S |
| VP04 Concurrency | S | P | S | X | P | S | S | S | S | X | S | S |
| VP05 Development | X | S | S | S | S | S | P | P | S | X | S | P |
| VP06 Deployment | X | P | P | X | P | P | S | P | P | X | P | S |
| VP07 Operational | X | P | S | S | P | S | P | P | S | S | S | P |
| XV CrossView | X | X | X | X | S | P | X | X | P | P | X | P |

Counts: 36 primary cells, 43 secondary cells and 17 cells without default criteria, 96 cells in total (eight rows and twelve columns). Every viewpoint and every perspective has at least one primary cell.

Home cells are the primary cells of the row XV CrossView: XV x SE (Security), XV x SA (Safety), XV x RG (Regulation) and XV x RS (Resources). Home cells hold the deep criteria for that topic. Other viewpoints hold short cross-checks, for example Security x Context or Reliability x CrossView.

How the matrix was derived. The starting point was the matrix of Draft 0.7 (nine columns, thirteen rows), merged by the mapping of section 4.1. A mechanical merge, where the highest value wins, would have made VP02 Functional primary in seven of the nine ISO columns. It was not used. Each cell was decided again under the rule "one primary location for each concern". The derivation is our interpretation. The R+W per-view tables (R+W Tables 25-1, 26-1, 27-1, 28-1 and 29-1 to 29-6) hold prose and no ratings. Where R+W give such a table for a perspective, it was used as the guide: P where the viewpoint is the place where the concern is specified, S where it is a cross-check, X where R+W state little or no impact. FS, CO and SA have no R+W table. Their cells follow the earlier matrix. The cell by cell reasons are in the linked QA. After the validation against four systems (Phase 120, issue 267), four cells changed from S to P: VP02 x SE (the main input-handling controls landed in an S cell in three of four systems), VP03 x MA (the shared data model is the strongest coupling of an enterprise application), and VP02 x SA and VP06 x SA (the safety design of a cyber-physical system). VP03 x FL stays S: scalability by data volume or by instances depends on the system class (section 3.1).

Rules for tailoring:

- Removing a primary cell needs a written one-line justification in the review record.
- Removing a secondary cell needs no justification, unless the review methodology requires that cross-check.
- Activating a X cell needs no justification. Record the reason if it adds assessment scope.
- Interaction Capability applies wherever the assessed product has user-facing, operator-facing, administrative or maintenance interfaces. If no relevant human interaction exists within the review scope, mark the perspective inapplicable once, with one scope-level justification.
- Location applies where elements or interacting systems are physically far from each other. If all of them are in one place, mark the perspective inapplicable once, with one scope-level justification. Check the disaster recovery site and the external systems first. Legal differences between countries are RG. LO keeps the physical and network differences.
- Regulation applies to any system that can be subject to law, regulation or organisational policy. If none applies within the review scope, mark the perspective inapplicable once, with one scope-level justification.
- Resources applies to every software project, because R+W state that all of them are constrained by time and cost. It covers build and operating constraints. Its depth depends on the review type, for example a periodic health check puts more weight on operating capacity than on build constraints.
- Safety gate: the Safety perspective is opt-in. The review scope must state "safety relevant" or "not safety relevant", each with a one-line justification.
  - If safety relevant: the SA column is included, with its home cell XV x SA. Primary and secondary cells are assessed as the matrix shows. Removing an individual primary cell needs a justification.
  - If not safety relevant: the SA column is excluded. The justification is recorded at review-scope level.
  - Safety relevance is not decided only by direct control of physical equipment. Software that influences decisions or actions with possible safety consequences can be safety relevant.
  - A system that emits or controls energy that can harm people is safety relevant: radio frequency, electrical, thermal or mechanical energy.
  - The justification names the protected party: people, equipment or the environment. Protection of equipment alone does not satisfy the SA column.
  - A development tool can be safety relevant through its output, when that output is used in a safety-relevant system (tool qualification, for example IEC 61508-3 and ISO 26262-8, to be confirmed).
  - If SA is included, a conflict between RE and SA (keep running against stop safely) is recorded as a trade-off point (section 8.1). SA wins, unless a recorded decision says otherwise.
  - A later change of the decision needs a new documented decision.
- The word inapplicable in this section describes a cell or perspective for a review scope. The applicability value Inapplicable (section 7.1) applies to a single criterion.
- Cell counts and markings are a first judgement. They stay provisional until the validation against three architectures is done.

### 5.3 Comparison with R+W Table 4-1

The P, S and X values are our interpretation. R+W give no rating for every cell. Their per-view tables of the perspectives (Tables 25-1 to 28-1 and 29-1 to 29-6) hold prose, one paragraph for each view. The only rating grid in the book is Table 4-1 (High, Medium, Low, "typical" applicability). It covers four perspectives. The book offers it as an example for your own grid and not as a norm. The table below compares it with our matrix. A difference is not an error. It needs a reason or a change.

| Perspective | Viewpoint | R+W Table 4-1 | Our cell | Remark |
|-------------|-----------|---------------|----------|--------|
| SE | VP01 Context | Medium | P | Judgement call. P because of the one primary location rule (external connections), not because of the impact |
| SE | VP03 Information | Medium | P | Sensitive data. Same reason |
| SE | VP06 Deployment | High | P | Same |
| PE | VP05 Development | Low | S | Taken from the R+W text on performance guidelines for developers |
| PE | VP07 Operational | Low | P | The book concern Performance monitoring is in VP07 |
| RE | VP01, VP02, VP05 | Low | S | Cross-checks from the R+W text (external availability, offline operation, start and stop for failover) |
| RE | VP03 Information | Low | P | Backup, recovery and consistency. Judgement call |
| MA and FL (Evolution) | VP03 Information | High | P and S | Decided after the validation (Phase 120): MA became P (shared data model). FL stays S, because scalability depends on the system class |
| FL (Evolution, Scalability) | VP06 Deployment | Low | P | Scalability and installability sit in FL. The book groups scalability with Performance |
| MA and FL (Evolution) | VP07 Operational | Low | P and P | Installation, upgrade and migration are Operational concerns in the book |
| MA | VP01 Context | Medium | X | FL is S for the same view. Check if MA needs an S |

All other cells of the four perspectives agree with the ordering of the book (High corresponds to P or S, Low to S or X). The check is part of the validation of QA 25bd5b93, items 0.0340, 0.0350 and 0.0550.

## 6. Criterion Record

### 6.1 Record format

Each criterion is one record with these fields, each on one physical line.

- ID: viewpoint ID (VP01 to VP07, or XV for CrossView), perspective code and a three-digit number, for example VP06-RE-090. Numbers start at 090 and run in steps of 10 within each viewpoint and perspective pair. Numbers are permanent. They are never renumbered or reused. A retired criterion is marked deprecated. The viewpoint IDs themselves were renumbered once, in Draft 0.8 (section 4.1). From then on they are permanent as well.
- Viewpoint and perspective: with the ISO/IEC 25010:2023 sub-characteristic where one applies. For RG, LO and RS the R+W concern takes its place.
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
| Complete | Every primary cell has criteria, and every home cell starts with a target criterion (for SA: the hazard analysis) |
| Consistent | No two criteria conflict or restate each other. Each criterion has one primary viewpoint and one primary AD |
| Feasible | The criteria selected for one review type can be worked within the available time |
| Comprehensible | IDs, tags and rating words are defined once, in this document |
| Able to be validated | Each criterion names an evidence type that exists in practice |

Additional authoring rules:

- Do not presuppose a solution. Ask "Which workload and growth targets are stated, and how does the design meet them?" instead of "Is the system horizontally scalable?".
- Place each criterion under the perspective it measures. Scalability is under Flexibility (as in ISO/IEC 25010, although R+W group it with Performance). Load behaviour is under Performance Efficiency. Single points of failure are under Reliability.
- The first criterion of every home cell asks for the measurable target of that perspective. For Regulation it asks which obligations apply. For Resources it asks which constraints are stated.
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
| AD08 | Modularity (deprecated) | Deprecated on 2026-11-22. The Maintainability perspective (MA, sub-characteristic Modularity) carries it. Not used for new criteria, never reused |
| AD09 | Understandability | Is the architecture understandable to its intended stakeholders? |
| AD10 | Extensibility (deprecated) | Deprecated on 2026-11-22. The Flexibility perspective (FL, sub-characteristic Adaptability) carries it. Not used for new criteria, never reused |
| AD11 | Compliance | Does it comply with applicable standards, regulations and principles? |
| AD12 | Risk management | Are architectural risks identified and adequately addressed? |
| AD13 | Necessity | Is every significant element and decision needed, with a stakeholder need or constraint behind it? |
| AD14 | Economic viability | Is the architecture economically viable over its life, including build, run and change cost? |
| AD15 | Organisational fit | Does the architecture fit the skills, structure and capacity of the organisation that builds and operates it? |

How the new dimensions differ from existing ones:

- AD13 asks per element and decision whether it is needed. AD05 asks whether the solution as a whole is right-sized. AD06 is the mechanism: an element that traces to nothing is a candidate for removal.
- AD14 asks whether the architecture is worth building and running. AD04 asks only whether it can be built within the constraints.
- AD15 asks whether the organisation can build and operate it. The capability profile (section 7.3) supplies the evidence.

Resolved overlaps with ISO/IEC 25010 (QA 0.0250):

- AD01, AD03 and AD05 share names with the Functional Suitability sub-characteristics. Read them here as properties of the architecture, not of the product functions.
- AD08 Modularity and AD10 Extensibility restated the perspectives Maintainability and Flexibility. They are deprecated; a criterion names the perspective instead.

Relation of the dimensions to the perspectives: a perspective says which property or constraint is judged. A dimension says what kind of merit is judged. They are independent axes. Two dimensions have a natural home perspective: AD11 Compliance in Regulation (RG), and AD14 Economic viability and AD15 Organisational fit in Resources (RS). A criterion in another perspective can carry these tags too.

### 6.4 Architecture-level pass

Run this short pass once per review, over the architecture description as a whole. A tag on a criterion cannot test these dimensions. For AD14 and AD15 the Resources perspective holds the criteria on single views. This pass checks them once for the whole description.

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
- A criterion that asks where something is stated (a target, an obligation, a constraint) is answered by a search of the baseline. A complete search that finds nothing is Evidence Sufficient and Outcome Unsatisfactory, not Evidence Missing. The record names the places searched. Evidence Missing remains for a search that could not be completed.
- A criterion that uses the result of another criterion names it. Its Outcome is judged on the part that does not depend on the missing input, and its finding refers to the finding of the other criterion.
- Record evidence before the rating (section 8.2).
- A finding is mandatory for the ratings Partially, Unsatisfactory and Unassessable. An Unassessable finding is recorded against AD01 or AD07 and states whether the evidence is insufficient or missing. The severity of a finding does not define the rating.
- Do not average ratings. Ratings are ordinal. Report the count per rating.
- This catalogue does not define knock-out criteria. Which criteria are critical depends on the organisation and the architecture. The final evaluation of a review decides this for its specific environment.
- The catalogue defines no criticality weight and no numeric mapping of the rating words (QA 0.0290, 0.0300). A report gives the count per rating word. What is critical is decided in the final evaluation of the review.

### 7.2 Maturity of practices

The rating says whether a practice meets the criterion today. Maturity says how repeatably the organisation performs it. They are different axes, and both are recorded for practice criteria. Design criteria carry no maturity level.

The scale is the CMMI-based scheme of ISACA COBIT 2019 (COBIT 2019 Framework: Introduction and Methodology, section 6.4). A practice criterion records a process capability level. COBIT gives these levels no names, so they are written as numbers. The meaning is paraphrased from COBIT Figure 6.2.

| Capability level | Meaning |
|------------------|---------|
| 0 | No basic capability. The approach is incomplete and may or may not meet the intent of the practice |
| 1 | The practice more or less achieves its purpose with an incomplete set of activities, initial or intuitive, not very organised |
| 2 | The practice achieves its purpose with a basic but complete set of activities, which can be called performed |
| 3 | The practice achieves its purpose in a more organised way, with organisational assets. It is well defined |
| 4 | As 3, and its performance is measured, quantitatively |
| 5 | As 4, and continuous improvement is pursued |

How far a level is reached is rated with the COBIT achievement scale: Fully (more than 85 percent), Largely (50 to 85 percent), Partially (15 to 50 percent), Not (less than 15 percent). It is a judgement and is recorded with the level, for example "2, Largely". A level counts as reached when it is Fully or Largely achieved.

### 7.3 Capability profile

Each review records one capability profile. It is required. It rates the organisation's practice areas with the focus area maturity levels of COBIT 2019 (COBIT 2019 Framework: Introduction and Methodology, section 6.4, Figure 6.3). A practice area is a focus area in the COBIT sense. It reaches a maturity level when all its practice criteria reach that capability level (section 7.2). Each level is recorded with the evidence behind it.

| Maturity level | Name | Meaning (paraphrased from COBIT) |
|----------------|------|----------------------------------|
| 0 | Incomplete | Work may or may not be done towards the purpose of the practice area |
| 1 | Initial | Work is done, but the full goal and intent are not yet achieved |
| 2 | Managed | Planning and performance measurement take place, not yet in a standardised way |
| 3 | Defined | Organisation-wide standards guide the work |
| 4 | Quantitative | The organisation is data driven, with quantitative performance improvement |
| 5 | Optimizing | The organisation is focused on continuous improvement |
 Do not average the levels. Report the profile as a list. The profile is the main evidence for AD15 Organisational fit.

A practice area is a COBIT focus area: a set of governance and management objectives (COBIT 2019 Framework: Introduction and Methodology, section 6.4.3). The objectives column makes the profile traceable to COBIT. The list of practice areas is still a proposal; candidate additions are in QA 0.0230. TOGAF 9.1 (ch. 51) names the ACMM as a related architecture maturity model. Its nine elements can cross-check the list, but its level names differ from COBIT and it averages the levels, so it is not used for rating.

| Practice area | Related viewpoint | COBIT 2019 objectives | Level (0 to 5) | Evidence |
|---------------|-------------------|-----------------------|----------------|----------|
| Architecture governance | XV | APO03 Managed Enterprise Architecture, EDM01 Ensured Governance Framework Setting and Maintenance | | |
| Decision management and decision records | XV | No direct counterpart. Nearest: EDM01.01 (decision-making model), BAI08 Managed Knowledge | | |
| Traceability from requirements to architecture | XV | BAI02 Managed Requirements Definition, BAI03.09 (changes to requirements) | | |
| Architecture evaluation and conformance checking | VP05 | APO03.05 (architecture services and compliance), MEA04 Managed Assurance | | |
| Security engineering practice | XV (SE) | APO13 Managed Security, DSS05 Managed Security Services | | |
| Operations and incident learning | VP07 | DSS02 Managed Service Requests and Incidents, DSS03 Managed Problems | | |
| Change, release and deployment | VP07 | BAI06 Managed IT Changes, BAI07 Managed IT Change Acceptance and Transitioning | | |
| Skills and ownership | XV (RS) | APO07 Managed Human Resources | | |

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
- Provenance: artefact name, version and date, relative to the review baseline. For the producer Tool, also the command or query and its result. Evidence from outside the reviewed repository carries its own repository and commit or date, and is checked against the code baseline before use.
- Object of the evidence: the artefact that was tested, measured or read. Evidence about a copy, a model or a simulation of an element is at most Documented for the element itself. A simulation result keeps its level for the simulation.
- Conflicting evidence: when two artefacts at the baseline contradict each other, the executable artefact (code, configuration) is the evidence, the other one is Insufficient, and the contradiction is a mandatory finding (type weakness, link AD07). In a safety-relevant scope its severity is at least major.
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

Status of this table: it is a generic tag vocabulary for criteria. It is a library of well-known principles from the sources named in the table. Nobody has decided that an organisation or a system applies them. A principle that is adopted for a system or an organisation is a DEC document, one for each principle. The DEC states the principle (Decision Outcome), the rationale (Context), the implications (Consequences) and how to test it (Confirmation). It carries the tag `arch.principle`. The tag PR18 is the link: a review refers to the adopted principles through PR18 and AD11. The definitions and the way to find the adopted principles are in TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09, section 6. Patterns are handled in the same way, with the tag `arch.pattern`.

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
| PR09 | Dependency rule: source dependencies point inward, towards policy | Martin ch. 22, "The Dependency Rule". Checked. It is stated on source-code dependencies only |
| PR10 | Acyclic dependencies between components | Martin ch. 14, Acyclic Dependencies Principle. Checked. "Component" is Martin's deployable unit (Architecture Model TXT, section 3.3) |
| PR11 | Stable dependencies and stable abstractions | Martin ch. 14, Stable Dependencies Principle and Stable Abstractions Principle. Checked. The metrics I, A and D give measurable evidence. Martin calls them imperfect, so they are indicators and not thresholds |
| PR12 | Policy separated from detail, independence of frameworks, UI and database | Martin ch. 19 and 20 (policy, level, business rules), ch. 22 and ch. 30 to 32 (database, web and frameworks are details). Checked |
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

## 10. Criteria: Deployment x Reliability (worked example), CrossView x Safety, CrossView x Regulation, Multi-Tenancy, Extension Interfaces

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
- Question: Show which deployment nodes and shared services have no redundant counterpart.
- Expected evidence: deployment diagram, failure mode analysis, dependency list.
- Note: this criterion can be rated without a target. The effect on the target is VP06-RE-160.

### VP06-RE-110 Failure domains

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD03 Correctness.
- Principle tags: PR14.
- Question: How are redundant instances placed across independent failure domains such as host, zone and region, and which failure domains are shared?
- Expected evidence: deployment diagram, infrastructure configuration, placement rules.
- Applicability: Inapplicable only when the scope has exactly one failure domain by design. Missing redundancy on a system that can run on several nodes is Unsatisfactory, not Inapplicable.

### VP06-RE-120 Failure detection and failover or safe state

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD07 Verifiability.
- Principle tags: PR14, PR16.
- Question: How is a failed node detected, how long does the failover or the transition to the defined safe state take, and where is that behaviour defined?
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
- Expected evidence: failover test report, disaster recovery exercise report, chaos test results. A fault injection capability is not a test result.

### VP06-RE-160 Effect of single points of failure on the target

- Type: design.
- Sub-characteristic: Availability.
- Primary AD: AD12 Risk management.
- Principle tags: PR14.
- Depends on: VP06-RE-090 (target), VP06-RE-100 (single points of failure).
- Question: For each node and shared service found in VP06-RE-100, what happens to the stated availability target if it fails?
- Expected evidence: failure mode analysis, availability calculation, the target of VP06-RE-090.

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
- Maturity: capability level 1, Fully. The practice more or less achieves its purpose, informally (section 7.2).
- Finding F-05: weakness, minor. Failover tests have no schedule and no owner.

### XV-SA-090 Hazard identification

- Type: design.
- Sub-characteristic: Risk Identification.
- Primary AD: AD12 Risk management.
- Principle tags: none.
- Question: Where is the hazard analysis, which hazards does it list, and which party does each hazard affect (people, equipment, environment)?
- Expected evidence: hazard analysis, hazard log.
- Note: the first criterion of the home cell. Without it no other SA criterion can be rated.

### XV-SA-100 Safety targets and integrity

- Type: design.
- Sub-characteristic: Operational Constraint.
- Primary AD: AD07 Verifiability.
- Principle tags: none.
- Depends on: XV-SA-090.
- Question: Which safety target or integrity level is stated for each hazard, and against which standard?
- Expected evidence: safety requirements, safety integrity assessment.

### XV-SA-110 Safety functions and safe states

- Type: design.
- Sub-characteristic: Fail Safe, Hazard Warning.
- Primary AD: AD03 Correctness.
- Principle tags: PR07.
- Depends on: XV-SA-090.
- Question: Which safety function reduces each hazard, what is its defined safe state, and how is the operator warned?
- Expected evidence: list of safety functions, safety concept.

### XV-SA-120 Allocation of safety functions

- Type: design.
- Sub-characteristic: Safe Integration.
- Primary AD: AD06 Traceability.
- Principle tags: none.
- Depends on: XV-SA-110.
- Question: Show for each safety function the hardware and software elements that implement it, end to end.
- Expected evidence: allocation table, architecture model with the `safety.function` property (Architecture Model TXT, section 8.3).

### XV-SA-130 Independence from the mission function

- Type: design.
- Sub-characteristic: Safe Integration.
- Primary AD: AD12 Risk management.
- Principle tags: PR06.
- Depends on: XV-SA-120.
- Question: How is each safety function kept independent of the mission function that it protects against, and which elements do both share?
- Expected evidence: allocation table, common cause analysis.

### XV-SA-140 Verification of safety functions

- Type: practice.
- Sub-characteristic: Fail Safe.
- Primary AD: AD07 Verifiability.
- Principle tags: none.
- Depends on: XV-SA-110.
- Question: How is each safety function verified on the real element, how often, and with what result?
- Expected evidence: safety function test reports, test code that calls the real element (section 8.2, object of the evidence).

### XV-RG-090 Applicable obligations

- Type: design.
- R+W concern: Regulation.
- Primary AD: AD11 Compliance.
- Principle tags: PR18.
- Question: Where is the register of the laws, regulations and policies that apply, and which obligations must the subject meet itself and which must it enable for its operator?
- Expected evidence: regulation register, legal assessment, conformity statements.
- Note: the first criterion of the home cell.

### XV-RG-100 Allocation of obligations

- Type: design.
- R+W concern: Regulation.
- Primary AD: AD06 Traceability.
- Principle tags: none.
- Depends on: XV-RG-090.
- Question: Show for each obligation the requirement, the architectural element and the evidence that meets it.
- Expected evidence: compliance matrix, requirements, architecture model.

### XV-RG-110 Differences between countries

- Type: design.
- R+W concern: Regulation.
- Primary AD: AD11 Compliance.
- Principle tags: none.
- Depends on: XV-RG-090.
- Question: In which countries is the system used or sold, and how does the architecture handle the legal differences between them (for example radio licences, data residency, export control)?
- Expected evidence: regulation register per country, deployment and configuration options.

### VP03-SE-090 Separation of tenant data

- Type: design.
- Sub-characteristic: Confidentiality, Integrity.
- Primary AD: AD03 Correctness.
- Principle tags: PR03, PR08.
- Applicability: only if the scope is multi-tenant (section 3).
- Question: How is the data of each tenant kept separate (separate store, schema or key, row-level rule), and which data, keys or caches do tenants share?
- Expected evidence: data model, tenant configuration, key management design.

### VP02-SE-090 Tenant resolution

- Type: design.
- Sub-characteristic: Authenticity, Integrity.
- Primary AD: AD12 Risk management.
- Principle tags: PR07, PR13.
- Applicability: only if the scope is multi-tenant (section 3).
- Question: How does the system decide which tenant a request belongs to, and how is it prevented that a user selects or switches to a tenant that is not theirs (for example by a host name or a request parameter)?
- Expected evidence: request handling design, authentication and authorisation design, security tests.

### VP06-PE-090 Capacity shared between tenants

- Type: design.
- Sub-characteristic: Capacity, Resource Utilization.
- Primary AD: AD12 Risk management.
- Principle tags: PR14.
- Applicability: only if the scope is multi-tenant (section 3).
- Question: Which runtime resources do tenants share, and how is the load of one tenant kept from reducing the performance of the others?
- Expected evidence: deployment diagram, quotas and limits configuration, load test results per tenant.

### VP06-RE-170 Fault isolation between tenants

- Type: design.
- Sub-characteristic: Fault Tolerance.
- Primary AD: AD12 Risk management.
- Principle tags: PR14.
- Applicability: only if the scope is multi-tenant (section 3).
- Question: Which failures of one tenant (data corruption, exhausted resources, failed migration) can affect the availability of other tenants, and how are they contained?
- Expected evidence: failure mode analysis, deployment diagram, tenant migration design.

### VP02-SE-100 Privilege of extension code

- Type: design.
- Sub-characteristic: Integrity, Confidentiality.
- Primary AD: AD12 Risk management.
- Principle tags: PR06, PR08.
- Applicability: only if the scope has an extension interface (section 3).
- Question: Which privileges does third-party extension code have inside the process, how is it isolated or reviewed, and how is its origin verified before it is loaded?
- Expected evidence: extension interface design, security policy for extensions, supply chain controls.

### VP02-CO-090 Versioning of the extension interface

- Type: design.
- Sub-characteristic: Interoperability.
- Primary AD: AD02 Consistency.
- Principle tags: PR04.
- Applicability: only if the scope has an extension interface (section 3).
- Question: Where is the extension interface defined, how is it versioned, and how are extensions told about a breaking change?
- Expected evidence: interface definition, versioning policy, compatibility tests of extensions.

### VP05-MA-090 Independent build and release of extensions

- Type: design.
- Sub-characteristic: Modularity, Modifiability.
- Primary AD: AD12 Risk management.
- Principle tags: PR02.
- Applicability: only if the scope has an extension interface (section 3).
- Question: How are extensions built, tested and released independently of the system, and which parts of the system must change when an extension changes?
- Expected evidence: build configuration, repository layout, release process of extensions.

## 11. Model Generation Agent (C4 and Structurizr)

This section describes an agent that creates architecture models in the Structurizr DSL (C4 model) from existing source code or from specmgr artifacts. The models are input evidence for a review. Status: design proposal, not implemented. Open items are tracked in the linked QA.

The criteria in sections 6 to 10 stay tool neutral and name no product. Product names appear only in this section.

### 11.1 Scope and Boundary

- The agent creates one or more Structurizr workspaces, a facts file for each, and a gaps report.
- The agent does not review. It records no rating, outcome, finding, maturity or capability profile. A modeler that judges its own model grades itself.
- A separate review agent reads the workspaces and applies sections 6 to 10. It is out of scope here.
- A C4 model is evidence for some viewpoints only. Section 8 of TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model) lists which. The gaps report lists the viewpoints that the model cannot show. For those viewpoints the review agent finds Evidence Missing, so the rating is Unassessable.

### 11.2 Inputs and Outputs

- Input, source code: one or more repository paths.
- Input, specmgr artifacts: one or more artifact IDs, for example a SYSRS and the REQ, UC, DEC, RSK and GOL documents it references.
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
- The properties `origin` and `provenance` are set on every element and relationship. A model-level property holds the safety relevance declaration and its justification (Architecture Model, section 8.3).

### 11.5 Components

Agents, in `.opencode/agent/`:

| Agent | Task | Access |
|-------|------|--------|
| c4-modeler | Orchestrator. Runs the phases of section 11.7 and writes the workspace and the gaps report | Read and write |
| c4-source-extractor | Source code to facts file. Can run once per container, so a large repository fits in the context | Read only |
| c4-specmgr-extractor | specmgr artifacts to facts file | Read only |
| c4-model-checker | Validates the workspace, runs the inspections and compares a sample of facts with the source | Read only |

Skills, in `.opencode/skill/`, one subfolder each. A skill holds knowledge, not behaviour, and loads on demand:

| Skill | Content |
|-------|---------|
| c4-structurizr-dsl | DSL syntax and conventions: identifiers, views, styles, tags, properties, deployment, perspectives, the validation and export tools |
| c4-from-source | How to find containers, components, relationships and external systems in code. Containers come from compose files, Kubernetes manifests, Dockerfiles and build manifests. Relationships come from HTTP, queue and database clients. External systems come from environment variables and SDKs. Where to stop |
| c4-from-specmgr | The mapping from specmgr artifact types to C4 constructs. UC actors become persons. REQ items about interfaces and compatibility become external systems. DEC becomes documentation and properties. Everything is Proposed unless an artifact states a structure |
| c4-viewpoint-mapping | Reads the mapping and the property conventions of the Architecture Model TXT, section 8. It holds no copy |
| c4-model-quality | The checks of section 11.8 as modelling rules, including the severity setting per inspection |

Commands, in `.opencode/command/`:

| Command | Effect |
|---------|--------|
| `/c4 source <path...>` | Runs the flow of section 11.7 for source code |
| `/c4 specmgr <id...>` | Runs the flow of section 11.7 for specmgr artifacts |

### 11.6 Viewpoints and C4 Views

The mapping of viewpoints and perspectives to C4 views and Structurizr constructs, the coverage statements and the property conventions are defined in TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model), section 8. This section holds no copy, so that the agent and the definition cannot drift apart. The skill c4-viewpoint-mapping reads that section.

What the agent must keep in mind from it:

- C4 has no native construct for VP03 Information. The row XV CrossView is not modelled. VP05 Development and VP07 Operational are covered in part only. VP04 Concurrency is covered only between processes, not inside a process.
- Quality targets, ratings, maturity levels and the capability profile are not modelled. The agent can reference such evidence through properties. It does not create it.
- Properties appear only in the JSON export. A query script over the JSON export is the authoritative reader.
- Structurizr does not check property values. The check script of section 11.8 reports values that occur once and conflicts between a parent and a child.
- The properties `origin` and `provenance` have the closed values of section 11.4.
- A C4 model alone is no evidence for the Dependency Rule (PR09) or for acyclic dependencies (PR10). C4 relationships show the direction of use, and Martin states these principles on source-code dependencies (Architecture Model TXT, section 3.4 and 8.5). The agent reports such a criterion as Evidence Missing unless a code dependency analysis exists.

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
- Phase 3: split workspaces by system and team boundary, not by viewpoint. Create one workspace per software system with one owning team. Create a landscape workspace only if there is more than one system. A review overlay is a separate workspace and needs `workspace extends`, which is not yet tested. Create one deployment environment for each shipped deployment descriptor and for each variant in scope (section 3).
- Phase 5: the checker never edits the workspace. It only reports.

### 11.8 Checks and Evidence

The checks of phase 5 support the architecture-level pass of section 6.4. They have the producer Tool (section 8.2). They are recorded with their command and result, so that someone else can run them again. They support structure claims only. They do not support quality targets.

| Check | Supports |
|-------|----------|
| Workspace parses without errors | Evidence for all views is Documented, from a valid model |
| Disconnected element | AD01, AD02 |
| Element in no view | AD13 |
| Decisions of the system, checked over the decision store with list_dec and list_references, not with the Structurizr inspection. The inspection "missing decisions" is set off, because Structurizr reads decisions only from files named `NNNN-*.md` and cannot tell a system with decisions in another format from a system without decisions | AD06 |
| Software system or container without documentation | AD09 |
| Container without technology, relationship without description | AD07 |
| Property check over the JSON export: shared failure domains, boundary crossings, unset values, values that occur once, parent and child conflicts, group name against `trust.boundary`, elements per `safety.function` (gaps in the chain) | VP06 failure domains, XV x SE trust boundaries, XV-SA-120, AD02 |
| Sample of facts compared with the source | Correctness of the extraction, not of the architecture |

- The default severity of the inspections is error. Set the severity per inspection before the run. Set the decision inspection off (see the table).
- A Proposed element has at least one Proposed relationship, so that the inspection does not report it as disconnected.
- A view from a valid model is Documented. A recorded inspection is Demonstrated. An inspection that a pipeline runs repeatedly is Measured.
- A deployment node with an instance count of one and no replica is visible in the model. This supports VP06-RE-100 and VP06-RE-120.

## 12. Related Documents

TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09: Architecture Model: Viewpoints, Perspectives and Structurizr Mapping

QA 25bd5b93-a228-4d6c-8b70-d143dfd39444: Architecture Review Checklist: Decisions and Open Items

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-22 22:30:00.000Z - Draft 0.15

Open items of QA 25bd5b93-a228-4d6c-8b70-d143dfd39444 decided by the user. AD08 and AD10 deprecated (0.0250); XV-SA-130 and VP05-MA-090 re-tagged to AD12, VP02-CO-090 to AD02. No criticality weight and no numeric mapping (0.0290, 0.0300). Capability profile: COBIT 2019 objectives per practice area, ACMM note (0.0230, partly). TOGAF 9.1 added to the sources: Business/Capability note in section 4 (0.0260), precondition requester, objectives and sign-off in section 3 (0.0210, partly). Issue 267.

### 2026-11-22 20:30:00.000Z - Draft 0.14

Maturity scale from ISACA COBIT 2019 (CMMI-based, checked against the markdown copy): section 7.2 uses the unnamed process capability levels 0 to 5 with the achievement scale Fully, Largely, Partially, Not; section 7.3 rates practice areas with the named focus area maturity levels Incomplete, Initial, Managed, Defined, Quantitative, Optimizing. ISO/IEC 33020 is no longer used (sources in section 2, example rating record in section 10). New preconditions multi-tenant and extension interface (section 3). New criteria in section 10: VP03-SE-090, VP02-SE-090, VP06-PE-090 and VP06-RE-170 for multi-tenancy; VP02-SE-100, VP02-CO-090 and VP05-MA-090 for extension interfaces. Issue 267. See QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0220 and 0.0700.

### 2026-11-22 19:30:00.000Z - Draft 0.13

Applied the 15 proposed changes of the Phase 120 validation (four systems: specmgr, AERIS-10, Apache OFBiz, OpenTelemetry Demo; synthesis in the feature folder, QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0690). Matrix: VP02 x SE, VP03 x MA, VP02 x SA and VP06 x SA from S to P (now 36 P, 43 S, 17 X); section 5.3 updated. Section 3: variant and deployment descriptor in the baseline, new preconditions system class, subject and intended operating profile, new section 3.1 default tailoring by system class. Section 4: the MA split between VP02 and VP05, input handling and extension interfaces in VP02 x SE. Section 5.2: Safety gate with hazard types, protected party, development tools and the RE against SA rule; LO against RG rule. Section 7.1: complete-search rule and dependent criteria. Section 8.2: external evidence, object of the evidence, conflicting evidence. Section 10: VP06-RE-100 split (new VP06-RE-160), RE-110 applicability, RE-120 safe state, RE-150 note; new criteria XV-SA-090 to -140 and XV-RG-090 to -110. Section 11: decision check over the decision store, safety function check, one environment per descriptor and variant. Issue 267.

### 2026-11-22 14:27:37.000Z - Draft 0.12

Mechanical corrections. Section 5.1: RS is re-scoped to the full lifecycle, as in the Architecture Model TXT. Section 11.5: the skill directory is `.opencode/skill/` (singular, one subfolder for each skill), the only skill directory that the harness bundle includes. Sections 11.2 and 11.5: ADR removed as an input artifact type, because the ADR artifact type was removed in favour of DEC (issue 46). Issue 267.

### 2026-11-20 11:43:54.000Z - Draft 0.11

Renamed the perspective DevelopmentResource (DR) to Resources (RS) and re-scoped it to the full lifecycle, build and operate; the R+W counterpart Development Resource is named in section 5.1 and in the sources. The matrix header, the perspective codes and all DR references change to RS. No criterion carried a DR code, so no criterion ID changed. Issue 267. See QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0670.

### 2026-11-18 15:00:00.000Z - Draft 0.10

Clean Architecture (Martin) is checked against the markdown copy. Section 2: the status "to be confirmed" is replaced by the checked status and the chapters used. Section 4: PR12 joins PR09 to PR11 in Development, labelled as our interpretation. Section 9: the Origin column of PR09 to PR12 names the chapters. Section 11.6: a C4 model alone is no evidence for PR09 and PR10. No viewpoint, perspective, matrix cell or criterion ID changed. Issue 267.

### 2026-11-18 14:30:00.000Z - Draft 0.9

Consolidation for issue 267. The viewpoint definitions, the perspective definitions and the Structurizr mapping moved to the new TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model). Section 4 no longer paraphrases the concern lists. The concern lists of the book are in the new TXT, and the topics that the earlier lists added are placed there. Section 2 now states what was checked against the book, and that the book's per-view tables are prose. Section 5.2 states that the P, S, X derivation is our interpretation. New section 5.3 compares the matrix with R+W Table 4-1. Section 9 is relabelled as a tag vocabulary, and adopted principles are DEC documents. Section 11.6 points to the new TXT for the mapping and the property conventions. The file name now ends in viewpoints-x-perspectives. No viewpoint, perspective, matrix cell or criterion ID changed.

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
