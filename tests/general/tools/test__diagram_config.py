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

"""Tests for ``general.tools._diagram_config`` (feat-207-reference-graph, Phase 110, Task 110.120).

The ``SPECMGR_DIAGRAM_MAX_TITLE`` env-var helper (rulebook §5.2): unset ⇒
``(40, True)`` (the default, valid); a valid int N ⇒ ``(N, True)``;
set-but-invalid (empty, non-int, or < 1) ⇒ ``(40, False)`` (the fallback
with the invalidity flag the Phase 120 ``specmgr://config`` ``diagram``
section surfaces). The helper registers the variable in the central
env-var registry at import time and reads it through the registry's
``get_with_default`` accessor (the feat-208 dev sync; the int parse with
fallback + validity flag on top is the helper's own part); the pure
renderer never reads the env var itself (it takes ``max_label`` as a plain
parameter).
"""

from __future__ import annotations

import os
import unittest

from biz.dfch.specmgr import _envregistry
from biz.dfch.specmgr.general.models.reference_graph import DEFAULT_MAX_LABEL
from biz.dfch.specmgr.general.tools._diagram_config import (
    DEFAULT_MAX_TITLE,
    ENV_VAR_DIAGRAM_MAX_TITLE,
    diagram_max_title,
)


class TestDiagramMaxTitle(unittest.TestCase):
    """The env read + the int parse with fallback + validity flag."""

    def setUp(self) -> None:
        self._previous = os.environ.get(ENV_VAR_DIAGRAM_MAX_TITLE)
        os.environ.pop(ENV_VAR_DIAGRAM_MAX_TITLE, None)

    def tearDown(self) -> None:
        if self._previous is None:
            os.environ.pop(ENV_VAR_DIAGRAM_MAX_TITLE, None)
        else:
            os.environ[ENV_VAR_DIAGRAM_MAX_TITLE] = self._previous

    def test_unset_is_the_default_and_valid(self):
        self.assertEqual(diagram_max_title(), (40, True))

    def test_valid_ints_round_trip(self):
        for value, expected in (("1", (1, True)), ("7", (7, True)), ("40", (40, True)), ("999", (999, True))):
            with self.subTest(value=value):
                os.environ[ENV_VAR_DIAGRAM_MAX_TITLE] = value
                self.assertEqual(diagram_max_title(), expected)

    def test_whitespace_surrounding_a_valid_int_parses(self):
        # int() semantics: surrounding whitespace is tolerated
        os.environ[ENV_VAR_DIAGRAM_MAX_TITLE] = "  7  "
        self.assertEqual(diagram_max_title(), (7, True))

    def test_set_but_invalid_values_fall_back_with_the_flag(self):
        for value in ("", "abc", "0", "-5", "3.5", "0x28", "40chars"):
            with self.subTest(value=value):
                os.environ[ENV_VAR_DIAGRAM_MAX_TITLE] = value
                self.assertEqual(diagram_max_title(), (40, False))

    def test_the_default_is_shared_with_the_pure_renderer(self):
        # the helper's fallback and the renderer's parameter default must be
        # one constant (the single source of truth in the model module)
        self.assertEqual(DEFAULT_MAX_TITLE, 40)
        self.assertEqual(DEFAULT_MAX_TITLE, DEFAULT_MAX_LABEL)

    def test_env_var_name(self):
        self.assertEqual(ENV_VAR_DIAGRAM_MAX_TITLE, "SPECMGR_DIAGRAM_MAX_TITLE")

    def test_the_registry_record_default_equals_the_frozen_default(self):
        """feat-208 dev sync: the registry record's own default ("40") must equal
        ``str(DEFAULT_MAX_TITLE)`` -- the manifest/registry/code triple cannot
        drift (the ``server.json`` entry documents the same "40", pinned by
        ``tests/test_envregistry_coverage.py``'s manifest-fidelity tests)."""
        record = next(entry for entry in _envregistry.all_vars() if entry.name == ENV_VAR_DIAGRAM_MAX_TITLE)
        self.assertEqual(record.default, str(DEFAULT_MAX_TITLE))
        self.assertEqual(record.default, "40")


if __name__ == "__main__":
    unittest.main()
