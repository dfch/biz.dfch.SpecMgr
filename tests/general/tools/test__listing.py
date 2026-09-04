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

"""Tests for ``general.tools._listing`` (feat-81-83-validation Phase 3, Task 3.1)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml
from pydantic import ValidationError

from biz.dfch.specmgr.general.models.summary import DocSummary
from biz.dfch.specmgr.general.tools._listing import (
    DEFAULT_ERROR_TYPES,
    FAILED_TO_PARSE_MARKER,
    build_summaries,
    default_failed_summary,
)


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just an id/title/status."""

    def __init__(self, id_: str | None, title: str, status: str) -> None:
        self.id = id_
        self.title = title
        self.status = status


class _FakeSummary(DocSummary):
    """A plain ``DocSummary`` subclass, mirroring every domain except ``rsk``/``feat``."""


def _read(path: Path) -> _FakeDoc:
    """Parse fixture text into a ``_FakeDoc``; special sentinel filenames simulate failures."""
    text = path.read_text(encoding="utf-8")
    if text == "ASSERTION_ERROR":
        raise AssertionError("simulated structural failure")
    if text == "VALIDATION_ERROR":
        raise ValidationError.from_exception_data("_FakeDoc", [])
    if text == "YAML_ERROR":
        raise yaml.YAMLError("simulated malformed YAML")
    if text == "VALUE_ERROR":
        raise ValueError("not in the default catch set")
    return _FakeDoc(id_=path.stem, title=text, status="draft")


def _to_summary(doc: _FakeDoc, path: Path) -> _FakeSummary:
    return _FakeSummary(id=doc.id, title=doc.title, status=doc.status, ref=path.stem, path=str(path.resolve()))


def _to_failed_summary(path: Path, error: Exception) -> _FakeSummary:
    return default_failed_summary(_FakeSummary, path, error)


class TestDefaultFailedSummary(unittest.TestCase):
    """Tests for default_failed_summary."""

    def test_sets_the_fixed_marker_and_none_id(self) -> None:
        path = Path("/tmp/some-doc.md")

        sut = default_failed_summary(_FakeSummary, path, ValueError("boom"))

        self.assertIsNone(sut.id)
        self.assertEqual(sut.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(sut.status, FAILED_TO_PARSE_MARKER)
        self.assertEqual(sut.error, "boom")

    def test_ref_defaults_to_path_stem(self) -> None:
        path = Path("/tmp/some-doc.md")

        sut = default_failed_summary(_FakeSummary, path, ValueError("boom"))

        self.assertEqual(sut.ref, "some-doc")

    def test_ref_can_be_overridden(self) -> None:
        path = Path("/tmp/feat-1-x/README.md")

        sut = default_failed_summary(_FakeSummary, path, ValueError("boom"), ref="feat-1-x")

        self.assertEqual(sut.ref, "feat-1-x")

    def test_path_is_always_resolved(self) -> None:
        path = Path("relative/some-doc.md")

        sut = default_failed_summary(_FakeSummary, path, ValueError("boom"))

        self.assertEqual(Path(sut.path), path.resolve())
        self.assertTrue(Path(sut.path).is_absolute())


class TestBuildSummaries(unittest.TestCase):
    """Tests for build_summaries."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_empty_paths_yields_empty_list_and_zero_errors(self) -> None:
        summaries, error_count = build_summaries([], _read, _to_summary, _to_failed_summary)

        self.assertEqual(summaries, [])
        self.assertEqual(error_count, 0)

    def test_all_successful_yields_no_failures(self) -> None:
        paths = [
            self._write("a.md", "Title A"),
            self._write("b.md", "Title B"),
        ]

        summaries, error_count = build_summaries(paths, _read, _to_summary, _to_failed_summary)

        self.assertEqual(error_count, 0)
        self.assertEqual([s.title for s in summaries], ["Title A", "Title B"])
        for summary in summaries:
            self.assertIsNone(summary.error)

    def test_assertion_error_is_caught_and_reported(self) -> None:
        paths = [self._write("broken.md", "ASSERTION_ERROR")]

        summaries, error_count = build_summaries(paths, _read, _to_summary, _to_failed_summary)

        self.assertEqual(error_count, 1)
        self.assertEqual(summaries[0].title, FAILED_TO_PARSE_MARKER)
        self.assertIn("simulated structural failure", summaries[0].error or "")

    def test_validation_error_is_caught_and_reported(self) -> None:
        paths = [self._write("broken.md", "VALIDATION_ERROR")]

        summaries, error_count = build_summaries(paths, _read, _to_summary, _to_failed_summary)

        self.assertEqual(error_count, 1)
        self.assertEqual(summaries[0].status, FAILED_TO_PARSE_MARKER)

    def test_yaml_error_is_caught_and_reported(self) -> None:
        paths = [self._write("broken.md", "YAML_ERROR")]

        summaries, error_count = build_summaries(paths, _read, _to_summary, _to_failed_summary)

        self.assertEqual(error_count, 1)
        self.assertIn("simulated malformed YAML", summaries[0].error or "")

    def test_error_not_in_error_types_propagates(self) -> None:
        paths = [self._write("broken.md", "VALUE_ERROR")]

        with self.assertRaises(ValueError):
            build_summaries(paths, _read, _to_summary, _to_failed_summary)

    def test_mixed_success_and_failure_preserves_order_and_counts_only_failures(self) -> None:
        paths = [
            self._write("a.md", "Title A"),
            self._write("broken.md", "ASSERTION_ERROR"),
            self._write("b.md", "Title B"),
        ]

        summaries, error_count = build_summaries(paths, _read, _to_summary, _to_failed_summary)

        self.assertEqual(error_count, 1)
        self.assertEqual([s.ref for s in summaries], ["a", "broken", "b"])
        self.assertIsNone(summaries[0].error)
        self.assertIsNotNone(summaries[1].error)
        self.assertIsNone(summaries[2].error)

    def test_custom_error_types_narrows_the_catch_set(self) -> None:
        paths = [self._write("broken.md", "ASSERTION_ERROR")]

        with self.assertRaises(AssertionError):
            build_summaries(paths, _read, _to_summary, _to_failed_summary, error_types=(yaml.YAMLError,))

    def test_default_error_types_is_the_three_channel_tuple(self) -> None:
        self.assertEqual(DEFAULT_ERROR_TYPES, (AssertionError, ValidationError, yaml.YAMLError))


if __name__ == "__main__":
    unittest.main()
