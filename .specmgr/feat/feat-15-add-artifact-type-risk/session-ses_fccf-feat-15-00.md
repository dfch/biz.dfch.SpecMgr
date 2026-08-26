# Risk artifact type with 5x5 matrix

**Session ID:** ses_fccfcc16dffe26CQNj7An2gpIQ
**Created:** 8/24/2026, 11:04:05 AM
**Updated:** 8/24/2026, 3:25:52 PM

______________________________________________________________________

## User

I want to create a new feature to create a new artifact type, similar to the feature feat-10 and the other features: 'add artifact type "risk" (RSK)'

There is an ADR that describes how we create work units with features. And there is a template in the .specmgr feat folder.

Suggest typical attributes of a "risk". I want a separate risk matrix impact/probability of 5x5 for BEFORE and AFTER mitigation (residual risk).
I want an attribute for the risk strategy: TARRA principle
I want a status for the risk
I want a scope (which system is affected)?
I want a list of tags
I want a "More Information" section (optional)

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 39.3s)

_Thinking:_

The user wants to create a new feature for a new artifact type: "risk" (RSK). The user's requests are as follows:

1. A typical risk attribute
2. A 5x5 risk matrix (impact/probability) for both BEFORE mitigation and AFTER mitigation (residual risk)
3. A risk strategy attribute: TARRA principle (Tolerate, Assign, Reduce, Recover, Avoid)
4. Risk status
5. Scope (which system is affected)
6. List of tags
7. "More Information" section (optional)

The user mentions feat-10 as a similar feature. Let me explore the codebase:

- `.specmgr/feat/` folder structure
- feat-10 (probably the feature that added the QA artifact type)
- ADR regarding how work units are created with features
- Template at `.specmgr/_template/v1/README.md`

Let me start exploring. I should look at the following:

1. The template README
2. The feat-10 folder (to see what was done when the artifact type was added)
3. ADRs regarding work units (probably e369ee2e-3353-4f92-991c-6367d76d832e)
4. Existing domain packages (e.g., tsk, qa) to understand the structure

The user is asking me to "propose typical risk attributes" — so the deliverable is a feature plan (README.md inside `.specmgr/feat/feat-NNN-risk/` or similar) that includes the proposed attribute set.

First, let me explore the filesystem.

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/user/src/biz.dfch.SpecMgr/.specmgr/feat/ && ls /home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/"
}
```

**Output:**

```
feat-10-add-artifact-type-tasklist
feat-12-qa-artifact
feat-13-list-paging
feat-14-qa-v2-adjacent-qa
feat-4-use-cases
feat-5-md-model-parser
feat-6-requirement-artifact
feat-7-various-improvements
feat-8-coverage-badge
feat-9-doc-in-specmgr
README.md

```

**Tool: specmgr_list_adr**

**Input:**

```json
{}
```

**Output:**

```
{
  "total": 24,
  "offset": 0,
  "max_results": 25,
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

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 29.2s)

_Thinking:_

The user mentioned feat-10 as a similar feature. feat-10 is "add-artifact-type-tasklist" (TSK). Let's take a look at it as a model. I'll also check the template and related ADRs. Let's read the following:

1. `.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md`
2. `.specmgr/_template/v1/README.md`

Let's do these in parallel.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-16
3: id: feat-10-add-artifact-type-tasklist
4: status: done
5: updated: 2026-08-19
6: version: 1.0.0
7: ---
8: 
9: # Feature: Add artifact type TaskList (tsk)
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Add a new markdown artifact type, `TaskList` (abbreviation `tsk`), for specifying
16: task/todo lists. Whenever an agent creates a "procedure" or step-based plan, it
17: should be able to use a `TaskList` document instead of a full `feat-N-slug`
18: feature file — keeping the list out of the main feature file's context and
19: providing a lightweight vehicle for small procedures where a complete feature
20: is too much. `tsk` follows the domain-first hierarchy and MCP surface already
21: established by `req` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing its
22: tools/resources shape almost exactly (per GitHub issue #10).
23: 
24: ### Requirements
25: 
26: - [x] REQ-001: Define the `tsk` markdown schema — frontmatter (`type="tsk"`,
27:   4-value status set: `draft`/`active`/`done`/`cancelled`) and body (H1 title,
28:   optional leading comment, flat checklist of items, mandatory `## Recent Updates` section holding a dynamic list of H3 update entries)
29: - [x] REQ-002: Pydantic models for `tsk` documents (`tsk/models/v1/` —
30:   domain-first path, mirroring `req/models/v1/`)
31: - [x] REQ-003: Parse and validate `tsk` documents from markdown
32:   (`parse_tsk`, mirroring `parse_req`)
33: - [x] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_tsk`,
34:   `get_tsk_example`, `get_tsk_template`, `create_tsk`, `update_tsk`,
35:   `set_status_tsk`, `delete_tsk` (stub), `validate_tsk`, `get_tsk`
36: - [x] REQ-005: MCP resources mirroring `req`: `specmgr://tsk/list`,
37:   `/example`, `/schema`, `/template`
38: - [x] REQ-006: MCP prompts — `create_task`, `update_task` (narrated tool
39:   sequences, mirroring `req/prompts/create_req.py`/`update_req.py`), and a new
40:   `implement_task` prompt: reads an existing `tsk` document (via `get_tsk`),
41:   builds an actual `TodoWrite` list from its items, and uses the `question`
42:   tool to resolve ambiguity before proceeding
43: - [x] REQ-007: Packaged example/template/schema data (`tsk/data/`) via the
44:   existing generic `general/tools/_packaged_data.py`, with the matching
45:   `pyproject.toml` package-data entry, pre-commit hook, and CI step
46: - [x] REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema`
47:   (new `tsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept
48:   drift-free via pre-commit/CI
49: 
50: ### Acceptance Criteria
51: 
52: - [x] ACC-001: Verifies REQ-001 — schema documented (`docs/tsk_schema.json`,
53:   `specmgr://tsk/schema`), reference `tsk` document (`tsk_reference.md`)
54:   round-trips through the parser (`test_parses_full_reference_document`)
55: - [x] ACC-002: Verifies REQ-002 — Pydantic models validate required/optional
56:   fields correctly, including the `TaskItem` checked/description split
57:   (`tests/tsk/models/v1/test_task_item.py`, `test_body.py`)
58: - [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree;
59:   malformed input raises (structural `AssertionError` / field-level
60:   `pydantic.ValidationError`, matching `req`/`uc`'s error-channel convention)
61:   — `tests/tsk/models/v1/test_parser.py`
62: - [x] ACC-004: Verifies REQ-004 — every listed tool implemented and
63:   registered (confirmed present in regenerated `docs/MCP.md`), with
64:   `create_tsk`/`update_tsk` validating body-only content the same way
65:   `create_req`/`update_req` do
66: - [x] ACC-005: Verifies REQ-005 — every listed resource implemented and
67:   registered (confirmed present in regenerated `docs/MCP.md`)
68: - [x] ACC-006: Verifies REQ-006 — `create_task`/`update_task` prompts
69:   narrate the correct tool sequence (`tests/tsk/prompts/`); `implement_task`
70:   demonstrably drives a `TodoWrite` list from a real `tsk` document and asks
71:   a clarifying question via the `question` tool when an item's intent is
72:   ambiguous — verified live during Phase 4: created a real document via
73:   `create_tsk`, called `implement_task(id)`, built an actual `TodoWrite` list
74:   from its items, identified the ambiguous item ("Do the thing") per the
75:   prompt's own Step 3 guidance, and asked a clarifying question via the
76:   `question` tool before completing it
77: - [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
78:   real, non-editable install, mirroring `req`'s own verification (feat-6
79:   Task 5.1) — verified during Phase 4: built a wheel (`uv build --wheel`),
80:   confirmed `tsk/data/{tsk_example.md,tsk_template.md,tsk_schema.json}` are
81:   packaged inside it, installed into a scratch venv (`biz-dfch-specmgr[mcp]`,
82:   non-editable), and confirmed `read_packaged_text`/`get_tsk_example`/
83:   `get_tsk_template`/`tsk_schema()` all resolve correctly from a working
84:   directory outside the repo (no source-tree fallback possible)
85: - [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
86:   `specmgr mcp-docs` all report no drift after implementation — verified
87:   during Phase 4: all three commands re-run cleanly with zero `git diff`
88:   after Phase 3's commit; confirmed the generic (no `--type`) `docs`/
89:   `mcp-docs`/`schema` CI steps already cover `tsk` automatically
90:   (registry-driven), needing no new per-type step beyond the packaged-copy
91:   step Task 3.12 already added
92: 
93: ### Scope
94: 
95: **Included in this feature:**
96: 
97: - Specification of the `tsk` markdown schema (frontmatter + body)
98: - Pydantic models, parser, and schema generation under `tsk/models/v1/`
99: - Full MCP surface (tools/resources/prompts/packaged data) mirroring `req`
100: - `implement_task` prompt behavior (TodoWrite + `question`-tool clarification)
101: - Tests mirroring `tests/req/`'s layout and coverage
102: 
103: **Explicitly out of scope:**
104: 
105: - Phases, per-item `depends on`/`status` metadata, or any other structure
106:   beyond a flat checklist (explicit decision — see Design Notes)
107: - Granular, ADR-style section-mutation tools (e.g. an `option_*`-style
108:   surface for `## Recent Updates` entries) — entries are appended via a
109:   whole-body `update_tsk` call, same conclusion `req` reached in its own
110:   Task 3.9 design discussion
111: - Cross-referencing/linking `tsk` documents to other artifact types
112:   (REQ/UC/ADR) — not part of this feature
113: - A `specmgr tsk-toc`-equivalent generation command or its own CI/pre-commit
114:   drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`
115:   already provide generically
116: 
117: ### Dependencies
118: 
119: - Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
120:   hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
121:   `MarkdownFrontmatter` base), `general/tools/_doc_paths.py` and
122:   `_packaged_data.py` (generalized past REQ specifically for this kind of
123:   reuse, `feat-6-requirement-artifact` Tasks 3.10/5.2/5.3), the existing
124:   `models/md` engine — in particular `MarkdownSection1WithComment` and
125:   `MarkdownListItem` (reused as-is) and `MarkdownComment` (feat-6 Task 3.20)
126: - Blocks: None identified yet
127: 
128: ### Design Notes
129: 
130: - **Body shape** — `Task` (the body's H1 class) subclasses the already-
131:   existing `MarkdownSection1WithComment` mixin (`models/md/`), reusing it
132:   as-is (no new mixin needed):
133: 
134:   ```
135:   # {H1 title}
136:   <!-- optional leading comment -->        comment: MarkdownComment | None
137:   - [ ] flat checklist item                items: list[TaskItem]  (>=1)
138:   - [x] another item
139:   ...
140: 
141:   ## Recent Updates                        recent_updates: RecentUpdates
142:   ### {free-form title}
143:   {update text}
144:   ### {another entry}
145:   {update text}
146:   ```
147: 
148:   Order is enforced by the model: title -> optional comment -> items (>=1)
149:   -> mandatory `## Recent Updates` heading, whose own `updates` list also
150:   requires `>=1` entry (`min_length=1`, corrected during Phase 2 — see
151:   Decisions Made: a freshly created `tsk` document must seed a first update
152:   entry, e.g. "Created", since the underlying parsing engine already
153:   rejected an empty `## Recent Updates` section and direct construction is
154:   now made consistent with it rather than silently diverging).
155: 
156: - **`TaskItem`** (new leaf, `tsk/models/v1/task_item.py`, subclass of
157:   `MarkdownListItem`) parses a literal `- [ ] text` / `- [x] text` marker
158:   into `checked: bool` + `description: str` computed fields. This is
159:   necessary because the project's markdown parser (`MarkdownIt("commonmark")`,
160:   `models/md/_markdown.py`) has no GFM task-list plugin enabled — `[ ]`/`[x]`
161:   is otherwise just literal inline text, not a distinct AST node.
162: 
163: - **`RecentUpdates`** — an H2 section holding a dynamic list of H3 entries
164:   (free-form title + content each), structurally similar to `AdrBody`'s
165:   `## Pros and Cons of the Options` / `AdrOption` collection, but with no
166:   dedicated per-entry tools (no `option_create`/`option_list` equivalent).
167:   Entries are appended by editing the whole body and calling
168:   `update_tsk(id, content)`. Requires `>=1` entry at all times (see body
169:   shape note above) — Phase 3's `create_tsk`/`get_tsk_template`/
170:   `get_tsk_example` must seed a first entry (e.g. "Created").
171: 
172: - **Frontmatter status** — `draft`/`active`/`done`/`cancelled`: a small,
173:   purpose-fit set matching how a task list is actually used (start it, work
174:   it, finish it, or drop it), rather than reusing REQ's 7-value ADR-like set,
175:   most of which doesn't map naturally onto a todo list.
176: 
177: - **Prompt naming** — the three prompts use the issue's literal wording
178:   (`create_task`/`update_task`/`implement_task`), not the `tsk`-prefixed
179:   convention the tools/resources use, matching GitHub issue #10 verbatim.
180: 
181: ### Related ADRs
182: 
183: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
184:   document-type domain (domain-first hierarchy)
185: - bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
186:   markdown document types
187: 
188: No new ADR is anticipated for this feature — the `TaskItem` checkbox-parsing
189: approach and the `RecentUpdates` dynamic-section design are scoped enough to
190: log only in this file's own Decisions Made, not a full ADR.
191: 
192: ### Task List
193: 
194: Single, canonical breakdown of work phases and tasks. Status lives on the
195: task itself — there is no separate "planned" vs. "executed" list to keep in
196: sync; a task's line *is* its current status. Update it in place as work
197: progresses (edit, don't duplicate).
198: 
199: **Execution approach** (decided 2026-08-16, see Decisions Made): each phase
200: below is delegated to the `implementation-specialist` subagent as one unit
201: (implementation + its own mirrored tests together, not a separate later test
202: phase), reviewed and quality-gated (ruff format/check, vulture, full
203: `unittest` suite) by the orchestrator, then committed as one Conventional
204: Commit per phase. The original standalone "Phase 5: Tests" has been folded
205: into Phases 1–3 below (each phase now carries its own test tasks); Phase 4
206: absorbs a final cross-cutting verification pass instead. This collapses the
207: original 5 phases into **4 commits**.
208: 
209: #### Phase 1: Specification (commit 1) — done
210: 
211: - [x] Task 1.1: Define `tsk` frontmatter (`tsk/models/v1/frontmatter.py` —
212:   `TskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["tsk"]`,
213:   4-value status set `draft`/`active`/`done`/`cancelled`) — depends on: none
214:   — status: done
215: - [x] Task 1.2: Define `tsk` body structure (`tsk/models/v1/body.py`,
216:   `tsk/models/v1/task_item.py`) — `Task(MarkdownSection1WithComment)` with
217:   `items: list[TaskItem]` and `recent_updates: RecentUpdates`; `TaskItem`
218:   (checked/description computed fields, new `MarkdownListItem` subclass);
219:   `RecentUpdates(MarkdownSection2)` holding `updates: list[UpdateEntry]`
220:   built on `models/md`'s generic `list[MarkdownStr]` engine
221:   (`process_list_field`), with `UpdateEntry` a free-form-title H3 leaf via
222:   `@alias(value=".+", type=AliasType.REGEX)` — not ADR's numbered-option
223:   pattern — depends on: Task 1.1 — status: done
224: - [x] Task 1.3 (renumbered; was 1.4): Create a reference `tsk` document
225:   (`tsk_reference.md`) exercising every field, used as the parser's
226:   round-trip test fixture — depends on: Task 1.2 — status: done (placed at
227:   `.specmgr/feat/feat-10-add-artifact-type-tasklist/tsk_reference.md`,
228:   mirroring `req`'s own reference-fixture location convention, not
229:   `tsk/data/` — see Recent Updates)
230: - [x] Task 1.4 (renumbered; was 1.5, folded from former Task 5.1):
231:   `tests/tsk/models/v1/test_frontmatter.py`, `test_body.py`/`test_task_item.py`
232:   — structural + validation tests mirroring `tests/req/models/v1/`, with
233:   explicit coverage of `MarkdownSection1WithComment`'s comment-present/
234:   comment-absent cases (its first real production consumer — no prior test
235:   coverage outside `models/md`'s own unit tests) — depends on: Task 1.3 —
236:   status: done
237: 
238: **Plan correction (2026-08-16, see Decisions Made)**: the former Task 1.3
239: ("draft `tsk_schema.json` + register in the schema generator") has moved to
240: Phase 2 as Task 2.5 — `generate_req_schema`/`generate_uc_schema`
241: (`commands/schema.py`) both call the full `XDocument.model_json_schema()`,
242: not just the body model, so schema generation cannot happen before
243: `TskDocument` (Task 2.1) exists.
244: 
245: #### Phase 2: Pydantic Models & Parser (commit 2) — done
246: 
247: - [x] Task 2.1: `tsk/models/v1/document.py` (`TskDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:
248:   done
249: - [x] Task 2.2: Implement `parse_tsk(text: str) -> TskDocument` (mirrors
250:   `parse_req`/`parse_uc`) — depends on: Task 2.1 — status: done
251: - [x] Task 2.3: `tsk/models/v1/summary.py` (`TskSummary`, mirroring
252:   `ReqSummary`/`AdrSummary`, for the `specmgr://tsk/list` resource) —
253:   depends on: Task 2.1 — status: done
254: - [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
255:   optional field (schema-quality parity with REQ's Task 2.4/2.5/2.6) —
256:   depends on: Task 2.1 — status: done (audited; Phase 1 already met the bar,
257:   no gaps found)
258: - [x] Task 2.5 (moved from Phase 1's former Task 1.3): Draft `tsk_schema.json`
259:   via `generate_tsk_schema()` (mirroring `generate_req_schema`/
260:   `generate_uc_schema` in `commands/schema.py`, calling
261:   `TskDocument.model_json_schema()`) + register `"tsk"` in the `specmgr
262:   schema` doc-type generator registry (`_GENERATORS`) — depends on: Task
263:   2.1 — status: done (`docs/tsk_schema.json` generated, mirroring
264:   `docs/req_schema.json`/`docs/uc_schema.json`'s own precedent)
265: - [x] Task 2.6 (folded from former Task 5.1): `tests/tsk/models/v1/test_parser.py`
266:   — mirrors `TestParseReq`'s 8-case shape (minimal doc, full
267:   reference-doc round-trip, defaults-when-absent, invalid status, malformed
268:   structure, etc.), plus round-trip coverage of the new
269:   `RecentUpdates`/`UpdateEntry` dynamic-list combo — depends on: Task 2.2,
270:   Task 2.5 — status: done
271: 
272: #### Phase 3: MCP Surface (commit 3) — done
273: 
274: **Plan correction (2026-08-16, see Decisions Made)**: REQ-004 explicitly
275: lists `parse_tsk` among the 9 required MCP tools, but the Task List below
276: never allocated a task for the `parse_tsk` **tool** wrapper (Phase 2 only
277: built the model-layer `parse_tsk(text) -> TskDocument` free function).
278: Inserted as Task 3.2 below (mirroring `req/tools/parse_req.py`, a thin
279: `Path(path).read_text()` -> model-layer `parse_tsk` adapter), renumbering
280: every subsequent Phase 3 task by one and updating all cross-references.
281: 
282: - [x] Task 3.1: `tsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
283:   thin wrappers over `general/tools/_doc_paths.py` (mirrors
284:   `req/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:
285:   done
286: - [x] Task 3.2 (new): `parse_tsk(path: str) -> TskDocument` tool wrapper
287:   (`tsk/tools/parse_tsk.py`, mirroring `req/tools/parse_req.py` — reads a
288:   filepath from disk, delegates to the model-layer `parse_tsk`) — depends
289:   on: Task 3.1 — status: done
290: - [x] Task 3.3: `create_tsk(content: str) -> TskDocument` tool (body-only
291:   content, MCP builds frontmatter: `id`, `type="tsk"`, `status="draft"`,
292:   `created=updated=now`, `version`) — depends on: Task 3.1 — status:
293:   done
294: - [x] Task 3.4: `update_tsk(id, content) -> TskDocument` tool (whole-body
295:   replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
296:   `updated`) — depends on: Task 3.1 — status: done
297: - [x] Task 3.5: `set_status_tsk(id, status) -> TskDocument` tool (only path
298:   that changes `status`) — depends on: Task 3.1 — status: done
299: - [x] Task 3.6: `delete_tsk(id) -> NoReturn` stub tool — depends on: Task
300:   3.1 — status: done
301: - [x] Task 3.7: `validate_tsk(content, full=False) -> bool` tool — depends
302:   on: none — status: done
303: - [x] Task 3.8: `get_tsk(id) -> TskDocument` tool (id-based single-document
304:   read; tool, not resource — matches REQ's revisited Task 3.17 conclusion)
305:   — depends on: Task 3.1 — status: done
306: - [x] Task 3.9: `get_tsk_example`/`get_tsk_template` tools + packaged data
307:   (`tsk/data/tsk_example.md`, `tsk/data/tsk_template.md`) via
308:   `general/tools/_packaged_data.py` — depends on: Task 1.3 — status:
309:   done
310: - [x] Task 3.10: `specmgr://tsk/list` and `specmgr://tsk/schema` resources
311:   (packaged `tsk/data/tsk_schema.json`, mirroring `specmgr://req/schema`) —
312:   depends on: Task 3.1, Task 2.5 — status: done
313: - [x] Task 3.11: `specmgr://tsk/example` and `specmgr://tsk/template`
314:   resources — depends on: Task 3.9 — status: done
315: - [x] Task 3.12: `pyproject.toml` package-data entry for
316:   `biz.dfch.specmgr.tsk` (`data/*.md`, `data/*.json`), pre-commit hook + CI
317:   step for the packaged `tsk_schema.json` copy (mirroring
318:   `specmgr-schema-req-package`) — depends on: Task 2.5 — status: done
319: - [x] Task 3.13: `tsk/prompts/create_task.py` + `update_task.py` — narrate
320:   the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)
321:   — depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10 — status: done
322: - [x] Task 3.14: `tsk/prompts/implement_task.py` — reads an existing `tsk`
323:   document via `get_tsk`, builds a `TodoWrite` list from its `items`, and
324:   uses the `question` tool to resolve ambiguity for any item before
325:   proceeding — depends on: Task 3.8 — status: done
326: - [x] Task 3.15: add `tsk` to `server.py`'s domain import line (last-line
327:   import convention — easily forgotten, silently means nothing registers)
328:   — depends on: Tasks 3.2-3.14 — status: done
329: - [x] Task 3.16 (folded from former Tasks 5.2/5.3): `tests/tsk/tools/...`,
330:   `tests/tsk/resources/...`, `tests/tsk/prompts/...` mirroring
331:   `tests/req/tools/`/`tests/req/resources/` layout, plus dedicated tests for
332:   `implement_task`'s `TodoWrite`/`question`-tool driven behavior — depends
333:   on: Tasks 3.1-3.15 — status: done
334: 
335: #### Phase 4: Docs, CI wiring & final verification (commit 4) — done
336: 
337: - [x] Task 4.1: `specmgr docs` regeneration (new `tsk` modules picked up) —
338:   depends on: Phase 1-3 complete — status: done (regenerated as part of the
339:   Phase 3 commit; re-verified zero drift in Phase 4)
340: - [x] Task 4.2: `specmgr mcp-docs` regeneration (new tools/resources/
341:   prompts appear in `docs/MCP.md`) — depends on: Phase 3 complete — status:
342:   done (regenerated as part of the Phase 3 commit; re-verified zero drift
343:   in Phase 4)
344: - [x] Task 4.3: CI wiring — confirm the Python-3.13-only `specmgr schema`/
345:   `specmgr docs`/`specmgr mcp-docs` steps in `.github/workflows/ci.yml`
346:   cover `tsk` with no separate per-type step needed (registry-driven,
347:   mirroring `req`'s own wiring) — depends on: Task 4.1, Task 4.2 — status:
348:   done (confirmed by inspection: the generic, no-`--type` `docs`/
349:   `mcp-docs`/`schema` steps already cover every registered type; only the
350:   packaged-copy step is per-type and Task 3.12 already added it)
351: - [x] Task 4.4: Final verification pass — walk every ACC-001..008 below and
352:   confirm each is actually satisfied; run the full quality gate (ruff
353:   format/check, pylint advisory, vulture, unittest, `specmgr docs`,
354:   `specmgr schema`, `specmgr mcp-docs` drift checks) once more end-to-end —
355:   depends on: Tasks 4.1-4.3 — status: done. All 8 ACCs re-verified with
356:   concrete evidence (see updated Acceptance Criteria section above),
357:   including two substantive live demonstrations beyond unit tests: (1)
358:   ACC-006 — created a real `tsk` document, drove an actual `TodoWrite` list
359:   from `implement_task`'s narrated instructions, and asked a clarifying
360:   question via the `question` tool for its ambiguous item; (2) ACC-007 —
361:   built a real wheel, installed it non-editably into a scratch venv, and
362:   confirmed packaged data resolves correctly outside the source tree. Full
363:   quality gate (980 tests, ruff format/check, vulture, pylint 9.72/10
364:   advisory) all clean.
365: 
366: **Note:** If a task's scope changes mid-flight, edit its description in
367: place; rely on git history (`git log -p` on this file) to recover what was
368: originally planned, rather than keeping a second copy of the task around.
369: 
370: ## Progress
371: 
372: ### Current Status
373: 
374: **As of 2026-08-16**: Phases 1-3 done. Phase 1 (`9ace8dd`) and Phase 2
375: (`1cb9ffe`) committed. Phase 3 (full MCP surface — 9 tools, 4 resources, 3
376: prompts, packaged data, `pyproject.toml`/pre-commit/CI wiring, `server.py`
377: registration) implemented and quality-gated, about to be committed. Along
378: the way, fixed a real correctness defect found during Phase 3 testing:
379: `TaskItem.checked`/`.description` are lazily-evaluated `@computed_field`s,
380: so `Task.from_text` alone silently accepted a malformed checkbox marker
381: (e.g. `"- [z] foo"`) — `create_tsk`/`update_tsk` could have written a bad
382: file to disk before any error surfaced, breaking this project's
383: "successful construction is validation" convention. Fixed with a
384: `Task`-level `model_validator(mode="after")` that forces eager evaluation
385: (a `TaskItem`-level validator doesn't work — `MarkdownListItem.from_text`
386: constructs a bare instance first, populating `.text` only afterward via a
387: private attribute). 980 tests passing, ruff/vulture clean, `docs/`
388: regenerated.
389: 
390: **Feature complete.** Phase 4 (Docs, CI wiring & final verification) done:
391: confirmed no drift in `specmgr docs`/`specmgr schema`/`specmgr mcp-docs`,
392: confirmed CI needs no new generic per-type step, and walked every
393: ACC-001..008 with concrete evidence, including two live demonstrations
394: (ACC-006: `implement_task` driving a real `TodoWrite`+`question`-tool flow
395: against a real document; ACC-007: packaged data resolving from a real,
396: non-editable wheel install in a scratch venv). All 8 requirements and all
397: 8 acceptance criteria satisfied. All four commits landed
398: (`9ace8dd`/`1cb9ffe`/`cba8799`/pending Phase 4 commit).
399: 
400: ### Blockers
401: 
402: None.
403: 
404: ### Recent Updates
405: 
406: See `history.md` for updates before 2026-08-16 (yet further continued, 2).
407: 
408: #### 2026-08-16 (yet further continued, 2)
409: 
410: - Completed: caught and fixed a second Phase-3 gap before dispatching
411:   implementation — REQ-004 lists `parse_tsk` among the 9 required MCP
412:   tools, but the Task List had no task for the tool wrapper itself (only
413:   the Phase 2 model-layer function). Inserted as Task 3.2, renumbering the
414:   rest of Phase 3 (see Decisions Made).
415: - Completed: **Phase 3 (MCP Surface)** — all 9 tools (`parse_tsk`,
416:   `create_tsk`, `update_tsk`, `set_status_tsk`, `delete_tsk` stub,
417:   `validate_tsk`, `get_tsk`, `get_tsk_example`, `get_tsk_template`), all 4
418:   resources (`specmgr://tsk/list`, `/schema`, `/example`, `/template`), all
419:   3 prompts (`create_task`, `update_task`, `implement_task` — the last one
420:   genuinely new, no `req`/`adr` precedent), packaged data
421:   (`tsk/data/tsk_example.md`/`tsk_template.md`/`tsk_schema.json`),
422:   `pyproject.toml`/`.pre-commit-config.yaml`/`.github/workflows/ci.yml`
423:   wiring, and `server.py` registration, all mirroring `req`'s exact
424:   structure file-for-file. 93 new tests under `tests/tsk/{tools,resources,
425:   prompts}/`. Delegated to `implementation-specialist` with the full `req`
426:   reference implementation embedded in the prompt for precision; reviewed
427:   and quality-gated by the orchestrator before committing.
428: - Also completed: found and fixed a real correctness defect during review
429:   (not caught by the implementation-specialist's own test suite, which
430:   passed by construction but didn't probe this specific gap) —
431:   `TaskItem.checked`/`.description` are `@computed_field`s, evaluated only
432:   on access, never during model construction/validation. This meant
433:   `Task.from_text(...)` (and therefore `create_tsk`/`update_tsk`) silently
434:   accepted a malformed checkbox marker like `"- [z] foo"`, breaking this
435:   project's universal "successfully constructing the model *is* the
436:   validation" convention — a caller could have written a bad file to disk
437:   before any error surfaced, if it ever did. First attempted fix (a
438:   `model_validator(mode="after")` directly on `TaskItem`) broke everything
439:   — `MarkdownListItem.from_text` constructs a bare `cls()` first and only
440:   assigns the parsed text to a private `_value` attribute *afterward*
441:   (bypassing Pydantic's own validation), so a `TaskItem`-level validator
442:   fires on an empty, not-yet-populated instance. Fixed correctly instead
443:   with a `model_validator(mode="after")` on `Task` itself (`_validate_items_eagerly`),
444:   which runs after every `TaskItem` in `self.items` is already fully
445:   constructed, forcing each one's `.checked` to evaluate immediately.
446:   Added regression tests at both the model layer
447:   (`tests/tsk/models/v1/test_body.py::TestTaskItemMarkerValidatedEagerly`)
448:   and the tool layer (`tests/tsk/tools/test_create_tsk.py::test_malformed_checkbox_marker_raises_and_writes_nothing`).
449:   Whitelisted `_validate_items_eagerly` in `whitelist.py` (same
450:   Pydantic-validator category as the other `_validate_*` entries).
451: - Next: Execute Phase 4 (Docs, CI wiring & final verification) — confirm
452:   `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` all report no drift,
453:   confirm CI wiring, and walk every ACC-001..008 to verify.
454: - Notes: 980 tests passing total; ruff format/check and vulture clean.
455:   `docs/` (API docs, `GENERATED.md`, `MCP.md`) regenerated to reflect the
456:   new `tsk` modules/tools/resources/prompts.
457: 
458: #### 2026-08-16 (final)
459: 
460: - Completed: **Phase 4 (Docs, CI wiring & final verification)** — feature
461:   complete. Re-ran `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`
462:   (generic and `--type tsk` packaged copy) and confirmed zero drift after
463:   Phase 3's commit. Confirmed by inspecting `.github/workflows/ci.yml` that
464:   the generic (no `--type`) `docs`/`mcp-docs`/`schema` steps already cover
465:   `tsk` automatically (registry-driven) — no new generic CI step needed,
466:   only the per-type packaged-copy step Task 3.12 already added.
467: - Also completed: two substantive live verifications beyond unit tests,
468:   going beyond what the plan strictly required to make the acceptance
469:   criteria genuinely convincing rather than just "the tests pass":
470:   - **ACC-006**: created a real `tsk` document via `create_tsk` with one
471:     checked item, one clear unchecked item, and one deliberately ambiguous
472:     item ("Do the thing"); called `implement_task(id)` and confirmed its
473:     instructions correctly narrate the `get_tsk` → `TodoWrite`-list-build →
474:     `question`-tool-for-ambiguity → separate `update_tsk`-to-persist
475:     sequence; then actually drove a real `TodoWrite` list from the parsed
476:     items and used the `question` tool to resolve the ambiguous item before
477:     marking it complete, exactly as the prompt instructs.
478:   - **ACC-007**: ran `uv build --wheel`, confirmed
479:     `tsk/data/{tsk_example.md,tsk_template.md,tsk_schema.json}` are present
480:     inside the built wheel, installed it non-editably into a scratch venv
481:     (`biz-dfch-specmgr[mcp]`), and confirmed `read_packaged_text`/
482:     `get_tsk_example`/`get_tsk_template`/`tsk_schema()` all resolve
483:     correctly from a working directory outside the repo entirely (no
484:     source-tree fallback possible) — mirroring `req`'s own feat-6 Task 5.1
485:     verification.
486:   - Ran the full quality gate one final time: 980 tests passing, ruff
487:     format/check clean, vulture clean, pylint (advisory) 9.72/10 — the
488:     handful of pylint findings (`redefined-builtin 'id'`, missing test
489:     docstrings, `duplicate-code` across mirrored test files) all match
490:     `req`'s own existing, accepted pattern exactly (verified by running
491:     pylint against `req`'s own files too), not a `tsk`-specific regression.
492: - All 8 requirements (REQ-001..008) and all 8 acceptance criteria
493:   (ACC-001..008) checked off with concrete evidence in their respective
494:   sections above. Feature status set to `done`.
495: - Notes: no `CHANGELOG.md` entry added — confirmed by inspecting `uc`'s own
496:   domain-addition commit (`74e271e`) that new-domain features are not
497:   logged there; `CHANGELOG.md`'s `[Unreleased]` section is only updated at
498:   version-bump time per `AGENTS.md`.
499: 
500: ### Decisions Made
501: 
502: - **2026-08-16**: Target GitHub issue #10, not #11 — issue #11 does not
503:   exist; #10 ("Add artifact type TaskList") matches the pre-existing local
504:   branch's slug. Rationale: avoid creating a redundant new issue when an
505:   existing one already describes the same feature.
506: - **2026-08-16**: Rename the local branch from `feat-11-...` to
507:   `feat-10-...` rather than keep the mismatched number or leave a new issue
508:   to be filed — rationale: keeps the `feat-NNN-slug` convention
509:   (AGENTS.md) accurate and avoids a second `.specmgr/feat/` folder later
510:   needing a rename too.
511: - **2026-08-16**: `tsk` body is a flat checklist (H1 + optional comment +
512:   `items: list[TaskItem]` + mandatory `## Recent Updates`) — no phases, no
513:   per-item `depends on`/`status` metadata. Rationale: keeps the artifact
514:   genuinely lightweight, distinct from the heavier `.specmgr/feat/*`
515:   Task List format it is meant to be a smaller alternative to.
516: - **2026-08-16**: `tsk` frontmatter `status` is `draft`/`active`/`done`/
517:   `cancelled`, not REQ's 7-value set. Rationale: purpose-fit to how a task
518:   list is actually used, rather than maximizing schema consistency with an
519:   artifact type (REQ) whose lifecycle semantics don't map naturally onto a
520:   todo list.
521: - **2026-08-16**: No dedicated per-entry tools for `## Recent Updates`
522:   (no `option_create`/`option_list` equivalent) — entries are appended via
523:   whole-body `update_tsk` calls. Rationale: mirrors REQ's own Task 3.9
524:   conclusion that granular, ADR-style section-mutation tooling isn't worth
525:   building for an artifact this small.
526: - **2026-08-16**: Execution strategy — delegate each phase to the
527:   `implementation-specialist` subagent (implementation + its own mirrored
528:   tests together, not a separate later test phase); one Conventional Commit
529:   per completed phase; orchestrator quality-gates (ruff/vulture/unittest)
530:   before each commit. Rationale: user-selected approach; keeps the original
531:   5-phase plan's dependency ordering intact while avoiding a large,
532:   disconnected final test-writing pass.
533: - **2026-08-16**: `RecentUpdates`/its H3 entries are built on `models/md`'s
534:   generic `list[MarkdownStr]` engine (`process_list_field`) with a
535:   free-form-title H3 leaf via `@alias(value=".+", type=AliasType.REGEX)`,
536:   not adapted from ADR's `AdrOption`/`_OPTION_HEADING_PATTERN`. Rationale:
537:   ADR's option model bakes in mandatory sequential numbering and a fixed
538:   `"Option {number}: "` render format that free-form update entries don't
539:   want; the declarative `models/md` engine already provides the needed
540:   "H2 with dynamic H3 children" shape generically (confirmed by
541:   exploration), matching how `req`'s own `Requirement` H1 already uses the
542:   same free-form-title alias mechanism.
543: - **2026-08-16**: Moved schema generation (`generate_tsk_schema()` +
544:   `specmgr schema` registry entry) from Phase 1 to Phase 2, as Task 2.5.
545:   Rationale: verified `commands/schema.py`'s `generate_req_schema`/
546:   `generate_uc_schema` both call the full `XDocument.model_json_schema()`
547:   (frontmatter + body combined), not the body model alone — so it cannot
548:   run before `TskDocument` (Task 2.1) exists. The original Task List had
549:   this as Task 1.3, before `TskDocument` was even defined; corrected before
550:   starting implementation to avoid building against a broken dependency
551:   order.
552: - **2026-08-16**: Added `min_length=1` to `RecentUpdates.updates`,
553:   superseding the original Design Notes wording ("its own `updates` list may
554:   start empty on creation"). Rationale: Phase 2 empirically confirmed
555:   `models/md`'s generic list-parsing engine already rejects a `## Recent
556:   Updates` section with zero `### ` entries during `from_text` for any
557:   non-`Optional` `list[X]` field (regardless of `min_length`) — but direct
558:   Python construction (`RecentUpdates(updates=[])`) still silently
559:   succeeded, an inconsistency that would have surfaced confusingly in
560:   Phase 3's `create_tsk`. Making the constraint explicit and consistent
561:   means a freshly created `tsk` document must seed a first Recent Updates
562:   entry (e.g. "Created") — `create_tsk`/`get_tsk_template`/`get_tsk_example`
563:   in Phase 3 must account for this, same as `Task.items`' own `min_length=1`
564:   already requires at least one checklist item.
565: - **2026-08-16**: Inserted a Phase 3 task for the `parse_tsk` **tool**
566:   wrapper (renumbered as Task 3.2, shifting every subsequent Phase 3 task
567:   by one). Rationale: REQ-004 explicitly lists `parse_tsk` among the 9
568:   required MCP tools, but the original Task List only ever planned the
569:   model-layer `parse_tsk(text) -> TskDocument` free function (Phase 2,
570:   Task 2.2) — the thin `@mcp.tool()` adapter over it (mirroring
571:   `req/tools/parse_req.py`) had no task of its own. Caught before starting
572:   Phase 3 implementation, same as the earlier schema-sequencing fix.
573: - **2026-08-16**: Added `Task._validate_items_eagerly`, a
574:   `model_validator(mode="after")` on `Task` (not `TaskItem`) that forces
575:   every item's `.checked` computed field to evaluate immediately after
576:   parsing. Rationale: `TaskItem.checked`/`.description` are
577:   `@computed_field`s, which Pydantic only evaluates on access, never
578:   during model construction -- `Task.from_text(...)` alone silently
579:   accepted a malformed checkbox marker (e.g. `"- [z] foo"`), breaking this
580:   project's "successful construction is validation" convention that every
581:   `create_*`/`update_*`/`validate_*` tool's own docstring states literally.
582:   A `model_validator` directly on `TaskItem` does not work for this --
583:   `MarkdownListItem.from_text` constructs a bare, no-argument `cls()` first
584:   and only assigns the parsed text to the private `_value` attribute
585:   afterward (bypassing Pydantic's validation pipeline for that
586:   assignment), so a `TaskItem`-level validator fires on an empty,
587:   not-yet-populated instance. Placing the validator on `Task` instead
588:   works because by the time it runs, every `TaskItem` in `self.items` has
589:   already completed its own `from_text` construction.
590: 
591: ### Related PRs / Commits
592: 
593: No PR opened yet. Implemented across 4 commits on this branch
594: (`feat-10-add-artifact-type-tasklist`), one per phase (see Recent Updates
595: for details of each): `9ace8dd` (Phase 1: Specification), `1cb9ffe` (Phase
596: 2: Models & Parser), `cba8799` (Phase 3: MCP Surface), plus a final Phase 4
597: (Docs, CI wiring & final verification) commit.

(End of file - total 597 lines)
</content>
````

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

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 62.8s)

_Thinking:_

Okay, so now I understand the structure of feat-10 and the template. What the user is asking for is:

1. A new feature "Add artifact type 'risk' (RSK)" — similar to feat-10
2. A proposal of typical attributes for "risk"

Requested attributes:

- 5x5 risk matrix (impact/probability) for both pre-mitigation and post-mitigation (residual risk)
- Risk strategy: TARRA principle (Tolerate, Assign, Reduce, Recover, Avoid)
- Risk status
- Scope (which system is affected)
- List of tags
- "More Information" section (optional)

On top of that, I should also propose typical attributes (e.g., title, description, cause, owner, date, mitigation, etc.) and create a feature folder.

Let me check a few more things:

1. The feat-12 QA feature README (as another example of an artifact type)
2. Check whether there's a GitHub issue number — the user said "add artifact type 'risk' (RSK)". The feat folder numbers are: 10, 12, 13, 14, 4, 5, 6, 7, 8, 9. So the next number might be 15? Let me check the repo's GitHub issues. I can't check GitHub directly, but let me check whether gh is available or whether there's a remote.

Let me check git remote, and if possible, check the issues too.

Also, let me check what the model structure looks like for the existing artifact (e.g., req/models/v1) so I can design the schema for the risk attributes. Additionally, I'll check the existing models to see what building blocks exist (e.g., MarkdownSection1WithComment, MarkdownSection2, etc.).

Let me explore:

- src/biz/dfch/specmgr/req/models/v1/
- src/biz/dfch/specmgr/models/md/
- git remote / gh issues

Let me run these in parallel.

Now let me look at the existing model building blocks and check the GitHub issue numbering.

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/ /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/ /home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/:
__init__.py
__pycache__
_markdown.py
_util.py
alias.py
alias_match.py
alias_type.py
frontmatter.py
markdown.py
markdown_block_quote.py
markdown_code_block.py
markdown_comment.py
markdown_list_item.py
markdown_paragraph.py
markdown_section.py
markdown_section1.py
markdown_section1_with_comment.py
markdown_section2.py
markdown_section2_with_comment.py
markdown_section3.py
markdown_section3_with_comment.py
markdown_section4.py
markdown_section4_with_comment.py
markdown_section5.py
markdown_section5_with_comment.py
markdown_section6.py
markdown_section6_with_comment.py
markdown_str.py

/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/:
__init__.py
__pycache__
_util.py
body.py
document.py
frontmatter.py
parser.py
summary.py

/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/:
__init__.py
__pycache__
_util.py
body.py
document.py
frontmatter.py
parser.py
summary.py
task_item.py

```

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue list --repo $(git remote get-url origin | sed 's@.*github.com/@@') --state open --limit 20 2>&1 | head -30; git branch --show-current",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
GraphQL: Could not resolve to a Repository with the name 'dfch/biz.dfch.SpecMgr.git'. (repository)
dev

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 40.3s)

_Thinking:_

The remote URL has a .git suffix. Let me fix it:
`git remote get-url origin | sed 's@.*github.com/@@' | sed 's@\.git$@@'`

**Tool: bash**

**Input:**

```json
{
  "command": "git remote get-url origin; gh issue list --state open --limit 30 2>&1 | head -40",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr.git
14	OPEN	QA v2: adjacent question/answer pairs (no per-question heading)		2026-08-23T08:41:54Z
7	OPEN	Various cross-cutting improvements	enhancement	2026-08-16T06:50:05Z
2	OPEN	docs: Add Technical Debt section to feature template	documentation, enhancement	2026-08-05T11:46:58Z
1	OPEN	Refactor: Move ADR models from models/adr to adr/models for consistency	enhancement	2026-08-05T11:44:11Z

```

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

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 324.2s)

_Thinking:_

Open issues: #14 (QA v2, probably done/being worked on in feat-14), #7, #2, #1. So issue numbers used in the features so far are: 4, 5, 6, 7, 8, 9, 10, 12, 13, 14. Issue #15 doesn't exist yet.

The user says they want to "create a new feature to create a new artifact type similar to feat-10, i.e., 'add artifact type risk (RSK)'."

Per the convention in AGENTS.md:

- `feat-NNN-slug`, where NNN is the GitHub issue number. Work that is being started without an issue yet uses `feat-0-slug` (issue number `0`) until/unless an issue is later opened for that work.

So, I should first ask the user whether to open a GitHub issue (which would make it something like feat-15-add-artifact-type-risk), or use feat-0-slug. Actually, looking at the decisions in feat-10: the reason issue #10 was chosen was because it already existed. For the risk artifact type, no issue exists yet. Options:

1. Open a new GitHub issue (probably #15) and name it feat-15-add-artifact-type-risk
2. Start as feat-0-add-artifact-type-risk and later create the issue.

Hmm, but I shouldn't just open a GitHub issue without being asked. Let me check the user's intent: "I want to create a new feature to create a new artifact type similar to the other features feat-10 and feat-10: 'add artifact type risk (RSK)'."

So what's being asked is:

1. Create a feature folder (following the template)
2. Propose typical risk attributes (this is the main creative part — they want my proposal, including the explicitly requested attributes)

Let me think about the naming. The user wrote "add artifact type risk (RSK)". The feat-10 title is "Feature: Add artifact type TaskList (tsk)". So mine would be "Feature: Add artifact type Risk (rsk)".

Wait — the abbreviation. TSK = TaskList → "tsk". For risk, the natural abbreviation would be "rsk". The user wrote "(RSK)" in uppercase. Existing domains: adr, req, uc, tsk, qa. So the new domain would be `rsk`.

Now, let me design the risk schema. What the user is asking for:

1. **Typical risk attributes** — I should propose standard risk attributes from ISO 31000 / common risk management practice:

   - Title (H1)
   - Risk description / statement (what can happen, the scenario: cause → event → consequence)
   - Risk owner
   - Date (identified on)
   - Category (e.g., technical, organizational, external) — hmm, the user didn't ask for this, but it's "typical"
   - Mitigation / treatment measures
   - Monitoring

2. **Before/after mitigation 5x5 risk matrix**:

   - Probability (1-5) and Impact (1-5) for the initial risk
   - Probability (1-5) and Impact (1-5) for the residual risk (after mitigation)
   - The risk level is derived: probably a 5x5 matrix that maps (probability, impact) → low/medium/high/critical. The user is asking for "a separate 5x5 risk matrix of impact/probability for before and after mitigation." So two (probability, impact) pairs, each on a 5x5 scale. Should I derive the risk class (low/medium/high/very high) from the product or a matrix? Let me propose: `initial_probability: int 1..5`, `initial_impact: int 1..5`, `residual_probability: int 1..5`, `residual_impact: int 1..5`, and a derived `risk_class` computed from the matrix (e.g., product-based: 1-4 low, 5-9 medium, 10-14 high, 15-25 very high — or a standard matrix). Should I make the derived class a computed field? That's a design decision — could be an option.

3. **Risk strategy: TARRA** — Tolerate, Assign, Reduce, Recover, Avoid. So `strategy: Literal["tolerate", "assign", "reduce", "recover", "avoid"]`. Should there also be an optional strategy rationale? The user said "I want an attribute for risk strategy: TARRA principle". I'll propose a closed 5-value vocabulary. Should strategy be required or optional? Typically a risk without a mitigation has a strategy of "tolerate". Probably required (every risk needs a disposition). Hmm — or optional with default "tolerate". Let me propose required with a value, or… let me think: in risk registers, every risk gets a response strategy. I'll propose `strategy` as required (closed set of 5 values). Though "tolerate" is the natural default. I could make it `strategy: Literal[...] = "tolerate"`. Let me propose this as a design decision in the README.

4. **Risk status** — frontmatter status. What's a good vocabulary for risk lifecycle? E.g.: `open` (identified, active), `mitigated`/`in-treatment`, `accepted` (tolerated), `closed` (resolved/retired), `occurred` (the risk materialized — it became an issue), `cancelled`/`retired`? Common risk statuses:

   - `identified`/`open` — active risk under monitoring
   - `mitigating` — treatment in progress
   - `accepted` — residual risk accepted (tolerated)
   - `occurred` — risk event happened (transitioned to incident/issue)
   - `closed` — no longer relevant, resolved, or expired
   - `dropped`/`cancelled` — not a real risk / removed from the register

   Proposing: `open`, `mitigating`, `accepted`, `occurred`, `closed`, `dropped`. Hmm, 6 values. Or simpler: `open`/`mitigating`/`accepted`/`occurred`/`closed`. TSK used 4 values, REQ used 7. Let me propose: `open`, `mitigating`, `accepted`, `occurred`, `closed`, `dropped`. I'll document the rationale. Actually, to keep it lean and consistent with tsk's "purpose-fit set" approach: default at creation = `open`.

5. **Scope (which system is affected)** — an attribute like `scope: str` or `affected_system: str`. The user said "I want scope (which system is affected)?" So a `## Scope` section or a frontmatter field. Probably a body section that lists affected systems. Could be `scope: str` (free-form text naming the affected system/component). Could also be a multi-item list (a risk can affect multiple systems). The user asked "which system" in singular, but a list would be more flexible. Hmm. I'll propose a `## Scope` section with one or more items (list) — or a single free-form field. Let me think about the markdown schema shape: other documents use H2 sections. A scope section with a list of affected systems works with the `process_list_field` engine. I'll propose `scope: list[MarkdownStr]` (>=1) under `## Scope` — "which system is affected" can be multiple. Actually, the user wrote "I want scope (which system is affected)?" — the question mark suggests they're asking for my opinion. I'll propose a mandatory `## Scope` H2 section holding one or more affected systems/components as list items.

6. **List of tags** — `## Tags` section with a list of tags. Free-form list. Optional? Tags are usually optional. I'll make it optional (empty allowed → section omitted). Hmm, but for parsing: `process_list_field` for an optional list — does the engine support optional H2 sections? Yes, probably via `Optional[MarkdownSection2]` or field default None. I'll propose `tags: list[Tag] | None` as optional.

7. **"More Information" section (optional)** — free-form H2 section, optional. ADR has `## More Information` (optional). So `more_information: str | None`.

Additional typical attributes to propose:

- **Risk description / scenario**: `## Description` — the core of the document. Cause, event, consequence (the "If X, then Y, with consequence Z" formulation).
- **Risk owner**: `## Owner` or frontmatter? Owner is a person/role responsible for the risk. Could be frontmatter `owner: str` or body section. Hmm. Let me think about which fields go into frontmatter vs. body. Looking at the pattern: frontmatter = type, id, status, created, updated, version. Body = H1 title + sections. So owner, date identified, etc. → body sections.

Typical risk register fields (ISO 31000, ISO/IEC 27005):

- ID (already in frontmatter)
- Title (H1)
- Description / scenario (what/why)
- Cause
- Consequence/impact (covered by the 5x5 impact value, but a textual impact description is useful too)
- Owner
- Probability (1-5) + Impact (1-5) → initial risk
- Mitigation/treatment measures (free text)
- Residual probability (1-5) + residual impact (1-5) → residual risk
- Strategy (TARRA)
- Due date / review date
- Status
- Tags
- Related risks / dependencies

Let me design the body schema:

```
# {Risk title}                                   (H1)
<!-- optional leading comment -->

## Description                                   description: MarkdownStr (mandatory)
{Free-form risk scenario: cause → event → consequence}

## Scope                                        scope: list[MarkdownStr] (>=1)
- {Affected system / component}

## Risk Assessment (Before Mitigation)?         — hmm
```

Wait — how do I represent the 5x5 matrix in markdown? Options:

1. Scalar fields: `## Assessment` section with fields like `Probability: 3`, `Impact: 4`… but the models/md engine is heading-based, mapping each H2/H3 section to a field. Scalar inline fields within a section — is there precedent? Let me check how existing documents represent structured scalar data within sections. ADR uses free-form text. Let me check models/md for supported field types: `list[MarkdownStr]` (process_list_field), `MarkdownSection2`/`WithComment`, free-form title + content H3 entries. Are there `str` sections? Yes — e.g., in ADR body, whole-section fields like `context_and_problem_statement` are H2 sections holding a markdown blob.

So the 5x5 values could be represented as:

Option A: two H2 sections:

```
## Initial Risk
Probability: 4
Impact: 3

## Residual Risk
Probability: 2
Impact: 3
```

This needs a new leaf type that parses key-value lines — a `MarkdownListItem`-like custom parser (similar to TaskItem parsing `- [ ]` markers). Feasible: a `RiskMatrix` section with two int fields.

Option B: make the risk matrix part of the frontmatter! E.g., frontmatter fields:

```yaml
initial_probability: 4
initial_impact: 3
residual_probability: 2
residual_impact: 3
```

Frontmatter is YAML, so integers are trivially parseable, and they'd appear in the list summary (`specmgr://rsk/list`) — great for building a risk matrix overview view! And they're stable machine-readable data. Hmm, but is this the pattern of this project? The base frontmatter (MarkdownFrontmatter) has id, type, status, created, updated, version. Domain frontmatters so far have only added type/status narrowing (Req, Uc, Tsk, Qa?). Let me check whether any domain has added extra frontmatter fields… I don't think so — the frontmatter extension fields ADR is about specmgr-specific `id`/`version` (bbf412a7). All domain content lives in the body.

Option C: a markdown table in the body:

```
## Risk Assessment
|          | Initial | Residual |
|----------|---------|----------|
| Probability | 4     | 2        |
| Impact        | 3     | 3        |
```

Parsing GFM tables — the parser is MarkdownIt commonmark without a table plugin, so this would require custom parsing.

I think Option A with custom parsing (key-value list items) is the cleanest and most in line with the project's pattern (TaskItem did exactly this for checkboxes: parse a non-standard marker into a computed field). E.g.:

```
## Initial Assessment
- Probability: 4
- Impact: 3

## Residual Assessment
- Probability: 2
- Impact: 3
```

Each section is an `Assessment(MarkdownSection2)` with `probability: int (1..5)` and `impact: int (1..5)` parsed from list items `- Probability: N`. Plus a derived `level` (low/medium/high/very high) computed from the 5x5 matrix.

Actually wait — the user said "a separate 5x5 risk matrix of impact/probability for before and after mitigation (residual risk)". So they want both an initial (before mitigation) matrix and a residual (after mitigation) matrix, each 5x5. The derived risk class per matrix cell: standard 5x5 color matrix:

- Rows = probability (1 low → 5 high), columns = impact (1 low → 5 high)
- Cell class typically: product-based or zone-based:
  - Zone 1 (low): p\*i \<= 4
  - Zone 2 (medium): 5..9
  - Zone 3 (high): 10..14
  - Zone 4 (very high): 15..25

I'll propose `level: Literal["low", "medium", "high", "very_high"]` as a computed field from the 5x5 matrix via the product threshold. And the `## Mitigation` section (free text) that sits between the initial and residual assessments, explaining what reduces the risk.

Body schema (my proposal):

```
# {Risk title}
<!-- optional leading comment -->

## Description                          description: MarkdownStr
{Risk scenario: what can happen, why it can happen}

## Scope                                scope: list[MarkdownStr] (>=1)
- {Affected system / component}
- {Another system}

## Initial Assessment                   initial_assessment: Assessment (Mandatory)
- Probability: {1-5}
- Impact: {1-5}

## Mitigation                           mitigation: MarkdownStr (Mandatory?)
{Response measures taken to reduce the risk; "none" if strategy is tolerate}

## Residual Assessment                  residual_assessment: Assessment (Mandatory)
- Probability: {1-5}
- Impact: {1-5}

## Strategy                             strategy: Literal[tolerate, assign, reduce, recover, avoid]
...
```

Hmm, strategy — a closed vocabulary from a single line. Could be an H2 section with a single word, or a list item. In the markdown world, maybe:

```
## Strategy
- reduce
```

Or a free-form section validated to be exactly one of the 5 words. Simpler: `strategy: str` section whose content is validated against the TARRA set (single line). Similar to how status works in frontmatter. Let me propose a `Strategy` H2 section holding exactly one of the 5 TARRA words (validated).

Should I include other typical attributes as well? The user said "propose typical risk attributes" — so I have latitude to propose a reasonable complete set. Let me decide the final set:

1. **Title** (H1) — required
2. **Description** — `## Description` required: risk scenario (cause, trigger, consequence)
3. **Scope** — `## Scope` required, list of affected systems/components (user's request)
4. **Initial Assessment** — `## Initial Assessment` required: probability 1-5, impact 1-5 (derived level: low/medium/high/very high)
5. **Mitigation** — `## Mitigation` required: free text on treatment measures (allowing "none" when strategy is tolerate) — needed to make the "before/after" story meaningful
6. **Residual Assessment** — `## Residual Assessment` required: probability 1-5, impact 1-5 (derived residual level)
7. **Strategy** — `## Strategy` required: one of tolerate/assign/reduce/recover/avoid (TARRA)
8. **Tags** — `## Tags` optional: free list of tags
9. **More Information** — `## More Information` optional: free-form (user's request, mirrors ADR's optional more_information)

Frontmatter: type="rsk", status vocabulary (my proposal: `open`, `mitigating`, `accepted`, `occurred`, `closed`, `dropped` — or simpler `open`/`mitigating`/`accepted`/`occurred`/`closed`? Let me think about the lifecycle:

- `open`: identified, being actively monitored
- `mitigating`: treatment in progress
- `accepted`: residual risk formally accepted (strategy=tolerate, or decided to keep)
- `occurred`: the risk materialized → becomes an incident; track here or close?
- `closed`: risk no longer exists (resolved, mitigated to zero, or expired)
- `dropped`: removed from register (wasn't really a risk / duplicate / out of scope)

I'll propose all 6 values, default `open`.

Should I also propose `owner` and `review_date`? The user didn't ask. "Propose typical risk attributes" — owner is very typical in a risk register. Hmm, but every extra field expands the schema. Let me consider what's most defensible: the user gave a specific list and asked for "typical risk attributes" as a starting point. I'll include a complete set, but can mark `owner` as optional in the proposal. Actually, let me reconsider: keeping the schema lean and purpose-fit (like tsk's design notes) is a project convention. Owner is quite central to risk management (every risk has an owner). I'll propose it as an optional `## Owner` section. Hmm, but is it worth it? The user said "propose typical risk attributes for 'risk'" — so I'll propose and let them trim. I'll present the core set (the user's 6 requests + title/description/mitigation as the "typical" glue) and explicitly mark owner as an optional addition.

Now, where to create the feature folder:

- Numbering: existing feat folders: 4, 5, 6, 7, 8, 9, 10, 12, 13, 14. Open issues: 1, 2, 7, 14. Next issue to open would be #15. Per convention: "work that is being started without an issue yet uses feat-0-slug (issue number 0) until/unless an issue is later opened for that work."

Options for the user:
a) Open GitHub issue #15 "Add artifact type Risk" and use `feat-15-add-artifact-type-risk`
b) Start as `feat-0-add-artifact-type-risk` and open the issue later

Since feat-10's decisions made note shows that issue numbers matter, I should ask the user which they prefer. Or I could create the folder as feat-0 and note that the issue should be opened. Hmm, actually let me ask the user — this is a decision with lasting impact (folder name, frontmatter id). Actually, the question tool is appropriate here: ask whether to open the GitHub issue now (→ feat-15) or start as feat-0.

Wait, also about the branch name: they're currently on `dev`. Features are developed on branches named after feat slugs (feat-10's decisions mention renaming the local branch to feat-10-...). So part of the work might be: create branch `feat-15-add-artifact-type-risk` (or feat-0-...) and folder. The user said "I want to create a new feature" — meaning create the feature folder/plan. Let me not overreach: first, the core deliverable is the feature README.md (plan) with the proposed risk attributes. Plus the folder + branch.

Also to check: are there existing risk-related artifacts in the repo (docs or the like)? Probably not. Also to check: does the server.py docstring mention "and later `ac`" — AGENTS.md says a reserved spot for the `ac` domain. Adding rsk doesn't conflict.

Let me also quickly check the QA feature (feat-12) README to see another example of a recent artifact type feature and whether there's a "Technical Debt" section convention (issue #2 mentions adding a Technical Debt section to the feature template — open, so not in the template yet).

Actually, the template I read is the current one. No problem.

Let me quickly check feat-12's README for the shape of a recent feature, particularly how it references issues, and check git log for the branch naming convention.

Actually, I have enough info. Let me also quickly peek at tsk's body model to understand the section structure convention, and check `MarkdownFrontmatter` to see which fields exist (id, type, status, created, updated, version).

Let me quickly read the tsk body + document to check naming, and also check whether there's a "list" summary resource pattern. Actually — I shouldn't over-explore. Key design decisions to validate against the codebase:

1. H2 sections mapping to `list[MarkdownStr]` fields (scope, tags) — supported via `process_list_field` (per tsk's design notes, used for RecentUpdates updates… actually used for MarkdownListItem). Tags as plain `- item` list: does the engine support `list[MarkdownStr]`? TSK's design notes say the updates list is "built on the generic `list[MarkdownStr]` engine (process_list_field) in models/md". OK, so `list[MarkdownStr]` for tags/scope is supported.
2. Scalar int fields parsed from list-item text ("- Probability: 4") — needs a custom leaf like TaskItem (a `MarkdownListItem` subclass with computed fields). Supported (TaskItem precedent).
3. Optional H2 sections — supported (ADR's more_information is optional; uc/qa have optional sections).

Good. Let me confirm that MarkdownFrontmatter has exactly id/type/status/created/updated/version. Quick read.

Let me quickly verify the frontmatter base and an H2 list-section precedent before drafting.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/frontmatter.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/frontmatter.py</path>
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
18: """Generic base frontmatter model shared by every markdown-backed document type.
19: 
20: Per ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (REQ-006/Task 4.1 of
21: ``feat-5-md-model-parser``): this is a *base* frontmatter model carrying only
22: the handful of fields every document type shares. A concrete document type
23: (e.g. a future ``uc``/``req``) defines its own frontmatter model that
24: subclasses :class:`MarkdownFrontmatter` and adds its own fields, narrowing
25: ``type`` to a fixed ``Literal[...]`` value, e.g.::
26: 
27:     from typing import Literal
28: 
29:     class UcFrontmatter(MarkdownFrontmatter):
30:         type: Literal["uc"] = "uc"
31:         # ... uc-specific fields ...
32: 
33: This model is deliberately independent of ``models.adr.v1.AdrFrontmatter``:
34: no shared base class, no shared validator module. ``AdrFrontmatter`` is left
35: exactly as-is (see the ADR's Decision Outcome/Consequences) -- a possible
36: future convergence is noted there but not decided.
37: 
38: This module has no import dependency on ``models.adr.v1`` or any other
39: document-type package, consistent with ``models.md``'s existing
40: no-dependency invariant (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae).
41: """
42: 
43: from __future__ import annotations
44: 
45: from pydantic import BaseModel, field_validator
46: 
47: from ._util import CURRENT_SCHEMA_VERSION, blank_to_none, default_if_blank, validate_schema_version
48: 
49: #: Default ``status`` value when omitted or blank/``None``.
50: DEFAULT_STATUS = "draft"
51: 
52: 
53: class MarkdownFrontmatter(BaseModel):
54:     """The core YAML frontmatter fields shared by every markdown document type.
55: 
56:     Parameters
57:     ----------
58:     id:
59:         The specmgr-assigned document identifier (a server-generated
60:         identifier string), used to resolve ``id -> file path``. Optional,
61:         defaults to ``None`` so existing/hand-authored files without one
62:         still parse; they are just not addressable via id-based tools until
63:         one is assigned.
64:     type:
65:         The document-type discriminator (e.g. ``"uc"``, ``"req"``).
66:         Mandatory with no default on this base model -- every concrete
67:         document type must supply its own fixed value, typically by
68:         overriding this field as ``Literal["..."] = "..."`` in its own
69:         frontmatter subclass. This lets a generic loader read ``type``
70:         alone from a raw frontmatter block to decide which concrete
71:         subclass to validate the rest of the block against, without
72:         needing to know that beforehand. Must not be blank.
73:     created:
74:         Free-form date/timestamp the document was first created. Optional.
75:     updated:
76:         Free-form date/timestamp the document was last updated. Optional.
77:     status:
78:         Free-form lifecycle status. Defaults to ``"draft"`` -- both when
79:         the key is absent entirely and when it is present but blank (e.g. a
80:         template shipping a placeholder ``status:`` with nothing after the
81:         colon, which YAML parses as ``None``, not an absent key).
82:         Deliberately not restricted to a fixed set of values here (unlike
83:         ``AdrFrontmatter.status``'s closed six-value enum): different
84:         document types may have different valid status vocabularies, and a
85:         subclass is free to add its own stricter validator.
86:     version:
87:         The ``models.md`` schema major.minor.patch version this document's
88:         frontmatter was written with. Defaults to
89:         :data:`biz.dfch.specmgr.models.md._util.CURRENT_SCHEMA_VERSION`.
90:         Must share this package's major component -- a
91:         ``MarkdownFrontmatter`` (or subclass) never accepts a ``"2.x.x"``
92:         value while ``models.md``'s
93:         :data:`biz.dfch.specmgr.models.md._util.SCHEMA_MAJOR_VERSION` is
94:         ``1``.
95:     """
96: 
97:     id: str | None = None
98:     type: str
99:     created: str | None = None
100:     updated: str | None = None
101:     status: str = DEFAULT_STATUS
102:     version: str = CURRENT_SCHEMA_VERSION
103: 
104:     @field_validator("type")
105:     @classmethod
106:     def _validate_type_non_blank(cls, value: str) -> str:
107:         if not value.strip():
108:             raise ValueError("type must not be blank")
109:         return value
110: 
111:     @field_validator("version")
112:     @classmethod
113:     def _validate_version(cls, value: str) -> str:
114:         return validate_schema_version(value)
115: 
116:     @field_validator("status", mode="before")
117:     @classmethod
118:     def _default_blank_status_to_draft(cls, value: object) -> object:
119:         return default_if_blank(value, DEFAULT_STATUS)
120: 
121:     @field_validator("created", "updated", mode="before")
122:     @classmethod
123:     def _optional_blank_to_none(cls, value: str | None) -> str | None:
124:         return blank_to_none(value)

(End of file - total 124 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "git log --oneline -5 --all --grep=\"feat-12\" ; git branch -a | head -20",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
4f8024f docs(feat-12): add session record of qa artifact work
74ee817 chore(feat-12-qa-artifact): final verification pass, mark feature done
49e5537 feat(qa): register qa domain across server, packaging, CI, and docs
c993e6e feat(qa): add MCP tool/resource/prompt surface for qa documents
471a951 feat(qa): add qa domain Pydantic models and parser (v1)
* dev
  feat-10-add-artifact-type-tasklist
  feat-14
  main
  remotes/origin/HEAD -> origin/dev
  remotes/origin/dev
  remotes/origin/feat-10-add-artifact-type-tasklist
  remotes/origin/feat-14
  remotes/origin/main

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 229.9s)

_Thinking:_

Now I have the full picture:

- Branch naming: `feat-NNN-slug` (e.g., `feat-10-add-artifact-type-tasklist`, `feat-14`)
- Feature folder: `.specmgr/feat/feat-NNN-slug/README.md`
- GitHub issue numbers: the next new issue would be #15 (open issues: 1, 2, 7, 14; #14 is "QA v2" = feat-14, probably done or in progress)

Now, decisions to confirm with the user before creating the feature folder:

1. **Feature number / GitHub issue**: open issue #15 "Add artifact type Risk" now → `feat-15-add-artifact-type-risk`, or start as `feat-0-add-artifact-type-risk`?
2. **Status vocabulary**: my proposal
3. **Schema details** (derived risk level? owner? mitigation required?)

The user's request: "Please suggest typical attributes for 'risk'." — the main deliverable is a proposed attribute set. They want to create a feature like feat-10. So I'll do the following:

1. Ask the issue/numbering question (and possibly the branch question too)
2. Create the feature folder containing the plan README with the proposed schema

No wait, let me reconsider — should I ask, or just make reasonable choices? The feature number is genuinely ambiguous (the issue doesn't exist). AGENTS.md convention says use feat-0 until an issue is opened. Opening a GitHub issue is a visible external side effect that the user hasn't explicitly requested. Let me ask via the question tool — it's a legitimate decision point with persistent impact (folder name, branch name, frontmatter id). I'll also include the design questions there.

What I'll ask:

1. Feature numbering: open GitHub issue #15 now (feat-15-add-artifact-type-risk, new branch), or start as feat-0 (feat-0-add-artifact-type-risk) and open the issue later?
2. Schema-related decisions:
   a. Status vocabulary: `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped` (6 values) — or a smaller set?
   b. Derived risk level (low/medium/high/very high) from the 5x5 matrix as a computed field — yes or no?
   c. Include optional `## Owner`?
   d. Mitigation section required or optional?

Too many questions. Let me narrow it down: the numbering question is the most important. For the schema, I can present the proposal within the feature plan and let them review. The user said "please suggest typical attributes" — meaning they want me to propose, and they'll review. So:

Plan:

1. Ask the numbering/branch question (1 question, 2–3 options)
2. Create the feature folder with the complete proposed schema in the Design Notes
3. Present the proposed attributes concisely in chat

Actually, I could also ask about the status vocabulary. That's a core attribute the user explicitly requested ("I want a status for the risk"), and I need to propose values. But I can propose values in the plan and let them edit — that's the normal workflow for a feature plan (status: planning, the user reviews). Let me stick to just the numbering question.

No wait — let me reconsider asking at all. The user's message is a work instruction: "I want to create a new feature…". The blocking decision is the folder name (feat-0 vs feat-15). If I guess wrong, the folder + branch will need to be renamed. The precedent in feat-10's Decisions Made shows exactly this issue was faced ("target is GitHub issue #10, not #11 — issue #11 does not exist"). So asking is justified. One compact question.

Also, should the feature include opening the issue? If I choose to open it, I'd run `gh issue create`. Let me present the options:

- "Open GitHub issue #15 now, use feat-15-add-artifact-type-risk (recommended)" — matches the convention (issue number in the id)
- "Start as feat-0-add-artifact-type-risk, open issue later"
- Also mention branch creation.

Hmm, the "recommended" tag — which do I actually recommend? The repo convention: "work started without an issue yet uses feat-0-slug (issue number 0) until an issue is later opened for the work". The feat-10 precedent: issue existed, used its number. For new work where the issue doesn't exist, the established convention is feat-0. But all other features (4–14) have real issue numbers, and issue #2 is about docs… The cleanest approach matching convention is: open issue #15 now (it's a real feature warranting an issue), use feat-15. But that requires gh auth and user approval for the issue text. Or, follow the convention literally: start as feat-0.

I'll make the recommendation "feat-0 now, open the issue later". This follows the documented convention without external side effects and keeps momentum. No wait — the documented convention is "work started without an issue yet uses feat-0-slug until an issue is later opened for the work". That's the literal rule. But the user's phrasing "similar to the other feat-10 features" — feat-10 has a real issue number. Hmm.

Let me just ask — present both, recommend the feat-0 approach (no external side effect, follows the convention, can be renamed later per the feat-10 precedent), and mention that if the issue is opened first, I can switch to feat-15.

One more thing: should I ask about branch creation? If the user chooses, I'll create the branch as part of the same work. I'll weave branch creation into the options ("+ new branch from dev").

Next, the schema proposal. Let me finalize the attributes:

**Frontmatter** (per the established pattern):

- `type: "rsk"` (Literal)
- `status`: closed set — proposed values: `open`, `mitigating`, `accepted`, `occurred`, `closed`, `dropped`
  - `open`: identified, under monitoring (default on creation)
  - `mitigating`: treatment actions in progress
  - `accepted`: residual risk formally accepted
  - `occurred`: the risk event materialized (linked to an incident/issue)
  - `closed`: risk resolved/expired, no further action
  - `dropped`: removed from the register (not a real risk / duplicate / out of scope)
- id/created/updated/version inherited

**Body**:

```
# {Risk title}
<!-- optional leading comment -->

## Description                # required — risk scenario (cause → event → consequence)
## Scope                      # required — one or more affected systems/components (list)
## Initial Assessment         # required — 5x5 matrix values:
                               #   - Probability: {1..5}
                               #   - Impact: {1..5}
                               #   + derived Level: low|medium|high|very_high
## Mitigation                 # required — treatment actions ("none" if strategy is tolerate)
## Residual Assessment        # required — 5x5 matrix values after mitigation (same shape)
## Strategy                   # required — one of: tolerate, assign, reduce, recover, avoid (TARRA)
## Owner                      # optional — responsible person/role
## Tags                       # optional — free list of tags
## More Information           # optional — free-form
```

Derived level from the 5x5 product (standard zoning):

- 1–4: low
- 5–9: medium
- 10–14: high
- 15–25: very high

This mirrors the ADR's optional `## More Information`.

Order consideration: the user listed "risk strategy" — where to place it? I put Strategy after the assessments (so the mitigation flow reads: initial → mitigation → residual → strategy). Or strategy before mitigation (strategy drives mitigation)? TARRA is the response plan; mitigation describes the actions. Either works; let me propose: Description → Scope → Initial Assessment → Strategy → Mitigation → Residual Assessment → (Owner) → Tags → More Information. Hmm, that reads better: the assessment motivates the strategy, the strategy motivates the mitigation actions, and the residual assessment verifies the effect. Yes, I'll use this order.

Wait, but if strategy is "tolerate", mitigation = "none" and residual ≈ initial. That works.

Parsing note: `Initial Assessment`/`Residual Assessment` are custom leaf sections (new model `Assessment` — `MarkdownSection2` with two `MarkdownListItem`-like fields parsed from `- Probability: N` lines, int 1..5, plus a computed `level`). This follows the TaskItem precedent exactly (custom marker → computed field, eager validation via parent model_validator).

Tags/scope: `list[MarkdownStr]` via `process_list_field` (precedent: TSK's RecentUpdates uses the list engine; scope is required with >=1, tags optional).

Strategy: H2 section whose content is validated against the 5-word closed set (a single-line literal). Precedent: frontmatter status narrowing — but this is in the body. It's a `MarkdownSection2` with a constrained `str` field.

Hmm wait — one design question: should probability/impact be `int` (1-5) or a string? int with ge=1 le=5 is clean for JSON schema and matrix computation. Yes, int.

The list summary (`RskSummary`) will include: id, title, status, scope (or first item?), initial level, residual level, strategy — perfect for building a risk-matrix overview. That's a nice bonus; I'll mention it in the Design Notes (fields available in the `specmgr://rsk/list` summary).

Now, the structure of the feature README (following the template + feat-10's shape):

- Frontmatter: id, version 1.0.0, status: planning, created/updated: 2026-08-24 (today per env)
- # Feature: Add artifact type Risk (rsk)
- ## Plan: Overview, Requirements (REQ-001..), Acceptance Criteria (ACC-001..), Scope, Dependencies, Design Notes, Related ADRs, Task List (phases)
- ## Progress: Current Status, Blockers (none), Recent Updates, Decisions Made, Related PRs/Commits

For requirements, I'll mirror feat-10's REQ-001..008 shape (schema, model, parser, MCP tools, resources, prompts, package data, doc wiring). For RSK, which prompts? feat-10 had create_task/update_task/implement_task. For RSK: `create_risk`/`update_risk`? tsk used the issue's literal wording for prompt naming (create_task/update_task). For RSK, `create_risk`/`update_risk` seems reasonable. There's no tsk-like "implement" prompt specific to RSK… unless there's a `review_risk` or something? I won't over-invent; I'll stick with create/update. I can note in the plan that additional prompts can be considered later.

Let me write the task list phases mirroring feat-10's 4 phases:

- Phase 1: Specification (frontmatter, body model, assessment leaf, reference doc, model tests)
- Phase 2: Models & Parser (document, parse_rsk, summary, Field descriptions, schema.json + registry, parser tests)
- Phase 3: MCP Surface (paths/io/write/lock, parse_rsk tool, create/update/set_status/delete stub/validate/get_rsk, examples/templates + package data, resources list/schema/example/template, pyproject package-data + pre-commit + CI, prompts create_risk/update_risk, server.py registration, tool tests)
- Phase 4: Documentation/CI wiring/final verification

I'll write it in the same "status: not-started" style.

Also note: the docstring of `server.py` reserves "and later `ac`" — I'll add rsk to the registration. Also `specmgr docs`/`mcp-docs`/`schema` are registry-driven.

Another consideration — the user's question "I want a scope (which systems are affected)?" — the trailing "?" suggests they're unsure. My answer: yes, keep it, as a required H2 list section (a risk can affect multiple systems). I'll note in the chat.

Let me also double-check that there's no existing "risk" mention in the repo to avoid clashes: quick grep. And check the server.py docstring to see the registered domain list (for Dependencies/Design Notes accuracy). Let me quickly grep for "risk" and look at the last line of server.py.

Then I'll ask the numbering question, create the folder + branch, and write the README.

No wait — the order of operations. The question tool interrupts the user. I should gather everything and ask just one consolidated question with the key decisions. Let me limit to at most 2 questions:

Q1: Feature ID / issue — options:
a. "feat-0 now, issue later (recommended)" — follows the AGENTS.md convention for work without an issue; rename once the issue is opened (precedent from feat-10's Decisions Made)
b. "Open issue #15 now → feat-15" — I'll create the GitHub issue + branch + folder all at once
c. Type my own answer is available automatically (custom enabled).

Q2: Status vocabulary — options:
a. "open, mitigating, accepted, occurred, closed, dropped (recommended)"
b. "open, accepted, occurred, closed (leaner)"
Hmm. Is this worth asking? The user explicitly asked for status but didn't specify values. This is a core attribute where the values matter. I'll ask — it's cheap and prevents rework. Or I could just propose it in the plan and let them review the plan. The plan is a living document (status: planning); the user will review it anyway. But asking consolidates the decisions in one shot. Let me ask both questions in a single question tool call (the tool supports multiple questions).

Should I also ask about derived level (computed low/medium/high/very_high)? I could fold it into Q2… no, let me keep it to 2 questions. I'll include the derived level as part of the schema in the Design Notes — it's a natural part of "a 5x5 matrix" (matrix = zone). The user asked for "a separate 5x5 risk matrix for impact/probability" — the matrix itself implies zones. I'll include the derived `level` in the proposal and mention it in chat so they can veto.

Let me first do a quick grep for "risk" in src/.

**Tool: bash**

**Input:**

```json
{
  "command": "rg -il \"risk\" src/ docs/ .specmgr/feat/ 2>/dev/null | head; rg -n \"later \\`ac\\`|import.*general.*qa.*req\" src/biz/dfch/specmgr/server.py | head -5",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
/bin/bash: line 1: rg: command not found

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 49.9s)

_Thinking:_

rg is not available. Use the grep tool instead.

**Tool: grep**

**Input:**

```json
{
  "path": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr",
  "pattern": "risk"
}
```

**Output:**

```
Found 3 matches
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/data/general_iso25010.md:
  Line 197: Identify a course of events or operations that can expose life, property or environment to unacceptable risk

  Line 205: Warnings of unacceptable risks to operations or internal controls so they can react in sufficient time to sustain safe operations


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models/v2/body.py:
  Line 81: the base does not risk any heading-detection ambiguity between the

```

**Tool: grep**

**Input:**

```json
{
  "path": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py",
  "pattern": "import.*\\(adr|general, qa|later `ac`"
}
```

**Output:**

```
Found 1 matches
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py:
  Line 155: from . import adr, general, qa, req, tsk, uc  # noqa: E402, F401

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 367.3s)

_Thinking:_

Alright — there's no existing "risk" domain. The import line at server.py:155 is `from . import adr, general, qa, req, tsk, uc`.

Next, let me confirm with the user about the two decisions (feature numbering + status vocabulary).

No existing `risk`/`rsk` artifacts in the codebase — clean slate. Two decisions affect the folder/branch naming, so let me confirm before creating the feature:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Feature ID",
      "question": "No GitHub issue exists for 'Add artifact type Risk' yet (open issues are #1, #2, #7, #14; next would be #15). Per AGENTS.md, work started without an issue uses feat-0-slug until an issue is opened. How should this feature be numbered?",
      "options": [
        {
          "label": "feat-0 now, issue later (Recommended)",
          "description": "Create .specmgr/feat/feat-0-add-artifact-type-risk/ + branch feat-0-add-artifact-type-risk; open the GitHub issue later and rename (feat-10 did exactly this rename)"
        },
        {
          "label": "Open issue #15 now",
          "description": "I create the GitHub issue 'Add artifact type Risk (rsk)' first, then use feat-15-add-artifact-type-risk + matching branch"
        }
      ]
    },
    {
      "header": "Status set",
      "question": "You asked for a risk status. Which frontmatter status vocabulary should the plan propose?",
      "options": [
        {
          "label": "6-value: open, mitigating, accepted, occurred, closed, dropped (Recommended)",
          "description": "Full risk lifecycle: identified/monitored -> treatment in progress -> residual accepted -> risk materialized -> resolved/expired -> removed from register. Default: open"
        },
        {
          "label": "4-value: open, accepted, occurred, closed",
          "description": "Leaner set, closer to tsk's purpose-fit 4-value approach; no explicit 'mitigating' or 'dropped'"
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "No GitHub issue exists for 'Add artifact type Risk' yet (open issues are #1, #2, #7, #14; next would be #15). Per AGENTS.md, work started without an issue uses feat-0-slug until an issue is opened. How should this feature be numbered?"="Open issue #15 now", "You asked for a risk status. Which frontmatter status vocabulary should the plan propose?"="6-value: open, mitigating, accepted, occurred, closed, dropped (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 58.5s)

_Thinking:_

User's choices:

1. Open Issue #15 now → `feat-15-add-artifact-type-risk`
2. 6-value status: open, mitigating, accepted, occurred, closed, dropped

So next:

1. Create GitHub issue #15 "Add artifact type Risk (rsk)" — following the style of other issues. To match the title format, let me check how the previous issues were worded. Issue #10 was "Add artifact type TaskList". Issue #14 was "QA v2: adjacent question/answer pairs (no per-question heading)". To follow convention, let me look at the issue body. I'll try `gh issue view 10`.

2. Create a branch `feat-15-add-artifact-type-risk` from dev.

3. Create `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` with the full plan.

First let me check the body of issue #10 and follow convention.

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue view 10 --json title,body -q '.title + \"\\n---\\n\" + .body' 2>&1",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
Add artifact type TaskList
---
We create a new artifact type `TaskList`:

* abbreviation `tsk`
* sub-folder as `req`
* resources: same as `req`
* tools: same as `req`
* prompts: `create_task` and `update_task` and `implement_task` (this will create an existing list, make a todo list from it and ask questions with the question tool if not clear how to proceed).

This artifact is needed for specifications of task or todo lists. Whenever, an agent creates a "procedure" or step-based plan, it shall use a list. This list can then reside outside of main feature file and does not add to the context size. In addition, the task list is useful when doing small procedures for which a complete feature is too much.

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 327.7s)

_Thinking:_

Good — I've got a handle on the issue body conventions. Now, let me draft issue #15 for the risk artifact type. The issue should be concise, in the same style as #10. I'll include the attribute set (since it's the core of the design). Issue #10 didn't include the full schema, but it described the surface. For RSK, I'll write it with a similar structure:

```
Add artifact type Risk

Creates a new artifact type `Risk`:

* Abbreviation `rsk`
* Subfolder as `req`/`tsk`
* Resources: same as `req`
* Tools: same as `req`
* Prompts: `create_risk` and `update_risk`

Attributes (schema):
* Frontmatter: type="rsk", status is one of open/mitigating/accepted/occurred/closed/dropped
* H1 title
* ## Description — risk scenario
* ## Scope — affected systems/components (list, ≥1)
* ## Initial Assessment — 5x5 matrix: Probability 1..5, Impact 1..5 (derived level)
* ## Strategy — TARRA: tolerate/assign/reduce/recover/avoid
* ## Mitigation — treatment measures
* ## Residual Assessment — 5x5 matrix after mitigation
* ## Owner — optional
* ## Tags — optional
* ## More Information — optional

This artifact is needed for risk registers within system specs...
```

Hmm, should the issue go into this level of detail? Issue #10 was light on detail (details were deferred to the feature README). But the user specifically asked for these attributes, and the issue is a work unit. I think it's right to include the attribute list in the issue — that way the issue itself captures the user's requirements. Keep it reasonably concise.

Now — should I `git add` the README? AGENTS.md says pylint only sees files tracked by git, and pre-commit needs the file to be tracked. The feature README is a .specmgr file. In the feat-10 workflow, the feature folder was probably committed along with Phase 1. The user asked to "create a new feature" — i.e., create the feature folder/plan. I will **not** commit (rule: only commit when explicitly asked). Create the branch and files, and leave the commit to the user or to a later explicit instruction.

Wait — branch creation: `git switch -c feat-15-add-artifact-type-risk` from dev. I'm currently on dev. That's fine — creating a branch is part of the feat convention (feat-10's branch exists locally + remotely). Creating a local branch is a low-risk operation, and the user implicitly asked for it by choosing "open issue #15 now" (the options included a matching branch). I'll create the branch.

Next, the feature README. Let me draft it in full, following the template + feat-10's structure. Date: 2026-08-24.

Content plan:

```markdown
---
created: 2026-08-24
id: feat-15-add-artifact-type-risk
status: planning
updated: 2026-08-24
version: 1.0.0
---

# Feature: Add artifact type Risk (rsk)

## Plan

### Overview

Add a new markdown artifact type `Risk` (abbreviation `rsk`) for maintaining a risk register within system specifications. ... Follow the domain-first hierarchy and MCP surface established by `req`/`tsk` (ADR ece4554b-...), reusing the same tool/resource shape nearly 1:1 (per GitHub issue #15).

### Requirements

- [ ] REQ-001: Define the `rsk` markdown schema — frontmatter (`type="rsk"`, 6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open`) and body (H1 title, optional leading comment, `## Description`, `## Scope` (list, ≥1), `## Initial Assessment` (5x5: probability/impact 1..5, derived level), `## Strategy` (TARRA closed 5-value set), `## Mitigation`, `## Residual Assessment` (5x5), optional `## Owner`, optional `## Tags`, optional `## More Information`)
- [ ] REQ-002: Pydantic model for `rsk` documents (`rsk/models/v1/` — domain-first path, mirroring `tsk/models/v1/`)
- [ ] REQ-003: Parsing and validation of `rsk` documents from markdown (`parse_rsk`, mirroring `parse_tsk`)
- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`, `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`
- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`, `/example`, `/schema`, `/template`
- [ ] REQ-006: MCP prompts — `create_risk`, `update_risk` (narrated tool sequences, mirroring `req`/`tsk`'s create/update prompts)
- [ ] REQ-007: Bundled sample/template/schema data (`rsk/data/`) via `general/tools/_packaged_data.py`. With corresponding `pyproject.toml` package-data entries, pre-commit hook, and CI step
- [ ] REQ-008: Doc-generation wiring — `specmgr docs`, `specmgr schema` (new `rsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept drift-free via pre-commit/CI

### Acceptance Criteria

- [ ] ACC-001: Validates REQ-001 — schema is documented (`docs/rsk_schema.json`, `specmgr://rsk/schema`), the reference `rsk` document (`rsk_reference.md`) round-trips through the parser. Both assessment sections validate the 5x5 constraint (probability/impact 1..5, derived level)
- [ ] ACC-002: Validates REQ-002 — the Pydantic model correctly validates required/optional fields, including the derived risk level, TARRA strategy closed set, scope list ≥1, and tags optional (absent/present)
- [ ] ACC-003: Validates REQ-003 — the parser produces a valid object tree; malformed input raises (structural `AssertionError` / field-level `pydantic.ValidationError`, matching the error-channel convention of `req`/`tsk`)
- [ ] ACC-004: Validates REQ-004 — all listed tools are implemented and registered (confirmed present in the regenerated `docs/MCP.md`)
- [ ] ACC-005: Validates REQ-005 — all listed resources are implemented and registered
- [ ] ACC-006: Validates REQ-006 — the `create_risk`/`update_risk` prompts narrate the correct tool sequence
- [ ] ACC-007: Validates REQ-007 — the bundled data resolves correctly from an actual, non-editable install
- [ ] ACC-008: Validates REQ-008 — `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` report no drift

### Scope

**Included:**
- `rsk` markdown schema (frontmatter + body), with 5x5 initial/residual assessment, TARRA strategy
- Pydantic model, parser, schema generation under `rsk/models/v1/`
- Full MCP surface (tools/resources/prompts/bundled data) mirroring `req`/`tsk`
- Tests mirroring the `tests/req/`/`tests/tsk/` layout and coverage

**Explicitly out of scope:**
- Risk interlinking (probability-impact correlation, risk dependency graphs)
- Aggregate views/reports (e.g. a risk-matrix chart across all `rsk` documents) — the summary fields of `specmgr://rsk/list` carry the per-document level and strategy for that purpose
- Cross-referencing `rsk` documents to other artifact types (REQ/UC/ADR)
- `specmgr rsk-toc`-style generation commands

### Dependencies

- Depends on: ADR ece4554b-... (domain-first hierarchy), ADR bc5e18ad-... (generic MarkdownFrontmatter base), `general/tools/_doc_paths.py` + `_packaged_data.py`, the `models/md` engine (in particular `MarkdownSection1WithComment`, `MarkdownSection2`, the generic `list[MarkdownStr]` engine `process_list_field`, and the `MarkdownListItem` custom-leaf precedent of `tsk`'s `TaskItem`)
- Blocks: none identified yet

### Design Notes

- **Body shape** — `Risk` (the body H1 class) subclasses `MarkdownSection1WithComment`...:

```

# {H1 title}

<!-- optional leading comment -->          comment: MarkdownComment | None

## Description description: MarkdownStr (mandatory)

{Risk scenario: cause, trigger, consequence}

## Scope scope: list[MarkdownStr] (>=1)

- {Affected system/component}
- {Another affected system}

## Initial Assessment initial_assessment: Assessment

- Probability: {1..5}
- Impact: {1..5}

## Strategy strategy: str (TARRA closed 5-value set)

{tolerate | assign | reduce | recover | avoid}

## Mitigation mitigation: MarkdownStr (mandatory)

{Treatment actions taken ("none" if strategy is tolerate)}

## Residual Assessment residual_assessment: Assessment

- Probability: {1..5}
- Impact: {1..5}

## Owner owner: MarkdownStr | None

{Responsible person/role}

## Tags tags: list[MarkdownStr] | None

- {tag}

## More Information more_information: MarkdownStr | None

{Free form}

```

- **5x5 matrix** — `Assessment` is a new `MarkdownSection2` leaf holding `probability: int` (1..5) and `impact: int` (1..5), parsed from the list items `- Probability: N`/`- Impact: N` (a `MarkdownListItem` subclass with computed fields, following the `tsk.TaskItem` precedent of parsing a non-standard marker, and the same eager-validation `model_validator` on the parent section to force computed-field evaluation). Each assessment derives `level: Literal["low","medium","high","very_high"]` from the product zones: 1–4 low, 5–9 medium, 10–14 high, 15–25 very high. Having two independent assessments (initial = before mitigation, residual = after mitigation) side by side makes the mitigation effect auditable: a sound `reduce` strategy should show residual < initial.
- **Strategy (TARRA)** — closed 5-value set `tolerate`/`assign`/`reduce`/`recover`/`avoid`; validated as a single-line H2 section body (mirroring the frontmatter-status narrowing approach in `ReqFrontmatter`, but at the body level).
- **Status** — `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open`: open = identified and under monitoring; mitigating = treatment in progress; accepted = residual risk formally accepted; occurred = the risk event materialized (tracked as an incident); closed = resolved/expired; dropped = removed from the register (not a real risk/duplicate/out of scope).
- **List summary** — `RskSummary` (for `specmgr://rsk/list`) carries id/title/status plus `initial_level`, `residual_level`, `strategy`, and the first scope entry, so a register-wide risk-matrix view can be built without reading each document.
- **Section order is enforced by the model**: title → optional comment → Description → Scope → Initial Assessment → Strategy → Mitigation → Residual Assessment → optional Owner → optional Tags → optional More Information.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for markdown document types

No new ADR is anticipated for this feature — the `Assessment` 5x5 parsing approach and TARRA closed set are scoped enough that they can be logged in this file's own Decisions Made without a full ADR.

### Task List

... (four phases mirroring feat-10)

#### Phase 1: Specification (commit 1)
- [ ] Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` — `RskFrontmatter` subclassing `MarkdownFrontmatter`, `type=Literal["rsk"]`, 6-value status set) — depends on: none — status: not-started
- [ ] Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`, `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with description/scope/initial_assessment/strategy/mitigation/residual_assessment/owner/tags/more_information; `Assessment` (MarkdownSection2, probability/impact int 1..5 computed from `- Probability:`/`- Impact:` list items, derived `level` computed field, parent-level eager-validation validator) — depends on: Task 1.1 — status: not-started
- [ ] Task 1.3: Create the reference `rsk` document (`rsk_reference.md`) exercising every field (initial 5x5 + residual 5x5 + all sections) as the parser round-trip fixture — depends on: Task 1.2 — status: not-started (placed under this feature folder, following `tsk_reference.md`/`req`'s convention)
- [ ] Task 1.4: `tests/rsk/models/v1/test_frontmatter.py`, `test_body.py`, `test_assessment.py` — structural + validation tests (status set, 5x5 bounds, derived-level zones, TARRA set, scope ≥1, tags absent/present) — depends on: Task 1.3 — status: not-started

#### Phase 2: Pydantic model & parser (commit 2)
- [ ] Task 2.1: `rsk/models/v1/document.py` (`RskDocument(frontmatter, body)`) — depends on: Task 1.3
- [ ] Task 2.2: `parse_rsk(text: str) -> RskDocument` — depends on: Task 2.1
- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` including initial_level/residual_level/strategy) — depends on: Task 2.1
- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/optional field — depends on: Task 2.1
- [ ] Task 2.5: `rsk_schema.json` via `generate_rsk_schema()` + register `"rsk"` in the `specmgr schema` registry (`_GENERATORS`) — depends on: Task 2.1
- [ ] Task 2.6: `tests/rsk/models/v1/test_parser.py` mirroring `TestParseTsk`'s shape — depends on: Task 2.2, Task 2.5

#### Phase 3: MCP surface (commit 3)
- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py` thin wrappers — depends on: Task 2.2
- [ ] Task 3.2: `parse_rsk(path)` tool wrapper — depends on: Task 3.1
- [ ] Task 3.3: `create_rsk(content)` tool (body only; MCP builds the frontmatter) — depends on: Task 3.1
- [ ] Task 3.4: `update_rsk(id, content)` tool — depends on: Task 3.1
- [ ] Task 3.5: `set_status_rsk(id, status)` tool — depends on: Task 3.1
- [ ] Task 3.6: `delete_rsk(id)` stub tool — depends on: Task 3.1
- [ ] Task 3.7: `validate_rsk(content, full=False)` tool — depends on: none
- [ ] Task 3.8: `get_rsk(id)` tool (id-based read; tool, not resource — per ADR ddfb1109-...) — depends on: Task 3.1
- [ ] Task 3.9: `get_rsk_example`/`get_rsk_template` tools + bundled data (`rsk/data/`) — depends on: Task 1.3
- [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources — depends on: Task 3.1, Task 2.5
- [ ] Task 3.11: `specmgr://rsk/example` and `specmgr://rsk/template` resources — depends on: Task 3.9
- [ ] Task 3.12: `pyproject.toml` package-data entry + pre-commit hook + CI step for the bundled `rsk_schema.json` — depends on: Task 2.5
- [ ] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10
- [ ] Task 3.14: Add `rsk` to the domain-import line in `server.py` — depends on: Tasks 3.2-3.13
- [ ] Task 3.15: `tests/rsk/tools/`, `tests/rsk/resources/`, `tests/rsk/prompts/` mirroring `tests/tsk/` — depends on: Tasks 3.1-3.14

#### Phase 4: Docs, CI wiring, and final verification (commit 4)
- [ ] Task 4.1: Regenerate `specmgr docs` — depends on: Phases 1-3
- [ ] Task 4.2: Regenerate `specmgr mcp-docs` — depends on: Phase 3
- [ ] Task 4.3: CI wiring — confirm the registry-driven steps cover `rsk`; only per-type steps are the bundled-copy step from Task 3.12 — depends on: Tasks 4.1, 4.2
- [ ] Task 4.4: Final verification pass — walk every ACC, run the full quality gate — depends on: Tasks 4.1-4.3

**Note:** ...

## Progress

### Current Status

**As of 2026-08-24**: Planning. GitHub issue #15 opened. Schema proposed (see Design Notes); awaiting review/confirmation of the attribute set before Phase 1.

### Blockers

None.

### Recent Updates

#### 2026-08-24T... (newest)
- Completed: feature folder created from `.specmgr/_template/v1/README.md`; GitHub issue #15 opened; schema + MCP surface planned, mirroring feat-10 (`tsk`)
- Next: review the proposed attribute set (Design Notes), then execute Phase 1
- Notes: ...

### Decisions Made

- **2026-08-24**: Target GitHub issue #15, opening it now (no earlier issue describes this feature) — Rationale: the `feat-NNN-slug` convention embeds the issue number; opening first avoids the rename pass (feat-10's Decisions Made) we did when the local branch came first.
- **2026-08-24**: Status vocabulary is the 6 values `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open` — Rationale: user-selected (question, 2026-08-24); purpose-fit to a risk lifecycle rather than reusing REQ's ADR-style 7-value set.
- **2026-08-24**: Initial and residual risk are modeled as two separate `Assessment` sections (both 5x5: probability 1..5, impact 1..5, derived level zone) around a `## Mitigation` section — Rationale: user requirement ("a separate 5x5 impact/probability matrix for BEFORE and AFTER mitigation"); the before/after juxtaposition makes the mitigation effect auditable.
- **2026-08-24**: Derived `level` is a product-zone computed field (1–4 low, 5–9 medium, 10–14 high, 15–25 very high) and is not stored in markdown — Rationale: the 5x5 matrix zones are a standard mapping; storing only probability/impact avoids stale derived values on round-trip (following the `TaskItem.checked` computed-field precedent).
- **2026-08-24**: `## Strategy` is a TARRA closed 5-value set (tolerate/assign/reduce/recover/avoid) — Rationale: user requirement; a single-line validated section.
- **2026-08-24**: `## Scope` is mandatory with ≥1 list entry; `## Tags`, `## Owner`, `## More Information` are optional — Rationale: "which systems are affected" is the core of a risk (a risk that affects nothing is not scoped); tags/owner/more-info follow ADR's optional `more_information` precedent.

### Related PRs / Commits

No PR opened yet. Work happens on the `feat-15-add-artifact-type-risk` branch from `dev`.
```

Hmm, wait, on the ordering of the Decisions Made entries — feat-10's Decisions Made is date-ordered. That's fine.

One detail: on the timestamp for Recent Updates — the template uses `YYYY-MM-DDTHH:mm:ssz`. I don't know the current time; I could use `date` in bash to get it. Let me grab it.

Also on the frontmatter field ordering: the template has id, version, status, created, updated. feat-10 has created, id, status, updated, version. Template (v1) is: id, version, status, created, updated. I'll follow the template ordering.

On `## Strategy` — I said "validated as a single-line H2 section body". In markdown terms, the section body is one line containing one of the five words. OK.

Another design question I should make explicit: should `strategy` be required? Yes — every risk in the register has a disposition. And `mitigation` required (allowing "none"). OK.

On `Assessment` parsing: list items `- Probability: 4` and `- Impact: 3`. Both required, each exactly one. Custom `MarkdownListItem` subclass `AssessmentValue` with a computed int field? Or two separate items, each `MarkdownListItem` with key/value. Simplest: an `Assessment` section with `probability: int` and `impact: int` fields, each parsed from a list item via the `process_list_field`-style mechanism... actually the engine's `process_list_field` handles `list[X]` fields. For two separate scalar fields, I might need two `list[X]` fields each with `max_length=1`... hmm, the exact mechanics are for implementation time (Phase 1/2). In the plan, I'll describe it at the right level: "parsed from the list items `- Probability: N`/`- Impact: N` (a `MarkdownListItem` subclass with computed fields, following the `tsk.TaskItem` precedent...)" — that's accurate enough and consistent with how feat-10 described TaskItem.

I'll also decide on the `level` zone thresholds. The classic 5x5 heat map often uses zones where the product p\*i gives:

```
I1 I2 I3 I4 I5
P1: 1  2  3  4  5
P2: 2  4  6  8 10
P3: 3  6  9 12 15
P4: 4  8 12 16 20
P5: 5 10 15 20 25
```

Zones by product: ≤4 low, 5–9 medium, 10–14 high, ≥15 very high. This is a common simple mapping. I'll use this and document it.

Next, the issue body. Keep it in #10's style:

```
Creates a new artifact type `Risk`:

* Abbreviation `rsk`
* Subfolder as `req`/`tsk`
* Resources: same as `req`
* Tools: same as `req`
* Prompts: `create_risk` and `update_risk`

Attributes:

* Frontmatter `status`: `open` / `mitigating` / `accepted` / `occurred` / `closed` / `dropped` (default `open`)
* H1 title, optional leading comment
* `## Description` (mandatory): risk scenario — cause, trigger, consequence
* `## Scope` (mandatory, list): which systems/components are affected
* `## Initial Assessment` (mandatory): 5x5 risk matrix — probability 1..5 and impact 1..5 before mitigation (derived level: low/medium/high/very high)
* `## Strategy` (mandatory): TARRA — `tolerate` / `assign` / `reduce` / `recover` / `avoid`
* `## Mitigation` (mandatory): treatment actions ("none" if strategy is `tolerate`)
* `## Residual Assessment` (mandatory): 5x5 matrix — probability 1..5 and impact 1..5 after mitigation
* `## Owner` (optional): responsible person/role
* `## Tags` (optional, list): free tags
* `## More Information` (optional): free form

This artifact is needed for risk registers within system specs: risks with an explicit before/after-mitigation 5x5 assessment (residual risk) and a TARRA response strategy, kept alongside requirements/use-cases as first-class managed artifacts.
```

Good. Next, the steps:

1. `gh issue create --title "Add artifact type Risk" --body ...` → get the number (should be 15).
2. `git switch -c feat-15-add-artifact-type-risk` (confirm the issue number first! If the number turns out to be different, name the branch accordingly).
3. `mkdir .specmgr/feat/feat-15-add-artifact-type-risk/` + write the README.

Let me also grab the current timestamp for Recent Updates. Run issue creation first, then everything else.

Actually one thought on the title: issue #10 was "Add artifact type TaskList" (no abbreviation in the title). The user wrote: 'add artifact type "risk" (RSK)'. Following the convention: "Add artifact type Risk". I'll use that.

For the issue body I'll use a heredoc. Use `--body-file` with a temp file, or use $'...' quoting. Simpler: write the body to /tmp with the write tool? The write tool writes files — /tmp/opencode is pre-approved. I'll write to /tmp/opencode/rsk-issue.md and then `gh issue create --title ... --body-file ...`. That avoids the quoting hassle.

Both decisions confirmed. Now I'll create the issue, then the branch and feature plan.

**Tool: write**

**Input:**

```json
{
  "filePath": "/tmp/opencode/rsk-issue-body.md",
  "content": "We create a new artifact type `Risk`:\n\n* abbreviation `rsk`\n* sub-folder as `req`/`tsk`\n* resources: same as `req`\n* tools: same as `req`\n* prompts: `create_risk` and `update_risk`\n\nAttributes:\n\n* frontmatter `status`: `open` / `mitigating` / `accepted` / `occurred` / `closed` / `dropped` (default `open`)\n* H1 title, optional leading comment\n* `## Description` (mandatory): risk scenario — cause, trigger, consequence\n* `## Scope` (mandatory, list): which system/component is affected\n* `## Initial Assessment` (mandatory): 5x5 risk matrix — probability 1..5 and impact 1..5 BEFORE mitigation (derived level: low / medium / high / very high)\n* `## Strategy` (mandatory): TARRA — `tolerate` / `assign` / `reduce` / `recover` / `avoid`\n* `## Mitigation` (mandatory): treatment measures (\"none\" if strategy is `tolerate`)\n* `## Residual Assessment` (mandatory): 5x5 risk matrix — probability 1..5 and impact 1..5 AFTER mitigation (residual risk)\n* `## Owner` (optional): responsible person/role\n* `## Tags` (optional, list): free-form tags\n* `## More Information` (optional): free-form\n\nThis artifact is needed for risk registers in system specifications: risks with an\nexplicit before/after mitigation 5x5 assessment (residual risk) and a TARRA response\nstrategy, kept as first-class managed artifacts alongside requirements and use cases.\n"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 56.1s)

_Thinking:_

Alright, let's try creating the issue.

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue create --title \"Add artifact type Risk\" --body-file /tmp/opencode/rsk-issue-body.md",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/15

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 57.7s)

_Thinking:_

Issue #15 has been created. Next:

1. Create branch `feat-15-add-artifact-type-risk` from dev
2. Create the feature folder and README

First, get the current timestamp, then write the README.

Issue #15 created. Now the branch and feature folder:

**Tool: bash**

**Input:**

```json
{
  "command": "git switch -c feat-15-add-artifact-type-risk && date +%Y-%m-%dT%H:%M:%S%:z",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
Switched to a new branch 'feat-15-add-artifact-type-risk'
2026-08-24T11:31:28+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 283.8s)

_Thinking:_

Alright, I'll create the feature README. I'll carefully write it out while following the template structure and the shape of feat-10.

**Tool: write**

**Input:**

````json
{
  "content": "---\nid: feat-15-add-artifact-type-risk\nversion: 1.0.0\nstatus: planning\ncreated: 2026-08-24\nupdated: 2026-08-24\n---\n\n# Feature: Add artifact type Risk (rsk)\n\n## Plan\n\n### Overview\n\nAdd a new markdown artifact type, `Risk` (abbreviation `rsk`), for maintaining risk\nregisters in system specifications. Every risk carries a 5x5 probability/impact\nassessment BEFORE mitigation (`## Initial Assessment`) and the same 5x5 assessment\nAFTER mitigation (`## Residual Assessment`), a TARRA response strategy\n(`## Strategy`: tolerate / assign / reduce / recover / avoid), the treatment\nmeasures bridging the two (`## Mitigation`), and the affected scope\n(`## Scope`). `rsk` follows the domain-first hierarchy and MCP surface already\nestablished by `req`/`tsk` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing\ntheir tools/resources shape almost exactly (per GitHub issue #15).\n\n### Requirements\n\n- [ ] REQ-001: Define the `rsk` markdown schema — frontmatter (`type=\"rsk\"`,\n  6-value status set: `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`,\n  default `open`) and body (H1 title, optional leading comment, mandatory\n  `## Description`, mandatory `## Scope` list (>=1 affected\n  system/component), mandatory `## Initial Assessment` (5x5: probability 1..5,\n  impact 1..5, derived level), mandatory `## Strategy` (TARRA 5-value closed\n  set), mandatory `## Mitigation`, mandatory `## Residual Assessment` (5x5,\n  same shape as initial), optional `## Owner`, optional `## Tags` list,\n  optional `## More Information`)\n- [ ] REQ-002: Pydantic models for `rsk` documents (`rsk/models/v1/` —\n  domain-first path, mirroring `tsk/models/v1/` and `req/models/v1/`)\n- [ ] REQ-003: Parse and validate `rsk` documents from markdown\n  (`parse_rsk`, mirroring `parse_tsk`/`parse_req`)\n- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`,\n  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,\n  `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`\n- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`,\n  `/example`, `/schema`, `/template`\n- [ ] REQ-006: MCP prompts — `create_risk`, `update_risk` (narrated tool\n  sequences, mirroring `req/prompts/create_req.py`/`update_req.py` and\n  `tsk/prompts/create_task.py`/`update_task.py`)\n- [ ] REQ-007: Packaged example/template/schema data (`rsk/data/`) via the\n  existing generic `general/tools/_packaged_data.py`, with the matching\n  `pyproject.toml` package-data entry, pre-commit hook, and CI step\n- [ ] REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema`\n  (new `rsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept\n  drift-free via pre-commit/CI\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/rsk_schema.json`,\n  `specmgr://rsk/schema`), reference `rsk` document (`rsk_reference.md`)\n  round-trips through the parser (`test_parses_full_reference_document`),\n  including both 5x5 assessments (probability/impact bounded 1..5, derived\n  level zone correct)\n- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required/optional\n  fields correctly, including the `Assessment` probability/impact/derived-level\n  split, the TARRA closed set, `Scope` (>=1) and the `Tags`/`Owner`/\n  `More Information` absent-vs-present cases (`tests/rsk/models/v1/`)\n- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree;\n  malformed input raises (structural `AssertionError` / field-level\n  `pydantic.ValidationError`, matching `req`/`tsk`'s error-channel convention)\n  — `tests/rsk/models/v1/test_parser.py`\n- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`), with\n  `create_rsk`/`update_rsk` validating body-only content the same way\n  `create_req`/`update_req`/`create_tsk`/`update_tsk` do\n- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`)\n- [ ] ACC-006: Verifies REQ-006 — `create_risk`/`update_risk` prompts narrate\n  the correct tool sequence (`tests/rsk/prompts/`)\n- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a\n  real, non-editable install, mirroring `req`'s (feat-6 Task 5.1) and `tsk`'s\n  (feat-10 ACC-007) own verification\n- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/\n  `specmgr mcp-docs` all report no drift after implementation\n\n### Scope\n\n**Included in this feature:**\n\n- Specification of the `rsk` markdown schema (frontmatter + body), including\n  the 5x5 initial/residual assessment, the TARRA strategy set, and the\n  before/after-mitigation structure\n- Pydantic models, parser, and schema generation under `rsk/models/v1/`\n- Full MCP surface (tools/resources/prompts/packaged data) mirroring\n  `req`/`tsk`\n- Tests mirroring `tests/req/`'s and `tests/tsk/`'s layout and coverage\n\n**Explicitly out of scope:**\n\n- Aggregated, register-wide views (e.g. a combined risk-matrix chart across\n  all `rsk` documents) — `RskSummary` (see `specmgr://rsk/list`) carries\n  `initial_level`/`residual_level`/`strategy` per document precisely so such a\n  view can be built later without reading each document\n- Cross-referencing/linking `rsk` documents to other artifact types\n  (REQ/UC/ADR) — not part of this feature\n- Risk relationships (dependency, correlation, common-cause analysis)\n- A `specmgr rsk-toc`-equivalent generation command or its own CI/pre-commit\n  drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`\n  already provide generically\n\n### Dependencies\n\n- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic\n  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614\n  (id-based reads as a tool, not a resource), `general/tools/_doc_paths.py`\n  and `_packaged_data.py`, the existing `models/md` engine — in particular\n  `MarkdownSection1WithComment`, `MarkdownSection2`, the generic\n  `list[MarkdownStr]` engine (`process_list_field`), and `tsk`'s\n  `TaskItem` custom-list-item-leaf precedent (parsing a non-standard marker\n  into computed fields with parent-level eager validation)\n- Blocks: None identified yet\n\n### Design Notes\n\n- **Body shape** — `Risk` (the body's H1 class) subclasses the existing\n  `MarkdownSection1WithComment` mixin (`models/md/`), reusing it as-is (no\n  new mixin needed):\n\n  ```\n  # {H1 title}\n  <!-- optional leading comment -->            comment: MarkdownComment | None\n\n  ## Description                               description: MarkdownStr  (mandatory)\n  {Risk scenario: cause, trigger, consequence}\n\n  ## Scope                                     scope: list[MarkdownStr]  (>=1)\n  - {Affected system / component}\n  - {Another affected system / component}\n\n  ## Initial Assessment                        initial_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Strategy                                  strategy: str  (TARRA closed 5-value set)\n  {tolerate | assign | reduce | recover | avoid}\n\n  ## Mitigation                                mitigation: MarkdownStr  (mandatory)\n  {Treatment measures; \"none\" if strategy is tolerate}\n\n  ## Residual Assessment                       residual_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Owner                                     owner: MarkdownStr | None\n  {Responsible person / role}\n\n  ## Tags                                      tags: list[MarkdownStr] | None\n  - {tag}\n\n  ## More Information                          more_information: MarkdownStr | None\n  {Free-form}\n  ```\n\n  Order is enforced by the model: title -> optional comment -> Description\n  -> Scope -> Initial Assessment -> Strategy -> Mitigation -> Residual\n  Assessment -> optional Owner -> optional Tags -> optional More Information.\n  The before/after pair (Initial Assessment ... Residual Assessment) is\n  separated by exactly the sections that explain the delta: `Strategy`\n  (chosen TARRA response) and `Mitigation` (the measures taken).\n\n- **5x5 matrix** — `Assessment` is a new `MarkdownSection2` leaf\n  (`rsk/models/v1/assessment.py`) holding `probability: int` (1..5) and\n  `impact: int` (1..5), parsed from the literal list items\n  `- Probability: N` / `- Impact: N` (a `MarkdownListItem` subclass with\n  computed fields, on the exact `tsk.TaskItem` precedent — including a\n  parent-level `model_validator(mode=\"after\")` forcing eager evaluation,\n  since computed fields are never validated at construction otherwise).\n  Each assessment derives `level:\n  Literal[\"low\", \"medium\", \"high\", \"very_high\"]` as a computed field from\n  the probability x impact product zones: 1-4 low, 5-9 medium, 10-14 high,\n  15-25 very high. `level` is never stored in the markdown (no stale\n  derived value on round-trip, same convention as `TaskItem.checked`).\n\n- **Strategy (TARRA)** — `## Strategy` is a single-line H2 section whose\n  content is validated against the closed 5-value set `tolerate`/`assign`/\n  `reduce`/`recover`/`avoid` (same narrowing approach `ReqFrontmatter`\n  applies to its `status` field, at body-section level). Mandatory: every\n  risk in a register has a disposition.\n\n- **Frontmatter status** — `open`/`mitigating`/`accepted`/`occurred`/\n  `closed`/`dropped`, default `open`: a purpose-fit risk lifecycle (user-\n  selected 2026-08-24) rather than reusing REQ's 7-value ADR-like set —\n  `open` = identified and monitored; `mitigating` = treatment in progress;\n  `accepted` = residual risk formally accepted; `occurred` = the risk event\n  materialized (tracked as incident); `closed` = resolved/expired; `dropped`\n  = removed from the register (not a real risk, duplicate, or out of scope).\n\n- **List summary** — `RskSummary` (for `specmgr://rsk/list`) carries\n  `id`/`title`/`status` plus `initial_level`, `residual_level`, `strategy`,\n  and the first `scope` entry, so a register-wide risk-matrix view can be\n  built from the listing alone.\n\n- **Prompt naming** — `create_risk`/`update_risk` follow the\n  `tsk`-prompt precedent of the issue's literal wording (issue #15 names\n  both), not the `rsk`-prefixed convention the tools/resources use.\n\n### Related ADRs\n\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by\n  document-type domain (domain-first hierarchy)\n- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for\n  markdown document types\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a\n  tool (get_rsk), not a resource\n\nNo new ADR is anticipated for this feature — the `Assessment` 5x5 parsing\napproach, the TARRA closed set, and the 6-value status set are scoped enough\nto log only in this file's own Decisions Made, not a full ADR.\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself — there is no separate \"planned\" vs. \"executed\" list to keep in\nsync; a task's line *is* its current status. Update it in place as work\nprogresses (edit, don't duplicate).\n\n**Execution approach** (to confirm at Phase 1 start, see Decisions Made):\neach phase below is delegated to the `implementation-specialist` subagent as\none unit (implementation + its own mirrored tests together, not a separate\nlater test phase), reviewed and quality-gated (ruff format/check, vulture,\nfull `unittest` suite) by the orchestrator, then committed as one\nConventional Commit per phase — the `feat-10` (tsk) 4-phase/4-commit shape.\n\n#### Phase 1: Specification (commit 1)\n\n- [ ] Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` —\n  `RskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal[\"rsk\"]`,\n  6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/\n  `dropped`) — depends on: none — status: not-started\n- [ ] Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`,\n  `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with\n  `description`/`scope`/`initial_assessment`/`strategy`/`mitigation`/\n  `residual_assessment`/`owner`/`tags`/`more_information`; `Assessment`\n  (new `MarkdownSection2` leaf: `probability`/`impact` int 1..5 parsed from\n  `- Probability: N`/`- Impact: N` list items via a `MarkdownListItem`\n  subclass with computed fields, derived `level` computed field, parent-\n  level eager-validation `model_validator` on the `Risk` H1 per the\n  `TaskItem` precedent) — depends on: Task 1.1 — status: not-started\n- [ ] Task 1.3: Create a reference `rsk` document (`rsk_reference.md`)\n  exercising every field (full initial + residual 5x5 pair, all mandatory\n  and optional sections), used as the parser's round-trip test fixture —\n  depends on: Task 1.2 — status: not-started (placed at\n  `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md`, mirroring\n  `tsk_reference.md`'s own location convention, not `rsk/data/`)\n- [ ] Task 1.4: `tests/rsk/models/v1/test_frontmatter.py`,\n  `test_body.py`/`test_assessment.py` — structural + validation tests\n  mirroring `tests/tsk/models/v1/`: status set, 5x5 bounds and derived-\n  level zones (all four zone boundaries: 4/5, 9/10, 14/15), TARRA closed\n  set, `Scope` >=1, `Tags`/`Owner`/`More Information` absent-vs-present —\n  depends on: Task 1.3 — status: not-started\n\n#### Phase 2: Pydantic Models & Parser (commit 2)\n\n- [ ] Task 2.1: `rsk/models/v1/document.py` (`RskDocument(frontmatter,\n  body)`, mirroring `TskDocument`) — depends on: Task 1.3 — status:\n  not-started\n- [ ] Task 2.2: Implement `parse_rsk(text: str) -> RskDocument` (mirrors\n  `parse_tsk`/`parse_req`) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry, for the\n  `specmgr://rsk/list` resource) — depends on: Task 2.1 — status:\n  not-started\n- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/\n  optional field (schema-quality parity with REQ/TSK's own Task 2.4\n  audits) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.5: Draft `rsk_schema.json` via `generate_rsk_schema()`\n  (mirroring `generate_req_schema`/`generate_tsk_schema` in\n  `commands/schema.py`, calling `RskDocument.model_json_schema()`) +\n  register `\"rsk\"` in the `specmgr schema` doc-type generator registry\n  (`_GENERATORS`) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.6: `tests/rsk/models/v1/test_parser.py` — mirrors\n  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,\n  defaults-when-absent, invalid status, malformed structure, out-of-range\n  probability/impact, invalid TARRA word, missing Scope entry) — depends\n  on: Task 2.2, Task 2.5 — status: not-started\n\n#### Phase 3: MCP Surface (commit 3)\n\n- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,\n  thin wrappers over `general/tools/_doc_paths.py` (mirrors\n  `tsk/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:\n  not-started\n- [ ] Task 3.2: `parse_rsk(path: str) -> RskDocument` tool wrapper\n  (`rsk/tools/parse_rsk.py`, mirroring `tsk/tools/parse_tsk.py` — reads a\n  filepath from disk, delegates to the model-layer `parse_rsk`) — depends\n  on: Task 3.1 — status: not-started\n- [ ] Task 3.3: `create_rsk(content: str) -> RskDocument` tool (body-only\n  content, MCP builds frontmatter: `id`, `type=\"rsk\"`, `status=\"open\"`,\n  `created=updated=now`, `version`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: `update_rsk(id, content) -> RskDocument` tool (whole-body\n  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps\n  `updated`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: `set_status_rsk(id, status) -> RskDocument` tool (only path\n  that changes `status`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.6: `delete_rsk(id) -> NoReturn` stub tool — depends on: Task\n  3.1 — status: not-started\n- [ ] Task 3.7: `validate_rsk(content, full=False) -> bool` tool — depends\n  on: none — status: not-started\n- [ ] Task 3.8: `get_rsk(id) -> RskDocument` tool (id-based single-document\n  read; tool, not resource — per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614)\n  — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.9: `get_rsk_example`/`get_rsk_template` tools + packaged data\n  (`rsk/data/rsk_example.md`, `rsk/data/rsk_template.md`) via\n  `general/tools/_packaged_data.py` — depends on: Task 1.3 — status:\n  not-started\n- [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources\n  (packaged `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`) —\n  depends on: Task 3.1, Task 2.5 — status: not-started\n- [ ] Task 3.11: `specmgr://rsk/example` and `specmgr://rsk/template`\n  resources — depends on: Task 3.9 — status: not-started\n- [ ] Task 3.12: `pyproject.toml` package-data entry for\n  `biz.dfch.specmgr.rsk` (`data/*.md`, `data/*.json`), pre-commit hook +\n  CI step for the packaged `rsk_schema.json` copy (mirroring\n  `specmgr-schema-tsk-package`) — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — narrate\n  the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)\n  — depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10 — status: not-started\n- [ ] Task 3.14: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers) —\n  depends on: Tasks 3.2-3.13 — status: not-started\n- [ ] Task 3.15: `tests/rsk/tools/...`, `tests/rsk/resources/...`,\n  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/\n  resources/`/`tests/tsk/prompts/` layout — depends on: Tasks 3.1-3.14 —\n  status: not-started\n\n#### Phase 4: Docs, CI wiring & final verification (commit 4)\n\n- [ ] Task 4.1: `specmgr docs` regeneration (new `rsk` modules picked up) —\n  depends on: Phase 1-3 complete — status: not-started\n- [ ] Task 4.2: `specmgr mcp-docs` regeneration (new tools/resources/\n  prompts appear in `docs/MCP.md`) — depends on: Phase 3 complete — status:\n  not-started\n- [ ] Task 4.3: CI wiring — confirm the Python-3.13-only `specmgr schema`/\n  `specmgr docs`/`specmgr mcp-docs` steps in `.github/workflows/ci.yml`\n  cover `rsk` with no separate per-type step needed (registry-driven,\n  mirroring `req`/`tsk`'s own wiring) — depends on: Task 4.1, Task 4.2 —\n  status: not-started\n- [ ] Task 4.4: Final verification pass — walk every ACC-001..008 below and\n  confirm each is actually satisfied; run the full quality gate (ruff\n  format/check, pylint advisory, vulture, unittest, `specmgr docs`,\n  `specmgr schema`, `specmgr mcp-docs` drift checks) once more end-to-end —\n  depends on: Tasks 4.1-4.3 — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder\ncreated from `.specmgr/_template/v1/README.md`. Full schema and MCP surface\nproposed (see Design Notes and Task List), mirroring `feat-10` (tsk)'s\n4-phase/4-commit shape. Awaiting review/confirmation of the proposed\nattribute set before Phase 1 starts.\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### 2026-08-24T11:31:28+02:00 (newest)\n\n- Completed: opened GitHub issue #15 (\"Add artifact type Risk\"); created\n  branch `feat-15-add-artifact-type-risk` from `dev`; drafted this feature\n  plan (schema with 5x5 initial/residual assessment, TARRA strategy,\n  6-value status, scope/tags/owner/more-information) modeled on\n  `feat-10-add-artifact-type-tasklist`\n- Next: user review of the proposed attribute set (Design Notes); then\n  Phase 1 (Specification)\n- Notes: `Assessment` parsing reuses `tsk.TaskItem`'s custom-list-item-leaf +\n  eager-validation precedent; no new ADR anticipated\n\n### Decisions Made\n\n- **2026-08-24**: Target GitHub issue #15, opened up front (no earlier issue\n  describes this feature) — rationale: the `feat-NNN-slug` convention\n  embeds the issue number; opening it first avoids the branch/folder rename\n  pass `feat-10` did when its local branch predated its issue number.\n- **2026-08-24**: Frontmatter `status` is the 6-value set `open`/\n  `mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open` —\n  rationale: user-selected (question, 2026-08-24); purpose-fit to a risk\n  lifecycle rather than reusing REQ's 7-value ADR-like set or tsk's 4-value\n  todo set.\n- **2026-08-24**: Before/after mitigation is modeled as two separate\n  `Assessment` sections (`## Initial Assessment` and `## Residual\n  Assessment`), each 5x5 (probability 1..5, impact 1..5), with `## Strategy`\n  and `## Mitigation` between them — rationale: user requirement for \"a\n  separate risk matrix impact/probability of 5x5 for BEFORE and AFTER\n  mitigation (residual risk)\"; the juxtaposition makes the mitigation\n  effect directly auditable (a sensible `reduce` strategy shows\n  residual < initial).\n- **2026-08-24**: The derived risk `level` (`low`/`medium`/`high`/`very_\n  high`) is a computed field from the probability x impact product zones\n  (1-4 low, 5-9 medium, 10-14 high, 15-25 very high), never stored in the\n  markdown — rationale: keeps the 5x5 mapping in one place and avoids stale\n  derived values on round-trip, following `tsk.TaskItem.checked`'s\n  computed-field convention.\n- **2026-08-24**: `## Strategy` is the TARRA closed 5-value set `tolerate`/\n  `assign`/`reduce`/`recover`/`avoid`, mandatory, single-line validated —\n  rationale: user requirement; same narrowing approach `ReqFrontmatter`\n  uses for its `status` field.\n- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected\n  system/component); `## Owner`, `## Tags`, `## More Information` are\n  optional — rationale: scope answers \"which system is affected\" and is\n  central to a risk (user requirement); the remaining three follow ADR's\n  optional `more_information` precedent and keep the schema lean.\n\n### Related PRs / Commits\n\nNo PR opened yet. Work happens on branch `feat-15-add-artifact-type-risk`\n(from `dev`), one Conventional Commit per phase (see Execution approach).\n",
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md"
}
````

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 68.1s)

_Thinking:_

Let's verify the file we created and check git status. Also, I want to double-check a few details:

1. I wrote "specmgr-schema-tsk-package" as the pre-commit hook name in Task 3.12 — I should verify the actual hook name in .pre-commit-config.yaml so that the plan's description is accurate.
2. Confirm that the feat-10 hook name for tsk exists.

Let me check .pre-commit-config.yaml.

Let me verify the pre-commit hook naming I referenced in Task 3.12 matches the actual config:

**Tool: grep**

**Input:**

```json
{
  "include": ".pre-commit-config.yaml",
  "path": "/home/user/src/biz.dfch.SpecMgr",
  "pattern": "schema.*(req|tsk|uc|package)"
}
```

**Output:**

```
Found 12 matches
/home/user/src/biz.dfch.SpecMgr/.pre-commit-config.yaml:
  Line 63:           create_adr's schema without touching adr/tools/*.py), so this

  Line 96:       - id: specmgr-schema-req-package

  Line 97:         name: specmgr schema (req package copy)

  Line 108:         entry: uv run --frozen specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data

  Line 113:       - id: specmgr-schema-uc-package

  Line 114:         name: specmgr schema (uc package copy)

  Line 125:         entry: uv run --frozen specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data

  Line 130:       - id: specmgr-schema-tsk-package

  Line 131:         name: specmgr schema (tsk package copy)

  Line 142:         entry: uv run --frozen specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data

  Line 147:       - id: specmgr-schema-qa-package

  Line 148:         name: specmgr schema (qa package copy)

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 97.7s)

_Thinking:_

The hook ID naming convention is `specmgr-schema-{type}-package` — my reference to `specmgr-schema-tsk-package` is accurate.

Next, check git status to confirm that the new files are visible, and do a final review of the README. The plan is complete. Summarize to the user:

1. Issue #15 has been created
2. Branch `feat-15-add-artifact-type-risk` has been created from dev
3. Created the feature plan at `.specmgr/feat/feat-15-add-artifact-type-risk/README.md`
4. Proposed attributes (a concise summary of the design)

Keep the response concise (under 4 lines is ideal, but here a short structured summary is reasonable — the user is asking for the proposed attributes, and that's in the plan. I should briefly indicate the main points). Per the system prompt, unless details are requested, keep responses to under 4 lines. The user asked me to "propose typical attributes for 'risk'" — the proposal is inside the feature plan. In the chat, I should concisely summarize the proposed attribute set. Let me make it a compact list.

Hook ID convention confirmed (`specmgr-schema-tsk-package` matches). Feature is set up:

**Created:**

- GitHub issue #15: https://github.com/dfch/biz.dfch.SpecMgr/issues/15
- Branch `feat-15-add-artifact-type-risk` (from `dev`)
- Plan: `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` (modeled on feat-10's 4-phase/4-commit shape)

**Proposed `rsk` schema** — frontmatter: `type="rsk"`, `status` = `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped` (default `open`). Body (order enforced):

| Section | Required | Content |
|---|---|---|
| `## Description` | yes | risk scenario: cause, trigger, consequence |
| `## Scope` | yes (>=1) | affected system(s)/component(s) as a list |
| `## Initial Assessment` | yes | 5x5: `- Probability: 1..5`, `- Impact: 1..5` + derived level |
| `## Strategy` | yes | TARRA: `tolerate`/`assign`/`reduce`/`recover`/`avoid` |
| `## Mitigation` | yes | treatment measures ("none" if `tolerate`) |
| `## Residual Assessment` | yes | 5x5 after mitigation, same shape |
| `## Owner` | no | responsible person/role |
| `## Tags` | no | free-form tag list |
| `## More Information` | no | free-form (mirrors ADR's) |

Design notes worth flagging:

- **Derived risk level** is a computed field from the product zones (1–4 low, 5–9 medium, 10–14 high, 15–25 very high) — never stored in the markdown, same convention as `tsk`'s `TaskItem.checked`. This is what makes each 5x5 pair a true matrix cell, and `RskSummary` will expose `initial_level`/`residual_level`/`strategy` in `specmgr://rsk/list` for a register-wide matrix view.
- **Parsing**: `Assessment` reuses `tsk.TaskItem`'s precedent (custom list-item leaf + parent-level eager validation) for the `- Probability: N` markers.
- **Out of scope**: cross-referencing to REQ/UC/ADR, risk relationships, aggregated charts.

Review the plan — once you confirm the attribute set, Phase 1 (Specification) can start.

______________________________________________________________________

## User

- see https://www.consuunt.com/tara-framework/ for the correct words: Transfer, Accept, Reduce, Avoid, allow only valid TARA words
- cause, trigger, consequence shall be separate sections (level 2)
- explain the structure of the initial/resdiual assessment, give an example

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 127.4s)

_Thinking:_

User feedback on the plan:

1. TARRA → TARA framework (Transfer, Accept, Reduce, Avoid) — see https://www.consuunt.com/tara-framework/ — allow only valid TARA words
2. cause, trigger, consequence should be separate H2 sections (not one "Description" section containing all three)
3. Explain the structure of the initial/residual assessment, with examples

So what I should do is:

1. Fetch the consuunt TARA page and confirm the exact wording/definitions (good for citing in the plan).
2. Update the feature README:
   - Replace TARRA with TARA: strategy closed set = `transfer`/`accept`/`reduce`/`avoid` (4 words). Also update the issue body! Issue #15 currently says TARRA with 5 words. Should update the GitHub issue too — `gh issue edit 15`.
   - Replace `## Description` with three separate H2 sections: `## Cause`, `## Trigger`, `## Consequence`. (Order: Cause → Trigger → Consequence is the natural risk-scenario order.)
   - Add an explanation + example for the initial/residual assessment structure (e.g. a concrete example showing probability/impact values and derived levels).
   - Update REQ-001, design notes, decisions, ACC, task list descriptions accordingly.
   - Frontmatter status `accepted` — hmm, this is fine as a lifecycle status, unrelated to TARA.

Let me fetch the page first.

Then edit the README. There are multiple spots to update:

- Overview: "TARRA response strategy (tolerate / assign / reduce / recover / avoid)" → "TARA response strategy (transfer / accept / reduce / avoid)"
- REQ-001: body list — replace `## Description` with `## Cause`, `## Trigger`, `## Consequence`; TARRA 5-value closed set → TARA 4-value closed set
- ACC-002: "TARRA closed set" → "TARA closed set"
- Design Notes body-shape block: replace Description section with three sections; change strategy line; add explanation of Assessment
- Add "Assessment structure" design note with example
- Decisions Made: update the TARRA entry; add a new decision entry for TARA (user correction) and cause/trigger/consequence split
- Task list: Task 1.2 (strategy TARRA → TARA), 1.4 ("TARRA closed set" → "TARA closed set"), 2.6 ("invalid TARRA word" → "invalid TARA word"), 3.3 fine.
- Recent Updates: add an entry about the 2026-08-24 revision.
- Prompt naming note: "create_risk/update_risk" unchanged.

Also update GitHub issue #15 body: TARRA → TARA words; Description → Cause/Trigger/Consequence.

Wait — let me double-check the TARA words: Transfer, Accept, Reduce, Avoid. Yes, classic TARA. Let me fetch the page and confirm the exact definitions so I can cite them accurately in the plan.

On the assessment example — let me make a concrete one:

```
## Initial Assessment
- Probability: 4
- Impact: 3
```

→ product 12 → level `high`

```
## Mitigation
Add input validation on the file-upload endpoint and restrict the parser
to a whitelist of allowed formats.

## Residual Assessment
- Probability: 2
- Impact: 3
```

→ product 6 → level `medium`

This nicely demonstrates the before/after auditability: high → medium.

Zone table:
| p \\ i | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | low (1) | low (2) | low (3) | low (4) | medium (5) |
| 2 | low (2) | low (4) | medium (6) | medium (8) | high (10) |
| 3 | low (3) | medium (6) | medium (9) | high (12) | very high (15) |
| 4 | low (4) | medium (8) | high (12) | high (16) | very high (20) |
| 5 | medium (5) | high (10) | high (15) | very high (20) | very high (25) |

Verify zones: 1–4 low; 5–9 medium; 10–14 high; 15–25 very high.

- (1,5)=5 medium ✓
- (2,5)=10 high ✓
- (3,5)=15 very high ✓
- (4,3)=12 high ✓
- (5,3)=15 very high ✓
- (4,4)=16 very high ✓
  Good.

Should I include the full 5x5 zone matrix table in the plan? It would be a nice concrete artifact — yes, I'll include it in a Design Notes "Assessment structure" entry.

Now, on cause/trigger/consequence as separate sections: are they all mandatory? A risk scenario classically needs all three (cause → trigger → consequence). I'll make all three mandatory (each a MarkdownStr H2 section). Order: Cause, Trigger, Consequence.

Also to consider: `## Scope` — keep it. The body order becomes:
title → optional comment → Cause → Trigger → Consequence → Scope → Initial Assessment → Strategy → Mitigation → Residual Assessment → Owner → Tags → More Information.

Now let me fetch the TARA page and confirm the wording/definitions.

**Tool: webfetch**

**Input:**

```json
{
  "url": "https://www.consuunt.com/tara-framework/",
  "format": "markdown"
}
```

**Output:**

```
          TARA Framework explained in a Practical way with Examples.                                          

Toggle navigation

**[![Consuunt](https://www.consuunt.com/wp-content/uploads/2022/07/Logo-Image-Consuunt.png "Consuunt")](https://www.consuunt.com)**

-   [Content](https://www.consuunt.com/content/ "Content")
-   [Your Project](https://www.consuunt.com/business-analysis-request/ "Your Project")
-   [](#)
    
     
    

-   [Leadership](https://www.consuunt.com/leadership/ "Leadership")
-   [About us](https://www.consuunt.com/about-us/ "About us")
-   [Español](https://www.consuunt.es "Español")

# TARA Framework

## What is the TARA Framework?

The **TARA Framework** is a **Tool that helps to Assess Risks and How to Manage them**.

To do so, it proposes to **classify Risks according to 2 variables**:

-   The **Probability** of these Risks occurring.
-   The **Impact** these Risks would have.

This model then **defines 4 scenarios** **depending on whether these variables have High or Low values**.

It’s name is an acronym for the **Strategies proposed** in each scenario:

-   **Transfer** the Risk.
-   **Avoid** the Risk.
-   **Reduce** the Risk.
-   **Accept** the Risk.

## The Four Scenarios of the TARA Framework

![](https://www.consuunt.com/wp-content/uploads/2021/04/TARA-Framework-Template.gif)

**1\. Transfer** Strategy: Different parties should Share the Risk.

-   **When the Probability is reduced, people are willing to share Risks**.

**2\. Avoid** Strategy: When Probability and Impact are High, Risk should be avoided.

-   In these situations, **you should not even analyze potential gains**.

**3\. Reduce** Strategy: To reduce exposure to the Risk and contain potential effects.

-   In this scenario **your main Goal is not ta have a large exposure to the Risk**.

**4\. Accept** Strategy: If the Impact and the Odds are low, you can Accept a Risk.

-   In these scenarios, **you should only worry about the Outcome, not Risks**.

Before sharing some examples with you, we will give you some **Tips on How to use the TARA Framework**:

## How to use the TARA Framework

**All Risks can be mitigated in different ways**.

-   There is always a way to reduce exposure to Risk.

**Avoid “Paralysis by Analysis”**.

-   Risks must be handled, but don’t let your Analysis paralyze your Actions.

**When looking for Risk-sharing Partners, Highlight the low odds**.

-   Or How, by sharing the Risk, both of you would reduce your chances of failure.

**Be disciplined and Don’t get obsessed with potential Gains**.

-   If your TARA Framework says to Avoid Risk, Avoid it or try to Reduce it.

Now, let’s see some examples:

## TARA Framework examples

We’ll now analyze **4 examples that perfectly explain each scenario of the TARA Framework**.

Let’s begin:

### Electric Car - Transfer TARA Framework example

![](https://www.consuunt.com/wp-content/uploads/2021/04/TARA-Framework-example-Transfer-example-300x186.gif)

**The Electric vehicle** (either using batteries or Hydrogen Fuel cells) **seems to be the next big thing**…

…. Or at least, it seems…

And that “seems” is the problem.

**Modifying a traditional manufacturing line** to produce Electric Vehicles **costs billions of dollars**.

-   The manufacturing process is very different.

**What if finally the demand for the Electric Vehicle is not as great as expected** **in the long term?**

-   The probability seems to be reduced… But there is one probability.

That is why **Car companies are sharing the costs of developing Batteries, Charging Stations, etc**.

Currently there are different associations of Automobile Companies to develop electric vehicles together.

-   **Impact** of Potential losses in case the Electric vehicle doesn’t take off: **High**.
-   **Probability** that the Electric vehicle finally doesn’t take off at all: **Low**.

**They are Transferring the Risk that the Demand for Electric Vehicles will not increase as much as expected**.

-   Or that it takes longer than expected.

### Bitcoin - Avoid TARA Framework example

![](https://www.consuunt.com/wp-content/uploads/2021/04/TARA-Framework-example-Avoid-example.jpg)

**Tesla recently allowed its customers to pay with Bitcoin**.

-   They have had to modify their accounting to allow this payment method.

Is this a good idea for an average Business? No.

-   The **Probability** of Bitcoin crashing is: **High**.
-   The **Impact** this drop would have on your Business would be: **High**.

**The TARA framework tells us to avoid allowing sales in Bitcoin**.

Is there anything you could do to mitigate this Risk?

-   Yes.

**You could only allow a limited amount of sales in Bitcoin**.

The Risk of Bitcoin crashing would remain intact but its Impact would diminish.

How many sales should you allow?

-   You should develop a more detailed TARA Framework to find out.

### Stocks - Reduce TARA Framework example

![](https://www.consuunt.com/wp-content/uploads/2021/04/TARA-Framework-example-Reduce-example-300x179.gif)

Now, let’s imagine that **you have some savings** (we hope you do).

-   And, as you are an Amateur Investor, **you keep half of your savings in Stocks**.

Although **you have** **generally** **chosen “good” stocks** you have a pretty diverse portfolio.

-   You hold Coca-Cola, but also small volatile companies.

-   The **Probability** of these Stocks to fall is relatively **High**.
-   The **Impact** this drop would cause to your Savings is: **Low**.

**The TARA Framework tells you that you should Reduce your exposure to the Risk**.

What do you do?

**You sell your volatile Stocks and only keep the best ones; the solid Companies**.

In this way, **the Probability of falling is reduced** and you can take the Risk.

### A New Product - Accept TARA Framework example

![](https://www.consuunt.com/wp-content/uploads/2021/04/TARA-Framework-example-Accept-example-300x176.gif)

Have you seen Tesla’s Cybertruck?

-   It is a weird Electric SUV with an eccentric design.

What was Tesla thinking when they decided to launch that model?

Well, we imagine that, **with that Linear Design**, **Stamping costs are Reduced**.

-   Curves are much more difficult to handle for a Press.

In addition, we imagine that the **Interior, the Materials, the Batteries used**… **Are common with those of other Tesla models**.

We believe it has been carefully designed to be **cheap to produce but satisfying to ride**.

-   Being also, original.

Also, and most importantly, **there are millions of Tesla fans who would buy any design proposed by Elon Musk**.

-   The **Probability** that the car is a failure is: **Low**.
-   The **Impact** that this failure would cause on the company would be: **Low**.

**According to the TARA Framework, Tesla should be not worried its Cybertruck.**

Even if it fails, we are almost certain that the shared costs with other models would reduce its economic impact.

-   [Business Plan](https://www.consuunt.com/business-plan/)
    -   [Basic Concepts](#)
        -   [Economies of Scale](https://www.consuunt.com/economies-of-scale/)
        -   [Business Plan for Beginners](https://www.consuunt.com/business-plan-for-entrepreneurs/)
        -   [Business Plan Basics](https://www.consuunt.com/business-plan-basics/)
        -   [Costs](https://www.consuunt.com/costs/)
        -   [How to write a Business Plan](https://www.consuunt.com/how-writing-a-business-plan/)
    -   [Advanced Concepts](#)
        -   [Cash Flow Calculation](https://www.consuunt.com/cash-flow-calculation/)
    -   [Fundraising](#)
        -   [Raising Funds for a Business](https://www.consuunt.com/raising-funds-for-a-business/)
        -   [4 C’s of Credit](https://www.consuunt.com/4-cs-of-credit/)
    -   [Business Plan Templates](https://www.consuunt.com/business-plan-templates/)
-   [Marketing](https://www.consuunt.com/marketing/)
    -   [Customer Oriented](#)
        -   [Customer Insight](https://www.consuunt.com/customer-insight/)
        -   [Customer Experience](https://www.consuunt.com/customer-experience/)
        -   [Customer Pain Points](https://www.consuunt.com/customer-pain-points/)
        -   [4C Marketing Model](https://www.consuunt.com/4c-marketing-model/)
        -   [AIO Model](https://www.consuunt.com/aio-model/)
        -   [RFM Model](https://www.consuunt.com/rfm-model/)
        -   [RATER Model](https://www.consuunt.com/rater-model/)
    -   [Product Oriented](#)
        -   [Augmented Product](https://www.consuunt.com/augmented-product/)
        -   [Product Mix](https://www.consuunt.com/product-mix/)
        -   [Unique Selling Proposition](https://www.consuunt.com/unique-selling-proposition/)
        -   [DAGMAR Model](https://www.consuunt.com/dagmar-model/)
    -   [Brand Oriented](#)
        -   [Branding](https://www.consuunt.com/branding/)
        -   [Marketing Storytelling](https://www.consuunt.com/marketing-storytelling/)
        -   [Content Marketing](https://www.consuunt.com/content-marketing/)
    -   [Market Research](#)
        -   [Psychographics](https://www.consuunt.com/psychographics/)
        -   [Barnum Effect](https://www.consuunt.com/barnum-effect/)
        -   [Market Segmentation](https://www.consuunt.com/market-segmentation/)
        -   [Market Research & Big Data](https://www.consuunt.com/market-research-and-big-data/)
        -   [Marketing to Generation Z](https://www.consuunt.com/marketing-to-generation-z/)
    -   [Implementation](#)
        -   [AIDA Model](https://www.consuunt.com/aida-model/)
        -   [4P Marketing Mix](https://www.consuunt.com/4p-marketing-mix/)
        -   [7P Marketing Mix](https://www.consuunt.com/7p-marketing-mix/)
        -   [Sales Funnel](https://www.consuunt.com/sales-funnel/)
        -   [Loyalty Ladder](https://www.consuunt.com/loyalty-ladder/)
        -   [RACE Planning](https://www.consuunt.com/race-planning/)
        -   [Push and Pull Marketing](https://www.consuunt.com/push-and-pull-marketing/)
        -   [Marketing Strategy](https://www.consuunt.com/marketing-strategy/)
    -   [Marketing Templates](https://www.consuunt.com/marketing-templates/)
-   [Entrepreneurship](https://www.consuunt.com/entrepreneurship/)
    -   [Starting your Business](#)
        -   [Starting your own business](https://www.consuunt.com/starting-your-own-business/)
        -   [From Startup to a Business](https://www.consuunt.com/from-startup-to-a-business/)
        -   [Entrepreneur FAQs](https://www.consuunt.com/entrepreneur-faqs/)
        -   [Start your Business Idea](https://www.consuunt.com/how-to-start-your-business-idea/)
        -   [Entrepreneur Golden Rules](https://www.consuunt.com/entrepreneurship-golden-rules/)
    -   [Creative Methods](#)
        -   [Innovate or Imitate?](https://www.consuunt.com/innovate-or-imitate/)
        -   [Design Thinking](https://www.consuunt.com/design-thinking/)
        -   [C-K Theory](https://www.consuunt.com/c-k-theory/)
        -   [SCAMPER Model](https://www.consuunt.com/scamper-model/)
        -   [Hook Model](https://www.consuunt.com/hook-model/)
        -   [AAR Process](https://www.consuunt.com/aar-process/)
        -   [Work From Home](https://www.consuunt.com/work-from-home/)
    -   [Growing the Business](#)
        -   [Growth strategies for Startups](https://www.consuunt.com/growth-strategies-for-startups/)
        -   [VMOST Analysis](https://www.consuunt.com/vmost-analysis/)
        -   [3P Framework](https://www.consuunt.com/3p-framework/)
        -   [SOAR Analysis](https://www.consuunt.com/soar-analysis/)
        -   [TELOS Analysis](https://www.consuunt.com/telos-analysis/)
    -   [Raising Money](#)
        -   [5 C’s of Entrepreneurship](https://www.consuunt.com/5-cs-of-entrepreneurship/)
        -   [Crowdfunding](https://www.consuunt.com/crowdfunding/)
        -   [BATNA & ZOPA Negotiation](https://www.consuunt.com/batna-and-zopa-negotiation/)
        -   [Entrepreneur with no Money](https://www.consuunt.com/entrepreneur-with-no-money/)
    -   [Entrepreneurship Templates](https://www.consuunt.com/entrepreneurship-templates/)
-   [Strategy](https://www.consuunt.com/strategy/)
    -   [Basics of Strategy](#)
        -   [Strategy vs Tactics](https://www.consuunt.com/strategy-vs-tactics/)
        -   [Mission and Vision](https://www.consuunt.com/mission-and-vision/)
        -   [Business Values](https://www.consuunt.com/business-values/)
        -   [Value Chain](https://www.consuunt.com/value-chain/)
        -   [Scenario Planning](https://www.consuunt.com/scenario-planning/)
    -   [Product Oriented](#)
        -   [Porter 6 Forces](https://www.consuunt.com/porter-6-forces/)
        -   [Bowman’s Strategy Clock](https://www.consuunt.com/bowmans-strategy-clock/)
        -   [BCG Matrix](https://www.consuunt.com/bcg-matrix/)
        -   [GE-McKinsey Matrix](https://www.consuunt.com/ge-mckinsey-matrix/)
    -   [Customer Oriented](#)
        -   [Delta Model](https://www.consuunt.com/delta-model/)
    -   [Market Oriented](#)
        -   [PEST Analysis](https://www.consuunt.com/pest-analysis/)
        -   [PESTEL Analysis](https://www.consuunt.com/pestel-analysis/)
        -   [SWOT Analysis](https://www.consuunt.com/swot-analysis/)
    -   [Competition Oriented](#)
        -   [VRIO Framework](https://www.consuunt.com/vrio-framework/)
        -   [Strategy Canvas](https://www.consuunt.com/strategy-canvas/)
        -   [Competitive Advantages](https://www.consuunt.com/competitive-advantages/)
        -   [Porter’s Four Corners](https://www.consuunt.com/porters-four-corners/)
    -   [Efficiency Oriented](#)
        -   [5 Ps of Strategy](https://www.consuunt.com/5-ps-of-strategy/)
        -   [Porter’s Generic Strategies](https://www.consuunt.com/porters-generic-strategies/)
        -   [Porter’s Diamond Model](https://www.consuunt.com/porters-diamond-model/)
        -   [Wardley Map](https://www.consuunt.com/wardley-map/)
        -   [Core Competencies](https://www.consuunt.com/core-competencies/)
        -   [Resource Based View](https://www.consuunt.com/resource-based-view/)
    -   [Growth Oriented](#)
        -   [Bridges Transition Model](https://www.consuunt.com/bridges-transition-model/)
        -   [CAGE Distance Framework](https://www.consuunt.com/cage-distance-framework/)
        -   [McKinsey’s 3 Horizons](https://www.consuunt.com/mckinseys-3-horizons/)
        -   [Vertical Integration](https://www.consuunt.com/vertical-integration/)
        -   [Horizontal Integration](https://www.consuunt.com/horizontal-integration/)
        -   [Blue Ocean Strategy](https://www.consuunt.com/blue-ocean-strategy/)
        -   [Red Ocean Strategy](https://www.consuunt.com/red-ocean-strategy/)
    -   [Holistic](#)
        -   [Porter 5 Forces](https://www.consuunt.com/porter-5-forces/)
        -   [Ansoff Matrix](https://www.consuunt.com/ansoff-matrix/)
        -   [McKinsey 7S Framework](https://www.consuunt.com/mckinsey-7s-framework/)
        -   [CATWOE Analysis](https://www.consuunt.com/catwoe-analysis/)
        -   [Strategy Pyramid](https://www.consuunt.com/strategy-pyramid/)
    -   [Implementation](#)
        -   [Bain’s RAPID Framework](https://www.consuunt.com/bains-rapid-framework/)
        -   [Balanced Scorecard](https://www.consuunt.com/balanced-scorecard/)
        -   [Resources and Capabilities](https://www.consuunt.com/resources-and-capabilities/)
    -   [Examples of Success](#)
        -   [Strategy of Apple](https://www.consuunt.com/strategy-of-apple/)
        -   [Strategy of Amazon](https://www.consuunt.com/strategy-of-amazon/)
        -   [Strategy of Starbucks](https://www.consuunt.com/strategy-of-starbucks/)
    -   [Strategy Templates](https://www.consuunt.com/strategy-templates/)
-   [Personal Skills](https://www.consuunt.com/interpersonal-skills/)
    -   [Communication](#)
        -   [Communicate Effectively](https://www.consuunt.com/communicate-effectively/)
        -   [COIN Conversation Model](https://www.consuunt.com/coin-conversation-model/)
        -   [SCARF Model](https://www.consuunt.com/scarf-model/)
        -   [SBI Feedback Model](https://www.consuunt.com/sbi-feedback-model/)
        -   [CEDAR Feedback Model](https://www.consuunt.com/cedar-feedback-model/)
        -   [How to behave at a meeting](https://www.consuunt.com/how-to-behave-at-a-meeting/)
    -   [Learning](#)
        -   [Gibbs’ Reflective Cycle](https://www.consuunt.com/gibbs-reflective-cycle/)
        -   [Bloom’s Taxonomy](https://www.consuunt.com/blooms-taxonomy/)
        -   [5E Learning Model](https://www.consuunt.com/5e-learning-model/)
    -   [People Classification](#)
        -   [DiSC Model](https://www.consuunt.com/disc-model/)
        -   [9-Box Performance Grid](https://www.consuunt.com/9-box-performance-grid/)
    -   [Social Phenomena](#)
        -   [SEEDS Bias Model](https://www.consuunt.com/seeds-bias-model/)
        -   [Halo Effect](https://www.consuunt.com/halo-effect/)
        -   [Pygmalion Rosenthal Effect](https://www.consuunt.com/pygmalion-rosenthal-effect/)
        -   [Dunning-Kruger Effect](https://www.consuunt.com/dunning-kruger-effect/)
    -   [Motivation](#)
        -   [How to be an Entrepreneur](https://www.consuunt.com/how-to-be-an-entrepreneur/)
        -   [GROW Model](https://www.consuunt.com/grow-model/)
        -   [ERG Theory](https://www.consuunt.com/erg-theory/)
    -   [Team Management](#)
        -   [How to be a Leader](https://www.consuunt.com/how-to-be-a-leader/)
        -   [Mintzberg Managerial Roles](https://www.consuunt.com/mintzberg-managerial-roles/)
        -   [Cog’s Ladder](https://www.consuunt.com/cogs-ladder/)
        -   [The Peter Principle](https://www.consuunt.com/the-peter-principle/)
        -   [How to Negotiate](https://www.consuunt.com/how-to-negotiate/)
        -   [Delegate](https://www.consuunt.com/delegate/)
        -   [Teamwork Skills and Profiles](https://www.consuunt.com/teamwork-skills-and-profiles/)
-   [Planning](https://www.consuunt.com/operational-planning/)
    -   [Task Organization](#)
        -   [Gantt Chart](https://www.consuunt.com/gantt-chart/)
        -   [Kanban](https://www.consuunt.com/kanban/)
        -   [RACI Matrix](https://www.consuunt.com/raci-matrix/)
    -   [Task Prioritization](#)
        -   [Eisenhower Matrix](https://www.consuunt.com/eisenhower-matrix/)
        -   [PERT Chart](https://www.consuunt.com/pert-chart/)
        -   [RAID Log](https://www.consuunt.com/raid-log/)
        -   [MoSCoW Method](https://www.consuunt.com/moscow-method/)
        -   [FMEA Process](https://www.consuunt.com/fmea-process/)
    -   [Problem Solving](#)
        -   [Problem Solving](https://www.consuunt.com/problem-solving/)
        -   [Ishikawa Fishbone diagram](https://www.consuunt.com/ishikawa-fishbone-diagram/)
        -   [CTQ Tree](https://www.consuunt.com/ctq-tree/)
        -   [5 Whys Method](https://www.consuunt.com/5-whys-method/)
        -   [PDCA Model](https://www.consuunt.com/pdca-model/)
        -   [8 Disciplines Method](https://www.consuunt.com/8-disciplines-method/)
        -   [ADDIE Model](https://www.consuunt.com/addie-model/)
    -   [Decision Making](#)
        -   [CODM Model](https://www.consuunt.com/codm-model/)
        -   [ORAPAPA Method](https://www.consuunt.com/orapapa-method/)
        -   [Cynefin Framework](https://www.consuunt.com/cynefin-framework/)
    -   [Optimization of Operations](#)
        -   [KPI](https://www.consuunt.com/kpi/)
        -   [Just In Time](https://www.consuunt.com/just-in-time/)
        -   [SMART Goals](https://www.consuunt.com/smart-goals/)
        -   [KISS Principle](https://www.consuunt.com/kiss-principle/)
        -   [Birkinshaw’s 4 Dimensions](https://www.consuunt.com/birkinshaws-four-dimensions/)
        -   [Parkinson’s Law](https://www.consuunt.com/parkinsons-law/)
        -   [OGSM Framework](https://www.consuunt.com/ogsm-framework/)
        -   [OKR Methodology](https://www.consuunt.com/okr-methodology/)
        -   [APQP Framework](https://www.consuunt.com/apqp-framework/)
        -   [Theory of Constraints](https://www.consuunt.com/theory-of-constraints/)
        -   [Success through Organization](https://www.consuunt.com/success-through-organization/)
    -   [Change Management](#)
        -   [ADKAR Model](https://www.consuunt.com/adkar-model/)
        -   [Lewin’s Change Model](https://www.consuunt.com/lewins-change-model/)
        -   [Kotter’s 8-Step Model](https://www.consuunt.com/kotters-8-step-model/)
        -   [The Greiner Curve](https://www.consuunt.com/the-greiner-curve/)
        -   [GAP Analysis](https://www.consuunt.com/gap-analysis/)
    -   [Planning Templates](https://www.consuunt.com/planning-templates/)
-   [Data Analysis](https://www.consuunt.com/data-analysis/)
    -   [Basics](#)
        -   [Mean, Median and Mode](https://www.consuunt.com/mean-median-and-mode/)
        -   [Define your Data](https://www.consuunt.com/define-your-data/)
        -   [Pareto Principle 80/20 Rule](https://www.consuunt.com/pareto-principle-80-20-rule/)
    -   [Decision Analysis](#)
        -   [Decision Matrix](https://www.consuunt.com/decision-matrix/)
        -   [Decision Tree](https://www.consuunt.com/decision-tree/)
        -   [TARA Framework](https://www.consuunt.com/tara-framework/)
    -   [Problem Analysis](#)
        -   [Root Cause Analysis](https://www.consuunt.com/root-cause-analysis/)
        -   [OODA Loop](https://www.consuunt.com/ooda-loop/)
        -   [DMAIC](https://www.consuunt.com/dmaic/)
        -   [Simplex Process](https://www.consuunt.com/simplex-process/)
    -   [Forecasting](#)
        -   [Forecasting Methods](https://www.consuunt.com/forecasting-methods/)
        -   [Product Life Cycle](https://www.consuunt.com/product-life-cycle/)
        -   [How to use Google Trends](https://www.consuunt.com/how-to-use-google-trends/)
        -   [Correlation vs Causation](https://www.consuunt.com/correlation-vs-causation/)

-   [Business Plan](https://www.consuunt.com/business-plan/)
    -   [Basic Concepts](#)
        -   [Economies of Scale](https://www.consuunt.com/economies-of-scale/)
        -   [Business Plan for Beginners](https://www.consuunt.com/business-plan-for-entrepreneurs/)
        -   [Business Plan Basics](https://www.consuunt.com/business-plan-basics/)
        -   [Costs](https://www.consuunt.com/costs/)
        -   [How to write a Business Plan](https://www.consuunt.com/how-writing-a-business-plan/)
    -   [Advanced Concepts](#)
        -   [Cash Flow Calculation](https://www.consuunt.com/cash-flow-calculation/)
    -   [Fundraising](#)
        -   [Raising Funds for a Business](https://www.consuunt.com/raising-funds-for-a-business/)
        -   [4 C’s of Credit](https://www.consuunt.com/4-cs-of-credit/)
    -   [Business Plan Templates](https://www.consuunt.com/business-plan-templates/)
-   [Marketing](https://www.consuunt.com/marketing/)
    -   [Customer Oriented](#)
        -   [Customer Insight](https://www.consuunt.com/customer-insight/)
        -   [Customer Experience](https://www.consuunt.com/customer-experience/)
        -   [Customer Pain Points](https://www.consuunt.com/customer-pain-points/)
        -   [4C Marketing Model](https://www.consuunt.com/4c-marketing-model/)
        -   [AIO Model](https://www.consuunt.com/aio-model/)
        -   [RFM Model](https://www.consuunt.com/rfm-model/)
        -   [RATER Model](https://www.consuunt.com/rater-model/)
    -   [Product Oriented](#)
        -   [Augmented Product](https://www.consuunt.com/augmented-product/)
        -   [Product Mix](https://www.consuunt.com/product-mix/)
        -   [Unique Selling Proposition](https://www.consuunt.com/unique-selling-proposition/)
        -   [DAGMAR Model](https://www.consuunt.com/dagmar-model/)
    -   [Brand Oriented](#)
        -   [Branding](https://www.consuunt.com/branding/)
        -   [Marketing Storytelling](https://www.consuunt.com/marketing-storytelling/)
        -   [Content Marketing](https://www.consuunt.com/content-marketing/)
    -   [Market Research](#)
        -   [Psychographics](https://www.consuunt.com/psychographics/)
        -   [Barnum Effect](https://www.consuunt.com/barnum-effect/)
        -   [Market Segmentation](https://www.consuunt.com/market-segmentation/)
        -   [Market Research & Big Data](https://www.consuunt.com/market-research-and-big-data/)
        -   [Marketing to Generation Z](https://www.consuunt.com/marketing-to-generation-z/)
    -   [Implementation](#)
        -   [AIDA Model](https://www.consuunt.com/aida-model/)
        -   [4P Marketing Mix](https://www.consuunt.com/4p-marketing-mix/)
        -   [7P Marketing Mix](https://www.consuunt.com/7p-marketing-mix/)
        -   [Sales Funnel](https://www.consuunt.com/sales-funnel/)
        -   [Loyalty Ladder](https://www.consuunt.com/loyalty-ladder/)
        -   [RACE Planning](https://www.consuunt.com/race-planning/)
        -   [Push and Pull Marketing](https://www.consuunt.com/push-and-pull-marketing/)
        -   [Marketing Strategy](https://www.consuunt.com/marketing-strategy/)
    -   [Marketing Templates](https://www.consuunt.com/marketing-templates/)
-   [Entrepreneurship](https://www.consuunt.com/entrepreneurship/)
    -   [Starting your Business](#)
        -   [Starting your own business](https://www.consuunt.com/starting-your-own-business/)
        -   [From Startup to a Business](https://www.consuunt.com/from-startup-to-a-business/)
        -   [Entrepreneur FAQs](https://www.consuunt.com/entrepreneur-faqs/)
        -   [Start your Business Idea](https://www.consuunt.com/how-to-start-your-business-idea/)
        -   [Entrepreneur Golden Rules](https://www.consuunt.com/entrepreneurship-golden-rules/)
    -   [Creative Methods](#)
        -   [Innovate or Imitate?](https://www.consuunt.com/innovate-or-imitate/)
        -   [Design Thinking](https://www.consuunt.com/design-thinking/)
        -   [C-K Theory](https://www.consuunt.com/c-k-theory/)
        -   [SCAMPER Model](https://www.consuunt.com/scamper-model/)
        -   [Hook Model](https://www.consuunt.com/hook-model/)
        -   [AAR Process](https://www.consuunt.com/aar-process/)
        -   [Work From Home](https://www.consuunt.com/work-from-home/)
    -   [Growing the Business](#)
        -   [Growth strategies for Startups](https://www.consuunt.com/growth-strategies-for-startups/)
        -   [VMOST Analysis](https://www.consuunt.com/vmost-analysis/)
        -   [3P Framework](https://www.consuunt.com/3p-framework/)
        -   [SOAR Analysis](https://www.consuunt.com/soar-analysis/)
        -   [TELOS Analysis](https://www.consuunt.com/telos-analysis/)
    -   [Raising Money](#)
        -   [5 C’s of Entrepreneurship](https://www.consuunt.com/5-cs-of-entrepreneurship/)
        -   [Crowdfunding](https://www.consuunt.com/crowdfunding/)
        -   [BATNA & ZOPA Negotiation](https://www.consuunt.com/batna-and-zopa-negotiation/)
        -   [Entrepreneur with no Money](https://www.consuunt.com/entrepreneur-with-no-money/)
    -   [Entrepreneurship Templates](https://www.consuunt.com/entrepreneurship-templates/)
-   [Strategy](https://www.consuunt.com/strategy/)
    -   [Basics of Strategy](#)
        -   [Strategy vs Tactics](https://www.consuunt.com/strategy-vs-tactics/)
        -   [Mission and Vision](https://www.consuunt.com/mission-and-vision/)
        -   [Business Values](https://www.consuunt.com/business-values/)
        -   [Value Chain](https://www.consuunt.com/value-chain/)
        -   [Scenario Planning](https://www.consuunt.com/scenario-planning/)
    -   [Product Oriented](#)
        -   [Porter 6 Forces](https://www.consuunt.com/porter-6-forces/)
        -   [Bowman’s Strategy Clock](https://www.consuunt.com/bowmans-strategy-clock/)
        -   [BCG Matrix](https://www.consuunt.com/bcg-matrix/)
        -   [GE-McKinsey Matrix](https://www.consuunt.com/ge-mckinsey-matrix/)
    -   [Customer Oriented](#)
        -   [Delta Model](https://www.consuunt.com/delta-model/)
    -   [Market Oriented](#)
        -   [PEST Analysis](https://www.consuunt.com/pest-analysis/)
        -   [PESTEL Analysis](https://www.consuunt.com/pestel-analysis/)
        -   [SWOT Analysis](https://www.consuunt.com/swot-analysis/)
    -   [Competition Oriented](#)
        -   [VRIO Framework](https://www.consuunt.com/vrio-framework/)
        -   [Strategy Canvas](https://www.consuunt.com/strategy-canvas/)
        -   [Competitive Advantages](https://www.consuunt.com/competitive-advantages/)
        -   [Porter’s Four Corners](https://www.consuunt.com/porters-four-corners/)
    -   [Efficiency Oriented](#)
        -   [5 Ps of Strategy](https://www.consuunt.com/5-ps-of-strategy/)
        -   [Porter’s Generic Strategies](https://www.consuunt.com/porters-generic-strategies/)
        -   [Porter’s Diamond Model](https://www.consuunt.com/porters-diamond-model/)
        -   [Wardley Map](https://www.consuunt.com/wardley-map/)
        -   [Core Competencies](https://www.consuunt.com/core-competencies/)
        -   [Resource Based View](https://www.consuunt.com/resource-based-view/)
    -   [Growth Oriented](#)
        -   [Bridges Transition Model](https://www.consuunt.com/bridges-transition-model/)
        -   [CAGE Distance Framework](https://www.consuunt.com/cage-distance-framework/)
        -   [McKinsey’s 3 Horizons](https://www.consuunt.com/mckinseys-3-horizons/)
        -   [Vertical Integration](https://www.consuunt.com/vertical-integration/)
        -   [Horizontal Integration](https://www.consuunt.com/horizontal-integration/)
        -   [Blue Ocean Strategy](https://www.consuunt.com/blue-ocean-strategy/)
        -   [Red Ocean Strategy](https://www.consuunt.com/red-ocean-strategy/)
    -   [Holistic](#)
        -   [Porter 5 Forces](https://www.consuunt.com/porter-5-forces/)
        -   [Ansoff Matrix](https://www.consuunt.com/ansoff-matrix/)
        -   [McKinsey 7S Framework](https://www.consuunt.com/mckinsey-7s-framework/)
        -   [CATWOE Analysis](https://www.consuunt.com/catwoe-analysis/)
        -   [Strategy Pyramid](https://www.consuunt.com/strategy-pyramid/)
    -   [Implementation](#)
        -   [Bain’s RAPID Framework](https://www.consuunt.com/bains-rapid-framework/)
        -   [Balanced Scorecard](https://www.consuunt.com/balanced-scorecard/)
        -   [Resources and Capabilities](https://www.consuunt.com/resources-and-capabilities/)
    -   [Examples of Success](#)
        -   [Strategy of Apple](https://www.consuunt.com/strategy-of-apple/)
        -   [Strategy of Amazon](https://www.consuunt.com/strategy-of-amazon/)
        -   [Strategy of Starbucks](https://www.consuunt.com/strategy-of-starbucks/)
    -   [Strategy Templates](https://www.consuunt.com/strategy-templates/)
-   [Personal Skills](https://www.consuunt.com/interpersonal-skills/)
    -   [Communication](#)
        -   [Communicate Effectively](https://www.consuunt.com/communicate-effectively/)
        -   [COIN Conversation Model](https://www.consuunt.com/coin-conversation-model/)
        -   [SCARF Model](https://www.consuunt.com/scarf-model/)
        -   [SBI Feedback Model](https://www.consuunt.com/sbi-feedback-model/)
        -   [CEDAR Feedback Model](https://www.consuunt.com/cedar-feedback-model/)
        -   [How to behave at a meeting](https://www.consuunt.com/how-to-behave-at-a-meeting/)
    -   [Learning](#)
        -   [Gibbs’ Reflective Cycle](https://www.consuunt.com/gibbs-reflective-cycle/)
        -   [Bloom’s Taxonomy](https://www.consuunt.com/blooms-taxonomy/)
        -   [5E Learning Model](https://www.consuunt.com/5e-learning-model/)
    -   [People Classification](#)
        -   [DiSC Model](https://www.consuunt.com/disc-model/)
        -   [9-Box Performance Grid](https://www.consuunt.com/9-box-performance-grid/)
    -   [Social Phenomena](#)
        -   [SEEDS Bias Model](https://www.consuunt.com/seeds-bias-model/)
        -   [Halo Effect](https://www.consuunt.com/halo-effect/)
        -   [Pygmalion Rosenthal Effect](https://www.consuunt.com/pygmalion-rosenthal-effect/)
        -   [Dunning-Kruger Effect](https://www.consuunt.com/dunning-kruger-effect/)
    -   [Motivation](#)
        -   [How to be an Entrepreneur](https://www.consuunt.com/how-to-be-an-entrepreneur/)
        -   [GROW Model](https://www.consuunt.com/grow-model/)
        -   [ERG Theory](https://www.consuunt.com/erg-theory/)
    -   [Team Management](#)
        -   [How to be a Leader](https://www.consuunt.com/how-to-be-a-leader/)
        -   [Mintzberg Managerial Roles](https://www.consuunt.com/mintzberg-managerial-roles/)
        -   [Cog’s Ladder](https://www.consuunt.com/cogs-ladder/)
        -   [The Peter Principle](https://www.consuunt.com/the-peter-principle/)
        -   [How to Negotiate](https://www.consuunt.com/how-to-negotiate/)
        -   [Delegate](https://www.consuunt.com/delegate/)
        -   [Teamwork Skills and Profiles](https://www.consuunt.com/teamwork-skills-and-profiles/)
-   [Planning](https://www.consuunt.com/operational-planning/)
    -   [Task Organization](#)
        -   [Gantt Chart](https://www.consuunt.com/gantt-chart/)
        -   [Kanban](https://www.consuunt.com/kanban/)
        -   [RACI Matrix](https://www.consuunt.com/raci-matrix/)
    -   [Task Prioritization](#)
        -   [Eisenhower Matrix](https://www.consuunt.com/eisenhower-matrix/)
        -   [PERT Chart](https://www.consuunt.com/pert-chart/)
        -   [RAID Log](https://www.consuunt.com/raid-log/)
        -   [MoSCoW Method](https://www.consuunt.com/moscow-method/)
        -   [FMEA Process](https://www.consuunt.com/fmea-process/)
    -   [Problem Solving](#)
        -   [Problem Solving](https://www.consuunt.com/problem-solving/)
        -   [Ishikawa Fishbone diagram](https://www.consuunt.com/ishikawa-fishbone-diagram/)
        -   [CTQ Tree](https://www.consuunt.com/ctq-tree/)
        -   [5 Whys Method](https://www.consuunt.com/5-whys-method/)
        -   [PDCA Model](https://www.consuunt.com/pdca-model/)
        -   [8 Disciplines Method](https://www.consuunt.com/8-disciplines-method/)
        -   [ADDIE Model](https://www.consuunt.com/addie-model/)
    -   [Decision Making](#)
        -   [CODM Model](https://www.consuunt.com/codm-model/)
        -   [ORAPAPA Method](https://www.consuunt.com/orapapa-method/)
        -   [Cynefin Framework](https://www.consuunt.com/cynefin-framework/)
    -   [Optimization of Operations](#)
        -   [KPI](https://www.consuunt.com/kpi/)
        -   [Just In Time](https://www.consuunt.com/just-in-time/)
        -   [SMART Goals](https://www.consuunt.com/smart-goals/)
        -   [KISS Principle](https://www.consuunt.com/kiss-principle/)
        -   [Birkinshaw’s 4 Dimensions](https://www.consuunt.com/birkinshaws-four-dimensions/)
        -   [Parkinson’s Law](https://www.consuunt.com/parkinsons-law/)
        -   [OGSM Framework](https://www.consuunt.com/ogsm-framework/)
        -   [OKR Methodology](https://www.consuunt.com/okr-methodology/)
        -   [APQP Framework](https://www.consuunt.com/apqp-framework/)
        -   [Theory of Constraints](https://www.consuunt.com/theory-of-constraints/)
        -   [Success through Organization](https://www.consuunt.com/success-through-organization/)
    -   [Change Management](#)
        -   [ADKAR Model](https://www.consuunt.com/adkar-model/)
        -   [Lewin’s Change Model](https://www.consuunt.com/lewins-change-model/)
        -   [Kotter’s 8-Step Model](https://www.consuunt.com/kotters-8-step-model/)
        -   [The Greiner Curve](https://www.consuunt.com/the-greiner-curve/)
        -   [GAP Analysis](https://www.consuunt.com/gap-analysis/)
    -   [Planning Templates](https://www.consuunt.com/planning-templates/)
-   [Data Analysis](https://www.consuunt.com/data-analysis/)
    -   [Basics](#)
        -   [Mean, Median and Mode](https://www.consuunt.com/mean-median-and-mode/)
        -   [Define your Data](https://www.consuunt.com/define-your-data/)
        -   [Pareto Principle 80/20 Rule](https://www.consuunt.com/pareto-principle-80-20-rule/)
    -   [Decision Analysis](#)
        -   [Decision Matrix](https://www.consuunt.com/decision-matrix/)
        -   [Decision Tree](https://www.consuunt.com/decision-tree/)
        -   [TARA Framework](https://www.consuunt.com/tara-framework/)
    -   [Problem Analysis](#)
        -   [Root Cause Analysis](https://www.consuunt.com/root-cause-analysis/)
        -   [OODA Loop](https://www.consuunt.com/ooda-loop/)
        -   [DMAIC](https://www.consuunt.com/dmaic/)
        -   [Simplex Process](https://www.consuunt.com/simplex-process/)
    -   [Forecasting](#)
        -   [Forecasting Methods](https://www.consuunt.com/forecasting-methods/)
        -   [Product Life Cycle](https://www.consuunt.com/product-life-cycle/)
        -   [How to use Google Trends](https://www.consuunt.com/how-to-use-google-trends/)
        -   [Correlation vs Causation](https://www.consuunt.com/correlation-vs-causation/)

**© 2026 - *Consuunt*.**

[](#)

#### CONTACT US

We're not around right now. But you can send us an email and we'll get back to you, asap.

Send

Sending

[](#)

-   [Business Plan](https://www.consuunt.com/business-plan/ "Business Plan")
    -   [Basic Concepts](# "Basic Concepts")
        -   [Economies of Scale](https://www.consuunt.com/economies-of-scale/ "Economies of Scale")
        -   [Business Plan for Beginners](https://www.consuunt.com/business-plan-for-entrepreneurs/ "Business Plan for Beginners")
        -   [Business Plan Basics](https://www.consuunt.com/business-plan-basics/ "Business Plan Basics")
        -   [Costs](https://www.consuunt.com/costs/ "Costs")
        -   [How to write a Business Plan](https://www.consuunt.com/how-writing-a-business-plan/ "How to write a Business Plan")
    -   [Advanced Concepts](# "Advanced Concepts")
        -   [Cash Flow Calculation](https://www.consuunt.com/cash-flow-calculation/ "Cash Flow Calculation")
    -   [Fundraising](# "Fundraising")
        -   [Raising Funds for a Business](https://www.consuunt.com/raising-funds-for-a-business/ "Raising Funds for a Business")
        -   [4 C’s of Credit](https://www.consuunt.com/4-cs-of-credit/ "4 C’s of Credit")
    -   [Business Plan Templates](https://www.consuunt.com/business-plan-templates/ "Business Plan Templates")
-   [Marketing](https://www.consuunt.com/marketing/ "Marketing")
    -   [Customer Oriented](# "Customer Oriented")
        -   [Customer Insight](https://www.consuunt.com/customer-insight/ "Customer Insight")
        -   [Customer Experience](https://www.consuunt.com/customer-experience/ "Customer Experience")
        -   [Customer Pain Points](https://www.consuunt.com/customer-pain-points/ "Customer Pain Points")
        -   [4C Marketing Model](https://www.consuunt.com/4c-marketing-model/ "4C Marketing Model")
        -   [AIO Model](https://www.consuunt.com/aio-model/ "AIO Model")
        -   [RFM Model](https://www.consuunt.com/rfm-model/ "RFM Model")
        -   [RATER Model](https://www.consuunt.com/rater-model/ "RATER Model")
    -   [Product Oriented](# "Product Oriented")
        -   [Augmented Product](https://www.consuunt.com/augmented-product/ "Augmented Product")
        -   [Product Mix](https://www.consuunt.com/product-mix/ "Product Mix")
        -   [Unique Selling Proposition](https://www.consuunt.com/unique-selling-proposition/ "Unique Selling Proposition")
        -   [DAGMAR Model](https://www.consuunt.com/dagmar-model/ "DAGMAR Model")
    -   [Brand Oriented](# "Brand Oriented")
        -   [Branding](https://www.consuunt.com/branding/ "Branding")
        -   [Marketing Storytelling](https://www.consuunt.com/marketing-storytelling/ "Marketing Storytelling")
        -   [Content Marketing](https://www.consuunt.com/content-marketing/ "Content Marketing")
    -   [Market Research](# "Market Research")
        -   [Psychographics](https://www.consuunt.com/psychographics/ "Psychographics")
        -   [Barnum Effect](https://www.consuunt.com/barnum-effect/ "Barnum Effect")
        -   [Market Segmentation](https://www.consuunt.com/market-segmentation/ "Market Segmentation")
        -   [Market Research & Big Data](https://www.consuunt.com/market-research-and-big-data/ "Market Research & Big Data")
        -   [Marketing to Generation Z](https://www.consuunt.com/marketing-to-generation-z/ "Marketing to Generation Z")
    -   [Implementation](# "Implementation")
        -   [AIDA Model](https://www.consuunt.com/aida-model/ "AIDA Model")
        -   [4P Marketing Mix](https://www.consuunt.com/4p-marketing-mix/ "4P Marketing Mix")
        -   [7P Marketing Mix](https://www.consuunt.com/7p-marketing-mix/ "7P Marketing Mix")
        -   [Sales Funnel](https://www.consuunt.com/sales-funnel/ "Sales Funnel")
        -   [Loyalty Ladder](https://www.consuunt.com/loyalty-ladder/ "Loyalty Ladder")
        -   [RACE Planning](https://www.consuunt.com/race-planning/ "RACE Planning")
        -   [Push and Pull Marketing](https://www.consuunt.com/push-and-pull-marketing/ "Push and Pull Marketing")
        -   [Marketing Strategy](https://www.consuunt.com/marketing-strategy/ "Marketing Strategy")
    -   [Marketing Templates](https://www.consuunt.com/marketing-templates/ "Marketing Templates")
-   [Entrepreneurship](https://www.consuunt.com/entrepreneurship/ "Entrepreneurship")
    -   [Starting your Business](# "Starting your Business")
        -   [Starting your own business](https://www.consuunt.com/starting-your-own-business/ "Starting your own business")
        -   [From Startup to a Business](https://www.consuunt.com/from-startup-to-a-business/ "From Startup to a Business")
        -   [Entrepreneur FAQs](https://www.consuunt.com/entrepreneur-faqs/ "Entrepreneur FAQs")
        -   [Start your Business Idea](https://www.consuunt.com/how-to-start-your-business-idea/ "Start your Business Idea")
        -   [Entrepreneur Golden Rules](https://www.consuunt.com/entrepreneurship-golden-rules/ "Entrepreneur Golden Rules")
    -   [Creative Methods](# "Creative Methods")
        -   [Innovate or Imitate?](https://www.consuunt.com/innovate-or-imitate/ "Innovate or Imitate?")
        -   [Design Thinking](https://www.consuunt.com/design-thinking/ "Design Thinking")
        -   [C-K Theory](https://www.consuunt.com/c-k-theory/ "C-K Theory")
        -   [SCAMPER Model](https://www.consuunt.com/scamper-model/ "SCAMPER Model")
        -   [Hook Model](https://www.consuunt.com/hook-model/ "Hook Model")
        -   [AAR Process](https://www.consuunt.com/aar-process/ "AAR Process")
        -   [Work From Home](https://www.consuunt.com/work-from-home/ "Work From Home")
    -   [Growing the Business](# "Growing the Business")
        -   [Growth strategies for Startups](https://www.consuunt.com/growth-strategies-for-startups/ "Growth strategies for Startups")
        -   [VMOST Analysis](https://www.consuunt.com/vmost-analysis/ "VMOST Analysis")
        -   [3P Framework](https://www.consuunt.com/3p-framework/ "3P Framework")
        -   [SOAR Analysis](https://www.consuunt.com/soar-analysis/ "SOAR Analysis")
        -   [TELOS Analysis](https://www.consuunt.com/telos-analysis/ "TELOS Analysis")
    -   [Raising Money](# "Raising Money")
        -   [5 C’s of Entrepreneurship](https://www.consuunt.com/5-cs-of-entrepreneurship/ "5 C’s of Entrepreneurship")
        -   [Crowdfunding](https://www.consuunt.com/crowdfunding/ "Crowdfunding")
        -   [BATNA & ZOPA Negotiation](https://www.consuunt.com/batna-and-zopa-negotiation/ "BATNA & ZOPA Negotiation")
        -   [Entrepreneur with no Money](https://www.consuunt.com/entrepreneur-with-no-money/ "Entrepreneur with no Money")
    -   [Entrepreneurship Templates](https://www.consuunt.com/entrepreneurship-templates/ "Entrepreneurship Templates")
-   [Strategy](https://www.consuunt.com/strategy/ "Strategy")
    -   [Basics of Strategy](# "Basics of Strategy")
        -   [Strategy vs Tactics](https://www.consuunt.com/strategy-vs-tactics/ "Strategy vs Tactics")
        -   [Mission and Vision](https://www.consuunt.com/mission-and-vision/ "Mission and Vision")
        -   [Business Values](https://www.consuunt.com/business-values/ "Business Values")
        -   [Value Chain](https://www.consuunt.com/value-chain/ "Value Chain")
        -   [Scenario Planning](https://www.consuunt.com/scenario-planning/ "Scenario Planning")
    -   [Product Oriented](# "Product Oriented")
        -   [Porter 6 Forces](https://www.consuunt.com/porter-6-forces/ "Porter 6 Forces")
        -   [Bowman’s Strategy Clock](https://www.consuunt.com/bowmans-strategy-clock/ "Bowman’s Strategy Clock")
        -   [BCG Matrix](https://www.consuunt.com/bcg-matrix/ "BCG Matrix")
        -   [GE-McKinsey Matrix](https://www.consuunt.com/ge-mckinsey-matrix/ "GE-McKinsey Matrix")
    -   [Customer Oriented](# "Customer Oriented")
        -   [Delta Model](https://www.consuunt.com/delta-model/ "Delta Model")
    -   [Market Oriented](# "Market Oriented")
        -   [PEST Analysis](https://www.consuunt.com/pest-analysis/ "PEST Analysis")
        -   [PESTEL Analysis](https://www.consuunt.com/pestel-analysis/ "PESTEL Analysis")
        -   [SWOT Analysis](https://www.consuunt.com/swot-analysis/ "SWOT Analysis")
    -   [Competition Oriented](# "Competition Oriented")
        -   [VRIO Framework](https://www.consuunt.com/vrio-framework/ "VRIO Framework")
        -   [Strategy Canvas](https://www.consuunt.com/strategy-canvas/ "Strategy Canvas")
        -   [Competitive Advantages](https://www.consuunt.com/competitive-advantages/ "Competitive Advantages")
        -   [Porter’s Four Corners](https://www.consuunt.com/porters-four-corners/ "Porter’s Four Corners")
    -   [Efficiency Oriented](# "Efficiency Oriented")
        -   [5 Ps of Strategy](https://www.consuunt.com/5-ps-of-strategy/ "5 Ps of Strategy")
        -   [Porter’s Generic Strategies](https://www.consuunt.com/porters-generic-strategies/ "Porter’s Generic Strategies")
        -   [Porter’s Diamond Model](https://www.consuunt.com/porters-diamond-model/ "Porter’s Diamond Model")
        -   [Wardley Map](https://www.consuunt.com/wardley-map/ "Wardley Map")
        -   [Core Competencies](https://www.consuunt.com/core-competencies/ "Core Competencies")
        -   [Resource Based View](https://www.consuunt.com/resource-based-view/ "Resource Based View")
    -   [Growth Oriented](# "Growth Oriented")
        -   [Bridges Transition Model](https://www.consuunt.com/bridges-transition-model/ "Bridges Transition Model")
        -   [CAGE Distance Framework](https://www.consuunt.com/cage-distance-framework/ "CAGE Distance Framework")
        -   [McKinsey’s 3 Horizons](https://www.consuunt.com/mckinseys-3-horizons/ "McKinsey’s 3 Horizons")
        -   [Vertical Integration](https://www.consuunt.com/vertical-integration/ "Vertical Integration")
        -   [Horizontal Integration](https://www.consuunt.com/horizontal-integration/ "Horizontal Integration")
        -   [Blue Ocean Strategy](https://www.consuunt.com/blue-ocean-strategy/ "Blue Ocean Strategy")
        -   [Red Ocean Strategy](https://www.consuunt.com/red-ocean-strategy/ "Red Ocean Strategy")
    -   [Holistic](# "Holistic")
        -   [Porter 5 Forces](https://www.consuunt.com/porter-5-forces/ "Porter 5 Forces")
        -   [Ansoff Matrix](https://www.consuunt.com/ansoff-matrix/ "Ansoff Matrix")
        -   [McKinsey 7S Framework](https://www.consuunt.com/mckinsey-7s-framework/ "McKinsey 7S Framework")
        -   [CATWOE Analysis](https://www.consuunt.com/catwoe-analysis/ "CATWOE Analysis")
        -   [Strategy Pyramid](https://www.consuunt.com/strategy-pyramid/ "Strategy Pyramid")
    -   [Implementation](# "Implementation")
        -   [Bain’s RAPID Framework](https://www.consuunt.com/bains-rapid-framework/ "Bain’s RAPID Framework")
        -   [Balanced Scorecard](https://www.consuunt.com/balanced-scorecard/ "Balanced Scorecard")
        -   [Resources and Capabilities](https://www.consuunt.com/resources-and-capabilities/ "Resources and Capabilities")
    -   [Examples of Success](# "Examples of Success")
        -   [Strategy of Apple](https://www.consuunt.com/strategy-of-apple/ "Strategy of Apple")
        -   [Strategy of Amazon](https://www.consuunt.com/strategy-of-amazon/ "Strategy of Amazon")
        -   [Strategy of Starbucks](https://www.consuunt.com/strategy-of-starbucks/ "Strategy of Starbucks")
    -   [Strategy Templates](https://www.consuunt.com/strategy-templates/ "Strategy Templates")
-   [Personal Skills](https://www.consuunt.com/interpersonal-skills/ "Personal Skills")
    -   [Communication](# "Communication")
        -   [Communicate Effectively](https://www.consuunt.com/communicate-effectively/ "Communicate Effectively")
        -   [COIN Conversation Model](https://www.consuunt.com/coin-conversation-model/ "COIN Conversation Model")
        -   [SCARF Model](https://www.consuunt.com/scarf-model/ "SCARF Model")
        -   [SBI Feedback Model](https://www.consuunt.com/sbi-feedback-model/ "SBI Feedback Model")
        -   [CEDAR Feedback Model](https://www.consuunt.com/cedar-feedback-model/ "CEDAR Feedback Model")
        -   [How to behave at a meeting](https://www.consuunt.com/how-to-behave-at-a-meeting/ "How to behave at a meeting")
    -   [Learning](# "Learning")
        -   [Gibbs’ Reflective Cycle](https://www.consuunt.com/gibbs-reflective-cycle/ "Gibbs’ Reflective Cycle")
        -   [Bloom’s Taxonomy](https://www.consuunt.com/blooms-taxonomy/ "Bloom’s Taxonomy")
        -   [5E Learning Model](https://www.consuunt.com/5e-learning-model/ "5E Learning Model")
    -   [People Classification](# "People Classification")
        -   [DiSC Model](https://www.consuunt.com/disc-model/ "DiSC Model")
        -   [9-Box Performance Grid](https://www.consuunt.com/9-box-performance-grid/ "9-Box Performance Grid")
    -   [Social Phenomena](# "Social Phenomena")
        -   [SEEDS Bias Model](https://www.consuunt.com/seeds-bias-model/ "SEEDS Bias Model")
        -   [Halo Effect](https://www.consuunt.com/halo-effect/ "Halo Effect")
        -   [Pygmalion Rosenthal Effect](https://www.consuunt.com/pygmalion-rosenthal-effect/ "Pygmalion Rosenthal Effect")
        -   [Dunning-Kruger Effect](https://www.consuunt.com/dunning-kruger-effect/ "Dunning-Kruger Effect")
    -   [Motivation](# "Motivation")
        -   [How to be an Entrepreneur](https://www.consuunt.com/how-to-be-an-entrepreneur/ "How to be an Entrepreneur")
        -   [GROW Model](https://www.consuunt.com/grow-model/ "GROW Model")
        -   [ERG Theory](https://www.consuunt.com/erg-theory/ "ERG Theory")
    -   [Team Management](# "Team Management")
        -   [How to be a Leader](https://www.consuunt.com/how-to-be-a-leader/ "How to be a Leader")
        -   [Mintzberg Managerial Roles](https://www.consuunt.com/mintzberg-managerial-roles/ "Mintzberg Managerial Roles")
        -   [Cog’s Ladder](https://www.consuunt.com/cogs-ladder/ "Cog’s Ladder")

...6726 bytes truncated...

The tool call succeeded but the output was truncated. Full output saved to: /home/user/.local/share/opencode/tool-output/tool_0332eb66d001vHNM6tJDrCdSQw
Use the Task tool to have explore agent process this file with Grep and Read (with offset/limit). Do NOT read the full file yourself - delegate to save context.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 216.7s)

_Thinking:_

TARA confirmed: **Transfer, Accept, Reduce, Avoid** — four strategies. (Not TARRA which includes "Tolerate/Recover".)

Next, I need to update the following:

1. The body of GitHub issue #15 (TARRA → TARA, Description → Cause/Trigger/Consequence)

2. The feature README:

   - Overview: TARRA → TARA
   - REQ-001: Replace `## Description` with `## Cause`, `## Trigger`, `## Consequence` (each a mandatory H2); "TARRA closed 5-value set" → "TARA closed 4-value set"
   - ACC-002: "TARRA closed set" → "TARA closed set"
   - Design notes:
     - Body shape block: Replace the Description section with Cause/Trigger/Consequence; strategy line → `tolerate...` → `transfer | accept | reduce | avoid`
     - Replace "Strategy (TARRA)" bullet with "Strategy (TARA)" — 4-value set, with a reference to the TARA framework (consuunt) and a brief note on each strategy's meaning
     - Add a new design note: "Assessment structure (initial/residual)" with an explanation + a concrete example (full before/after example with zone table)
     - Update order-enforcement line: title → comment → Cause → Trigger → Consequence → Scope → Initial Assessment → Strategy → Mitigation → Residual Assessment → ...
   - Dependencies: no change
   - "Related ADRs" / "no new ADR" line: "TARRA closed set" → "TARA closed set"
   - Task list: Task 1.2 (TARRA → TARA? Actually task 1.2 doesn't explicitly mention TARRA — check: task 1.2 lists fields as `description`/`scope`/... → needs updating to `cause`/`trigger`/`consequence`), Task 1.4 ("TARRA closed set" → "TARA closed set"), Task 2.6 ("invalid TARRA word" → "invalid TARA word")
   - Current status: no problem ("TARRA strategy" — check: does "TARRA response strategy" appear? In Current Status: "Full schema and MCP surface proposed (see Design Notes and Task List)" — no mention of TARRA. Overview has it. Check each occurrence.)
   - Recent updates: add a new entry at the top (newest), documenting the revision (TARA correction, C/T/C split, assessment example)
   - Decisions Made: update the TARRA bullet (2026-08-24) — actually, better: add a new dated decision bullet for the revision. And either fix the old TARRA bullet to reference the correction, or add a new bullet and leave the old one (Decisions Made is a log — feat-10's log retains old decisions and adds new ones; superseded decisions are noted explicitly). Cleanest is: leave the old bullet and add a new bullet marked as superseding it. Or just edit the old bullet to TARA. Per convention: "if a decision reverses/supersedes a prior ADR" that's for ADRs; for feature logs, feat-10 had a "superseded the original Design Notes wording" bullet. I'll add a new decision bullet: "**2026-08-24**: `## Strategy` is the TARA closed 4-value set `transfer`/`accept`/`reduce`/`avoid` (supersedes the earlier TARRA 5-value proposal) — rationale: user correction with reference to the TARA framework (https://www.consuunt.com/tara-framework/); the valid strategy words are Transfer, Accept, Reduce, Avoid."
     And a bullet: "**2026-08-24**: risk scenario split into three separate H2 sections `## Cause`, `## Trigger`, `## Consequence` (supersedes the single `## Description` proposal) — rationale: user requirement; each aspect of the scenario gets its own validated section instead of one mixed free-text blob."

   Should I delete the old TARRA bullet or keep it with a note? To keep the log clean I'd edit the old TARRA bullet to mark it as superseded... Actually, the simplest and most honest approach: leave the old bullet as-is (as a historical log entry) and add the superseding bullet. feat-10's log shows both the original decisions and the later "superseded the original Design Notes wording" decision. I'll follow that pattern.

   Hmm, but the body-shape and REQ/ACC/Design Notes sections must reflect the current design (those are "current state", not logs). Only Decisions Made / Recent Updates are append-only logs.

3. Also the `Strategy` design-note bullet: "single-line H2 section validated against a closed 5-value set..." → 4-value set.

4. Also fix: in the old design note I wrote "TARRA" in multiple places. Let me grep the README for TARRA/Description.

New body shape:

```
# {H1 title}
<!-- optional leading comment -->            comment: MarkdownComment | None

## Cause                                     cause: MarkdownStr  (mandatory)
{Why the risk exists — root condition}

## Trigger                                   trigger: MarkdownStr  (mandatory)
{What sets the risk event in motion}

## Consequence                                consequence: MarkdownStr  (mandatory)
{What happens if the risk event occurs}

## Scope                                     scope: list[MarkdownStr]  (>=1)
- {Affected system / component}

## Initial Assessment                        initial_assessment: Assessment
- Probability: {1..5}
- Impact: {1..5}

## Strategy                                  strategy: str  (TARA closed 4-value set)
{transfer | accept | reduce | avoid}

## Mitigation                                mitigation: MarkdownStr  (mandatory)
{Treatment actions; "none" if strategy is accept}

## Residual Assessment                       residual_assessment: Assessment
- Probability: {1..5}
- Impact: {1..5}

## Owner                                     owner: MarkdownStr | None
## Tags                                      tags: list[MarkdownStr] | None
## More Information                          more_information: MarkdownStr | None
```

Note: "none" if the strategy is `tolerate` → becomes "none" if the strategy is `accept`.

Assessment structure design note with example:

```
- **Assessment structure (initial/residual)** — Each assessment is a 5x5
  matrix cell: two integer coordinates on the 1..5 scale,
  `probability` (1 = rare ... 5 = almost certain) and `impact`
  (1 = negligible ... 5 = severe), written as two list items under the
  H2 section heading:

```

## Initial Assessment

- Probability: 4
- Impact: 3

```

The model derives the zone `level` from the product of the two
coordinates (probability x impact):

| p \ i | 1    | 2    | 3    | 4    | 5         |
|-------|------|------|------|------|-----------|
| 1     | low  | low  | low  | low  | medium    |
| 2     | low  | low  | medium | medium | high     |
| 3     | low  | medium | medium | high | very high |
| 4     | low  | medium | high | high | very high |
| 5     | medium | high | high | very high | very high |

Zones: 1-4 `low`, 5-9 `medium`, 10-14 `high`, 15-25 `very high`.

**Example** (risk: untrusted file upload parsed by an old parser
library):

```

## Initial Assessment

- Probability: 4
- Impact: 3 -> 4 x 3 = 12 => level `high`

## Strategy

reduce

## Mitigation

Replace the parser with a maintained library and limit uploads to
a format whitelist.

## Residual Assessment

- Probability: 2
- Impact: 3 -> 2 x 3 = 6 => level `medium`

```

The before/after pair shows the mitigation moved the risk one zone
down (`high` -> `medium`) — the register's audit trail. (Comment
annotations like "-> 4 x 3 = 12" are shown here for readability only;
the actual document stores just the two list items and the level is
computed.)
```

Hmm wait, should I include scale anchors for probability (1=rare...5=almost certain)? That's useful. But keep it brief in the plan. I'll include a one-line anchor for each.

Also update REQ-001 wording: "mandatory `## Description`" → "mandatory `## Cause`, `## Trigger`, `## Consequence`", "TARRA closed 5-value set" → "TARA closed 4-value set".

ACC-001: mention both assessments — no issue. ACC-002: "TARRA closed set" → "TARA closed set".

Overview: "TARRA response strategy (`## Strategy`: tolerate / assign / reduce / recover / avoid)" → "TARA response strategy (`## Strategy`: transfer / accept / reduce / avoid)".

Design note "Strategy (TARRA)" → "Strategy (TARA)": closed 4-value set `transfer`/`accept`/`reduce`/`avoid` — TARA framework (Transfer, Accept, Reduce, Avoid; see https://www.consuunt.com/tara-framework/). Mandatory.

Task 1.2 field list: `description`/`scope`/... → `cause`/`trigger`/`consequence`/`scope`/...

Task 1.4: "TARRA closed set" → "TARA closed set".

Task 2.6: "invalid TARRA word" → "invalid TARA word".

"No new ADR is anticipated" paragraph: "TARRA closed set" → "TARA closed set".

Current status: "Full schema and MCP surface proposed (see Design Notes and Task List)" — no issue, no TARRA. Check: "**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder created... Full schema and MCP surface proposed..." OK.

Recent updates: new top entry:

```
#### 2026-08-24T... (newest)
- Completed: plan revised per user feedback — (1) strategy set corrected from
  TARRA (tolerate/assign/reduce/recover/avoid) to TARA (transfer/accept/
  reduce/avoid), the valid TARA words per the TARA framework
  (https://www.consuunt.com/tara-framework/); (2) the single `## Description`
  section replaced by three separate H2 sections `## Cause`, `## Trigger`,
  `## Consequence`; (3) added Design Notes entry explaining the
  initial/residual assessment structure with a worked example (5x5 zone
  table, high -> medium before/after pair)
- Next: user review, then Phase 1 (Specification)
- Notes: GitHub issue #15 body updated to match
```

Issue #15 edit: rewrite the body with TARA and C/T/C.

Also: frontmatter `updated: 2026-08-24` — same day, no change needed.

Also — one more consideration: does `strategy: accept` affect the status vocabulary? Status `accepted` = "residual risk formally accepted" — that stays consistent with TARA's "Accept". Good.

Also "mitigation ('none' if strategy is `tolerate`)" appears in the body-shape block and in the issue. Update to `accept`.

So first get the current time, then do the edits. Do a series of `edit` calls against the README. Since there are many edits, might be easier to rewrite the whole file with `write`. File is ~330 lines; a full rewrite risks losing details, but I have the content I just wrote in full context. Given the number of scattered changes (10+ spots), a full rewrite via `write` is cleaner and less error-prone than 12 edits. I'll rewrite the README with the updated content.

After that, `gh issue edit 15 --body-file` with the updated body.

Let me get the timestamp first.

TARA confirmed: **Transfer, Accept, Reduce, Avoid** (4 words). Updating the plan (full rewrite of the README), the issue body, and the decision log:

**Tool: bash**

**Input:**

```json
{
  "command": "date +%Y-%m-%dT%H:%M:%S%:z"
}
```

**Output:**

```
2026-08-24T11:55:11+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 334.1s)

_Thinking:_

Alright, let's rewrite the README reflecting all the changes. Let me carefully create the updated version.

**Tool: write**

**Input:**

````json
{
  "content": "---\nid: feat-15-add-artifact-type-risk\nversion: 1.0.0\nstatus: planning\ncreated: 2026-08-24\nupdated: 2026-08-24\n---\n\n# Feature: Add artifact type Risk (rsk)\n\n## Plan\n\n### Overview\n\nAdd a new markdown artifact type, `Risk` (abbreviation `rsk`), for maintaining risk\nregisters in system specifications. Every risk decomposes its scenario into\nseparate `## Cause`, `## Trigger`, and `## Consequence` sections, carries a 5x5\nprobability/impact assessment BEFORE mitigation (`## Initial Assessment`) and\nthe same 5x5 assessment AFTER mitigation (`## Residual Assessment`), a TARA\nresponse strategy (`## Strategy`: transfer / accept / reduce / avoid), and the\ntreatment measures bridging the two (`## Mitigation`), scoped to the affected\nsystem(s) (`## Scope`). `rsk` follows the domain-first hierarchy and MCP\nsurface already established by `req`/`tsk` (ADR\nece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/resources shape\nalmost exactly (per GitHub issue #15).\n\n### Requirements\n\n- [ ] REQ-001: Define the `rsk` markdown schema — frontmatter (`type=\"rsk\"`,\n  6-value status set: `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`,\n  default `open`) and body (H1 title, optional leading comment, mandatory\n  `## Cause`, mandatory `## Trigger`, mandatory `## Consequence`, mandatory\n  `## Scope` list (>=1 affected system/component), mandatory `## Initial\n  Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory\n  `## Strategy` (TARA 4-value closed set: `transfer`/`accept`/`reduce`/\n  `avoid`), mandatory `## Mitigation`, mandatory `## Residual Assessment`\n  (5x5, same shape as initial), optional `## Owner`, optional `## Tags`\n  list, optional `## More Information`)\n- [ ] REQ-002: Pydantic models for `rsk` documents (`rsk/models/v1/` —\n  domain-first path, mirroring `tsk/models/v1/` and `req/models/v1/`)\n- [ ] REQ-003: Parse and validate `rsk` documents from markdown\n  (`parse_rsk`, mirroring `parse_tsk`/`parse_req`)\n- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`,\n  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,\n  `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`\n- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`,\n  `/example`, `/schema`, `/template`\n- [ ] REQ-006: MCP prompts — `create_risk`, `update_risk` (narrated tool\n  sequences, mirroring `req/prompts/create_req.py`/`update_req.py` and\n  `tsk/prompts/create_task.py`/`update_task.py`)\n- [ ] REQ-007: Packaged example/template/schema data (`rsk/data/`) via the\n  existing generic `general/tools/_packaged_data.py`, with the matching\n  `pyproject.toml` package-data entry, pre-commit hook, and CI step\n- [ ] REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema`\n  (new `rsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept\n  drift-free via pre-commit/CI\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/rsk_schema.json`,\n  `specmgr://rsk/schema`), reference `rsk` document (`rsk_reference.md`)\n  round-trips through the parser (`test_parses_full_reference_document`),\n  including both 5x5 assessments (probability/impact bounded 1..5, derived\n  level zone correct)\n- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required/optional\n  fields correctly, including the `Assessment` probability/impact/derived-level\n  split, the TARA closed set, `Scope` (>=1) and the `Tags`/`Owner`/\n  `More Information` absent-vs-present cases (`tests/rsk/models/v1/`)\n- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree;\n  malformed input raises (structural `AssertionError` / field-level\n  `pydantic.ValidationError`, matching `req`/`tsk`'s error-channel convention)\n  — `tests/rsk/models/v1/test_parser.py`\n- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`), with\n  `create_rsk`/`update_rsk` validating body-only content the same way\n  `create_req`/`update_req`/`create_tsk`/`update_tsk` do\n- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`)\n- [ ] ACC-006: Verifies REQ-006 — `create_risk`/`update_risk` prompts narrate\n  the correct tool sequence (`tests/rsk/prompts/`)\n- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a\n  real, non-editable install, mirroring `req`'s (feat-6 Task 5.1) and `tsk`'s\n  (feat-10 ACC-007) own verification\n- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/\n  `specmgr mcp-docs` all report no drift after implementation\n\n### Scope\n\n**Included in this feature:**\n\n- Specification of the `rsk` markdown schema (frontmatter + body), including\n  the cause/trigger/consequence scenario split, the 5x5 initial/residual\n  assessment, the TARA strategy set, and the before/after-mitigation\n  structure\n- Pydantic models, parser, and schema generation under `rsk/models/v1/`\n- Full MCP surface (tools/resources/prompts/packaged data) mirroring\n  `req`/`tsk`\n- Tests mirroring `tests/req/`'s and `tests/tsk/`'s layout and coverage\n\n**Explicitly out of scope:**\n\n- Aggregated, register-wide views (e.g. a combined risk-matrix chart across\n  all `rsk` documents) — `RskSummary` (see `specmgr://rsk/list`) carries\n  `initial_level`/`residual_level`/`strategy` per document precisely so such a\n  view can be built later without reading each document\n- Cross-referencing/linking `rsk` documents to other artifact types\n  (REQ/UC/ADR) — not part of this feature\n- Risk relationships (dependency, correlation, common-cause analysis)\n- A `specmgr rsk-toc`-equivalent generation command or its own CI/pre-commit\n  drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`\n  already provide generically\n\n### Dependencies\n\n- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic\n  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614\n  (id-based reads as a tool, not a resource), `general/tools/_doc_paths.py`\n  and `_packaged_data.py`, the existing `models/md` engine — in particular\n  `MarkdownSection1WithComment`, `MarkdownSection2`, the generic\n  `list[MarkdownStr]` engine (`process_list_field`), and `tsk`'s\n  `TaskItem` custom-list-item-leaf precedent (parsing a non-standard marker\n  into computed fields with parent-level eager validation)\n- Blocks: None identified yet\n\n### Design Notes\n\n- **Body shape** — `Risk` (the body's H1 class) subclasses the existing\n  `MarkdownSection1WithComment` mixin (`models/md/`), reusing it as-is (no\n  new mixin needed):\n\n  ```\n  # {H1 title}\n  <!-- optional leading comment -->            comment: MarkdownComment | None\n\n  ## Cause                                     cause: MarkdownStr  (mandatory)\n  {Why the risk exists — the root condition}\n\n  ## Trigger                                   trigger: MarkdownStr  (mandatory)\n  {What sets the risk event in motion}\n\n  ## Consequence                                consequence: MarkdownStr  (mandatory)\n  {What happens if the risk event occurs}\n\n  ## Scope                                     scope: list[MarkdownStr]  (>=1)\n  - {Affected system / component}\n  - {Another affected system / component}\n\n  ## Initial Assessment                        initial_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Strategy                                  strategy: str  (TARA closed 4-value set)\n  {transfer | accept | reduce | avoid}\n\n  ## Mitigation                                mitigation: MarkdownStr  (mandatory)\n  {Treatment measures; \"none\" if strategy is accept}\n\n  ## Residual Assessment                       residual_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Owner                                     owner: MarkdownStr | None\n  {Responsible person / role}\n\n  ## Tags                                      tags: list[MarkdownStr] | None\n  - {tag}\n\n  ## More Information                          more_information: MarkdownStr | None\n  {Free-form}\n  ```\n\n  Order is enforced by the model: title -> optional comment -> Cause ->\n  Trigger -> Consequence -> Scope -> Initial Assessment -> Strategy ->\n  Mitigation -> Residual Assessment -> optional Owner -> optional Tags ->\n  optional More Information. The scenario sections (Cause/Trigger/\n  Consequence) lead the document; the before/after pair (Initial Assessment\n  ... Residual Assessment) is separated by exactly the sections that explain\n  the delta: `Strategy` (chosen TARA response) and `Mitigation` (the\n  measures taken).\n\n- **Assessment structure (initial/residual)** — each assessment is one cell\n  of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;\n  1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...\n  5 = severe), written as exactly two list items under the H2 heading:\n\n  ```\n  ## Initial Assessment\n  - Probability: 4\n  - Impact: 3\n  ```\n\n  The model derives the zone `level` from the product of the two\n  coordinates (probability x impact):\n\n  | p \\ i | 1      | 2      | 3      | 4        | 5         |\n  |-------|--------|--------|--------|----------|-----------|\n  | 1     | low    | low    | low    | low      | medium    |\n  | 2     | low    | low    | medium | medium   | high      |\n  | 3     | low    | medium | medium | high     | very high |\n  | 4     | low    | medium | high   | high     | very high |\n  | 5     | medium | high   | high   | very high| very high |\n\n  Zone thresholds on the product: 1-4 `low`, 5-9 `medium`, 10-14 `high`,\n  15-25 `very high`.\n\n  **Worked example** (risk: untrusted file uploads parsed by an unmaintained\n  parser library, affecting the document-processing subsystem):\n\n  ```\n  ## Cause\n  The parser library has no security updates since 2021.\n\n  ## Trigger\n  An uploaded file exploits a known format flaw.\n\n  ## Consequence\n  Remote code execution in the document-processing subsystem; other\n  subsystems unaffected (isolated network zone).\n\n  ## Scope\n  - document-processing subsystem\n\n  ## Initial Assessment\n  - Probability: 4\n  - Impact: 3\n\n  ## Strategy\n  reduce\n\n  ## Mitigation\n  Replace the parser with a maintained library; restrict uploads to a\n  format whitelist.\n\n  ## Residual Assessment\n  - Probability: 2\n  - Impact: 3\n  ```\n\n  Initial cell 4 x 3 = 12 -> `high`; residual cell 2 x 3 = 6 -> `medium`:\n  the mitigation moved the risk one zone down. That before/after pair is the\n  register's audit trail — a sensible `reduce` strategy must show\n  residual < initial (the example's annotations are for readability only;\n  the document stores the two list items, and `level` is always computed,\n  never written).\n\n- **Strategy (TARA)** — `## Strategy` is a single-line H2 section whose\n  content is validated against the closed 4-value set `transfer`/`accept`/\n  `reduce`/`avoid` — the TARA framework's risk-response strategies\n  (Transfer, Accept, Reduce, Avoid; cf.\n  https://www.consuunt.com/tara-framework/) — same narrowing approach\n  `ReqFrontmatter` applies to its `status` field, at body-section level.\n  Mandatory: every risk in a register has a disposition. Only the four valid\n  TARA words are accepted; anything else (e.g. the TARRA-era words\n  `tolerate`/`assign`/`recover`) is a validation error.\n\n- **Frontmatter status** — `open`/`mitigating`/`accepted`/`occurred`/\n  `closed`/`dropped`, default `open`: a purpose-fit risk lifecycle (user-\n  selected 2026-08-24) rather than reusing REQ's 7-value ADR-like set —\n  `open` = identified and monitored; `mitigating` = treatment in progress;\n  `accepted` = residual risk formally accepted; `occurred` = the risk event\n  materialized (tracked as incident); `closed` = resolved/expired; `dropped`\n  = removed from the register (not a real risk, duplicate, or out of scope).\n\n- **List summary** — `RskSummary` (for `specmgr://rsk/list`) carries\n  `id`/`title`/`status` plus `initial_level`, `residual_level`, `strategy`,\n  and the first `scope` entry, so a register-wide risk-matrix view can be\n  built from the listing alone.\n\n- **Prompt naming** — `create_risk`/`update_risk` follow the\n  `tsk`-prompt precedent of the issue's literal wording (issue #15 names\n  both), not the `rsk`-prefixed convention the tools/resources use.\n\n### Related ADRs\n\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by\n  document-type domain (domain-first hierarchy)\n- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for\n  markdown document types\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a\n  tool (get_rsk), not a resource\n\nNo new ADR is anticipated for this feature — the `Assessment` 5x5 parsing\napproach, the TARA closed set, and the 6-value status set are scoped enough\nto log only in this file's own Decisions Made, not a full ADR.\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself — there is no separate \"planned\" vs. \"executed\" list to keep in\nsync; a task's line *is* its current status. Update it in place as work\nprogresses (edit, don't duplicate).\n\n**Execution approach** (to confirm at Phase 1 start, see Decisions Made):\neach phase below is delegated to the `implementation-specialist` subagent as\none unit (implementation + its own mirrored tests together, not a separate\nlater test phase), reviewed and quality-gated (ruff format/check, vulture,\nfull `unittest` suite) by the orchestrator, then committed as one\nConventional Commit per phase — the `feat-10` (tsk) 4-phase/4-commit shape.\n\n#### Phase 1: Specification (commit 1)\n\n- [ ] Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` —\n  `RskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal[\"rsk\"]`,\n  6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/\n  `dropped`) — depends on: none — status: not-started\n- [ ] Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`,\n  `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with\n  `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/\n  `mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;\n  `Assessment` (new `MarkdownSection2` leaf: `probability`/`impact` int 1..5\n  parsed from `- Probability: N`/`- Impact: N` list items via a\n  `MarkdownListItem` subclass with computed fields, derived `level` computed\n  field from the product zones, parent-level eager-validation\n  `model_validator` on the `Risk` H1 per the `TaskItem` precedent) —\n  depends on: Task 1.1 — status: not-started\n- [ ] Task 1.3: Create a reference `rsk` document (`rsk_reference.md`)\n  exercising every field (cause/trigger/consequence, full initial +\n  residual 5x5 pair, all mandatory and optional sections), used as the\n  parser's round-trip test fixture — depends on: Task 1.2 — status:\n  not-started (placed at\n  `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md`, mirroring\n  `tsk_reference.md`'s own location convention, not `rsk/data/`)\n- [ ] Task 1.4: `tests/rsk/models/v1/test_frontmatter.py`,\n  `test_body.py`/`test_assessment.py` — structural + validation tests\n  mirroring `tests/tsk/models/v1/`: status set, 5x5 bounds and derived-\n  level zones (all four zone boundaries: 4/5, 9/10, 14/15), TARA closed\n  set, `Scope` >=1, `Tags`/`Owner`/`More Information` absent-vs-present —\n  depends on: Task 1.3 — status: not-started\n\n#### Phase 2: Pydantic Models & Parser (commit 2)\n\n- [ ] Task 2.1: `rsk/models/v1/document.py` (`RskDocument(frontmatter,\n  body)`, mirroring `TskDocument`) — depends on: Task 1.3 — status:\n  not-started\n- [ ] Task 2.2: Implement `parse_rsk(text: str) -> RskDocument` (mirrors\n  `parse_tsk`/`parse_req`) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry, for the\n  `specmgr://rsk/list` resource) — depends on: Task 2.1 — status:\n  not-started\n- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/\n  optional field (schema-quality parity with REQ/TSK's own Task 2.4\n  audits) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.5: Draft `rsk_schema.json` via `generate_rsk_schema()`\n  (mirroring `generate_req_schema`/`generate_tsk_schema` in\n  `commands/schema.py`, calling `RskDocument.model_json_schema()`) +\n  register `\"rsk\"` in the `specmgr schema` doc-type generator registry\n  (`_GENERATORS`) — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.6: `tests/rsk/models/v1/test_parser.py` — mirrors\n  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,\n  defaults-when-absent, invalid status, malformed structure, out-of-range\n  probability/impact, invalid TARA word, missing Scope entry) — depends on:\n  Task 2.2, Task 2.5 — status: not-started\n\n#### Phase 3: MCP Surface (commit 3)\n\n- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,\n  thin wrappers over `general/tools/_doc_paths.py` (mirrors\n  `tsk/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:\n  not-started\n- [ ] Task 3.2: `parse_rsk(path: str) -> RskDocument` tool wrapper\n  (`rsk/tools/parse_rsk.py`, mirroring `tsk/tools/parse_tsk.py` — reads a\n  filepath from disk, delegates to the model-layer `parse_rsk`) — depends\n  on: Task 3.1 — status: not-started\n- [ ] Task 3.3: `create_rsk(content: str) -> RskDocument` tool (body-only\n  content, MCP builds frontmatter: `id`, `type=\"rsk\"`, `status=\"open\"`,\n  `created=updated=now`, `version`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: `update_rsk(id, content) -> RskDocument` tool (whole-body\n  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps\n  `updated`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: `set_status_rsk(id, status) -> RskDocument` tool (only path\n  that changes `status`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.6: `delete_rsk(id) -> NoReturn` stub tool — depends on: Task\n  3.1 — status: not-started\n- [ ] Task 3.7: `validate_rsk(content, full=False) -> bool` tool — depends\n  on: none — status: not-started\n- [ ] Task 3.8: `get_rsk(id) -> RskDocument` tool (id-based single-document\n  read; tool, not resource — per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614)\n  — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.9: `get_rsk_example`/`get_rsk_template` tools + packaged data\n  (`rsk/data/rsk_example.md`, `rsk/data/rsk_template.md`) via\n  `general/tools/_packaged_data.py` — depends on: Task 1.3 — status:\n  not-started\n- [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources\n  (packaged `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`) —\n  depends on: Task 3.1, Task 2.5 — status: not-started\n- [ ] Task 3.11: `specmgr://rsk/example` and `specmgr://rsk/template`\n  resources — depends on: Task 3.9 — status: not-started\n- [ ] Task 3.12: `pyproject.toml` package-data entry for\n  `biz.dfch.specmgr.rsk` (`data/*.md`, `data/*.json`), pre-commit hook +\n  CI step for the packaged `rsk_schema.json` copy (mirroring\n  `specmgr-schema-tsk-package`) — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — narrate\n  the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)\n  — depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10 — status: not-started\n- [ ] Task 3.14: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers) —\n  depends on: Tasks 3.2-3.13 — status: not-started\n- [ ] Task 3.15: `tests/rsk/tools/...`, `tests/rsk/resources/...`,\n  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/\n  resources/`/`tests/tsk/prompts/` layout — depends on: Tasks 3.1-3.14 —\n  status: not-started\n\n#### Phase 4: Docs, CI wiring & final verification (commit 4)\n\n- [ ] Task 4.1: `specmgr docs` regeneration (new `rsk` modules picked up) —\n  depends on: Phase 1-3 complete — status: not-started\n- [ ] Task 4.2: `specmgr mcp-docs` regeneration (new tools/resources/\n  prompts appear in `docs/MCP.md`) — depends on: Phase 3 complete — status:\n  not-started\n- [ ] Task 4.3: CI wiring — confirm the Python-3.13-only `specmgr schema`/\n  `specmgr docs`/`specmgr mcp-docs` steps in `.github/workflows/ci.yml`\n  cover `rsk` with no separate per-type step needed (registry-driven,\n  mirroring `req`/`tsk`'s own wiring) — depends on: Task 4.1, Task 4.2 —\n  status: not-started\n- [ ] Task 4.4: Final verification pass — walk every ACC-001..008 below and\n  confirm each is actually satisfied; run the full quality gate (ruff\n  format/check, pylint advisory, vulture, unittest, `specmgr docs`,\n  `specmgr schema`, `specmgr mcp-docs` drift checks) once more end-to-end —\n  depends on: Tasks 4.1-4.3 — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder\ncreated from `.specmgr/_template/v1/README.md`. Full schema and MCP surface\nproposed (see Design Notes and Task List), mirroring `feat-10` (tsk)'s\n4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead\nof TARRA, cause/trigger/consequence split into separate sections, assessment\nstructure documented with a worked example). Awaiting final review before\nPhase 1 starts.\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### 2026-08-24T11:55:11+02:00 (newest)\n\n- Completed: revised the plan per user feedback — (1) `## Strategy`\n  corrected from the TARRA 5-value set to the TARA 4-value closed set\n  `transfer`/`accept`/`reduce`/`avoid` (the valid TARA words, per the TARA\n  framework, https://www.consuunt.com/tara-framework/); only those four\n  words are accepted; (2) the single `## Description` section replaced by\n  three separate mandatory H2 sections `## Cause`, `## Trigger`,\n  `## Consequence`; (3) added a Design Notes entry explaining the\n  initial/residual assessment structure (5x5 zone table with product\n  thresholds) plus a worked example showing a `reduce` strategy moving the\n  risk from `high` (4x3=12) to `medium` (2x3=6); GitHub issue #15's body\n  updated to match\n- Next: user review; then Phase 1 (Specification)\n- Notes: see the two new Decisions Made entries below (supersede the\n  earlier TARRA and single-`Description` decisions)\n\n#### 2026-08-24T11:31:28+02:00\n\n- Completed: opened GitHub issue #15 (\"Add artifact type Risk\"); created\n  branch `feat-15-add-artifact-type-risk` from `dev`; drafted this feature\n  plan (schema with 5x5 initial/residual assessment, TARA strategy,\n  6-value status, scope/tags/owner/more-information) modeled on\n  `feat-10-add-artifact-type-tasklist`\n- Next: user review of the proposed attribute set (Design Notes); then\n  Phase 1 (Specification)\n- Notes: `Assessment` parsing reuses `tsk.TaskItem`'s custom-list-item-leaf +\n  eager-validation precedent; no new ADR anticipated\n\n### Decisions Made\n\n- **2026-08-24**: Target GitHub issue #15, opened up front (no earlier issue\n  describes this feature) — rationale: the `feat-NNN-slug` convention\n  embeds the issue number; opening it first avoids the branch/folder rename\n  pass `feat-10` did when its local branch predated its issue number.\n- **2026-08-24**: Frontmatter `status` is the 6-value set `open`/\n  `mitigating`/`accepted`/`occurred`/`closed`/`dropped`, default `open` —\n  rationale: user-selected (question, 2026-08-24); purpose-fit to a risk\n  lifecycle rather than reusing REQ's 7-value ADR-like set or tsk's 4-value\n  todo set.\n- **2026-08-24**: Before/after mitigation is modeled as two separate\n  `Assessment` sections (`## Initial Assessment` and `## Residual\n  Assessment`), each 5x5 (probability 1..5, impact 1..5), with `## Strategy`\n  and `## Mitigation` between them — rationale: user requirement for \"a\n  separate risk matrix impact/probability of 5x5 for BEFORE and AFTER\n  mitigation (residual risk)\"; the juxtaposition makes the mitigation\n  effect directly auditable (a sensible `reduce` strategy shows\n  residual < initial).\n- **2026-08-24**: The derived risk `level` (`low`/`medium`/`high`/`very_\n  high`) is a computed field from the probability x impact product zones\n  (1-4 low, 5-9 medium, 10-14 high, 15-25 very high), never stored in the\n  markdown — rationale: keeps the 5x5 mapping in one place and avoids stale\n  derived values on round-trip, following `tsk.TaskItem.checked`'s\n  computed-field convention.\n- **2026-08-24** (superseded): `## Strategy` was initially proposed as the\n  TARRA 5-value set `tolerate`/`assign`/`reduce`/`recover`/`avoid`, and the\n  risk scenario was initially a single `## Description` section — superseded\n  by the two decisions below.\n- **2026-08-24**: `## Strategy` is the TARA 4-value closed set\n  `transfer`/`accept`/`reduce`/`avoid` (Transfer, Accept, Reduce, Avoid —\n  the TARA framework, https://www.consuunt.com/tara-framework/), mandatory,\n  single-line validated; only those four valid TARA words are accepted —\n  rationale: user correction with reference (the initially proposed \"TARRA\"\n  set was the wrong acronym); same narrowing approach `ReqFrontmatter` uses\n  for its `status` field.\n- **2026-08-24**: The risk scenario is split into three separate mandatory\n  H2 sections `## Cause` (root condition), `## Trigger` (what sets the event\n  in motion), `## Consequence` (what happens if it occurs) — rationale:\n  user requirement; each scenario aspect gets its own validated section\n  instead of one mixed free-text blob, keeping cause/trigger/consequence\n  mechanically checkable (all three present and non-blank).\n- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected\n  system/component); `## Owner`, `## Tags`, `## More Information` are\n  optional — rationale: scope answers \"which system is affected\" and is\n  central to a risk (user requirement); the remaining three follow ADR's\n  optional `more_information` precedent and keep the schema lean.\n\n### Related PRs / Commits\n\nNo PR opened yet. Work happens on branch `feat-15-add-artifact-type-risk`\n(from `dev`), one Conventional Commit per phase (see Execution approach).\n",
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md"
}
````

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 147.6s)

_Thinking:_

Wait—I need to re-check one of the edits I made: in the second entry of Recent Updates (the original 11:31 one), I wrote "TARA strategy", but that entry historically should have been recording the original draft which was TARRA. Hmm, let me think about this. The original entry said "drafted this feature plan (schema with 5x5 initial/residual assessment, TARA strategy, ...)". Actually, the first draft said TARRA. But the Recent Updates log is a living document—feat-10's log entries describe what happened at that point in time. The first entry was written at 11:31, and at that time the plan was TARRA. To be historically accurate, that entry should say TARRA. But it's a trivial thing... no wait—there's a subtle point: I want the log to be accurate. Let me fix that entry to say TARRA (as it originally was). Hmm, but the "superseded" decision entry covers that. Let me fix the 11:31 entry to say "TARRA strategy" to preserve historical accuracy.

Actually, let me reconsider: is it worth editing? Accuracy of the decision log matters in this repo (they take this seriously). Yes, a quick fix.

Next, update the body of GitHub issue #15 with TARA + cause/trigger/consequence.

New issue body:

```
Creates a new artifact type `Risk`:

* Abbreviation `rsk`
* Subfolder as `req`/`tsk`
* Resources: same as `req`
* Tools: same as `req`
* Prompts: `create_risk` and `update_risk`

Attributes:

* Frontmatter `status`: `open` / `mitigating` / `accepted` / `occurred` / `closed` / `dropped` (default `open`)
* H1 title, optional leading comment
* `## Cause` (required): root condition—why this risk exists
* `## Trigger` (required): what causes the risk event to occur
* `## Consequence` (required): what happens if the risk event occurs
* `## Scope` (required, list): which systems/components are affected
* `## Initial Assessment` (required): 5x5 risk matrix before mitigation—probability 1..5 and impact 1..5 (derived level: low / medium / high / very high)
* `## Strategy` (required): TARA—`transfer` / `accept` / `reduce` / `avoid`
* `## Mitigation` (required): response measures ("none" if strategy is `accept`)
* `## Residual Assessment` (required): 5x5 risk matrix after mitigation (residual risk)
* `## Owner` (optional): responsible person/role
* `## Tags` (optional, list): free-form tags
* `## More Information` (optional): free-form

This artifact is needed for risk registers in system specifications: risks with
explicit pre- and post-mitigation 5x5 assessments (residual risk) and a TARA
response strategy, managed as first-class artifacts alongside requirements and use cases.
```

Write to /tmp/opencode/rsk-issue-body.md (overwrite), then `gh issue edit 15 --body-file`.

Now fix the historical accuracy of the first Recent Updates entry (it originally proposed TARRA), and update issue #15's body:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- Completed: opened GitHub issue #15 (\"Add artifact type Risk\"); created\n  branch `feat-15-add-artifact-type-risk` from `dev`; drafted this feature\n  plan (schema with 5x5 initial/residual assessment, TARA strategy,\n  6-value status, scope/tags/owner/more-information) modeled on\n  `feat-10-add-artifact-type-tasklist`",
  "newString": "- Completed: opened GitHub issue #15 (\"Add artifact type Risk\"); created\n  branch `feat-15-add-artifact-type-risk` from `dev`; drafted this feature\n  plan (schema with 5x5 initial/residual assessment, strategy set,\n  6-value status, scope/tags/owner/more-information) modeled on\n  `feat-10-add-artifact-type-tasklist` — the first draft's strategy set and\n  single-`Description` section were revised the same day (see the entry\n  above and Decisions Made)"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: write**

**Input:**

```json
{
  "content": "We create a new artifact type `Risk`:\n\n* abbreviation `rsk`\n* sub-folder as `req`/`tsk`\n* resources: same as `req`\n* tools: same as `req`\n* prompts: `create_risk` and `update_risk`\n\nAttributes:\n\n* frontmatter `status`: `open` / `mitigating` / `accepted` / `occurred` / `closed` / `dropped` (default `open`)\n* H1 title, optional leading comment\n* `## Cause` (mandatory): root condition — why the risk exists\n* `## Trigger` (mandatory): what sets the risk event in motion\n* `## Consequence` (mandatory): what happens if the risk event occurs\n* `## Scope` (mandatory, list): which system/component is affected\n* `## Initial Assessment` (mandatory): 5x5 risk matrix BEFORE mitigation — probability 1..5 and impact 1..5 (derived level: low / medium / high / very high)\n* `## Strategy` (mandatory): TARA — `transfer` / `accept` / `reduce` / `avoid`\n* `## Mitigation` (mandatory): treatment measures (\"none\" if strategy is `accept`)\n* `## Residual Assessment` (mandatory): 5x5 risk matrix AFTER mitigation (residual risk)\n* `## Owner` (optional): responsible person/role\n* `## Tags` (optional, list): free-form tags\n* `## More Information` (optional): free-form\n\nThis artifact is needed for risk registers in system specifications: risks with an\nexplicit before/after mitigation 5x5 assessment (residual risk) and a TARA response\nstrategy, kept as first-class managed artifacts alongside requirements and use cases.\n",
  "filePath": "/tmp/opencode/rsk-issue-body.md"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 111.0s)

_Thinking:_

Wait, I need to reconsider the edit I just made to the 11:31 entry. The original text said "TARA strategy"—but I had rewritten it when I rewrote the file. The original draft (before the user's feedback) was TARRA. But in my rewrite, the first Recent Updates entry said "TARA strategy" (which would be historically inaccurate, since at 11:31 it was TARRA). I just fixed it to be neutral ("strategy set") and added a pointer to the revision. Good.

Hmm, wait, actually I should double-check that the current state of the file is consistent. Let me re-read the Recent Updates section and Decisions Made to verify. Also, the "superseded" decision entry I added says the following:

"**2026-08-24** (superseded): `## Strategy` was initially proposed as the TARRA 5-value set ..., and the risk scenario was initially a single `## Description` section — superseded by the two decisions below."

This is fine.

Now, let's update the issue body.

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue edit 15 --body-file /tmp/opencode/rsk-issue-body.md && git status --short",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/15
?? .specmgr/feat/feat-15-add-artifact-type-risk/

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 103.4s)

_Thinking:_

Updated the issue. The new feature folder is untracked (as expected — I haven't committed yet, and the user hasn't asked for a commit either).

Let me do a final check of the README to see if it renders correctly and is internally consistent — in particular, the new "Assessment Structure" design note with the table and worked example, and confirming that no "TARRA" remains except in the intentionally historical spot (the superseded decision entry).

**Tool: grep**

**Input:**

```json
{
  "include": "README.md",
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk",
  "pattern": "TARRA|tolerate|assign|recover"
}
```

**Output:**

```
Found 8 matches
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md:
  Line 254:   TARA words are accepted; anything else (e.g. the TARRA-era words

  Line 255:   `tolerate`/`assign`/`recover`) is a validation error.

  Line 426: place; rely on git history (`git log -p` on this file) to recover what was

  Line 437: of TARRA, cause/trigger/consequence split into separate sections, assessment

  Line 450:   corrected from the TARRA 5-value set to the TARA 4-value closed set

  Line 462:   earlier TARRA and single-`Description` decisions)

  Line 504:   TARRA 5-value set `tolerate`/`assign`/`reduce`/`recover`/`avoid`, and the

  Line 511:   rationale: user correction with reference (the initially proposed "TARRA"

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 119.9s)

_Thinking:_

All the remaining occurrences of "TARRA" are in the intended historical context (decision log / recent updates / a note that words from the TARRA era are validation errors). Line 426 is "recover what was originally planned," which is fine.

The plan has been fully updated. Summary for the user:

1. TARA: strategy is now `transfer`/`accept`/`reduce`/`avoid` — closed 4-value set, only valid TARA words are accepted (the words from the TARRA era are validation errors)
2. Cause/Trigger/Consequence are now three separate required H2 sections
3. Design Notes explains the structure of the assessment with a zone table and worked examples (initial 4x3=12 high → residual 2x3=6 medium)
4. The body of GitHub Issue #15 has been updated to match

Keeping the reply short.

Plan revised and issue #15 updated. Changes:

1. **TARA**: `## Strategy` is now the closed 4-value set `transfer` / `accept` / `reduce` / `avoid` — only valid TARA words accepted (TARRA-era words like `tolerate`/`assign`/`recover` are validation errors). The old TARRA decision is logged as *superseded* in Decisions Made.
2. **Cause / Trigger / Consequence**: three separate mandatory H2 sections (root condition / what sets the event in motion / what happens), replacing the single `## Description`.
3. **Assessment structure** — new Design Notes entry with:
   - the exact markdown shape (`- Probability: N` / `- Impact: N`, N 1..5)
   - the full 5x5 zone table with product thresholds (1–4 low, 5–9 medium, 10–14 high, 15–25 very high)
   - a worked example: unmaintained parser risk, initial 4×3 = 12 → `high`, `reduce` strategy, residual 2×3 = 6 → `medium` — showing the before/after pair as the register's audit trail

REQ-001/ACC-002/task-list references updated to match. Ready for your final review — then Phase 1 (Specification) can start.

______________________________________________________________________

## User

regarding "probability" and "impact": we cannot enforce a string on a bullet list item, but we can on a MarkdownSectionN. We dont we use level 3 sections "### Probability 3" and "### Impact 4" with a regex similar to this: "^Proability \\d$". With it we can enforce the heading and a number. Your opinion?

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 176.5s)

_Thinking:_

The user is proposing a structural change to the representation of `Assessment`:

Instead of this:

```
## Initial Assessment
- Probability: 4
- Impact: 3
```

(parsed as a custom `MarkdownListItem` subclass, like `TaskItem`)

Use H3 subsections with regex headings:

```
## Initial Assessment
### Probability 4
### Impact 3
```

The heading itself encodes the value: `^Probability \d$` (the user wrote "Proability" with a typo, but the intent is clear). The user says: "You can't enforce a string on a bullet list item, but you can on a MarkdownSectionN. Why not use level 3 sections '### Probability 3' and '### Impact 4' with a regex like this: '^Proability \\d$'. Then we can enforce the heading and the number. What do you think?"

Interesting — they're referencing an existing mechanism: a regex alias on a heading. The feat-10 design notes say: `UpdateEntry` was a free-form-title H3 leaf via `@alias(value=".+", type=AliasType.REGEX)`. In other words, the `models/md` engine supports heading aliases with `AliasType.REGEX` — the heading text is matched against a regex. This is exactly what the user is suggesting: a `MarkdownSection3` subclass with a regex-constrained heading like `^Probability \d$`…

Wait, but how do heading-mapped sections work in this engine? Let me think. In `models/md`, sections are mapped to fields by heading. For a dynamic list of H3 entries (like `RecentUpdates.updates`), each H3 is a leaf with `@alias(value=".+", type=AliasType.REGEX)` — meaning "any H3 heading matches, and the title is captured." In `AdrOption`, the heading pattern is `Option {number}: ` with numbered matching.

So the user's idea is: make `Assessment` an H2 section containing two H3 sections, whose headings are `### Probability {n}` and `### Impact {n}` where n is 1..5. The value is extracted from the heading itself via a regex alias like `^Probability ([1-5])$`… The user's regex `^Proability \d$` captures the number in the heading.

Hmm, but is a regex alias in this engine capable of *capturing* groups and mapping them to fields? Let me check `models/md/alias.py` and `markdown_section.py` to understand the capability. The user is asking for my opinion, so I need to understand what's feasible:

1. If the engine supports capturing groups within a heading regex that map to a field (like `AliasType.REGEX` with named groups?), then the H3 approach works cleanly: the heading enforces both the key and the value.

2. If it only supports match/no-capture (like `.+` → the whole heading text is the "title" of a free-form entry), then the value would end up being parsed from the heading text by another mechanism.

To give an informed opinion, let me look at the actual engine code. Key files: `models/md/alias.py`, `models/md/alias_match.py`, `models/md/alias_type.py`, `models/md/markdown_section.py`, `models/md/_markdown.py`, and how `UpdateEntry` (tsk) and `AdrOption` use the regex alias.

Let me read these. I should form a real opinion, not just agree.

Considerations for the opinion:

**Arguments in favor of the H3 approach:**

- The heading itself enforces structure: a malformed `### Probability 7` or `### Probability` fails the regex at parse time — "successful parsing is validation," matching the project's convention.
- No custom `MarkdownListItem` subclass needed (the TaskItem-style leaf is a workaround for a parser that has no GFM plugin — but here the H3 regex alias is a *first-class* mechanism of the engine).
- The feat-10 precedent used exactly this mechanism for `UpdateEntry` (`@alias(value=".+", type=AliasType.REGEX)`), so this is idiomatic in this codebase.

**Arguments against / things to verify:**

- Does the regex alias mechanism support *capture groups* and mapping them to fields? Or does it only do matching, with the value coming from the section content? If the value has to come from the content (empty H3 with a body), then `### Probability\n4\n` is… hmm.
- The H3 section's content: what goes in it? If the value is in the heading, the H3's content is empty. Does the engine allow an empty H3 section? (ADR options have content; tsk's `UpdateEntry` has content = update text.)
- Semantics: "### Probability 4" as a heading is a bit unusual as a document — but for machine-generated, machine-managed documents it's actually fine, and unambiguous for both parser and reader.

Let me check the code to see what's supported. Files to read:

- `src/biz/dfch/specmgr/models/md/alias.py`
- `src/biz/dfch/specmgr/models/md/alias_match.py`
- `src/biz/dfch/specmgr/models/md/alias_type.py`
- `src/biz/dfch/specmgr/models/md/markdown_section.py` (how H3 children are handled)
- tsk's `body.py` (how `UpdateEntry` uses `.+`)
- adr's model (how `AdrOption` uses a numbered pattern) — under `models/adr/v1/`

Let me start exploring.

Good question — let me check what the `models/md` heading-alias engine actually supports before opining, since the feasibility hinges on whether regex aliases can capture the value or only match it.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/alias.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/alias.py</path>
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
18: """Alias decorator for MarkdownStr class name transformation.
19: 
20: This module provides the @alias decorator to control how class names are
21: displayed, independent of the @annotate decorator. Works in combination with
22: @annotate to separate concerns: @annotate defines markdown-it properties, while
23: @alias controls display naming.
24: """
25: 
26: from __future__ import annotations
27: 
28: from .alias_type import AliasType
29: 
30: 
31: def alias(value: str | None = None, type: AliasType = AliasType.SPACE_SEPARATED):
32:     """Decorator to set a display name/alias for a MarkdownStr class.
33: 
34:     Separates alias configuration from markdown-it type information. Use this
35:     decorator in combination with @annotate to control how class names are
36:     displayed.
37: 
38:     Args:
39:         value: The alias/display name for the class. Interpretation depends on type:
40:                - LITERAL: Used as exact display name
41:                - SPACE_SEPARATED: Ignored; class name is converted automatically
42:                - REGEX: Treated as a regex pattern for matching
43:                If not provided, class name is used.
44:         type: How to interpret the alias value. One of AliasType values:
45:               - AliasType.SPACE_SEPARATED: Auto-convert class name to title case
46:                 with spaces (e.g., RequiredInformation → Required Information)
47:               - AliasType.LITERAL: Use alias as exact string (explicit override)
48:               - AliasType.REGEX: Treat alias as regex pattern
49:               Defaults to AliasType.SPACE_SEPARATED.
50: 
51:     Returns:
52:         A class decorator that attaches alias metadata to the decorated class.
53: 
54:     Example:
55:         Space-separated (automatic conversion):
56:         >>> @annotate(type="paragraph_open")
57:         ... @alias(type=AliasType.SPACE_SEPARATED)
58:         ... class RequiredInformation(MarkdownStr): ...
59:         >>> RequiredInformation._alias_metadata['value']
60:         'Required Information'
61: 
62:         Literal alias (explicit):
63:         >>> @annotate(type="heading_open", tag="h1")
64:         ... @alias(value="Custom Title")
65:         ... class Title(MarkdownStr): ...
66:         >>> Title._alias_metadata
67:         {'value': 'Custom Title', 'type': 'LITERAL'}
68: 
69:         Regex pattern matching:
70:         >>> @annotate(type="inline")
71:         ... @alias(value=r"^Title.*", type=AliasType.REGEX)
72:         ... class Title(MarkdownStr): ...
73:         >>> Title._alias_metadata['type']
74:         'REGEX'
75:     """
76: 
77:     def decorator(cls):
78:         cls._alias_metadata = {
79:             "value": value or cls.__name__,
80:             "type": type,
81:         }
82:         return cls
83: 
84:     return decorator

(End of file - total 84 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/alias_match.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/alias_match.py</path>
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
18: """Match a parsed heading's actual text against a class's declared `@alias`.
19: 
20: Encapsulates the comparison logic so `MarkdownSection.from_text` can assert
21: that the heading it just parsed is actually the one the class claims to
22: represent, instead of leaving `@alias`'s `_alias_metadata` as inert,
23: never-checked class data.
24: """
25: 
26: from __future__ import annotations
27: 
28: import re
29: 
30: from .alias_type import AliasType
31: 
32: _SPACE_SEPARATED_PATTERN = re.compile(r"(?<!^)(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])")
33: 
34: 
35: def space_separated_name(class_name: str) -> str:
36:     """Convert a PascalCase class name to space-separated title case.
37: 
38:     E.g. `"GoalInContext"` -> `"Goal In Context"`, `"SectionLevel1"` ->
39:     `"Section Level 1"`. This is `AliasType.SPACE_SEPARATED`'s
40:     auto-derivation rule -- an explicit, opt-in alternative for a class
41:     whose natural heading text differs from its bare class name (see
42:     `match_alias`; this is no longer the fallback for a class with no
43:     `@alias` metadata at all).
44: 
45:     Args:
46:         class_name: A class's `__name__`, e.g. `"GoalInContext"`.
47: 
48:     Returns:
49:         `class_name` with a space inserted before every non-leading
50:         uppercase letter, and at every letter<->digit boundary in either
51:         direction (e.g. `"SectionLevel1"` -> `"Section Level 1"`,
52:         `"Level1abc"` -> `"Level 1 abc"`). A run of consecutive digits
53:         (`"Level123"` -> `"Level 123"`) or consecutive uppercase letters is
54:         never split internally by this rule.
55:     """
56:     assert isinstance(class_name, str) and class_name, class_name
57: 
58:     result = _SPACE_SEPARATED_PATTERN.sub(" ", class_name)
59: 
60:     return result
61: 
62: 
63: def match_alias(cls: type, heading_text: str) -> bool:
64:     """Return whether `heading_text` satisfies `cls`'s declared `@alias`.
65: 
66:     A class with no `_alias_metadata` at all (no `@alias` decorator applied,
67:     directly or inherited) defaults to `AliasType.SPACE_SEPARATED`'s own
68:     derivation of `cls.__name__` -- equivalent to an implicit
69:     `@alias(type=AliasType.SPACE_SEPARATED)` -- rather than accepting any
70:     heading text (see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0; a
71:     literal match against `cls.__name__` verbatim was v1.2.0/v1.3.0/v1.3.1's
72:     incorrect specification of this same default, corrected in v1.4.0).
73:     `@alias` is opt-in for *customizing* the comparison away from that
74:     default (a literal value with different wording/casing/suffixes/
75:     formatting, or a regex), not for enabling matching in the first place:
76:     an undecorated `MarkdownSection` subclass is always checked against
77:     something. A class whose heading text is data rather than a fixed
78:     schema label (e.g. a document's own H1 title) should declare an
79:     explicit `@alias(value=".+", type=AliasType.REGEX)` to accept any
80:     non-empty heading text (v1.3.1) -- there is no separate opt-out of alias
81:     matching for this case; the `SPACE_SEPARATED` default alone would still
82:     pin such a title to a fixed, class-name-derived value.
83: 
84:     Args:
85:         cls: A `MarkdownSection` subclass, possibly decorated with `@alias`.
86:         heading_text: The heading's actual inline content, as parsed by
87:             `MarkdownSection.from_text` (e.g. `t_mid.content.strip()`).
88: 
89:     Returns:
90:         `True` if `heading_text` satisfies the effective `@alias` -- either
91:         the declared one, or the implicit `SPACE_SEPARATED`-derived default
92:         when none is declared -- under the applicable `AliasType`:
93:         - `LITERAL`: `heading_text` equals the declared value exactly
94:           (case-sensitive, no normalization).
95:         - `SPACE_SEPARATED`: `heading_text` equals `cls.__name__` converted
96:           via `space_separated_name`.
97:         - `REGEX`: `heading_text` fully matches the declared value as a
98:           regular expression pattern.
99:         `False` otherwise.
100:     """
101:     assert isinstance(cls, type), type(cls)
102:     assert isinstance(heading_text, str), type(heading_text)
103: 
104:     metadata = getattr(cls, "_alias_metadata", None)
105:     if metadata is None:
106:         return heading_text == space_separated_name(cls.__name__)
107: 
108:     alias_type = metadata["type"]
109:     alias_value = metadata["value"]
110: 
111:     if alias_type == AliasType.LITERAL:
112:         result = heading_text == alias_value
113:     elif alias_type == AliasType.SPACE_SEPARATED:
114:         result = heading_text == space_separated_name(cls.__name__)
115:     elif alias_type == AliasType.REGEX:
116:         result = re.fullmatch(alias_value, heading_text) is not None
117:     else:
118:         assert False, f"{cls.__name__}: unknown alias type {alias_type!r}"
119: 
120:     return result

(End of file - total 120 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 114.9s)

_Thinking:_

Key findings: `match_alias` in the REGEX case uses `re.fullmatch(alias_value, heading_text)` — match-only, no capture. In other words, a regex alias enforces the format of a heading, but does not extract a value.

So then, how does a `MarkdownSection` expose its heading text as data? In the case of `UpdateEntry` (tsk) and H1 title, the heading text itself becomes the data (the "title" computed field of the section). Let me check `MarkdownSection.from_text` and `markdown_section.py` to see how the heading text is stored — for example, whether the section exposes the raw heading text as an attribute (like `title` on H1).

The REGEX alias is match-only (`re.fullmatch`, no capture groups). Now let me see how a section exposes its own heading text as data:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_section.py</path>
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
18: """Base class for markdown sections with heading constraints."""
19: 
20: from __future__ import annotations
21: 
22: from abc import ABC
23: 
24: from markdown_it.token import Token
25: from pydantic import model_validator, computed_field, PrivateAttr
26: 
27: from .markdown_str import MarkdownStr
28: from ._markdown import format_text, parse
29: from .markdown import markdown
30: from .alias_match import match_alias
31: 
32: _HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
33: 
34: 
35: @markdown(type="heading_open")
36: class MarkdownSection(MarkdownStr, ABC):
37:     """Abstract base class for markdown sections with heading constraints."""
38: 
39:     _tokens: list[Token] = PrivateAttr(default_factory=list)
40: 
41:     @classmethod
42:     def get_extent(cls, text: str) -> int:
43:         """Return the extent of this heading section, as a line count.
44: 
45:         Overrides `MarkdownStr.get_extent` for heading-based sections. A
46:         level-N heading section's extent spans from its own `heading_open`
47:         token through every subsequent token, up to (but excluding) the
48:         next heading whose level is `<= N` -- i.e. a sibling or ancestor
49:         heading. Deeper headings (level > N, nested subsections) do not end
50:         the extent. If no such heading follows, the extent reaches the end
51:         of `text`.
52: 
53:         If `cls`'s `@markdown` metadata declares an `end_marker` (a
54:         `MarkdownStr` subclass, e.g. `MarkdownBlockQuote`), an occurrence of
55:         that class's own `type`/`tag` also stops the scan, alongside the
56:         heading-level check above -- but only when it occurs at nesting
57:         depth 0 relative to this section's own body, i.e. it is not itself
58:         nested inside some other block construct (a list item, another
59:         block quote, ...) that legitimately belongs to this section's own
60:         content. A depth counter is maintained across *every* token in the
61:         stream (incremented/decremented by that token's own `Token.nesting`,
62:         not just tokens matching the `end_marker`'s type), since any
63:         intervening open/close pair -- not only the `end_marker`'s own --
64:         shifts what "depth 0" means for everything that follows it; a token
65:         is considered "at depth 0" when the running depth *going into* it
66:         (before applying its own nesting delta) is 0, mirroring how the
67:         heading check above already treats a stopping heading's own line as
68:         outside the extent.
69: 
70:         There is only an extent at all if the *first* token parsed from
71:         `text` is a `heading_open` matching this class's own tag (from the
72:         `@markdown` decorator's metadata) *and* that heading's own text
73:         satisfies `cls`'s effective `@alias` (`match_alias`, the same check
74:         `from_text` itself makes) -- otherwise this returns `0`, same as the
75:         "no extent" case in the base class. This alias check is what lets
76:         `process_field`'s optional-field handling correctly treat a
77:         same-level-but-differently-named heading (e.g. an absent optional
78:         `Notes` immediately followed by a sibling `Assumptions` heading) as
79:         "this field is absent", instead of matching the wrong heading's
80:         extent and then failing deeper inside `from_text`'s own alias
81:         assertion.
82: 
83:         Args:
84:             text: Markdown source, pre-formatted with `mdformat`.
85: 
86:         Returns:
87:             0: `text` does not start with this class's own heading, or that
88:                 heading's text does not satisfy `cls`'s `@alias` (no extent).
89:             int > 0: line count (see `MarkdownStr.get_extent`) covered by this
90:                 heading and its nested content, stopping before the next
91:                 sibling/ancestor heading, the next depth-0 `end_marker`
92:                 occurrence (if declared), or at the end of `text`.
93:         """
94:         assert isinstance(text, str), type(text)
95:         assert text == format_text(text), "text is not in 'mdformat'."
96: 
97:         own_tag = cls._metadata.get("tag")
98:         own_type = cls._metadata.get("type")
99:         assert isinstance(own_tag, str) and own_tag in _HEADING_TAGS, (
100:             f"{cls.__name__}: expected a heading tag in {_HEADING_TAGS}, got {own_tag!r}"
101:         )
102:         own_level = _HEADING_TAGS.index(own_tag) + 1
103: 
104:         end_marker = cls._metadata.get("end_marker")
105:         end_marker_type: str | None = None
106:         end_marker_tag: str | None = None
107:         if end_marker is not None:
108:             assert isinstance(end_marker, type) and issubclass(end_marker, MarkdownStr), type(end_marker)
109:             end_marker_metadata = getattr(end_marker, "_metadata", {})
110:             end_marker_type = end_marker_metadata.get("type")
111:             end_marker_tag = end_marker_metadata.get("tag")
112: 
113:         tokens = parse(text)
114: 
115:         if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
116:             return 0
117: 
118:         if len(tokens) < 2 or not match_alias(cls, tokens[1].content.strip()):
119:             return 0
120: 
121:         result: int = 0
122:         depth: int = 0
123:         for idx, tok in enumerate(tokens):
124:             depth_at_entry = depth
125:             depth += tok.nesting
126: 
127:             m = tok.map
128:             if not m or len(m) != 2:
129:                 continue
130: 
131:             if idx > 0 and tok.type == own_type and tok.tag in _HEADING_TAGS:
132:                 if _HEADING_TAGS.index(tok.tag) + 1 <= own_level:
133:                     return m[0]
134: 
135:             if (
136:                 idx > 0
137:                 and end_marker_type is not None
138:                 and tok.type == end_marker_type
139:                 and tok.tag == end_marker_tag
140:                 and depth_at_entry == 0
141:             ):
142:                 return m[0]
143: 
144:             result = max(result, m[1])
145: 
146:         return result
147: 
148:     @classmethod
149:     def from_text(cls, text: str) -> MarkdownSection:
150:         """Create an instance from markdown text starting with this class's own heading.
151: 
152:         Validates that `text` starts with the heading triple
153:         (`heading_open`/`inline`/`heading_close`) declared by the `@markdown`
154:         decorator's metadata (`type`/`tag`), then that the heading's actual
155:         text satisfies `cls`'s effective `@alias` (`match_alias`) -- either
156:         the one explicitly declared, or, absent one, the implicit
157:         `AliasType.SPACE_SEPARATED` derivation of `cls.__name__` (see
158:         `match_alias`).
159: 
160:         If `cls` declares no nested `MarkdownStr` fields (leaf case), nothing
161:         else will ever retain this section's body text, so `_value` is set to
162:         the complete extent `from_text` received (heading and body verbatim),
163:         exactly like the base `MarkdownStr.from_text` leaf case.
164: 
165:         Otherwise the heading's own line span is stripped off `text` and the
166:         remainder ("body") is delegated to `MarkdownStr.from_text` (via
167:         `super()`) for the actual recursive field population -- each child
168:         field recursively captures its own full extent this same way, all the
169:         way down to whichever leaf(ves) ultimately hold the body text. Since
170:         the body is therefore already fully represented by the nested fields,
171:         this section's own `_value` only needs the heading's inline content
172:         (the `inline` token's text, e.g. `"Characteristic Information"`) so
173:         that `__str__` can re-emit the original heading line without
174:         duplicating what the children already carry.
175:         """
176:         assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
177:         assert text == format_text(text), "text is not in 'mdformat'."
178: 
179:         tokens = parse(text)
180:         assert len(tokens) >= 3, "Expected at least 3 tokens for heading triple"
181: 
182:         # Get the expected heading tag from decorator metadata
183:         metadata = getattr(cls, "_metadata", {})
184:         expected_type = str(metadata.get("type"))
185:         assert isinstance(expected_type, str), type(expected_type)
186:         expected_tag = str(metadata.get("tag"))
187:         assert isinstance(expected_tag, str), type(expected_tag)
188: 
189:         # Validate token structure: [heading_open, inline, heading_close]
190:         t_open = tokens[0]
191:         t_mid = tokens[1]
192:         t_close = tokens[2]
193:         assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
194:         assert t_open.tag == expected_tag, f"{cls.__name__}: expected heading {expected_tag}, got {t_open.tag}"
195:         assert t_close.nesting == -1, f"Token[2]: expected closing tag, got '{t_close.type}' '{t_close.nesting}'."
196: 
197:         heading_text = t_mid.content.strip()
198:         assert match_alias(cls, heading_text), (
199:             f"{cls.__name__}: heading text {heading_text!r} does not match its declared @alias"
200:         )
201: 
202:         field_names = cls._get_field_names()
203: 
204:         if not field_names:
205:             instance = cls()
206:             instance._value = text
207:             return instance
208: 
209:         heading_map = t_open.map
210:         assert heading_map and len(heading_map) == 2, f"{cls.__name__}: heading token has no line map"
211:         heading_lines = heading_map[1]
212: 
213:         body_lines = text.splitlines()[heading_lines:]
214:         body_text = format_text("\n".join(body_lines)) if body_lines else ""
215: 
216:         instance = super().from_text(body_text)
217:         instance._value = heading_text
218:         return instance
219: 
220:     def __str__(self) -> str:
221:         """Return markdown representation, including this section's own heading.
222: 
223:         Leaf case (no declared nested fields): `_value` already holds the
224:         complete extent verbatim (heading and body, see `from_text`), so this
225:         defers to `super().__str__()` (`MarkdownStr.__str__`'s leaf branch,
226:         which returns `_value` unchanged) exactly like any other leaf
227:         `MarkdownStr`.
228: 
229:         Composite case: `MarkdownStr.__str__` would only concatenate the
230:         rendered text of declared nested fields and silently drop this
231:         section's own heading line, since `_value` here holds only the
232:         heading's inline content (not the full extent, see `from_text`).
233:         Reconstructs the heading (`"#" * level + " " + self._value`) from
234:         `cls._metadata['tag']`, then prepends it to `super().__str__()`'s
235:         children output.
236:         """
237:         if not self._get_field_names():
238:             return super().__str__()
239: 
240:         own_tag = self._metadata.get("tag")
241:         assert isinstance(own_tag, str) and own_tag in _HEADING_TAGS, (
242:             f"{type(self).__name__}: expected a heading tag in {_HEADING_TAGS}, got {own_tag!r}"
243:         )
244:         level = _HEADING_TAGS.index(own_tag) + 1
245:         heading_line = f"{'#' * level} {self._value}"
246: 
247:         body = super().__str__()
248:         return format_text(f"{heading_line}\n\n{body}")
249: 
250:     @model_validator(mode="after")
251:     def validate_heading_structure(self) -> MarkdownSection:
252:         """Validate that section starts with a heading (h1-h6) triple.
253: 
254:         Tokens [0:3] must form a heading triple (heading_open/inline/heading_close).
255:         Token [0] must have tag h1-h6.
256:         """
257:         text = str(self)
258:         tokens = parse(text)
259:         _ = tokens
260: 
261:         # assert len(tokens) >= 3, "Expected at least 3 tokens for heading triple"
262:         # assert tokens[0].type == "heading_open", f"Token[0]: expected heading_open, got {tokens[0].type}"
263:         # assert tokens[2].type == "heading_close", f"Token[2]: expected heading_close, got {tokens[2].type}"
264:         # assert tokens[0].tag in ("h1", "h2", "h3", "h4", "h5", "h6"), (
265:         #     f"Token[0]: expected h1-h6, got {tokens[0].tag}"
266:         # )
267:         return self
268: 
269:     @computed_field  # type: ignore
270:     @property
271:     def text(self) -> str:
272:         """Computed property exposing this section's textual content.
273: 
274:         `_value` is a Pydantic private attribute (leading underscore), so it
275:         is invisible to `model_dump()`/`model_dump_json()` -- exactly the
276:         serialization path used, for example, by an MCP server transmitting a
277:         tool's return value. This property is what makes a section's content
278:         reachable through that path at all, mirroring `MarkdownParagraph.text`/
279:         `MarkdownListItem.text`'s established "expose `_value` as a public
280:         field" pattern.
281: 
282:         Leaf case (no declared nested fields, see `_get_field_names`):
283:         `_value` already holds this section's complete extent verbatim --
284:         its own heading *and* body (see `from_text`) -- so this returns
285:         `str(self)` unchanged, i.e. everything, not just the heading.
286:         Without this branch, a leaf section with no field of its own to hold
287:         its body (e.g. a bare `class Notes(MarkdownSection2): ...`) would
288:         serialize to just its heading text, silently dropping the entire
289:         body from `model_dump()`.
290: 
291:         Composite case (has declared nested fields): the body is already
292:         fully represented by those nested fields (each recursively exposing
293:         its own content the same way), so returning the whole extent here
294:         again would only duplicate it. Instead this extracts and returns
295:         just this section's own heading text, by locating the `inline` token
296:         immediately following this section's own `heading_open` (tag taken
297:         from the `@markdown` decorator's `tag` metadata) in `str(self)`'s
298:         token stream.
299: 
300:         Returns:
301:             Leaf: the complete extent verbatim (heading and body).
302:             Composite: the heading text alone, without markdown formatting,
303:             or an empty string if no matching heading is found (e.g.
304:             `_value` is unset).
305: 
306:         Example:
307:             >>> @markdown(type="notes", tag="h3")
308:             ... class Notes(MarkdownSection): ...
309:             >>> notes = Notes()
310:             >>> notes._value = "### My Notes\n\nSome content"
311:             >>> notes.text
312:             '### My Notes\n\nSome content'
313:         """
314:         if not self._get_field_names():
315:             return str(self)
316: 
317:         text = str(self)
318:         tokens = parse(text)
319: 
320:         # Get the expected heading tag from the @markdown decorator metadata
321:         metadata = getattr(self.__class__, "_metadata", {})
322:         expected_tag = metadata.get("tag")
323: 
324:         # Look for the inline token that follows a heading_open with the expected tag
325:         # Heading structure: [heading_open, inline, heading_close]
326:         for i, token in enumerate(tokens):
327:             if (
328:                 token.type == "inline"
329:                 and i > 0
330:                 and tokens[i - 1].type == "heading_open"
331:                 and tokens[i - 1].tag == expected_tag
332:             ):
333:                 return token.content.strip()
334: 
335:         return ""

(End of file - total 335 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 163.9s)

_Thinking:_

This is an important discovery. `MarkdownSection.from_text`:

- Verifies that the heading text matches `@alias` (via `match_alias` — regex uses `re.fullmatch`, matching only).
- For composite sections, sets `instance._value = heading_text` — the heading's inline content is stored in `_value`.
- The `text` computed property (composite case) returns the heading text alone.

So a `MarkdownSection3` subclass with `@alias(value=r"^Probability [1-5]$", type=AliasType.REGEX)` will:

1. **Enforce** that the heading is `Probability <n>` where n is a single digit (we can refine to `[1-5]` so out-of-range fails immediately — better than the user's `\d`, which would also accept 0/6-9… well, the user said "a regex similar to `^Proability \d$`" — we should refine to `[1-5]` so the 5x5 range is enforced at the heading level itself!).
2. **Store** the entire heading text in `_value`, and expose it via the `.text` computed field.

Therefore, the value is recoverable: parse `n` from `.text` (or via a computed `value: int` property that does `int(self.text.split()[1])`). The regex alias enforces the format, and the computed field extracts the digit. This is exactly the same pattern as the `TaskItem`/`UpdateEntry` computed fields — the engine natively supports it, no custom list item parsing needed.

So the user's idea works well and is arguably better than my list item approach:

- The heading itself is a first-class, validated structure (match_alias's `re.fullmatch`).
- Range can be enforced in the regex: `^Probability [1-5]$` — `### Probability 6` immediately fails parse.
- No dependence on the quirks of `MarkdownListItem` marker parsing (the `TaskItem` workaround existed because the parser had no GFM plugin; the H3 regex alias is a designed-in feature of the engine — feat-10's own design notes confirm `@alias(value=".+", type=AliasType.REGEX)` is a standard mechanism for H3 leaves).
- Eager validation: `from_text` asserts the alias before construction — no lazy-computed-field gap like the one feat-10 had to fix with `_validate_items_eagerly`. The regex check happens at parse time, in `from_text`/`get_extent`.

Let me check how the `MarkdownSection3` class is defined, and look at `UpdateEntry` (tsk) to confirm the exact pattern for an H3 leaf. Also, confirm how a parent section (H2 `Assessment`) declares two named H3 child fields (`probability`, `impact`) — the heading→field mapping is presumably done by matching each declared field class's alias against the heading text, in document order. Let me read tsk's body.py (UpdateEntry) and the section2/section3 base classes, and probably the field processing machinery (`process_field`/`process_list_field` in \_markdown.py or markdown_str.py).

Let me read:

- `models/md/markdown_section2.py`, `markdown_section3.py` (probably thin wrappers)
- tsk's `body.py` (RecentUpdates/UpdateEntry)
- `models/md/markdown_str.py` (from_text's field handling — how a composite section's fields are populated in order)

`_value` retains the heading text, and `match_alias` performs enforcement at parse time via `re.fullmatch`. Let's check the H3 leaf precedent (tsk's `UpdateEntry`) and how composite sections map child fields:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/body.py"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/body.py</path>
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
18: """TaskList (TSK) body models: whole-section fields under a single H1.
19: 
20: Built on the generic `models.md` `MarkdownSection1WithComment`/
21: `MarkdownSection2`/`MarkdownSection3`/`MarkdownParagraph`/`TaskItem` engine,
22: mirroring `req/models/v1/body.py`'s "one class per heading/list" shape. `Task`
23: is the top-level H1 container:
24: 
25: ```
26: # {H1 title}
27: <!-- optional leading comment -->        comment: MarkdownComment | None
28: - [ ] flat checklist item                items: list[TaskItem]  (>=1)
29: - [x] another item
30: ...
31: 
32: ## Recent Updates                        recent_updates: RecentUpdates
33: ### {free-form title}
34: {update text}
35: ### {another entry}
36: {update text}
37: ```
38: 
39: Field declaration order on `Task` enforces markdown order (title -> optional
40: comment (inherited) -> items (>=1) -> mandatory `## Recent Updates`), since
41: `models.md`'s `MarkdownStr.from_text` distributes text among declared fields
42: in that same order.
43: """
44: 
45: from pydantic import Field, model_validator
46: 
47: from ....models.md import (
48:     MarkdownParagraph,
49:     MarkdownSection1WithComment,
50:     MarkdownSection2,
51:     MarkdownSection3,
52:     alias,
53:     AliasType,
54: )
55: from .task_item import TaskItem
56: 
57: 
58: @alias(value=".+", type=AliasType.REGEX)
59: class UpdateEntry(MarkdownSection3):
60:     """`### {free-form title}` under `## Recent Updates` -- one dated/titled update entry.
61: 
62:     The H3 heading text is free-form (no fixed vocabulary/numbering, unlike
63:     ADR's `### Option N: ...` -- update entries are not numbered options).
64: 
65:     Parameters
66:     ----------
67:     content:
68:         The lead paragraph right after the H3 heading -- this entry's own
69:         update text. Mandatory.
70:     """
71: 
72:     content: MarkdownParagraph = Field(
73:         description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
74:     )
75: 
76: 
77: class RecentUpdates(MarkdownSection2):
78:     """`## Recent Updates` -- a dynamic list of free-form-titled `### ` update entries.
79: 
80:     A fixed-title (non-alias) `MarkdownSection2`, structurally similar to
81:     `AdrBody`'s `## Pros and Cons of the Options`/`AdrOption` collection, but
82:     with no dedicated per-entry tools (no `option_create`/`option_list`
83:     equivalent) -- entries are appended by editing the whole body.
84: 
85:     Parameters
86:     ----------
87:     updates:
88:         The dynamic collection of `### ` entries, in document order. Requires
89:         at least one entry (``min_length=1``), same as `Task.items` below --
90:         `models.md`'s generic list-parsing engine already enforces this
91:         during `from_text` for any non-`Optional` `list[X]` field regardless
92:         of `min_length`, so this constraint makes direct Python construction
93:         (e.g. a future `create_tsk` tool) consistent with parsing instead of
94:         silently allowing `RecentUpdates(updates=[])`. A newly created `tsk`
95:         document must therefore seed a first entry (e.g. "Created") -- see
96:         the feature README's Decisions Made.
97:     """
98: 
99:     updates: list[UpdateEntry] = Field(
100:         min_length=1,
101:         description="Dynamic collection of `### {free-form title}` entries, in document order. "
102:         "Must contain at least one entry.",
103:     )
104: 
105: 
106: @alias(value=".+", type=AliasType.REGEX)
107: class Task(MarkdownSection1WithComment):
108:     """The `tsk` body: a single H1 section with the fields below.
109: 
110:     The H1 heading text is free-form. `comment` is inherited from
111:     `MarkdownSection1WithComment` (see its own docstring) -- not redeclared
112:     here.
113: 
114:     Parameters
115:     ----------
116:     comment:
117:         Optional explanatory HTML comment (`<!-- ... -->`) preceding
118:         `items`. Inherited from `MarkdownSection1WithComment`.
119:     items:
120:         The flat checklist -- one `- [ ] .../- [x] ...` entry per line.
121:         Mandatory. At least one item.
122:     recent_updates:
123:         `## Recent Updates`. Mandatory.
124:     """
125: 
126:     items: list[TaskItem] = Field(
127:         min_length=1,
128:         description="The flat checklist -- one `- [ ] .../- [x] ...` entry per line; must contain at least one item.",
129:     )
130:     recent_updates: RecentUpdates = Field(description="`## Recent Updates` section. Mandatory.")
131: 
132:     @model_validator(mode="after")
133:     def _validate_items_eagerly(self) -> "Task":
134:         """Force every `TaskItem.checked` computed field to evaluate eagerly, not lazily.
135: 
136:         `TaskItem.checked`/`.description` are `@computed_field`s -- Pydantic
137:         only evaluates a computed field's getter on access (e.g. during
138:         `model_dump()`/serialization), never during construction/validation
139:         of the underlying model itself. Left unchecked, that would mean
140:         `Task.from_text(...)` (and therefore `create_tsk`/`update_tsk`/
141:         `validate_tsk`) could silently accept a malformed checkbox marker
142:         like `"- [z] foo"`, breaking this project's universal "successfully
143:         constructing the model *is* the validation" convention -- a caller
144:         could write a bad file to disk before the error ever surfaced, if it
145:         surfaced at all.
146: 
147:         A `model_validator` on `TaskItem` itself cannot fix this:
148:         `MarkdownListItem.from_text` constructs each item via a bare,
149:         no-argument `cls()` first and only assigns its parsed text to the
150:         private `_value` attribute *afterward* (bypassing Pydantic's own
151:         validation pipeline), so a `TaskItem`-level `model_validator` would
152:         fire on an empty, not-yet-populated instance. By the time *this*
153:         validator runs, `self.items` already holds fully-parsed `TaskItem`
154:         instances (each already went through its own `from_text` above), so
155:         accessing `.checked` here is safe and forces the check immediately.
156:         """
157:         for item in self.items:
158:             _ = item.checked
159:         return self

(End of file - total 159 lines)
</content>
````

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py",
  "limit": 120
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/markdown_str.py</path>
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
18: """Parse markdown into tokens using shared MarkdownIt instance.
19: 
20: Note: `md.parse(text, env)` accepts optional `env: dict` (EnvType) to pass data
21: between parsing rules and collect metadata like reference definitions.
22: """
23: 
24: from __future__ import annotations
25: 
26: import types
27: import typing
28: from typing import Any
29: from pydantic import BaseModel
30: from ._markdown import format_text, parse
31: 
32: 
33: def _snippet(text: str, max_lines: int = 5, max_chars: int = 300) -> str:
34:     """Return a truncated snippet of text for error messages.
35: 
36:     Args:
37:         text: the markdown text to excerpt.
38:         max_lines: maximum number of lines to include before truncating.
39:         max_chars: maximum number of characters to include before truncating.
40: 
41:     Returns:
42:         A snippet of up to `max_lines` lines and `max_chars` characters,
43:         with a "... (truncated)" suffix if either limit was exceeded.
44:     """
45:     lines = text.splitlines()
46:     truncated_lines = lines[:max_lines]
47:     snippet = "\n".join(truncated_lines)
48: 
49:     if len(lines) > max_lines or len(snippet) > max_chars:
50:         snippet = snippet[:max_chars]
51:         return f"{snippet}... (truncated)"
52:     return snippet
53: 
54: 
55: class MarkdownStr(BaseModel):
56:     """Markdown text parsed into token stream."""
57: 
58:     _value: str = ""
59: 
60:     @classmethod
61:     def get_extent(cls, text: str) -> int:
62:         """Return the extent of the markdown token stream parsed from `text`, as a line count.
63: 
64:         The result is a count, not a 0-based line index, matching Python's own
65:         slicing/`len()`/`range()` convention: `text.splitlines()[:get_extent(text)]`
66:         yields exactly the lines covered by the extent. This also keeps `0`
67:         unambiguous as "no extent" -- a single-line extent returns `1`, never
68:         colliding with the no-extent sentinel the way a 0-based last-line-index
69:         would.
70: 
71:         NOTE that `text` must already be formatted with `mdformat`.
72: 
73:         Args:
74:             text: Markdown source, pre-formatted with `mdformat`.
75: 
76:         Returns:
77:             0: no extend found.
78:             int > 0: the number of lines, from the start of `text`, covered by
79:                 the extent. Equivalent to the highest `token.map[1]` across all
80:                 tokens with a 2-element `.map` (`token.map[1]` is already the
81:                 exclusive-end line bound, so it doubles as a line count since
82:                 every extent starts at line 0).
83:         """
84: 
85:         assert isinstance(text, str), type(text)
86:         assert text == format_text(text), "text is not in 'mdformat'."
87: 
88:         tokens = parse(text)
89: 
90:         result: int = 0
91:         for tok in tokens:
92:             m = tok.map
93:             if not m or len(m) != 2:
94:                 continue
95:             result = max(result, m[1])
96: 
97:         return result
98: 
99:     @classmethod
100:     def _unwrap_optional(cls, annotation: Any) -> tuple[Any, bool]:
101:         """Return `(inner_type, is_optional)` for a field's raw annotation.
102: 
103:         Recognizes `Optional[X]` and PEP 604 `X | None` -- both of which are
104:         `typing.Union[X, None]` under the hood -- with exactly one non-`None`
105:         member, and unwraps them to `(X, True)`. Any other annotation
106:         (including plain `X`, or a `Union` with more than one non-`None`
107:         member) is returned unchanged as `(annotation, False)`.
108: 
109:         Args:
110:             annotation: a field's raw `model_fields[...].annotation`.
111: 
112:         Returns:
113:             `(inner_type, is_optional)`.
114:         """
115:         origin = typing.get_origin(annotation)
116:         if origin is typing.Union or origin is types.UnionType:
117:             args = typing.get_args(annotation)
118:             non_none = [a for a in args if a is not type(None)]
119:             if len(non_none) == 1 and type(None) in args:
120:                 return non_none[0], True

(Showing lines 1-120 of 467. Use offset=121 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 479.7s)

_Thinking:_

I've confirmed the `UpdateEntry` pattern: `@alias(value=".+", type=AliasType.REGEX)` on a `MarkdownSection3` — the heading text becomes the data (stored in `_value`, exposed via `.text`). The composite section's `from_text` distributes body text across the declared fields in order.

So the user's proposal maps cleanly onto the engine:

```python
@alias(value=r"^Probability [1-5]$", type=AliasType.REGEX)
class AssessmentProbability(MarkdownSection3):
    """### Probability {1..5} — leaf H3, value in the heading."""

    @computed_field
    @property
    def value(self) -> int: ...  # int(self.text.split()[1])
```

Hmm, wait — but there's a subtle point. `UpdateEntry` is an H3 with `content: MarkdownParagraph` (a child field holding the body text). If we use `### Probability 4` as a leaf section (no child fields), then per `from_text`'s leaf case, `_value` = the full extent (heading + body verbatim), and `.text` (leaf branch) returns `str(self)` — the entire extent verbatim, not just the heading! Let me re-read:

Leaf case in `text`'s computed property: "if no declared nested fields exist (leaf case): `_value` already holds this section's full extent verbatim — its own heading *and* body… so we return `str(self)` unchanged."

Hmm, so for a leaf H3 with no body (just the heading), `.text` returns the whole thing = just the heading line "### Probability 4"? Wait no — `str(self)` for a leaf returns `_value` = the full extent verbatim = "### Probability 4" (since there's no body). Hmm, actually, if the section has no body content, the extent is just the heading line. So `.text` = "### Probability 4" with the "### " prefix included.

Composite case: `.text` = heading inline content only (no # prefix): "Probability 4".

This distinction matters for the value-extraction computed field:

- Leaf: `text` = "### Probability 4" → extract via regex on the raw line
- Composite: `text` = "Probability 4" → `split()[1]`

Alternatively, the leaf section could just hold its own value… Let me think about what's cleanest.

Actually wait — there's another subtlety in the leaf case. `get_extent` on a leaf: `MarkdownSection.get_extent` returns the extent spanning up to the next same-or-shallower heading. For `### Probability 4` followed by `### Impact 3`, the Probability leaf's extent is just that one line. OK.

But hmm — for a leaf section, `from_text` asserts that the heading matches the alias. For `@alias(value=r"^Probability [1-5]$")`:

- `### Probability 4` → match ✓
- `### Probability 6` → AssertionError at parse time ✗ (exactly the eager enforcement the user wants)
- `### Probability` (no digit) → AssertionError ✗

And the parent H2 `Assessment(MarkdownSection2)` declares:

```python
class Assessment(MarkdownSection2):
    probability: Probability3  # ### Probability {1..5}
    impact: Impact3  # ### Impact {1..5}
```

The field names don't need to be `probability`/`impact` as section classes. And each leaf H3 gets a computed `value: int`.

Then the parent `Risk` derives `initial_level`/`residual_level` from the two computed values.

One concern: does the engine support two *different* leaf H3 sections as named fields under one H2? `RecentUpdates` used `list[UpdateEntry]` (dynamic). Here we'd have two different classes (`Probability` and `Impact`) — like `Task` having `comment` + `items` + `recent_updates` (different types under one H1). Yes, composite `from_text` "distributes text across the declared fields in the same order" — different field types in sequence is exactly how `Task` works (H1 → H2 recent_updates). So H2 → H3 probability → H3 impact works by the same mechanism.

Another consideration: what's the *body* of `### Probability 4`? Nothing — just the heading. So the section is a leaf (no child fields). Per the leaf branch of `MarkdownSection.text`: returns the full extent verbatim ("### Probability 4"). Then the `value` computed field: `int(re.fullmatch(r"### Probability (\d)", str(self)).group(1))` — hmm, or more simply: strip the "### " prefix and take the last token. Either way.

Wait, actually — I should double-check: is `MarkdownSection3` a concrete class, and does a leaf (empty-body) section round-trip correctly? `__str__`'s leaf branch returns `_value` unchanged = "### Probability 4". Round-trip stable ✓.

But wait — there's a subtlety about the extent of an empty-body leaf: `get_extent` scans tokens up to the next same-or-shallower heading. For the last H3 before `## Residual Assessment` (H2), the extent stops at the H2. ✓.

OK — so, my opinion. The user's proposal is good, and better than my list-item approach. Points:

**In favor (agree with user):**

1. It's the engine's *native* mechanism — `match_alias`'s `re.fullmatch` against the declared `@alias` REGEX. `UpdateEntry` (tsk) and ADR's `Option N:` already use regex aliases. My `- Probability: N` list-item leaf was a workaround born of the missing GFM task-list plugin. The H3 approach doesn't need any such workaround.
2. Eager enforcement at parse time: `from_text` asserts the alias before construction — `### Probability 6`, `### Probability`, `### probability 4` all fail immediately. No need for the `TaskItem`-style `_validate_items_eagerly` fix (which was a real bug that came out of the list-item approach in feat-10).
3. We can enforce the 5x5 range *inside the regex itself*: `^Probability [1-5]$` — better than the user's `\d` (which accepts 0, 6–9, and "Probability 12" fails but "Probability 0" slips through).
4. The heading text is stored in `_value`/`.text`, so the value is available for the computed `value: int` field and for `model_dump` (via computed_field) — `RskSummary` gets `probability`/`impact`/`level` cleanly.
5. Self-describing document: `### Probability 4` reads as data even without a parser.

**Caveats / refinements to flag:**

1. Use `[1-5]` instead of `\d` (range enforcement at the heading level).
2. Leaf H3 sections have no body — so the value lives *only* in the heading, and `.text` (leaf branch) returns the full line verbatim including `### `. The `value` computed field needs to parse from that (trivial regex/strip). A little awkward compared to the composite `.text` (heading only) — but fine.
3. Rendering: `__str__` re-emits the heading from `_value` — round-trips verbatim. ✓
4. One design consequence: the H2 `## Initial Assessment` section itself becomes a pure container with two child H3s (composite with fields `probability: Probability`, `impact: Impact`), and the parent derives the `level` computed field from them. Same as before, but the leaf is now a section instead of a list item.
5. Optional concern: does the "order-enforced" field distribution correctly handle two different leaf H3s? Precedent: `Task` (H1) distributes `comment` → `items` (list) → `recent_updates` (H2). Different field types in sequence work. Two H3 leaves in sequence — same mechanism. I'm confident but should note "verify in Phase 1 Task 1.2" — actually the reference-doc round-trip test (Task 1.3/1.4) will prove it.

Hmm wait, one more thing to double-check: how does the parent's `from_text` know which heading belongs to which field? "Distributes text across the declared fields in the same order" — presumably each field class's `get_extent` is tried in order at the current position. `get_extent` asserts that the first token matches the field class's tag (h3) and alias (`^Probability [1-5]$` vs `^Impact [1-5]$`) — so a `### Impact 3` in the `probability` field slot would give `get_extent`=0 (alias mismatch) → structural error, or the distribution engine handles it. Order matters: in the document, `### Probability` must come before `### Impact`. If reversed → parse failure (good, strict).

Also worth noting: since the H3 heading text is data, the regex alias pattern `^Probability [1-5]$` is the schema — the field type name is separate.

OK — the user is asking "your view?" so I give a concise opinion: agree, with two refinements ([1-5] instead of \\d; note that it's a body-less leaf and value extraction is via computed field). And update the plan (Design Notes, REQ-001, tasks, decisions, worked example) and the issue body? The issue body says "probability 1..5 and impact 1..5" — the issue doesn't specify the list-item vs H3 shape, so the issue body is still accurate. Only the README's Design Notes (body shape block, assessment structure, Task 1.2 wording, Decisions Made) need updating.

Let me draft the updated design-notes body shape:

```
  ## Initial Assessment                        initial_assessment: Assessment
  ### Probability 4                            (H3 leaf, value in heading)
  ### Impact 3

  ## Strategy                                  strategy: str  (TARA closed 4-value set)
  {transfer | accept | reduce | avoid}

  ## Mitigation                                mitigation: MarkdownStr  (mandatory)
  {Treatment measures; "none" if strategy is accept}

  ## Residual Assessment                       residual_assessment: Assessment
  ### Probability 2
  ### Impact 3
```

And the "Assessment structure" design note:

- `Assessment` (H2, `MarkdownSection2`) has two mandatory leaf H3 children: `probability: Probability` and `impact: Impact`. Each is a `MarkdownSection3` with `@alias(value=r"^Probability [1-5]$", type=AliasType.REGEX)` (respectively `^Impact [1-5]$`) — the regex alias mechanism of the engine (same `re.fullmatch` enforcement as tsk's `UpdateEntry` free-form H3 and ADR's numbered `Option N:`).
- The value lives *in* the heading: `### Probability 4`. The heading text is enforced at parse time (`from_text` asserts `match_alias` before construction — eager, no `TaskItem`-style lazy-computed-field gap). Out-of-range (`### Probability 6`), missing digit, or wrong order (`### Impact` before `### Probability`) all fail the parse.
- Each leaf exposes a computed `value: int` (parsed from the heading text); `Assessment` derives a computed `level` from the product zone.
- Why not list items: the parser (MarkdownIt commonmark, no GFM plugin) has no first-class structure for `- Probability: N` markers — that would require a custom `MarkdownListItem` leaf with lazy computed fields plus an eager-validation workaround (feat-10's `TaskItem` history). The H3 regex alias is a designed-in feature of the engine.

Worked example update:

```
## Initial Assessment
### Probability 4
### Impact 3

## Strategy
reduce

## Mitigation
Replace the parser with a maintained library; restrict uploads to a
format whitelist.

## Residual Assessment
### Probability 2
### Impact 3
```

Zone table: unchanged.

REQ-001 update: "(5x5: H3 headings `### Probability {1..5}` / `### Impact {1..5}`, value in heading, derived level)" — adjust.

Task 1.2 update: "Assessment (new MarkdownSection2: two mandatory leaf H3 children `Probability`/`Impact` with regex alias `^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced by `match_alias` at parse time; computed `value: int` per leaf; derived `level` computed field from the product zone; order enforced by field declaration)."

Task 1.4: add "out-of-range heading digit, missing digit, H3 order violation."

Task 2.6: "out-of-range probability/impact" → "out-of-range/missing heading digit."

New entry in Recent Updates + new Decisions Made entry (H3 regex-alias assessment structure, 2026-08-24, user proposal).

Also update the body-shape block in the design notes and the "Assessment structure (initial/residual)" note. Also the note "level is always computed, never written" — that stays true.

Also, the overview sentence doesn't mention the list-item detail — check: "carries a 5x5 probability/impact assessment BEFORE mitigation..." — generic, fine.

OK let me do the edits. Multiple targeted `edit` calls:

1. REQ-001: "mandatory `## Initial Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory `## Strategy` ... mandatory `## Residual Assessment` (5x5, same shape as initial)" → change the assessment description to mention H3-in-heading values.

2. Design note body-shape block:

```
  ## Initial Assessment                        initial_assessment: Assessment
  - Probability: {1..5}
  - Impact: {1..5}
```

→

```
  ## Initial Assessment                        initial_assessment: Assessment
  ### Probability {1..5}                       probability: Probability (H3 leaf)
  ### Impact {1..5}                            impact: Impact (H3 leaf)
```

And the residual block similarly.

3. "Assessment structure (initial/residual)" note — rewrite the opening paragraph + example + add the "why H3 not list items" rationale.

4. Task 1.2 — rewrite the Assessment description.

5. Task 1.4 — add cases.

6. Task 2.6 — adjust wording.

7. Recent Updates — new entry at top.

8. Decisions Made — new entry.

Let me get the current exact text of the relevant sections in the file so my oldStrings match. I have the file contents from when I wrote them, so I can use those directly.

Current text of the assessment structure note (from my write):

```
- **Assessment structure (initial/residual)** — each assessment is one cell
  of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;
  1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...
  5 = severe), written as exactly two list items under the H2 heading:

```

## Initial Assessment

- Probability: 4
- Impact: 3

```

The model derives the zone `level` from the product of the two
coordinates (probability x impact):
```

And the example:

```
  ## Initial Assessment
  - Probability: 4
  - Impact: 3

  ## Strategy
  reduce

  ## Mitigation
  Replace the parser with a maintained library; restrict uploads to a
  format whitelist.

  ## Residual Assessment
  - Probability: 2
  - Impact: 3
```

And the closing:

```
  Initial cell 4 x 3 = 12 -> `high`; residual cell 2 x 3 = 6 -> `medium`:
  the mitigation moved the risk one zone down. That before/after pair is the
  register's audit trail — a sensible `reduce` strategy must show
  residual < initial (the example's annotations are for readability only;
  the document stores the two list items, and `level` is always computed,
  never written).
```

OK, let me make the edits. I'll do them in a batch of edit calls (all against the same file, sequential — each edit depends on the previous file state, but the oldStrings are disjoint from each other so they can be issued in parallel. The tool processes them in order. Disjoint regions, so parallel is fine).

Actually, for safety against overlapping matches, all my oldStrings are unique and disjoint. Let me batch them.

Edit 1 — REQ-001:
old: "mandatory `## Scope` list (>=1 affected system/component), mandatory `## Initial\n  Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory `## Strategy` (TARA 4-value closed set: `transfer`/`accept`/`reduce`/\\n `avoid`), mandatory `## Mitigation`, mandatory `## Residual Assessment`\\n (5x5, same shape as initial)"
new: "mandatory `## Scope` list (>=1 affected system/component), mandatory `## Initial\n  Assessment` (5x5: H3 headings `### Probability {1..5}` / `### Impact {1..5}`,\\n value in the heading, derived level), mandatory `## Strategy` (TARA 4-value\\n closed set: `transfer`/`accept`/`reduce`/`avoid`), mandatory `## Mitigation`,\\n mandatory `## Residual Assessment` (5x5, same shape as initial)"

Hmm, let me be careful to match the exact text I wrote. From the write:

```
  `## Scope` list (>=1 affected system/component), mandatory `## Initial
  Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory
  `## Strategy` (TARA 4-value closed set: `transfer`/`accept`/`reduce`/
  `avoid`), mandatory `## Mitigation`, mandatory `## Residual Assessment`
  (5x5, same shape as initial), optional `## Owner`, optional `## Tags`
```

Edit 1 oldString:
"mandatory `## Initial\n  Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory"
newString:
"mandatory `## Initial\n  Assessment` (5x5: H3 headings `### Probability {1..5}` / `###\n  Impact {1..5}`, value in the heading, derived level), mandatory"

Edit 2 — body-shape initial block:
old:
" ## Initial Assessment initial_assessment: Assessment

- Probability: {1..5}
- Impact: {1..5}"
  new:
  " ## Initial Assessment initial_assessment: Assessment

### Probability {1..5} probability: leaf H3 (value in heading)

### Impact {1..5} impact: leaf H3 (value in heading)"

Edit 3 — body-shape residual block:
old:
" ## Residual Assessment residual_assessment: Assessment

- Probability: {1..5}
- Impact: {1..5}"
  new:
  " ## Residual Assessment residual_assessment: Assessment

### Probability {1..5} probability: leaf H3 (value in heading)

### Impact {1..5} impact: leaf H3 (value in heading)"

Edit 4 — assessment structure note opening:
old:
"- **Assessment structure (initial/residual)** — each assessment is one cell
of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;
1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...
5 = severe), written as exactly two list items under the H2 heading:

```
## Initial Assessment
- Probability: 4
- Impact: 3
```

The model derives the zone `level` from the product of the two
coordinates (probability x impact):"
new:
"- **Assessment structure (initial/residual)** — each assessment is one cell
of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;
1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...
5 = severe), carried by exactly two leaf H3 sections under the H2
heading, with the value *in the heading itself*:

```
## Initial Assessment
### Probability 4
### Impact 3
```

Each H3 is a `MarkdownSection3` leaf with a regex `@alias` —
`^Probability [1-5]$` / `^Impact [1-5]$` — enforced by `match_alias`
(`re.fullmatch`) at parse time, the engine's own first-class heading-
constraint mechanism (same family as `tsk`'s free-form `### `
`UpdateEntry` and ADR's numbered `### Option N:` headings). The range is
baked into the regex itself: `### Probability 6`, `### Probability`
(missing value), or `### Impact` before `### Probability` (wrong order)
all fail the parse eagerly — no `TaskItem`-style lazy-computed-field gap
and no custom list-item marker parsing (the parser is MarkdownIt
commonmark without a GFM plugin, which is exactly why `tsk` needed a
`TaskItem` workaround for checkboxes — not needed here). Each leaf
exposes the heading's digit as a computed `value: int`; the H2 `Assessment`
derives the zone `level` from the product of the two values
(probability x impact):"

Edit 5 — worked example assessment lines:
old:
" ## Initial Assessment

- Probability: 4
- Impact: 3

## Strategy

reduce"
new:
" ## Initial Assessment

### Probability 4

### Impact 3

## Strategy

reduce"

Edit 6 — worked example residual lines:
old:
" ## Residual Assessment

- Probability: 2
- Impact: 3

````"
new:
"  ## Residual Assessment
### Probability 2
### Impact 3
```"

Edit 7 — worked example closing:
old:
"  Initial cell 4 x 3 = 12 -> `high`; residual cell 2 x 3 = 6 -> `medium`:
the mitigation moved the risk one zone down. That before/after pair is the
register's audit trail — a sensible `reduce` strategy must show
residual < initial (the example's annotations are for readability only;
the document stores the two list items, and `level` is always computed,
never written)."
new:
"  Initial cell 4 x 3 = 12 -> `high`; residual cell 2 x 3 = 6 -> `medium`:
the mitigation moved the risk one zone down. That before/after pair is the
register's audit trail — a sensible `reduce` strategy must show
residual < initial (the example's annotations are for readability only;
the document stores the two H3 heading values, and `level` is always
computed, never written)."

Edit 8 — Task 1.2:
old:
"  `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/
`mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;
`Assessment` (new `MarkdownSection2` leaf: `probability`/`impact` int 1..5
parsed from `- Probability: N`/`- Impact: N` list items via a
`MarkdownListItem` subclass with computed fields, derived `level` computed
field from the product zones, parent-level eager-validation
`model_validator` on the `Risk` H1 per the `TaskItem` precedent) —
depends on: Task 1.1 — status: not-started"
new:
"  `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/
`mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;
`Assessment` (new `MarkdownSection2`: two mandatory leaf-H3 children
`Probability`/`Impact`, each a `MarkdownSection3` with regex `@alias`
`^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced
eagerly by `match_alias` at parse time; computed `value: int` per leaf,
derived `level` computed field on `Assessment` from the product zones) —
depends on: Task 1.1 — status: not-started"

Edit 9 — Task 1.4:
old:
"  mirroring `tests/tsk/models/v1/`: status set, 5x5 bounds and derived-
level zones (all four zone boundaries: 4/5, 9/10, 14/15), TARA closed
set, `Scope` >=1, `Tags`/`Owner`/`More Information` absent-vs-present —"
new:
"  mirroring `tests/tsk/models/v1/`: status set, 5x5 heading-value bounds
(`### Probability 0`/`6` rejected, zone boundaries 4/5, 9/10, 14/15),
missing-heading-value and wrong H3-order rejection, TARA closed set,
`Scope` >=1, `Tags`/`Owner`/`More Information` absent-vs-present —"

Edit 10 — Task 2.6:
old:
"  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,
defaults-when-absent, invalid status, malformed structure, out-of-range
probability/impact, invalid TARA word, missing Scope entry) — depends on:"
new:
"  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,
defaults-when-absent, invalid status, malformed structure, out-of-range
or missing assessment heading value, invalid TARA word, missing Scope
entry) — depends on:"

Edit 11 — Recent Updates new entry (insert above the 11:55 entry… no wait, this will be even newer, so at the very top):
old:
"### Recent Updates

#### 2026-08-24T11:55:11+02:00 (newest)"
new:
"### Recent Updates

#### 2026-08-24T{now} (newest)

- Completed: revised the `Assessment` structure per user proposal —
probability/impact are no longer list items (`- Probability: N`) under
the H2 but leaf H3 sections with the value in the heading
(`### Probability 4` / `### Impact 3`), each a `MarkdownSection3` with a
regex `@alias` (`^Probability [1-5]$` / `^Impact [1-5]$`) enforced by
`match_alias` (`re.fullmatch`) at parse time. Rationale: the regex alias
is the engine's first-class heading-constraint mechanism (same family as
`tsk`'s `UpdateEntry`), enforces the heading *and* the digit *and* the
1..5 range eagerly at parse time — replacing the planned `TaskItem`-style
custom list-item leaf (which needed a lazy-computed-field workaround and
depends on a parser that has no GFM list-marker structure)
- Next: user review; then Phase 1 (Specification)
- Notes: see the new Decisions Made entry below

#### 2026-08-24T11:55:11+02:00"

Edit 12 — Decisions Made new entry (after the superseded TARRA/Description entry? Order: append to end, or near related entries. I'll insert after the "superseded" entry, before the TARA entry… actually the simplest: append after the scope entry at the end. Hmm, the decisions list is roughly chronological. New entry is the same day, so append at the end:

old (end of file):
"- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected
system/component); `## Owner`, `## Tags`, `## More Information` are
optional — rationale: scope answers "which system is affected" and is
central to a risk (user requirement); the remaining three follow ADR's
optional `more_information` precedent and keep the schema lean."
new: same + append:

"- **2026-08-24**: `Assessment`'s probability/impact are leaf H3 sections
with the value in the heading (`### Probability {1..5}`, `### Impact
{1..5}`), each constrained by a regex `@alias` (`^Probability [1-5]$` /
`^Impact [1-5]$`) and enforced eagerly by `match_alias` at parse time —
rationale: user proposal; this is the `models/md` engine's first-class
heading-constraint mechanism (same family as `tsk`'s free-form-`### `
`UpdateEntry` and ADR's numbered `Option N:` headings), it validates the
heading word, the digit, and the 1..5 range in one check at parse time,
and it replaces the originally planned `- Probability: N` list-item leaf
(a `TaskItem`-style workaround for the parser's missing GFM list-marker
support, with its own lazy-computed-field eager-validation history)
(supersedes the assessment-shape detail in the earlier
before/after-mitigation decision, which stands otherwise)."

Also, I should update the "(newest)" marker on the 11:55 entry — in my new top entry I dropped the "(newest)" from the 11:55 header, but the 11:55 entry still says "(newest)". Let me check what I wrote: "#### 2026-08-24T11:55:11+02:00 (newest)" — after inserting the new entry above, I need to change that header to drop "(newest)". My Edit 11 oldString ends with "#### 2026-08-24T11:55:11+02:00" and the newString also ends with that (without "(newest)"), so the old "(newest)" suffix is… wait, my oldString is "#### 2026-08-24T11:55:11+02:00 (newest)" and the newString ends with "#### 2026-08-24T11:55:11+02:00" — that removes the "(newest)". Good.

Wait, let me re-check Edit 11: my oldString is:
"### Recent Updates

#### 2026-08-24T11:55:11+02:00 (newest)"

newString:
"### Recent Updates

#### 2026-08-24T{ts} (newest)

- Completed: ...
- Next: user review; then Phase 1 (Specification)
- Notes: see the new Decisions Made entry below

#### 2026-08-24T11:55:11+02:00"

Yes, that works.

I need a new timestamp. Let me get the time. Also — should I update GitHub issue #15? The issue body says "probability 1..5 and impact 1..5 (derived level...)" — no mention of the list-item shape, so it's still accurate. No issue change needed.

One more thing: the Design Notes "Assessment structure" note previously said "written as exactly two list items under the H2 heading" — that's replaced by Edit 4. And the "5x5 matrix" bullet in the earlier version… no, that was replaced in the previous rewrite. Let me also check the "order is enforced by the model" paragraph — no list-item mention. OK.

Let me get the timestamp and then run all the edits.




This is a native mechanism of the engine, and it's actually better than my list item plan. Here's what I confirmed in the code:

- `match_alias` enforces REGEX aliases via `re.fullmatch` **at parse time** (`markdown_section.py:198` — `from_text` asserts the alias before construction). So `### Probability 6` or `### Probability` will fail immediately — no lazy-computed-field gap, and no `TaskItem`-style eager-validation workaround is needed (that feat-10 had a real bug with).
- The heading text is preserved (`_value`/`.text`), so the digits are available as a computed `value: int` and in `model_dump` for `RskSummary`.
- Same mechanism family that `tsk`'s `UpdateEntry` (`.+` H3) and ADR's numbered `### Option N:` headings already use.
- Two improvements: use `[1-5]` instead of `\d` (bake the 5x5 range into the regex — `\d` accepts `0`/`6`–`9`), and the leaf H3 has no body (the value exists *only* in the heading), so extraction is done via a computed field on the heading text.

Updating the plan accordingly:



**Tool: bash**

**Input:**
```json
{
"command": "date +%Y-%m-%dT%H:%M:%S%:z"
}
````

**Output:**

```
2026-08-24T13:07:31+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 176.6s)

_Thinking:_

Okay, so I'll batch all the edits. They're all in separate regions, so they can be executed in parallel.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  `## Scope` list (>=1 affected system/component), mandatory `## Initial\n  Assessment` (5x5: probability 1..5, impact 1..5, derived level), mandatory\n  `## Strategy` (TARA 4-value closed set: `transfer`/`accept`/`reduce`/",
  "newString": "  `## Scope` list (>=1 affected system/component), mandatory `## Initial\n  Assessment` (5x5: H3 headings `### Probability {1..5}` / `### Impact\n  {1..5}`, value in the heading, derived level), mandatory `## Strategy`\n  (TARA 4-value closed set: `transfer`/`accept`/`reduce`/"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  ## Initial Assessment                        initial_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Strategy                                  strategy: str  (TARA closed 4-value set)",
  "newString": "  ## Initial Assessment                        initial_assessment: Assessment\n  ### Probability {1..5}                       probability: leaf H3 (value in heading)\n  ### Impact {1..5}                            impact: leaf H3 (value in heading)\n\n  ## Strategy                                  strategy: str  (TARA closed 4-value set)"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  ## Residual Assessment                       residual_assessment: Assessment\n  - Probability: {1..5}\n  - Impact: {1..5}\n\n  ## Owner                                     owner: MarkdownStr | None",
  "newString": "  ## Residual Assessment                       residual_assessment: Assessment\n  ### Probability {1..5}                       probability: leaf H3 (value in heading)\n  ### Impact {1..5}                            impact: leaf H3 (value in heading)\n\n  ## Owner                                     owner: MarkdownStr | None"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

````json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- **Assessment structure (initial/residual)** — each assessment is one cell\n  of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;\n  1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...\n  5 = severe), written as exactly two list items under the H2 heading:\n\n  ```\n  ## Initial Assessment\n  - Probability: 4\n  - Impact: 3\n  ```\n\n  The model derives the zone `level` from the product of the two\n  coordinates (probability x impact):",
  "newString": "- **Assessment structure (initial/residual)** — each assessment is one cell\n  of a 5x5 risk matrix: two integer coordinates, `probability` (1..5;\n  1 = rare ... 5 = almost certain) and `impact` (1..5; 1 = negligible ...\n  5 = severe), carried by exactly two leaf H3 sections under the H2\n  heading, with the value *in the heading itself*:\n\n  ```\n  ## Initial Assessment\n  ### Probability 4\n  ### Impact 3\n  ```\n\n  Each H3 is a `MarkdownSection3` leaf with a regex `@alias` —\n  `^Probability [1-5]$` / `^Impact [1-5]$` — enforced by `match_alias`\n  (`re.fullmatch`) at parse time: the engine's first-class\n  heading-constraint mechanism (same family as `tsk`'s free-form `### `\n  `UpdateEntry` and ADR's numbered `### Option N:` headings). The range is\n  baked into the regex itself, so `### Probability 6`, `### Probability`\n  (missing value), and `### Impact` before `### Probability` (wrong order)\n  all fail the parse eagerly — no `TaskItem`-style lazy-computed-field gap\n  and no custom list-item marker parsing (the parser is MarkdownIt\n  commonmark without a GFM plugin, which is exactly why `tsk` needed its\n  `TaskItem` workaround for checkboxes — not needed here). The heading\n  text is retained by the engine (`_value`/`.text`), so each leaf exposes\n  the digit as a computed `value: int`; the H2 `Assessment` derives the\n  zone `level` from the product of the two values (probability x impact):"
}
````

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  ## Initial Assessment\n  - Probability: 4\n  - Impact: 3\n\n  ## Strategy\n  reduce",
  "newString": "  ## Initial Assessment\n  ### Probability 4\n  ### Impact 3\n\n  ## Strategy\n  reduce"
}
```

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

````json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  ## Residual Assessment\n  - Probability: 2\n  - Impact: 3\n  ```",
  "newString": "  ## Residual Assessment\n  ### Probability 2\n  ### Impact 3\n  ```"
}
````

**Output:**

```
Edit applied successfully.
```

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  residual < initial (the example's annotations are for readability only;\n  the document stores the two list items, and `level` is always computed,\n  never written).",
  "newString": "  residual < initial (the example's annotations are for readability only;\n  the document stores the two H3 heading values, and `level` is always\n  computed, never written)."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 185.6s)

_Thinking:_

Next, I'll do edits to the task list, recent updates, and decisions made.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  `mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;\n  `Assessment` (new `MarkdownSection2` leaf: `probability`/`impact` int 1..5\n  parsed from `- Probability: N`/`- Impact: N` list items via a\n  `MarkdownListItem` subclass with computed fields, derived `level` computed\n  field from the product zones, parent-level eager-validation\n  `model_validator` on the `Risk` H1 per the `TaskItem` precedent) —\n  depends on: Task 1.1 — status: not-started",
  "newString": "  `mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`;\n  `Assessment` (new `MarkdownSection2`: two mandatory leaf-H3 children\n  `Probability`/`Impact`, each a `MarkdownSection3` with regex `@alias`\n  `^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced\n  eagerly by `match_alias` at parse time; computed `value: int` per leaf;\n  derived `level` computed field on `Assessment` from the product zones) —\n  depends on: Task 1.1 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  mirroring `tests/tsk/models/v1/`: status set, 5x5 bounds and derived-\n  level zones (all four zone boundaries: 4/5, 9/10, 14/15), TARA closed\n  set, `Scope` >=1, `Tags`/`Owner`/`More Information` absent-vs-present —",
  "newString": "  mirroring `tests/tsk/models/v1/`: status set, 5x5 heading-value bounds\n  (`### Probability 0`/`6` rejected) and derived-level zones (all four zone\n  boundaries: 4/5, 9/10, 14/15), missing heading value and wrong H3-order\n  rejection, TARA closed set, `Scope` >=1, `Tags`/`Owner`/`More\n  Information` absent-vs-present —"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,\n  defaults-when-absent, invalid status, malformed structure, out-of-range\n  probability/impact, invalid TARA word, missing Scope entry) — depends on:\n  Task 2.2, Task 2.5 — status: not-started",
  "newString": "  `TestParseTsk`'s case shape (minimal doc, full reference-doc round-trip,\n  defaults-when-absent, invalid status, malformed structure, out-of-range\n  or missing assessment heading value, invalid TARA word, missing Scope\n  entry) — depends on: Task 2.2, Task 2.5 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "### Recent Updates\n\n#### 2026-08-24T11:55:11+02:00 (newest)",
  "newString": "### Recent Updates\n\n#### 2026-08-24T13:07:31+02:00 (newest)\n\n- Completed: revised the `Assessment` structure per user proposal —\n  probability/impact are no longer list items (`- Probability: N`) under\n  the H2 but leaf H3 sections with the value in the heading\n  (`### Probability 4` / `### Impact 3`), each a `MarkdownSection3` with a\n  regex `@alias` (`^Probability [1-5]$` / `^Impact [1-5]$`) enforced by\n  `match_alias` (`re.fullmatch`) at parse time. Rationale: the regex alias\n  is the engine's first-class heading-constraint mechanism (same family as\n  `tsk`'s `UpdateEntry`), enforces the heading word, the digit, and the\n  1..5 range eagerly at parse time — replacing the planned `TaskItem`-style\n  custom list-item leaf (a workaround for the parser's missing GFM\n  list-marker support, with its own lazy-computed-field eager-validation\n  history); confirmed against the engine source before adopting\n- Next: user review; then Phase 1 (Specification)\n- Notes: see the new Decisions Made entry below\n\n#### 2026-08-24T11:55:11+02:00"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected\n  system/component); `## Owner`, `## Tags`, `## More Information` are\n  optional — rationale: scope answers \"which system is affected\" and is\n  central to a risk (user requirement); the remaining three follow ADR's\n  optional `more_information` precedent and keep the schema lean.",
  "newString": "- **2026-08-24**: `## Scope` is mandatory with >=1 list entry (affected\n  system/component); `## Owner`, `## Tags`, `## More Information` are\n  optional — rationale: scope answers \"which system is affected\" and is\n  central to a risk (user requirement); the remaining three follow ADR's\n  optional `more_information` precedent and keep the schema lean.\n- **2026-08-24**: `Assessment`'s probability/impact are leaf H3 sections\n  with the value in the heading (`### Probability {1..5}`, `### Impact\n  {1..5}`), each constrained by a regex `@alias` (`^Probability [1-5]$` /\n  `^Impact [1-5]$`) and enforced eagerly by `match_alias` (`re.fullmatch`)\n  at parse time — rationale: user proposal; this is the `models/md`\n  engine's first-class heading-constraint mechanism (same family as `tsk`'s\n  free-form-`### ` `UpdateEntry` and ADR's numbered `Option N:` headings),\n  it validates the heading word, the digit, and the 1..5 range in one check\n  at parse time, and it replaces the originally planned\n  `- Probability: N` list-item leaf — a `TaskItem`-style workaround for\n  the parser's missing GFM list-marker support, with its own\n  lazy-computed-field eager-validation history (supersedes the\n  assessment-shape detail of the earlier before/after-mitigation decision,\n  which stands otherwise)."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 138.6s)

_Thinking:_

All edits have been applied. Let's verify consistency — grep for any remaining references to "- Probability:" list items and check the sections of the updated file.

Verifying no stale list-item references remain:

**Tool: grep**

**Input:**

```json
{
  "include": "README.md",
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk",
  "pattern": "- Probability:|list-item|list items"
}
```

**Output:**

```
Found 6 matches
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md:
  Line 123:   `TaskItem` custom-list-item-leaf precedent (parsing a non-standard marker

  Line 203:   and no custom list-item marker parsing (the parser is MarkdownIt

  Line 466:   probability/impact are no longer list items (`- Probability: N`) under

  Line 474:   custom list-item leaf (a workaround for the parser's missing GFM

  Line 508: - Notes: `Assessment` parsing reuses `tsk.TaskItem`'s custom-list-item-leaf +

  Line 567:   `- Probability: N` list-item leaf — a `TaskItem`-style workaround for

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 187.0s)

_Thinking:_

Line 508 is an old note in the first "Recent Updates" entry (the one at 11:31): "Note: `Assessment` parsing reuses the custom list item leaf + eager verification precedent of `tsk.TaskItem`; no new ADR is planned" — this is a past entry describing what the original draft assumed. It's historically accurate as of 11:31 (at that point in time it really was TaskItem-based), and the new entry explains the change. Hmm, but it could be confusing: past entries describe the state at the time, and the 13:07 entry supersedes it. I think this is fine — the log is chronological, and the supersession is documented. Actually, let me reconsider: the feat-10 convention is that entries describe "what happened at that point in time," and later entries supersede earlier assumptions. This is consistent.

Line 123 (Dependencies): "and `tsk`'s `TaskItem` custom list item leaf precedent (parsing non-standard markers into computed fields with parent-level eager verification)" — this is in the Dependencies section, describing what `rsk` depends on. Since we're no longer using the TaskItem precedent, this dependency should be updated. The dependencies now include the regex `@alias` mechanism (the `AliasType.REGEX` / `match_alias` precedent from `UpdateEntry`). Let's fix this line.

Lines 203, 466, 474, 567 are all new intentional mentions (explaining why we don't use list items). No problem.

Fix for line 123:
Old:
" `list[MarkdownStr]` engine (`process_list_field`), and `tsk`'s
`TaskItem` custom list item leaf precedent (parsing non-standard markers
into computed fields with parent-level eager verification)"
New:
" `list[MarkdownStr]` engine (`process_list_field`), the engine's regex
`@alias` heading constraint mechanism (`AliasType.REGEX` + `match_alias`
`re.fullmatch`; precedents: `tsk`'s free-form `### ` `UpdateEntry`, ADR's
numbered `### Option N:` heading), and `tsk`'s computed field convention"

Hmm, let me get the exact current text around line 123. From the original write:

```
- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (id-based reads as a tool, not a resource), `general/tools/_doc_paths.py`
  and `_packaged_data.py`, the existing `models/md` engine — in particular
  `MarkdownSection1WithComment`, `MarkdownSection2`, the generic
  `list[MarkdownStr]` engine (`process_list_field`), and `tsk`'s
  `TaskItem` custom list item leaf precedent (parsing non-standard markers
  into computed fields with parent-level eager verification)
- Blocks: none identified yet
```

New:

```
- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (id-based reads as a tool, not a resource), `general/tools/_doc_paths.py`
  and `_packaged_data.py`, the existing `models/md` engine — in particular
  `MarkdownSection1WithComment`, `MarkdownSection2`, `MarkdownSection3`,
  the generic `list[MarkdownStr]` engine (`process_list_field`), and the
  regex `@alias` heading constraint mechanism (`AliasType.REGEX` +
  `match_alias`'s `re.fullmatch`; precedents: `tsk`'s free-form `### `
  `UpdateEntry`, ADR's numbered `### Option N:` heading)
- Blocks: none identified yet
```

This is the only fix needed.

Line 508 is fine (it's a historical log entry describing the initial draft, and has already been replaced by the new 13:07 entry). However, the Dependencies section still lists the `TaskItem` precedent as a dependency — let me fix that:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  `MarkdownSection1WithComment`, `MarkdownSection2`, the generic\n  `list[MarkdownStr]` engine (`process_list_field`), and `tsk`'s\n  `TaskItem` custom-list-item-leaf precedent (parsing a non-standard marker\n  into computed fields with parent-level eager validation)\n- Blocks: None identified yet",
  "newString": "  `MarkdownSection1WithComment`, `MarkdownSection2`, `MarkdownSection3`,\n  the generic `list[MarkdownStr]` engine (`process_list_field`), and the\n  regex `@alias` heading-constraint mechanism (`AliasType.REGEX` +\n  `match_alias`'s `re.fullmatch`; precedents: `tsk`'s free-form `### `\n  `UpdateEntry`, ADR's numbered `### Option N:` headings)\n- Blocks: None identified yet"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 166.1s)

_Thinking:_

The plan has been fully updated. My opinion to the user — concise:

1. Agree — this is the engine's first-class mechanism, and it's strictly better than the list item approach I had planned.
2. Verified against the source: match_alias's re.fullmatch is enforced at parse time (before construction), the heading text is preserved in \_value/.text, and the computed value: int works.
3. Two improvements I incorporated: the regex is `^Probability [1-5]$` (not `\d` — it bakes in the range), and a note about bodyless leaf H3s (value extraction from the heading).
4. Updated the plan: REQ-001, Design Notes (body shape + structure of the Assessment with examples), dependencies, tasks 1.2/1.4/2.6, new Recent Updates + Decisions Made entries. No changes to the Issue body (it doesn't specify the representation format).

Keep it short.

Agreed — it's strictly better than the list-item approach I planned. Verified against the engine source:

- `match_alias` enforces REGEX aliases with `re.fullmatch` **at parse time, before construction** (`markdown_section.py:198`) — so the heading word, the digit, and the range are all checked eagerly. No `TaskItem`-style lazy-computed-field workaround needed (that was feat-10's real bug with list markers).
- The heading text is retained (`_value`/`.text`), so each leaf exposes a computed `value: int` that flows into `model_dump` and `RskSummary`.
- It's the same mechanism family as `tsk`'s free-form `### ` `UpdateEntry` and ADR's numbered `### Option N:` headings — first-class, not a workaround.

Two refinements folded into the plan:

1. **Regex `[1-5]`, not `\d`** — `^Probability [1-5]$` bakes the 5x5 range into the heading constraint (`### Probability 6` / `### Probability 0` fail at parse; your `\d` would accept 0 and 6–9).
2. **Leaf H3s have no body** — the value lives *only* in the heading, so extraction is a computed field on the heading text (the engine's leaf branch returns the full line verbatim).

Plan updated: REQ-001, Design Notes (body shape + the worked example now shows `### Probability 4` / `### Impact 3`, initial 4×3=12 `high` → residual 2×3=6 `medium`), Dependencies (regex-`@alias` mechanism replaces the `TaskItem` precedent), Tasks 1.2/1.4/2.6 (new rejection cases: out-of-range digit, missing digit, wrong H3 order), plus new Decisions Made + Recent Updates entries. Issue #15's body needed no change (it doesn't specify the representation).

______________________________________________________________________

## User

I intend to implement this via the ORchestrator/Phase-Implementer pattern. That means, that at the end of each phase the Phase-Implementer does a full test, and the after every phase the Orchestrator verifies the results, but does not change anything. Do we have the same setup here?

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 283.8s)

_Thinking:_

The user is asking about the Orchestrator/Phase-Implementer pattern. They're saying they intend to implement it using this pattern, and the points are as follows:

1. At the end of each phase, the Phase-Implementer runs full tests
2. After every phase, the Orchestrator validates the results but makes no changes

And the question is "Is the same setup available here?"

This is a question about the available agent types. Let me check the task tool description:

- `phase-implementer`: "Implement one phase of the `.specmgr/feat/<id>/README.md` plan from start to finish — code, tests, phase-end quality gates, and updating the Progress section of the plan — and then stop and report. Driven by `phase-orchestrator`. Not intended for direct selection."

In other words, the `phase-implementer` agent does exist. It says "driven by `phase-orchestrator`", but `phase-orchestrator` is **not** listed among the available agent types. The list of available agent types is as follows:

- architect-designer
- ccm
- explore
- general
- implementation-specialist
- python-reviewer
- requirements-clarifier
- phase-implementer
- ste100
- test-automation-engineer

So `phase-implementer` exists, but `phase-orchestrator` does not. Therefore the answer is: partially — the Phase-Implementer half exists as a dedicated agent type (`phase-implementer`). This is exactly as described: implements one phase of the `.specmgr/feat/<id>/README.md` plan end-to-end (code, tests, phase-end quality gates, updating the Progress section of the plan) and then stops and reports. The Orchestrator role is filled by me (the main session) — I drive phase-implementer via the task tool and validate the results myself (running quality gates, reviewing diffs, not making changes per the user's instruction — well, the orchestrator validates. The user is saying the orchestrator "makes no changes").

Let me carefully check the phase-implementer description once more: "Implement one phase of the `.specmgr/feat/<id>/README.md` plan from start to finish — code, tests, phase-end quality gates, and updating the Progress section of the plan — and then stop and report. Driven by `phase-orchestrator`. Not intended for direct selection."

Interesting point: it's "not intended for direct selection" — meaning it's assumed to be driven by an orchestrator. The orchestrator can be any agent, or the main session itself. Since `phase-orchestrator` is not in my available agent list, the orchestrator role is played by me (the main opencode session).

Also, a note about my task tool usage policy: "Once work has been delegated to an agent, do not duplicate that work yourself." And the phase-implementer performs quality gates at the end of the phase (full tests), and I (the orchestrator) validate the results after each phase without making changes — this is exactly the pattern the user described.

So the answer is:

- Yes, almost: `phase-implementer` exists as a dedicated subagent type, and it does exactly this: one phase of the `.specmgr/feat/<id>/README.md` plan end-to-end (code + tests + phase-end quality gates + Progress section update), then stop and report.
- The `phase-orchestrator` agent type does not exist in this environment — the orchestrator role falls to me (the main session): I dispatch phase by phase, and after each report I run/confirm the quality gates (ruff format/check, vulture, full unittest, drift check) and validate without making changes. If anything fails, I report back and have the phase-implementer fix it (rather than fixing it myself), preserving the "orchestrator doesn't change anything" rule.

Wait — the user says "the Orchestrator validates the results but makes no changes." If validation fails, the orchestrator shouldn't fix it — it should re-dispatch to the phase-implementer. I should make this division of labor explicit.

Also worth noting: the "Execution approach" section of the feat-10 plan says each phase was delegated to `implementation-specialist`. The current feat-15 plan also states "delegated to the `implementation-specialist` subagent" in the Execution approach paragraph! So to align with the user's intent, I should update the plan's Execution approach to state that phases are driven by `phase-implementer` under orchestrator validation. This is a change the user implicitly wants ("Is the same setup available here?" — they intend to implement with this pattern, and the plan currently names implementation-specialist).

Let me re-read the current plan's Execution approach:

"**Execution approach** (to confirm at Phase 1 start. See Decisions Made): each phase below is delegated to the `implementation-specialist` subagent as one unit (implementation and its own mirror tests together, not a separate test phase later), reviewed and quality-gated (ruff format/check, vulture, full `unittest` suite) by the orchestrator, and then committed as one Conventional Commit per phase — the 4-phase/4-commit form of `feat-10` (tsk)."

I should update this to name the phase-implementer/orchestrator pattern. Plus a Decisions Made entry, and a Recent Updates entry.

So my reply is:

1. Direct answer: Yes — with one caveat. `phase-implementer` exists (built for exactly this: one phase of `.specmgr/feat/<id>/README.md` end-to-end, with phase-end quality gates, updating Progress, stopping and reporting). There is no separate `phase-orchestrator` agent type in this environment, so I (the main session) act as orchestrator: I dispatch each phase, validate the results (running the quality gates, reviewing) without making changes, and on failure I re-dispatch to the phase-implementer rather than fixing it myself.
2. The plan currently says `implementation-specialist` (copied from feat-10). Update the Execution approach + Decisions Made + Recent Updates to pin down the pattern.

Let me do that edit now. The user's question "Is the same setup available here?" — answer + align the plan. I should be careful not to overdo it: the user is asking a question. But aligning the plan is a natural part of it (the plan explicitly says "to confirm at Phase 1 start"). Since the user just stated their intent, updating the plan is appropriate, and I think I should also add a decision entry recording the user's choice.

Let me check the phase-implementer description once more: "Implement one phase of the `.specmgr/feat/<id>/README.md` plan from start to finish — code, tests, phase-end quality gates, and updating the Progress section of the plan — and then stop and report."

Note: "updating the Progress section of the plan" — the phase-implementer itself updates the Progress section of the plan. This is a bit at odds with "the orchestrator makes no changes," but this refers to changes to code. Updating the plan's Progress section is done by the phase-implementer as part of its work. Good — that's consistent: the orchestrator validates the code, the implementer records progress.

Hmm, wait — actually, should the orchestrator validate *and commit*? The user didn't say the orchestrator commits. In feat-10 the orchestrator committed (one Conventional Commit per phase). I'll leave commit behavior as "one Conventional Commit per phase" (by the orchestrator after validation) — consistent with prior features and with my git rule (only commit when explicitly requested; the plan's execution approach is the user's standing instruction... hmm, my system prompt says "never commit changes unless the user explicitly asks." The plan says commit per phase. The user hasn't yet explicitly asked to commit in this session. I'll keep the plan's wording (it was written as part of the agreed plan form), but in the reply I can note that commits happen only when they want them / per the plan. Actually — let's not overthink this. The plan already says "committed as one Conventional Commit per phase," and the user has seen and approved this plan structure (modeled on feat-10). My job now: answer the question + update the Execution approach to name the pattern.

Edit 1 — Execution approach paragraph:

Old:
"**Execution approach** (to confirm at Phase 1 start. See Decisions Made): each phase below is delegated to the `implementation-specialist` subagent as one unit (implementation and its own mirror tests together, not a separate test phase later), reviewed and quality-gated (ruff format/check, vulture, full `unittest` suite) by the orchestrator, and then committed as one Conventional Commit per phase — the 4-phase/4-commit form of `feat-10` (tsk)."

New:
"**Execution approach** (confirmed 2026-08-24. See Decisions Made): the Orchestrator/Phase-Implementer pattern. Each phase below is delegated to the `phase-implementer` subagent as one unit, which implements the phase end-to-end (code, its own mirror tests, phase-end quality gates — full `unittest` suite + ruff format/check + vulture — and this plan file's Progress section update), and then stops and reports. After every phase, the orchestrator validates the results independently (reruns the quality gates, reviews the phase diff, checks the ACC evidence) but makes no changes: on failure the phase is re-delegated to `phase-implementer` with the validation findings, not patched by the orchestrator. One Conventional Commit per validated phase — the 4-phase/4-commit form of `feat-10` (tsk), with `phase-implementer` replacing the `implementation-specialist` that feature used."

Edit 2 — New Decisions Made entry (appended at the end):

"- **2026-08-24**: Execution follows the Orchestrator/Phase-Implementer pattern — each phase is delegated to the `phase-implementer` subagent (phase end-to-end: code, tests, phase-end quality gates, plan's Progress section update, then stop and report); after every phase the orchestrator validates the results (independent quality-gate rerun + diff review) but makes no changes, re-delegating on failure — rationale: user-stated intent (2026-08-24); the `phase-implementer` agent type is purpose-built for exactly this (one phase of a `.specmgr/feat/<id>/README.md` plan, driven by an orchestrator); the orchestrator role is filled by the main session (no separate `phase-orchestrator` agent type is registered in this environment). Replaces the `implementation-specialist` delegation named in the original Execution approach (which `feat-10` used)."

Edit 3 — Recent Updates entry (new top):

"#### 2026-08-24T{ts} (newest)

- Completed: confirmed the execution approach with the user — the Orchestrator/Phase-Implementer pattern: `phase-implementer` subagent per phase (end-to-end: code, tests, phase-end quality gates, Progress section update, stop and report); the orchestrator (main session) validates each phase's results without making changes, re-delegating on failure; one Conventional Commit per validated phase. Updated the Execution approach and Decisions Made
- Next: user review of the revised `Assessment` structure (H3 headings); then Phase 1 (Specification)
- Notes: no separate `phase-orchestrator` agent type is registered in this environment — the orchestrator role is filled by the main session

#### 2026-08-24T13:07:31+02:00"

Wait — the 13:07:31 entry currently has "(newest)" attached. I need to remove that marker. Old string "#### 2026-08-24T13:07:31+02:00 (newest)" → becomes "#### 2026-08-24T13:07:31+02:00" without the marker.

Get a new timestamp.

Also, the 13:07 entry's "Next: user review; then Phase 1 (Specification)" — still accurate.

Now the reply: a concise answer:

- Yes — with one caveat. `phase-implementer` exists as a subagent type, purpose-built for exactly this (one phase of `.specmgr/feat/<id>/README.md` end-to-end: code, tests, phase-end quality gates, plan's Progress update, stop and report).
- There is no `phase-orchestrator` agent type registered here — I (the main session) act as orchestrator: I dispatch each phase and validate results (independent quality-gate rerun + diff review) without changing anything. On failure I re-delegate to the phase-implementer with the findings.
- The plan previously named `implementation-specialist` (copied from feat-10) — I've now updated the Execution approach / Decisions Made / Recent Updates to pin down the pattern.

Keep it concise.

Let me check what's registered here before answering, and note the plan currently names a different subagent:

**Tool: bash**

**Input:**

```json
{
  "command": "date +%Y-%m-%dT%H:%M:%S%:z"
}
```

**Output:**

```
2026-08-24T13:40:33+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 210.0s)

_Thinking:_

Available agent types (from my task tool): architect-designer, ccm, explore, general, implementation-specialist, python-reviewer, requirements-clarifier, phase-implementer, ste100, test-automation-engineer.

In other words, `phase-implementer` exists, but `phase-orchestrator` does not. The orchestrator role is something I (the main session) take on.

Alright, let me update the plan with three edits.

**Yes, with one caveat** — and the plan needs a correction, because it currently names `implementation-specialist` (copied over from feat-10). Here's what exists in this environment:

- **`phase-implementer`**: a dedicated sub-agent type, built precisely for this — it implements *exactly one phase* of the `.specmgr/feat/<id>/README.md` plan end-to-end (code, its own tests, quality gate at phase end, updating the plan's Progress section), then stops and reports. It's described as "driven by `phase-orchestrator`" and is not intended for direct selection.
- **`phase-orchestrator`**: not registered as a sub-agent type here — that role falls to me (the main session): dispatch phases one by one, independently verify each phase's results (rerun quality gate, review diffs, check ACC evidence), and **change nothing** — on failure, re-delegate to `phase-implementer` along with the verification findings rather than patching it myself.

This matches your setup 1:1. Pinning it down in the plan now:

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "**Execution approach** (to confirm at Phase 1 start, see Decisions Made):\neach phase below is delegated to the `implementation-specialist` subagent as\none unit (implementation + its own mirrored tests together, not a separate\nlater test phase), reviewed and quality-gated (ruff format/check, vulture,\nfull `unittest` suite) by the orchestrator, then committed as one\nConventional Commit per phase — the `feat-10` (tsk) 4-phase/4-commit shape.",
  "newString": "**Execution approach** (confirmed 2026-08-24, see Decisions Made): the\nOrchestrator/Phase-Implementer pattern. Each phase below is delegated to the\n`phase-implementer` subagent as one unit, which implements the phase end to\nend (code, its own mirrored tests, the phase-end quality gate — full\n`unittest` suite + ruff format/check + vulture — and this plan's Progress\nsection update), then stops and reports. After every phase, the orchestrator\nverifies the results independently (re-runs the quality gate, reviews the\nphase diff, checks the evidence against the phase's tasks) but changes\nnothing: a failing verification re-delegates the phase to `phase-implementer`\nwith the findings, it is not patched by the orchestrator. One Conventional\nCommit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with\n`phase-implementer` replacing the `implementation-specialist` that feature\nused."
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "### Recent Updates\n\n#### 2026-08-24T13:07:31+02:00 (newest)",
  "newString": "### Recent Updates\n\n#### 2026-08-24T13:40:33+02:00 (newest)\n\n- Completed: confirmed the execution approach with the user — the\n  Orchestrator/Phase-Implementer pattern: `phase-implementer` subagent per\n  phase (end to end: code, tests, phase-end quality gate, this plan's\n  Progress section update, then stop and report); the orchestrator (main\n  session) verifies each phase's results — independent quality-gate re-run\n  + diff review — but changes nothing, re-delegating the phase to\n  `phase-implementer` with the findings on failure; one Conventional Commit\n  per verified phase. Execution approach, Decisions Made, and Current\n  Status updated to pin this down\n- Next: user review of the revised `Assessment` structure (H3 headings, see\n  the 13:07:31 entry); then Phase 1 (Specification)\n- Notes: no separate `phase-orchestrator` agent type is registered in this\n  environment — the orchestrator role is fulfilled by the main session\n\n#### 2026-08-24T13:07:31+02:00"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  lazy-computed-field eager-validation history (supersedes the\n  assessment-shape detail of the earlier before/after-mitigation decision,\n  which stands otherwise).",
  "newString": "  lazy-computed-field eager-validation history (supersedes the\n  assessment-shape detail of the earlier before/after-mitigation decision,\n  which stands otherwise).\n- **2026-08-24**: Execution follows the Orchestrator/Phase-Implementer\n  pattern — each phase is delegated to the `phase-implementer` subagent\n  (one phase end to end: code, tests, phase-end quality gate, this plan's\n  Progress section update, then stop and report); after every phase the\n  orchestrator verifies the results (independent quality-gate re-run + diff\n  review) but changes nothing, re-delegating the phase with the findings on\n  failure — rationale: user-stated intent (2026-08-24); the\n  `phase-implementer` agent type is purpose-built for exactly this (one\n  phase of a `.specmgr/feat/<id>/README.md` plan, driven by an orchestrator,\n  not intended for direct selection), and no separate `phase-orchestrator`\n  agent type is registered in this environment, so the orchestrator role is\n  fulfilled by the main session. Replaces the `implementation-specialist`\n  delegation named in the original Execution approach (the pattern\n  `feat-10` used)."
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder\ncreated from `.specmgr/_template/v1/README.md`. Full schema and MCP surface\nproposed (see Design Notes and Task List), mirroring `feat-10` (tsk)'s\n4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead\nof TARRA, cause/trigger/consequence split into separate sections, assessment\nstructure documented with a worked example). Awaiting final review before\nPhase 1 starts.",
  "newString": "**As of 2026-08-24**: Planning. GitHub issue #15 opened, feature folder\ncreated from `.specmgr/_template/v1/README.md`. Full schema and MCP surface\nproposed (see Design Notes and Task List), mirroring `feat-10` (tsk)'s\n4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead\nof TARRA, cause/trigger/consequence split into separate sections,\nassessment values moved from list items to H3 headings with regex `@alias`\nconstraints, execution pinned to the Orchestrator/Phase-Implementer\npattern). Awaiting final review before Phase 1 starts."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 166.4s)

_Thinking:_

All edits have been applied. Now for the final answer — the user's question was "Is the same configuration available here?", and that has already been answered in the previous message. The edits have pinned down the pattern in the plan. Keep it concise: confirm what was changed in the plan, and point out one nuance: the phase implementer itself updates the Progress section of the plan (this is its defined responsibility), and the orchestrator only performs verification. Also mention that in feat-10 the orchestrator committed after each phase — this pattern preserves that (one Conventional Commit per verified phase).

The main body has already been conveyed in the previous message, so keep the final wrap-up short.

Plan pinned to the pattern. What's now in the README:

- **Execution approach**: `phase-implementer` per phase (end-to-end: code, tests, phase-end quality gate, this plan's Progress-section update, stop and report) → orchestrator verifies independently, changes nothing → re-delegate on failure → one Conventional Commit per verified phase.
- **Decisions Made + Recent Updates**: recorded the user-confirmed intent and the environment caveat (no `phase-orchestrator` agent type registered — main session orchestrates).
- **Current Status**: updated to reflect the full set of same-day revisions.

One nuance to align expectations: the `phase-implementer`'s own contract includes updating this plan's Progress section as part of the phase (task checkboxes + status lines) — that's the only file it touches besides code/tests. Verification (quality-gate re-run, diff review, ACC evidence check) is mine, read-only on the implementation. When you give the go-ahead, I'll dispatch Phase 1.

______________________________________________________________________

## User

We need to add a task: Create a TARA and RiskMatrix resource. This resource shall help the agent to understand what, when and how to use TARA. And what a "high risk" and "low risk" is.
In addition, the list_risk resource shall return these additional fields: impact, probability, risk product for the residual risk

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 339.2s)

_Thinking:_

The user is requesting two things:

1. **New task: Creation of TARA and RiskMatrix resources** — MCP resources (something like `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix`, or perhaps a single resource?). The content should be as follows:

   - Assist the agent in understanding what TARA is, when and how to use it
   - Define what "high risk" and "low risk" are (i.e., the 5x5 matrix / zone definitions)

2. **The `list_risk` resource** (`specmgr://rsk/list`) must return additional fields: impact, probability, and risk product — for **residual risk**.

Wait — the user wrote "list_risk", but the resource name is `specmgr://rsk/list` (the ADR says `Expose <domain>_list as paged MCP tools (list_<domain>)` — hmm, ec9f5262: "expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource". Let me recall: according to AGENTS.md, each domain has a `specmgr://tsk/list` resource… no, actually feat-10's REQ-005 says "MCP resource mirroring req: `specmgr://tsk/list`, `/example`, `/schema`, `/template`". And the ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 is "Expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource" — accepted. So in other words, there is a paged tool `list_tsk`, AND a `specmgr://tsk/list` resource? To be precise, let me check what exists for tsk/req. The user says "the list_risk resource shall return these additional fields" — so they're calling it the list resource. Let me quickly check the code: `tsk/resources/` — which resources exist?

In my plan, REQ-005 lists `specmgr://rsk/list`, `/example`, `/schema`, `/template`. The user is referring to "the list_risk resource" — presumably the `specmgr://rsk/list` resource (or the `list_rsk` tool — the tool is named `list_rsk` per the naming convention `list_<domain>`… wait, per the ADR the tool is `list_<domain>`, e.g., `list_tsk`? Hmm, but the tool list in feat-10's REQ-004 didn't include `list_tsk` — the tools were parse/get/create/update/set_status/delete/validate/get_example/get_template. And resources included `specmgr://tsk/list`. Hmm, but ADR ec9f5262 says "expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource" — but that ADR is about… let me check what it actually decided. Its title is "expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource". But feat-10 (tsk, built after that ADR, 2026-08-16) has a `specmgr://tsk/list` resource… the ADR's date is? Not sure. Let me check the actual current code to see what exists: `list_tsk` tool? `specmgr://tsk/list` resource?

To be accurate in the plan, I should quickly check `tsk/resources/` and `tsk/tools/`. Also check how `TskSummary` is used in the list resource.

Regarding the second request: "impact, probability, and risk product of the residual risk" — so `RskSummary` needs `residual_impact`, `residual_probability`, and `residual_product` (risk product = probability × impact). "Risk product" is the product (e.g., 12) — the numeric value that determines the zone. My current plan has `initial_level`, `residual_level`, `strategy`, first scope entry in `RskSummary`. Now the user wants to add residual risk impact, probability, and product. Should initial also be added? The user explicitly says "for the residual risk". So only residual: `residual_probability`, `residual_impact`, `residual_product` (computed value). Keep `initial_level`/`residual_level` as they are.

Hmm, wait — should the product be a stored/computed value? It's computed: probability × impact. In the summary it's a computed value. No problem.

Regarding the new resources: "TARA and RiskMatrix resources" — two resources:

- `specmgr://rsk/tara` (or `specmgr://rsk/strategy-tara`?) — packaged content explaining TARA: what it is, the four strategies (transfer/accept/reduce/avoid), when and how to use each strategy, and mapping to `## Strategy` section values + `status` vocabulary + `## Mitigation` guidance.
- `specmgr://rsk/risk-matrix` — packaged content explaining the 5x5 matrix: probability/impact scales with anchors (1=rare…5=almost certain; 1=negligible…5=severe), the zone table, product thresholds (1-4 low, 5-9 medium, 10-14 high, 15-25 very high) — i.e., what "high risk" and "low risk" mean, plus the derived-level semantics and how the initial/residual pair works (residual < initial under reduce).

These are static packaged documents (like `general/data/general_iso25010.md` and `general/resources/`'s `specmgr://iso25010`). The `iso25010` resource is a good precedent: a packaged domain-knowledge document exposed as a resource. Let me check how it's implemented: `general/resources/` — version + iso25010. So `rsk/resources/tara.py` + `rsk/resources/risk_matrix.py`, reading packaged data from `rsk/data/rsk_tara.md` + `rsk/data/rsk_risk_matrix.md` (or .txt/.md). The package data task 3.12 (currently "data/*.md, data/*.json") already covers `data/*.md` — good, no new glob needed; the pre-commit/CI step for schema copying is only about the schema. The content of these two documents should be derived from the plan's design notes (the TARA definitions and the 5x5 zone table), so it becomes a single source of truth… well, actually the packaged document is the source for the agent, and the plan/zone logic is inside the model. Drift concern: the zone thresholds live in both the model code (computed level) and the risk-matrix document — note in the task that the document must match the model's zone mapping and ACC-008-style drift check? Hmm — the simplest is: note that the risk-matrix document is generated from / verified against the model's zone mapping. Or keep it simple: the task says "content must match the model's derived-level zone mapping; tests assert the documented thresholds match the computed zones".

Actually, let me check how `iso25010` is handled to mirror it precisely. Let me look at `general/resources/iso25010.py` and how the data file `general/data/general_iso25010.md` is packaged (pyproject's package data for general?). Quick read.

Also, the naming: the user says "TARA and RiskMatrix resources". Resource URIs: `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix`.

Plan changes:

1. REQ-005: add the two new resources: `specmgr://rsk/list`, `/example`, `/schema`, `/template`, **`/tara`**, **`/risk-matrix`**.

2. ACC-005: mention that they are registered and their content is verified (tara: the four valid words and usage guidance; risk-matrix: zone table matching the model's derived-level mapping).

3. REQ-007 / package data: add `rsk/data/rsk_tara.md` + `rsk/data/rsk_risk_matrix.md` (the glob `data/*.md` already covers them — mention it).

4. Task 2.3 (`RskSummary`): add `residual_probability`, `residual_impact`, `residual_product` (computed value) fields for residual risk.

5. New tasks in phase 3: `rsk/resources/tara.py` + `rsk/resources/risk_matrix.py` reading the packaged data (mirroring `general/resources/iso25010.py`), plus the content documents themselves. Content writing — part of phase 3 (package data task 3.9 is about example/template; the tara/risk-matrix documents are content so they could go in phase 1 (spec) or phase 3. In feat-10, the reference documents were phase 1. The TARA/risk-matrix documents are spec content — put the drafting in phase 1 (task 1.x) and the resource wiring in phase 3. Hmm, or simpler: a single new task in phase 3 that creates the content + resource. Let me think: phase 1 = spec (schema + reference documents + tests). The TARA/risk-matrix documents are part of the spec (what "high risk" is = part of the schema semantics). Draft in phase 1 (new task 1.5? or extend 1.3), resource implementation in phase 3 (new task). Let me renumber carefully — the note in the plan says edit in place / git history; renumbering shifts cross-references. Cleaner: add task 1.5 (draft `rsk_tara.md` + `rsk_risk_matrix.md` content documents in this feature folder, or… where? The packaged data goes in `rsk/data/`. But the reference documents are placed in the feature folder. The content documents must end up in `rsk/data/` (package data). The phase 3 task (package data) copies/writes them into `rsk/data/`. In feat-10: `tsk/data/tsk_example.md`/`tsk_template.md` were created in phase 3 task 3.9. The reference document (test fixture) was placed in the feature folder in phase 1.

   Simplest, most consistent plan:

   - Task 1.5 (new, phase 1): draft the packaged content documents `rsk_tara.md` (TARA: what/when/how for each of the four strategies, mapping to `## Strategy` values, interaction with status/mitigation) and `rsk_risk_matrix.md` (probability/impact scale anchors, 5x5 zone table, product thresholds, definition of high/medium/low/very-high, before/after residual semantics) — content must match the model's zone mapping; place drafts in this feature folder, mirroring the `rsk_reference.md` convention; depends on task 1.2.
   - Task 3.x (new, phase 3): `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix` resources + packaged copies `rsk/data/rsk_tara.md`/`rsk_risk_matrix.md` via `_packaged_data.py`, mirroring `general/resources/iso25010.py`; add tests asserting that the documented zone thresholds in `rsk_risk_matrix.md` match `Assessment.level`'s computed mapping (drift guard); depends on task 1.5 + task 3.1 (or 3.9).

   Renumbering: insert as task 3.12, and shift 3.12→3.13, 3.13→3.14, 3.14→3.15, 3.15→3.16? Ugh, renumbering touches cross-references (task 3.13 depends on "tasks 3.3, 3.4, 3.5, 3.8, 3.10"; task 3.14 depends on "tasks 3.2-3.13"; task 3.15 depends on "tasks 3.1-3.14"). The plan's note says edit in place; but shifting is fine as long as cross-references are updated. Or append at the end as tasks 3.16/3.17 without renumbering (dependency: the package data entry task 3.12 already covers `data/*.md`). Appending avoids renumbering:

   - Task 3.16 (new): content documents → packaged data + resources `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix` — depends on task 1.5, task 3.12.
   - Task 3.17: tests for the two resources (registered in MCP.md; content drift guard) — depends on task 3.16.
     And task 3.14 (server.py import) depends on "tasks 3.2-3.13" — should now be 3.2-3.17. Task 3.15 (tests) depends on "tasks 3.1-3.14" → 3.1-3.16/3.17… let me update those dependency ranges.

   Hmm, wait, actually — phase 1's task 1.5: the content documents are spec content, but the risk-matrix document's thresholds must match task 1.2's model zone mapping. Order: 1.2 (model) → 1.3 (reference doc) → 1.4 (tests) → 1.5 (tara/matrix content doc, depending on 1.2). No problem.

6. Update the Design Notes "List summary" bullet: add the residual fields.

7. REQ-007: the package data description mentions "package data example/template/schema" — add the TARA/risk-matrix documents.

8. Current Status + Recent Updates + Decisions Made entries.

9. Also — the issue body? The issue lists attributes, and resources are "same as req". The new resources are an addition beyond that — should issue #15 also be updated? The issue says "resources: same as `req`" — now there are two more (tara, risk-matrix). Minor point: update the issue body line to "\* resources: same as `req`, plus `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` (domain-knowledge documents for the agent)". And the RskSummary fields… the issue body doesn't mention the list's fields, so no problem. Let me update the issue body line — keep the issue as the canonical requirements statement.

Also, the user says "the list_risk resource" — to make sure I'm naming it correctly in the plan, let me check the actual naming in the code (is it `list_rsk`? or `specmgr://rsk/list`?). Let me look at tsk's resources and summary. Quick exploration:

- `src/biz/dfch/specmgr/tsk/resources/`
- `src/biz/dfch/specmgr/tsk/models/v1/summary.py`
- `src/biz/dfch/specmgr/general/resources/iso25010.py` (precedent for domain-knowledge resources)

Let me read these in parallel.

Let me check the existing list-resource and a domain-knowledge resource precedent (`iso25010`) so the new tasks mirror real names:

**Tool: bash**

**Input:**

```json
{
  "command": "ls src/biz/dfch/specmgr/tsk/resources/ src/biz/dfch/specmgr/general/resources/ src/biz/dfch/specmgr/general/data/",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
src/biz/dfch/specmgr/general/data/:
general_compact_history_instructions.md
general_iso25010.md

src/biz/dfch/specmgr/general/resources/:
__init__.py
__pycache__
iso25010.py
version.py

src/biz/dfch/specmgr/tsk/resources/:
__init__.py
__pycache__
tsk_example.py
tsk_schema.py
tsk_template.py

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/summary.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/summary.py</path>
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
18: """Pydantic model for one line of TSK listing output (Phase 2, Task 2.3).
19: 
20: Mirrors :class:`~biz.dfch.specmgr.req.models.v1.summary.ReqSummary`
21: field-for-field, for the (Phase-3, not-yet-built) ``specmgr://tsk/list``
22: resource. Subclasses
23: :class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
24: ``id``/``title``/``status``/``ref`` fields (feat-13 Task 1.3, REQ-003).
25: """
26: 
27: from __future__ import annotations
28: 
29: from ....general.models.summary import DocSummary
30: 
31: __all__ = ["TskSummary"]
32: 
33: 
34: class TskSummary(DocSummary):
35:     """One line of ``specmgr://tsk/list`` output.
36: 
37:     Parameters
38:     ----------
39:     id:
40:         The document's specmgr-assigned identifier, or ``None`` if the file
41:         has not been assigned one yet (e.g. hand-authored without the
42:         ``id`` frontmatter key).
43:     title:
44:         The task list's ``# {title}`` H1.
45:     status:
46:         The task list's ``frontmatter.status`` value, verbatim.
47:     ref:
48:         The document's extensionless base name (e.g.
49:         ``"tsk-<uuid>-a-title"``), deliberately *not* a filename or path --
50:         callers must not read this off disk themselves, only pass it to
51:         ``get_tsk`` alongside (or instead of) ``id``. Named ``ref`` rather
52:         than ``filename`` precisely to avoid inviting direct filesystem
53:         access (mirrors
54:         :class:`~biz.dfch.specmgr.req.models.v1.summary.ReqSummary`).
55:     """

(End of file - total 55 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 174.8s)

_Thinking:_

Interesting — `tsk/resources/` only has tsk_example, tsk_schema, and tsk_template — there's no `tsk_list.py`! But feat-10's REQ-005 claims that `specmgr://tsk/list` exists… and the TskSummary docstring says "for the (phase 3, not yet built) `specmgr://tsk/list` resource". Wait a sec — maybe feat-13 (list paging) changed things: ADR ec9f5262 "expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource". So feat-13 probably replaced the list resource with a paged `list_<domain>` tool! Let me check: is there a `list_tsk` tool somewhere? And AGENTS.md says "expose listing and by-id reads as MCP resources in addition to tools" (ADR 7531106b) — that's an old one. ADR ec9f5262 seems newer (feat-13, list paging).

The user is saying "the list_risk resource shall return these additional fields" — hmm, they call this a resource. But if feat-13 converted listing into a paged tool `list_rsk`… the user might be using "resource" loosely, or maybe the list resource still exists alongside the paged tool. Let me check what feat-13 did: look at tsk/tools and the feat-13 README, and search for "list_tsk".

I found that `tsk/resources/` doesn't have a list resource — feat-13 (list paging) likely converted listings into paged tools. Let me check how listings are currently exposed:

**Tool: bash**

**Input:**

```json
{
  "command": "ls src/biz/dfch/specmgr/tsk/tools/ src/biz/dfch/specmgr/general/tools/ | head -40; rg -l \"list_tsk|list_req\" src/ tests/ 2>/dev/null || true",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
src/biz/dfch/specmgr/general/tools/:
__init__.py
__pycache__
_doc_paths.py
_packaged_data.py
_paging.py
mdformat.py
webfetch.py

src/biz/dfch/specmgr/tsk/tools/:
__init__.py
__pycache__
_io.py
_lock.py
_paths.py
_write.py
create_tsk.py
delete_tsk.py
get_tsk.py
get_tsk_example.py
get_tsk_template.py
list_tsk.py
parse_tsk.py
set_status_tsk.py
update_tsk.py
validate_tsk.py

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 192.0s)

_Thinking:_

In other words, feat-13 added a paged `list_tsk` **tool** (`tsk/tools/list_tsk.py`), and the list resource was removed (per ADR ec9f5262: "Expose <domain>_list as a paged MCP tool (list_<domain>), not as a resource"). My rg for "list_tsk" against src/tests returned nothing — weird, `rg -l` returned nothing? Actually, rg's output shows nothing after the ls output... wait, the command was `rg -l ... || true` — no output means no matches?? But `list_tsk.py` exists. Oh — maybe rg isn't installed either (just like before, `rg: command not found` got swallowed by `|| true`). Right, rg is not available in this environment. Use the grep tool instead.

So the current situation is:

- `specmgr://tsk/list` resource: gone (feat-13)
- `list_tsk` paged tool: exists
- `TskSummary`: one line of the listing output

Now the user's request: "the list_risk resource shall return these additional fields" — they're calling it a resource, but the actual vehicle is the `list_rsk` paged tool (ADR ec9f5262). My plan (written before this detail) states REQ-005 as: "MCP resources mirroring `req`: `specmgr://rsk/list`, `/example`, `/schema`, `/template`" — this is stale with respect to feat-13! feat-10 included `specmgr://tsk/list` as a resource, but feat-13 later removed it and replaced it with the paged `list_tsk` tool. Therefore my rsk plan must be corrected as follows:

- Resources: `specmgr://rsk/example`, `/schema`, `/template` (no `/list`)
- Tools: add the paged `list_rsk` tool (using `RskSummary` + `general/tools/_paging.py`)

To mirror this accurately, let me check what feat-13's list_tsk looks like (signature: max_results/offset, returns a summary) — read the header of `tsk/tools/list_tsk.py` and check feat-13's README for how it was implemented. Also check `general/models/summary.py` (DocSummary: id/title/status/ref).

Then the user's request "the list_risk resource shall return these additional fields: impact, probability, risk product for the residual risk" → this means the `list_rsk` paged tool / `RskSummary` must include `residual_impact`, `residual_probability`, `residual_product` (risk product = p×i).

To read:

- tsk/tools/list_tsk.py
- .specmgr/feat/feat-13-list-paging/README.md (skim: what was removed/added, resources vs tools)
- general/resources/iso25010.py (precedent for domain-knowledge resources — for the new TARA/RiskMatrix resources)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools/list_tsk.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools/list_tsk.py</path>
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
18: """``@mcp.tool()`` wrapper: list_tsk (feat-13-list-paging Task 2.4).
19: 
20: Replaces the earlier ``specmgr://tsk/list`` resource
21: (``tsk.resources.tsk_list``). Converted from a resource to a tool because
22: MCP resources cannot take arbitrary parameters (only URI-template path
23: segments), and ``max_results``/``offset`` paging needs exactly that -- the
24: same resource->tool reasoning already applied to ``get_req``
25: (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). See
26: ``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging
27: contract shared by every ``list_<domain>`` tool.
28: """
29: 
30: from __future__ import annotations
31: 
32: from pydantic import ValidationError
33: 
34: from ...general.models import PagedResult
35: from ...general.tools._paging import normalize_paging, paginate
36: from ...server import mcp
37: from ..models.v1 import TskSummary
38: from ._io import read_tsk
39: from ._paths import iter_tsk_paths
40: 
41: 
42: @mcp.tool(
43:     name="list_tsk",
44:     title="List task lists",
45:     description=(
46:         "Ids, titles, statuses, and refs of task lists in the configured task list base "
47:         "directory, one page at a time, for context before addressing one by id. "
48:         "'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- "
49:         "for documents that have no assigned id; use it with the get_tsk tool instead. "
50:         "max_results/offset control paging (default page size 25, capped at 100); "
51:         "out-of-range values are clamped, not errored."
52:     ),
53: )
54: def list_tsk(max_results: int | None = None, offset: int | None = None) -> PagedResult[TskSummary]:
55:     """Return one page of one-line task-list summaries from the configured base directory.
56: 
57:     A file that fails to parse (``AssertionError`` or
58:     ``pydantic.ValidationError`` -- the same two error channels
59:     :func:`~biz.dfch.specmgr.tsk.models.v1.parse_tsk` raises) is silently
60:     skipped -- a single malformed file must not break listing every other
61:     valid one (mirrors ``tsk.tools._paths.find_tsk_path``'s own
62:     skip-on-parse-failure rule). The complete, skip-broken-file-filtered
63:     list is materialized first, then paginated in memory, so the returned
64:     ``total`` always reflects the count of parseable documents only,
65:     independent of paging.
66: 
67:     Parameters
68:     ----------
69:     max_results:
70:         Maximum number of summaries to return in this page. Defaults to
71:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
72:         otherwise clamped into range (see
73:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
74:     offset:
75:         Zero-based index of the first summary to include in this page.
76:         Defaults to ``0`` when not given (``None``); negative values are
77:         floored to ``0``.
78: 
79:     Returns
80:     -------
81:     PagedResult[TskSummary]
82:         One entry per successfully-parsed ``*.md`` file within the
83:         requested page, in filename-sorted order. ``results`` is empty if
84:         the base directory does not exist, holds no task lists, or
85:         ``offset`` is past the end of the full list.
86:     """
87:     summaries: list[TskSummary] = []
88:     for path in iter_tsk_paths():
89:         try:
90:             doc = read_tsk(path)
91:         except (AssertionError, ValidationError):
92:             continue
93:         summaries.append(
94:             TskSummary(
95:                 id=doc.frontmatter.id,
96:                 title=doc.body.text,
97:                 status=doc.frontmatter.status,
98:                 ref=path.stem,
99:             )
100:         )
101:     return paginate(summaries, *normalize_paging(max_results, offset))

(End of file - total 101 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources/iso25010.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources/iso25010.py</path>
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
18: """Resource: specmgr://iso25010 (Task 0.8.3).
19: 
20: Reads the packaged ISO/IEC 25010:2023 product quality model markdown
21: (``general/data/general_iso25010.md``, via
22: ``general.tools._packaged_data.read_packaged_text``) and parses it into a
23: structured :class:`~biz.dfch.specmgr.models.Iso25010`, mirroring
24: ``req/resources/req_schema.py``'s packaged-data-read style.
25: """
26: 
27: from __future__ import annotations
28: 
29: from ...models import Iso25010, parse_iso25010
30: from ...server import mcp
31: from ..tools._packaged_data import read_packaged_text
32: 
33: 
34: @mcp.resource(
35:     "specmgr://iso25010",
36:     name="iso25010",
37:     title="ISO/IEC 25010:2023 Product Quality Model",
38:     description=(
39:         "The nine main characteristics (and their sub-characteristics) of the ISO/IEC "
40:         "25010:2023 system/software product quality model, each with a description."
41:     ),
42:     mime_type="application/json",
43: )
44: def iso25010() -> Iso25010:
45:     """Return the parsed ISO/IEC 25010:2023 product quality model.
46: 
47:     Reads the packaged copy (``general/data/general_iso25010.md``) fresh on
48:     every call (no in-memory cache, consistent with every other resource/tool
49:     in this codebase) but never regenerates it -- this is static reference
50:     data, not a user-edited/versioned document type.
51: 
52:     Returns
53:     -------
54:     Iso25010
55:         The nine main characteristics (each with its sub-characteristics),
56:         the ordered list of characteristic names, and the copyright notice.
57: 
58:     Raises
59:     ------
60:     FileNotFoundError
61:         If the packaged ``general_iso25010.md`` is missing.
62:     AssertionError
63:         If the packaged file's heading/list structure is malformed.
64:     """
65:     result: Iso25010 = parse_iso25010(read_packaged_text("general", "iso25010", "md"))
66:     return result

(End of file - total 66 lines)
</content>
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 564.5s)

_Thinking:_

Now everything is clear:

1. **feat-13 converted the list resource into a paged tool**: `list_tsk(max_results, offset) -> PagedResult[TskSummary]`, built on top of `general/tools/_paging.py` + `DocSummary`. The `specmgr://tsk/list` resource no longer exists. Therefore, my rsk plan is outdated on this point (I wrote "resources mirroring req: specmgr://rsk/list, /example, /schema, /template" — the /list one must be removed, and a paged `list_rsk` tool must be added).

   Note: `req` still has… no wait, feat-13 probably converted all domains (req, uc, tsk, qa, adr?) into `list_<domain>` tools. The tool description I can see in my MCP toolset has `specmgr_list_tsk`? Looking at the available specmgr tools in my function list: `specmgr_list_adr`, `specmgr_list_qa`, `specmgr_list_req`, `specmgr_list_tsk`, `specmgr_list_uc` — yes! All domains have a `list_*` paged tool, and none of them have a list resource. Confirmed.

   So the user's "list_risk resource" = the **`list_rsk` paged tool** (the one-line `RskSummary` entries). The plan must be corrected as follows:

   - REQ-004 tools: add `list_rsk` (paged, feat-13 contract: `max_results`/`offset`, `PagedResult[RskSummary]`, skip malformed files, default 25 / cap 100)
   - REQ-005 resources: `specmgr://rsk/example`, `/schema`, `/template` only (no `/list`) — plus two new ones: `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`
   - Task 2.3 RskSummary: in addition to the existing ones, add `residual_probability`, `residual_impact`, `residual_product` (the risk product)
   - New phase-3 tasks: the `list_rsk` tool (mirroring `tsk/tools/list_tsk.py` + the paging contract in feat-13's README), and the two content resources.

2. **iso25010 is a direct precedent for the new resources**: a static packaged markdown read via `read_packaged_text(domain, name, "md")`, parsed into a structured model and returned as JSON (mime_type application/json). For TARA and RiskMatrix:

   - Option A (mirror iso25010 exactly): a structured Pydantic model + parser (`parse_tara`, `parse_risk_matrix`) — heavier.
   - Option B: return the markdown text as-is (mime_type text/markdown) — simpler. Does any existing resource return raw text? `req_schema.py` — "mirrors the packaged-data-read style of req/resources/req_schema.py" — let me think about what req_schema returns… probably JSON of the schema. tsk_template/example returns raw markdown text (read_packaged_text). So there is a precedent for raw-text resources (`specmgr://tsk/example`).

   For "helping the agent understand what, when, and how to use TARA," raw markdown prose is exactly what an LLM agent wants to read (like the example/template resources). Parsing into a structured model would be overkill and would impose a rigid structure on prose. Proposal: `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` return packaged markdown text (mime_type `text/markdown`), mirroring `tsk_example`/`tsk_template`, with content written as agent-facing guidance:

   - `rsk_tara.md`: what TARA is (Transfer/Accept/Reduce/Avoid), the four valid words (exactly the values allowed in `## Strategy`), when and how to apply each strategy (mapping to the consuunt scenarios: low probability/high impact → transfer; high/high → avoid; high probability/low impact → reduce; low/low → accept), and how strategy interacts with `## Mitigation` and frontmatter status.
   - `rsk_risk_matrix.md`: the 5x5 matrix — anchors of the probability scale (1=rare…5=almost certain), anchors of the impact scale (1=negligible…5=severe), the zone table, product thresholds (1–4 low, 5–9 medium, 10–14 high, 15–25 very high) — what "high risk"/"low risk" means; how to read initial and residual, and the rule that `reduce` implies residual < initial.

   Drift guard: the thresholds documented in `rsk_risk_matrix.md` must match the `Assessment.level` computed mapping — a test asserts that the model's zone boundaries agree with the constants documented in the packaged document (e.g., parse the thresholds from the document, or more simply: the test hardcodes the same boundaries and asserts against the model; the real guard is that both are written from the plan). Simplest, most honest statement: "a test asserts the model's derived-level zone mapping against the four threshold boundaries, and the packaged document is written from the same table in the plan's Design Notes; ACC-005 verifies the documented zones agree with the model's mapping."

3. The user's exact words: "the list_risk resource shall return these additional fields: impact, probability, risk product for the residual risk." → `RskSummary` gets `residual_impact: int`, `residual_probability: int`, `residual_product: int` (the product). (Plus, per the earlier design, `initial_level`/`residual_level`/`strategy`/first `scope` are retained.) The tool name is `list_rsk` (naming convention `list_<domain>` — the user said "list_risk," but the convention is `list_rsk`, just as tsk is "list_tsk" and not "list_task". I'll name it `list_rsk` and note this.)

OK, editing the plan:

**REQ-004** (tools): current text:
"REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`, `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`"
→ add `list_rsk` (paged, feat-13 contract). New text:
"REQ-004: MCP tools mirroring `req`'s lifecycle surface plus the feat-13 listing contract: `parse_rsk`, `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`, and the paged `list_rsk` tool (`max_results`/`offset`, `PagedResult[RskSummary]`, skip-and-continue on unparseable files — mirroring `tsk/tools/list_tsk.py` and the shared paging contract in feat-13)"

**REQ-005** (resources): current:
"REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`, `/example`, `/schema`, `/template`"
→
"REQ-005: MCP resources: `specmgr://rsk/example`, `/schema`, `/template` (no `/list` — listing is the paged `list_rsk` tool per feat-13/ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), plus two new static domain-knowledge resources for the agent: `specmgr://rsk/tara` (what TARA is, the four valid strategy words, when and how to apply each) and `specmgr://rsk/risk-matrix` (the 5x5 matrix: scale anchors, zone table, product thresholds — what 'high risk' and 'low risk' mean)"

**ACC-004**: add a reference to list_rsk. Current text: "every listed tool implemented and registered (confirmed present in regenerated `docs/MCP.md`), with `create_rsk`/`update_rsk` validating body-only content…" → add ", and `list_rsk` returns one-line `RskSummary` entries including the residual-risk fields (`residual_probability`/`residual_impact`/`residual_product`) with correct paging".

**ACC-005**: "every listed resource implemented and registered (confirmed present in regenerated `docs/MCP.md`)" → add ", with `specmgr://rsk/tara` documenting the four valid TARA words and `specmgr://rsk/risk-matrix`'s zone table matching the model's derived-level mapping".

**REQ-007** (packaged data): current: "Packaged example/template/schema data (`rsk/data/`) via the existing generic `general/tools/_packaged_data.py`, with the matching `pyproject.toml` package-data entry, pre-commit hook, and CI step" → add "+ the two domain-knowledge documents (`rsk_tara.md`, `rsk_risk_matrix.md`)".

**Design Notes — List summary bullet**: current:
"- **List summary** — `RskSummary` (for `specmgr://rsk/list`) carries `id`/`title`/`status` plus `initial_level`, `residual_level`, `strategy`, and the first `scope` entry, so a register-wide risk-matrix view can be built from the listing alone."
→
"- **List summary** — `RskSummary` (one line of the paged `list_rsk` tool's output — no `specmgr://rsk/list` resource, per feat-13) carries `id`/`title`/`status`/`ref` plus `initial_level`, `residual_level`, `strategy`, the first `scope` entry, and the residual-risk coordinates `residual_probability`, `residual_impact`, `residual_product` (the risk product, probability x impact) — so a register-wide risk-matrix view can be built from the listing alone."

**Design Notes — new bullet on domain-knowledge resources**:
"- **Domain-knowledge resources** — `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` are static packaged markdown documents (content written in Phase 1 from this plan's Design Notes), served as raw text (`text/markdown`, mirroring `specmgr://tsk/example`/`/template`) rather than parsed into structured models — the audience is an LLM agent that needs to read guidance, not code that needs data. `rsk_tara.md`: what TARA is, the four valid `## Strategy` words (verbatim the closed set), when and how to apply each (low probability/high impact → transfer; high/high → avoid; high probability/low impact → reduce; low/low → accept), and how the strategy interacts with `## Mitigation` and frontmatter `status`. `rsk_risk_matrix.md`: probability/impact scale anchors, the 5x5 zone table, product thresholds (1-4 low, 5-9 medium, 10-14 high, 15-25 very high) — i.e. what 'high risk' and 'low risk' mean — plus the initial/residual reading rule (`reduce` implies residual < initial). The documented zone thresholds must match the model's derived-`level` mapping (test in ACC-005)."

**Task list changes:**

Phase 2: Task 2.3 — update to include the residual fields:
Current: "Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with `initial_level`/`residual_level`/`strategy`/first `scope` entry, for the `specmgr://rsk/list` resource) — depends on: Task 2.1 — status: not-started"
→ "Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with `initial_level`/`residual_level`/`strategy`/first `scope` entry plus `residual_probability`/`residual_impact`/`residual_product` (risk product), for the `list_rsk` tool) — depends on: Task 2.1 — status: not-started"

New phase-1 task (content documents): add as Task 1.5:
"- [ ] Task 1.5: Draft the two packaged domain-knowledge documents (`rsk_tara.md`, `rsk_risk_matrix.md`) from this plan's Design Notes (TARA: what/when/how for each of the four valid words + interaction with `## Mitigation`/`status`; risk matrix: scale anchors, zone table, product thresholds, initial/residual reading rule) — placed in this feature folder until Phase 3 packages them into `rsk/data/` (mirroring the `rsk_reference.md` convention) — depends on: Task 1.2 — status: not-started"

Phase 3: add tasks for the `list_rsk` tool and the two resources. Current phase-3 tasks go up to 3.15. Insert `list_rsk` as Task 3.9 and shift?? Renumbering again… alternative: append:

- Task 3.16: `list_rsk` paged tool — depends on Task 2.3, Task 3.1
- Task 3.17: `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix` resources + packaged copies `rsk/data/rsk_tara.md`/`rsk_risk_matrix.md` (via `read_packaged_text`, mirroring `tsk/resources/tsk_example.py`) — depends on Task 1.5, Task 3.1
- Task 3.18: tests for `list_rsk` (paging contract, residual fields present) and the two resources (registered, content present, zone-table/mapping agreement test) — depends on Tasks 3.16, 3.17

And update Task 3.14 (server.py import): "depends on: Tasks 3.2-3.13" → "Tasks 3.2-3.18"? Wait, 3.14 currently depends on 3.2-3.13; with 3.16-3.18 appended after it, the server.py import line needs to be re-verified after those… actually, the server.py import registers the whole domain package; in feat-10 task 3.15 (server.py) depended on 3.2-3.14. In my plan, task 3.14 = server.py import, depends on "Tasks 3.2-3.13" — but now there are tasks 3.16-3.18 after it that also add tools/resources, so the server.py task should really depend on everything, or at least be re-verified at the end. Cleanest: update 3.14's dependency to "Tasks 3.2-3.13, 3.16-3.18" and task 3.15's (tests) dependency to "Tasks 3.1-3.14, 3.16-3.18". Hmm, but that's a little odd ordering-wise (tests before the new tasks' tests). Alternatively, renumber and insert 3.16-3.18 before server.py/tests… renumbering 3.14→3.16, 3.15→3.17 and inserting list_rsk as 3.14, resources as 3.15? That shifts two tasks and their cross-references (3.13 depends on 3.3,3.4,3.5,3.8,3.10 — unaffected; 3.14(server) depends on 3.2-3.13; 3.15(tests) depends on 3.1-3.14).

Simplest, correct order-preserving approach: renumber so the new tasks slot in logically before the server.py registration and the tests:

- Current 3.14 (server.py import) → becomes 3.17
- Current 3.15 (tests) → becomes 3.18
- New 3.14: `list_rsk` tool (depends on 2.3, 3.1)
- New 3.15: `tara` + `risk-matrix` resources + packaged documents (depends on 1.5, 3.1)
- New 3.16: tests for list_rsk + the two resources (depends on 3.14, 3.15)

And update dependencies:

- 3.17 (server.py): depends on Tasks 3.2-3.16
- 3.18 (tests, mirroring tsk): depends on Tasks 3.1-3.17 — hmm, the current 3.15's text is "depends on: Tasks 3.1-3.14". New 3.18: "depends on: Tasks 3.1-3.17".

Wait — but the current 3.15 is the general tests task mirroring tests/tsk. The new 3.16 is tests specifically for list_rsk + resources. That's fine (feat-13 also had its own test tasks).

Renumbering affects: task 3.13's dependencies (3.3, 3.4, 3.5, 3.8, 3.10 — no change), and any mention of "Tasks 3.2-3.13"/"Tasks 3.1-3.14" in the body. Plus REQ/ACC references don't name tasks. OK.

Also **Phase 4 / REQ-008**: no change (registry-driven, mcp-docs picks up new tools/resources).

**Issue #15 body**: update — add a line for the new resources and the list fields. The issue body has "\* resources: same as `req`". Update to:
"\* resources: same as `req` (no `/list` — listing is the paged `list_rsk` tool per feat-13), plus `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` (static domain-knowledge documents: when/how to use TARA; what 'high'/'low' risk means on the 5x5 matrix)"
And add under Attributes:
"\* `list_rsk` summary fields: … impact, probability, and risk product (probability x impact) of the residual risk"
Hmm, the attributes list is about document attributes; the list fields are about the tool. I'll add a short "Listing" bullet. Let me just append two bullets after the attributes list:

"\* listing (`list_rsk` tool, paged): each summary line additionally carries the residual risk's `impact`, `probability`, and risk product (`probability x impact`)"

**Frontmatter updated date**: same day, no change.

**Recent Updates**: new entry (13:5x? get the timestamp):

- Completed: added two requirements per user feedback — (1) new static domain-knowledge resources `specmgr://rsk/tara` (what/when/how of the four valid TARA words) and `specmgr://rsk/risk-matrix` (5x5 scale anchors, zone table, product thresholds — the definition of 'high'/'low' risk), content drafted in Phase 1 and served as packaged markdown; (2) the `list_rsk` summary lines now carry the residual risk's `residual_probability`/`residual_impact`/`residual_product` (risk product). Also corrected the plan against feat-13 (listing is the paged `list_<domain>` tool, not a `specmgr://rsk/list` resource). New tasks 1.5, 3.14-3.16; renumbered old 3.14/3.15 to 3.17/3.18. Issue #15 updated.
- Next: user review; then Phase 1

**Decisions Made**: new entry:

- **2026-08-24**: Two static domain-knowledge resources (`specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`) are served as raw packaged markdown rather than structured models — rationale: user requirement (the resources should help the agent understand when/how to use TARA and what 'high'/'low' risk means); the audience is an LLM agent reading guidance, and raw prose mirrors the `specmgr://tsk/example`/`/template` text resources, while `iso25010`'s structured parse is for machine data. Content is drafted in Phase 1 from the plan's Design Notes so the zone table and TARA words have a single source of truth; a test guards the documented zone thresholds against the model's derived-`level` mapping.
- **2026-08-24**: The `RskSummary` lines (paged `list_rsk` tool) carry the residual risk's `residual_probability`/`residual_impact`/`residual_product` in addition to `initial_level`/`residual_level`/`strategy`/first `scope` — rationale: user requirement ("impact, probability, risk product for the residual risk"); `residual_product` (probability x impact) is the matrix coordinate that determines the residual zone, so a register-wide matrix view can be built from the listing alone. Also corrected the plan's REQ-005 against feat-13: no `specmgr://rsk/list` resource exists — listing is the paged `list_rsk` tool (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

Hmm, two decisions in one bullet — split into two. OK.

Also **Current Status**: append to the revision list: "+ domain-knowledge resources and residual-risk listing fields added 2026-08-24; listing corrected to the paged `list_rsk` tool per feat-13".

Also **REQ-001**? No — schema unchanged.

Also **Out of scope**: "Aggregated, register-wide views" — mentions `RskSummary (see specmgr://rsk/list)` — must update that reference to the `list_rsk` tool. Current text:
"`RskSummary` (see `specmgr://rsk/list`) carries `initial_level`/`residual_level`/`strategy` per document" → update to "`RskSummary` (one line of the paged `list_rsk` tool) carries … plus the residual-risk coordinates".

Also the **Scope Included** bullet: "Full MCP surface (tools/resources/prompts/packaged data) mirroring req/tsk" — no problem, plus I could add "two domain-knowledge resources". Minor; update to "mirroring `req`/`tsk` (including the feat-13 paged `list_rsk` tool and the two new domain-knowledge resources)".

Also **Dependencies**: add ADR ec9f5262 (paging) + `general/tools/_paging.py`, `general/models.summary.DocSummary`. And iso25010 as the domain-knowledge-resource precedent? iso25010 is structured, but I chose raw text like tsk_example. I'll cite `tsk/resources/tsk_example.py` as the raw-text precedent.

**ACC-007** (packaged data from an install): mentions `rsk/data/{...}` — the glob already covers \*.md. Fine.

Task 3.12 (package-data entry `data/*.md`, `data/*.json`) — the glob already covers the two new .md documents. Good, no change needed; maybe add a note.

Now let me get a timestamp and do all the edits. It's a lot of edits; I'll be careful about exact oldStrings from the current file state. I'll list the edits:

E1. REQ-004 line.
Current (from the last write):
"- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`,
`get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,
`set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`"
New:
"- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface plus the
feat-13 listing contract: `parse_rsk`, `get_rsk_example`,
`get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`,
`delete_rsk` (stub), `validate_rsk`, `get_rsk`, and the paged `list_rsk`
tool (`max_results`/`offset`, `PagedResult[RskSummary]`, skip-and-
continue on unparseable files — mirroring `tsk/tools/list_tsk.py` and
feat-13's shared paging contract)"

E2. REQ-005 line.
Current:
"- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`,
`/example`, `/schema`, `/template`"
New:
"- [ ] REQ-005: MCP resources: `specmgr://rsk/example`, `/schema`,
`/template` (no `/list` — listing is the paged `list_rsk` tool per
feat-13 / ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), plus two new static
domain-knowledge resources: `specmgr://rsk/tara` (what TARA is, the four
valid strategy words, when and how to apply each) and
`specmgr://rsk/risk-matrix` (the 5x5 matrix: scale anchors, zone table,
product thresholds — what 'high risk' and 'low risk' mean)"

E3. ACC-004.
Current:
"- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and
registered (confirmed present in regenerated `docs/MCP.md`), with
`create_rsk`/`update_rsk` validating body-only content the same way
`create_req`/`update_req`/`create_tsk`/`update_tsk` do"
New:
"- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and
registered (confirmed present in regenerated `docs/MCP.md`), with
`create_rsk`/`update_risk`... " — no wait, keep "update_rsk". Add: ", and `list_rsk` returning one-line `RskSummary` entries that include the residual-risk fields (`residual_probability`/`residual_impact`/`residual_product`) with correct paging/clamping per the feat-13 contract"

E4. ACC-005.
Current:
"- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and
registered (confirmed present in regenerated `docs/MCP.md`)"
New:
"- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and
registered (confirmed present in regenerated `docs/MCP.md`), with
`specmgr://rsk/tara` documenting exactly the four valid TARA words and
`specmgr://rsk/risk-matrix`'s zone table matching the model's
derived-`level` mapping (threshold test)"

E5. Scope Out-of-scope bullet:
Current:
"- Aggregated, register-wide views (e.g. a combined risk-matrix chart across
all `rsk` documents) — `RskSummary` (see `specmgr://rsk/list`) carries
`initial_level`/`residual_level`/`strategy` per document precisely so such a
view can be built later without reading each document"
New:
"- Aggregated, register-wide views (e.g. a combined risk-matrix chart across
all `rsk` documents) — `RskSummary` (one line of the paged `list_rsk`
tool) carries `initial_level`/`residual_level`/`strategy` plus the
residual-risk coordinates per document precisely so such a view can be
built later without reading each document"

E6. Scope Included bullet:
Current:
"- Full MCP surface (tools/resources/prompts/packaged data) mirroring
`req`/`tsk`"
New:
"- Full MCP surface (tools/resources/prompts/packaged data) mirroring
`req`/`tsk`, including the feat-13 paged `list_rsk` tool and the two new
domain-knowledge resources (`specmgr://rsk/tara`,
`specmgr://rsk/risk-matrix`)"

E7. Dependencies:
Current tail:
" and `_packaged_data.py`, the existing `models/md` engine — in particular
`MarkdownSection1WithComment`, `MarkdownSection2`, `MarkdownSection3`,
the generic `list[MarkdownStr]` engine (`process_list_field`), and the
regex `@alias` heading-constraint mechanism (`AliasType.REGEX` +
`match_alias`'s `re.fullmatch`; precedents: `tsk`'s free-form `### `
`UpdateEntry`, ADR's numbered `### Option N:` headings)

- Blocks: None identified yet"
  New:
  " and `_packaged_data.py`, the feat-13 paging machinery
  (`general/tools/_paging.py`, `general/models/summary.py::DocSummary`,
  `general/models/__init__.py::PagedResult`, ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13), the existing `models/md` engine —
  in particular
  `MarkdownSection1WithComment`, `MarkdownSection2`, `MarkdownSection3`,
  the generic `list[MarkdownStr]` engine (`process_list_field`), and the
  regex `@alias` heading-constraint mechanism (`AliasType.REGEX` +
  `match_alias`'s `re.fullmatch`; precedents: `tsk`'s free-form `### `
  `UpdateEntry`, ADR's numbered `### Option N:` headings)
- Blocks: None identified yet"

E8. Design Notes — List summary bullet (as drafted above).

E9. Design Notes — new Domain-knowledge resources bullet (insert after the List summary bullet, before the Prompt naming bullet).

E10. Phase 1 — add Task 1.5 after the Task 1.4 line.
Task 1.4's current text ends with: " depends on: Task 1.3 — status: not-started", followed by "#### Phase 2: Pydantic Models & Parser (commit 2)". Insert the new task in between.

E11. Phase 2 Task 2.3 (residual fields + "for the `list_rsk` tool").

E12. Phase 3 renumbering + new tasks:

- Current 3.14 (server.py) → renumber to 3.17 and update dependency "Tasks 3.2-3.13" → "Tasks 3.2-3.16"
- Current 3.15 (tests) → renumber to 3.18, "Tasks 3.1-3.14" → "Tasks 3.1-3.17"
- Insert new 3.14 (list_rsk), 3.15 (tara/risk-matrix resources), 3.16 (their tests) after the current 3.13.

The current 3.13/3.14/3.15 text:
"- [ ] Task 3.13: `rsk/prompts/create_risk.py` + `update_risk.py` — narrate
the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)
— depends on: Tasks 3.3, 3.4, 3.5, 3.8, 3.10 — status: not-started

- [ ] Task 3.14: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers) —
  depends on: Tasks 3.2-3.13 — status: not-started
- [ ] Task 3.15: `tests/rsk/tools/...`, `tests/rsk/resources/...`,
  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/ resources/`/`tests/tsk/prompts/` layout — depends on: Tasks 3.1-3.14 —
  status: not-started"

New:
"- [ ] Task 3.13: ... (unchanged)

- [ ] Task 3.14: `rsk/tools/list_rsk.py` — the paged `list_rsk` tool
  (`max_results`/`offset` -> `PagedResult[RskSummary]`, mirroring
  `tsk/tools/list_tsk.py` + feat-13's shared paging contract, with the
  residual-risk fields from Task 2.3) — depends on: Tasks 3.1, 2.3 — status: not-started
- [ ] Task 3.15: `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix`
  resources (`rsk/resources/tara.py`, `rsk/resources/risk_matrix.py` — raw
  packaged markdown via `read_packaged_text`, mirroring
  `tsk/resources/tsk_example.py`) + packaged copies `rsk/data/ rsk_tara.md`/`rsk_risk_matrix.md` from the Phase 1 drafts (Task 1.5) —
  depends on: Tasks 1.5, 3.1 — status: not-started
- [ ] Task 3.16: `tests/rsk/tools/test_list_rsk.py` (paging contract,
  clamping, skip-on-broken-file, residual fields present and correct) +
  `tests/rsk/resources/test_tara.py`/`test_risk_matrix.py` (registered,
  packaged content resolves, `rsk_risk_matrix.md`'s documented zone
  thresholds match the model's derived-`level` mapping) — depends on:
  Tasks 3.14, 3.15 — status: not-started
- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers) —
  depends on: Tasks 3.2-3.16 — status: not-started
- [ ] Task 3.18: `tests/rsk/tools/...`, `tests/rsk/resources/...`,
  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/ resources/`/`tests/tsk/prompts/` layout (Task 3.16's tests live under the
  same tree) — depends on: Tasks 3.1-3.17 — status: not-started"

Wait — task numbering: the old 3.14's text is "Task 3.14: add `rsk` to server.py..." and I'm replacing the whole 3.13-3.15 block with the new 3.13 (unchanged prefix)… I'll replace the block from "- [ ] Task 3.14: add `rsk`" through the end of the old 3.15 with the new tasks 3.14-3.18. oldString = the entire old 3.14 + 3.15 text. newString = new 3.14, 3.15, 3.16, 3.17, 3.18.

Also, ACC-004 mentions "every listed tool" — fine.

E13. REQ-007:
Current:
"- [ ] REQ-007: Packaged example/template/schema data (`rsk/data/`) via the
existing generic `general/tools/_packaged_data.py`, with the matching
`pyproject.toml` package-data entry, pre-commit hook, and CI step"
New:
"- [ ] REQ-007: Packaged example/template/schema data plus the two
domain-knowledge documents (`rsk/data/`: `rsk_example.md`,
`rsk_template.md`, `rsk_schema.json`, `rsk_tara.md`,
`rsk_risk_matrix.md`) via the existing generic
`general/tools/_packaged_data.py`, with the matching `pyproject.toml`
package-data entry, pre-commit hook, and CI step"

E14. Current Status — extend the revision list.
Current:
"4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead
of TARRA, cause/trigger/consequence split into separate sections,
assessment values moved from list items to H3 headings with regex `@alias`
constraints, execution pinned to the Orchestrator/Phase-Implementer
pattern). Awaiting final review before Phase 1 starts."
New:
"4-phase/4-commit shape; revised 2026-08-24 per user feedback (TARA instead
of TARRA, cause/trigger/consequence split into separate sections,
assessment values moved from list items to H3 headings with regex `@alias`
constraints, execution pinned to the Orchestrator/Phase-Implementer
pattern, two domain-knowledge resources `specmgr://rsk/tara` +
`specmgr://rsk/risk-matrix` added, `list_rsk` summary lines carry the
residual-risk coordinates, listing corrected to the paged `list_rsk` tool
per feat-13). Awaiting final review before Phase 1 starts."

E15. Recent Updates — new top entry.

E16. Decisions Made — new entry at the end.

Also, the "List summary" design-notes bullet mentions `specmgr://rsk/list` — covered by E8.

Also — does the plan anywhere else mention `specmgr://rsk/list`? Search: the REQ-005 line (E2), the out-of-scope bullet (E5), the design-notes list bullet (E8), Task 2.3 (E11). Anywhere else? I'll grep after the edits.

Also update the issue #15 body.

Timestamp: I'll get it now.

One more check — the user's wording "list_risk resource": I'll note in my reply that the plan/tool follows the feat-13 convention and is named `list_rsk` (like `list_tsk`), and that it's a paged tool, not a resource — flagging this correction.

OK, let me run all the edits in a parallel batch (disjoint regions). First, get the timestamp.

I've checked both precedents — and this also reveals a stale part of my plan: **feat-13 removed the `specmgr://<domain>/list` resource and replaced it with a paginated `list_<domain>` tool** (ADR ec9f5262). Therefore, the "list_risk resource" actually becomes a paginated `list_rsk` tool (following the naming convention of `list_tsk`). And `iso25010` gives us a precedent for domain knowledge resources. I'll now update the plan:

**Tool: bash**

**Input:**

```json
{
  "command": "date +%Y-%m-%dT%H:%M:%S%:z"
}
```

**Output:**

```
2026-08-24T14:09:54+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 228.4s)

_Thinking:_

Alright, let's do all the edits. Batch 1: REQ-004, REQ-005, REQ-007, ACC-004, ACC-005, Scope bullets (2 items).

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_rsk`,\n  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,\n  `set_status_rsk`, `delete_rsk` (stub), `validate_rsk`, `get_rsk`",
  "newString": "- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface plus the\n  feat-13 listing contract: `parse_rsk`, `get_rsk_example`,\n  `get_rsk_template`, `create_rsk`, `update_rsk`, `set_status_rsk`,\n  `delete_rsk` (stub), `validate_rsk`, `get_rsk`, and the paged `list_rsk`\n  tool (`max_results`/`offset`, `PagedResult[RskSummary]`, skip-and-\n  continue on unparseable files — mirroring `tsk/tools/list_tsk.py` and\n  feat-13's shared paging contract)"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://rsk/list`,\n  `/example`, `/schema`, `/template`",
  "newString": "- [ ] REQ-005: MCP resources: `specmgr://rsk/example`, `/schema`,\n  `/template` (no `/list` — listing is the paged `list_rsk` tool per\n  feat-13 / ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), plus two new static\n  domain-knowledge resources: `specmgr://rsk/tara` (what TARA is, the four\n  valid strategy words, when and how to apply each) and\n  `specmgr://rsk/risk-matrix` (the 5x5 matrix: scale anchors, zone table,\n  product thresholds — what 'high risk' and 'low risk' mean)"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] REQ-007: Packaged example/template/schema data (`rsk/data/`) via the\n  existing generic `general/tools/_packaged_data.py`, with the matching\n  `pyproject.toml` package-data entry, pre-commit hook, and CI step",
  "newString": "- [ ] REQ-007: Packaged example/template/schema data plus the two\n  domain-knowledge documents (`rsk/data/`: `rsk_example.md`,\n  `rsk_template.md`, `rsk_schema.json`, `rsk_tara.md`,\n  `rsk_risk_matrix.md`) via the existing generic\n  `general/tools/_packaged_data.py`, with the matching `pyproject.toml`\n  package-data entry, pre-commit hook, and CI step"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`), with\n  `create_rsk`/`update_rsk` validating body-only content the same way\n  `create_req`/`update_req`/`create_tsk`/`update_tsk` do",
  "newString": "- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`), with\n  `create_rsk`/`update_rsk` validating body-only content the same way\n  `create_req`/`update_req`/`create_tsk`/`update_tsk` do, and `list_rsk`\n  returning one-line `RskSummary` entries that include the residual-risk\n  fields (`residual_probability`/`residual_impact`/`residual_product`)\n  with correct paging/clamping per the feat-13 contract"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`)",
  "newString": "- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and\n  registered (confirmed present in regenerated `docs/MCP.md`), with\n  `specmgr://rsk/tara` documenting exactly the four valid TARA words and\n  `specmgr://rsk/risk-matrix`'s zone table matching the model's\n  derived-`level` mapping (threshold test)"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- Full MCP surface (tools/resources/prompts/packaged data) mirroring\n  `req`/`tsk`\n- Tests mirroring `tests/req/`'s and `tests/tsk/`'s layout and coverage",
  "newString": "- Full MCP surface (tools/resources/prompts/packaged data) mirroring\n  `req`/`tsk`, including the feat-13 paged `list_rsk` tool and the two new\n  domain-knowledge resources (`specmgr://rsk/tara`,\n  `specmgr://rsk/risk-matrix`)\n- Tests mirroring `tests/req/`'s and `tests/tsk/`'s layout and coverage"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- Aggregated, register-wide views (e.g. a combined risk-matrix chart across\n  all `rsk` documents) — `RskSummary` (see `specmgr://rsk/list`) carries\n  `initial_level`/`residual_level`/`strategy` per document precisely so such a\n  view can be built later without reading each document",
  "newString": "- Aggregated, register-wide views (e.g. a combined risk-matrix chart across\n  all `rsk` documents) — `RskSummary` (one line of the paged `list_rsk`\n  tool) carries `initial_level`/`residual_level`/`strategy` plus the\n  residual-risk coordinates per document precisely so such a view can be\n  built later without reading each document"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 251.2s)

_Thinking:_

Batch 2: Dependencies, Design Notes (list summary items + new domain knowledge items), Phase 1 Task 1.5, Phase 2 Task 2.3, Phase 3 renumbering + new tasks.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  (id-based reads as a tool, not a resource), `general/tools/_doc_paths.py`\n  and `_packaged_data.py`, the existing `models/md` engine — in particular",
  "newString": "  (id-based reads as a tool, not a resource), ADR\n  ec9f5262-9912-49d0-903f-fcfb54f28c13 + the feat-13 paging machinery\n  (`general/tools/_paging.py`, `general/models/summary.py::DocSummary`,\n  `PagedResult`), `general/tools/_doc_paths.py` and `_packaged_data.py`,\n  the existing `models/md` engine — in particular"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- **List summary** — `RskSummary` (for `specmgr://rsk/list`) carries\n  `id`/`title`/`status` plus `initial_level`, `residual_level`, `strategy`,\n  and the first `scope` entry, so a register-wide risk-matrix view can be\n  built from the listing alone.",
  "newString": "- **List summary** — `RskSummary` (one line of the paged `list_rsk` tool's\n  output — no `specmgr://rsk/list` resource, per feat-13) carries\n  `id`/`title`/`status`/`ref` plus `initial_level`, `residual_level`,\n  `strategy`, the first `scope` entry, and the residual-risk coordinates\n  `residual_probability`, `residual_impact`, and `residual_product` (the\n  risk product, probability x impact — the matrix coordinate that\n  determines the residual zone), so a register-wide risk-matrix view can\n  be built from the listing alone.\n\n- **Domain-knowledge resources** — `specmgr://rsk/tara` and\n  `specmgr://rsk/risk-matrix` are static packaged markdown documents,\n  served as raw text (`text/markdown`, mirroring\n  `specmgr://tsk/example`/`/template`) rather than parsed into structured\n  models — the audience is an LLM agent that needs to read guidance, not\n  code that needs data (`specmgr://iso25010`'s structured parse is the\n  precedent for machine-readable reference data; these are prose). Content\n  is drafted in Phase 1 from this plan's Design Notes, so the TARA words\n  and the zone table have a single source of truth:\n  - `rsk_tara.md` — what TARA is (Transfer, Accept, Reduce, Avoid), the\n    four valid `## Strategy` words verbatim (exactly the model's closed\n    set), when and how to apply each (low probability / high impact ->\n    transfer; high / high -> avoid; high probability / low impact ->\n    reduce; low / low -> accept), and how the strategy interacts with\n    `## Mitigation` and the frontmatter `status` vocabulary\n  - `rsk_risk_matrix.md` — the probability/impact scale anchors (1 = rare\n    ... 5 = almost certain; 1 = negligible ... 5 = severe), the 5x5 zone\n    table, the product thresholds (1-4 low, 5-9 medium, 10-14 high,\n    15-25 very high) — i.e. what 'high risk' and 'low risk' mean — and the\n    initial/residual reading rule (a `reduce` strategy implies\n    residual < initial)\n  A test guards the documented zone thresholds against the model's\n  derived-`level` mapping (ACC-005)."
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  set, `Scope` >=1, `Tags`/`Owner`/`More\n  Information` absent-vs-present —\n  depends on: Task 1.3 — status: not-started",
  "newString": "  set, `Scope` >=1, `Tags`/`Owner`/`More\n  Information` absent-vs-present —\n  depends on: Task 1.3 — status: not-started\n- [ ] Task 1.5: Draft the two packaged domain-knowledge documents\n  (`rsk_tara.md`, `rsk_risk_matrix.md`) from this plan's Design Notes —\n  TARA: what/when/how for each of the four valid words, interaction with\n  `## Mitigation`/`status`; risk matrix: scale anchors, zone table,\n  product thresholds, initial/residual reading rule — placed in this\n  feature folder until Phase 3 packages them into `rsk/data/` (mirroring\n  the `rsk_reference.md` location convention) — depends on: Task 1.2 —\n  status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry, for the\n  `specmgr://rsk/list` resource) — depends on: Task 2.1 — status:\n  not-started",
  "newString": "- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the\n  residual-risk coordinates `residual_probability`/`residual_impact`/\n  `residual_product` (risk product), for the `list_rsk` tool) — depends on:\n  Task 2.1 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 3.14: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers) —\n  depends on: Tasks 3.2-3.13 — status: not-started\n- [ ] Task 3.15: `tests/rsk/tools/...`, `tests/rsk/resources/...`,\n  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/\n  resources/`/`tests/tsk/prompts/` layout — depends on: Tasks 3.1-3.14 —\n  status: not-started",
  "newString": "- [ ] Task 3.14: `rsk/tools/list_rsk.py` — the paged `list_rsk` tool\n  (`max_results`/`offset` -> `PagedResult[RskSummary]`, mirroring\n  `tsk/tools/list_tsk.py` + feat-13's shared paging contract, with the\n  residual-risk fields from Task 2.3) — depends on: Tasks 3.1, 2.3 —\n  status: not-started\n- [ ] Task 3.15: `specmgr://rsk/tara` + `specmgr://rsk/risk-matrix`\n  resources (`rsk/resources/tara.py`, `rsk/resources/risk_matrix.py` — raw\n  packaged markdown via `read_packaged_text`, mirroring\n  `tsk/resources/tsk_example.py`) + packaged copies `rsk/data/\n  rsk_tara.md`/`rsk_risk_matrix.md` from the Phase 1 drafts (Task 1.5) —\n  depends on: Tasks 1.5, 3.1 — status: not-started\n- [ ] Task 3.16: `tests/rsk/tools/test_list_rsk.py` (paging contract,\n  clamping, skip-on-broken-file, residual fields present and correct) +\n  `tests/rsk/resources/test_tara.py`/`test_risk_matrix.py` (registered,\n  packaged content resolves from the source tree, `rsk_risk_matrix.md`'s\n  documented zone thresholds match the model's derived-`level` mapping) —\n  depends on: Tasks 3.14, 3.15 — status: not-started\n- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers) —\n  depends on: Tasks 3.2-3.16 — status: not-started\n- [ ] Task 3.18: `tests/rsk/tools/...`, `tests/rsk/resources/...`,\n  `tests/rsk/prompts/...` mirroring `tests/tsk/tools/`/`tests/tsk/\n  resources/`/`tests/tsk/prompts/` layout (Task 3.16's tests live under the\n  same tree) — depends on: Tasks 3.1-3.17 — status: not-started"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 233.8s)

_Thinking:_

Batch 3: current status, recent updates (new entry), decisions made (new entry). Also, update the issue body.

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "assessment values moved from list items to H3 headings with regex `@alias`\nconstraints, execution pinned to the Orchestrator/Phase-Implementer\npattern). Awaiting final review before Phase 1 starts.",
  "newString": "assessment values moved from list items to H3 headings with regex `@alias`\nconstraints, execution pinned to the Orchestrator/Phase-Implementer\npattern, two domain-knowledge resources `specmgr://rsk/tara` +\n`specmgr://rsk/risk-matrix` added, `list_rsk` summary lines carry the\nresidual-risk coordinates, and listing corrected to the paged `list_rsk`\ntool per feat-13). Awaiting final review before Phase 1 starts."
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "### Recent Updates\n\n#### 2026-08-24T13:40:33+02:00 (newest)",
  "newString": "### Recent Updates\n\n#### 2026-08-24T14:09:54+02:00 (newest)\n\n- Completed: added two requirements per user feedback — (1) new static\n  domain-knowledge resources `specmgr://rsk/tara` (what TARA is, the four\n  valid words, when and how to apply each) and `specmgr://rsk/risk-matrix`\n  (scale anchors, zone table, product thresholds — what 'high risk' and\n  'low risk' mean), raw packaged markdown, content drafted in Phase 1\n  (Task 1.5) from the plan's Design Notes with a threshold test against the\n  model's derived-`level` mapping; (2) the `list_rsk` summary lines now\n  carry the residual risk's `residual_probability`/`residual_impact`/\n  `residual_product` (risk product). Also corrected the plan against\n  feat-13 (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13): there is no\n  `specmgr://rsk/list` resource — listing is the paged `list_rsk` tool\n  (REQ-004/REQ-005, Task 2.3, new Tasks 3.14-3.16, old Tasks 3.14/3.15\n  renumbered to 3.17/3.18). GitHub issue #15 updated to match\n- Next: user review; then Phase 1 (Specification)\n- Notes: see the two new Decisions Made entries below\n\n#### 2026-08-24T13:40:33+02:00"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  `phase-implementer` agent type is purpose-built for exactly this (one\n  phase of a `.specmgr/feat/<id>/README.md` plan, driven by an orchestrator,\n  not intended for direct selection), and no separate `phase-orchestrator`\n  agent type is registered in this environment, so the orchestrator role is\n  fulfilled by the main session. Replaces the `implementation-specialist`\n  delegation named in the original Execution approach (the pattern\n  `feat-10` used).",
  "newString": "  `phase-implementer` agent type is purpose-built for exactly this (one\n  phase of a `.specmgr/feat/<id>/README.md` plan, driven by an orchestrator,\n  not intended for direct selection), and no separate `phase-orchestrator`\n  agent type is registered in this environment, so the orchestrator role is\n  fulfilled by the main session. Replaces the `implementation-specialist`\n  delegation named in the original Execution approach (the pattern\n  `feat-10` used).\n- **2026-08-24**: Two static domain-knowledge resources —\n  `specmgr://rsk/tara` and `specmgr://rsk/risk-matrix` — are served as raw\n  packaged markdown (`text/markdown`) rather than parsed into structured\n  models — rationale: user requirement (the resources shall help the agent\n  understand what TARA is, when and how to use it, and what 'high risk' /\n  'low risk' means); the audience is an LLM agent reading guidance, which\n  mirrors the `specmgr://tsk/example`/`/template` text resources, while\n  `specmgr://iso25010`'s structured parse is the precedent for\n  machine-readable reference data. Content is drafted in Phase 1 (Task 1.5)\n  from this plan's Design Notes so the TARA words and the zone table have a\n  single source of truth; a test guards the documented zone thresholds\n  against the model's derived-`level` mapping.\n- **2026-08-24**: `RskSummary` (one line of the paged `list_rsk` tool)\n  carries the residual risk's `residual_probability`/`residual_impact`/\n  `residual_product` in addition to `initial_level`/`residual_level`/\n  `strategy`/first `scope` entry — rationale: user requirement (\"impact,\n  probability, risk product for the residual risk\"); `residual_product`\n  (probability x impact) is the matrix coordinate that determines the\n  residual zone, so a register-wide risk-matrix view can be built from the\n  listing alone.\n- **2026-08-24**: Corrected REQ-005 against feat-13 — no\n  `specmgr://rsk/list` resource; listing is the paged `list_rsk` tool\n  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: MCP resources cannot take\n  arbitrary parameters, and `max_results`/`offset` paging needs exactly\n  that) — rationale: the plan originally mirrored feat-10's (pre-feat-13)\n  resource list; verified against `tsk/tools/list_tsk.py` and\n  `tsk/resources/` (no list resource) before correcting."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 204.6s)

_Thinking:_

Next, I'll update the body of GitHub issue #15 to match the new resource and the list fields. I'll update the "resources" line and add notes regarding the list summary.

Now sync issue #15 with the additions:

**Tool: write**

**Input:**

```json
{
  "content": "We create a new artifact type `Risk`:\n\n* abbreviation `rsk`\n* sub-folder as `req`/`tsk`\n* resources: same as `req` — but no `/list` (listing is the paged `list_rsk` tool, per feat-13 / ADR ec9f5262), plus two static domain-knowledge resources: `specmgr://rsk/tara` (what TARA is, the four valid strategy words, when and how to apply each) and `specmgr://rsk/risk-matrix` (the 5x5 matrix: scale anchors, zone table, product thresholds — what 'high risk' and 'low risk' mean)\n* tools: same as `req`, plus the paged `list_rsk` tool (feat-13 listing contract) — each summary line additionally carries the residual risk's `impact`, `probability`, and risk product (`probability x impact`)\n* prompts: `create_risk` and `update_risk`\n\nAttributes:\n\n* frontmatter `status`: `open` / `mitigating` / `accepted` / `occurred` / `closed` / `dropped` (default `open`)\n* H1 title, optional leading comment\n* `## Cause` (mandatory): root condition — why the risk exists\n* `## Trigger` (mandatory): what sets the risk event in motion\n* `## Consequence` (mandatory): what happens if the risk event occurs\n* `## Scope` (mandatory, list): which system/component is affected\n* `## Initial Assessment` (mandatory): 5x5 risk matrix BEFORE mitigation — probability 1..5 and impact 1..5 as H3 headings (`### Probability 4`, `### Impact 3`), derived level: low / medium / high / very high\n* `## Strategy` (mandatory): TARA — `transfer` / `accept` / `reduce` / `avoid`\n* `## Mitigation` (mandatory): treatment measures (\"none\" if strategy is `accept`)\n* `## Residual Assessment` (mandatory): 5x5 risk matrix AFTER mitigation (residual risk)\n* `## Owner` (optional): responsible person/role\n* `## Tags` (optional, list): free-form tags\n* `## More Information` (optional): free-form\n\nThis artifact is needed for risk registers in system specifications: risks with an\nexplicit before/after mitigation 5x5 assessment (residual risk) and a TARA response\nstrategy, kept as first-class managed artifacts alongside requirements and use cases.\n",
  "filePath": "/tmp/opencode/rsk-issue-body.md"
}
```

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 194.3s)

_Thinking:_

Wait — regarding the H3 heading details I added to the issue body: this is consistent with the revised schema (value inside the heading). Good.

Alright, let me apply the issue edit and do a final consistency check: grep the README for any remaining old references (specmgr://rsk/list, old task numbers 3.14/3.15 within cross-references, "list_risk").

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue edit 15 --body-file /tmp/opencode/rsk-issue-body.md",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/15

```

**Tool: grep**

**Input:**

```json
{
  "include": "README.md",
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk",
  "pattern": "specmgr://rsk/list|list_risk|Tasks 3\\.1-3\\.14|Tasks 3\\.2-3\\.13"
}
```

**Output:**

```
Found 4 matches
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md:
  Line 305:   output — no `specmgr://rsk/list` resource, per feat-13) carries

  Line 471: - [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources

  Line 565:   `specmgr://rsk/list` resource — listing is the paged `list_rsk` tool

  Line 731:   `specmgr://rsk/list` resource; listing is the paged `list_rsk` tool

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 210.4s)

_Thinking:_

Line 471 is an actual oversight: Task 3.10 still lists the `specmgr://rsk/list` resource. This needs to be fixed — the current Task 3.10:

"- [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources
(packaged `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`) —
depends on: Task 3.1, Task 2.5 — status: not-started"

→ Should be as follows:
"- [ ] Task 3.10: `specmgr://rsk/schema` resource
(packaged `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`;
no `/list` resource — listing is the `list_rsk` tool, Task 3.14) —
depends on: Task 3.1, Task 2.5 — status: not-started"

The other 3 lines (305, 565, 731) are intentional correction references (stating that no such resource exists). No problem there.

Wait — let me also check Task 3.11: "`specmgr://rsk/example` and `specmgr://rsk/template` resources — depends on: Task 3.9" — no problem.

Also checking ACC-005/REQ-005: currently there's no /list — good. And Task 3.16 references tests/rsk/resources/test_tara.py etc. No problem.

Fix Task 3.10.

One real straggler — Task 3.10 still lists the removed `/list` resource (the other three matches are the intentional "no such resource" corrections):

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 3.10: `specmgr://rsk/list` and `specmgr://rsk/schema` resources\n  (packaged `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`) —\n  depends on: Task 3.1, Task 2.5 — status: not-started",
  "newString": "- [ ] Task 3.10: `specmgr://rsk/schema` resource (packaged\n  `rsk/data/rsk_schema.json`, mirroring `specmgr://req/schema`; no `/list`\n  resource — listing is the `list_rsk` tool, Task 3.14) — depends on:\n  Task 3.1, Task 2.5 — status: not-started"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 223.6s)

_Thinking:_

Complete. Let me summarize what was added/modified:

1. **Two new domain knowledge resources** (`specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`) — raw packaged Markdown, with content drafted in Phase 1 (Task 1.5) from the Design Notes in the plan (single source of truth), plus a threshold test that matches the documented zone table against the model's derived-level mapping.

2. **`list_rsk` summary fields** — `residual_probability`, `residual_impact`, `residual_product` (risk product) added to `RskSummary`.

3. **Fix discovered along the way**: feat-13 removed `specmgr://<domain>/list` resources in favor of the paginated `list_<domain>` tools (ADR ec9f5262) — so the "list_risk resource" became the paginated `list_rsk` tool (Task 3.14). The plan's REQ-005 was outdated on this point. Updated the plan + issue.

Task list changes: new 1.5, new 3.14–3.16, renumbered old 3.14/3.15 → 3.17/3.18, Task 2.3 expanded, Task 3.10 fixed. Issue #15 updated.

Keep the reply concise.

Done. Both requirements are in the plan, plus one correction I found along the way:

**New: domain-knowledge resources**

- `specmgr://rsk/tara` — what TARA is, the four valid words verbatim, when/how to apply each (low p / high i → transfer, high/high → avoid, high p / low i → reduce, low/low → accept), interaction with `## Mitigation` and `status`.
- `specmgr://rsk/risk-matrix` — scale anchors (1 = rare … 5 = almost certain; 1 = negligible … 5 = severe), the 5x5 zone table, product thresholds (1–4 low, 5–9 medium, 10–14 high, 15–25 very high), and the initial/residual reading rule.
- Served as **raw packaged markdown** (`text/markdown`, like `tsk/example`) rather than a structured parse — the audience is an LLM agent reading guidance. Content is drafted in Phase 1 (new Task 1.5) from the plan's Design Notes so the TARA words and zone table have a single source of truth; a test (Task 3.16) guards the documented thresholds against the model's derived-`level` mapping.

**`list_rsk` summary fields**

- `RskSummary` gains `residual_probability`, `residual_impact`, `residual_product` (the risk product, probability × impact) alongside the existing `initial_level`/`residual_level`/`strategy`/first-scope (Task 2.3, ACC-004).

**Correction: it's a tool, not a resource**

- feat-13 (ADR ec9f5262) already removed `specmgr://<domain>/list` resources in favor of paged `list_<domain>` **tools** — MCP resources can't take `max_results`/`offset` parameters. So the "list_risk resource" becomes the paged `list_rsk` tool (new Task 3.14, mirroring `tsk/tools/list_tsk.py`). My plan's REQ-005 still mirrored the pre-feat-13 `req` surface; now fixed, including Task 3.10 which listed the removed `/list` resource. Old Tasks 3.14/3.15 renumbered to 3.17/3.18.

Issue #15 updated to match. Task list is now: 1.1–1.5, 2.1–2.6, 3.1–3.18, 4.1–4.4.

______________________________________________________________________

## User

anything else, before we can implement?

______________________________________________________________________

## Assistant (Plan · qwen3.8:27b-nvfp4-896k · 319.5s)

_Thinking:_

The user is asking, "Before we can start implementation, is there anything else?" — and I'm in plan mode (read-only). So I should audit the plan for unresolved items, gaps, or open questions before Phase 1 begins.

Let me think about what's still unresolved or worth verifying (all read-only checks):

01. **Base directory for RSK documents** — where do `rsk` documents get placed? `general/tools/_doc_paths.py` — each domain has a configured base directory (environment variable?). For example, `SPECMGR_ADR_DIR`, `SPECMGR_REQ_DIR`, `SPECMGR_TSK_DIR`, `SPECMGR_QA_DIR`, `SPECMGR_UC_DIR`? I need to check `_doc_paths.py` to see how the base directory is configured (env vars via python-dotenv?), and record that `rsk` requires a base directory config (env var + default + `.env.example`?). This is a real gap that should be verified — feat-10/feat-13 tasks reference `general/tools/_doc_paths.py` as already generalized. Let me check what's in there and whether an environment variable for the rsk directory is needed.

02. **`server.py` docstring** — per AGENTS.md, the docstring of server.py is the authoritative list of all resources/tools/prompts and must be updated when adding/removing/renaming. My task list doesn't explicitly include updating the server.py docstring! Task 3.17 (currently 3.17) is only "add `rsk` to the domain import line in `server.py`". The docstring update should be part of that task or a separate task. Let me check whether the feat-10/feat-13 plans included it… Actually, docs/MCP.md is auto-generated, and the docstring is hand-maintained. Task 3.17 should be amended to include the docstring update. Worth pointing out.

03. **`_doc_paths.py`/`_paths.py` for rsk** — Task 3.1 covers `rsk/tools/_paths.py` etc. as a thin wrapper over `general/tools/_doc_paths.py`. But does `general/tools/_doc_paths.py` need a new entry for the rsk base directory (function `rsk_base_dir()` or env var `SPECMGR_RSK_DIR`)? Let me read `_doc_paths.py` to check the shape.

04. **Environment configuration** — the project uses `python-dotenv`. There may be a `.env.example` or documentation about the base directory. Check.

05. **`whitelist.py` for vulture** — if I add a `_validate_*` method, a whitelist entry is needed. For rsk, the assessment no longer uses the TaskItem pattern (value-in-heading is enforced by parse-time match_alias — is an eager validator even needed in the first place? The computed `value: int` field is still lazy! `match_alias` enforces the *format* of the heading at parse time, and the computed `value` field is only evaluated on access. But since the format is enforced at parse time, `value` cannot be invalid — the digit always exists and is in range. So the TaskItem-style eager validation problem doesn't apply: the heading constraint guarantees the validity of the computed field. But wait — direct Python construction (e.g., `Assessment(probability=Probability())`)? The same concern as feat-10's `RecentUpdates(updates=[])` (direct construction bypassing from_text) applies. `create_rsk`/`update_rsk` always go through parse (from_text), so it's fine. Still, a `model_validator` may be needed on `Risk` to force evaluation of `level` (product of two computed values) — `level` is a computed field on `Assessment` derived from the computed `value` fields; if the values are valid (format-enforced at parse time), level is always computable. Direct construction of `Assessment` with invalid leaves — the leaves are sections, and constructing them directly without `_value` would… `.text` returns "" and `value` extraction would fail at dump time, not at construction time. Hmm — is a model-level validator still prudent? The feat-10 lesson was about the "successful construction is validation" convention for tools. For rsk, tools always parse from text, so the alias check happens at parse time. Direct Python construction isn't a tool path. I think we can record this as a design consideration: a `model_validator(mode="after")` on `Assessment` that forces `.value` on both children (cheap, consistent with convention). It's not a blocker; can be decided in Phase 1. Worth mentioning as an open micro-decision? Maybe I can fold it into the task notes. Let me mention it briefly.

06. **Package data glob in pyproject** — Task 3.12 covers it. The glob for `rsk`'s `data/*.md` covers tara/risk-matrix. Good.

07. **`specmgr schema` registry + pre-commit/CI** — covered in Task 2.5/3.12.

08. **Branch/worktree state** — currently on `feat-15-add-artifact-type-risk` (from dev). Untracked feature folder. Working tree clean otherwise? `git status` showed only untracked feature folders. Also: the plan file is untracked — per AGENTS.md, pylint only sees tracked files, but the README is markdown, not Python. Pre-commit hooks scope to changes in src/tests; no issue. Should the feature folder be committed before Phase 1? feat-10's Phase 1 commit included the reference document… The plan is the work unit; committing the plan first is good practice (the feat-10 branch had plan commits). My "one Conventional Commit per phase" — Phase 1's commit would include the plan file if it's uncommitted. Better: commit the plan (docs commit) now as baseline, so phase commits are clean. Point to raise: propose a `docs(feat-15): add risk artifact type feature plan` commit before Phase 1. But plan mode — I can't commit now; I'll just note it.

09. **GitHub issue #15** — open, linked. Good.

10. **`docs/adr/README.md` TOC / ADR** — no new ADR is planned. Fine.

11. **CHANGELOG** — feat-10's decision: new domain features don't get a CHANGELOG entry (only at version-bump time). Already decided by precedent. Fine.

12. **`RskSummary` base** — subclasses `DocSummary` (general/models/summary.py) per feat-13. Task 2.3 says "RskSummary with initial_level/..." — should note that it subclasses `DocSummary` like TskSummary does. Minor; the implementer can mirror tsk.

13. **Base directory for the rsk register** — this is the biggest potential gap. Let me read `general/tools/_doc_paths.py` to check how the base directory is derived (env var? default path?).

14. **`implement_task`-equivalent prompt** — not needed for rsk (issue only specifies create_risk/update_risk). Fine.

15. **`question`/clarification** — the plan says "user review; then Phase 1" — the user is effectively reviewing now. Remaining open questions to the user:

    - Confirm commit of the plan baseline before Phase 1 (conventional? feat-10 committed the plan within a phase commit? Actually feat-10: "Phase 1 (9ace8dd) and Phase 2 (1cb9ffe) committed" — the plan file itself was probably included in the Phase 1 commit or committed earlier. Let me quickly check git log for when the feat-10 README was committed… I can read the git log (read-only). Check: `git log --oneline -- .specmgr/feat/feat-10-add-artifact-type-tasklist/README.md | tail -3` to see the first commit.
    - Anything about the rsk base directory (env var naming, e.g., `SPECMGR_RSK_DIR`).

Let me do read-only checks:

- Read `general/tools/_doc_paths.py`
- Check `.env` / dotenv usage: grep for "SPECMGR\_" env vars in src and .env.example
- git log for when the feat-10 README first appeared (to learn the plan commit convention)
- Check the tail of the server.py docstring for the registration list convention (to confirm docstring update is needed — I already know from AGENTS.md, but confirm it's the docstring, e.g., "the docstring of server.py is the single most authoritative…").

Let me run these in parallel.

Good moment to audit the plan for gaps before implementation. Let me check a few things read-only: how base directories are configured per domain (a likely missing task), the plan-commit convention, and the `server.py` docstring requirement:

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

**Tool: bash**

**Input:**

```json
{
  "command": "git log --oneline --follow --reverse -- .specmgr/feat/feat-10-add-artifact-type-tasklist/README.md | head -3; echo ---; grep -rn \"SPECMGR_\" .env.example .env* 2>/dev/null | head; echo ---; grep -rln \"os.getenv\\|getenv(\" src/biz/dfch/specmgr/general/ | head",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
5985a1d docs(feat-10): plan tsk (TaskList) artifact type feature
c27328b docs(feat-10): fix schema-generation task sequencing
afb1c96 docs(feat-10): mark Phase 1 done, log progress
---
---

```

______________________________________________________________________

## Assistant (Plan · qwen3.8:27b-nvfp4-896k · 359.0s)

_Thinking:_

Good news: `_doc_paths.py` is fully generic — `doc_base_dir("rsk")` returns `{SPECMGR_DOCS_DIR or docs}/rsk`. **No new environment variable or base-directory task is needed.** All that's required is `rsk/tools/_paths.py` calling the generic function with `type_name="rsk"` (Task 3.1 already covers this). No gap.

Plan-commit convention: `docs(feat-10): plan tsk (TaskList) artifact type feature` — the plan README gets its own `docs(feat-NN)` commit first, followed by progress updates (`docs(feat-10): mark Phase 1 done, log progress`). That is, the convention is: commit the plan before Phase 1 (a `docs` commit, not a feat commit). This should be added as an explicit step: commit the current plan state as `docs(feat-15): plan risk (RSK) artifact type feature` before dispatching Phase 1. In feat-10's Execution approach it said "one Conventional Commit per phase" — but in reality there are also docs(feat-10) commits. Let me confirm: 5985a1d (plan commit) → c27328b (docs fix) → afb1c96 (mark Phase 1 done, log progress)… interestingly, "mark Phase 1 done, log progress" is a separate docs commit — so Phase 1's implementation commit (9ace8dd per the README) may have been separate from the progress-log commit. Whatever — the convention is clear: the plan gets a `docs(feat-15):` baseline commit before implementation begins, and progress updates get their own docs commits.

Other gaps to consider:

01. **server.py docstring** — AGENTS.md: "the module docstring of server.py itself is the single most authoritative, currently maintained list of every resource/tool/prompt this MCP server registers — read it before referencing this file for details, and update it every time you add/remove/rename a resource, tool, or prompt." My Task 3.17 only says "add `rsk` to the domain import line of `server.py`". It has to also include updating the docstring. This is a real gap in the task wording. Let me quickly check the shape of the server.py docstring (read the first ~60 lines) to be precise.

02. **`whitelist.py` (vulture)** — if I add private `_validate_*` helpers or module-level functions referenced only from Pydantic decorators, I need whitelist entries. In rsk, the alias-enforced headings mostly eliminate the need for custom validators; still, a new `_ALLOWED_TARA_STRATEGIES` constant etc. may get flagged? No — vulture with --min-confidence 60 against src/ with whitelist.py; constants used in a validator are used. Only dead code gets flagged. The phase-implementer + quality gate (vulture) catches it. No task needed; mention it? The phase gate runs vulture. OK.

03. **`RskSummary` subclasses `DocSummary`** — Task 2.3 should state that (mirror `TskSummary`). Minor wording; the implementer mirrors tsk anyway. Could add to the task wording: "(subclass of `DocSummary` like `TskSummary`)".

04. **Commit order / baseline commit** — add an explicit "before Phase 1" step: commit the plan as `docs(feat-15): plan risk (RSK) artifact type feature` (feat-10 convention: 5985a1d). Also, subsequent phase progress updates: the phase-implementer updates the Progress section as part of the phase (its contract); per feat-10, a separate docs commit for progress? In feat-10: "afb1c96 docs(feat-10): mark Phase 1 done, log progress" — a docs commit after the Phase 1 implementation commit (9ace8dd). So the pattern per phase is: (a) phase-implementer implements + quality gate + updates plan progress; (b) orchestrator verifies; (c) implementation commit (feat(rsk): ...) + docs commit for plan progress? Or combined? feat-10 shows separate commits. My Execution approach says "one Conventional Commit per verified phase" — but the evidence shows an implementation commit and a docs commit. Hmm: let me actually check the sequence: 9ace8dd (Phase 1: Specification), 1cb9ffe (Phase 2), cba8799 (Phase 3) + a Phase 4 commit. And the docs(feat-10) commits — 5985a1d is before 9ace8dd (the plan), afb1c96 is "mark Phase 1 done, log progress" — where does it sit relative to 9ace8dd? `git log --oneline -10` on that branch… let me not dig too deep; I'll note in the plan that the baseline plan commit goes first, and per feat-10 precedent, progress updates may be separate docs commits (leave the details to execution). Actually, to keep the plan clean: add one line to the Execution approach: "Before Phase 1, the current plan state is committed as a `docs(feat-15):` baseline (feat-10 precedent: `5985a1d`), so each phase's commit contains only that phase's changes."

05. **`docs/` drift**: Phase 4 covers it.

06. **Untracked files / working tree**: the feature folder is untracked; everything else is clean. Good.

07. **Issue #15 labels?** Other issues have labels (enhancement, etc.). #10 had none? `gh issue view 10` — I didn't check labels. #14 had none; #7 has "enhancement"; #1/#2 have labels. Not important.

08. **Python version note**: the implementer uses `uv run --frozen` per AGENTS.md. The phase-implementer prompt should include the exact quality-gate commands from AGENTS.md (ruff format --check, ruff check, vulture, unittest). My Execution approach lists the gates. The phase-implementer sub-agent knows the repo (it reads AGENTS.md itself). OK.

09. **One more schema consideration**: `## Scope` as `list[MarkdownStr]` — "which system is affected" — fine. Tags are optional. Fine.

10. **`rsk_reference.md` + example/template docs**: Tasks 1.3 and 3.9. Example/template must be consistent with the schema (TARA words, H3 assessment). The Phase 3 implementer writes from the reference. Fine.

11. **ACC-007 (wheel install check)** — covered.

So the remaining items:

- (a) Task 3.17 wording: also update the server.py module docstring (AGENTS.md requirement).
- (b) Execution approach: baseline `docs(feat-15):` plan commit before Phase 1 (feat-10 precedent).
- (c) Task 2.3: note that `RskSummary` subclasses `DocSummary` (mirror `TskSummary`).
- (d) Possibly an explicit note: no new base-directory/env-var task is needed — `doc_base_dir("rsk")` is generic (`{SPECMGR_DOCS_DIR or docs}/rsk`) — verified; add to Dependencies or Design Notes? This is a verified non-gap; a one-liner in Design Notes prevents the implementer from worrying about it. Add to Task 3.1 wording: "(`doc_base_dir("rsk")` — no new env var; the generic `{SPECMGR_DOCS_DIR or docs}/rsk`)".

Any remaining questions for the user?

- Do you want me to commit the baseline plan commit now? Plan mode → can't commit now. The user said "before we can implement" — so once we exit plan mode, the first action is that commit. I could ask: commit the baseline plan now (as soon as plan mode is lifted) — or should the plan ride along with the Phase 1 commit? Per convention (5985a1d), it's a separate docs commit. I'll present it as the recommended first step and ask for a go-ahead (the go-ahead is implicit in "before we can implement" — they want a list of remaining items).

- Also: any open design items? The only micro-decision I flagged earlier: whether `Assessment` needs an eager `model_validator` given the alias-enforced headings (I argued it's not needed for the tool path; direct construction isn't a supported path). Let me check how `create_tsk`/`update_tsk` handle validation — they parse via the model-layer parse function; direct construction only happens via the tool through parsing. In tsk, the TaskItem problem existed because the computed field (checkbox parsing) could be invalid even with a valid parse… no wait — the reason the TaskItem problem existed was that a malformed marker `- [z] foo` "passed" parsing (the marker is free-form text in commonmark) and the computed field failed silently. In rsk, a malformed heading fails `match_alias` at parse time → so no silent gap. A `model_validator` to force `.level` evaluation would only guard direct Python construction (e.g., `RskDocument(...)` built without parsing), but no tool does that. `create_rsk` builds frontmatter + parses body. So: not needed. But for consistency with the "successful construction is validation" convention (if someone hand-constructs in the future), an after-validator forcing `.value`/`.level` is cheap. I'll mention it as an optional micro-decision for Phase 1, defaulting to "add it, mirroring the TaskItem precedent" — no wait, that contradicts… Let me think about what's cleanest for the plan: record the decision: "No eager-validation `model_validator` is needed on `Assessment`/`Risk` for the tool path, because heading-format violations fail at parse time (`match_alias` assertion in `from_text`) — unlike `TaskItem`, whose marker was free text. (The Phase 1 implementer may still add a low-cost after-validator if the direct-construction path proves to be a concern; the plan's default: no.)" Hmm — this is a design detail; better to keep the plan decisive: "not needed" with rationale. Add as a note in Design Notes (Assessment structure bullet).

Anything else? Let me quickly check the server.py docstring to confirm what needs updating (read the top of server.py).

I've verified `_doc_paths.py` — it's completely generic (`doc_base_dir("rsk")` → `{SPECMGR_DOCS_DIR or docs}/rsk`), so **no base directory / environment variable tasks are needed**. And feat-10's git history shows the plan commit convention (`docs(feat-10): plan tsk...` before implementation). Let me check one more thing — the registration list in the `server.py` docstring that AGENTS.md says must be kept in sync:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py",
  "limit": 80
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py</path>
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
18: """MCP server for ``biz-dfch-specmgr``.
19: 
20: Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).
21: 
22: Registers the following resources and tools so far (plan §8, §9a):
23: 
24: Resources
25: ---------
26: specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
27: specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
28: specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
29:                         (kept in sync with ``docs/req_schema.json``) so it works from a
30:                         real, non-editable install.
31: specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
32: specmgr://req/template -- A requirement template (every field present, placeholder text)
33:                           as raw markdown.
34: specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
35:                         (kept in sync with ``docs/uc_schema.json``) so it works from a
36:                         real, non-editable install.
37: specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
38: specmgr://uc/template -- A use-case template (every field present, placeholder text)
39:                           as raw markdown.
40: specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
41:                         (kept in sync with ``docs/tsk_schema.json``) so it works from a
42:                         real, non-editable install.
43: specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
44: specmgr://tsk/template -- A task list template (every field present, placeholder text)
45:                           as raw markdown.
46: specmgr://qa/schema --  The generated QA JSON Schema, read from a packaged data copy
47:                         (kept in sync with ``docs/qa_schema.json``) so it works from a
48:                         real, non-editable install.
49: specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
50:                         markdown.
51: specmgr://qa/template -- A question-and-answer template (every field present,
52:                           placeholder text) as raw markdown.
53: specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
54:                         characteristics (and sub-characteristics), each with a description.
55: 
56: REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
57: through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
58: UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
59: reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
60: resource either -- id-based reads go through the ``get_tsk`` tool only, and
61: there never was such a resource to remove in the first place. QA has no
62: ``specmgr://qa/{id}`` resource either, for the same reason -- id-based reads go
63: through the ``get_qa`` tool only.
64: 
65: Tools
66: -----
67: ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
68: ``update_section``, ``set_status``, ``option_list``, ``option_create``,
69: ``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
70: Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc``, ``list_uc``, ``get_uc_example``,
71: ``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``
72: (stub, not yet implemented), ``validate_uc``.
73: Requirement tools (``req/tools/``): ``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
74: ``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``, ``delete_req``
75: (stub, not yet implemented), ``validate_req``.
76: Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk``, ``list_tsk``, ``get_tsk_example``,
77: ``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``, ``delete_tsk``
78: (stub, not yet implemented), ``validate_tsk``.
79: QA tools (``qa/tools/``): ``parse_qa``, ``get_qa``, ``list_qa``, ``get_qa_example``,
80: ``get_qa_template``, ``create_qa``, ``update_qa``, ``set_status_qa``, ``delete_qa``

(Showing lines 1-80 of 155. Use offset=81 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Plan · qwen3.8:27b-nvfp4-896k · 358.7s)

_Thinking:_

Confirmed — the docstring in server.py lists all resources and tools (and probably all prompts further down). So Task 3.17 must include updating that docstring (the resource block: rsk's schema/example/template/tara/risk-matrix; the tool block: rsk's 10 tools including list_rsk; the prompt block: create_risk/update_risk; plus a note that "RSK has no specmgr://rsk/{id} resource").

So here's my audit summary. Remaining items before implementation:

**Gaps found (should be fixed in the plan):**

1. **Task 3.17 is missing the docstring update for server.py** — AGENTS.md mandates keeping the module docstring in sync (the authoritative list of resources/tools/prompts). For rsk: 5 resources (schema/example/template/tara/risk-matrix), 10 tools (parse_rsk, get_rsk, list_rsk, get_rsk_example, get_rsk_template, create_rsk, update_rsk, set_status_rsk, delete_rsk stub, validate_rsk), 2 prompts (create_risk, update_risk), plus a note in the "no {id} resource" section.
2. **Baseline commit of the plan before Phase 1** — feat-10's convention: a `docs(feat-10): plan tsk (TaskList) artifact type feature` commit before any implementation commit. Add this to the execution approach.
3. **Task 2.3 wording**: `RskSummary` subclasses `DocSummary` (mirroring `TskSummary`) — explicit.
4. **Task 3.1 wording**: note that no new env var/base-dir wiring is needed — `doc_base_dir("rsk")` is generic (`{SPECMGR_DOCS_DIR or docs}/rsk`) — verified.

**Verified non-gaps:**

- Base dir: generic, no new task needed ✓
- Package data glob `data/*.md` already covers tara/risk-matrix ✓ (Task 3.12)
- Registry-driven docs/mcp-docs/schema CI steps cover rsk ✓ (Phase 4 Task 4.3)
- No new ADR planned ✓
- No CHANGELOG entry (feat-10 precedent) ✓
- Eager-validation validator: not needed for rsk — heading format violations fail at parse time via the `match_alias` assertion inside `from_text` (different from TaskItem, where the marker was free text). Worth recording as a decision so the phase-implementer doesn't blindly copy tsk's `_validate_items_eagerly`.
- Working tree: only the untracked feature folder; branch feat-15-add-artifact-type-risk is ready; issue #15 is open ✓

**Questions for the user (minor):**

- Do you approve the two micro-decisions: (a) no eager-validation validator on Assessment (parse-time alias check is sufficient), (b) baseline docs commit of the plan before Phase 1? Or should I just state them as recommendations and have the user confirm? Plan mode says to ask when weighing tradeoffs. These are trivial; present as recommendations baked into the plan fix.

Since plan mode is read-only, I cannot apply these edits right now. I'll present: audit result + the 4 concrete plan fixes I'm about to make (upon plan mode release) + the 2 recommendations to confirm. Actually — should I ask about the validator decision? It's a substantive design choice. Present it clearly as a recommendation with rationale and ask for confirmation along with the baseline commit. Use the question tool? The user asked "is there anything else before we can implement?" — they're asking for a list. Present the list and ask for confirmation on the 2 judgment items. Use the question tool for the 2 items (multi-question). Hmm, the question tool is good here: (1) eager-validation validator: not needed (recommended) / add it anyway for consistency with tsk; (2) baseline plan commit before Phase 1: yes (recommended) / include it in Phase 1's commit.

But wait — plan mode: I can ask questions. OK.

Actually, let me reconsider (2): is it even a question to begin with? The feat-10 precedent is clear (a separate docs commit). Just recommend it; no question needed. And (1): this is a real design choice worth one question. But honestly, "not needed" is the correct engineering answer with solid rationale, and the plan can just record it as a decision; the user can veto during review. Present both as recommendations in the text and ask a single question to confirm both, or just ask for the go-ahead. Let me structure the reply as follows:

1. The audit results (what's ready)
2. The 4 fixes I'll apply (enumerated, precise)
3. The 2 recommendations requiring approval (validator decision; baseline commit) — use the question tool for these 2 items.

Keep it concise.

The audit found the plan is nearly implementation-ready. Four concrete fixes and two recommendations:

**Fixes I'll apply to the plan (read-only now, applied on exit from plan mode):**

1. **Task 3.17 is incomplete** — it only says "add `rsk` to `server.py`'s import line", but AGENTS.md mandates keeping `server.py`'s module docstring (the authoritative registration list) in sync. It needs: 5 resources (`schema`/`example`/`template`/`tara`/`risk-matrix`), 10 tools (incl. `list_rsk`), 2 prompts, plus the "no `specmgr://rsk/{id}` resource" note (lines 56–63 pattern).
2. **Missing baseline commit step** — feat-10's convention (git history): the plan gets its own `docs(feat-10): plan tsk (TaskList) artifact type feature` commit *before* any implementation commit. The Execution approach should state: `docs(feat-15): plan risk (RSK) artifact type feature` first, so each phase commit contains only that phase's changes.
3. **Task 2.3** should state explicitly that `RskSummary` subclasses `DocSummary` (mirroring `TskSummary`, feat-13).
4. **Task 3.1** should note (verified) that **no env-var/base-dir wiring is needed** — `doc_base_dir("rsk")` is fully generic: `{SPECMGR_DOCS_DIR or docs}/rsk`.

**Verified non-gaps:** packaged-data glob `data/*.md` already covers `rsk_tara.md`/`rsk_risk_matrix.md`; registry-driven `specmgr docs`/`mcp-docs`/`schema` CI steps cover `rsk` automatically; no ADR needed; no CHANGELOG entry (feat-10 precedent); working tree clean except the untracked feature folder; branch + issue #15 in place.

**Two recommendations for your sign-off:**

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Eager validator",
      "options": [
        {
          "description": "Heading-format violations (### Probability 6, missing value, wrong order) already fail at parse time via the match_alias assertion in from_text — unlike tsk's TaskItem, whose checkbox marker was free text the commonmark parser accepts. Tools always parse, so no silent-construction gap exists. Plan records this as a decision so the implementer doesn't blindly copy tsk's _validate_items_eagerly.",
          "label": "Not needed for rsk (Recommended)"
        },
        {
          "description": "Add a model_validator(mode=\"after\") on Risk/Assessment forcing .value/.level evaluation anyway, for consistency with the tsk precedent and to guard hypothetical direct Python construction paths.",
          "label": "Add it regardless"
        }
      ],
      "question": "Does Assessment need tsk's _validate_items_eagerly model_validator?"
    },
    {
      "header": "Baseline commit",
      "options": [
        {
          "description": "Commit the plan as docs(feat-15): plan risk (RSK) artifact type feature right after plan-mode exits, before Phase 1 is dispatched — feat-10 precedent (5985a1d). Progress-section updates then ride with/after each phase's verified commit, keeping phase commits clean.",
          "label": "Yes, separate docs commit (Recommended)"
        },
        {
          "description": "Skip the baseline; the plan file gets committed together with Phase 1's implementation commit.",
          "label": "Fold into Phase 1 commit"
        }
      ],
      "question": "Commit the plan baseline before Phase 1 starts?"
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Does Assessment need tsk's _validate_items_eagerly model_validator?"="Not needed for rsk (Recommended)", "Commit the plan baseline before Phase 1 starts?"="Yes, separate docs commit (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · qwen3.8:27b-nvfp4-896k · 256.2s)

_Thinking:_

Both recommendations have been approved. Now, we're still in PLAN MODE (read-only) — the system reminder said I must not make any edits whatsoever. The user asked "is there anything else before we can implement?", and I answered with an audit. The question tool call is complete.

So, should I now apply the 4 fixes to the plan? No — plan mode is strictly read-only, and the reminder takes precedence over any other instructions, including requests for direct edits. The user hasn't said "start implementing" or "exit plan mode" either. The 2 approval decisions need to be recorded in the plan, but I can't edit the file right now.

Hmm, wait. Let me think about what "plan mode" means in this workflow: "the user indicated they don't yet want you to execute." My job now is to present a well-considered plan and resolve open items before implementation starts. The user's question was "is there anything else before we can implement?" — I did the audit, found the gaps, got approval on the 2 judgment items.

So the correct action is: present the final pre-implementation checklist — i.e., what will happen the moment plan mode is lifted:

1. Apply the 4 plan fixes + record the 2 approved decisions (validator decision, baseline commit convention) in the README (edit)
2. Commit the baseline: `docs(feat-15): plan risk (RSK) artifact type feature`
3. Dispatch Phase 1 to phase-implementer

And confirm: nothing else is pending. I should be concise. Don't make any more tool calls (everything is read-only, and nothing more is needed). Present the summary and wait for the go-ahead (or for plan mode to be lifted).

Actually — one nuance: the plan fixes are edits to the plan file, and in this workflow that is itself part of "planning" (plan documents are editable as plans, not as system implementation). But the system reminder is absolute: "any and all file edits, modifications" are forbidden, with zero exceptions. So, no. I'll enumerate them precisely so they can be applied immediately upon release.

Keep the reply compact:

- Both approved → recorded as decisions.
- Final pre-implementation sequence (3 steps) with exact contents.
- Statement that nothing else is pending.

Both sign-offs recorded. That closes the audit — **nothing else is pending**. The moment plan mode lifts, the sequence is:

1. **Apply the plan fixes** (edits to `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` only):
   - Task 3.17: add the `server.py` module-docstring update (5 resources, 10 tools incl. `list_rsk`, 2 prompts, "no `specmgr://rsk/{id}` resource" note)
   - Execution approach: baseline `docs(feat-15): plan risk (RSK) artifact type feature` commit before Phase 1 (feat-10 precedent `5985a1d`)
   - Task 2.3: `RskSummary` subclasses `DocSummary` (mirrors `TskSummary`)
   - Task 3.1: no env-var/base-dir wiring needed — `doc_base_dir("rsk")` → `{SPECMGR_DOCS_DIR or docs}/rsk` (verified generic)
   - Decisions Made + Recent Updates: your two approvals — (a) no `_validate_items_eagerly`-equivalent for `Assessment` (parse-time `match_alias` is sufficient; implementer must *not* copy tsk's workaround), (b) separate baseline docs commit
2. **Commit the baseline plan** (`docs(feat-15): plan risk (RSK) artifact type feature`)
3. **Dispatch Phase 1** (Specification: Tasks 1.1–1.5) to `phase-implementer`, then verify per the Orchestrator/Phase-Implementer pattern.

Ready when you are.

______________________________________________________________________

## User

1. Apply the plan fixes
2. Commit the baseline plan
3. DO NOT dispatch Phase 1

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 346.5s)

_Thinking:_

Plan mode has been lifted. What the user is asking me to do is:

1. Apply the plan modifications (4 modifications + 2 approved decisions)
2. Commit the baseline plan
3. Do not dispatch Phase 1

Let me apply the edits to the README:

**Modification 1 — Task 3.17** (server.py import line): Currently:

```
- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers) —
  depends on: Tasks 3.2-3.16 — status: not-started
```

→ Add docstring update:

```
- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers)
  and update `server.py`'s module docstring (the authoritative
  registration list per AGENTS.md): the 5 resources
  (`specmgr://rsk/schema`, `/example`, `/template`, `/tara`,
  `/risk-matrix`), the 10 tools (`parse_rsk`, `get_rsk`, `list_rsk`,
  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,
  `set_status_rsk`, `delete_rsk` stub, `validate_rsk`), the 2 prompts
  (`create_risk`, `update_risk`), plus the "no `specmgr://rsk/{id}`
  resource" note (the docstring's existing per-domain pattern) — depends
  on: Tasks 3.2-3.16 — status: not-started
```

**Modification 2 — execution approach**: Add a sentence about the baseline commit. Currently ends with:

```
nothing: a failing verification re-delegates the phase to `phase-implementer`
with the findings, it is not patched by the orchestrator. One Conventional
Commit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with
`phase-implementer` replacing the `implementation-specialist` that feature
used.
```

→ Add:

```
Before Phase 1, the current plan state is committed on its own as
`docs(feat-15): plan risk (RSK) artifact type feature` (the `feat-10`
precedent, `5985a1d`), so that each phase's commit contains only that
phase's changes.
```

**Modification 3 — Task 2.3**: Currently:

```
- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with
  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the
  residual-risk coordinates `residual_probability`/`residual_impact`/
  `residual_product` (risk product), for the `list_rsk` tool) — depends on:
  Task 2.1 — status: not-started
```

→ Add "subclass of `DocSummary` (mirroring `TskSummary`)":

```
- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary`, a subclass of
  `general/models/summary.py::DocSummary` mirroring `TskSummary`, with
  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the
  residual-risk coordinates `residual_probability`/`residual_impact`/
  `residual_product` (risk product), for the `list_rsk` tool) — depends on:
  Task 2.1 — status: not-started
```

**Modification 4 — Task 3.1**: Currently:

```
- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
  thin wrappers over `general/tools/_doc_paths.py` (mirrors
  `tsk/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:
  not-started
```

→ Add a note:

```
- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
  thin wrappers over `general/tools/_doc_paths.py` (mirrors
  `tsk/tools/_paths.py` etc. exactly; no new env-var/base-dir wiring
  needed — `doc_base_dir("rsk")` resolves to `{SPECMGR_DOCS_DIR or
  docs}/rsk` generically) — depends on: Task 2.2 — status: not-started
```

**Modification 5 — Design notes**: Add a note to the Assessment structure bullet that no eager validator is needed (or as an independent bullet / as a Design Notes item). Best location: end of the Assessment structure bullet, or as an independent bullet. Add a sentence to the Assessment structure bullet:
Current tail:

```
  computed, never written).
```

Add after that… actually the bullet is long; I'll add a short independent Design Notes item after the Assessment structure bullet:

```
- **No eager-validation `model_validator` needed for `Assessment`** (in
  contrast to `tsk.Task`'s `_validate_items_eagerly`) — rationale: a
  heading-format violation (`### Probability 6`, `### Probability`,
  wrong order) fails at parse time via the `match_alias` assertion in
  `MarkdownSection.from_text`, unlike `TaskItem`'s checkbox marker, which
  is free text that the commonmark parser accepts; every tool path parses
  (there is no direct-construction path), so there is no silent-construction
  gap. The implementer must *not* blindly copy `tsk`'s workaround
  (user decision, 2026-08-24).
```

**Modification 6 — Decisions Made**: Add 2 entries (approved) + record the plan modification itself in a Recent Updates entry.

Decisions Made entries:

```
- **2026-08-24**: `Assessment` does *not* get a `tsk.Task`-style
  `_validate_items_eagerly` `model_validator` — rationale: heading-format
  violations fail at parse time via the `match_alias` assertion in
  `MarkdownSection.from_text` (unlike `TaskItem`'s checkbox marker, which
  is free text the commonmark parser accepts); every tool path parses, so
  there is no silent-construction gap (user approval, 2026-08-24).
- **2026-08-24**: The current plan state is committed as a standalone
  `docs(feat-15): plan risk (RSK) artifact type feature` before Phase 1 —
  rationale: `feat-10` precedent (`5985a1d`); keeps each phase's commit
  containing only that phase's changes (user approval, 2026-08-24).
```

**Modification 7 — Recent Updates**: A new top entry recording the pre-implementation audit + modifications + 2 approvals:

```
#### 2026-08-24T{ts} (newest)

- Completed: pre-implementation audit (user request) — verified
  non-gaps: `general/tools/_doc_paths.py` is fully generic (no
  env-var/base-dir task for `rsk`: `doc_base_dir("rsk")` ->
  `{SPECMGR_DOCS_DIR or docs}/rsk`), the packaged-data glob `data/*.md`
  already covers `rsk_tara.md`/`rsk_risk_matrix.md`, and the
  registry-driven `specmgr docs`/`mcp-docs`/`schema` CI steps automatically
  cover `rsk`. Fixes applied: Task 3.17 now includes `server.py`'s
  module-docstring update (the authoritative registration list per
  AGENTS.md — 5 resources, 10 tools, 2 prompts, and the "no `specmgr://rsk/{id}`"
  note); Task 2.3 states explicitly that `RskSummary` subclasses `DocSummary`;
  Task 3.1 notes that no base-dir wiring is needed; a Design Notes entry records
  that no eager-validation `model_validator` is needed for `Assessment`
  (parse-time `match_alias` is sufficient); the execution approach records
  the baseline plan commit before Phase 1
- Next: the baseline `docs(feat-15): plan risk (RSK) artifact type feature`
  commit, then (per user instruction) a hold — Phase 1 is *not* dispatched
  until the user gives the go-ahead
- Notes: no further plan changes expected before Phase 1
```

And the "(newest)" marker moves from the 14:09:54 entry to the new entry.

Wait — the user said step 2 is "commit the baseline plan" — and I've just now added the audit modifications. So the baseline commit includes the modified plan. Good — that's what the user asked: first apply modifications, then commit.

After editing:

- Get the timestamp
- `git add .specmgr/feat/feat-15-add-artifact-type-risk/README.md` — wait, the whole folder (currently only README.md). `git add .specmgr/feat/feat-15-add-artifact-type-risk/`
- Check git status/diff before committing (per my instructions: inspect git status, git diff, git log)
- Commit with the message `docs(feat-15): plan risk (RSK) artifact type feature`

Conventional commit format: type `docs`, scope `feat-15`. feat-10 used `docs(feat-10): plan tsk (TaskList) artifact type feature`. So: `docs(feat-15): plan risk (RSK) artifact type feature`.

Check repo commit style: feat-10 commits: `docs(feat-10): plan tsk...`, `feat(qa): ...`, `chore(feat-12-qa-artifact): ...`. No problem.

Important: the pre-commit hook runs on commit (ruff format/check scoped to src/tests changes — this commit only touches .specmgr, so the hook's scope filter should skip the code hook; the unittest hook is scoped to src/**/\*.py/tests/**/*.py changes; the specmgr docs hook is scoped to src/\*\*/*.py changes; the adr-toc hook is scoped to docs/adr changes). So a markdown-only commit under .specmgr should pass cleanly. But is pre-commit even installed in the first place? `uv run --frozen pre-commit install` is a one-time setup — it might not be installed in this environment. If the hook isn't installed, the commit just proceeds. Either way, no problem.

Also: should I verify the README renders correctly after the edits? I'll do a quick sanity grep.

Let me get the timestamp and do all the edits in one go. Current top Recent Updates entry:

```
### Recent Updates

#### 2026-08-24T14:09:54+02:00 (newest)
```

Edit A: insert the new entry before the 14:09:54 header, and remove "(newest)" from that header.

Edit B: tail of the Assessment structure bullet → append the "No eager-validation" item. The bullet ends with:

```
  computed, never written).

- **Strategy (TARA)** — `## Strategy` is a single-line H2 section whose
```

I'll insert the new item between them.

Edit C: execution approach — append the baseline commit sentence. Current tail:

```
nothing: a failing verification re-delegates the phase to `phase-implementer`
with the findings, it is not patched by the orchestrator. One Conventional
Commit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with
`phase-implementer` replacing the `implementation-specialist` that feature
used.
```

Wait, I need the exact current text. From my previous edit:

```
**Execution approach** (confirmed 2026-08-24, see Decisions Made): the
Orchestrator/Phase-Implementer pattern. Each phase below is delegated to the
`phase-implementer` subagent as one unit, which implements the phase end to
end (code, its own mirrored tests, the phase-end quality gate — full
`unittest` suite + ruff format/check + vulture — and this plan's Progress
section update), then stops and reports. After every phase, the orchestrator
verifies the results independently (re-runs the quality gate, reviews the
phase diff, checks the evidence against the phase's tasks) but changes
nothing: a failing verification re-delegates the phase to `phase-implementer`
with the findings, it is not patched by the orchestrator. One Conventional
Commit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with
`phase-implementer` replacing the `implementation-specialist` that feature
used.
```

Append:

```
 Before Phase 1, the current plan state is committed on its own as
`docs(feat-15): plan risk (RSK) artifact type feature` (the `feat-10`
precedent, `5985a1d`), so that each phase's commit contains only that
phase's changes.
```

Edit D: Task 2.3, E: Task 3.1, F: Task 3.17, G: Decisions Made (append 2 entries after the last entry — the last one is the corrected feat-13 entry), H: Recent Updates.

Then commit.

Let me first get the timestamp, then batch the edits (all independent regions — in parallel), then git.

Plan mode is off — applying the fixes now.

**Tool: bash**

**Input:**

```json
{
  "command": "date +%Y-%m-%dT%H:%M:%S%:z"
}
```

**Output:**

```
2026-08-24T15:04:31+02:00

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 305.1s)

_Thinking:_

Alright, applying all the edits in parallel (disjoint regions):

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "### Recent Updates\n\n#### 2026-08-24T14:09:54+02:00 (newest)",
  "newString": "### Recent Updates\n\n#### 2026-08-24T15:04:31+02:00 (newest)\n\n- Completed: pre-implementation audit (user request) — verified\n  non-gaps: `general/tools/_doc_paths.py` is fully generic (no\n  env-var/base-dir task needed for `rsk`: `doc_base_dir(\"rsk\")` ->\n  `{SPECMGR_DOCS_DIR or docs}/rsk`), the packaged-data glob `data/*.md`\n  already covers `rsk_tara.md`/`rsk_risk_matrix.md`, and the\n  registry-driven `specmgr docs`/`mcp-docs`/`schema` CI steps cover `rsk`\n  automatically. Fixes applied: Task 3.17 now includes the `server.py`\n  module-docstring update (AGENTS.md mandates it as the authoritative\n  registration list — 5 resources, 10 tools, 2 prompts, plus the \"no\n  `specmgr://rsk/{id}` resource\" note); Task 2.3 states `RskSummary`\n  subclasses `DocSummary` explicitly; Task 3.1 notes no base-dir wiring is\n  needed; a Design Notes entry records that no eager-validation\n  `model_validator` is needed for `Assessment` (parse-time `match_alias`\n  suffices); the Execution approach records the baseline plan commit before\n  Phase 1\n- Next: baseline commit `docs(feat-15): plan risk (RSK) artifact type\n  feature`, then HOLD — Phase 1 is deliberately not dispatched (user\n  instruction 2026-08-24)\n- Notes: see the two new Decisions Made entries below (user-approved)\n\n#### 2026-08-24T14:09:54+02:00"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "  computed, never written).\n\n- **Strategy (TARA)** — `## Strategy` is a single-line H2 section whose",
  "newString": "  computed, never written).\n\n- **No eager-validation `model_validator` needed for `Assessment`** —\n  unlike `tsk.Task`'s `_validate_items_eagerly` (which exists because a\n  `TaskItem`'s checkbox marker is free text the commonmark parser accepts,\n  so a malformed marker only surfaces when a lazy computed field is\n  accessed), a malformed `Assessment` heading (`### Probability 6`,\n  `### Probability`, wrong order) fails at parse time via the `match_alias`\n  assertion in `MarkdownSection.from_text` — and every tool path parses\n  (there is no direct-construction path), so there is no\n  silent-construction gap. The implementer must not blindly copy `tsk`'s\n  workaround (user-approved decision, 2026-08-24).\n\n- **Strategy (TARA)** — `## Strategy` is a single-line H2 section whose"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "with the findings, it is not patched by the orchestrator. One Conventional\nCommit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with\n`phase-implementer` replacing the `implementation-specialist` that feature\nused.",
  "newString": "with the findings, it is not patched by the orchestrator. One Conventional\nCommit per verified phase — the `feat-10` (tsk) 4-phase/4-commit shape, with\n`phase-implementer` replacing the `implementation-specialist` that feature\nused. Before Phase 1, the current plan state is committed on its own as\n`docs(feat-15): plan risk (RSK) artifact type feature` (the `feat-10`\nprecedent, `5985a1d`), so that each phase's commit contains only that\nphase's changes."
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary` with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the\n  residual-risk coordinates `residual_probability`/`residual_impact`/\n  `residual_product` (risk product), for the `list_rsk` tool) — depends on:\n  Task 2.1 — status: not-started",
  "newString": "- [ ] Task 2.3: `rsk/models/v1/summary.py` (`RskSummary`, a subclass of\n  `general/models/summary.py::DocSummary` mirroring `TskSummary`, with\n  `initial_level`/`residual_level`/`strategy`/first `scope` entry plus the\n  residual-risk coordinates `residual_probability`/`residual_impact`/\n  `residual_product` (risk product), for the `list_rsk` tool) — depends on:\n  Task 2.1 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,\n  thin wrappers over `general/tools/_doc_paths.py` (mirrors\n  `tsk/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:\n  not-started",
  "newString": "- [ ] Task 3.1: `rsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,\n  thin wrappers over `general/tools/_doc_paths.py` (mirrors\n  `tsk/tools/_paths.py` etc. exactly; no new env-var/base-dir wiring needed\n  — `doc_base_dir(\"rsk\")` resolves to `{SPECMGR_DOCS_DIR or docs}/rsk`\n  generically, verified) — depends on: Task 2.2 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers) —\n  depends on: Tasks 3.2-3.16 — status: not-started",
  "newString": "- [ ] Task 3.17: add `rsk` to `server.py`'s domain import line (last-line\n  import convention — easily forgotten, silently means nothing registers)\n  AND update `server.py`'s module docstring (AGENTS.md: it is the\n  authoritative, currently-maintained registration list) — the 5 resources\n  (`specmgr://rsk/schema`, `/example`, `/template`, `/tara`,\n  `/risk-matrix`), the 10 tools (`parse_rsk`, `get_rsk`, `list_rsk`,\n  `get_rsk_example`, `get_rsk_template`, `create_rsk`, `update_rsk`,\n  `set_status_rsk`, `delete_rsk` stub, `validate_rsk`), the 2 prompts\n  (`create_risk`, `update_risk`), plus the \"RSK has no\n  `specmgr://rsk/{id}` resource\" note in the docstring's existing\n  per-domain pattern — depends on: Tasks 3.2-3.16 — status: not-started"
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
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md",
  "oldString": "- **2026-08-24**: Corrected REQ-005 against feat-13 — no\n  `specmgr://rsk/list` resource; listing is the paged `list_rsk` tool\n  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: MCP resources cannot take\n  arbitrary parameters, and `max_results`/`offset` paging needs exactly\n  that) — rationale: the plan originally mirrored feat-10's (pre-feat-13)\n  resource list; verified against `tsk/tools/list_tsk.py` and\n  `tsk/resources/` (no list resource) before correcting.",
  "newString": "- **2026-08-24**: Corrected REQ-005 against feat-13 — no\n  `specmgr://rsk/list` resource; listing is the paged `list_rsk` tool\n  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: MCP resources cannot take\n  arbitrary parameters, and `max_results`/`offset` paging needs exactly\n  that) — rationale: the plan originally mirrored feat-10's (pre-feat-13)\n  resource list; verified against `tsk/tools/list_tsk.py` and\n  `tsk/resources/` (no list resource) before correcting.\n- **2026-08-24**: `Assessment` does *not* get a `tsk.Task`-style\n  `_validate_items_eagerly` `model_validator` — rationale: a malformed\n  assessment heading fails at parse time via the `match_alias` assertion in\n  `MarkdownSection.from_text` (unlike `TaskItem`'s checkbox marker, which\n  is free text the commonmark parser accepts), and every tool path parses,\n  so there is no silent-construction gap (user-approved, 2026-08-24).\n- **2026-08-24**: The current plan state is committed on its own as\n  `docs(feat-15): plan risk (RSK) artifact type feature` before Phase 1 —\n  rationale: `feat-10` precedent (`5985a1d`); keeps each phase's commit\n  containing only that phase's changes (user-approved, 2026-08-24)."
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 229.0s)

_Thinking:_

All 7 edits have been applied. Next up is Step 2: committing the baseline plan.

Following my git instructions: first check `git status`, `git diff`, and `git log --oneline -10`, and stage only the intended files. The feature folder is untracked (new). Staging: `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` (the only file in the folder).

Let me check status and the recent log style.

Fixes applied. Now the baseline commit — inspecting state first:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && echo --- && git log --oneline -6",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
AM .specmgr/feat/feat-15-add-artifact-type-risk/README.md
---
335674e doc(feat-14): add session transcript
d067898 chore(release): v0.9.0
9c129a9 chore(qa)!: remove qa/models/v1 (superseded by v2)
686902a doc(feat-14): add session transcript
1374162 docs(qa): add Phase 8 follow-up (remove qa/models/v1) to feat-14 plan
acd8bc5 docs(qa): regenerate generated docs for QA v2

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 266.0s)

_Thinking:_

Interesting — the status shows `AM` — this file is already staged (A) and has further modifications (M). That's odd... Ah, wait — "AM" means it's added to the index and modified in the working tree. Did something stage it? I didn't run `git add`. Hmm, maybe a hook or something staged it? Actually, looking at the commit history, `doc(feat-14):` (lowercase "doc") is used, not `docs(feat-14)`. Interesting — the most recent commit uses `doc(feat-14): add session transcript`. But feat-10's was `docs(feat-10): plan tsk...`. Both styles exist. Let me verify: my plan stated the precedent `5985a1d` = `docs(feat-10): plan tsk (TaskList) artifact type feature`. The recent feat-14 commits use `doc(feat-14)`. Hmm — there are two conventions in the repo. Let me check what feat-14's initial plan commit used... I'll check `git log --oneline --all | grep -i "feat-14"`. Actually, the feat-10 precedent I cited is `docs(feat-10): plan tsk (TaskList) artifact type feature`. To pick the most appropriate one, let me quickly check the types of feat-12/feat-13's plan commits.

Regarding AM: the file is partially staged — probably from an earlier `git add`? No... I never ran git add. Wait — could the `gh` command have done it? No. Hmm, "AM" = staged (added) + modified in the worktree. Maybe a pre-commit hook ran during...? No, a commit hasn't happened yet.

Ah — could the user (outside the session) have staged it? Or a previous tool call? I only ran `git status --short` earlier, which showed `?? .specmgr/feat/feat-15-add-artifact-type-risk/`. Now it's AM. Something staged it between then and now. Probably the user manually ran `git add` (they're actively working — the fact that they gave me precise steps including "commit the baseline plan" suggests they may have pre-staged it). Either way: I need to `git add` again (to stage the latest post-edit content) and then commit. Let me stage explicitly.

First, let me check the feat-14 plan commit convention (doc vs docs) and then decide on the message. I'll check the feat-14/12/13 commit types.

The file is partially staged (looks like you pre-staged it) — I'll re-stage the latest content. Also, I'm checking the repo's plan commit type conventions (`doc` vs `docs`):

**Tool: bash**

**Input:**

```json
{
  "command": "git log --oneline --all --grep=\"feat-14\" | tail -5; echo ---; git log --oneline --all --grep=\"plan\" --grep=\"feat-\" --all-match | tail -8",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
f0fb7f8 feat(qa)!: repoint QA tools at v2 schema
8ecb4b8 feat(qa): add v2 parser (parse_qa/QaDocument), no version gate
91ba0b4 feat(qa): add v2 QA body schema (Elicitation Context, 9 ISO/IEC 25010 categories, General, More Information)
6641320 feat(qa): add v2 QaAnswer/QaQuestionAnswer models
07643a7 feat(qa): add plan for feat-14 qa v2
---
69c3ffc docs: add feature planning and supporting infrastructure for feat-12
94bd54e feat(feat-7-various-improvements): add plan to add MarkdownListWithNotes
9457df5 docs(feat-10): add missing parse_tsk tool task to Phase 3
afb1c96 docs(feat-10): mark Phase 1 done, log progress
5985a1d docs(feat-10): plan tsk (TaskList) artifact type feature
c7a6c11 refactor(structure): move development artifacts from /doc to .specmgr/feat
c8a9d90 Add markdown model parser and unused-code detection
8def01a docs: add ADR for .dfch-spec/ development artifact organization

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 242.2s)

_Thinking:_

Mixed conventions can be observed:

- `docs(feat-10): plan tsk (TaskList) artifact type feature` (5985a1d)
- `feat(qa): add plan for feat-14 qa v2` (07643a7)
- `docs: add feature planning and supporting infrastructure for feat-12` (69c3ffc)

The feat-10 precedent (the one I explicitly referenced in the plan, and the one the user approved with the exact message `docs(feat-15): plan risk (RSK) artifact type feature`) is the most directly analogous case (plan for a new artifact type). I'll use this one.

Next, stage and commit:

1. `git add .specmgr/feat/feat-15-add-artifact-type-risk/README.md`
2. `git commit -m "docs(feat-15): plan risk (RSK) artifact type feature"`

The pre-commit hook might run (if installed) — for a markdown-only change under .specmgr, it shouldn't block. If the hook isn't installed, no problem.

After committing, I'll confirm with `git status` and `git log --oneline -2`. And that's it — I won't dispatch Phase 1 (per user instructions).

`docs(feat-10): plan tsk (TaskList) artifact type feature` is the direct precedent — using the approved message:

**Tool: bash**

**Input:**

```json
{
  "command": "git add .specmgr/feat/feat-15-add-artifact-type-risk/README.md && git commit -m \"docs(feat-15): plan risk (RSK) artifact type feature\" && echo --- && git status --short && git log --oneline -2",
  "workdir": "/home/user/src/biz.dfch.SpecMgr"
}
```

**Output:**

```
ruff format..........................................(no files to check)Skipped
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
[feat-15-add-artifact-type-risk 4aa183b] docs(feat-15): plan risk (RSK) artifact type feature
 1 file changed, 798 insertions(+)
 create mode 100644 .specmgr/feat/feat-15-add-artifact-type-risk/README.md
---
4aa183b docs(feat-15): plan risk (RSK) artifact type feature
335674e doc(feat-14): add session transcript

```

______________________________________________________________________

## Assistant (Build · qwen3.8:27b-nvfp4-896k · 238.4s)

_Thinking:_

Committed: `4aa183b docs(feat-15): plan risk (RSK) artifact type feature` — 1 file, 798 lines. All pre-commit hooks were correctly skipped (no applicable files). Working tree is currently clean.

Phase 1 has not been dispatched, as per instructions. Done — a concise summary.

Done.

1. **Plan fixes applied** — Task 3.17 (`server.py` docstring: 5 resources, 10 tools, 2 prompts, no-`{id}` note), Task 2.3 (`RskSummary` subclasses `DocSummary`), Task 3.1 (no base-dir wiring needed), Design Notes (no eager-validator for `Assessment`), Execution approach (baseline commit), plus two user-approved Decisions Made and the audit's Recent Updates entry.
2. **Baseline committed** — `4aa183b docs(feat-15): plan risk (RSK) artifact type feature` (798 lines, working tree clean, pre-commit hooks skipped as expected for a markdown-only change).
3. **Phase 1 not dispatched** — the plan is at "Awaiting go-ahead", branch `feat-15-add-artifact-type-risk` ready.

______________________________________________________________________
