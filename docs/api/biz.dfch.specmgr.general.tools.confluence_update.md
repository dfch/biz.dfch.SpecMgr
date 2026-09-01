# `biz.dfch.specmgr.general.tools.confluence_update`

``@mcp.tool()`` wrapper: confluence_update (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac,
feat-50-confluence Phases 3-4, duplicate-filename detection fixed in Phase 6).

Writes a local Markdown file's content into an existing Confluence page's
body via the REST API, using the same Bearer/PAT authentication and the
same two environment variables :mod:`.confluence_fetch` already uses (see
:mod:`._confluence_config`). The full write flow (REQ-007/REQ-008/REQ-009,
ACC-006/ACC-007):

1. Resolve ``page_url_or_id`` to a numeric page id (see
   :func:`._confluence_url.resolve_page_id`) -- a bare id, a browsable page
   URL, or an already-REST-shaped URL are all accepted; a ``/x/<tinyid>``
   tiny link is rejected the same way :func:`.confluence_fetch.confluence_fetch`
   rejects it.
2. ``GET {base}/rest/api/content/{id}?expand=version,title`` to read the
   page's current ``version.number`` and ``title`` (``body.storage`` is not
   needed here, since this phase never reads the *existing* body).
3. Render the Markdown file at ``markdown_file_path`` to an HTML fragment
   via ``markdown_it.MarkdownIt("commonmark").render(...)``.
4. Best-effort local-image attachment upload and ``<img>`` -> ``<ac:image>``
   storage-format macro rewriting (REQ-009/ACC-007, Phase 4): every local
   image referenced by the rendered HTML (a ``src`` with no ``://`` scheme)
   that exists on disk is uploaded via
   ``POST {base}/rest/api/content/{id}/child/attachment`` (falling back to
   ``.../child/attachment/{attachment_id}/data`` if an attachment with the
   same filename already exists), and its ``<img>`` tag is rewritten to
   ``<ac:image><ri:attachment ri:filename="..." /></ac:image>`` on success.
   A missing local file or any upload failure leaves that specific ``<img>``
   tag unrewritten and never aborts the overall update -- see
   :func:`_rewrite_local_images` for the full best-effort contract. The
   attachment-create endpoint shape, the ``<ac:image>`` rewrite, and the
   fallback ``.../child/attachment/{attachment_id}/data`` endpoint shape are
   all now confirmed against a real Confluence instance (Phase 6, plus
   Phase 5's real smoke test); re-uploading an already-attached filename
   never creates a second attachment -- Confluence 400s the create attempt,
   and the fallback data-update endpoint bumps only that existing
   attachment's own ``version.number``, independent of the page's own
   version this module's ``PUT`` always increments regardless of attachment
   outcome. See :func:`_looks_like_duplicate_filename_response` for the
   real, confirmed duplicate-filename 400 error-message shape and the
   feature README's Decisions Made log for the full history.
5. ``PUT {base}/rest/api/content/{id}`` with the incremented version number,
   the unchanged title, and the (possibly image-macro-rewritten) rendered
   fragment as the new ``body.storage.value``.

## Classes

### `ConfluenceAttachmentLookupError`

The duplicate-filename fallback lookup could not find an existing attachment.

Raised internally by :func:`_find_existing_attachment_id` and always caught by
:func:`_rewrite_local_images`'s per-image ``try``/``except`` -- a lookup failure is just
another best-effort per-image failure (REQ-009), never propagated out of
:func:`confluence_update` itself.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `ConfluencePageIdNotResolvedError`

``page_url_or_id`` could not be resolved to a numeric Confluence page id.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `ConfluenceUnexpectedResponseShapeError`

A Confluence REST API response is missing an expected ``version``/``title`` key.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_find_existing_attachment_id(base_url: 'str', page_id: 'str', filename: 'str', headers: 'dict[str, str]') -> 'str'`

Look up the id of an existing attachment named ``filename`` on ``page_id``.

**Still unverified against a real instance as this specific lookup call**: this fallback
lookup (``GET {base}/rest/api/content/{id}/child/attachment?filename=...``) is documented
Confluence REST API behavior in general, and the sibling
``POST .../child/attachment/{attachment_id}/data`` call that consumes this lookup's result
IS now confirmed against a real instance (feat-50-confluence Phase 6, using a directly
hardcoded attachment id rather than this lookup's own output) -- but this specific
filename-lookup GET itself was not separately exercised live during that investigation. See
the feature README's Decisions Made log.

Parameters
----------
base_url:
    The configured Confluence base URL.
page_id:
    The numeric Confluence page id the attachment belongs to.
filename:
    The attachment's filename to look up.
headers:
    The ``Authorization`` header to reuse (no ``X-Atlassian-Token`` needed for a plain GET).

Returns
-------
str
    The existing attachment's id.

Raises
------
ConfluenceAttachmentLookupError
    If no attachment named ``filename`` is found, or the response shape is unexpected.
httpx.HTTPStatusError
    If the lookup GET response status code is not in the 2xx range.


### `_is_local_image_src(src: 'str') -> 'bool'`

Return whether ``src`` looks like a local filesystem path rather than an absolute URL.

Parameters
----------
src:
    An ``<img>`` tag's ``src`` attribute value, as rendered by ``markdown-it``.

Returns
-------
bool
    ``True`` if ``src`` contains no ``://`` scheme separator (i.e. it is a relative or
    absolute filesystem path, per the plan's Design Notes), ``False`` for an absolute URL
    such as ``https://...``.


### `_looks_like_duplicate_filename_response(response: 'httpx.Response', filename: 'str') -> 'bool'`

Best-effort heuristic: does ``response`` look like a "filename already exists" 400?

**Confirmed against a real Confluence Server/Data Center instance** (feat-50-confluence
Phase 6, see the feature README's Decisions Made log). Phase 4's original heuristic checked
exclusively for the substring "already exist", inferred from documented/community-reported
behavior; a real-instance follow-up test found the ACTUAL error message for this case is:

    "Cannot add a new attachment with same file name as an existing attachment:
    <filename>. Log referral number is <uuid>"

which does not contain "already exist" at all, so the original heuristic never matched it and
the fallback path silently never fired against a real server. The response is now treated as
a duplicate-filename 400 if the status code is 400 AND EITHER:

- the uploaded ``filename`` itself (case-insensitively) appears in the JSON body's
  ``message`` field -- the primary, more robust check: Confluence's real message always names
  the offending file, so this check survives future wording changes that the exact-phrase
  check above would not; or
- (secondary, kept for backward compatibility with community-reported message variants that
  do not repeat the filename) the ``message`` field mentions both "already exist" and one of
  "file"/"attachment"/"filename" (case-insensitively).

Any other 400 (or a non-JSON body) is treated as a genuine failure, not a duplicate-filename
case, so the fallback path is not attempted for it.

Parameters
----------
response:
    The response from the initial ``POST .../child/attachment`` create attempt.
filename:
    The filename that was uploaded, used for the primary "filename appears in the message"
    check.

Returns
-------
bool
    Whether ``response`` looks like a duplicate-filename 400.


### `_read_version_and_title(payload: 'dict[str, Any]') -> 'tuple[int, str]'`

Extract ``version.number`` and ``title`` from a GET response's JSON payload.

Parameters
----------
payload:
    The parsed JSON body of the ``GET {base}/rest/api/content/{id}``
    response.

Returns
-------
tuple[int, str]
    The ``(version_number, title)`` pair.

Raises
------
ConfluenceUnexpectedResponseShapeError
    If ``version``, ``version.number``, or ``title`` is missing, instead
    of letting a raw ``KeyError``/``TypeError`` propagate.


### `_resolve_page_id(page_url_or_id: 'str') -> 'str'`

Resolve ``page_url_or_id`` to a numeric page id, or raise a clear error.

Parameters
----------
page_url_or_id:
    A bare numeric page id, a browsable page URL, or a REST content URL.

Returns
-------
str
    The resolved numeric page id.

Raises
------
ConfluenceTinyLinkNotSupportedError
    If ``page_url_or_id`` is a ``/x/<tinyid>`` tiny link.
ConfluencePageIdNotResolvedError
    If ``page_url_or_id`` matches none of the accepted shapes.


### `_rewrite_local_images(html_fragment: 'str', markdown_file_path: 'str', base_url: 'str', page_id: 'str', headers: 'dict[str, str]') -> 'tuple[str, list[dict[str, str]]]'`

Upload every local image referenced by ``html_fragment`` and rewrite its ``<img>`` tag.

Local-image discovery scans the *rendered* HTML fragment's ``<img src="...">`` tags
(:data:`_IMG_TAG_PATTERN`) rather than the raw Markdown source: ``markdown-it`` has already
resolved the exact ``src`` values here, which are also exactly the strings that must be
found-and-replaced in this same fragment, so scanning the rendered output avoids a second,
separate regex over the Markdown source that could disagree with what was actually rendered.

For each ``<img>`` tag found:

- a ``src`` containing ``://`` (an absolute URL) is left unrewritten, no upload attempted;
- a local ``src`` resolved (relative to ``markdown_file_path``'s containing directory) to a
  path that does not exist on disk is left unrewritten, no upload attempted (REQ-009's
  "best-effort" -- a missing local image is silently skipped, not an error);
- a local ``src`` that exists on disk is uploaded via :func:`_upload_attachment`; on success
  its ``<img>`` tag is rewritten to
  ``<ac:image><ri:attachment ri:filename="..." /></ac:image>`` (just the basename, matching
  how Confluence names attachments -- not the full local path); on ANY failure (network
  error, non-2xx, unresolvable duplicate-filename fallback, ...) the tag is left unrewritten
  and the failure is recorded in the returned list.

A failed image upload never raises out of this function or aborts the overall page update --
every exception :func:`_upload_attachment` can raise is caught here.

Parameters
----------
html_fragment:
    The rendered HTML fragment to scan and (partially) rewrite.
markdown_file_path:
    The source Markdown file's path, used to resolve relative image paths against its
    containing directory.
base_url:
    The configured Confluence base URL.
page_id:
    The numeric Confluence page id images are attached to.
headers:
    The ``Authorization`` header to reuse for the attachment GET/POST calls.

Returns
-------
tuple[str, list[dict[str, str]]]
    The (possibly rewritten) HTML fragment, plus a list of
    ``{"src": <original src>, "error": <str(exception)>}`` entries for every image whose
    upload was attempted and failed -- surfaced to the caller rather than silently
    swallowed, so a caller can tell which images (if any) were not uploaded.


### `_upload_attachment(*, base_url: 'str', page_id: 'str', local_path: 'Path', headers: 'dict[str, str]') -> 'None'`

Upload ``local_path`` as an attachment on ``page_id``, best-effort.

``POST {base}/rest/api/content/{page_id}/child/attachment`` with the file as
``multipart/form-data`` (field name ``file``) -- the real, documented Confluence REST API
shape for attachment uploads. The ``X-Atlassian-Token: no-check`` header is required
specifically by this endpoint and is sent only here, never on the page GET/PUT calls this
module also makes.

If the create attempt fails with what looks like a duplicate-filename 400 (see
:func:`_looks_like_duplicate_filename_response`, fixed and confirmed against a real instance
in feat-50-confluence Phase 6), falls back to looking up the existing attachment's id
(:func:`_find_existing_attachment_id` -- this specific lookup GET itself remains unverified
against a real instance) and ``POST``\ ing the new content to
``.../child/attachment/{attachment_id}/data`` instead -- that data-update endpoint IS now
confirmed against a real instance (Phase 6): a real re-upload of an already-attached filename
returns HTTP 200 and bumps only that existing attachment's own ``version.number`` (never
creates a second attachment), independent of the page's own version (which this module's
``PUT`` always increments regardless of attachment outcome). See the feature README's
Decisions Made log for the full evidence and remaining caveat.

Parameters
----------
base_url:
    The configured Confluence base URL.
page_id:
    The numeric Confluence page id to attach ``local_path`` to.
local_path:
    The local image file to upload.
headers:
    The ``Authorization`` header to reuse; ``X-Atlassian-Token`` is added on top of this
    for the attachment calls specifically.

Raises
------
httpx.HTTPStatusError
    If the (possibly-fallback) upload response is not in the 2xx range.
ConfluenceAttachmentLookupError
    If the duplicate-filename fallback cannot find the existing attachment.
OSError
    If ``local_path`` cannot be read.


### `confluence_update(page_url_or_id: 'str', markdown_file_path: 'str') -> 'dict[str, Any]'`

Write ``markdown_file_path``'s rendered content into the Confluence page identified by ``page_url_or_id``.

Resolves ``page_url_or_id`` to a numeric page id, ``GET``\ s the page's
current ``version.number``/``title``, renders the Markdown file at
``markdown_file_path`` to an HTML fragment, best-effort uploads every
local image it references as a Confluence attachment and rewrites the
corresponding ``<img>`` tags into ``<ac:image>``/``<ri:attachment>``
macros (see :func:`_rewrite_local_images`), then ``PUT``\ s the
incremented version with that (possibly rewritten) fragment as the new
``body.storage.value``, leaving the title unchanged. Both the GET and
the PUT apply the same post-redirect host check
:func:`.confluence_fetch.confluence_fetch` applies, via
:func:`._confluence_url.assert_same_host_as_base_url`.

Parameters
----------
page_url_or_id:
    A bare numeric page id, a browsable Confluence page URL
    (Cloud-style ``/pages/<id>/<title>`` or Server-style
    ``?pageId=<id>``), or an already-``/rest/api/content/<id>``-shaped
    REST URL.
markdown_file_path:
    The local filesystem path to the Markdown file to render and push
    as the page's new body. Read as UTF-8 text; a missing file raises
    the natural ``FileNotFoundError`` -- no dedicated wrapper, since
    that built-in exception already names the offending path clearly.
    Any local image it references (relative to this file's containing
    directory) is a candidate for attachment upload/``<ac:image>``
    rewriting.

Returns
-------
dict[str, Any]
    ``{"id": <page id>, "title": <unchanged title>, "version": <new version number>,
    "failed_images": [{"src": ..., "error": ...}, ...]}`` -- a small, caller-useful summary
    rather than the raw PUT response JSON. ``failed_images`` is always present (an empty
    list when every referenced local image either did not need uploading or uploaded
    successfully), so a caller can tell which images, if any, were left unrewritten because
    their upload failed.

Raises
------
ConfluenceNotConfiguredError
    If either environment variable is unset or blank.
ConfluenceTinyLinkNotSupportedError
    If ``page_url_or_id`` is a ``/x/<tinyid>`` tiny link.
ConfluencePageIdNotResolvedError
    If ``page_url_or_id`` cannot be resolved to a page id.
ConfluenceAuthRedirectError
    If either the GET's or the PUT's final response URL host differs
    from the configured base URL's host.
ConfluenceUnexpectedResponseShapeError
    If the GET response JSON is missing ``version``/``version.number``/``title``.
FileNotFoundError
    If ``markdown_file_path`` does not exist.
httpx.HTTPStatusError
    If either the GET or the PUT response status code is not in the 2xx
    range. A failed attachment upload/rewrite does NOT raise this or
    any other exception -- see :func:`_rewrite_local_images`.

