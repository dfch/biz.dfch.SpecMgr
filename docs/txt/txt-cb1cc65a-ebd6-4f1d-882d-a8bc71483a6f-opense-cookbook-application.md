---
classification: null
created: '2026-11-23T17:17:27.147+01:00'
id: cb1cc65a-ebd6-4f1d-882d-a8bc71483a6f
status: draft
type: txt
updated: '2026-11-23T17:55:15.644+01:00'
version: 1.0.0
---

# OpenSE Cookbook Application

This document records how the ideas of the OpenSE Cookbook can be applied to the architecture modelling in this repository. Our architecture modelling is the catalogue of TXT 30983f27, the review checklist of TXT 23ded6d8 and the C4 models in Structurizr. The ideas are:

- the pattern format;
- property-based requirements;
- the OOSEM design layers;
- the deployment and context patterns;
- the information and physical perspectives;
- model validation rules;
- the layered catalogue;
- the workflow volumes.

This document is a proposal. Nothing here is implemented.

Tracking: GitHub issue 267, feature feat-267-arch-rvw. Downstream: issue 228 (ARC artifact) and issue 250 (C4 agent skills).

## 1. Sources and Status

| Source | What it is | Status |
|--------|------------|--------|
| github.com/Open-MBEE/OpenSE-Cookbook, license Apache-2.0 | The Cookbook itself. MagicDraw models generated from the server version of the Cookbook (Cameo Systems Modeler 19.0 SP2, MDK 4.1.3), the 2011 material, SysML v2 notebooks, VQL validation rules, the TMT model | Read. `Models/OpenSE Cookbook.mdzip` (28 MB) was unpacked and its packages and view text were extracted on 2026-11-23. The text is View Editor HTML inside the model |
| Printed documents of the Cookbook (public Google Drive folder "OpenSE Cookbook documents V2", linked from the repository README; subfolders Mar2023, Sep2023, Oct2023) | Documents generated from the model with DocGen (pandoc, Prince) | Oct2023 set downloaded and read on 2026-11-23: "OpenSE Cookbook.pdf" (479 pages, generated 2023-09-08), "OpenSE Cookbook Management.pdf" (13 pages), "About Reusable DocGen Methods.pdf", "Exposed Diagrams for OpenSE Cookbook.pdf" (315 pages, diagrams only, not read). The Mar2023 and Sep2023 sets were not read |
| OpenMBEE server, guest login named in the repository README | The original versions | Not read |
| R. Karban, A. G. Crawford, G. Trancho, M. Zamparelli, S. Herzig, I. Gomes, M. Piette, E. Brower, "The OpenSE Cookbook: A practical, recipe based collection of patterns, procedures, and best practices for executable systems engineering for the Thirty Meter Telescope", Proc. SPIE 10705, 2018 | Paper about the Cookbook | Read in full. The paper is "© 2018. All rights reserved": paraphrase only |
| TXT 0881bc3f-cc34-463d-9eeb-a919c5cd934c | Our C4 trial on the TMT model, which is the main case study of the Cookbook | Ours |

### 1.1 License and attribution

The Cookbook repository is under the Apache License, Version 2.0. Content taken from it, such as pattern names, the pattern template or short descriptions, is allowed with attribution and a reference to the license. This document paraphrases. Copy the text of a pattern into the repository only with a NOTICE, as done for the TMT model in `.specmgr/feat/feat-267-arch-rvw/tmt/NOTICE`. The SPIE paper is not under the Apache license.

### 1.2 Local copies

The Oct2023 PDFs and the SPIE paper are in the sibling docs repository, under `sources/openmbee/` (git-ignored, not committed). Markdown conversions with figure crops are in `md/opense-cookbook-2023-10.md`, `md/opense-cookbook-management-2023-10.md`, `md/opense-cookbook-reusable-docgen-methods-2023-10.md`, `md/opense-cookbook-exposed-diagrams-2023-10.md` and `md/opense-cookbook-spie-2018-karban.md`. They were made with SOP c79d22e9, using the separate module `src/docs/openmbee.py` (profiles for the pandoc + Prince prints and for the SPIE paper). Tables are kept as flagged fenced text, because Prince sets words without space glyphs and grid reconstruction loses the spaces.

## 2. What the OpenSE Cookbook Is

- A collection of patterns, procedures, guidelines and best practices for model-based and executable systems engineering with SysML. The repository README calls engineering cookbooks a compendium of best practices and lessons learned, with guidance on how to use languages and tools for an engineering task.
- Origin: JPL, with TMT and ESO. The content grew from two models: the TMT model (APS, NFIRAOS), and the 2011 INCOSE "Cookbook for MBSE with SysML", whose case study is the ESO Active Phasing Experiment (APE). The 2011 material is in the repository (`2011Material/`).
- The Cookbook introduction says that each project must set a minimal set of rules for the use of SysML and for the organisation of the model, and that the recipes solve day-to-day modelling problems. It assumes knowledge of SysML and is not a SysML introduction.
- Method: ESEM, the Executable Systems Engineering Method. ESEM refines OOSEM with executable models.
- OpenMBEE is the tool environment (model server, MDK, View Editor, DocGen). The Cookbook is written in it: every chapter is a View with Viewpoints, and the documents are generated from the model.

### 2.1 Volumes and patterns

The model package `Content to-be` holds ten volumes. The table uses the package names of the model. The printed document of October 2023 numbers them differently: 01 Systems Requirements Management, 02 Systems Design Management, 03 Systems Interface Management, 04 Systems Analysis Management, 05 Interdisciplinary Integration, 06 Systems Trade Study Management, 07 Systems Resource Management, 08 Antipatterns, 09 Miscellaneous, 99 Work in Progress. In print, the Systems Environment chapters, Context Modeling, Variant Modeling, the Trade Study Pattern and the interface chapters are in 99 Work in Progress.

| Volume | Patterns and chapters |
|--------|-----------------------|
| 01 Systems Environment | Introduction, Project Description, MBSE Goals, How Do I Get Started?, Model Organization, Styles, Layout, Naming |
| 02 Systems Requirements Management | Property Based Requirements Pattern, Requirement Verification Pattern, Use Case Modeling (with TMT use cases); guidelines for context modelling and for requirements |
| 03 Systems Design Management | Behavioral Modeling, Customer/Supplier Pattern, Constraint Patterns, Structure Modeling, Frame of References and Coordinate System Pattern, Model Organization/Abstraction Pattern, Enabling Activity Reusability in States Pattern, Abstraction Layer Traceability Pattern, Deployment Pattern |
| 04 Systems Interface Management | Interface Modeling: interface elements and their SysML representation, Interface Pattern, Protocol Pattern, layered interface model, network interface examples |
| 05 Systems Analysis Management | Black Box Specification with Property Based Requirements, Monte Carlo Simulations, Multi-Scenario Analysis Pattern, Duration Analysis Pattern, Scenario Modeling Pattern |
| 06 Interdisciplinary Integration | Cross-Cutting the Model and Traceability, Integration with other disciplines |
| 07 Systems Trade Study Management | Variant Modeling, Trade Study Pattern |
| 08 Systems Resource Management | Quantities, Units, Dimensions and Values; Roll-up Patterns; Time Modeling; Error Budgeting |
| 09 Antipatterns | A chapter without text in the model |
| 10 Miscellaneous | Guidelines for Modeling Non-Functional Aspects, Domain Specific Model Extensions, Systems Reasoner, WBS/Orgchart Pattern, Aggregation of Convenience Pattern |

A package `99 Work In Progress` holds drafts. The most relevant draft for us is chapter 6 "System Views" of the 2011 version (section 4.6).

### 2.2 Pattern template

The model has a package `Templates/Pattern Documentation Template` with these sections, paraphrased:

| Section | Content |
|---------|---------|
| Intent | The goal behind the pattern and the reason to use it |
| Motivation | The situations and the context in which the pattern is usable |
| Concept | The structure of the pattern |
| Simulation | How the elements interact when simulated |
| Consequences | Results, side effects and trade-offs |
| Known Uses | Real uses of the pattern |
| Analysis | How the pattern helps to analyse a system model |

The printed document (October 2023, chapter 2 "Pattern Template") has a different set of eight views: Intent, Motivation, Concept, Consequences, Implementation, Known Uses, Tooling, Related Patterns. This is the same set as in the 2018 paper. The template package in the model is therefore not the template the print uses. The patterns do not follow either set exactly: some add Participants or Analysis, and the Deployment Pattern uses Intent, Applicability, Structure, Consequences, Sample Model, Known Uses, Analysis, Conflicting Usages, Related Patterns. For proposal 5.1, the print is the reference, and Analysis is taken from the model template.

### 2.3 Other assets in the repository

| Folder | Content | Relevance for us |
|--------|---------|------------------|
| `Models/` | OpenSE Cookbook, OpenSE Library, TMT, APE reference model, DocGen, PBR cross-reference demo | Source of the patterns. MagicDraw format |
| `SysML2x/RollUpPatterns/` | Jupyter notebooks with roll-up patterns in SysML v2 textual notation (static roll-up, recursive roll-up, power roll-up) | Text, readable without a proprietary tool. A model for a roll-up script (section 5.6) |
| `SAIC-DE/vql/` | Validation rules for a digital engineering profile, in the VQL query language: requirements, sequence diagrams, state machines, structure, system context, use cases, activities, completeness, flows, forbidden elements, interfaces, parametrics | A catalogue of model validation rules. Compare with Structurizr `inspect` and our `query.py` (section 5.7) |
| `MapleMBSE/` | Spreadsheet front end for model data (ICD examples) | Not relevant |
| `2011Material/` | The 2011 Cookbook (two volumes), APE models, presentations | Background |

### 2.4 Limits

- Efficient use of the patterns needs tooling. The Cookbook uses Cameo Systems Modeler, the Cameo simulation toolkit, MDK and the Systems Reasoner.
- The executable parts (simulation, Monte Carlo, parametric solving) run in Cameo.
- Many patterns are marked DRAFT in the model. The Antipatterns volume is empty, in the model and in the October 2023 print (section 10, an empty introduction).
- The Cookbook is maintained through an OpenMBEE Jira and Slack channel ("OpenSE Cookbook Management.pdf"), with a review table that maps the GitHub resources to chapters.

## 3. Patterns of Direct Interest

Paraphrased from the view text of the Cookbook model.

### 3.1 Requirement Verification Pattern

- Context: the system specification sits in an enterprise. It can be generalised by a conceptual design, a conceptual node design or a physical design (OOSEM). Property-based requirements belong to the system specification.
- The conceptual node design specifies functional, technology-independent components and their behaviour. Components talk through signals over ports.
- An analysis context holds the structure, the constraint blocks, the test results, and the simulation configuration. It does not change the system. Each verification scenario is a specialisation of the analysis context.
- TMT use: the APS post-segment exchange alignment shall take at most 7200 s. The simulated scenario took 4804 s, so the requirement passed (SPIE paper).

### 3.2 Property Based Requirements Pattern

- Intent: express numerical requirements as model properties, constraints and equations. This reduces ambiguity and enables verification by analysis.
- A generic property-based requirement is specialised into a domain property-based requirement, which owns a constraint block.
- The Cookbook notes that the TMT model uses plain blocks, not the library stereotype, for its formalised requirements.

### 3.3 Black Box Specification with Property Based Requirements

- From OOSEM. A black-box specification describes the externally observable behaviour and the physical characteristics of a system, not how the system achieves them. It can be applied at any level: system, element, component.
- A black-box specification captures functions, properties and interfaces. It is realised by one or more physical architectures.

### 3.4 Customer/Supplier Pattern

- The customer system specification is a black box. The supplier system specification specialises it, and inherits and redefines its property values.
- The customer gives a conceptual (functional) design component and a realisation design component. Property-based requirements can be applied to the decomposed components.

### 3.5 Deployment Pattern

- It relates the black-box specification of a system to the environments in which it is actually deployed. Its intent is a repeatable pattern for the realisation of an application or service environment in relation to the physical deployment (print, section 4.7.1).
- After the abstraction layers of a system are described, the next step is its actual deployments. The pattern applies to software, but also to other systems. Its main benefit is several specifications for several environments, each with its own set of implementations (print, section 4.7.2).
- A specification realisation holds all possible parts, ports and connections. The production environment specialises it and fixes the concrete servers, tools and versions. A test environment specialises production, not the specification, because it is meant as a variation of what is actually deployed.
- A rationale element on the diagram marks each difference between environments.
- Consequence: a design change propagates through the specialisations. With many deployments it can be cumbersome to keep them consistent.

### 3.6 Context Modelling (Requirements Management guidelines)

- The context diagram fixes the system scope and the system boundary. It shows the system as a black box with all interacting external elements (systems, persons).
- Information flow to external elements can be shown as flow items on the connections. Avoid clutter. If necessary, make one diagram for the information flow to each external system.
- Interfaces can be modelled at block level or at part level. An abstract interface can represent an ICD. Keeping the ICD document and the model consistent is a known problem.

### 3.7 System Views and perspectives (2011 chapter 6, draft)

- The views that are necessary depend on the purpose of the model. The 2011 Cookbook names these aspects: behavioural (functional), context, data, performance, requirements (with the use case model), structural, variations, verification.
- It adds domain perspectives for a cyber-physical system: a mechanical perspective (each part has a counterpart in the CAD tool, with synchronised properties such as mass and size) and an optical perspective (how the light beam propagates, with optical properties such as transmission; the counterpart is an optical design tool).
- It states that it does not use SysML views for this purpose. The reason given: a SysML view may not contain model elements, but the authors wanted the elements of an aspect grouped together with its diagrams (print, section 12.3.1). This is the same tension we have: a C4 view is a presentation, while a 42010 view also holds models (TXT 30983f27, section 8.4).

### 3.8 Information and physical perspectives (Interdisciplinary Integration)

- A control system needs at least two perspectives. The information perspective has components, ports and data flows. The physical perspective has the transport layer (CAN bus, Ethernet, RS-232).
- Start with the information perspective. The physical connection is often not known at that time.
- Allocation: a single allocate dependency has one supplier and one or more clients. Allocation of an activity is always a 100 % allocation.

### 3.9 Roll-up and error budget

- Recursive static roll-up: total = sum of the children + own value. The aspect is a block with a recursive part property.
- Error budget: trace the maximum allowable value, the current best estimate and its growth through the system hierarchy. TMT use: the M3 tip/tilt error budget against the telescope pupil alignment requirement of the APS.

## 4. Mapping to This Repository

| Cookbook concept | Repository concept | Fit |
|------------------|--------------------|-----|
| Pattern template (section 2.2) | A pattern DEC (TXT 30983f27, section 6.3) | Good (section 5.1) |
| Layers: generic, institutional, project (SPIE paper) | Three levels of TXT 30983f27, section 6.2 | Good. The same idea is already in place |
| Volumes by engineering workflow | Skills and prompts of the C4 agent (issue 250) | Good |
| Property-based requirement | REQ with a measurable EARS statement plus a VCR acceptance criterion with method Analysis | Partial. The binding to a model property is a convention, not a construct |
| Requirement Verification Pattern | Checklist evidence level Demonstrated: a recorded check over the Structurizr JSON export | Partial. Static checks only |
| Black Box Specification, Context Modelling | VP01 Context: C4 system context view | Good. A gap: C4 has no flow items. The relationship description carries the data |
| OOSEM layers: enterprise, black box, conceptual design, conceptual node design, physical design | C4 context (VP01), container and component (VP02), deployment (VP06) | Good for structure. The TMT model uses these layers as packages |
| Customer/Supplier | SYSRS for the customer view; ARC artifact for the supplier design | Partial |
| Deployment Pattern | Structurizr: one deployment environment for each deployed variant (TXT 30983f27, section 8.4) | Good in intent. Structurizr has no specialisation of environments. `workspace extends` is the nearest mechanism |
| Information and physical perspectives | VP02 Functional against VP06 Deployment; relationship technology for the transport | Partial. Matches the TMT lesson: physical elements need a rule |
| Mechanical and optical perspectives | None | None. This is the gap that the TMT trial found (TXT 0881bc3f, section 4.2) |
| Roll-up, error budget | Numeric properties summed by a script over the JSON export | Possible, not tested |
| VQL validation rules | Structurizr `inspect`, `query.py`, `specmgr lint` | Good in intent. A rule catalogue is a model for our checks |
| Duration, Monte Carlo, Multi-Scenario Analysis | Nothing | None. These need an executable model |
| DocGen, View Editor, Viewpoints | `specmgr docs`, the Structurizr static site, the view property `viewpoint` | Partial |

## 5. Proposals

### 5.1 Pattern DEC template from the Cookbook template

A pattern DEC records the decision to adopt a pattern (TXT 30983f27, section 6.3). Use the Cookbook template to fill it:

| Cookbook section | DEC section |
|------------------|-------------|
| Intent | Title and first sentence of Context and Problem Statement |
| Motivation | Context and Problem Statement, with the preconditions |
| Concept, Participants | Decision Outcome: the structure of the pattern |
| Consequences | Consequences, positive and negative |
| Implementation, Simulation | More Information: a reference to an example in the repository |
| Known Uses | Source |
| Analysis | Confirmation: how a model shows that the pattern is applied |
| Related Patterns | Related Artifacts: DEC references, so that list_references finds them |

The section Analysis is the nearest equivalent of the DEC section Confirmation. A pattern with no Analysis needs one before it can be a DEC.

### 5.2 Property-based requirements for architecture criteria

For a criterion with a measurable target (instance count, failure-domain spread, latency budget, number of trust boundary crossings):

1. The REQ states the target in EARS form with a value and a unit.
2. The model carries the value as a property of the element. The key is to be confirmed, for example a reference `req.id`.
3. The VCR has one acceptance criterion with method Analysis. Its test steps run the recorded script over the JSON export.
4. The script prints pass or fail for each bound requirement.

This needs a property key convention in TXT 30983f27, section 8.3, and a check in `query.py`.

### 5.3 OOSEM layers as the order of work for the model generation agent

The agent of issue 250 builds the model in this order:

1. The context and the black box (VP01), with all external interfaces.
2. The white box (VP02).
3. The deployments (VP06), one environment for each variant (section 5.4).

Do not start a layer before the previous one is complete.

### 5.4 Deployment variants after the Deployment Pattern

Record in TXT 30983f27, section 8.4, how a variant is modelled. Our proposal is the following:

- One base workspace holds the realisation with all options.
- Each environment is a deployment environment.
- A variant that differs from production records the difference in a property, for example `variant.rationale`. The key is to be confirmed.

Test whether `workspace extends` can carry a variant without copying the base.

### 5.5 A rule for physical elements, from the perspectives

The TMT trial put hardware into C4 containers (TXT 0881bc3f, proposal 1). The Cookbook separates an information perspective from a physical one, and adds domain perspectives (mechanical, optical) for cyber-physical systems. Proposal:

- Containers and components stay in the information perspective (VP02).
- Physical assemblies become deployment nodes or infrastructure nodes (VP06), with a tag `Physical` and the domain as a property (for example `domain` = `optical`).
- Mechanical and optical properties stay in the domain tools. The model names the counterpart only.

This proposal goes to TXT 30983f27, section 3.3 or 8.

### 5.6 Roll-up script (later)

Write a script over the JSON export, modelled on the SysML v2 roll-up notebooks of the Cookbook. It computes total = sum of the children + own value for numeric properties such as `resource.mass.kg` or `resource.power.w`, with a margin check against a REQ. Do it only when a real system needs it.

### 5.7 A catalogue of model validation rules

The VQL rules of `SAIC-DE/vql/` are grouped by concern: completeness, system context integrity, interface integrity, flow integrity, forbidden elements. Today, our checks are spread over three tools: Structurizr `inspect`, `query.py` and the property conventions. Proposal: list our checks in the same grouping, with one ID for each rule. Each rule names the criterion of the checklist that it gives evidence for.

### 5.8 Layered catalogue and workflow volumes

- Record in TXT 30983f27, section 6.2, that the three levels follow the same idea as the Cookbook hierarchy (generic, institutional, project).
- Group the skills of issue 250 by engineering task, as the Cookbook groups its volumes: context, interfaces, deployment variants, verification, resources.

## 6. What Does Not Transfer

- Execution: activity simulation, Monte Carlo runs, parametric solving, duration and multi-scenario analysis. Structurizr has none of them.
- Generalisation and redefinition of blocks (Customer/Supplier, Deployment Pattern). Structurizr has no inheritance between elements or environments.
- Flow items on connections. A C4 relationship has a description and a technology only.
- The SysML model library and the Systems Reasoner. They are MagicDraw artefacts.

## 7. Open Questions

- Which property key binds a model element to a REQ (section 5.2), and which key records a variant difference (section 5.4)?
- Is a VCR the right home for an architecture criterion check, or does the checklist evidence rule (TXT 23ded6d8, section 8.2) already cover it?
- Is the rule for physical elements (section 5.5) enough for a safety-relevant cyber-physical system, or does it need a catalogue viewpoint of its own?

## 8. Related Documents

TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09: Architecture Model: Viewpoints, Perspectives and Structurizr Mapping

TXT 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9: Architecture Review Checklist: Viewpoints x Perspectives

TXT 0881bc3f-cc34-463d-9eeb-a919c5cd934c: TMT C4 Model: Results and Lessons for the Architecture Model

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-23 18:00:00.000Z - Draft 0.3

The printed Cookbook (Google Drive, October 2023 set, "OpenSE Cookbook.pdf", 479 pages) was read. Section 1: the Drive folder and the files read. Section 2.1: the numbering of the print. Section 2.2: the print has the eight-view template of the paper, not the template package of the model. Section 2.4: Antipatterns empty in print too; maintenance through Jira and Slack. Section 3.5: intent and applicability of the Deployment Pattern from the print. Section 3.7: the reason why the 2011 Cookbook does not use SysML views. Section 7: the question about the printed documents is closed. Issue 267.

### 2026-11-23 17:45:00.000Z - Draft 0.2

The Cookbook itself was read: the repository github.com/Open-MBEE/OpenSE-Cookbook (Apache-2.0), with the package structure and the view text of `Models/OpenSE Cookbook.mdzip`. Section 1 now lists the repository as the main source, with license and attribution. Section 2 has the ten volumes, the pattern template of the model, and the other assets (SysML v2 roll-up notebooks, VQL validation rules). New section 3 with nine patterns of direct interest. Section 4 has more mappings. New proposals 5.4 (deployment variants), 5.5 (rule for physical elements) and 5.7 (catalogue of validation rules). Issue 267.

### 2026-11-23 17:30:00.000Z - Draft 0.1

First draft. Summary of the OpenSE Cookbook from the SPIE 2018 paper, mapping to the repository, six proposals, what does not transfer, open questions. Issue 267.
