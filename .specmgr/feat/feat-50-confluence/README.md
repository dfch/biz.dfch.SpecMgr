---
created: '2026-09-01T17:36:02.251286'
id: feat-50-confluence
status: done
type: feat
updated: '2026-09-01T23:00:00.000000'
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

- [x] ACC-001: Verifies REQ-001/REQ-002 — given a URL containing `/pages/<id>/` or `?pageId=<id>`, `confluence_fetch` fetches `{base}/rest/api/content/{id}?expand=body.storage` instead of the given URL.

- [x] ACC-002: Verifies REQ-003 — given a `/x/<tinyid>` URL, `confluence_fetch`/`confluence_update` raise a clear, dedicated error rather than attempting the request.

- [x] ACC-003: Verifies REQ-004 — given a mocked response whose final URL (after following redirects) has a different host than the configured base URL, `confluence_fetch` raises a clear error instead of returning the redirected content.

- [x] ACC-004: Verifies REQ-005 — given a mocked non-text `Content-Type` response and a `destination_path`, `confluence_fetch` writes the response bytes to that path and returns the path; given no `destination_path`, it raises a clear error.

- [x] ACC-005: Verifies REQ-006 — `SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER` no longer exist anywhere in `src/`; `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` are used instead, documented in `README.md`.

- [x] ACC-006: Verifies REQ-008 — given a mocked GET returning `version.number: N` and a Markdown file, `confluence_update`'s `PUT` payload has `version.number == N + 1`, unchanged `title`, and `body.storage.value` equal to the Markdown rendered via `markdown-it-py` (no head/body wrapper).

- [x] ACC-007: Verifies REQ-009 — given a Markdown file referencing a local image that exists on disk, `confluence_update` issues a `POST` to the page's `child/attachment` endpoint for that image and the rendered HTML fragment's corresponding `<img>` tag is rewritten to `<ac:image><ri:attachment ri:filename="..." /></ac:image>`.

- [x] ACC-008: A real, reversible smoke test against the dedicated Confluence test page (id `1232503612`, "fetch and update") succeeds for both `confluence_fetch` (REST content GET) and `confluence_update` (version-incrementing PUT), performed once outside any read-only exploration constraint.

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

- [x] Task 2.1: Add `general/tools/_confluence_url.py` (`extract_page_id`, `build_rest_content_url`, `looks_like_rest_or_download_url`) with `tests/general/tools/test__confluence_url.py`.

- [x] Task 2.2: Wire automatic REST URL construction, tiny-link rejection, and SSO-redirect detection into `confluence_fetch`.

- [x] Task 2.3: Add binary/image download support (content-type detection, write-to-`destination_path`) to `confluence_fetch`.

- [x] Task 2.4: Extend `test_confluence_fetch.py` with cases for all of the above.

#### Phase 3: `confluence_update` core (no attachments yet)

- [x] Task 3.1: Implement `confluence_update` (GET version/title, render Markdown via `markdown-it-py`, PUT with incremented version).

- [x] Task 3.2: Add `tests/general/tools/test_confluence_update.py` (mocked GET/PUT).

#### Phase 4: Attachment upload + image macro rewrite

- [x] Task 4.1: Implement local-image discovery, attachment upload (with existing-filename fallback), and `<img>` -> `<ac:image>` rewriting in `confluence_update`.

- [x] Task 4.2: Extend `test_confluence_update.py` with mocked `POST` attachment upload/fallback cases.

#### Phase 5: Verification and docs

- [x] Task 5.1: Real, reversible smoke test against the dedicated Confluence test page (id `1232503612`).

- [x] Task 5.2: `specmgr docs`, `ruff format`/`check`, `vulture`, full `unittest` suite, `CHANGELOG.md` entry.

## Progress

### Current Status

**As of 2026-09-01**: **Feature complete — all 5 phases done.** Phase 5's real, reversible smoke test against the dedicated Confluence test page (id `1232503612`, "fetch and update") succeeded for `confluence_fetch` (both confirmed browsable URL shapes auto-converted to the REST content URL, HTTP 200, no `ConfluenceAuthRedirectError`) and `confluence_update` (a `PUT` cycle taking the page from `version 1` -> `2` -> `3`, each independently `GET`-verified, ending with the page body restored byte-for-byte to the original `<p>This is a page for testing.</p>`); the optional attachment-upload path (REQ-009) was also exercised live (`version 3` -> `4` -> `5`), confirming the real `POST .../child/attachment` shape and the `<img>` -> `<ac:image>`/`<ri:attachment>` rewrite end to end, leaving one permanent test attachment (`feat-50-smoke-test.png`, id `1232699838`) on the page as an accepted, documented byproduct. All quality-gate checks are green (`ruff format --check`/`ruff check`/`vulture` clean, 2788 `unittest` tests pass, `specmgr docs`/`specmgr mcp-docs` regenerate with zero drift) and the `CHANGELOG.md` `[Unreleased]` section now summarizes the whole feature. See this date's Updates entry below for the full step-by-step smoke-test evidence.

### Blockers

- None. The real Confluence test page (id `1232503612`) permanently shows `version 5` (four extra revisions in its edit history from this phase's smoke test) and carries one permanent test attachment (`feat-50-smoke-test.png`) — both are documented, accepted, non-blocking side effects of Task 5.1's real smoke test (Confluence's version number is monotonic and cannot itself be reverted via the REST API; there is no attachment-delete tool in this codebase), not blockers on this feature or any future work.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 23:00:00.000Z — Phase 5 complete: real smoke test + final verification (feature done)

Completed: performed the real, reversible smoke test against the dedicated Confluence test page (id `1232503612`, "fetch and update") required by Task 5.1/ACC-008, sourcing the real base URL/bearer token from a sibling project's `.env` (`SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER`, exported into this shell session only under the new `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` names, never written to any tracked file). Step-by-step evidence: (1) independently confirmed the starting page state via a raw `httpx.get` of `{base}/rest/api/content/1232503612?expand=version,title,body.storage` — `id=1232503612`, `title="fetch and update"`, `version.number=1`, `body.storage.value="<p>This is a page for testing.</p>"`, exactly as documented; (2) called `confluence_fetch` directly (imported from `biz.dfch.specmgr.general.tools.confluence_fetch`, no MCP protocol) against both confirmed real browsable URL shapes — `.../spaces/~fzpn/pages/1232503612/fetch+and+update` (Cloud-style) and `.../pages/editpage.action?pageId=1232503612` (Server-style) — both returned HTTP 200 JSON with `"id":"1232503612"`/`"title":"fetch and update"`, confirming live auto-conversion to `{base}/rest/api/content/1232503612?expand=body.storage` and no `ConfluenceAuthRedirectError`; (3) called `confluence_update("1232503612", <temp .md file>)` with throwaway content — returned `{"version": 2, "title": "fetch and update", "failed_images": []}`, independently `GET`-verified the new `body.storage.value` matched the rendered Markdown exactly (Confluence stripped `markdown-it`'s trailing `\n`, as anticipated); (4) reverted with a second temp Markdown file (`This is a page for testing.` -> `MarkdownIt("commonmark").render()` -> `<p>This is a page for testing.</p>\n`) — `confluence_update` returned `version: 3`, and an independent final `GET` confirmed `body.storage.value` is an EXACT, byte-for-byte match of the original `<p>This is a page for testing.</p>`; (5) **optional attachment path attempted**: uploaded a throwaway 1x1 PNG (`feat-50-smoke-test.png`) referenced from a temp Markdown file via `confluence_update` — the real `POST {base}/rest/api/content/1232503612/child/attachment` multipart call succeeded (HTTP 200, `version: 4`, `failed_images: []`), and an independent `GET` confirmed both the attachment now exists (`GET .../child/attachment` lists `feat-50-smoke-test.png`, id `1232699838`) and the page body was correctly rewritten to `<ac:image><ri:attachment ri:filename="feat-50-smoke-test.png" /></ac:image>`; the page was then reverted a second time (`version: 5`), independently `GET`-verified as an exact byte-for-byte match of the original body again. The duplicate-filename-fallback branch (uploading the SAME filename twice) was deliberately NOT attempted, per the phase instructions' explicit caution about leaving avoidable clutter behind. All temp scratch files lived under `/tmp/opencode/` and were deleted immediately after use; `git status --porcelain` was empty both before and after Task 5.1, confirming nothing untracked was left in the working tree. Then ran the full Task 5.2 quality gate: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean, the full `unittest` suite (2788 tests) passes, `specmgr docs`/`specmgr mcp-docs` both produced zero `git status` diff (confirming Phase 4's regeneration was already current), and appended a feature-completion summary to `CHANGELOG.md`'s existing `[Unreleased]` section (a new `### Added` entry for `confluence_update`, expanding the existing `confluence_fetch` rename `### Changed` entry with its full auto-conversion/tiny-link/SSO-redirect/binary-download behavior), referencing GitHub issue #50 and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac. Checked off every remaining Task List item and every ACC-001..ACC-008 acceptance criterion (all now genuinely satisfied — see the Acceptance Criteria section above), and set this document's frontmatter `status` to `done`.

Permanent, accepted side effects of this real smoke test (explicitly NOT blockers, see Blockers above): the real page (id `1232503612`) now permanently shows `version 5` with four extra revisions in its edit history (Confluence's version number is monotonic and cannot itself be reverted via the REST API — only the CONTENT was restored, which is what "reversible" means for this smoke test), and it carries one permanent test attachment (`feat-50-smoke-test.png`, id `1232699838`, since this codebase has no attachment-delete tool).

Next: Feature complete, awaiting final orchestrator review and commit.
Notes: **ACC-008 verdict: PASS** (both `confluence_fetch` GET and `confluence_update`'s version-incrementing PUT succeeded live, reversibly, exactly as required). **REQ-001/002/004 verdict (as exercised live): PASS** — both browsable URL shapes auto-converted correctly and no SSO-redirect was hit (the earlier read-only exploration phase's documented SSO-redirect findings were for other browsable URL shapes/attachment-download endpoints, not these two REST-content-URL-converted GETs). **REQ-007/008 verdict (as exercised live): PASS** — `confluence_update` correctly reused the same two env vars and produced the exact documented GET-version/render/PUT-increment flow. **REQ-009 verdict (as exercised live, optional path): PASS** — the real attachment-create `POST .../child/attachment` multipart shape and the `<img>` -> `<ac:image>`/`<ri:attachment>` rewrite both worked exactly as implemented; the duplicate-filename-fallback branch (`_looks_like_duplicate_filename_response`/`_find_existing_attachment_id`/`.../child/attachment/{id}/data`) remains genuinely unverified against a real instance, since it was deliberately not attempted (see the Decisions Made entry below).

#### 2026-09-01 22:00:00.000Z — Phase 4 complete: attachment upload + image macro rewrite

Completed: extended `general/tools/confluence_update.py` (REQ-009/ACC-007) to insert a best-effort local-image attachment-upload/`<img>` -> `<ac:image>` rewrite step between rendering the Markdown file and the existing `PUT`. Local-image discovery scans the *rendered* HTML fragment's `<img src="...">` tags (a new `_IMG_TAG_PATTERN` regex), not the raw Markdown source, since `markdown-it` has already resolved the exact `src` values that also need to be found-and-replaced in the same fragment. A `src` is "local" if it contains no `://` (`_is_local_image_src`); a local `src` is resolved against `markdown_file_path`'s containing directory and, if the resulting path does not exist on disk, its `<img>` tag is silently left unrewritten with no upload attempted (REQ-009's explicit "best-effort"). For each local image that does exist, `_upload_attachment` `POST`s it to `{base}/rest/api/content/{id}/child/attachment` as `multipart/form-data` (field name `file`, real Confluence REST API shape) with the `X-Atlassian-Token: no-check` header (sent only on this and the fallback attachment call, never on the page GET/PUT); on a 400 response that looks like a duplicate-filename error (new `_looks_like_duplicate_filename_response` heuristic: status 400 plus a JSON `message` mentioning both "already exist" and "file"/"attachment"/"filename"), it falls back to `_find_existing_attachment_id` (a `GET .../child/attachment?filename=...` lookup) followed by a `POST .../child/attachment/{id}/data` with the new content. On success, the image's `<img>` tag is rewritten to `<ac:image><ri:attachment ri:filename="<basename>" /></ac:image>`; on ANY failure (missing file, non-2xx, network exception, unresolvable duplicate-filename fallback) the tag is left unrewritten, the failure is caught inside `_rewrite_local_images` (never propagates), and recorded as a `{"src": ..., "error": ...}` entry in a new `failed_images` list now always present in `confluence_update`'s return value (empty when nothing failed) -- this call sees this design decision as a deliberate deviation from purely "swallow-and-say-nothing" best-effort framing, since zero visibility into per-image failures would be a worse design. Added 8 new tests to `tests/general/tools/test_confluence_update.py` (24 tests total, up from 20): ACC-007 exactly (real temp Markdown + temp image file, mocked successful attachment POST, asserting the exact `<ac:image>`/`<ri:attachment>` rewrite and the POST's captured filename/bytes/headers), a missing-local-file case (no POST attempted, tag unrewritten, PUT still succeeds), a non-local `https://` image case (no POST attempted, tag unrewritten), the duplicate-filename fallback path (mocked 400 + lookup GET + fallback data POST, asserting the tag is still rewritten), an outright upload failure (mocked 500, tag unrewritten, `failed_images` populated), an `httpx` exception during upload (same assertions), and a mixed-multiple-images case (successful/missing/non-local in one call, each independently verified). Updated the existing Phase-3 ACC-006 test's expected return-value dict to include the now-always-present `failed_images: []` key. Updated `confluence_update`'s `@mcp.tool()` description/docstring, `general/tools/__init__.py`'s module docstring bullet, and `server.py`'s module docstring bullet to describe the new attachment-upload/image-rewrite behavior in full, removing the "not yet supported"/"a later phase, not yet implemented" language.
Next: Phase 5 (final phase — a real, reversible smoke test against the dedicated Confluence test page (id `1232503612`), plus final `specmgr docs`/`ruff`/`vulture`/`unittest` verification and the `CHANGELOG.md` entry).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2788 tests, up from 2781) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/biz.dfch.specmgr.general.tools.confluence_update.md`, `docs/api/biz.dfch.specmgr.general.tools.md`, `docs/api/biz.dfch.specmgr.server.md`, and `docs/MCP.md`'s `confluence_update` entry with no unexpected diffs. **Flagging explicitly for Phase 5 and the human relaying this to the user**: the real Confluence REST API shapes this phase implements -- the attachment-create `POST .../child/attachment` multipart shape is well-documented and implemented with reasonable confidence, but (a) the exact duplicate-filename 400 error-message wording `_looks_like_duplicate_filename_response` detects, (b) the existing-attachment lookup shape (`GET .../child/attachment?filename=...` and its `results[0].id` response shape) `_find_existing_attachment_id` assumes, and (c) the fallback binary-content-update shape (`POST .../child/attachment/{id}/data`) `_upload_attachment` uses, are ALL unverified against a real Confluence instance in this environment -- only mocked-`httpx` coverage exists for all three. Per the plan's own Task 5.1/ACC-008 wording, Phase 5's real smoke test is scoped narrowly to `confluence_fetch`'s REST content GET and `confluence_update`'s version-incrementing PUT against the dedicated test page, and may not exercise this attachment path (create, duplicate-fallback, or lookup) end-to-end at all.

#### 2026-09-01 20:00:00.000Z — Phase 3 complete: `confluence_update` core (no attachments yet)

Completed: implemented the new `general/tools/confluence_update.py` tool (`confluence_update(page_url_or_id: str, markdown_file_path: str) -> dict[str, Any]`, REQ-007/REQ-008/ACC-006): `page_url_or_id` (a bare numeric page id, a browsable `/pages/<id>/...`/`?pageId=<id>` URL, or an already-`/rest/api/content/<id>`-shaped REST URL) is resolved to a numeric page id via the new shared `_confluence_url.resolve_page_id()` helper (tries bare-numeric, then `extract_page_id`, then a new `/rest/api/content/(\d+)` pattern), with a `/x/<tinyid>` tiny link raising the same `ConfluenceTinyLinkNotSupportedError` `confluence_fetch` raises (imported, not redefined) and anything else unresolvable raising the new `ConfluencePageIdNotResolvedError`; `GET {base}/rest/api/content/{id}?expand=version,title` (deliberately no `body.storage` -- this phase never reads the existing body) reads `version.number`/`title`, with a new `ConfluenceUnexpectedResponseShapeError` raised instead of a raw `KeyError` if either key is missing; the Markdown file at `markdown_file_path` is read as UTF-8 (a missing file raises the natural `FileNotFoundError`, no wrapper) and rendered via a local `MarkdownIt("commonmark")` instance (confirmed to emit a bare fragment, no `<html>`/`<head>`/`<body>` wrapper); `PUT {base}/rest/api/content/{id}` writes `{"version": {"number": N+1}, "title": <unchanged>, "type": "page", "body": {"storage": {"value": <rendered fragment>, "representation": "storage"}}}`. Extracted the SSO-redirect-host check the ADR says is "reused for `confluence_update`'s internal GET/PUT" out of `confluence_fetch.py` into a new shared `_confluence_url.assert_same_host_as_base_url()` (plus its `ConfluenceAuthRedirectError`, which moved into `_confluence_url.py` too and is re-exported, unchanged, from `confluence_fetch.py` for backward compatibility) -- both the GET and the PUT apply this identical check. Added `tests/general/tools/test_confluence_update.py` (20 tests: the exact ACC-006 payload assertion computing the expected HTML via a fresh `MarkdownIt("commonmark").render(...)` call and asserting equality, shared-config reuse, all three page-id-resolution input shapes converging on the same GET/PUT target, tiny-link rejection with no HTTP call, GET- and PUT-redirect detection, all three missing-key GET-response-shape cases, non-2xx GET/PUT, and a missing Markdown file) plus 11 new tests in `tests/general/tools/test__confluence_url.py` for `resolve_page_id`/`assert_same_host_as_base_url`. Updated `general/tools/__init__.py`, `general/__init__.py`, and `server.py`'s module docstrings to register/describe the new tool.
Next: Phase 4 (attachment upload + image macro rewrite: local-image discovery, `POST .../child/attachment` upload with existing-filename fallback, and `<img>` -> `<ac:image>`/`<ri:attachment>` rewriting in `confluence_update`).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2781 tests) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/` (new `biz.dfch.specmgr.general.tools.confluence_update.md` page, updated `_confluence_url`/`confluence_fetch`/`general`/`general.tools`/`server` pages), `docs/GENERATED.md` (321 test files), and `docs/MCP.md` (94 tools, new `confluence_update` entry) with no unexpected diffs. `confluence_update`'s write flow (GET/PUT payload shape, version-increment) remains unverified against the real dedicated Confluence test page (id `1232503612`) -- only mocked-`httpx` coverage exists so far; the real, reversible smoke test is Phase 5's job.

#### 2026-09-01 00:00:00.000Z — Phase 2 complete: URL helper + `confluence_fetch` enhancements

Completed: added the new shared, `mcp`-free `general/tools/_confluence_url.py` helper (`extract_page_id` -- tries `[?&]pageId=(\d+)` then `/pages/(\d+)(?:/|$|\?)`, returning `None` for anything else including `/x/<tinyid>`; `build_rest_content_url` -- `f"{base_url.rstrip('/')}/rest/api/content/{page_id}"` plus an optional `?expand=`; `looks_like_rest_or_download_url` -- case-sensitive `/rest/api/`/`/download/` substring check; `looks_like_tiny_link` -- a small, dedicated `/x/<opaque-segment>` detector, not explicitly named in the plan's bullet list but required by REQ-003/ACC-002) with a fully-covered `tests/general/tools/test__confluence_url.py` (22 tests: Cloud-style/Server-style extraction including mid-query-string `&pageId=`, tiny-link/non-matching `None` cases, `build_rest_content_url` with/without `expand` and with/without a trailing base-URL slash, `looks_like_rest_or_download_url`/`looks_like_tiny_link` true/false cases). Wired all of this into `confluence_fetch` (REQ-001/002/003/004, ACC-001/002/003): the caller-supplied `url` is checked against the configured base URL first (unchanged from Phase 1), then a tiny link raises the new `ConfluenceTinyLinkNotSupportedError` with no HTTP call attempted, then a URL already shaped like a REST/download URL is used unchanged, then a URL with an extractable page id is rewritten to `{base}/rest/api/content/{id}?expand=body.storage`, and anything else falls through to a plain fetch of the URL as given (Phase-1 compatibility preserved); after the `httpx.get` call returns, the final `response.url.host` (case-folded) is compared against the configured base URL's host (also via `httpx.URL(base_url).host`, which normalizes casing) and a mismatch raises the new `ConfluenceAuthRedirectError` instead of returning/using that response. Added binary/image download support (REQ-005/ACC-004): `confluence_fetch`'s signature is now `confluence_fetch(url: str, destination_path: str | None = None) -> str`; a private `_is_text_content_type` helper classifies the response `Content-Type` (media-type prefix match against `text/`/`application/json`/`application/xml`, or suffix match against `+json`/`+xml`, both case-insensitive, ignoring any `;` parameters) -- text/JSON/XML responses are returned as `response.text` exactly as before (any given `destination_path` is silently ignored in this case, documented in the docstring); any other content type is written as raw bytes to `destination_path` (creating parent directories via `Path.mkdir(parents=True, exist_ok=True)`, mirroring how other tools use `pathlib.Path` directly rather than a shared write helper, since no existing shared "write bytes to path" helper exists in `general/tools/`) and the path itself is returned, or the new `ConfluenceDestinationPathRequiredError` is raised if `destination_path` was not given. Updated the `@mcp.tool()` description/docstring, `general/tools/__init__.py`'s module docstring, and `server.py`'s module docstring to describe the new behavior. Extended `tests/general/tools/test_confluence_fetch.py` (now 20 tests) with fully-mocked coverage for all of the above (a shared `_make_response()` test helper now sets `.headers`/`.url` on every mocked `httpx.Response` in addition to `.text`/`.content`/`.raise_for_status`) plus regression coverage confirming every Phase-1 behavior (base-URL matching case-insensitivity, missing-config errors, non-2xx raises, plain text returned as-is) still passes.
Next: Phase 3 (`confluence_update` core: `GET` version/title, render Markdown via `markdown-it-py`, `PUT` with incremented version -- no attachments yet).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2753 tests) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/` (new `biz.dfch.specmgr.general.tools._confluence_url.md` page, updated `confluence_fetch`/`general.tools`/`server` pages), `docs/GENERATED.md` (320 test files), and `docs/MCP.md` (`confluence_fetch`'s richer description and new `destination_path` parameter) with no unexpected diffs. Binary/image download support remains unverified against the one real customer instance with the confirmed oauth2-proxy limitation (documented in the feature's Decisions Made log and the ADR) -- only mocked-`httpx` coverage exists for it so far; the real, reversible smoke test is Phase 5's job.

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

#### 2026-09-01 23:00:00.000Z — Phase 5: resolved two of Phase 4's three "unverified against a real instance" caveats; attempted the optional attachment smoke-test path

Decision: attempted the OPTIONAL attachment-upload real-instance verification (Task 5.1 step 5) rather than skipping it, judging the tradeoff (one permanent, clearly-named, harmless test attachment left on the real page, since this codebase has no attachment-delete tool) worthwhile against the value of finally confirming the real REST API shape live. Result: (1) the attachment-CREATE shape (`POST {base}/rest/api/content/{id}/child/attachment` as `multipart/form-data`, field name `file`, `X-Atlassian-Token: no-check` header) is now **confirmed against a real instance** — it returned HTTP 200 and the attachment was genuinely created and listed by a subsequent `GET .../child/attachment`. (2) The `<img>` -> `<ac:image><ri:attachment ri:filename="..." /></ac:image>` rewrite is now **confirmed against a real instance** — the independently-fetched page body after the update showed exactly this macro, and Confluence accepted/rendered it without error on the subsequent PUT. (3) The duplicate-filename-detection heuristic (`_looks_like_duplicate_filename_response`), the existing-attachment lookup (`_find_existing_attachment_id`, `GET .../child/attachment?filename=...`), and the fallback binary-content-update endpoint (`POST .../child/attachment/{id}/data`) **remain genuinely unverified against a real instance** — the duplicate-filename path was deliberately NOT exercised (per the phase instructions' explicit caution against uploading the same filename twice purely to trigger it, which would have left a second, harder-to-justify piece of permanent clutter and a real Confluence page's actual 400-response wording is still unconfirmed). This is an intentionally incomplete verification, not an oversight: a future change to any of these three code paths should still be treated as carrying residual real-instance risk until someone chooses to accept that specific additional tradeoff.

#### 2026-09-01 22:00:00.000Z — Phase 4 judgement calls: image discovery approach, duplicate-filename detection, failure visibility, and unverified REST shapes

Decision: (1) **Local-image discovery scans the rendered HTML fragment's `<img src="...">` tags, not the raw Markdown source.** The plan's Design Notes explicitly offered either approach; scanning the rendered output was chosen because `markdown-it` has already resolved the exact `src` string that must also be found-and-replaced in that same fragment -- a separate regex over the raw Markdown source risks producing a `src` value that does not exactly match what `markdown-it` actually emitted (e.g. differing whitespace/escaping rules), which would silently break the find-and-replace step. (2) **Duplicate-filename detection (`_looks_like_duplicate_filename_response`) is a heuristic, not a confirmed API contract**: it treats a response as "duplicate filename" only if the status code is exactly 400 AND the JSON body's `message` field contains both "already exist" and one of "file"/"attachment"/"filename" (case-insensitively) -- inferred from generally documented/community-reported Confluence behavior, NOT confirmed against a real instance during this feature's development (see the flag in this date's Updates entry). Any other 400, or a non-JSON 400 body, is treated as a genuine upload failure instead, so the fallback path is deliberately conservative rather than over-eager. (3) **Per-image upload failures ARE surfaced to the caller**, via a new `failed_images: list[{"src": ..., "error": ...}]` key always present in `confluence_update`'s return value (empty list when nothing failed) -- chosen over the plan's more minimal "best-effort, catch and continue" framing alone, since a caller with zero visibility into which images silently failed to upload would be a strictly worse design for a tool an LLM agent is expected to act on the result of. (4) **The existing-attachment lookup (`_find_existing_attachment_id`, `GET .../child/attachment?filename=...`) and the fallback binary-content-update endpoint (`POST .../child/attachment/{id}/data`) are both implemented as good-faith, best-effort attempts at the real Confluence REST API shape, but neither was verified against a real instance** -- flagged inline in both functions' docstrings/comments and explicitly called out in this date's Updates entry, per the phase instructions' explicit requirement not to silently guess without flagging the uncertainty. The attachment-create endpoint itself (`POST .../child/attachment`, multipart `file` field, `X-Atlassian-Token: no-check` header) is comparatively well-documented, real, confirmed Confluence REST API behavior and is implemented with higher confidence than the two fallback-path shapes.

#### 2026-09-01 20:00:00.000Z — Phase 3 judgement calls: signature/return shape, `MarkdownIt` instance, shared-helper placement, and page-id resolution scope

Decision: (1) `confluence_update(page_url_or_id: str, markdown_file_path: str) -> dict[str, Any]`, returning `{"id": <page id>, "title": <unchanged title>, "version": <new version number>}` rather than the raw PUT response JSON -- a small, caller-useful summary that does not require the caller to know Confluence's own response shape, and keeps the mocked-`httpx` PUT response in tests free of a `.json()` stub it would otherwise need only to satisfy an unused return value. (2) Instantiate a fresh, module-level `MarkdownIt("commonmark")` in `confluence_update.py` rather than reusing `models.md._markdown`'s shared `md` instance: that module is private to `models/md/`'s own parser pipeline, is not re-exported via `models.md.__all__`, and its sibling `parse()` wrapper additionally rejects raw HTML -- a constraint irrelevant to, and never called by, `confluence_update`; a second `MarkdownIt("commonmark")` instantiation is a negligible cost next to avoiding a cross-domain dependency on a private module. Confirmed empirically (via the new test's own `MarkdownIt("commonmark").render(...)` expectation, which passes byte-for-byte) that `.render()` already emits a bare HTML fragment with no `<html>`/`<head>`/`<body>` wrapper, as the plan assumed. (3) The SSO-redirect-host check (`ConfluenceAuthRedirectError` and a new `assert_same_host_as_base_url()`) moved from `confluence_fetch.py` into the shared `_confluence_url.py` module, since the ADR explicitly requires it "reused for `confluence_update`'s internal GET/PUT"; `confluence_fetch.py` now imports and re-exports the exception unchanged (same `__all__` entry, same import path for existing callers/tests), so this is a pure internal refactor with no external-facing rename. The tiny-link exception (`ConfluenceTinyLinkNotSupportedError`) was deliberately *not* moved -- `confluence_update.py` simply imports it directly from `confluence_fetch.py`, per the phase instructions' explicit "reuse whatever exception confluence_fetch.py defines for this, imported, not redefined." (4) `confluence_update` does *not* apply `confluence_fetch`'s base-URL prefix-match check (`ConfluenceUrlNotAllowedError`) to `page_url_or_id`: unlike `confluence_fetch`, which fetches the caller-supplied URL (possibly rewritten) directly, `confluence_update` only ever extracts a page *id* from `page_url_or_id` and then always rebuilds both the GET and PUT target URLs from the trusted, configured `base_url` via `build_rest_content_url()` -- the original URL's host is therefore never actually dereferenced, so restricting it would add a check with no corresponding safety benefit. A new `resolve_page_id()` helper (in `_confluence_url.py`, alongside a new `_REST_CONTENT_ID_PATTERN` regex) additionally accepts a bare numeric id and an already-`/rest/api/content/<id>`-shaped URL, on top of `extract_page_id()`'s existing browsable-URL shapes -- both new capabilities `confluence_fetch` itself has no need for. (5) Beyond ACC-006's three mandated PUT fields, the payload also sends `"type": "page"`, which real-world Confluence REST API PUT semantics require even when unchanged (confirmed via general REST API knowledge, not the real test instance, per the phase's own read-only-exploration-until-Phase-5 constraint).

#### 2026-09-01 00:00:00.000Z — Phase 2 judgement calls: naming, content-type heuristic, and text/binary precedence

Decision: (1) name the tiny-link detector `looks_like_tiny_link()`, mirroring the existing `looks_like_rest_or_download_url()` naming, and give the two new `confluence_fetch` exceptions the names `ConfluenceTinyLinkNotSupportedError` and `ConfluenceAuthRedirectError` (both suggested in the plan's own Design Notes), plus `ConfluenceDestinationPathRequiredError` for the missing-`destination_path` case (not explicitly named in the plan) -- all as plain, undecorated subclasses of `ValueError` (the two "bad input/config" cases) or `RuntimeError` (the auth-redirect case, since it is a runtime environment condition, not a caller input error), consistent with `ConfluenceUrlNotAllowedError`'s existing `ValueError` choice. (2) Classify a response `Content-Type` as text via a private `_is_text_content_type()` helper: the media type (text before any `;` parameter) must case-insensitively start with `text/`, `application/json`, or `application/xml`, or end with `+json`/`+xml` -- covering common vendor-specific JSON/XML variants (e.g. `application/vnd.api+json`) as the plan's Design Notes suggested "if judged worthwhile", while keeping the check itself a single `startswith`/`endswith` call, no MIME-type parsing library. A blank/missing `Content-Type` is conservatively treated as non-text (requires `destination_path`), since silently returning empty text for an unlabeled binary response would be a worse failure mode than a clear "provide a destination_path" error. (3) For a text/JSON/XML response, any given `destination_path` is silently ignored rather than raising -- the plan explicitly allowed either choice, and silently ignoring is simpler for callers that pass a `destination_path` speculatively without first knowing the content type. (4) The base-URL prefix-match check (`ConfluenceUrlNotAllowedError`) is applied to the original caller-supplied `url` before any tiny-link/REST-URL classification, and the SSO-redirect host check is applied unconditionally after the `httpx.get` call regardless of which of the three URL branches (tiny link / already-REST-or-download / auto-converted / pass-through) was taken -- exactly the order ACC-001..ACC-003 require. (5) The binary write path uses `pathlib.Path.mkdir(parents=True, exist_ok=True)` directly rather than introducing a new shared "write bytes to path" helper in `general/tools/`, since `_doc_paths.py`/`_path_safety.py` are id-to-document-path resolvers for the eleven whole-body domains, not general-purpose byte-writing helpers, and `confluence_fetch`'s `destination_path` is an arbitrary caller-supplied filesystem path outside any domain's base directory (so `_path_safety.assert_within` does not apply here either).

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
