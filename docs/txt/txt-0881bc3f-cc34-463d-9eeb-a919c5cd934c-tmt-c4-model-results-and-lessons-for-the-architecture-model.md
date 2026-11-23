---
classification: null
created: '2026-11-23T16:54:55.699+01:00'
id: 0881bc3f-cc34-463d-9eeb-a919c5cd934c
status: draft
type: txt
updated: '2026-11-23T17:17:31.843+01:00'
version: 1.0.0
---

# TMT C4 Model: Results and Lessons for the Architecture Model

Report of a trial: a C4 model in Structurizr of the Thirty Meter Telescope (TMT), made from the public TMT SysML model, with the viewpoints and property conventions of TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09. It records what was created, what worked with the source model and with the modelling requirements, and what did not.

Tracking: GitHub issue 267, feature feat-267-arch-rvw. The TMT system is the third contrasting architecture that TXT 30983f27 section 8.4 asks for: a safety-relevant cyber-physical system.

## Attribution

The architecture in this report is not ours. The work here is the C4 mapping only.

- Telescope design: TMT Observatory Corporation (TMT International Observatory).
- SysML model: Jet Propulsion Laboratory, California Institute of Technology, published at github.com/Open-MBEE/TMT-SysML-Model under the Apache License, Version 2.0. Copyright (c) 2016, California Institute of Technology ("Caltech"). U.S. Government sponsorship acknowledged. All rights reserved. The full copyright notice, its conditions and its disclaimer are reproduced in `.specmgr/feat/feat-267-arch-rvw/tmt/NOTICE`, and the license text in `LICENSE-Apache-2.0` next to it. Both are also in the static site folder.
- Method and environment: Executable System Engineering Method (ESEM) and OpenMBEE.
- Publications on the model:
  - R. Karban, F. G. Dekens, S. Herzig, M. Elaasar, N. Jankevičius, "Creating system engineering products with executable models in a model-based engineering environment", Proc. SPIE 9911, 99110B, 2016.
  - S. Herzig, R. Karban, G. Trancho, F. Dekens, N. Jankevičius, M. Troy, "Analyzing the Operational Behavior of the Alignment and Phasing System of the Thirty Meter Telescope using SysML", AO4ELT5, 2017.
  - R. Karban, A. G. Crawford, G. Trancho, M. Zamparelli, S. Herzig, I. Gomes, M. Piette, E. Brower, "The OpenSE Cookbook", Proc. SPIE 10705, 2018.

The derived files (workspace, documentation, PlantUML sources, SVGs, static site) carry this attribution: a header comment and the model property `copyright` in `workspace.dsl`, an Attribution section in `docs/01-provenance.md`, and a footer on each SVG. This derived work is not endorsed by Caltech, JPL or the TMT Observatory Corporation. The names of Caltech and JPL are used here for attribution only.

## 1. Source

| Item | Value |
|------|-------|
| Repository | github.com/Open-MBEE/TMT-SysML-Model, license Apache-2.0 |
| File used | `EA/TMT_mtip.zip`, MTIP 2022x XML export of 2025-06-12 (90 MB unpacked) |
| Files not used | `TMT.mdzip`, `TMT-2024x.mdzip` (MagicDraw/Cameo, proprietary tool), `EA/TMT.qeax` (Enterprise Architect) |
| Packages used | `01 TMT PO/System Model/TMT Observatory/.../Logical Design` (34 logical system components), `02 JPL/System Model/APS` (mission, logical design, physical design) |
| Tool | Structurizr 2026.10.26 (Docker image `structurizr/structurizr:2026.10.26-noble`), PlantUML server on 127.0.0.1:8080 |

The modelling method of the source is ESEM (an extension of the INCOSE OOSEM method) on the open-source OpenMBEE environment. The modelling tool itself is not open source.

## 2. What Was Created

All files are in `.specmgr/feat/feat-267-arch-rvw/tmt/`, except the two metamodel SVGs.

| File | Content |
|------|---------|
| `workspace.dsl` | The Structurizr workspace: 2 persons, 1 software system, 34 containers in 6 groups, 11 APS components, 65 explicit relationships, 1 deployment environment, 7 views |
| `docs/01-provenance.md` | Documentation section (`!docs`): source, limits, viewpoint coverage |
| `adrs/0001-derive-the-c4-model-from-the-mtip-export.md` | One MADR decision (`!adrs ... madr`) |
| `static/index.html` | Static site export (`export -f static`), 2.5 MB, all assets local. Interactive viewer for all 7 views |
| `puml/*.puml` | C4-PlantUML export of the 7 views, the intermediate source of the SVGs |
| `svg/*.svg` | The 7 views as SVG, rendered from `puml/` |
| `arch-metamodel-a-conceptual.svg`, `arch-metamodel-b-structurizr.svg` | SVGs of the two metamodel diagrams of TXT 30983f27, next to their PNGs |
| `NOTICE`, `LICENSE-Apache-2.0` | Attribution, the verbatim copyright notice of the source, and the license text. Copies in `static/` |
| `out/` | JSON export, PNGs. Not committed (`.gitignore`) |

### 2.1 Views and viewpoints

Each view carries the view property `viewpoint` (TXT 30983f27, section 8.4).

| View | Viewpoint | Content |
|------|-----------|---------|
| `context` | VP01 | The APS User and the APS Operator, and the TMT Observatory System |
| `containers` | VP02 | The 34 logical subsystems, grouped |
| `aps-neighbours` | VP02 | The APS and its interfaces to M1CS, TCS, ESW and Common Services |
| `laser-safety` | VP02, applied perspective SA | The laser propagation chain, property `safety.function` = `laser-propagation` |
| `aps-components` | VP02, VP05 | The 11 APS logical parts and 33 relationships |
| `aps-guide-loop` | VP04 | Dynamic view of the APT guide loop between ESW, APS and TCS |
| `deployment` | VP06, VP07 | Summit site with `failure.domain.*` properties. Illustrative |

No view for VP03 Information and XV CrossView. This agrees with the coverage "none" in TXT 30983f27, section 8.1.

### 2.2 Provenance

| `origin` | Elements | Relationships | Basis |
|----------|----------|---------------|-------|
| Extracted | 48 | 34 | SysML blocks, part properties, connectors, sender and receiver pairs of signals |
| Inferred | 0 | 29 | Names of behaviours and workflow steps |
| Proposed | 0 | 2, and the deployment nodes except the APS optical bench | Not in the SysML model |

The 10 relationships with no `origin` are implied relationships that Structurizr makes itself.

### 2.3 Checks

| Check | Result |
|-------|--------|
| `structurizr validate` | OK |
| `structurizr inspect` | 3 findings: the containers TTS, NSEN and ESEN are disconnected. Kept by intent (section 4) |
| `query.py` of the probe | 15 findings VP06-RE-100 (one instance, no replica). They come from the illustrative deployment, not from TMT. The safety-function check passes |
| `specmgr plantuml-check` with the URL source | All 9 PlantUML files: valid, rendered |
| Static site in a browser | All views render, 0 console errors |

## 3. What Worked Well

### 3.1 With the source model

- The MTIP export is open XML, and you can read it without the proprietary tool. A short standard-library script makes an index of all 42,000 elements with type, name, owner and relations.
- The logical design is clean. The block `TMT Observatory System Logical` has one part property for each of the 34 subsystems. They map one to one to C4 containers.
- The APS part is complete enough for a C4 component view. The block `APS Logical` has 11 parts and 41 connectors with named ports (for example `PEAS2M1CSOut`). The port names give the direction.
- Signals give the direction of the data flow. A `SendSignalAction` in the behaviour of one block, and a `Trigger` on the same signal in another block, give a sender and receiver pair. This confirmed most of the connector directions.
- The physical design of the APS (Optical Bench, SH and PIT assemblies) gives one deployment node that is Extracted and not Proposed.
- Stakeholder blocks (APS User, APS Operator) map to C4 persons.

### 3.2 With the modelling requirements of TXT 30983f27

- `origin` and `provenance` on each element and relationship were easy to apply. They made the difference between Extracted, Inferred and Proposed visible in every place. A reviewer can see at once which relationships rest on the source.
- The view property `viewpoint`, with comma-separated values, held the many-to-many mapping of views to viewpoints without a problem (`VP02,VP05`, `VP06,VP07`).
- `safety.function` on the elements and on the relationships made the laser propagation chain a query result. The probe script `query.py` found a real gap in the first draft (relationships tagged, endpoint elements not tagged).
- `failure.domain.region`, `.zone`, `.host` and `.placement` worked as specified. `query.py` derived the shared domains from the ancestors without a change to the script.
- `review.safety.relevant` and `review.safety.justification` on the model gave the safety declaration one fixed place.
- The probe script `query.py` ran without a change on a second, unrelated workspace. This is evidence that the conventions are generic.
- `!docs` and `!adrs ... madr` inside the software system removed the `inspect` errors for missing documentation and decisions, as the probe predicted.
- The static export, the C4-PlantUML export and the SVG rendering need no network, and the result is self-contained.

## 4. What Did Not Work

### 4.1 With the source model

- The MTIP export drops the membership of actions in activity partitions (swimlanes). The observatory workflows ("Acquire Target with IRIS and NFIRAOS" and others) have their steps, but not the subsystem that does each step. Most relationships between observatory subsystems are therefore Inferred from step names, not Extracted.
- The observatory logical block has only two connectors (ESW to AO Sequencer). The observatory level of the SysML model holds the behaviour in workflows, not in a connected structure. A C4 container view needs structure.
- The model does not expand some acronyms (TTS, NSEN, ESEN, aORC). Their role is unknown. They stay as disconnected containers with the tag `Unresolved`, and `inspect` reports them.
- The model has no deployment. It has no software technology either: the technology fields hold generic kinds (Software, Hardware and software, Opto-mechanical assembly). The perspective PE has nothing to read.
- The model has no external systems and no observatory-level actors (the three actors are samples). VP01 has two APS stakeholders only.
- The model gives no order for the dynamic view. The order of the guide loop is Inferred.
- The requirements (DOORS imports, formalized timing requirements of the APS) are not mapped. C4 has no construct for them.

### 4.2 With the modelling requirements

- C4 is a software model. A telescope is mostly hardware: mirrors, lasers, opto-mechanical assemblies. Hardware became C4 containers with a technology such as "Hardware". This is a misuse of the container concept ("a separately runnable or deployable unit"). The catalogue has no rule for physical elements.
- A safety style (red element) works in the Structurizr renderer and in the static site, but not in the C4-PlantUML export and its SVGs. This confirms the probe result for perspectives and applies to tags too.
- Properties, `origin` and `provenance` are not in the SVGs and PNGs. They are only in the JSON export and in the tooltips of the static site.
- `inspect` treats a disconnected element as an error. For a model made from an incomplete source, a disconnected element is honest evidence of a gap, not a fault.
- VP03 Information has no carrier, as expected. The SysML item and interface definitions (for example `APS to M1CS Interface`, `APS Data`) would be the evidence source for VP03, but C4 cannot hold them.
- The `safety.function` value is a free name (`laser-propagation`), because the SysML model has no hazard analysis with safety function IDs.

## 5. Proposals

| No. | Proposal | Target |
|-----|----------|--------|
| 1 | Add a catalogue rule for physical elements in a cyber-physical system: either a tag `Physical` on containers, or a deployment node with an infrastructure node, and say which | TXT 30983f27, section 3.3 or 8 |
| 2 | Record in section 8.3 that `safety.function` must be set on the endpoint elements as well as on the relationships, because `query.py` checks both | TXT 30983f27, section 8.3 |
| 3 | Add the tag `Unresolved` to the vocabulary, for elements of the source that the model cannot explain, and accept the `inspect` finding "disconnected" for them | TXT 30983f27, section 8.3 |
| 4 | Record that an export from a SysML tool can lose partition membership, and that `origin` Inferred is then the expected result for behaviour-derived relationships | Model generation agent, issue 250 |
| 5 | Use the static site export as the review artefact, because it shows properties in tooltips and keeps the styles. Use the SVGs for documents | Checklist, evidence rules |
| 6 | Map the SysML interface blocks to VP03 evidence in documentation, not in the C4 model | TXT 30983f27, section 8.1 |

## 6. Related Documents

TXT 30983f27-f5aa-4d42-972e-5593f0c3ba09: Architecture Model: Viewpoints, Perspectives and Structurizr Mapping

TXT 23ded6d8-b184-4ef5-9fd9-9e484a1da7f9: Architecture Review Checklist: Viewpoints x Perspectives

TXT 4a09922d-bc32-4c03-86ba-d30ebc34e0b8: Structurizr and C4 for specmgr: Spike Findings and Design Suggestions

TXT cb1cc65a-ebd6-4f1d-882d-a8bc71483a6f: OpenSE Cookbook Application

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-23 17:15:00.000Z - Draft 0.2

New section Attribution: design owner, copyright holder of the SysML model, method, and the three publications with their full author lists. NOTICE and license text added to the model folder and the static site; header comment and model property `copyright` in the workspace; footer on each SVG. Issue 267.

### 2026-11-23 16:00:00.000Z - Draft 0.1

First draft. TMT C4 workspace from the MTIP export, 7 views with viewpoint properties, static site, C4-PlantUML sources and SVGs, metamodel SVGs. Issue 267.
