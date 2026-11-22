---
classification: null
created: '2026-11-18T13:25:56.718+01:00'
id: 30983f27-f5aa-4d42-972e-5593f0c3ba09
status: draft
type: txt
updated: '2026-11-22T22:30:00.000+01:00'
version: 1.0.0
---

# Architecture Model: Viewpoints, Perspectives and Structurizr Mapping

Definition of the architecture model that the architecture review checklist and the model generation agent rely on. It fixes the concepts (metamodel), the seven viewpoints, the 12 perspectives, the home of principles, patterns, tactics and decisions, and the mapping of viewpoints and perspectives to a C4 model in Structurizr.

This document holds definitions. The review criteria, the applicability matrix, the rating scale and the evidence rules stay in the checklist. Status of this draft: design proposal for validation. Nothing here is implemented. The Structurizr statements marked "to be confirmed" are not yet checked with the tool.

## 1. Purpose, Scope and Status

- Purpose: one place for the architecture concepts, so that the checklist, a future ARC artifact and the model generation agent use the same words.
- Alignment rule: the viewpoints follow the book of Rozanski and Woods (R+W), 2nd edition, 2012. A deviation needs a reason, and it is labelled "catalogue extension" (section 7).
- A viewpoint is catalogue knowledge, not a specmgr artifact. It is generic and the same for every project. It is meant to become a resource and a skill. The instances (Structurizr workspaces and their views) are the future ARC artifact.
- Out of scope in this draft: running the Structurizr probe again, the c4-\* agents and skills, a viewpoint resource, and DEC documents for single principles. They follow after validation.
- Tracking: GitHub issue 267, feature feat-267-arch-rvw. The downstream issues are 228 (ARC artifact) and 250 (C4 agent skills).

## 2. Sources and Provenance

| Source | Used for | Status |
|--------|----------|--------|
| Rozanski and Woods, Software Systems Architecture, 2nd edition, Addison-Wesley, 2012 (R+W) | Viewpoints (ch. 3 and 15 to 22), perspectives (ch. 4 and 24 to 29), principles and decisions (ch. 8), patterns and styles (ch. 11), the architecture description (ch. 13) | Concern lists, names and order checked against the text of the book. Line references in this document point to the markdown copy of the book in the sibling docs repository |
| Martin, Clean Architecture, Pearson, 2018 (Martin), with chapter 34 by Simon Brown | Source-level dependency principles (ch. 14, 19, 22), decoupling modes (ch. 16 and 18), the meaning of component, boundary and service (ch. 12, 18, 27 and 34) | Checked against the markdown copy in the sibling docs repository. Line references written "Martin L..." point to that file and not to the R+W copy. Used for the principle tags PR09 to PR12 of the checklist and for the term rules in section 3.3. It is not a source for viewpoints, perspectives or tactics |
| ISO/IEC/IEEE 42010:2011 | Architecture description, viewpoint, view, model kind, correspondence, rationale | Concepts and clause 5.6 NOTE 1 checked against the text. Annex B.3 cites the 1st edition of R+W, which has six viewpoints and no Context viewpoint |
| ISO/IEC 25010:2023 | Nine quality characteristics, used as perspectives | Names and sub-characteristics checked against specmgr://iso25010. The original standard is not in the docs repository |
| Structurizr documentation and tool, version 2026.10.26 | Mapping in section 6 | Property and perspective behaviour verified in QA 25bd5b93 (0.0380, 0.0500). Everything else is to be confirmed |
| ISO/IEC/IEEE 42030 | Architecture evaluation framework | Missing. Only cited in the texts of 12207 and 15288 |
| TOGAF, ATAM report of the SEI | Possible alignment, Business/Capability viewpoint | Missing |

## 3. Metamodel

Two class diagrams define the concepts. The PlantUML files are the single source. This document does not copy them.

- Diagram A, conceptual: `.specmgr/feat/feat-267-arch-rvw/arch-metamodel-a-conceptual.puml`
- Diagram B, realisation in Structurizr: `.specmgr/feat/feat-267-arch-rvw/arch-metamodel-b-structurizr.puml`

Both files parse and render with PlantUML (checked with a local jar during authoring). The structure check of specmgr alone does not render them.

### 3.1 Concepts

| Concept | Meaning | Source |
|---------|---------|--------|
| ArchitectureDescription | The set of work products that documents an architecture. It consists of views | 42010, R+W ch. 2 |
| Stakeholder, Concern | A party with an interest in the system. An interest that matters to a stakeholder | 42010, R+W ch. 9 |
| Viewpoint | A template for the construction of views. It names the concerns it frames, the model kinds, the guidelines and the typical pitfalls | 42010, R+W ch. 3 |
| View | The architecture description of one system from one viewpoint. A view conforms to one viewpoint | 42010, R+W ch. 3 |
| ModelKind, Model | The kind of model a viewpoint prescribes, and an instance of it in a view | 42010 |
| Correspondence | A recorded relation between elements of different views | 42010, R+W ch. 23 |
| Perspective | A set of activities, tactics and guidelines that you apply across views, so that the system shows a quality property. It usually changes views and creates no new ones | R+W ch. 4 |
| Tactic | An established approach to reach a quality property. It belongs to a perspective. It is not a design pattern | R+W ch. 4 |
| Principle | A statement of belief, approach or intent that guides the architecture. It has a rationale and implications | R+W ch. 8 |
| Pattern, style | A reusable solution form. R+W treat architectural style and architectural pattern as synonyms | R+W ch. 11 |
| Decision, rationale | A choice with significance for the architecture, and the reason for it | 42010, R+W ch. 8 and 13 |
| Scenario | A description of a use of the system or of a quality situation. It is a technique and not a viewpoint | R+W ch. 10 |
| Criterion, MatrixCell, Finding | Catalogue concepts of the review checklist. A cell is the crossing of a matrix row and a perspective | Catalogue extension |
| MatrixRow, CrossView | A matrix row is a viewpoint or the row XV CrossView. CrossView is not a viewpoint. It holds the criteria on the architecture description as a whole: security target, hazard analysis, regulation register, resource constraints | Catalogue extension |

### 3.2 Relations that matter

- A view conforms to exactly one viewpoint. A viewpoint frames several concerns.
- Perspectives are orthogonal to viewpoints. A perspective is applied to some or all views (R+W ch. 4). The applicability matrix of the checklist is the record of this application.
- A principle guides concerns and is followed by decisions. The chain concern, principle, decision is the traceability line of R+W ch. 8.
- A decision follows principles and applies patterns and tactics. A tactic belongs to a perspective.
- A matrix row is a viewpoint or CrossView. CrossView spans the architecture description, not a view. In 42010 the description itself holds the stakeholders, concerns, decisions and rationale outside any view. The criteria of XV are about these items.
- Scenarios exercise perspectives. They state quality targets.

### 3.3 Terms used in two senses

Four words carry different meanings in the sources and in C4. The rule of this catalogue is stated for each one. A criterion or a Structurizr element uses the word in the catalogue sense only.

| Term | Sense in the sources | Sense in C4 and Structurizr | Catalogue rule |
|------|----------------------|-----------------------------|----------------|
| Component | Martin: the unit of deployment, the smallest entity that can be deployed, for example a jar or a DLL (ch. 12, Martin L1623) | Brown, the author of C4: a grouping of related functionality behind a clean interface, inside an execution environment. Whether it sits in its own jar is an orthogonal concern (ch. 34, Martin L4306) | "Component" means the C4 sense. The Martin sense is written "deployable unit". Martin's component principles (PR10 and PR11 of the checklist) are written for deployable units. A criterion that uses them says which sense it means |
| Boundary | Martin: a line between components. It is kept by the direction of source-code dependencies (ch. 17 and 18, Martin L2474, L2658) | A trust boundary is a catalogue property on elements (section 8.3). It is a security concept | "Boundary" alone is not used. Write "architectural boundary" (Martin) or "trust boundary" (SE) |
| Service | Martin: a process that talks over a network. A service is not an architecture by itself. The architecture is the boundaries that follow the Dependency Rule (ch. 27, Martin L3446) | A container, or a software system | Map a service by its decoupling mode (section 8.5). A criterion does not take a service to be an architectural boundary |
| Layer | Martin: a horizontal partition of source modules, for example the circles of ch. 22. R+W: the Layered style (ch. 11) | No construct | A layer is content of the Module Structure Model in VP05 (section 4.3) |

### 3.4 Dependency direction

Martin separates two directions: the flow of control and the direction of the source-code dependency. With dynamic polymorphism they can point in opposite ways (ch. 18, Figure 18.2, Martin L2658 to L2700). The Dependency Rule is stated on the source-code dependency only (ch. 22, Martin L2969). A C4 relationship usually shows the direction of use. It does not show the direction of the source dependency. A C4 model alone is therefore no evidence for PR09. See section 8.5.

## 4. Viewpoints

The viewpoints are the seven core viewpoints of R+W, in the order of the book (R+W Table 3-1, ch. 16 to 22). The IDs VP01 to VP07 are catalogue IDs. The names and the concerns are the book's.

Concern lists are quoted from the concern row at the start of each viewpoint chapter. The book has no other viewpoint. It allows more (R+W ch. 3), and a review can add one.

### 4.1 Concerns of the viewpoints (R+W)

| ID | Viewpoint | Concerns, as the book states them | Book |
|----|-----------|-----------------------------------|------|
| VP01 | Context | System scope and responsibilities, identity of external entities and services and data used, nature and characteristics of external entities, identity and responsibilities of external interfaces, nature and characteristics of external interfaces, other external interdependencies, impact of the system on its environment, and overall completeness, consistency, and coherence | ch. 16, L4001 |
| VP02 | Functional | Functional capabilities, external interfaces, internal structure, and functional design philosophy | ch. 17, L4359 |
| VP03 | Information | Information structure and content; information purpose and usage; information ownership; enterprise-owned information; identifiers and mappings; volatility of information semantics; information storage models; information flow; information consistency; information quality; timeliness, latency, and age; and archiving and information retention | ch. 18, L4730 |
| VP04 | Concurrency | Task structure, mapping of functional elements to tasks, interprocess communication, state management, synchronization and integrity, supporting scalability, startup and shutdown, task failure, and reentrancy | ch. 19, L5396 |
| VP05 | Development | Module organization, common processing, standardization of design, standardization of testing, instrumentation, and codeline organization | ch. 20, L5698 |
| VP06 | Deployment | Runtime platform required, specification and quantity of hardware or hosting required, third-party software requirements, technology compatibility, network requirements, network capacity required, and physical constraints | ch. 21, L5993 |
| VP07 | Operational | Installation and upgrade, functional migration, data migration, operational monitoring and control, alerting, configuration management, performance monitoring, support, backup and restore, and operation in third-party environments | ch. 22, L6323 |

The earlier draft of the checklist paraphrased these lists, and its lists differed from the book in six of the seven viewpoints. The paraphrases are replaced by this table. The topics that the earlier lists added are placed in section 4.3.

### 4.2 Typical stakeholders and model kinds

The typical stakeholders and the typical model kinds are working lists of the checklist, section 4. They are not quotations of the book. The model kinds that the book names are: Context Model; Functional Structure Model; Information Structure, Ownership, Flow and Lifecycle Models; Concurrency Model; Module Structure, Common Design and Codeline Models; Runtime Platform, Network and Technology Dependency Models; Installation, Migration, Configuration Management, Administration and Support Models.

### 4.3 Placement of other topics

The earlier viewpoint definitions of the checklist listed topics that are not concern headings in the book. Each one has a place. "Book" means that the book treats the topic in that place. "Catalogue extension" means that the book has no home for it and the catalogue decides.

| Topic | Placement | Basis | Label |
|-------|-----------|-------|-------|
| Contract and partner of an external interface | VP01 Context Model attributes: owner and responsibilities of the entity, the service level expected of the interface | L4181, L4185, L4088 | Book. The words "contract" and "partner" are not book concepts |
| Layering | VP05 Module Structure Model, concern Module organization | L5762 | Book |
| Dependencies between runtime elements | VP02 concern Internal structure, and the design philosophy characteristics coupling and interdependency | L4393 | Book |
| External and internal interfaces | VP01 holds the external entity side: identity, responsibilities and nature of the external interface. VP02 holds the connectors and the internal handling. A criterion has one primary viewpoint by this rule | L4072, L4373 | Catalogue rule. The book lists external interfaces in both viewpoints |
| Lock-in | Perspective FL, sub-characteristic Replaceability. Also the Evolution pitfall "Overreliance on Specific Hardware or Software" | L9146 | Book, in a perspective |
| Nodes, environments, topology | VP06 concerns Runtime platform required and Network requirements. They are contents of the Runtime Platform Model and the Network Model | L6013, L6039, L6073 | Book |
| Redundancy, failover | Perspective RE (fault tolerance, recoverability). R+W: Availability and Resilience tactics. The Deployment view shows the result | L8555 to L8627 | Book, in a perspective |
| Scaling | Perspective FL, sub-characteristic Scalability, with PE. R+W: Performance and Scalability tactics. VP04 holds the concern Supporting scalability | L8073, L5462 | Book, with the ISO split |
| Logging | VP05 concern Instrumentation. VP07 consumes it in the Administration Model. Audit logging belongs to SE (Accountability) | L5732, L6645, L7171 | Book |
| Incident handling | VP07 concern Support, with the Support Model (incident classes, escalation). Incident recovery analysis belongs to RE | L6413, L6675, L8474 | Book |
| Change and release | Release mechanics: VP05 concern Codeline organization. Installation, upgrade and configuration: VP07. Reliability of change: MA and FL | L5738, L6337, L8926 | Book |
| Team ownership | Perspective RS | L5944 only hints at it | Catalogue extension |
| Trust boundaries | Perspective SE, applied to VP06 and VP01 | L7123, L7420 | Catalogue term. The book has no trust boundary concept |
| Failure domains | Perspective RE. The nearest book items are Single Point of Failure, Cascading Failure and Disaster Recovery | L8651 to L8682 | Catalogue term |
| Observability | VP07 concerns Operational monitoring and control, Alerting and Performance monitoring, enabled by VP05 Instrumentation | L6381 to L6412 | Book. The word does not occur in the book |
| Data migration and functional migration | Two concerns of VP07 with one Migration Model. Context lists data that will be migrated as part of the impact on the environment | L6345 to L6380, L4123 | Book |

## 5. Perspectives

There are 12 perspectives. The first nine are the ISO/IEC 25010:2023 product quality characteristics, with the ISO names, the ISO order and the ISO sub-characteristics. The last three are R+W perspectives that ISO cannot express, because they describe constraints and not properties of the product.

| Code | Perspective | Basis | R+W counterpart |
|------|-------------|-------|-----------------|
| FS | Functional Suitability | ISO | None. A concern of the Functional viewpoint in R+W |
| PE | Performance Efficiency | ISO | Performance and Scalability, without Scalability |
| CO | Compatibility | ISO | None |
| IC | Interaction Capability | ISO | Usability, Accessibility, and the language and culture part of Internationalization |
| RE | Reliability | ISO | Availability and Resilience |
| SE | Security | ISO | Security |
| MA | Maintainability | ISO | Evolution, in part |
| FL | Flexibility | ISO | Evolution in part, Scalability, the locale and unit part of Internationalization |
| SA | Safety | ISO | None. Catalogue extension |
| RG | Regulation | R+W | Regulation |
| LO | Location | R+W | Location |
| RS | Resources | R+W | Development Resource, re-scoped to the full lifecycle (catalogue extension) |

Why ISO as the base: the repository already uses the nine ISO characteristics for requirements, so a criterion matches the requirement that it checks.

Costs of this choice, accepted:

- Scalability sits in FL, as in ISO. The book groups it with Performance. A review that follows the book reads FL x Scalability together with PE.
- Evolution is split into MA and FL. Usability and Accessibility are merged into IC. Internationalization has no perspective of its own. IC (Inclusivity) and FL (Adaptability) share it.
- In the book a perspective is a package of concerns, activities, tactics and pitfalls. Our perspectives are the ISO names and the matrix. The mapping in section 5.1 keeps the book guidance reachable.

### 5.1 Mapping of R+W perspective guidance to the 12 codes

The table maps the concerns of each R+W perspective, with the tactics and pitfalls that the book names for them, to the codes of this catalogue. It cites chapters and uses no copied text. A tactic or pitfall is a reference point for a criterion, not a requirement.

| R+W perspective | R+W concern | Our code | Note |
|-----------------|-------------|----------|------|
| Security (ch. 25) | Resources, principals, policies, threats | SE | Context for the security target (XV x SE) |
| Security | Confidentiality, integrity, accountability | SE | Same-named ISO sub-characteristics. Audit logging: Accountability |
| Security | Availability | RE | Security availability is judged under Availability |
| Security | Detection and recovery, security mechanisms | SE | Tactics: recognized security principles, compartmentalisation |
| Performance and Scalability (ch. 26) | Response time, throughput, hardware resource requirements, peak load behavior | PE | Time Behaviour, Resource Utilization, Capacity |
| Performance and Scalability | Predictability | PE | Capacity, with the measured evidence |
| Performance and Scalability | Scalability | FL | Scalability. Read with PE. Tactic: scale up or scale out |
| Availability and Resilience (ch. 27) | Classes of service, planned downtime, unplanned downtime | RE | Availability |
| Availability and Resilience | Time to repair | RE | Recoverability. Activity: incident recovery analysis |
| Availability and Resilience | Disaster recovery | RE and LO | RE for the recovery, LO when the recovery site is far away |
| Availability and Resilience | Pitfalls: single point of failure, cascading failure | RE | Used for VP06-RE-100 and VP06-RE-140 |
| Evolution (ch. 28) | Magnitude, dimensions, likelihood and timescale of change | FL | Adaptability |
| Evolution | Changes driven by external factors | FL and RS | Replaceability and lock-in. External dependencies in RS |
| Evolution | Development complexity, preservation of knowledge | MA | Modularity, Analysability |
| Evolution | Reliability of change | MA | Modifiability, Testability. The mechanics are in VP05 |
| Evolution | When to pay for change, product management | RS | Economic viability (AD14) |
| Accessibility (ch. 29) | Types of disability, functional availability, disability regulation | IC and RG | Inclusivity. The legal part: Regulation |
| Development Resource | Time, cost, skills, resources, budgets, external dependencies | RS | Book perspective, re-scoped to the full lifecycle (catalogue extension) |
| Internationalization | Character sets, language needs, cultural norms | IC | Inclusivity |
| Internationalization | Currency conversion, locale, cultural neutrality | FL | Adaptability |
| Location | All concerns | LO | Same concern |
| Regulation | All concerns | RG | Same concern |
| Usability | Interface usability, information quality, alignment with working practices | IC | Operability, User Assistance and others. Information quality also touches VP03 |

## 6. Principles, Patterns, Tactics and Decisions

### 6.1 Definitions

- Principle: "a fundamental statement of belief, approach, or intent that guides the definition of an architecture" (R+W ch. 8, L2058). A good principle is constructive, reasoned, well articulated, testable and significant (L2070).
- Pattern and style: a reusable solution form (R+W ch. 11). R+W give Pipes and Filters and the Layered style as examples. Ports and adapters (Cockburn) is not in R+W. Martin names it with Hexagonal Architecture, DCI and BCE as related approaches (ch. 22, Martin L2943), and Brown discusses it in ch. 34 (Martin L4254).
- Measurable principles: R+W ask that a principle is testable (L2070). Martin gives measures for three principles. Instability I, Abstractness A and Distance D support PR11 (ch. 14, Martin L1972 to L2124). They count classes and imports. Martin calls them imperfect and "not a god" (Martin L2132), and the control limit in his Figure 14.15 is a mock-up. They are indicators for a criterion and not thresholds.
- Tactic: an approach to reach one quality property. It belongs to a perspective (R+W ch. 4). It is more general than a design pattern.
- Decision: a choice with significance for the architecture, with its rationale (R+W ch. 8, 13).

### 6.2 Three levels, three homes

| Level | What | Home |
|-------|------|------|
| Definition | What a principle, pattern, tactic and decision are, and how they relate | This document, sections 3 and 6 |
| Generic library | The tags PR01 to PR18 for criteria, and the pattern sources by viewpoint | The checklist, section 9. It is a tag vocabulary. Nobody decided these tags |
| Adopted | A principle or a pattern that an organisation or a system has decided to apply | One DEC document for each principle and each pattern |

### 6.3 An adopted principle as a DEC

- The statement of the principle is the Decision Outcome.
- The rationale is the Context and Problem Statement.
- The implications are the Consequences.
- The test that makes the principle testable is the Confirmation.
- A pattern DEC records the decision to adopt the pattern. The definition of the pattern stays in its source and is named in the section Source. Tactics are no DEC documents. They are generic knowledge of a perspective.

### 6.4 How to find the principles that apply

A tag alone is not enough. list_dec filters only by identifier, and the tags are free-form. Three layers are used:

1. Hub document, authoritative: the architecture description (a future ARC artifact, until then an index in a TXT) references each applicable principle as a DEC reference line. list_references then returns exactly the principles that apply, and the reverse reference diagram shows where one principle is applied.
2. Tags, a convention for people: `arch.principle` or `arch.pattern`, and a scope tag.
3. Scope, from the book: a principle is general (it applies to the whole architecture description) or view-specific. In the model, a view or the workspace carries the link in a property, for example `principle.dec`. The key is proposed and to be confirmed.

Follow-up outside this document: a tag filter in list_dec would remove the need for the hub in simple cases.

## 7. Deviations from the Book

| Deviation | Reason | Label |
|-----------|--------|-------|
| Row XV CrossView in the matrix | Criteria that no single view can hold: security target, hazard analysis, regulation register, resource constraints | Catalogue extension |
| Safety (SA) as a perspective | ISO/IEC 25010:2023 has Safety. R+W have no safety perspective | Catalogue extension |
| Nine ISO characteristics as perspectives | Match with the requirement model of the repository | Catalogue extension |
| Terms trust boundary and failure domain | Needed for Structurizr properties and for review criteria | Catalogue extension |
| External interfaces in VP01 as primary | One primary viewpoint for each criterion. Both viewpoints keep the book concern | Catalogue rule |
| Applicability matrix P, S, X | The per-view tables of R+W (Tables 25-1 to 29-6) are prose. The only rating grid is Table 4-1, for four perspectives. See the checklist, section 5.3 | Our interpretation |
| Viewpoint IDs VP01 to VP07 | The book has no IDs | Catalogue extension |
| Component means the C4 sense, a Martin component is a deployable unit | Martin and Brown use the word in two senses (section 3.3) | Catalogue rule |
| System class, subject and operating profile as preconditions, with default tailoring by class | The validation against four systems showed that tailoring depends on the class (checklist, section 3.1) | Catalogue extension |
| Martin's decoupling modes mapped to C4 containers and components | Martin has no C4 mapping. Brown (ch. 34) links his components to C4 but does not map the decoupling modes (section 8.5) | Our interpretation |

## 8. Mapping to C4 and Structurizr

C4 is not based on viewpoints. The mapping is many to many. A C4 model is evidence for some viewpoints only. It is a presentation layer and an evidence source. It is not part of the checklist structure.

Coverage values: full (the viewpoint concerns can be read from the model), partial (some concerns), none (no native construct).

### 8.1 Viewpoint to C4

| Viewpoint | C4 view and Structurizr construct | Coverage | Not modelled |
|-----------|-----------------------------------|----------|--------------|
| VP01 Context | System context and system landscape views. Persons and software systems, external ones tagged. Relationship description and technology as the external interface catalogue | partial to full | Impact of the system on its environment, other external interdependencies, overall coherence. Put them in documentation |
| VP02 Functional | Container and component views. Element description and relationship technology as responsibilities and interfaces | partial | Functional capabilities (what the system does for users), functional design philosophy |
| VP03 Information | No native construct. Relationship descriptions can name the data. Ownership and flow need another model. The evidence source is the data model of the system (entity definitions, DDL, ORM mapping, document schemas), checked with a recorded script, linked from documentation | none | All concerns |
| VP04 Concurrency | Dynamic view for flows between processes: order, parallel consumers, the failure point. Container instances for process structure | partial between processes, none inside a process | Threads, clock domains, interrupts, pools, synchronization, reentrancy, state management, order of initialisation. Between processes: delivery guarantees, consumer semantics, compensation |
| VP05 Development | Component view and technology as module structure. Documentation sections | partial | Common processing, standardization of design and testing, instrumentation, codeline organization. The dependency metrics I, A and D of Martin (section 6.1) and the direction of source dependencies (section 3.4) |
| VP06 Deployment | Deployment view: nested deployment nodes, infrastructure nodes, container instances with instance count and health checks. Properties for failure domains and trust boundaries | full for structure | Hardware specification, network capacity, third-party software requirements beyond technology |
| VP07 Operational | Deployment view: health checks, infrastructure nodes. Documentation sections. Monitoring design: monitoring containers plus a relationship tag for telemetry flows (tag name to be confirmed), excluded from VP02 views so that telemetry does not swamp them | partial | Installation, migration, configuration management, support, backup and restore. Health check details and alert rules stay text |
| XV CrossView | Not modelled. Properties can reference the evidence | none | Security target, threat model, hazard analysis, regulation register, resource constraints |

The early chat sessions mapped Information to container and component views, and Development to the C4 code level. This catalogue does not do that. C4 has no Information construct, and the model generation agent does not model code level.

### 8.2 Perspective to Structurizr

| Code | What the model can show | Carrier |
|------|-------------------------|---------|
| FS | Nothing about the functions. Structure only | None |
| PE | Technology of elements. Capacity is not modelled | Technology field |
| CO | Protocol and technology of relationships, external systems | Relationship technology |
| IC | Persons and user-facing containers | Persons, container technology |
| RE | Instance count, health check, no replica, shared failure domain | Deployment view, properties `failure.domain.host`, `.zone`, `.region` |
| SE | Trust boundaries, boundary crossings, protocol of relationships | Properties `trust.boundary`, `trust.boundary.crossing` |
| MA | Component structure, cycles in the dependency graph | Component view, JSON export |
| FL | Technology and replaceable elements. Scalability through instance count | Container instances |
| SA | The declaration "safety relevant" with its justification | Model properties `review.safety.relevant`, `review.safety.justification` |
| RG | A reference to the regulation register. Not modelled | Property reference. Key to be confirmed |
| LO | Sites and regions of deployment nodes | `failure.domain.region`. A separate site key is to be confirmed |
| RS | A reference to team ownership. Not modelled | Property reference. Key to be confirmed |

A review result can be attached to an element with the Structurizr perspective feature. Proposed use: one perspective for each criterion. Perspective name = the criterion ID (for example VP06-RE-100), value = the rating word, description = the evidence level and the finding summary (for example "Documented. Host A has no replica."). The perspective code is part of the criterion ID. Verified with the parse tool (QA 25bd5b93, 0.0680): a perspective name must be unique on an element, and a second perspective with the same name is a parse error. So a name per perspective code (for example Reliability) holds only one result per element, but one deployment node is subject to several criteria. Properties are no alternative: a repeated key is overwritten without a warning. A style on a perspective value works only in the Structurizr renderer, not in the PlantUML export. A style selector names one perspective, so a style per criterion ID is needed, or the review report holds the coloured view. Rating and evidence: the rating of a criterion sits on the top deployment node of the environment, or on the software system for a criterion outside VP06. A perspective with the same name on a lower node or element is evidence for that rating, not a second rating.

### 8.3 Property conventions

Verified with Structurizr 2026.10.26 (QA 25bd5b93, 0.0500):

| Key | Placed on | Note |
|-----|-----------|------|
| `failure.domain.host`, `failure.domain.zone`, `failure.domain.region` | Deployment nodes, infrastructure nodes, container instances | One key for each level. Set each key once, on the node of that level. Children do not inherit properties |
| `trust.boundary` | Elements and deployment nodes. Never on a group | A group holds no properties. The group name is for display |
| `trust.boundary.crossing` | Explicit relationships | Cross-check only |
| `review.safety.relevant`, `review.safety.justification` | Model | |
| `origin`, `provenance` | Elements and relationships | `origin` is Extracted, Inferred or Proposed |
| `trust.level` | Containers and components | To be confirmed. A privilege tier inside one process (for example administrator, back-office user, API client, plugin). `trust.boundary` stays on deployment nodes and elements at process level |
| `safety.function` | Elements and relationships | To be confirmed. The ID of the safety function that the element is part of. One key per element; an element in two safety functions is recorded in the hazard analysis, not in the model. The property check lists all elements per safety function |
| `failure.domain.placement` | Deployment nodes and container instances | To be confirmed. `fixed` or `scheduler`. With `scheduler`, the host is chosen at run time, `failure.domain.host` is not set, and the placement rules (anti-affinity, spread) are the evidence |

The probe in `.specmgr/feat/feat-267-arch-rvw/probe/` (workspace, negative cases, overlay and the query script `query.py`) re-checks these conventions with one command list. Keys use only the characters a to z, 0 to 9 and the dot. Values are never empty. A key is set once on an element: a repeated key is overwritten by the last value, without a warning (QA 25bd5b93, 0.0680). A property cannot hold a list. Properties appear only in the JSON export. The PlantUML and Mermaid exports drop them, so a query script over the JSON export is the authoritative reader.

### 8.4 To be confirmed

- How a view records the viewpoint it conforms to. A C4 view is a presentation and not a 42010 view. One C4 view can serve several viewpoints, for example the deployment view serves VP06 and VP07 (diagram B). Verified with the probe (Task 120.110): a view takes a `properties` block and keeps it in the JSON export. Convention: the view property `viewpoint` holds the viewpoint IDs, comma-separated when a view serves several (for example `VP06,VP07`). The key name is proposed.
- The keys `principle.dec`, a site key for LO, the reference keys for RG and RS, and the keys `trust.level`, `safety.function` and `failure.domain.placement` of section 8.3. The tag for telemetry relationships (section 8.1).
- One deployment environment for each shipped deployment descriptor and each variant in scope (checklist, section 3).
- Verified with the probe (Task 120.110), no longer open: `!docs` with a local folder; `!adrs` with the madr importer, which must sit inside the software system to satisfy the decision inspection; `workspace extends` with `!element` for a review overlay.
- The mapping of the decoupling modes in section 8.5, and whether a model can carry the direction of the source dependency, for example in a relationship property. No key is proposed yet.
- The same mapping on three contrasting architectures: a traditional enterprise application, a distributed cloud-native platform and a safety-relevant cyber-physical system.

### 8.5 Decoupling modes (our interpretation)

Martin names three modes in which components are decoupled: source level, deployment level and service level (ch. 16, Martin L2434). Ch. 18 adds the local process as a fourth physical boundary form (Martin L2658 to L2730). The validation found a fifth form that Martin does not name, the runtime-loaded module (Apache OFBiz). The choice of mode is an option that a good architecture keeps open (Martin L2434 to L2466). The mapping below is our interpretation and is to be confirmed in Phase 120. Martin gives no C4 mapping.

| Mode | What it is | C4 and Structurizr | Coverage |
|------|-----------|--------------------|----------|
| Source level | Components in one address space that call each other by function calls. One executable, the monolith | C4 components inside one container | partial. Structure only |
| Deployment level | Independently deployable units such as jar files, DLLs or gems. They may share one process | No native construct. The component technology field or a property can name the unit. A key is to be confirmed | none |
| Local process | Separate address space on the same processor. Communication by sockets or queues | C4 containers on the same deployment node | partial |
| Service | A process that assumes a network between it and its partners | C4 containers on different deployment nodes | partial |
| Runtime-loaded module (catalogue extension) | A module with a descriptor that the runtime loads (entities, services, web applications), while the code of all modules is built into one artefact. Neither source level nor deployment level | C4 component, with the descriptor named in a property | partial |

Consequences for criteria:

- A criterion that asks which mode a system uses can read the mode from the model for the process and service levels. It cannot read it for the source and deployment levels.
- The Dependency Rule (PR09) and the acyclic dependency principle (PR10) cannot be evidenced from the containers and the components of a C4 model alone (section 3.4). A code dependency analysis is the evidence. An agent reaches Demonstrated for it only by running a recorded, repeatable check (checklist, section 8.2).

## 9. Related Documents

TXT 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9: Architecture Review Checklist: Viewpoints x Perspectives

QA 25bd5b93-a228-4d6c-8b70-d143dfd39444: Architecture Review Checklist: Decisions and Open Items

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-22 21:30:00.000Z - Draft 0.7

Structurizr probe re-run from a committed location (`.specmgr/feat/feat-267-arch-rvw/probe/`, Task 120.110). Section 8.3 names the probe. Section 8.4: view properties verified, with the convention `viewpoint` = comma-separated viewpoint IDs; `!docs`, `!adrs` (madr, inside the software system) and `workspace extends` verified and removed from the open list. Issue 267. See QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0500.

### 2026-11-22 19:30:00.000Z - Draft 0.6

Applied the Architecture Model part of the Phase 120 validation (QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0690). Section 7: deviation row for the system class preconditions. Section 8.1: VP03 names the data model as the evidence source; VP04 coverage is partial between processes and none inside a process; VP07 telemetry relationships carry a tag and stay out of VP02 views. Section 8.2: the rating sits on the top node or the software system, lower perspectives are evidence. Section 8.3: proposed keys `trust.level`, `safety.function` and `failure.domain.placement`. Section 8.4: the new keys and one environment per descriptor and variant. Section 8.5: the mode runtime-loaded module. Issue 267.

### 2026-11-22 15:30:00.000Z - Draft 0.5

Metamodel corrections after the review. Section 3.1: MatrixRow and CrossView. Section 3.2: a decision applies patterns and tactics (the relation "a pattern implements a principle" is removed, it is not in R+W), and CrossView spans the architecture description. Section 8.2: one Structurizr perspective for each criterion, named by the criterion ID, because a perspective name is unique on an element (verified). The properties `review.criterion` and `review.evidence` are removed. Section 8.3: a repeated property key is overwritten silently (verified). Section 8.4: a C4 view is a presentation of 42010 views. Diagrams A and B changed to match. Issue 267.

### 2026-11-22 14:27:37.000Z - Draft 0.4

Section 5.1: the Development Resource row says "re-scoped to the full lifecycle", the same words as section 5 and the checklist. Issue 267.

### 2026-11-20 11:43:54.000Z - Draft 0.3

Renamed the perspective DevelopmentResource (DR) to Resources (RS) and re-scoped it to the full lifecycle, build and operate. The R+W counterpart Development Resource is named in section 5 and section 5.1; the re-scoping is the catalogue extension. All DR codes in the deviation table, the mapping table and the Structurizr mapping change to RS. Issue 267. See QA 25bd5b93-a228-4d6c-8b70-d143dfd39444, 0.0670.

### 2026-11-18 15:00:00.000Z - Draft 0.2

Clean Architecture (Martin) is now a checked source. New source row in section 2. New sections 3.3 (terms used in two senses: component, boundary, service, layer) and 3.4 (dependency direction). Section 6.1: corrected the example of ports and adapters, which is not in R+W, and added the measurable principles of Martin with their limits. Section 7: two new deviation rows. Section 8.1: the VP05 row names what C4 cannot hold. New section 8.5 with the decoupling modes mapped to C4, labelled as our interpretation. Issue 267.

### 2026-11-18 14:00:00.000Z - Draft 0.1

First draft. Metamodel concepts and two PlantUML diagrams. Viewpoints with the concern lists of the book, and the placement of the extra topics of the earlier checklist lists. The 12 perspectives with the mapping of R+W perspective guidance. Principles, patterns, tactics and decisions with their homes. Deviations from the book. Viewpoint and perspective mapping to C4 and Structurizr. Issue 267.
