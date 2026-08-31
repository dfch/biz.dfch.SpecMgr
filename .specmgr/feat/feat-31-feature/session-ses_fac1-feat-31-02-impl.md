# feat-31 timestamp implementation

**Session ID:** ses_fac109805ffez30uRRIgjiayw4
**Created:** 8/30/2026, 8:29:53 PM
**Updated:** 8/30/2026, 8:48:03 PM

______________________________________________________________________

## User

Implement the feature planned in \`.specmgr/feat/feat-31

We already implement the feature and have some follow up tasks with a new Phase. Examine the last phase. There is one task regarding time stamps. We need to implement this. Be careful not to break existing code. Update existing tests. Do not create new ones, because there is no real NEW functionality.

Proceed if you do not have questions./README.md\`.

Act strictly as an orchestrator: read the plan in full, build a phase-by-phase
`todowrite` list, and drive it to completion by delegating **each phase** to a
fresh `phase-implementer` subagent (one subagent per phase, in dependency
order). After each subagent returns, independently re-run that phase's quality
gate, inspect `git diff`, confirm the phase's acceptance criteria, then — with
my confirmation — commit that phase as one Conventional Commit before moving
on. Do not write or edit any file yourself; delegate all implementation.

Before delegating a phase whose design depends on an unresolved decision, ask
me first.

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-30
3: id: feat-31-feature
4: status: in-progress
5: updated: 2026-08-30
6: version: 1.12.0
7: ---
8: 
9: # Feature: Formalize the Feature artifact type ("feat")
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Formalize the ad hoc `.specmgr/feat/<id>/README.md` convention (ADR
16: e369ee2e-3353-4f92-991c-6367d76d832e) into a real, schema-backed `feat`
17: document-type domain — the same kind of markdown-frontmatter, Pydantic-modeled,
18: MCP-tool-addressable artifact every other document type in this repo already
19: is. `feat` is deliberately special among domains: it formalizes a convention
20: that has already been used, by hand, 17+ times before this feature existed,
21: and its addressing scheme (`id` = a chosen `feat-NNN-slug`, not a
22: server-generated UUID; one folder per document holding a fixed `README.md`
23: filename, not a flat file directly under the base directory) is a genuine,
24: intentional deviation from every other domain's `8cf940c5` precedent. `feat`
25: follows the domain-first hierarchy (ADR
26: ece4554b-725c-4f76-bc04-5d2b760363d2) and is built on the generic `models/md`
27: parsing engine with the simple surface used by GOL/RSK/DEC/(planned)SOP — no
28: fine-grained mutation tools, no renderer (writes persist the caller's raw
29: validated body byte-for-byte) — and is the second domain (after the
30: still-unimplemented `feat-30-sop`) planned to use the post-feat-22 generic
31: `update`/`set_status` dispatch tools from day one (ADR
32: 36905d5b-8057-4294-8665-c7eed5534db0): there is no `update_feat`/
33: `set_status_feat` tool of its own.
34: 
35: Implementation happens on a dedicated branch `feat-31-feature`, created off
36: `dev` before Phase 0 starts (this branch), mirroring every prior "add
37: artifact type" feature's own branch-per-feature convention (e.g.
38: `feat-21-decision`, `feat-15-add-artifact-type-risk`).
39: 
40: ### Requirements
41: 
42: - REQ-001: Define the `feat` markdown schema — frontmatter (`type="feat"`,
43:   closed 4-value status set `planning`/`progress`/`review`/`done` with no
44:   hyphens in any value, default `planning`) and body (H1 `# Feature: {title}`,
45:   `## Plan` composite with mandatory leaf `### Overview`; mandatory
46:   regex-validated `### Requirements`/`### Acceptance Criteria` lists (≥1 item
47:   each, `REQ-\d{3}: ...`/`- [ ] ACC-\d{3}: ...`); mandatory composite
48:   `### Scope` (mandatory `#### Included`/`#### Explicitly Out Of Scope`
49:   leaves); optional composite `### Dependencies` (optional
50:   `#### Depends On`/`#### Blocks` leaves); optional leaf `### Design Notes`/
51:   `### Related Decisions`; mandatory composite `### Task List` (no own text, only
52:   `#### Phase N: ...` entries, ≥1, each a regex-validated heading holding its
53:   own `- [ ] .../- [x] ...` checklist, ≥1 item); `## Progress` composite
54:   with mandatory leaf `### Current Status`, optional leaf `### Blockers`,
55:   mandatory composite `### Updates` (optional leading comment,
56:   ISO8601-timestamped `#### {timestamp} — {title}` entries, ≥1,
57:   newest-first order enforced), optional composite `### Decisions Made`
58:   (same shape as `### Updates` — optional leading comment, ISO8601
59:   timestamps, newest-first order enforced), optional leaf
60:   `### Related PRs / Commits`, optional leaf `### More Information`).
61: - REQ-002: Pydantic models under `feat/models/v1/` (frontmatter, body,
62:   document, parser, summary, `_util.py` with `SCHEMA_COMMENT_VERSION = "v1"`),
63:   domain-first, mirroring `dec`/`gol`'s exact file shapes. `Updates`/
64:   `UpdateEntry` copies `feat-30-sop`'s planned ISO8601-enforced shape one
65:   heading level deeper (`### Updates`/`#### {timestamp} — {title}` instead of
66:   SOP's `## Updates`/`### {timestamp} — {title}`) — see Design Notes for the
67:   exact regex. No `models/md` engine changes needed: `MarkdownSection1`
68:   through `MarkdownSection6` already exist, so the H3→H4 dynamic-list pattern
69:   is the same generic mechanism TSK's/DEC's H2→H3 `Updates`/`UpdateEntry`
70:   already exercises, just one level deeper.
71: - REQ-003: Parse/validate `feat` documents from markdown, mirroring
72:   `parse_dec`/`parse_gol`'s two-error-channel convention (`AssertionError` for
73:   structural problems, `pydantic.ValidationError` for field-level problems).
74:   Additionally: the invariant "frontmatter `id` equals the containing
75:   folder's name" is enforced at the **tool** layer (`feat/tools/_paths.py`/
76:   `_io.py`), not the model layer — the model-layer `parse_feat(text: str)`
77:   has no path/folder-name to check against, matching every other domain's
78:   pure-text model-layer parser signature.
79: - REQ-004: Bespoke, folder-per-document addressing (`feat/tools/_paths.py`,
80:   hand-rolled like ADR's own `adr/tools/_paths.py`, **not** the shared
81:   flat-file `general/tools/_doc_paths.py`): base directory `.specmgr/feat`,
82:   documents at `<base>/<id>/README.md`. **`SPECMGR_FEAT_DIR` (mandatory,
83:   not optional)** overrides the base directory — this is not a `feat`-only
84:   nicety: every existing domain has an equivalent env var
85:   (`SPECMGR_ADR_DIR` in `adr/tools/_paths.py`; the shared `SPECMGR_DOCS_DIR`
86:   in `general/tools/_doc_paths.py`, used by `req`/`uc`/`tsk`/`qa`/`prb`/
87:   `gol`/`rsk`/`dec`), specifically so tests never read/write the real
88:   base directory (for `feat`, that would mean the real `.specmgr/feat/`
89:   — the very folder this plan file itself lives in). Omitting it would
90:   make `feat` the only domain in the codebase without test isolation for
91:   its base directory. Since `id` is the folder name by convention,
92:   `find_feat_path_by_id` shortcuts straight to `<base>/<id>/README.md` and
93:   verifies the frontmatter `id` matches (raising `FeatNotFoundError`
94:   otherwise) instead of a full directory scan. `create_feat` derives the next
95:   `NNN` by scanning existing `feat-*` folder names under a **global**
96:   create-lock (distinct from every other domain's per-id lock, since the id
97:   doesn't exist yet when the lock must be taken). No partial-id-match
98:   support (e.g. resolving a bare `"feat-31"` to `"feat-31-feature"`) —
99:   considered and rejected, see Decisions Made.
100: - REQ-005: 8 MCP tools, sop-style generic dispatch (**no**
101:   `update_feat`/`set_status_feat` — see Overview): `create_feat`,
102:   `parse_feat`, `list_feat` (paged tool from day one, ADR
103:   ec9f5262-9912-49d0-903f-fcfb54f28c13), `get_feat(id, raw=False)`,
104:   `get_feat_example`, `get_feat_template`, `delete_feat` (stub),
105:   `validate_feat` — plus private `_paths`/`_io`/`_lock`/`_write` helpers per
106:   REQ-004.
107: - REQ-006: Add `"feat"` to the generic cross-domain mutation tools —
108:   `_update_feat`/`_set_status_feat` adapters and `type="feat"` dispatch table
109:   entries in `general/tools/update.py`/`set_status.py`, built on REQ-004's
110:   bespoke `_paths`/`_io`/`_lock`/`_write` (same shape as the eight existing
111:   adapters, just resolving paths differently).
112: - REQ-007: MCP resources: `specmgr://feat/schema`, `/example`, `/template`
113:   (no `/list` — REQ-005 covers listing as a tool; no `/{id}` — id-based reads
114:   are `get_feat`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
115: - REQ-008: MCP prompts `create_feat(topic)`/`update_feat(id, instructions=None)` — narrated instruction flows reusing the
116:   dedup-check-first pattern (`list_feat`) and the `TodoWrite`/`question`-tool
117:   narration pattern from `gol`/`dec`/`prb`'s prompts; both read their own
118:   packaged instructions data file (`feat/data/feat_create_instructions.md`/
119:   `feat_update_instructions.md`), not an inline string.
120: - REQ-009: `generate_feat_schema()` + `_GENERATORS["feat"]` in
121:   `commands/schema.py`; packaged `feat/data/feat_schema.json`.
122: - REQ-010: Cross-cutting registration (`server.py`, `pyproject.toml`,
123:   `.pre-commit-config.yaml`, CI, `AGENTS.md`, root `README.md`, regenerated
124:   docs) and a new backlog task in `feat-7-various-improvements` (Task 0.31)
125:   tracking the future migration of the 17 pre-existing feature folders into
126:   this schema — added as part of this feature's own scope, the migration
127:   itself is explicitly out of scope (see Scope).
128: - REQ-011: Full test coverage mirroring `tests/dec/`'s layout and depth.
129: 
130: ### Acceptance Criteria
131: 
132: - [x] ACC-001: Verifies REQ-001/002 — schema documented
133:   (`docs/feat_schema.json`, `specmgr://feat/schema`); a reference
134:   `feat_reference.md` exercising every field (all mandatory + optional
135:   sections present, ≥2 `### Updates` entries in newest-first order, ≥2
136:   `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`
137:   entries each with ≥1 task item) round-trips through `parse_feat`
138:   byte-exact; `FeatFrontmatter.status` rejects any value outside the
139:   4-set; malformed `#### {timestamp} — {title}` headings (both `Updates`
140:   and `Decisions Made` — identical format) and `#### Phase N: ...`
141:   (`Task List`) headings all raise `AssertionError`; an out-of-order
142:   (not newest-first) entry in either `Updates` or `Decisions Made` raises
143:   `AssertionError`; a malformed `REQ-\d{3}: ...`/`- [ ] ACC-\d{3}: ...`
144:   list item raises `AssertionError`.
145: - [x] ACC-002: Verifies REQ-003/004 — a document whose frontmatter `id`
146:   doesn't match its containing folder's name is rejected by the tool layer
147:   (not the model layer); `find_feat_path_by_id` resolves via the direct
148:   `<base>/<id>/README.md` shortcut, not a directory scan; `create_feat`
149:   correctly derives the next `NNN` under concurrent-create simulation (global
150:   lock prevents two callers from picking the same `NNN`).
151: - [x] ACC-003: Verifies REQ-005 — every listed tool is implemented,
152:   registered, and callable; a create→get→list→delete(stub)→validate
153:   round-trip against a temp `SPECMGR_FEAT_DIR` succeeds; `list_feat` returns
154:   `PagedResult[FeatSummary]` with default page size 25 / cap 100.
155: - [x] ACC-004: Verifies REQ-006 — `update(type="feat", ...)` and
156:   `set_status(type="feat", ...)` both work end to end (whole-body, line-range,
157:   and status-change modes), preserving `id`/`type`/`created`/`version` and
158:   bumping only `updated`/`status` as appropriate.
159: - [x] ACC-005: Verifies REQ-007 — every listed resource is implemented and
160:   registered (no `/{id}`, no `/list`).
161: - [x] ACC-006: Verifies REQ-008 — both prompts narrate the full
162:   dedup-check → `TodoWrite` → `question`-tool → tool-call-sequence flow,
163:   verified by walking both packaged instruction files end to end against a
164:   real document, not just asserting their static text.
165: - [x] ACC-007: Verifies REQ-009 — `specmgr schema --type feat` and the
166:   generic `specmgr schema` both produce an identical, packaged-copy-matching
167:   `feat_schema.json`.
168: - [x] ACC-008: Verifies REQ-010 — `specmgr docs`/`specmgr mcp-docs`/
169:   `specmgr schema` all report zero drift after implementation; `AGENTS.md`
170:   reflects the new domain; `feat-7-various-improvements` carries the new
171:   Task 0.31 and Task 0.30's background note is extended to mention `feat` as
172:   a fourth divergent `Updates`/`Recent Updates` shape.
173: - [x] ACC-009: Verifies REQ-011 — full unittest suite green; ruff
174:   format/check and vulture clean; `specmgr unused-code` clean.
175: 
176: ### Scope
177: 
178: Included:
179: 
180: - `feat/` domain package (models, tools, resources, prompts, data) built on
181:   the existing `models/md` engine, with its own bespoke folder-per-document
182:   addressing (`feat/tools/_paths.py` et al. — not the shared
183:   `general/tools/_doc_paths.py`).
184: - The frontmatter + body schema in Design Notes below.
185: - Generic `update`/`set_status` dispatch additions (`type="feat"`), no
186:   per-domain `update_feat`/`set_status_feat`.
187: - Cross-cutting registration (server.py, schema command, pyproject,
188:   pre-commit, CI, AGENTS.md, root README.md, generated docs).
189: - One new backlog task in `feat-7-various-improvements` (Task 0.31) tracking
190:   the future migration of existing feature folders.
191: - Tests mirroring `tests/dec/`'s layout.
192: 
193: Explicitly out of scope:
194: 
195: - **Migrating the 17 existing `.specmgr/feat/*/README.md` files** into the
196:   new schema (no `type: feat` field, `feat-8`'s `status: completed` left
197:   as-is). They remain readable as plain markdown but unparseable by
198:   `parse_feat`/`get_feat` (silently skipped by `list_feat`, matching this
199:   codebase's universal skip-on-parse-failure convention) until the new
200:   `feat-7` Task 0.31 does this later. This is a deliberate, user-directed
201:   decision, not an oversight.
202: - **Consolidating `Updates`/`Recent Updates` naming/shape across domains**
203:   (TSK's free-form `## Recent Updates`, DEC's unenforced `## Updates`,
204:   (planned) SOP's ISO8601-enforced `## Updates`, and now `feat`'s
205:   ISO8601-enforced `### Updates` one level deeper) — tracked entirely by the
206:   existing `feat-7-various-improvements` Task 0.30, whose background note
207:   this feature extends to mention `feat` as a fourth variant. No new task,
208:   no consolidation performed here.
209: - Structured modeling of the free-form metadata *inside* each Task List
210:   checklist item (`depends on:`/`status:`/`ETA` annotations) — `#### Phase N`
211:   headings and their flat `- [ ] .../- [x] ...` item lists are now
212:   structurally modeled (see Design Notes), but each item's own text stays an
213:   unparsed `TaskItem` description; per-task metadata edits are still expected
214:   to go through the generic `update` tool's line-range mode, not a dedicated
215:   tool. (Supersedes the earlier "Task List stays a single opaque leaf"
216:   decision — see Decisions Made.)
217: - ADR-style granular `update_section`/option-style per-field mutation tools —
218:   `feat` uses only the generic whole-body/line-range `update` tool.
219: - Real implementation of `delete_feat` — a stub raising
220:   `NotImplementedError`, matching every other domain's `delete_*` stub.
221: - Any changes to the `models/md` engine itself (already supports every shape
222:   needed — `MarkdownSection1`..`6` all exist; if this turns out wrong during
223:   implementation, stop and report rather than patching the engine).
224: - Any changes to any other existing (or planned-but-unimplemented, i.e. sop)
225:   domain's schema, tools, or data.
226: 
227: ### Dependencies
228: 
229: - Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (the governing
230:   `.specmgr/feat/` convention this feature formalizes), ADR
231:   ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy), ADR
232:   bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic `MarkdownFrontmatter` base),
233:   ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads), ADR
234:   ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
235:   resource), ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic
236:   `update`/`set_status` dispatch — `feat` must use these from day one), the
237:   existing `models/md` engine (feat-5, done) and
238:   `general/tools/_packaged_data.py`/`_paging.py`/`_splice.py` infrastructure.
239:   The `### Updates`/`UpdateEntry` ISO8601 shape is copied from
240:   `feat-30-sop`'s **plan** (not its code — `sop` is not yet implemented, this
241:   feature independently implements its own copy one heading level deeper).
242:   ADR 8cf940c5-3100-485c-a12d-14b59b631712 (UUID/flat-file addressing) is
243:   cited as the precedent this feature *deviates from*, not one it follows.
244: - Blocks: `feat-7-various-improvements` Task 0.31 (existing-folder
245:   migration), which cannot start until this feature ships.
246: 
247: ### Design Notes
248: 
249: **Document structure** (section order is binding — field declaration order =
250: markdown order):
251: 
252: ```markdown
253: ---
254: id: feat-NNN-slug       # = containing folder's name; NOT a generated UUID
255: type: feat               # Literal["feat"]
256: created: YYYY-MM-DD
257: updated: YYYY-MM-DD
258: status: planning         # closed 4-set, no hyphens
259: version: 1.0.0
260: ---
261: 
262: # Feature: {Free-form title}                  H1, @alias REGEX "^Feature: .+$"
263: ## Plan                                        REQUIRED (LITERAL alias, composite)
264:   ### Overview                                 REQUIRED (leaf)
265:   ### Requirements                             REQUIRED (regex list, ≥1 item)
266:     - REQ-NNN: {text}                          item @regex "^REQ-\d{3}: .+$"
267:   ### Acceptance Criteria                      REQUIRED (regex checklist, ≥1 item)
268:     - [ ] ACC-NNN: {text}                       item description @regex "^ACC-\d{3}: .+$"
269:   ### Scope                                    REQUIRED (composite, no own text)
270:     #### Included                               REQUIRED (leaf)
271:     #### Explicitly Out Of Scope                REQUIRED (leaf)
272:   ### Dependencies                             OPTIONAL (composite, no own text)
273:     #### Depends On                             OPTIONAL (leaf)
274:     #### Blocks                                 OPTIONAL (leaf)
275:   ### Design Notes                             OPTIONAL (leaf)
276:   ### Related Decisions                        OPTIONAL (leaf)
277:   ### Task List                                REQUIRED (composite, no own text)
278:     #### Phase N: {title}                      ≥1, @regex "^Phase \d+: .+$"
279:     - [ ] Task N.M: {text}                      ≥1 item per phase, opaque TaskItem
280: ## Progress                                    REQUIRED (LITERAL alias, composite)
281:   ### Current Status                           REQUIRED (leaf)
282:   ### Blockers                                 OPTIONAL (leaf)
283:   ### Updates                                  REQUIRED (composite, opt. comment, ISO8601, newest-first enforced)
284:     <!-- optional comment, e.g. ordering hint -->
285:     #### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}   ≥1, newest entry first
286:     {entry prose}
287:   ### Decisions Made                           OPTIONAL (composite, opt. comment, ISO8601, newest-first enforced)
288:     <!-- optional comment, e.g. ordering hint -->
289:     #### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}   ≥1 (if section present), newest entry first
290:     {entry prose}
291:   ### Related PRs / Commits                    OPTIONAL (leaf)
292:   ### More Information                         OPTIONAL (leaf)
293: ```
294: 
295: **Model classes** (all in `feat/models/v1/body.py`, one
296: `MarkdownSection1`/`MarkdownSection2`/`MarkdownSection3`/`MarkdownSection4`
297: subclass per heading; implicit SPACE_SEPARATED aliases unless noted):
298: 
299: - `Feature(MarkdownSection1)` — `@alias(value="^Feature: .+$", type=AliasType.REGEX)`; fields in order: `plan`, `progress`.
300: - `Plan(MarkdownSection2)` — implicit alias "Plan"; fields in order:
301:   `overview`, `requirements`, `acceptance_criteria`, `scope`,
302:   `dependencies | None`, `design_notes | None`, `related_decisions | None`,
303:   `task_list`.
304: - `Overview`, `DesignNotes`, `RelatedDecisions` — bare opaque leaves
305:   (`MarkdownSection3`), implicit SPACE_SEPARATED aliases (RSK's
306:   `Cause`/`Trigger`/GOL's `Description` precedent).
307:   `space_separated_name("RelatedDecisions")` derives exactly `"Related Decisions"`, so no `LITERAL` override is needed here (unlike the
308:   `RelatedAdrs`/`"Related ADRs"` name this replaces, which *did* need
309:   one — see Decisions Made). Renamed from "Related ADRs" to "Related
310:   Decisions" per explicit user direction: this codebase intends to phase
311:   out ADR terminology in favor of `dec` over time, so `feat`'s own new
312:   schema adopts the forward-looking name rather than perpetuating "ADR"
313:   in a brand-new document type; entries may still reference either an
314:   ADR id or a `dec` id (or any other decision record) — the field stays a
315:   free-form cross-reference list, not restricted to one domain's id
316:   format.
317: - `RequirementItem(MarkdownListItem)` — `TaskItem`-style: no declared nested
318:   fields (leaf), a `@computed_field description: str` re-matching
319:   `^REQ-\d{3}: (?P<description>.+)$` against `.text` and raising
320:   `AssertionError` on a malformed item (mirrors `tsk`'s own `TaskItem`
321:   regex-on-`.text` pattern, just without a checkbox marker).
322:   `Requirements(MarkdownSection3)` — implicit alias "Requirements";
323:   `items: list[RequirementItem] = Field(min_length=1)`.
324: - `AcceptanceCriterionItem(TaskItem)` — reuses `tsk.TaskItem`'s
325:   `checked`/`description`-from-checkbox split as-is, adding one more
326:   computed field, `criterion_description: str`, that re-matches
327:   `^ACC-\d{3}: (?P<description>.+)$` against the inherited `description`
328:   and raises `AssertionError` on a malformed item.
329:   `AcceptanceCriteria(MarkdownSection3)` — implicit alias "Acceptance
330:   Criteria"; `items: list[AcceptanceCriterionItem] = Field(min_length=1)`.
331: - `Included`, `ExplicitlyOutOfScope` — bare opaque leaves
332:   (`MarkdownSection4`), implicit SPACE_SEPARATED aliases.
333:   `space_separated_name("ExplicitlyOutOfScope")` derives exactly
334:   `"Explicitly Out Of Scope"` — every word capitalized ("Start Case"),
335:   matching this codebase's own existing multi-word heading style
336:   ("Acceptance Criteria", "Design Notes"), so no `LITERAL` override is
337:   needed (the earlier `"Explicitly out of scope"` sentence-case spelling
338:   — this plan's own pre-existing ad hoc `### Scope` convention — is
339:   dropped in favor of this, per explicit user direction to minimize
340:   `LITERAL` use where it doesn't change the meaning). `Scope (MarkdownSection3)` — implicit alias "Scope", no own text; fields in
341:   order: `included`, `explicitly_out_of_scope` (both mandatory — a
342:   feature must always state both what is included and what is explicitly
343:   excluded).
344: - `Blocks`, `DependsOn` — bare opaque leaves (`MarkdownSection4`),
345:   implicit SPACE_SEPARATED aliases. `space_separated_name("DependsOn")`
346:   derives exactly `"Depends On"` (capitalized "On"), so no `LITERAL`
347:   override is needed (the earlier `"Depends on"` sentence-case spelling
348:   is dropped in favor of this, same rationale as `ExplicitlyOutOfScope`
349:   above; reusing the parent's own name, `"Dependencies"`, for this child
350:   heading was considered and rejected — it would read as a confusing
351:   tautology, `### Dependencies` containing `#### Dependencies`, and the
352:   Python field would awkwardly become `Dependencies.dependencies`).
353:   `Dependencies(MarkdownSection3)` — implicit alias "Dependencies", no
354:   own text; fields in order: `depends_on | None`, `blocks | None` (both
355:   optional — a feature may have no dependencies and block nothing else,
356:   matching `Dependencies` itself already being optional overall).
357: - `Phase(MarkdownSection4)` — `@alias(value=r"^Phase \d+: .+$", type=AliasType.REGEX)` (unpadded phase numbers, matching this very plan's
358:   own "Phase 0".."Phase 5" headings); computed fields `number: int`/
359:   `title: str` extracted from the heading via `^Phase (?P<number>\d+): (?P<title>.+)$` (`UpdateEntry` precedent); `items: list[TaskItem] = Field(min_length=1)` reusing `tsk.models.v1.task_item.TaskItem` as-is for
360:   each phase's own flat `- [ ] .../- [x] ...` checklist — per-item metadata
361:   (`depends on:`/`status:`/`ETA`) stays unparsed free text inside each
362:   item's description (see Scope). `TaskList(MarkdownSection3)` — implicit
363:   alias "Task List", no own text; `phases: list[Phase] = Field(min_length=1)`.
364: - `Progress(MarkdownSection2)` — implicit alias "Progress"; fields in order:
365:   `current_status`, `blockers | None`, `updates`, `decisions_made | None`,
366:   `related_prs_commits | None`, `more_information | None`.
367: - `CurrentStatus`, `Blockers`, `RelatedPrsCommits`, `MoreInformation` — bare
368:   opaque leaves (`MarkdownSection3`), implicit SPACE_SEPARATED aliases
369:   (`RelatedPrsCommits` → "Related PRs / Commits" needs an explicit
370:   `@alias(value="Related PRs / Commits", type=AliasType.LITERAL)` — the
371:   slash/mixed-case breaks the plain SPACE_SEPARATED convention, same
372:   reasoning as SOP's `SafetyAndPrecautions`; `MoreInformation` mirrors
373:   `req`'s/ADR's own `## More Information`, one heading level deeper).
374: - `UpdateEntry(MarkdownSection4)` — `@alias(value=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$", type=AliasType.REGEX)`; `content: MarkdownParagraph` (mandatory lead
375:   paragraph, TSK/DEC shape); computed fields `timestamp: str`/`title: str`
376:   extracted from the heading via `^(?P<timestamp>...) — (?P<title>.+)$`
377:   (DEC `Option`/SOP `Step`/`UpdateEntry` precedent). Format: ISO8601 date +
378:   space + time + milliseconds + explicit UTC offset (`+02:00`, `-05:00`) or
379:   `Z` for UTC — deliberately **not** the same format as frontmatter
380:   `created`/`updated` (plain `YYYY-MM-DD`), matching `feat-30-sop`'s own
381:   stated rationale (this format is scoped to `### Updates` entry headings
382:   only, hand/LLM-authored body content, not tool-generated frontmatter).
383:   Malformed headings raise `AssertionError`.
384: - `DecisionEntry(MarkdownSection4)` — identical shape to `UpdateEntry`
385:   (same alias regex, same `timestamp`/`title` computed-field extraction,
386:   same `content: MarkdownParagraph`) — full ISO8601 timestamp, not
387:   date-only, so same-day entries stay strictly orderable (see the
388:   ordering validator below).
389: - `Updates(MarkdownSection3WithComment)` — implicit alias "Updates";
390:   inherits an optional `comment: MarkdownComment | None` field (`req`'s
391:   `Level`/`Priority` precedent) meant to hold a machine-readable ordering
392:   hint (`feat_template.md`/`feat_example.md` populate it with e.g.
393:   `<!-- Newest entry first -- prepend new entries directly below this comment. -->`); `updates: list[UpdateEntry] = Field(min_length=1)`. One
394:   heading level deeper than `feat-30-sop`'s planned `## Updates`
395:   (`MarkdownSection2`), otherwise identical shape.
396: - `DecisionsMade(MarkdownSection3WithComment)` — implicit alias "Decisions
397:   Made", same optional `comment` field as `Updates`; `decisions: list[DecisionEntry] = Field(min_length=1)`, same "non-`Optional`
398:   `list[X]` implies ≥1 once the section exists" convention as
399:   `Updates.updates`/`TaskList.phases` (`RecentUpdates` precedent).
400:   Optionality lives one level up instead: `Progress.decisions_made: DecisionsMade | None = None` — a brand-new feature has no `### Decisions Made` section at all, rather than an empty one.
401: - **Newest-first ordering, enforced, on both `Updates` and
402:   `DecisionsMade`**: a `@model_validator(mode="after")` on each class
403:   asserts consecutive entries' parsed `datetime.fromisoformat(entry. timestamp)` values are non-increasing (each entry's timestamp \<= the
404:   previous entry's), raising `AssertionError` on the first out-of-order
405:   pair — extending the existing eager-computed-field-validation pattern
406:   (`tsk.models.v1.body.Task._validate_items_eagerly`) to a genuine
407:   cross-item ordering guarantee, not just a documented convention.
408:   Newest-first (not oldest-first/append) was chosen to match the
409:   *existing*, already-tool-supported convention for the ad hoc
410:   `### Recent Updates` this feature formalizes:
411:   `general/data/general_compact_history_instructions.md` (the
412:   `compact_history` prompt) already assumes/states "newest first" for
413:   that section, and prepending new entries at the top keeps the
414:   always-cut-from-the-bottom rotation-into-`history.md` rule simple.
415:   (`tsk_example.md`'s own shipped example already happens to be
416:   newest-first; `dec_example.md`'s is oldest-first — that pre-existing
417:   cross-domain inconsistency is out of scope here, tracked by
418:   `feat-7-various-improvements` Task 0.30; `feat`'s own two sections
419:   define and enforce their own explicit convention instead of inheriting
420:   the ambiguity.)
421: 
422: **Frontmatter**: `FeatFrontmatter(MarkdownFrontmatter)` — `type: Literal["feat"] = "feat"`; closed status set `frozenset({"planning", "progress", "review", "done"})` (GOL/SOP error-message pattern), default
423: `"planning"` (overriding the base's `"draft"` default). No hyphens in any
424: value, per explicit user direction (`"progress"`, not `"in-progress"`).
425: `version` means schema version only (`CURRENT_SCHEMA_VERSION`,
426: machine-managed) — the historical hand-bumped "plan revision" meaning
427: (`feat-4-use-cases` reaching `1.7.0`, `feat-5-md-model-parser` reaching
428: `1.16.4` by hand) is retired for documents created under this schema;
429: revision history is tracked via `created`/`updated` plus git history
430: instead, per user direction. `created`/`updated` stay plain `YYYY-MM-DD`
431: (not the other domains' microsecond `T`-separator timestamp) — matching
432: every one of the 17 existing feature files and ADR e369ee2e's own template,
433: a deliberate divergence from the rest of the codebase's frontmatter
434: timestamp convention.
435: 
436: **Addressing** (the genuinely novel part — see REQ-004):
437: 
438: - `feat/tools/_paths.py` is hand-rolled (ADR-style), not built on
439:   `general/tools/_doc_paths.py`: `feat_base_dir()` reads `SPECMGR_FEAT_DIR`,
440:   falling back to `.specmgr/feat`; `iter_feat_paths()` globs
441:   `<base>/*/README.md`; `find_feat_path_by_id(base_dir, id_)` shortcuts to
442:   `<base>/<id_>/README.md` and verifies the parsed frontmatter `id` matches
443:   (raising `FeatNotFoundError` with a clear message otherwise — no fallback
444:   full-directory scan, since a mismatch means the folder was renamed/copied
445:   incorrectly and should be surfaced, not silently worked around).
446: - `create_feat(content)`: derives the next `NNN` by scanning `feat-*`
447:   folder names under `feat_base_dir()`, taking the max existing `NNN` + 1
448:   (or `1` if none exist) under a **global** `feat_create_lock()` (a single
449:   lock file at `<base>/.create.lock`, distinct from every other domain's
450:   per-id lock, since the id doesn't exist until the scan completes);
451:   slugifies the H1 title (reusing `general/tools/_doc_paths.py::slugify`)
452:   for the folder-name suffix; creates `<base>/feat-<NNN>-<slug>/` and writes
453:   `README.md` inside it.
454: - `list_feat`/`get_feat`/`update`/`set_status` (dispatched via
455:   `type="feat"`) all reuse this same `_paths.py`, plus feat-specific
456:   `_io.py`/`_lock.py` (per-id lock keyed on the full `id`, e.g. a lock file
457:   at `<base>/<id>/.lock`) /`_write.py` mirroring the shape (not the
458:   implementation) of `dec`'s/`gol`'s equivalents.
459: - No partial-id-match support in `find_feat_path_by_id` — e.g. a bare
460:   `"feat-31"` does **not** resolve to `"feat-31-feature"`. Considered and
461:   explicitly rejected (see Decisions Made): an agent that only has a bare
462:   `"feat-31"` can already resolve the real id for free by calling
463:   `list_feat` (whose `FeatSummary` entries carry the real `id`) and
464:   matching the prefix itself, then calling `get_feat` with the resolved
465:   id — the same "list, then resolve, then act" pattern already used
466:   elsewhere in this codebase (e.g. `create_dec`/`create_gol`'s own
467:   dedup-check-first prompts), rather than adding boundary-matching regex,
468:   a new ambiguous-match error type, and a scan fallback to
469:   `find_feat_path_by_id` for a need the existing tools already cover.
470: - `FeatSummary(DocSummary)` adds one extra field beyond the inherited
471:   `id`/`title`/`status`/`ref`: **`path: str`**, the real filesystem path
472:   to the document's `README.md` (e.g.
473:   `.specmgr/feat/feat-31-feature/README.md`; the containing folder is
474:   trivially `Path(path).parent` for a caller that wants to look at
475:   sibling files). This is a deliberate divergence from every other
476:   domain's summary: `DocSummary.ref`'s own docstring states callers "must
477:   not read this off disk themselves, only pass it to the matching
478:   domain's `get_<domain>` tool" — `AdrSummary` enforces the identical
479:   policy, backed by ADR "author and edit ADRs only through MCP structured
480:   tools, never raw markdown." `feat` is the opposite case: ADR
481:   e369ee2e's whole governing convention *is* direct hand/agent markdown
482:   editing of `.specmgr/feat/<id>/README.md`, which remains normal and
483:   sanctioned even after `feat`'s own MCP tools exist — so hiding the path
484:   behind `ref` alone would work against the domain's own intended
485:   workflow. `id`/`ref` stay on `FeatSummary` too (still useful for
486:   `get_feat`/`update`/`set_status` lookups) — `path` is additive, not a
487:   replacement.
488: 
489: **Prompts are narrated instructions only** (return a string, auto-wrapped as
490: a `UserMessage`), same contract as every existing prompt — `create_feat`/
491: `update_feat` never call `TodoWrite`/`question`/`get_feat`/`create_feat`/
492: `update`/`set_status` themselves, they only narrate that the calling LLM
493: should, mirroring `gol`/`dec`/`prb`'s prompts.
494: 
495: **Cross-cutting wiring**: `server.py` (add `feat` to the domain import
496: line + docstring), `commands/schema.py` (`generate_feat_schema()` +
497: `_GENERATORS["feat"]`), `pyproject.toml` (package-data entry for
498: `biz.dfch.specmgr.feat`), `.pre-commit-config.yaml` (`feat/models/v1` added
499: to the schema-hook globs + new `specmgr-schema-feat-package` hook),
500: `.github/workflows/ci.yml` (new packaged-copy drift step), `AGENTS.md` (new
501: `feat/` bullet documenting the addressing deviation explicitly), root
502: `README.md` (add `Feature (FEAT)` — or omit if this is judged an
503: internal/meta artifact type rather than a specification artifact; decide
504: during Phase 5), `general/tools/update.py`/`set_status.py` (`_update_feat`/
505: `_set_status_feat` adapters + `"feat"` dispatch entries, per REQ-006).
506: 
507: **Backlog housekeeping** (part of REQ-010, done in Phase 0, not deferred):
508: add Task 0.31 to `feat-7-various-improvements` (migrate the 17 existing
509: feature folders once this schema exists) and extend that feature's existing
510: Task 0.30 background note (Updates/Recent Updates consolidation) to mention
511: `feat`'s new ISO8601-enforced `### Updates` shape as a fourth divergent
512: variant.
513: 
514: ### Related ADRs
515: 
516: - e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
517:   `.specmgr` with feature-driven work units — the convention this feature
518:   formalizes into a real schema.
519: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
520:   document-type domain (domain-first hierarchy).
521: - bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
522:   markdown document types.
523: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
524:   (`get_feat`), not a resource.
525: - ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
526:   MCP tool (`list_feat`), not a resource.
527: - 36905d5b-8057-4294-8665-c7eed5534db0: Consolidate whole-body update and
528:   status-change tools into generic type-dispatched tools — `feat` uses these
529:   from day one, no `update_feat`/`set_status_feat` of its own.
530: - 8cf940c5-3100-485c-a12d-14b59b631712: id/filename/addressing scheme —
531:   cited as the precedent this feature *deviates from* (non-UUID id,
532:   folder-per-document, fixed filename), not one it follows.
533: 
534: No new ADR is anticipated for the schema/tooling decisions themselves (each
535: follows an existing ADR's precedent or is scoped to this file's own
536: Decisions Made log), **except possibly** for the addressing deviation
537: (REQ-004) if, during implementation, it turns out to have implications
538: beyond this one domain — flagged here, decided in Phase 1/2 if it comes up.
539: 
540: ### Task List
541: 
542: Single, canonical breakdown of work phases and tasks. Status lives on the
543: task itself — there is no separate "planned" vs. "executed" list to keep in
544: sync; a task's line *is* its current status. Update it in place as work
545: progresses (edit, don't duplicate). Each phase ends with a mandatory
546: phase-end task (tests, full quality gate, README Progress update, one
547: commit), mirroring `feat-21-decision`'s/`feat-30-sop`'s per-phase commit
548: discipline.
549: 
550: #### Phase 0: Scaffolding
551: 
552: - [x] Task 0.1: File GitHub issue #31, create branch `feat-31-feature` off
553:   `dev`, write this plan file — depends on: none — status: completed
554:   (2026-08-30)
555: - [x] Task 0.2: Package skeleton — `feat/__init__.py` (`from . import prompts, resources, tools` + registration docstring), empty
556:   `feat/models/v1/`, `feat/tools/`, `feat/resources/`, `feat/prompts/`
557:   packages, and `tests/feat/` skeleton mirroring `tests/dec/` — depends on:
558:   Task 0.1 — status: completed (2026-08-30). `feat/data/` deferred to
559:   Phase 3, which is the first phase that writes anything into it.
560: - [x] Task 0.3: Add Task 0.31 to `feat-7-various-improvements` (migrate
561:   existing feature folders once this schema ships) and extend that
562:   feature's Task 0.30 background note to mention `feat`'s `### Updates`
563:   shape as a fourth divergent variant — depends on: none — status:
564:   completed (2026-08-30)
565: - [x] Task 0.4: Phase-end quality gate + baseline commit + comment the
566:   commit hash on issue #31 — depends on: Task 0.2, Task 0.3 — status:
567:   completed (2026-08-30, commit 31c5c30, issue #31 comment posted)
568: 
569: #### Phase 1: Models + parser (`feat/models/v1/`)
570: 
571: - [x] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on:
572:   Task 0.2 — status: completed (2026-08-30)
573: - [x] Task 1.2: `frontmatter.py` — `FeatFrontmatter(MarkdownFrontmatter)`:
574:   `type: Literal["feat"] = "feat"`, closed 4-set status validator, default
575:   `"planning"` — depends on: Task 1.1 — status: completed (2026-08-30)
576: - [x] Task 1.3: `body.py` — all section classes per Design Notes:
577:   `Feature` (root), `Plan` + its 8 children (`Overview`/`DesignNotes`/
578:   `RelatedDecisions` leaves; `Requirements`/`RequirementItem`,
579:   `AcceptanceCriteria`/`AcceptanceCriterionItem` regex-validated lists;
580:   `Scope`/`Included`/`ExplicitlyOutOfScope`, `Dependencies`/`DependsOn`/
581:   `Blocks` composites (all four implicit-alias, no `LITERAL` needed);
582:   `TaskList`/`Phase` dynamic-list composite reusing
583:   `tsk.TaskItem`), `Progress` + its 6 children (`CurrentStatus`/`Blockers`/
584:   `RelatedPrsCommits`/`MoreInformation` leaves; `Updates`/`UpdateEntry`,
585:   `DecisionsMade`/`DecisionEntry` dynamic-list composites) — depends on:
586:   Task 1.2 — status: completed (2026-08-30). Added one judgment call not
587:   spelled out verbatim in Design Notes: `Requirements`/`AcceptanceCriteria`/
588:   `Phase` each gained their own eager-computed-field-validation
589:   `model_validator`, mirroring `tsk.models.v1.body.Task._validate_items_eagerly`
590:   exactly, so a malformed `REQ-\d{3}: .../ACC-\d{3}: .../- [z] ...` item
591:   raises immediately at parse time instead of only whenever something
592:   later happens to read the offending computed field — see Decisions Made.
593: - [x] Task 1.4: `document.py` (`FeatDocument`), `parser.py` (`parse_feat`
594:   glue), `summary.py` (`FeatSummary(DocSummary)` — adds one extra field,
595:   `path: str`, beyond the inherited `id`/`title`/`status`/`ref`; see
596:   Design Notes' Addressing section and Decisions Made for why `feat`
597:   needs this and every other domain's summary deliberately doesn't),
598:   `models/v1/__init__.py` - `models/__init__.py` exports — depends on:
599:   Task 1.3 — status: completed (2026-08-30)
600: - [x] Task 1.5: Reference fixture `feat_reference.md`, **seeded from this
601:   feature's own `.specmgr/feat/feat-31-feature/example.md`** (the
602:   canonical, engine-verified example — see Current Status/Decisions Made;
603:   do not re-derive the schema from scratch or restart from
604:   `feat_template.md`) — adjusted only as needed to exercise every field
605:   (all optional sections present, ≥2 `### Updates` entries and ≥2
606:   `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`
607:   entries each with ≥1 task item), all well-formed, exercising the
608:   ISO8601 regex on both `Updates` and `Decisions Made` — depends on: Task
609:   1.3 — status: completed (2026-08-30), at
610:   `tests/feat/models/v1/data/feat_reference.md` (mirroring the
611:   `tests/models/adr/v1/examples/` file-fixture-on-disk convention, since
612:   `tests/dec/models/v1/` itself keeps its reference text inline in
613:   `test_body.py`/`test_parser.py`, not as a separate file — see Decisions
614:   Made). Two small, content-preserving adjustments were needed beyond
615:   "seeded from `example.md`": every bullet/checklist list gained a blank
616:   line between items (a loose list) to sidestep `MarkdownListItem`'s own
617:   documented tight-list round-trip quirk (`dec`'s own reference text
618:   already uses the same loose-list workaround), and Task 0.1's item text
619:   had its trailing `— status: completed (2026-08-30)` suffix dropped so
620:   the item stays on one physical line (`TaskItem`'s marker regex does not
621:   span embedded newlines) — see Decisions Made.
622: - [x] Task 1.6: Tests `tests/feat/models/v1/` — `test_frontmatter.py`
623:   (4-set status incl. rejection), `test_body.py` (alias acceptance/
624:   rejection incl. the `### Updates` ISO8601 regex, mandatory-vs-optional
625:   field combinations), `test_parser.py` (ACC-001 matrix + round-trip) —
626:   depends on: Task 1.4, Task 1.5 — status: completed (2026-08-30), 99 new
627:   tests (11 `test_frontmatter.py` + 70 `test_body.py` + 18 `test_parser.py`).
628: - [x] Task 1.7: Phase-end quality gate + commit + comment on issue #31 —
629:   depends on: Task 1.6 — status: completed (2026-08-30) — quality gate
630:   green; **commit and issue comment left to the orchestrator**, per this
631:   phase's own task instructions (implementer runs the gate only).
632: 
633: #### Phase 2: Tools (`feat/tools/`) — bespoke addressing
634: 
635: - [x] Task 2.1: `_paths.py` (`feat_base_dir`, `iter_feat_paths`,
636:   `find_feat_path_by_id`, `FeatNotFoundError`, `FEAT_TYPE_NAME = "feat"`,
637:   `slugify` reuse) per Design Notes' Addressing section — depends on: Task
638:   1.4 — status: completed (2026-08-30). Also added `feature_title()` (strips
639:   the literal `"Feature: "` prefix off `Feature.text`, see Decisions Made)
640:   and `FEAT_FOLDER_PATTERN`/`README_FILENAME` constants, none spelled out
641:   verbatim in the task but needed by `create_feat`/`list_feat` in Task 2.3.
642: - [x] Task 2.2: `_lock.py` (per-id `feat_lock(id_)` + global
643:   `feat_create_lock()`), `_io.py` (`read_feat`, `load_by_id`), `_write.py`
644:   (`write_feat_file`, creates the `<id>/` folder if missing) — depends on:
645:   Task 2.1 — status: completed (2026-08-30). Both locks are in-process
646:   `threading.Lock` instances (see Decisions Made — the plan's own prose
647:   mentioning "a single lock file at `<base>/.create.lock`" was not
648:   followed, for consistency with every other domain's precedent).
649: - [x] Task 2.3: The 8 tool modules + `tools/__init__.py`: `create_feat`
650:   (next-`NNN` derivation under the global lock), `parse_feat`, `list_feat`
651:   (`PagedResult[FeatSummary]`), `get_feat(id, raw=False)`,
652:   `get_feat_example`/`get_feat_template`, `delete_feat` (stub,
653:   `structured_output=False`), `validate_feat` — depends on: Task 2.2 —
654:   status: completed (2026-08-30). `get_feat_example`/`get_feat_template`
655:   are wired to `read_packaged_text("feat", "example"/"template")` exactly
656:   like every other domain, but the packaged files themselves don't exist
657:   until Phase 3 (Task 3.1/3.2) — both tools currently raise
658:   `FileNotFoundError` when actually called; see Decisions Made.
659: - [x] Task 2.4: `general/tools/update.py`/`set_status.py` — add
660:   `_update_feat`/`_set_status_feat` adapters + `"feat"` dispatch table
661:   entries, built on Task 2.1/2.2's helpers — depends on: Task 2.2 —
662:   status: completed (2026-08-30). Both adapters bump `updated` to a plain
663:   `YYYY-MM-DD` date (`datetime.now().date().isoformat()`), not the other
664:   eight/nine domains' microsecond timestamp, matching `create_feat`'s own
665:   frontmatter convention. Also updated one pre-existing test
666:   (`tests/general/tools/test_update.py::TestUpdateRegistration`) whose
667:   hardcoded 8-value `type` enum assertion needed `"feat"` added, now that
668:   the live `update` tool's registered schema carries 9 values.
669: - [x] Task 2.5: Tests `tests/feat/tools/` — one module per tool + helper
670:   tests + `test_integration.py` (ACC-003/ACC-004, incl. concurrent-create
671:   `NNN`-collision simulation) — depends on: Task 2.3, Task 2.4 — status:
672:   completed (2026-08-30), 73 new tests (`test__paths.py`/`test__lock.py`/
673:   `test__io.py`/`test__write.py`/`test_create_feat.py`/`test_get_feat.py`/
674:   `test_list_feat.py`/`test_parse_feat.py`/`test_validate_feat.py`/
675:   `test_delete_feat.py`/`test_get_feat_example.py`/
676:   `test_get_feat_template.py`/`test_integration.py`), plus the one
677:   pre-existing test file updated in Task 2.4.
678: - [x] Task 2.6: Phase-end quality gate + commit + comment on issue #31 —
679:   depends on: Task 2.5 — status: completed (2026-08-30) — quality gate
680:   green; **commit and issue comment left to the orchestrator**, per this
681:   phase's own task instructions (implementer runs the gate only).
682: 
683: #### Phase 3: Resources + packaged data + schema
684: 
685: - [x] Task 3.1: `feat/data/feat_example.md` (byte-identical copy of
686:   `feat_reference.md`, DEC/GOL precedent) — depends on: Task 2.6 — status:
687:   completed (2026-08-30)
688: - [x] Task 3.2: `feat/data/feat_template.md` — all-sections placeholder
689:   skeleton, `status: planning`; must round-trip through `parse_feat` —
690:   depends on: Task 2.6 — status: completed (2026-08-30)
691: - [x] Task 3.3: `feat/data/feat_create_instructions.md` +
692:   `feat_update_instructions.md` — depends on: Task 2.6 — status:
693:   completed (2026-08-30)
694: - [x] Task 3.4: `commands/schema.py` — `generate_feat_schema()` +
695:   `_GENERATORS["feat"]`; run `specmgr schema --type feat` (writes
696:   `docs/feat_schema.json`) and the packaged-copy variant — depends on:
697:   Task 1.4 — status: completed (2026-08-30), `_GENERATORS` entry inserted
698:   alphabetically (`dec`, `feat`, `gol`, ...); both invocations produce
699:   byte-identical output, confirmed via `diff`.
700: - [x] Task 3.5: `feat/resources/` — `feat_schema.py`, `feat_example.py`,
701:   `feat_template.py`, `__init__.py` — depends on: Task 3.1, Task 3.2, Task
702:   3.4 — status: completed (2026-08-30)
703: - [x] Task 3.6: Tests `tests/feat/resources/` (ACC-005/ACC-007) — depends
704:   on: Task 3.5 — status: completed (2026-08-30), 20 new tests
705:   (`test_feat_schema.py`/`test_feat_example.py`/`test_feat_template.py`);
706:   also replaced the two Phase-2-deferred `FileNotFoundError`-only tests
707:   (`tests/feat/tools/test_get_feat_example.py`/
708:   `test_get_feat_template.py`) with real "returns the packaged file"
709:   happy-path assertions, mirroring `test_get_dec_example.py`/
710:   `test_get_dec_template.py`.
711: - [x] Task 3.7: Phase-end quality gate + commit + comment on issue #31 —
712:   depends on: Task 3.6 — status: completed (2026-08-30) — quality gate
713:   green; **commit and issue comment left to the orchestrator**, per this
714:   phase's own task instructions (implementer runs the gate only).
715: 
716: #### Phase 4: Prompts
717: 
718: - [x] Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`),
719:   `update_feat.py` (`update_feat(id, instructions=None)`), `__init__.py`
720:   — depends on: Task 3.3 — status: completed (2026-08-30). Both are thin
721:   `string.Template` wrappers around the Phase-3 packaged instructions
722:   files, 1:1 mirrors of `dec.prompts.create_dec`/`update_dec` — neither
723:   calls `TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/
724:   `update`/`set_status` itself.
725: - [x] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
726:   4.1 — status: completed (2026-08-30), 29 new tests
727:   (`test_create_feat.py`/`test_update_feat.py`), including a real
728:   "walk the instructions end to end" test per prompt (ACC-006) against a
729:   temporary `SPECMGR_FEAT_DIR` — see Decisions Made for the fallback
730:   string judgment call.
731: - [x] Task 4.3: Phase-end quality gate + commit + comment on issue #31 —
732:   depends on: Task 4.2 — status: completed (2026-08-30) — quality gate
733:   green; **commit and issue comment left to the orchestrator**, per this
734:   phase's own task instructions (implementer runs the gate only).
735: 
736: #### Phase 5: Cross-cutting registration
737: 
738: - [x] Task 5.1: `server.py` — add `feat` to the domain import line +
739:   module docstring — depends on: Task 4.3 — status: completed
740:   (2026-08-30). Alphabetical import order (`adr, dec, feat, general, gol,
741:   prb, qa, req, rsk, tsk, uc`); the module docstring gained a
742:   `specmgr://feat/schema`/`/example`/`/template` Resources block (same
743:   position as `dec`'s own block, right before it in the file), a "FEAT has
744:   no `specmgr://feat/{id}` ... no `specmgr://feat/list`" sentence appended
745:   to the "DEC has no ..." paragraph, a new "Feature tools (`feat/tools/`)"
746:   paragraph in Tools (mirroring "Decision tools", plus one extra sentence
747:   noting `feat`'s bespoke addressing and its lack of
748:   `update_feat`/`set_status_feat` of its own), the `update`/`set_status`
749:   paragraphs' domain counts bumped from eight/nine to nine/ten
750:   whole-body/total domains (matching `general/tools/update.py`'s/
751:   `set_status.py`'s own docstrings, both already updated in Phase 2), a
752:   new "Feature prompts (`feat/prompts/`)" paragraph in Prompts (mirroring
753:   "Decision prompts"), and `feat` inserted into both domain-enumeration
754:   sentences ("Modules are grouped domain-first ..." and "Add a new domain
755:   by ...") plus the final "each register `tools`, `resources`, and
756:   `prompts`" sentence.
757: - [x] Task 5.2: `pyproject.toml` package-data entry; `.pre-commit-config.yaml`
758:   (`feat/models/v1` added to schema-hook globs + new
759:   `specmgr-schema-feat-package` hook); `.github/workflows/ci.yml` (new
760:   packaged-copy drift step) — depends on: Task 3.4 — status: completed
761:   (2026-08-30). `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]`
762:   added alphabetically between `dec` and `gol`. `feat/models/v1` added to
763:   the one shared `files:` regex glob in all 9 pre-existing occurrences
764:   (verified 9 before, 9 after) plus a new 10th occurrence in the new
765:   `specmgr-schema-feat-package` hook itself (mirroring
766:   `specmgr-schema-dec-package` verbatim, placed last, matching this
767:   file's insertion-order — not alphabetical — convention for per-domain
768:   hooks). CI gained a `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` ``
769:   drift step, same `if: matrix.python-version == '3.13'` guard and error-
770:   message format as the `dec` step, placed immediately after it.
771: - [x] Task 5.3: `AGENTS.md` — new `feat/` bullet documenting the addressing
772:   deviation explicitly (non-UUID id, folder-per-document, bespoke
773:   `_paths.py`); update the domain-enumeration sentences; decide (and note)
774:   whether root `README.md`'s artifact list gains `Feature (FEAT)` — depends
775:   on: Task 5.1 — status: completed (2026-08-30). New `feat/` bullet added
776:   between the `dec/` and `general/` bullets, same depth/style as `dec/`'s
777:   own; the `general/` bullet's domain counts bumped eight→nine/nine→ten;
778:   `delete_*`/`validate_*` enumeration lists, the domain-register-all-three
779:   sentence, and the `server.py`-description sentence in "MCP server
780:   (server.py)" all gained `feat`/`delete_feat`/`validate_feat`. Root
781:   `README.md`: added `Feature (FEAT)` to the active bulleted list
782:   (alphabetically between `Decision (DEC)` and `Goal (GOL)`), removed
783:   `Feature (FTR)` from the commented-out placeholder (wrong abbreviation
784:   besides being redundant now), and moved `Risk (RSK)` — already a fully
785:   implemented domain per `AGENTS.md`'s own `rsk/` bullet — from the
786:   placeholder into the active list as a drive-by fix, leaving only
787:   `Acceptance Criterium (ACC)` (not yet implemented) commented out. See
788:   Decisions Made for the full reasoning.
789: - [x] Task 5.4: Regenerate `docs/MCP.md`/`docs/GENERATED.md`/`docs/api/`/
790:   `docs/feat_schema.json`; confirm all idempotent on a second run — depends
791:   on: Task 5.1, Task 5.2 — status: completed (2026-08-30). `specmgr docs`
792:   changed only `docs/api/biz.dfch.specmgr.server.md` (the Task 5.1
793:   docstring changes); `specmgr mcp-docs` produced no diff at all (FEAT's
794:   tools/resources/prompts were already fully registered before this
795:   phase, so `docs/MCP.md` was already current); `specmgr schema` (all
796:   types) and `specmgr schema --type feat --output-dir
797:   src/biz/dfch/specmgr/feat/data` both reported every file "unchanged".
798:   Every one of the four commands was run a second time immediately after
799:   and produced byte-identical output/no further `git diff` — confirmed
800:   idempotent.
801: - [x] Task 5.5: Final verification pass — walk every ACC-001..009 with
802:   concrete evidence; full quality gate end to end; set feature status to
803:   `done` — depends on: Phase 0-4 complete, Task 5.4 — status: completed

(Output capped at 50 KB. Showing lines 1-803. Use offset=804 to continue.)
</content>
````

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.8s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md",
  "offset": 803
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
803:   `done` — depends on: Phase 0-4 complete, Task 5.4 — status: completed
804:   (2026-08-30). Full quality gate green: `ruff format --check` (1286
805:   files already formatted), `ruff check` (all checks passed), `vulture
806:   src/ whitelist.py --min-confidence 60` (clean), full `unittest` suite
807:   (2228 tests, OK; 221 of them under `tests/feat/` specifically), `specmgr
808:   unused-code` (no unused code found). See Recent Updates for the
809:   ACC-by-ACC evidence walkthrough. Frontmatter `status` set to `done`.
810: - [x] Task 5.6: Final commit + comment on issue #31; update this README's
811:   Progress section — depends on: Task 5.5 — status: **README Progress
812:   section updated by the implementing agent (2026-08-30); commit and
813:   issue #31 comment intentionally left to the orchestrator**, per this
814:   task's own instructions to the implementing agent.
815: 
816: #### Phase 6: Frontmatter timestamp format fix
817: 
818: - [ ] Task 6.1: Change `feat` frontmatter's `created`/`updated` fields
819:   from plain `YYYY-MM-DD` dates to microsecond timestamps
820:   (`datetime.now().isoformat(timespec="microseconds")`), matching every
821:   other whole-body domain's own convention (`req`/`uc`/`tsk`/`qa`/`prb`/
822:   `gol`/`rsk`/`dec`). Affects `feat/tools/create_feat.py` (frontmatter
823:   construction), `general/tools/update.py`'s `_update_feat` adapter,
824:   `general/tools/set_status.py`'s `_set_status_feat` adapter, the Design
825:   Notes' "Frontmatter" section (which currently documents the plain-date
826:   divergence as deliberate), and any tests asserting the plain-date
827:   format (`tests/feat/tools/test_create_feat.py`,
828:   `tests/feat/tools/test_integration.py`, `tests/general/tools/`
829:   equivalents if any). This reverses this feature's own earlier
830:   deliberate design decision (see Decisions Made) — reversing it needs
831:   the same care as the original decision: update the Decisions Made log
832:   with a new entry explaining why, not just silently change the code —
833:   depends on: Phase 5 complete — status: not-started
834: 
835: **Note:** If a task's scope changes mid-flight, edit its description in
836: place; rely on git history (`git log -p` on this file) to recover what was
837: originally planned, rather than keeping a second copy of the task around.
838: 
839: ## Progress
840: 
841: ### Current Status
842: 
843: **As of 2026-08-30 (Phase 6 recorded, not started)**: A new `#### Phase
844: 6: Frontmatter timestamp format fix` has been added to the Task List
845: (Task 6.1, not-started) to reverse this feature's own earlier deliberate
846: divergence and switch `feat` frontmatter's `created`/`updated` fields
847: from plain `YYYY-MM-DD` dates to microsecond timestamps, matching every
848: other whole-body domain. This is planning/recording only — no
849: `src`/`tests` code has been touched. The feature's frontmatter `status`
850: has reverted from `done` to `in-progress` to reflect this new,
851: not-yet-started follow-up work.
852: 
853: **As of 2026-08-30**: Phase 0 (Scaffolding) committed — GitHub issue #31
854: filed, branch `feat-31-feature` created off `dev`, this plan written and
855: reviewed with the user across several rounds (body-modeling depth,
856: addressing scheme, frontmatter `version` semantics, status vocabulary,
857: `Updates` shape/naming, MCP surface scope, no-migration decision, branch
858: naming, feat-7 backlog entry); package skeleton
859: (`feat/{models/v1,tools,resources,prompts}`, `tests/feat/{models/v1, tools,resources,prompts}`) in place; `feat-7-various-improvements` Task 0.31
860: added and Task 0.30 extended. Full quality gate green (2007 tests, ruff
861: format/check clean, vulture clean). Committed as 31c5c30/164182e. **Paused
862: here, deliberately**: implementation was not what was asked for at this
863: point — the design (schema, addressing scheme, MCP surface) needs a review
864: pass by the user first, who may request adjustments, before Phase 1 (or any
865: further phase) starts. See Blockers.
866: 
867: A second design-review round produced a full worked example of the
868: proposed document structure, refined through two further review rounds
869: (ordering/comment/hyperlink questions; LITERAL-alias elimination) into
870: `.specmgr/feat/feat-31-feature/example.md` — not consumed by any code.
871: That round's resolved questions are folded into this plan's Design
872: Notes/Decisions Made above; the Blocker below still applies (no
873: `src`/`tests` code yet, but the Design Notes themselves have now had
874: four review passes).
875: 
876: **`.specmgr/feat/feat-31-feature/example.md` is the canonical,
877: implementation-ready worked example** — every design decision through the
878: fourth review round is reflected in it, and it has been cross-checked
879: against the live `models/md` engine (not just eyeballed): every implicit
880: `SPACE_SEPARATED` heading alias in the design was run through
881: `space_separated_name()` directly, which is what caught the three
882: `RelatedAdrs`/`ExplicitlyOutOfScope`/`DependsOn` issues recorded in
883: Decisions Made above. **Task 1.5 in the Task List explicitly instructs
884: the implementing agent to seed `feat_reference.md` from this file** —
885: this is a load-bearing pointer, not just narrative context, since Task
886: 1.5 is what an agent executing Phase 1 actually follows. The two
887: superseded review-process drafts (`example-initial.md`,
888: `example-revised.md`) have been removed — this is now the only example
889: file in this feature's own folder.
890: 
891: **Design review is complete, as of 2026-08-30, after five review
892: rounds.** The Blocker below is resolved — Phase 1 is authorized to
893: start. Frontmatter `status` moved from `planning` to `in-progress`
894: accordingly. **Implementation itself is explicitly deferred to a
895: separate session/agent (e.g. a Phase-Orchestrator-style agent driving
896: the Task List phase by phase)** — this design-review session closes
897: here without touching any `src`/`tests` code; Phase 0's committed
898: scaffold (`31c5c30`, `164182e`) stays exactly as-is, untouched, ready
899: for whichever agent picks up Task 1.1 next.
900: 
901: **As of 2026-08-30 (Phase 1 complete)**: `feat/models/v1/` is fully
902: implemented per Design Notes — `_util.py`, `frontmatter.py`
903: (`FeatFrontmatter`), `body.py` (`Feature`/`Plan`/`Progress` and every
904: child section class), `document.py` (`FeatDocument`), `parser.py`
905: (`parse_feat`), `summary.py` (`FeatSummary`), plus `models/v1/__init__.py`/
906: `models/__init__.py` exports. Reference fixture
907: `tests/feat/models/v1/data/feat_reference.md` seeded from `example.md`
908: (two small, content-preserving adjustments — loose lists, one shortened
909: task item — see Task 1.5/Decisions Made). 99 new tests
910: (`test_frontmatter.py`/`test_body.py`/`test_parser.py`) all green. Full
911: quality gate green: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean (after adding the new
912: `feat`-only field names and `_validate_newest_first`/
913: `_default_blank_status_to_planning` to `whitelist.py`, same pattern as
914: every other domain's pydantic-field/validator false positives),
915: `specmgr unused-code` clean, full `unittest` suite green (2106 tests).
916: Phase 2 (`feat/tools/`) is next.
917: 
918: **As of 2026-08-30 (Phase 2 complete)**: `feat/tools/` is fully
919: implemented — hand-rolled `_paths.py` (`feat_base_dir`/`ensure_feat_base_dir`,
920: `iter_feat_paths`, `find_feat_path_by_id`'s no-scan shortcut,
921: `FeatNotFoundError`, `feature_title()`, `FEAT_FOLDER_PATTERN`), `_lock.py`
922: (per-id `feat_lock` + global `feat_create_lock`), `_io.py` (`read_feat`,
923: `load_by_id`), `_write.py` (`write_feat_file`, folder-creating), and all 8
924: lifecycle tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`,
925: `get_feat_example`, `get_feat_template`, `delete_feat` stub, `validate_feat`)
926: plus `tools/__init__.py`. `general/tools/update.py`/`set_status.py` gained
927: `_update_feat`/`_set_status_feat` adapters and `"feat"` dispatch entries
928: (REQ-006) — `feat` is now a 9th `update` domain and a 10th `set_status`
929: domain, both with the same plain-date `updated` divergence `create_feat`
930: established. A full live create→get→list→update(whole-body)→
931: update(line-range)→set_status→get→list→validate→delete(stub) round-trip and
932: a 20-thread concurrent-create collision test both pass
933: (`tests/feat/tools/test_integration.py`). 73 new tests across
934: `tests/feat/tools/` (all green), plus one pre-existing test
935: (`tests/general/tools/test_update.py::TestUpdateRegistration`) updated for
936: the now-9-value `type` enum. Full quality gate green: `ruff format --check`/
937: `ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean
938: (no new whitelist entries needed — every new tool function is reachable via
939: its domain's own `tools/__init__.py` `__all__` export, same as every other
940: domain), `specmgr unused-code` clean, full `unittest` suite green (2179
941: tests, up from 2106 after Phase 1). Phase 3 (resources + packaged data +
942: schema) is next — in
943: particular, `feat/data/feat_example.md`/`feat_template.md` (Task 3.1/3.2),
944: which `get_feat_example`/`get_feat_template` are already wired to read but
945: which don't exist on disk yet (both currently raise `FileNotFoundError`
946: when actually called; `tests/feat/tools/test_get_feat_example.py`/
947: `test_get_feat_template.py` document this explicitly and should be revisited
948: once Phase 3 ships those files).
949: 
950: **As of 2026-08-30 (Phase 3 complete)**: `feat/data/` and `feat/resources/`
951: are fully implemented — `feat_example.md` (byte-identical copy of
952: `tests/feat/models/v1/data/feat_reference.md`), `feat_template.md`
953: (all-sections placeholder skeleton, `status: planning`, round-trips
954: through `parse_feat`), `feat_create_instructions.md`/
955: `feat_update_instructions.md` (narrated instruction bodies for the
956: Phase-4 prompts, tailored to `feat`'s own schema/status set/no-
957: `update_feat`-of-its-own MCP surface), and `feat_schema.json` (both
958: `docs/feat_schema.json` and the packaged `feat/data/feat_schema.json`
959: copy, byte-identical, confirmed via `diff`). `commands/schema.py` gained
960: `generate_feat_schema()` and a `"feat"` entry in `_GENERATORS` (inserted
961: alphabetically between `"dec"` and `"gol"`). `feat/resources/` gained
962: `feat_schema.py`/`feat_example.py`/`feat_template.py`/`__init__.py`,
963: registering `specmgr://feat/schema`/`specmgr://feat/example`/
964: `specmgr://feat/template` (no `/{id}`, no `/list`), each a 1:1 mirror of
965: `dec.resources`' own three modules. The two Phase-2-deferred tool tests
966: (`tests/feat/tools/test_get_feat_example.py`/
967: `test_get_feat_template.py`) were updated to assert the real packaged-file
968: happy path instead of `FileNotFoundError`, now that the packaged files
969: exist. 20 new tests across `tests/feat/resources/` (all green), including
970: a byte-exact match between `specmgr://feat/example`'s output and the
971: Phase-1 reference fixture, a fresh-`generate_feat_schema()` parity check,
972: and a `parse_feat` structural round-trip for the template. Full quality
973: gate green: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean (no new whitelist entries needed),
974: `specmgr unused-code` clean, full `unittest` suite green (2199 tests, up
975: from 2179 after Phase 2). Phase 4 (`feat/prompts/`) is next.
976: 
977: **As of 2026-08-30 (Phase 4 complete)**: `feat/prompts/` is fully
978: implemented — `create_feat.py` (`create_feat(topic)`), `update_feat.py`
979: (`update_feat(id, instructions=None)`), `__init__.py`, each a 1:1 mirror
980: of `dec.prompts.create_dec`/`update_dec`: thin `string.Template` wrappers
981: that read the already-existing Phase-3 packaged instructions files
982: (`feat_create_instructions.md`/`feat_update_instructions.md`) and
983: substitute `$topic` / `$id`+`$instructions`, never calling
984: `TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/`update`/
985: `set_status` themselves. `update_feat`'s missing-`instructions` fallback
986: is the literal string `"(not given)"` (not DEC's longer
987: `"(not given -- ask the user before making any change)"`), matching
988: `feat_update_instructions.md`'s own step 2 check verbatim (`If "Requested
989: change" above says "(not given)"...`). 29 new tests across
990: `tests/feat/prompts/` (`test_create_feat.py`/`test_update_feat.py`), all
991: green: static string-content/ordering assertions mirroring
992: `tests/dec/prompts/`'s own depth, plus one "walk the instructions end to
993: end" test per prompt (ACC-006) that drives the real
994: `create_feat`/`get_feat`/`list_feat`/`update`/`set_status` tools against
995: a temporary `SPECMGR_FEAT_DIR` — `TestCreateFeatInstructionsWalkthrough`
996: follows step 0 (dedup check via `list_feat`) and step 4 (`create_feat`)
997: literally; `TestUpdateFeatInstructionsWalkthrough` creates a real
998: document, then follows `get_feat` → line-range `update` → whole-body
999: `update` → `set_status` exactly as the packaged update instructions
1000: narrate, asserting the end state (status `progress`, 2 Requirements
1001: items, id/created preserved). `tests/dec/prompts/` itself does not do
1002: this deeper walk-through (static-text assertions only), so this is new
1003: depth introduced for `feat` specifically, per ACC-006's explicit
1004: requirement. `feat/__init__.py`'s module docstring updated to reflect
1005: Phase 4 completion (only Phase 5 cross-cutting registration remains).
1006: Full quality gate green: `ruff format --check`/`ruff check` clean,
1007: `vulture src/ whitelist.py --min-confidence 60` clean (no new entries
1008: needed), `specmgr unused-code` clean, full `unittest` suite green (2228
1009: tests, up from 2199 after Phase 3). Phase 5 (cross-cutting registration)
1010: is next.
1011: 
1012: **As of 2026-08-30 (Phase 5 complete — feature done)**: Cross-cutting
1013: registration is complete and this feature is **done**. `server.py` gained
1014: `feat` in the domain import line and a full set of module-docstring
1015: updates (Resources block, "no `/{id}`/no `/list`" sentence, Tools
1016: paragraph, Prompts paragraph, both `update`/`set_status` count bumps,
1017: both domain-enumeration sentences). `pyproject.toml`/
1018: `.pre-commit-config.yaml`/`.github/workflows/ci.yml` all gained their
1019: `feat` entries (package-data, schema-hook globs + new
1020: `specmgr-schema-feat-package` hook, CI drift step). `AGENTS.md` gained a
1021: new `feat/` bullet plus every other domain-enumeration sentence updated;
1022: root `README.md` gained `Feature (FEAT)` in its active artifact list and
1023: (drive-by fix) `Risk (RSK)` moved out of the commented-out placeholder
1024: alongside it, leaving only the not-yet-implemented `Acceptance Criterium
1025: (ACC)` commented out (see Decisions Made). `specmgr docs`/`specmgr
1026: mcp-docs`/`specmgr schema` (both invocations) were each run twice in a
1027: row and confirmed idempotent — only `docs/api/biz.dfch.specmgr.server.md`
1028: changed (from the `server.py` docstring edits themselves); `docs/MCP.md`
1029: had zero diff, since every FEAT tool/resource/prompt was already fully
1030: registered before this phase. Every ACC-001..009 was walked with concrete
1031: evidence (tests, generated docs, live command output — see this update's
1032: own detail below) and all nine are satisfied. Full quality gate green:
1033: `ruff format --check` (1286 files already formatted), `ruff check` (all
1034: checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean),
1035: full `unittest` suite (2228 tests, OK, unchanged from Phase 4 — Phase 5
1036: touched no `src/biz/dfch/specmgr/feat/` or `tests/feat/` code, only
1037: cross-cutting registration files), `specmgr unused-code` (clean).
1038: Frontmatter `status` set to `done`. **Per this phase's own task
1039: instructions, no commit was made and no comment was posted to issue
1040: #31** — that is the orchestrator's responsibility for this run, not the
1041: implementing agent's.
1042: 
1043: ### Blockers
1044: 
1045: - [x] Design review — resolved 2026-08-30. Reviewed across five rounds
1046:   (body-modeling depth; Task List/Scope/Dependencies/Decisions Made
1047:   structure; ordering/comment/hyperlink questions; LITERAL-alias
1048:   elimination; partial-id-match/env-var/FeatSummary-path questions).
1049:   Approved as final; see Decisions Made for the complete decision log.
1050:   Phase 0's committed scaffold (`31c5c30`, `164182e`) stays as-is — no
1051:   revert/rebase/rewrite performed or needed. No blockers remain; Phase 1
1052:   is authorized to start (by a separate implementing agent/session, not
1053:   as part of this design-review conversation).
1054: 
1055: ### Recent Updates
1056: 
1057: #### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)
1058: 
1059: - Added a new `#### Phase 6: Frontmatter timestamp format fix` to the
1060:   Task List, with one new task, **Task 6.1** (not-started): change
1061:   `feat` frontmatter's `created`/`updated` fields from plain
1062:   `YYYY-MM-DD` dates to microsecond timestamps
1063:   (`datetime.now().isoformat(timespec="microseconds")`), matching every
1064:   other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/
1065:   `dec`) already in use — reversing this feature's own earlier
1066:   deliberate divergence documented in Design Notes' "Frontmatter"
1067:   section and in Decisions Made. The task calls out the affected files
1068:   (`feat/tools/create_feat.py`, `general/tools/update.py`'s
1069:   `_update_feat` adapter, `general/tools/set_status.py`'s
1070:   `_set_status_feat` adapter, the Design Notes prose, and the tests
1071:   asserting the plain-date format) and requires a new Decisions Made
1072:   entry when the reversal is actually implemented, not a silent code
1073:   change.
1074: - Frontmatter `status` reverted from `done` to `in-progress` and
1075:   `version` bumped from `1.11.0` to `1.12.0` to reflect this new,
1076:   not-yet-started follow-up item.
1077: - **This is planning/recording only — no `src`/`tests` code was
1078:   touched.** Task 6.1 remains not-started; implementation is deferred to
1079:   a future session.
1080: 
1081: #### Update 2026-08-30 (Phase 5 complete — cross-cutting registration; feature done)
1082: 
1083: - **`server.py` (Task 5.1)**: added `feat` to the domain import line
1084:   (alphabetical: `adr, dec, feat, general, gol, prb, qa, req, rsk, tsk,
1085:   uc`). Module docstring gained: a `specmgr://feat/schema`/`/example`/
1086:   `/template` Resources block placed right after the `dec` block (same
1087:   relative position `feat` occupies in the domain-enumeration
1088:   elsewhere); a "FEAT has no `specmgr://feat/{id}` ... no
1089:   `specmgr://feat/list`" sentence appended to the "DEC has no ..."
1090:   paragraph; a new "Feature tools (`feat/tools/`)" paragraph in Tools
1091:   mirroring "Decision tools" (verified `get_feat` does take
1092:   `raw: bool = False`, matching every other domain, before writing this
1093:   paragraph — checked `feat/tools/get_feat.py` directly per this task's
1094:   own instruction), plus one extra sentence noting `feat`'s bespoke
1095:   `_paths.py` addressing and its lack of `update_feat`/`set_status_feat`
1096:   tools of its own; the `update`/`set_status` paragraphs' domain counts
1097:   bumped from eight/nine to nine/ten whole-body/total domains (both
1098:   `general/tools/update.py` and `set_status.py` had already made this
1099:   exact bump to their own docstrings back in Phase 2, so this brought
1100:   `server.py` in line with code that was already correct); a new
1101:   "Feature prompts (`feat/prompts/`)" paragraph in Prompts mirroring
1102:   "Decision prompts"; and `feat` inserted into both domain-enumeration
1103:   sentences ("Modules are grouped domain-first ..." and "Add a new
1104:   domain by ...") plus the final "each register `tools`, `resources`,
1105:   and `prompts`" sentence.
1106: - **Cross-cutting config (Task 5.2)**: `pyproject.toml` gained
1107:   `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]` alphabetically
1108:   between `dec` and `gol`. `.pre-commit-config.yaml`'s one shared
1109:   `files:` regex glob (`^src/biz/dfch/specmgr/(dec/models/v1|gol/
1110:   models/v1|...)/.*\.py$`) gained `feat/models/v1` between `dec/models/v1`
1111:   and `gol/models/v1` in all 9 pre-existing occurrences (counted 9 before
1112:   the edit, 9 after — a global find/replace, not a manual per-occurrence
1113:   edit, so the count check was mostly a sanity confirmation) plus a new
1114:   10th occurrence in the brand-new `specmgr-schema-feat-package` hook
1115:   itself, which mirrors `specmgr-schema-dec-package` verbatim (id/name/
1116:   description/entry/language/pass_filenames/files) and is placed last,
1117:   matching this file's own insertion-order (not alphabetical) convention
1118:   for per-domain schema-package hooks: `req, uc, tsk, rsk, qa, prb, gol,
1119:   dec, feat`. `.github/workflows/ci.yml` gained a new
1120:   `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` `` drift-check
1121:   step, same `if: matrix.python-version == '3.13'` guard and
1122:   `::error::...` message format as the existing `dec` step, placed
1123:   immediately after it; the `docs/*_schema.json` step's own comment
1124:   prose and the `specmgr-schema` pre-commit hook's description were both
1125:   updated to name `feat` among the registered types.
1126: - **`AGENTS.md`/root `README.md` (Task 5.3)**: added a new `**`feat/`**`
1127:   bullet to `AGENTS.md`'s per-domain enumeration (between `dec/` and
1128:   `general/`), at the same depth/style as `dec/`'s own, spelling out the
1129:   addressing deviation explicitly (non-UUID `id`, folder-per-document,
1130:   bespoke `feat/tools/_paths.py`, mandatory `SPECMGR_FEAT_DIR`, all 8
1131:   tools, generic `update`/`set_status` dispatch, resources, prompts,
1132:   `FeatSummary.path`). Updated every other domain-enumeration sentence in
1133:   `AGENTS.md` that listed all current domains: the `general/` bullet's
1134:   own whole-body/total domain counts (eight→nine, nine→ten) and `type`
1135:   enumeration; the "Still genuinely missing" section's `validate_*`/
1136:   `delete_*` lists and the register-all-three sentence; the "MCP server
1137:   (server.py)" section's own domain-import-line description. Root
1138:   `README.md`: added `Feature (FEAT)` to the active bulleted artifact
1139:   list (alphabetically between `Decision (DEC)` and `Goal (GOL)`),
1140:   removed the `Feature (FTR)` line from the commented-out placeholder
1141:   block (the abbreviation was wrong there too — "FTR", not the actually-
1142:   implemented "FEAT" — on top of being redundant now that FEAT is
1143:   active), and, as a drive-by fix, moved `Risk (RSK)` out of the same
1144:   placeholder into the active list since `AGENTS.md`'s own `rsk/` bullet
1145:   confirms RSK has been a fully implemented, schema-backed domain for
1146:   some time — only the not-yet-implemented `Acceptance Criterium (ACC)`
1147:   stays commented out. Recorded as a new Decisions Made entry below.
1148: - **Regeneration (Task 5.4)**: ran `specmgr docs`, `specmgr mcp-docs`,
1149:   `specmgr schema`, and `specmgr schema --type feat --output-dir
1150:   src/biz/dfch/specmgr/feat/data`, each twice in a row. `specmgr docs`
1151:   changed only `docs/api/biz.dfch.specmgr.server.md` (reflecting the
1152:   Task 5.1 docstring edits) on the first run and produced zero further
1153:   diff on the second. `specmgr mcp-docs` produced no diff on either
1154:   run — every FEAT tool/resource/prompt was already fully registered
1155:   against the live `mcp` instance before this phase (Phases 2-4), so
1156:   `docs/MCP.md` was already current; this phase's `server.py` docstring
1157:   changes only affect `docs/api/`, not `docs/MCP.md`, which is generated
1158:   from the actual tool/resource/prompt registrations, not the module
1159:   docstring. `specmgr schema` (all 9 registered types) and the `feat`-
1160:   only packaged-copy invocation both reported every file "(unchanged)"
1161:   on both runs. Confirmed idempotent across the board.
1162: - **Final verification (Task 5.5)** — ACC-001..009 walked with concrete
1163:   evidence:
1164:   - ACC-001: `tests/feat/models/v1/test_parser.py` exercises the full
1165:     matrix (`TestParseFeatValueViolations`/`TestParseFeatStructuralViolations`)
1166:     — malformed status/hyphenated status/wrong `type`, malformed
1167:     `REQ-\d{3}`/`ACC-\d{3}` items, out-of-order `Updates` entries,
1168:     unknown H2, missing `Requirements`, malformed `Phase`/`UpdateEntry`
1169:     headings, zero-phase/zero-entry composites, leading content before
1170:     H1, a second H1 — all raise, all covered. `docs/feat_schema.json`/
1171:     `specmgr://feat/schema` (via `feat/resources/feat_schema.py`) both
1172:     exist and are exercised by `tests/feat/resources/test_feat_schema.py`.
1173:   - ACC-002: `tests/feat/tools/test__paths.py::TestFindFeatPathById`
1174:     covers the direct-shortcut resolution, the id/folder-name-mismatch
1175:     rejection (tool-layer, not model-layer), and the no-partial-match
1176:     behavior; `tests/feat/tools/test_integration.py::
1177:     TestCreateFeatConcurrencyIntegration::test_many_concurrent_create_feat_calls_never_collide`
1178:     proves the global create-lock prevents two callers picking the same
1179:     `NNN`.
1180:   - ACC-003: all 8 tools exist, are registered (confirmed live in
1181:     `docs/MCP.md`'s Tools section), and are exercised by
1182:     `tests/feat/tools/test_integration.py::TestFeatLifecycleIntegration::
1183:     test_full_lifecycle_roundtrip` (create→get→list→...→delete-stub→
1184:     validate against a temp `SPECMGR_FEAT_DIR`); `list_feat` returns
1185:     `PagedResult[FeatSummary]` per `tests/feat/tools/test_list_feat.py`.
1186:   - ACC-004: the same integration test drives `update(type="feat", ...)`
1187:     in both whole-body and line-range modes and `set_status(type="feat",
1188:     ...)`, asserting `id`/`type`/`created`/`version` are preserved and
1189:     only `updated`/`status` change.
1190:   - ACC-005: `docs/MCP.md`'s Resources section lists exactly
1191:     `specmgr://feat/schema`/`/example`/`/template`, no `/{id}`, no
1192:     `/list`; `tests/feat/resources/` exercises all three live.
1193:   - ACC-006: `tests/feat/prompts/test_create_feat.py::
1194:     TestCreateFeatInstructionsWalkthrough`/`test_update_feat.py::
1195:     TestUpdateFeatInstructionsWalkthrough` drive the real tools following
1196:     the packaged instructions' own narrated steps end to end (not just
1197:     static-text assertions), per this ACC's explicit requirement.
1198:   - ACC-007: `diff`-verified byte-identical `docs/feat_schema.json` and
1199:     `src/biz/dfch/specmgr/feat/data/feat_schema.json` (both freshly
1200:     regenerated this phase); `tests/feat/resources/test_feat_schema.py::
1201:     test_matches_fresh_generate_feat_schema_output` covers the same
1202:     invariant at the test-suite level.
1203:   - ACC-008: `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` all
1204:     report zero drift (see Task 5.4 above); `AGENTS.md` reflects the new
1205:     domain (this update); `feat-7-various-improvements` already carries
1206:     Task 0.31 and its Task 0.30 background note already names `feat` as
1207:     a fourth divergent variant (done in Phase 0, verified still present).
1208:   - ACC-009: full `unittest` suite green (2228 tests, 221 of them under
1209:     `tests/feat/`); `ruff format --check`/`ruff check` clean; `vulture
1210:     src/ whitelist.py --min-confidence 60` clean; `specmgr unused-code`
1211:     clean.
1212:   Full quality gate re-run end to end, all green (see this update's own
1213:   Current Status entry for exact command output). Frontmatter `status`
1214:   set from `in-progress` to `done`.
1215: - Per this phase's own task instructions, **no commit was made and no
1216:   comment was posted to issue #31** — that is the phase orchestrator's
1217:   responsibility, not the implementing agent's, for this run.
1218: - **This feature is now complete.** All 5 phases and all 11 requirements
1219:   (REQ-001..011) are implemented, tested, and cross-registered; all 9
1220:   acceptance criteria (ACC-001..009) are verified with concrete evidence.
1221: 
1222: #### Update 2026-08-30 (Phase 4 complete — prompts)
1223: 
1224: - Implemented `feat/prompts/` in full: `create_feat.py`
1225:   (`create_feat(topic)`), `update_feat.py`
1226:   (`update_feat(id, instructions=None)`), `__init__.py` — each a 1:1
1227:   mirror of `dec.prompts.create_dec`/`update_dec`: thin `string.Template`
1228:   wrappers around `general.tools._packaged_data.read_packaged_text`
1229:   reading the already-existing Phase-3 packaged instructions files
1230:   (`feat_create_instructions.md`/`feat_update_instructions.md`),
1231:   substituting `$topic` (create) and `$id`/`$instructions` (update).
1232:   Neither calls `TodoWrite`/`question`/`list_feat`/`get_feat`/
1233:   `create_feat`/`update`/`set_status` themselves — they only narrate that
1234:   sequence, matching every other prompt in this codebase.
1235: - Judgment call: `update_feat`'s fallback for a missing `instructions`
1236:   argument is the literal string `"(not given)"`, not DEC's own longer
1237:   `"(not given -- ask the user before making any change)"` — verified
1238:   `feat_update_instructions.md`'s step 2 checks for the literal substring
1239:   `"(not given)"` (`If "Requested change" above says "(not given)", ask
1240:   the user...`), so the fallback matches that check exactly rather than
1241:   reusing DEC's wording verbatim.
1242: - Updated `feat/prompts/__init__.py` to import and export both prompts
1243:   (mirroring `dec/prompts/__init__.py`'s one-module-per-prompt shape) and
1244:   `feat/__init__.py`'s module docstring to reflect Phase 4 completion
1245:   (only Phase 5 cross-cutting registration remains).
1246: - Wrote 29 new tests across `tests/feat/prompts/`
1247:   (`test_create_feat.py`/`test_update_feat.py`) — all green: static
1248:   string-content/ordering assertions mirroring `tests/dec/prompts/`'s own
1249:   depth (topic/id/instructions substitution, packaged-file provenance,
1250:   tool-call-sequence ordering, missing-file propagation), plus, per
1251:   ACC-006's explicit requirement, one "walk the instructions end to end"
1252:   test per prompt driving the real `create_feat`/`get_feat`/`list_feat`/
1253:   `update`/`set_status` tools against a temporary `SPECMGR_FEAT_DIR`:
1254:   `TestCreateFeatInstructionsWalkthrough` follows step 0 (dedup check via
1255:   `list_feat`) and step 4 (`create_feat`) literally;
1256:   `TestUpdateFeatInstructionsWalkthrough` creates a real document, then
1257:   follows `get_feat` → line-range `update` → whole-body `update` →
1258:   `set_status` exactly as the packaged update instructions narrate,
1259:   asserting the end state. Checked `tests/dec/prompts/` first per this
1260:   phase's own instructions — it only does static-text assertions, so this
1261:   deeper walk-through is new depth introduced specifically for `feat`.
1262: - Quality gate: `ruff format --check` (clean), `ruff check` (clean),
1263:   `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
1264:   needed), `specmgr unused-code` (clean), full `unittest` suite (2228
1265:   tests, green, up from 2199 after Phase 3).
1266: - Per this phase's own task instructions, **no commit was made and no
1267:   comment was posted to issue #31** — that is the phase orchestrator's
1268:   responsibility, not the implementing agent's, for this run.
1269: - Next: Phase 5 (cross-cutting registration) — `server.py` domain import,
1270:   `pyproject.toml`/`.pre-commit-config.yaml`/CI wiring, `AGENTS.md`
1271:   updates, regenerated docs, final verification pass, and setting the
1272:   feature status to `done`.
1273: 
1274: #### Update 2026-08-30 (Phase 3 complete — resources, packaged data, schema)
1275: 
1276: - Implemented `feat/data/` in full: `feat_example.md` (a byte-identical
1277:   copy of `tests/feat/models/v1/data/feat_reference.md`, confirmed via
1278:   `diff`), `feat_template.md` (all-sections placeholder skeleton --
1279:   `Dependencies` with both `Depends On`/`Blocks`, `Design Notes`,
1280:   `Related Decisions`, `Blockers`, `Decisions Made`, `Related PRs /
1281:   Commits`, `More Information` all present -- `status: planning`,
1282:   round-trips through `parse_feat`), `feat_create_instructions.md`/
1283:   `feat_update_instructions.md` (narrated instruction bodies mirroring
1284:   `dec`'s/`gol`'s own two files, tailored to `feat`'s actual schema, its
1285:   four-value hyphen-free status set, and its no-`update_feat`/
1286:   `set_status_feat`-of-its-own generic-dispatch MCP surface), and
1287:   `feat_schema.json` (both `docs/feat_schema.json` and the packaged
1288:   `feat/data/feat_schema.json` copy, generated via `specmgr schema --type feat` and `specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data`, confirmed byte-identical via
1289:   `diff`).
1290: - `commands/schema.py` gained `generate_feat_schema()` (mirroring
1291:   `generate_dec_schema()` exactly) and a `"feat"` entry in `_GENERATORS`,
1292:   inserted alphabetically between the existing `"dec"` and `"gol"` keys.
1293: - Implemented `feat/resources/`: `feat_schema.py`/`feat_example.py`/
1294:   `feat_template.py`/`__init__.py`, each a 1:1 mirror of
1295:   `dec.resources`' own three modules plus its `__init__.py`, registering
1296:   `specmgr://feat/schema`/`specmgr://feat/example`/
1297:   `specmgr://feat/template` (no `/{id}` -- id-based reads are
1298:   `get_feat`-only; no `/list` -- listing is the `list_feat` tool).
1299:   Updated `feat/__init__.py`'s module docstring to reflect Phase 3
1300:   completion (data/resources populated, only `prompts` still empty).
1301: - Replaced the two Phase-2-deferred tests
1302:   (`tests/feat/tools/test_get_feat_example.py`/
1303:   `test_get_feat_template.py`) with real "returns the packaged file"
1304:   happy-path assertions (mirroring `test_get_dec_example.py`/
1305:   `test_get_dec_template.py`), now that the packaged files they read
1306:   actually exist on disk.
1307: - Wrote 20 new tests across `tests/feat/resources/`
1308:   (`test_feat_schema.py`/`test_feat_example.py`/`test_feat_template.py`)
1309:   -- all green, including: `feat_schema` matches a fresh
1310:   `generate_feat_schema()` output; `feat_example` is byte-identical to
1311:   both the packaged file and the Phase-1 reference fixture, and
1312:   round-trips through `parse_feat` byte-exact (re-verifying ACC-001 at
1313:   this layer too, per this phase's own instructions) while exercising
1314:   every optional section (`Dependencies` with both children,
1315:   `Design Notes`, `Related Decisions`, `Blockers`, `Decisions Made`,
1316:   `Related PRs / Commits`, `More Information`); `feat_template`
1317:   successfully parses via `parse_feat` (structurally valid, `status: planning`) while exercising the same set of optional sections, without
1318:   being required to be a "realistic" document.
1319: - Quality gate: `ruff format --check` (clean), `ruff check` (clean),
1320:   `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
1321:   needed), `specmgr unused-code` (clean), full `unittest` suite (2199
1322:   tests, green, up from 2179 after Phase 2).
1323: - Per this phase's own task instructions, **no commit was made and no
1324:   comment was posted to issue #31** -- that is the phase orchestrator's
1325:   responsibility, not the implementing agent's, for this run.
1326: - Next: Phase 4 (`feat/prompts/`) -- `create_feat.py`
1327:   (`create_feat(topic)`), `update_feat.py`
1328:   (`update_feat(id, instructions=None)`), `__init__.py`, and
1329:   `tests/feat/prompts/` (ACC-006).
1330: 
1331: #### Update 2026-08-30 (Phase 2 complete — tools, bespoke addressing)
1332: 
1333: - Implemented `feat/tools/` in full per Design Notes' Addressing section:
1334:   - `_paths.py` — hand-rolled, ADR-style (not built on
1335:     `general/tools/_doc_paths.py`): `feat_base_dir()`/`ensure_feat_base_dir()`
1336:     (`SPECMGR_FEAT_DIR`, falling back to `.specmgr/feat`), `iter_feat_paths(base_dir)` (globs `<base>/*/README.md`), `find_feat_path_by_id(base_dir, id_)` (the no-scan `<base>/<id_>/README.md` shortcut — no partial-id
1337:     matching), `FeatNotFoundError`, plus `feature_title()` (strips the
1338:     literal `"Feature: "` prefix off `Feature.text`, needed because
1339:     `Feature` declares no `title` computed field of its own, unlike
1340:     `Phase`/`UpdateEntry`/`DecisionEntry`) and `FEAT_FOLDER_PATTERN`.
1341:   - `_lock.py` — per-id `feat_lock(id_)` (identical shape to
1342:     `dec_lock`/`adr_lock`) plus the new **global** `feat_create_lock()`
1343:     (a single module-level `threading.Lock`, no per-id registry needed).
1344:   - `_io.py`/`_write.py` — `read_feat`/`load_by_id` (mirrors `dec.tools._io`
1345:     file-for-file) and `write_feat_file` (mirrors `dec.tools._write`, plus
1346:     `path.parent.mkdir(parents=True, exist_ok=True)` since `feat` is
1347:     folder-per-document).
1348:   - The 8 lifecycle tools + `tools/__init__.py`: `create_feat` (derives
1349:     `feat-NNN-slug` under the global create lock, plain-date
1350:     `created`/`updated`), `parse_feat`, `list_feat`
1351:     (`PagedResult[FeatSummary]`, `path`/`ref` populated from the real
1352:     resolved path), `get_feat(id, raw=False)`, `get_feat_example`/
1353:     `get_feat_template` (wired to the shared packaged-data reader, though
1354:     the packaged files themselves are Phase 3's job), `delete_feat` (stub),
1355:     `validate_feat`.
1356: - `general/tools/update.py`/`set_status.py` gained `_update_feat`/
1357:   `_set_status_feat` adapters and `"feat"` dispatch table entries (REQ-006)
1358:   — `feat` is now included in both tools' `type` `Literal`/dispatch table,
1359:   with the same plain-`YYYY-MM-DD`-date `updated` divergence `create_feat`
1360:   established (not the other domains' microsecond timestamp). Updated both
1361:   modules' module-level docstrings' domain-count prose (8→9 for `update`,
1362:   9→10 for `set_status`).
1363: - Updated one pre-existing test,
1364:   `tests/general/tools/test_update.py::TestUpdateRegistration`, whose
1365:   hardcoded 8-value `type` enum assertion against the live `mcp` tool
1366:   registration needed `"feat"` added (now 9 values).
1367: - Wrote 73 new tests across `tests/feat/tools/` (`test__paths.py`,
1368:   `test__lock.py`, `test__io.py`, `test__write.py`, `test_create_feat.py`,
1369:   `test_get_feat.py`, `test_list_feat.py`, `test_parse_feat.py`,
1370:   `test_validate_feat.py`, `test_delete_feat.py`,
1371:   `test_get_feat_example.py`, `test_get_feat_template.py`,
1372:   `test_integration.py`) — all green, including a live full
1373:   create→get→list→update(whole-body)→update(line-range)→set_status→get→
1374:   list→validate→delete(stub) round-trip and a 20-thread concurrent-`create_feat` collision test (ACC-002/ACC-003/ACC-004).
1375: - Quality gate: `ruff format --check` (clean), `ruff check` (clean),
1376:   `vulture src/ whitelist.py --min-confidence 60` (clean, no new entries
1377:   needed), `specmgr unused-code` (clean), full `unittest` suite (2179
1378:   tests, green, up from 2106 after Phase 1).
1379: - Per this phase's own task instructions, **no commit was made and no
1380:   comment was posted to issue #31** — that is the phase orchestrator's
1381:   responsibility, not the implementing agent's, for this run.
1382: - Next: Phase 3 (`feat/resources/` + `feat/data/` + schema command) —
1383:   `feat_example.md`/`feat_template.md` (byte-identical copy of
1384:   `feat_reference.md` / all-sections placeholder skeleton),
1385:   `feat_create_instructions.md`/`feat_update_instructions.md`,
1386:   `generate_feat_schema()`, and the three `specmgr://feat/*` resources.
1387:   `get_feat_example`/`get_feat_template` are already wired to read the
1388:   packaged files that Phase 3 ships — no further tool-layer changes needed
1389:   once those files exist, only the two currently-deferred tests
1390:   (`test_get_feat_example.py`/`test_get_feat_template.py`) need their
1391:   "real packaged file" happy-path test added back in.
1392: 
1393: #### Update 2026-08-30 (Phase 1 complete — models + parser)
1394: 
1395: - Implemented `feat/models/v1/` in full: `_util.py`
1396:   (`SCHEMA_COMMENT_VERSION = "v1"`), `frontmatter.py` (`FeatFrontmatter`,
1397:   closed 4-set status, `"planning"` default overriding the base's
1398:   `"draft"`, mirroring `rsk.RskFrontmatter`'s `_default_blank_status_to_open`
1399:   pattern), `body.py` (`Feature`/`Plan`/`Progress` and all 20 child section
1400:   classes per Design Notes, including the `RequirementItem`/
1401:   `AcceptanceCriterionItem` computed-field regexes, `Phase`'s
1402:   `number`/`title` computed fields, `UpdateEntry`/`DecisionEntry`'s shared
1403:   ISO8601 `timestamp`/`title` computed fields and `@alias` regex, and the
1404:   newest-first `@model_validator` on `Updates`/`DecisionsMade`),
1405:   `document.py` (`FeatDocument`), `parser.py` (`parse_feat`), `summary.py`
1406:   (`FeatSummary(DocSummary)` + `path: str`), and the `models/v1/__init__.py`/
1407:   `models/__init__.py` exports.
1408: - Verified, live, that the "no `LITERAL` needed" claims in Design Notes for
1409:   `Plan`/`Progress`/`RelatedDecisions`/`ExplicitlyOutOfScope`/`DependsOn`
1410:   all hold against the real `space_separated_name()` engine function before
1411:   writing any code — only `RelatedPrsCommits` needed the documented
1412:   `LITERAL` override.
1413: - Seeded `tests/feat/models/v1/data/feat_reference.md` from
1414:   `.specmgr/feat/feat-31-feature/example.md` per Task 1.5, with two small,
1415:   content-preserving adjustments needed to satisfy the generic `models/md`
1416:   engine's own existing constraints (both recorded as Decisions Made
1417:   entries below, not schema changes): every bullet/checklist list became a
1418:   loose list (blank line between items), and Task 0.1's item text dropped
1419:   its wrapped `— status: completed (2026-08-30)` suffix.
1420: - Added one design decision beyond Design Notes' literal text:
1421:   `Requirements`/`AcceptanceCriteria`/`Phase` each gained an eager-
1422:   computed-field-validation `@model_validator`, mirroring
1423:   `tsk.models.v1.body.Task._validate_items_eagerly` exactly, so a malformed
1424:   item raises immediately at parse time (see Decisions Made).
1425: - Wrote 99 new tests across `test_frontmatter.py` (11)/`test_body.py`
1426:   (70)/`test_parser.py` (18); all green.
1427: - Quality gate: `ruff format --check` (clean), `ruff check` (clean),
1428:   `vulture src/ whitelist.py --min-confidence 60` (clean, after adding
1429:   `feat`'s new pydantic-field/validator names to `whitelist.py`, same
1430:   false-positive pattern already documented there for every other
1431:   domain), `specmgr unused-code` (clean), full `unittest` suite (2106
1432:   tests, green).
1433: - Per this phase's own task instructions, **no commit was made and no
1434:   comment was posted to issue #31** — that is the phase orchestrator's
1435:   responsibility, not the implementing agent's, for this run.
1436: - Next: Phase 2 (`feat/tools/`) — bespoke addressing (`_paths.py`,
1437:   `_lock.py`, `_io.py`, `_write.py`), the 8 MCP tool modules, and the
1438:   generic `update`/`set_status` dispatch adapters.
1439: 
1440: #### Update 2026-08-30 (design review complete — Blocker resolved, Phase 1 authorized)
1441: 
1442: - **Design review declared complete** after five rounds spanning
1443:   body-modeling depth, addressing scheme, frontmatter semantics, MCP
1444:   surface scope, ordering/comment/hyperlink questions, LITERAL-alias
1445:   elimination, and partial-match/env-var/FeatSummary-path questions — no
1446:   open questions remain in Design Notes.
1447: - Frontmatter `status` changed from `planning` to `in-progress`; version
1448:   bumped to `1.6.0`.
1449: - Blockers: "Design review pending" marked resolved (`[x]`), recording
1450:   the five-round history and confirming Phase 0's committed scaffold
1451:   (`31c5c30`, `164182e`) stays untouched.
1452: - Recorded as a new Decisions Made entry.
1453: - **Implementation was explicitly not started in this session** —
1454:   user-directed: Phase 1 (and every later phase) is to be carried out by
1455:   a separate implementing session/agent (e.g. a Phase-Orchestrator-style
1456:   agent working through the Task List), not as a continuation of this
1457:   design-review conversation. Nothing under `src`/`tests` was touched.
1458: - Next: a separate agent starts at Task 1.1 (`feat/models/v1/_util.py`).
1459: 
1460: #### Update 2026-08-30 (fifth design-review round — partial-match rejected, env var confirmed mandatory, FeatSummary gains path)
1461: 
1462: - Resolved three more follow-up questions and updated Design Notes/Task
1463:   List/Decisions Made accordingly:
1464:   - **Partial-id matching rejected**: verified an agent can already
1465:     resolve a bare `"feat-31"` to the real id via `list_feat` +
1466:     `get_feat` composition, so no boundary-matching/ambiguous-match/scan
1467:     logic is being added to `find_feat_path_by_id`.
1468:   - **`SPECMGR_FEAT_DIR` confirmed mandatory**: checked the actual
1469:     precedent (`adr/tools/_paths.py`'s `SPECMGR_ADR_DIR`,
1470:     `general/tools/_doc_paths.py`'s shared `SPECMGR_DOCS_DIR`) — every
1471:     existing domain has an equivalent env var for test isolation; `feat`
1472:     keeps its own, made explicit in REQ-004/Design Notes rather than
1473:     just a parenthetical.
1474:   - **`FeatSummary` gains `path: str`**: checked `general/models/ summary.py`'s `DocSummary` and confirmed its `ref` field is
1475:     deliberately *not* a path, specifically to discourage direct file
1476:     access (same policy `AdrSummary` enforces, backed by an ADR requiring
1477:     ADRs be edited only through MCP tools). `feat` is the opposite case
1478:     by design — direct hand/agent editing of `.specmgr/feat/<id>/ README.md` is the intended, sanctioned workflow — so `FeatSummary`
1479:     adds a real `path` field alongside the inherited `id`/`ref`, not in
1480:     place of them.
1481: - Nothing under `src`/`tests` was touched.
1482: 
1483: #### Update 2026-08-30 (removed superseded example drafts; closed the "does Phase 1 know to use it" gap)
1484: 
1485: - Removed `.specmgr/feat/feat-31-feature/example-initial.md` and
1486:   `example-revised.md` — both superseded review-process drafts, now that
1487:   `example.md` has absorbed everything useful from them across four
1488:   review rounds. `example.md` is the only example file left in this
1489:   feature's folder.
1490: - Caught and fixed a real gap: `example.md` had only ever been marked
1491:   "canonical" in narrative Current Status/Decisions Made/Recent Updates
1492:   text — Task 1.5 (the actionable Task List item an implementing agent
1493:   actually follows in Phase 1) never mentioned it at all. Updated Task
1494:   1.5 to explicitly instruct seeding `feat_reference.md` from
1495:   `example.md`, and updated Current Status to reflect the same.
1496: - Nothing under `src`/`tests` was touched.
1497: 
1498: #### Update 2026-08-30 (fourth design-review round — eliminated all remaining LITERAL aliases except one)
1499: 
1500: - Per explicit user direction to minimize `LITERAL` alias use, replaced
1501:   three headings with spellings that match the implicit `SPACE_SEPARATED`
1502:   derivation exactly, eliminating the need for a `LITERAL` override on
1503:   each (verified against the live engine, same as the previous round):
1504:   - `"Related ADRs"` → **`"Related Decisions"`** (`RelatedAdrs` →
1505:     `RelatedDecisions`) — also a deliberate terminology change: phases
1506:     out "ADR" in favor of "Decision"/`dec`, per user direction, since
1507:     this codebase intends to retire ADR terminology over time. Entries
1508:     may still reference either an ADR id or a `dec` id.
1509:   - `"Explicitly out of scope"` → **`"Explicitly Out Of Scope"`**
1510:     (`ExplicitlyOutOfScope` unchanged) — accepted as consistent with this
1511:     codebase's existing Start-Case multi-word headings.
1512:   - `"Depends on"` → **`"Depends On"`** (`DependsOn` unchanged) — reusing
1513:     the parent's own name "Dependencies" for this child was considered
1514:     and rejected (confusing tautology, awkward `Dependencies.dependencies`
1515:     field name).
1516:   - `RelatedPrsCommits`/`"Related PRs / Commits"` keeps its `LITERAL`
1517:     alias — no casing-only fix exists for a heading containing a slash.
1518: - Updated the ASCII diagram, Model classes prose, REQ-001, and Task 1.3
1519:   in Design Notes; recorded as a new Decisions Made entry. `example.md`
1520:   needed no content changes beyond the "Related ADRs" → "Related
1521:   Decisions" heading rename itself.
1522: - Nothing under `src`/`tests` was touched.
1523: 
1524: #### Update 2026-08-30 (example.md verified and marked canonical)
1525: 
1526: - Cross-checked every implicit `SPACE_SEPARATED` heading alias in the
1527:   design against the live engine (`models.md.alias_match. space_separated_name`) instead of assuming the derivation matched the
1528:   intended heading text. Found and fixed 3 real bugs that would have
1529:   broken `parse_feat` in Phase 1: `RelatedAdrs` (pre-existing since round
1530:   1), `ExplicitlyOutOfScope`, `DependsOn` — all three now get an explicit
1531:   `@alias(..., type=AliasType.LITERAL)`, added to Design Notes and
1532:   recorded as a new Decisions Made entry. `example.md` itself needed no
1533:   changes (its heading text was already the intended natural-English
1534:   form); only the model-class documentation was wrong.
1535: - Marked `.specmgr/feat/feat-31-feature/example.md` as the canonical,
1536:   implementation-ready worked example in Current Status above.
1537:   `example-initial.md`/`example-revised.md` are superseded review-process
1538:   artifacts — flagged as safe to remove, not yet deleted (awaiting
1539:   explicit confirmation).
1540: - Nothing under `src`/`tests` was touched. Next: remove the two
1541:   superseded example files once confirmed, then this feature is ready to
1542:   come off the design-review Blocker and resume at Phase 1.
1543: 
1544: #### Update 2026-08-30 (third design-review round — ordering/comment/hyperlink questions)
1545: 
1546: - Resolved three follow-up design questions and updated the Design Notes/
1547:   Decisions Made accordingly:
1548:   - `### Related PRs / Commits`: confirmed it stays free-form, not
1549:     regex-enforced as hyperlinks (the existing "no PR yet" placeholder
1550:     idiom would otherwise break).
1551:   - `### Updates`/`### Decisions Made` both gain an optional `comment`
1552:     field (`MarkdownSection3WithComment`, `req`'s `Level`/`Priority`
1553:     precedent) to host a machine-readable ordering hint in
1554:     `feat_template.md`/`feat_example.md`, rather than a bare editorial
1555:     comment.
1556:   - `### Decisions Made` entries switch to the same full ISO8601
1557:     timestamp as `### Updates` (not date-only), and both sections gain a
1558:     real `@model_validator`-enforced newest-first ordering invariant —
1559:     discovered along the way that `tsk_example.md` (newest-first) and
1560:     `dec_example.md` (oldest-first) already disagree on direction with no
1561:     enforcement either way; confirmed via
1562:     `general/data/general_compact_history_instructions.md` that
1563:     "newest first" is the existing, already-tool-supported convention for
1564:     the ad hoc `### Recent Updates` this feature formalizes, so that's
1565:     what both new sections enforce.
1566: - Nothing under `src`/`tests` was touched. Next: continue design review,
1567:   or unblock and resume Phase 1 once the user confirms the design is
1568:   final.
1569: 
1570: #### Update 2026-08-30 (second design-review round — Task List/Scope/Dependencies/Decisions Made structure)
1571: 
1572: - The user drafted `example-revised.md` (annotated with review comments/
1573:   open questions) building on the first `example.md`. Resolved every open
1574:   question raised in it:
1575:   - `### Requirements`/`### Acceptance Criteria` become regex-validated
1576:     lists (`REQ-\d{3}: ...`/checkbox `ACC-\d{3}: ...`), not opaque leaves.
1577:   - `### Scope` becomes a composite with mandatory `#### Included`/
1578:     `#### Explicitly out of scope` leaves (both required).
1579:   - `### Dependencies` becomes a composite with optional `#### Depends on`/
1580:     `#### Blocks` leaves (both optional).
1581:   - `### Task List` becomes a composite of `#### Phase N: ...` entries
1582:     (regex-validated heading, unpadded numbering), each phase reusing
1583:     `tsk.TaskItem` for its own flat checklist — a partial reversal of the
1584:     original "Task List stays opaque" decision (per-item metadata still
1585:     stays unparsed).
1586:   - `### Decisions Made` becomes a composite of dated
1587:     `#### {yyyy-MM-dd} — {title}` entries, chosen over a formalized-flat-
1588:     list alternative for consistency with `### Updates`.
1589:   - A new optional `### More Information` leaf is added under
1590:     `## Progress`.
1591:   - Recorded all of the above as a new Decisions Made entry, explicitly
1592:     superseding the earlier "mostly opaque leaves"/"Task List stays a
1593:     single opaque leaf" decisions.
1594: - Updated this plan's REQ-001, the Design Notes' ASCII structure diagram
1595:   and "Model classes" prose, Task 1.3, ACC-001, and the Scope section's
1596:   "explicitly out of scope" bullet on Task List to match.
1597: - Nothing under `src`/`tests` was touched — the Blocker (design review
1598:   pending before Phase 1) still applies; this round only revised the
1599:   design itself, per explicit user instruction not to remove/change
1600:   anything else yet.
1601: - Next: continue the design review (any further structural questions),
1602:   then unblock and resume at Phase 1 once the user confirms.
1603: 
1604: #### Update 2026-08-30 (paused for design review after Phase 0)
1605: 
1606: - Corrected: implementing Phase 0's package skeleton was premature — the
1607:   user had asked for the design to be planned and reviewed, not for
1608:   implementation to start. Nothing from Phase 0 is reverted (both commits,
1609:   `31c5c30` and `164182e`, stay on the branch as-is); instead, this feature
1610:   is explicitly paused here, recorded as a Blocker above, until the user
1611:   completes a review pass over this plan's Design Notes and either confirms
1612:   it or requests adjustments.
1613: - Also noted and resolved as a non-issue: an earlier "fyi, `sop` is still
1614:   in development and not pushed yet" flag from the user turned out not to
1615:   affect this branch — `git fetch origin dev` confirmed the `feat(sop): …`

(Output capped at 50 KB. Showing lines 803-1615. Use offset=1616 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status && git branch --show-current && git log --oneline -5"
}
```

**Output:**

```
On branch feat-31-feature
Your branch is ahead of 'origin/feat-31-feature' by 6 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
feat-31-feature
ab2b5ab docs(feat-31): record Phase 6 task -- feat frontmatter must use microsecond timestamps
ae53f51 feat(feat-31): cross-cutting registration for Feature (feat) domain (Phase 5)
b974b63 feat(feat-31): implement Feature (feat) prompts (Phase 4)
c6f8b9c feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

_Thinking:_

**Tool: grep**

**Input:**

```json
{
  "pattern": "Frontmatter.*plain|plain-date|YYYY-MM-DD.*divergence|Decisions Made",
  "path": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md"
}
```

**Output:**

````
Found 100 matches (more matches available)
/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/example.md:
  Line 94: ### Decisions Made


/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md:
  Line 57:   newest-first order enforced), optional composite `### Decisions Made`

  Line 99:   considered and rejected, see Decisions Made.

  Line 136:   `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`

  Line 140:   and `Decisions Made` — identical format) and `#### Phase N: ...`

  Line 142:   (not newest-first) entry in either `Updates` or `Decisions Made` raises

  Line 216:   decision — see Decisions Made.)

  Line 287:   ### Decisions Made                           OPTIONAL (composite, opt. comment, ISO8601, newest-first enforced)

  Line 309:   one — see Decisions Made). Renamed from "Related ADRs" to "Related

  Line 400:   Optionality lives one level up instead: `Progress.decisions_made: DecisionsMade | None = None` — a brand-new feature has no `### Decisions Made` section at all, rather than an empty one.

  Line 461:   explicitly rejected (see Decisions Made): an agent that only has a bare

  Line 536: Decisions Made log), **except possibly** for the addressing deviation

  Line 592:   later happens to read the offending computed field — see Decisions Made.

  Line 596:   Design Notes' Addressing section and Decisions Made for why `feat`

  Line 602:   canonical, engine-verified example — see Current Status/Decisions Made;

  Line 606:   `### Decisions Made` entries in newest-first order, ≥2 `#### Phase N`

  Line 608:   ISO8601 regex on both `Updates` and `Decisions Made` — depends on: Task

  Line 621:   span embedded newlines) — see Decisions Made.

  Line 639:   the literal `"Feature: "` prefix off `Feature.text`, see Decisions Made)

  Line 646:   `threading.Lock` instances (see Decisions Made — the plan's own prose

  Line 658:   `FileNotFoundError` when actually called; see Decisions Made.

  Line 729:   temporary `SPECMGR_FEAT_DIR` — see Decisions Made for the fallback

  Line 788:   Decisions Made for the full reasoning.

  Line 825:   Notes' "Frontmatter" section (which currently documents the plain-date

  Line 826:   divergence as deliberate), and any tests asserting the plain-date

  Line 830:   deliberate design decision (see Decisions Made) — reversing it needs

  Line 831:   the same care as the original decision: update the Decisions Made log

  Line 872: Notes/Decisions Made above; the Blocker below still applies (no

  Line 883: Decisions Made above. **Task 1.5 in the Task List explicitly instructs

  Line 909: task item — see Task 1.5/Decisions Made). 99 new tests

  Line 929: domain, both with the same plain-date `updated` divergence `create_feat`

  Line 1025: (ACC)` commented out (see Decisions Made). `specmgr docs`/`specmgr

  Line 1046:   (body-modeling depth; Task List/Scope/Dependencies/Decisions Made

  Line 1049:   Approved as final; see Decisions Made for the complete decision log.

  Line 1067:   section and in Decisions Made. The task calls out the affected files

  Line 1071:   asserting the plain-date format) and requires a new Decisions Made

  Line 1147:   stays commented out. Recorded as a new Decisions Made entry below.

  Line 1280:   `Related Decisions`, `Blockers`, `Decisions Made`, `Related PRs /

  Line 1315:   `Design Notes`, `Related Decisions`, `Blockers`, `Decisions Made`,

  Line 1349:     `feat-NNN-slug` under the global create lock, plain-date

  Line 1359:   with the same plain-`YYYY-MM-DD`-date `updated` divergence `create_feat`

  Line 1416:   engine's own existing constraints (both recorded as Decisions Made

  Line 1424:   item raises immediately at parse time (see Decisions Made).

  Line 1452: - Recorded as a new Decisions Made entry.

  Line 1463:   List/Decisions Made accordingly:

  Line 1491:   "canonical" in narrative Current Status/Decisions Made/Recent Updates

  Line 1519:   in Design Notes; recorded as a new Decisions Made entry. `example.md`

  Line 1532:   recorded as a new Decisions Made entry. `example.md` itself needed no

  Line 1547:   Decisions Made accordingly:

  Line 1551:   - `### Updates`/`### Decisions Made` both gain an optional `comment`

  Line 1556:   - `### Decisions Made` entries switch to the same full ISO8601

  Line 1570: #### Update 2026-08-30 (second design-review round — Task List/Scope/Dependencies/Decisions Made structure)

  Line 1586:   - `### Decisions Made` becomes a composite of dated

  Line 1591:   - Recorded all of the above as a new Decisions Made entry, explicitly

  Line 1680: ### Decisions Made

  Line 1695:   Related ADRs, Task List, Current Status, Blockers, Decisions Made,

  Line 1716:   original "don't structurally model Task List" stance; `### Decisions Made` becomes a composite of dated `#### {...} — {title}` entries

  Line 1734:   concrete use: `### Updates`/`### Decisions Made` both change from

  Line 1738:   machine-readable ordering hint. (3) `### Decisions Made` entries switch

  Line 1743:   `### Updates` and `### Decisions Made` gain a real, enforced ordering

  Line 1969:   `Decisions Made`, `Related PRs / Commits`, `More Information`) with one

  Line 1970:   entry each for `Updates`/`Decisions Made` (not two, unlike


/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/session-ses_fadb-feat-31-00-design.md:
  Line 369: 102: ### Decisions Made

  Line 641:     "consequences": "**Positive:**\n- Agents can reference specific feature paths inline, keeping instructions lean and focused\n- Clear separation: agents only read what's relevant to their task\n- Structure is reusable for future projects adopting specmgr as a toolkit\n- Development progress is version-controlled and auditable\n- The `.specmgr/` folder (and its `feat/` work units) is committed to git like any other tracked path in the repo — no `.gitignore` exclusion — so history and review apply to it the same way they do to `docs/` and source code\n\n**Negative:**\n- Adds another top-level folder to the repo structure\n- Requires discipline to keep progress sections updated (hand-maintained, not auto-generated)\n- Migrating `doc/`'s existing content (e.g. `doc/adr-tool-plan.md`, `doc/refactor-domain.md`) into the new structure is done manually, one file at a time, once this ADR is adopted — no automated migration tooling is planned\n\n**Numbering convention:**\n- `feat-NNN-slug` — `NNN` is the GitHub issue number for feature work tied to an issue. There is no separate `github_issue` frontmatter field or body line: `id` (the folder name itself) is the single source of truth for the issue number, read by parsing its `NNN` infix.\n- Work started without a GitHub issue yet uses `feat-0-slug` (issue number `0`) until/unless an issue is later opened for it\n\n**ADR vs. feature-level \"Decisions Made\" log:**\nA decision belongs in a full ADR (under `docs/adr/`) if it: (a) is architecture/structure-level and affects more than one feature or the repo as a whole, (b) would be relevant to someone joining the project later trying to understand why something is the way it is, or (c) reverses/supersedes a previous ADR. A decision belongs in the feature's own \"Decisions Made\" log instead if it: (a) is scoped entirely to that one feature's implementation details, (b) wouldn't need to be found by searching ADRs later, and (c) doesn't constrain future features. Tie-breaker: if...
  Line 647:         "content": "```\n.specmgr/\n├── feat/                          # Feature work units\n│   └── feat-NNN-slug/             # One folder per GitHub issue\n│       ├── README.md              # Feature plan + progress (mandatory)\n│       └── history.md             # Archived older \"Recent Updates\" entries (optional)\n└── (other dirs as needed)\n```\n\n**File purposes:**\n- `README.md` — Single file containing both the feature plan (requirements, acceptance criteria, task list, scope, dependencies, design notes) and progress tracking (current state, blockers, decisions made during implementation, links to related ADRs or PRs)\n- `history.md` — Optional sibling file. Holds older `Recent Updates` entries once `README.md` grows too long; `README.md` keeps only recent entries and links back to this file for anything older.\n\n**Frontmatter:** Every feature `README.md` carries a YAML frontmatter block, mandatory fields `id` (the `feat-NNN-slug` folder name itself, not a generated UUID — unlike ADR frontmatter's server-generated `id`), `version` (semver, starts at `1.0.0`), `status` (`planning` | `in-progress` | `review` | `done`), and `created`/`updated` (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no separate `GitHub Issue` field, in frontmatter or body: the issue number is the `NNN` infix already embedded in `id` (i.e. the folder name, `feat-NNN-slug`) — `0` means no issue yet — so it is derived by reading `id`, never duplicated as its own field.\n\n**Template: README.md**\n\n```markdown\n---\nid: feat-NNN-slug\nversion: 1.0.0\nstatus: planning\ncreated: YYYY-MM-DD\nupdated: YYYY-MM-DD\n---\n\n# Feature: [Feature Title]\n\n## Plan\n\n### Overview\n\nBrief description of what this feature does and why it matters.\n\n### Requirements\n\n- REQ-001: [Functional requirement]\n- REQ-002: [Non-functional requirement]\n- REQ-003: [Constraint or dependency]\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — [testable condition]\n- [ ] AC...
  Line 652:         "content": "```\n.specmgr/\n├── feat/                          # Feature work units\n│   └── feat-NNN-slug/             # One folder per GitHub issue\n│       ├── README.md              # Feature plan (mandatory)\n│       └── progress.md            # Status tracking (mandatory)\n└── (other dirs as needed)\n```\n\n**File purposes:**\n- `README.md` — Contains the complete feature plan: requirements, acceptance criteria, implementation plan, scope, dependencies, design notes, any pre-implementation research. Treated as immutable once work begins (except Implementation Plan, which may be refined during execution).\n- `progress.md` — Hand-maintained status log: execution plan (tracking actual progress), current state, blockers, decisions made during implementation, links to related ADRs or PRs. Updated throughout the feature lifecycle.\n\n**Template: README.md**\n\n```markdown\n# Feature: [Feature Title]\n\n**GitHub Issue**: #NNN  \n**Status**: [Planning | In Progress | Review | Done]\n\n## Overview\n\nBrief description of what this feature does and why it matters.\n\n## Requirements\n\n- REQ-001: [Functional requirement]\n- REQ-002: [Non-functional requirement]\n- REQ-003: [Constraint or dependency]\n\n## Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — [testable condition]\n- [ ] ACC-002: Verifies REQ-002 — [testable condition]\n- [ ] ACC-003: Verifies REQ-003 — [testable condition]\n\n## Scope\n\nWhat is included in this feature:\n- Item 1\n- Item 2\n\nWhat is explicitly out of scope:\n- Item A\n- Item B\n\n## Dependencies\n\n- Depends on: [other feat-NNN-slug, ADR id, or external]\n- Blocks: [other feat-NNN-slug]\n\n## Design Notes\n\nAny architectural decisions, patterns, or design rationale relevant to this feature.\n\n## Related ADRs\n\n- [ADR id]: [Title]\n- [ADR id]: [Title]\n\n## Implementation Plan\n\nHigh-level breakdown of work phases and tasks:\n\n### Phase 1: [Phase name]\n- Task 1.1: [description] — Depends on: [none/other tasks]\n- Task 1...
  Line 1121: 440: log only in this file's own Decisions Made.

  Line 1420: 739:     Decisions Made): the "Still genuinely missing" bullet that lists

  Line 1524: 843:     `gol/prompts/update_gol.py` (`id: str` only — see Decisions Made;

  Line 1652: 107: **Document/parser/summary**: `DecDocument(BaseModel)` (`frontmatter: DecFrontmatter`, `body: Decision`); `parse_dec(text)` is the 4-line glue (`frontmatter.loads` → `_stringify_metadata` → `Decision.from_text(format_text(post.content))`) exactly like `parse_gol`; `DecSummary(DocSummary)` plain (id/title/status/ref, no extras).

  Line 1824: 279: ### Decisions Made

  Line 2218: 96:         the feature README's Decisions Made.

  Line 2587:   Line 48: Supersedes the listing-resource half of ADR 7531106b-074b-4bd8-a83a-e433d01676e2 ("Expose listing and by-id reads as MCP resources in addition to tools") for all five domains; that ADR's by-id resource decision is unaffected. Extends the tool-over-resource precedent of ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (`get_req`) to the listing case. Implemented in `.specmgr/feat/feat-13-list-paging/README.md` (split out of `feat-7-various-improvements` Task 0.15), which tracks the full per-domain task breakdown; see that feature folder's Decisions Made log for implementation-level detail not repeated here.

  Line 2663:   Line 5328:   "command": "cd /home/user/src/biz.dfch.SpecMgr && git commit -m \"feat(qa): add qa domain Pydantic models and parser (v1)\" -m \"Phase 3 of feat-12-qa-artifact: new qa/models/v1 package (frontmatter,\nbody, document, parser, summary, _util), domain-first per ADR\nece4554b-725c-4f76-bc04-5d2b760363d2, mirroring req/tsk's exact layout.\n\nQaFrontmatter narrows type to Literal[\\\"qa\\\"] and reuses TSK's closed\nstatus set (draft/active/done/cancelled). The body implements the full\nschema from the feature's Design Notes: Qa (H1) containing General\n(Introduction + Raw Requirements), the 9 ISO/IEC 25010:2023 characteristic\ncategories, and an optional More Information section. Each category\nshares a private _QaCategory(MarkdownSection2) intermediate base\ndeclaring items once -- empirically verified this creates no\nheading-alias ambiguity across the 9 final subclasses. QaSection models\none free-form Q&A pair (comment/requirement/question/answer, all\noptional). Requirement is a leaf MarkdownSection4 decorated\n@markdown(end_marker=MarkdownBlockQuote) (Phase 1's mechanism), verified\nend-to-end against qa_reference.md: its content does not swallow the\nimmediately-following question block quote. QaAnswer is a bare\nMarkdownStr (no heading of its own), with a text computed property for\nserialization.\n\nAdds generate_qa_schema() to commands/schema.py, registered in\n_GENERATORS, and drafts docs/qa_schema.json. Adds 35 new unit tests\nunder tests/qa/models/v1/ covering frontmatter status validation,\nrequired/optional field validation, the 9 categories' distinct heading\naliases, the end_marker wiring, and a full parse_qa round-trip against\nqa_reference.md (including the deliberately-empty Compatibility category\nand the end_marker scenario). Adds 15 qa-domain field names to\nwhitelist.py (Pydantic fields read only via (de)serialization).\n\nUpdates .specmgr/feat/feat-12-qa-artifact/README.md (Tasks 3.1/3.1.1/3.2/3.3\ndone, Progress section, Decisions...
  Line 2668:   Line 11751:   "command": "cd /home/user/src/biz.dfch.SpecMgr && git commit -m \"feat(qa): register qa domain across server, packaging, CI, and docs\" -m \"Phase 5 of feat-12-qa-artifact: cross-cutting registration completing\nthe qa domain's rollout.\n\nserver.py: added qa to the bottom-of-file domain import line\n(from . import adr, general, qa, req, tsk, uc) and updated the module\ndocstring (qa resources, no specmgr://qa/{id} note, qa tools, qa\nprompts, and the domain-first summary paragraph). qa's MCP surface was\nalready transitively registered since Phase 4 (via commands/schema.py's\nimport of qa.models.v1) -- this makes the registration explicit per the\nproject's own documented convention.\n\npyproject.toml: added the biz.dfch.specmgr.qa package-data entry\n(data/*.md, data/*.json).\n\n.pre-commit-config.yaml: widened the specmgr-schema/-req-package/\n-uc-package/-tsk-package hooks' shared files glob to include\nqa/models/v1, and added a specmgr-schema-qa-package hook regenerating\nthe packaged qa/data/qa_schema.json copy.\n\n.github/workflows/ci.yml: added the docs/qa_schema.json and packaged\nsrc/biz/dfch/specmgr/qa/data/qa_schema.json drift-check steps, mirroring\nthe existing req/uc/tsk step pairs.\n\nAGENTS.md: updated to six domain/cross-cutting packages (added a qa/\nbullet, delete_qa/validate_qa to the not-yet-done lists, and every\ndomain-enumeration sentence that would otherwise be stale).\n\nVerified specmgr docs/mcp-docs/schema --type qa are all idempotent\n(zero drift on a second run) now that registration is complete.\n\nUpdates .specmgr/feat/feat-12-qa-artifact/README.md (Tasks 5.1/5.3-5.8\ndone, Progress section, Decisions Made).\""

  Line 2744:   Line 5817:   "prompt": "You are implementing Phase 7 (the final phase) of the feature plan at:\n/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md\n\nRead that entire README first, in full, including every Requirement\n(REQ-001..008, noting REQ-004/ACC-004 and REQ-005/ACC-005 were revised\nin place during Phase 3/4), every Acceptance Criterion (ACC-001..008),\nthe Decisions Made log (documents the version-gate blocker/resolution and\nseveral other decisions), and the \"Phase 7: Cross-cutting docs + final\nverification\" section under Task List.\n\nWe are on git branch `feat-14`. Phases 1-6 are complete and committed:\nQA's entire v2 schema/tools/resources/prompts surface now exists and is\nfully repointed; `qa/models/v1/` is untouched, kept as historical\nreference only. Do not commit — the orchestrator commits after verifying.\nDo not create/switch git branches.\n\n## Phase 7 tasks (verbatim from the plan)\n\n- Task 7.1: `uv run --frozen specmgr docs` (regenerate `docs/api/`,\n  `docs/GENERATED.md`); update `server.py`'s module docstring; update\n  `AGENTS.md`'s QA section (v2 as the tool-reachable schema, v1 retained\n  on-disk only, unreachable from tools).\n- Task 7.2: Final verification pass — walk every ACC-001..008 with\n  concrete evidence; run the full quality gate end-to-end (`ruff\n  format/check`, `pylint` advisory, `vulture`, full `unittest`, `specmgr\n  docs`/`specmgr adr-toc` drift checks).\n- Task 7.3: Update Progress section (Current Status, dated Recent Updates\n  entry); set feature frontmatter `status: done`; DO NOT commit (the\n  orchestrator will commit after verifying).\n\n## Concrete scope of Task 7.1\n\n1. **`src/biz/dfch/specmgr/server.py`**'s module docstring — read it in\n   full first. Two spots need a small correction:\n   - The `refine` prompt's description (around \"QA prompts\n     (`qa/prompts/`): `create_qa`, `update_qa`, plus `refine` -- ... for\n     one or more of the nine ISO/IEC 25010:2023 qual...
  Line 2780:   Line 2594: Preconditions check: the baseline plan commit `4aa183b docs(feat-15): plan risk (RSK) artifact type feature` already exists, the working tree is clean, and there are no unresolved design decisions for Phase 1 (all schema decisions are user-approved and recorded in the plan's "Decisions Made"). No need to ask the user.

  Line 2782:   Line 2608:   "prompt": "Implement exactly ONE phase of a feature plan, end to end. You write code, tests, and update the plan's Progress section. You do NOT commit, and you do NOT start any other phase.\n\n## Plan and phase\n\nPlan file (read it IN FULL first — especially \"Design Notes\", \"Decisions Made\", and \"Execution approach\"):\n/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md\n\nPhase to implement: `#### Phase 1: Specification (commit 1)`\n\nWorking directory: /home/user/src/biz.dfch.SpecMgr (git branch `feat-15-add-artifact-type-risk`, clean tree, baseline plan already committed as `4aa183b`).\n\n## Tasks (verbatim from the plan)\n\n- Task 1.1: Define `rsk` frontmatter (`rsk/models/v1/frontmatter.py` — `RskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal[\"rsk\"]`, 6-value status set `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`) — depends on: none\n- Task 1.2: Define `rsk` body structure (`rsk/models/v1/body.py`, `rsk/models/v1/assessment.py`) — `Risk(MarkdownSection1WithComment)` with `cause`/`trigger`/`consequence`/`scope`/`initial_assessment`/`strategy`/`mitigation`/`residual_assessment`/`owner`/`tags`/`more_information`; `Assessment` (new `MarkdownSection2`: two mandatory leaf-H3 children `Probability`/`Impact`, each a `MarkdownSection3` with regex `@alias` `^Probability [1-5]$`/`^Impact [1-5]$` — value in the heading, enforced eagerly by `match_alias` at parse time; computed `value: int` per leaf; derived `level` computed field on `Assessment` from the product zones) — depends on: Task 1.1\n- Task 1.3: Create a reference `rsk` document (`rsk_reference.md`) exercising every field (cause/trigger/consequence, full initial + residual 5x5 pair, all mandatory and optional sections), used as the parser's round-trip test fixture — depends on: Task 1.2 (placed at `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md`, mirroring `tsk_reference.md`'s own location convention, not `rsk...
  Line 2789:   Line 5547:   "prompt": "Implement exactly ONE phase of a feature plan, end to end. You write code, tests, and update the plan's Progress section. You do NOT commit, and you do NOT start any other phase.\n\n## Plan and phase\n\nPlan file (read it IN FULL first — especially \"Design Notes\", \"Decisions Made\", \"Execution approach\", and the completed Phase 1 report under Recent Updates):\n/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md\n\nPhase to implement: `#### Phase 2: Pydantic Models & Parser (commit 2)`\n\nWorking directory: /home/user/src/biz.dfch.SpecMgr (branch `feat-15-add-artifact-type-risk`, clean tree).\n\n## What already exists (Phase 1, committed as 397ff74 — build on it, do not rework it)\n\n- `src/biz/dfch/specmgr/rsk/models/v1/`: `frontmatter.py` (`RskFrontmatter`), `assessment.py` (`Probability`/`Impact` leaves, `Assessment` base with computed `level`, `InitialAssessment`/`ResidualAssessment` LITERAL-pinned subclasses, public `level_from_product` + zone constants), `body.py` (`Risk(MarkdownSection1WithComment)` with the full enforced section order), `__init__.py` (re-exports; its docstring currently says RskDocument/parse_rsk/RskSummary are Phase 2 — update it).\n- Reference fixture: `.specmgr/feat/feat-15-add-artifact-type-risk/rsk_reference.md` (complete valid rsk document; its body round-trips through `Risk.from_text` per Phase 1's pinned test).\n- Mirrors to study: `tsk/models/v1/{document,parser,summary,_util}.py`, `req/models/v1/{document,parser,summary}.py`, `tests/tsk/models/v1/test_parser.py` (class `TestParseTsk`), `tests/req/models/v1/test_parser.py`, `commands/schema.py` (`generate_tsk_schema`, `_GENERATORS` registry, per-domain `SCHEMA_COMMENT_VERSION` imports), `general/models/summary.py` (`DocSummary`), `tests/tsk/models/v1/__init__.py` etc.\n- `rsk/models/v1/__init__.py` does NOT yet export `SCHEMA_COMMENT_VERSION` — create `rsk/models/v1/_util.py` with `SCHEMA_COMMENT_VERSION = \"v1\"` mirr...
  Line 2790:   Line 7247:   "prompt": "Implement exactly ONE phase of a feature plan, end to end. This is the largest phase (18 tasks). You write code, tests, and update the plan's Progress section. You do NOT commit, and you do NOT start any other phase.\n\n## Plan and phase\n\nPlan file (read it IN FULL first — especially \"Design Notes\", \"Decisions Made\", \"Execution approach\", and the completed Phase 1/Phase 2 reports under Recent Updates):\n/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-15-add-artifact-type-risk/README.md\n\nPhase to implement: `#### Phase 3: MCP Surface (commit 3)`\n\nWorking directory: /home/user/src/biz.dfch.SpecMgr (branch `feat-15-add-artifact-type-risk`, clean tree).\n\n## What already exists (Phases 1-2, committed as 397ff74 + 2a8b2af — build on it, do not rework it)\n\n- `src/biz/dfch/specmgr/rsk/models/v1/`: frontmatter (`RskFrontmatter`), assessment (`Probability`/`Impact`/`Assessment`/`InitialAssessment`/`ResidualAssessment`, `level_from_product`, zone constants), body (`Risk`), document (`RskDocument`), parser (`parse_rsk`), summary (`RskSummary.from_document(document, ref)` — the Phase 3 `list_rsk` construction site), `_util` (`SCHEMA_COMMENT_VERSION`).\n- `commands/schema.py`: `generate_rsk_schema()` + `\"rsk\"` in `_GENERATORS`; `docs/rsk_schema.json` generated.\n- Feature-folder artifacts: `rsk_reference.md` (the complete valid reference doc), `rsk_tara.md`, `rsk_risk_matrix.md` (Phase 1's domain-knowledge drafts — these get PACKAGED into `rsk/data/` in this phase, Task 3.15).\n- **The mirrors** (study each before writing its rsk twin): `tsk/tools/` (10 `@mcp.tool()`s + `_paths.py`/`_io.py`/`_write.py`/`_lock.py` helpers), `tsk/resources/` (schema/example/template), `tsk/prompts/` (create_task/update_task — they read packaged `*_instructions.md` via `read_packaged_text` and use a `Template`), `req/data/` + `tsk/data/` (packaged data incl. create/update instruction files), `tsk/tools/list_tsk.py` (the paged list tool), `general/tools/...
  Line 4065: ### Decisions Made           — bullet list "**YYYY-MM-DD**: decision — rationale"

  Line 4096:           "description": "Model ## Plan / ## Progress as composite H2 sections with fixed H3 children, but keep Overview/Requirements/Scope/Dependencies/Design Notes/Task List/Current Status/Decisions Made/Related PRs as opaque free-text leaves (like RSK's Cause/Trigger or GOL's Description). Only 'Recent Updates' gets real structure (H4 dynamic list, TSK/DEC precedent), since it's already proven and gives real validation value (>=1 entry)."

  Line 4100:           "description": "Also model Task List as structured Phase/Task objects (checkbox, dependency, status fields parsed out), Requirements/Related ADRs/Decisions Made as structured list items, etc. More validation, much more engine/schema work, and brittle against the free-text variability I observed across real files."

  Line 4446:   ### Decisions Made                         leaf, optional

  Line 4555:   Line 2035:   "newString": "- [ ] Task 0.30: Consolidate \"Recent Updates\" and \"Updates\" across\n  artifact types — depends on: none — status: not-started\n\n  Background: Found while planning `feat-30-sop` (2026-08-30). Different\n  document-type domains use different heading text and different section\n  shapes for their own \"what changed over time\" section: `tsk`'s\n  `RecentUpdates`/`## Recent Updates` (free-form `@alias(value=\".+\",\n  type=AliasType.REGEX)` H3 heading, mandatory lead `MarkdownParagraph`\n  content, no timestamp format enforced structurally); `dec`'s\n  `Updates`/`## Updates` (implicit-alias heading, `UpdateEntry` H3s). `sop`\n  (feat-30, not yet implemented) is about to add a **third** variant,\n  `Updates`/`## Updates` with a structurally-enforced ISO8601 timestamp +\n  \" — \" + title heading regex\n  (`^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2}) — .+$`)\n  — a stricter shape than either `tsk` or `dec` currently has. None of\n  `req`/`uc`/`qa`/`prb`/`gol`/`rsk` have any such section at all today.\n  Decide: (a) whether a single canonical heading name/shape\n  (`## Updates` vs `## Recent Updates`, timestamp format enforced or not)\n  should be retrofitted across every domain that has one, or whether the\n  divergence is intentional/acceptable per-domain; (b) if consolidating,\n  whether this warrants a shared `models/md` mixin/base class (e.g. a\n  generic `UpdatesSection`/`UpdateEntry` pair domains can subclass) rather\n  than each domain hand-rolling its own `Updates`/`UpdateEntry` pair; (c)\n  whether `sop`'s new ISO8601-with-offset timestamp format for `## Updates`\n  entry headings should become the new cross-domain standard (superseding\n  `tsk`'s free-form heading and `dec`'s implicit-alias heading), be\n  retrofitted onto `tsk`/`dec`, or stay `sop`-only as a deliberate\n  divergence; record whichever decision is made, with rationale, in this\n  file's Decisions Made log (or a full ADR if it turns ...
  Line 4612:   Line 3871: Now let's add the Recent Updates entry and a Decisions Made entry documenting this design change:

  Line 4614:   Line 3879:   "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"### Recent Updates\\|### Decisions Made\\|Update 2026-08-30\" .specmgr/feat/feat-30-sop/README.md"

  Line 4629:   Line 4232: 7. **Progress**: new dated Recent Updates entry and a Decisions Made entry recording the promotion decision and rationale.

  Line 4653:   Line 1291: - **Section order** is stated identically in REQ-001, the ASCII diagram, the Model classes field order, and the "Decisions Made" log (`Purpose, Scope, Definitions, Roles and Responsibilities, Safety and Precautions, Procedure, Related Artifacts, More Information, Updates`).

  Line 4655:   Line 1308: No numbering gaps, no dangling task dependencies, no conflicting status values, no drift between the Design Notes/Task List/Scope/Decisions Made sections. The two "Recent Updates" entries (RASCI promotion, pre-implementation review) correctly reflect the renumbering they describe (Phase 3's Task 3.4/3.5/3.8 insertion and the downstream dependency fixes in 5.2–5.4 are consistent with the current numbering).

  Line 4902:   ### Decisions Made                          leaf, optional

  Line 5126:   "content": "---\ncreated: 2026-08-30\nid: feat-31-feature\nstatus: planning\nupdated: 2026-08-30\nversion: 1.0.0\n---\n\n# Feature: Formalize the Feature artifact type (\"feat\")\n\n## Plan\n\n### Overview\n\nFormalize the ad hoc `.specmgr/feat/<id>/README.md` convention (ADR\ne369ee2e-3353-4f92-991c-6367d76d832e) into a real, schema-backed `feat`\ndocument-type domain — the same kind of markdown-frontmatter, Pydantic-modeled,\nMCP-tool-addressable artifact every other document type in this repo already\nis. `feat` is deliberately special among domains: it formalizes a convention\nthat has already been used, by hand, 17+ times before this feature existed,\nand its addressing scheme (`id` = a chosen `feat-NNN-slug`, not a\nserver-generated UUID; one folder per document holding a fixed `README.md`\nfilename, not a flat file directly under the base directory) is a genuine,\nintentional deviation from every other domain's `8cf940c5` precedent. `feat`\nfollows the domain-first hierarchy (ADR\nece4554b-725c-4f76-bc04-5d2b760363d2) and is built on the generic `models/md`\nparsing engine with the simple surface used by GOL/RSK/DEC/(planned)SOP — no\nfine-grained mutation tools, no renderer (writes persist the caller's raw\nvalidated body byte-for-byte) — and is the second domain (after the\nstill-unimplemented `feat-30-sop`) planned to use the post-feat-22 generic\n`update`/`set_status` dispatch tools from day one (ADR\n36905d5b-8057-4294-8665-c7eed5534db0): there is no `update_feat`/\n`set_status_feat` tool of its own.\n\nImplementation happens on a dedicated branch `feat-31-feature`, created off\n`dev` before Phase 0 starts (this branch), mirroring every prior \"add\nartifact type\" feature's own branch-per-feature convention (e.g.\n`feat-21-decision`, `feat-15-add-artifact-type-risk`).\n\n### Requirements\n\n- REQ-001: Define the `feat` markdown schema — frontmatter (`type=\"feat\"`,\n  closed 4-value status set `planning`/`progress`/`review`/`done` with no\n  hyphens ...
  Line 5224: 807:   file's Decisions Made log (or a full ADR if it turns out to affect the

  Line 5255:   "oldString": "  Background: Found while planning `feat-30-sop` (2026-08-30). Different\n  document-type domains use different heading text and different section\n  shapes for their own \"what changed over time\" section: `tsk`'s\n  `RecentUpdates`/`## Recent Updates` (free-form `@alias(value=\".+\",\n  type=AliasType.REGEX)` H3 heading, mandatory lead `MarkdownParagraph`\n  content, no timestamp format enforced structurally); `dec`'s\n  `Updates`/`## Updates` (implicit-alias heading, `UpdateEntry` H3s). `sop`\n  (feat-30, not yet implemented) is about to add a **third** variant,\n  `Updates`/`## Updates` with a structurally-enforced ISO8601 timestamp +\n  \" — \" + title heading regex\n  (`^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2}) — .+$`)\n  — a stricter shape than either `tsk` or `dec` currently has. None of\n  `req`/`uc`/`qa`/`prb`/`gol`/`rsk` have any such section at all today.\n  Decide: (a) whether a single canonical heading name/shape\n  (`## Updates` vs `## Recent Updates`, timestamp format enforced or not)\n  should be retrofitted across every domain that has one, or whether the\n  divergence is intentional/acceptable per-domain; (b) if consolidating,\n  whether this warrants a shared `models/md` mixin/base class (e.g. a\n  generic `UpdatesSection`/`UpdateEntry` pair domains can subclass) rather\n  than each domain hand-rolling its own `Updates`/`UpdateEntry` pair; (c)\n  whether `sop`'s new ISO8601-with-offset timestamp format for `## Updates`\n  entry headings should become the new cross-domain standard (superseding\n  `tsk`'s free-form heading and `dec`'s implicit-alias heading), be\n  retrofitted onto `tsk`/`dec`, or stay `sop`-only as a deliberate\n  divergence; record whichever decision is made, with rationale, in this\n  file's Decisions Made log (or a full ADR if it turns out to affect the\n  parser engine itself, per the ADR-vs-feature-log tie-breaker in ADR\n  e369ee2e-3353-4f92-991c-6367d76d832e). Out of scope fo...
  Line 5256:   "newString": "  Background: Found while planning `feat-30-sop` (2026-08-30). Different\n  document-type domains use different heading text and different section\n  shapes for their own \"what changed over time\" section: `tsk`'s\n  `RecentUpdates`/`## Recent Updates` (free-form `@alias(value=\".+\",\n  type=AliasType.REGEX)` H3 heading, mandatory lead `MarkdownParagraph`\n  content, no timestamp format enforced structurally); `dec`'s\n  `Updates`/`## Updates` (implicit-alias heading, `UpdateEntry` H3s). `sop`\n  (feat-30, not yet implemented) is about to add a **third** variant,\n  `Updates`/`## Updates` with a structurally-enforced ISO8601 timestamp +\n  \" — \" + title heading regex\n  (`^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2}) — .+$`)\n  — a stricter shape than either `tsk` or `dec` currently has. `feat`\n  (feat-31, formalizing the `.specmgr/feat/` artifact type itself, also not\n  yet implemented) adds a **fourth** variant: the same ISO8601-enforced\n  `Updates`/`UpdateEntry` shape as `sop`, but one heading level deeper\n  (`### Updates`/`#### {timestamp} — {title}`, since it sits under\n  `## Progress` rather than directly under the document's H1) — copied from\n  `sop`'s planned shape rather than `sop`'s code (which does not exist yet).\n  None of `req`/`uc`/`qa`/`prb`/`gol`/`rsk` have any such section at all\n  today. Decide: (a) whether a single canonical heading name/shape\n  (`## Updates` vs `## Recent Updates`, timestamp format enforced or not,\n  and at which heading depth) should be retrofitted across every domain\n  that has one, or whether the divergence is intentional/acceptable\n  per-domain; (b) if consolidating, whether this warrants a shared\n  `models/md` mixin/base class (e.g. a generic `UpdatesSection`/\n  `UpdateEntry` pair domains can subclass) rather than each domain\n  hand-rolling its own `Updates`/`UpdateEntry` pair; (c) whether `sop`'s/\n  `feat`'s ISO8601-with-offset timestamp format for `Updates` e...
  Line 6070: -   record that decision in this file's Decisions Made — depends on: none —

  Line 6072: +  record that decision in this file's Decisions Made — depends on: none —

  Line 6181: -  file's Decisions Made log (or a full ADR if it turns out to affect the

  Line 6209: +  Decisions Made log (or a full ADR if it turns out to affect the parser

  Line 6250:   "oldString": "  Background: Found while planning `feat-30-sop` (2026-08-30). Different\n  document-type domains use different heading text and different section\n  shapes for their own \"what changed over time\" section: `tsk`'s\n  `RecentUpdates`/`## Recent Updates` (free-form `@alias(value=\".+\",\n  type=AliasType.REGEX)` H3 heading, mandatory lead `MarkdownParagraph`\n  content, no timestamp format enforced structurally); `dec`'s\n  `Updates`/`## Updates` (implicit-alias heading, `UpdateEntry` H3s). `sop`\n  (feat-30, not yet implemented) is about to add a **third** variant,\n  `Updates`/`## Updates` with a structurally-enforced ISO8601 timestamp +\n  \" — \" + title heading regex\n  (`^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2}) — .+$`)\n  — a stricter shape than either `tsk` or `dec` currently has. None of\n  `req`/`uc`/`qa`/`prb`/`gol`/`rsk` have any such section at all today.\n  Decide: (a) whether a single canonical heading name/shape\n  (`## Updates` vs `## Recent Updates`, timestamp format enforced or not)\n  should be retrofitted across every domain that has one, or whether the\n  divergence is intentional/acceptable per-domain; (b) if consolidating,\n  whether this warrants a shared `models/md` mixin/base class (e.g. a\n  generic `UpdatesSection`/`UpdateEntry` pair domains can subclass) rather\n  than each domain hand-rolling its own `Updates`/`UpdateEntry` pair; (c)\n  whether `sop`'s new ISO8601-with-offset timestamp format for `## Updates`\n  entry headings should become the new cross-domain standard (superseding\n  `tsk`'s free-form heading and `dec`'s implicit-alias heading), be\n  retrofitted onto `tsk`/`dec`, or stay `sop`-only as a deliberate\n  divergence; record whichever decision is made, with rationale, in this\n  file's Decisions Made log (or a full ADR if it turns out to affect the\n  parser engine itself, per the ADR-vs-feature-log tie-breaker in ADR\n  e369ee2e-3353-4f92-991c-6367d76d832e). Out of scope fo...

(Results truncated. Consider using a more specific path or pattern.)
````

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"^### Decisions Made\\|^#### \" .specmgr/feat/feat-31-feature/README.md | grep -i \"decision\\|frontmatter\\|timestamp\\|version\" "
}
```

**Output:**

```
816:#### Phase 6: Frontmatter timestamp format fix
1057:#### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)
1570:#### Update 2026-08-30 (second design-review round — Task List/Scope/Dependencies/Decisions Made structure)
1680:### Decisions Made

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.7s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md",
  "offset": 1680,
  "limit": 140
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
1680: ### Decisions Made
1681: 
1682: - **2026-08-30**: `id` stays `feat-NNN-slug` (the folder name), not a
1683:   server-generated UUID — a deliberate, documented deviation from ADR
1684:   8cf940c5's precedent, confirmed by the user rather than switched to match
1685:   every other domain.
1686: - **2026-08-30**: Frontmatter `version` becomes schema-version-only
1687:   (machine-managed), dropping the historical hand-bumped "plan revision"
1688:   meaning entirely (user chose "drop the hand-bumped counter" over
1689:   "split into two fields" or "keep as-is").
1690: - **2026-08-30**: Closed 4-value status set with **no hyphens** —
1691:   `planning`/`progress`/`review`/`done` (user explicitly rejected
1692:   `in-progress` in favor of `progress`).
1693: - **2026-08-30**: ~~Body sections stay mostly opaque leaves (Overview,
1694:   Requirements, Acceptance Criteria, Scope, Dependencies, Design Notes,
1695:   Related ADRs, Task List, Current Status, Blockers, Decisions Made,
1696:   Related PRs/Commits) — only `### Updates` gets real structure (H4 dynamic
1697:   list, ISO8601-enforced heading).~~ **Superseded 2026-08-30** (see the
1698:   entry directly below) — a second design-review round asked for real
1699:   structure on several more sections.
1700: - **2026-08-30**: Second design-review round — supersedes the "mostly
1701:   opaque leaves"/"Task List stays a single opaque leaf" decisions above,
1702:   based on a revised example the user drafted directly
1703:   (`example-revised.md`): `### Requirements`/`### Acceptance Criteria`
1704:   become regex-validated lists (`REQ-\d{3}: ...`/checkbox
1705:   `ACC-\d{3}: ...`, `TaskItem`-style, zero-padded 3-digit ids matching this
1706:   plan's own numbering); `### Scope` becomes a composite of mandatory
1707:   `#### Included`/`#### Explicitly out of scope` leaves (both required —
1708:   every feature must state both); `### Dependencies` becomes a composite of
1709:   optional `#### Depends on`/`#### Blocks` leaves (both optional, matching
1710:   `Dependencies` itself already being optional); `### Task List` becomes a
1711:   composite holding only `#### Phase N: ...` entries (regex
1712:   `^Phase \d+: .+$`, unpadded, matching this plan's own "Phase 0".."Phase
1713:   5" headings), each phase reusing `tsk.TaskItem` for its own flat
1714:   checklist — per-item metadata (`depends on:`/`status:`/`ETA`) stays
1715:   unparsed free text, so this is a partial, not full, reversal of the
1716:   original "don't structurally model Task List" stance; `### Decisions Made` becomes a composite of dated `#### {...} — {title}` entries
1717:   (format finalized in the entry directly below — chosen over a
1718:   formalized-flat-list alternative for consistency with `### Updates`'s
1719:   own shape); a new optional `### More Information` leaf is added under
1720:   `## Progress`, mirroring `req`'s/ADR's own section one heading level
1721:   deeper. `Overview`/`Design Notes`/`Related ADRs`/`Current Status`/
1722:   `Blockers`/`Related PRs / Commits` remain opaque leaves, unchanged.
1723: - **2026-08-30**: `### Updates` (not `### Recent Updates`), ISO8601-enforced
1724:   `#### {yyyy-MM-dd HH:mm:ss.fff±HH:mm} — {title}` heading regex, copied
1725:   from `feat-30-sop`'s plan one heading level deeper (H3/H4 instead of
1726:   H2/H3, since it sits under `## Progress` not directly under the H1).
1727: - **2026-08-30**: Third design-review round — three follow-up questions
1728:   resolved: (1) `### Related PRs / Commits` list items stay free-form, not
1729:   regex-enforced as hyperlinks — the section's own current content
1730:   (`- (Phase 0 baseline commit not yet made)`) is a legitimate non-link
1731:   placeholder idiom that a strict link-only regex would break. (2)
1732:   Confirmed the "comments only belong in an example if they populate a
1733:   real schema-declared field" rule from the entry above by giving it a
1734:   concrete use: `### Updates`/`### Decisions Made` both change from
1735:   `MarkdownSection3` to `MarkdownSection3WithComment`, adding an optional
1736:   `comment: MarkdownComment | None` field (`req`'s `Level`/`Priority`
1737:   precedent) that `feat_template.md`/`feat_example.md` populate with a
1738:   machine-readable ordering hint. (3) `### Decisions Made` entries switch
1739:   from date-only `#### {yyyy-MM-dd} — {title}` (the shape recorded two
1740:   entries above) to the *same* full ISO8601 timestamp format as
1741:   `### Updates` — necessary because a same-day pair of decisions is
1742:   otherwise indistinguishable for ordering purposes; and both
1743:   `### Updates` and `### Decisions Made` gain a real, enforced ordering
1744:   invariant (a `@model_validator` asserting newest-first, i.e. each
1745:   entry's timestamp \<= the previous entry's, raising `AssertionError`
1746:   otherwise) rather than relying on undocumented convention — newest-first
1747:   was chosen (not oldest-first/append) because it matches the *existing*
1748:   `compact_history` prompt's own "newest first" assumption for the ad hoc
1749:   `### Recent Updates` this feature formalizes, and keeps history-rotation
1750:   a simple cut-from-the-bottom operation. This directly resolves a
1751:   concrete, pre-existing gap noticed during this round: `tsk_example.md`'s
1752:   shipped example is newest-first while `dec_example.md`'s is
1753:   oldest-first, with neither domain's model code enforcing (or even
1754:   documenting) either direction — an ambiguity `feat`'s own two sections
1755:   now avoid inheriting (the cross-domain inconsistency itself stays out of
1756:   scope, tracked by `feat-7-various-improvements` Task 0.30).
1757: - **2026-08-30**: The 17 existing feature folders are **not** migrated by
1758:   this feature — tracked as a new `feat-7-various-improvements` Task 0.31
1759:   instead (user-directed).
1760: - **2026-08-30**: `Updates`/`Recent Updates` naming consolidation across
1761:   domains is **not** a new task — the existing `feat-7-various-improvements`
1762:   Task 0.30 already covers it; only its background note is extended to
1763:   mention `feat` as a fourth divergent variant (user-directed: "let the
1764:   existing feat-7 0.30 task handle this consolidation").
1765: - **2026-08-30**: Implementation happens on branch `feat-31-feature`,
1766:   created off `dev` before Phase 0 (user-directed).
1767: - **2026-08-30**: MCP surface is full sop-style generic dispatch (`create_feat`/
1768:   `parse_feat`/`list_feat`/`get_feat`/`get_feat_example`/`get_feat_template`/
1769:   `delete_feat` stub/`validate_feat` + `type="feat"` in the generic
1770:   `update`/`set_status` tools) — no `update_feat`/`set_status_feat` of its
1771:   own (user chose the "full lifecycle, sop-style generic dispatch" option).
1772: - **2026-08-30**: Fixed three implicit-alias bugs found by actually running
1773:   `space_separated_name()` from `models/md/alias_match.py` against every
1774:   implicit-`SPACE_SEPARATED`-alias class name in this design, rather than
1775:   assuming the derivation matched the intended heading text:
1776:   `RelatedAdrs` (would derive `"Related Adrs"`, not `"Related ADRs"` — a
1777:   bug present since round 1, undetected through two subsequent review
1778:   rounds), `ExplicitlyOutOfScope` (would derive `"Explicitly Out Of Scope"`, not `"Explicitly out of scope"`), and `DependsOn` (would
1779:   derive `"Depends On"`, not `"Depends on"`). All three now get an
1780:   explicit `@alias(value=..., type=AliasType.LITERAL)`, the same fix
1781:   already used for `RelatedPrsCommits`. `example.md`'s own heading text
1782:   needed no changes — it already used the intended natural-English
1783:   headings; only the Design Notes' model-class documentation was wrong.
1784:   This verification pass is what qualifies `example.md` as the canonical,
1785:   implementation-ready example (see Current Status) rather than just a
1786:   visually-plausible one.
1787: - **2026-08-30**: Fourth design-review round — eliminated all three
1788:   `LITERAL` aliases added in the entry directly above, per explicit user
1789:   direction to minimize `LITERAL` use wherever a different, still-clear
1790:   spelling makes the implicit `SPACE_SEPARATED` derivation match exactly:
1791:   `RelatedAdrs`/`"Related ADRs"` → `RelatedDecisions`/`"Related Decisions"` (`space_separated_name("RelatedDecisions")` derives this
1792:   exactly) — also a deliberate terminology change, not just a casing fix:
1793:   this codebase intends to phase out ADR in favor of `dec` over time, so
1794:   a brand-new schema adopts the forward-looking name; entries may still
1795:   reference an ADR id, a `dec` id, or any other decision record.
1796:   `ExplicitlyOutOfScope`/`"Explicitly out of scope"` →
1797:   `"Explicitly Out Of Scope"` (matches the derivation exactly; accepted
1798:   as consistent with this codebase's own existing Start-Case multi-word
1799:   headings, e.g. "Acceptance Criteria"). `DependsOn`/`"Depends on"` →
1800:   `"Depends On"` (matches the derivation exactly; reusing the parent's
1801:   own name "Dependencies" for this child was considered and rejected as
1802:   a confusing tautology). `RelatedPrsCommits` keeps its `LITERAL` alias
1803:   — the slash in "Related PRs / Commits" has no casing-only fix, unlike
1804:   the three eliminated here. Updated Design Notes' ASCII diagram, Model
1805:   classes prose, REQ-001, and Task 1.3 to match; `example.md` needs no
1806:   further heading changes since it always used the intended spelling
1807:   (only the `Design Notes` heading text itself and `## Related ADRs`
1808:   cross-reference label conceptually rename to "Related Decisions" — no
1809:   content change needed in the example beyond that heading).
1810: - **2026-08-30**: Fifth design-review round — three more questions
1811:   resolved: (1) **No partial-id-match support** in `find_feat_path_by_id`
1812:   — considered and rejected; an agent that only has a bare `"feat-31"`
1813:   can already resolve the real id for free via `list_feat` (whose
1814:   `FeatSummary` entries carry the real `id`) followed by `get_feat` with
1815:   the resolved id, so adding boundary-matching regex/an ambiguous-match
1816:   error/a scan fallback to the addressing layer would solve a need the
1817:   existing tools already cover. (2) **Confirmed `SPECMGR_FEAT_DIR` is
1818:   mandatory, not optional** — every existing domain has an equivalent env
1819:   var (`SPECMGR_ADR_DIR`, the shared `SPECMGR_DOCS_DIR`), specifically for

(Showing lines 1680-1819 of 2037. Use offset=1820 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && echo \"--- create_feat.py ---\" && cat src/biz/dfch/specmgr/feat/tools/create_feat.py && echo \"--- update.py _update_feat ---\" && grep -n \"_update_feat\" -A 30 src/biz/dfch/specmgr/general/tools/update.py | head -60"
}
```

**Output:**

```
--- create_feat.py ---
# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``@mcp.tool()`` wrapper: create_feat (Task 2.3).

Unlike every other domain's ``create_<d>`` (a fresh server-generated UUID,
always assignable without coordinating with any other in-flight create),
``create_feat`` derives its id (``feat-NNN-slug``) by scanning existing
``feat-*`` folder names for the highest ``NNN`` and adding one, under the
**global** :func:`~biz.dfch.specmgr.feat.tools._lock.feat_create_lock` --
see that module's docstring for why a global (not per-id) lock is needed
here. ``content`` is body markdown only (no frontmatter block), same shape
as ``create_dec``/``create_gol``: the caller's own already-validated body is
persisted byte-for-byte, and only the small, code-constructed frontmatter
YAML block is (re)generated.

**Timestamp format is a deliberate ``feat``-only divergence.** Every other
domain's ``create_<d>`` sets ``created``/``updated`` to
``datetime.now().isoformat(timespec="microseconds")``; `feat`'s own
frontmatter keeps plain ``YYYY-MM-DD`` dates instead
(``datetime.now().date().isoformat()``), matching every one of the 17
pre-existing hand-authored feature files and ADR
e369ee2e-3353-4f92-991c-6367d76d832e's own template -- see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Frontmatter").
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import FeatDocument, FeatFrontmatter, Feature
from ._lock import feat_create_lock
from ._paths import FEAT_FOLDER_PATTERN, README_FILENAME, ensure_feat_base_dir, feature_title, slugify
from ._write import write_feat_file


@mcp.tool(
    name="create_feat",
    title="Create feature",
    description=(
        "Create a new feature: assigns a fresh id, derives a filename from the body's H1 title, "
        "validates the submitted body-only content, and writes the new document to the feature base "
        "directory."
    ),
)
def create_feat(content: str) -> FeatDocument:
    """Create and write a new feature document.

    ``content`` is body markdown only (the ``Feature`` H1 and its sections)
    -- it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh ``feat-NNN-slug`` id (see this module's
    docstring), ``type="feat"``, ``status="planning"`` (always, never
    caller-supplied on create -- `feat`'s own default lifecycle state),
    ``created``/``updated`` both set to today's plain ``YYYY-MM-DD`` date,
    and ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.feat.models.v1.Feature` from it
    (``Feature.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both uncaught -- nothing is written in
    either case, and neither the base directory nor any new folder is
    touched (validation happens before the create lock is even acquired).

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    FeatDocument
        The newly created document, with its assigned ``feat-NNN-slug`` id
        in ``frontmatter.id``.
    """
    body = Feature.from_text(format_text(content))
    slug = slugify(feature_title(body.text))

    with feat_create_lock():
        base_dir = ensure_feat_base_dir()
        new_id = f"feat-{_next_feat_number(base_dir)}-{slug}"

        today = datetime.now().date().isoformat()
        new_frontmatter = FeatFrontmatter(
            id=new_id,
            type="feat",
            status="planning",
            created=today,
            updated=today,
            version=CURRENT_SCHEMA_VERSION,
        )
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)

        write_feat_file(base_dir / new_id / README_FILENAME, new_frontmatter, content)
    return new_doc


def _next_feat_number(base_dir: Path) -> int:
    """Return one past the highest existing ``feat-NNN-...`` folder number under ``base_dir``.

    Scans only folder *names* (not their content) directly under
    ``base_dir`` -- a folder that fails to parse as a feature document still
    counts toward the ``NNN`` derivation, since its name alone is enough to
    reserve that number. Returns ``1`` if ``base_dir`` holds no matching
    folder yet.
    """
    assert isinstance(base_dir, Path), type(base_dir)

    existing = [
        int(match.group(1))
        for entry in base_dir.iterdir()
        if entry.is_dir() and (match := FEAT_FOLDER_PATTERN.match(entry.name))
    ]
    result = max(existing, default=0) + 1
    return result
--- update.py _update_feat ---
40:``feat`` is the one domain whose adapter (``_update_feat``) diverges in two
41-ways from the other eight's identical shape: it bumps ``updated`` to a
42-plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``), not the
43-others' microsecond timestamp, matching ``create_feat``'s own frontmatter
44-convention (see ``.specmgr/feat/feat-31-feature/README.md`` Design Notes,
45-"Frontmatter"); and it resolves ``id`` via ``feat.tools._paths``'s bespoke
46-folder-per-document shortcut, not a flat-file directory scan (see that
47-feature's Design Notes, "Addressing").
48-
49-ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
50-contract (``update_frontmatter``/``update_section``/``option_*``) has no
51-whole-body replace by design.
52-"""
53-
54-from __future__ import annotations
55-
56-from collections.abc import Callable
57-from datetime import datetime
58-from typing import Literal
59-
60-from ...dec.models.v1 import DecDocument, DecFrontmatter, Decision
61-from ...dec.tools._io import load_by_id as load_dec_by_id
62-from ...dec.tools._lock import dec_lock
63-from ...dec.tools._paths import dec_base_dir
64-from ...dec.tools._write import write_dec_file
65-from ...feat.models.v1 import FeatDocument, FeatFrontmatter, Feature
66-from ...feat.tools._io import load_by_id as load_feat_by_id
67-from ...feat.tools._lock import feat_lock
68-from ...feat.tools._paths import feat_base_dir
69-from ...feat.tools._write import write_feat_file
70-from ...gol.models.v1 import GolDocument, GolFrontmatter, Goal
--
443:def _update_feat(id_: str, content: str, begin: int | None, end: int | None) -> FeatDocument:
444-    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).
445-
446-    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
447-    ``write_feat_file``, ``FeatNotFoundError``) with two feat-only
448-    divergences (see the module docstring): ``id_`` resolves via
449-    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
450-    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan; and
451-    ``updated`` is bumped to a plain ``YYYY-MM-DD`` date
452-    (``datetime.now().date().isoformat()``), not the other eight domains'
453-    microsecond timestamp, matching ``create_feat``'s own frontmatter
454-    convention.
455-    """
456-    if begin is not None or end is not None:
457-        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
458-
459-        base_dir = feat_base_dir()
460-        with feat_lock(id_):
461-            path, existing = load_feat_by_id(base_dir, id_)
462-            spliced = splice_body(body_text(path), begin, end, content)
463-            body = Feature.from_text(format_text(spliced))
464-            today = datetime.now().date().isoformat()
465-            fm_data = existing.frontmatter.model_dump()
466-            fm_data["updated"] = today
467-            new_frontmatter = FeatFrontmatter(**fm_data)
468-            new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
469-            write_feat_file(path, new_frontmatter, spliced)
470-        return new_doc

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"_set_status_feat\" -A 30 src/biz/dfch/specmgr/general/tools/set_status.py | head -50"
}
```

**Output:**

```
36:The ``feat`` adapter (``_set_status_feat``) diverges from the other eight
37-whole-body domains' identical shape in the same two ways ``_update_feat``
38-(in ``update.py``) does: it bumps ``updated`` to a plain ``YYYY-MM-DD``
39-date, not the others' microsecond timestamp; and it resolves ``id`` via
40-``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
41-flat-file directory scan (see
42-``.specmgr/feat/feat-31-feature/README.md`` Design Notes).
43-
44-The parameter is intentionally named ``type`` (it matches the frontmatter
45-field vocabulary the client already knows); no enabled ruff rule objects
46-to the builtin shadow. The 10-way union return type is annotation-only --
47-the MCP input schema is built from the parameters, and the SDK
48-serializes whichever concrete document is returned.
49-
50-``superseded_by`` is accepted only for ``type="adr"``: the
51-"superseded by X" status pattern is ADR-specific (no other domain's
52-``XFrontmatter.status`` accepts it). The public :func:`set_status`
53-rejects it for any other ``type`` with a ``ValueError`` before any file
54-access.
55-
56-Neither any ``create_<d>`` tool nor the generic :func:`update` tool
57-accepts a ``status`` argument at all -- this tool is the sole
58-status-change entry point for every domain.
59-
60-``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
61-because the pure, in-memory operation it delegates to shares this
62-wrapper's own name.
63-"""
64-
65-from __future__ import annotations
66-
--
355:def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDocument:
356-    """Replace the status of the feature identified by ``id_``.
357-
358-    Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
359-    ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
360-    :func:`_set_status_req` for the full semantics -- with the same two
361-    feat-only divergences ``_update_feat`` (in ``update.py``) documents:
362-    ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
363-    shortcut, not a flat-file directory scan; and ``updated`` is bumped to
364-    a plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``),
365-    not the other eight domains' microsecond timestamp.
366-    """
367-    assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
368-
369-    base_dir = feat_base_dir()
370-    with feat_lock(id_):
371-        path, existing = load_feat_by_id(base_dir, id_)
372-        raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

Now let's check test files that assert plain-date format, to understand scope of test updates.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -rln \"date().isoformat\\|plain.*date\\|YYYY-MM-DD\\|\\\\\\\\d{4}-\\\\\\\\d{2}-\\\\\\\\d{2}\\$\" tests/feat/ tests/general/tools/ 2>/dev/null"
}
```

**Output:**

```
tests/feat/tools/test_integration.py
tests/general/tools/test_set_status.py
tests/general/tools/__pycache__/test_set_status.cpython-313.pyc

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.9s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"date().isoformat\\|YYYY-MM-DD\\|r\\\"\\\\^\\\\\\\\d\\|isoformat\" tests/feat/tools/test_create_feat.py tests/feat/tools/test_integration.py tests/general/tools/test_update.py tests/general/tools/test_set_status.py 2>/dev/null"
}
```

**Output:**

```
tests/feat/tools/test_create_feat.py:127:        self.assertRegex(result.frontmatter.created or "", r"^\d{4}-\d{2}-\d{2}$")
tests/feat/tools/test_integration.py:217:        #    YYYY-MM-DD date, not the other domains' microsecond timestamp) and preserve
tests/feat/tools/test_integration.py:225:        self.assertRegex(updated.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}$")
tests/feat/tools/test_integration.py:243:        self.assertRegex(in_progress.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}$")

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"feat\\|YYYY-MM-DD\" tests/general/tools/test_set_status.py | head -30"
}
```

**Output:**

```
18:"""Tests for the generic ``set_status`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 4).

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/models/v1/frontmatter.py"
}
```

**Output:**

```
# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Feature (FEAT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `rsk/models/v1/frontmatter.py::RskFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["feat"]`` and narrows the free-form ``status`` to a closed,
hyphen-free four-value lifecycle set, *and* redeclares the default away from
the base's ``"draft"`` (a `feat` document starts life ``"planning"``, not
``"draft"`` -- ``"draft"`` is not part of `feat`'s own closed set) -- see
`.specmgr/feat/feat-31-feature/README.md` Design Notes ("Frontmatter").

`created`/`updated` are inherited unchanged from `MarkdownFrontmatter` as
plain, unvalidated ``str | None`` -- the base model performs no format
validation on either field for any domain (the specific ``YYYY-MM-DD``
convention `feat` uses, versus other domains' microsecond timestamp, is a
tool-layer/`_write.py` concern for Phase 2, not a model-layer one).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md._util import default_if_blank

#: Fixed, closed set of accepted ``status`` values for features -- a
#: deliberately hyphen-free four-value lifecycle (``"progress"``, not
#: ``"in-progress"``), per explicit user direction:
#: ``planning`` (design/requirements still being written), ``progress``
#: (implementation under way), ``review`` (implementation done, pending
#: verification), or ``done`` (shipped).
_ALLOWED_STATUSES = frozenset(
    {
        "planning",
        "progress",
        "review",
        "done",
    }
)

#: Default ``status`` value when the key is absent or blank -- the starting
#: state of a feature's lifecycle. The base `MarkdownFrontmatter`'s own
#: default is ``"draft"``, which is not part of `feat`'s own set.
DEFAULT_FEAT_STATUS = "planning"


class FeatFrontmatter(MarkdownFrontmatter):
    """Feature (FEAT) frontmatter: `MarkdownFrontmatter` narrowed for the ``feat`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"feat"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["feat"] = "feat"``, so a document
        omitting ``type`` entirely still parses as a feature document.
    status:
        One of ``"planning"``, ``"progress"``, ``"review"``, ``"done"``.
        Narrows the base's free-form ``str`` field to this closed four-value
        set; absent/blank defaults to ``"planning"``
        (``_default_blank_status_to_planning`` below, which runs before the
        base's inherited ``_default_blank_status_to_draft``).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["feat"] = "feat"  # type: ignore
    status: str = DEFAULT_FEAT_STATUS

    @field_validator("status", mode="before")
    @classmethod
    def _default_blank_status_to_planning(cls, value: object) -> object:
        """Map an absent/blank ``status`` to ``"planning"`` (not the base's ``"draft"``).

        Runs before the base's inherited ``_default_blank_status_to_draft``
        (Pydantic applies child-class ``mode="before"`` validators first), so
        by the time the base's validator sees the value it is already
        ``"planning"`` and passes it through unchanged.
        """
        return default_if_blank(value, DEFAULT_FEAT_STATUS)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.0s)

_Thinking:_

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 6: Frontmatter timestamp format fix (Task 6.1) - change feat created/updated from plain YYYY-MM-DD to microsecond ISO timestamps in create_feat.py, update.py's _update_feat, set_status.py's _set_status_feat; update Design Notes/Decisions Made; update existing tests asserting plain-date format",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 6: Frontmatter timestamp format fix (Task 6.1) - change feat created/updated from plain YYYY-MM-DD to microsecond ISO timestamps in create_feat.py, update.py's _update_feat, set_status.py's _set_status_feat; update Design Notes/Decisions Made; update existing tests asserting plain-date format",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

No open design questions here — the plan is unambiguous (Task 6.1's scope, target format, and affected files are all spelled out). Proceeding to delegate Phase 6.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 6: Frontmatter timestamp format fix (Task 6.1) - change feat created/updated from plain YYYY-MM-DD to microsecond ISO timestamps in create_feat.py, update.py's _update_feat, set_status.py's _set_status_feat; update Design Notes/Decisions Made; update existing tests asserting plain-date format",
      "status": "in_progress",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 6: Frontmatter timestamp format fix (Task 6.1) - change feat created/updated from plain YYYY-MM-DD to microsecond ISO timestamps in create_feat.py, update.py's _update_feat, set_status.py's _set_status_feat; update Design Notes/Decisions Made; update existing tests asserting plain-date format",
    "status": "in_progress",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 810.6s)

**Tool: task**

**Input:**

```json
{
  "description": "Implement Phase 6 of feat-31",
  "subagent_type": "phase-implementer",
  "prompt": "Implement exactly ONE phase of a feature plan, end to end. You write code and update existing tests only. You do NOT create new tests (there is no new functionality, only a format change), you do NOT commit, and you do NOT start any other phase.\n\n## Plan and phase\n\nPlan file (read it IN FULL first — especially \"Design Notes\" (particularly the \"Frontmatter\" subsection), \"Decisions Made\", and the Phase 6 task under \"Task List\"):\n/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md\n\nPhase to implement: `#### Phase 6: Frontmatter timestamp format fix`\n\nWorking directory: /home/user/src/biz.dfch.SpecMgr (git branch `feat-31-feature`, clean tree).\n\n## Task (verbatim from the plan)\n\n- Task 6.1: Change `feat` frontmatter's `created`/`updated` fields from plain\n  `YYYY-MM-DD` dates to microsecond timestamps\n  (`datetime.now().isoformat(timespec=\"microseconds\")`), matching every\n  other whole-body domain's own convention (`req`/`uc`/`tsk`/`qa`/`prb`/\n  `gol`/`rsk`/`dec`). Affects `feat/tools/create_feat.py` (frontmatter\n  construction), `general/tools/update.py`'s `_update_feat` adapter,\n  `general/tools/set_status.py`'s `_set_status_feat` adapter, the Design\n  Notes' \"Frontmatter\" section (which currently documents the plain-date\n  divergence as deliberate), and any tests asserting the plain-date format\n  (`tests/feat/tools/test_create_feat.py`,\n  `tests/feat/tools/test_integration.py`, `tests/general/tools/`\n  equivalents if any). This reverses this feature's own earlier deliberate\n  design decision (see Decisions Made) — reversing it needs the same care\n  as the original decision: update the Decisions Made log with a new entry\n  explaining why, not just silently change the code.\n\n## Context: what already exists (do not rework it, only fix the timestamp format)\n\nThe `feat` domain (models, tools, resources, prompts) is fully implemented and done (Phases 0-5 already committed). This is a narrow follow-up fix reversing one specific earlier design decision: `feat`'s frontmatter `created`/`updated` fields currently use plain `YYYY-MM-DD` dates (`datetime.now().date().isoformat()`) instead of the microsecond ISO timestamp format every other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`) uses (`datetime.now().isoformat(timespec=\"microseconds\")`).\n\nI already located the exact code sites for you (verified via grep, but re-verify yourself before editing):\n\n1. `src/biz/dfch/specmgr/feat/tools/create_feat.py`:\n   - Module docstring paragraph starting \"**Timestamp format is a deliberate `feat`-only divergence.**\" — describes and justifies the old plain-date behavior. This needs rewriting to remove the divergence claim (feat now matches every other domain).\n   - The `create_feat()` docstring also mentions \"`created`/`updated` both set to today's plain `YYYY-MM-DD` date\" — needs updating.\n   - The actual code: `today = datetime.now().date().isoformat()` used for both `created` and `updated` in `FeatFrontmatter(...)`. Change to `datetime.now().isoformat(timespec=\"microseconds\")` (rename the local variable away from `today` if it no longer reflects a date-only value — check how other domains' `create_<d>.py` name this local variable, e.g. `dec/tools/create_dec.py` or `gol/tools/create_gol.py`, and mirror that naming exactly for consistency).\n\n2. `src/biz/dfch/specmgr/general/tools/update.py`:\n   - Module docstring (around lines 40-47) describing `_update_feat`'s \"two ways\" divergence — one of those two ways (the plain-date `updated` bump) is being eliminated; update this prose to reflect that `_update_feat` now only diverges in the addressing-resolution way (bespoke `feat.tools._paths` folder-per-document shortcut), not in timestamp format.\n   - `_update_feat()` function docstring — same update.\n   - The code: `today = datetime.now().date().isoformat()` and `fm_data[\"updated\"] = today` — change to the microsecond timestamp format, matching how the other 8 domains' `_update_<d>` adapters in this same file do it (check e.g. `_update_dec` or `_update_gol` in the same file for the exact pattern/variable naming to mirror).\n\n3. `src/biz/dfch/specmgr/general/tools/set_status.py`:\n   - Module docstring (around lines 36-42) describing `_set_status_feat`'s divergence — same update as above (only the addressing-resolution divergence remains, not timestamp format).\n   - `_set_status_feat()` function docstring — same update.\n   - The code — find the plain-date `updated` bump inside `_set_status_feat` (similar shape to `_update_feat`'s) and change it to the microsecond timestamp format, mirroring `_set_status_dec`/`_set_status_gol`/etc. in the same file.\n\n4. `.specmgr/feat/feat-31-feature/README.md` — **Design Notes' \"Frontmatter\" section** (search for \"created`/`updated` stay plain `YYYY-MM-DD`\" — it's near the end of the \"Frontmatter\" paragraph in Design Notes, right before the \"Addressing\" subsection heading). This currently says something like: \"`created`/`updated` stay plain `YYYY-MM-DD` (not the other domains' microsecond `T`-separator timestamp) — matching every one of the 17 existing feature files and ADR e369ee2e's own template, a deliberate divergence from the rest of the codebase's frontmatter timestamp convention.\" Update this to state that `created`/`updated` now use the same microsecond ISO timestamp format as every other domain, reversing the earlier stated divergence, with a pointer to the new Decisions Made entry (see below) for the rationale. Do not delete the historical context about the 17 existing hand-authored files (they's still out of scope / unaffected — this only affects documents created/updated via the `feat` MCP tools going forward), just correct the \"stays plain YYYY-MM-DD\" claim.\n\n5. `.specmgr/feat/feat-31-feature/README.md` — **Decisions Made log** (`### Decisions Made` section): add ONE new dated entry (`- **2026-08-30**: ...`) explaining that the earlier \"`feat` frontmatter timestamps stay plain `YYYY-MM-DD`, matching the 17 hand-authored files\" decision (see the \"Frontmatter `version` becomes schema-version-only...\" era entries) is now reversed: `feat`'s `created`/`updated` now use the same microsecond ISO timestamp format as every other whole-body domain, for consistency across the codebase (this was a follow-up decision made after the feature initially shipped, not part of the original five design-review rounds). Be explicit that this is a reversal, matching the Task 6.1 instruction's own requirement to \"update the Decisions Made log with a new entry explaining why, not just silently change the code.\"\n\n6. Tests — search `tests/feat/` and `tests/general/tools/` for any assertion tied to the plain-date format. I already found these two:\n   - `tests/feat/tools/test_create_feat.py` line ~127: `self.assertRegex(result.frontmatter.created or \"\", r\"^\\d{4}-\\d{2}-\\d{2}$\")` — this regex only matches a bare date, not a full ISO timestamp with microseconds; update it to match the new format (look at how another domain's `test_create_<d>.py` (e.g. `tests/dec/tools/test_create_dec.py`) asserts its timestamp format and mirror that regex/assertion style).\n   - `tests/feat/tools/test_integration.py` — two occurrences around lines 217-243 (one is just a comment mentioning the old format, one is `self.assertRegex(updated.frontmatter.updated or \"\", r\"^\\d{4}-\\d{2}-\\d{2}$\")` used twice) — update the regex assertions AND the explanatory comment to match the new format/behavior. Look at how `tests/dec/tools/test_integration.py` (or another domain's integration test) asserts its `updated` timestamp format for the mirror pattern.\n   - Do a final `grep -rn \"date().isoformat\\|YYYY-MM-DD\" tests/feat/ tests/general/tools/*.py src/biz/dfch/specmgr/feat/ src/biz/dfch/specmgr/general/tools/update.py src/biz/dfch/specmgr/general/tools/set_status.py` yourself before finishing, to make sure nothing is missed (docstrings, comments, or test assertions).\n   - Do NOT write any brand-new test file or add new test methods for this — this is a format fix to existing behavior/tests only, no new functionality is being added. Only *update* what already exists.\n\n## Important constraints\n\n- Do NOT touch any other domain's code (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`adr`) — only `feat`-specific code paths within `create_feat.py`/`update.py`/`set_status.py`.\n- Do NOT change `FeatFrontmatter`'s model (no format validation exists there today per its own docstring, and none should be added — this is purely a tool-layer change, same as the original decision documented in `frontmatter.py`'s own module docstring, which explicitly says the timestamp convention is \"a tool-layer/`_write.py` concern... not a model-layer one\").\n- Do NOT touch `feat/tools/_write.py` unless you find it also hardcodes something date-related (check it, but I don't believe it does based on my earlier review).\n- Preserve every other existing behavior of `create_feat`/`_update_feat`/`_set_status_feat` exactly (locking, addressing, id/type/version preservation, etc.) — this is a single, narrow format change.\n- Do not create/switch git branches. Do not commit.\n\n## Phase-end quality gate (mandatory — run yourself and report exact command + output)\n\nRun, in order, and report concrete evidence (command + relevant output, not just \"passed\"):\n\n1. `uv run --frozen ruff format --check`\n2. `uv run --frozen ruff check`\n3. `uv run --frozen vulture src/ whitelist.py --min-confidence 60`\n4. `uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"` (full suite must be green; report the final tally, e.g. \"NNNN tests, OK\")\n5. `uv run --frozen specmgr unused-code` (must report clean)\n\nIf any of these newly fail because of your change, fix it before reporting done.\n\n## Progress-section update (mandatory, per the plan's own phase-end convention)\n\nUpdate `.specmgr/feat/feat-31-feature/README.md`'s Progress section:\n- Mark Task 6.1 as `[x]` completed in the Task List, with a `— status: completed (2026-08-30)` note describing what was actually done (mirror the style of the other completed tasks' status notes in this same file).\n- Add a new dated entry under \"### Recent Updates\" (at the top, since that section is newest-first) titled something like `#### Update 2026-08-30 (Phase 6 complete — frontmatter timestamp format fix implemented)`, describing exactly what changed (the 3 src files, the Design Notes correction, the new Decisions Made entry, and which 2 test files were updated), plus the quality-gate evidence (test count, etc.).\n- Update \"### Current Status\" to reflect Phase 6 is now complete (this feature's frontmatter `status` field — check whether it should move back to `done` now that this follow-up is complete; use your judgment based on how the plan handled the status field when Phase 6 was first added, i.e. it was moved from `done` to `in-progress` when Phase 6 was added as a not-started follow-up — now that Phase 6 is done, it likely should move back to `done`). Also bump the frontmatter `version` (semver patch or minor bump — check the file's own version-bumping convention used for prior phase completions) and `updated` date at the top of the README file itself.\n- Do NOT touch the \"### Blockers\" section (already resolved, no changes needed) or any of the older historical \"Recent Updates\" entries.\n\n## What to report back to me (your one final message)\n\n- Confirmation of every file you changed (list them).\n- The exact quality-gate commands you ran and their concrete pass/fail evidence (final test tally, ruff/vulture/unused-code output summary).\n- Confirmation that no new test files/methods were added, only existing assertions updated.\n- Confirmation that the Decisions Made log and Design Notes were both updated as instructed.\n- Confirmation you did NOT commit and did NOT start any other phase.\n- Any blockers or judgment calls you had to make that weren't spelled out explicitly above."
}
```

**Output:**

```
<task id="ses_fac0f1c80ffetCAfijJAefvFLS" state="completed">
<task_result>
## Summary

I implemented **Phase 6 (Task 6.1)** of the `feat-31-feature` plan: reverting `feat`'s frontmatter `created`/`updated` fields from plain `YYYY-MM-DD` dates back to the microsecond ISO timestamp format every other whole-body domain uses.

### Files changed

**Source (behavior + docstrings):**
- `src/biz/dfch/specmgr/feat/tools/create_feat.py` — `today = datetime.now().date().isoformat()` → `now = datetime.now().isoformat(timespec="microseconds")` (variable renamed to match `dec`/`gol`'s convention), used for both `created`/`updated`; module + function docstrings updated.
- `src/biz/dfch/specmgr/general/tools/update.py` — `_update_feat`'s two branches (whole-body + line-range) switched to the microsecond timestamp, mirroring `_update_dec`; module + function docstrings updated to state the only remaining `feat` divergence is addressing resolution, not timestamp format.
- `src/biz/dfch/specmgr/general/tools/set_status.py` — same change in `_set_status_feat`; module, function, and public `set_status()` docstrings updated.
- Four **stale-doc corrections** found via the instructed grep sweep, not explicitly named in Task 6.1 but factually wrong otherwise: `feat/models/v1/frontmatter.py` (module docstring), `feat/models/v1/body.py` (`UpdateEntry` docstring — only its contrast-with-frontmatter clause, not the still-distinct body-level ISO8601 format), `feat/prompts/create_feat.py` (module docstring), and the packaged `feat/data/feat_create_instructions.md`/`feat_update_instructions.md` (LLM-facing narrated text).
- `docs/feat_schema.json` + `src/biz/dfch/specmgr/feat/data/feat_schema.json` — regenerated via `specmgr schema --type feat` (both invocations, confirmed byte-identical) since they embed the changed `UpdateEntry` docstring.
- `docs/api/*.md` (6 files) — regenerated via `specmgr docs`; `specmgr mcp-docs` re-run, zero further diff.

**Tests (existing assertions only, no new tests/methods):**
- `tests/feat/tools/test_create_feat.py` — regex `^\d{4}-\d{2}-\d{2}$` → `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$`.
- `tests/feat/tools/test_integration.py` — same regex fix (2 occurrences) + explanatory comment updated.

**Plan doc:** `.specmgr/feat/feat-31-feature/README.md` — Task 6.1 marked `[x]` completed; Design Notes' "Frontmatter" section corrected (no longer claims the plain-date divergence); new Decisions Made entry explicitly reversing the earlier decision; new Current Status + Recent Updates entries; frontmatter `status: in-progress → done`, `version: 1.12.0 → 1.13.0`.

### Quality gate (all green)
1. `uv run --frozen ruff format --check` → `1286 files already formatted`
2. `uv run --frozen ruff check` → `All checks passed!`
3. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` → no output (clean)
4. `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` → `Ran 2228 tests ... OK` (unchanged count — no new tests added)
5. `uv run --frozen specmgr unused-code` → `No unused code found`

### Confirmations
- No new test files/methods added — only existing assertions updated (verified via `git diff --stat`, only 2 test files touched with small diffs).
- Decisions Made log and Design Notes both updated per instructions.
- No commit made; no other phase started. Working tree has only unstaged changes for the orchestrator to review/commit.

### Judgment calls (not spelled out verbatim)
- Fixed 4 additional stale docstring/data-file mentions beyond the 3 `src` files + 2 test files literally named in the task (in `feat/models/v1/frontmatter.py`, `feat/models/v1/body.py`, `feat/prompts/create_feat.py`, and the two packaged instructions `.md` files) — justified by the task's own instruction to run a broad grep sweep "to make sure nothing is missed (docstrings, comments...)" across `src/biz/dfch/specmgr/feat/` as a whole.
- Regenerated `docs/feat_schema.json`/packaged schema copy since they embed the changed docstring text — not explicitly called out in the task, but necessary to avoid drift.
- Chose a regex-based test assertion (matching the microsecond ISO shape) rather than restructuring to `dec`'s `assertNotEqual` style, to keep the diff minimal and preserve existing test structure/semantics.
- Bumped README `version` to `1.13.0` (minor bump) and `status` back to `done`, inferring from how Phase 5's completion and Phase 6's initial recording each bumped version/status.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.6s)

Now let me independently verify the work.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short && echo \"---DIFF STAT---\" && git diff --stat"
}
```

**Output:**

```
 M .specmgr/feat/feat-31-feature/README.md
 M docs/api/biz.dfch.specmgr.feat.models.v1.body.md
 M docs/api/biz.dfch.specmgr.feat.models.v1.frontmatter.md
 M docs/api/biz.dfch.specmgr.feat.prompts.create_feat.md
 M docs/api/biz.dfch.specmgr.feat.tools.create_feat.md
 M docs/api/biz.dfch.specmgr.general.tools.set_status.md
 M docs/api/biz.dfch.specmgr.general.tools.update.md
 M docs/feat_schema.json
 M src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
 M src/biz/dfch/specmgr/feat/data/feat_schema.json
 M src/biz/dfch/specmgr/feat/data/feat_update_instructions.md
 M src/biz/dfch/specmgr/feat/models/v1/body.py
 M src/biz/dfch/specmgr/feat/models/v1/frontmatter.py
 M src/biz/dfch/specmgr/feat/prompts/create_feat.py
 M src/biz/dfch/specmgr/feat/tools/create_feat.py
 M src/biz/dfch/specmgr/general/tools/set_status.py
 M src/biz/dfch/specmgr/general/tools/update.py
 M tests/feat/tools/test_create_feat.py
 M tests/feat/tools/test_integration.py
---DIFF STAT---
 .specmgr/feat/feat-31-feature/README.md            | 181 +++++++++++++++++++--
 docs/api/biz.dfch.specmgr.feat.models.v1.body.md   |   3 +-
 .../biz.dfch.specmgr.feat.models.v1.frontmatter.md |   6 +-
 .../biz.dfch.specmgr.feat.prompts.create_feat.md   |   6 +-
 .../api/biz.dfch.specmgr.feat.tools.create_feat.md |  19 +--
 .../biz.dfch.specmgr.general.tools.set_status.md   |  26 +--
 docs/api/biz.dfch.specmgr.general.tools.update.md  |  29 ++--
 docs/feat_schema.json                              |   2 +-
 .../specmgr/feat/data/feat_create_instructions.md  |   3 +-
 src/biz/dfch/specmgr/feat/data/feat_schema.json    |   2 +-
 .../specmgr/feat/data/feat_update_instructions.md  |   5 +-
 src/biz/dfch/specmgr/feat/models/v1/body.py        |   3 +-
 src/biz/dfch/specmgr/feat/models/v1/frontmatter.py |   6 +-
 src/biz/dfch/specmgr/feat/prompts/create_feat.py   |   6 +-
 src/biz/dfch/specmgr/feat/tools/create_feat.py     |  25 ++-
 src/biz/dfch/specmgr/general/tools/set_status.py   |  30 ++--
 src/biz/dfch/specmgr/general/tools/update.py       |  37 ++---
 tests/feat/tools/test_create_feat.py               |   2 +-
 tests/feat/tools/test_integration.py               |   8 +-
 19 files changed, 277 insertions(+), 122 deletions(-)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.6s)

Let's inspect the key diffs.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff src/biz/dfch/specmgr/feat/tools/create_feat.py"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/feat/tools/create_feat.py b/src/biz/dfch/specmgr/feat/tools/create_feat.py
index 9e6c93e..4e899a4 100644
--- a/src/biz/dfch/specmgr/feat/tools/create_feat.py
+++ b/src/biz/dfch/specmgr/feat/tools/create_feat.py
@@ -28,14 +28,13 @@ as ``create_dec``/``create_gol``: the caller's own already-validated body is
 persisted byte-for-byte, and only the small, code-constructed frontmatter
 YAML block is (re)generated.
 
-**Timestamp format is a deliberate ``feat``-only divergence.** Every other
-domain's ``create_<d>`` sets ``created``/``updated`` to
-``datetime.now().isoformat(timespec="microseconds")``; `feat`'s own
-frontmatter keeps plain ``YYYY-MM-DD`` dates instead
-(``datetime.now().date().isoformat()``), matching every one of the 17
-pre-existing hand-authored feature files and ADR
-e369ee2e-3353-4f92-991c-6367d76d832e's own template -- see
-``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Frontmatter").
+``created``/``updated`` use the same microsecond ISO timestamp format
+(``datetime.now().isoformat(timespec="microseconds")``) as every other
+whole-body domain's ``create_<d>`` -- an earlier, deliberate ``feat``-only
+divergence (plain ``YYYY-MM-DD`` dates, matching the 17 pre-existing
+hand-authored feature files) was reversed for cross-domain consistency; see
+``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Frontmatter") and
+Decisions Made.
 """
 
 from __future__ import annotations
@@ -69,8 +68,8 @@ def create_feat(content: str) -> FeatDocument:
     built by this tool: a fresh ``feat-NNN-slug`` id (see this module's
     docstring), ``type="feat"``, ``status="planning"`` (always, never
     caller-supplied on create -- `feat`'s own default lifecycle state),
-    ``created``/``updated`` both set to today's plain ``YYYY-MM-DD`` date,
-    and ``version`` set to the current ``models.md`` schema version.
+    ``created``/``updated`` both set to the current timestamp, and
+    ``version`` set to the current ``models.md`` schema version.
 
     ``content`` is validated by constructing a
     :class:`~biz.dfch.specmgr.feat.models.v1.Feature` from it
@@ -102,13 +101,13 @@ def create_feat(content: str) -> FeatDocument:
         base_dir = ensure_feat_base_dir()
         new_id = f"feat-{_next_feat_number(base_dir)}-{slug}"
 
-        today = datetime.now().date().isoformat()
+        now = datetime.now().isoformat(timespec="microseconds")
         new_frontmatter = FeatFrontmatter(
             id=new_id,
             type="feat",
             status="planning",
-            created=today,
-            updated=today,
+            created=now,
+            updated=now,
             version=CURRENT_SCHEMA_VERSION,
         )
         new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.4s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff src/biz/dfch/specmgr/general/tools/update.py src/biz/dfch/specmgr/general/tools/set_status.py"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/general/tools/set_status.py b/src/biz/dfch/specmgr/general/tools/set_status.py
index a75e0d5..beb0e21 100644
--- a/src/biz/dfch/specmgr/general/tools/set_status.py
+++ b/src/biz/dfch/specmgr/general/tools/set_status.py
@@ -34,12 +34,14 @@ previous per-domain ADR status tool's function body (same ``adr_lock``,
 ``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
 
 The ``feat`` adapter (``_set_status_feat``) diverges from the other eight
-whole-body domains' identical shape in the same two ways ``_update_feat``
-(in ``update.py``) does: it bumps ``updated`` to a plain ``YYYY-MM-DD``
-date, not the others' microsecond timestamp; and it resolves ``id`` via
+whole-body domains' identical shape in the same way ``_update_feat``
+(in ``update.py``) does: it resolves ``id`` via
 ``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
 flat-file directory scan (see
-``.specmgr/feat/feat-31-feature/README.md`` Design Notes).
+``.specmgr/feat/feat-31-feature/README.md`` Design Notes). It bumps
+``updated`` to the same microsecond timestamp as every other domain --
+an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was
+reversed for cross-domain consistency; see that feature's Decisions Made.
 
 The parameter is intentionally named ``type`` (it matches the frontmatter
 field vocabulary the client already knows); no enabled ruff rule objects
@@ -357,12 +359,11 @@ def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDo
 
     Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
     ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
-    :func:`_set_status_req` for the full semantics -- with the same two
-    feat-only divergences ``_update_feat`` (in ``update.py``) documents:
+    :func:`_set_status_req` for the full semantics -- with the same
+    feat-only divergence ``_update_feat`` (in ``update.py``) documents:
     ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
-    shortcut, not a flat-file directory scan; and ``updated`` is bumped to
-    a plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``),
-    not the other eight domains' microsecond timestamp.
+    shortcut, not a flat-file directory scan. ``updated`` is bumped to the
+    same microsecond timestamp as every other domain.
     """
     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
 
@@ -371,10 +372,10 @@ def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDo
         path, existing = load_feat_by_id(base_dir, id_)
         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
 
-        today = datetime.now().date().isoformat()
+        now = datetime.now().isoformat(timespec="microseconds")
         fm_data = existing.frontmatter.model_dump()
         fm_data["status"] = status
-        fm_data["updated"] = today
+        fm_data["updated"] = now
         new_frontmatter = FeatFrontmatter(**fm_data)
         new_doc = FeatDocument(frontmatter=new_frontmatter, body=existing.body)
         write_feat_file(path, new_frontmatter, raw_body)
@@ -444,10 +445,9 @@ def set_status(
 
     For the nine whole-body domains the existing file's frontmatter is
     carried over with every field preserved except ``status`` (replaced)
-    and ``updated`` (bumped to the current timestamp -- a plain
-    ``YYYY-MM-DD`` date for ``feat``, a microsecond timestamp for the other
-    eight); the body is never touched -- its raw, on-disk markdown (not a
-    render of the parsed model) is re-read and re-persisted verbatim. For
+    and ``updated`` (bumped to the current microsecond timestamp); the
+    body is never touched -- its raw, on-disk markdown (not a render of
+    the parsed model) is re-read and re-persisted verbatim. For
     ``type="adr"`` the change delegates to
     ``models.adr.v1.mutations.set_status`` (which composes ``status`` as
     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given)
diff --git a/src/biz/dfch/specmgr/general/tools/update.py b/src/biz/dfch/specmgr/general/tools/update.py
index 0e49387..868fbf4 100644
--- a/src/biz/dfch/specmgr/general/tools/update.py
+++ b/src/biz/dfch/specmgr/general/tools/update.py
@@ -37,14 +37,15 @@ the builtin shadow. The 9-way union return type is annotation-only -- the
 MCP input schema is built from the parameters, and the SDK serializes
 whichever concrete document is returned.
 
-``feat`` is the one domain whose adapter (``_update_feat``) diverges in two
-ways from the other eight's identical shape: it bumps ``updated`` to a
-plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``), not the
-others' microsecond timestamp, matching ``create_feat``'s own frontmatter
-convention (see ``.specmgr/feat/feat-31-feature/README.md`` Design Notes,
-"Frontmatter"); and it resolves ``id`` via ``feat.tools._paths``'s bespoke
-folder-per-document shortcut, not a flat-file directory scan (see that
-feature's Design Notes, "Addressing").
+``feat`` is the one domain whose adapter (``_update_feat``) diverges from
+the other eight's identical shape in how it resolves ``id``: via
+``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
+flat-file directory scan (see
+``.specmgr/feat/feat-31-feature/README.md`` Design Notes, "Addressing").
+It bumps ``updated`` to the same microsecond timestamp as every other
+domain -- an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date)
+was reversed for cross-domain consistency; see that feature's Decisions
+Made.
 
 ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
 contract (``update_frontmatter``/``update_section``/``option_*``) has no
@@ -444,14 +445,12 @@ def _update_feat(id_: str, content: str, begin: int | None, end: int | None) ->
     """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).
 
     Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
-    ``write_feat_file``, ``FeatNotFoundError``) with two feat-only
-    divergences (see the module docstring): ``id_`` resolves via
+    ``write_feat_file``, ``FeatNotFoundError``) with one feat-only
+    divergence (see the module docstring): ``id_`` resolves via
     ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
-    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan; and
-    ``updated`` is bumped to a plain ``YYYY-MM-DD`` date
-    (``datetime.now().date().isoformat()``), not the other eight domains'
-    microsecond timestamp, matching ``create_feat``'s own frontmatter
-    convention.
+    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
+    ``updated`` is bumped to the same microsecond timestamp as every other
+    domain.
     """
     if begin is not None or end is not None:
         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
@@ -461,9 +460,9 @@ def _update_feat(id_: str, content: str, begin: int | None, end: int | None) ->
             path, existing = load_feat_by_id(base_dir, id_)
             spliced = splice_body(body_text(path), begin, end, content)
             body = Feature.from_text(format_text(spliced))
-            today = datetime.now().date().isoformat()
+            now = datetime.now().isoformat(timespec="microseconds")
             fm_data = existing.frontmatter.model_dump()
-            fm_data["updated"] = today
+            fm_data["updated"] = now
             new_frontmatter = FeatFrontmatter(**fm_data)
             new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
             write_feat_file(path, new_frontmatter, spliced)
@@ -474,9 +473,9 @@ def _update_feat(id_: str, content: str, begin: int | None, end: int | None) ->
     base_dir = feat_base_dir()
     with feat_lock(id_):
         path, existing = load_feat_by_id(base_dir, id_)
-        today = datetime.now().date().isoformat()
+        now = datetime.now().isoformat(timespec="microseconds")
         fm_data = existing.frontmatter.model_dump()
-        fm_data["updated"] = today
+        fm_data["updated"] = now
         new_frontmatter = FeatFrontmatter(**fm_data)
         new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
         write_feat_file(path, new_frontmatter, content)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

This looks correct and matches the required change exactly. Let's check the test diffs and the other feat-related doc/data changes.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff tests/feat/tools/test_create_feat.py tests/feat/tools/test_integration.py"
}
```

**Output:**

```
diff --git a/tests/feat/tools/test_create_feat.py b/tests/feat/tools/test_create_feat.py
index 3d7f1d2..9aae0c7 100644
--- a/tests/feat/tools/test_create_feat.py
+++ b/tests/feat/tools/test_create_feat.py
@@ -124,7 +124,7 @@ class TestCreateFeat(TempFeatDirTestCase):
         self.assertEqual(result.frontmatter.status, "planning")
         self.assertIsNotNone(result.frontmatter.created)
         self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
-        self.assertRegex(result.frontmatter.created or "", r"^\d{4}-\d{2}-\d{2}$")
+        self.assertRegex(result.frontmatter.created or "", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$")
         self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
         self.assertEqual(result.body.text, "Feature: Example Widget")
 
diff --git a/tests/feat/tools/test_integration.py b/tests/feat/tools/test_integration.py
index 13c5309..3b21f77 100644
--- a/tests/feat/tools/test_integration.py
+++ b/tests/feat/tools/test_integration.py
@@ -213,8 +213,8 @@ class TestFeatLifecycleIntegration(TempFeatDirTestCase):
         self.assertEqual(page.results[0].title, "Example Widget")
         self.assertEqual(page.results[0].path, str(expected_path))
 
-        # 4. update (type="feat", whole-body): must bump only `updated` (a plain
-        #    YYYY-MM-DD date, not the other domains' microsecond timestamp) and preserve
+        # 4. update (type="feat", whole-body): must bump only `updated` (the same
+        #    microsecond timestamp format every other domain uses) and preserve
         #    id/type/status/created/version (ACC-004).
         updated = update(feat_id, "feat", _REVISED_BODY)
         self.assertEqual(updated.frontmatter.id, created.frontmatter.id)
@@ -222,7 +222,7 @@ class TestFeatLifecycleIntegration(TempFeatDirTestCase):
         self.assertEqual(updated.frontmatter.created, created.frontmatter.created)
         self.assertEqual(updated.frontmatter.status, "planning")
         self.assertEqual(updated.frontmatter.version, created.frontmatter.version)
-        self.assertRegex(updated.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}$")
+        self.assertRegex(updated.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$")
         self.assertEqual(len(updated.body.plan.requirements.items), 2)
 
         # 4b. update (type="feat", line-range): a single-line splice must round-trip
@@ -240,7 +240,7 @@ class TestFeatLifecycleIntegration(TempFeatDirTestCase):
         self.assertEqual(in_progress.frontmatter.status, "progress")
         self.assertEqual(in_progress.frontmatter.id, updated.frontmatter.id)
         self.assertEqual(in_progress.frontmatter.created, updated.frontmatter.created)
-        self.assertRegex(in_progress.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}$")
+        self.assertRegex(in_progress.frontmatter.updated or "", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$")
         self.assertEqual(len(in_progress.body.plan.requirements.items), 2)
 
         # 6. get_feat: must reflect the latest on-disk state.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

Good — correct, minimal, matches other domains' patterns. Now check the extra doc/data fixes and grep for any remaining stale references.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff src/biz/dfch/specmgr/feat/models/v1/frontmatter.py src/biz/dfch/specmgr/feat/models/v1/body.py src/biz/dfch/specmgr/feat/prompts/create_feat.py"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/feat/models/v1/body.py b/src/biz/dfch/specmgr/feat/models/v1/body.py
index 5950e46..43ae0fe 100644
--- a/src/biz/dfch/specmgr/feat/models/v1/body.py
+++ b/src/biz/dfch/specmgr/feat/models/v1/body.py
@@ -430,7 +430,8 @@ class UpdateEntry(MarkdownSection4):
     """`#### {timestamp} — {title}` under `### Updates` -- one update entry.
 
     The timestamp format is deliberately not the same format as frontmatter
-    `created`/`updated` (plain `YYYY-MM-DD`) -- this format is scoped to
+    `created`/`updated` (a `datetime.isoformat(timespec="microseconds")`
+    value, e.g. `2026-08-30T14:23:01.123456`) -- this format is scoped to
     `### Updates`/`### Decisions Made` entry headings only, hand/LLM-authored
     body content, not tool-generated frontmatter.
 
diff --git a/src/biz/dfch/specmgr/feat/models/v1/frontmatter.py b/src/biz/dfch/specmgr/feat/models/v1/frontmatter.py
index a020f8d..a62fc99 100644
--- a/src/biz/dfch/specmgr/feat/models/v1/frontmatter.py
+++ b/src/biz/dfch/specmgr/feat/models/v1/frontmatter.py
@@ -27,9 +27,9 @@ the base's ``"draft"`` (a `feat` document starts life ``"planning"``, not
 
 `created`/`updated` are inherited unchanged from `MarkdownFrontmatter` as
 plain, unvalidated ``str | None`` -- the base model performs no format
-validation on either field for any domain (the specific ``YYYY-MM-DD``
-convention `feat` uses, versus other domains' microsecond timestamp, is a
-tool-layer/`_write.py` concern for Phase 2, not a model-layer one).
+validation on either field for any domain (the specific microsecond
+timestamp convention every domain, including `feat`, uses is a
+tool-layer/`_write.py` concern, not a model-layer one).
 """
 
 from __future__ import annotations
diff --git a/src/biz/dfch/specmgr/feat/prompts/create_feat.py b/src/biz/dfch/specmgr/feat/prompts/create_feat.py
index f960c53..7eca3aa 100644
--- a/src/biz/dfch/specmgr/feat/prompts/create_feat.py
+++ b/src/biz/dfch/specmgr/feat/prompts/create_feat.py
@@ -27,9 +27,9 @@ through drafting a brand-new Feature (FEAT) document using the existing
 (``id``/``type``/``status``/``created``/``updated``/``version``) -- the
 caller only ever supplies body markdown. Unlike every other domain in this
 codebase, ``id`` is not a server-generated UUID but a fresh
-``feat-NNN-slug`` derived from the H1 title, and ``created``/``updated``
-are plain ``YYYY-MM-DD`` dates, not the microsecond timestamp most other
-domains use (REQ-004).
+``feat-NNN-slug`` derived from the H1 title (REQ-004); ``created``/
+``updated`` use the same microsecond timestamp format as every other
+domain.
 
 Naming note: this prompt is named ``create_feat``, the same name as the
 ``@mcp.tool()`` in ``feat/tools/create_feat.py``. This is not a collision

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

All these are correct fact-corrections consistent with the reversal. Let's verify data files and check for any leftover stale references.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff src/biz/dfch/specmgr/feat/data/feat_create_instructions.md src/biz/dfch/specmgr/feat/data/feat_update_instructions.md\necho \"---- grep leftover stale refs ----\"\ngrep -rn \"date().isoformat\\|plain.*YYYY-MM-DD\\|YYYY-MM-DD.*divergence\" src/biz/dfch/specmgr/feat/ src/biz/dfch/specmgr/general/tools/update.py src/biz/dfch/specmgr/general/tools/set_status.py tests/feat/ tests/general/tools/ 2>/dev/null"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/feat/data/feat_create_instructions.md b/src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
index c882833..d3930b1 100644
--- a/src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
+++ b/src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
@@ -6,8 +6,7 @@ every write to disk goes through the specmgr MCP tools listed below.
 There is no frontmatter for you to draft: `create_feat` builds
 id/type/status/created/updated/version automatically -- a fresh
 `feat-NNN-slug` id, `status="planning"` always (never caller-supplied on
-create), and plain `YYYY-MM-DD` dates (not the microsecond timestamp most
-other domains use).
+create), and the current microsecond timestamp for `created`/`updated`.
 
 Make a todo list and use the question tool.
 
diff --git a/src/biz/dfch/specmgr/feat/data/feat_update_instructions.md b/src/biz/dfch/specmgr/feat/data/feat_update_instructions.md
index d5a68a0..766403e 100644
--- a/src/biz/dfch/specmgr/feat/data/feat_update_instructions.md
+++ b/src/biz/dfch/specmgr/feat/data/feat_update_instructions.md
@@ -61,9 +61,8 @@ revise.
     read the current body first (step 1) and carry forward every section
     you are not intentionally changing, or it will be dropped.
     `id`/`type`/`created`/`version` are preserved automatically
-    regardless of what you submit; only `updated` changes (a plain
-    `YYYY-MM-DD` date, not the microsecond timestamp most other domains
-    use).
+    regardless of what you submit; only `updated` changes (the current
+    microsecond timestamp, same as every other domain).
 - A change to `status` -> `set_status(id, type="feat", status)` instead
   -- `update` never accepts or changes `status`. `status` must be one
   of: planning, progress, review, done (no hyphens -- `progress`, not
---- grep leftover stale refs ----
src/biz/dfch/specmgr/feat/tools/create_feat.py:34:divergence (plain ``YYYY-MM-DD`` dates, matching the 17 pre-existing
src/biz/dfch/specmgr/general/tools/update.py:46:domain -- an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date)
src/biz/dfch/specmgr/general/tools/set_status.py:43:an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

Those three remaining hits are historical/explanatory mentions of the reversed divergence (correctly phrased as past-tense), not stale claims. Clean. Now let's verify the README.md plan updates (Design Notes, Decisions Made, Task List, Progress).

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .specmgr/feat/feat-31-feature/README.md | head -250"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-31-feature/README.md b/.specmgr/feat/feat-31-feature/README.md
index ea03fff..f8f461c 100644
--- a/.specmgr/feat/feat-31-feature/README.md
+++ b/.specmgr/feat/feat-31-feature/README.md
@@ -1,9 +1,9 @@
 ---
 created: 2026-08-30
 id: feat-31-feature
-status: in-progress
+status: done
 updated: 2026-08-30
-version: 1.12.0
+version: 1.13.0
 ---
 
 # Feature: Formalize the Feature artifact type ("feat")
@@ -427,11 +427,16 @@ machine-managed) — the historical hand-bumped "plan revision" meaning
 (`feat-4-use-cases` reaching `1.7.0`, `feat-5-md-model-parser` reaching
 `1.16.4` by hand) is retired for documents created under this schema;
 revision history is tracked via `created`/`updated` plus git history
-instead, per user direction. `created`/`updated` stay plain `YYYY-MM-DD`
-(not the other domains' microsecond `T`-separator timestamp) — matching
-every one of the 17 existing feature files and ADR e369ee2e's own template,
-a deliberate divergence from the rest of the codebase's frontmatter
-timestamp convention.
+instead, per user direction. `created`/`updated` use the same
+microsecond ISO timestamp (`datetime.now().isoformat(timespec="microseconds")`)
+as every other whole-body domain — **this reverses an earlier, deliberate
+divergence** (plain `YYYY-MM-DD` dates, matching every one of the 17
+pre-existing hand-authored feature files and ADR e369ee2e's own
+template), reversed as a Phase 6 follow-up for cross-domain consistency;
+see Decisions Made for the rationale. The 17 pre-existing feature files
+themselves remain out of scope/unaffected by this change (see Scope) —
+this only affects documents created/updated via the `feat` MCP tools
+going forward.
 
 **Addressing** (the genuinely novel part — see REQ-004):
 
@@ -815,7 +820,7 @@ discipline.
 
 #### Phase 6: Frontmatter timestamp format fix
 
-- [ ] Task 6.1: Change `feat` frontmatter's `created`/`updated` fields
+- [x] Task 6.1: Change `feat` frontmatter's `created`/`updated` fields
   from plain `YYYY-MM-DD` dates to microsecond timestamps
   (`datetime.now().isoformat(timespec="microseconds")`), matching every
   other whole-body domain's own convention (`req`/`uc`/`tsk`/`qa`/`prb`/
@@ -827,10 +832,24 @@ discipline.
   format (`tests/feat/tools/test_create_feat.py`,
   `tests/feat/tools/test_integration.py`, `tests/general/tools/`
   equivalents if any). This reverses this feature's own earlier
-  deliberate design decision (see Decisions Made) — reversing it needs
-  the same care as the original decision: update the Decisions Made log
+  deliberate design decision (see Decisions Made): update the Decisions Made log
   with a new entry explaining why, not just silently change the code —
-  depends on: Phase 5 complete — status: not-started
+  depends on: Phase 5 complete — status: completed (2026-08-30). Beyond
+  the three enumerated `src` files, also corrected four stale docstring/
+  data-file mentions of the old plain-date behavior that would otherwise
+  have been left inaccurate: `feat/models/v1/frontmatter.py`'s module
+  docstring, `feat/models/v1/body.py`'s `UpdateEntry` docstring (its
+  contrast with frontmatter's format, not the body-level ISO8601
+  `### Updates`/`### Decisions Made` heading format itself, which is
+  unchanged and stays deliberately different), `feat/prompts/create_feat.py`'s
+  module docstring, and the packaged `feat/data/feat_create_instructions.md`/
+  `feat_update_instructions.md` narrated-instruction text read by the
+  `create_feat`/`update_feat` prompts. `docs/feat_schema.json` and the
+  packaged `feat/data/feat_schema.json` copy were regenerated
+  (`specmgr schema --type feat` both ways) since they embed the changed
+  `UpdateEntry` docstring text verbatim; `specmgr docs`/`specmgr mcp-docs`
+  were also re-run and confirmed to only touch the expected six
+  `docs/api/*.md` files (no further drift).
 
 **Note:** If a task's scope changes mid-flight, edit its description in
 place; rely on git history (`git log -p` on this file) to recover what was
@@ -840,6 +859,34 @@ originally planned, rather than keeping a second copy of the task around.
 
 ### Current Status
 
+**As of 2026-08-30 (Phase 6 complete — frontmatter timestamp format fix
+implemented; feature done again)**: Task 6.1 is implemented and this
+feature is **done** again. `feat` frontmatter's `created`/`updated`
+fields now use the same microsecond ISO timestamp
+(`datetime.now().isoformat(timespec="microseconds")`) as every other
+whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`),
+reversing this feature's own earlier deliberate plain-`YYYY-MM-DD`-date
+divergence. Changed: `feat/tools/create_feat.py` (frontmatter
+construction), `general/tools/update.py`'s `_update_feat` adapter,
+`general/tools/set_status.py`'s `_set_status_feat` adapter, plus four
+stale docstring/data-file mentions of the old format
+(`feat/models/v1/frontmatter.py`, `feat/models/v1/body.py`'s
+`UpdateEntry` docstring, `feat/prompts/create_feat.py`, and the packaged
+`feat_create_instructions.md`/`feat_update_instructions.md`). Two
+existing tests updated to assert the new format
+(`tests/feat/tools/test_create_feat.py`,
+`tests/feat/tools/test_integration.py`) — no new tests added, per this
+phase's own no-new-functionality scope. `docs/feat_schema.json` and the
+packaged `feat/data/feat_schema.json` copy regenerated (embed the
+changed `UpdateEntry` docstring); `specmgr docs`/`specmgr mcp-docs`
+re-run, touching only the expected `docs/api/*.md` files for the six
+changed `src` modules. Full quality gate green: `ruff format --check`
+(1286 files already formatted), `ruff check` (all checks passed),
+`vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest`
+suite (2228 tests, OK, unchanged from Phase 5 — no new tests added),
+`specmgr unused-code` (clean). Frontmatter `status` set back to `done`;
+`version` bumped from `1.12.0` to `1.13.0`.
+
 **As of 2026-08-30 (Phase 6 recorded, not started)**: A new `#### Phase
 6: Frontmatter timestamp format fix` has been added to the Task List
 (Task 6.1, not-started) to reverse this feature's own earlier deliberate
@@ -1054,6 +1101,99 @@ implementing agent's.
 
 ### Recent Updates
 
+#### Update 2026-08-30 (Phase 6 complete — frontmatter timestamp format fix implemented)
+
+- **Implemented Task 6.1**: `feat` frontmatter's `created`/`updated`
+  fields now use `datetime.now().isoformat(timespec="microseconds")`,
+  the same microsecond ISO timestamp format every other whole-body
+  domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`) already uses —
+  reversing this feature's own earlier, deliberate plain-`YYYY-MM-DD`
+  divergence.
+- **3 `src` files enumerated by the task**, each edited at both the code
+  and docstring level:
+  - `feat/tools/create_feat.py`: the local `today = datetime.now().date().isoformat()` variable became `now = datetime.now().isoformat(timespec="microseconds")`
+    (renamed to match `dec`/`gol`'s own `create_<d>.py` local-variable
+    naming, checked first per the task's own instruction), used for both
+    `created`/`updated` in the constructed `FeatFrontmatter`. Module
+    docstring's "Timestamp format is a deliberate `feat`-only divergence"
+    paragraph and the `create_feat()` docstring's "today's plain
+    `YYYY-MM-DD` date" line both rewritten to describe the now-matching
+    behavior.
+  - `general/tools/update.py`'s `_update_feat` adapter: both the
+    whole-body and line-range branches' `today = datetime.now().date().isoformat()` became `now = datetime.now().isoformat(timespec="microseconds")`,
+    mirroring `_update_dec`'s exact pattern/variable naming. Module
+    docstring and `_update_feat()`'s own docstring rewritten so `feat`'s
+    only remaining stated divergence is addressing resolution (the
+    bespoke `feat.tools._paths` folder-per-document shortcut), not
+    timestamp format.
+  - `general/tools/set_status.py`'s `_set_status_feat` adapter: same
+    `today` → `now`/microsecond-timestamp change, mirroring
+    `_set_status_dec`. Module docstring, `_set_status_feat()`'s own
+    docstring, and the public `set_status()` docstring's "a plain
+    `YYYY-MM-DD` date for `feat`, a microsecond timestamp for the other
+    eight" sentence all rewritten to state every domain now shares one
+    format.
+- **Design Notes' "Frontmatter" section** (`.specmgr/feat/feat-31-feature/README.md`,
+  this file) updated: the "`created`/`updated` stay plain `YYYY-MM-DD`
+  ... a deliberate divergence" sentence now states `created`/`updated`
+  use the same microsecond timestamp as every other domain, reversing
+  the earlier stated divergence, with a pointer to this update's own new
+  Decisions Made entry for the rationale — the historical context about
+  the 17 pre-existing hand-authored feature files (still out of scope,
+  unaffected by this change) is preserved, not deleted.
+- **New Decisions Made entry added** (see below), explicit that this is
+  a reversal of the earlier "`feat` frontmatter timestamps stay plain
+  `YYYY-MM-DD`" decision, made as a follow-up after the feature initially
+  shipped `done`, not part of the original five design-review rounds.
+- **Beyond the task's own enumerated files**, also found and corrected
+  four stale docstring/data-file mentions of the old plain-date behavior
+  via the task's own suggested final grep
+  (`grep -rn "date().isoformat\|YYYY-MM-DD" ...`), none of which were
+  explicitly named in Task 6.1 but would otherwise have been left
+  factually wrong: `feat/models/v1/frontmatter.py`'s module docstring
+  ("the specific `YYYY-MM-DD` convention `feat` uses" → "the specific
+  microsecond timestamp convention every domain, including `feat`,
+  uses"); `feat/models/v1/body.py`'s `UpdateEntry` class docstring,
+  which contrasts the body-level `### Updates`/`### Decisions Made`
+  entry-heading ISO8601 format against frontmatter's format (updated the
+  frontmatter-format description only — the body-level format itself is
+  unchanged and stays deliberately different, per Design Notes); the
+  `feat/prompts/create_feat.py` module docstring; and the packaged
+  `feat/data/feat_create_instructions.md`/`feat_update_instructions.md`
+  narrated-instruction text the `create_feat`/`update_feat` MCP prompts
+  read verbatim (these are user/LLM-facing text, not just internal
+  comments, so leaving them stale would have actively misled a caller
+  following the prompts).
+- **Regenerated `docs/feat_schema.json` and the packaged
+  `feat/data/feat_schema.json` copy** (`specmgr schema --type feat` both
+  ways, confirmed byte-identical via `diff`) since both embed the
+  changed `UpdateEntry` docstring text verbatim. Re-ran `specmgr docs`
+  (touched exactly the 6 expected `docs/api/*.md` files for the 6
+  changed `src` modules, nothing else) and `specmgr mcp-docs` (zero
+  further diff — no tool/resource/prompt registration text changed,
+  only docstrings already reflected by the Task 5.1-era MCP.md).
+- **2 existing tests updated, no new tests added** (per this phase's own
+  "format fix, no new functionality" scope):
+  `tests/feat/tools/test_create_feat.py`'s
+  `test_builds_frontmatter_and_returns_document` regex assertion changed
+  from `r"^\d{4}-\d{2}-\d{2}$"` to
+  `r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}$"`;
+  `tests/feat/tools/test_integration.py`'s two equivalent `updated`-field
+  regex assertions (whole-body `update` and `set_status` steps) updated
+  the same way, plus the explanatory comment above the `update` step
+  that referenced "a plain YYYY-MM-DD date, not the other domains'
+  microsecond timestamp".
+- Full quality gate green: `ruff format --check` (1286 files already
+  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest` suite (2228 tests,
+  OK — unchanged from Phase 5, since no new tests were added, only
+  existing assertions changed), `specmgr unused-code` (clean, no unused
+  code found).
+- Frontmatter `status` set back to `done` (this was the only remaining
+  not-done work); `version` bumped from `1.12.0` to `1.13.0`.
+- Per this phase's own task instructions (implementer runs the gate
+  only), **no commit was made** — that is the orchestrator's
+  responsibility for this run.
+
 #### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)
 
 - Added a new `#### Phase 6: Frontmatter timestamp format fix` to the
@@ -2028,6 +2168,25 @@ implementing agent's.
   deliberate scoping choice. `Acceptance Criterium (ACC)` stays commented
   out -- `AGENTS.md`'s "Still genuinely missing" section confirms no `ac`
   domain exists yet.
+- **2026-08-30 (Phase 6)**: **Reversed** the earlier "`feat` frontmatter
+  timestamps stay plain `YYYY-MM-DD`, matching the 17 hand-authored
+  files" decision (recorded in Design Notes' "Frontmatter" section and
+  implicit in the "Frontmatter `version` becomes schema-version-only"
+  entry's era, above). `feat`'s `created`/`updated` now use the same
+  microsecond ISO timestamp format
+  (`datetime.now().isoformat(timespec="microseconds")`) as every other
+  whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`), for
+  consistency across the codebase. This was a follow-up decision made
+  after the feature initially shipped `done` (Phase 5) -- not part of
+  the original five design-review rounds -- prompted by the divergence
+  proving more disruptive in practice than anticipated (every generic
+  cross-domain tool/adapter and every piece of `feat`-facing narration
+  had to carry an explicit "except `feat`, which uses a plain date"
+  caveat). The 17 pre-existing hand-authored feature files this
+  divergence originally matched remain untouched and out of scope (see
+  Scope) -- this reversal only affects documents created/updated via the
+  `feat` MCP tools (`create_feat`, the generic `update`/`set_status`
+  with `type="feat"`) going forward, not any file already on disk.
 
 ### Related PRs / Commits
 

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.1s)

This all looks thorough and well-documented. Now let's independently re-run the quality gate.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===CHECK===\" && uv run --frozen ruff check 2>&1 | tail -10"
}
```

**Output:**

```
1286 files already formatted
===CHECK===
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.7s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -20"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 92.8s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | tail -15"
}
```

**Output:**

```
'
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content', '']
['### Sec3 only', '', 'content', 'more content']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '', '#### Nested', '', 'more']
['### Sec3', '', 'content', '', '##### Nested', '', 'more']
['### Sec3', '', 'content', '', '###### Nested', '', 'more']
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content']
[]
['### Sec3', '', 'content', '']


[0] # Title

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 82.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(OK|FAILED|Ran |ERROR|FAIL:)\" | tail -20"
}
```

**Output:**

```
Ran 2228 tests in 78.095s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

2228 tests, OK — matches the report.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen specmgr unused-code 2>&1 | tail -10"
}
```

**Output:**

```
No unused code found in /home/user/src/biz.dfch.SpecMgr/src.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.0s)

All quality gate checks confirmed independently: ruff format/check clean, vulture clean, full unittest suite green (2228 tests, OK), unused-code clean. Let's also confirm docs regeneration is idempotent (no drift) since the agent touched docs/api files.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen specmgr docs >/tmp/opencode/docs_run.log 2>&1; tail -20 /tmp/opencode/docs_run.log; echo \"---git status after---\"; git status --short docs/ | head -20"
}
```

**Output:**

```
✓ Wrote 363 module file(s) to /home/user/src/biz.dfch.SpecMgr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/GENERATED.md
---git status after---
 M docs/api/biz.dfch.specmgr.feat.models.v1.body.md
 M docs/api/biz.dfch.specmgr.feat.models.v1.frontmatter.md
 M docs/api/biz.dfch.specmgr.feat.prompts.create_feat.md
 M docs/api/biz.dfch.specmgr.feat.tools.create_feat.md
 M docs/api/biz.dfch.specmgr.general.tools.set_status.md
 M docs/api/biz.dfch.specmgr.general.tools.update.md
 M docs/feat_schema.json

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.9s)

Confirmed idempotent — re-running `specmgr docs` produced exactly the same 6 already-changed files, no new drift. Everything checks out. Let's ask for confirmation before committing.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff --stat"
}
```

**Output:**

```
 .specmgr/feat/feat-31-feature/README.md            | 181 +++++++++++++++++++--
 docs/api/biz.dfch.specmgr.feat.models.v1.body.md   |   3 +-
 .../biz.dfch.specmgr.feat.models.v1.frontmatter.md |   6 +-
 .../biz.dfch.specmgr.feat.prompts.create_feat.md   |   6 +-
 .../api/biz.dfch.specmgr.feat.tools.create_feat.md |  19 +--
 .../biz.dfch.specmgr.general.tools.set_status.md   |  26 +--
 docs/api/biz.dfch.specmgr.general.tools.update.md  |  29 ++--
 docs/feat_schema.json                              |   2 +-
 .../specmgr/feat/data/feat_create_instructions.md  |   3 +-
 src/biz/dfch/specmgr/feat/data/feat_schema.json    |   2 +-
 .../specmgr/feat/data/feat_update_instructions.md  |   5 +-
 src/biz/dfch/specmgr/feat/models/v1/body.py        |   3 +-
 src/biz/dfch/specmgr/feat/models/v1/frontmatter.py |   6 +-
 src/biz/dfch/specmgr/feat/prompts/create_feat.py   |   6 +-
 src/biz/dfch/specmgr/feat/tools/create_feat.py     |  25 ++-
 src/biz/dfch/specmgr/general/tools/set_status.py   |  30 ++--
 src/biz/dfch/specmgr/general/tools/update.py       |  37 ++---
 tests/feat/tools/test_create_feat.py               |   2 +-
 tests/feat/tools/test_integration.py               |   8 +-
 19 files changed, 277 insertions(+), 122 deletions(-)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 11.7s)

## Phase 6 verification complete

I independently verified `phase-implementer`'s work for Phase 6 ("Frontmatter timestamp format fix", Task 6.1):

**What changed** (19 files, all in scope):

- Behavior: `feat/tools/create_feat.py`, `general/tools/update.py` (`_update_feat`), `general/tools/set_status.py` (`_set_status_feat`) — all now use `datetime.now().isoformat(timespec="microseconds")` instead of `datetime.now().date().isoformat()` for `created`/`updated`, matching every other whole-body domain.
- Docstrings corrected in those 3 files plus 4 more places the agent found via a grep sweep that were left stale otherwise (`feat/models/v1/frontmatter.py`, `feat/models/v1/body.py`'s `UpdateEntry`, `feat/prompts/create_feat.py`, and the two packaged `feat_*_instructions.md` files read by the MCP prompts).
- `docs/feat_schema.json` + packaged copy + `docs/api/*.md` regenerated (they embed the changed docstring text) — confirmed idempotent by re-running `specmgr docs` myself.
- Only 2 existing test files updated (`test_create_feat.py`, `test_integration.py`) — regex assertions widened from date-only to the full microsecond ISO format. **No new tests were added**, consistent with your instruction.
- `.specmgr/feat/feat-31-feature/README.md`: Task 6.1 marked done, Design Notes' "Frontmatter" section corrected, a new dated Decisions Made entry explicitly documents the reversal and rationale, Current Status/Recent Updates updated, frontmatter `status` moved back to `done`, `version` bumped to `1.13.0`.

**Independently re-ran the full quality gate myself:**

- `ruff format --check` → 1286 files already formatted
- `ruff check` → All checks passed
- `vulture src/ whitelist.py --min-confidence 60` → clean
- `python -m unittest discover ...` → **2228 tests, OK** (unchanged count, confirming no new tests were added)
- `specmgr unused-code` → no unused code found
- `specmgr docs` re-run → touches exactly the same 6 already-diffed `docs/api/*.md` files, confirming idempotency

Everything matches the plan's Task 6.1 scope precisely, no other domain's code was touched, and no existing behavior beyond the timestamp format was altered.

This is the plan's only remaining phase. Ready to commit as one Conventional Commit for Phase 6 — may I proceed with:

```
fix(feat-31): use microsecond timestamps for feat frontmatter created/updated

Reverts the feature's own earlier deliberate divergence (plain
YYYY-MM-DD dates) in create_feat, the generic update/set_status feat
adapters, and their docstrings/packaged instructions, to match every
other whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec). Updates the
two existing tests asserting the old format; no new tests added.
Records the reversal in the feature plan's Decisions Made log.
```

Let me know if you'd like the wording changed, otherwise I'll stage and commit.

______________________________________________________________________
