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

"""feat-189 Phase 135 (Task 135.100): the missing wire-satisfiability pin.

Root cause this test pins (round-trip-rerun.md, feat-189): Phase 120 (C13)
emitted 11 string ``enum`` keys on OBJECT-typed generated-schema nodes (req
``Level.value``, rsk ``Strategy.value``, vcr ``Coverage.value``, vcr
``AcceptanceCriterion``, prb ``Question1``..``Question7``). The MCP SDK
derives every tool's ``outputSchema`` from its return annotation and its
client validates the tool's ``structuredContent`` against that schema with
``jsonschema`` (``mcp.client.session.Session.validate_tool_result``) -- an
object instance can never equal a string ``enum`` member, so the non-raw
``get_prb``/``get_vcr`` (and every other ``get_<d>`` whose document carries
such a node) ALWAYS failed with ``MCP error -32602`` / "Invalid structured
content". The 11 emissions were removed in Phase 135 (closed-set facts
retained in the field/class descriptions; regression-guarded against
re-emission by ``tests/test_schema_metadata_content.py``); this test is the
12-domain pin that the fix actually holds on the wire.

For every whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/
sysrs, the shared ``WHOLE_BODY_DOMAINS`` source):

1. parse the domain's packaged example through its own models-level
   ``parse_<d>(text)`` (the same parser every ``parse_<d>``/``get_<d>``
   tool runs) -- the prb example carries 5W2H answers and the vcr example
   carries AC entries, so the previously-breaking nodes are exercised;
2. derive the output schema exactly as the MCP SDK does -- confirmed from
   the installed SDK source
   (``mcp/server/mcpserver/utilities/func_metadata.py``): the return
   annotation is a PEP 604 union (``XDocument | str | ParseFailureResult``),
   so the SDK wraps it in a one-``result``-field model
   (``_create_wrapped_model``) and emits
   ``model.model_json_schema()`` as the tool's ``outputSchema``;
3. build the ``structuredContent`` exactly as the SDK's
   ``FuncMetadata.convert_result`` does for a wrapped return --
   ``{"result": doc}`` validated through that same output model and dumped
   with ``model_dump(mode="json", by_alias=True)``;
4. assert ``jsonschema.validate(structured, schema)`` passes -- the same
   validator class the client's ``validate_tool_result`` compiles
   (``validator_for`` over the schema; no ``$schema`` key, so
   Draft 2020-12).

``jsonschema`` is already installed (a direct dependency of the ``mcp``
extra -- the same dependency the SDK's own client validation imports); no
new dependency is introduced.
"""

from __future__ import annotations

import unittest
from collections.abc import Callable
from typing import Any

import jsonschema
from pydantic import BaseModel

from mcp.server.mcpserver.utilities.func_metadata import func_metadata

from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS, whole_body_domain
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.gol.tools.get_gol import get_gol
from biz.dfch.specmgr.prb.tools.get_prb import get_prb
from biz.dfch.specmgr.qa.tools.get_qa import get_qa
from biz.dfch.specmgr.req.tools.get_req import get_req
from biz.dfch.specmgr.rsk.tools.get_rsk import get_rsk
from biz.dfch.specmgr.sop.tools.get_sop import get_sop
from biz.dfch.specmgr.sysrs.tools.get_sysrs import get_sysrs
from biz.dfch.specmgr.tsk.tools.get_tsk import get_tsk
from biz.dfch.specmgr.uc.tools.get_uc import get_uc
from biz.dfch.specmgr.vcr.tools.get_vcr import get_vcr

#: The per-domain ``get_<d>`` tool functions (the raw decorated functions --
#: the ``@mcp.tool()`` decorator returns its argument unchanged), keyed by
#: domain name; the natural dispatch table for this central test, guarded
#: against the shared domain source exactly like every other dispatch table.
_GET_TOOLS: dict[str, Callable[..., Any]] = {
    "req": get_req,
    "uc": get_uc,
    "tsk": get_tsk,
    "qa": get_qa,
    "prb": get_prb,
    "gol": get_gol,
    "rsk": get_rsk,
    "dec": get_dec,
    "sop": get_sop,
    "feat": get_feat,
    "vcr": get_vcr,
    "sysrs": get_sysrs,
}

assert set(_GET_TOOLS) == set(WHOLE_BODY_DOMAINS), (
    "_GET_TOOLS keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- add or "
    "remove the domain in both places"
)


class TestMcpOutputSchemaSatisfiability(unittest.TestCase):
    """Every whole-body domain's SDK-derived ``outputSchema`` accepts the
    ``structuredContent`` the SDK itself would send for the domain's packaged
    example (the non-raw ``get_<d>`` wire path)."""

    def test_packaged_example_structured_content_validates_against_sdk_output_schema(self) -> None:
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                meta = func_metadata(_GET_TOOLS[domain])
                assert meta.output_schema is not None, (
                    f"get_{domain} lost its SDK-derived output schema -- the annotation no longer "
                    "supports structured output, and this pin would pass vacuously"
                )
                assert meta.output_model is not None
                assert meta.wrap_output, (
                    f"get_{domain}'s SDK output wrapping changed -- the structuredContent shape this "
                    "test builds ({'result': doc}) would no longer mirror the wire"
                )
                doc = whole_body_domain(domain).parse_text(read_packaged_text(domain, "example"))
                assert isinstance(doc, BaseModel)
                # Mirror FuncMetadata.convert_result for the wrapped return:
                # {"result": <return value>} -> output_model.model_validate ->
                # model_dump(mode="json", by_alias=True) is the structuredContent.
                structured = meta.output_model.model_validate({"result": doc}).model_dump(mode="json", by_alias=True)
                # The client's Session.validate_tool_result compiles
                # validator_for(output_schema) and runs iter_errors over the
                # structuredContent -- jsonschema.validate is the same check.
                jsonschema.validate(structured, meta.output_schema)


if __name__ == "__main__":
    unittest.main()
