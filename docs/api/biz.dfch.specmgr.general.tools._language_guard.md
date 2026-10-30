# `biz.dfch.specmgr.general.tools._language_guard`

The write-side ``language`` guard shared by the generic, type-dispatched tools (feat-197-i18n Phase 120).

The generic ``update``/``edit``/``set_status``/``set_classification``/
``delete`` tools dispatch on ``type`` across every whole-body domain (and,
for ``set_status``, ``adr``), but the ``language`` parameter they all gained
in Phase 120 is honored by only a growing subset of those domains: in
Phase 120 just the pilot domain ``dec`` (:data:`LANGUAGE_AWARE_DOMAINS`;
Phase 125 extends the set to the remaining ten i18n-eligible domains).
:func:`guard_language` is the one up-front check every one of those tools
runs, before any filesystem access and before dispatch:

1. :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_language` --
   the shape guard (REQ-008/ACC-013), run for *every* ``type`` and every
   value, including the paths that end up rejecting the value anyway.
2. The default language (``"en"``) always passes: it is the byte-identical,
   flat, pre-i18n path for every domain.
3. A non-default language for a language-aware domain resolves its
   heading-mapping table (so a shape-valid code without a packaged table is
   an actionable ``ValueError`` before any filesystem access).
4. A non-default language for ``feat`` or ``adr`` is rejected with
   permanently-worded text (REQ-002/REQ-009: these two domains are always
   English); for every other, not-yet-enabled domain the rejection says
   the language is not yet supported (Phase 125 enables them).

## Functions

### `guard_language(type_: 'str', language: 'str') -> 'None'`

Validate ``language`` for the dispatched ``type_``, before any filesystem access.

Parameters
----------
type_:
    The dispatched document type (a whole-body domain, or ``adr`` for
    ``set_status``).
language:
    The caller-supplied ``language`` parameter.

Raises
------
ValueError
    ``language`` is not an ISO 639-1-shaped lowercase two-letter code
    (:func:`~biz.dfch.specmgr.general.tools._path_safety.assert_language`);
    a non-default ``language`` was given for ``feat``/``adr`` (always
    English -- permanent) or for a domain that does not yet support
    language variants (temporary, Phase 125); or a non-default
    ``language`` of a language-aware domain has no packaged
    heading-mapping table (the table loader's actionable error).

