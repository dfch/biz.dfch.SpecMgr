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
specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                        characteristics (and sub-characteristics), each with a description.

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
day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``set_status``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc``, ``list_uc``, ``get_uc_example``,
``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``
(stub, not yet implemented), ``validate_uc``.
Requirement tools (``req/tools/``): ``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``, ``delete_req``
(stub, not yet implemented), ``validate_req``.
Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk``, ``list_tsk``, ``get_tsk_example``,
``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``, ``delete_tsk``
(stub, not yet implemented), ``validate_tsk``.
QA tools (``qa/tools/``): ``parse_qa``, ``get_qa``, ``list_qa``, ``get_qa_example``,
``get_qa_template``, ``create_qa``, ``update_qa``, ``set_status_qa``, ``delete_qa``
(stub, not yet implemented), ``validate_qa``.
Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb``, ``list_prb``,
``get_prb_example``, ``get_prb_template``, ``create_prb``, ``update_prb``,
``set_status_prb``, ``delete_prb`` (stub, not yet implemented), ``validate_prb``.
Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol``, ``list_gol``,
``get_gol_example``, ``get_gol_template``, ``create_gol``, ``update_gol``,
``set_status_gol``, ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
preserving YAML frontmatter blocks; ``webfetch`` -- fetch a URL over HTTP GET with a
bearer token, restricted to a configured base URL (``SPECMGR_WEBFETCH_BASE_URL``,
``SPECMGR_WEBFETCH_BEARER``).

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
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
General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
``README.md`` into an optional sibling ``history.md``, per ADR
e369ee2e-3353-4f92-991c-6367d76d832e.

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, and later ``ac``) is a
top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
Add a new domain by
creating its top-level package and importing it at the bottom of this
module, next to the existing ``adr``/``general``/``gol``/``prb``/``qa``/``req``/``tsk``/``uc``
imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, and ``gol`` each
register ``tools``, ``resources``, and ``prompts``; ``general`` now also
registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
has no ``prompts`` sub-package yet.

## Functions

### `_lifespan(_server: 'MCPServer') -> 'AsyncGenerator[None, None]'`

Placeholder lifespan: no shared state to initialise yet.

