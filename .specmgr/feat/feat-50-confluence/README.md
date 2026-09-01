---
created: '2026-09-01T17:36:02.251286'
id: feat-50-confluence
status: in-progress
type: feat
updated: '2026-09-01T18:00:00.000000'
version: 1.0.0
---

# Feature: Confluence Fetch and Update Tools

## Plan

### Overview

Adds a `confluence_update` tool that converts a local Markdown file to an HTML fragment and writes it into a Confluence page's body via the REST API using Bearer/PAT authentication, and renames/extends the existing `webfetch` tool to `confluence_fetch` so it can construct the Confluence REST API URL itself from a normal, browsable page URL and download binary/image content. Implements GitHub issue #50.

### Requirements

- REQ-001: `confluence_fetch` (renamed from `webfetch`) must construct a Confluence REST API content URL from a normal browsable page URL, without relying on any external "confluence skill" (none exists in this repository or environment).

- REQ-002: `confluence_fetch` must support both confirmed real-world page URL shapes: Cloud-style `/pages/<id>/<title>` and Server-style `?pageId=<id>`.

- REQ-003: `confluence_fetch` must reject the `/x/<tinyid>` tiny-link URL format with a clear error, since it cannot be resolved to a page id without an authenticated browser session (confirmed against a real instance).

- REQ-004: `confluence_fetch` must detect when a request was redirected off the configured base URL's host (e.g. to an SSO login page) and raise a clear error instead of silently returning/saving that page's content as if it were the requested resource.

- REQ-005: `confluence_fetch` must download binary/non-text content (based on the response `Content-Type`) by writing it to a caller-supplied destination file path and returning that path, while preserving today's behavior of returning text content directly for text/JSON/XML responses.

- REQ-006: `confluence_fetch`'s two environment variables must be renamed from `SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER` to `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`.

- REQ-007: `confluence_update` must reuse the same two environment variables as `confluence_fetch` (no new configuration surface).

- REQ-008: `confluence_update` must resolve the target page's current version number and title via the REST API, render the given Markdown file to an HTML fragment (no `<html>`/`<head>`/`<body>` wrapper), and `PUT` the incremented version with the new body in Confluence "storage" representation.

- REQ-009: `confluence_update` must upload local images referenced by the source Markdown file as Confluence attachments and rewrite the corresponding `<img>` tags into Confluence's `<ac:image>`/`<ri:attachment>` storage-format macro, on a best-effort basis.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001/REQ-002 — given a URL containing `/pages/<id>/` or `?pageId=<id>`, `confluence_fetch` fetches `{base}/rest/api/content/{id}?expand=body.storage` instead of the given URL.

- [ ] ACC-002: Verifies REQ-003 — given a `/x/<tinyid>` URL, `confluence_fetch`/`confluence_update` raise a clear, dedicated error rather than attempting the request.

- [ ] ACC-003: Verifies REQ-004 — given a mocked response whose final URL (after following redirects) has a different host than the configured base URL, `confluence_fetch` raises a clear error instead of returning the redirected content.

- [ ] ACC-004: Verifies REQ-005 — given a mocked non-text `Content-Type` response and a `destination_path`, `confluence_fetch` writes the response bytes to that path and returns the path; given no `destination_path`, it raises a clear error.

- [ ] ACC-005: Verifies REQ-006 — `SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER` no longer exist anywhere in `src/`; `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` are used instead, documented in `README.md`.

- [ ] ACC-006: Verifies REQ-008 — given a mocked GET returning `version.number: N` and a Markdown file, `confluence_update`'s `PUT` payload has `version.number == N + 1`, unchanged `title`, and `body.storage.value` equal to the Markdown rendered via `markdown-it-py` (no head/body wrapper).

- [ ] ACC-007: Verifies REQ-009 — given a Markdown file referencing a local image that exists on disk, `confluence_update` issues a `POST` to the page's `child/attachment` endpoint for that image and the rendered HTML fragment's corresponding `<img>` tag is rewritten to `<ac:image><ri:attachment ri:filename="..." /></ac:image>`.

- [ ] ACC-008: A real, reversible smoke test against the dedicated Confluence test page (id `1232503612`, "fetch and update") succeeds for both `confluence_fetch` (REST content GET) and `confluence_update` (version-incrementing PUT), performed once outside any read-only exploration constraint.

### Scope

#### Included

- Renaming `general/tools/webfetch.py` to `general/tools/confluence_fetch.py` (tool, exceptions, environment variables, tests, docs).

- A new shared, `mcp`-free helper `general/tools/_confluence_url.py` for page-id extraction and REST URL construction.

- A new shared `general/tools/_confluence_config.py` helper for the two environment variables, replacing the config logic duplicated today only in `webfetch.py`.

- `confluence_fetch` binary/image download support (content-type based, write-to-path).

- The new `confluence_update` tool, including basic local-image attachment upload and `<ac:image>` macro rewriting.

- One new ADR (a156fdf9-052c-4f43-93a2-eeec04a91eac) documenting the rename/design decisions.

#### Explicitly Out Of Scope

- Any workaround for the confirmed infrastructure-level limitation where an external oauth2-proxy blocks `/download/attachments/...` binary downloads on at least one real customer instance (hostname withheld) — this is documented as a known environment constraint, not fixed in code.

- Supporting the `/x/<tinyid>` Confluence tiny-link URL format — confirmed unresolvable via PAT alone; explicitly rejected with a clear error instead.

- Rich Confluence storage-format macro conversion beyond plain XHTML tags and the one `<ac:image>` image macro (e.g. code-block macros, panels, galleries, draw.io embeds).

- Any session-cookie-based or browser-emulation authentication workaround for SSO-gated endpoints.

### Dependencies

#### Depends On

- ADR a156fdf9-052c-4f43-93a2-eeec04a91eac: rename/design decisions this feature implements.

#### Blocks

- None known.

### Design Notes

**Real-instance findings (exploration phase, read-only GETs only, against a real Confluence Server/Data Center deployment -- hostname withheld -- using a PAT found in a sibling project's `.env`):**

- `GET {base}/rest/api/content/{id}?expand=version,title,body.storage` works with Bearer/PAT auth and returns the expected JSON shape — confirmed against a real, dedicated test page (id `1232503612`, title "fetch and update", body `<p>This is a page for testing.</p>`).
- All three "normal" browsable URL formats (`/spaces/<key>/pages/<id>/<title>`, `/x/<tinyid>`, `/pages/viewpage.action?pageId=<id>`) redirect to an SSO login page regardless of the Bearer token — confirmed live.
- `/download/attachments/...` (the only URL Confluence exposes for attachment binary content) also redirects to SSO — confirmed twice, with two different real attachments on the same test page (`Meilensteine Detailliertes Vorgehen.png` on an unrelated page, and `apc-log.png` added directly to the dedicated test page, attachment id `1232503616`).
- Response headers distinguish the two cases cleanly: successful `/rest/api/...` calls carry `x-seraph-loginreason: OK`/`JSESSIONID` (reached Confluence's own auth), while blocked calls carry an `_oauth2_proxy_csrf` cookie and a 302 to the SSO login page (intercepted by an external oauth2-proxy before reaching Confluence at all).

**URL conversion algorithm (`_confluence_url.py`):**

- `extract_page_id(url)`: try `[?&]pageId=(\d+)`, then `/pages/(\d+)(?:/|$|\?)`; return `None` for anything else (including `/x/<tinyid>`).
- `build_rest_content_url(base_url, page_id, expand=None)`: `f"{base_url.rstrip('/')}/rest/api/content/{page_id}"` plus an optional `?expand=`.
- `looks_like_rest_or_download_url(url)`: `True` if the URL already contains `/rest/api/` or `/download/`, so it is passed through unchanged.

**SSO-redirect detection (`confluence_fetch`, and reused for `confluence_update`'s internal GET/PUT):** after `httpx` follows redirects, compare the final response URL's host against the configured base URL's host (case-insensitive); a mismatch raises a new `ConfluenceAuthRedirectError` explaining that the endpoint may be gated by an SSO/auth proxy that does not forward Bearer tokens.

**`confluence_update` write flow:** `GET` current `version`/`title` -> render Markdown via `markdown_it.MarkdownIt().render(...)` (already a base dependency; emits a bare fragment, no new dependency needed) -> best-effort local-image attachment upload (`POST .../child/attachment`, falling back to `.../child/attachment/{id}/data` if the filename already exists) with `<img>` -> `<ac:image>` rewriting -> `PUT` with `version.number + 1`.

**No new runtime dependency required** — `httpx` (already in the `mcp` extra) and `markdown-it-py` (already a base dependency) cover the full scope.

### Related Decisions

- a156fdf9-052c-4f43-93a2-eeec04a91eac (ADR): Rename `webfetch` to `confluence_fetch`, add `confluence_update`, and self-construct Confluence REST API URLs instead of relying on a non-existent "confluence skill".

### Task List

#### Phase 1: Rename `webfetch` to `confluence_fetch`

- [x] Task 1.1: Extract `general/tools/_confluence_config.py` (env var constants, `ConfluenceNotConfiguredError`, `_confluence_config()`).

- [x] Task 1.2: Rename `webfetch.py` to `confluence_fetch.py` (tool/function/exception names, env var names), update `general/tools/__init__.py`, `general/__init__.py`, `server.py` docstrings.

- [x] Task 1.3: Rename `test_webfetch.py` to `test_confluence_fetch.py`, updating all references.

- [x] Task 1.4: Update `README.md` environment variables section and `CHANGELOG.md`.

#### Phase 2: URL helper + `confluence_fetch` enhancements

- [ ] Task 2.1: Add `general/tools/_confluence_url.py` (`extract_page_id`, `build_rest_content_url`, `looks_like_rest_or_download_url`) with `tests/general/tools/test__confluence_url.py`.

- [ ] Task 2.2: Wire automatic REST URL construction, tiny-link rejection, and SSO-redirect detection into `confluence_fetch`.

- [ ] Task 2.3: Add binary/image download support (content-type detection, write-to-`destination_path`) to `confluence_fetch`.

- [ ] Task 2.4: Extend `test_confluence_fetch.py` with cases for all of the above.

#### Phase 3: `confluence_update` core (no attachments yet)

- [ ] Task 3.1: Implement `confluence_update` (GET version/title, render Markdown via `markdown-it-py`, PUT with incremented version).

- [ ] Task 3.2: Add `tests/general/tools/test_confluence_update.py` (mocked GET/PUT).

#### Phase 4: Attachment upload + image macro rewrite

- [ ] Task 4.1: Implement local-image discovery, attachment upload (with existing-filename fallback), and `<img>` -> `<ac:image>` rewriting in `confluence_update`.

- [ ] Task 4.2: Extend `test_confluence_update.py` with mocked `POST` attachment upload/fallback cases.

#### Phase 5: Verification and docs

- [ ] Task 5.1: Real, reversible smoke test against the dedicated Confluence test page (id `1232503612`).

- [ ] Task 5.2: `specmgr docs`, `ruff format`/`check`, `vulture`, full `unittest` suite, `CHANGELOG.md` entry.

## Progress

### Current Status

**As of 2026-09-01**: Phase 1 (rename `webfetch` to `confluence_fetch`) complete — the mechanical rename with no new behavior. Next is Phase 2 (URL helper + `confluence_fetch` enhancements: automatic REST URL construction, tiny-link rejection, SSO-redirect detection, binary/image download support).

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 00:00:00.000Z — Phase 1 complete: renamed `webfetch` to `confluence_fetch`

Completed: extracted the shared `general/tools/_confluence_config.py` helper (env var constants `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`, `ConfluenceNotConfiguredError`, `confluence_config()`), moved out of the former `webfetch.py`; renamed `general/tools/webfetch.py` to `general/tools/confluence_fetch.py` (tool `confluence_fetch`, function `confluence_fetch(url) -> str`, `ConfluenceUrlNotAllowedError` staying local to this module since it is fetch-specific), reusing the shared `_confluence_config` helper instead of redefining env vars/exceptions locally; updated `general/tools/__init__.py`, `general/__init__.py`, and `server.py` module docstrings accordingly; renamed `tests/general/tools/test_webfetch.py` to `test_confluence_fetch.py` (class `TestConfluenceFetchTool`, all names/imports renamed, full existing coverage preserved) and added a new `tests/general/tools/test__confluence_config.py` for the extracted helper; updated `README.md`'s Environment Variables section and added a `[Unreleased]` `CHANGELOG.md` entry documenting the breaking rename; regenerated `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` via `specmgr docs`/`specmgr mcp-docs` (and manually removed the now-stale `docs/api/biz.dfch.specmgr.general.tools.webfetch.md`, which those generators do not prune automatically). No behavior changed -- this was a pure, mechanical rename; no URL auto-conversion, binary download, or `confluence_update` yet.
Next: Phase 2 (URL helper + `confluence_fetch` enhancements: `_confluence_url.py`, automatic REST URL construction, tiny-link rejection, SSO-redirect detection, binary/image download support).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2719 tests) passes with zero remaining `webfetch`/`Webfetch`/`WEBFETCH` references anywhere in `src/`/`tests/` (only the pre-existing historical `CHANGELOG.md` entry, `.specmgr/` artifacts, and `docs/adr/` content still mention the old name, as expected).

#### 2026-09-01 00:00:00.000Z — Feature and ADR created; exploration complete

Completed: read GitHub issue #50; discovered no "confluence skill" exists anywhere; explored a real Confluence Server/Data Center instance (hostname withheld; read-only GETs, real PAT from a sibling project's `.env`) and confirmed the URL-conversion algorithm, the SSO-redirect-only-on-non-`/rest/api/`-paths behavior, and that binary attachment download is blocked at the infrastructure layer; wrote ADR a156fdf9-052c-4f43-93a2-eeec04a91eac; created this feature document via `create_feat` and manually corrected its id from the tool-assigned `feat-37-...` to `feat-50-confluence`.
Next: Phase 1 (rename `webfetch` to `confluence_fetch`).
Notes: implementation has not started; this update only covers planning/design/exploration.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 00:00:00.000Z — Named the shared helper function `confluence_config()`, not `_confluence_config()`

Decision: name the shared config-reading function in `general/tools/_confluence_config.py` as `confluence_config()` (no leading underscore), even though the plan's task list parenthetically writes it as `_confluence_config()`. Rationale: the module itself is already private (leading-underscore filename), and both `confluence_fetch.py` and the future `confluence_update.py` import this function as a sibling-module symbol -- a non-underscore-prefixed name exported via the module's own `__all__` is the clearer, more idiomatic signal that it is the module's public API surface, while the module's filename alone already conveys "private to `general/tools/`". Also removed the local `_webfetch_config()`-style helper entirely from `confluence_fetch.py` in favor of importing this one shared function, per the plan's explicit instruction to not duplicate config-reading logic.

#### 2026-09-01 00:00:00.000Z — Accepted feat-37 -> feat-50-confluence manual id correction

Decision: use `create_feat` as designed (accepting its auto-assigned `feat-37-...` id), then manually rename the folder to `feat-50-confluence` and fix the frontmatter `id` field to match, rather than bypassing the tool entirely or leaving the mismatched sequential id in place. Rationale: keeps the tool as the primary creation path (per project convention) while preserving the GitHub-issue-number/branch-name correspondence every other feature folder in this repository follows; `create_feat`'s current design has no parameter to target a specific issue number directly.

#### 2026-09-01 00:00:00.000Z — Keep binary-download support despite confirmed real-instance limitation

Decision: implement `confluence_fetch`'s content-type-based binary download exactly as designed, and document the confirmed oauth2-proxy limitation as a known environment constraint, rather than dropping the feature or attempting a session-cookie workaround. Rationale: the implementation is correct and portable to Confluence deployments without this specific proxy restriction; the limitation is infrastructure the project does not control.

### Related PRs / Commits

- [Issue #50](https://github.com/dfch/biz.dfch.SpecMgr/issues/50): tracking issue for this feature.

### More Information

None.
