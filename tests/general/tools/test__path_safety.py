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

"""Tests for ``general.tools._path_safety`` (id traversal/format validation and resolved-path containment).

Pure unit tests: no fixture is required for the id checks, and
:func:`tempfile.TemporaryDirectory` is used only to construct real
:class:`~pathlib.Path` objects for the containment checks (the functions
themselves perform no filesystem mutation).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from biz.dfch.specmgr.general.tools._path_safety import (
    assert_feat_id,
    assert_no_traversal,
    assert_uuid,
    assert_within,
    validate_id,
)

#: A canonical lowercase 8-4-4-4-12 hex UUID (the shape every create tool writes).
_VALID_UUID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"

#: A well-formed feat-NNN-slug folder name.
_VALID_FEAT_ID = "feat-36-delete"

#: The eleven UUID domains whose id is a server-generated UUID (the ten
#: whole-body domains plus ``adr``, feat-38-39-41-43-44 Phase 4).
_UUID_DOMAINS = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "adr")

#: The feat document type name.
_FEAT_TYPE = "feat"


class TestAssertNoTraversal(unittest.TestCase):
    """Tests for assert_no_traversal."""

    def test_accepts_a_plain_uuid_id(self):
        """A bare UUID id contains no separators or traversal and must pass."""
        assert_no_traversal(_VALID_UUID)

    def test_accepts_a_plain_feat_id(self):
        """A feat-NNN-slug folder name contains no separators or traversal and must pass."""
        assert_no_traversal(_VALID_FEAT_ID)

    def test_rejects_the_pinned_injection_shapes(self):
        """Each pinned injection shape must raise a ValueError naming the offending value."""
        for value in ("", "../x", "a/b", "a\\b", "..", "a/../b"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    assert_no_traversal(value)
                self.assertIn(repr(value), str(ctx.exception))


class TestAssertUuid(unittest.TestCase):
    """Tests for assert_uuid."""

    def test_accepts_a_canonical_lowercase_uuid(self):
        """A canonical 8-4-4-4-12 lowercase-hex UUID must pass."""
        assert_uuid(_VALID_UUID)

    def test_rejects_an_uppercase_uuid(self):
        """A UUID with uppercase hex digits must raise a ValueError naming the offending value."""
        value = _VALID_UUID.upper()
        with self.assertRaises(ValueError) as ctx:
            assert_uuid(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_31_character_string(self):
        """A 31-character string (not the 36-character UUID shape) must raise a ValueError."""
        value = "x" * 31
        with self.assertRaises(ValueError) as ctx:
            assert_uuid(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_uuid_with_a_slash(self):
        """A UUID with an appended '/' path component must raise a ValueError."""
        value = f"{_VALID_UUID}/x"
        with self.assertRaises(ValueError) as ctx:
            assert_uuid(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_feat_id(self):
        """A feat-NNN-slug folder name is not a UUID and must raise a ValueError."""
        value = "feat-1-x"
        with self.assertRaises(ValueError) as ctx:
            assert_uuid(value)
        self.assertIn(repr(value), str(ctx.exception))


class TestAssertFeatId(unittest.TestCase):
    """Tests for assert_feat_id."""

    def test_accepts_a_well_formed_feat_id(self):
        """A feat-NNN-slug folder name must pass."""
        assert_feat_id(_VALID_FEAT_ID)

    def test_rejects_a_missing_slug(self):
        """'feat-36' has no slug after the number and must raise a ValueError."""
        value = "feat-36"
        with self.assertRaises(ValueError) as ctx:
            assert_feat_id(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_wrong_prefix(self):
        """'feature-36-x' does not start with 'feat-' and must raise a ValueError."""
        value = "feature-36-x"
        with self.assertRaises(ValueError) as ctx:
            assert_feat_id(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_traversal(self):
        """'feat-36/../x' contains separators and traversal and must raise a ValueError."""
        value = "feat-36/../x"
        with self.assertRaises(ValueError) as ctx:
            assert_feat_id(value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_a_uuid(self):
        """A UUID is not a feat-NNN-slug folder name and must raise a ValueError."""
        value = _VALID_UUID
        with self.assertRaises(ValueError) as ctx:
            assert_feat_id(value)
        self.assertIn(repr(value), str(ctx.exception))


class TestValidateId(unittest.TestCase):
    """Tests for validate_id."""

    def test_accepts_a_uuid_for_each_uuid_domain(self):
        """For each of the eleven UUID domains, a canonical UUID must pass."""
        for type_ in _UUID_DOMAINS:
            with self.subTest(type_=type_):
                validate_id(type_, _VALID_UUID)

    def test_rejects_a_feat_id_for_each_uuid_domain(self):
        """For each of the eleven UUID domains, a feat-NNN-slug id must raise a ValueError."""
        for type_ in _UUID_DOMAINS:
            with self.subTest(type_=type_):
                with self.assertRaises(ValueError):
                    validate_id(type_, _VALID_FEAT_ID)

    def test_accepts_a_feat_id_for_the_feat_domain(self):
        """For the feat domain, a feat-NNN-slug id must pass."""
        validate_id(_FEAT_TYPE, _VALID_FEAT_ID)

    def test_rejects_a_uuid_for_the_feat_domain(self):
        """For the feat domain, a UUID must raise a ValueError."""
        with self.assertRaises(ValueError):
            validate_id(_FEAT_TYPE, _VALID_UUID)

    def test_rejects_a_traversal_id(self):
        """A path-injection id must raise a ValueError before any format check."""
        value = "../x"
        with self.assertRaises(ValueError) as ctx:
            validate_id("req", value)
        self.assertIn(repr(value), str(ctx.exception))

    def test_rejects_an_unknown_type(self):
        """A type that is neither a UUID domain nor feat must raise a ValueError naming the type."""
        value = "not-a-real-domain"
        with self.assertRaises(ValueError) as ctx:
            validate_id(value, _VALID_UUID)
        self.assertIn(repr(value), str(ctx.exception))

    def test_accepts_a_uuid_for_adr(self):
        """For the adr domain (feat-38-39-41-43-44 Phase 4), a canonical UUID must pass."""
        validate_id("adr", _VALID_UUID)

    def test_rejects_a_feat_id_for_adr(self):
        """For the adr domain, a feat-NNN-slug id must raise a ValueError."""
        with self.assertRaises(ValueError):
            validate_id("adr", _VALID_FEAT_ID)


class TestAssertWithin(unittest.TestCase):
    """Tests for assert_within."""

    def test_a_child_path_of_the_base_passes(self):
        """A path inside the base directory must pass."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            child = base / "2026-08-31-some-requirement.md"
            assert_within(base, child)

    def test_the_base_itself_passes(self):
        """The base directory is is_relative_to itself and must pass."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            assert_within(base, base)

    def test_a_sibling_path_raises(self):
        """A path in a sibling subdirectory must raise a ValueError naming both paths."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            sibling = Path(tmp) / "uc"
            with self.assertRaises(ValueError) as ctx:
                assert_within(base, sibling)
            message = str(ctx.exception)
            self.assertIn(str(sibling), message)
            self.assertIn(str(base), message)

    def test_an_ancestor_path_raises(self):
        """A path above the base directory must raise a ValueError naming both paths."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "req"
            ancestor = Path(tmp)
            with self.assertRaises(ValueError) as ctx:
                assert_within(base, ancestor)
            message = str(ctx.exception)
            self.assertIn(str(ancestor), message)
            self.assertIn(str(base), message)


if __name__ == "__main__":
    unittest.main()
