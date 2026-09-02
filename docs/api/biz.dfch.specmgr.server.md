# `biz.dfch.specmgr.server`

MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

Registers the following resources and tools so far (plan §8, §9a):

Resources
---------
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/req_schema.json``) so it works from a
                        real, non-editable install.
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/uc_schema.json``) so it works from a
                        real, non-editable install.
specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
specmgr://uc/template -- A use-case template (every field present, placeholder text)
                          as raw markdown.
specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/tsk_schema.json``) so it works from a
                        real, non-editable install.
specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
specmgr://tsk/template -- A task list template (every field present, placeholder text)
                          as raw markdown.
specmgr://qa/schema --  The generated QA JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/qa_schema.json``) so it works from a
                        real, non-editable install.
specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
                        markdown.
specmgr://qa/template -- A question-and-answer template (every field present,
                          placeholder text) as raw markdown.
specmgr://prb/schema -- The generated PRB JSON Schema, read from a packaged data copy
                         (kept in sync with ``docs/prb_schema.json``) so it works from a
                         real, non-editable install.
specmgr://prb/example -- A complete, valid sample problem statement document as raw
                         markdown.
specmgr://prb/template -- A problem statement template (every field present,
                           placeholder text) as raw markdown.
specmgr://gol/schema -- The generated GOL JSON Schema, read from a packaged data copy
                         (kept in sync with ``docs/gol_schema.json``) so it works from a
                         real, non-editable install.
specmgr://gol/example -- A complete, valid sample goal document as raw markdown.
specmgr://gol/template -- A goal template (every field present,
                           placeholder text) as raw markdown.
specmgr://rsk/schema -- The generated RSK JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/rsk_schema.json``) so it works from a
                        real, non-editable install.
specmgr://rsk/example -- A complete, valid sample risk document as raw markdown.
specmgr://rsk/template -- A risk template (every field present, placeholder text)
                           as raw markdown.
specmgr://rsk/tara --     The TARA risk-response framework: what TARA is (Transfer,
                           Accept, Reduce, Avoid), the four valid `## Strategy` words,
                           and when and how to apply each -- raw markdown domain-knowledge
                           guidance.
specmgr://rsk/risk-matrix -- The 5x5 risk matrix: probability/impact scale anchors, the
                           zone table, and the product thresholds (what 'high risk' and
                           'low risk' mean) -- raw markdown domain-knowledge guidance.
specmgr://dec/schema -- The generated DEC JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/dec_schema.json``) so it works from a
                        real, non-editable install.
specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
specmgr://dec/template -- A decision template (every field present, placeholder text)
                          as raw markdown.
 specmgr://sop/schema -- The generated SOP JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/sop_schema.json``) so it works from a
                        real, non-editable install.
 specmgr://sop/example -- A complete, valid sample standard operating procedure document as
                         raw markdown.
 specmgr://sop/template -- A standard operating procedure template (every field present,
                          placeholder text) as raw markdown.
 specmgr://feat/schema -- The generated FEAT JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/feat_schema.json``) so it works from a
                        real, non-editable install.
 specmgr://feat/example -- A complete, valid sample feature document as raw markdown.
 specmgr://feat/template -- A feature template (every field present, placeholder text)
                          as raw markdown.
specmgr://vcr/schema -- The generated VCR JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/vcr_schema.json``) so it works from a
                        real, non-editable install.
specmgr://vcr/example -- A complete, valid sample verification case record document as
                        raw markdown.
specmgr://vcr/template -- A verification case record template (every field present,
                          placeholder text) as raw markdown.
specmgr://dtais --      The DTAIS verification-method vocabulary (Demonstration, Test,
                        Analysis, Inspection, Special), the five valid
                        ``### AC-NNN (Method): ...`` method words, and when and how to
                        apply each -- raw markdown domain-knowledge guidance.
specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                        characteristics (and sub-characteristics), each with a description.
specmgr://rasci --      The generic RASCI (Responsible/Accountable/Support/Consulted/
                        Informed) responsibility-assignment framework, as raw markdown.

REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
resource either -- id-based reads go through the ``get_tsk`` tool only, and
there never was such a resource to remove in the first place. QA has no
``specmgr://qa/{id}`` resource either, for the same reason -- id-based reads go
through the ``get_qa`` tool only. PRB has no ``specmgr://prb/{id}`` resource
either, for the same reason -- id-based reads go through the ``get_prb`` tool
only, and there is also no ``specmgr://prb/list`` resource -- ``list_prb``
ships as a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
GOL has no ``specmgr://gol/{id}`` resource either, for the same reason --
id-based reads go through the ``get_gol`` tool only, and there is also no
 ``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged tool from
 day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). RSK has no
 ``specmgr://rsk/{id}`` resource either, for the same reason -- id-based reads go
 through the ``get_rsk`` tool only, and there never was such a resource to
 remove in the first place. DEC has no
 ``specmgr://dec/{id}`` resource either, for the same reason -- id-based reads go
 through the ``get_dec`` tool only, and there is also no
 ``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged tool from
 day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). SOP has no
 ``specmgr://sop/{id}`` resource either, for the same reason -- id-based reads go
 through the ``get_sop`` tool only, and there is also no
 ``specmgr://sop/list`` resource -- ``list_sop`` ships as a paged tool from
 day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). FEAT has no
 ``specmgr://feat/{id}`` resource either, for the same reason -- id-based
 reads go through the ``get_feat`` tool only, and there is also no
 ``specmgr://feat/list`` resource either -- ``list_feat`` ships as a paged
 tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). VCR has no
 ``specmgr://vcr/{id}`` resource either, for the same reason -- id-based
 reads go through the ``get_vcr`` tool only, and there is also no
 ``specmgr://vcr/list`` resource either -- ``list_vcr`` ships as a paged
 tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_uc``,
``get_uc_example``,
``get_uc_template``, ``create_uc``, ``validate_uc``.
Requirement tools (``req/tools/``): ``parse_req``, ``get_req`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_req``,
``get_req_example``,
``get_req_template``, ``create_req``, ``validate_req``.
Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_tsk``,
``get_tsk_example``,
``get_tsk_template``, ``create_tsk``, ``validate_tsk``.
QA tools (``qa/tools/``): ``parse_qa``, ``get_qa`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_qa``,
``get_qa_example``,
``get_qa_template``, ``create_qa``, ``validate_qa``.
Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb`` (``raw=True`` returns
the frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_prb``,
``get_prb_example``, ``get_prb_template``, ``create_prb``,
``validate_prb``.
Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_gol``,
``get_gol_example``, ``get_gol_template``, ``create_gol``,
``validate_gol``.
 Risk tools (``rsk/tools/``): ``parse_rsk``, ``get_rsk`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_rsk``,
 ``get_rsk_example``,
 ``get_rsk_template``, ``create_rsk``, ``validate_rsk``.
   Decision tools (``dec/tools/``): ``parse_dec``, ``get_dec`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_dec``,
    ``get_dec_example``,
    ``get_dec_template``, ``create_dec``, ``validate_dec``.
    SOP tools (``sop/tools/``): ``parse_sop``, ``get_sop`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_sop``,
    ``get_sop_example``,
    ``get_sop_template``, ``create_sop``, ``validate_sop``. SOP is the first domain with NO
    per-domain ``update_sop``/``set_status_sop`` tools at all -- whole-body and line-range
    updates go through the generic ``update`` tool in ``general/tools/`` (``type="sop"``)
    and status changes through the generic ``set_status`` tool (``type="sop"``), per ADR
    36905d5b-8057-4294-8665-c7eed5534db0 (the dispatch-only convention every future domain
    follows). SOP relies on the cross-cutting ``specmgr://rasci`` resource (see the
    ``general`` resources paragraph above) for the generic RASCI role definitions used by
    its ``## Roles and Responsibilities`` section -- role definitions: see general
    ``specmgr://rasci``.
  Feature tools (``feat/tools/``): ``parse_feat``, ``get_feat`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping)), ``list_feat``,
  ``get_feat_example``,
  ``get_feat_template``, ``create_feat``, ``set_feat_id`` (renames an existing feature's
  ``feat-NNN-slug`` id: validates the new id's shape, refuses if the target folder already
  exists, renames the folder, rewrites the frontmatter ``id``/``updated``, leaves the body
  byte-identical), ``validate_feat``. Unlike every other domain here, ``feat``
  uses bespoke, folder-per-document addressing (``feat/tools/_paths.py``, not the shared
  ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
  its own -- it dispatches through the generic ``update``/``set_status`` tools below from
  day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), same as every other domain.
  Verification case record tools (``vcr/tools/``): ``parse_vcr``, ``get_vcr``
  (``raw=True`` returns the frontmatter-stripped body text verbatim instead of the
  parsed document, optionally windowed with read-style ``offset``/``limit``
  (raw-only, clamping)), ``list_vcr``, ``get_vcr_example``, ``get_vcr_template``,
  ``create_vcr``, ``validate_vcr``.
  General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
existing document's content across the eleven whole-body domains (``type`` is one of
 ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``;
 optional read-style
 ``offset``/``limit`` body-line coordinates -- ``offset`` = 1-based first line,
 ``limit`` = number of lines, omitted ``limit`` = through end of body, ``0`` =
 pure insert, ``offset = N+1`` = the virtual end-of-body append position;
 strict validation; the spliced result is validated as a whole document
 before anything is written); ``set_status`` --
replace an existing document's status across all twelve domains (``type`` is one of
``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``adr``),
also bumping
``updated`` (the eleven whole-body domains) and leaving the body untouched;
``superseded_by`` is ``adr``-only (it composes the status as
``"superseded by {superseded_by}"``);
``delete`` -- the generic type-dispatched hard-delete for the eleven
whole-body domains (``type`` is one of ``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``; ``adr`` is not supported),
resolves by ``id``, takes the domain lock, and returns the deleted path; a
``ValueError`` for injection/wrong-format ids before any file access, the
domain's ``XNotFoundError`` for missing documents, and a ``DeleteError`` for
I/O failures;
``confluence_fetch`` (renamed from ``webfetch``, ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac) -- fetch a URL over HTTP GET with a
bearer token, restricted to a configured base URL (``SPECMGR_CONFLUENCE_BASE_URL``,
``SPECMGR_CONFLUENCE_BEARER``); automatically converts a browsable Confluence
page URL (Cloud-style ``/pages/<id>/<title>`` or Server-style
``?pageId=<id>``) into ``{base}/rest/api/content/{id}?expand=body.storage``,
rejects ``/x/<tinyid>`` tiny links, raises on an SSO-redirect off the
configured base URL's host, and downloads non-text/binary content to an
optional ``destination_path`` instead of returning it as text.
``confluence_update`` (ADR a156fdf9-052c-4f43-93a2-eeec04a91eac,
feat-50-confluence Phases 3-4) -- write a local Markdown file's rendered HTML
into an existing Confluence page's body via the REST API: ``page_url_or_id``
(a bare page id, browsable page URL, or REST content URL; a ``/x/<tinyid>``
tiny link is rejected the same way ``confluence_fetch`` rejects it) is
resolved to a page id, its current ``version.number``/``title`` are read via
a ``GET``, ``markdown_file_path`` is rendered via ``markdown-it-py``, every
local image it references (a relative/absolute filesystem path, not an
``http(s)://`` URL) that exists on disk is best-effort uploaded as a
Confluence attachment (``POST .../child/attachment``, falling back to
``.../child/attachment/{id}/data`` if the filename already exists) with its
``<img>`` tag rewritten to ``<ac:image><ri:attachment ri:filename="..." />
</ac:image>`` on success (a missing file or a failed upload just leaves that
one ``<img>`` tag unrewritten), and the incremented version is written via a
``PUT`` with the (possibly rewritten) HTML fragment as the new
``body.storage.value`` and the title unchanged; reuses the same two
environment variables as ``confluence_fetch``, no new configuration surface.
  Path safety (feat-38-39-41-43-44 Phase 4, REQ-009, extending feat-36-delete's
``delete``-only guards, ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d): every one of the twelve
``get_<d>`` tools (including ``get_adr``), the generic ``update``, and the generic
``set_status`` now validate ``id`` via ``general.tools._path_safety.validate_id`` (no
``/``, no ``\``, no ``..``, plus the dispatched/fixed domain's own format --
canonical lowercase-hex UUID for the eleven UUID domains including ``adr``,
``feat-NNN-slug`` for ``feat``) before any filesystem access, raising ``ValueError``
before dispatch on a path-injection attempt or a wrong-format id, and additionally
confine the resolved path to the domain's own base directory with
``general.tools._path_safety.assert_within`` after id resolution (defense-in-depth).
``delete`` itself is unchanged by this phase.

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
§11).
Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
items, and uses the ``question`` tool to resolve ambiguity before proceeding.
QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
appends a fresh batch of unanswered interview questions (each with an empty
`_(awaiting response)_` placeholder) to an existing QA document, for
``Elicitation Context`` or one or more of the nine ISO/IEC 25010:2023 quality
characteristics.
Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
instructional text guiding an LLM through a ``TodoWrite`` + ``question``-tool-
driven 5W2H interview flow, including agent-synthesized ``Summary``/``Gap``
text.
Goal prompts (``gol/prompts/``): ``create_gol``, ``update_gol`` --
instructional text guiding an LLM through a ``TodoWrite`` +
``question``-tool-driven interview flow over the goal's mandatory
``statement``/``Source`` fields and its optional sections.
Risk prompts (``rsk/prompts/``): ``create_risk``, ``update_risk`` -- instructional
text guiding an LLM through the RSK tool sequence above.
Decision prompts (``dec/prompts/``): ``create_dec``, ``update_dec`` --
instructional text guiding an LLM through a ``TodoWrite`` +
``question``-tool-driven interview flow; ``create_dec`` first checks
``list_dec`` for a near-duplicate decision.
SOP prompts (``sop/prompts/``): ``create_sop``, ``update_sop`` --
instructional text guiding an LLM through a ``TodoWrite`` +
``question``-tool-driven interview flow over the SOP surface (the
``specmgr://sop/template``/``/example``/``/schema`` starting-point resources,
the ``specmgr://rasci`` read-first step before ``## Roles and Responsibilities``,
and the ``create_sop``/``validate_sop`` tool calls); ``create_sop`` first checks
``list_sop`` for a near-duplicate SOP. ``update_sop`` names the GENERIC
``update``/``set_status`` tools with ``type="sop"`` (both whole-body and line-range
via ``get_sop(id, raw=True)``) -- ``sop`` has no per-domain ``update_sop``/
``set_status_sop`` tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0).
Feature prompts (``feat/prompts/``): ``create_feat``, ``update_feat`` --
narrated instruction flows guiding an LLM through the FEAT tool sequence
above; ``create_feat`` first checks ``list_feat`` for a near-duplicate
feature.
Verification case record prompts (``vcr/prompts/``): ``create_vcr``,
``update_vcr`` -- narrated instruction flows guiding an LLM through the VCR
tool sequence above; ``create_vcr`` first checks ``list_vcr`` for a
near-duplicate verification case record.
General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
``README.md`` into an optional sibling ``history.md``, per ADR
e369ee2e-3353-4f92-991c-6367d76d832e; plus ``confluence_update``/
``confluence_fetch`` -- thin, single-tool-call prompts sharing their
respective tools' exact names (see the ``confluence_update``/``confluence_fetch``
tools above), each returning instructional text that tells the LLM to call
the matching tool with the given parameters, never calling it themselves
(feat-50-confluence Phase 8, REQ-012/REQ-013).

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``feat``, ``vcr``, and later ``ac``) is a
top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010``/``specmgr://dtais``
resources, the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
Add a new domain by
creating its top-level package and importing it at the bottom of this
module, next to the existing
``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``sop``/``tsk``/``uc``/``vcr``
imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``feat``, and ``vcr``
each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
has no ``prompts`` sub-package yet.

## Functions

### `_lifespan(_server: 'MCPServer') -> 'AsyncGenerator[None, None]'`

Placeholder lifespan: no shared state to initialise yet.

