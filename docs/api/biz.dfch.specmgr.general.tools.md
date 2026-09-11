# `biz.dfch.specmgr.general.tools`

MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the eleven
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; optional read-style body-line
``offset``/``limit`` coordinates -- ``offset`` = 1-based first line,
``limit`` = number of lines, omitted = through end of body, ``0`` = pure
insert, ``offset = N+1`` = the virtual end-of-body append position -- strict
validation, splice-then-validate-whole). ``set_status`` -- the generic,
cross-domain status change for all twelve document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/adr; ``superseded_by`` is
``adr``-only, composing the status as ``"superseded by {superseded_by}"``).
``set_classification`` -- the generic, cross-domain change of the free-text
``classification`` frontmatter field for the eleven whole-body document
types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr;
``adr`` is not supported), bumping ``updated`` and leaving the body and
every other frontmatter field untouched; a blank/whitespace-only value
clears ``classification`` back to ``None``/absent.
``delete`` -- the
generic, cross-domain hard-delete for the eleven whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
ten flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``validate`` -- the generic,
cross-domain, disk-free/id-free dry-run content validator for the twelve
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs; ``adr`` is not supported,
``validate_adr`` remains its own standalone tool); unlike every other
generic tool here, it never raises for a content-validation failure --
it always returns ``{valid: bool, errors: list[{message: str}]}``, only
raising ``ValueError`` for a ``full``/content-shape mismatch or an
unsupported ``type`` (feat-81-83-validation, ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6).
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
