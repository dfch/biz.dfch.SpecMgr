# History: Requirement (REQ) artifact template with characteristic assignment

#### 2026-08-15 00:00:00.000Z - (continued) Task 5.1 implemented: REQ's packaged `data/` moved out of `resources/`; feature marked `done` again

Executed Task 5.1's own todo list exactly as planned:
Moved the 3 packaged files (`git mv`) from
`src/biz/dfch/specmgr/req/resources/data/{req_example.md,req_template.md,req_schema.json}`
to `src/biz/dfch/specmgr/req/data/{req_example.md,req_template.md,req_schema.json}`;
deleted the now-empty `req/resources/data/` directory.
`req/_data.py`: `_DATA_PACKAGE` changed from
`"biz.dfch.specmgr.req.resources"` to `"biz.dfch.specmgr.req"`; module
and constant docstrings updated to the new path.
`pyproject.toml`'s `[tool.setuptools.package-data]` key renamed from
`"biz.dfch.specmgr.req.resources"` to `"biz.dfch.specmgr.req"` (patterns
unchanged).
`req/resources/__init__.py`: dropped the now-false "this sub-package
also holds `data/`" sentence.
`req/resources/req_schema.py`: docstrings updated to the new
`req/data/req_schema.json` path and `--output-dir` value.
`.pre-commit-config.yaml`'s `specmgr-schema-req-package` hook and
`.github/workflows/ci.yml`'s matching CI step: both `--output-dir`
arguments, the step title, and `::error::` messages updated to
`src/biz/dfch/specmgr/req/data`.
Tests required **zero** changes, as predicted — every test that reads
these files patches `_data`'s module-level path constants
(`_EXAMPLE_PATH`/`_TEMPLATE_PATH`/`_SCHEMA_PATH`) via
`mock.patch.object`, never a hardcoded path string. Full suite
(773 tests) still passes.
Regenerated and committed: `specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data` (unchanged content, confirming the move
is behavior-preserving), `specmgr schema` (`docs/req_schema.json`,
unchanged), `specmgr docs` (3 `docs/api/` pages updated:
`biz.dfch.specmgr.req._data.md`, `biz.dfch.specmgr.req.resources.md`,
`biz.dfch.specmgr.req.resources.req_schema.md`), `specmgr mcp-docs` and
`specmgr adr-toc` (both confirmed **no drift** — this move never
touches tool/resource/prompt registration, only where the packaged
files physically live).
`ruff format --check`/`ruff check`/`vulture` all clean.
Verified with a real, non-editable install: built the wheel
(`uv build --wheel`), confirmed the packaged data files land at
`biz/dfch/specmgr/req/data/*` (not `req/resources/data/*`) inside it,
installed the wheel into a scratch venv (`uv venv` + `uv pip install ...[mcp]`), and called `req_example()`/`req_template()`/`req_schema()`
directly against the installed package — all three resolved and
returned content correctly, confirming Task 3.8's packaged-data
guarantee survives the move.
With Task 5.1 (the one remaining open item) now complete, frontmatter
`status` moved from `in-progress` back to `done`.


#### 2026-08-15 00:00:00.000Z - (continued) Phase 5 added: Task 5.1, move REQ's packaged `data/` out of `resources/`

New **Phase 5: Cleanup** with **Task 5.1**, not-started: `req/resources/`
is explicitly the sub-package for MCP **resources**
(`@mcp.resource()` registrations) — the `data/` directory of packaged
example/template/schema files (`req_example.md`, `req_template.md`,
`req_schema.json`, added across Tasks 3.6/3.7/3.8) does not belong
nested inside it and should move to `req/data/`, a sibling of
`req/models/`, `req/prompts/`, `req/resources/`, `req/tools/`.
Planning only for now — the task's own body captures the full concrete
todo list (file moves, `_data.py`'s `_DATA_PACKAGE` anchor,
`pyproject.toml` package-data key, docstring updates in
`req/resources/__init__.py`/`req/resources/req_schema.py`, the
`specmgr-schema-req-package` pre-commit hook, the matching CI step, and
a real non-editable-install sanity check) — nothing has been moved yet.
Frontmatter `status` reverted from `done` back to `in-progress` — a new
open task exists again.


#### 2026-08-15 00:00:00.000Z - (continued) ACC-002 formalized as out of scope; feature marked `done`

Characteristics/tags filtering — the one item ACC-002 flagged as an open
gap — is now formally added to the Scope section's "Explicitly out of
scope" list, rather than left as an informal deferral only mentioned in
Task 3.9's design discussion. Assignment/retrieval (the actual REQ-002
requirement) were already fully implemented; only filtering was ever in
question.
ACC-002 checked off accordingly — with filtering now out of scope, there
is nothing left for it to verify beyond assignment/retrieval, which
already pass.
With REQ-001..005 and ACC-001..005 all checked and the full Task List
(Phases 1-4) complete, frontmatter `status` moved from `in-progress` to
`done`.


#### 2026-08-15 00:00:00.000Z - (continued) Requirements/Acceptance Criteria checklist re-synced; top-level `README.md` MCP description updated

REQ-005 and ACC-005 were still unchecked with stale "prompts/resources
not-started" wording, left over from the 2026-08-14 sync-up (before Tasks
3.5-3.19 landed). Checked both off now that the full lifecycle surface
(8 tools, 5 resources, 2 prompts) exists.
ACC-002 (characteristics/tags filtering) remains deliberately unchecked —
Task 3.9's design discussion explicitly deferred filtering rather than
implementing it, but that deferral was never formalized in the Scope
section's "Explicitly out of scope" list. This is the one open item
standing between this feature and a `status: done` frontmatter — left
as-is pending a decision on whether to formalize the deferral as
out-of-scope or actually implement filtering.
Top-level `/README.md` (project root, not this feature file) was updated
to fix its now-stale MCP capability description: the intro "Status"
blurb and "CLI Usage" section still described a single ADR-only domain
with no CLI commands beyond `version`/`mcp`; both now reflect the three
implemented domains (ADR, UC, REQ) and the handful of existing
cross-cutting CLI commands. Added a short "Supported artifact types"
list to the "MCP Server" section (ADR v1, UC v2, REQ v1) without
duplicating the full tool/resource/prompt inventory, which stays solely
in the generated `docs/MCP.md`.


#### 2026-08-15 00:00:00.000Z - (continued) Task 4.6: `specmgr mcp-docs` wired into CI as a drift-check backstop

`.github/workflows/ci.yml`: new "Make sure `docs/MCP.md` is correct" step,
placed right after the "Make sure `docs/adr/README.md` is correct" step and
before the `docs/req_schema.json` checks — grouped with its `docs`/
`adr-toc` siblings since all three share the same "regenerate, then
separate `git diff --exit-code`" shape, unlike `specmgr schema` (which
exits non-zero on drift by itself, needing no extra diff step). Gated to
`matrix.python-version == '3.13'`, matching every other doc-generation
check in this job (Python version differences in generated docstring
formatting).
This closes the one documented gap between the `specmgr-*` pre-commit
hooks and their CI counterparts (Task 4.3 added the `specmgr-mcp-docs`
pre-commit hook already; only its CI backstop was missing) — every
`specmgr-*` pre-commit hook now has a matching CI step.
Verified locally: `uv run --frozen --all-extras specmgr mcp-docs` followed
by `git diff --exit-code -- docs/MCP.md` reports no drift, confirming the
new step would pass as-is.
No code/test changes needed — `tests/commands/test_mcp_docs.py` already
covers `generate_mcp_docs()`/`mcp_docs()` directly; CI workflow wiring has
no dedicated test, same as `adr-toc`'s own CI step.


#### 2026-08-15 00:00:00.000Z - (continued) Tasks 3.21/3.22: `MarkdownSection{1..6}WithComment` opt-in mixins, `Level`/`Priority` refactored

**Task 3.21 discussion trail**: prompted by a direct question on why Task
3.20's `comment: MarkdownComment | None` field lives on `Level`/`Priority`
individually rather than on a shared base. Two proposals were evaluated
and rejected before landing on the implemented design:
**`comment` on the shared `MarkdownSection`/`MarkdownStr` ABC** (used by
ADR and UC too, not just REQ): rejected — no ADR/UC section has any
current use for it (neither domain even has a template/example
resource), so every section in every domain would carry a permanently-
unused property purely for a REQ-only need; a base-class field is also
always first in declaration order for every subclass forever
(pydantic's MRO-ordered `model_fields`), foreclosing any future section
wanting a different shape.
**A correctness bug found while tracing the proposal**: any
`MarkdownStr`-typed field, including an inherited one, disqualifies a
class from `MarkdownStr`/`MarkdownSection`'s "leaf" verbatim-`_value`-
storage path (`if not field_names: instance._value = text`) — `_get_field_names()`
iterates `cls.model_fields`, which include inherited fields. So a
currently-bare/leaf section (e.g. `Description`, `MoreInformation`,
`Notes` — free-form prose, zero declared fields today) that merely
inherited a base-class `comment` field would break on any real content:
`_value` would hold only the heading text (not the body), the body
would go unmatched by anything, and `MarkdownStr.from_text`'s own
`assert remaining_text == ""` would raise. Confirmed by tracing
`MarkdownSection.from_text`/`MarkdownStr.from_text`/`_get_field_names`
together, not just by inspection.
**Resolution**: an opt-in `MarkdownSection{N}WithComment` mixin per
level (N=1..6), documented as "must be paired with >=1 other declared
field" — exactly `Level`/`Priority`'s existing shape, generalized.
Zero impact on ADR/UC (they simply never inherit from it), and safe by
construction: the constraint is a class-shape requirement, not
something every section is forced to carry.
**Task 3.22 implementation**: 6 new `models/md/markdown_section{1..6}_with_comment.py`
files, mirroring the one-file-per-level `markdown_sectionN.py` convention.
Each `MarkdownSection{N}WithComment(MarkdownSection{N})` declares
`comment: MarkdownComment | None` plus a hard runtime guard
(`assert len(cls._get_field_names()) > 1` in both `get_extent` and
`from_text`) matching the codebase's existing guard idiom
(`MarkdownComment`'s own leaf-only `assert not cls._get_field_names()`),
rather than a novel `__pydantic_init_subclass__` hook (verified available
in pydantic 2.13 with `model_fields` already populated, but not used
anywhere else in this codebase, so rejected for consistency). Class
docstrings kept short (~250 chars), same Task 2.6 concern (inlined into
every schema `$defs` entry that references the class).
`req/models/v1/body.py`: `Level`/`Priority` now inherit from
`MarkdownSection2WithComment` instead of `MarkdownSection2`, dropping
their own duplicated `comment` field *declaration* -- each still
re-declares/overrides `comment`'s `Field(description=...)` with its own
more specific wording ("e.g. listing the allowed obligation-strength
values" / "e.g. describing the numeric range"), so no information was
lost. Purely a refactor: `value`/its validators untouched.
All 6 new classes exported from `models/md/__init__.py`.
Tests: new `tests/models/md/test_markdown_section_with_comment.py` (4
tests, looping across all 6 levels via `subTest`): a well-formed fixture
(comment + `value` field) round-trips with/without a leading comment; a
malformed comment-only fixture raises on both `get_extent` and
`from_text` — mirrors `test_markdown_comment.py`'s
`_InvalidCommentWithField` fixture-to-prove-a-guard pattern. 773 tests
project-wide (up from 769), no regressions -- confirmed the refactor is
fully behavior-preserving (identical `docs/req_schema.json` output,
byte-for-byte, since `Level`/`Priority` keep their own overridden
descriptions).
`ruff format --check`/`ruff check`/`vulture` clean; `specmgr schema`
reports `docs/req_schema.json` **unchanged** (mixin classes are never
directly referenced as a field type anywhere, so they never get their
own `$defs` entry — only `Level`/`Priority`'s own generated schema
entries matter, and those are identical to before); `specmgr docs`
regenerated (6 new module pages); `specmgr mcp-docs`/`specmgr adr-toc`
confirmed no drift (this change never touches either surface).


#### 2026-08-15 00:00:00.000Z - (continued) Task 3.20 implemented: `models.md.MarkdownComment` + inline-HTML-comment permission; `req_template.md` parse-validity fixed

**Root-caused the actual break first**: `req_template.md` (Task 3.7's
template file, already committed) currently fails `parse_req` outright —
not because of raw-HTML rejection (an `"html_block"` comment starting
with `<!--` was already permitted before this change), but because
`Level`/`Priority`'s `value: MarkdownParagraph` field only ever expects a
single paragraph, and the template's own leading `<!-- ... -->` comment
line (mdformat-normalized onto its own separate block, blank-line
separated from the value paragraph that follows) is an *extra* sibling
block neither field declared or expected. Confirmed via `parse_req`
raising `Level.value: expected MarkdownParagraph, found no match` before
any of this change's code existed.
**New `models/md/markdown_comment.py`**: `MarkdownComment`, a leaf-only
`MarkdownStr` subclass matching a single self-closing `"html_block"`
token whose content starts with `<!--` — mirrors `MarkdownCodeBlock`'s
established single-token (`nesting == 0`) leaf pattern exactly
(`get_extent`/`from_text`/`text`). Registered in `models/md/__init__.py`.
Its class docstring was kept deliberately short (~400 chars, not the
~2k-char first draft) since it gets inlined into every schema `$defs`
entry that uses it — same Task 2.6 concern this feature already applied
to `MarkdownListItem`/`MarkdownParagraph`.
**Fixed the actual template break** by declaring an optional
`comment: MarkdownComment | None = Field(default=None, ...)` field ahead
of `value` on both `Level` and `Priority` (`req/models/v1/body.py`) — the
existing generic `MarkdownStr.from_text` field-distribution loop already
supports an `Optional[X]` field anywhere in declaration order (consumes
it if present, skips it untouched otherwise), so no engine change was
needed for this part. `req_template.md` and the feature's own
`req_reference.md` (which has no comment) both now parse successfully via
`parse_req` — confirmed directly, not just via a new unit test.
**Also implemented the task's own literal ask**: extended
`models/md/_markdown.py`'s `_assert_no_raw_html` to permit an
`"html_inline"` token whose content starts with `<!--`, the same
exception `"html_block"` already had (`_ALLOWED_RAW_HTML_PREFIX`
constant, shared by both checks) — confirmed empirically first that
`mdformat`/`markdown-it` tokenize `MUST <!-- ... -->` as a single
paragraph with a nested `html_inline` child, so this permission alone
would have made that same-line form parseable too. **This is not what
fixes `req_template.md`**, though (that file uses the block form, not
inline) — it is independently useful (e.g. a future inline annotation
mid-sentence elsewhere) and is exactly what Task 3.20's own wording
asked for, so it was implemented alongside the `MarkdownComment` fix
rather than skipped. A non-comment inline tag (e.g. `<b>bold</b>`) is
still rejected exactly as before.
Tests: `tests/models/md/test_markdown_comment.py` (8 new cases:
`get_extent`/`from_text`/`text`/leaf-only-guard, mirroring
`test_markdown_code_block.py`'s structure) and two new cases added to
`tests/models/md/test_markdown_html_rejection.py` (inline comment
permitted, non-comment inline tag still rejected) — 769 tests
project-wide (up from 746 after Task 3.19), no regressions. `whitelist.py`
gained `comment` (a pydantic field name vulture otherwise flags as
unused, same reason `priority`/`source`/etc. are already listed).
`ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs`/
`specmgr mcp-docs`/`specmgr adr-toc` regenerated (1 new module page:
`models.md.markdown_comment`; `docs/MCP.md`/`docs/adr/README.md` show no
drift, as expected — this change never touches either surface);
`specmgr schema` regenerated both `docs/req_schema.json` and the packaged
`req/resources/data/req_schema.json` copy (Level/Priority gained an
optional `comment` property, a new `MarkdownComment` `$defs` entry was
added).
**Decision**: chose the `MarkdownComment`-field approach over the task's
originally-sketched "edit `req_template.md` to the same-line inline form,
then make `_LEVEL_PATTERN`/`_PRIORITY_PATTERN` tolerate a trailing
comment via string-stripping" alternative — the field approach fixes the
template that is *actually* on disk today without touching regex
validators at all, and generalizes to any future section wanting an
optional explanatory comment, not just `Level`/`Priority`. See Decisions
Made.


#### 2026-08-15 00:00:00.000Z - (continued) Task 3.19 implemented: `req/prompts/create_req.py` + `update_req.py`

New `req/prompts/` sub-package (first for REQ — until now only `tools`/
`resources` existed), mirroring `adr/prompts/`'s one-module-per-prompt
split: `create_req.py` (`@mcp.prompt(name="create_req")`) and
`update_req.py` (`@mcp.prompt(name="update_req")`), both returning plain
instructional text, not a tool call.
`create_req(topic: str) -> str` narrates: check `specmgr://req/list` for
an existing duplicate first; recap the body-only markdown structure
(H1 + statement, `Description`, `Characteristics`, `Level`, `Priority`,
`Tags`, `Source`, `Related Artifacts`, `More Information`, `Notes`);
gather the required fields from the user; fetch
`specmgr://req/template`/`specmgr://req/example` as a starting point and
`specmgr://req/schema` to confirm field names/constraints; call
`create_req(content)`; optionally dry-run via
`validate_req(content, full=False)` first. Unlike `adr.prompts.create_adr`,
there are **no** frontmatter-related parameters to pre-fill — `create_req`
the tool builds `id`/`type`/`status`/`created`/`updated`/`version`
entirely itself, so the prompt's only parameter is `topic`.
`update_req(id: str, instructions: str | None = None) -> str` narrates:
read `specmgr://req/{id}` first (never assume prior state); ask the user
if no change was specified; route a body change through
`update_req(id, content)` (a whole-body replace — carry forward every
section not being changed) and a status change through
`set_status_req(id, status)` instead, since `update_req` never accepts or
changes `status`; check `specmgr://req/schema` before drafting the
replacement body; optionally dry-run via `validate_req(content, full=False)` first. Simpler than `adr.prompts.update_adr`'s tool-mapping
table — REQ's lifecycle surface (Task 3.9's design) has no
`update_frontmatter`/`option_*` equivalent, just the one whole-body-replace
tool plus the one status-change tool.
Registered in `req/prompts/__init__.py`, `req/__init__.py` (now imports
`prompts` alongside `resources`/`tools`), and `server.py`'s prompts
docstring block.
Tests: `tests/req/prompts/test_create_req.py` (6 tests) and
`tests/req/prompts/test_update_req.py` (7 tests), mirroring
`tests/adr/prompts/test_create_adr.py`/`test_update_adr.py`'s own
assertion style (topic/id interpolation, resource/tool-name mentions,
tool-sequence ordering, optional-argument placeholder text) — 759 tests
project-wide (up from 746), no regressions. `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr docs`/`specmgr mcp-docs`
regenerated (3 new module pages: `req.prompts`, `req.prompts.create_req`,
`req.prompts.update_req`; `docs/MCP.md` now lists both new prompts);
`specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this
task never touches either artifact).
**Task 3.20 deliberately not started** — unrelated scope (a
`models/md/_markdown.py` inline-HTML-comment parsing fix for Task 3.7's
template), explicitly excluded from this change per direct instruction.


#### 2026-08-15 00:00:00.000Z - (continued) Phase 4 implemented: `docs/MCP.md` auto-generated MCP server reference (`commands/mcp_docs.py`, cross-cutting — all domains, not REQ-specific)

New `commands/mcp_docs.py`: `generate_mcp_docs()` + `mcp_docs()` Typer entry
point — introspects the live `biz.dfch.specmgr.server:mcp` instance at
runtime via its public `list_tools()`/`list_resources()`/
`list_resource_templates()`/`list_prompts()` methods (async, driven via
`asyncio.run`), **not** static `ast` parsing (contrast `commands/docs.py`)
— so the emitted reference can never drift from what the server actually
registers. Writes a single `docs/MCP.md`: a summary/table-of-contents
header, then one indexed `Name | Description` table plus one
`### <Kind>: <name>` detail subsection per kind (Resources, Resource
Templates, Tools, Prompts). Tool parameter tables (`_tool_parameters`/
`_schema_type_str` helpers) only unpack each tool's top-level
`properties`/`required` — `$ref`s resolve to the referenced definition's
bare name rather than inlining the full, often-paragraphs-long nested
Pydantic model docstring from `$defs`.
**Headings are kind-prefixed** (`### Tool: create_adr` vs.
`### Prompt: create_adr`), not bare names — `create_adr` exists as both a
tool and a prompt name; bare headings would collide into duplicate
anchors that only GitHub's own undocumented `-1`/`-2`/... disambiguation
would resolve, which `_slugify` deliberately does not try to reproduce.
`mcp-docs` registered as a new Typer command (`app.command()(mcp_docs)`
in `cli.py`, `from .mcp_docs import mcp_docs` in `commands/__init__.py`)
— Typer's automatic underscore-to-hyphen conversion gives
`specmgr mcp-docs`, matching `adr-toc`/`coverage-badge`'s existing
precedent (no explicit `name=` needed).
New `specmgr-mcp-docs` local pre-commit hook (`.pre-commit-config.yaml`,
placed directly after `specmgr-docs`): regenerates `docs/MCP.md`, then
`git diff --exit-code`s it — standard formatter-hook UX, matching every
other `specmgr-*` hook. **Trigger scope is `^src/.*\.py$`** (the same
broad pattern as `specmgr-docs`), not a narrower
`adr/general/req/uc/resources`-only pattern — a tool's generated
parameter schema also depends on the shared `models/` package (e.g. a
field added to `AdrBody` changes `create_adr`'s emitted schema without
touching any `adr/tools/*.py` file), so a narrower trigger risked a
silently-missed regeneration; see Decisions Made.
`README.md`'s "MCP Server" section had a **stale, hand-maintained**
`Kind | Name(s) | Description` table listing only `specmgr://version` and
the ADR tools/resources — REQ, UC, and `general`'s `mdformat` tool were
entirely absent, exactly the drift this phase exists to prevent. Replaced
with a short prose summary plus a bolded pointer to `docs/MCP.md` as the
single, always-current source of truth.
Tests: `tests/commands/test_mcp_docs.py` (16 tests, mirroring
`test_docs.py`'s "exercise the actual Typer entry point, not just private
helpers" approach) — covers both `--output` and default-path branches,
output determinism across two calls, unique anchors across kinds sharing
a bare name, and all three helper functions (`_schema_type_str`,
`_tool_parameters`, `_slugify`). **Regression guard included**:
`test_default_output_resolves_under_repo_root_not_src` — an earlier draft
of `_DEFAULT_OUTPUT` resolved one `.parent` too shallow
(`src/docs/MCP.md` instead of the repo-root `docs/MCP.md`), caught by
manually running the generated pre-commit hook command during
verification, then locked in as a permanent regression test rather than
left as a one-off manual fix.
Full verification: `ruff format --check`/`ruff check` clean, `pylint`
only advisory-level warnings (same categories already present in sibling
`docs.py`/`test_docs.py`, not a regression), `vulture` clean, full suite
746 tests project-wide (up from 730), no regressions.
**No CI backstop yet** for `specmgr mcp-docs` (`specmgr docs`/
`specmgr adr-toc` both already have one in `.github/workflows/ci.yml`'s
Python-3.13-only job; `mcp-docs` does not yet) — tracked as the
still-open Task 4.6 rather than silently left undocumented.
**Caution for whoever commits this work**: while verifying with
`pylint`, `git add -A` was run once, which also staged unrelated,
already-in-progress Phase 3 work in this same feature (`req_get.py`/
`req_list.py`/`summary.py`/associated tests/this file itself) that
predates this phase — immediately caught and reverted via `git reset`
(nothing was committed), but noted here since `docs/MCP.md`/
`docs/GENERATED.md`/`docs/api/*` were regenerated afterward and now
reflect a mix of both this phase's and Phase 3's concurrent changes (by
design for `docs/MCP.md`, which always reflects whatever the live server
currently has registered — it correctly picked up
`specmgr://req/list`/`specmgr://req/{id}` from Phase 3 too).


#### 2026-08-15 00:00:00.000Z - (continued) Tasks 3.17/3.18 implemented: `specmgr://req/{id}` and `specmgr://req/list` resources

New `req/models/v1/summary.py`: `ReqSummary` (`id`/`title`/`status`/`filename`),
mirroring `models.adr.v1.summary.AdrSummary` field-for-field; re-exported from
`req/models/v1/__init__.py`.
New `req/resources/req_get.py` (`@mcp.resource("specmgr://req/{id}")`):
`req_get(id: str) -> ReqDocument` — single-document read by id, mirroring
`adr.resources.adr_get`/`specmgr://adr/{id}` exactly (same no-cache,
re-read-per-call design via `req.tools._io.load_by_id` +
`req.tools._paths.req_base_dir`). Confirms Task 3.9's design conclusion:
id-based single-document read is a resource only in this surface — there
is no `get_req` tool.
New `req/resources/req_list.py` (`@mcp.resource("specmgr://req/list")`):
`req_list() -> list[ReqSummary]` — every requirement in the configured base
directory, unfiltered (characteristics/tags filtering, i.e. ACC-002, stays
explicitly deferred per Task 3.9's discussion). A file that fails to parse
(`AssertionError`/`pydantic.ValidationError`, the two channels `parse_req`
raises) is silently skipped, mirroring `adr.resources.adr_list`'s own
skip-on-parse-failure rule. Uses `req.tools._paths.iter_req_paths()`'s own
zero-arg shape (resolves `req_base_dir()` internally, per Task 3.11's own
literal signature) rather than passing a `base_dir` explicitly.
Registered in `req/resources/__init__.py`, `req/__init__.py`'s docstring,
and `server.py`'s resource-list docstring block.
Tests: `tests/req/resources/test_req_get.py` (2 tests: returns the full
document for a known id, raises `ReqNotFoundError` for an unknown id) and
`tests/req/resources/test_req_list.py` (2 tests: returns summaries for
every valid requirement while silently skipping a broken file, returns an
empty list when the base directory does not exist yet) — both build their
fixture documents via `create_req` (or a raw hand-written broken file)
rather than a `render_req` that doesn't exist. 730 tests project-wide (up
from 726), no regressions. `ruff format --check`/`ruff check`/`vulture`
clean; `specmgr docs` regenerated (2 new module pages:
`req.resources.req_get`, `req.resources.req_list` — `req.models.v1.summary`
has no page of its own, folded into the existing `req.models.v1` page like
every other model submodule); `specmgr schema`/`specmgr adr-toc` both
confirmed to have no drift (this task never touches either artifact).


#### 2026-08-15 00:00:00.000Z - (continued) Task 3.15 implemented: `delete_req` stub tool

New `req/tools/delete_req.py` (`@mcp.tool()`): `delete_req(id: str) -> NoReturn` —
a registered stub only, unconditionally `raise NotImplementedError("delete_req is not yet implemented")`. Never resolves or validates `id`, never touches the filesystem —
reserves the tool name/slot in the REQ lifecycle surface without committing to a
deletion strategy (soft-delete via `status`, archival, hard removal, or something else
is still undecided, per Task 3.9's design discussion).
**`structured_output=False`** passed to `@mcp.tool(...)` — `NoReturn` has no
pydantic-serializable schema (`PydanticSchemaGenerationError` at import time otherwise,
since `mcp.server.mcpserver`'s `func_metadata()` tries to derive an output schema from
the return-type annotation by default); `structured_output=False` skips that derivation
entirely instead of lying with a fake return type.
Registered in `req/tools/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s tool-list docstring line.
Tests: `tests/req/tools/test_delete_req.py` (2 tests: raises for an arbitrary id, raises
for an unknown id without ever looking it up) — 726 tests project-wide (up from 724), no
regressions. `ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs`
regenerated (1 new module page: `req.tools.delete_req`); `specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this task never touches either artifact).


#### 2026-08-15 00:00:00.000Z - (continued) Task 3.16 implemented: `validate_req` tool (Task 3.15 deliberately skipped for now)

New `req/tools/validate_req.py` (`@mcp.tool()`):
`validate_req(content: str, full: bool = False) -> bool` — a disk-free,
id-free dry run. Detects whether `content` carries a YAML frontmatter
block via `frontmatter.loads(content).metadata` (non-empty means "has
frontmatter"), the same library every parser in this codebase already
depends on.
`full=False` (default): rejects `content` with a frontmatter block via a
`ValueError` carrying a corrective message ("...pass full=True to
validate a complete document instead"), otherwise validates via
`Requirement.from_text(format_text(content))` — literally the same check
`create_req`/`update_req` already run internally on their own `content`
argument.
`full=True`: rejects `content` with *no* frontmatter block via the
symmetric `ValueError`, otherwise delegates to `parse_req(content)` (full
frontmatter + body validation, the same shape `parse_req` expects for an
on-disk file).
Like `validate_adr`, "successfully constructing the model *is* the
validation" — this function only ever returns `True`; every failure mode
(`AssertionError`/`pydantic.ValidationError`/the two `ValueError` shape
mismatches above) propagates uncaught.
Registered in `req/tools/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s tool-list docstring line.
**Task 3.15 (`delete_req` stub) explicitly skipped this round**, per
direct instruction — not implemented, task left `not-started` in the
task list (not marked done, since no design/implementation decision was
actually made for it).
Tests: `tests/req/tools/test_validate_req.py` (7 tests: valid body-only
content, valid full document, structural failure, field-validation
failure, frontmatter-present-but-full=False rejection,
frontmatter-absent-but-full=True rejection, invalid-frontmatter-under-
full=True propagation) — 724 tests project-wide (up from 717), no
regressions. `ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs` regenerated (1 new module page: `req.tools.validate_req`);
`specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this
task never touches either artifact).


#### 2026-08-15 00:00:00.000Z - Task 3.14 implemented: `set_status_req` tool

New `req/tools/set_status_req.py` (`@mcp.tool()`):
`set_status_req(id: str, status: str) -> ReqDocument` — the only path that
changes a requirement's `status`, mirroring `adr.tools.set_status` minus
its `superseded_by`-composition special case (`ReqFrontmatter.status` has
no `"superseded by ..."` pattern, just the closed seven-value set).
**Frontmatter reconstructed via `ReqFrontmatter(**fm_data)`, not
`model_copy`** — this is the reason `update_req` (Task 3.13) was also
revisited in this same change: `model_copy(update=...)` does **not**
re-run pydantic validators, so a `model_copy`-based `set_status_req` would
have silently accepted an invalid `status` value, bypassing
`ReqFrontmatter._validate_status`'s closed-set check entirely. Switched
`update_req.py` to the same `model_dump()` + mutate dict + reconstruct
pattern for consistency, even though its own `updated`-only mutation
happened to be safe under `model_copy` too (no validator on `updated`
beyond a blank-to-`None` before-mode normalizer, moot for a non-blank
timestamp) — this exactly mirrors `models.adr.v1.mutations.set_status`'s
own `fm_data = adr.frontmatter.model_dump(); fm_data["status"] = value;  AdrFrontmatter(**fm_data)` shape.
**Body is read back from disk raw, never rendered from the parsed
model**: `frontmatter.loads(path.read_text(...)).content` is re-persisted
verbatim via `write_req_file` — deliberately not `str(existing.body)`
(confirmed feasible per the Task 3.9 design discussion, but avoided here
so this tool cannot introduce any render-fidelity drift into a body it
isn't even supposed to touch).
Registered in `req/tools/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s tool-list docstring line.
Tests: `tests/req/tools/test_set_status_req.py` (5 tests: status set +
`updated` bumped + other fields preserved, body left byte-for-byte
unchanged, round-trip via `parse_req`, `ReqNotFoundError` for an unknown
id, invalid status raises `pydantic.ValidationError` and leaves the file
untouched) — 717 tests project-wide (up from 712), no regressions. `ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs` regenerated
(1 new module page: `req.tools.set_status_req`); `specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this task never touches either
artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.13 implemented: `update_req` tool

New `req/tools/update_req.py` (`@mcp.tool()`): `update_req(id: str, content: str) -> ReqDocument`.
`content` is body markdown only, same shape/validation as `create_req`
(`Requirement.from_text(format_text(content))`; `AssertionError`/
`pydantic.ValidationError` propagate uncaught, nothing written on failure).
Resolves the existing file via `req.tools._io.load_by_id` (raising
`ReqNotFoundError` for an unknown id) and preserves every frontmatter
field except `updated` — done with `existing.frontmatter.model_copy(update={"updated": now})`, so `id`/`type`/`status`/`created`/`version` are
carried over byte-for-byte from whatever is currently on disk, not
reconstructed. `status` is not settable through this tool at all (see
the still-not-started Task 3.14, `set_status_req`).
**New `req/tools/_lock.py`** (`req_lock`), ported unchanged (aside from
naming) from `adr.tools._lock.adr_lock` — added because `update_req`
introduces this codebase's first REQ read-modify-write mutation, exposed
to the same lost-update race `adr_lock`'s own docstring describes;
deliberately **not** generalized into `general.tools` alongside Task
3.10's `_doc_paths.py`, since a lock is a mutation-time correctness
primitive Task 3.9's design discussion never actually recorded (unlike
the id → path lookup plumbing, which was explicitly called out as
shared). The whole `load_by_id` → mutate → `write_req_file` sequence in
`update_req` runs under `with req_lock(id):`.
**Refactored `create_req.py`**: the frontmatter+body file-composition
logic (`frontmatter.Post(...)` + `frontmatter.dumps(...)` + trailing-
newline normalization) was factored out of `create_req.py`'s own
previously-private `_write_req_file` into a new, shared
`req/tools/_write.py::write_req_file` — used by both `create_req` and
`update_req` now, instead of `update_req` duplicating it. Deliberately
**not** added to `req/tools/_io.py` (which stays read-only, per Task
3.11's own docstring ruling out a `write_req`/`render_req` there, since
neither tool ever renders a body back out from a parsed model).
**Timestamp precision widened to microseconds**: both `create_req` and
`update_req` now use `datetime.now().isoformat(timespec="microseconds")`
(was `timespec="seconds"` in the original Task 3.12 entry below) so two
calls in quick succession — e.g. a `create_req` immediately followed by
an `update_req` in the same test — get distinguishably different
`created`/`updated` values without an artificial `time.sleep()`. Still
ISO 8601 per ADR 23a14195, which explicitly permits fractional seconds.
Registered in `req/tools/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s tool-list docstring line.
Tests: `tests/req/tools/test_update_req.py` (5 tests: preserves
id/type/status/created/version while bumping `updated`, round-trips via
`parse_req`, raises `ReqNotFoundError` for an unknown id, structural
failure leaves the file untouched, field-validation failure leaves the
file untouched), `tests/req/tools/test__write.py` (2 tests: round-trip,
exactly-one-trailing-newline), `tests/req/tools/test__lock.py` (3 tests,
mirroring `tests/adr/tools/test_lock.py` exactly: same-id serialization,
cross-id concurrency, reentrant-safe sequential acquisition) — 712 tests
project-wide (up from 702), no regressions. `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr docs` regenerated (3 new module
pages: `req.tools.update_req`, `req.tools._write`, `req.tools._lock`);
`specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this
task never touches either artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.12 implemented: `create_req` tool

New `req/tools/create_req.py` (`@mcp.tool()`): `create_req(content: str) -> ReqDocument`.
`content` is body markdown only (no frontmatter block) — validated via
`Requirement.from_text(format_text(content))`, letting `AssertionError`/
`pydantic.ValidationError` propagate uncaught with nothing written (verified:
the requirement base directory isn't even created on a validation failure,
since `ensure_req_base_dir()` is only called after validation succeeds).
The entire frontmatter is code-generated: `id=str(uuid.uuid4())`,
`type="req"`, `status="draft"` (always), `created=updated=` a single shared
`datetime.now().isoformat(timespec="microseconds")` timestamp (ISO 8601,
per ADR 23a14195, with fractional seconds so two calls in quick succession
-- e.g. `create_req` immediately followed by `update_req`, Task 3.13 -- get
distinguishable timestamps without an artificial test sleep),
`version=models.md.CURRENT_SCHEMA_VERSION` (already
`ReqFrontmatter.version`'s own default, set explicitly here for clarity,
matching the task's literal wording).
No rendering: unlike `adr.tools.create_adr` (which renders `AdrBody` back
out via `render_adr`), the caller's `content` is embedded byte-for-byte via
`frontmatter.Post(content=content, **frontmatter_.model_dump())` +
`frontmatter.dumps(...)` — a small private `_write_req_file` helper local to
this module, **not** added to `req/tools/_io.py`, since that module's own
docstring (Task 3.11) explicitly rules out a `write_req`/`render_req` there.
One caveat inherent to `python-frontmatter`'s `YAMLHandler`, not special-cased
here: trailing whitespace on `content` is stripped by `frontmatter.dumps`
(confirmed interactively) — "byte-for-byte" means "not re-rendered from the
parsed model", not a literal guarantee against this one library-level
normalization, consistent with every other frontmatter-writing tool in this
codebase (`general.tools.mdformat`, `adr.tools._io.write_adr` use the same
library).
Filename: `f"req-{new_id}-{slugify(body.text)}.md"` — `slugify` imported
directly from `general.tools._doc_paths` (Task 3.10), not re-exported
through `req.tools._paths`. `body.text` (not `body.title` — `Requirement` is
a `MarkdownSection1`, not a plain-field model like `AdrBody`) is the H1
heading text, exposed via `MarkdownSection.text`'s composite-case branch.
Registered in `req/tools/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s tool-list docstring line.
Tests: `tests/req/tools/test_create_req.py` (6 tests: frontmatter fields,
expected filename, round-trip via `parse_req`, base-dir auto-creation,
structural failure writes nothing, field-validation failure writes
nothing) — 702 tests project-wide (up from 696), no regressions. `ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs` regenerated (1
new module page: `req.tools.create_req`); `specmgr schema`/`specmgr adr-toc`
both confirmed to have no drift (this task never touches either artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.11 implemented: `req/tools/_paths.py` + `_io.py`, thin REQ wrappers over Task 3.10's generic module

New `req/tools/_paths.py`: `REQ_TYPE_NAME = "req"`, `ReqNotFoundError(LookupError)`
(its own class, not a subclass of `general.tools._doc_paths.DocNotFoundError`
— same non-relationship `AdrNotFoundError` has to anything generic),
`req_base_dir()`/`ensure_req_base_dir()` (thin wraps over
`doc_base_dir("req")`/`ensure_doc_base_dir("req")`), `iter_req_paths()`
(zero-arg — resolves `req_base_dir()` internally and delegates to
`iter_doc_paths`, deliberately differing from the generic module's/ADR's
own `iter_*_paths(base_dir)` shape, per Task 3.11's own literal wording),
and `find_req_path(base_dir, id_)` (delegates to
`find_doc_path_by_id(base_dir, id_, parse_req, _get_req_id)`, translating
the generic `DocNotFoundError` into `ReqNotFoundError` at the boundary).
New `req/tools/_io.py`: `read_req(path)` and `load_by_id(base_dir, id_)`,
mirroring `adr/tools/_io.py`'s shape exactly, minus `write_adr`'s
counterpart — no `write_req`/`render_req` exists or is planned, since
Task 3.9's design settled on `create_req`/`update_req` (Tasks 3.12/3.13)
persisting the caller's already-validated body text byte-for-byte rather
than rendering it back out from a parsed model.
`ensure_req_base_dir()` was added even though Task 3.11's own task text
only lists `req_base_dir()` — needed by the still-not-started `create_req`
(Task 3.12) and cheap/harmless to add now alongside its read-only sibling,
mirroring `adr.tools._paths.ensure_adr_base_dir`'s existence.
Neither module is re-exported from `req/tools/__init__.py`'s `__all__` —
both are underscore-prefixed, non-`@mcp.tool()` internal modules, matching
`adr/tools/_paths.py`/`_io.py`'s own precedent of staying unexported.
Tests: `tests/req/tools/test__paths.py` (12 tests: `req_base_dir`/
`ensure_req_base_dir` incl. env-var override and no-side-effect-on-read,
`iter_req_paths`, `find_req_path` incl. skip-on-parse-failure) and
`tests/req/tools/test__io.py` (4 tests: `read_req`, `load_by_id` incl.
not-found) — both use a small local minimal-requirement-text fixture
(mirroring `tests/req/models/v1/test_parser.py`'s own `_MINIMAL_DOC`
pattern) rather than the packaged `req_example.md`, so each test file
controls its own `id` per fixture instance. 696 tests project-wide (up
from 684), no regressions. `ruff format --check`/`ruff check`/`vulture`
clean; `specmgr docs` regenerated (2 new module pages:
`req.tools._paths`, `req.tools._io`); `specmgr schema` (both the
`docs/req_schema.json` and packaged-data invocations)/`specmgr adr-toc`
both confirmed to have no drift (this task never touches either
artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.10 implemented: generic `general/tools/_doc_paths.py` id → path lookup plumbing

New `general/tools/_doc_paths.py`: `doc_base_dir(type_name)`/`ensure_doc_base_dir(type_name)`
(root env var `SPECMGR_DOCS_DIR`, default `docs`, per-type subdirectory
`{root}/{type_name}/`), `iter_doc_paths(base_dir)`, `find_doc_path_by_id(base_dir, id_, parse_fn, get_id_fn)`, `slugify(title)` — a direct generalization of
`adr/tools/_paths.py`'s shape, parameterized by `type_name` and by
caller-supplied `parse_fn`/`get_id_fn` instead of being hardcoded to
`parse_adr`/`AdrFrontmatter.id`. `DocNotFoundError(LookupError)` is a new,
doc-type-agnostic exception (the task text didn't name one explicitly, but
`find_doc_path_by_id` needs a not-found signal); `ReqNotFoundError`
(Task 3.11) is expected to be its own separate class, not a subclass, same
relationship as `AdrNotFoundError` has to nothing generic today.
`find_doc_path_by_id` skips a file that fails to parse by catching
`(AssertionError, ValueError)` around `parse_fn(...)` — deliberately
narrower than a bare `except Exception`, but wide enough to cover every
parser error type in this codebase today: `AdrParseError` (a `ValueError`
subclass) and `pydantic.ValidationError` (also a `ValueError` subclass) for
ADR, plus the bare `AssertionError`/`pydantic.ValidationError` pair
`parse_req` raises for REQ (per Task 2.2's docstring) — no dedicated
`ReqParseError` exists.
`slugify` was ported unchanged except for its empty-title fallback
(`"doc"` instead of ADR's `"adr"`, since this module is no longer
ADR-specific).
**ADR left untouched, as specified**: `adr/tools/_paths.py` still has its
own `SPECMGR_ADR_DIR`/`DEFAULT_ADR_DIR`/`AdrNotFoundError`/`adr_base_dir`/
etc.; nothing there was changed or made to delegate to the new module.
Migrating ADR onto this shared module remains optional future cleanup.
Not re-exported from `general/tools/__init__.py`'s `__all__` — an
underscore-prefixed, non-`@mcp.tool()` internal module, matching
`adr/tools/_paths.py`'s own precedent of staying unexported.
Tests: `tests/general/tools/test__doc_paths.py` (20 tests: `slugify`,
`doc_base_dir`/`ensure_doc_base_dir` incl. env-var override and
no-side-effect-on-read, `iter_doc_paths`, and `find_doc_path_by_id`
including a second, independent `parse_fn`/`get_id_fn` pair to prove
genericity) — uses small in-test fake parse functions/doc objects rather
than importing `models.adr`/`models.req`, keeping this test file decoupled
from either concrete doc type. 684 tests project-wide (up from 664), no
regressions. `ruff format --check`/`ruff check`/`vulture` clean; `specmgr docs` regenerated (1 new module page: `general.tools._doc_paths`);
`specmgr schema`/`specmgr adr-toc` both confirmed to have no drift (this
task never touches either artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.9 design discussion completed: lean, generic, id-based REQ lifecycle (Tasks 3.10-3.20 queued); no ADR-style granular section tools

Design-only entry (no code yet) — resolves Task 3.9 ("discuss what is useful for this artifact type") by working through the full ADR-vs-REQ-vs-UC tooling comparison and a token/effort-vs-benefit trade-off, rather than mechanically extending ADR's tool count to REQ.
**Rejected granular section-mutation tooling** (ADR-style `update_section`/`option_*`) **for REQ**: `req_reference.md` is 64 lines — a full requirement document is roughly one screen of markdown, not a multi-page ADR. The schema/example/template/LLM combination is already good enough for reliable whole-document authoring, every validation failure (granular or whole-document) already reports the offending field via the pydantic error message, and — critically — REQ has no ADR-style *derived* section (`## Pros and Cons of the Options`, computed from the dynamic `options` list) that only tool-mediation could keep in sync. Granular tooling's ongoing maintenance cost (a `_SECTION_KEYS`/renderer-table entry per field, kept in sync by hand) isn't bought back by a real benefit here. This conclusion is explicitly **not** REQ-specific reasoning generalized carelessly — it was re-examined once UC (described as "MUCH larger") was raised as a counter-example, and held: the design below is generic/reusable, not a REQ-only shortcut.
**Verified render feasibility, then made it moot anyway**: confirmed `MarkdownSection.__str__()` (inherited by `Requirement`) already does a full, self-validating structural round-trip (`validate_heading_structure`'s own `model_validator` calls `str(self)` and re-tokenizes it on every construction) — so a `render_req` would have been cheap to build. Turned out not to matter: the final `create_req`/`update_req` design never renders the body from the parsed model at all — the caller's own already-validated markdown text is persisted byte-for-byte; only the small, code-constructed frontmatter YAML block is ever (re)generated. This sidesteps the render-fidelity question entirely rather than solving it.
**Settled the generic lifecycle surface** (detailed in Tasks 3.10-3.20): `create_req`/`update_req` accept **body-only** `content` (no frontmatter block) — every frontmatter field is either MCP-owned (`id`/`created`/`updated`/`version`/`type`) or fixed (`status="draft"` on create); `status` is only ever changed via a new, narrow `set_status_req(id, status)` tool, mirroring ADR's `set_status`. `delete_req(id)` is a registered stub that always raises `NotImplementedError` — reserves the name without a governance/soft-delete decision. `validate_req(content, full=False)` is a disk-free, id-free dry run: `full=False` (default) validates body-only content (literally the same check `create_req`/`update_req` run internally); `full=True` validates a complete document (frontmatter + body, matching `parse_req`'s file-based contract). Both directions of the shape mismatch get a clear `ValueError` (frontmatter found when none expected, or vice versa) via `frontmatter.loads(content).metadata` presence/absence — reusing the same `python-frontmatter` library every parser in this codebase already depends on, rather than a hand-rolled `startswith("---")` heuristic.
**READ is a resource, not a tool, everywhere in this surface**: `specmgr://req/{id}` (single document) and `specmgr://req/list` (`ReqSummary`, unfiltered — characteristics/tags filtering, i.e. ACC-002, stays explicitly deferred) replace the earlier considered `get_req` tool. Every other verb (create/update/status/delete/validate) is a tool. Flagged, not yet decided: whether ADR's redundant `get_adr` tool (which duplicates `specmgr://adr/{id}`) should eventually be retired in favor of the resource alone — deferred as optional future ADR cleanup, out of scope here.
**Generalized the id -> path lookup plumbing** rather than copy-pasting `adr/tools/_paths.py` a second time: a new shared module under `general/` (already the home of cross-cutting, dependency-light code like `mdformat`), parameterized by doc-type name, backed by one root env var (`SPECMGR_DOCS_DIR`, default `docs`) with a per-type subdirectory (`docs/req/`, later `docs/uc/`) — justified by already knowing of three consumers (ADR, REQ, UC) rather than speculative generalization. **ADR is deliberately left on its own `SPECMGR_ADR_DIR`/`docs/adr` for this pass** — migrating it is optional future cleanup, not bundled into REQ's work. Filenames follow ADR's scheme: `req-{id}-{slug}.md`.
**Found (but did not yet fix) a small, separately-tracked `models/md` gap**: `_assert_no_raw_html` in `models/md/_markdown.py` already permits HTML *block* comments (`<!-- ... -->` on its own line — a `REQ-005`-labeled exception already in the code) but unconditionally rejects `html_inline` comments. This explains Task 3.7's known template-annotation breakage (the comment became a second standalone paragraph, tripping `Level`/`Priority`'s single-paragraph check) — the actual fix is narrow (also exempt `<!--`-prefixed `html_inline` content) and the correct placement is *inline on the same line as the value*, not a separate paragraph. Queued as Task 3.20, to be coordinated with `feat-5-md-model-parser` per this project's established "downstream feature triggers a fix in the closed engine" precedent.
Explicitly out of scope for now (raised and set aside during the discussion): characteristics/tags filtering (ACC-002, already deferred), migrating ADR onto the new shared path plumbing, and retiring ADR's `get_adr` tool in favor of its resource.
**No implementation in this entry** — Tasks 3.10-3.20 are all `not-started`; this entry records the design/rationale only, per explicit instruction to write the plan without starting implementation.


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.8 implemented: `specmgr://req/schema` now reads a packaged-data copy, not `docs/req_schema.json` directly

**No new copy logic in `commands/schema.py`**: the existing, fully generic
`specmgr schema --type req --output-dir <dir>` (already covered end-to-end
by `tests/commands/test_schema.py`) is simply invoked a **second** time
against `src/biz/dfch/specmgr/req/resources/data/` -- one new, committed
build artifact (`req/resources/data/req_schema.json`), zero new generation
code. `docs/req_schema.json` is unchanged and still generated/committed as
before (kept per Decisions Made).
`req/_data.py` gained a third patchable constant/reader, mirroring
`_EXAMPLE_PATH`/`read_req_example_text()` exactly: `_SCHEMA_PATH` (an
`importlib.resources` `Traversable`) and `read_req_schema_text() -> str`
(returns raw JSON text; the caller `json.loads()`s it, same split of
responsibility as the example/template readers).
`req/resources/req_schema.py`'s `req_schema()` resource now calls
`json.loads(read_req_schema_text())` instead of reading
`_paths.DOCS_DIR / "req_schema.json"` directly -- the `_paths`/`DOCS_DIR`
import was removed entirely from this module. This is the actual fix:
`DOCS_DIR` only resolves from an editable/source checkout (per its own
docstring), which would silently break `specmgr://req/schema` for a real
`pip install`; the packaged copy is real package data (`pyproject.toml`'s
`"biz.dfch.specmgr.req.resources"` package-data glob extended from
`["data/*.md"]` to `["data/*.md", "data/*.json"]`), so it survives one.
**Two independent drift gates, not one chained command**: a new
`specmgr-schema-req-package` pre-commit hook and a new "Make sure
`src/biz/dfch/specmgr/req/resources/data/req_schema.json` is correct" CI
step (Python-3.13-only, same as the existing `docs/req_schema.json` step)
each just run the second `specmgr schema` invocation and rely on its own
exit code -- deliberately not chained with `&&`/`;` into the existing
`specmgr-schema` hook/step, so each artifact's regeneration/drift check
stays its own clean, independently-failing gate (consistent with
`specmgr-docs`/`specmgr-adr-toc`/`specmgr-schema` already being three
separate entries, not one).
`_paths.py`'s module docstring and `server.py`'s `specmgr://req/schema`
resource-list line were both updated -- neither should still claim this
resource reads `docs/req_schema.json` via `DOCS_DIR` now that it doesn't.
Tests: `tests/req/test_data.py` gained `TestReadReqSchemaText` (4 tests,
mirroring the existing example/template reader test classes: real
packaged file, patched round-trip, fresh-read-per-call, missing-file
`FileNotFoundError`); `tests/req/resources/test_req_schema.py` was
rewritten to patch `req._data._SCHEMA_PATH` instead of the now-removed
`_REQ_SCHEMA_PATH` module constant, assertions otherwise unchanged. No
changes needed to `tests/commands/test_schema.py` -- `--type`/
`--output-dir` were already fully covered generically. 664 tests
project-wide (up from 660), no regressions. `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr docs` regenerated (picks up the
`_paths.py`/`req._data`/`req.resources.req_schema`/`server.py` docstring
changes); `specmgr schema` (both invocations) and `specmgr adr-toc` both
confirmed to have no drift.
**Not verified against a real, non-editable wheel install this time**
(unlike Task 3.6's `get_req_example`, which was) -- deferred to manual
testing outside this session, per explicit instruction; the packaged-data/
`importlib.resources` mechanism itself is already proven by that Task 3.6
precedent.


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.7 implemented: `get_req_template` tool + `specmgr://req/template` resource

Mechanical mirror of Task 3.6's shape: `req/_data.py` gained a second
patchable constant (`_TEMPLATE_PATH`) and reader function
(`read_req_template_text()`), reusing the same `_DATA_PACKAGE`/
`importlib.resources` plumbing -- no `pyproject.toml` change needed, since
the existing `"data/*.md"` package-data glob already covers the
already-committed `req_template.md`.
New `req/tools/get_req_template.py` (`@mcp.tool()`) and
`req/resources/req_template.py` (`@mcp.resource("specmgr://req/template", mime_type="text/markdown")`), both thin wrappers around
`_data.read_req_template_text()`, registered in `req/tools/__init__.py`,
`req/resources/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s resource/tool docstring lists -- same registration points
Task 3.6 touched.
**Template parse-validity, decided differently from Task 3.6's example**:
unlike `req_example.md` (a byte-for-byte copy of the parser's own
`req_reference.md` fixture, and therefore implicitly round-trip tested),
`req_template.md` is **not** asserted to satisfy `parse_req`/
`ReqDocument`'s field-level validators -- confirmed by hand: parsing it
currently raises (first a `pydantic.ValidationError` on `## Level`'s
placeholder prose against `_LEVEL_PATTERN`, and -- after a separate,
in-progress edit to the template swapped in HTML-comment-annotated real
values -- an `AssertionError` instead, since `Level`/`Priority` only
accept a single paragraph and the comment is now a second one). No parse
round-trip test was added for the template (unlike the example's implicit
one via `req_reference.md`); both tool/resource docstrings state this
caveat explicitly. Revisit only if/when the template is made fully
parse-valid (see the next entry down for that in-progress, separate
effort) and a round-trip test becomes meaningful.
Tests: `tests/req/test_data.py` (+4: real packaged file, patched
round-trip, fresh-read-per-call, missing-file `FileNotFoundError`, mirrors
the existing example tests), `tests/req/tools/test_get_req_template.py`
(3 tests), `tests/req/resources/test_req_template.py` (4 tests, including
one asserting the tool and the resource return identical content) -- 660
tests project-wide (up from 649), no regressions. `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr docs` regenerated (2 new module
pages: `req.tools.get_req_template`, `req.resources.req_template`, plus
the extended `req._data` page); `specmgr schema`/`specmgr adr-toc` both
confirmed to have no drift (this task never touches either artifact).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.6 implemented: `get_req_example` tool + `specmgr://req/example` resource

New packaged data file `src/biz/dfch/specmgr/req/resources/data/req_example.md`
(a byte-for-byte copy of `.specmgr/feat-6.../req_reference.md`'s content) is
declared as real **package data** in `pyproject.toml`'s
`[tool.setuptools.package-data]` (`"biz.dfch.specmgr.req.resources" = ["data/*.md"]`) and read via `importlib.resources` -- the first use of that
module anywhere in this codebase. Verified end-to-end: built the wheel
(`python -m build --wheel`), confirmed `req_example.md` is actually inside
it, installed it into a throwaway venv (no editable/source checkout) with
the `mcp` extra, and confirmed `get_req_example()`/`req_example()` both read
it successfully. This is a strictly stronger guarantee than
`docs/req_schema.json`'s `DOCS_DIR`-based read (`_paths.py`'s own docstring
already documents that approach only resolves from an editable/source
checkout) -- see Decisions Made.
New `req/_data.py` -- a small, stdlib-only, framework-free module (no
`mcp`/`typer` import) exposing a patchable module-level `_EXAMPLE_PATH`
(an `importlib.resources` `Traversable`) and `read_req_example_text() -> str`. Lives directly under `req/`, not `req/tools/` or `req/resources/`,
so neither of those two sub-packages needs to import from the other just
to share this one file read -- both import `req._data` directly.
New `req/tools/get_req_example.py` (`@mcp.tool()`) and
`req/resources/req_example.py` (`@mcp.resource("specmgr://req/example", mime_type="text/markdown")`), both thin wrappers around
`_data.read_req_example_text()`. Registered in `req/tools/__init__.py`,
`req/resources/__init__.py`, `req/__init__.py`'s docstring, and
`server.py`'s resource/tool docstring lists.
Return shape: plain `str` (the example's full markdown, frontmatter
included), `mime_type="text/markdown"` -- no base64/encoding needed, that's
only relevant for binary resources. No in-memory cache (read fresh every
call, consistent with every other tool/resource here); a missing/corrupted
packaged file is an uncaught, hard `FileNotFoundError`, matching the task's
own "build time guarantee, hard exception if not true" requirement.
Tests: `tests/req/test_data.py` (4 tests: real packaged file, patched
round-trip, fresh-read-per-call, missing-file `FileNotFoundError`),
`tests/req/tools/test_get_req_example.py` (3 tests), and
`tests/req/resources/test_req_example.py` (4 tests, including one asserting
the tool and the resource return identical content) -- 649 tests
project-wide (up from 638), no regressions. `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr docs` regenerated (3 new module
pages: `req._data`, `req.tools.get_req_example`,
`req.resources.req_example`); `specmgr schema`/`specmgr adr-toc` both
confirmed to have no drift (this task never touches either artifact).
`.specmgr/feat-6.../req_reference.md` (Task 1.3's parser test fixture) was
deliberately **not** unified with the new packaged file -- both now hold
the same content independently, with no shared source and no enforced
sync. See Decisions Made for the trade-off this accepts.


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.3 implemented: `specmgr req-parse` CLI command

New `src/biz/dfch/specmgr/commands/req_parse.py` — the first REQ-specific CLI
command, registered as flat top-level `specmgr req-parse <path>`
(Typer auto-derives the hyphenated name from the `req_parse` function, same
as `adr_toc` → `adr-toc`), consistent with this repo's existing flat command
list (no sub-app/command-group pattern introduced).
Path-based only, mirroring `req.tools.parse_req`'s own `Path(path).read_text(...)`
→ `parse_req(text)` flow — **no `req-get`** (id-based lookup): REQ has no
`_paths.py`/`_io.py` equivalent to ADR's yet (Task 3.1/3.2 note this gap
explicitly), so an id → file-path resolver would need to be built first;
deferred to a future task rather than bundled into this one. Narrows Task
3.3's original "`req-get`, `req-parse`, etc." wording down to just
`req-parse` — see Decisions Made.
Two output formats: `--format json` (default) prints the full parsed
`ReqDocument` as `rich`-syntax-highlighted JSON (`Console.print_json`);
`--format markdown` re-reads the original file, splits it into its raw
YAML frontmatter block and markdown body, reformats the body via the
existing `format_text()` helper (`models/md/_markdown.py`, the same one
`general.tools.mdformat` uses) **without writing anything back to disk**,
and renders both through `rich` (`Syntax` for the frontmatter, `Markdown`
for the body). This is the first use of the `rich` dependency anywhere in
`src/` — previously declared in the `cli` extra (`pyproject.toml`) but
never actually imported.
Parse errors (missing file → `OSError`, malformed structure →
`AssertionError`, invalid field values → `pydantic.ValidationError`) are
caught here and reported via `typer.echo(f"Error parsing '{path}': {ex}")`
(the original exception's message included) followed by `typer.Exit(1)` —
deliberately diverging from the parser/MCP tool's own "let it raise"
philosophy, since a CLI should not surface a raw Python traceback for an
expected failure mode. An unknown `--format` value is rejected the same
way `schema.py`'s unknown `--type` is (plain `typer.echo` + `typer.Exit(1)`,
no `err=True`, matching this repo's existing convention across all other
commands).
Tests: `tests/commands/test_req_parse.py` (10 tests, mirroring
`test_schema.py`'s split between a pure-helper test class and a
CLI-wrapper test class) — 638 tests project-wide (up from 628), no
regressions. `ruff format --check`/`ruff check`/`vulture` clean;
`specmgr docs` regenerated (new `commands.req_parse` module page).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.5 implemented: `specmgr://req/schema` MCP resource

New `req/resources/` sub-package (`req/resources/req_schema.py` + `__init__.py`),
registered from `req/__init__.py` (`from . import resources, tools`) — the first
`resources` sub-package under `req/`, mirroring `adr/`'s
`tools`/`prompts`/`resources` shape.
`req_schema()` reads `docs/req_schema.json` fresh on every call (no
in-memory cache) and returns `json.loads()`'d content as a `dict[str, Any]` — chosen over a raw-`str` return after weighing fidelity
(byte-identical to the committed file) against consistency with every
other resource in this codebase (`version_info`/`adr_list`/`adr_get` all
return a structured type that FastMCP serializes) and against turning a
corrupted on-disk file into a hard failure at read time. Schema
*presence* is a build-time guarantee (the `specmgr-schema` pre-commit
hook/CI step), so a missing file raises `FileNotFoundError` and a
corrupted one raises `json.JSONDecodeError`, both uncaught — no
defensive handling, matching this codebase's existing let-it-raise
convention.
Path is a **fixed** location, not configurable via an env var (unlike
`adr.tools._paths.adr_base_dir`'s `SPECMGR_ADR_DIR`) — `docs/req_schema.json`
is a build artifact of this package's own source tree, not user-authored
content living elsewhere, so there's no meaningful "different location" to
override to.
New `biz/dfch/specmgr/_paths.py` — a top-level, dependency-free module
(only `pathlib`) exposing `REPO_ROOT`/`DOCS_DIR`, computed by climbing
from `__file__`. Both `commands/schema.py` (the `cli` extra) and
`req/resources/req_schema.py` (the `mcp` extra) import it, so neither
extra's optional dependency (`typer`/`mcp`) leaks into the other's import
graph — the Decisions Made entry below already ruled out importing
`commands.schema` directly from the resource for exactly this reason;
this factors out the *path* computation (previously duplicated inline in
`commands/schema.py`) into a shared home instead of a second duplicate.
Only resolves correctly from an editable/source checkout — a built,
non-editable install doesn't ship `docs/` as package data, so this would
hard-fail for a real `pip install` consumer; accepted as out of scope
(no `mcp.run()` caller exists yet regardless, per AGENTS.md).
Tests: `tests/req/resources/test_req_schema.py` (5 tests: real
committed-schema smoke test, patched-file round-trip, no-cache/fresh-read
regression, missing-file `FileNotFoundError`, corrupted-file
`json.JSONDecodeError`) and `tests/test_paths.py` (2 tests: `REPO_ROOT`
sanity-checked against `pyproject.toml`'s presence, `DOCS_DIR == REPO_ROOT / "docs"`) — 628 tests project-wide (up from 621), no
regressions. `ruff format --check`/`ruff check`/`vulture` clean;
`specmgr schema`/`specmgr docs`/`specmgr adr-toc` all regenerated with no
further drift (`docs/req_schema.json` itself is byte-identical --
`commands/schema.py`'s only change was importing the shared path
constant instead of computing its own).


#### 2026-08-14 00:00:00.000Z - (continued) Task 3.4 implemented: `"$comment": "v1"` schema-layout version marker

Implements the design queued in the "Tasks 3.4/3.5 queued" entry below.
Added `SCHEMA_COMMENT_VERSION = "v1"` to a new, private
`req/models/v1/_util.py` — mirroring `models/adr/v1/_util.py`'s existing
`SCHEMA_MAJOR_VERSION`/`CURRENT_SCHEMA_VERSION` precedent, so the value
can't silently drift from the package's own `v1` folder name the way a
hardcoded literal in `commands/schema.py` could. Re-exported from
`req/models/v1/__init__.py`.
`generate_req_schema()` now injects `schema_dict["$comment"] = SCHEMA_COMMENT_VERSION` alongside its existing `$schema` injection.
`docs/req_schema.json` regenerated (one new top-level key).
Deliberately **not** wired into `ReqFrontmatter.version`/any
document-instance validation — this constant is scoped purely to the
generated schema *artifact's* own layout version, a different concept
from the frontmatter's semver (see Decisions Made, "Schema `"$comment"`
version marker omits the doc-type name").
Added `test_comment_is_schema_layout_version` to
`tests/commands/test_schema.py` — 621 tests project-wide (up from 620),
no regressions. `ruff format --check`/`ruff check`/`vulture` clean;
`specmgr schema`/`specmgr docs`/`specmgr adr-toc` all regenerated with no
further drift.


#### 2026-08-14 00:00:00.000Z - (continued) Bug fix: `## Priority` accepted any digit string, not just 0-99

Found during the Task 2.3 review above: `Priority.value`'s `Field(description=...)`
documents the range as "0 to 99", but `_PRIORITY_PATTERN` was `r"^\d+$"` —
digits-only, no upper bound, so e.g. `"12345"` passed validation despite the
stated contract. Fixed by narrowing the pattern to `r"^(0|[1-9][0-9]?)$"`
(0-99, no leading zeros other than "0" itself); the `field_validator` logic
around it (checking `value.text`, since `value` is a `MarkdownParagraph`
model, not a plain string) is unchanged.
Not a Task 2.4/2.3 scope change (both are already closed/completed) — fixed
directly as a bug rather than reopening either task, since it's a pure
correctness fix with no design decision attached. Added two regression
tests to `tests/req/models/v1/test_parser.py`
(`test_priority_out_of_range_raises_validation_error`,
`test_priority_upper_bound_is_accepted`) — 620 tests project-wide (up from
618), all passing. `ruff format --check`/`ruff check`/`vulture` clean;
`specmgr schema` exits 0 (unchanged) since this validator was never
reflected in the emitted JSON Schema's `pattern` keyword either before or
after (same pydantic model-vs-string-field limitation noted in the
2026-08-14 `Level`/`Priority` regression entry below).


#### 2026-08-14 00:00:00.000Z - (continued) Task 2.3 closed as not applicable

Reviewed against `req/models/v1/body.py`'s final state (post Tasks 2.4–2.12):
no cross-field/model-level invariant exists in the current spec. The only
candidate — validating `related_artifacts`' cross-reference IDs against
other documents on disk — is explicitly out of scope for this feature (see
Scope) and, even if in scope, would need data outside the document being
validated, so wouldn't be a `@model_validator` regardless. Closed Task 2.3
rather than leave it open indefinitely, resolving the inconsistency between
its `not-started` status and "Current Status"'s claim that Phase 2 is fully
complete.


#### 2026-08-14 00:00:00.000Z - (continued) Tasks 3.4/3.5 queued: `specmgr://req/schema` resource design settled (unversioned URI, disk-read only, `$comment` version marker)

Design-only entry (no code yet) resolving an agent-discoverability question raised in review: how should an agent learn the REQ schema's structure via MCP tools/resources, beyond `parse_req`'s own `outputSchema` (already fully populated via `model_json_schema()`, per the 2026-08-14 docstring-audit entry below).
Decided a new `specmgr://req/schema` resource is the right complement to `parse_req`'s tool-discovery `outputSchema` — the latter is free but host-dependent (not every MCP client surfaces it as agent-usable context); the former is an explicit, addressable fetch, mirroring the existing `specmgr://version`/`specmgr://adr/list`/`specmgr://adr/{id}` pattern.
Decided it must only read the already-persisted `docs/req_schema.json` from disk — trusting the `specmgr-schema` pre-commit hook to keep it current — rather than importing `commands/schema.py`'s `generate_req_schema()` directly, which would leak the `cli` extra's `typer` dependency into the `mcp` extra's import graph.
Decided the resource's URI stays unversioned (`specmgr://req/schema`, no `/v1`) — see Decisions Made.
Decided to add a bare `"$comment"` version marker (e.g. `"v1"`, no doc-type prefix) to `generate_req_schema()`'s output so a caller can detect a schema-layout change without diffing the whole document — see Decisions Made.
Queued as Task 3.4 (the `"$comment"` marker, in `generate_req_schema()`) and Task 3.5 (the resource itself, depends on 3.4).


#### 2026-08-14 00:00:00.000Z - (continued) Task 2.4 regression fixed: invalid `Field(pattern=...)` on model-typed `Level.value`/`Priority.value`

The Task 2.4 entry below added `Field(..., pattern=r"...")` to
`Level.value`/`Priority.value` in `req/models/v1/body.py`. Both fields are
typed `MarkdownParagraph` — a Pydantic **model** (built on `MarkdownStr`),
not a `str` — and pydantic v2 cannot apply a string `pattern` constraint to
a model-typed field: every call to `Requirement.from_text(...)` (i.e.
`parse_req` and `parse_req()`/the MCP tool) raised
`TypeError: Unable to apply constraint 'pattern' ... for schema of type 'model'`
at instantiation. This was never caught at the time because Tasks 2.7/2.8's
`model_json_schema()`-based schema generation and its own tests don't
instantiate the model, only introspect its schema — the break only
surfaced in the pre-existing parser/tool tests
(`tests/req/models/v1/test_parser.py`,
`tests/req/tools/test_parse_req.py`, 6 tests).
Fixed by replacing each `pattern=...` `Field` argument with a
`@field_validator("value")` that checks `value.text` (the paragraph's own
inline text) against the same regex and raises `ValueError` otherwise —
the same "constrain the rendered text, not the model" approach forced by
`value`'s model type. `docs/req_schema.json` regenerated as a result (the
two `value` fields' schema entries lose their `title` key, a
pydantic/JSON-Schema side effect of moving the constraint out of `Field`;
no `pattern` keyword was ever emitted for these two fields either before
or after, since pydantic silently dropped the invalid keyword at schema-
generation time rather than raising there too).
Added `_._validate_value` to `whitelist.py`'s existing
`@field_validator`/`@model_validator` false-positive section (same pattern
as `_._validate_status`/`_._validate_version` etc.) since vulture flags
the two new `_validate_value` methods as unused.
618 tests project-wide, all passing (no count change — this fixes
previously-failing tests, doesn't add new ones). `ruff format --check`/
`ruff check`/`vulture` clean; `specmgr schema` exits 0 (unchanged) on a
second run; `specmgr docs` regenerated (picks up the `body.py`/
`whitelist.py` changes).


#### 2026-08-14 00:00:00.000Z - (continued) Tasks 2.4-2.12 implemented: `req_schema.json` now generated (JSON Schema 2020-12) via `specmgr schema`

Implements the plan queued in the entry directly below. Phase 1 and Phase 2
are now both fully complete.
**Task 2.4**: `req/models/v1/body.py`'s `Requirement` fields and every
section's `items`/`value` field now carry `Field(description=...)`;
`RelatedArtifacts`'s four optional sub-fields got the same treatment for
consistency; every `items: list[MarkdownListItem]` field gained
`min_length=1` plus a "must contain at least one item" description.
**Task 2.5**: verified the **class** docstrings (the only ones
`model_json_schema()` surfaces) were already self-contained from the
2026-08-14 audit entry below; only `body.py`'s **module**-level docstring
still referenced `models.adr.v1`/`req_reference.md`, cleaned up for
consistency even though it never reaches the emitted schema.
**Task 2.6**: shortened `MarkdownListItem`'s (~2.7k → ~1.1k chars) and
`MarkdownParagraph`'s (~1.3k → ~0.7k chars) **class** docstrings in
`models/md/` — method docstrings (`get_extent`/`from_text`/`__str__`,
never surfaced in a schema) untouched. This is `feat-5-md-model-parser`
owned code; done as a post-closure change and logged in that feature's
own Recent Updates (2026-08-14 entry), same "downstream feature triggers
a fix in the closed engine" precedent as its 2026-08-12/13 entries. Net
effect on `req_schema.json`'s total size was roughly a wash against
Task 2.4's own additions — the benefit is capping what these two shared
base classes contribute per `$ref`, not shrinking this particular
schema's overall byte count.
**Task 2.7/2.8**: new `commands/schema.py` — `generate_req_schema()`
(pure function, `ReqDocument.model_json_schema()` + explicit `$schema`
injection, since Pydantic v2 omits it by default) and the `specmgr schema` Typer command, registered in `cli.py`/`commands/__init__.py`.
Built on a `_GENERATORS: dict[str, Callable[[], str]]` registry
(`{"req": generate_req_schema}` today); `--type` restricts to one
registered name, omitting it generates all; each type's output goes to
`{output_dir}/{type}_schema.json` (default `docs/`). The command compares
old vs. new content per file and exits 1 if anything changed (or didn't
exist yet), while still writing the file either way — verified manually:
first run exits 1 (file didn't exist), second run exits 0 (unchanged), an
unknown `--type` exits 1 without writing anything.
**Task 2.9**: added a "Make sure `docs/req_schema.json` is correct" step
to `.github/workflows/ci.yml`'s Python-3.13-only job, right after the
`docs/adr/README.md` step — just runs `specmgr schema` and relies on its
own exit code (no `git diff --exit-code`, unlike the `docs`/`adr-toc`
steps).
**Task 2.10**: added a `specmgr-schema` local hook to
`.pre-commit-config.yaml`, scoped to
`src/biz/dfch/specmgr/(req/models/v1|models/md)/**/*.py`, entry `uv run --frozen specmgr schema` (no `--type` — always "all", future-proofed for
when more doc types register). Verified with `uv run --frozen pre-commit run specmgr-schema --files src/biz/dfch/specmgr/req/models/v1/body.py`
(passed).
**Task 2.11**: `tests/commands/test_schema.py` — 14 new tests: valid
JSON/deterministic output, `$schema` is the 2020-12 URI,
`frontmatter`/`body` structural assertions, `--type req` vs. no-option
("all") file selection, unknown `--type` exits 1 without writing, exit 0
when unchanged vs. 1 when missing/stale, `--output-dir` auto-creation.
618 tests project-wide (up from 604), no regressions.
Regenerated `docs/api/` and `docs/GENERATED.md` (`specmgr docs`, picks up
the new `commands/schema.py` module and the shortened
`MarkdownListItem`/`MarkdownParagraph` docstrings) and confirmed
`docs/adr/README.md` (`specmgr adr-toc`) has no drift. `ruff format --check`/`ruff check`/`vulture` all clean throughout.


#### 2026-08-14 00:00:00.000Z - (continued) `req_schema.json` generation planned: 2020-12 dialect, generic `specmgr schema` command, Tasks 2.7-2.12 queued

Decided (Decisions Made) that `req_schema.json` (Task 1.2) will be
**generated** from `ReqDocument.model_json_schema()` rather than
hand-authored like `uc_schema.json`, and will use Pydantic v2's native
**JSON Schema 2020-12** dialect rather than the draft-07 Task 1.2
originally specified — avoids lossy `$defs`→`definitions` conversion for
a dialect with no known consumer yet.
Queued Tasks 2.7-2.12 to implement this: `generate_req_schema()` (2.7,
depends on the docstring cleanup in 2.4-2.6 landing first so the emitted
schema is clean on first generation); a new **generic** `specmgr schema`
CLI command (2.8, `commands/schema.py`) — named `schema`, not
`req-schema`, since more doc-type schemas are expected later — built on
a doc-type generator registry (`{"req": generate_req_schema}` today), a
`--type` option to restrict to one registered type, and "generate all
registered types" as the no-option default; the command exits 1 if any
regenerated file differs from what was already on disk, so CI can rely
on the exit code directly instead of a separate `git diff --exit-code`
step; CI wiring (2.9); a pre-commit hook that always runs `specmgr schema` with no `--type` (2.10, future-proofed for when more types are
registered); tests (2.11); and a final README status sync-up (2.12).


#### 2026-08-14 00:00:00.000Z - (continued) Requirements/Acceptance Criteria checklists synced with actual progress

The top-level Requirements (REQ-001..005) and Acceptance Criteria
(ACC-001..005) checklists had drifted out of sync with the canonical Task
List and Recent Updates — all ten checkboxes were still unchecked despite
Phase 1/2 being complete and Phase 3 partially so. Checked off
REQ-001..004 and ACC-001/003/004, which the completed Task List entries
and passing tests already substantiate; left REQ-005/ACC-002/ACC-005
unchecked since MCP prompts/resources and characteristics "filtering"
remain unimplemented.
Fixed REQ-005's parenthetical, which pointed at "Task 2.1" (the Pydantic
model task) instead of Task 3.1 ("Define MCP tools, prompts, and
resources for REQ management").
Fixed REQ-003's stated path (`models/req/v1/`) to match what was actually
implemented (`req/models/v1/`), and updated Design Notes' "decision
deferred until spec phase" wording for the same model-location question,
which had never been revisited after Task 2.1 actually settled it.


#### 2026-08-14 00:00:00.000Z - Docstrings audited against actual MCP schema exposure; follow-up tasks queued

Added concise class docstrings to every `req/models/v1/body.py` section
class and to `Requirement` itself (agent-annotation request).
Verified against the installed `mcp>=2.0.0` SDK (`mcp.server.mcpserver`)
exactly how these surface to a calling agent: `model_json_schema()` builds
the tool's `outputSchema` at `tools/list` time, and every class docstring
lands verbatim as that type's `$defs[...].description` — confirmed via a
live `Requirement.model_json_schema()` dump. Field/attribute docstrings are
**not** picked up automatically (only explicit `Field(description=...)`
is); `required`/`anyOf ... null` already communicates mandatory/optional
structurally. Per-call tool results (`_convert_to_content`) only ever
serialize field values (`model_dump`/`pydantic_core.to_json`) — no
docstring text is ever resent per call, only once at discovery.
Follow-up: Tasks 2.4-2.6 queued to (1) add field-level descriptions with
constraints, (2) make class docstrings self-contained (no references to
`models/adr/v1` or `req_reference.md`, which an agent can't necessarily
read at runtime), and (3) shorten the shared `models/md` base classes'
docstrings that get inlined into every schema referencing them.


#### 2026-08-13 00:00:00.000Z - (continued) upstream `MarkdownSection.text` leaf-serialization bug found and fixed

While reviewing `parse_req`'s output, noticed `Description`/`MoreInformation`/
`Notes` (the three bare leaf `MarkdownSection2`s in `body.py` — no `value`/
`items` field of their own) serialized via `model_dump()` to just their
heading text (e.g. `{"text": "Notes"}`), with the entire prose body silently
missing. Root cause was upstream in `feat-5-md-model-parser`'s shared engine,
not this feature's own model code: `MarkdownSection.text`'s computed_field
always extracted only the heading, regardless of leaf vs. composite, even
though a leaf's `_value` already held the complete heading+body extent
verbatim. Fixed at the source (`models/md/markdown_section.py`) rather than
worked around here by adding `value: MarkdownParagraph` fields to
`Description`/`MoreInformation`/`Notes` — the fix makes `.text` return the
complete extent for *any* leaf `MarkdownSection`, so REQ's own body model
needed no change at all. Full details, root cause, and fix recorded in
`feat-5-md-model-parser`'s own Recent Updates (2026-08-13 entry) since it
owns that module; noted here only because it was discovered through this
feature's own `parse_req` tool.
Extended `tests/req/tools/test_parse_req.py`'s `_VALID_DOC` fixture with
`## More Information`/`## Notes` sections and added
`test_model_dump_surfaces_leaf_section_body_content`, a dedicated
regression test asserting `model_dump()` now surfaces the full body text
(heading included) for `description`/`more_information`/`notes` — REQ
test count now 21 (up from 19), 604 tests project-wide.


#### 2026-08-13 00:00:00.000Z - Body model, reference document, parser, and `parse_req` MCP tool completed

**Task 1.1.2 COMPLETED**: `req/models/v1/body.py` defines the full REQ body hierarchy on top of `feat-5-md-model-parser`'s generic `models/md` engine (`MarkdownStr`/`MarkdownSectionN`/`MarkdownParagraph`/`MarkdownListItem`), the same approach `uc/models/v2` uses — not a hand-written token parser like `uc/models/v1`/`models/adr/v1`. `Requirement` (H1, `@alias(".+", REGEX)` to accept any title) has: `statement` (the requirement-statement paragraph directly under the H1, before any H2); mandatory `description`/`characteristics`/`level`/`source`; optional `priority`/`tags`/`related_artifacts`/`more_information`/`notes`. `related_artifacts` nests four optional H3 subsections (`requirements`/`decisions`/`goals`/`acceptance_criteria`), each a bullet list of `{ID}: {description}` references (e.g. `REQ-9687: ...`, `DEC-2703: ...`). All section classes rely on the engine's default `SPACE_SEPARATED` alias (PascalCase class name → heading text), no explicit `@alias` needed beyond `Requirement`'s own.
**Task 1.3 COMPLETED** (ahead of Task 1.2): `.specmgr/feat/feat-6-requirement-artifact/req_reference.md` — a full sample requirement ("Maximum Engine Temperature") exercising every section — plus `req_reference.ast` (its markdown-it token dump). Used directly as the parser's own test fixture rather than a separate, hand-maintained example.
**Task 2.1 COMPLETED**: `req/models/v1/document.py` — `ReqDocument(frontmatter: ReqFrontmatter, body: Requirement)`, mirroring `uc.models.v2.document.UcDocument`.
**Task 2.2 COMPLETED**: `req/models/v1/parser.py` — `parse_req(text) -> ReqDocument`, mirroring `uc.models.v2.parser.parse_uc` line-for-line (`frontmatter.loads()` → `_stringify_metadata()` → `ReqFrontmatter.model_validate()` → `Requirement.from_text(format_text(post.content))` → `ReqDocument(...)`). Same two uncaught error channels: `AssertionError` for structural failures (unrecognized/missing heading), `pydantic.ValidationError` for field/frontmatter validation failures — no dedicated `ReqParseError`.
**Task 3.1/3.2 PARTIALLY COMPLETED**: `req/tools/parse_req.py` — `@mcp.tool()` wrapper (`parse_req(path: str) -> ReqDocument`), reading the file from disk and delegating to the parser, mirroring `uc.tools.parse_uc` exactly (including its docstring's error-propagation contract). `req/tools/__init__.py` and `req/__init__.py` added for registration; `server.py` now imports `req` alongside `adr`/`general`/`uc`, and `parse_req` appears in `mcp.list_tools()`. No `_paths.py`/`_io.py`/id-based file resolution yet (same as `uc/tools/`'s current scope) — the tool takes a raw filesystem path, not an id.
**Tests**: `tests/req/models/v1/test_parser.py` (5 tests: minimal doc, full reference-document round-trip, frontmatter-absent defaults, invalid status → `ValidationError`, malformed structure → `AssertionError`) and `tests/req/tools/test_parse_req.py` (5 tests: happy path, `model_dump()` surfaces `MarkdownParagraph`-backed field content via its `text` computed field, invalid frontmatter, malformed structure, nonexistent file) — 19 REQ tests total, 600 project-wide (no regressions). `ruff format`/`ruff check` clean, `vulture` clean (9 new whitelist entries added for body.py's Pydantic fields, same false-positive pattern as UC's existing entries: `statement`, `characteristics`, `tags`, `source`, `related_artifacts`, `requirements`, `decisions`, `goals`, `acceptance_criteria`).


#### 2026-08-13 00:00:00.000Z - Task 1.1.1 completed — REQ frontmatter

**Task 1.1.1 COMPLETED**: Created `src/biz/dfch/specmgr/req/models/v1/frontmatter.py` with `ReqFrontmatter(MarkdownFrontmatter)` subclass, narrowing:
`type: Literal["req"] = "req"` (fixed discriminator)
`status`: 7-value closed set (`draft`, `proposed`, `accepted`, `superseded`, `deprecated`, `rejected`, `implemented`) — ADR's 6 values plus `"implemented"` since requirements track implementation beyond acceptance
Inherits `id`, `created`, `updated`, `version` unchanged from base
Blank/None normalization correct (blank status → "draft", blank optional → None)
Created `tests/req/models/v1/test_frontmatter.py` — 8 test cases mirroring existing patterns, all passing. 590 tests total (no regressions), ruff format/check clean, vulture clean.
