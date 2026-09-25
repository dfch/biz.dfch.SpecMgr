# `biz.dfch.specmgr.telemetry.domain_mapping`

The explicit tool/resource/prompt-name -> document-domain mapping (feat-139-logging-telemetry, Phase 5, Task 5.1).

The ``mcp.domain`` attribute of every metric (and the ``domain`` extra of
every log record) this feature emits needs a document domain per observed
invocation, and no such name -> domain mapping existed anywhere in the
codebase before this module (the Design Notes' "``mcp.domain``
attribution" bullet: new design work, not a refactor of an existing
mechanism). The mapping is explicit and static, built by reading the
actual ``@mcp.tool()``/``@mcp.prompt()``/``@mcp.resource()``
registrations across every domain package and ``general``:

- **domain-specific tools** (``create_req``, ``get_req``, ...) and
  **prompts** (``create_req``, ``update_req``, ...) map by their
  registered ``name`` via :data:`_TOOL_DOMAINS`/
  :data:`_PROMPT_DOMAINS`. The tables are explicit name lists, not
  prefix/suffix heuristics, because several registered names do not
  contain their domain's name at all (``refine`` -> ``qa``,
  ``create_task``/``implement_task``/``update_task`` -> ``tsk``,
  ``create_risk``/``update_risk`` -> ``rsk``, ``create_adr_test``/
  ``update_adr_test`` -> ``adr``);
- **generic dispatch tools** (:data:`GENERIC_DISPATCH_TOOLS` --
  ``update``/``set_status``/``set_classification``/``delete``/
  ``validate``/``list_references``) carry the domain in their own
  ``type`` argument at call
  time, so they map via that argument (a ``type`` value that is not one
  of the :data:`DOMAINS` yields no domain -- the tool will fail its own
  closed-vocabulary validation anyway);
- **resources** map by their ``uri`` (never a ``name`` argument -- the
  Design Notes' "Per-method target extraction" bullet), by the uri's
  first path segment after the ``specmgr://`` prefix (the RFC 3986
  authority of ``specmgr://<segment>/...``): when that segment is one of
  the :data:`DOMAINS` it *is* the domain (``specmgr://req/schema`` ->
  ``req``, ``specmgr://rsk/tara``/``specmgr://rsk/risk-matrix`` ->
  ``rsk``, the parameterized ``specmgr://adr/{id}`` template and every
  concrete ``specmgr://adr/<uuid>`` read -> ``adr``); when it is not
  (``specmgr://version``, ``specmgr://config``, ``specmgr://iso25010``,
  ``specmgr://dtais``, ``specmgr://ears``, ``specmgr://rasci``,
  ``specmgr://telemetry/status``) there is no domain;
- the **no-domain case** (``mdformat``, ``compact_history``, the
  no-domain resources above, an unknown future item) yields ``None`` --
  the caller then *omits* the ``mcp.domain`` attribute / ``domain``
  extra entirely (never an empty string).

The deprecated ADR domain still counts as a domain for metrics (its tools
map to ``adr``). ``tests/telemetry/test_domain_mapping.py``'s
live-registration drift test keeps the static tables exactly in sync
with what ``server.py`` actually registers (both directions: no
unregistered name may remain in a table, no registered item may go
unmapped).

Like ``telemetry/config.py``, this module is stdlib-only and
import-safe from the base library (it is imported by
``telemetry/middleware.py`` and its tests).

## Functions

### `item_domain(item_type: 'str', item_name: 'str | None', *, type_argument: 'str | None' = None) -> 'str | None'`

Derive the ``mcp.domain`` value for one observed invocation (Task 5.1).

The single entry point the middleware calls with the invocation's
item type, its per-method identity key (the tool/prompt ``name`` or
the resource ``uri``, per the middleware's own extraction), and, for
a generic dispatch tool, that tool's ``type`` argument.

Args:
    item_type: The item type (``tool``/``resource``/``prompt``).
    item_name: The invoked item's identity (``None`` when it could
        not be extracted -- always yields ``None``).
    type_argument: The generic dispatch tool's ``type`` argument
        (``None`` when absent or not a string; only consulted for
        the tools in :data:`GENERIC_DISPATCH_TOOLS`).

Returns:
    The document domain, or ``None`` (the caller then omits the
    ``mcp.domain`` attribute / ``domain`` extra entirely -- never an
    empty string).


### `resource_domain(uri: 'str') -> 'str | None'`

Return the document domain a ``specmgr://`` resource uri belongs to.

The rule: the uri's first path segment after the ``specmgr://``
prefix (the RFC 3986 authority of ``specmgr://<segment>/...``) is the
domain when it is one of :data:`DOMAINS`, else there is no domain.
This maps ``specmgr://req/schema`` -> ``req`` and every domain's
``schema``/``example``/``template`` resource to its domain,
``specmgr://rsk/tara``/``specmgr://rsk/risk-matrix`` -> ``rsk``, and
the parameterized ``specmgr://adr/{id}`` template (and every concrete
``specmgr://adr/<uuid>`` a client reads) -> ``adr``; the cross-cutting
resources (``specmgr://version``, ``specmgr://config``,
``specmgr://iso25010``, ``specmgr://dtais``, ``specmgr://ears``,
``specmgr://rasci``, ``specmgr://telemetry/status``) have no domain.

Args:
    uri: The resource uri (``resources/read``'s ``ctx.params["uri"]``).

Returns:
    The domain, or ``None`` when the uri has no domain.

