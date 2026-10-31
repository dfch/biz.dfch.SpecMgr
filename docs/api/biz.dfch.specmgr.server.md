# `biz.dfch.specmgr.server`

MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

The server singleton is a ``SpecMgrServer`` (defined below) -- a thin
``mcp.server.MCPServer`` subclass, not a plain ``MCPServer``: since ``mcp``
v2.1.0 (upstream #3314) a tool handler's raised exception reaches the client
wrapped as ``UnexpectedToolError("Error executing tool <name>")`` with the
handler's own message swallowed, and this repo's documented tool contract is
that the still-raising usage errors (the ``_path_safety`` invalid-id
``ValueError``s, the whole-body domains' ``XNotFoundError``s,
``create_feat``'s ``FileExistsError``, ...) surface to the caller as that
message text. ``SpecMgrServer`` overrides only the public ``call_tool`` to
re-raise ``UnexpectedToolError.__cause__`` (the original exception,
``from None`` -- no doubled exception chain in the server log), which the
SDK's own ``_handle_call_tool`` catch then stringifies into the
``is_error=True`` result it returns -- the v2.0.0 wire shape minus the
``Error executing tool <name>: `` prefix, uniform for every registered tool,
no per-domain logic (feat-221-mcp-220-error-contract, Phase 100, REQ-002).

Registers the following resources and tools so far:

Resources
---------
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package, plus the
                        installed ``fastembed`` package version (the ``similarity`` extra's
                        embedding backend) or null when that extra is not installed -- read via
                        ``importlib.metadata``, never an import of ``fastembed`` itself (feat-134
                        Phase 7, REQ-014).
specmgr://adr/{id} --    Full ADR document for a given id (ADR 7531106b-074b-4bd8-a83a-e433d01676e2).
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
specmgr://uc/template -- A use-case template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/plantuml -- The frozen UC -> PlantUML mapping and validation rulebook: the
                         per-UC usecase and package diagram mapping, the sequence-skeleton
                         attribution rule + UNATTRIBUTED marker grammar, the strict
                         3-source validation chain, the jar/bin + URL invocation contracts,
                         the two-mode structure checker, and the user-owned platform-adapter
                         snippets -- raw markdown domain-knowledge guidance (feat-185-
                         uc-diagrams Phase 100).
specmgr://uc/plantuml-template -- The packaged PlantUML sequence-skeleton template (placeholder
                         participants + mapping comments, rulebook §2.9) as raw PlantUML
                         source: not markdown, not a specmgr document (no frontmatter, not
                         validate-able) -- text/plain (feat-185-uc-diagrams Phase 120).
specmgr://uc/plantuml-example -- The complete, fully attributed sequence diagram for the
                         packaged "Buy Goods" example UC as raw PlantUML source: not
                         markdown, not a specmgr document (no frontmatter, not
                         validate-able) -- text/plain; the model for the
                         generate_uc_sequence_diagram prompt flow (feat-185-uc-diagrams
                         Phase 120).
specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
specmgr://tsk/template -- A task list template (every field present, placeholder text)
                          as raw markdown.
specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
                        markdown.
specmgr://qa/template -- A question-and-answer template (every field present,
                          placeholder text) as raw markdown.
specmgr://prb/example -- A complete, valid sample problem statement document as raw
                         markdown.
specmgr://prb/template -- A problem statement template (every field present,
                           placeholder text) as raw markdown.
specmgr://gol/example -- A complete, valid sample goal document as raw markdown.
specmgr://gol/template -- A goal template (every field present,
                           placeholder text) as raw markdown.
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
specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
specmgr://dec/template -- A decision template (every field present, placeholder text)
                          as raw markdown.
 specmgr://sop/example -- A complete, valid sample standard operating procedure document as
                         raw markdown.
 specmgr://sop/template -- A standard operating procedure template (every field present,
                          placeholder text) as raw markdown.
 specmgr://feat/example -- A complete, valid sample feature document as raw markdown.
 specmgr://feat/template -- A feature template (every field present, placeholder text)
                          as raw markdown.
specmgr://vcr/example -- A complete, valid sample verification case record document as
                        raw markdown.
specmgr://vcr/template -- A verification case record template (every field present,
                          placeholder text) as raw markdown.
specmgr://sysrs/example -- A complete, valid sample system requirements specification
                         document as raw markdown.
specmgr://sysrs/template -- A system requirements specification template (every field
                           present, placeholder text) as raw markdown.
specmgr://txt/example -- A complete, valid sample free-form text document as raw
                         markdown.
specmgr://txt/template -- A free-form text template (every field present,
                          placeholder text) as raw markdown.
specmgr://dtais --      The DTAIS verification-method vocabulary (Demonstration, Test,
                        Analysis, Inspection, Special), the five valid
                        ``### AC-NNN (Method): ...`` method words, and when and how to
                        apply each -- raw markdown domain-knowledge guidance.
specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                        characteristics (and sub-characteristics), each with a description.
specmgr://rasci --      The generic RASCI (Responsible/Accountable/Support/Consulted/
                        Informed) responsibility-assignment framework, as raw markdown.
specmgr://ears --       The EARS (Easy Approach to Requirements Syntax) five
                        requirement-phrasing templates (Ubiquitous requirements,
                        Event-driven requirements, Unwanted behaviours, State-driven
                        requirements, Optional features) and when to use each -- raw
                        markdown domain-knowledge guidance.
specmgr://reference-graph -- The frozen reference-graph rulebook: the deterministic
                              PlantUML component-diagram emission layout for the
                              cross-reference network (the 15-entry palette, the bracketed
                              alias/label/truncation rules, the title override + defaults,
                             the FEAT-exclusion rule, the bare-`feat-NNN` source-id
                             rejection with the `list_feat` discovery pointer, the SCC
                             cycle rule + red-arrow syntax, the construction semantics,
                             the CLI file layout) plus the pointer at the UC rulebook
                             §3–§6 for the validation chain reused as-is -- raw markdown
                             domain-knowledge guidance (feat-207-reference-graph Phase 100).
specmgr://i18n --       How language variants of the same artifact are stored and
                        translated (feat-197-i18n Phase 130): the ``docs/{type}/{language}/``
                        layout and the EN-slug basename rule, the language vocabulary and
                        per-language heading tables, the tool surface honoring ``language``,
                        the exact never-translate list per domain (closed-vocabulary and
                        schema-constant tokens, the ``prb`` ``problem_statement``
                        exemption), how to translate headings, the create-versus-update
                        decision, and the guard/error semantics (``feat``/``adr`` are always
                        English) -- raw markdown domain-knowledge guidance.
specmgr://i18n/headings/{language} -- (resource template, feat-197-i18n Phase 130) A
                        language's heading-mapping table as JSON text (``application/json``):
                        a flat object mapping each translated heading text to its canonical
                        English heading text, obtained via the heading-table loader (same
                        validation as every parse). ``language`` is shape-guarded first;
                        ``en`` (canonical, no table) and a language without a packaged table
                        are an actionable ``ValueError``. Read-only; lets the
                        ``translate_artifact`` flow read the table without a host file tool.
specmgr://config --     For every document domain (adr, req, uc, tsk, qa, prb, gol,
                         rsk, dec, sop, feat, vcr, sysrs, txt), the resolved absolute base directory and
                        whether the domain's ``SPECMGR_*_DIR`` environment variable is
                        explicitly set (feat-51-mcp-cwd REQ-001) -- lets a client
                        self-diagnose a CWD/env-var misconfiguration without shell access to
                        the server's host. Never discloses the value of any environment
                        variable, only whether the relevant directory-path env var is present
                        (REQ-002). Plus a static ``similarity`` section for the
                        semantic-similarity feature (feat-134 Phase 7, REQ-013): whether the
                        ``similarity`` extra (``fastembed``) is installed (a spec lookup, never
                        an import), whether the presence-based
                        ``SPECMGR_SIMILARITY_DISABLED`` opt-out flag is set, the fixed model
                        name (the shared ``SIMILARITY_MODEL_NAME`` constant, the single source
                        both ``get_default_provider()`` and the section read), and the resolved
                        model cache directory (``FASTEMBED_CACHE_PATH`` if set, else
                        ``<tempdir>/fastembed_cache`` -- reported, never created). Plus a
                        static ``plantuml`` section for the PlantUML validation source
                        (feat-185-uc-diagrams Phase 120): the presence-only state of the
                        exactly-three source env vars (SPECMGR_PLANTUML_JAR/
                        SPECMGR_PLANTUML_BIN/SPECMGR_PLANTUML_URL, each {set: bool}, never
                        a value) plus ``selected`` -- the first-set-wins selection over
                        them ("jar"/"bin"/"url"/"none"). Plus a static ``diagram`` section
                        for the reference-graph label limit (feat-207-reference-graph Phase
                        120, REQ-010): the presence-only state of
                        ``SPECMGR_DIAGRAM_MAX_TITLE`` ({set: bool}, never a value), the
                        helper's validity flag ({valid: bool}), the frozen default (40), and
                        ``resolved`` -- a derived value, the effective label limit the
                        ``get_reference_diagram``/``get_reference_diagram_all`` tools render
                        with (40 when unset or set-but-invalid, the set int otherwise). Plus
                        whether the presence-based
                        ``SPECMGR_FEAT_WARMUP_DISABLED`` opt-out flag is set (the unified
                        startup warmup's ``feat`` frontmatter/full-parse phases,
                        feat-187-list-feat-timeout, Task 110.120). Static configuration
                        only: the tools' own dynamic runtime availability is their
                        structured ``{available, reason, message}`` result, not part of
                        this resource (no ``loaded`` field).

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
 tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). SYSRS has no
 ``specmgr://sysrs/{id}`` resource either, for the same reason -- id-based
 reads go through the ``get_sysrs`` tool only, and there is also no
 ``specmgr://sysrs/list`` resource either -- ``list_sysrs`` ships as a
 paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). TXT
 has no ``specmgr://txt/{id}`` resource either, for the same reason --
 id-based reads go through the ``get_txt`` tool only, and there is also no
 ``specmgr://txt/list`` resource either -- ``list_txt`` ships as a paged
 tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_uc``,
``get_uc_example``,
``get_uc_template``, ``get_uc_schema``, ``create_uc``, and the read-only diagram surface
(feat-185-uc-diagrams Phase 120, thin over the Phase 110
``uc.models.v2.renderer`` + the import-free ``plantuml`` package):
``get_uc_diagram`` (the per-UC usecase diagram by id),
``get_uc_sequence_skeleton`` (the deterministic sequence skeleton by id;
UNATTRIBUTED markers for the messages the attribution rule cannot pre-fill)
-- both ``_path_safety``-guarded and cache-aware, an existing-but-broken
document returning the non-raising ``ParseFailureResult`` per the feat-150
precedent --, and ``get_use_case_package_diagram`` (the multi-UC package diagram;
``ids=None`` = every UC in ``list_uc`` order, delegated to the ``list_uc``
tool; an id missing on disk or existing-but-broken becomes a skipped slot
whose references take the deterministic unresolvable-note path -- the render
never fails on an id; a wrong-format id is a ``ValueError`` before any file
access), ``validate_plantuml`` (the strict validation chain over diagram
text: structure pre-flight always, then the single first-set-wins source
-- no fall-through -- or the all-unset structure-only floor; non-raising
§3.6 ``PlantumlValidationResult``), ``get_uc_plantuml_template``/
``get_uc_plantuml_example`` (the packaged PlantUML-source template/example,
verbatim), and ``plantuml_encode`` (the classic ``SoWkI…``-form URL text
encoding -- the ``{enc}`` payload of ``GET {base}/svg/{enc}``; the tool takes
no base URL, so it returns the encoding itself; fully offline).
Requirement tools (``req/tools/``): ``parse_req``, ``get_req`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_req``,
``get_req_example``,
``get_req_template``, ``get_req_schema``, ``create_req``.
Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_tsk``,
``get_tsk_example``,
``get_tsk_template``, ``get_tsk_schema``, ``create_tsk``.
QA tools (``qa/tools/``): ``parse_qa``, ``get_qa`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_qa``,
``get_qa_example``,
``get_qa_template``, ``get_qa_schema``, ``create_qa``.
Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb`` (``raw=True`` returns
the frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_prb``,
``get_prb_example``, ``get_prb_template``, ``get_prb_schema``, ``create_prb``.
Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_gol``,
``get_gol_example``, ``get_gol_template``, ``get_gol_schema``, ``create_gol``.
 Risk tools (``rsk/tools/``): ``parse_rsk``, ``get_rsk`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_rsk``,
 ``get_rsk_example``,
 ``get_rsk_template``, ``get_rsk_schema``, ``create_rsk``.
    Decision tools (``dec/tools/``): ``parse_dec`` (takes no ``language`` parameter -- it
derives the file's language from its path position relative to the decision base
directory: flat ``docs/dec/`` = canonical/no table, a direct two-letter
``docs/dec/{language}/`` subdirectory = that language's packaged heading-mapping
table), ``get_dec`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``; the optional ``language`` parameter
(feat-197-i18n Phase 110, default ``"en"``) selects the variant to read --
omitted/``"en"`` = the flat ``docs/dec/`` document exactly as before, any other
ISO 639-1-shaped lowercase two-letter code = that language's variant at
``docs/dec/{language}/`` (shape-guarded before any file access like ``id``, and a
shape-valid code without a heading-mapping table is rejected up front); ``raw=True``
returns the variant's body verbatim, ``raw=False`` parses it through the variant's
table so the model holds canonical heading text), ``list_dec`` (the same optional
``language`` parameter, default ``"en"`` -- omitted/``"en"`` scans the flat
directory exactly as before, any other code scans only that language's
subdirectory, listing exactly the existing variants of that language; deliberately
no "all languages" mode -- the row shape is unchanged, no language column),
    ``get_dec_example``,
    ``get_dec_template``, ``get_dec_schema``, ``create_dec`` (optional ``language``
(default ``"en"``) and ``id`` parameters, feat-197-i18n Phase 120: omitted/``"en"``
= a new flat ``docs/dec/`` document with a fresh server-assigned id exactly as
before, ``id`` then must be omitted; a non-default ``language`` creates a
TRANSLATION of an existing decision instead -- ``id``, the shared id of the EN
source document, is then required (a missing one, or one given for the default
language, is a ``ValueError`` before any file access), the EN source must exist
(``DecNotFoundError`` otherwise), the variant is written to
``docs/dec/{language}/`` under the EN source's exact file name with the shared id
as its frontmatter ``id`` (``status`` draft), its body is validated through the
language's heading-mapping table and persisted verbatim, and an existing variant of
that id and language is never overwritten (``FileExistsError``)).
     SOP tools (``sop/tools/``): ``parse_sop``, ``get_sop`` (``raw=True`` returns the
frontmatter-stripped body text verbatim instead of the parsed document, optionally
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_sop``,
    ``get_sop_example``,
    ``get_sop_template``, ``get_sop_schema``, ``create_sop``. SOP is the first domain with NO
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
windowed with read-style ``offset``/``limit`` (raw-only, clamping), and, with
``numbered=True`` (raw-only; ``ValueError`` with ``raw=False``, like
``offset``/``limit``), prefixes every returned body line with its 1-based absolute
body-line number in the ``"<n>: "`` form -- a windowed numbered read numbers from
the clamped offset and never restarts, so a number seen can be fed straight back
into the generic ``update`` tool's ``offset``)), ``list_feat``,
  ``get_feat_example``,
  ``get_feat_template``, ``get_feat_schema``, ``create_feat``, ``set_feat_id`` (renames an existing feature's
  ``feat-NNN-slug`` id: validates the new id's shape, refuses if the target folder already
  exists, renames the folder, rewrites the frontmatter ``id``/``updated``, leaves the body
  byte-identical). Unlike every other domain here, ``feat``
  uses bespoke, folder-per-document addressing (``feat/tools/_paths.py``, not the shared
  ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
  its own -- it dispatches through the generic ``update``/``set_status`` tools below from
  day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), same as every other domain.
  Verification case record tools (``vcr/tools/``): ``parse_vcr``, ``get_vcr``
  (``raw=True`` returns the frontmatter-stripped body text verbatim instead of the
  parsed document, optionally windowed with read-style ``offset``/``limit``
  (raw-only, clamping), and, with ``numbered=True`` (raw-only; ``ValueError`` with
  ``raw=False``, like ``offset``/``limit``), prefixes every returned body line with
  its 1-based absolute body-line number in the ``"<n>: "`` form -- a windowed
  numbered read numbers from the clamped offset and never restarts, so a number
  seen can be fed straight back into the generic ``update`` tool's
  ``offset``)), ``list_vcr``, ``get_vcr_example``, ``get_vcr_schema``, ``get_vcr_template``,
  ``create_vcr``.
  System Requirements Specification tools (``sysrs/tools/``): ``parse_sysrs``,
  ``get_sysrs`` (``raw=True`` returns the frontmatter-stripped body text verbatim
  instead of the parsed document, optionally windowed with read-style
  ``offset``/``limit`` (raw-only, clamping), and, with ``numbered=True`` (raw-only;
  ``ValueError`` with ``raw=False``, like ``offset``/``limit``), prefixes every
  returned body line with its 1-based absolute body-line number in the
  ``"<n>: "`` form -- a windowed numbered read numbers from the clamped offset and
  never restarts, so a number seen can be fed straight back into the generic
  ``update`` tool's ``offset``)), ``list_sysrs``, ``get_sysrs_example``,
  ``get_sysrs_schema``, ``get_sysrs_template``, ``create_sysrs``. ``sysrs`` is an
  aggregator domain tying together already-existing artifacts (``gol``, ``prb``,
  ``qa``, ``uc``, ``req``, ``rsk``, ``dec``/``adr``, ``vcr``) via per-section
  type-tagged cross-reference lists, and is built dispatch-only from day one (ADR
  36905d5b-8057-4294-8665-c7eed5534db0) like ``sop``/``vcr`` -- no per-domain
  ``update_sysrs``/``set_status_sysrs`` tools of its own; deletion goes through the
  generic ``delete`` tool (``type="sysrs"``).
  Free-form text tools (``txt/tools/``): ``parse_txt``, ``get_txt``
  (``raw=True`` returns the frontmatter-stripped body text verbatim instead of the
  parsed document, optionally windowed with read-style ``offset``/``limit``
  (raw-only, clamping), and, with ``numbered=True`` (raw-only; ``ValueError`` with
  ``raw=False``, like ``offset``/``limit``), prefixes every returned body line with
  its 1-based absolute body-line number in the ``"<n>: "`` form -- a windowed
  numbered read numbers from the clamped offset and never restarts, so a number
  seen can be fed straight back into the generic ``update`` tool's
  ``offset``)), ``list_txt``, ``get_txt_example``, ``get_txt_schema``,
  ``get_txt_template``, ``create_txt``. ``txt`` is the generic, minimally
  structured catch-all domain (a mandatory free-form body plus a mandatory
  newest-first ``## Updates`` log; everything between the H1 and ``## Updates`` is
  opaque to the parser) and is built dispatch-only from day one (ADR
  36905d5b-8057-4294-8665-c7eed5534db0) like ``sop``/``vcr``/``sysrs`` -- no
  per-domain ``update_txt``/``set_status_txt``/``validate_txt``/``delete_txt``
  tools of its own: whole-body and line-range updates go through the generic
  ``update`` tool (``type="txt"``), surgical edits through the generic ``edit``
  tool (``type="txt"``), status changes through the generic ``set_status`` tool
  (``type="txt"``), classification changes through the generic
  ``set_classification`` tool (``type="txt"``), deletions through the generic
  ``delete`` tool (``type="txt"``), and dry-run content validation through the
  generic ``validate`` tool (``type="txt"``). A ``TXT <uuid>`` reference is both a
  reference source and a reference target (the shared tag vocabulary, feat-229-txt),
  and the reference-graph palette's 15th entry colours a TXT node ``LightGrey``.
  Language variants, every i18n-eligible domain (feat-197-i18n Phases 110/120/125): the
``get_<d>``/``list_<d>`` tools take an optional ``language`` parameter (default ``"en"``)
and the ``create_<d>`` tools an optional ``language`` plus ``id`` (the shared id of the
EN source, required for a non-default language and forbidden for ``"en"``) for all
twelve domains ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``vcr``/``sysrs``/``txt`` -- exactly the behavior documented for ``get_dec``/``list_dec``/
``create_dec`` above (flat ``docs/<type>/`` for ``"en"``, ``docs/<type>/{language}/``
under the EN source's exact file name for any other code, shape-guarded before any file
access, single language per ``list_<d>`` call, a new variant's ``status`` is the
domain's own create status: ``draft``, ``open`` for ``rsk``); every ``parse_<d>`` tool
derives the language from its path position; ``prb``'s ``problem_statement`` lead
paragraph is exempt from translation (the one regex-locked English field, it stays the
canonical English template sentence in every language). ``feat`` (always English) and
``adr`` take no ``language`` parameter.
  General tools (``general/tools/``) -- language variants (feat-197-i18n Phases 120/125):
the generic ``update``/``edit``/``set_status``/``set_classification``/``delete``
tools each take an optional ``language`` parameter (default ``"en"``, appended
last). Omitted/``"en"`` dispatches exactly as before. A non-default
ISO 639-1-shaped lowercase two-letter code acts on that language's variant file
ONLY (``docs/<type>/{language}/``, located by id-scan; the EN file's bytes,
``updated`` timestamp, and cache entry stay untouched, and a variant's content is
validated through the language's heading-mapping table) -- honored by every
whole-body domain except ``feat``; ``feat``/``adr`` raise a ``ValueError`` for a
non-default language before any file access (those documents are always English),
as does a malformed ``language`` or one without a packaged table. The generic
``validate`` tool takes no ``language`` parameter (EN/canonical content only).
General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
existing document's content across the whole-body domains (``type`` is one of
  ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``;
  optional read-style
  ``offset``/``limit`` body-line coordinates -- ``offset`` = 1-based first line,
  ``limit`` = number of lines, omitted ``limit`` = through end of body, ``0`` =
  pure insert, ``offset = N+1`` = the virtual end-of-body append position;
   ``offset``/``limit`` address the frontmatter-stripped body, never the raw
   on-disk ``.md`` file -- the YAML frontmatter block is variable-length, so a
   raw file read's line numbers are never the same as body-line coordinates
   (the only safe source of coordinates is a ``get_<d>(id, raw=True)`` read,
   never a raw file read minus an assumed constant), and a
   ``get_<d>(raw=True, numbered=True)`` read's numbered output must never be
   fed back verbatim into ``content`` (strip the ``"<n>: "`` prefix from each
   line first); strict validation; the spliced result is validated as a whole
   document before anything is written; on success returns an
   ``UpdateResult``: ``frontmatter`` (the updated frontmatter only, no body)
   plus ``snippet`` -- in range mode, the before/after window of the touched
   range (dropped lines numbered pre-splice, inserted lines numbered
   post-splice, up to 2 unchanged context lines per side), bounded by the
   touched range rather than the document size; ``snippet`` is ``None`` in
   whole-body mode and for the whole-body-equivalent range (``offset=1`` with
   ``limit`` omitted) (feat-153-off-by-n, GitHub issue #153, ADR
   19ff316b-cd11-41a7-a616-ffd84917da51));
  ``edit`` (feat-159-edit, GitHub issue #159) -- surgical, exact-match string
  replacement of an existing document's frontmatter-stripped body across the
  whole-body domains (``type`` is one of
  ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``;
  ``adr`` is not supported -- an explicit pre-dispatch ``ValueError``, unlike
  ``update``'s inherited ``KeyError``, following the generic ``validate`` tool's
  precedent, ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6); ``old_str`` must match
  the on-disk body byte-exactly (no line-ending normalization -- an
  ``old_str`` containing a ``\n`` will not match a CRLF body -- no BOM
  handling, no fuzzy/regex fallback) and must be unique unless ``replace_all``
  rewrites every exact occurrence; the edit is 2-fold: then the *edited* body
  must still validate as a whole document, and the document is written to disk
  only if both stages pass, and nothing is written on any failure (the file
  stays byte-unchanged); an empty ``new_str`` is a pure deletion, legal iff
  the edited body validates; returns the updated frontmatter only (no body;
  ``updated`` bumped), with an invalid ``id`` a ``ValueError`` before any file
  access; ``set_status`` --
replace an existing document's status across every domain (``type`` is one of
``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``/``adr``),
also bumping
``updated`` (the whole-body domains) and leaving the body untouched;
``superseded_by`` is ``adr``-only (it composes the status as
``"superseded by {superseded_by}"``);
``set_classification`` -- replace the free-text ``classification``
frontmatter field of an existing document across the whole-body
domains (``type`` is one of
``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``;
``adr`` is not supported), also bumping ``updated`` and leaving the body
and every other frontmatter field untouched; a blank/whitespace-only value
clears ``classification`` back to ``None``/absent; no ``create_<d>`` tool
accepts a ``classification`` argument at all -- this is the sole
classification-change entry point;
``delete`` -- the generic type-dispatched hard-delete for the
whole-body domains (``type`` is one of ``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``; ``adr`` is not supported),
resolves by ``id``, takes the domain lock, and returns the deleted path; a
``ValueError`` for injection/wrong-format ids before any file access, the
domain's ``XNotFoundError`` for missing documents, and a ``DeleteError`` for
I/O failures;
``validate`` (feat-81-83-validation, ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6) --
the generic, disk-free/id-free dry-run content validator for the
whole-body domains (``type`` is one of
``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``;
``adr`` is not supported -- use ``validate_adr`` instead), replacing the
former per-domain ``validate_<d>`` tools; it is the one generic tool
above whose entire surface is non-raising structured results: it never
raises for a content-validation failure -- it always returns
``{valid: bool, errors: list[{message: str}]}`` (``errors`` empty when
``valid`` is ``True``), only raising ``ValueError`` for a ``full``/
content-shape mismatch or an unsupported ``type`` (the four generic
mutation tools' non-raising branches, above, cover
content-validation and existing-document-parse-failure only -- their
caller-usage errors still raise);
``find_related`` -- find the documents most semantically related to an
existing document, given its ``type``/``id``, across every whole-body domain
(``type`` is one of ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/
``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``; ``adr`` is excluded structurally),
ranked by cosine similarity of local sentence embeddings (the ``similarity``
extra, ``fastembed``/``bge-small``), excluding the source document itself;
``find_similar_text`` -- the same ranking for a free-form ``query`` text (the
pre-creation dedup/discovery companion of ``find_related``). Both return up
to ``top_k`` (default 10, validated 1..100) ranked ``{type, id, title,
status, path, score}`` hit rows (an unparseable candidate appears with
``id = null`` and the ``<failed to parse>`` marker title/status), and both
return the structured, non-raising ``{available: false, reason, message}``
result whenever the embedding feature is unavailable (the
``SPECMGR_SIMILARITY_DISABLED`` flag present, or the backend/model fails to
load) -- the tools always register; availability is decided at call time
(feat-134-related-artifact-similarity, ADR
750842b2-aca4-4649-ba0c-855ec8e1f505);
``list_references`` (feat-144-ref-artifact, GitHub issue #144) -- the
generic, cross-domain cross-reference listing tool: takes a *source*
document's ``type`` (one of
``adr``/``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``)
and its ``id``, scans the source's frontmatter-stripped body for
``<TYPE> <id>`` references (the shared reference-tag vocabulary
``GOL``/``PRB``/``QA``/``UC``/``REQ``/``RSK``/``DEC``/``ADR``/``VCR``/``SYSRS``/``TXT``/
``FEAT``: case-insensitive tag, one or more space/tab/dash separators,
anywhere in a line; the UUID tags carry a canonical uuid id, while
``FEAT`` carries the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
number), dedupes repeated occurrences of the same reference
(first-occurrence order preserved), and resolves each unique reference in
its target domain (the target domains' own cache-backed ``load_by_id``;
``adr`` excluded from the cache, ADR bfd76370-b59b-4d65-b550-a969f6c93c9d),
returning a paged ``PagedResult[ReferenceRow]`` -- one row per unique
reference carrying ``type``/``id``/``title`` (the referenced document's
H1, re-derived from the resolved document)/``path`` (the referenced
document's resolved absolute file path); a reference that cannot be
resolved on disk is a row with null ``title``/``path`` and the target
domain's not-found message in ``error`` -- it never raises;
``max_results``/``offset`` control paging with the same clamp-not-error
contract as every ``list_*`` tool (default page size 25, capped at 100).
It applies the same ``_path_safety`` guards: an invalid source
``type``/``id`` (unknown type, path-injection attempt, or wrong-format
id) is a ``ValueError`` before any filesystem access, and a source
document that does not exist on disk raises the source domain's own
``XNotFoundError`` (identical to ``get_<d>``);
``get_reference_diagram`` (feat-207-reference-graph, Phase 120, REQ-004)
-- the read-only, id-based reference-diagram tool: takes a *source*
document's ``type`` (one of
``adr``/``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``)
and its ``id``, plus ``depth`` (1..5, default 1, the forward BFS depth),
``reverse`` (additive, direct-only on the incoming side), ``include_feat``
(the FEAT exclusion, applied last), and an optional ``title`` override;
renders the source document's reference neighbourhood as the deterministic
PlantUML component diagram of the frozen ``specmgr://reference-graph``
rulebook (one node per artifact -- label = the document title, truncated
to ``SPECMGR_DIAGRAM_MAX_TITLE``, default 40 -- a stereotype + colour per
type, per-domain curly-brace component groups, one label-free edge per
unique reference, on-cycle edges red, dangling targets top-level
``<<UNRESOLVED>>`` nodes), returning the
byte-stable PlantUML source. Guard order: ``id`` (for ``type="feat"`` the
full ``feat-NNN-slug`` only -- a bare ``feat-NNN`` is a wrong-format id,
not a normalization candidate; use ``list_feat`` to discover the exact
id) and ``depth`` are both a ``ValueError`` before any filesystem access;
a missing source raises the source domain's own ``XNotFoundError``
(identical to ``get_<d>``); an existing-but-broken source returns the
non-raising ``ParseFailureResult`` (``error``/``path``/``id``, the
``error`` text byte-identical to the domain's ``list_<d>`` failed-row
``error`` for the same file (ADR 9080b37c) for the 13 whole-body domains --
time-qualified by ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 for ``feat``
(``get_feat`` the unconditional full-fidelity authority), and the leg-read
``AdrParseError``'s own text for ``adr`` (whose ``list_adr`` carries no
failed row: broken ADRs are skipped));
``get_reference_diagram_all`` (feat-207-reference-graph, Phase 120,
REQ-005) -- the read-only, registry-wide reference-diagram tool: the same
deterministic PlantUML component diagram over every parseable document of
all 14 domains (broken documents are skipped -- the render never fails for
content), with the ``include_feat`` switch (the FEAT exclusion, applied
last) and an optional ``title`` override (default: ``Reference Graph``;
the diagram title is sanitized but never truncated, the node labels are
truncated to ``SPECMGR_DIAGRAM_MAX_TITLE``, default 40);
``list_languages`` (feat-197-i18n Phase 140, Task 140.120, REQ-012, ACC-008) --
the read-only language-listing tool: takes a ``type`` (one of the eleven
i18n-eligible domains ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``vcr``/``sysrs``;
``feat`` and ``adr`` are permanently English and rejected with the "always
English" ``ValueError``, before the id is looked at) and an ``id``, and returns a
``LanguageListResult``: ``languages`` -- ``"en"`` first when the EN source exists
(never invented: an id with variants but no EN source lists no ``"en"``), then
every other language holding a variant sorted by code -- plus one entry per
language (resolved ``path``, ``parseable``, and the parse ``error`` of a variant
that exists but fails to parse, byte-identical to the domain's ``list_<d>``
failed-row ``error``). It probes the flat ``docs/{type}/`` directory and each
shape-valid ``docs/{type}/{language}/`` subdirectory through the domains' own
language-aware readers -- never through, and never altering, the EN-only scans
of the other tools (REQ-013); only ``*.md`` documents participate. A
path-injection/wrong-format ``id`` is a ``ValueError`` before any filesystem
access; an id that exists in no language raises the domain's own
``XNotFoundError``. Strictly read-only (writes, creates and invalidates
nothing);
``check_translation_drift`` (feat-197-i18n Phase 140, Tasks 140.100/140.110,
REQ-014, ACC-009) -- the read-only drift check between a translated variant
(``language``, never ``"en"``) and its source (``source_language``, default
``"en"``, any language with a heading table): one non-raising
``TranslationDriftResult`` reports BOTH drift kinds. STRUCTURAL: both documents'
raw body text is reduced to a heading skeleton (the parse boundary's own
fence-aware heading recognizer), each heading is mapped back to canonical English
through the document language's heading table, the free text of the data-carrying
headings (``Option N:``, ``Step N:``, ``Extension N.``, ``AC-NNN (Method):``) is
dropped so only the schema-constant token is compared, and timestamp-led update
entries (change-log rows) are not compared; each ``missing``/``extra``/
``reordered`` section is a finding (canonical ``heading``, ``path``, ``level``,
positions), and a document that fails to parse is an ``unparseable`` finding
carrying the parse error -- never swallowed, never raised. STALENESS: ``stale``
is true iff the source's frontmatter ``updated`` is strictly newer than the
variant's, compared as offset-aware datetimes (``T``/space separators and UTC
offsets compare correctly; equal is not stale), with both timestamps, the signed
``source_ahead_by_seconds`` and a ``staleness_error`` for a missing/unparseable
timestamp. ``in_sync`` is true iff there is no structural finding, the variant is
not stale and staleness could be determined. Wording, prose, frontmatter values
and ``prb``'s English ``problem_statement`` are never compared. Guards before any
filesystem access: ``feat``/``adr`` (always English), unknown ``type``,
path-injection/wrong-format ``id``, a malformed or table-less ``language``/
``source_language``, ``language="en"``, and equal languages are ``ValueError``s;
a truly absent source or variant raises the domain's own ``XNotFoundError``
(naming the missing side). Strictly read-only; no tool translates (translating is
the ``translate_artifact`` prompt).
Path safety (feat-38-39-41-43-44 Phase 4, REQ-009, extending feat-36-delete's
``delete``-only guards, ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d): every one of the
``get_<d>`` tools (including ``get_adr``), the generic ``update``, the generic
``edit``, and the generic ``set_status`` now validate ``id`` via ``general.tools._path_safety.validate_id`` (no
``/``, no ``\``, no ``..``, plus the dispatched/fixed domain's own format --
canonical lowercase-hex UUID for every domain other than ``feat``, including ``adr``,
``feat-NNN-slug`` for ``feat``) before any filesystem access, raising ``ValueError``
before dispatch on a path-injection attempt or a wrong-format id, and additionally
confine the resolved path to the domain's own base directory with
``general.tools._path_safety.assert_within`` after id resolution (defense-in-depth).
``delete`` itself is unchanged by this phase.
Parse-failure error channel (feat-150-mcp-lifecycle-commands Phase 1a, ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c): every ``get_<d>`` tool for the 13
whole-body domains (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``/``txt``; ``get_adr`` excluded) additionally returns a
structured, non-raising ``ParseFailureResult`` (``error``/``path``/``id``) for a
document that exists but fails to parse, instead of raising the domain's
not-found error -- the ``error`` text is byte-identical to that
domain's ``list_<d>`` tool's failed-row ``error`` for the same file (identical
field path and cause, including the trailing pydantic documentation line --
feat-162-doc-cache-exception-footer, GitHub issue #162) for every domain
EXCEPT ``feat``, where this byte-identity is time-qualified
(feat-187-list-feat-timeout, ADR 3982712a-a46b-4b2b-809f-9c6925a49b44):
``get_feat`` always fully parses and remains the unconditional,
full-fidelity authority, but ``list_feat``'s own row may carry a
transiently-healthy or dirty-stage-specific ``error`` instead until its
background warmup (or an on-demand ``get_feat`` read) has fully parsed
that file, or permanently under ``SPECMGR_FEAT_WARMUP_DISABLED`` (see
``feat.tools.list_feat``'s own docstring for the full three-tier
contract). ``raw=True`` on a broken
document still returns the result (never a raw ``str``); a healthy document's
shape and every other ``get_<d>`` outcome are unchanged. This is the third
extension of the ADR 519d1206 client-side-``isError``-truncation workaround
chain after ``validate`` and ``set_status``'s invalid-status case. A fourth
extension (feat-170-update-edit-parse-failure, GitHub issue #170, ADR
b8c9bfea-6dcf-4158-bfc5-4ec17abb842f) adds the same non-raising
``ParseFailureResult`` to the generic ``update``/``edit``/``set_status``/
``set_classification`` tools for an existing-but-broken target document
(the per-domain adapters catch the ``load_by_id`` failure, probe the same
parse-failure lookup, and return the result -- a truly-absent id still
raises the domain's not-found error), and ``update``/``edit`` additionally
return the non-raising ``ValidateResult`` for a content-validation failure
on the submitted new content / post-edit result instead of raising
``AssertionError``/``pydantic.ValidationError`` (the single
``errors[].message`` capped at 300 chars as ``validate`` caps it, feat-110;
every caller-usage ``ValueError`` still raises, and
``set_status``'s own ``InvalidStatusResult`` check still runs
pre-lock/pre-load first). A fifth extension (feat-204-create-error,
GitHub issue #204, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e) adds the
non-raising ``ValidateResult`` to every ``create_<d>`` tool (a
content-validation failure of the caller-submitted body; nothing written)
and every ``parse_<d>`` tool (an existing file that fails to parse);
``parse_<d>``'s ``OSError``-family file-access errors from
``Path.read_text()`` and every caller-usage ``ValueError``/``FileExistsError``
(``create_feat``'s id guards keep their existing execution order -- a
compound failure returns ``ValidateResult`` first) still raise; the shared
catch tuple and 300-char cap constant are defined in
``general/models/validate_result.py`` and re-exported by
``general/tools/validate.py``.

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (ADR
ddd038f0-ae16-4f4b-beef-df06f7ed226f).
Use-case prompts (``uc/prompts/``): ``create_uc``, ``update_uc`` --
instructional text guiding an LLM through the UC tool sequence above -- plus
``generate_uc_sequence_diagram`` (feat-185-uc-diagrams Phase 120), the
rulebook §3.8 agent flow for one use case's sequence diagram: read the frozen
rulebook (``specmgr://uc/plantuml``) first, build a ``TodoWrite`` plan, read
the UC via ``get_uc`` (a ``ParseFailureResult`` stops the flow -- repair first),
apply the §2.11 Subfunction judgment, fetch the deterministic skeleton via
``get_uc_sequence_skeleton``, attribute every ``UNATTRIBUTED`` marker by
understanding the free text (the ``question`` tool MUST be used whenever not
confident; pre-filled arrows are positional, not semantic, and may be
corrected), enforce the zero-marker rule, loop ``validate_plantuml`` until
green at the highest available layer (``source_state != ok`` with a source set
=> report ``reason``/``fix_hint`` and do not write; all unset => write with the
``' validated: structure-only`` header as the file's first line), write the
``.puml`` file host-native at ``diagrams/uc/<id>.sequence.puml`` (no specmgr
tool writes ``.puml``), and never commit.
Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
items, and uses the ``question`` tool to resolve ambiguity before proceeding.
QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
appends a fresh batch of unanswered interview questions (each numbered with
its target category's next `**<d>.<NNNN>**: ` prefix and carrying the
`TODO: answer pending` placeholder in place of an answer) to an existing
QA document, for ``Elicitation Context`` or one or more of the nine
ISO/IEC 25010:2023 quality characteristics.
Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
instructional text guiding an LLM through a ``TodoWrite`` + ``question``-tool-
driven 5W2H interview flow, including agent-synthesized ``Summary``/``Gap``
text. ``create_prb`` accepts an optional ``qa_id`` that carries over
already-answered 5W2H questions from a linked QA document instead of
re-asking them, and both prompts narrate composing the mandatory,
code-level-validated ``problem_statement`` lead sentence every PRB now
carries.
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
``specmgr://sop/template``/``/example`` starting-point resources plus the
``get_sop_schema`` tool, the ``specmgr://rasci`` read-first step before ``## Roles and Responsibilities``,
and the ``create_sop``/generic ``validate`` (``type="sop"``) tool calls); ``create_sop`` first checks
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
System Requirements Specification prompts (``sysrs/prompts/``): ``create_sysrs``,
``update_sysrs`` -- narrated instruction flows guiding an LLM through the SYSRS
tool sequence above; ``create_sysrs`` first checks ``list_sysrs`` for a
near-duplicate system requirements specification, then reads the existing
cross-cutting ``specmgr://iso25010`` resource for the nine canonical ISO/IEC
25010:2023 characteristic names used to group ``## Requirements`` (no new
``general`` resource is introduced); ``update_sysrs`` names the generic
``update``/``set_status`` tools with ``type="sysrs"`` (both whole-body and
line-range via ``get_sysrs(id, raw=True)``) -- ``sysrs`` has no per-domain
``update_sysrs``/``set_status_sysrs`` tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0).
Free-form text prompts (``txt/prompts/``): ``create_txt``, ``update_txt`` --
narrated instruction flows guiding an LLM through the TXT tool sequence
above; ``create_txt`` first checks ``list_txt`` for a near-duplicate
free-form text document. ``update_txt`` names the generic ``update``/
``edit``/``set_status`` tools with ``type="txt"`` (both whole-body and
line-range via ``get_txt(id, raw=True)``) -- ``txt`` has no per-domain
``update_txt``/``set_status_txt`` tools (ADR
36905d5b-8057-4294-8665-c7eed5534db0).
General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
``README.md`` into an optional sibling ``history.md``, per ADR
e369ee2e-3353-4f92-991c-6367d76d832e; ``repair`` -- guides repairing a
whole-body document (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/
``dec``/``sop``/``feat``/``vcr``/``sysrs``/``txt``; ADR out of scope) that fails to
parse: discover it via ``get_<d>``'s non-raising parse-failure result
(``error``/``path``/``id``, the ``error`` text carrying the same parse
defect as ``list_<d>``'s failed row for the same file, modulo a possibly-
missing trailing pydantic documentation line; ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c) or ``list_<d>``'s ``<failed to parse>``
failed row, then a host-native raw read, a generic ``validate`` (``full=True``)
loop, a host-native write-back (never the generic ``update`` (or ``edit``) tool, which is
structurally unable to repair a document that fails to parse), and a
post-write ``get_<d>``/``list_<d>`` confirmation against the file as it now
exists on disk (success: the parsed document, not an ``error``-carrying
result); degrades to diagnose-only on a host without file tools
(feat-150-mcp-lifecycle-commands, Phase 1); ``translate_artifact`` -- guides
producing or updating a target-language variant of a whole-body document
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``vcr``/
``sysrs``; ``feat`` and ``adr`` are always English and rejected) from its
source-language content (arguments ``type``, ``id``, ``language``, optional
``source_language`` default ``"en"``): read the ``specmgr://i18n`` resource
first (and the heading table via ``specmgr://i18n/headings/{language}``), read the
source via ``get_<d>(id, raw=True, language=...)`` (a
``ParseFailureResult`` stops the flow), probe the target variant to decide
``create_<d>(content, language, id)`` versus the generic ``update``/``edit`` with
``language``, translate only free-form prose and fixed-text heading text (through
the language's heading table) -- never the closed-vocabulary/schema-constant
tokens (REQ-010) nor ``prb``'s ``problem_statement`` -- retry the write a bounded
number of times on the non-raising ``ValidateResult`` (the generic ``validate``
tool is canonical-only and cannot dry-run a translation), verify with
``get_<d>(id, language=...)`` against the file on disk, and report; it never
commits, never writes English, and a language without a heading table stops the
flow. There is no MCP tool that translates and no dedicated subagent: the
OpenCode host surface is the ``translate-artifact`` skill
(``.opencode/skill/translate-artifact/SKILL.md``) and the ``/translate`` command
(``.opencode/command/translate.md``) (feat-197-i18n, Phase 130).

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``feat``, ``vcr``, ``sysrs``, ``txt``) is a
top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010``/``specmgr://dtais``
resources, the ``mdformat`` tool, or the ``compact_history``/``repair``/``translate_artifact``
prompts) stay under the top-level
``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
Add a new domain by
creating its top-level package and importing it at the bottom of this
module, next to the existing
``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``sop``/``sysrs``/``tsk``/``txt``/``uc``/``vcr``
imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
decorators actually run. ``req``, ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``feat``, ``vcr``, ``sysrs``, and ``txt``
each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
registers all three.

## Classes

### `SpecMgrServer`

``MCPServer`` preserving this repo's caller-visible tool error text.

Since ``mcp`` v2.1.0 (upstream #3314), a tool handler's raised exception
reaches the client wrapped as ``UnexpectedToolError("Error executing tool
<name>")`` -- the handler's own message is swallowed (it survives only in
``__cause__`` and the server log). This repo's documented tool contract is
that the still-raising usage errors (the ``_path_safety`` invalid-id
``ValueError``s, the whole-body domains' ``XNotFoundError``s,
``create_feat``'s ``FileExistsError``, ...) surface to the caller as that
message text, so this subclass overrides only the public ``call_tool`` to
re-raise ``UnexpectedToolError.__cause__`` -- the original exception, which
the SDK always sets via ``raise ... from exc`` -- ``from None`` (no doubled
exception chain in the server log). The SDK's own ``_handle_call_tool``
catch then stringifies that original exception into the ``is_error=True``
``CallToolResult`` it returns: the v2.0.0 wire shape minus the
``Error executing tool <name>: `` prefix. The override is uniform for
every tool registered on this server (the ``adr`` domain's tools
included); it carries no per-domain logic.
(feat-221-mcp-220-error-contract, Phase 100, REQ-002.)

**Methods:**

- `add_prompt(self, prompt: 'Prompt') -> 'None'`
  Add a prompt to the server.

  Args:
      prompt: A Prompt instance to add

- `add_resource(self, resource: 'Resource') -> 'None'`
  Add a resource to the server.

  Args:
      resource: A Resource instance to add

- `add_tool(self, fn: 'Callable[..., Any]', name: 'str | None' = None, title: 'str | None' = None, description: 'str | None' = None, annotations: 'ToolAnnotations | None' = None, icons: 'list[Icon] | None' = None, meta: 'dict[str, Any] | None' = None, structured_output: 'bool | None' = None) -> 'None'`
  Add a tool to the server.

  The tool function can optionally request a Context object by adding a parameter
  with the Context type annotation. See the @tool decorator for examples.

  Args:
      fn: The function to register as a tool
      name: Optional name for the tool (defaults to function name)
      title: Optional human-readable title for the tool
      description: Optional description of what the tool does
      annotations: Optional ToolAnnotations providing additional tool information
      icons: Optional list of icons for the tool
      meta: Optional metadata dictionary for the tool
      structured_output: Controls whether the tool's output is structured or unstructured
          - If None, auto-detects based on the function's return type annotation
          - If True, creates a structured tool (return type annotation permitting)
          - If False, unconditionally creates an unstructured tool

- `call_tool(self, name: 'str', arguments: 'dict[str, Any]', context: 'Context[Any, Any] | None' = None) -> 'CallToolResult | InputRequiredResult'`
  Call a registered tool, re-raising the handler's original exception.

  Args:
      name: The registered tool name.
      arguments: The tool arguments (already validated by the SDK).
      context: The request context; the SDK constructs one when omitted.

  Returns:
      The tool's ``CallToolResult`` (or ``InputRequiredResult``),
      unchanged from ``super().call_tool``.

  Raises:
      The original handler exception, re-raised uniformly from the
      wrapping ``UnexpectedToolError``'s ``__cause__`` -- whatever its
      type, special-casing none. The still-raising families this repo
      documents all surface to the caller as their original message
      text: the ``_path_safety`` invalid-id ``ValueError``s, the
      whole-body domains' ``XNotFoundError``s (``LookupError``
      subclasses), ``create_feat``'s ``FileExistsError``, and the
      ``parse_<d>`` tools' ``OSError`` family (absent/unreadable
      paths). ``exc.__cause__`` is total -- the installed mcp SDK wraps
      every handler crash with ``raise ... from exc`` (verified on
      2.3.0) -- which is what the ``raising-non-exception`` inline
      disable on the raise line documents.

- `completion(self)`
  Decorator to register a completion handler.

  The completion handler receives:
  - ref: PromptReference or ResourceTemplateReference
  - argument: CompletionArgument with name and partial value
  - context: Optional CompletionContext with previously resolved arguments

  Example:
      ```python
      @mcp.completion()
      async def handle_completion(ref, argument, context):
          if isinstance(ref, ResourceTemplateReference):
              # Return completions based on ref, argument, and context
              return Completion(values=["option1", "option2"])
          return None
      ```

- `custom_route(self, path: 'str', methods: 'list[str]', name: 'str | None' = None, include_in_schema: 'bool' = True)`
  Decorator to register a custom HTTP route on the MCP server.

  Allows adding arbitrary HTTP endpoints outside the standard MCP protocol,
  which can be useful for OAuth callbacks, health checks, or admin APIs.
  The handler function must be an async function that accepts a Starlette
  Request and returns a Response.

  Routes using this decorator will not require authorization. It is intended
  for uses that are either a part of authorization flows or intended to be
  public such as health check endpoints.

  Args:
      path: URL path for the route (e.g., "/oauth/callback")
      methods: List of HTTP methods to support (e.g., ["GET", "POST"])
      name: Optional name for the route (to reference this route with
            Starlette's reverse URL lookup feature)
      include_in_schema: Whether to include in OpenAPI schema, defaults to True

  Example:
      ```python
      @server.custom_route("/health", methods=["GET"])
      async def health_check(request: Request) -> Response:
          return JSONResponse({"status": "ok"})
      ```

- `get_prompt(self, name: 'str', arguments: 'dict[str, Any] | None' = None, context: 'Context[LifespanResultT, Any] | None' = None) -> 'GetPromptResult | InputRequiredResult'`
  Get a prompt by name with arguments.

  An `InputRequiredResult` returned by the prompt function is passed
  through unchanged (the 2026-07-28 multi-round-trip flow); the retry's
  answers arrive on `ctx.input_responses`, with `ctx.request_state`
  carrying the echoed opaque state.

- `list_prompts(self) -> 'list[MCPPrompt]'`
  List all available prompts.

- `list_resource_templates(self) -> 'list[MCPResourceTemplate]'`

- `list_resources(self) -> 'list[MCPResource]'`
  List all available resources.

- `list_tools(self) -> 'list[MCPTool]'`
  List all available tools.

- `prompt(self, name: 'str | None' = None, title: 'str | None' = None, description: 'str | None' = None, icons: 'list[Icon] | None' = None) -> 'Callable[[_CallableT], _CallableT]'`
  Decorator to register a prompt.

          The function returns the prompt messages (a string, content block, `Image`/`Audio`,
          `Message`, dict, or a sequence of these), or an `InputRequiredResult` to request
          client input first (the 2026-07-28 multi-round-trip flow — read
          `ctx.input_responses` on the retry).

          Args:
              name: Optional name for the prompt (defaults to function name)
              title: Optional human-readable title for the prompt
              description: Optional description of what the prompt does
              icons: Optional list of icons for the prompt

          Example:
              ```python
              @server.prompt()
              def analyze_table(table_name: str) -> list[Message]:
                  schema = read_table_schema(table_name)
                  return [
                      {
                          "role": "user",
                          "content": f"Analyze this schema:
  {schema}"
                      }
                  ]

              @server.prompt()
              async def analyze_file(path: str) -> list[Message]:
                  content = await read_file(path)
                  return [
                      {
                          "role": "user",
                          "content": {
                              "type": "resource",
                              "resource": {
                                  "uri": f"file://{path}",
                                  "text": content
                              }
                          }
                      }
                  ]
              ```


- `read_resource(self, uri: 'AnyUrl | str', context: 'Context[LifespanResultT, Any] | None' = None) -> 'Iterable[ReadResourceContents] | InputRequiredResult'`
  Read a resource by URI.

  An `InputRequiredResult` returned by a resource template function is
  passed through unchanged (the 2026-07-28 multi-round-trip flow); the
  retry's answers arrive on `ctx.input_responses`, with
  `ctx.request_state` carrying the echoed opaque state.

  Raises:
      ResourceNotFoundError: If no resource or template matches the URI.
      ResourceError: If the resource or template function raises `ResourceError`.
      UnexpectedResourceError: If reading the resource (or creating it from a
          template) raises anything other than `ResourceError` or `MCPError`.
          `__cause__` is the original exception.
      MCPError: Raised by the resource or template function; passed through unchanged.

- `remove_prompt(self, name: 'str') -> 'None'`
  Remove a prompt from the server by name.

  Args:
      name: The name of the prompt to remove

  Raises:
      ValueError: If the prompt does not exist

- `remove_tool(self, name: 'str') -> 'None'`
  Remove a tool from the server by name.

  Args:
      name: The name of the tool to remove

  Raises:
      ToolError: If the tool does not exist

- `resource(self, uri: 'str', *, name: 'str | None' = None, title: 'str | None' = None, description: 'str | None' = None, mime_type: 'str | None' = None, icons: 'list[Icon] | None' = None, annotations: 'Annotations | None' = None, meta: 'dict[str, Any] | None' = None, security: 'ResourceSecurity | None' = None) -> 'Callable[[_CallableT], _CallableT]'`
  Decorator to register a function as a resource.

  The function will be called when the resource is read to generate its content.
  The function can return:
  - str for text content
  - bytes for binary content
  - an InputRequiredResult (template resources only; passed through
    unchanged for the 2026-07-28 multi-round-trip flow — read
    `ctx.input_responses` on the retry)
  - other types will be converted to JSON

  If the URI contains parameters (e.g. "resource://{param}"), it is
  registered as a template resource. Otherwise it is registered as a
  static resource; function parameters on a static URI raise an error.

  Args:
      uri: URI for the resource (e.g. "resource://my-resource" or "resource://{param}")
      name: Optional name for the resource
      title: Optional human-readable title for the resource
      description: Optional description of the resource
      mime_type: Optional MIME type for the resource
      icons: Optional list of icons for the resource
      annotations: Optional annotations for the resource
      meta: Optional metadata dictionary for the resource
      security: Path-safety policy for extracted template parameters.
          Defaults to the server's ``resource_security`` setting.
          Only applies to template resources.

  Example:
      ```python
      @server.resource("resource://my-resource")
      def get_data() -> str:
          return "Hello, world!"


      @server.resource("resource://my-resource")
      async def get_data() -> str:
          data = await fetch_data()
          return f"Hello, world! {data}"


      @server.resource("resource://{city}/weather")
      def get_weather(city: str) -> str:
          return f"Weather for {city}"


      @server.resource("resource://{city}/weather")
      async def get_weather(city: str) -> str:
          data = await fetch_weather(city)
          return f"Weather for {city}: {data}"
      ```

  Raises:
      InvalidUriTemplate: If ``uri`` is not a valid RFC 6570 template.
      ValueError: If URI template parameters don't match the
          function's parameters, or if a parameter bound to a
          ``{?...}``/``{&...}`` query variable has no default
          (the client may omit it).
      TypeError: If the decorator is applied without being called
          (``@resource`` instead of ``@resource("uri")``).

- `run(self, transport: "Literal['stdio', 'sse', 'streamable-http']" = 'stdio', **kwargs: 'Any') -> 'None'`
  Run the MCP server. Note this is a synchronous function.

  Args:
      transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
      **kwargs: Transport-specific options (see overloads for details)

- `run_sse_async(self, *, host: 'str' = '127.0.0.1', port: 'int' = 8000, sse_path: 'str' = '/sse', message_path: 'str' = '/messages/', max_request_body_size: 'int' = 4194304, transport_security: 'TransportSecuritySettings | None' = None) -> 'None'`
  Run the server using SSE transport.

- `run_stdio_async(self) -> 'None'`
  Run the server using stdio transport.

- `run_streamable_http_async(self, *, host: 'str' = '127.0.0.1', port: 'int' = 8000, streamable_http_path: 'str' = '/mcp', json_response: 'bool' = False, stateless_http: 'bool' = False, event_store: 'EventStore | None' = None, retry_interval: 'int | None' = None, max_request_body_size: 'int' = 4194304, session_idle_timeout: 'float | None' = 1800, max_sessions: 'int | None' = 10000, transport_security: 'TransportSecuritySettings | None' = None) -> 'None'`
  Run the server using StreamableHTTP transport.

- `sse_app(self, *, sse_path: 'str' = '/sse', message_path: 'str' = '/messages/', max_request_body_size: 'int' = 4194304, transport_security: 'TransportSecuritySettings | None' = None, host: 'str' = '127.0.0.1') -> 'Starlette'`
  Return an instance of the SSE server app.

- `streamable_http_app(self, *, streamable_http_path: 'str' = '/mcp', json_response: 'bool' = False, stateless_http: 'bool' = False, event_store: 'EventStore | None' = None, retry_interval: 'int | None' = None, max_request_body_size: 'int' = 4194304, session_idle_timeout: 'float | None' = 1800, max_sessions: 'int | None' = 10000, transport_security: 'TransportSecuritySettings | None' = None, host: 'str' = '127.0.0.1') -> 'Starlette'`
  Return an instance of the StreamableHTTP server app.

- `tool(self, name: 'str | None' = None, title: 'str | None' = None, description: 'str | None' = None, annotations: 'ToolAnnotations | None' = None, icons: 'list[Icon] | None' = None, meta: 'dict[str, Any] | None' = None, structured_output: 'bool | None' = None) -> 'Callable[[_CallableT], _CallableT]'`
  Decorator to register a tool.

  Tools can optionally request a Context object by adding a parameter with the
  Context type annotation. The context provides access to MCP capabilities like
  logging, progress reporting, and resource access.

  Args:
      name: Optional name for the tool (defaults to function name)
      title: Optional human-readable title for the tool
      description: Optional description of what the tool does
      annotations: Optional ToolAnnotations providing additional tool information
      icons: Optional list of icons for the tool
      meta: Optional metadata dictionary for the tool
      structured_output: Controls whether the tool's output is structured or unstructured
          - If None, auto-detects based on the function's return type annotation
          - If True, creates a structured tool (return type annotation permitting)
          - If False, unconditionally creates an unstructured tool

  Example:
      ```python
      @server.tool()
      def my_tool(x: int) -> str:
          return str(x)
      ```

      ```python
      @server.tool()
      async def tool_with_context(x: int, ctx: Context) -> str:
          await ctx.info(f"Processing {x}")
          return str(x)
      ```

      ```python
      @server.tool()
      async def async_tool(x: int, context: Context) -> str:
          await context.report_progress(50, 100)
          return str(x)
      ```


## Functions

### `_lifespan(_server: 'MCPServer') -> 'AsyncGenerator[None, None]'`

Server lifespan: start the unified background startup warmup, then run (ADR 3982712a, REQ-007).

At startup (before the first ``yield`` -- i.e. before any tool call can
run), ``general.tools._startup_warmup.start_startup_warmup`` checks two
lightweight, synchronous presence flags and, unless *both* are set,
starts a single daemon thread (``specmgr-startup-warmup``) running
three phases in order, without joining it: (1) the ``feat`` frontmatter
warmup phase (every live feature folder's frontmatter + H1, cheap);
(2) the ``feat`` full-parse warmup phase (the same folders, fully
parsed through the content-hash-validated clean cache, expensive); (3)
the pre-existing, unchanged feat-134 similarity warmup
(``warmup_similarity_cache``, embedding the full default corpus into
the embedding cache). Phase gating is per-phase, not per-thread: the
new ``SPECMGR_FEAT_WARMUP_DISABLED`` presence flag gates phases 1-2
only, the pre-existing ``SPECMGR_SIMILARITY_DISABLED`` gates phase 3
only (unchanged in meaning) -- when both flags are present, no thread
is started at all (a true no-op, and the server runs exactly as before
either feature shipped). This fixes GitHub issue #187's ``list_feat``
cold-scan timeout by making the very first ``list_feat`` call, even
against a cold server process, resolve every folder via a cheap
frontmatter+H1 cache instead of a full body parse (see
``feat.tools.list_feat``'s own docstring for the request-path contract
this warmup feeds) -- phases 1-2 run first, specifically so ``list_feat``
is already fast within roughly a second of server start, well before
the heavier phase 2/phase 3 work even begins.

Each phase's own availability probe/crash containment lives inside
that phase's own body (``feat.tools._warmup.warmup_feat_caches``'s two
phases; ``warmup_similarity_cache``'s own full availability probe --
the lazy ``import fastembed`` plus the eager model load, including the
one-time first-use download -- runs inside its own phase, Phase 5, Task
5.2 of feat-134, never on this startup path), so server startup is
never blocked by either warmup, and a mid-warmup failure in any phase
is logged and swallowed, never raised out of the thread. This lifespan
does not wait for the thread, and the daemon thread dies with the
process (ADR 3982712a-a46b-4b2b-809f-9c6925a49b44, refining ADR
750842b2-aca4-4649-ba0c-855ec8e1f505's **Warmup** sub-decision via its
own v1.4.0 note).

The import is function-level on purpose: the ``general.tools``
package (via its own ``__init__``'s tool-module imports) imports this
very module (``from ...server import mcp``) for the ``@mcp.tool()``
decorators, so a module-level import here would be a circular import
that fails on the partially-initialised ``mcp`` name.

