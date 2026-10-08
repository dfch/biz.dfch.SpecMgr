# `biz.dfch.specmgr.uc.tools.get_uc_diagram`

``@mcp.tool()`` wrapper: get_uc_diagram (feat-185-uc-diagrams, Phase 120).

Read-only, id-based diagram tool: renders one use case's deterministic
PlantUML usecase diagram (rulebook ``specmgr://uc/plantuml`` §2.5 -- one
``usecase`` node labelled by title + level stereotype, one ``actor`` node
per distinct cleaned actor label, plain associations). Thin wrapper: the id
resolution mirrors ``get_uc`` exactly (``_path_safety``-guarded, cache-aware
via ``load_by_id``; a truly-absent id raises the domain's not-found error,
an existing-but-broken document returns the non-raising
``ParseFailureResult`` per the feat-150 precedent), and the rendering is the
pure ``uc.models.v2.renderer.render_uc_diagram`` (Phase 110).

## Functions

### `get_uc_diagram(id: 'str') -> 'str | ParseFailureResult'`

Render and return the PlantUML usecase diagram for the use case ``id``.

Parameters
----------
id:
    The use case document's specmgr-assigned identifier.

Returns
-------
str | ParseFailureResult
    The diagram text (``@startuml ...`` through ``@enduml``, one trailing
    newline) -- byte-stable per the rulebook §2.6 frozen reference. When
    the document exists but fails to parse, a
    :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
    (``error``/``path``/``id``) is returned instead of raising (the
    feat-150 precedent, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c).
    Raises :class:`._paths.UcNotFoundError` if no use case has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed id for this
    domain (raised before any filesystem access).

