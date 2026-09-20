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

"""Unit tests for the content-hash-validated in-memory embedding cache (feat-134, Phase 1, REQ-004).

Covers ACC-005 (a read against an unchanged document is a cache hit: the
``embed_fn`` is not re-invoked and the same vector object is returned), ACC-006
(a content change invalidates the entry: the ``embed_fn`` runs again), and the
``invalidate``/``move``/``reset`` lifecycle operations the generic ``delete``
and ``set_feat_id`` tools wire into (ACC-011 -- the tool-level wiring itself is
tested in ``test_find_related.py``).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from biz.dfch.specmgr.general.tools._embedding_cache import (
    EmbeddingCache,
    invalidate_embedding_cache,
    move_embedding_cache,
    read_embedding,
    reset_embedding_cache,
)


class _CountingEmbedFn:
    """An ``embed_fn`` that records how many times it ran and returns the text length as the vector."""

    def __init__(self) -> None:
        self.calls: int = 0
        self.inputs: list[str] = []

    def __call__(self, text: str) -> list[float]:
        self.calls += 1
        self.inputs.append(text)
        result: list[float] = [float(len(text))]
        return result


class EmbeddingCacheTestCase(unittest.TestCase):
    """Common fixture: a temp file and a fresh :class:`EmbeddingCache` per test."""

    def setUp(self) -> None:
        self.dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.dir / "doc.md"
        self.path.write_text("initial content", encoding="utf-8")
        self.cache = EmbeddingCache()
        self.fn = _CountingEmbedFn()


class TestRead(EmbeddingCacheTestCase):
    """ACC-005/ACC-006: hit on unchanged content, recompute on changed content."""

    def test_miss_then_hit_returns_same_vector_without_reembedding(self) -> None:
        first = self.cache.read("req", self.path, self.fn)
        second = self.cache.read("req", self.path, self.fn)

        self.assertEqual(self.fn.calls, 1)  # the second read is a hit
        self.assertIs(second, first)  # the same stored array object is returned
        self.assertEqual(list(first), [float(len("initial content"))])

    def test_content_change_recomputes(self) -> None:
        self.cache.read("req", self.path, self.fn)
        self.path.write_text("different content now", encoding="utf-8")

        second = self.cache.read("req", self.path, self.fn)

        self.assertEqual(self.fn.calls, 2)  # the changed hash forces one re-embed
        self.assertEqual(list(second), [float(len("different content now"))])

    def test_embed_fn_receives_the_exact_text_read(self) -> None:
        self.cache.read("req", self.path, self.fn)

        self.assertEqual(self.fn.inputs, ["initial content"])

    def test_different_domains_same_path_are_separate_entries(self) -> None:
        self.cache.read("req", self.path, self.fn)
        self.cache.read("gol", self.path, self.fn)

        self.assertEqual(self.fn.calls, 2)
        self.assertEqual(len(self.cache._entries), 2)  # pylint: disable=protected-access

    def test_path_is_normalized_to_resolved_form(self) -> None:
        self.cache.read("req", self.path, self.fn)

        keys = list(self.cache._entries)  # pylint: disable=protected-access
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0][1], self.path.resolve())

    def test_embed_failure_is_not_cached(self) -> None:
        def failing(text: str) -> Any:
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            self.cache.read("req", self.path, failing)

        self.assertEqual(len(self.cache._entries), 0)  # pylint: disable=protected-access
        self.cache.read("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 1)  # a later read still computes fresh


class TestInvalidate(EmbeddingCacheTestCase):
    """ACC-011 (cache half): ``invalidate`` drops the entry; a later read recomputes."""

    def test_invalidate_drops_the_entry(self) -> None:
        self.cache.read("req", self.path, self.fn)
        self.cache.invalidate("req", self.path)

        self.assertEqual(len(self.cache._entries), 0)  # pylint: disable=protected-access
        self.cache.read("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 2)

    def test_invalidate_missing_key_is_a_no_op(self) -> None:
        self.cache.invalidate("req", self.path)  # nothing was ever read

        self.assertEqual(len(self.cache._entries), 0)  # pylint: disable=protected-access
        self.cache.read("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 1)


class TestMove(EmbeddingCacheTestCase):
    """ACC-011 (cache half): ``move`` relocates the entry to the new path (a rename)."""

    def test_move_relocates_the_entry_without_reembedding(self) -> None:
        new_path = self.dir / "renamed.md"
        new_path.write_text("initial content", encoding="utf-8")  # same content: a real rename
        self.cache.read("req", self.path, self.fn)

        self.cache.move("req", self.path, new_path)

        self.assertNotIn(("req", self.path.resolve()), self.cache._entries)  # pylint: disable=protected-access
        self.assertIn(("req", new_path.resolve()), self.cache._entries)  # pylint: disable=protected-access
        self.assertEqual(self.fn.calls, 1)  # the move itself never re-embeds
        self.cache.read("req", new_path, self.fn)
        self.assertEqual(self.fn.calls, 1)  # same content hash: a hit at the new path

    def test_move_missing_old_key_is_a_no_op(self) -> None:
        new_path = self.dir / "renamed.md"

        self.cache.move("req", self.path, new_path)

        self.assertEqual(len(self.cache._entries), 0)  # pylint: disable=protected-access

    def test_move_keeps_domain_unchanged(self) -> None:
        new_path = self.dir / "renamed.md"
        self.cache.read("feat", self.path, self.fn)

        self.cache.move("feat", self.path, new_path)

        self.assertIn(("feat", new_path.resolve()), self.cache._entries)  # pylint: disable=protected-access


class TestReset(EmbeddingCacheTestCase):
    """The test-only ``reset`` hook clears every entry."""

    def test_reset_clears_all_entries(self) -> None:
        self.cache.read("req", self.path, self.fn)
        self.cache.read("gol", self.path, self.fn)

        self.cache.reset()

        self.assertEqual(len(self.cache._entries), 0)  # pylint: disable=protected-access


class TestModuleLevelWrappers(unittest.TestCase):
    """The public ``read_embedding``/``invalidate``/``move``/``reset`` wrappers over the global singleton."""

    def setUp(self) -> None:
        self.dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.dir / "doc.md"
        self.path.write_text("wrapper content", encoding="utf-8")
        self.fn = _CountingEmbedFn()
        reset_embedding_cache()

    def tearDown(self) -> None:
        reset_embedding_cache()

    def test_read_embedding_then_invalidate_then_reread(self) -> None:
        first = read_embedding("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 1)

        invalidate_embedding_cache("req", self.path)

        second = read_embedding("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 2)
        self.assertEqual(list(first), list(second))

    def test_move_embedding_cache(self) -> None:
        new_path = self.dir / "renamed.md"
        new_path.write_text("wrapper content", encoding="utf-8")
        read_embedding("req", self.path, self.fn)

        move_embedding_cache("req", self.path, new_path)

        read_embedding("req", new_path, self.fn)
        self.assertEqual(self.fn.calls, 1)  # the moved entry hit at the new path

    def test_reset_embedding_cache(self) -> None:
        read_embedding("req", self.path, self.fn)

        reset_embedding_cache()

        read_embedding("req", self.path, self.fn)
        self.assertEqual(self.fn.calls, 2)


if __name__ == "__main__":
    unittest.main()
