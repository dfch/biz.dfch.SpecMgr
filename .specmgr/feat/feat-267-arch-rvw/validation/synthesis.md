# Phase 120 Validation: Synthesis of Runs 1 to 4

Task 120.100. Summary of four validation runs of the Architecture Model (TXT 30983f27, Draft 0.5) and the checklist matrix (TXT 23ded6d8, Draft 0.12). The detail and the provenance of every finding are in the run records. Nothing below is applied to the texts yet. Section 3 lists the proposed changes for decision.

## 1. Runs

| Run | System | Class | Record | Findings |
|-----|--------|-------|--------|----------|
| 1 | specmgr | Single-user local tool (extra class) | `specmgr/validation-record.md` | V-01 to V-10 |
| 2 | AERIS-10 phased-array radar | Safety-relevant cyber-physical system | `aeris10/validation-record.md` | A-01 to A-12 |
| 3 | Apache OFBiz | Traditional enterprise application | `ofbiz/validation-record.md` | O-01 to O-14 |
| 4 | OpenTelemetry Demo | Distributed cloud-native platform | `otel-demo/validation-record.md` | C-01 to C-13 |

Every model passes Structurizr `validate`. `inspect` reports "missing documentation" and "missing decisions" for all four.

Answer to QA 0.0340: the matrix structure holds. Every concern of the four systems found a viewpoint and a perspective. The weak points are not the axes. They are a few cell values, missing preconditions, missing criteria in the home cells, and rules for ratings and evidence.

## 2. Cross-run results

Support counts how many runs back a result. "Contradicted" means that a run showed the opposite.

| # | Result | Support | Findings |
|---|--------|---------|----------|
| R1 | A target criterion ("Where is X stated?") ends Unassessable after a complete search that found nothing. Absence and "cannot assess" are mixed | 4 of 4 | V-07, A-08, O-12, C-05 |
| R2 | A criterion that depends on another one (VP06-RE-100 on the target of RE-090) has no rule. RE-100 should be split into a structural half and a target half | 2 | O-12, C-02 |
| R3 | The scope needs a system class (and with it default tailoring), a subject (product or installation) and an intended operating profile | 4 of 4 | V-03, A-12, O-08, C-01 |
| R4 | The main controls of a quality land in S cells: security input handling in VP02 x SE, the safety design in VP02, VP04 and VP06 x SA | 3 of 4 (not run 4, where the main gap sat in VP01) | V-04, O-05, A-10, C-11 |
| R5 | C4 coverage of VP04 Concurrency: none for threads, clock domains, interrupts and pools inside a process; partial for flows between processes (dynamic view) | 4 of 4 | V-02, A-09, O-14, C-06 |
| R6 | "Missing decisions" from `inspect` cannot tell a system with decisions outside the ADR format (run 1) from a system without decisions (runs 2 to 4) | 4 of 4 | V-05, A (section 1), O-13, C-12 |
| R7 | VP03 x MA should be P: the shared data model is the strongest coupling of an enterprise application. The book rates Evolution High for the Information view | 2 (runs 1 and 3) | V-08, O-03 |
| R8 | VP03 x FL stays S: scalability by data volume (run 1) is class-dependent; by instances (runs 3 and 4) it belongs in VP06 x FL | contradicted for the move | V-08 vs O-04, C-08 |
| R9 | VP02 x MA and VP05 x MA do not duplicate in general. They duplicate only where the runtime calls are the source calls | V-01 contradicted by run 3 | V-01, O-02 |
| R10 | VP06-RE-110 is Inapplicable only for a single failure domain by design. Missing redundancy on a multi-node platform is Unsatisfactory. Run 1 used the weaker reasoning | 1, corrects run 1 | C-03 |
| R11 | The Safety gate names no hazard types and no protected party, and does not cover development tools whose output is safety relevant | 2 | V-09, A-01 |
| R12 | The home cells XV x SA and XV x RG have no criteria, so the absence of a hazard analysis or of a regulation register cannot be recorded | 2 | A-02, A-11, O-11 |
| R13 | The evidence record lacks the object under test, the baseline of evidence from a second repository, a rule for conflicting evidence, and variants in the baseline | 1 each | A-05, A-06, A-07, C-10 |
| R14 | One `trust.boundary` value per element cannot show privilege tiers inside a process; a safety function across elements has no property key; placement by a scheduler defeats `failure.domain.host` | 3 | O-06, C-11, A-04, C-03 |
| R15 | Several perspectives for one criterion in one model: the rating and the evidence must be told apart | 1 | C-13 |
| R16 | New concepts without a home: tenant isolation, an in-process extension interface, a runtime-loaded module as a decoupling mode, several deployment descriptors as several environments, telemetry relationships that swamp a view | 1 each | O-07, O-10, O-09, C-04, C-09 |

## 3. Proposed changes, for decision

Grouped by target. The numbers in brackets are the results of section 2.

Matrix (checklist 5.2, QA 0.0550 and 0.0640):

1. VP02 x SE from S to P [R4].
2. VP03 x MA from S to P [R7].
3. VP03 x FL stays S [R8]. VP02 x MA stays P, with the rule of R9 for the split with VP05.
4. With SA included: VP02 x SA and VP06 x SA from S to P [R4, A-10].

Checklist rules:

5. Section 3: new preconditions system class, subject (product or installation) and intended operating profile, with default tailoring per class [R3].
6. Section 5.2 Safety gate: hazard types, protected party, development tools [R11].
7. Section 7.1: a complete search that finds nothing is Evidence Sufficient and Outcome Unsatisfactory; a dependent criterion names its dependency [R1, R2].
8. Section 8.2: the evidence record names the object of the evidence and the baseline of every repository it comes from; conflicting evidence is a finding [R13].
9. Section 10: split VP06-RE-100; restate the Inapplicable condition of RE-110; reword RE-120 to cover a safe stop [R2, R10, A-08].
10. New criteria for the home cells XV x SA (from XV-SA-090) and XV x RG [R12].
11. Section 11.8: the decision inspection off; decisions checked with list_dec and list_references [R6].

Architecture Model:

12. Section 8.1: VP04 "partial for flows between processes, none inside a process"; VP03 names the data model as the evidence source; VP07 telemetry as a relationship tag [R5, O-01, C-09].
13. Section 8.2: rating perspective on the top node, node-level perspectives as evidence [R15].
14. Section 8.3: conventions for privilege tiers, a safety function key and scheduler placement [R14].
15. Section 8.5: the mode "runtime-loaded module" [O-09].

Not decided here: tenant isolation and extension interfaces as catalogue concerns [R16].

## 4. Open

- Several facts per run are marked "not verified" in the records. None of them changes a cross-run result.
- The capability profile (checklist 7.3) was not filled in any run. Its practice areas are still a proposal (QA 0.0230).
