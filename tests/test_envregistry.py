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

"""Tests for the central env-var registry (``_envregistry``, feat-208 Phase 100).

Covers the ``register``/``get``/``get_with_default``/``all_vars`` semantics
(default insertion, presence-based, set-but-empty, unknown name, idempotent
and conflicting re-registration) and pins the module's stdlib-only import
graph with an AST walk (REQ-001, ACC-001 -- mirroring ``plantuml/``'s
import-free pin in ``tests/plantuml/test_structure.py``), so a
``[cli]``-only import of the registry can never reach the third-party
``mcp`` package or ``server``.

The registry is module-level state, so every behaviour test subclasses
``_IsolatedRegistry``, which snapshots and restores it (and the test names'
own environment entries) around each test -- later phases' registry-backed
completeness test (Phase 150) must never see a test-only registration.
"""

from __future__ import annotations

import ast
import os
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr import _envregistry
from biz.dfch.specmgr._envregistry import EnvVar, all_vars, get, get_with_default, register

# Test-only variable names. No owning module registers any of them (Phase
# 100's registry starts empty; Phase 110+ registers only real ``SPECMGR_*``
# names plus ``FASTEMBED_CACHE_PATH``), and ``_IsolatedRegistry`` restores
# the registry after every test, so they can never leak into Phase 150's
# registry-backed completeness scan.
_NAME_WITH_DEFAULT = "ENVREG_TEST_WITH_DEFAULT"
_NAME_PRESENCE = "ENVREG_TEST_PRESENCE"
_NAME_FLAGGED = "ENVREG_TEST_FLAGGED"
_TEST_NAMES = (_NAME_WITH_DEFAULT, _NAME_PRESENCE, _NAME_FLAGGED)
_UNKNOWN_NAME = "ENVREG_TEST_NEVER_REGISTERED"


def _import_roots(node: Any) -> list[str]:
    """Top-level package(s) of every module ``node`` imports (``[]`` when not an import node).

    Dotted imports resolve by their top-level package; relative imports
    resolve against ``_envregistry``'s own package, so they name the
    namespace root (``biz``) and fail the stdlib check in
    ``TestImportGraphPin``.
    """
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.level > 0:
            package_parts = (_envregistry.__package__ or "").split(".")
            base_parts = package_parts[: len(package_parts) - (node.level - 1)]
            if node.module is not None:
                base_parts = [*base_parts, *node.module.split(".")]
            return [base_parts[0]] if base_parts else []
        if node.module is None:
            return []
        return [node.module.split(".")[0]]
    return []


class _IsolatedRegistry(unittest.TestCase):
    """Snapshots the module-level registry and the test names' env entries around every test."""

    def setUp(self) -> None:
        self._saved_registry: dict[str, EnvVar] = dict(_envregistry._REGISTRY)
        self._saved_env: dict[str, str | None] = {name: os.environ.get(name) for name in _TEST_NAMES}
        for name in _TEST_NAMES:
            os.environ.pop(name, None)

    def tearDown(self) -> None:
        for name, value in self._saved_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        _envregistry._REGISTRY.clear()
        _envregistry._REGISTRY.update(self._saved_registry)


class TestEnvVarRecord(unittest.TestCase):
    """``EnvVar``'s own invariants, via direct construction (no registry involved)."""

    def test_blank_name_is_rejected(self):
        with self.assertRaises(AssertionError) as ctx:
            EnvVar(name="", default=None, description="A test variable.", owner="adr")

        self.assertIn("name", str(ctx.exception))

    def test_blank_description_is_rejected(self):
        with self.assertRaises(AssertionError) as ctx:
            EnvVar(name="ENVREG_X", default=None, description="   ", owner="adr")

        self.assertIn("description", str(ctx.exception))

    def test_blank_owner_is_rejected(self):
        with self.assertRaises(AssertionError) as ctx:
            EnvVar(name="ENVREG_X", default=None, description="A test variable.", owner="")

        self.assertIn("owner", str(ctx.exception))

    def test_empty_fallback_flag_without_a_default_is_rejected(self):
        with self.assertRaises(AssertionError) as ctx:
            EnvVar(
                name="ENVREG_X",
                default=None,
                description="A test variable.",
                owner="general",
                empty_falls_back_to_default=True,
            )

        self.assertIn("default", str(ctx.exception))


class TestRegister(_IsolatedRegistry):
    """``register``: storage, idempotency, and conflict detection."""

    def test_stores_and_returns_the_record(self):
        expected = EnvVar(
            name=_NAME_WITH_DEFAULT,
            default="docs/adr",
            description="ADR base directory override.",
            owner="adr",
            format="filepath",
            choices=("stdio", "sse"),
        )

        result = register(
            _NAME_WITH_DEFAULT,
            default="docs/adr",
            description="ADR base directory override.",
            owner="adr",
            format="filepath",
            choices=("stdio", "sse"),
        )

        self.assertEqual(result, expected)
        self.assertIs(_envregistry._REGISTRY[_NAME_WITH_DEFAULT], result)
        self.assertEqual(all_vars(), (result,))

    def test_idempotent_for_identical_metadata(self):
        first = register(
            _NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr"
        )

        second = register(
            _NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr"
        )

        self.assertIs(second, first)
        self.assertEqual(len(all_vars()), 1)

    def test_conflicting_re_registration_fails_naming_var_and_field(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")

        with self.assertRaises(AssertionError) as ctx:
            register(_NAME_WITH_DEFAULT, default="other", description="ADR base directory override.", owner="adr")

        message = str(ctx.exception)
        self.assertIn(_NAME_WITH_DEFAULT, message)
        self.assertIn("default", message)
        self.assertIn("'docs/adr'", message)
        self.assertIn("'other'", message)

    def test_conflict_report_names_each_conflicting_field(self):
        register(
            _NAME_WITH_DEFAULT, default="stdio", description="MCP transport.", owner="cli", choices=("stdio", "sse")
        )

        with self.assertRaises(AssertionError) as ctx:
            register(
                _NAME_WITH_DEFAULT, default="stdio", description="MCP transport.", owner="general", choices=("sse",)
            )

        message = str(ctx.exception)
        self.assertIn("owner", message)
        self.assertIn("choices", message)
        self.assertNotIn("  default:", message)
        self.assertNotIn("  description:", message)

    def test_re_registration_leaves_the_stored_record_unchanged(self):
        first = register(
            _NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr"
        )

        with self.assertRaises(AssertionError):
            register(_NAME_WITH_DEFAULT, default="other", description="ADR base directory override.", owner="adr")

        self.assertIs(_envregistry._REGISTRY[_NAME_WITH_DEFAULT], first)
        self.assertEqual(all_vars(), (first,))


class TestGet(_IsolatedRegistry):
    """``get``: raw, at-call-time environment read without default insertion."""

    def test_returns_none_when_unset(self):
        register(_NAME_PRESENCE, description="Presence gate.", owner="general")
        sut = get

        result = sut(_NAME_PRESENCE)

        self.assertIsNone(result)

    def test_returns_the_set_value(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get

        with mock.patch.dict(os.environ, {_NAME_WITH_DEFAULT: "override"}):
            result = sut(_NAME_WITH_DEFAULT)

        self.assertEqual(result, "override")

    def test_returns_a_set_but_empty_value_unchanged(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get

        with mock.patch.dict(os.environ, {_NAME_WITH_DEFAULT: ""}):
            result = sut(_NAME_WITH_DEFAULT)

        self.assertEqual(result, "")

    def test_reads_the_environment_at_call_time(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get

        self.assertIsNone(sut(_NAME_WITH_DEFAULT))
        with mock.patch.dict(os.environ, {_NAME_WITH_DEFAULT: "late"}):
            self.assertEqual(sut(_NAME_WITH_DEFAULT), "late")
        self.assertIsNone(sut(_NAME_WITH_DEFAULT))

    def test_unknown_name_fails_loudly_naming_it(self):
        sut = get

        with self.assertRaises(AssertionError) as ctx:
            sut(_UNKNOWN_NAME)

        self.assertIn(_UNKNOWN_NAME, str(ctx.exception))
        self.assertIn("not registered", str(ctx.exception))


class TestGetWithDefault(_IsolatedRegistry):
    """``get_with_default``: at-call-time read, default inserted only when unset."""

    def test_inserts_the_registered_default_when_unset(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get_with_default

        result = sut(_NAME_WITH_DEFAULT)

        self.assertEqual(result, "docs/adr")

    def test_returns_the_set_value(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get_with_default

        with mock.patch.dict(os.environ, {_NAME_WITH_DEFAULT: "override"}):
            result = sut(_NAME_WITH_DEFAULT)

        self.assertEqual(result, "override")

    def test_set_but_empty_stays_set_unless_flagged(self):
        register(_NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr")
        sut = get_with_default

        with mock.patch.dict(os.environ, {_NAME_WITH_DEFAULT: ""}):
            result = sut(_NAME_WITH_DEFAULT)

        self.assertEqual(result, "")

    def test_set_but_empty_falls_back_to_the_default_when_flagged(self):
        register(
            _NAME_FLAGGED,
            default="fastembed_cache",
            description="Model cache directory.",
            owner="general",
            empty_falls_back_to_default=True,
        )
        sut = get_with_default

        with mock.patch.dict(os.environ, {_NAME_FLAGGED: ""}):
            result = sut(_NAME_FLAGGED)

        self.assertEqual(result, "fastembed_cache")

    def test_flagged_still_returns_a_set_nonempty_value(self):
        register(
            _NAME_FLAGGED,
            default="fastembed_cache",
            description="Model cache directory.",
            owner="general",
            empty_falls_back_to_default=True,
        )
        sut = get_with_default

        with mock.patch.dict(os.environ, {_NAME_FLAGGED: "/custom/cache"}):
            result = sut(_NAME_FLAGGED)

        self.assertEqual(result, "/custom/cache")

    def test_presence_based_unset_fails_loudly_naming_it(self):
        register(_NAME_PRESENCE, description="Presence gate.", owner="general")
        sut = get_with_default

        with self.assertRaises(AssertionError) as ctx:
            sut(_NAME_PRESENCE)

        message = str(ctx.exception)
        self.assertIn(_NAME_PRESENCE, message)
        self.assertIn("presence-based", message)
        self.assertIn("get()", message)

    def test_unknown_name_fails_loudly_naming_it(self):
        sut = get_with_default

        with self.assertRaises(AssertionError) as ctx:
            sut(_UNKNOWN_NAME)

        self.assertIn(_UNKNOWN_NAME, str(ctx.exception))
        self.assertIn("not registered", str(ctx.exception))


class TestAllVars(_IsolatedRegistry):
    """``all_vars``: full registry snapshot in registration order."""

    def test_returns_every_record_in_registration_order(self):
        first = register(_NAME_PRESENCE, description="Presence gate.", owner="general")
        second = register(
            _NAME_WITH_DEFAULT, default="docs/adr", description="ADR base directory override.", owner="adr"
        )

        result = all_vars()

        self.assertIsInstance(result, tuple)
        self.assertEqual(result, (first, second))

    def test_is_empty_for_a_fresh_registry(self):
        result = all_vars()

        self.assertEqual(result, ())


class TestImportGraphPin(unittest.TestCase):
    """REQ-001/ACC-001: ``_envregistry`` is stdlib-only, pinned by an AST walk.

    Mirrors ``plantuml/``'s import-free pin (``tests/plantuml/test_structure.py``'s
    ``TestImportFree``), generalized from "no specmgr imports" to "stdlib only"
    (Design Notes "Registry placement"): a ``[cli]``-only import of the
    registry must not be able to reach the third-party ``mcp`` package or
    ``server``.
    """

    def test_every_import_resolves_to_a_stdlib_module(self):
        source_path = Path(_envregistry.__file__)
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

        offenders = [
            f"line {node.lineno}: {root!r}"
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for root in _import_roots(node)
            if root not in sys.stdlib_module_names
        ]

        self.assertEqual(offenders, [], "non-stdlib imports in _envregistry.py:\n" + "\n".join(offenders))

    def test_import_roots_flags_non_stdlib_and_resolves_relative_imports(self):
        tree = ast.parse("import mcp\nfrom biz.dfch.specmgr import server\nfrom . import _paths\n")

        roots = [root for node in ast.walk(tree) for root in _import_roots(node)]

        self.assertIn("mcp", roots)
        self.assertIn("biz", roots)
        self.assertNotIn("mcp", sys.stdlib_module_names)


if __name__ == "__main__":
    unittest.main()
