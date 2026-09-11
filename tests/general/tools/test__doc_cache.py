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

"""Tests for ``general.tools._doc_cache`` (feat-107-doc-cache, Phase 2/Phase 6).

Phase 6 changed :meth:`DocCache.read`'s ``parse_fn`` contract from
``Callable[[Path], _DocT]`` (path in) to ``Callable[[str], _DocT]`` (text
in, REQ-007) -- every fake ``parse_fn`` in this module (:class:`_CountingParser`
in particular) now receives already-read text, not a ``Path`` it would have
to re-read itself.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from biz.dfch.specmgr.general.tools._doc_cache import CACHEABLE_ERROR_TYPES, DocCache


class _FakeDoc:
    """Minimal stand-in for a parsed document, holding just the text it was parsed from."""

    def __init__(self, text: str) -> None:
        self.text = text


class _FakeModelDoc(BaseModel):
    """A ``pydantic.BaseModel``-based stand-in, so :meth:`DocCache.read`'s copy-on-hit path
    (REQ-008, Phase 6) -- which only applies to a ``BaseModel`` result -- is exercised."""

    text: str


class _CountingParser:
    """A counting fake ``parse_fn``: increments ``calls`` each time it is actually invoked.

    Receives already-read text (the ``parse_fn`` contract Phase 6 fixed,
    REQ-007) and raises ``raise_type`` (with ``raise_message``) instead of
    returning a document when the text equals a configured trigger
    sentinel, so a test can flip a file's content to simulate a parse
    failure vs. a parse success.
    """

    def __init__(self, doc_cls: type[_FakeDoc] | type[_FakeModelDoc] = _FakeDoc) -> None:
        self.calls = 0
        self.doc_cls = doc_cls

    def __call__(self, text: str) -> _FakeDoc | _FakeModelDoc:
        self.calls += 1
        if text.startswith("RAISE:"):
            _, type_name, message = text.split(":", 2)
            raise _EXCEPTION_TYPES_BY_NAME[type_name](message)
        return self.doc_cls(text=text)


_EXCEPTION_TYPES_BY_NAME: dict[str, type[Exception]] = {
    "AssertionError": AssertionError,
    "RuntimeError": RuntimeError,
    "OSError": OSError,
}


def _make_marked_yaml_error() -> yaml.YAMLError:
    """Build a real ``yaml.error.MarkedYAMLError`` by actually parsing deliberately malformed YAML.

    A genuine, unmocked construction (mirroring ``tests/req/tools/test_doc_cache_wiring.py``'s
    own ``_MALFORMED_YAML_FRONTMATTER_DOC`` fixture text) rather than a hand-built instance, so
    :func:`~biz.dfch.specmgr.general.tools._doc_cache._fresh_exception`'s ``MarkedYAMLError``
    reconstruction branch is exercised against the exact same shape of exception every real
    ``parse_<domain>`` failure in this codebase actually raises.
    """
    try:
        yaml.safe_load("[this is not valid yaml because the flow sequence is never closed")
    except yaml.YAMLError as exc:
        assert isinstance(exc, yaml.error.MarkedYAMLError), type(exc)
        return exc
    raise AssertionError("expected yaml.safe_load to raise on malformed YAML")


def _make_validation_error(message: str) -> ValidationError:
    """Build a real ``pydantic.ValidationError`` whose sole error message is ``message``.

    Mirrors the shape ``models.md._frontmatter_parse.enrich_frontmatter_validation_error``
    actually produces (a ``pydantic_core.PydanticCustomError``-wrapped message, not a
    builtin-kind one), so :func:`_fresh_exception`'s ``ValidationError`` reconstruction
    branch is exercised the same way it would be against this codebase's own real
    ``parse_<domain>`` failures.
    """
    line_errors: list[InitErrorDetails] = [
        InitErrorDetails(type=PydanticCustomError("fake_error", message), loc=("field",), input="bad-value")
    ]
    result = ValidationError.from_exception_data("FakeModel", line_errors)
    return result


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

    def test_acc009_parse_fn_receives_the_exact_text_that_was_hashed_no_second_file_read(self) -> None:
        """ACC-009: hash and parsed result always originate from one read.

        Regression test for the Phase 1-5 TOCTOU race (REQ-007): a fake
        ``parse_fn`` that mutates ``path`` on disk *after* being called
        (simulating a second, independent read that would observe
        different content than what was hashed) must have no effect on
        the result, since ``parse_fn`` no longer receives ``path`` at all
        -- only the text already read and hashed for this call.
        """
        path = self._write("a.md", "original content")
        observed_texts: list[str] = []

        def _mutate_after_call(text: str) -> _FakeDoc:
            observed_texts.append(text)
            # If parse_fn still received `path` and re-read it itself (the pre-Phase-6
            # shape), this on-disk mutation would let a second, independent read inside
            # parse_fn observe different content than what was just hashed above.
            path.write_text("mutated-by-parse-fn-side-effect", encoding="utf-8")
            return _FakeDoc(text=text)

        result = self.sut.read(path, _mutate_after_call)

        self.assertEqual(observed_texts, ["original content"])
        self.assertEqual(result.text, "original content")

    def test_acc010_two_reads_of_the_same_unchanged_path_return_distinct_object_instances(self) -> None:
        """ACC-010: two DocCache.read calls for the same path return distinct instances (REQ-008).

        Uses a ``pydantic.BaseModel``-based fake document, since the
        copy-on-hit fix only applies to a ``BaseModel`` result.
        """
        model_parser = _CountingParser(doc_cls=_FakeModelDoc)
        model_cache: DocCache[_FakeModelDoc] = DocCache()
        path = self._write("a.md", "hello")

        first = model_cache.read(path, model_parser)
        second = model_cache.read(path, model_parser)

        self.assertEqual(model_parser.calls, 1)  # still just one real parse -- the second call is a cache hit
        self.assertIsNot(first, second)
        self.assertEqual(first, second)  # equal in content, just not the same object

        # Mutating the object returned by one call must not affect the object returned by another.
        first.text = "mutated"
        self.assertEqual(second.text, "hello")

    def test_acc013_two_hits_on_a_failed_entry_raise_is_distinct_exception_objects(self) -> None:
        """ACC-013: two hits on the same cached failure raise `is`-distinct exceptions (REQ-011).

        Same type, same message -- but never the same object -- on every
        hit, for each of the three CACHEABLE_ERROR_TYPES.
        """
        path = self._write("a.md", "RAISE:AssertionError:simulated structural failure")

        with self.assertRaises(AssertionError) as ctx1:
            self.sut.read(path, self.parser)
        with self.assertRaises(AssertionError) as ctx2:
            self.sut.read(path, self.parser)

        self.assertIsNot(ctx1.exception, ctx2.exception)
        self.assertIs(type(ctx1.exception), type(ctx2.exception))
        self.assertEqual(str(ctx1.exception), str(ctx2.exception))

    def test_acc013_validation_error_hits_are_also_is_distinct_with_equal_type_and_message(self) -> None:
        """ACC-013, ValidationError variant: the special-cased reconstruction path (REQ-011)."""
        model_cache: DocCache[_FakeModelDoc] = DocCache()
        path = self._write("a.md", "irrelevant text -- the fake parser always raises")

        def _always_raises_validation_error(_text: str) -> _FakeModelDoc:
            raise _make_validation_error("simulated field failure")

        with self.assertRaises(ValidationError) as ctx1:
            model_cache.read(path, _always_raises_validation_error)
        with self.assertRaises(ValidationError) as ctx2:
            model_cache.read(path, _always_raises_validation_error)

        self.assertIsNot(ctx1.exception, ctx2.exception)
        self.assertIs(type(ctx1.exception), type(ctx2.exception))
        self.assertEqual(str(ctx1.exception), str(ctx2.exception))

    def test_acc019_marked_yaml_error_hits_are_also_is_distinct_with_equal_type_and_message(self) -> None:
        """ACC-019 (feat-107-doc-cache Phase 8): the third CACHEABLE_ERROR_TYPES member --
        ``yaml.error.MarkedYAMLError`` -- round-trips a cache hit the same way ACC-013 already
        proves for AssertionError/ValidationError. Closes the gap where `_fresh_exception`'s own
        docstring claimed all three CACHEABLE_ERROR_TYPES members are "verified to round-trip ...
        via ACC-013's regression tests" when only two of the three actually were.
        """
        model_cache: DocCache[_FakeModelDoc] = DocCache()
        path = self._write("a.md", "irrelevant text -- the fake parser always raises")

        def _always_raises_marked_yaml_error(_text: str) -> _FakeModelDoc:
            raise _make_marked_yaml_error()

        with self.assertRaises(yaml.YAMLError) as ctx1:
            model_cache.read(path, _always_raises_marked_yaml_error)
        with self.assertRaises(yaml.YAMLError) as ctx2:
            model_cache.read(path, _always_raises_marked_yaml_error)

        self.assertIsNot(ctx1.exception, ctx2.exception)
        self.assertIs(type(ctx1.exception), type(ctx2.exception))
        self.assertEqual(str(ctx1.exception), str(ctx2.exception))


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

    def test_acc011_invalidate_via_a_relative_form_of_an_already_cached_resolved_path(self) -> None:
        """ACC-011: read/invalidate given two different-but-equivalent Path forms hit one entry.

        The path is written under ``self.tmp_path`` (already absolute);
        ``read`` is called with its resolved form, ``invalidate`` with an
        unresolved relative-looking form built by walking through ``..``
        segments -- both must address the exact same normalized key.
        """
        path = self._write("a.md", "hello")
        resolved_path = path.resolve()
        equivalent_path = path.parent / ".." / path.parent.name / path.name

        self.sut.read(resolved_path, self.parser)
        self.assertEqual(self.parser.calls, 1)

        self.sut.invalidate(equivalent_path)
        self.sut.read(resolved_path, self.parser)

        self.assertEqual(self.parser.calls, 2)  # invalidate actually hit the same entry, forcing a re-parse


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

    def test_acc011_reconcile_matches_an_equivalent_unresolved_live_path_form(self) -> None:
        """ACC-011: reconcile's live_paths are normalized the same way read's key is."""
        kept_path = self._write("kept.md", "kept")
        self.sut.read(kept_path.resolve(), self.parser)
        self.assertEqual(self.parser.calls, 1)

        equivalent_live_path = kept_path.parent / ".." / kept_path.parent.name / kept_path.name
        self.sut.reconcile([equivalent_live_path])

        self.sut.read(kept_path.resolve(), self.parser)
        self.assertEqual(self.parser.calls, 1)  # still a hit -- reconcile recognized the equivalent form


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

    def test_acc011_move_accepts_an_equivalent_unresolved_old_path_form(self) -> None:
        """ACC-011: move's old_path/new_path are normalized the same way read's key is."""
        old_path = self._write("old.md", "same content")
        self.sut.read(old_path.resolve(), self.parser)
        self.assertEqual(self.parser.calls, 1)

        new_path = self._write("new.md", "same content")
        equivalent_old_path = old_path.parent / ".." / old_path.parent.name / old_path.name
        self.sut.move(equivalent_old_path, new_path)

        result = self.sut.read(new_path.resolve(), self.parser)
        self.assertEqual(self.parser.calls, 1)  # still a hit -- move recognized the equivalent old_path form
        self.assertEqual(result.text, "same content")


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
