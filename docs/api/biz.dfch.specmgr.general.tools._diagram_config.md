# `biz.dfch.specmgr.general.tools._diagram_config`

The ``SPECMGR_DIAGRAM_MAX_TITLE`` env-var helper (feat-207-reference-graph, Phase 110, REQ-008).

The shared read site for the reference-graph label limit (rulebook §5.2):
the ``plantuml/chain.py`` ``ENV_VAR_*`` + ``os.environ.get`` idiom, plus the
new int parse with fallback + validity flag. The Phase 120 MCP tools and
the Phase 130 CLI both call :func:`diagram_max_title` -- the pure renderer
(``general.models.reference_graph.render_reference_graph``) takes the limit
as a plain ``max_label`` parameter and never reads the env var itself.

Set-but-invalid values (empty, non-int, or < 1) fall back to the default
40 with a validity flag ``False`` -- the flag is surfaced by the
``specmgr://config`` ``diagram`` section (Phase 120). The ``server.json``
manifest entry for the variable must travel with this first read site
(``tests/test_server_json.py``'s drift test enforces manifest coverage of
every ``SPECMGR_*`` read in ``src/``).

Plain Python, no ``mcp`` import (like ``plantuml/chain.py``) --
independently testable by pinning the process environment.

## Functions

### `diagram_max_title() -> 'tuple[int, bool]'`

Read ``SPECMGR_DIAGRAM_MAX_TITLE`` into the effective label limit + a validity flag (rulebook §5.2).

Unset ⇒ ``(40, True)`` (the default, valid). Set-but-invalid (empty
string, non-int, or < 1) ⇒ ``(40, False)`` (the fallback with the
invalidity flag -- surfaced by the ``specmgr://config`` ``diagram``
section, Phase 120). A valid int N ⇒ ``(N, True)``.

Returns
-------
tuple[int, bool]
    ``(effective limit, valid)`` -- the int the renderer's
    ``max_label`` parameter must be called with, plus whether the
    environment value (when set) actually determined it.

