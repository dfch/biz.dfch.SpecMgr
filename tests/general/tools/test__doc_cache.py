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

"""Tests for ``general.tools._doc_cache`` (feat-107-doc-cache, Phase 2)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_cache import CACHEABLE_ERROR_TYPES, DocCache


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just the text it was parsed from."""

    def __init__(self, text: str) -> None:
        self.text = text


class _CountingParser:
    """A counting fake ``parse_fn``: increments ``calls`` each time it is actually invoked.

    Reads ``path``'s text and raises ``raise_type`` (with ``raise_message``)
    instead of returning a ``_FakeDoc`` when the text equals a configured
    trigger sentinel, so a test can flip a file's content to simulate a
    parse failure vs. a parse success.
    """

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, path: Path) -> _FakeDoc:
        self.calls += 1
        text = path.read_text(encoding="utf-8")
        if text.startswith("RAISE:"):
            _, type_name, message = text.split(":", 2)
            raise _EXCEPTION_TYPES_BY_NAME[type_name](message)
        return _FakeDoc(text=text)


_EXCEPTION_TYPES_BY_NAME: dict[str, type[Exception]] = {
    "AssertionError": AssertionError,
    "RuntimeError": RuntimeError,
    "OSError": OSError,
}


class TestDocCacheRead(unittest.TestCase):
    """Tests for DocCache.read (success + failure caching paths)."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sut: DocCache[_FakeDoc] = DocCache()
        self.parser = _CountingParser()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_cache_miss_calls_parse_fn_exactly_once_and_returns_its_result(self) -> None:
        path = self._write("a.md", "hello")

        result = self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 1)
        self.assertEqual(result.text, "hello")

    def test_second_call_against_unchanged_content_does_not_call_parse_fn_again(self) -> None:
        path = self._write("a.md", "hello")
        self.sut.read(path, self.parser)

        result = self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 1)
        self.assertEqual(result.text, "hello")

    def test_modifying_file_content_calls_parse_fn_again(self) -> None:
        path = self._write("a.md", "hello")
        self.sut.read(path, self.parser)

        path.write_text("goodbye", encoding="utf-8")
        result = self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 2)
        self.assertEqual(result.text, "goodbye")

    def test_cacheable_failure_is_reraised_without_reinvoking_parse_fn_on_unchanged_content(self) -> None:
        path = self._write("a.md", "RAISE:AssertionError:simulated structural failure")

        with self.assertRaises(AssertionError):
            self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        with self.assertRaises(AssertionError) as ctx:
            self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 1)
        self.assertIn("simulated structural failure", str(ctx.exception))

    def test_cacheable_failure_reattempts_after_content_change(self) -> None:
        path = self._write("a.md", "RAISE:AssertionError:first failure")
        with self.assertRaises(AssertionError):
            self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        path.write_text("now valid", encoding="utf-8")
        result = self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 2)
        self.assertEqual(result.text, "now valid")

    def test_validation_error_is_a_cacheable_failure_type(self) -> None:
        self.assertIn(ValidationError, CACHEABLE_ERROR_TYPES)

    def test_non_cacheable_failure_is_not_cached_and_is_reinvoked_on_unchanged_content(self) -> None:
        path = self._write("a.md", "RAISE:RuntimeError:not a cacheable failure type")

        with self.assertRaises(RuntimeError):
            self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        with self.assertRaises(RuntimeError):
            self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 2)

    def test_a_read_failure_before_parse_fn_is_not_cached(self) -> None:
        missing_path = self.tmp_path / "does-not-exist.md"

        with self.assertRaises(OSError):
            self.sut.read(missing_path, self.parser)
        self.assertEqual(self.parser.calls, 0)

        with self.assertRaises(OSError):
            self.sut.read(missing_path, self.parser)
        self.assertEqual(self.parser.calls, 0)


class TestDocCacheInvalidate(unittest.TestCase):
    """Tests for DocCache.invalidate."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sut: DocCache[_FakeDoc] = DocCache()
        self.parser = _CountingParser()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_removes_entry_so_next_read_reinvokes_parse_fn_even_with_unchanged_content(self) -> None:
        path = self._write("a.md", "hello")
        self.sut.read(path, self.parser)

        self.sut.invalidate(path)
        self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 2)

    def test_is_a_no_op_for_a_path_with_no_cached_entry(self) -> None:
        path = self.tmp_path / "never-read.md"

        self.sut.invalidate(path)  # must not raise


class TestDocCacheReconcile(unittest.TestCase):
    """Tests for DocCache.reconcile."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sut: DocCache[_FakeDoc] = DocCache()
        self.parser = _CountingParser()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_drops_cached_path_not_in_live_paths(self) -> None:
        kept_path = self._write("kept.md", "kept")
        dropped_path = self._write("dropped.md", "dropped")
        self.sut.read(kept_path, self.parser)
        self.sut.read(dropped_path, self.parser)
        self.assertEqual(self.parser.calls, 2)

        self.sut.reconcile([kept_path])

        self.sut.read(dropped_path, self.parser)
        self.assertEqual(self.parser.calls, 3)

    def test_keeps_cached_path_still_present_in_live_paths(self) -> None:
        kept_path = self._write("kept.md", "kept")
        dropped_path = self._write("dropped.md", "dropped")
        self.sut.read(kept_path, self.parser)
        self.sut.read(dropped_path, self.parser)
        self.assertEqual(self.parser.calls, 2)

        self.sut.reconcile([kept_path])

        self.sut.read(kept_path, self.parser)
        self.assertEqual(self.parser.calls, 2)


class TestDocCacheMove(unittest.TestCase):
    """Tests for DocCache.move."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sut: DocCache[_FakeDoc] = DocCache()
        self.parser = _CountingParser()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_moved_entry_survives_as_a_hit_when_new_path_content_is_identical(self) -> None:
        old_path = self._write("old.md", "same content")
        self.sut.read(old_path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        # Simulate a rename: new_path carries byte-for-byte identical content.
        new_path = self._write("new.md", "same content")
        self.sut.move(old_path, new_path)

        result = self.sut.read(new_path, self.parser)

        self.assertEqual(self.parser.calls, 1)
        self.assertEqual(result.text, "same content")

    def test_moved_entry_misses_and_reparses_when_new_path_content_differs(self) -> None:
        old_path = self._write("old.md", "old content")
        self.sut.read(old_path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        new_path = self._write("new.md", "different content")
        self.sut.move(old_path, new_path)

        result = self.sut.read(new_path, self.parser)

        self.assertEqual(self.parser.calls, 2)
        self.assertEqual(result.text, "different content")

    def test_old_path_no_longer_serves_a_cached_hit_after_move(self) -> None:
        old_path = self._write("old.md", "same content")
        self.sut.read(old_path, self.parser)

        new_path = self._write("new.md", "same content")
        self.sut.move(old_path, new_path)

        # old_path's entry is gone; re-reading old_path (still on disk with
        # unchanged content in this test) is a fresh cache miss.
        self.sut.read(old_path, self.parser)
        self.assertEqual(self.parser.calls, 2)

    def test_is_a_no_op_for_an_old_path_with_no_cached_entry(self) -> None:
        old_path = self.tmp_path / "never-read.md"
        new_path = self.tmp_path / "new.md"

        self.sut.move(old_path, new_path)  # must not raise

        self.assertFalse(new_path.exists())


class TestDocCacheReset(unittest.TestCase):
    """Tests for DocCache.reset."""

    def setUp(self) -> None:
        self.tmp_path = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.sut: DocCache[_FakeDoc] = DocCache()
        self.parser = _CountingParser()

    def _write(self, name: str, content: str) -> Path:
        path = self.tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_clears_every_entry_so_next_read_reinvokes_parse_fn(self) -> None:
        path = self._write("a.md", "hello")
        self.sut.read(path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        self.sut.reset()
        self.sut.read(path, self.parser)

        self.assertEqual(self.parser.calls, 2)


if __name__ == "__main__":
    unittest.main()
