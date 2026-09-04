# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dedicated Pydantic models with drift-guard unittests for
  `specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`,
  and `specmgr://rasci`; all four are now also parsed on every resource
  call to fail fast on structural drift, discarding the parsed result,
  matching `specmgr://iso25010`'s existing pattern. New
  `specmgr://ears` resource documenting the EARS (Easy Approach to
  Requirements Syntax) five requirement-phrasing templates, likewise
  backed by a model and drift-guard tests. New ADR
  (356d8781-e446-4c26-917a-eda85648ce9d) documenting the resulting
  repo-wide convention for reference resources (GitHub issue #92).

### Changed

- `specmgr://iso25010` now returns raw markdown (`text/markdown`)
  instead of a structured `Iso25010` JSON object, still parsed via
  `parse_iso25010()` on every read to fail fast on structural drift
  (GitHub issue #92).

## [0.21.0] - 2026-09-03

### Changed

- README now flags the Architecture Decision Record (ADR) artifact type
  as deprecated in favor of Decision (DEC).

### Fixed

- Replaced round, all-zero-time-of-day placeholder timestamps (frontmatter
  `created`/`updated`, and `feat`'s body-level `#### {timestamp}` headings)
  across all 24 affected domain template/example files with realistic,
  non-round values, so they no longer invite copy-paste-without-substitution
  (GitHub issue #67).

## [0.20.0] - 2026-09-03

### Added

- `confluence_update` now sets the Confluence page's title from the source
  markdown's first H1 heading, falling back to the existing (GET-fetched)
  title unchanged when no H1 is present (GitHub issue #76).

### Fixed

- `specmgr://config` now reports the `sysrs` domain (it was missing from
  the resource's `domains` dict even though `sysrs` was already fully
  wired into every dispatch tool), matching every other domain's entry
  (GitHub issue #74).
- Corrected stale/incorrect copyright holders in `NOTICE` for `pydantic`,
  `python-dotenv`, `typer`, `rich`, and `mcp`; added missing attributions
  for `mdformat`, `mdformat-simple-breaks`, and `httpx` (GitHub issue #73).

## [0.19.0] - 2026-09-03

### Changed

- On a successful write, the generic `update`, `set_status` (its twelve
  non-`adr` adapters), and `set_classification` tools, and every
  per-domain `create_<d>` tool (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/
  `dec`/`sop`/`feat`/`vcr`/`sysrs`), now return the domain's frontmatter
  object only, instead of the full document with its (potentially large,
  ever-growing) body. The `adr` dispatch branch of `set_status` and every
  ADR-specific tool (`create_adr`, `update_frontmatter`, `update_section`,
  the `option_*` tools) are unchanged and still return the full document
  (GitHub issue #69).

## [0.18.0] - 2026-09-02

### Added

- New `sysrs` (System Requirements Specification) domain: an aggregator
  document type that ties together existing `gol`/`prb`/`qa`/`uc`/`req`/
  `rsk`/`dec`/`adr`/`vcr` artifacts into one coherent, navigable
  specification via per-section, type-tagged cross-reference lists (e.g.
  `### Goals` accepts only `GOL` bullets, `## Decisions` accepts `DEC` or
  `ADR`, and the nine `## Requirements` H3s plus six `## Other
  Characteristics` H3s each accept only `REQ`) rather than duplicating
  their content. Dispatch-only from day one, with no `update_sysrs`/
  `set_status_sysrs` tools of its own — whole-body/line-range updates,
  status changes, classification changes, and deletions all go through
  the existing generic `update`/`set_status`/`set_classification`/
  `delete` tools (`type="sysrs"`). Ships 7 tools (`create_sysrs`,
  `parse_sysrs`, `list_sysrs`, `get_sysrs`, `get_sysrs_example`,
  `get_sysrs_template`, `validate_sysrs`), 3 resources
  (`specmgr://sysrs/schema`, `specmgr://sysrs/example`,
  `specmgr://sysrs/template`), and 2 prompts (`create_sysrs`,
  `update_sysrs`) (GitHub issue #32).

- New `specmgr://config` resource: reports, for all twelve document
  domains, the resolved absolute base directory and whether the domain's
  `SPECMGR_*_DIR` environment variable is explicitly set, so a client can
  self-diagnose a working-directory-relative base-directory
  misconfiguration. Only the twelve known env var names are ever read
  (never `os.environ` wholesale), so no unrelated secret is ever
  disclosed. The "Add to OpenCode" README example now shows two
  alternatives for pinning the resolved base directory — `uv`/`uvx`'s
  `--directory` flag, or explicit `SPECMGR_*_DIR` environment variables in
  the MCP client config — and documents the previously-missing
  `SPECMGR_FEAT_DIR` variable (GitHub issue #51).

- `create_uc`/`update_uc` MCP prompts for the `uc` (Use Case) domain,
  mirroring the `req` domain's prompt pattern and including
  `set_classification` guidance (GitHub issue #57).

### Fixed

- `format_text()`/`format_markdown_document()` (`models/md/_markdown.py`),
  and transitively every domain's `parse_<d>`/`create_<d>`/`validate_<d>`/
  `update` path plus the `mdformat` CLI command and MCP tool, now render a
  thematic break (`---`, `***`, `___`, or any other CommonMark-valid
  variant) as a literal `---` instead of `mdformat`'s hardcoded 70-character
  underscore line (`"_" * 70`, not otherwise configurable upstream — see
  executablebooks/mdformat#69). Fixed by wiring the third-party
  `mdformat-simple-breaks` plugin (pinned exactly, `==0.1.0`) into the
  shared `mdformat.text(...)` call via its `mdformat.parser_extension`
  entry point (GitHub issue #47).

## [0.17.0] - 2026-09-02

### Added

- `create_feat` (feat domain) now accepts an optional, caller-chosen
  `id: str | None = None` parameter — a full, well-formed `feat-NNN-slug`
  value, validated via `assert_feat_id` (`general/tools/_path_safety.py`)
  before any lock/filesystem access. When `id` is omitted, the default is
  now `feat-0-<slug-from-title>` — the previous `feat-{max existing NNN +
  1}-{slug}` auto-increment fallback is gone entirely, since `NNN` is
  meant to be the GitHub issue number a feature tracks, and `feat-0-...`
  now signals "no issue yet" rather than a scan-derived guess. Either way
  (caller-supplied or defaulted), `create_feat` raises `FileExistsError`
  before any write if the resulting id/folder already exists, and raises
  `ValueError` before any write if a caller-supplied `id` doesn't match the
  `feat-NNN-slug` shape. A new `set_feat_id(id, new_id)` `@mcp.tool()`
  (feat domain, `feat/tools/set_feat_id.py`) complements this by letting an
  existing feature's id be renamed afterwards (e.g. once its GitHub issue
  number becomes known): it validates `new_id`'s shape, refuses via
  `FileExistsError` if the target folder already exists, renames
  `<base>/<id>/` to `<base>/<new_id>/`, rewrites the frontmatter `id` and
  bumps `updated`, leaves the body byte-identical, and raises
  `FeatNotFoundError` if `id` does not resolve. It runs under
  `feat_create_lock()` (outermost) then `feat_lock(id)` (nested) to avoid
  races with `create_feat`/`update`/`set_status`/`delete` on the same id.
  `feat` remains dispatch-only for whole-body updates/status changes — no
  `update_feat`/`set_status_feat` tool of its own; `set_feat_id` is a
  distinct, bespoke tool for id changes specifically (GitHub issue #48).

- Windowed raw reads on the eleven `get_<d>` MCP tools
  (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`):
  each now accepts optional read-style `offset`/`limit` coordinates for a
  windowed raw read — valid with `raw=True` only (coordinates with
  `raw=False` raise `ValueError`), `offset` 1-based with default 1
  (floored, never errors), `limit` a line count defaulting to through end
  of body (capped at the remaining lines), and `offset > N` returning the
  empty string; out-of-range values clamp, consistent with the `list_<d>`
  paging convention. The window is served by a new no-I/O
  `window_body(text, offset, limit)` helper in `general/tools/_splice.py`,
  beside `body_text`/`splice_body`, so the raw/splice invariant (the line
  numbers a client sees in any `get_<d>(raw=True)` read, windowed or not,
  index byte-for-byte into the same text the generic `update` tool splices
  against) is defined once and shared by all eleven tools (GitHub issue
  #28; ADR 4ec08dcb-fcb7-4961-abaf-ff7803e2f21d).

- `confluence_update` MCP tool (`general/tools/`): writes a local Markdown
  file's rendered content into an existing Confluence page's body via the
  REST API, resolving a bare page id, a browsable page URL, or a REST
  content URL to a numeric page id, `GET`-ing the page's current
  `version`/`title`, rendering the Markdown via `markdown-it-py` to an
  HTML fragment, and `PUT`-ing the incremented version. Local images
  referenced by the Markdown file are uploaded as Confluence attachments
  on a best-effort basis (`POST .../child/attachment`, falling back to
  `.../child/attachment/{id}/data` if the filename already exists --
  duplicate-filename detection is confirmed against a real Confluence
  server's actual 400 response, "Cannot add a new attachment with same
  file name as an existing attachment: `<filename>`. Log referral number
  is `<uuid>`") and their `<img>` tags are rewritten into Confluence's
  `<ac:image>`/`<ri:attachment>` storage-format macro. Also sanitizes any
  raw `--` sequence inside rendered `<!-- -->` HTML comments (valid
  CommonMark but rejected outright by Confluence's strict XHTML
  storage-format parser, confirmed against a real instance: `"Error
  parsing xhtml: String '--' not allowed in comment"`) and converts a
  leading YAML frontmatter block into a fenced code block before
  rendering, instead of letting CommonMark's thematic-break/Setext-heading
  rules mangle it into a stray `<h2>` heading (also confirmed against a
  real instance). Closes GitHub issue #50, per ADR
  a156fdf9-052c-4f43-93a2-eeec04a91eac.
- `confluence_update`/`confluence_fetch` MCP prompts (`general/prompts/`):
  thin, single-tool-call prompts sharing their respective tools' exact
  names (a separate MCP registry from tools). Each returns instructional
  text telling the LLM to call the matching `confluence_update`/
  `confluence_fetch` tool with the given parameters -- neither prompt ever
  calls its tool itself. `confluence_update` also tells the LLM to report
  back the tool's returned `version`/`failed_images`; `confluence_fetch`
  documents that `destination_path` is only required for binary/non-text
  content. Part of feat-50-confluence Phase 8, REQ-012/REQ-013.

- Optional, free-text `classification` frontmatter field on the shared
  `MarkdownFrontmatter` base, inherited by all eleven whole-body domains
  (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`; ADR
  excluded, since it has its own separate frontmatter model). A new
  generic `set_classification(id, type, classification)` MCP tool
  (`general/tools/`) mirrors `set_status`'s dispatch pattern to change it
  after creation, bumping `updated` and leaving the body and every other
  frontmatter field untouched; a blank/whitespace-only value clears
  `classification` back to `None`/absent, same as every other optional
  frontmatter field's blank-to-`None` normalization. Existing documents
  without a `classification` key keep parsing unchanged. The ten
  whole-body domains' packaged create/update prompt instruction files
  (`uc`, which has no prompts sub-package yet, is untouched) now mention
  `set_classification` alongside the existing `set_status` mentions
  (GitHub issue #56).

### Changed

- **BREAKING** (0.x): the generic `update` MCP tool's 1-based inclusive
  `begin`/`end` body-line range (with the `N+1` end-of-body sentinel) is
  replaced by read-style `offset`/`limit` coordinates in a hard rename (no
  compatibility alias): `offset` is the 1-based first line to replace
  (allowed `1..N+1`, where `N+1` is the virtual end-of-body append
  position), `limit` is the number of lines (`offset..offset+limit-1`);
  omitted `limit` replaces through the last body line, `limit=0` is a pure
  insert. Out-of-range coordinates raise `ValueError` (strict, never
  clamped, nothing written) and `limit` without `offset` raises
  `ValueError` before any file access; splice-then-validate-whole, verbatim
  persistence, and frontmatter carry-over are unchanged. Every LLM-facing
  surface (the packaged prompt instruction files, tool descriptions,
  docstrings, `AGENTS.md`) moved to the new vocabulary in this same
  release. The revised contract is recorded in ADR
  4ec08dcb-fcb7-4961-abaf-ff7803e2f21d (referencing, not superseding, ADR
  36905d5b-8057-4294-8665-c7eed5534db0) (GitHub issue #28).

- Eliminated all 42 pylint W0622 (redefined-builtin) findings via 39
  explicit, per-file `# pylint: disable=redefined-builtin` comments (with
  a one-line rationale) on the files whose public API intentionally uses
  `id`/`type` as parameter names — the twelve `get_<d>` tools, the
  per-domain update/implement prompts, the ADR tools/resources/prompts,
  the generic `update`/`set_status`/`delete` public functions, and
  `models/md/markdown.py`/`alias.py`. Not breaking — no behavior change,
  purely an internal lint-suppression change. No global `pyproject.toml`
  pylint configuration change: a future file that shadows a builtin
  without adding its own disable comment still warns (GitHub issue #41,
  Phase 5 of feat-38-39-41-43-44).

- The twelve `get_<d>` tools (including `get_adr`), the generic `update`
  tool, and the generic `set_status` tool now validate `id` for
  path-injection/wrong-format before any filesystem access, and confine
  the resolved path to the domain's own base directory after resolution —
  the same `general.tools._path_safety` guards the generic `delete` tool
  already had (feat-36-delete). `_path_safety.validate_id` now also
  accepts `"adr"` as a UUID-shaped domain. This is purely additive
  validation: a previously well-formed id for its domain is unaffected; a
  path-injection attempt or a malformed id — which would already have
  failed downstream (e.g. via a `FileNotFoundError`/`XNotFoundError`) —
  now fails earlier and more explicitly with a `ValueError`. `delete`
  itself is unchanged (GitHub issue #43, Phase 4 of
  feat-38-39-41-43-44).

- **BREAKING**: renamed the `webfetch` MCP tool to `confluence_fetch` (and
  its environment variables `SPECMGR_WEBFETCH_BASE_URL`/
  `SPECMGR_WEBFETCH_BEARER` to `SPECMGR_CONFLUENCE_BASE_URL`/
  `SPECMGR_CONFLUENCE_BEARER`); part of feat-50-confluence. Beyond the
  rename, `confluence_fetch` now auto-converts browsable Confluence page
  URLs (Cloud-style `/pages/<id>/<title>` and Server-style
  `?pageId=<id>`) into the equivalent
  `{base}/rest/api/content/{id}?expand=body.storage` REST API URL before
  fetching, rejects the `/x/<tinyid>` tiny-link URL shape with a clear
  error (unresolvable to a page id without an authenticated browser
  session), detects when a request is redirected off the configured base
  URL's host (e.g. to an SSO login page) and raises instead of returning
  that content, and supports binary/image download via a
  `destination_path` parameter (content-type based). GitHub issue #50,
  ADR a156fdf9-052c-4f43-93a2-eeec04a91eac.

- **BREAKING**: frontmatter `created`/`updated` now strictly require the
  date+time variant `yyyy-MM-dd HH:mm:ss.fff` followed by `Z` (UTC) or a
  signed `±HH:mm` offset — date-only, `T`-separated, six-digit-microsecond,
  and timezone-less values are all rejected at parse time
  (`pydantic.ValidationError`), eagerly, on the shared
  `MarkdownFrontmatter` base every one of the eleven whole-body domains'
  frontmatter subclasses inherits from. Every tool-written `created`/
  `updated` value — across all 11 whole-body `create_<d>` tools, the 22
  generic `update` adapter sites, and the 11 generic `set_status` adapter
  sites — is now produced by one shared helper
  (`general.tools._timestamps.now_timestamp()`) that guarantees this exact
  shape (local time via `datetime.now().astimezone()`, `Z` when the UTC
  offset is exactly zero, milliseconds truncated to exactly three digits).
  ADR frontmatter is unaffected (it has no `created`/`updated` fields).
  Existing documents with a non-conforming frontmatter timestamp must be
  migrated to the new shape before they will parse again — the repo's own
  artifacts (the release SOP, the two `docs/tsk` documents, every
  `.specmgr/feat/*/README.md`'s frontmatter, and every packaged
  template/example) were migrated as part of this change (GitHub issue
  #44, Phase 3 of feat-38-39-41-43-44).

- **BREAKING**: SOP `## Updates`, DEC `## Updates`, VCR `## Updates`, and
  TSK `## Recent Updates` now enforce newest-first ordering at parse
  time — an entry whose timestamp precedes (is older than) the entry
  above it fails to parse (`AssertionError`/`ValidationError`), eagerly,
  at construction time. Consecutive entries are compared with an aware
  `datetime` comparison; when either side is a bare date (no time
  component) the comparison happens at day granularity, so a date-only
  entry and a same-day date+time entry are treated as equal, and equal
  timestamps are always allowed (non-strict "newest-first"). DEC/VCR/TSK
  update-entry headings, previously free-form, are now themselves
  timestamp-led: `### {yyyy-MM-dd or yyyy-MM-dd HH:mm:ss.fff±HH:mm/Z}
  ( - | : ) {title}`, mirroring SOP/FEAT's existing shape — a heading
  that does not start with a valid date fails to parse. The SOP/DEC/TSK
  update containers gained leading-HTML-comment support (promoted from
  `MarkdownSection2` to `MarkdownSection2WithComment`; VCR already had
  it), so all four now carry a `<!-- Newest entry first -- prepend new
  entries directly below this comment. -->` ordering hint in their
  packaged templates, and the create/update instructions of all four
  domains now direct prepending new entries instead of appending them.
  Existing out-of-order or non-timestamp-led SOP/DEC/VCR/TSK documents
  must be migrated to the newest-first, timestamp-led shape before they
  will parse again (GitHub issue #39, Phase 2 of
  feat-38-39-41-43-44).

- **BREAKING**: update-entry headings no longer accept an em-dash (`—`)
  separator between the timestamp and the title. SOP `## Updates`
  (`### {timestamp} - {title}`/`### {timestamp} : {title}`) and FEAT
  `## Updates`/`### Decisions Made` (`#### {timestamp} - {title}`/
  `#### {timestamp} : {title}`) now only accept `" - "` (space, hyphen,
  space) or `" : "` (space, colon, space) as the separator; an em-dash
  entry fails to parse (`AssertionError`/alias mismatch), eagerly, at
  construction time. Existing SOP/FEAT documents using the em-dash
  separator must be migrated to `" - "` or `" : "` (GitHub issue #38,
  Phase 1 of feat-38-39-41-43-44). DEC/VCR update-entry convention text
  (docstrings, packaged templates/examples/create-instructions) was
  updated to the same separators for consistency, though those two
  domains' `## Updates` headings remain free-form and unenforced until
  Phase 2.

### Fixed

- `specmgr docs`: stale per-module API pages are now pruned.
  `_generate_api_docs` only ever *wrote* pages, so a module removed from
  `src/` left its `docs/api/*.md` page behind forever — an orphaned file
  no longer linked by the regenerated `api/README.md` index. It now
  deletes every flat `*.md` file in the output `api/` directory that is
  neither the `README.md` index nor a page written by the same run —
  never touching `README.md`, non-`.md` files, or nested directories.
  Pruning is skipped entirely rather than deleting the existing tree on
  any untrustworthy run (zero pages written, any module import failure,
  or truncated module collection), so a partial-import environment can
  never wipe the tree. `docs()` echoes `✓ Pruned {n} stale page(s) from
  {api_dir}` only when n > 0 (unchanged-tree output stays unchanged) plus
  a one-line `⚠` warning when pruning was skipped due to import
  problems. The first run with pruning enabled deleted the five real
  stale pages left by feat-13-list-paging's resource→tool conversion
  (`biz.dfch.specmgr.{adr,qa,req,tsk,uc}.resources.*_list.md`) (GitHub
  issue #40).
- Every validation error surfaced by the `parse_<d>`/`create_<d>`/
  `validate_<d>` MCP tools (all twelve document types) and the generic
  `update`/`set_status` tools is now actionable instead of a bare,
  uninformative message. Structural `AssertionError`s now carry a
  document-relative field path (e.g. `Task > RecentUpdates > UpdateEntry
  > content`), a 1-based line reference into the mdformat-normalized body
  plus a snippet of the offending text, and what was expected. For the
  two triggers that motivated this fix specifically: a bare `<word>`-style
  token is rejected as raw HTML with a fix hint ("wrap it in a code span,
  or write it as an HTML comment"), and a `+`/`-`/`*`-prefixed
  continuation line gets a cause + fix hint ("this begins a new
  CommonMark list; remove the marker or indent the line so it belongs to
  the preceding block instead"). Malformed frontmatter YAML
  (`yaml.YAMLError`) now names "the frontmatter block" instead of
  PyYAML's opaque `"<unicode string>"`, with document-relative (not
  block-relative) line numbers. Every touched tool additionally prepends
  its own domain + tool context (e.g. `"tsk create_tsk (body): ..."`). No
  new exception types and no channel changes throughout — the documented
  two-channel contract (`AssertionError` structural / `pydantic.
  ValidationError` value) is preserved exactly; only message content
  changes (GitHub issue #27; subsumes feat-7's not-started Task 0.29).

## [0.16.0] - 2026-09-01

### Added

- Generic `delete(id, type)` MCP tool in `general/tools/`: the
  type-dispatched hard-delete for the eleven whole-body domains (`type` is
  one of `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`;
  `adr` is not supported). Resolves the document by `id` under the
  domain's own per-id lock and removes it — the single `*.md` file for the
  ten flat domains, or the entire `<base>/<id>/` folder for `feat` —
  returning the deleted path as a string. An invalid `id` (path-injection
  attempt or wrong format) is a `ValueError` raised before any file access;
  a missing document is the domain's own `XNotFoundError`; an I/O failure
  during the delete is a `DeleteError` (an `OSError` subclass). This is
  the sole delete entry point: every current and future domain implements
  a `delete` adapter in the generic tool, never a per-domain `delete_<d>`
  tool.
- A reusable, doc-type-agnostic path-safety module
  `general/tools/_path_safety.py`: `assert_no_traversal`, `assert_uuid`,
  `assert_feat_id`, `validate_id`, and `assert_within` — pure, no-I/O
  guards preventing path-injection through `type`/`id` inputs and confining
  resolved paths to their base directory. Wired into the new `delete` tool
  now; designed so the `get_<d>`, `update`, and `set_status` tools can
  adopt it later with zero rework (they are not modified in this change).

### Changed

- The release SOP (now `active` — its status was `draft` until the first
  release executed under it succeeded end to end, v0.15.0) was clarified:
  tool prerequisites and the stage-to-step execution map up front in
  Scope, the fast-forward-only merge mechanism the script actually uses
  (pre- and post-merge SHA assertions around the plain merge method,
  replacing the description of a nonexistent `gh pr merge --ff-only`),
  the publication workflow's name ("Publish to PyPI") vs. file
  (`.github/workflows/publish.yml`) distinction, and a dedicated
  precaution about the old `gh` 2.4.0 the script targets.

### Removed

- **BREAKING** (0.x): the eleven per-domain `delete_<d>` stub MCP tools are
  deleted outright (no deprecated wrappers): `delete_req`, `delete_uc`,
  `delete_tsk`, `delete_qa`, `delete_prb`, `delete_gol`, `delete_rsk`,
  `delete_dec`, `delete_sop`, `delete_feat`, `delete_vcr` — each was a
  registered stub that always raised `NotImplementedError`. The eleven
  per-domain `delete_<d>.py` modules, their `__init__.py` registrations,
  and their stub tests are gone with them. Callers must switch from
  `tools/call --tool-name delete_<d>` to `tools/call --tool-name delete`
  with the explicit `type` parameter (see "Added" above).

### Fixed

- `scripts/release.sh`: the `pr-merge`, `publish-wait`, `status`, and
  `release-notes` stages no longer rely on `gh` CLI features that do not
  exist in this environment's `gh` 2.4.0 — a nonexistent `--ff-only`
  merge flag, `gh run list --commit`, `gh run view --json jobs`, and
  `gh release view --json`/`gh release edit`. Fast-forward-only merging
  is now enforced by pre-merge and post-merge SHA assertions around the
  plain merge method; the publication run is located by workflow name
  ("Publish to PyPI") plus the tag's commit SHA (filtered with `jq`);
  the GitHub Release is read and its notes set through `gh api`.

## [0.15.0] - 2026-08-31

### Added

- **Tenth domain feature (SOP/Standard Operating Procedure tooling)**: new
  document-type domain, `sop`, for structured, step-by-step operational
  documents with a RASCI-style responsibility assignment and a closed
  five-value approval/effectivity lifecycle (`draft` → `review` → `approved`
  → `active` → `retired` — status changes only via a manual `set_status`
  call, never automatic). Built on the generic `models.md` parser with the
  GOL/RSK/QA/DEC simple surface (no fine-grained mutation tools, no
  renderer — writes persist the caller's raw validated body byte-for-byte)
  and the first domain built dispatch-only from day one (ADR
  36905d5b-8057-4294-8665-c7eed5534db0) — no per-domain
  `update_sop`/`set_status_sop` tools: whole-body and line-range updates go
  through the generic `update` tool (`type="sop"`), status changes through
  the generic `set_status` tool (`type="sop"`, asserting `superseded_by` is
  `None` for SOPs):
  - `sop/models/v1/`: Pydantic schema (`SopFrontmatter` narrowing `type`
    to `Literal["sop"]` and `status` to the five-value lifecycle, default
    `draft`; `Sop` body with mandatory `## Purpose` and `## Procedure` — the
    latter carrying at least one `### Step {N}: {name}` entry,
    regex-`@alias`-constrained with number/name computed from the heading
    and duplicate step numbers rejected — plus optional `## Scope`,
    `## Definitions`, `## Safety and Precautions`, a RASCI
    `## Roles and Responsibilities` composite (mandatory `### Accountable`
    single paragraph + `### Responsible` list once present, optional
    `### Support`/`### Consulted`/`### Informed` that MAY be present with
    zero items), `## Related Artifacts` with five all-optional
    cross-reference lists (requirements/decisions/goals/acceptance
    criteria/sops), and `## More Information`/`## Updates`
    (ISO8601-timestamped `###` entries, last section if present)), parser,
    `SopSummary`, and JSON schema generation, inside the domain package
    itself.
  - `sop/tools/`: `@mcp.tool()` wrappers for the SOP lifecycle
    (`create_sop` — fixes `status: draft`, writes `sop-{id}-{slug}.md`,
    `parse_sop`, `list_sop` (paged, default 25/cap 100), `get_sop` with
    `raw`, `get_sop_example`, `get_sop_template`, `validate_sop`), plus a
    `delete_sop` stub.
  - `sop/resources/` (`specmgr://sop/schema`, `specmgr://sop/example`,
    `specmgr://sop/template` — no `specmgr://sop/{id}`, no
    `specmgr://sop/list`) and `sop/prompts/` (`create_sop`/`update_sop`,
    each with an explicit `specmgr://rasci` read-first step before
    `## Roles and Responsibilities`; `create_sop` first checks `list_sop`
    for a near-duplicate SOP).
  - A cross-cutting `specmgr://rasci` resource (`general/resources/`,
    REQ-011) — the generic RASCI role definitions used by the SOP's
    `## Roles and Responsibilities` section, kept in `general/` rather than
    under `sop/resources/` since it is domain-knowledge other document
    types may also want to reference (mirroring RSK's
    `specmgr://rsk/tara` shape).
  - A new shared `PagedResult` model (`general/models/paged_result.py`)
    backing paged list summaries, plus `specmgr schema --type sop`
    generating `docs/sop_schema.json` and the packaged copy;
    `.pre-commit-config.yaml` and the CI schema-drift hooks extended for
    the new domain.
  - `server.py` updated to import the new `sop` domain package;
    `.pre-commit-config.yaml`, `AGENTS.md`, and root `README.md` updated
    for the tenth domain.
- **Staged release automation, the `/release` command, and the release
  SOP**: new `scripts/release.sh` — a deterministic, idempotent stage
  projection of the new normative SOP "Perform a release of
  biz.dfch.SpecMgr" (draft, `docs/sop/`): `resolve`, `precheck`, `bump`,
  `changelog`, `commit-push`, `pr-create`, `pr-merge`, `tag-push`,
  `publish-wait`, `release-notes`, plus read-only `status` and interactive
  `all`. It enforces the fast-forward-only `dev`→`main` merge invariant,
  the exactly-three-file release commit (`pyproject.toml`, `uv.lock`,
  `CHANGELOG.md`), and green-CI gates before every irreversible step (the
  tag push starts TestPyPI → PyPI → GitHub Release → MCP Registry
  publication), leaving the maintainer merge gate to a human. Alongside it,
  the new `/release` OpenCode command (`.opencode/command/release.md`) that
  drives the stages and performs the agent-judgment steps (version
  confirmation, changelog curation, merge gate, failure triage); the README
  "Make a Release" section is rewritten around the SOP-based flow.
- **Twelfth domain feature (VCR/Verification Case Record tooling)**: new
  document-type domain, `vcr`, capturing how a single REQ/UC is verified --
  a coverage assessment plus a list of DTAIS-classified acceptance
  criteria. Fills a gap identified during `feat-32-sysrs` planning (no
  existing domain modeled ISO/IEC/IEEE 29148's/MITRE SE Guide's
  "Verification / Test and Evaluation" concept). Follows the domain-first
  hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and lands on the
  "simple surface" from day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0
  -- no per-domain mutation tools, including no per-AC create/read/update/
  delete tools):
  - `vcr/models/v1/`: Pydantic schema (`VcrFrontmatter` with a closed
    4-value status set `draft`/`progress`/`complete`/`approved`, `Vcr` body
    with a mandatory `## Verifies` single-value cross-reference (exactly
    one `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase --
    not a bullet list), a mandatory `## Coverage` closed-vocabulary outcome
    signal (`full`/`partial`/`none`), a mandatory `## Acceptance Criteria`
    collection of `### AC-NNN (Method): ...` entries (3-digit zero-padded
    number, closed **DTAIS** method vocabulary parsed from the heading via
    regex, optional `description` paragraph and/or `#### Test Steps`
    numbered procedure, duplicate-number rejection via `model_validator`),
    and optional `## More Information`/`## Updates`), parser (`parse_vcr`),
    `VcrSummary`, and JSON schema generation, inside the domain package
    itself.
  - `vcr/tools/`: `@mcp.tool()` wrappers for the VCR lifecycle (`create_vcr`,
    `parse_vcr`, `list_vcr`, `get_vcr` with `raw`, `get_vcr_example`,
    `get_vcr_template`, `validate_vcr`), plus a stub for `delete_vcr`.
    Generic `update(type="vcr", ...)`/`set_status(type="vcr", ...)` dispatch
    adapters in `general/tools/update.py`/`set_status.py`.
  - `vcr/resources/` (`specmgr://vcr/schema`, `specmgr://vcr/example`,
    `specmgr://vcr/template` -- no `specmgr://vcr/{id}`, no
    `specmgr://vcr/list`) and `vcr/prompts/` (`create_vcr`/`update_vcr`
    narrated instruction flows; `create_vcr` first checks `list_vcr` for a
    near-duplicate verification case record).
  - A cross-cutting `specmgr://dtais` resource (`general/resources/dtais.py`
    + `general/data/general_dtais.md`), explaining the DTAIS
    verification-method vocabulary (Demonstration, Test, Analysis,
    Inspection, Special) that VCR's `## Acceptance Criteria` depends on --
    kept in `general/` rather than `vcr/`, since it is domain-knowledge
    other document types may also want to reference, mirroring RSK's
    `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` resources.
  - `server.py` updated to import the new `vcr` domain package;
    `.pre-commit-config.yaml`, `AGENTS.md`, and root `README.md` all
    updated for the twelfth domain. `specmgr schema --type vcr` generates
    `docs/vcr_schema.json` and the packaged copy.
  - Comprehensive test coverage across `tests/vcr/models/`,
    `tests/vcr/tools/`, `tests/vcr/resources/`, `tests/vcr/prompts/`, and
    `tests/general/resources/test_dtais.py`.

## [0.14.0] - 2026-08-30

### Added

- **Eleventh domain feature (FEAT/Feature tooling)**: formalized the ad hoc
  `.specmgr/feat/<id>/README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e)
  into a real, schema-backed `feat` document-type domain, with full MCP tool surface,
  resources, prompts, and cross-cutting registration. Deliberately special among domains:
  uses non-UUID `feat-NNN-slug` ids (chosen by user, derived from H1 title) and
  folder-per-document addressing (`.specmgr/feat/<id>/README.md`), deviating from ADR
  8cf940c5's flat-file UUID precedent. Mirrors GOL/RSK/DEC's simple surface (no
  fine-grained mutation tools, no renderer — writes persist raw validated body
  byte-for-byte) and uses the post-feat-22 generic `update`/`set_status` dispatch
  from day one:
  - `feat/models/v1/`: Pydantic schema (`FeatFrontmatter` with a closed 4-value
    status set `planning`/`progress`/`review`/`done`, `Feature` body with mandatory
    `## Plan`/`## Progress` composites containing structured `### Requirements`
    (regex-validated list), `### Acceptance Criteria` (checked list), `### Scope`
    (mandatory `#### Included`/`#### Explicitly Out Of Scope`), optional `### Dependencies`
    (`#### Depends On`/`#### Blocks`), `### Task List` (`#### Phase N` entries each with
    `- [ ] ...` checklist), `### Updates`/`### Decisions Made` (ISO8601-enforced
    `#### {timestamp} — {title}` entries, newest-first ordered), and optional leaves),
    parser (`parse_feat`), `FeatSummary` (adds `path: str` field — the only document
    type where direct hand/agent markdown editing remains the sanctioned workflow),
    and JSON schema generation, inside the domain package itself.
  - `feat/tools/`: `@mcp.tool()` wrappers for the FEAT lifecycle (`create_feat`,
    `parse_feat`, `list_feat`, `get_feat`, `get_feat_example`, `get_feat_template`,
    `validate_feat`), plus a stub for `delete_feat`. Bespoke `_paths.py` (hand-rolled
    like ADR's own, not the shared flat-file pattern): `feat_base_dir()`/
    `find_feat_path_by_id()` (no-scan shortcut + folder-name-mismatch rejection at
    tool layer), global `feat_create_lock()` (since id doesn't exist until scanning
    completes). `list_feat` ships as a paged tool from day one.
  - Generic `update(type="feat", ...)`/`set_status(type="feat", ...)` dispatch
    adapters in `general/tools/update.py`/`set_status.py`, using `feat.tools._paths`
    bespoke addressing (only remaining divergence from other domains).
  - `feat/resources/`: `specmgr://feat/schema`, `specmgr://feat/example`,
    `specmgr://feat/template` (no `specmgr://feat/{id}` — id-based reads are
    `get_feat`-only; no `specmgr://feat/list` — listing is the `list_feat` tool).
  - `feat/prompts/`: `create_feat(topic)`/`update_feat(id, instructions?)`
    prompts reading packaged instruction data, following the post-feat-22 generic
    dispatch pattern.
  - `server.py` updated to import the new `feat` domain package; `pyproject.toml`,
    `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `AGENTS.md`, and root
    `README.md` all updated for the eleventh domain. `specmgr schema --type feat`
    generates `docs/feat_schema.json` and the packaged copy.
  - Comprehensive test coverage across `tests/feat/models/`, `tests/feat/tools/`,
    `tests/feat/resources/`, and `tests/feat/prompts/` (221 new tests total,
    including live lifecycle and concurrent-create collision tests).
  - **Phase 6 follow-up (part of v0.14.0)**: reversed an earlier deliberate
    divergence — `feat` frontmatter's `created`/`updated` fields now use the same
    microsecond ISO timestamp format (`datetime.now().isoformat(timespec="microseconds")`)
    as every other whole-body domain, for cross-domain consistency. The 17 pre-existing
    hand-authored feature files remain untouched and out of scope — this only affects
    documents created/updated via the `feat` MCP tools going forward.

## [0.13.0] - 2026-08-27

### Removed

- **BREAKING**: the 16 per-domain mutation MCP tools are deleted outright
  (no deprecated wrappers): `update_req`, `update_uc`, `update_tsk`,
  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `update_dec`,
  `set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`,
  `set_status_prb`, `set_status_gol`, `set_status_rsk`, `set_status_dec`
  (the two `dec` tools were shipped in v0.12.0). Whole-body and line-range
  updates now go through the generic `update` tool and status changes
  through the generic `set_status` tool in `general/tools/` (see "Added"
  below).
- **BREAKING**: ADR's own `set_status` tool is removed; the surviving
  `set_status` tool is the generic one, whose signature changes from
  `(id, status, superseded_by)` to `(id, type, status, superseded_by)` —
  `type="adr"` is now required (and the tool is accepted for all nine
  domains).

### Added

- Generic `update(id, type, content, begin=None, end=None)` MCP tool in
  `general/tools/`: whole-body and line-range replace of an existing
  document across the eight whole-body domains (`type` is one of
  `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`). With no `begin`/`end`,
  `content` is the full replacement body; with both, it replaces the
  1-based, inclusive body-line range `begin`..`end` of the current on-disk
  body (`N+1` = end-of-body sentinel: append after the last line, or
  replace through end of body). The spliced result is validated as a whole
  document before anything is written; unchanged regions stay
  byte-identical.
- Generic `set_status(id, type, status, superseded_by=None)` MCP tool in
  `general/tools/`: the status change for all nine domains (`type` is one
  of `req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`adr`), enforcing each
  domain's closed status vocabulary. `superseded_by` is accepted only for
  `type="adr"` (composing the status as `"superseded by {superseded_by}"`)
  and raises `ValueError` with any other `type`.
- Optional `raw: bool = False` parameter on the eight `get_<d>` tools
  (`get_req`, `get_uc`, `get_tsk`, `get_qa`, `get_prb`, `get_gol`,
  `get_rsk`, `get_dec`): `raw=True` returns the frontmatter-stripped body
  text verbatim — the text `update`'s `begin`/`end` index into;
  `raw=False` (the default) behaves exactly as before.
- The consolidation above is recorded in ADR
  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
  status-change tools into generic type-dispatched tools"), whose
  convention for new domains (one dispatch entry per generic tool plus a
  `raw` getter parameter) was applied to the DEC domain when it was
  integrated from dev.

## [0.12.0] - 2026-08-27

### Added

- **Tenth domain feature (DEC/Decision tooling)**: implemented tooling for
  decisions in general (not architecture-only), keeping the ADR's general
  structure (MADR-style headings, an `Options` collection) but built on the
  generic `models/md` engine with the simple surface used by GOL/RSK/QA —
  no fine-grained ADR mutation tools, no `specmgr://dec/{id}` resource, no
  renderer (writes persist the caller's raw validated body byte-for-byte):
  - `dec/models/v1/`: Pydantic schema (`DecFrontmatter` with a closed
    6-value status set `draft`/`proposed`/`accepted`/`rejected`/
    `deprecated`/`superseded`, `Decision` body with `## Context and Problem
    Statement`/`## Decision Outcome` mandatory, optional `## Decision
    Drivers`/`## Considered Options`/`## Related Artifacts`/`## Pros and
    Cons`/`## More Information`/`## Updates`, `### Consequences`/
    `### Confirmation` under Decision Outcome, and `### Option N: {name}`
    entries with computed `number`/`name` fields and a duplicate-number
    guard), parser (`parse_dec`), `DecSummary`, and JSON schema generation,
    inside the domain package itself (not top-level `models/`).
  - `dec/tools/`: `@mcp.tool()` wrappers for the DEC lifecycle
    (`create_dec`, `update_dec`, `set_status_dec`, `parse_dec`, `list_dec`,
    `get_dec`, `get_dec_example`, `get_dec_template`, `validate_dec`),
    plus a stub for `delete_dec`. `list_dec` ships as a paged tool from day
    one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `dec/resources/`: `specmgr://dec/schema`, `specmgr://dec/example`,
    `specmgr://dec/template` (no `specmgr://dec/{id}` — id-based reads are
    `get_dec`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
    `specmgr://dec/list` — listing is the `list_dec` tool, ADR
    ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `dec/prompts/`: `create_dec(topic)`/`update_dec(id, instructions?)`
    prompts reading packaged instruction data.
  - `server.py` updated to import the new `dec` domain package; `AGENTS.md`
    updated for ten domain/cross-cutting packages; root `README.md`
    updated with the new `Decision (DEC)` artifact type.
  - Comprehensive test coverage across `tests/dec/models/`,
    `tests/dec/tools/`, `tests/dec/resources/`, and `tests/dec/prompts/`,
    including a live lifecycle integration test.

## [0.11.0] - 2026-08-26

### Added

- **Eighth domain feature (GOL/Goal tooling)**: implemented high-level
  business-goal document tools and infrastructure (the strategic
  "what the organization wants to achieve" level that sits above
  individual requirements):
  - `gol/models/v1/`: Pydantic schema (`GolFrontmatter` with REQ's exact
    7-value status set, `Goal` body mirroring `Requirement` with exactly
    two deliberate omissions — no `## Characteristics`, no `## Level`, so
    the only mandatory body fields are statement + Source, plus optional
    Description/Priority/Tags/Related Artifacts/More Information/Notes),
    parser (`parse_gol`), `GolSummary`, and JSON schema generation, inside
    the domain package itself (not top-level `models/`).
  - `gol/tools/`: `@mcp.tool()` wrappers for the GOL lifecycle
    (`create_gol`, `update_gol`, `set_status_gol`, `parse_gol`, `list_gol`,
    `get_gol`, `get_gol_example`, `get_gol_template`, `validate_gol`),
    plus a stub for `delete_gol`. `list_gol` ships as a paged tool from day
    one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `gol/resources/`: `specmgr://gol/schema`, `specmgr://gol/example`,
    `specmgr://gol/template` (no `specmgr://gol/{id}` — id-based reads are
    `get_gol`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
    `specmgr://gol/list` — listing is the `list_gol` tool, ADR
    ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `gol/prompts/`: narrated `create_gol`/`update_gol` prompts driving a
    `TodoWrite` + `question`-tool interview flow; `create_gol` first checks
    `list_gol` for a near-duplicate goal.
  - `server.py` updated to import the new `gol` domain package; `AGENTS.md`
    updated for eight domain/cross-cutting packages.
  - Comprehensive test coverage across `tests/gol/models/`,
    `tests/gol/tools/`, `tests/gol/resources/`, and `tests/gol/prompts/`,
    including a live lifecycle integration test.

- **Ninth domain feature (RSK/Risk tooling)**: implemented risk-register
  entry document tools and infrastructure (the scenario decomposed into
  `## Cause`/`## Trigger`/`## Consequence`, a 5x5 probability/impact
  assessment before mitigation (`## Initial Assessment`) and the same 5x5
  after mitigation (`## Residual Assessment`) with the value in the H3
  heading itself, and a TARA response strategy `## Strategy` — closed
  4-value set `transfer`/`accept`/`reduce`/`avoid`):
  - `rsk/models/v1/`: Pydantic schema (`RskFrontmatter` with 6-value status
    set `open`/`mitigating`/`accepted`/`occurred`/`closed`/`dropped`,
    `Risk` body with computed probability/impact values and a derived risk
    `level` always computed from the 5x5 product), parser (`parse_rsk`),
    `RskSummary`, and JSON schema generation, inside the domain package
    itself (not top-level `models/`).
  - `rsk/tools/`: `@mcp.tool()` wrappers for the RSK lifecycle
    (`create_rsk`, `update_rsk`, `set_status_rsk`, `parse_rsk`, `list_rsk`,
    `get_rsk`, `get_rsk_example`, `get_rsk_template`, `validate_rsk`),
    plus a stub for `delete_rsk`. `list_rsk` ships as a paged tool from day
    one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13), and its `RskSummary`
    lines carry the residual-risk coordinates so a register-wide
    risk-matrix view can be built from the listing alone.
  - `rsk/resources/`: `specmgr://rsk/schema`, `specmgr://rsk/example`,
    `specmgr://rsk/template`, plus two static domain-knowledge resources
    `specmgr://rsk/tara` (what TARA is and when/how to apply each of the
    four words) and `specmgr://rsk/risk-matrix` (the 5x5 scale anchors,
    zone table, and product thresholds) (no `specmgr://rsk/{id}` —
    id-based reads are `get_rsk`-only, ADR
    ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://rsk/list` — listing
    is the `list_rsk` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
  - `rsk/prompts/`: `create_risk`/`update_risk` prompts (the issue's
    literal wording, not the `rsk`-prefixed convention the tools/resources
    use) driving a narrated `TodoWrite` + `question`-tool interview flow.
  - `server.py` updated to import the new `rsk` domain package; `AGENTS.md`
    updated for nine domain/cross-cutting packages.
  - Comprehensive test coverage across `tests/rsk/models/`,
    `tests/rsk/tools/`, `tests/rsk/resources/`, and `tests/rsk/prompts/`,
    including guards that keep the packaged TARA/risk-matrix domain
    knowledge consistent with the model's derived-level zone mapping.

## [0.10.0] - 2026-08-25

### Added

- **Seventh domain feature (PRB/Problem Statement tooling)**: implemented
  Six-Sigma-style problem-statement document tools and infrastructure:
  - `prb/models/v1/`: Pydantic schema (`PrbFrontmatter`, `PrbBody`,
    `PrbDocument`), parser (`parse_prb`), `PrbSummary`, and JSON schema
    generation, inside the domain package itself (not top-level `models/`).
  - `prb/tools/`: `@mcp.tool()` wrappers for the PRB lifecycle
    (`create_prb`, `update_prb`, `set_status_prb`, `parse_prb`, `list_prb`,
    `get_prb`, `get_prb_example`, `get_prb_template`, `validate_prb`),
    plus a stub for `delete_prb`.
  - `prb/resources/`: `specmgr://prb/schema`, `specmgr://prb/example`,
    `specmgr://prb/template` (no `specmgr://prb/{id}` or
    `specmgr://prb/list`, consistent with REQ/UC/TSK/QA).
  - `prb/prompts/`: narrated `create_prb`/`update_prb` prompts driving a
    `TodoWrite` + `question`-tool 5W2H interview flow.
  - `server.py` updated to import the new `prb` domain package; `AGENTS.md`
    updated for seven domain/cross-cutting packages; README.md documents
    the new Problem Statement (PRB) artifact type.
  - Comprehensive test coverage across `tests/prb/models/`, `tests/prb/tools/`,
    `tests/prb/resources/`, and `tests/prb/prompts/`, including a live
    lifecycle integration test.

## [0.9.0] - 2026-08-23

### Changed

- **BREAKING**: QA (Question and Answer) documents now use a new v2 body
  schema (`qa/models/v2/`); every QA MCP tool/resource/prompt (`create_qa`,
  `update_qa`, `set_status_qa`, `parse_qa`, `list_qa`, `get_qa`,
  `get_qa_example`, `get_qa_template`, `delete_qa` stub, `validate_qa`,
  `specmgr://qa/schema`/`/example`/`/template`, `create_qa`/`update_qa`/
  `refine` prompts) is repointed at it. v2 replaces v1's one
  `### {heading}` H3 sub-section per question/answer pair with many
  adjacent, un-headed pairs (`<!-- optional comment -->` + `> {question}`
  block quote + free-form answer prose) directly inside a category
  section, and adds a new `## Elicitation Context` section (a 10th
  `_QaCategory`-shaped section, not one of the 9 ISO/IEC 25010:2023
  characteristics) between `## General` and `## Functional Suitability`.
  This is a hard cutover with no version gate and no dual v1/v2 read
  support: a document shaped for the former v1 schema fails v2 parsing
  with a structural `AssertionError`/`pydantic.ValidationError`, not a
  migration-specific error. `qa/models/v1/` has since been removed from
  disk entirely (`QaFrontmatter`/`QaSummary` moved into `qa/models/v2/`);
  QA is once again a single-schema (v2-only) domain.

## [0.8.0] - 2026-08-19

### Changed

- **BREAKING**: Removed the five `specmgr://<domain>/list` MCP resources
  (`adr`, `req`, `uc`, `tsk`, `qa`); replaced by paged `list_<domain>`
  `@mcp.tool()`s (`list_adr`, `list_req`, `list_uc`, `list_tsk`, `list_qa`)
  accepting `max_results`/`offset` and returning a shared `PagedResult`
  wrapper (`total`, `offset`, `max_results`, `truncated`, `results`).
  Resources cannot accept parameters, so pagination required the
  resource→tool conversion (see ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13). Callers must switch from
  `resources/read --uri specmgr://<domain>/list` to `tools/call
  --tool-name list_<domain>`.

### Added

- Shared `general/models/PagedResult[T]` and `general/tools/_paging`
  (`normalize_paging`/`paginate`) infrastructure, and a shared
  `general/models/DocSummary` base for four of the five domains' summary
  models (`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary`); `AdrSummary`
  stays a deliberate, documented outlier (field-identical, not a
  subclass, since `models/adr` must stay free of the `mcp` extra).

## [0.7.0] - 2026-08-18

### Added

- **`compact_history` MCP prompt** (`general/prompts/`): New prompt for compacting
  verbose history entries, with packaged instruction data file
  (`general/data/general_compact_history_instructions.md`) and full test coverage
  (12 tests). Establishes prompts support under the `general/` domain package.
- **External prompt instruction files**: Migrated inline instruction strings from
  Python code to external markdown files in `*/data/` directories across all
  domains (adr, qa, req, tsk). Enables easier maintenance and better separation
  of concerns.
- **`refine` prompt for QA module**: New prompt to elicit additional Q&A pairs
  by quality category.

### Changed

- Prompt instruction text storage: replaced inline `str.format()` calls with
  external markdown data files and `string.Template` for placeholder substitution,
  allowing unescaped braces in markdown content. Instructions are read fresh on
  every call (no caching) via the `read_packaged_text()` helper.

## [0.6.0] - 2026-08-18

### Added

- **Fifth domain feature (QA/Q&A tooling)**: implemented question-and-answer document
  tools and infrastructure:
  - `qa/models/v1/`: Pydantic schema (`QaFrontmatter`, `QaBody`, `QaItem`, `QaDocument`),
    parser (`parse_qa`), renderer (`render_qa`), re-exported via `qa/models/__init__.py`
    and `models/__init__.py`.
  - `qa/tools/`: `@mcp.tool()` wrappers for Q&A lifecycle (`create_qa`, `update_qa`,
    `parse_qa`, `set_status_qa`), plus stub for `delete_qa`.
  - `qa/resources/`: MCP resources for Q&A read operations (`specmgr://qa/list`,
    `specmgr://qa/{id}`).
  - `qa/prompts/`: `create_qa` and `update_qa` prompts for Q&A drafting and revision
    workflows.
  - Comprehensive test coverage with 80+ passing tests across `tests/models/qa/`,
    `tests/qa/tools/`, `tests/qa/resources/`, and `tests/qa/prompts/`.
- **Markdown infrastructure improvements**: generalized `@markdown` decorator with
  enhanced merge semantics and `end_marker` support for more flexible section
  composition across document types.

### Changed

- MCP server registration in `server.py` updated to import all six domains
  (`adr`, `general`, `qa`, `req`, `tsk`, `uc`) to register their respective
  tools, resources, and prompts.

## [0.5.1] - 2026-08-18

### Fixed

- **`md` models**: `MarkdownListItem.get_extent()` now correctly handles
  continuation paragraphs in loose numbered lists (e.g., "1. Safety\n\n  Details...").
  Previously, mdformat rendered numbered lists differently from bullet lists,
  causing `get_extent()` to only capture the first paragraph and leave
  continuation paragraphs unparsed. The model's `Characteristics.Items` also
  changed from `MarkdownListItemWithNotes` back to plain `MarkdownListItem`
  per domain decision.

## [0.5.0] - 2026-08-16

### Added

- **`specmgr webfetch` MCP tool**: bearer-token-authenticated HTTP GET utility
  for fetching URL content with configurable base-URL filtering (case-insensitive
  matching via `SPECMGR_WEBFETCH_BASE_URL` and `SPECMGR_WEBFETCH_BEARER` environment
  variables). Includes custom exceptions (`WebfetchNotConfiguredError`,
  `WebfetchUrlNotAllowedError`) and comprehensive test coverage (45+ tests).
  Documented in README.md; registered in `general/tools/` with full API
  documentation auto-generated.

### Changed

- Error messages for not-found exceptions (`AdrNotFoundError`, `ReqNotFoundError`,
  `UcNotFoundError`, `TskNotFoundError`, `DocNotFoundError`) standardized across
  all domains for consistent UX when a document cannot be located. Updated all
  related tool modules (`adr/tools/_paths.py`, `req/tools/_paths.py`, etc.) and
  extended test coverage in each domain's `test_paths.py` and `test_get_<type>.py`
  to assert on message content.

## [0.4.0] - 2026-08-16

### Added

- **Third domain feature (TSK/TaskList tooling)**: implemented task-list document
  tools and infrastructure:
  - `models/tsk/v1/`: Pydantic schema (`TskFrontmatter`, `TskBody`, `TaskListItem`,
    `TskDocument`), parser (`parse_tsk`), renderer (`render_tsk`), re-exported via
    `models/tsk/__init__.py` and `models/__init__.py`.
  - `tsk/tools/`: `@mcp.tool()` wrappers for task-list lifecycle (`create_tsk`,
    `update_tsk`, `parse_tsk`, `set_status_tsk`), plus stub for `delete_tsk`.
  - `tsk/resources/`: MCP resources for task-list read operations (`specmgr://tsk/list`,
    `specmgr://tsk/{id}`).
  - `tsk/prompts/`: `create_tsk` and `update_tsk` prompts for task-list drafting
    and revision workflows.
  - Comprehensive test coverage with 70+ passing tests under `tests/models/tsk/`,
    `tests/tsk/tools/`, `tests/tsk/resources/`, `tests/tsk/prompts/`.
- **Fourth domain feature (UC/UseCase tooling)**: implemented use-case document
  tools and infrastructure:
  - `models/uc/v1/`: Pydantic schema (`UcFrontmatter`, `UcBody`, `UseCase`),
    parser (`parse_uc`), renderer (`render_uc`), re-exported via `models/uc/__init__.py`
    and `models/__init__.py`.
  - `uc/tools/`: `@mcp.tool()` wrappers for use-case lifecycle (`create_uc`,
    `update_uc`, `parse_uc`, `set_status_uc`), plus stub for `delete_uc`.
  - `uc/resources/`: MCP resources for use-case read operations (`specmgr://uc/list`,
    `specmgr://uc/{id}`).
  - `uc/prompts/`: `create_uc` and `update_uc` prompts for use-case drafting
    and revision workflows.
  - Comprehensive test coverage with 75+ passing tests under `tests/models/uc/`,
    `tests/uc/tools/`, `tests/uc/resources/`, `tests/uc/prompts/`.
- **ISO/IEC 25010:2023 quality model resource** (`iso25010`): a cross-cutting
  shared resource providing the ISO/IEC 25010:2023 software product quality
  characteristics and sub-characteristics, accessible via `specmgr://iso25010/model`.

### Changed

- Moved the top-level `resources/` package (the `specmgr://version` MCP
  resource) into `general/resources/`, since it is itself a cross-cutting,
  not domain-specific, concern — consistent with `general/tools/`. Updated
  `server.py`'s registration import accordingly (`general` now pulls in its
  own `resources`/`tools` sub-packages).

### Fixed

- Task-list (TSK) examples and error messages clarified for better UX.

## [0.3.1] - 2026-08-15

### Added

- **`general/tools/_packaged_data.py`**: Generic, doc-type-agnostic utility
  module providing `packaged_data_path()` and `read_packaged_text()` functions
  for accessing packaged data files (example/template/schema documents) across
  all artifact types. Eliminates per-doc-type boilerplate and reduces
  duplication.

### Changed

- REQ's packaged data files (example, template, schema) relocated from
  `req/resources/data/` to `req/data/` for consistency with future artifact
  types.
- REQ tools updated to use `general.tools._packaged_data` instead of the
  retired `req._data` module, centralizing packaged-data access.
- `pyproject.toml` package-data key updated to reflect new `req/data/` path.
- Pre-commit hook and CI step updated to reference new packaged-data location.

### Removed

- `req/_data.py`: REQ-specific packaged-data module superseded by
  `general/tools/_packaged_data.py`.

## [0.3.0] - 2026-08-15

### Added

- **`specmgr coverage-badge`**: a CLI command that reads the `.coverage`
  data file (generated by `coverage run`), extracts the total test coverage
  percentage, and renders a flat-style SVG badge with color based on
  coverage threshold (≥90% green, ≥75% yellowgreen, ≥50% yellow, else red).
  Badge written to `docs/coverage.svg` by default, with `--output`/`-o` to
  override. Wired into CI and pre-commit to enforce badge freshness on every
  change to source/test files. Coverage measurement now runs by default as
  part of the existing test suite (no separate test run); the badge itself
  is only regenerated/verified on Python 3.13 to match `docs`/`adr-toc`
  behavior.
- `vulture` dead-code detector: added to the `test` extra, wired into a new
  local `vulture` pre-commit hook (`uv run --frozen vulture src/
  whitelist.py --min-confidence 60`) and into CI's lint step across the
  full 3.11/3.12/3.13 matrix. Known framework false positives (Pydantic
  `@field_validator`/`@model_validator` methods and `model_config`, and MCP
  `@mcp.resource()`/`@mcp.tool()` entry points) are suppressed via a new
  root-level `whitelist.py`, grouped and commented by the reason each is a
  false positive rather than real dead code.
- **`specmgr unused-code`**: a CLI command wrapping `vulture`. By default,
  reports every unreferenced symbol in `--src` (plus `--whitelist`, if it
  exists) -- the same check the pre-commit hook/CI step enforce, without
  having to remember the raw `vulture` invocation. With `--test`/`-t`,
  instead reports symbols `vulture` only considers "used" because the
  test suite references them, never production code itself: compares a
  scan of `--src` alone against a scan of `--src` together with `--tests`,
  and reports the symbol names that disappear from the findings once
  tests are included -- a lead worth a manual look, since it may indicate
  an orphaned public surface. Supports `--min-confidence` and an opt-in
  `--strict` flag (exit 1 if any findings are reported, for future CI
  wiring). Requires the `test` extra, since `vulture` is only declared
  there.
- **`specmgr adr-toc`**: a CLI command that generates a table of contents
  (`docs/adr/README.md`) listing all ADRs with their titles, frontmatter
  (id, status, date, decision-makers, consulted, informed), and links to
  the actual ADR files. Scans the configurable ADR base directory (default
  `docs/adr`, via `SPECMGR_ADR_DIR` environment variable). Supports
  `--output`/`-o` to write to an alternate location. Run after adding new
  ADRs and commit the result.
- **`specmgr docs`**: a single CLI command that writes `api/*.md`
  (per-module Markdown API reference, plus a `README.md` index) and
  `GENERATED.md` (implemented-domain list, per-module docstrings, and a
  static test-file count) under an `--output`/`-o` base directory,
  defaulting to the repo's `docs/` (committed, so it browses directly on
  GitHub). Replaces the previous `generate-docs`, `markdown-docs`, and
  `pydoc` commands (see "Removed" below). The `api/README.md` index now
  includes the first-line docstring for each module, improving discoverability.
- `pre-commit` adoption: `.pre-commit-config.yaml` runs `ruff format`/`ruff
  check`, the full `unittest` suite (scoped to `src/**/*.py`/`tests/**/*.py`
  changes), and a local `specmgr docs` hook (scoped to `src/**/*.py`
  changes) before every commit; `pre-commit` added to the `dev` extras.
  One-time setup: `uv run --frozen pre-commit install`.
- CI backstop: `.github/workflows/ci.yml` now regenerates `docs/` and
  fails the build on drift, catching anyone who bypassed or never
  installed the pre-commit hook. The `specmgr docs` drift check is pinned
  to Python 3.13 (the project's default dev version) since Python's
  `inspect` module formats docstrings differently across versions, causing
  false drift reports on Python 3.12 (see AGENTS.md for details).
- `docs/api/` committed-to-repo policy: the Markdown API reference is
  version-controlled, not generated on demand, so it renders on GitHub
  without a build step.
- **Developer experience**: documented Python version handling in AGENTS.md.
  When using a non-default Python version (e.g., 3.12 instead of 3.13),
  both `uv sync` and `uv run` require `--python X.Y` and `--all-extras` flags
  to ensure CLI/MCP dependencies are installed correctly.
- **Second domain feature (REQ tooling)**: implemented requirement/specification
  document tools and infrastructure:
  - `models/req/v1/`: Pydantic schema (`ReqFrontmatter`, `ReqBody`, `Requirement`),
    parser (`parse_req`), renderer (`render_req`), re-exported via `models/req/__init__.py`
    and `models/__init__.py`.
  - `req/tools/`: 5 `@mcp.tool()` wrappers for requirement lifecycle (`create_req`,
    `update_req`, `delete_req` stub, `set_status_req`, `parse_req`).
  - `req/resources/`: MCP resources for requirement read operations (`specmgr://req/list`,
    `specmgr://req/{id}`).
  - `req/prompts/`: `create_req` and `update_req` prompts for requirement drafting
    and revision workflows.
  - Comprehensive test coverage with 120+ passing tests under `tests/models/req/`,
    `tests/req/tools/`, `tests/req/resources/`, `tests/req/prompts/`.
- **Markdown infrastructure improvements**:
  - `models/md/`: New markdown section models (`MarkdownSection1`, `MarkdownSection2`,
    ..., `MarkdownSection6`) and optional comment mixins
    (`MarkdownSection1WithComment`, etc.) for modular document building.
  - `MarkdownComment` model for structured comment blocks within document sections.
  - Full test coverage for markdown models (25+ tests).
- **Shared cross-domain utilities**:
  - `general/tools/`: Expanded with `mdformat` tool (format markdown in place,
    preserving YAML frontmatter).
  - `general/lookup/`: New shared document path and id lookup module for consistent
    id→file-path resolution across all document types (adr, req, uc, etc.).

### Removed

- The `generate-docs`, `markdown-docs`, and `pydoc` CLI commands (and
  `docs/pydoc/` HTML output) — superseded by `specmgr docs` above. HTML
  pydoc output didn't render usefully in GitHub's file browser and
  duplicated the Markdown output.
- 6 fabricated ADRs and a stray duplicate file that had been written into
  `docs/adr/`/`doc/` by mistake.

### Fixed

- `AGENTS.md`'s auto-generated internals replaced with a short, permanent,
  hand-written pointer to `docs/GENERATED.md` — eliminates the fragile
  regex-splice logic that had produced a duplicate section.
- Corrected a stale "no `publish.yml` yet" note in `AGENTS.md`'s "CI /
  Release" section; `publish.yml` exists and has shipped `v0.1.0`,
  `v0.2.0`, `v0.2.1`.

### Changed

- **Breaking (internal-API only):** repackaged the ADR domain's interface
  layer to be domain-first (`doc/refactor-domain.md`): `tools/adr/`,
  `prompts/adr/`, and `resources/adr_get.py`/`adr_list.py` all moved under a
  new top-level `adr/` package, becoming `adr/tools/`, `adr/prompts/`, and
  `adr/resources/adr_get.py`/`adr_list.py` respectively. The now-empty
  top-level `tools/` and `prompts/` packages were removed entirely.
  `biz.dfch.specmgr.models.adr` is unchanged. No MCP-facing names change:
  tool names (`get_adr`, `create_adr`, ...), resource URIs
  (`specmgr://adr/{id}`, `specmgr://adr/list`), and prompt names
  (`create_adr`, `update_adr`, ...) are all identical -- only the Python
  import paths move. Test modules moved correspondingly:
  `tests/tools/adr/` → `tests/adr/tools/`, `tests/prompts/adr/` →
  `tests/adr/prompts/`, `tests/resources/test_adr.py` →
  `tests/adr/resources/test_adr.py`.

## [0.2.1] - 2026-08-04

### Changed

- `server.json`: corrected the MCP Registry server `name` from
  `io.github.dfch/biz.dfch.specmgr` to `io.github.dfch/biz-dfch-specmgr`,
  matching the `mcp-name` HTML comment convention (package identifier with
  hyphens, not the repo/namespace name with dots).
- `README.md`: updated the MCP Registry badge and registry search links to
  match the corrected `io.github.dfch/biz-dfch-specmgr` server name.

## [0.2.0] - 2026-08-04

### Added

- `prompts/adr/` MCP prompts module with two main workflows and two experimental variants:
  - `create_adr.py`: Prompt-driven workflow for drafting new Architecture Decision Records,
    sequencing tool calls in the correct order (context → decision drivers → options → outcome).
  - `update_adr.py`: Prompt-driven workflow for revising existing ADRs by id, supporting
    frontmatter updates, section edits, and option management.
  - `create_adr_test.py` and `update_adr_test.py`: Experimental step-gated variants with
    explicit gates (`GATE 0`…`GATE N`), exit conditions, and stricter phrasing to test
    compliance under more rigorous constraints (side-by-side A/B comparison, not yet
    recommended for production).
- `tools/adr/_lock.py`: File-locking mechanism for safe concurrent access to ADR files
  during tool operations, preventing race conditions when multiple clients modify the
  same ADR simultaneously.
- Comprehensive test coverage for all new prompts and the lock mechanism with 175 passing
  tests across `tests/prompts/adr/`, `tests/tools/adr/`, `tests/resources/`, and
  `tests/models/adr/`.
- Updated `AGENTS.md` to document the new prompt surface, experimental test variants,
  and finalized ADR tooling status (§11 in `doc/adr-tool-plan.md`).
- Updated `doc/adr-tool-plan.md` (§8 and §11) to finalize prompt design, document
  experimental variants, and mark the implementation as complete.

### Fixed

- `models/adr/v1/parser.py`: rewrote the ADR body parser to build a proper
  heading *outline tree* (`_Node`/`_build_outline`, standard table-of-contents
  nesting rules) instead of a flat H1/H2/H3 token list. Headings nested inside
  a "leaf" section (e.g. `### Postgres` under `## Considered Options`, `####
  Good`/`#### Bad` under `### Consequences`, or any heading under `## More
  Information`) are now correctly preserved as opaque section content instead
  of being misparsed or rejected with a spurious "heading level is not part
  of the ADR schema" error. Added regression tests in
  `tests/models/adr/v1/test_parser.py` covering nested headings under
  Considered Options, Consequences, Confirmation, More Information, and a
  full-document round trip.

## [0.1.0] - 2026-08-03

### Added

- Initial project scaffolding: namespace package layout
  (`src/biz/dfch/specmgr/`), `setuptools` build backend, `cli`/`mcp`/`test`/`dev`
  extras, placeholder CLI (`specmgr version`) and MCP server skeleton, CI
  workflow (`.github/workflows/ci.yml`), and governance documents
  (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `NOTICE`).
- `specmgr mcp` CLI command to start the MCP server, with `--transport`/
  `--host`/`--port` options (and matching `SPECMGR_MCP_TRANSPORT`/
  `SPECMGR_MCP_HOST`/`SPECMGR_MCP_PORT` env vars), mirroring
  `biz-dfch-asdste100mcp`'s dual-transport entry point.
- `specmgr://version` MCP resource returning the installed
  `biz-dfch-specmgr` package version, plus the backing `VersionInfo` model.
- ADR (Architecture Decision Record) schema, version 1, under
  `src/biz/dfch/specmgr/models/adr/v1/` (see `doc/adr-tool-plan.md` for the
  full design): Pydantic models `AdrFrontmatter`, `AdrBody`, `AdrOption`,
  and `Adr`, covering the MADR 4.0.0-derived frontmatter block and body
  sections, including the dynamic `### Option N: {title}` collection
  backing the derived `## Pros and Cons of the Options` section.
- `parse_adr`/`AdrParseError` (`models/adr/v1/parser.py`): parses an
  on-disk ADR `.md` file's frontmatter and body into an `Adr`, using
  `python-frontmatter` for the YAML block and a `markdown-it-py` token
  walk to map fixed headings onto model fields.
- `render_adr` (`models/adr/v1/renderer.py`): renders an `Adr` back into
  the canonical MADR-derived markdown text, completing the
  parse → validate → render pipeline — always regenerating the full file
  deterministically, omitting optional sections whose field is unset, and
  emitting the derived `## Pros and Cons of the Options` container iff at
  least one option exists.
- `models/adr/v1/mutations.py`: pure, in-memory edit operations on an `Adr`
  (`update_section`, `set_status`, `option_list`, `option_create`,
  `option_read`, `option_update`, `option_delete`), implementing the §4/§5/§8
  update semantics — deletion-sentinel handling (blank or `"REMOVE"`) with
  mandatory-section rejection (`AdrSectionError`), and option lookup-by-title
  with not-found reporting (`AdrOptionNotFoundError`) — ahead of the
  file-I/O-backed MCP tool wrappers.
- Server-assigned `id` field on `AdrFrontmatter` (`models/adr/v1/frontmatter.py`,
  rendered by `renderer.py` immediately before `version`) and the new
  `AdrSummary` model (`models/adr/v1/summary.py`: id/title/status/filename),
  re-exported through `models/adr/__init__.py` and `models/__init__.py`
  (plan §9a).
- `tools/adr/` MCP tool wrappers (plan §8, §9a), each doing a
  re-read/re-parse/mutate/re-render/re-write cycle against the on-disk `.md`
  file (no in-memory cache): `get_adr`, `create_adr`, `update_frontmatter`,
  `update_section`, `set_status`, `option_list`, `option_create`,
  `option_read`, `option_update`, `option_delete`, and `validate_adr`.
  Backed by `tools/adr/_paths.py` (`SPECMGR_ADR_DIR` env var, default
  `docs/adr`; id → file-path resolution via directory scan, `slugify`,
  `AdrNotFoundError`) and `tools/adr/_io.py` (`read_adr`/`write_adr`/
  `load_by_id`).
- `specmgr://adr/list` and `specmgr://adr/{id}` MCP resources
  (`resources/adr_list.py`, `resources/adr_get.py`) — read-only,
  no-tool-round-trip counterparts of the ADR listing/`get_adr` tool,
  matching the existing `specmgr://version` resource convention. A file
  that fails to parse is skipped by `adr_list` rather than failing the
  whole listing.
- `server.json` (repo root): the MCP Registry publisher manifest, modeling
  the `biz-dfch-specmgr` `pypi` package and its `uvx --from
  biz-dfch-specmgr[mcp] python -m biz.dfch.specmgr mcp` invocation (see
  `README.md`'s "Add to OpenCode" section). Not yet publishable to the
  official registry — that requires a first PyPI release (see "Make a
  Release" in `README.md`).
- `.github/workflows/publish.yml`: release automation triggered on `v*`
  tags — builds and publishes the `sdist`/wheel to TestPyPI then PyPI via
  Trusted Publishing (OIDC, no stored token), creates the matching GitHub
  Release with the built artifacts attached, and publishes `server.json`
  to the MCP Registry via `mcp-publisher`/GitHub OIDC.
- `README.md` badges: `mcp-name` HTML comment
  (`io.github.dfch/biz.dfch.specmgr`, matching `server.json`) plus
  TestPyPI/PyPI version, PyPI downloads, and MCP Registry badges.

### Changed

- Moved each CLI command into its own module under
  `src/biz/dfch/specmgr/commands/` (`version.py`, `mcp.py`), registered
  on the Typer `app` in `cli.py` via `app.command()(fn)`, mirroring the
  `commands/` package layout used by sibling projects (e.g.
  `biz-dfch-asdste100vocab`).
- Split `tools/adr/tools.py`'s 11 `@mcp.tool()` wrappers into one module
  per tool (`get_adr.py`, `create_adr.py`, `update_frontmatter.py`,
  `update_section.py`, `set_status.py`, `option_create.py`,
  `option_update.py`, `option_read.py`, `option_delete.py`,
  `option_list.py`, `validate_adr.py`), re-exported unchanged through
  `tools/adr/__init__.py`.
