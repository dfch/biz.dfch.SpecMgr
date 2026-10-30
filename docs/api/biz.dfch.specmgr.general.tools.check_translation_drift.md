# `biz.dfch.specmgr.general.tools.check_translation_drift`

``@mcp.tool()`` wrapper: check_translation_drift (feat-197-i18n Phase 140, Tasks 140.100/140.110, REQ-014, ACC-009).

The generic, read-only drift check between a translated language variant and its source document (the EN source by
default): one deterministic run reports BOTH drift kinds (ACC-009) in a single, structured,
non-raising :class:`~biz.dfch.specmgr.general.models.translation_drift.TranslationDriftResult`:

* **structural drift** (REQ-014a, Task 140.100) -- sections of the variant that are *missing*, *extra*, or
  *reordered* relative to the source's canonical schema. Both documents' *raw* body text is reduced to a heading
  skeleton (the same fence-aware heading recognizer the parse boundary uses), each heading is mapped back to canonical
  English through the document language's heading table, and the free text of the data-carrying headings
  (``Option N: <title>``, ``Step N: <title>``, ``Extension N<l>. <title>``, ``AC-NNN (Method): <text>``) is dropped so
  only the schema-constant token is compared; timestamp-led update entries are change-log rows and are not compared.
  See :mod:`~biz.dfch.specmgr.general.models.translation_drift` for the full rule. A document that fails to parse at
  all is reported as an ``unparseable`` structural finding carrying the parse error (byte-identical to the domain's
  ``list_<d>`` failed-row ``error``), never swallowed and never raised;
* **staleness** (REQ-014b, Task 140.110) -- the source's frontmatter ``updated`` timestamp is strictly newer than the
  variant's. Compared as parsed offset-aware datetimes (not strings), so the ``T``/space separators and any UTC offset
  compare correctly; equal or older is not stale; a missing/unparseable timestamp is reported in ``staleness_error``.

Drift is about structure and staleness, never about wording or translation quality: prose, list items, frontmatter
values and ``prb``'s regex-locked English ``problem_statement`` lead paragraph (ADR 38efdb66 item 11) are invisible
to it. The tool is strictly read-only: it writes, creates, and invalidates nothing.

**Languages.** ``language`` is the variant (always non-EN: ``"en"`` is the canonical source form, never a translation
target -- the ``translate_artifact`` prompt's own rule); ``source_language`` (default ``"en"``) may be any language
with a heading table, since both sides are resolved the same way. Both are shape-guarded and table-probed before any
filesystem access (``_language_guard.guard_language``); ``language == source_language`` is a ``ValueError``.

**Error semantics.** ``feat``/``adr`` are rejected with the permanent "always English" ``ValueError`` (before the id is
looked at); an unknown ``type``, a path-injection/wrong-format ``id`` or ``language``/``source_language``, a table-less
language, ``language='en'`` and equal languages are ``ValueError``s before any filesystem access. A source or variant
document that does not exist at all raises the domain's own not-found error (naming the missing language); one that
exists but fails to parse is a finding in the result, never an exception.

## Functions

### `_locate_or_explain(type_: 'str', id_: 'str', language: 'str', role: 'str') -> 'Location'`

Locate one side of the comparison; a truly absent document raises the domain's not-found error, named.


### `_read_side(location: 'Location') -> 'tuple[list[SkeletonEntry] | None, object, DriftFinding | None]'`

Read one document's heading skeleton and raw ``updated`` value, plus its ``unparseable`` finding if any.

The skeleton and the timestamp are read from the raw on-disk text (frontmatter split, body mdformat-normalized
exactly as the parser does), independent of whether the document parses -- a document whose frontmatter cannot
be split yields ``(None, None, ...)`` for them (its parse error is already carried by the finding).


### `check_translation_drift(type: 'WholeBodyOrAdrType', id: 'str', language: 'str', source_language: 'str' = 'en') -> 'TranslationDriftResult'`

Check a translated variant for structural drift and staleness against its source.

Parameters
----------
type:
    The document type: one of the eleven i18n-eligible domains ``req``, ``uc``, ``tsk``, ``qa``, ``prb``,
    ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``, ``sysrs`` (``feat``/``adr`` are permanently English and
    rejected).
id:
    The artifact's specmgr-assigned id (shared by both languages).
language:
    The translated variant's language: an ISO 639-1-shaped lowercase two-letter code with a packaged heading
    table, never ``"en"``.
source_language:
    The language the variant is compared against (default ``"en"``); any language with a heading table, and
    different from ``language``.

Returns
-------
TranslationDriftResult
    ``structural`` (the ``missing``/``extra``/``reordered``/``unparseable`` findings), ``stale`` with both
    ``updated`` timestamps and the signed delta (``staleness_error`` when not comparable), the two resolved
    paths, and ``in_sync`` (no structural finding, not stale, staleness determined).

Raises
------
ValueError
    ``type`` is ``feat``/``adr`` (always English) or unknown; ``id`` is a path-injection attempt or not in the
    domain's own format; ``language``/``source_language`` is not a two-letter lowercase code or has no packaged
    heading table; ``language`` is ``"en"``; or ``language == source_language`` (all raised before any
    filesystem access).
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError / PrbNotFoundError /
GolNotFoundError / RskNotFoundError / DecNotFoundError / SopNotFoundError / VcrNotFoundError /
SysrsNotFoundError
    The source or the variant document does not exist at all (the domain's own not-found error, naming the
    missing side); a document that exists but fails to parse is an ``unparseable`` finding instead.

