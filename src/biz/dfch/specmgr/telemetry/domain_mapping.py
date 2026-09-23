# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The explicit tool/resource/prompt-name -> document-domain mapping (feat-139-logging-telemetry, Phase 5, Task 5.1).

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
  ``validate``) carry the domain in their own ``type`` argument at call
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
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# The document domains
# ---------------------------------------------------------------------------

#: Every document domain a ``mcp.domain`` attribute may carry (the 13
#: registered domains -- the 12 whole-body domains plus the deprecated
#: ``adr``).
DOMAINS: frozenset[str] = frozenset(
    {
        "adr",
        "dec",
        "feat",
        "gol",
        "prb",
        "qa",
        "req",
        "rsk",
        "sop",
        "sysrs",
        "tsk",
        "uc",
        "vcr",
    }
)

#: The generic dispatch tools whose domain lives in their own ``type``
#: argument at call time, not in their registered name.
GENERIC_DISPATCH_TOOLS: frozenset[str] = frozenset({"update", "set_status", "set_classification", "delete", "validate"})

#: The resource uri's scheme prefix (every registered resource uses it).
URI_SCHEME_PREFIX = "specmgr://"

# ---------------------------------------------------------------------------
# The static name -> domain tables (built from the actual registrations;
# see the module docstring for why explicit lists, not heuristics)
# ---------------------------------------------------------------------------

#: Domain-specific tools by registered name (every ``@mcp.tool()`` outside
#: :data:`GENERIC_DISPATCH_TOOLS` and ``mdformat``).
_TOOL_DOMAINS: dict[str, str] = {
    "create_adr": "adr",
    "get_adr": "adr",
    "list_adr": "adr",
    "option_create": "adr",
    "option_delete": "adr",
    "option_list": "adr",
    "option_read": "adr",
    "option_update": "adr",
    "update_frontmatter": "adr",
    "update_section": "adr",
    "validate_adr": "adr",
    "create_dec": "dec",
    "get_dec": "dec",
    "get_dec_example": "dec",
    "get_dec_template": "dec",
    "list_dec": "dec",
    "parse_dec": "dec",
    "create_feat": "feat",
    "get_feat": "feat",
    "get_feat_example": "feat",
    "get_feat_template": "feat",
    "list_feat": "feat",
    "parse_feat": "feat",
    "set_feat_id": "feat",
    "create_gol": "gol",
    "get_gol": "gol",
    "get_gol_example": "gol",
    "get_gol_template": "gol",
    "list_gol": "gol",
    "parse_gol": "gol",
    "create_prb": "prb",
    "get_prb": "prb",
    "get_prb_example": "prb",
    "get_prb_template": "prb",
    "list_prb": "prb",
    "parse_prb": "prb",
    "create_qa": "qa",
    "get_qa": "qa",
    "get_qa_example": "qa",
    "get_qa_template": "qa",
    "list_qa": "qa",
    "parse_qa": "qa",
    "create_req": "req",
    "get_req": "req",
    "get_req_example": "req",
    "get_req_template": "req",
    "list_req": "req",
    "parse_req": "req",
    "create_rsk": "rsk",
    "get_rsk": "rsk",
    "get_rsk_example": "rsk",
    "get_rsk_template": "rsk",
    "list_rsk": "rsk",
    "parse_rsk": "rsk",
    "create_sop": "sop",
    "get_sop": "sop",
    "get_sop_example": "sop",
    "get_sop_template": "sop",
    "list_sop": "sop",
    "parse_sop": "sop",
    "create_sysrs": "sysrs",
    "get_sysrs": "sysrs",
    "get_sysrs_example": "sysrs",
    "get_sysrs_template": "sysrs",
    "list_sysrs": "sysrs",
    "parse_sysrs": "sysrs",
    "create_tsk": "tsk",
    "get_tsk": "tsk",
    "get_tsk_example": "tsk",
    "get_tsk_template": "tsk",
    "list_tsk": "tsk",
    "parse_tsk": "tsk",
    "create_uc": "uc",
    "get_uc": "uc",
    "get_uc_example": "uc",
    "get_uc_template": "uc",
    "list_uc": "uc",
    "parse_uc": "uc",
    "create_vcr": "vcr",
    "get_vcr": "vcr",
    "get_vcr_example": "vcr",
    "get_vcr_template": "vcr",
    "list_vcr": "vcr",
    "parse_vcr": "vcr",
}

#: Prompts by registered name (every ``@mcp.prompt()``; ``compact_history``
#: is the one prompt with no domain).
_PROMPT_DOMAINS: dict[str, str] = {
    "create_adr": "adr",
    "create_adr_test": "adr",
    "update_adr": "adr",
    "update_adr_test": "adr",
    "create_dec": "dec",
    "update_dec": "dec",
    "create_feat": "feat",
    "update_feat": "feat",
    "create_gol": "gol",
    "update_gol": "gol",
    "create_prb": "prb",
    "update_prb": "prb",
    "create_qa": "qa",
    "refine": "qa",
    "update_qa": "qa",
    "create_req": "req",
    "update_req": "req",
    "create_risk": "rsk",
    "update_risk": "rsk",
    "create_sop": "sop",
    "update_sop": "sop",
    "create_sysrs": "sysrs",
    "update_sysrs": "sysrs",
    "create_task": "tsk",
    "implement_task": "tsk",
    "update_task": "tsk",
    "create_uc": "uc",
    "update_uc": "uc",
    "create_vcr": "vcr",
    "update_vcr": "vcr",
}

#: The item-type values this module maps (mirrors ``telemetry/middleware.
#: py``'s own ``ITEM_TYPE_*`` constants; duplicated here so this module
#: stays importable without the middleware).
_ITEM_TYPE_TOOL = "tool"
_ITEM_TYPE_RESOURCE = "resource"
_ITEM_TYPE_PROMPT = "prompt"


def resource_domain(uri: str) -> str | None:
    """Return the document domain a ``specmgr://`` resource uri belongs to.

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
    """
    assert isinstance(uri, str), type(uri)
    if not uri.startswith(URI_SCHEME_PREFIX):
        result: str | None = None
        return result
    first_segment = uri[len(URI_SCHEME_PREFIX) :].split("/", 1)[0]
    if first_segment in DOMAINS:
        result = first_segment
        return result
    result = None
    return result


def item_domain(item_type: str, item_name: str | None, *, type_argument: str | None = None) -> str | None:
    """Derive the ``mcp.domain`` value for one observed invocation (Task 5.1).

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
    """
    assert item_type in {_ITEM_TYPE_TOOL, _ITEM_TYPE_RESOURCE, _ITEM_TYPE_PROMPT}, item_type
    if item_name is None:
        result: str | None = None
        return result
    if item_type == _ITEM_TYPE_TOOL:
        if item_name in GENERIC_DISPATCH_TOOLS:
            if type_argument in DOMAINS:
                result = type_argument
                return result
            result = None
            return result
        result = _TOOL_DOMAINS.get(item_name)
        return result
    if item_type == _ITEM_TYPE_PROMPT:
        result = _PROMPT_DOMAINS.get(item_name)
        return result
    result = resource_domain(item_name)
    return result
