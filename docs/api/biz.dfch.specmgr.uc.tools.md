# `biz.dfch.specmgr.uc.tools`

MCP tool wrappers for use cases (mirrors ``req/tools/``'s own shape).

``parse_uc`` reads a raw filepath, parses, and validates it into a structured
document model (added ahead of Task 3.1's full specification; unchanged).
``get_uc_example`` returns a complete, valid sample use-case document as raw
markdown (Task 3.1.2); ``get_uc_template`` returns a document with every
field present but populated with short placeholder ("blind text") content
instead (Task 3.1.3) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. ``get_uc`` (Task 3.1.5)
reads, parses, and returns a full use-case document by id -- the sole
id-based read path for UC. ``list_uc`` (feat-13-list-paging Task 2.3)
returns one page of id/title/status/ref summaries of every use case,
replacing the former ``specmgr://uc/list`` resource so that
``max_results``/``offset`` paging parameters could be accepted (see
``.specmgr/feat/feat-13-list-paging/README.md``). ``create_uc`` (Task 3.1.5)
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the use-case base directory
(``uc.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in ``general.tools``
(``type="uc"``), preserving every frontmatter field except ``updated``.
Status changes of an existing document go through the generic
``set_status`` tool in ``general.tools`` (``type="uc"``), also bumping
``updated``, leaving the body untouched. Deletion of ``uc`` documents
goes through the generic ``delete`` tool in ``general.tools``
(``type="uc"``). Disk-free, id-free dry-run content validation goes
through the generic ``validate`` tool in ``general.tools`` (``type="uc"``)
-- the former ``validate_uc`` tool was removed in favor of it
(feat-81-83-validation Phase 2).

The diagram surface (feat-185-uc-diagrams, Phase 120) is read-only and
thin over the Phase 110 library (``uc.models.v2.renderer`` + the
import-free ``plantuml`` package): ``get_uc_diagram``/
``get_uc_sequence_skeleton`` render one use case's per-UC usecase diagram /
sequence skeleton by id (``_path_safety``-guarded, cache-aware; an
existing-but-broken document returns the non-raising ``ParseFailureResult``,
the feat-150 precedent), ``get_use_case_package_diagram`` renders the
multi-UC package diagram (``ids=None`` = every UC in ``list_uc`` order,
delegated to the ``list_uc`` tool; missing/broken ids become skipped slots
whose references take the deterministic unresolvable-note path -- the render
never fails on an id), ``validate_plantuml`` is the strict validation chain
(non-raising §3.6 result), ``get_uc_plantuml_template``/
``get_uc_plantuml_example`` return the packaged PlantUML-source
template/example verbatim, and ``plantuml_encode`` returns the classic
``SoWkI…``-form URL encoding (the ``{enc}`` payload of
``GET {base}/svg/{enc}``; the tool takes no base URL).

Import this package to register all use-case tools at once::

    from biz.dfch.specmgr.uc import tools  # noqa: F401 (side-effects only)
