# `biz.dfch.specmgr.uc.tools.validate_plantuml`

``@mcp.tool()`` wrapper: validate_plantuml (feat-185-uc-diagrams, Phase 120).

Direct, thin wrapper over ``plantuml.chain.validate_plantuml`` (Phase 110)
-- the strict first-set-wins validation chain (rulebook
``specmgr://uc/plantuml`` §3: structure pre-flight always, then the single
configured source -- ``SPECMGR_PLANTUML_JAR`` → ``SPECMGR_PLANTUML_BIN`` →
``SPECMGR_PLANTUML_URL``, no fall-through; the all-unset state is the
structure-only floor). The returned ``PlantumlValidationResult`` is the
frozen §3.6 non-raising result model (the ADR 519d1206 chain precedent) --
a dataclass the MCP SDK serializes directly; this wrapper adds no state of
its own. Content-based: the caller passes the diagram text (the Phase 130
CLI reads the file and passes its text).

## Functions

### `validate_plantuml(text: 'str') -> 'PlantumlValidationResult'`

Validate one PlantUML diagram's text through the strict chain.

Parameters
----------
text:
    The full diagram source (``@startuml ...`` through ``@enduml``).
    Content-based by design -- a CLI reads the file and passes its text.

Returns
-------
PlantumlValidationResult
    The frozen §3.6 result model (non-raising): ``structure_ok`` plus
    ``valid``/``rendered`` (``None`` = "not run"), ``checked_by``,
    ``errors``/``warnings`` (1-based line + message + fix hint),
    ``source_state``, ``available``, ``reason``, ``fix_hint``. On a
    structure-red short-circuit (§3.7) the parser is never called
    (no subprocess, no network); on the all-unset floor (§3.4) only
    the structure checker runs; with a configured source, a
    set-but-unavailable one is a hard failure (no fall-through,
    rulebook §3.3).

