# `biz.dfch.specmgr.general.tools.list_languages`

``@mcp.tool()`` wrapper: list_languages (feat-197-i18n Phase 140, Task 140.120, REQ-012, ACC-008).

The generic, read-only language-listing tool for one artifact: given a ``type`` (one of the twelve i18n-eligible
domains ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``vcr``/``sysrs``/``txt``) and an
``id``, it
reports the language codes the artifact currently exists in -- the dedicated tool ADR 38efdb66 item 7 names in place of
an "all languages" mode of ``list_<d>``. The result is a
:class:`~biz.dfch.specmgr.general.models.language_list_result.LanguageListResult`: ``languages`` (``"en"`` first when
the EN source exists -- ACC-008 -- then every other language that holds a variant, sorted by code) plus one entry per
language with its resolved path and a ``parseable`` flag (a variant that exists but fails to parse is listed, flagged,
with the parse error -- never dropped, never raised).

**Layout probing, not scanning.** The tool never uses or alters the EN-only scans of the other tools (REQ-013): it
probes the flat ``docs/{type}/`` directory and each shape-valid ``docs/{type}/{language}/`` subdirectory through the
domain's own language-aware readers (:mod:`._language_variants`). Only ``*.md`` documents participate: a non-``.md``
sibling (the ``.pdf`` next to a ``sysrs`` document) and a shape-invalid directory name (``Notes``, ``de-DE``) are
ignored. An id with variants but no EN source is reported as such (no ``"en"``); an id that exists in no language at
all raises the domain's own not-found error. Strictly read-only: it writes, creates, and invalidates nothing.

**Error semantics.** ``feat`` and ``adr`` are permanently English (REQ-002/REQ-009): they are rejected with the
permanent "always English" ``ValueError``, before the id is looked at; an unknown ``type``, a path-injection attempt, or
a wrong-format ``id`` is a ``ValueError`` before any filesystem access (``_path_safety.validate_id``).

## Functions

### `list_languages(type: 'WholeBodyOrAdrType', id: 'str') -> 'LanguageListResult'`

List the languages the artifact ``id`` of ``type`` currently exists in.

Parameters
----------
type:
    The document type: one of the twelve i18n-eligible domains ``req``, ``uc``, ``tsk``, ``qa``, ``prb``,
    ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``, ``sysrs``, ``txt``. ``feat`` and ``adr`` are accepted by the
    schema only so that they get an explanation: they are permanently English and are rejected.
id:
    The artifact's specmgr-assigned id (shared by every language variant).

Returns
-------
LanguageListResult
    ``languages`` (``"en"`` first when the EN source exists, then the other languages sorted by code) and one
    entry per language: ``language``, resolved ``path``, ``parseable``, and the parse ``error`` of an
    unparseable variant.

Raises
------
ValueError
    ``type`` is ``feat``/``adr`` (always English) or unknown, or ``id`` is a path-injection attempt or not in
    the domain's own format (raised before any filesystem access).
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError / PrbNotFoundError /
GolNotFoundError / RskNotFoundError / DecNotFoundError / SopNotFoundError / VcrNotFoundError /
SysrsNotFoundError
    The artifact exists in no language at all (neither the EN source nor any variant) -- the domain's own
    not-found error, as ``get_<d>`` raises it.

