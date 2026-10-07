---
created: '2026-08-25 00:00:00.000Z'
id: feat-18-goal
status: done
updated: '2026-10-07T06:21:40.913Z'
version: 1.0.0
---

# Feature: Add artifact type Goal (gol)

## Plan

### Overview

Add a new markdown artifact type, `Goal` (abbreviation `gol`), for capturing
high-level business goals — the strategic "what the organization wants to
achieve" level that sits above individual requirements. `gol` follows the
domain-first hierarchy and MCP surface already established by `req`/`prb`
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and mirrors `req`'s body schema
with exactly two deliberate omissions: no `## Characteristics` section (ISO
25010:2023 quality characteristics are a requirement-level attribute — a
business goal stays deliberately free of them) and no `## Level` section
(RFC 2119 obligation strength is implicit — a goal is always a MUST). `req`
already anticipates this artifact type: its `## Related Artifacts` →
`### Goals` cross-reference sub-list (exercised in `req_example.md` as
`GOL-0007: Competitive Engines in Consumer Vehicles`) points at documents
of exactly this shape, and `gol_example.md` will be that very goal so the
two packaged examples read coherently side by side. `gol` reuses `req`'s
whole-body update convention (not ADR's granular `update_section`
mechanism) and `req`'s 7-value frontmatter status set.

### Requirements

- REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`, 7-value status set `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented`, `req`'s exact set) and body (H1 title, mandatory `statement` lead paragraph, optional `## Description`, optional `## Priority`, optional `## Tags`, mandatory `## Source`, optional `## Related Artifacts` holding four optional, fixed-heading `### ` cross-reference sub-lists — `Requirements`/`Decisions`/`Goals`/`Acceptance Criteria` — optional `## More Information`, optional `## Notes`). No `## Characteristics` and no `## Level` (see Design Notes).
- REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body, document, parser, summary), domain-first, mirroring `req`/`prb`'s exact file shapes. No `models/md` engine changes are needed — every field is buildable with the existing declarative heading-mapped parser.
- REQ-003: Parse/validate `gol` documents from markdown, mirroring `parse_req`/`parse_prb`'s two-error-channel convention (`AssertionError` for structural problems, `pydantic.ValidationError` for field-level problems).
- REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, **plus** `list_gol` as a paged tool from day one (per ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a `specmgr://gol/list` resource and convert it later): `parse_gol`, `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub), `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`, `list_gol`.
- REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template` (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_gol`/`update_gol` — narrated, `TodoWrite` + `question`-tool-driven interview flows reusing the dedup-check-first pattern from `req/prompts/create_req.py` and the `TodoWrite`/`question`-tool narration pattern from `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use their own packaged instructions data file (`gol_create_instructions.md`/`gol_update_instructions.md` under `gol/data/`), not an inline string.
- REQ-007: Packaged example/template/schema data (`gol/data/`) via the existing generic `general/tools/_packaged_data.py`, with the matching `pyproject.toml` package-data entry, pre-commit hook, and CI step.
- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new `gol` entry in the doc-type registry, `commands/schema.py`), `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md` updated to eight domain/cross-cutting packages.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`, `specmgr://gol/schema`); a reference `gol_reference.md` exercising every field (`statement`, `Source` plus all optional sections present, `Related Artifacts` with all four sub-lists) round-trips through the parser. **PASS** — `docs/gol_schema.json` exists with `"$comment": "v1"` (line 2) and `"$schema": "https://json-schema.org/draft/2020-12/schema"` (line 403); `specmgr://gol/schema` is registered — live `asyncio.run(mcp.list_resources())` on the real `server.mcp` instance returns it among exactly 3 gol resources, and `docs/MCP.md` carries it (resource table line 20, detail section line 49). Live round-trip: `uv run --frozen python` reads `.specmgr/feat/feat-18-goal/gol_reference.md`, calls `parse_gol`, and asserts `str(doc.body)` equals the file's body (frontmatter stripped, `format_text`-normalized) byte-exact — 2030 == 2030 bytes (id `deaddead-goal-goal-goal-deaddeadgoal`, status `accepted`); the committed test `tests/gol/models/v1/test_parser.py` (10 tests, incl. `test_parses_full_reference_document`'s own byte-exact assertion) re-run live: OK.
- [x] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`, `Related Artifacts` and each of its four sub-lists, `More Information`, `Notes`) fields correctly; `GolFrontmatter.status` rejects any value outside the seven-value set. **PASS** — `tests/gol/models/v1/test_frontmatter.py` + `test_body.py` re-run live: 41 tests OK (each optional section and each of the four `Related Artifacts` sub-lists covered individually absent/present); a live minimal doc (H1 + statement + `## Source`, zero optional sections) parses with all six optional fields `None` (`description`/`priority`/`tags`/`related_artifacts`/`more_information`/`notes`); `GolFrontmatter(status="pending")` raises `pydantic.ValidationError` naming the seven allowed values — "status must be one of ['accepted', 'deprecated', 'draft', 'implemented', 'proposed', 'rejected', 'superseded'], got 'pending'" — and the same at parse level for a `status: pending` frontmatter block (loc `('status',)`).
- [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a well-formed document; missing the `statement` lead paragraph or the `Source` section raises `AssertionError`; an invalid field value (e.g. a `Priority` outside 0–99, an out-of-set `status`) raises `pydantic.ValidationError`. **PASS** — `tests/gol/models/v1/test_parser.py` re-run live: 10 tests OK, with the `AssertionError` tests (`test_missing_statement_raises_assertion_error`, `test_missing_source_raises_assertion_error`, `test_out_of_order_sections_raise_assertion_error`) and the `ValidationError` tests (`test_invalid_status_raises_validation_error`, `test_invalid_type_raises_validation_error`, `test_priority_out_of_range_raises_validation_error` over 100/-1/007, plus `test_priority_upper_bound_is_accepted` for 99) all green; live demos: a doc without `## Source` raises `AssertionError` ("Goal.source: expected Source, found no match; remaining text (0 line(s)) starts with:") and `## Priority` value `100` raises `pydantic.ValidationError` (loc `('value',)`, "value must match pattern '^(0|[1-9][0-9]?)$', got '100'").
- [x] ACC-004: Verifies REQ-004 — every listed tool is implemented, registered, and callable; `list_gol` returns a `PagedResult[GolSummary]` with default page size 25 / cap 100, mirroring the other five domains' `list_<d>` tools exactly (no resource-first-then-converted history for this domain). **PASS** — `docs/MCP.md` carries all 10 `### Tool:` gol entries (`create_gol`, `delete_gol`, `get_gol`, `get_gol_example`, `get_gol_template`, `list_gol`, `parse_gol`, `set_status_gol`, `update_gol`, `validate_gol`) under the header line 6: `20 resource(s), 1 resource template(s), 74 tool(s), 17 prompt(s)`; live `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real `server.mcp` instance confirms the 74/20/17 totals with exactly those 10 gol tools present; `tests/gol/tools/test_list_gol.py` re-run live: 11 tests OK (default page size with 26 docs, `max_results` clamped to the 100 cap, `offset` paging without overlap, `truncated` boundary incl. offset exactly at the end, negative-offset flooring, skip-malformed-file); live paging in a temp `SPECMGR_DOCS_DIR` with 26 `create_gol`-ed docs: `list_gol()` → total=26, max_results=25, truncated=True, 25 items; `list_gol(max_results=100)` → 26 items, truncated=False; `list_gol(offset=25)` → 1 item, truncated=False.
- [x] ACC-005: Verifies REQ-005 — every listed resource is implemented and registered (no `/{id}`, no `/list`, as designed). **PASS** — `docs/MCP.md` carries exactly three `specmgr://gol/...` rows (`/example` line 19, `/schema` line 20, `/template` line 21; detail sections lines 40–56), and a grep of both `docs/MCP.md` and `src/biz/dfch/specmgr/gol/resources/` finds no `specmgr://gol/{id}`-style dynamic resource and no `specmgr://gol/list` (the package holds exactly `gol_example.py`, `gol_schema.py`, `gol_template.py`, one `@mcp.resource()` each); live: `gol_schema()` returns the parsed dict (`$comment` `v1`, 2020-12 `$schema`, top-level `required: ['frontmatter', 'body']`), `gol_example()` 2162 chars, `gol_template()` 1201 chars; `tests/gol/resources/` re-run live: 13 tests OK.
- [x] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate: (a) a duplicate/similar-document check via `list_gol` first, (b) building a `TodoWrite` list covering `statement` + `Source` + each optional section, (c) using the `question` tool to elicit each field (explicitly allowing skip for optional ones), (d) calling `create_gol(content)`/`update_gol(id, content)` (whole-body) at the end — verified live by reading both packaged instruction files in full and manually walking the narrated flows end to end against a real document, not just asserting their static text. **PASS** — both instruction files read in full, step headers quoted: `gol_create_instructions.md` — `## 0. Check for an existing goal on this topic first` (`list_gol` dedup check, `question`-tool follow-up on a near-duplicate), `## 1. Structure recap` (incl. the explicit no-`Characteristics`/no-`Level` note), `## 2. Build a todo list, then gather the information one at a time` (TodoWrite per `statement` + `Source` + each optional section; `question`-tool interview, mandatory fields first, explicit skip allowance), `## 3. Use the template/example/schema as references`, `## 4. Tool call sequence` (`create_gol(content)`, optional `validate_gol` dry-run), `## 5. Later revisions`; `gol_update_instructions.md` — `## 1. Read current state first` (`get_gol(id)`, never assume prior state), `## 2. Show which sections are present and which are empty`, `## 3. Elicit the new/revised text`, `## 4. Map the requested change to the right tool` (whole-body `update_gol(id, content)` carrying forward every unchanged section; `set_status_gol` as a separate, optional follow-up naming the 7-value set), `## 5. Check the schema, and validate before writing if useful`. Then the narrated flows were walked end to end against a real document in a temp `SPECMGR_DOCS_DIR` (self-simulated `question`-tool answers): `list_gol()` empty → no near-duplicate; `create_gol(content)` (statement + `Source` + one optional `## Description`) → id `07331e39-993d-4c17-b6b6-35bd83f11dab`, status `draft`; `get_gol(id)`; `update_gol(id, content)` adding the absent `## Notes` while carrying forward every unchanged section (id/status/created preserved, `updated` bumped); `set_status_gol(id, "accepted")`; final `get_gol(id)`/`list_gol()` show status `accepted`. Both prompt functions also resolved their packaged narration live (`$topic`/`$id` substituted: 3554 / 2567 chars). `tests/gol/prompts/` re-run live: 22 tests OK; `tests/gol/tools/test_integration.py` re-run live: 2 tests OK (full create→update→set_status→get→list→delete(stub) lifecycle, the stub raising `NotImplementedError` without touching the file).
- [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a real, non-editable install (`uv build --wheel` + scratch-venv install), mirroring feat-16's ACC-007 verification. **PASS** — `uv build --wheel` produced `dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl`; `unzip -l` confirms all five `gol/data/*` files (`gol_example.md`, `gol_schema.json`, `gol_template.md`, `gol_create_instructions.md`, `gol_update_instructions.md`) plus every gol module (35 wheel entries under `biz/dfch/specmgr/gol/`); installed non-editably with the mcp extra into a scratch venv under `/tmp/opencode/` (`uv venv --python 3.13` + `uv pip install "…whl[mcp]"` — the system `python3` is 3.10, below the project's `>=3.11` floor, so `uv`'s managed CPython 3.13.13 was used); in that venv, `inspect.getfile` proves the module loads from `…/gol-scratch-venv/lib/python3.13/site-packages/biz/dfch/specmgr/gol/…`, not the source checkout, and `get_gol_example()` (2162 chars), `get_gol_template()` (1201 chars), and `gol_schema()` (`$comment` `v1`, 2020-12 dialect, `title` `GolDocument`) all resolve real packaged content. Scratch venv and `dist/`/`build/` removed afterward; `git status` shows no residue (both gitignored).
- [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` all report no drift after implementation; `AGENTS.md` reflects eight domain/cross-cutting packages. **PASS** — re-run end to end in Phase 5: `specmgr docs` (exit 0), `specmgr mcp-docs` (exit 0), `specmgr schema` (exit 0, all six doc types "unchanged"), `specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data` (exit 0, packaged copy "unchanged"), `specmgr adr-toc` (exit 0), `specmgr coverage-badge` (exit 0, 98%, `docs/coverage.svg` unchanged); `git diff --exit-code -- docs/` exits 0 — zero drift on disk, and `docs/GENERATED.md`'s test-file count is unchanged (Phase 5 adds no test files). `AGENTS.md` line 5 reads `## Status: eight domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)` with the `gol/` bullet at line 81 (Phase 4 work).

### Scope

#### Included

in this feature:

- The `gol` markdown schema, Pydantic models, parser, and summary under
  `gol/models/v1/`.
- Full MCP surface (tools/resources/prompts/packaged data), including
  `list_gol` as a tool (not a resource) from the start.
- The interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` +
  `question`-tool-driven interview).
- Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

#### Explicitly Out Of Scope

- A `## Characteristics` section (ISO 25010:2023 quality attributes).
  Quality characteristics are a requirement-level attribute — a business
  goal states *what* to achieve, not *which quality dimension* it loads
  (user decision, planning session 2026-08-25).
- A `## Level` section (RFC 2119 obligation strength). A goal is
  implicitly always a MUST — obligation grading applies to requirements
  below it, not to the goal itself (user decision, planning session
  2026-08-25).
- Structured cross-referencing/validation of the `Related Artifacts`
  sub-lists (typed id validation, `GOL-NNNN:`-style format checks,
  existence checks against the other domains' base directories) — v1 keeps
  all four sub-lists as opaque free text, matching `req`'s own precedent.
  Revisit only if a concrete need emerges.
- ADR-style granular `update_section`/option-style per-field mutation
  tools — `update_gol` is a single whole-body replace tool, like
  `update_req`/`update_prb`. Individual sections stay addressable by their
  fixed heading text within the markdown body itself, not via a dedicated
  tool per section.
- Real implementation of `delete_gol` — a stub raising
  `NotImplementedError`, matching the other five domains' `delete_*` stubs
  (a shared, cross-domain decision deferred to future work).
- Any changes to `req`'s schema, data, or tools — REQ's existing
  `### Goals` cross-reference sub-list already anticipates this artifact
  type and needs no modification.
- A `specmgr gol-toc`-equivalent generation command or dedicated CI/
  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` already provide generically.

### Dependencies

#### Depends On

- ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
  not a resource — `list_gol` must follow this from day one), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
  `general/models/{DocSummary,PagedResult}` infrastructure, and the
  existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`,
  `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`,
  `MarkdownListItem`, `@alias`) — reused as-is, no engine changes
  anticipated.

#### Blocks

- None identified yet.

### Design Notes

**Schema:**

```
GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
  status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}
  (req's exact 7-value set -- goals are business-level requirements, so
   requirement-lifecycle semantics apply)

Goal(MarkdownSection1)                          # H1, free-form title (@alias ".+" REGEX)
├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)
├── description: Description | None             # optional H2 "Description", opaque free text leaf
├── priority: Priority | None                   # optional H2 "Priority", 0-99 single-line value + optional comment
├── tags: Tags | None                           # optional H2 "Tags", bullet list
├── source: Source                              # mandatory H2 "Source", single-line value
├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
│   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. "REQ-9687: ...")
│   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. "DEC-2703: ...")
│   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. "GOL-0007: ...")
│   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free text leaf
└── notes: Notes | None                         # optional H2 "Notes", opaque free text leaf
```

**No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —
both are deliberate, domain-driven omissions, not oversights: ISO 25010
quality characteristics grade *requirements*, and RFC 2119 obligation
strength is implicit (a goal is always a MUST). Consequently the only
mandatory body fields are `statement` and `Source`; a freshly created
`gol` document may have zero optional sections yet (all deferred to a later
`update_gol` call) but must always carry the goal statement and its source.

**`Priority` keeps `req`'s `MarkdownSection2WithComment` +
`field_validator`-on-`value.text` pattern** (0–99, no leading zeros other
than "0" itself), re-declared in `gol/models/v1/body.py` — domain packages
never import model classes from each other (verified: no cross-domain
imports exist in `src/`), so `req`'s `Priority`/`Level` classes are
*pattern* precedents, not shared code. `Description`/`Source`/
`MoreInformation`/`Notes` are bare opaque leaf subclasses with no further
declared fields — the same pattern verified for REQ's `MoreInformation`/
`Notes` and PRB's leaves.

**The four `RelatedArtifacts` sub-lists are 1:1 re-declarations of REQ's
own four classes**: `MarkdownSection3` with
`items: list[MarkdownListItem] = Field(min_length=1)`; heading text
("Requirements"/"Decisions"/"Goals"/"Acceptance Criteria") derives
implicitly via the `AliasType.SPACE_SEPARATED` convention (multi-word
`AcceptanceCriteria` → "Acceptance Criteria"), so no explicit `@alias` is
needed — exactly as in `req/models/v1/body.py`. All four sub-lists are
optional, as is `Related Artifacts` as a whole, and no consistency check
is enforced between them (REQ precedent). Cross-reference id formats
(`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text
only — not validated in v1. The `### Goals` sub-list includes goals for
cross-referencing peer/superseding goals (self-referencing is allowed; the
parser does not special-case a document's own id).

**Update mechanism: whole-body `update_gol(id, content)`**, not an
ADR-style `update_section`. The generic `adr/tools/update_section.py`
mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
ADR-specific code, not a shared cross-domain component — the same decision
as feat-16's for `prb`. Individual sections stay addressable by grepping/
editing their fixed heading text within the whole-body markdown.

**`list_gol` is a paged tool from day one** (`@mcp.tool(name="list_gol")`
returning `PagedResult[GolSummary]`, via `general/tools/_paging.py`'s
`paginate`/`normalize_paging`, default page size 25 / cap 100), not a
`specmgr://gol/list` resource — GOL is a new domain built *after* ADR
ec9f5262 was accepted, so it must not repeat the resource-then-convert
history of REQ/UC/TSK/QA/PRB (feat-13). `GolSummary` subclasses
`general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`),
like `ReqSummary`/`PrbSummary`; `title` is the body's H1 text.

**Prompts are narrated instructions only** (return a string, auto-wrapped
as a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call
`TodoWrite`/`question`/`get_gol`/`create_gol`/`update_gol` themselves; they
only narrate that the calling LLM should. This is the same contract every
existing prompt in this codebase already follows
(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).

- `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol`
  first to check for an existing, similar goal (mirrors `create_req`'s
  dedup-check pattern) and ask the user via `question` if a near-duplicate
  is found; (2) build a `TodoWrite` list with one entry per `statement` +
  `Source` + each optional section (`Description`/`Priority`/`Tags`/
  `Related Artifacts`/`More Information`/`Notes`); (3) use the `question`
  tool to elicit the goal statement (mandatory) and the source (mandatory)
  plus each optional field in turn, explicitly allowing the user to skip
  any optional one; (4) reference the packaged
  `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`
  for the fixed structure; (5) assemble the full body markdown per the
  schema above and call `create_gol(content)`.
- `update_gol(id: str) -> str`: instructs the LLM to (1) call
  `get_gol(id)` first (never assume prior state); (2) show the user which
  sections are already present and which are empty, and ask via
  `question` which ones (if any) they want to add or revise; (3) for each
  selected section, elicit the new/revised text via `question`; (4) call
  `update_gol(id, content)` (whole-body replace, carrying forward every
  unchanged section); (5) mention `set_status_gol` as a separate, optional
  follow-up (e.g. `implemented` once the goal has genuinely been reached,
  `rejected`/`superseded` if abandoned or replaced).

Both prompts' instructional text lives in packaged data files
(`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`, read
via `general.tools._packaged_data.read_packaged_text`, `string.Template`
substitution), matching `req_create_instructions.md`/
`prb_create_instructions.md`'s precedent — not an inline Python string.

**Frontmatter status** is REQ's exact 7-value closed set
(`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
`implemented`), re-declared as `GolFrontmatter`'s own `_ALLOWED_STATUSES`
frozenset (each domain declares its own set — `ReqFrontmatter`,
`TskFrontmatter`, `PrbFrontmatter` all do), with goal-specific semantics:
`draft` = still being written; `proposed` = under consideration;
`accepted` = agreed to be pursued; `implemented` = the goal has genuinely
been reached; `superseded` = replaced by another goal; `deprecated` = no
longer pursued, kept for reference; `rejected` = considered and not
pursued.

**Example/template documents:** `gol_example.md` is drafted as
`GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal
`req_example.md`'s `### Goals` sub-list already cross-references — so the
two packaged examples read coherently side by side; it reuses
`gol_reference.md`'s content verbatim (feat-16's own precedent:
`prb_example.md` reuses `prb_reference.md`). `gol_template.md` mirrors
`req_template.md` minus the `Characteristics` and `Level` sections, with
goal-oriented placeholder prose.

- Related, but explicitly out of scope here: issue #15 "Add artifact type
  Risk" (open) — a sibling domain that will follow the same pattern
  independently.

Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
  (`get_gol`), not a resource
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
  MCP tool (`list_gol`), not a resource — must be followed from the start
  for this new domain, not retrofitted later
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
  and explicitly *not* reused for `gol` (see Design Notes)

No new ADR is anticipated for this feature — every schema/tooling decision
either follows an existing ADR's precedent directly or is scoped enough to
log only in this file's own Decisions Made.

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end task (tests, full
quality gate, README Progress update), mirroring feat-16's per-phase
commit discipline, since implementation is likely to span multiple
sessions.

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

### Task List

#### Phase 100: Specification

- [x] Task 100.100: Write a full reference `gol_reference.md` (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field (`statement`, `Source`, plus all optional sections present: `Description`/`Priority`/`Tags`/`Related Artifacts` with all four sub-lists/`More Information`/`Notes`) — depends on: none — status: completed
- [x] Task 100.110: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` — `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["gol"]`, 7-value status set identical to `ReqFrontmatter`'s) — depends on: none — status: completed
- [x] Task 100.120: Define `gol` body structure (`gol/models/v1/body.py`) — `Goal(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`, mandatory `statement: MarkdownParagraph` + `source: Source`, optional `description`/`priority`/`tags`/`related_artifacts`/`more_information`/`notes`; `Priority` re-declares REQ's `MarkdownSection2WithComment` + `field_validator` pattern (0–99); `RelatedArtifacts(MarkdownSection2)` with four optional `MarkdownSection3` sub-lists (see Design Notes) — depends on: Task 1.2 — status: completed
- [x] Task 100.130: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` — structural + validation tests mirroring `tests/req/models/v1/`/`tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field combinations (each optional section individually absent/present; each of the four `Related Artifacts` sub-lists individually absent/present) — depends on: Task 1.3 — status: completed
- [x] Task 100.140: Phase-end quality gate — run the full pre-commit/quality gate (ruff format/check, vulture, full `unittest` suite); confirm `gol_reference.md` is `specmgr mdformat`-clean; add any new vulture-invisible Pydantic field names to `whitelist.py` if needed; update this README's Progress section — depends on: Task 1.1, Task 1.4 — status: completed

#### Phase 110: Pydantic Models, Parser & Schema

- [x] Task 110.100: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status: completed
- [x] Task 110.110: Implement `parse_gol(text: str) -> GolDocument` (model-layer function, mirrors `parse_req`) — depends on: Task 2.1 — status: completed
- [x] Task 110.120: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`, subclassing `general/models/summary.py::DocSummary`, for `list_gol`) — depends on: Task 2.1 — status: completed
- [x] Task 110.130: Field-level `Field(description=...)` on every scalar/optional field (schema-quality parity with REQ/PRB) — depends on: Task 2.1 — status: completed
- [x] Task 110.140: Implement `generate_gol_schema()` in `commands/schema.py` (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`), and register `"gol"` in the `specmgr schema` doc-type generator registry (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 — status: completed
- [x] Task 110.150: `tests/gol/models/v1/test_parser.py` — mirrors `TestParseReq`'s shape (minimal doc, full reference-doc round-trip, defaults-when-absent, invalid status, missing-mandatory-field `AssertionError` cases (`statement`, `Source`), invalid-field `ValidationError` (e.g. `Priority` out of 0–99 range, invalid `type` field)) — depends on: Task 2.2, Task 2.5 — status: completed
- [x] Task 110.160: Phase-end quality gate — full pre-commit/quality gate including Task 2.6's new tests; update this README's Progress section — depends on: Task 2.5, Task 2.6 — status: completed

#### Phase 120: MCP Surface

- [x] Task 120.100: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/`prb/tools/` exactly) — depends on: Task 2.2 — status: completed
- [x] Task 120.110: `parse_gol(path: str) -> GolDocument` tool wrapper (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: completed
- [x] Task 120.120: `create_gol(content: str) -> GolDocument` tool (body-only content; MCP builds frontmatter: `id`, `type="gol"`, `status="draft"`, `created=updated=now`, `version`) — depends on: Task 3.1 — status: completed
- [x] Task 120.130: `update_gol(id, content) -> GolDocument` tool (whole-body replace, preserves `id`/`type`/`status`/`created`/`version`, bumps `updated`) — depends on: Task 3.1 — status: completed
- [x] Task 120.140: `set_status_gol(id, status) -> GolDocument` tool (only path that changes `status`; reconstructs `GolFrontmatter` via its own constructor so the 7-value validator runs, mirroring `set_status_req`) — depends on: Task 3.1 — status: completed
- [x] Task 120.150: `delete_gol(id) -> NoReturn` stub tool — depends on: Task 3.1 — status: completed
- [x] Task 120.160: `validate_gol(content, full=False) -> bool` tool — depends on: none — status: completed
- [x] Task 120.170: `get_gol(id) -> GolDocument` tool (id-based single-document read; tool, not resource) — depends on: Task 3.1 — status: completed
- [x] Task 120.180: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]` tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging` (default page size 25, cap 100), preserving the standard skip-malformed-file scan behavior — depends on: Task 2.3, Task 3.1 — status: completed
- [x] Task 120.190: `get_gol_example`/`get_gol_template` tools + packaged data (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` — `req_template.md` mirrored minus `Characteristics`/`Level`) via `general/tools/_packaged_data.py` — depends on: Task 1.1 — status: completed
- [x] Task 120.200: `gol/resources/{gol_schema,gol_example,gol_template}.py` — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`, mirroring `specmgr://req/schema`), `specmgr://gol/example`, `specmgr://gol/template` (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status: completed
- [x] Task 120.210: `pyproject.toml` package-data entry for `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml` — widen the shared schema-hook glob to include `gol/models/v1`, add a `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status: completed
- [x] Task 120.220: `.github/workflows/ci.yml` — add the `docs/gol_schema.json` check + packaged-copy check steps — depends on: Task 2.5 — status: completed
- [x] Task 120.230: `gol/data/gol_create_instructions.md` + `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template` substitution, narrates the full interview flow — see Design Notes) — depends on: Tasks 3.3, 3.9 — status: completed
- [x] Task 120.240: `gol/data/gol_update_instructions.md` + `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status: completed
- [x] Task 120.250: `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`) and update its module docstring (Tools/Resources/Prompts sections) — depends on: Tasks 3.2-3.15 — status: completed
- [x] Task 120.260: `tests/gol/tools/...`, `tests/gol/resources/...`, `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout, including live end-to-end coverage of `create_gol`/`update_gol`'s narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_gol`'s paging behavior (default page size, `max_results` clamping, `offset` paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status: completed
- [x] Task 120.270: Phase-end quality gate — full pre-commit/quality gate including Task 3.17's new tests; update this README's Progress section — depends on: Task 3.17 — status: completed

#### Phase 130: Cross-cutting registration

- [x] Task 130.100: `AGENTS.md` — update heading to "eight domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)"; add a `gol/` bullet (chronological order, after `prb/`); update the "Still genuinely missing" list (`validate_gol` not enforced via pre-commit/CI, `delete_gol` stub) and the closing domain-enumeration paragraphs — depends on: Phase 3 complete — status: completed
- [x] Task 130.110: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema` regeneration — confirm `gol` appears correctly and all three commands report zero drift — depends on: Task 4.1 — status: completed
- [x] Task 130.120: Phase-end quality gate — full pre-commit/quality gate; update this README's Progress section — depends on: Task 4.2 — status: completed

#### Phase 140: Final cross-cutting verification

- [x] Task 140.100: Final verification pass — walk every ACC-001..008 and confirm each is satisfied with concrete evidence (including a live `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests); run the full quality gate (ruff format/check, pylint advisory, vulture, unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift checks) end to end; set feature status to `done` — depends on: Phase 1-4 complete — status: completed

## Progress

### Current Status

**As of 2026-08-26**: Feature complete — all five phases done, all eight
acceptance criteria verified PASS (see annotated Acceptance Criteria
above), full quality gate green (1609 tests, coverage 98%, ruff
format/check clean, vulture clean, pylint 8.92/10 advisory — identical to
the Phase-4 baseline, no regressions). Phase 5's final verification walk
included a live, non-mocked `create_gol`→`get_gol`→`update_gol`→
`set_status_gol`→`get_gol`→`list_gol` run against a temp docs directory
(not just unit tests), `list_gol` paging confirmed live with 26 documents
(default 25 / cap 100 / `truncated` boundary), the MCP registration counts
(74 tools / 20 resources / 17 prompts) confirmed on the real `server.mcp`
instance, and ACC-007's real `uv build --wheel` + non-editable
scratch-venv install (scratch venv, `dist/`, and `build/` removed
afterward — `git status` shows no residue). GitHub issue #18 ("Add
artifact type Goal (GOL)") is filed and open; the feature is ready for
review/merge and the issue can be closed when the PR merges.

### Blockers

None.

### Updates

<!-- Recent -->

#### 2026-08-26T07:23:26.000Z - Update (Phase 5: Final cross-cutting verification — feature complete)

Completed Task 5.1, the final task of the feature. Walked every ACC-001..008 with concrete evidence (recorded inline in the Acceptance Criteria section above, each now checked `[x]`). This phase modified no source/test/doc/config/data file — the only write is this README (frontmatter `status: done`, the ACC annotations, the Task 5.1 flip, and these Progress updates). ACC-001/002/003 (schema/models/parser): `docs/gol_schema.json`'s `"$comment": "v1"` (line 2) and 2020-12 `"$schema"` (line 403) confirmed; live byte-exact round-trip of `gol_reference.md` through `parse_gol` (2030 == 2030 body bytes); live minimal-doc (all six optionals `None`) and closed-set (`status: pending` → `ValidationError` naming the seven allowed values, model- and parse-level) demos; `test_parser.py` (10 tests), `test_frontmatter.py` + `test_body.py` (41 tests) re-run green. ACC-004/005 (tools/resources): live `mcp.list_tools()/list_resources()/list_prompts()` on the real `server.mcp` instance — 74/20/17 totals, exactly 10 gol tools / 3 gol resources / 2 gol prompts; `docs/MCP.md` citations match (header line 6, 10 `### Tool:` entries, 3 resource rows, no `/{id}`, no `/list`); `test_list_gol.py` (11 tests) re-run green and paging re-confirmed live with 26 docs in a temp `SPECMGR_DOCS_DIR` (`total=26`/default `max_results=25`/`truncated=True`; `max_results=100` → 26 items/`False`; `offset=25` → 1 item/`False`, no page overlap); the three gol resources resolved live (`schema` dict with top-level `required: ['frontmatter', 'body']`, example 2162 chars, template 1201 chars), `tests/gol/resources/` (13 tests) green. ACC-006 (prompts): both packaged instruction files read in full (step headers quoted in the annotation); the narrated `create_gol`/`update_gol` flows walked end to end with the real tool functions in a temp `SPECMGR_DOCS_DIR` — `list_gol` empty (no near-duplicate) → `create_gol` (draft, id `07331e39-…`) → `get_gol` → `update_gol` (adds the absent `## Notes`, carries forward every unchanged section, `updated` bumped) → `set_status_gol(…, "accepted")` → final `get_gol`/`list_gol` show `accepted`; both prompt functions resolved their packaged narration live with `$topic`/`$id` substituted (3554 / 2567 chars); `tests/gol/prompts/` (22 tests) and `tests/gol/tools/test_integration.py` (2 tests) re-run green. ACC-007 (packaged data from a real install): `uv build --wheel` → `dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl`; `unzip -l` confirms all five `gol/data/*` files + every gol module (35 entries under `biz/dfch/specmgr/gol/`); non-editable install with the mcp extra into a scratch venv under `/tmp/opencode/`; `inspect.getfile` proves the module loads from the venv's `site-packages`, and `get_gol_example()`/`get_gol_template()`/`gol_schema()` resolve real packaged content from there (see Notes for the venv specifics). ACC-008 (doc generation drift): `specmgr docs`/`mcp-docs`/`schema` (generic + `--type gol --output-dir …/gol/data`)/`adr-toc`/`coverage-badge` all re-run exit 0, every generated file reported "unchanged", `git diff --exit-code -- docs/` clean (no test files added this phase, so `docs/GENERATED.md`'s test-file count is unchanged); `AGENTS.md`'s eight-package heading (line 5) + `gol/` bullet (line 81) confirmed from Phase 4. Ran the full quality gate one final time: `ruff format --check` (1011 files already formatted), `ruff check` (all passed), `pylint` (advisory; 8.92/10 — "previous run: 8.92/10, +0.00", identical to the Phase-4 baseline; no `.py` file changed this phase), `vulture src/ whitelist.py --min-confidence 60` (exit 0, no output), full suite via `coverage run` (**1609 tests**, 54.6s, OK) followed by `specmgr coverage-badge` (98%, `docs/coverage.svg` byte-unchanged). Set this README's own frontmatter `status: in-progress` → `status: done` as Task 5.1's own required action; every phase and every acceptance criterion is now checked off. Next: Feature complete — ready for review/merge; issue #18 can be closed when the PR merges. Notes: ACC-007 venv specifics: the system `python3` is 3.10.12, below the project's `requires-python = ">=3.11"`, so the scratch venv was created with `uv venv --python 3.13` (uv-managed CPython 3.13.13) and the wheel installed with `uv pip install --python /tmp/opencode/gol-scratch-venv/bin/python "dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl[mcp]"` (network to PyPI was available; the full mcp dependency tree installed). Cleanup confirmed: `rm -rf /tmp/opencode/gol-scratch-venv dist/*` plus removal of the `uv build`-created `build/` artifact dir (`build/lib` copies of the source tree); `git status` shows zero entries afterward (both `dist/` and `build/` are gitignored, `.gitignore` lines 11/13). The full-suite run's merged log carries a few lines of stray stdout after the `OK` summary (a test-spawned subprocess flushing late); the process exit code is 0 and the summary reads `Ran 1609 tests in 54.648s / OK` — no test failures. No new design decisions required this phase — purely verification, exactly as scoped.

### Decisions Made

#### 2026-08-26T07:23:26.000Z : Body `Description` is declared `description: Description | None = Field(default=None, ...)` —

a deliberate deviation from a 1:1 copy of REQ's line, where `description` has *no* default and is therefore pydantic-required (REQ's `Requirement.from_text` demonstrably fails on a document without a `## Description` section; REQ's own docstring for that section says "Mandatory"). The plan makes `Description` optional for `gol` ("a freshly created `gol` document may have zero optional sections"), so the default is mandatory here. Fixing REQ's own quirk is out of scope for this feature.

#### 2026-08-26T07:23:26.000Z : `gol_reference.md` frontmatter values:

`id: deaddead-goal-goal-goal-deaddeadgoal` (prb_reference's `deaddead-cafe-cafe-cafe-deaddeadcafe` dead-UUID pattern, `goal` in place of `cafe`), `status: accepted` (a non-default status, so the packaged example demonstrates the closed set in action; the goal is an agreed, pursued business goal), `created`/`updated: 2026-08-25` (prb_reference's plain-`YYYY-MM-DD` style, not req_example's full-timestamp style).

#### 2026-08-26T07:23:26.000Z : Multi-item bullet lists in `gol_reference.md` (`Tags`'s three items, the `### Goals` sub-list's two items) are authored *loose* (blank line between items).

Engine behavior (documented in `MarkdownListItem`'s docstring): a `list[MarkdownListItem]` field round-trips tight → loose, while loose lists remain byte-exact. Since ACC-001/Task 1.4 require the reference doc to round-trip byte-exactly, it is authored in the engine's own canonical output form. Single-item lists (the other three sub-lists) are unaffected by tight/loose and are authored tight, matching `req_example.md`'s look.

#### 2026-08-26T07:23:26.000Z : Package-init split for Phase 1 —

`gol/models/v1/__init__.py` is created now with the Phase-1 export set (frontmatter + body classes, `__all__` alphabetical, mirroring `req/models/v1/__init__.py`'s shape) and is extended in Phase 2 (`GolDocument`, `parse_gol`, `GolSummary`, `SCHEMA_COMMENT_VERSION`); `gol/models/__init__.py` is *not* created (mirrors REQ's exact file shape — REQ has none; PRB's docstring-only one is not the pattern the plan points at); `gol/__init__.py` is *not* created (Task 3.16 owns it, and its `from . import prompts, resources, tools` line would fail while those sub-packages don't exist). `gol` is therefore an implicit namespace package until Phase 3 — imports work today and setuptools' `namespaces = true` keeps wheel packaging correct.

#### 2026-08-26T07:23:26.000Z : No `whitelist.py` entry for the Phase-2 `gol` names —

vulture sees `GolDocument`/`parse_gol`/`GolSummary` through their imports in `gol/models/v1/__init__.py` and `SCHEMA_COMMENT_VERSION` additionally through `commands/schema.py`; mirroring REQ/PRB, whose `parse_req`/`ReqSummary`/`parse_prb`/`PrbSummary` are also not whitelisted. The extended `__all__` order follows the REQ/PRB shape: `SCHEMA_COMMENT_VERSION` first, class names alphabetical, `parse_gol` last.

#### 2026-08-26T07:23:26.000Z : `docs/gol_schema.json`'s `$defs.Goal.description` prose contains the words "Characteristics"/"Level" (verbatim from the `Goal` class docstring, which documents the deliberate omissions); the schema structure itself has no such sections, fields, or RFC 2119 values.

The Phase-1 `body.py` docstring was not reworded (outside this phase's file surface) — if a character-level absence is ever required, that is a one-line docstring edit to make together with its `specmgr docs` regeneration.

#### 2026-08-26T07:23:26.000Z : `gol`'s `update_gol` **prompt** takes `id: str` only —

no `instructions: str | None = None` parameter, deliberately diverging from the `update_req`/`update_prb` prompt signatures. The plan settles this in two independent places (Design Notes' bullet "`update_gol(id: str) -> str`" and the Task 3.15 guidance repeating the same signature), and its narrated flow discovers the requested change *during* the interview (step 2 shows the user which sections are present vs. empty and asks via `question`), so a pre-filled "requested change" argument would be redundant. `gol/prompts/update_gol.py`'s own docstring calls out the divergence explicitly. The `update_gol` **tool** is unaffected (`(id, content)` exactly like `update_req`).

#### 2026-08-26T07:23:26.000Z : `gol_template.md`'s frontmatter uses the domain's dead-UUID `id: deaddead-goal-goal-goal-deaddeadgoal` (gol_reference's own pattern, like prb_template's `deaddead-b00b-...`) with plain `2026-08-26` dates (gol_reference's plain-date style), rather than req_template's generic `deaddead-dead-dead-dead-deaddeaddead` id and full-timestamp dates.

Both styles parse identically (`_stringify_metadata` coerces either); the choice keeps the packaged gol data internally consistent.

#### 2026-08-26T07:23:26.000Z : Two `AGENTS.md` domain-set enumerations beyond the four the task explicitly lists were updated, per the task's item-5 rule ("update those too IF the enumeration is about the domain set"): (a) the "Still genuinely missing" bullet "`req`/`tsk`/`qa`/`prb` each register `tools`, `resources`, and `prompts`" gained `/`gol`` (GOL registers all three, verified in Phase 3 —

without it the bullet understates the domain set); (b) the "MCP server (`server.py`)" section's parenthetical list of the domain packages imported by `server.py`'s bottom line gained `gol` (that line has included `gol` since Phase 3, so the list was factually stale). Both are minimal in-place insertions, no reflow.

#### 2026-08-26T07:23:26.000Z : The "Models location" paragraph's sentence "REQ, UC, and TSK were built *after* that refactor and each keep their schema inside their own domain package (`req/models/`, `uc/models/`, `tsk/models/`) instead" was deliberately **not** touched: it is already stale *before* this feature (it omits QA and PRB, both of which keep their schemas in-domain —

the `prb/` bullet itself says "PRB is a new domain built after the domain-first refactor, same as REQ/UC/TSK/QA"), so making it complete would mean fixing pre-existing staleness for three domains at once, which is outside Task 4.1's scope ("do not rewrite or reflow anything else in the file"). The new `gol/` bullet carries GOL's own models-location statement, so nothing GOL-specific is left unrecorded. Flagged for the orchestrator to decide separately.

#### 2026-08-26T07:23:26.000Z : No `whitelist.py` entry for any Phase-3 `gol` name —

every `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` function is import-referenced by its sub-package's `__init__.py` (`gol/tools/__init__.py` imports all ten tools by name; `gol/resources/__init__.py` and `gol/prompts/__init__.py` likewise), which vulture sees, exactly as REQ's/PRB's own MCP entry points are seen (the MCP section of `whitelist.py` holds only `version_info`). Vulture ran clean (exit 0, no output) with the new tree in place.

#### 2026-08-25T19:07:01.000Z : Type abbreviation `gol`, domain-first layout (`gol/models/v1/`, `gol/tools/`, `gol/resources/`, `gol/prompts/`, `gol/data/`) —

matches REQ/PRB precedent (schema lives inside the domain package, not top-level `models/`), since GOL is a new domain built after the domain-first refactor.

#### 2026-08-25T19:07:01.000Z : Body mirrors REQ minus `## Characteristics` —

ISO 25010 quality characteristics are a requirement-level attribute; a business goal states *what* to achieve, not *which quality dimension* it loads (user decision).

#### 2026-08-25T19:07:01.000Z : No `## Level` section —

a goal is implicitly always a MUST; RFC 2119 obligation strength is a requirement-level attribute (user decision). Consequently the only mandatory body fields are `statement` and `Source`, and `gol/models/v1/body.py` declares no `Level` class or RFC 2119 validator.

#### 2026-08-25T19:07:01.000Z : Status set = REQ's exact 7-value set `draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/`implemented` —

goals are business-level requirements, so requirement-lifecycle semantics apply (user decision), with goal-specific meanings for `implemented` (= goal reached) and `superseded` (= replaced by another goal) as spelled out in Design Notes.

#### 2026-08-25T19:07:01.000Z : `Related Artifacts` carries all four sub-lists, identical to REQ (`Requirements`/`Decisions`/`Goals`/`Acceptance Criteria`), each optional and opaque free text —

the `### Goals` sub-list cross-references peer/superseding goals (user decision).

#### 2026-08-25T19:07:01.000Z : `update_gol` is a single whole-body replace tool (REQ/PRB convention), not an ADR-style `update_section`/option-style granular tool —

the latter is currently ADR-specific code (ADR 71fd95d7), same decision as feat-16's for `prb`. Individual sections remain addressable by their fixed heading text within the whole-body markdown.

#### 2026-08-25T19:07:01.000Z : `list_gol` is a paged tool from day one per ADR ec9f5262 —

no `specmgr://gol/list` resource, no resource-then-convert history.

#### 2026-08-25T19:07:01.000Z : `gol_example.md` is drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` —

the exact goal `req_example.md`'s `### Goals` sub-list already cross-references — so the two packaged examples read coherently side by side; it reuses `gol_reference.md`'s content verbatim (feat-16's own `prb_example.md`/`prb_reference.md` precedent).

#### 2026-08-25T19:07:01.000Z : Folder name `feat-18-goal` (issue #18) —

GitHub number 17 was already consumed by the merged feat-16 PR, so the convention's `feat-NNN-slug` ↔ issue-number tie lands on 18.

### Related PRs / Commits

- [Issue #18](https://github.com/dfch/biz.dfch.SpecMgr/issues/18): Add
  artifact type Goal (GOL) — the issue this feature implements.
