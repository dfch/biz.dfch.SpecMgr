# `biz.dfch.specmgr.general.prompts.translate_artifact`

``@mcp.prompt()``: translate_artifact (feat-197-i18n, Phase 130, REQ-011).

Returns instructional text -- not itself a tool call -- that guides an LLM
through producing (or updating) a target-language variant of a specmgr
document from its source-language content. Translation is LLM judgment
work wrapped around deterministic tools that already exist, so this prompt
(plus the ``translate-artifact`` skill and the ``/translate`` command) is
the whole translation surface: there is no MCP tool that translates and
no dedicated subagent (the ``generate_uc_sequence_diagram`` /
``uc-diagram`` precedent, not the ``repair`` / ``doc-repairer`` one).

The narrated flow: read the ``specmgr://i18n`` resource first; check the
language pair; read the source via ``get_<d>(id, raw=True, language=...)``
(a ``ParseFailureResult`` stops the flow -- an English source is pointed to
``repair``); probe the target variant to decide **create**
(``create_<d>(content, language, id)``) versus **update** (the generic
``update``/``edit`` with ``language``); read the target language's heading
table and translate only free-form prose plus the fixed-text heading text
through that table, never the closed-vocabulary / schema-constant tokens
(REQ-010) nor -- per ADR 38efdb66 item 11 -- ``prb``'s ``problem_statement``
lead paragraph; write with bounded retries on the non-raising
``ValidateResult`` (a translated body cannot be dry-run: the generic
``validate`` tool is canonical-only and has no ``language`` parameter, so
the write tools' own validation is the feedback channel); verify with
``get_<d>(id, language=...)`` against the file on disk; and report. It
never commits, never writes English, and never changes a document's
frontmatter ``id``/``status``. A language without a heading table stops
the flow (the table file ``general/data/headings/<language>.json`` must be
added first -- never invented here).

``type`` is one of the twelve i18n-eligible domains (imported from
``general.tools._language_guard.LANGUAGE_AWARE_DOMAINS``, the single
source of truth); ``feat`` and ``adr`` are permanently English and
explicitly rejected. Like ``repair``, the prompt validates its arguments
up front and raises ``ValueError`` -- before any text is rendered.

This prompt is cross-cutting (it takes ``type`` + ``id`` + languages), so
-- like ``repair`` and ``compact_history`` -- it lives under
``general.prompts``. ``translate_artifact`` is a deliberate exception to
the ``<verb>_<domain>`` prompt-naming convention, following the bare-word
cross-cutting precedent of ``repair``.

The instructional text lives in its own packaged data file,
``general/data/general_translate_artifact_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$type``/``$id``/``$language``/
``$source_language``), not ``str.format``, so the packaged file is free to
use plain, unescaped ``{...}`` braces of its own.

## Functions

### `translate_artifact(type: 'str', id: 'str', language: 'str', source_language: 'str' = 'en') -> 'str'`

Return instructional text for translating the document ``id`` into ``language``.

Parameters
----------
type:
    The document domain to translate: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``,
    ``sysrs``, ``txt`` (matched case-insensitively). ``feat`` and ``adr``
    are permanently English and rejected with an actionable error; so is
    any other unknown value.
id:
    The shared id of the artifact (the EN source's id, which every
    language variant reuses).
language:
    The target language: an ISO 639-1-shaped lowercase two-letter code
    (``"de"``; matched case-insensitively) with a packaged heading
    table. ``"en"`` is rejected (English is the canonical source
    language and is never written by this flow), as is a code equal to
    ``source_language``.
source_language:
    The language to translate from; defaults to ``"en"``. A non-EN
    source needs a heading table too, and the EN document with the
    same id must still exist.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

Raises
------
ValueError
    ``type`` is ``feat``/``adr`` (always English) or unknown; ``id`` is
    blank/whitespace-only; ``language`` or ``source_language`` is not an
    ISO 639-1-shaped lowercase two-letter code or has no heading-mapping
    table; ``language`` is ``"en"``; or ``language`` equals
    ``source_language``.

