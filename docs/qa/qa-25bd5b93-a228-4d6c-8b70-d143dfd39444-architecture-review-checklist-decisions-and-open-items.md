---
classification: null
created: '2026-11-05T08:11:57.662+01:00'
id: 25bd5b93-a228-4d6c-8b70-d143dfd39444
status: draft
type: qa
updated: '2026-11-22T20:30:00.000+01:00'
version: 1.0.0
---

# Architecture Review Checklist: Decisions and Open Items

## General

### Introduction

Decision record and open-item list for the architecture review checklist TXT 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9: Architecture Review Checklist: Viewpoints x Perspectives (renamed in TXT Draft 0.8, formerly "Viewpoints x Quality Characteristics"). Answered questions record decisions taken in the refinement sessions of 2026-11-05. Questions marked `TODO` are open items. The TXT holds only the result of the work. Open items are tracked here.

### Raw Requirements

The raw requirement was a draft checklist from several interviews, using ISO 42010 viewpoints, ISO 25010 quality characteristics, the assessment dimensions AD01 to AD12 and the ISO 29148 characteristics, with the structure viewpoint, quality characteristic, review criteria, assessment, findings and evidence.

## Elicitation Context

<!-- Decisions from the refinement sessions of 2026-11-05. -->

> **0.0010**: What is the source of the assessment dimensions AD01 to AD12?

A draft list collected from several interviews. There is no single reference. The list must not be cited as an ISO standard.

> **0.0020**: Are Security, Safety and Performance viewpoints or quality characteristics?

Security and Safety are viewpoints. Performance is a quality characteristic only. The removed Performance viewpoint is replaced by a Runtime/Process viewpoint at VP12.

Reversed on 2026-11-10 (TXT Draft 0.8, see 0.0520): Security and Safety are perspectives, not viewpoints. Performance Efficiency stays a perspective. The viewpoint VP12 Runtime/Process is now VP04 Concurrency.

> **0.0030**: What is ISO 29148 used for?

It is used to author the checklist criteria. Each criterion is checked against the characteristics of a well-formed requirement.

> **0.0040**: Which format holds the checklist, and which holds open items?

The checklist catalogue is a TXT document and holds only results. Open items and decisions are tracked in this QA.

> **0.0050**: What default applicability does Safety have?

Opt-in. Each review states "safety relevant" or "not safety relevant", with a one-line justification for either decision.

> **0.0060**: Which language and style does the checklist use?

English, plain style.

> **0.0070**: What is the criterion ID scheme?

`VP08-RE-090`: viewpoint, quality characteristic code, three-digit number. Numbers start at 090 and run in steps of 10. Numbers are permanent. They are not renumbered or reused.

Update 2026-11-10 (TXT Draft 0.8): the viewpoint part is now VP01 to VP07 or XV (CrossView), and the second part is a perspective code, for example `VP06-RE-090` (the former `VP08-RE-090`). The viewpoint IDs were renumbered once, with the move to the R+W viewpoint set (0.0520). The old to new table is in 0.0520. From Draft 0.8 on, viewpoint IDs and criterion numbers are permanent.

> **0.0080**: Which dimensions are added to the AD list?

AD13 Necessity, AD14 Economic viability and AD15 Organisational fit.

> **0.0090**: Which rating scale is used?

Single-word ratings: Satisfactory, Partially, Unsatisfactory, Inapplicable, Unassessable. The words follow the first draft, shortened to one word each.

Refined in TXT Draft 0.5: the rating is no longer recorded directly. Each criterion records three fields, each with single-word values: Applicability (Applicable, Inapplicable), Evidence (Sufficient, Insufficient, Missing) and Outcome (Satisfactory, Partially, Unsatisfactory). The five rating words are derived: Inapplicable if not applicable, Unassessable if the evidence is not sufficient, otherwise the Outcome word. The severity of a finding no longer defines the rating.

> **0.0100**: How is maturity handled?

Maturity is rated only on practice criteria, plus one required capability profile per review. Design criteria carry no maturity level. The scale starts with ISO/IEC 33020: incomplete, performed, managed, established, predictable, innovating.

> **0.0110**: Does the review result justify a new artifact type now?

Not yet. Run two or three real reviews as TXT first, linking findings to RSK and DEC artifacts. Then decide.

> **0.0200**: Do the statements about ISO/IEC/IEEE 42010, 29148 and 42030 hold against the standards?

fyi: information about ISO 29148 is in ~/src/docs/md/iso-iec-ieee-29148-2018.md, verify

Partly answered on 2026-11-18 (issue 267, TXT checklist Draft 0.9). Checked against the local texts:

- ISO/IEC/IEEE 29148:2018: the nine characteristics of an individual requirement (clause 5.2.5: Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, Verifiable, Correct, Conforming) and the five characteristics of a set (clause 5.2.6: Complete, Consistent, Feasible, Comprehensible, Able to be validated) match the checklist, sections 6.2. The use for criteria is by analogy, because 29148 is a requirements standard.
- ISO/IEC/IEEE 42010:2011: the concepts viewpoint (5.4), view (5.5), model (5.6), correspondence (5.7), rationale (5.8) and the term model kind exist. Clause 5.6 NOTE 1 cites R+W for perspectives. Annex B.3 cites the 1st edition of R+W (six viewpoints, no Context).
- ISO/IEC/IEEE 42030: missing source. It is only cited in the texts of 12207 and 15288. Please add it to the docs repository.

TODO: check the 42030 statements once the standard is available

> **0.0210**: Does ISO/IEC/IEEE 42030 or ATAM require changes to the structure?

Blocked on 2026-11-18 by missing sources: ISO/IEC/IEEE 42030 (only cited in the texts of 12207 and 15288) and the ATAM report of the SEI (CMU/SEI-2000-TR-004). Neither is in the docs repository.

TODO: answer pending, needs the sources

> **0.0220**: Which capability level names does the current ISACA COBIT version use, and does it differ from ISO/IEC 33020?

Blocked on 2026-11-18 by missing sources. The public ISACA COBIT page and the Wikipedia article do not list capability level names. They are in the COBIT 2019 Framework: Introduction and Methodology and the COBIT 2019 Design Guide, which are not freely available. ISO/IEC 33020:2019 is only cited in the texts of 12207 and 15288. Please add COBIT 2019 and ISO/IEC 33020 to the docs repository.

TODO: answer pending, needs the sources

> **0.0230**: Which practice areas make up the capability profile?

TODO: answer pending

> **0.0240**: How are the overlaps between Functional, Logical and Application/Software, and between Technology/Infrastructure and Deployment, resolved?

Answered on 2026-11-10 (TXT Draft 0.8). The overlaps disappear because the thirteen viewpoints are reduced to the seven core viewpoints of R+W (0.0520). Logical is merged into Functional (runtime structure) and Development (source-level dependency rule). Application/Software is merged into Development. Technology/Infrastructure is merged into Deployment. The remaining boundaries are written in TXT section 4: Functional is runtime, Development is source modules; Deployment is the environment, Operational is how it is run; an interface to an entity outside the system is Context, an interface inside is Functional.

> **0.0250**: How are the overlaps between the AD list and ISO 25010 resolved, namely AD08 and AD10 against Maintainability and Flexibility, and the names shared by AD01, AD03 and AD05 with Functional Suitability?

TODO: answer pending

> **0.0260**: Is Organisational promoted to an actual viewpoint, and are Business/Capability, Scenarios, Evolution and Migration, and Privacy and Regulatory added?

**TODO** What does TOGAF or ISO 42010 say about this?

Partly answered on 2026-11-10 (TXT Draft 0.8), based on R+W (0.0520). Not added as viewpoints: Evolution (it is covered by the perspectives MA and FL), Privacy and Regulatory (perspective RG Regulation), Organisational (perspective DR DevelopmentResource, which covers skills, budget, time and external dependencies), Scenarios (a technique of R+W, ch. 10, used for quality targets), Migration (part of VP07 Operational). Business/Capability is not in the R+W set. VP01 Context holds scope and responsibilities. It can be added per review.

ISO/IEC/IEEE 42010 defines no viewpoint catalogue. Its text names the R+W viewpoints Functional, Information, Concurrency, Development, Deployment and Operational and the perspectives Security, Performance and Scalability, Availability and Resilience, and Evolution as an example (bibliography entry for R+W). It refers to TOGAF only in a list of architecture frameworks.

TODO: check what TOGAF says about a Business/Capability viewpoint, if a review needs one. Missing source (2026-11-18): the TOGAF Standard of The Open Group is not in the docs repository. The BIZBOK (Business Architecture Guild) is in the sources folder of the docs repository and can be checked for capability maps.

> **0.0270**: Is the applicability matrix and its cell count correct?

Partly answered. An external review of 2026-11-05 claimed 28 primary cells. A recount of the table gives 30 primary, 68 secondary (after the change below) and 19 dash cells. The count of 30 stays. Structural fixes were applied: the dash means "no default criteria assigned", P and S were redefined, removal and activation rules were added, and VP11 x SA changed from a dash to S. The matrix stays provisional until the validation in 0.0340 is done. The remaining dash cells were kept. VP11 x RE, VP08 x MA and VP09 x FL can be activated per review if the validation shows a gap.

Superseded on 2026-11-10 (TXT Draft 0.8): the matrix was rebuilt for seven viewpoints plus CrossView and twelve perspectives. The new counts are 32 primary, 47 secondary and 17 X cells, 96 in total. The reasons for each cell are in 0.0530.

> **0.0340**: Does the matrix hold up against three contrasting architectures: a traditional enterprise application, a distributed cloud-native platform, and a safety-relevant cyber-physical system?

Answered on 2026-11-22 (issue 267): yes, the structure holds. Four runs: specmgr (an extra class, single-user local tool), AERIS-10 (safety-relevant cyber-physical system), Apache OFBiz (traditional enterprise application) and the OpenTelemetry Demo (distributed cloud-native platform). Every concern of the four systems found a viewpoint and a perspective. The weak points are a few cell values, missing preconditions (system class, subject, operating profile), missing criteria in the home cells XV x SA and XV x RG, and rules for ratings and evidence. The records and models are in `.specmgr/feat/feat-267-arch-rvw/validation/`, the cross-run summary with 16 results and 15 proposed changes in `validation/synthesis.md`. None of the changes is applied yet.

All 15 proposed changes were accepted by the user on 2026-11-22 and applied, see 0.0690.

> **0.0350**: For each of the three architectures: does every important quality concern have a primary location, do the secondary cells give useful cross-checks without duplicating primary criteria, and which concerns fit no viewpoint?

Answered on 2026-11-22 (issue 267), over the four runs of 0.0340. Primary location: two kinds of main control land in S cells, security input handling (VP02 x SE, runs 1 and 3) and the safety design (VP02, VP04 and VP06 x SA, run 2). The shared data model of an enterprise application has no P cell (VP03 x MA, runs 1 and 3). Duplicates: VP02 x MA and VP05 x MA duplicate only where the runtime calls are the source calls (run 1 yes, run 3 no). Concerns without a home: tenant isolation and an in-process extension interface (run 3), and an LLM agent as user, IC or CO (run 1). See `validation/synthesis.md`, results R4, R7, R9 and R16.

> **0.0360**: Should VP11 x RE, VP08 x MA or VP09 x FL become secondary cells, if the validation shows a coverage gap?

Update 2026-11-10: the question uses the old IDs. In the new matrix (TXT Draft 0.8) the equivalent cells are VP05 x RE and VP06 x MA, and both are already S (0.0530). The old VP09 x FL has no equivalent cell. The nearest one is XV x FL, which is X and can be activated per review.

Closed on 2026-11-18. The question uses IDs that no longer exist, and its answer is in the paragraph above. The remaining coverage questions are tracked by 0.0340, 0.0350 and 0.0550, and by the Table 4-1 comparison in 0.0640.

<!-- Split from 3.0090 (C4/Structurizr). Checked on 2026-11-05 against the Structurizr documentation and the local Structurizr MCP server (DSL tools and PlantUML and Mermaid export, no file access). Items not yet checked are marked "to be confirmed". -->

> **0.0370**: Can a C4 model serve as input evidence for a review, and which C4 views support which viewpoints?

Yes, as evidence. The mapping is many to many, because C4 is not viewpoint based. Draft mapping:

- System context and system landscape view: VP01 Context. A landscape view is a candidate for the Business/Capability viewpoint (0.0260).
- Container view: VP03, VP05 and VP07 together. A C4 container is both a logical unit and a technology unit. This feeds the overlaps in 0.0240.
- Component view: VP03 and VP05.
- Dynamic view: VP12 Runtime/Process, and sequence evidence for VP06.
- Deployment view with infrastructure nodes and health checks: VP08, partly VP07 and VP10.
- Relationship description and technology: evidence for the VP06 interface catalogue.
- Groups, tags and properties: trust boundaries, failure domains and the safety relevance declaration.

Checked with the MCP server: a deployment node with an instance count and a health check is machine readable. A single instance node with no replica is therefore visible in the model. This supports VP08-RE-100 and VP08-RE-120.

Update 2026-11-10 (TXT Draft 0.8): the mapping above uses the old viewpoint IDs. The current mapping is in TXT section 11.6: Container is VP02 Functional and VP06 Deployment, partly VP05 Development. Component is VP02 Functional, partly VP05. Dynamic is VP04 Concurrency, and sequence evidence for the interfaces of VP01 and VP02. Deployment is VP06, partly VP07 Operational. Relationship description and technology is the interface catalogue of VP01 (external) and VP02 (internal). Groups, tags and properties carry trust boundaries (XV x SE), failure domains (VP06) and the safety relevance declaration (XV x SA). The overlaps of 0.0240 no longer exist. The criteria are `VP06-RE-100` and `VP06-RE-120`.

Evidence level: a view drawn from a validated model is Documented. A Structurizr inspection that is run and recorded so that it can be run again is Demonstrated, and Measured when it runs repeatedly in a pipeline, but only for structure claims. Inspections check the model, not the quality targets.

Inspections that fit the architecture-level pass (TXT section 6.4): disconnected element (AD01, AD02), element in no view (AD13), software system with containers but no decisions (AD06), no documentation (AD09), container without technology and relationship without description (AD07). A probe workspace returned six violations with the default severity error, so a review must set the severity per inspection first.

To be confirmed: the same mapping on the three architectures of 0.0340. Pattern catalog entries of Structurizr (microservice, Kubernetes, hardware system) can serve as starting models.

> **0.0380**: Can a review result be shown on a Structurizr model?

Yes, with a limit. A perspective (name, description, value) can be attached to any element and relationship. Proposed use: the perspective name is the checklist perspective (since TXT Draft 0.8 the word is the same on both sides, for example Reliability), the value is the rating word, the description is the finding summary. Properties carry the criterion ID and the evidence strength, for example `review.criterion` `VP06-RE-100` and `review.evidence` `Documented`. Verified with the parse tool: both are kept in the model. Superseded on 2026-11-22 by 0.0680: this holds only one result per element and perspective. A model-level property can hold the safety relevance declaration and its justification.

Limit: a style on a perspective value, for example `Perspective:Reliability[value==Unsatisfactory]`, works in the Structurizr renderer only. In the PlantUML export of the probe workspace the style was not applied. A coloured rating view in an exported diagram needs another way, for example tag based styles. To be confirmed: whether tag based styles survive the export.

To be confirmed: a review as an overlay on the architecture baseline with `workspace extends` and `!element`. This needs file access and cannot be tested with the MCP server. The local Structurizr container mounts a workspace directory and can test it.

> **0.0390**: Which viewpoints and checklist concepts have no C4 equivalent?

No native C4 construct exists for VP02 Functional, VP04 Information/Data, VP09 Security, VP11 Development/Construction and VP13 Safety. VP10 Operational is covered in part only (health checks, infrastructure nodes).

Update 2026-11-10 (TXT Draft 0.8): with the R+W viewpoints the list is shorter and more precise. No native construct: VP03 Information, and the functional capabilities of VP02 (the structure of VP02 is modelled by container and component views). Covered in part only: VP05 Development (technology and component structure, not build, test or codeline) and VP07 Operational. The row XV CrossView (security target, threat model, hazard analysis, regulation register, resource constraints) is not modelled. Quality targets, the rating scale, the maturity levels and the capability profile are not modelled in C4 either. These need other evidence, for example quality attribute scenarios, threat models and hazard analyses. Model properties and perspectives can only reference this evidence.

> **0.0400**: Is tooling or automation for the C4/Structurizr mapping wanted now?

Not yet. This follows the decision of 0.0110 and 0.0320: run two or three real reviews first. Candidates for later, each as a phase in a feature: an inspection step that produces E3 evidence for the architecture-level pass, and a generator that turns a review document into a `workspace extends` overlay.

To be confirmed before any such work:

- `workspace extends` and `!docs` with a local container (see 0.0380).
- Whether the Structurizr PlantUML and C4-PlantUML exports pass the `validate_plantuml` tool of specmgr. A plain PlantUML export of a deployment view passed with two warnings about unclosed rectangle fragments. C4-PlantUML was not tested. It relies on `!include`.
- Whether `!adrs` accepts the MADR format of specmgr ADR documents. DEC documents are not compatible without conversion.

The checklist TXT stays tool neutral. It names no product in its criteria (TXT section 6.2). Update 2026-11-06: the design of a model generation agent is now part of the TXT, in section 11. Product names are confined to that section. The criteria stay tool neutral. See 0.0450.

> **0.0410**: Which source describes the viewpoint and perspective model that the matrix resembles, and how reliable are the two links found?

Partly answered. The Structurizr documentation says that its perspectives come from the book *Viewpoints and Perspectives* (Rozanski and Woods). In that model a viewpoint is a way to look at the architecture, and a perspective is a quality property applied across viewpoints. This has the same structure as the matrix of the checklist. The TXT section 2 does not yet name this source and says only "compiled from several practice sources" for VP01 to VP13.

Links found (secondary sources, from one demo project, not the book):

- https://github.com/humank/genai-demo/blob/a48be6fb9534feb6b35dfc16ae9edab30543f38b/.kiro/steering/rozanski-woods-architecture-methodology.md
- https://github.com/humank/genai-demo/blob/a48be6fb9534feb6b35dfc16ae9edab30543f38b/.kiro/steering/README.md

What the first link shows: seven viewpoints (Context, Functional, Information, Concurrency, Development, Deployment, Operational) as per feature checklists, and four perspectives (Security, Performance and Scalability, Availability and Resilience, Evolution). Of these, Concurrency matches our VP12 Runtime/Process, and Evolution matches in part our Flexibility. It also gives a quality attribute scenario template (source, stimulus, environment, artifact, response, response measure). This template supports the first criterion of every home cell, which asks for the measurable target. The second link is an index of that project and adds nothing for the matrix.

Cautions: the files are written for a Java and DDD project and mix project rules with the methodology. The scenario template comes from the quality attribute work of the SEI, not from Rozanski and Woods. The cited commit is pinned, which is good, but the content is a secondary source and must not be cited as the book.

Resolved on 2026-11-10 (TXT Draft 0.8). The viewpoint list, the perspective list, the definitions and the per-view applicability tables were checked against the text of the book (2nd edition, 2012). The book has seven viewpoints (Table 3-1) and ten perspectives: four in detail (Security, Performance and Scalability, Availability and Resilience, Evolution) and six in brief (Accessibility, Development Resource, Internationalization, Location, Regulation, Usability; Tables 4-2, 24-1 and 24-2). The demo project of the first link lists only four of the ten. The source is now in TXT section 2, and the decision on the other perspectives is in 0.0520.

> **0.0420**: Are the evidence levels E0 to E3 kept as codes?

No. Decided on 2026-11-06 for TXT Draft 0.5. The codes are replaced by three named levels, ordered from weakest to strongest: Documented, Demonstrated, Measured. The order is needed to compare evidence against a minimum. The codes are not needed. E0 is dropped, because evidence that is only asserted is Evidence Missing in the rating. Demonstrated and Measured require a result that someone else can reproduce. A review, an opinion, or the reading of an artefact is not a level.

> **0.0430**: Where is the minimum evidence level defined?

In one policy table in TXT section 8.2, by review type and by criterion type (design or practice). The per-criterion field "Minimum evidence strength" was removed. The reason is that a fixed minimum per criterion made a concept review fail by construction. Provisional values: concept and pre-implementation need Documented for both criterion types. Pre-release needs Documented for design and Demonstrated for practice. A periodic health check needs Demonstrated for design and Measured for practice. To be confirmed against real reviews (see 0.0110).

> **0.0440**: What evidence level can an LLM agent reach, and how is that made visible?

The reading or judgement of an LLM is never evidence by itself. The evidence level is the level of the artefact or result that was read. An agent reaches Demonstrated or Measured only by running a recorded, repeatable check (producer Tool), for example a model parse, a dependency cycle check, or a query for nodes with one instance. Such a check supports structure claims only. Load tests, failover tests and penetration tests come from a person or a pipeline. The agent reads the report and checks its provenance. If the artefact does not exist, the Evidence is Missing and the rating is Unassessable. The evidence record in TXT section 8.2 gets a Producer attribute for this: Author, Human, Pipeline or Tool.

> **0.0450**: Where is the design of the C4 model generation agent described?

In TXT section 11, as a design proposal (TXT Draft 0.6). It is not implemented. It covers scope, inputs and outputs, design principles, origin and provenance, four agents, five skills, two commands, the viewpoint to C4 view mapping, a six-phase flow and the checks. This changes the position of 0.0400, which kept the checklist free of product names. The criteria in TXT sections 6 to 10 stay tool neutral. Section 11 names Structurizr. Building the agent is still not started. The decision of 0.0110 applies: run real reviews first.

> **0.0460**: Where are the outputs of the model generation agent stored, and are they linked from a specmgr artifact?

Proposed in TXT section 11.2: `diagrams/c4/<system>/`.

TODO: answer pending

> **0.0470**: In which format is the facts file written?

TODO: answer pending

> **0.0480**: Does the viewpoint to C4 view mapping live only in the skill c4-viewpoint-mapping, or does the skill read it from the TXT?

A copy in the skill can drift from the TXT.

Answered on 2026-11-18 (issue 267). The mapping is defined once, in TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model), section 8. The checklist section 11.6 now points to it and holds no copy. The skill c4-viewpoint-mapping reads that section and keeps no copy. A viewpoint is catalogue knowledge, so it is meant to become a resource plus a skill. The resource is not built before the design is validated.

> **0.0490**: How many failed check attempts end phase 5 of the flow, and how large is the sample of facts compared with the source?

TODO: answer pending

> **0.0500**: Do the property conventions `trust.boundary`, `failure.domain`, `review.safety.relevant` and `review.safety.justification` survive the Structurizr parse and the exports?

The first two are proposals. The safety properties follow the verified model-level property of 0.0380. To be confirmed with the Structurizr tools.

Verified on 2026-11-06 with a probe workspace and Structurizr 2026.10.26 (image `structurizr/structurizr:2026.10.26-noble`, no network needed). The probe is in `/tmp/opencode/c4-probe/` (`README.md` has the reproduce commands). It is to be moved into a feature folder. Results:

- Properties parse on elements, deployment nodes, infrastructure nodes, container instances, software system instances and relationships. They are kept verbatim in the JSON export.
- Properties are dropped in the PlantUML (Structurizr and C4-PlantUML) and Mermaid exports. A diagram does not show them. The JSON export is the only carrier, so a query script is the authoritative reader.
- `trust.boundary` cannot be set on a group. Inside a software system or deployment environment it is a parse error. In a model-level group it parses, but writes to the model properties. In JSON a group is only a string `group` on each member element.
- There is no inheritance in the JSON. A child does not carry the properties of its parent. A reader must walk the hierarchy.
- Dots, hyphens and spaces in keys, and spaces, commas, semicolons and unicode in values, are kept. An empty value is a parse error. A duplicate key in one block takes the last value silently. Keys are case sensitive.
- Relationship properties exist only on explicit relationships. Implied and instance-to-instance relationships carry none.
- The Structurizr `inspect` command knows nothing about properties. There is no vocabulary enforcement.
- A stdlib-only Python query script grouped instances by failure domain, found shared domains, derived boundary-crossing relationships, reported unset values without failing, and flagged a singleton typo and a group/property conflict.
- Three Structurizr PlantUML exports and one C4-PlantUML export passed the specmgr `validate_plantuml` tool. This also answers part of 0.0400. The Structurizr exports give "unclosed rectangle fragment" warnings on every plain `rectangle ... as X` line. This looks like a false positive of the structure check.

Decisions taken in TXT Draft 0.7: `trust.boundary` on elements and deployment nodes only, never on groups. One key per failure domain level (`failure.domain.host`, `.zone`, `.region`), set once on the node of that level. Keys use `[a-z0-9.]+`. No empty values. Relationship placement is renamed `trust.boundary.crossing` and is only a cross-check against the boundary derived from the endpoints.

Not verified: the full deployment export in the PlantUML validator (only a trimmed subset), image rendering, properties on views, components and deployment groups, the Structurizr MCP server, other Structurizr versions.

TODO: decide where the probe and the query script live (feature folder) and whether the query script becomes the c4-model-checker check.

> **0.0510**: Which pilot runs are used for the model generation agent?

Candidates: this repository for the code path and one SYSRS for the specmgr path. This follows 0.0110.

TODO: answer pending

> **0.0520**: Which viewpoint set and which perspective set does the TXT use, and what happened to the old viewpoints VP01 to VP13?

Decided on 2026-11-10 for TXT Draft 0.8, after the check of the book (0.0410). The TXT can reduce its viewpoints if each one maps clearly to an R+W viewpoint, and it keeps the ISO wording where that makes sense.

- Viewpoints: the seven core R+W viewpoints, VP01 Context, VP02 Functional, VP03 Information, VP04 Concurrency, VP05 Development, VP06 Deployment and VP07 Operational. The names are the R+W names.
- Perspectives: the nine ISO/IEC 25010:2023 characteristics keep their ISO names, order and sub-characteristics. Three R+W perspectives are added because ISO/IEC 25010 cannot express them: RG Regulation, LO Location and DR DevelopmentResource. That gives twelve.
- Not added as perspectives: Usability and Accessibility are part of IC. Internationalization is covered by IC (Inclusivity) and FL (Adaptability). Evolution is split into MA and FL, as in ISO. Scalability stays under FL, as in ISO, although R+W group it with Performance.
- Security and Safety are perspectives and no longer viewpoints (as R+W). Safety is an extension of R+W, which has no safety perspective.
- A new matrix row, XV CrossView, holds the deep criteria that no single view can hold. Its primary cells are the home cells XV x SE, XV x SA, XV x RG and XV x DR. The row is not an R+W viewpoint.
- The assessment dimensions follow: AD11 Compliance is carried by RG, AD14 Economic viability and AD15 Organisational fit by DR. The statement that AD14 and AD15 have no ISO characteristic is obsolete.
- Interfaces: the old Integration/Interface viewpoint is split into VP01 Context (external interfaces) and VP02 Functional (internal interfaces and connectors). Both keep "Interfaces" as a named concern group. Behaviour when an external system fails is assessed in VP06 x RE (VP06-RE-140).

Old to new viewpoint IDs (the IDs were renumbered once, before the catalogue was released):

- Old VP01 Context is VP01 Context.
- Old VP02 Functional is VP02 Functional.
- Old VP03 Logical is VP02 Functional (runtime structure, layering) and VP05 Development (source-level dependency rule).
- Old VP04 Information/Data is VP03 Information.
- Old VP05 Application/Software is VP05 Development.
- Old VP06 Integration/Interface is VP01 Context, VP02 Functional and VP06 Deployment, as described above.
- Old VP07 Technology/Infrastructure is VP06 Deployment.
- Old VP08 Deployment is VP06 Deployment.
- Old VP09 Security is the perspective SE, with its deep criteria in XV x SE.
- Old VP10 Operational is VP07 Operational.
- Old VP11 Development/Construction is VP05 Development. Team ownership and skills are in the perspective DR.
- Old VP12 Runtime/Process is VP04 Concurrency. Load behaviour is in the perspective PE.
- Old VP13 Safety is the perspective SA, with its deep criteria in XV x SA.

The only released criteria were the worked example VP08-RE-090 to VP08-RE-150. They are now VP06-RE-090 to VP06-RE-150. The untracked review file `agent-review-of-txt-23de-sec-5-matrix.md` in the repository root reviews the old matrix and uses the old IDs. It was not changed. It is history.

> **0.0530**: How were the cells of the new matrix decided, and which cells are judgement calls?

Decided on 2026-11-10 for TXT Draft 0.8. A mechanical merge of the old matrix (the highest value wins) would have made VP02 Functional primary in seven of the nine ISO columns, so each cell was decided again under the rule "one primary location for each concern". Guide: the per-view applicability tables of R+W (Tables 25-1, 26-1, 27-1, 28-1, 29-1 to 29-6): P where the viewpoint is where the concern is specified, S where it is a cross-check, X where R+W state little or no impact. R+W have no table for FS, CO and SA, so those columns follow the old matrix. Result: 8 rows, 12 columns, 96 cells, 32 P, 47 S, 17 X. Every viewpoint and every perspective has at least one P. The share of P cells is 33 percent. It was 26 percent in the old matrix (30 of 117).

Reasons by perspective (cells that changed from a straight merge are marked "changed"):

- FS: P in VP01 (scope and completeness) and VP02 (correctness and appropriateness of elements), as before. S in VP03 (information quality) and VP04 (race conditions affect correctness). X in VP05 (no R+W concern; changed from S of the old VP05), VP06, VP07 and XV.
- PE: P in VP04 (contention, throughput), VP06 (hardware capacity, headroom) and VP07 (performance monitoring). S in VP01 (performance of external interfaces), VP02 (R+W: functional structure may change for performance; changed from X), VP03 (shared resources, transactions) and VP05 (R+W: performance guidelines for developers; changed from X of the old VP11). X in XV.
- CO: P in VP01 (external entities and interfaces), VP02 (interfaces and connectors, absorbing the old Integration/Interface; changed from X), VP03 (data exchange semantics and formats) and VP06 (technology compatibility is a named R+W concern of Deployment; changed from S). S in VP04, VP05 and VP07. X in XV.
- IC: P in VP02 only (where the user-facing interfaces are). S in VP01 (specialist devices), VP03 (R+W: information quality affects usability; changed from X), VP05 (R+W: UI guidelines and standards; changed from X of the old VP11) and VP07 (R+W: usability for administrators). X in VP04, VP06 (R+W: little or no impact) and XV.
- RE: P in VP03 (backup, recovery, consistency), VP04 (deadlock, task failure), VP06 (redundancy, failover, disaster recovery site, external dependencies) and VP07 (recovery processes). S in VP01 (availability of external systems), VP02 (offline operation; the old Integration/Interface P was moved into VP06-RE-140, which the worked example already holds in Deployment), VP05 (R+W: modules must support start, stop and restart for failover; changed from X of the old VP11) and XV (Reliability x Safety cross-check; changed from the P of the old Safety viewpoint).
- SE: P in XV (home cell, replaces the old Security viewpoint), VP01 (external connections and trust boundaries; changed from S, takes the old Integration/Interface P), VP03 (sensitive data) and VP06 (R+W: major impact on the deployment environment, trust boundaries on deployment nodes; changed from S). S in VP02, VP04 (isolation into runtime elements), VP05 (guidelines) and VP07 (security assumptions in operation).
- MA: P in VP02 (modularity and responsibilities), VP05 (module organisation, testing standards, instrumentation) and VP07 (analysability through monitoring and logging). S in VP03, VP04 and VP06 (changed from X of the old VP08). X in VP01 and XV.
- FL: P in VP02, VP05, VP06 (scalability, installability) and VP07 (R+W: installation, upgrade and migration are Operational concerns; changed from S). S in VP01 (future external entities), VP03 (flexible information model) and VP04. X in XV.
- SA: P in XV only (home cell). S in all seven viewpoints, as before.
- RG: P in VP03 (R+W: privacy, retention, audit) and XV (identify the applicable regulations, then assess). S in VP01 (interfaces to auditing and regulatory reporting), VP02 and VP07 (regulatory reporting tools and processes). X in VP04, VP05 and VP06 (R+W: little or no impact).
- LO: P in VP06 (R+W: rollout, latency and links are modelled in Deployment). S in VP01, VP03 (distributed data), VP04, VP05 (development at several sites) and VP07 (monitoring distributed systems). X in VP02 (R+W: presented independently of location) and XV.
- DR: P in VP05 (environments, developer skills), VP07 (operating and support capacity, cost) and XV (budget, time, skills, dependencies; AD14 and AD15). S in VP01, VP02, VP03, VP04 and VP06 (R+W Table 29-2).

Judgement calls to check in the validation of 0.0340 and 0.0350: VP06 x CO as P, VP07 x FL as P, VP01 x SE as P, VP06 x SE as P, VP02 x RE as S, VP05 x RE as S, XV x RE as S, and the high share of P cells. If a cell produces duplicate criteria, demote it to S.

> **0.0540**: Which naming rules apply to viewpoints, perspectives and codes?

Decided on 2026-11-10. Names of viewpoints, of the row CrossView and of the perspectives added from R+W are single words without special characters, so that they work in IDs, tags and tool properties: Concurrency (not Runtime/Process), CrossView, Regulation, Location, DevelopmentResource. The viewpoint names follow R+W. The nine ISO perspective names are kept as ISO writes them. Codes: VP01 to VP07 and XV for the row; FS, PE, CO, IC, RE, SE, MA, FL, SA for the ISO perspectives; RG, LO, DR for the added ones.

Superseded in part on 2026-11-20 by 0.0670: DevelopmentResource (DR) is renamed to Resources (RS). The other rules stay.

> **0.0550**: Which of the judgement-call cells of the 8 x 12 matrix stay P or S?

Follow-up of 0.0530 (TXT Draft 0.8). Cells to check: VP06 x CO, VP07 x FL, VP01 x SE and VP06 x SE (all P), and VP02 x RE, VP05 x RE and XV x RE (all S). The share of P cells rose from 26 percent to 33 percent. Rule: demote a cell to S if it produces duplicate criteria. The check is done together with the validation of 0.0340 and 0.0350, which is still open for the new matrix. The TOGAF question stays in 0.0260.

Answered on 2026-11-22 (issue 267), after the four validation runs of 0.0340. None of the four runs reported a duplicate or a misplaced concern in these seven cells, so they stay as they are. Run 4 (C-11) supports VP01 x SE as P: the main security gap of the OpenTelemetry Demo sat there. The cells that did change are other cells, see 0.0690.

> **0.0560**: Should the question text of 0.0360 be rewritten with the new viewpoint IDs?

Follow-up of TXT Draft 0.8. 0.0360 asks about VP11 x RE, VP08 x MA and VP09 x FL. These IDs no longer exist. An update note was added to 0.0360, but the question text is unchanged. Options: keep it as history, or replace it by a question about VP05 x RE, VP06 x MA and XV x FL.

Answered on 2026-11-18. Kept as history. 0.0360 is closed with an update note, and the new matrix is compared with R+W Table 4-1 in the checklist, section 5.3 (see 0.0640).

> **0.0570**: How is the TXT file renamed, now that the title no longer says "Quality Characteristics"?

Follow-up of TXT Draft 0.8. The file name still ends in `viewpoints-x-quality-character`. The specmgr tools cannot rename a TXT file, so the rename is done by hand. It changes the path that other documents or tools may store. The id stays the same.

Answered on 2026-11-18. The file is renamed with git mv. The name now ends in `viewpoints-x-perspectives`. The id is unchanged. Documents refer to the TXT by id, so no reference changes.

> **0.0580**: What happens to the file `agent-review-of-txt-23de-sec-5-matrix.md`?

Follow-up of 0.0520. The untracked file in the repository root reviews the old 13 x 9 matrix and uses the old IDs VP01 to VP13. It was not changed. Options: keep it as history, move it into a feature folder, mark it as superseded at the top, or delete it.

Answered on 2026-11-18. Correction: the file was not untracked. It is in the git history (commit 904c8c74). It is moved with git mv into `.specmgr/feat/feat-267-arch-rvw/`, and a note at the top marks it as superseded by Draft 0.8. The nine ChatGPT transcripts are in `.specmgr/feat/feat-267-arch-rvw/chatgpt/`.

> **0.0590**: How are the Draft 0.8 changes formatted and committed?

Follow-up of TXT Draft 0.8. `mdformat` was not run on the TXT or on this QA. The TXT was already staged and modified before the session, and the QA is untracked. Open: run `mdformat` first, review `git diff`, then decide on one commit or separate commits for the TXT and the QA.

Answered on 2026-11-18. The earlier commits are done (the TXT and the QA are in git). `mdformat` is run on the TXT, the new TXT and this QA after the Draft 0.9 changes. Nothing is committed yet. The user decides on the commits.

> **0.0600**: Is a viewpoint a specmgr artifact?

Decided on 2026-11-18 (issue 267): no. A viewpoint is generic catalogue knowledge, identical for every project, and changes only when the book changes. That is the shape of the resources specmgr://iso25010, specmgr://rasci and specmgr://dtais. A viewpoint fails the tests for a new artifact type (independent lifecycle, own validation, independent traceability): views refer to it by ID and nothing else needs to point at it. The viewpoint definition is meant to become a resource plus a skill. The instances (Structurizr workspaces and views) are the future ARC artifact (issue 228). A project-specific viewpoint that a review adds is recorded as a DEC. Until the resource exists, TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 is the single source.

> **0.0610**: Where do architecture principles and patterns live, and how do we find the ones that apply?

Decided on 2026-11-18 (issue 267). Three levels: the definitions are in the Architecture Model TXT (sections 3 and 6). The generic tags PR01 to PR18 stay in the checklist as a tag vocabulary. An adopted principle or pattern is one DEC document each (statement = Decision Outcome, rationale = Context, implications = Consequences, test = Confirmation). To find the DEC documents that apply: a hub document (the architecture description, a future ARC artifact, until then an index in a TXT) references them, and list_references returns them. The tags `arch.principle` and `arch.pattern` are a convention for people. Scope is general or view-specific, as in R+W chapter 8. One list DEC was rejected, because a principle in a list has no ID, status or reference of its own. Tactics are no DEC documents. No DEC is created before the design is validated. Follow-up: a tag filter in list_dec. The ID schemes AP-NN and PRN-NNN of the ChatGPT sessions are dropped.

> **0.0620**: Which perspective set is used, and how is R+W perspective guidance kept?

Confirmed on 2026-11-18 (issue 267): the 12 perspectives of 0.0520. The Architecture Model TXT, section 5, states the costs of the choice (Scalability in FL, Evolution split, Usability and Accessibility merged, Internationalization divided) and holds a table that maps the concerns, tactics and pitfalls of each R+W perspective to the 12 codes, with chapter references and no copied text.

> **0.0630**: Where are the metamodel diagrams, and how do the TXT documents refer to them?

Decided on 2026-11-18 (issue 267). Two PlantUML class diagrams in `.specmgr/feat/feat-267-arch-rvw/`: `arch-metamodel-a-conceptual.puml` and `arch-metamodel-b-structurizr.puml`. The files are the single source. The TXT refers to them by path and holds no copy. Both parse and render with a local PlantUML jar. The specmgr structure check alone does not render them (no PlantUML source is configured). If the files move to a diagrams folder later, the paths in the TXT must change.

> **0.0640**: Which cells differ from R+W Table 4-1, and what is decided?

Open, found on 2026-11-18 (issue 267). The checklist section 5.3 compares the matrix with the only rating grid of the book (four perspectives). Cells that differ and need a decision: Information x MA and FL (the book rates Evolution High for Information, the matrix has S and S), Context x MA (the book rates Medium, the matrix has X), and the judgement calls with P where the book says Low or Medium (Operational x PE, Information x RE, Context x SE, Information x SE). The rule of 0.0550 applies: demote a P cell if it produces duplicate criteria.

Decided on 2026-11-22 (issue 267), after the validation of 0.0340. VP03 x MA becomes P: the shared data model is the strongest coupling of an enterprise application (runs 1 and 3). VP03 x FL stays S: scalability by data volume (run 1) or by instances (runs 3 and 4) depends on the system class. The other differences from Table 4-1 stay: no run contradicted them. Checklist Draft 0.13, section 5.3.

> **0.0650**: Does Clean Architecture (Martin) support the principle tags PR09 to PR12, and what does it add to the architecture model?

Answered on 2026-11-18 (issue 267), after the book was added to the docs repository as markdown. Checked against `md/clean-architecture-robert-c-martin.md`:

- PR09 is the Dependency Rule of ch. 22. It is stated on source-code dependencies only.
- PR10 is the Acyclic Dependencies Principle and PR11 is the Stable Dependencies Principle with the Stable Abstractions Principle, both ch. 14. The metrics I, A and D are defined there. Martin calls them imperfect, so they are indicators and not thresholds.
- PR12 is supported by ch. 19 and 20 (policy, level, business rules), ch. 22 and ch. 30 to 32 (database, web and frameworks are details).
- Chapter 34 is by Simon Brown, the author of C4. It defines a component in the C4 sense, and Martin's ch. 12 defines it as a deployable unit.

Decisions:

- The book is a source for the principle tags only. It is not a source for viewpoints, perspectives or tactics. Those stay with R+W, 42010 and ISO.
- "Component" in this catalogue means the C4 sense. The Martin sense is "deployable unit". The rules for component, boundary, service and layer are in the Architecture Model TXT, section 3.3.
- A C4 model alone is no evidence for PR09 and PR10, because C4 relationships show the direction of use and not the direction of source dependencies (Architecture Model TXT, section 3.4).
- PR12 joins PR09 to PR11 in the Development viewpoint, as our interpretation (checklist, section 4).
- The mapping of Martin's decoupling modes to C4 containers and components is our interpretation, in the Architecture Model TXT, section 8.5. It is to be confirmed in the validation of feat-267 phase 120.
- The error "ports and adapters as an R+W example" is corrected. R+W do not contain that term. Martin names it in ch. 22.

> **0.0660**: Which sources named in the checklist, section 2, have no markdown copy yet?

Answered on 2026-11-18 (issue 267). Not available as markdown, or not available at all: ISO/IEC/IEEE 42030, the ATAM report of the SEI, COBIT 2019, ISO/IEC 33020, TOGAF and the ISO/IEC 25010:2023 text (see 0.0210, 0.0220, 0.0260 and 0.0620). Also without a copy: Saltzer and Schroeder, Release It!, Enterprise Integration Patterns and the GoF Design Patterns book. PDF files exist, not yet converted to markdown, for the three POSA books (in `sources/praedeep/` of the docs repository). The checklist cites POSA only as a pattern source and as "to be confirmed". Converting them is not part of this feature.

TODO: decide which of these sources to add and convert, in the order of the pattern and principle tags that cite them (PR07, PR08, PR13, PR14)

> **0.0670**: Is the perspective DevelopmentResource renamed, and if so to what?

Answered on 2026-11-20 (issue 267): yes. Renamed to Resources, code RS. One column, no split into development and operating resources. The scope is the full lifecycle (design, build, deploy, operate), which the description in checklist section 5.1, AD15 Organisational fit and the primary cell of the operational viewpoint in that column already expressed; the name caught up with the scope. The R+W counterpart is the Development Resource perspective (Tables 4-2, 24-1, 24-2; named in 0.0410), development-view centric in the book. The re-scoping is labelled a catalogue extension, following the Safety precedent of 0.0520. The book name stays in the sources and in the R+W counterpart column. No criterion carried a DR code, so no criterion ID changed. Checklist Draft 0.11, Architecture Model TXT Draft 0.3.

> **0.0680**: Can one element carry the results of several criteria of the same perspective?

Answered on 2026-11-22 (issue 267), verified with the Structurizr MCP parse tool. No, not with the design of 0.0380. A deployment node with three perspectives named Reliability (VP06-RE-100, -110, -120) fails with the parse error "A perspective named "Reliability" already exists". Properties are no alternative: two `review.criterion` keys on one element parse without an error, and the JSON export keeps only the last value. Perspective names are free text, so a criterion ID such as `VP06-RE-120` is a valid name. Decision for the design proposal: one perspective for each criterion, name = criterion ID, value = rating word, description = evidence level and finding summary. The properties `review.criterion` and `review.evidence` are dropped. Cost: a style selector names one perspective, so a coloured view per perspective code needs one style for each criterion ID, and only in the Structurizr renderer. Architecture Model TXT Draft 0.5, sections 8.2 and 8.3.

> **0.0690**: Which changes follow from the validation against four systems?

Decided on 2026-11-22 (issue 267): all 15 proposed changes of the synthesis (`.specmgr/feat/feat-267-arch-rvw/validation/synthesis.md`, section 3), accepted by the user. Matrix: VP02 x SE, VP03 x MA, VP02 x SA and VP06 x SA from S to P; VP03 x FL stays S; VP02 x MA stays P with the runtime against source split. Counts now 36 P, 43 S, 17 X. Checklist rules: preconditions system class, subject and intended operating profile with default tailoring by class (new section 3.1); Safety gate with hazard types, protected party, development tools and the RE against SA rule; complete-search rule and dependent criteria (7.1); external evidence, object of the evidence and conflicting evidence (8.2); VP06-RE-100 split with the new VP06-RE-160, RE-110 applicability, RE-120 safe state; new home-cell criteria XV-SA-090 to -140 and XV-RG-090 to -110; decisions checked over the decision store, not the Structurizr inspection (11.8). Architecture Model: VP03 evidence source, VP04 coverage, VP07 telemetry tag (8.1), rating against evidence perspectives (8.2), proposed keys `trust.level`, `safety.function`, `failure.domain.placement` (8.3), the mode runtime-loaded module (8.5). Not decided: tenant isolation and extension interfaces as catalogue concerns (synthesis R16). Checklist Draft 0.13, Architecture Model Draft 0.6.

> **0.0280**: Which criteria are knock-out criteria, per review type?

**CHECK** We must not define "knock-out criteria". This can change across organisations and architectures. A final evaluation will be done by a different agent with guidance what "knock-out" in that specifc environment is.

Answered in TXT Draft 0.5. The checklist defines no knock-out criteria. The knock-out rules were removed from TXT section 7.1. A criticality weight stays an optional, separate attribute and is never part of the rating. Which criteria are critical is decided by the final evaluation for the specific organisation and architecture.

> **0.0290**: Is a criticality weight attached to each criterion, and how is it defined?

TODO: answer pending

> **0.0300**: Is the optional numeric report mapping 0/3/7/10 needed for the four scored ratings?

Since TXT Draft 0.5 the rating is derived from Applicability, Evidence and Outcome. A numeric mapping would apply to the derived rating word, not to the three fields. Which of the five words are scored is still to be decided.

TODO: answer pending

> **0.0310**: How is a completed review stored and linked?

TODO: answer pending

> **0.0320**: Is a `specmgr://iso29148` resource worth a separate feature?

It is not worth a feature, but a separate Phase in a feature.

Update 2026-11-22: done. The resource `specmgr://iso29148` exists (feat-173-req-iso29148-level-set, issue 173). It documents the four requirement specifications BRS, StRS, SyRS and SRS, and the characteristics of a requirement set (clause 5.2.6). The characteristics of an individual requirement (clause 5.2.5), which the checklist uses in section 6.2, are not in it.

> **0.0330**: How are the remaining primary cells expanded, and in which order?

TODO: answer pending

## Functional Suitability

## Performance Efficiency

## Compatibility

> **3.0090**: How can we map this architecture assessment with C4/structurizr?

Split into singular questions in `## Elicitation Context`: 0.0370 (C4 model as input evidence), 0.0380 (review result shown on a Structurizr model), 0.0390 (concepts without a C4 equivalent), 0.0400 (tooling and automation) and 0.0410 (source of the viewpoint and perspective model). Short answer: C4/Structurizr is an evidence source and a presentation layer. It is not part of the checklist structure. This question stays here as the entry point and is answered once 0.0370 to 0.0410 are answered.

Answered on 2026-11-18 (issue 267): the mapping is defined in TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09 (Architecture Model), section 8, for each viewpoint and each perspective, with coverage statements. The metamodel is in two PlantUML diagrams in `.specmgr/feat/feat-267-arch-rvw/`. The mapping is a design proposal. The validation (0.0340) and the new probe are open.

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety
