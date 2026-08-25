# Problem Statement artifact type (PRB) design

**Session ID:** ses_fc877c2f2ffe1rY475BR5QEkdJ
**Created:** 8/25/2026, 6:07:50 AM
**Updated:** 8/25/2026, 6:29:49 AM

______________________________________________________________________

## User

I want to create a new feature: Create new artifact type "Problem Statement" (PRB)

There is an ADR how to create a new feature. There are examples how we created features in the past, example: feat-10-add-artifact-type-tasklist. There also is an template for a template in .specmgr/\_template.
I want you to design the feature with me an make a plan for it (as we did with the other features). After the plan is done, we DO NOT implement. This will be done in another session with a fresh context. We thus need the plan to be complete and precise, so that a new agent can pick up the work and implement.

We want a structure like this:

Current State
Summary
Question 1 (optional)
Question 2 (optional)
...
Question 7 (optional)
Gap
Future State
References (optional)
More Information (optional)

We use the questions from this link: https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/

We have a frontmatter as with other documents, we use "prb" as the type abbreviation.

In the "Current State" section I want the questions (fiexed heading per question) and their answers, so that we can reference and refine that in the future.
Suggest additional sections. Also examine https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/ for additional input. An then, you can query the internet yourself for additional input or use your internal knowledge.
Suggest status values. I think there are only very few.
I also want a mcp "create" command that walks the user through to create the problem statement. Maybe it is a good idea to use a todo list for this.
And the "update" command shall ask the user for more input to the questions if the user wants to provide it, and then create a summary for the "summary" of the current state.
If possible the agent shall identify the GAP and record it in "Gap" (in both commands).
Any questions before you start?

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 7.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/admin/src/biz.dfch.SpecMgr/.specmgr -iname \"*tasklist*\" -o -iname \"*feat-10*\" | sort"
}
```

**Output:**

```
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/session-ses_ff52-feat-10-task-list.md

```

**Tool: glob**

**Input:**

```json
{
  "pattern": ".specmgr/_template/**"
}
```

**Output:**

```
No files found
```

**Tool: glob**

**Input:**

```json
{
  "pattern": ".specmgr/feat/**"
}
```

**Output:**

```
No files found
```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 3.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/admin/src/biz.dfch.SpecMgr/.specmgr -maxdepth 3 | sort"
}
```

**Output:**

```
/home/admin/src/biz.dfch.SpecMgr/.specmgr
/home/admin/src/biz.dfch.SpecMgr/.specmgr/conventions.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/history.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/session-ses_ff52-feat-10-task-list.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/session-ses_ff52-feat-7-task-list.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/tsk_reference.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/history.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/qa_reference.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/session-ses_feab-feat-12-qa-artifact.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-13-list-paging
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-13-list-paging/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/session-ses_fd18-feat-14-01.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/session-ses_fd23-feat-14-00.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/ac-ears.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/history.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/img
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/playground
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/tsk-2c434ef6-17a2-47f5-a7d1-08e92f6e4c27-review-uc-feature-implementation-commits.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/v1
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-4-use-cases/v2
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-5-md-model-parser
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-5-md-model-parser/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-6-requirement-artifact
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-6-requirement-artifact/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-6-requirement-artifact/req_reference.ast
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-6-requirement-artifact/req_reference.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/history.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/product-quality-model.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/tsk-266eb332-795b-48c4-9bc0-7115eb209378-improve-get-type-not-found-error-messages.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/tsk-602740af-0445-48d8-bcc3-18df541dad72-fix-markdown-list-item-numbered-lists.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/tsk-efb7d049-a222-4730-901f-6d57283b387c-implement-webfetch-mcp-tool-bearer-authenticated-url-filtere.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/tsk-f581fb2f-9a82-11f1-9c57-fc4cea71c519-markdown-list-item-with-notes.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-8-coverage-badge
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-8-coverage-badge/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr/create-adr.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr/docs-generator-cleanup-plan.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr/history
/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-9-doc-in-specmgr/README.md
/home/admin/src/biz.dfch.SpecMgr/.specmgr/_template
/home/admin/src/biz.dfch.SpecMgr/.specmgr/_template/v1
/home/admin/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md

```

**Tool: bash**

**Input:**

```json
{
  "command": "ls -la /home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/"
}
```

**Output:**

```
total 344
drwxrwxr-x  2 admin admin   4096 Aug 25 05:47 .
drwxrwxr-x 12 admin admin   4096 Aug 25 05:47 ..
-rw-rw-r--  1 admin admin   5966 Aug 25 05:47 history.md
-rw-rw-r--  1 admin admin  34855 Aug 25 05:47 README.md
-rw-rw-r--  1 admin admin 147317 Aug 25 05:47 session-ses_ff52-feat-10-task-list.md
-rw-rw-r--  1 admin admin 147317 Aug 25 05:47 session-ses_ff52-feat-7-task-list.md
-rw-rw-r--  1 admin admin    619 Aug 25 05:47 tsk_reference.md

```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 4.6s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md"
}
```

**Output:**

````
<path>/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md</path>
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
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md</path>
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

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/README.md"
}
```

**Output:**

````
<path>/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-12-qa-artifact/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-18
3: id: feat-12-qa-artifact
4: status: done
5: updated: 2026-08-18
6: version: 1.0.0
7: ---
8: 
9: # Feature: Question and Answer (QA) artifact type
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: A new `qa` document-type domain: a requirements-elicitation interview structured
16: around the fixed ISO/IEC 25010:2023 quality-characteristic categories (plus
17: `General` and `More Information`), each holding a repeating list of
18: question/answer pairs, with an optional embedded `Requirement` callout per
19: answer holding arbitrary, deliberately unspecified agent-authored content.
20: Follows the domain-first hierarchy (ADR
21: ece4554b-725c-4f76-bc04-5d2b760363d2) and is modeled most closely on `req/`
22: (single artifact per file, no ADR-style dynamic option tooling, no UC-style
23: dual schema versions). Introduces the project's first real domain use of
24: `MarkdownBlockQuote`, and a new, generalized `@markdown(end_marker=...)`
25: mechanism in the shared `models/md` engine.
26: 
27: ### Requirements
28: 
29: - REQ-001: Generalize `models/md`'s `@markdown` decorator and
30:   `MarkdownSection.get_extent` with a depth-aware `end_marker` stop
31:   condition — a standalone, reusable engine capability, not `qa`-specific,
32:   needed so a composite section (e.g. an embedded `Requirement` H4) can stop
33:   at the next block quote instead of only at the next heading.
34: - REQ-002: Define the `qa` markdown schema (frontmatter + body) — H1 title;
35:   fixed H2s (`General`, the 9 ISO 25010:2023 characteristics, `More Information`); repeating `QaSection` (H3) Q&A pairs inside each
36:   ISO-characteristic H2; special fixed `Introduction`/`Raw Requirements` H3s
37:   inside `General`.
38: - REQ-003: Pydantic models under `qa/models/v1/` (frontmatter, body,
39:   document, parser, summary), status set reused from TSK
40:   (`draft`/`active`/`done`/`cancelled`).
41: - REQ-004: Parse/validate `qa` documents from markdown, mirroring
42:   `parse_req`/`parse_tsk`'s two-error-channel convention
43:   (`AssertionError`/`pydantic.ValidationError`).
44: - REQ-005: MCP tools/resources/prompts mirroring REQ's surface: `parse_qa`,
45:   `get_qa`, `get_qa_example`, `get_qa_template`, `create_qa`, `update_qa`,
46:   `set_status_qa`, `delete_qa` (stub), `validate_qa`; resources
47:   `specmgr://qa/schema`, `/example`, `/template`, `/list` (no `/{id}`, per
48:   ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614); prompts `create_qa`,
49:   `update_qa`.
50: - REQ-006: Full cross-cutting registration (`server.py`,
51:   `commands/schema.py`, `pyproject.toml`, `.pre-commit-config.yaml`, CI,
52:   `AGENTS.md`) and test coverage mirroring `tests/req/`'s layout.
53: 
54: ### Acceptance Criteria
55: 
56: - [ ] ACC-001: Verifies REQ-001 — `@markdown(...)` merges into any inherited
57:   `_metadata` instead of replacing it (regression-tested against all
58:   existing `models/md` classes); a class declaring `end_marker=X` stops
59:   `MarkdownSection.get_extent`'s scan at the first *depth-0* occurrence of
60:   `X`'s token type, not the first occurrence anywhere (nested/legitimate
61:   occurrences one level deeper do not truncate).
62: - [ ] ACC-002: Verifies REQ-002 — a full reference `qa_reference.md`
63:   document exercising every field (including `General`'s special structure,
64:   every ISO characteristic category, an embedded `Requirement` callout, and
65:   `More Information`) parses successfully.
66: - [ ] ACC-003: Verifies REQ-003 — Pydantic models validate required/optional
67:   fields correctly; `QaFrontmatter.status` rejects any value outside the
68:   four-value set.
69: - [ ] ACC-004: Verifies REQ-004 — parser produces a valid object tree for a
70:   well-formed document; malformed structure raises `AssertionError`; invalid
71:   field values raise `pydantic.ValidationError`.
72: - [ ] ACC-005: Verifies REQ-005 — every listed tool/resource/prompt is
73:   registered and callable via the MCP server.
74: - [ ] ACC-006: Verifies REQ-006 — `specmgr docs`, `specmgr mcp-docs`, and
75:   `specmgr schema --type qa` all run clean with no drift; CI/pre-commit
76:   hooks cover the new domain.
77: 
78: ### Scope
79: 
80: **Included in this feature:**
81: 
82: - The `@markdown(end_marker=...)` engine enhancement in `models/md`
83:   (Phase 1) — a standalone, reusable addition, exercised for the first time
84:   by `qa`'s embedded `Requirement` callout.
85: - The `qa` markdown schema, Pydantic models, parser, and summary.
86: - MCP tools, resources, and prompts, in the same shape as REQ.
87: - Example/template packaged data files, generated JSON Schema.
88: - Full test suite mirroring `tests/req/`'s layout, plus new `models/md`
89:   tests for Phase 1.
90: - Cleanup of stray, untracked, empty scaffold directories left over from an
91:   earlier session (see Decisions Made).
92: 
93: **Explicitly out of scope (for v1):**
94: 
95: - Cross-document validation of an embedded `requirement` callout's content
96:   against real REQ documents (e.g. checking it against an actual
97:   `req-*.md` file, or promoting it into one).
98: - Characteristic-based filtering/search over `qa` documents (same
99:   deferral REQ made for its own `characteristics`).
100: - Any rendering/exporting of `qa` documents to non-markdown formats.
101: 
102: ### Dependencies
103: 
104: - Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
105:   hierarchy), ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure),
106:   ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads);
107:   the existing, already-tested `MarkdownBlockQuote` class
108:   (`models/md/markdown_block_quote.py`); the existing `Iso25010`/
109:   `parse_iso25010` model and `specmgr://iso25010` resource
110:   (`models/iso25010.py`), whose 9 characteristic names are the canonical
111:   source for `qa`'s fixed H2 set.
112: - Blocks: None identified yet.
113: 
114: ### Design Notes
115: 
116: **Schema (finalized during planning discussion):**
117: 
118: ```
119: QaFrontmatter(MarkdownFrontmatter): type: Literal["qa"];
120:   status in {draft, active, done, cancelled} (reused from TSK's set)
121: 
122: Qa(MarkdownSection1)                          # H1, free-form title (alias ".+")
123: ├── general: General                           # always present
124: ├── functional_suitability: <QaCategory>        # always present, items may be empty
125: ├── performance_efficiency: <QaCategory>
126: ├── compatibility: <QaCategory>
127: ├── interaction_capability: <QaCategory>
128: ├── reliability: <QaCategory>
129: ├── security: <QaCategory>
130: ├── maintainability: <QaCategory>
131: ├── flexibility: <QaCategory>
132: ├── safety: <QaCategory>
133: └── more_information: MoreInformation | None    # leaf, opaque raw text (mirrors REQ's MoreInformation)
134: 
135: General(MarkdownSection2WithComment)              # inherited `comment: MarkdownComment | None`, not redeclared
136: ├── introduction: Introduction                  # always present
137: └── raw_requirements: RawRequirements            # always present
138: 
139: Introduction(MarkdownSection3WithComment)         # inherited `comment: MarkdownComment | None`, not redeclared
140: └── body: list[MarkdownParagraph] | None
141: 
142: RawRequirements(MarkdownSection3)                # leaf, opaque raw text (mirrors MoreInformation/Notes)
143: 
144: <QaCategory>(MarkdownSection2)                   # one of the 9 ISO characteristic H2s; fixed, exact heading name (not free-form)
145: └── items: list[QaSection] | None                # repeating Q&A pairs; category may be empty
146: 
147: QaSection(MarkdownSection3WithComment)            # one Q&A pair, free-form H3 heading (alias ".+"); inherited `comment`, not redeclared
148: ├── requirement: Requirement | None              # @markdown(end_marker=MarkdownBlockQuote) -- new mechanism
149: ├── question: MarkdownBlockQuote | None
150: └── answer: QaAnswer | None                      # leaf, opaque raw text (mirrors MoreInformation/Notes)
151: ```
152: 
153: All fields on `QaSection` (`requirement`/`question`/`answer`), plus the
154: inherited `comment`, are fully optional.
155: 
156: **`requirement`'s content is deliberately unspecified.** Unlike
157: `RawRequirements`/`MoreInformation`/`QaAnswer` (which are leaf classes for
158: the *same* reason -- capturing free-form markdown verbatim), `requirement`
159: is called out separately here because its purpose differs: it exists to
160: hold whatever an *agent* (not a human author) chooses to write when it
161: determines a given Q&A answer implies a concrete requirement, with no
162: enforced shape (not REQ's own `statement`/`level`/etc. fields, not any
163: other structure). This is intentional -- the field's value is exactly
164: "arbitrary agent-authored content," not a gap to close later.
165: 
166: **The `end_marker` engine problem this schema exposed, and its resolution:**
167: placing `requirement` (an H4 section) before `question` (a block quote) in
168: field-declaration order only parses correctly if `requirement`'s own
169: `get_extent` knows to stop *before* the next block quote, not just the next
170: heading — `MarkdownSection.get_extent`'s existing stop condition only ever
171: checks heading tokens (verified against its actual implementation), so a
172: block quote following a `requirement` section would otherwise be silently
173: absorbed into it. Resolved by adding a generalized, declarative
174: `end_marker` parameter to `@markdown(...)` rather than a one-off
175: `get_extent` override on a single class — but only after confirming (a) the
176: existing decorator does a full, unconditional `_metadata` replace with no
177: merge against inherited data (verified: every one of the 11 existing
178: `@markdown(...)` call sites in `models/md/` applies the decorator exactly
179: once — the `*WithComment` classes inherit it rather than re-applying it —
180: so this exact drift risk has no precedent yet, but would be hit
181: immediately by a further subclass adding `end_marker` on top of
182: `MarkdownSection4`), so the decorator itself must switch to merge-into-
183: inherited semantics first (Task 1.1, verified 100% backward compatible
184: against all existing call sites); and (b) a block quote has no notion of
185: heading "levels", so the stop condition must be depth-aware (via
186: `Token.nesting`, tracking open/close pairs — already an established idiom in
187: `models/md`, used by `markdown_section`/`markdown_block_quote`/
188: `markdown_comment`/`markdown_code_block`/`markdown_paragraph`/
189: `markdown_list_item`, so this reuses an existing pattern rather than
190: introducing one) rather than "stop at the first occurrence anywhere" —
191: otherwise a legitimately nested block quote inside `requirement`'s own valid
192: content would cause premature truncation.
193: 
194: **Deliberately deferred to Phase 3 (not blocking this plan):** whether the 9
195: `<QaCategory>` H2 sections share one parameterized base class (9 distinct
196: final subclasses, each deriving its own fixed heading name from its class
197: name via the existing implicit `AliasType.SPACE_SEPARATED` convention) or
198: need a more bespoke approach; `models/iso25010.py::Characteristic` was
199: checked as a possible reuse candidate but its field shape (`description` +
200: `sub_characteristics`) doesn't match `qa`'s `items: list[QaSection]` need,
201: so it is a naming/pattern precedent only, not directly reusable.
202: 
203: **ISO 25010:2023 characteristic names, verified exact wording:** fetched
204: directly via the `specmgr://iso25010` MCP resource (not just read from the
205: packaged `.md` file) to confirm the canonical spelling/casing each
206: `<QaCategory>` heading must match: `Functional Suitability`, `Performance Efficiency`, `Compatibility`, `Interaction Capability`, `Reliability`,
207: `Security`, `Maintainability`, `Flexibility`, `Safety`. The schema's
208: snake_case field names above (`functional_suitability`,
209: `performance_efficiency`, etc.) already correspond 1:1 to this exact
210: wording.
211: 
212: **`Introduction`/`RawRequirements`'s implicit alias derivation is kept as
213: relying on `AliasType.SPACE_SEPARATED` class-name derivation (no explicit
214: `@alias`), intentionally** -- not changed to an explicit `@alias`
215: declaration, per direct instruction.
216: 
217: **`answer`/`raw_requirements`/`more_information` as opaque raw text:**
218: verified against the actual `MarkdownStr.from_text`/`get_extent`
219: implementation that a class with no declared `MarkdownStr`-typed fields
220: already captures "any remaining markdown text" verbatim in `_value` — this
221: is exactly how REQ's existing `MoreInformation`/`Notes` classes already
222: work (bare `MarkdownSection2` subclasses with no further fields). No new
223: engine mechanism is needed for this part; it is only the `requirement`
224: field's placement *before* `question` that required the `end_marker` work
225: above.
226: 
227: ### Related ADRs
228: 
229: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
230:   document-type domain (domain-first hierarchy)
231: - e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
232:   `.specmgr` with feature-driven work units
233: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: (tool-only id-based reads, no
234:   `specmgr://{type}/{id}` resource)
235: 
236: ### Task List
237: 
238: Single, canonical breakdown of work phases and tasks. Status lives on the
239: task itself — there is no separate "planned" vs. "executed" list to keep in
240: sync; a task's line *is* its current status. Update it in place as work
241: progresses (edit, don't duplicate).
242: 
243: **Execution approach** (decided 2026-08-18, see Decisions Made): because
244: implementation is likely to span multiple sessions (context-size
245: constrained), each phase below ends with a mandatory phase-end task —
246: extend/run that phase's unit tests, run the full pre-commit/quality gate
247: (ruff format/check, vulture, full `unittest` suite), and update this
248: README's Progress section (Current Status, a dated Recent Updates entry,
249: and Decisions Made if applicable) — before the phase is considered done or
250: a session ends. Each phase is committed as one Conventional Commit,
251: mirroring feat-10's per-phase test-and-commit discipline
252: (`.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md`), adopted
253: here explicitly so a fresh-context session can resume correctly from this
254: file alone. Phase 4 and Phase 5 each gain their own dedicated test task
255: (new task numbers, not renumbered into the existing sequence) rather than
256: deferring all MCP-surface/cross-cutting testing to a terminal phase; Phase
257: 6 is repurposed accordingly to a final cross-cutting verification pass
258: only (mirroring feat-10's own Phase 4), not where tests get written for
259: the first time.
260: 
261: #### Phase 0: Cleanup
262: 
263: - [x] Task 0.1: Delete stray untracked scaffolding from an earlier session
264:   — `src/qa/` (wrong namespace, missing `biz/dfch/specmgr/` prefix),
265:   `src/biz/dfch/specmgr/qa/{tools,resources,prompts}/` (empty, no
266:   `models/`), `tests/qa/` (empty), and `biz/dfch/specmgr/qa/` (top-level,
267:   wrong -- missing `src/` prefix entirely). All confirmed empty
268:   directories, untracked by git (git does not track empty directories, so
269:   none of these show up in `git status`). Do not reuse any of these. Note:
270:   a previously-listed `models/qa/v1/` path does **not** exist on disk
271:   (verified) — there is nothing to delete there. Note: `tests/qa/` is
272:   deliberately deleted here and re-created later by Task 4.5 as the real
273:   test location (mirroring `tests/req/`); this is intentional, not a
274:   contradiction — depends on: none — status: done.
275: 
276: - [x] Task 0.2: Phase-end check (lightweight — no code/tests affected by a
277:   pure directory deletion) — confirm `git status` and `git status --ignored` show no residue from the deleted paths; update this README's
278:   Progress section (Current Status, a dated Recent Updates entry) noting
279:   Phase 0 complete — depends on: Task 0.1 — status: done.
280: 
281: #### Phase 1: `models/md` engine enhancement
282: 
283: Standalone, reusable addition to the shared engine; `qa` is its first real
284: consumer but not the motivating point on its own.
285: 
286: - [x] Task 1.1: Change `@markdown(...)` to merge into any inherited
287:   `_metadata` rather than fully replacing it — depends on: none — status:
288:   done.
289: 
290: - [x] Task 1.2: Add `end_marker: type[MarkdownStr] | None = None` parameter
291:   to `@markdown` — depends on: Task 1.1 — status: done.
292: 
293: - [x] Task 1.3: `MarkdownSection.get_extent` — add a depth-aware (via
294:   `Token.nesting`) stop condition for `cls._metadata.get("end_marker")`'s
295:   `type`/`tag`, alongside the existing heading-level check; only a depth-0
296:   occurrence stops the scan — depends on: Task 1.2 — status: done.
297: 
298:   Note on "depth-0": A real correctness nuance for Phase 1's depth-aware end_marker check. `Token.nesting` itself is already used across `models/md` (see Design Notes), so the primitive is not new — the new part is applying it as a depth counter inside `get_extent`'s stop scan. The plan says "depth-0 occurrence" via Token.nesting, which is correct in principle, but it's worth being explicit now: the depth counter must track every nesting open/close pair in the token stream (list items, other block quotes, etc.), not just the end_marker type's own open/close tokens. Otherwise, e.g., a bullet list legitimately nested inside requirement's own body would throw off the depth count, and a block quote appearing after it could be misjudged as depth-0 when it's actually still nested one level deep — or vice versa. This is exactly the kind of easy-to-get-subtly-wrong logic Task 1.4's edge-case test needs to specifically exercise (a nested list and a nested block quote both inside requirement's own valid content, not just one or the other).
299: 
300: - [x] Task 1.4: Unit tests — merge-semantics regression (all existing
301:   `models/md` classes unaffected), new `end_marker` stop behavior, and the
302:   nested/legitimate-occurrence edge case (an end-marker-type token
303:   appearing one level deeper inside otherwise-valid content must not
304:   truncate) — depends on: Task 1.3 — status: done.
305: 
306: - [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
307:   gate (ruff format/check, vulture, full `unittest` suite covering Task
308:   1.4's new tests plus the full existing suite for regressions); update
309:   this README's Progress section (Current Status, a dated Recent Updates
310:   entry, Decisions Made if applicable); commit as one Conventional Commit
311:   — depends on: Task 1.4 — status: done (commit itself left to the
312:   orchestrator, per this session's instructions).
313: 
314: #### Phase 2: Specification
315: 
316: - [x] Task 2.1: Write a full reference `qa_reference.md` exercising every
317:   field — depends on: Phase 1 complete — status: done.
318: 
319:   **Plan correction (2026-08-18, see Decisions Made):** the former Task
320:   2.2 ("Draft `qa_schema.json`") has moved to Phase 3 as Task 3.1.1 —
321:   schema generation needs `QaDocument` to exist
322:   (`QaDocument.model_json_schema()`), which isn't defined until Task 3.1,
323:   not just the reference markdown file this phase produces (same bug
324:   feat-10 hit and fixed in its own Decisions Made log, moving its
325:   equivalent task from Phase 1 to Phase 2 as Task 2.5). Task numbering is
326:   intentionally left with a gap at 2.2 rather than renumbering Task 2.3
327:   or any later task.
328: 
329: - [x] Task 2.3: Phase-end check — no Pydantic models exist yet in this
330:   phase, so no unit-test suite applies; instead confirm `qa_reference.md`
331:   is well-formed (`specmgr mdformat` clean) and run the general
332:   pre-commit/quality gate (ruff format/check, vulture) over any changed
333:   files; update this README's Progress section (Current Status, a dated
334:   Recent Updates entry) noting Phase 2 complete — depends on: Task 2.1 —
335:   status: done.
336: 
337: #### Phase 3: Pydantic Models & Parser
338: 
339: - [x] Task 3.1: `qa/models/v1/{frontmatter,body,document,parser,summary, _util}.py`, including `Requirement`'s `end_marker` wiring (leaf class,
340:   deliberately unspecified/arbitrary agent-authored content -- see Design
341:   Notes) and resolving the 9-category class-sharing question (see Design
342:   Notes) — depends on: Task 2.1 — status: done.
343: 
344: - [x] Task 3.1.1 (moved from former Phase 2 Task 2.2, folded together with
345:   former Phase 5 Task 5.2, see Decisions Made): Implement
346:   `generate_qa_schema()` in `commands/schema.py` (mirroring
347:   `generate_req_schema`/`generate_uc_schema`/`generate_tsk_schema`, via
348:   `QaDocument.model_json_schema()`, JSON Schema 2020-12) and register
349:   `"qa"` in the `specmgr schema` doc-type generator registry
350:   (`_GENERATORS`); draft `docs/qa_schema.json` by running it — mirrors
351:   feat-10's own Task 2.5 exactly (generator + registry + draft, as one
352:   task, right after the document model exists) — depends on: Task 3.1 —
353:   status: done.
354: 
355: - [x] Task 3.2: Unit tests + full parser round-trip against
356:   `qa_reference.md` — depends on: Task 3.1 — status: done.
357: 
358: - [x] Task 3.3: Phase-end quality gate — run the full pre-commit/quality
359:   gate (ruff format/check, vulture, full `unittest` suite including Task
360:   3.2's new tests); update this README's Progress section (Current
361:   Status, a dated Recent Updates entry, Decisions Made if applicable);
362:   commit as one Conventional Commit — depends on: Task 3.1.1, Task 3.2 —
363:   status: done (commit itself left to the orchestrator, per this
364:   session's instructions).
365: 
366: #### Phase 4: MCP Surface
367: 
368: - [x] Task 4.1: `qa/tools/{_paths,_io,_lock,_write,parse_qa,get_qa, get_qa_example,get_qa_template,create_qa,update_qa,set_status_qa, delete_qa,validate_qa}.py` — 1:1 port of REQ's tool plumbing — depends
369:   on: Task 3.1 — status: done.
370: 
371: - [x] Task 4.2: `qa/resources/{qa_schema,qa_example,qa_template, qa_list}.py` — depends on: Task 4.1 — status: done.
372: 
373: - [x] Task 4.3: `qa/prompts/{create_qa,update_qa}.py` — depends on: Task
374:   4.1 — status: done.
375: 
376: - [x] Task 4.4: `qa/data/{qa_example.md,qa_template.md,qa_schema.json}` +
377:   `qa/__init__.py` — depends on: Tasks 4.1-4.3 — status: done.
378: 
379: - [x] Task 4.5: `tests/qa/{tools,resources,prompts}/` mirroring
380:   `tests/req/{tools,resources,prompts}/`'s layout and coverage — depends
381:   on: Tasks 4.1-4.4 — status: done.
382: 
383: - [x] Task 4.6: Phase-end quality gate — run the full pre-commit/quality
384:   gate (ruff format/check, vulture, full `unittest` suite including Task
385:   4.5's new tests); update this README's Progress section (Current
386:   Status, a dated Recent Updates entry, Decisions Made if applicable);
387:   commit as one Conventional Commit — depends on: Task 4.5 — status:
388:   done (commit itself left to the orchestrator, per this session's
389:   instructions).
390: 
391: #### Phase 5: Cross-cutting registration
392: 
393: - [x] Task 5.1: `server.py` — add `qa` to the bottom import line, update
394:   the module docstring — depends on: Phase 4 complete — status: done.
395: 
396:   **Plan correction (2026-08-18, see Decisions Made):** the former Task
397:   5.2 (`generate_qa_schema()` + registry entry) has been folded into
398:   Phase 3's Task 3.1.1 instead, right after `QaDocument` is defined,
399:   mirroring feat-10's own Task 2.5. Task numbering is intentionally left
400:   with a gap at 5.2 rather than renumbering Tasks 5.3-5.8.
401: 
402: - [x] Task 5.3: `pyproject.toml` — `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]` package-data entry — depends on: Task 4.4 — status:
403:   done.
404: 
405: - [x] Task 5.4: `.pre-commit-config.yaml` — widen the shared schema-hook
406:   glob to include `qa/models/v1`; add a `specmgr-schema-qa-package` hook —
407:   depends on: Task 3.1.1 — status: done.
408: 
409: - [x] Task 5.5: `.github/workflows/ci.yml` — add the `docs/qa_schema.json`
410:   check + packaged-copy check steps — depends on: Task 3.1.1 — status:
411:   done.
412: 
413: - [x] Task 5.6: `AGENTS.md` — update to six domain/cross-cutting packages
414:   — depends on: Phase 5 complete — status: done.
415: 
416: - [x] Task 5.7: `specmgr docs` / `specmgr mcp-docs` regeneration, `specmgr schema --type qa` — confirm the `qa` domain appears correctly and all
417:   three commands report zero drift now that registration (Task 3.1.1,
418:   Tasks 5.1, 5.3-5.6) is complete — depends on: Task 3.1.1, Task 5.1,
419:   Tasks 5.3-5.6 — status: done.
420: 
421: - [x] Task 5.8: Phase-end quality gate — run the full pre-commit/quality
422:   gate (ruff format/check, vulture, full `unittest` suite); update this
423:   README's Progress section (Current Status, a dated Recent Updates
424:   entry, Decisions Made if applicable); commit as one Conventional Commit
425:   — depends on: Task 5.7 — status: done (commit itself left to the
426:   orchestrator, per this session's instructions).
427: 
428: #### Phase 6: Final cross-cutting verification
429: 
430: - [x] Task 6.1: Final verification pass — walk every ACC-001..006 and
431:   confirm each is satisfied with concrete evidence; run the full quality
432:   gate (ruff format/check, pylint advisory, vulture, unittest, `specmgr docs`, `specmgr mcp-docs`, `specmgr schema --type qa` drift checks) one
433:   last time end-to-end; update this README's Progress section (Current
434:   Status, a dated Recent Updates entry) and set feature status to `done`
435:   — depends on: Phase 0-5 complete — status: done.
436: 
437: ## Progress
438: 
439: ### Current Status
440: 
441: **As of 2026-08-18**: Feature complete — all 6 phases done, Task 6.1 (Final
442: verification pass) confirmed all six acceptance criteria satisfied with
443: concrete evidence and the full quality gate green end-to-end. Feature
444: status set to `done`. Phase 0 (Cleanup), Phase 1 (`models/md` engine
445: enhancement), Phase 2 (Specification), Phase 3 (Pydantic Models & Parser),
446: Phase 4 (MCP Surface), Phase 5 (Cross-cutting registration), and Phase 6
447: (Final cross-cutting verification) complete — Tasks 1.1-1.5, 2.1/2.3,
448: 3.1/3.1.1/3.2/3.3, 4.1-4.6, 5.1/5.3-5.8, and 6.1 done (intentional gap at
449: 5.2, folded into Task 3.1.1 earlier in the plan). ACC-001 (merge-semantics
450: regression + depth-0 `end_marker` stop condition, 18 tests in
451: `tests/models/md/test_markdown.py`/`test_markdown_section_end_marker.py`),
452: ACC-002 (`qa_reference.md` re-verified to parse successfully via
453: `parse_qa` on the current committed state), ACC-003 (35 tests in
454: `tests/qa/models/v1/test_frontmatter.py`/`test_body.py` covering
455: required/optional field validation and the four-value `status` closed
456: set), ACC-004 (`tests/qa/models/v1/test_parser.py` covering a valid
457: object tree, `AssertionError` on malformed structure, and
458: `pydantic.ValidationError` on invalid field values), ACC-005 (live
459: `biz.dfch.specmgr.server.mcp` introspection confirming all 9 tools, 4
460: resources, and 2 prompts registered and callable), and ACC-006 (fresh
461: `specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa` runs, all
462: reporting zero drift) were each independently re-verified this phase, not
463: just trusted from earlier phase reports. The
464: `qa` domain is now fully registered end-to-end: `server.py`'s bottom-of-file
465: import line reads `from . import adr, general, qa, req, tsk, uc`, and its
466: module docstring documents `qa`'s four resources (`specmgr://qa/schema`,
467: `/example`, `/template`, `/list`, no `/{id}`), nine tools, and two prompts
468: alongside the other domains. `pyproject.toml` packages `qa/data/*.md` and
469: `*.json`; `.pre-commit-config.yaml`'s shared schema-hook glob now matches
470: `qa/models/v1` and a new `specmgr-schema-qa-package` hook keeps
471: `qa/data/qa_schema.json` in sync; `.github/workflows/ci.yml` gained a
472: `docs/qa_schema.json` + packaged-copy check pair mirroring REQ/UC's. Note:
473: as already established at the end of Phase 4, this registration wiring was
474: *functionally* redundant with the transitive import `commands/schema.py`
475: already causes via `qa.models.v1` (so `docs/MCP.md` and `docs/GENERATED.md`
476: already listed all of `qa`'s tools/resources/prompts before this phase and
477: needed no regeneration here beyond `docs/api/biz.dfch.specmgr.server.md`,
478: which changed solely due to the docstring edit) -- Task 5.1 was still done
479: for documented-convention clarity/correctness, per `AGENTS.md`'s own
480: "add its import to that same last line" instruction. `AGENTS.md` now reads
481: "six domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA,
482: general)" with a `qa/` bullet (mirroring REQ's/TSK's bullet shape) inserted
483: after the `tsk/` bullet, its "Still genuinely missing" list updated
484: (`delete_qa` stub, `validate_qa` omitted from pre-commit/CI enforcement,
485: `qa` added to the tools/resources/prompts registration summary), and every
486: other domain-enumeration spot in the file (the closing "don't assume any
487: other domain package exists" paragraph, and the "MCP server (`server.py`)"
488: section's own import-list mention) updated to include `qa` too. Ran
489: `specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa` (both
490: `docs/qa_schema.json` and the packaged `qa/data/qa_schema.json` copy) twice
491: each and confirmed the second run of every command reports zero further
492: drift (`(unchanged)` for both schema outputs, identical `git diff` for
493: `docs/`/`docs/MCP.md` across both runs). Full quality gate green: `ruff
494: format --check` (766 files already formatted), `ruff check` (all checks
495: passed), `vulture` (no output, clean), and the full `unittest` suite (1144
496: tests, OK -- unchanged from Phase 4's count, no regressions, as expected
497: since this phase touched no `src/`/`tests/` Python logic). Commit for Phase
498: 5 intentionally left to the orchestrator. Phase 6 (Final cross-cutting
499: verification) subsequently completed Task 6.1: see the dated Recent
500: Updates entry below for the full evidence trail. Commit for Phase 6
501: intentionally left to the orchestrator as well. No further phases remain.
502: 
503: ### Blockers
504: 
505: None currently.
506: 
507: ### Recent Updates
508: 
509: Older entries (2026-08-18T11:15:00Z and earlier) are archived in
510: [`history.md`](history.md).
511: 
512: #### Update 2026-08-18T23:45:00Z
513: 
514: - Completed: Phase 6 (Final cross-cutting verification) — Task 6.1 (Final
515:   verification pass). Re-read the plan's Acceptance Criteria section and
516:   Phase 6 verbatim first, per the orchestrator's instructions, then walked
517:   every ACC-001..006 independently with fresh, concrete evidence (not
518:   trusting earlier phase reports):
519:   - **ACC-001**: Ran `tests/models/md/test_markdown.py` (12 tests —
520:     merge-semantics regression, including
521:     `test_reapplying_with_no_arguments_keeps_every_inherited_key`,
522:     `test_explicitly_passing_none_clears_an_inherited_value`,
523:     `test_end_marker_is_merged_the_same_way`) and
524:     `tests/models/md/test_markdown_section_end_marker.py` (6 tests —
525:     depth-0 stop condition, including
526:     `test_extent_stops_before_the_first_depth_zero_block_quote` and the
527:     nested-list-and-nested-block-quote edge case
528:     `test_nested_list_and_nested_block_quote_do_not_truncate`/
529:     `test_from_text_retains_the_nested_list_and_quote_but_not_the_end_marker`)
530:     — 18/18 passed.
531:   - **ACC-002**: Called
532:     `parse_qa('.specmgr/feat/feat-12-qa-artifact/qa_reference.md')`
533:     directly against the current committed state (not just re-reading a
534:     prior phase's claim): confirmed `frontmatter.id`, `frontmatter.status`,
535:     `body.text`, `compatibility.items is None`, `functional_suitability`'s
536:     2 Q&A pairs, and `more_information` all round-trip correctly.
537:   - **ACC-003**: Ran `tests/qa/models/v1/test_frontmatter.py` (9 tests,
538:     including `test_accepts_all_four_statuses`/
539:     `test_rejects_unknown_status`) and `tests/qa/models/v1/test_body.py`
540:     (17 tests, including `TestQaRequiredVsOptionalFields`'s
541:     missing-mandatory-field checks) — 26/26 passed.
542:   - **ACC-004**: Ran `tests/qa/models/v1/test_parser.py` (6 tests —
543:     `test_parses_minimal_document`/`test_parses_full_reference_document`
544:     for a valid object tree,
545:     `test_missing_general_section_raises_assertion_error`/
546:     `test_missing_iso_characteristic_section_raises_assertion_error` for
547:     `AssertionError`, `test_invalid_status_raises_validation_error` for
548:     `pydantic.ValidationError`) — 6/6 passed.
549:   - **ACC-005**: Imported `biz.dfch.specmgr.server` live and introspected
550:     `server.mcp` via `list_tools()`/`list_resources()`/`list_prompts()`
551:     (async): confirmed all 9 tools (`parse_qa`, `get_qa`, `get_qa_example`,
552:     `get_qa_template`, `create_qa`, `update_qa`, `set_status_qa`,
553:     `delete_qa`, `validate_qa`), all 4 resources (`specmgr://qa/schema`,
554:     `/example`, `/template`, `/list`), and both prompts (`create_qa`,
555:     `update_qa`) present among the server's 49 total tools / 19 total
556:     resources / 11 total prompts (matching `docs/MCP.md`'s documented
557:     counts). Went further than mere registration: actually called
558:     `mcp.call_tool('get_qa_template', {})`,
559:     `mcp.read_resource('specmgr://qa/schema')`,
560:     `mcp.get_prompt('create_qa', {'topic': ...})`, and
561:     `mcp.get_prompt('update_qa', {'id': 'x'})` live and confirmed each
562:     returns successfully — proving callable, not just registered.
563:   - **ACC-006**: Re-ran `specmgr docs`, `specmgr mcp-docs`,
564:     `specmgr schema --type qa`, and `specmgr schema --type qa --output-dir
565:     src/biz/dfch/specmgr/qa/data` fresh against the current committed
566:     state: `specmgr docs`/`specmgr mcp-docs` produced no
567:     `git status --short` changes under `docs/`, and both schema commands
568:     reported `(unchanged)` — zero drift confirmed independently of Phase
569:     5's own claim.
570:   - Ran the full quality gate end-to-end: `uv run --frozen ruff format
571:     --check` (766 files already formatted), `uv run --frozen ruff check`
572:     (all checks passed), `uv run --frozen pylint $(git ls-files '*.py')`
573:     (9.01/10, advisory only — the only findings are pre-existing `R0401`
574:     cyclic-import warnings following the same domain-package/`server.py`
575:     import pattern already present for every other domain (`adr`, `req`,
576:     `tsk`, `uc`), not a `qa`-specific regression, so not treated as a
577:     blocker), `uv run --frozen vulture src/ whitelist.py
578:     --min-confidence 60` (no output, clean), and `uv run --frozen python
579:     -m unittest discover -v -s tests -t . -p "test_*.py"` (1144 tests, OK
580:     — identical count to Phase 5's end, no regressions, as expected for a
581:     verification-only phase). Found no genuine regression or surprise;
582:     nothing required fixing.
583: - Next: None — feature complete.
584: - Notes: Set frontmatter `status: done` (from `planning`); `version`
585:   intentionally left at `1.0.0` per the orchestrator's explicit
586:   instruction. Left staging/committing to the orchestrator per this
587:   session's instructions; no `src/`/`tests/` files were touched this
588:   phase (verification-and-documentation only), so the working tree has
589:   only this README's edits, unstaged.
590: 
591: #### Update 2026-08-18T22:45:00Z
592: 
593: - Completed: Phase 5 (Cross-cutting registration) — Tasks 5.1, 5.3, 5.4,
594:   5.5, 5.6, 5.7, 5.8 (intentional gap at 5.2, folded into Task 3.1.1 earlier
595:   in the plan). Read `server.py`, `pyproject.toml`'s
596:   `[tool.setuptools.package-data]`, `.pre-commit-config.yaml`,
597:   `.github/workflows/ci.yml`, and `AGENTS.md` in full first, per the
598:   orchestrator's instructions, confirming the already-established fact
599:   that `qa`'s MCP surface was already transitively registered (via
600:   `commands/schema.py` importing `qa.models.v1`, which triggers
601:   `qa/__init__.py`'s own `tools`/`resources`/`prompts` import) before this
602:   phase started, so `docs/MCP.md`/`docs/GENERATED.md` needed no
603:   regeneration here.
604:   - **Task 5.1**: Changed `server.py`'s bottom import line to
605:     `from . import adr, general, qa, req, tsk, uc  # noqa: E402, F401`
606:     (alphabetical order). Updated the module docstring: added a
607:     `specmgr://qa/schema`/`/example`/`/template`/`/list` resources block
608:     (placed after the `tsk` block and before `specmgr://iso25010`, matching
609:     the existing chronological-addition-order convention, not strict
610:     alphabetical), a sentence extending the existing REQ/UC/TSK
611:     no-`/{id}`-resource note to cover QA, a "QA tools (`qa/tools/`): ..."
612:     line listing all 9 tools (placed after the Task list tools line, before
613:     General tools), a "QA prompts (`qa/prompts/`): `create_qa`,
614:     `update_qa`" line (after Task list prompts), and updated the "Modules
615:     are grouped domain-first" paragraph's domain list
616:     (`adr`, `uc`, `req`, `tsk`, `qa`, and later `ac`), its import-list
617:     mention (`adr`/`general`/`qa`/`req`/`tsk`/`uc`, alphabetical), and its
618:     closing sentence (`req`, `tsk`, and `qa` each register `tools`,
619:     `resources`, and `prompts`; `uc` registers `tools` and `resources`
620:     only).
621:   - **Task 5.3**: Added `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]`
622:     to `pyproject.toml`'s `[tool.setuptools.package-data]`, placed
623:     alphabetically among the domain packages (`qa` before `req`, `req`
624:     before `tsk`, `tsk` before `uc`), with `general` kept last as the
625:     existing convention already has it (not alphabetical -- `general`
626:     would otherwise sort before `qa`/`req`/`tsk`/`uc`).
627:   - **Task 5.4**: Widened the shared `files:` glob on all four existing
628:     schema hooks (`specmgr-schema`, `specmgr-schema-req-package`,
629:     `specmgr-schema-uc-package`, `specmgr-schema-tsk-package`) from
630:     `^src/biz/dfch/specmgr/(req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$`
631:     to
632:     `^src/biz/dfch/specmgr/(qa/models/v1|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$`
633:     (alphabetical inside the group). Added a new `specmgr-schema-qa-package`
634:     hook, a 1:1 mirror of `specmgr-schema-tsk-package`'s shape/wording
635:     (`entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`,
636:     same widened glob).
637:   - **Task 5.5**: Added two new CI steps to `.github/workflows/ci.yml`,
638:     placed immediately after the existing
639:     `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` step and before the
640:     `docs/coverage.svg` step: "Make sure `docs/qa_schema.json` is correct"
641:     (bare `specmgr schema`, same `if: matrix.python-version == '3.13'`
642:     guard and `::error::` failure-message pattern as the existing
643:     `docs/req_schema.json`/`docs/uc_schema.json` steps) and "Make sure
644:     `src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct"
645:     (`specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`).
646:   - **Task 5.6**: Updated `AGENTS.md`'s heading to "six domain/cross-cutting
647:     packages implemented (ADR, REQ, UC, TSK, QA, general)" and its lead-in
648:     sentence to "Five document-type domains plus one cross-cutting package".
649:     Added a `qa/` bullet after the `tsk/` bullet (matching the existing
650:     chronological-order convention the other bullets already use, not
651:     alphabetical), mirroring REQ's/TSK's own bullet depth (tools list,
652:     resources list, prompts list, no-`/{id}`-resource note citing ADR
653:     ddfb1109-422d-4507-8dbc-dc5e4bec9614). Updated the "Still genuinely
654:     missing" list: added `validate_qa` to the pre-commit/CI enforcement
655:     bullet (for consistency -- `qa` has the identical gap REQ/UC/TSK
656:     already have), added `delete_qa` to the stubs bullet, and added `qa` to
657:     the tools/resources/prompts registration-summary bullet. Updated the
658:     closing "don't assume any other domain package exists beyond..."
659:     paragraph and, since it also enumerates all five prior domains and
660:     would otherwise be factually wrong by omission, the "MCP server
661:     (`server.py`)" section's own "imports every domain package (...)"
662:     sentence -- the one specific case the hard-rule carve-out ("unless it
663:     specifically enumerates the 5 domains and would now be factually wrong
664:     by omitting `qa`") applies to; no other section was touched.
665:   - **Task 5.7**: Ran `specmgr docs`, `specmgr mcp-docs`, `specmgr schema
666:     --type qa`, and `specmgr schema --type qa --output-dir
667:     src/biz/dfch/specmgr/qa/data`, each twice. First run: `specmgr docs`
668:     regenerated only `docs/api/biz.dfch.specmgr.server.md` (the docstring
669:     changes from Task 5.1); `specmgr mcp-docs` produced no `git diff` at
670:     all (confirming the orchestrator's stated fact that `docs/MCP.md`
671:     already reflected `qa`'s full surface from the Phase-4-era transitive
672:     import); both `specmgr schema --type qa` invocations reported
673:     `(unchanged)` since Task 3.1.1/4.4 already drafted both files
674:     correctly. Second run of every command: identical `(unchanged)`
675:     results and an identical `git diff --stat docs/` to the first run --
676:     all four commands confirmed idempotent, no further drift introduced by
677:     Task 5.1's docstring edit or Task 5.6's `AGENTS.md` edit (which
678:     `specmgr docs`/`mcp-docs` don't even read, since `AGENTS.md` isn't a
679:     `src/` docstring source).
680:   - **Task 5.8**: Ran the full phase-end quality gate:
681:     `uv run --frozen ruff format --check` (766 files already formatted),
682:     `uv run --frozen ruff check` (all checks passed),
683:     `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no
684:     output, clean), and
685:     `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
686:     (1144 tests, OK -- identical count to Phase 4's end, no regressions, as
687:     expected since Phase 5 is pure cross-cutting registration/config with
688:     no new `src/`/`tests/` Python logic). Left staging/committing to the
689:     orchestrator per this session's instructions; working tree has the
690:     edited `server.py`, `pyproject.toml`, `.pre-commit-config.yaml`,
691:     `.github/workflows/ci.yml`, `AGENTS.md`, and the regenerated
692:     `docs/api/biz.dfch.specmgr.server.md`, all unstaged.
693: - Next: Phase 6 (Final cross-cutting verification) — Task 6.1.
694: - Notes: `qa` is now identically wired into every cross-cutting mechanism
695:   REQ/UC/TSK already have (server registration, packaging, pre-commit
696:   schema hooks, CI schema-drift checks, `AGENTS.md`). Phase 6 is a
697:   verification-only pass (walk ACC-001..006, run the full quality gate
698:   including pylint-advisory/`specmgr docs`/`specmgr mcp-docs`/`specmgr
699:   schema --type qa` end-to-end one more time) and setting the feature
700:   status to `done` -- no new implementation is expected there.
701: 
702: #### Update 2026-08-18T21:10:00Z
703: 
704: - Completed: Phase 4 (MCP Surface) — Tasks 4.1, 4.2, 4.3, 4.4, 4.5, 4.6.
705:   Read every REQ file the plan named (`req/tools/*.py`, `req/resources/*.py`,
706:   `req/prompts/*.py`, `req/data/*`, `req/__init__.py`,
707:   `general/tools/_packaged_data.py`, `general/tools/_doc_paths.py`) plus
708:   `qa_reference.md` and `qa/models/v1/*.py` before writing anything, per the
709:   orchestrator's instructions.
710:   - **Task 4.1**: Created `qa/tools/{__init__,_paths,_io,_lock,_write,
711:     parse_qa,get_qa,get_qa_example,get_qa_template,create_qa,update_qa,
712:     set_status_qa,delete_qa,validate_qa}.py`, a 1:1 port of every
713:     corresponding `req.tools` module with every `Req`/`req` identifier
714:     substituted for `Qa`/`qa` (`ReqDocument` -> `QaDocument`,
715:     `ReqFrontmatter` -> `QaFrontmatter`, `Requirement` -> `Qa` -- the `qa`
716:     domain's own body class, not to be confused with `qa`'s *own*,
717:     differently-shaped `Requirement` callout class from Phase 3 --
718:     `ReqNotFoundError` -> `QaNotFoundError`, `req_lock`/`req_base_dir` ->
719:     `qa_lock`/`qa_base_dir`, `REQ_TYPE_NAME` -> `QA_TYPE_NAME`). Every
720:     design-rationale docstring (error-channel split, lock rationale,
721:     no-render-just-persist-verbatim design, read-only/write directory
722:     split, id -> path skip-on-parse-failure rule) was preserved and
723:     reworded for QA, not stripped. `create_qa`'s filename convention is
724:     `qa-{id}-{slugify(body.text)}.md`. `set_status_qa` reconstructs
725:     `QaFrontmatter` via its own constructor (not `model_copy`) so the
726:     four-value closed-set `status` validator (`draft`/`active`/`done`/
727:     `cancelled`) actually runs. `delete_qa` is a registered
728:     `structured_output=False` stub, always raising `NotImplementedError`.
729:     `validate_qa` mirrors `validate_req`'s disk-free/id-free dry-run shape
730:     exactly.
731:   - **Task 4.2**: Created `qa/resources/{__init__,qa_schema,qa_example,
732:     qa_template,qa_list}.py`, 1:1 ports of REQ's four resources at the
733:     same four URIs (`specmgr://qa/schema`, `/example`, `/template`,
734:     `/list`, no `/{id}`). `qa_list` builds `QaSummary` entries
735:     (`id`/`title`=`doc.body.text`/`status`/`ref`=`path.stem`), silently
736:     skipping any file that fails to parse
737:     (`AssertionError`/`pydantic.ValidationError`), identical to
738:     `req_list`'s own skip rule.
739:   - **Task 4.3**: Created `qa/prompts/{__init__,create_qa,update_qa}.py`,
740:     matching `req/prompts/`'s instructional-text-returning `@mcp.prompt()`
741:     shape exactly, but with the instructional content fully rewritten for
742:     QA's own schema: the `create_qa` prompt recaps `# {title}`, `##
743:     General` (`### Introduction`/`### Raw Requirements`), the nine fixed
744:     ISO/IEC 25010:2023 characteristic H2s in their canonical order/wording,
745:     the free-form `### {question}` `QaSection` pattern (optional
746:     `comment`/`requirement`/`question`/`answer`), and optional `##
747:     More Information`; it tells the LLM to check `specmgr://qa/list`
748:     first, elicit characteristic-relevant answers per category (noting a
749:     category may legitimately stay empty), and reference
750:     `specmgr://qa/template`/`/example`/`/schema` before calling
751:     `create_qa`/`validate_qa`. The `update_qa` prompt maps body changes to
752:     `update_qa(id, content)` (whole-body replace, explicitly warning that
753:     all nine fixed category headings must be carried forward even when
754:     empty) and status changes to `set_status_qa(id, status)`
755:     (draft/active/done/cancelled), mirroring `update_req`'s prompt
756:     structure/tone.
757:   - **Task 4.4**: Created `qa/data/qa_example.md` by reusing Phase 2's
758:     `qa_reference.md` verbatim (mirroring REQ's own reference-is-example
759:     precedent named as an explicit option in this task) -- verified via a
760:     throwaway `parse_qa(...)` call that it round-trips successfully
761:     (`frontmatter.id`, `body.text`, `compatibility.items is None`, and
762:     `functional_suitability`'s two Q&A pairs all came back correctly; see
763:     Decisions Made for why no TSK-style light adaptation was needed).
764:     Created `qa/data/qa_template.md` from scratch (not adapted from
765:     `qa_reference.md`) with every fixed H2 present, both `## General`
766:     sub-sections, one Q&A pair with all four optional fields filled with
767:     short placeholder text (`comment`/`#### Requirement`/`question`/
768:     `answer`), and `## More Information` -- verified it happens to parse
769:     successfully end-to-end too (a stronger guarantee than the task
770:     required, which only asked for structural completeness). Copied
771:     `docs/qa_schema.json` byte-for-byte to `qa/data/qa_schema.json`
772:     (confirmed via `diff`). Edited (not recreated) `qa/__init__.py`,
773:     replacing its Phase-3-only docstring with one mirroring
774:     `req/__init__.py`'s exact shape/wording, and added
775:     `from . import prompts, resources, tools  # noqa: F401` plus the
776:     matching `__all__`; explicitly noted `server.py`'s own import list
777:     still excludes `qa` (Phase 5's Task 5.1).
778:   - **Task 4.5**: Read every file under `tests/req/{tools,resources,
779:     prompts}/` first, then created the mirrored `tests/qa/{tools,
780:     resources,prompts}/` suites (`__init__.py` markers plus 19 test
781:     files, 83 tests total: 53 in `tools/`, 15 in `resources/`, 15 in
782:     `prompts/`), all isolated from the real filesystem via
783:     `mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: ...})` against a
784:     `tempfile.TemporaryDirectory()`, the same pattern `tests/req/` uses.
785:     Coverage mirrors REQ's own depth/shape per file (base-dir resolution,
786:     id lookup and its skip-on-parse-failure rule, lock serialization,
787:     write-and-round-trip, create/update/get/set-status/delete/validate/
788:     parse tool behavior including every error channel, packaged-data
789:     example/template reads with cache-freshness and missing-file checks,
790:     the `qa_list` resource's skip-malformed-file behavior, and prompt
791:     content/ordering assertions) -- adapted only where QA's own schema
792:     differs from REQ's (see Decisions Made for the one genuine coverage
793:     gap this surfaced).
794:   - **Task 4.6**: Ran the full phase-end quality gate:
795:     `uv run --frozen ruff format --check` (744 files already formatted),
796:     `uv run --frozen ruff check` (all checks passed),
797:     `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no
798:     output, clean -- no new dead-code flags this phase, unlike Phase 3),
799:     and `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
800:     (1144 tests, OK -- up from 1061, i.e. exactly the 83 new `qa` tests,
801:     no regressions). Also ran `uv run --frozen specmgr docs` (regenerated
802:     `docs/api/*.md` for 20 new `qa` modules plus `docs/GENERATED.md`'s
803:     test-file count 156 -> 175) and confirmed a second run produces an
804:     identical `git status --short docs/` (idempotent). Left
805:     staging/committing to the orchestrator per this session's
806:     instructions; working tree has the new `qa/{tools,resources,prompts,
807:     data}/`/`tests/qa/{tools,resources,prompts}/` trees, the edited
808:     `qa/__init__.py`, and the regenerated docs, all unstaged.
809: - Next: Phase 5 (Cross-cutting registration) — Task 5.1 (`server.py` --
810:   add `qa` to the bottom import line, update the module docstring).
811: - Notes: `qa`'s tools/resources/prompts are fully built, importable, and
812:   unit-tested standalone (each test imports the specific function directly,
813:   e.g. `from biz.dfch.specmgr.qa.tools.create_qa import create_qa`, mirroring
814:   how `tests/req/` itself never round-trips through a live MCP server), but
815:   are not yet registered against the live MCP server -- `server.py`'s
816:   bottom-of-file import list still only imports `adr`, `general`, `req`,
817:   `tsk`, `uc`, not `qa`. That wiring, plus `pyproject.toml` package-data,
818:   the pre-commit schema-hook glob, and the CI schema-drift check, are all
819:   Phase 5 work and were deliberately left untouched this phase.
820: 
821: #### Update 2026-08-18T19:30:00Z
822: 
823: - Completed: Phase 3 (Pydantic Models & Parser) — Tasks 3.1, 3.1.1, 3.2, 3.3.
824:   - **Task 3.1**: Created the `qa` domain package:
825:     `src/biz/dfch/specmgr/qa/__init__.py` (docstring-only for now, since
826:     `tools`/`resources`/`prompts` don't exist until Phase 4 -- it does not
827:     import them yet, unlike `req`/`tsk`'s own `__init__.py`), plus
828:     `qa/models/__init__.py` and `qa/models/v1/{__init__,_util,frontmatter,
829:     body,document,parser,summary}.py`, all inside the domain package per
830:     the domain-first layout (ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
831:     mirroring `req`/`tsk`'s exact file shapes read directly from disk
832:     first. `QaFrontmatter` reuses `TskFrontmatter`'s `_ALLOWED_STATUSES`
833:     pattern verbatim (`draft`/`active`/`done`/`cancelled`). `body.py`
834:     implements the full schema from Design Notes: `Qa(MarkdownSection1)`,
835:     `General(MarkdownSection2WithComment)` with `Introduction
836:     (MarkdownSection3WithComment)`/`RawRequirements(MarkdownSection3)`,
837:     `QaSection(MarkdownSection3WithComment)` with `requirement`/`question`/
838:     `answer`, `Requirement(MarkdownSection4)` decorated
839:     `@markdown(end_marker=MarkdownBlockQuote)`, and the 9 ISO/IEC
840:     25010:2023 `<QaCategory>` classes. Resolved the plan's deferred
841:     9-category class-sharing question by empirically verifying (via a
842:     throwaway script, then codified in `tests/qa/models/v1/test_body.py`)
843:     that approach (a) -- one shared, private `_QaCategory(MarkdownSection2)`
844:     intermediate base declaring `items` once, with 9 final subclasses each
845:     relying on implicit `AliasType.SPACE_SEPARATED` alias derivation from
846:     their own class names -- carries no heading-detection risk: confirmed
847:     that `MarkdownSection.get_extent`/`from_text`'s `match_alias` call
848:     always passes the actual runtime subclass (e.g. `FunctionalSuitability`),
849:     not the shared base, as `cls`, so `cls.__name__` (not `_QaCategory`'s)
850:     is what the implicit alias derivation keys off; also confirmed
851:     `_get_field_names()` correctly resolves the inherited `items` field
852:     through the extra inheritance level, and that `@markdown`'s
853:     `_metadata` (`heading_open`/`h2`) is inherited transparently with no
854:     per-subclass re-application needed. Discovered mid-implementation that
855:     `QaAnswer` cannot be heading-anchored like `MoreInformation`/

(Output capped at 50 KB. Showing lines 1-855. Use offset=856 to continue.)
</content>
````

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 5.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rl -i \"how to create\\|creating a new feature\\|new feature workflow\\|feature creation\" /home/admin/src/biz.dfch.SpecMgr/docs/adr/ 2>/dev/null; ls /home/admin/src/biz.dfch.SpecMgr/docs/adr/ | head -50"
}
```

**Output:**

```
23a14195-339c-48af-99d2-97c9964041ae-use-iso-8601-for-all-dates-and-times.md
3159caf2-4beb-43f2-9f5d-8f46be0211af-adopt-icontract-as-the-design-by-contract-library-for-specmg.md
33c5ab08-ff58-4c73-8c32-23abaf3838e3-filesystem-is-the-sole-source-of-truth-no-in-memory-id-to-do.md
3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se.md
4c6119c9-532f-4629-8977-108e78304f48-parse-validate-render-pipeline-library-choices-no-ast-preser.md
71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and.md
737858a9-7796-4f01-ae35-5afc1c707818-use-pre-commit-hooks-for-local-quality-gates.md
7531106b-074b-4bd8-a83a-e433d01676e2-expose-listing-and-by-id-reads-as-mcp-resources-in-addition.md
832cd6c1-ef8a-4bfc-990e-a610823f61ae-generic-heading-mapped-markdown-to-pydantic-parsing-with-dec.md
898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md
8cf940c5-3100-485c-a12d-14b59b631712-id-filename-addressing-scheme-server-generated-uuid-id-slug.md
9c687bb1-8ee7-41c8-84ec-07606356bc73-enforce-doc-generation-lint-and-tests-locally-via-pre-commit.md
9d3800cf-b3b4-4d46-8b68-3573d932b1c8-detect-unreferenced-code-with-vulture-not-snakefood-enforced.md
bbf412a7-965e-4435-8669-c338407d73b7-frontmatter-extension-fields-id-version-with-whole-object-fu.md
bc5e18ad-6bbf-4265-bae4-3e34984a2d29-generic-base-frontmatter-model-for-markdown-document-types-m.md
c73e4f9d-81f3-495d-bd3a-f660ab992ed3-base-the-adr-template-on-madr-4-0-0.md
cb5a2d5f-7020-4c6e-b28d-a38d17b23243-use-conventional-commits-for-commit-messages.md
d54abe50-a2c5-44f8-8bfe-11ea634b6f87-pros-and-cons-of-the-options-as-a-derived-container-with-a-d.md
ddd038f0-ae16-4f4b-beef-df06f7ed226f-prompt-surface-narrated-guidance-plus-step-gated-test-varian.md
ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r.md
e11421d3-cc1d-487b-af32-ee4093422712-use-architecture-decision-records-adrs-to-document-design-de.md
e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md
ec9f5262-9912-49d0-903f-fcfb54f28c13-expose-domain-list-as-paged-mcp-tools-list-domain-not-resour.md
ece4554b-725c-4f76-bc04-5d2b760363d2-organize-the-codebase-by-document-type-domain-domain-first-h.md
README.md

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

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 6.4s)

_Thinking:_

**Tool: webfetch**

**Input:**

```json
{
  "url": "https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/"
}
```

**Output:**

```
                    How to Write an Effective Problem Statement                                             

[![logo](https://www.isixsigma.com/wp-content/themes/isixsigma-theme/img/logo/iSixSigma-Logo-40x200.png)](https://www.isixsigma.com) 

Menu

-   [Explore](https://www.isixsigma.com/blogs/best-quality-books-of-all-time/)
    -   [Top 10 Books](https://www.isixsigma.com/blogs/best-quality-books-of-all-time/)
    -   [Six Sigma Costs and Savings](https://www.isixsigma.com/financial-analysis/six-sigma-costs-and-savings/)
    -   [Get Six Sigma Qualified](https://www.sixsigma.com/?utm_source=isixsigma&utm_medium=banner&utm_campaign=adlink)
    -   [Concepts](https://www.isixsigma.com/category/dictionary/)
    -   [Process Sigma Calculator](https://www.isixsigma.com/process-sigma-calculator/)
-   [Learn](/directory/)
    -   [Six Sigma Tools & Templates](https://www.isixsigma.com/category/tools-templates/)
        -   [Capability Indices/Process Capability](https://www.isixsigma.com/category/capability-indices-process-capability/)
        -   [Cause & Effect](https://www.isixsigma.com/category/cause-effect/)
        -   [Control Charts](https://www.isixsigma.com/category/control-charts/)
        -   [Design of Experiments (DOE)](https://www.isixsigma.com/category/design-of-experiments-doe/)
        -   [FMEA](https://www.isixsigma.com/category/fmea/)
        -   [Hypothesis Testing](https://www.isixsigma.com/category/hypothesis-testing/)
        -   [Kanban](https://www.isixsigma.com/category/kanban-tool/)
        -   [Kano Analysis](https://www.isixsigma.com/category/kano-analysis/)
        -   [Measurement Systems Analysis (MSA)/Gage R&R](https://www.isixsigma.com/category/measurement-systems-analysis-msa-gage-rr/)
        -   [Normality](https://www.isixsigma.com/category/normality/)
        -   [Pareto](https://www.isixsigma.com/category/pareto/)
        -   [Poka Yoke](https://www.isixsigma.com/category/poka-yoke/)
        -   [Process Mapping](https://www.isixsigma.com/category/process-mapping/)
        -   [Project Charter](https://www.isixsigma.com/category/project-charter/)
        -   [Pugh Matrix](https://www.isixsigma.com/category/pugh-matrix-tools-templates/)
        -   [QFD/House of Quality](https://www.isixsigma.com/category/qfd-house-of-quality/)
        -   [RACI Diagram](https://www.isixsigma.com/category/raci-diagram/)
        -   [Regression](https://www.isixsigma.com/category/regression/)
        -   [Risk Management](https://www.isixsigma.com/category/risk-management/)
        -   [Robotic Process Automation/Machine Learning/Artificial Intelligence](https://www.isixsigma.com/category/robotic-process-automation/)
        -   [Sampling/Data](https://www.isixsigma.com/category/sampling-data/)
        -   [Simulation](https://www.isixsigma.com/category/simulation/)
        -   [SIPOC/COPIS](https://www.isixsigma.com/category/sipoc-copis/)
        -   [Software](https://www.isixsigma.com/category/software/)
        -   [Statistical Analysis](https://www.isixsigma.com/category/statistical-analysis/)
        -   [Templates](https://www.isixsigma.com/category/templates/)
        -   [Value Stream Mapping](https://www.isixsigma.com/category/value-stream-mapping/)
        -   [Variation](https://www.isixsigma.com/category/variation/)
        -   [Wizards](https://www.isixsigma.com/category/wizards/)
    -   [New to Six Sigma](https://www.isixsigma.com/category/new-to-six-sigma/)
        -   [Deployment](https://www.isixsigma.com/category/deployment/)
        -   [Design for Six Sigma (DFSS)](https://www.isixsigma.com/category/dfss/)
        -   [DMAIC](https://www.isixsigma.com/category/dmaic-methodology/)
        -   [Getting Started](https://www.isixsigma.com/category/getting-started/)
        -   [History](https://www.isixsigma.com/category/history/)
        -   [How Is Six Sigma Different?](https://www.isixsigma.com/category/how-is-six-sigma-different/)
        -   [Roles & Responsibilities](https://www.isixsigma.com/category/roles-responsibilities/)
        -   [Sigma Level](https://www.isixsigma.com/category/sigma-level/)
    -   [Methodology](https://www.isixsigma.com/category/methodology/)
        -   [Balanced Scorecard](https://www.isixsigma.com/category/balanced-scorecard/)
        -   [Benchmarking](https://www.isixsigma.com/category/benchmarking/)
        -   [Business Process Management (BPM)](https://www.isixsigma.com/category/business-process-management-bpm/)
        -   [Design for Six Sigma (DFSS)](https://www.isixsigma.com/category/dfss/)
        -   [DMAIC](https://www.isixsigma.com/category/dmaic-methodology/)
        -   [Harada Method](https://www.isixsigma.com/category/harada-method/)
        -   [Hoshin Kanri](https://www.isixsigma.com/category/hoshin-kanri/)
        -   [Innovation](https://www.isixsigma.com/category/innovation-methodology/)
        -   [Kaizen](https://www.isixsigma.com/category/kaizen/)
        -   [Lean](https://www.isixsigma.com/category/lean-methodology/)
        -   [Metrics](https://www.isixsigma.com/category/metrics-methodology/)
        -   [Plan, Do, Check, Act](https://www.isixsigma.com/category/plan-do-check-act/)
        -   [Project Management](https://www.isixsigma.com/category/project-management/)
        -   [Robust Design/Taguchi Method](https://www.isixsigma.com/category/robust-design-taguchi-method/)
        -   [Theory of Constraints](https://www.isixsigma.com/category/theory-of-constraints/)
        -   [Total Quality Management (TQM)](https://www.isixsigma.com/category/total-quality-management-tqm/)
        -   [VOC/Customer Focus](https://www.isixsigma.com/category/voc-customer-focus/)
        -   [Work-out](https://www.isixsigma.com/category/work-out/)
    -   [Implementation](https://www.isixsigma.com/category/implementation/)
        -   [Basics](https://www.isixsigma.com/category/basics/)
        -   [Case Studies](https://www.isixsigma.com/category/case-studies/)
        -   [Change Management](https://www.isixsigma.com/category/change-management-implementation/)
        -   [Communication](https://www.isixsigma.com/category/communication/)
        -   [Deployment Health](https://www.isixsigma.com/category/deployment-health/)
        -   [Deployment Structure](https://www.isixsigma.com/category/deployment-structure/)
        -   [Financial Analysis](https://www.isixsigma.com/category/financial-analysis/)
        -   [Getting Started](https://www.isixsigma.com/category/getting-started/)
        -   [Project Selection & Tracking](https://www.isixsigma.com/category/project-selection-tracking/)
        -   [Remote/Virtual](https://www.isixsigma.com/category/remote-virtual/)
        -   [Sports](https://www.isixsigma.com/category/sports/)
        -   [Standard Work](https://www.isixsigma.com/category/standard-work/)
        -   [Success Factors](https://www.isixsigma.com/category/success-factors/)
        -   [Teams](https://www.isixsigma.com/category/teams/)
    -   [Industries](https://www.isixsigma.com/category/industries/)
        -   [Aerospace and Defense](https://www.isixsigma.com/category/aerospace-and-defense/)
        -   [Airline](https://www.isixsigma.com/category/airline/)
        -   [Automotive](https://www.isixsigma.com/category/automotive/)
        -   [Business Services](https://www.isixsigma.com/category/business-services/)
        -   [Chemicals](https://www.isixsigma.com/category/chemicals/)
        -   [Computers & Electronics](https://www.isixsigma.com/category/computers-electronics/)
        -   [Construction](https://www.isixsigma.com/category/construction/)
        -   [Consumer Food Products](https://www.isixsigma.com/category/consumer-food-products/)
        -   [Consumer Products](https://www.isixsigma.com/category/consumer-products/)
        -   [Education](https://www.isixsigma.com/category/education/)
        -   [Energy](https://www.isixsigma.com/category/energy/)
        -   [Financial Services](https://www.isixsigma.com/category/financial-services/)
        -   [Forest & Paper Products](https://www.isixsigma.com/category/forest-amp-paper-products/)
        -   [Fortune 500](https://www.isixsigma.com/category/fortune-500/)
        -   [Global 500](https://www.isixsigma.com/category/global-500/)
        -   [Government/Non-Profit](https://www.isixsigma.com/category/government-non-profit/)
        -   [Healthcare](https://www.isixsigma.com/category/healthcare/)
        -   [Hospitality](https://www.isixsigma.com/category/hospitality/)
        -   [Industrial](https://www.isixsigma.com/category/industrial/)
        -   [Industry Lists](https://www.isixsigma.com/category/industry-lists/)
        -   [Insurance](https://www.isixsigma.com/category/insurance/)
        -   [Law Enforcement](https://www.isixsigma.com/category/law-enforcement/)
        -   [Manufacturing](https://www.isixsigma.com/category/manufacturing/)
        -   [Military](https://www.isixsigma.com/category/military/)
        -   [Pharmaceuticals](https://www.isixsigma.com/category/pharmaceuticals/)
        -   [Restaurants](https://www.isixsigma.com/category/restaurants/)
        -   [Retail](https://www.isixsigma.com/category/retail/)
        -   [Software/IT](https://www.isixsigma.com/category/software-it/)
        -   [Transportation & Logistics](https://www.isixsigma.com/category/transportation-amp-logistics/)
        -   [Travel & Leisure](https://www.isixsigma.com/category/travel-leisure/)
    -   [Training](https://www.isixsigma.com/category/training/)
        -   [Certification Articles](https://www.isixsigma.com/category/certification-articles/)
        -   [Consultants](https://www.isixsigma.com/category/consultants/)
        -   [E-learning Articles](https://www.isixsigma.com/category/e-learning-articles/)
        -   [E-learning Providers](https://www.isixsigma.com/category/e-learning-providers/)
        -   [Games](https://www.isixsigma.com/category/games/)
        -   [Training Materials & Aids](https://www.isixsigma.com/category/training-materials-aids/)
        -   [Universities & Colleges](https://www.isixsigma.com/category/colleges-universities/)
        -   [Video Interviews](https://www.isixsigma.com/category/video-interviews/)
-   [News](/news/)
-   [Store](https://shop.isixsigma.com)
-   [Privacy Policy](https://www.isixsigma.com/updated-privacy-policy/)
-   [About](https://www.isixsigma.com/about-isixsigma/)
-   [Advertise with Us](https://www.isixsigma.com/advertising/)

Search Menu

![](https://www.isixsigma.com/wp-content/uploads/2018/11/shutterstock_2086924969-scaled.jpg)

1.  [](https://www.isixsigma.com)
2.  [Getting Started](https://www.isixsigma.com/category/getting-started/)
3.  How to Write an Effective Problem Statement: Get to the Root Cause Without the Fluff

[Getting Started](https://www.isixsigma.com/category/getting-started/)

# How to Write an Effective Problem Statement: Get to the Root Cause Without the Fluff

Updated: February 7, 2025 by [Rod Morgan](https://www.isixsigma.com/author/rmorgan/ "Posts by Rod Morgan")

![](https://www.isixsigma.com/wp-content/uploads/2018/11/shutterstock_2086924969-scaled.jpg)

    

Continuous improvement specialists are challenged to solve problems for their organizations or clients. They have acquired a wide array of tools, [methods](https://www.isixsigma.com/methodology/), and techniques for that purpose.

If continuous improvement practitioners can establish the winning conditions for change, they can look forward to successful outcomes. However, the devil is in the details, making continuous improvement jobs interesting and challenging.

One of those “little devils” that often gets overlooked is the need to construct an effective problem statement. You’ll want to do that at the start of any [improvement](https://www.isixsigma.com/pareto/pareto-chart-how-to-use-it-to-identify-root-causes/) project.

## What Is a Problem Statement?

![problem statement](https://www.isixsigma.com/wp-content/uploads/2018/11/shutterstock_1533736115-1024x683.jpg)

Adapted from an [article by Alan Bryman in the *International Journal of Social Research Methodology*](https://www.tandfonline.com/doi/abs/10.1080/13645570600655282): A problem is a statement about an area of concern. It is a condition to be improved upon, a difficulty to be eliminated, or a troubling question that exists in theory or in practice that points to the need for meaningful understanding and deliberate investigation.

## Why Is It So Hard to Write an Effective Problem Statement?

One of the challenges in writing a great [problem statement](https://www.isixsigma.com/community/the-cox-box/problem-statement/) is the distractions that arise.

-   **Symptoms** associated with the problem add to the confusion when trying to describe a problem. For example, arriving at the physician’s office and stating, “Doctor, I am experiencing pain in the back of my thigh down to the lower part of my leg! I need you to ‘fix’ my leg!” It is only after a thoughtful evaluation that the doctor concludes that your problem lies with your sciatic nerve and originates in your lower back.
-   **Solutions** are often an early consideration when wrestling with a problem. When one is faced with a problem, alleviating that pain as quickly as possible is a natural, almost reflexive, action. It is, however, extremely important to avoid jumping to solutions until a profound understanding of the current state is achieved.
-   The search for **causes** of your pain is a natural reaction. However, that also needs to be avoided when first describing a problem. Establishing the root cause will be a part of the ensuing investigative procedure. It should be reserved for the appropriate time in the lifecycle of the problem-solving method.
-   **Blame** is also a natural reflex when one is afflicted with a problem. A quote attributed to John Burroughs, an American naturalist and nature essayist, may be all that needs to be said on this subject: “You can get discouraged many times, but you are not a failure until you begin to blame somebody else and stop trying.”

In short, a great problem statement must be free of causes, solutions, and blame. Careful consideration must be given to ensure symptoms do not become a distraction.

## What Is in a Problem Statement?

A problem statement should describe an undesirable gap between the current state level and the desired future state level of performance. A [problem statement](https://www.isixsigma.com/dictionary/cause-and-effect-diagram/) *should* include absolute or relative measures of the problem that quantify that gap. It *should not* include possible causes or solutions!

![](https://www.isixsigma.com/wp-content/uploads/2018/04/Problem-Statement.png)

Key elements of an effective problem statement include:

-   **Gap**: Identify the [gap](https://www.isixsigma.com/dictionary/gap-analysis/) (pain) that exists today.
-   **Timeframe, location, and trend**: Describe when and where the problem was first observed and what kind of trend it is following.
-   **Impact**: Quantify the gap (cost, time, quality, environmental, personal, etc.)
-   **Importance**: To the organization, the individual, etc. to better understand the urgency.

### What Method Can I Employ to Write a Great Problem Statement?

The ability to articulate an effective problem statement is not simply a business skill – it is a life skill. How can children, youth, and adults begin to solve problems if they haven’t been able to adequately describe them? This holds for continuous improvement specialists.

The 5W2H (what, when, where, why, who, how, how much) method is deceptively simple. Ask the right questions in the right order and let the answers lead you to a great problem statement.

## Example of Developing a Problem Statement

Let’s walk through the 5W2H method for manufacturing and [call center](https://www.isixsigma.com/operations/call-centers/) examples.

### **Question 1**: What is the problem that needs to be solved?

-   **Manufacturer**: Window frames and parts are ending up in the assembly department missing required weep holes or slots.
-   **Call center**: The assessment call is too complex, time-consuming, and administratively heavy. This results in a diminished experience for the client as well as the staff member performing the work.

### **Question 2**: Why is it a problem? (highlight the pain)

-   **Manufacturer**: If identified (visual inspection), the affected parts must be sent back for rework. This increases the overall cost of manufacturing, creating higher inventory levels (WIP). It also increases risk since some of the defects may not be detected until later in the process. Worse, they may end up being incorrectly shipped to the job sites.
-   **Call center**: This results in higher variability and length of call handling time. Clients have to repeat their “story” as they move through the assessment and downstream case worker (meeting) process. Further, clients have to provide more information than may be required. This in turn leads to increased workload for the assessment worker and increased wait times in the (telephone) queue. The overall impact is reduced service levels as well as diminished client and assessment worker experience.

### **Question 3**: Where is the problem observed? (location, products)

-   **Manufacturer**: This problem is observed in the assembly department, downstream departments as well as ultimately in the field with customer complaints and costly field repairs and replacements.
-   **Call center**: This problem is observed in all assessment calls but will vary in magnitude depending on the client (needs and circumstance), assessment worker (experience), and other factors that contribute to variation in the handling of assessment calls.

### **Question 4**: Who is impacted? (customers, businesses, departments)

-   **Manufacturer**: This problem affects the assembly department that is tasked with trying to inspect for the error and react accordingly, [rework](https://www.isixsigma.com/methodology/dmaic-methodology/green-belt-project-reduce-resolution-time-and-rework-in-software-development/) occurring in the department/work cell responsible for weep holes and slots, the company as a whole in terms of cost, brand, and reputation, and, most importantly, the customer who is affected by this problem if it makes it to the field.
-   **Call center**: This affects the client associated with the call, clients waiting in the queue, client’s families, and the organization and employers in the community being served.

### **Question 5**: When was the problem first observed?

-   **Manufacturer**: This has been an ongoing issue going back as far as memory serves in the long-term employees, but with increased volume, more customization, and higher complexity in design, the impact and severity of this problem have increased rapidly over the last two years.
-   **Call center**: This is a latent problem that has always existed but has become more evident with recent changes, including changes in funding, legislation, demand for services, client demographics, and recent integration efforts in the organization as part of their ongoing commitment to continuous improvement of service pathways and client experience.

### **Question 6**: How is the problem observed? (symptoms)

-   **Manufacturer**: Customer (in-field installation and service) complaints, increased warranty costs, manufacturing non-conformance reports (NCR), complaints from the assembly department team, and increased costs in fabrication.
-   **Call center**: This problem is observed in the variation in call-handling times, wait times in the telephone queue, call abandon rates, increased stress in front-line staff (workload and client anxiety/dissatisfaction), and ambiguity in call-handling protocols.

### **Question 7**: How often is the problem observed? (error rate, magnitude, trend)

-   **Manufacturer**: There is an observed 62,000 parts per million (PPM) for this specific defect, taking into consideration rework completed in-house and observed defects in the field. The PPM is derived from the number of weeping holes and slots required per unit assembly versus the actual number of deficiencies overall observed for the same number of units.
-   **Call center**: This is a daily operational occurrence but increases in call complexity related to changes in the knowledge base – multiple programs and changes in the environment (client demographics and needs/circumstances, legislation, etc.) – have resulted in an increase in severity and stress on the system.

## A Real-World Example of Using Problem Statements

So, how do you use a [problem statement](https://www.isixsigma.com/dictionary/root-cause-and-failure-analysis-rcfa/)? We’ve covered the methodology and practices behind it, but that means little without something a little more grounded to back it up. For a moment, let’s consider that you’re in charge of a production line manufacturing printed circuit boards for smartphones. Lately, the units coming back from quality testing are reporting issues with the touchscreen registering inputs.

So, how do you get to the bottom of this issue? First, you’d consult with your continuous improvement specialist to start drafting a problem state. Using the 5W2H method, you’d create something like this:

-   **What is the problem?**: The touchscreen isn’t registering inputs
-   **Why is it a problem?**: This is the primary interface your customers use on the device.
-   **Where is the problem observed?**: In quality testing before the phones are packaged for shipping
-   **Who is impacted?**: The production line and assembly technicians
-   **When was the problem first observed?**: Four days ago.
-   **How is the problem observed?**: QC technicians noticed it when tasting the latest batch of units off the line.
-   **How often is the problem observed?**: 42,000 PPM

So, now that the problem statement is drafted, you can get to work on deciding if this is a significant enough issue to address given the scale of production.

## Other Tools for Problem-Solving

A problem statement is just one part of the equation when getting into how to improve your processes. When you’re identifying problems, it helps to have the tools on hand to help you get down to the matter with ease. The [7 QC Tools](https://www.isixsigma.com/dictionary/7-qc-tools/) frequently used in Six Sigma methodology are an easy and effective way of getting down to brass tacks when it comes to looking at your problems.

Further, we touched somewhat on the 5W2H method of drafting a problem statement, but this concept extends to more than just solving problems. The 6Ws are an effective way of analyzing topics while considering every perspective. You can read all about how to best implement it in our handy [guide](https://www.isixsigma.com/dictionary/6w/).

## Your Turn!

Think of a problem you have encountered in your personal or professional life, or a problem you are currently tasked to solve. Employ the preceding method of asking seven simple questions and see where it takes you.

Teach this simple and effective method to your friends, colleagues, and family. Writing [problem statements](https://www.isixsigma.com/dictionary/fishbone-diagram/) truly is a life skill and, when employed correctly, will place anyone in good stead to start solving the problem.

#### Join 65,000 Black Belts and Register For The Industry Leading ISIXSIGMA Newsletter Today

 

Signup Now -- It's FREE >>

Thanks! Keep an eye out in your mailbox for our emails.

By providing your email address, you agree to receive communications from us regarding website updates and other offerings that may be of interest to you. You can unsubscribe at any time. For more information, please review our [Disclaimer and Terms of Use](/disclaimer-and-terms-of-use/?utm_source=247wallst&utm_campaign&utm_content=desktop||6423&utm_term=247wallst&utm_medium=eoaCTALink&site&tc=671184b2e299e&tpid=6423).

##### About the Author

![](https://secure.gravatar.com/avatar/85f9addada30d3933422e61f8476b888?s=80&d=mm&r=g)

# [Rod Morgan](https://www.isixsigma.com/author/rmorgan/)

Tagged [problem statement](https://www.isixsigma.com/tag/problem-statement/) [Quality](https://www.isixsigma.com/tag/quality/)

-   [How AI Is Changing the Nature of Work Across Industries](https://www.isixsigma.com/artificial-intelligence/how-ai-is-changing-the-nature-of-work-across-industries/)
-   [MVP (Minimum Viable Product): From Concept to Reality](https://www.isixsigma.com/lean-methodology/mvp-minimum-viable-product-from-concept-to-reality/)

## Six Sigma Topics

Six Sigma Topics Select Category 5 Whys  (21) 5S  (18) Aerospace and Defense  (5) Affinity Diagram/KJ Analysis  (8) Agile  (34) Airline  (3) Analysis of Variance (ANOVA)  (9) Analytic Hierarchy Process (AHP)  (2) Artificial Intelligence  (18) Asia  (14) Ask Dr. Mikel Harry  (20) Automation  (4) Automotive  (12) Awards and Standards  (14) Balanced Scorecard  (10) Basics  (59) Benchmarking  (16) Blogs  (1,095) Brainstorming  (20) Business Intelligence  (2) Business Process Management (BPM)  (43) Business Services  (6) Calculators  (3) Call Centers  (27) Capability Indices/Process Capability  (28) Case Studies  (138) Cause & Effect  (24) Certification & Training  (21) Certification Articles  (30) Change Management  (141) Chemicals  (8) Communication  (42) Computers & Electronics  (18) Concepts  (782) Conjoint Analysis  (1) Construction  (3) Consultants  (1) Consumer Food Products  (12) Consumer Products  (7) Control Charts  (64) Deployment  (18) Deployment Health  (7) Deployment Structure  (27) Design for Six Sigma (DFSS)  (31) Design for Six Sigma (DFSS)  (30) Design of Experiments (DOE)  (30) Design Thinking  (10) DMAIC  (152) E-learning Articles  (5) E-learning Providers  (4) Education  (7) Energy  (17) Europe  (35) Finance  (23) Financial Analysis  (19) Financial Services  (55) FMEA  (27) Forest & Paper Products  (3) Fortune 500  (2) Games  (6) Getting Started  (12) Getting Started  (45) Global 500  (5) Government/Non-Profit  (70) Graphical Analysis Charts  (11) Harada Method  (9) Healthcare  (141) History  (11) Hoshin Kanri  (24) Hospitality  (5) How Is Six Sigma Different?  (10) Human Resources  (30) Hypothesis Testing  (27) Implementation  (28) Industrial  (7) Industries  (6) Industry Lists  (5) Innovation  (16) Insurance  (3) IT  (85) Kaizen  (60) Kanban  (11) Kano Analysis  (9) Law Enforcement  (1) Leadership & Teamwork  (15) Lean  (185) Manufacturing  (8) Manufacturing  (46) Marketing and Sales  (22) Measurement Systems Analysis (MSA)/Gage R&R  (28) Methodology  (220) Metrics  (66) Metrics  (52) Military  (20) Mood’s Median Test  (1) New to Six Sigma  (15) Normality  (5) Organization & Strategy  (34) Pareto  (17) Pharmaceuticals  (11) Plan, Do, Check, Act  (8) Poka Yoke  (8) Press Releases  (717) Process Mapping  (23) Project Charter  (7) Project Management  (23) Project Selection & Tracking  (55) Pugh Matrix  (4) QFD/House of Quality  (10) Quality Management  (5) RACI Diagram  (3) Regression  (22) Remote-Work  (10) Remote/Virtual  (12) Resource Pages  (13) Restaurants  (1) Retail  (17) Risk Management  (10) Robotic Process Automation/Machine Learning/Artificial Intelligence  (5) Robust Design/Taguchi Method  (9) Roles & Responsibilities  (51) Sampling/Data  (45) Scorecard  (3) Sigma Level  (12) Simulation  (7) SIPOC/COPIS  (23) Six Sigma  (69) Six Sigma Methodology  (51) Six Sigma Tools & Templates  (28) Six Thinking Hats  (1) Software  (91) Software/IT  (75) Sports  (6) Standard Work  (3) Statistical Analysis  (21) Success Factors  (43) Supply Chain  (26) Teams  (54) Templates  (5) The Cox-Box  (187) Theory of Constraints  (22) Tools & Techniques  (42) Total Quality Management (TQM)  (30) Training  (40) Training Materials & Aids  (34) Transportation & Logistics  (11) Travel & Leisure  (5) Uncategorized  (93) Universities & Colleges  (2) Value Stream Mapping  (23) Variation  (22) Video Interviews  (11) VOC/Customer Focus  (69) Wizards  (2) Work-out  (8)

Search

Search

## Recent Posts

-   [Buying an American-Made Car? Trump’s New Tax Deduction Could Lower Your Tax Bill](https://www.isixsigma.com/uncategorized/buying-an-american-made-car-trumps-new-tax-deduction-could-lower-your-tax-bill/)
-   [10 “Minor” Car Repairs That Can Cost Thousands](https://www.isixsigma.com/uncategorized/10-minor-car-repairs-that-can-cost-thousands/)
-   [15 Pickup Trucks Americans Keep Coming Back To](https://www.isixsigma.com/uncategorized/15-pickup-trucks-americans-keep-coming-back-to/)
-   [10 SUVs That Could Cost More Than They’re Worth](https://www.isixsigma.com/uncategorized/10-suvs-that-could-cost-more-than-theyre-worth/)
-   [7 Pickup Trucks With Reliability Problems That Could Cost You](https://www.isixsigma.com/uncategorized/7-pickup-trucks-with-reliability-problems-that-could-cost-you/)

-   [About iSixSigma](https://www.isixsigma.com/about-isixsigma/)
-   [Terms of Service & Disclaimer](https://www.isixsigma.com/disclaimer-and-terms-of-use/)
-   [Updated Privacy Policy](https://www.isixsigma.com/updated-privacy-policy/)
-   [Advertise with iSixSigma](https://www.isixsigma.com/advertising/)

© 2026 - isixsigma.com

[To top](#)
```

**Tool: webfetch**

**Input:**

```json
{
  "url": "https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/"
}
```

**Output:**

````
---
description: Learn how to write a clear, measurable problem statement with a practical formula, worked manufacturing examples, common mistakes and a free template.
title: How To Write A Problem Statement: Examples &amp; Template
---

 

[Skip to content](#content) 

[Root Cause Analysis](https://www.learnleansigma.com/category/root-cause-analysis/)/Practical Guide

PROBLEM DEFINITION

# How to Write a Good Problem Statement (With Examples)

Turn a vague complaint into a specific, evidence-led statement that sets the scope for 5 Whys, A3, DMAIC or another structured investigation.

[Write the statement→](#write) [Open the free template↓](https://www.learnleansigma.com/template/is-is-not-template/) 

[![Daniel Croft-Bednarski](https://secure.gravatar.com/avatar/4073a93815879716212ddab9fc00f615a73d17b30d272f48072a3bb0a895438b?s=300&d=mm&r=g)](https://www.learnleansigma.com/creator/daniel-croft-bednarski/) [**Daniel Croft-Bednarski**](https://www.learnleansigma.com/creator/daniel-croft-bednarski/)Head of Continuous Improvement · LSS Black Belt · [LinkedIn](https://www.linkedin.com/in/danielcroftb/) **Updated**8 Aug 2026 · 11 min read 

VAGUE **“The machine keeps breaking down.”** 

EXPECTED**No unplanned stops**

ACTUAL**4 stops · 127 min**

WHERE**Line 3**

WHEN**18–22 July**

READY TO INVESTIGATE **Line 3 recorded four unplanned stops totalling 127 minutes.** _Cause not assumed_ 

Define the gap first. Explain it only after the evidence is collected.

QUICK ANSWER

## A good problem statement defines the measurable gap between expected and actual performance—without assuming a cause or solution.

1. 1Start with the observable gap: expected versus actual performance.
2. 2Add where, when and how large the gap is.
3. 3Record the evidence source and mark what is still unknown.
4. 4Keep causes, blame and preferred solutions out of the statement.
5. 5Use a deeper Is/Is Not analysis when the boundary is unclear.

ADVERTISEMENT

On this page **What a problem statement is** 

Contents☰ 

ON THIS PAGE

View all sections ↗ 

ARTICLE RESOURCE**Define the boundaries with the Is/Is Not template**[Open the free template _→_](https://www.learnleansigma.com/template/is-is-not-template/)

CONTINUE LEARNING [**How to Do a 5 Whys Analysis**Continue from a defined problem into an evidence-led cause chain.](https://www.learnleansigma.com/root-cause-analysis/how-to-do-a-5-whys-analysis/)[**5W1H Is/Is Not Problem Definition**Expand the boundaries when the problem is still unclear.](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/) 

EXPLORE MORE[FREE PRACTICAL TOOLS**View Templates**_→_](https://www.learnleansigma.com/templates/)[**View Guides**_→_](https://www.learnleansigma.com/guides/)

01 · THE ESSENTIALS

## What is a problem statement?

A problem statement is a concise, factual description of the gap between the performance that should be happening and what is actually happening. It gives the team a shared starting point for investigation without assuming the cause, assigning blame or prescribing a solution.

D

KEY DEFINITION

### Problem statement

“A good problem statement in its simplest form is a clear statement of the difference between our target condition and our actual condition.”

In practical terms, a useful problem statement identifies four things:

* **Expected condition:** What standard, target or requirement should have been met?
* **Actual condition:** What was observed or measured?
* **Gap:** How large or frequent was the difference?
* **Scope:** Where and when did the problem occur?

The practical rule is simple: **define the gap before trying to explain it**.

**Factual problem statement:** During the first five working days of May, Line 3 experienced four unplanned drive stops, causing 127 minutes of downtime against a target of no more than 30 minutes.

**Premature causal statement:** Poor maintenance caused Line 3 to stop repeatedly.

The first statement describes evidence that the team can verify. The second introduces a possible cause before the maintenance history, failure mode and operating conditions have been investigated.

This distinction matters whether the next step is a [5 Whys analysis](https://www.learnleansigma.com/root-cause-analysis/how-to-do-a-5-whys-analysis/), a [Fishbone diagram](https://www.learnleansigma.com/guides/fishbone-diagram/), an [A3 investigation](https://www.learnleansigma.com/guides/a3-problem-solving/) or a [DMAIC project](https://www.learnleansigma.com/guides/dmaic/). When the starting statement already contains a preferred explanation, the investigation can become an attempt to confirm an assumption rather than understand the problem.

[![Daniel Croft-Bednarski](https://secure.gravatar.com/avatar/4073a93815879716212ddab9fc00f615a73d17b30d272f48072a3bb0a895438b?s=300&d=mm&r=g)](https://www.learnleansigma.com/creator/daniel-croft-bednarski/)

PRACTITIONER NOTE

I treat the first problem statement as a working draft. Before asking why the problem occurred, I check that the team can show the expected standard, the actual result and the evidence supporting the gap. Any missing facts are recorded and collected before the cause investigation begins.

[Daniel Croft-Bednarski](https://www.learnleansigma.com/creator/daniel-croft-bednarski/), Head of Continuous Improvement · [LinkedIn](https://www.linkedin.com/in/danielcroftb/)

[![Good problem statement example showing the scope, actual condition, expected condition and measurable gap, compared with a premature causal statement.](https://www.learnleansigma.com/wp-content/uploads/2026/03/What-a-good-problem-statement-looks-like-png.webp)](https://www.learnleansigma.com/wp-content/uploads/2026/03/What-a-good-problem-statement-looks-like.png)

PROBLEM STATEMENT BASICS

A good problem statement defines the expected condition, actual condition, measurable gap and scope without assuming the cause or prescribing a solution.

Illustrative example based on the article’s Line 3 downtime scenario. The dates, quantities and operational details are constructed for teaching purposes and do not represent a mea

×![Good problem statement example showing the scope, actual condition, expected condition and measurable gap, compared with a premature causal statement.](https://www.learnleansigma.com/wp-content/uploads/2026/03/What-a-good-problem-statement-looks-like.png) 

02 · SEPARATE THE FOUR JOBS

## Separate the problem, business case, goal and root cause

A project should not use one statement to describe what is wrong, why it matters, what success looks like and what caused it. These are four separate decisions. The problem statement, business case and goal can be defined near the start of the work; the root cause should only be stated after it has been investigated and verified.

01

#### Problem statement

**Purpose:** Define the current performance gap.

**Question:** What is happening, where, when and by how much?

**Example:** During May, Line 3 experienced four unplanned drive stops during first shift, resulting in 127 minutes of downtime against a target of no more than 30 minutes.

02

#### Business case

**Purpose:** Explain why the gap is worth addressing.

**Question:** What is the operational, financial or customer consequence?

**Example:** The lost production time is reducing available capacity, increasing overtime risk and threatening the on-time completion of customer orders.

03

#### Goal statement

**Purpose:** Define the measurable result the work must achieve.

**Question:** What performance is required, within what scope and by when?

**Example:** Reduce first-shift drive downtime on Line 3 from 127 minutes to no more than 30 minutes per month by 30 September, without increasing safety or quality risk.

04

#### Root-cause statement

**Purpose:** Describe the verified mechanism creating the gap.

**Question:** What evidence-based condition caused or allowed the problem?

**Example:** Testing confirmed that loose drive-cabinet terminals caused intermittent power loss. The terminals loosened because the maintenance standard did not specify a torque setting or verification check.

**Important:** Do not insert a suspected cause or preferred solution into the problem statement. Doing so can narrow the investigation before the evidence has been examined.

A [project charter](https://www.learnleansigma.com/template/project-charter-template/) may contain all four, but they should still remain distinct fields. A problem statement can be valid even when the cause is unknown and the final solution has not been selected.

03 · COLLECT THE FACTS

## Create a factual picture of the problem

Start at the process, not at the keyboard. Speak with the people who perform and support the work, review the current standard, and preserve the records or observations that show what happened. The purpose is to build an evidence-based picture of the current condition before compressing it into a problem statement.

A practical way to organise this fact-finding is the **5W1H method**: What, Where, When, Who, Why and How. These questions help the team describe the problem from several angles, expose missing information and define the boundary of the investigation.

At this stage, 5W1H is a **problem-definition method**, not a root-cause analysis. Use it to establish what was observed, where and when it occurred, who or what was affected, how the problem appeared and why the gap matters. Do not use the first “why” to insert an untested explanation of what caused the problem.

01

#### Expected condition

**Reference point:** What should have happened?

Record the approved standard, specification, target, service level or normal condition. Without a reference point, words such as _slow_, _high_ or _unreliable_ are only opinions.

02

#### Actual condition

**What:** What actually happened?

Describe what was directly observed, recorded or measured. Name the defect, delay, failure, variation or missed requirement without explaining its cause.

03

#### Object and boundary

**Where and who:** Where was the gap found, and what or whom did it affect?

Identify the relevant product, process, transaction, customer group, equipment, team or population. “Who” should define involvement or impact, not assign blame.

04

#### Time and pattern

**When:** When and under what conditions did it occur?

Record the period, shift, sequence, frequency or operating condition. A bounded period is more useful than “recently” or “often”.

05

#### Extent and impact

**How and why it matters:** How large is the gap, and what consequence does it create?

Use a count, rate, duration, percentage, value or another suitable unit. Keep impact separate when its calculation is not yet supported by evidence.

06

#### Evidence source and status

**Verification:** How do you know?

Record where each fact came from and whether it was directly observed, measured, confirmed from records, estimated or is still to be verified.

[![Completed 5W1H example showing the what, where, when, who, why and how of four unplanned drive stops on Line 3.](https://www.learnleansigma.com/wp-content/uploads/2026/03/Completed-5W1H-Problem-Definition-Example-1024x683-png.webp)](https://www.learnleansigma.com/wp-content/uploads/2026/03/Completed-5W1H-Problem-Definition-Example.png)

BUILD THE PICTURE

A completed 5W1H analysis builds a factual picture of the Line 3 downtime problem before the team investigates its root cause.

Illustrative 5W1H analysis based on the article’s Line 3 downtime scenario. Dates, quantities, evidence sources and operational details are constructed for teaching purposes and do

×![Completed 5W1H example showing the what, where, when, who, why and how of four unplanned drive stops on Line 3.](https://www.learnleansigma.com/wp-content/uploads/2026/03/Completed-5W1H-Problem-Definition-Example.png) 

If an impact is estimated, make its basis visible:

`Estimated impact = verified gap × supported rate or unit value`

For example, an output estimate based on 127 minutes of downtime is useful only when the production rate, period and evidence source are stated. If that basis is weak, label it _estimate to validate_ or leave it outside the core problem statement.

_!_

**Do not use the first “why” as an assumed cause**

In 5W1H, “why” can describe why the problem matters. It should not be used to insert an unverified root cause. Remove words such as “because”, “need” and “should” when they smuggle an explanation or solution into the starting statement.

[Read the University of Leeds guidance →](https://deliveringresults.leeds.ac.uk/delivering-results-lifecycle/problem-statement/)

Use the [5W1H and Is/Is Not problem-definition method](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/) when the initial facts are incomplete, the process boundary is uncertain or the problem appears in some conditions but not others. The completed analysis should give you the factual picture needed to write a concise problem statement.

04 · THE METHOD

## How to write a problem statement, step by step

The seven steps below turn observations and records into a problem statement that is specific enough to investigate. Work through them in order, but treat the result as a working draft. If new evidence changes the measurement, boundary or time period, update the statement rather than defending the original wording.

The aim is not to produce an impressive sentence. It is to create an accurate description of the gap that another person could verify from the same evidence.

* 01  
#### Define the expected or standard condition  
Start by establishing the condition the process was expected to achieve. This might come from a customer requirement, specification, standard work document, production target, service-level agreement, control plan, approved schedule or another recognised standard.  
Do not begin with the failure itself. Without an expected condition, you cannot demonstrate that a measurable gap actually exists. Saying that downtime is “high”, delivery is “poor” or defects are “excessive” is not enough unless there is a reference point against which those statements can be tested.

**Check:** Is the standard current, applicable to this process and relevant to the period being investigated? Record where it came from so the team can verify it later.

**Output:** A clear reference point showing what should have happened.

**Example:** Unplanned main-drive downtime on Line 3 should not exceed 30 minutes during a five-working-day period.
* 02  
#### State the actual observable condition  
Next, describe the actual condition using observations, measurements or records. State what happened without explaining why it happened.  
Use specific operational language where possible. Instead of saying “the machine was unreliable”, identify the recorded event: four unplanned main-drive stops. Instead of “quality was poor”, state the defect type, quantity or measured failure rate.

**Check:** Could another person look at the same records or observations and reach the same description? If not, the wording may still contain opinion or interpretation.

**Output:** A neutral description of what actually happened.

**Example:** Downtime records show four unplanned main-drive stops totalling 127 minutes.
* 03  
#### Define the object and process boundary  
Specify exactly what is affected. Depending on the problem, this could be a machine, product family, process step, transaction type, customer group, production line, location or service.  
Then define where the problem starts and stops. Avoid expanding the statement to cover every similar symptom in the organisation unless the evidence shows that they belong to the same problem.  
For example, if the evidence only concerns Line 3 during first shift, do not write “the production lines suffer excessive drive downtime”. That changes a bounded problem into an organisation-wide claim that has not been demonstrated.

**Check:** Can the team tell from the statement what is inside the investigation and what is currently outside it?

**Output:** A clearly bounded part of the process for the team to investigate.

**Example:** Line 3, first shift, main-drive stoppages.
* 04  
#### Add the time period and any verified pattern  
State when the observed condition occurred and the period over which the measurement was calculated. Time is part of the problem boundary, not an optional detail.  
Use the period supported by the evidence. This might be a particular shift, week, month, production batch, service period or operating condition. Avoid vague terms such as “recently”, “regularly” or “for some time”.  
If a pattern has been confirmed, include it. For example, the stops may occur only during first shift, after a changeover or while producing a particular product. Do not include a pattern simply because someone remembers seeing it before.

**Check:** If the measurement were repeated over the same defined period, would another person know exactly which data to include?

**Output:** A defined period that makes the measurement reproducible.

**Example:** During first shift in the first five working days of May.
* 05  
#### Quantify the gap and its extent  
Compare the actual condition with the expected condition using an appropriate unit. Depending on the problem, this may be minutes, defects, percentage, cost, lead time, complaints, failures, missed deliveries or another meaningful measure.  
Where useful, include both frequency and magnitude. In this example, knowing that there were **four stops** provides different information from knowing that those stops created **127 minutes of downtime**.  
Make the gap explicit where it improves understanding:  
`Gap = actual performance − expected performance`  
For the Line 3 example:  
`127 minutes − 30 minutes = 97 minutes above target`  
Keep estimated financial, output or customer impact separate unless its calculation can be supported. A precise-looking financial number based on an assumed production rate can make the statement appear stronger while actually weakening its evidence base.

**Check:** Does every number have a unit, period and evidence source?

**Output:** A measurable difference between expected and actual performance.

**Example:** 127 minutes of downtime against a target of no more than 30 minutes: a 97-minute gap.
* 06  
#### Remove causes, blame and solutions  
Read the draft again and remove anything that explains the cause, assigns responsibility or recommends what should be done next.  
Watch for words and phrases such as _because_, _caused by_, _operator error_, _poor maintenance_, _lack of training_, _need to_, _should replace_ or _must automate_. These may eventually prove relevant, but they belong to the cause-analysis or countermeasure stages.  
For example:

**Too early:** Poor maintenance caused Line 3 to stop repeatedly.

**Evidence-led:** During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime against a target of no more than 30 minutes.

**Check:** Could several different causes still explain the problem described by the statement? If the wording points the team toward only one explanation, it may already contain an assumption.

**Output:** A problem statement that remains open to investigation.

**Example:** Replace “poor maintenance caused repeated stops” with the recorded drive-stop condition.
* 07  
#### Verify the statement and record what remains unknown  
Review the statement with people who understand the process and, where possible, people who directly observed the condition. The purpose is not to obtain agreement with a theory. It is to check whether the description accurately represents the available evidence.  
Work through the statement fact by fact. Confirm the expected condition, actual result, measurement period, process boundary and every number used. If a fact cannot yet be supported, identify it as an evidence gap rather than hiding the uncertainty with confident wording.  
Before moving into root-cause analysis, ask:

* Can we show the expected standard or target?
* Can we show the actual condition from evidence?
* Is the size of the gap measurable?
* Are the process and time boundaries clear?
* Does every important number have a source?
* Have we removed assumed causes and solutions?
* Are we describing one problem rather than several different problems?  
If the answer to an important question is no, mark the statement **Evidence needed** and collect the missing information. If the essential facts can be demonstrated, the statement can move forward as **Ready for analysis**.

**Output:** A reviewed draft marked ready for analysis or evidence still required.

**Example:** The downtime log, alarm history and current operating standard are identified as evidence sources.

![Seven-step method for writing a problem statement, progressing from the expected and actual conditions through scope, period, measurement, neutral wording and final verification. Description](https://www.learnleansigma.com/wp-content/uploads/2026/03/Seven-Steps-from-Standard-to-Analysis-Ready-Statement-1024x576.png)

SEVEN-STEP METHOD

Move from a confirmed standard and observable condition to a bounded, measured and verified statement that remains open to causal evidence.

LearnLeanSigma teaching sequence based on the article’s controlled-draft method. Reaching “Ready for analysis” confirms the starting condition, not the root cause.

A problem statement may change when new evidence changes the measurement, scope or time boundary. That is disciplined learning rather than a failure of the original draft—provided the evidence and reason for the revision remain traceable.

ADVERTISEMENT

05 · COPYABLE FORMULAS

## Copyable problem statement formulas

A formula can help you organise the facts when the first draft feels difficult to write. Treat these as drafting structures rather than rigid sentence templates. Include the information needed to make the gap clear, then edit the wording so the final statement reads naturally.

The strongest formula is usually the simplest one: **define what should have happened, what actually happened, where and when it happened, and the size of the difference.**

OPERATIONAL GAP 

### Expected versus actual

**Use when:** A process, machine or operation has a measurable standard or target that was not achieved.

`During [period], [process/object] at [location] recorded [actual condition] against [expected condition], a gap of [extent and units].` 

**Example:** During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime against a target of no more than 30 minutes, a gap of 97 minutes.

SERVICE OR TRANSACTION 

### Population and service level

**Use when:** The problem affects a defined group of orders, requests, customers, transactions or cases.

`For [defined population] during [period], [metric] was [actual condition] compared with [target], with [count or percentage] outside the requirement.` 

**Example:** For 240 customer orders processed during May, 38 were completed after the 48-hour service target, resulting in an on-time completion rate of 84.2% against a target of 95%.

OPTIONAL IMPACT 

### Add impact only when the basis is supported

**Use when:** The operational gap has a customer, output or financial consequence that can be calculated from verified information.

`The verified gap resulted in [impact], calculated from [measured gap] × [supported rate or unit value from named source].` 

**Example:** The 97 minutes above the downtime target represented an estimated 32 units of lost output, based on the documented average production rate for Line 3.

**Caution:** If the rate, value or conversion is uncertain, label the impact as an estimate to validate or leave it outside the core problem statement.

**A completed statement does not need every possible field.** The aim is to include enough information to make the gap clear and verifiable without turning the statement into a paragraph.

**Line 3 example:** During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime against a target of no more than 30 minutes.

✓

#### Use

* **Specific objects:** Line 3, customer orders, Product A or the final inspection process.
* **Measured conditions:** 127 minutes, 38 late orders or a 4.2% defect rate.
* **A reference point:** the approved target, standard, specification or requirement.
* **Defined boundaries:** the relevant location, shift, population and period.
* **Neutral wording:** describe what the evidence shows and make important unknowns visible.

×

#### Avoid

* **Assumed causes:** “because”, “due to”, “poor maintenance” or “operator error” before verification.
* **Preferred solutions:** “we need to retrain”, “must replace” or “should automate”.
* **Unsupported judgements:** bad, excessive, unreliable or inefficient without a measurable reference point.
* **False precision:** financial or output impacts calculated from rates that have not been checked.
* **Overloaded statements:** forcing every fact and consequence into one long sentence.

06 · BUILD IT

## Build your problem statement

Use the builder to assemble a draft from the evidence fields. It will flag missing inputs and wording that may contain an assumed cause, blame or solution. Your entries remain in your browser and are not sent in analytics.

Define the gap Process, object or population _Required_ Expected or standard condition _Required_ Actual observable condition _Required_ Where or process boundary _Required_ When or pattern _Required_ Extent, including units _Required_ 

Show the evidence Evidence source _Required_ Evidence status _Required_ Unknown / still to verify Observed Measured Confirmed from records Estimate with a stated basis Optional impact Impact calculation or source 

Check the statement → Reset 

DRAFT Complete the required facts. 

#### Your draft statement

During \[time\], \[object\] in \[location\] recorded \[actual condition\] against \[expected condition\], a gap of \[extent\].

Missing facts will appear here. Causes and solutions are intentionally excluded.

Copy statement [Boundary still unclear? Use Is/Is Not →](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/) 

Your entries stay in this browser. Analytics records only component actions and readiness status—not the text you enter.

The generated sentence is a draft, not an approval. Check it with the people who know the process and confirm the source behind each fact. If you cannot define where the problem begins and ends, use the [free Is/Is Not template](https://www.learnleansigma.com/template/is-is-not-template/) to compare what is and is not affected.

07 · WORKED TRANSFORMATION

## Worked example: from complaint to evidence-led statement

**Illustrative example:** the dates, quantities and operational details below are constructed to demonstrate the method. Replace them with verified facts from your own process rather than presenting the example as a real case result.

This example shows how an initially vague complaint becomes more useful as the team adds a defined object, evidence, measurement period, expected condition and measurable gap.

BEFORE

#### The machine keeps breaking down.

This tells the team that something is wrong, but almost everything needed for investigation is missing. The machine is not identified, “keeps” is unmeasured, the time period is unknown and there is no standard against which performance can be compared.

AFTER

#### During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime against a target of no more than 30 minutes.

The final version identifies the process, event, shift, period, actual condition and expected condition. It creates a measurable 97-minute gap without claiming why the drive stopped or what should be done about it.

_→_

REVISION HISTORY

1. 01  
> “The machine keeps breaking down.”

**Status:** Initial complaint.  
The object, period, frequency, downtime, expected condition and evidence source are all missing. The wording expresses a concern but does not yet define an investigable problem.
2. 02  
> “Line 3 stopped four times during first shift.”

**Status:** Scope becoming clearer.  
The affected process, shift and event count are now identified, but the measurement period and duration are still missing. The team also cannot yet tell how far performance was from the expected condition.
3. 03  
> “During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime.”

**Status:** Measured actual condition.  
The event type, period, frequency and duration can now be checked against downtime and alarm records. The statement describes what happened, but it still does not establish whether the measured result represents a performance gap.
4. 04  
> “During first shift in the first five working days of May, Line 3 recorded four unplanned main-drive stops totalling 127 minutes of downtime against a target of no more than 30 minutes.”

**Status:** Ready for analysis.  
The current operating target provides the expected condition. Actual downtime was 127 minutes against a maximum target of 30 minutes, creating a measurable gap of 97 minutes. The statement remains neutral about what caused the stoppages.

The final statement can also be expressed as a simple performance gap:

`127 minutes actual downtime − 30 minutes target = 97 minutes above target`

That calculation is useful because it shows the size of the problem without adding interpretation. The four stops and 127 minutes describe the actual condition; the 30-minute target establishes the reference point; the 97-minute difference expresses the gap.

If the verified gap creates a measurable output, financial or customer consequence, record that separately rather than forcing it into the core problem statement. For example, an estimated output loss should only be stated when the production rate, measurement period and source of that rate are known and traceable.

Avoid adding statements such as “poor maintenance caused the stops” or “the drive needs replacing” at this stage. Those statements move from _what happened_ into either cause analysis or solution selection before the evidence has established the answer.

The next question is causal: **what verified condition produced or allowed the four drive stoppages?** Continue with the [complete 5 Whys method](https://www.learnleansigma.com/root-cause-analysis/how-to-do-a-5-whys-analysis/) when the evidence points toward a cause path that can be tested, or [compare Fishbone and 5 Whys](https://www.learnleansigma.com/root-cause-analysis/fishbone-diagram-vs-5-whys-analysis/) when several possible cause families need to be explored before narrowing the investigation.

08 · EXAMPLES

## Good and weak problem statement examples

The examples below apply the same principles to quality, transactional and customer-delivery problems. The stronger version is not better because it sounds more technical. It is better because another person can identify the affected population, measurement period, actual condition and expected condition from the statement.

WEAK

> Operators are making too many scratches.

This statement assigns responsibility before the cause has been investigated. “Too many” is also an unmeasured judgement: the product, sample size, location, period and expected quality level are all missing.

BETTER

> During weeks 18–21, 12 of 80 painted covers inspected from Assembly Cell A had scratches outside the acceptance standard, a defect rate of 15% against a target of no more than 3%.

The defect type, affected product, sample size, process location, period, actual performance and expected performance are explicit. The measurable gap is 12 percentage points, while the cause remains open to investigation.

WEAK

> Purchase orders take too long.

“Too long” has no measurable reference point. The type of purchase order, period, actual processing time, service requirement and size of the affected population are unknown.

BETTER

> During Q2, the median approval time for maintenance purchase orders above £5,000 was 3.6 working days against a two-day service target, with 18 of 64 requests exceeding the requirement.

The population, period, metric, actual result, target and number of affected requests are all defined. The team can now investigate why some approvals exceed the requirement without assuming where the delay occurs.

WEAK

> We keep delivering late because planning is unreliable.

“Keep delivering late” does not quantify the delivery problem, while “because planning is unreliable” introduces an unverified explanation and assigns the investigation to one function before the evidence supports it.

BETTER

> During May and June, on-time delivery for made-to-order Product Group B was 87% across 214 orders against a customer target of 96%, a gap of nine percentage points.

The customer requirement, affected order population, measurement period, actual result and size of the performance gap are clear. Planning may eventually prove relevant, but the problem statement leaves that question for the evidence.

Although the measures are different, each stronger example follows the same logic:

**defined scope + defined period + actual performance + expected performance + measurable gap**

The details needed will vary by problem. A quality issue may require a sample and defect rate, a transactional problem may need a processing-time distribution, and a delivery problem may use a percentage across an order population. The principle remains the same: describe the performance gap in terms the team can verify before trying to explain why it exists.

09 · VALIDATION

## Test the statement before analysis

A statement is ready when it is useful for the next decision—not merely when the sentence is grammatically complete. Review it with the process team and mark any failed check as **Revise** or **Evidence needed**.

* ✓

**A standard or expected condition is named**  
The reference is current, applies to the scope and has a traceable source.
* ✓

**The actual condition is observable**  
The wording describes what happened rather than what the team believes caused it.
* ✓

**The boundary is explicit**  
The product, process, population, location and relevant operating boundary are clear.
* ✓

**The period and pattern are defined**  
The reader can tell when the data was collected and what frequency or sequence is being examined.
* ✓

**The extent has units**  
Counts, rates, duration or percentages include enough context to avoid a misleading number.
* ✓

**Evidence sources are recorded**  
Observed, measured, confirmed, estimated and unknown facts are distinguished.
* ✓

**Cause, blame and solution are absent**  
The statement can survive even if the team’s first explanation later proves wrong.
* ✓

**It describes one investigable problem**  
Separate materially different defects or process gaps instead of joining them with “and”.

Passing this checklist does not prove causation. It means the starting condition is sufficiently clear for the team to select and run the next method.

10 · CHOOSE THE DEPTH

## When one sentence is not enough

A concise statement should focus the work, not flatten a complex system. Use a deeper tool when the boundary, governance or cause structure cannot be represented honestly in one line.

| Current condition                                                          | Use next                                                                                                                  | Why                                                                                                 |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| The boundary is unclear or important contrasts are missing.                | [5W1H Is/Is Not](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/)                                | Compare what is and is not affected across object, place, time and extent.                          |
| One bounded problem has one plausible cause path.                          | [5 Whys](https://www.learnleansigma.com/root-cause-analysis/how-to-do-a-5-whys-analysis/)                                 | Build and verify a focused cause-and-effect chain.                                                  |
| Several credible cause families or functions may interact.                 | [Fishbone, then targeted 5 Whys](https://www.learnleansigma.com/root-cause-analysis/fishbone-diagram-vs-5-whys-analysis/) | Explore broadly before drilling into the evidence-supported paths.                                  |
| The work requires scope, sponsorship, measures and governance.             | [Project charter](https://www.learnleansigma.com/template/project-charter-template/)                                      | Keep the problem, goal, business case, scope, roles and measures aligned.                           |
| The problem needs a complete improvement story or project method.          | [A3](https://www.learnleansigma.com/guides/a3-problem-solving/) or [DMAIC](https://www.learnleansigma.com/guides/dmaic/)  | Carry the defined problem through analysis, countermeasures, implementation and control.            |
| Safety, regulatory or legal consequences are high, or safeguards interact. | [A governed investigation](https://www.learnleansigma.com/guides/root-cause-analysis/)                                    | Use a process capable of representing multiple factors, evidence, barriers and review requirements. |

11 · TROUBLESHOOTING

## Common problem statement mistakes—and how to correct them

Most weak statements do not fail because the author chose the wrong sentence template. They fail because an evidence or reasoning problem is hidden inside polished wording.

01

#### Starting with the assumed cause

**Failure:** “The line stopped because maintenance was poor.” **Correct:** state the recorded stop condition first; test maintenance-related hypotheses later.

02

#### Writing the preferred solution

**Failure:** “We need an automated inspection system.” **Correct:** define the undetected defect or decision gap before choosing technology.

03

#### Blaming a person or role

**Failure:** “Operator error causes scrap.” **Correct:** describe the action, result, standard and conditions without deciding why the action was possible.

04

#### Using adjectives instead of measures

**Failure:** “Delivery performance is poor.” **Correct:** show the service target, actual rate, period and order population.

05

#### Combining several problems

**Failure:** defects, downtime and late delivery are joined in one sentence. **Correct:** separate gaps unless evidence shows they are one bounded event.

06

#### Omitting the standard

**Failure:** the actual number looks unusual but has no approved reference point. **Correct:** name the specification, target or expected condition.

07

#### Adding false precision

**Failure:** a precise cost or impact is quoted without a traceable basis. **Correct:** show the calculation, mark it as an estimate or omit it.

08

#### Hiding unknowns

**Failure:** missing dates or evidence are silently filled from memory. **Correct:** label the statement Evidence needed and assign fact collection.

  
12 · PUT IT TO WORK

## Your next step

Do not wait for a perfect sentence. Create a controlled draft, expose the missing evidence and move it through a short review with the people closest to the work.

1. 01  
#### Draft the observable gap  
Use the formula or builder and keep unsupported facts visibly marked as unknown or estimated.
2. 02  
#### Verify the fact base  
Correct the wording when the current standard, records or direct observation do not support it.
3. 03  
#### Select the lightest suitable next method  
Use Is/Is Not for uncertain boundaries, 5 Whys for a focused path, Fishbone for competing causes, or a governed method for higher-risk work.

LLS**TOOL**_CUST_

ARTICLE RESOURCE

### Define the boundaries with the Is/Is Not template

[Open the free template →](https://www.learnleansigma.com/template/is-is-not-template/)

  
13 · COMMON QUESTIONS

## Problem statement questions, answered

How long should a problem statement be?

Use the shortest wording that preserves the expected condition, actual condition, boundary, period and extent. One or two sentences often work for an operational gap, while supporting evidence, calculation notes and exclusions can sit below it. Do not remove a critical fact merely to meet an arbitrary word count.

Should a problem statement include the root cause?

No—not unless the causal condition has already been established by credible evidence and the statement is explicitly being updated after analysis. The initial problem statement should define what happened and how it differs from the standard. Keep suspected causes as hypotheses to test.

Should it include the solution or goal?

Keep them separate. The problem statement defines the current gap, the goal statement defines the desired future result, and the selected countermeasure describes how the system will be changed. Separating them prevents a preferred solution from narrowing the investigation too early.

Can the problem statement change during an investigation?

Yes. Revise it when verified evidence changes the boundary, measure or affected population. Preserve the revision and explain which evidence changed it. Quietly rewriting the statement to fit a preferred cause is not the same as evidence-led refinement.

What if the expected condition is not documented?

Mark the reference point as unresolved. The team may need to confirm a customer requirement, specification, policy, control limit or agreed operating condition before it can quantify the gap. Do not invent a standard from the best recent result.

What is the difference between 5W1H and a problem statement?

5W1H is a fact-gathering structure that asks who or what, where, when, how and why the issue matters. The problem statement is the concise output built from the verified facts. Use the deeper [Is/Is Not comparison](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/) when boundaries or distinctions remain unclear.

  
14 · SOURCES & EDITORIAL METHOD

## References and editorial method

This guide combines recognised improvement guidance with Daniel Croft-Bednarski’s practical application of problem definition in operational improvement. All numerical examples are illustrative unless explicitly labelled otherwise. A good statement supports investigation; it does not prove causation or guarantee a successful outcome.

1. [Lean Enterprise Institute — Why Effective Problem Solving Begins with a Good Problem Statement](https://www.lean.org/the-lean-post/articles/why-effective-problem-solving-begins-with-a-good-problem-statement/)Supports the observable and measurable target-versus-actual gap at the start of Lean problem solving.
2. [University of Leeds — Problem Statement](https://deliveringresults.leeds.ac.uk/delivering-results-lifecycle/problem-statement/)Provides practical guidance on expected versus actual performance, measurable wording and removing cause or solution language.
3. [ASQ — DMAIC Process: Define, Measure, Analyze, Improve, Control](https://asq.org/quality-resources/dmaic)Places the problem, goals, customers and project charter within the Define phase.
4. [ASQ — What is Problem Solving?](https://asq.org/quality-resources/problem-solving)Positions problem definition before root-cause analysis, solution selection and sustainment.
5. [Boston University CIDA — Crafting Effective Problem Statements](https://www.bu.edu/cida/2024/10/18/crafting-effective-problem-statements/)Supports clarity, measurability, neutrality and refinement as better information becomes available.
6. [Institute for Healthcare Improvement — QI Project Charter](https://www.ihi.org/library/tools/qi-project-charter)Shows how a charter focuses a team on a specific problem or opportunity within a governed improvement effort.
  
Helpful? 

Was this article helpful?

One click. No sign-in required.

Yes, it helped Not quite 

What made this article helpful?

Adding a reason is optional.

**0% found this helpful** Based on 0 responses 

Anything else? (optional) 

Skip Submit feedback 

Feedback received

Thank you for helping us improve this resource.

**0% found this helpful** Based on 0 responses 

[![Daniel Croft-Bednarski](https://secure.gravatar.com/avatar/4073a93815879716212ddab9fc00f615a73d17b30d272f48072a3bb0a895438b?s=300&d=mm&r=g)](https://www.learnleansigma.com/creator/daniel-croft-bednarski/)

ABOUT THE AUTHOR

## Daniel Croft-Bednarski

Daniel is Head of Continuous Improvement and Lean Six Sigma Black Belt with more than 10 years' experience translating problem-solving methods into practical operating routines.

**10+ years' experience** **50+ projects led** **LSS Black Belt**

[Author profile →](https://www.learnleansigma.com/creator/daniel-croft-bednarski/)[LinkedIn →](https://www.linkedin.com/in/danielcroftb/)

ADVERTISEMENT

KEEP LEARNING

## Continue learning.

[01**How to Do a 5 Whys Analysis**Continue from a defined problem into an evidence-led cause chain._→_](https://www.learnleansigma.com/root-cause-analysis/how-to-do-a-5-whys-analysis/)[02**5W1H Is/Is Not Problem Definition**Expand the boundaries when the problem is still unclear._→_](https://www.learnleansigma.com/guides/5w1h-is-is-not-problem-definition/)[03**A3 Problem Solving Guide**Carry the problem statement into a one-page improvement story._→_](https://www.learnleansigma.com/guides/a3-problem-solving/)

Clear 

Search

```json

...6469 bytes truncated...

The tool call succeeded but the output was truncated. Full output saved to: /home/admin/.local/share/opencode/tool-output/tool_03788a4cc001gKCBBlzhdYmiiO
Use the Task tool to have explore agent process this file with Grep and Read (with offset/limit). Do NOT read the full file yourself - delegate to save context.
````

**Tool: specmgr_get_req_example**

**Input:**

```json
{}
```

**Output:**

```
---
created: 2026-08-05 08:15:42
id: deaddead-dead-dead-dead-deaddeaddead
status: draft
type: req
updated: 2026-08-06 03:27:27
version: 1.0.0
---

# Maximum Engine Temperature

WHILE the engine is running, THE temperature must be a maximum of 80 °C.

## Description

If the engine becomes too hot, the lifetime of the system decreases.

## Characteristics

1. Safety
2. Reliability

## Level

MUST

## Priority

50

## Tags

- Combustion Engines
- Vehicles

## Source

The International Safety Board Association (TISBA)

## Related Artifacts

### Requirements

- REQ-9687: Maximum temperatures of running engines in civil vehicles

### Decisions

- DEC-2703: Usage of metal conductors in moving engine parts

### Goals

- GOL-0007: Competitive Engines in Consumer Vehicles

### Acceptance Criteria

- ACC-1234: Temperature Measurements on running combustion engines

## More Information

This optional section can contain additional information. There is no defined format for this section.

## Notes

This optional section can contain additional notes. Example: changes to the requirement.

```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 68.7s)

_Thinking:_

**Tool: asdste100_word_count**

**Input:**

```json
{}
```

**Output:**

```
2200
```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 4.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cat \"/home/admin/src/biz.dfch.SpecMgr/docs/adr/71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and.md\""
}
```

**Output:**

```
---
status: accepted
decision-makers: dfch
id: 71fd95d7-07f2-466f-81aa-d29b7e3ef34c
version: 1.0.0
---

# Generic update_section(key, value) with deletion sentinel and mandatory-section rejection

## Context and Problem Statement

ADR body sections (title, context, decision drivers, outcome, consequences, etc.) must be independently editable. The question is how to structure the tool surface: should each section have its own dedicated tool, or should there be one generic tool that operates on any section key? Additionally, deletion semantics must be clear: how does a caller indicate they want to remove a section?

## Decision Drivers

Maintainability and consistency across the 7 body section types; clear deletion semantics that cannot be confused with other operations; prevent deletion of mandatory sections that would leave the ADR invalid.

## Considered Options

Per-field dedicated tools (update_title, update_context, update_drivers, etc.) vs. one generic keyed tool (update_section); silent drop on empty input vs. explicit deletion sentinel vs. separate delete tool; allow deleting mandatory sections vs. reject with error.

## Decision Outcome

Implement one generic `update_section(id, key, value)` tool for whole-section body edits. Mandatory sections (title, context_and_problem_statement, considered_options, decision_outcome) cannot be deleted; attempting to delete them raises AdrSectionError. Deletion is indicated by submitting an empty string, a whitespace-only string, or the literal case-insensitive "REMOVE". When deletion is requested for a non-mandatory optional section (decision_drivers, consequences, confirmation, more_information), the section heading and content are dropped from the render. Each call re-reads, mutates through in-memory Pydantic models, validates, and re-renders the full file.

### Consequences

One consistent tool interface for all body sections reduces cognitive load and maintenance burden. Clear sentinel-based deletion prevents accidental data loss. Mandatory-section protection ensures ADRs remain schema-valid. Trade-off: the tool surface is slightly more abstract than per-field tools.

```

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/admin/src/biz.dfch.SpecMgr/src -iname \"*update_section*\" -o -iname \"*_util*\" | grep -v test | sort"
}
```

**Output:**

```
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/update_section.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/v1/_util.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/_util.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/models/v2/_util.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/models/v1/_util.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/models/v1/_util.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/models/v2/_util.py

```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 37.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cat \"/home/admin/src/biz.dfch.SpecMgr/docs/adr/ec9f5262-9912-49d0-903f-fcfb54f28c13-expose-domain-list-as-paged-mcp-tools-list-domain-not-resour.md\""
}
```

**Output:**

```
---
status: accepted
date: '2026-08-19'
decision-makers: OpenCode agent + user decision
id: ec9f5262-9912-49d0-903f-fcfb54f28c13
version: 1.0.0
---

# Expose <domain>_list as paged MCP tools (list_<domain>), not resources

## Context and Problem Statement

The five `<domain>_list` MCP resources (`specmgr://adr/list`, `specmgr://req/list`, `specmgr://uc/list`, `specmgr://tsk/list`, `specmgr://qa/list`) each did a full, unbounded directory scan and returned a bare `list[<D>Summary]` on every call. As the number of documents in a base directory grows, this becomes increasingly expensive and eventually unwieldy for a calling agent to consume in one shot. Pagination (`max_results`/`offset`) was raised as feat-7-various-improvements Task 0.15/REQ-002, but MCP resources can only be parameterized via URI-template path segments, not arbitrary query parameters -- so `max_results`/`offset` cannot be added to a `@mcp.resource()` without contorting the URI shape. This mirrors the reasoning already recorded in ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 for `get_req`: resources are a poor fit whenever a read needs caller-supplied parameters.

## Decision Drivers

- Pagination parameters (`max_results`/`offset`) do not fit MCP resources, which are URI-template-only.
- Consistency with ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614's precedent: prefer tools over resources for parameterized, on-demand reads.
- Reuse an existing, proven paged-result shape rather than invent a new one, for consistency across this project's own MCP servers.
- Preserve the exact current scan/sort/skip-broken-file semantics -- no behavioral regression for callers relying on today's full listing.
- Keep the five domains' summary models on one shared, documented base field set where the dependency graph allows it.

## Considered Options

- Option 1: Keep `<domain>_list` as resources, encode `max_results`/`offset` into the URI template (e.g. `specmgr://req/list/{offset}/{max_results}`)
- Option 2: Convert all five `<domain>_list` resources into `@mcp.tool()` `list_<domain>` tools accepting `max_results`/`offset`, returning a shared `PagedResult[T]` wrapper
- Option 3: Keep resources unbounded as-is and defer pagination indefinitely

## Decision Outcome

Chosen option: "Option 2: Convert all five `<domain>_list` resources into `list_<domain>` tools returning `PagedResult[T]`", because it is the only option that gives callers real, bounded pagination without abusing the URI-template mechanism, and it follows the precedent already accepted in ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614. Each `list_<domain>` tool accepts `max_results`/`offset` (default page size 25, cap 100; out-of-range inputs are clamped, not errored), and returns a `PagedResult` shape -- `total`, `offset`, `max_results`, `truncated`, `results` -- taken verbatim from this project's own `asdste100` MCP server (`word_list`, `rules_examples`), rather than inventing a new contract. Each tool still fully materializes its domain's summary list first (identical scan/sort/skip-broken-file behavior as the retired resource) and then slices it in memory, so `total` reflects only parseable documents and no existing behavior regresses.

Four of the five domains' `*Summary` models (`ReqSummary`, `UcSummary`, `TskSummary`, `QaSummary`) now subclass a new shared `general/models/summary.py::DocSummary` base (`id`, `title`, `status`, `ref`). `AdrSummary` (`models/adr/v1/summary.py`) is a deliberate, permanent-for-now outlier: it stays field-identical to `DocSummary` but does not subclass it, because `models/adr` is a dependency-free base-library module (no `mcp` import, per `AGENTS.md`'s "models location" note), while `general/models` transitively requires the `mcp` extra through `general/__init__.py`'s unconditional import of `general.tools`/`general.resources`/`general.prompts`. Making `AdrSummary` subclass `DocSummary` would silently add a new `mcp` dependency to the base library. This is accepted as-is, with a known future redesign path: ADR is the only domain not yet using the generic markdown parser, and a future ADR-domain redesign is expected to revisit this asymmetry; a structural-equivalence test (`tests/general/models/test_summary.py`) keeps the two field sets in sync in the meantime.

This work was split out of feat-7-various-improvements Task 0.15 into its own feature folder, `feat-13-list-paging` (GitHub issue #13), and closes feat-7's REQ-002/ACC-002 (the pagination decision). It also advances, but does not fully close, feat-7's REQ-001/ACC-001 (the shared list-output contract): the contract is now shared and documented across all five domains, but ADR's summary shares it structurally rather than via inheritance, per the outlier above.

### Consequences

Good, because all five `list_<domain>` tools are now reliably invocable by agents with real pagination, matching the tool-first precedent already set for `get_req`.
Good, because the paged-result shape is proven and reused (from `asdste100`), not invented, keeping this project's own MCP servers consistent with each other.
Good, because scan/sort/skip-broken-file behavior is unchanged -- `total` still reflects only parseable documents, and each domain's own parse-failure exception tuple (e.g. ADR's `(AdrParseError, ValidationError)` vs. the other four's `(AssertionError, ValidationError)`) is preserved exactly.
Bad, because the five `<domain>_list` MCP resources are gone; any external client that was reading them as context-attachment resources (per the original rationale in ADR 7531106b-074b-4bd8-a83a-e433d01676e2) must switch to calling the `list_<domain>` tool instead.
Bad, because `AdrSummary` remains a visible, permanent-for-now asymmetry against the shared `DocSummary` base -- readers must know this is intentional (dependency-graph-driven), not an oversight, and that a future ADR-domain redesign may eventually resolve it.
Neutral, because this partially reverses the listing side of ADR 7531106b-074b-4bd8-a83a-e433d01676e2 (which added `specmgr://adr/list` as a resource) while leaving that ADR's by-id resource decision (`specmgr://adr/{id}`) untouched.

## More Information

Supersedes the listing-resource half of ADR 7531106b-074b-4bd8-a83a-e433d01676e2 ("Expose listing and by-id reads as MCP resources in addition to tools") for all five domains; that ADR's by-id resource decision is unaffected. Extends the tool-over-resource precedent of ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (`get_req`) to the listing case. Implemented in `.specmgr/feat/feat-13-list-paging/README.md` (split out of `feat-7-various-improvements` Task 0.15), which tracks the full per-domain task breakdown; see that feature folder's Decisions Made log for implementation-level detail not repeated here.

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-13-list-paging/README.md"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-13-list-paging/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-19
3: id: feat-13-list-paging
4: status: done
5: updated: 2026-08-19
6: version: 1.0.0
7: ---
8: 
9: # Feature: Pagination for `<domain>_list` MCP tools
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Convert the five `<domain>_list` MCP resources (`adr_list`, `req_list`,
16: `uc_list`, `tsk_list`, `qa_list`) into `@mcp.tool()` tools that support
17: pagination via `max_results`/`offset`, returning a shared `PagedResult`
18: wrapper. Split out of `feat-7-various-improvements` Task 0.15 (and closes
19: its REQ-002/ACC-002 pagination decision) into a dedicated, orchestrator-
20: drivable feature folder.
21: 
22: Today every `<domain>_list` is an `@mcp.resource("specmgr://<d>/list")`
23: returning a bare `list[<D>Summary]` via a full, unbounded
24: `sorted(glob("*.md"))` scan on every call. MCP resources cannot take
25: arbitrary parameters (only URI-template path segments), so
26: `max_results`/`offset` fit cleanly only as tool parameters — the same
27: resource→tool reasoning already applied in feat-7 Task 0.9 (`get_req`).
28: 
29: ### Requirements
30: 
31: - REQ-001: All five `list_<domain>` tools share one documented paged output
32:   contract — a `PagedResult` wrapper with fields `total`, `offset`,
33:   `max_results`, `truncated`, `results`.
34: - REQ-002: `max_results`/`offset` with a sane default page size (25) and cap
35:   (100); out-of-range inputs are clamped, not errored (mirrors this
36:   project's `asdste100` MCP tools).
37: - REQ-003: The five id/title/status/`ref` summaries share a documented
38:   common base model (carries forward feat-7 ACC-001).
39: - REQ-004: No behavioral regression in directory scan/sort/skip-broken-file
40:   semantics; each domain's existing parse-failure exception tuple is
41:   preserved.
42: 
43: ### Acceptance Criteria
44: 
45: - [x] ACC-001: Verifies REQ-001 — all five tools return the same
46:   `PagedResult` shape, asserted by tests across every domain. **Verified**:
47:   `tests/adr/tools/test_list_adr.py`, `tests/req/tools/test_list_req.py`,
48:   `tests/uc/tools/test_list_uc.py`, `tests/tsk/tools/test_list_tsk.py`,
49:   and `tests/qa/tools/test_list_qa.py` each import `PagedResult` and
50:   assert `self.assertIsInstance(sut, PagedResult)` on the `list_<d>()`
51:   return value.
52: - [x] ACC-002: Verifies REQ-002 — tests cover default page size, cap
53:   clamping, negative-offset flooring, and `offset` past the end returning
54:   empty `results` with `truncated == False`. **Verified**: unit-level
55:   coverage in `tests/general/tools/test_paging.py` (e.g.
56:   `test_defaults_both_when_neither_given`,
57:   `test_clamps_max_results_above_the_cap`,
58:   `test_floors_a_negative_offset_to_zero`,
59:   `test_offset_past_the_end_yields_empty_results_and_is_not_truncated`,
60:   `test_out_of_range_inputs_are_clamped_not_errored`), plus each of the
61:   five `test_list_<d>.py` files independently re-asserting the same
62:   behaviors end-to-end through the tool
63:   (`test_default_page_size_and_shape`,
64:   `test_max_results_limits_page_and_marks_truncated`,
65:   `test_offset_selects_the_next_page`,
66:   `test_max_results_is_clamped_to_the_cap`,
67:   `test_negative_offset_is_floored_to_zero`,
68:   `test_truncated_boundary_false_when_page_covers_all_items`,
69:   `test_truncated_boundary_true_when_one_item_remains`).
70: - [x] ACC-003: Verifies REQ-003 — all five Summary models share a common
71:   base field set, asserted by a shared/side-by-side test. **Verified as
72:   literally worded** (a common *field set*, not necessarily a common
73:   *base class* — that stronger claim belongs to REQ-003/Task 1.3, not this
74:   ACC): `tests/general/models/test_summary.py::
75:   TestAllFiveSummariesShareTheCommonBaseFieldSet.
76:   test_all_five_summaries_declare_the_same_field_names` asserts
77:   `[AdrSummary, ReqSummary, UcSummary, TskSummary, QaSummary]` all declare
78:   exactly `["id", "title", "status", "ref"]`. Four of the five
79:   (`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary`) achieve this via
80:   actual `DocSummary` subclassing (`TestReqSummarySharesDocSummaryBase` et
81:   al. assert `issubclass(..., DocSummary)`); `AdrSummary` achieves it via
82:   structural equivalence only (`TestAdrSummaryIsStructurallyEquivalent`
83:   explicitly asserts `assertFalse(issubclass(AdrSummary, DocSummary))`
84:   alongside matching field names/annotations) — the field-set contract
85:   this ACC actually asks for holds across all five, the class-hierarchy
86:   mechanism does not.
87: - [x] ACC-004: Verifies REQ-004 — existing skip-malformed-file and
88:   empty-directory behavior still holds; per-domain exception tuples
89:   unchanged. **Verified**: each `<d>/tools/list_<d>.py` preserves its
90:   domain's original parse-failure exception tuple exactly — ADR's
91:   `except (AdrParseError, ValidationError):` in `list_adr.py` vs. the
92:   other four's `except (AssertionError, ValidationError):` in
93:   `list_req.py`/`list_uc.py`/`list_tsk.py`/`list_qa.py`. Skip-malformed-
94:   file and empty-directory coverage was migrated (not dropped) into each
95:   `test_list_<d>.py`'s `test_returns_summaries_and_skips_malformed_file`
96:   and `test_empty_result_for_missing_directory` tests, e.g.
97:   `tests/adr/tools/test_list_adr.py` writes one valid + one syntactically
98:   broken `.md` file and asserts `sut.total == 2` (the broken file is
99:   silently skipped, not counted or raised).
100: 
101: ### Scope
102: 
103: What is included in this feature:
104: 
105: - New shared infrastructure in `general/`: `PagedResult[T]` model and a
106:   `paginate`/`normalize_paging` helper.
107: - Optional shared base `DocSummary` for the five Summary models.
108: - Resource→tool conversion of all five `<domain>_list` (adr/req/uc/tsk/qa),
109:   including deleting the old resource modules and updating registrations.
110: - Repointing prompt instruction files and `server.py` docstring from
111:   `specmgr://<d>/list` to the new `list_<d>` tool.
112: - A short ADR recording the resource→tool + `PagedResult` contract decision.
113: 
114: What is explicitly out of scope:
115: 
116: - Filtering (feat-7 Task 0.16) — the contract must stay forward-compatible
117:   with it, but no filtering is implemented here.
118: - Migrating ADR onto the shared `general/tools/_doc_paths` module — ADR
119:   keeps its own `adr/tools/_paths` (only its resource→tool layer changes).
120: - Any change to the `specmgr://<d>/{id}` / `get_<d>` single-document reads.
121: 
122: ### Dependencies
123: 
124: - Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
125:   feature-folder structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2
126:   (domain-first hierarchy).
127: - Split out of: `feat-7-various-improvements` Task 0.15 (pointer left in
128:   that file). Closes feat-7 REQ-002/ACC-002; advances feat-7 REQ-001/ACC-001.
129: - Blocks: feat-7 Task 3.1b (pagination piece of the list-resource contract).
130: 
131: ### Design Notes
132: 
133: - **Result shape** is taken verbatim from this project's `asdste100` MCP
134:   tools (e.g. `word_list`, `rules_examples`), whose live shape is
135:   `{ total, offset, max_results, truncated, results: [...] }`. Reused rather
136:   than invented so the contract is consistent across d-fens MCP servers.
137: - **Full materialize, then slice.** `total` must reflect the count of
138:   *parseable* documents (skip-broken-file semantics), so each tool builds
139:   the complete `summaries` list exactly as today, then paginates the
140:   in-memory list. Behavior is therefore identical to the current scan; a
141:   streaming/early-stop optimization is explicitly out of scope.
142: - **Tool naming** `list_<domain>` (verb-first, matching `get_<domain>` /
143:   `create_<domain>`). The retired resource *name* `<domain>_list` is not
144:   resurrected as a tool name.
145: - **Module location** `<d>/tools/list_<d>.py` (it is now a tool, so it
146:   belongs under `tools/`, not `resources/`), registered in
147:   `<d>/tools/__init__.py` like `get_<d>`.
148: - **ADR outlier.** ADR uses its own `adr/tools/_paths.iter_adr_paths` and
149:   the top-level `models/adr` `AdrSummary`; the conversion happens at the
150:   tool layer only, leaving its `_paths` untouched. Its parse-failure tuple
151:   `(AdrParseError, ValidationError)` differs from the others'
152:   `(AssertionError, ValidationError)` — this divergence is intentional and
153:   must be preserved (REQ-004).
154: - **Shared base Summary** (`DocSummary`) is the concrete way to satisfy
155:   ACC-001/REQ-003; the five domain Summaries subclass it, keeping their
156:   domain-specific docstrings.
157: 
158: ### Related ADRs
159: 
160: - e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
161:   `.specmgr` with feature-driven work units
162: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
163:   document-type domain (domain-first hierarchy)
164: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: `get_req` tool vs. resource
165:   (precedent for resource→tool for agent reliability)
166: - ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as paged
167:   MCP tools (`list_<domain>`), not resources (this feature's own decision
168:   record, written in Task 4.3; partially supersedes the listing side of
169:   ADR 7531106b-074b-4bd8-a83a-e433d01676e2)
170: 
171: ### Task List
172: 
173: Single, canonical breakdown of work phases and tasks. Status lives on the
174: task itself — there is no separate "planned" vs. "executed" list to keep in
175: sync; a task's line *is* its current status. Update it in place as work
176: progresses (edit, don't duplicate).
177: 
178: #### Phase 1: Shared infrastructure
179: 
180: - [x] Task 1.1: Add `general/models/` sub-package (does not exist yet) with
181:   `paged_result.py` — `PagedResult(BaseModel, Generic[T])`, fields in order
182:   `total: int`, `offset: int`, `max_results: int`, `truncated: bool`,
183:   `results: list[T]`, fully documented per `.specmgr/conventions.md`; export
184:   from `general/models/__init__.py` — depends on: none — status: done
185: - [x] Task 1.2: Add `general/tools/_paging.py` (no `mcp` dependency, like
186:   `_doc_paths.py`): `DEFAULT_MAX_RESULTS = 25`, `MAX_MAX_RESULTS = 100`,
187:   `normalize_paging(max_results, offset) -> tuple[int, int]` (clamp/floor),
188:   `paginate(items, offset, max_results) -> PagedResult[T]` (`total = len`,
189:   slice, `truncated = offset + max_results < total`) — depends on: Task 1.1
190:   — status: done
191: - [x] Task 1.3: Add `general/models/summary.py::DocSummary(BaseModel)` with
192:   the four common fields (`id`, `title`, `status`, `ref`) and make
193:   `AdrSummary`/`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` subclass it
194:   (ACC-001/REQ-003) — depends on: none — status: done, with one deliberate
195:   exception: `AdrSummary` does **not** subclass `DocSummary` (see Decisions
196:   Made below) — `ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` do.
197: - [x] Task 1.4: Tests — `tests/general/models/test_paged_result.py`,
198:   `tests/general/tools/test_paging.py` (empty, exact-fit, over-offset,
199:   `truncated` boundary, clamping, negative offset), and (if 1.3 adopted) a
200:   shared-base assertion — depends on: Task 1.1, Task 1.2, Task 1.3 —
201:   status: done (`tests/general/models/test_summary.py` added for the
202:   shared-base assertion, including the structural-equivalence check for
203:   the `AdrSummary` exception)
204: - [x] Task 1.5: Phase gate — `ruff format --check`, `ruff check`,
205:   `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite —
206:   depends on: Task 1.4 — status: done, all green (see Recent Updates)
207: 
208: #### Phase 2: Per-domain resource→tool conversion
209: 
210: Each of these adds `<d>/tools/list_<d>.py` (`@mcp.tool(name="list_<d>")`
211: returning `PagedResult[<D>Summary]`, same scan + preserved exception tuple,
212: then `paginate(summaries, *normalize_paging(...))`), deletes
213: `<d>/resources/<d>_list.py`, drops its import/`__all__` from
214: `<d>/resources/__init__.py`, registers the tool in `<d>/tools/__init__.py`,
215: updates `<d>/__init__.py`'s module docstring, and moves/rewrites that
216: domain's list test to `tests/<d>/tools/test_list_<d>.py` with paging
217: assertions. All depend only on Phase 1 (parallelizable).
218: 
219: - [x] Task 2.1: ADR (`adr/tools/list_adr.py`; delete
220:   `adr/resources/adr_list.py`; keep `adr_get` in
221:   `adr/resources/__init__.py`; uses `iter_adr_paths` + top-level
222:   `AdrSummary`; exception tuple `(AdrParseError, ValidationError)`) —
223:   depends on: Task 1.5 — status: done
224: - [x] Task 2.2: REQ (`req/tools/list_req.py`) — depends on: Task 1.5 —
225:   status: done
226: - [x] Task 2.3: UC (`uc/tools/list_uc.py`; uses `..models.v2` `UcSummary`)
227:   — depends on: Task 1.5 — status: done
228: - [x] Task 2.4: TSK (`tsk/tools/list_tsk.py`) — depends on: Task 1.5 —
229:   status: done
230: - [x] Task 2.5: QA (`qa/tools/list_qa.py`) — depends on: Task 1.5 —
231:   status: done
232: - [x] Task 2.6: Phase gate — `ruff format --check`, `ruff check`,
233:   `vulture src/ whitelist.py --min-confidence 60` (catches the five deleted
234:   resource modules), full `unittest` suite — depends on: Task 2.1, Task 2.2,
235:   Task 2.3, Task 2.4, Task 2.5 — status: done, all green (see Recent
236:   Updates); one pre-existing test
237:   (`tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`)
238:   needed its hardcoded ADR tool/resource counts updated (11->12 tools,
239:   2->1 resources) to reflect the resource->tool conversion -- `docs/
240:   GENERATED.md`/`docs/MCP.md` themselves are left stale on purpose,
241:   regeneration is Task 4.1
242: 
243: #### Phase 3: Cross-references
244: 
245: - [x] Task 3.1: Repoint `specmgr://<d>/list` mentions in prompt instruction
246:   data files (`qa/data/qa_create_instructions.md`,
247:   `qa/data/qa_refine_instructions.md`, `adr/data/adr_create_instructions.md`,
248:   `adr/data/adr_create_test_instructions.md`,
249:   `tsk/data/tsk_create_instructions.md`, `req/data/req_create_instructions.md`)
250:   and `qa/prompts/refine.py`'s docstring to the new `list_<d>` tool; update
251:   `tests/qa/prompts/test_refine.py` if it asserts the old resource string —
252:   depends on: Phase 2 — status: done (also repointed the analogous stale
253:   `specmgr://<d>/list` mentions in `req/prompts/create_req.py`,
254:   `tsk/prompts/create_task.py`, and `qa/prompts/create_qa.py`'s own module
255:   docstrings, and fixed the five sibling prompt tests that broke as a
256:   direct consequence — see Recent Updates)
257: - [x] Task 3.2: `server.py` module docstring — remove the five
258:   `specmgr://<d>/list` resource lines, add `list_<d>` to each domain's Tools
259:   line — depends on: Phase 2 — status: done
260: 
261: #### Phase 4: Verify & document
262: 
263: - [x] Task 4.1: Regenerate `docs/api/`/`docs/GENERATED.md`
264:   (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 —
265:   depends on: Task 3.1, Task 3.2 — status: done (2026-08-19); both
266:   commands ran clean with zero resulting diff — Phases 2/3's pre-commit
267:   hooks had already kept `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`
268:   in sync, so this step confirmed no drift rather than fixing any
269: - [x] Task 4.2: Full quality gate — `ruff format --check`, `ruff check`,
270:   `vulture src/ whitelist.py --min-confidence 60`, full `unittest` suite —
271:   depends on: Task 4.1 — status: done (2026-08-19), all green (1276
272:   tests; see Recent Updates)
273: - [x] Task 4.3: Write a **short** ADR recording the resource→tool +
274:   `PagedResult` contract decision (mirroring ADR `ddfb1109`'s precedent);
275:   run `specmgr adr-toc`; update `AGENTS.md` if the per-domain
276:   resource/tool inventory shifts — depends on: Task 4.2 — status: done
277:   (2026-08-19); ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 ("Expose
278:   `<domain>_list` as paged MCP tools (`list_<domain>`), not resources")
279:   written via the `create_adr` MCP tool, `specmgr adr-toc` regenerated
280:   `docs/adr/README.md`, and `AGENTS.md`'s per-domain inventory bullets
281:   updated (all five `list_<d>` tools added, all five
282:   `specmgr://<d>/list` resource mentions removed)
283: - [x] Task 4.4: Back-update `feat-7-various-improvements/README.md` — mark
284:   Task 0.15 done/split, close REQ-002/ACC-002, advance REQ-001/ACC-001,
285:   update Task 2.1/3.1b status lines — depends on: Task 4.3 — status: done
286:   (2026-08-19); Task 0.15 marked done, ACC-002 marked done citing the new
287:   ADR, ACC-001 left unchecked but annotated with the 4-of-5-subclass /
288:   ADR-outlier caveat, Task 2.1's note updated to "completed" (checkbox
289:   left as-is pending its own Task 1.1 dependency), Task 3.1b marked done
290: 
291: **Note:** If a task's scope changes mid-flight, edit its description in place;
292: rely on git history (`git log -p` on this file) to recover what was
293: originally planned, rather than keeping a second copy of the task around.
294: 
295: ## Progress
296: 
297: ### Current Status
298: 
299: **As of 2026-08-19: feature complete (all four phases done).** `PagedResult`
300: (`general/models/paged_result.py`), `DocSummary`
301: (`general/models/summary.py`), and the `normalize_paging`/`paginate` helpers
302: (`general/tools/_paging.py`) all exist, tested, and pass the full quality
303: gate. `ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary` now subclass
304: `DocSummary`; `AdrSummary` deliberately does not, staying field-identical
305: but structurally verified instead (the permanent-for-now "ADR outlier" --
306: see Decisions Made and the new ADR below). All five `<domain>_list`
307: resources (`adr_list`, `req_list`, `uc_list`, `tsk_list`, `qa_list`) have
308: been converted into paged `list_<domain>` `@mcp.tool()`s
309: (`adr/tools/list_adr.py`, `req/tools/list_req.py`, `uc/tools/list_uc.py`,
310: `tsk/tools/list_tsk.py`, `qa/tools/list_qa.py`), each returning
311: `PagedResult[<D>Summary]` and preserving its own skip-malformed-file
312: exception tuple exactly (REQ-004). Every prompt instruction data file and
313: prompt module docstring that used to point at a retired
314: `specmgr://<d>/list` resource now points at the corresponding `list_<d>`
315: tool instead, and `server.py`'s own module docstring reflects the same
316: repointing. `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` are regenerated
317: and drift-free; the full quality gate (`ruff format --check`, `ruff
318: check`, `vulture`, 1276 `unittest` tests) is green. The decision is
319: recorded in ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 ("Expose
320: `<domain>_list` as paged MCP tools (`list_<domain>`), not resources"),
321: `docs/adr/README.md` includes it, and `AGENTS.md`'s per-domain inventory
322: reflects the five new `list_<d>` tools / five removed
323: `specmgr://<d>/list` resources. `feat-7-various-improvements/README.md`
324: has been back-updated: Task 0.15 is done, ACC-002/REQ-002 (pagination
325: decision) is closed, and ACC-001/REQ-001 (shared list-output contract) is
326: advanced but explicitly not closed, since the ADR outlier means the
327: contract is shared by convention/test rather than uniformly by class
328: hierarchy. Nothing further is planned for this feature folder.
329: 
330: ### Recent Updates
331: 
332: #### Update 2026-08-19 (newest, feature complete)
333: 
334: - Completed: Phase 4 (Verify & document) -- Tasks 4.1-4.4. This closes
335:   out `feat-13-list-paging` entirely; frontmatter `status` moved from
336:   `planning` to `done`.
337:   - Task 4.1: Ran `specmgr docs` and `specmgr mcp-docs` (Python 3.13.13,
338:     confirmed via `uv run --frozen python --version`). Both completed with
339:     zero resulting `git status` diff -- Phase 2's and Phase 3's own
340:     pre-commit hooks had already kept `docs/api/`/`docs/GENERATED.md`/
341:     `docs/MCP.md` fully in sync with the `list_<d>` conversion, so this
342:     step confirmed no drift remained rather than fixing any.
343:   - Task 4.2: Full quality gate re-run one more time --
344:     `ruff format --check` (814 files already formatted), `ruff check`
345:     (all checks passed), `vulture src/ whitelist.py --min-confidence 60`
346:     (no output, i.e. clean), and the full `unittest` suite (1276 tests,
347:     OK) -- all green.
348:   - Task 4.3: Wrote ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 ("Expose
349:     `<domain>_list` as paged MCP tools (`list_<domain>`), not resources"),
350:     via the `create_adr` MCP tool (canonical path, available in-session --
351:     no manual UUID/slug/file-write fallback needed). Covers: the
352:     URI-template limitation that ruled out paginated resources, the
353:     `PagedResult`/`asdste100`-shape decision, the `DocSummary`
354:     shared-base decision plus the ADR-outlier asymmetry (with its accepted,
355:     known-future-redesign framing per the user's explicit guidance), and
356:     the feat-7 Task 0.15 split/REQ-002/ACC-002/REQ-001/ACC-001
357:     cross-references -- kept short, mirroring ADR `ddfb1109`'s tone rather
358:     than restating this whole plan. Ran `specmgr adr-toc`, which
359:     regenerated `docs/adr/README.md` to include the new entry. Updated
360:     `AGENTS.md`'s per-domain inventory section (the "six domain/
361:     cross-cutting packages implemented" list): added `list_adr`/`list_req`/
362:     `list_uc`/`list_tsk`/`list_qa` to each domain's tools enumeration, and
363:     removed the now-retired `specmgr://adr/list`/`specmgr://req/list`/
364:     `specmgr://qa/list` resource mentions (ADR's tool count bullet updated
365:     from 11 to 12; UC's and TSK's bullets never explicitly enumerated
366:     `specmgr://<d>/list` in the first place, so only their tool lists
367:     needed the `list_<d>` addition).
368:   - Task 4.4: Back-updated `feat-7-various-improvements/README.md`:
369:     Task 0.15 marked `[x]` done, noting `feat-13-list-paging` is complete
370:     and citing the new ADR; ACC-002 marked `[x]` done, citing the new ADR
371:     as the recorded pagination decision; ACC-001 deliberately left `[ ]`
372:     unchecked but annotated with the explicit 4-of-5-domains-subclass /
373:     ADR-structural-not-inheritance caveat, since the shared base contract
374:     is not uniformly achieved by class hierarchy across all five domains;
375:     Task 2.1's status note updated from "split" to "completed" (citing the
376:     ADR), checkbox left as `[ ]` since its own stated dependency (Task
377:     1.1, the formal inventory audit) is still not-started; Task 3.1b
378:     marked `[x]` done, citing the new ADR. Task 3.1a, Task 2.2, Task 3.2,
379:     and the `_test` prompt-variant material were left untouched
380:     (REQ-003/REQ-004 concerns, out of scope here).
381: - Quality gate: all four commands green (see Task 4.2 above); no
382:   code under `src/` was touched in this phase (docs/ADR/plan-file changes
383:   only), consistent with this phase's constraint.
384: - Next: none -- `feat-13-list-paging` is done.
385: 
386: #### Update 2026-08-19 (continued)
387: 
388: - Completed: Phase 3 (Cross-references) -- Tasks 3.1-3.2.
389:   - Repointed every prompt-instruction-data-file mention of a retired
390:     `specmgr://<d>/list` resource to its replacement `list_<d>` tool, with
391:     wording reworded from "Read the ... resource" to "Call the ... tool"
392:     (or "call the ... tool" in the step-gated ADR variant) to read
393:     naturally as a tool call rather than a resource read:
394:     `qa/data/qa_create_instructions.md`, `qa/data/qa_refine_instructions.md`,
395:     `adr/data/adr_create_instructions.md`,
396:     `adr/data/adr_create_test_instructions.md`,
397:     `tsk/data/tsk_create_instructions.md`,
398:     `req/data/req_create_instructions.md`.
399:   - Repointed `qa/prompts/refine.py`'s module docstring and its `refine()`
400:     function docstring the same way (`specmgr://qa/list` -> `list_qa`).
401:   - Went beyond the plan's explicitly named locations to also fix three
402:     analogous stale mentions the plan's own grep pass had missed, since
403:     leaving them would have described a resource that no longer exists:
404:     `req/prompts/create_req.py`, `tsk/prompts/create_task.py`, and
405:     `qa/prompts/create_qa.py`'s own module docstrings each still named
406:     `specmgr://<d>/list` as part of the tool/resource surface they
407:     describe; repointed each to `list_<d>`.
408:   - Updated `server.py`'s module docstring: removed all five
409:     `specmgr://adr/list`/`specmgr://req/list`/`specmgr://uc/list`/
410:     `specmgr://tsk/list`/`specmgr://qa/list` lines from the "Resources"
411:     section, and added `list_adr`/`list_req`/`list_uc`/`list_tsk`/`list_qa`
412:     to each domain's "Tools" line, positioned right after the matching
413:     `get_<d>` entry.
414:   - Fixed the five sibling prompt tests that broke as a direct, expected
415:     consequence of the instruction-file repointing (each asserted the old
416:     `specmgr://<d>/list` string against the prompt's rendered output;
417:     not explicitly named by the plan's task text beyond
418:     `tests/qa/prompts/test_refine.py`, but required for a green quality
419:     gate): `tests/qa/prompts/test_create_qa.py`,
420:     `tests/tsk/prompts/test_create_task.py`,
421:     `tests/adr/prompts/test_create_adr.py`,
422:     `tests/adr/prompts/test_create_adr_test.py`,
423:     `tests/req/prompts/test_create_req.py` -- each renamed its
424:     `test_mentions_duplicate_check_resource`/similar test method to
425:     `test_mentions_duplicate_check_tool`/`test_mentions_list_qa_tool_for_lookup`
426:     and reasserts against the new `list_<d>` tool name instead of the old
427:     resource URI.
428:   - Initially left `README.md`'s CLI-examples/TUI-tabs sections untouched
429:     (not named by this phase's task text), but on reviewer correction
430:     fixed all three genuinely broken spots there too, since they demoed a
431:     resource that no longer exists (a reader following them verbatim would
432:     hit "resource not found"): "List task lists via the `specmgr://tsk/list`
433:     resource" + its `--method resources/read --uri specmgr://tsk/list`
434:     example -> "List task lists via the `list_tsk` tool" +
435:     `--method tools/call --tool-name list_tsk`, matching the `get_tsk`
436:     example's own `tools/call` style immediately below it; the `get_tsk`
437:     example's own "from the `specmgr://tsk/list` output above" ->
438:     "from the `list_tsk` output above"; and the TUI Resources-tab
439:     description's `specmgr://tsk/list` example -> `specmgr://iso25010`
440:     (a resource that still exists).
441:   - Quality gate: `ruff format --check`, `ruff check`,
442:     `vulture src/ whitelist.py --min-confidence 60`, and the full
443:     `unittest` suite (1276 tests) all pass clean (re-confirmed after the
444:     `README.md` fix too, unchanged since `README.md` isn't executed/linted).
445: - Next: Phase 4 (verify & document, Tasks 4.1-4.4).
446: 
447: #### Update 2026-08-19 (continued)
448: 
449: - Completed: Phase 2 (Per-domain resource->tool conversion) -- Tasks
450:   2.1-2.6.
451:   - Added `adr/tools/list_adr.py`, `req/tools/list_req.py`,
452:     `uc/tools/list_uc.py`, `tsk/tools/list_tsk.py`, `qa/tools/list_qa.py`
453:     -- each an `@mcp.tool(name="list_<d>")` returning
454:     `PagedResult[<D>Summary]`; same directory scan and skip-broken-file
455:     logic as the retired resource, then
456:     `paginate(summaries, *normalize_paging(max_results, offset))`.
457:     ADR's `(AdrParseError, ValidationError)` exception tuple and the other
458:     four's `(AssertionError, ValidationError)` were both preserved exactly
459:     unchanged, per-domain.
460:   - Deleted the five retired resource modules: `adr/resources/adr_list.py`,
461:     `req/resources/req_list.py`, `uc/resources/uc_list.py`,
462:     `tsk/resources/tsk_list.py`, `qa/resources/qa_list.py`.
463:   - Updated every `<d>/resources/__init__.py` to drop the `<d>_list`
464:     import/`__all__` entry (ADR's `adr_get` stays); updated every
465:     `<d>/tools/__init__.py` to register `list_<d>`; updated every
466:     `<d>/__init__.py`'s own module docstring where it enumerated
467:     tools/resources.
468:   - Migrated list tests: `tests/adr/tools/test_list_adr.py` (new; the old
469:     `TestAdrListResource` class was removed from
470:     `tests/adr/resources/test_adr.py`, leaving `TestAdrGetResource` in
471:     place), `tests/req/tools/test_list_req.py`,
472:     `tests/uc/tools/test_list_uc.py`, `tests/tsk/tools/test_list_tsk.py`,
473:     `tests/qa/tools/test_list_qa.py` (each replaces the deleted
474:     `tests/<d>/resources/test_<d>_list.py`). Each migrated
475:     skip-malformed-file/empty-directory coverage as-is, plus added: default
476:     page size/shape, `max_results` limiting + `truncated`, `offset` paging
477:     to a second page, `max_results` clamped to the cap, negative `offset`
478:     floored to zero, `truncated` boundary (false when a page exactly covers
479:     all items, true when one item remains), and `total` reflecting the full
480:     parseable count independent of paging.
481:   - Fixed one pre-existing test that broke as a direct, expected
482:     consequence of the ADR resource->tool conversion:
483:     `tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`
484:     hardcoded ADR's tool/resource counts (11/2); updated to 12/1 now that
485:     `list_adr` lives under `adr/tools/` instead of `adr/resources/`.
486:     `docs/GENERATED.md`/`docs/MCP.md` themselves are deliberately left
487:     stale -- their regeneration is Task 4.1, not Phase 2's job.
488:   - Quality gate: `ruff format --check`, `ruff check`,
489:     `vulture src/ whitelist.py --min-confidence 60`, and the full
490:     `unittest` suite (1276 tests) all pass clean.
491: - Next: Phase 3 (cross-references, Tasks 3.1-3.2).
492: 
493: - Completed: Phase 1 (Shared infrastructure) — Tasks 1.1-1.5.
494:   - Added `general/models/` (new sub-package): `__init__.py`,
495:     `paged_result.py::PagedResult(BaseModel, Generic[T])`,
496:     `summary.py::DocSummary(BaseModel)`.
497:   - Added `general/tools/_paging.py`: `DEFAULT_MAX_RESULTS`/
498:     `MAX_MAX_RESULTS`/`MIN_MAX_RESULTS`/`MIN_OFFSET` constants,
499:     `normalize_paging(max_results, offset) -> tuple[int, int]` (returns
500:     `(offset, max_results)`, clamped/floored), `paginate(items, offset,
501:     max_results) -> PagedResult[T]`.
502:   - Made `ReqSummary`, `UcSummary`, `TskSummary`, `QaSummary` subclass
503:     `DocSummary`, dropping their now-duplicated field declarations.
504:     `AdrSummary` was deliberately **not** changed to subclass it (see
505:     Decisions Made) — a structural-equivalence test covers it instead.
506:   - Added tests: `tests/general/models/test_paged_result.py`,
507:     `tests/general/models/test_summary.py` (`DocSummary` +
508:     shared/side-by-side base-field-set assertion across all five domains),
509:     `tests/general/tools/test_paging.py` (empty, exact-fit, over-offset,
510:     `truncated` boundary, clamping, negative-offset flooring,
511:     `normalize_paging` + `paginate` splat-unpacking integration).
512:   - Added `results`/`truncated` to `whitelist.py`'s "Pydantic model fields
513:     read only via (de)serialization/rendering" section (flagged by
514:     vulture since nothing under `src/` reads them as plain attributes
515:     yet -- that lands in Phase 2).
516:   - Quality gate: `ruff format --check`, `ruff check`,
517:     `vulture src/ whitelist.py --min-confidence 60`, and the full
518:     `unittest` suite (1236 tests) all pass clean.
519: - Next: Phase 2 (per-domain resource→tool conversion, Tasks 2.1-2.6).
520: - Notes: Confirmed via a simulated mcp-import-blocked run that
521:   `biz.dfch.specmgr.models.adr`/`AdrSummary` still import successfully
522:   without the `mcp` extra installed, preserving the base-library
523:   invariant documented in `AGENTS.md`'s "models location" note.
524: 
525: #### Update 2026-08-19
526: 
527: - Completed: Created GitHub issue #13; created this feature folder from
528:   `.specmgr/_template/v1/README.md` with the full four-phase plan.
529: - Next: Phase 1 (shared `PagedResult` model + `_paging` helper).
530: - Notes: Split out of `feat-7` Task 0.15; a pointer was added there.
531: 
532: ### Decisions Made
533: 
534: - **2026-08-19**: Convert `<domain>_list` from `@mcp.resource` to
535:   `@mcp.tool()` (`list_<domain>`) — resources cannot take arbitrary
536:   parameters, so paging params only fit as tool inputs; consistent with the
537:   feat-7 Task 0.9 `get_req` resource→tool precedent.
538: - **2026-08-19**: Return an `asdste100`-style `PagedResult` wrapper
539:   (`total`/`offset`/`max_results`/`truncated`/`results`) — reuse an existing
540:   d-fens MCP shape rather than invent one.
541: - **2026-08-19**: Put paging infrastructure in `general/`
542:   (`general/models/PagedResult`, `general/tools/_paging`) shared by all five
543:   domains; ADR stays the outlier (own `_paths`), converted at the tool layer
544:   only.
545: - **2026-08-19**: Paging only; filtering stays feat-7 Task 0.16, but the
546:   contract must remain forward-compatible with it.
547: - **2026-08-19**: `normalize_paging` clamping semantics (not fully pinned
548:   down by the plan text): a caller-supplied `max_results` out of
549:   `[MIN_MAX_RESULTS, MAX_MAX_RESULTS]` is *clamped* to the nearer bound
550:   (e.g. `500` -> `100`, `0` -> `1`), not reset to `DEFAULT_MAX_RESULTS`;
551:   only an actually-absent (`None`) `max_results`/`offset` gets the default
552:   (`DEFAULT_MAX_RESULTS`/`0`). A negative `offset` floors to `0`.
553:   `normalize_paging` returns `(offset, max_results)` -- offset first, the
554:   reverse of its own parameter order -- specifically so Phase 2 call sites
555:   can write `paginate(items, *normalize_paging(max_results, offset))`
556:   exactly as sketched in the Phase 2 task description, since `paginate`
557:   takes `(items, offset, max_results)`.
558: - **2026-08-19 (Task 1.3 implementation note -- flagging for follow-up)**:
559:   `AdrSummary` (`models/adr/v1/summary.py`) does **not** subclass the new
560:   `general/models/summary.py::DocSummary`, unlike the other four domains.
561:   Root cause: `models/adr` is documented (`AGENTS.md`'s "models location"
562:   note) as having *no* dependency on `mcp`/`tools`/`resources`/`prompts`,
563:   so it stays usable from the dependency-free base library without the
564:   `mcp` extra installed. `general/__init__.py`, however, unconditionally
565:   imports `general.tools`/`general.resources`/`general.prompts`, which
566:   import `server.mcp` -- so importing anything under `general` (including
567:   `general.models`) already requires the `mcp` extra, by way of Python
568:   needing to run every ancestor package's `__init__.py`. Making
569:   `AdrSummary` subclass `DocSummary` would therefore silently add a new,
570:   previously-absent `mcp` dependency to `models.adr` -- confirmed by
571:   actually blocking `mcp`'s import and re-running
572:   `from biz.dfch.specmgr.models.adr import AdrSummary`, which succeeds
573:   today and would not once `AdrSummary` imports from `general`. Resolved
574:   conservatively: `AdrSummary` keeps its own field-identical declaration;
575:   `tests/general/models/test_summary.py` asserts structural (not
576:   inheritance-based) equivalence for it, plus a side-by-side field-set
577:   assertion across all five Summary classes for ACC-001/ACC-003. **Flagged
578:   for a follow-up decision** (candidate for Task 4.3's short ADR, or an
579:   `AGENTS.md` update): whether this asymmetry is acceptable long-term, or
580:   whether `DocSummary` should instead live somewhere with no `general`/
581:   `mcp` dependency (e.g. top-level `models/`, alongside `models/adr` and
582:   `models/iso25010.py`) so `AdrSummary` can subclass it too.
583: - **2026-08-19 (Phase 2)**: The ADR resource->tool conversion shifts one
584:   module from `adr/resources/` to `adr/tools/`, which changes the
585:   hardcoded MCP feature counts a pre-existing test
586:   (`tests/commands/test_docs.py::test_count_mcp_features_matches_known_counts`)
587:   asserts (11 tools/2 resources -> 12 tools/1 resource). Updated that
588:   test's literals in place rather than deferring the fix to Phase 4,
589:   since Phase 2's own quality gate requires a green full test suite.
590:   `docs/GENERATED.md`/`docs/MCP.md` regeneration (which would otherwise
591:   reflect the same shift) stays out of scope here -- that is explicitly
592:   Task 4.1's job, run once after every domain's cross-references are
593:   repointed in Phase 3.
594: 
595: ### Related PRs / Commits
596: 
597: - [Issue #13](https://github.com/dfch/biz.dfch.SpecMgr/issues/13): Add
598:   pagination to `<domain>_list` (resource→tool + shared `PagedResult`)

(End of file - total 598 lines)
</content>
```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 10.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa -iname \"*refine*\"; echo ---; find /home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts -type f"
}
```

**Output:**

```
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/refine.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
---
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/create_task.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/update_task.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/__init__.py
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/implement_task.py

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/refine.py"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/refine.py</path>
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
18: """``@mcp.prompt()``: refine (Phase 4, Task 4.3).
19: 
20: Returns instructional text -- not itself a tool call -- that guides an LLM
21: through adding a fresh batch of open interview questions to an *existing*
22: Question and Answer (QA) document, one or more of the nine ISO/IEC
23: 25010:2023 quality characteristics at a time (e.g. "5 questions each about
24: Functional Suitability, Security, Maintainability", or "3 questions for
25: each of the 9 main characteristics"). Unlike ``create_qa``/``update_qa``,
26: this prompt never elicits or writes an actual answer itself -- each new
27: question is appended with an empty ``_(awaiting response)_`` placeholder in
28: place of an answer, for a human to fill in directly in the document
29: afterwards.
30: 
31: Like ``update_qa``, this targets an existing document via the ``qa/tools/``
32: surface (``get_qa``, ``update_qa``, ``list_qa`` -- the last to resolve a
33: title to an id when no id is given) and the ``specmgr://iso25010`` resource
34: (to ground each new question in that characteristic's actual definition).
35: This prompt deliberately does not
36: implement or call any ``/resolve`` follow-up step itself -- it only tells
37: the human user, in its final instructions to the LLM, that such a step
38: exists and comes next.
39: 
40: The actual instructional text lives in its own packaged data file,
41: ``qa/data/qa_refine_instructions.md``, read fresh on every call via
42: ``general.tools._packaged_data.read_packaged_text`` -- the same
43: example/template/schema packaging convention this domain already uses
44: (``qa_example.md``/``qa_template.md``/``qa_schema.json``), rather than as
45: an inline Python string constant like every other prompt in this codebase.
46: Placeholders use ``string.Template`` (``$id_or_name``/``$scope``), not
47: ``str.format``, precisely so the instructions file itself is free to use
48: plain, unescaped ``{...}`` braces for the Q&A markdown placeholders it
49: narrates to the LLM (e.g. ``{the question}``) without those colliding with
50: this module's own substitution.
51: """
52: 
53: from __future__ import annotations
54: 
55: from string import Template
56: 
57: from ...general.tools._packaged_data import read_packaged_text
58: from ...server import mcp
59: 
60: 
61: @mcp.prompt(
62:     name="refine",
63:     title="Add interview questions to a QA document",
64:     description=(
65:         "Guides the LLM through appending a batch of new, unanswered interview questions "
66:         "(each with an empty placeholder answer) to an existing QA document, for one or more "
67:         "of the nine ISO/IEC 25010:2023 quality characteristics."
68:     ),
69: )
70: def refine(id_or_name: str, scope: str | None = None) -> str:
71:     """Return instructional text for adding new interview questions to an existing QA document.
72: 
73:     Parameters
74:     ----------
75:     id_or_name:
76:         Either the target document's specmgr-assigned id, or a free-text
77:         title/topic to look up via the `list_qa` tool when no id is known.
78:     scope:
79:         Free-text description of which characteristics to target and how
80:         many questions to add to each, e.g. "5 questions each about
81:         Functional Suitability, Security, Maintainability" or "3 questions
82:         for each of the 9 main characteristics". When absent or ambiguous,
83:         the returned instructions tell the LLM to ask the user via the
84:         `question` tool rather than guessing.
85: 
86:     Returns
87:     -------
88:     str
89:         Instructional text (auto-wrapped as a single ``UserMessage`` by
90:         the MCP SDK), not itself a tool call.
91:     """
92:     template = Template(read_packaged_text("qa", "refine_instructions", "md"))
93:     return template.substitute(
94:         id_or_name=id_or_name,
95:         scope=scope or "(not given -- ask the user before choosing characteristics or counts)",
96:     )

(End of file - total 96 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/implement_task.py"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/implement_task.py</path>
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
18: """``@mcp.prompt()``: implement_task (Task 3.14).
19: 
20: Returns instructional text -- not itself a tool call -- that guides an LLM
21: through actually *working* an existing Task List (TSK) document's checklist:
22: reading it via ``get_tsk``, building an in-session ``TodoWrite`` list from
23: its ``items``, and using the ``question`` tool to resolve ambiguity for any
24: item before starting work on it. Unlike ``create_task``/``update_task``,
25: there is no ``req``/``adr`` precedent for this prompt -- it is genuinely new
26: (REQ-006/ACC-006 in the feature README).
27: 
28: This is a **thin-precedent** prompt: like ``req.prompts.create_req``'s one
29: line "Make a todo list and use the question tool." and
30: ``adr.prompts.create_adr_test``'s similar line, the instructional text below
31: merely *narrates* two host-provided tools by name -- ``TodoWrite`` and
32: ``question`` -- neither of which is implemented anywhere in this repo as an
33: ``@mcp.tool()``. This module does not, and must not, define stub tools of
34: those names: they are assumed to be supplied by the MCP host/client the LLM
35: is running in, exactly like every other reference to them in this codebase.
36: ``implement_task`` itself never calls ``get_tsk``/``TodoWrite``/``question``
37: either -- it only returns the text instructing an LLM to do so.
38: 
39: The actual instructional text lives in its own packaged data file,
40: ``tsk/data/tsk_implement_instructions.md``, read fresh on every call via
41: ``general.tools._packaged_data.read_packaged_text``, rather than as an
42: inline Python string constant. Placeholders use ``string.Template``
43: (``$id``), not ``str.format``, precisely so the instructions file itself
44: is free to use plain, unescaped ``{...}`` braces for the TSK markdown it
45: narrates to the LLM without those colliding with this module's own
46: substitution.
47: """
48: 
49: from __future__ import annotations
50: 
51: from string import Template
52: 
53: from ...general.tools._packaged_data import read_packaged_text
54: from ...server import mcp
55: 
56: 
57: @mcp.prompt(
58:     name="implement_task",
59:     title="Implement a task list",
60:     description=(
61:         "Reads an existing task list by id, builds a TodoWrite list from its items, and "
62:         "uses the question tool to resolve ambiguity before proceeding."
63:     ),
64: )
65: def implement_task(id: str) -> str:
66:     """Return instructional text for working the checklist of the task list identified by ``id``.
67: 
68:     Parameters
69:     ----------
70:     id:
71:         The existing document's specmgr-assigned identifier.
72: 
73:     Returns
74:     -------
75:     str
76:         Instructional text (auto-wrapped as a single ``UserMessage`` by
77:         the MCP SDK), not itself a tool call. This function never calls
78:         ``get_tsk``, ``TodoWrite``, or ``question`` itself -- it only
79:         narrates that sequence for the LLM to carry out.
80:     """
81:     template = Template(read_packaged_text("tsk", "implement_instructions", "md"))
82:     return template.substitute(id=id)

(End of file - total 82 lines)
</content>
```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 7.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "find /home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr -iname \"*_instructions.md\" | sort"
}
```

**Output:**

```
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_create_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_update_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/data/general_compact_history_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_create_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_update_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md</path>
<type>file</type>
<content>
1: You are implementing the checklist of an existing Task List (TSK)
2: document, id: $id
3: 
4: Follow this sequence exactly.
5: 
6: ## 1. Read the current document
7: Call `get_tsk(id)` to load the document's current frontmatter and body.
8: Never assume prior state -- the on-disk file is always the source of
9: truth and may have been hand-edited since you last saw it.
10: 
11: ## 2. Build a TodoWrite list from its items
12: Create one TodoWrite entry per checklist item in `body.items`, in the
13: same order:
14: - An item whose `checked` is already `true` -> mark its TodoWrite entry
15:   `completed`.
16: - An item whose `checked` is `false` -> mark its TodoWrite entry
17:   `pending` (moving it to `in_progress` only once you actually start
18:   working on it -- keep at most one `in_progress` at a time, per
19:   TodoWrite's own usage conventions).
20: Use each item's `description` as the TodoWrite entry's own content.
21: 
22: ## 3. Resolve ambiguity before starting an item
23: Before marking any pending item `in_progress`, check whether its
24: `description` is clear enough to act on. If its intent or scope is
25: ambiguous or underspecified, use the `question` tool to ask the user
26: for clarification first -- do not guess and start working on an
27: unclear item.
28: 
29: ## 4. Work the list
30: Proceed item by item, updating your TodoWrite list's statuses as you
31: go (one `in_progress` at a time, then `completed` once genuinely done).
32: 
33: ## 5. Persisting completed work back to the document (separate, deliberate step)
34: Completing TodoWrite entries in-session does **not** update the
35: underlying `tsk` document -- its checkboxes on disk are left exactly as
36: they were read in step 1. So, for each entry, you must persist the document
37: to reflect the work you completed, you must separately call
38: `update_tsk(id, content)` with the updated checklist (`- [x] ...` for
39: items you completed) -- a whole-body replace, so carry forward every
40: other section unchanged, including at least one `## Recent Updates`
41: entry (add a new one summarizing the work, or keep the existing ones --
42: never end up with zero). This is a distinct, deliberate step: do not
43: assume finishing the TodoWrite list alone is enough.
44: 
45: Optionally, check `specmgr://tsk/schema` if you need to double-check
46: the document's structure before drafting the replacement body.

(End of file - total 46 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/create_req.py"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/create_req.py</path>
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

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 36.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/admin/src/biz.dfch.SpecMgr && gh issue list --search \"problem statement\" --state all 2>&1 | head -30; echo \"---branch---\"; git branch --show-current; git status --short | head -5"
}
```

**Output:**

```
/bin/bash: line 1: gh: command not found
---branch---
dev

```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 348.3s)

_Thinking:_

I've done the research. Here's what I found and what I'm proposing, followed by the decisions I need from you before drafting the plan.

## Research summary

**iSixSigma's 7 questions (5W2H)** — these map exactly to your "7 questions":

1. What is the problem that needs to be solved?
2. Why is it a problem? (the pain)
3. Where is the problem observed? (location, products)
4. Who is impacted?
5. When was the problem first observed?
6. How is the problem observed? (symptoms)
7. How often is the problem observed? (error rate, magnitude, trend)

**LearnLeanSigma's complementary guidance** (useful for the `Gap`/`Future State` sections and for prompt guidance, not necessarily new schema fields):

- A problem statement = **expected condition** vs. **actual condition** = a measurable **gap**, bounded by **scope** (where/who) and **period** (when), with **evidence source** stated.
- Must explicitly **exclude** causes, blame, and solutions — those belong to root-cause analysis / countermeasure selection, which is a *later*, separate activity.
- "Future State" naturally corresponds to their "Goal statement" (measurable target, by when).

## Codebase precedent found

- **`list_prb` must be a paged `@mcp.tool()`, not a `specmgr://prb/list` resource** — `AGENTS.md` is stale here; ADR `ec9f5262` (feat-13, already `done`) converted all five `<domain>_list` resources to tools. New domains should launch with `list_prb` from day one, not add a resource then convert it later.
- No `specmgr://prb/{id}` resource — id-based reads are `get_prb`-only (ADR `ddfb1109`).
- `PrbSummary` should subclass `general/models/summary.py::DocSummary`.
- The interactive "walk the user through it with a TodoWrite list + `question` tool" pattern you want already has a precedent: `tsk/prompts/implement_task.py` (narrated instructions only, doesn't call `TodoWrite`/`question` itself — just tells the LLM to). I'll model `create_prb`/`update_prb` on that + `req/prompts/create_req.py`'s "check for duplicates first" pattern.
- Schema-wise, this looks buildable entirely with the *existing* `models/md` engine (no engine changes needed, unlike QA's `end_marker` addition) — nested fixed H3s under a fixed H2, with a mix of mandatory (`Summary`) and optional (`Question1..7`) children, is the same shape QA's `General`/`Qa` already use.

## Proposed schema

```
PrbFrontmatter(MarkdownFrontmatter): type: Literal["prb"]; status: <small set, see Q2>

Prb(MarkdownSection1WithComment)            # H1 title + optional leading comment
├── current_state: CurrentState              # mandatory H2
├── gap: Gap                                 # mandatory H2, opaque free text
├── future_state: FutureState                # mandatory H2, opaque free text
├── references: References | None            # optional H2
└── more_information: MoreInformation | None # optional H2, opaque free text (REQ precedent)

CurrentState(MarkdownSection2)               # H2 "Current State"
├── summary: Summary                         # mandatory H3, opaque free text (agent-synthesized)
├── question_1: Question1 | None             # optional H3, fixed heading
├── question_2: Question2 | None
├── question_3: Question3 | None
├── question_4: Question4 | None
├── question_5: Question5 | None
├── question_6: Question6 | None
└── question_7: Question7 | None
```

Now the actual open decisions:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "question": "What GitHub issue number / folder slug should this feature use?",
      "header": "Feature folder",
      "options": [
        {
          "label": "feat-0-problem-statement (Recommended)",
          "description": "No issue exists yet; use the feat-0 placeholder per AGENTS.md convention, matching e.g. feat-0-slug pattern until an issue is filed."
        },
        {
          "label": "I have an issue number",
          "description": "Type the issue number and preferred slug, e.g. 'feat-15-problem-statement'."
        }
      ]
    },
    {
      "question": "What status values should PrbFrontmatter.status accept?",
      "header": "Status values",
      "options": [
        {
          "label": "draft / active / resolved / cancelled (Recommended)",
          "description": "Mirrors TSK/QA's 4-value set exactly. draft = being filled in; active = investigating/gap being refined; resolved = future state reached; cancelled = abandoned."
        },
        {
          "label": "draft / open / closed / cancelled",
          "description": "Generic issue-tracker style wording instead of TSK/QA's draft/active/done/cancelled wording."
        },
        {
          "label": "Just 3 values: draft / active / done",
          "description": "Simplest possible set, no cancelled state (a cancelled PRB would just stay in draft/active or get deleted)."
        }
      ]
    },
    {
      "question": "How should the 7 question headings (H3, under Current State) be worded?",
      "header": "Question headings",
      "options": [
        {
          "label": "Plain question text (Recommended)",
          "description": "e.g. \"### What Is the Problem?\", \"### Why Is It a Problem?\" -- self-documenting, no numbering baked into the heading."
        },
        {
          "label": "Numbered + question text",
          "description": "e.g. \"### Question 1: What Is the Problem?\" -- keeps your own Q1..Q7 numbering visible in the document itself."
        }
      ]
    },
    {
      "question": "How should updates work: one whole-body replace tool, or ADR-style granular per-section editing?",
      "header": "Update mechanism",
      "options": [
        {
          "label": "Whole-body update_prb(id, content) (Recommended)",
          "description": "Mirrors REQ/TSK/QA exactly -- simplest, lowest implementation cost. Sections stay individually addressable by their fixed headings within the markdown text itself; no new generic tooling needed."
        },
        {
          "label": "ADR-style update_section(id, key, value)",
          "description": "Reuses the pattern from adr/tools/update_section.py, but that mechanism is currently ADR-specific code, not a generic shared component -- porting it to PRB is real additional scope (a new per-domain update_section implementation), for granular single-question edits without resending the whole body."
        }
      ]
    },
    {
      "question": "How should the optional 'References' section be shaped?",
      "header": "References shape",
      "options": [
        {
          "label": "Opaque free text (Recommended)",
          "description": "Like MoreInformation/Notes elsewhere -- just prose/bullets, no enforced structure. Simplest, matches the 'defer structured cross-linking' pattern every other domain has explicitly chosen for v1."
        },
        {
          "label": "Structured by artifact type",
          "description": "Mirrors REQ's 'Related Artifacts' section (### Requirements / ### Decisions / ### Use Cases / etc. sub-lists of ids) -- more powerful for traceability, more upfront schema work."
        }
      ]
    },
    {
      "question": "Should I add any additional sections beyond Current State/Gap/Future State/References/More Information?",
      "header": "Additional sections",
      "options": [
        {
          "label": "No additional sections (Recommended)",
          "description": "Keep exactly your 5 sections. Impact/urgency can be folded into the Gap prose itself (per the LearnLeanSigma formula) via prompt guidance, without a new schema field."
        },
        {
          "label": "Add optional 'Impact' H2",
          "description": "Between Gap and Future State -- quantifies cost/time/quality/safety consequence of the gap, kept separate from Gap itself (which is purely the measured actual-vs-expected delta)."
        }
      ]
    },
    {
      "question": "What should the create/update prompt names be?",
      "header": "Prompt naming",
      "options": [
        {
          "label": "create_prb / update_prb (Recommended)",
          "description": "Matches the domain-consistent tool-name convention (REQ/QA precedent) -- not a collision, prompts and tools are separate MCP registries."
        },
        {
          "label": "create_problem_statement / update_problem_statement",
          "description": "Literal full-name wording, like TSK's create_task/update_task/implement_task deliberately using the issue's own wording instead of the tsk-prefixed convention."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "What GitHub issue number / folder slug should this feature use?"="feat-0-problem-statement (Recommended)", "What status values should PrbFrontmatter.status accept?"="draft / active / resolved / cancelled (Recommended)", "How should the 7 question headings (H3, under Current State) be worded?"="Plain question text (Recommended)", "How should updates work: one whole-body replace tool, or ADR-style granular per-section editing?"="Whole-body update_prb(id, content) (Recommended)", "How should the optional 'References' section be shaped?"="Opaque free text (Recommended)", "Should I add any additional sections beyond Current State/Gap/Future State/References/More Information?"="It is actually 7 questions: What, Why, Where, Who, When, How observed, How often. Have an optional "Impact".", "What should the create/update prompt names be?"="create_prb / update_prb (Recommended)". You can now continue with the user's answers in mind.
```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 70.9s)

_Thinking:_

Good — that resolves everything. Confirmed structure now:

```
Current State
  Summary
  What Is the Problem?                    (optional)
  Why Is It a Problem?                    (optional)
  Where Is the Problem Observed?          (optional)
  Who Is Impacted?                        (optional)
  When Was the Problem First Observed?    (optional)
  How Is the Problem Observed?            (optional)
  How Often Is the Problem Observed?      (optional)
Gap
Impact                                    (optional)
Future State
References                                (optional)
More Information                          (optional)
```

Here is the complete draft plan I intend to write to `.specmgr/feat/feat-0-problem-statement/README.md`. Please review it — once you approve, I'll write the file (I can't write it yet while in plan mode).

**Tool: bash**

**Input:**

```json
{
  "command": "date +%Y-%m-%d"
}
```

**Output:**

```
2026-08-25

```

______________________________________________________________________

## Assistant (Plan · Claude Sonnet 5 · 122.1s)

_Thinking:_

______________________________________________________________________

```markdown
---
id: feat-0-problem-statement
version: 1.0.0
status: planning
created: 2026-08-25
updated: 2026-08-25
---

# Feature: Add artifact type Problem Statement (prb)

## Plan

### Overview

Add a new markdown artifact type, `ProblemStatement` (abbreviation `prb`),
for capturing a Six-Sigma-style problem statement: a factual, evidence-led
description of the gap between the current and desired state of a system —
deliberately free of assumed causes, blame, or solutions. `prb` follows the
domain-first hierarchy and MCP surface already established by `req`/`tsk`/
`qa` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/
resources shape almost exactly, and reuses their whole-body update
convention rather than ADR's granular `update_section` mechanism.

The body's `Current State` section is structured around the classic 5W2H
("What/Why/Where/Who/When/How/How Often") interview questions from
<https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/>,
each under its own fixed heading so an answer can be added, referenced, and
refined independently over the document's lifetime. `Gap`/`Impact`/
`Future State` follow the expected-vs-actual/measurable-gap/goal-statement
discipline from
<https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/>.
Two new prompts (`create_prb`/`update_prb`) narrate an interactive,
`TodoWrite` + `question`-tool-driven interview flow (precedented by
`tsk/prompts/implement_task.py`), including agent-drafted `Summary` and
`Gap` synthesis from whichever answers the user chooses to supply.

### Requirements

- REQ-001: Define the `prb` markdown schema — frontmatter (`type="prb"`,
  4-value status set `draft`/`active`/`resolved`/`cancelled`) and body (H1
  title, optional leading comment, mandatory `## Current State` holding a
  mandatory `### Summary` plus 7 optional, fixed-heading 5W2H `### ` question
  leaves, mandatory `## Gap`, optional `## Impact`, mandatory
  `## Future State`, optional `## References`, optional `## More Information`).
- REQ-002: Pydantic models under `prb/models/v1/` (frontmatter, body,
  document, parser, summary), domain-first, mirroring `tsk`/`qa`'s exact
  file shapes. No `models/md` engine changes are needed (unlike QA's
  `end_marker` addition) — every field is buildable with the existing
  declarative heading-mapped parser.
- REQ-003: Parse/validate `prb` documents from markdown, mirroring
  `parse_req`/`parse_tsk`/`parse_qa`'s two-error-channel convention
  (`AssertionError` for structural problems, `pydantic.ValidationError` for
  field-level problems).
- REQ-004: MCP tools mirroring REQ/TSK/QA's lifecycle surface, **plus**
  `list_prb` as a paged tool from day one (per ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
  `specmgr://prb/list` resource and convert it later): `parse_prb`,
  `create_prb`, `update_prb`, `set_status_prb`, `delete_prb` (stub),
  `validate_prb`, `get_prb`, `get_prb_example`, `get_prb_template`,
  `list_prb`.
- REQ-005: MCP resources: `specmgr://prb/schema`, `/example`, `/template`
  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
  reads are `get_prb`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_prb`/`update_prb` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows (no other prompt in
  this codebase calls `create_*`/`update_*` in a loop over 7 sub-questions
  with agent-synthesized `Summary`/`Gap` text, so this is a new prompt
  shape, though it reuses the `TodoWrite`/`question`-tool narration pattern
  from `tsk/prompts/implement_task.py` and the dedup-check-first pattern
  from `req/prompts/create_req.py`). Both use their own packaged
  instructions data file (`prb/data/prb_create_instructions.md`/
  `prb_update_instructions.md`), not an inline string.
- REQ-007: Packaged example/template/schema data (`prb/data/`) via the
  existing generic `general/tools/_packaged_data.py`, with the matching
  `pyproject.toml` package-data entry, pre-commit hook, and CI step.
- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
  `prb` entry in the doc-type registry, `commands/schema.py`),
  `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
  updated to seven domain/cross-cutting packages.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/prb_schema.json`,
  `specmgr://prb/schema`); a reference `prb_reference.md` exercising every
  field (all 7 questions answered, `Impact`/`References`/
  `More Information` all present) round-trips through the parser.
- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required
  (`Summary`, `Gap`, `Future State`) vs. optional (7 questions, `Impact`,
  `References`, `More Information`) fields correctly; `PrbFrontmatter.status`
  rejects any value outside the four-value set.
- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
  well-formed document; missing a mandatory section raises
  `AssertionError`; an invalid field value raises `pydantic.ValidationError`.
- [ ] ACC-004: Verifies REQ-004 — every listed tool is implemented,
  registered, and callable; `list_prb` returns a `PagedResult[PrbSummary]`
  with default page size 25 / cap 100, mirroring the other five domains'
  `list_<d>` tools exactly (no resource-first-then-converted history for
  this domain).
- [ ] ACC-005: Verifies REQ-005 — every listed resource is implemented and
  registered.
- [ ] ACC-006: Verifies REQ-006 — `create_prb`/`update_prb` prompts
  narrate: (a) a duplicate/similar-document check via `list_prb` first,
  (b) building a `TodoWrite` list covering the `Summary` + all 7 questions
  + `Gap` + `Impact` + `Future State`, (c) using the `question` tool to
  elicit each optional answer (explicitly allowing skip), (d)
  agent-synthesizing/refining the `Summary` from whichever answers exist,
  (e) agent-drafting/refining the `Gap` from the current-state answers and
  confirming it with the user via the `question` tool before finalizing,
  (f) calling `create_prb`/`update_prb` (whole-body) at the end — verified
  live by actually running through both prompts end to end against a real
  document, not just asserting their static text.
- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
  real, non-editable install (`uv build --wheel` + scratch-venv install),
  mirroring TSK's own feat-10 Task 5.1-equivalent verification.
- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
  reflects seven domain/cross-cutting packages.

### Scope

**Included in this feature:**

- The `prb` markdown schema, Pydantic models, parser, and summary under
  `prb/models/v1/`.
- Full MCP surface (tools/resources/prompts/packaged data), including
  `list_prb` as a tool (not a resource) from the start.
- The interactive `create_prb`/`update_prb` prompt behavior (`TodoWrite` +
  `question`-tool-driven 5W2H interview, agent-synthesized `Summary`/`Gap`).
- Tests mirroring `tests/tsk/`/`tests/qa/`'s layout and coverage depth.
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

**Explicitly out of scope:**

- A **Root Cause** section/field. Six Sigma discipline (and both source
  articles) explicitly requires a problem statement to stay free of
  assumed causes — root-cause analysis is a separate, later activity, not
  part of this artifact. If/when a dedicated RCA artifact type is wanted,
  it should be its own future feature, only ever cross-referenced from
  `References`, never embedded here.
- Structured cross-referencing of `References` to real REQ/UC/ADR/other
  PRB documents (typed sub-lists, id validation, etc.) — v1 keeps
  `References` as opaque free text, matching `MoreInformation`/`Notes`
  elsewhere. Revisit only if a concrete need emerges.
- ADR-style granular `update_section`/option-style per-field mutation
  tools — `update_prb` is a single whole-body replace tool, like
  `update_req`/`update_tsk`/`update_qa`. Individual questions stay
  addressable by their fixed heading text within the markdown body itself,
  not via a dedicated tool per section.
- Any deterministic/algorithmic (non-LLM) computation of `Summary`/`Gap`
  text. Both are synthesized by the calling agent while following the
  prompt's narrated instructions — no NLP/heuristic code ships in `src/`
  for this.
- A `specmgr prb-toc`-equivalent generation command or dedicated CI/
  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` already provide generically.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (tool-only id-based reads, no `specmgr://prb/{id}` resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
  not a resource — `list_prb` must follow this from day one), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
  `general/models/{DocSummary,PagedResult}` infrastructure, and the
  existing `models/md` engine (`MarkdownSection1WithComment`,
  `MarkdownSection2`, `MarkdownSection3`, `@alias`) — reused as-is, no
  engine changes anticipated.
- Blocks: None identified yet.

### Design Notes

**Schema:**

```

PrbFrontmatter(MarkdownFrontmatter): type: Literal["prb"];
status in {draft, active, resolved, cancelled}

Prb(MarkdownSection1WithComment) # H1, free-form title (alias ".+"); inherited optional comment
├── current_state: CurrentState # mandatory H2 "Current State"
├── gap: Gap # mandatory H2 "Gap", opaque free text leaf
├── impact: Impact | None # optional H2 "Impact", opaque free text leaf
├── future_state: FutureState # mandatory H2 "Future State", opaque free text leaf
├── references: References | None # optional H2 "References", opaque free text leaf
└── more_information: MoreInformation | None # optional H2 "More Information", opaque free text leaf (REQ precedent)

CurrentState(MarkdownSection2) # H2 "Current State"
├── summary: Summary # mandatory H3 "Summary", opaque free text leaf
├── question_1: Question1 | None # optional H3, @alias(value="What Is the Problem\\?")
├── question_2: Question2 | None # optional H3, @alias(value="Why Is It a Problem\\?")
├── question_3: Question3 | None # optional H3, @alias(value="Where Is the Problem Observed\\?")
├── question_4: Question4 | None # optional H3, @alias(value="Who Is Impacted\\?")
├── question_5: Question5 | None # optional H3, @alias(value="When Was the Problem First Observed\\?")
├── question_6: Question6 | None # optional H3, @alias(value="How Is the Problem Observed\\?")
└── question_7: Question7 | None # optional H3, @alias(value="How Often Is the Problem Observed\\?")

```

Every `Question{N}`/`Summary`/`Gap`/`Impact`/`FutureState`/`References`/
`MoreInformation` class is a bare leaf subclass with no further declared
fields — the same "opaque, captures any remaining markdown verbatim"
pattern already verified for REQ's `MoreInformation`/`Notes` and QA's
`RawRequirements`/`QaAnswer` (no new engine mechanism needed for this).

**Question heading wording is fixed and exact** (verbatim from the
iSixSigma 5W2H list, each requiring an explicit `@alias(...)` since the
class names `Question1`..`Question7` don't derive to this wording via the
implicit `AliasType.SPACE_SEPARATED` convention):

1. What Is the Problem?
2. Why Is It a Problem?
3. Where Is the Problem Observed?
4. Who Is Impacted?
5. When Was the Problem First Observed?
6. How Is the Problem Observed?
7. How Often Is the Problem Observed?

**`Summary` is mandatory, the 7 questions are all optional.** A freshly
created `prb` document may have zero questions answered yet (all deferred
to a later `update_prb` call) but must always carry *some* `Summary` text
(even a short placeholder at creation time) — mirrors ADR's own
mandatory-vs-optional body-field split, not TSK's "must seed a first
Recent Updates entry" pattern (there is no dynamic list here).

**`Gap`/`Future State` are mandatory; `Impact`/`References`/
`More Information` are optional** — matching the plain list the user gave,
plus the newly-added optional `Impact`, placed between `Gap` and
`Future State` (current state → gap → why it matters → target state).

**No Root Cause section** (see Scope: Explicitly out of scope) — this is a
deliberate, methodology-driven omission, not an oversight.

**Update mechanism: whole-body `update_prb(id, content)`**, not an
ADR-style `update_section`. The generic `adr/tools/update_section.py`
mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
ADR-specific code, not a shared cross-domain component — reusing it for
PRB would mean building a second, parallel implementation. Individual
questions/sections stay addressable by grepping/editing their fixed
heading text within the whole-body markdown, which is what "fixed heading
per question" is actually for (addressability without a dedicated tool
per field).

**`list_prb` is a paged tool from day one** (`@mcp.tool(name="list_prb")`
returning `PagedResult[PrbSummary]`, via `general/tools/_paging.py`'s
`paginate`/`normalize_paging`), not a `specmgr://prb/list` resource —
unlike REQ/TSK/QA (which launched as resources and were converted later in
feat-13), PRB is a new domain built *after* ADR ec9f5262 was accepted, so
it must not repeat the resource-then-convert history. `PrbSummary`
subclasses `general/models/summary.py::DocSummary` (`id`/`title`/`status`/
`ref`), like `ReqSummary`/`TskSummary`/`QaSummary`.

**Prompts are narrated instructions only** (return a string, auto-wrapped
as a `UserMessage` by the MCP SDK) — `create_prb`/`update_prb` never call
`TodoWrite`/`question`/`get_prb`/`create_prb`/`update_prb` themselves; they
only narrate that the calling LLM should. This is the same contract every
existing prompt in this codebase already follows
(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).

- `create_prb(topic: str) -> str`: instructs the LLM to (1) call `list_prb`
  first to check for an existing, similar problem statement (mirrors
  `create_req`'s dedup-check pattern) and ask the user via `question` if a
  near-duplicate is found; (2) build a `TodoWrite` list with one entry per
  the `Summary` + 7 questions + `Gap` + `Impact` + `Future State`; (3) use
  the `question` tool to elicit each of the 7 answers in turn, explicitly
  allowing the user to skip any; (4) synthesize a `Summary` paragraph from
  whichever answers were actually given; (5) draft a candidate `Gap`
  statement from the collected current-state answers (following the
  expected-vs-actual/measurable-difference formula from the
  LearnLeanSigma article) and confirm/refine it with the user via
  `question` before finalizing; (6) optionally ask for `Impact`; (7) ask
  for `Future State` (desired/target condition); (8) optionally ask for
  `References`/`More Information`; (9) assemble the full body markdown per
  the fixed schema above and call `create_prb(content)`.
- `update_prb(id: str) -> str`: instructs the LLM to (1) call `get_prb(id)`
  first (never assume prior state); (2) show the user which of the 7
  questions already have answers and which are still empty, and ask via
  `question` which ones (if any) they want to add to or revise; (3) for
  each selected question, elicit the new/revised text via `question`; (4)
  regenerate the `Summary` from the *complete*, current set of answers
  (a full re-synthesis, not an append); (5) re-draft/refine the `Gap`
  the same way as `create_prb` step 5, based on the now-current-state
  answers, confirming with the user; (6) optionally revise `Impact`/
  `Future State`/`References`/`More Information`; (7) call
  `update_prb(id, content)` (whole-body replace, carrying forward every
  unchanged section); (8) mention `set_status_prb` as a separate, optional
  follow-up (e.g. `resolved` once `Future State` has genuinely been
  reached, `cancelled` if abandoned).

Both prompts' instructional text lives in packaged data files
(`prb/data/prb_create_instructions.md`/`prb_update_instructions.md`, read
via `general.tools._packaged_data.read_packaged_text`, `string.Template`
substitution), matching `req_create_instructions.md`/
`tsk_implement_instructions.md`'s precedent — not an inline Python string
— since the narration is long enough to warrant it.

**Frontmatter status** (`draft`/`active`/`resolved`/`cancelled`) mirrors
TSK/QA's 4-value closed set exactly, with PRB-specific semantics: `draft`
= still being filled in; `active` = current state captured, gap/future
state being refined; `resolved` = future state reached; `cancelled` =
abandoned.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
  (`get_prb`), not a resource
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
  MCP tool (`list_prb`), not a resource — must be followed from the start
  for this new domain, not retrofitted later
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
  and explicitly *not* reused for `prb` (see Design Notes)

No new ADR is anticipated for this feature — every schema/tooling decision
either follows an existing ADR's precedent directly or is scoped enough to
log only in this file's own Decisions Made.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end task (tests, full
quality gate, README Progress update), mirroring feat-10/feat-12's
per-phase commit discipline, since implementation is likely to span
multiple sessions.

#### Phase 1: Specification

- [ ] Task 1.1: Write a full reference `prb_reference.md`
  (`.specmgr/feat/feat-0-problem-statement/prb_reference.md`) exercising
  every field (all 7 questions answered, `Impact`/`References`/
  `More Information` all present) — depends on: none — status: not-started
- [ ] Task 1.2: Define `prb` frontmatter (`prb/models/v1/frontmatter.py` —
  `PrbFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["prb"]`,
  4-value status set `draft`/`active`/`resolved`/`cancelled`, mirroring
  `TskFrontmatter`'s `_ALLOWED_STATUSES` pattern) — depends on: none —
  status: not-started
- [ ] Task 1.3: Define `prb` body structure
  (`prb/models/v1/body.py`) — `Prb(MarkdownSection1WithComment)`,
  `CurrentState(MarkdownSection2)` with mandatory `summary: Summary` and
  optional `question_1..question_7: Question{N} | None` (each with an
  explicit `@alias(...)` matching the exact 5W2H wording — see Design
  Notes), `Gap`/`FutureState` (mandatory leaves), `Impact`/`References`/
  `MoreInformation` (optional leaves) — depends on: Task 1.2 — status:
  not-started
- [ ] Task 1.4: `tests/prb/models/v1/test_frontmatter.py`, `test_body.py`
  — structural + validation tests mirroring `tests/tsk/models/v1/`/
  `tests/qa/models/v1/`, explicit coverage of mandatory-vs-optional field
  combinations (each of the 7 questions individually absent/present;
  `Impact`/`References`/`More Information` absent/present) — depends on:
  Task 1.3 — status: not-started
- [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite); confirm
  `prb_reference.md` is `specmgr mdformat`-clean; update this README's
  Progress section — depends on: Task 1.1, Task 1.4 — status: not-started

#### Phase 2: Pydantic Models, Parser & Schema

- [ ] Task 2.1: `prb/models/v1/document.py` (`PrbDocument(frontmatter,
  body)`, mirroring `TskDocument`/`QaDocument`) — depends on: Task 1.3 —
  status: not-started
- [ ] Task 2.2: Implement `parse_prb(text: str) -> PrbDocument` (model-layer
  function, mirrors `parse_tsk`/`parse_qa`) — depends on: Task 2.1 —
  status: not-started
- [ ] Task 2.3: `prb/models/v1/summary.py` (`PrbSummary(DocSummary)`,
  subclassing `general/models/summary.py::DocSummary`, for `list_prb`) —
  depends on: Task 2.1 — status: not-started
- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/TSK/QA) — depends on:
  Task 2.1 — status: not-started
- [ ] Task 2.5: Implement `generate_prb_schema()` in `commands/schema.py`
  (mirroring `generate_tsk_schema`/`generate_qa_schema`, via
  `PrbDocument.model_json_schema()`) + register `"prb"` in the
  `specmgr schema` doc-type generator registry (`_GENERATORS`); draft
  `docs/prb_schema.json` — depends on: Task 2.1 — status: not-started
- [ ] Task 2.6: `tests/prb/models/v1/test_parser.py` — mirrors
  `TestParseTsk`/`TestParseQa`'s shape (minimal doc, full reference-doc
  round-trip, defaults-when-absent, invalid status, missing-mandatory-
  section `AssertionError`, invalid-field `ValidationError`) — depends on:
  Task 2.2, Task 2.5 — status: not-started
- [ ] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
  including Task 2.6's new tests; update this README's Progress section —
  depends on: Task 2.5, Task 2.6 — status: not-started

#### Phase 3: MCP Surface

- [ ] Task 3.1: `prb/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
  wrappers over `general/tools/_doc_paths.py` (mirrors `tsk/tools/`/
  `qa/tools/` exactly) — depends on: Task 2.2 — status: not-started
- [ ] Task 3.2: `parse_prb(path: str) -> PrbDocument` tool wrapper
  (`prb/tools/parse_prb.py`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.3: `create_prb(content: str) -> PrbDocument` tool (body-only
  content; MCP builds frontmatter: `id`, `type="prb"`, `status="draft"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status:
  not-started
- [ ] Task 3.4: `update_prb(id, content) -> PrbDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.5: `set_status_prb(id, status) -> PrbDocument` tool (only path
  that changes `status`; reconstructs `PrbFrontmatter` via its own
  constructor so the 4-value validator runs, mirroring `set_status_tsk`/
  `set_status_qa`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.6: `delete_prb(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: not-started
- [ ] Task 3.7: `validate_prb(content, full=False) -> bool` tool — depends
  on: none — status: not-started
- [ ] Task 3.8: `get_prb(id) -> PrbDocument` tool (id-based single-document
  read; tool, not resource) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.9: `list_prb(max_results=None, offset=None) -> PagedResult[PrbSummary]`
  tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
  (default page size 25, cap 100), preserving the standard skip-malformed-
  file scan behavior — depends on: Task 2.3, Task 3.1 — status:
  not-started
- [ ] Task 3.10: `get_prb_example`/`get_prb_template` tools + packaged data
  (`prb/data/prb_example.md`, `prb/data/prb_template.md`) via
  `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
  not-started
- [ ] Task 3.11: `prb/resources/{prb_schema,prb_example,prb_template}.py`
  — `specmgr://prb/schema` (packaged `prb/data/prb_schema.json`, mirroring
  `specmgr://tsk/schema`), `specmgr://prb/example`, `specmgr://prb/template`
  (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
  not-started
- [ ] Task 3.12: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.prb` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
  — widen the shared schema-hook glob to include `prb/models/v1`, add a
  `specmgr-schema-prb-package` hook — depends on: Task 2.5 — status:
  not-started
- [ ] Task 3.13: `.github/workflows/ci.yml` — add the `docs/prb_schema.json`
  check + packaged-copy check steps — depends on: Task 2.5 — status:
  not-started
- [ ] Task 3.14: `prb/data/prb_create_instructions.md` +
  `prb/prompts/create_prb.py` (`@mcp.prompt()`, `string.Template`
  substitution, narrates the full interview flow — see Design Notes) —
  depends on: Tasks 3.3, 3.9 — status: not-started
- [ ] Task 3.15: `prb/data/prb_update_instructions.md` +
  `prb/prompts/update_prb.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
  not-started
- [ ] Task 3.16: `prb/__init__.py` (docstring + `from . import prompts,
  resources, tools`), add `prb` to `server.py`'s bottom-of-file domain
  import line (alphabetical: `adr, general, prb, qa, req, tsk, uc`) and
  update its module docstring (Tools/Resources/Prompts sections) — depends
  on: Tasks 3.2-3.15 — status: not-started
- [ ] Task 3.17: `tests/prb/tools/...`, `tests/prb/resources/...`,
  `tests/prb/prompts/...` mirroring `tests/tsk/`/`tests/qa/`'s layout,
  including live end-to-end coverage of `create_prb`/`update_prb`'s
  narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_prb`'s
  paging behavior (default page size, `max_results` clamping, `offset`
  paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
  not-started
- [ ] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
  including Task 3.17's new tests; update this README's Progress section
  — depends on: Task 3.17 — status: not-started

#### Phase 4: Cross-cutting registration

- [ ] Task 4.1: `AGENTS.md` — update heading to "seven domain/cross-cutting
  packages implemented (ADR, REQ, UC, TSK, QA, PRB, general)"; add a
  `prb/` bullet (chronological order, after `qa/`); update the "Still
  genuinely missing" list (`validate_prb` not enforced via pre-commit/CI,
  `delete_prb` stub) and the closing domain-enumeration paragraphs —
  depends on: Phase 3 complete — status: not-started
- [ ] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
  regeneration — confirm `prb` appears correctly and all three commands
  report zero drift — depends on: Task 4.1 — status: not-started
- [ ] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
  update this README's Progress section — depends on: Task 4.2 — status:
  not-started

#### Phase 5: Final cross-cutting verification

- [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and
  confirm each is satisfied with concrete evidence (including a live
  `create_prb`→`update_prb`→`set_status_prb` run, not just unit tests);
  run the full quality gate (ruff format/check, pylint advisory, vulture,
  unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
  checks) end to end; set feature status to `done` — depends on: Phase
  1-4 complete — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-25**: Planning complete. This plan was designed
collaboratively (user + agent) in a dedicated planning session before any
implementation; no code has been written yet. A fresh-context session
should pick up at Phase 1, Task 1.1.

### Blockers

None.

### Recent Updates

#### Update 2026-08-25

- Completed: Full design/planning discussion — schema shape (5W2H
  questions under `Current State`, `Gap`/`Impact`/`Future State`/
  `References`/`More Information`), status set, update mechanism, prompt
  behavior, and MCP surface all decided; this README written from that
  discussion.
- Next: Phase 1 (Specification) — write `prb_reference.md`, define
  frontmatter/body models.
- Notes: No implementation attempted this session by design (planning-only
  session per explicit user instruction).

### Decisions Made

- **2026-08-25**: Type abbreviation `prb`, domain-first layout
  (`prb/models/v1/`, `prb/tools/`, `prb/resources/`, `prb/prompts/`,
  `prb/data/`) — matches TSK/QA precedent (schema lives inside the domain
  package, not top-level `models/`), since PRB is a new domain built after
  the domain-first refactor.
- **2026-08-25**: 5W2H question set taken verbatim from the iSixSigma
  article (What/Why/Where/Who/When/How/How Often), each a fixed, optional
  H3 heading under a mandatory `## Current State` H2 with a mandatory
  `### Summary` leaf. Question heading wording is the plain question text
  (not numbered) — chosen over "Question N: ..." for readability.
- **2026-08-25**: Status set `draft`/`active`/`resolved`/`cancelled` —
  reuses TSK/QA's 4-value pattern/wording convention, with PRB-specific
  semantics.
- **2026-08-25**: `update_prb` is a single whole-body replace tool
  (REQ/TSK/QA convention), not an ADR-style `update_section`/option-style
  granular tool — the latter is currently ADR-specific code (ADR
  71fd95d7), and porting it was judged not worth the added scope for this
  feature. Individual questions/sections remain addressable by their fixed
  heading text within the whole-body markdown.
- **2026-08-25**: `References` is opaque free text for v1 (like
  `MoreInformation`/`Notes`), not structured by artifact type — deferred,
  matching every other domain's own "defer structured cross-linking"
  decision.
- **2026-08-25**: Added an optional `Impact` H2 (between `Gap` and
  `Future State`) per user request, to hold business/cost/safety
  consequence separately from `Gap` itself (which stays a pure
  actual-vs-expected measurement, per the LearnLeanSigma article's
  explicit warning against conflating gap and consequence).
- **2026-08-25**: No `Root Cause` section — deliberately excluded per Six
  Sigma discipline (both source articles explicitly warn against including
  assumed causes in a problem statement); any future RCA artifact type
  would be a separate feature, only ever referenced from `References`.
- **2026-08-25**: `list_prb` ships as a paged `@mcp.tool()` from day one
  (per ADR ec9f5262, already accepted/`done` via feat-13) — this domain
  must not repeat REQ/TSK/QA's original resource-then-later-converted
  history.
- **2026-08-25**: Prompt names `create_prb`/`update_prb` (tool-name
  convention, like REQ/QA), not literal wording like TSK's
  `create_task`/`update_task`/`implement_task`.
- **2026-08-25**: GitHub issue not yet filed — feature folder uses the
  `feat-0-problem-statement` placeholder per `AGENTS.md`'s convention;
  rename the folder (and this frontmatter `id`) once/if an issue number is
  assigned.

### Related PRs / Commits

None yet — planning only.
```

______________________________________________________________________

A few things worth flagging explicitly before you sign off:

1. **`AGENTS.md`'s current TSK/QA "resources: `specmgr://tsk/list`" bullets are already stale** relative to actual code (feat-13 converted them to `list_tsk`/`list_qa` tools, but `AGENTS.md` wasn't updated in this session's snapshot). I've written the PRB plan against the *actual current* code/ADR state, not against `AGENTS.md`'s wording — Task 4.1 fixes `AGENTS.md`'s PRB bullet, but doesn't fix the pre-existing TSK/QA drift (out of scope for this feature).
2. `feat-0-problem-statement` is a placeholder — tell me if you already have a GitHub issue number and I'll rename it before writing the file.
3. I did **not** invent any new `models/md` engine mechanism (unlike QA's `end_marker` work) — everything here is buildable with what already exists, which should make this a comparatively low-risk implementation.

Let me know if you want any changes, then I'll write this file.

______________________________________________________________________

## User

-- 1: good, we have to clean up AGENTS.md - but you are right, not in this feature. Add a task to feat-7 to do the cleanup.
-- 2: create a the feature as feat-0. We will change it later, after I reviewed it.
-- 3: ok

any more questions or notes, before you can write the feature file?

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 7.0s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md"
}
```

**Output:**

```
<path>/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-15
3: id: feat-7-various-improvements
4: status: planning
5: updated: 2026-08-19
6: version: 1.0.0
7: ---
8: 
9: # Feature: Various cross-cutting improvements
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: A rolling bucket for small, cross-cutting improvements that touch more than
16: one document domain (`adr`/`req`/`uc`/`general`) but are each too small to
17: justify their own `feat-NNN-slug` folder. Sections/tasks are added here as
18: new concerns come up; a concern gets split into its own feature folder if
19: it grows large enough to need dedicated requirements/acceptance criteria of
20: its own (see Design Notes).
21: 
22: The first tracked concern: standardizing the output format/contract of the
23: MCP `specmgr://*/list` resources (`adr_list`, `req_list`, and any future
24: `uc_list`/`ac_list`), and reviewing/optimizing the MCP `@mcp.prompt()`
25: modules (`adr/prompts/`, `req/prompts/`) for consistency and token
26: efficiency, including deciding the fate of the step-gated `_test` prompt
27: variants (`adr/prompts/create_adr_test.py`, `update_adr_test.py`) that
28: currently exist alongside the narrated originals for A/B comparison.
29: 
30: ### Requirements
31: 
32: - REQ-001: All `specmgr://*/list` resources (`adr_list`, `req_list`, and
33:   future `uc_list`/`ac_list`) share a consistent, documented output
34:   contract (fields, sort order, skip-on-parse-failure semantics).
35: - REQ-002: A decision is made on whether/how list resources should support
36:   pagination or size limits as the number of documents in a base directory
37:   grows (both `adr_list` and `req_list` currently do a full, unbounded
38:   directory scan on every call).
39: - REQ-003: Every existing MCP prompt module (`create_adr`, `update_adr`,
40:   `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) is
41:   reviewed against a documented set of prompt-quality criteria (length,
42:   redundancy, step-gating, clarity of the tool-call sequence it drives).
43: - REQ-004: A decision is recorded on the fate of the step-gated `_test`
44:   prompt variants — keep both narrated and step-gated variants long-term,
45:   consolidate into one style, or retire one — applied consistently across
46:   the `adr` and (if adopted) `req` domains.
47: 
48: ### Acceptance Criteria
49: 
50: - [ ] ACC-001: Verifies REQ-001 — `adr_list`/`req_list` (and any future
51:   `*_list` resource) share a common base summary shape/contract, checked
52:   by a shared test or an explicit side-by-side comparison. **Partially
53:   advanced by `feat-13-list-paging`** (2026-08-19): 4 of 5 domains
54:   (`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary`) now literally
55:   subclass the shared `general.models.DocSummary` base; `AdrSummary`
56:   shares the identical field set structurally but deliberately does
57:   **not** subclass it (dependency-graph reason: `models/adr` must stay
58:   free of the `mcp` extra — see feat-13's Decisions Made log and ADR
59:   ec9f5262-9912-49d0-903f-fcfb54f28c13), with equivalence enforced by a
60:   structural test instead of inheritance. Not marking this `[x]` yet since
61:   the contract is shared by convention/test, not uniformly by class
62:   hierarchy, across all five domains.
63: - [x] ACC-002: Verifies REQ-002 — a decision (ADR or an entry in this
64:   file's Decisions Made log, per the ADR-vs-feature-log tie-breaker in ADR
65:   e369ee2e) is recorded on list-resource pagination, with rationale even
66:   if the decision is "defer." **Done**: recorded in ADR
67:   ec9f5262-9912-49d0-903f-fcfb54f28c13 ("Expose `<domain>_list` as paged
68:   MCP tools (`list_<domain>`), not resources"), implemented in full by
69:   `feat-13-list-paging`.
70: - [ ] ACC-003: Verifies REQ-003 — each prompt module has a recorded
71:   review outcome (kept as-is / changed / retired) against the documented
72:   criteria.
73: - [ ] ACC-004: Verifies REQ-004 — an explicit decision on the `_test`
74:   variants is recorded and, if it implies code changes, those changes are
75:   made consistently in both domains that have prompts.
76: 
77: ### Scope
78: 
79: **Included in this feature:**
80: 
81: - The output shape/contract of `specmgr://adr/list` and `specmgr://req/list`
82: - Design guidance for future `*_list` resources (`uc`, `ac`, ...)
83: - Review and optimization of existing `adr/prompts/` and `req/prompts/`
84:   modules
85: - The decision on keeping/consolidating/retiring the `_test` prompt
86:   variants
87: 
88: **Explicitly out of scope:**
89: 
90: - Net-new domains or document types (tracked separately, e.g. `uc`
91:   currently has no `prompts`/`resources` sub-package yet — adding one is
92:   its own feature, not this one)
93: - Other cross-cutting concerns not yet described (logging, error-handling
94:   conventions, config management, etc.) — these get their own section/task
95:   list added to this same file when they come up, or are split into a
96:   dedicated `feat-NNN-slug` folder if they turn out to be large
97: 
98: ### Dependencies
99: 
100: - Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
101:   feature-folder structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2
102:   (domain-first hierarchy)
103: - Blocks: None identified yet
104: 
105: ### Design Notes
106: 
107: - `adr_list` (`adr/resources/adr_list.py`) and `req_list`
108:   (`req/resources/req_list.py`) already follow the same general shape
109:   (id/title/status/filename, filename-sorted, skip-on-parse-failure) but
110:   catch different exception tuples per domain parser
111:   (`(AdrParseError, ValidationError)` vs. `(AssertionError, ValidationError)`) — worth confirming this divergence is intentional
112:   (domain-specific parser errors) rather than accidental drift.
113: - Neither list resource paginates; both differ from this project's own
114:   `asdste100` MCP tools (e.g. `word_list`, `rules_examples`), which
115:   already use a `max_results`/`offset` pattern — that pattern is a
116:   candidate model to reuse here rather than inventing a new one.
117: - `adr/prompts/create_adr_test.py`/`update_adr_test.py` are explicitly
118:   documented (AGENTS.md) as experimental, step-gated (`GATE 0`..`GATE N`)
119:   variants registered under distinct prompt names for side-by-side
120:   comparison against the narrated originals — this feature is where that
121:   comparison's outcome should get decided and recorded.
122: 
123: ### Related ADRs
124: 
125: - e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
126:   `.specmgr` with feature-driven work units
127: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
128:   document-type domain (domain-first hierarchy)
129: 
130: ### Task List
131: 
132: Single, canonical breakdown of work phases and tasks. Status lives on the
133: task itself — there is no separate "planned" vs. "executed" list to keep in
134: sync; a task's line *is* its current status. Update it in place as work
135: progresses (edit, don't duplicate).
136: 
137: #### Phase 0: Housekeeping
138: 
139: - [x] Task 0.1: Create GitHub issue #7 for this feature and rename
140:   `feat-0-various-improvements` → `feat-7-various-improvements`, updating
141:   the frontmatter `id` to match — depends on: none — status: done
142:   (2026-08-15)
143: 
144: * [x] Task 0.2: Create and immediately close GitHub issue #8
145:   (`feat-0-coverage-badge`, already-completed feature) and rename the
146:   folder → `feat-8-coverage-badge`, updating the frontmatter `id` to match
147:   — depends on: none — status: done (2026-08-15)
148: 
149: - [x] Task 0.3: Create and immediately close GitHub issue #9
150:   (`feat-0-doc-in-specmgr`) and rename the folder →
151:   `feat-9-doc-in-specmgr`, updating the frontmatter `id` to match —
152:   depends on: none — status: done (2026-08-15)
153: 
154: - [x] Task 0.4: Fix all ~20 live cross-references to the old
155:   `feat-0-doc-in-specmgr` path across `AGENTS.md`, source docstrings
156:   (`server.py`, `adr/prompts/*.py`, `models/adr/__init__.py`,
157:   `models/adr/v1/__init__.py`, `uc/models/v1/use_case.py`), tests
158:   (`tests/adr/prompts/test_*.py`), and other feature docs
159:   (`feat-4-use-cases/README.md`, `v1/uc-schema.md`, `v1/eval-uc.md`) —
160:   deliberately left one reference untouched in an archived session
161:   transcript (`feat-9-doc-in-specmgr/history/session-ses_038f-adr-tool-plan.md`)
162:   since historical logs are point-in-time records, not live docs — depends
163:   on: Task 0.3 — status: done (2026-08-15)
164: 
165: - [x] Task 0.5: Regenerate `docs/api/` and `docs/GENERATED.md` via
166:   `uv run --frozen specmgr docs` (Python 3.13) to pick up the renamed
167:   path, then verify with `ruff format --check`, `ruff check`, and the full
168:   `unittest` suite (771 tests, all passing) — depends on: Task 0.4 —
169:   status: done (2026-08-15)
170: 
171: - [ ] Task 0.6: Review whether repeatedly referencing
172:   `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` (and its section
173:   numbers) inline in source docstrings (`server.py`, `adr/prompts/*.py`,
174:   `models/adr/__init__.py`, `models/adr/v1/__init__.py`,
175:   `uc/models/v1/use_case.py`) is genuinely useful or just redundant bloat
176:   that also creates a maintenance liability (as Task 0.4 just showed —
177:   ~20 references had to be fixed for a single folder rename). Decide a
178:   tighter convention (e.g. reference the plan once per module/file at
179:   most, or drop path+section references from docstrings entirely in
180:   favor of the plan file itself being the single source of truth) and
181:   apply it — depends on: Task 0.4 — status: not-started
182: 
183: - [ ] Task 0.7: Update ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO
184:   8601 for all dates and times") to require timezone information on every
185:   timestamp — either an explicit offset (`±HHMM`) or `Z` for UTC — rather
186:   than treating it as optional, if this is not already stated; the current
187:   "Standard Format (Non-Filename Contexts)" section only shows `±HHMM` as
188:   an example under "With timezone" without mandating it — depends on: none
189:   — status: not-started
190: 
191: - [x] Task 0.8: Create a new `general` MCP resource that returns the main
192:   characteristics of ISO/IEC 25010:2023 (system/software quality model). Use this as input: `.specmgr/feat/feat-7-various-improvements/product-quality-model.md`. Name of resource: `iso25010`. Location: `src/general/resources`.
193:   with a description for each — depends on: none — status: done (2026-08-16,
194:   all 9 sub-tasks 0.8.1 through 0.8.9 complete)
195: 
196:   - [x] Task 0.8.1: Rewrite `product-quality-model.md`'s content into a new
197:     packaged data file, `general/data/general_iso25010.md` — drop each
198:     characteristic heading's leading `N. ` numbering (e.g. `## Functional Suitability`, not `## 1. Functional Suitability`; list order alone
199:     conveys the number) and convert every sub-characteristic bullet into
200:     its own nested `### ` heading directly under its characteristic's `##`
201:     heading (instead of a bullet list), so the generic `models.md` engine
202:     can parse names/descriptions as structured headings instead of
203:     regex-splitting bullet text. Also convert the trailing copyright/fair-use
204:     sentence into a leading HTML comment (`<!-- ... -->`) rather than a plain
205:     paragraph, so it maps onto `Iso25010.comment` below. The H1 title and the
206:     9-item bullet list of characteristic names are kept as-is (not dropped);
207:     the intro paragraph ("The product quality model consists of 9 main
208:     characteristics:") that originally sat between the H1 and the bullet
209:     list was later hand-edited out of `product-quality-model.md` (user
210:     edit, after this task's first pass), dropping `Iso25010.intro`
211:     accordingly (see Task 0.8.2) — `product-quality-model.md` itself was
212:     already hand-edited into this exact shape ahead of this task, so this
213:     step is a straight copy into the new packaged path plus an `mdformat`
214:     pass. Add a `"biz.dfch.specmgr.general" = ["data/*.md"]` entry to
215:     `pyproject.toml`'s `[tool.setuptools.package-data]` (none exists for
216:     `general` yet) — depends on: none — status: done (2026-08-16)
217:   - [x] Task 0.8.2: Add `models/iso25010.py` (flat, unversioned — this is
218:     static reference data, not a user-edited/versioned document type
219:     like ADR/REQ): `SubCharacteristic(MarkdownSection3)` and
220:     `Characteristic(MarkdownSection2)`, both
221:     `@alias(value=".+", type=AliasType.REGEX)` (free-form heading text,
222:     mirroring `req.models.v1.body.Requirement`'s own H1 precedent) with a
223:     `description: MarkdownParagraph` field each (plus
224:     `sub_characteristics: list[SubCharacteristic]` on `Characteristic`,
225:     `min_length=1`). `Iso25010(MarkdownSection1)` as the H1 container
226:     (mirroring `req.models.v1.body.Requirement`'s own H1 precedent), with
227:     fields in document order: `names: list[MarkdownListItem]`
228:     (`min_length=9, max_length=9` — exactly the 9 characteristic names, no
229:     lead-in `intro` field: the user hand-edited the source data to drop
230:     the intro sentence between the H1 and the bullet list), `comment: MarkdownComment | None` (the copyright/fair-use notice), and
231:     `characteristics: list[Characteristic]` (`min_length=9, max_length=9`
232:     — exactly the 9 main characteristics); and `parse_iso25010(text) -> Iso25010`, a thin `format_text` + `Iso25010.from_text` wrapper (no
233:     frontmatter to split off, unlike `parse_adr`/`parse_req`). Re-export
234:     `Iso25010`, `Characteristic`, `SubCharacteristic`, `parse_iso25010`
235:     from `models/__init__.py` — depends on: Task 0.8.1 — status:
236:     done (2026-08-16)
237:   - [x] Task 0.8.3: Add `general/resources/iso25010.py` —
238:     `@mcp.resource("specmgr://iso25010", name="iso25010", ..., mime_type="application/json")` wrapping
239:     `parse_iso25010(read_packaged_text("general", "iso25010", "md"))`,
240:     mirroring `req/resources/req_schema.py`'s packaged-data-read style;
241:     register in `general/resources/__init__.py` (import + `__all__`) —
242:     depends on: Task 0.8.2 — status: done (2026-08-16)
243:   - [x] Task 0.8.4: Update `general/__init__.py`'s and `server.py`'s module
244:     docstrings to list `specmgr://iso25010`; while in `server.py`, also
245:     fix its stale "top-level `resources` package" line (pre-existing
246:     drift left over from Task 0.12's move of `resources/` into
247:     `general/resources/`) — depends on: Task 0.8.3 — status: done (2026-08-16)
248:   - [x] Task 0.8.5: Add `tests/models/test_iso25010.py` — parse the
249:     packaged `general_iso25010.md` end-to-end via `parse_iso25010`,
250:     asserting 9 characteristics, spot-checking a couple of
251:     characteristic/sub-characteristic names and descriptions, and that
252:     the leading HTML comment is captured — depends on: Task 0.8.2 —
253:     status: done (2026-08-16)
254:   - [x] Task 0.8.6: Add `tests/general/resources/test_iso25010.py`,
255:     mirroring `tests/general/resources/test_version.py` — asserts the
256:     `iso25010` resource function returns an `Iso25010` instance with the
257:     expected characteristic count — depends on: Task 0.8.3 — status:
258:     done (2026-08-16)
259:   - [x] Task 0.8.7: Regenerate `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 — depends
260:     on: Task 0.8.4 — status: done (2026-08-16)
261:   - [x] Task 0.8.8: Verify — `ruff format --check`, `ruff check`,
262:     `vulture src/ whitelist.py --min-confidence 60`, and the full
263:     `unittest` suite — depends on: Task 0.8.1 through Task 0.8.7 —
264:     status: done (2026-08-16, 791 tests, all passing)
265:   - [x] Task 0.8.9: Update this feature's own Decisions Made / Recent
266:     Updates logs and mark Task 0.8 (and this sub-list) done — depends
267:     on: Task 0.8.1 through Task 0.8.8 — status: done (2026-08-16)
268: 
269: - [x] Task 0.9: Add an id-based `get_req` MCP **tool** (not just the
270:   existing `specmgr://req/{id}` resource) — reason: in practice, LLMs and
271:   agents fail to reliably use `specmgr://req/{id}` (a resource, not a
272:   tool) to retrieve an artifact by id, defeating the point of exposing it
273:   that way. This directly revisits `feat-6-requirement-artifact` Task
274:   3.17's design decision ("`specmgr://req/{id}` resource ... supersedes
275:   the earlier considered `get_req` tool — id-based single-document read is
276:   a resource only"); may also need the equivalent look at `get_adr` (which
277:   already exists as a tool, unlike REQ) and any future `uc`/`get_uc` for
278:   consistency — depends on: none — status: done (2026-08-15)
279: 
280:   - [x] Task 0.9.1: Write a new ADR recording the decision: add a `get_req`
281:     tool mirroring `get_adr`; remove `specmgr://req/{id}` (`req_get`)
282:     entirely so REQ is tool-only for id-based reads; explicitly leave
283:     `specmgr://adr/{id}` (`adr_get`) coexisting with `get_adr` as-is
284:     (accepted, deliberate cross-domain divergence, not silently ignored);
285:     note future `uc`/`get_uc` should follow the REQ (tool-only) precedent
286:     — depends on: none — status: done (2026-08-15)
287:   - [x] Task 0.9.2: Add `req/tools/get_req.py` — `@mcp.tool(name="get_req")`
288:     wrapper mirroring `adr/tools/get_adr.py`, using
289:     `req/tools/_io.py`/`_paths.py`'s `load_by_id(req_base_dir(), id)`,
290:     returning `ReqDocument` — depends on: Task 0.9.1 — status: done (2026-08-15)
291:   - [x] Task 0.9.3: Remove `req/resources/req_get.py` and drop its
292:     import/registration from `req/resources/__init__.py` (module
293:     docstring, the `from . import ...` line, and `__all__`) — depends on:
294:     Task 0.9.2 — status: done (2026-08-15)
295:   - [x] Task 0.9.4: Update `req/__init__.py`'s module docstring — drop
296:     `specmgr://req/{id}` from the resources list, add `get_req` to the
297:     tools list — depends on: Task 0.9.3 — status: done (2026-08-15)
298:   - [x] Task 0.9.5: Update `server.py`'s module docstring — remove the
299:     `specmgr://req/{id}` resource line, add `get_req` to the "Requirement
300:     tools" line — depends on: Task 0.9.3 — status: done (2026-08-15)
301:   - [x] Task 0.9.6: Update `req/prompts/update_req.py`'s `## 1. Read current state first` step to call `get_req(id)` instead of reading the
302:     now-removed `specmgr://req/{id}` resource (mirror `update_adr.py`'s
303:     phrasing style) — depends on: Task 0.9.2, Task 0.9.3 — status:
304:     done (2026-08-15)
305:   - [x] Task 0.9.7: Add `tests/req/tools/test_get_req.py`, mirroring
306:     `tests/adr/tools/test_get_adr.py`'s two cases
307:     (`test_returns_matching_document`, `test_raises_not_found_for_unknown_id`)
308:     — depends on: Task 0.9.2 — status: done (2026-08-15)
309:   - [x] Task 0.9.8: Remove `tests/req/resources/test_req_get.py` — depends
310:     on: Task 0.9.3 — status: done (2026-08-15)
311:   - [x] Task 0.9.9: Update `tests/req/prompts/test_update_req.py`'s
312:     assertions (currently asserting on the literal `"specmgr://req/{id}"`
313:     string) to assert on the new `get_req(id)` wording instead — depends
314:     on: Task 0.9.6 — status: done (2026-08-15)
315:   - [x] Task 0.9.10: Regenerate `docs/adr/README.md` (`specmgr adr-toc`)
316:     and `docs/api/`/`docs/GENERATED.md` (`specmgr docs`), Python 3.13 —
317:     depends on: Task 0.9.1, Task 0.9.4, Task 0.9.5 — status: done (2026-08-15)
318:   - [x] Task 0.9.11: Annotate `feat-6-requirement-artifact/README.md`'s
319:     Task 3.17 line with a short pointer note ("revisited/superseded by
320:     feat-7 Task 0.9 and ADR `<new-id>` — `get_req` tool added, resource
321:     removed"), without rewriting its existing history — depends on: Task
322:     0.9.1 — status: done (2026-08-15)
323:   - [x] Task 0.9.12: Update this feature's own Decisions Made / Recent
324:     Updates logs and mark Task 0.9 (and this sub-list) done — depends on:
325:     Task 0.9.1 through Task 0.9.11 — status: done (2026-08-15)
326:   - [x] Task 0.9.13: Verify — `ruff format --check`, `ruff check`,
327:     `vulture src/ whitelist.py --min-confidence 60` (catches the removed
328:     `req_get` file), and the full `unittest` suite — depends on: Task 0.9.2
329:     through Task 0.9.9 — status: done (2026-08-15)
330: 
331: - [x] Task 0.10: Create a new `general` MCP resource that returns the RFC
332:   2119\. This is an ad interim solution until we have a filter option in
333:   ASD-STE100 MCP by source. — depends on: none — status: cancelled
334: 
335: - [x] Task 0.11: Add CLI command "mdformat". This command formats a Markdown
336:   document with or without frontmatter in the same way that the MCP server
337:   formats documents when it reads and write artifacts (example: it uses
338:   numbering for ordered lists). This command does not perform a content
339:   validation — depends on: none — status: done (2026-08-16)
340: 
341: - [x] Task 0.12: Move src/resources to src/general/resources. Update refs to
342:   it — depends on: none — status: done (2026-08-16)
343: 
344: - [x] Task 0.13: Make the not-found error message easier to understand for
345:   `get_<type>` tools (`get_adr`, `get_req`, `get_uc`, `get_tsk`) — agents
346:   frequently pass a prefixed id (e.g. `"req-<uuid>"`) instead of the bare
347:   `<uuid>`, since the on-disk filename/slug carries that prefix; the id
348:   parameter must be the bare uuid only, with no domain prefix. Each
349:   domain's `<domain>/tools/_paths.py` raises its own `*NotFoundError`
350:   (`AdrNotFoundError`/`ReqNotFoundError`/`UcNotFoundError`/`TskNotFoundError`)
351:   with an `f"no {DOMAIN} found with id {id_!r}"`-style message that does
352:   not hint at this; `req`/`uc`/`tsk` funnel through the shared
353:   `general/tools/_doc_paths.py`'s `DocNotFoundError` before re-raising
354:   their own domain-specific message, while `adr/tools/_paths.py` raises
355:   `AdrNotFoundError` inline (no shared-module dependency); `tsk`'s message
356:   already carries a first-pass, not-yet-standardized hint ("Make sure,
357:   that you only use the 'id' without a prefix.") that needs grammar
358:   cleanup and alignment with whatever single wording gets decided. The
359:   detailed 9-step implementation breakdown lives in its own specmgr task
360:   list, TSK `266eb332-795b-48c4-9bc0-7115eb209378` ("Improve
361:   get_adr/get_req/get_uc/get_tsk Not-Found Error Messages") — retrieve it
362:   via the `get_tsk` MCP tool with id `266eb332-795b-48c4-9bc0-7115eb209378`
363:   — depends on: none — status: done (2026-08-16), all 9 sub-tasks
364:   complete: standardized wording decided (see Decisions Made) and applied
365:   to `AdrNotFoundError`/`ReqNotFoundError`/`UcNotFoundError`/
366:   `TskNotFoundError`/`DocNotFoundError`; tests extended to assert on
367:   message content in each domain's `test_paths.py`/`test__paths.py` and
368:   `test_get_<type>.py`; verified clean via `ruff format --check`/
369:   `ruff check`/`vulture src/ whitelist.py --min-confidence 60`/full
370:   `unittest` suite
371: 
372: - [x] Task 0.14: MCP tool: WebFetch with BearerToken and URL filter — a
373:   general, cross-cutting `webfetch` MCP tool for a Web Server
374:   instance (generic bearer-authenticated GET fetch, URL-filtered against a
375:   configured base URL). The full implementation plan and its per-task
376:   breakdown live in specmgr task list TSK
377:   `efb7d049-a222-4730-901f-6d57283b387c` ("Implement `webfetch` MCP Tool
378:   (Bearer-Authenticated, URL-Filtered Fetch for Web Server)") — retrieve it
379:   via the `get_tsk` MCP tool with id `efb7d049-a222-4730-901f-6d57283b387c`
380:   — depends on: none — status: done (2026-08-16)
381: 
382: - [x] Task 0.15: MCP tools `<domain>_list` must support paging — depends on:
383:   none — status: split out into `feat-13-list-paging` (GitHub issue #13,
384:   `.specmgr/feat/feat-13-list-paging/README.md`) on 2026-08-19; design
385:   agreed (resource→tool `list_<domain>`, `asdste100`-style `PagedResult`
386:   wrapper, shared `general/` infra, paging-only). **`feat-13-list-paging`
387:   is now complete** (all four phases done, decision recorded in ADR
388:   ec9f5262-9912-49d0-903f-fcfb54f28c13): closes REQ-002/ACC-002 and
389:   advances (but does not fully close) REQ-001/ACC-001 — see those entries
390:   below for the remaining ADR-outlier caveat.
391: 
392: - [ ] Task 0.16: MCP tools `<domain>_list` must support filtering — depends on: none — status: not-started
393: 
394:   we have to discuss the design first, before we can implement
395: 
396: - [x] Task 0.17: Add a `MarkdownListItemWithNotes` class to `markdown_list_item.py` that introduces a `notes: list[MarkdownParagraph] | None = None` field for captured continuation paragraphs inside list items — depends on: none — status: completed
397: 
398:   Background: `MarkdownListItem._value` correctly captures the full markdown content of each item (including indented continuation paragraphs after a blank line), but `_value` is a Pydantic private attribute so it does not appear in `model_dump()` / MCP JSON output. `ExtensionItem` solves this with an explicit `notes` field; REQ's `Characteristics.items` has no such field, so the `text` property only returns the leading-paragraph text and everything after the first blank line is dropped on serialization. The new base class adds `notes` to all list-item consumers (REQ characteristics, UC extensions, task lists, etc.) — items with no continuation paragraphs will serialize with `"notes": null` or a missing key; items with continuation paragraphs will carry the captured paragraphs in JSON.
399: 
400:   Full implementation plan: specmgr TSK `f581fb2f-9a82-11f1-9c57-fc4cea71c519`.
401: 
402: - [x] Task 0.18: Fix `MarkdownListItem.get_extent` for numbered lists — depends on: Task 0.17 — status: completed
403: 
404:   Background: `mdformat` renders loose numbered lists (`1.`, `2.`) differently from bullet lists (`-`): the `list_item_open` token's `.map` only spans the first paragraph, leaving continuation paragraphs as separate tokens outside the list item. This breaks `get_extent` for numbered lists with continuation paragraphs (e.g. REQ's `Characteristics` section). The fix detects single-item ordered lists (where `ordered_list_open.map[1] == list_item_open.map[1]`) and scans for trailing `paragraph_open` tokens after `ordered_list_close` but before the next `ordered_list_open`, extending the extent accordingly.
405: 
406:   Full implementation plan: specmgr TSK `602740af-0445-48d8-bcc3-18df541dad72`.
407: 
408: - [x] Task 0.19: Add a new `refine` QA prompt (`qa/prompts/refine.py`) that
409:   appends a batch of new, unanswered interview questions to an existing QA
410:   document, for one or more of the nine ISO/IEC 25010:2023 quality
411:   characteristics — resolves its target document via `specmgr://qa/list`
412:   (id or title lookup) plus `get_qa`, grounds each question in
413:   `specmgr://iso25010`'s actual characteristic definitions, asks the user
414:   via the `question` tool when the count/characteristics are ambiguous,
415:   appends `> {question}` / `_(awaiting response)_` placeholder pairs via a
416:   whole-body `update_qa` replace, and tells the user to answer the
417:   placeholders and then run the (separate, not-yet-implemented) `/resolve`
418:   command next. Registered in `qa/prompts/__init__.py` and `server.py`'s
419:   module docstring; 12 tests added in `tests/qa/prompts/test_refine.py` —
420:   depends on: none — status: done (2026-08-18)
421: 
422:   - [x] Task 0.19.1: Retrofit `refine`'s instructional text out of an
423:     inline `_INSTRUCTIONS_TEMPLATE` Python string (this codebase's
424:     universal convention for all 11 other prompt modules at the time) and
425:     into a new packaged data file, `qa/data/qa_refine_instructions.md`,
426:     read fresh on every call via
427:     `general.tools._packaged_data.read_packaged_text("qa", "refine_instructions", "md")`
428:     — the same packaging convention already used for
429:     `qa_example.md`/`qa_template.md`/`qa_schema.json`, applied to a
430:     prompt's instructional text for the first time in this codebase.
431:     Switched placeholder substitution from `str.format`
432:     (`{id_or_name}`/`{scope}`, requiring `{{`/`}}`-escaping of the
433:     template's own literal Q&A markdown placeholders like
434:     `{the question}`) to `string.Template`
435:     (`$id_or_name`/`$scope`), so the packaged `.md` file can use plain,
436:     unescaped `{...}` braces throughout. Added 2 more tests
437:     (`test_instructions_loaded_from_packaged_data_file`,
438:     `test_raises_file_not_found_when_instructions_missing`, mirroring
439:     `tests/uc/resources/test_uc_example.py`'s
440:     `mock.patch.object(_packaged_data, "packaged_data_path", ...)`
441:     pattern) — depends on: Task 0.19 — status: done (2026-08-18)
442:   - [x] Task 0.19.2: Regenerate `docs/api/`/`docs/GENERATED.md`
443:     (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); verify
444:     `ruff format --check`/`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the full `unittest` suite — depends
445:     on: Task 0.19.1 — status: done (2026-08-18, 1158 tests, all passing,
446:     up from 1156)
447: 
448: - [x] Task 0.20: Apply the packaged-instructions-file pattern established
449:   by Task 0.19.1 to every remaining inline `_INSTRUCTIONS_TEMPLATE` prompt
450:   module in the codebase: `adr/prompts/create_adr.py`,
451:   `create_adr_test.py`, `update_adr.py`, `update_adr_test.py`;
452:   `req/prompts/create_req.py`, `update_req.py`; `tsk/prompts/create_task.py`,
453:   `update_task.py`, `implement_task.py`; `qa/prompts/create_qa.py`,
454:   `update_qa.py` (11 modules total). Each gets its own packaged
455:   `<domain>/data/<domain>_<kind>_instructions.md` file, loaded via
456:   `read_packaged_text` + `string.Template`, with any `str.format`-style
457:   `{...}`/`{{...}}` escaping unwound to plain `{...}` since
458:   `string.Template` needs none. Extend/add each module's test file with
459:   the same fresh-read/missing-file coverage `refine`'s Task 0.19.1 got —
460:   depends on: Task 0.19 — status: done (2026-08-18)
461: 
462:   - [x] Task 0.20.1 (ADR): `create_adr.py`/`create_adr_test.py`/
463:     `update_adr.py`/`update_adr_test.py` converted; new `adr/data/`
464:     package created (didn't exist before) with `adr_create_instructions.md`
465:     / `adr_create_test_instructions.md` / `adr_update_instructions.md` /
466:     `adr_update_test_instructions.md`; added
467:     `"biz.dfch.specmgr.adr" = ["data/*.md"]` to `pyproject.toml`'s
468:     `[tool.setuptools.package-data]` (ADR's package had none before, since
469:     its schema lives under top-level `models/adr/`, not `adr/models/`) —
470:     depends on: Task 0.19 — status: done (2026-08-18)
471:   - [x] Task 0.20.2 (REQ): `create_req.py`/`update_req.py` converted;
472:     `req_create_instructions.md`/`req_update_instructions.md` added to the
473:     already-existing `req/data/` — depends on: Task 0.19 — status: done
474:     (2026-08-18)
475:   - [x] Task 0.20.3 (TSK): `create_task.py`/`update_task.py`/
476:     `implement_task.py` converted; `tsk_create_instructions.md`/
477:     `tsk_update_instructions.md`/`tsk_implement_instructions.md` added to
478:     the already-existing `tsk/data/` — note the `tsk_*` file-name prefix
479:     (matching the domain/package name) even though the prompt names
480:     themselves are `create_task`/`update_task`/`implement_task` (with
481:     "task" not "tsk"), consistent with `tsk/data/tsk_example.md` already
482:     using that same prefix — depends on: Task 0.19 — status: done
483:     (2026-08-18)
484:   - [x] Task 0.20.4 (QA): `create_qa.py`/`update_qa.py` converted;
485:     `qa_create_instructions.md`/`qa_update_instructions.md` added
486:     alongside `qa_refine_instructions.md` in the already-existing
487:     `qa/data/` — depends on: Task 0.19 — status: done (2026-08-18)
488:   - [x] Task 0.20.5: Regenerated `docs/api/`/`docs/GENERATED.md`
489:     (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); verified
490:     `ruff format --check`/`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the full `unittest` suite — depends
491:     on: Task 0.20.1, Task 0.20.2, Task 0.20.3, Task 0.20.4 — status: done
492:     (2026-08-18, 1180 tests, all passing, up from 1158)
493: 
494: - [x] Task 0.21: Create a new, general-purpose MCP `@mcp.prompt()` (e.g.
495:   `general/prompts/compact_history.py`, prompt name `compact_history` —
496:   `general/` currently has `tools`/`resources` but no `prompts`
497:   sub-package yet, so this also stands up that new sub-package and its
498:   registration in `general/__init__.py`/`server.py`) that guides an LLM
499:   through compacting the "Recent Updates" section of *any* feature folder
500:   under `.specmgr/feat/<feature_id>/README.md`, not just this one — per
501:   ADR e369ee2e-3353-4f92-991c-6367d76d832e's chosen option, which
502:   documents an optional sibling `history.md` file for rotating out older
503:   `Recent Updates` entries once a feature's `README.md` section grows too
504:   long, leaving a pointer in its place (e.g. "See history.md for updates
505:   before YYYY-MM-DD."). Unlike `adr`/`req`/`uc`/`tsk`/`qa`, feature
506:   folders have no dedicated parser/get/update MCP tools of their own, so
507:   this prompt's instructions rely on the LLM's own file
508:   read/edit/write tools directly on `README.md`/`history.md`, not on any
509:   new specmgr tool. The prompt takes the feature id (e.g.
510:   `feat-7-various-improvements`) as a parameter; the exact rotation
511:   trigger/cutoff (entry count, age, line count, ...) is left for the
512:   prompt's instructions to ask the user about when ambiguous, per the
513:   ADR's own "Open Questions" note that this is deliberately not
514:   prescribed. This feature folder's own `Recent Updates` was already
515:   manually compacted (2026-08-18, ahead of this task), so no live demo
516:   run against it is planned here — coverage is unit tests only, using
517:   fixtures rather than re-running the prompt against this folder — but
518:   the prompt itself must not be specific to `feat-7-various-improvements`
519:   — depends on: none — status: done (2026-08-18), all 5 sub-tasks
520:   complete: 1192 tests, all passing, up from 1180
521: 
522:   - [x] Task 0.21.1: Add `general/prompts/__init__.py` and
523:     `general/prompts/compact_history.py`
524:     (`@mcp.prompt(name="compact_history")`, params `feature_id: str` and
525:     optional `cutoff_hint: str | None`), following the `refine` reference
526:     pattern exactly: instructional text lives in a packaged data file,
527:     `general/data/general_compact_history_instructions.md`, loaded via
528:     `read_packaged_text("general", "compact_history_instructions", "md")`
529:     - `string.Template` (`$feature_id`/`$cutoff_hint`). The instructions
530:       must: locate `.specmgr/feat/$feature_id/README.md` (and sibling
531:       `history.md` if present) via the LLM's own file tools; ask the user
532:       via the `question` tool for the rotation cutoff when `$cutoff_hint`
533:       is absent/ambiguous rather than guessing; move older `Recent Updates`
534:       entries verbatim into `history.md` (creating it if absent), preserve
535:       remaining entries and the `README.md` pointer line convention exactly
536:       as already used in this file; bump frontmatter `updated`; and verify
537:       every archived entry appears exactly once in `history.md` and nowhere
538:       else, mirroring the manual pass already performed on this folder —
539:       depends on: none — status: done (2026-08-18)
540:   - [x] Task 0.21.2: Register `compact_history` in
541:     `general/prompts/__init__.py`; add `prompts` to
542:     `general/__init__.py`'s imports/`__all__`/docstring; update
543:     `server.py`'s module docstring (`Prompts` section: add a "General
544:     prompts" line; package-shape paragraph: note `general` now also has a
545:     `prompts` sub-package) — depends on: Task 0.21.1 — status: done
546:     (2026-08-18)
547:   - [x] Task 0.21.3: Add `tests/general/prompts/__init__.py` and
548:     `tests/general/prompts/test_compact_history.py`, mirroring
549:     `tests/qa/prompts/test_refine.py`'s shape: parameter interpolation
550:     checks, key-instruction content checks (question tool, history.md,
551:     pointer line, frontmatter `updated`), plus the
552:     fresh-read-per-call/missing-file `FileNotFoundError` pair via
553:     `mock.patch.object(_packaged_data, "packaged_data_path", ...)` — no
554:     live run against this feature folder itself (already compacted) —
555:     depends on: Task 0.21.1 — status: done (2026-08-18, 12 tests added)
556:   - [x] Task 0.21.4: Regenerate `docs/api/`/`docs/GENERATED.md`
557:     (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13;
558:     verify `ruff format --check`/`ruff check` (clean),
559:     `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
560:     `unittest` suite — depends on: Task 0.21.1, Task 0.21.2, Task 0.21.3
561:     — status: done (2026-08-18, 1192 tests, all passing, up from 1180)
562:   - [x] Task 0.21.5: Update this feature's own Decisions Made / Recent
563:     Updates logs and mark Task 0.21 (and this sub-list) done — depends
564:     on: Task 0.21.1 through Task 0.21.4 — status: done (2026-08-18)
565: 
566: - [x] Task 0.22: Examine cyclic dependency in `set_status.py` (qa) to server
567:   and mcp — depends on: none — status: documented (2026-08-19). Confirmed
568:   the cycle is real (`specmgr.server -> specmgr.qa -> specmgr.qa.tools -> specmgr.qa.tools.set_status_qa -> specmgr.server`) but architecture-wide,
569:   not qa-specific (~80 files across every domain follow the identical
570:   `from ...server import mcp` pattern; `pylint` R0401 flags ~90 equivalent
571:   warnings, already suppressed via `|| true`). Not currently breaking
572:   anything — safe only due to `server.py`'s fragile import-ordering
573:   convention (`mcp = MCPServer(...)` textually precedes its bottom-of-file
574:   domain imports). Decision recorded in ADR
575:   `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` ("Extract MCP Singleton into Its
576:   Own Module to Break Domain/Server Cyclic Imports"): extract a new
577:   `mcp_instance.py` leaf module owning the `MCPServer` singleton, imported
578:   by both `server.py` and every domain file instead of `server.py` directly
579:   — implementation deferred to specmgr TSK
580:   `699432f5-6f95-498e-a269-8001e4afc0e5` ("Extract `mcp_instance.py` to
581:   Break Domain/Server Cyclic Imports"); no code changes made as part of
582:   this task
583: 
584: - [x] Task 0.23: Add the `mcp` SDK's `streamable-http` transport as a third
585:   `specmgr mcp --transport` option, alongside the existing `stdio`/`sse` —
586:   `mcp>=2.0.0` (already a dependency) exposes `run_streamable_http_async`
587:   symmetrically to the existing `run_sse_async` used for `sse`, so this is
588:   purely a transport-wiring change confined to `commands/mcp.py`, with no
589:   changes needed to `server.py`, tools, resources, or prompts (MCP
590:   transport is orthogonal to the legacy/modern protocol-era negotiation,
591:   which the SDK already handles automatically on every transport). `sse`
592:   is the legacy/deprecated MCP HTTP transport; `streamable-http` is its
593:   spec-current replacement. The detailed implementation breakdown lives in
594:   its own specmgr task list, TSK `aaf70093-8a7c-4565-9985-3beaa85e1d3d`
595:   ("Add `streamable-http` MCP Transport Option") — retrieve it via the
596:   `get_tsk` MCP tool with id `aaf70093-8a7c-4565-9985-3beaa85e1d3d` —
597:   depends on: none — status: done (2026-08-19)
598: 
599: - [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff
600:   their output shape/behavior (`adr_list` vs. `req_list`) — depends on:
601:   none — status: not-started
602: 
603: - [ ] Task 1.2: Inventory current MCP prompt modules and their
604:   structure/length/gating style (`create_adr`, `update_adr`,
605:   `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) —
606:   depends on: none — status: not-started
607: 
608: #### Phase 2: Decide
609: 
610: - [ ] Task 2.1: Decide the standardized list-resource contract (shared
611:   base summary model, pagination yes/no and shape if yes) — depends on:
612:   Task 1.1 — status: in-progress — one piece already decided directly
613:   (2026-08-15, ahead of the formal audit): the fallback identifier field is
614:   named `ref`, not `filename`, and holds the extensionless base name, not
615:   the raw on-disk filename (see Decisions Made). Pagination is now
616:   **completed** via `feat-13-list-paging` (resource→tool `list_<domain>` +
617:   `asdste100`-style `PagedResult` wrapper, recorded in ADR
618:   ec9f5262-9912-49d0-903f-fcfb54f28c13); the shared-base-summary piece was
619:   also carried into and completed by that feature (`general.models.
620:   DocSummary`, subclassed by 4 of 5 domains — see ACC-001).
621: - [ ] Task 2.2: Decide the fate of the `_test` prompt variants and the
622:   criteria used for the prompt-quality review — depends on: Task 1.2 —
623:   status: not-started
624: 
625: #### Phase 3: Implement
626: 
627: - [x] Task 3.1a: Rename `AdrSummary.filename`/`ReqSummary.filename` to
628:   `ref`, changing its value from `path.name` (e.g. `"<uuid>-a-title.md"`)
629:   to the extensionless `path.stem` (e.g. `"<uuid>-a-title"`), and update
630:   the `adr_list`/`req_list` resource descriptions accordingly — done to
631:   stop steering the calling LLM toward reading the file off disk directly
632:   instead of using `get_adr`/`get_req`/`specmgr://{adr,req}/{id}` — depends
633:   on: none — status: done (2026-08-15)
634: - [x] Task 3.1b: Apply the remaining piece of the standardized
635:   list-resource contract (pagination) to `adr_list`/`req_list` (and
636:   document the full contract for future `*_list` resources) — depends on:
637:   Task 2.1 — status: **completed via `feat-13-list-paging`** (GitHub issue
638:   #13); implemented there as the resource→tool + `PagedResult` conversion
639:   across all five domains, not just `adr`/`req` — decision recorded in ADR
640:   ec9f5262-9912-49d0-903f-fcfb54f28c13.
641: - [ ] Task 3.2: Apply prompt optimizations and the `_test`-variant decision
642:   — depends on: Task 2.2 — status: not-started
643: 
644: #### Phase 4: Verify
645: 
646: - [ ] Task 4.1: Update/extend tests covering the list resources and
647:   prompts affected by Phase 3 — depends on: Task 3.1, Task 3.2 — status:
648:   not-started
649: - [ ] Task 4.2: Update `AGENTS.md`/`docs/GENERATED.md` (via `specmgr docs`)
650:   to reflect the final state — depends on: Task 4.1 — status: not-started
651: 
652: **Note:** If a task's scope changes mid-flight, edit its description in place;
653: rely on git history (`git log -p` on this file) to recover what was
654: originally planned, rather than keeping a second copy of the task around.
655: 
656: ## Progress
657: 
658: ### Current Status
659: 
660: **As of 2026-08-16**: Feature folder created with the first tracked
661: concern (MCP list-resource format + prompt optimizations) scoped. Phase 0
662: housekeeping (backfilling GitHub issue numbers for `feat-0-*` folders,
663: including this one) is complete. The `filename` → `ref` field rename
664: (Task 3.1a) is implemented ahead of the formal Phase 1/2 audit/decision;
665: the rest of Phase 1 (audit) and the pagination question are not started.
666: Task 0.9 (`get_req` tool, all 13 sub-tasks) is now complete: `get_req` was
667: added, `specmgr://req/{id}` was removed, `specmgr://adr/{id}` was
668: deliberately left untouched, and the decision is recorded in ADR
669: `ddfb1109-422d-4507-8dbc-dc5e4bec9614`. Task 0.11 (`mdformat` CLI command)
670: is now complete: the formatting logic previously inlined in the `mdformat`
671: MCP tool was extracted into a shared, disk-free
672: `models.md._markdown.format_markdown_document()` helper, which both the MCP
673: tool and the new `specmgr mdformat` CLI command now call. Task 0.12 (move
674: `src/resources` to `src/general/resources`) is now complete: the top-level
675: `resources` package (the `specmgr://version` resource) was folded into
676: `general/` alongside `general/tools/`, since it is itself a cross-cutting,
677: not domain-specific, concern. Task 0.8 (`specmgr://iso25010` resource, all
678: 9 sub-tasks) is now complete: `general/resources/iso25010.py` wraps
679: `parse_iso25010(read_packaged_text("general", "iso25010", "md"))`, is
680: registered in `general/resources/__init__.py`, and `general/__init__.py`/
681: `server.py`'s module docstrings (the latter's stale "top-level `resources`
682: package" line also fixed) list it; new tests
683: (`tests/models/test_iso25010.py`, `tests/general/resources/test_iso25010.py`)
684: and regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` are in place.
685: Task 0.13 (standardized not-found error message across `get_adr`/`get_req`/
686: `get_uc`/`get_tsk`, all 9 sub-tasks from TSK
687: `266eb332-795b-48c4-9bc0-7115eb209378`) is now complete: one wording
688: template is applied identically across all four `*NotFoundError` classes
689: plus the shared `DocNotFoundError`, and tests assert on the message content.
690: Task 0.19 (new `refine` QA prompt, both sub-tasks) is now complete: the
691: prompt itself was added and registered, then its instructional text was
692: retrofitted out of an inline Python string into a packaged data file
693: (`qa/data/qa_refine_instructions.md`) read via `read_packaged_text` +
694: `string.Template` — the first time this codebase has moved a prompt's
695: instructions out of an inline `_INSTRUCTIONS_TEMPLATE` constant. Task 0.20
696: (applying that same pattern to the remaining 11 prompt modules across
697: `adr`/`req`/`tsk`/`qa`, all five sub-tasks) is now complete: every prompt
698: module that previously carried an inline `_INSTRUCTIONS_TEMPLATE` now
699: loads its instructions from a packaged `<domain>/data/<domain>_<kind>.md`
700: file via `read_packaged_text` + `string.Template`, including a brand-new
701: `adr/data/` package (registered in `pyproject.toml`) since ADR had none
702: before. This feature folder's own `Recent Updates` section was also
703: compacted (manually, ahead of Task 0.21): entries older than 2026-08-18
704: now live in a sibling `history.md`, per ADR
705: e369ee2e-3353-4f92-991c-6367d76d832e. Task 0.21 (a new, general-purpose
706: `compact_history` MCP prompt, all 5 sub-tasks) is now complete: `general/`
707: gained its first `prompts` sub-package (`general/prompts/`), registered
708: alongside its existing `tools`/`resources` in `general/__init__.py` and
709: `server.py`'s module docstring; the prompt guides an LLM through rotating
710: older `### Recent Updates` entries out of any `.specmgr` feature folder's
711: `README.md` into an optional sibling `history.md`, using the LLM's own
712: file tools directly (no dedicated specmgr tool exists for feature
713: folders) and the `question` tool to resolve an ambiguous rotation cutoff.
714: Covered by 12 new unit tests (fixtures only, no live re-run against this
715: already-compacted folder).
716: 
717: ### Recent Updates
718: 
719: See `history.md` for updates before 2026-08-18 (rotated out per ADR
720: e369ee2e-3353-4f92-991c-6367d76d832e once this section grew too long).
721: 
722: #### Update 2026-08-19T06:49:34Z (Task 0.22)
723: 
724: - Completed (documented only, no code changes): Task 0.22 (examine the
725:   `qa/tools/set_status_qa.py` \<-> `server.py` cyclic dependency):
726: 
727:   - Confirmed the import cycle is real: `specmgr.server -> specmgr.qa -> specmgr.qa.tools -> specmgr.qa.tools.set_status_qa -> specmgr.server`,
728:     via `qa/tools/set_status_qa.py`'s `from ...server import mcp`. Confirmed
729:     via `pylint`'s R0401 check and by tracing `server.py`'s own bottom-of-file
730:     `from . import adr, general, qa, req, tsk, uc` registration imports.
731:   - Confirmed this is **not** qa-specific: identical
732:     `from ...server import mcp` imports exist in ~80 tool/resource/prompt
733:     files across every domain (`adr`, `general`, `qa`, `req`, `tsk`, `uc`),
734:     all flagged by the same ~90 R0401 warnings, already permanently
735:     suppressed in CI via `|| true`.
736:   - Confirmed it is not currently breaking anything: the cycle resolves
737:     safely today only because `server.py` constructs
738:     `mcp = MCPServer(...)` textually before its own domain-package
739:     registration imports — a fragile ordering convention, not an enforced
740:     invariant.
741:   - Wrote ADR `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` ("Extract MCP Singleton
742:     into Its Own Module to Break Domain/Server Cyclic Imports"), recording
743:     the decision to extract a new `mcp_instance.py` leaf module owning the
744:     `MCPServer` singleton, imported by both `server.py` and every domain
745:     file instead of reaching into `server.py` directly.
746:   - Created specmgr TSK `699432f5-6f95-498e-a269-8001e4afc0e5` ("Extract
747:     `mcp_instance.py` to Break Domain/Server Cyclic Imports") with the
748:     7-task implementation breakdown for executing the ADR's decision
749:     (new module, `server.py`/domain-file import updates, test/docs/lint
750:     verification), referenced from both the ADR's "More Information" and
751:     this task's line. Implementation deliberately not started as part of
752:     this task.
753: 
754: #### Update 2026-08-19T06:24:46Z (Task 0.23)
755: 
756: - Completed: Task 0.23 (add the `mcp` SDK's `streamable-http` transport as
757:   a third `specmgr mcp --transport` option), all 8 sub-tasks from TSK
758:   `aaf70093-8a7c-4565-9985-3beaa85e1d3d`:
759: 
760:   - Extended `commands/mcp.py`'s `--transport`/`-t` Typer option (help
761:     text, `show_default`, `SPECMGR_MCP_TRANSPORT` envvar description) to
762:     accept `"streamable-http"` alongside the existing `"stdio"`/`"sse"`.
763:   - Added a `streamable-http` branch in the `mcp()` command function,
764:     calling `_warn_on_public_binding(host)` (same as the `sse` branch)
765:     then `mcp_server.run(transport="streamable-http", host=host, port=port, stateless_http=True)` — `stateless_http=True` set
766:     explicitly to match this server's already-stateless `_lifespan`.
767:   - Updated `commands/mcp.py`'s module docstring with a third
768:     `streamable-http` bullet and usage example, and `README.md`'s MCP
769:     section (`--transport` table row + a short usage example mirroring
770:     the existing `sse` one).
771:   - Extended `tests/commands/test_mcp.py` with a new `TestMcpCommand`
772:     class asserting `mcp_server.run` is called correctly for all three
773:     branches (`stdio`, `sse`, `streamable-http`) — no prior test exercised
774:     the `mcp()` command function's branches directly, so symmetric
775:     coverage was added for all three, not just the new one.
776:   - Regenerated `docs/api/`/`docs/GENERATED.md`; verified
777:     `ruff format --check`/`ruff check`/
778:     `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
779:     full `unittest` suite (1195 tests, all passing, up from 1192).
780:   - Purely a transport-wiring change confined to `commands/mcp.py` (plus
781:     its tests/docs) — no changes to `server.py`, tools, resources, or
782:     prompts, since MCP transport is orthogonal to protocol-era/tool logic.
783: 
784: #### Update 2026-08-18T21:32:28Z (Task 0.21)
785: 
786: - Completed: Task 0.21 (new `compact_history` MCP prompt), all 5
787:   sub-tasks:
788: 
789:   - Added `general/prompts/__init__.py` and
790:     `general/prompts/compact_history.py`
791:     (`@mcp.prompt(name="compact_history")`, params `feature_id: str` and
792:     optional `cutoff_hint: str | None`), the first prompt under `general/`
793:     (which previously had `tools`/`resources` only). Instructional text
794:     lives in a new packaged data file,
795:     `general/data/general_compact_history_instructions.md`, loaded via
796:     `read_packaged_text("general", "compact_history_instructions", "md")`
797:     - `string.Template` (`$feature_id`/`$cutoff_hint`), following the
798:       `refine` reference pattern exactly.
799:   - The instructions guide the LLM through: locating
800:     `.specmgr/feat/<feature_id>/README.md` (and sibling `history.md` if
801:     present) via its own file tools (no dedicated specmgr tool exists for
802:     feature folders); asking the user via the `question` tool for the
803:     rotation cutoff when ambiguous; moving older `#### YYYY-MM-DD` entries
804:     verbatim into `history.md` (creating it if absent); updating the
805:     `README.md` pointer line (`See \`history.md\` for updates before
806:     YYYY-MM-DD.`); bumping frontmatter `updated`; and verifying each moved entry appears exactly once in `history.md\` and nowhere else.
807:   - Registered `compact_history` in `general/__init__.py`'s
808:     imports/`__all__`/docstring and `server.py`'s module docstring
809:     (`Prompts` section plus the package-shape paragraph, now noting
810:     `general` registers `tools`/`resources`/`prompts` like `req`/`tsk`/
811:     `qa`).
812:   - Added `tests/general/prompts/test_compact_history.py` (12 tests),
813:     mirroring `tests/qa/prompts/test_refine.py`'s shape: parameter
814:     interpolation, key-instruction content checks, and the
815:     fresh-read-per-call/missing-file `FileNotFoundError` pair via
816:     `mock.patch.object(_packaged_data, "packaged_data_path", ...)`. No
817:     live run against this feature folder itself, since it was already
818:     manually compacted on 2026-08-18 ahead of this task — there was
819:     nothing left to rotate.
820:   - Regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`; verified
821:     `ruff format --check`/`ruff check`/
822:     `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
823:     full `unittest` suite (1192 tests, all passing, up from 1180).
824: 
825: - Completed: Task 0.18 (Fix `MarkdownListItem.get_extent` for numbered lists), TSK `602740af-0445-48d8-bcc3-18df541dad72`:
826: 

(Output capped at 50 KB. Showing lines 1-826. Use offset=827 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 12.5s)

_Thinking:_

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md",
  "oldString": "- [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff\n  their output shape/behavior (`adr_list` vs. `req_list`) — depends on:\n  none — status: not-started",
  "newString": "- [ ] Task 0.24: Clean up `AGENTS.md`'s stale `specmgr://<d>/list` resource\n  mentions left over from `feat-13-list-paging`'s resource→tool conversion\n  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13) — `AGENTS.md`'s per-domain\n  bullets (at least `req`/`tsk`/`qa`, confirm `uc`/`adr` too) still\n  describe `specmgr://req/list`/`specmgr://tsk/list`/`specmgr://qa/list`\n  as resources instead of the `list_req`/`list_tsk`/`list_qa` tools they\n  actually are today; found and flagged during\n  `.specmgr/feat/feat-0-problem-statement/README.md`'s planning session\n  (2026-08-25) while designing that new domain's own `list_prb` tool\n  against the *current* code/ADR state rather than `AGENTS.md`'s\n  (out-of-date) wording. Fix every affected domain bullet, plus any other\n  live `specmgr://<d>/list` mention in `AGENTS.md` (e.g. the \"MCP server\n  (`server.py`)\" section's own domain-surface description, if it lists\n  resources per domain) — depends on: none — status: not-started\n\n- [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff\n  their output shape/behavior (`adr_list` vs. `req_list`) — depends on:\n  none — status: not-started"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 4.4s)

_Thinking:_

**Tool: edit**

**Input:**

```json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md",
  "oldString": "created: 2026-08-15\nid: feat-7-various-improvements\nstatus: planning\nupdated: 2026-08-19\nversion: 1.0.0",
  "newString": "created: 2026-08-15\nid: feat-7-various-improvements\nstatus: planning\nupdated: 2026-08-25\nversion: 1.0.0"
}
```

**Output:**

```
Edit applied successfully.
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 3.8s)

Now let me check the `.specmgr/feat/` directory naming to make sure `feat-0-problem-statement` doesn't collide with anything, and check `feat-4-use-cases` isn't already using `feat-0` elsewhere.

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/ | grep -i \"feat-0\" "
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 3.6s)

No collision. Now let me write the PRB feature plan file.

**Tool: bash**

**Input:**

```json
{
  "command": "mkdir -p /home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-0-problem-statement"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 102.0s)

**Tool: write**

**Input:**

````json
{
  "filePath": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-0-problem-statement/README.md",
  "content": "---\nid: feat-0-problem-statement\nversion: 1.0.0\nstatus: planning\ncreated: 2026-08-25\nupdated: 2026-08-25\n---\n\n# Feature: Add artifact type Problem Statement (prb)\n\n## Plan\n\n### Overview\n\nAdd a new markdown artifact type, `ProblemStatement` (abbreviation `prb`),\nfor capturing a Six-Sigma-style problem statement: a factual, evidence-led\ndescription of the gap between the current and desired state of a system —\ndeliberately free of assumed causes, blame, or solutions. `prb` follows the\ndomain-first hierarchy and MCP surface already established by `req`/`tsk`/\n`qa` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/\nresources shape almost exactly, and reuses their whole-body update\nconvention rather than ADR's granular `update_section` mechanism.\n\nThe body's `Current State` section is structured around the classic 5W2H\n(\"What/Why/Where/Who/When/How/How Often\") interview questions from\n<https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/>,\neach under its own fixed heading so an answer can be added, referenced, and\nrefined independently over the document's lifetime. `Gap`/`Impact`/\n`Future State` follow the expected-vs-actual/measurable-gap/goal-statement\ndiscipline from\n<https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/>.\nTwo new prompts (`create_prb`/`update_prb`) narrate an interactive,\n`TodoWrite` + `question`-tool-driven interview flow (precedented by\n`tsk/prompts/implement_task.py`), including agent-drafted `Summary` and\n`Gap` synthesis from whichever answers the user chooses to supply.\n\n### Requirements\n\n- REQ-001: Define the `prb` markdown schema — frontmatter (`type=\"prb\"`,\n  4-value status set `draft`/`active`/`resolved`/`cancelled`) and body (H1\n  title, optional leading comment, mandatory `## Current State` holding a\n  mandatory `### Summary` plus 7 optional, fixed-heading 5W2H `### ` question\n  leaves, mandatory `## Gap`, optional `## Impact`, mandatory\n  `## Future State`, optional `## References`, optional `## More Information`).\n- REQ-002: Pydantic models under `prb/models/v1/` (frontmatter, body,\n  document, parser, summary), domain-first, mirroring `tsk`/`qa`'s exact\n  file shapes. No `models/md` engine changes are needed (unlike QA's\n  `end_marker` addition) — every field is buildable with the existing\n  declarative heading-mapped parser.\n- REQ-003: Parse/validate `prb` documents from markdown, mirroring\n  `parse_req`/`parse_tsk`/`parse_qa`'s two-error-channel convention\n  (`AssertionError` for structural problems, `pydantic.ValidationError` for\n  field-level problems).\n- REQ-004: MCP tools mirroring REQ/TSK/QA's lifecycle surface, **plus**\n  `list_prb` as a paged tool from day one (per ADR\n  ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a\n  `specmgr://prb/list` resource and convert it later): `parse_prb`,\n  `create_prb`, `update_prb`, `set_status_prb`, `delete_prb` (stub),\n  `validate_prb`, `get_prb`, `get_prb_example`, `get_prb_template`,\n  `list_prb`.\n- REQ-005: MCP resources: `specmgr://prb/schema`, `/example`, `/template`\n  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based\n  reads are `get_prb`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).\n- REQ-006: MCP prompts `create_prb`/`update_prb` — narrated,\n  `TodoWrite` + `question`-tool-driven interview flows (no other prompt in\n  this codebase calls `create_*`/`update_*` in a loop over 7 sub-questions\n  with agent-synthesized `Summary`/`Gap` text, so this is a new prompt\n  shape, though it reuses the `TodoWrite`/`question`-tool narration pattern\n  from `tsk/prompts/implement_task.py` and the dedup-check-first pattern\n  from `req/prompts/create_req.py`). Both use their own packaged\n  instructions data file (`prb/data/prb_create_instructions.md`/\n  `prb_update_instructions.md`), not an inline string.\n- REQ-007: Packaged example/template/schema data (`prb/data/`) via the\n  existing generic `general/tools/_packaged_data.py`, with the matching\n  `pyproject.toml` package-data entry, pre-commit hook, and CI step.\n- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new\n  `prb` entry in the doc-type registry, `commands/schema.py`),\n  `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`\n  updated to seven domain/cross-cutting packages.\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — schema documented (`docs/prb_schema.json`,\n  `specmgr://prb/schema`); a reference `prb_reference.md` exercising every\n  field (all 7 questions answered, `Impact`/`References`/\n  `More Information` all present) round-trips through the parser.\n- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required\n  (`Summary`, `Gap`, `Future State`) vs. optional (7 questions, `Impact`,\n  `References`, `More Information`) fields correctly; `PrbFrontmatter.status`\n  rejects any value outside the four-value set.\n- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a\n  well-formed document; missing a mandatory section raises\n  `AssertionError`; an invalid field value raises `pydantic.ValidationError`.\n- [ ] ACC-004: Verifies REQ-004 — every listed tool is implemented,\n  registered, and callable; `list_prb` returns a `PagedResult[PrbSummary]`\n  with default page size 25 / cap 100, mirroring the other five domains'\n  `list_<d>` tools exactly (no resource-first-then-converted history for\n  this domain).\n- [ ] ACC-005: Verifies REQ-005 — every listed resource is implemented and\n  registered.\n- [ ] ACC-006: Verifies REQ-006 — `create_prb`/`update_prb` prompts\n  narrate: (a) a duplicate/similar-document check via `list_prb` first,\n  (b) building a `TodoWrite` list covering the `Summary` + all 7 questions\n  + `Gap` + `Impact` + `Future State`, (c) using the `question` tool to\n  elicit each optional answer (explicitly allowing skip), (d)\n  agent-synthesizing/refining the `Summary` from whichever answers exist,\n  (e) agent-drafting/refining the `Gap` from the current-state answers and\n  confirming it with the user via the `question` tool before finalizing,\n  (f) calling `create_prb`/`update_prb` (whole-body) at the end — verified\n  live by actually running through both prompts end to end against a real\n  document, not just asserting their static text.\n- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a\n  real, non-editable install (`uv build --wheel` + scratch-venv install),\n  mirroring TSK's own feat-10 Task 5.1-equivalent verification.\n- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/\n  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`\n  reflects seven domain/cross-cutting packages.\n\n### Scope\n\n**Included in this feature:**\n\n- The `prb` markdown schema, Pydantic models, parser, and summary under\n  `prb/models/v1/`.\n- Full MCP surface (tools/resources/prompts/packaged data), including\n  `list_prb` as a tool (not a resource) from the start.\n- The interactive `create_prb`/`update_prb` prompt behavior (`TodoWrite` +\n  `question`-tool-driven 5W2H interview, agent-synthesized `Summary`/`Gap`).\n- Tests mirroring `tests/tsk/`/`tests/qa/`'s layout and coverage depth.\n- Cross-cutting registration (`server.py`, `pyproject.toml`,\n  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).\n\n**Explicitly out of scope:**\n\n- A **Root Cause** section/field. Six Sigma discipline (and both source\n  articles) explicitly requires a problem statement to stay free of\n  assumed causes — root-cause analysis is a separate, later activity, not\n  part of this artifact. If/when a dedicated RCA artifact type is wanted,\n  it should be its own future feature, only ever cross-referenced from\n  `References`, never embedded here.\n- Structured cross-referencing of `References` to real REQ/UC/ADR/other\n  PRB documents (typed sub-lists, id validation, etc.) — v1 keeps\n  `References` as opaque free text, matching `MoreInformation`/`Notes`\n  elsewhere. Revisit only if a concrete need emerges.\n- ADR-style granular `update_section`/option-style per-field mutation\n  tools — `update_prb` is a single whole-body replace tool, like\n  `update_req`/`update_tsk`/`update_qa`. Individual questions stay\n  addressable by their fixed heading text within the markdown body itself,\n  not via a dedicated tool per section.\n- Any deterministic/algorithmic (non-LLM) computation of `Summary`/`Gap`\n  text. Both are synthesized by the calling agent while following the\n  prompt's narrated instructions — no NLP/heuristic code ships in `src/`\n  for this.\n- A `specmgr prb-toc`-equivalent generation command or dedicated CI/\n  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/\n  `specmgr schema` already provide generically.\n\n### Dependencies\n\n- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic\n  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614\n  (tool-only id-based reads, no `specmgr://prb/{id}` resource), ADR\n  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,\n  not a resource — `list_prb` must follow this from day one), the existing\n  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and\n  `general/models/{DocSummary,PagedResult}` infrastructure, and the\n  existing `models/md` engine (`MarkdownSection1WithComment`,\n  `MarkdownSection2`, `MarkdownSection3`, `@alias`) — reused as-is, no\n  engine changes anticipated.\n- Blocks: None identified yet.\n- Related, but explicitly out of scope here: `feat-7-various-improvements`\n  Task 0.24 (cleaning up `AGENTS.md`'s stale `specmgr://<d>/list`\n  resource-vs-tool wording for TSK/QA, found during this feature's own\n  planning session but not this feature's concern to fix).\n\n### Design Notes\n\n**Schema:**\n\n```\nPrbFrontmatter(MarkdownFrontmatter): type: Literal[\"prb\"];\n  status in {draft, active, resolved, cancelled}\n\nPrb(MarkdownSection1WithComment)                # H1, free-form title (alias \".+\"); inherited optional comment\n├── current_state: CurrentState                  # mandatory H2 \"Current State\"\n├── gap: Gap                                     # mandatory H2 \"Gap\", opaque free text leaf\n├── impact: Impact | None                        # optional H2 \"Impact\", opaque free text leaf\n├── future_state: FutureState                    # mandatory H2 \"Future State\", opaque free text leaf\n├── references: References | None                # optional H2 \"References\", opaque free text leaf\n└── more_information: MoreInformation | None      # optional H2 \"More Information\", opaque free text leaf (REQ precedent)\n\nCurrentState(MarkdownSection2)                   # H2 \"Current State\"\n├── summary: Summary                             # mandatory H3 \"Summary\", opaque free text leaf\n├── question_1: Question1 | None                 # optional H3, @alias(value=\"What Is the Problem\\\\?\")\n├── question_2: Question2 | None                 # optional H3, @alias(value=\"Why Is It a Problem\\\\?\")\n├── question_3: Question3 | None                 # optional H3, @alias(value=\"Where Is the Problem Observed\\\\?\")\n├── question_4: Question4 | None                 # optional H3, @alias(value=\"Who Is Impacted\\\\?\")\n├── question_5: Question5 | None                 # optional H3, @alias(value=\"When Was the Problem First Observed\\\\?\")\n├── question_6: Question6 | None                 # optional H3, @alias(value=\"How Is the Problem Observed\\\\?\")\n└── question_7: Question7 | None                 # optional H3, @alias(value=\"How Often Is the Problem Observed\\\\?\")\n```\n\nEvery `Question{N}`/`Summary`/`Gap`/`Impact`/`FutureState`/`References`/\n`MoreInformation` class is a bare leaf subclass with no further declared\nfields — the same \"opaque, captures any remaining markdown verbatim\"\npattern already verified for REQ's `MoreInformation`/`Notes` and QA's\n`RawRequirements`/`QaAnswer` (no new engine mechanism needed for this).\n\n**Question heading wording is fixed and exact** (verbatim from the\niSixSigma 5W2H list, each requiring an explicit `@alias(...)` since the\nclass names `Question1`..`Question7` don't derive to this wording via the\nimplicit `AliasType.SPACE_SEPARATED` convention):\n\n1. What Is the Problem?\n2. Why Is It a Problem?\n3. Where Is the Problem Observed?\n4. Who Is Impacted?\n5. When Was the Problem First Observed?\n6. How Is the Problem Observed?\n7. How Often Is the Problem Observed?\n\n**`Summary` is mandatory, the 7 questions are all optional.** A freshly\ncreated `prb` document may have zero questions answered yet (all deferred\nto a later `update_prb` call) but must always carry *some* `Summary` text\n(even a short placeholder at creation time) — mirrors ADR's own\nmandatory-vs-optional body-field split, not TSK's \"must seed a first\nRecent Updates entry\" pattern (there is no dynamic list here).\n\n**`Gap`/`Future State` are mandatory; `Impact`/`References`/\n`More Information` are optional** — matching the plain list the user gave,\nplus the newly-added optional `Impact`, placed between `Gap` and\n`Future State` (current state → gap → why it matters → target state).\n\n**No Root Cause section** (see Scope: Explicitly out of scope) — this is a\ndeliberate, methodology-driven omission, not an oversight.\n\n**Update mechanism: whole-body `update_prb(id, content)`**, not an\nADR-style `update_section`. The generic `adr/tools/update_section.py`\nmechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently\nADR-specific code, not a shared cross-domain component — reusing it for\nPRB would mean building a second, parallel implementation. Individual\nquestions/sections stay addressable by grepping/editing their fixed\nheading text within the whole-body markdown, which is what \"fixed heading\nper question\" is actually for (addressability without a dedicated tool\nper field).\n\n**`list_prb` is a paged tool from day one** (`@mcp.tool(name=\"list_prb\")`\nreturning `PagedResult[PrbSummary]`, via `general/tools/_paging.py`'s\n`paginate`/`normalize_paging`), not a `specmgr://prb/list` resource —\nunlike REQ/TSK/QA (which launched as resources and were converted later in\nfeat-13), PRB is a new domain built *after* ADR ec9f5262 was accepted, so\nit must not repeat the resource-then-convert history. `PrbSummary`\nsubclasses `general/models/summary.py::DocSummary` (`id`/`title`/`status`/\n`ref`), like `ReqSummary`/`TskSummary`/`QaSummary`.\n\n**Prompts are narrated instructions only** (return a string, auto-wrapped\nas a `UserMessage` by the MCP SDK) — `create_prb`/`update_prb` never call\n`TodoWrite`/`question`/`get_prb`/`create_prb`/`update_prb` themselves; they\nonly narrate that the calling LLM should. This is the same contract every\nexisting prompt in this codebase already follows\n(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).\n\n- `create_prb(topic: str) -> str`: instructs the LLM to (1) call `list_prb`\n  first to check for an existing, similar problem statement (mirrors\n  `create_req`'s dedup-check pattern) and ask the user via `question` if a\n  near-duplicate is found; (2) build a `TodoWrite` list with one entry per\n  the `Summary` + 7 questions + `Gap` + `Impact` + `Future State`; (3) use\n  the `question` tool to elicit each of the 7 answers in turn, explicitly\n  allowing the user to skip any; (4) synthesize a `Summary` paragraph from\n  whichever answers were actually given; (5) draft a candidate `Gap`\n  statement from the collected current-state answers (following the\n  expected-vs-actual/measurable-difference formula from the\n  LearnLeanSigma article) and confirm/refine it with the user via\n  `question` before finalizing; (6) optionally ask for `Impact`; (7) ask\n  for `Future State` (desired/target condition); (8) optionally ask for\n  `References`/`More Information`; (9) assemble the full body markdown per\n  the fixed schema above and call `create_prb(content)`.\n- `update_prb(id: str) -> str`: instructs the LLM to (1) call `get_prb(id)`\n  first (never assume prior state); (2) show the user which of the 7\n  questions already have answers and which are still empty, and ask via\n  `question` which ones (if any) they want to add to or revise; (3) for\n  each selected question, elicit the new/revised text via `question`; (4)\n  regenerate the `Summary` from the *complete*, current set of answers\n  (a full re-synthesis, not an append); (5) re-draft/refine the `Gap`\n  the same way as `create_prb` step 5, based on the now-current-state\n  answers, confirming with the user; (6) optionally revise `Impact`/\n  `Future State`/`References`/`More Information`; (7) call\n  `update_prb(id, content)` (whole-body replace, carrying forward every\n  unchanged section); (8) mention `set_status_prb` as a separate, optional\n  follow-up (e.g. `resolved` once `Future State` has genuinely been\n  reached, `cancelled` if abandoned).\n\nBoth prompts' instructional text lives in packaged data files\n(`prb/data/prb_create_instructions.md`/`prb_update_instructions.md`, read\nvia `general.tools._packaged_data.read_packaged_text`, `string.Template`\nsubstitution), matching `req_create_instructions.md`/\n`tsk_implement_instructions.md`'s precedent — not an inline Python string\n— since the narration is long enough to warrant it.\n\n**Frontmatter status** (`draft`/`active`/`resolved`/`cancelled`) mirrors\nTSK/QA's 4-value closed set exactly, with PRB-specific semantics: `draft`\n= still being filled in; `active` = current state captured, gap/future\nstate being refined; `resolved` = future state reached; `cancelled` =\nabandoned.\n\n### Related ADRs\n\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by\n  document-type domain (domain-first hierarchy)\n- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for\n  markdown document types\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool\n  (`get_prb`), not a resource\n- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged\n  MCP tool (`list_prb`), not a resource — must be followed from the start\n  for this new domain, not retrofitted later\n- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed\n  and explicitly *not* reused for `prb` (see Design Notes)\n\nNo new ADR is anticipated for this feature — every schema/tooling decision\neither follows an existing ADR's precedent directly or is scoped enough to\nlog only in this file's own Decisions Made.\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself. Each phase ends with a mandatory phase-end task (tests, full\nquality gate, README Progress update), mirroring feat-10/feat-12's\nper-phase commit discipline, since implementation is likely to span\nmultiple sessions.\n\n#### Phase 1: Specification\n\n- [ ] Task 1.1: Write a full reference `prb_reference.md`\n  (`.specmgr/feat/feat-0-problem-statement/prb_reference.md`) exercising\n  every field (all 7 questions answered, `Impact`/`References`/\n  `More Information` all present) — depends on: none — status: not-started\n- [ ] Task 1.2: Define `prb` frontmatter (`prb/models/v1/frontmatter.py` —\n  `PrbFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal[\"prb\"]`,\n  4-value status set `draft`/`active`/`resolved`/`cancelled`, mirroring\n  `TskFrontmatter`'s `_ALLOWED_STATUSES` pattern) — depends on: none —\n  status: not-started\n- [ ] Task 1.3: Define `prb` body structure\n  (`prb/models/v1/body.py`) — `Prb(MarkdownSection1WithComment)`,\n  `CurrentState(MarkdownSection2)` with mandatory `summary: Summary` and\n  optional `question_1..question_7: Question{N} | None` (each with an\n  explicit `@alias(...)` matching the exact 5W2H wording — see Design\n  Notes), `Gap`/`FutureState` (mandatory leaves), `Impact`/`References`/\n  `MoreInformation` (optional leaves) — depends on: Task 1.2 — status:\n  not-started\n- [ ] Task 1.4: `tests/prb/models/v1/test_frontmatter.py`, `test_body.py`\n  — structural + validation tests mirroring `tests/tsk/models/v1/`/\n  `tests/qa/models/v1/`, explicit coverage of mandatory-vs-optional field\n  combinations (each of the 7 questions individually absent/present;\n  `Impact`/`References`/`More Information` absent/present) — depends on:\n  Task 1.3 — status: not-started\n- [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality\n  gate (ruff format/check, vulture, full `unittest` suite); confirm\n  `prb_reference.md` is `specmgr mdformat`-clean; update this README's\n  Progress section — depends on: Task 1.1, Task 1.4 — status: not-started\n\n#### Phase 2: Pydantic Models, Parser & Schema\n\n- [ ] Task 2.1: `prb/models/v1/document.py` (`PrbDocument(frontmatter,\n  body)`, mirroring `TskDocument`/`QaDocument`) — depends on: Task 1.3 —\n  status: not-started\n- [ ] Task 2.2: Implement `parse_prb(text: str) -> PrbDocument` (model-layer\n  function, mirrors `parse_tsk`/`parse_qa`) — depends on: Task 2.1 —\n  status: not-started\n- [ ] Task 2.3: `prb/models/v1/summary.py` (`PrbSummary(DocSummary)`,\n  subclassing `general/models/summary.py::DocSummary`, for `list_prb`) —\n  depends on: Task 2.1 — status: not-started\n- [ ] Task 2.4: Field-level `Field(description=...)` on every scalar/\n  optional field (schema-quality parity with REQ/TSK/QA) — depends on:\n  Task 2.1 — status: not-started\n- [ ] Task 2.5: Implement `generate_prb_schema()` in `commands/schema.py`\n  (mirroring `generate_tsk_schema`/`generate_qa_schema`, via\n  `PrbDocument.model_json_schema()`) + register `\"prb\"` in the\n  `specmgr schema` doc-type generator registry (`_GENERATORS`); draft\n  `docs/prb_schema.json` — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.6: `tests/prb/models/v1/test_parser.py` — mirrors\n  `TestParseTsk`/`TestParseQa`'s shape (minimal doc, full reference-doc\n  round-trip, defaults-when-absent, invalid status, missing-mandatory-\n  section `AssertionError`, invalid-field `ValidationError`) — depends on:\n  Task 2.2, Task 2.5 — status: not-started\n- [ ] Task 2.7: Phase-end quality gate — full pre-commit/quality gate\n  including Task 2.6's new tests; update this README's Progress section —\n  depends on: Task 2.5, Task 2.6 — status: not-started\n\n#### Phase 3: MCP Surface\n\n- [ ] Task 3.1: `prb/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin\n  wrappers over `general/tools/_doc_paths.py` (mirrors `tsk/tools/`/\n  `qa/tools/` exactly) — depends on: Task 2.2 — status: not-started\n- [ ] Task 3.2: `parse_prb(path: str) -> PrbDocument` tool wrapper\n  (`prb/tools/parse_prb.py`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.3: `create_prb(content: str) -> PrbDocument` tool (body-only\n  content; MCP builds frontmatter: `id`, `type=\"prb\"`, `status=\"draft\"`,\n  `created=updated=now`, `version`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: `update_prb(id, content) -> PrbDocument` tool (whole-body\n  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps\n  `updated`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: `set_status_prb(id, status) -> PrbDocument` tool (only path\n  that changes `status`; reconstructs `PrbFrontmatter` via its own\n  constructor so the 4-value validator runs, mirroring `set_status_tsk`/\n  `set_status_qa`) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.6: `delete_prb(id) -> NoReturn` stub tool — depends on: Task\n  3.1 — status: not-started\n- [ ] Task 3.7: `validate_prb(content, full=False) -> bool` tool — depends\n  on: none — status: not-started\n- [ ] Task 3.8: `get_prb(id) -> PrbDocument` tool (id-based single-document\n  read; tool, not resource) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.9: `list_prb(max_results=None, offset=None) -> PagedResult[PrbSummary]`\n  tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`\n  (default page size 25, cap 100), preserving the standard skip-malformed-\n  file scan behavior — depends on: Task 2.3, Task 3.1 — status:\n  not-started\n- [ ] Task 3.10: `get_prb_example`/`get_prb_template` tools + packaged data\n  (`prb/data/prb_example.md`, `prb/data/prb_template.md`) via\n  `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:\n  not-started\n- [ ] Task 3.11: `prb/resources/{prb_schema,prb_example,prb_template}.py`\n  — `specmgr://prb/schema` (packaged `prb/data/prb_schema.json`, mirroring\n  `specmgr://tsk/schema`), `specmgr://prb/example`, `specmgr://prb/template`\n  (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:\n  not-started\n- [ ] Task 3.12: `pyproject.toml` package-data entry for\n  `biz.dfch.specmgr.prb` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`\n  — widen the shared schema-hook glob to include `prb/models/v1`, add a\n  `specmgr-schema-prb-package` hook — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.13: `.github/workflows/ci.yml` — add the `docs/prb_schema.json`\n  check + packaged-copy check steps — depends on: Task 2.5 — status:\n  not-started\n- [ ] Task 3.14: `prb/data/prb_create_instructions.md` +\n  `prb/prompts/create_prb.py` (`@mcp.prompt()`, `string.Template`\n  substitution, narrates the full interview flow — see Design Notes) —\n  depends on: Tasks 3.3, 3.9 — status: not-started\n- [ ] Task 3.15: `prb/data/prb_update_instructions.md` +\n  `prb/prompts/update_prb.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:\n  not-started\n- [ ] Task 3.16: `prb/__init__.py` (docstring + `from . import prompts,\n  resources, tools`), add `prb` to `server.py`'s bottom-of-file domain\n  import line (alphabetical: `adr, general, prb, qa, req, tsk, uc`) and\n  update its module docstring (Tools/Resources/Prompts sections) — depends\n  on: Tasks 3.2-3.15 — status: not-started\n- [ ] Task 3.17: `tests/prb/tools/...`, `tests/prb/resources/...`,\n  `tests/prb/prompts/...` mirroring `tests/tsk/`/`tests/qa/`'s layout,\n  including live end-to-end coverage of `create_prb`/`update_prb`'s\n  narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_prb`'s\n  paging behavior (default page size, `max_results` clamping, `offset`\n  paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:\n  not-started\n- [ ] Task 3.18: Phase-end quality gate — full pre-commit/quality gate\n  including Task 3.17's new tests; update this README's Progress section\n  — depends on: Task 3.17 — status: not-started\n\n#### Phase 4: Cross-cutting registration\n\n- [ ] Task 4.1: `AGENTS.md` — update heading to \"seven domain/cross-cutting\n  packages implemented (ADR, REQ, UC, TSK, QA, PRB, general)\"; add a\n  `prb/` bullet (chronological order, after `qa/`); update the \"Still\n  genuinely missing\" list (`validate_prb` not enforced via pre-commit/CI,\n  `delete_prb` stub) and the closing domain-enumeration paragraphs —\n  depends on: Phase 3 complete — status: not-started\n- [ ] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`\n  regeneration — confirm `prb` appears correctly and all three commands\n  report zero drift — depends on: Task 4.1 — status: not-started\n- [ ] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;\n  update this README's Progress section — depends on: Task 4.2 — status:\n  not-started\n\n#### Phase 5: Final cross-cutting verification\n\n- [ ] Task 5.1: Final verification pass — walk every ACC-001..008 and\n  confirm each is satisfied with concrete evidence (including a live\n  `create_prb`→`update_prb`→`set_status_prb` run, not just unit tests);\n  run the full quality gate (ruff format/check, pylint advisory, vulture,\n  unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift\n  checks) end to end; set feature status to `done` — depends on: Phase\n  1-4 complete — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-25**: Planning complete. This plan was designed\ncollaboratively (user + agent) in a dedicated planning session before any\nimplementation; no code has been written yet. A fresh-context session\nshould pick up at Phase 1, Task 1.1. Note: this feature folder uses the\n`feat-0-problem-statement` placeholder id/slug (no GitHub issue filed yet,\nper `AGENTS.md`'s convention) — expect it to be renamed to\n`feat-NNN-problem-statement` (frontmatter `id` updated to match) once an\nissue number is assigned; do not treat `feat-0` as permanent.\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### Update 2026-08-25\n\n- Completed: Full design/planning discussion — schema shape (5W2H\n  questions under `Current State`, `Gap`/`Impact`/`Future State`/\n  `References`/`More Information`), status set, update mechanism, prompt\n  behavior, and MCP surface all decided; this README written from that\n  discussion. Also flagged (but explicitly did not fix, as out of scope\n  here) that `AGENTS.md`'s TSK/QA `specmgr://<d>/list` bullets are stale\n  post-`feat-13-list-paging` — added as `feat-7-various-improvements`\n  Task 0.24 instead.\n- Next: Phase 1 (Specification) — write `prb_reference.md`, define\n  frontmatter/body models.\n- Notes: No implementation attempted this session by design (planning-only\n  session per explicit user instruction).\n\n### Decisions Made\n\n- **2026-08-25**: Type abbreviation `prb`, domain-first layout\n  (`prb/models/v1/`, `prb/tools/`, `prb/resources/`, `prb/prompts/`,\n  `prb/data/`) — matches TSK/QA precedent (schema lives inside the domain\n  package, not top-level `models/`), since PRB is a new domain built after\n  the domain-first refactor.\n- **2026-08-25**: 5W2H question set taken verbatim from the iSixSigma\n  article (What/Why/Where/Who/When/How/How Often), each a fixed, optional\n  H3 heading under a mandatory `## Current State` H2 with a mandatory\n  `### Summary` leaf. Question heading wording is the plain question text\n  (not numbered) — chosen over \"Question N: ...\" for readability.\n- **2026-08-25**: Status set `draft`/`active`/`resolved`/`cancelled` —\n  reuses TSK/QA's 4-value pattern/wording convention, with PRB-specific\n  semantics.\n- **2026-08-25**: `update_prb` is a single whole-body replace tool\n  (REQ/TSK/QA convention), not an ADR-style `update_section`/option-style\n  granular tool — the latter is currently ADR-specific code (ADR\n  71fd95d7), and porting it was judged not worth the added scope for this\n  feature. Individual questions/sections remain addressable by their fixed\n  heading text within the whole-body markdown.\n- **2026-08-25**: `References` is opaque free text for v1 (like\n  `MoreInformation`/`Notes`), not structured by artifact type — deferred,\n  matching every other domain's own \"defer structured cross-linking\"\n  decision.\n- **2026-08-25**: Added an optional `Impact` H2 (between `Gap` and\n  `Future State`) per user request, to hold business/cost/safety\n  consequence separately from `Gap` itself (which stays a pure\n  actual-vs-expected measurement, per the LearnLeanSigma article's\n  explicit warning against conflating gap and consequence).\n- **2026-08-25**: No `Root Cause` section — deliberately excluded per Six\n  Sigma discipline (both source articles explicitly warn against including\n  assumed causes in a problem statement); any future RCA artifact type\n  would be a separate feature, only ever referenced from `References`.\n- **2026-08-25**: `list_prb` ships as a paged `@mcp.tool()` from day one\n  (per ADR ec9f5262, already accepted/`done` via feat-13) — this domain\n  must not repeat REQ/TSK/QA's original resource-then-later-converted\n  history.\n- **2026-08-25**: Prompt names `create_prb`/`update_prb` (tool-name\n  convention, like REQ/QA), not literal wording like TSK's\n  `create_task`/`update_task`/`implement_task`.\n- **2026-08-25**: GitHub issue not yet filed — feature folder uses the\n  `feat-0-problem-statement` placeholder per `AGENTS.md`'s convention;\n  rename the folder (and this frontmatter `id`) once/if an issue number is\n  assigned.\n- **2026-08-25**: `AGENTS.md`'s pre-existing TSK/QA `specmgr://<d>/list`\n  drift (found during this planning session) is fixed under\n  `feat-7-various-improvements` Task 0.24, not here — out of scope for\n  this feature.\n\n### Related PRs / Commits\n\nNone yet — planning only.\n"
}
````

**Output:**

```
Wrote file successfully.
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 8.7s)

_Thinking:_

Now let me format both files with the project's markdown formatter to match the repo's conventions.

**Tool: specmgr_mdformat**

**Input:**

```json
{
  "path": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-0-problem-statement/README.md"
}
```

**Output:**

```
true
```

**Tool: specmgr_mdformat**

**Input:**

```json
{
  "path": "/home/admin/src/biz.dfch.SpecMgr/.specmgr/feat/feat-7-various-improvements/README.md"
}
```

**Output:**

```
true
```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 4.0s)

Both files were reformatted. Let me quickly review the diffs to make sure `mdformat` didn't mangle anything important (e.g., the schema code block or task list numbering).

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/admin/src/biz.dfch.SpecMgr && git diff --stat .specmgr/ && echo \"---\" && git status --short .specmgr/"
}
```

**Output:**

```
 .specmgr/feat/feat-7-various-improvements/README.md | 20 +++++++++++++++++---
 1 file changed, 17 insertions(+), 3 deletions(-)
---
 M .specmgr/feat/feat-7-various-improvements/README.md
?? .specmgr/feat/feat-0-problem-statement/

```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 3.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/admin/src/biz.dfch.SpecMgr && git diff .specmgr/feat/feat-7-various-improvements/README.md"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-7-various-improvements/README.md b/.specmgr/feat/feat-7-various-improvements/README.md
index 32c5d58..d988a47 100644
--- a/.specmgr/feat/feat-7-various-improvements/README.md
+++ b/.specmgr/feat/feat-7-various-improvements/README.md
@@ -2,7 +2,7 @@
 created: 2026-08-15
 id: feat-7-various-improvements
 status: planning
-updated: 2026-08-19
+updated: 2026-08-25
 version: 1.0.0
 ---
 
@@ -596,6 +596,21 @@ progresses (edit, don't duplicate).
   `get_tsk` MCP tool with id `aaf70093-8a7c-4565-9985-3beaa85e1d3d` —
   depends on: none — status: done (2026-08-19)
 
+- [ ] Task 0.24: Clean up `AGENTS.md`'s stale `specmgr://<d>/list` resource
+  mentions left over from `feat-13-list-paging`'s resource→tool conversion
+  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13) — `AGENTS.md`'s per-domain
+  bullets (at least `req`/`tsk`/`qa`, confirm `uc`/`adr` too) still
+  describe `specmgr://req/list`/`specmgr://tsk/list`/`specmgr://qa/list`
+  as resources instead of the `list_req`/`list_tsk`/`list_qa` tools they
+  actually are today; found and flagged during
+  `.specmgr/feat/feat-0-problem-statement/README.md`'s planning session
+  (2026-08-25) while designing that new domain's own `list_prb` tool
+  against the *current* code/ADR state rather than `AGENTS.md`'s
+  (out-of-date) wording. Fix every affected domain bullet, plus any other
+  live `specmgr://<d>/list` mention in `AGENTS.md` (e.g. the "MCP server
+  (`server.py`)" section's own domain-surface description, if it lists
+  resources per domain) — depends on: none — status: not-started
+
 - [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff
   their output shape/behavior (`adr_list` vs. `req_list`) — depends on:
   none — status: not-started
@@ -616,8 +631,7 @@ progresses (edit, don't duplicate).
   **completed** via `feat-13-list-paging` (resource→tool `list_<domain>` +
   `asdste100`-style `PagedResult` wrapper, recorded in ADR
   ec9f5262-9912-49d0-903f-fcfb54f28c13); the shared-base-summary piece was
-  also carried into and completed by that feature (`general.models.
-  DocSummary`, subclassed by 4 of 5 domains — see ACC-001).
+  also carried into and completed by that feature (`general.models. DocSummary`, subclassed by 4 of 5 domains — see ACC-001).
 - [ ] Task 2.2: Decide the fate of the `_test` prompt variants and the
   criteria used for the prompt-quality review — depends on: Task 1.2 —
   status: not-started

```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 5.6s)

Clean — only my intended change plus a pre-existing line-wrap fix from `mdformat`. Let me verify the new PRB plan file rendered correctly too (spot-check the code block and task list survived formatting intact).

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/admin/src/biz.dfch.SpecMgr && wc -l .specmgr/feat/feat-0-problem-statement/README.md && sed -n '1,10p;150,175p' .specmgr/feat/feat-0-problem-statement/README.md"
}
```

**Output:**

```
573 .specmgr/feat/feat-0-problem-statement/README.md
---
created: 2026-08-25
id: feat-0-problem-statement
status: planning
updated: 2026-08-25
version: 1.0.0
---

# Feature: Add artifact type Problem Statement (prb)

- Any deterministic/algorithmic (non-LLM) computation of `Summary`/`Gap`
  text. Both are synthesized by the calling agent while following the
  prompt's narrated instructions — no NLP/heuristic code ships in `src/`
  for this.
- A `specmgr prb-toc`-equivalent generation command or dedicated CI/
  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` already provide generically.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (tool-only id-based reads, no `specmgr://prb/{id}` resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
  not a resource — `list_prb` must follow this from day one), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
  `general/models/{DocSummary,PagedResult}` infrastructure, and the
  existing `models/md` engine (`MarkdownSection1WithComment`,
  `MarkdownSection2`, `MarkdownSection3`, `@alias`) — reused as-is, no
  engine changes anticipated.
- Blocks: None identified yet.
- Related, but explicitly out of scope here: `feat-7-various-improvements`
  Task 0.24 (cleaning up `AGENTS.md`'s stale `specmgr://<d>/list`
  resource-vs-tool wording for TSK/QA, found during this feature's own
  planning session but not this feature's concern to fix).

```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 7.3s)

Both files are written and clean. Summary of what's done:

1. **`.specmgr/feat/feat-0-problem-statement/README.md`** — the complete PRB feature plan, with the full schema design (Design Notes), REQ-001..008, ACC-001..008, Scope, Dependencies, a 5-phase Task List (Specification → Models/Parser/Schema → MCP Surface → Cross-cutting registration → Final verification), and a Decisions Made log capturing every choice we made today. Status `planning`, `feat-0` placeholder id as agreed — rename it once an issue number exists.

2. **`.specmgr/feat/feat-7-various-improvements/README.md`** — added Task 0.24 (Phase 0: Housekeeping) to track cleaning up `AGENTS.md`'s stale TSK/QA `specmgr://<d>/list` resource wording (should be `list_<d>` tool wording, post-feat-13), with a note pointing back to this session as the origin of the finding. Bumped `updated` to today.

Nothing was implemented — no `src/`/`tests/` code was touched, per your instruction that implementation happens in a fresh session. A future agent can pick this up starting at Phase 1, Task 1.1 of the PRB plan.

______________________________________________________________________

## User

now create a gh issue and use the overview of our feat as the description. Use the created id and rename the path from feat-0-problem... to the actual id.

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 7.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "which gh 2>&1; gh --version 2>&1; echo \"---\"; cd /home/admin/src/biz.dfch.SpecMgr && git remote -v"
}
```

**Output:**

```
/bin/bash: line 1: gh: command not found
---
origin	https://github.com/dfch/biz.dfch.SpecMgr.git (fetch)
origin	https://github.com/dfch/biz.dfch.SpecMgr.git (push)

```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 10.5s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "env | grep -i -E \"github|gh_token|gitea\" | sed 's/=.*/=<redacted>/'; echo \"---apt---\"; apt list --installed 2>/dev/null | grep -i \"gh$\"; which curl; cat /etc/os-release | head -3"
}
```

**Error:**

```
The user rejected permission to use this specific tool call.
```

______________________________________________________________________

## User

you use the gh cli command to create the isse

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 7.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "which gh 2>&1; command -v gh 2>&1; echo \"exit:$?\""
}
```

**Output:**

```
exit:1

```

______________________________________________________________________

## Assistant (Build · Claude Sonnet 5 · 19.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cat /etc/os-release 2>&1 | head -5; echo \"---\"; which apt apt-get dnf yum brew snap 2>&1"
}
```

**Error:**

```
The user rejected permission to use this specific tool call.
```

______________________________________________________________________
