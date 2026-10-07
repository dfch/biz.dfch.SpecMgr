# History: Confluence Fetch and Update Tools

#### 2026-09-02 04:00:00.000Z - Phase 8 added: sync with upstream `dev`; new `confluence_update`/`confluence_fetch` MCP prompts

Completed: per the user's explicit request, added Phase 8 (6 tasks, REQ-012/REQ-013,
ACC-011/ACC-012) to the Task List: (1) merge `origin/dev` into this feature branch, since `dev` has
advanced by 2 large merged PRs (`#52` "make every validation error message actionable",
`#49` "specmgr docs prunes stale docs/api pages") since this branch's fork point, confirmed via
`git fetch origin` + `git rev-list --left-right --count origin/dev...HEAD` (2 commits only on
`origin/dev`, 7 only on this branch) and `git diff --stat` (192 files changed on `dev`'s side, none
overlapping `general/tools/confluence_*.py` or its tests -- expected conflicts are limited to
generated/shared files this feature also touched: `CHANGELOG.md`, `docs/GENERATED.md`,
`docs/api/README.md`); (2) add a new `confluence_update` MCP prompt (same name as the existing
tool, a separate MCP registry, per this codebase's `create_adr`/`create_dec`/`create_gol`/
`create_req` precedent) taking the same `page_url_or_id`/`markdown_file_path` parameters and
instructing an LLM to call the `confluence_update` tool with them; (3) add a new `confluence_fetch`
MCP prompt taking the same `url`/`destination_path` parameters and instructing an LLM to call the
`confluence_fetch` tool with them. The sync (Task 8.1) is ordered first even though the user listed
the two new prompts first in their own request, purely to build the new prompts on the
freshly-merged base rather than doing the work twice against a soon-to-be-stale branch. A separate,
earlier request from the user (to add a new MCP/CLI command wrapping the same upload/download
workflow as a *tool*, discussed but never actioned in the prior 2026-09-02 02:00 Updates entry) was
explicitly reframed by the user as these two *prompts* instead, and is considered fully superseded
by this Phase 8 addition -- not a separate, still-open request. Reverted this document's
frontmatter `status` from `done` back to `in-progress`.
Next: Phase 8 (sync with `dev`, then implement both new prompts).
Notes: implementation has not started; this update only covers planning (Task List/REQ/ACC
additions).


#### 2026-09-02 03:00:00.000Z - Phase 7 complete: HTML-comment sanitization + frontmatter-to-code-block conversion fixed and re-verified live; feature done again

Completed: fixed both real content-robustness bugs found by the post-completion investigation
(Task 7.1/Task 7.3), in `general/tools/confluence_update.py`. (1) REQ-010/ACC-009: a new
`_sanitize_html_comments(html)` helper (applied to the rendered HTML fragment, right after
`_MD.render(...)` and before `_rewrite_local_images`) finds every `<!-- ... -->` comment via a
`re.DOTALL`, non-greedy `_HTML_COMMENT_PATTERN = re.compile(r"<!--(.*?)-->", re.DOTALL)` and
replaces every `--` inside the comment body with an em dash (`—`); if the sanitized body would
still end in a bare `-` immediately before the closing `-->` (also invalid per the XML comment
grammar), a single trailing space is appended. Handles multi-line comments, multiple `--`
occurrences, and multiple separate comments in one fragment (verified by dedicated unit tests, not
just the integration-level ACC-009 test). (2) REQ-011/ACC-010: a new
`_convert_leading_frontmatter_to_code_block(markdown_text)` helper (applied to the RAW Markdown
text, BEFORE `_MD.render(...)`) detects a leading YAML frontmatter block by requiring the
markdown text's literal first line (no leading blank lines tolerated -- deliberately strict, per
this codebase's own frontmatter convention) to be exactly `---` (trailing whitespace tolerated via
`.strip()`) and a LATER line to also be exactly `---`; if found, that whole span is replaced with
a fenced code block using FOUR backticks (`` ```` ``, not the usual three -- unambiguous even in
the unlikely case the YAML content itself contains a triple-backtick run) and a `yaml` language
hint, containing the same inner content completely unmodified. If no closing `---` is found, or
the first line is not exactly `---`, the text is returned untouched -- verified by dedicated unit
tests for "no frontmatter", "unclosed opening fence", "fence lines with trailing whitespace" (still
detected), and "leading blank line before the opening fence" (NOT treated as frontmatter). Neither
`models.md.frontmatter.MarkdownFrontmatter` (a Pydantic model for already-parsed fields, not raw-
span detection) nor the `python-frontmatter` library used by `models.adr.v1.parser` (which
re-serializes the YAML through its own dumper, which would NOT preserve the content "completely
unmodified" as required) were suitable for reuse, so both new helpers are private, local functions
in `confluence_update.py`, per the task's own explicit fallback guidance. Wired both into
`confluence_update`'s write flow (Task 7.1/7.3) and added 10 new tests to
`test_confluence_update.py` (Task 7.2/7.4): 2 integration-level tests (ACC-009's exact confirmed
real scenario -- a Markdown file with `<!-- Newest entry first -- prepend ... -->`, asserting the
final `body.storage.value` has no raw `--` inside any `<!-- -->` comment; ACC-010's exact confirmed
real scenario -- a leading YAML frontmatter block, asserting the final body has no `<h2>`/`<hr>`
and does have a `<pre>` block with the frontmatter content and a correctly-rendered `<h1>Heading</h1>`
immediately after) plus 8 unit-level tests directly exercising the two private helpers' edge cases
(em-dash replacement, trailing-bare-hyphen guarding, multiple separate comments, no-comments
passthrough, no-frontmatter passthrough, unclosed-fence passthrough, trailing-whitespace-on-fence
detection, leading-blank-line non-detection). Updated `confluence_update`'s module docstring (Task
7.5) to document the frontmatter-conversion and comment-sanitization steps as new steps 3/4 in the
write flow (renumbering the later steps), and its `@mcp.tool()` `description` string with a short
mention of both. Re-ran the full quality gate (Task 7.5): `ruff format --check`/`ruff check`/
`vulture` clean; full `unittest` suite green, 2799 tests (up from 2789, the 10 new tests);
`specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/biz.dfch.specmgr.general.tools.confluence_update.md`
and `docs/MCP.md`'s `confluence_update` entries with no unexpected diffs (only the docstring/
description wording changes made above). Amended the existing `[Unreleased]` `confluence_update`
bullet in `CHANGELOG.md` (not a new `### Fixed` entry, matching Phase 6's precedent, since this
feature has not shipped in a release yet) to document both new robustness behaviors.

Attempted and PASSED Task 7.6 (optional live re-verification), sourcing the real base URL/bearer
token from the sibling project's `.env` (same pattern as Phases 5/6, exported under the new
`SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` names into this shell session only, never
written to any tracked file): called the FIXED `confluence_update` directly (imported, no MCP
protocol) against the real dedicated test page (id `1232503612`) with the REAL, UNMODIFIED
`.specmgr/feat/feat-50-confluence/README.md` path -- no scratch-copy workaround needed this time,
which was the whole point of the fix. The `PUT` succeeded on the first try (`version: 10`, no
manual intervention), confirming REQ-010's fix in the real environment. An independent follow-up
`GET` confirmed: the leading YAML frontmatter now renders as `<pre><code class="language-yaml">...
</code></pre>` (not `<hr>`/`<h2>`), immediately followed by the correct `<h1>Feature: Confluence
Fetch and Update Tools</h1>`, confirming REQ-011's fix live; and the stored body contains ZERO
`<!-- -->` HTML comments at all (`body.count("<!--") == 0`) -- Confluence's own storage layer
apparently strips HTML comments entirely on save, rather than preserving a sanitized version of
them, which was not anticipated but trivially satisfies ACC-009's "no raw `--` inside any comment"
requirement (there being no comment left to contain one), and does not indicate any defect in the
sanitization step itself (which is what made the `PUT` succeed in the first place -- confirmed by
the fact the identical unsanitized content had previously failed the `PUT` outright with the
strict-XHTML parser error). Immediately reverted the page back to its original test content via a
second `confluence_update` call (a throwaway `/tmp/opencode/revert.md` containing exactly
`This is a page for testing.`) -- returned `version: 11` -- and independently `GET`-verified the
reverted `body.storage.value` is an EXACT, byte-for-byte match of the original
`<p>This is a page for testing.</p>`. Cleaned up the throwaway revert file afterward; no untracked
files left behind from this real-instance testing. Restored this document's frontmatter `status`
from `in-progress` back to `done`.

Next: none -- feature complete again, and this time with two real-instance-confirmed content-
robustness fixes closing out the exact scenario (uploading this feature's own README) that first
surfaced the gap.
Notes: this closes out both genuine content-robustness defects found post-completion; the ADR's
chosen design (best-effort Markdown-to-storage-format rendering via `markdown-it-py`) remains
correct and unchanged -- these were pre-render/post-render sanitization steps layered on top, not
a change to the core rendering approach. The real Confluence test page (id `1232503612`) now
permanently sits at `version 11` (up from `version 8` at the start of this phase), with no other
permanent side effects beyond the version-number increments already documented in Blockers above.


#### 2026-09-02 02:00:00.000Z - Post-completion real-instance test uncovers two content-robustness bugs; Phase 7 added

Completed: at the user's request, uploaded this feature's own `.specmgr/feat/feat-50-confluence/README.md`
(a real, representative Markdown file -- YAML frontmatter, `<!-- -->` HTML comments, headings,
lists, links) to the dedicated Confluence test page (id `1232503612`) via `confluence_update`,
using the real base URL/bearer token from the sibling project's `.env` (same pattern as Phase 5/6).
The first attempt failed: `PUT` returned `400`, `"Error parsing xhtml: String '--' not allowed in
comment (missing '>'?)"`. Root cause: this repository's Markdown docs commonly write HTML comments
like `<!-- Newest entry first -- prepend new entries directly below this comment. -->` -- valid
CommonMark (raw HTML passes through `markdown-it` unmodified) but invalid strict XML/XHTML, which
disallows a bare `--` inside a comment body; Confluence's storage-format parser enforces this
strictly. Worked around it by hand in a scratch copy (`/tmp/opencode/`, not touching the repo file)
by replacing `--` with an em dash inside the two comments, then retried -- the `PUT` succeeded
(`version: 8`), independently `GET`-verified: the full rendered README is now the page's body.
However, the leading YAML frontmatter block rendered oddly: `markdown-it` treated the first `---`
as a thematic break (`<hr>`) and the frontmatter's closing `---` fence as a Setext-heading
underline, turning the whole frontmatter block into a single `<h2>` heading -- cosmetically wrong
but not a parse failure. Per the user's explicit request, added Phase 7 (6 tasks, REQ-010/REQ-011,
ACC-009/ACC-010) to fix both issues for real in `confluence_update`'s own code (not a one-off
manual workaround): (a) sanitize `--` inside rendered `<!-- -->` comments, (b) convert a leading
YAML frontmatter block into a fenced code block before rendering. Reverted this document's
frontmatter `status` from `done` back to `in-progress`. An earlier, separate request to add a new
MCP/CLI command wrapping this workflow was explicitly withdrawn by the user in favor of this
robustness-focused Phase 7 -- not tracked anywhere, intentionally not pursued.
Next: Phase 7 (fix HTML-comment sanitization and frontmatter-to-code-block conversion).
Notes: the real Confluence test page's body currently shows this feature's own README content
(from the scratch-copy workaround upload), not yet reverted to the original test text -- see
Blockers above and Phase 7's optional Task 7.6.


#### 2026-09-02 01:00:00.000Z - Phase 6 complete: duplicate-filename detection fixed; feature done again

Completed: fixed `_looks_like_duplicate_filename_response()` in `general/tools/confluence_update.py`
(Task 6.1) to accept the filename that was uploaded and treat a 400 response as a duplicate-filename
case if EITHER that filename itself (case-insensitively) appears in the JSON body's `message` field
(the new, primary check -- directly matches the real, confirmed Confluence message "Cannot add a new
attachment with same file name as an existing attachment: `<filename>`. Log referral number is
`<uuid>`", which never contained "already exist") OR the original "already exist" + keyword
combination still matches (kept as a secondary check for the community-reported message variant the
existing mocked test already covered, so no existing test needed to change). Updated the call site in
`_upload_attachment` to pass the uploaded filename through. Added a new regression test,
`test_real_duplicate_filename_message_triggers_fallback_and_rewrites_img_tag` (Task 6.2), using the
exact real message captured live (with `image.png` as the filename, matching the test's uploaded
file) -- asserts the fallback path (`_find_existing_attachment_id`'s lookup GET, then `POST
.../child/attachment/{id}/data`) now actually fires and the `<img>` tag IS rewritten to
`<ac:image><ri:attachment .../></ac:image>`, with `failed_images` empty, reproducing exactly the bug
this phase fixes. Updated docstrings/comments (Task 6.3) on `_looks_like_duplicate_filename_response`,
`_upload_attachment`, `_find_existing_attachment_id`, and the module's own header docstring to record
which REST API shapes are now confirmed against a real instance (attachment-create, `<ac:image>`
rewrite, and the fallback `.../child/attachment/{id}/data` data-update endpoint -- the last one
specifically via Phase 6's post-completion investigation, which called it directly with a hardcoded
attachment id) versus what remains unconfirmed (the filename-lookup GET
`_find_existing_attachment_id` itself uses, `GET .../child/attachment?filename=...`, which was not
separately exercised live). Re-ran the full quality gate (Task 6.4): `ruff format --check`/`ruff
check`/`vulture` clean; full `unittest` suite green, 2789 tests (up from 2788, the one new regression
test); `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/biz.dfch.specmgr.general.tools.confluence_update.md`
with no unexpected diff (only the docstring wording changes made above) and left `docs/MCP.md`/other
`docs/api/` pages unchanged (the tool's own `@mcp.tool()` description string was not modified). Added
a `CHANGELOG.md` clause to the existing `[Unreleased]` `confluence_update` bullet (amended, not a new
`### Fixed` entry, since this feature has not shipped in a release yet) documenting the confirmed real
400 message. Deliberately skipped Task 6.5 (optional live re-verification against the real test page)
-- see the Decisions Made entry below. Restored this document's frontmatter `status` from
`in-progress` back to `done`.
Next: none -- feature complete again.
Notes: this closes out the genuine implementation defect found post-completion; the ADR's chosen
design (best-effort upload with a duplicate-filename fallback) remains correct and unchanged -- only
the detection heuristic that decides *when* to use the fallback was fixed, plus its documentation.


#### 2026-09-02 00:00:00.000Z - Post-completion bug found: duplicate-filename detection doesn't match real Confluence message; Phase 6 added

Completed: after Phase 5 marked the feature `done`, a follow-up real-instance investigation
directly re-called `confluence_update("1232503612", <markdown referencing the same already-
attached feat-50-smoke-test.png>)` to answer a direct question about re-uploading a same-named
attachment. The real Confluence server rejected the create attempt with `400 Bad Request`,
`message: "Cannot add a new attachment with same file name as an existing attachment:
feat-50-smoke-test.png. Log referral number is <uuid>"`. `_looks_like_duplicate_filename_response()`
only checks for the substring `"already exist"`, which this real message does not contain, so the
fallback path (`_find_existing_attachment_id` -> `.../child/attachment/{id}/data`) was never
attempted; the `<img>` tag was left unrewritten and the failure recorded in `failed_images`
instead. A follow-up manual call directly to `POST .../child/attachment/1232699838/data` confirmed
the fallback *endpoint itself* is correctly shaped and works: HTTP 200, and the existing
attachment's own `version.number` incremented from `1` to `2` (confirming that re-uploading a
same-named attachment bumps only that attachment's own version, never creates a second attachment,
and is independent of the page's own version, which `confluence_update`'s `PUT` increments on
every call regardless of attachment outcome). The page body (left dangling by the failed test call)
was reverted again, confirmed byte-for-byte back to the original; page is now permanently at
`version 7`. Added Phase 6 (5 tasks) to the Task List to fix `_looks_like_duplicate_filename_response()`
against this real message, add a regression test for it, update documentation/Decisions Made, and
re-verify; reverted this document's frontmatter `status` from `done` back to `in-progress`.
Next: Phase 6 (fix the duplicate-filename detection heuristic).
Notes: this is a genuine implementation defect, not a design-level ADR issue -- the ADR's chosen
approach (best-effort upload with a duplicate-filename fallback) remains correct; only the
heuristic that decides *when* to use the fallback needs fixing.


#### 2026-09-01 23:00:00.000Z - Phase 5 complete: real smoke test + final verification (feature done)

Completed: performed the real, reversible smoke test against the dedicated Confluence test page (id `1232503612`, "fetch and update") required by Task 5.1/ACC-008, sourcing the real base URL/bearer token from a sibling project's `.env` (`SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER`, exported into this shell session only under the new `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` names, never written to any tracked file). Step-by-step evidence: (1) independently confirmed the starting page state via a raw `httpx.get` of `{base}/rest/api/content/1232503612?expand=version,title,body.storage` — `id=1232503612`, `title="fetch and update"`, `version.number=1`, `body.storage.value="<p>This is a page for testing.</p>"`, exactly as documented; (2) called `confluence_fetch` directly (imported from `biz.dfch.specmgr.general.tools.confluence_fetch`, no MCP protocol) against both confirmed real browsable URL shapes — `.../spaces/~fzpn/pages/1232503612/fetch+and+update` (Cloud-style) and `.../pages/editpage.action?pageId=1232503612` (Server-style) — both returned HTTP 200 JSON with `"id":"1232503612"`/`"title":"fetch and update"`, confirming live auto-conversion to `{base}/rest/api/content/1232503612?expand=body.storage` and no `ConfluenceAuthRedirectError`; (3) called `confluence_update("1232503612", <temp .md file>)` with throwaway content — returned `{"version": 2, "title": "fetch and update", "failed_images": []}`, independently `GET`-verified the new `body.storage.value` matched the rendered Markdown exactly (Confluence stripped `markdown-it`'s trailing `\n`, as anticipated); (4) reverted with a second temp Markdown file (`This is a page for testing.` -> `MarkdownIt("commonmark").render()` -> `<p>This is a page for testing.</p>\n`) — `confluence_update` returned `version: 3`, and an independent final `GET` confirmed `body.storage.value` is an EXACT, byte-for-byte match of the original `<p>This is a page for testing.</p>`; (5) **optional attachment path attempted**: uploaded a throwaway 1x1 PNG (`feat-50-smoke-test.png`) referenced from a temp Markdown file via `confluence_update` — the real `POST {base}/rest/api/content/1232503612/child/attachment` multipart call succeeded (HTTP 200, `version: 4`, `failed_images: []`), and an independent `GET` confirmed both the attachment now exists (`GET .../child/attachment` lists `feat-50-smoke-test.png`, id `1232699838`) and the page body was correctly rewritten to `<ac:image><ri:attachment ri:filename="feat-50-smoke-test.png" /></ac:image>`; the page was then reverted a second time (`version: 5`), independently `GET`-verified as an exact byte-for-byte match of the original body again. The duplicate-filename-fallback branch (uploading the SAME filename twice) was deliberately NOT attempted, per the phase instructions' explicit caution about leaving avoidable clutter behind. All temp scratch files lived under `/tmp/opencode/` and were deleted immediately after use; `git status --porcelain` was empty both before and after Task 5.1, confirming nothing untracked was left in the working tree. Then ran the full Task 5.2 quality gate: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py --min-confidence 60` clean, the full `unittest` suite (2788 tests) passes, `specmgr docs`/`specmgr mcp-docs` both produced zero `git status` diff (confirming Phase 4's regeneration was already current), and appended a feature-completion summary to `CHANGELOG.md`'s existing `[Unreleased]` section (a new `### Added` entry for `confluence_update`, expanding the existing `confluence_fetch` rename `### Changed` entry with its full auto-conversion/tiny-link/SSO-redirect/binary-download behavior), referencing GitHub issue #50 and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac. Checked off every remaining Task List item and every ACC-001..ACC-008 acceptance criterion (all now genuinely satisfied — see the Acceptance Criteria section above), and set this document's frontmatter `status` to `done`.

Permanent, accepted side effects of this real smoke test (explicitly NOT blockers, see Blockers above): the real page (id `1232503612`) now permanently shows `version 5` with four extra revisions in its edit history (Confluence's version number is monotonic and cannot itself be reverted via the REST API — only the CONTENT was restored, which is what "reversible" means for this smoke test), and it carries one permanent test attachment (`feat-50-smoke-test.png`, id `1232699838`, since this codebase has no attachment-delete tool).

Next: Feature complete, awaiting final orchestrator review and commit.
Notes: **ACC-008 verdict: PASS** (both `confluence_fetch` GET and `confluence_update`'s version-incrementing PUT succeeded live, reversibly, exactly as required). **REQ-001/002/004 verdict (as exercised live): PASS** — both browsable URL shapes auto-converted correctly and no SSO-redirect was hit (the earlier read-only exploration phase's documented SSO-redirect findings were for other browsable URL shapes/attachment-download endpoints, not these two REST-content-URL-converted GETs). **REQ-007/008 verdict (as exercised live): PASS** — `confluence_update` correctly reused the same two env vars and produced the exact documented GET-version/render/PUT-increment flow. **REQ-009 verdict (as exercised live, optional path): PASS** — the real attachment-create `POST .../child/attachment` multipart shape and the `<img>` -> `<ac:image>`/`<ri:attachment>` rewrite both worked exactly as implemented; the duplicate-filename-fallback branch (`_looks_like_duplicate_filename_response`/`_find_existing_attachment_id`/`.../child/attachment/{id}/data`) remains genuinely unverified against a real instance, since it was deliberately not attempted (see the Decisions Made entry below).


#### 2026-09-01 22:00:00.000Z - Phase 4 complete: attachment upload + image macro rewrite

Completed: extended `general/tools/confluence_update.py` (REQ-009/ACC-007) to insert a best-effort local-image attachment-upload/`<img>` -> `<ac:image>` rewrite step between rendering the Markdown file and the existing `PUT`. Local-image discovery scans the *rendered* HTML fragment's `<img src="...">` tags (a new `_IMG_TAG_PATTERN` regex), not the raw Markdown source, since `markdown-it` has already resolved the exact `src` values that also need to be found-and-replaced in the same fragment. A `src` is "local" if it contains no `://` (`_is_local_image_src`); a local `src` is resolved against `markdown_file_path`'s containing directory and, if the resulting path does not exist on disk, its `<img>` tag is silently left unrewritten with no upload attempted (REQ-009's explicit "best-effort"). For each local image that does exist, `_upload_attachment` `POST`s it to `{base}/rest/api/content/{id}/child/attachment` as `multipart/form-data` (field name `file`, real Confluence REST API shape) with the `X-Atlassian-Token: no-check` header (sent only on this and the fallback attachment call, never on the page GET/PUT); on a 400 response that looks like a duplicate-filename error (new `_looks_like_duplicate_filename_response` heuristic: status 400 plus a JSON `message` mentioning both "already exist" and "file"/"attachment"/"filename"), it falls back to `_find_existing_attachment_id` (a `GET .../child/attachment?filename=...` lookup) followed by a `POST .../child/attachment/{id}/data` with the new content. On success, the image's `<img>` tag is rewritten to `<ac:image><ri:attachment ri:filename="<basename>" /></ac:image>`; on ANY failure (missing file, non-2xx, network exception, unresolvable duplicate-filename fallback) the tag is left unrewritten, the failure is caught inside `_rewrite_local_images` (never propagates), and recorded as a `{"src": ..., "error": ...}` entry in a new `failed_images` list now always present in `confluence_update`'s return value (empty when nothing failed) -- this call sees this design decision as a deliberate deviation from purely "swallow-and-say-nothing" best-effort framing, since zero visibility into per-image failures would be a worse design. Added 8 new tests to `tests/general/tools/test_confluence_update.py` (24 tests total, up from 20): ACC-007 exactly (real temp Markdown + temp image file, mocked successful attachment POST, asserting the exact `<ac:image>`/`<ri:attachment>` rewrite and the POST's captured filename/bytes/headers), a missing-local-file case (no POST attempted, tag unrewritten, PUT still succeeds), a non-local `https://` image case (no POST attempted, tag unrewritten), the duplicate-filename fallback path (mocked 400 + lookup GET + fallback data POST, asserting the tag is still rewritten), an outright upload failure (mocked 500, tag unrewritten, `failed_images` populated), an `httpx` exception during upload (same assertions), and a mixed-multiple-images case (successful/missing/non-local in one call, each independently verified). Updated the existing Phase-3 ACC-006 test's expected return-value dict to include the now-always-present `failed_images: []` key. Updated `confluence_update`'s `@mcp.tool()` description/docstring, `general/tools/__init__.py`'s module docstring bullet, and `server.py`'s module docstring bullet to describe the new attachment-upload/image-rewrite behavior in full, removing the "not yet supported"/"a later phase, not yet implemented" language.
Next: Phase 5 (final phase — a real, reversible smoke test against the dedicated Confluence test page (id `1232503612`), plus final `specmgr docs`/`ruff`/`vulture`/`unittest` verification and the `CHANGELOG.md` entry).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2788 tests, up from 2781) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/biz.dfch.specmgr.general.tools.confluence_update.md`, `docs/api/biz.dfch.specmgr.general.tools.md`, `docs/api/biz.dfch.specmgr.server.md`, and `docs/MCP.md`'s `confluence_update` entry with no unexpected diffs. **Flagging explicitly for Phase 5 and the human relaying this to the user**: the real Confluence REST API shapes this phase implements -- the attachment-create `POST .../child/attachment` multipart shape is well-documented and implemented with reasonable confidence, but (a) the exact duplicate-filename 400 error-message wording `_looks_like_duplicate_filename_response` detects, (b) the existing-attachment lookup shape (`GET .../child/attachment?filename=...` and its `results[0].id` response shape) `_find_existing_attachment_id` assumes, and (c) the fallback binary-content-update shape (`POST .../child/attachment/{id}/data`) `_upload_attachment` uses, are ALL unverified against a real Confluence instance in this environment -- only mocked-`httpx` coverage exists for all three. Per the plan's own Task 5.1/ACC-008 wording, Phase 5's real smoke test is scoped narrowly to `confluence_fetch`'s REST content GET and `confluence_update`'s version-incrementing PUT against the dedicated test page, and may not exercise this attachment path (create, duplicate-fallback, or lookup) end-to-end at all.


#### 2026-09-01 20:00:00.000Z - Phase 3 complete: `confluence_update` core (no attachments yet)

Completed: implemented the new `general/tools/confluence_update.py` tool (`confluence_update(page_url_or_id: str, markdown_file_path: str) -> dict[str, Any]`, REQ-007/REQ-008/ACC-006): `page_url_or_id` (a bare numeric page id, a browsable `/pages/<id>/...`/`?pageId=<id>` URL, or an already-`/rest/api/content/<id>`-shaped REST URL) is resolved to a numeric page id via the new shared `_confluence_url.resolve_page_id()` helper (tries bare-numeric, then `extract_page_id`, then a new `/rest/api/content/(\d+)` pattern), with a `/x/<tinyid>` tiny link raising the same `ConfluenceTinyLinkNotSupportedError` `confluence_fetch` raises (imported, not redefined) and anything else unresolvable raising the new `ConfluencePageIdNotResolvedError`; `GET {base}/rest/api/content/{id}?expand=version,title` (deliberately no `body.storage` -- this phase never reads the existing body) reads `version.number`/`title`, with a new `ConfluenceUnexpectedResponseShapeError` raised instead of a raw `KeyError` if either key is missing; the Markdown file at `markdown_file_path` is read as UTF-8 (a missing file raises the natural `FileNotFoundError`, no wrapper) and rendered via a local `MarkdownIt("commonmark")` instance (confirmed to emit a bare fragment, no `<html>`/`<head>`/`<body>` wrapper); `PUT {base}/rest/api/content/{id}` writes `{"version": {"number": N+1}, "title": <unchanged>, "type": "page", "body": {"storage": {"value": <rendered fragment>, "representation": "storage"}}}`. Extracted the SSO-redirect-host check the ADR says is "reused for `confluence_update`'s internal GET/PUT" out of `confluence_fetch.py` into a new shared `_confluence_url.assert_same_host_as_base_url()` (plus its `ConfluenceAuthRedirectError`, which moved into `_confluence_url.py` too and is re-exported, unchanged, from `confluence_fetch.py` for backward compatibility) -- both the GET and the PUT apply this identical check. Added `tests/general/tools/test_confluence_update.py` (20 tests: the exact ACC-006 payload assertion computing the expected HTML via a fresh `MarkdownIt("commonmark").render(...)` call and asserting equality, shared-config reuse, all three page-id-resolution input shapes converging on the same GET/PUT target, tiny-link rejection with no HTTP call, GET- and PUT-redirect detection, all three missing-key GET-response-shape cases, non-2xx GET/PUT, and a missing Markdown file) plus 11 new tests in `tests/general/tools/test__confluence_url.py` for `resolve_page_id`/`assert_same_host_as_base_url`. Updated `general/tools/__init__.py`, `general/__init__.py`, and `server.py`'s module docstrings to register/describe the new tool.
Next: Phase 4 (attachment upload + image macro rewrite: local-image discovery, `POST .../child/attachment` upload with existing-filename fallback, and `<img>` -> `<ac:image>`/`<ri:attachment>` rewriting in `confluence_update`).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2781 tests) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/` (new `biz.dfch.specmgr.general.tools.confluence_update.md` page, updated `_confluence_url`/`confluence_fetch`/`general`/`general.tools`/`server` pages), `docs/GENERATED.md` (321 test files), and `docs/MCP.md` (94 tools, new `confluence_update` entry) with no unexpected diffs. `confluence_update`'s write flow (GET/PUT payload shape, version-increment) remains unverified against the real dedicated Confluence test page (id `1232503612`) -- only mocked-`httpx` coverage exists so far; the real, reversible smoke test is Phase 5's job.


#### 2026-09-01 00:00:00.000Z - Phase 2 complete: URL helper + `confluence_fetch` enhancements

Completed: added the new shared, `mcp`-free `general/tools/_confluence_url.py` helper (`extract_page_id` -- tries `[?&]pageId=(\d+)` then `/pages/(\d+)(?:/|$|\?)`, returning `None` for anything else including `/x/<tinyid>`; `build_rest_content_url` -- `f"{base_url.rstrip('/')}/rest/api/content/{page_id}"` plus an optional `?expand=`; `looks_like_rest_or_download_url` -- case-sensitive `/rest/api/`/`/download/` substring check; `looks_like_tiny_link` -- a small, dedicated `/x/<opaque-segment>` detector, not explicitly named in the plan's bullet list but required by REQ-003/ACC-002) with a fully-covered `tests/general/tools/test__confluence_url.py` (22 tests: Cloud-style/Server-style extraction including mid-query-string `&pageId=`, tiny-link/non-matching `None` cases, `build_rest_content_url` with/without `expand` and with/without a trailing base-URL slash, `looks_like_rest_or_download_url`/`looks_like_tiny_link` true/false cases). Wired all of this into `confluence_fetch` (REQ-001/002/003/004, ACC-001/002/003): the caller-supplied `url` is checked against the configured base URL first (unchanged from Phase 1), then a tiny link raises the new `ConfluenceTinyLinkNotSupportedError` with no HTTP call attempted, then a URL already shaped like a REST/download URL is used unchanged, then a URL with an extractable page id is rewritten to `{base}/rest/api/content/{id}?expand=body.storage`, and anything else falls through to a plain fetch of the URL as given (Phase-1 compatibility preserved); after the `httpx.get` call returns, the final `response.url.host` (case-folded) is compared against the configured base URL's host (also via `httpx.URL(base_url).host`, which normalizes casing) and a mismatch raises the new `ConfluenceAuthRedirectError` instead of returning/using that response. Added binary/image download support (REQ-005/ACC-004): `confluence_fetch`'s signature is now `confluence_fetch(url: str, destination_path: str | None = None) -> str`; a private `_is_text_content_type` helper classifies the response `Content-Type` (media-type prefix match against `text/`/`application/json`/`application/xml`, or suffix match against `+json`/`+xml`, both case-insensitive, ignoring any `;` parameters) -- text/JSON/XML responses are returned as `response.text` exactly as before (any given `destination_path` is silently ignored in this case, documented in the docstring); any other content type is written as raw bytes to `destination_path` (creating parent directories via `Path.mkdir(parents=True, exist_ok=True)`, mirroring how other tools use `pathlib.Path` directly rather than a shared write helper, since no existing shared "write bytes to path" helper exists in `general/tools/`) and the path itself is returned, or the new `ConfluenceDestinationPathRequiredError` is raised if `destination_path` was not given. Updated the `@mcp.tool()` description/docstring, `general/tools/__init__.py`'s module docstring, and `server.py`'s module docstring to describe the new behavior. Extended `tests/general/tools/test_confluence_fetch.py` (now 20 tests) with fully-mocked coverage for all of the above (a shared `_make_response()` test helper now sets `.headers`/`.url` on every mocked `httpx.Response` in addition to `.text`/`.content`/`.raise_for_status`) plus regression coverage confirming every Phase-1 behavior (base-URL matching case-insensitivity, missing-config errors, non-2xx raises, plain text returned as-is) still passes.
Next: Phase 3 (`confluence_update` core: `GET` version/title, render Markdown via `markdown-it-py`, `PUT` with incremented version -- no attachments yet).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2753 tests) passes; `specmgr docs`/`specmgr mcp-docs` regenerated `docs/api/` (new `biz.dfch.specmgr.general.tools._confluence_url.md` page, updated `confluence_fetch`/`general.tools`/`server` pages), `docs/GENERATED.md` (320 test files), and `docs/MCP.md` (`confluence_fetch`'s richer description and new `destination_path` parameter) with no unexpected diffs. Binary/image download support remains unverified against the one real customer instance with the confirmed oauth2-proxy limitation (documented in the feature's Decisions Made log and the ADR) -- only mocked-`httpx` coverage exists for it so far; the real, reversible smoke test is Phase 5's job.


#### 2026-09-01 00:00:00.000Z - Phase 1 complete: renamed `webfetch` to `confluence_fetch`

Completed: extracted the shared `general/tools/_confluence_config.py` helper (env var constants `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER`, `ConfluenceNotConfiguredError`, `confluence_config()`), moved out of the former `webfetch.py`; renamed `general/tools/webfetch.py` to `general/tools/confluence_fetch.py` (tool `confluence_fetch`, function `confluence_fetch(url) -> str`, `ConfluenceUrlNotAllowedError` staying local to this module since it is fetch-specific), reusing the shared `_confluence_config` helper instead of redefining env vars/exceptions locally; updated `general/tools/__init__.py`, `general/__init__.py`, and `server.py` module docstrings accordingly; renamed `tests/general/tools/test_webfetch.py` to `test_confluence_fetch.py` (class `TestConfluenceFetchTool`, all names/imports renamed, full existing coverage preserved) and added a new `tests/general/tools/test__confluence_config.py` for the extracted helper; updated `README.md`'s Environment Variables section and added a `[Unreleased]` `CHANGELOG.md` entry documenting the breaking rename; regenerated `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` via `specmgr docs`/`specmgr mcp-docs` (and manually removed the now-stale `docs/api/biz.dfch.specmgr.general.tools.webfetch.md`, which those generators do not prune automatically). No behavior changed -- this was a pure, mechanical rename; no URL auto-conversion, binary download, or `confluence_update` yet.
Next: Phase 2 (URL helper + `confluence_fetch` enhancements: `_confluence_url.py`, automatic REST URL construction, tiny-link rejection, SSO-redirect detection, binary/image download support).
Notes: quality gate green -- `ruff format --check`/`ruff check`/`vulture` clean, full `unittest` suite (2719 tests) passes with zero remaining `webfetch`/`Webfetch`/`WEBFETCH` references anywhere in `src/`/`tests/` (only the pre-existing historical `CHANGELOG.md` entry, `.specmgr/` artifacts, and `docs/adr/` content still mention the old name, as expected).


#### 2026-09-01 00:00:00.000Z - Feature and ADR created; exploration complete

Completed: read GitHub issue #50; discovered no "confluence skill" exists anywhere; explored a real Confluence Server/Data Center instance (hostname withheld; read-only GETs, real PAT from a sibling project's `.env`) and confirmed the URL-conversion algorithm, the SSO-redirect-only-on-non-`/rest/api/`-paths behavior, and that binary attachment download is blocked at the infrastructure layer; wrote ADR a156fdf9-052c-4f43-93a2-eeec04a91eac; created this feature document via `create_feat` and manually corrected its id from the tool-assigned `feat-37-...` to `feat-50-confluence`.
Next: Phase 1 (rename `webfetch` to `confluence_fetch`).
Notes: implementation has not started; this update only covers planning/design/exploration.
