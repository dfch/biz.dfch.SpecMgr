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

"""Unit tests for the shared ``WHOLE_BODY_DOMAINS`` registry (feat-134, Phase 1, REQ-012).

Covers ACC-013 (the registry is the one source of the 12-domain set, ``adr``
excluded, and the lookup rejects ``adr``/unknown names with ``ValueError``)
and the ``adr``-rejection half of ACC-007.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._domains import (
    WHOLE_BODY_DOMAINS,
    WholeBodyDomain,
    whole_body_domain,
)


class TestWholeBodyDomainsTuple(unittest.TestCase):
    """ACC-013: the registry tuple is exactly the 12 whole-body domains, ``adr`` excluded."""

    def test_equals_the_12_domain_tuple(self) -> None:
        expected = (
            "req",
            "uc",
            "tsk",
            "qa",
            "prb",
            "gol",
            "rsk",
            "dec",
            "sop",
            "feat",
            "vcr",
            "sysrs",
        )

        self.assertEqual(WHOLE_BODY_DOMAINS, expected)

    def test_adr_is_excluded(self) -> None:
        self.assertNotIn("adr", WHOLE_BODY_DOMAINS)

    def test_no_duplicates(self) -> None:
        self.assertEqual(len(WHOLE_BODY_DOMAINS), len(set(WHOLE_BODY_DOMAINS)))


class TestWholeBodyDomainLookup(unittest.TestCase):
    """ACC-013/ACC-007: the name lookup returns each entry and rejects ``adr``/unknown names."""

    def test_returns_an_entry_for_every_registered_domain(self) -> None:
        for name in WHOLE_BODY_DOMAINS:
            with self.subTest(name=name):
                entry = whole_body_domain(name)
                self.assertIsInstance(entry, WholeBodyDomain)
                self.assertEqual(entry.name, name)
                for attr in ("base_dir", "iter_paths", "load_by_id", "parse_text"):
                    self.assertTrue(callable(getattr(entry, attr)), f"{entry.name}.{attr} must be callable")

    def test_adr_rejected_with_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            whole_body_domain("adr")
        self.assertIn("adr", str(ctx.exception))

    def test_unknown_name_rejected_with_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            whole_body_domain("bogus")
        self.assertIn("bogus", str(ctx.exception))

    def test_error_names_the_allowed_set(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            whole_body_domain("nope")
        for name in WHOLE_BODY_DOMAINS:
            self.assertIn(name, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
