# `biz.dfch.specmgr.general.tools`

MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; optional read-style body-line
``offset``/``limit`` coordinates -- ``offset`` = 1-based first line,
``limit`` = number of lines, omitted = through end of body, ``0`` = pure
insert, ``offset = N+1`` = the virtual end-of-body append position -- strict
validation, splice-then-validate-whole). ``set_status`` -- the generic,
cross-domain status change for all document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/adr; ``superseded_by`` is
``adr``-only, composing the status as ``"superseded by {superseded_by}"``).
``set_classification`` -- the generic, cross-domain change of the free-text
``classification`` frontmatter field for the whole-body document
types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs;
``adr`` is not supported), bumping ``updated`` and leaving the body and
every other frontmatter field untouched; a blank/whitespace-only value
clears ``classification`` back to ``None``/absent.
``delete`` -- the
generic, cross-domain hard-delete for the whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``validate`` -- the generic,
cross-domain, disk-free/id-free dry-run content validator for the
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; ``adr`` is not supported,
``validate_adr`` remains its own standalone tool); unlike every other
generic tool here, it never raises for a content-validation failure --
it always returns ``{valid: bool, errors: list[{message: str}]}``, only
raising ``ValueError`` for a ``full``/content-shape mismatch or an
unsupported ``type`` (feat-81-83-validation, ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6).
``find_related`` -- find the documents most semantically related to an
existing document, given its ``type``/``id``, across every whole-body
domain (``adr`` excluded structurally), ranked by cosine similarity of
local sentence embeddings (the ``similarity`` extra), excluding the
source document itself (feat-134-related-artifact-similarity, ADR
750842b2-aca4-4649-ba0c-855ec8e1f505). ``find_similar_text`` -- find the
documents most semantically similar to a free-form ``query`` text (the
pre-creation dedup/discovery companion of ``find_related``). Both return
ranked ``{type, id, title, status, path, score}`` hit rows (an
unparseable candidate appears with ``id = None`` and the ``<failed to
parse>`` marker title/status), and both return the structured,
non-raising ``{available: false, reason, message}`` result whenever the
embedding feature is unavailable (``SPECMGR_SIMILARITY_DISABLED`` present
or the backend/model failed to load) -- the tools always register,
availability is decided at call time (REQ-003).
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
