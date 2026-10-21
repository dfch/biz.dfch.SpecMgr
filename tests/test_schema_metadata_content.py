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

"""feat-189 Phase 120 (C14), retargeted in Phase 135: the regenerated
``docs/<domain>_schema.json`` files carry the inventory's ``enum``/``pattern``
metadata at the expected schema locations (ACC-004's "carrying the inventory's
enum/pattern metadata" half) -- and the 11 object-node ``enum`` keys Phase 120
emitted no longer exist.

One parametrized central test over all 12 domains (rather than one test class per
domain) because every assertion has the same shape -- a key present at a fixed JSON
pointer with a fixed expected value -- and the expected values are imported from the
domains' own enforcing constants (single source of truth; no hand-copied set), so the
table below is the per-domain enumeration of *where* each emitted set lands. The
``$comment`` version marker is pinned per domain as well (E4: the metadata change
must not bump it).

Phase 135 (the C13 corrective): the 12 kept keys are the 12 frontmatter status
``enum``s (plain string nodes -- wire-valid) and the 9 object-level ``pattern``
keys (inert on object nodes; JSON Schema ``pattern`` applies to strings only).
The 11 removed ``enum`` keys sat on OBJECT-typed nodes (req ``Level.value``,
rsk ``Strategy.value``, vcr ``Coverage.value``, vcr ``AcceptanceCriterion``,
prb ``Question1``..``Question7``), where the MCP SDK's own
``structuredContent``-vs-``outputSchema`` validation can never be satisfied (an
object instance can never equal a string ``enum`` member) -- pinned by
``tests/test_mcp_output_schema_satisfiability.py``, and regression-guarded here
against re-emission (``test_removed_object_node_enums_absent``: the 11 former
pointers carry NO ``enum`` key).
"""

from __future__ import annotations

import json
import unittest
from typing import cast

from biz.dfch.specmgr._paths import REPO_ROOT
from biz.dfch.specmgr.dec.models.v1 import SCHEMA_COMMENT_VERSION as _DEC_COMMENT
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_STATUSES
from biz.dfch.specmgr.feat.models.v1 import SCHEMA_COMMENT_VERSION as _FEAT_COMMENT
from biz.dfch.specmgr.feat.models.v1.frontmatter import _ALLOWED_STATUSES as _FEAT_STATUSES
from biz.dfch.specmgr.gol.models.v1 import SCHEMA_COMMENT_VERSION as _GOL_COMMENT
from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_STATUSES
from biz.dfch.specmgr.prb.models.v1 import SCHEMA_COMMENT_VERSION as _PRB_COMMENT
from biz.dfch.specmgr.prb.models.v1.body import _PROBLEM_STATEMENT_PATTERN
from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_STATUSES
from biz.dfch.specmgr.qa.models.v2 import SCHEMA_COMMENT_VERSION as _QA_COMMENT
from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_STATUSES
from biz.dfch.specmgr.req.models.v1 import SCHEMA_COMMENT_VERSION as _REQ_COMMENT
from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_STATUSES
from biz.dfch.specmgr.rsk.models.v1 import SCHEMA_COMMENT_VERSION as _RSK_COMMENT
from biz.dfch.specmgr.rsk.models.v1.assessment import _IMPACT_ALIAS_PATTERN
from biz.dfch.specmgr.rsk.models.v1.assessment import _PROBABILITY_ALIAS_PATTERN
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_STATUSES
from biz.dfch.specmgr.sop.models.v1 import SCHEMA_COMMENT_VERSION as _SOP_COMMENT
from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_STATUSES
from biz.dfch.specmgr.sysrs.models.v1 import SCHEMA_COMMENT_VERSION as _SYSRS_COMMENT
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_STATUSES
from biz.dfch.specmgr.tsk.models.v1 import SCHEMA_COMMENT_VERSION as _TSK_COMMENT
from biz.dfch.specmgr.tsk.models.v1.body import _UPDATE_ENTRY_ALIAS_PATTERN
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_STATUSES
from biz.dfch.specmgr.tsk.models.v1.task_item import _MARKER_SCHEMA_PATTERN
from biz.dfch.specmgr.uc.models.v2 import SCHEMA_COMMENT_VERSION as _UC_COMMENT
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_STATUSES
from biz.dfch.specmgr.vcr.models.v1 import SCHEMA_COMMENT_VERSION as _VCR_COMMENT
from biz.dfch.specmgr.vcr.models.v1.body import _AC_ALIAS_PATTERN
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_STATUSES


def _status_pointer(frontmatter_def: str) -> list[str]:
    """The JSON-pointer path (relative to the schema root) of one domain's own
    ``status`` ``enum`` metadata."""
    result = ["$defs", frontmatter_def, "properties", "status", "enum"]
    return result


#: (domain, its own ``$comment`` version marker, [(schema path, expected value)]) --
#: every expected value imported from the domain's own enforcing source, never
#: hand-copied.
_SCHEMA_SPECS: dict[str, tuple[str, list[tuple[list[str], object]]]] = {
    "req": (
        _REQ_COMMENT,
        [
            (_status_pointer("ReqFrontmatter"), sorted(_REQ_STATUSES)),
        ],
    ),
    "uc": (
        _UC_COMMENT,
        [(_status_pointer("UcFrontmatter"), sorted(_UC_STATUSES))],
    ),
    "tsk": (
        _TSK_COMMENT,
        [
            (_status_pointer("TskFrontmatter"), sorted(_TSK_STATUSES)),
            (["$defs", "TaskItem", "pattern"], _MARKER_SCHEMA_PATTERN),
            (["$defs", "UpdateEntry", "pattern"], _UPDATE_ENTRY_ALIAS_PATTERN),
        ],
    ),
    "qa": (
        _QA_COMMENT,
        [
            (_status_pointer("QaFrontmatter"), sorted(_QA_STATUSES)),
            (["$defs", "QaQuestionAnswer", "properties", "question", "pattern"], r"^\*\*\d\.\d{4}\*\*:\s"),
        ],
    ),
    "prb": (
        _PRB_COMMENT,
        [
            (_status_pointer("PrbFrontmatter"), sorted(_PRB_STATUSES)),
            (["$defs", "Prb", "properties", "problem_statement", "pattern"], _PROBLEM_STATEMENT_PATTERN.pattern),
        ],
    ),
    "gol": (
        _GOL_COMMENT,
        [(_status_pointer("GolFrontmatter"), sorted(_GOL_STATUSES))],
    ),
    "rsk": (
        _RSK_COMMENT,
        [
            (_status_pointer("RskFrontmatter"), sorted(_RSK_STATUSES)),
            (["$defs", "Probability", "pattern"], _PROBABILITY_ALIAS_PATTERN),
            (["$defs", "Impact", "pattern"], _IMPACT_ALIAS_PATTERN),
        ],
    ),
    "dec": (
        _DEC_COMMENT,
        [(_status_pointer("DecFrontmatter"), sorted(_DEC_STATUSES))],
    ),
    "sop": (
        _SOP_COMMENT,
        [(_status_pointer("SopFrontmatter"), sorted(_SOP_STATUSES))],
    ),
    "feat": (
        _FEAT_COMMENT,
        [
            (_status_pointer("FeatFrontmatter"), sorted(_FEAT_STATUSES)),
            # feat's TaskItem subclasses inherit tsk TaskItem's own model_config
            # metadata (Pydantic merges base config) -- the same checkbox
            # constraint they enforce through the inherited computed fields.
            (["$defs", "AcceptanceCriterionItem", "pattern"], _MARKER_SCHEMA_PATTERN),
            (["$defs", "FeatTaskItem", "pattern"], _MARKER_SCHEMA_PATTERN),
        ],
    ),
    "vcr": (
        _VCR_COMMENT,
        [
            (_status_pointer("VcrFrontmatter"), sorted(_VCR_STATUSES)),
            (["$defs", "AcceptanceCriterion", "pattern"], _AC_ALIAS_PATTERN),
        ],
    ),
    "sysrs": (
        _SYSRS_COMMENT,
        [(_status_pointer("SysrsFrontmatter"), sorted(_SYSRS_STATUSES))],
    ),
}


#: The 11 OBJECT-typed schema nodes whose Phase 120 (C13) ``enum`` key was
#: removed in Phase 135 (the C13 corrective, round-trip-rerun.md): the MCP SDK
#: validates every tool's ``structuredContent`` against the generated output
#: schema, and an object instance can never equal a string ``enum`` member, so
#: any ``enum`` key at one of these pointers breaks the non-raw ``get_<d>``
#: wire. (domain, node path) -- the node must exist and carry NO ``enum`` key.
_REMOVED_OBJECT_NODE_ENUMS: list[tuple[str, list[str]]] = [
    ("req", ["$defs", "Level", "properties", "value"]),
    ("prb", ["$defs", "Question1"]),
    ("prb", ["$defs", "Question2"]),
    ("prb", ["$defs", "Question3"]),
    ("prb", ["$defs", "Question4"]),
    ("prb", ["$defs", "Question5"]),
    ("prb", ["$defs", "Question6"]),
    ("prb", ["$defs", "Question7"]),
    ("rsk", ["$defs", "Strategy", "properties", "value"]),
    ("vcr", ["$defs", "Coverage", "properties", "value"]),
    ("vcr", ["$defs", "AcceptanceCriterion"]),
]


def _lookup(root: object, path: list[str]) -> object:
    node = root
    for key in path:
        assert isinstance(node, dict)
        node = node[key]
    return node


class TestSchemaCarriesInventoryMetadata(unittest.TestCase):
    """Every regenerated ``docs/<domain>_schema.json`` carries the emitted metadata at the
    expected location with the expected value, and the ``$comment`` marker is unchanged."""

    def test_expected_enum_and_pattern_keys_present(self) -> None:
        for domain, (_comment, specs) in _SCHEMA_SPECS.items():
            schema = json.loads((REPO_ROOT / "docs" / f"{domain}_schema.json").read_text(encoding="utf-8"))
            for path, expected in specs:
                with self.subTest(domain=domain, path=".".join(path)):
                    self.assertEqual(_lookup(schema, path), expected)

    def test_schema_comment_version_marker_unchanged(self) -> None:
        for domain, (comment, _specs) in _SCHEMA_SPECS.items():
            schema = json.loads((REPO_ROOT / "docs" / f"{domain}_schema.json").read_text(encoding="utf-8"))
            with self.subTest(domain=domain):
                self.assertEqual(schema["$comment"], comment)

    def test_removed_object_node_enums_absent(self) -> None:
        """Regression guard (feat-189 Phase 135): none of the 11 removed object-node
        ``enum`` keys may re-appear at its former pointer."""
        for domain, path in _REMOVED_OBJECT_NODE_ENUMS:
            schema = json.loads((REPO_ROOT / "docs" / f"{domain}_schema.json").read_text(encoding="utf-8"))
            with self.subTest(domain=domain, path=".".join(path)):
                node = _lookup(schema, path)
                self.assertIsInstance(node, dict)
                self.assertNotIn("enum", cast("dict[str, object]", node))


class TestPackagedCopiesIdentical(unittest.TestCase):
    """Every packaged ``data/<domain>_schema.json`` copy is byte-identical to its
    ``docs/`` counterpart (the pre-commit ``specmgr-schema-<d>-package`` hook's own
    contract, asserted here directly)."""

    def test_packaged_copy_byte_identical(self) -> None:
        for domain in _SCHEMA_SPECS:
            docs_path = REPO_ROOT / "docs" / f"{domain}_schema.json"
            packaged_path = REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / domain / "data" / f"{domain}_schema.json"
            with self.subTest(domain=domain):
                self.assertEqual(docs_path.read_bytes(), packaged_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
