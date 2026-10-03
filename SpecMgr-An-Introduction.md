# SpecMgr — An introduction

## 1. Management Summary

SpecMgr is an open-source system that gives an organization a single, traceable record of *why* something is being built, *what* exactly is required, *what risks and decisions* were considered, *how it was built*, and *proof that it was verified* — all stored as permanent, version-controlled text files rather than scattered emails, chat logs, or slide decks. Work always starts from a high-level intent and is progressively broken down into smaller, well-defined items, so that at every step an AI agent is working from a clear, unambiguous understanding of the goal rather than guessing at it.

Its distinguishing feature is not that it uses an AI assistant to help write and implement specifications — many tools do that now. It is that the AI's work is run inside a **structured, role-separated process with mandatory checkpoints**, rather than being left to operate freely on the codebase. A written specification must exist and be approved before implementation starts; implementation is broken into discrete, independently-verified phases; a second, independent AI role reviews the finished work against the original specification before anyone signs off; and defined human decision points cannot be skipped. This is the key difference from simply asking a coding assistant to "build this feature" directly in the repository — commonly called "vibe coding" — covered in Section 7 below.

Critically for an organization handling confidential or regulated information, the entire system can run **fully on premises**, with no data ever required to leave the organisation's own infrastructure.

The project itself is open source under the AGPL-3.0 license.

---

## 2. Functionality: From Specification to Reviewed Implementation

SpecMgr supports one continuous pipeline from an initial specification to a reviewed, verified implementation. The stages below describe that pipeline as it is applied to any project managed through SpecMgr.

### Stage A — Capture and Specify

1. **Q&A (elicitation interview)** — stakeholder input is captured as structured question/answer pairs, organized by recognized software quality dimensions.
2. **Goals / Problem Statements** — raw input is distilled into a clear statement of what the organization wants to achieve and what specific problem is being solved.
3. **Requirements / Use Cases** — goals are translated into precise, testable statements of required behavior, each classified by quality characteristic.
4. **Risk / Decisions** — each requirement is checked against a formal risk assessment and, where a significant choice is made, a decision record capturing the options considered, the rationale, and a named accountable owner.

At this point, nothing has been built yet — only decided, on paper (in text, under version control).

### Stage B — Plan the Implementation

5. A feature is broken down into a **written plan**: numbered phases, each phase containing numbered tasks, each phase ending with an explicit, mandatory **quality gate** and defined **acceptance criteria**. Ambiguities are flagged for a human decision *before* any code is written — they are never left for the implementer to guess at.

### Stage C — Implement, Phase by Phase, Independently Verified

6. An **orchestrator** role reads the plan and hands off **one phase at a time** to a separate **implementer** role, with a fresh working context each time (no accumulated bias or shortcuts carried over from earlier phases).
7. The implementer writes the code *and* its tests, runs the mandatory quality gate itself, and must leave it green before stopping. It is not permitted to start the next phase, to commit, or to delegate further — strict scope discipline enforced by the tool's own permission settings, not just by instruction.
8. The orchestrator **does not trust the implementer's self-report**: it independently re-runs the same quality gate, inspects the actual file changes, and confirms the phase's acceptance criteria before accepting the phase. If anything fails, the work is sent back — not patched over.
9. Only after independent verification does a **human-confirmed commit** happen, one clean commit per phase, so the history itself stays auditable.

**The quality gate**, enforced at *every* phase boundary, not just at the end: automated formatting and lint checks, a dead-code check, the **full automated test suite**, and documentation/schema-drift checks — nothing proceeds while any of these is red.

### Stage D — Verify Against the Original Requirement

10. Every requirement/use case is linked to a **Verification Case Record**: specific, numbered acceptance criteria with a defined verification method, and an explicit coverage outcome (full/partial/none). A requirement cannot be silently declared "done" without a corresponding, documented check.

### Stage E — Independent Review

11. Once a feature is complete, a **separate, independent reviewer role** — never the same one that wrote the code — re-reads the original plan and the entire resulting change set, and produces a fixed-format report: Errors, Gaps, Inconsistencies, Code Smells, Improvements, Positives, each citing the exact file and line. This reviewer is read-only by tooling enforcement: a real user must acknowledge any fixes.
12. The feature is then pushed, a pull request is opened, and a **human makes the final merge decision** — the tooling never merges on its own.

### Stage F — Aggregate

13. Individual goals, requirements, risks, decisions, and verification records can be assembled into one consolidated **System Requirements Specification**, giving a single navigable document for the whole effort.

---

## 3. Standards Used

SpecMgr does not invent its own vocabulary where an established standard already exists. It builds on these and other standards:

| Standard / Framework | Used for |
|---|---|
| **ISO/IEC 25010:2023** | Software/systems quality characteristics — used to classify requirements and organize elicitation interviews |
| **ISO/IEC/IEEE 29148:2018** | Requirements engineering life-cycle processes — structure of the consolidated System Requirements Specification. *(ISO/IEC/IEEE 29148 can be applied to specify a system per ISO/IEC 15288, software per ISO/IEC 12207, or a combined system-and-software scope.)* |
| **TARA**-style risk response (Transfer / Accept / Reduce / Avoid), with a 5x5 probability-impact matrix | Formal risk assessment, before and after mitigation |
| **Model Context Protocol (MCP)** | The open, vendor-neutral standard used for AI-assistant integration — not a proprietary plugin interface |

---

## 4. On-Premise Operation and Confidentiality

This is a material point for an organisation handling confidential, personal, or otherwise sensitive information.

- **No mandatory cloud service.** SpecMgr is not a SaaS product. It runs as a normal local program (or background service) inside a coding agent on infrastructure the organisation controls — a staff member's machine, an internal server, or an internal network address. There is no external account, no subscription portal, and no requirement to send data to the vendor or anyone else.
- **Storage is plain files, under the organisation's own control.** Every specification, decision, and risk record is a text file in the organisation's own file system / internal git repository. There is no hidden database and no copy of the data held anywhere outside that storage.
- **Core functionality works fully offline.** Reading, writing, validating, and cross-referencing specifications requires no network access at all — confirmed by inspection of the source code; no telemetry, analytics, or "phone-home" behavior exists anywhere in it.
- **The AI assistant is a separate, swappable choice.** SpecMgr itself is only the specification-management backend. Which AI assistant is connected to it — including a fully private, internally hosted language model rather than a public cloud AI service — is an entirely independent decision for the organisation to make, based on its own confidentiality requirements. SpecMgr does not dictate or depend on any particular AI vendor. The specmgr is primarily tested with "OpenCode" - which is also open source.

**Net effect:** confidential specifications, risk assessments, and decision records never need to be transmitted to, or processed by, any external party as a condition of using this tool.

---

## 5. Diagram Generation and the Wider MCP Ecosystem

**a) Automatic UML diagram generation.** SpecMgr generates standard UML diagrams directly from structured specifications — use-case, activity, sequence, component, and class diagrams — deterministically, using the open-source **PlantUML** notation, with automated validation of the generated diagram syntax. Because each diagram is derived directly from the reviewed specification text, it stays consistent with it automatically, rather than being redrawn by hand and drifting out of sync over time.

**b) Composability with other specialized tools (the more important point).** SpecMgr is built on the **Model Context Protocol (MCP)** — an open, vendor-neutral standard for connecting an AI assistant to external tools. This means SpecMgr does not need to do everything itself: an organization can connect **several specialized MCP servers to the same AI assistant at once**. For example, alongside SpecMgr managing the specifications themselves, a separate diagramming/whiteboard tool exposed as its own MCP server could be connected in the same session to turn specification content into visual diagrams — without requiring any change to SpecMgr itself. A connected whiteboard-style MCP server can similarly be used for rapid UI prototyping straight from the specification, and the same composable pattern extends to other common design tools — e.g. Figma or Miro — each integrating as its own independent MCP server, with no change to SpecMgr itself. 

---

## 6. Additional Governance-Relevant Capabilities

- **Human-escalation by design, not by convention.** Throughout both the specification interviews and the implementation process, the AI is explicitly instructed to stop and ask a person whenever it is uncertain or faces an undocumented decision, rather than guessing and moving on — it is a recurring design pattern across the whole tool, not a one-off feature.
- **Automatic cross-reference checking.** Every artifact can reference others (e.g. a requirement pointing at the risk or decision behind it); a dedicated check resolves every such reference and flags any that point to something that doesn't actually exist on disk — catching broken traceability automatically rather than relying on someone noticing.
- **Duplicate-detection before creating new specs.** Before a new goal, decision, or requirement is created, the system can search existing specifications for semantically similar ones already on file — reducing the risk of duplicate or contradictory specifications accumulating over time.
- **Self-repair workflow for damaged documents.** If a specification file becomes malformed (e.g. through manual editing), there is a defined, guided repair procedure rather than the document silently becoming unreadable or being discarded.
- **Not locked to one AI vendor or one AI assistant product.** Because it speaks the open MCP standard, it is not tied to any single AI assistant brand — it would work the same way with any MCP-compatible assistant the organisation chooses now or switches to later.
- **Drift detection across related artifacts.** When one part of a specification — or of SpecMgr's own generated documentation — changes, automated checks detect when a related, dependent item was not updated to match, and either flag it or regenerate it. This catches the kind of silent inconsistency that unharnessed, ad hoc AI-assisted coding routinely misses.

---

## 7. Difference from "Vibe Coding" / Unharnessed AI Assistance

Unlike "vibe coding" — prompting an assistant to edit a codebase directly, with no required specification, no independent verification, and no fixed checkpoint before merging — SpecMgr requires a written, approved specification before implementation begins, breaks the work into independently-verified phases, and mandates a separate reviewer role plus a human merge decision before anything ships. The AI still writes the code either way; the difference is that SpecMgr runs it inside a defined, auditable process, so speed does not come at the cost of traceability or accountability.
