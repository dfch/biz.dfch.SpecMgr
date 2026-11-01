# `biz.dfch.specmgr.general.tools._diagram_config`

The ``SPECMGR_DIAGRAM_MAX_TITLE`` env-var helper (feat-207-reference-graph, Phase 110, REQ-008).

The shared read site for the reference-graph label limit (rulebook §5.2):
the variable's own name constant, its import-time registration in the
central env-var registry, plus the int parse with fallback + validity
flag. The read goes through ``biz.dfch.specmgr._envregistry`` -- the
import-free top-level registry (the import-chain constraint is why the
registry is top-level, not under ``general/tools/``; see the registry's
own module docstring) -- and the Phase 120 MCP tools and the Phase 130
CLI both call :func:`diagram_max_title`; the pure renderer
(``general.models.reference_graph.render_reference_graph``) takes the
limit as a plain ``max_label`` parameter and never reads the env var
itself.

:func:`diagram_max_title` resolves the value through the registry's
``get_with_default`` accessor (an unset value falls back to the record's
registered default, "40"), then applies the int parse with fallback +
validity flag: set-but-invalid values (empty, non-int, or < 1) fall back
to the default 40 with a validity flag ``False`` -- the flag is surfaced
by the ``specmgr://config`` ``diagram`` section (Phase 120). The
``server.json`` manifest entry for the variable must travel with this
first read site (``tests/test_server_json.py``'s drift test enforces
manifest coverage of every ``SPECMGR_*`` read in ``src/``, and
``tests/test_envregistry_coverage.py`` pins the manifest's ``default``/
``format`` against the registry record).

Plain Python, no ``mcp`` import (like ``plantuml/chain.py``) --
independently testable by pinning the process environment.

## Functions

### `diagram_max_title() -> 'tuple[int, bool]'`

Read ``SPECMGR_DIAGRAM_MAX_TITLE`` into the effective label limit + a validity flag (rulebook §5.2).

The value read goes through the central env-var registry's
``get_with_default`` accessor (the registry record's own default is
"40", so an unset value resolves to the default before the parse
below; a set-but-empty value stays set, since the record's
``empty_falls_back_to_default`` flag is False -- the empty string is
one of the set-but-invalid cases, not an empty-fallback). Unset ⇒
``(40, True)`` (the default, valid). Set-but-invalid (empty string,
non-int, or < 1) ⇒ ``(40, False)`` (the fallback with the invalidity
flag -- surfaced by the ``specmgr://config`` ``diagram`` section,
Phase 120). A valid int N ⇒ ``(N, True)``.

Returns
-------
tuple[int, bool]
    ``(effective limit, valid)`` -- the int the renderer's
    ``max_label`` parameter must be called with, plus whether the
    environment value (when set) actually determined it.

