# `biz.dfch.specmgr.uc.tools.get_use_case_package_diagram`

``@mcp.tool()`` wrapper: get_use_case_package_diagram (feat-185-uc-diagrams, Phase 120).

Read-only diagram tool: renders the deterministic PlantUML **package**
diagram (rulebook ``specmgr://uc/plantuml`` §2.7 -- one ``usecase`` node
per document, the deduplicated actor union, and the ``<<include>>`` /
``<<extend>>`` / superordinate edges from ``Related Use Cases``). Thin
wrapper over the pure ``uc.models.v2.renderer.render_use_case_package``
(Phase 110), which takes **resolved facts** (``list[PackageDocument]``),
not directory handles: this tool owns the disk resolution (the §11
contract) --

- ``ids=None``: every UC in ``list_uc`` order (all pages, delegated to the
  ``list_uc`` tool itself so the package can never disagree with the
  listing); a ``list_uc`` failed row (an existing-but-broken document)
  becomes a skipped ``use_case=None`` slot,
- explicit ``ids``: each id ``_path_safety``-guarded (a wrong-format id is
  a ``ValueError`` before any file access), cache-aware via
  ``load_by_id``; an id missing on disk or existing-but-broken becomes the
  same skipped slot -- the render never fails on an id,

and every reference that does not resolve to a parsed slot in the package
(taken up by an explicit id, a ``list_uc`` row, or a legacy ``UC-NNN``
token) takes the renderer's deterministic ``Unresolved UC reference`` note
path (rulebook §2.8).

## Functions

### `_list_uc_all_rows() -> 'list[UcSummary]'`

Every ``list_uc`` row, in ``list_uc`` order, across all pages.


### `_slots_from_ids(ids: 'list[str]') -> 'list[PackageDocument]'`

One slot per explicit id, in the given order.

A missing id or an existing-but-broken one (both surface as
``load_by_id``'s ``UcNotFoundError`` -- a broken file's own id is
unreadable, so the id scan skips it) is a ``use_case=None`` slot;
references to it take the renderer's unresolvable-note path. The ids
were already ``_path_safety``-guarded by the caller before this ran.


### `_slots_from_listing() -> 'list[PackageDocument]'`

One slot per ``list_uc`` row, in ``list_uc`` order (all pages).

A failed row (``title`` the ``<failed to parse>`` marker) is a
``use_case=None`` slot. A successful row is read back through the
domain's own cache-backed reader at the row's resolved path (a cache
hit in the normal case -- the listing scan moments ago read the same
file through the same reader); a read that fails in the narrow window
after the listing scan (a concurrent modification or deletion) degrades
to the same ``use_case=None`` slot -- the render never fails.


### `get_use_case_package_diagram(ids: 'list[str] | None' = None) -> 'str'`

Render and return the PlantUML package diagram for the given use cases.

Parameters
----------
ids:
    The use case document ids, in package order. ``None`` (the
    default) selects every UC in ``list_uc`` order -- including the
    ``list_uc`` failed rows, which become skipped slots. An id missing
    on disk or existing-but-broken becomes the same skipped slot; the
    render never fails on an id.

Returns
-------
str
    The package diagram text (``@startuml UC Package`` through
    ``@enduml``, one trailing newline). A reference that does not
    resolve to a parsed slot of the package is emitted as the
    deterministic ``note bottom of {alias}: Unresolved UC reference:
    "{label}"`` line (rulebook §2.8) instead of failing the render.

Raises
------
ValueError
    Any given ``id`` is a path-injection attempt or not a well-formed
    id for this domain (raised before any filesystem access).

