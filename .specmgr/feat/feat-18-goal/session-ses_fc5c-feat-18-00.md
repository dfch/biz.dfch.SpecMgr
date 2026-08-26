# Plan Goal Artifact Type Feature

**Session ID:** ses_fc5c43a45ffeBvefUFAadyQ5ZA
**Created:** 8/25/2026, 8:43:10 PM
**Updated:** 8/25/2026, 9:18:46 PM

---

## User

I want to create a new feature: Create Artifact type "Goal" (GOL)

There is an ADR that tells you how to create a feature. And there is a template in the ".specmgr" folder.
I want the same structure as the feature "feat-16-problem-statement".

A "goal" is like a high level business requirement. So it is similar to the structure of a requirement. But it would not have ISO25010 characteristics. 

Let us plan this feature.

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 10.9s)

_Thinking:_

Let me investigate the repository structure to understand the following:
1. The ADR regarding feature creation
2. The template in the `.specmgr` folder
3. The structure of the "feat-16-problem-statement" feature
4. The structure of the req domain (since goals are similar to requirements but don't have ISO25010 characteristics)

First, I'll start by checking the feature folders, the template, and the relevant ADRs.




I'll explore the repository to understand the feature creation process, the template, and the feat-16 structure before planning.




**Tool: bash**

**Input:**
```json
{
  "command": "ls -la .specmgr/feat/ && ls -la .specmgr/_template/v1/ && ls .specmgr/feat/feat-16-problem-statement/"
}
```

**Output:**
```
total 52
drwxrwxr-x 13 user user 4096 Aug 25 20:34 .
drwxrwxr-x  4 user user 4096 Aug 25 20:34 ..
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-10-add-artifact-type-tasklist
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-12-qa-artifact
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-13-list-paging
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-14-qa-v2-adjacent-qa
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-16-problem-statement
drwxrwxr-x  6 user user 4096 Aug 25 20:34 feat-4-use-cases
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-5-md-model-parser
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-6-requirement-artifact
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-7-various-improvements
drwxrwxr-x  2 user user 4096 Aug 25 20:34 feat-8-coverage-badge
drwxrwxr-x  3 user user 4096 Aug 25 20:34 feat-9-doc-in-specmgr
total 12
drwxrwxr-x 2 user user 4096 Aug 25 20:34 .
drwxrwxr-x 3 user user 4096 Aug 25 20:34 ..
-rw-rw-r-- 1 user user 2817 Aug 25 20:34 README.md
prb-2f967bd2-7c55-4adf-a17b-8589b62dd3a9-victron-energy-multiplus-ii-48-5000-70-does-not-charge-with.md
prb_reference.md
README.md
session-ses_fc80-test-prb.md
session-ses_fc85-feat-16-01.md
session-ses_fc87-feat-16-00.md

```

**Tool: specmgr_list_adr**

**Input:**
```json
{
  "max_results": 100
}
```

**Output:**
```
{
  "total": 24,
  "offset": 0,
  "max_results": 100,
  "truncated": false,
  "results": [
    {
      "id": "23a14195-339c-48af-99d2-97c9964041ae",
      "title": "Use ISO 8601 for all dates and times",
      "status": "accepted",
      "ref": "23a14195-339c-48af-99d2-97c9964041ae-use-iso-8601-for-all-dates-and-times"
    },
    {
      "id": "3159caf2-4beb-43f2-9f5d-8f46be0211af",
      "title": "Adopt icontract as the Design by Contract library for SpecMgr",
      "status": "accepted",
      "ref": "3159caf2-4beb-43f2-9f5d-8f46be0211af-adopt-icontract-as-the-design-by-contract-library-for-specmg"
    },
    {
      "id": "33c5ab08-ff58-4c73-8c32-23abaf3838e3",
      "title": "Filesystem is the sole source of truth: no in-memory id-to-document cache",
      "status": "accepted",
      "ref": "33c5ab08-ff58-4c73-8c32-23abaf3838e3-filesystem-is-the-sole-source-of-truth-no-in-memory-id-to-do"
    },
    {
      "id": "3bf0326f-065a-424c-a2b9-87e5d5bcfa99",
      "title": "Extract MCP Singleton into Its Own Module to Break Domain/Server Cyclic Imports",
      "status": "accepted",
      "ref": "3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se"
    },
    {
      "id": "4c6119c9-532f-4629-8977-108e78304f48",
      "title": "Parse-validate-render pipeline: library choices, no AST-preserving round-trip",
      "status": "accepted",
      "ref": "4c6119c9-532f-4629-8977-108e78304f48-parse-validate-render-pipeline-library-choices-no-ast-preser"
    },
    {
      "id": "71fd95d7-07f2-466f-81aa-d29b7e3ef34c",
      "title": "Generic update_section(key, value) with deletion sentinel and mandatory-section rejection",
      "status": "accepted",
      "ref": "71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and"
    },
    {
      "id": "737858a9-7796-4f01-ae35-5afc1c707818",
      "title": "Use pre-commit hooks for local quality gates",
      "status": "accepted",
      "ref": "737858a9-7796-4f01-ae35-5afc1c707818-use-pre-commit-hooks-for-local-quality-gates"
    },
    {
      "id": "7531106b-074b-4bd8-a83a-e433d01676e2",
      "title": "Expose listing and by-id reads as MCP resources in addition to tools",
      "status": "accepted",
      "ref": "7531106b-074b-4bd8-a83a-e433d01676e2-expose-listing-and-by-id-reads-as-mcp-resources-in-addition"
    },
    {
      "id": "832cd6c1-ef8a-4bfc-990e-a610823f61ae",
      "title": "Generic heading-mapped markdown-to-Pydantic parsing with declarative Heading metadata and opt-in constraints",
      "status": "accepted",
      "ref": "832cd6c1-ef8a-4bfc-990e-a610823f61ae-generic-heading-mapped-markdown-to-pydantic-parsing-with-dec"
    },
    {
      "id": "898bfcd0-85f9-462f-93a8-747bda4166c8",
      "title": "Author and edit ADRs only through MCP structured tools, never raw markdown",
      "status": "accepted",
      "ref": "898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never"
    },
    {
      "id": "8cf940c5-3100-485c-a12d-14b59b631712",
      "title": "id/filename/addressing scheme: server-generated UUID, {id}-{slug}.md, directory-scan resolution",
      "status": "accepted",
      "ref": "8cf940c5-3100-485c-a12d-14b59b631712-id-filename-addressing-scheme-server-generated-uuid-id-slug"
    },
    {
      "id": "9c687bb1-8ee7-41c8-84ec-07606356bc73",
      "title": "Enforce doc generation, lint, and tests locally via pre-commit hook, not just CI",
      "status": "accepted",
      "ref": "9c687bb1-8ee7-41c8-84ec-07606356bc73-enforce-doc-generation-lint-and-tests-locally-via-pre-commit"
    },
    {
      "id": "9d3800cf-b3b4-4d46-8b68-3573d932b1c8",
      "title": "Detect unreferenced Python Code",
      "status": "accepted",
      "ref": "9d3800cf-b3b4-4d46-8b68-3573d932b1c8-detect-unreferenced-code-with-vulture-not-snakefood-enforced"
    },
    {
      "id": "bbf412a7-965e-4435-8669-c338407d73b7",
      "title": "Frontmatter extension fields (id, version) with whole-object full-replace update contract",
      "status": "accepted",
      "ref": "bbf412a7-965e-4435-8669-c338407d73b7-frontmatter-extension-fields-id-version-with-whole-object-fu"
    },
    {
      "id": "bc5e18ad-6bbf-4265-bae4-3e34984a2d29",
      "title": "Generic base frontmatter model for markdown document types (models/md/frontmatter.py)",
      "status": "accepted",
      "ref": "bc5e18ad-6bbf-4265-bae4-3e34984a2d29-generic-base-frontmatter-model-for-markdown-document-types-m"
    },
    {
      "id": "c73e4f9d-81f3-495d-bd3a-f660ab992ed3",
      "title": "Base the ADR template on MADR 4.0.0",
      "status": "accepted",
      "ref": "c73e4f9d-81f3-495d-bd3a-f660ab992ed3-base-the-adr-template-on-madr-4-0-0"
    },
    {
      "id": "cb5a2d5f-7020-4c6e-b28d-a38d17b23243",
      "title": "Use Conventional Commits for commit messages",
      "status": "accepted",
      "ref": "cb5a2d5f-7020-4c6e-b28d-a38d17b23243-use-conventional-commits-for-commit-messages"
    },
    {
      "id": "d54abe50-a2c5-44f8-8bfe-11ea634b6f87",
      "title": "\"Pros and Cons of the Options\" as a derived container with a dedicated Option sub-API",
      "status": "accepted",
      "ref": "d54abe50-a2c5-44f8-8bfe-11ea634b6f87-pros-and-cons-of-the-options-as-a-derived-container-with-a-d"
    },
    {
      "id": "ddd038f0-ae16-4f4b-beef-df06f7ed226f",
      "title": "Prompt surface: narrated guidance plus step-gated test variants",
      "status": "accepted",
      "ref": "ddd038f0-ae16-4f4b-beef-df06f7ed226f-prompt-surface-narrated-guidance-plus-step-gated-test-varian"
    },
    {
      "id": "ddfb1109-422d-4507-8dbc-dc5e4bec9614",
      "title": "Expose id-based REQ document reads as a tool (get_req), not a resource",
      "status": "accepted",
      "ref": "ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r"
    },
    {
      "id": "e11421d3-cc1d-487b-af32-ee4093422712",
      "title": "Use Architecture Decision Records (ADRs) to document design decisions",
      "status": "accepted",
      "ref": "e11421d3-cc1d-487b-af32-ee4093422712-use-architecture-decision-records-adrs-to-document-design-de"
    },
    {
      "id": "e369ee2e-3353-4f92-991c-6367d76d832e",
      "title": "Organize development artifacts in `.specmgr` with feature-driven work units",
      "status": "accepted",
      "ref": "e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature"
    },
    {
      "id": "ec9f5262-9912-49d0-903f-fcfb54f28c13",
      "title": "Expose <domain>_list as paged MCP tools (list_<domain>), not resources",
      "status": "accepted",
      "ref": "ec9f5262-9912-49d0-903f-fcfb54f28c13-expose-domain-list-as-paged-mcp-tools-list-domain-not-resour"
    },
    {
      "id": "ece4554b-725c-4f76-bc04-5d2b760363d2",
      "title": "Organize the codebase by document-type domain: domain-first hierarchy for tools/prompts/resources, shared versioned models",
      "status": "accepted",
      "ref": "ece4554b-725c-4f76-bc04-5d2b760363d2-organize-the-codebase-by-document-type-domain-domain-first-h"
    }
  ]
}
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 11.1s)

_Thinking:_

Alright, let's read the main ADR: "Organize development artifacts within `.specmgr` in feature-driven work units" (e369ee2e-3353-4f92-991c-6367d76d832e). This is the ADR that explains how to create features. Also, I'll read the template and the README of feat-16.




Now let me read the feature-creation ADR, the template, and the feat-16 structure.




**Tool: specmgr_get_adr**

**Input:**
```json
{
  "id": "e369ee2e-3353-4f92-991c-6367d76d832e"
}
```

**Output:**
```
{
  "frontmatter": {
    "id": "e369ee2e-3353-4f92-991c-6367d76d832e",
    "version": "1.0.0",
    "status": "accepted",
    "date": "2026-08-05",
    "decision_makers": "dfch",
    "consulted": null,
    "informed": null
  },
  "body": {
    "title": "Organize development artifacts in `.specmgr` with feature-driven work units",
    "context_and_problem_statement": "The project maintains two documentation folders with an unclear split: `docs/` — published, generated documentation (API docs, ADRs, specifications), which reflects the current state of the project — and `doc/` — development progress notes, planning artifacts, research, which has no clear ongoing purpose once this ADR's structure exists. As part of adopting this ADR's outcome, `doc/` is dissolved: its content is migrated (manually, see Consequences) into the new structure below, and the `doc/` folder is retired. Development artifacts (plans, progress tracking, work-unit status) need a structured, agent-friendly location that is: (1) separate from published documentation (`docs/`); (2) organized by feature/work-unit for easy agent reference; (3) generic enough to serve as a template for future projects using specmgr as a toolkit.",
    "decision_drivers": "- Agent-friendly reference paths: agents should reference specific feature paths inline (e.g., \"See `.specmgr/feat/feat-001-adr-toc/README.md`\"), keeping agent instructions lean and focused\n- Toolkit reusability: structure should be generic enough for future projects adopting specmgr as a toolkit — the folder name itself (`.specmgr/`) is chosen for this reason, following the convention of tool-named dotfolders like `.github/`, `.vscode/`, `.docker/`\n- Clear separation of concerns: development artifacts must be distinct from published documentation\n- Version control and auditability: development progress should be tracked in git with full history",
    "considered_options": "- Single README.md per feature containing both plan and progress\n- Separate README.md (plan) and progress.md (status) per feature",
    "decision_outcome": "**Chosen option: \"Option 1: .specmgr structure\"** — a single `README.md` per feature combining plan and progress, with an optional sibling `history.md` for rotating out older `Recent Updates` entries. Every feature `README.md` also carries a minimal YAML frontmatter block (`id`, `version`, `status`, `created`, `updated` — see that option's \"Frontmatter\" note for details). There is no separate `GitHub Issue` field or body line: the issue number is the `NNN` infix already embedded in `id` (the folder name, `feat-NNN-slug`) itself.\n\nThis is preferred over Option 2 (separate `README.md`/`progress.md`) for its simplicity: one file per feature, no cross-file cross-referencing needed to see the full feature story, and the single canonical Task List (status inline per task) removes the Implementation Plan/Execution Plan duplication that Option 2 still carries. See \"Pros and Cons of the Options\" below for the full tradeoff analysis, and that option's \"Open Questions\" for points intentionally left open for later decisions.",
    "consequences": "**Positive:**\n- Agents can reference specific feature paths inline, keeping instructions lean and focused\n- Clear separation: agents only read what's relevant to their task\n- Structure is reusable for future projects adopting specmgr as a toolkit\n- Development progress is version-controlled and auditable\n- The `.specmgr/` folder (and its `feat/` work units) is committed to git like any other tracked path in the repo — no `.gitignore` exclusion — so history and review apply to it the same way they do to `docs/` and source code\n\n**Negative:**\n- Adds another top-level folder to the repo structure\n- Requires discipline to keep progress sections updated (hand-maintained, not auto-generated)\n- Migrating `doc/`'s existing content (e.g. `doc/adr-tool-plan.md`, `doc/refactor-domain.md`) into the new structure is done manually, one file at a time, once this ADR is adopted — no automated migration tooling is planned\n\n**Numbering convention:**\n- `feat-NNN-slug` — `NNN` is the GitHub issue number for feature work tied to an issue. There is no separate `github_issue` frontmatter field or body line: `id` (the folder name itself) is the single source of truth for the issue number, read by parsing its `NNN` infix.\n- Work started without a GitHub issue yet uses `feat-0-slug` (issue number `0`) until/unless an issue is later opened for it\n\n**ADR vs. feature-level \"Decisions Made\" log:**\nA decision belongs in a full ADR (under `docs/adr/`) if it: (a) is architecture/structure-level and affects more than one feature or the repo as a whole, (b) would be relevant to someone joining the project later trying to understand why something is the way it is, or (c) reverses/supersedes a previous ADR. A decision belongs in the feature's own \"Decisions Made\" log instead if it: (a) is scoped entirely to that one feature's implementation details, (b) wouldn't need to be found by searching ADRs later, and (c) doesn't constrain future features. Tie-breaker: if in doubt, write the ADR — it is cheap to write and already indexed by `adr-toc`, so overuse is low-cost, while under-use risks losing a decision in a feature folder no one will grep later.",
    "confirmation": "For now, confirmation that new `feat-NNN-slug/README.md` files follow the chosen structure/template is done manually via PR review. Automated enforcement (e.g. a `specmgr feat-*` validation tool mirroring `validate_adr`) is deferred to future work, consistent with the other deferred-tooling items noted in the chosen option's Open Questions.",
    "options": [
      {
        "number": 1,
        "partial_title": ".specmgr structure",
        "content": "```\n.specmgr/\n├── feat/                          # Feature work units\n│   └── feat-NNN-slug/             # One folder per GitHub issue\n│       ├── README.md              # Feature plan + progress (mandatory)\n│       └── history.md             # Archived older \"Recent Updates\" entries (optional)\n└── (other dirs as needed)\n```\n\n**File purposes:**\n- `README.md` — Single file containing both the feature plan (requirements, acceptance criteria, task list, scope, dependencies, design notes) and progress tracking (current state, blockers, decisions made during implementation, links to related ADRs or PRs)\n- `history.md` — Optional sibling file. Holds older `Recent Updates` entries once `README.md` grows too long; `README.md` keeps only recent entries and links back to this file for anything older.\n\n**Frontmatter:** Every feature `README.md` carries a YAML frontmatter block, mandatory fields `id` (the `feat-NNN-slug` folder name itself, not a generated UUID — unlike ADR frontmatter's server-generated `id`), `version` (semver, starts at `1.0.0`), `status` (`planning` | `in-progress` | `review` | `done`), and `created`/`updated` (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no separate `GitHub Issue` field, in frontmatter or body: the issue number is the `NNN` infix already embedded in `id` (i.e. the folder name, `feat-NNN-slug`) — `0` means no issue yet — so it is derived by reading `id`, never duplicated as its own field.\n\n**Template: README.md**\n\n```markdown\n---\nid: feat-NNN-slug\nversion: 1.0.0\nstatus: planning\ncreated: YYYY-MM-DD\nupdated: YYYY-MM-DD\n---\n\n# Feature: [Feature Title]\n\n## Plan\n\n### Overview\n\nBrief description of what this feature does and why it matters.\n\n### Requirements\n\n- REQ-001: [Functional requirement]\n- REQ-002: [Non-functional requirement]\n- REQ-003: [Constraint or dependency]\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — [testable condition]\n- [ ] ACC-002: Verifies REQ-002 — [testable condition]\n- [ ] ACC-003: Verifies REQ-003 — [testable condition]\n\n### Scope\n\nWhat is included in this feature:\n- Item 1\n- Item 2\n\nWhat is explicitly out of scope:\n- Item A\n- Item B\n\n### Dependencies\n\n- Depends on: [other feat-NNN-slug, ADR id, or external]\n- Blocks: [other feat-NNN-slug]\n\n### Design Notes\n\nAny architectural decisions, patterns, or design rationale relevant to this feature.\n\n### Related ADRs\n\n- [ADR id]: [Title]\n- [ADR id]: [Title]\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself — there is no separate \"planned\" vs. \"executed\" list to keep in\nsync; a task's line *is* its current status. Update it in place as work\nprogresses (edit, don't duplicate).\n\n#### Phase 1: [Phase name]\n- [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)\n- [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10\n- [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)\n\n#### Phase 2: [Phase name]\n- [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started\n- [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in place;\nrely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of [YYYY-MM-DD]**: [Brief status summary]\n\n### Blockers\n\n- [ ] Blocker 1 — [description, impact, mitigation]\n- [ ] Blocker 2 — [description, impact, mitigation]\n\n(Remove this section if no blockers.)\n\n### Recent Updates\n\nIf this section grows too long, move older entries to `history.md` in this\nsame folder and leave a pointer here, e.g.:\n`See history.md for updates before YYYY-MM-DD.`\n\n#### Update [YYYY-MM-DDTHH:mm:ssz] (newest)\n- Completed: [what was done]\n- Next: [what comes next]\n- Notes: [any relevant context]\n\n#### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)\n- Completed: [what was done]\n- Next: [what comes next]\n- Notes: [any relevant context]\n\n### Decisions Made\n\n- **[YYYY-MM-DD]**: [Decision] — [Rationale]\n- **[YYYY-MM-DD]**: [Decision] — [Rationale]\n\n### Related PRs / Commits\n\n- [PR #NNN](link): [description]\n- [Commit hash](link): [description]\n```\n\n**Pros:**\n- Single file to maintain\n- Simpler structure: one file per feature\n- Plan and progress are always together in one document\n- Easier to see the full feature story (what was planned vs. what happened) in one place\n- Requirements and acceptance criteria are co-located with clear traceability\n- Single Task List: no separate Implementation/Execution Plan pair to keep in sync — status is a property of each task line, not a duplicated list, so there is nothing to drift\n- Auditability of \"what was planned vs. what actually happened\" comes from git history on this one file, not from a hand-maintained duplicate\n- `Recent Updates` growth is bounded by rotating older entries into an optional `history.md`, keeping `README.md` itself lean\n- Frontmatter `id`/`version`/`status`/`created`/`updated` gives each feature folder a compact, machine-readable header, mirroring the ADR frontmatter's `status` field for consistency across both document types\n- No `GitHub Issue` duplication: the issue number is already encoded in `id`'s `NNN` infix, so there is nothing to keep in sync between a frontmatter/body field and the folder name itself\n\n**Cons:**\n- File grows over time as progress updates (Recent Updates, Decisions Made) accumulate, even with rotation available\n- Plan and progress are intermingled, making it harder to extract just the plan for reference\n- No clear separation between \"contract\" (what we committed to) and \"journal\" (what actually happened) — relies on git history to reconstruct the original plan instead of a preserved, separate copy\n- Still hand-maintained/free-text: nothing currently enforces that a task's status field, or the frontmatter `status`/`updated` fields, are kept in sync with reality, or that `history.md` rotation actually happens\n- Deriving the GitHub issue number from `id`'s `NNN` infix requires parsing the folder name rather than reading a dedicated field — acceptable since `feat-NNN-slug` is already a fixed, documented convention\n\n**Open Questions:**\n- Archival/lifecycle rule for the file once `status: done` (stay in place / archive / prune) — intentionally left undecided here; treated as a separate future project decision, not a gap in this ADR.\n- Rotation strategy for `Recent Updates`: rotating older entries into `history.md` is documented here as an available option; the exact trigger (manual vs. a fixed entry-count rule) and mechanics are left to the user/agent maintaining the feature folder to decide at the time, not prescribed by this ADR.\n- Template location: **resolved** — the template now exists at `.specmgr/_template/v1/README.md`, matching the versioned path scheme originally proposed here.\n- Whether to add further frontmatter fields later (e.g. `decision_makers`, `related_adrs`, `tags`) is left open; the current five-field frontmatter (`id`, `version`, `status`, `created`, `updated`) is a deliberate, minimal starting point, not a ceiling.\n- Recommendation (not yet built, non-blocking): a dedicated MCP tool (analogous to this project's `update_section`/`option_update` for ADRs) that flips one task's status field, or the frontmatter `status`, atomically, instead of relying on an agent/human to locate and hand-edit the right line."
      },
      {
        "number": 2,
        "partial_title": ".specmgr structure with separate README.md (plan) and progress.md (status)",
        "content": "```\n.specmgr/\n├── feat/                          # Feature work units\n│   └── feat-NNN-slug/             # One folder per GitHub issue\n│       ├── README.md              # Feature plan (mandatory)\n│       └── progress.md            # Status tracking (mandatory)\n└── (other dirs as needed)\n```\n\n**File purposes:**\n- `README.md` — Contains the complete feature plan: requirements, acceptance criteria, implementation plan, scope, dependencies, design notes, any pre-implementation research. Treated as immutable once work begins (except Implementation Plan, which may be refined during execution).\n- `progress.md` — Hand-maintained status log: execution plan (tracking actual progress), current state, blockers, decisions made during implementation, links to related ADRs or PRs. Updated throughout the feature lifecycle.\n\n**Template: README.md**\n\n```markdown\n# Feature: [Feature Title]\n\n**GitHub Issue**: #NNN  \n**Status**: [Planning | In Progress | Review | Done]\n\n## Overview\n\nBrief description of what this feature does and why it matters.\n\n## Requirements\n\n- REQ-001: [Functional requirement]\n- REQ-002: [Non-functional requirement]\n- REQ-003: [Constraint or dependency]\n\n## Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — [testable condition]\n- [ ] ACC-002: Verifies REQ-002 — [testable condition]\n- [ ] ACC-003: Verifies REQ-003 — [testable condition]\n\n## Scope\n\nWhat is included in this feature:\n- Item 1\n- Item 2\n\nWhat is explicitly out of scope:\n- Item A\n- Item B\n\n## Dependencies\n\n- Depends on: [other feat-NNN-slug, ADR id, or external]\n- Blocks: [other feat-NNN-slug]\n\n## Design Notes\n\nAny architectural decisions, patterns, or design rationale relevant to this feature.\n\n## Related ADRs\n\n- [ADR id]: [Title]\n- [ADR id]: [Title]\n\n## Implementation Plan\n\nHigh-level breakdown of work phases and tasks:\n\n### Phase 1: [Phase name]\n- Task 1.1: [description] — Depends on: [none/other tasks]\n- Task 1.2: [description] — Depends on: Task 1.1\n\n### Phase 2: [Phase name]\n- Task 2.1: [description] — Depends on: Task 1.2\n- Task 2.2: [description] — Depends on: Task 2.1\n```\n\n**Template: progress.md**\n\n```markdown\n# Progress: [Feature Title]\n\n## Current Status\n\n**As of [YYYY-MM-DD]**: [Brief status summary]\n\n## Execution Plan\n\nTracks actual progress against the Implementation Plan in README.md. Update task status here as work progresses.\n\n### Phase 1: [Phase name]\n- [x] Task 1.1: [description] — Completed [YYYY-MM-DD]\n- [ ] Task 1.2: [description] — In progress, ETA [YYYY-MM-DD]\n\n### Phase 2: [Phase name]\n- [ ] Task 2.1: [description] — Blocked by: [blocker]\n- [ ] Task 2.2: [description] — Not started\n\n### Blockers\n\n- [ ] Blocker 1 — [description, impact, mitigation]\n- [ ] Blocker 2 — [description, impact, mitigation]\n\n(Remove this section if no blockers.)\n\n## Recent Updates\n\n### [YYYY-MM-DD]\n- Completed: [what was done]\n- Next: [what comes next]\n- Notes: [any relevant context]\n\n### [YYYY-MM-DD]\n- Completed: [what was done]\n- Next: [what comes next]\n- Notes: [any relevant context]\n\n## Decisions Made\n\n- **[YYYY-MM-DD]**: [Decision] — [Rationale]\n- **[YYYY-MM-DD]**: [Decision] — [Rationale]\n\n## Related PRs / Commits\n\n- [PR #NNN](link): [description]\n- [Commit hash](link): [description]\n```\n\n**Pros:**\n- Clear separation of concerns: README.md is the immutable \"contract\" (what we committed to), progress.md is the mutable \"journal\" (what actually happened)\n- Auditability: you can see what was promised vs. what was delivered by comparing the two files\n- Plan stays clean and focused: not cluttered with progress updates\n- Easier to reference just the plan without scrolling through progress history\n- Requirements and acceptance criteria are co-located with clear traceability\n- Implementation Plan lives in README.md (single source of truth for the plan)\n- Execution Plan lives in progress.md (single source of truth for actual progress)\n\n**Cons:**\n- Two files to maintain — requires reading both to get the full picture\n- More complex structure\n- Requires discipline to keep progress.md updated (hand-maintained, not auto-generated)\n- Agents need to read both files to understand plan + current status\n- Implementation Plan and Execution Plan are in separate files (requires cross-referencing)\n\n**Open Questions:**\n- Not chosen — this option was not carried forward with the same scrutiny/refinement pass as Option 1, since Option 1 was selected as the Decision Outcome. Retained here for reference only.\n- Still has the original Implementation Plan / Execution Plan split (across two files, no less), i.e. the sync-burden issue identified and resolved in Option 1 via a single Task List with inline status was never addressed here.\n- No `history.md`-equivalent or rotation mechanism for `progress.md`'s `Recent Updates` growth.\n- Template-location ambiguity applies here too — no separate reusable template files, only what's embedded in this ADR.\n- To be answered later, if this option is ever revisited: same open items as Option 1 (archival/lifecycle rule, template versioning path, potential atomic status-update tooling)."
      }
    ],
    "more_information": "- specmgr repository: https://github.com/anomalyco/biz.dfch.SpecMgr"
  }
}
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md</path>
<type>file</type>
<content>
1: ---
2: id: feat-NNN-slug
3: version: 1.0.0
4: status: planning
5: created: YYYY-MM-DD
6: updated: YYYY-MM-DD
7: ---
8: 
9: # Feature: [Feature Title]
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Brief description of what this feature does and why it matters.
16: 
17: ### Requirements
18: 
19: - REQ-001: [Functional requirement]
20: - REQ-002: [Non-functional requirement]
21: - REQ-003: [Constraint or dependency]
22: 
23: ### Acceptance Criteria
24: 
25: - [ ] ACC-001: Verifies REQ-001 — [testable condition]
26: - [ ] ACC-002: Verifies REQ-002 — [testable condition]
27: - [ ] ACC-003: Verifies REQ-003 — [testable condition]
28: 
29: ### Scope
30: 
31: What is included in this feature:
32: - Item 1
33: - Item 2
34: 
35: What is explicitly out of scope:
36: - Item A
37: - Item B
38: 
39: ### Dependencies
40: 
41: - Depends on: [other feat-NNN-slug, ADR id, or external]
42: - Blocks: [other feat-NNN-slug]
43: 
44: ### Design Notes
45: 
46: Any architectural decisions, patterns, or design rationale relevant to this feature.
47: 
48: ### Related ADRs
49: 
50: - [ADR id]: [Title]
51: - [ADR id]: [Title]
52: 
53: ### Task List
54: 
55: Single, canonical breakdown of work phases and tasks. Status lives on the
56: task itself — there is no separate "planned" vs. "executed" list to keep in
57: sync; a task's line *is* its current status. Update it in place as work
58: progresses (edit, don't duplicate).
59: 
60: #### Phase 1: [Phase name]
61: - [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)
62: - [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10
63: - [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)
64: 
65: #### Phase 2: [Phase name]
66: - [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started
67: - [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started
68: 
69: **Note:** If a task's scope changes mid-flight, edit its description in place;
70: rely on git history (`git log -p` on this file) to recover what was
71: originally planned, rather than keeping a second copy of the task around.
72: 
73: ## Progress
74: 
75: ### Current Status
76: 
77: **As of [YYYY-MM-DD]**: [Brief status summary]
78: 
79: ### Blockers
80: 
81: - [ ] Blocker 1 — [description, impact, mitigation]
82: - [ ] Blocker 2 — [description, impact, mitigation]
83: 
84: (Remove this section if no blockers.)
85: 
86: ### Recent Updates
87: 
88: If this section grows too long, move older entries to `history.md` in this
89: same folder and leave a pointer here, e.g.:
90: `See history.md for updates before YYYY-MM-DD.`
91: 
92: #### Update [YYYY-MM-DDTHH:mm:ssz] (newest)
93: - Completed: [what was done]
94: - Next: [what comes next]
95: - Notes: [any relevant context]
96: 
97: #### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)
98: - Completed: [what was done]
99: - Next: [what comes next]
100: - Notes: [any relevant context]
101: 
102: ### Decisions Made
103: 
104: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
105: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
106: 
107: ### Related PRs / Commits
108: 
109: - [PR #NNN](link): [description]
110: - [Commit hash](link): [description]

(End of file - total 110 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 9.8s)

_Thinking:_

Alright, let me read the feat-16 README and understand its structure, especially since it was a domain addition (problem statement) feature. That's what the user wants to mirror.




Now let me read the feat-16 problem statement feature README to understand its structure.



**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-16-problem-statement/README.md"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-16-problem-statement/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-25
3: id: feat-16-problem-statement
4: status: done
5: updated: 2026-08-25
6: version: 1.0.0
7: ---
8: 
9: # Feature: Add artifact type Problem Statement (prb)
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Add a new markdown artifact type, `ProblemStatement` (abbreviation `prb`),
16: for capturing a Six-Sigma-style problem statement: a factual, evidence-led
17: description of the gap between the current and desired state of a system —
18: deliberately free of assumed causes, blame, or solutions. `prb` follows the
19: domain-first hierarchy and MCP surface already established by `req`/`tsk`/
20: `qa` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/
21: resources shape almost exactly, and reuses their whole-body update
22: convention rather than ADR's granular `update_section` mechanism.
23: 
24: The body's `Current State` section is structured around the classic 5W2H
25: ("What/Why/Where/Who/When/How/How Often") interview questions from
26: <https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/>,
27: each under its own fixed heading so an answer can be added, referenced, and
28: refined independently over the document's lifetime. `Gap`/`Impact`/
29: `Future State` follow the expected-vs-actual/measurable-gap/goal-statement
30: discipline from
31: <https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/>.
32: Two new prompts (`create_prb`/`update_prb`) narrate an interactive,
33: `TodoWrite` + `question`-tool-driven interview flow (precedented by
34: `tsk/prompts/implement_task.py`), including agent-drafted `Summary` and
35: `Gap` synthesis from whichever answers the user chooses to supply.
36: 
37: ### Requirements
38: 
39: - REQ-001: Define the `prb` markdown schema — frontmatter (`type="prb"`,
40:   4-value status set `draft`/`active`/`resolved`/`cancelled`) and body (H1
41:   title, optional leading comment, mandatory `## Current State` holding a
42:   mandatory `### Summary` plus 7 optional, fixed-heading 5W2H `### ` question
43:   leaves, mandatory `## Gap`, optional `## Impact`, mandatory
44:   `## Future State`, optional `## References`, optional `## More Information`).
45: - REQ-002: Pydantic models under `prb/models/v1/` (frontmatter, body,
46:   document, parser, summary), domain-first, mirroring `tsk`/`qa`'s exact
47:   file shapes. No `models/md` engine changes are needed (unlike QA's
48:   `end_marker` addition) — every field is buildable with the existing
49:   declarative heading-mapped parser.
50: - REQ-003: Parse/validate `prb` documents from markdown, mirroring
51:   `parse_req`/`parse_tsk`/`parse_qa`'s two-error-channel convention
52:   (`AssertionError` for structural problems, `pydantic.ValidationError` for
53:   field-level problems).
54: - REQ-004: MCP tools mirroring REQ/TSK/QA's lifecycle surface, **plus**
55:   `list_prb` as a paged tool from day one (per ADR
56:   ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
57:   `specmgr://prb/list` resource and convert it later): `parse_prb`,
58:   `create_prb`, `update_prb`, `set_status_prb`, `delete_prb` (stub),
59:   `validate_prb`, `get_prb`, `get_prb_example`, `get_prb_template`,
60:   `list_prb`.
61: - REQ-005: MCP resources: `specmgr://prb/schema`, `/example`, `/template`
62:   (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
63:   reads are `get_prb`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
64: - REQ-006: MCP prompts `create_prb`/`update_prb` — narrated,
65:   `TodoWrite` + `question`-tool-driven interview flows (no other prompt in
66:   this codebase calls `create_*`/`update_*` in a loop over 7 sub-questions
67:   with agent-synthesized `Summary`/`Gap` text, so this is a new prompt
68:   shape, though it reuses the `TodoWrite`/`question`-tool narration pattern
69:   from `tsk/prompts/implement_task.py` and the dedup-check-first pattern
70:   from `req/prompts/create_req.py`). Both use their own packaged
71:   instructions data file (`prb/data/prb_create_instructions.md`/
72:   `prb_update_instructions.md`), not an inline string.
73: - REQ-007: Packaged example/template/schema data (`prb/data/`) via the
74:   existing generic `general/tools/_packaged_data.py`, with the matching
75:   `pyproject.toml` package-data entry, pre-commit hook, and CI step.
76: - REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
77:   `prb` entry in the doc-type registry, `commands/schema.py`),
78:   `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
79:   updated to seven domain/cross-cutting packages.
80: 
81: ### Acceptance Criteria
82: 
83: - [x] ACC-001: Verifies REQ-001 — schema documented (`docs/prb_schema.json`,
84:   `specmgr://prb/schema`); a reference `prb_reference.md` exercising every
85:   field (all 7 questions answered, `Impact`/`References`/
86:   `More Information` all present) round-trips through the parser. **PASS**
87:   — `docs/prb_schema.json` exists (2020-12 JSON Schema, `$comment: "v1"`,
88:   `title: PrbDocument`), `specmgr://prb/schema` resolves the packaged copy
89:   and returns the same 8 top-level keys; `.specmgr/feat/feat-16-problem-statement/prb_reference.md`
90:   round-trips via `tests/prb/models/v1/test_parser.py::TestParsePrb::test_parses_full_reference_document`.
91: - [x] ACC-002: Verifies REQ-002 — Pydantic models validate required
92:   (`Summary`, `Gap`, `Future State`) vs. optional (7 questions, `Impact`,
93:   `References`, `More Information`) fields correctly; `PrbFrontmatter.status`
94:   rejects any value outside the four-value set. **PASS** —
95:   `tests/prb/models/v1/test_body.py`/`test_frontmatter.py` (32 tests)
96:   cover each field's mandatory/optional behavior individually;
97:   `test_parser.py::test_invalid_status_raises_validation_error` confirms
98:   the closed 4-value status set.
99: - [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
100:   well-formed document; missing a mandatory section raises
101:   `AssertionError`; an invalid field value raises `pydantic.ValidationError`.
102:   **PASS** — `test_parser.py`'s 9 tests, re-run live: minimal/full-reference
103:   parses OK; `test_missing_current_state_section_raises_assertion_error`,
104:   `test_missing_gap_section_raises_assertion_error`,
105:   `test_missing_future_state_section_raises_assertion_error`,
106:   `test_missing_summary_raises_assertion_error` (all `AssertionError`);
107:   `test_invalid_status_raises_validation_error` (`pydantic.ValidationError`).
108: - [x] ACC-004: Verifies REQ-004 — every listed tool is implemented,
109:   registered, and callable; `list_prb` returns a `PagedResult[PrbSummary]`
110:   with default page size 25 / cap 100, mirroring the other five domains'
111:   `list_<d>` tools exactly (no resource-first-then-converted history for
112:   this domain). **PASS** — live `mcp.list_tools()` call confirms all 10:
113:   `create_prb`, `delete_prb`, `get_prb`, `get_prb_example`,
114:   `get_prb_template`, `list_prb`, `parse_prb`, `set_status_prb`,
115:   `update_prb`, `validate_prb`; `general/tools/_paging.py`'s
116:   `DEFAULT_MAX_RESULTS = 25`/`MAX_MAX_RESULTS = 100` confirmed used by
117:   `list_prb`; live integration test
118:   (`tests/prb/tools/test_integration.py`) exercises the full
119:   create→update→set_status→get→list→delete(stub) lifecycle end to end.
120: - [x] ACC-005: Verifies REQ-005 — every listed resource is implemented and
121:   registered. **PASS** — live `mcp.list_resources()` call confirms all 3:
122:   `specmgr://prb/example`, `specmgr://prb/schema`, `specmgr://prb/template`
123:   (no `/{id}`, no `/list`, as designed).
124: - [x] ACC-006: Verifies REQ-006 — `create_prb`/`update_prb` prompts
125:   narrate: (a) a duplicate/similar-document check via `list_prb` first,
126:   (b) building a `TodoWrite` list covering the `Summary` + all 7 questions
127:   - `Gap` + `Impact` + `Future State`, (c) using the `question` tool to
128:     elicit each optional answer (explicitly allowing skip), (d)
129:     agent-synthesizing/refining the `Summary` from whichever answers exist,
130:     (e) agent-drafting/refining the `Gap` from the current-state answers and
131:     confirming it with the user via the `question` tool before finalizing,
132:     (f) calling `create_prb`/`update_prb` (whole-body) at the end — verified
133:     live by actually running through both prompts end to end against a real
134:     document, not just asserting their static text. **PASS** — read both
135:     packaged instruction files (`prb_create_instructions.md`/
136:     `prb_update_instructions.md`) in full and manually walked their
137:     narrated 10-step/9-step flows end to end against a real document via
138:     `tests/prb/tools/test_integration.py`, simulating every `question`-tool
139:     answer myself: (0) `list_prb` dedup check narrated first in
140:     `create_prb`; (1)-(2) `TodoWrite` list + per-question `question`-tool
141:     elicitation, explicit skip allowance; (3) `Summary` synthesis; (4)
142:     `Gap` draft + `question`-tool confirmation before finalizing; (5)-(7)
143:     optional `Impact`/mandatory `Future State`/optional
144:     `References`/`More Information`; (8)-(9) template/example/schema
145:     reference then `create_prb(content)`. Confirmed the resulting document
146:     (`test_create_update_set_status_get_list_delete_roundtrip`) actually
147:     carries a `Summary`, `Question3` (`Where Is the Problem Observed?`),
148:     `Impact`, `Gap`, `Future State` exactly as narrated.
149:     `prb_update_instructions.md`'s symmetric flow (`get_prb` first, show
150:     answered/unanswered questions, full `Summary` re-synthesis not append,
151:     `Gap` re-confirmation, `set_status_prb` as a separate optional
152:     follow-up) was walked the same way via the test's `update_prb`/
153:     `set_status_prb` steps.
154: - [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
155:   real, non-editable install (`uv build --wheel` + scratch-venv install),
156:   mirroring TSK's own feat-10 Task 5.1-equivalent verification. **PASS** —
157:   `uv build --wheel` produced `dist/biz_dfch_specmgr-0.9.0-py3-none-any.whl`
158:   containing all 5 `prb/data/*` files; installed non-editably
159:   (`pip install "...[mcp]"`) into a scratch venv under `/tmp/opencode/`
160:   (outside the repo entirely); confirmed `get_prb_example()`/
161:   `get_prb_template()`/`prb_schema()` all resolved real, non-empty content
162:   from `.../scratch-venv/lib/.../site-packages/biz/dfch/specmgr/prb/...`
163:   (verified via `inspect.getfile`), not the source checkout. Wheel/venv
164:   cleaned up afterward; `dist/`/`build/` left empty (gitignored).
165: - [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
166:   `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
167:   reflects seven domain/cross-cutting packages. **PASS** — `specmgr docs`/
168:   `specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema` (generic + `--type
169:   prb --output-dir src/biz/dfch/specmgr/prb/data`) all re-run: every
170:   generated file reported "unchanged" except `docs/GENERATED.md`'s test
171:   file count (204 → 205, expected from this phase's new
172:   `tests/prb/tools/test_integration.py`); `AGENTS.md`'s heading already
173:   reads "seven domain/cross-cutting packages implemented (ADR, REQ, UC,
174:   TSK, QA, PRB, general)" from Phase 4.
175: 
176: ### Scope
177: 
178: **Included in this feature:**
179: 
180: - The `prb` markdown schema, Pydantic models, parser, and summary under
181:   `prb/models/v1/`.
182: - Full MCP surface (tools/resources/prompts/packaged data), including
183:   `list_prb` as a tool (not a resource) from the start.
184: - The interactive `create_prb`/`update_prb` prompt behavior (`TodoWrite` +
185:   `question`-tool-driven 5W2H interview, agent-synthesized `Summary`/`Gap`).
186: - Tests mirroring `tests/tsk/`/`tests/qa/`'s layout and coverage depth.
187: - Cross-cutting registration (`server.py`, `pyproject.toml`,
188:   `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).
189: 
190: **Explicitly out of scope:**
191: 
192: - A **Root Cause** section/field. Six Sigma discipline (and both source
193:   articles) explicitly requires a problem statement to stay free of
194:   assumed causes — root-cause analysis is a separate, later activity, not
195:   part of this artifact. If/when a dedicated RCA artifact type is wanted,
196:   it should be its own future feature, only ever cross-referenced from
197:   `References`, never embedded here.
198: - Structured cross-referencing of `References` to real REQ/UC/ADR/other
199:   PRB documents (typed sub-lists, id validation, etc.) — v1 keeps
200:   `References` as opaque free text, matching `MoreInformation`/`Notes`
201:   elsewhere. Revisit only if a concrete need emerges.
202: - ADR-style granular `update_section`/option-style per-field mutation
203:   tools — `update_prb` is a single whole-body replace tool, like
204:   `update_req`/`update_tsk`/`update_qa`. Individual questions stay
205:   addressable by their fixed heading text within the markdown body itself,
206:   not via a dedicated tool per section.
207: - Any deterministic/algorithmic (non-LLM) computation of `Summary`/`Gap`
208:   text. Both are synthesized by the calling agent while following the
209:   prompt's narrated instructions — no NLP/heuristic code ships in `src/`
210:   for this.
211: - A `specmgr prb-toc`-equivalent generation command or dedicated CI/
212:   pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
213:   `specmgr schema` already provide generically.
214: 
215: ### Dependencies
216: 
217: - Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
218:   hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
219:   `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
220:   (tool-only id-based reads, no `specmgr://prb/{id}` resource), ADR
221:   ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
222:   not a resource — `list_prb` must follow this from day one), the existing
223:   `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
224:   `general/models/{DocSummary,PagedResult}` infrastructure, and the
225:   existing `models/md` engine (`MarkdownSection1WithComment`,
226:   `MarkdownSection2`, `MarkdownSection3`, `@alias`) — reused as-is, no
227:   engine changes anticipated.
228: - Blocks: None identified yet.
229: - Related, but explicitly out of scope here: `feat-7-various-improvements`
230:   Task 0.24 (cleaning up `AGENTS.md`'s stale `specmgr://<d>/list`
231:   resource-vs-tool wording for TSK/QA, found during this feature's own
232:   planning session but not this feature's concern to fix).
233: 
234: ### Design Notes
235: 
236: **Schema:**
237: 
238: ```
239: PrbFrontmatter(MarkdownFrontmatter): type: Literal["prb"];
240:   status in {draft, active, resolved, cancelled}
241: 
242: Prb(MarkdownSection1WithComment)                # H1, free-form title (alias ".+"); inherited optional comment
243: ├── current_state: CurrentState                  # mandatory H2 "Current State"
244: ├── gap: Gap                                     # mandatory H2 "Gap", opaque free text leaf
245: ├── impact: Impact | None                        # optional H2 "Impact", opaque free text leaf
246: ├── future_state: FutureState                    # mandatory H2 "Future State", opaque free text leaf
247: ├── references: References | None                # optional H2 "References", opaque free text leaf
248: └── more_information: MoreInformation | None      # optional H2 "More Information", opaque free text leaf (REQ precedent)
249: 
250: CurrentState(MarkdownSection2)                   # H2 "Current State"
251: ├── summary: Summary                             # mandatory H3 "Summary", opaque free text leaf
252: ├── question_1: Question1 | None                 # optional H3, @alias(value="What Is the Problem\\?")
253: ├── question_2: Question2 | None                 # optional H3, @alias(value="Why Is It a Problem\\?")
254: ├── question_3: Question3 | None                 # optional H3, @alias(value="Where Is the Problem Observed\\?")
255: ├── question_4: Question4 | None                 # optional H3, @alias(value="Who Is Impacted\\?")
256: ├── question_5: Question5 | None                 # optional H3, @alias(value="When Was the Problem First Observed\\?")
257: ├── question_6: Question6 | None                 # optional H3, @alias(value="How Is the Problem Observed\\?")
258: └── question_7: Question7 | None                 # optional H3, @alias(value="How Often Is the Problem Observed\\?")
259: ```
260: 
261: Every `Question{N}`/`Summary`/`Gap`/`Impact`/`FutureState`/`References`/
262: `MoreInformation` class is a bare leaf subclass with no further declared
263: fields — the same "opaque, captures any remaining markdown verbatim"
264: pattern already verified for REQ's `MoreInformation`/`Notes` and QA's
265: `RawRequirements`/`QaAnswer` (no new engine mechanism needed for this).
266: 
267: **Question heading wording is fixed and exact** (verbatim from the
268: iSixSigma 5W2H list, each requiring an explicit `@alias(...)` since the
269: class names `Question1`..`Question7` don't derive to this wording via the
270: implicit `AliasType.SPACE_SEPARATED` convention):
271: 
272: 1. What Is the Problem?
273: 2. Why Is It a Problem?
274: 3. Where Is the Problem Observed?
275: 4. Who Is Impacted?
276: 5. When Was the Problem First Observed?
277: 6. How Is the Problem Observed?
278: 7. How Often Is the Problem Observed?
279: 
280: **`Summary` is mandatory, the 7 questions are all optional.** A freshly
281: created `prb` document may have zero questions answered yet (all deferred
282: to a later `update_prb` call) but must always carry *some* `Summary` text
283: (even a short placeholder at creation time) — mirrors ADR's own
284: mandatory-vs-optional body-field split, not TSK's "must seed a first
285: Recent Updates entry" pattern (there is no dynamic list here).
286: 
287: **`Gap`/`Future State` are mandatory; `Impact`/`References`/
288: `More Information` are optional** — matching the plain list the user gave,
289: plus the newly-added optional `Impact`, placed between `Gap` and
290: `Future State` (current state → gap → why it matters → target state).
291: 
292: **No Root Cause section** (see Scope: Explicitly out of scope) — this is a
293: deliberate, methodology-driven omission, not an oversight.
294: 
295: **Update mechanism: whole-body `update_prb(id, content)`**, not an
296: ADR-style `update_section`. The generic `adr/tools/update_section.py`
297: mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
298: ADR-specific code, not a shared cross-domain component — reusing it for
299: PRB would mean building a second, parallel implementation. Individual
300: questions/sections stay addressable by grepping/editing their fixed
301: heading text within the whole-body markdown, which is what "fixed heading
302: per question" is actually for (addressability without a dedicated tool
303: per field).
304: 
305: **`list_prb` is a paged tool from day one** (`@mcp.tool(name="list_prb")`
306: returning `PagedResult[PrbSummary]`, via `general/tools/_paging.py`'s
307: `paginate`/`normalize_paging`), not a `specmgr://prb/list` resource —
308: unlike REQ/TSK/QA (which launched as resources and were converted later in
309: feat-13), PRB is a new domain built *after* ADR ec9f5262 was accepted, so
310: it must not repeat the resource-then-convert history. `PrbSummary`
311: subclasses `general/models/summary.py::DocSummary` (`id`/`title`/`status`/
312: `ref`), like `ReqSummary`/`TskSummary`/`QaSummary`.
313: 
314: **Prompts are narrated instructions only** (return a string, auto-wrapped
315: as a `UserMessage` by the MCP SDK) — `create_prb`/`update_prb` never call
316: `TodoWrite`/`question`/`get_prb`/`create_prb`/`update_prb` themselves; they
317: only narrate that the calling LLM should. This is the same contract every
318: existing prompt in this codebase already follows
319: (`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).
320: 
321: - `create_prb(topic: str) -> str`: instructs the LLM to (1) call `list_prb`
322:   first to check for an existing, similar problem statement (mirrors
323:   `create_req`'s dedup-check pattern) and ask the user via `question` if a
324:   near-duplicate is found; (2) build a `TodoWrite` list with one entry per
325:   the `Summary` + 7 questions + `Gap` + `Impact` + `Future State`; (3) use
326:   the `question` tool to elicit each of the 7 answers in turn, explicitly
327:   allowing the user to skip any; (4) synthesize a `Summary` paragraph from
328:   whichever answers were actually given; (5) draft a candidate `Gap`
329:   statement from the collected current-state answers (following the
330:   expected-vs-actual/measurable-difference formula from the
331:   LearnLeanSigma article) and confirm/refine it with the user via
332:   `question` before finalizing; (6) optionally ask for `Impact`; (7) ask
333:   for `Future State` (desired/target condition); (8) optionally ask for
334:   `References`/`More Information`; (9) assemble the full body markdown per
335:   the fixed schema above and call `create_prb(content)`.
336: - `update_prb(id: str) -> str`: instructs the LLM to (1) call `get_prb(id)`
337:   first (never assume prior state); (2) show the user which of the 7
338:   questions already have answers and which are still empty, and ask via
339:   `question` which ones (if any) they want to add to or revise; (3) for
340:   each selected question, elicit the new/revised text via `question`; (4)
341:   regenerate the `Summary` from the *complete*, current set of answers
342:   (a full re-synthesis, not an append); (5) re-draft/refine the `Gap`
343:   the same way as `create_prb` step 5, based on the now-current-state
344:   answers, confirming with the user; (6) optionally revise `Impact`/
345:   `Future State`/`References`/`More Information`; (7) call
346:   `update_prb(id, content)` (whole-body replace, carrying forward every
347:   unchanged section); (8) mention `set_status_prb` as a separate, optional
348:   follow-up (e.g. `resolved` once `Future State` has genuinely been
349:   reached, `cancelled` if abandoned).
350: 
351: Both prompts' instructional text lives in packaged data files
352: (`prb/data/prb_create_instructions.md`/`prb_update_instructions.md`, read
353: via `general.tools._packaged_data.read_packaged_text`, `string.Template`
354: substitution), matching `req_create_instructions.md`/
355: `tsk_implement_instructions.md`'s precedent — not an inline Python string
356: — since the narration is long enough to warrant it.
357: 
358: **Frontmatter status** (`draft`/`active`/`resolved`/`cancelled`) mirrors
359: TSK/QA's 4-value closed set exactly, with PRB-specific semantics: `draft`
360: = still being filled in; `active` = current state captured, gap/future
361: state being refined; `resolved` = future state reached; `cancelled` =
362: abandoned.
363: 
364: ### Related ADRs
365: 
366: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
367:   document-type domain (domain-first hierarchy)
368: - bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
369:   markdown document types
370: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
371:   (`get_prb`), not a resource
372: - ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
373:   MCP tool (`list_prb`), not a resource — must be followed from the start
374:   for this new domain, not retrofitted later
375: - 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
376:   and explicitly *not* reused for `prb` (see Design Notes)
377: 
378: No new ADR is anticipated for this feature — every schema/tooling decision
379: either follows an existing ADR's precedent directly or is scoped enough to
380: log only in this file's own Decisions Made.
381: 
382: ### Task List
383: 
384: Single, canonical breakdown of work phases and tasks. Status lives on the
385: task itself. Each phase ends with a mandatory phase-end task (tests, full
386: quality gate, README Progress update), mirroring feat-10/feat-12's
387: per-phase commit discipline, since implementation is likely to span
388: multiple sessions.
389: 
390: #### Phase 1: Specification
391: 
392: - [x] Task 1.1: Write a full reference `prb_reference.md`
393:   (`.specmgr/feat/feat-16-problem-statement/prb_reference.md`) exercising
394:   every field (all 7 questions answered, `Impact`/`References`/
395:   `More Information` all present) — depends on: none — status: done
396: - [x] Task 1.2: Define `prb` frontmatter (`prb/models/v1/frontmatter.py` —
397:   `PrbFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["prb"]`,
398:   4-value status set `draft`/`active`/`resolved`/`cancelled`, mirroring
399:   `TskFrontmatter`'s `_ALLOWED_STATUSES` pattern) — depends on: none —
400:   status: done
401: - [x] Task 1.3: Define `prb` body structure
402:   (`prb/models/v1/body.py`) — `Prb(MarkdownSection1WithComment)`,
403:   `CurrentState(MarkdownSection2)` with mandatory `summary: Summary` and
404:   optional `question_1..question_7: Question{N} | None` (each with an
405:   explicit `@alias(...)` matching the exact 5W2H wording — see Design
406:   Notes), `Gap`/`FutureState` (mandatory leaves), `Impact`/`References`/
407:   `MoreInformation` (optional leaves) — depends on: Task 1.2 — status:
408:   done
409: - [x] Task 1.4: `tests/prb/models/v1/test_frontmatter.py`, `test_body.py`
410:   — structural + validation tests mirroring `tests/tsk/models/v1/`/
411:   `tests/qa/models/v1/`, explicit coverage of mandatory-vs-optional field
412:   combinations (each of the 7 questions individually absent/present;
413:   `Impact`/`References`/`More Information` absent/present) — depends on:
414:   Task 1.3 — status: done
415: - [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
416:   gate (ruff format/check, vulture, full `unittest` suite); confirm
417:   `prb_reference.md` is `specmgr mdformat`-clean; update this README's
418:   Progress section — depends on: Task 1.1, Task 1.4 — status: done
419: 
420: #### Phase 2: Pydantic Models, Parser & Schema
421: 
422: - [x] Task 2.1: `prb/models/v1/document.py` (`PrbDocument(frontmatter, body)`, mirroring `TskDocument`/`QaDocument`) — depends on: Task 1.3 —
423:   status: done
424: - [x] Task 2.2: Implement `parse_prb(text: str) -> PrbDocument` (model-layer
425:   function, mirrors `parse_tsk`/`parse_qa`) — depends on: Task 2.1 —
426:   status: done
427: - [x] Task 2.3: `prb/models/v1/summary.py` (`PrbSummary(DocSummary)`,
428:   subclassing `general/models/summary.py::DocSummary`, for `list_prb`) —
429:   depends on: Task 2.1 — status: done
430: - [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
431:   optional field (schema-quality parity with REQ/TSK/QA) — depends on:
432:   Task 2.1 — status: done
433: - [x] Task 2.5: Implement `generate_prb_schema()` in `commands/schema.py`
434:   (mirroring `generate_tsk_schema`/`generate_qa_schema`, via
435:   `PrbDocument.model_json_schema()`) + register `"prb"` in the
436:   `specmgr schema` doc-type generator registry (`_GENERATORS`); draft
437:   `docs/prb_schema.json` — depends on: Task 2.1 — status: done
438: - [x] Task 2.6: `tests/prb/models/v1/test_parser.py` — mirrors
439:   `TestParseTsk`/`TestParseQa`'s shape (minimal doc, full reference-doc
440:   round-trip, defaults-when-absent, invalid status, missing-mandatory-
441:   section `AssertionError`, invalid-field `ValidationError`) — depends on:
442:   Task 2.2, Task 2.5 — status: done
443: - [x] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
444:   including Task 2.6's new tests; update this README's Progress section —
445:   depends on: Task 2.5, Task 2.6 — status: done
446: 
447: #### Phase 3: MCP Surface
448: 
449: - [x] Task 3.1: `prb/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
450:   wrappers over `general/tools/_doc_paths.py` (mirrors `tsk/tools/`/
451:   `qa/tools/` exactly) — depends on: Task 2.2 — status: done
452: - [x] Task 3.2: `parse_prb(path: str) -> PrbDocument` tool wrapper
453:   (`prb/tools/parse_prb.py`) — depends on: Task 3.1 — status: done
454: - [x] Task 3.3: `create_prb(content: str) -> PrbDocument` tool (body-only
455:   content; MCP builds frontmatter: `id`, `type="prb"`, `status="draft"`,
456:   `created=updated=now`, `version`) — depends on: Task 3.1 — status:
457:   done
458: - [x] Task 3.4: `update_prb(id, content) -> PrbDocument` tool (whole-body
459:   replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
460:   `updated`) — depends on: Task 3.1 — status: done
461: - [x] Task 3.5: `set_status_prb(id, status) -> PrbDocument` tool (only path
462:   that changes `status`; reconstructs `PrbFrontmatter` via its own
463:   constructor so the 4-value validator runs, mirroring `set_status_tsk`/
464:   `set_status_qa`) — depends on: Task 3.1 — status: done
465: - [x] Task 3.6: `delete_prb(id) -> NoReturn` stub tool — depends on: Task
466:   3.1 — status: done
467: - [x] Task 3.7: `validate_prb(content, full=False) -> bool` tool — depends
468:   on: none — status: done
469: - [x] Task 3.8: `get_prb(id) -> PrbDocument` tool (id-based single-document
470:   read; tool, not resource) — depends on: Task 3.1 — status: done
471: - [x] Task 3.9: `list_prb(max_results=None, offset=None) -> PagedResult[PrbSummary]`
472:   tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
473:   (default page size 25, cap 100), preserving the standard skip-malformed-
474:   file scan behavior — depends on: Task 2.3, Task 3.1 — status:
475:   done
476: - [x] Task 3.10: `get_prb_example`/`get_prb_template` tools + packaged data
477:   (`prb/data/prb_example.md`, `prb/data/prb_template.md`) via
478:   `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
479:   done
480: - [x] Task 3.11: `prb/resources/{prb_schema,prb_example,prb_template}.py`
481:   — `specmgr://prb/schema` (packaged `prb/data/prb_schema.json`, mirroring
482:   `specmgr://tsk/schema`), `specmgr://prb/example`, `specmgr://prb/template`
483:   (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
484:   done
485: - [x] Task 3.12: `pyproject.toml` package-data entry for
486:   `biz.dfch.specmgr.prb` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
487:   — widen the shared schema-hook glob to include `prb/models/v1`, add a
488:   `specmgr-schema-prb-package` hook — depends on: Task 2.5 — status:
489:   done
490: - [x] Task 3.13: `.github/workflows/ci.yml` — add the `docs/prb_schema.json`
491:   check + packaged-copy check steps — depends on: Task 2.5 — status:
492:   done
493: - [x] Task 3.14: `prb/data/prb_create_instructions.md` +
494:   `prb/prompts/create_prb.py` (`@mcp.prompt()`, `string.Template`
495:   substitution, narrates the full interview flow — see Design Notes) —
496:   depends on: Tasks 3.3, 3.9 — status: done
497: - [x] Task 3.15: `prb/data/prb_update_instructions.md` +
498:   `prb/prompts/update_prb.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
499:   done
500: - [x] Task 3.16: `prb/__init__.py` (docstring + `from . import prompts, resources, tools`), add `prb` to `server.py`'s bottom-of-file domain
501:   import line (alphabetical: `adr, general, prb, qa, req, tsk, uc`) and
502:   update its module docstring (Tools/Resources/Prompts sections) — depends
503:   on: Tasks 3.2-3.15 — status: done
504: - [x] Task 3.17: `tests/prb/tools/...`, `tests/prb/resources/...`,
505:   `tests/prb/prompts/...` mirroring `tests/tsk/`/`tests/qa/`'s layout,
506:   including live end-to-end coverage of `create_prb`/`update_prb`'s
507:   narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_prb`'s
508:   paging behavior (default page size, `max_results` clamping, `offset`
509:   paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
510:   done
511: - [x] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
512:   including Task 3.17's new tests; update this README's Progress section
513:   — depends on: Task 3.17 — status: done
514: 
515: #### Phase 4: Cross-cutting registration
516: 
517: - [x] Task 4.1: `AGENTS.md` — update heading to "seven domain/cross-cutting
518:   packages implemented (ADR, REQ, UC, TSK, QA, PRB, general)"; add a
519:   `prb/` bullet (chronological order, after `qa/`); update the "Still
520:   genuinely missing" list (`validate_prb` not enforced via pre-commit/CI,
521:   `delete_prb` stub) and the closing domain-enumeration paragraphs —
522:   depends on: Phase 3 complete — status: done
523: - [x] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
524:   regeneration — confirm `prb` appears correctly and all three commands
525:   report zero drift — depends on: Task 4.1 — status: done
526: - [x] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
527:   update this README's Progress section — depends on: Task 4.2 — status:
528:   done
529: 
530: #### Phase 5: Final cross-cutting verification
531: 
532: - [x] Task 5.1: Final verification pass — walk every ACC-001..008 and
533:   confirm each is satisfied with concrete evidence (including a live
534:   `create_prb`→`update_prb`→`set_status_prb` run, not just unit tests);
535:   run the full quality gate (ruff format/check, pylint advisory, vulture,
536:   unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
537:   checks) end to end; set feature status to `done` — depends on: Phase
538:   1-4 complete — status: done
539: 
540: **Note:** If a task's scope changes mid-flight, edit its description in
541: place; rely on git history (`git log -p` on this file) to recover what was
542: originally planned, rather than keeping a second copy of the task around.
543: 
544: ## Progress
545: 
546: ### Current Status
547: 
548: **Feature complete, as of 2026-08-25.** All 5 phases done. `prb` (Problem
549: Statement) is a fully implemented seventh domain/cross-cutting
550: package (ADR, REQ, UC, TSK, QA, PRB, general), with a domain-first
551: `prb/models/v1/` schema (frontmatter, body — mandatory `Summary`/`Gap`/
552: `Future State`, 7 optional 5W2H questions, optional `Impact`/`References`/
553: `More Information`), a full MCP surface (10 tools including `list_prb` as
554: a paged tool from day one per ADR ec9f5262, 3 resources, 2 narrated
555: prompts, packaged data), and `AGENTS.md`/`specmgr docs`/`specmgr mcp-docs`/
556: `specmgr schema` all up to date and drift-free. Phase 5's final
557: verification pass walked every ACC-001..008 with concrete evidence
558: (see the Acceptance Criteria section above for the per-ACC verdicts),
559: including a live, non-mocked `create_prb`→`update_prb`→`set_status_prb`→
560: `get_prb`→`list_prb`→`delete_prb`(stub) lifecycle exercise
561: (`tests/prb/tools/test_integration.py`, isolated to a temp docs
562: directory), a manual walk-through of both prompts' narrated interview
563: flows against that same live document, and a real `uv build --wheel` +
564: scratch-venv, non-editable install confirming packaged data resolves
565: correctly outside the source tree. Full quality gate green: 1454 tests
566: (up from 1452), ruff format/check clean, vulture clean, pylint 8.96/10
567: advisory (pre-existing `redefined-builtin 'id'`/missing-test-docstring/
568: duplicate-code findings only, no regressions), zero drift in
569: `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema`
570: (both `docs/prb_schema.json` and the packaged copy) beyond
571: `docs/GENERATED.md`'s expected test-file-count bump (204 → 205).
572: Note: this feature folder uses the `feat-16-problem-statement` placeholder
573: id/slug (no GitHub issue filed yet, per `AGENTS.md`'s convention) — expect
574: it to be renamed to `feat-NNN-problem-statement` (frontmatter `id` updated
575: to match) once an issue number is assigned; do not treat `feat-0` as
576: permanent.
577: 
578: ### Blockers
579: 
580: None.
581: 
582: ### Recent Updates
583: 
584: #### Update 2026-08-25 (Phase 5: Final cross-cutting verification — feature complete)
585: 
586: - Completed Task 5.1, the final task of the feature. Walked every
587:   ACC-001..008 with concrete evidence (recorded inline in the Acceptance
588:   Criteria section above, each now checked `[x]`):
589:   - ACC-001/002/003 (schema/models/parser): confirmed via
590:     `docs/prb_schema.json`/`specmgr://prb/schema`, `prb_reference.md`'s
591:     round-trip, and the existing `tests/prb/models/v1/` suite (structural
592:     `AssertionError`s for each missing mandatory section, `Validation
593:     Error` for invalid `status`).
594:   - ACC-004/005 (tools/resources): live `mcp.list_tools()`/
595:     `list_resources()` calls against the actual `server.mcp` instance
596:     confirmed all 10 tools and all 3 resources are registered and
597:     callable; confirmed `list_prb` uses `general/tools/_paging.py`'s
598:     `DEFAULT_MAX_RESULTS = 25`/`MAX_MAX_RESULTS = 100`.
599:   - ACC-006 (prompts): read both packaged instruction files in full and
600:     manually walked their narrated flows end to end against a real
601:     document (see below), rather than only asserting narration text
602:     contains the right tool names.
603:   - ACC-007 (packaged data from a real install): built a real wheel
604:     (`uv build --wheel`), confirmed all 5 `prb/data/*` files are packaged
605:     inside it, installed it non-editably into a scratch venv under
606:     `/tmp/opencode/` (`pip install "biz_dfch_specmgr-...-py3-none-any.whl[mcp]"`),
607:     and confirmed `get_prb_example()`/`get_prb_template()`/`prb_schema()`
608:     resolve real content from that venv's `site-packages`, not the source
609:     checkout (`inspect.getfile` confirmed the module path). Wheel and
610:     scratch venv cleaned up afterward (`dist/`/`build/` removed; both are
611:     gitignored anyway).
612:   - ACC-008 (doc generation drift): re-ran `specmgr docs`/
613:     `specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema` (generic + the
614:     `--type prb --output-dir src/biz/dfch/specmgr/prb/data` packaged-copy
615:     invocation) — every generated file reported unchanged except
616:     `docs/GENERATED.md`'s test-file count (204 → 205, expected from this
617:     phase's own new test file); `AGENTS.md` already reflects seven
618:     domains from Phase 4.
619: - Added `tests/prb/tools/test_integration.py` (2 tests): a live,
620:   non-mocked lifecycle exercise —
621:   `create_prb`→`update_prb`→`set_status_prb`→`get_prb`→`list_prb`→
622:   `delete_prb` (confirms the stub still raises `NotImplementedError`
623:   without touching the filesystem) — plus a packaged
624:   example/template round-trip-via-`parse_prb` test. Isolated via the same
625:   `SPECMGR_DOCS_DIR`-pointed-at-a-`tempfile.TemporaryDirectory()` pattern
626:   already used by `test_create_prb.py`'s `TempPrbDirTestCase`, so nothing
627:   was ever written to the real, developer-configured `prb` base directory.
628:   This test doubles as the concrete evidence for ACC-004's "`list_prb`
629:   reflects the changes" and ACC-006's "verified live" requirements.
630: - Ran the full quality gate one final time: `ruff format --check`/
631:   `ruff check` (both clean), `pylint` (advisory, 8.96/10 — the pre-existing
632:   `redefined-builtin 'id'` (5 `prb` tools/prompts taking an `id` parameter,
633:   matching every other domain's own convention), missing-test-docstring,
634:   and `duplicate-code`-across-mirrored-test-files findings only; nothing
635:   new introduced by this phase's test file), `vulture src/ whitelist.py
636:   --min-confidence 60` (no findings), full `unittest` suite (**1454
637:   tests**, up from 1452, all green).
638: - Set this README's own frontmatter `status: planning` → `status: done`
639:   (top of file) as Task 5.1's own required action; every phase and every
640:   acceptance criterion is now checked off.
641: - Next: None — feature complete. A follow-up feature would be needed to
642:   (a) file a real GitHub issue and rename this folder from its `feat-16`
643:   placeholder if desired, (b) implement `delete_prb` for real, or (c)
644:   wire `validate_prb` (and its five siblings) into pre-commit/CI per
645:   ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73 — none of that is in this
646:   feature's scope.
647: - Notes: No new design decisions required this phase — purely
648:   verification, exactly as scoped. One clarification for future readers:
649:   ACC-006's "live" verification, per this phase's own task instructions,
650:   necessarily means manually executing the narrated flow using the real
651:   tool functions and self-simulated `question`-tool answers (there is no
652:   live human user or live MCP client in this environment) — both prompts
653:   themselves only ever return narration strings, by hard MCP-SDK contract,
654:   and never call `TodoWrite`/`question`/`list_prb`/`create_prb`/
655:   `update_prb` themselves; this was already true by design (see Phase 3's
656:   Decisions Made) and is not a limitation introduced by this
657:   verification pass.
658: 
659: #### Update 2026-08-25 (Phase 4: Cross-cutting registration)
660: 
661: - Completed Tasks 4.1-4.3. `AGENTS.md`: heading changed to "seven
662:   domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA, PRB,
663:   general)"; added a `prb/` bullet (chronological, right after `qa/`)
664:   describing its domain-first `prb/models/v1/` location, its full tool
665:   list, its three resources (`specmgr://prb/schema`/`/example`/
666:   `/template`, no `/{id}`, no `/list`), and its two prompts
667:   (`create_prb`/`update_prb`); updated the "Still genuinely missing" list
668:   to add `validate_prb` (alongside the other `validate_*` tools not yet
669:   enforced via pre-commit/CI) and `delete_prb` (alongside the other
670:   `delete_*` stubs); updated both closing domain-enumeration paragraphs
671:   (`Don't assume any other domain package exists beyond ...` and the
672:   `server.py` bottom-of-file import line description) to include `prb` in
673:   alphabetical position; updated the "`req`/`tsk`/`qa` each register
674:   tools, resources, and prompts; `uc` ..." sentence to
675:   "`req`/`tsk`/`qa`/`prb` each register tools, resources, and prompts;
676:   `uc` ...".
677: - Re-ran `specmgr schema` (all five doc types, including a separate
678:   `--type prb --output-dir src/biz/dfch/specmgr/prb/data` invocation for
679:   the packaged copy), `specmgr docs`, and `specmgr mcp-docs` — all three
680:   reported zero drift (only `AGENTS.md` shows as modified in `git
681:   status`; no generated file changed).
682: - Phase-end quality gate: `ruff format --check`/`ruff check` (both
683:   clean), `vulture src/ whitelist.py --min-confidence 60` (no findings),
684:   full `unittest` suite (1452 tests, unchanged from Phase 3, all green —
685:   expected, since this phase touched only `AGENTS.md`).
686: - Next: Phase 5 (Final cross-cutting verification) — walk every
687:   ACC-001..008 with concrete evidence including a live
688:   `create_prb`→`update_prb`→`set_status_prb` run, full quality gate end
689:   to end, set feature status to `done`.
690: - Notes: No design decisions required; this phase was purely
691:   documentation (AGENTS.md) plus re-confirming Phase 3's drift-free
692:   state, exactly as scoped.
693: 
694: #### Update 2026-08-25 (Phase 3: MCP Surface)
695: 
696: - Completed all of Tasks 3.1-3.18. New `src/biz/dfch/specmgr/prb/`
697:   sub-packages: `tools/` (`_paths.py`/`_io.py`/`_write.py`/`_lock.py`
698:   plumbing plus `parse_prb`, `create_prb`, `update_prb`, `set_status_prb`,
699:   `delete_prb` stub, `validate_prb`, `get_prb`, `list_prb`,
700:   `get_prb_example`, `get_prb_template` -- each a 1:1 port of the
701:   matching `tsk.tools`/`qa.tools` module, adapted for PRB's 4-value
702:   status set and mandatory `Gap`/`Future State` fields); `resources/`
703:   (`specmgr://prb/schema`/`/example`/`/template`, no `/list`, no
704:   `/{id}`); `prompts/` (`create_prb`/`update_prb`, each reading its own
705:   packaged instructions file via `string.Template`); `data/`
706:   (`prb_example.md` -- reused from `prb_reference.md` verbatim,
707:   `prb_template.md`, `prb_schema.json` -- the packaged copy generated by
708:   `specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data`,
709:   `prb_create_instructions.md`, `prb_update_instructions.md`).
710:   `prb/__init__.py` now imports `prompts`/`resources`/`tools`; `server.py`
711:   imports `prb` alphabetically (`adr, general, prb, qa, req, tsk, uc`)
712:   and its module docstring lists every new `prb` resource/tool/prompt.
713: - `create_prb`'s narrated instructions cover the full 9-step interview
714:   flow from the plan's Design Notes verbatim: (0) `list_prb` dedup check;
715:   (1) structure recap; (2) `TodoWrite`-list + `question`-tool-driven 5W2H
716:   interview, explicitly allowing skip; (3) `Summary` synthesis; (4) `Gap`
717:   drafting + `question`-tool confirmation; (5) optional `Impact`; (6)
718:   `Future State`; (7) optional `References`/`More Information`; (8)
719:   template/example/schema references; (9) the `create_prb(content)` tool
720:   call sequence. `update_prb`'s instructions cover the symmetric 8-step
721:   revision flow (read via `get_prb` first, show which of the 7 questions
722:   are answered, elicit revisions, full re-synthesis of `Summary` -- not
723:   an append, re-draft/confirm `Gap`, optional revisions to
724:   `Impact`/`Future State`/`References`/`More Information`,
725:   `update_prb(id, content)` whole-body replace, `set_status_prb` as a
726:   separate optional follow-up). Both prompts only ever return narration
727:   strings -- neither calls `TodoWrite`/`question`/`list_prb`/`get_prb`/
728:   `create_prb`/`update_prb` itself, matching every existing prompt's
729:   contract in this codebase.
730: - `pyproject.toml` gained a `biz.dfch.specmgr.prb` package-data entry
731:   (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`'s shared
732:   schema-hook glob now includes `prb/models/v1`, plus a new
733:   `specmgr-schema-prb-package` hook; `.github/workflows/ci.yml` gained
734:   the matching `docs/prb_schema.json` + packaged-copy check steps,
735:   mirroring the existing `tsk`/`qa` steps exactly.
736: - Added `tests/prb/tools/` (14 test modules mirroring `tests/tsk/tools/`
737:   file-for-file), `tests/prb/resources/` (3 test modules), and
738:   `tests/prb/prompts/` (2 test modules, ACC-006: asserting every
739:   narrated step/tool-call marker is present and, where sequence matters,
740:   in the correct relative order) -- 146 new tests, all green.
741: - Verified end to end, live (not just via tests): `create_prb` ->
742:   `update_prb` -> `set_status_prb` -> `get_prb` -> `list_prb` ->
743:   `delete_prb` (stub) against a real temp docs directory, plus
744:   `get_prb_example`/`get_prb_template` returning real, non-empty,
745:   parseable packaged markdown.
746: - Phase-end quality gate: `ruff format --check`/`ruff check` (both
747:   clean), `vulture src/ whitelist.py --min-confidence 60` (no findings
748:   -- no whitelist additions were needed), full `unittest` suite (1452
749:   tests, up from 1347, all green), `specmgr schema` (all five doc types,
750:   including `prb`, unchanged/drift-free), `specmgr docs` (regenerated
751:   `docs/api/`/`docs/GENERATED.md` with the new `prb` module docs),
752:   `specmgr mcp-docs` (regenerated `docs/MCP.md` with every new `prb`
753:   resource/tool/prompt).
754: - Next: Phase 4 (Cross-cutting registration) -- `AGENTS.md` update,
755:   final `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` drift
756:   re-check.
757: - Notes: No design decisions required beyond following the plan's Design
758:   Notes and the TSK/QA precedent files verbatim; one deliberate,
759:   in-scope deviation from a literal reading of Task 3.10 -- `prb_example.md`
760:   reuses `prb_reference.md`'s exact content (including its id) rather than
761:   a freshly drafted document, following QA's own precedent
762:   (`qa_example.md`/`qa_reference.md` share the same id and content too).
763: 
764: #### Update 2026-08-25 (Phase 2: Pydantic Models, Parser & Schema)
765: 
766: - Completed: Task 2.1 (`prb/models/v1/document.py::PrbDocument`, mirroring
767:   `TskDocument`/`QaDocument` exactly); Task 2.2
768:   (`prb/models/v1/parser.py::parse_prb`, mirroring `parse_tsk`/`parse_qa`'s
769:   frontmatter/body split via `python-frontmatter` and the same two-error-
770:   channel convention); Task 2.3 (`prb/models/v1/summary.py::PrbSummary`,
771:   subclassing `general/models/summary.py::DocSummary`); Task 2.4 (verified
772:   Phase 1's `body.py` already carries `Field(description=...)` on every
773:   scalar/optional field, matching REQ/TSK/QA precedent for
774:   schema-quality parity — no changes needed since Phase 1 already covered
775:   this; `frontmatter.py` deliberately has no `Field(description=...)`,
776:   matching `TskFrontmatter`/`QaFrontmatter`'s own precedent of relying on
777:   the class docstring instead); Task 2.5 (`generate_prb_schema()` added to
778:   `commands/schema.py`, registered as `"prb"` in `_GENERATORS`,
779:   `docs/prb_schema.json` generated via `uv run --frozen specmgr schema`
780:   — confirmed byte-identical/unchanged on a second run); Task 2.6
781:   (`tests/prb/models/v1/test_parser.py`, 9 tests: minimal doc, full
782:   reference-doc round-trip, defaults-when-absent, invalid status,
783:   3 missing-mandatory-section `AssertionError` cases (`Current State`,
784:   `Gap`, `Future State`, plus missing `Summary` within `Current State`),
785:   invalid-`type`-field `ValidationError`); Task 2.7 (phase-end quality
786:   gate — ruff format/check, vulture, full `unittest` suite (1347 tests, up
787:   from 1338, all green), `specmgr docs`/`specmgr mcp-docs` confirmed no
788:   unexpected drift beyond the new `prb` entries).
789: - Also added `SCHEMA_COMMENT_VERSION` via a new
790:   `prb/models/v1/_util.py`, mirroring `tsk/models/v1/_util.py` exactly,
791:   and re-exported it (plus `PrbDocument`/`parse_prb`/`PrbSummary`) from
792:   `prb/models/v1/__init__.py`.
793: - Next: Phase 3 (MCP Surface) — tools, resources, prompts, packaged data.
794: - Notes: No design decisions required beyond following the plan's Design
795:   Notes and the TSK/QA precedent files verbatim.
796: 
797: #### Update 2026-08-25 (Phase 1: Specification)
798: 
799: - Completed: Task 1.1 (`prb_reference.md`, exercising all 7 5W2H questions
800:   plus `Impact`/`References`/`More Information`); Task 1.2
801:   (`prb/models/v1/frontmatter.py::PrbFrontmatter`, 4-value status set);
802:   Task 1.3 (`prb/models/v1/body.py` — `Prb`, `CurrentState`,
803:   `Question1`..`Question7` with explicit regex `@alias`es matching the
804:   exact 5W2H wording, `Gap`/`FutureState`/`Impact`/`References`/
805:   `MoreInformation` leaves); Task 1.4 (`tests/prb/models/v1/`
806:   `test_frontmatter.py`/`test_body.py`, 32 tests total, covering each of
807:   the 7 questions and `Impact`/`References`/`More Information` both
808:   absent/present individually, plus the full reference document's
809:   round-trip); Task 1.5 (phase-end quality gate — ruff format/check,
810:   vulture, full `unittest` suite (1338 tests, all green),
811:   `prb_reference.md` confirmed `specmgr mdformat`-clean).
812: - Also created the supporting domain-package skeleton needed for the
813:   models to be importable ahead of Phase 3: `prb/__init__.py` (docstring
814:   only, no `prompts`/`resources`/`tools` imports yet — those don't exist
815:   until Phase 3 Task 3.16), `prb/models/__init__.py`,
816:   `prb/models/v1/__init__.py` (aggregating `PrbFrontmatter` + body
817:   classes; `PrbDocument`/`parse_prb`/`PrbSummary` are added in Phase 2).
818:   Added `current_state`/`gap`/`impact`/`future_state`/`summary`/
819:   `question_1`..`question_7` to `whitelist.py` (new Pydantic field names
820:   vulture cannot otherwise see as used).
821: - Next: Phase 2 (Pydantic Models, Parser & Schema) — `PrbDocument`,
822:   `parse_prb`, `PrbSummary`, `generate_prb_schema()`, parser tests.
823: - Notes: Followed the plan's Design Notes schema verbatim; no ambiguity
824:   encountered requiring a design decision beyond what's already logged.
825: 
826: #### Update 2026-08-25 (planning)
827: 
828: - Completed: Full design/planning discussion — schema shape (5W2H
829:   questions under `Current State`, `Gap`/`Impact`/`Future State`/
830:   `References`/`More Information`), status set, update mechanism, prompt
831:   behavior, and MCP surface all decided; this README written from that
832:   discussion. Also flagged (but explicitly did not fix, as out of scope
833:   here) that `AGENTS.md`'s TSK/QA `specmgr://<d>/list` bullets are stale
834:   post-`feat-13-list-paging` — added as `feat-7-various-improvements`
835:   Task 0.24 instead.
836: - Next: Phase 1 (Specification) — write `prb_reference.md`, define
837:   frontmatter/body models.
838: - Notes: No implementation attempted this session by design (planning-only
839:   session per explicit user instruction).
840: 
841: ### Decisions Made
842: 
843: - **2026-08-25**: Type abbreviation `prb`, domain-first layout
844:   (`prb/models/v1/`, `prb/tools/`, `prb/resources/`, `prb/prompts/`,
845:   `prb/data/`) — matches TSK/QA precedent (schema lives inside the domain
846:   package, not top-level `models/`), since PRB is a new domain built after
847:   the domain-first refactor.
848: - **2026-08-25**: 5W2H question set taken verbatim from the iSixSigma
849:   article (What/Why/Where/Who/When/How/How Often), each a fixed, optional
850:   H3 heading under a mandatory `## Current State` H2 with a mandatory
851:   `### Summary` leaf. Question heading wording is the plain question text
852:   (not numbered) — chosen over "Question N: ..." for readability.
853: - **2026-08-25**: Status set `draft`/`active`/`resolved`/`cancelled` —
854:   reuses TSK/QA's 4-value pattern/wording convention, with PRB-specific
855:   semantics.
856: - **2026-08-25**: `update_prb` is a single whole-body replace tool
857:   (REQ/TSK/QA convention), not an ADR-style `update_section`/option-style
858:   granular tool — the latter is currently ADR-specific code (ADR
859:   71fd95d7), and porting it was judged not worth the added scope for this
860:   feature. Individual questions/sections remain addressable by their fixed
861:   heading text within the whole-body markdown.
862: - **2026-08-25**: `References` is opaque free text for v1 (like

(Output capped at 50 KB. Showing lines 1-862. Use offset=863 to continue.)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 18.2s)

_Thinking:_

Got a solid understanding of the feat-16 structure. Next, since "goal" is similar to a requirement, let's look at the `req` domain structure. I'll check the following:
1. The REQ model (req/models/v1/)
2. The prb model for comparison
3. The structure of commands/schema.py
4. The structure of the req domain (tools, resources, prompts, data)

The user says: "A 'goal' is like a high-level business requirement. So it's similar in structure to a requirement. But it doesn't have the ISO25010 characteristics."

In other words, a Goal is like a Requirement, but it doesn't have the ISO25010 quality characteristics sections (Functional Suitability, Performance Efficiency, etc.). Let's take a look at the REQ schema to understand its structure.




Let me examine the `req` domain structure (since GOL will mirror it) and the shared infrastructure.




**Tool: bash**

**Input:**
```json
{
  "command": "find src/biz/dfch/specmgr/req src/biz/dfch/specmgr/prb -type f | sort && echo \"---\" && ls tests/req tests/prb 2>/dev/null"
}
```

**Output:**
```
src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
src/biz/dfch/specmgr/prb/data/prb_example.md
src/biz/dfch/specmgr/prb/data/prb_schema.json
src/biz/dfch/specmgr/prb/data/prb_template.md
src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
src/biz/dfch/specmgr/prb/__init__.py
src/biz/dfch/specmgr/prb/models/__init__.py
src/biz/dfch/specmgr/prb/models/v1/body.py
src/biz/dfch/specmgr/prb/models/v1/document.py
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py
src/biz/dfch/specmgr/prb/models/v1/__init__.py
src/biz/dfch/specmgr/prb/models/v1/parser.py
src/biz/dfch/specmgr/prb/models/v1/summary.py
src/biz/dfch/specmgr/prb/models/v1/_util.py
src/biz/dfch/specmgr/prb/prompts/create_prb.py
src/biz/dfch/specmgr/prb/prompts/__init__.py
src/biz/dfch/specmgr/prb/prompts/update_prb.py
src/biz/dfch/specmgr/prb/resources/__init__.py
src/biz/dfch/specmgr/prb/resources/prb_example.py
src/biz/dfch/specmgr/prb/resources/prb_schema.py
src/biz/dfch/specmgr/prb/resources/prb_template.py
src/biz/dfch/specmgr/prb/tools/create_prb.py
src/biz/dfch/specmgr/prb/tools/delete_prb.py
src/biz/dfch/specmgr/prb/tools/get_prb_example.py
src/biz/dfch/specmgr/prb/tools/get_prb.py
src/biz/dfch/specmgr/prb/tools/get_prb_template.py
src/biz/dfch/specmgr/prb/tools/__init__.py
src/biz/dfch/specmgr/prb/tools/_io.py
src/biz/dfch/specmgr/prb/tools/list_prb.py
src/biz/dfch/specmgr/prb/tools/_lock.py
src/biz/dfch/specmgr/prb/tools/parse_prb.py
src/biz/dfch/specmgr/prb/tools/_paths.py
src/biz/dfch/specmgr/prb/tools/set_status_prb.py
src/biz/dfch/specmgr/prb/tools/update_prb.py
src/biz/dfch/specmgr/prb/tools/validate_prb.py
src/biz/dfch/specmgr/prb/tools/_write.py
src/biz/dfch/specmgr/req/data/req_create_instructions.md
src/biz/dfch/specmgr/req/data/req_example.md
src/biz/dfch/specmgr/req/data/req_schema.json
src/biz/dfch/specmgr/req/data/req_template.md
src/biz/dfch/specmgr/req/data/req_update_instructions.md
src/biz/dfch/specmgr/req/__init__.py
src/biz/dfch/specmgr/req/models/v1/body.py
src/biz/dfch/specmgr/req/models/v1/document.py
src/biz/dfch/specmgr/req/models/v1/frontmatter.py
src/biz/dfch/specmgr/req/models/v1/__init__.py
src/biz/dfch/specmgr/req/models/v1/parser.py
src/biz/dfch/specmgr/req/models/v1/summary.py
src/biz/dfch/specmgr/req/models/v1/_util.py
src/biz/dfch/specmgr/req/prompts/create_req.py
src/biz/dfch/specmgr/req/prompts/__init__.py
src/biz/dfch/specmgr/req/prompts/update_req.py
src/biz/dfch/specmgr/req/resources/__init__.py
src/biz/dfch/specmgr/req/resources/req_example.py
src/biz/dfch/specmgr/req/resources/req_schema.py
src/biz/dfch/specmgr/req/resources/req_template.py
src/biz/dfch/specmgr/req/tools/create_req.py
src/biz/dfch/specmgr/req/tools/delete_req.py
src/biz/dfch/specmgr/req/tools/get_req_example.py
src/biz/dfch/specmgr/req/tools/get_req.py
src/biz/dfch/specmgr/req/tools/get_req_template.py
src/biz/dfch/specmgr/req/tools/__init__.py
src/biz/dfch/specmgr/req/tools/_io.py
src/biz/dfch/specmgr/req/tools/list_req.py
src/biz/dfch/specmgr/req/tools/_lock.py
src/biz/dfch/specmgr/req/tools/parse_req.py
src/biz/dfch/specmgr/req/tools/_paths.py
src/biz/dfch/specmgr/req/tools/set_status_req.py
src/biz/dfch/specmgr/req/tools/update_req.py
src/biz/dfch/specmgr/req/tools/validate_req.py
src/biz/dfch/specmgr/req/tools/_write.py
---
tests/prb:
__init__.py
models
prompts
resources
tools

tests/req:
__init__.py
models
prompts
resources
tools

```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/body.py"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/body.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Requirement (REQ) models: whole-section fields under a single H1.
19: 
20: Built on the generic `models.md` `MarkdownSectionN`/`MarkdownParagraph`/
21: `MarkdownListItem` engine: each class below models one markdown heading
22: (`## `/`### `) or list, and `Requirement` is the top-level H1 container.
23: """
24: 
25: import re
26: 
27: from pydantic import Field, field_validator
28: 
29: from ....models.md import (
30:     MarkdownSection1,
31:     MarkdownSection2,
32:     MarkdownSection2WithComment,
33:     MarkdownSection3,
34:     MarkdownParagraph,
35:     MarkdownListItem,
36:     MarkdownListItemWithNotes,
37:     MarkdownComment,
38:     alias,
39:     AliasType,
40: )
41: 
42: 
43: class Description(MarkdownSection2):
44:     """`## Description` -- free-form prose giving context/rationale for the
45:     requirement statement above it. Mandatory.
46:     """
47: 
48: 
49: class Characteristics(MarkdownSection2):
50:     """`## Characteristics` -- bullet list of ISO 25010:2023 quality attributes this
51:     requirement concerns ("Functional Suitability", "Performance", "User Interaction",
52:     "Compatibility", "Maintainability", "Security", "Reliability", "Safety").
53:     Mandatory. At least one characteristic.
54:     """
55: 
56:     items: list[MarkdownListItem] = Field(
57:         min_length=1,
58:         max_length=9,
59:         description="Bullet list of ISO 25010:2023 quality attributes; must contain at least one item.",
60:     )
61: 
62: 
63: _LEVEL_PATTERN = r"^(MUST|SHOULD|MUST NOT|SHOULD NOT|MAY)$"
64: 
65: 
66: class Level(MarkdownSection2WithComment):
67:     """`## Level` -- single-line value giving the requirement's obligation
68:     strength (e.g. "MUST"). Mandatory. May be preceded by an explanatory
69:     HTML comment (e.g. listing the allowed values).
70:     """
71: 
72:     comment: MarkdownComment | None = Field(
73:         default=None,
74:         description="Optional explanatory HTML comment (`<!-- ... -->`) preceding `value`, "
75:         "e.g. listing the allowed obligation-strength values.",
76:     )
77:     value: MarkdownParagraph = Field(
78:         description='Single-line value giving the requirement\'s obligation strength (e.g. "MUST").',
79:     )
80: 
81:     @field_validator("value")
82:     @classmethod
83:     def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
84:         """Enforce `_LEVEL_PATTERN` against `value.text`.
85: 
86:         `value` is a `MarkdownParagraph` (a model, not a `str`), so a
87:         `Field(pattern=...)` string constraint cannot be applied directly --
88:         pydantic only applies `pattern` to string-typed schemas. This
89:         validator re-implements the same check against `value.text`, the
90:         paragraph's own inline text.
91:         """
92:         if not re.fullmatch(_LEVEL_PATTERN, value.text):
93:             raise ValueError(f"value must match pattern {_LEVEL_PATTERN!r}, got {value.text!r}")
94:         return value
95: 
96: 
97: _PRIORITY_PATTERN = r"^(0|[1-9][0-9]?)$"  # 0-99, no leading zeros other than "0" itself
98: 
99: 
100: class Priority(MarkdownSection2WithComment):
101:     """`## Priority` -- single-line value giving the requirement's relative
102:     priority (e.g. a numeric rank). Optional. May be preceded by an
103:     explanatory HTML comment (e.g. describing the numeric range).
104:     """
105: 
106:     comment: MarkdownComment | None = Field(
107:         default=None,
108:         description="Optional explanatory HTML comment (`<!-- ... -->`) preceding `value`, "
109:         "e.g. describing the numeric range.",
110:     )
111:     value: MarkdownParagraph = Field(
112:         description=(
113:             "Single-line value giving the requirement's relative importance (0 to 99, lower number"
114:             " is more important, e.g. 50)."
115:         ),
116:     )
117: 
118:     @field_validator("value")
119:     @classmethod
120:     def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
121:         """Enforce `_PRIORITY_PATTERN` against `value.text`.
122: 
123:         `value` is a `MarkdownParagraph` (a model, not a `str`), so a
124:         `Field(pattern=...)` string constraint cannot be applied directly --
125:         pydantic only applies `pattern` to string-typed schemas. This
126:         validator re-implements the same check against `value.text`, the
127:         paragraph's own inline text.
128:         """
129:         if not re.fullmatch(_PRIORITY_PATTERN, value.text):
130:             raise ValueError(f"value must match pattern {_PRIORITY_PATTERN!r}, got {value.text!r}")
131:         return value
132: 
133: 
134: class Tags(MarkdownSection2):
135:     """`## Tags` -- bullet list of free-form labels for grouping/filtering
136:     requirements. Optional.
137:     """
138: 
139:     items: list[MarkdownListItemWithNotes] = Field(
140:         min_length=1,
141:         description="Bullet list of free-form labels for grouping/filtering requirements; "
142:         "must contain at least one item.",
143:     )
144: 
145: 
146: class Source(MarkdownSection2):
147:     """`## Source` -- single-line value naming the origin/authority of this
148:     requirement. Mandatory.
149:     """
150: 
151:     value: MarkdownParagraph = Field(description="Single-line value naming the origin/authority of this requirement.")
152: 
153: 
154: class Requirements(MarkdownSection3):
155:     """`### Requirements` under Related Artifacts -- bullet list of
156:     cross-references to other requirements, one per line
157:     (e.g. "REQ-9687: <title>").
158:     """
159: 
160:     items: list[MarkdownListItem] = Field(
161:         min_length=1,
162:         description="Bullet list of cross-references to other requirements, one per line "
163:         '(e.g. "REQ-9687: <title>"); must contain at least one item.',
164:     )
165: 
166: 
167: class Decisions(MarkdownSection3):
168:     """`### Decisions` under Related Artifacts -- bullet list of
169:     cross-references to decisions, one per line (e.g. "DEC-2703: <title>").
170:     """
171: 
172:     items: list[MarkdownListItem] = Field(
173:         min_length=1,
174:         description="Bullet list of cross-references to decisions, one per line "
175:         '(e.g. "DEC-2703: <title>"); must contain at least one item.',
176:     )
177: 
178: 
179: class AcceptanceCriteria(MarkdownSection3):
180:     """`### Acceptance Criteria` under Related Artifacts -- bullet list of
181:     cross-references to acceptance criteria, one per line
182:     (e.g. "ACC-1234: <title>").
183:     """
184: 
185:     items: list[MarkdownListItem] = Field(
186:         min_length=1,
187:         description="Bullet list of cross-references to acceptance criteria, one per line "
188:         '(e.g. "ACC-1234: <title>"); must contain at least one item.',
189:     )
190: 
191: 
192: class Goals(MarkdownSection3):
193:     """`### Goals` under Related Artifacts -- bullet list of
194:     cross-references to goals, one per line (e.g. "GOL-0007: <title>").
195:     """
196: 
197:     items: list[MarkdownListItem] = Field(
198:         min_length=1,
199:         description="Bullet list of cross-references to goals, one per line "
200:         '(e.g. "GOL-0007: <title>"); must contain at least one item.',
201:     )
202: 
203: 
204: class RelatedArtifacts(MarkdownSection2):
205:     """`## Related Artifacts` -- container for four independent, all-optional
206:     `### ` cross-reference lists (requirements/decisions/goals/acceptance
207:     criteria). Optional as a whole; no consistency check is enforced between
208:     the sub-lists.
209:     """
210: 
211:     requirements: Requirements | None = Field(default=None, description="`### Requirements` sub-section. Optional.")
212:     decisions: Decisions | None = Field(default=None, description="`### Decisions` sub-section. Optional.")
213:     goals: Goals | None = Field(default=None, description="`### Goals` sub-section. Optional.")
214:     acceptance_criteria: AcceptanceCriteria | None = Field(
215:         default=None, description="`### Acceptance Criteria` sub-section. Optional."
216:     )
217: 
218: 
219: class MoreInformation(MarkdownSection2):
220:     """`## More Information` -- free-form optional supplementary text, no
221:     fixed format. Optional.
222:     """
223: 
224: 
225: class Notes(MarkdownSection2):
226:     """`## Notes` -- free-form optional remarks (e.g. change history). Optional."""
227: 
228: 
229: @alias(value=".+", type=AliasType.REGEX)
230: class Requirement(MarkdownSection1):
231:     """The requirement body: a single H1 section with the fields below.
232: 
233:     The H1 heading text is free-form.
234: 
235:     Parameters
236:     ----------
237:     statement:
238:         The lead paragraph right after the H1. Mandatory.
239:     description:
240:         `## Description`. Optional.
241:     characteristics:
242:         `## Characteristics`. Mandatory.
243:     level:
244:         `## Level`. Mandatory.
245:     priority:
246:         `## Priority`. Optional.
247:     tags:
248:         `## Tags`. Optional.
249:     source:
250:         `## Source`. Mandatory.
251:     related_artifacts:
252:         `## Related Artifacts`. Optional.
253:     more_information:
254:         `## More Information`. Optional.
255:     notes:
256:         `## Notes`. Optional.
257:     """
258: 
259:     statement: MarkdownParagraph = Field(
260:         description="The lead paragraph directly under the H1, before any H2 section -- the "
261:         "requirement statement itself. Mandatory."
262:     )
263:     description: Description | None = Field(description="`## Description` section. Optional.")
264:     characteristics: Characteristics = Field(description="`## Characteristics` section. Mandatory.")
265:     level: Level = Field(description="`## Level` section. Mandatory.")
266:     priority: Priority | None = Field(default=None, description="`## Priority` section. Optional.")
267:     tags: Tags | None = Field(default=None, description="`## Tags` section. Optional.")
268:     source: Source = Field(description="`## Source` section. Mandatory.")
269:     related_artifacts: RelatedArtifacts | None = Field(
270:         default=None, description="`## Related Artifacts` section. Optional."
271:     )
272:     more_information: MoreInformation | None = Field(
273:         default=None, description="`## More Information` section. Optional."
274:     )
275:     notes: Notes | None = Field(default=None, description="`## Notes` section. Optional.")

(End of file - total 275 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 27.1s)

_Thinking:_

Now I understand the REQ body structure. The user says the following about Goal (GOL):
- It's like a high-level business requirement
- Similar in structure to a requirement
- But it does not have ISO25010 characteristics

Therefore the GOL body would be similar to REQ's body, minus the `Characteristics` section.

REQ body:
- H1 title (free-form)
- statement (required lead paragraph)
- description (optional)
- characteristics (required) — ISO 25010
- level (required)
- priority (optional)
- tags (optional)
- source (required)
- related_artifacts (optional) — contains sub-lists for requirements/decisions/goals/acceptance_criteria
- more_information (optional)
- notes (optional)

For GOL, I'd probably propose:
- H1 title
- statement (required lead paragraph)
- description (optional)
- level (required?) — for a goal, maybe "MUST/SHOULD/MAY" still applies, or perhaps something else
- priority (optional)
- tags (optional)
- source (required?)
- related_artifacts (optional) — interestingly, REQ's RelatedArtifacts already has a `Goals` sub-list! In other words, the cross-reference from REQ to GOL already exists.
- more_information (optional)
- notes (optional)

Note: REQ's RelatedArtifacts already has a `Goals` section (`### Goals` — cross-reference to goals, e.g., "GOL-0007: <title>"). This suggests the concept of GOL is already anticipated in REQ's schema.

Let's look at REQ's example and template data files to understand the document structure in its actual form, and check the frontmatter, document, parser, summary, _util files. Also, I'll check commands/schema.py for the registry, and req/tools for the naming conventions.

Furthermore, let's check feat-6-requirement-artifact's README to see how the REQ feature was planned (since GOL is similar to REQ). Actually, what the user is explicitly asking for is a feature folder with the same structure as feat-16. The key thing is the plan in feat-16's README.

Let's read the remaining req model files and data files.




Now let me look at the REQ frontmatter, example/template data, and the schema registry to understand the full picture.





**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/frontmatter.py"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/frontmatter.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Requirement frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
19: 
20: Mirrors the pattern established by `uc/models/v2/frontmatter.py::UcFrontmatter`:
21: subtype of `MarkdownFrontmatter` that restricts `type` to a fixed ``Literal["req"]``
22: and narrows the free-form ``status`` to an appropriate closed vocabulary for requirements.
23: """
24: 
25: from __future__ import annotations
26: 
27: from typing import Literal
28: 
29: from pydantic import field_validator
30: 
31: from biz.dfch.specmgr.models.md import MarkdownFrontmatter
32: 
33: #: Fixed, closed set of accepted ``status`` values for requirements -- ADR's six plus
34: #: ``"implemented"``, since requirements track implementation beyond acceptance.
35: _ALLOWED_STATUSES = frozenset(
36:     {
37:         "draft",
38:         "proposed",
39:         "accepted",
40:         "superseded",
41:         "deprecated",
42:         "rejected",
43:         "implemented",
44:     }
45: )
46: 
47: 
48: class ReqFrontmatter(MarkdownFrontmatter):
49:     """Requirement frontmatter: `MarkdownFrontmatter` narrowed for the ``req`` document type.
50: 
51:     Parameters
52:     ----------
53:     type:
54:         Fixed discriminator, always ``"req"``. Narrows the base's mandatory,
55:         default-less ``str`` field to a ``Literal["req"] = "req"``, so a document
56:         omitting ``type`` entirely still parses as a requirement document.
57:     status:
58:         One of ``"draft"``, ``"proposed"``, ``"accepted"``, ``"superseded"``,
59:         ``"deprecated"``, ``"rejected"``, ``"implemented"``. Narrows the base's
60:         free-form ``str = "draft"`` default to this closed seven-value set.
61:         Blank/absent still defaults to ``"draft"`` (inherited from the base's
62:         ``_default_blank_status_to_draft`` validator, which runs before this one).
63:     version:
64:         The ``models.md`` schema major.minor.patch version this document's
65:         frontmatter was written with. DO NOT CHANGE!
66: 
67:     All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
68:     unchanged from :class:`MarkdownFrontmatter`.
69:     """
70: 
71:     type: Literal["req"] = "req"  # type: ignore
72: 
73:     @field_validator("status")
74:     @classmethod
75:     def _validate_status(cls, value: str) -> str:
76:         if value not in _ALLOWED_STATUSES:
77:             raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
78:         return value

(End of file - total 78 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_example.md"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_example.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-05 08:15:42
3: id: deaddead-dead-dead-dead-deaddeaddead
4: status: draft
5: type: req
6: updated: 2026-08-06 03:27:27
7: version: 1.0.0
8: ---
9: 
10: # Maximum Engine Temperature
11: 
12: WHILE the engine is running, THE temperature must be a maximum of 80 °C.
13: 
14: ## Description
15: 
16: If the engine becomes too hot, the lifetime of the system decreases.
17: 
18: ## Characteristics
19: 
20: 1. Safety
21: 2. Reliability
22: 
23: ## Level
24: 
25: MUST
26: 
27: ## Priority
28: 
29: 50
30: 
31: ## Tags
32: 
33: - Combustion Engines
34: - Vehicles
35: 
36: ## Source
37: 
38: The International Safety Board Association (TISBA)
39: 
40: ## Related Artifacts
41: 
42: ### Requirements
43: 
44: - REQ-9687: Maximum temperatures of running engines in civil vehicles
45: 
46: ### Decisions
47: 
48: - DEC-2703: Usage of metal conductors in moving engine parts
49: 
50: ### Goals
51: 
52: - GOL-0007: Competitive Engines in Consumer Vehicles
53: 
54: ### Acceptance Criteria
55: 
56: - ACC-1234: Temperature Measurements on running combustion engines
57: 
58: ## More Information
59: 
60: This optional section can contain additional information. There is no defined format for this section.
61: 
62: ## Notes
63: 
64: This optional section can contain additional notes. Example: changes to the requirement.

(End of file - total 64 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_template.md"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_template.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-05 08:15:42
3: id: deaddead-dead-dead-dead-deaddeaddead
4: status: draft
5: type: req
6: updated: 2026-08-06 03:27:27
7: version: 1.0.0
8: ---
9: 
10: # Level 1 Heading is the Title of the Requirement
11: 
12: This is the requirement statement. Write it formal and concise and use ASD-STE100 writing style.
13: 
14: ## Description
15: 
16: This is a description of the requirement statement that gives more context. Use only if necessary.
17: 
18: ## Characteristics
19: 
20: 1. A numbered list with ISO 25010:2023 main characteristics
21: 2. Must have at least one characteristic
22: 
23: ## Level
24: 
25: <!-- RFC 2119 Requirement Keyword. Mandatory. -->
26: MUST
27: 
28: ## Priority
29: 
30: <!-- A number between 0 and 99. Lower number is higher priority. -->
31: 50
32: 
33: ## Tags
34: 
35: - An optional bullet list
36: - This can contain tag of different domains
37: 
38: ## Source
39: 
40: Where does this requirement come from? This can be a document reference, an interest group or something else. Mandatory.
41: 
42: ## Related Artifacts
43: 
44: ### Requirements
45: 
46: - A bullet list with related requirements. Optional.
47: 
48: ### Decisions
49: 
50: - A bullet list with related decisions. Optional.
51: 
52: ### Goals
53: 
54: - A bullet list with related goals. Optional.
55: 
56: ### Acceptance Criteria
57: 
58: - A bullet list with related acceptance criteria. Optional.
59: 
60: ## More Information
61: 
62: This optional section can contain additional information. There is no defined format for this section.
63: 
64: ## Notes
65: 
66: This optional section can contain additional notes. There is no defined format for this section.

(End of file - total 66 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 28.2s)

_Thinking:_

Now I understand the REQ structure. REQ's "Related Artifacts" already has a "### Goals" sub-list, which references "GOL-0007: Competitive Engines in Consumer Vehicles". In other words, the concept of Goal already exists as a cross-reference within REQ.

Next things to check:
1. `commands/schema.py` — the registry of document type generators
2. `req/tools/list_req.py` and `req/tools/create_req.py` for the naming conventions
3. `prb/data/prb_reference.md` and `prb_example.md`
4. Look at feat-6-requirement-artifact's README for context (optional)
5. Check the docstring of `server.py`
6. Check the domain-first ADR for the structure

Also, an important issue: GOL is "similar to the structure of a requirement, but does not have ISO25010 characteristics". So the GOL body would be REQ's body minus `Characteristics`.

Design questions that need to be resolved with the user:
1. Which sections should GOL have? Probably: H1 title, statement, description (optional), level (required?), priority (optional), tags (optional), source (required?), related_artifacts (optional), more_information (optional), notes (optional). No `characteristics`.
2. What should the status set be? REQ has a 7-value set (draft/proposed/accepted/superseded/deprecated/rejected/implemented). PRB/TSK/QA have a 4-value set (draft/active/resolved/cancelled). For a goal (a high-level business requirement), REQ's 7-value set might be appropriate, or a simpler 4-value set might work too.
3. What should GOL's Related Artifacts be? REQ has sub-lists for Requirements/Decisions/Goals/Acceptance Criteria. For GOL, probably Requirements/Decisions/Acceptance Criteria (excluding Goals itself? Or maybe include them?). Hmm.
4. Prompt: create_gol/update_gol following the same format as req/prb.
5. Naming: abbreviation is `gol` (the user explicitly wrote "Goal" (GOL)).

Let me check the remaining infrastructure: commands/schema.py, the server.py docstring, the req tools for the exact naming pattern.




Let me check the schema registry, server.py registration, and a couple of req tool modules for exact conventions.




**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"GENERATORS\\|def generate_\\|add_parser\\|choices\" src/biz/dfch/specmgr/commands/schema.py | head -40 && echo \"=== server.py tail ===\" && tail -20 src/biz/dfch/specmgr/server.py && echo \"=== pyproject package data ===\" && grep -n \"package-data\\|prb\\|req\" pyproject.toml | head -20"
}
```

**Output:**
```
22:``_GENERATORS`` below, keyed by its short doc-type name (``"req"``, ``"uc"``).
64:def generate_req_schema() -> str:
90:def generate_qa_schema() -> str:
108:def generate_uc_schema() -> str:
126:def generate_tsk_schema() -> str:
144:def generate_prb_schema() -> str:
165:_GENERATORS: dict[str, Callable[[], str]] = {
179:            help=f"Restrict generation to one registered doc type ({', '.join(sorted(_GENERATORS))}). "
201:    if type_ is not None and type_ not in _GENERATORS:
202:        valid = ", ".join(sorted(_GENERATORS))
206:    selected = {type_: _GENERATORS[type_]} if type_ is not None else dict(_GENERATORS)
=== server.py tail ===
async def _lifespan(_server: MCPServer) -> AsyncGenerator[None, None]:
    """Placeholder lifespan: no shared state to initialise yet."""
    yield


mcp = MCPServer(
    name="specmgr",
    instructions="An artifact manager for system specifications.",
    lifespan=_lifespan,
)

# ---------------------------------------------------------------------------
# Resource/tool/prompt registration (side-effect: registers everything on
# mcp). Every domain package here (including the cross-cutting `general`
# package, which in turn imports its own `resources`/`tools` sub-packages)
# must be imported for its @mcp.tool()/@mcp.prompt()/@mcp.resource()
# decorators to actually run.
# ---------------------------------------------------------------------------

from . import adr, general, prb, qa, req, tsk, uc  # noqa: E402, F401
=== pyproject package data ===
2:requires = ["setuptools>=81.0"]
10:requires-python = ">=3.11"
23:  "requirements",
24:  "requirements management",
110:include-package-data = true
116:[tool.setuptools.package-data]
123:"biz.dfch.specmgr.prb" = [
131:"biz.dfch.specmgr.req" = [

```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/list_req.py"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/list_req.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: list_req (feat-13-list-paging Task 2.2).
19: 
20: Replaces the earlier ``specmgr://req/list`` resource
21: (``req.resources.req_list``). Converted from a resource to a tool because
22: MCP resources cannot take arbitrary parameters (only URI-template path
23: segments), and ``max_results``/``offset`` paging needs exactly that -- the
24: same resource->tool reasoning already applied to ``get_req``
25: (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Deliberately unfiltered --
26: characteristics/tags filtering (feat-7 Task 0.16) was explicitly deferred
27: during Task 3.9's design discussion and stays out of scope here too. See
28: ``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
29: contract shared by every ``list_<domain>`` tool.
30: """
31: 
32: from __future__ import annotations
33: 
34: from pydantic import ValidationError
35: 
36: from ...general.models import PagedResult
37: from ...general.tools._paging import normalize_paging, paginate
38: from ...server import mcp
39: from ..models.v1 import ReqSummary
40: from ._io import read_req
41: from ._paths import iter_req_paths
42: 
43: 
44: @mcp.tool(
45:     name="list_req",
46:     title="List requirements",
47:     description=(
48:         "Ids, titles, statuses, and refs of requirements in the configured requirement base "
49:         "directory, one page at a time, for context before addressing one by id. "
50:         "'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- "
51:         "for documents that have no assigned id; use it with the get_req tool instead. "
52:         "max_results/offset control paging (default page size 25, capped at 100); "
53:         "out-of-range values are clamped, not errored."
54:     ),
55: )
56: def list_req(max_results: int | None = None, offset: int | None = None) -> PagedResult[ReqSummary]:
57:     """Return one page of one-line requirement summaries from the configured base directory.
58: 
59:     A file that fails to parse (``AssertionError`` or
60:     ``pydantic.ValidationError`` -- the same two error channels
61:     :func:`~biz.dfch.specmgr.req.models.v1.parse_req` raises) is silently
62:     skipped -- a single malformed file must not break listing every other
63:     valid one (mirrors ``req.tools._paths.find_req_path``'s own
64:     skip-on-parse-failure rule). The complete, skip-broken-file-filtered
65:     list is materialized first, then paginated in memory, so the returned
66:     ``total`` always reflects the count of parseable documents only,
67:     independent of paging.
68: 
69:     Parameters
70:     ----------
71:     max_results:
72:         Maximum number of summaries to return in this page. Defaults to
73:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
74:         otherwise clamped into range (see
75:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
76:     offset:
77:         Zero-based index of the first summary to include in this page.
78:         Defaults to ``0`` when not given (``None``); negative values are
79:         floored to ``0``.
80: 
81:     Returns
82:     -------
83:     PagedResult[ReqSummary]
84:         One entry per successfully-parsed ``*.md`` file within the
85:         requested page, in filename-sorted order. ``results`` is empty if
86:         the base directory does not exist, holds no requirements, or
87:         ``offset`` is past the end of the full list.
88:     """
89:     summaries: list[ReqSummary] = []
90:     for path in iter_req_paths():
91:         try:
92:             doc = read_req(path)
93:         except (AssertionError, ValidationError):
94:             continue
95:         summaries.append(
96:             ReqSummary(
97:                 id=doc.frontmatter.id,
98:                 title=doc.body.text,
99:                 status=doc.frontmatter.status,
100:                 ref=path.stem,
101:             )
102:         )
103:     return paginate(summaries, *normalize_paging(max_results, offset))

(End of file - total 103 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 18.0s)

_Thinking:_

Now I've got the overall picture. Let me check a few more things:

1. `_doc_paths.py` in `general/tools` — to understand how the base directory is configured (environment variable like `SPECMGR_REQ_DIR`?)
2. req's prompts (create_req instructions) — to confirm whether it uses `string.Template`
3. The structure of feat-6-requirement-artifact's README (how the REQ feature planned phases) — optional but useful
4. The "Still genuinely missing" section of AGENTS.md — GOL would be added there

Let me check `_doc_paths.py` and req's prompts.




Let me check the doc-path configuration and the req prompt instructions to complete my understanding.




**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Generic, doc-type-agnostic base directory resolution, filename slugification,
19: and id -> path lookup (plan Task 3.10).
20: 
21: Generalizes ``adr.tools._paths``'s shape into a single module shared across
22: document domains (REQ now, UC later) instead of a copy per domain: one root
23: env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
24: every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
25: for ``type_name="req"``).
26: 
27: **ADR is deliberately left untouched** -- it keeps its own
28: ``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
29: Migrating ADR onto this shared module is optional future cleanup, not
30: bundled into this change.
31: 
32: As with ``adr.tools._paths``, this module has no ``mcp``/file-write
33: dependency beyond read-only directory listing: :func:`doc_base_dir` never
34: creates the directory (a read-only tool shouldn't have that side effect),
35: only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
36: id -> path cache either -- every lookup re-scans the base directory and
37: re-parses each file, matching this codebase's "the on-disk file is the sole
38: source of truth" design.
39: """
40: 
41: from __future__ import annotations
42: 
43: import os
44: import re
45: from collections.abc import Callable, Iterator
46: from pathlib import Path
47: from typing import TypeVar
48: 
49: __all__ = [
50:     "DEFAULT_DOCS_ROOT",
51:     "DOCS_DIR_ENV_VAR",
52:     "DocNotFoundError",
53:     "doc_base_dir",
54:     "ensure_doc_base_dir",
55:     "find_doc_path_by_id",
56:     "iter_doc_paths",
57:     "slugify",
58: ]
59: 
60: #: Environment variable that overrides the shared documents root directory.
61: DOCS_DIR_ENV_VAR = "SPECMGR_DOCS_DIR"
62: 
63: #: Default documents root directory, relative to the current working directory.
64: DEFAULT_DOCS_ROOT = Path("docs")
65: 
66: #: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.
67: _NON_ALNUM_RUN_PATTERN = re.compile(r"[^a-z0-9]+")
68: 
69: #: Maximum length of a slugified title (mirrors ``adr.tools._paths``'s filename scheme).
70: _SLUG_MAX_LENGTH = 60
71: 
72: #: Fallback slug used when a title has no alphanumeric characters at all.
73: _FALLBACK_SLUG = "doc"
74: 
75: #: Parsed-document type returned by a caller-supplied ``parse_fn``.
76: _DocT = TypeVar("_DocT")
77: 
78: 
79: class DocNotFoundError(LookupError):
80:     """No document file found matching the given id, under a given base directory."""
81: 
82: 
83: def _docs_root() -> Path:
84:     """Return the configured documents root directory, without creating it."""
85:     value = os.environ.get(DOCS_DIR_ENV_VAR)
86:     result = Path(value) if value else DEFAULT_DOCS_ROOT
87:     return result
88: 
89: 
90: def doc_base_dir(type_name: str) -> Path:
91:     """Return the base directory for ``type_name`` documents, without creating it.
92: 
93:     Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
94:     :data:`DEFAULT_DOCS_ROOT`, then appends ``type_name`` as a subdirectory
95:     (e.g. ``docs/req`` for ``type_name="req"``). Read-only tools/resources
96:     use this so merely reading never has the side effect of creating the
97:     directory -- see :func:`ensure_doc_base_dir` for the write path.
98: 
99:     Parameters
100:     ----------
101:     type_name:
102:         The document type's subdirectory name, e.g. ``"req"``.
103: 
104:     Returns
105:     -------
106:     Path
107:         The resolved base directory for ``type_name`` documents.
108:     """
109:     assert isinstance(type_name, str), type(type_name)
110:     assert type_name.strip()
111: 
112:     result = _docs_root() / type_name
113:     return result
114: 
115: 
116: def ensure_doc_base_dir(type_name: str) -> Path:
117:     """Return the base directory for ``type_name`` documents, creating it if missing.
118: 
119:     Only a doc type's ``create_*`` tool should call this -- every other
120:     tool/resource uses the read-only :func:`doc_base_dir` instead.
121: 
122:     Parameters
123:     ----------
124:     type_name:
125:         The document type's subdirectory name, e.g. ``"req"``.
126: 
127:     Returns
128:     -------
129:     Path
130:         The resolved, now-guaranteed-to-exist base directory for
131:         ``type_name`` documents.
132:     """
133:     assert isinstance(type_name, str), type(type_name)
134:     assert type_name.strip()
135: 
136:     result = doc_base_dir(type_name)
137:     result.mkdir(parents=True, exist_ok=True)
138:     return result
139: 
140: 
141: def slugify(title: str) -> str:
142:     """Derive a filename-safe slug from a document title.
143: 
144:     Ported from ``adr.tools._paths.slugify`` unchanged: lowercases
145:     ``title``, collapses every run of non-``[a-z0-9]`` characters into a
146:     single ``-``, strips leading/trailing ``-``, truncates to
147:     :data:`_SLUG_MAX_LENGTH` characters (stripping a trailing ``-`` again in
148:     case the truncation lands mid-run), and falls back to
149:     :data:`_FALLBACK_SLUG` if the result would otherwise be empty (e.g. a
150:     title with no alphanumeric characters at all).
151: 
152:     Parameters
153:     ----------
154:     title:
155:         The document title to slugify.
156: 
157:     Returns
158:     -------
159:     str
160:         The filename-safe slug.
161:     """
162:     assert isinstance(title, str), type(title)
163: 
164:     slug = _NON_ALNUM_RUN_PATTERN.sub("-", title.lower()).strip("-")
165:     slug = slug[:_SLUG_MAX_LENGTH].strip("-")
166:     result = slug or _FALLBACK_SLUG
167:     return result
168: 
169: 
170: def iter_doc_paths(base_dir: Path) -> Iterator[Path]:
171:     """Yield every ``*.md`` file directly under ``base_dir``, sorted by name.
172: 
173:     Yields nothing (rather than raising) if ``base_dir`` does not exist.
174: 
175:     Parameters
176:     ----------
177:     base_dir:
178:         The directory to scan for ``*.md`` files.
179: 
180:     Returns
181:     -------
182:     Iterator[Path]
183:         An iterator over the matching, sorted paths.
184:     """
185:     assert isinstance(base_dir, Path), type(base_dir)
186: 
187:     if not base_dir.exists():
188:         return iter(())
189:     result = iter(sorted(base_dir.glob("*.md")))
190:     return result
191: 
192: 
193: def find_doc_path_by_id(
194:     base_dir: Path,
195:     id_: str,
196:     parse_fn: Callable[[str], _DocT],
197:     get_id_fn: Callable[[_DocT], str | None],
198: ) -> Path:
199:     """Resolve an ``id`` to its on-disk file path, for any doc type.
200: 
201:     Scans every ``*.md`` file under ``base_dir``, parsing each via
202:     ``parse_fn`` and comparing ``get_id_fn(parsed)`` against ``id_``. A file
203:     that fails to parse (``AssertionError`` or ``ValueError``, which
204:     ``pydantic.ValidationError`` and every parser-specific error in this
205:     codebase -- e.g. ``AdrParseError`` -- subclass) is silently skipped --
206:     one broken file must not prevent lookup of a different, valid id.
207: 
208:     Parameters
209:     ----------
210:     base_dir:
211:         The directory to scan for ``*.md`` files.
212:     id_:
213:         The id to look up.
214:     parse_fn:
215:         Parses a file's full text into a document object (e.g. ``parse_adr``,
216:         ``parse_req``).
217:     get_id_fn:
218:         Extracts the id (or ``None``) from a parsed document object (e.g.
219:         ``lambda doc: doc.frontmatter.id``).
220: 
221:     Returns
222:     -------
223:     Path
224:         The resolved file path.
225: 
226:     Raises
227:     ------
228:     DocNotFoundError
229:         If no file's parsed id matches ``id_``.
230:     """
231:     assert isinstance(base_dir, Path), type(base_dir)
232:     assert isinstance(id_, str), type(id_)
233:     assert id_.strip()
234: 
235:     for path in iter_doc_paths(base_dir):
236:         try:
237:             doc = parse_fn(path.read_text(encoding="utf-8"))
238:         except (AssertionError, ValueError):
239:             continue
240:         if get_id_fn(doc) == id_:
241:             return path
242:     raise DocNotFoundError(
243:         f"no document found with id {id_!r} under {base_dir}. The id must be the bare document UUID, without "
244:         f"a domain prefix."
245:     )

(End of file - total 245 lines)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/create_req.py"
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/create_req.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.prompt()``: create_req (Task 3.19).
19: 
20: Returns instructional text -- not itself a tool call -- that guides an LLM
21: through drafting a brand-new Requirement (REQ) document using the existing
22: ``req/tools/``/``req/resources/`` surface (``list_req``,
23: ``specmgr://req/template``/``specmgr://req/example``, ``specmgr://req/schema``,
24: ``create_req``, ``validate_req``).
25: 
26: Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
27: parameters to pre-fill: ``create_req`` builds the entire REQ frontmatter
28: itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
29: the caller only ever supplies body markdown.
30: 
31: Naming note: this prompt is named ``create_req``, the same name as the
32: ``@mcp.tool()`` in ``req/tools/create_req.py``. This is not a collision --
33: the MCP protocol keeps prompts and tools in separate registries
34: (``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
35: so the two are not mistaken for the same registration.
36: 
37: The actual instructional text lives in its own packaged data file,
38: ``req/data/req_create_instructions.md``, read fresh on every call via
39: ``general.tools._packaged_data.read_packaged_text``, rather than as an
40: inline Python string constant. Placeholders use ``string.Template``
41: (``$topic``), not ``str.format``, precisely so the instructions file
42: itself is free to use plain, unescaped ``{...}`` braces for the REQ
43: markdown headings it narrates to the LLM (e.g. ``# {title}``) without
44: those colliding with this module's own substitution.
45: """
46: 
47: from __future__ import annotations
48: 
49: from string import Template
50: 
51: from ...general.tools._packaged_data import read_packaged_text
52: from ...server import mcp
53: 
54: 
55: @mcp.prompt(
56:     name="create_req",
57:     title="Create a requirement",
58:     description=(
59:         "Guides the LLM through checking for an existing similar requirement, gathering the "
60:         "required information, and driving create_req/validate_req to author a new REQ document."
61:     ),
62: )
63: def create_req(topic: str) -> str:
64:     """Return instructional text for drafting a new requirement about ``topic``.
65: 
66:     Parameters
67:     ----------
68:     topic:
69:         Free-text description of the requirement to be drafted -- becomes
70:         the seed for the document's title and requirement statement.
71: 
72:     Returns
73:     -------
74:     str
75:         Instructional text (auto-wrapped as a single ``UserMessage`` by
76:         the MCP SDK), not itself a tool call.
77:     """
78:     template = Template(read_packaged_text("req", "create_instructions", "md"))
79:     return template.substitute(topic=topic)

(End of file - total 79 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 35.9s)

_Thinking:_

With this, I've got a comprehensive understanding of the codebase. Next, let me quickly check the following as well:
1. The structure of feat-6 (requirement artifact) — probably not needed, feat-16 is the reference.
2. Check the "missing" list in AGENTS.md and see what needs to be updated.
3. Check the hooks related to the schema in `.pre-commit-config.yaml` to understand what GOL needs.
4. Check the `docs/` structure for the schema files.

Actually, I have enough info about the pre-commit configuration from feat-16's plan: "expand the shared schema-hook glob to include `prb/models/v1`, and add a `specmgr-schema-prb-package` hook." Let me quickly verify the current state of the pre-commit configuration.

Also, one important design question: the user said goal is "something like a high-level business requirement" and is "similar in structure to a requirement, but without ISO25010 characteristics." So the GOL body would look like:

```
Goal(MarkdownSection1)  # H1 free-form title
├── statement: MarkdownParagraph        # required lead paragraph
├── description: Description | None     # optional
├── level: Level | None?                # required?
├── priority: Priority | None           # optional
├── tags: Tags | None                   # optional
├── source: Source | None?              # required?
├── related_artifacts: RelatedArtifacts | None  # optional
├── more_information: MoreInformation | None    # optional
└── notes: Notes | None                     # optional
```

Questions to resolve with the user:
1. **Section set**: Should GOL be REQ minus Characteristics (i.e. keep statement, description, level, priority, tags, source, related_artifacts, more_information, notes)? Or a smaller set? The user said "similar in structure to a requirement, but without ISO25010 characteristics" — so probably REQ minus Characteristics. But should `Level` (MUST/SHOULD) be kept? For a high-level business goal, "Level" might not make much sense. Hmm. Also `Source`? These are design decisions I should confirm with the user.

2. **Status set**: REQ uses 7 values (draft/proposed/accepted/superseded/deprecated/rejected/implemented); TSK/QA/PRB use 4 values (draft/active/resolved/cancelled). For a goal (business level, long-term), which set? Maybe draft/active/achieved/cancelled? Or reuse REQ's? I need to ask the user.

3. **Related Artifacts sub-lists for GOL**: REQ's RelatedArtifacts has Requirements/Decisions/Goals/Acceptance Criteria. For GOL, probably Requirements/Decisions/Acceptance Criteria (no self-referencing Goals). Or keep all four? Probably exclude Goals, or replace with "Requirements" (the requirements that realize this goal). I need to ask the user.

4. **Feature number**: The next feature folder will be `feat-17-goal-artifact` (feat-16 is the latest; feat-13, 14, 16 are in between… actual folders are: feat-0? No, there's no feat-0. Folders: 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16. So next is 17). Note: feat-16's status indicates it used "feat-16" as a placeholder for the GitHub issue number. So I'd use `feat-17-goal-artifact` — wait, the user said "Goal" (GOL). The slug would probably be `feat-17-goal`.

5. **Prompts**: create_gol/update_gol following the same shape as req (narration-type instructions using packaged data files).

Let me quickly check the pre-commit configuration and the docs directory for the schema files.




Let me check the pre-commit config and docs layout for the schema-file conventions.



**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"specmgr-schema\\|models/v\" .pre-commit-config.yaml | head -30 && echo \"=== docs ===\" && ls docs/*.json docs/ | head -30 && echo \"=== ci schema checks ===\" && grep -n \"schema\" .github/workflows/ci.yml | head -30"
}
```

**Output:**
```
82:      - id: specmgr-schema
94:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
96:      - id: specmgr-schema-req-package
104:          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
106:          independent hook (not chained into `specmgr-schema`) so each artifact's
111:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
113:      - id: specmgr-schema-uc-package
121:          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
123:          independent hook (not chained into `specmgr-schema`) so each artifact's
128:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
130:      - id: specmgr-schema-tsk-package
138:          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
140:          independent hook (not chained into `specmgr-schema`) so each artifact's
145:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
147:      - id: specmgr-schema-qa-package
155:          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
157:          independent hook (not chained into `specmgr-schema`) so each artifact's
162:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
164:      - id: specmgr-schema-prb-package
172:          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
174:          independent hook (not chained into `specmgr-schema`) so each artifact's
179:        files: ^src/biz/dfch/specmgr/(prb/models/v1|qa/models/v2|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
=== docs ===
docs/prb_schema.json
docs/qa_schema.json
docs/req_schema.json
docs/tsk_schema.json
docs/uc_schema.json

docs/:
adr
api
coverage.svg
GENERATED.md
MCP.md
prb_schema.json
qa_schema.json
req_schema.json
tsk
tsk_schema.json
uc_schema.json
=== ci schema checks ===
88:    - name: Make sure `docs/req_schema.json` is correct
89:      # `specmgr schema` itself exits 1 when the regenerated content differs from what
95:        uv run --frozen --all-extras --python 3.13.13 specmgr schema || {
96:          echo "::error::docs/req_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema' and commit the result (see AGENTS.md)."
100:    - name: Make sure `src/biz/dfch/specmgr/req/data/req_schema.json` is correct
101:      # Packaged copy of the same schema, read by the `specmgr://req/schema` MCP resource
106:        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data || {
107:          echo "::error::src/biz/dfch/specmgr/req/data/req_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data' and commit the result (see AGENTS.md)."
111:    - name: Make sure `docs/uc_schema.json` is correct
112:      # `specmgr schema` itself exits 1 when the regenerated content differs from what
118:        uv run --frozen --all-extras --python 3.13.13 specmgr schema || {
119:          echo "::error::docs/uc_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema' and commit the result (see AGENTS.md)."
123:    - name: Make sure `src/biz/dfch/specmgr/uc/data/uc_schema.json` is correct
124:      # Packaged copy of the same schema, read by the `specmgr://uc/schema` MCP resource
129:        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data || {
130:          echo "::error::src/biz/dfch/specmgr/uc/data/uc_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data' and commit the result (see AGENTS.md)."
134:    - name: Make sure `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` is correct
135:      # Packaged copy of the same schema, read by the `specmgr://tsk/schema` MCP resource
137:      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
140:        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data || {
141:          echo "::error::src/biz/dfch/specmgr/tsk/data/tsk_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data' and commit the result (see AGENTS.md)."
145:    - name: Make sure `docs/qa_schema.json` is correct
146:      # `specmgr schema` itself exits 1 when the regenerated content differs from what
152:        uv run --frozen --all-extras --python 3.13.13 specmgr schema || {
153:          echo "::error::docs/qa_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema' and commit the result (see AGENTS.md)."
157:    - name: Make sure `src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct
158:      # Packaged copy of the same schema, read by the `specmgr://qa/schema` MCP resource
160:      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
163:        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data || {
164:          echo "::error::src/biz/dfch/specmgr/qa/data/qa_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data' and commit the result (see AGENTS.md)."

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 177.1s)

_Thinking:_

Now I have a full picture of the required infrastructure. Time to draw up the plan and ask the user some confirmation questions about design decisions.

Key design questions for the user:

1. **GOL body structure** — user says "similar structure to a requirement. But no ISO25010 characteristics." So the baseline is REQ minus `Characteristics`. But some REQ sections may not make sense for high-level business goals:
   - `statement` (required lead paragraph) — keep
   - `description` (optional) — keep
   - `level` (MUST/SHOULD/MAY, RFC 2119) — questionable for a business goal? Or keep?
   - `priority` (optional) — keep?
   - `tags` (optional) — keep?
   - `source` (required) — keep? For a business goal, "source" (who/what it came from) makes sense.
   - `related_artifacts` — keep, but what sub-lists?
   - `more_information`, `notes` — keep
   
   Simplest interpretation: GOL = REQ minus `Characteristics`, everything else identical. I should confirm whether to keep `Level` and `Source` as required, or whether to make them optional for goals.

2. **Status set** — REQ's 7 values (draft/proposed/accepted/superseded/deprecated/rejected/implemented) vs TSK/QA/PRB's 4 values (draft/active/resolved/cancelled). For a business goal, what fits? Probably: `draft`/`active`/`achieved`/`cancelled`? Or reuse REQ's 7 values? Need to ask.

3. **GOL's related-artifact sub-lists** — REQ has Requirements/Decisions/Goals/Acceptance Criteria. For GOL: Requirements/Decisions/Acceptance Criteria (excluding Goals since it's self-referential)? Or should I include "Acceptance Criteria"? The `ac` domain doesn't exist yet (per AGENTS.md: "The `ac` (acceptance criteria) domain does not yet exist, despite server.py's docstring already reserving a place for it"). Hmm, interesting — so the `### Acceptance Criteria` sub-list within REQ's RelatedArtifacts is a forward-looking cross-reference. For GOL, I'd suggest: Requirements, Decisions, Acceptance Criteria (no Goals). Need to confirm.

4. **Feature folder number** — feat-17-goal (next after feat-16). And slug: "goal-artifact" or "goal"? feat-16 is "problem-statement", feat-6 is "requirement-artifact", feat-10 is "add-artifact-type-tasklist". So the slug might be `feat-17-goal-artifact`.

5. **Prompts** — create_gol/update_gol, same as req/prb (narrated instructions, TodoWrite + question-tool-driven flow, packaged instruction data files). Confirm scope.

Now, on the plan structure itself: the user asked "let's plan this feature" and stated "I want the same structure as the feat-16-problem-statement feature." So the deliverable is the feature folder `.specmgr/feat/feat-17-goal-artifact/README.md`, with a plan following the template structure (frontmatter, Plan section including Overview/Requirements/Acceptance Criteria/Scope/Dependencies/Design Notes/Related ADRs/Task List, Progress section). feat-16's phases were:
- Phase 1: Specification (reference doc, frontmatter model, body model, tests, quality gate)
- Phase 2: Pydantic model, parser & schema (document, parser, summary, field descriptions, generate_gol_schema, parser tests, quality gate)
- Phase 3: MCP surface (tool plumbing, 10 tools, resources, package data, pre-commit, CI, prompts, __init__ + server.py, tests, quality gate)
- Phase 4: Cross-cutting registration (AGENTS.md, doc regeneration, quality gate)
- Phase 5: Final cross-cutting validation (walk through all ACCs, full gate, mark done)

Note: in plan mode I can only create a plan — I can't actually write the README. I should present the plan to the user, get answers to the confirmation questions, and then (after plan mode ends) create the feature folder + README.

Wait — actually, the user said "let's plan this feature." In plan mode, the output should be a well-formed plan. The plan itself is: what's included in the new feature README. I should present the design and ask confirmation questions first.

Let me ask the key confirmation questions:

1. Body structure: GOL = REQ minus Characteristics. Keep `Level` (MUST/SHOULD/MAY) and `Source` as required? Or make them optional?
2. Status set: which one?
3. Related artifacts sub-lists for GOL?
4. Feature number/slug: feat-17-goal-artifact?
5. Should GOL be referenced from REQ's `### Goals` list (already exists) — no changes needed.

Let me think about what's reasonable to recommend:

1. Body structure: keep it simple and mirror REQ minus Characteristics:
   - `statement` (required)
   - `description` (optional)
   - `level` — hmm. For a business goal, obligation strength (MUST/SHOULD/MAY) is actually common in business-requirement literature (e.g., "the company SHOULD reduce costs by X%"). Keep as required? REQ has it required. For symmetry, keep it required. But the user may want something different. I'll ask.
   - `priority` (optional) — keep
   - `tags` (optional) — keep
   - `source` (required) — keep (who/what the goal came from: e.g., a board decision, a stakeholder)
   - `related_artifacts` (optional)
   - `more_information` (optional), `notes` (optional) — keep
   
2. Status: goal lifecycle: draft → active → achieved → cancelled? Or reuse REQ's 7 values? A goal is a "high-level business requirement" so REQ's 7-value set (including `implemented`/`accepted`) might be overkill; business goals are more like `draft`/`active`/`achieved`/`cancelled`. PRB has `resolved` = future state achieved, which is very analogous to a goal being achieved. Hmm. Let me ask the user with options:
   - Option A: 4 values mirroring PRB/TSK/QA: `draft`/`active`/`achieved`/`cancelled`
   - Option B: REQ's 7 values: `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented`
   - Option C: custom

3. Related artifacts sub-lists: `Requirements` (the requirements realizing this goal), `Decisions`, `Acceptance Criteria`. No `Goals` (self-reference). Or maybe include `Goals` for peer goals? I recommend excluding it.

Actually wait — I should think about whether GOL's RelatedArtifacts should be a new model class or reusable. Each domain has its own model class (Req body has `Requirements`/`Decisions`/`Goals`/`AcceptanceCriteria` classes; PRB has opaque leaves). For GOL, I'll define `GolRelatedArtifacts` with sub-sections `Requirements`, `Decisions`, `AcceptanceCriteria` — new classes within `gol/models/v1/body.py`.

4. Numbering: next folder is `feat-17-goal-artifact` (or `feat-17-goal`). Looking at conventions: feat-10-add-artifact-type-tasklist, feat-12-qa-artifact, feat-16-problem-statement. Mixed. I'd propose `feat-17-goal-artifact`.

Also, per AGENTS.md, "the `ac` (acceptance criteria) domain does not yet exist" — the `### Acceptance Criteria` sub-list within RelatedArtifacts is a forward-looking cross-reference to a domain that doesn't exist yet. That's fine for GOL too (same pattern as REQ).

One more consideration: the example id format `GOL-0007` from REQ's example suggests a 4-digit human-facing id prefix "GOL-". This is just cross-reference text, no enforcement.

OK, deliverable for this session (plan mode): I'll present a plan including:
- Confirmation questions (ask now)
- Then the plan: create `.specmgr/feat/feat-17-goal-artifact/README.md` with the full plan structure mirroring feat-16: frontmatter (id, version 1.0.0, status planning, created/updated 2026-08-25), Plan (Overview, Requirements REQ-001..REQ-008, Acceptance Criteria ACC-001..ACC-008, Scope, Dependencies, Design Notes including schema block, Related ADRs, Task List with Phases 1–5), Progress (Current Status, Blockers, Recent Updates with planning entry, Decisions Made, Related PRs/Commits).

Let me use the question tool to ask the confirmation questions. Actually, per plan mode guidance: "when considering trade-offs, ask the user confirmation questions or solicit their opinion." Let me ask the key design questions.

Questions:
1. GOL body structure — which sections? Recommendation: REQ minus Characteristics, keeping statement (required), description (optional), level (required), priority (optional), tags (optional), source (required), related_artifacts (optional), more_information (optional), notes (optional).
   Options:
   - A: Exact mirror of REQ minus Characteristics (level + source required) (recommended)
   - B: Mirror minus Characteristics, but with level/source optional
   - C: Smaller set (statement + description + priority + tags + source + related artifacts only)

2. Status set:
   - A: `draft`/`active`/`achieved`/`cancelled` (4 values, PRB/TSK/QA-style) (recommended — goal lifecycle)
   - B: REQ's 7 values (draft/proposed/accepted/superseded/deprecated/rejected/implemented)
   - C: Something else

3. Related artifacts sub-lists:
   - A: Requirements, Decisions, Acceptance Criteria (no self-referential Goals) (recommended)
   - B: Requirements, Decisions, Goals, Acceptance Criteria (keep all four, same as REQ)

4. Feature folder: `feat-17-goal-artifact`? (Recommendation) or `feat-17-goal`?

Also, should I ask about prompts (create_gol/update_gol)? feat-16 had 2 prompts. req has 2 prompts. I'll assume the same shape (create_gol/update_gol) — low risk, so I'll just note it in the plan rather than asking.

Let me ask 4 questions in a single question tool call.




I now have the full picture. Key findings:

- **feat-16's README** is the structural template: frontmatter (`id`/`version`/`status`/`created`/`updated`), Plan (Overview → Requirements → Acceptance Criteria → Scope → Dependencies → Design Notes → Related ADRs → Task List with 5 phases), Progress (Current Status → Blockers → Recent Updates → Decisions Made).
- **REQ's schema** is the model to mirror: `Requirement(MarkdownSection1)` with mandatory `statement`, optional `description`/`priority`/`tags`/`related_artifacts`/`more_information`/`notes`, mandatory `characteristics`/`level`/`source` — GOL would drop `Characteristics` (ISO 25010).
- Notably, REQ's `RelatedArtifacts` **already has a `### Goals` cross-reference sub-list** (e.g. `GOL-0007: ...`), so the concept is anticipated in the existing schema.
- The full MCP surface pattern (10 tools incl. `list_gol` as paged tool from day one, 3 resources, 2 narrated prompts, packaged data, `specmgr schema` registry, pre-commit + CI hooks, `server.py`/`AGENTS.md` updates) is well-established by REQ/PRB.

Before I write the feature plan, a few design decisions need your input:



**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "Which body sections should GOL have? (Baseline: REQ minus the ISO 25010 `## Characteristics` section.)",
      "header": "GOL body sections",
      "options": [
        {
          "label": "REQ minus Characteristics (Recommended)",
          "description": "statement (mandatory), description (opt), level MUST/SHOULD/MAY (mandatory), priority (opt), tags (opt), source (mandatory), related_artifacts (opt), more_information (opt), notes (opt) — maximal symmetry with REQ."
        },
        {
          "label": "Same, but level+source optional",
          "description": "A high-level business goal may not have an RFC 2119 obligation strength or a named source, so both become optional; only statement stays mandatory."
        },
        {
          "label": "Smaller set",
          "description": "statement, description, priority, tags, source, related_artifacts, more_information, notes — drop `level` entirely."
        }
      ]
    },
    {
      "question": "Which frontmatter status set should GOL use?",
      "header": "Status set",
      "options": [
        {
          "label": "draft/active/achieved/cancelled (Recommended)",
          "description": "4-value set in PRB/TSK/QA style, goal-specific semantics: draft = being written, active = pursued, achieved = reached, cancelled = abandoned."
        },
        {
          "label": "REQ's 7-value set",
          "description": "draft/proposed/accepted/superseded/deprecated/rejected/implemented — full symmetry with requirements."
        }
      ]
    },
    {
      "question": "Which cross-reference sub-lists should GOL's `## Related Artifacts` contain?",
      "header": "Related artifacts",
      "options": [
        {
          "label": "Requirements, Decisions, Acceptance Criteria (Recommended)",
          "description": "No self-referencing `### Goals` sub-list; requirements list the REQs that realize the goal."
        },
        {
          "label": "All four, same as REQ",
          "description": "Requirements, Decisions, Goals, Acceptance Criteria — identical to REQ's RelatedArtifacts (Goals would list peer/superseding goals)."
        }
      ]
    },
    {
      "question": "What folder name for the feature? (Next free number after feat-16.)",
      "header": "Feature folder",
      "options": [
        {
          "label": "feat-17-goal-artifact (Recommended)",
          "description": "Follows feat-12-qa-artifact / feat-6-requirement-artifact naming."
        },
        {
          "label": "feat-17-goal",
          "description": "Shorter, follows feat-16-problem-statement naming."
        }
      ]
    }
  ]
}
```

**Output:**
```
User has answered your questions: "Which body sections should GOL have? (Baseline: REQ minus the ISO 25010 `## Characteristics` section.)"="REQ minus Characteristics (Recommended)", "Which frontmatter status set should GOL use?"="REQ's 7-value set", "Which cross-reference sub-lists should GOL's `## Related Artifacts` contain?"="All four, same as REQ", "What folder name for the feature? (Next free number after feat-16.)"="feat-17-goal". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 97.1s)

_Thinking:_

User's answers:
1. Body: REQ minus Characteristics — statement (required), description (optional), level (required), priority (optional), tags (optional), source (required), related_artifacts (optional), more_information (optional), notes (optional)
2. Status: REQ's 7-value set (draft/proposed/accepted/superseded/deprecated/rejected/implemented)
3. Related artifacts: all four (Requirements, Decisions, Goals, Acceptance Criteria)
4. Folder: feat-17-goal

Now I can write the plan. Plan mode is still active — I can't create files. I'll present a comprehensive plan for the feature README, so that after plan mode ends, I can create `.specmgr/feat/feat-17-goal/README.md` following the feat-16 structure.

Let me carefully draft the full plan contents:

**Frontmatter:**
```yaml
---
id: feat-17-goal
version: 1.0.0
status: planning
created: 2026-08-25
updated: 2026-08-25
---
```

**Title:** `# Feature: Add artifact type Goal (gol)`

**Overview:**
Add a new markdown artifact type `Goal` (abbreviation `gol`) for capturing high-level business goals. `gol` follows the domain-first hierarchy and MCP surface established by `req`/`prb` (ADR ece4554b), and mirrors REQ's body schema minus the ISO 25010 `## Characteristics` section. REQ's `### Goals` cross-reference sub-list (e.g. `GOL-0007: ...`) already anticipates this artifact type. Status set: REQ's 7-value set. Related artifacts: all four sub-lists same as REQ.

**Requirements (REQ-001..REQ-008), mirroring feat-16:**
- REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`, 7-value status set `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented`) and body (H1 title, required `statement` lead paragraph, optional `## Description`, required `## Level`, optional `## Priority`, optional `## Tags`, required `## Source`, optional `## Related Artifacts` with four optional `### ` sub-lists, optional `## More Information`, optional `## Notes`).
- REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body, document, parser, summary), domain-first, mirroring `req`/`prb` file shape. No changes to the `models/md` engine.
- REQ-003: Parse/validate `gol` documents from markdown, mirroring `parse_req`/`parse_prb`'s two-error-channel convention.
- REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, plus `list_gol` as a paging tool from day one (ADR ec9f5262): `parse_gol`, `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub), `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`, `list_gol`.
- REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template` (no `/list`, no `/{id}`).
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated `TodoWrite` + `question`-tool-driven flow, packaged instruction data files (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`).
- REQ-007: Package example/template/schema data under `gol/data/` via `general/tools/_packaged_data.py`, with corresponding `pyproject.toml` package-data entries, pre-commit hooks, and CI steps.
- REQ-008: Documentation generation wiring — `specmgr docs`, `specmgr schema` (new `gol` entry in `commands/schema.py`), `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; update `AGENTS.md` to eight domain/cross-cutting packages.

**Acceptance Criteria (ACC-001..ACC-008)** — mirror feat-16's 8 ACCs, one per REQ.

**Scope:**
Included:
- `gol` schema, models, parser, summary under `gol/models/v1/`.
- Full MCP surface (10 tools including `list_gol`, 3 resources, 2 prompts, package data).
- Tests mirroring `tests/req/`/`tests/prb/`.
- Cross-cutting registrations (`server.py`, `pyproject.toml`, `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

Out of scope:
- No structured enforcement/validation of cross-references within `### Requirements`/`### Decisions`/`### Goals`/`### Acceptance Criteria` sub-lists (opaque free text, same as REQ).
- Implementation of `delete_gol` (stub only, same as all other domains).
- Granular mutation tools of ADR-style `update_section` — `update_gol` is a whole-body replace.
- A `specmgr gol-toc` equivalent.
- No new ADR — all decisions follow existing precedent.

**Dependencies:**
- ADR ece4554b (domain-first), ADR bc5e18ad (generic frontmatter), ADR ddfb1109 (id-based read = tool only), ADR ec9f5262 (list as paging tool from day one), existing `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py`, `general/models/{DocSummary,PagedResult}`, `models/md` engine as-is.
- Blocks: none.

**Design Notes:**
Schema block:
```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}

Goal(MarkdownSection1)                 # H1, free-form title (alias ".+")
├── statement: MarkdownParagraph       # required lead paragraph
├── description: Description | None    # optional H2 "Description"
├── level: Level                       # required H2 "Level", RFC 2119 value + optional comment
├── priority: Priority | None          # optional H2 "Priority", 0-99 + optional comment
├── tags: Tags | None                  # optional H2 "Tags", bullet list
├── source: Source                     # required H2 "Source", single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
│   ├── requirements: Requirements | None       # optional H3
│   ├── decisions: Decisions | None             # optional H3
│   ├── goals: Goals | None                     # optional H3
│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3
├── more_information: MoreInformation | None  # optional H2 "More Information"
└── notes: Notes | None                    # optional H2 "Notes"
```

- Reuse REQ's exact pattern: `Level`/`Priority` are `MarkdownSection2WithComment` + `field_validator` (pattern re-implemented inside `gol/models/v1/body.py` — not imported from `req` — same as how PRB keeps its own leaf classes. Domain packages do not import from each other).

Wait — actually, do domain packages import from each other? Let me check: prb's body has its own leaf classes. req's body defines its own classes. I should verify whether GOL can import `req.models.v1.body.Level` or whether it must duplicate it. Let me check whether cross-domain imports exist… In feat-16's PRB design, "every `Question{N}` class is a plain leaf subclass" — they made their own. For Level/Priority with validators, there are two choices:
  a) Duplicate the classes into `gol/models/v1/body.py` (each domain is self-contained)
  b) Import from `req.models.v1.body` (cross-domain dependency)

Let me check whether cross-domain imports exist in the codebase. A quick grep would help. Actually — this is a planning detail. I'll check before writing the plan. Let me grep for "from ...req" or "from ..req" within src.

- `RelatedArtifacts`'s four sub-lists: same class shape as REQ's (`MarkdownSection3` with `items: list[MarkdownListItem] = Field(min_length=1)`).
- Note: the cross-reference id format (e.g. `GOL-0007`, `REQ-9687`) is conventional text only, not enforced.
- Whole-body replace for `update_gol(id, content)`.
- `list_gol` as a paging tool from day one (ADR ec9f5262) — `GolSummary(DocSummary)`.
- `GolFrontmatter.status` uses REQ's 7-value `_ALLOWED_STATUSES` set (re-declared within gol's frontmatter module, same as `TskFrontmatter`/`ReqFrontmatter` each declare their own).
- Prompts: narrated only, packaged instruction files, `string.Template`.
- Example/template: `gol_example.md` — hmm, REQ's example is "Maximum Engine Temperature". For GOL, the example should be a business goal, e.g. "Competitive Engines in Consumer Vehicles" (which appears in REQ's example's `### Goals` sub-list as GOL-0007!). Nice: `req_example.md` already references `GOL-0007: Competitive Engines in Consumer Vehicles`. So the gol example can be that very goal — a good consistency touch. And the template mirrors `req_template.md` minus Characteristics.

**Related ADRs:** same 5 as feat-16:
- ece4554b: domain-first hierarchy
- bc5e18ad: generic base frontmatter
- ddfb1109: id-based read is tool-only
- ec9f5262: list as paging tool
- 71fd95d7: update_section — reviewed, explicitly not reused

**Task list** (mirror feat-16's 5 phases):

Phase 1: Spec
- 1.1: Create `gol_reference.md` in the feature folder, exercising every field
- 1.2: `gol/models/v1/frontmatter.py` — `GolFrontmatter` (7-value status set, mirror `ReqFrontmatter`)
- 1.3: `gol/models/v1/body.py` — `Goal(MarkdownSection1)`, etc.
- 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py`
- 1.5: Phase-end quality gate + README progress update

Phase 2: Pydantic models, parser, schema
- 2.1: `gol/models/v1/document.py` — `GolDocument`
- 2.2: `parse_gol`
- 2.3: `gol/models/v1/summary.py` — `GolSummary`
- 2.4: Field descriptions
- 2.5: `generate_gol_schema()` in `commands/schema.py` + registry + `docs/gol_schema.json`
- 2.6: `tests/gol/models/v1/test_parser.py`
- 2.7: Phase-end quality gate

Phase 3: MCP surface
- 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`
- 3.2: `parse_gol` tool
- 3.3: `create_gol` tool
- 3.4: `update_gol` tool
- 3.5: `set_status_gol` tool
- 3.6: `delete_gol` stub
- 3.7: `validate_gol` tool
- 3.8: `get_gol` tool
- 3.9: `list_gol` tool
- 3.10: `get_gol_example`/`get_gol_template` + package data
- 3.11: `gol/resources/` — 3 resources
- 3.12: `pyproject.toml` package-data + pre-commit hooks (expand the shared schema-hook glob to include `gol/models/v1`, add `specmgr-schema-gol-package`)
- 3.13: CI steps
- 3.14: `create_gol` prompt + instruction file
- 3.15: `update_gol` prompt + instruction file
- 3.16: `gol/__init__.py` + `server.py` import line (`adr, general, gol, prb, qa, req, tsk, uc`) + docstring
- 3.17: `tests/gol/...` (tools, resources, prompts, integration)
- 3.18: Phase-end quality gate

Phase 4: Cross-cutting registrations
- 4.1: `AGENTS.md` — heading "eight domain/cross-cutting packages (ADR, REQ, UC, TSK, QA, PRB, GOL, general)", `gol/` bullet, "Still genuinely missing" list, closing paragraph
- 4.2: Regenerate `specmgr docs`/`mcp-docs`/`schema`, zero drift
- 4.3: Phase-end quality gate

Phase 5: Final cross-cutting verification
- 5.1: Walk every ACC with evidence, full gate, set status to done

**Progress section** (initial state):
- Current Status: as of 2026-08-25: planning complete, implementation not started.
- Blockers: none.
- Recent Updates: planning entry (completed: design/planning discussion; next: Phase 1).
- Decisions Made:
  - 2026-08-25: abbreviation `gol`, domain-first layout (`gol/models/v1/`, etc.)
  - 2026-08-25: body mirrors REQ minus `Characteristics`; `statement`/`level`/`source` required.
  - 2026-08-25: status set = REQ's 7-value set.
  - 2026-08-25: Related Artifacts = all four sub-lists same as REQ (including a `### Goals` self-reference for peer goals).
  - 2026-08-25: `update_gol` is a whole-body replace, not `update_section`.
  - 2026-08-25: `list_gol` is a paging tool from day one (ADR ec9f5262).
- Related PRs/Commits: (empty for now)

One more check before finalizing the plan: does any domain import model classes from another domain (e.g. can gol import req's `Level`)? Let me quickly grep. Also, I'll check `req/models/v1/_util.py` and `document.py` to reference the exact pattern. Also check `whitelist.py` (vulture whitelist) — feat-16 added field names to the whitelist; the new Pydantic fields for GOL will also need a whitelist entry.

Let me run these greps.




All decisions have been recorded. Before drafting the plan, I'll do a final check on a few implementation details (cross-domain imports, the vulture whitelist, the document/parser patterns).



**Tool: bash**

**Input:**
```json
{
  "command": "grep -rn \"from ...req\\|from ...prb\\|from ...tsk\\|from ...qa\\|from ...uc\\|from ...adr\" src/biz/dfch/specmgr --include=\"*.py\" | grep -v \"tools/_paths\\|models.md\\|general\" | head -10; echo \"=== whitelist ===\"; grep -n \"current_state\\|question_1\\|statement\\|characteristics\" whitelist.py | head; echo \"=== req document.py ===\"; sed -n '17,60p' src/biz/dfch/specmgr/req/models/v1/document.py"
}
```

**Output:**
```
=== whitelist ===
70:characteristics
92:statement
93:sub_characteristics
120:current_state
124:question_1
=== req document.py ===

"""Pydantic model for a full requirement document (frontmatter + body).

Mirrors `models.adr.v1.Adr`'s own frontmatter+body pairing. ``ReqDocument`` holds
no file/id/path information itself -- that lives on ``frontmatter.id``, same
convention as ``AdrFrontmatter.id``.

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``ReqFrontmatter`` and ``.content`` as ``Requirement.from_text(...)`` separately, then
constructs a ``ReqDocument`` from the two already-parsed pieces -- there is no
``ReqDocument.from_text``/parser function here.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Requirement
from .frontmatter import ReqFrontmatter

__all__ = ["ReqDocument"]


class ReqDocument(BaseModel):
    """A full requirement document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`ReqFrontmatter`.
    body:
        The parsed requirement sections. See :class:`Requirement`.
    """

    frontmatter: ReqFrontmatter
    body: Requirement

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 78.3s)

_Thinking:_

Confirmed:
- No imports of model classes between domains (grep results were empty) — so GOL needs to define its own `Level`/`Priority`/etc. classes inside `gol/models/v1/body.py` (re-implementing the patterns from REQ), which is consistent with the domain-first policy.
- `whitelist.py` already has `characteristics`, `statement`, `current_state`, `question_1`, etc. — the new Pydantic field names in GOL (statement, level, priority, tags, source, related_artifacts, etc.) will need to be added if vulture can't recognize them. Note that `statement` (line 92) is already in the whitelist. New names like `goal`... actually, the body class field names are: statement (already exists), description (probably already exists — used in ADR? needs checking), level, priority, tags, source, related_artifacts, more_information, notes. Many of these already exist in REQ, so they should already be in the whitelist. I'll note in the plan: "add any new field names that vulture can't recognize to whitelist.py as needed" (following the note for feat-16's phase 1).
- `ReqDocument` pattern confirmed.

Now I'm ready to present the complete plan. The deliverable is `.specmgr/feat/feat-17-goal/README.md`, and the contents will follow the structure of feat-16. Since I'm in plan mode, I'll present the plan as text so the user can review and approve, and then (in execution mode) I'll create the file.

Following the instructions: the plan should be comprehensive yet concise. The user has requested "let's plan this feature" — the feature plan itself is the README. I'll present a structured summary of what will go into the README. Main sections with the actual content decisions baked in.

I'll write it in a form that's readable in the CLI. I'll show the overall design and the phase structure, and note that I'll create the complete README (with all the details like ACCs and task lines) in the execution phase.

Actually, the plan should be detailed enough to be executable. Since I'll be writing the README myself right after, the plan presentation can be somewhat compact. However, the plan-mode system prompt says "present a well-researched plan to the user and resolve all ambiguities before starting implementation." I'll present the following:

1. Deliverable: `.specmgr/feat/feat-17-goal/README.md` (planning session only — no code yet)
2. Design decisions (from Q&A + my investigation)
3. Schema (design notes)
4. Requirements / ACCs overview
5. Task phases (overview of the 5 phases)
6. Cross-cutting changes (server.py, AGENTS.md, pyproject, pre-commit, CI, commands/schema.py)
7. Out of scope

Then, on user approval, I'll write the full README.




No cross-domain model imports exist (each domain re-implements its own classes), `whitelist.py` already carries the REQ/PRB field names, and the `ReqDocument` pattern is confirmed. Here is the plan.

---

# Plan: Feature `feat-17-goal` — Add artifact type Goal (GOL)

## Deliverable

**This session is planning-only** (mirrors how feat-16 started): create `.specmgr/feat/feat-17-goal/README.md` from `.specmgr/_template/v1/README.md`, structured exactly like `feat-16-problem-statement/README.md`. No source code is written yet.

## Design decisions (per your answers + codebase precedent)

| Decision | Choice |
|---|---|
| Abbreviation / folder | `gol` / `feat-17-goal` (next free number after feat-16; `NNN` = GitHub issue number placeholder convention, like feat-16) |
| Layout | Domain-first: `gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`, `gol/data/` (ADR ece4554b; schema inside the domain package, like REQ/PRB) |
| Body | REQ mirrored **minus `## Characteristics`**: mandatory `statement` (H1 lead paragraph), optional `Description`, mandatory `Level` (RFC 2119), optional `Priority` (0–99), optional `Tags`, mandatory `Source`, optional `Related Artifacts` + `More Information` + `Notes` |
| `Related Artifacts` | All four sub-lists, identical to REQ: `Requirements`, `Decisions`, `Goals`, `Acceptance Criteria` (each optional `###` H3 bullet list, `min_length=1`) |
| Status set | REQ's 7-value set: `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented` |
| Update mechanism | Whole-body `update_gol(id, content)` (REQ/PRB convention) — ADR-style `update_section` explicitly *not* reused (ADR 71fd95d7) |
| Listing | `list_gol` as a **paged tool from day one** (`PagedResult[GolSummary]`, 25/100 via `general/tools/_paging.py`) per ADR ec9f5262 — no `specmgr://gol/list` resource |
| Id reads | `get_gol` tool only, no `specmgr://gol/{id}` resource (ADR ddfb1109) |
| Classes | `Level`/`Priority` (with their `field_validator` re-implementations) and all list/leaf classes are re-declared in `gol/models/v1/body.py` — no cross-domain imports (verified: none exist) |
| Prompts | `create_gol(topic)` / `update_gol(id)` — narrated `TodoWrite` + `question`-tool flows, instructions in packaged `gol/data/gol_{create,update}_instructions.md` via `string.Template` (req/prb precedent) |
| Example consistency | `req_example.md` already references `GOL-0007: Competitive Engines in Consumer Vehicles` — the GOL example document will *be* that goal, so the existing cross-reference reads coherently |
| New ADRs | None — every decision follows an accepted ADR's precedent |

## README contents (feat-16 structure)

**Plan section**
- **Overview** — as above, plus note that REQ's `### Goals` sub-list already anticipates this artifact.
- **Requirements REQ-001…REQ-008** (1:1 mapping to feat-16's): schema; models under `gol/models/v1/` (no `models/md` engine changes); parser with two-error-channel convention; 10 MCP tools incl. `list_gol` paged-from-day-one; 3 resources (`schema`/`example`/`template`); 2 narrated prompts; packaged data + pyproject/pre-commit/CI wiring; doc generation + `AGENTS.md` → "eight domain/cross-cutting packages (ADR, REQ, UC, TSK, QA, PRB, GOL, general)".
- **Acceptance Criteria ACC-001…ACC-008** — one per REQ, each with a concrete, testable PASS condition (schema JSON exists + reference round-trips; mandatory/optional field validation; parser error channels; all 10 tools live-registered incl. paging behavior; 3 resources; prompts narrated end-to-end; packaged data resolves from a real wheel install; zero doc drift).
- **Scope** — included: models, parser, full MCP surface, tests mirroring `tests/req/`/`tests/prb/`, cross-cutting registration. Out of scope: cross-reference id validation (sub-lists stay opaque text), `delete_gol` real implementation (stub like all domains), `update_section`-style granular tools, a `gol-toc` command.
- **Dependencies** — ADRs ece4554b, bc5e18ad, ddfb1109, ec9f5262, 71fd95d7 (reviewed, not reused); `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py`, `general/models`, `models/md` engine as-is.
- **Design Notes** — the full schema tree (mirroring feat-16's style):

```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}

Goal(MarkdownSection1)                          # H1, free-form title (alias ".+")
├── statement: MarkdownParagraph                # mandatory lead paragraph
├── description: Description | None             # optional H2
├── level: Level                                # mandatory H2, RFC 2119 value + optional comment
├── priority: Priority | None                   # optional H2, 0-99 + optional comment
├── tags: Tags | None                           # optional H2 bullet list
├── source: Source                              # mandatory H2 single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2
│   ├── requirements / decisions / goals /
│   └── acceptance_criteria                     # 4 optional H3 bullet lists, each min_length=1
├── more_information: MoreInformation | None    # optional H2
└── notes: Notes | None                         # optional H2
```

plus: two-error-channel parser contract, `GolSummary(DocSummary)`, prompts behavior, `whitelist.py` additions for new vulture-invisible field names.

- **Task List — 5 phases** (1:1 mapping to feat-16's task shape, all `status: not-started`):
  - **Phase 1: Specification** — `gol_reference.md` in the feature folder; `frontmatter.py`; `body.py`; `test_frontmatter.py`/`test_body.py`; phase-end gate
  - **Phase 2: Pydantic Models, Parser & Schema** — `document.py`; `parse_gol`; `summary.py`; field descriptions; `generate_gol_schema()` + `commands/schema.py` registry + `docs/gol_schema.json`; `test_parser.py`; phase-end gate
  - **Phase 3: MCP Surface** — tools plumbing (`_paths`/`_io`/`_write`/`_lock`); 9 lifecycle tools (`parse_gol`, `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` stub, `validate_gol`, `get_gol`, `list_gol`, `get_gol_example`/`get_gol_template`); 3 resources; pyproject package-data + pre-commit (shared schema-hook glob + `specmgr-schema-gol-package`) + CI steps; 2 prompts + instruction files; `gol/__init__.py` + `server.py` import line (`adr, general, gol, prb, qa, req, tsk, uc`) + docstring; `tests/gol/` (tools/resources/prompts/integration); phase-end gate
  - **Phase 4: Cross-cutting registration** — `AGENTS.md` (heading, `gol/` bullet, "Still genuinely missing" list, closing enumerations); `specmgr docs`/`mcp-docs`/`schema` zero-drift re-run; phase-end gate
  - **Phase 5: Final verification** — walk ACC-001…008 with evidence (live lifecycle run, wheel install check, full quality gate); set status `done`

**Progress section** (initial) — Current Status: planning complete; Blockers: none; Recent Updates: one planning entry; Decisions Made: the table above logged as dated entries; Related PRs/Commits: empty.

## What happens after you approve

1. Create the feature folder + full `README.md` (the only file touched in this session).
2. Phases 1–5 get implemented in later sessions, phase by phase, each ending in the quality gate (ruff, vulture, full unittest, doc drift checks).

Shall I proceed with writing `.specmgr/feat/feat-17-goal/README.md`?

---

## User

A GOAL does not have a (requirement) "level". (A GOAL is implicitly always a MUST.)

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 37.9s)

_Thinking:_

User's statement: Goals (GOAL) do not have a (requirement) "Level". Goals are implicitly always MUST.

Therefore the GOL body should drop `## Level` entirely. This is essentially the third option from my initial question ("smaller set — drop Level"), but combined with their other answers: REQ minus Characteristics, minus Level, keeping source required, Related Artifacts has all four, status is REQ's 7-value set.

So the revised schema is:

```
Goal(MarkdownSection1)                          # H1, free-form title (alias ".+")
├── statement: MarkdownParagraph                # mandatory lead paragraph
├── description: Description | None             # optional H2
├── priority: Priority | None                   # optional H2, 0-99 + optional comment
├── tags: Tags | None                           # optional H2 bullet list
├── source: Source                              # mandatory H2 single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2, 4 optional H3 sublists
├── more_information: MoreInformation | None    # optional H2
└── notes: Notes | None                         # optional H2
```

Mandatory: `statement`, `source`. Optional: everything else. No `Level`, no `Characteristics`.

Design note to record: goals are implicitly obligation strength MUST — no `## Level` section; the rationale for this is recorded in the Decisions Made entry.

This is a clear correction, no need to re-ask. Just briefly confirm the updated schema and ask whether to proceed with writing the README. Keep it short. Should I also update the ACC/REQ wording? REQ-001's description changes: mandatory `statement` + `source`; no `level`.

I should present the diff concisely and ask for approval to proceed (the previous question "Shall I proceed?" is still pending).




Understood — `## Level` drops out entirely; a goal's obligation strength is implicitly always MUST. That leaves exactly two mandatory body fields: `statement` and `source`.

**Revised schema** (Design Notes for the README):

```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}

Goal(MarkdownSection1)                          # H1, free-form title (alias ".+")
├── statement: MarkdownParagraph                # MANDATORY lead paragraph
├── description: Description | None             # optional H2
├── priority: Priority | None                   # optional H2, 0-99 + optional comment
├── tags: Tags | None                           # optional H2 bullet list
├── source: Source                              # MANDATORY H2 single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2
│   ├── requirements / decisions / goals /
│   └── acceptance_criteria                     # 4 optional H3 bullet lists, each min_length=1
├── more_information: MoreInformation | None    # optional H2
└── notes: Notes | None                         # optional H2
```

Consequences for the plan:

- **REQ-001** schema wording: no `Level`; mandatory = `statement` + `source`.
- **`gol/models/v1/body.py`**: no `Level` class or RFC 2119 validator — REQ's `Level` precedent is *not* carried over; only `Priority` keeps the `MarkdownSection2WithComment` + `field_validator` pattern.
- **Example/template/reference documents**: no `## Level` section; a "Decisions Made" entry logs the rationale (a goal is implicitly always MUST; obligation strength is a requirement-level attribute).
- **Prompts**: `create_gol`/`update_gol` interview flow elicits `statement`, `source`, and the optional fields — no level question.
- Everything else in the approved plan is unchanged (status set, all-four related-artifact sub-lists, `gol` abbreviation, 10 tools / 3 resources / 2 prompts, 5 phases, `feat-17-goal` folder).

Shall I now write `.specmgr/feat/feat-17-goal/README.md` with this revision?

---

## User

Create the github issue with a short overview as the description. Get the id of the issue, confirm it is 17. Then write the feature to disk.

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 21.5s)

_Thinking:_

What the user is asking for is:
1. Create a GitHub issue with a short overview description
2. Get the issue ID and confirm it is 17
3. Then write the feature (README.md) to disk

Wait — if the issue ID comes out to 17, then the folder is `feat-17-goal`. But if the ID comes out to something different, I should use that ID. Let me create the issue first.

Check whether `gh` is available and what the remote is. Let me create the issue. The title will be something like "Add artifact type Goal (GOL)", and the description will be a short overview.

Let's get started.


**Tool: bash**

**Input:**
```json
{
  "command": "git remote -v && gh auth status 2>&1 | head -5"
}
```

**Output:**
```
origin	https://github.com/dfch/biz.dfch.SpecMgr.git (fetch)
origin	https://github.com/dfch/biz.dfch.SpecMgr.git (push)
github.com
  ✓ Logged in to github.com as dfch (/home/user/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: *******************
  

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 24.8s)

_Thinking:_

Good. Now let's create the issue. Title: "Add artifact type Goal (GOL)". Description: a short overview.


**Tool: bash**

**Input:**
```json
{
  "command": "gh issue create --title \"Add artifact type Goal (GOL)\" --body \"New markdown artifact type \\\\\\`Goal\\\\\\` (abbreviation \\\\\\`gol\\\\\\`) for capturing high-level business goals, mirroring the \\\\\\`req\\\\\\` domain's schema minus the ISO 25010 \\\\\\`Characteristics\\\\\\` section and the \\\\\\`Level\\\\\\` section (a goal is implicitly always MUST).\n\n- Body: mandatory \\\\\\`statement\\\\\\` + \\\\\\`source\\\\\\`; optional \\\\\\`description\\\\\\`, \\\\\\`priority\\\\\\`, \\\\\\`tags\\\\\\`, \\\\\\`related artifacts\\\\\\` (all four REQ sub-lists), \\\\\\`more information\\\\\\`, \\\\\\`notes\\\\\\`\n- Frontmatter status: REQ's 7-value set\n- Full MCP surface per ADR ece4554b/ec9f5262/ddfb1109: 10 tools (incl. \\\\\\`list_gol\\\\\\` as paged tool from day one), 3 resources, 2 narrated prompts, packaged data\n- Plan: \\\\\\`.specmgr/feat/feat-17-goal/README.md\\\\\\`\" 2>&1"
}
```

**Output:**
```
https://github.com/dfch/biz.dfch.SpecMgr/issues/18

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 21.0s)

_Thinking:_

The issue was created with ID 18, not 17. The user said "get the issue ID and verify that it's 17." But it's 18. So issue number 17 must already exist (probably closed, or assigned to something else). Let me check.




The issue got ID **18**, not 17. Let me check what issue 17 is.



**Tool: bash**

**Input:**
```json
{
  "command": "gh issue view 17 --json number,title,state 2>&1; echo \"---\"; gh issue list --state all --limit 25 --json number,title,state 2>&1"
}
```

**Output:**
```
{"number":17,"state":"MERGED","title":"Feat 16 problem statement"}
---
[{"number":18,"state":"OPEN","title":"Add artifact type Goal (GOL)"},{"number":16,"state":"CLOSED","title":"Add artifact type ProblemStatement (prb)"},{"number":15,"state":"OPEN","title":"Add artifact type Risk"},{"number":14,"state":"OPEN","title":"QA v2: adjacent question/answer pairs (no per-question heading)"},{"number":13,"state":"CLOSED","title":"Add pagination to <domain>_list (resource->tool + shared PagedResult)"},{"number":12,"state":"CLOSED","title":"Feature: Question and Answer (QA) artifact type"},{"number":10,"state":"CLOSED","title":"Add artifact type TaskList"},{"number":9,"state":"CLOSED","title":"Migrate /doc to .specmgr"},{"number":8,"state":"CLOSED","title":"Add coverage badge with SVG generation and CI/pre-commit enforcement"},{"number":7,"state":"OPEN","title":"Various cross-cutting improvements"},{"number":6,"state":"CLOSED","title":"Requirement (REQ) artifact template"},{"number":5,"state":"CLOSED","title":"Generic heading-mapped Markdown-to-Pydantic document parser"},{"number":4,"state":"CLOSED","title":"Feature: Create Use Cases with tool support"},{"number":3,"state":"CLOSED","title":"Feature: Implement Markdown string type with content constraints for specmgr"},{"number":2,"state":"OPEN","title":"docs: Add Technical Debt section to feature template"},{"number":1,"state":"OPEN","title":"Refactor: Move ADR models from models/adr to adr/models for consistency"}]

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 233.4s)

_Thinking:_

Interesting — issue #17 exists as a **PR** ("Feat 16 problem statement", state MERGED). In other words, issue/PR numbers share the same counter on GitHub, and 17 was consumed by the PR for feat-16. So the new issue became #18.

Per the convention: `feat-NNN-slug`, where NNN is the GitHub issue number. So the folder must be `feat-18-goal`, not `feat-17-goal`.

The user explicitly said: "get the issue ID and confirm it's 17." But it's 18. I should tell the user about this: #17 was already used by a merged PR. The feature folder per convention must be `feat-18-goal`. I should report this discrepancy and proceed with 18 (since that's what the convention dictates — the ID inside the folder name is the single source of truth). The user asked to "confirm it's 17" — since it can't be 17, I should tell them and proceed with 18. The whole point of "get the issue ID and confirm it's 17" was to derive the folder name. The folder name has to match the actual issue ID, so it's `feat-18-goal`.

Let's not over-block on this. Report it clearly, then proceed to write the feature to disk as `feat-18-goal` with `id: feat-18-goal` in the frontmatter. That's what's consistent with the ADR convention (id = folder name = issue number).

Hmm, but should I ask the user first? The user's instruction was "get the issue ID and confirm it's 17. Then write the feature to disk." The confirmation failed. The intent is clear: the folder name derives from the issue ID. Since the issue ID is 18, the folder is `feat-18-goal`. Asking again would be noise. The right action is: proceed with 18, and clearly flag the reason (17 was consumed by the merged PR for feat-16).

Also, should I update the issue body? The issue body says `.specmgr/feat/feat-17-goal/README.md` — it's a typo in my body. Let me edit the issue body to point to feat-18-goal.

Now let's write the feature README. I'll model it on feat-16's structure, including the design decisions:

- id: feat-18-goal
- version: 1.0.0
- status: planning
- created: 2026-08-25
- updated: 2026-08-25

Title: `# Feature: Add artifact type Goal (gol)`

Let me draft the full content carefully, mirroring feat-16's structure:

**Overview**: Add a new markdown artifact type `Goal` (abbreviation `gol`) to capture high-level business goals... mirrors the `req` domain minus `Characteristics` (ISO 25010) and minus `Level` (RFC 2119 — goals are implicitly always MUST). REQ's `### Goals` cross-reference sub-list already anticipates this (req_example.md references GOL-0007). Domain-first layout, full MCP surface per ADR. Status: REQ's 7-value set. Related artifacts: all four sub-lists same as REQ.

**Requirements** (8, mirroring feat-16):
- REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`, 7-value status set `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented` — REQ's exact set) and body (H1 title, mandatory `statement` lead paragraph, optional `## Description`, optional `## Priority`, optional `## Tags`, mandatory `## Source`, optional `## Related Artifacts` with four optional `### ` sub-lists (Requirements/Decisions/Goals/Acceptance Criteria), optional `## More Information`, optional `## Notes`). No `## Characteristics` (ISO 25010 is a requirement-level attribute), no `## Level` (RFC 2119 obligation strength is implicit: a goal is always MUST).
- REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body, document, parser, summary), domain-first, mirroring `req`/`prb`'s exact file shape. No changes to the `models/md` engine — all fields constructible with the existing declarative heading-mapped parser.
- REQ-003: Parse/validate `gol` documents from markdown, mirroring `parse_req`/`parse_prb`'s two-error-channel convention (`AssertionError` for structural problems, `pydantic.ValidationError` for field-level problems).
- REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, and further, per ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, `list_gol` as a paged tool from day one (new domains must not add a `specmgr://gol/list` resource and convert it later): `parse_gol`, `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub), `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`, `list_gol`.
- REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template` (no `/list` — REQ-004 covers listing as a tool. no `/{id}` — id-based reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated `TodoWrite` + `question`-tool-driven interview flow (reusing the narration pattern from `req/prompts/create_req.py` and the dedup-check-first pattern). Both use their own packaged instruction data files (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`), not inline strings.
- REQ-007: Packaged example/template/schema data (`gol/data/`) via the existing generic `general/tools/_packaged_data.py`, with corresponding `pyproject.toml` package-data entries, pre-commit hooks, and CI steps.
- REQ-008: Doc-generation wiring — `specmgr docs`, `specmgr schema` (new `gol` entry in the doc-type registry, `commands/schema.py`), `specmgr mcp-docs`, all kept drift-free via pre-commit/CI. Update `AGENTS.md` to "eight domain/cross-cutting packages."

**Acceptance Criteria** (8, mirroring feat-16):
- ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`, `specmgr://gol/schema`). Reference `gol_reference.md` exercising every field round-trips through the parser.
- ACC-002: Verifies REQ-002 — Pydantic models validate required (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`, `Related Artifacts` and its four sub-lists, `More Information`, `Notes`) fields correctly. `GolFrontmatter.status` rejects any value outside the 7-value set.
- ACC-003: Verifies REQ-003 — parser produces a valid object tree for a well-formed document. Missing mandatory sections raises `AssertionError`. Invalid field values raise `pydantic.ValidationError`.
- ACC-004: Verifies REQ-004 — all enumerated tools are implemented, registered, and callable. `list_gol` returns a `PagedResult[GolSummary]` with default page size 25 / cap 100, mirroring the other domains' `list_<d>` tools exactly.
- ACC-005: Verifies REQ-005 — all enumerated resources are implemented and registered.
- ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate: (a) duplicate/similar-document check via `list_gol` first, (b) building a `TodoWrite` list covering `statement` + optional fields + `source`, (c) elicitation via the `question` tool (explicitly permitting skips), (d) assembling and calling `create_gol(content)`/`update_gol(id, content)` at the end — validated by reading the packaged instruction files in full and manually walking the narrated flow end-to-end against a real document.
- ACC-007: Verifies REQ-007 — packaged data resolves correctly from a real, non-editable install (`uv build --wheel` + scratch-venv install).
- ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` all report no drift after implementation. `AGENTS.md` reflects eight domain/cross-cutting packages.

Note: for a planning-phase README, feat-16's ACCs were written with `[x]` + PASS evidence after implementation. In planning state, ACCs should be `[ ]` checkboxes without PASS verdicts (the template shows `- [ ] ACC-001: ...`). Right — planning-phase READMEs have unchecked ACCs. feat-16's README was fully implemented (status: done). Ours is planning, so ACCs stay unchecked, and Task List all `not-started`.

**Scope**:
Included:
- The `gol` markdown schema, Pydantic models, parser, and summary under `gol/models/v1/`.
- Full MCP surface (tools/resources/prompts/packaged data), including `list_gol` as a tool (not a resource) from the start.
- Interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` + `question`-tool-driven interview, agent-drafted/refined sections).
- Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.
- Cross-cutting registration (`server.py`, `pyproject.toml`, `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

Explicitly out of scope:
- `## Characteristics` (ISO 25010) — quality characteristics are a requirement-level attribute. Goals stay deliberately free of them (user decision).
- `## Level` (RFC 2119 obligation strength) — a goal is implicitly always MUST (user decision). No `Level` class/validator in `gol/models/v1/body.py`.
- Structured cross-reference validation for the `Related Artifacts` sub-lists (typed id validation, format checks like `GOL-NNNN:`) — v1 keeps all four sub-lists as opaque free text, matching REQ's own precedent.
- ADR-style granular `update_section`/option-style per-field mutation tools — `update_gol` is a single whole-body replace tool, like `update_req`/`update_prb`.
- Real implementation of `delete_gol` — stub only, matching the other five domains' own `delete_*` stubs.
- A `specmgr gol-toc`-equivalent generation command or a dedicated CI/pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` already provide generically.
- Changes to `req`'s schema or data — REQ's existing `### Goals` cross-reference sub-list stays as-is (already anticipates this artifact type).

**Dependencies**:
- Depends on: ADR ece4554b (domain-first), ADR bc5e18ad (generic `MarkdownFrontmatter` base), ADR ddfb1109 (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR ec9f5262 (`list_<domain>` as a paged tool, not a resource — `list_gol` must follow this from day one), the existing `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and `general/models/{DocSummary,PagedResult}` infrastructure, the existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`, `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`, `MarkdownListItem`, `@alias`) — reused as-is, no engine changes anticipated.
- Blocks: None identified.
- Related: issue #15 "Add artifact type Risk" (open) — another sibling domain that will follow the same pattern.

Hmm, should I mention Risk? It's a related but independent feature. It's fine to mention it in a "Related, but explicitly out of scope here" fashion. Keep it light.

**Design Notes**:

**Schema:**

```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}
  (REQ's exact 7-value set -- goals are business-level requirements, so
  requirement-lifecycle semantics apply)

Goal(MarkdownSection1)                          # H1, free-form title (alias ".+")
├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)
├── description: Description | None             # optional H2 "Description", opaque free-text leaf
├── priority: Priority | None                   # optional H2 "Priority", 0-99 single-line value + optional comment
├── tags: Tags | None                           # optional H2 "Tags", bullet list
├── source: Source                              # mandatory H2 "Source", single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
│   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. "REQ-9687: ...")
│   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. "DEC-2703: ...")
│   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. "GOL-0007: ...")
│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free-text leaf
└── notes: Notes | None                         # optional H2 "Notes", opaque free-text leaf
```

- **No `Characteristics`, no `Level`** (see Scope): a goal is implicitly always MUST. `Priority` is the only remaining quantified attribute, and it keeps REQ's `MarkdownSection2WithComment` + `field_validator`-on-`value.text` pattern (re-declared in `gol/models/v1/body.py` — no cross-domain imports, matching every existing domain).
- `Description`/`Source`/`MoreInformation`/`Notes` are bare opaque leaf subclasses (no declared fields) — same pattern as PRB's leaves.
- The four `RelatedArtifacts` sub-list classes are `MarkdownSection3` with `items: list[MarkdownListItem] = Field(min_length=1)` — a 1:1 re-declaration of REQ's own four classes (the heading names "Requirements"/"Decisions"/"Goals"/"Acceptance Criteria" derive implicitly via the `AliasType.SPACE_SEPARATED` convention, so no explicit `@alias` needed — same as REQ).

Wait, let me verify: REQ's `Requirements`/`Decisions`/`Goals`/`AcceptanceCriteria` classes — do they use an explicit @alias? Looking at req body.py: the class names are `Requirements(MarkdownSection3)` — "Requirements" → "Requirements" (single word, no spaces). `Decisions` → "Decisions". `Goals` → "Goals". `AcceptanceCriteria` → "Acceptance Criteria" via SPACE_SEPARATED. Yes, no explicit @alias in REQ. Good, same for GOL.

And `Priority(MarkdownSection2WithComment)` — class name "Priority" → "Priority", no alias needed. `Level` likewise (not used here).

- **Mandatory fields: `statement` + `Source`** — a freshly created `gol` document may have zero optional sections yet, but must always carry the goal statement and its source.

Hmm wait — is `source` really mandatory? The user's answer to my question #1 was "REQ minus Characteristics (recommended)," which kept source mandatory. Then they only removed Level. So yes: statement + source mandatory.

- **`Related Artifacts` is entirely optional** and so are all four sub-lists — mirroring REQ exactly (no consistency check between sub-lists). Cross-reference id format (e.g. `GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) is conventional text only, not validated.

- **Update mechanism: whole-body `update_gol(id, content)`**, not ADR-style `update_section` (ADR 71fd95d7 is ADR-specific code. Same decision as feat-16).

- **`list_gol` is a paged tool from day one** (`@mcp.tool(name="list_gol")` returning `PagedResult[GolSummary]` via `general/tools/_paging.py`'s `paginate`/`normalize_paging`), not a `specmgr://gol/list` resource — per ADR ec9f5262, GOL is a new domain built after that ADR was accepted, so it must not repeat the resource-then-convert history. `GolSummary` subclasses `general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`), like `ReqSummary`/`PrbSummary`.

- **Prompts are narrated instructions only** (return a string. Auto-wrapped as a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call tools themselves.

  - `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol` first to check for an existing, similar goal (mirroring `create_req`'s dedup-check pattern), asking the user via `question` if a near-duplicate is found. (2) build a `TodoWrite` list with one entry per `statement` + optional `Description`/`Priority`/`Tags` + `Source` + optional `Related Artifacts`/`More Information`/`Notes`. (3) use the `question` tool to elicit the goal statement and source (both mandatory) and each optional field, explicitly allowing skips. (4) assemble the full body markdown per the fixed schema above, referencing the packaged `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`. (5) call `create_gol(content)`.
  - `update_gol(id: str) -> str`: instructs the LLM to (1) call `get_gol(id)` first (never assume prior state). (2) show the user which sections are present and elicit revisions via `question` for each the user selects. (3) call `update_gol(id, content)` (whole-body replace, carrying forward every unchanged section). (4) mention `set_status_gol` as a separate, optional follow-up (e.g. `implemented` once the goal has genuinely been reached...

Hmm wait, "implemented" for a goal? REQ's 7-value set includes `implemented` because requirements track implementation beyond acceptance. For a goal, reaching the goal would be... The user chose REQ's 7-value set, so the semantics are: `draft` = being written. `proposed` = under consideration. `accepted` = agreed to pursue. `superseded` = replaced by another goal. `deprecated` = no longer pursued but kept for reference. `rejected` = not pursued. `implemented` = goal reached/achieved. The status semantics should be spelled out in Design Notes: mirror REQ's wording with goal-specific semantics: `implemented` = goal reached (all realizing requirements done).

- **Frontmatter status** (`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented`) is REQ's exact 7-value closed set (`GolFrontmatter` re-declares its own `_ALLOWED_STATUSES` frozenset, same as `ReqFrontmatter`/`TskFrontmatter` each declare their own), with goal-specific semantics: `draft` = being written. `proposed` = under consideration. `accepted` = agreed to pursue. `implemented` = goal reached. `superseded` = replaced by another goal. `deprecated` = no longer pursued, kept for reference. `rejected` = considered and not pursued.

- **Example document**: `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal `req_example.md`'s `### Goals` sub-list already cross-references — so the two packaged examples read coherently side by side. (Same "reference doubles as example" precedent as feat-16, where `prb_example.md` reused `prb_reference.md` verbatim.)

**Related ADRs**: same five as feat-16:
- ece4554b-725c-4f76-bc04-5d2b760363d2: domain-first hierarchy
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: generic base frontmatter
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: id-based reads as tools (`get_gol`), not resources
- ec9f5262-9912-49d0-903f-fcfb54f28c13: `<domain>_list` as a paged MCP tool (`list_gol`), not a resource — follow from the start
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: generic `update_section` — reviewed and explicitly *not* reused for `gol` (see Design Notes)

No new ADR is anticipated for this feature.

**Task List** (5 phases, all not-started, mirroring feat-16's task shape):

#### Phase 1: Specification
- [ ] Task 1.1: Write a full reference `gol_reference.md` (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field (`statement`, all optional sections present: `Description`/`Priority`/`Tags`/`Source`/`Related Artifacts` with all four sub-lists/`More Information`/`Notes`) — depends on: none — status: not-started
- [ ] Task 1.2: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` — `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["gol"]`, 7-value status set identical to `ReqFrontmatter`'s) — depends on: none — status: not-started
- [ ] Task 1.3: Define `gol` body structure (`gol/models/v1/body.py`) — `Goal(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`, mandatory `statement: MarkdownParagraph` + `source: Source`, optional `description`/`priority`/`tags`/`related_artifacts`/`more_information`/`notes` — `Priority` re-declares REQ's `MarkdownSection2WithComment` + `field_validator` pattern. `RelatedArtifacts(MarkdownSection2)` with four optional `MarkdownSection3` sub-lists — depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` — structural + validation tests mirroring `tests/req/models/v1/`/`tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field combinations — depends on: Task 1.3 — status: not-started
- [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality gate (ruff format/check, vulture, full `unittest` suite). Confirm `gol_reference.md` is `specmgr mdformat`-clean. Update this README's Progress section. Add any new vulture-invisible Pydantic field names to `whitelist.py` if needed — depends on: Task 1.1, Task 1.4 — status: not-started

#### Phase 2: Pydantic Models, Parser & Schema
- [ ] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status: not-started
- [ ] Task 2.2: Implement `parse_gol(text: str) -> GolDocument` (model-layer function, mirrors `parse_req`) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.3: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`, for `list_gol`) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/optional field (schema-quality parity with REQ/PRB) — depends on: Task 2.1 — status: not-started
- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py` (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`) + register `"gol"` in the `specmgr schema` doc-type generator registry (`_GENERATORS`). Draft `docs/gol_schema.json` — depends on: Task 2.1 — status: not-started
- [ ] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors `TestParseReq`'s shape (minimal document, full reference document round-trip, default when absent, invalid status, missing-mandatory-section `AssertionError` (`statement`/`Source`), invalid-field `ValidationError` (e.g. out-of-range `Priority` value)) — depends on: Task 2.2, Task 2.5 — status: not-started
- [ ] Task 2.7: Phase-end quality gate — full pre-commit/quality gate including Task 2.6's new tests. Update this README's Progress section — depends on: Task 2.5, Task 2.6 — status: not-started

#### Phase 3: MCP Surface
- [ ] Task 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/`prb/tools/` exactly) — depends on: Task 2.2 — status: not-started
- [ ] Task 3.2: `parse_gol(path: str) -> GolDocument` tool wrapper (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.3: `create_gol(content: str) -> GolDocument` tool (body-only content. MCP builds the frontmatter: `id`, `type="gol"`, `status="draft"`, `created=updated=now`, `version`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.4: `update_gol(id, content) -> GolDocument` tool (whole-body replace, preserving `id`/`type`/`status`/`created`/`version`, bumping `updated`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.5: `set_status_gol(id, status) -> GolDocument` tool (the only path that changes `status`. Reconstructs `GolFrontmatter` via its own constructor so the 7-value validator runs, mirroring `set_status_req`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.6: `delete_gol(id) -> NoReturn` stub tool — depends on: Task 3.1 — status: not-started
- [ ] Task 3.7: `validate_gol(content, full=False) -> bool` tool — depends on: none — status: not-started
- [ ] Task 3.8: `get_gol(id) -> GolDocument` tool (id-based single-document read. A tool, not a resource) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.9: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]` tool, via `general/tools/_paging.py` (default page size 25, cap 100), preserving the standard skip-malformed-file scan behavior — depends on: Task 2.3, Task 3.1 — status: not-started
- [ ] Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` — `req_template.md` mirrored minus `Characteristics`/`Level`) via `general/tools/_packaged_data.py` — depends on: Task 1.1 — status: not-started
- [ ] Task 3.11: `gol/resources/{gol_schema,gol_example,gol_template}.py` — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`), `specmgr://gol/example`, `specmgr://gol/template` (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status: not-started
- [ ] Task 3.12: `pyproject.toml` package-data entry for `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`). `.pre-commit-config.yaml` — widen the shared schema-hook glob to include `gol/models/v1`, add a `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status: not-started
- [ ] Task 3.13: `.github/workflows/ci.yml` — add the `docs/gol_schema.json` check + packaged-copy check steps — depends on: Task 2.5 — status: not-started
- [ ] Task 3.14: `gol/data/gol_create_instructions.md` + `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template` substitution, narrating the full interview flow — see Design Notes) — depends on: Tasks 3.3, 3.9 — status: not-started
- [ ] Task 3.15: `gol/data/gol_update_instructions.md` + `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status: not-started
- [ ] Task 3.16: `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`), and update its module docstring (Tools/Resources/Prompts sections) — depends on: Tasks 3.2–3.15 — status: not-started
- [ ] Task 3.17: `tests/gol/tools/...`, `tests/gol/resources/...`, `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout, including live end-to-end coverage of `create_gol`/`update_gol`'s narrated flow (ACC-006) and `list_gol`'s paging behavior — depends on: Tasks 3.1–3.16 — status: not-started
- [ ] Task 3.18: Phase-end quality gate — full pre-commit/quality gate including Task 3.17's new tests. Update this README's Progress section — depends on: Task 3.17 — status: not-started

#### Phase 4: Cross-cutting registration
- [ ] Task 4.1: `AGENTS.md` — update heading to "eight domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)". Add a `gol/` bullet (in chronological order, after `prb/`). Update the "Still genuinely missing" list (`validate_gol` not enforced via pre-commit/CI, `delete_gol` stub) and the closing domain-enumeration paragraphs — depends on: Phase 3 complete — status: not-started
- [ ] Task 4.2: Regenerate `specmgr docs` / `specmgr mcp-docs` / `specmgr schema` — confirm `gol` appears correctly and all three commands report zero drift — depends on: Task 4.1 — status: not-started
- [ ] Task 4.3: Phase-end quality gate — full pre-commit/quality gate. Update this README's Progress section — depends on: Task 4.2 — status: not-started

#### Phase 5: Final cross-cutting verification
- [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and confirm each is satisfied with concrete evidence (including a live `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests). Run the full quality gate end-to-end. Set feature status to `done` — depends on: Phases 1–4 complete — status: not-started

**Progress**:
- Current Status: **As of 2026-08-25**: planning complete (GitHub issue #18 filed, schema/surface decisions made in the planning session). Implementation not started — Phase 1 next.
- Blockers: None.
- Recent Updates: one entry (planning) — Completed: GitHub issue #18 filed ("Add artifact type Goal (GOL)"). Full design/planning discussion — schema shape (REQ mirrored minus `Characteristics` and minus `Level`), status set (REQ's 7-value), related-artifact sub-lists (all four), update mechanism, prompt behavior, MCP surface all decided. This README written from that discussion. Next: Phase 1 (Specification) — write `gol_reference.md`, define frontmatter/body models. Notes: planning-only session per explicit user instruction.
- Decisions Made:
  - 2026-08-25: Type abbreviation `gol`, domain-first layout (`gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`, `gol/data/`) — matches REQ/PRB precedent.
  - 2026-08-25: Body mirrors REQ minus `## Characteristics` (ISO 25010 quality characteristics are a requirement-level attribute. Goals stay deliberately free of them).
  - 2026-08-25: No `## Level` section — a goal is implicitly always MUST. RFC 2119 obligation strength is a requirement-level attribute (user decision). Only `statement` and `Source` are mandatory.
  - 2026-08-25: Status set = REQ's exact 7-value set `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented` (goals are high-level business requirements, so requirement-lifecycle semantics apply).
  - 2026-08-25: `Related Artifacts` carries all four sub-lists, identical to REQ (`Requirements`/`Decisions`/`Goals`/`Acceptance Criteria`), each optional, opaque free text — includes a `### Goals` sub-list for peer/superseding goals.
  - 2026-08-25: `update_gol` is a single whole-body replace tool (REQ/PRB convention), not ADR-style `update_section` (ADR 71fd95d7 is ADR-specific code. Same decision as feat-16).
  - 2026-08-25: `list_gol` is a paged tool from day one per ADR ec9f5262 (no resource-then-convert history).
  - 2026-08-25: `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` — the goal `req_example.md`'s `### Goals` sub-list already cross-references, so the two packaged examples read coherently side by side.
  - 2026-08-25: Folder name `feat-18-goal` — GitHub issue #17 was already consumed by the merged PR for feat-16, so the new issue is #18. Per convention, `id`/folder name must match the issue number.
- Related PRs / Commits:
  - Issue #18: Add artifact type Goal (GOL) — https://github.com/dfch/biz.dfch.SpecMgr/issues/18

Frontmatter: note that feat-16's frontmatter was in alphabetical order: created, id, status, updated, version. The template shows id, version, status, created, updated. feat-16 (the reference to mirror) used alphabetical: created/id/status/updated/version. Hmm, the template is `id, version, status, created, updated`. feat-16's actual file is `created, id, status, updated, version` (alphabetical). Since the user asked to mirror feat-16's structure, I'll use feat-16's ordering. Either is fine, but feat-16's ordering is probably what mdformat or something normalized to... Actually, mdformat doesn't reorder YAML frontmatter. feat-16's file was probably written in alphabetical order. I'll match feat-16: created, id, status, updated, version.

Now — one more consideration: the issue body I created contains `feat-17-goal`. I should edit the issue body to reference `feat-18-goal`. Let me use `gh issue edit 18 --body "..."`.

Then create the folder + README.md.

After writing, should I run `specmgr mdformat` on the README? feat-16's Phase 1 task 1.5 says to confirm the reference doc is mdformat-clean. For the README itself, mdformat may reflow. Let me run it to be safe — it preserves frontmatter. Actually wait: mdformat may reformat the YAML frontmatter keys (it preserves the frontmatter block but doesn't necessarily sort it). Let me just run it on the README after writing and see what happens. If it changes the ordering of the frontmatter keys, I'll reconsider. Actually, specmgr_mdformat is "format a markdown file in place, preserving the YAML frontmatter" — the frontmatter is preserved (not reordered). OK, safe to run.

Also, per the convention: frontmatter `updated` is bumped on every substantive edit — it's created/updated = 2026-08-25, both today. Good.

Let me also double-check the issue body text I submitted — I used escaped backticks `\\\`Goal\\\`` — with shell single quotes... wait, I wrapped --body in double quotes and used `\\\`` inside. Let me see what the issue body actually contains. In bash double quotes, `\\\`` becomes `\`` — i.e. a backslash + backtick? Hmm: inside double quotes, `\\` → `\`, and `` \` `` → `` ` `` (escaped backtick). So `\\\`` = `\\` + `` \` `` → `\` + `` ` `` → `\`` — a literal backslash before each backtick. That would render in the issue body as escaped backticks — actually, in GitHub-flavored markdown, `\`` renders as a literal backtick. Hmm, that's not what I want — I want code formatting.

Let me check the issue body to see how it came out, and fix it if needed. Let me fetch it.

Actually, simpler: let me rewrite the issue body cleanly with a heredoc... but the tool guidance says to avoid echo/cat for file writes. For gh, I can use --body-file. Let me write the body to /tmp/opencode/issue-body.md with the Write tool, then `gh issue edit 18 --body-file /tmp/opencode/issue-body.md`. That also fixes the feat-17 → feat-18 reference.

First let me look at the current body to confirm the escaping mess.




Issue created as **#18**, not 17 — GitHub number 17 was already consumed by the merged PR *"Feat 16 problem statement"* (issues and PRs share the counter). Per the `feat-NNN-slug` convention, the folder must match the actual issue number, so this becomes **`feat-18-goal`**. Let me check the issue body rendered correctly, then fix it (it currently references `feat-17`).



**Tool: bash**

**Input:**
```json
{
  "command": "gh issue view 18 --json body --jq .body"
}
```

**Output:**
```
New markdown artifact type \`Goal\` (abbreviation \`gol\`) for capturing high-level business goals, mirroring the \`req\` domain's schema minus the ISO 25010 \`Characteristics\` section and the \`Level\` section (a goal is implicitly always MUST).

- Body: mandatory \`statement\` + \`source\`; optional \`description\`, \`priority\`, \`tags\`, \`related artifacts\` (all four REQ sub-lists), \`more information\`, \`notes\`
- Frontmatter status: REQ's 7-value set
- Full MCP surface per ADR ece4554b/ec9f5262/ddfb1109: 10 tools (incl. \`list_gol\` as paged tool from day one), 3 resources, 2 narrated prompts, packaged data
- Plan: \`.specmgr/feat/feat-17-goal/README.md\`

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 26.3s)

_Thinking:_

As expected, the backslashes ended up in the body verbatim (in GitHub's Markdown, `\`` is displayed as an escaped literal backtick—ugly). Let's rewrite the body cleanly with --body-file.




The body has stray backslash escapes. Rewriting it cleanly and pointing at the correct folder:



**Tool: write**

**Input:**
```json
{
  "filePath": "/tmp/opencode/issue-18-body.md",
  "content": "New markdown artifact type `Goal` (abbreviation `gol`) for capturing high-level business goals, mirroring the `req` domain's schema minus the ISO 25010 `Characteristics` section and minus the `Level` section (a goal is implicitly always MUST).\n\n- Body: mandatory `statement` + `Source`; optional `Description`, `Priority`, `Tags`, `Related Artifacts` (all four REQ sub-lists), `More Information`, `Notes`\n- Frontmatter status: REQ's 7-value set\n- Full MCP surface per ADR ece4554b/ec9f5262/ddfb1109: 10 tools (incl. `list_gol` as paged tool from day one), 3 resources, 2 narrated prompts, packaged data\n- Plan: `.specmgr/feat/feat-18-goal/README.md`\n"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 22.3s)

_Thinking:_

Let's fix the issue body with the correct folder name (feat-18, not feat-17) and without the escaped backslashes.


**Tool: bash**

**Input:**
```json
{
  "command": "gh issue edit 18 --body-file /tmp/opencode/issue-18-body.md 2>&1 && echo \"OK\""
}
```

**Output:**
```
https://github.com/dfch/biz.dfch.SpecMgr/issues/18
OK

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 250.7s)

_Thinking:_

The Issue body has already been corrected. Next, I'll create the feature folder and write the README. Folder: `.specmgr/feat/feat-18-goal/`, file: `README.md`.

I'll write the complete README following the feat-16 structure. Frontmatter ordering follows feat-16: created, id, status, updated, version (alphabetical order).




Issue #18 body fixed. Now writing the feature plan to disk:



**Tool: write**

**Input:**
```json
{
  "content": "---\ncreated: 2026-08-25\nid: feat-18-goal\nstatus: planning\nupdated: 2026-08-25\nversion: 1.0.0\n---\n\n# Feature: Add artifact type Goal (gol)\n\n## Plan\n\n### Overview\n\nAdd a new markdown artifact type, `Goal` (abbreviation `gol`), for capturing\nhigh-level business goals — the strategic \"what the organization wants to\nachieve\" level that sits above individual requirements. `gol` follows the\ndomain-first hierarchy and MCP surface already established by `req`/`prb`\n(ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and mirrors `req`'s body schema\nwith exactly two deliberate omissions: no `## Characteristics` section (ISO\n25010:2023 quality characteristics are a requirement-level attribute — a\nbusiness goal stays deliberately free of them) and no `## Level` section\n(RFC 2119 obligation strength is implicit — a goal is always a MUST). `req`\nalready anticipates this artifact type: its `## Related Artifacts` →\n`### Goals` cross-reference sub-list (exercised in `req_example.md` as\n`GOL-0007: Competitive Engines in Consumer Vehicles`) points at documents\nof exactly this shape, and `gol_example.md` will be that very goal so the\ntwo packaged examples read coherently side by side. `gol` reuses `req`'s\nwhole-body update convention (not ADR's granular `update_section`\nmechanism) and `req`'s 7-value frontmatter status set.\n\n### Requirements\n\n- REQ-001: Define the `gol` markdown schema — frontmatter (`type=\"gol\"`,\n  7-value status set `draft`/`proposed`/`accepted`/`superseded`/\n  `deprecated`/`rejected`/`implemented`, `req`'s exact set) and body (H1\n  title, mandatory `statement` lead paragraph, optional `## Description`,\n  optional `## Priority`, optional `## Tags`, mandatory `## Source`,\n  optional `## Related Artifacts` holding four optional, fixed-heading\n  `### ` cross-reference sub-lists — `Requirements`/`Decisions`/`Goals`/\n  `Acceptance Criteria` — optional `## More Information`, optional\n  `## Notes`). No `## Characteristics` and no `## Level` (see Design\n  Notes).\n- REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body,\n  document, parser, summary), domain-first, mirroring `req`/`prb`'s exact\n  file shapes. No `models/md` engine changes are needed — every field is\n  buildable with the existing declarative heading-mapped parser.\n- REQ-003: Parse/validate `gol` documents from markdown, mirroring\n  `parse_req`/`parse_prb`'s two-error-channel convention\n  (`AssertionError` for structural problems, `pydantic.ValidationError`\n  for field-level problems).\n- REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, **plus**\n  `list_gol` as a paged tool from day one (per ADR\n  ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a\n  `specmgr://gol/list` resource and convert it later): `parse_gol`,\n  `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub),\n  `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`,\n  `list_gol`.\n- REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template`\n  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based\n  reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).\n- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,\n  `TodoWrite` + `question`-tool-driven interview flows reusing the\n  dedup-check-first pattern from `req/prompts/create_req.py` and the\n  `TodoWrite`/`question`-tool narration pattern from\n  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use\n  their own packaged instructions data file (`gol/data/gol_create_\n  instructions.md`/`gol_update_instructions.md`), not an inline string.\n- REQ-007: Packaged example/template/schema data (`gol/data/`) via the\n  existing generic `general/tools/_packaged_data.py`, with the matching\n  `pyproject.toml` package-data entry, pre-commit hook, and CI step.\n- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new\n  `gol` entry in the doc-type registry, `commands/schema.py`),\n  `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`\n  updated to eight domain/cross-cutting packages.\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`,\n  `specmgr://gol/schema`); a reference `gol_reference.md` exercising every\n  field (`statement`, `Source` plus all optional sections present,\n  `Related Artifacts` with all four sub-lists) round-trips through the\n  parser.\n- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory\n  (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`,\n  `Related Artifacts` and each of its four sub-lists, `More Information`,\n  `Notes`) fields correctly; `GolFrontmatter.status` rejects any value\n  outside the seven-value set.\n- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a\n  well-formed document; missing the `statement` lead paragraph or the\n  `Source` section raises `AssertionError`; an invalid field value (e.g. a\n  `Priority` outside 0–99, an out-of-set `status`) raises\n  `pydantic.ValidationError`.\n- [ ] ACC-004: Verifies REQ-004 — every listed tool is implemented,\n  registered, and callable; `list_gol` returns a `PagedResult[GolSummary]`\n  with default page size 25 / cap 100, mirroring the other five domains'\n  `list_<d>` tools exactly (no resource-first-then-converted history for\n  this domain).\n- [ ] ACC-005: Verifies REQ-005 — every listed resource is implemented and\n  registered (no `/{id}`, no `/list`, as designed).\n- [ ] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate:\n  (a) a duplicate/similar-document check via `list_gol` first, (b) building\n  a `TodoWrite` list covering `statement` + `Source` + each optional\n  section, (c) using the `question` tool to elicit each field (explicitly\n  allowing skip for optional ones), (d) calling `create_gol(content)`/\n  `update_gol(id, content)` (whole-body) at the end — verified live by\n  reading both packaged instruction files in full and manually walking the\n  narrated flows end to end against a real document, not just asserting\n  their static text.\n- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a\n  real, non-editable install (`uv build --wheel` + scratch-venv install),\n  mirroring feat-16's ACC-007 verification.\n- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/\n  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`\n  reflects eight domain/cross-cutting packages.\n\n### Scope\n\n**Included in this feature:**\n\n- The `gol` markdown schema, Pydantic models, parser, and summary under\n  `gol/models/v1/`.\n- Full MCP surface (tools/resources/prompts/packaged data), including\n  `list_gol` as a tool (not a resource) from the start.\n- The interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` +\n  `question`-tool-driven interview).\n- Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.\n- Cross-cutting registration (`server.py`, `pyproject.toml`,\n  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).\n\n**Explicitly out of scope:**\n\n- A `## Characteristics` section (ISO 25010:2023 quality attributes).\n  Quality characteristics are a requirement-level attribute — a business\n  goal states *what* to achieve, not *which quality dimension* it loads\n  (user decision, planning session 2026-08-25).\n- A `## Level` section (RFC 2119 obligation strength). A goal is\n  implicitly always a MUST — obligation grading applies to requirements\n  below it, not to the goal itself (user decision, planning session\n  2026-08-25).\n- Structured cross-referencing/validation of the `Related Artifacts`\n  sub-lists (typed id validation, `GOL-NNNN:`-style format checks,\n  existence checks against the other domains' base directories) — v1 keeps\n  all four sub-lists as opaque free text, matching `req`'s own precedent.\n  Revisit only if a concrete need emerges.\n- ADR-style granular `update_section`/option-style per-field mutation\n  tools — `update_gol` is a single whole-body replace tool, like\n  `update_req`/`update_prb`. Individual sections stay addressable by their\n  fixed heading text within the markdown body itself, not via a dedicated\n  tool per section.\n- Real implementation of `delete_gol` — a stub raising\n  `NotImplementedError`, matching the other five domains' `delete_*` stubs\n  (a shared, cross-domain decision deferred to future work).\n- Any changes to `req`'s schema, data, or tools — REQ's existing\n  `### Goals` cross-reference sub-list already anticipates this artifact\n  type and needs no modification.\n- A `specmgr gol-toc`-equivalent generation command or dedicated CI/\n  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/\n  `specmgr schema` already provide generically.\n\n### Dependencies\n\n- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic\n  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614\n  (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR\n  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,\n  not a resource — `list_gol` must follow this from day one), the existing\n  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and\n  `general/models/{DocSummary,PagedResult}` infrastructure, and the\n  existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`,\n  `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`,\n  `MarkdownListItem`, `@alias`) — reused as-is, no engine changes\n  anticipated.\n- Blocks: None identified yet.\n- Related, but explicitly out of scope here: issue #15 \"Add artifact type\n  Risk\" (open) — a sibling domain that will follow the same pattern\n  independently.\n\n### Design Notes\n\n**Schema:**\n\n```\nGolFrontmatter(MarkdownFrontmatter): type: Literal[\"gol\"];\n  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}\n  (req's exact 7-value set -- goals are business-level requirements, so\n   requirement-lifecycle semantics apply)\n\nGoal(MarkdownSection1)                          # H1, free-form title (@alias \".+\" REGEX)\n├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)\n├── description: Description | None             # optional H2 \"Description\", opaque free text leaf\n├── priority: Priority | None                   # optional H2 \"Priority\", 0-99 single-line value + optional comment\n├── tags: Tags | None                           # optional H2 \"Tags\", bullet list\n├── source: Source                              # mandatory H2 \"Source\", single-line value\n├── related_artifacts: RelatedArtifacts | None  # optional H2 \"Related Artifacts\"\n│   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. \"REQ-9687: ...\")\n│   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. \"DEC-2703: ...\")\n│   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. \"GOL-0007: ...\")\n│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. \"ACC-1234: ...\")\n├── more_information: MoreInformation | None    # optional H2 \"More Information\", opaque free text leaf\n└── notes: Notes | None                         # optional H2 \"Notes\", opaque free text leaf\n```\n\n**No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —\nboth are deliberate, domain-driven omissions, not oversights: ISO 25010\nquality characteristics grade *requirements*, and RFC 2119 obligation\nstrength is implicit (a goal is always a MUST). Consequently the only\nmandatory body fields are `statement` and `Source`; a freshly created\n`gol` document may have zero optional sections yet (all deferred to a later\n`update_gol` call) but must always carry the goal statement and its source.\n\n**`Priority` keeps `req`'s `MarkdownSection2WithComment` +\n`field_validator`-on-`value.text` pattern** (0–99, no leading zeros other\nthan \"0\" itself), re-declared in `gol/models/v1/body.py` — domain packages\nnever import model classes from each other (verified: no cross-domain\nimports exist in `src/`), so `req`'s `Priority`/`Level` classes are\n*pattern* precedents, not shared code. `Description`/`Source`/\n`MoreInformation`/`Notes` are bare opaque leaf subclasses with no further\ndeclared fields — the same pattern verified for REQ's `MoreInformation`/\n`Notes` and PRB's leaves.\n\n**The four `RelatedArtifacts` sub-lists are 1:1 re-declarations of REQ's\nown four classes**: `MarkdownSection3` with\n`items: list[MarkdownListItem] = Field(min_length=1)`; heading text\n(\"Requirements\"/\"Decisions\"/\"Goals\"/\"Acceptance Criteria\") derives\nimplicitly via the `AliasType.SPACE_SEPARATED` convention (multi-word\n`AcceptanceCriteria` → \"Acceptance Criteria\"), so no explicit `@alias` is\nneeded — exactly as in `req/models/v1/body.py`. All four sub-lists are\noptional, as is `Related Artifacts` as a whole, and no consistency check\nis enforced between them (REQ precedent). Cross-reference id formats\n(`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text\nonly — not validated in v1. The `### Goals` sub-list includes goals for\ncross-referencing peer/superseding goals (self-referencing is allowed; the\nparser does not special-case a document's own id).\n\n**Update mechanism: whole-body `update_gol(id, content)`**, not an\nADR-style `update_section`. The generic `adr/tools/update_section.py`\nmechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently\nADR-specific code, not a shared cross-domain component — the same decision\nas feat-16's for `prb`. Individual sections stay addressable by grepping/\nediting their fixed heading text within the whole-body markdown.\n\n**`list_gol` is a paged tool from day one** (`@mcp.tool(name=\"list_gol\")`\nreturning `PagedResult[GolSummary]`, via `general/tools/_paging.py`'s\n`paginate`/`normalize_paging`, default page size 25 / cap 100), not a\n`specmgr://gol/list` resource — GOL is a new domain built *after* ADR\nec9f5262 was accepted, so it must not repeat the resource-then-convert\nhistory of REQ/UC/TSK/QA/PRB (feat-13). `GolSummary` subclasses\n`general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`),\nlike `ReqSummary`/`PrbSummary`; `title` is the body's H1 text.\n\n**Prompts are narrated instructions only** (return a string, auto-wrapped\nas a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call\n`TodoWrite`/`question`/`get_gol`/`create_gol`/`update_gol` themselves; they\nonly narrate that the calling LLM should. This is the same contract every\nexisting prompt in this codebase already follows\n(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).\n\n- `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol`\n  first to check for an existing, similar goal (mirrors `create_req`'s\n  dedup-check pattern) and ask the user via `question` if a near-duplicate\n  is found; (2) build a `TodoWrite` list with one entry per `statement` +\n  `Source` + each optional section (`Description`/`Priority`/`Tags`/\n  `Related Artifacts`/`More Information`/`Notes`); (3) use the `question`\n  tool to elicit the goal statement (mandatory) and the source (mandatory)\n  plus each optional field in turn, explicitly allowing the user to skip\n  any optional one; (4) reference the packaged\n  `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`\n  for the fixed structure; (5) assemble the full body markdown per the\n  schema above and call `create_gol(content)`.\n- `update_gol(id: str) -> str`: instructs the LLM to (1) call\n  `get_gol(id)` first (never assume prior state); (2) show the user which\n  sections are already present and which are empty, and ask via\n  `question` which ones (if any) they want to add or revise; (3) for each\n  selected section, elicit the new/revised text via `question`; (4) call\n  `update_gol(id, content)` (whole-body replace, carrying forward every\n  unchanged section); (5) mention `set_status_gol` as a separate, optional\n  follow-up (e.g. `implemented` once the goal has genuinely been reached,\n  `rejected`/`superseded` if abandoned or replaced).\n\nBoth prompts' instructional text lives in packaged data files\n(`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`, read\nvia `general.tools._packaged_data.read_packaged_text`, `string.Template`\nsubstitution), matching `req_create_instructions.md`/\n`prb_create_instructions.md`'s precedent — not an inline Python string.\n\n**Frontmatter status** is REQ's exact 7-value closed set\n(`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/\n`implemented`), re-declared as `GolFrontmatter`'s own `_ALLOWED_STATUSES`\nfrozenset (each domain declares its own set — `ReqFrontmatter`,\n`TskFrontmatter`, `PrbFrontmatter` all do), with goal-specific semantics:\n`draft` = still being written; `proposed` = under consideration;\n`accepted` = agreed to be pursued; `implemented` = the goal has genuinely\nbeen reached; `superseded` = replaced by another goal; `deprecated` = no\nlonger pursued, kept for reference; `rejected` = considered and not\npursued.\n\n**Example/template documents:** `gol_example.md` is drafted as\n`GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal\n`req_example.md`'s `### Goals` sub-list already cross-references — so the\ntwo packaged examples read coherently side by side; it reuses\n`gol_reference.md`'s content verbatim (feat-16's own precedent:\n`prb_example.md` reuses `prb_reference.md`). `gol_template.md` mirrors\n`req_template.md` minus the `Characteristics` and `Level` sections, with\ngoal-oriented placeholder prose.\n\n### Related ADRs\n\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by\n  document-type domain (domain-first hierarchy)\n- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for\n  markdown document types\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool\n  (`get_gol`), not a resource\n- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged\n  MCP tool (`list_gol`), not a resource — must be followed from the start\n  for this new domain, not retrofitted later\n- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed\n  and explicitly *not* reused for `gol` (see Design Notes)\n\nNo new ADR is anticipated for this feature — every schema/tooling decision\neither follows an existing ADR's precedent directly or is scoped enough to\nlog only in this file's own Decisions Made.\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself. Each phase ends with a mandatory phase-end task (tests, full\nquality gate, README Progress update), mirroring feat-16's per-phase\ncommit discipline, since implementation is likely to span multiple\nsessions.\n\n#### Phase 1: Specification\n\n- [ ] Task 1.1: Write a full reference `gol_reference.md`\n  (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field\n  (`statement`, `Source`, plus all optional sections present:\n  `Description`/`Priority`/`Tags`/`Related Artifacts` with all four\n  sub-lists/`More Information`/`Notes`) — depends on: none — status:\n  not-started\n- [ ] Task 1.2: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` —\n  `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal[\"gol\"]`,\n  7-value status set identical to `ReqFrontmatter`'s) — depends on: none —\n  status: not-started\n- [ ] Task 1.3: Define `gol` body structure (`gol/models/v1/body.py`) —\n  `Goal(MarkdownSection1)` with `@alias(value=\".+\", type=AliasType.REGEX)`,\n  mandatory `statement: MarkdownParagraph` + `source: Source`, optional\n  `description`/`priority`/`tags`/`related_artifacts`/`more_information`/\n  `notes`; `Priority` re-declares REQ's `MarkdownSection2WithComment` +\n  `field_validator` pattern (0–99); `RelatedArtifacts(MarkdownSection2)`\n  with four optional `MarkdownSection3` sub-lists (see Design Notes) —\n  depends on: Task 1.2 — status: not-started\n- [ ] Task 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` —\n  structural + validation tests mirroring `tests/req/models/v1/`/\n  `tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field\n  combinations (each optional section individually absent/present; each of\n  the four `Related Artifacts` sub-lists individually absent/present) —\n  depends on: Task 1.3 — status: not-started\n- [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality\n  gate (ruff format/check, vulture, full `unittest` suite); confirm\n  `gol_reference.md` is `specmgr mdformat`-clean; add any new\n  vulture-invisible Pydantic field names to `whitelist.py` if needed;\n  update this README's Progress section — depends on: Task 1.1, Task 1.4 —\n  status: not-started\n\n#### Phase 2: Pydantic Models, Parser & Schema\n\n- [ ] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter,\n  body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:\n  not-started\n- [ ] Task 2.2: Implement `parse_gol(text: str) -> GolDocument` (model-layer\n  function, mirrors `parse_req`) — depends on: Task 2.1 — status:\n  not-started\n- [ ] Task 2.3: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`,\n  subclassing `general/models/summary.py::DocSummary`, for `list_gol`) —\n  depends on: Task 2.1 — status: not-started\n- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/\n  optional field (schema-quality parity with REQ/PRB) — depends on:\n  Task 2.1 — status: not-started\n- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`\n  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)\n  + register `\"gol\"` in the `specmgr schema` doc-type generator registry\n  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —\n  status: not-started\n- [ ] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors\n  `TestParseReq`'s shape (minimal doc, full reference-doc round-trip,\n  defaults-when-absent, invalid status, missing-mandatory-field\n  `AssertionError` cases (`statement`, `Source`), invalid-field\n  `ValidationError` (e.g. `Priority` out of 0–99 range, invalid `type`\n  field)) — depends on: Task 2.2, Task 2.5 — status: not-started\n- [ ] Task 2.7: Phase-end quality gate — full pre-commit/quality gate\n  including Task 2.6's new tests; update this README's Progress section —\n  depends on: Task 2.5, Task 2.6 — status: not-started\n\n#### Phase 3: MCP Surface\n\n- [ ] Task 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin\n  wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/\n  `prb/tools/` exactly) — depends on: Task 2.2 — status: not-started\n- [ ] Task 3.2: `parse_gol(path: str) -> GolDocument` tool wrapper\n  (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.3: `create_gol(content: str) -> GolDocument` tool (body-only\n  content; MCP builds frontmatter: `id`, `type=\"gol\"`, `status=\"draft\"`,\n  `created=updated=now`, `version`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: `update_gol(id, content) -> GolDocument` tool (whole-body\n  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps\n  `updated`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: `set_status_gol(id, status) -> GolDocument` tool (only path\n  that changes `status`; reconstructs `GolFrontmatter` via its own\n  constructor so the 7-value validator runs, mirroring `set_status_req`) —\n  depends on: Task 3.1 — status: not-started\n- [ ] Task 3.6: `delete_gol(id) -> NoReturn` stub tool — depends on: Task\n  3.1 — status: not-started\n- [ ] Task 3.7: `validate_gol(content, full=False) -> bool` tool — depends\n  on: none — status: not-started\n- [ ] Task 3.8: `get_gol(id) -> GolDocument` tool (id-based single-document\n  read; tool, not resource) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.9: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]`\n  tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`\n  (default page size 25, cap 100), preserving the standard skip-malformed-\n  file scan behavior — depends on: Task 2.3, Task 3.1 — status: not-started\n- [ ] Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data\n  (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in\n  Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —\n  `req_template.md` mirrored minus `Characteristics`/`Level`) via\n  `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:\n  not-started\n- [ ] Task 3.11: `gol/resources/{gol_schema,gol_example,gol_template}.py`\n  — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`, mirroring\n  `specmgr://req/schema`), `specmgr://gol/example`, `specmgr://gol/template`\n  (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:\n  not-started\n- [ ] Task 3.12: `pyproject.toml` package-data entry for\n  `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`\n  — widen the shared schema-hook glob to include `gol/models/v1`, add a\n  `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.13: `.github/workflows/ci.yml` — add the `docs/gol_schema.json`\n  check + packaged-copy check steps — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.14: `gol/data/gol_create_instructions.md` +\n  `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template`\n  substitution, narrates the full interview flow — see Design Notes) —\n  depends on: Tasks 3.3, 3.9 — status: not-started\n- [ ] Task 3.15: `gol/data/gol_update_instructions.md` +\n  `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:\n  not-started\n- [ ] Task 3.16: `gol/__init__.py` (docstring + `from . import prompts,\n  resources, tools`), add `gol` to `server.py`'s bottom-of-file domain\n  import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`)\n  and update its module docstring (Tools/Resources/Prompts sections) —\n  depends on: Tasks 3.2-3.15 — status: not-started\n- [ ] Task 3.17: `tests/gol/tools/...`, `tests/gol/resources/...`,\n  `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout,\n  including live end-to-end coverage of `create_gol`/`update_gol`'s\n  narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_gol`'s\n  paging behavior (default page size, `max_results` clamping, `offset`\n  paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:\n  not-started\n- [ ] Task 3.18: Phase-end quality gate — full pre-commit/quality gate\n  including Task 3.17's new tests; update this README's Progress section —\n  depends on: Task 3.17 — status: not-started\n\n#### Phase 4: Cross-cutting registration\n\n- [ ] Task 4.1: `AGENTS.md` — update heading to \"eight domain/cross-cutting\n  packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)\"; add a\n  `gol/` bullet (chronological order, after `prb/`); update the \"Still\n  genuinely missing\" list (`validate_gol` not enforced via pre-commit/CI,\n  `delete_gol` stub) and the closing domain-enumeration paragraphs —\n  depends on: Phase 3 complete — status: not-started\n- [ ] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`\n  regeneration — confirm `gol` appears correctly and all three commands\n  report zero drift — depends on: Task 4.1 — status: not-started\n- [ ] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;\n  update this README's Progress section — depends on: Task 4.2 — status:\n  not-started\n\n#### Phase 5: Final cross-cutting verification\n\n- [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and\n  confirm each is satisfied with concrete evidence (including a live\n  `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests);\n  run the full quality gate (ruff format/check, pylint advisory, vulture,\n  unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift\n  checks) end to end; set feature status to `done` — depends on: Phase\n  1-4 complete — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-25**: Planning complete; implementation not started.\nGitHub issue #18 (\"Add artifact type Goal (GOL)\") is filed and open; all\nschema/surface decisions were made in the planning session and are logged\nbelow. Phase 1 (Specification) is next.\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### Update 2026-08-25 (planning)\n\n- Completed: GitHub issue #18 filed (\"Add artifact type Goal (GOL)\") with a\n  short overview description. Full design/planning discussion — schema\n  shape (REQ mirrored minus `Characteristics` and minus `Level`; mandatory\n  `statement` + `Source` only), status set (REQ's 7-value set), related-\n  artifact sub-lists (all four, identical to REQ), update mechanism\n  (whole-body replace), prompt behavior, and MCP surface (10 tools / 3\n  resources / 2 prompts) all decided; this README written from that\n  discussion.\n- Next: Phase 1 (Specification) — write `gol_reference.md`, define\n  frontmatter/body models.\n- Notes: Planning-only session per explicit user instruction (no\n  implementation attempted). Issue numbering note: GitHub number 17 was\n  already consumed by the merged feat-16 PR, so this feature's issue is\n  #18 and the folder is `feat-18-goal` accordingly (the `feat-NNN-slug`\n  convention ties the folder name to the issue number).\n\n### Decisions Made\n\n- **2026-08-25**: Type abbreviation `gol`, domain-first layout\n  (`gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`,\n  `gol/data/`) — matches REQ/PRB precedent (schema lives inside the domain\n  package, not top-level `models/`), since GOL is a new domain built after\n  the domain-first refactor.\n- **2026-08-25**: Body mirrors REQ minus `## Characteristics` — ISO 25010\n  quality characteristics are a requirement-level attribute; a business\n  goal states *what* to achieve, not *which quality dimension* it loads\n  (user decision).\n- **2026-08-25**: No `## Level` section — a goal is implicitly always a\n  MUST; RFC 2119 obligation strength is a requirement-level attribute\n  (user decision). Consequently the only mandatory body fields are\n  `statement` and `Source`, and `gol/models/v1/body.py` declares no\n  `Level` class or RFC 2119 validator.\n- **2026-08-25**: Status set = REQ's exact 7-value set\n  `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/\n  `implemented` — goals are business-level requirements, so\n  requirement-lifecycle semantics apply (user decision), with goal-specific\n  meanings for `implemented` (= goal reached) and `superseded` (= replaced\n  by another goal) as spelled out in Design Notes.\n- **2026-08-25**: `Related Artifacts` carries all four sub-lists, identical\n  to REQ (`Requirements`/`Decisions`/`Goals`/`Acceptance Criteria`), each\n  optional and opaque free text — the `### Goals` sub-list cross-\n  references peer/superseding goals (user decision).\n- **2026-08-25**: `update_gol` is a single whole-body replace tool\n  (REQ/PRB convention), not an ADR-style `update_section`/option-style\n  granular tool — the latter is currently ADR-specific code (ADR\n  71fd95d7), same decision as feat-16's for `prb`. Individual sections\n  remain addressable by their fixed heading text within the whole-body\n  markdown.\n- **2026-08-25**: `list_gol` is a paged tool from day one per ADR\n  ec9f5262 — no `specmgr://gol/list` resource, no resource-then-convert\n  history.\n- **2026-08-25**: `gol_example.md` is drafted as `GOL-0007: Competitive\n  Engines in Consumer Vehicles` — the exact goal `req_example.md`'s\n  `### Goals` sub-list already cross-references — so the two packaged\n  examples read coherently side by side; it reuses `gol_reference.md`'s\n  content verbatim (feat-16's own `prb_example.md`/`prb_reference.md`\n  precedent).\n- **2026-08-25**: Folder name `feat-18-goal` (issue #18) — GitHub number\n  17 was already consumed by the merged feat-16 PR, so the convention's\n  `feat-NNN-slug` ↔ issue-number tie lands on 18.\n\n### Related PRs / Commits\n\n- [Issue #18](https://github.com/dfch/biz.dfch.SpecMgr/issues/18): Add\n  artifact type Goal (GOL) — the issue this feature implements.\n",
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md"
}
```

**Output:**
```
Wrote file successfully.
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 24.8s)

_Thinking:_

Alright, let's verify:
1. Run `specmgr mdformat` on the README and confirm that it's mdformat-clean (following the project's conventions).
2. Check git status.

Let me try running mdformat on the new README.




Now let me verify the file is `specmgr mdformat`-clean (project convention) and check the final state:



**Tool: specmgr_mdformat**

**Input:**
```json
{
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md"
}
```

**Output:**
```
true
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 25.5s)

_Thinking:_

mdformat made changes (returned True). Let me check what changed — to make sure it's still correct (e.g., whether frontmatter was preserved, whether the schema code block was preserved).




mdformat made changes — let me verify the result is still correct:



**Tool: bash**

**Input:**
```json
{
  "command": "git diff --stat .specmgr/feat/feat-18-goal/README.md 2>/dev/null; head -12 .specmgr/feat/feat-18-goal/README.md; grep -n \"Goal(MarkdownSection1)\\|characteristics\\|Level\" .specmgr/feat/feat-18-goal/README.md | head -10"
}
```

**Output:**
```
---
created: 2026-08-25
id: feat-18-goal
status: planning
updated: 2026-08-25
version: 1.0.0
---

# Feature: Add artifact type Goal (gol)

## Plan

21:25010:2023 quality characteristics are a requirement-level attribute — a
22:business goal stays deliberately free of them) and no `## Level` section
42:  `## Notes`). No `## Characteristics` and no `## Level` (see Design
133:  Quality characteristics are a requirement-level attribute — a business
136:- A `## Level` section (RFC 2119 obligation strength). A goal is
189:Goal(MarkdownSection1)                          # H1, free-form title (@alias ".+" REGEX)
204:**No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —
206:quality characteristics grade *requirements*, and RFC 2119 obligation
216:imports exist in `src/`), so `req`'s `Priority`/`Level` classes are
304:`req_template.md` minus the `Characteristics` and `Level` sections, with

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 25.0s)

_Thinking:_

mdformat preserved the frontmatter and content (since the file is new, git diff --stat doesn't show anything, but this is a new untracked file). The structure is intact. Let me verify that mdformat is idempotent (run it once more to confirm it's clean now), and check the final file statistics.




Content intact. Confirming mdformat idempotency (file now clean):



**Tool: specmgr_mdformat**

**Input:**
```json
{
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md"
}
```

**Output:**
```
false
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 36.6s)

_Thinking:_

Second run returned `false` = no changes → file is currently in a clean state per mdformat.

Summary of what was done:
1. Created GitHub issue #18 (not #17 — #17 had already been used by the merged feat-16 PR). Verified with `gh issue view 17`.
2. Fixed the body of the issue (it had backslash-escape artifacts, and it referenced feat-17).
3. Created `.specmgr/feat/feat-18-goal/README.md` with the full plan, following the feat-16 structure. Includes the revision of "no Level".
4. Ran mdformat → clean.

Done. Now for a concise reply.




Done. Summary:

**GitHub issue:** Created as **#18**, not #17 — number 17 was already consumed by the merged feat-16 PR (`gh issue view 17` → "Feat 16 problem statement", MERGED; issues and PRs share GitHub's counter). Per the `feat-NNN-slug` convention the folder must carry the real issue number, so the feature is **`feat-18-goal`**. I also fixed the issue body (shell-escaping artifacts + stale `feat-17` reference) → https://github.com/dfch/biz.dfch.SpecMgr/issues/18

**Feature written to disk:** `.specmgr/feat/feat-18-goal/README.md`, structured exactly like `feat-16-problem-statement/README.md` (frontmatter `id`/`version`/`status: planning`/`created`/`updated`; Plan → Overview, Requirements REQ-001…008, Acceptance Criteria ACC-001…008, Scope, Dependencies, Design Notes with the full schema tree, Related ADRs, 5-phase Task List all `not-started`; Progress → Current Status, Blockers, Recent Updates, Decisions Made, Related PRs/Commits). Key content:

- Schema = REQ minus `Characteristics` **and** minus `Level` (goal is implicitly always MUST); mandatory body fields are only `statement` + `Source`
- Status = REQ's 7-value set; `Related Artifacts` = all four REQ sub-lists
- Full MCP surface: 10 tools (`list_gol` paged from day one per ADR ec9f5262), 3 resources, 2 narrated prompts, packaged data; `gol_example.md` will be `GOL-0007: Competitive Engines in Consumer Vehicles` (the goal `req_example.md` already cross-references)
- No new ADRs anticipated; the issue-numbering twist is logged in Decisions Made

File is `specmgr mdformat`-clean (verified idempotent). Phase 1 (Specification) is the next step whenever you want to start implementation.

---

## User

anything else to add before we wrap up this session?

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 49.2s)

_Thinking:_

The user is asking whether there's anything else to add before wrapping up this session. Now we're in build mode, so file modifications are permitted. Let me think about what's still missing or worth doing:

1. **The README itself** — done, mdformat clean.
2. **`git status`** — the new file is untracked. Should I stage it? Per instructions, don't commit unless explicitly asked. But staging might be useful… actually the user didn't ask for a commit. Leave it untracked but mention it.
3. **Consistency check on the issue body** — done.
4. **Things that could be added to the feature folder**:
   - `gol_reference.md` — no, that's a Phase 1 task.
   - `history.md` — not needed yet.
5. **Cross-references to update right now?**
   - AGENTS.md — no, that's Phase 4.
   - feat-7's task list (Task 0.24 was about fixing stale wording in AGENTS.md) — out of scope.
   - What about the "Existing feature folders" list in AGENTS.md? It says "Existing feature folders: `.specmgr/feat/feat-9-doc-in-specmgr/`, `.specmgr/feat/feat-4-use-cases/`, `.specmgr/feat/feat-5-md-model-parser/`" — this list is already stale (feat-10, feat-12, feat-13, feat-14, feat-16 exist but aren't listed). That's a pre-existing issue, and feat-16 didn't update it either. Out of scope, but worth mentioning as an observation.

6. **Things worth verifying before wrap-up**:
   - Check the final README content once more (read it back) to make sure mdformat didn't break any code blocks or structure. Let me skim through the whole file.
   - Verify the frontmatter fields are correct.
   - Check the issue body renders correctly.
   - Should I run a quick validation of the feature README against the template's expected structure? There's no such tool.
   
7. **One gap in the plan I noticed**: in Design Notes I wrote that `list_gol`'s title is the body's H1 text — consistent with `list_req` (which uses `doc.body.text`). No problem.

8. **Another gap**: ACC-003 mentions `AssertionError` when `statement` or `Source` is missing — consistent.

9. **Paging/whitelist**: the vulture whitelist note is already in Task 1.5.

10. **Should the "Existing feature folders" list in AGENTS.md or the conventions doc be updated?** No — out of scope for this session (and it's already stale anyway).

11. **Git**: the file is untracked. The pre-commit hook doesn't run until commit. I won't commit unless asked. But I should mention that it's ready to be committed, or offer to commit. The user said "before wrapping up this session" — it's their call. I'll mention it.

12. **One more useful thing**: the issue body says "Plan: `.specmgr/feat/feat-18-goal/README.md`" — good.

13. **Verify the README renders correctly** — let me read back the sections that mdformat changed to make sure nothing is broken (e.g., code fences inside the schema block, list continuation).

To do:
- Read back the entire README (at least skim through it).
- Run git status.
- Then answer: essentially nothing more needed; mention (a) the file is untracked/commit-ready, (b) the pre-existing stale "Existing feature folders" list in AGENTS.md (not something we should fix in this session), (c) optionally I could have added a "Technical Debt" section per issue #2, but… wait — issue #2 is "docs: add a Technical Debt section to the feature template". That's an open issue about the template itself, and our template version is v1 without that. Not our concern.

Actually, one more thing to consider: should I double-check that the feature README's structure matches the template's required sections? Let me diff the headings against the template. Template headings:
- # Feature: [title]
- ## Plan
- ### Overview / Requirements / Acceptance Criteria / Scope / Dependencies / Design Notes / Related ADRs / Task List
- ## Progress
- ### Current Status / Blockers / Recent Updates / Decisions Made / Related PRs / Commits

Mine has all of these. The template's "### Scope" is a single section with "What is included" / "What is explicitly out of scope" — I used bold paragraphs "**Included in this feature:**" / "**Explicitly out of scope:**" same as feat-16. Consistent with the reference. Good.

Let me read the file back and check git status.




Let me do a final review pass before wrapping up — read back the mdformatted README to make sure nothing broke, and check git state.




**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md",
  "limit": 120
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-25
3: id: feat-18-goal
4: status: planning
5: updated: 2026-08-25
6: version: 1.0.0
7: ---
8: 
9: # Feature: Add artifact type Goal (gol)
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Add a new markdown artifact type, `Goal` (abbreviation `gol`), for capturing
16: high-level business goals — the strategic "what the organization wants to
17: achieve" level that sits above individual requirements. `gol` follows the
18: domain-first hierarchy and MCP surface already established by `req`/`prb`
19: (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and mirrors `req`'s body schema
20: with exactly two deliberate omissions: no `## Characteristics` section (ISO
21: 25010:2023 quality characteristics are a requirement-level attribute — a
22: business goal stays deliberately free of them) and no `## Level` section
23: (RFC 2119 obligation strength is implicit — a goal is always a MUST). `req`
24: already anticipates this artifact type: its `## Related Artifacts` →
25: `### Goals` cross-reference sub-list (exercised in `req_example.md` as
26: `GOL-0007: Competitive Engines in Consumer Vehicles`) points at documents
27: of exactly this shape, and `gol_example.md` will be that very goal so the
28: two packaged examples read coherently side by side. `gol` reuses `req`'s
29: whole-body update convention (not ADR's granular `update_section`
30: mechanism) and `req`'s 7-value frontmatter status set.
31: 
32: ### Requirements
33: 
34: - REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`,
35:   7-value status set `draft`/`proposed`/`accepted`/`superseded`/
36:   `deprecated`/`rejected`/`implemented`, `req`'s exact set) and body (H1
37:   title, mandatory `statement` lead paragraph, optional `## Description`,
38:   optional `## Priority`, optional `## Tags`, mandatory `## Source`,
39:   optional `## Related Artifacts` holding four optional, fixed-heading
40:   `### ` cross-reference sub-lists — `Requirements`/`Decisions`/`Goals`/
41:   `Acceptance Criteria` — optional `## More Information`, optional
42:   `## Notes`). No `## Characteristics` and no `## Level` (see Design
43:   Notes).
44: - REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body,
45:   document, parser, summary), domain-first, mirroring `req`/`prb`'s exact
46:   file shapes. No `models/md` engine changes are needed — every field is
47:   buildable with the existing declarative heading-mapped parser.
48: - REQ-003: Parse/validate `gol` documents from markdown, mirroring
49:   `parse_req`/`parse_prb`'s two-error-channel convention
50:   (`AssertionError` for structural problems, `pydantic.ValidationError`
51:   for field-level problems).
52: - REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, **plus**
53:   `list_gol` as a paged tool from day one (per ADR
54:   ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
55:   `specmgr://gol/list` resource and convert it later): `parse_gol`,
56:   `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub),
57:   `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`,
58:   `list_gol`.
59: - REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template`
60:   (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
61:   reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
62: - REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
63:   `TodoWrite` + `question`-tool-driven interview flows reusing the
64:   dedup-check-first pattern from `req/prompts/create_req.py` and the
65:   `TodoWrite`/`question`-tool narration pattern from
66:   `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
67:   their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string.
68: - REQ-007: Packaged example/template/schema data (`gol/data/`) via the
69:   existing generic `general/tools/_packaged_data.py`, with the matching
70:   `pyproject.toml` package-data entry, pre-commit hook, and CI step.
71: - REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
72:   `gol` entry in the doc-type registry, `commands/schema.py`),
73:   `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
74:   updated to eight domain/cross-cutting packages.
75: 
76: ### Acceptance Criteria
77: 
78: - [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`,
79:   `specmgr://gol/schema`); a reference `gol_reference.md` exercising every
80:   field (`statement`, `Source` plus all optional sections present,
81:   `Related Artifacts` with all four sub-lists) round-trips through the
82:   parser.
83: - [ ] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory
84:   (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`,
85:   `Related Artifacts` and each of its four sub-lists, `More Information`,
86:   `Notes`) fields correctly; `GolFrontmatter.status` rejects any value
87:   outside the seven-value set.
88: - [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
89:   well-formed document; missing the `statement` lead paragraph or the
90:   `Source` section raises `AssertionError`; an invalid field value (e.g. a
91:   `Priority` outside 0–99, an out-of-set `status`) raises
92:   `pydantic.ValidationError`.
93: - [ ] ACC-004: Verifies REQ-004 — every listed tool is implemented,
94:   registered, and callable; `list_gol` returns a `PagedResult[GolSummary]`
95:   with default page size 25 / cap 100, mirroring the other five domains'
96:   `list_<d>` tools exactly (no resource-first-then-converted history for
97:   this domain).
98: - [ ] ACC-005: Verifies REQ-005 — every listed resource is implemented and
99:   registered (no `/{id}`, no `/list`, as designed).
100: - [ ] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate:
101:   (a) a duplicate/similar-document check via `list_gol` first, (b) building
102:   a `TodoWrite` list covering `statement` + `Source` + each optional
103:   section, (c) using the `question` tool to elicit each field (explicitly
104:   allowing skip for optional ones), (d) calling `create_gol(content)`/
105:   `update_gol(id, content)` (whole-body) at the end — verified live by
106:   reading both packaged instruction files in full and manually walking the
107:   narrated flows end to end against a real document, not just asserting
108:   their static text.
109: - [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
110:   real, non-editable install (`uv build --wheel` + scratch-venv install),
111:   mirroring feat-16's ACC-007 verification.
112: - [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
113:   `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
114:   reflects eight domain/cross-cutting packages.
115: 
116: ### Scope
117: 
118: **Included in this feature:**
119: 
120: - The `gol` markdown schema, Pydantic models, parser, and summary under

(Showing lines 1-120 of 571. Use offset=121 to continue.)
</content>
```

**Tool: bash**

**Input:**
```json
{
  "command": "git status --short && git diff --stat"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 47.9s)

_Thinking:_

Found one bug introduced by mdformat: line 67 — `` (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`) `` — mdformat split a long line and inserted a space inside the code span: `gol_create_ instructions.md`. This is wrong; the filename is broken. I originally wrote it like this:

```
  their own packaged instructions data file (`gol/data/gol_create_
  instructions.md`/`gol_update_instructions.md`), not an inline string.
```

Wait, did I actually write it that way originally? Let me check what I originally wrote: "Both use their own packaged instructions data file (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`), not an inline string." Hmm, in the original write it was on a single line:

```
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows reusing the
  dedup-check-first pattern from `req/prompts/create_req.py` and the
  `TodoWrite`/`question`-tool narration pattern from
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol/data/gol_create_
  instructions.md`/`gol_update_instructions.md`), not an inline string.
```

No wait. Looking at the original write, line by line:

```
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows reusing the
  dedup-check-first pattern from `req/prompts/create_req.py` and the
  `TodoWrite`/`question`-tool narration pattern from
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol/data/gol_create_
  instructions.md`/`gol_update_instructions.md`), not an inline string.
```

Hmm, in the content I wrote I had: "Both use their own packaged instructions data file (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`), not an inline string." — I think I wrote the full filename on a single line, and that line was too long (over 120 chars?), and mdformat wrapped it by inserting a newline + space inside the code span. Actually, mdformat should normally wrap prose but shouldn't split inline code spans... but looking at the result, it's been split with a space. This is a known mdformat behavior when it re-wraps lines that exceed the width and the code span happens to be at the wrap point — it shouldn't do that... but the evidence (line 67) shows `gol_create_ instructions.md` with a space, and the backtick pair is still intact (a single code span containing the space).

So mdformat corrupted the filename. I need to fix this. Best fix: restructure so that the long code span isn't at a wrap boundary — e.g., shorten the sentence, or split into two separate backtick spans on separate lines.

Also `git status --short` returned no output at all?? That's strange — a new untracked file `.specmgr/feat/feat-18-goal/README.md` should show as `??`. Wait, the bash output was "(no output)" for the whole command. Maybe `.specmgr/` is gitignored? No — AGENTS.md says the `.specmgr/` folder is committed. Hmm, but `git status --short` showed nothing, and `git diff --stat` also showed nothing. Let me check: maybe there's a .gitignore entry? Or the file is... let me re-run git status explicitly.

Actually wait — maybe the command output got swallowed. Let me re-run `git status` and check .gitignore.

Also, I need to scan the rest of the file (lines 120–571) for similar mdformat corruption (other long code spans). Let me read the rest of the file.




Two things need checking: line 67 shows mdformat split a code span mid-filename (`gol_create_ instructions.md`), and `git status` came back suspiciously empty. Let me review the rest of the file and git state.




**Tool: read**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md",
  "offset": 120
}
```

**Output:**
```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md</path>
<type>file</type>
<content>
120: - The `gol` markdown schema, Pydantic models, parser, and summary under
121:   `gol/models/v1/`.
122: - Full MCP surface (tools/resources/prompts/packaged data), including
123:   `list_gol` as a tool (not a resource) from the start.
124: - The interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` +
125:   `question`-tool-driven interview).
126: - Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.
127: - Cross-cutting registration (`server.py`, `pyproject.toml`,
128:   `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).
129: 
130: **Explicitly out of scope:**
131: 
132: - A `## Characteristics` section (ISO 25010:2023 quality attributes).
133:   Quality characteristics are a requirement-level attribute — a business
134:   goal states *what* to achieve, not *which quality dimension* it loads
135:   (user decision, planning session 2026-08-25).
136: - A `## Level` section (RFC 2119 obligation strength). A goal is
137:   implicitly always a MUST — obligation grading applies to requirements
138:   below it, not to the goal itself (user decision, planning session
139:   2026-08-25).
140: - Structured cross-referencing/validation of the `Related Artifacts`
141:   sub-lists (typed id validation, `GOL-NNNN:`-style format checks,
142:   existence checks against the other domains' base directories) — v1 keeps
143:   all four sub-lists as opaque free text, matching `req`'s own precedent.
144:   Revisit only if a concrete need emerges.
145: - ADR-style granular `update_section`/option-style per-field mutation
146:   tools — `update_gol` is a single whole-body replace tool, like
147:   `update_req`/`update_prb`. Individual sections stay addressable by their
148:   fixed heading text within the markdown body itself, not via a dedicated
149:   tool per section.
150: - Real implementation of `delete_gol` — a stub raising
151:   `NotImplementedError`, matching the other five domains' `delete_*` stubs
152:   (a shared, cross-domain decision deferred to future work).
153: - Any changes to `req`'s schema, data, or tools — REQ's existing
154:   `### Goals` cross-reference sub-list already anticipates this artifact
155:   type and needs no modification.
156: - A `specmgr gol-toc`-equivalent generation command or dedicated CI/
157:   pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
158:   `specmgr schema` already provide generically.
159: 
160: ### Dependencies
161: 
162: - Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
163:   hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
164:   `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
165:   (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR
166:   ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
167:   not a resource — `list_gol` must follow this from day one), the existing
168:   `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
169:   `general/models/{DocSummary,PagedResult}` infrastructure, and the
170:   existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`,
171:   `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`,
172:   `MarkdownListItem`, `@alias`) — reused as-is, no engine changes
173:   anticipated.
174: - Blocks: None identified yet.
175: - Related, but explicitly out of scope here: issue #15 "Add artifact type
176:   Risk" (open) — a sibling domain that will follow the same pattern
177:   independently.
178: 
179: ### Design Notes
180: 
181: **Schema:**
182: 
183: ```
184: GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
185:   status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}
186:   (req's exact 7-value set -- goals are business-level requirements, so
187:    requirement-lifecycle semantics apply)
188: 
189: Goal(MarkdownSection1)                          # H1, free-form title (@alias ".+" REGEX)
190: ├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)
191: ├── description: Description | None             # optional H2 "Description", opaque free text leaf
192: ├── priority: Priority | None                   # optional H2 "Priority", 0-99 single-line value + optional comment
193: ├── tags: Tags | None                           # optional H2 "Tags", bullet list
194: ├── source: Source                              # mandatory H2 "Source", single-line value
195: ├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
196: │   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. "REQ-9687: ...")
197: │   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. "DEC-2703: ...")
198: │   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. "GOL-0007: ...")
199: │   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
200: ├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free text leaf
201: └── notes: Notes | None                         # optional H2 "Notes", opaque free text leaf
202: ```
203: 
204: **No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —
205: both are deliberate, domain-driven omissions, not oversights: ISO 25010
206: quality characteristics grade *requirements*, and RFC 2119 obligation
207: strength is implicit (a goal is always a MUST). Consequently the only
208: mandatory body fields are `statement` and `Source`; a freshly created
209: `gol` document may have zero optional sections yet (all deferred to a later
210: `update_gol` call) but must always carry the goal statement and its source.
211: 
212: **`Priority` keeps `req`'s `MarkdownSection2WithComment` +
213: `field_validator`-on-`value.text` pattern** (0–99, no leading zeros other
214: than "0" itself), re-declared in `gol/models/v1/body.py` — domain packages
215: never import model classes from each other (verified: no cross-domain
216: imports exist in `src/`), so `req`'s `Priority`/`Level` classes are
217: *pattern* precedents, not shared code. `Description`/`Source`/
218: `MoreInformation`/`Notes` are bare opaque leaf subclasses with no further
219: declared fields — the same pattern verified for REQ's `MoreInformation`/
220: `Notes` and PRB's leaves.
221: 
222: **The four `RelatedArtifacts` sub-lists are 1:1 re-declarations of REQ's
223: own four classes**: `MarkdownSection3` with
224: `items: list[MarkdownListItem] = Field(min_length=1)`; heading text
225: ("Requirements"/"Decisions"/"Goals"/"Acceptance Criteria") derives
226: implicitly via the `AliasType.SPACE_SEPARATED` convention (multi-word
227: `AcceptanceCriteria` → "Acceptance Criteria"), so no explicit `@alias` is
228: needed — exactly as in `req/models/v1/body.py`. All four sub-lists are
229: optional, as is `Related Artifacts` as a whole, and no consistency check
230: is enforced between them (REQ precedent). Cross-reference id formats
231: (`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text
232: only — not validated in v1. The `### Goals` sub-list includes goals for
233: cross-referencing peer/superseding goals (self-referencing is allowed; the
234: parser does not special-case a document's own id).
235: 
236: **Update mechanism: whole-body `update_gol(id, content)`**, not an
237: ADR-style `update_section`. The generic `adr/tools/update_section.py`
238: mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
239: ADR-specific code, not a shared cross-domain component — the same decision
240: as feat-16's for `prb`. Individual sections stay addressable by grepping/
241: editing their fixed heading text within the whole-body markdown.
242: 
243: **`list_gol` is a paged tool from day one** (`@mcp.tool(name="list_gol")`
244: returning `PagedResult[GolSummary]`, via `general/tools/_paging.py`'s
245: `paginate`/`normalize_paging`, default page size 25 / cap 100), not a
246: `specmgr://gol/list` resource — GOL is a new domain built *after* ADR
247: ec9f5262 was accepted, so it must not repeat the resource-then-convert
248: history of REQ/UC/TSK/QA/PRB (feat-13). `GolSummary` subclasses
249: `general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`),
250: like `ReqSummary`/`PrbSummary`; `title` is the body's H1 text.
251: 
252: **Prompts are narrated instructions only** (return a string, auto-wrapped
253: as a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call
254: `TodoWrite`/`question`/`get_gol`/`create_gol`/`update_gol` themselves; they
255: only narrate that the calling LLM should. This is the same contract every
256: existing prompt in this codebase already follows
257: (`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).
258: 
259: - `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol`
260:   first to check for an existing, similar goal (mirrors `create_req`'s
261:   dedup-check pattern) and ask the user via `question` if a near-duplicate
262:   is found; (2) build a `TodoWrite` list with one entry per `statement` +
263:   `Source` + each optional section (`Description`/`Priority`/`Tags`/
264:   `Related Artifacts`/`More Information`/`Notes`); (3) use the `question`
265:   tool to elicit the goal statement (mandatory) and the source (mandatory)
266:   plus each optional field in turn, explicitly allowing the user to skip
267:   any optional one; (4) reference the packaged
268:   `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`
269:   for the fixed structure; (5) assemble the full body markdown per the
270:   schema above and call `create_gol(content)`.
271: - `update_gol(id: str) -> str`: instructs the LLM to (1) call
272:   `get_gol(id)` first (never assume prior state); (2) show the user which
273:   sections are already present and which are empty, and ask via
274:   `question` which ones (if any) they want to add or revise; (3) for each
275:   selected section, elicit the new/revised text via `question`; (4) call
276:   `update_gol(id, content)` (whole-body replace, carrying forward every
277:   unchanged section); (5) mention `set_status_gol` as a separate, optional
278:   follow-up (e.g. `implemented` once the goal has genuinely been reached,
279:   `rejected`/`superseded` if abandoned or replaced).
280: 
281: Both prompts' instructional text lives in packaged data files
282: (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`, read
283: via `general.tools._packaged_data.read_packaged_text`, `string.Template`
284: substitution), matching `req_create_instructions.md`/
285: `prb_create_instructions.md`'s precedent — not an inline Python string.
286: 
287: **Frontmatter status** is REQ's exact 7-value closed set
288: (`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
289: `implemented`), re-declared as `GolFrontmatter`'s own `_ALLOWED_STATUSES`
290: frozenset (each domain declares its own set — `ReqFrontmatter`,
291: `TskFrontmatter`, `PrbFrontmatter` all do), with goal-specific semantics:
292: `draft` = still being written; `proposed` = under consideration;
293: `accepted` = agreed to be pursued; `implemented` = the goal has genuinely
294: been reached; `superseded` = replaced by another goal; `deprecated` = no
295: longer pursued, kept for reference; `rejected` = considered and not
296: pursued.
297: 
298: **Example/template documents:** `gol_example.md` is drafted as
299: `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal
300: `req_example.md`'s `### Goals` sub-list already cross-references — so the
301: two packaged examples read coherently side by side; it reuses
302: `gol_reference.md`'s content verbatim (feat-16's own precedent:
303: `prb_example.md` reuses `prb_reference.md`). `gol_template.md` mirrors
304: `req_template.md` minus the `Characteristics` and `Level` sections, with
305: goal-oriented placeholder prose.
306: 
307: ### Related ADRs
308: 
309: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
310:   document-type domain (domain-first hierarchy)
311: - bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
312:   markdown document types
313: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
314:   (`get_gol`), not a resource
315: - ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
316:   MCP tool (`list_gol`), not a resource — must be followed from the start
317:   for this new domain, not retrofitted later
318: - 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
319:   and explicitly *not* reused for `gol` (see Design Notes)
320: 
321: No new ADR is anticipated for this feature — every schema/tooling decision
322: either follows an existing ADR's precedent directly or is scoped enough to
323: log only in this file's own Decisions Made.
324: 
325: ### Task List
326: 
327: Single, canonical breakdown of work phases and tasks. Status lives on the
328: task itself. Each phase ends with a mandatory phase-end task (tests, full
329: quality gate, README Progress update), mirroring feat-16's per-phase
330: commit discipline, since implementation is likely to span multiple
331: sessions.
332: 
333: #### Phase 1: Specification
334: 
335: - [ ] Task 1.1: Write a full reference `gol_reference.md`
336:   (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field
337:   (`statement`, `Source`, plus all optional sections present:
338:   `Description`/`Priority`/`Tags`/`Related Artifacts` with all four
339:   sub-lists/`More Information`/`Notes`) — depends on: none — status:
340:   not-started
341: - [ ] Task 1.2: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` —
342:   `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["gol"]`,
343:   7-value status set identical to `ReqFrontmatter`'s) — depends on: none —
344:   status: not-started
345: - [ ] Task 1.3: Define `gol` body structure (`gol/models/v1/body.py`) —
346:   `Goal(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`,
347:   mandatory `statement: MarkdownParagraph` + `source: Source`, optional
348:   `description`/`priority`/`tags`/`related_artifacts`/`more_information`/
349:   `notes`; `Priority` re-declares REQ's `MarkdownSection2WithComment` +
350:   `field_validator` pattern (0–99); `RelatedArtifacts(MarkdownSection2)`
351:   with four optional `MarkdownSection3` sub-lists (see Design Notes) —
352:   depends on: Task 1.2 — status: not-started
353: - [ ] Task 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` —
354:   structural + validation tests mirroring `tests/req/models/v1/`/
355:   `tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field
356:   combinations (each optional section individually absent/present; each of
357:   the four `Related Artifacts` sub-lists individually absent/present) —
358:   depends on: Task 1.3 — status: not-started
359: - [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
360:   gate (ruff format/check, vulture, full `unittest` suite); confirm
361:   `gol_reference.md` is `specmgr mdformat`-clean; add any new
362:   vulture-invisible Pydantic field names to `whitelist.py` if needed;
363:   update this README's Progress section — depends on: Task 1.1, Task 1.4 —
364:   status: not-started
365: 
366: #### Phase 2: Pydantic Models, Parser & Schema
367: 
368: - [ ] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:
369:   not-started
370: - [ ] Task 2.2: Implement `parse_gol(text: str) -> GolDocument` (model-layer
371:   function, mirrors `parse_req`) — depends on: Task 2.1 — status:
372:   not-started
373: - [ ] Task 2.3: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`,
374:   subclassing `general/models/summary.py::DocSummary`, for `list_gol`) —
375:   depends on: Task 2.1 — status: not-started
376: - [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/
377:   optional field (schema-quality parity with REQ/PRB) — depends on:
378:   Task 2.1 — status: not-started
379: - [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
380:   (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)
381:   - register `"gol"` in the `specmgr schema` doc-type generator registry
382:     (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
383:     status: not-started
384: - [ ] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors
385:   `TestParseReq`'s shape (minimal doc, full reference-doc round-trip,
386:   defaults-when-absent, invalid status, missing-mandatory-field
387:   `AssertionError` cases (`statement`, `Source`), invalid-field
388:   `ValidationError` (e.g. `Priority` out of 0–99 range, invalid `type`
389:   field)) — depends on: Task 2.2, Task 2.5 — status: not-started
390: - [ ] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
391:   including Task 2.6's new tests; update this README's Progress section —
392:   depends on: Task 2.5, Task 2.6 — status: not-started
393: 
394: #### Phase 3: MCP Surface
395: 
396: - [ ] Task 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
397:   wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/
398:   `prb/tools/` exactly) — depends on: Task 2.2 — status: not-started
399: - [ ] Task 3.2: `parse_gol(path: str) -> GolDocument` tool wrapper
400:   (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: not-started
401: - [ ] Task 3.3: `create_gol(content: str) -> GolDocument` tool (body-only
402:   content; MCP builds frontmatter: `id`, `type="gol"`, `status="draft"`,
403:   `created=updated=now`, `version`) — depends on: Task 3.1 — status:
404:   not-started
405: - [ ] Task 3.4: `update_gol(id, content) -> GolDocument` tool (whole-body
406:   replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
407:   `updated`) — depends on: Task 3.1 — status: not-started
408: - [ ] Task 3.5: `set_status_gol(id, status) -> GolDocument` tool (only path
409:   that changes `status`; reconstructs `GolFrontmatter` via its own
410:   constructor so the 7-value validator runs, mirroring `set_status_req`) —
411:   depends on: Task 3.1 — status: not-started
412: - [ ] Task 3.6: `delete_gol(id) -> NoReturn` stub tool — depends on: Task
413:   3.1 — status: not-started
414: - [ ] Task 3.7: `validate_gol(content, full=False) -> bool` tool — depends
415:   on: none — status: not-started
416: - [ ] Task 3.8: `get_gol(id) -> GolDocument` tool (id-based single-document
417:   read; tool, not resource) — depends on: Task 3.1 — status: not-started
418: - [ ] Task 3.9: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]`
419:   tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
420:   (default page size 25, cap 100), preserving the standard skip-malformed-
421:   file scan behavior — depends on: Task 2.3, Task 3.1 — status: not-started
422: - [ ] Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data
423:   (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —
424:   `req_template.md` mirrored minus `Characteristics`/`Level`) via
425:   `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
426:   not-started
427: - [ ] Task 3.11: `gol/resources/{gol_schema,gol_example,gol_template}.py`
428:   — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`, mirroring
429:   `specmgr://req/schema`), `specmgr://gol/example`, `specmgr://gol/template`
430:   (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
431:   not-started
432: - [ ] Task 3.12: `pyproject.toml` package-data entry for
433:   `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
434:   — widen the shared schema-hook glob to include `gol/models/v1`, add a
435:   `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status:
436:   not-started
437: - [ ] Task 3.13: `.github/workflows/ci.yml` — add the `docs/gol_schema.json`
438:   check + packaged-copy check steps — depends on: Task 2.5 — status:
439:   not-started
440: - [ ] Task 3.14: `gol/data/gol_create_instructions.md` +
441:   `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template`
442:   substitution, narrates the full interview flow — see Design Notes) —
443:   depends on: Tasks 3.3, 3.9 — status: not-started
444: - [ ] Task 3.15: `gol/data/gol_update_instructions.md` +
445:   `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
446:   not-started
447: - [ ] Task 3.16: `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain
448:   import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`)
449:   and update its module docstring (Tools/Resources/Prompts sections) —
450:   depends on: Tasks 3.2-3.15 — status: not-started
451: - [ ] Task 3.17: `tests/gol/tools/...`, `tests/gol/resources/...`,
452:   `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout,
453:   including live end-to-end coverage of `create_gol`/`update_gol`'s
454:   narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_gol`'s
455:   paging behavior (default page size, `max_results` clamping, `offset`
456:   paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
457:   not-started
458: - [ ] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
459:   including Task 3.17's new tests; update this README's Progress section —
460:   depends on: Task 3.17 — status: not-started
461: 
462: #### Phase 4: Cross-cutting registration
463: 
464: - [ ] Task 4.1: `AGENTS.md` — update heading to "eight domain/cross-cutting
465:   packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)"; add a
466:   `gol/` bullet (chronological order, after `prb/`); update the "Still
467:   genuinely missing" list (`validate_gol` not enforced via pre-commit/CI,
468:   `delete_gol` stub) and the closing domain-enumeration paragraphs —
469:   depends on: Phase 3 complete — status: not-started
470: - [ ] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
471:   regeneration — confirm `gol` appears correctly and all three commands
472:   report zero drift — depends on: Task 4.1 — status: not-started
473: - [ ] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
474:   update this README's Progress section — depends on: Task 4.2 — status:
475:   not-started
476: 
477: #### Phase 5: Final cross-cutting verification
478: 
479: - [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and
480:   confirm each is satisfied with concrete evidence (including a live
481:   `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests);
482:   run the full quality gate (ruff format/check, pylint advisory, vulture,
483:   unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
484:   checks) end to end; set feature status to `done` — depends on: Phase
485:   1-4 complete — status: not-started
486: 
487: **Note:** If a task's scope changes mid-flight, edit its description in
488: place; rely on git history (`git log -p` on this file) to recover what was
489: originally planned, rather than keeping a second copy of the task around.
490: 
491: ## Progress
492: 
493: ### Current Status
494: 
495: **As of 2026-08-25**: Planning complete; implementation not started.
496: GitHub issue #18 ("Add artifact type Goal (GOL)") is filed and open; all
497: schema/surface decisions were made in the planning session and are logged
498: below. Phase 1 (Specification) is next.
499: 
500: ### Blockers
501: 
502: None.
503: 
504: ### Recent Updates
505: 
506: #### Update 2026-08-25 (planning)
507: 
508: - Completed: GitHub issue #18 filed ("Add artifact type Goal (GOL)") with a
509:   short overview description. Full design/planning discussion — schema
510:   shape (REQ mirrored minus `Characteristics` and minus `Level`; mandatory
511:   `statement` + `Source` only), status set (REQ's 7-value set), related-
512:   artifact sub-lists (all four, identical to REQ), update mechanism
513:   (whole-body replace), prompt behavior, and MCP surface (10 tools / 3
514:   resources / 2 prompts) all decided; this README written from that
515:   discussion.
516: - Next: Phase 1 (Specification) — write `gol_reference.md`, define
517:   frontmatter/body models.
518: - Notes: Planning-only session per explicit user instruction (no
519:   implementation attempted). Issue numbering note: GitHub number 17 was
520:   already consumed by the merged feat-16 PR, so this feature's issue is
521:   #18 and the folder is `feat-18-goal` accordingly (the `feat-NNN-slug`
522:   convention ties the folder name to the issue number).
523: 
524: ### Decisions Made
525: 
526: - **2026-08-25**: Type abbreviation `gol`, domain-first layout
527:   (`gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`,
528:   `gol/data/`) — matches REQ/PRB precedent (schema lives inside the domain
529:   package, not top-level `models/`), since GOL is a new domain built after
530:   the domain-first refactor.
531: - **2026-08-25**: Body mirrors REQ minus `## Characteristics` — ISO 25010
532:   quality characteristics are a requirement-level attribute; a business
533:   goal states *what* to achieve, not *which quality dimension* it loads
534:   (user decision).
535: - **2026-08-25**: No `## Level` section — a goal is implicitly always a
536:   MUST; RFC 2119 obligation strength is a requirement-level attribute
537:   (user decision). Consequently the only mandatory body fields are
538:   `statement` and `Source`, and `gol/models/v1/body.py` declares no
539:   `Level` class or RFC 2119 validator.
540: - **2026-08-25**: Status set = REQ's exact 7-value set
541:   `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
542:   `implemented` — goals are business-level requirements, so
543:   requirement-lifecycle semantics apply (user decision), with goal-specific
544:   meanings for `implemented` (= goal reached) and `superseded` (= replaced
545:   by another goal) as spelled out in Design Notes.
546: - **2026-08-25**: `Related Artifacts` carries all four sub-lists, identical
547:   to REQ (`Requirements`/`Decisions`/`Goals`/`Acceptance Criteria`), each
548:   optional and opaque free text — the `### Goals` sub-list cross-
549:   references peer/superseding goals (user decision).
550: - **2026-08-25**: `update_gol` is a single whole-body replace tool
551:   (REQ/PRB convention), not an ADR-style `update_section`/option-style
552:   granular tool — the latter is currently ADR-specific code (ADR
553:   71fd95d7), same decision as feat-16's for `prb`. Individual sections
554:   remain addressable by their fixed heading text within the whole-body
555:   markdown.
556: - **2026-08-25**: `list_gol` is a paged tool from day one per ADR
557:   ec9f5262 — no `specmgr://gol/list` resource, no resource-then-convert
558:   history.
559: - **2026-08-25**: `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal `req_example.md`'s
560:   `### Goals` sub-list already cross-references — so the two packaged
561:   examples read coherently side by side; it reuses `gol_reference.md`'s
562:   content verbatim (feat-16's own `prb_example.md`/`prb_reference.md`
563:   precedent).
564: - **2026-08-25**: Folder name `feat-18-goal` (issue #18) — GitHub number
565:   17 was already consumed by the merged feat-16 PR, so the convention's
566:   `feat-NNN-slug` ↔ issue-number tie lands on 18.
567: 
568: ### Related PRs / Commits
569: 
570: - [Issue #18](https://github.com/dfch/biz.dfch.SpecMgr/issues/18): Add
571:   artifact type Goal (GOL) — the issue this feature implements.

(End of file - total 571 lines)
</content>
```

**Tool: bash**

**Input:**
```json
{
  "command": "git status; echo \"=== gitignore check ===\"; git check-ignore -v .specmgr/feat/feat-18-goal/README.md; echo \"exit: $?\""
}
```

**Output:**
```
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean
=== gitignore check ===
exit: 1

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 150.4s)

_Thinking:_

Two issues:

1. **`git status` shows "nothing to commit, working tree clean"** — but `.specmgr/feat/feat-18-goal/README.md` exists on disk, is not gitignored (`git check-ignore` exit 1 = not ignored), and should be shown as untracked `??`. "Working tree clean" with no untracked files is... wait, if the file were untracked, `git status` should show "Untracked files: .specmgr/feat/feat-18-goal/". It's showing nothing. So one of the following:
   - The file is already tracked and committed?? No, I just created it.
   - A `.gitignore` covers it — check-ignore says no (exit 1).
   - `git status` is being run in a different worktree? No, cwd is the repo.
   
   Hmm wait, let me double-check: `git check-ignore -v` returned exit 1 with no output → not ignored. And `git status` says clean. So either the file isn't actually at that path relative to the repo root, or... let me verify the file exists and check `git status` more carefully. Actually — wait. Could it be that the whole `.specmgr/feat/` is tracked, and my `write` actually... no, that's not it. Anyway, let me run `ls -la .specmgr/feat/feat-18-goal/` and `git status --porcelain` and `git ls-files .specmgr/feat/feat-18-goal`.

   Oh! Could there be a nested git repo or something? Or is the `git status` output being truncated? It said "nothing to commit, working tree clean". Bizarre. Let me investigate.

2. **mdformat corrupted several code spans** (wrapping at bad positions):
   - Line 67: `gol_create_ instructions.md` (space inside code span) — wait, looking at the actual line 67: "their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string." — hmm wait, is there a line break before that? In the read result, line 67 is one long line: "  instructions.md`/`gol_update_instructions.md`), not an inline string." Let me re-read lines 66–67:
     ```
     66:   `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
     67:   their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string.
     ```
     So mdformat joined lines 66–67 of my original text (I had a line break inside the code span: "`gol/data/gol_create_\n  instructions.md`") and produced a space inside the code span. My original text had an ugly wrap:
     ```
     their own packaged instructions data file (`gol/data/gol_create_
     instructions.md`/`gol_update_instructions.md`), not an inline string.
     ```
     Wait, did I write that? In my original write, the text of REQ-006 was:
     ```
     - REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
       `TodoWrite` + `question`-tool-driven interview flows reusing the
       dedup-check-first pattern from `req/prompts/create_req.py` and the
       `TodoWrite`/`question`-tool narration pattern from
       `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
       their own packaged instructions data file (`gol/data/gol_create_
       instructions.md`/`gol_update_instructions.md`), not an inline string.
     ```
     Yes — I wrapped a code span across a line break in the source (bad practice; mdformat then joined with a space). Result: `gol_create_ instructions.md` — a corrupted filename. Must fix.

   - Line 381: "- register `"gol"` in the `specmgr schema` doc-type generator registry" — originally I had "+ register" but mdformat changed the `+` to `-`? Let me check the original: "   + register `"gol"` in the `specmgr schema` doc-type generator registry". In the read result, line 381 shows "   - register `"gol"`...". Hmm wait, this is inside Task 2.5:
     ```
     379: - [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
     380:   (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)
     381:   - register `"gol"` in the `specmgr schema` doc-type generator registry
     382:     (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
     383:     status: not-started
     ```
     So mdformat re-indented the continuation: originally it was "  + register ... \n   (`_GENERATORS`)..." — the `+` became `-`?? No wait — mdformat shouldn't change `+` to `-`. Let me check the original text I wrote for Task 2.5:
     ```
     - [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
       (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)
       + register `"gol"` in the `specmgr schema` doc-type generator registry
       (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
       status: not-started
     ```
     In the current file it shows "- register" — so the `+` was replaced with `-`? That doesn't seem like mdformat's behavior... actually, hmm, it might be: in the original, the line "       + register ..." — mdformat sees a paragraph with lines starting with 2 spaces and "+ register"... the `+` at the start of a line after indentation could be interpreted as... no, that's not it.

     Wait, let me look more carefully. Current line 381: "   - register `"gol"` in the `specmgr schema` doc-type generator registry". And line 382 has extra indentation "     (`_GENERATORS`)..." — so mdformat interpreted "- register" as a list item? Because... if the source line had been "       + register", hmm, in some markdown flavors `+` is a bullet. Does mdformat (python-markdown) treat `+ register` as an ordered/unordered list bullet? In python-markdown, `+` at the start of a line is a valid bullet marker for an unordered list! So "+ register ..." inside a 2-space-indented paragraph (a lazy continuation of the list item above?) got parsed as a new list item with the `+` bullet, and mdformat normalized the bullet to `-`. That's the corruption: Task 2.5's description is now broken — "- register" became a nested list item, and the line was re-indented.

     I need to fix that too.

   - Line 423: "(`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —" — this is a long line (exceeds 120?), but it's intact (no space inserted inside code spans). Let me count: "   (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —" — that's about 140 characters. mdformat's default line width is 80, but this project probably configures mdformat with a different width? Actually specmgr's mdformat might have its own width setting. Line 423 is long and not wrapped — meaning mdformat's width here is ≥ 120? But then why did it wrap other lines at about 78? Hmm, line 67 is also very long (about 140 characters) and not wrapped.

     Wait, I'm confused. Let me re-check: did mdformat actually wrap at 80? Looking at the file: most lines are under 80 characters. Lines 67 and 423 exceed that. So mdformat wrapped at 80, but couldn't wrap lines 67/423 at word boundaries that didn't produce over-80... no, if it's 80-width wrapping, every line should be ≤80. Line 67: "  their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string." — that's about 135 characters. So it's not 80-width.

     Actually, specmgr_mdformat might use width 120. Line 67 is about 135 characters > 120 — but can't be split at a space without splitting a code span? There are spaces: "their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string." Splitting at the space after "file" would put the code span on the next line — legal. So why did mdformat leave it over 120? Because the code span "(`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`)" is a single unbreakable "word" of about 66 characters, and the preceding "their own packaged instructions data file " is 43 characters → 43+66 = 109, and the next word ")," fits... hmm 109+2=111 <120. So it should have wrapped after "file". Unless mdformat considers the whole thing... actually, python-markdown's wrapping: it wraps at word boundaries, and "words" include inline code as a single token. "(`gol/data/gol_create_" is one token (44 chars with the paren+space), then "instructions.md`/`gol_update_instructions.md`)," is another token (about 50). 44+1+50 = 95+indentation 2 = 97. That would fit in 120...

     I'm going too deep. The real problem: line 67 has a space inside a code span → the filename is corrupted. That must be fixed. And line 423 is long but content-intact (just a long line; mdformat left it — probably because splitting would... whatever, it's intact).

     Also line 368: "- [ ] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:" followed by "   not-started" — this is an intentional wrap (I wrote it that way to avoid a line exceeding 120? I wrote:
     ```
     - [ ] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 —
       status: not-started
     ```
     Hmm, in the original I had it wrapped as "— depends on: Task 1.3 —\n   status: not-started". Currently it shows "status:" at the end of line 368 and "not-started" on line 369. So mdformat re-wrapped it. Content is intact, no problem.

     And line 447: "import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`)" — originally I had "domain\n  import line" (a wrap between "domain" and "import" — legal, no code-span split). Currently line 447 is "  `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain" (about 120 characters) — intact.

     Line 559: "  `### Goals` sub-list already cross-references — so the two packaged" — wait, originally I wrote:
     ```
     - **2026-08-25**: `gol_example.md` is drafted as `GOL-0007: Competitive
       Engines in Consumer Vehicles` — the exact goal `req_example.md`'s
     ```
     (wrap inside the code span "GOL-0007: Competitive\nEngines..." → becomes "GOL-0007: Competitive Engines in Consumer Vehicles" when joined — legal since it's a space, no corruption, and line 559 is long (about 118?). Let me check: "   **2026-08-25**: `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal `req_example.md`'s" ≈ 135 characters. Intact but long. Hmm wait — actually, mdformat joined my two lines into one. Content is intact (space was the boundary). OK.

So the actual corruption from mdformat is:
1. **Line 67**: `gol_create_ instructions.md` — space inside code span (corrupted filename).
2. **Lines 380–383 (Task 2.5)**: `+ register` got parsed as a list bullet → became `- register` with a nested re-indentation, corrupting the task's sentence.

Everything else is either intact or merely re-wrapped.

Also, lines that are long but intact (67, 423, 559, and maybe others) — if I fix the file, I should rerun mdformat to check idempotency. But if mdformat produces lines exceeding 120, that's its own behavior (probably width=80 but can't split long tokens). feat-16's README — let me check if it has lines exceeding 120... for example, feat-16's line 512: "   `prb_update_instructions.md`'s symmetric flow (`get_prb` first, show" — short. But feat-16's line 143: "     narrated 10-step/9-step flows end to end against a real document via" — all short. Hmm, but feat-16's README passed their mdformat check. If specmgr_mdformat uses width 80, my file should have every line ≤ 80 after mdformat... but line 67 is 135 and line 423 is 140. So mdformat couldn't wrap them — meaning the width must be larger (e.g., 120), and these lines exceed 120 because they contain unbreakable tokens longer than the remaining width? No wait — if the width is 120 and a line is 135, there must have been a wrap point that mdformat missed... or mdformat only wraps prose and these lines were originally written by me as long single lines, and mdformat doesn't re-wrap lines that were already ≤... no, mdformat always re-wraps.

Hmm, actually, maybe specmgr's mdformat width is 120 and my lines 67/423/559 were originally written as long single lines? Let me check the original:
- Original REQ-006 line: "  their own packaged instructions data file (`gol/data/gol_create_" + newline + "  instructions.md`/`gol_update_instructions.md`), not an inline string." — the original first line was about 118 characters? "  their own packaged instructions data file (`gol/data/gol_create_" = 66 chars. No.

OK, let me stop the archaeology. The pragmatic approach: fix the two corruptions by editing, restructure so mdformat won't break them again (avoid code spans at wrap boundaries — put long code spans on their own lines, or rephrase), rerun specmgr_mdformat, verify idempotency and content integrity, and confirm that lines like 67 stay intact.

For line 67, the simplest thing: rephrase REQ-006 to avoid the long inline code span:
```
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows reusing the
  dedup-check-first pattern from `req/prompts/create_req.py` and the
  `TodoWrite`/`question`-tool narration pattern from
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol_create_instructions.md`/
  `gol_update_instructions.md` under `gol/data/`), not an inline string.
```
This splits the code span into two shorter ones. "(`gol_create_instructions.md`/\n`gol_update_instructions.md` under `gol/data/`)" — the first token "(`gol_create_instructions.md`/" is about 30 chars — wraps cleanly.

For Task 2.5, rephrase to avoid the leading "+":
```
- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
  and register `"gol"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
  status: not-started
```
Using "and register" instead of "+ register" completely avoids the bullet-parsing issue.

Wait — but how did the `+` become a bullet? In python-markdown, "+ register" at the start of a line (after 2-space indentation) — in a context where the previous line is a continuation of a list item (2-space indent), a `+` at the start of a line could be treated as the start of a nested list. mdformat normalized the `+` → `-` bullet and re-indented. Yes. So avoid a leading `+`.

Now, the git mystery: `git status` says the working tree is clean, yet there's a new file on disk that isn't ignored. That can't be, unless... let me think. `git check-ignore -v` exit 1 = not ignored. `git status` = clean, no untracked.

Ah, wait. Maybe the file was already committed?? No. Or... `core.excludesFile`? check-ignore would have caught it. Or the repo's index already contains this path as identical? If the path were tracked with the same content, `git status` would show nothing — but I just created it. Unless a previous session... no, the folder is new.

Hmm, could `git status` have run in a different directory? The bash tool runs in cwd = /home/user/src/biz.dfch.SpecMgr. git remote was shown, so we're in the repo.

Let me debug: `git ls-files .specmgr/feat/ | head`, `ls -la .specmgr/feat/feat-18-goal/`, `git status --porcelain=v1`, `git rev-parse --show-toplevel`.

Actually — wait a moment. Could there be a global git config, or `.git/info/exclude` containing `.specmgr/`? `git check-ignore` checks all ignore sources including info/exclude — it said not ignored (exit 1). Hmm.

Another possibility: `git status` output was "nothing to commit, working tree clean" — if the file were untracked, it should show "Untracked files". Unless `status.showUntrackedFiles=no` is set in the config! That's a real git setting. If the repo/user has `status.showUntrackedFiles = no`, untracked files won't appear in git status, and it would say "working tree clean". That would explain it. Let me check `git config status.showUntrackedFiles`.

That would mean the file just isn't staged — no problem. Let me verify with `git status --untracked-files=all`.

So my action plan:
1. Debug git untracked visibility (check the config).
2. Fix the two mdformat corruptions with the edit tool.
3. Rerun specmgr_mdformat; verify idempotency; re-check the fixed spots.
4. Report a summary to the user: yes — found and fixed two mdformat re-wrap corruptions; the file is untracked and commit-ready (ask/suggest committing — the user said "wrap up this session"; commit convention: only when explicitly requested. They asked "anything else to add before we wrap up this session?" — that's a question, not a commit request. Fix the file, verify git state, and suggest committing (or, since we're wrapping up, maybe the user expects a commit? No — "only commit when explicitly asked". I'll suggest it).

Also: should I double-check whether mdformat corrupted other lines I missed? Let me systematically scan the file for suspicious content: code spans containing internal spaces that look like filenames with underscores: grep for patterns like "_ [a-z]" inside backticks... more simply: after fixing, rerun mdformat and diff. And grep for "  - " nested bullets inside the Task List to catch other `+`→`-` conversions. Original uses of "+" in prose: I used "+" in "(`TodoWrite` + `question`..." — mid-line, no problem. "create_gol/update_gol" is also fine. Only the leading `+ register` at the start of a line was a problem. Let me grep the current file for lines starting with whitespace + "-" inside the task section to find nested bullets.

Let me run the checks.




The file is mdformat-formatted but I found **2 actual corruptions** where mdformat re-wrapped lines badly:

1. **Line 67** — code span split mid-filename: `` `gol_create_ instructions.md` `` (space inside the filename)
2. **Task 2.5 (lines 380-383)** — my `+ register` continuation was parsed as a list bullet, becoming a nested `- register` item with re-indented text

Also `git status` shows clean, which is suspicious for a brand-new file. Let me investigate both:




**Tool: bash**

**Input:**
```json
{
  "command": "git config --get status.showUntrackedFiles; git status --untracked-files=all --porcelain; echo \"---\"; git ls-files .specmgr/feat/ | tail -5"
}
```

**Output:**
```
---
.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md
.specmgr/feat/feat-9-doc-in-specmgr/create-adr.md
.specmgr/feat/feat-9-doc-in-specmgr/docs-generator-cleanup-plan.md
.specmgr/feat/feat-9-doc-in-specmgr/history/session-ses_038f-adr-tool-plan.md
.specmgr/feat/feat-9-doc-in-specmgr/history/test.md

```

**Tool: bash**

**Input:**
```json
{
  "command": "grep -n \"^   - \\|^    - \\|^  - [a-z]\" .specmgr/feat/feat-18-goal/README.md | grep -v \"^\\(3[3-9][0-9]\\|4[0-9][0-9]\\|5[0-7][0-9]\\): - \" | head; echo \"=== nested bullets in task lines ===\"; awk '/^#### Phase/,/^## Progress/' .specmgr/feat/feat-18-goal/README.md | grep -n \"^   - [a-z]\" "
}
```

**Output:**
```
381:  - register `"gol"` in the `specmgr schema` doc-type generator registry
=== nested bullets in task lines ===

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 43.2s)

_Thinking:_

1. Git: `git status --untracked-files=all --porcelain` didn't output anything about feat-18-goal! And the `status.showUntrackedFiles` config isn't set either. But the file exists on disk... wait, does it really exist? Let me check with `ls`. The read tool was able to read it without any problem just a moment ago. Hmm, `git status --untracked-files=all --porcelain` should display `?? .specmgr/feat/feat-18-goal/`.

Wait a sec, the porcelain output is completely empty — not even the "nothing to commit" text (that's normal with --porcelain). So according to git, there are no untracked files in the entire repository. But `ls`... let me check whether the file actually exists on disk. The read tool read it, and grep just found a line in it — so it exists (grep was run against it).

Could it be... that the file is being ignored via some mechanism that check-ignore missed? check-ignore exited with 1 (not ignored). Hmm, wait — actually, let me double-check: earlier I ran `git check-ignore -v .specmgr/feat/feat-18-goal/README.md; echo "exit: $?"` and got "exit: 1" — that's not ignored.

Then why doesn't git status show it? Ah, wait. I think it's because of **sparse-checkout**, or the file being inside a path excluded from the index... or... hmm, another thought: `git status` in a repo with `core.untrackedCache`... no, that's not it.

Actually — wait. Isn't `.specmgr/feat/feat-18-goal` being shown as `??` but my porcelain command was... no, the output was empty.

Let me test directly: `ls -la .specmgr/feat/feat-18-goal/` and `git status .specmgr/feat/feat-18-goal/` and `git check-ignore -v --no-index .specmgr/feat/feat-18-goal/README.md`.

Hmm, or maybe there's a nested .git directory or something. Or the file is on an overlay filesystem and git's stat is... anyway, let me just run the diagnostics.

2. Confirmed that the nested bullet on line 381 is the only corruption of that kind. Good.




Only one nested-bullet corruption (line 381, as suspected). But git still doesn't see the file — let me dig deeper:



**Tool: bash**

**Input:**
```json
{
  "command": "ls -la .specmgr/feat/feat-18-goal/ && git status .specmgr/feat/feat-18-goal/ ; echo \"check-ignore: $(git check-ignore .specmgr/feat/feat-18-goal/README.md; echo exit=$?)\"; git config --list --local | grep -i \"sparse\\|untracked\" ; cat .git/info/exclude 2>/dev/null | grep -v \"^#\""
}
```

**Output:**
```
total 304
drwxrwxr-x  2 user user   4096 Aug 25 21:06 .
drwxrwxr-x 14 user user   4096 Aug 25 21:03 ..
-rw-rw-r--  1 user user  32583 Aug 25 21:03 README.md
-rw-rw-r--  1 user user 268935 Aug 25 21:06 session-ses_fc5c-feat-18-00.md
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean
check-ignore: exit=1

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 43.7s)

_Thinking:_

Interesting! There's a second file in the folder: `session-ses_fc5c-feat-18-00.md` (268KB, created at 21:06 — just now). This is a session file, and it seems something (an opencode session logger?) is writing session records into the feature folder. Wait — feat-16's folder had similar files: `session-ses_fc80-test-prb.md`, `session-ses_fc85-feat-16-01.md`, `session-ses_fc87-feat-16-00.md`. So this repo's workflow is to save session logs to the feature folder. But this session file appeared without me creating it — probably opencode or some hook is automatically saving the session. Hmm, or maybe it's from a previous session named ses_fc5c... Actually, the timestamp 21:06 = just now (the directory mtime is also 21:06). Something is writing to it right now. Probably a session recorder tied to this session ID (ses_fc5c-feat-18-00).

Wait, but git status shows the whole folder as "clean"?! Even with a 32KB untracked README.md and a 268KB untracked session file present? Both are untracked, yet `git status <folder>` says "nothing to commit, working tree clean". And `git check-ignore` says they're not ignored. This is really strange.

However... it's different if git's stat cache / index has them. Let me check `git ls-files --others --exclude-standard .specmgr/feat/feat-18-goal/` and `git ls-files .specmgr/feat/feat-18-goal/`.

Hmm wait, maybe there's a bug in git's untracked cache (untrackedCache) that's hiding new untracked files? That's possible, but it's rare for it to be this complete.

Or — is the working tree on a filesystem where git's lstat returns weird results? The file is clearly there (ls shows it).

Let me run: `git ls-files --others --directory .specmgr/feat/` and `git status --ignored .specmgr/feat/feat-18-goal/ | head`.




A 268 KB `session-ses_fc5c-feat-18-00.md` has appeared in the folder (the session recorder is writing the session log there, following the feat-16 pattern). However, git is still claiming that the folder is clean, which is odd. Let's check:



**Tool: bash**

**Input:**
```json
{
  "command": "git ls-files --others --directory .specmgr/feat/ ; echo \"=== all untracked (top) ===\"; git ls-files --others --exclude-standard | head -20; echo \"=== ignored? ===\"; git status --ignored=matching .specmgr/feat/feat-18-goal/ 2>&1 | head; echo \"=== untrackedCache ===\"; git config --get core.untrackedCache; git version"
}
```

**Output:**
```
=== all untracked (top) ===
=== ignored? ===
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean
=== untrackedCache ===
git version 2.34.1

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 37.6s)

_Thinking:_

`git ls-files --others` returns nothing across the entire repo. And yet, a file that is neither ignored nor tracked exists on disk. Git 2.34.1. No untrackedCache setting.

Hypotheses:
1. Filesystem-level issue: git's `lstat`/`readdir` against `.specmgr/feat/feat-18-goal/` is failing silently? Unlikely — ls works.
2. **Sparse checkout**: if a sparse-checkout cone is excluding that path... but sparse checkout affects tracked files, and untracked files within a sparse-excluded area are — actually, in sparse checkout, untracked files inside excluded directories are not shown by git status (they're treated as if they don't exist). I checked `git config --list --local | grep -i sparse` — it returned nothing. But the sparse config might be in a different form. `git sparse-checkout list` would tell us.
3. `status.relativePaths`? No.
4. Some global git config like `status.showUntrackedFiles=no`? I only checked local with --local earlier... actually, the first command `git config --get status.showUntrackedFiles` (without --local) checks all scopes — nothing was output. So no.

Let me test: `git add -n .specmgr/feat/feat-18-goal/README.md` (dry run) — if git recognizes it, it should show "add '.specmgr/...'" and not say "did not match any files". Also `git sparse-checkout list`.


**Tool: bash**

**Input:**
```json
{
  "command": "git add -n .specmgr/feat/feat-18-goal/README.md; echo \"rc=$?\"; git sparse-checkout list 2>&1; echo \"=== global configs ===\"; git config --global --list 2>/dev/null | head -20"
}
```

**Output:**
```
rc=0
warning: this worktree is not sparse (sparse-checkout file may not exist)
=== global configs ===
credential.https://github.com.helper=
credential.https://github.com.helper=!/usr/bin/gh auth git-credential
user.email=dfch@users.noreply.github.com
user.name=Ronald Rink

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 33.2s)

_Thinking:_

Interesting: `git add -n` (dry run) succeeded with rc=0, but no "add '...'" line was output at all. Hmm, in newer git, `git add -n` (without `-v`) doesn't output anything on success — in fact, `git add --dry-run` only outputs when combined with `--verbose`. So rc=0 just means it ran normally.

Let me try `git add -nv` to see what gets added. No wait, a better approach: create a test file in a different location, e.g. `/tmp` — no, inside the repo: `touch .specmgr/feat/test-untracked.txt` and check `git status --porcelain`. That will let me isolate whether it's a per-path issue or a repo-wide issue.


**Tool: bash**

**Input:**
```json
{
  "command": "touch .specmgr/feat/__probe_untracked.txt && git status --porcelain; echo \"---\"; rm .specmgr/feat/__probe_untracked.txt"
}
```

**Output:**
```
?? .specmgr/feat/__probe_untracked.txt
---

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 36.8s)

_Thinking:_

The probe file is shown as untracked (`??`). So git is working correctly for new untracked files in `.specmgr/feat/`. But `.specmgr/feat/feat-18-goal/README.md` isn't shown!

So something specific to that path is… Wait. What if that path is tracked in the index? If the index already contains `.specmgr/feat/feat-18-goal/README.md` (e.g., from a previous commit or a staging operation), and the on-disk content matches the index, then git status would show nothing! Let me check: `git ls-files -s .specmgr/feat/feat-18-goal/` and `git ls-tree HEAD .specmgr/feat/feat-18-goal/`.

Hmm, how could it end up tracked? Did I run `git add` myself? No. Did the session recorder do it? Or… wait — actually, what if the index has that file because someone (a previous opencode session in this worktree, or a hook) staged it? Let me check.




Probe file shows as untracked — so git works fine for that directory. That means `feat-18-goal/README.md` must already be **in the index**. Checking:



**Tool: bash**

**Input:**
```json
{
  "command": "git ls-files -s .specmgr/feat/feat-18-goal/; echo \"=== in HEAD? ===\"; git ls-tree HEAD .specmgr/feat/feat-18-goal/ 2>&1; echo \"=== log for path ===\"; git log --oneline -3 -- .specmgr/feat/feat-18-goal/ 2>&1"
}
```

**Output:**
```
100644 08ccf0d0db083d6939a2754cf60cca90150851b4 0	.specmgr/feat/feat-18-goal/README.md
100644 a7583b5a9a6cb12ef7de610e3ad5c5a5f3bd1766 0	.specmgr/feat/feat-18-goal/session-ses_fc5c-feat-18-00.md
=== in HEAD? ===
100644 blob 08ccf0d0db083d6939a2754cf60cca90150851b4	.specmgr/feat/feat-18-goal/README.md
100644 blob a7583b5a9a6cb12ef7de610e3ad5c5a5f3bd1766	.specmgr/feat/feat-18-goal/session-ses_fc5c-feat-18-00.md
=== log for path ===
916e672 feat(gol): add design and plan

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 55.6s)

_Thinking:_

The file has already been committed! There's a commit `916e672 feat(gol): add design and plan` that includes both `README.md` and the session file. But wait — the README on disk is 32583 bytes, and the mtime is 21:03 (after my write around 21:00?). And in the index there's blob 08ccf0d for the README — does that match the current disk content? git status says "working tree clean", so yes, the on-disk content == index == HEAD blob.

Hold on — when was that commit made? I didn't commit. Let me check: `git log -1 --format=fuller 916e672` and `git log --oneline -5`. Also, is 916e672 the tip of dev? "Your branch is up to date with 'origin/dev'" — hmm, that message comes from git status comparing against the upstream. If 916e672 is local-only, the status should say "ahead of origin/dev by 1 commit". It says "up to date" — meaning 916e672 is already on origin/dev?? That would mean someone/something pushed it.

Wait, that's weird. Let me look at the git log and check whether HEAD == origin/dev.

Possibilities: an opencode session hook / git agent (a "ccm" agent? no...) — or the user committed from another terminal during the session. The commit message "feat(gol): add design and plan" is in conventional-commit style (this repo uses Conventional Commits per ADR cb5a2d5f). The user (Ronald Rink / dfch) may have committed themselves while I was working — and the 21:06 session file was also included in that commit, but the session file keeps growing... no wait, if the session file on disk kept growing after the commit, git status should show it as modified. It says clean — so the session file on disk matches the committed blob exactly (268935 bytes). The directory mtime is 21:06, the file mtime is also 21:06 — perhaps the commit happened around 21:06 and captured the file at that moment, and the session recorder hasn't written anything since (or the file just stopped).

Hmm wait, actually there's a subtle point: git status's "working tree clean" compares disk against index. If the session file grew after the commit, status should show ` M`. It shows nothing. So disk == index.

But hold on — my mdformat run (around 21:03?) — the README mtime is 21:03 — that was my mdformat edit. If the commit captured that version, then the committed README = the current (broken) version. Let me verify: `git show 916e672 --stat`, and compare the committed README against disk: `git diff HEAD -- .specmgr/feat/feat-18-goal/` (should be empty).

So what happened: the user (or an automated process) committed my file at 21:06 with the message "feat(gol): add design and plan". Probably the user did it from their own terminal during our session.

Now, my pending work: fix the 2 mdformat-induced corruptions in the README (line 67 `gol_create_ instructions.md` and task 2.5's `+ register` → nested bullet). After the fix, the file will differ from HEAD → will show as modified. Then I should tell the user about it. Should I commit the fix? Only if explicitly requested — the user asked "is there anything else I should add before wrapping up this session?" — I can fix the file and ask whether to commit (or they'll commit themselves, as they apparently just did).

Wait, actually — let me reconsider. Is it possible that an automated hook in this environment commits? The commit includes a session log file (`session-ses_fc5c-feat-18-00.md`) — this is the current session (the "feat-18-00" naming matches feat-16's `session-ses_fc87-feat-16-00.md` pattern). It's plausible the user's workflow auto-saves session transcripts to the feature folder, and the user commits periodically. The commit message style "feat(gol): add design and plan" is exactly Conventional Commits.

Let me check the commit's author/timestamp and position relative to origin/dev.




The file has already been **committed** — commit `916e672 feat(gol): add design and plan` includes both the README and the session log. Let me check who/when, and whether it has been pushed:



**Tool: bash**

**Input:**
```json
{
  "command": "git log -1 --format=\"%H%n%an <%ae>%n%ad%n%s\" 916e672; echo \"=== HEAD vs origin ===\"; git log --oneline -3; git rev-parse HEAD origin/dev 2>&1; echo \"=== diff disk vs HEAD ===\"; git diff HEAD --stat"
}
```

**Output:**
```
916e672696335c392cffff91c4f9c5e095b64154
Ronald Rink <dfch@users.noreply.github.com>
Tue Aug 25 21:07:01 2026 +0200
feat(gol): add design and plan
=== HEAD vs origin ===
916e672 feat(gol): add design and plan
72cf70a chore(prb): add example transcript and resulting problem statement
331d901 chore(release): set version to v0.10.0
916e672696335c392cffff91c4f9c5e095b64154
916e672696335c392cffff91c4f9c5e095b64154
=== diff disk vs HEAD ===

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 61.6s)

_Thinking:_

In other words, the user (Ronald Rink) committed at 21:07:01 — "feat(gol): add design and plan" — and it's already been pushed (HEAD == origin/dev). The committed version is the mdformat-applied version (with the two small breakages that I found).

So the remaining task before wrapping up is: fix the two breakages in the README. The user is committing on their own, so I'll fix the file and leave the commit to them (or ask). Given that they're actively committing, I'll fix it, re-verify mdformat idempotency, and tell them the file needs a follow-up commit (I'll propose one).

Fix 1 — lines 66-67 (REQ-006):
Current:
```
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string.
```
Replace with a rewording that keeps the code spans short:
```
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol_create_instructions.md`/
  `gol_update_instructions.md` under `gol/data/`), not an inline string.
```
Hmm wait — I need to be careful about how mdformat re-wraps this. "(`gol_create_instructions.md`/" — a token of about 31 chars; then "`gol_update_instructions.md`" 27; then "under" "gol/data/" ")," — all fine, no token straddles a wrap point.

Fix 2 — task 2.5 (lines 379-383):
Current:
```
- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)
  - register `"gol"` in the `specmgr schema` doc-type generator registry
    (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
    status: not-started
```
Replace with the following (avoiding a leading "+"):
```
- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
  and register `"gol"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
  status: not-started
```
All tokens are short. Good.

After that, re-run specmgr_mdformat and confirm it returns false (no changes) — if mdformat reformats it again in a different way, check idempotency once more and inspect the result.

Also, bump the frontmatter `updated` date? Per the convention, "updated is bumped on every substantive edit." Today is still 2026-08-25, so no change needed. Good.

Should I also add a "Recent Updates" entry noting the fix? This fix is a trivial correction to the planning document made in the same session before the implementation phase starts, so it's not a substantive planning change, and the existing planning entry covers the writing of the README. I'll skip adding an entry (keep it lean) — hmm, but the "Decisions Made"/updates discipline… this fix isn't a decision. Skip. Actually, wait — the user committed the broken version, so a one-line note might be useful for the git history narrative, but the user can write their own commit message. I'll skip editing the Progress section; the file diff itself is self-evident.

Now let me apply the edits.




The user (Ronald Rink) has already committed and pushed the README at 21:07 as `916e672 feat(gol): add design and plan` — meaning the two mdformat corruptions I found have made it into the pushed commit. Before we wrap up, I'll fix them in the file:




**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md",
  "oldString": "  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use\n  their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string.",
  "newString": "  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use\n  their own packaged instructions data file (`gol_create_instructions.md`/\n  `gol_update_instructions.md` under `gol/data/`), not an inline string."
}
```

**Output:**
```
Edit applied successfully.
```

**Tool: edit**

**Input:**
```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md",
  "oldString": "- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`\n  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)\n  - register `\"gol\"` in the `specmgr schema` doc-type generator registry\n    (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —\n    status: not-started",
  "newString": "- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`\n  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),\n  and register `\"gol\"` in the `specmgr schema` doc-type generator registry\n  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —\n  status: not-started"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 31.6s)

_Thinking:_

Next, I'll re-run specmgr_mdformat to confirm idempotency (making sure no re-wrapping that would break things again occurs), and verify that the two fixed spots remain intact.




Re-running mdformat to confirm the fixes are stable (no re-wrap regression), then verifying the two spots:



**Tool: specmgr_mdformat**

**Input:**
```json
{
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md"
}
```

**Output:**
```
false
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 33.9s)

_Thinking:_

No changes — the file is in a clean state under mdformat, and my fix is preserved as-is (mdformat returns false = already formatted, meaning that the current layout is stable under its own rules and won't get re-broken on re-execution).

Wait, that's a bit surprising: if I run mdformat on the "fixed" content, nothing should change — but would it re-break it? If the fixed line wraps cleanly at token boundaries, then it's stable. `false` means no changes were made to the current file.

Let me check the two fixed spots and check git diff.


**Tool: bash**

**Input:**
```json
{
  "command": "sed -n '62,68p;376,383p' .specmgr/feat/feat-18-goal/README.md; echo \"=== diff vs HEAD ===\"; git diff HEAD --stat; git diff HEAD | head -40"
}
```

**Output:**
```
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows reusing the
  dedup-check-first pattern from `req/prompts/create_req.py` and the
  `TodoWrite`/`question`-tool narration pattern from
  `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
  their own packaged instructions data file (`gol_create_instructions.md`/
  `gol_update_instructions.md` under `gol/data/`), not an inline string.
  depends on: Task 2.1 — status: not-started
- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/PRB) — depends on:
  Task 2.1 — status: not-started
- [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
  and register `"gol"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
=== diff vs HEAD ===
 .specmgr/feat/feat-18-goal/README.md | 11 ++++++-----
 1 file changed, 6 insertions(+), 5 deletions(-)
diff --git a/.specmgr/feat/feat-18-goal/README.md b/.specmgr/feat/feat-18-goal/README.md
index 08ccf0d..8eacc12 100644
--- a/.specmgr/feat/feat-18-goal/README.md
+++ b/.specmgr/feat/feat-18-goal/README.md
@@ -64,7 +64,8 @@ mechanism) and `req`'s 7-value frontmatter status set.
   dedup-check-first pattern from `req/prompts/create_req.py` and the
   `TodoWrite`/`question`-tool narration pattern from
   `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
-  their own packaged instructions data file (`gol/data/gol_create_ instructions.md`/`gol_update_instructions.md`), not an inline string.
+  their own packaged instructions data file (`gol_create_instructions.md`/
+  `gol_update_instructions.md` under `gol/data/`), not an inline string.
 - REQ-007: Packaged example/template/schema data (`gol/data/`) via the
   existing generic `general/tools/_packaged_data.py`, with the matching
   `pyproject.toml` package-data entry, pre-commit hook, and CI step.
@@ -377,10 +378,10 @@ sessions.
   optional field (schema-quality parity with REQ/PRB) — depends on:
   Task 2.1 — status: not-started
 - [ ] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
-  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`)
-  - register `"gol"` in the `specmgr schema` doc-type generator registry
-    (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
-    status: not-started
+  (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
+  and register `"gol"` in the `specmgr schema` doc-type generator registry
+  (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
+  status: not-started
 - [ ] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors
   `TestParseReq`'s shape (minimal doc, full reference-doc round-trip,
   defaults-when-absent, invalid status, missing-mandatory-field

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 47.3s)

_Thinking:_

Both fixes are complete, the diff is minimal and clean, and the file is mdformat-stable.

Alright, to answer the user's question "Is there anything else I should add before wrapping up this session?" — let me summarize the findings and remaining items:

1. ✅ Discovered and fixed 2 mdformat corruptions (the pushed commit 916e672 contains the corrupted version, so a small follow-up commit is needed).
2. The session file `session-ses_fc5c-feat-18-00.md` is still being appended to (the session recorder writes to it) — it was committed at 21:06/21:07 and will keep growing for the rest of this session. Since the user's own commit included it, the established workflow is clearly to commit the session transcript as well (feat-16 had 3 session files). So no action needed — just worth mentioning that it will show up as modified again after the commit.
3. Optional additions considered but not made (deliberately):
   - AGENTS.md update → explicitly Phase 4, don't do it now.
   - `gol_reference.md` → Phase 1 task, don't do it now.
   - The "Existing feature folders" list in AGENTS.md is stale (doesn't even list feat-10/12/13/14/16) — pre-existing issue, and it's noted as feat-7 Task 0.24-ish housekeeping. Not doing it.

So: the only actual gap was the 2 corruptions, which have now been fixed. Suggest a follow-up commit (or, since the user themselves committed the first one, the user can commit it).

Keep the reply concise.




Both fixes are in, the diff is minimal (6 insertions, 5 deletions), and the file is mdformat-stable. Here's the wrap-up:

**Found and fixed** — the pushed commit `916e672` contains the README right after my `specmgr mdformat` run, which had silently corrupted two spots:
1. REQ-006: code span split mid-filename → `gol_create_ instructions.md` (now reworded so the spans can't be split)
2. Task 2.5: my `+ register` line continuation was parsed as a nested list bullet, mangling the task (now plain prose: `...), and register "gol" ...`)

**Nothing else to add** — I considered and deliberately deferred:
- `AGENTS.md` / `server.py` / schema-registry updates → Phase 3–4 tasks
- `gol_reference.md` → Phase 1 Task 1.1
- The stale "Existing feature folders" list in AGENTS.md (missing feat-10/12/13/14/16) → pre-existing, already tracked under feat-7's housekeeping

**One heads-up**: your commit captured `session-ses_fc5c-feat-18-00.md` (269 KB session transcript, same pattern as feat-16's session files) — it keeps growing until this session ends, so the follow-up commit for the two README fixes will include that file's growth too.

The fix is uncommitted on disk, ready for you to commit (or say the word and I'll commit it as `docs(gol): fix two mdformat re-wrap corruptions in feat-18 plan`).

---

