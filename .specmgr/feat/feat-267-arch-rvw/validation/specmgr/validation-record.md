# Phase 120 Validation Run 1: specmgr

Task 120.100, validation run 1. specmgr is none of the three architecture classes of QA 0.0340 (traditional enterprise application, distributed cloud-native platform, safety-relevant cyber-physical system). It is a fourth class, a single-user local tool, and an extra run: it was chosen because source, documents and deployment are fully available. Validation of the Architecture Model (TXT 30983f27, Draft 0.5) and the checklist matrix (TXT 23ded6d8, Draft 0.12) against specmgr itself. This is a validation of the catalogue, not a review of specmgr. Ratings appear only where they test a catalogue rule.

## 1. Scope

- System: specmgr, baseline branch feat-267-arch-rvw, 2026-11-22.
- Architecture class: a single-user local tool. One Python package with three extras, run as an MCP server process started by an agent harness, and as a CLI. State is markdown files in a git working tree.
- Review type used for the test: periodic health check (the product is released, v0.38.0).
- Safety gate: not safety relevant. Justification: a local document manager. It controls no equipment, and the integrity of the documents is protected by git review. See finding V-09.
- Evidence sources: AGENTS.md, pyproject.toml, src/, the CI workflows, docs/dec (48 DECs), docs/req (14 REQs).
- Model: `workspace.dsl` in this folder. Checked with the Structurizr MCP (version as in QA 0.0500): `validate` OK. `inspect` with workspace scope `softwaresystem` reports two errors, both expected: no documentation and no decisions (V-05).

## 2. Coverage of the C4 model (Architecture Model, section 8.1)

| Viewpoint | Claimed coverage | Found for specmgr | Remark |
|-----------|------------------|-------------------|--------|
| VP01 Context | partial to full | partial | Persons, the agent harness, git, PlantUML and the model download source are modelled. The MCP protocol contract (SDK 2.x error contract, DEC 80305c52) fits only into free text |
| VP02 Functional | partial | partial | Containers and seven components. The agent harness also writes the document store directly (feat plans, repair), so there are two writers of the store. The model shows this well |
| VP03 Information | none | none, confirmed | The core of specmgr is information architecture: 14 document schemas, ids, frontmatter, versioned models, language variants, the reference graph. The model holds one box "Document store". The evidence is the JSON schemas (`get_<d>_schema`) and the models, outside C4 |
| VP04 Concurrency | partial | none in practice | The real concerns are threads inside one process: the SDK thread pool for sync tools, per-domain locks, the warmup daemon thread, the GIL contention behind the feat-187 timeout. A container instance is one process. The lock had to go into relationship technology text. See V-02 |
| VP05 Development | partial | partial | Components are source packages (source-level mode, section 8.5). The extras `[cli]`, `[mcp]`, `[similarity]` of one wheel cannot be modelled (deployment-level mode: none, confirmed) |
| VP06 Deployment | full for structure | full, but trivial | One workstation, one host failure domain. The interesting deployment concern is distribution (PyPI, uvx, MCP registry, harness bundle), which is VP07 installation and upgrade |
| VP07 Operational | partial | none in practice | Installation, upgrade and release (scripts/release.sh, SOP 98537416) have no construct. No monitoring exists, and none is expected for a local tool |
| XV CrossView | none | none, confirmed | |

The CLI to MCP server relationship is a process start for `specmgr mcp`, but a Python import for `specmgr lint` and `specmgr diagram`. A C4 relationship between two containers shows a runtime call, so the import is misrepresented. This confirms section 8.5: the source-level mode cannot be read from the model.

## 3. Applicability matrix against specmgr

For each perspective: does specmgr have the concern, is the primary cell the right place, and do primary cells duplicate each other?

| Perspective | Result | Finding |
|-------------|--------|---------|
| FS | P cells VP01, VP02 fit (scope, tool surface) | none |
| PE | P cells VP04, VP06, VP07. The real issue (cold scan of the feat corpus, 348 s) is caused by parse cost and corpus size, which is VP03 and VP05 (both S). The S cross-checks catch it | none. S works as designed |
| CO | VP01 P (MCP protocol, harness versions) and VP03 P (schema evolution of stored documents, the breaking `prb` change) fit very well | none |
| IC | VP02 P. The main user of the tool surface is an LLM agent. Error texts, non-raising results and numbered raw reads (feat-27, feat-153, feat-189) are interaction design for an agent. It is unclear whether this is IC or CO (interoperability) | V-06 |
| RE | VP03 P (state recovery = git) fits. VP04 P (thread crash containment of the warmup) fits. VP06 P and VP07 P are close to empty for a local tool | V-03, V-07 |
| SE | The main control is the path-injection guard (`_path_safety.validate_id`) against an LLM caller that can call `delete`. By the interface rule it is internal handling, so VP02 x SE, which is S. The main control of the system sits in a secondary cell | V-04 |
| MA | VP02 P and VP05 P. In a source-level monolith the components are the source packages, so the criteria of the two cells would ask the same thing | V-01 |
| FL | VP06 P asks for scalability by instances. For specmgr scalability means corpus size (number of documents), which is VP03 (S) | V-08 |
| SA | Gate: not relevant. The gate text does not cover a tool that is used to develop safety-relevant systems | V-09 |
| RG | XV P, VP03 P. Licence (AGPL-3.0) and personal data in RASCI names are thin but real. The once-per-scope rule fits | none |
| LO | VP06 P. All local except GitHub and PyPI. Inapplicable once, with the justification. The rule works | none |
| RS | VP05 P, VP07 P, XV P. One maintainer: skills, bus factor and release capacity are the real risks. Fits | none |

## 4. Worked example VP06 x RE applied

Recorded in the model as one perspective per criterion on the node "Developer workstation" (QA 0.0680). The design worked: three perspectives on one node parsed without an error.

| Criterion | Applicability | Evidence | Outcome | Rating |
|-----------|---------------|----------|---------|--------|
| VP06-RE-090 Targets | Applicable | Missing: no availability or recovery target in docs/req or docs/gol (searched) | empty | Unassessable |
| VP06-RE-100 Single points of failure | Applicable | Insufficient for a health check: the model is Documented, the minimum is Demonstrated | empty | Unassessable |
| VP06-RE-110 Failure domains | Inapplicable: one host, no redundancy by design | not recorded | empty | Inapplicable |
| VP06-RE-130 Recovery of state and data | Applicable | Sufficient: git push and clone, run by every contributor (Measured, producer Pipeline, CI clones every commit) | Partially: no recovery target to compare with | Partially |
| VP06-RE-140 External dependencies | Applicable | Insufficient: degradation is documented (PlantUML all unset falls back to structure-only, similarity returns `available: false`), not demonstrated | empty | Unassessable |

Two of five end Unassessable although the reviewer knows the answer. See V-07.

## 5. Findings for the catalogue

| ID | Finding | Proposal | Affects |
|----|---------|----------|---------|
| V-01 | VP02 x MA and VP05 x MA duplicate each other for a system with one process, where components are source packages | Rule: in a source-level monolith, MA criteria go to VP05 and VP02 x MA keeps only runtime coupling. Or make VP02 x MA an S cell | Matrix, QA 0.0350, 0.0550 |
| V-02 | VP04 Concurrency coverage "partial" is too high for in-process concurrency. C4 has no thread construct | Section 8.1: "partial for process structure, none for threads and locks" | Architecture Model 8.1 |
| V-03 | For a single-user local tool, VP06 x RE and VP07 x RE are near empty. The tailoring rules handle it, but one justification per cell is needed seven times | A scope-level system class (for example local tool, enterprise application, distributed platform, cyber-physical system) as a precondition, with default tailoring per class, like the Safety gate | Checklist sections 3 and 5.2 |
| V-04 | The main security control (input validation against an untrusted caller) is in an S cell by the interface rule | VP02 x SE to P, or the interface rule names input validation at the system boundary as VP01 | Matrix, interface rule in checklist section 4 |
| V-05 | Structurizr expects decisions in `!adrs` format. The 48 DECs of specmgr are invisible to it, so the inspection reports "missing decisions" for a system that records decisions well | Section 11: either an export of DEC to the `!adrs` format, or the inspection is set to warning and the decision check runs over list_dec. The c4-from-specmgr skill needs one of the two | Checklist 11.5, 11.8 |
| V-06 | An LLM agent as the user of a tool surface has no clear home: IC or CO | Rule: a machine client that interprets text (an LLM agent) is a user for IC. A machine client with a fixed protocol is CO | Checklist section 5.1 |
| V-07 | A target criterion ("Where are the targets stated?") ends Unassessable when there is no target, although the search was complete. Absence and "cannot assess" are mixed | Rule: for a "where is X stated" criterion, a complete search of the baseline that finds nothing is Evidence Sufficient and Outcome Unsatisfactory | Checklist section 7.1 |
| V-08 | Scalability by data volume is a VP03 concern. VP03 x FL is S. R+W Table 4-1 rates Evolution High for the Information view | First evidence for the gap candidate of checklist section 5.3: VP03 x FL to P | Matrix, QA 0.0640 |
| V-09 | The Safety gate does not mention tools that are used to develop safety-relevant systems (tool qualification, for example IEC 61508-3 or ISO 26262-8 tool confidence) | Add one bullet to the gate: a development tool can be safety relevant through its output. Source to be confirmed | Checklist section 5.2 |
| V-10 | The perspective-per-criterion design (QA 0.0680) works. The description field carries the evidence level and the justification of Inapplicable | Keep | Architecture Model 8.2 |

Note on V-05, checked in the Structurizr source (`structurizr/structurizr`, `MadrDecisionImporter.java`, 2026-11-22). The `madr` importer reads only files whose name matches `\d{4}-.+?.md` and takes the decision ID from the four digits. specmgr DEC files are named `{uuid}-{slug}.md`, so not one is imported. Status comes from a frontmatter line `status: `, the date from a frontmatter line `date: yyyy-MM-dd` (else the file modification time), the title from the first `# ` line, and links between decisions only from markdown links to another `NNNN-*.md` file. `!adrs` needs a path on disk, so the Structurizr MCP (DSL text only) can never load decisions. Options: (a) generate a throw-away folder of `NNNN-{slug}.md` files from the DECs (frontmatter `status` and `date`, body unchanged, `DEC <uuid>` references rewritten as links) for the Structurizr CLI or container; (b) a custom Java importer on the Structurizr classpath, not usable with the MCP; (c) set the inspection off and check decisions with list_dec and list_references. Proposal: (c) for the agent, (a) later as a CLI export if a Structurizr site with decisions is wanted.

## 6. Open

- The three architecture classes of QA 0.0340: no system chosen yet.
- None of the proposals is applied to the matrix or the texts. They wait for the other two validations, so that a cell is not changed on one data point.
