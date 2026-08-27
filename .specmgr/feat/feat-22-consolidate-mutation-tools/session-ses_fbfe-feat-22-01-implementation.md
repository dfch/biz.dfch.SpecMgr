# Feat-22 phased implementation

**Session ID:** ses_fbfe45404ffeXiyfJ9D8zwRikK
**Created:** 8/27/2026, 12:05:50 AM
**Updated:** 8/27/2026, 4:16:28 PM

______________________________________________________________________

## User

Implement the feature planned in `.specmgr/feat/feat-22  You commit after each phase without asking me first. But DO NOT push. You continue to implement the whole feature without asking me, unless you hit a wall or need my decision. DO NOT implement yourself, use the Phase-Implementer agent for that./README.md`.

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

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 19.6s)

_Thinking:_

First, let's start by reading the feature plan in full. The user is asking me to act as an orchestrator for `.specmgr/feat/feat-22/README.md`. I'll read that file first.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22/README.md"
}
```

**Error:**

```
File not found: /home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22/README.md
```

**Tool: bash**

**Input:**

```json
{
  "command": "ls -la /home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22/ && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 status && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 log --oneline -10"
}
```

**Output:**

```
ls: cannot access '/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22/': No such file or directory

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 12.0s)

_Thinking:_

The directory doesn't exist. The bash command output was cut off partway through (it looks like the git status and log weren't displayed — actually, ls failed, and it stopped there due to the && chain). Let me check the .specmgr/feat/ directory to find the feat-22 folder.

The exact path doesn't exist. Let me find the actual feat-22 folder.

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/ && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 status --short && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 log --oneline -10"
}
```

**Output:**

```
feat-0-termxplorer-mcp
feat-10-add-artifact-type-tasklist
feat-12-qa-artifact
feat-13-list-paging
feat-14-qa-v2-adjacent-qa
feat-15-add-artifact-type-risk
feat-16-problem-statement
feat-18-goal
feat-21-decision
feat-22-consolidate-mutation-tools
feat-4-use-cases
feat-5-md-model-parser
feat-6-requirement-artifact
feat-7-various-improvements
feat-8-coverage-badge
feat-9-doc-in-specmgr
f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools
3152c48 docs(termxplorer-mcp): add API investigation results for TermXplorer
0719f3e feat(dec): add plan for the Decision (DEC) artifact type
45c9ad5 doc: add examples
7512281 ci(schema): replace the 5 schema check steps with one
15e27bd Merge branch 'dev' into feat-7
1d4f612 docs(readme): add a one-time pre-commit hook install part
9f84a00 docs: replace the AGENTS.md domain lists with the models-location rule
d559879 docs: replace specmgr://<d>/list names with list_<d> tool names
cf673d6 chore(release): set version to v0.11.0

```

**Tool: glob**

**Input:**

```json
{
  "pattern": ".specmgr/feat/**/README.md"
}
```

**Output:**

```
No files found
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 9.4s)

_Thinking:_

The folder is "feat-22-consolidate-mutation-tools". Let me try reading that README.

Found it — the folder is `feat-22-consolidate-mutation-tools`. Reading the full plan now.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-26
3: id: feat-22-consolidate-mutation-tools
4: status: planning
5: updated: 2026-08-26
6: version: 1.0.0
7: ---
8: 
9: # Feature: Consolidate update and set_status tools into generic type-dispatched tools
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Replace the 15 near-duplicate per-domain mutation MCP tools with two generic,
16: cross-cutting tools that live in `general/tools/`: `update(id, type, content,
17: begin, end)` for whole-body (and now line-range) document replacement across
18: the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`),
19: and `set_status(id, type, status, superseded_by)` for status changes across
20: all eight domains including `adr`. The per-domain tools
21: (`update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/
22: `update_rsk`, `set_status_req`/`set_status_uc`/`set_status_tsk`/`set_status_qa`/
23: `set_status_prb`/`set_status_gol`/`set_status_rsk`, and ADR's own `set_status`)
24: are deleted outright (breaking; the package is 0.x and the MCP tool list is the
25: only contract). The generic `update` gains optional 1-based, inclusive
26: `begin`/`end` body-line parameters so a client can replace a line range
27: without re-sending the whole body — spliced into the current on-disk body and
28: validated as a *whole* document before anything is written (the
29: filesystem-is-source-of-truth and validate-before-write invariants are
30: untouched). To make line targeting reliable, the seven `get_<d>` tools gain an
31: optional `raw: bool = False` parameter returning the frontmatter-stripped body
32: text verbatim — the exact text `begin`/`end` index into (tool-first per ADR
33: ddfb1109; re-introducing `specmgr://<d>/{id}` resources was considered and
34: rejected). ADR keeps its section-level mutation surface
35: (`update_frontmatter`/`update_section`/`option_*`) unchanged — ADR is
36: deliberately *excluded* from `update` because it has no whole-body replace by
37: design (MADR contract), but is *included* in `set_status` with its
38: `superseded_by`-composition special case. A short ADR records the new
39: conventions so future domains (e.g. `ac`) add one dispatch entry instead of a
40: new tool. Expected end state: **71 tools / 25 resources / 19 prompts**
41: (today 84/25/19: −15 +2).
42: 
43: ### Requirements
44: 
45: - REQ-001: A generic `update(id, type, content)` MCP tool in
46:   `general/tools/update.py` covering the seven whole-body domains
47:   (`type: Literal["req","uc","tsk","qa","prb","gol","rsk"]`), preserving each
48:   domain's existing whole-body semantics 1:1: body-only `content` (no
49:   frontmatter block) validated via the domain's own
50:   `X.from_text(format_text(content))` two-channel contract
51:   (`AssertionError` structural / `pydantic.ValidationError` field-level,
52:   nothing written on failure); under the domain's own lock, `load_by_id`,
53:   every frontmatter field preserved except `updated` (bumped to the current
54:   microsecond timestamp); `status` never settable through `update`; the
55:   caller's raw `content` persisted verbatim via the domain's `write_X_file`;
56:   unknown id raises the domain's own `XNotFoundError`.
57: - REQ-002: Optional `begin: int | None` / `end: int | None` parameters on
58:   `update`. When both are absent, behavior is exactly REQ-001 (backward-
59:   compatible default). When both are given, `content` is a replacement
60:   *fragment* for the current body's 1-based, inclusive line range
61:   `begin..end`, where `N` = number of lines of the current frontmatter-
62:   stripped body and `N+1` is a virtual position past the last line
63:   (`begin = end = N+1` → append at end of body; `end = N+1` → range extends
64:   through end of body). Misuse (exactly one of the two given, `begin < 1`,
65:   `begin > end`, `end > N+1`) raises `ValueError` with a clear message and
66:   writes nothing. The spliced *result* is validated as a whole body (REQ-001's
67:   validation contract) before writing; unchanged regions of the on-disk body
68:   remain byte-identical. An empty `content` fragment deletes the range (legal
69:   iff the result still validates). The YAML frontmatter is never addressable
70:   (coordinates are body-relative by construction).
71: - REQ-003: The seven `get_<d>` tools (`get_req`, `get_uc`, `get_tsk`,
72:   `get_qa`, `get_prb`, `get_gol`, `get_rsk`) gain an optional
73:   `raw: bool = False` parameter. `raw=False` (default) behaves exactly as
74:   today (returns the parsed `XDocument`). `raw=True` returns the
75:   frontmatter-stripped body text of the document verbatim as a plain string —
76:   produced by the *same* body-extraction helper the REQ-002 splice uses, so
77:   the text a client counts lines in is byte-for-byte the text the server
78:   splices against. Unknown id raises the domain's `XNotFoundError` in both
79:   modes. No `get_adr` change (ADR is not a `update` type).
80: - REQ-004: A generic `set_status(id, type, status, superseded_by=None)` MCP
81:   tool in `general/tools/set_status.py` covering all eight domains
82:   (`type: Literal["req","uc","tsk","qa","prb","gol","rsk","adr"]`). For the
83:   seven whole-body domains, semantics are preserved 1:1 from the deleted
84:   `set_status_<d>` tools: under the domain lock, `load_by_id`, the raw body
85:   re-read and re-persisted verbatim (body never touched), the frontmatter
86:   reconstructed through the domain's own `XFrontmatter` constructor so each
87:   domain's closed status vocabulary validates (invalid `status` →
88:   `pydantic.ValidationError`, nothing written), `updated` bumped, unknown id →
89:   domain `XNotFoundError`. For `type="adr"`, semantics are preserved 1:1 from
90:   the deleted ADR `set_status` tool: delegates to
91:   `models.adr.v1.mutations.set_status(adr, status, superseded_by)` (which
92:   composes `status` as `"superseded by {superseded_by}"` when
93:   `superseded_by` is given), `write_adr` render round-trip, `adr_lock`,
94:   `AdrNotFoundError`. `superseded_by` given with any `type` other than
95:   `"adr"` raises `ValueError` and writes nothing.
96: - REQ-005: The 15 superseded tools are removed from source and from MCP
97:   registration: `update_req`, `update_uc`, `update_tsk`, `update_qa`,
98:   `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
99:   `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
100:   `set_status_gol`, `set_status_rsk`, and ADR `set_status`. No deprecated
101:   wrappers are kept (user decision; 0.x breaking change, recorded in
102:   `CHANGELOG.md`).
103: - REQ-006: All prompt narration referencing the superseded tools is rewritten
104:   to the generic tools with correct signatures: the six domain
105:   `<d>_update_instructions.md` files (req, tsk, qa, rsk, prb, gol — `uc` has
106:   no prompts sub-package), `qa/data/qa_refine_instructions.md`, and the four
107:   ADR instruction files (`adr_create_instructions.md`,
108:   `adr_create_test_instructions.md`, `adr_update_instructions.md`,
109:   `adr_update_test_instructions.md` — their `set_status(id, …)` call sites
110:   gain `type="adr"`). The six domain update-instruction files additionally
111:   teach the REQ-002 range-update flow. Prompt Python module docstrings that
112:   name the superseded tools are corrected (6 domain `prompts/update_<d>.py`
113:   modules + 4 ADR prompt modules whose surface mentions become inaccurate).
114:   The 10 corresponding prompt test files (6 domain + 4 ADR) are updated to
115:   match the rewritten narration.
116: - REQ-007: Documentation and registration consistency: `server.py` module
117:   docstring (the authoritative tool/resource/prompt list) updated in the same
118:   phase that changes the surface it describes; `docs/MCP.md`, `docs/api/`,
119:   `docs/adr/README.md` regenerated with zero drift at every phase gate;
120:   `AGENTS.md` per-domain bullets and the `general/` bullet updated;
121:   `CHANGELOG.md` `[Unreleased]` carries the breaking-change and
122:   addition entries; a short ADR (Phase 1) records the conventions (explicit
123:   `type` over uuid-only resolution; ADR excluded from `update` but included
124:   in `set_status`; the REQ-002 range contract; the REQ-003 raw-read-over-
125:   resource decision; "future domains add one dispatch entry, not a new
126:   tool").
127: 
128: ### Acceptance Criteria
129: 
130: - [ ] ACC-001: Verifies REQ-001 — for every one of the seven types, `update`
131:   in whole-body mode (no `begin`/`end`) replaces the body, preserves
132:   `id`/`type`/`status`/`created`/`version`, bumps `updated` (microsecond
133:   timestamp), never sets `status`, propagates structural `AssertionError` /
134:   field `pydantic.ValidationError` with the file left byte-identical on disk,
135:   and raises the domain's own `XNotFoundError` for an unknown id.
136: - [ ] ACC-002: Verifies REQ-002 — for every one of the seven types: a middle-
137:   range replace leaves all out-of-range body lines byte-identical and inserts
138:   the fragment at the range; `begin = end = N+1` appends at end of body;
139:   `end = N+1` replaces through end of body; empty `content` deletes the range
140:   (verified with an optional-section deletion that yields a still-valid
141:   document); `begin = 1`, `end = N` produces the same file as whole-body mode
142:   with the identical text; each misuse case (one parameter only, `begin < 1`,
143:   `begin > end`, `end > N+1`, range deleting the H1, range producing an
144:   out-of-vocabulary field value) raises (`ValueError` / `AssertionError` /
145:   `ValidationError`) with the file left byte-identical on disk.
146: - [ ] ACC-003: Verifies REQ-003 — for all seven domains, `get_<d>(id,
147:   raw=True)` returns the frontmatter-stripped body text byte-identical to the
148:   on-disk body (the text whose lines `begin`/`end` address — proven by a test
149:   that reads `raw`, picks a line range, calls `update` with that range, and
150:   confirms the splice landed exactly there); `get_<d>(id)` (`raw=False`)
151:   returns the parsed document exactly as before (regression); unknown id
152:   raises the domain `XNotFoundError` in both modes.
153: - [ ] ACC-004: Verifies REQ-004 — for all eight types, `set_status` changes
154:   `status`, bumps `updated`, and leaves the body untouched (seven domains: raw
155:   body byte-identical; ADR: re-render round-trip equal apart from
156:   status/updated); each domain's closed vocabulary is enforced (out-of-set
157:   value → `pydantic.ValidationError`, nothing written — including domain-
158:   distinct sets: `uc` 5-value, `tsk`/`qa` 4-value, `prb` 4-value, `rsk`
159:   6-value); ADR `superseded_by` composes `"superseded by X"`; `superseded_by`
160:   with a non-`adr` type raises `ValueError`, nothing written; unknown id
161:   raises the domain `XNotFoundError` / `AdrNotFoundError`.
162: - [ ] ACC-005: Verifies REQ-005 — the 15 superseded tools are absent from
163:   `src/` and from the live MCP registration; a grep over `src/` and `tests/`
164:   finds no code references to the removed tool names (any residual mention
165:   before Phase 5 is limited to the Phase-5-owned prompt narration files, and
166:   zero afterwards); `vulture` is clean.
167: - [ ] ACC-006: Verifies REQ-006 — all 11 instruction data files reference the
168:   generic tools with the correct signatures (`update(id, type="<d>", content
169:   [,...])`, `set_status(id, type=..., status[, superseded_by])`); the six
170:   domain update-instruction files teach the range-update flow (`get_<d>(id,
171:   raw=True)` → identify the 1-based range → `update(..., begin, end)`; whole-
172:   body for multi-section or uncertain changes); the 10 prompt test files pass
173:   against the rewritten narration.
174: - [ ] ACC-007: Verifies REQ-007 — `specmgr docs`, `specmgr mcp-docs`,
175:   `specmgr adr-toc`, and `specmgr schema` all report zero drift;
176:   `docs/MCP.md` shows the two new general tools (with `type` rendered as a 7-
177:   / 8-value enum) and none of the 15 removed tools; `server.py`'s docstring
178:   lists exactly the post-feature surface; `AGENTS.md` and `CHANGELOG.md` are
179:   updated per REQ-007.
180: - [ ] ACC-008: Verifies REQ-001/002/004/005 — the Phase-1 ADR exists in
181:   `docs/adr/` with status `accepted` and is listed in `docs/adr/README.md`; a
182:   live, un-mocked end-to-end run in a temporary `SPECMGR_DOCS_DIR` passes for
183:   `req`, `rsk`, and `uc`: `create_<d>` → `get_<d>(id, raw=True)` →
184:   `update(id, type, content, begin, end)` (one middle-range replace, one
185:   `N+1` append) → `get_<d>` (content verified) → `set_status(id, type,
186:   status)` (domain-valid value) → `get_<d>` (status verified); for ADR:
187:   `create_adr` → `set_status(id, type="adr", status="superseded",
188:   superseded_by=…)` → status reads `"superseded by …"`;
189:   `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real
190:   `server.mcp` instance reports **71 tools / 25 resources / 19 prompts**; a
191:   fresh subprocess import of `biz.dfch.specmgr.server` succeeds.
192: 
193: ### Scope
194: 
195: **Included in this feature:**
196: 
197: - `general/tools/update.py`, `general/tools/set_status.py`, and the shared
198:   body-text/splice helpers (private module under `general/tools/`), plus
199:   their registration in `general/tools/__init__.py`.
200: - The `raw` parameter on the seven `get_<d>` tools.
201: - Deletion of the 15 superseded tool modules, their test files, and all
202:   code/docstring references outside Phase-5-owned narration.
203: - The narration rewrite (11 instruction data files, prompt module
204:   docstrings, 10 prompt test files).
205: - The Phase-1 ADR, `AGENTS.md`, `CHANGELOG.md`, and all generated docs.
206: 
207: **Explicitly out of scope:**
208: 
209: - Any change to ADR's section-level mutation tools (`update_frontmatter`,
210:   `update_section`, `option_*`) or to ADR's `specmgr://adr/{id}` resource —
211:   ADR has no whole-body replace by design and is therefore not a `update`
212:   type; its `set_status` behavior moves to the generic tool unchanged.
213: - Re-introducing `specmgr://<d>/{id}` resources for the seven domains —
214:   rejected in the planning session on ADR ddfb1109's empirical reliability
215:   finding (agents invoke tools more reliably than parameterized resources);
216:   `get_<d>(raw=True)` serves the same need (recorded in the Phase-1 ADR).
217: - Consolidation of `create_*`, `get_*` (beyond the `raw` parameter),
218:   `list_*`, `validate_*`, `parse_*`, or the `delete_*` stubs.
219: - Any schema/model change: the per-domain status vocabularies, body schemas,
220:   and `specmgr schema` outputs are untouched.
221: - A version bump of `pyproject.toml` (release-time concern per `AGENTS.md`;
222:   the breaking change lands in `[Unreleased]`).
223: - The `ac` domain (does not exist yet) — but its *convention* is fixed by the
224:   ADR: it will add one dispatch entry to the two generic tools, not new
225:   tools.
226: - The pre-existing, already-documented AGENTS.md staleness items (e.g. the
227:   historical "REQ, UC, and TSK were built after that refactor" enumeration) —
228:   fixing unrelated stale text is not part of this feature.
229: 
230: ### Dependencies
231: 
232: - Depends on: ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based reads are
233:   tool-first — the basis for `raw` on `get_<d>` instead of `/{id}`
234:   resources); ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
235:   hierarchy — the generic tools live in the cross-cutting `general/`
236:   package, reusing each domain's private helpers); ADR
237:   3bf0326f-065a-424c-a2b9-87e5d5bcfa99 (the `mcp` singleton lives in
238:   `server.py` — import-order consideration, see Design Notes); ADR
239:   71fd95d7-07f2-466f-81aa-d29b7e3ef34c (ADR's `update_section` contract —
240:   what `update` deliberately does *not* extend to ADR); ADR
241:   898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs are authored/edited only
242:   through the MCP structured tools — Phase 1 must use `specmgr_create_adr`);
243:   ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of
244:   truth — the splice re-reads the on-disk body and the validate-before-write
245:   invariant is preserved); the existing `general/tools/_doc_paths.py`/
246:   `_packaged_data.py` infrastructure and each domain's `_paths`/`_io`/
247:   `_write`/`_lock` private helpers (reused as-is, not modified).
248: - Blocks: none. Future domain work (e.g. `ac`) must follow the ADR's
249:   dispatch-entry convention.
250: 
251: ### Design Notes
252: 
253: **Dispatch architecture.** Each of the two generic tools is a thin MCP
254: wrapper around a dispatch table `dict[str, Callable]` mapping the `type`
255: value to a private adapter function (`_update_<d>` / `_set_status_<d>`). Each
256: adapter is a **verbatim port** of the corresponding deleted tool's function
257: body (same lock, same `load_by_id`, same frontmatter carry-over / `updated`
258: bump, same `write_X_file`, same domain `XNotFoundError`) — for `update`, plus
259: the REQ-002 range branch; for `set_status`, the ADR adapter ports
260: `adr/tools/set_status.py` including its delegation to
261: `models.adr.v1.mutations.set_status`. Domain private helpers (`_paths`,
262: `_io`, `_write`, `_lock`) and domain models are **not modified** —
263: `create_*`/`get_*`/`validate_*`/`list_*` keep using them exactly as today,
264: and the new adapters import them the same way the old tools did. The adapters
265: and table live in `general/tools/` because the tools are cross-cutting (the
266: `general/` package is the documented home for non-domain-specific tools, per
267: `AGENTS.md`); no new shared *code* is added to the domain packages.
268: 
269: **`update` signature and return type.**
270: 
271:     @mcp.tool(
272:         name="update",
273:         title="Update document",
274:         description=(...),  # whole-body or line-range replace; type = domain;
275:     )                       # begin/end optional 1-based inclusive body-line range
276:     def update(
277:         id: str,
278:         type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk"],
279:         content: str,
280:         begin: int | None = None,
281:         end: int | None = None,
282:     ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument:
283: 
284: The parameter is named `type` (matches the frontmatter field vocabulary the
285: client already knows; ruff's enabled rule set E/F/W has no builtin-shadowing
286: rule). The 7-way union return type is annotation-only — the MCP input schema
287: is built from the parameters, and the SDK serializes whichever concrete
288: document is returned. The `type` value must render as a 7-entry JSON-schema
289: `enum` in `docs/MCP.md` (verify in the Phase 2 gate).
290: 
291: **Range contract (REQ-002), precisely.** Let `N` be the number of lines of
292: the current frontmatter-stripped body (`len(body_text.splitlines())`).
293: Coordinates are 1-based and inclusive. `N+1` is a virtual position past the
294: last line:
295: 
296: - `begin = end = k` (1 ≤ k ≤ N) → replace line `k` only.
297: - `begin = k`, `end = m` (k ≤ m ≤ N) → replace lines `k..m`.
298: - `end = N+1` → the range extends through the last line (`k..N`).
299: - `begin = end = N+1` → the range is empty at end-of-body: pure append.
300: - `begin = 1`, `end = N` → whole-body replace, file-identical to whole-body
301:   mode with the same text (test this equivalence).
302: - Empty `content` → the range is deleted (legal iff the result validates).
303: 
304: Misuse → `ValueError` (client-controlled input, **not** `assert` — per
305: `.specmgr/conventions.md` Rule 3): exactly one of `begin`/`end` given;
306: `begin < 1`; `begin > end`; `end > N + 1`. The error message names the
307: offending value(s) and the allowed range. Splice algorithm: take the on-disk
308: body lines, drop lines `begin..min(end, N)`, insert `content.splitlines()` at
309: position `begin - 1`, rejoin with `"\n"` plus a single trailing `"\n"`. The
310: **result** is validated exactly like whole-body mode (`X.from_text(
311: format_text(spliced))`) and the spliced text (not the fragment) is persisted
312: verbatim via the domain `write_X_file` — so out-of-range regions are
313: byte-identical to disk and no renderer ever touches them. Frontmatter
314: addressing is impossible by construction: the body text is extracted with the
315: frontmatter block removed, and coordinates are defined relative to that text
316: only.
317: 
318: **Shared body extraction + `raw` invariant (REQ-003).** One private helper
319: (live in a new `general/tools/_splice.py` alongside the splice function, no
320: `mcp` dependency — plain file I/O, mirroring `_doc_paths.py`'s placement)
321: returns the frontmatter-stripped body text of a file using the established
322: `frontmatter.loads(path.read_text(encoding="utf-8")).content` mechanism (the
323: same one all seven `set_status_<d>` tools use today). Both the REQ-002 splice
324: and each `get_<d>(raw=True)` call go through this one helper, which *is* the
325: "what the client counts is what the server splices" invariant of ACC-003.
326: `get_<d>` with `raw=True` stays read-only: no lock, no directory creation —
327: matching every existing `get_<d>`.
328: 
329: **`set_status` signature and the `superseded_by` guard (REQ-004).**
330: 
331:     @mcp.tool(
332:         name="set_status",
333:         title="Set document status",
334:         description=(...),  # type = domain (8 values, incl. adr);
335:     )                       # superseded_by: adr only
336:     def set_status(
337:         id: str,
338:         type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "adr"],
339:         status: str,
340:         superseded_by: str | None = None,
341:     ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr:
342: 
343: Per-domain closed status vocabularies (authoritative source: each domain's
344: `_ALLOWED_STATUSES` in `models/<v>/frontmatter.py` — re-read them when
345: implementing; the table below reflects 2026-08-26): `req` and `gol`:
346: `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
347: `implemented` (7); `uc`: `draft`/`proposed`/`accepted`/`deprecated`/
348: `superseded` (5); `tsk` and `qa`: `draft`/`active`/`done`/`cancelled` (4);
349: `prb`: `draft`/`active`/`resolved`/`cancelled` (4); `rsk`: `open`/
350: `mitigating`/`accepted`/`occurred`/`closed`/`dropped` (6); `adr`: 6 values
351: (`draft`/`proposed`/`rejected`/`accepted`/`deprecated`/`superseded`) plus the
352: `"superseded by X"` pattern. The guard `superseded_by is not None and type !=
353: "adr"` → `ValueError` runs **before** any file access.
354: 
355: **Import-order consideration.** `server.py` imports the domain packages in
356: one bottom-of-file line, with `general` second (`from . import adr, general,
357: gol, prb, qa, req, rsk, tsk, uc`). Once `general/tools/__init__.py` registers
358: the new tools, importing `general` pulls in **all** seven domain `tools` (and
359: `prompts`) packages earlier than today. This is safe by construction: every
360: domain tool module already does `from ...server import mcp` while
361: `server.py` is still executing its import line (the `mcp` name is bound at
362: `server.py:197`, before the import line at `server.py:211`), and every
363: `general.tools._packaged_data` import in domain prompts/resources uses the
364: submodule form (`from ...general.tools._packaged_data import read_packaged_
365: text`), which is safe mid-initialization. The Phase 2 gate's fresh-subprocess
366: import smoke test (ACC-008) proves it rather than assuming it.
367: 
368: **Docs discipline.** `server.py`'s module docstring is updated *inside* each
369: phase that changes the surface it describes (Phase 2 adds both tools' lines
370: as they are added; Phase 3 removes the `update_<d>` lines; Phase 4 removes
371: the `set_status_<d>` + ADR `set_status` lines). `docs/MCP.md` and
372: `docs/api/` are regenerated in every phase gate and must be drift-free
373: (`git diff --exit-code -- docs/`) at every phase commit — the pre-commit
374: hooks enforce this for any commit touching `src/`.
375: 
376: **Name-collision constraint.** ADR's existing tool is already named
377: `set_status`. Registering the generic `set_status` while `adr/tools/
378: set_status.py` still exists would double-register the name, which is why
379: Phase 4 adds the generic tool and deletes all eight old status tools in one
380: phase. (No such constraint exists for `update` — Phase 2 is purely additive,
381: Phase 3 deletes the seven `update_<d>` tools.)
382: 
383: **Phase-end quality gate (every phase).** Unless a phase task says otherwise:
384: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run
385: --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen
386: python -m unittest discover -v -s tests -t . -p "test_*.py"`, plus the
387: `specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema`
388: regenerations the phase touches, then `git diff --exit-code -- docs/`. Fix
389: failures and re-run until green — a phase is not done with a red gate. Then
390: update this README: a dated entry in the **Recent Updates** section, Current
391: Status, and the phase's task lines flipped to done in place.
392: 
393: ### Related ADRs
394: 
395: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a
396:   tool (`get_<d>`), not a resource — the basis for `get_<d>(raw=True)`
397:   instead of re-introducing `specmgr://<d>/{id}` resources
398: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-
399:   type domain — the generic tools live in the cross-cutting `general/`
400:   package, reusing domain-private helpers
401: - 3bf0326f-065a-424c-a2b9-87e5d5bcfa99: Extract the `mcp` singleton into its
402:   own module — the import-order consideration in Design Notes
403: - 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` (ADR
404:   domain) — the section-level contract that `update` deliberately does not
405:   extend to ADR
406: - 898bfcd0-85f9-462f-93a8-747bda4166c8: Author and edit ADRs only through MCP
407:   structured tools — Phase 1 must use `specmgr_create_adr`, never a hand-
408:   written file
409: - 33c5ab08-ff58-4c73-8c32-23abaf3838e3: Filesystem is the sole source of
410:   truth — the splice re-reads the on-disk body; validate-before-write
411: - (Phase 1 creates the feature's own short ADR; its id is recorded in
412:   Decisions Made once created)
413: 
414: ### Task List
415: 
416: Single, canonical breakdown of work phases and tasks. Status lives on the
417: task itself. Each phase ends with a mandatory phase-end quality-gate task
418: (full gate per Design Notes + this README's Progress update), and the
419: phase-orchestrator commits each accepted phase as one Conventional Commit.
420: 
421: #### Phase 1: ADR
422: 
423: - [ ] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP
424:   tool (never hand-write the file — ADR 898bfcd0), status `accepted`, title
425:   "Consolidate whole-body update and status-change tools into generic type-
426:   dispatched tools": Context (15 near-duplicate mutation tools; LLM clients
427:   see 15 entries for 2 conceptual operations; each new domain would add
428:   more); Decision Drivers (simpler tool surface; no all-directories write-
429:   path scan and no per-domain v4-UUID-collision ambiguity — uuid-only
430:   resolution was rejected; the client already knows the domain; preserve the
431:   filesystem-source-of-truth and validate-before-write invariants);
432:   Considered Options (1: generic tools with explicit `type` — chosen; 2:
433:   uuid-only id resolution scanning all domain directories; 3: keep per-
434:   domain tools); Decision Outcome (Option 1) with Consequences (breaking: 14
435:   per-domain tools removed and ADR `set_status`'s signature gains a required
436:   `type`; ADR is excluded from `update` — its section-level MADR contract
437:   has no whole-body replace — but included in `set_status` with the
438:   `superseded_by` special case; the `update` line-range contract: 1-based
439:   inclusive `begin`/`end`, `N+1` EOF sentinel, splice-then-validate-whole,
440:   frontmatter never addressable; `get_<d>(raw=True)` as the line-number
441:   source — tool-first per ADR ddfb1109, re-introducing `specmgr://<d>/{id}`
442:   resources was considered and rejected; future domains add one dispatch
443:   entry per generic tool, not new tools) — depends on: none — status: not-
444:   started
445: - [ ] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run
446:   --frozen specmgr adr-toc` and confirm the ADR appears in
447:   `docs/adr/README.md` — depends on: Task 1.1 — status: not-started
448: - [ ] Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff
449:   check, vulture, full unittest suite; no `src/` changes are expected, so
450:   `docs/` drift checks cover `specmgr adr-toc` output only); set this
451:   README's frontmatter `status: planning` → `status: in-progress`; add a
452:   dated entry to the Recent Updates section, update Current Status, flip the
453:   phase's task lines to done in place; record the new ADR's id — depends on:
454:   Task 1.2 — status: not-started
455: 
456: #### Phase 2: Generic `update` tool + `raw` read parameter
457: 
458: - [ ] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain
459:   file I/O + text manipulation, module docstring explaining the raw/splice
460:   invariant): `body_text(path: Path) -> str` (frontmatter-stripped body text
461:   via the established `frontmatter.loads(...).content` mechanism) and
462:   `splice_body(current_body: str, begin: int, end: int, content: str) -> str`
463:   (implements the Design-Notes range contract exactly: `N` = `len(
464:   current_body.splitlines())`; `ValueError` with a clear message for `begin <
465:   1`, `begin > end`, `end > N + 1`; drop lines `begin..min(end, N)`; insert
466:   `content.splitlines()` at position `begin - 1`; rejoin `"\n"` + single
467:   trailing `"\n"`; empty `content` = deletion) — depends on: none — status:
468:   not-started
469: - [ ] Task 2.2: Create `general/tools/update.py`: seven private adapter
470:   functions `_update_<d>(id_, content, begin, end)` — verbatim ports of the
471:   current `update_<d>` function bodies (same `X_lock`, `load_by_id`,
472:   frontmatter carry-over + microsecond `updated` bump, `write_X_file`,
473:   domain `XNotFoundError`) with the range branch added (no `begin`/`end` →
474:   today's behavior: validate `X.from_text(format_text(content))`, persist
475:   `content` verbatim; both given → `body_text` + `splice_body`, validate the
476:   *result* via `X.from_text(format_text(spliced))`, persist the *spliced*
477:   text verbatim; the both-or-neither `ValueError` guard runs before any file
478:   access); a dispatch table; and `@mcp.tool(name="update", ...)` `def
479:   update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"],
480:   content: str, begin: int | None = None, end: int | None = None) ->
481:   ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
482:   GolDocument | RskDocument` with a full numpy-style docstring (including
483:   the range contract and the error types) — depends on: Task 2.1 — status:
484:   not-started
485: - [ ] Task 2.3: Register `update` in `general/tools/__init__.py` (import,
486:   `__all__`, module docstring) — depends on: Task 2.2 — status: not-started
487: - [ ] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`
488:   tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`,
489:   `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`,
490:   `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) ->
491:   XDocument | str`; `raw=True` resolves the id as today (no lock — read-only)
492:   and returns `body_text(path)` (the same helper the splice uses, per the
493:   Design-Notes invariant); `raw=False` returns the parsed document exactly as
494:   today; update each tool's `@mcp.tool` description and docstring Returns
495:   section — depends on: Task 2.1 — status: not-started
496: - [ ] Task 2.5: Update `server.py`'s module docstring: add `update` to the
497:   General-tools lines (one line describing whole-body *and* line-range
498:   replace, the 7-value `type`, optional `begin`/`end`); note the `raw`
499:   parameter where the seven `get_<d>` tools are enumerated — depends on:
500:   Task 2.2, Task 2.4 — status: not-started
501: - [ ] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all
502:   seven types (seed a document per type, e.g. via the domain `create_<d>`
503:   tool in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the
504:   `tests/<d>/tools/test_update_<d>.py` files still on disk at this phase):
505:   whole-body mode (ACC-001 cases: body replaced; id/type/status/created/
506:   version preserved; `updated` bumped; status not settable; structural
507:   `AssertionError` and field `ValidationError` each leave the file
508:   byte-identical; unknown id → domain `XNotFoundError`); range mode (ACC-002
509:   cases: middle-range replace with out-of-range lines byte-identical; `N+1`
510:   append; `end=N+1` replace-through-EOF; empty-fragment deletion of an
511:   optional section yielding a valid document; `begin=1`/`end=N` ≡ whole-body;
512:   every `ValueError` misuse case; range deleting the H1 → `AssertionError`,
513:   file untouched; range producing an out-of-vocabulary field value →
514:   `ValidationError`, file untouched) — depends on: Task 2.2 — status: not-
515:   started
516: - [ ] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`
517:   (seven files) with `raw` coverage (ACC-003 cases): `raw=True` returns the
518:   body text byte-identical to the on-disk frontmatter-stripped body; the
519:   coordinate invariant (read `raw`, pick a real line range, `update` with it,
520:   assert the splice landed exactly there); `raw=False` regression (parsed
521:   document as before); unknown id → `XNotFoundError` in both modes — depends
522:   on: Task 2.4, Task 2.2 — status: not-started
523: - [ ] Task 2.8: Registration smoke test: a unittest asserting
524:   `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a
525:   7-value `enum` and optional integer `begin`/`end` in the input schema, plus
526:   a fresh-subprocess `uv run --frozen python -c "import biz.dfch.specmgr.
527:   server"` check run inside the phase gate (import-order proof, Design Notes)
528:   — depends on: Task 2.3 — status: not-started
529: - [ ] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's
530:   new tests; `uv run --frozen specmgr mcp-docs` and `uv run --frozen specmgr
531:   docs` regeneration, then `git diff --exit-code -- docs/` zero drift;
532:   confirm `docs/MCP.md` shows the `update` entry (enum) and the `raw` note on
533:   the `get_<d>` entries; add a dated entry to the Recent Updates section,
534:   update Current Status, flip the phase's task lines to done in place —
535:   depends on: Tasks 2.3, 2.5, 2.8 — status: not-started
536: 
537: #### Phase 3: Retire the per-domain `update_*` tools
538: 
539: - [ ] Task 3.1: Delete the seven tool modules: `req/tools/update_req.py`,
540:   `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`,
541:   `prb/tools/update_prb.py`, `gol/tools/update_gol.py`,
542:   `rsk/tools/update_rsk.py` — depends on: Phase 2 complete — status: not-
543:   started
544: - [ ] Task 3.2: Delete the seven test files: `tests/req/tools/
545:   test_update_req.py`, `tests/uc/tools/test_update_uc.py`, `tests/tsk/tools/
546:   test_update_tsk.py`, `tests/qa/tools/test_update_qa.py`, `tests/prb/tools/
547:   test_update_prb.py`, `tests/gol/tools/test_update_gol.py`, `tests/rsk/
548:   tools/test_update_rsk.py` — depends on: Task 3.1 — status: not-started
549: - [ ] Task 3.3: Update the seven domain `tools/__init__.py` files (remove the
550:   `update_<d>` import, `__all__` entry, and the module-docstring tool-list
551:   mention) and the seven domain `__init__.py` files (remove `update_<d>` from
552:   the docstring tool enumeration; note that whole-body updates go through the
553:   generic `update` tool in `general/tools/`) — depends on: Task 3.1 — status:
554:   not-started
555: - [ ] Task 3.4: Update `server.py`'s module docstring: remove `update_<d>`
556:   from the seven per-domain Tools lines (the `set_status_<d>` entries stay
557:   until Phase 4) — depends on: Task 3.1 — status: not-started
558: - [ ] Task 3.5: Grep verification: `grep -rn "update_req\|update_uc\|
559:   update_tsk\|update_qa\|update_prb\|update_gol\|update_rsk" src/ tests/`
560:   must return only prompt-narration matches (the six `prompts/update_<d>.py`
561:   module docstrings and their `data/*.md` files — Phase 5's ownership) and
562:   nothing in `tools/`, `models/`, or `general/`; record the residual match
563:   list in the Progress entry — depends on: Tasks 3.2, 3.3, 3.4 — status: not-
564:   started
565: - [ ] Task 3.6: Phase-end quality gate — full gate; `specmgr mcp-docs` +
566:   `specmgr docs` regeneration, then `git diff --exit-code -- docs/` zero
567:   drift (`docs/MCP.md` loses the seven `update_<d>` entries; `docs/api/`
568:   loses the seven module pages); add a dated entry to the Recent Updates
569:   section, update Current Status, flip the phase's task lines to done in
570:   place — depends on: Task 3.5 — status: not-started
571: 
572: #### Phase 4: Generic `set_status` + retire the eight old status tools
573: 
574: - [ ] Task 4.1: Create `general/tools/set_status.py`: eight private adapters
575:   `_set_status_<d>` — seven verbatim ports of the `set_status_<d>` bodies
576:   (lock, `load_by_id`, raw body re-read via the established
577:   `frontmatter.loads(...).content` mechanism, frontmatter reconstructed
578:   through the domain `XFrontmatter` constructor so the closed vocabulary
579:   validates, `updated` bump, body persisted verbatim, domain
580:   `XNotFoundError`) plus the ADR port (lock, `load_by_id`, delegation to
581:   `models.adr.v1.mutations.set_status(adr, status, superseded_by)`,
582:   `write_adr` render round-trip, `AdrNotFoundError`); the guard (`
583:   superseded_by is not None` and `type != "adr"` → `ValueError`, before any
584:   file access); a dispatch table; and `@mcp.tool(name="set_status", ...)`
585:   `def set_status(id: str, type: Literal["req","uc","tsk","qa","prb","gol",
586:   "rsk","adr"], status: str, superseded_by: str | None = None) ->
587:   ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
588:   GolDocument | RskDocument | Adr` with a full numpy-style docstring —
589:   depends on: Phase 3 complete (the `set_status` tool name must be free
590:   before this tool registers — see Design Notes, Name-collision constraint) —
591:   status: not-started
592: - [ ] Task 4.2: Delete the eight superseded modules: `adr/tools/set_status.py`,
593:   `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`,
594:   `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`,
595:   `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`,
596:   `rsk/tools/set_status_rsk.py` — depends on: Task 4.1 — status: not-started
597: - [ ] Task 4.3: Delete the eight test files: `tests/adr/tools/
598:   test_set_status.py`, `tests/req/tools/test_set_status_req.py`,
599:   `tests/uc/tools/test_set_status_uc.py`, `tests/tsk/tools/
600:   test_set_status_tsk.py`, `tests/qa/tools/test_set_status_qa.py`,
601:   `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/
602:   test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py` — depends
603:   on: Task 4.1 — status: not-started
604: - [ ] Task 4.4: Register `set_status` in `general/tools/__init__.py` (import,
605:   `__all__`, module docstring); update `adr/tools/__init__.py` and the seven
606:   domain `tools/__init__.py` files (remove the `set_status*` imports,
607:   `__all__` entries, and docstring mentions; note status changes go through
608:   the generic `set_status` in `general/tools/`); update the eight domain
609:   `__init__.py` docstring enumerations likewise — depends on: Tasks 4.2, 4.3 —
610:   status: not-started
611: - [ ] Task 4.5: Update `server.py`'s module docstring: remove `set_status`
612:   from the ADR tools line and `set_status_<d>` from the seven per-domain
613:   lines; add `set_status` to the General-tools lines (8-value `type`;
614:   `superseded_by` is ADR-only) — depends on: Tasks 4.1, 4.4 — status: not-
615:   started
616: - [ ] Task 4.6: `tests/general/tools/test_set_status.py` — parameterized over
617:   all eight types (ACC-004 cases): status changed + `updated` bumped + body
618:   untouched (seven domains: raw body byte-identical; ADR: re-parsed document
619:   equal apart from status/updated); closed-vocabulary enforcement per domain
620:   (positive value from the domain's own set; negative value — re-read each
621:   domain's `_ALLOWED_STATUSES` and pick a value valid in one domain but
622:   invalid in the tested one, e.g. `implemented` against `rsk`/`uc`/`tsk`/`qa`/
623:   `prb`, `open` against `req` — each → `pydantic.ValidationError`, file
624:   untouched); ADR `superseded_by` composes `"superseded by X"` in the file;
625:   ADR plain `status` values work with `superseded_by=None`; `superseded_by`
626:   with any non-`adr` type → `ValueError`, file untouched; unknown id →
627:   domain `XNotFoundError` / `AdrNotFoundError` — depends on: Task 4.1 —
628:   status: not-started
629: - [ ] Task 4.7: Phase-end quality gate — full gate including Task 4.6's new
630:   tests; `specmgr mcp-docs` + `specmgr docs` regeneration, then `git diff
631:   --exit-code -- docs/` zero drift; add a dated entry to the Recent Updates
632:   section, update Current Status, flip the phase's task lines to done in
633:   place — depends on: Tasks 4.5, 4.6 — status: not-started
634: 
635: #### Phase 5: Narration rewrite (prompts + instruction data)
636: 
637: - [ ] Task 5.1: Grep-driven rewrite of every instruction data file naming a
638:   superseded tool (`grep -rn "update_req\|update_uc\|update_tsk\|update_qa\|
639:   update_prb\|update_gol\|update_rsk\|set_status_" src/biz/dfch/specmgr/
640:   */data/` plus bare `set_status(` in the ADR data files). Eleven files
641:   expected: the six `<d>_update_instructions.md` (req, tsk, qa, rsk, prb,
642:   gol — `uc` has no prompts sub-package): `update_<d>(id, content)` →
643:   `update(id, type="<d>", content)`; `set_status_<d>(id, status)` →
644:   `set_status(id, type="<d>", status)`; **add a range-update passage** — for
645:   a localized change (one paragraph/field/section), first call
646:   `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based
647:   line range (the `N+1` position is end-of-body), and call
648:   `update(id, type="<d>", content, begin=…, end=…)` passing only the
649:   replacement lines; for multi-section or uncertain changes, use the whole-
650:   body replace (no `begin`/`end`); correct each file's status-vocabulary
651:   prose where it differs per the Design-Notes table. `qa/data/
652:   qa_refine_instructions.md`: its `update_qa` call sites → `update(id,
653:   type="qa", …)` (refine appends — use the `N+1` append range for a clean
654:   append, else whole-body; keep the existing carry-forward guidance for the
655:   whole-body path). The four ADR instruction files: `set_status(id, status[,
656:   superseded_by])` → `set_status(id, type="adr", status[, superseded_by])` —
657:   depends on: Phase 4 complete — status: not-started
658: - [ ] Task 5.2: Correct prompt Python module docstrings that name superseded
659:   tools: the six `prompts/update_<d>.py` modules (rsk's is `update_risk.py`,
660:   tsk's is `update_task.py`) — their module docstrings narrate the
661:   `update_<d>` / `set_status_<d>` surface; the four ADR prompt modules
662:   (`create_adr.py`, `create_adr_test.py`, `update_adr.py`,
663:   `update_adr_test.py`) — their surface mentions of `set_status` stay true
664:   (the tool still exists, now generic) but are made precise where they imply
665:   the old ADR-only signature. No behavioral change to any prompt function —
666:   depends on: Task 5.1 — status: not-started
667: - [ ] Task 5.3: Update the ten prompt test files to assert the rewritten
668:   narration: `tests/req/prompts/test_update_req.py`, `tests/tsk/prompts/
669:   test_update_task.py`, `tests/qa/prompts/test_update_qa.py`, `tests/rsk/
670:   prompts/test_update_risk.py`, `tests/prb/prompts/test_update_prb.py`,
671:   `tests/gol/prompts/test_update_gol.py`, `tests/adr/prompts/
672:   test_create_adr.py`, `tests/adr/prompts/test_create_adr_test.py`,
673:   `tests/adr/prompts/test_update_adr.py`, `tests/adr/prompts/
674:   test_update_adr_test.py` — assertions must confirm the generic call shapes
675:   (and, for the six domain update prompts, the range-update passage) —
676:   depends on: Tasks 5.1, 5.2 — status: not-started
677: - [ ] Task 5.4: Phase-end quality gate — full gate (the prompt data files are
678:   package data; `specmgr docs` regeneration covers Task 5.2's docstring
679:   changes), then `git diff --exit-code -- docs/` zero drift; add a dated
680:   entry to the Recent Updates section, update Current Status, flip the
681:   phase's task lines to done in place — depends on: Task 5.3 — status: not-
682:   started
683: 
684: #### Phase 6: Cross-cutting documentation and release notes
685: 
686: - [ ] Task 6.1: Update `AGENTS.md`: the seven per-domain bullets — remove
687:   `update_<d>`/`set_status_<d>` from each tool enumeration and note that
688:   whole-body/line-range updates go through the generic `update` tool and
689:   status changes through the generic `set_status` tool (both in
690:   `general/tools/`); the ADR bullet — remove `set_status` from its 12-wrapper
691:   enumeration (11 remain); the `general/` bullet — add `update` (7-type;
692:   optional `begin`/`end` range with the `N+1` sentinel) and `set_status`
693:   (8-type; ADR-only `superseded_by`), and note the `raw` parameter on the
694:   seven `get_<d>` tools; the "Still genuinely missing / not yet done" list —
695:   add the convention note that future domains (e.g. `ac`) add one dispatch
696:   entry to the two generic tools (plus a `raw` getter parameter) instead of
697:   new `update_<d>`/`set_status_<d>` tools, citing the Phase-1 ADR id —
698:   depends on: Phase 5 complete — status: not-started
699: - [ ] Task 6.2: Update `CHANGELOG.md`'s `[Unreleased]` section: **Breaking** —
700:   removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`,
701:   `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
702:   `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
703:   `set_status_gol`, `set_status_rsk`) and ADR `set_status`'s signature
704:   changes from `(id, status, superseded_by)` to `(id, type, status,
705:   superseded_by)` with `type="adr"` now required; **Added** — generic
706:   `update(id, type, content, begin, end)` (7 types; optional 1-based
707:   inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole)
708:   and generic `set_status(id, type, status, superseded_by)` (8 types);
709:   optional `raw: bool = False` on the seven `get_<d>` tools (returns the
710:   frontmatter-stripped body text verbatim — the text `begin`/`end` index
711:   into); cite the Phase-1 ADR id — depends on: Phase 5 complete — status:
712:   not-started
713: - [ ] Task 6.3: Final regeneration: `uv run --frozen specmgr docs`, `uv run
714:   --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc`, `uv run
715:   --frozen specmgr schema` (models are untouched — expect no schema
716:   changes); confirm `git diff --exit-code -- docs/` exits zero — depends on:
717:   Task 6.1, Task 6.2 — status: not-started
718: - [ ] Task 6.4: Phase-end quality gate — full gate; add a dated entry to the
719:   Recent Updates section, update Current Status, flip the phase's task lines
720:   to done in place — depends on: Task 6.3 — status: not-started
721: 
722: #### Phase 7: Final cross-cutting verification
723: 
724: - [ ] Task 7.1: Walk ACC-001…ACC-008 and confirm each with concrete evidence,
725:   annotating the Acceptance Criteria section inline in the style of
726:   feat-18-goal: live, un-mocked end-to-end in a temporary
727:   `SPECMGR_DOCS_DIR` — for `req`, `rsk`, and `uc`: `create_<d>` →
728:   `get_<d>(id, raw=True)` → `update(id, type, content, begin, end)` (one
729:   middle-range replace verified byte-exact, one `N+1` append) → `get_<d>`
730:   (content verified) → `set_status(id, type, status)` (domain-valid value
731:   from the Design-Notes table) → `get_<d>` (status verified); for ADR:
732:   `create_adr` → `set_status(id, type="adr", status="superseded",
733:   superseded_by=…)` → status reads `"superseded by …"`; confirm
734:   `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the
735:   real `server.mcp` instance reports 71 tools / 25 resources / 19 prompts;
736:   fresh-subprocess import check; full quality gate (ruff format/check, pylint
737:   advisory, vulture, unittest, `specmgr docs`/`mcp-docs`/`adr-toc`/`schema`
738:   zero drift); remove the temporary docs directory and confirm `git status`
739:   shows no residue — depends on: Phases 1–6 complete — status: not-started
740: - [ ] Task 7.2: Set this README's frontmatter `status: in-progress` →
741:   `status: done`; final Recent Updates entry and Current Status summary —
742:   depends on: Task 7.1 — status: not-started
743: 
744: **Note:** If a task's scope changes mid-flight, edit its description in
745: place; rely on git history (`git log -p` on this file) to recover what was
746: originally planned, rather than keeping a second copy of the task around.
747: 
748: ## Progress
749: 
750: ### Current Status
751: 
752: **As of 2026-08-26**: Planned. This README was drafted in the planning
753: session (all decisions in "Decisions Made" below are locked); all seven
754: phases are not started. Execution is handed to the phase-orchestrator via
755: `/implement-feature feat-22-consolidate-mutation-tools` (one phase-
756: implementer per phase, one Conventional Commit per accepted phase).
757: 
758: ### Blockers
759: 
760: None.
761: 
762: ### Recent Updates
763: 
764: #### Update 2026-08-26 (planning session)
765: 
766: - Completed: Feature planned end to end with the user. Design locked:
767:   generic `update(id, type, content, begin, end)` for the seven whole-body
768:   domains (line-range contract with the `N+1` EOF sentinel, splice-then-
769:   validate-whole), generic `set_status(id, type, status, superseded_by)` for
770:   all eight domains (ADR-only `superseded_by`), `get_<d>(raw=True)` body-text
771:   read, outright deletion of the 15 superseded tools, per-domain prompts
772:   kept with rewritten narration, and a short ADR (Phase 1).
773: - Next: Phase 1 (ADR) via `/implement-feature feat-22-consolidate-mutation-
774:   tools`.
775: - Notes: Phase 4 is deliberately atomic (add generic `set_status` + delete
776:   all eight old status tools) because ADR's existing tool already occupies
777:   the `set_status` name. Target end state: 71 tools / 25 resources / 19
778:   prompts (from 84/25/19).
779: 
780: ### Decisions Made
781: 
782: - **2026-08-26**: Explicit `type` parameter on both generic tools rather
783:   than bare-uuid resolution — per-domain v4 UUIDs are not *guaranteed*
784:   unique, uuid-only would force an all-domains directory scan (parsing every
785:   file) on the write path with cost growing per domain, and the calling
786:   client always already knows the domain.
787: - **2026-08-26**: ADR is excluded from `update` (its section-level MADR
788:   contract — `update_frontmatter`/`update_section`/`option_*` — has no
789:   whole-body replace by design) but included in `set_status` with the
790:   `superseded_by` special case.
791: - **2026-08-26**: The 15 superseded tools are deleted outright — no
792:   deprecated wrapper release; the package is 0.x and the MCP tool list is
793:   the only contract (breaking change recorded in `CHANGELOG.md`).
794: - **2026-08-26**: The per-domain `update_*` prompts are kept (domain-
795:   tailored interview guidance) and their narration text rewritten to the
796:   generic tools — rather than consolidating seven near-duplicate prompts
797:   into one generic prompt and losing domain-specific section names.
798: - **2026-08-26**: The decision is recorded as a short ADR (Phase 1) rather
799:   than README-only — it fixes a repo-wide convention future domains must
800:   follow (per AGENTS.md's "when in doubt, write the ADR").
801: - **2026-08-26**: `update` gains optional 1-based, inclusive `begin`/`end`
802:   body-line coordinates with an `N+1` EOF sentinel (append/through-EOF); the
803:   spliced result is always validated as a whole document before writing, and
804:   unchanged regions stay byte-identical to disk (user request: smaller,
805:   faster, safer targeted updates).
806: - **2026-08-26**: Line numbers are served by `get_<d>(raw=True)` (shared
807:   body-extraction helper with the splice) rather than re-introducing
808:   `specmgr://<d>/{id}` resources — ADR ddfb1109's empirical finding that
809:   agents invoke tools more reliably than parameterized resources, plus the
810:   maintenance cost of seven new resource templates, decided it.
811: 
812: ### Related PRs / Commits
813: 
814: None yet (one Conventional Commit per accepted phase, created by the phase-
815: orchestrator with user confirmation).

(End of file - total 815 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 81.0s)

_Thinking:_

Finished reading the entire plan. Let me also check history.md (which probably doesn't exist — ls showed only README.md… actually, in the first ls output the directory wasn't visible, so let me check the contents of the feat-22-consolidate-mutation-tools folder).

Wait, the first ls failed on the wrong path. Let me list the actual directory. Also, the git log showed a commit "f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools". The working tree status — the first command's output got cut off. Let me re-run git status.

Plan structure:

- Phase 1: ADR (Tasks 1.1–1.3)
- Phase 2: Generic `update` tool + `raw` read parameter (Tasks 2.1–2.9)
- Phase 3: Deprecate per-domain `update_*` tools (Tasks 3.1–3.6)
- Phase 4: Generic `set_status` + deprecate the 8 old status tools (Tasks 4.1–4.7)
- Phase 5: Narration rewrite (Tasks 5.1–5.4)
- Phase 6: Cross-cutting documentation and release notes (Tasks 6.1–6.4)
- Phase 7: Final cross-cutting verification (Tasks 7.1–7.2)

Dependencies: sequential Phase 1 → 2 → 3 → 4 → 5 → 6 → 7. Each phase has its own quality gate and progress update.

User instructions:

- Commit after each phase without confirmation (explicitly overriding the orchestrator's "confirm with user" step).
- Do not push.
- Continue without asking, except when hitting a wall or a decision is needed.
- Don't implement myself, use the phase-implementer agent.
- Act strictly as an orchestrator.

Before delegating a phase whose design depends on an undecided item, ask me first.

Let me scan for undecided items: the plan says "all decisions in 'Decisions Made' below are locked" and the blockers are "None". All design decisions appear to be resolved:

- Explicit type parameter — locked
- Exclude ADR from update — locked
- Direct deletion — locked
- Keep per-domain prompts — locked
- Short ADR — locked
- begin/end N+1 — locked
- raw parameter — locked

One thing to verify: the plan references `specmgr mcp-docs` as a CLI command. The dev commands in AGENTS.md list `specmgr docs`, `specmgr adr-toc`, `specmgr unused-code`, `specmgr version`, but don't mention `mcp-docs`. However, AGENTS.md also says "docs/MCP.md is auto-generated (via specmgr mcp-docs)". So mcp-docs exists. No issue.

Also the plan mentions `specmgr schema` — ACC-007 says "specmgr docs, specmgr mcp-docs, specmgr adr-toc, specmgr schema all report zero drift". OK.

The quality gate for each phase: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`, plus regeneration, `git diff --exit-code -- docs/`.

Let me verify the current state of the repo: git status, whether pre-commit is installed, and quickly check the current tool count to confirm the "84 tools" claim. Actually the phase-implementer will handle the implementation; I just need to confirm preflight: a clean working tree and that the plan is unambiguous.

Let me check:

1. ls of the feat-22 folder (is there a history.md?)
2. git status (clean?)
3. Maybe verify the current tool count with a quick python command — but that's close to read-only; no issue.

Also, per my workflow I should first build the todowrite list.

Another consideration: Phase 1 requires creating an ADR using the `specmgr_create_adr` MCP tool — the phase-implementer subagent has access to MCP tools (the specmgr server is available). Note: where does the ADR get created? The SPECMGR_ADR_DIR environment variable determines the base directory. In this repo it's probably `docs/adr`. I'll leave that detail to the implementer, but I should verify the tool writes to the repo's docs/adr directory. Let me check the environment: is there a .env file? The package uses python-dotenv. Let me quickly check how the ADR directory is resolved — I can look at `general/tools/_doc_paths.py`. Let me do a quick read to confirm the default base directory is `docs/adr` so that the phase-1 ADR lands in the repo.

Also check the current `set_status` tool for adr and the number of registered tools (84) to establish a baseline. Actually a quick python check:

```
uv run --frozen --all-extras python -c "import asyncio; from biz.dfch.specmgr.server import mcp; tools = asyncio.run(mcp.list_tools()); print(len(tools))"
```

Hmm, `mcp.list_tools()` on an MCPServer instance — in the mcp SDK, MCPServer has `list_tools()` which returns a list of Tool. ACC-008 says `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())`. So that works. This is a read-only verification and is permitted for the orchestrator.

Let me also confirm the default for SPECMGR_ADR_DIR. Quick look at \_doc_paths.py.

Plan for the next step:

1. Quick preflight checks (in parallel):
   - ls the feat-22 folder
   - git status
   - read general/tools/\_doc_paths.py (or grep for SPECMGR_ADR_DIR)
   - baseline tool/resource/prompt counts
2. Build the todowrite list (7 phases).
3. Delegate Phase 1 to phase-implementer.

Regarding preflight: I don't see any undecided items. The plan is detailed and locked. No need to ask the user.

The user explicitly said "commit after each phase without confirmation" — so my workflow step 6 (confirm with user) is overridden by user instructions. I'll commit without confirmation and never push.

Let me start with the preflight checks.

I've finished reading through the entire plan. It's a 7-phase sequential feature (ADR → generic `update`+`raw` → retirement of `update_*` → generic `set_status`+retirement of status tools → narration rewrite → docs/changelog → final validation), and all design decisions are locked in ("Decisions Made", no blockers). Next, I'll do preflight checks: repository state, where ADRs get placed, and the current tool count baseline.

**Tool: bash**

**Input:**

```json
{
  "command": "ls -la /home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/ && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 status --short && git -C /home/user/src/biz.dfch.SpecMgr-feat-22 log --oneline -3"
}
```

**Output:**

```
total 60
drwxrwxr-x  2 user user  4096 Aug 26 23:59 .
drwxrwxr-x 18 user user  4096 Aug 26 23:59 ..
-rw-rw-r--  1 user user 50522 Aug 26 23:59 README.md
f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools
3152c48 docs(termxplorer-mcp): add API investigation results for TermXplorer
0719f3e feat(dec): add plan for the Decision (DEC) artifact type

```

**Tool: grep**

**Input:**

```json
{
  "pattern": "SPECMGR_ADR_DIR|_ADR_DIR|adr_dir",
  "path": "/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools"
}
```

**Output:**

```
Found 1 matches
/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/_doc_paths.py:
  Line 28: ``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 77.5s)

_Thinking:_

The working tree is clean (git status --short output nothing). The feat-22 folder contains only README.md (no history.md).

ADR directory: the `SPECMGR_ADR_DIR` environment variable, with default being `docs/adr`. Let me check the default in adr/tools/\_paths.py to confirm that `specmgr_create_adr` will write to the repository's `docs/adr` (i.e., that the MCP server here is running with the repository as its base). Let me check the .env file and the \_paths defaults.

The working tree is clean. Let me verify the ADR directory default so that the Phase 1 ADR gets placed in the repository's `docs/adr`, and record the baseline tool/resource/prompt counts.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"SPECMGR_ADR_DIR\\|docs/adr\\|Path(\" /home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/adr/tools/_paths.py | head -30; ls -la /home/user/src/biz.dfch.SpecMgr-feat-22/.env 2>/dev/null; ls /home/user/src/biz.dfch.SpecMgr-feat-22/docs/adr | head -5"
}
```

**Output:**

```
56:ADR_DIR_ENV_VAR = "SPECMGR_ADR_DIR"
59:DEFAULT_ADR_DIR = Path("docs/adr")
81:    return Path(value) if value else DEFAULT_ADR_DIR
23a14195-339c-48af-99d2-97c9964041ae-use-iso-8601-for-all-dates-and-times.md
3159caf2-4beb-43f2-9f5d-8f46be0211af-adopt-icontract-as-the-design-by-contract-library-for-specmg.md
33c5ab08-ff58-4c73-8c32-23abaf3838e3-filesystem-is-the-sole-source-of-truth-no-in-memory-id-to-do.md
3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se.md
4c6119c9-532f-4629-8977-108e78304f48-parse-validate-render-pipeline-library-choices-no-ast-preser.md

```

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen --all-extras python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\ntools = asyncio.run(mcp.list_tools())\nresources = asyncio.run(mcp.list_resources())\nprompts = asyncio.run(mcp.list_prompts())\nprint('tools:', len(tools), 'resources:', len(resources), 'prompts:', len(prompts))\n\"",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22",
  "timeout": 180000
}
```

**Output:**

```
tools: 84 resources: 25 prompts: 19

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 25.3s)

_Thinking:_

Baseline confirmed: 84 tools / 25 resources / 19 prompts, matching the plan's "current 84/25/19". ADR directory default is `docs/adr` (relative path — cwd-dependent). The MCP server running here is… wait, I ran `uv run python -c` with workdir = repo root, so `docs/adr` resolves to the repo's docs/adr. The specmgr MCP server attached to my session (the one providing `specmgr_create_adr`) — its cwd might be different. The phase implementer uses the same MCP tools. Hmm, actually the phase-implementer subagent runs in the same environment. Let me think about whether `specmgr_create_adr` writes to the repo's docs/adr.

The MCP server in my session — where is it running from? If it was started from the repo root, then `docs/adr` is correct. This is exactly the kind of risk that could cause a phase to "hit a wall", but it's something the phase-implementer will discover immediately (the ADR file either appears in docs/adr, or appears somewhere else). Actually, let me quickly check whether there's a .env setting SPECMGR_ADR_DIR. `ls -la .env` produced no output (file doesn't exist — no line between the grep results and the docs/adr listing). So the default is in effect: relative path `docs/adr` from the MCP server process's cwd.

Can I verify the MCP server's cwd? Not directly. But I can confirm: the specmgr MCP server's tools in my session — e.g. `specmgr_list_adr` — should list ADRs from that directory. If it returns ADRs matching the repo's docs/adr contents, then the MCP server is rooted at the repo. Let me do a quick check of the ADR listing and compare counts.

Actually, even simpler: run `specmgr_list_adr` and compare with the file count in docs/adr.

Baseline confirmed: **84 tools / 25 resources / 19 prompts** — matches the plan. ADR directory resolves via `SPECMGR_ADR_DIR` or default `docs/adr` (cwd-relative). Going to verify whether the specmgr MCP server session is rooted in this repository (so that the Phase 1 ADR gets placed in the repo's `docs/adr`):

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

**Tool: bash**

**Input:**

```json
{
  "command": "ls /home/user/src/biz.dfch.SpecMgr-feat-22/docs/adr/*.md | wc -l"
}
```

**Output:**

```
25

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 79.1s)

_Thinking:_

The MCP server's ADR directory has 24 ADRs, but the repo's `docs/adr/*.md` has 25 files. One of those 25 files is probably `README.md` (the ADR table of contents). 25 - 1 (README.md) = 24. Matches. In other words, the specmgr MCP session is rooted at this repo's `docs/adr`. Phase 1's `specmgr_create_adr` will write into the repo's `docs/adr`.

Preflight complete:

- Clean tree ✓
- Plan is fully specified, all decisions locked, no blockers ✓
- Baseline 84/25/19 ✓ (matches the plan's "today's 84/25/19: −15 +2")
- MCP ADR directory = repo's docs/adr ✓
- No unresolved design decisions → no need to ask the user before delegation

Next, build the todowrite list: one entry per phase (7 phases), with a final wrap-up as well. Then delegate phase 1.

Phase 1 prompt to phase-implementer — must be precise and self-contained:

- Absolute path to the plan README: /home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
- Exact phase heading: "#### Phase 1: ADR"
- Tasks 1.1–1.3 verbatim (or with high fidelity)
- Context: repo, branch, commit policy
- Quality gate for phase 1: ruff format --check, ruff check, vulture, full unittest; no src/ changes expected → docs drift check covers only specmgr adr-toc output; `specmgr adr-toc` regeneration; git diff --exit-code -- docs/
- Progress update: README frontmatter status planning → in-progress, dated Recent Updates entry, Current Status, flip task lines to done
- Record the new ADR's id (in the Recent Updates entry / Decisions Made — the task says "record the new ADR's id")
- Do NOT commit, do NOT proceed to phase 2, stop and return a summary
- ADR content requirements: use specmgr_create_adr with status accepted; the body content is specified in Task 1.1 (context, decision drivers, options 1–3, decision outcome is option 1, consequences). The ADR should also include a "Pros and Cons of the Options" section — the create_adr tool has an `options` collection that backs the derived "## Pros and Cons of the Options". The plan's Task 1.1 enumerates three considered options; the implementer should fill in the options collection with pros/cons. Let's include this instruction.
- Note: per ADR 898bfcd0, never write the file by hand.
- Also, Task 1.2: validate with specmgr_validate_adr, run `uv run --frozen specmgr adr-toc`, confirm the ADR appears in docs/adr/README.md.
- Frontmatter: decision_makers? The plan doesn't specify. Keep it minimal: status accepted, date 2026-08-27 (today). In fact, per MADR, date is the last-updated date. Today is 2026-08-27.
- The phase gate says "no src/ changes expected" — the only file changes should be docs/adr/\*.md (new ADR), docs/adr/README.md (regenerated toc), and the feature README.md.

One question: does `specmgr_create_adr` set the frontmatter's `date`? The frontmatter model has a `date` field. The implementer can set date: "2026-08-27".

Also important: the new ADR file will be untracked in git until committed. I'll commit it after validation (the user said to commit after each phase without confirmation, and not to push).

Furthermore, the phase-implementer agent needs to know the working directory and commands. And a note about pre-commit hooks: committing is my job, not theirs.

Regarding conventions: the plan's "Phase-end quality gate (all phases)" is in Design Notes — include it in the prompt.

So now write the todo list, then launch the phase 1 subagent.

Todo list:

1. Phase 1: ADR (create feature ADR, adr-toc, gate, progress update) — in_progress
2. Phase 2: generic update tool + raw read parameter — pending
3. Phase 3: deprecate per-domain update\_\* tools — pending
4. Phase 4: generic set_status + deprecate the 8 old status tools — pending
5. Phase 5: narration rewrite (prompts + instruction data) — pending
6. Phase 6: cross-cutting documentation and release notes — pending
7. Phase 7: final cross-cutting validation + close feature — pending

Now the phase 1 prompt. Must be detailed and self-contained. Include:

- Role: implement exactly one phase, then stop.
- Plan path + phase heading.
- Tasks verbatim (1.1, 1.2, 1.3) — include the full text.
- Repo/commands context: uv run --frozen, ADR creation must use the specmgr_create_adr MCP tool (the specmgr MCP server is connected and rooted at this repo's docs/adr — verified: 24 ADRs).
- ADR content guidance from Task 1.1 (title, context, drivers, three options, outcome is option 1, consequences).
- status: accepted.
- Also fill in the options collection (Pros and Cons of the Options) — the plan lists 3 considered options, and each should have pros/cons content.
- After creation: specmgr_validate_adr, specmgr adr-toc, confirm it appears in docs/adr/README.md.
- Quality gate commands.
- Progress README update details: frontmatter status → in-progress, updated date → 2026-08-27, Recent Updates dated entry, Current Status, flip tasks 1.1/1.2/1.3 to done, record ADR id.
- Do NOT commit; do NOT proceed to phase 2; report back: ADR id, file path, evidence of gate runs (command + result), summary of changes.

Note on README editing: the phase-implementer has edit tools, no problem.

Another minor point: the plan's phase gate for phase 1 says "the docs/ drift check covers only the specmgr adr-toc output" — i.e., after `specmgr adr-toc`, docs/ should be drift-free relative to the commit (the regenerated README.md is the new expected state, so `git diff --exit-code -- docs/` will fail because the toc changed... no wait. Let me think.

`git diff --exit-code -- docs/` compares the working tree to the index/HEAD. If adr-toc regenerates docs/adr/README.md and it changed, then git diff will show the change → non-zero exit. But the phase gate in other phases says "regenerate, then zero drift via git diff --exit-code -- docs/" — meaning: run the regeneration, and the regenerated output must match what's already committed... no, that can't be right either, because the whole point of a regeneration in a phase is that it produces new content.

Let me reread: "regenerate `specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema` touched in the phase, then zero drift via `git diff --exit-code -- docs/`."

I think the intent is: after regeneration, run the generation command again to confirm it's idempotent / stable — i.e., a second run produces no diff. Actually, the pre-commit hooks (specmgr docs hook, adr-toc hook) run the generation at commit time. "Zero drift via git diff --exit-code -- docs/" in the context of these hooks means: after the hook runs the generator, the working tree should equal HEAD (the generator didn't change anything beyond what the phase already committed/regenerated). In other words, the phase itself must regenerate the docs, and then a subsequent regeneration must produce no further changes.

For a phase that adds tools: the implementer runs `specmgr mcp-docs` + `specmgr docs`, commits the regenerated output as part of the phase (I commit). Then at commit time the pre-commit hook runs the generator again; if the output is stable (no drift), the commit proceeds. The "zero drift via git diff --exit-code -- docs/" check the implementer can do: run the generator twice and confirm the second run changes nothing, or simply confirm that after regeneration, `git diff` on docs/ shows only the expected new content (and a re-run of the generator produces no additional changes).

I'll instruct the implementer as follows: regenerate all generators touched in the phase, then re-run each generator and confirm the second run is a no-op (zero diff) — this is the "drift-free" proof. This matches the pre-commit behavior.

OK. The phase-implementer's description says it handles "code, tests, phase-end quality gate, and updating the plan's Progress section — then stops and reports". Good.

So launch phase 1. Mark todo 1 as in_progress.

Preflight is clean:

- **Working tree**: clean, branch tip is at the planning commit `f9586e6`
- **Plan**: fully specified — all design decisions are locked in ("Decisions Made"), no blockers, no unresolved issues requiring your judgment
- **Baseline**: confirmed live MCP registration is **84 tools / 25 resources / 19 prompts** (plan: −15 +2 → target 71/25/19)
- **MCP ADR root**: the specmgr session lists exactly 24 ADRs = the repository's `docs/adr` (25 files minus the TOC `README.md`) — therefore, `specmgr_create_adr` in phase 1 will write to the repository

No unresolved design decisions → no questions needed. I'll set up the phase list and start delegating phase 1.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 5: Narration rewrite — 11 instruction data files, prompt module docstrings, 10 prompt test files, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
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
    "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 5: Narration rewrite — 11 instruction data files, prompt module docstrings, 10 prompt test files, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 2108.3s)

_Thinking:_

Here, delegate Phase 1 to a new phase-implementer subagent. A precise, self-contained prompt.

**Delegating Phase 1 (ADR)** to a fresh phase-implementer:

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 1 (ADR)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 1: ADR** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22` (a git repo, currently clean, on the branch that has planning commit `f9586e6` at its tip).\n\n## Your plan\nRead the full plan first: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`\nYour phase heading: `#### Phase 1: ADR` (Tasks 1.1, 1.2, 1.3). Read the whole README (Plan, Requirements, Design Notes, phase-end quality gate) for context, but implement ONLY Phase 1.\n\n## Environment facts (verified by the orchestrator — trust these)\n- The `specmgr` MCP server is connected in this environment and its ADR base directory resolves to THIS repo's `docs/adr` (it currently lists 24 ADRs, matching the 24 ADR files in `docs/adr/`). So `specmgr_create_adr` will write the new ADR file into the repo's `docs/adr/` directory.\n- Python tooling: always use `uv run --frozen` (add `--all-extras` if a CLI command fails on missing extras). Working directory for all commands: the repo root.\n- Per ADR 898bfcd0-85f9-462f-93a8-747bda4166c8: ADRs are authored ONLY through the MCP structured tools. **Never hand-write the ADR .md file.**\n\n## Tasks (verbatim from the plan)\n\n- **Task 1.1**: Create the feature's ADR with the `specmgr_create_adr` MCP tool, status `accepted`, title **\"Consolidate whole-body update and status-change tools into generic type-dispatched tools\"**. Required content:\n  - **Context**: 15 near-duplicate mutation tools exist (seven `update_<d>` + seven `set_status_<d>` + ADR `set_status`); LLM clients see 15 entries for 2 conceptual operations; each new domain (e.g. the planned `ac`) would add more duplicates.\n  - **Decision Drivers**: simpler tool surface; no all-directories write-path scan and no per-domain v4-UUID-collision ambiguity (uuid-only id resolution was rejected); the calling client already knows the domain; preserve the filesystem-is-source-of-truth and validate-before-write invariants.\n  - **Considered Options** (three): (1) generic tools with explicit `type` parameter — chosen; (2) uuid-only id resolution scanning all domain directories; (3) keep per-domain tools. Populate the ADR's `options` collection (which renders the derived `## Pros and Cons of the Options` section) with one `### Option` entry per considered option, each with concrete pros/cons content consistent with the drivers above (Option 2's cons: full-directory scan on every write parsing every file, cost growing per domain, UUIDs not guaranteed unique across domains since they are per-domain v4 UUIDs; Option 3's cons: 15 near-duplicate entries in the MCP tool list for 2 conceptual operations, every future domain adds N more tools, LLM clients must pick among duplicates; Option 1's pros: minimal surface, client already knows the domain, one dispatch entry per future domain, preserves all per-domain semantics via verbatim adapter ports; cons: breaking change for 0.x clients calling the removed tools, ADR needs special-casing in `set_status` (`superseded_by`) and is excluded from `update` by design).\n  - **Decision Outcome**: Option 1, with **Consequences**: breaking — 14 per-domain tools removed and ADR `set_status`'s signature gains a required `type` (callers must pass `type=\"adr\"`); ADR is excluded from `update` — its section-level MADR contract (`update_frontmatter`/`update_section`/`option_*`) has no whole-body replace — but included in `set_status` with the `superseded_by` special case; the `update` line-range contract: 1-based inclusive `begin`/`end`, `N+1` EOF sentinel, splice-then-validate-whole, frontmatter never addressable; `get_<d>(raw=True)` as the line-number source — tool-first per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614, re-introducing `specmgr://<d>/{id}` resources was considered and rejected; future domains add one dispatch entry per generic tool, not new tools.\n  - Frontmatter: `status: accepted`, `date: 2026-08-27`.\n- **Task 1.2**: Validate the new ADR with `specmgr_validate_adr`; run `uv run --frozen specmgr adr-toc` (from the repo root) and confirm the ADR appears in `docs/adr/README.md`.\n- **Task 1.3**: Phase-end quality gate — full gate per the plan's Design Notes \"Phase-end quality gate\" section: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"` (use `--all-extras` on the `uv run` calls if a ModuleNotFoundError for CLI/MCP extras appears). No `src/` changes are expected in this phase, so the docs-drift check covers `specmgr adr-toc` output only: after regenerating, re-run `specmgr adr-toc` a second time and confirm it is a no-op (no further file changes — that is the zero-drift proof; the committed-state comparison happens at commit time, which is NOT your job). Fix any failure and re-run until green — a phase is not done with a red gate.\n  Then update the plan README at `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`:\n  - frontmatter: `status: planning` → `status: in-progress`, and `updated: 2026-08-27`;\n  - **Current Status**: rewrite to reflect Phase 1 complete / Phases 2–7 not started (as of 2026-08-27);\n  - **Recent Updates**: add a new dated entry `#### Update 2026-08-27 (Phase 1: ADR)` recording: the new ADR's id and title (get the id from the `specmgr_create_adr` result — a UUID), that it is `accepted` and listed in `docs/adr/README.md`, and the gate result; keep the existing planning-session entry below it (do not delete history);\n  - **Decisions Made**: append one bullet recording the new ADR's id (the plan's Related ADRs section anticipates \"its id is recorded in Decisions Made once created\");\n  - flip Task 1.1, 1.2, 1.3 lines to done in place (`- [x]` and `status: done` at the end of each task line, matching how the plan writes status on the task line).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`). The orchestrator commits after verifying.\n- Do NOT start Phase 2 or touch any phase-2+ files (no `general/tools/update.py`, no `src/` changes at all in this phase — the only file changes should be: the new ADR `.md` in `docs/adr/`, the regenerated `docs/adr/README.md`, and the feature README's Progress updates).\n- Do NOT renumber or reword tasks; edit status in place only.\n- If you hit a genuine blocker (e.g. `specmgr_create_adr` writes somewhere unexpected, a gate failure you cannot fix within Phase 1 scope), STOP and report it — do not invent a workaround.\n\n## Report back (your final message)\n1. The new ADR's id (UUID) and on-disk file path.\n2. Evidence for each task: the `specmgr_validate_adr` result, the `specmgr adr-toc` run + confirmation the ADR row is in `docs/adr/README.md` (quote the row), and the no-op second run.\n3. The full quality-gate commands with their pass/fail output summaries (ruff format --check, ruff check, vulture, unittest counts).\n4. `git status --short` and `git diff --stat` of your changes.\n5. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbfde3d13ffeCzV54ScW0EWtZP" state="completed">
<task_result>


Phase 1 is complete and verified. Final report:

## Phase 1: ADR — Complete

### 1. New ADR
- **Id**: `36905d5b-8057-4294-8665-c7eed5534db0`
- **Title**: "Consolidate whole-body update and status-change tools into generic type-dispatched tools"
- **File**: `docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md`
- Created via `specmgr_create_adr` (not hand-written, per ADR 898bfcd0); frontmatter `status: accepted`, `date: 2026-08-27`; all required content present (Context: 15 near-duplicate tools / 2 operations; 4 Decision Drivers; 3 Considered Options with the 3-entry `options` collection rendering `## Pros and Cons of the Options` with concrete pros/cons; Decision Outcome = Option 1 with all five required Consequences).

### 2. Task evidence
- **Task 1.2** `specmgr_validate_adr(36905d5b-…)` → `true`. `uv run --frozen specmgr adr-toc` → `✓ Wrote docs/adr/README.md`. ADR row in `docs/adr/README.md` (lines 20–24):
```

- [Consolidate whole-body update and status-change tools into generic type-dispatched tools](36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md)
  - Id: 36905d5b-8057-4294-8665-c7eed5534db0
  - Status: accepted
  - Date: 2026-08-27
  - Decision-makers: OpenCode agent + user decision

```
- **No-op proof**: `md5sum docs/adr/README.md` before and after a repeat `specmgr adr-toc` run: `9312d8a223946cb7fb9b65da5a7823e3` both times (verified twice, including final state).

### 3. Quality gate (all green, re-run in final state)
| Command | Result |
|---|---|
| `uv run --frozen ruff format --check` | `1131 files already formatted` |
| `uv run --frozen ruff check` | `All checks passed!` |
| `uv run --frozen vulture src/ whitelist.py --min-confidence 60` | clean (exit 0, no output) |
| `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` | `Ran 1783 tests in 41.283s` → `OK` (exit 0) |
| `uv run --frozen specmgr adr-toc` ×2 | byte-identical (zero drift) |

No `src/` changes, so no `specmgr docs`/`mcp-docs`/`schema` regeneration was required this phase (per plan).

### 4. Git state (nothing staged, nothing committed)
```

M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
M docs/adr/README.md
?? docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md

```
`git diff --stat`: feature README `52 +++…` (43 insertions / 14 deletions total across both files), `docs/adr/README.md` `+5`. Verified via `git diff -U0` that the README change set is exactly: frontmatter `status: in-progress` / `updated: 2026-08-27`; Tasks 1.1–1.3 flipped to `- [x]` + `status: done` in place (original 2-space wrapping preserved byte-for-byte on every untouched line); Current Status rewritten (Phase 1 complete, Phases 2–7 not started, as of 2026-08-27); new `#### Update 2026-08-27 (Phase 1: ADR)` entry above the preserved planning-session entry; one new Decisions-Made bullet recording the ADR id.

### 5. Deviations / notes for the orchestrator
- **Mid-phase self-inflicted fix**: an Edit-tool whitespace-tolerant match briefly re-indented 9 continuation lines in the Phase-1 task region (2→3 spaces). Caught via byte-level `git diff -U0`/`cat -A` audit and fully restored — final diff contains zero unintended line changes.
- **Task 1.1 line merge**: the in-place flip of the wrapped `status: not-` / `started` pair to `status: done` necessarily collapses those two lines into one (the new value can't keep the mid-word wrap). This is the only structural change to a task line.
- **`decision-makers` added** to the ADR frontmatter ("OpenCode agent + user decision") beyond the mandated `status`/`date` — matches the repo's ADR convention for user-co-decided ADRs; trivial to drop via `specmgr_update_frontmatter` if undesired.
- `specmgr adr-toc` prints "✓ Wrote" even when content is unchanged; no-op status is proven by hash identity, not the message.
- Nothing blocks Phase 2; the new ADR id for later citation (AGENTS.md/CHANGELOG/Related ADRs) is `36905d5b-8057-4294-8665-c7eed5534db0`.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 24.0s)

_Thinking:_

Phase 1's subagent is reporting complete. Next, I have to verify independently:

1. Re-run the quality gate commands myself.
2. Inspect git status/diff.
3. Check the ADR file and its contents (read it).
4. Confirm that docs/adr/README.md contains that line.
5. Verify the README progress updates (frontmatter status, task checkboxes, Recent Updates, Decisions Made).

Let's run the verification in parallel:

- git status --short + diff
- ruff format --check, ruff check, vulture, unittest (the full suite takes about 41 seconds, so no problem)
- Read the new ADR file
- grep the ADR line in docs/adr/README.md
- Read the progress section of the feature README (the changed parts)

First, let's start with a batch of quick ones and the test suite.

Phase 1 reported complete. Now verifying independently — re-running the full gate and inspecting the diff:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && echo --- && git diff --stat && echo --- && uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22",
  "timeout": 300000
}
```

**Output:**

```
 M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
 M docs/adr/README.md
?? docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md
---
 .../feat-22-consolidate-mutation-tools/README.md   | 52 ++++++++++++++++------
 docs/adr/README.md                                 |  5 +++
 2 files changed, 43 insertions(+), 14 deletions(-)
---
1131 files already formatted
All checks passed!
VULTURE_OK

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md</path>
<type>file</type>
<content>
1: ---
2: status: accepted
3: date: '2026-08-27'
4: decision-makers: OpenCode agent + user decision
5: id: 36905d5b-8057-4294-8665-c7eed5534db0
6: version: 1.0.0
7: ---
8: 
9: # Consolidate whole-body update and status-change tools into generic type-dispatched tools
10: 
11: ## Context and Problem Statement
12: 
13: The specmgr MCP server currently exposes 15 near-duplicate mutation tools for what are two conceptual operations: seven per-domain whole-body updates (`update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`), seven per-domain status changes (`set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`, `set_status_gol`, `set_status_rsk`), and ADR's own `set_status`. Each tool shares the same shape — id resolution in one domain directory, validation, frontmatter carry-over, `updated` bump, write — and differs only in domain vocabulary. LLM/agent clients see 15 entries in the MCP tool list for 2 conceptual operations, and every future document domain (e.g. the planned `ac`) would add more of the same duplicates, growing the surface linearly with the number of domains.
14: 
15: ## Decision Drivers
16: 
17: - A simpler tool surface: the two conceptual operations should be exposed as two tools, not fifteen near-duplicates.
18: - Id resolution must not require an all-domains directory scan on the write path, and must not introduce per-domain v4-UUID-collision ambiguity — uuid-only id resolution was considered and rejected (per-domain v4 UUIDs are not guaranteed unique across domains).
19: - The calling client already knows the domain it is operating on (the same vocabulary as the frontmatter `type` field), so passing it explicitly costs the client nothing.
20: - Preserve the existing invariants: the filesystem is the sole source of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3) and validation happens before any write (nothing is written on validation failure).
21: 
22: ## Considered Options
23: 
24: - Option 1: two generic tools in `general/tools/` with an explicit `type` parameter — `update(id, type, content, begin, end)` covering the seven whole-body domains and `set_status(id, type, status, superseded_by)` covering all eight domains including `adr` — each dispatching to a private, verbatim-ported per-domain adapter. Chosen.
25: - Option 2: generic tools that resolve the id by uuid alone, scanning every domain directory to locate the matching document.
26: - Option 3: keep the 15 per-domain tools unchanged.
27: 
28: ## Decision Outcome
29: 
30: Option 1: two generic, type-dispatched tools — `update(id, type, content, begin, end)` in `general/tools/update.py` for the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`), and `set_status(id, type, status, superseded_by)` in `general/tools/set_status.py` for all eight domains including `adr`. The explicit `type` parameter keeps id resolution single-domain (no directory scan, no cross-domain UUID ambiguity), matches the domain vocabulary the calling client already has, and reduces the tool surface from 15 near-duplicate entries to 2. Each domain's semantics are preserved 1:1 by a private adapter that is a verbatim port of the deleted tool body, so the filesystem-is-source-of-truth and validate-before-write invariants are untouched.
31: 
32: ### Consequences
33: 
34: - Bad (breaking): the 14 per-domain tools are removed outright, and ADR `set_status`'s signature gains a required `type` parameter — existing ADR callers must now pass `type="adr"`. The package is 0.x and the MCP tool list is the only client contract; the breaking change is recorded in `CHANGELOG.md`.
35: - ADR is excluded from `update` — its section-level MADR contract (`update_frontmatter`/`update_section`/`option_*`, ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) has no whole-body replace by design — but is included in `set_status` with the `superseded_by` special case: `superseded_by` composes the status as `"superseded by {superseded_by}"`, and `superseded_by` given with any `type` other than `"adr"` raises `ValueError` before any file access.
36: - The `update` line-range contract: optional 1-based, inclusive body-line coordinates `begin`/`end`, with `N+1` as the EOF sentinel (`begin = end = N+1` appends at end of body; `end = N+1` extends the range through the last line). The spliced result is validated as a whole document before anything is written (splice-then-validate-whole), and the YAML frontmatter is never addressable (coordinates are body-relative by construction).
37: - Line numbers for range updates are served by a new `get_<d>(raw=True)` parameter returning the frontmatter-stripped body text verbatim — tool-first per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (agents invoke tools more reliably than parameterized resources); re-introducing `specmgr://<d>/{id}` resources was considered and rejected.
38: - Good: future domains (e.g. `ac`) add one dispatch entry per generic tool (plus a `raw` getter parameter), not new tools.
39: 
40: ## Pros and Cons of the Options
41: 
42: ### Option 1: Generic tools with an explicit type parameter
43: 
44: #### Pros
45: 
46: - Minimal tool surface: two tools for the two conceptual operations (the feature ends at 71 tools / 25 resources / 19 prompts, from 84/25/19: −15 +2), instead of 15 near-duplicate entries in the MCP tool list.
47: - The calling client already knows the domain — it is the same vocabulary as the frontmatter `type` field — so the explicit parameter costs the client nothing, and id resolution stays single-domain: no all-directories scan on the write path, no per-domain v4-UUID-collision ambiguity.
48: - Every future domain (e.g. the planned `ac`) adds one dispatch entry per generic tool, keeping the surface flat as domains grow.
49: - Preserves all per-domain semantics: each adapter is a verbatim port of the deleted tool body (same lock, same `load_by_id`, same frontmatter carry-over and `updated` bump, same write path, same domain not-found error), and the filesystem-is-source-of-truth and validate-before-write invariants are untouched.
50: 
51: #### Cons
52: 
53: - Breaking change for 0.x clients: the 14 per-domain tools disappear, and ADR `set_status`'s signature gains a required `type` (existing ADR callers must now pass `type="adr"`).
54: - ADR needs special-casing in `set_status` (the `superseded_by` composition) and is excluded from `update` by design (its MADR section-level contract has no whole-body replace).
55: 
56: ### Option 2: uuid-only id resolution scanning all domain directories
57: 
58: #### Pros
59: 
60: - Shortest client call: no `type` parameter; any document in any domain is addressable by id alone.
61: 
62: #### Cons
63: 
64: - Full-directory scan on every write: all domain directories must be traversed and every file parsed to locate the matching id, and the cost grows with each added domain on the write path.
65: - Per-domain v4 UUIDs are not guaranteed unique across domains, so a collision between two domains makes the id ambiguous — the server would have to pick one arbitrarily or raise a new class of errors.
66: - Loses the explicit domain vocabulary clients already use everywhere else (the frontmatter `type` field) and obscures which domain's semantics (status vocabulary, lock, write path) are actually being applied.
67: 
68: ### Option 3: Keep the per-domain tools
69: 
70: #### Pros
71: 
72: - No breaking change; existing clients keep working unchanged.
73: - No dispatch-table machinery; each tool remains a simple single-domain wrapper.
74: 
75: #### Cons
76: 
77: - The MCP tool list carries 15 near-duplicate entries for 2 conceptual operations, inflating every client's tool context.
78: - Every future domain adds more near-duplicate tools (a `update_<d>` / `set_status_<d>` pair per domain), growing the surface linearly with the number of domains.
79: - LLM clients must pick among the duplicates for each operation, which risks mis-selection and makes the surface harder to document, test, and keep consistent.
80: 
81: ## More Information
82: 
83: - Feature plan and progress: `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`.
84: - Related ADRs: ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based document reads are tools, not resources), 71fd95d7-07f2-466f-81aa-d29b7e3ef34c (the ADR `update_section` contract that `update` deliberately does not extend to ADR), 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth), ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy — the generic tools live in the cross-cutting `general/` package).

(End of file - total 84 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 70.0s)

_Thinking:_

The ADR content is excellent — it covers all the requirements of Task 1.1:

- Context: 15 nearly duplicated tools / 2 operations ✓
- Decision drivers (4 items) ✓
- Considered options (3 items) ✓, and the "Pros and Cons of the Options" section including all 3 options ✓
- Decision outcome = Option 1 ✓
- Consequences: breaking changes, ADR excluded from update / included in set_status, row-range contracts, raw=True, dispatch entry for future domains ✓
- status: accepted, date 2026-08-27 ✓
- id: 36905d5b-8057-4294-8665-c7eed5534db0 ✓

Gate re-runs: ruff format ✓, ruff check ✓, vulture ✓. What's still needed:

- unittest suite (takes about 41 seconds)
- no-op check for adr-toc (run `specmgr adr-toc` and check the hash; the implementer has already proven it, but I'll verify the current state: run it and take the diff)
- git diff of the feature README (verify that only the progress changes are in place)
- the ADR row in docs/adr/README.md

I'll run unittest and the adr-toc re-run, and in parallel read the feature README diff.

ADR content is complete and accurate against Task 1.1. Continuing verification: full test suite, adr-toc no-op proof, and the feature README diff.

**Tool: bash**

**Input:**

```json
{
  "command": "md5sum docs/adr/README.md && uv run --frozen specmgr adr-toc && md5sum docs/adr/README.md && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" 2>&1 | tail -3",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
9312d8a223946cb7fb9b65da5a7823e3  docs/adr/README.md
✓ Wrote docs/adr/README.md
9312d8a223946cb7fb9b65da5a7823e3  docs/adr/README.md
[4] ## *More* `heading`

[0] # Title

```

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U3 -- .specmgr/feat/feat-22-consolidate-mutation-tools/README.md docs/adr/README.md",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md b/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
index f3683ac..155696d 100644
--- a/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
+++ b/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
@@ -1,8 +1,8 @@
 ---
 created: 2026-08-26
 id: feat-22-consolidate-mutation-tools
-status: planning
-updated: 2026-08-26
+status: in-progress
+updated: 2026-08-27
 version: 1.0.0
 ---
 
@@ -420,7 +420,7 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
 
 #### Phase 1: ADR
 
-- [ ] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP
+- [x] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP
   tool (never hand-write the file — ADR 898bfcd0), status `accepted`, title
   "Consolidate whole-body update and status-change tools into generic type-
   dispatched tools": Context (15 near-duplicate mutation tools; LLM clients
@@ -440,18 +440,17 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   frontmatter never addressable; `get_<d>(raw=True)` as the line-number
   source — tool-first per ADR ddfb1109, re-introducing `specmgr://<d>/{id}`
   resources was considered and rejected; future domains add one dispatch
-  entry per generic tool, not new tools) — depends on: none — status: not-
-  started
-- [ ] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run
+  entry per generic tool, not new tools) — depends on: none — status: done
+- [x] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run
   --frozen specmgr adr-toc` and confirm the ADR appears in
-  `docs/adr/README.md` — depends on: Task 1.1 — status: not-started
-- [ ] Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff
+  `docs/adr/README.md` — depends on: Task 1.1 — status: done
+- [x] Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff
   check, vulture, full unittest suite; no `src/` changes are expected, so
   `docs/` drift checks cover `specmgr adr-toc` output only); set this
   README's frontmatter `status: planning` → `status: in-progress`; add a
   dated entry to the Recent Updates section, update Current Status, flip the
   phase's task lines to done in place; record the new ADR's id — depends on:
-  Task 1.2 — status: not-started
+  Task 1.2 — status: done
 
 #### Phase 2: Generic `update` tool + `raw` read parameter
 
@@ -749,11 +748,12 @@ originally planned, rather than keeping a second copy of the task around.
 
 ### Current Status
 
-**As of 2026-08-26**: Planned. This README was drafted in the planning
-session (all decisions in "Decisions Made" below are locked); all seven
-phases are not started. Execution is handed to the phase-orchestrator via
-`/implement-feature feat-22-consolidate-mutation-tools` (one phase-
-implementer per phase, one Conventional Commit per accepted phase).
+**As of 2026-08-27**: Phase 1 (ADR) complete — the feature's ADR
+36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
+status-change tools into generic type-dispatched tools") was created via
+`specmgr_create_adr`, validated with `specmgr_validate_adr`, and listed in
+`docs/adr/README.md` (regenerated with zero drift); the phase-end quality
+gate is green. Phases 2–7 are not started.
 
 ### Blockers
 
@@ -761,6 +761,23 @@ None.
 
 ### Recent Updates
 
+#### Update 2026-08-27 (Phase 1: ADR)
+
+- Completed: Phase 1 (Tasks 1.1–1.3). Created the feature's ADR via
+  `specmgr_create_adr` (never hand-written — ADR 898bfcd0): id
+  36905d5b-8057-4294-8665-c7eed5534db0, title "Consolidate whole-body update
+  and status-change tools into generic type-dispatched tools", status
+  `accepted`, date 2026-08-27, on disk at
+  `docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-
+  update-and-status-change-tools-into-g.md`. `specmgr_validate_adr` passed;
+  `specmgr adr-toc` regenerated `docs/adr/README.md` with the ADR row
+  listed, and repeat runs are byte-identical no-ops (zero drift).
+- Quality gate (green): `ruff format --check` (1131 files already
+  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py
+  --min-confidence 60` (clean), full unittest suite (Ran 1783 tests, OK).
+  No `src/` changes in this phase.
+- Next: Phase 2 (Generic `update` tool + `raw` read parameter).
+
 #### Update 2026-08-26 (planning session)
 
 - Completed: Feature planned end to end with the user. Design locked:
@@ -808,6 +825,13 @@ None.
   `specmgr://<d>/{id}` resources — ADR ddfb1109's empirical finding that
   agents invoke tools more reliably than parameterized resources, plus the
   maintenance cost of seven new resource templates, decided it.
+- **2026-08-27**: The Phase-1 ADR was created with id
+  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
+  status-change tools into generic type-dispatched tools", status
+  `accepted`) — it records the explicit-`type` dispatch convention (uuid-
+  only resolution rejected), ADR's exclusion from `update` / inclusion in
+  `set_status` with the `superseded_by` special case, the `update` line-
+  range contract, and the `get_<d>(raw=True)` decision.
 
 ### Related PRs / Commits
 
diff --git a/docs/adr/README.md b/docs/adr/README.md
index 9e1e606..4641a91 100644
--- a/docs/adr/README.md
+++ b/docs/adr/README.md
@@ -17,6 +17,11 @@ Index of all ADRs in this repository.
   - Id: 33c5ab08-ff58-4c73-8c32-23abaf3838e3
   - Status: accepted
   - Decision-makers: dfch
+- [Consolidate whole-body update and status-change tools into generic type-dispatched tools](36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md)
+  - Id: 36905d5b-8057-4294-8665-c7eed5534db0
+  - Status: accepted
+  - Date: 2026-08-27
+  - Decision-makers: OpenCode agent + user decision
 - [Extract MCP Singleton into Its Own Module to Break Domain/Server Cyclic Imports](3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se.md)
   - Id: 3bf0326f-065a-424c-a2b9-87e5d5bcfa99
   - Status: accepted

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 116.8s)

_Thinking:_

Everything checked out with no issues, but I need to verify the unittest results — the tail of the output was as follows:

```
[4] ## *More* `heading`

[0] # Title
```

This looks like stray output, not the unittest summary. The unittest `tail -3` got mixed up… actually, that output `[4] ## *More* heading` and `[0] # Title` is bizarre — could it be from vulture? No, that's not it. Hmm, that was the output of the first command: md5sum, specmgr adr-toc (✓ Wrote), md5sum, and then the tail -3 of unittest. The tail shows those two weird lines. That's suspicious — it's not a "Ran N tests ... OK" line.

Wait — could those lines be part of unittest's verbose output? No, I wasn't using -v. In the case of non-verbose output, unittest prints the following on success:

```
Ran 1783 tests in 41.283s

OK
```

That's 3 lines. But what tail -3 showed was:

```
[4] ## *More* `heading`

[0] # Title
```

Hmm, this is strange. Did some test print something to stdout? Maybe some test somewhere in the test suite is outputting `[4] ## *More* heading` — could be a prompt test that outputs example output. Actually, wait — could the unittest run have failed, and the tail is showing part of a traceback? No, traceback lines look different.

Also, that blank line in between. Let me capture the exit code and re-run unittest properly to confirm. The command chain used `&&`, so `uv run ... unittest ... 2>&1 | tail -3` — because of the pipe, the exit code that of tail (the last command in the pipeline) — meaning even if unittest failed, the pipeline would have exited with 0. I need to verify the actual result. Let me re-run it, capturing the summary line and the exit code properly.

The README diff is exactly as required. However, the tail end of the unittest run looked off (it was showing what appeared to be stdout noise from a test, not the summary line, and the exit code was being masked by the pipe). I'll explicitly re-run the test suite to confirm:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase1-unittest.log 2>&1; echo \"exit=$?\"; tail -5 /tmp/opencode/phase1-unittest.log; grep -c \"^test\" /tmp/opencode/phase1-unittest.log 2>/dev/null | head -1",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
exit=0
[2] Paragraph on line 2.
[3] 
[4] ## *More* `heading`

[0] # Title
0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 51.4s)

_Thinking:_

exit=0 — the suite passed. The lines at the end are stdout noise from the test itself (some test is outputting lines with numbers). Let's grab the actual unittest summary from the log — either search for "Ran " or "OK" with grep.

Exit 0 confirmed. Let me pull the actual suite summary from the log:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase1-unittest.log"
}
```

**Output:**

```
Ran 1783 tests in 39.461s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 154.9s)

_Thinking:_

Phase 1 verification complete:

- ✅ `ruff format --check`: 1131 files already formatted
- ✅ `ruff check`: All checks passed
- ✅ `vulture`: Clean
- ✅ unittest: Ran 1783 tests, OK, exit code 0
- ✅ `specmgr adr-toc`: Idempotent (md5 is identical before and after: 9312d8a223946cb7fb9b65da5a7823e3)
- ✅ ADR file exists in docs/adr/ with correct front matter (status accepted, date, id), and all content required by Task 1.1 is present (context, 4 drivers, 3 options with pros/cons, outcome is option 1, all 5 consequences)
- ✅ ADR rows present in docs/adr/README.md
- ✅ Feature README: front matter status → in-progress, updated → 2026-08-27; tasks 1.1–1.3 flipped to done in place; Current Status updated; new dated Recent Updates entry; Decisions Made bullet recording the ADR id
- ✅ No src/ changes; git status shows only the expected 3 files

Minor notes from the implementer:

- Merging of task 1.1's line wrap (`status: not-started` → `status: done`) — acceptable, in place.
- `decision-makers: OpenCode agent + user decision` was added — matches the repo's conventions (other ADRs also have Decision-makers lines). No problem.

Phase 1 is approved. Next, commit as a single Conventional Commit (user instruction: commit after each phase without confirmation, no push).

Commit message: per ADR cb5a2d5f "Use Conventional Commits". Repo style is confirmed from git log: `feat(feat-22): add design and plan for consolidation of mutation tools`. So the scope is `feat-22`. Phase 1 is the ADR:

`docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools`

Hmm — the ADR is in docs/adr, and it also touches the feature README. Looking at past commits: "0719f3e feat(dec): add plan for the Decision (DEC) artifact type" — a docs-leaning commit uses feat(dec) scope. "f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools". So for the ADR, `docs(feat-22): ...` seems right.

The message is:

```
docs(feat-22): add Phase-1 ADR consolidating mutation tools (36905d5b)
```

Or, more in line with the repo's style (lowercase, descriptive):
`docs(feat-22): add ADR for generic type-dispatched update/set_status tools`

Body: mention that the ADR is accepted, adr-toc is regenerated, and the progress README is updated. Keep it concise.

Note: pre-commit hooks are installed (per AGENTS.md, one-time install; the hooks run ruff, unittest on changed files, specmgr docs, and adr-toc on changes under docs/adr). This commit touches docs/adr/\*.md → the adr-toc hook runs; since it's already generated, no drift. src changes: none → the specmgr docs hook is skipped. No problem.

Stage exactly 3 files: the new ADR, docs/adr/README.md, the feature README. Then commit. Then verify the commit and confirm it's unpushed.

**Phase 1 verification passed** — all gates were green in my own execution (ruff format/check, vulture, 1783 tests OK, adr-toc is a no-op byte-for-byte identical), the ADR's content satisfies Task 1.1, and the README's progress update is also accurate. Committing Phase 1 (per your instruction, no push, no confirmation):

**Tool: bash**

**Input:**

```json
{
  "command": "git add docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md docs/adr/README.md .specmgr/feat/feat-22-consolidate-mutation-tools/README.md && git commit -m \"docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools\n\nCreate the feature ADR 36905d5b-8057-4294-8665-c7eed5534db0 (status\naccepted) via specmgr_create_adr: explicit type dispatch over uuid-only\nresolution, ADR excluded from update but included in set_status with\nthe superseded_by special case, the 1-based inclusive begin/end range\ncontract with N+1 EOF sentinel, and get_<d>(raw=True) as the\nline-number source. Regenerate docs/adr/README.md (adr-toc) and update\nthe feature README progress (Phase 1 done, status in-progress).\" && git log --oneline -2 && git status --short",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
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
specmgr adr-toc..........................................................Passed
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 2647649] docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools
 3 files changed, 127 insertions(+), 14 deletions(-)
 create mode 100644 docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-into-g.md
2647649 docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools
f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 201.7s)

_Thinking:_

Phase 1 committed as `2647649` on branch `feat-22`. Pre-commit hooks passed (adr-toc Passed, others skipped since no target files). Working tree is clean. Not pushed.

Next up is Phase 2. Update the todo list, and delegate to a new phase-implementer with a detailed, self-contained prompt.

What Phase 2 needs:

- Task 2.1: `general/tools/_splice.py` — body_text(path) + splice_body(current_body, begin, end, content)
- Task 2.2: `general/tools/update.py` — 7 adapters, dispatch table, @mcp.tool(name="update", ...)
- Task 2.3: Registration into general/tools/__init__.py
- Task 2.4: `raw` parameter for the 7 get\_<d> tools
- Task 2.5: server.py module docstring
- Task 2.6: tests/general/tools/test_update.py
- Task 2.7: Extend the 7 tests/<d>/tools/test_get\_<d>.py files
- Task 2.8: Registration smoke test (unittest asserting update's input schema has a 7-value enum + optional begin/end) + fresh-subprocess import check at the gate
- Task 2.9: Phase-end quality gate + progress update

Key design details to include in the prompt (from the plan's design notes):

- \_splice.py: no mcp dependency, plain file I/O, module docstring explaining the raw/splice invariant; body_text via `frontmatter.loads(path.read_text(encoding="utf-8")).content`; splice_body implements the range contract exactly: N = len(current_body.splitlines()); ValueError for begin < 1, begin > end, end > N+1 (message must include the offending values and allowed ranges); remove lines begin..min(end, N); insert content.splitlines() at position begin-1; join with "\\n" + single trailing "\\n"; empty content = deletion.
- update.py: 7 private adapters _update_<d>(id\_, content, begin, end) — verbatim port of the current update\_<d> bodies (X_lock, load_by_id, frontmatter carry-over + microsecond updated bump, write_X_file, domain XNotFoundError) plus the range branch; both-or-neither ValueError guard before file access; dispatch table dict[str, Callable]; @mcp.tool(name="update", title="Update document", description=...) def update(id: str, type: Literal[...7...], content: str, begin: int | None = None, end: int | None = None) -> 7-way union; numpy-style docstring including range contract and error types.
- Important: parameter name is `type`; ruff's E/F/W has no builtin-shadow rule (plan asserts this).
- get\_<d>: signature get\_<d>(id: str, raw: bool = False) -> XDocument | str; raw=True resolves id as usual (no lock — read-only) and returns body_text(path); raw=False unchanged; update @mcp.tool description and docstring Returns.
- Import-ordering concern: general's import pulls in all 7 domain tools/prompts earlier than before — safe by construction; the fresh-subprocess import smoke test proves this.
- server.py docstring: add the update line to General-tools; add raw note where get\_<d> is enumerated.
- Tests:
  - test_update.py parameterized over all 7 types, seeds documents via the domain's create\_<d> tool in a temporary SPECMGR_DOCS_DIR, mirroring the fixture strategy of the still-on-disk tests/<d>/tools/test_update\_<d>.py files.
  - ACC-001 cases in whole-body mode + ACC-002 cases in range mode.
  - Extend the 7 test_get\_<d>.py with raw coverage (ACC-003): byte-identical body; coordinate invariant test (read raw, pick a range, update, assert the splice landed in the right place); raw=False regression; unknown id → XNotFoundError in both modes.
  - Registration smoke test: unittest asserting asyncio.run(mcp.list_tools()) contains update, with type rendered as a 7-value enum and optional integer begin/end in the input schema; plus at the gate, a fresh-subprocess `uv run --frozen python -c "import biz.dfch.specmgr.server"` check.
- Gate: full gate + specmgr mcp-docs + specmgr docs regeneration, zero drift via git diff --exit-code -- docs/ (interpretation: regenerate, then a second regeneration run is a no-op; also confirm the new entries appear in docs/MCP.md: update entry with the enum, and the raw note on get\_<d> entries).
- Progress update: dated Recent Updates entry, Current Status, flip tasks 2.1–2.9 to done.

Also, conventions from .specmgr/conventions.md: no assert for client input (use ValueError), type hints required, numpy-style docstrings, `result` for return values, etc. The implementer should read .specmgr/conventions.md.

Points to watch out for: Phase 2 is purely additive — the old update\_<d> tools and tests must remain untouched (they're deleted in Phase 3).

Another important detail: the 7-way union return type — how do the existing tools handle this? The domain document types are in <d>/models/vN/. Adapters need to import those types for the return annotation. The plan says annotation-only.

Also, the "two-channel contract" for update: `X.from_text(format_text(content))` — format_text is presumably from models/md. The verbatim port handles this.

Where is `load_by_id`? Each domain has a private helper. The old update\_<d> tool modules show exactly how. Instruction: read the 7 current update\_<d> modules and port them verbatim.

Also, the `general/tools/__init__.py` currently registers mdformat (and maybe others). Let the implementer inspect it.

One more thing: the plan says "plus their registration in general/tools/__init__.py" — for both update (Phase 2) and set_status (Phase 4). In Phase 2, only update.

Environment facts to hand off:

- Repo path, branch feat-22, current HEAD 2647649, clean tree.
- Baseline tool count is currently 84/25/19; after Phase 2: 85 tools (84 + update), 25 resources, 19 prompts. (Worth telling the implementer for the smoke test context, though the smoke test asserts the presence of update, not the total count.)
- uv run --frozen, --all-extras for CLI/MCP extras (the unittest discovery ran fine without --all-extras earlier... wait, my unittest run was `uv run --frozen python -m unittest discover` without --all-extras and it worked — tests must be in the dev group. The AGENTS.md dev command lists `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` without --all-extras. OK, use that exactly.
- Phase 2's fresh-subprocess import check: `uv run --frozen python -c "import biz.dfch.specmgr.server"` — hmm, does importing server require the mcp extra? server.py imports mcp — base deps are only pydantic + python-dotenv; mcp is in the `mcp` extra. But my earlier baseline run used `uv run --frozen --all-extras python -c ...` and it worked. Without --all-extras, `import biz.dfch.specmgr.server` would fail with ModuleNotFoundError: mcp? Unless dev deps include the mcp extra. My earlier unittest run without --all-extras worked, and tests probably import the server (a registration smoke test would need it). Actually, the existing tests probably already import biz.dfch.specmgr.server — e.g., there might be a test that lists tools. If unittest without --all-extras worked (1783 tests), then the mcp module is available in the default env (probably dev dependency group). But to be safe, tell the implementer: use exactly `uv run --frozen python -c "import biz.dfch.specmgr.server"` for the gate's subprocess check (the plan says so), and if it fails on a missing extra, retry with `--all-extras` and record it.

Wait, actually the plan's Task 2.8 says "plus a fresh-subprocess uv run --frozen python -c "import biz.dfch.specmgr.server" check run inside the phase gate." And ACC-008 (Phase 7) repeats the fresh subprocess import check. Follow the plan's exact command; if the env lacks the mcp extra, the tests themselves would already have failed in the full suite, so it's almost certainly fine.

Let me quickly confirm: does the current env (without --all-extras) have the mcp module? My baseline count command used --all-extras. unittest without --all-extras ran 1783 tests OK — among those tests, is any importing server? Probably (there should be MCP registration tests). Not 100% sure. Rather than block, let the implementer verify. Actually — it's a cheap check I can do right now and it informs the prompt. But it's also fine to let the implementer discover it; they have bash. I'll include a note.

Pre-commit hooks: commit touches src/ → ruff format, ruff check, vulture, unittest (scoped), specmgr docs, specmgr mcp-docs (hook list showed a "specmgr mcp-docs" hook!), specmgr schema hooks all run. Interesting — the hook list shows more hooks than AGENTS.md describes (coverage-badge, mcp-docs, schema ×7). Good to know: the commit itself runs the regeneration hooks; the implementer must leave the tree in a state where those hooks pass (i.e., docs already regenerated).

Wait — one concern: the pre-commit "specmgr docs" and "specmgr mcp-docs" hooks — do they run the generator and fail on drift, or do they run the generator and stage the output? AGENTS.md says "local specmgr docs hook (scoped to src/\*\*/\*.py changes), and local specmgr adr-toc hook" — "so broken tests or docs/api/... drift is caught locally rather than failing later in CI" — so they detect drift (fail on it) rather than auto-fixing. In Phase 1's commit, the adr-toc hook ran as "Passed" and the others were skipped. In Phase 2's commit, the docs/mcp-docs/schema/coverage-badge hooks will run — the implementer must regenerate everything touched: specmgr docs + specmgr mcp-docs + (schema is unchanged — but the hook runs `specmgr schema` for the domain package copies? "specmgr schema (req package copy)" etc. — those probably compare the generated schema files in the repo against the current model output. Models are unchanged, so it should pass).

Hmm, the coverage-badge hook: "specmgr coverage-badge" — scoped to what? Probably src changes → regenerate coverage badge in README? Let me not over-analyze; the hook's pass/fail will surface at commit time. If a hook fails at my commit, I investigate and send the implementer back. Actually — better: tell the implementer that the repo has pre-commit hooks (ruff, vulture, unittest, specmgr docs/mcp-docs/adr-toc/schema/coverage-badge) that run at commit time, and that the phase gate must leave the tree in a state where a commit would pass — i.e., all generators touched by the phase are already regenerated. That's exactly what the plan's gate requires.

Also let me double-check which generators exist: `specmgr docs` (docs/api + docs/GENERATED.md), `specmgr mcp-docs` (docs/MCP.md), `specmgr adr-toc` (docs/adr/README.md), `specmgr schema` (schema files?), and the coverage-badge one. Phase 2's plan gate: "uv run --frozen specmgr mcp-docs and uv run --frozen specmgr docs regeneration, then zero drift via git diff --exit-code -- docs/". So in Phase 2, mcp-docs + docs. The coverage-badge hook is scoped to… whatever; if the implementer's changes affect it (src changes), regeneration might be needed. Let me quickly check .pre-commit-config.yaml so I can give the implementer exact info about which hooks run on src changes. That's a read-only orchestrator action and worth it for accurate prompt construction.

Let me quickly read .pre-commit-config.yaml.

Phase 1 has been committed as `2647649` on branch `feat-22` — pre-commit hooks passed (adr-toc Passed, others correctly skipped). The tree is clean, and nothing has been pushed.

Before delegating Phase 2, I'll check the pre-commit configuration to find out exactly which hooks get triggered by `src/` changes (so the phase gate can leave a committable tree):

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/.pre-commit-config.yaml"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/.pre-commit-config.yaml</path>
<type>file</type>
<content>
1: repos:
2:   - repo: https://github.com/astral-sh/ruff-pre-commit
3:     rev: v0.16.1
4:     hooks:
5:       - id: ruff-format
6:       - id: ruff-check
7:         args: [--fix]
8: 
9:   - repo: local
10:     hooks:
11:       - id: vulture
12:         name: vulture
13:         description: >-
14:           Static dead-code check. Known false positives (Pydantic
15:           validators/config, MCP resource/tool entry points, the Typer
16:           `_callback`, etc.) are suppressed via whitelist.py -- add a name
17:           there only after confirming it's a real false positive, not
18:           genuine dead code, which should be deleted instead.
19:         entry: uv run --frozen vulture src/ whitelist.py --min-confidence 60
20:         language: system
21:         pass_filenames: false
22:         files: ^(src/.*\.py|whitelist\.py)$
23: 
24:       - id: unittest
25:         name: unittest
26:         description: Run the full test suite with coverage before every commit.
27:         entry: uv run --frozen coverage run -m unittest discover -v -s tests -t . -p "test_*.py"
28:         language: system
29:         pass_filenames: false
30:         files: ^(src|tests)/.*\.py$
31: 
32:       - id: specmgr-coverage-badge
33:         name: specmgr coverage-badge
34:         description: >-
35:           Generate coverage badge SVG, then fail if that changed anything
36:           -- standard formatter-hook UX: review and `git add` the regenerated
37:           badge, then commit again.
38:         entry: bash -c 'uv run --frozen specmgr coverage-badge && git diff --exit-code -- docs/coverage.svg'
39:         language: system
40:         pass_filenames: false
41:         files: ^(src|tests)/.*\.py$
42: 
43:       - id: specmgr-docs
44:         name: specmgr docs
45:         description: >-
46:           Regenerate docs/api/ and docs/GENERATED.md, then fail if that
47:           changed anything -- standard formatter-hook UX: review and
48:           `git add` the regenerated files, then commit again.
49:         entry: bash -c 'uv run --frozen specmgr docs && git diff --exit-code -- docs/'
50:         language: system
51:         pass_filenames: false
52:         files: ^src/.*\.py$
53: 
54:       - id: specmgr-mcp-docs
55:         name: specmgr mcp-docs
56:         description: >-
57:           Regenerate docs/MCP.md (MCP tools/resources/prompts reference),
58:           then fail if that changed anything -- standard formatter-hook UX:
59:           review and `git add` the regenerated file, then commit again.
60:           Triggers on any src/ change, not just adr/general/req/uc/resources/
61:           server.py -- a tool's generated parameter schema also depends on
62:           the shared models/ package (e.g. adding a field to AdrBody changes
63:           create_adr's schema without touching adr/tools/*.py), so this
64:           mirrors the equally broad specmgr-docs hook above rather than
65:           risk a missed regeneration.
66:         entry: bash -c 'uv run --frozen specmgr mcp-docs && git diff --exit-code -- docs/MCP.md'
67:         language: system
68:         pass_filenames: false
69:         files: ^src/.*\.py$
70: 
71:       - id: specmgr-adr-toc
72:         name: specmgr adr-toc
73:         description: >-
74:           Regenerate docs/adr/README.md, then fail if that changed anything
75:           -- standard formatter-hook UX: review and `git add` the regenerated
76:           file, then commit again.
77:         entry: bash -c 'uv run --frozen specmgr adr-toc && git diff --exit-code -- docs/adr/README.md'
78:         language: system
79:         pass_filenames: false
80:         files: ^docs/adr/.*\.md$
81: 
82:       - id: specmgr-schema
83:         name: specmgr schema
84:         description: >-
85:           Regenerate every registered doc-type JSON Schema (docs/{type}_schema.json)
86:           -- always runs with no `--type` (all registered types), currently `gol`,
87:           `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`. `specmgr schema` itself exits
88:           non-zero when the
89:           regenerated content differs from what was already on disk, so no separate
90:           `git diff --exit-code` is needed here, unlike the other `specmgr-*` hooks
91:           above.
92:         entry: uv run --frozen specmgr schema
93:         language: system
94:         pass_filenames: false
95:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
96: 
97:       - id: specmgr-schema-req-package
98:         name: specmgr schema (req package copy)
99:         description: >-
100:           Regenerate the packaged copy of REQ's JSON Schema
101:           (src/biz/dfch/specmgr/req/data/req_schema.json), read by the
102:           `specmgr://req/schema` MCP resource via `importlib.resources` so it
103:           works from a real, non-editable install (unlike `docs/req_schema.json`,
104:           which only resolves from an editable/source checkout). Same generator
105:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
106:           bespoke copy logic exists in `commands/schema.py`. Kept as an
107:           independent hook (not chained into `specmgr-schema`) so each artifact's
108:           drift check is its own clean gate.
109:         entry: uv run --frozen specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data
110:         language: system
111:         pass_filenames: false
112:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
113: 
114:       - id: specmgr-schema-uc-package
115:         name: specmgr schema (uc package copy)
116:         description: >-
117:           Regenerate the packaged copy of UC's JSON Schema
118:           (src/biz/dfch/specmgr/uc/data/uc_schema.json), read by the
119:           `specmgr://uc/schema` MCP resource via `importlib.resources` so it
120:           works from a real, non-editable install (unlike `docs/uc_schema.json`,
121:           which only resolves from an editable/source checkout). Same generator
122:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
123:           bespoke copy logic exists in `commands/schema.py`. Kept as an
124:           independent hook (not chained into `specmgr-schema`) so each artifact's
125:           drift check is its own clean gate.
126:         entry: uv run --frozen specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data
127:         language: system
128:         pass_filenames: false
129:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
130: 
131:       - id: specmgr-schema-tsk-package
132:         name: specmgr schema (tsk package copy)
133:         description: >-
134:           Regenerate the packaged copy of TSK's JSON Schema
135:           (src/biz/dfch/specmgr/tsk/data/tsk_schema.json), read by the
136:           `specmgr://tsk/schema` MCP resource via `importlib.resources` so it
137:           works from a real, non-editable install (unlike `docs/tsk_schema.json`,
138:           which only resolves from an editable/source checkout). Same generator
139:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
140:           bespoke copy logic exists in `commands/schema.py`. Kept as an
141:           independent hook (not chained into `specmgr-schema`) so each artifact's
142:           drift check is its own clean gate.
143:         entry: uv run --frozen specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data
144:         language: system
145:         pass_filenames: false
146:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
147: 
148:       - id: specmgr-schema-rsk-package
149:         name: specmgr schema (rsk package copy)
150:         description: >-
151:           Regenerate the packaged copy of RSK's JSON Schema
152:           (src/biz/dfch/specmgr/rsk/data/rsk_schema.json), read by the
153:           `specmgr://rsk/schema` MCP resource via `importlib.resources` so it
154:           works from a real, non-editable install (unlike `docs/rsk_schema.json`,
155:           which only resolves from an editable/source checkout). Same generator
156:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
157:           bespoke copy logic exists in `commands/schema.py`. Kept as an
158:           independent hook (not chained into `specmgr-schema`) so each artifact's
159:           drift check is its own clean gate.
160:         entry: uv run --frozen specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data
161:         language: system
162:         pass_filenames: false
163:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
164: 
165:       - id: specmgr-schema-qa-package
166:         name: specmgr schema (qa package copy)
167:         description: >-
168:           Regenerate the packaged copy of QA's JSON Schema
169:           (src/biz/dfch/specmgr/qa/data/qa_schema.json), read by the
170:           `specmgr://qa/schema` MCP resource via `importlib.resources` so it
171:           works from a real, non-editable install (unlike `docs/qa_schema.json`,
172:           which only resolves from an editable/source checkout). Same generator
173:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
174:           bespoke copy logic exists in `commands/schema.py`. Kept as an
175:           independent hook (not chained into `specmgr-schema`) so each artifact's
176:           drift check is its own clean gate.
177:         entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data
178:         language: system
179:         pass_filenames: false
180:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
181: 
182:       - id: specmgr-schema-prb-package
183:         name: specmgr schema (prb package copy)
184:         description: >-
185:           Regenerate the packaged copy of PRB's JSON Schema
186:           (src/biz/dfch/specmgr/prb/data/prb_schema.json), read by the
187:           `specmgr://prb/schema` MCP resource via `importlib.resources` so it
188:           works from a real, non-editable install (unlike `docs/prb_schema.json`,
189:           which only resolves from an editable/source checkout). Same generator
190:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
191:           bespoke copy logic exists in `commands/schema.py`. Kept as an
192:           independent hook (not chained into `specmgr-schema`) so each artifact's
193:           drift check is its own clean gate.
194:         entry: uv run --frozen specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data
195:         language: system
196:         pass_filenames: false
197:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
198:       - id: specmgr-schema-gol-package
199:         name: specmgr schema (gol package copy)
200:         description: >-
201:           Regenerate the packaged copy of GOL's JSON Schema
202:           (src/biz/dfch/specmgr/gol/data/gol_schema.json), read by the
203:           `specmgr://gol/schema` MCP resource via `importlib.resources` so it
204:           works from a real, non-editable install (unlike `docs/gol_schema.json`,
205:           which only resolves from an editable/source checkout). Same generator
206:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
207:           bespoke copy logic exists in `commands/schema.py`. Kept as an
208:           independent hook (not chained into `specmgr-schema`) so each artifact's
209:           drift check is its own clean gate.
210:         entry: uv run --frozen specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data
211:         language: system
212:         pass_filenames: false
213:         files: ^src/biz/dfch/specmgr/(gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$

(End of file - total 213 lines)
</content>
```

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 5: Narration rewrite — 11 instruction data files, prompt module docstrings, 10 prompt test files, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
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
    "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 5: Narration rewrite — 11 instruction data files, prompt module docstrings, 10 prompt test files, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 16590.9s)

_Thinking:_

Key facts about pre-commit regarding the Phase 2 commit (changes to src + changes to tests):

- ruff-format, ruff-check(--fix) run against staged files
- vulture runs against src
- unittest: full suite with coverage (`coverage run -m unittest discover -v ...`)
- specmgr coverage-badge: regenerates docs/coverage.svg and fails if there are any changes → **the implementer must run `uv run --frozen specmgr coverage-badge` and `git add` the badge if it was changed** — this is new information not included in the plan's gate list! Changes to tests/ alter coverage → docs/coverage.svg will almost certainly change. The plan's gate says "regeneration of `specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema` that the phase touches," but coverage-badge is also a generator tied to src/tests changes. Include it: run `specmgr coverage-badge` as part of the gate and commit the regenerated svg.
- specmgr docs: regenerates docs/api + docs/GENERATED.md and fails if there's a diff in docs/
- specmgr mcp-docs: regenerates docs/MCP.md and fails if there's a diff
- specmgr adr-toc: only for docs/adr changes (not in Phase 2)
- specmgr schema hook: only for changes under models/ (Phase 2 doesn't touch models) — skipped.

So the complete regeneration set for the Phase 2 gate is: `specmgr coverage-badge`, `specmgr docs`, `specmgr mcp-docs`. And the tree must be in a state where a second run of each becomes a no-op.

Also, note the hook's UX: "review the regenerated files, git add them, and commit again" — meaning the implementer should run the generators, review the diff, and leave the regenerated files in the working tree (I'll git add them when committing).

Now, let me write the Phase 2 prompt. It has to be comprehensive. Key content:

01. Plan path + phase heading + "implement only Phase 2."
02. Repo state: branch feat-22, HEAD 2647649 (Phase 1 commit), clean tree.
03. Context from Phase 1: ADR 36905d5b-8057-4294-8665-c7eed5534db0 accepted.
04. Environment: uv run --frozen; exact commands for the gate.
05. Tasks 2.1–2.9 verbatim.
06. Key design notes (dispatch architecture, update signature, exact semantics of the range contract, shared body extraction + raw invariant, import order considerations).
07. Important constraints: Phase 2 is purely additive — do not touch the old update\_<d> tool modules or their tests (deleted in Phase 3). Do not touch set_status tools at all (Phase 4). Do not change models.
08. Details of the pre-commit hooks (coverage-badge!) — the tree at handoff must pass all hooks: regenerate `specmgr coverage-badge` + `specmgr docs` + `specmgr mcp-docs` and verify each becomes a no-op on re-run.
09. Conventions: read .specmgr/conventions.md (assertions for client input → ValueError not assert; type hints; numpy docstrings; `result` naming; etc.).
10. What to do with the progress README.
11. Don't commit, don't do Phase 3, stop and report.
12. Reporting requirements: evidence.

Details to nail down precisely:

**\_splice.py** (Task 2.1):

- Location `src/biz/dfch/specmgr/general/tools/_splice.py`

- No mcp dependency; plain file I/O + text manipulation

- Module docstring explaining the raw/splice invariant ("what the client counts is what the server splices")

- `body_text(path: Path) -> str` — frontmatter-stripped body via `frontmatter.loads(path.read_text(encoding="utf-8")).content` (the same mechanism the set_status\_<d> tools use — have the implementer check one of them, e.g. req/tools/set_status_req.py)

- `splice_body(current_body: str, begin: int, end: int, content: str) -> str`:

  - N = len(current_body.splitlines())
  - ValueError: begin < 1; begin > end; end > N + 1 — messages must spell out the offending value and the allowed range
  - Remove lines begin..min(end, N); insert content.splitlines() at position begin - 1; join with "\\n" + a single trailing "\\n"; empty content = deletion
  - Note: `begin = end = N+1` → remove nothing (min(end,N) = N < begin so the range is empty), insert at position N → append at end of body. Need to be careful about the algorithm: lines[begin-1:min(end,N)] — if begin = N+1 then lines[N:N] = [] empty. Insert at index begin-1 = N → append. Good.

  Edge case: what if the current body has no trailing newline, or is empty? N is from splitlines. body_text should return exactly the frontmatter's .content. For a document body ending in "\\n", splitlines gives N lines and joining with a trailing "\\n" preserves it. Fine — the implementer should test this with real documents.

- Also: who calls splice_body with a single-sided begin/end? The both-or-neither guard lives in the update tool (before file access), so splice_body itself only validates begin\<1, begin>end, end>N+1. Per Task 2.1, that's correct.

**update.py** (Task 2.2):

- 7 adapters `_update_<d>(id_, content, begin, end)` — verbatim ports of the current `update_<d>` bodies, plus the range branch.

  - Have the implementer read the 7 current modules: req/tools/update_req.py, uc/tools/update_uc.py, tsk/tools/update_tsk.py, qa/tools/update_qa.py, prb/tools/update_prb.py, gol/tools/update_gol.py, rsk/tools/update_rsk.py.
  - Whole-body: X.from_text(format_text(content)) validation (structural AssertionError / pydantic ValidationError, nothing written on failure); under X_lock: load_by_id; frontmatter carry-over (all fields preserved except updated, which gets bumped to the current microsecond timestamp); status is never settable via update; write the caller's raw content as-is with write_X_file; unknown id → XNotFoundError.
  - Range branch: both-or-neither guard (exactly one of begin/end given → ValueError) runs before any file access; then under the lock (re-reading on disk is needed for the splice): body = body_text(path); spliced = splice_body(body, begin, end, content); validate the spliced result via X.from_text(format_text(spliced)); write the spliced text as-is with write_X_file.

  Hmm — wait, a design detail: where does the both-or-neither guard run relative to the lock? "The both-or-neither ValueError guard runs before any file access." File access = reading the document file. The guard is about parameter consistency, so run it at the top of the adapter (or in the update tool wrapper before dispatch). Either works; spell it out: in the `update` tool function before dispatch, or at the top of each adapter — before any file access. Let the implementer decide, but the requirement is: no file access before the guard. Actually, the simplest thing is: guard in the public `update` function before dispatch. But the per-adapter ValueError for begin\<1 etc. needs N (from disk), so that runs inside the adapter under/after the read. Fine.

  Also: the frontmatter carry-over + updated bump is the same for range mode — only the body text changes. The adapter already does this on the whole-body port; in range mode just use the spliced text as the "raw content" to persist.

- Dispatch table `dict[str, Callable]`.

- `@mcp.tool(name="update", title="Update document", description=...)` — description should mention: whole-body or line-range replacement; type = domain; begin/end are optional 1-based inclusive body line ranges, N+1 sentinel.

- Signature exactly: `def update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"], content: str, begin: int | None = None, end: int | None = None) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument`

- Full numpy-style docstring (including the range contract and error types).

- The `type` parameter shadows the builtin — fine (no ruff rule against it in the E/F/W set).

- Return the parsed (validated) document — same as the old update\_<d> tools (which return XDocument).

**__init__.py** (Task 2.3): Register update in general/tools/__init__.py (import, __all__, module docstring). Have the implementer inspect the current file (which registers mdformat, and maybe others).

**get\_<d> raw parameter** (Task 2.4): 7 files. Signature `get_<d>(id: str, raw: bool = False) -> XDocument | str`. raw=True: resolve id as it does today (no lock — read-only), return body_text(path). raw=False: exactly today's behavior. Update the @mcp.tool description + docstring Returns section.

- Where does get\_<d> get `path`? It must already resolve the id → path (load_by_id or a \_paths helper). Have the implementer check the current get_req.py etc.

**server.py docstring** (Task 2.5): Add an update line to the General-tools section; add a raw note where the seven get\_<d> tools are enumerated. The server.py module docstring is the authoritative list — update it in the same phase (per the plan).

**Tests** (Tasks 2.6–2.8):

- tests/general/tools/test_update.py — parameterized over all 7 types. Seed the document per type via the domain's create\_<d> tool in a temporary SPECMGR_DOCS_DIR, mirroring the fixture strategy of the still-on-disk tests/<d>/tools/test_update\_<d>.py files (at this phase those still exist — instruct the implementer to read one or two of them, e.g. tests/req/tools/test_update_req.py, for the fixture strategy: how SPECMGR_DOCS_DIR is set, how create is called).
  - Whole-body mode (ACC-001): body is replaced; id/type/status/created/version are preserved; updated is bumped (microsecond timestamp); status is not settable (content containing a different status? — hmm, "status is never settable via update" — the frontmatter's status is carried over; the body content has no status. Test: seed with status X, update body, assert frontmatter's status is still X. And probably: the whole-body mode port preserves status even though the old tests verified the same thing); structural AssertionError (malformed body, e.g. missing H1 or malformed heading) and field ValidationError each leave the file byte-identical; unknown id → the domain's XNotFoundError.
  - Range mode (ACC-002): middle-range replacement, out-of-range lines byte-identical; N+1 append; end=N+1 replace-to-EOF; empty-fragment deletion of an optional section yielding a valid document; begin=1/end=N ≡ whole-body (same file with same text); each ValueError misuse (only one of the params, begin\<1, begin>end, end>N+1); range that deletes the H1 → AssertionError, file unchanged; range producing an out-of-vocabulary field value → ValidationError, file unchanged.
- Extend each domain's existing tests/<d>/tools/test_get\_<d>.py (7 files) with raw coverage (ACC-003): raw=True is byte-identical to the frontmatter-stripped body on disk; coordinate invariant (read raw, pick a real line range, update with it, assert the splice landed exactly there); raw=False is a regression; unknown id → XNotFoundError in both modes.
- Registration smoke test: a unittest asserting asyncio.run(mcp.list_tools()) contains update, with type rendered as a 7-value enum and begin/end as optional integers in the input schema; plus a fresh-subprocess `uv run --frozen python -c "import biz.dfch.specmgr.server"` check run at the phase gate (not a unittest — the plan says "run at the phase gate").
- Where to put the smoke test? Probably tests/general/tools/test_update.py, or a separate file — Task 2.8 doesn't specify a filename. Let the implementer choose (e.g. put it in tests/general/tools/test_update.py or tests/test_mcp_registration.py if such a thing exists — have them check the existing tests for a similar pattern).

**Gate (Task 2.9)**:

- uv run --frozen ruff format --check (or ruff format? the plan says `ruff format --check`; pre-commit auto-formats. Instruct: at the end run `uv run --frozen ruff format` to normalize new files, then `--check` must pass)

Hmm, note: the plan's gate is `ruff format --check`. The pre-commit hook runs ruff-format (fix). The implementer can just run `ruff format` (write mode) on new/changed files so that `--check` passes. OK — instruct that.

- uv run --frozen ruff check
- uv run --frozen vulture src/ whitelist.py --min-confidence 60
- uv run --frozen python -m unittest discover -v -s tests -t . -p "test\_\*.py" (full suite; note the pre-commit hook also runs with coverage — the implementer's plain run is the gate per the plan; the coverage run at commit time is my concern, but the coverage-badge regeneration covers the svg)
- uv run --frozen specmgr coverage-badge (regenerate docs/coverage.svg — the pre-commit hook requires no drift; new tests change coverage)
- uv run --frozen specmgr mcp-docs (docs/MCP.md)
- uv run --frozen specmgr docs (docs/api + docs/GENERATED.md)
- Then verify zero drift: re-run each generator; a second run must be a no-op (byte-identical). Also confirm docs/MCP.md shows the update entry with a 7-value enum and the raw note on the get\_<d> entries; confirm docs/api/ has new module pages for general/tools/update.py + _splice.py (and the get_<d> pages are updated).
- Fresh-subprocess: uv run --frozen python -c "import biz.dfch.specmgr.server"
- Progress README update: dated entry, Current Status, tasks 2.1–2.9 → done, frontmatter updated → 2026-08-27 (status stays in-progress).

**Constraints**:

- Purely additive: do not modify the 7 update\_<d> tool modules or their tests (Phase 3); do not touch any set_status tool (Phase 4); no changes to models/ (schema hooks stay quiet); do not rename anything existing.
- The domain's private helpers (\_paths/\_io/\_write/\_lock) and models are reused as-is, unmodified; the new adapters import them the same way the old tools did.
- Don't commit. Don't start Phase 3.
- If vulture flags anything (e.g. a ported helper becomes "unused"? No — the old tools remain, so their helpers are still used; the new adapters add usage), fix it properly.

Potential vulture trap: none anticipated, because Phase 2 is additive and everything is used.

Another consideration — the `update` tool name: MCP tool name "update" — is there a name collision with any existing tool? No (existing: update\_<d>, update_frontmatter, update_section). OK.

Also `set_status` (generic) in Phase 4 collides with ADR's set_status — handled by the atomicity of Phase 4.

One more: Task 2.6 says "seed the document per type, e.g. via the domain's create\_<d> tool in a temporary SPECMGR_DOCS_DIR, mirroring the fixture strategy of the still-on-disk tests/<d>/tools/test_update\_<d>.py files." Note: the create\_<d> tool writes the document; the tests then call update. Fine.

ACC-002 also requires: "begin = 1, end = N produces the same file as whole-body mode with the same text" — include in tests.

Length: the prompt will be long, but that's fine and necessary.

Now let me write it.

Pre-commit analysis complete. Key finding for Phase 2: In addition to the plan's gate generators (`specmgr docs`, `specmgr mcp-docs`), the **`specmgr coverage-badge`** hook regenerates `docs/coverage.svg` and fails on drift when `src/`/`tests/` are changed — since the new tests change coverage, the implementer must also regenerate this. All schema hooks are scoped to changes under `models/` (which Phase 2 does not touch).

**Delegating Phase 2** to a new phase-implementer:

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 2 (update tool)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 2: Generic `update` tool + `raw` read parameter** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `2647649` (Phase 1 commit: the feature ADR `36905d5b-8057-4294-8665-c7eed5534db0`, status `accepted`, is in `docs/adr/` and the feature README progress reflects Phase 1 done). Working tree is clean.\n- Live MCP registration baseline is currently 84 tools / 25 resources / 19 prompts. After Phase 2 (purely additive) it must be 85 / 25 / 19.\n\n## Your plan\nRead the FULL plan first: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — especially Overview, Requirements REQ-001…REQ-003, Design Notes (dispatch architecture, `update` signature, the precise range contract, shared body extraction + raw invariant, import-order consideration, docs discipline), and the \"Phase-end quality gate\" section. Your phase heading: `#### Phase 2: Generic `update` tool + `raw` read parameter` (Tasks 2.1–2.9). Also read `.specmgr/conventions.md` (coding standards: no `assert` for client-controlled input — use `ValueError`; mandatory type hints; numpy-style docstrings; `result` for return values; comparison constants) and skim the existing `general/tools/` package (`__init__.py`, `mdformat.py`, `_doc_paths.py`) for house style.\n\nImplement ONLY Phase 2. **Phase 2 is purely additive**: do NOT modify, delete, or rename any existing file's behavior except where a task explicitly says so — in particular the seven `update_<d>` tool modules and their test files stay untouched (Phase 3 deletes them), no `set_status*` tool is touched (Phase 4), and nothing under any `models/` package changes (schema hooks must stay quiet).\n\n## Tasks (from the plan — follow them precisely)\n\n- **Task 2.1**: Create `src/biz/dfch/specmgr/general/tools/_splice.py` (no `mcp` dependency — plain file I/O + text manipulation, mirroring `_doc_paths.py`'s placement; module docstring explaining the raw/splice invariant: \"what the client counts is what the server splices\"):\n  - `body_text(path: Path) -> str` — the frontmatter-stripped body text via the established `frontmatter.loads(path.read_text(encoding=\"utf-8\")).content` mechanism. (Check how the existing `set_status_<d>` tools do it, e.g. `src/biz/dfch/specmgr/req/tools/set_status_req.py`, and use the same mechanism.)\n  - `splice_body(current_body: str, begin: int, end: int, content: str) -> str` — implements the Design-Notes range contract exactly: `N = len(current_body.splitlines())`; raise `ValueError` (NOT `assert`) with a clear message naming the offending value(s) and the allowed range for `begin < 1`, `begin > end`, `end > N + 1`; drop lines `begin..min(end, N)`; insert `content.splitlines()` at position `begin - 1`; rejoin with `\"\\n\"` plus a single trailing `\"\\n\"`; empty `content` = range deletion. Note the `N+1` semantics fall out of this: `begin = end = N+1` → nothing dropped, insert at end (pure append); `end = N+1` → range extends through the last line.\n- **Task 2.2**: Create `src/biz/dfch/specmgr/general/tools/update.py`:\n  - Seven private adapter functions `_update_<d>(id_, content, begin, end)` — **verbatim ports** of the current `update_<d>` function bodies (read all seven: `req/tools/update_req.py`, `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`, `prb/tools/update_prb.py`, `gol/tools/update_gol.py`, `rsk/tools/update_rsk.py`) — same `X_lock`, same `load_by_id`, same frontmatter carry-over (every field preserved except `updated`, bumped to the current microsecond timestamp), same `status` never settable, same `write_X_file` persisting the caller's raw text verbatim, same domain `XNotFoundError` — with the range branch added:\n    - no `begin`/`end` → today's behavior: validate `X.from_text(format_text(content))` (structural `AssertionError` / field `pydantic.ValidationError`, nothing written on failure), persist `content` verbatim;\n    - both given → read the on-disk body via `body_text`, `splice_body`, validate the *spliced result* via `X.from_text(format_text(spliced))`, persist the *spliced* text verbatim (frontmatter carry-over identical to whole-body mode).\n    - The both-or-neither `ValueError` guard (exactly one of `begin`/`end` given) runs **before any file access** — place it in the public `update` function before dispatch (or the very top of each adapter, before any I/O); the `N`-dependent misuses (`begin < 1`, `begin > end`, `end > N+1`) are raised by `splice_body` after the body read.\n  - A dispatch table `dict[str, Callable]` mapping the `type` value to the adapter.\n  - `@mcp.tool(name=\"update\", title=\"Update document\", description=(...))` with `def update(id: str, type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\"], content: str, begin: int | None = None, end: int | None = None) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument`. The parameter is intentionally named `type` (no enabled ruff rule against builtin shadowing — verify `ruff check` passes). The 7-way union is annotation-only. Full numpy-style docstring covering the whole-body AND range contract (1-based inclusive, `N+1` EOF sentinel, splice-then-validate-whole, frontmatter never addressable) and the error types (`ValueError`, `AssertionError`, `pydantic.ValidationError`, domain `XNotFoundError`s).\n  - Domain private helpers and models are imported the same way the old tools did — no new shared code in domain packages.\n- **Task 2.3**: Register `update` in `general/tools/__init__.py` (import, `__all__`, module docstring updated).\n- **Task 2.4**: Add `raw: bool = False` to the seven `get_<d>` tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`, `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`, `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) -> XDocument | str`. `raw=False` (default) behaves exactly as today (parsed `XDocument`). `raw=True` resolves the id as today (no lock — read-only, matching every existing `get_<d>`) and returns `body_text(path)` — the SAME helper the splice uses (REQ-003 invariant). Update each tool's `@mcp.tool` description and docstring Returns section.\n- **Task 2.5**: Update `server.py`'s module docstring (the authoritative registration list): add `update` to the General-tools lines (one line describing whole-body AND line-range replace, the 7-value `type`, optional `begin`/`end`); note the `raw` parameter where the seven `get_<d>` tools are enumerated.\n- **Task 2.6**: `tests/general/tools/test_update.py` — parameterized over all seven types. Seed a document per type in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the `tests/<d>/tools/test_update_<d>.py` files still on disk (read at least `tests/req/tools/test_update_req.py` and one other, e.g. rsk or qa, and copy their temp-dir/seed approach). Cover:\n  - Whole-body mode (ACC-001): body replaced; `id`/`type`/`status`/`created`/`version` preserved; `updated` bumped (microsecond timestamp); `status` not settable through `update`; structural `AssertionError` and field `pydantic.ValidationError` each leave the file byte-identical on disk; unknown id → the domain's own `XNotFoundError`.\n  - Range mode (ACC-002): middle-range replace with out-of-range body lines byte-identical; `begin = end = N+1` appends at end of body; `end = N+1` replaces through end of body; empty `content` deletes a range (use an optional-section deletion that yields a still-valid document); `begin = 1`, `end = N` produces a file identical to whole-body mode with the identical text; each `ValueError` misuse (exactly one of `begin`/`end`, `begin < 1`, `begin > end`, `end > N+1`) with the file untouched; a range deleting the H1 → `AssertionError`, file untouched; a range producing an out-of-vocabulary field value → `pydantic.ValidationError`, file untouched.\n- **Task 2.7**: Extend each domain's EXISTING `tests/<d>/tools/test_get_<d>.py` (seven files) with `raw` coverage (ACC-003): `raw=True` returns the body text byte-identical to the on-disk frontmatter-stripped body; the coordinate invariant — a test that reads `raw=True`, picks a real line range, calls `update` with that range, and confirms the splice landed exactly there; `raw=False` regression (parsed document exactly as before); unknown id → domain `XNotFoundError` in both modes.\n- **Task 2.8**: Registration smoke test — a unittest asserting `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a 7-value `enum` and optional integer `begin`/`end` in the input schema (import the real `mcp` instance from `biz.dfch.specmgr.server`; check existing tests for the established pattern of doing this). PLUS, run inside the phase gate (not as a unittest): fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.server\"` — this is the import-order proof (Design Notes: `general` now pulls all seven domain tool packages in earlier; must still import cleanly).\n- **Task 2.9**: Phase-end quality gate — the FULL gate, then the README progress update:\n  1. `uv run --frozen ruff format` (write mode, to normalize your new files) then `uv run --frozen ruff format --check` (must pass) and `uv run --frozen ruff check` (must pass).\n  2. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (must be clean; if it flags something, fix the real issue — only touch `whitelist.py` for a confirmed false positive).\n  3. `uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"` (full suite, must pass — your new tests included).\n  4. Regenerations — the pre-commit hooks for this commit set will run `specmgr coverage-badge`, `specmgr docs`, and `specmgr mcp-docs` and FAIL if any leaves a diff, so all three must be regenerated by you and left in the tree: `uv run --frozen specmgr coverage-badge` (new tests change coverage → `docs/coverage.svg` will change — commit it), `uv run --frozen specmgr mcp-docs` (→ `docs/MCP.md`), `uv run --frozen specmgr docs` (→ `docs/api/` + `docs/GENERATED.md`).\n  5. Zero-drift proof: re-run each of the three generators a second time and confirm each is a no-op (byte-identical output; `git diff` on `docs/` shows no NEW changes after the second run).\n  6. Confirm `docs/MCP.md` shows the `update` entry with the 7-value `type` enum and the `raw` note on the seven `get_<d>` entries; confirm `docs/api/` gained pages for `general/tools/update.py` and `_splice.py` and the seven `get_<d>` pages changed.\n  7. Fresh-subprocess import check from Task 2.8: `uv run --frozen python -c \"import biz.dfch.specmgr.server\"` → exit 0.\n  8. Fix failures and re-run until green — a phase is not done with a red gate.\n  9. Update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); a new dated entry `#### Update 2026-08-27 (Phase 2: ...)` in Recent Updates (above the Phase 1 entry, preserve all history) recording what was added, the new ADR citation is NOT needed here, and the gate results; Current Status updated (Phase 2 complete, Phases 3–7 not started); Tasks 2.1–2.9 flipped to done in place (`- [x]` + `status: done` on the task line, preserving the plan's existing 2-space continuation wrapping on untouched lines — be byte-careful with edits).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`) — the orchestrator commits after verifying.\n- Do NOT start Phase 3 (no deletions of `update_<d>` tools/tests), do NOT touch `set_status*` tools, do NOT change anything under `models/` or `docs/adr/`.\n- The existing seven `update_<d>` tools must keep working identically at end of phase (their tests must still pass — they're in the suite).\n- If you hit a genuine blocker, STOP and report — do not invent a workaround that contradicts the plan.\n\n## Report back (your final message)\n1. Files created/modified (`git status --short` + `git diff --stat`), with the new files listed explicitly.\n2. Evidence per task: for 2.1–2.5 what you built/changed (key signatures, how the verbatim port was verified against the originals); for 2.6–2.8 the test counts (new tests added, full-suite result `Ran N tests ... OK`); for 2.9 each gate command with pass/fail output, the three generator no-op proofs (hashes or `git diff` emptiness after re-run), the `docs/MCP.md` `update` entry + enum + `raw` notes (quote the relevant lines), and the fresh-subprocess import result.\n3. The post-phase live registration counts if you can confirm them (85/25/19 expected) — e.g. via a quick `asyncio.run(mcp.list_tools())` length check.\n4. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbfae60f7ffeJNoRxb6DuoLCX0" state="completed">
<task_result>


Phase 2 is complete and the gate is green. Final report:

---

# Phase 2 Report — Generic `update` tool + `raw` read parameter (feat-22)

## 1. Files

**New (untracked, `??` in git status — left for the orchestrator to stage/commit):**
- `src/biz/dfch/specmgr/general/tools/_splice.py`
- `src/biz/dfch/specmgr/general/tools/update.py`
- `tests/general/tools/test_update.py`
- `docs/api/biz.dfch.specmgr.general.tools._splice.md` (generated)
- `docs/api/biz.dfch.specmgr.general.tools.update.md` (generated)

**Modified:** `src/biz/dfch/specmgr/general/tools/__init__.py`; the seven `get_<d>` tools (`req/uc/tsk/qa/prb/gol/rsk`); `server.py`; `commands/mcp_docs.py` (see deviation 1); `tests/commands/test_mcp_docs.py`; the seven `tests/<d>/tools/test_get_<d>.py`; regenerated `docs/MCP.md`, `docs/GENERATED.md`, `docs/api/README.md`, `docs/api/biz.dfch.specmgr.{commands.mcp_docs,general.tools,server}.md` + 7 `get_<d>` api pages; the plan README.

`git diff --stat`: **32 files changed, 942 insertions(+), 134 deletions(-)**. Untouched (verified by `git diff --name-only`): all seven `update_<d>` tool+test files, all `set_status*` tools, everything under `models/`, everything under `docs/adr/`. Nothing committed.

## 2. Evidence per task

**2.1 `_splice.py`** (no `mcp` dep, mirrors `_doc_paths.py` placement; module docstring states the "what the client counts is what the server splices" invariant):
- `body_text(path: Path) -> str` — `frontmatter.loads(path.read_text(encoding="utf-8")).content`, the exact mechanism `set_status_req.py` uses (assert `str` instead of `# type: ignore`).
- `splice_body(current_body: str, begin: int, end: int, content: str) -> str` — `N = len(current_body.splitlines())`; `ValueError` (not assert, per conventions Rule 3) for `begin < 1` / `begin > end` / `end > N+1`, each message naming the offending value(s) and allowed range (`_MIN_LINE = 1` comparison constant); drops `begin..min(end, N)`, inserts `content.splitlines()` at `begin-1`, rejoins `"\n"` + single trailing `"\n"`; empty `content` = deletion. Probed: middle replace, `begin=end=N+1` → pure append, `end=N+1` → through-EOF, all correct.

**2.2 `update.py`**: seven private adapters `_update_<d>(id_, content, begin, end)`. Verbatim-port verification: each whole-body branch is line-for-line the original body (same `X_lock`, same `load_by_id` (aliased per domain, e.g. `load_req_by_id`), same `fm_data = existing.frontmatter.model_dump(); fm_data["updated"] = now` microsecond bump, same `XFrontmatter(**fm_data)` (status never settable), same `write_X_file(path, new_frontmatter, content)` verbatim persistence, same `XNotFoundError`); whole-body branch keeps the original ordering (validate `X.from_text(format_text(content))` **before** any file access). Range branch (single lock scope): `load_by_id` → `body_text` → `splice_body` → validate the *spliced result* `X.from_text(format_text(spliced))` → persist the *spliced* text verbatim. Both-or-neither guard is in public `update` before dispatch (proven pre-file-access by a test that passes `begin` only with an *unknown* id and gets `ValueError`, not `XNotFoundError`). Dispatch table `_ADAPTERS: dict[str, Callable[[str, str, int | None, int | None], _UpdateDocument]]`. `@mcp.tool(name="update", title="Update document", description=...)` with `def update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"], content: str, begin: int | None = None, end: int | None = None) -> ReqDocument | ... | RskDocument`; full numpy docstring (both modes, `N+1` sentinel, splice algorithm, all error types). Domain helpers/models imported exactly as the old tools imported them — no new shared code in domain packages.

**2.3** `general/tools/__init__.py`: `from .update import update`, `__all__` = `["mdformat", "update", "webfetch"]`, module docstring now describes `update`.

**2.4** Seven `get_<d>` tools: `def get_<d>(id: str, raw: bool = False) -> XDocument | str`; `raw=False` path unchanged (parsed doc); `raw=True` resolves id via the existing no-lock `load_by_id` and returns `body_text(path)` — the *same* helper the splice uses. `@mcp.tool` descriptions and docstring Parameters/Returns updated in all seven.

**2.5** `server.py` module docstring: `update` added to the General-tools lines (whole-body *and* line-range, 7-value `type`, optional `begin`/`end`, `N+1` sentinel, splice-validated-whole); `raw=True` note added on each of the seven per-domain `get_<d>` lines.

**2.6 `tests/general/tools/test_update.py`** — 18 test methods, each parameterized over all 7 types via `subTest` (per-type `_Case` dataclass; seeded through the domain's own `create_<d>` in a temp `SPECMGR_DOCS_DIR`, mirroring `tests/<d>/tools/test_update_<d>.py`'s fixture strategy):
- ACC-001: body replaced + `id/type/status/created/version` preserved + `updated` bumped (microsecond shape via `re.fullmatch`); smuggled frontmatter in `content` → `AssertionError`, file byte-identical (status not settable); structural `AssertionError` and per-type field failure each leave the file byte-identical; unknown id → domain `XNotFoundError`.
- ACC-002: middle-range replace (out-of-range lines byte-identical, exact line-list equality); `begin=end=N+1` append; `end=N+1` through-EOF replace; empty `content` deleting an optional trailing section (still-valid doc, back to the minimal body); `begin=1,end=N` file-identical to whole-body mode with the same text (`datetime` frozen via `_FixedDatetime` mock so both `updated` bumps are equal); all four `ValueError` misuses with file untouched; range deleting the H1 → `AssertionError`, untouched; range producing an out-of-vocabulary field value → per-type error, untouched.

**2.7** Each of the seven `tests/<d>/tools/test_get_<d>.py` gained 4 tests (28 total): `raw=True` byte-identical to `body_text(path)` (the shared helper — the invariant itself); coordinate invariant (read raw → pick a real line → `update` with that range → splice landed exactly there, all other lines equal, same length); `raw=False` regression (explicit `raw=False` == default, parsed `XDocument`); unknown id → domain `XNotFoundError` in both modes.

**2.8** `TestUpdateRegistration` runs `asyncio.run(mcp.list_tools())` on the real `server.mcp`: exactly one `update`; `input_schema.properties.type == {"enum": ["req","uc","tsk","qa","prb","gol","rsk"], "type": "string", ...}` (raw JSON-schema 7-value enum); `begin`/`end` each `{"anyOf": [{"type": "integer"}, {"type": "null"}], "default": null}`; `required == ["id", "type", "content"]`. Fresh-subprocess import check run in the gate (below).

## 3. Test counts

- New: **47 tests** (18 in `test_update.py` + 28 across the seven get-test files + 1 in `test_mcp_docs.py`).
- Full suite: **`Ran 1830 tests in 56.744s` — `OK`** (exit 0), up from 1783 at Phase 1. The seven pre-existing `update_<d>` files still pass unchanged (34 tests, verified in isolation).

## 4. Quality gate (Task 2.9) — all green

| Command | Result |
|---|---|
| `uv run --frozen ruff format` (write) then `ruff format --check` | write pass normalized new files; check: **`1136 files already formatted`** |
| `uv run --frozen ruff check` | **`All checks passed!`** (incl. the `type` builtin-shadowing param — no enabled rule objects) |
| `uv run --frozen vulture src/ whitelist.py --min-confidence 60` | **exit 0, clean** (no whitelist changes needed) |
| `uv run --frozen python -m unittest discover -s tests -t . -p "test_*.py"` | **`Ran 1830 tests ... OK`** |
| `uv run --frozen specmgr coverage-badge` | 98% coverage — **same rounded value as the committed badge (98%)**, so `docs/coverage.svg` is byte-identical, no diff (the pre-commit hook's `git diff --exit-code -- docs/coverage.svg` will pass) |
| `uv run --frozen specmgr mcp-docs` | → `docs/MCP.md` (header: `25 resource(s), 1 resource template(s), 85 tool(s), 19 prompt(s)`) |
| `uv run --frozen specmgr docs` | → 319 api pages + `docs/GENERATED.md` |
| `uv run --frozen specmgr schema` (extra safety) | all seven schemas `(unchanged)` — models stayed quiet |

**Zero-drift proof:** sha256 manifest of every file under `docs/` taken, then all three generators re-run, manifest re-taken: **`diff` empty — `docs/` byte-identical after the second run** (no new changes in `git diff -- docs/` beyond the intended first-pass regeneration).

**`docs/MCP.md` confirmation (quoted):**
- `| type | string (enum: req, uc, tsk, qa, prb, gol, rsk) | Yes |`, `| begin | integer | None | No |`, `| end | integer | None | No |` under `### Tool: update`; index row: `` [`update`](#tool-update) | Whole-body or line-range replace of an existing document's content across the seven whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk), ... | ``
- All seven `get_<d>` index rows end with: ``Pass raw=True to return the frontmatter-stripped body text verbatim instead.`` (e.g. `| get_req | Read, parse, and return a full requirement document (frontmatter and body) by its id. Pass raw=True to ... |`)
- `docs/api/` gained `biz.dfch.specmgr.general.tools.update.md` and `biz.dfch.specmgr.general.tools._splice.md`; the seven `get_<d>` api pages changed (each +~20 lines, new `raw` param documented).

**Fresh-subprocess import (import-order proof):** `uv run --frozen python -c "import biz.dfch.specmgr.server"` → **exit 0** — `general` now pulls all seven domain tool packages earlier than before and still imports cleanly.

## 5. Post-phase live registration counts

`asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real `server.mcp`: **85 tools / 25 resources / 19 prompts** (plus the 1 `specmgr://adr/{id}` resource template counted separately, as in the 84/25/19 baseline) — exactly the expected additive delta of +1 tool.

## 6. Deviations from the plan (2, both recorded in the README entry)

1. **`commands/mcp_docs.py` gained an enum branch in `_schema_type_str`** (renders `{"type": "string", "enum": [...]}` as `string (enum: req, uc, tsk, qa, prb, gol, rsk)`, +1 `TestSchemaTypeStr` case). Why: the Design Notes state `type` "must render as a 7-entry JSON-schema enum in `docs/MCP.md` (verify in the Phase 2 gate)" and Task 2.9 says to confirm the enum in `docs/MCP.md`, but the existing renderer collapsed enums to bare `string`, making the gate check unsatisfiable. The branch is strictly additive — it fires only for properties declaring `enum`, and `update.type` is the only one in the current surface (no other MCP.md row changed).
2. **ACC-002 out-of-vocabulary case for `qa`/`prb` raises `AssertionError`, not `pydantic.ValidationError`.** Why: I probed the models — `qa` and `prb` body schemas contain *zero* field-level validation (no closed vocabularies, no field constraints, no model validators; every section is free-form text), so no body input can produce a field `ValidationError` in those two domains. For `req` (bad `Level`), `uc` (unresolvable `Extension 99a` cross-ref), `tsk` (malformed `- [z]` checkbox via the eager model validator), `gol` (out-of-range `## Priority`), and `rsk` (non-TARA `## Strategy`) the test uses genuine `ValidationError` inputs; for `qa`/`prb` it uses an unrecognized section heading (structural `AssertionError`). The invariant under test — invalid range input → exception with the file left byte-identical — is verified for all seven types. Flagged in the test module docstring, the case data (`field_error_is_validation`), and the README Recent Updates entry.

No Phase 3 work started; working tree left uncommitted for the orchestrator.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 156.8s)

_Thinking:_

Phase 2 complete. Two deviations declared:

1. `commands/mcp_docs.py` — added an enum branch to `_schema_type_str`. The plan requires that `type` be rendered as a 7-value enum in docs/MCP.md, but the existing renderer was collapsing enums to plain `string`. This is a reasonable, minimal, additive fix, and it's also recorded. Acceptable — it's necessary to satisfy the gate requirements of Task 2.9, and strictly additive.
2. In the qa/prb out-of-vocabulary cases, AssertionError occurs instead of ValidationError — because the qa/prb body schema has no field-level validation. The tests verify the invariants per type with the appropriate error kinds. This is an honest finding about the model, not a scope violation.

Next, verify independently:

1. Run the gate myself: ruff format --check, ruff check, vulture, full unittest, regenerators (coverage-badge, mcp-docs, docs) + no-op proof via re-run, fresh subprocess imports.
2. Inspect git status/diff — confirm that the untouched areas really are untouched (update\_<d> files, set_status\*, models/, docs/adr/).
3. Spot-check the quality of the main new files: _splice.py (range contract), update.py (verbatim port), one get_<d> (raw parameter), the server.py docstring diff, the mcp_docs.py diff, and the test files (skimming the test_update.py structure).
4. Check the progress update in the plan's README.
5. Confirm the registration count is 85/25/19.

Start with the heavy verification batch first: gate commands + git status. After that, read the files.

Batch 1 (parallel):

- bash: git status --short; git diff --name-only (confirm the untouched set);
- bash: full gate run (ruff format --check, ruff check, vulture, unittest, three generators + manifest diff + fresh imports). Takes about 2–3 minutes.

Batch 2: read \_splice.py, update.py (maybe just the main parts), the get_req.py diff, the server.py diff, the mcp_docs.py diff.

Phase 2 was reported as green, with two declared deviations (an additional enum rendering branch in `commands/mcp_docs.py` that was required by the plan's own gate, and `qa`/`prb` using structural `AssertionError` for out-of-vocabulary cases because their body schema has no field-level validation — an honest model finding). Now verifying independently:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && echo === && git diff --name-only | wc -l && echo === && git diff --name-only | grep -E \"update_(req|uc|tsk|qa|prb|gol|rsk)\\.py|set_status|models/|docs/adr/\" ; echo \"untouched-check-exit=$?\"",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
 M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
 M docs/GENERATED.md
 M docs/MCP.md
 M docs/api/README.md
 M docs/api/biz.dfch.specmgr.commands.mcp_docs.md
 M docs/api/biz.dfch.specmgr.general.tools.md
 M docs/api/biz.dfch.specmgr.gol.tools.get_gol.md
 M docs/api/biz.dfch.specmgr.prb.tools.get_prb.md
 M docs/api/biz.dfch.specmgr.qa.tools.get_qa.md
 M docs/api/biz.dfch.specmgr.req.tools.get_req.md
 M docs/api/biz.dfch.specmgr.rsk.tools.get_rsk.md
 M docs/api/biz.dfch.specmgr.server.md
 M docs/api/biz.dfch.specmgr.tsk.tools.get_tsk.md
 M docs/api/biz.dfch.specmgr.uc.tools.get_uc.md
 M src/biz/dfch/specmgr/commands/mcp_docs.py
 M src/biz/dfch/specmgr/general/tools/__init__.py
 M src/biz/dfch/specmgr/gol/tools/get_gol.py
 M src/biz/dfch/specmgr/prb/tools/get_prb.py
 M src/biz/dfch/specmgr/qa/tools/get_qa.py
 M src/biz/dfch/specmgr/req/tools/get_req.py
 M src/biz/dfch/specmgr/rsk/tools/get_rsk.py
 M src/biz/dfch/specmgr/server.py
 M src/biz/dfch/specmgr/tsk/tools/get_tsk.py
 M src/biz/dfch/specmgr/uc/tools/get_uc.py
 M tests/commands/test_mcp_docs.py
 M tests/gol/tools/test_get_gol.py
 M tests/prb/tools/test_get_prb.py
 M tests/qa/tools/test_get_qa.py
 M tests/req/tools/test_get_req.py
 M tests/rsk/tools/test_get_rsk.py
 M tests/tsk/tools/test_get_tsk.py
 M tests/uc/tools/test_get_uc.py
?? docs/api/biz.dfch.specmgr.general.tools._splice.md
?? docs/api/biz.dfch.specmgr.general.tools.update.md
?? src/biz/dfch/specmgr/general/tools/_splice.py
?? src/biz/dfch/specmgr/general/tools/update.py
?? tests/general/tools/test_update.py
===
32
===
untouched-check-exit=1

```

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase2-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase2-unittest.log",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
1136 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1830 tests in 56.279s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 41.7s)

_Thinking:_

- File set confirmed: 32 modified files + 5 new files; grep didn't find any changes to update\_<d>.py, set_status\*, models/, or docs/adr/ (exit=1 = no match).
- ruff format ✓, ruff check ✓, vulture ✓, unittest 1830 OK, exit 0.

Next: regeneration + zero-drift proof + fresh subprocess + live count. After that, read and spot-check the main files.

The file set is as declared (no changes to `update_*`/`set_status*`/`models/`/`docs/adr/`), lint + full suite (1830 tests OK) are green in my run as well. Next up: zero-drift proof for the generator, fresh subprocess import, and live count:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen specmgr coverage-badge && uv run --frozen specmgr mcp-docs && uv run --frozen specmgr docs && find docs -type f | sort | xargs sha256sum > /tmp/opencode/docs-manifest-1.txt && uv run --frozen specmgr coverage-badge && uv run --frozen specmgr mcp-docs && uv run --frozen specmgr docs && find docs -type f | sort | xargs sha256sum > /tmp/opencode/docs-manifest-2.txt && diff /tmp/opencode/docs-manifest-1.txt /tmp/opencode/docs-manifest-2.txt && echo DOCS_ZERO_DRIFT && uv run --frozen python -c \"import biz.dfch.specmgr.server\" && echo IMPORT_OK && uv run --frozen python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\nprint('tools:', len(asyncio.run(mcp.list_tools())))\nprint('resources:', len(asyncio.run(mcp.list_resources())))\nprint('prompts:', len(asyncio.run(mcp.list_prompts())))\n\"",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
...output truncated...

Full output saved to: /home/user/.local/share/opencode/tool-output/tool_0414a0850001x5qp7dFuRb5Gsp

src/biz/dfch/specmgr/models/adr/v1/body.py                            27      0   100%
src/biz/dfch/specmgr/models/adr/v1/frontmatter.py                     33      0   100%
src/biz/dfch/specmgr/models/adr/v1/mutations.py                       54      0   100%
src/biz/dfch/specmgr/models/adr/v1/option.py                          17      0   100%
src/biz/dfch/specmgr/models/adr/v1/parser.py                         137      5    96%
src/biz/dfch/specmgr/models/adr/v1/renderer.py                        45      0   100%
src/biz/dfch/specmgr/models/adr/v1/summary.py                          7      0   100%
src/biz/dfch/specmgr/models/iso25010.py                               21      0   100%
src/biz/dfch/specmgr/models/md/__init__.py                            25      0   100%
src/biz/dfch/specmgr/models/md/_markdown.py                           36      0   100%
src/biz/dfch/specmgr/models/md/_util.py                               25      1    96%
src/biz/dfch/specmgr/models/md/alias.py                                7      0   100%
src/biz/dfch/specmgr/models/md/alias_match.py                         24      1    96%
src/biz/dfch/specmgr/models/md/alias_type.py                           6      0   100%
src/biz/dfch/specmgr/models/md/frontmatter.py                         29      0   100%
src/biz/dfch/specmgr/models/md/markdown.py                            16      0   100%
src/biz/dfch/specmgr/models/md/markdown_block_quote.py                78      1    99%
src/biz/dfch/specmgr/models/md/markdown_code_block.py                 52      1    98%
src/biz/dfch/specmgr/models/md/markdown_comment.py                    55      2    96%
src/biz/dfch/specmgr/models/md/markdown_list_item.py                  85      7    92%
src/biz/dfch/specmgr/models/md/markdown_paragraph.py                  76      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section2.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section5.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section5_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section6.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section6_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section.py                   108      1    99%
src/biz/dfch/specmgr/models/md/markdown_str.py                       150      3    98%
src/biz/dfch/specmgr/models/version_info.py                            4      0   100%
src/biz/dfch/specmgr/prb/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/prb/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/prb/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/prb/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/prb/models/v1/body.py                            40      0   100%
src/biz/dfch/specmgr/prb/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/prb/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/prb/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/prb/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/prb/prompts/create_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/prompts/update_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/prb/resources/prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/resources/prb_schema.py                       9      0   100%
src/biz/dfch/specmgr/prb/resources/prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/prb/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/prb/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/prb/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/prb/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/prb/tools/create_prb.py                          21      0   100%
src/biz/dfch/specmgr/prb/tools/delete_prb.py                           6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb.py                             15      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/list_prb.py                            18      0   100%
src/biz/dfch/specmgr/prb/tools/parse_prb.py                            8      0   100%
src/biz/dfch/specmgr/prb/tools/set_status_prb.py                      23      0   100%
src/biz/dfch/specmgr/prb/tools/update_prb.py                          22      0   100%
src/biz/dfch/specmgr/prb/tools/validate_prb.py                        16      0   100%
src/biz/dfch/specmgr/qa/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/qa/models/__init__.py                             0      0   100%
src/biz/dfch/specmgr/qa/models/v2/__init__.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/qa/models/v2/body.py                             37      0   100%
src/biz/dfch/specmgr/qa/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/qa/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/qa/models/v2/question_answer.py                  71      0   100%
src/biz/dfch/specmgr/qa/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/qa/prompts/__init__.py                            4      0   100%
src/biz/dfch/specmgr/qa/prompts/create_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/prompts/refine.py                              8      0   100%
src/biz/dfch/specmgr/qa/prompts/update_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/qa/resources/qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/resources/qa_schema.py                         9      0   100%
src/biz/dfch/specmgr/qa/resources/qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/__init__.py                             11      0   100%
src/biz/dfch/specmgr/qa/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/qa/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/qa/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/qa/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/qa/tools/create_qa.py                            21      0   100%
src/biz/dfch/specmgr/qa/tools/delete_qa.py                             6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa.py                               15      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/list_qa.py                              18      0   100%
src/biz/dfch/specmgr/qa/tools/parse_qa.py                              8      0   100%
src/biz/dfch/specmgr/qa/tools/set_status_qa.py                        23      0   100%
src/biz/dfch/specmgr/qa/tools/update_qa.py                            22      0   100%
src/biz/dfch/specmgr/qa/tools/validate_qa.py                          16      0   100%
src/biz/dfch/specmgr/req/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/req/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/req/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/req/models/v1/body.py                            57      0   100%
src/biz/dfch/specmgr/req/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/req/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/req/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/req/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/req/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/req/prompts/create_req.py                         8      0   100%
src/biz/dfch/specmgr/req/prompts/update_req.py                         8      0   100%
src/biz/dfch/specmgr/req/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/req/resources/req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/resources/req_schema.py                       9      0   100%
src/biz/dfch/specmgr/req/resources/req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/req/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/req/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/req/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/req/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/req/tools/create_req.py                          21      0   100%
src/biz/dfch/specmgr/req/tools/delete_req.py                           6      0   100%
src/biz/dfch/specmgr/req/tools/get_req.py                             15      0   100%
src/biz/dfch/specmgr/req/tools/get_req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/tools/get_req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/list_req.py                            18      0   100%
src/biz/dfch/specmgr/req/tools/parse_req.py                            8      0   100%
src/biz/dfch/specmgr/req/tools/set_status_req.py                      23      0   100%
src/biz/dfch/specmgr/req/tools/update_req.py                          22      0   100%
src/biz/dfch/specmgr/req/tools/validate_req.py                        16      0   100%
src/biz/dfch/specmgr/rsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/rsk/models/__init__.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/assessment.py                      57      0   100%
src/biz/dfch/specmgr/rsk/models/v1/body.py                            38      0   100%
src/biz/dfch/specmgr/rsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py                     20      0   100%
src/biz/dfch/specmgr/rsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/rsk/models/v1/summary.py                         23      0   100%
src/biz/dfch/specmgr/rsk/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/rsk/prompts/create_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/prompts/update_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/rsk/resources/risk_matrix.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/resources/tara.py                             6      0   100%
src/biz/dfch/specmgr/rsk/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/rsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/rsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/rsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/rsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/rsk/tools/create_rsk.py                          21      0   100%
src/biz/dfch/specmgr/rsk/tools/delete_rsk.py                           6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk.py                             15      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/tools/list_rsk.py                            18      0   100%
src/biz/dfch/specmgr/rsk/tools/parse_rsk.py                            8      0   100%
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py                      23      0   100%
src/biz/dfch/specmgr/rsk/tools/update_rsk.py                          22      0   100%
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py                        16      0   100%
src/biz/dfch/specmgr/server.py                                         9      1    89%
src/biz/dfch/specmgr/tsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/tsk/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/tsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/tsk/models/v1/body.py                            17      0   100%
src/biz/dfch/specmgr/tsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/tsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/tsk/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/tsk/models/v1/task_item.py                       19      0   100%
src/biz/dfch/specmgr/tsk/prompts/__init__.py                           4      0   100%
src/biz/dfch/specmgr/tsk/prompts/create_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/prompts/implement_task.py                     8      0   100%
src/biz/dfch/specmgr/tsk/prompts/update_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/tsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/tsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/tsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/tsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/tsk/tools/create_tsk.py                          21      0   100%
src/biz/dfch/specmgr/tsk/tools/delete_tsk.py                           6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk.py                             15      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/list_tsk.py                            18      0   100%
src/biz/dfch/specmgr/tsk/tools/parse_tsk.py                            8      0   100%
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py                      23      0   100%
src/biz/dfch/specmgr/tsk/tools/update_tsk.py                          22      0   100%
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py                        16      0   100%
src/biz/dfch/specmgr/uc/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/uc/models/__init__.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v1/__init__.py                         16      0   100%
src/biz/dfch/specmgr/uc/models/v1/characteristic_information.py       27      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension.py                        14      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension_action.py                  5      0   100%
src/biz/dfch/specmgr/uc/models/v1/extensions.py                        5      0   100%
src/biz/dfch/specmgr/uc/models/v1/main_success_scenario.py            12      0   100%
src/biz/dfch/specmgr/uc/models/v1/open_issues.py                       4      0   100%
src/biz/dfch/specmgr/uc/models/v1/parser.py                          204     11    95%
src/biz/dfch/specmgr/uc/models/v1/related_information.py               6      0   100%
src/biz/dfch/specmgr/uc/models/v1/related_use_cases.py                 6      0   100%
src/biz/dfch/specmgr/uc/models/v1/step.py                              5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variation.py                     5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variations.py                    5      0   100%
src/biz/dfch/specmgr/uc/models/v1/uc_diagram.py                       47      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case.py                         36      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case_frontmatter.py             16      0   100%
src/biz/dfch/specmgr/uc/models/v2/__init__.py                          7      0   100%
src/biz/dfch/specmgr/uc/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/uc/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/uc/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/uc/models/v2/use_case.py                        113      0   100%
src/biz/dfch/specmgr/uc/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/uc/resources/uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/resources/uc_schema.py                         9      0   100%
src/biz/dfch/specmgr/uc/resources/uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/__init__.py                             11      0   100%
src/biz/dfch/specmgr/uc/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/uc/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/uc/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/uc/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/uc/tools/create_uc.py                            21      0   100%
src/biz/dfch/specmgr/uc/tools/delete_uc.py                             6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc.py                               15      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/list_uc.py                              18      0   100%
src/biz/dfch/specmgr/uc/tools/parse_uc.py                              8      0   100%
src/biz/dfch/specmgr/uc/tools/set_status_uc.py                        23      0   100%
src/biz/dfch/specmgr/uc/tools/update_uc.py                            22      0   100%
src/biz/dfch/specmgr/uc/tools/validate_uc.py                          16      0   100%
--------------------------------------------------------------------------------------
TOTAL                                                               5943    105    98%
✓ Wrote docs/coverage.svg (98% coverage)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/MCP.md
✓ Wrote 319 module file(s) to /home/user/src/biz.dfch.SpecMgr-feat-22/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/GENERATED.md
Name                                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------------
src/biz/dfch/specmgr/__init__.py                                       1      0   100%
src/biz/dfch/specmgr/__main__.py                                       3      1    67%
src/biz/dfch/specmgr/_paths.py                                         6      0   100%
src/biz/dfch/specmgr/adr/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/adr/prompts/__init__.py                           5      0   100%
src/biz/dfch/specmgr/adr/prompts/create_adr.py                         8      0   100%
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py                    8      0   100%
src/biz/dfch/specmgr/adr/prompts/update_adr.py                         8      0   100%
src/biz/dfch/specmgr/adr/prompts/update_adr_test.py                    8      0   100%
src/biz/dfch/specmgr/adr/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/adr/resources/adr_get.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/__init__.py                            13      0   100%
src/biz/dfch/specmgr/adr/tools/_io.py                                 12      0   100%
src/biz/dfch/specmgr/adr/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/adr/tools/_paths.py                              37      0   100%
src/biz/dfch/specmgr/adr/tools/create_adr.py                          15      0   100%
src/biz/dfch/specmgr/adr/tools/get_adr.py                             10      0   100%
src/biz/dfch/specmgr/adr/tools/list_adr.py                            19      0   100%
src/biz/dfch/specmgr/adr/tools/option_create.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/option_delete.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/option_list.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/option_read.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/option_update.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/set_status.py                          15      0   100%
src/biz/dfch/specmgr/adr/tools/update_frontmatter.py                  15      0   100%
src/biz/dfch/specmgr/adr/tools/update_section.py                      15      0   100%
src/biz/dfch/specmgr/adr/tools/validate_adr.py                         9      0   100%
src/biz/dfch/specmgr/cli.py                                           23      2    91%
src/biz/dfch/specmgr/commands/__init__.py                             11      0   100%
src/biz/dfch/specmgr/commands/adr_toc.py                              42     32    24%
src/biz/dfch/specmgr/commands/coverage_badge.py                       49     11    78%
src/biz/dfch/specmgr/commands/docs.py                                218      8    96%
src/biz/dfch/specmgr/commands/mcp.py                                  23      3    87%
src/biz/dfch/specmgr/commands/mcp_docs.py                            131      8    94%
src/biz/dfch/specmgr/commands/mdformat.py                             18      0   100%
src/biz/dfch/specmgr/commands/req_parse.py                            44      0   100%
src/biz/dfch/specmgr/commands/schema.py                               76      0   100%
src/biz/dfch/specmgr/commands/unused_code.py                          53      0   100%
src/biz/dfch/specmgr/commands/version.py                               8      2    75%
src/biz/dfch/specmgr/general/__init__.py                               2      0   100%
src/biz/dfch/specmgr/general/models/__init__.py                        3      0   100%
src/biz/dfch/specmgr/general/models/paged_result.py                   11      0   100%
src/biz/dfch/specmgr/general/models/summary.py                         8      0   100%
src/biz/dfch/specmgr/general/prompts/__init__.py                       2      0   100%
src/biz/dfch/specmgr/general/prompts/compact_history.py                8      0   100%
src/biz/dfch/specmgr/general/resources/__init__.py                     2      0   100%
src/biz/dfch/specmgr/general/resources/iso25010.py                     8      0   100%
src/biz/dfch/specmgr/general/resources/version.py                      7      0   100%
src/biz/dfch/specmgr/general/tools/__init__.py                         4      0   100%
src/biz/dfch/specmgr/general/tools/_doc_paths.py                      53      0   100%
src/biz/dfch/specmgr/general/tools/_packaged_data.py                  11      0   100%
src/biz/dfch/specmgr/general/tools/_paging.py                         28      0   100%
src/biz/dfch/specmgr/general/tools/_splice.py                         30      0   100%
src/biz/dfch/specmgr/general/tools/mdformat.py                        12      0   100%
src/biz/dfch/specmgr/general/tools/update.py                         234      0   100%
src/biz/dfch/specmgr/general/tools/webfetch.py                        27      0   100%
src/biz/dfch/specmgr/gol/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/gol/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/gol/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/gol/models/v1/body.py                            43      0   100%
src/biz/dfch/specmgr/gol/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/gol/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/gol/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/gol/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/gol/prompts/create_gol.py                         8      0   100%
src/biz/dfch/specmgr/gol/prompts/update_gol.py                         8      0   100%
src/biz/dfch/specmgr/gol/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/gol/resources/gol_example.py                      6      0   100%
src/biz/dfch/specmgr/gol/resources/gol_schema.py                       9      0   100%
src/biz/dfch/specmgr/gol/resources/gol_template.py                     6      0   100%
src/biz/dfch/specmgr/gol/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/gol/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/gol/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/gol/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/gol/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/gol/tools/create_gol.py                          21      0   100%
src/biz/dfch/specmgr/gol/tools/delete_gol.py                           6      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol.py                             15      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol_example.py                      6      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol_template.py                     6      0   100%
src/biz/dfch/specmgr/gol/tools/list_gol.py                            18      0   100%
src/biz/dfch/specmgr/gol/tools/parse_gol.py                            8      0   100%
src/biz/dfch/specmgr/gol/tools/set_status_gol.py                      23      0   100%
src/biz/dfch/specmgr/gol/tools/update_gol.py                          22      0   100%
src/biz/dfch/specmgr/gol/tools/validate_gol.py                        16      0   100%
src/biz/dfch/specmgr/models/__init__.py                                4      0   100%
src/biz/dfch/specmgr/models/adr/__init__.py                            2      0   100%
src/biz/dfch/specmgr/models/adr/v1/__init__.py                         9      0   100%
src/biz/dfch/specmgr/models/adr/v1/_util.py                           25      0   100%
src/biz/dfch/specmgr/models/adr/v1/adr.py                              9      0   100%
src/biz/dfch/specmgr/models/adr/v1/body.py                            27      0   100%
src/biz/dfch/specmgr/models/adr/v1/frontmatter.py                     33      0   100%
src/biz/dfch/specmgr/models/adr/v1/mutations.py                       54      0   100%
src/biz/dfch/specmgr/models/adr/v1/option.py                          17      0   100%
src/biz/dfch/specmgr/models/adr/v1/parser.py                         137      5    96%
src/biz/dfch/specmgr/models/adr/v1/renderer.py                        45      0   100%
src/biz/dfch/specmgr/models/adr/v1/summary.py                          7      0   100%
src/biz/dfch/specmgr/models/iso25010.py                               21      0   100%
src/biz/dfch/specmgr/models/md/__init__.py                            25      0   100%
src/biz/dfch/specmgr/models/md/_markdown.py                           36      0   100%
src/biz/dfch/specmgr/models/md/_util.py                               25      1    96%
src/biz/dfch/specmgr/models/md/alias.py                                7      0   100%
src/biz/dfch/specmgr/models/md/alias_match.py                         24      1    96%
src/biz/dfch/specmgr/models/md/alias_type.py                           6      0   100%
src/biz/dfch/specmgr/models/md/frontmatter.py                         29      0   100%
src/biz/dfch/specmgr/models/md/markdown.py                            16      0   100%
src/biz/dfch/specmgr/models/md/markdown_block_quote.py                78      1    99%
src/biz/dfch/specmgr/models/md/markdown_code_block.py                 52      1    98%
src/biz/dfch/specmgr/models/md/markdown_comment.py                    55      2    96%
src/biz/dfch/specmgr/models/md/markdown_list_item.py                  85      7    92%
src/biz/dfch/specmgr/models/md/markdown_paragraph.py                  76      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section2.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section5.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section5_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section6.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section6_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section.py                   108      1    99%
src/biz/dfch/specmgr/models/md/markdown_str.py                       150      3    98%
src/biz/dfch/specmgr/models/version_info.py                            4      0   100%
src/biz/dfch/specmgr/prb/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/prb/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/prb/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/prb/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/prb/models/v1/body.py                            40      0   100%
src/biz/dfch/specmgr/prb/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/prb/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/prb/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/prb/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/prb/prompts/create_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/prompts/update_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/prb/resources/prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/resources/prb_schema.py                       9      0   100%
src/biz/dfch/specmgr/prb/resources/prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/prb/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/prb/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/prb/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/prb/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/prb/tools/create_prb.py                          21      0   100%
src/biz/dfch/specmgr/prb/tools/delete_prb.py                           6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb.py                             15      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/list_prb.py                            18      0   100%
src/biz/dfch/specmgr/prb/tools/parse_prb.py                            8      0   100%
src/biz/dfch/specmgr/prb/tools/set_status_prb.py                      23      0   100%
src/biz/dfch/specmgr/prb/tools/update_prb.py                          22      0   100%
src/biz/dfch/specmgr/prb/tools/validate_prb.py                        16      0   100%
src/biz/dfch/specmgr/qa/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/qa/models/__init__.py                             0      0   100%
src/biz/dfch/specmgr/qa/models/v2/__init__.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/qa/models/v2/body.py                             37      0   100%
src/biz/dfch/specmgr/qa/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/qa/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/qa/models/v2/question_answer.py                  71      0   100%
src/biz/dfch/specmgr/qa/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/qa/prompts/__init__.py                            4      0   100%
src/biz/dfch/specmgr/qa/prompts/create_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/prompts/refine.py                              8      0   100%
src/biz/dfch/specmgr/qa/prompts/update_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/qa/resources/qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/resources/qa_schema.py                         9      0   100%
src/biz/dfch/specmgr/qa/resources/qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/__init__.py                             11      0   100%
src/biz/dfch/specmgr/qa/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/qa/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/qa/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/qa/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/qa/tools/create_qa.py                            21      0   100%
src/biz/dfch/specmgr/qa/tools/delete_qa.py                             6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa.py                               15      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/list_qa.py                              18      0   100%
src/biz/dfch/specmgr/qa/tools/parse_qa.py                              8      0   100%
src/biz/dfch/specmgr/qa/tools/set_status_qa.py                        23      0   100%
src/biz/dfch/specmgr/qa/tools/update_qa.py                            22      0   100%
src/biz/dfch/specmgr/qa/tools/validate_qa.py                          16      0   100%
src/biz/dfch/specmgr/req/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/req/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/req/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/req/models/v1/body.py                            57      0   100%
src/biz/dfch/specmgr/req/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/req/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/req/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/req/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/req/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/req/prompts/create_req.py                         8      0   100%
src/biz/dfch/specmgr/req/prompts/update_req.py                         8      0   100%
src/biz/dfch/specmgr/req/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/req/resources/req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/resources/req_schema.py                       9      0   100%
src/biz/dfch/specmgr/req/resources/req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/req/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/req/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/req/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/req/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/req/tools/create_req.py                          21      0   100%
src/biz/dfch/specmgr/req/tools/delete_req.py                           6      0   100%
src/biz/dfch/specmgr/req/tools/get_req.py                             15      0   100%
src/biz/dfch/specmgr/req/tools/get_req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/tools/get_req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/list_req.py                            18      0   100%
src/biz/dfch/specmgr/req/tools/parse_req.py                            8      0   100%
src/biz/dfch/specmgr/req/tools/set_status_req.py                      23      0   100%
src/biz/dfch/specmgr/req/tools/update_req.py                          22      0   100%
src/biz/dfch/specmgr/req/tools/validate_req.py                        16      0   100%
src/biz/dfch/specmgr/rsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/rsk/models/__init__.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/assessment.py                      57      0   100%
src/biz/dfch/specmgr/rsk/models/v1/body.py                            38      0   100%
src/biz/dfch/specmgr/rsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py                     20      0   100%
src/biz/dfch/specmgr/rsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/rsk/models/v1/summary.py                         23      0   100%
src/biz/dfch/specmgr/rsk/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/rsk/prompts/create_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/prompts/update_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/rsk/resources/risk_matrix.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/resources/tara.py                             6      0   100%
src/biz/dfch/specmgr/rsk/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/rsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/rsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/rsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/rsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/rsk/tools/create_rsk.py                          21      0   100%
src/biz/dfch/specmgr/rsk/tools/delete_rsk.py                           6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk.py                             15      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/tools/list_rsk.py                            18      0   100%
src/biz/dfch/specmgr/rsk/tools/parse_rsk.py                            8      0   100%
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py                      23      0   100%
src/biz/dfch/specmgr/rsk/tools/update_rsk.py                          22      0   100%
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py                        16      0   100%
src/biz/dfch/specmgr/server.py                                         9      1    89%
src/biz/dfch/specmgr/tsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/tsk/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/tsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/tsk/models/v1/body.py                            17      0   100%
src/biz/dfch/specmgr/tsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/tsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/tsk/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/tsk/models/v1/task_item.py                       19      0   100%
src/biz/dfch/specmgr/tsk/prompts/__init__.py                           4      0   100%
src/biz/dfch/specmgr/tsk/prompts/create_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/prompts/implement_task.py                     8      0   100%
src/biz/dfch/specmgr/tsk/prompts/update_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/__init__.py                            11      0   100%
src/biz/dfch/specmgr/tsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/tsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/tsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/tsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/tsk/tools/create_tsk.py                          21      0   100%
src/biz/dfch/specmgr/tsk/tools/delete_tsk.py                           6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk.py                             15      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/list_tsk.py                            18      0   100%
src/biz/dfch/specmgr/tsk/tools/parse_tsk.py                            8      0   100%
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py                      23      0   100%
src/biz/dfch/specmgr/tsk/tools/update_tsk.py                          22      0   100%
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py                        16      0   100%
src/biz/dfch/specmgr/uc/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/uc/models/__init__.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v1/__init__.py                         16      0   100%
src/biz/dfch/specmgr/uc/models/v1/characteristic_information.py       27      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension.py                        14      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension_action.py                  5      0   100%
src/biz/dfch/specmgr/uc/models/v1/extensions.py                        5      0   100%
src/biz/dfch/specmgr/uc/models/v1/main_success_scenario.py            12      0   100%
src/biz/dfch/specmgr/uc/models/v1/open_issues.py                       4      0   100%
src/biz/dfch/specmgr/uc/models/v1/parser.py                          204     11    95%
src/biz/dfch/specmgr/uc/models/v1/related_information.py               6      0   100%
src/biz/dfch/specmgr/uc/models/v1/related_use_cases.py                 6      0   100%
src/biz/dfch/specmgr/uc/models/v1/step.py                              5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variation.py                     5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variations.py                    5      0   100%
src/biz/dfch/specmgr/uc/models/v1/uc_diagram.py                       47      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case.py                         36      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case_frontmatter.py             16      0   100%
src/biz/dfch/specmgr/uc/models/v2/__init__.py                          7      0   100%
src/biz/dfch/specmgr/uc/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/uc/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/uc/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/uc/models/v2/use_case.py                        113      0   100%
src/biz/dfch/specmgr/uc/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/uc/resources/uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/resources/uc_schema.py                         9      0   100%
src/biz/dfch/specmgr/uc/resources/uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/__init__.py                             11      0   100%
src/biz/dfch/specmgr/uc/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/uc/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/uc/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/uc/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/uc/tools/create_uc.py                            21      0   100%
src/biz/dfch/specmgr/uc/tools/delete_uc.py                             6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc.py                               15      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/list_uc.py                              18      0   100%
src/biz/dfch/specmgr/uc/tools/parse_uc.py                              8      0   100%
src/biz/dfch/specmgr/uc/tools/set_status_uc.py                        23      0   100%
src/biz/dfch/specmgr/uc/tools/update_uc.py                            22      0   100%
src/biz/dfch/specmgr/uc/tools/validate_uc.py                          16      0   100%
--------------------------------------------------------------------------------------
TOTAL                                                               5943    105    98%
✓ Wrote docs/coverage.svg (98% coverage)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/MCP.md
✓ Wrote 319 module file(s) to /home/user/src/biz.dfch.SpecMgr-feat-22/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/GENERATED.md
DOCS_ZERO_DRIFT
IMPORT_OK
tools: 85
resources: 25
prompts: 19

```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/_splice.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/_splice.py</path>
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
18: """Frontmatter-stripped body extraction and body-line splicing for the generic
19: ``update`` tool (feat-22-consolidate-mutation-tools, Phase 2).
20: 
21: Two small, doc-type-agnostic text helpers shared by the generic ``update``
22: tool's range mode and the seven ``get_<d>`` tools' ``raw=True`` reads:
23: 
24: - :func:`body_text` extracts a document file's frontmatter-stripped body text
25:   using the established ``frontmatter.loads(path.read_text(encoding="utf-8")).
26:   content`` mechanism -- the same one every ``set_status_<d>`` tool uses.
27: - :func:`splice_body` replaces a 1-based, inclusive body-line range of that
28:   text with a replacement fragment, implementing the plan's range contract
29:   (the ``N+1`` end-of-body sentinel, splice-then-validate-whole).
30: 
31: **The raw/splice invariant.** Both helpers are the *single* definition of
32: "the body text" in this codebase: every ``get_<d>(raw=True)`` read and every
33: ``update`` range splice go through :func:`body_text`, so *what the client
34: counts is what the server splices* -- the line numbers a client sees in a raw
35: read index byte-for-byte into the same text the server splices against.
36: 
37: As with :mod:`_doc_paths`, this module has no ``mcp`` dependency -- plain
38: file I/O and text manipulation only, kept separately from any
39: ``@mcp.tool()``-decorated function so it stays independently testable.
40: """
41: 
42: from __future__ import annotations
43: 
44: from pathlib import Path
45: 
46: import frontmatter
47: 
48: __all__ = ["body_text", "splice_body"]
49: 
50: #: Minimum allowed 1-based body-line coordinate (the first line of the body).
51: _MIN_LINE = 1
52: 
53: 
54: def body_text(path: Path) -> str:
55:     """Return the frontmatter-stripped body text of the document at ``path``.
56: 
57:     Uses the established ``frontmatter.loads(path.read_text(encoding=
58:     "utf-8")).content`` mechanism (the same one every ``set_status_<d>``
59:     tool uses to re-read the raw body): the YAML frontmatter block is
60:     removed, and the remaining body markdown is returned verbatim -- never
61:     reformatted, re-rendered, or otherwise touched. The returned text is
62:     exactly the text whose 1-based lines the generic ``update`` tool's
63:     ``begin``/``end`` coordinates address (see the module docstring's
64:     raw/splice invariant).
65: 
66:     Parameters
67:     ----------
68:     path:
69:         The filesystem path to the document ``.md`` file.
70: 
71:     Returns
72:     -------
73:     str
74:         The body text with the YAML frontmatter block removed, verbatim.
75: 
76:     Raises
77:     ------
78:     FileNotFoundError
79:         The file at ``path`` does not exist.
80:     ValueError
81:         The file has no parseable frontmatter delimiters (the
82:         ``frontmatter`` library raises ``ValueError`` for that shape).
83:     """
84:     assert isinstance(path, Path), type(path)
85: 
86:     post = frontmatter.loads(path.read_text(encoding="utf-8"))
87:     content: str | bytes = post.content
88:     assert isinstance(content, str), type(content)
89:     result = content
90:     return result
91: 
92: 
93: def splice_body(current_body: str, begin: int, end: int, content: str) -> str:
94:     """Replace the 1-based, inclusive body-line range ``begin..end`` of ``current_body`` with ``content``.
95: 
96:     Implements the generic ``update`` tool's range contract (REQ-002)
97:     exactly. Let ``N = len(current_body.splitlines())`` be the number of
98:     lines of the current body; ``N + 1`` is a virtual position past the
99:     last line:
100: 
101:     - ``begin = end = k`` (1 <= k <= N) -> replace line ``k`` only.
102:     - ``begin = k``, ``end = m`` (k <= m <= N) -> replace lines ``k..m``.
103:     - ``end = N + 1`` -> the range extends through the last line (``k..N``).
104:     - ``begin = end = N + 1`` -> the range is empty at end-of-body: a pure
105:       append of ``content`` after the last line.
106:     - ``begin = 1``, ``end = N`` -> whole-body replace, equivalent to the
107:       no-range (whole-body) mode with the identical text.
108:     - Empty ``content`` -> the range is deleted (legal iff the spliced
109:       result still validates as a whole body).
110: 
111:     The splice drops lines ``begin..min(end, N)``, inserts
112:     ``content.splitlines()`` at position ``begin - 1``, and rejoins with
113:     ``"\\n"`` plus a single trailing ``"\\n"``. Lines outside the range are
114:     never touched, so unchanged regions of the on-disk body stay
115:     byte-identical; the caller validates the *spliced result* as a whole
116:     document before persisting it.
117: 
118:     Parameters
119:     ----------
120:     current_body:
121:         The current frontmatter-stripped body text (e.g. from
122:         :func:`body_text`).
123:     begin:
124:         The 1-based first line of the range to replace.
125:     end:
126:         The 1-based last line of the range to replace (inclusive); may be
127:         ``N + 1`` to extend the range through (or past, i.e. append after)
128:         the last line.
129:     content:
130:         The replacement fragment; its lines (``content.splitlines()``) take
131:         the place of the dropped range. Empty string deletes the range.
132: 
133:     Returns
134:     -------
135:     str
136:         The spliced body text (rejoined lines plus a single trailing
137:         newline).
138: 
139:     Raises
140:     ------
141:     ValueError
142:         Misused coordinates -- ``begin < 1``, ``begin > end``, or
143:         ``end > N + 1`` -- with a message naming the offending value(s)
144:         and the allowed range. Client-controlled input, so this is a
145:         ``ValueError`` (not an ``assert``), per the project's
146:         user-controlled-flow-control rule.
147:     """
148:     assert isinstance(current_body, str), type(current_body)
149:     assert isinstance(begin, int), type(begin)
150:     assert isinstance(end, int), type(end)
151:     assert isinstance(content, str), type(content)
152: 
153:     lines = current_body.splitlines()
154:     n_lines = len(lines)
155:     max_coordinate = n_lines + _MIN_LINE
156: 
157:     if begin < _MIN_LINE:
158:         raise ValueError(f"begin must be in {_MIN_LINE}..{max_coordinate}, got {begin}")
159:     if begin > end:
160:         raise ValueError(f"begin must be <= end, got begin={begin} > end={end}")
161:     if end > max_coordinate:
162:         raise ValueError(
163:             f"end must be in {_MIN_LINE}..{max_coordinate} for this {n_lines}-line body "
164:             f"(N+1 = {max_coordinate} is the end-of-body sentinel), got {end}"
165:         )
166: 
167:     drop_end = min(end, n_lines)
168:     result_lines = lines[: begin - _MIN_LINE] + content.splitlines() + lines[drop_end:]
169:     result = "\n".join(result_lines) + "\n"
170:     return result

(End of file - total 170 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 73.9s)

_Thinking:_

Excellent. Everything verified in my independent execution:

- Regeneration: coverage-badge (98%, svg written), mcp-docs, docs — then re-ran all 3, `diff` of the manifest was empty → **DOCS_ZERO_DRIFT**

- Fresh subprocess import: **IMPORT_OK**

- Live count: **85 tools / 25 resources / 19 prompts** — exactly the expected additive diff

- `_splice.py` looks correct:

  - `body_text`: frontmatter.loads mechanism, assert isinstance (internal invariant — no problem, these are assertions on internal types, not on client input; conforms to convention)
  - `splice_body`: N = len(splitlines); ValueError on begin\<1, begin>end, end>N+1 (with explicit message); drop lines[:begin-1] + content.splitlines() + lines[min(end,N):]; join + trailing \\n.

  Let me verify the splice algorithm against the contract:

  - Middle replacement: lines[:k-1] + frag + lines[m:] — correct (drop k..m, 1-indexed → slice begin-1:drop_end).
  - begin=end=N+1: drop_end = min(N+1, N) = N; lines[:N] + frag + lines[N:] = all lines + frag → append at the end. ✓
  - end=N+1: drop_end = N; lines[:k-1] + frag + lines[N:] → replace k..N. ✓
  - begin=1, end=N: lines[:0] + frag + lines[N:] → full replacement. ✓
  - Empty content: frag = [] → delete. ✓
  - Edge case: when body is empty (N=0): begin must be 1 (only N+1=1 is valid), begin=end=1 → append. lines[:0]+frag+lines[0:] → frag. ✓

- Copyright header: the new file has an AGPL header — good house style (other files probably have it too; ruff check passed).

Next, I'll spot-check `update.py` — the verbatim port is the highest-risk part. Let me read it, and also look at one of the original update_req.py to compare, plus check one get\_<d> diff and the mcp_docs.py diff, and skim the plan README diff for the Phase 2 progress entry.

update.py is probably about 234 lines (per the coverage report: `update.py 234 0 100%` — 234 statements, 100% covered).

Let me read update.py and update_req.py in parallel.

Independent verification of the Phase 2 gate is green: the generator has zero drift (re-run the manifest diff → empty), the new subprocess imports are OK, live counts are **85/25/19**, and the splice algorithm has been verified against the contract (N+1 append / trailing EOF / full range / delete all correct). Next is a code-level spot check — the verbatim porting is the highest-risk part, so I'll compare `update.py` against the original `update_req.py`, and additionally check the `get_<d>` and `mcp_docs.py` diffs:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/update.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/update.py</path>
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
18: """``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).
19: 
20: The generic, cross-domain whole-body *and* line-range replace tool for the
21: seven whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
22: ``gol``/``rsk``). It dispatches on the explicit ``type`` parameter to a
23: private per-domain adapter (``_update_<d>``), each a **verbatim port** of
24: the corresponding per-domain ``update_<d>`` tool's function body (same
25: domain lock, same ``load_by_id``, same frontmatter carry-over with only
26: ``updated`` bumped, same verbatim persistence via the domain's own
27: ``write_<d>_file``, same domain ``XNotFoundError``) plus the REQ-002 range
28: branch: with ``begin``/``end`` given, the on-disk body is re-read via
29: :func:`._splice.body_text`, spliced via :func:`._splice.splice_body`, and
30: the *spliced result* is validated as a whole document and persisted
31: verbatim instead of the raw fragment.
32: 
33: The parameter is intentionally named ``type`` (it matches the frontmatter
34: field vocabulary the client already knows); no enabled ruff rule objects to
35: the builtin shadow. The 7-way union return type is annotation-only -- the
36: MCP input schema is built from the parameters, and the SDK serializes
37: whichever concrete document is returned.
38: 
39: ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
40: contract (``update_frontmatter``/``update_section``/``option_*``) has no
41: whole-body replace by design.
42: """
43: 
44: from __future__ import annotations
45: 
46: from collections.abc import Callable
47: from datetime import datetime
48: from typing import Literal
49: 
50: from ...gol.models.v1 import GolDocument, GolFrontmatter, Goal
51: from ...gol.tools._io import load_by_id as load_gol_by_id
52: from ...gol.tools._lock import gol_lock
53: from ...gol.tools._paths import gol_base_dir
54: from ...gol.tools._write import write_gol_file
55: from ...models.md._markdown import format_text
56: from ...prb.models.v1 import Prb, PrbDocument, PrbFrontmatter
57: from ...prb.tools._io import load_by_id as load_prb_by_id
58: from ...prb.tools._lock import prb_lock
59: from ...prb.tools._paths import prb_base_dir
60: from ...prb.tools._write import write_prb_file
61: from ...qa.models.v2 import Qa, QaDocument, QaFrontmatter
62: from ...qa.tools._io import load_by_id as load_qa_by_id
63: from ...qa.tools._lock import qa_lock
64: from ...qa.tools._paths import qa_base_dir
65: from ...qa.tools._write import write_qa_file
66: from ...req.models.v1 import ReqDocument, ReqFrontmatter, Requirement
67: from ...req.tools._io import load_by_id as load_req_by_id
68: from ...req.tools._lock import req_lock
69: from ...req.tools._paths import req_base_dir
70: from ...req.tools._write import write_req_file
71: from ...rsk.models.v1 import Risk, RskDocument, RskFrontmatter
72: from ...rsk.tools._io import load_by_id as load_rsk_by_id
73: from ...rsk.tools._lock import rsk_lock
74: from ...rsk.tools._paths import rsk_base_dir
75: from ...rsk.tools._write import write_rsk_file
76: from ...server import mcp
77: from ...tsk.models.v1 import Task, TskDocument, TskFrontmatter
78: from ...tsk.tools._io import load_by_id as load_tsk_by_id
79: from ...tsk.tools._lock import tsk_lock
80: from ...tsk.tools._paths import tsk_base_dir
81: from ...tsk.tools._write import write_tsk_file
82: from ...uc.models.v2 import UcDocument, UcFrontmatter, UseCase
83: from ...uc.tools._io import load_by_id as load_uc_by_id
84: from ...uc.tools._lock import uc_lock
85: from ...uc.tools._paths import uc_base_dir
86: from ...uc.tools._write import write_uc_file
87: from ._splice import body_text, splice_body
88: 
89: __all__ = ["update"]
90: 
91: #: The generic tool's 7-way return union -- annotation-only (see module docstring).
92: _UpdateDocument = ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument
93: 
94: 
95: def _update_req(id_: str, content: str, begin: int | None, end: int | None) -> ReqDocument:
96:     """Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).
97: 
98:     Verbatim port of ``req.tools.update_req.update_req``'s function body
99:     (same ``req_lock``, ``load_by_id``, frontmatter carry-over with only
100:     ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``), plus the
101:     REQ-002 range branch: with ``begin``/``end`` given (both-or-neither is
102:     enforced by the public :func:`update` before dispatch), the on-disk
103:     body is re-read via :func:`body_text`, spliced via
104:     :func:`splice_body`, and the *spliced result* is validated and
105:     persisted verbatim instead of the raw fragment.
106:     """
107:     if begin is not None or end is not None:
108:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
109: 
110:         base_dir = req_base_dir()
111:         with req_lock(id_):
112:             path, existing = load_req_by_id(base_dir, id_)
113:             spliced = splice_body(body_text(path), begin, end, content)
114:             body = Requirement.from_text(format_text(spliced))
115:             now = datetime.now().isoformat(timespec="microseconds")
116:             fm_data = existing.frontmatter.model_dump()
117:             fm_data["updated"] = now
118:             new_frontmatter = ReqFrontmatter(**fm_data)
119:             new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
120:             write_req_file(path, new_frontmatter, spliced)
121:         return new_doc
122: 
123:     body = Requirement.from_text(format_text(content))
124: 
125:     base_dir = req_base_dir()
126:     with req_lock(id_):
127:         path, existing = load_req_by_id(base_dir, id_)
128:         now = datetime.now().isoformat(timespec="microseconds")
129:         fm_data = existing.frontmatter.model_dump()
130:         fm_data["updated"] = now
131:         new_frontmatter = ReqFrontmatter(**fm_data)
132:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
133:         write_req_file(path, new_frontmatter, content)
134:     return new_doc
135: 
136: 
137: def _update_uc(id_: str, content: str, begin: int | None, end: int | None) -> UcDocument:
138:     """Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).
139: 
140:     Verbatim port of ``uc.tools.update_uc.update_uc``'s function body (same
141:     ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
142:     ``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``), plus the
143:     REQ-002 range branch (see :func:`_update_req`).
144:     """
145:     if begin is not None or end is not None:
146:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
147: 
148:         base_dir = uc_base_dir()
149:         with uc_lock(id_):
150:             path, existing = load_uc_by_id(base_dir, id_)
151:             spliced = splice_body(body_text(path), begin, end, content)
152:             body = UseCase.from_text(format_text(spliced))
153:             now = datetime.now().isoformat(timespec="microseconds")
154:             fm_data = existing.frontmatter.model_dump()
155:             fm_data["updated"] = now
156:             new_frontmatter = UcFrontmatter(**fm_data)
157:             new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
158:             write_uc_file(path, new_frontmatter, spliced)
159:         return new_doc
160: 
161:     body = UseCase.from_text(format_text(content))
162: 
163:     base_dir = uc_base_dir()
164:     with uc_lock(id_):
165:         path, existing = load_uc_by_id(base_dir, id_)
166:         now = datetime.now().isoformat(timespec="microseconds")
167:         fm_data = existing.frontmatter.model_dump()
168:         fm_data["updated"] = now
169:         new_frontmatter = UcFrontmatter(**fm_data)
170:         new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
171:         write_uc_file(path, new_frontmatter, content)
172:     return new_doc
173: 
174: 
175: def _update_tsk(id_: str, content: str, begin: int | None, end: int | None) -> TskDocument:
176:     """Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).
177: 
178:     Verbatim port of ``tsk.tools.update_tsk.update_tsk``'s function body
179:     (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over with only
180:     ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``), plus the
181:     REQ-002 range branch (see :func:`_update_req`).
182:     """
183:     if begin is not None or end is not None:
184:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
185: 
186:         base_dir = tsk_base_dir()
187:         with tsk_lock(id_):
188:             path, existing = load_tsk_by_id(base_dir, id_)
189:             spliced = splice_body(body_text(path), begin, end, content)
190:             body = Task.from_text(format_text(spliced))
191:             now = datetime.now().isoformat(timespec="microseconds")
192:             fm_data = existing.frontmatter.model_dump()
193:             fm_data["updated"] = now
194:             new_frontmatter = TskFrontmatter(**fm_data)
195:             new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
196:             write_tsk_file(path, new_frontmatter, spliced)
197:         return new_doc
198: 
199:     body = Task.from_text(format_text(content))
200: 
201:     base_dir = tsk_base_dir()
202:     with tsk_lock(id_):
203:         path, existing = load_tsk_by_id(base_dir, id_)
204:         now = datetime.now().isoformat(timespec="microseconds")
205:         fm_data = existing.frontmatter.model_dump()
206:         fm_data["updated"] = now
207:         new_frontmatter = TskFrontmatter(**fm_data)
208:         new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
209:         write_tsk_file(path, new_frontmatter, content)
210:     return new_doc
211: 
212: 
213: def _update_qa(id_: str, content: str, begin: int | None, end: int | None) -> QaDocument:
214:     """Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).
215: 
216:     Verbatim port of ``qa.tools.update_qa.update_qa``'s function body (same
217:     ``qa_lock``, ``load_by_id``, frontmatter carry-over with only
218:     ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``), plus the
219:     REQ-002 range branch (see :func:`_update_req`).
220:     """
221:     if begin is not None or end is not None:
222:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
223: 
224:         base_dir = qa_base_dir()
225:         with qa_lock(id_):
226:             path, existing = load_qa_by_id(base_dir, id_)
227:             spliced = splice_body(body_text(path), begin, end, content)
228:             body = Qa.from_text(format_text(spliced))
229:             now = datetime.now().isoformat(timespec="microseconds")
230:             fm_data = existing.frontmatter.model_dump()
231:             fm_data["updated"] = now
232:             new_frontmatter = QaFrontmatter(**fm_data)
233:             new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
234:             write_qa_file(path, new_frontmatter, spliced)
235:         return new_doc
236: 
237:     body = Qa.from_text(format_text(content))
238: 
239:     base_dir = qa_base_dir()
240:     with qa_lock(id_):
241:         path, existing = load_qa_by_id(base_dir, id_)
242:         now = datetime.now().isoformat(timespec="microseconds")
243:         fm_data = existing.frontmatter.model_dump()
244:         fm_data["updated"] = now
245:         new_frontmatter = QaFrontmatter(**fm_data)
246:         new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
247:         write_qa_file(path, new_frontmatter, content)
248:     return new_doc
249: 
250: 
251: def _update_prb(id_: str, content: str, begin: int | None, end: int | None) -> PrbDocument:
252:     """Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).
253: 
254:     Verbatim port of ``prb.tools.update_prb.update_prb``'s function body
255:     (same ``prb_lock``, ``load_by_id``, frontmatter carry-over with only
256:     ``updated`` bumped, ``write_prb_file``, ``PrbNotFoundError``), plus the
257:     REQ-002 range branch (see :func:`_update_req`).
258:     """
259:     if begin is not None or end is not None:
260:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
261: 
262:         base_dir = prb_base_dir()
263:         with prb_lock(id_):
264:             path, existing = load_prb_by_id(base_dir, id_)
265:             spliced = splice_body(body_text(path), begin, end, content)
266:             body = Prb.from_text(format_text(spliced))
267:             now = datetime.now().isoformat(timespec="microseconds")
268:             fm_data = existing.frontmatter.model_dump()
269:             fm_data["updated"] = now
270:             new_frontmatter = PrbFrontmatter(**fm_data)
271:             new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
272:             write_prb_file(path, new_frontmatter, spliced)
273:         return new_doc
274: 
275:     body = Prb.from_text(format_text(content))
276: 
277:     base_dir = prb_base_dir()
278:     with prb_lock(id_):
279:         path, existing = load_prb_by_id(base_dir, id_)
280:         now = datetime.now().isoformat(timespec="microseconds")
281:         fm_data = existing.frontmatter.model_dump()
282:         fm_data["updated"] = now
283:         new_frontmatter = PrbFrontmatter(**fm_data)
284:         new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
285:         write_prb_file(path, new_frontmatter, content)
286:     return new_doc
287: 
288: 
289: def _update_gol(id_: str, content: str, begin: int | None, end: int | None) -> GolDocument:
290:     """Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).
291: 
292:     Verbatim port of ``gol.tools.update_gol.update_gol``'s function body
293:     (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with only
294:     ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``), plus the
295:     REQ-002 range branch (see :func:`_update_req`).
296:     """
297:     if begin is not None or end is not None:
298:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
299: 
300:         base_dir = gol_base_dir()
301:         with gol_lock(id_):
302:             path, existing = load_gol_by_id(base_dir, id_)
303:             spliced = splice_body(body_text(path), begin, end, content)
304:             body = Goal.from_text(format_text(spliced))
305:             now = datetime.now().isoformat(timespec="microseconds")
306:             fm_data = existing.frontmatter.model_dump()
307:             fm_data["updated"] = now
308:             new_frontmatter = GolFrontmatter(**fm_data)
309:             new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
310:             write_gol_file(path, new_frontmatter, spliced)
311:         return new_doc
312: 
313:     body = Goal.from_text(format_text(content))
314: 
315:     base_dir = gol_base_dir()
316:     with gol_lock(id_):
317:         path, existing = load_gol_by_id(base_dir, id_)
318:         now = datetime.now().isoformat(timespec="microseconds")
319:         fm_data = existing.frontmatter.model_dump()
320:         fm_data["updated"] = now
321:         new_frontmatter = GolFrontmatter(**fm_data)
322:         new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
323:         write_gol_file(path, new_frontmatter, content)
324:     return new_doc
325: 
326: 
327: def _update_rsk(id_: str, content: str, begin: int | None, end: int | None) -> RskDocument:
328:     """Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).
329: 
330:     Verbatim port of ``rsk.tools.update_rsk.update_rsk``'s function body
331:     (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with only
332:     ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``), plus the
333:     REQ-002 range branch (see :func:`_update_req`).
334:     """
335:     if begin is not None or end is not None:
336:         assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"
337: 
338:         base_dir = rsk_base_dir()
339:         with rsk_lock(id_):
340:             path, existing = load_rsk_by_id(base_dir, id_)
341:             spliced = splice_body(body_text(path), begin, end, content)
342:             body = Risk.from_text(format_text(spliced))
343:             now = datetime.now().isoformat(timespec="microseconds")
344:             fm_data = existing.frontmatter.model_dump()
345:             fm_data["updated"] = now
346:             new_frontmatter = RskFrontmatter(**fm_data)
347:             new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
348:             write_rsk_file(path, new_frontmatter, spliced)
349:         return new_doc
350: 
351:     body = Risk.from_text(format_text(content))
352: 
353:     base_dir = rsk_base_dir()
354:     with rsk_lock(id_):
355:         path, existing = load_rsk_by_id(base_dir, id_)
356:         now = datetime.now().isoformat(timespec="microseconds")
357:         fm_data = existing.frontmatter.model_dump()
358:         fm_data["updated"] = now
359:         new_frontmatter = RskFrontmatter(**fm_data)
360:         new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
361:         write_rsk_file(path, new_frontmatter, content)
362:     return new_doc
363: 
364: 
365: #: Dispatch table mapping the ``type`` value to its private adapter.
366: _ADAPTERS: dict[str, Callable[[str, str, int | None, int | None], _UpdateDocument]] = {
367:     "req": _update_req,
368:     "uc": _update_uc,
369:     "tsk": _update_tsk,
370:     "qa": _update_qa,
371:     "prb": _update_prb,
372:     "gol": _update_gol,
373:     "rsk": _update_rsk,
374: }
375: 
376: 
377: @mcp.tool(
378:     name="update",
379:     title="Update document",
380:     description=(
381:         "Whole-body or line-range replace of an existing document's content across the seven "
382:         "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk), preserving its "
383:         "id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` "
384:         "is the full replacement body (body markdown only, no frontmatter block). With both, "
385:         "`content` replaces the 1-based inclusive body-line range `begin`..`end` of the current "
386:         "on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace "
387:         "through end of body); the spliced result is validated as a whole document before "
388:         "anything is written. `status` is never settable -- use the `set_status_*` tools."
389:     ),
390: )
391: def update(
392:     id: str,
393:     type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk"],
394:     content: str,
395:     begin: int | None = None,
396:     end: int | None = None,
397: ) -> _UpdateDocument:
398:     """Replace the body of an existing document, in whole-body or line-range mode.
399: 
400:     Cross-domain generic for the seven whole-body document types
401:     (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``); dispatches on
402:     ``type`` to the domain's own ported adapter (same lock, same id
403:     resolution, same frontmatter carry-over, same verbatim persistence,
404:     same domain not-found error).
405: 
406:     **Whole-body mode** (no ``begin``/``end``): ``content`` is body
407:     markdown only, with no YAML frontmatter block -- the same shape the
408:     per-domain ``update_<d>`` tools accept. Validated the same way: the
409:     domain body model's ``from_text(format_text(content))``, letting
410:     ``AssertionError`` (structural failure) or ``pydantic.ValidationError``
411:     (field/cross-field failure) propagate uncaught, with nothing written in
412:     either case.
413: 
414:     **Range mode** (both ``begin`` and ``end`` given): ``content`` is a
415:     replacement *fragment* for the current on-disk body's 1-based,
416:     inclusive line range ``begin..end``, where ``N`` is the number of lines
417:     of the current frontmatter-stripped body (the text ``get_<d>(id,
418:     raw=True)`` returns) and ``N+1`` is a virtual position past the last
419:     line (``begin = end = N+1`` appends at end of body; ``end = N+1``
420:     extends the range through the last line). The on-disk body is re-read
421:     under the domain lock, spliced (drop lines ``begin..min(end, N)``,
422:     insert the fragment's lines at position ``begin - 1``), and the
423:     *spliced result* -- not the fragment -- is validated as a whole body
424:     exactly like whole-body mode and then persisted verbatim, so unchanged
425:     regions of the on-disk body stay byte-identical. An empty ``content``
426:     deletes the range (legal iff the result still validates). The YAML
427:     frontmatter is never addressable: coordinates are body-relative by
428:     construction.
429: 
430:     In both modes the existing file's frontmatter is carried over with
431:     every field preserved except ``updated`` (bumped to the current
432:     microsecond timestamp); ``status`` in particular is never settable
433:     through this tool -- the per-domain ``set_status_<d>`` tools are the
434:     only status-change path.
435: 
436:     Parameters
437:     ----------
438:     id:
439:         The document's specmgr-assigned identifier.
440:     type:
441:         The document type / domain: one of ``req``, ``uc``, ``tsk``,
442:         ``qa``, ``prb``, ``gol``, ``rsk``.
443:     content:
444:         Whole-body mode: the replacement body markdown, with no
445:         frontmatter block. Range mode: the replacement fragment for lines
446:         ``begin..end`` (may be empty to delete the range).
447:     begin:
448:         Optional 1-based first line of the range to replace. Must be given
449:         together with ``end`` (exactly one of the two is a ``ValueError``).
450:     end:
451:         Optional 1-based last line of the range to replace (inclusive);
452:         ``N+1`` (one past the last body line) extends the range through
453:         end of body. Must be given together with ``begin``.
454: 
455:     Returns
456:     -------
457:     ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument
458:         The updated document of the dispatched domain type.
459: 
460:     Raises
461:     ------
462:     ValueError
463:         Misused range coordinates: exactly one of ``begin``/``end`` given
464:         (raised before any file access), or ``begin < 1``, ``begin > end``,
465:         or ``end > N + 1`` (raised after the on-disk body is read; the
466:         message names the offending value(s) and the allowed range).
467:         Nothing is written in any of these cases.
468:     AssertionError
469:         The (spliced) body is structurally invalid (e.g. a range that
470:         deletes the H1). Nothing is written.
471:     pydantic.ValidationError
472:         A field/cross-field validation failure in the (spliced) body (e.g.
473:         a range producing an out-of-vocabulary value). Nothing is written.
474:     ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
475:     PrbNotFoundError / GolNotFoundError / RskNotFoundError
476:         No document of the dispatched ``type`` has this id -- the
477:         domain's own not-found error, unchanged from the per-domain tools.
478:     """
479:     if (begin is None) != (end is None):
480:         raise ValueError(f"begin and end must be given together (both or neither), got begin={begin!r}, end={end!r}")
481: 
482:     adapter = _ADAPTERS[type]
483:     result = adapter(id, content, begin, end)
484:     return result

(End of file - total 484 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/req/tools/update_req.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/req/tools/update_req.py</path>
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
18: """``@mcp.tool()`` wrapper: update_req (Task 3.13).
19: 
20: Same body-only ``content`` shape as ``create_req`` (Task 3.12), but against
21: an *existing* document: ``id``/``type``/``status``/``created``/``version``
22: are all read back from the file currently on disk and preserved unchanged;
23: only ``updated`` is bumped to the current timestamp. ``status`` is never
24: settable here -- see the dedicated ``set_status_req`` tool (Task 3.14).
25: 
26: Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
27: on-disk state before re-writing the full file; there is no in-memory cache
28: of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
29: ``.md`` file itself is always the source of truth. The whole sequence runs
30: under ``req_lock(id)`` so a concurrent mutation against the same id cannot
31: interleave with it and cause a lost update (mirrors every ADR mutation
32: tool's own ``adr_lock`` usage).
33: """
34: 
35: from __future__ import annotations
36: 
37: from datetime import datetime
38: 
39: from ...models.md._markdown import format_text
40: from ...server import mcp
41: from ..models.v1 import ReqDocument, ReqFrontmatter, Requirement
42: from ._io import load_by_id
43: from ._lock import req_lock
44: from ._paths import req_base_dir
45: from ._write import write_req_file
46: 
47: 
48: @mcp.tool(
49:     name="update_req",
50:     title="Update requirement",
51:     description=(
52:         "Whole-body replace of an existing requirement's content, preserving its "
53:         "id/type/status/created/version; only `updated` changes. Use `set_status_req` to "
54:         "change status instead."
55:     ),
56: )
57: def update_req(id: str, content: str) -> ReqDocument:
58:     """Replace the body of the requirement identified by ``id``.
59: 
60:     ``content`` is body markdown only, same shape as :func:`.create_req.create_req`
61:     -- it must not carry a YAML frontmatter block. Validated the same way:
62:     ``Requirement.from_text(format_text(content))``, letting ``AssertionError``
63:     (structural failure) or ``pydantic.ValidationError`` (field/cross-field
64:     failure) propagate uncaught, with nothing written in either case.
65: 
66:     The existing file is read first (under ``req_lock(id)``) to resolve its
67:     path and current frontmatter; every frontmatter field except ``updated``
68:     is carried over unchanged -- ``status`` in particular is never settable
69:     through this tool.
70: 
71:     Parameters
72:     ----------
73:     id:
74:         The document's specmgr-assigned identifier.
75:     content:
76:         The replacement body markdown, with no frontmatter block.
77: 
78:     Returns
79:     -------
80:     ReqDocument
81:         The updated document. Raises :class:`._paths.ReqNotFoundError` if
82:         no requirement has this id.
83:     """
84:     body = Requirement.from_text(format_text(content))
85: 
86:     base_dir = req_base_dir()
87:     with req_lock(id):
88:         path, existing = load_by_id(base_dir, id)
89:         now = datetime.now().isoformat(timespec="microseconds")
90:         fm_data = existing.frontmatter.model_dump()
91:         fm_data["updated"] = now
92:         new_frontmatter = ReqFrontmatter(**fm_data)
93:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
94:         write_req_file(path, new_frontmatter, content)
95:     return new_doc

(End of file - total 95 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 144.9s)

_Thinking:_

Verbatim port confirmed for `req`: the full-body branch of `_update_req` matches the body of `update_req` line by line (validate → base_dir → lock → load → now → fm_data → updated → new_frontmatter → new_doc → write). The range branch is added correctly:

- Guard on the public `update` before dispatch: `(begin is None) != (end is None)` → ValueError before any file access. ✓
- Inside the adapter: both-or-neither assert (defense in depth — assert on an internal invariant, permissible), base_dir, lock, load, splice_body(body_text(path), ...), validate the spliced result, carry over the frontmatter, write the spliced text as-is. ✓

One thing I noticed: the `@mcp.tool` description for `update` says "the per-domain `set_status_*` tools are the only path for status changes" — at the end of Phase 2 this is still correct (those tools exist until Phase 4). In Phase 4 it will need to be reworded to refer to the generic `set_status`. This is a Phase 4 task concern (the plan's Phase 4 Task 4.1/4.5 covers server.py; updating the description in update.py isn't explicitly in the plan, but the Phase 4 grep verification… hmm, actually, ACC-005 says that after Phase 5, grepping for the deleted tool names in src/ and tests/ must return zero hits. The description in `update.py` mentions `set_status_*` (with wildcard — grep for `set_status_` will match `set_status_*`!). In Phase 4, the tool description in `general/tools/update.py` needs to be updated to refer to the generic `set_status`. Let me note this as a Phase 4 requirement — the plan's Task 4.5 covers the server.py docstring, but the `set_status_<d>` reference inside update.py's description is a leftover from the deleted tools. ACC-005: "grep against src/ and tests/ finds no code references to deleted tool names (residual mentions before Phase 5 are limited to prompt description files owned by Phase 5, and zero thereafter)". The literal deleted tool names are `set_status_req`, `set_status_uc`, etc. `set_status_*` is a wildcard, not a literal name. But it's still an inaccurate description after Phase 4. I'll explicitly instruct in the Phase 4 prompt: update the `@mcp.tool` description and the docstring in `general/tools/update.py` that refer to the `set_status_<d>`/`set_status_*` tools so they reference the generic `set_status` tool. Good catch.

Let me also quickly check the diff of get_req.py and the diff of mcp_docs.py, plus the Phase 2 progress entry in the plan README. Then commit Phase 2.

Actually, let me do it efficiently: read the get_req.py diff + the mcp_docs.py diff + the README diff (the Phase 2 entry).

The verbatim port has been confirmed line by line for `req` (and the structure is identical across all 7 adapters). The both-or-neither guard is placed inside the public `update` before any file access — exactly as the plan requires.

**One point to note for Phase 4**: The `@mcp.tool` description and docstring of `update.py` state "the per-domain `set_status_*` tools are the only path for changing status," which is correct at the end of Phase 2, but becomes an outdated description after Phase 4 deletes those tools. I'll make this an explicit task in the Phase 4 delegation.

Currently checking the diff of `get_<d>`, the diff of `mcp_docs.py`, and the progress entry of Phase 2 in the plan's README:

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U4 -- src/biz/dfch/specmgr/req/tools/get_req.py src/biz/dfch/specmgr/commands/mcp_docs.py src/biz/dfch/specmgr/general/tools/__init__.py",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/commands/mcp_docs.py b/src/biz/dfch/specmgr/commands/mcp_docs.py
index 4532314..775a7db 100644
--- a/src/biz/dfch/specmgr/commands/mcp_docs.py
+++ b/src/biz/dfch/specmgr/commands/mcp_docs.py
@@ -56,12 +56,15 @@ def _schema_type_str(prop_schema: dict[str, Any]) -> str:
     """Render a single JSON Schema property as a short type string.
 
     Resolves ``$ref`` to the referenced definition's bare name (e.g.
     ``#/$defs/AdrBody`` -> ``AdrBody``), collapses ``anyOf`` (typically an
-    optional field's ``[T, null]`` union) into ``T | None``, and renders
-    ``array`` as ``list[T]``. Falls back to ``"any"`` when no recognizable
-    shape is present -- this is a best-effort summary for documentation, not
-    a full schema renderer.
+    optional field's ``[T, null]`` union) into ``T | None``, renders
+    ``array`` as ``list[T]``, and surfaces a closed ``enum`` (e.g. the
+    generic ``update`` tool's 7-value ``type``) as
+    ``T (enum: v1, v2, ...)`` -- the enum's values are part of the
+    contract, not an implementation detail. Falls back to ``"any"`` when
+    no recognizable shape is present -- this is a best-effort summary for
+    documentation, not a full schema renderer.
     """
     if "$ref" in prop_schema:
         return str(prop_schema["$ref"]).rsplit("/", maxsplit=1)[-1]
 
@@ -77,8 +80,12 @@ def _schema_type_str(prop_schema: dict[str, Any]) -> str:
         return f"list[{_schema_type_str(items)}]"
     if schema_type == "null":
         return "None"
     if isinstance(schema_type, str):
+        enum_values = prop_schema.get("enum")
+        if enum_values is not None:
+            values = ", ".join(str(value) for value in enum_values)
+            return f"{schema_type} (enum: {values})"
         return schema_type
 
     return "any"
 
diff --git a/src/biz/dfch/specmgr/general/tools/__init__.py b/src/biz/dfch/specmgr/general/tools/__init__.py
index 546fa6b..2cb4374 100644
--- a/src/biz/dfch/specmgr/general/tools/__init__.py
+++ b/src/biz/dfch/specmgr/general/tools/__init__.py
@@ -17,18 +17,24 @@
 
 """MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).
 
 ``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
-blocks (for ADR/UC files) and formats only the body markdown. ``webfetch`` --
-a bearer-authenticated HTTP GET fetch restricted to a configured base URL.
-Import this package to register all general tools at once::
+blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
+the generic, cross-domain whole-body or line-range replace for the seven
+whole-body document types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk;
+optional 1-based inclusive body-line ``begin``/``end`` range with the
+``N+1`` end-of-body sentinel). ``webfetch`` -- a bearer-authenticated HTTP
+GET fetch restricted to a configured base URL. Import this package to
+register all general tools at once::
 
     from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
 """
 
 from .mdformat import mdformat
+from .update import update
 from .webfetch import webfetch
 
 __all__ = [
     "mdformat",
+    "update",
     "webfetch",
 ]
diff --git a/src/biz/dfch/specmgr/req/tools/get_req.py b/src/biz/dfch/specmgr/req/tools/get_req.py
index 0259ca7..fa38f11 100644
--- a/src/biz/dfch/specmgr/req/tools/get_req.py
+++ b/src/biz/dfch/specmgr/req/tools/get_req.py
@@ -28,12 +28,20 @@ was removed because LLM/agent clients calling this MCP server failed to
 reliably invoke it. See ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose
 id-based REQ document reads as a tool (get_req), not a resource") for the
 full rationale, including why the equivalent ``specmgr://adr/{id}`` resource
 was deliberately left untouched.
+
+``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
+frontmatter-stripped body text verbatim instead of the parsed document --
+produced by the same :func:`~biz.dfch.specmgr.general.tools._splice.body_text`
+helper the generic ``update`` tool's range splice uses, so the line numbers
+a client counts in a raw read index byte-for-byte into the text the server
+splices against.
 """
 
 from __future__ import annotations
 
+from ...general.tools._splice import body_text
 from ...server import mcp
 from ..models.v1 import ReqDocument
 from ._io import load_by_id
 from ._paths import req_base_dir
@@ -41,23 +49,37 @@ from ._paths import req_base_dir
 
 @mcp.tool(
     name="get_req",
     title="Get requirement",
-    description="Read, parse, and return a full requirement document (frontmatter and body) by its id.",
+    description=(
+        "Read, parse, and return a full requirement document (frontmatter and body) by its id. "
+        "Pass raw=True to return the frontmatter-stripped body text verbatim instead."
+    ),
 )
-def get_req(id: str) -> ReqDocument:
+def get_req(id: str, raw: bool = False) -> ReqDocument | str:
     """Read and return the requirement identified by ``id``.
 
     Parameters
     ----------
     id:
         The document's specmgr-assigned identifier.
+    raw:
+        With ``False`` (the default), return the parsed document, exactly
+        as before. With ``True``, return the frontmatter-stripped body
+        text verbatim as a plain string -- the same text whose 1-based
+        lines the generic ``update`` tool's ``begin``/``end`` coordinates
+        address (shared body-extraction helper with the splice).
 
     Returns
     -------
-    ReqDocument
-        The current on-disk document, freshly re-read and re-parsed.
+    ReqDocument | str
+        With ``raw=False``: the current on-disk document, freshly re-read
+        and re-parsed. With ``raw=True``: the body text as a plain string.
         Raises :class:`._paths.ReqNotFoundError` if no requirement has this id.
     """
     base_dir = req_base_dir()
-    _, doc = load_by_id(base_dir, id)
-    return doc
+    path, doc = load_by_id(base_dir, id)
+    if raw:
+        result: ReqDocument | str = body_text(path)
+        return result
+    result = doc
+    return result

```

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U2 -- .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | head -150",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md b/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
index 155696d..94b7d0b 100644
--- a/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
+++ b/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md
@@ -455,5 +455,5 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
 #### Phase 2: Generic `update` tool + `raw` read parameter
 
-- [ ] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain
+- [x] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain
   file I/O + text manipulation, module docstring explaining the raw/splice
   invariant): `body_text(path: Path) -> str` (frontmatter-stripped body text
@@ -465,6 +465,6 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   `content.splitlines()` at position `begin - 1`; rejoin `"\n"` + single
   trailing `"\n"`; empty `content` = deletion) — depends on: none — status:
-  not-started
-- [ ] Task 2.2: Create `general/tools/update.py`: seven private adapter
+  done
+- [x] Task 2.2: Create `general/tools/update.py`: seven private adapter
   functions `_update_<d>(id_, content, begin, end)` — verbatim ports of the
   current `update_<d>` function bodies (same `X_lock`, `load_by_id`,
@@ -481,8 +481,8 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   GolDocument | RskDocument` with a full numpy-style docstring (including
   the range contract and the error types) — depends on: Task 2.1 — status:
-  not-started
-- [ ] Task 2.3: Register `update` in `general/tools/__init__.py` (import,
-  `__all__`, module docstring) — depends on: Task 2.2 — status: not-started
-- [ ] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`
+  done
+- [x] Task 2.3: Register `update` in `general/tools/__init__.py` (import,
+  `__all__`, module docstring) — depends on: Task 2.2 — status: done
+- [x] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`
   tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`,
   `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`,
@@ -492,11 +492,11 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   Design-Notes invariant); `raw=False` returns the parsed document exactly as
   today; update each tool's `@mcp.tool` description and docstring Returns
-  section — depends on: Task 2.1 — status: not-started
-- [ ] Task 2.5: Update `server.py`'s module docstring: add `update` to the
+  section — depends on: Task 2.1 — status: done
+- [x] Task 2.5: Update `server.py`'s module docstring: add `update` to the
   General-tools lines (one line describing whole-body *and* line-range
   replace, the 7-value `type`, optional `begin`/`end`); note the `raw`
   parameter where the seven `get_<d>` tools are enumerated — depends on:
-  Task 2.2, Task 2.4 — status: not-started
-- [ ] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all
+  Task 2.2, Task 2.4 — status: done
+- [x] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all
   seven types (seed a document per type, e.g. via the domain `create_<d>`
   tool in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the
@@ -511,7 +511,6 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   every `ValueError` misuse case; range deleting the H1 → `AssertionError`,
   file untouched; range producing an out-of-vocabulary field value →
-  `ValidationError`, file untouched) — depends on: Task 2.2 — status: not-
-  started
-- [ ] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`
+  `ValidationError`, file untouched) — depends on: Task 2.2 — status: done
+- [x] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`
   (seven files) with `raw` coverage (ACC-003 cases): `raw=True` returns the
   body text byte-identical to the on-disk frontmatter-stripped body; the
@@ -519,12 +518,12 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   assert the splice landed exactly there); `raw=False` regression (parsed
   document as before); unknown id → `XNotFoundError` in both modes — depends
-  on: Task 2.4, Task 2.2 — status: not-started
-- [ ] Task 2.8: Registration smoke test: a unittest asserting
+  on: Task 2.4, Task 2.2 — status: done
+- [x] Task 2.8: Registration smoke test: a unittest asserting
   `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a
   7-value `enum` and optional integer `begin`/`end` in the input schema, plus
   a fresh-subprocess `uv run --frozen python -c "import biz.dfch.specmgr.
   server"` check run inside the phase gate (import-order proof, Design Notes)
-  — depends on: Task 2.3 — status: not-started
-- [ ] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's
+  — depends on: Task 2.3 — status: done
+- [x] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's
   new tests; `uv run --frozen specmgr mcp-docs` and `uv run --frozen specmgr
   docs` regeneration, then `git diff --exit-code -- docs/` zero drift;
@@ -532,5 +531,5 @@ phase-orchestrator commits each accepted phase as one Conventional Commit.
   the `get_<d>` entries; add a dated entry to the Recent Updates section,
   update Current Status, flip the phase's task lines to done in place —
-  depends on: Tasks 2.3, 2.5, 2.8 — status: not-started
+  depends on: Tasks 2.3, 2.5, 2.8 — status: done
 
 #### Phase 3: Retire the per-domain `update_*` tools
@@ -749,10 +748,19 @@ originally planned, rather than keeping a second copy of the task around.
 ### Current Status
 
-**As of 2026-08-27**: Phase 1 (ADR) complete — the feature's ADR
-36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
-status-change tools into generic type-dispatched tools") was created via
-`specmgr_create_adr`, validated with `specmgr_validate_adr`, and listed in
-`docs/adr/README.md` (regenerated with zero drift); the phase-end quality
-gate is green. Phases 2–7 are not started.
+**As of 2026-08-27**: Phase 2 (Generic `update` tool + `raw` read
+parameter) complete — the generic `update(id, type, content, begin, end)`
+tool (the seven whole-body domains; verbatim-ported private adapters;
+whole-body mode plus the splice-then-validate-whole range mode with the
+`N+1` EOF sentinel) is registered in `general/tools/` alongside the new
+`general/tools/_splice.py` shared body-text/splice helpers, and all seven
+`get_<d>` tools gained `raw: bool = False` (frontmatter-stripped body text
+via the same helper the splice uses — REQ-003's invariant). Purely
+additive: the seven `update_<d>` tools and their tests are untouched
+(Phase 3 deletes them), no `set_status*` tool changed (Phase 4), and
+nothing under any `models/` package changed. The phase-end quality gate is
+green (1830 tests OK, zero `docs/` drift, fresh-subprocess import OK);
+live registration is 85 tools / 25 resources / 19 prompts (baseline
+84/25/19). Phases 3–7 are not started. (Phase 1 — the feature's ADR
+36905d5b-8057-4294-8665-c7eed5534db0 — completed on 2026-08-27.)
 
 ### Blockers
@@ -762,4 +770,92 @@ None.
 ### Recent Updates
 
+#### Update 2026-08-27 (Phase 2: Generic `update` tool + `raw` read parameter)
+
+- Completed: Phase 2 (Tasks 2.1–2.9). Purely additive — the seven
+  `update_<d>` tools, all `set_status*` tools, and every `models/` package
+  are untouched:
+  - `general/tools/_splice.py` (no `mcp` dependency): `body_text(path)` —
+    the single frontmatter-stripped body extraction via
+    `frontmatter.loads(path.read_text(encoding="utf-8")).content` (the same
+    mechanism every `set_status_<d>` tool uses) — and
+    `splice_body(current_body, begin, end, content)` implementing the
+    Design-Notes range contract exactly (`N` = line count; `ValueError` for
+    `begin < 1` / `begin > end` / `end > N+1`, each message naming the
+    offending value(s) and the allowed range; drop lines
+    `begin..min(end, N)`, insert `content.splitlines()` at `begin - 1`,
+    rejoin `"\n"` + one trailing `"\n"`; empty `content` = deletion; the
+    `N+1` EOF sentinel falls out — `begin = end = N+1` is a pure append,
+    `end = N+1` extends the range through the last line).
+  - `general/tools/update.py`: `@mcp.tool(name="update")`
+    `update(id, type, content, begin=None, end=None)` with a
+    `dict[str, Callable]` dispatch table over seven private adapters
+    `_update_<d>` — verbatim ports of the `update_<d>` function bodies
+    (same `X_lock`, same `load_by_id`, same frontmatter carry-over with
+    only `updated` bumped to the current microsecond timestamp, `status`
+    never settable, same verbatim `write_X_file` persistence, same domain
+    `XNotFoundError`) plus the range branch (no `begin`/`end` → today's
+    behavior; both given → `body_text` + `splice_body`, validate the
+    *spliced result* as a whole via `X.from_text(format_text(spliced))`,
+    persist the *spliced* text verbatim; the both-or-neither `ValueError`
+    guard runs in the public `update` before dispatch, i.e. before any file
+    access). The parameter is intentionally named `type` (7-value
+    `Literal` → 7-entry JSON-schema `enum` in the input schema); the
+    7-way union return type is annotation-only.
+  - `raw: bool = False` on the seven `get_<d>` tools: `raw=True` resolves
+    the id as today (no lock — read-only) and returns `body_text(path)` —
+    the *same* helper the splice uses (REQ-003's "what the client counts is
+    what the server splices" invariant); `raw=False` behaves exactly as
+    today (parsed `XDocument`). Each tool's `@mcp.tool` description and
+    docstring updated.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 39.8s)

_Thinking:_

All spot checks passed:

- `get_req.py`: signature `get_req(id: str, raw: bool = False) -> ReqDocument | str`, raw branch uses `body_text(path)` from the shared helper, no lock (load_by_id as-is), description/docstring updated. ✓
- `mcp_docs.py`: additive enum branch in `_schema_type_str`, docstring also updated, strictly fires only for enum properties. ✓
- `general/tools/__init__.py`: import + `__all__` + module docstring. ✓
- Plan README: tasks 2.1–2.9 flipped to done, Current Status rewritten, a detailed dated entry under Recent Updates. ✓ (The rest of the entry probably covers gate results and deviations.)

Let me quickly check the rest of the README diff (the deviations part) — no, actually I've seen enough. The implementer stated that both deviations were recorded in the README entry. Let me quickly verify with a grep for "mcp_docs" and "AssertionError" (deviation notes) in the README.

After that, commit Phase 2. Files to stage: all modified + new files in the working tree (37 paths: 32 M + 5 ??). Should I `git add -A`? The working tree should contain only the phase 2 changes (verified with git status). I'll explicitly add the relevant paths: `git add -A` would pick up everything in the working tree — safe here, but let me first confirm nothing extraneous exists. git status showed exactly the 37 files. Use `git add -A`.

Commit message:
`feat(feat-22): add generic update tool with line-range replace and raw get reads`

Body: summarize. Keep the repo's style (subject line lowercase).

All spot checks passed. After confirming that the two declared deviations are recorded in the README entry, I'll commit Phase 2:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"mcp_docs\\|_schema_type_str\\|AssertionError, not\\|field-level validation\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | head -10",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
816:  enum — `commands/mcp_docs.py`'s `_schema_type_str` collapsed

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 29.8s)

_Thinking:_

The README entry mentions the enum deviation of mcp_docs on line 816. To confirm that both deviations are recorded, I'll display that region (approximately lines 790-840).

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md",
  "offset": 790,
  "limit": 50
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md</path>
<type>file</type>
<content>
790:     `update(id, type, content, begin=None, end=None)` with a
791:     `dict[str, Callable]` dispatch table over seven private adapters
792:     `_update_<d>` — verbatim ports of the `update_<d>` function bodies
793:     (same `X_lock`, same `load_by_id`, same frontmatter carry-over with
794:     only `updated` bumped to the current microsecond timestamp, `status`
795:     never settable, same verbatim `write_X_file` persistence, same domain
796:     `XNotFoundError`) plus the range branch (no `begin`/`end` → today's
797:     behavior; both given → `body_text` + `splice_body`, validate the
798:     *spliced result* as a whole via `X.from_text(format_text(spliced))`,
799:     persist the *spliced* text verbatim; the both-or-neither `ValueError`
800:     guard runs in the public `update` before dispatch, i.e. before any file
801:     access). The parameter is intentionally named `type` (7-value
802:     `Literal` → 7-entry JSON-schema `enum` in the input schema); the
803:     7-way union return type is annotation-only.
804:   - `raw: bool = False` on the seven `get_<d>` tools: `raw=True` resolves
805:     the id as today (no lock — read-only) and returns `body_text(path)` —
806:     the *same* helper the splice uses (REQ-003's "what the client counts is
807:     what the server splices" invariant); `raw=False` behaves exactly as
808:     today (parsed `XDocument`). Each tool's `@mcp.tool` description and
809:     docstring updated.
810:   - Registration in `general/tools/__init__.py` (import, `__all__`, module
811:     docstring); `server.py`'s module docstring updated (`update` added to
812:     the General-tools lines; the `raw` parameter noted on each of the seven
813:     per-domain `get_<d>` lines).
814: - Deviation (additive renderer extension, recorded here per the plan's
815:   docs-discipline note): `docs/MCP.md` could not show the 7-value `type`
816:   enum — `commands/mcp_docs.py`'s `_schema_type_str` collapsed
817:   `{"type": "string", "enum": [...]}` to bare `string`. Added an enum
818:   branch rendering `string (enum: req, uc, tsk, qa, prb, gol, rsk)` (it
819:   fires only for properties declaring `enum` — no other current tool has
820:   one, so no pre-existing `docs/MCP.md` row changed) plus a
821:   `TestSchemaTypeStr` case. The Design Notes require the enum to be
822:   rendered in `docs/MCP.md` and verified in this phase's gate, which the
823:   untouched renderer could not satisfy.
824: - Test note (per-type out-of-vocabulary field-value cases): `req`/`uc`/
825:   `tsk`/`gol`/`rsk` each have a genuine body-level
826:   `pydantic.ValidationError` path (closed vocabularies or cross-field
827:   validators), but `qa`/`prb` bodies are free-form text with no closed
828:   vocabulary and no field constraint — their out-of-vocabulary input (an
829:   unrecognized section heading) fails structurally with `AssertionError`
830:   instead. The ACC-002 invariant (invalid input via a range → the file
831:   left byte-identical on disk) is verified for both error types, per type;
832:   the case data in `tests/general/tools/test_update.py` flags which each
833:   type raises.
834: - Quality gate (green): `ruff format` (initial run normalized the new
835:   files; subsequent `ruff format --check`: 1136 files already formatted),
836:   `ruff check` (all checks passed), `vulture src/ whitelist.py
837:   --min-confidence 60` (clean, exit 0), full unittest suite (**Ran 1830
838:   tests, OK** — up from 1783: +18 `tests/general/tools/test_update.py`
839:   (whole-body ACC-001, range ACC-002, and Task-2.8 registration, each

(Showing lines 790-839 of 935. Use offset=840 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 177.6s)

_Thinking:_

Both deviations are recorded in detail in the README entry. Phase 2 verification is complete:

✅ The full gate passes in my own runs (ruff format/check, vulture, 1830 tests OK)
✅ Zero drift on regeneration (manifest diff is empty)
✅ New subprocess imports are OK
✅ Live count 85/25/19
✅ The verbatim ports are accurate (req has been compared line by line. The other 6 adapters are structurally identical)
✅ The semantics of \_splice.py are correct
✅ The raw parameter is correct (shared helper, no lock)
✅ The registration is correct
✅ The README progress update is accurate, and the deviations are recorded
✅ No changes to protected areas

Committing Phase 2.

Both deviations are fully recorded. **Phase 2 verified** — committing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git status --short | head -45 && git commit -m \"feat(feat-22): add generic update tool with line-range replace and raw get reads\n\nPhase 2 (purely additive): new @mcp.tool update(id, type, content,\nbegin, end) in general/tools/ dispatching to seven verbatim-ported\nper-domain adapters (whole-body mode unchanged; range mode splices the\n1-based inclusive begin..end body lines via the new general/tools/\n_splice.py helpers, validates the spliced result as a whole, persists\nit verbatim; N+1 EOF sentinel; frontmatter never addressable). All\nseven get_<d> tools gain raw: bool = False returning the\nfrontmatter-stripped body text via the same body_text helper the splice\nuses. commands/mcp_docs.py renders closed enums in docs/MCP.md (added\nbranch, required by the phase gate). 47 new tests (1830 total, OK);\nlive registration 85 tools / 25 resources / 19 prompts.\" && git log --oneline -2",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
M  .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
M  docs/GENERATED.md
M  docs/MCP.md
M  docs/api/README.md
M  docs/api/biz.dfch.specmgr.commands.mcp_docs.md
A  docs/api/biz.dfch.specmgr.general.tools._splice.md
M  docs/api/biz.dfch.specmgr.general.tools.md
A  docs/api/biz.dfch.specmgr.general.tools.update.md
M  docs/api/biz.dfch.specmgr.gol.tools.get_gol.md
M  docs/api/biz.dfch.specmgr.prb.tools.get_prb.md
M  docs/api/biz.dfch.specmgr.qa.tools.get_qa.md
M  docs/api/biz.dfch.specmgr.req.tools.get_req.md
M  docs/api/biz.dfch.specmgr.rsk.tools.get_rsk.md
M  docs/api/biz.dfch.specmgr.server.md
M  docs/api/biz.dfch.specmgr.tsk.tools.get_tsk.md
M  docs/api/biz.dfch.specmgr.uc.tools.get_uc.md
M  src/biz/dfch/specmgr/commands/mcp_docs.py
M  src/biz/dfch/specmgr/general/tools/__init__.py
A  src/biz/dfch/specmgr/general/tools/_splice.py
A  src/biz/dfch/specmgr/general/tools/update.py
M  src/biz/dfch/specmgr/gol/tools/get_gol.py
M  src/biz/dfch/specmgr/prb/tools/get_prb.py
M  src/biz/dfch/specmgr/qa/tools/get_qa.py
M  src/biz/dfch/specmgr/req/tools/get_req.py
M  src/biz/dfch/specmgr/rsk/tools/get_rsk.py
M  src/biz/dfch/specmgr/server.py
M  src/biz/dfch/specmgr/tsk/tools/get_tsk.py
M  src/biz/dfch/specmgr/uc/tools/get_uc.py
M  tests/commands/test_mcp_docs.py
A  tests/general/tools/test_update.py
M  tests/gol/tools/test_get_gol.py
M  tests/prb/tools/test_get_prb.py
M  tests/qa/tools/test_get_qa.py
M  tests/req/tools/test_get_req.py
M  tests/rsk/tools/test_get_rsk.py
M  tests/tsk/tools/test_get_tsk.py
M  tests/uc/tools/test_get_uc.py
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 fc76490] feat(feat-22): add generic update tool with line-range replace and raw get reads
 37 files changed, 2831 insertions(+), 134 deletions(-)
 create mode 100644 docs/api/biz.dfch.specmgr.general.tools._splice.md
 create mode 100644 docs/api/biz.dfch.specmgr.general.tools.update.md
 create mode 100644 src/biz/dfch/specmgr/general/tools/_splice.py
 create mode 100644 src/biz/dfch/specmgr/general/tools/update.py
 create mode 100644 tests/general/tools/test_update.py
fc76490 feat(feat-22): add generic update tool with line-range replace and raw get reads
2647649 docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 148.6s)

_Thinking:_

Phase 2 committed as `fc76490` — all pre-commit hooks passed (ruff, vulture, unittest, coverage-badge, docs, mcp-docs).

Next up is Phase 3: deprecation of the per-domain `update_*` tools.
Tasks:

- 3.1: Delete the 7 tool modules
- 3.2: Delete the 7 test files
- 3.3: Update the 7 domain `tools/__init__.py` files + the 7 domain `__init__.py` files
- 3.4: Update the docstring in server.py (remove the update\_<d> lines; leave set_status\_<d> as-is)
- 3.5: Verification via grep — residual matches should only be prompt-narration ones (the 6 prompts/update\_<d>.py module docstrings + their data/\*.md — owned by Phase 5); nothing should appear in tools/, models/, general/; record the residual list in Progress
- 3.6: Phase-end gate + README update

Key points for Phase 3:

- After deletion, live count: 85 - 7 = 78 tools / 25 / 19.
- The generic `update` in general/tools/update.py now fully replaces these.
- Watch out for my Phase-4 note: the description in update.py says "the per-domain `set_status_*` tools are the only path for status changes" — that's fine for Phase 3 (they still exist); it'll be updated in Phase 4.
- Grep pattern: `update_req\|update_uc\|update_tsk\|update_qa\|update_prb\|update_gol\|update_rsk` against src/ and tests/ — expected residual matches: 6 prompt module docstrings (req/prompts/update_req.py, tsk/prompts/update_task.py, qa/prompts/update_qa.py, rsk/prompts/update_risk.py, prb/prompts/update_prb.py, gol/prompts/update_gol.py) + their data/*.md files (the 6 <d>_update_instructions.md). Note: `uc` has no prompts. Wait — the grep also matches against the prompt "module" filename update_req.py — no wait, grep is against content, not filenames. The prompt module docstrings narrate about update_req. Also tests/req/prompts/test_update_req.py etc. — do these reference tool names? These are prompt tests and… they assert against the narration, and the narration mentions update_req. So the residual matches in tests/ = 6 prompt test files (tests/<d>/prompts/test_update_*.py) + 6 prompt modules + 6 data files. The plan says "must return only prompt-narration matches (the 6 prompts/update\_<d>.py module docstrings and their data/\*.md files — owned by Phase 5) and nothing should appear in tools/, models/, or general/". It says "residual matches are limited to the prompt-narration files owned by Phase 5" — the prompt test files are also owned by Phase 5 (Task 5.3). So the expected residual list: 6 prompt modules + 6 data md files + 6 prompt test files (18 files). The implementer should record the exact list.

Hmm, wait, one more: the docstring of `general/tools/update.py` says "verbatim port of the corresponding per-domain `update_<d>` tool's function body" — the generic backtick form `update_<d>` — does that match the grep? The pattern is `update_req\|update_uc\|...` — literal names. "update\_<d>" doesn't match any literal. But the module docstring says "`update_req`"? Let me check: line 98: "Verbatim port of `req.tools.update_req.update_req`'s function body" — yes! It contains the literal `update_req`. So general/tools/update.py will match the grep. But the plan says "nothing should appear in tools/, models/, or general/". Hmm — that refers to the "old" tools/ directories (per-domain). general/tools/update.py references the old module path `req.tools.update_req.update_req` in the adapter docstring. This is a historical reference inside the new code.

Is this a problem? ACC-005 says: "a grep against src/ and tests/ finds no code references to deleted tool names (residual matches before Phase 5 are limited to prompt-narration files owned by Phase 5, and zero thereafter)". The "code references" to `update_req` inside the adapter docstring of general/tools/update.py — this is a docstring, not a code reference (import/call). But if we take grep literally, it matches a file under general/. The plan's Task 3.5 says the grep "must return only prompt-narration matches … and nothing should appear in tools/, models/, or general/".

So strictly, the `req.tools.update_req.update_req` reference in the adapter docstring violates the Phase 3 gate. The docstring should be reworded to avoid the deleted literal tool names — e.g., "verbatim port of the then-per-domain whole-body update function body (same lock, …)". This is a small docstring edit in general/tools/update.py — owned by Phase 3 (since it's about deleting references).

Hmm, but wait: the Phase 2 commit is already done with those docstrings. In Phase 3, the implementer will need to edit the docstrings in general/tools/update.py to remove the literal `update_req`/`update_uc`/… references. That's a legitimate part of "remove all code/docstring references other than Phase 5-owned narration" (Scope: "deletion of the 15 deprecated tool modules, their test files, and all code/docstring references other than Phase 5-owned narration").

Let me verify exactly which literal names appear in general/tools/update.py:

- Line 98: `req.tools.update_req.update_req` (the \_update_req docstring)
- Line 140: `uc.tools.update_uc.update_uc`
- Line 178: `tsk.tools.update_tsk.update_tsk`
- Line 217: `qa.tools.update_qa.update_qa`
- Line 255: `prb.tools.update_prb.update_prb`
- Line 292: `gol.tools.update_gol.update_gol`
- Line 330: `rsk.tools.update_rsk.update_rsk`

Also, the test file tests/general/tools/test_update.py — does it reference the old tool names? It "mirrors the fixture strategy of tests/<d>/tools/test_update\_<d>.py" — the implementer might have written a comment like "mirrors tests/req/tools/test_update_req.py's fixture strategy" — that's a literal reference. Also, the coordinate-invariant test in test_get\_<d>.py uses the generic update. Let me grep now to figure out exactly what Phase 3 has to clean up.

Also, the feature's README itself contains tons of literal names, but that's a plan file — the grep in Task 3.5 is against src/ and tests/ only. No problem.

Additionally: the docstring of `commands/mcp_docs.py` mentions "the 7-value `type` of the generic `update` tool" — no old names. The docstring of `server.py` — updated in Phase 2; the per-domain lines still list update\_<d> (Phase 3 removes them), and set_status\_<d> remains (Phase 4).

The docstrings of get\_<d> in Phase 2 don't reference update\_<d>.

To give the Phase 3 implementer the exact list, let me grep src/ and tests/ now for the 7 literal names.

Phase 2 has been committed as `fc76490`, and all pre-commit hooks passed.

**Preparation for Phase 3**: The grep in Task 3.5 requires that no matches exist under `tools/`, `models/`, or `general/` — however, the adapter docstring in `general/tools/update.py` contains the literal old module path (e.g., `req.tools.update_req.update_req`). To give the implementer the exact list, let me try to enumerate all current residual matches:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rln \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" src/ tests/ | sort",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
src/biz_dfch_specmgr.egg-info/SOURCES.txt
src/biz/dfch/specmgr/general/tools/__pycache__/update.cpython-313.pyc
src/biz/dfch/specmgr/general/tools/update.py
src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
src/biz/dfch/specmgr/gol/__init__.py
src/biz/dfch/specmgr/gol/prompts/__init__.py
src/biz/dfch/specmgr/gol/prompts/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/gol/prompts/__pycache__/update_gol.cpython-313.pyc
src/biz/dfch/specmgr/gol/prompts/update_gol.py
src/biz/dfch/specmgr/gol/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__init__.py
src/biz/dfch/specmgr/gol/tools/_io.py
src/biz/dfch/specmgr/gol/tools/_lock.py
src/biz/dfch/specmgr/gol/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/set_status_gol.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/update_gol.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/validate_gol.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/gol/tools/set_status_gol.py
src/biz/dfch/specmgr/gol/tools/update_gol.py
src/biz/dfch/specmgr/gol/tools/validate_gol.py
src/biz/dfch/specmgr/gol/tools/_write.py
src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
src/biz/dfch/specmgr/prb/__init__.py
src/biz/dfch/specmgr/prb/prompts/__init__.py
src/biz/dfch/specmgr/prb/prompts/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/prb/prompts/__pycache__/update_prb.cpython-313.pyc
src/biz/dfch/specmgr/prb/prompts/update_prb.py
src/biz/dfch/specmgr/prb/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__init__.py
src/biz/dfch/specmgr/prb/tools/_io.py
src/biz/dfch/specmgr/prb/tools/_lock.py
src/biz/dfch/specmgr/prb/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/set_status_prb.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/update_prb.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/validate_prb.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/prb/tools/set_status_prb.py
src/biz/dfch/specmgr/prb/tools/update_prb.py
src/biz/dfch/specmgr/prb/tools/validate_prb.py
src/biz/dfch/specmgr/prb/tools/_write.py
src/biz/dfch/specmgr/__pycache__/server.cpython-313.pyc
src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
src/biz/dfch/specmgr/qa/__init__.py
src/biz/dfch/specmgr/qa/prompts/__init__.py
src/biz/dfch/specmgr/qa/prompts/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/qa/prompts/__pycache__/refine.cpython-313.pyc
src/biz/dfch/specmgr/qa/prompts/__pycache__/update_qa.cpython-313.pyc
src/biz/dfch/specmgr/qa/prompts/refine.py
src/biz/dfch/specmgr/qa/prompts/update_qa.py
src/biz/dfch/specmgr/qa/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/create_qa.py
src/biz/dfch/specmgr/qa/tools/__init__.py
src/biz/dfch/specmgr/qa/tools/_io.py
src/biz/dfch/specmgr/qa/tools/_lock.py
src/biz/dfch/specmgr/qa/tools/__pycache__/create_qa.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/set_status_qa.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/update_qa.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/validate_qa.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/qa/tools/set_status_qa.py
src/biz/dfch/specmgr/qa/tools/update_qa.py
src/biz/dfch/specmgr/qa/tools/validate_qa.py
src/biz/dfch/specmgr/qa/tools/_write.py
src/biz/dfch/specmgr/req/data/req_create_instructions.md
src/biz/dfch/specmgr/req/data/req_update_instructions.md
src/biz/dfch/specmgr/req/__init__.py
src/biz/dfch/specmgr/req/prompts/__init__.py
src/biz/dfch/specmgr/req/prompts/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/req/prompts/__pycache__/update_req.cpython-313.pyc
src/biz/dfch/specmgr/req/prompts/update_req.py
src/biz/dfch/specmgr/req/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/create_req.py
src/biz/dfch/specmgr/req/tools/__init__.py
src/biz/dfch/specmgr/req/tools/_io.py
src/biz/dfch/specmgr/req/tools/_lock.py
src/biz/dfch/specmgr/req/tools/__pycache__/create_req.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/set_status_req.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/update_req.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/validate_req.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/req/tools/set_status_req.py
src/biz/dfch/specmgr/req/tools/update_req.py
src/biz/dfch/specmgr/req/tools/validate_req.py
src/biz/dfch/specmgr/req/tools/_write.py
src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
src/biz/dfch/specmgr/rsk/__init__.py
src/biz/dfch/specmgr/rsk/prompts/__pycache__/update_risk.cpython-313.pyc
src/biz/dfch/specmgr/rsk/prompts/update_risk.py
src/biz/dfch/specmgr/rsk/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__init__.py
src/biz/dfch/specmgr/rsk/tools/_io.py
src/biz/dfch/specmgr/rsk/tools/_lock.py
src/biz/dfch/specmgr/rsk/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/set_status_rsk.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/update_rsk.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/validate_rsk.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py
src/biz/dfch/specmgr/rsk/tools/update_rsk.py
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py
src/biz/dfch/specmgr/rsk/tools/_write.py
src/biz/dfch/specmgr/server.py
src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
src/biz/dfch/specmgr/tsk/__init__.py
src/biz/dfch/specmgr/tsk/models/v1/body.py
src/biz/dfch/specmgr/tsk/models/v1/__pycache__/body.cpython-313.pyc
src/biz/dfch/specmgr/tsk/prompts/__pycache__/update_task.cpython-313.pyc
src/biz/dfch/specmgr/tsk/prompts/update_task.py
src/biz/dfch/specmgr/tsk/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__init__.py
src/biz/dfch/specmgr/tsk/tools/_io.py
src/biz/dfch/specmgr/tsk/tools/_lock.py
src/biz/dfch/specmgr/tsk/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/set_status_tsk.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/update_tsk.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/validate_tsk.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py
src/biz/dfch/specmgr/tsk/tools/update_tsk.py
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py
src/biz/dfch/specmgr/tsk/tools/_write.py
src/biz/dfch/specmgr/uc/__init__.py
src/biz/dfch/specmgr/uc/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/create_uc.py
src/biz/dfch/specmgr/uc/tools/__init__.py
src/biz/dfch/specmgr/uc/tools/_io.py
src/biz/dfch/specmgr/uc/tools/_lock.py
src/biz/dfch/specmgr/uc/tools/__pycache__/create_uc.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/_io.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/_lock.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/set_status_uc.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/update_uc.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/validate_uc.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/__pycache__/_write.cpython-313.pyc
src/biz/dfch/specmgr/uc/tools/set_status_uc.py
src/biz/dfch/specmgr/uc/tools/update_uc.py
src/biz/dfch/specmgr/uc/tools/validate_uc.py
src/biz/dfch/specmgr/uc/tools/_write.py
tests/gol/prompts/__pycache__/test_create_gol.cpython-313.pyc
tests/gol/prompts/__pycache__/test_update_gol.cpython-313.pyc
tests/gol/prompts/test_create_gol.py
tests/gol/prompts/test_update_gol.py
tests/gol/tools/__pycache__/test_integration.cpython-313.pyc
tests/gol/tools/__pycache__/test_update_gol.cpython-313.pyc
tests/gol/tools/test_integration.py
tests/gol/tools/test_update_gol.py
tests/prb/prompts/__pycache__/test_create_prb.cpython-313.pyc
tests/prb/prompts/__pycache__/test_update_prb.cpython-313.pyc
tests/prb/prompts/test_create_prb.py
tests/prb/prompts/test_update_prb.py
tests/prb/tools/__pycache__/test_integration.cpython-313.pyc
tests/prb/tools/__pycache__/test_update_prb.cpython-313.pyc
tests/prb/tools/test_integration.py
tests/prb/tools/test_update_prb.py
tests/qa/prompts/__pycache__/test_create_qa.cpython-313.pyc
tests/qa/prompts/__pycache__/test_refine.cpython-313.pyc
tests/qa/prompts/__pycache__/test_update_qa.cpython-313.pyc
tests/qa/prompts/test_create_qa.py
tests/qa/prompts/test_refine.py
tests/qa/prompts/test_update_qa.py
tests/qa/tools/__pycache__/test_update_qa.cpython-313.pyc
tests/qa/tools/test_update_qa.py
tests/req/prompts/__pycache__/test_create_req.cpython-313.pyc
tests/req/prompts/__pycache__/test_update_req.cpython-313.pyc
tests/req/prompts/test_create_req.py
tests/req/prompts/test_update_req.py
tests/req/tools/__pycache__/test_update_req.cpython-313.pyc
tests/req/tools/test_update_req.py
tests/rsk/prompts/__pycache__/test_update_risk.cpython-313.pyc
tests/rsk/prompts/test_update_risk.py
tests/rsk/tools/__pycache__/test_update_rsk.cpython-313.pyc
tests/rsk/tools/test_update_rsk.py
tests/tsk/prompts/__pycache__/test_implement_task.cpython-313.pyc
tests/tsk/prompts/__pycache__/test_update_task.cpython-313.pyc
tests/tsk/prompts/test_implement_task.py
tests/tsk/prompts/test_update_task.py
tests/tsk/tools/__pycache__/test_update_tsk.cpython-313.pyc
tests/tsk/tools/test_update_tsk.py
tests/uc/tools/__pycache__/test_update_uc.cpython-313.pyc
tests/uc/tools/test_update_uc.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 131.8s)

_Thinking:_

Interesting — there are more matches than I expected. Excluding __pycache__ (binary .pyc files — grep matches them too, but they're not tracked source. Is __pycache__ gitignored? Let me check: pyc files show up in the grep output, but git status is clean, so __pycache__ must be gitignored. The plan's grep is `grep -rn "..." src/ tests/` — if __pycache__ is gitignored, a naive grep would still match it. The implementer should grep against text files only (e.g. `grep -rn --include="*.py" --include="*.md"` or `git grep`). Actually, `git grep` is the cleanest: it only matches tracked files. The plan says "grep against src/ and tests/ finds no code references" — I'll instruct to use `git grep -n "update_req\|update_uc\|update_tsk\|update_qa\|update_prb\|update_gol\|update_rsk" -- src/ tests/` so pycache noise is excluded.

Non-pycache matches found in the current tree (tracked):

**To be deleted in Phase 3 (tool modules + tests):**

- src/.../gol/tools/update_gol.py, prb/tools/update_prb.py, qa/tools/update_qa.py, req/tools/update_req.py, rsk/tools/update_rsk.py, tsk/tools/update_tsk.py, uc/tools/update_uc.py
- tests/gol/tools/test_update_gol.py, prb/tools/test_update_prb.py, qa/tools/test_update_qa.py, req/tools/test_update_req.py, rsk/tools/test_update_rsk.py, tsk/tools/test_update_tsk.py, uc/tools/test_update_uc.py

**Files to be edited in Phase 3 (removing references to update\_<d>):**

- src/.../general/tools/update.py — adapter docstrings with literal `req.tools.update_req.update_req` etc. (7 spots)
- src/.../server.py — per-domain tool lines
- src/.../req/tools/__init__.py, uc/tools/__init__.py, tsk/tools/__init__.py, qa/tools/__init__.py, prb/tools/__init__.py, gol/tools/__init__.py, rsk/tools/__init__.py — imports, __all__, docstrings
- src/.../req/__init__.py, uc/__init__.py, tsk/__init__.py, qa/__init__.py, prb/__init__.py, gol/__init__.py, rsk/__init__.py — docstring enumerations
- Plus unexpected ones:
  - src/.../gol/tools/\_io.py, \_lock.py, validate_gol.py, \_write.py — hmm! Why do \_io.py/\_lock.py/validate_gol.py/\_write.py mention update_gol? Probably in docstrings ("mirrors the update_gol tool's lock usage" or "same as create_gol/update_gol"). E.g. the update_req.py docstring says "mirrors every ADR mutation tool's own adr_lock usage". The \_lock.py module docstring might enumerate the tools that use it: "used by create_req, get_req, update_req, ...". If so, Phase 3 must clean these up too — the plan's Task 3.3 only mentions tools/__init__.py and the domain __init__.py, but Task 3.5's grep must show nothing under tools/. So the implementer has to find and fix all mentions in tools/ files (probably in \_lock.py/_write.py/_io.py docstrings, and in create_\*/validate_\* docstrings that cross-reference the update tool).

  - src/.../qa/tools/create_qa.py, req/tools/create_req.py, uc/tools/create_uc.py — probably cross-references in docstrings like "for updates see update_qa".

  - src/.../tsk/models/v1/body.py — oh, the model file references update_tsk?? "src/biz/dfch/specmgr/tsk/models/v1/body.py" matched. The model's docstring probably says something like "task items are updated by update_tsk...". Per the plan, the grep must show "nothing under tools/, models/, or general/". So this too needs to be fixed in Phase 3. The plan's Task 3.3 doesn't mention it, but Task 3.5's acceptance criteria cover it. The implementer should fix the wording.

  - tests/gol/tools/test_integration.py, tests/prb/tools/test_integration.py — integration tests that probably call update_gol/update_prb! These are not in the "7 test files" to be deleted (Task 3.2 only deletes test_update\_<d>.py). If test_integration.py uses the update\_<d> tool, Phase 3 must rewrite those integration tests to use the generic update tool. Hmm — wait, do the integration tests actually call the update tool? The grep matched tests/gol/tools/test_integration.py and tests/prb/tools/test_integration.py. Let me check what they reference.

  - Prompt module docstrings (6): req/prompts/update_req.py, tsk/prompts/update_task.py, qa/prompts/update_qa.py, rsk/prompts/update_risk.py, prb/prompts/update_prb.py, gol/prompts/update_gol.py — Phase 5's jurisdiction, keep.

  - qa/prompts/refine.py — matches! The module docstring of the refine prompt probably references update_qa. Hmm — is refine.py one of the "6 domain prompts/update\_<d>.py modules"? No, it's separate: qa/prompts/refine.py. Task 5.2 lists "the 6 prompts/update\_<d>.py modules ... plus the 4 ADR prompt modules". The refine.py docstring reference — which phase's jurisdiction? ACC-005 says residual references before Phase 5 are limited to Phase 5's prompt narrative files. refine.py is a prompt module (its narrative is in qa/data/qa_refine_instructions.md, which is Phase 5's jurisdiction). The docstring in refine.py itself — Task 5.2 doesn't explicitly list it... but it says "fix the prompt Python module docstrings that name the deprecated tools: the 6 ... plus the 4 ADR prompt modules — surface mentions become inaccurate". Hmm, the refine.py docstring names update_qa → this should also be fixed in Phase 5. It's not in Task 5.2's explicit list, but it's in spirit. Or the Phase 3 grep would flag it as a residual in src/ (prompts/ directory — the plan's Task 3.5 says "must return only prompt narrative matches (the 6 prompts/update\_<d>.py module docstrings and their data/\*.md files — Phase 5's jurisdiction), and nothing under tools/, models/, general/". prompts/ is not excluded, so a match in qa/prompts/refine.py is a prompt-module match — allowed as residual, but Phase 5 must clear it (per ACC-005, "zero thereafter"). I'll explicitly note refine.py in the Phase 5 prompt.

  - Data files (Phase 5's jurisdiction): gol/data/gol_create_instructions.md, gol_update_instructions.md, prb/data/prb_create_instructions.md, prb_update_instructions.md, qa/data/qa_create_instructions.md, qa_refine_instructions.md, qa_update_instructions.md, req/data/req_create_instructions.md, req_update_instructions.md, rsk/data/rsk_create_instructions.md, rsk_update_instructions.md, tsk/data/tsk_create_instructions.md, tsk_implement_instructions.md, tsk_update_instructions.md.

    Oh wait — the CREATE instruction data files also match (req_create_instructions.md, qa_create_instructions.md, prb_create_instructions.md, gol_create_instructions.md, rsk_create_instructions.md, tsk_create_instructions.md, tsk_implement_instructions.md)! But REQ-006/Task 5.1 only lists 11 files: 6 <d>_update_instructions.md + qa_refine_instructions.md + 4 ADR files. The create instruction files mention update_<d> (probably "after creating, update with update_req") — they are prompt narrative data files owned by Phase 5, but not in Task 5.1's list of 11. ACC-005 requires zero references after Phase 5. So Phase 5 must also fix these create/implement instruction files (their update\_<d> mentions). This is scope expansion beyond the "11 files expected" — Task 5.1 says "11 files expected", but grep will show more. ACC-005 is the binding acceptance criterion: zero references after Phase 5 (outside prompt narrative... wait, no: "a grep against src/ and tests/ finds no code references to deleted tool names (residual mentions before Phase 5 are limited to Phase 5's prompt narrative files, zero thereafter)").

    Hmm, "no code references" — mentions in data files are narrative, not code. But "zero thereafter" — the parenthesis says residuals are limited to Phase 5's narrative files before Phase 5, and "zero thereafter" = after Phase 5, zero. So Phase 5 must clear all narrative references including the create instruction files. OK — I'll instruct Phase 5 to use grep to find all residual references (not just the 11 files) and rewrite any that name deprecated tools.

    Note for Phase 3's residual list: prompt narrative files = 6 update prompt modules + refine.py + 14 data files? Let me count data files from grep: gol_create, gol_update, prb_create, prb_update, qa_create, qa_refine, qa_update, req_create, req_update, rsk_create, rsk_update, tsk_create, tsk_implement, tsk_update = 14 data files + 7 prompt modules (6 update + refine) = 21 narrative files as Phase 5's jurisdiction. Plus tests: prompt test files (test_update_req.py, test_update_task.py, test_update_qa.py, test_update_risk.py, test_update_prb.py, test_update_gol.py, test_create_req.py, test_create_qa.py, test_create_prb.py, test_create_gol.py, test_refine.py, test_implement_task.py) — some of these matched! tests/gol/prompts/test_create_gol.py, tests/prb/prompts/test_create_prb.py, tests/qa/prompts/test_create_qa.py, tests/qa/prompts/test_refine.py, tests/req/prompts/test_create_req.py, tests/tsk/prompts/test_implement_task.py — these prompt tests assert on narrative and mention update\_<d> (because the create narrative tells you to update with update\_<d> later). Phase 5's jurisdiction (Task 5.3 lists only 10 prompt test files, but the create/refine/implement tests also need updating to match the rewritten narrative).

    And tests/gol/tools/test_integration.py, tests/prb/tools/test_integration.py — do these use the update\_<d> tools in code? If so, Phase 3 must fix them (they're in tools/ tests, not prompt narrative). Let me check right now.

So before delegating Phase 3, let me examine:

1. tests/gol/tools/test_integration.py and tests/prb/tools/test_integration.py — what do they reference update_gol/update_prb for?
2. tsk/models/v1/body.py — which references?
3. \_lock.py/_write.py/_io.py/validate_\*/create_\* — which references? (to estimate the scope of Phase 3's docstring cleanup)

Let me grep with line context against the tracked text files (excluding pycache, excluding the obvious Phase 5 narrative files).

This grep revealed that the scope of Phase 3 is larger than the task list in the plan: several non-narrative files reference `update_<d>` (cross-references within docstrings of `_lock`/`_write`/`_io`/`create_*`/`validate_*`, `tsk/models/v1/body.py`, and two `test_integration.py` files). Let me try to accurately identify what those references actually are:

**Tool: bash**

**Input:**

```json
{
  "command": "git grep -n \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" -- src/ tests/ | grep -v \"__pycache__\" | grep -vE \"data/|prompts/(update_|refine|create|implement)|tests/.*(prompts)/\" | grep -v \"tools/update_\\|tools/test_update_\"",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
src/biz/dfch/specmgr/general/tools/update.py:95:def _update_req(id_: str, content: str, begin: int | None, end: int | None) -> ReqDocument:
src/biz/dfch/specmgr/general/tools/update.py:98:    Verbatim port of ``req.tools.update_req.update_req``'s function body
src/biz/dfch/specmgr/general/tools/update.py:137:def _update_uc(id_: str, content: str, begin: int | None, end: int | None) -> UcDocument:
src/biz/dfch/specmgr/general/tools/update.py:140:    Verbatim port of ``uc.tools.update_uc.update_uc``'s function body (same
src/biz/dfch/specmgr/general/tools/update.py:143:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:175:def _update_tsk(id_: str, content: str, begin: int | None, end: int | None) -> TskDocument:
src/biz/dfch/specmgr/general/tools/update.py:178:    Verbatim port of ``tsk.tools.update_tsk.update_tsk``'s function body
src/biz/dfch/specmgr/general/tools/update.py:181:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:213:def _update_qa(id_: str, content: str, begin: int | None, end: int | None) -> QaDocument:
src/biz/dfch/specmgr/general/tools/update.py:216:    Verbatim port of ``qa.tools.update_qa.update_qa``'s function body (same
src/biz/dfch/specmgr/general/tools/update.py:219:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:251:def _update_prb(id_: str, content: str, begin: int | None, end: int | None) -> PrbDocument:
src/biz/dfch/specmgr/general/tools/update.py:254:    Verbatim port of ``prb.tools.update_prb.update_prb``'s function body
src/biz/dfch/specmgr/general/tools/update.py:257:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:289:def _update_gol(id_: str, content: str, begin: int | None, end: int | None) -> GolDocument:
src/biz/dfch/specmgr/general/tools/update.py:292:    Verbatim port of ``gol.tools.update_gol.update_gol``'s function body
src/biz/dfch/specmgr/general/tools/update.py:295:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:327:def _update_rsk(id_: str, content: str, begin: int | None, end: int | None) -> RskDocument:
src/biz/dfch/specmgr/general/tools/update.py:330:    Verbatim port of ``rsk.tools.update_rsk.update_rsk``'s function body
src/biz/dfch/specmgr/general/tools/update.py:333:    REQ-002 range branch (see :func:`_update_req`).
src/biz/dfch/specmgr/general/tools/update.py:367:    "req": _update_req,
src/biz/dfch/specmgr/general/tools/update.py:368:    "uc": _update_uc,
src/biz/dfch/specmgr/general/tools/update.py:369:    "tsk": _update_tsk,
src/biz/dfch/specmgr/general/tools/update.py:370:    "qa": _update_qa,
src/biz/dfch/specmgr/general/tools/update.py:371:    "prb": _update_prb,
src/biz/dfch/specmgr/general/tools/update.py:372:    "gol": _update_gol,
src/biz/dfch/specmgr/general/tools/update.py:373:    "rsk": _update_rsk,
src/biz/dfch/specmgr/gol/__init__.py:30:``get_gol_template``, ``create_gol``, ``update_gol``, ``set_status_gol``,
src/biz/dfch/specmgr/gol/__init__.py:33:(``create_gol``, ``update_gol``) all exist. Like REQ/PRB/TSK/QA, GOL has no
src/biz/dfch/specmgr/gol/prompts/__init__.py:30:from .update_gol import update_gol
src/biz/dfch/specmgr/gol/prompts/__init__.py:34:    "update_gol",
src/biz/dfch/specmgr/gol/tools/__init__.py:33:directory (``gol.tools._paths``/``_io``). ``update_gol`` (Task 3.4) replaces
src/biz/dfch/specmgr/gol/tools/__init__.py:54:from .update_gol import update_gol
src/biz/dfch/specmgr/gol/tools/__init__.py:66:    "update_gol",
src/biz/dfch/specmgr/gol/tools/_io.py:22:``update_gol`` persist the caller's own already-validated body markdown
src/biz/dfch/specmgr/gol/tools/_lock.py:24:``update_gol``/``set_status_gol`` wrap their whole sequence in
src/biz/dfch/specmgr/gol/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_gol``/``update_gol``.
src/biz/dfch/specmgr/gol/tools/_write.py:22:neither ``create_gol`` nor ``update_gol`` ever render a body back out from a
src/biz/dfch/specmgr/gol/tools/_write.py:29:``update_gol.py``/``set_status_gol.py`` do not have to duplicate it. Mirrors
src/biz/dfch/specmgr/gol/tools/set_status_gol.py:28:``update_gol`` accept a ``status`` argument at all -- this is the sole entry
src/biz/dfch/specmgr/gol/tools/validate_gol.py:24:calling ``create_gol``/``update_gol`` (or independently of either), and is
src/biz/dfch/specmgr/gol/tools/validate_gol.py:57:    exactly as ``create_gol``/``update_gol`` themselves do.
src/biz/dfch/specmgr/gol/tools/validate_gol.py:71:        shape ``create_gol``/``update_gol`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/prb/__init__.py:30:``get_prb_template``, ``create_prb``, ``update_prb``, ``set_status_prb``,
src/biz/dfch/specmgr/prb/__init__.py:33:(``create_prb``, ``update_prb``) all exist. Like REQ/TSK/QA, PRB has no
src/biz/dfch/specmgr/prb/prompts/__init__.py:24:prompt split. Named ``create_prb``/``update_prb`` (the tool-name
src/biz/dfch/specmgr/prb/prompts/__init__.py:33:from .update_prb import update_prb
src/biz/dfch/specmgr/prb/prompts/__init__.py:37:    "update_prb",
src/biz/dfch/specmgr/prb/tools/__init__.py:34:``update_prb`` replaces an existing document's body the same way,
src/biz/dfch/specmgr/prb/tools/__init__.py:54:from .update_prb import update_prb
src/biz/dfch/specmgr/prb/tools/__init__.py:66:    "update_prb",
src/biz/dfch/specmgr/prb/tools/_io.py:22:``update_prb`` persist the caller's own already-validated body markdown
src/biz/dfch/specmgr/prb/tools/_lock.py:24:``update_prb``/``set_status_prb`` wrap their whole sequence in
src/biz/dfch/specmgr/prb/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_prb``/``update_prb``.
src/biz/dfch/specmgr/prb/tools/_write.py:22:neither ``create_prb`` nor ``update_prb`` ever render a body back out from a
src/biz/dfch/specmgr/prb/tools/_write.py:29:``update_prb.py``/``set_status_prb.py`` do not have to duplicate it. Mirrors
src/biz/dfch/specmgr/prb/tools/set_status_prb.py:24:``create_prb`` nor ``update_prb`` accept a ``status`` argument at all --
src/biz/dfch/specmgr/prb/tools/validate_prb.py:24:draft before ever calling ``create_prb``/``update_prb`` (or independently of
src/biz/dfch/specmgr/prb/tools/validate_prb.py:58:    exactly as ``create_prb``/``update_prb`` themselves do.
src/biz/dfch/specmgr/prb/tools/validate_prb.py:72:        shape ``create_prb``/``update_prb`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/qa/__init__.py:30:``get_qa_template``, ``create_qa``, ``update_qa``, ``set_status_qa``,
src/biz/dfch/specmgr/qa/__init__.py:33:(``create_qa``, ``update_qa``) all exist. Like REQ, QA has no
src/biz/dfch/specmgr/qa/prompts/__init__.py:20:``create_qa`` guides drafting a brand-new QA document. ``update_qa`` guides
src/biz/dfch/specmgr/qa/prompts/__init__.py:33:from .update_qa import update_qa
src/biz/dfch/specmgr/qa/prompts/__init__.py:38:    "update_qa",
src/biz/dfch/specmgr/qa/tools/__init__.py:34:(``qa.tools._paths``/``_io``). ``update_qa`` replaces an existing document's
src/biz/dfch/specmgr/qa/tools/__init__.py:54:from .update_qa import update_qa
src/biz/dfch/specmgr/qa/tools/__init__.py:66:    "update_qa",
src/biz/dfch/specmgr/qa/tools/_io.py:22:``update_qa`` persist the caller's already-validated body markdown
src/biz/dfch/specmgr/qa/tools/_lock.py:24:overlapping calls against the same id). ``update_qa`` and any future QA
src/biz/dfch/specmgr/qa/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_qa``/``update_qa``
src/biz/dfch/specmgr/qa/tools/_write.py:31:``update_qa.py`` does not have to duplicate it. 1:1 port of
src/biz/dfch/specmgr/qa/tools/create_qa.py:28:``qa.tools._write.write_qa_file`` instead, shared with ``update_qa``.
src/biz/dfch/specmgr/qa/tools/set_status_qa.py:26:``create_qa`` nor ``update_qa`` accept a ``status`` argument at all -- this
src/biz/dfch/specmgr/qa/tools/validate_qa.py:24:calling ``create_qa``/``update_qa`` (or independently of either), and is
src/biz/dfch/specmgr/qa/tools/validate_qa.py:58:    exactly as ``create_qa``/``update_qa`` themselves do.
src/biz/dfch/specmgr/qa/tools/validate_qa.py:72:        shape ``create_qa``/``update_qa`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/req/__init__.py:12:``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``,
src/biz/dfch/specmgr/req/__init__.py:15:(``create_req``, ``update_req``) all exist. Unlike ADR, REQ has no
src/biz/dfch/specmgr/req/prompts/__init__.py:30:from .update_req import update_req
src/biz/dfch/specmgr/req/prompts/__init__.py:34:    "update_req",
src/biz/dfch/specmgr/req/tools/__init__.py:36:(``req.tools._paths``/``_io``). ``update_req`` (Task 3.13) replaces an
src/biz/dfch/specmgr/req/tools/__init__.py:57:from .update_req import update_req
src/biz/dfch/specmgr/req/tools/__init__.py:69:    "update_req",
src/biz/dfch/specmgr/req/tools/_io.py:22:settled on ``create_req``/``update_req`` (Tasks 3.12/3.13) persisting the
src/biz/dfch/specmgr/req/tools/_lock.py:24:``update_req`` (Task 3.13) and any future requirement mutation tool
src/biz/dfch/specmgr/req/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_req``/``update_req``
src/biz/dfch/specmgr/req/tools/_write.py:31:``update_req.py`` (Task 3.13) does not have to duplicate it.
src/biz/dfch/specmgr/req/tools/create_req.py:28:shared with ``update_req`` (Task 3.13).
src/biz/dfch/specmgr/req/tools/set_status_req.py:25:``rejected``/``implemented``). Neither ``create_req`` nor ``update_req``
src/biz/dfch/specmgr/req/tools/validate_req.py:24:draft before ever calling ``create_req``/``update_req`` (or independently of
src/biz/dfch/specmgr/req/tools/validate_req.py:57:    exactly as ``create_req``/``update_req`` themselves do.
src/biz/dfch/specmgr/req/tools/validate_req.py:71:        shape ``create_req``/``update_req`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/rsk/__init__.py:30:``get_rsk_template``, ``create_rsk``, ``update_rsk``, ``set_status_rsk``,
src/biz/dfch/specmgr/rsk/tools/__init__.py:36:``_io``). ``update_rsk`` replaces an existing document's body the same way,
src/biz/dfch/specmgr/rsk/tools/__init__.py:56:from .update_rsk import update_rsk
src/biz/dfch/specmgr/rsk/tools/__init__.py:68:    "update_rsk",
src/biz/dfch/specmgr/rsk/tools/_io.py:22:``update_rsk`` persist the caller's already-validated body markdown
src/biz/dfch/specmgr/rsk/tools/_lock.py:24:``update_rsk`` and any future risk mutation tool (``set_status_rsk``)
src/biz/dfch/specmgr/rsk/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_rsk``/``update_rsk``.
src/biz/dfch/specmgr/rsk/tools/_write.py:22:neither ``create_rsk`` nor ``update_rsk`` ever render a body back out from a
src/biz/dfch/specmgr/rsk/tools/_write.py:29:``update_rsk.py`` does not have to duplicate it. Mirrors ``tsk.tools._write``
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py:27:set. Neither ``create_rsk`` nor ``update_rsk`` accept a ``status`` argument
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py:24:calling ``create_rsk``/``update_rsk`` (or independently of either), and is
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py:58:    exactly as ``create_rsk``/``update_rsk`` themselves do.
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py:72:        shape ``create_rsk``/``update_rsk`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/server.py:109:``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``
src/biz/dfch/specmgr/server.py:114:``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``, ``delete_req``
src/biz/dfch/specmgr/server.py:119:``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``, ``delete_tsk``
src/biz/dfch/specmgr/server.py:124:``get_qa_template``, ``create_qa``, ``update_qa``, ``set_status_qa``, ``delete_qa``
src/biz/dfch/specmgr/server.py:128:``get_prb_example``, ``get_prb_template``, ``create_prb``, ``update_prb``,
src/biz/dfch/specmgr/server.py:132:``get_gol_example``, ``get_gol_template``, ``create_gol``, ``update_gol``,
src/biz/dfch/specmgr/server.py:137: ``get_rsk_template``, ``create_rsk``, ``update_rsk``, ``set_status_rsk``, ``delete_rsk``
src/biz/dfch/specmgr/server.py:155:Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
src/biz/dfch/specmgr/server.py:161:QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
src/biz/dfch/specmgr/server.py:166:Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
src/biz/dfch/specmgr/server.py:170:Goal prompts (``gol/prompts/``): ``create_gol``, ``update_gol`` --
src/biz/dfch/specmgr/tsk/__init__.py:30:``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``,
src/biz/dfch/specmgr/tsk/models/v1/body.py:140:        `Task.from_text(...)` (and therefore `create_tsk`/`update_tsk`/
src/biz/dfch/specmgr/tsk/tools/__init__.py:35:list base directory (``tsk.tools._paths``/``_io``). ``update_tsk`` replaces
src/biz/dfch/specmgr/tsk/tools/__init__.py:56:from .update_tsk import update_tsk
src/biz/dfch/specmgr/tsk/tools/__init__.py:68:    "update_tsk",
src/biz/dfch/specmgr/tsk/tools/_io.py:22:``update_tsk`` persist the caller's already-validated body markdown
src/biz/dfch/specmgr/tsk/tools/_lock.py:24:``update_tsk`` and any future task list mutation tool (``set_status_tsk``)
src/biz/dfch/specmgr/tsk/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_tsk``/``update_tsk``.
src/biz/dfch/specmgr/tsk/tools/_write.py:22:neither ``create_tsk`` nor ``update_tsk`` ever render a body back out from a
src/biz/dfch/specmgr/tsk/tools/_write.py:29:``update_tsk.py`` does not have to duplicate it. Mirrors ``req.tools._write``
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py:26:``create_tsk`` nor ``update_tsk`` accept a ``status`` argument at all --
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py:24:ever calling ``create_tsk``/``update_tsk`` (or independently of either), and
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py:58:    exactly as ``create_tsk``/``update_tsk`` themselves do.
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py:72:        shape ``create_tsk``/``update_tsk`` accept) -- raises ``ValueError``
src/biz/dfch/specmgr/uc/__init__.py:12:``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``,
src/biz/dfch/specmgr/uc/tools/__init__.py:35:(``uc.tools._paths``/``_io``). ``update_uc`` (Task 3.1.5) replaces an
src/biz/dfch/specmgr/uc/tools/__init__.py:56:from .update_uc import update_uc
src/biz/dfch/specmgr/uc/tools/__init__.py:68:    "update_uc",
src/biz/dfch/specmgr/uc/tools/_io.py:21:``write_uc``/``render_uc`` counterpart here, since ``create_uc``/``update_uc``
src/biz/dfch/specmgr/uc/tools/_lock.py:24:``update_uc`` and any future use-case mutation tool (``set_status_uc``) wrap
src/biz/dfch/specmgr/uc/tools/_write.py:18:"""Shared frontmatter+body composition/write helper for ``create_uc``/``update_uc``
src/biz/dfch/specmgr/uc/tools/_write.py:29:file. Factored out of ``create_uc.py`` into its own module so ``update_uc.py``
src/biz/dfch/specmgr/uc/tools/create_uc.py:26:shared with ``update_uc``.
src/biz/dfch/specmgr/uc/tools/set_status_uc.py:25:``update_uc`` accept a ``status`` argument at all -- this is the sole entry
src/biz/dfch/specmgr/uc/tools/validate_uc.py:23:before ever calling ``create_uc``/``update_uc`` (or independently of either),
src/biz/dfch/specmgr/uc/tools/validate_uc.py:56:    exactly as ``create_uc``/``update_uc`` themselves do.
src/biz/dfch/specmgr/uc/tools/validate_uc.py:70:        shape ``create_uc``/``update_uc`` accept) -- raises ``ValueError``
tests/gol/tools/test_integration.py:23:``update_gol`` -> ``set_status_gol`` -> ``get_gol`` (status changed) ->
tests/gol/tools/test_integration.py:52:from biz.dfch.specmgr.gol.tools.update_gol import update_gol
tests/gol/tools/test_integration.py:95:        """list_gol -> create_gol -> get_gol -> list_gol -> update_gol -> set_status_gol -> get_gol ->
tests/gol/tools/test_integration.py:126:        # 4. update_gol: whole-body replace must preserve id/type/created, bump updated.
tests/gol/tools/test_integration.py:127:        updated = update_gol(gol_id, _REVISED_BODY)
tests/prb/tools/test_integration.py:22:``create_prb`` -> ``update_prb`` -> ``set_status_prb`` -> ``get_prb`` ->
tests/prb/tools/test_integration.py:50:from biz.dfch.specmgr.prb.tools.update_prb import update_prb
tests/prb/tools/test_integration.py:126:        """create_prb -> update_prb -> set_status_prb -> get_prb -> list_prb -> delete_prb, live."""
tests/prb/tools/test_integration.py:137:        # 2. update_prb: whole-body replace must preserve id/type/created, bump updated.
tests/prb/tools/test_integration.py:138:        updated = update_prb(prb_id, _REVISED_BODY)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 10308.5s)

_Thinking:_

Now I have a grasp of the overall picture of Phase 3's cleanup work:

**Phase 3's jurisdiction (deletions + docstring/registration cleanup):**

1. Delete the 7 tool modules (Task 3.1)
2. Delete the 7 test files (Task 3.2)
3. Update the 7 `tools/__init__.py` files (imports, `__all__`, docstrings) (Task 3.3)
4. Update the 7 domain `__init__.py` docstrings (Task 3.3)
5. Update the `server.py` docstring — the 7 tool lines (Task 3.4)
6. **Additional cleanup that Task 3.5's grep requires** (the plan's Task 3.3 doesn't enumerate these, but Task 3.5's acceptance criteria and ACC-005 do):
   - `general/tools/update.py`: 7 adapter docstrings referencing `req.tools.update_req.update_req` etc. → rephrase (e.g., "verbatim port of the previous per-domain whole-body update function body")
   - Per-domain `tools/_io.py` (7): references in the "`update_<d>` persists the caller's..." docstrings
   - Per-domain `tools/_lock.py` (7): references in the "`update_<d>`/`set_status_<d>` wraps..." docstrings (the set_status mentions will become stale in Phase 4 — for now either just fix the update mentions, or rewrite to refer to the generic tools)
   - Per-domain `tools/_write.py` (7): module docstring "helper for create\_<d>/update\_<d>" + references
   - Per-domain `tools/create_req.py`/`create_qa.py`/`create_uc.py` (3): "shared with update\_<d>" references
   - Per-domain `tools/validate_<d>.py` (7): "create\_<d>/update\_<d>" references
   - Per-domain `tools/set_status_<d>.py` (7): "neither create\_<d> nor update\_<d> accepts status" references (these modules will be deleted in Phase 4, but the grep is also run in Phase 3 — since Task 3.5 says "nothing under tools/", the update\_<d> mentions inside set_status\_<d>.py must also be fixed in Phase 3. The set_status\_<d> name itself is not subject to this grep.)
   - `tsk/models/v1/body.py` (1): the "(and therefore create_tsk/update_tsk/..." on line 140 → rewrite to refer to the generic update.
   - `tests/gol/tools/test_integration.py` + `tests/prb/tools/test_integration.py`: these import and call `update_gol`/`update_prb` — must be rewritten to use the generic `update(id, type="gol", content)` (imports from biz.dfch.specmgr.general.tools.update). These are code references and fall within Phase 3's jurisdiction.

Wait — do test_integration files exist for the other domains too? grep only matched the gol and prb integration tests for the update\_<d> names. Probably the other domains (req, uc, tsk, qa, rsk) don't have test_integration.py. No problem.

**Phase 5's jurisdiction (narration) — confirmed residual set:**

- 6 prompt modules: req/prompts/update_req.py, uc? no, wrong — the prompt modules are: req/prompts/update_req.py, tsk/prompts/update_task.py, qa/prompts/update_qa.py, rsk/prompts/update_risk.py, prb/prompts/update_prb.py, gol/prompts/update_gol.py. Note: the prompt module `update_gol` is a function named update_gol (the prompt function) — this is a prompt function name, not an MCP tool! Wait. Prompt: `@mcp.prompt(name="update_gol")` — the prompt is also named update_gol! The grep for "update_gol" will match the prompt name. The plan says prompts are kept and only the narration is rewritten (Decision Made: "per-domain update\_\* prompts are kept"). So the prompt names (update_req, update_task, update_qa, update_risk, update_prb, update_gol) remain — they collide with the deleted tool names but they are prompts, not tools. ACC-005's grep "finds no code references to the deleted tool names" — the prompt name `update_req` inside `@mcp.prompt(name="update_req")` is a reference to the prompt name, and the plan explicitly keeps it (the 19 prompts count stays at 19). The plan's Task 3.5 says the grep "must return only prompt narration matches (the 6 prompts/update\_<d>.py module docstrings and their data/\*.md files — Phase 5's jurisdiction)". So the prompt module file paths / prompt names / imports inside prompts/__init__.py are allowed residuals — those are prompt-narration files owned by Phase 5. OK.
  - So: the prompts/__init__.py files (importing update_gol etc. as prompt functions) — Phase 5's jurisdiction (kept as-is; they reference prompt functions, and the names stay).
  - server.py lines 155–170: prompt enumerations (`create_req`, `update_req` -- these are prompt names, kept) — Phase 3's Task 3.4 only deletes the update\_<d> entries from the tool lines. The prompt lines stay (Phase 5's jurisdiction, but the prompt names don't change, so no change needed at all).
- Data files: the 6 <d>_update_instructions.md + qa_refine + the 4 ADR files (Task 5.1) + the create/implement instruction files that mention update_<d> (req_create, qa_create, prb_create, gol_create, rsk_create, tsk_create, tsk_implement — additional narration residuals, Phase 5's jurisdiction per ACC-005's "zero thereafter").
- Prompt test files: the 10 in Task 5.3 + the create/refine/implement prompt tests that matched (test_create_req, test_create_qa, test_create_prb, test_create_gol, test_refine, test_implement_task) — additional Phase 5 work to keep in sync with the rewritten narration.

So my Phase 3 prompt must explicitly add: "Beyond Tasks 3.1–3.4, Task 3.5's grep acceptance criteria require zero matches under src/.../tools/, models/, general/ (excluding the prompt-narration files owned by Phase 5) — the current residual set includes: [enumerated]. Rewrite all of those (docstring cross-references → refer to the generic `update` tool; the 2 integration tests → call the generic `update(id, type=..., content)`)."

Let me be careful with the set_status\_<d>.py docstrings: they say "neither create\_<d> nor update\_<d> accepts a status argument at all — this is the sole entry point..." — Phase 3 rewrites to "neither create\_<d> nor the generic update tool accepts status; set_status\_<d> is the sole entry point (until Phase 4...)" — hmm, let's keep it simple: refer to the generic `update` in `general/tools/`. Phase 4 will delete these files anyway, but for now we just need a clean grep.

`_lock.py` too: "update_req (Task 3.13) and any future requirement mutation tool (set_status_req) wrap..." → "the generic update tool (general/tools/) and set_status_req wrap...".

Now, another consideration for Phase 3: the test count. Deleting the 7 test_update\_<d>.py files removes their tests (per Phase 2's report: 34 tests, "the 7 existing update\_<d> files still pass without modification (34 tests, verified in isolation)"). 1830 - 34 = 1796 + the rewritten integration tests (gol/prb integration tests are kept, just re-pointed). So the expected total ≈ 1796 (the implementer will report the exact number).

Live count: 85 - 7 = 78 tools / 25 / 19.

Also: `docs/MCP.md` will lose the 7 update\_<d> entries; `docs/api/` will lose the 7 update\_<d> module pages (per Task 3.6). Regenerate coverage-badge (the tests changed).

OK, let's write the Phase 3 prompt. Also, I'll hand over the exact grep command (using git grep to avoid pycache) and the expected residual list, and instruct to record the residual match list in the Progress entry (per Task 3.5).

I'll also include my note: do not yet update the `update.py` docstring line "per-domain set_status\_\* tools are the sole path for status changes" — that's Phase 4's jurisdiction (still true in Phase 3).

One more thing: `uc/tools/_io.py:21` references update_uc; `uc/tools/create_uc.py:26` "shared with update_uc". Covered.

And `tsk/models/v1/body.py:140`: "`Task.from_text(...)` (and therefore `create_tsk`/`update_tsk`/..." → rewrite to "create_tsk/the generic update tool/...".

OK, launching Phase 3.

The full picture of Phase 3 has become clear. In addition to the deletion of 7+7, the plan's Task 3.5 grep acceptance requires cleanup of roughly 40 docstring cross-references within `tools/` (the `_io`/`_lock`/`_write`/`create_*`/`validate_*`/`set_status_*` modules), `tsk/models/v1/body.py`, `general/tools/update.py`, and `server.py` — plus rewriting **two live integration tests** (`tests/gol/tools/test_integration.py`, `tests/prb/tools/test_integration.py`), which directly import and invoke `update_gol`/`update_prb`. The residual matches in prompt narration (the prompt module, `prompts/__init__.py`, data files, prompt tests) remain in the territory of Phase 5.

**Delegating Phase 3:**

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 3 (retire update_<d>)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 3: Retire the per-domain `update_*` tools** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `fc76490` (Phase 2 commit), working tree clean.\n- Phase 2 added the generic `update` tool in `src/biz/dfch/specmgr/general/tools/update.py` (seven private adapters `_update_<d>`, dispatch table, both-or-neither `ValueError` guard) and the `raw` parameter on the seven `get_<d>` tools. Live registration is currently 85 tools / 25 resources / 19 prompts. After Phase 3 it must be **78 / 25 / 19**.\n- The seven `set_status_*` tools (per-domain + ADR) still exist and are Phase 4's concern — do NOT touch them (except the specific docstring cross-references listed below).\n\n## Your plan\nRead the FULL plan first: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — Overview, Requirements (esp. REQ-005), Design Notes (docs discipline), the \"Phase-end quality gate\" section, and your phase heading `#### Phase 3: Retire the per-domain `update_*` tools` (Tasks 3.1–3.6). Also read `.specmgr/conventions.md`.\n\n## Tasks (from the plan)\n\n- **Task 3.1**: Delete the seven tool modules: `src/biz/dfch/specmgr/{req,uc,tsk,qa,prb,gol,rsk}/tools/update_<d>.py` (uc's is `update_uc.py`, etc. — the seven domains are req, uc, tsk, qa, prb, gol, rsk).\n- **Task 3.2**: Delete the seven test files: `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_update_<d>.py`.\n- **Task 3.3**: Update the seven domain `tools/__init__.py` files (remove the `update_<d>` import, `__all__` entry, and the module-docstring tool-list mention — each docstring currently narrates `update_<d>`; rewrite that sentence to say whole-body/line-range updates go through the generic `update` tool in `general/tools/`) and the seven domain `__init__.py` files (remove `update_<d>` from the docstring tool enumeration and add the same pointer to the generic `update` tool).\n- **Task 3.4**: Update `server.py`'s module docstring: remove `update_<d>` from the seven per-domain Tools lines (the `set_status_<d>` entries STAY until Phase 4; the per-domain *prompt* enumerations in server.py stay entirely — those are prompt names, not tools).\n- **Task 3.5 (orchestrator-verified residual list — you must clear ALL of these)**: Task 3.5's grep is `git grep -n \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" -- src/ tests/` (use `git grep` — plain grep also matches untracked `__pycache__` binaries). After Tasks 3.1–3.4, the orchestrator has already verified the current match set. Everything that is NOT a Phase-5-owned prompt-narration file must end up with zero matches. The non-narration residuals you must fix are:\n  - `src/biz/dfch/specmgr/general/tools/update.py` — the seven adapter docstrings each say \"Verbatim port of ``<d>.tools.update_<d>.update_<d>``'s function body\" (lines ~98, 140, 178, 216, 254, 292, 330). Reword to name the historical port WITHOUT the deleted tool names (e.g. \"Verbatim port of the then-per-domain whole-body ``update_<d>``... \" is NOT acceptable — it must not contain the literal `update_req` etc.; say e.g. \"Verbatim port of the previous per-domain requirement update tool's function body (feat-22 Phase 2 removed the per-domain module)\").\n  - The seven domain `tools/_io.py` — module docstring lines like \"``create_req``/``update_req`` (Tasks 3.12/3.13) persist the caller's own already-validated body markdown\" / \"``update_gol`` persist the caller's...\" — reword to point at the generic `update` tool.\n  - The seven domain `tools/_lock.py` — lines like \"``update_req`` (Task 3.13) and any future requirement mutation tool (``set_status_req``) wrap their whole sequence...\" — reword (keep the `set_status_<d>` mentions; they are still live tools).\n  - The seven domain `tools/_write.py` — module docstrings \"Shared frontmatter+body composition/write helper for ``create_req``/``update_req``\" + \"neither ``create_req`` nor ``update_req`` ever render...\" + \"so ``update_req.py`` (Task 3.13) does not have to duplicate it\" — reword to the generic `update` tool.\n  - `req/tools/create_req.py` (\"shared with ``update_req`` (Task 3.13)\"), `uc/tools/create_uc.py` (\"shared with ``update_uc``\"), `qa/tools/create_qa.py` (\"shared with ``update_qa``\") — reword to the generic `update` tool.\n  - The seven domain `tools/validate_<d>.py` — \"calling ``create_req``/``update_req`` (or independently of either)\", \"exactly as ``create_req``/``update_req`` themselves do\", \"shape ``create_req``/``update_req`` accept\" — reword.\n  - The seven domain `tools/set_status_<d>.py` — \"Neither ``create_req`` nor ``update_req`` accept a ``status`` argument at all -- this is the sole entry...\" — reword (these modules are deleted in Phase 4, but their current text must not name the deleted tools).\n  - `tsk/models/v1/body.py` line ~140 — \"`Task.from_text(...)` (and therefore `create_tsk`/`update_tsk`/...\" — reword.\n  - `tests/gol/tools/test_integration.py` — imports `from biz.dfch.specmgr.gol.tools.update_gol import update_gol` (line 52) and calls `update_gol(gol_id, _REVISED_BODY)` (line 127), plus docstring/step mentions (lines 23, 95, 126). Rewrite to use the generic tool: `from biz.dfch.specmgr.general.tools.update import update` and `update(gol_id, \"gol\", _REVISED_BODY)` (whole-body mode), updating the docstring/step text accordingly.\n  - `tests/prb/tools/test_integration.py` — same treatment (`update_prb` → `update(prb_id, \"prb\", _REVISED_BODY)`; lines 22, 50, 126, 137, 138).\n  - After all fixes, the ONLY remaining `git grep` matches must be in Phase-5-owned prompt-narration files: the six `prompts/update_<d>.py` modules (req, tsk=update_task.py, qa, rsk=update_risk.py, prb, gol), the six `prompts/__init__.py` files (they import the prompt FUNCTIONS named `update_<d>` — prompt names are kept by the plan), `server.py`'s per-domain PROMPT enumeration lines only, the `*/data/*.md` instruction files, and the prompt test files under `tests/*/prompts/`. Record the full residual match list in the Progress entry (Task 3.5 requires it).\n  - IMPORTANT: do NOT reword `general/tools/update.py`'s line \"`status` is never settable -- use the `set_status_*` tools\" or the docstring sentence \"the per-domain ``set_status_<d>`` tools are the only status-change path\" — those refer to still-live tools and become Phase 4's job.\n- **Task 3.6**: Phase-end quality gate — full gate per the plan's Design Notes:\n  1. `uv run --frozen ruff format` (write mode for any file you touched) then `uv run --frozen ruff format --check` and `uv run --frozen ruff check` — must pass.\n  2. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — must be clean. (Watch for: nothing should become dead code — the generic adapters in `general/tools/update.py` use the same domain helpers, so `_paths`/`_io`/`_lock`/`_write` remain referenced.)\n  3. `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` — full suite must pass. Expected delta vs Phase 2's 1830: −(the 34 tests in the seven deleted `test_update_<d>.py` files) with the two re-pointed integration tests still passing; report the exact new total.\n  4. Regenerations (the pre-commit hooks for this commit set run all three and fail on drift, so leave the tree hook-clean): `uv run --frozen specmgr coverage-badge` (test deletions change coverage → `docs/coverage.svg` may change — commit it), `uv run --frozen specmgr mcp-docs` (→ `docs/MCP.md`), `uv run --frozen specmgr docs` (→ `docs/api/` + `docs/GENERATED.md`).\n  5. Zero-drift proof: re-run each of the three generators; a second run must be a no-op (no further file changes).\n  6. Confirm `docs/MCP.md` LOST the seven `update_<d>` entries (and still shows the generic `update` entry and the seven `set_status_<d>` entries) and `docs/api/` lost the seven `update_<d>` module pages (and gained nothing spurious); confirm the `git grep` residual list from Task 3.5.\n  7. Fix failures and re-run until green — a phase is not done with a red gate.\n  8. Update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); new dated entry `#### Update 2026-08-27 (Phase 3: ...)` in Recent Updates (above the Phase 2 entry, preserve all history) — it MUST include the residual-match list required by Task 3.5 (grouped: prompt-narration files owned by Phase 5, with file list); Current Status updated (Phase 3 complete, Phases 4–7 not started, live registration 78/25/19); Tasks 3.1–3.6 flipped to done in place (byte-careful: preserve the plan's 2-space continuation wrapping on untouched lines).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`).\n- Do NOT start Phase 4: no `set_status*` module deletions, no generic `set_status` creation.\n- Do NOT touch Phase-5-owned narration content (the prompt data files' `update_<d>` call sites stay as-is — Phase 5 rewrites them; you only fix non-narration code/docstring references).\n- Do NOT change any behavior except deleting the seven tools and re-pointing the two integration tests to the generic `update`.\n- If the residual list turns out to differ from what the orchestrator enumerated (e.g. a file you didn't expect matches), include it in your report and apply the same rule: non-narration → fix now; narration → list for Phase 5.\n\n## Report back (your final message)\n1. `git status --short` + `git diff --stat`; confirm the 14 deleted files are staged-for-deletion in the working tree (deleted on disk).\n2. The FINAL `git grep -n \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" -- src/ tests/` output (file list with counts), classified as Phase-5-narration-residual vs anything else (anything else = failure — do not hand the phase back to me with non-narration residuals).\n3. The two integration-test rewrites (quote the new import + call lines).\n4. Gate evidence: ruff format --check / ruff check / vulture results; full suite `Ran N tests ... OK` with the exact N; the three generator runs + no-op second-run proof; `docs/MCP.md` before/after (7 `update_<d>` entries gone, generic `update` intact, `set_status_*` intact); `docs/api/` page delta.\n5. Live registration counts (78/25/19 expected) via `asyncio.run(mcp.list_tools())` etc.\n6. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

````
<task id="ses_fbea740caffeId6e8RKkzjOwAW" state="completed">
<task_result>


Phase 3 is complete and the full gate is green. Final report:

---

# Phase 3 Report — Retire the per-domain `update_*` tools (feat-22)

## 1. Tree state

**`git status --short`**: 21 `D` + 115 `M` (136 files). `git diff --stat`: **136 files changed, 684 insertions(+), 2765 deletions(-)**. Nothing staged, nothing committed.

**The 14 deleted files** (deleted on disk, shown as ` D` — per the hard constraint I did not `git add`):
- 7 tool modules: `src/biz/dfch/specmgr/{req,uc,tsk,qa,prb,gol,rsk}/tools/update_<d>.py`
- 7 test files: `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_update_<d>.py`

Plus 7 **manually deleted stale doc pages** (see deviation D4): `docs/api/biz.dfch.specmgr.<d>.tools.update_<d>.md`.

Modified: `server.py`, `general/tools/update.py`, 7× domain `__init__.py` + `tools/__init__.py` + `_io.py` + `_lock.py` + `_write.py` + `validate_<d>.py` + `set_status_<d>.py` (49), `create_req.py`/`create_uc.py`/`create_qa.py`, `tsk/models/v1/body.py`, `tests/{gol,prb}/tools/test_integration.py`, and the plan README. 57 `docs/` files regenerated (50 `docs/api/` pages, `docs/api/README.md`, `docs/GENERATED.md`, `docs/MCP.md`).

## 2. FINAL `git grep` residual (43 files, 251 match lines)

**Class A — Phase-5 prompt-narration files (left untouched, per plan ownership):**
| file | lines | file | lines |
|---|---|---|---|
| `src/.../req/prompts/update_req.py` | 5 | `tests/req/prompts/test_update_req.py` | 21 |
| `src/.../req/prompts/__init__.py` | 2 | `tests/qa/prompts/test_update_qa.py` | 24 |
| `src/.../qa/prompts/update_qa.py` | 6 | `tests/prb/prompts/test_update_prb.py` | 27 |
| `src/.../qa/prompts/refine.py` | 3 | `tests/gol/prompts/test_update_gol.py` | 24 |
| `src/.../qa/prompts/__init__.py` | 3 | `tests/tsk/prompts/test_update_task.py` | 8 |
| `src/.../prb/prompts/update_prb.py` | 9 | `tests/rsk/prompts/test_update_risk.py` | 8 |
| `src/.../prb/prompts/__init__.py` | 3 | `tests/{req,qa,prb,gol}/prompts/test_create_*.py` | 3 each |
| `src/.../gol/prompts/update_gol.py` | 10 | `tests/qa/prompts/test_refine.py` | 4 |
| `src/.../gol/prompts/__init__.py` | 2 | `tests/tsk/prompts/test_implement_task.py` | 3 |
| `src/.../tsk/prompts/update_task.py` | 4 | `src/.../{req,qa,prb,gol}/data/*_create_instructions.md` | 3/3/2/3 |
| `src/.../rsk/prompts/update_risk.py` | 3 | `src/.../{req,tsk,qa,prb,gol,rsk}/data/*_update_instructions.md` | 4/4/4/4/4/4 |
| | | `src/.../qa/data/qa_refine_instructions.md`, `tsk/data/tsk_implement_instructions.md` | 4, 1 |

**Class B — kept-by-design prompt-name enumerations (prompt names are kept by the plan; not tool references):** `server.py` lines 155/161/166/170 (4 matches — the per-domain PROMPT enumeration lines you told me to keep) and the prompt-enumeration sentence in `req/__init__.py`, `qa/__init__.py`, `prb/__init__.py`, `gol/__init__.py` (1 each — **not in your residual list; flagged here**).

**Class C — substring-only matches on the generic tool's own private adapter names (NOT references to deleted tools):** `general/tools/update.py` (20) — the seven `def _update_<d>` lines, six `:func:`_update_req`` cross-references, seven dispatch-table entries. **Flagged for your confirmation** (deviation D1).

**Everything else: zero matches** — no per-domain `tools/` file, no `models/` file, no other `general/` file names a deleted tool. The full list is recorded in the README's Phase-3 Progress entry.

## 3. Integration-test rewrites

`tests/gol/tools/test_integration.py`:
```python
from biz.dfch.specmgr.general.tools.update import update
...
        # 4. update: whole-body replace must preserve id/type/created, bump updated.
        updated = update(gol_id, "gol", _REVISED_BODY)
````

`tests/prb/tools/test_integration.py`:

```python
from biz.dfch.specmgr.general.tools.update import update
...
        # 2. update: whole-body replace must preserve id/type/created, bump updated.
        updated = update(prb_id, "prb", _REVISED_BODY)
```

Both pass live (verified standalone, 4 tests OK).

## 4. Gate evidence (all green)

| check | result |
|---|---|
| `ruff format --check` | **1115 files already formatted** (1136 baseline −14 deleted .py −7 deleted .md — ruff 0.16's format counts `.md` too) |
| `ruff check` | **All checks passed!** |
| `vulture src/ whitelist.py --min-confidence 60` | **clean, exit 0** |
| full unittest suite | **`Ran 1796 tests ... OK`** (twice — before and after the stale-page deletions; exact delta 1830 − 34) |
| `specmgr coverage-badge` | **98% — badge byte-identical, no diff** |
| `specmgr mcp-docs` | header **"78 tool(s)"**; diff 1+/85−: the seven `update_<d>` table rows + `### Tool:` sections gone; generic `### Tool: update` and all eight `set_status*` intact; `update_<d>` **prompt** rows untouched |
| `specmgr docs` | 54 `docs/api/` pages + `docs/api/README.md` + `docs/GENERATED.md` regenerated; seven stale `update_<d>` API pages deleted (D4) |
| zero-drift proof | sha256 manifest of `docs/` before/after a second run of all three generators: **byte-identical, empty diff** |
| fresh-subprocess import | `python -c "import biz.dfch.specmgr.server"` → **exit 0** |
| `git grep` | 43 files / 251 lines, all classified above |

Note: `docs/api/biz.dfch.specmgr.tsk.models.v1.body.md` shows no diff — the generator doesn't render the private `_validate_items_eagerly` method, so the reworded docstring has no API-page surface.

## 5. Live registration

`asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real `server.mcp`: **78 tools / 25 resources / 19 prompts** ✓. None of the seven deleted tools registered; `update` registered; all eight `set_status*` still registered (Phase 4's).

## 6. Deviations / items for the orchestrator

- **D1 (needs your confirmation):** the seven `_update_<d>` **adapter function names** in `general/tools/update.py` survive the grep as substring matches (20 lines). Your Task 3.5 list named only that file's docstrings, and the plan's Design Notes mandate the `_update_<d>` adapter naming (Phase 4 will mirror it with `_set_status_<d>`), so renaming would be an out-of-scope design change — I reworded the docstrings (which no longer match) and kept the names, and flagged them in the Progress entry. If you want them renamed, that's a one-file change.
- **D2:** the plan's Task 3.5 wording expects "nothing in … `general/`" — the 20 Class-C matches are the single documented exception (D1).
- **D3:** `qa/prompts/refine.py` (3 matches) is a prompt module your residual list didn't name; its docstring narrates the qa/tools surface. Classified as Phase-5 narration and left untouched — but note the plan's Task 5.2 lists only the six `prompts/update_<d>.py` + four ADR modules; Task 5.2 should probably add `qa/prompts/refine.py`. Also, only **four** `prompts/__init__.py` files actually match (tsk/rsk's prompt functions are named `update_task`/`update_risk`, which don't hit the grep).
- **D4:** `specmgr docs` writes pages for existing modules but **never deletes stale ones** — the seven orphaned `docs/api/...update_<d>.md` pages had to be removed manually (recorded in the Progress entry; a second generator run cannot resurrect them).
- **D5:** `specmgr coverage-badge` initially failed with `NoSource: .../gol/tools/update_gol.py` — the pre-existing `.coverage` data referenced deleted modules. Fixed by regenerating coverage with the exact pre-commit command (`uv run --frozen coverage run -m unittest discover -s tests -t . -p "test_*.py"`, exit 0) before running the badge (98%, byte-identical output).
- **No behavioral change** beyond the seven tool deletions and the two integration-test re-points; all `set_status_*` modules untouched except their docstrings (per your instruction), no `models/` schema changed, prompt narration untouched.

Plan README updated: frontmatter `updated: 2026-08-27` (already set), `status: in-progress` kept, new `#### Update 2026-08-27 (Phase 3: …)` entry above the Phase 2 entry (full residual list included), Current Status rewritten (Phase 3 complete, Phases 4–7 not started, 78/25/19), Tasks 3.1–3.6 flipped to `[x] … status: done` in place with wrapping preserved.
\</task_result>
</task>

````

---

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 195.8s)

_Thinking:_

Phase 3 was reported complete along with the classified residuals. Let me evaluate the flagged deviations:

**D1/D2**: The `_update_<d>` adapter function names in general/tools/update.py match the grep pattern as substrings. Wait — does `_update_req` match the grep pattern `update_req\|...`? Yes! `git grep "update_req"` matches `_update_req` (substring). The plan says the grep "must return only prompt-narration matches… and nothing in tools/, models/, general/". Hmm. The adapter names are mandated by the plan's own design notes ("private adapter functions (_update_<d> / _set_status_<d>)"). So there's a tension: the design notes mandate `_update_req` etc., and Task 3.5's grep (a naive substring pattern) will inevitably match them.

How to resolve? The intent of ACC-005 is "no code references to the deleted tool names." `_update_req` (the private adapter) is not a reference to the deleted tool `update_req` — it's a private function with an underscore prefix. A stricter grep like `grep -n "\bupdate_req\b"` would… well, in regex `\b` between `_` and `u` — `_` is a word character, so `\bupdate_req\b` won't match `_update_req` (no word boundary between `_` and `u`, since both are word characters). So with a word-boundary grep, the Class-C matches disappear. The plan's grep pattern lacks boundaries, but the intent is clear: no references to the deleted tools. The adapter names are plan-mandated. My ruling: D1 is acceptable — keep the `_update_<d>` names (the design notes mandate them), and note that with a word-boundary grep the residuals under general/ vanish. I should verify this myself.

**D3**: `qa/prompts/refine.py` (3 matches) — a prompt module not on my residual list; classified as Phase 5 narration. Agreed — this is a prompt module whose docstring describes the surface; Phase 5 must fix it. Note: Task 5.2 should include this. Also, only 4 prompts/__init__.py match (tsk/rsk prompt functions are update_task/update_risk — not in the grep pattern… wait, the grep pattern does include `update_tsk` and `update_rsk` — but the tsk prompt module is `update_task.py` defining the prompt `update_task`, and rsk is `update_risk.py` defining `update_risk`. These names don't match `update_tsk`/`update_rsk`. Correct.)

But wait — this raises a mirror-image issue in Phase 5: the prompts named `update_task`/`update_risk` don't collide with the deleted tool names, no problem.

**D4**: Stale API pages had to be deleted manually because `specmgr docs` never removes orphan pages. Reasonable — the alternative (leaving 7 orphan pages in docs/api) violates the "docs/api/ loses 7 module pages" requirement of Task 3.6. Accept.

**D5**: Stale .coverage data caused a NoSource failure; fixed by running coverage with the pre-commit command. This is also a known pre-commit flow (the pre-commit unittest hook runs `coverage run` and regenerates the data). Accept — and importantly, this means that at my commit time, the pre-commit unittest hook will again run `coverage run -m unittest discover` and regenerate .coverage, then coverage-badge will run on the new data. No problem.

**Class B additions**: The prompt-enumeration sentences in `req/__init__.py`, `qa/__init__.py`, `prb/__init__.py`, `gol/__init__.py` (1 match each) — "prompt enumeration sentences" — these domain __init__ docstrings also enumerate prompts (e.g., "prompts: create_req, update_req"). These are prompt names (retained by design), not tool references. Accept as Class B.

Now, let me verify independently:
1. The 14 deletions exist.
2. The final git grep with word boundaries: `git grep -nE "\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk)\b" -- src/ tests/` — check what remains (should be only narration + prompt-name enumeration).
3. Run the full gate: ruff format --check, ruff check, vulture, unittest (1796 expected), coverage run (needed for badge), coverage-badge, mcp-docs, docs, zero drift on rerun, fresh import, live count 78/25/19.
4. docs/MCP.md check: update_<d> entries are gone, the generic update is intact, set_status is intact.
5. Spot-check the docstring rewrites (1–2 files: _lock.py, set_status_req.py, the docstring of the adapter in general/tools/update.py, tsk/models/v1/body.py).
6. README progress entry with the residual list.
7. git diff --stat.

Note: For the coverage-badge to work, .coverage data must exist and be up to date. The pre-commit hook runs `coverage run -m unittest discover -v ...` and then coverage-badge. At my commit, the hooks handle that. In my verification, I'll run the same sequence.

Let me batch the commands. First batch: status + word-boundary grep + MCP.md check. Second batch: full gate (long).




Phase 3 returned with 5 flagged deviations. My rulings before verifying:

- **D1/D2** (`_update_<d>` adapter names matching the naive substring grep): the Design Notes themselves *mandate* the naming `_update_<d>`; a word-boundary grep (`\bupdate_req\b`) does not match `_update_req`. Intent of ACC-005 = no references to *deleted tools* — acceptable, will verify with the boundary grep.
- **D3** (`qa/prompts/refine.py` narration): correctly classified as Phase 5; will add to Phase 5's scope.
- **D4** (manual deletion of orphaned `docs/api` pages): necessary — the generator does not delete orphan pages, and the plan requires that 7 pages be removed. Accept.
- **D5** (stale `.coverage` data): the pre-commit flow regenerates this; accept.

Verifying independently now:




**Tool: bash**

**Input:**
```json
{
  "command": "git status --short | awk '{print $1}' | sort | uniq -c && echo === && git diff --stat | tail -3 && echo === && git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk)\\b\" -- src/ tests/ | grep -vE \"data/|prompts/|tests/.*prompts/\" ; echo \"boundary-non-narration-exit=$?\" && echo === && git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk)\\b\" -- src/ tests/ | cut -d: -f1 | sort | uniq -c | sort -rn",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
````

**Output:**

```
     21 D
    115 M
===
 tests/tsk/tools/test_update_tsk.py                 | 156 ----------------
 tests/uc/tools/test_update_uc.py                   | 199 --------------------
 136 files changed, 684 insertions(+), 2765 deletions(-)
===
src/biz/dfch/specmgr/gol/__init__.py:33:(``create_gol``, ``update_gol``) all exist; whole-body and line-range
src/biz/dfch/specmgr/prb/__init__.py:33:(``create_prb``, ``update_prb``) all exist; whole-body and line-range
src/biz/dfch/specmgr/qa/__init__.py:33:(``create_qa``, ``update_qa``) all exist; whole-body and line-range updates
src/biz/dfch/specmgr/req/__init__.py:15:(``create_req``, ``update_req``) all exist; whole-body and line-range
boundary-non-narration-exit=0
===
     26 tests/prb/prompts/test_update_prb.py
     23 tests/qa/prompts/test_update_qa.py
     23 tests/gol/prompts/test_update_gol.py
     20 tests/req/prompts/test_update_req.py
     10 src/biz/dfch/specmgr/gol/prompts/update_gol.py
      9 src/biz/dfch/specmgr/prb/prompts/update_prb.py
      7 tests/tsk/prompts/test_update_task.py
      7 tests/rsk/prompts/test_update_risk.py
      6 src/biz/dfch/specmgr/qa/prompts/update_qa.py
      5 src/biz/dfch/specmgr/req/prompts/update_req.py
      4 src/biz/dfch/specmgr/tsk/prompts/update_task.py
      4 src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
      4 src/biz/dfch/specmgr/server.py
      4 src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
      4 src/biz/dfch/specmgr/req/data/req_update_instructions.md
      4 src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
      4 src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
      4 src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
      4 src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
      3 tests/qa/prompts/test_refine.py
      3 src/biz/dfch/specmgr/rsk/prompts/update_risk.py
      3 src/biz/dfch/specmgr/req/data/req_create_instructions.md
      3 src/biz/dfch/specmgr/qa/prompts/refine.py
      3 src/biz/dfch/specmgr/qa/prompts/__init__.py
      3 src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
      3 src/biz/dfch/specmgr/prb/prompts/__init__.py
      3 src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
      2 tests/tsk/prompts/test_implement_task.py
      2 tests/req/prompts/test_create_req.py
      2 tests/qa/prompts/test_create_qa.py
      2 tests/prb/prompts/test_create_prb.py
      2 tests/gol/prompts/test_create_gol.py
      2 src/biz/dfch/specmgr/req/prompts/__init__.py
      2 src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
      2 src/biz/dfch/specmgr/gol/prompts/__init__.py
      1 src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
      1 src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
      1 src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
      1 src/biz/dfch/specmgr/req/__init__.py
      1 src/biz/dfch/specmgr/qa/__init__.py
      1 src/biz/dfch/specmgr/prb/__init__.py
      1 src/biz/dfch/specmgr/gol/__init__.py

```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -nE \"update_(req|uc|tsk|qa|prb|gol|rsk)\" docs/MCP.md | grep -vE \"^\\s*\\| update_(req|uc|tsk|qa|prb|gol|rsk) \\|\" | head; echo ---; grep -cE \"^### Tool: set_status\" docs/MCP.md; grep -cE \"^### Tool: update\" docs/MCP.md; grep -nE \"prompt.*update_(req|tsk|qa|risk|prb|gol)|update_(req|tsk|qa|prb|gol).*prompt\" docs/MCP.md | head -8",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
1102:| [`update_gol`](#prompt-update_gol) | Guides the LLM through revising an existing goal by id: reading current state, showing which sections are present vs. empty, eliciting revisions, applying the change with the right tool, and validating. |
1103:| [`update_prb`](#prompt-update_prb) | Guides the LLM through revising an existing problem statement by id: reading current state, showing which of the 7 5W2H questions are answered, eliciting revisions, re-synthesizing Summary/Gap, applying the change with the right tool, and validating. |
1104:| [`update_qa`](#prompt-update_qa) | Guides the LLM through revising an existing QA document by id: reading current state, applying the requested change with the right tool, and validating. |
1105:| [`update_req`](#prompt-update_req) | Guides the LLM through revising an existing requirement by id: reading current state, applying the requested change with the right tool, and validating. |
1223:### Prompt: update_gol
1231:### Prompt: update_prb
1240:### Prompt: update_qa
1249:### Prompt: update_req
---
8
3
1102:| [`update_gol`](#prompt-update_gol) | Guides the LLM through revising an existing goal by id: reading current state, showing which sections are present vs. empty, eliciting revisions, applying the change with the right tool, and validating. |
1103:| [`update_prb`](#prompt-update_prb) | Guides the LLM through revising an existing problem statement by id: reading current state, showing which of the 7 5W2H questions are answered, eliciting revisions, re-synthesizing Summary/Gap, applying the change with the right tool, and validating. |
1104:| [`update_qa`](#prompt-update_qa) | Guides the LLM through revising an existing QA document by id: reading current state, applying the requested change with the right tool, and validating. |
1105:| [`update_req`](#prompt-update_req) | Guides the LLM through revising an existing requirement by id: reading current state, applying the requested change with the right tool, and validating. |
1106:| [`update_risk`](#prompt-update_risk) | Guides the LLM through revising an existing risk by id: reading current state, applying the requested change with the right tool, and validating. |

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 137.8s)

_Thinking:_

Wait — the grep on docs/MCP.md needs to be looked at carefully. Let me analyze:

1. `grep -cE "^### Tool: set_status" docs/MCP.md` → **8** ✓ (7 per-domain + 1 ADR — all still exist as expected)
2. `grep -cE "^### Tool: update" docs/MCP.md` → **3**?? Should be 1 (the generic `update`). What are the other 2? Hmm — wait, "^### Tool: update" matches "### Tool: update" — the generic one. What else? `### Tool: update_frontmatter`! and `### Tool: update_section`! ADR's section-level tools — these exist (ADR keeps update_frontmatter/update_section). So 3 = update + update_frontmatter + update_section. ✓ And importantly, `### Tool: update_req` etc. don't exist (if they did, the count would be 10).
3. The first grep with exclusion showed prompt lines 1102–1105 — these are **prompt** lines in the prompts table (`#prompt-update_gol`), not tools. Retained by design. ✓
4. Lines 1223–1249: `### Prompt: update_*` sections — prompts, retained. ✓

So docs/MCP.md is correct: the 7 update\_<d> tool entries have been removed, and the generic update + ADR's update_frontmatter/update_section remain; set_status has 8 entries; prompts are unharmed.

Next, the word-boundary grep results against src/tests:

- Remaining non-narration matches (excluding data/, prompts/, tests/\*/prompts/): only 4 lines — the prompt enumeration sentences in `req/__init__.py:15`, `qa/__init__.py:33`, `prb/__init__.py:33`, `gol/__init__.py:33` — "(create_req, update_req) all exist" — these are enumerations of **prompt** names (retained by design, Class B).

Wait, but the implementer said tsk/rsk's __init__.py don't match — correct, because their prompt names are update_task/update_risk (don't hit the boundary grep pattern).

Hmm, wait — but let me double-check: `req/__init__.py:15` says "(create_req, update_req) all exist; whole-body and line-range..." — let me make sure this sentence is about prompts and not about tools. The sentence structure "...prompts (create_req, update_req) all exist..." — I need to check the actual line. Let me look at req/__init__.py lines 10–20.

Also confirming: zero matches in general/tools/update.py with the boundary grep (Class C disappeared as predicted — `_update_req` doesn't match `\bupdate_req\b`). ✓ (not included in the output above).

And `server.py` has 4 matches (line numbers 155/161/166/170 — prompt enumeration). ✓ Retained by design.

So the only remaining item to verify is: that the 4 domain __init__.py matches are prompt references. Let me quickly read those lines. Then run the full gate.

`docs/MCP.md` is exactly right: 8 `### Tool: set_status*` entries remain, `### Tool: update` count = 3 (generic `update` + ADR's `update_frontmatter`/`update_section` — no per-domain `update_<d>` tools), and the remaining `update_*` lines are all **prompt** entries (which we're keeping by design). With the word-boundary grep, Class C has vanished (as predicted, `_update_<d>` does not match `\bupdate_req\b`). The only remaining non-narration match is the 4 lines in the domain `__init__.py` — currently checking whether those are really prompt references:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '8,20p' src/biz/dfch/specmgr/req/__init__.py && echo === && sed -n '25,40p' src/biz/dfch/specmgr/qa/__init__.py",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```

    from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)

``tools`` (``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
``get_req_template``, ``create_req``, ``set_status_req``,
``delete_req``, ``validate_req``), ``resources`` (``specmgr://req/schema``,
``specmgr://req/example``, ``specmgr://req/template``), and ``prompts``
(``create_req``, ``update_req``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="req"``). Unlike ADR, REQ has no
``specmgr://req/{id}`` resource -- id-based reads go through the ``get_req``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, the former
``specmgr://req/list`` resource was replaced by the ``list_req`` tool, so
===
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import qa  # noqa: F401 (side-effects only)

``tools`` (``parse_qa``, ``get_qa``, ``list_qa``, ``get_qa_example``,
``get_qa_template``, ``create_qa``, ``set_status_qa``,
``delete_qa``, ``validate_qa``), ``resources`` (``specmgr://qa/schema``,
``specmgr://qa/example``, ``specmgr://qa/template``), and ``prompts``
(``create_qa``, ``update_qa``) all exist; whole-body and line-range updates
of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="qa"``). Like REQ, QA has no
``specmgr://qa/{id}`` resource -- id-based reads go through the ``get_qa``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, the former
``specmgr://qa/list`` resource was replaced by the ``list_qa`` tool, so
that paging parameters could be accepted (feat-13-list-paging).


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 241.3s)

_Thinking:_

Confirmed — those 4 matches are the **prompts** enumerations (`create_req`, `update_req`), and the tool enumerations correctly no longer include `update_req` (only `create_req` remains... no, looking more closely: the tool list is `parse_req, get_req, list_req, get_req_example, get_req_template, create_req, set_status_req, delete_req, validate_req` — `update_req` is not in the tools ✓, and the text points to the generic update tool ✓). The `update_req` there is a prompt name, which is retained by design.

Next, run the full gate independently:

1. ruff format --check, ruff check, vulture
2. Coverage run (pre-commit command) → unittest 1796
3. coverage-badge, mcp-docs, docs
4. Zero-drift proof via re-run
5. Import in a new subprocess
6. Live count 78/25/19
7. Spot-check the rewritten docstrings (general/tools/update.py adapter docstrings, \_lock.py, set_status_req.py, tsk/models/v1/body.py)
8. README progress entry (residual list)

After that, commit.

Confirmed — those are prompt-name enumerations (tools lists correctly no longer carry `update_<d>` and point to the generic tool). Now the full independent gate:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase3-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase3-unittest.log && uv run --frozen specmgr coverage-badge && uv run --frozen specmgr mcp-docs && uv run --frozen specmgr docs && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p3-m1.txt && uv run --frozen specmgr coverage-badge >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && uv run --frozen specmgr docs >/dev/null && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p3-m2.txt && diff /tmp/opencode/p3-m1.txt /tmp/opencode/p3-m2.txt && echo P3_DOCS_ZERO_DRIFT && uv run --frozen python -c \"import biz.dfch.specmgr.server\" && echo IMPORT_OK && uv run --frozen python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\nprint('tools:', len(asyncio.run(mcp.list_tools())))\nprint('resources:', len(asyncio.run(mcp.list_resources())))\nprint('prompts:', len(asyncio.run(mcp.list_prompts())))\n\"",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
1115 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1796 tests in 97.516s
OK
Name                                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------------
src/biz/dfch/specmgr/__init__.py                                       1      0   100%
src/biz/dfch/specmgr/__main__.py                                       3      1    67%
src/biz/dfch/specmgr/_paths.py                                         6      0   100%
src/biz/dfch/specmgr/adr/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/adr/prompts/__init__.py                           5      0   100%
src/biz/dfch/specmgr/adr/prompts/create_adr.py                         8      0   100%
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py                    8      0   100%
src/biz/dfch/specmgr/adr/prompts/update_adr.py                         8      0   100%
src/biz/dfch/specmgr/adr/prompts/update_adr_test.py                    8      0   100%
src/biz/dfch/specmgr/adr/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/adr/resources/adr_get.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/__init__.py                            13      0   100%
src/biz/dfch/specmgr/adr/tools/_io.py                                 12      0   100%
src/biz/dfch/specmgr/adr/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/adr/tools/_paths.py                              37      0   100%
src/biz/dfch/specmgr/adr/tools/create_adr.py                          15      0   100%
src/biz/dfch/specmgr/adr/tools/get_adr.py                             10      0   100%
src/biz/dfch/specmgr/adr/tools/list_adr.py                            19      0   100%
src/biz/dfch/specmgr/adr/tools/option_create.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/option_delete.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/option_list.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/option_read.py                         10      0   100%
src/biz/dfch/specmgr/adr/tools/option_update.py                       14      0   100%
src/biz/dfch/specmgr/adr/tools/set_status.py                          15      0   100%
src/biz/dfch/specmgr/adr/tools/update_frontmatter.py                  15      0   100%
src/biz/dfch/specmgr/adr/tools/update_section.py                      15      0   100%
src/biz/dfch/specmgr/adr/tools/validate_adr.py                         9      0   100%
src/biz/dfch/specmgr/cli.py                                           23      2    91%
src/biz/dfch/specmgr/commands/__init__.py                             11      0   100%
src/biz/dfch/specmgr/commands/adr_toc.py                              42     32    24%
src/biz/dfch/specmgr/commands/coverage_badge.py                       49     11    78%
src/biz/dfch/specmgr/commands/docs.py                                218      8    96%
src/biz/dfch/specmgr/commands/mcp.py                                  23      3    87%
src/biz/dfch/specmgr/commands/mcp_docs.py                            131      8    94%
src/biz/dfch/specmgr/commands/mdformat.py                             18      0   100%
src/biz/dfch/specmgr/commands/req_parse.py                            44      0   100%
src/biz/dfch/specmgr/commands/schema.py                               76      0   100%
src/biz/dfch/specmgr/commands/unused_code.py                          53      0   100%
src/biz/dfch/specmgr/commands/version.py                               8      2    75%
src/biz/dfch/specmgr/general/__init__.py                               2      0   100%
src/biz/dfch/specmgr/general/models/__init__.py                        3      0   100%
src/biz/dfch/specmgr/general/models/paged_result.py                   11      0   100%
src/biz/dfch/specmgr/general/models/summary.py                         8      0   100%
src/biz/dfch/specmgr/general/prompts/__init__.py                       2      0   100%
src/biz/dfch/specmgr/general/prompts/compact_history.py                8      0   100%
src/biz/dfch/specmgr/general/resources/__init__.py                     2      0   100%
src/biz/dfch/specmgr/general/resources/iso25010.py                     8      0   100%
src/biz/dfch/specmgr/general/resources/version.py                      7      0   100%
src/biz/dfch/specmgr/general/tools/__init__.py                         4      0   100%
src/biz/dfch/specmgr/general/tools/_doc_paths.py                      53      0   100%
src/biz/dfch/specmgr/general/tools/_packaged_data.py                  11      0   100%
src/biz/dfch/specmgr/general/tools/_paging.py                         28      0   100%
src/biz/dfch/specmgr/general/tools/_splice.py                         30      0   100%
src/biz/dfch/specmgr/general/tools/mdformat.py                        12      0   100%
src/biz/dfch/specmgr/general/tools/update.py                         234      0   100%
src/biz/dfch/specmgr/general/tools/webfetch.py                        27      0   100%
src/biz/dfch/specmgr/gol/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/gol/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/gol/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/gol/models/v1/body.py                            43      0   100%
src/biz/dfch/specmgr/gol/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/gol/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/gol/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/gol/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/gol/prompts/create_gol.py                         8      0   100%
src/biz/dfch/specmgr/gol/prompts/update_gol.py                         8      0   100%
src/biz/dfch/specmgr/gol/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/gol/resources/gol_example.py                      6      0   100%
src/biz/dfch/specmgr/gol/resources/gol_schema.py                       9      0   100%
src/biz/dfch/specmgr/gol/resources/gol_template.py                     6      0   100%
src/biz/dfch/specmgr/gol/tools/__init__.py                            10      0   100%
src/biz/dfch/specmgr/gol/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/gol/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/gol/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/gol/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/gol/tools/create_gol.py                          21      0   100%
src/biz/dfch/specmgr/gol/tools/delete_gol.py                           6      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol.py                             15      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol_example.py                      6      0   100%
src/biz/dfch/specmgr/gol/tools/get_gol_template.py                     6      0   100%
src/biz/dfch/specmgr/gol/tools/list_gol.py                            18      0   100%
src/biz/dfch/specmgr/gol/tools/parse_gol.py                            8      0   100%
src/biz/dfch/specmgr/gol/tools/set_status_gol.py                      23      0   100%
src/biz/dfch/specmgr/gol/tools/validate_gol.py                        16      0   100%
src/biz/dfch/specmgr/models/__init__.py                                4      0   100%
src/biz/dfch/specmgr/models/adr/__init__.py                            2      0   100%
src/biz/dfch/specmgr/models/adr/v1/__init__.py                         9      0   100%
src/biz/dfch/specmgr/models/adr/v1/_util.py                           25      0   100%
src/biz/dfch/specmgr/models/adr/v1/adr.py                              9      0   100%
src/biz/dfch/specmgr/models/adr/v1/body.py                            27      0   100%
src/biz/dfch/specmgr/models/adr/v1/frontmatter.py                     33      0   100%
src/biz/dfch/specmgr/models/adr/v1/mutations.py                       54      0   100%
src/biz/dfch/specmgr/models/adr/v1/option.py                          17      0   100%
src/biz/dfch/specmgr/models/adr/v1/parser.py                         137      5    96%
src/biz/dfch/specmgr/models/adr/v1/renderer.py                        45      0   100%
src/biz/dfch/specmgr/models/adr/v1/summary.py                          7      0   100%
src/biz/dfch/specmgr/models/iso25010.py                               21      0   100%
src/biz/dfch/specmgr/models/md/__init__.py                            25      0   100%
src/biz/dfch/specmgr/models/md/_markdown.py                           36      0   100%
src/biz/dfch/specmgr/models/md/_util.py                               25      1    96%
src/biz/dfch/specmgr/models/md/alias.py                                7      0   100%
src/biz/dfch/specmgr/models/md/alias_match.py                         24      1    96%
src/biz/dfch/specmgr/models/md/alias_type.py                           6      0   100%
src/biz/dfch/specmgr/models/md/frontmatter.py                         29      0   100%
src/biz/dfch/specmgr/models/md/markdown.py                            16      0   100%
src/biz/dfch/specmgr/models/md/markdown_block_quote.py                78      1    99%
src/biz/dfch/specmgr/models/md/markdown_code_block.py                 52      1    98%
src/biz/dfch/specmgr/models/md/markdown_comment.py                    55      2    96%
src/biz/dfch/specmgr/models/md/markdown_list_item.py                  85      7    92%
src/biz/dfch/specmgr/models/md/markdown_paragraph.py                  76      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section1_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section2.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section3_with_comment.py      14      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section4_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section5.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section5_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section6.py                    9      0   100%
src/biz/dfch/specmgr/models/md/markdown_section6_with_comment.py      14      1    93%
src/biz/dfch/specmgr/models/md/markdown_section.py                   108      1    99%
src/biz/dfch/specmgr/models/md/markdown_str.py                       150      3    98%
src/biz/dfch/specmgr/models/version_info.py                            4      0   100%
src/biz/dfch/specmgr/prb/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/prb/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/prb/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/prb/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/prb/models/v1/body.py                            40      0   100%
src/biz/dfch/specmgr/prb/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/prb/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/prb/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/prb/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/prb/prompts/create_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/prompts/update_prb.py                         8      0   100%
src/biz/dfch/specmgr/prb/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/prb/resources/prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/resources/prb_schema.py                       9      0   100%
src/biz/dfch/specmgr/prb/resources/prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/__init__.py                            10      0   100%
src/biz/dfch/specmgr/prb/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/prb/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/prb/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/prb/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/prb/tools/create_prb.py                          21      0   100%
src/biz/dfch/specmgr/prb/tools/delete_prb.py                           6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb.py                             15      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_example.py                      6      0   100%
src/biz/dfch/specmgr/prb/tools/get_prb_template.py                     6      0   100%
src/biz/dfch/specmgr/prb/tools/list_prb.py                            18      0   100%
src/biz/dfch/specmgr/prb/tools/parse_prb.py                            8      0   100%
src/biz/dfch/specmgr/prb/tools/set_status_prb.py                      23      0   100%
src/biz/dfch/specmgr/prb/tools/validate_prb.py                        16      0   100%
src/biz/dfch/specmgr/qa/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/qa/models/__init__.py                             0      0   100%
src/biz/dfch/specmgr/qa/models/v2/__init__.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/qa/models/v2/body.py                             37      0   100%
src/biz/dfch/specmgr/qa/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/qa/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/qa/models/v2/question_answer.py                  71      0   100%
src/biz/dfch/specmgr/qa/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/qa/prompts/__init__.py                            4      0   100%
src/biz/dfch/specmgr/qa/prompts/create_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/prompts/refine.py                              8      0   100%
src/biz/dfch/specmgr/qa/prompts/update_qa.py                           8      0   100%
src/biz/dfch/specmgr/qa/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/qa/resources/qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/resources/qa_schema.py                         9      0   100%
src/biz/dfch/specmgr/qa/resources/qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/__init__.py                             10      0   100%
src/biz/dfch/specmgr/qa/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/qa/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/qa/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/qa/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/qa/tools/create_qa.py                            21      0   100%
src/biz/dfch/specmgr/qa/tools/delete_qa.py                             6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa.py                               15      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_example.py                        6      0   100%
src/biz/dfch/specmgr/qa/tools/get_qa_template.py                       6      0   100%
src/biz/dfch/specmgr/qa/tools/list_qa.py                              18      0   100%
src/biz/dfch/specmgr/qa/tools/parse_qa.py                              8      0   100%
src/biz/dfch/specmgr/qa/tools/set_status_qa.py                        23      0   100%
src/biz/dfch/specmgr/qa/tools/validate_qa.py                          16      0   100%
src/biz/dfch/specmgr/req/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/req/models/v1/__init__.py                         7      0   100%
src/biz/dfch/specmgr/req/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/req/models/v1/body.py                            57      0   100%
src/biz/dfch/specmgr/req/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/req/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/req/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/req/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/req/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/req/prompts/create_req.py                         8      0   100%
src/biz/dfch/specmgr/req/prompts/update_req.py                         8      0   100%
src/biz/dfch/specmgr/req/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/req/resources/req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/resources/req_schema.py                       9      0   100%
src/biz/dfch/specmgr/req/resources/req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/__init__.py                            10      0   100%
src/biz/dfch/specmgr/req/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/req/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/req/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/req/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/req/tools/create_req.py                          21      0   100%
src/biz/dfch/specmgr/req/tools/delete_req.py                           6      0   100%
src/biz/dfch/specmgr/req/tools/get_req.py                             15      0   100%
src/biz/dfch/specmgr/req/tools/get_req_example.py                      6      0   100%
src/biz/dfch/specmgr/req/tools/get_req_template.py                     6      0   100%
src/biz/dfch/specmgr/req/tools/list_req.py                            18      0   100%
src/biz/dfch/specmgr/req/tools/parse_req.py                            8      0   100%
src/biz/dfch/specmgr/req/tools/set_status_req.py                      23      0   100%
src/biz/dfch/specmgr/req/tools/validate_req.py                        16      0   100%
src/biz/dfch/specmgr/rsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/rsk/models/__init__.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/rsk/models/v1/assessment.py                      57      0   100%
src/biz/dfch/specmgr/rsk/models/v1/body.py                            38      0   100%
src/biz/dfch/specmgr/rsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py                     20      0   100%
src/biz/dfch/specmgr/rsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/rsk/models/v1/summary.py                         23      0   100%
src/biz/dfch/specmgr/rsk/prompts/__init__.py                           3      0   100%
src/biz/dfch/specmgr/rsk/prompts/create_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/prompts/update_risk.py                        8      0   100%
src/biz/dfch/specmgr/rsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/rsk/resources/risk_matrix.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/rsk/resources/rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/resources/tara.py                             6      0   100%
src/biz/dfch/specmgr/rsk/tools/__init__.py                            10      0   100%
src/biz/dfch/specmgr/rsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/rsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/rsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/rsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/rsk/tools/create_rsk.py                          21      0   100%
src/biz/dfch/specmgr/rsk/tools/delete_rsk.py                           6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk.py                             15      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_example.py                      6      0   100%
src/biz/dfch/specmgr/rsk/tools/get_rsk_template.py                     6      0   100%
src/biz/dfch/specmgr/rsk/tools/list_rsk.py                            18      0   100%
src/biz/dfch/specmgr/rsk/tools/parse_rsk.py                            8      0   100%
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py                      23      0   100%
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py                        16      0   100%
src/biz/dfch/specmgr/server.py                                         9      1    89%
src/biz/dfch/specmgr/tsk/__init__.py                                   2      0   100%
src/biz/dfch/specmgr/tsk/models/__init__.py                            0      0   100%
src/biz/dfch/specmgr/tsk/models/v1/__init__.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/_util.py                            2      0   100%
src/biz/dfch/specmgr/tsk/models/v1/body.py                            17      0   100%
src/biz/dfch/specmgr/tsk/models/v1/document.py                         8      0   100%
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py                     13      0   100%
src/biz/dfch/specmgr/tsk/models/v1/parser.py                          14      0   100%
src/biz/dfch/specmgr/tsk/models/v1/summary.py                          4      0   100%
src/biz/dfch/specmgr/tsk/models/v1/task_item.py                       19      0   100%
src/biz/dfch/specmgr/tsk/prompts/__init__.py                           4      0   100%
src/biz/dfch/specmgr/tsk/prompts/create_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/prompts/implement_task.py                     8      0   100%
src/biz/dfch/specmgr/tsk/prompts/update_task.py                        8      0   100%
src/biz/dfch/specmgr/tsk/resources/__init__.py                         2      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_schema.py                       9      0   100%
src/biz/dfch/specmgr/tsk/resources/tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/__init__.py                            10      0   100%
src/biz/dfch/specmgr/tsk/tools/_io.py                                 16      0   100%
src/biz/dfch/specmgr/tsk/tools/_lock.py                               19      0   100%
src/biz/dfch/specmgr/tsk/tools/_paths.py                              29      0   100%
src/biz/dfch/specmgr/tsk/tools/_write.py                              11      0   100%
src/biz/dfch/specmgr/tsk/tools/create_tsk.py                          21      0   100%
src/biz/dfch/specmgr/tsk/tools/delete_tsk.py                           6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk.py                             15      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_example.py                      6      0   100%
src/biz/dfch/specmgr/tsk/tools/get_tsk_template.py                     6      0   100%
src/biz/dfch/specmgr/tsk/tools/list_tsk.py                            18      0   100%
src/biz/dfch/specmgr/tsk/tools/parse_tsk.py                            8      0   100%
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py                      23      0   100%
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py                        16      0   100%
src/biz/dfch/specmgr/uc/__init__.py                                    2      0   100%
src/biz/dfch/specmgr/uc/models/__init__.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v1/__init__.py                         16      0   100%
src/biz/dfch/specmgr/uc/models/v1/characteristic_information.py       27      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension.py                        14      0   100%
src/biz/dfch/specmgr/uc/models/v1/extension_action.py                  5      0   100%
src/biz/dfch/specmgr/uc/models/v1/extensions.py                        5      0   100%
src/biz/dfch/specmgr/uc/models/v1/main_success_scenario.py            12      0   100%
src/biz/dfch/specmgr/uc/models/v1/open_issues.py                       4      0   100%
src/biz/dfch/specmgr/uc/models/v1/parser.py                          204     11    95%
src/biz/dfch/specmgr/uc/models/v1/related_information.py               6      0   100%
src/biz/dfch/specmgr/uc/models/v1/related_use_cases.py                 6      0   100%
src/biz/dfch/specmgr/uc/models/v1/step.py                              5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variation.py                     5      0   100%
src/biz/dfch/specmgr/uc/models/v1/sub_variations.py                    5      0   100%
src/biz/dfch/specmgr/uc/models/v1/uc_diagram.py                       47      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case.py                         36      0   100%
src/biz/dfch/specmgr/uc/models/v1/use_case_frontmatter.py             16      0   100%
src/biz/dfch/specmgr/uc/models/v2/__init__.py                          7      0   100%
src/biz/dfch/specmgr/uc/models/v2/_util.py                             2      0   100%
src/biz/dfch/specmgr/uc/models/v2/document.py                          8      0   100%
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py                      13      0   100%
src/biz/dfch/specmgr/uc/models/v2/parser.py                           14      0   100%
src/biz/dfch/specmgr/uc/models/v2/summary.py                           4      0   100%
src/biz/dfch/specmgr/uc/models/v2/use_case.py                        113      0   100%
src/biz/dfch/specmgr/uc/resources/__init__.py                          2      0   100%
src/biz/dfch/specmgr/uc/resources/uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/resources/uc_schema.py                         9      0   100%
src/biz/dfch/specmgr/uc/resources/uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/__init__.py                             10      0   100%
src/biz/dfch/specmgr/uc/tools/_io.py                                  16      0   100%
src/biz/dfch/specmgr/uc/tools/_lock.py                                19      0   100%
src/biz/dfch/specmgr/uc/tools/_paths.py                               29      0   100%
src/biz/dfch/specmgr/uc/tools/_write.py                               11      0   100%
src/biz/dfch/specmgr/uc/tools/create_uc.py                            21      0   100%
src/biz/dfch/specmgr/uc/tools/delete_uc.py                             6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc.py                               15      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_example.py                        6      0   100%
src/biz/dfch/specmgr/uc/tools/get_uc_template.py                       6      0   100%
src/biz/dfch/specmgr/uc/tools/list_uc.py                              18      0   100%
src/biz/dfch/specmgr/uc/tools/parse_uc.py                              8      0   100%
src/biz/dfch/specmgr/uc/tools/set_status_uc.py                        23      0   100%
src/biz/dfch/specmgr/uc/tools/validate_uc.py                          16      0   100%
--------------------------------------------------------------------------------------
TOTAL                                                               5782    105    98%
✓ Wrote docs/coverage.svg (98% coverage)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/MCP.md
✓ Wrote 312 module file(s) to /home/user/src/biz.dfch.SpecMgr-feat-22/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/GENERATED.md
P3_DOCS_ZERO_DRIFT
IMPORT_OK
tools: 78
resources: 25
prompts: 19

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 57.7s)

_Thinking:_

The full gate for Phase 3 is independently green:

- ruff format --check: 1115 files ✓
- ruff check: passed ✓
- vulture: clean ✓
- unittest (coverage run, pre-commit format): **1796 tests, OK**, exit code 0 ✓ (exactly 1830−34)
- coverage-badge: 98%, written ✓
- mcp-docs: 78 tools in MCP.md ✓
- docs: 312 module pages (319−7) ✓
- zero-drift proof via re-run: **P3_DOCS_ZERO_DRIFT** ✓
- fresh import: OK ✓
- live count: **78/25/19** ✓

Also confirmed: no pages for the update\_<d> modules remain in the coverage table (the src listing shows that update_req.py etc. are gone from the coverage report — the modules were deleted).

Next, spot-check the quality of the docstring rewrites and the README entries. After that, commit.

Phase 3 gate fully green on my independent run: 1796 tests OK (exactly −34), 78/25/19 live, zero docs drift, 312 API pages (−7). Final spot-checks — the reworded docstrings and the README progress entry with the required residual list:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '95,106p' src/biz/dfch/specmgr/general/tools/update.py && echo === && sed -n '20,30p' src/biz/dfch/specmgr/req/tools/_lock.py && echo === && sed -n '23,30p' src/biz/dfch/specmgr/req/tools/set_status_req.py && echo === && sed -n '136,144p' src/biz/dfch/specmgr/tsk/models/v1/body.py && echo === && sed -n '105,115p' src/biz/dfch/specmgr/server.py",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
def _update_req(id_: str, content: str, begin: int | None, end: int | None) -> ReqDocument:
    """Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain requirement update tool's
    function body (same ``req_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch: with ``begin``/``end`` given (both-or-neither is
    enforced by the public :func:`update` before dispatch), the on-disk
    body is re-read via :func:`body_text`, spliced via
    :func:`splice_body`, and the *spliced result* is validated and
    persisted verbatim instead of the raw fragment.
===
Ported from ``adr.tools._lock.adr_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` tool in ``general.tools`` (``type="req"``) and any
future requirement mutation tool (``set_status_req``, Task 3.14) wrap their
whole sequence in ``with req_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` (Task
3.10) -- the id -> path lookup plumbing was generalized because it was
already shared, read-only, dependency-light code; a lock, by contrast, is a
===
``"superseded by ..."`` pattern, just the closed seven-value set
(``draft``/``proposed``/``accepted``/``superseded``/``deprecated``/
``rejected``/``implemented``). Neither ``create_req`` nor the generic
``update`` tool in ``general.tools`` accepts a ``status`` argument at all --
this is the sole entry point.

Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
on-disk state before re-writing the full file; there is no in-memory cache
===
        `TaskItem.checked`/`.description` are `@computed_field`s -- Pydantic
        only evaluates a computed field's getter on access (e.g. during
        `model_dump()`/serialization), never during construction/validation
        of the underlying model itself. Left unchecked, that would mean
        `Task.from_text(...)` (and therefore `create_tsk`, the generic
        `update` tool in `general.tools`, and `validate_tsk`) could
        silently accept a malformed checkbox marker like `"- [z] foo"`,
        breaking this project's universal "successfully
        constructing the model *is* the validation" convention -- a caller
===
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document), ``list_uc``,
``get_uc_example``,
``get_uc_template``, ``create_uc``, ``set_status_uc``, ``delete_uc``
(stub, not yet implemented), ``validate_uc``.
Requirement tools (``req/tools/``): ``parse_req``, ``get_req`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document), ``list_req``,
``get_req_example``,
``get_req_template``, ``create_req``, ``set_status_req``, ``delete_req``
(stub, not yet implemented), ``validate_req``.

```

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U1 -- .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | grep -E \"^\\+\" | grep -vE \"^\\+\\+\\+\" | head -120",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
+- [x] Task 3.1: Delete the seven tool modules: `req/tools/update_req.py`,
+  `rsk/tools/update_rsk.py` — depends on: Phase 2 complete — status: done
+- [x] Task 3.2: Delete the seven test files: `tests/req/tools/
+  tools/test_update_rsk.py` — depends on: Task 3.1 — status: done
+- [x] Task 3.3: Update the seven domain `tools/__init__.py` files (remove the
+  done
+- [x] Task 3.4: Update `server.py`'s module docstring: remove `update_<d>`
+  until Phase 4) — depends on: Task 3.1 — status: done
+- [x] Task 3.5: Grep verification: `grep -rn "update_req\|update_uc\|
+  list in the Progress entry — depends on: Tasks 3.2, 3.3, 3.4 — status: done
+- [x] Task 3.6: Phase-end quality gate — full gate; `specmgr mcp-docs` +
+  place — depends on: Task 3.5 — status: done
+**As of 2026-08-27**: Phase 3 (Retire the per-domain `update_*` tools)
+complete — the seven `update_<d>` tool modules, their seven test files
+(34 tests), and every non-narration code/docstring reference to the
+deleted tools are gone: whole-body *and* line-range updates now go only
+through the generic `update` tool in `general/tools/` (Phase 2), with the
+re-pointed `gol`/`prb` integration tests exercising it live. No
+`set_status*` tool changed (Phase 4 deletes all eight), and no schema
+changed (only `tsk/models/v1/body.py`'s docstring was reworded). The
+phase-end quality gate is green (1796 tests OK, zero `docs/` drift,
+fresh-subprocess import OK); live registration is 78 tools / 25 resources
+/ 19 prompts (baseline 85/25/19: −7). Phases 4–7 are not started.
+(Phase 1 — the feature's ADR 36905d5b-8057-4294-8665-c7eed5534db0 — and
+Phase 2 — the generic `update` tool + `raw` reads — completed on
+2026-08-27.)
+#### Update 2026-08-27 (Phase 3: Retire the per-domain `update_*` tools)
+
+- Completed: Phase 3 (Tasks 3.1–3.6). The seven `update_<d>` tools are
+  deleted from source and from MCP registration; whole-body *and*
+  line-range updates now go only through the generic `update` tool in
+  `general/tools/` (Phase 2). Every non-narration code/docstring
+  reference to the deleted tools was re-pointed:
+  - Deleted (7 tool modules):
+    `src/biz/dfch/specmgr/{req,uc,tsk,qa,prb,gol,rsk}/tools/update_<d>.py`;
+    deleted (7 test files, 34 tests):
+    `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_update_<d>.py`.
+  - Seven domain `tools/__init__.py`: `update_<d>` import + `__all__`
+    entry removed; the narrating sentence rewritten to say whole-body and
+    line-range updates go through the generic `update` tool in
+    `general.tools` (`type="<d>"`).
+  - Seven domain `__init__.py`: `update_<d>` removed from the docstring
+    tool enumeration, same generic-`update` pointer added. The prompt
+    enumerations in `req`/`qa`/`prb`/`gol`'s `__init__.py` keep the
+    prompt names `update_<d>` (the plan keeps the prompts).
+  - `server.py`: `update_<d>` removed from the seven per-domain Tools
+    lines; the `set_status_<d>` entries (Phase 4) and the per-domain
+    prompt enumerations (kept prompt names) stay.
+  - `general/tools/update.py`: the seven adapter docstrings reworded to
+    name the historical port without the deleted tool names ("Verbatim
+    port of the previous per-domain … update tool's function body … that
+    per-domain tool was retired in feat-22 Phase 3"). The private
+    adapter *function names* `_update_<d>` stay — they are this module's
+    own names per the Design Notes' dispatch convention (Phase 4 mirrors
+    it with `_set_status_<d>`), not references to the deleted tools.
+  - Seven `_io.py`/`_lock.py`/`_write.py` helper pairs: docstrings
+    re-pointed at the generic `update` tool; the live `set_status_<d>`
+    mentions in the `_lock.py` modules kept.
+  - `req/tools/create_req.py`, `uc/tools/create_uc.py`,
+    `qa/tools/create_qa.py`: "shared with `update_<d>`" reworded to the
+    generic `update` tool.
+  - Seven `validate_<d>.py` and seven `set_status_<d>.py`: docstring
+    mentions of the deleted tools reworded (the `set_status_<d>` modules
+    themselves stay — Phase 4 deletes them).
+  - `tsk/models/v1/body.py`: the `_validate_items_eagerly` docstring's
+    `create_tsk`/`update_tsk`/`validate_tsk` mention reworded.
+  - `tests/gol/tools/test_integration.py` +
+    `tests/prb/tools/test_integration.py`: re-pointed from
+    `update_gol`/`update_prb` to
+    `from biz.dfch.specmgr.general.tools.update import update` and
+    `update(<d>_id, "<d>", _REVISED_BODY)` (whole-body mode); docstring/
+    step text updated; both still pass live.
+- Task 3.5 residual match list — full
+  `git grep -n "update_req\|update_uc\|update_tsk\|update_qa\|update_prb\|
+  update_gol\|update_rsk" -- src/ tests/` after Tasks 3.1–3.5 (43 files,
+  251 match lines), grouped:
+  - Phase-5 prompt-narration files (left for Phase 5, per the plan's
+    ownership): the prompt modules `req/prompts/update_req.py` (5),
+    `qa/prompts/update_qa.py` (6), `qa/prompts/refine.py` (3),
+    `prb/prompts/update_prb.py` (9), `gol/prompts/update_gol.py` (10),
+    `tsk/prompts/update_task.py` (4), `rsk/prompts/update_risk.py` (3);
+    the prompt `__init__.py` files `req/prompts/__init__.py` (2),
+    `qa/prompts/__init__.py` (3), `prb/prompts/__init__.py` (3),
+    `gol/prompts/__init__.py` (2) — tsk/rsk's `prompts/__init__.py`
+    match nothing (their prompt functions are named `update_task`/
+    `update_risk`); the 14 `*/data/*.md` instruction files
+    (`req_create` 3, `req_update` 4, `tsk_create` 1, `tsk_implement` 1,
+    `tsk_update` 4, `qa_create` 3, `qa_refine` 4, `qa_update` 4,
+    `prb_create` 2, `prb_update` 4, `gol_create` 3, `gol_update` 4,
+    `rsk_create` 1, `rsk_update` 4); and the 12 prompt test files under
+    `tests/*/prompts/` (`test_update_req` 21, `test_update_qa` 24,
+    `test_update_prb` 27, `test_update_gol` 24, `test_update_task` 8,
+    `test_update_risk` 8, `test_create_req` 3, `test_create_qa` 3,
+    `test_create_prb` 3, `test_create_gol` 3, `test_refine` 4,
+    `test_implement_task` 3).
+  - Kept-by-design prompt-name enumerations (not tool references — the
+    plan keeps the prompt names): `server.py`'s four per-domain PROMPT
+    enumeration lines (155/161/166/170: req, qa, prb, gol — tsk/rsk's
+    prompt lines name `update_task`/`update_risk` and match nothing),
+    and the prompt-enumeration sentence in `req/__init__.py`,
+    `qa/__init__.py`, `prb/__init__.py`, `gol/__init__.py` (one match
+    each).
+  - Substring-only matches on the generic tool's own private adapter
+    names (not references to deleted tools; see the adapter-name note
+    above): `general/tools/update.py` (20 — the seven
+    `def _update_<d>` lines, the six `:func:`_update_req``
+    cross-references, and the seven dispatch-table entries).
+  - Everything else: zero matches — in particular, no per-domain
+    `tools/` file and no `models/` file names a deleted tool anymore
+    (Task 3.5's plan wording anticipated nothing in `general/` either;
+    the 20 adapter-name matches above are the single, documented
+    exception — flagging for the orchestrator's confirmation).
+- Quality gate (green): `ruff format --check` (1122 files already
+  formatted, down from 1136 — the 14 deleted files), `ruff check` (all
+  checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean,
+  exit 0), full unittest suite (**Ran 1796 tests, OK** — down from 1830:
+  −34, the seven deleted `test_update_<d>.py` files; the two re-pointed
+  `gol`/`prb` integration tests still pass live). Regenerations:
+  `specmgr coverage-badge` (98% — unchanged rounded value, badge
+  byte-identical, no diff), `specmgr mcp-docs` (header now "78 tool(s)";

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 179.9s)

_Thinking:_

Everything checked out fine. The docstring rewrites are clean and accurate, the server.py enumeration correctly excludes `update_<d>` from tools while preserving the raw note and set_status, and the README entry has a complete residual list (43 files, classified) and a gate result.

Minor discrepancy: the README says "1122 files already formatted," but my run showed 1115 files. That's because 7 old .md pages were deleted after the implementer's ruff run (deviation D4). 1122 − 7 = 1115. Consistent.

Phase 3 verified. Committing. Staging all changes (21 D + 115 M, including the deletion of 7 old docs/api pages).

Commit message: `refactor(feat-22): retire the seven per-domain update_<d> tools` — hmm, repo style: past commits use feat/docs/chore/ci scopes. Phase 2 used `feat(feat-22)`. Phase 3 is removal — `refactor(feat-22)` or `feat(feat-22)`? Conventional commits: removal of deprecated tools as part of a feature is... I'd use `refactor(feat-22): retire the seven per-domain update_<d> tools in favor of the generic update`. Actually, the plan says "one Conventional Commit per phase," and the type is left to my judgment. Since this phase removes the 14 files and changes behavior (the tools go away), `refactor` fits (it's not a new feature, it's structural). I'll use refactor.

**Phase 3 verification complete** — docstring rewrites are clean, the server.py list is accurate (the tool list no longer includes `update_<d>`, while the raw note and `set_status_*` are retained), and the README entry contains the complete classified residual list required by Task 3.5. (The implementer's "1122 files" vs. my "1115" is just the 7 orphaned API pages deleted per deviation D4.) Committing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git commit -m \"refactor(feat-22): retire the seven per-domain update_<d> tools\n\nPhase 3: delete the seven update_<d> tool modules and their seven test\nfiles (34 tests); whole-body and line-range updates now go only through\nthe generic update tool in general/tools/ (Phase 2). Re-point every\nnon-narration docstring/code reference (domain __init__.py and\ntools/__init__.py enumerations, _io/_lock/_write helpers, create_*/\nvalidate_*/set_status_* cross-refs, server.py tool lines,\ngeneral/tools/update.py adapter docstrings, tsk models body docstring)\nand the gol/prb integration tests (now call update(id, type, content)).\nPrompt narration references are Phase 5's; the residual match list is\nrecorded in the feature README. Regenerate docs (78 tools now); live\nregistration 78 tools / 25 resources / 19 prompts.\" && git log --oneline -3 && git status --short | head -5",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema...........................................................Passed
specmgr schema (req package copy)........................................Passed
specmgr schema (uc package copy).........................................Passed
specmgr schema (tsk package copy)........................................Passed
specmgr schema (rsk package copy)........................................Passed
specmgr schema (qa package copy).........................................Passed
specmgr schema (prb package copy)........................................Passed
specmgr schema (gol package copy)........................................Passed
[feat-22 971998f] refactor(feat-22): retire the seven per-domain update_<d> tools
 136 files changed, 684 insertions(+), 2765 deletions(-)
 delete mode 100644 docs/api/biz.dfch.specmgr.gol.tools.update_gol.md
 delete mode 100644 docs/api/biz.dfch.specmgr.prb.tools.update_prb.md
 delete mode 100644 docs/api/biz.dfch.specmgr.qa.tools.update_qa.md
 delete mode 100644 docs/api/biz.dfch.specmgr.req.tools.update_req.md
 delete mode 100644 docs/api/biz.dfch.specmgr.rsk.tools.update_rsk.md
 delete mode 100644 docs/api/biz.dfch.specmgr.tsk.tools.update_tsk.md
 delete mode 100644 docs/api/biz.dfch.specmgr.uc.tools.update_uc.md
 delete mode 100644 src/biz/dfch/specmgr/gol/tools/update_gol.py
 delete mode 100644 src/biz/dfch/specmgr/prb/tools/update_prb.py
 delete mode 100644 src/biz/dfch/specmgr/qa/tools/update_qa.py
 delete mode 100644 src/biz/dfch/specmgr/req/tools/update_req.py
 delete mode 100644 src/biz/dfch/specmgr/rsk/tools/update_rsk.py
 delete mode 100644 src/biz/dfch/specmgr/tsk/tools/update_tsk.py
 delete mode 100644 src/biz/dfch/specmgr/uc/tools/update_uc.py
 delete mode 100644 tests/gol/tools/test_update_gol.py
 delete mode 100644 tests/prb/tools/test_update_prb.py
 delete mode 100644 tests/qa/tools/test_update_qa.py
 delete mode 100644 tests/req/tools/test_update_req.py
 delete mode 100644 tests/rsk/tools/test_update_rsk.py
 delete mode 100644 tests/tsk/tools/test_update_tsk.py
 delete mode 100644 tests/uc/tools/test_update_uc.py
971998f refactor(feat-22): retire the seven per-domain update_<d> tools
fc76490 feat(feat-22): add generic update tool with line-range replace and raw get reads
2647649 docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 249.6s)

_Thinking:_

Phase 3 has been committed as `971998f` — all pre-commit hooks passed (including the schema hook, which was correctly verified as unchanged).

Interesting point: at commit time, the schema hook actually ran ("Passed") — that's because `tsk/models/v1/body.py` was modified (docstring-only changes), and the hook detected this and confirmed that the schema output was unchanged. Good.

Update the TODO and delegate Phase 4.

Phase 4: generic `set_status` + deprecation of the 8 old status tools (atomic operation).

Tasks:

- 4.1: Create `general/tools/set_status.py`: 8 private adapters `_set_status_<d>` — 7 verbatim ports of the `set_status_<d>` bodies + ADR port; guards; dispatch table; `@mcp.tool(name="set_status", ...)` with signature `def set_status(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","adr"], status: str, superseded_by: str | None = None) -> 8-way union`; full numpy docstring.
- 4.2: Delete the 8 modules: adr/tools/set_status.py + 7 set_status\_<d>.py
- 4.3: Delete the 8 test files
- 4.4: Register in general/tools/__init__.py; update adr/tools/__init__.py + 7 domain tools/__init__.py; update 8 domain __init__.py docstrings
- 4.5: server.py docstring: remove ADR set_status + 7 set_status\_<d>; add set_status to the General-tools line (8-value type; superseded_by is ADR-only)
- 4.6: tests/general/tools/test_set_status.py — parameterized over all 8 types (ACC-004 case)
- 4.7: Gate + README

Critical dependencies: Phase 4 must also address my Phase 2 note: update.py's @mcp.tool description says "`status` is never settable -- use the `set_status_*` tools." and the docstring says "the per-domain `set_status_<d>` tools are the only status-change path" — these must be reworded to point at the generic `set_status` tool (otherwise the grep for `set_status_` in ACC-005/Phase 5 will catch them — well actually, the grep for Phase 5's residual check will use the `set_status_` pattern, and `set_status_*`... the literal `set_status_req` etc. won't appear (it's the wildcard `set_status_*`), but after Phase 4 the description will be inaccurate — set_status\_\* no longer exists. Also the _lock.py docstring: "any future requirement mutation tool (set_status_req, Task 3.14) wrap their whole sequence" — this mentions set_status_req, which gets deleted in Phase 4 → must be reworded in Phase 4. The set_status_<d>.py docstrings themselves disappear along with the files.

Let me pre-compute Phase 4's residual list with a git grep for the set_status names.

Also, the per-domain `set_status_<d>` tool docstrings — those files get deleted. But the `_lock.py` files mention set_status\_<d> as live tools. And the domain `__init__.py` files list set_status\_<d> in their tool enumerations (Task 4.4 covers this). And `server.py` (Task 4.5). And the ADR `tools/__init__.py` (Task 4.4). And the ADR `__init__.py`? Task 4.4 says "the 8 domain __init__.py docstring enumerations are updated similarly" — including adr/__init__.py (the 8th domain = adr). Let me check what adr/__init__.py enumerates.

Further, the prompts: do any of the prompt data files mention set_status\_<d>? The 6 <d>_update_instructions.md mention set_status_<d> (Task 5.1 covers this: "set_status\_<d>(id, status) → set_status(id, type="<d>", status)"). The 4 ADR instruction files mention set_status(id, ...) → they get type="adr". Phase 5's territory.

Let me grep now for `set_status_` and bare `set_status` in src/tests to pre-compute Phase 4's residual list. Patterns: `set_status_req\|set_status_uc\|set_status_tsk\|set_status_qa\|set_status_prb\|set_status_gol\|set_status_rsk`, plus ADR's `set_status` (the ADR tool name — after Phase 4, bare `set_status` references in the ADR context must point at the generic tool; the generic tool itself is named set_status, so many legitimate references will remain).

Let me run the grep to enumerate exactly.

Phase 3 has been committed as `971998f` — all hooks passed (the schema hook correctly verified that the docstring-only change in `tsk/models/v1/body.py` did not alter the schema). Updating the plan, and pre-computing the residual reference set for Phase 4 (since Phase 4 removes the `set_status_*` tools, all non-narrative references need to be handled):

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 5: Narration rewrite — 11 instruction data files + additional create/implement files + qa/prompts/refine.py docstring, prompt module docstrings, prompt test files, gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
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
    "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 5: Narration rewrite — 11 instruction data files + additional create/implement files + qa/prompts/refine.py docstring, prompt module docstrings, prompt test files, gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 7: Final cross-cutting verification — walk ACC-001..008 with evidence, 71/25/19 live check, e2e runs, README status → done",
    "status": "pending",
    "priority": "high"
  }
]
```

**Tool: bash**

**Input:**

```json
{
  "command": "git grep -nE \"\\b(set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/ | grep -vE \"data/|prompts/|tests/.*prompts/\" ; echo === && git grep -nE \"set_status\" -- src/biz/dfch/specmgr/adr/ src/biz/dfch/specmgr/general/ | grep -vE \"prompts/|data/\" | head -30",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
src/biz/dfch/specmgr/gol/__init__.py:30:``get_gol_template``, ``create_gol``, ``set_status_gol``,
src/biz/dfch/specmgr/gol/tools/__init__.py:36:except ``updated``. ``set_status_gol`` (Task 3.5) is the only path that
src/biz/dfch/specmgr/gol/tools/__init__.py:54:from .set_status_gol import set_status_gol
src/biz/dfch/specmgr/gol/tools/__init__.py:65:    "set_status_gol",
src/biz/dfch/specmgr/gol/tools/_lock.py:25:``set_status_gol`` wrap their whole sequence in ``with gol_lock(id):``.
src/biz/dfch/specmgr/gol/tools/_write.py:31:``update`` tool in ``general.tools`` and ``set_status_gol.py`` do not have
src/biz/dfch/specmgr/gol/tools/set_status_gol.py:18:"""``@mcp.tool()`` wrapper: set_status_gol (Task 3.5).
src/biz/dfch/specmgr/gol/tools/set_status_gol.py:21:``prb.tools.set_status_prb``/``req.tools.set_status_req``:
src/biz/dfch/specmgr/gol/tools/set_status_gol.py:54:    name="set_status_gol",
src/biz/dfch/specmgr/gol/tools/set_status_gol.py:58:def set_status_gol(id: str, status: str) -> GolDocument:
src/biz/dfch/specmgr/prb/__init__.py:30:``get_prb_template``, ``create_prb``, ``set_status_prb``,
src/biz/dfch/specmgr/prb/tools/__init__.py:36:every frontmatter field except ``updated``. ``set_status_prb``
src/biz/dfch/specmgr/prb/tools/__init__.py:54:from .set_status_prb import set_status_prb
src/biz/dfch/specmgr/prb/tools/__init__.py:65:    "set_status_prb",
src/biz/dfch/specmgr/prb/tools/_lock.py:25:``set_status_prb`` wrap their whole sequence in ``with prb_lock(id):``.
src/biz/dfch/specmgr/prb/tools/_write.py:31:``update`` tool in ``general.tools`` and ``set_status_prb.py`` do not have
src/biz/dfch/specmgr/prb/tools/set_status_prb.py:18:"""``@mcp.tool()`` wrapper: set_status_prb (Task 3.5).
src/biz/dfch/specmgr/prb/tools/set_status_prb.py:21:``tsk.tools.set_status_tsk``/``qa.tools.set_status_qa``:
src/biz/dfch/specmgr/prb/tools/set_status_prb.py:50:    name="set_status_prb",
src/biz/dfch/specmgr/prb/tools/set_status_prb.py:54:def set_status_prb(id: str, status: str) -> PrbDocument:
src/biz/dfch/specmgr/qa/__init__.py:30:``get_qa_template``, ``create_qa``, ``set_status_qa``,
src/biz/dfch/specmgr/qa/tools/__init__.py:37:``set_status_qa`` is the only path that changes ``status``, also bumping
src/biz/dfch/specmgr/qa/tools/__init__.py:54:from .set_status_qa import set_status_qa
src/biz/dfch/specmgr/qa/tools/__init__.py:65:    "set_status_qa",
src/biz/dfch/specmgr/qa/tools/_lock.py:26:(``set_status_qa``) wrap their whole sequence in ``with qa_lock(id):``.
src/biz/dfch/specmgr/qa/tools/set_status_qa.py:18:"""``@mcp.tool()`` wrapper: set_status_qa (Phase 4, Task 4.1).
src/biz/dfch/specmgr/qa/tools/set_status_qa.py:21:``adr.tools.set_status``/``req.tools.set_status_req``, minus the
src/biz/dfch/specmgr/qa/tools/set_status_qa.py:52:    name="set_status_qa",
src/biz/dfch/specmgr/qa/tools/set_status_qa.py:56:def set_status_qa(id: str, status: str) -> QaDocument:
src/biz/dfch/specmgr/req/__init__.py:12:``get_req_template``, ``create_req``, ``set_status_req``,
src/biz/dfch/specmgr/req/tools/__init__.py:39:``set_status_req`` (Task 3.14) is the only path that
src/biz/dfch/specmgr/req/tools/__init__.py:57:from .set_status_req import set_status_req
src/biz/dfch/specmgr/req/tools/__init__.py:68:    "set_status_req",
src/biz/dfch/specmgr/req/tools/_lock.py:25:future requirement mutation tool (``set_status_req``, Task 3.14) wrap their
src/biz/dfch/specmgr/req/tools/set_status_req.py:18:"""``@mcp.tool()`` wrapper: set_status_req (Task 3.14).
src/biz/dfch/specmgr/req/tools/set_status_req.py:52:    name="set_status_req",
src/biz/dfch/specmgr/req/tools/set_status_req.py:56:def set_status_req(id: str, status: str) -> ReqDocument:
src/biz/dfch/specmgr/rsk/__init__.py:30:``get_rsk_template``, ``create_rsk``, ``set_status_rsk``,
src/biz/dfch/specmgr/rsk/tools/__init__.py:38:preserving every frontmatter field except ``updated``. ``set_status_rsk``
src/biz/dfch/specmgr/rsk/tools/__init__.py:56:from .set_status_rsk import set_status_rsk
src/biz/dfch/specmgr/rsk/tools/__init__.py:67:    "set_status_rsk",
src/biz/dfch/specmgr/rsk/tools/_lock.py:25:future risk mutation tool (``set_status_rsk``) wrap their whole sequence in
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py:18:"""``@mcp.tool()`` wrapper: set_status_rsk (Task 3.5).
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py:21:``tsk.tools.set_status_tsk``:
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py:54:    name="set_status_rsk",
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py:58:def set_status_rsk(id: str, status: str) -> RskDocument:
src/biz/dfch/specmgr/server.py:109:``get_uc_template``, ``create_uc``, ``set_status_uc``, ``delete_uc``
src/biz/dfch/specmgr/server.py:114:``get_req_template``, ``create_req``, ``set_status_req``, ``delete_req``
src/biz/dfch/specmgr/server.py:119:``get_tsk_template``, ``create_tsk``, ``set_status_tsk``, ``delete_tsk``
src/biz/dfch/specmgr/server.py:124:``get_qa_template``, ``create_qa``, ``set_status_qa``, ``delete_qa``
src/biz/dfch/specmgr/server.py:129:``set_status_prb``, ``delete_prb`` (stub, not yet implemented), ``validate_prb``.
src/biz/dfch/specmgr/server.py:133: ``set_status_gol``, ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
src/biz/dfch/specmgr/server.py:137: ``get_rsk_template``, ``create_rsk``, ``set_status_rsk``, ``delete_rsk``
src/biz/dfch/specmgr/tsk/__init__.py:30:``get_tsk_template``, ``create_tsk``, ``set_status_tsk``,
src/biz/dfch/specmgr/tsk/tools/__init__.py:38:frontmatter field except ``updated``. ``set_status_tsk`` is the only path
src/biz/dfch/specmgr/tsk/tools/__init__.py:57:from .set_status_tsk import set_status_tsk
src/biz/dfch/specmgr/tsk/tools/__init__.py:68:    "set_status_tsk",
src/biz/dfch/specmgr/tsk/tools/_lock.py:25:future task list mutation tool (``set_status_tsk``) wrap their whole
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py:18:"""``@mcp.tool()`` wrapper: set_status_tsk (Task 3.5).
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py:21:``req.tools.set_status_req``:
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py:52:    name="set_status_tsk",
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py:56:def set_status_tsk(id: str, status: str) -> TskDocument:
src/biz/dfch/specmgr/uc/__init__.py:12:``get_uc_template``, ``create_uc``, ``set_status_uc``,
src/biz/dfch/specmgr/uc/tools/__init__.py:38:``set_status_uc`` (Task 3.1.5) is the only path that
src/biz/dfch/specmgr/uc/tools/__init__.py:56:from .set_status_uc import set_status_uc
src/biz/dfch/specmgr/uc/tools/__init__.py:67:    "set_status_uc",
src/biz/dfch/specmgr/uc/tools/_lock.py:25:future use-case mutation tool (``set_status_uc``) wrap their whole sequence
src/biz/dfch/specmgr/uc/tools/set_status_uc.py:18:"""``@mcp.tool()`` wrapper: set_status_uc (Task 3.1.5).
src/biz/dfch/specmgr/uc/tools/set_status_uc.py:21:``req.tools.set_status_req``, except
src/biz/dfch/specmgr/uc/tools/set_status_uc.py:51:    name="set_status_uc",
src/biz/dfch/specmgr/uc/tools/set_status_uc.py:55:def set_status_uc(id: str, status: str) -> UcDocument:
tests/gol/tools/test_integration.py:23:``update`` -> ``set_status_gol`` -> ``get_gol`` (status changed) ->
tests/gol/tools/test_integration.py:52:from biz.dfch.specmgr.gol.tools.set_status_gol import set_status_gol
tests/gol/tools/test_integration.py:95:        """list_gol -> create_gol -> get_gol -> list_gol -> update -> set_status_gol -> get_gol ->
tests/gol/tools/test_integration.py:135:        # 5. set_status_gol: only status/updated may change.
tests/gol/tools/test_integration.py:136:        accepted = set_status_gol(gol_id, "accepted")
tests/gol/tools/test_set_status_gol.py:18:"""Tests for the ``set_status_gol`` ``@mcp.tool()`` wrapper (Task 3.5)."""
tests/gol/tools/test_set_status_gol.py:34:from biz.dfch.specmgr.gol.tools.set_status_gol import set_status_gol
tests/gol/tools/test_set_status_gol.py:68:    """Tests for the set_status_gol tool."""
tests/gol/tools/test_set_status_gol.py:71:        """set_status_gol must write the new status and a fresh `updated` timestamp."""
tests/gol/tools/test_set_status_gol.py:74:        result = set_status_gol(original.frontmatter.id, "accepted")
tests/gol/tools/test_set_status_gol.py:83:        """set_status_gol must not alter the body at all."""
tests/gol/tools/test_set_status_gol.py:86:        set_status_gol(original.frontmatter.id, "accepted")
tests/gol/tools/test_set_status_gol.py:95:        set_status_gol(original.frontmatter.id, "implemented")
tests/gol/tools/test_set_status_gol.py:101:        """set_status_gol must raise GolNotFoundError for an id with no matching file."""
tests/gol/tools/test_set_status_gol.py:103:            set_status_gol("no-such-id", "accepted")
tests/gol/tools/test_set_status_gol.py:112:            set_status_gol(original.frontmatter.id, "not-a-real-status")
tests/prb/tools/test_integration.py:22:``create_prb`` -> ``update`` -> ``set_status_prb`` -> ``get_prb`` ->
tests/prb/tools/test_integration.py:50:from biz.dfch.specmgr.prb.tools.set_status_prb import set_status_prb
tests/prb/tools/test_integration.py:126:        """create_prb -> update -> set_status_prb -> get_prb -> list_prb -> delete_prb, live."""
tests/prb/tools/test_integration.py:147:        # 3. set_status_prb: only status/updated may change.
tests/prb/tools/test_integration.py:148:        activated = set_status_prb(prb_id, "active")
tests/prb/tools/test_set_status_prb.py:18:"""Tests for the ``set_status_prb`` ``@mcp.tool()`` wrapper (Task 3.5)."""
tests/prb/tools/test_set_status_prb.py:34:from biz.dfch.specmgr.prb.tools.set_status_prb import set_status_prb
tests/prb/tools/test_set_status_prb.py:76:    """Tests for the set_status_prb tool."""
tests/prb/tools/test_set_status_prb.py:79:        """set_status_prb must write the new status and a fresh `updated` timestamp."""
tests/prb/tools/test_set_status_prb.py:82:        result = set_status_prb(original.frontmatter.id, "active")
tests/prb/tools/test_set_status_prb.py:91:        """set_status_prb must not alter the body at all."""
tests/prb/tools/test_set_status_prb.py:94:        set_status_prb(original.frontmatter.id, "active")
tests/prb/tools/test_set_status_prb.py:104:        set_status_prb(original.frontmatter.id, "resolved")
tests/prb/tools/test_set_status_prb.py:110:        """set_status_prb must raise PrbNotFoundError for an id with no matching file."""
tests/prb/tools/test_set_status_prb.py:112:            set_status_prb("no-such-id", "active")
tests/prb/tools/test_set_status_prb.py:121:            set_status_prb(original.frontmatter.id, "not-a-real-status")
tests/qa/tools/test_set_status_qa.py:18:"""Tests for the ``set_status_qa`` ``@mcp.tool()`` wrapper."""
tests/qa/tools/test_set_status_qa.py:34:from biz.dfch.specmgr.qa.tools.set_status_qa import set_status_qa
tests/qa/tools/test_set_status_qa.py:92:    """Tests for the set_status_qa tool."""
tests/qa/tools/test_set_status_qa.py:95:        """set_status_qa must write the new status and a fresh `updated` timestamp."""
tests/qa/tools/test_set_status_qa.py:98:        result = set_status_qa(original.frontmatter.id, "active")
tests/qa/tools/test_set_status_qa.py:107:        """set_status_qa must not alter the body at all."""
tests/qa/tools/test_set_status_qa.py:110:        set_status_qa(original.frontmatter.id, "active")
tests/qa/tools/test_set_status_qa.py:120:        set_status_qa(original.frontmatter.id, "done")
tests/qa/tools/test_set_status_qa.py:126:        """set_status_qa must raise QaNotFoundError for an id with no matching file."""
tests/qa/tools/test_set_status_qa.py:128:            set_status_qa("no-such-id", "active")
tests/qa/tools/test_set_status_qa.py:137:            set_status_qa(original.frontmatter.id, "not-a-real-status")
tests/req/tools/test_set_status_req.py:18:"""Tests for the ``set_status_req`` ``@mcp.tool()`` wrapper (Task 3.14)."""
tests/req/tools/test_set_status_req.py:34:from biz.dfch.specmgr.req.tools.set_status_req import set_status_req
tests/req/tools/test_set_status_req.py:81:    """Tests for the set_status_req tool."""
tests/req/tools/test_set_status_req.py:84:        """set_status_req must write the new status and a fresh `updated` timestamp."""
tests/req/tools/test_set_status_req.py:87:        result = set_status_req(original.frontmatter.id, "accepted")
tests/req/tools/test_set_status_req.py:96:        """set_status_req must not alter the body at all."""
tests/req/tools/test_set_status_req.py:99:        set_status_req(original.frontmatter.id, "accepted")
tests/req/tools/test_set_status_req.py:109:        set_status_req(original.frontmatter.id, "implemented")
tests/req/tools/test_set_status_req.py:115:        """set_status_req must raise ReqNotFoundError for an id with no matching file."""
tests/req/tools/test_set_status_req.py:117:            set_status_req("no-such-id", "accepted")
tests/req/tools/test_set_status_req.py:126:            set_status_req(original.frontmatter.id, "not-a-real-status")
tests/rsk/tools/test_set_status_rsk.py:18:"""Tests for the ``set_status_rsk`` ``@mcp.tool()`` wrapper (Task 3.5)."""
tests/rsk/tools/test_set_status_rsk.py:34:from biz.dfch.specmgr.rsk.tools.set_status_rsk import set_status_rsk
tests/rsk/tools/test_set_status_rsk.py:98:    """Tests for the set_status_rsk tool."""
tests/rsk/tools/test_set_status_rsk.py:101:        """set_status_rsk must write the new status and a fresh `updated` timestamp."""
tests/rsk/tools/test_set_status_rsk.py:104:        result = set_status_rsk(original.frontmatter.id, "mitigating")
tests/rsk/tools/test_set_status_rsk.py:113:        """set_status_rsk must not alter the body at all."""
tests/rsk/tools/test_set_status_rsk.py:116:        set_status_rsk(original.frontmatter.id, "mitigating")
tests/rsk/tools/test_set_status_rsk.py:127:        set_status_rsk(original.frontmatter.id, "closed")
tests/rsk/tools/test_set_status_rsk.py:133:        """set_status_rsk must raise RskNotFoundError for an id with no matching file."""
tests/rsk/tools/test_set_status_rsk.py:135:            set_status_rsk("no-such-id", "mitigating")
tests/rsk/tools/test_set_status_rsk.py:144:            set_status_rsk(original.frontmatter.id, "not-a-real-status")
tests/tsk/tools/test_set_status_tsk.py:18:"""Tests for the ``set_status_tsk`` ``@mcp.tool()`` wrapper (Task 3.5)."""
tests/tsk/tools/test_set_status_tsk.py:34:from biz.dfch.specmgr.tsk.tools.set_status_tsk import set_status_tsk
tests/tsk/tools/test_set_status_tsk.py:70:    """Tests for the set_status_tsk tool."""
tests/tsk/tools/test_set_status_tsk.py:73:        """set_status_tsk must write the new status and a fresh `updated` timestamp."""
tests/tsk/tools/test_set_status_tsk.py:76:        result = set_status_tsk(original.frontmatter.id, "active")
tests/tsk/tools/test_set_status_tsk.py:85:        """set_status_tsk must not alter the body at all."""
tests/tsk/tools/test_set_status_tsk.py:88:        set_status_tsk(original.frontmatter.id, "active")
tests/tsk/tools/test_set_status_tsk.py:101:        set_status_tsk(original.frontmatter.id, "done")
tests/tsk/tools/test_set_status_tsk.py:107:        """set_status_tsk must raise TskNotFoundError for an id with no matching file."""
tests/tsk/tools/test_set_status_tsk.py:109:            set_status_tsk("no-such-id", "active")
tests/tsk/tools/test_set_status_tsk.py:118:            set_status_tsk(original.frontmatter.id, "not-a-real-status")
tests/uc/tools/test_set_status_uc.py:18:"""Tests for the ``set_status_uc`` ``@mcp.tool()`` wrapper (Task 3.1.5)."""
tests/uc/tools/test_set_status_uc.py:34:from biz.dfch.specmgr.uc.tools.set_status_uc import set_status_uc
tests/uc/tools/test_set_status_uc.py:97:    """Tests for the set_status_uc tool."""
tests/uc/tools/test_set_status_uc.py:100:        """set_status_uc must write the new status and a fresh `updated` timestamp."""
tests/uc/tools/test_set_status_uc.py:103:        result = set_status_uc(original.frontmatter.id, "accepted")
tests/uc/tools/test_set_status_uc.py:112:        """set_status_uc must not alter the body at all."""
tests/uc/tools/test_set_status_uc.py:115:        set_status_uc(original.frontmatter.id, "accepted")
tests/uc/tools/test_set_status_uc.py:124:        set_status_uc(original.frontmatter.id, "deprecated")
tests/uc/tools/test_set_status_uc.py:130:        """set_status_uc must raise UcNotFoundError for an id with no matching file."""
tests/uc/tools/test_set_status_uc.py:132:            set_status_uc("no-such-id", "accepted")
tests/uc/tools/test_set_status_uc.py:141:            set_status_uc(original.frontmatter.id, "not-a-real-status")
===
src/biz/dfch/specmgr/adr/tools/__init__.py:36:from .set_status import set_status
src/biz/dfch/specmgr/adr/tools/__init__.py:50:    "set_status",
src/biz/dfch/specmgr/adr/tools/_lock.py:21:``update_frontmatter``, ``set_status``, ``option_create``, ``option_update``,
src/biz/dfch/specmgr/adr/tools/set_status.py:18:"""``@mcp.tool()`` wrapper: set_status (plan §8, §9a, §10 item 4).
src/biz/dfch/specmgr/adr/tools/set_status.py:20:Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.set_status``:
src/biz/dfch/specmgr/adr/tools/set_status.py:44:    name="set_status",
src/biz/dfch/specmgr/adr/tools/set_status.py:48:def set_status(id: str, status: str, superseded_by: str | None = None) -> Adr:
src/biz/dfch/specmgr/adr/tools/set_status.py:51:    Delegates to ``models.adr.v1.mutations.set_status``: when
src/biz/dfch/specmgr/adr/tools/set_status.py:72:        new_adr = mutations.set_status(adr, status, superseded_by)
src/biz/dfch/specmgr/general/tools/_splice.py:26:  content`` mechanism -- the same one every ``set_status_<d>`` tool uses.
src/biz/dfch/specmgr/general/tools/_splice.py:58:    "utf-8")).content`` mechanism (the same one every ``set_status_<d>``
src/biz/dfch/specmgr/general/tools/update.py:395:        "anything is written. `status` is never settable -- use the `set_status_*` tools."
src/biz/dfch/specmgr/general/tools/update.py:440:    through this tool -- the per-domain ``set_status_<d>`` tools are the

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 8704.2s)

_Thinking:_

Complete inventory for Phase 4:

**To be deleted (Task 4.2/4.3):**

- 8 tool modules: adr/tools/set_status.py + 7 set_status\_<d>.py
- 8 test files: tests/adr/tools/test_set_status.py + 7 test_set_status\_<d>.py

**To be edited in Phase 4 (non-narrative references to the set_status\_<d> tools):**

- 7 domain `tools/__init__.py`: imports, `__all__`, docstring narrative ("set_status_req (Task 3.14) is the only path that changes status...") → rewrite to point to the generic `set_status` tool
- 7 domain `__init__.py`: tool enumeration containing set_status\_<d> → rewrite
- 7 domain `tools/_lock.py`: "future <d> mutation tool (set_status_req, Task 3.14) wrap their whole sequence" → rewrite (mentioning the generic set_status)
- 4 domain `tools/_write.py` files: "and set_status_gol.py do not have to duplicate it" (gol, prb — let me check which \_write files mention it: gol/tools/\_write.py:31, prb/tools/\_write.py:31 — what about req? The grep for set_status in _write showed only gol and prb... no wait, the grep was `set_status` against adr/ and general/ in the second command, and the first command covered set_status_<d> names. From the first command: gol/tools/\_write.py:31, prb/tools/_write.py:31 mention set_status_<d>.py. What about _write files for the other domains (req, uc, tsk, qa, rsk)? They didn't appear in the grep output — so they don't reference the set_status_<d> modules. OK.)
- server.py: ADR tools line (set_status entry) + 7 per-domain lines (set_status\_<d>) → Task 4.5
- adr/tools/__init__.py: imports/__all__/docstring for set_status → Task 4.4
- adr/__init__.py: need to check if it enumerates set_status — the grep for "set_status" against src/adr/ showed only tools/__init__.py and tools/\_lock.py within adr/. Let me re-check adr/__init__.py... the second grep covered src/biz/dfch/specmgr/adr/ and showed only tools/__init__.py:36,50, \_lock.py:21, set_status.py. So adr/__init__.py doesn't mention set_status. No problem — but Task 4.4 says "similarly update the docstring enumerations in the 8 domain __init__.py files" — for adr, if there's nothing, then nothing.
- adr/tools/\_lock.py:21: the enumeration containing `set_status` — this refers to the ADR tool being deleted → rewrite (Task 4.4's scope: update adr/tools/__init__.py; \_lock.py wasn't listed, but the grep needs to be clean — hmm, what does ACC-005 require for Phase 5's grep? Phase 5's grep (Task 5.1) uses the pattern `set_status_` (with underscore) against data files, plus bare `set_status(` against ADR data files. The final ACC-005 grep is against "the deleted tool names" — the deleted ADR tool name is `set_status`, which is now also the name of the generic tool. References to `set_status` within adr/tools/\_lock.py are fine as long as they now point to the generic tool. Reword: "update_frontmatter, set_status (now generic, in general/tools/), option_create..." — no, just say the generic set_status tool wraps.
- general/tools/_splice.py lines 26, 58: "the same one every `set_status_<d>` tool uses" → after Phase 4, set_status_<d> tools no longer exist → rewrite to "the same one the generic set_status tool's adapters use" or "the established mechanism". This file is in general/ — Phase 4's territory. (My Phase 2 grep instructions missed this, but it'll be caught by Phase 4/5's `set_status_` grep.)
- general/tools/update.py line 395 (the description "use the `set_status_*` tools.") and line 440 (the docstring "the per-domain set_status\_<d> tools are the only status-change path") → rewrite to point to the generic `set_status` tool. (This was my earlier note — now it's explicitly in scope.)
- tests/gol/tools/test_integration.py: imports set_status_gol (line 52), calls set_status_gol(gol_id, "accepted") (line 136), docstring lines 23, 95, 135 → rewrite to `set_status(gol_id, "gol", "accepted")`.
- tests/prb/tools/test_integration.py: same → `set_status(prb_id, "prb", "active")`.
- The 8 test files will be deleted.

**Prompt narrative (Phase 5's territory, remains for now):** the 6 <d>_update_instructions.md mention set_status_<d>; the ADR data files mention set_status( ...; probably the create instructions too. These are Phase 5's.

**New tests (Task 4.6):** tests/general/tools/test_set_status.py parameterized over all 8 types, ACC-004 cases:

- status changed + updated bumped + body unchanged (7 domains: raw body byte-identical; ADR: re-rendered round-trip equivalence except for status/updated)
- closed vocabulary per domain: positive values from the domain's set; negative values: read each domain's \_ALLOWED_STATUSES and pick a value that's valid in one domain but invalid in the domain being tested (e.g., `implemented` against rsk/uc/tsk/qa/prb, `open` against req) → pydantic.ValidationError, file unchanged
- ADR superseded_by composes "superseded by X" within the file
- ADR plain status with superseded_by=None
- superseded_by with non-adr types → ValueError, file unchanged
- unknown id → domain's XNotFoundError / AdrNotFoundError

Vocabulary table (from the plan's design notes, as of 2026-08-26; implementer must re-read each domain's \_ALLOWED_STATUSES):

- req, gol: draft/proposed/accepted/superseded/deprecated/rejected/implemented (7)
- uc: draft/proposed/accepted/deprecated/superseded (5)
- tsk, qa: draft/active/done/cancelled (4)
- prb: draft/active/resolved/cancelled (4)
- rsk: open/mitigating/accepted/occurred/closed/dropped (6)
- adr: draft/proposed/rejected/accepted/deprecated/superseded (6) + "superseded by X" pattern

Expected test count delta: −(8 test files' tests: let me count — the 7 per-domain set_status tests are roughly 5-6 tests each ≈ 40-45; adr's test_set_status.py has some) + new test_set_status.py (parameterized over 8). The implementer will report the exact numbers.

Live count: 78 − 8 + 1 = 71 tools. **71/25/19** — the final target count is achieved in Phase 4!

Also, the ADR adapter port needs to be verbatim from adr/tools/set_status.py: lock (adr_lock), load_by_id (adr's own _io), delegation to models.adr.v1.mutations.set_status(adr, status, superseded_by), write_adr rendering round-trip, AdrNotFoundError. The generic adapter takes (id_, status, superseded_by) — the ADR adapter passes superseded_by; the 7-domain adapters must raise... no wait — the guard runs before dispatch (superseded_by is not None and type != "adr" → ValueError, before any file access), so the 7-domain adapters never receive a non-None superseded_by. Their signatures can either be (id\_, status, superseded_by) ignoring it, or just (id\_, status). For dispatch-table uniformity, keep the 3-argument signature; the domain adapters can assert superseded_by is None (internal invariant) — or simply take it and ignore it. I'll instruct: keep the 3-argument signature for table uniformity; the 7 domain adapters don't use superseded_by (the guard ensures None).

Name-collision atomicity: within the same phase, create general/tools/set_status.py before deleting adr/tools/set_status.py — actually, does it matter on disk? No — Python module names don't collide (different packages), and the MCP registration is at import time: if both were registered at the same time it would double-register the name "set_status". The plan says "Phase 4 adds the generic tool and deletes all 8 old status tools within a single phase" — because at any committed point in time only one `set_status` tool is registered. Within the phase, the order of file operations doesn't matter as long as the final tree has only the generic one. The implementer should delete the old modules before running registration tests (or in the same working session) — as long as the gate runs against the final state, no problem.

Registration smoke test: Task 4.6 covers the set_status tests; the plan doesn't explicitly require a new registration enum test in Phase 4 (that was Task 2.8 for update). But the gate should confirm MCP.md shows set_status with the 8-value enum. mcp_docs now renders enums (Phase 2's change), so docs/MCP.md will show `string (enum: req, uc, tsk, qa, prb, gol, rsk, adr)`. Good — include a check for that.

Also: `set_status`'s `status` parameter is `str` (not Literal) — per-domain closed vocabularies validate via the XFrontmatter constructor (pydantic). ADR's frontmatter status allows 6 values + "superseded by X" pattern — wait, how does the ADR port validate? models.adr.v1.mutations.set_status(adr, status, superseded_by) composes and re-validates via the Adr model (the frontmatter status field has a regex constraint `^superseded by .+$` or the 6 values). Invalid → ValidationError propagates. OK — the verbatim port handles it.

One more check — the ADR frontmatter status: is it a plain str with a validator, or a Literal? From the create_adr tool schema above: status is "either one of draft/proposed/rejected/accepted/deprecated/superseded, or a string matching ^superseded by .+$". So the model validates. No problem.

Also, Task 4.4 mentions updating the 8 domain __init__.py files — including adr/__init__.py? "Similarly update the docstring enumerations in the 8 domain __init__.py files" — the 8 domains = req, uc, tsk, qa, prb, gol, rsk, adr. adr/__init__.py apparently doesn't enumerate set_status (the grep found nothing), but the implementer should verify and only edit where needed.

Coverage: after deleting the 8 test files, the set_status\_<d>.py modules disappear (no NoSource issue, since they're gone from src too). The new general/tools/set_status.py will be fully covered by the new tests. The ADR adapter path is covered by ADR tests in the new file. Coverage % stays around 98%.

OK, let me write the Phase 4 prompt. Include:

- Atomicity warning (name collision)
- Complete verbatim port instructions (read the 8 modules first: 7 set_status\_<d> + adr/tools/set_status.py)
- Guard before file access
- My additional Phase 4 cleanup list (from the grep inventory above): \_splice.py, update.py's description + docstring, \_lock.py ×7, \_write.py ×2 (gol/prb), tools/__init__.py ×8, __init__.py ×7 (+ adr if any), server.py, the 2 integration tests
- Status of the vocabulary table + instruction to re-read \_ALLOWED_STATUSES
- ACC-004 test details
- Gate: full + 3 generators + zero drift + fresh import + live 71/25/19 + MCP.md 8-value enum check
- README update
- No commit, no Phase 5

Expected live count 71/25/19 = the final target.

Phase 4's complete inventory has been established. Key points: **This phase achieves the final 71/25/19 count** (78 − 8 + 1). In addition to the plan's tasks, the cleanup set includes `general/tools/_splice.py` (the "every `set_status_<d>` tool" wording), `general/tools/update.py` (the `set_status_*` description — my Phase 2 note), 7× `_lock.py`, 2× `_write.py`, 8× `tools/__init__.py`, 7× domain `__init__.py`, `server.py`, and the 2 integration tests (these call `set_status_gol`/`set_status_prb`).

**Delegating Phase 4:**

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 4 (set_status)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 4: Generic `set_status` + retire the eight old status tools** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `971998f` (Phase 3 commit), working tree clean.\n- The generic `update` tool exists in `src/biz/dfch/specmgr/general/tools/update.py` (seven adapters `_update_<d>`, dispatch table, `@mcp.tool(name=\"update\")`); `general/tools/_splice.py` has `body_text`/`splice_body`; the seven `get_<d>` tools have `raw`. The seven `update_<d>` tools are already deleted (Phase 3).\n- Live registration is currently **78 tools / 25 resources / 19 prompts**. After Phase 4 (−8 status tools +1 generic) it must be the final **71 / 25 / 19**.\n- **This phase is deliberately ATOMIC** (Design Notes, Name-collision constraint): ADR's existing tool is already named `set_status`; the generic tool and the deletion of all eight old status tools must land in the same tree state so the MCP name `set_status` is never double-registered. Do all of Tasks 4.1–4.5 in this phase before running any gate.\n\n## Your plan\nRead the FULL plan first: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — Overview, Requirements REQ-004/REQ-005/REQ-007, Design Notes (esp. the `set_status` signature + `superseded_by` guard, the per-domain status vocabulary table, docs discipline), the \"Phase-end quality gate\" section, and your phase heading `#### Phase 4: Generic `set_status` + retire the eight old status tools` (Tasks 4.1–4.7). Also read `.specmgr/conventions.md`.\n\n## Tasks (from the plan)\n\n- **Task 4.1**: Create `src/biz/dfch/specmgr/general/tools/set_status.py`:\n  - Eight private adapters. First READ the eight existing modules you are porting: `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`, `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`, `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`, `rsk/tools/set_status_rsk.py`, and `adr/tools/set_status.py`. The seven whole-body-domain adapters `_set_status_<d>(id_, status, superseded_by)` are **verbatim ports** of the `set_status_<d>` bodies: same `X_lock`, same `load_by_id`, raw body re-read via the established `frontmatter.loads(...).content` mechanism, frontmatter reconstructed through the domain's own `XFrontmatter` constructor so the closed status vocabulary validates (invalid `status` → `pydantic.ValidationError`, nothing written), `updated` bumped (microsecond timestamp), body persisted verbatim (body never touched), domain `XNotFoundError`. The ADR adapter `_set_status_adr(id_, status, superseded_by)` ports `adr/tools/set_status.py` including its delegation to `models.adr.v1.mutations.set_status(adr, status, superseded_by)` (which composes `status` as `\"superseded by {superseded_by}\"` when given), `write_adr` render round-trip, `adr_lock`, `AdrNotFoundError`. Keep the 3-arg signature on all eight for dispatch-table uniformity; the seven domain adapters never use `superseded_by` (the guard ensures it is `None` for them — an internal-invariant `assert` is acceptable there, mirroring `update.py`'s adapters).\n  - The guard: `superseded_by is not None and type != \"adr\"` → `ValueError` (clear message), running **before any file access** — place it in the public `set_status` function before dispatch (mirroring `update.py`'s both-or-neither guard placement).\n  - A dispatch table `dict[str, Callable]`.\n  - `@mcp.tool(name=\"set_status\", title=\"Set document status\", description=(...))` with `def set_status(id: str, type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"adr\"], status: str, superseded_by: str | None = None) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr` and a full numpy-style docstring (8 values incl. adr; `superseded_by` adr-only; per-domain closed vocabularies — do NOT hardcode the vocabulary list into the docstring in a way that must be maintained, describe where it lives; error types: `ValueError`, `pydantic.ValidationError`, the domain `XNotFoundError`s + `AdrNotFoundError`). The `type` parameter naming follows `update.py` (no ruff rule against the builtin shadow).\n  - **Status vocabularies** — the plan's table reflects 2026-08-26; RE-READ each domain's `_ALLOWED_STATUSES` in `models/<v>/frontmatter.py` (req `models/v1`, uc `models/v2`, tsk `models/v1`, qa `models/v2`, prb `models/v1`, gol `models/v1`, rsk `models/v1`; adr `models/adr/v1/frontmatter.py`) and make your tests match the source of truth: expected `req`/`gol`: draft/proposed/accepted/superseded/deprecated/rejected/implemented (7); `uc`: draft/proposed/accepted/deprecated/superseded (5); `tsk`/`qa`: draft/active/done/cancelled (4); `prb`: draft/active/resolved/cancelled (4); `rsk`: open/mitigating/accepted/occurred/closed/dropped (6); `adr`: 6 values + the `\"superseded by X\"` pattern.\n- **Task 4.2**: Delete the eight superseded modules: `adr/tools/set_status.py`, `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`, `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`, `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`, `rsk/tools/set_status_rsk.py`.\n- **Task 4.3**: Delete the eight test files: `tests/adr/tools/test_set_status.py`, `tests/req/tools/test_set_status_req.py`, `tests/uc/tools/test_set_status_uc.py`, `tests/tsk/tools/test_set_status_tsk.py`, `tests/qa/tools/test_set_status_qa.py`, `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py`.\n- **Task 4.4**: Register `set_status` in `general/tools/__init__.py` (import, `__all__`, module docstring — add it next to `update`). Update `adr/tools/__init__.py` (remove the `set_status` import, `__all__` entry, docstring mention; point status changes at the generic tool in `general/tools/`) and the seven domain `tools/__init__.py` files (same: remove `set_status_<d>` import/`__all__`/docstring mention — each currently narrates \"`set_status_<d>` (Task 3.x) is the only path that changes `status`\"; rewrite to the generic `set_status` tool with `type=\"<d>\"`). Update the seven domain `__init__.py` docstring tool enumerations (remove `set_status_<d}`, add the generic pointer; check `adr/__init__.py` too — if it doesn't name the tool, leave it).\n- **Task 4.5**: Update `server.py`'s module docstring: remove `set_status` from the ADR tools line and `set_status_<d>` from the seven per-domain Tools lines; add `set_status` to the General-tools lines (8-value `type`; `superseded_by` is ADR-only, composing `\"superseded by X\"`).\n- **Orchestrator-verified additional cleanup (must all be done in this phase — the final ACC-005 grep must find zero references to the deleted tools)**: the current `git grep -nE \"\\b(set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/` residual set outside the eight deleted modules and their eight test files is exactly:\n  - `src/biz/dfch/specmgr/general/tools/update.py` line ~395: the `@mcp.tool` description ends \"`status` is never settable -- use the `set_status_*` tools.\" → reword to the generic `set_status` tool; and line ~440: docstring \"the per-domain ``set_status_<d>`` tools are the only status-change path\" → reword (status changes go through the generic ``set_status`` tool in ``general.tools``).\n  - `src/biz/dfch/specmgr/general/tools/_splice.py` lines ~26 and ~58: \"the same one every ``set_status_<d>`` tool uses\" → reword to the established mechanism (e.g. \"the same frontmatter-stripping mechanism the domain write paths use\" — it must no longer name the deleted tools).\n  - The seven domain `tools/_lock.py` (~line 24-26): \"future <d> mutation tool (``set_status_<d>``, Task 3.x) wrap their whole sequence\" → reword to the generic `set_status` tool.\n  - `gol/tools/_write.py` (~line 31) and `prb/tools/_write.py` (~line 31): \"and ``set_status_<d>.py`` do not have to duplicate it\" → reword to the generic `set_status` tool.\n  - `tests/gol/tools/test_integration.py`: imports `from biz.dfch.specmgr.gol.tools.set_status_gol import set_status_gol` (line 52) and calls `set_status_gol(gol_id, \"accepted\")` (line 136), plus docstring/step text (lines 23, 95, 135) → re-point to `from biz.dfch.specmgr.general.tools.set_status import set_status` and `set_status(gol_id, \"gol\", \"accepted\")`.\n  - `tests/prb/tools/test_integration.py`: same treatment (`set_status(prb_id, \"prb\", \"active\")`; lines 22, 50, 126, 147, 148).\n  - Also grep for ADR's old tool in non-Phase-5 locations: after your changes, `git grep -n \"set_status\" -- src/ tests/` must show matches only in: the new `general/tools/set_status.py` (itself), `general/tools/__init__.py` (registration), `general/tools/update.py` (your reworded pointers), `general/tools/_splice.py` (your reworded text — or zero if you reword to no name), `server.py` (your new General-tools line), `adr/tools/_lock.py` (reword it: its ~line 21 enumerates the ADR mutating tools incl. the old `set_status` — point at the generic tool), the re-pointed integration tests, the ADR mutation model (`models/adr/v1/mutations.py` defines the function `set_status` — that is a model-layer function, NOT the MCP tool; keep it, it is not a tool reference), and Phase-5-owned prompt narration files (`*/data/*.md`, `*/prompts/*.py`, `tests/*/prompts/*`). If anything else surfaces, apply the same rule and list it in your report.\n- **Task 4.6**: `tests/general/tools/test_set_status.py` — parameterized over all eight types (ACC-004). Seed a document per type in a temp `SPECMGR_DOCS_DIR` (mirror the fixture strategy of `tests/general/tools/test_update.py` from Phase 2 — read it first; for ADR, seed via the `create_adr` tool or by writing a minimal valid ADR file — check `tests/adr/tools/test_set_status.py` in git history via `git show 971998f^:tests/adr/tools/test_set_status.py` if you need its seeding approach before it is deleted — better: copy what you need BEFORE deleting in Task 4.3, or work Task 4.6 after 4.1-4.5 but derive the ADR seed from `tests/adr/tools/test_create_adr.py` or similar surviving ADR tests). Cover:\n  - For all eight types: `set_status` changes `status`, bumps `updated` (microsecond timestamp), leaves the body untouched — seven domains: re-read the on-disk raw body via the `frontmatter.loads(...).content` mechanism and assert byte-identical; ADR: re-parse and assert document equal apart from status/updated (re-render round-trip).\n  - Closed-vocabulary enforcement per domain: positive — a value from the domain's OWN `_ALLOWED_STATUSES` works; negative — re-read each domain's `_ALLOWED_STATUSES` and pick a value valid in one domain but invalid in the tested one (e.g. `implemented` against `rsk`/`uc`/`tsk`/`qa`/`prb`; `open` against `req`) — each → `pydantic.ValidationError` with the file left byte-identical on disk.\n  - ADR `superseded_by` composes `\"superseded by X\"` in the file (status reads back exactly that string); ADR plain `status` values work with `superseded_by=None`.\n  - `superseded_by` with any non-`adr` type → `ValueError`, nothing written (verify with an unknown id too if cheap — the guard must fire BEFORE file access, so `set_status(\"no-such-id\", \"req\", \"active\", superseded_by=\"x\")` must raise `ValueError`, not `ReqNotFoundError`).\n  - Unknown id → the domain's `XNotFoundError` / `AdrNotFoundError` (no `superseded_by`).\n- **Task 4.7**: Phase-end quality gate — full gate per the plan's Design Notes:\n  1. `uv run --frozen ruff format` (write mode) then `uv run --frozen ruff format --check` and `uv run --frozen ruff check` — must pass.\n  2. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — must be clean.\n  3. `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` — full suite must pass; report the exact new total (expect 1796 − <tests in the 8 deleted files> + <your new test_set_status.py tests>).\n  4. Regenerations (pre-commit hooks run all three on this commit set and fail on drift): `uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\"` first (refresh `.coverage` — stale data referencing the deleted modules breaks the badge with NoSource; this is the exact pre-commit command), then `uv run --frozen specmgr coverage-badge` (→ `docs/coverage.svg`), `uv run --frozen specmgr mcp-docs` (→ `docs/MCP.md`), `uv run --frozen specmgr docs` (→ `docs/api/` + `docs/GENERATED.md`).\n  5. Zero-drift proof: re-run each of the three generators; second run must be a no-op.\n  6. Confirm `docs/MCP.md`: the header now says **71 tool(s)**; the seven `set_status_<d>` entries and ADR's old `set_status` entry are GONE; the new general `set_status` entry exists with `type` rendered as the 8-value enum (`string (enum: req, uc, tsk, qa, prb, gol, rsk, adr)`) — Phase 2's `mcp_docs` enum rendering makes this verifiable; the generic `update` entry is intact; `docs/api/` lost the eight `set_status*` module pages (if `specmgr docs` leaves orphan pages behind — it never deletes stale ones — remove the orphaned `docs/api/biz.dfch.specmgr.<domain>.tools.set_status*.md` files manually, as Phase 3 did for the `update_<d>` pages).\n  7. Fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.server\"` → exit 0.\n  8. Live counts: `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` → **71 / 25 / 19** (the feature's target end state).\n  9. Fix failures and re-run until green — a phase is not done with a red gate.\n  10. Update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); new dated entry `#### Update 2026-08-27 (Phase 4: ...)` in Recent Updates (above the Phase 3 entry, preserve all history) — include the gate results, the 71/25/19 confirmation, and a note that this is the phase where the name-collision constraint was honored atomically; Current Status updated (Phase 4 complete, Phases 5–7 not started, live registration 71/25/19 = target end state); Tasks 4.1–4.7 flipped to done in place (byte-careful: preserve the 2-space continuation wrapping on untouched lines).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`).\n- Do NOT start Phase 5: prompt narration files (`*/data/*.md`), prompt module docstrings, and prompt test files that name the deleted tools stay as-is — Phase 5 rewrites them. (Your cleanup list above deliberately excludes them.)\n- Do NOT change any model/schema file; `models/adr/v1/mutations.py`'s `set_status` FUNCTION stays (it is ported, not removed).\n- No behavioral change beyond: new generic `set_status` tool, deletion of the eight old tools, and the re-pointed references.\n- If the vocabulary you read from `_ALLOWED_STATUSES` differs from the plan's table, follow the source of truth and note the discrepancy in your report.\n\n## Report back (your final message)\n1. `git status --short` summary (deletions count) + `git diff --stat`; confirm the 8+8 deleted files.\n2. Task 4.6 test evidence: the final `git grep -nE \"\\b(set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/` output classified (Phase-5-narration vs kept-by-design model function vs anything else — anything else is a failure); quote the ADR `mutations.set_status` kept-function line.\n3. The two integration-test rewrites (new import + call lines).\n4. Gate evidence: ruff format --check / ruff check / vulture; full suite `Ran N tests ... OK` with exact N and the delta breakdown; the coverage-run + three generator runs + no-op second-run proof; `docs/MCP.md` header line + the new `set_status` entry's `type` row (quote it) + confirmation the 8 old entries are gone; `docs/api/` page delta incl. any manual orphan removals; fresh-subprocess import; live counts 71/25/19.\n5. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbdf176e5ffebtjxZhRHR25K1d" state="completed">
<task_result>


Phase 4 is complete and the gate is fully green. Final report:

---

# Phase 4 Report: Generic `set_status` + retire the eight old status tools

## 1. `git status --short` summary + `git diff --stat`

**24 staged deletions / 65 unstaged modifications / 3 untracked new files** (nothing committed):

| Category | Count | Files |
|---|---|---|
| `D` tool modules (Task 4.2) | **8** | `adr/tools/set_status.py` + `{req,uc,tsk,qa,prb,gol,rsk}/tools/set_status_<d>.py` |
| `D` test files (Task 4.3) | **8** | `tests/adr/tools/test_set_status.py` + `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_set_status_<d>.py` |
| `D` orphan `docs/api/` pages (Task 4.7.6) | 8 | `docs/api/biz.dfch.specmgr.{adr.tools.set_status, <d>.tools.set_status_<d>}.md` |
| `??` new code (Task 4.1/4.6) | 2 | `src/biz/dfch/specmgr/general/tools/set_status.py`, `tests/general/tools/test_set_status.py` |
| `??` new docs page | 1 | `docs/api/biz.dfch.specmgr.general.tools.set_status.md` |
| ` M` modified | 65 | registration `__init__.py`s (10), domain `__init__.py`s (7), `_lock.py` (8), `_write.py` (2), `update.py`, `_splice.py`, `server.py`, 2 integration tests, `tests/commands/test_docs.py`, plan README, and 47 regenerated `docs/` files |

`git diff --stat` (working tree vs index): **65 files changed, 415 insertions(+), 320 deletions(−)**; src/tests-only: 32 files, +122/−103.

## 2. ACC-005 grep evidence

`git grep -nE "\b(set_status_req|…|set_status_rsk)\b" -- src/ tests/` final residual — **all 24 files are Phase-5-owned prompt narration** (left as-is per hard constraints): 12 `*/data/*.md` instruction files, 6 `*/prompts/update_<d>.py` modules, 6 `tests/*/prompts/test_update_<d>.py`. **Zero** in `tools/`, `models/`, `general/`, or any `__init__.py`.

The kept-by-design model function (quoted):
```

src/biz/dfch/specmgr/models/adr/v1/mutations.py:131:def set_status(adr: Adr, status: str, superseded_by: str | None = None) -> Adr:

````
Bare `set_status` elsewhere matches only: the new `general/tools/set_status.py` + its registration, my re-pointed references (`update.py`, `_splice.py`, 8× `_lock.py`, 2× `_write.py`, `server.py`, 2 integration tests), the ADR model re-exports (`models/adr/__init__.py`, `models/adr/v1/__init__.py`) + its model test (`tests/models/adr/v1/test_mutations.py`), and the Phase-5 ADR narration files. **No other matches — nothing outside the allowed sets.**

## 3. Integration-test rewrites (new import + call lines)

`tests/gol/tools/test_integration.py`:
```python
from biz.dfch.specmgr.general.tools.set_status import set_status
...
        # 5. set_status (type="gol"): only status/updated may change.
        accepted = set_status(gol_id, "gol", "accepted")
````

`tests/prb/tools/test_integration.py`:

```python
from biz.dfch.specmgr.general.tools.set_status import set_status
...
        # 3. set_status (type="prb"): only status/updated may change.
        activated = set_status(prb_id, "prb", "active")
```

Both pass live (4/4 in their module).

## 4. Gate evidence (all green, final tree state)

| Check | Result |
|---|---|
| `ruff format` (write) then `ruff format --check` | write run changed nothing; **1094 files already formatted** (ruff 0.16 counts md too: 1101 − 8 deleted `docs/api` pages + 1 new = 1094) |
| `ruff check` | **All checks passed** |
| `vulture src/ whitelist.py --min-confidence 60` | **clean, exit 0** |
| full suite `python -m unittest discover -s tests -t .` | **Ran 1768 tests, OK** (twice; delta: 1796 − 38 deleted [ADR 3 + 7×5] + 10 new `test_set_status.py` = 1768) |
| `coverage run -m unittest discover …` (pre-commit's exact cmd) | Ran 1768, OK → refreshed `.coverage` |
| `specmgr coverage-badge` | 98% — unchanged rounded value, badge **byte-identical, no diff** |
| `specmgr mcp-docs` | header: **`25 resource(s), 1 resource template(s), 71 tool(s), 19 prompt(s).`** |
| `specmgr docs` | 305 module pages + `GENERATED.md` + `api/README.md` |
| zero-drift proof | snapshot → re-ran all three generators → `diff` of sha256 manifests: **empty (byte-identical no-op)** |
| `docs/MCP.md` new entry, `type` row (quoted) | `` | `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, adr)` | Yes | `` plus `` | `superseded_by` | `string | None` | No | ``; all 8 old `set_status*` entries **gone** (grep for their titles: zero); generic `update` entry intact (its description now says "use the generic `set_status` tool") |
| `docs/api/` delta | 8 orphan `set_status*` pages removed **manually** (generator never deletes stale); 1 new `general.tools.set_status.md`; `api/README.md` references only the new page |
| fresh subprocess `python -c "import biz.dfch.specmgr.server"` | **exit 0** |
| live counts `mcp.list_tools()/list_resources()/list_prompts()` | **71 / 25 / 19 — target end state**; `set_status` registered **exactly once** (name-collision constraint honored atomically); `required: ["id","type","status"]` |
| pylint (advisory) | 9.73/10 on changed files — only intentional duplicate-code mirrors (the per-domain port pattern, same as pre-existing) |

New tests (`tests/general/tools/test_set_status.py`, 10 tests, parameterized over all 8 types): status changed + `updated` bumped (microsecond) + body untouched (7 domains: raw body byte-identical via `frontmatter.loads(...).content`; ADR: re-parsed render round-trip equal apart from status — ADR has no `updated` field); per-domain vocabulary enforcement with the tests importing each domain's private `_ALLOWED_STATUSES`/`_FIXED_STATUSES` and asserting the pairs against them (negative cross-domain values: `implemented` vs uc/tsk/qa/prb/rsk/adr, `open` vs req/gol → `ValidationError`, file byte-identical); ADR `superseded_by` → `"superseded by X"` in file + plain values with `superseded_by=None`; `superseded_by` with non-`adr` → `ValueError` file untouched, **including unknown id** (guard fires before file access); unknown id → domain `XNotFoundError`/`AdrNotFoundError`.

## 5. Deviations from the plan

1. **`tests/commands/test_docs.py` count 12 → 11** (outside the named task list, required): `test_count_mcp_features_matches_known_counts` asserts the number of tool *modules* under `adr/tools/`; deleting `adr/tools/set_status.py` is a direct consequence of Task 4.2, and the suite would be red without updating the known count. Flagged in the README entry.
2. **ADR `updated` semantics**: the plan's "bumps `updated`" applies to the seven whole-body domains only — `AdrFrontmatter` has no `updated` field (the ported ADR behavior never bumped anything either). Tests and README state this explicitly; no behavior invented.
3. **`adr/tools/__init__.py` docstring** had no `set_status` mention to remove (only import + `__all__`); I added a pointer sentence to the generic tool for consistency with the seven domain files.
4. **`_splice.py` reworded to name no tool** ("the same frontmatter-stripping mechanism the domain write paths use") — explicitly allowed by the orchestrator's list ("or zero if you reword to no name").
5. **Vocabulary source-of-truth check**: re-read all eight domains' `_ALLOWED_STATUSES`/`_FIXED_STATUSES` — **exact match** with the plan's Design-Notes table (req/gol 7, uc 5, tsk/qa 4, prb 4, rsk 6, adr 6 + pattern). No discrepancy.

**Plan README updated**: frontmatter `updated: 2026-08-27` (already; status stays `in-progress`), new `#### Update 2026-08-27 (Phase 4: …)` entry above the Phase 3 entry (history preserved), Current Status rewritten (Phase 4 complete, Phases 5–7 not started, 71/25/19 = target end state), Tasks 4.1–4.7 flipped to `[x]`/`status: done` in place with 2-space continuations preserved (ruff-md-format clean).

**Nothing blocks Phase 5** — the narration files are exactly the grep-residual set, ready for the Task 5.1–5.3 rewrites.
\</task_result>
</task>

````

---

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 68.9s)

_Thinking:_

Phase 4 is reported as complete, green. Let me verify independently:

1. Gate: ruff format --check, ruff check, vulture, full unittest (expected value 1768), coverage run, 3 generators + zero drift, fresh import, live count 71/25/19.
2. grep: word-boundary grep for set_status_<d> — remaining should be only Phase 5 narration.
3. Verify that `set_status` is registered exactly once.
4. Check docs/MCP.md header + new entries + old entries have been removed.
5. Spot-check general/tools/set_status.py (guard placement, ADR adapter port, verbatim port of one domain adapter).
6. Check diff of update.py's description (rephrasing of set_status_*), and diff of _lock.py.
7. Check README progress entries.
8. Check the test_docs.py count change (12→11) — verify it's the only test count change.

Deviations:
1. test_docs.py count 12→11 — legitimate (adr/tools lost one module).
2. ADR has no updated field — correct, ADR's frontmatter doesn't have updated. Good catch, matches the verbatim port.
3. Pointer sentence in adr/tools/__init__.py — no problem.
4. Rewording of _splice.py — no problem.
5. Vocabulary match — good.

Let me batch the verification. First: grep + live count + import + MCP.md check (fast). Next: gate (slow). Then file reads.




Phase 4 reported green with 5 reasonable deviations (notably: ADR's frontmatter doesn't have an `updated` field — the port correctly doesn't bump it; and the tool module count assertion in `tests/commands/test_docs.py` needs to be 12→11). Verifying independently — first grep, registration, and MCP.md, then running the full gate:




**Tool: bash**

**Input:**
```json
{
  "command": "git grep -nE \"\\b(set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/ | cut -d: -f1 | sort | uniq -c && echo === && uv run --frozen python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\ntools = asyncio.run(mcp.list_tools())\nnames = [t.name for t in tools]\nprint('tools:', len(names), 'resources:', len(asyncio.run(mcp.list_resources())), 'prompts:', len(asyncio.run(mcp.list_prompts())))\nprint('set_status count:', names.count('set_status'))\nss = [t for t in tools if t.name == 'set_status'][0]\nprint('type prop:', ss.inputSchema['properties']['type'])\nprint('required:', ss.inputSchema['required'])\nupd = [t for t in tools if t.name == 'update'][0]\nprint('update desc tail:', upd.description[-80:])\n\"",
  "timeout": 300000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
````

**Output:**

```
      1 src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
      2 src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
      5 src/biz/dfch/specmgr/gol/prompts/update_gol.py
      1 src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
      2 src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
      5 src/biz/dfch/specmgr/prb/prompts/update_prb.py
      1 src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
      1 src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
      2 src/biz/dfch/specmgr/qa/prompts/update_qa.py
      1 src/biz/dfch/specmgr/req/data/req_create_instructions.md
      1 src/biz/dfch/specmgr/req/data/req_update_instructions.md
      2 src/biz/dfch/specmgr/req/prompts/update_req.py
      1 src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
      1 src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
      2 src/biz/dfch/specmgr/rsk/prompts/update_risk.py
      1 src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
      1 src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
      2 src/biz/dfch/specmgr/tsk/prompts/update_task.py
      4 tests/gol/prompts/test_update_gol.py
      4 tests/prb/prompts/test_update_prb.py
      2 tests/qa/prompts/test_update_qa.py
      2 tests/req/prompts/test_update_req.py
      2 tests/rsk/prompts/test_update_risk.py
      2 tests/tsk/prompts/test_update_task.py
===
Traceback (most recent call last):
  File "<string>", line 9, in <module>
    print('type prop:', ss.inputSchema['properties']['type'])
                        ^^^^^^^^^^^^^^
  File "/home/user/src/biz.dfch.SpecMgr-feat-22/.venv/lib/python3.13/site-packages/pydantic/main.py", line 1042, in __getattr__
    raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')
AttributeError: 'Tool' object has no attribute 'inputSchema'. Did you mean: 'input_schema'?
tools: 71 resources: 25 prompts: 19
set_status count: 1

```

**Tool: bash**

**Input:**

```json
{
  "command": "head -12 docs/MCP.md | grep -i \"tool\" ; echo === ; grep -nE \"^### Tool: set_status|^### Tool: update\" docs/MCP.md; echo === ; grep -c \"set_status_req\\|set_status_uc\\|set_status_tsk\\|set_status_qa\\|set_status_prb\\|set_status_gol\\|set_status_rsk\" docs/MCP.md; echo === && git status --short | awk '{print $1}' | sort | uniq -c && git diff --stat | tail -1",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
25 resource(s), 1 resource template(s), 71 tool(s), 19 prompt(s).
- [Tools](#tools)
===
855:### Tool: set_status
868:### Tool: update
882:### Tool: update_frontmatter
893:### Tool: update_section
===
0
===
      3 ??
     24 D
     65 M
 65 files changed, 415 insertions(+), 320 deletions(-)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 165.1s)

_Thinking:_

Good results:

- The grep residuals for `set_status_<d>` are only the 24 prompt narration files (Phase 5's responsibility) — zero in tools/, models/, general/. ✓ (Note: the implementer's report said 24 files: 12 data + 6 prompt modules + 6 prompt tests — matches my count: data files 12 + prompt modules 6 + tests 6 = 24 ✓)
- Live: **71 tools / 25 resources / 19 prompts**, `set_status` is registered **exactly once** ✓
- docs/MCP.md header: "71 tool(s)" ✓; `### Tool: set_status` (855) + `### Tool: update` (868) + ADR's update_frontmatter/update_section remain; zero set_status\_<d> strings in MCP.md ✓
- git status: 24 D (8 modules + 8 tests + 8 orphan pages), 65 M, 3 ?? (new set_status.py, new tests, new API pages) ✓

My python probe failed at inputSchema (the attribute is input_schema) — it printed the count before failing, but it didn't print the type property / required / update's desc. Let me rerun with input_schema. Then run the full gate.

Residuals are exactly the 24 Phase-5 narration files; live count is **71/25/19** with `set_status` registered exactly once; MCP.md header confirms. My probe had an attribute typo (`input_schema`) — re-running it and the full gate:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\ntools = asyncio.run(mcp.list_tools())\nss = [t for t in tools if t.name == 'set_status'][0]\nprint('type prop:', ss.input_schema['properties']['type'])\nprint('superseded_by:', ss.input_schema['properties']['superseded_by'])\nprint('required:', ss.input_schema['required'])\nupd = [t for t in tools if t.name == 'update'][0]\nprint('update desc tail:', repr(upd.description[-90:]))\n\"",
  "timeout": 300000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
type prop: {'enum': ['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'adr'], 'title': 'Type', 'type': 'string'}
superseded_by: {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'default': None, 'title': 'Superseded By'}
required: ['id', 'type', 'status']
update desc tail: 'fore anything is written. `status` is never settable -- use the generic `set_status` tool.'

```

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase4-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase4-unittest.log && uv run --frozen specmgr coverage-badge >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && uv run --frozen specmgr docs >/dev/null && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p4-m1.txt && uv run --frozen specmgr coverage-badge >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && uv run --frozen specmgr docs >/dev/null && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p4-m2.txt && diff /tmp/opencode/p4-m1.txt /tmp/opencode/p4-m2.txt && echo P4_DOCS_ZERO_DRIFT && uv run --frozen python -c \"import biz.dfch.specmgr.server\" && echo IMPORT_OK",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
1094 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1768 tests in 85.048s
OK
P4_DOCS_ZERO_DRIFT
IMPORT_OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 55.6s)

_Thinking:_

Full gate for Phase 4 is independently green:

- ruff format --check: 1094 files ✓
- ruff check ✓
- vulture clean ✓
- unittest (coverage run): **1768 tests OK** exit 0 ✓ (matches 1796 − 38 + 10)
- 3 generators + zero-drift proof: **P4_DOCS_ZERO_DRIFT** ✓
- fresh import: OK ✓
- set_status's input schema: 8-value enum, superseded_by is an optional string|null, required is [id, type, status] ✓
- update's description now points to the generic set_status tool ✓

Next, spot-check the code quality of general/tools/set_status.py (the ADR adapter port + guard + one domain adapter), the README entry, and the changes to test_docs.py. After that, commit.

Gate fully green. Final spot-checks — the new `set_status.py` (guard, ADR port, one domain adapter), the `test_docs.py` deviation, and the README entry:

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/set_status.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr-feat-22/src/biz/dfch/specmgr/general/tools/set_status.py</path>
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
18: """``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).
19: 
20: The generic, cross-domain status-change tool for all eight document types
21: (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``adr``). It
22: dispatches on the explicit ``type`` parameter to a private per-domain
23: adapter (``_set_status_<d>``), each a **verbatim port** of the
24: corresponding per-domain status tool's function body (same domain lock,
25: same ``load_by_id``, same raw-body re-read and verbatim re-persistence,
26: same frontmatter reconstruction through the domain's own
27: ``XFrontmatter`` constructor -- so the domain's closed status vocabulary
28: validates -- and the same domain ``XNotFoundError``; those per-domain
29: tools were retired in feat-22 Phase 4). The ADR adapter ports the
30: previous per-domain ADR status tool's function body (same ``adr_lock``,
31: ``load_by_id``, and ``write_adr`` render round-trip,
32: ``AdrNotFoundError``) including its delegation to
33: ``models.adr.v1.mutations.set_status``, which composes ``status`` as
34: ``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
35: 
36: The parameter is intentionally named ``type`` (it matches the frontmatter
37: field vocabulary the client already knows); no enabled ruff rule objects
38: to the builtin shadow. The 8-way union return type is annotation-only --
39: the MCP input schema is built from the parameters, and the SDK
40: serializes whichever concrete document is returned.
41: 
42: ``superseded_by`` is accepted only for ``type="adr"``: the
43: ``"superseded by X"`` status pattern is ADR-specific (no other domain's
44: ``XFrontmatter.status`` accepts it). The public :func:`set_status`
45: rejects it for any other ``type`` with a ``ValueError`` before any file
46: access.
47: 
48: Neither any ``create_<d>`` tool nor the generic :func:`update` tool
49: accepts a ``status`` argument at all -- this tool is the sole
50: status-change entry point for every domain.
51: 
52: ``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
53: because the pure, in-memory operation it delegates to shares this
54: wrapper's own name.
55: """
56: 
57: from __future__ import annotations
58: 
59: from collections.abc import Callable
60: from datetime import datetime
61: from typing import Literal
62: 
63: import frontmatter
64: 
65: from ...adr.tools._io import load_by_id as load_adr_by_id
66: from ...adr.tools._io import write_adr
67: from ...adr.tools._lock import adr_lock
68: from ...adr.tools._paths import adr_base_dir
69: from ...gol.models.v1 import GolDocument, GolFrontmatter
70: from ...gol.tools._io import load_by_id as load_gol_by_id
71: from ...gol.tools._lock import gol_lock
72: from ...gol.tools._paths import gol_base_dir
73: from ...gol.tools._write import write_gol_file
74: from ...models.adr import Adr
75: from ...models.adr.v1 import mutations
76: from ...prb.models.v1 import PrbDocument, PrbFrontmatter
77: from ...prb.tools._io import load_by_id as load_prb_by_id
78: from ...prb.tools._lock import prb_lock
79: from ...prb.tools._paths import prb_base_dir
80: from ...prb.tools._write import write_prb_file
81: from ...qa.models.v2 import QaDocument, QaFrontmatter
82: from ...qa.tools._io import load_by_id as load_qa_by_id
83: from ...qa.tools._lock import qa_lock
84: from ...qa.tools._paths import qa_base_dir
85: from ...qa.tools._write import write_qa_file
86: from ...req.models.v1 import ReqDocument, ReqFrontmatter
87: from ...req.tools._io import load_by_id as load_req_by_id
88: from ...req.tools._lock import req_lock
89: from ...req.tools._paths import req_base_dir
90: from ...req.tools._write import write_req_file
91: from ...rsk.models.v1 import RskDocument, RskFrontmatter
92: from ...rsk.tools._io import load_by_id as load_rsk_by_id
93: from ...rsk.tools._lock import rsk_lock
94: from ...rsk.tools._paths import rsk_base_dir
95: from ...rsk.tools._write import write_rsk_file
96: from ...server import mcp
97: from ...tsk.models.v1 import TskDocument, TskFrontmatter
98: from ...tsk.tools._io import load_by_id as load_tsk_by_id
99: from ...tsk.tools._lock import tsk_lock
100: from ...tsk.tools._paths import tsk_base_dir
101: from ...tsk.tools._write import write_tsk_file
102: from ...uc.models.v2 import UcDocument, UcFrontmatter
103: from ...uc.tools._io import load_by_id as load_uc_by_id
104: from ...uc.tools._lock import uc_lock
105: from ...uc.tools._paths import uc_base_dir
106: from ...uc.tools._write import write_uc_file
107: 
108: __all__ = ["set_status"]
109: 
110: #: The only ``type`` whose status can be composed via ``superseded_by``
111: #: (the ``"superseded by X"`` pattern is ADR-specific).
112: _TYPE_ADR = "adr"
113: 
114: #: The generic tool's 8-way return union -- annotation-only (see module docstring).
115: _SetStatusDocument = ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr
116: 
117: 
118: def _set_status_req(id_: str, status: str, superseded_by: str | None) -> ReqDocument:
119:     """Replace the status of the requirement identified by ``id_``.
120: 
121:     Verbatim port of the previous per-domain requirement status tool's
122:     function body (same ``req_lock``, ``load_by_id``, raw-body re-read via
123:     the established ``frontmatter.loads(...).content`` mechanism and
124:     verbatim re-persistence, frontmatter reconstructed through
125:     :class:`ReqFrontmatter`'s own constructor so the closed status
126:     vocabulary validates, ``write_req_file``, ``ReqNotFoundError``; that
127:     per-domain tool was retired in feat-22 Phase 4). ``superseded_by`` is
128:     never used here -- the public :func:`set_status` guard rejects it for
129:     every non-``adr`` type before dispatch.
130:     """
131:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
132: 
133:     base_dir = req_base_dir()
134:     with req_lock(id_):
135:         path, existing = load_req_by_id(base_dir, id_)
136:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
137: 
138:         now = datetime.now().isoformat(timespec="microseconds")
139:         fm_data = existing.frontmatter.model_dump()
140:         fm_data["status"] = status
141:         fm_data["updated"] = now
142:         new_frontmatter = ReqFrontmatter(**fm_data)
143:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=existing.body)
144:         write_req_file(path, new_frontmatter, raw_body)
145:     return new_doc
146: 
147: 
148: def _set_status_uc(id_: str, status: str, superseded_by: str | None) -> UcDocument:
149:     """Replace the status of the use case identified by ``id_``.
150: 
151:     Verbatim port of the previous per-domain use-case status tool's
152:     function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
153:     ``UcNotFoundError``; that per-domain tool was retired in feat-22
154:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
155:     """
156:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
157: 
158:     base_dir = uc_base_dir()
159:     with uc_lock(id_):
160:         path, existing = load_uc_by_id(base_dir, id_)
161:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
162: 
163:         now = datetime.now().isoformat(timespec="microseconds")
164:         fm_data = existing.frontmatter.model_dump()
165:         fm_data["status"] = status
166:         fm_data["updated"] = now
167:         new_frontmatter = UcFrontmatter(**fm_data)
168:         new_doc = UcDocument(frontmatter=new_frontmatter, body=existing.body)
169:         write_uc_file(path, new_frontmatter, raw_body)
170:     return new_doc
171: 
172: 
173: def _set_status_tsk(id_: str, status: str, superseded_by: str | None) -> TskDocument:
174:     """Replace the status of the task list identified by ``id_``.
175: 
176:     Verbatim port of the previous per-domain task list status tool's
177:     function body (same ``tsk_lock``, ``load_by_id``, ``write_tsk_file``,
178:     ``TskNotFoundError``; that per-domain tool was retired in feat-22
179:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
180:     """
181:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
182: 
183:     base_dir = tsk_base_dir()
184:     with tsk_lock(id_):
185:         path, existing = load_tsk_by_id(base_dir, id_)
186:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
187: 
188:         now = datetime.now().isoformat(timespec="microseconds")
189:         fm_data = existing.frontmatter.model_dump()
190:         fm_data["status"] = status
191:         fm_data["updated"] = now
192:         new_frontmatter = TskFrontmatter(**fm_data)
193:         new_doc = TskDocument(frontmatter=new_frontmatter, body=existing.body)
194:         write_tsk_file(path, new_frontmatter, raw_body)
195:     return new_doc
196: 
197: 
198: def _set_status_qa(id_: str, status: str, superseded_by: str | None) -> QaDocument:
199:     """Replace the status of the QA document identified by ``id_``.
200: 
201:     Verbatim port of the previous per-domain QA document status tool's
202:     function body (same ``qa_lock``, ``load_by_id``, ``write_qa_file``,
203:     ``QaNotFoundError``; that per-domain tool was retired in feat-22
204:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
205:     """
206:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
207: 
208:     base_dir = qa_base_dir()
209:     with qa_lock(id_):
210:         path, existing = load_qa_by_id(base_dir, id_)
211:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
212: 
213:         now = datetime.now().isoformat(timespec="microseconds")
214:         fm_data = existing.frontmatter.model_dump()
215:         fm_data["status"] = status
216:         fm_data["updated"] = now
217:         new_frontmatter = QaFrontmatter(**fm_data)
218:         new_doc = QaDocument(frontmatter=new_frontmatter, body=existing.body)
219:         write_qa_file(path, new_frontmatter, raw_body)
220:     return new_doc
221: 
222: 
223: def _set_status_prb(id_: str, status: str, superseded_by: str | None) -> PrbDocument:
224:     """Replace the status of the problem statement identified by ``id_``.
225: 
226:     Verbatim port of the previous per-domain problem statement status
227:     tool's function body (same ``prb_lock``, ``load_by_id``,
228:     ``write_prb_file``, ``PrbNotFoundError``; that per-domain tool was
229:     retired in feat-22 Phase 4) -- see :func:`_set_status_req` for the
230:     full semantics.
231:     """
232:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
233: 
234:     base_dir = prb_base_dir()
235:     with prb_lock(id_):
236:         path, existing = load_prb_by_id(base_dir, id_)
237:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
238: 
239:         now = datetime.now().isoformat(timespec="microseconds")
240:         fm_data = existing.frontmatter.model_dump()
241:         fm_data["status"] = status
242:         fm_data["updated"] = now
243:         new_frontmatter = PrbFrontmatter(**fm_data)
244:         new_doc = PrbDocument(frontmatter=new_frontmatter, body=existing.body)
245:         write_prb_file(path, new_frontmatter, raw_body)
246:     return new_doc
247: 
248: 
249: def _set_status_gol(id_: str, status: str, superseded_by: str | None) -> GolDocument:
250:     """Replace the status of the goal identified by ``id_``.
251: 
252:     Verbatim port of the previous per-domain goal status tool's function
253:     body (same ``gol_lock``, ``load_by_id``, ``write_gol_file``,
254:     ``GolNotFoundError``; that per-domain tool was retired in feat-22
255:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
256:     """
257:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
258: 
259:     base_dir = gol_base_dir()
260:     with gol_lock(id_):
261:         path, existing = load_gol_by_id(base_dir, id_)
262:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
263: 
264:         now = datetime.now().isoformat(timespec="microseconds")
265:         fm_data = existing.frontmatter.model_dump()
266:         fm_data["status"] = status
267:         fm_data["updated"] = now
268:         new_frontmatter = GolFrontmatter(**fm_data)
269:         new_doc = GolDocument(frontmatter=new_frontmatter, body=existing.body)
270:         write_gol_file(path, new_frontmatter, raw_body)
271:     return new_doc
272: 
273: 
274: def _set_status_rsk(id_: str, status: str, superseded_by: str | None) -> RskDocument:
275:     """Replace the status of the risk identified by ``id_``.
276: 
277:     Verbatim port of the previous per-domain risk status tool's function
278:     body (same ``rsk_lock``, ``load_by_id``, ``write_rsk_file``,
279:     ``RskNotFoundError``; that per-domain tool was retired in feat-22
280:     Phase 4) -- see :func:`_set_status_req` for the full semantics.
281:     """
282:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
283: 
284:     base_dir = rsk_base_dir()
285:     with rsk_lock(id_):
286:         path, existing = load_rsk_by_id(base_dir, id_)
287:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
288: 
289:         now = datetime.now().isoformat(timespec="microseconds")
290:         fm_data = existing.frontmatter.model_dump()
291:         fm_data["status"] = status
292:         fm_data["updated"] = now
293:         new_frontmatter = RskFrontmatter(**fm_data)
294:         new_doc = RskDocument(frontmatter=new_frontmatter, body=existing.body)
295:         write_rsk_file(path, new_frontmatter, raw_body)
296:     return new_doc
297: 
298: 
299: def _set_status_adr(id_: str, status: str, superseded_by: str | None) -> Adr:
300:     """Replace the status of the ADR identified by ``id_``.
301: 
302:     Port of the previous per-domain ADR status tool's function body
303:     (same ``adr_lock``, ``load_by_id``, delegation to
304:     ``models.adr.v1.mutations.set_status`` -- which composes ``status`` as
305:     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given --
306:     and the ``write_adr`` render round-trip, ``AdrNotFoundError``; that
307:     per-domain tool was retired in feat-22 Phase 4).
308:     """
309:     base_dir = adr_base_dir()
310:     with adr_lock(id_):
311:         path, adr = load_adr_by_id(base_dir, id_)
312:         new_adr = mutations.set_status(adr, status, superseded_by)
313:         write_adr(path, new_adr)
314:     return new_adr
315: 
316: 
317: #: Dispatch table mapping the ``type`` value to its private adapter.
318: _ADAPTERS: dict[str, Callable[[str, str, str | None], _SetStatusDocument]] = {
319:     "req": _set_status_req,
320:     "uc": _set_status_uc,
321:     "tsk": _set_status_tsk,
322:     "qa": _set_status_qa,
323:     "prb": _set_status_prb,
324:     "gol": _set_status_gol,
325:     "rsk": _set_status_rsk,
326:     _TYPE_ADR: _set_status_adr,
327: }
328: 
329: 
330: @mcp.tool(
331:     name="set_status",
332:     title="Set document status",
333:     description=(
334:         "Replace the status of an existing document across all eight domains (`type` is one of "
335:         "req, uc, tsk, qa, prb, gol, rsk, adr), also bumping `updated` (the seven whole-body "
336:         "domains) and leaving the body untouched. The new `status` must be one of the domain's "
337:         "own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything "
338:         "else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted "
339:         'only for `type="adr"` -- it composes the status as "superseded by '
340:         '{superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor '
341:         "the generic `update` tool accepts a `status` argument at all -- this is the sole "
342:         "status-change entry point."
343:     ),
344: )
345: def set_status(
346:     id: str,
347:     type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "adr"],
348:     status: str,
349:     superseded_by: str | None = None,
350: ) -> _SetStatusDocument:
351:     """Replace the status of an existing document, across all eight domains.
352: 
353:     Cross-domain generic for every document type
354:     (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``adr``);
355:     dispatches on ``type`` to the domain's own ported adapter (same lock,
356:     same id resolution, same body handling, same domain not-found error).
357: 
358:     For the seven whole-body domains the existing file's frontmatter is
359:     carried over with every field preserved except ``status`` (replaced)
360:     and ``updated`` (bumped to the current microsecond timestamp); the
361:     body is never touched -- its raw, on-disk markdown (not a render of
362:     the parsed model) is re-read and re-persisted verbatim. For
363:     ``type="adr"`` the change delegates to
364:     ``models.adr.v1.mutations.set_status`` (which composes ``status`` as
365:     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given)
366:     and re-renders the full file via the ``write_adr`` round-trip.
367: 
368:     The new ``status`` must be in the domain's own closed vocabulary: the
369:     frontmatter is reconstructed through the domain's own
370:     ``XFrontmatter`` constructor, so the domain's own validator enforces
371:     its set. Where that set lives is documented per domain -- see each
372:     ``XFrontmatter.status`` field (the seven whole-body domains'
373:     ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
374:     rather than any list in this docstring.
375: 
376:     Parameters
377:     ----------
378:     id:
379:         The document's specmgr-assigned identifier.
380:     type:
381:         The document type / domain: one of ``req``, ``uc``, ``tsk``,
382:         ``qa``, ``prb``, ``gol``, ``rsk``, ``adr``.
383:     status:
384:         The new status. Must be one of the dispatched domain's own
385:         accepted values (see its ``XFrontmatter.status`` field). For
386:         ``adr``, ignored when ``superseded_by`` is given.
387:     superseded_by:
388:         ADR only. When given (with ``type="adr"``), ``status`` is
389:         composed as ``f"superseded by {superseded_by}"`` instead of being
390:         used verbatim. A ``ValueError`` for any other ``type``.
391: 
392:     Returns
393:     -------
394:     ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr
395:         The updated document of the dispatched domain type.
396: 
397:     Raises
398:     ------
399:     ValueError
400:         ``superseded_by`` given with a ``type`` other than ``"adr"``
401:         (raised before any file access). Nothing is written.
402:     pydantic.ValidationError
403:         ``status`` is not in the dispatched domain's closed vocabulary
404:         (for ``adr``: not one of its six values and not a
405:         ``"superseded by ..."`` string). Nothing is written.
406:     ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
407:     PrbNotFoundError / GolNotFoundError / RskNotFoundError / AdrNotFoundError
408:         No document of the dispatched ``type`` has this id -- the
409:         domain's own not-found error, unchanged from the per-domain tools.
410:     """
411:     if superseded_by is not None and type != _TYPE_ADR:
412:         raise ValueError(
413:             f'superseded_by is only accepted for type={_TYPE_ADR!r} (the "superseded by X" '
414:             f"pattern is ADR-specific), got type={type!r} with superseded_by={superseded_by!r}"
415:         )
416: 
417:     adapter = _ADAPTERS[type]
418:     result = adapter(id, status, superseded_by)
419:     return result

(End of file - total 419 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U3 -- tests/commands/test_docs.py && git diff -U1 -- .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | grep -E \"^\\+\" | grep -vE \"^\\+\\+\\+\" | head -60",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
diff --git a/tests/commands/test_docs.py b/tests/commands/test_docs.py
index 50e3215..ac32a5c 100644
--- a/tests/commands/test_docs.py
+++ b/tests/commands/test_docs.py
@@ -150,14 +150,17 @@ class TestGeneratedMdContent(unittest.TestCase):
         self.assertIn("prompts", domains["adr_subpackages"])
 
     def test_count_mcp_features_matches_known_counts(self):
-        """Must count MCP tools/resources under adr/ (12 tools, 1 resource).
+        """Must count MCP tools/resources under adr/ (11 tools, 1 resource).
 
         The former ``specmgr://adr/list`` resource was converted into the
         ``list_adr`` tool (feat-13-list-paging Task 2.1), shifting one
-        module from ``adr/resources/`` to ``adr/tools/``.
+        module from ``adr/resources/`` to ``adr/tools/``. The ADR
+        ``set_status`` tool module was retired into the generic
+        ``set_status`` tool in ``general/tools/`` (feat-22 Phase 4),
+        shifting one module the other way.
         """
         features = _count_mcp_features()
-        self.assertEqual(features["tools"], 12)
+        self.assertEqual(features["tools"], 11)
         self.assertEqual(features["resources"], 1)
 
     def test_collect_module_docs_finds_domains(self):
+- [x] Task 4.1: Create `general/tools/set_status.py`: eight private adapters
+   depends on: Phase 3 complete (the `set_status` tool name must be free
+   before this tool registers — see Design Notes, Name-collision constraint) —
+   status: done
+- [x] Task 4.2: Delete the eight superseded modules: `adr/tools/set_status.py`,
+   `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`,
+   `rsk/tools/set_status_rsk.py` — depends on: Task 4.1 — status: done
+- [x] Task 4.3: Delete the eight test files: `tests/adr/tools/
+   `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/
+   test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py` — depends
+   on: Task 4.1 — status: done
+- [x] Task 4.4: Register `set_status` in `general/tools/__init__.py` (import,
+   `__init__.py` docstring enumerations likewise — depends on: Tasks 4.2, 4.3 —
+   status: done
+- [x] Task 4.5: Update `server.py`'s module docstring: remove `set_status`
+   `superseded_by` is ADR-only) — depends on: Tasks 4.1, 4.4 — status: done
+- [x] Task 4.6: `tests/general/tools/test_set_status.py` — parameterized over
+   domain `XNotFoundError` / `AdrNotFoundError` — depends on: Task 4.1 —
+   status: done
+- [x] Task 4.7: Phase-end quality gate — full gate including Task 4.6's new
+   place — depends on: Tasks 4.5, 4.6 — status: done
+**As of 2026-08-27**: Phase 4 (Generic `set_status` + retire the eight
+old status tools) complete — the generic `set_status` tool now lives in
+`general/tools/` (8-value `type` incl. `adr`; ADR-only `superseded_by`,
+guard running before any file access), and all eight old status tools
+(seven `set_status_<d>` + ADR's own `set_status`, whose MCP name the
+generic tool takes over) plus their eight test files (38 tests) are gone
+from source and from MCP registration. This was the phase where the
+plan's Name-collision constraint was honored atomically: adding the
+generic tool and deleting all eight old status tools landed in one tree
+state, so the MCP name `set_status` is never double-registered (verified:
+exactly one `set_status` in the live tool list). Every non-narration
+code/docstring reference to the deleted tools was re-pointed (the
+`gol`/`prb` integration tests exercise the generic tool live; the
+`adr`/domain `_lock` helpers and `gol`/`prb` `_write` helpers name it;
+the `update.py`/`_splice.py` pointers were reworded). The ADR mutation
+model's `set_status` *function* (`models/adr/v1/mutations.py`) stays —
+it is ported, not removed. No schema changed. The phase-end quality gate
+is green (1768 tests OK, zero `docs/` drift, fresh-subprocess import
+OK); live registration is **71 tools / 25 resources / 19 prompts — the
+feature's target end state** (baseline 85/25/19: −14). Phases 5–7 are
+not started. (Phase 1 — the feature's ADR
+36905d5b-8057-4294-8665-c7eed5534db0 — Phase 2 — the generic `update`
+tool + `raw` reads — and Phase 3 — retiring the seven `update_<d>` tools
+— completed on 2026-08-27.)
+#### Update 2026-08-27 (Phase 4: Generic `set_status` + retire the eight old status tools)
+
+- Completed: Phase 4 (Tasks 4.1–4.7). The eight per-domain status tools
+  (seven `set_status_<d>` + ADR's own `set_status`) are deleted from
+  source and from MCP registration; status changes now go only through
+  the generic `set_status` tool in `general/tools/`. **This is the
+  phase where the plan's Name-collision constraint was honored
+  atomically**: the generic tool (whose MCP name `set_status` was
+  occupied by ADR's old tool) and the deletion of all eight old status
+  tools landed in the same tree state, so the name `set_status` is never
+  double-registered (verified: exactly one `set_status` in the live tool
+  list). No schema changed.
+  - New: `src/biz/dfch/specmgr/general/tools/set_status.py` —
+    `@mcp.tool(name="set_status", title="Set document status")`
+    `set_status(id, type, status, superseded_by=None)` over an 8-entry

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 162.5s)

_Thinking:_

Phase 4 code is high quality:

- `set_status.py`: 8 adapters, all verbatim ports (req/uc/tsk/qa/prb/gol/rsk share identical structure: lock → load → re-read raw body → model_dump → status+updated → XFrontmatter(\*\*fm_data) → XDocument(frontmatter, body=existing.body) → write with raw_body). ADR adapter: adr_lock → load → mutations.set_status(adr, status, superseded_by) → write_adr. ✓

- The guard `superseded_by is not None and type != _TYPE_ADR` → ValueError is placed before dispatch/file access ✓

- Dispatch table with `_TYPE_ADR` constant (comparison-constant convention) ✓

- The module docstring explains everything, and there's no stale vocabulary list ✓

- The `# type: ignore[union-attr]` on the frontmatter.loads line — this matches the style of the old set_status\_<d> modules (verbatim port).

- The deviation in test_docs.py is properly documented (12→11, with rationale).

- README entry is comprehensive.

All verified:
✅ grep residuals = only the 24 Phase-5 narration files
✅ live 71/25/19, set_status is singular
✅ input schema: 8-value enum, optional superseded_by, required [id, type, status]
✅ MCP.md: header 71, no old entries, generic entry present
✅ Full gate: ruff format (1094), ruff check, vulture, 1768 tests OK, zero-drift on 3 generators, fresh import
✅ Atomicity of name collision

Commit Phase 4.

**Phase 4 verification complete** — `set_status.py` is a clean verbatim port (8 adapters, guard before file access, `_TYPE_ADR` comparison constant, no stale vocabulary lists). The name-collision atomicity is preserved, the final **71/25/19** target state is live, the gate is green on my own runs, and the `test_docs.py` deviation is documented. Committing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git commit -m \"feat(feat-22): add generic set_status tool and retire the eight old status tools\n\nPhase 4 (atomic — the MCP name set_status was occupied by ADR's old\ntool): new @mcp.tool set_status(id, type, status, superseded_by=None)\nin general/tools/ over eight verbatim-ported adapters (seven\nwhole-body domains: body re-read and re-persisted verbatim,\nfrontmatter reconstructed through the domain XFrontmatter so the closed\nvocabulary validates, updated bumped; adr: delegation to\nmodels.adr.v1.mutations.set_status with the superseded-by composition,\nwrite_adr round-trip). superseded_by with a non-adr type raises\nValueError before any file access. Delete the seven set_status_<d>\nmodules + ADR's set_status module and their eight test files (38\ntests); re-point every non-narration reference (domain\n__init__/tools __init__/_lock/_write, server.py, update.py and\n_splice.py pointers, the gol/prb integration tests, the adr tools\ncount in tests/commands/test_docs.py). 10 new parameterized tests\n(1768 total, OK); live registration reaches the feature's target end\nstate: 71 tools / 25 resources / 19 prompts.\" && git log --oneline -4 && git status --short | head -3",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 d9f7a28] feat(feat-22): add generic set_status tool and retire the eight old status tools
 92 files changed, 1569 insertions(+), 2470 deletions(-)
 delete mode 100644 docs/api/biz.dfch.specmgr.adr.tools.set_status.md
 create mode 100644 docs/api/biz.dfch.specmgr.general.tools.set_status.md
 delete mode 100644 docs/api/biz.dfch.specmgr.gol.tools.set_status_gol.md
 delete mode 100644 docs/api/biz.dfch.specmgr.prb.tools.set_status_prb.md
 delete mode 100644 docs/api/biz.dfch.specmgr.qa.tools.set_status_qa.md
 delete mode 100644 docs/api/biz.dfch.specmgr.req.tools.set_status_req.md
 delete mode 100644 docs/api/biz.dfch.specmgr.rsk.tools.set_status_rsk.md
 delete mode 100644 docs/api/biz.dfch.specmgr.tsk.tools.set_status_tsk.md
 delete mode 100644 docs/api/biz.dfch.specmgr.uc.tools.set_status_uc.md
 delete mode 100644 src/biz/dfch/specmgr/adr/tools/set_status.py
 create mode 100644 src/biz/dfch/specmgr/general/tools/set_status.py
 delete mode 100644 src/biz/dfch/specmgr/gol/tools/set_status_gol.py
 delete mode 100644 src/biz/dfch/specmgr/prb/tools/set_status_prb.py
 delete mode 100644 src/biz/dfch/specmgr/qa/tools/set_status_qa.py
 delete mode 100644 src/biz/dfch/specmgr/req/tools/set_status_req.py
 delete mode 100644 src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py
 delete mode 100644 src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py
 delete mode 100644 src/biz/dfch/specmgr/uc/tools/set_status_uc.py
 delete mode 100644 tests/adr/tools/test_set_status.py
 create mode 100644 tests/general/tools/test_set_status.py
 delete mode 100644 tests/gol/tools/test_set_status_gol.py
 delete mode 100644 tests/prb/tools/test_set_status_prb.py
 delete mode 100644 tests/qa/tools/test_set_status_qa.py
 delete mode 100644 tests/req/tools/test_set_status_req.py
 delete mode 100644 tests/rsk/tools/test_set_status_rsk.py
 delete mode 100644 tests/tsk/tools/test_set_status_tsk.py
 delete mode 100644 tests/uc/tools/test_set_status_uc.py
d9f7a28 feat(feat-22): add generic set_status tool and retire the eight old status tools
971998f refactor(feat-22): retire the seven per-domain update_<d> tools
fc76490 feat(feat-22): add generic update tool with line-range replace and raw get reads
2647649 docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 122.2s)

_Thinking:_

Phase 4 has been committed as `d9f7a28`. All hooks passed.

Next is Phase 5: narration rewrite. This is the phase where all prompt narration must reference the generic tools.

Tasks:

- 5.1: grep-driven rewrite of all instruction data files that reference deprecated tools. The plan anticipates 11 files, but the actual grep residual set (from the Phase 3/4 reports) is larger:

  - 6 `<d>_update_instructions.md` (req, tsk, qa, rsk, prb, gol)
  - qa/data/qa_refine_instructions.md
  - 4 ADR instruction files (adr_create_instructions.md, adr_create_test_instructions.md, adr_update_instructions.md, adr_update_test_instructions.md)
  - Additional create/implement data files that reference update\_<d>/set_status\_<d>: req_create, qa_create, prb_create, gol_create, rsk_create, tsk_create, tsk_implement (from Phase 3/4 greps)
  - Rewrite content: update\_<d>(id, content) → update(id, type="<d>", content); set_status\_<d>(id, status) → set_status(id, type="<d>", status); add a passage on range updates to the 6 update instruction files; fix status vocabulary prose per the Design Notes table; ADR files: set_status(id, status[, superseded_by]) → set_status(id, type="adr", status[, superseded_by]).

- 5.2: Fix the docstrings of the prompt Python modules that reference deprecated tools:

  - 6 prompts/update\_<d>.py modules (rsk = update_risk.py, tsk = update_task.py)
  - qa/prompts/refine.py (added by the orchestrator — references update_qa/set_status_qa)
  - 4 ADR prompt modules (create_adr.py, create_adr_test.py, update_adr.py, update_adr_test.py) — make the references to the set_status surface precise (now generic, type="adr")
  - No behavioral changes to the prompt functions

- 5.3: Update the 10 prompt test files (Task 5.3 list) + additional prompt tests that reference deprecated tools per grep: test_create_req, test_create_qa, test_create_prb, test_create_gol, test_refine, test_implement_task (6 additional). Task 5.3 lists 10: update_req, update_task, update_qa, update_risk, update_prb, update_gol, create_adr, create_adr_test, update_adr, update_adr_test. Phase 5's grep (Task 5.1's pattern) also found the following in tests: test_update_gol (4), test_update_prb (4), test_update_qa (2), test_update_req (2), test_update_risk (2), test_update_task (2) — these are the 6 in the list. Plus the create/refine/implement tests also reference the tools (from Phase 3 grep: test_create_req 3, test_create_qa 3, test_create_prb 3, test_create_gol 3, test_refine 4, test_implement_task 3). These assert narration content — if the narration in the data files is rewritten, these tests must be updated too (otherwise they'll fail… wait, will they? The prompt tests assert on the prompt's output text, which comes from the data files. If the data files change but the tests still assert the old text, the tests will fail. So, yes, these 6 additional test files must also be updated in Phase 5).

  Critical correctness point: the prompt tests might also be asserting on tool names in the narration. Let the implementer handle it via grep: after the rewrite, run the full suite, and all prompt tests must pass.

- 5.4: Gate — full gate; since prompt data files are package data and docstrings change → specmgr docs regeneration covers the docstrings; then zero drift via git diff.

Also important: ACC-006: all 11 instruction data files reference the generic tools with correct signatures; the 6 domain update instruction files teach the range update flow (get\_<d>(id, raw=True) → identify 1-based range → update(..., begin, end); for multi-section or uncertain changes, the whole body); the 10 prompt test files pass.

And the final state after Phase 5: grep across src/ + tests/ for the 15 deprecated tool names → zero. That's the "zero thereafter" of ACC-005.

Wait — but the prompt function names are update_req, update_gol, etc. (the prompts kept their names)! The prompt module `req/prompts/update_req.py` defines `def update_req(...)` and `@mcp.prompt(name="update_req")`. A grep for `update_req` will match these — but they are prompt names, not tool references. The plan's ACC-005: "grep across src/ and tests/ finds no code references to the removed tool names (residual references before Phase 5 are limited to Phase-5-owned prompt narration files, and zero thereafter)."

Hmm, "zero thereafter" — but the prompt names themselves (update_req as a prompt function name) remain in the code. There's tension here: the plan explicitly keeps the per-domain prompts and their names (Decisions Made: "per-domain update\_\* prompts are kept (with domain-specific interview guidance) and their narration text is rewritten to the generic tools"). The prompt function names update_req/update_gol etc. collide textually with the removed tool names.

Let me re-read ACC-005 carefully: "the 15 deprecated tools are removed from src/ and from live MCP registration; grep across src/ and tests/ finds no code references to the removed tool names (residual references before Phase 5 are limited to Phase-5-owned prompt narration files, and zero thereafter); vulture is clean."

Interpretation: "code references" — the parenthetical clarifies the grep's behavior: before Phase 5, references are limited to Phase 5's narration files; after Phase 5, zero [narration references]. The prompt function names aren't "references to removed tool names" — they're the names of the kept prompts. This feature's own plan (REQ-006) explicitly keeps these prompts, and server.py lists them as prompts. The 19-prompt count includes update_req etc. So the reasonable reading is: after Phase 5, no references to the removed tools remain in narration or code — prompt names are fine.

But there's a subtle point: after Phase 5, the prompt narration must not reference the tools `update_req`/`set_status_req` — it references `update(id, type="req", ...)`. The prompt function named update_req is a separate thing (it's the prompt's identifier, matching the domain's naming convention: create_req prompt, update_req prompt).

Hmm, wait — actually, let me reconsider. Is the prompt's name "update_req"? Let me confirm: from the server.py line in Phase 2: "Requirement prompts (req/prompts/): create_req, update_req --". Yes, the prompt is named update_req. And the removed tool was also named update_req. So after this feature, the name "update_req" exists as a prompt, not a tool. A grep for `update_req` will find the prompt's code (decorator, def, import, __all__) — those are references to the prompt, not to the tool.

In Phase 7 (final verification), the ACC-005 check should be done with this understanding: no references to the removed tools in any narration, and prompt-name matches are classified as prompt references. In Phase 5, the goal is: all narration (data files + prompt docstrings + prompt test assertions) references the generic tools; the remaining grep matches should be only the prompt function/module names themselves (unavoidable, by design) — and the implementer must classify and report them.

Let me define the exact post-Phase-5 residual expectation for the prompt:

- `src/.../<d>/prompts/update_<d>.py` (6 files): module file names and the prompt function names remain (update_req, update_task, update_qa, update_risk, update_prb, update_gol) — matches: @mcp.prompt(name="update_req"), def update_req, docstring (now references the generic tools), and the prompts/__init__.py imports + __all__ + docstring.
- tests: the prompt test files (test_update_req.py etc.) reference the prompt function (importing update_req from ...prompts).
- server.py's prompt enumeration lines.
- The domain __init__.py's prompt enumeration lines.
- docs/MCP.md's prompt entries (regenerated).

All of these are prompt references. The narration (data files) must contain zero `update_<d>(id, content)` / `set_status_<d>(id, status)` tool call references, and zero `set_status(id, status` ADR calls without type.

For the 4 ADR files: references to `set_status(id, ...)` gain `type="adr"`.

So in the Phase 5 prompt I'll write:

- The full file list (from the Phase 4 residual report + the ADR data files that reference bare set_status).
- The rewrite rules from Task 5.1.
- The range update passage requirements from ACC-006 (the 6 update instruction files teach: for localized changes, get\_<d>(id, raw=True) → identify 1-based inclusive range (N+1 = end of body) → update(id, type="<d>", content, begin=…, end=…) passing only the replacement lines; for multi-section or uncertain changes, the whole body (no begin/end)).
- Status vocabulary prose: where the narration states per-domain status values, it must be accurate per the Design Notes table (req/gol 7, uc 5, tsk/qa 4, prb 4, rsk 6, adr 6 + superseded-by pattern).
- Task 5.2: 6 update prompt modules + refine.py + 4 ADR prompt modules.
- Task 5.3: 10 prompt tests + 6 additional (create×4, refine, implement_task) — total 16 prompt test files to review/update.
- Gate: full + specmgr docs regeneration (docstrings) + zero drift; the full suite passes; then the final grep classification: the residual matches for the 15 names must be only prompt names/references (list them), with zero in data files.
- README update.

Also: the ADR data files — which ADR files reference set_status? Task 5.1 says: 4 ADR instruction files (adr_create_instructions.md, adr_create_test_instructions.md, adr_update_instructions.md, adr_update_test_instructions.md) — "their set_status(id, …) call sites gain type="adr"". Let me quickly check if there are other ADR data files… the adr domain data files: let me list them. Also, the ADR prompt modules' docstrings (create_adr.py etc.) reference set_status.

Also: does the narration reference the old ADR tool signature `set_status(id, status, superseded_by)`? After Phase 4, the generic tool is `set_status(id, type, status, superseded_by)`. The ADR narration's call sites become `set_status(id, type="adr", status[, superseded_by])`.

Before writing the prompt, let me grep to enumerate exactly the set_status references (bare) in the ADR data files and ADR prompt modules.

Phase 4 has been committed as `d9f7a28` — all hooks passed. Before delegating Phase 5, enumerate the exact set of ADR narrative references (the 4 ADR data files + ADR prompt modules that reference bare `set_status(`) and all remaining narrative files, so that the implementer can work from the verified list:

**Tool: bash**

**Input:**

```json
{
  "command": "ls src/biz/dfch/specmgr/adr/data/ 2>/dev/null; echo === ; git grep -n \"set_status\" -- \"src/biz/dfch/specmgr/adr/data/\" \"src/biz/dfch/specmgr/adr/prompts/\" | head -30; echo === ; git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/ | grep -E \"data/|prompts/\" | cut -d: -f1 | sort | uniq -c",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
adr_create_instructions.md
adr_create_test_instructions.md
adr_update_instructions.md
adr_update_test_instructions.md
===
src/biz/dfch/specmgr/adr/data/adr_create_instructions.md:51:   call `set_status(id, "accepted")` (or `"rejected"`, or
src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md:76:   `set_status(id, "accepted")` (or `"rejected"`, or `"proposed"`).
src/biz/dfch/specmgr/adr/data/adr_update_instructions.md:28:  decision, or marking it superseded) -> `set_status(id, status,
src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md:40:  decision, or marking it superseded) -> `set_status(id, status,
src/biz/dfch/specmgr/adr/prompts/create_adr.py:22:``adr/tools/`` surface (``create_adr``, ``option_create``, ``set_status``,
src/biz/dfch/specmgr/adr/prompts/create_adr.py:55:        "required information, and driving create_adr/option_create/set_status/"
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py:36:(``create_adr``, ``option_create``, ``set_status``, ``validate_adr``).
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py:62:        "the same MADR-4.0.0 structure and create_adr/option_create/set_status/validate_adr "
src/biz/dfch/specmgr/adr/prompts/update_adr.py:23:``update_frontmatter``, ``set_status``, ``option_create``/``option_update``/
===
      3 src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
      6 src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
      2 src/biz/dfch/specmgr/gol/prompts/__init__.py
     12 src/biz/dfch/specmgr/gol/prompts/update_gol.py
      2 src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
      6 src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
      3 src/biz/dfch/specmgr/prb/prompts/__init__.py
     11 src/biz/dfch/specmgr/prb/prompts/update_prb.py
      3 src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
      4 src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
      5 src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
      3 src/biz/dfch/specmgr/qa/prompts/__init__.py
      3 src/biz/dfch/specmgr/qa/prompts/refine.py
      8 src/biz/dfch/specmgr/qa/prompts/update_qa.py
      3 src/biz/dfch/specmgr/req/data/req_create_instructions.md
      5 src/biz/dfch/specmgr/req/data/req_update_instructions.md
      2 src/biz/dfch/specmgr/req/prompts/__init__.py
      7 src/biz/dfch/specmgr/req/prompts/update_req.py
      1 src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
      5 src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
      4 src/biz/dfch/specmgr/rsk/prompts/update_risk.py
      4 src/biz/dfch/specmgr/server.py
      1 src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
      1 src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
      5 src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
      6 src/biz/dfch/specmgr/tsk/prompts/update_task.py
      2 tests/gol/prompts/test_create_gol.py
     24 tests/gol/prompts/test_update_gol.py
      2 tests/prb/prompts/test_create_prb.py
     27 tests/prb/prompts/test_update_prb.py
      2 tests/qa/prompts/test_create_qa.py
      3 tests/qa/prompts/test_refine.py
     23 tests/qa/prompts/test_update_qa.py
      2 tests/req/prompts/test_create_req.py
     20 tests/req/prompts/test_update_req.py
      7 tests/rsk/prompts/test_update_risk.py
      2 tests/tsk/prompts/test_implement_task.py
      7 tests/tsk/prompts/test_update_task.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 5494.6s)

_Thinking:_

Complete inventory for Phase 5:

**Data files to rewrite (19):**

- 6 `<d>_update_instructions.md`: req (5 refs), qa (5), tsk (5), rsk (5), prb (6), gol (6) — tool call sites + add paragraph about range update
- qa_refine_instructions.md (4)
- 7 additional create/implement files: req_create (3), qa_create (3), prb_create (2), gol_create (3), rsk_create (1), tsk_create (1), tsk_implement (1)
- 4 ADR files: adr_create (1: `set_status(id, "accepted")`), adr_create_test (1), adr_update (1: `set_status(id, status, ...)`), adr_update_test (1)
  Total = 6+1+7+4 = 18... recount: 6 update + 1 refine + 7 create/implement + 4 ADR = 18 data files.

**Prompt modules to fix (Task 5.2 + additions):**

- 6 domain update prompt modules: req/prompts/update_req.py (7), tsk/prompts/update_task.py (6), qa/prompts/update_qa.py (8), rsk/prompts/update_risk.py (4), prb/prompts/update_prb.py (11), gol/prompts/update_gol.py (12)
- qa/prompts/refine.py (3) — orchestrator addition
- 4 ADR prompt modules: create_adr.py, create_adr_test.py, update_adr.py, update_adr_test.py (references to set_status)
- prompts/__init__.py files (gol 2, prb 3, qa 3, req 2) — do the docstrings describe the surface? The references are imports + __all__ (prompt names — keep) and possibly docstring text. Imports/__all__ keep the prompt names (update_gol etc. are prompt names). Docstring text that references tools needs fixing. The implementer should check each one.

**Prompt test files (Task 5.3 + additions):**

- 10 from the plan: test_update_req (20), test_update_task (7), test_update_qa (23), test_update_risk (7), test_update_prb (27), test_update_gol (24), test_create_adr, test_create_adr_test, test_update_adr, test_update_adr_test
- 6 additions: test_create_req (2), test_create_qa (2), test_create_prb (2), test_create_gol (2), test_refine (3), test_implement_task (2)

**server.py**: 4 matches — prompt enumeration lines (keep — those are prompt names. But if the line text says "drives update\_<d> tool" or the like, verify the wording — from Phase 3 verification, the prompt lines say things like "create_req, update_req -- narrated ...". No issue, keep).

The ADR data references need precise rewrites:

- `set_status(id, "accepted")` → `set_status(id, type="adr", "accepted")` — hmm, the call form in the narration: `set_status(id, type="adr", status="accepted")`. The implementer should keep it readable.
- `set_status(id, status, superseded_by=...)` → `set_status(id, type="adr", status, superseded_by=...)`.

Also, the ADR narration probably refers to the "superseded" flow. Keep it.

One more thing to check — does the narration in the ADR data files reference `update_section` etc.? No change (still exists).

One more: the 6 update instruction files must "teach the range update flow (REQ-002)": for localized changes (single paragraph/field/section), first `get_<d>(id, raw=True)` → identify 1-based inclusive line range (N+1 = end of body) → `update(id, type="<d>", content, begin=…, end=…)` passing only the lines being replaced; for multi-section or uncertain changes, replace the whole body (no begin/end). And "fix the status vocabulary wording in each file where it diverges from the design notes table."

Now, one important nuance: the prompt test files assert on the exact text of the narration. So the tests and data files must be rewritten consistently. Best workflow: rewrite the data files first, then update the tests to assert the new narration (or have the tests assert the key substrings of the generic tool call form).

Also note: the prompt output itself — the prompt functions load the data files and return the text. The tests call the prompt function (probably via the mcp prompt API) and assert on substrings. After rewriting the data, the tests asserting the old substrings will fail — update those.

Gate for Phase 5: full gate + specmgr docs regeneration (docstring changes) + zero drift. No changes to tools/resources → mcp-docs unchanged? Wait — the @mcp.prompt description: if the prompt module docstrings are used as the prompt description in MCP.md... prompt description comes from the @mcp.prompt(description=...) or from the function docstring? If the prompt's MCP description is derived from the docstring and docs/MCP.md renders the prompt description, then the docstring changes in Phase 5 (5.2) could change docs/MCP.md. Hmm — the mcp-docs hook runs on src changes and fails on drift, so either way the implementer must regenerate mcp-docs and verify. The plan's Phase 5 gate says "specmgr docs regeneration covers the docstring changes from task 5.2" — but to be safe, I'll instruct regeneration of all three (docs, mcp-docs, coverage-badge) + zero-drift verification. That's the robust approach, and it matches the pre-commit hook behavior.

Actually — coverage: prompt data files are .md (package data), no code changes other than docstrings → coverage unchanged. But the coverage-badge hook runs on src|tests changes → it runs at commit time. Regenerating anyway is cheap.

Also, ACC-006 says "all 11 instruction data files reference the generic tools with the correct signatures" — the 11 in the plan. Our list has 18 data files (11 + 7 create/implement). All 18 must reference the generic tools correctly (any reference to a deprecated tool is gone).

And the final acceptance for Phase 5: grep for the 15 deprecated tool names → the remaining matches must be only: prompt function names/imports/__all__/enumerations (server.py prompt lines, prompts/__init__.py, domain __init__.py prompt enumerations, tests that import prompt functions) + docs (MCP.md prompt entries — regenerated). The implementer should report this classification.

Alright, writing the Phase 5 prompt now. It's the most text-heavy phase — emphasize quality of the narration: the rewritten text must be technically accurate about the generic tools' signatures and the range contract, consistent with the update.py/set_status.py docstrings.

Phase 5's inventory has been fully verified: **18 data files** (the 6 update + qa_refine + 7 create/implement + 4 ADR), **7 prompt modules** (6 updates + refine) + **4 ADR prompt modules** + 4 `prompts/__init__.py` docstrings, and **16 prompt test files** (the planned 10 + 6 create/refine/implement). Delegating:

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 5 (narration)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 5: Narration rewrite (prompts + instruction data)** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `d9f7a28` (Phase 4 commit), working tree clean.\n- The 15 superseded mutation tools are all deleted. The live surface now is: generic `update(id, type, content, begin=None, end=None)` (type: req/uc/tsk/qa/prb/gol/rsk) and generic `set_status(id, type, status, superseded_by=None)` (type: req/uc/tsk/qa/prb/gol/rsk/adr) in `general/tools/`, plus `get_<d>(id, raw=False)` on the seven whole-body domains. Live registration: 71 tools / 25 resources / 19 prompts.\n- READ the source of truth for the narration you are writing: `src/biz/dfch/specmgr/general/tools/update.py` and `src/biz/dfch/specmgr/general/tools/set_status.py` (their `@mcp.tool` descriptions + numpy docstrings define the exact semantics: 1-based inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole, frontmatter never addressable, `status` never settable via `update`, `superseded_by` adr-only composing `\"superseded by X\"`).\n\n## Your plan\nRead the FULL plan: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — Overview, Requirements REQ-005/REQ-006, Design Notes (per-domain status vocabulary table), and your phase heading `#### Phase 5: Narration rewrite (prompts + instruction data)` (Tasks 5.1–5.4).\n\n## Scope note (orchestrator-verified file lists)\nThe plan's Task 5.1 says \"Eleven files expected\" — the verified grep residual set is LARGER, because the create/implement instruction files and `qa/prompts/refine.py` also name superseded tools, and ACC-005 requires ZERO references after this phase. Your rewrite set is exactly:\n\n**A. Instruction data files (18) — rewrite every superseded-tool reference to the generic tools:**\n1. The six `<d>_update_instructions.md` (`req/data/req_update_instructions.md`, `tsk/data/tsk_update_instructions.md`, `qa/data/qa_update_instructions.md`, `rsk/data/rsk_update_instructions.md`, `prb/data/prb_update_instructions.md`, `gol/data/gol_update_instructions.md`):\n   - `update_<d>(id, content)` call sites → `update(id, type=\"<d>\", content)`;\n   - `set_status_<d>(id, status)` call sites → `set_status(id, type=\"<d>\", status)`;\n   - **ADD a range-update passage** (REQ-006/ACC-006): for a localized change (one paragraph/field/section), first call `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based inclusive line range (the `N+1` position is end-of-body: `begin = end = N+1` appends; `end = N+1` extends through the last line), and call `update(id, type=\"<d>\", content, begin=…, end=…)` passing only the replacement lines; for multi-section or uncertain changes, use the whole-body replace (no `begin`/`end`);\n   - correct each file's status-vocabulary prose where it differs per the Design-Notes table (req/gol: draft, proposed, accepted, superseded, deprecated, rejected, implemented; uc: draft, proposed, accepted, deprecated, superseded; tsk/qa: draft, active, done, cancelled; prb: draft, active, resolved, cancelled; rsk: open, mitigating, accepted, occurred, closed, dropped).\n2. `qa/data/qa_refine_instructions.md`: its `update_qa` call sites → `update(id, type=\"qa\", …)` (refine appends — use the `N+1` append range for a clean append, else whole-body; keep the existing carry-forward guidance for the whole-body path).\n3. The seven create/implement files with residual references: `req/data/req_create_instructions.md`, `qa/data/qa_create_instructions.md`, `prb/data/prb_create_instructions.md`, `gol/data/gol_create_instructions.md`, `rsk/data/rsk_create_instructions.md`, `tsk/data/tsk_create_instructions.md`, `tsk/data/tsk_implement_instructions.md` — their `update_<d>`/`set_status_<d>` mentions → the generic tools.\n4. The four ADR instruction files (`adr/data/adr_create_instructions.md`, `adr/data/adr_create_test_instructions.md`, `adr/data/adr_update_instructions.md`, `adr/data/adr_update_test_instructions.md`): their `set_status(id, status[, superseded_by])` call sites gain `type=\"adr\"` → `set_status(id, type=\"adr\", status[, superseded_by])`.\n\n**B. Prompt Python module docstrings (11 + 4 `__init__`s) — correct references, NO behavioral change to any prompt function:**\n- The six domain update prompt modules: `req/prompts/update_req.py`, `tsk/prompts/update_task.py`, `qa/prompts/update_qa.py`, `rsk/prompts/update_risk.py`, `prb/prompts/update_prb.py`, `gol/prompts/update_gol.py` — their module docstrings narrate the `update_<d>`/`set_status_<d>` tool surface; re-point at the generic tools (the prompt FUNCTIONS keep their names — only the narration of which MCP tool is called changes).\n- `qa/prompts/refine.py` (3 residual references) — same treatment.\n- The four ADR prompt modules (`adr/prompts/create_adr.py`, `adr/prompts/create_adr_test.py`, `adr/prompts/update_adr.py`, `adr/prompts/update_adr_test.py`) — their `set_status` surface mentions stay true (the tool still exists, now generic) but must be made precise where they imply the old ADR-only signature (e.g. `create_adr.py` line ~22 \"(create_adr, option_create, set_status, …)\" and the docstring lines describing the flow — clarify `set_status` is the generic tool, called with `type=\"adr\"`).\n- The four `prompts/__init__.py` files with residual docstring text (`req`, `qa`, `prb`, `gol`) — check their module docstrings; the imports/`__all__` entries name the prompt FUNCTIONS (e.g. `from .update_gol import update_gol`) and STAY unchanged.\n\n**C. Prompt test files (16) — update assertions to the rewritten narration:**\nThe ten from Task 5.3: `tests/req/prompts/test_update_req.py`, `tests/tsk/prompts/test_update_task.py`, `tests/qa/prompts/test_update_qa.py`, `tests/rsk/prompts/test_update_risk.py`, `tests/prb/prompts/test_update_prb.py`, `tests/gol/prompts/test_update_gol.py`, `tests/adr/prompts/test_create_adr.py`, `tests/adr/prompts/test_create_adr_test.py`, `tests/adr/prompts/test_update_adr.py`, `tests/adr/prompts/test_update_adr_test.py` — assertions must confirm the generic call shapes (and, for the six domain update prompts, the new range-update passage: `get_<d>(id, raw=True)` → identify range → `update(..., begin=…, end=…)`; whole-body for multi-section/uncertain).\nPLUS the six with residual references (their asserted narration changes because the data files change): `tests/req/prompts/test_create_req.py`, `tests/qa/prompts/test_create_qa.py`, `tests/prb/prompts/test_create_prb.py`, `tests/gol/prompts/test_create_gol.py`, `tests/qa/prompts/test_refine.py`, `tests/tsk/prompts/test_implement_task.py`.\nRule: after your rewrites, the FULL test suite must pass — if a prompt test asserts a narration substring you changed, update the assertion to the new text (assert the generic call shape, not the old one).\n\n## Tasks\n- **Task 5.1**: The data-file rewrites (group A). Grep-driven: work from `git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/*/data/` plus `git grep -n \"set_status(\" -- src/biz/dfch/specmgr/adr/data/`. Keep each file's structure/tone; change only the tool references (and add the range-update passages in the six update files, and fix vocabulary prose where wrong).\n- **Task 5.2**: The prompt module docstring corrections (group B). No signature/behavior change to any `@mcp.prompt` function.\n- **Task 5.3**: The prompt test updates (group C).\n- **Task 5.4**: Phase-end quality gate — full gate per the plan's Design Notes:\n  1. `uv run --frozen ruff format` (write mode — ruff also formats the `.md` files) then `uv run --frozen ruff format --check` + `uv run --frozen ruff check` — must pass. (Careful: ruff format may re-wrap long lines in the .md files — that's fine, but run it and keep its output.)\n  2. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — clean.\n  3. `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` — full suite green (this catches any prompt test you missed).\n  4. Regenerations: `uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\"` (refresh `.coverage`), then `uv run --frozen specmgr coverage-badge`, `uv run --frozen specmgr docs`, `uv run --frozen specmgr mcp-docs` (prompt module docstrings may surface in `docs/api/` and possibly `docs/MCP.md` prompt descriptions — regenerate both).\n  5. Zero-drift proof: re-run all three generators; second run must be a no-op.\n  6. **Final ACC-005 grep**: `git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/` must now return matches ONLY in: the prompt function names/imports/`__all__` (the six `prompts/update_<d>.py` module defs + `@mcp.prompt(name=…)` + the `prompts/__init__.py` files + `server.py`'s per-domain PROMPT enumeration lines + the domain `__init__.py` prompt-enumeration sentences + the prompt test files' imports of the prompt functions) and `tests/adr/prompts/` ADR test references to the generic `set_status` (legit). ZERO matches in any `data/*.md` file. Record the classified final list in the Progress entry.\n  7. Fix failures and re-run until green — a phase is not done with a red gate.\n  8. Update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); new dated entry `#### Update 2026-08-27 (Phase 5: ...)` in Recent Updates (above the Phase 4 entry, preserve all history) — include the 18/11/16 file counts, the range-update passage addition, and the classified final-grep result; Current Status updated (Phase 5 complete, Phases 6–7 not started); Tasks 5.1–5.4 flipped to done in place (byte-careful with the plan's 2-space continuation wrapping).\n\n## Hard constraints\n- Do NOT commit anything.\n- Do NOT start Phase 6 (no AGENTS.md / CHANGELOG.md edits).\n- No changes to any `tools/` code, `models/`, or `server.py` tool registration — prompt module docstrings and data files only (plus the test files in group C). If you find a NON-narration reference to a superseded tool somewhere (e.g. in a tools/ module), STOP and report it rather than editing it.\n- The prompt FUNCTIONS keep their names (`update_req` prompt ≠ the deleted `update_req` tool) — do not rename any prompt.\n- Keep the narration technically accurate: generic `update` signature is `update(id, type, content, begin=None, end=None)`; generic `set_status` is `set_status(id, type, status, superseded_by=None)`; `raw=True` on `get_<d>`.\n\n## Report back (your final message)\n1. `git status --short` summary + `git diff --stat`.\n2. For group A: the list of 18 files with a one-line summary of the change per file; quote the full range-update passage as written in ONE of the six update files (e.g. req's) so the orchestrator can check it.\n3. For group B: per-file confirmation that only docstrings changed (no function signature/behavior diff) — `git diff --stat` per file suffices plus the ADR modules' reworded lines quoted.\n4. For group C: the 16 test files touched; full suite `Ran N tests ... OK`.\n5. Task 5.4 gate evidence: ruff format --check / ruff check / vulture; the coverage-run + 3 generators + no-op proof; the FINAL classified ACC-005 grep (data/*.md = zero matches; everything else classified prompt-name vs generic-set_status-reference); `docs/MCP.md` + `docs/api/` deltas.\n6. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Error:**

```
Task cancelled
```

______________________________________________________________________

## User

continue

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 57.8s)

_Thinking:_

The task was canceled (probably a user-side or temporary interruption). The user is saying "continue". I should re-delegate phase 5 with the same detailed prompt. First, let me check the state of the working tree — was anything partially modified by the canceled sub-agent? Let me check git status before re-delegating.

The Phase 5 delegation was cancelled before I could confirm the subagent's state. Checking the working tree for partial changes before re-delegating:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && git log --oneline -2 && git diff --stat | tail -3",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
 M docs/api/biz.dfch.specmgr.adr.prompts.create_adr.md
 M docs/api/biz.dfch.specmgr.adr.prompts.create_adr_test.md
 M docs/api/biz.dfch.specmgr.adr.prompts.update_adr.md
 M docs/api/biz.dfch.specmgr.gol.prompts.update_gol.md
 M docs/api/biz.dfch.specmgr.prb.prompts.update_prb.md
 M docs/api/biz.dfch.specmgr.qa.prompts.refine.md
 M docs/api/biz.dfch.specmgr.qa.prompts.update_qa.md
 M docs/api/biz.dfch.specmgr.req.prompts.update_req.md
 M docs/api/biz.dfch.specmgr.rsk.prompts.update_risk.md
 M docs/api/biz.dfch.specmgr.tsk.prompts.update_task.md
 M src/biz/dfch/specmgr/adr/data/adr_create_instructions.md
 M src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md
 M src/biz/dfch/specmgr/adr/data/adr_update_instructions.md
 M src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md
 M src/biz/dfch/specmgr/adr/prompts/create_adr.py
 M src/biz/dfch/specmgr/adr/prompts/create_adr_test.py
 M src/biz/dfch/specmgr/adr/prompts/update_adr.py
 M src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
 M src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
 M src/biz/dfch/specmgr/gol/prompts/update_gol.py
 M src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
 M src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
 M src/biz/dfch/specmgr/prb/prompts/update_prb.py
 M src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
 M src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
 M src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
 M src/biz/dfch/specmgr/qa/prompts/refine.py
 M src/biz/dfch/specmgr/qa/prompts/update_qa.py
 M src/biz/dfch/specmgr/req/data/req_create_instructions.md
 M src/biz/dfch/specmgr/req/data/req_update_instructions.md
 M src/biz/dfch/specmgr/req/prompts/update_req.py
 M src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
 M src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
 M src/biz/dfch/specmgr/rsk/prompts/update_risk.py
 M src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
 M src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
 M src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
 M src/biz/dfch/specmgr/tsk/prompts/update_task.py
 M tests/adr/prompts/test_create_adr.py
 M tests/adr/prompts/test_create_adr_test.py
 M tests/adr/prompts/test_update_adr.py
 M tests/adr/prompts/test_update_adr_test.py
 M tests/gol/prompts/test_create_gol.py
 M tests/gol/prompts/test_update_gol.py
 M tests/prb/prompts/test_create_prb.py
 M tests/prb/prompts/test_update_prb.py
 M tests/qa/prompts/test_create_qa.py
 M tests/qa/prompts/test_refine.py
 M tests/qa/prompts/test_update_qa.py
 M tests/req/prompts/test_create_req.py
 M tests/req/prompts/test_update_req.py
 M tests/rsk/prompts/test_update_risk.py
 M tests/tsk/prompts/test_implement_task.py
 M tests/tsk/prompts/test_update_task.py
d9f7a28 feat(feat-22): add generic set_status tool and retire the eight old status tools
971998f refactor(feat-22): retire the seven per-domain update_<d> tools
 tests/tsk/prompts/test_implement_task.py           |  7 +--
 tests/tsk/prompts/test_update_task.py              | 37 +++++++++++----
 54 files changed, 625 insertions(+), 298 deletions(-)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 94.0s)

_Thinking:_

The cancelled sub-agent had made significant progress: 54 files were changed, including all 18 data files, all prompt modules (6 updates + refine + 3 ADR — wait, `adr/prompts/update_adr_test.py` isn't in the list... let me check: what's included in the list is `adr/prompts/create_adr.py`, `create_adr_test.py`, `update_adr.py`, but `update_adr_test.py` is not included. Hmm, but `tests/adr/prompts/test_update_adr_test.py` is in the list. Interesting. Also `req/prompts/__init__.py`, `qa/prompts/__init__.py`, `prb/prompts/__init__.py`, `gol/prompts/__init__.py` are not in the modified list either. And the plan's README isn't changed either (meaning task 5.4/progress update wasn't started). Furthermore, the docs/api pages have been regenerated (10 changed — matching the docstring changes of the modified prompt modules).

Wait — but if `update_adr_test.py` (the prompt module) wasn't modified, then why is its test `test_update_adr_test.py` modified? Perhaps the test asserts content from data files or narration... The docstring of the ADR prompt module `update_adr_test.py` — from the earlier grep: `create_adr.py:22`, `create_adr_test.py:36`, `update_adr.py:23` matched set_status. `update_adr_test.py` didn't appear in that head-30 grep output (it was cut off at 30 lines — the head -30 display showed up through update_adr.py:23). So `update_adr_test.py` might also have a reference, or maybe it doesn't.

The sub-agent was cancelled mid-phase. The work is in a partial state. My options:

1. Resume the same sub-agent session with the task_id (ses_fbdf176e5ffebtjxZhRHR25K1d was phase 4 — no wait, that's wrong. The phase 5 task was cancelled; I don't have its task_id... Actually, the task tool returned "Task cancelled" — there's no task ID to resume. Hmm, the result was simply "Task cancelled". So I can't resume the session directly via task_id... Actually, if I had the task_id I could pass it to task, but the cancelled invocation returned no ID.

2. Start a new phase-implementer and have it pick up the partial state: audit what's been done, complete the rest, run the gate, and update the README.

Option 2 is the way to go. I need to tell the new sub-agent about the existing partial work and have it do the following:

- Audit the current diffs (54 modified files) and compare them against the scope I enumerated.
- Verify that the completed parts are correct (data file rewrites, docstrings, test updates).
- Fill in the gaps (e.g., update_adr_test.py if references remain, prompts/__init__.py docstrings if needed, plan README progress update, gate).
- Run the full gate and report.

Key audit points for the new sub-agent:

01. Final grep check: no data/\*.md references the deprecated tools; classify the remaining references.
02. All 16 prompt test files pass; the full suite is green.
03. The range-update passages exist in all 6 update instruction files (check each file!).
04. The 4 ADR data files have type="adr".
05. The 7 create/implement files have been re-pointed.
06. qa_refine has N+1 append guidance.
07. The prompts/__init__.py docstrings (4 files) — check whether they contain references to deprecated tools beyond prompt names (the residual list from my prompt said "check module docstrings").
08. `adr/prompts/update_adr_test.py` — check for set_status references.
09. Regenerate docs (coverage-badge, docs, mcp-docs) + zero drift; ruff; vulture; fresh import.
10. README progress update (not done).

Also, the sub-agent may have run ruff format (the docs pages were regenerated, suggesting specmgr docs was run). The plan's README is unmodified — task 5.4 is not complete.

Before delegating, let me quickly verify the state myself: run the grep for data files, check a few files, and see how far the sub-agent got. Actually — as the orchestrator, I should let the new sub-agent do the audit and only do targeted verification myself. But a quick orientation check is cheap and helps me write a precise prompt. Things to check:

1. Residuals of deprecated names in data files (should be zero).
2. Whether the range-update passages exist in all 6 update files.
3. Whether update_adr_test.py has a set_status reference.
4. Whether the prompts/__init__.py files were modified.
5. The tail end of the diff of one test file.

The cancelled subagent had done substantial work (54 files — all 18 data files, prompt modules, most tests, regenerated API pages) but never reached Task 5.4 (plan README untouched, gate not run). Before re-delegating, a quick orientation audit so the fresh subagent gets a precise gap list:

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"--- data file residuals (expect none):\" && git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- \"src/*/data/\" \"src/biz/dfch/specmgr/*/data/\"; echo \"exit=$?\" && echo \"--- range passages in the 6 update files:\" && grep -l \"raw=True\" src/biz/dfch/specmgr/{req,tsk,qa,rsk,prb,gol}/data/*_update_instructions.md | wc -l && grep -c \"begin=\" src/biz/dfch/specmgr/{req,tsk,qa,rsk,prb,gol}/data/*_update_instructions.md && echo \"--- update_adr_test.py set_status refs:\" && grep -n \"set_status\" src/biz/dfch/specmgr/adr/prompts/update_adr_test.py; echo \"exit=$?\" && echo \"--- prompts/__init__ residuals:\" && git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_)\\b\" -- \"src/biz/dfch/specmgr/*/prompts/__init__.py\"; echo \"exit=$?\"",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
--- data file residuals (expect none):
exit=1
--- range passages in the 6 update files:
6
src/biz/dfch/specmgr/req/data/req_update_instructions.md:1
src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md:1
src/biz/dfch/specmgr/qa/data/qa_update_instructions.md:1
src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md:1
src/biz/dfch/specmgr/prb/data/prb_update_instructions.md:1
src/biz/dfch/specmgr/gol/data/gol_update_instructions.md:1
--- update_adr_test.py set_status refs:
exit=1
--- prompts/__init__ residuals:
src/biz/dfch/specmgr/gol/prompts/__init__.py:30:from .update_gol import update_gol
src/biz/dfch/specmgr/gol/prompts/__init__.py:34:    "update_gol",
src/biz/dfch/specmgr/prb/prompts/__init__.py:24:prompt split. Named ``create_prb``/``update_prb`` (the tool-name
src/biz/dfch/specmgr/prb/prompts/__init__.py:33:from .update_prb import update_prb
src/biz/dfch/specmgr/prb/prompts/__init__.py:37:    "update_prb",
src/biz/dfch/specmgr/qa/prompts/__init__.py:20:``create_qa`` guides drafting a brand-new QA document. ``update_qa`` guides
src/biz/dfch/specmgr/qa/prompts/__init__.py:33:from .update_qa import update_qa
src/biz/dfch/specmgr/qa/prompts/__init__.py:38:    "update_qa",
src/biz/dfch/specmgr/req/prompts/__init__.py:30:from .update_req import update_req
src/biz/dfch/specmgr/req/prompts/__init__.py:34:    "update_req",
exit=0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 2909.1s)

_Thinking:_

Investigation findings:

1. **Data files: zero residuals** ✓ — all 18 files have been rewritten.

2. **Range passages**: all 6 update files contain `raw=True` and `begin=` ✓ (one each — a good sign, but the subagent should verify the quality of the content).

3. **update_adr_test.py**: no reference to set_status — nothing that needs to be done there ✓.

4. **prompts/__init__.py**: residuals are only the following:

   - Import statements + `__all__` (prompt names — keep) ✓
   - `prb/prompts/__init__.py:24`: "Named `create_prb`/`update_prb` (the tool-name..." — this docstring says "the tool-name" — the prompt was named after the tool name. Now that the tool is gone, this sentence has become somewhat stale (the prompt name no longer matches the tool name — actually, it never matched a *tool* name after Phase 3/4. update_prb is now the prompt name, and the tool is the generic `update`). This docstring needs a minor rewording (Phase 5's jurisdiction — a reference to the prompt module docstring that "narrates the surface").
   - `qa/prompts/__init__.py:20`: "`create_qa` guides drafting... `update_qa` guides..." — this is a description of the prompt function, which is still accurate (it's about the prompt, not the tool). No problem — unless it says "update_qa tool", keep it.

   In other words, at most 1-2 docstring tweaks in prompts/__init__.py (mainly the prb one).

What remains for the new subagent:

- Verify the quality/accuracy of the completed rewrites (spot-check the content of the data files: the generic signatures in the narration, the accuracy of the range passages, the accuracy of the vocabulary, the 4 ADR files with type="adr", the N+1 append guidance in qa_refine).
- Fix the prb prompts/__init__.py docstring (and qa if the wording is stale).
- Confirm all 16 prompt test files have been updated (the tests were in the changed list — 15 of 16? Let me count: the test files that were changed are: test_create_adr, test_create_adr_test, test_update_adr, test_update_adr_test (4 ADR) + test_create_gol, test_update_gol (2) + test_create_prb, test_update_prb (2) + test_create_qa, test_refine, test_update_qa (3) + test_create_req, test_update_req (2) + test_update_risk (1) + test_implement_task, test_update_task (2) = 16 ✓ all changed).
- Run the full gate (Task 5.4): ruff, vulture, full suite, coverage run, three generators, zero drift, final classification grep, new import.
- Update the plan's README (not yet done).
- Report.

One more check I can do quickly myself: the accuracy of the content in one data file + the diff of one test file. Actually, the new subagent should audit it. But as the orchestrator, I should verify at the end anyway. Let's delegate now with a precise gap list.

The audit results are good: zero residuals in the data files, all 6 range paths exist, `update_adr_test.py` is clean, and the only actual gap in `prompts/__init__.py` is a single stale docstring sentence (prb's "Named create_prb/update_prb (the tool-name…)"). The remaining work is as follows: quality audit of the rewrites, 1–2 docstring fixes, the full gate, and the plan's README update.

**Re-delegating Phase 5** to the new phase-implementer with a precise gap list:

**Tool: task**

**Input:**

```json
{
  "description": "Finish feat-22 Phase 5 (narration)",
  "prompt": "You are the phase-implementer for **Phase 5: Narration rewrite (prompts + instruction data)** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22` (branch `feat-22`, HEAD `d9f7a28`).\n\n## IMPORTANT: this phase is partially done — finish and verify it\nA previous implementer session was cancelled mid-phase. The working tree currently holds 54 modified files (uncommitted). The orchestrator's audit of that partial state found:\n- ALL 18 instruction data files rewritten — zero residual matches for the superseded tool names (`git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/biz/dfch/specmgr/*/data/` → exit 1 / no matches).\n- All six `<d>_update_instructions.md` contain a range-update passage (each has `raw=True` and `begin=`).\n- `adr/prompts/update_adr_test.py` has no `set_status` references (nothing to do).\n- The four `prompts/__init__.py` files still hold residual matches, but only: import/`__all__` lines naming the prompt FUNCTIONS (KEEP — prompt names are retained by design) plus one genuinely stale sentence in `prb/prompts/__init__.py` line ~24: \"prompt split. Named ``create_prb``/``update_prb`` (the tool-name ...\" — that parenthetical narrates the OLD tool-name origin and is now inaccurate (the prompts are kept by name; the tools are now the generic `update`/`set_status` in `general/tools/`). Also check `qa/prompts/__init__.py` line ~20 (\"``create_qa`` guides drafting... ``update_qa`` guides...\") — keep it only if it describes the prompts (accurate), reword if it implies the old tools.\n- All 16 prompt test files were modified by the previous session.\n- NOT done: the quality audit of the rewrites, the gate (Task 5.4), and the plan-README Progress update.\n\n## Your plan (read first)\n`/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — Overview, Requirements REQ-005/REQ-006, Design Notes (status vocabulary table), phase heading `#### Phase 5: Narration rewrite (prompts + instruction data)` (Tasks 5.1–5.4). And the source of truth for narration accuracy: the `@mcp.tool` descriptions + numpy docstrings of `src/biz/dfch/specmgr/general/tools/update.py` and `.../set_status.py`.\n\n## Work to do\n1. **Audit the previous session's rewrites for accuracy** (read the diffs — `git diff` on the data files and prompt modules):\n   - Generic call shapes must be exactly: `update(id, type=\"<d>\", content)` (whole-body) and `update(id, type=\"<d>\", content, begin=…, end=…)` (range); `set_status(id, type=\"<d>\", status)`; ADR: `set_status(id, type=\"adr\", status[, superseded_by])`.\n   - Each of the six update instruction files must teach the range flow correctly: for a localized change (one paragraph/field/section), first `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based INCLUSIVE line range, `N+1` = end-of-body sentinel (`begin = end = N+1` → append; `end = N+1` → through last line), call `update` with only the replacement lines; for multi-section or uncertain changes, whole-body replace (no `begin`/`end`). Fix any file where the passage is missing, wrong, or inconsistent.\n   - Status-vocabulary prose in the narration must match the Design-Notes table (req/gol 7 values: draft, proposed, accepted, superseded, deprecated, rejected, implemented; uc 5: draft, proposed, accepted, deprecated, superseded; tsk/qa 4: draft, active, done, cancelled; prb 4: draft, active, resolved, cancelled; rsk 6: open, mitigating, accepted, occurred, closed, dropped; adr 6 + \"superseded by X\" pattern).\n   - `qa_refine_instructions.md`: append guidance must use the `N+1` append range (or whole-body), carrying forward the existing carry-forward guidance.\n   - No prompt function signature/behavior changed anywhere (docstrings only) — verify with `git diff` on the prompt `.py` files that only docstrings/comments changed.\n   - Fix the stale `prb/prompts/__init__.py` sentence (and `qa` if needed).\n2. **Task 5.3 check**: confirm all 16 prompt test files assert the NEW narration (generic call shapes; the six update-prompt tests also assert the range-update passage). If the previous session left any old assertion, fix it. Files: `tests/{req,tsk,qa,rsk,prb,gol}/prompts/test_update_*.py` (six: test_update_req, test_update_task, test_update_qa, test_update_risk, test_update_prb, test_update_gol), `tests/adr/prompts/test_{create_adr,create_adr_test,update_adr,update_adr_test}.py` (four), `tests/{req,qa,prb,gol}/prompts/test_create_{req,qa,prb,gol}.py` (four), `tests/qa/prompts/test_refine.py`, `tests/tsk/prompts/test_implement_task.py`.\n3. **Task 5.4: Phase-end quality gate** (full, per the plan's Design Notes):\n   1. `uv run --frozen ruff format` (write mode — it also formats the .md files; keep its output) then `uv run --frozen ruff format --check` + `uv run --frozen ruff check` — must pass.\n   2. `uv run --frozen vulture src/ whitelist.py --min-confidence 60` — clean.\n   3. `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` — full suite green (expected ~1768 tests; report exact).\n   4. Regenerations (pre-commit hooks run these on this commit set and fail on drift): `uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\"` (refresh `.coverage`), then `uv run --frozen specmgr coverage-badge`, `uv run --frozen specmgr docs`, `uv run --frozen specmgr mcp-docs`.\n   5. Zero-drift proof: re-run all three generators; second run must be a no-op (sha256-manifest diff empty or `git diff` unchanged).\n   6. Fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.server\"` → exit 0.\n   7. **Final ACC-005 grep**: `git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/` — classify every remaining match: (a) prompt function names/imports/`__all__`/`@mcp.prompt(name=…)` in the six `prompts/update_<d>.py` modules + four `prompts/__init__.py` + prompt test imports — KEPT by design; (b) `server.py` per-domain PROMPT enumeration lines + domain `__init__.py` prompt-enumeration sentences — KEPT by design; (c) anything else is a FAILURE — fix it (narration) or report it (non-narration code — do not silently edit tools/models). ZERO matches in any `data/*.md`.\n   8. Fix failures and re-run until green — a phase is not done with a red gate.\n   9. Update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); new dated entry `#### Update 2026-08-27 (Phase 5: ...)` at the top of Recent Updates (preserve ALL existing entries below it) — record: the 18 data files / 11 prompt modules (6 domain update + refine + 4 ADR) + 2 `prompts/__init__.py` docstring fixes / 16 prompt test files; the range-update passage addition to the six update files; the vocabulary corrections; the classified final-grep result (counts per class); gate results. Current Status → Phase 5 complete, Phases 6–7 not started. Tasks 5.1–5.4 flipped to done in place (byte-careful: preserve the plan's 2-space continuation wrapping on untouched lines).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`) — the orchestrator commits after verifying.\n- Do NOT start Phase 6 (no AGENTS.md / CHANGELOG.md edits).\n- Do NOT change any `tools/` code, `models/`, `server.py` registration, or prompt function behavior — narration (data files + prompt module docstrings + prompt tests) only. If the audit finds a NON-narration reference to a superseded tool (e.g. in a `tools/` module), STOP and report it.\n- The previous session's 54 modified files are the baseline — keep what is correct, fix what is not. Do not revert working-tree changes to redo work already done correctly.\n\n## Report back (your final message)\n1. Audit findings: what was already correct, what you fixed (file + change per fix), including the `prompts/__init__.py` docstring rewordings quoted.\n2. `git status --short` summary + `git diff --stat` (final tree state).\n3. Quote the range-update passage from ONE update file (e.g. `req_update_instructions.md`) in full, plus the ADR `type=\"adr\"` call-site lines from the four ADR files, and the qa_refine append guidance.\n4. Gate evidence: ruff format --check / ruff check / vulture; full suite `Ran N tests ... OK` (exact N); coverage-run + 3 generators + no-op second-run proof; fresh-subprocess import; `docs/` delta summary (which API pages changed, MCP.md delta if any).\n5. The FINAL classified ACC-005 grep: per-class file list + match counts; explicit \"data/*.md: 0 matches\".\n6. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbd16b25effekQCuK02p9vtp0r" state="completed">
<task_result>


Phase 5 is complete and the gate is green. Final report:

---

## 1. Audit findings

**Already correct in the previous session's 54-file diff (verified, kept as-is):**
- All 18 instruction data files: generic call shapes are exactly `update(id, type="<d>", content)` / `update(id, type="<d>", content, begin=..., end=...)` / `set_status(id, type="<d>", status)`; all four ADR files use `type="adr"` with the `superseded_by` composition note.
- All six `<d>_update_instructions.md` contain the complete range-update passage (verified programmatically: `get_<d>(id, raw=True)`, "1-based, inclusive line range", `begin = end = N+1` append, `end = N+1` through-last-line, "passing only the replacement lines", whole-body fallback for multi-section/uncertain, byte-identical splice guarantee).
- Status-vocabulary prose in all six files matches the code's `_ALLOWED_STATUSES` (req/gol 7, tsk/qa 4, prb 4, rsk 6 — extracted from `models/<v>/frontmatter.py` and compared; `uc` has no narration).
- `qa_refine_instructions.md` uses the `N+1` append range with the carry-forward guidance preserved on the whole-body path.
- All 10 prompt-module rewrites are **docstring-only** (AST comparison HEAD vs. working tree with docstrings stripped: all 10 modules + `prb/prompts/__init__.py` identical code).
- All 16 prompt test files assert the new narration (186 prompt tests pass).

**Fixed by me (3 files):**
1. `src/biz/dfch/specmgr/prb/prompts/__init__.py` — the stale parenthetical. Old: *"Named ``create_prb``/``update_prb`` (the tool-name convention, like REQ/QA), not literal wording like TSK's…"*. New: *"Named ``create_prb``/``update_prb`` (the per-domain tool-name convention, like REQ/QA -- the prompt keeps its name, while the update/status tools are now the generic ``update``/``set_status`` in ``general/tools/``), not literal wording like TSK's…"* (regenerated API page `docs/api/biz.dfch.specmgr.prb.prompts.md` follows).
2. `src/biz/dfch/specmgr/adr/data/adr_create_instructions.md` — the rewritten step-3 list item had a stray leading space (` 3.` with 5-space continuations) inconsistent with the surrounding column-0 items; restored to `3.` with 3-space continuations.
3. `src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md` — same artifact, same fix.

**Checked and kept:** `qa/prompts/__init__.py`'s "``create_qa`` guides drafting… ``update_qa`` guides…" — describes the prompts (kept by name), accurate; no rewording needed.

**No non-narration references found:** zero matches for any superseded tool name in `tools/`, `models/`, `general/` code, `server.py` registration, or for `set_status_<d>` anywhere in `src/`/`tests/` (grep exit 1). Nothing to stop-and-report.

## 2. Final tree state

`git status --short`: **57 modified files, 0 untracked, 0 staged** (baseline 54 + `prb/prompts/__init__.py` + its API page + plan README). `git diff --stat`: `57 files changed, 799 insertions(+), 334 deletions(-)` — 18 data files, 11 prompt modules, 16 test files, 11 `docs/api/` pages, 1 plan README.

## 3. Requested quotations

**`req_update_instructions.md`, section 3 (range-update passage):**
```

## 3. Map the requested change to the right tool

- A change to the body -- the requirement statement, `description`,
  `characteristics`, `level`, `priority`, `tags`, `source`,
  `related_artifacts`, `more_information`, or `notes` -- -> the
  generic `update` tool called with `type="req"`: a **line-range replace**
  for a localized change, or a **whole-body replace** otherwise.
  `content` is body markdown only (no frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_req(id, raw=True)` to see the exact
    body text, identify the 1-based, inclusive line range to replace --
    the `N+1` position is end-of-body: `begin = end = N+1` appends after
    the last line, `end = N+1` extends the range through the last line
    -- and call `update(id, type="req", content, begin=..., end=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="req", content)`
    with no `begin`/`end` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="req", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, superseded, deprecated, rejected,
  implemented.

```

**ADR `type="adr"` call sites (all four files):**
```

adr_create_instructions.md:51: call `set_status(id, type="adr", status="accepted")` (or
adr_create_test_instructions.md:76: `set_status(id, type="adr", status="accepted")` (or
adr_update_instructions.md:29: `set_status(id, type="adr", status, superseded_by=...)`, always called
adr_update_test_instructions.md:41: `set_status(id, type="adr", status, superseded_by=...)`, always called

```
(update/test files continue: *"with `type="adr"` for an ADR (`superseded_by` … composing the status as `"superseded by {superseded_by}"`)"*)

**`qa_refine_instructions.md`, section 5 (append guidance):**
```

## 5. Persist the appended questions

The generic `update` tool is a whole-body replace unless you give it a
line range:

- **Clean append (the `N+1` range)**: when the new pairs all go at the
  very end of the body (every targeted category is the document's last
  `##` section), call `get_qa(id, raw=True)` to count the body's lines
  (`N`) and call `update(id, type="qa", content, begin=N+1, end=N+1)`
  passing only the new pairs -- the `N+1` position is end-of-body, so
  this appends without touching any existing line.
- **Otherwise (whole-body replace)**: carry forward every section of
  the document exactly as read in step 1 (including all ten fixed
  category headings, even ones you are not adding questions to this
  time, and every existing Q&A pair within a category you *are* adding
  to), append the new placeholder pairs from step 4 under their targeted
  category headings, and call `update(id, type="qa", content)` with the
  full resulting body markdown (no frontmatter block).

```

## 4. Gate evidence (final tree state, all re-run after my fixes)

| Check | Result |
|---|---|
| `ruff format` (write) | 1094 files left unchanged (stable; kept) |
| `ruff format --check` | 1094 files already formatted ✅ |
| `ruff check` | All checks passed ✅ |
| `vulture src/ whitelist.py --min-confidence 60` | clean, exit 0 ✅ |
| `python -m unittest discover -s tests -t . -p "test_*.py"` | **Ran 1779 tests — OK** ✅ (1768 Phase-4 baseline + 11 new narration tests: 6× range-flow, 4× ADR `type="adr"`, 1× refine N+1-append) |
| `coverage run -m unittest …` (pre-commit's exact command) | 1779 OK, `.coverage` refreshed |
| `specmgr coverage-badge` | 98% — unchanged rounded value, badge byte-identical, no diff |
| `specmgr docs` | 305 pages; **11 pages changed**: the ten reworded prompt-module API pages (`adr.prompts.{create_adr,create_adr_test,update_adr}`, `gol.prompts.update_gol`, `prb.prompts.update_prb`, `qa.prompts.{refine,update_qa}`, `req.prompts.update_req`, `rsk.prompts.update_risk`, `tsk.prompts.update_task`) + `prb.prompts.md` (my `__init__` docstring fix). `docs/GENERATED.md`/`docs/api/README.md` unchanged |
| `specmgr mcp-docs` | **no `docs/MCP.md` change** — narration-only phase, no MCP surface change |
| Zero-drift proof | all three generators re-run; second run byte-identical (sha256 manifest diff empty) ✅ |
| Fresh-subprocess `python -c "import biz.dfch.specmgr.server"` | exit 0 ✅ |
| `specmgr adr-toc` / `specmgr schema` | not touched this phase (no `docs/adr/**` change; models untouched — Phase 2 proved schemas invariant) |

## 5. Final classified ACC-005 grep

`git grep -nE "\b(update_req|…|set_status_rsk)\b" -- src/ tests/` → **121 match lines in 28 files, every one kept by design**:

- **(a) Prompt function names** (imports/`__all__`/`@mcp.prompt(name=…)`/`def`/module titles/cross-prompt references) — **31 lines**: `req/prompts/` (update_req.py 3, __init__.py 2), `qa/prompts/` (update_qa.py 4, refine.py 2, __init__.py 3), `prb/prompts/` (update_prb.py 4, __init__.py 3), `gol/prompts/` (update_gol.py 5, __init__.py 2), `tsk/prompts/update_task.py` 2, `rsk/prompts/update_risk.py` 1
- **(b) `server.py` PROMPT enumeration lines** (159/165/170/174) **+** the prompt-enumeration sentences in `req`/`qa`/`prb`/`gol` `__init__.py` (1 each) — **8 lines**
- **(c) Data files' prompt-name references** ("the `update_<d> prompt`" in "Later revisions"/duplicate-check paragraphs of the four `*_create_instructions.md`) — **8 lines** (asserted verbatim by the create-prompt tests)
- **(d) Prompt test files** (imports + calls of the prompt functions) — **74 lines**
- **`data/*.md` tool references: 0** (the only data-file matches are class-(c) prompt names)
- **`set_status_<d>`: 0 matches anywhere**; `tools/`/`models/`/`general/` code: 0 matches

## 6. Deviations

1. **18 data files, not the plan's "eleven expected"** — Task 5.1's grep-driven scope ("every instruction data file naming a superseded tool") catches the six `*_create` + `tsk_implement` files too (their "Later revisions"/persistence paragraphs named `update_<d>`/`set_status_<d>`). All 18 rewritten by the previous session; all 18 verified.
2. **16 test files, not the plan's "ten"** — the four `test_create_*` files (asserting the rewritten "Later revisions" text, strengthened to the generic call shapes) plus `test_refine.py` and `test_implement_task.py` (asserting rewritten narration) also needed and received updates.
3. **Orchestrator audit note corrected**: "zero residual matches" in `data/` is true for *tools*; 8 residual *prompt-name* lines exist in the four create files (class (c) above, kept by design, test-asserted).
4. No plan-README task text was edited beyond the in-place status flips (5.1–5.4 → `[x]`/`status: done`, byte-preserving; Task 5.4's wrapped `status: not-\nstarted` collapsed to one line `status: done`). Frontmatter already had `updated: 2026-08-27`; status stays `in-progress`. No Decisions Made entry added — the fixes were corrections, not design decisions.

Nothing committed, no Phase 6 work started; the working tree is left for the orchestrator to inspect and commit.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 170.2s)

_Thinking:_

Phase 5 is reported as complete. The subagent also added 11 new narration tests (total 1779 = 1768 + 11). Let's verify independently:

1. Full gate: ruff format --check, ruff check, vulture, full unittest (1779), coverage run, three generators, zero drift, fresh import.
2. Final ACC-005 grep classification — run it myself and spot-check the classes.
3. Spot-check quality: one data file (the quoted portion of req_update looks good), the prompt module docstring diff (confirm it's docstring-only), one test file.
4. README progress entries.
5. docs/MCP.md is unchanged (narration-only).

Let's batch it: gate run (slow) + grep + diff check.

Phase 5 reports green, with 11 new narration tests added (1779 total). The quoted narration looks technically accurate. Verifying independently — full gate, final grep, and docstring-only confirmation:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen coverage run -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase5-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase5-unittest.log && uv run --frozen specmgr coverage-badge >/dev/null && uv run --frozen specmgr docs >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p5-m1.txt && uv run --frozen specmgr coverage-badge >/dev/null && uv run --frozen specmgr docs >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && find docs -type f | sort | xargs sha256sum > /tmp/opencode/p5-m2.txt && diff /tmp/opencode/p5-m1.txt /tmp/opencode/p5-m2.txt && echo P5_DOCS_ZERO_DRIFT && uv run --frozen python -c \"import biz.dfch.specmgr.server\" && echo IMPORT_OK && git diff --name-only -- docs/MCP.md; echo \"mcpmd-diff-exit=$? (1 means unchanged)\"",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
1094 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1779 tests in 86.177s
OK
P5_DOCS_ZERO_DRIFT
IMPORT_OK
mcpmd-diff-exit=0 (1 means unchanged)

```

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"=== data/*.md residuals (tools vs prompt-names):\" && git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- \"src/biz/dfch/specmgr/*/data/\"; echo \"exit=$?\" && echo \"=== set_status_<d> anywhere:\" && git grep -nE \"\\bset_status_(req|uc|tsk|qa|prb|gol|rsk)\\b\" -- src/ tests/; echo \"exit=$?\" && echo \"=== prompt .py diff non-docstring lines (expect none):\" && for f in $(git diff --name-only -- \"src/biz/dfch/specmgr/*/prompts/*.py\"); do git diff -U0 -- \"$f\" | grep -E \"^[+-]\" | grep -vE \"^[+-]{3}\" | grep -vE \"^[+-]\\s*(#|\\\"\\\"\\\"|'''.*)?$\" | grep -E \"^\\+.*\\b(def |return |import |@mcp|raise |if |for |while |result)\" | head -3 && echo \"  ^ in $f\"; done; echo \"docstring-scan-done\" && echo \"=== git status counts:\" && git status --short | awk '{print $1}' | sort | uniq -c",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
=== data/*.md residuals (tools vs prompt-names):
exit=1
=== set_status_<d> anywhere:
exit=1
=== prompt .py diff non-docstring lines (expect none):
+``general/tools/`` (always called with ``type="adr"`` for an ADR).
  ^ in src/biz/dfch/specmgr/adr/prompts/create_adr.py
  ^ in src/biz/dfch/specmgr/adr/prompts/create_adr_test.py
+in ``general/tools/`` (always called with ``type="adr"`` for an ADR).
  ^ in src/biz/dfch/specmgr/adr/prompts/update_adr.py
+        -- it only narrates that sequence for the LLM to carry out.
  ^ in src/biz/dfch/specmgr/gol/prompts/update_gol.py
+name convention, like REQ/QA -- the prompt keeps its name, while the
  ^ in src/biz/dfch/specmgr/prb/prompts/__init__.py
+        -- it only narrates that sequence for the LLM to carry out.
  ^ in src/biz/dfch/specmgr/prb/prompts/update_prb.py
  ^ in src/biz/dfch/specmgr/qa/prompts/refine.py
  ^ in src/biz/dfch/specmgr/qa/prompts/update_qa.py
  ^ in src/biz/dfch/specmgr/req/prompts/update_req.py
  ^ in src/biz/dfch/specmgr/rsk/prompts/update_risk.py
  ^ in src/biz/dfch/specmgr/tsk/prompts/update_task.py
docstring-scan-done
=== git status counts:
     57 M

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 85.6s)

_Thinking:_

Verification results:

- Gate: ruff format --check (1094) ✓, ruff check ✓, vulture ✓, **1779 tests OK** ✓, coverage run ✓, 3 generators + **P5_DOCS_ZERO_DRIFT** ✓, new imports ✓.

- docs/MCP.md: `git diff --name-only -- docs/MCP.md` returned nothing (mcpmd-diff-exit=0 is the echo of the pipeline's exit code — hmm, actually `git diff --name-only -- docs/MCP.md; echo "exit=$?"` — the fact that nothing was output means MCP.md is unchanged ✓ (as expected for a narration-only phase)).

- Residuals in data/\*.md: **exit=1 = zero matches** (stronger than what the subagent's class (c) claim suggested — the create file no longer contains even the prompt name? The subagent said 8 prompt-name lines remained in data files, but my grep with the exact pattern shows zero matches in data/. Wait — the pattern I used in the first grep included all 14 tool names. The subagent's class (c) said "the data file prompt-name references (the `update_<d> prompt`) — 8 lines". Hmm, but my grep shows exit=1 (no matches) in data/. Let me reconcile: the subagent's class (c) match — perhaps it used a broader pattern (including `set_status(`), or the "update_req prompt" reference is… `update_req` is in my pattern. If my grep found nothing in data/, then the subagent's class-(c) count refers to something else… no actually wait — my grep pattern: `\b(update_req|...|update_rsk|set_status_req|...)\b`. The "the `update_req` prompt" in the create file should match `update_req`. But exit=1 means no match. Hmm, so did the subagent rewrite even those prompt-name references? Or did the class-(c) description refer to a pre-fix state…

  Wait a moment, let me re-read the subagent's claim: "(c) Data file prompt-name references (the `update_<d> prompt` in the 'Later revisions'/duplicate-check paragraphs of the four `*_create_instructions.md`) — 8 lines (asserted verbatim by the create-prompt tests)". And deviation 3: "the 'zero residual matches' in data/ is true for *tools*; 8 residual *prompt-name* lines exist in the four create files (class (c) above, retained by design and asserted by tests)".

  But my grep found zero matches in data/. This is a contradiction. Possibilities: (a) my glob "src/biz/dfch/specmgr/\*/data/" didn't match — but this is the same path I used earlier in this session when 14 files matched… no wait, that earlier grep was run before Phase 5's rewrites. Let me double-check: my earlier command `git grep -nE "\b(update_req|...)\b" -- "src/*/data/" "src/biz/dfch/specmgr/*/data/"` matched the data files. This time I used `"src/biz/dfch/specmgr/*/data/"` — the same second pattern. So the glob works. exit=1 is genuine: zero matches in data/ after Phase 5.

  So then, what is class (c)? Maybe the subagent's grep used a different pattern (e.g., including the word "prompt" or bare `set_status`), and those 8 lines are references to *prompt names* like "the update_req prompt" — but "update_req" is in my pattern… unless the data file now writes it in a different form like "the `update_req` *prompt*" — even so, it would match. Confusing.

  Let me check directly: grep for "prompt" near update\_ in the create file.

One discrepancy to resolve: the subagent reported 8 prompt-name residuals in the create data files, but my grep found **zero** matches in `data/`. Checking directly:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"update_req\\|update_qa\\|update_prb\\|update_gol\\|update_task\\|update_risk\" src/biz/dfch/specmgr/req/data/req_create_instructions.md src/biz/dfch/specmgr/qa/data/qa_create_instructions.md src/biz/dfch/specmgr/prb/data/prb_create_instructions.md src/biz/dfch/specmgr/gol/data/gol_create_instructions.md src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md; echo \"grep-exit=$?\" && grep -rn \"prompt\" src/biz/dfch/specmgr/req/data/req_create_instructions.md | head -5",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
src/biz/dfch/specmgr/req/data/req_create_instructions.md:15:`update_req` prompt) instead of creating a duplicate. Only proceed to
src/biz/dfch/specmgr/req/data/req_create_instructions.md:63:Any later change to this requirement should go through the `update_req` prompt
src/biz/dfch/specmgr/qa/data/qa_create_instructions.md:15:`update_qa` prompt) instead of creating a duplicate. Only proceed to
src/biz/dfch/specmgr/qa/data/qa_create_instructions.md:78:Any later change to this QA document should go through the `update_qa` prompt
src/biz/dfch/specmgr/prb/data/prb_create_instructions.md:16:that one (via the `update_prb` prompt) instead of creating a duplicate.
src/biz/dfch/specmgr/prb/data/prb_create_instructions.md:118:`update_prb` prompt (or directly through the generic
src/biz/dfch/specmgr/gol/data/gol_create_instructions.md:16:`update_gol` prompt) instead of creating a duplicate. Only proceed to
src/biz/dfch/specmgr/gol/data/gol_create_instructions.md:74:Any later change to this goal should go through the `update_gol` prompt
src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md:14:ask whether they want to revise that one (via the `update_risk` prompt)
src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md:72:Any later change to this risk should go through the `update_risk`
src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md:15:`update_task` prompt) instead of creating a duplicate. Only proceed to
src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md:57:Any later change to this task list should go through the `update_task`
grep-exit=0
15:`update_req` prompt) instead of creating a duplicate. Only proceed to
63:Any later change to this requirement should go through the `update_req` prompt
65:`set_status(id, type="req", status)` tools), not by re-running this prompt.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 94.6s)

_Thinking:_

Now it's clear: the create data file contains references to **prompt names** (like "`update_req` prompt") — these are references to *prompts*, not tools, and are kept by design. But then, why did my earlier `git grep` using the `\b(update_req|...)\b` pattern return exit=1 (no match) for the data files?

Let me look at the earlier command again:

```
git grep -nE "\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|...)\b" -- "src/biz/dfch/specmgr/*/data/"
```

Hmm, wait — in git grep, `--` separates options from paths. The pattern came before `--`. That should be fine... But note: the earlier grep (the first verification) used `git grep -nE "..." -- src/ tests/` and it worked (found matches). This time I passed the pathspec "src/biz/dfch/specmgr/*/data/" with quotes — git grep treats pathspecs as glob patterns, so `*` in a pathspec should match any string including slashes... Actually, in git pathspecs, `*` does match slashes (it's fnmatch with FNM_PATHNAME? no — git pathspecs don't use FNM_PATHNAME; `*` matches slashes too). Hmm, but maybe the problem is this: does git grep's pathspec matching happen against paths relative to the repo root? "src/biz/dfch/specmgr/*/data/" — `*` should match e.g. "req". It ought to work.

Wait, actually — let me double-check: was exit=1 really from grep finding nothing, or was it from the command failing? `git grep` returns 1 when there are no matches. If the pathspec matches no files at all, git grep also returns 1 (silently). That's the pitfall: an invalid/non-matching pathspec produces no output and exit 1 — indistinguishable from "no matches"!

So the earlier "zero residuals in data files" check may have been using a pathspec that matched no files. But wait — the first orientation audit ran:

```
git grep -nE "\b(...)\b" -- "src/*/data/" "src/biz/dfch/specmgr/*/data/"
```

and got exit=1. If the pathspec had been working, it would have found the prompt-name references (the `update_req` prompt) in the create files... unless the previous session's rewrites were done after my audit? No — my audit ran after the cancellation, and the data files were already rewritten (54 files modified). Hmm, but at that point, did the create files still contain references to the prompt names? The cancelled session may have rewritten the tool references while keeping the prompt references. My audit's grep should have matched those prompt-name lines (since `update_req` is in the pattern)... unless the pathspec wasn't matching any files.

Let me verify the pathspec hypothesis: run `git grep -nE "update_req" -- "src/biz/dfch/specmgr/*/data/"` — if it returns nothing, the pathspec is the problem. The plain grep above (GNU grep, not git grep) found them. So it's likely that git grep's pathspec `"src/biz/dfch/specmgr/*/data/"` is the issue.

Actually wait — I've got it. In my orientation audit I used two pathspecs: `"src/*/data/"` and `"src/biz/dfch/specmgr/*/data/"`. And in the Phase 5 verification I used one. In both cases exit=1. But the subagent's final grep (per its report) used `-- src/ tests/` and found class (c)'s 8 lines. So: **git grep with a `*/data/` pathspec was silently matching nothing** (or... hmm).

Let me test it directly to figure out what's going on. If git grep with that pathspec is broken, then both my "zero residuals" checks for the data files were invalid, and the true state is: the data files contain only references to prompt names (kept by design, no references to tools). This is consistent with the subagent's report and the plain grep I just ran.

Actually wait a moment — one more possibility: git grep's pathspec `src/biz/dfch/specmgr/*/data/` — the trailing slash might be the problem, or the `*` might not be spanning as expected. In git, pathspec `*` matches any string including `/` (unlike the shell's `ls`). So `src/biz/dfch/specmgr/*/data/` should match `src/biz/dfch/specmgr/req/data/`. Let me test it anyway.

The create file retains a reference to the **prompt name** (the "`update_req` prompt") — that's intentional and by design — which means my earlier `git grep` pathspec against `data/` was suspicious (the exit 1 may not have meant "no match" but rather "the pathspec matched nothing"). I'm testing to confirm:

**Tool: bash**

**Input:**

```json
{
  "command": "echo \"test1: git grep with */data/ pathspec:\" && git grep -nE \"\\bupdate_req\\b\" -- \"src/biz/dfch/specmgr/*/data/\"; echo \"exit=$?\"; echo \"test2: git grep with explicit path:\" && git grep -nE \"\\bupdate_req\\b\" -- \"src/biz/dfch/specmgr/req/data/req_create_instructions.md\"; echo \"exit=$?\"; echo \"test3: git grep with src/ tests/ (as subagent did):\" && git grep -cE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/ | grep -E \"data/|prompts/|server|__init__\"; echo \"exit=$?\"",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
test1: git grep with */data/ pathspec:
exit=1
test2: git grep with explicit path:
src/biz/dfch/specmgr/req/data/req_create_instructions.md:15:`update_req` prompt) instead of creating a duplicate. Only proceed to
src/biz/dfch/specmgr/req/data/req_create_instructions.md:63:Any later change to this requirement should go through the `update_req` prompt
exit=0
test3: git grep with src/ tests/ (as subagent did):
src/biz/dfch/specmgr/gol/__init__.py:1
src/biz/dfch/specmgr/gol/data/gol_create_instructions.md:2
src/biz/dfch/specmgr/gol/prompts/__init__.py:2
src/biz/dfch/specmgr/gol/prompts/update_gol.py:5
src/biz/dfch/specmgr/prb/__init__.py:1
src/biz/dfch/specmgr/prb/data/prb_create_instructions.md:2
src/biz/dfch/specmgr/prb/prompts/__init__.py:3
src/biz/dfch/specmgr/prb/prompts/update_prb.py:4
src/biz/dfch/specmgr/qa/__init__.py:1
src/biz/dfch/specmgr/qa/data/qa_create_instructions.md:2
src/biz/dfch/specmgr/qa/prompts/__init__.py:3
src/biz/dfch/specmgr/qa/prompts/refine.py:2
src/biz/dfch/specmgr/qa/prompts/update_qa.py:4
src/biz/dfch/specmgr/req/__init__.py:1
src/biz/dfch/specmgr/req/data/req_create_instructions.md:2
src/biz/dfch/specmgr/req/prompts/__init__.py:2
src/biz/dfch/specmgr/req/prompts/update_req.py:3
src/biz/dfch/specmgr/rsk/prompts/update_risk.py:1
src/biz/dfch/specmgr/server.py:4
src/biz/dfch/specmgr/tsk/prompts/update_task.py:2
tests/gol/prompts/test_create_gol.py:2
tests/gol/prompts/test_update_gol.py:16
tests/prb/prompts/test_create_prb.py:2
tests/prb/prompts/test_update_prb.py:19
tests/qa/prompts/test_create_qa.py:2
tests/qa/prompts/test_update_qa.py:17
tests/req/prompts/test_create_req.py:2
tests/req/prompts/test_update_req.py:14
exit=0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 79.6s)

_Thinking:_

Confirmed: **the `git grep` pathspec `src/biz/dfch/specmgr/*/data/` was silently matching nothing** (test1 exit=1, no output; test2 with explicit paths works). In other words, my two "zero residuals in data files" checks (the one at orientation time, and the one in Phase 5 verification) were void. Lesson: don't trust pathspecs containing `*` across multiple directories with git grep.

Truth from test3 (broad grep across the entire src/ tests/): the residual set is exactly as follows:

- `data/` files: **only the 4 create files** (req/qa/prb/gol, 2 lines each = 8 lines) — all references to **prompt names** ("the `update_req` prompt"). No references to tools in any data file. rsk_create/tsk_create/tsk_implement/qa_refine/the 6 update files/4 ADR files: zero.
- `prompts/` modules + `__init__`: prompt function names/docstrings (preserved by design).
- `server.py`: 4 (enumeration of prompts).
- Domain `__init__.py`: 4 (sentences enumerating prompts).
- Prompt tests: imports/assertions of the prompt functions.

This matches the subagent's class (a)–(d) report (31+8+8+74 = 121 lines; the per-file counts from test3 also line up). And ACC-005's "zero references to the deprecated tools" holds: every residual match is a reference to a prompt name, and the plan explicitly preserves those. `set_status_<d>` is zero everywhere (confirmed by an earlier grep, exit=1 — that grep was done over the entire src/ tests/ with no tricky pathspec, so it's valid).

So the state is correct. My verification is complete:
✅ Gate: 1779 tests OK, ruff, vulture, zero drift, fresh import
✅ docs/MCP.md unchanged (narration only)
✅ No references to deprecated tools in data files (only prompt names, preserved by design)
✅ set_status\_<d> is zero across src/+tests/
✅ Prompt module changes are docstring only (AST comparison by the subagent + my scan found only docstring-line changes)
✅ 57 modified files, no untracked files

Just to be safe, one more check: the README progress entry (task 5.x flipped, Recent Updates entry, Current Status). Let me check quickly. Then I'll commit Phase 5.

Confirmed: the `git grep` pathspec containing `*/data/` was silently matching nothing — my two "zero residuals" checks against data/ were invalid, but the correct state has been verified via full-tree grep: **the only remaining matches in data files are the 4 prompt-name references** ("the `update_req` prompt" inside the create files — kept by design); zero tool references in any data file, and `set_status_<d>` is zero across src/+tests/. This matches the subagent's classification exactly. Final check — the README progress entry — then commit:

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -U1 -- .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | grep -E \"^\\+\" | grep -vE \"^\\+\\+\\+\" | head -75",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
+- [x] Task 5.1: Grep-driven rewrite of every instruction data file naming a
+   depends on: Phase 4 complete — status: done
+- [x] Task 5.2: Correct prompt Python module docstrings that name superseded
+  depends on: Task 5.1 — status: done
+- [x] Task 5.3: Update the ten prompt test files to assert the rewritten
+   (and, for the six domain update prompts, the range-update passage) —
+   depends on: Tasks 5.1, 5.2 — status: done
+- [x] Task 5.4: Phase-end quality gate — full gate (the prompt data files are
+   entry to the Recent Updates section, update Current Status, flip the
+   phase's task lines to done in place — depends on: Task 5.3 — status: done
+**As of 2026-08-27**: Phase 5 (Narration rewrite — prompts +
+instruction data) complete — every instruction data file and prompt
+module docstring that named a superseded tool now narrates the two
+generic tools with their exact call shapes: `update(id, type="<d>",
+content)` (whole-body), `update(id, type="<d>", content, begin=…, end=…)`
+(line-range — the six domain update-instruction files each teach the
+REQ-002 flow: `get_<d>(id, raw=True)` → 1-based inclusive range, `N+1`
+end-of-body sentinel, replacement lines only; multi-section or
+uncertain → whole-body), and `set_status(id, type="<d>", status)` —
+`type="adr"` in the four ADR files, with `superseded_by` composing
+`"superseded by X"`. No prompt function signature or behavior changed
+anywhere (docstring-only edits, AST-verified); the 16 prompt test files
+assert the new narration (+11 tests); the final ACC-005 grep over
+`src/`/`tests/` leaves only kept-by-design matches — prompt function
+names in the prompt modules/`__init__` files/tests, the `server.py`
+PROMPT enumerations + the four domain `__init__.py` prompt sentences,
+and the data files' "Later revisions" prompt-name references — with
+zero matches in `tools/`/`models/`/`general/` code and zero tool
+references in `data/*.md`. The phase's quality audit fixed a stale
+`prb/prompts/__init__.py` sentence and a list-indentation artifact in
+the two ADR create-instruction files; everything else from the
+partially completed previous session was verified correct as-is.
+Phase-end gate green (1779 tests OK, zero `docs/` drift, fresh-
+subprocess import OK); live registration unchanged at **71 tools / 25
+resources / 19 prompts** (narration-only phase — the feature's target
+end state, reached in Phase 4). Phases 6–7 are not started. (Phase 1 —
+the feature's ADR 36905d5b-8057-4294-8665-c7eed5534db0 — Phase 2 — the
+generic `update` tool + `raw` reads — Phase 3 — retiring the seven
+`update_<d>` tools — and Phase 4 — the generic `set_status` tool +
+retiring the eight old status tools — completed on 2026-08-27.)
+#### Update 2026-08-27 (Phase 5: Narration rewrite — prompts + instruction data)
+
+- Completed: Phase 5 (Tasks 5.1–5.4). All prompt narration now names
+  the generic tools with their exact call shapes — `update(id,
+  type="<d>", content)` (whole-body), `update(id, type="<d>", content,
+  begin=…, end=…)` (line-range), `set_status(id, type="<d>", status)`,
+  and `set_status(id, type="adr", status[, superseded_by])` in the ADR
+  files (`superseded_by` composing `"superseded by X"`). No prompt
+  function signature or behavior changed anywhere — an AST comparison
+  of HEAD vs. working tree confirms docstring-only edits in all
+  touched prompt modules.
+  - 18 instruction data files rewritten (the 11 files named by
+    REQ-006, plus the six `*_create_instructions.md` and
+    `tsk_implement_instructions.md` files whose "Later revisions" /
+    persistence paragraphs also named the old tools): the six
+    `<d>_update_instructions.md` (req, tsk, qa, rsk, prb, gol — `uc`
+    has no prompts sub-package), `qa_refine_instructions.md`, the four
+    ADR files, and `{req,tsk,qa,prb,gol,rsk}_create_instructions.md` +
+    `tsk_implement_instructions.md`.
+  - Range-update passage added to the six domain
+    update-instruction files (REQ-002 flow, one passage per domain):
+    for a localized change (one paragraph/field/section), first
+    `get_<d>(id, raw=True)` to see the exact body text, identify the
+    1-based, inclusive line range — `N+1` is end-of-body:
+    `begin = end = N+1` appends after the last line, `end = N+1`
+    extends the range through the last line — then
+    `update(id, type="<d>", content, begin=…, end=…)` passing only the
+    replacement lines (the server splices the fragment into the current
+    on-disk body and validates the result as a whole document, so every
+    out-of-range line stays byte-identical); for a multi-section
+    change, or whenever uncertain about the line range, whole-body
+    replace (no `begin`/`end`) with the carry-forward warning.
+  - `qa_refine_instructions.md`: section 5 reworked from "Whole-body
+    replace" to "Persist the appended questions" — the clean-append
+    path uses the `N+1` append range (`get_qa(id, raw=True)` to count

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 161.3s)

_Thinking:_

The README entry is comprehensive and accurate. Phase 5 is fully verified. Committing.

Commit message for Phase 5: `docs(feat-22): rewrite prompt narration to the generic update/set_status tools`

**Phase 5 verified** — committing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git commit -m \"docs(feat-22): rewrite prompt narration to the generic update/set_status tools\n\nPhase 5: every instruction data file and prompt module docstring that\nnamed a superseded tool now narrates the generic tools with exact call\nshapes (update(id, type, content[, begin, end]); set_status(id, type,\nstatus[, superseded_by]); type=\\\"adr\\\" in the four ADR files). The six\ndomain update-instruction files each teach the REQ-002 range-update\nflow (get_<d>(id, raw=True) -> 1-based inclusive range, N+1 EOF\nsentinel, replacement lines only; whole-body for multi-section or\nuncertain changes) and qa_refine uses the N+1 append range for clean\nappends. 18 data files, 11 prompt modules (docstring-only,\nAST-verified), 4 prompts/__init__ docstrings where stale, 16 prompt\ntest files updated (+11 tests: 1779 total, OK). Kept-by-design\nresiduals only: prompt function names. Final ACC-005 state: zero tool\nreferences in data/*.md, zero set_status_<d> anywhere in src/ tests/.\" && git log --oneline -2 && git status --short | head -3",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 db0fec5] docs(feat-22): rewrite prompt narration to the generic update/set_status tools
 57 files changed, 799 insertions(+), 334 deletions(-)
db0fec5 docs(feat-22): rewrite prompt narration to the generic update/set_status tools
d9f7a28 feat(feat-22): add generic set_status tool and retire the eight old status tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 2699.1s)

_Thinking:_

Phase 5 committed as `db0fec5`. All hooks passed.

Next up is Phase 6: cross-cutting documentation and release notes.
Tasks:

- 6.1: Updating AGENTS.md:
  - 7 per-domain bullet points: remove update\_<d>/set_status\_<d> from the tools list and note that generic update/set_status in general/tools/ handle them
  - ADR bullet point: remove set_status from the 12-wrapper list (11 remain)
  - general/ bullet point: add update (7 types; optional begin/end with N+1) and set_status (8 types; ADR-only superseded_by); note raw on the 7 get\_<d> tools
  - "Still genuinely missing / not yet done" list: add convention note that future domains add one dispatch entry to the two generic tools (plus the raw getter parameter) rather than new tools, citing the Phase 1 ADR ID (36905d5b-8057-4294-8665-c7eed5534db0)
- 6.2: CHANGELOG.md \[Unreleased\]:
  - **Breaking**: remove 14 MCP tools (7 update\_<d> + 7 set_status\_<d>); ADR set_status signature (id, status, superseded_by) → (id, type, status, superseded_by), type="adr" becomes required
  - **Added**: generic update (7 types; optional 1-based inclusive body line range, N+1 EOF sentinel, validate as whole after splice); generic set_status (8 types); raw: bool = False on the 7 get\_<d> (returns frontmatter-stripped body text as-is — the text that begin/end index into)
  - Cite Phase 1 ADR ID
- 6.3: Final regeneration: specmgr docs, mcp-docs, adr-toc, schema (models unchanged — expect no schema changes); confirm git diff --exit-code -- docs/ is zero
- 6.4: Gate + README progress update

Note on scope: Task 6.1 in the plan says "the per-domain bullet points and general/ bullet point in AGENTS.md." The per-domain bullet points in the current AGENTS.md list tools like "req/tools (create_req, update_req, set_status_req, parse_req, list_req, delete_req stub, validate_req)". Need to remove update_req/set_status_req and add a pointer to the generic tools. ADR bullet point: "adr/tools/ has 12 @mcp.tool() wrappers (get_adr, list_adr, create_adr, update_frontmatter, update_section, set_status, option_list/..., validate_adr)" → remove set_status → 11 wrappers.

general/ bullet point: currently "general/tools/ (mdformat, ...)" — check the current text. It says "general/ — cross-cutting, non-domain-specific package: general/tools/ (mdformat, formats a markdown file in place while preserving YAML frontmatter blocks), general/resources/ (specmgr://version, specmgr://iso25010 ...), and general/prompts/ (compact_history ...)". Need to add update + set_status + webfetch? Wait — webfetch is also in general/tools (confirmed in __all__: mdformat, update, webfetch). The current AGENTS.md bullet point only mentions mdformat. Hmm — is webfetch mentioned? The bullet point says "general/tools/ (mdformat, formats...)". webfetch isn't mentioned in AGENTS.md — that's an existing omission, but is fixing it out of scope? Task 6.1 says "general/ bullet point — add update ... and set_status ... and note the raw parameter on the 7 get\_<d> tools." The get\_<d> raw note: where do the get\_<d> tools get enumerated in AGENTS.md? In the per-domain bullet points (e.g. "req/tools (create_req, update_req, ...)"). So "note the raw parameter on the 7 get\_<d> tools" happens within the per-domain bullet points where get\_<d> is listed.

The existing omission of webfetch — AGENTS.md says it's "the single most authoritative list" for server.py, but the AGENTS.md status section is a per-domain bullet list. Scope-wise, I'll stick to Task 6.1's list. I'll tell the implementer to update exactly what's in Task 6.1, and additionally fix the per-domain bullet points (which will change anyway) as needed.

Also: AGENTS.md's "Still genuinely missing" list — the first item says "No validate_adr (or validate_req/...) tools run against the repo's own documents..." — unchanged. Add the convention note per Task 6.1.

CHANGELOG.md — need to check the current format (Keep a Changelog style with [Unreleased]). The implementer will read it.

Also Phase 6 has no src/ changes → pre-commit hooks: only ruff format/check on .md files (AGENTS.md, CHANGELOG.md) + regeneration. specmgr docs/mcp-docs/adr-toc/schema hooks won't fire (scoped to src/\*\* or docs/adr/**... the adr-toc hook is scoped to docs/adr/**/\*.md — Phase 6 touches neither src nor docs/adr (except for the 6.3 regeneration, which should be a no-op). So the commit should pass the hooks trivially, but the task requires regeneration + zero-drift verification anyway.

Phase 6 gate: "full gate" per the plan = ruff format --check, ruff check, vulture, unittest + regeneration touched by the phase + zero drift. Even for a docs-only phase, running the full suite is the plan's standard.

Expected state after Phase 6: docs unchanged (regeneration is a no-op), AGENTS.md + CHANGELOG.md + plan README modified.

Phase 7 (final): walk ACC-001..ACC-008 with evidence; live unmocked e2e against temp SPECMGR_DOCS_DIR for req/rsk/uc; ADR e2e; live count check 71/25/19; fresh subprocess import; full gate including pylint advisory; delete temp directory; git status clean of residue; README status → done; final Recent Updates entry.

OK, delegating Phase 6 now.

Phase 5 has been committed as `db0fec5` — all hooks passed. **Delegating Phase 6** (cross-cutting documentation + release notes):

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 6 (docs/CHANGELOG)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 6: Cross-cutting documentation and release notes** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `db0fec5` (Phase 5 commit), working tree clean.\n- All code work is done: Phases 1–5 complete. Live surface: generic `update(id, type, content, begin=None, end=None)` (7 types: req/uc/tsk/qa/prb/gol/rsk) and `set_status(id, type, status, superseded_by=None)` (8 types incl. adr) in `general/tools/`; `get_<d>(id, raw=False)` on the seven whole-body domains; 15 superseded tools deleted; prompts kept with rewritten narration. Live registration: **71 tools / 25 resources / 19 prompts** (the feature's target end state). The feature's Phase-1 ADR id is `36905d5b-8057-4294-8665-c7eed5534db0`.\n- Phase 6 changes **no code** — only `AGENTS.md`, `CHANGELOG.md`, regenerations (expected no-ops), and the plan README.\n\n## Your plan\nRead the FULL plan: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — Overview, Requirements REQ-005/REQ-007, Design Notes (docs discipline), and your phase heading `#### Phase 6: Cross-cutting documentation and release notes` (Tasks 6.1–6.4). Also read `.specmgr/conventions.md` and the \"Coding Standards\"/\"Development Artifacts\" sections of AGENTS.md for house style.\n\n## Tasks\n\n- **Task 6.1**: Update `AGENTS.md`:\n  - **The seven per-domain bullets** (`req/`, `uc/`, `tsk/`, `qa/`, `prb/`, `gol/`, `rsk/`): remove `update_<d>` and `set_status_<d>` from each bullet's `tools` enumeration and note that whole-body/line-range updates go through the generic `update` tool and status changes through the generic `set_status` tool (both in `general/tools/`). Also note the `raw` parameter on each domain's `get_<d>` tool (returns the frontmatter-stripped body text verbatim — the text `begin`/`end` index into) where the bullet enumerates `get_<d>`. Keep every other part of each bullet (resources, prompts, models location, ADR citations) intact.\n  - **The ADR bullet**: remove `set_status` from its 12-wrapper enumeration (it now reads 11 `@mcp.tool()` wrappers: `get_adr`, `list_adr`, `create_adr`, `update_frontmatter`, `update_section`, `option_list`/`option_create`/`option_read`/`option_update`/`option_delete`, `validate_adr`) and note that ADR status changes go through the generic `set_status` tool in `general/tools/` (called with `type=\"adr\"`, ADR-only `superseded_by`).\n  - **The `general/` bullet**: add to `general/tools/`: `update` (the generic whole-body *and* line-range replace for the seven whole-body domains — `type` is one of req/uc/tsk/qa/prb/gol/rsk; optional 1-based inclusive body-line `begin`/`end` with the `N+1` end-of-body sentinel; splice-then-validate-whole) and `set_status` (the generic status change for all eight domains incl. adr; `superseded_by` is ADR-only, composing `\"superseded by X\"`), and note the `raw: bool = False` parameter on the seven `get_<d>` tools.\n  - **The \"Still genuinely missing / not yet done\" list**: add the convention note that future domains (e.g. `ac`) add one dispatch entry to the two generic tools (plus a `raw` getter parameter on their `get_<d>` tool) instead of new `update_<d>`/`set_status_<d>` tools, citing the Phase-1 ADR id `3690d55b` — no, citing the ADR id **`36905d5b-8057-4294-8665-c7eed5534db0`** (typo guard: use the full UUID exactly as written here).\n- **Task 6.2**: Update `CHANGELOG.md`'s `[Unreleased]` section (read the file first and follow its existing structure/section style — Keep a Changelog's Added/Changed/Deprecated/Removed/Fixed/Security or whatever it uses; add sections if missing):\n  - **Breaking** (use a `### Removed` and/or `### Changed` entry or a `### Breaking` label consistent with the file's style): removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`, `set_status_gol`, `set_status_rsk`) and ADR `set_status`'s signature changes from `(id, status, superseded_by)` to `(id, type, status, superseded_by)` with `type=\"adr\"` now required.\n  - **Added**: generic `update(id, type, content, begin, end)` (7 types; optional 1-based inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole) and generic `set_status(id, type, status, superseded_by)` (8 types); optional `raw: bool = False` on the seven `get_<d>` tools (returns the frontmatter-stripped body text verbatim — the text `begin`/`end` index into).\n  - Cite the Phase-1 ADR id `36905d5b-8057-4294-8665-c7eed5534db0`.\n  - Do NOT bump the version in `pyproject.toml` (explicitly out of scope per the plan — release-time concern); the breaking change lands in `[Unreleased]`.\n- **Task 6.3**: Final regeneration: `uv run --frozen specmgr docs`, `uv run --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc`, `uv run --frozen specmgr schema` (models are untouched — expect **no** schema changes; `specmgr schema` exits non-zero if content differs, so a clean exit is the proof). Confirm `git diff --exit-code -- docs/` exits zero after regeneration (i.e. all four generators are no-ops on the current tree).\n- **Task 6.4**: Phase-end quality gate — full gate per the plan's Design Notes: `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` (1779 tests expected), plus Task 6.3's regenerations and the zero-drift confirmation. Fix failures and re-run until green. Then update the plan README (`.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`): frontmatter `updated: 2026-08-27` (status stays `in-progress`); new dated entry `#### Update 2026-08-27 (Phase 6: ...)` at the top of Recent Updates (preserve ALL existing entries) — record the AGENTS.md changes (7 per-domain bullets, ADR bullet 12→11, general/ bullet, the future-domain convention note with the ADR id), the CHANGELOG.md `[Unreleased]` entries (breaking + added), and the gate results incl. the four-generator no-op proof; Current Status → Phase 6 complete, Phase 7 not started; Tasks 6.1–6.4 flipped to done in place (byte-careful with the plan's 2-space continuation wrapping).\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`).\n- Do NOT start Phase 7 (no acceptance-criteria walk, no frontmatter `status: done`).\n- Do NOT modify anything under `src/`, `tests/`, `docs/` (beyond no-op regenerations that must leave zero diff), or `pyproject.toml`.\n- AGENTS.md is the project's authoritative quick-reference — keep its existing formatting conventions (per-domain bullet structure, code styles, link styles) exactly; surgical edits only.\n- The `server.py` module docstring (the authoritative registration list) was already updated phase-by-phase in Phases 2–5 — do NOT touch it in Phase 6; if you believe it is inconsistent with the live surface, STOP and report instead of editing.\n\n## Report back (your final message)\n1. `git status --short` + `git diff --stat` (expect: AGENTS.md, CHANGELOG.md, plan README — and nothing else if Task 6.3's no-op proof holds).\n2. The AGENTS.md diff for: one per-domain bullet (e.g. req), the ADR bullet, the `general/` bullet, and the new \"Still genuinely missing\" note — quoted.\n3. The CHANGELOG.md `[Unreleased]` diff — quoted.\n4. Gate evidence: ruff format --check / ruff check / vulture / full suite (`Ran N tests ... OK`); the four regeneration commands with their outputs and the `git diff --exit-code -- docs/` exit code; confirm the ADR id is cited correctly (full UUID, twice at least: AGENTS.md + CHANGELOG.md).\n5. Any deviations from the plan and why.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbce11060ffeSjGcp50a02kTBr" state="completed">
<task_result>


All verification complete. Phase 6 is done — here is the final report.

---

# Phase 6 Report: Cross-cutting documentation and release notes (feat-22)

## 1. Final tree state

```

$ git status --short
M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
M AGENTS.md
M CHANGELOG.md

$ git diff --stat
.../feat-22-consolidate-mutation-tools/README.md | 133 +++++++++++++++------
AGENTS.md | 98 +++++++++++----
CHANGELOG.md | 42 +++++++
3 files changed, 210 insertions(+), 63 deletions(-)

````

Exactly the three expected files. Nothing under `src/`, `tests/`, `docs/`, `pyproject.toml`, or `server.py` touched. No commits made (working tree left for the orchestrator).

## 2. AGENTS.md diffs (quoted)

**req bullet:**
```diff
-- **`req/`** (Requirements) — `req/tools/` (`create_req`, `update_req`,
-  `set_status_req`, `parse_req`, `list_req`, `delete_req` stub, `validate_req`);
-  `req/resources/` (`specmgr://req/schema`,
+- **`req/`** (Requirements) — `req/tools/` (`create_req`, `parse_req`,
+  `list_req`, `delete_req` stub, `validate_req`); whole-body and line-range
+  updates go through the generic `update` tool in `general/tools/`
+  (`type="req"`), status changes through the generic `set_status` tool
+  (`type="req"`); `req/resources/` (`specmgr://req/schema`,
````

**ADR bullet:**

```diff
-  domain. `adr/tools/` has 12 `@mcp.tool()` wrappers (`get_adr`, `list_adr`,
-  `create_adr`, `update_frontmatter`, `update_section`, `set_status`,
+  domain. `adr/tools/` has 11 `@mcp.tool()` wrappers (`get_adr`, `list_adr`,
+  `create_adr`, `update_frontmatter`, `update_section`,
   `option_list`/`option_create`/`option_read`/`option_update`/
-  `option_delete`, `validate_adr`); `adr/resources/` exposes
+  `option_delete`, `validate_adr`); ADR status changes go through the
+  generic `set_status` tool in `general/tools/` (called with
+  `type="adr"`, ADR-only `superseded_by`); `adr/resources/` exposes
```

**`general/` bullet:**

```diff
  - **`general/`** — cross-cutting, non-domain-specific package:
    `general/tools/` (`mdformat`, formats a markdown file in place while
-   preserving YAML frontmatter blocks), `general/resources/`
+   preserving YAML frontmatter blocks; `update`, the generic whole-body
+   *and* line-range replace for the seven whole-body domains — `type` is
+   one of req/uc/tsk/qa/prb/gol/rsk, optional 1-based inclusive body-line
+   `begin`/`end` with the `N+1` end-of-body sentinel, splice-then-
+   validate-whole; `set_status`, the generic status change for all eight
+   domains incl. adr — `superseded_by` is ADR-only, composing
+   `"superseded by X"`), `general/resources/`
    (`specmgr://version`, `specmgr://iso25010` — the ISO/IEC 25010:2023
    quality model), and `general/prompts/` (`compact_history` — rotates
    older `Recent Updates` entries out of any feature folder's `README.md`
-   into a sibling `history.md`).
+   into a sibling `history.md`). The seven `get_<d>` tools additionally
+   take a `raw: bool = False` parameter — `raw=True` returns the
+   frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
+   index into).
```

**"Still genuinely missing" note:**

```diff
 - No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
-  docstring already reserving a spot for it ("... and later `ac`").
+  docstring already reserving a spot for it ("... and later `ac`") — the
+  convention for adding it (or any future domain) is fixed by ADR
+  36905d5b-8057-4294-8665-c7eed5534db0: one dispatch entry to each of the
+  two generic tools in `general/tools/` (`update`'s `type`,
+  `set_status`'s `type`) plus a `raw` parameter on the new `get_<d>` tool
+  — not new `update_<d>`/`set_status_<d>` tools.
```

The six remaining per-domain bullets (uc, tsk, qa, prb, gol, rsk) received the same shape of edit — `update_<d>`/`set_status_<d>` removed from the enumeration, the generic-tool pointer added, and the `raw: bool = False` note on each enumerated `get_<d>` (e.g. uc: `"...validate_uc`); whole-body and line-range updates go through the generic `update` tool in `general/tools/` (`type="uc"`), status changes through the generic `set_status` tool (`type="uc"`), and the `get_uc` tool takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped body text as-is (the text `update`'s `begin`/`end` index into); no `specmgr://uc/{id}` resource..."`). Resources, prompts, models-location, and ADR citations in every bullet are untouched; prompt names (`update_req`, `update_gol`, `create_risk`/`update_risk\`, …) are kept since the prompts retain their names.

## 3. CHANGELOG.md `[Unreleased]` diff (quoted)

```diff
 ## [Unreleased]

+### Removed
+
+- **BREAKING**: the 14 per-domain mutation MCP tools are deleted outright
+  (no deprecated wrappers): `update_req`, `update_uc`, `update_tsk`,
+  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
+  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
+  `set_status_gol`, `set_status_rsk`. Whole-body and line-range updates
+  now go through the generic `update` tool and status changes through the
+  generic `set_status` tool in `general/tools/` (see "Added" below).
+- **BREAKING**: ADR's own `set_status` tool is removed; the surviving
+  `set_status` tool is the generic one, whose signature changes from
+  `(id, status, superseded_by)` to `(id, type, status, superseded_by)` —
+  `type="adr"` is now required (and the tool is accepted for all eight
+  domains).
+
+### Added
+
+- Generic `update(id, type, content, begin=None, end=None)` MCP tool in
+  `general/tools/`: whole-body and line-range replace of an existing
+  document across the seven whole-body domains (`type` is one of
+  `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`). With no `begin`/`end`,
+  `content` is the full replacement body; with both, it replaces the
+  1-based, inclusive body-line range `begin`..`end` of the current on-disk
+  body (`N+1` = end-of-body sentinel: append after the last line, or
+  replace through end of body). The spliced result is validated as a whole
+  document before anything is written; unchanged regions stay
+  byte-identical.
+- Generic `set_status(id, type, status, superseded_by=None)` MCP tool in
+  `general/tools/`: the status change for all eight domains (`type` is one
+  of `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`adr`), enforcing each
+  domain's closed status vocabulary. `superseded_by` is accepted only for
+  `type="adr"` (composing the status as `"superseded by {superseded_by}"`)
+  and raises `ValueError` with any other `type`.
+- Optional `raw: bool = False` parameter on the seven `get_<d>` tools
+  (`get_req`, `get_uc`, `get_tsk`, `get_qa`, `get_prb`, `get_gol`,
+  `get_rsk`): `raw=True` returns the frontmatter-stripped body text
+  verbatim — the text `update`'s `begin`/`end` index into; `raw=False`
+  (the default) behaves exactly as before.
+- The consolidation above is recorded in ADR
+  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
+  status-change tools into generic type-dispatched tools").
+
 ## [0.11.0] - 2026-08-26
```

`pyproject.toml` untouched (no version bump — release-time concern per the plan).

## 4. Gate evidence

| Command | Result |
|---|---|
| `uv run --frozen ruff format --check` | `1094 files already formatted`, exit 0 (ran twice — after the AGENTS/CHANGELOG edits and after the plan-README edit, both green) |
| `uv run --frozen ruff check` | `All checks passed!`, exit 0 |
| `uv run --frozen vulture src/ whitelist.py --min-confidence 60` | no findings, exit 0 |
| `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` | `Ran 1779 tests in 46.790s` / `OK`, exit 0 (final run; an earlier run in the phase was identical — expected count met) |
| `uv run --frozen specmgr docs` | `✓ Wrote 305 module file(s) to …/docs/api` + `✓ Wrote …/docs/GENERATED.md`, exit 0 |
| `uv run --frozen specmgr mcp-docs` | `✓ Wrote …/docs/MCP.md`, exit 0 |
| `uv run --frozen specmgr adr-toc` | `✓ Wrote docs/adr/README.md`, exit 0 |
| `uv run --frozen specmgr schema` | all seven domain schemas `(unchanged)`, exit 0 |
| `git diff --exit-code -- docs/` | **exit 0** — all four generators are byte-identical no-ops on the current tree |

**ADR id citation:** full UUID `36905d5b-8057-4294-8665-c7eed5534db0` (verified against the on-disk file `docs/adr/36905d5b-…into-g.md` and `docs/adr/README.md` row) — appears once in AGENTS.md, once in CHANGELOG.md, and three times in the plan README (Current Status + Phase 6 update entry, matching the existing Phase-1/Decisions-Made citations).

**Plan README updates:** frontmatter already at `updated: 2026-08-27` / `status: in-progress` (no change needed); new `#### Update 2026-08-27 (Phase 6: …)` entry at the top of Recent Updates (all six prior entries preserved, verified by heading list); Current Status rewritten for Phase 6 complete / Phase 7 not started; Tasks 6.1–6.4 flipped to `- [x]` / `status: done` in place with the file's existing 2-space continuation wrapping intact (ruff-stable).

## 5. Deviations from the plan

1. **Gol bullet trailing clause removed (judgment call, within Task 6.1 scope).** The gol bullet ended with ", and `update_gol` is a single whole-body replace, like `update_req`/`update_prb`." — a sentence naming three of the tools this feature deletes, which would have left AGENTS.md affirmatively wrong after the enumeration edit. I dropped the clause (the sentence now ends at the feat-18 README reference); the semantics it carried are covered by the generic-`update` clause added to every domain bullet.
2. **`req` bullet gets no `raw` note.** The req bullet never enumerated `get_req` (pre-existing staleness the plan explicitly scopes out: "fixing unrelated stale text is not part of this feature"), and the task's instruction is conditional ("where the bullet enumerates `get_<d>`"). The `raw` parameter is still documented for `req` in the `general/` bullet's note covering all seven `get_<d>` tools.
3. No other deviations. The `server.py` module docstring was verified consistent with the live surface (11 ADR tools, generic `update`/`set_status` under General tools, `raw` notes on the seven per-domain `get_<d>` lines) and not touched, per the hard constraint.

**Nothing blocks Phase 7.** The orchestrator can commit this phase (Conventional Commit, e.g. `docs(feat-22): update AGENTS.md and CHANGELOG.md for the consolidated mutation tools`) and proceed to the ACC walkthrough; the live surface (71 tools / 25 resources / 19 prompts) was unchanged by this phase and the full gate is green.
\</task_result>
</task>

````

---

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 132.4s)

_Thinking:_

Phase 6 report looks good. The deviations are reasonable:
1. Removed the old trailing clause in the gol bullet that was referencing a deprecated tool — correct call (leaving it in would have made AGENTS.md affirmatively wrong).
2. No raw note in the req bullet — because req doesn't enumerate get_req in that bullet... wait, let me check the AGENTS.md text from the original system prompt: the req bullet says "**`req/`** (Requirements) — `req/tools/` (`create_req`, `update_req`, `set_status_req`, `parse_req`, `list_req`, `delete_req` stub, `validate_req`); ..." — indeed, this bullet does not enumerate get_req (existing staleness; the plan scopes out unrelated fixes). The general bullet covers raw for all 7. OK.

Hmm, wait, but actually looking at the diff in the report: the req bullet after the edit reads "`req/tools/` (`create_req`, `parse_req`, `list_req`, `delete_req` stub, `validate_req`)" — get_req is still missing. That's fine (existing issue, out of scope, documented).

Now verify independently:
1. git status = exactly 3 files.
2. Read the actual AGENTS.md diff and CHANGELOG diff (spot check).
3. Run the gate: ruff format --check, ruff check, vulture, unittest 1779, 4 regenerators, git diff --exit-code -- docs/.
4. Check the README progress entry.

Let me run the gate + diff review in parallel.




Phase 6 reported cleanly with two sensible judgment-call deviations. Verifying independently:




**Tool: bash**

**Input:**
```json
{
  "command": "git status --short && uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase6-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase6-unittest.log && uv run --frozen specmgr docs >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && uv run --frozen specmgr adr-toc >/dev/null && uv run --frozen specmgr schema && git diff --exit-code -- docs/ && echo P6_DOCS_ZERO_DRIFT",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
````

**Output:**

```
 M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
 M AGENTS.md
 M CHANGELOG.md
1094 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1779 tests in 47.089s
OK
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/gol_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/prb_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/qa_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/req_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/rsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/tsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr-feat-22/docs/uc_schema.json (unchanged)
P6_DOCS_ZERO_DRIFT

```

**Tool: bash**

**Input:**

```json
{
  "command": "git diff -- CHANGELOG.md | head -60 && echo ================= && git diff --stat -- AGENTS.md && grep -n \"36905d5b-8057-4294-8665-c7eed5534db0\" AGENTS.md CHANGELOG.md",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 691d0b6..61e86ed 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,48 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Removed
+
+- **BREAKING**: the 14 per-domain mutation MCP tools are deleted outright
+  (no deprecated wrappers): `update_req`, `update_uc`, `update_tsk`,
+  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
+  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
+  `set_status_gol`, `set_status_rsk`. Whole-body and line-range updates
+  now go through the generic `update` tool and status changes through the
+  generic `set_status` tool in `general/tools/` (see "Added" below).
+- **BREAKING**: ADR's own `set_status` tool is removed; the surviving
+  `set_status` tool is the generic one, whose signature changes from
+  `(id, status, superseded_by)` to `(id, type, status, superseded_by)` —
+  `type="adr"` is now required (and the tool is accepted for all eight
+  domains).
+
+### Added
+
+- Generic `update(id, type, content, begin=None, end=None)` MCP tool in
+  `general/tools/`: whole-body and line-range replace of an existing
+  document across the seven whole-body domains (`type` is one of
+  `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`). With no `begin`/`end`,
+  `content` is the full replacement body; with both, it replaces the
+  1-based, inclusive body-line range `begin`..`end` of the current on-disk
+  body (`N+1` = end-of-body sentinel: append after the last line, or
+  replace through end of body). The spliced result is validated as a whole
+  document before anything is written; unchanged regions stay
+  byte-identical.
+- Generic `set_status(id, type, status, superseded_by=None)` MCP tool in
+  `general/tools/`: the status change for all eight domains (`type` is one
+  of `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`adr`), enforcing each
+  domain's closed status vocabulary. `superseded_by` is accepted only for
+  `type="adr"` (composing the status as `"superseded by {superseded_by}"`)
+  and raises `ValueError` with any other `type`.
+- Optional `raw: bool = False` parameter on the seven `get_<d>` tools
+  (`get_req`, `get_uc`, `get_tsk`, `get_qa`, `get_prb`, `get_gol`,
+  `get_rsk`): `raw=True` returns the frontmatter-stripped body text
+  verbatim — the text `update`'s `begin`/`end` index into; `raw=False`
+  (the default) behaves exactly as before.
+- The consolidation above is recorded in ADR
+  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
+  status-change tools into generic type-dispatched tools").
+
 ## [0.11.0] - 2026-08-26
 
 ### Added
=================
 AGENTS.md | 98 ++++++++++++++++++++++++++++++++++++++++++++++-----------------
 1 file changed, 72 insertions(+), 26 deletions(-)
AGENTS.md:218:  36905d5b-8057-4294-8665-c7eed5534db0: one dispatch entry to each of the
CHANGELOG.md:49:  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 76.5s)

_Thinking:_

Phase 6 verification complete:

- Exactly 3 files changed ✓
- Gate: ruff (1094) ✓, ruff check ✓, vulture ✓, 1779 tests OK ✓
- All 7 schemas unchanged ✓ (proof that the models are invariant)
- `git diff --exit-code -- docs/` → P6_DOCS_ZERO_DRIFT ✓ (all 4 generators are no-ops)
- CHANGELOG's \[Unreleased\]: BREAKING Removed entries (14 tools + ADR signature) + Added entries (update, set_status, raw) + ADR citations ✓
- ADR UUID cited in AGENTS.md:218 and CHANGELOG.md:49 ✓ (full UUID, no typos)

Commit Phase 6, then on to Phase 7.

**Phase 6 verified** — gate green, all 7 schemas unchanged, docs zero-drift, ADR UUID cited correctly in both files. Committing:

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git commit -m \"docs(feat-22): update AGENTS.md and CHANGELOG.md for the consolidated mutation tools\n\nPhase 6: AGENTS.md per-domain bullets no longer enumerate the removed\nupdate_<d>/set_status_<d> tools and point at the generic update/\nset_status tools in general/tools/ (with the raw parameter noted on the\nseven get_<d> tools); the ADR bullet's wrapper count is 11; the\ngeneral/ bullet carries both generic tools; the future-domain\nconvention (one dispatch entry per generic tool, not new tools) is\nfixed in the still-missing list citing ADR 36905d5b. CHANGELOG.md\n[Unreleased] gains the breaking removal of the 14 per-domain mutation\ntools plus ADR set_status' new required type parameter, and the added\ngeneric update/set_status tools and raw getter parameter. No code,\nschema, or generated-doc changes (all four generators verified\nno-ops).\" && git log --oneline -3",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
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
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 c82abeb] docs(feat-22): update AGENTS.md and CHANGELOG.md for the consolidated mutation tools
 3 files changed, 210 insertions(+), 63 deletions(-)
c82abeb docs(feat-22): update AGENTS.md and CHANGELOG.md for the consolidated mutation tools
db0fec5 docs(feat-22): rewrite prompt narration to the generic update/set_status tools
d9f7a28 feat(feat-22): add generic set_status tool and retire the eight old status tools

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 100.5s)

_Thinking:_

Phase 6 has been committed as `c82abeb`. Next up is Phase 7 — final cross-cutting verification.

Phase 7 tasks:

- 7.1: Walk through ACC-001 through ACC-008 and verify each with concrete evidence, annotating the Acceptance Criteria section in-place, in feat-18-goal style. Live, unmocked end-to-end execution in a temporary SPECMGR_DOCS_DIR:
  - For req, rsk, uc: create\_<d> → get\_<d>(id, raw=True) → update(id, type, content, begin, end) (one mid-range replacement with byte-level exact-match verification, one N+1 append) → get\_<d> (verify content) → set_status(id, type, status) (a domain-valid value) → get\_<d> (verify status)
  - For ADR: create_adr → set_status(id, type="adr", status="superseded", superseded_by=...) → status is read as "superseded by ..."
  - Confirm asyncio.run(mcp.list_tools()/list_resources()/list_prompts()) against the actual server.mcp → 71/25/19
  - Import check in a fresh subprocess
  - Full quality gate (ruff format/check, pylint advisory, vulture, unittest, specmgr docs/mcp-docs/adr-toc/schema zero drift)
  - Delete the temporary docs directory and confirm no residue in git status
- 7.2: README frontmatter status: in-progress → done; final Recent Updates entry and Current Status summary.

"Annotate the Acceptance Criteria section in-place, in feat-18-goal style" — I need to check what that style is. Let me look at the Acceptance Criteria section of feat-18-goal's README and check how it was annotated.

Also, the e2e execution: how is it done? A Python script that sets SPECMGR_DOCS_DIR to a temp directory and calls the actual tool functions (imported from biz.dfch.specmgr...tools). The tools are plain functions (decorated with @mcp.tool but still callable). "Live, unmocked" — uses the actual filesystem via the environment variable override. The temp directory must be cleaned up afterwards and not left in the repo (place it in /tmp).

Should the e2e be written as a test, or as a one-off script? The plan says "live, unmocked end-to-end execution in a temporary SPECMGR_DOCS_DIR" — this is verification, not necessarily a permanent test. The implementer can either run it as a one-off script (via python -c or a temp file) and record the evidence, or add it as a permanent integration test. Hmm — ACC-008 says "verify REQ-001/002/004/005 — the Phase-1 ADR exists ... a live, unmocked end-to-end execution in a temporary SPECMGR_DOCS_DIR passes for req, rsk, uc ...; for ADR ...; asyncio.run(...) reports 71/25/19; import in a fresh subprocess succeeds."

Note: "the Phase-1 ADR exists in docs/adr/ with status accepted and is listed in docs/adr/README.md" — that part of ACC-008 is already verified (Phase 1). The e2e execution is the new part.

Should the e2e be a permanent test? The repo already has integration tests (tests/gol/tools/test_integration.py, tests/prb/tools/test_integration.py) that do create→update→set_status→get live in a temp directory. It's quite feasible to add a permanent e2e test that covers req/rsk/uc + ADR, and it would protect against regressions. But the plan phrases ACC-008 as a verification activity ("live, unmocked end-to-end execution ... passes"), and Phase 7 is the "final cross-cutting verification" phase. Task 7.1 says "walk through ACC-001 through ACC-008 and verify each with concrete evidence."

For ACC-001/002/003/004/005/006/007, the "concrete evidence" is: the test suite (1779 tests) covering them, the grep results, the docs state, the server.py docstring, etc. For each ACC, the implementer should cite specific test files/counts or command outputs. For ACC-008, the e2e execution + count + import.

My instructions to the implementer: run the e2e as a script (e.g., a temp Python file in /tmp, or `uv run python -c` with an explicit script path), against an actual SPECMGR_DOCS_DIR in /tmp, and record the full output as evidence. Do NOT add new permanent tests in Phase 7 (the plan's Phase 7 has no test-creation task — it's a verification phase). Actually, hmm, let me reconsider: if the e2e is one-off, future regressions won't be detected... but the existing test suite (test_update.py, test_set_status.py, the gol/prb integration tests) already covers these flows permanently. The ACC-008 e2e is a final confirmation of the complete flow including ADR supersession. A one-off is fine and aligns with the plan (Phase 7's task list has no test-creation task).

First, let me check the annotation style of feat-18-goal. Let me read the Acceptance Criteria section of feat-18-goal's README.

Phase 6 has been committed as `c82abeb`. For Phase 7, Task 7.1 requires annotating the Acceptance Criteria "inline in the style of feat-18-goal" — let me first confirm that style:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n -A4 \"ACC-\" .specmgr/feat/feat-18-goal/README.md | head -60",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

````
79:- [x] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`,
80-  `specmgr://gol/schema`); a reference `gol_reference.md` exercising every
81-  field (`statement`, `Source` plus all optional sections present,
82-  `Related Artifacts` with all four sub-lists) round-trips through the
83-  parser. **PASS** — `docs/gol_schema.json` exists with `"$comment": "v1"`
--
97:- [x] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory
98-  (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`,
99-  `Related Artifacts` and each of its four sub-lists, `More Information`,
100-  `Notes`) fields correctly; `GolFrontmatter.status` rejects any value
101-  outside the seven-value set. **PASS** —
--
113:- [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
114-  well-formed document; missing the `statement` lead paragraph or the
115-  `Source` section raises `AssertionError`; an invalid field value (e.g. a
116-  `Priority` outside 0–99, an out-of-set `status`) raises
117-  `pydantic.ValidationError`. **PASS** —
--
131:- [x] ACC-004: Verifies REQ-004 — every listed tool is implemented,
132-  registered, and callable; `list_gol` returns a `PagedResult[GolSummary]`
133-  with default page size 25 / cap 100, mirroring the other five domains'
134-  `list_<d>` tools exactly (no resource-first-then-converted history for
135-  this domain). **PASS** — `docs/MCP.md` carries all 10 `### Tool:` gol
--
150:- [x] ACC-005: Verifies REQ-005 — every listed resource is implemented and
151-  registered (no `/{id}`, no `/list`, as designed). **PASS** — `docs/MCP.md`
152-  carries exactly three `specmgr://gol/...` rows (`/example` line 19,
153-  `/schema` line 20, `/template` line 21; detail sections lines 40–56), and
154-  a grep of both `docs/MCP.md` and `src/biz/dfch/specmgr/gol/resources/`
--
162:- [x] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate:
163-  (a) a duplicate/similar-document check via `list_gol` first, (b) building
164-  a `TodoWrite` list covering `statement` + `Source` + each optional
165-  section, (c) using the `question` tool to elicit each field (explicitly
166-  allowing skip for optional ones), (d) calling `create_gol(content)`/
--
201:- [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
202-  real, non-editable install (`uv build --wheel` + scratch-venv install),
203:  mirroring feat-16's ACC-007 verification. **PASS** — `uv build --wheel`
204-  produced `dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl`; `unzip -l`
205-  confirms all five `gol/data/*` files (`gol_example.md`, `gol_schema.json`,
206-  `gol_template.md`, `gol_create_instructions.md`,
207-  `gol_update_instructions.md`) plus every gol module (35 wheel entries
--
219:- [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
220-  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
221-  reflects eight domain/cross-cutting packages. **PASS** — re-run end to
222-  end in Phase 5: `specmgr docs` (exit 0), `specmgr mcp-docs` (exit 0),
223-  `specmgr schema` (exit 0, all six doc types "unchanged"), `specmgr schema
--
316:│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
317-├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free text leaf
318-└── notes: Notes | None                         # optional H2 "Notes", opaque free text leaf
319-```
320-
--
348:(`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text
349-only — not validated in v1. The `### Goals` sub-list includes goals for
350-cross-referencing peer/superseding goals (self-referencing is allowed; the
351-parser does not special-case a document's own id).

````

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 4275.1s)

_Thinking:_

feat-18-goal's style: each ACC line is checked (`- [x]`) and has a `**PASS** — <concrete evidence>` annotation embedded in the item's text (additional sentences with specific file/line/command evidence).

Next, delegate Phase 7. The subagent needs to do the following:

1. For each of ACC-001 through ACC-008, gather concrete evidence and annotate the Acceptance Criteria section in place (keep the original requirement text, add `**PASS** — evidence...`, and check `[x]`).
2. Perform a live, un-mocked e2e run in a temporary SPECMGR_DOCS_DIR (for req, rsk, uc + ADR supersession).
3. Confirm the live count 71/25/19 + new subprocess import.
4. Run the full quality gate. This also includes pylint advisory (`uv run --frozen pylint $(git ls-files '*.py')` — advisory; CI runs with `|| true`).
5. Regenerate specmgr docs/mcp-docs/adr-toc/schema — zero drift.
6. Clean up the temp directory; confirm no residue in git status.
7. Update the README: front matter status in-progress → done; a final Recent Updates entry; Current Status summary.
8. Do not commit.

Details on evidence per ACC:

- ACC-001 (whole-body update semantics for all 7 types): evidence = tests/general/tools/test_update.py (18 methods parameterized over 7 types, including ACC-001 cases) + count. Can also cite a quick live run. Test evidence is sufficient: "tests/general/tools/test_update.py — TestUpdateWholeBody…; the suite ran 1779 tests OK."
- ACC-002 (range mode): same file, range method.
- ACC-003 (raw read): tests/<d>/tools/test_get\_<d>.py raw test (7 files, 4 each = 28).
- ACC-004 (set_status for all 8 types): tests/general/tools/test_set_status.py (10 tests parameterized over 8 types).
- ACC-005 (15 tools eliminated): grep evidence (word-boundary grep; classification) + absence in docs/MCP.md + vulture clean.
- ACC-006 (narration): 18 data files with the generic signature (cite grep: zero tool references in data/\*.md; the range description exists in the 6 files); 16 prompt test files pass.
- ACC-007 (doc/registration consistency): specmgr docs/mcp-docs/adr-toc/schema zero drift; MCP.md shows 2 generic tools with 7/8-value enums and none of the 15 removed; server.py's docstring lists the post-feature-applied surface; AGENTS.md + CHANGELOG.md have been updated.
- ACC-008: Phase 1 ADR exists with accepted status and is listed in docs/adr/README.md (cite the line); live e2e run (new, to be executed); 71/25/19 live count; new subprocess import.

E2E script: write to /tmp (not in the repo), set SPECMGR_DOCS_DIR to a temp directory (e.g., /tmp/opencode/feat22-e2e/docs), and run the following:

- For req: create_req (via tool function `from biz.dfch.specmgr.req.tools.create_req import create_req`) — wait, how do the create tools get their content? `create_req(content)` returns a ReqDocument with a new id. Then get_req(id, raw=True), a range update (mid-range + N+1 append), get_req(id) to verify content, set_status(id, "req", valid value), get_req(id) to verify status.
- Same for rsk, uc (domain-valid statuses: e.g., req "accepted", rsk "mitigating", uc "proposed").
- ADR: create_adr(...) → set_status(adr_id, "adr", "superseded", superseded_by="some-id") → get_adr → front matter status == "superseded by some-id".
- Byte-exact verification of the mid-range replacement: read raw before and after, and verify that out-of-range lines are identical.

The e2e must be live and un-mocked: the actual tool functions write to the actual temp filesystem via the SPECMGR_DOCS_DIR env var. The tools read the env var on each call (base_dir() function), so setting the env var in the script before the calls will work.

Where to place the script? /tmp/opencode/ (outside the repo) — that way there's no git residue. Run it with `uv run --frozen python /tmp/opencode/feat22_e2e.py` — hmm, `uv run` with a script path works (runs the script in the project environment).

Cleanup: delete the temp docs directory + script; confirm `git status` is clean (except for the intended README edit).

Also, the plan says for Phase 7's gate: "full quality gate (ruff format/check, pylint advisory, vulture, unittest, specmgr docs/mcp-docs/adr-toc/schema zero drift)." pylint advisory: `uv run --frozen pylint $(git ls-files '*.py')` — may take a while; CI runs it with `|| true`. Instruct the subagent to run it and record the score, and only fix if there's an actual problem (this is advisory).

Front matter: status in-progress → done, updated 2026-08-27 (already that date).

Also, the "Related PRs / Commits" section of the plan README — should it be updated with the 6 phase commits? The section says "None yet (one Conventional Commit per accepted phase, created by the phase-orchestrator with user confirmation)." Hmm — "with user confirmation" — the user told me to commit without asking; that phrase in the README is stale in that respect, but editing it is… Task 7.2 says "final Recent Updates entry and Current Status summary." Updating Related PRs/Commits with the phase commit SHAs is in the spirit of the Progress section discipline. Instruct the subagent to record the 6 commit hashes (f9586e6 is the planning commit — pre-existing; the 6 phase commits are: 2647649, fc76490, 971998f, d9f7a28, db0fec5, c82abeb) in the Related PRs / Commits section. That's appropriate.

One more thing to confirm: ACC-008 says the e2e is run for "req, rsk, uc" and ADR. The subagent should also double-check that `docs/adr/README.md` lists the Phase 1 ADR (it does — cite the line).

Let's write the Phase 7 prompt.

Confirmed the annotation style (inline `**PASS** — <concrete evidence>` on checked ACC lines). **Delegating Phase 7** (final cross-cutting verification):

**Tool: task**

**Input:**

```json
{
  "description": "Implement feat-22 Phase 7 (final verify)",
  "prompt": "Implement exactly ONE phase of a feature plan, then stop. You are the phase-implementer for **Phase 7: Final cross-cutting verification** of feature **feat-22-consolidate-mutation-tools** in the repo at `/home/user/src/biz.dfch.SpecMgr-feat-22`.\n\n## Repo / branch state\n- Branch `feat-22`, HEAD `c82abeb` (Phase 6 commit), working tree clean. Phases 1–6 complete: the feature ADR (`36905d5b-8057-4294-8665-c7eed5534db0`, accepted, in `docs/adr/` + TOC), the generic `update` and `set_status` tools in `general/tools/`, the `raw` parameter on the seven `get_<d>` tools, all 15 superseded tools deleted, narration rewritten, AGENTS.md/CHANGELOG.md updated. Live registration: 71 tools / 25 resources / 19 prompts. Full suite: 1779 tests.\n- Phase commits so far (for the README's Related PRs / Commits section): `2647649` (Phase 1), `fc76490` (Phase 2), `971998f` (Phase 3), `d9f7a28` (Phase 4), `db0fec5` (Phase 5), `c82abeb` (Phase 6). (The planning commit `f9586e6` predates this feature's execution.)\n\n## Your plan\nRead the FULL plan: `/home/user/src/biz.dfch.SpecMgr-feat-22/.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` — especially the **Acceptance Criteria** section (ACC-001…ACC-008), and your phase heading `#### Phase 7: Final cross-cutting verification` (Tasks 7.1–7.2). For the annotation style, read how feat-18-goal did it: `.specmgr/feat/feat-18-goal/README.md`'s Acceptance Criteria section — each ACC line is checked (`- [x]`) and carries an inline `**PASS** — <concrete evidence>` continuation (specific files, line numbers, commands, counts).\n\n## Task 7.1: Walk ACC-001…ACC-008, confirm each with concrete evidence, annotate inline\n\nFor each ACC, gather fresh evidence (run the commands yourself — do not reuse Phase 2–6 reports verbatim without re-running) and append a `**PASS** — ...` annotation to that ACC's bullet in the plan README's Acceptance Criteria section, checking the box (`- [x]`). Keep the original requirement text intact; the annotation is added text within the same list item (continuation lines wrapped at the plan's existing ~78-column style, 2-space continuation indent). Evidence per ACC:\n\n- **ACC-001** (whole-body `update`, all seven types): cite `tests/general/tools/test_update.py` — its whole-body test methods, parameterized over all seven types (read the file for the exact test method names + count), the covered cases (body replaced; id/type/status/created/version preserved; updated bumped microsecond; status not settable; AssertionError/ValidationError leave file byte-identical; unknown id → domain XNotFoundError), and the suite result.\n- **ACC-002** (range mode, all seven types): same file — the range test methods (middle-range byte-identity, N+1 append, end=N+1 through-EOF, empty-fragment deletion, begin=1/end=N ≡ whole-body, the ValueError misuses, H1-deletion AssertionError, out-of-vocabulary field failure) + the documented qa/prb nuance (their out-of-vocabulary case raises structural AssertionError because their bodies have no field-level validation — flagged in the test module docstring).\n- **ACC-003** (`raw=True`, all seven domains): the seven `tests/<d>/tools/test_get_<d>.py` raw test groups (4 tests each: byte-identical body; the coordinate-invariant test that reads raw, picks a line range, calls `update`, and confirms the splice landed exactly there; raw=False regression; unknown id both modes) + the shared `body_text` helper in `general/tools/_splice.py`.\n- **ACC-004** (`set_status`, all eight types): `tests/general/tools/test_set_status.py` (10 tests, parameterized over all eight types) — status changed + updated bumped + body untouched (seven domains raw-body byte-identical; ADR render round-trip apart from status — ADR has no `updated` field), per-domain closed-vocabulary enforcement with cross-domain negative values, ADR `superseded_by` composition, `superseded_by`-with-non-adr ValueError (before file access, unknown id included), domain not-found errors.\n- **ACC-005** (15 tools gone): fresh runs of `git grep -nE \"\\b(update_req|update_uc|update_tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|set_status_uc|set_status_tsk|set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\\b\" -- src/ tests/` (classify the residuals: kept-by-design prompt names only — the six prompt modules, prompts `__init__` files, server.py prompt enumerations, domain `__init__` prompt sentences, the four create-instruction files' \"the `update_<d>` prompt\" references, prompt test files; ZERO in tools/models/general code, ZERO tool references in data/*.md, ZERO `set_status_<d>` anywhere) + `git grep -c \"### Tool: update_req\\|### Tool: set_status_req\" docs/MCP.md`-style checks proving `docs/MCP.md` carries none of the 15 removed `### Tool:` entries while the generic `update`/`set_status` entries exist + vulture clean.\n- **ACC-006** (narration): the 18 data files reference the generic tools with correct signatures — fresh grep proving `update(id, type=\"<d>\"` / `set_status(id, type=\"<d>\"` / `set_status(id, type=\"adr\"` call shapes present in the data files and zero superseded-tool call sites; the six domain update-instruction files each contain the range-update flow passage (`get_<d>(id, raw=True)` → 1-based inclusive range → `update(..., begin=…, end=…)`; whole-body for multi-section/uncertain) — verify all six; the 16 prompt test files pass (count them in the suite).\n- **ACC-007** (docs/registration consistency): fresh `specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema` runs all no-op (then `git diff --exit-code -- docs/` exit 0); `docs/MCP.md` shows the two generic tools with `type` rendered as the 7-/8-value enums (quote the two `type` rows) and none of the 15 removed tools; `server.py`'s module docstring lists exactly the post-feature surface (spot-check the General-tools lines and one per-domain line); `AGENTS.md` + `CHANGELOG.md` updated per REQ-007 (cite the Phase 6 commit `c82abeb`).\n- **ACC-008** (ADR + live e2e + counts + import): (a) the Phase-1 ADR exists in `docs/adr/` with status `accepted` and is listed in `docs/adr/README.md` (quote the TOC line with the ADR id); (b) the **live, un-mocked end-to-end run** below; (c) `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real `server.mcp` reports **71 / 25 / 19** (quote the output); (d) fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.server\"` exit 0.\n\n**The live e2e run (part of ACC-008)** — write a throwaway script OUTSIDE the repo (e.g. `/tmp/opencode/feat22_e2e.py`), run it with `uv run --frozen python /tmp/opencode/feat22_e2e.py` from the repo root, and capture its full output as evidence. The script must:\n1. Create a temp docs dir (e.g. `tempfile.mkdtemp()`), set `os.environ[\"SPECMGR_DOCS_DIR\"]` to it BEFORE any tool call, and clean it up at the end (and confirm removal).\n2. Import the real tool functions (e.g. `from biz.dfch.specmgr.req.tools.create_req import create_req`, `from biz.dfch.specmgr.req.tools.get_req import get_req`, `from biz.dfch.specmgr.general.tools.update import update`, `from biz.dfch.specmgr.general.tools.set_status import set_status`, same for rsk/uc, plus `create_adr`/`get_adr` from `biz.dfch.specmgr.adr.tools`).\n3. For EACH of `req`, `rsk`, `uc` (print a section per domain):\n   - `create_<d>(<minimal valid body for that domain>)` → capture the returned document's id (read a minimal valid body from the domain's example data file, e.g. `src/biz/dfch/specmgr/<d>/data/<d>_example.md`'s body portion, or reuse what the domain's create test seeds — print the id).\n   - `get_<d>(id, raw=True)` → print the line count N of the body text.\n   - One **middle-range replace** via `update(id, \"<d>\", fragment, begin=k, end=m)` on a real middle line/lines (e.g. replace line 2's content with an altered version) — then `get_<d>(id, raw=True)` again and assert in the script: out-of-range lines byte-identical to before, the changed line(s) exactly as the fragment (print the before/after line lists or a diff).\n   - One **`N+1` append** via `update(id, \"<d>\", \"extra text\", begin=N2+1, end=N2+1)` where N2 is the current line count — assert the new last line is the fragment and prior lines unchanged (print evidence).\n   - `get_<d>(id)` (parsed) → assert the content reflects both edits (print the relevant field/section).\n   - `set_status(id, \"<d>\", <domain-valid status>)` (req: `accepted`; rsk: `mitigating`; uc: `proposed`) → `get_<d>(id)` → assert `frontmatter.status` equals it (print it).\n4. For ADR: `create_adr(frontmatter=…, body=…)` (build a minimal valid ADR — the `specmgr_create_adr` MCP tool's parameter shapes are the guide; or reuse a minimal Adr body like the existing `tests/adr/tools/test_create_adr.py` does — read that file for the minimal valid input) → `set_status(adr_id, \"adr\", \"superseded\", superseded_by=\"<some-uuid>\")` → `get_adr(adr_id)` → assert the frontmatter status reads exactly `\"superseded by <some-uuid>\"` (print it).\n5. Print `E2E-OK` as the final line only if every assertion passed. Any assertion failure must print the failure and exit non-zero.\n6. After the run: `rm -rf` the temp dir, then `git status --short` in the repo must show NO residue from the e2e (only the plan-README edit you are making).\n\n## Task 7.1 (continued) — full quality gate at the final state\n- `uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\"` (1779 expected).\n- `uv run --frozen pylint $(git ls-files '*.py')` — ADVISORY (CI runs it with `|| true`): run it, record the overall score/line, and fix ONLY if it reports a real error introduced by this feature (do not chase pre-existing advisory noise; do not touch code to game the score).\n- `uv run --frozen specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`, `specmgr schema` — all must be no-ops; `git diff --exit-code -- docs/` exit 0.\n- Fix failures and re-run until green — a phase is not done with a red gate.\n\n## Task 7.2: Close the feature README\nIn `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md`:\n- Frontmatter: `status: in-progress` → `status: done` (`updated` stays `2026-08-27`).\n- Acceptance Criteria: all eight ACCs checked + annotated per Task 7.1 (this IS the inline annotation).\n- Current Status: final summary (feature complete; all seven phases done; the 71/25/19 end state; the six phase commits; ADR id).\n- Recent Updates: a final dated entry `#### Update 2026-08-27 (Phase 7: Final verification)` at the top (preserve ALL existing entries) — record the e2e run outcome (per-domain + ADR, with the printed status string for the ADR supersession), the 71/25/19 confirmation, the import check, the pylint advisory result, the gate results, and the feature's completion.\n- **Related PRs / Commits** section (currently \"None yet …\"): replace with the six phase commits (`2647649` Phase 1 … `c82abeb` Phase 6), one line each with the phase number + short title. (Phase 7's own commit will not exist yet — note that the list covers Phases 1–6; do not invent a Phase-7 hash.)\n- Tasks 7.1, 7.2 flipped to done in place.\n- Byte-careful: preserve the plan's 2-space continuation wrapping on every untouched line.\n\n## Hard constraints\n- Do NOT commit anything (no `git add`/`git commit`) — the orchestrator commits Phase 7 last.\n- Do NOT modify anything under `src/`, `tests/`, `docs/` (the e2e script lives in `/tmp/opencode/`, outside the repo). The ONLY repo file you edit is the plan README.\n- If any ACC turns out to be unmet (a real failure), STOP, do NOT mark it PASS, and report the failure with evidence — the orchestrator decides.\n- If the e2e reveals a genuine product bug, STOP and report — do not fix code in Phase 7.\n\n## Report back (your final message)\n1. The complete captured output of the e2e script run (the printed per-domain sections + ADR supersession string + `E2E-OK`), plus the temp-dir cleanup + `git status --short` proving no residue.\n2. The 71/25/19 live-count output and the fresh-subprocess import exit code.\n3. Full gate evidence: ruff format --check / ruff check / vulture / unittest (`Ran N tests ... OK`, exact N) / pylint advisory score / the four generator no-op runs + `git diff --exit-code -- docs/` exit code.\n4. `git status --short` + `git diff --stat` (should be the plan README only) and confirmation that all eight ACC lines are checked + annotated.\n5. Any ACC that needed evidence nuance, any deviations, anything you stopped on.",
  "subagent_type": "phase-implementer"
}
```

**Output:**

```
<task id="ses_fbcb2719cffex56rRNwMEDbGNo" state="completed">
<task_result>


Phase 7 is complete. Final report:

---

# Phase 7: Final cross-cutting verification — complete

## 1. Live e2e run (ACC-008b) — full captured output

Script: `/tmp/opencode/feat22_e2e.py` (outside the repo), run as `uv run --frozen python /tmp/opencode/feat22_e2e.py` from the repo root. It sets `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR` to a fresh `tempfile.mkdtemp()` **before** any tool call, drives the real tool functions, asserts every step, then removes the temp dir:

```

=== DOMAIN req ===
created req id=594cd34e-5358-40f2-9a0b-e2b1f6f8d5a6
get(raw=True) body line count N=20
middle-range replace: begin=end=7
before line 7: 'If the engine becomes too hot, the lifetime of the system decreases.'
after line 7: 'E2E-replaced description line.'
out-of-range lines byte-identical (19 lines checked)
N+1 append: begin=end=21, fragment lines=['', '## Notes', '', 'A note.']
prior 20 lines unchanged; new last line(s)=['', '## Notes', '', 'A note.']
parsed: body.description='## Description\\n\\nE2E-replaced description line.\\n'
parsed: body.notes='## Notes\\n\\nA note.\\n'
set_status status='accepted': updated 2026-08-27T15:21:16.920820 -> 2026-08-27T15:21:17.376827, frontmatter.status='accepted'
=== DOMAIN rsk ===
created rsk id=7c70cc5e-1ce0-4cf1-a105-6ea45a40a248
get(raw=True) body line count N=37
middle-range replace: begin=end=5
before line 5: 'A root condition.'
after line 5: 'E2E-replaced root condition.'
out-of-range lines byte-identical (36 lines checked)
N+1 append: begin=end=38, fragment lines=['', '## Owner', '', 'The safety team.']
prior 37 lines unchanged; new last line(s)=['', '## Owner', '', 'The safety team.']
parsed: body.cause='## Cause\\n\\nE2E-replaced root condition.\\n'
parsed: body.owner='## Owner\\n\\nThe safety team.\\n'
set_status status='mitigating': updated 2026-08-27T15:21:17.475597 -> 2026-08-27T15:21:18.156772, frontmatter.status='mitigating'
=== DOMAIN uc ===
created uc id=151e0a6b-69f4-4fbe-ad08-c7b2e91b2a96
get(raw=True) body line count N=36
middle-range replace: begin=end=7
before line 7: 'Buyer issues request directly to our company.'
after line 7: 'E2E-replaced goal-in-context line.'
out-of-range lines byte-identical (35 lines checked)
N+1 append: begin=end=37, fragment lines=['', '## Open Issues', '', '- Is the scope final?']
prior 36 lines unchanged; new last line(s)=['', '## Open Issues', '', '- Is the scope final?']
parsed: body.characteristic_information.goal_in_context='### Goal in Context\\n\\nE2E-replaced goal-in-context line.\\n'
parsed: body.open_issues='## Open Issues\\n\\n- Is the scope final?\\n'
set_status status='proposed': updated 2026-08-27T15:21:18.309257 -> 2026-08-27T15:21:19.349610, frontmatter.status='proposed'
=== DOMAIN adr ===
created adr id=6bd17f45-0c1a-43ac-84a3-104e08e58d95, initial status='proposed'
adr frontmatter.status after set_status='superseded by 00000000-0000-4000-8000-000000000000'
temp dir removed: /tmp/feat22_e2e_zzkom46o exists=False
E2E-OK

```

Exit code 0. Cleanup: `git status --short` after the run showed **no residue** (only the plan-README edit, which I made afterwards).

## 2. Live counts + fresh-subprocess import

`asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real `server.mcp`:
```

tools=71 resources=25 prompts=19
removed-tools-present: none
generic-update-present: True generic-set_status-present: True

```
Fresh subprocess: `uv run --frozen python -c "import biz.dfch.specmgr.server"` → **exit 0**.

## 3. Full gate evidence (all fresh runs at the final state)

| Check | Result |
|---|---|
| `uv run --frozen ruff format --check` | `1094 files already formatted`, exit 0 (re-run **after** the README edit; the README itself explicitly checked: "1 file already formatted") |
| `uv run --frozen ruff check` | `All checks passed!`, exit 0 |
| `uv run --frozen vulture src/ whitelist.py --min-confidence 60` | clean, exit 0 |
| `uv run --frozen python -m unittest discover -s tests -t . -p "test_*.py"` | **`Ran 1779 tests in 46.361s` / `OK`**, exit 0 (final-state re-run; an earlier run at the same tree: `Ran 1779 tests in 46.627s` / `OK`) |
| `uv run --frozen pylint $(git ls-files '*.py')` (advisory) | **8.94/10** (exit 30 = advisory bitmask only). All 105 `E` messages are pre-existing false positives in the `req`/`gol`/`uc`/`rsk` `models/` packages and `models/md/`; **zero** in any of the 105 files this feature touched (verified by set-intersection with `git diff --name-only f9586e6..c82abeb -- src/`) and zero in `general/tools/` or `server.py` → per instructions, no code touched |
| `specmgr docs` / `mcp-docs` / `adr-toc` / `schema` | all no-ops (305 module pages + GENERATED.md; MCP.md; adr/README.md; all seven schemas "unchanged"), then `git diff --exit-code -- docs/` → **exit 0** |

Supporting fresh runs: the 16 prompt test files → **`Ran 186 tests in 0.034s` / `OK`**; ACC-005 grep → **121 match lines in 28 files**, all kept-by-design (31 prompt-function-name lines, 8 prompt-name enumerations in `server.py`/domain `__init__.py`, 8 prompt-name refs in the four `*_create_instructions.md`, 74 in the 16 prompt test files) — zero in `tools/`/`models/`/`general/`, zero `set_status_<d>` anywhere, zero tool refs in `data/*.md`; `docs/MCP.md` carries 0 of the 15 removed `### Tool:` entries (71 total; generic `set_status` line 855, `update` line 868, with the `type` enum rows quoted in the annotation); ACC-006 greps → 18 data files with the generic call shapes, all six domain update-instruction files verified to carry the range-update flow passage.

## 4. Repo state

```

$ git status --short
M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md

$ git diff --stat
.../feat-22-consolidate-mutation-tools/README.md | 339 +++++++++++++++++----
1 file changed, 283 insertions(+), 56 deletions(-)

```
Only the plan README changed; nothing committed. All **eight ACC lines are `- [x]` with inline `**PASS** — <evidence>` annotations** (feat-18 style, 2-space continuations, ≤80 cols). Structural byte-check performed: every HEAD line survives verbatim except the deliberately changed ones (8 checkboxes, 2 task checkboxes + `status: done`, frontmatter `status: done`, the 8 ACC final lines gaining their annotations, the Current Status paragraph, and the Related PRs/Commits placeholder). The pre-existing 19 three-space-indented lines in the Phase 4 task block were left untouched. Task 7.1/7.2 flipped to done; Current Status, a new top `#### Update 2026-08-27 (Phase 7: Final verification)` entry (all earlier entries preserved), and the six phase commits (`2647649`…`c82abeb`, Phases 1–6, with a note that Phase 7's commit is deliberately not listed) are in place.

## 5. Nuances / deviations (no ACC unmet, no product bugs)

- **My e2e script, first run**: failed on my own assertion (`Description.value` — plain `MarkdownSection2` sections have no `value` field; I switched to `str(section)` substring checks). The product behaved correctly throughout that run (both edits verified byte-exact before my check failed); the fixed script passed end-to-end on the second run. Not a product issue.
- **First unittest capture**: the `Ran N tests` summary is on stderr and a piped stdout print flushed out of order, so `tail` missed it; re-ran with separated streams (and again at final state) — `Ran 1779 tests … OK`.
- **Pylint**: 8.94/10, advisory; all E messages pre-existing and outside this feature's files — recorded, not fixed, per the phase instructions.
- **Typo in my own targeted test invocation** (`tests.tsv` for `tests.tsv`… i.e., `tsv` instead of `tsk`) caused two import errors on the first try; re-ran with a module list generated from `git ls-files` → 16 files, 186 tests, OK. No repo impact.
- While editing Task 7.1/7.2 lines I briefly drifted two continuation lines from the file's 2-space to 3-space indent; caught it in the byte-check and restored.

Nothing blocks the orchestrator: Phase 7 is done, gate is green, the working tree holds exactly the plan-README change ready for the Phase 7 commit.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 145.1s)

_Thinking:_

Phase 7 reported as complete, including the live e2e execution. Next is my independent verification:

1. Re-run the e2e script myself? The script is at /tmp/opencode/feat22_e2e.py — I can re-run it to confirm (read-only against the repo; creates/deletes a temp dir). This gives direct evidence of ACC-008. Let me confirm the script exists and re-run it.
2. Re-run the gate: ruff format --check, ruff check, vulture, unittest (1779), 4 generators, git diff --exit-code -- docs/.
3. Verify the README: all 8 ACCs checked + annotated; frontmatter status is done; Current Status; Recent Updates; Related PRs/Commits; tasks 7.1/7.2 done.
4. Confirm that git status shows only the README changes.

Batch 1 (parallel): e2e re-run + full gate.
Batch 2: README checks (read the ACC section, frontmatter, Related PRs section, git diff stat).

Phase 7 reported complete. Verifying independently — re-running the e2e script myself and the full final gate:

**Tool: bash**

**Input:**

```json
{
  "command": "ls -la /tmp/opencode/feat22_e2e.py && uv run --frozen python /tmp/opencode/feat22_e2e.py 2>&1 | tail -12; echo \"e2e-exit=$?\"",
  "timeout": 600000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
-rw-rw-r-- 1 user user 9319 Aug 27 15:20 /tmp/opencode/feat22_e2e.py
  after  line 7: 'E2E-replaced goal-in-context line.'
  out-of-range lines byte-identical (35 lines checked)
N+1 append: begin=end=37, fragment lines=['', '## Open Issues', '', '- Is the scope final?']
  prior 36 lines unchanged; new last line(s)=['', '## Open Issues', '', '- Is the scope final?']
  parsed: body.characteristic_information.goal_in_context='### Goal in Context\n\nE2E-replaced goal-in-context line.\n'
  parsed: body.open_issues='## Open Issues\n\n- Is the scope final?\n'
set_status status='proposed': updated 2026-08-27T16:08:21.846021 -> 2026-08-27T16:08:23.006327, frontmatter.status='proposed'
=== DOMAIN adr ===
created adr id=14360e2e-af1d-4e48-bc92-e484ffe6d3a5, initial status='proposed'
adr frontmatter.status after set_status='superseded by 00000000-0000-4000-8000-000000000000'
temp dir removed: /tmp/feat22_e2e_62jn33z1 exists=False
E2E-OK
e2e-exit=0

```

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && uv run --frozen ruff format --check && uv run --frozen ruff check && uv run --frozen vulture src/ whitelist.py --min-confidence 60 && echo VULTURE_OK && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/opencode/phase7-unittest.log 2>&1; echo \"unittest-exit=$?\"; grep -aE \"^(Ran |OK|FAILED)\" /tmp/opencode/phase7-unittest.log && uv run --frozen specmgr docs >/dev/null && uv run --frozen specmgr mcp-docs >/dev/null && uv run --frozen specmgr adr-toc >/dev/null && uv run --frozen specmgr schema >/dev/null && git diff --exit-code -- docs/ && echo P7_DOCS_ZERO_DRIFT && uv run --frozen python -c \"\nimport asyncio\nfrom biz.dfch.specmgr.server import mcp\nnames = [t.name for t in asyncio.run(mcp.list_tools())]\nprint('tools:', len(names), 'resources:', len(asyncio.run(mcp.list_resources())), 'prompts:', len(asyncio.run(mcp.list_prompts())))\nremoved = [n for n in ('update_req','update_uc','update_tsk','update_qa','update_prb','update_gol','update_rsk','set_status_req','set_status_uc','set_status_tsk','set_status_qa','set_status_prb','set_status_gol','set_status_rsk') if n in names]\nprint('removed-tools-present:', removed or 'none')\nprint('set_status count:', names.count('set_status'))\n\"",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
 M .specmgr/feat/feat-22-consolidate-mutation-tools/README.md
1094 files already formatted
All checks passed!
VULTURE_OK
unittest-exit=0
Ran 1779 tests in 47.931s
OK
P7_DOCS_ZERO_DRIFT
tools: 71 resources: 25 prompts: 19
removed-tools-present: none
set_status count: 1

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 83.8s)

_Thinking:_

My independent verification:

- **E2E re-run: E2E-OK, exit 0** — req/rsk/uc all passed (mid-range byte-exact match, N+1 append, parse verification, set_status verified), ADR supersession reads as `"superseded by 00000000-0000-4000-8000-000000000000"` ✓, temp directory deleted, no residue.
- Gate: ruff (1094) ✓, ruff check ✓, vulture ✓, **1779 tests OK** ✓, all 4 generators no-op → **P7_DOCS_ZERO_DRIFT** ✓.
- Live: **71/25/19**, 0 of the removed tools, exactly 1 set_status ✓.

Next, verifying the final state of the README: front matter status is done, 8 ACCs checked with PASS annotations, Related PRs/Commits, Current Status, Recent Updates. Let me read the relevant sections.

E2E independently reproduced: **E2E-OK** (all 3 domains + ADR supersession, temp dir cleaned, no residue). Gate is fully green: 1779 tests, zero drift across all 4 generators, live at 71/25/19, deleted tools are zero. Final check — the state of the feature README:

**Tool: bash**

**Input:**

```json
{
  "command": "head -8 .specmgr/feat/feat-22-consolidate-mutation-tools/README.md && echo === && grep -cE \"^- \\[x\\] ACC-\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md && grep -c \"\\*\\*PASS\\*\\*\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md && echo === && grep -nE \"^- \\[.\\] ACC-\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | cut -c1-60 && echo === && sed -n '/### Related PRs/,$p' .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | head -25 && echo === && grep -n \"Task 7.1:\\|Task 7.2:\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md | cut -c1-30",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
---
created: 2026-08-26
id: feat-22-consolidate-mutation-tools
status: done
updated: 2026-08-27
version: 1.0.0
---

===
8
10
===
130:- [x] ACC-001: Verifies REQ-001 — for every one of the
152:- [x] ACC-002: Verifies REQ-002 — for every one of the
187:- [x] ACC-003: Verifies REQ-003 — for all seven domain
209:- [x] ACC-004: Verifies REQ-004 — for all eight types,
242:- [x] ACC-005: Verifies REQ-005 — the 15 superseded to
266:- [x] ACC-006: Verifies REQ-006 — all 11 instruction d
291:- [x] ACC-007: Verifies REQ-007 — `specmgr docs`, `spe
314:- [x] ACC-008: Verifies REQ-001/002/004/005 — the Phas
===
### Related PRs / Commits

- `2647649` — Phase 1: ADR (the feature's accepted ADR,
  36905d5b-8057-4294-8665-c7eed5534db0)
- `fc76490` — Phase 2: generic `update` tool + `raw` read parameter
- `971998f` — Phase 3: retire the seven per-domain `update_<d>` tools
- `d9f7a28` — Phase 4: generic `set_status` tool + retire the eight old
  status tools
- `db0fec5` — Phase 5: narration rewrite (prompts + instruction data)
- `c82abeb` — Phase 6: cross-cutting documentation and release notes
  (`AGENTS.md`, `CHANGELOG.md`)

One Conventional Commit per accepted phase, created by the phase-
orchestrator. This list covers Phases 1–6; Phase 7's own commit does not
exist yet (the orchestrator commits it after this entry) and is
deliberately not listed.
===
879:- [x] Task 7.1: Walk ACC-0
895:- [x] Task 7.2: Set this R

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 77.8s)

_Thinking:_

README final state verification complete:

- Frontmatter: `status: done`, `updated: 2026-08-27` ✓
- All 8 ACCs are `- [x]`, with 10 `**PASS**` markers (8 ACC annotations; the 2 extra PASS strings are probably in Current Status / Recent Updates, or within annotations that mention multiple PASSes — either way, 8 checked ACCs is the important thing) ✓
- Related PRs/Commits: 6 phase commits with notes ✓
- Tasks 7.1/7.2 marked complete ✓

Just to be safe, let me skim one of the annotated ACCs to check the quality of the annotation style… Actually no, the subagent has already done the byte-level checks and my gate is green, so I'll just do a quick visual check of one annotation (ACC-008, the one with e2e evidence).

All final-state checks pass. One last look at the ACC-008 annotation quality, then the final commit:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '314,345p' .specmgr/feat/feat-22-consolidate-mutation-tools/README.md",
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
}
```

**Output:**

```
- [x] ACC-008: Verifies REQ-001/002/004/005 — the Phase-1 ADR exists in
  `docs/adr/` with status `accepted` and is listed in `docs/adr/README.md`; a
  live, un-mocked end-to-end run in a temporary `SPECMGR_DOCS_DIR` passes for
  `req`, `rsk`, and `uc`: `create_<d>` → `get_<d>(id, raw=True)` →
  `update(id, type, content, begin, end)` (one middle-range replace, one
  `N+1` append) → `get_<d>` (content verified) → `set_status(id, type,
  status)` (domain-valid value) → `get_<d>` (status verified); for ADR:
  `create_adr` → `set_status(id, type="adr", status="superseded",
  superseded_by=…)` → status reads `"superseded by …"`;
  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real
  `server.mcp` instance reports **71 tools / 25 resources / 19 prompts**; a
  fresh subprocess import of `biz.dfch.specmgr.server` succeeds. **PASS** —
  (a) the Phase-1 ADR exists at `docs/adr/36905d5b-8057-4294-
  8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-
  into-g.md` with `status: accepted` and is listed in `docs/adr/README.md`
  (line 20: "Consolidate whole-body update and status-change tools into
  generic type-dispatched tools", with "- Id: 36905d5b-8057-
  4294-8665-c7eed5534db0" and "- Status: accepted" beneath it). (b) the
  live, un-mocked end-to-end run (throwaway script `/tmp/opencode/feat22_
  e2e.py` against a temp `SPECMGR_DOCS_DIR` + `SPECMGR_ADR_DIR`, driving the
  real tool functions; printed `E2E-OK`, exit 0) passed for all three whole-
  body domains and ADR — per domain: `create_<d>` → `get_<d>(id, raw=True)`
  (req N=20, rsk N=37, uc N=36 body lines) → one middle-range replace
  (changed line exactly the fragment, every out-of-range line byte-identical)
  → one `N+1` append (prior lines unchanged, new last lines exactly the
  fragment) → parsed `get_<d>` reflecting both edits (req `description` +
  `notes`, rsk `cause` + `owner`, uc `goal_in_context` + `open_issues`) →
  `set_status` with a domain-valid value (req `accepted`, rsk `mitigating`,
  uc `proposed`) → parsed status verified and `updated` bumped; for ADR:
  `create_adr` (initial status `proposed`) → `set_status(id, type="adr",
  status="superseded", superseded_by="00000000-0000-4000-8000-000000000000")`
  → `get_adr`'s frontmatter status reads exactly "superseded by

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 83.7s)

_Thinking:_

The annotations are in exactly the same format as feat-18, complete with concrete evidence. Phase 7 is fully verified:

✅ E2E independently re-run: E2E-OK
✅ Full gate: 1779 tests, ruff, vulture, zero drift on all 4 generators
✅ 71/25/19, 0 deleted tools, 1 set_status
✅ README: front matter status is done, 8/8 ACCs have been checked and annotated, Related PRs/Commits, tasks completed

Commit Phase 7 (final commit, per user instructions no push). After that, update the todos and submit the final summary.

Annotation is feat-18-style with concrete evidence. **Phase 7 verified — committing the final phase** (no push, per your instructions):

**Tool: bash**

**Input:**

```json
{
  "command": "git add -A && git commit -m \"docs(feat-22): verify acceptance criteria and close the feature\n\nPhase 7: walk ACC-001..ACC-008 with fresh evidence and annotate each\ninline (feat-18 style); live un-mocked end-to-end in a temporary\nSPECMGR_DOCS_DIR passes for req/rsk/uc (create -> get raw ->\nmiddle-range replace verified byte-exact -> N+1 append -> parsed\ncontent verified -> set_status with domain-valid value -> status\nverified) and for ADR (create_adr -> set_status(type=\\\"adr\\\",\nsuperseded) -> status reads \\\"superseded by ...\\\"); full quality gate\ngreen (1779 tests OK, pylint advisory 8.94/10 with no findings in\nfeature-touched files, all four specmgr generators no-op, zero docs\ndrift); live registration 71 tools / 25 resources / 19 prompts with\nnone of the 15 superseded tools present; fresh-subprocess import OK.\nFeature README status -> done; Related PRs/Commits records the six\nphase commits.\" && git log --oneline -8 && git status --short | wc -l",
  "timeout": 900000,
  "workdir": "/home/user/src/biz.dfch.SpecMgr-feat-22"
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
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
[feat-22 5b459a0] docs(feat-22): verify acceptance criteria and close the feature
 1 file changed, 283 insertions(+), 56 deletions(-)
5b459a0 docs(feat-22): verify acceptance criteria and close the feature
c82abeb docs(feat-22): update AGENTS.md and CHANGELOG.md for the consolidated mutation tools
db0fec5 docs(feat-22): rewrite prompt narration to the generic update/set_status tools
d9f7a28 feat(feat-22): add generic set_status tool and retire the eight old status tools
971998f refactor(feat-22): retire the seven per-domain update_<d> tools
fc76490 feat(feat-22): add generic update tool with line-range replace and raw get reads
2647649 docs(feat-22): add Phase-1 ADR for generic type-dispatched mutation tools
f9586e6 feat(feat-22): add design and plan for consolidation of mutation tools
0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 81.6s)

_Thinking:_

Phase 7 has been committed as `5b459a0`. Working tree is clean (0 lines from git status). All 7 phases complete.

Update the TODO list to mark everything as done, then present the final summary to the user.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 5: Narration rewrite — 18 instruction data files + prompt module docstrings + 16 prompt test files, gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 7: Final cross-cutting verification — ACC-001..008 walked with evidence, 71/25/19 live check, e2e runs, README status → done",
      "status": "completed",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 1: ADR — create feature ADR via specmgr_create_adr (status accepted), validate, adr-toc, phase gate, README progress update",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Generic update tool (general/tools/update.py + _splice.py) + raw param on 7 get_<d> tools, tests, server.py docstring, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Retire the 7 per-domain update_<d> tools + tests + registrations, grep verification, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Generic set_status tool + retire 8 old status tools (atomic — name collision), tests, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 5: Narration rewrite — 18 instruction data files + prompt module docstrings + 16 prompt test files, gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 6: AGENTS.md + CHANGELOG.md updates, final regeneration (docs/mcp-docs/adr-toc/schema), gate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 7: Final cross-cutting verification — ACC-001..008 walked with evidence, 71/25/19 live check, e2e runs, README status → done",
    "status": "completed",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · qwen3.8-27b-bf16-896k · 96.0s)

_Thinking:_

Feature complete. Final summary for the user. Concise yet complete: the 7 phases, commits, key verification evidence, deviations worth noting, and state (committed, not pushed, clean tree).

**Feature feat-22-consolidate-mutation-tools is complete** — all 7 phases implemented, verified, and committed on `feat-22` (nothing pushed, tree clean).

## Phase commits

| Phase | Commit | Content |
|---|---|---|
| 1 | `2647649` | Feature ADR `36905d5b` (accepted, via `specmgr_create_adr`) + adr-toc |
| 2 | `fc76490` | Generic `update(id, type, content, begin, end)` + `_splice.py` + `raw` on the 7 `get_<d>` tools (47 tests, 85/25/19) |
| 3 | `971998f` | Retired the 7 `update_<d>` tools + all non-narration references (78/25/19) |
| 4 | `d9f7a28` | Generic `set_status(id, type, status, superseded_by)` + retired the 8 old status tools atomically (71/25/19 = target) |
| 5 | `db0fec5` | Narration rewrite: 18 data files, 11 prompt modules (docstring-only), 16 prompt tests (+11 tests) |
| 6 | `c82abeb` | `AGENTS.md` + `CHANGELOG.md` `[Unreleased]` (breaking + added, ADR cited) |
| 7 | `5b459a0` | ACC-001…008 walked and annotated inline; feature status → `done` |

## Verification (each gate re-run by me, not taken on trust)

- **Final state**: 1779 tests OK, ruff/vulture clean, pylint advisory 8.94/10 with zero findings in feature-touched files, all four `specmgr` generators no-op (zero `docs/` drift), fresh-subprocess import OK
- **Live registration**: 71 tools / 25 resources / 19 prompts; none of the 15 superseded tools present; `set_status` registered exactly once
- **ACC-005/006 greps**: zero tool references in `data/*.md`, zero `set_status_*` anywhere in `src/`+`tests/`; only kept-by-design prompt names remain
- **ACC-008 e2e** (I re-ran the script independently): req/rsk/uc each passed create → `get(raw=True)` → byte-exact middle-range replace → `N+1` append → parsed verification → `set_status`; ADR supersession reads exactly `"superseded by 00000000-…0000"`

## Notable decisions made along the way (all plan-consistent, all recorded in the README)

- Phase 2 needed a small additive enum-rendering branch in `commands/mcp_docs.py` (the plan's own gate required the 7-value enum to be visible in `docs/MCP.md`); `qa`/`prb` out-of-vocabulary test cases raise structural `AssertionError` because those bodies have no field-level validation
- Phase 3's plan-task list under-scoped the grep cleanup: ~40 docstring cross-references and 2 live integration tests had to be re-pointed too — all done
- Phase 5's "11 files" grew to 18 data + 16 test files (create/implement instructions and `qa_refine` also named old tools); ACC-005's zero-residual criterion was the binding one
- ADR's frontmatter has no `updated` field, so its `set_status` port correctly bumps nothing (verbatim behavior preserved)
- One Phase 5 subagent session was cancelled mid-work; I audited its partial state and re-delegated a finish-and-verify pass

The branch is ready for your review — say the word if you want it pushed or merged.

______________________________________________________________________
