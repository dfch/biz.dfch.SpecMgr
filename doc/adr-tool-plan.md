# ADR Tooling Plan — MADR 4.0.0-based, LLM-editable via MCP

## 1. Goal
Enable an LLM (via OpenCode) to create and update Architecture Decision Records
that conform to a custom schema derived from MADR 4.0.0, through a Python MCP
server exposing structured tools — never by having the LLM write raw markdown
text directly.

## 2. Source document
MADR 4.0.0 template:
`https://raw.githubusercontent.com/adr/madr/refs/tags/4.0.0/template/adr-template.md`

Heading structure:
```
--- (YAML frontmatter) ---
# {title}                                   H1
## Context and Problem Statement            H2, required
## Decision Drivers                         H2, optional
## Considered Options                       H2, required
## Decision Outcome                         H2, required
### Consequences                            H3, optional
### Confirmation                            H3, optional
## Pros and Cons of the Options             H2, derived (see §5)
### Option N: {title}                       H3, dynamic collection
## More Information                         H2, optional
```

## 3. Frontmatter schema (Pydantic)
- `status`: `Literal["proposed","rejected","accepted","deprecated","superseded"]` **or** a
  string matching `^superseded by .+$` (not a plain enum)
- `date`, `decision-makers`, `consulted`, `informed`: all optional
- `version`: **specmgr-only extension key, not part of the MADR 4.0.0
  standard.** A `major.minor.patch` string (default `CURRENT_SCHEMA_VERSION`,
  currently `"1.0.0"`), kept alongside the MADR-defined keys above purely so
  the schema version round-trips through the on-disk file's YAML block (§7's
  parse/render pipeline never persists anything outside frontmatter/body).
  Lives on `AdrFrontmatter`, not on the `Adr` wrapper — see §6.
- `id`: **specmgr-only extension key, not part of the MADR 4.0.0 standard,
  added per §9a.** `str | None`, default `None`. Server-assigned UUID,
  system-owned (never settable/changeable by the LLM through the normal
  frontmatter full-replace contract below — `create_adr`/`update_frontmatter`
  always re-inject the correct value regardless of what is submitted). `None`
  only for pre-existing/hand-authored files that predate this field; such a
  file is not addressable by any `id`-taking tool until one is assigned.
- Update contract: **whole object, full replace only** — no partial/sentinel
  mechanism needed (omitting a key from the submitted object is how you drop
  it) — **except `id`, which is never part of the replace, see §9a.**

## 4. Body schema — whole-section fields
Each is independently full-replace via a generic `update_section(key, value)`
tool.

| Key | Heading | Mandatory |
|---|---|---|
| `title` | H1 | yes |
| `contextAndProblemStatement` | `## Context and Problem Statement` | yes |
| `decisionDrivers` | `## Decision Drivers` | no |
| `consideredOptions` | `## Considered Options` | yes |
| `decisionOutcome` | `## Decision Outcome` (text before any H3) | yes |
| `consequences` | `### Consequences` (under Decision Outcome) | no |
| `confirmation` | `### Confirmation` (under Decision Outcome) | no |
| `moreInformation` | `## More Information` (always last) | no |

**Deletion sentinel:** submitting an empty string, a whitespace-only string, or
the literal `"REMOVE"` (case-insensitive) as `value` removes that section
(heading + content dropped from render). If the targeted section is
**mandatory**, `update_section` errors immediately and does not write.

**Considered Options vs. Option sub-sections:** kept fully independent.
`consideredOptions` is manual, freeform; no consistency check against the
`Option` collection is enforced. Drift is accepted; a future assistive
"summarize options" skill is a backlog idea, not part of the schema/validator.

## 5. `## Pros and Cons of the Options` — derived container
- Not directly editable. Rendered automatically **iff** ≥1 `Option`
  sub-section exists; otherwise the entire H2 (and any comment placeholder) is
  omitted.
- Options are never individually mandatory (zero is a valid state), so the
  mandatory/error rule in §4 never applies to them.
- Heading format: `f"Option {counter}: {partial_title}"` — plain ASCII
  `"Option "`, unpadded monotonically increasing counter, never reused, no
  line breaks allowed in `partial_title`. New options are always appended at
  the end; deleting one leaves a gap in numbering and does not reorder or
  renumber the rest.
- Content is an opaque markdown blob (no enforced Good/Bad/Neutral structure)
  — freeform text under each `### Option N: ...` heading.
- Dedicated sub-API (separate from `update_section`; the deletion sentinel
  from §4 does **not** apply here — deletion is exclusively via
  `option_delete`):
  - `option_list() -> list[str]` — full titles, e.g. `"Option 1: A title"`
  - `option_create(partial_title: str, value: str) -> str` — returns the
    assigned full title
  - `option_update(full_title: str, value: str) -> str` — full content
    replace, returns new content
  - `option_read(full_title: str) -> str` — returns current content
  - `option_delete(full_title: str) -> list[str]` — returns remaining titles

## 6. Module layout (`src/biz/dfch/specmgr/`)

Supersedes the generic `core/`/`adr/`/`req/`/`uc/`/`cli/`/`mcp_server/` sketch
from earlier drafts of this plan — this repo already has an established
sibling-project convention (`models/`, `tools/`, `resources/`, `commands/`;
see `AGENTS.md` and `server.py`'s own comment about the `tools/` import
convention), so the ADR feature is placed within that, not alongside it:

- **`models/`** — all Pydantic schemas, one subdirectory per document type,
  e.g. `models/adr/` holds the ADR frontmatter model, body/section model, and
  `Option` sub-model. Parser, renderer, and mutation functions for a document
  type live next to its models in the same subdirectory (they operate purely
  on the schema, no `mcp`/`typer` dependency, no file I/O — consistent with
  the core-library isolation rule below). `req`/`uc` get their own
  `models/req/`, `models/uc/` subdirectories later, following the same
  pattern.
  - **Mutation logic placement (settled):** the §4/§5/§8 edit semantics
    (`update_section`, `set_status`, `option_list`/`option_create`/
    `option_read`/`option_update`/`option_delete`, including deletion-
    sentinel handling and mandatory-section rejection) live as free
    functions in `models/adr/v1/mutations.py` — each takes an `Adr` and
    returns a new one (or plain data for read-only lookups), never mutating
    its argument — mirroring `parser.py`/`renderer.py`'s own free-function
    style rather than becoming methods on the Pydantic model classes
    themselves. `tools/adr/` (below) wraps these with the file I/O and
    id-lookup they deliberately exclude.
  - **Schema versioning:** within `models/adr/`, every model class lives in a
    `vN` sibling package, one per *major* schema version — currently only
    `models/adr/v1/` exists. `models/adr/__init__.py` re-exports whichever
    `vN` is current (today, `v1`) under the plain names (`Adr`, `AdrBody`,
    `AdrFrontmatter`, `AdrOption`, plus `SCHEMA_MAJOR_VERSION` and
    `CURRENT_SCHEMA_VERSION`), so callers that only care about "the current
    schema" import from `models.adr` directly and never need to know the
    version number; code that specifically needs an older version (e.g. a
    migration step) imports `models.adr.v1` (or `.v2`, ...) explicitly.
    `AdrFrontmatter.version` is a `major.minor.patch` string (default
    `CURRENT_SCHEMA_VERSION`), and each `vN.AdrFrontmatter` rejects any
    `version` whose major component doesn't match its own
    `SCHEMA_MAJOR_VERSION` — a `v1.AdrFrontmatter` can never carry
    `"2.x.x"`. It lives on the frontmatter, not on the `Adr` wrapper class,
    because only `frontmatter`/`body` are ever persisted to the on-disk
    `.md` file (§7); a field on `Adr` itself would never round-trip.
    A **new major version does not duplicate the whole `vN` tree.** A
    breaking schema change gets a new `models/adr/v2/` package containing
    *only* the classes that actually changed; unchanged classes are
    imported from `v1` rather than copy-pasted, plus a
    `migrate_v1_to_v2()`-style adapter function that upgrades a parsed `v1`
    document into `v2` shape. Non-breaking evolutions (e.g. a new optional
    field) don't need a new package at all — bump the minor/patch component
    of `CURRENT_SCHEMA_VERSION` within the existing `vN` package instead.
    This follows directly from §7's "no AST/round-trip preservation
    requirement": the renderer only ever needs to emit the *current*
    version's canonical form, so older versions only need a parser (or a
    migration step feeding the current parser), never their own renderer —
    avoiding an N-parsers-times-N-renderers maintenance matrix. Full,
    independent wholesale duplication of every `vN` package was considered
    and rejected: it invites drift, since an unrelated bugfix would have to
    be manually ported to every historical folder.
- **`tools/`** — MCP tool wrappers, one subdirectory per document type, e.g.
  `tools/adr/` holds the `@mcp.tool()`-decorated wrappers (`get_adr`,
  `create_adr`, `update_frontmatter`, `update_section`, `set_status`,
  `option_*`, `validate_adr` — `list_adrs` is the one exception, implemented
  as an MCP resource instead, see §9a) that call into `models/adr/`. Each such
  subpackage must be imported at the bottom of `server.py` (next to the
  existing `resources` import) or its `@mcp.tool()` decorators never run —
  see the warning already in `server.py`'s module docstring. **Implemented**,
  see §10 item 4.
- **`commands/`** — one module per CLI command (existing convention, e.g.
  `commands/version.py`), extended with ADR commands that call the same
  `models/adr/` functions as the MCP tools do — CLI and MCP stay thin
  adapters over one shared implementation, per the ports-and-adapters
  principle below.

## 7. Cross-cutting design decisions
- **Source of truth:** the `.md` file itself. Humans can hand-edit it at any
  time; every tool call re-reads and re-parses current on-disk state before
  acting — no assumption that the tool is the sole writer.
- **Validator:** one schema-driven `validate_adr` check, shared identically
  between LLM tool calls and human edits, surfacing clear errors. Does not
  enforce Considered-Options/Option-section consistency (see §4).
- **Pipeline:** parse → validate → render, always regenerating the full file
  deterministically from the parsed structured model rather than patching text
  in place. This is sufficient (no need for AST-preserving round-trip tooling
  like `remark`) because the validator/renderer define the canonical form;
  arbitrary human formatting nuances outside the schema aren't a preservation
  requirement.
- **Libraries (Python):**
  - `pydantic` for both the frontmatter model and the body model (mirrors the
    earlier Zod idea, Python-native; also matches the Python MCP SDK's use of
    Pydantic/type hints for tool schemas — one schema definition reused as the
    tool contract)
  - `python-frontmatter` for splitting/parsing the YAML header (settled;
    declared as a direct base dependency in `pyproject.toml`, not `PyYAML`
    directly — `python-frontmatter` wraps it)
  - `markdown-it-py` for walking the body's token stream to locate fixed-
    heading sections and the dynamic `Option N` collection (settled; declared
    as a direct base dependency in `pyproject.toml`, promoted from what was
    previously only a transitive dependency of `rich`)
  - Deterministic template rendering (not a markdown-it serializer, which
    doesn't exist) for the write path

## 8. MCP tool surface (Python MCP SDK)
- `list_adrs()` — ids/titles/status for context. **Implemented as an MCP
  resource (`specmgr://adr/list`), not a `@mcp.tool()` — see §9a.**
- `get_adr(id)` → structured object (frontmatter + body, not raw markdown)
- `create_adr(frontmatter, body_fields)` → validates, assigns id/filename,
  renders, writes
- `update_frontmatter(id, frontmatter)` — whole-object replace
- `update_section(id, key, value)` — whole-section replace/delete per §4
- `set_status(id, status, supersededBy?)` — narrow convenience wrapper over
  frontmatter update for the common case
- `option_list(id)`, `option_create(id, partial_title, value)`,
  `option_update(id, full_title, value)`, `option_read(id, full_title)`,
  `option_delete(id, full_title)`
- `validate_adr(id)` — schema check, usable standalone (e.g. pre-commit/CI)
  and by the LLM to self-correct

**Prompt surface:** in addition to the tools above, two `@mcp.prompt()`s
(`create_adr`, `update_adr`) return instructional text driving this exact
tool sequence — see §11.

## 9. Open backlog items (non-blocking)
- Possible future skill/tool to auto-summarize `Option` titles into
  `Considered Options` (explicitly not required now, drift accepted).
- ~~Whether `create_adr` needs a configurable numbering/filename scheme~~
  **Resolved, see §9a.**

## 9a. id/filename scheme and in-memory state (resolved)

Prompted by a design question: since `models/adr/v1/mutations.py` functions
take/return a whole in-memory `Adr`, but MCP tools (§8) only ever receive an
`id` string, does the MCP server need to cache parsed `Adr` objects in memory,
keyed by id? **No** — resolved as follows, keeping §7's "the `.md` file is
the sole source of truth, no assumption the tool is the sole writer" intact
and avoiding any server-side cache/staleness problem:

- **id:** a server-generated UUID (`str`), created once by `create_adr` and
  never reassigned. Persisted as a new `id` field on `AdrFrontmatter`
  (`models/adr/v1/frontmatter.py`) — optional (`str | None = None`, default
  `None`), the same non-breaking-addition pattern already used for `version`
  (§3/§6): existing/hand-authored files without an `id` still parse
  successfully, they are just not addressable via id-based tools until one is
  assigned. Rendered in `renderer.py`'s fixed frontmatter key order
  immediately before `version` (both are specmgr-only extensions, kept
  together after the MADR-defined keys).
- **Filename:** `f"{id}-{slug}.md"`, where `slug` is derived from `title` at
  `create_adr` time. There is no separate sequential `NNNN` counter — the
  UUID *is* the filename's identifying prefix, so there is no
  counter/race/gap-numbering concern (unlike the `Option` numbering in §5,
  which intentionally does have one).
- **id resolution (`id -> file path`):** every tool call scans the ADR base
  directory (`*.md`), parses each file's frontmatter via `parse_adr`, and
  matches on `frontmatter.id` — done fresh on every call, with **no
  in-memory cache**. This is the direct consequence of §7's design: the
  filesystem itself is the "memory" the LLM addresses by id, not the MCP
  server process. At expected ADR-repo scale (dozens to low hundreds of
  files) this is cheap enough; an id -> path cache was explicitly rejected
  because invalidating it correctly against concurrent human edits would
  reintroduce the exact staleness problem §7 avoids.
- **Base directory config:** environment variable `SPECMGR_ADR_DIR`, default
  `./docs/adr`. The MCP server is a long-running process with no CLI arg
  parsing of its own for this (`commands/mcp.py` only configures
  transport/host/port), so an env var is the natural channel; `commands/`
  ADR CLI commands (future work) read the same variable for consistency
  with the shared `models/adr/` implementation (ports-and-adapters, §6).
- **Listing:** `list_adrs` (§8) is implemented as an MCP **resource**
  (`specmgr://adr/list`, `@mcp.resource()`), not a `@mcp.tool()` — matching
  this repo's existing `resources/` convention (`specmgr://version`) rather
  than the generic `list_adrs()` tool name originally sketched in §8.
- **By-id read:** `specmgr://adr/{id}` is a second, template resource
  (`resources/adr.py`'s `adr_get`) alongside the `get_adr` MCP tool (§8) —
  both expose the identical read (same `find_adr_path`/`load_by_id`
  id-resolution, no cache), just through the two different MCP surfaces: the
  tool for an explicit LLM-invoked call, the resource for a host that wants
  to address a specific ADR as context (e.g. attach/subscribe) without a
  tool round-trip. The MCP SDK used here (`mcp>=2.0.0`) supports RFC 6570
  URI templates on `@mcp.resource()` — a `{param}` in the URI is
  auto-matched against a same-named function parameter.
- **`update_frontmatter`'s whole-object replace vs. the system-owned `id`:**
  `update_frontmatter(id, frontmatter)` still takes a full `AdrFrontmatter`
  per §3's "whole object, full replace" contract, but the tool wrapper always
  re-injects the *resolved* id after reconstructing the model, ignoring
  whatever `frontmatter.id` the caller submitted — the id is system-managed
  and never changes via this tool, even though every other frontmatter key
  follows normal full-replace semantics.

## 10. Next steps
1. **Done.** Pydantic models for frontmatter and body, under `models/adr/v1/`
   (§6): `AdrFrontmatter`, `AdrBody`, `AdrOption`, `Adr`.
2. **Done.** Parser (`models/adr/v1/parser.py`, `markdown-it-py` token walk →
   structured model, `parse_adr`/`AdrParseError`) and renderer
   (`models/adr/v1/renderer.py`, structured model → exact markdown,
   `render_adr`), alongside the models in `models/adr/v1/` (§6).
3. **Done.** `models/adr/v1/mutations.py`: the §4/§5/§8 edit semantics as
   pure, in-memory functions over `Adr` — `update_section`/`set_status`/
   `option_list`/`option_create`/`option_read`/`option_update`/
   `option_delete` — with deletion-sentinel handling and mandatory-section
   rejection (`AdrSectionError`) and not-found reporting
   (`AdrOptionNotFoundError`). Covered by
   `tests/models/adr/v1/test_mutations.py`. Deliberately excludes file I/O
   and id/filename lookup, which was `tools/adr/`'s job (item 4, now done).
4. **Done.** MCP tool wrappers under `tools/adr/` (§6), per the id/filename
   scheme resolved in §9a:
   - `models/adr/v1/frontmatter.py`/`renderer.py`: new `id` field (§3, §9a).
   - `models/adr/v1/summary.py`: new `AdrSummary` model (id/title/status/
     filename), re-exported through `models/adr/__init__.py` and
     `models/__init__.py`.
   - `tools/adr/_paths.py`: `adr_base_dir`/`ensure_adr_base_dir`
     (`SPECMGR_ADR_DIR` env var, default `docs/adr`), `slugify`,
     `iter_adr_paths`, `find_adr_path` (id → path via directory scan +
     parse, no cache, per §9a), `AdrNotFoundError`.
   - `tools/adr/_io.py`: `read_adr`/`write_adr`/`load_by_id` — thin
     `parse_adr`/`render_adr` + file I/O wrappers.
   - `tools/adr/`: the 11 `@mcp.tool()` wrappers from §8's list (`get_adr`,
     `create_adr`, `update_frontmatter`, `update_section`, `set_status`,
     `option_list`/`option_create`/`option_read`/`option_update`/
     `option_delete`, `validate_adr`), each doing the
     re-read/re-parse/mutate/re-render/re-write cycle per call. **Split one
     tool per module** (`get_adr.py`, `create_adr.py`, `update_frontmatter.py`,
     `update_section.py`, `set_status.py`, `option_create.py`,
     `option_update.py`, `option_read.py`, `option_delete.py`,
     `option_list.py`, `validate_adr.py`) rather than a single `tools.py` —
     `tools/adr/__init__.py` re-exports all 11 so `from biz.dfch.specmgr.tools
     import adr` (imported from `server.py`) still registers every
     `@mcp.tool()` decorator in one side-effecting import.
   - `resources/adr.py`: `specmgr://adr/list` resource (§9a), skipping
     unparseable files rather than failing the whole listing, plus the
     `specmgr://adr/{id}` template resource (`adr_get`) added afterward as
     a resource-based counterpart to the `get_adr` tool (§9a).
   - Covered by `tests/tools/adr/test_paths.py`, `test_io.py`, and one
     `test_*.py` per tool module (`test_get_adr.py`, `test_create_adr.py`,
     `test_update_frontmatter.py`, `test_update_section.py`,
     `test_set_status.py`, `test_option_create.py`, `test_option_update.py`,
     `test_option_read.py`, `test_option_delete.py`, `test_option_list.py`,
     `test_validate_adr.py`, mirroring the one-tool-per-module split above),
     plus `tests/resources/test_adr.py` — end-to-end through real
     temp-directory file I/O, not mocks. Full suite (143 tests),
     `ruff format --check`, and `ruff check` all pass.
5. **Done.** `tests/models/adr/v1/test_renderer.py` covers the renderer's own
   concerns: a golden-file test for a fully-populated ADR, per-field
   optional-section-omission tests, the zero-options "Pros and Cons" heading
   omission, option numbering-gap preservation, the `id` emission-order/
   omission-when-`None` behavior (§9a), and a drift-check (`render(parse(file))`
   is a stable, idempotent fixed point) against the real
   `adr-template-valid.md`/`adr-template-minimal-valid.md` fixtures plus a
   constructed full ADR. The model-layer counterparts of the
   previously-blocked cases — mandatory-deletion error, sentinel deletion,
   and option add/remove/numbering-gap — are covered by item 3's
   `test_mutations.py`; the end-to-end tool-layer counterparts (same
   behavior through actual file I/O) are covered by item 4's per-tool test
   modules under `tests/tools/adr/`.
6. Wire `validate_adr` into CI/pre-commit. **Partially done** — the
   `validate_adr` MCP tool now exists (item 4: re-reads/re-parses by id,
   letting the models' own Pydantic validators run, per §7, propagating
   `AdrParseError`/`ValidationError` on failure). **Not yet done:** a
   corresponding `commands/` CLI command and a CI/pre-commit hook that calls
   it over every ADR file, independent of the MCP server.
7. **Done.** `server.json` (repo root) — the MCP Registry publisher manifest
   (`https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`),
   validated against the official draft `server.schema.json`. Models the
   `pypi` package `biz-dfch-specmgr` and encodes the exact invocation already
   documented in `README.md`'s "Add to OpenCode" section —
   `uvx --from biz-dfch-specmgr[mcp] python -m biz.dfch.specmgr mcp` — via
   `runtimeArguments` (`--from biz-dfch-specmgr[mcp]`, then `python`) plus
   `packageArguments` (`-m biz.dfch.specmgr mcp`), rather than the package's
   own `specmgr` console-script entry point, since the entry-point name
   doesn't match the PyPI package name and `uvx <package>` alone would try to
   run a script called `biz-dfch-specmgr`. Declares the four `commands/mcp.py`
   environment variables (`SPECMGR_MCP_TRANSPORT`/`_HOST`/`_PORT`) plus
   `SPECMGR_ADR_DIR` (§9a) so registry clients can surface/configure them.
   `name` is `io.github.dfch/biz.dfch.specmgr`, matching this repo's verified
   GitHub namespace (`github.com/dfch`); `repository.id` is the numeric
   GitHub repo id (`1321701564`, from `gh api repos/dfch/biz.dfch.SpecMgr
   --jq '.id'`), per the schema's repository-resurrection-detection guidance.
   **Done.** The package is now published to PyPI: `biz-dfch-specmgr`
   `0.1.0` was released via `v0.1.0` (`.github/workflows/publish.yml`,
   Trusted Publishing/OIDC, no stored token) and is live at
   `https://pypi.org/project/biz-dfch-specmgr/`. `server.json` has also
   been submitted to and accepted by the official MCP Registry — confirmed
   live at
   `https://registry.modelcontextprotocol.io/?q=io.github.dfch%2Fbiz.dfch.specmgr`
   (`io.github.dfch/biz.dfch.specmgr` version `0.1.0`, status `active`).
   `version` in `server.json` must be bumped in lockstep with
   `pyproject.toml`'s `version` on every subsequent release, and the
   registry re-published via `mcp-publisher` each time, to stay in sync
   (same discipline as `CHANGELOG.md`, see `AGENTS.md`).
8. **Done.** `prompts/adr/` (§11): two `@mcp.prompt()`s, `create_adr` and
   `update_adr`, one module per prompt mirroring `tools/adr/`'s own
   one-item-per-module split, wired into `server.py` alongside the
   existing `resources`/`tools` side-effecting imports. Covered by
   `tests/prompts/adr/test_create_adr.py`/`test_update_adr.py`.

## 11. Prompt surface (MCP prompts)

Two `@mcp.prompt()`s in `prompts/adr/` (mirroring the `models/`/`tools/`/
`resources/` per-document-type sub-package convention from §6) return plain
instructional text — not tool calls themselves — that guide an LLM through
driving the §8 tool surface in the right order. Registered via
`server.py`'s `from . import prompts, resources, tools` side-effecting
import, exactly like `tools/`/`resources/` already are.

- **`create_adr(topic, decision_makers=None, consulted=None, informed=None)
  -> str`** (`prompts/adr/create_adr.py`): drafting a brand-new ADR.
  - Instructs the LLM to read the `specmgr://adr/list` resource *first* and
    check for an existing ADR on a similar topic, surfacing it to the user
    (and suggesting `update_adr` instead) rather than creating a duplicate.
  - Recaps the MADR structure (§2) and the mandatory/optional split (§3/§4).
  - Specifies the exact tool sequence: `create_adr(frontmatter, body)` (with
    `options=[]`) → one `option_create` call per considered option worth
    writing up → optional `set_status` → always `validate_adr(id)` last.
  - `decision_makers`/`consulted`/`informed` are optional pre-fills;
    when absent the returned text tells the LLM to ask the user rather than
    guessing or silently omitting them.
- **`update_adr(id, instructions=None) -> str`** (`prompts/adr/update_adr.py`):
  revising an existing ADR by id.
  - Instructs the LLM to call `get_adr(id)` (or read `specmgr://adr/{id}`)
    first, never assuming prior state.
  - When `instructions` is absent, tells the LLM to ask the user what
    should change before calling any write tool.
  - Maps a requested change onto the right tool: whole-section prose →
    `update_section` (mandatory-section-rejection/deletion-sentinel rules
    per §4 apply); status → `set_status`; other frontmatter fields →
    `update_frontmatter` (calling out its whole-object-replace semantics —
    unrelated fields must be carried forward from the just-read state, per
    §3); options → `option_create`/`option_update`/`option_delete` (no
    renumbering on delete, per §5).
  - Always finishes with `validate_adr(id)`.

**Naming note:** the `create_adr` *prompt* shares its name with the
`create_adr` *tool* (§8). This is intentional and not a collision — MCP
keeps prompts and tools in separate registries (`prompts/list` vs.
`tools/list`) — but is called out in `prompts/adr/create_adr.py`'s own
module docstring so the two are never mistaken for the same registration.

**Step-gated test variants (`create_adr_test`/`update_adr_test`):** prompted
by the open question of how far prompt text alone can *force* an LLM to
follow a fixed sequence (vs. tool-side Pydantic validation, which only
catches malformed/blank content, not fabricated-but-well-formed content; vs.
real MCP elicitation, which removes the LLM from the answer-collection loop
entirely but needs client-side support this repo hasn't wired up yet),
`prompts/adr/create_adr_test.py`/`update_adr_test.py` register two more
prompts under distinct names (`create_adr_test`, `update_adr_test`, no
collision with anything in §8). Same parameters, same underlying MADR
structure and `tools/adr/` sequence as `create_adr`/`update_adr`, but the
narrated steps are rewritten as hard numbered `GATE 0`..`GATE N` blocks,
each with an explicit "Exit condition", an explicit "do not proceed until
this is met", and a standing "never fabricate a value to pass a gate"
instruction — most pointedly in `create_adr_test`'s `GATE 2`, a checklist
of the four mandatory body fields that must each be backed by an actual
user answer, not a model guess. These exist purely so a caller can switch
between the narrated and gated variant for the same task and compare
compliance — no code elsewhere depends on which one is used, and neither
supersedes the other.
