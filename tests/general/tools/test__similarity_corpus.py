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

"""Unit tests for candidate enumeration and source resolution (feat-134, Phase 2, Task 2.1).

Covers ACC-007 (``adr`` never appears as a candidate and is rejected as a
``target_types``/source ``type``), ACC-015 (bad ``target_types``/``type``/``id``
are a ``ValueError`` before any filesystem access; a missing source is the
domain's own ``XNotFoundError``), and the per-candidate parseability / marker-row
decision (REQ-009, exercised at the unit level here; the tool-level marker rows
are asserted in ``test_find_related.py``/``test_find_similar_text.py``).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._listing import FAILED_TO_PARSE_MARKER
from biz.dfch.specmgr.general.tools._similarity_corpus import (
    candidate_similarity_text,
    is_parseable,
    iter_candidate_paths,
    resolve_source,
)
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError

from ._similarity_helpers import _FEAT_MINIMAL_BODY, _UNPARSEABLE_REQ, SimilarityTestCase

#: A well-formed but non-existent canonical UUID (the unknown-id case).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"


class TestIterCandidatePaths(SimilarityTestCase):
    """ACC-007: the enumeration walks the target domains and never yields ``adr``."""

    def test_default_walk_yields_seeded_domains_in_registry_order(self) -> None:
        req_fm = self.seed_req("Req Doc", "alpha")
        self.seed_gol("Gol Doc", "beta")
        feat_fm = self.seed_feat(_FEAT_MINIMAL_BODY)

        pairs = list(iter_candidate_paths(None))

        domains = [domain for domain, _ in pairs]
        self.assertIn("req", domains)
        self.assertIn("gol", domains)
        self.assertIn("feat", domains)
        self.assertNotIn("adr", domains)
        # Registry order among the seeded domains: req (index 0) < gol (5) < feat (9).
        self.assertEqual([d for d in domains if d in ("req", "gol", "feat")], ["req", "gol", "feat"])
        self.assertEqual(len(pairs), 3)
        req_pair = [p for d, p in pairs if d == "req"][0]
        self.assertEqual(req_pair, self.path_for_id("req", req_fm.id))
        feat_pair = [p for d, p in pairs if d == "feat"][0]
        self.assertEqual(feat_pair, self.feat_dir / feat_fm.id / "README.md")

    def test_target_types_restricts_the_walk(self) -> None:
        self.seed_req("Req Doc", "alpha")
        self.seed_gol("Gol Doc", "beta")

        pairs = list(iter_candidate_paths(["gol"]))

        self.assertEqual([domain for domain, _ in pairs], ["gol"])

    def test_target_types_deduplicate_and_preserve_order(self) -> None:
        self.seed_req("Req Doc", "alpha")
        self.seed_gol("Gol Doc", "beta")

        pairs = list(iter_candidate_paths(["gol", "req", "gol"]))

        self.assertEqual([domain for domain, _ in pairs], ["gol", "req"])

    def test_missing_base_dir_yields_nothing_for_that_domain(self) -> None:
        # No documents seeded anywhere: every domain's base dir is absent, so the walk is empty.
        pairs = list(iter_candidate_paths(None))

        self.assertEqual(pairs, [])


class TestIterCandidatePathsRejection(SimilarityTestCase):
    """ACC-007/ACC-015: a bad ``target_types`` entry is a ``ValueError`` before any filesystem access."""

    def _nonexistent_docs_dir(self) -> Any:
        missing = Path(self.enterContext(tempfile.TemporaryDirectory())) / "does-not-exist"
        return mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(missing)})

    def test_adr_target_rejected_before_filesystem_access(self) -> None:
        with self._nonexistent_docs_dir():
            with self.assertRaises(ValueError) as ctx:
                list(iter_candidate_paths(["adr"]))
        self.assertIn("adr", str(ctx.exception))

    def test_unknown_target_rejected_before_filesystem_access(self) -> None:
        with self._nonexistent_docs_dir():
            with self.assertRaises(ValueError) as ctx:
                list(iter_candidate_paths(["bogus"]))
        self.assertIn("bogus", str(ctx.exception))


class TestResolveSource(SimilarityTestCase):
    """ACC-007/ACC-015: source resolution reuses the registry + path-safety guards."""

    def test_resolves_a_valid_source(self) -> None:
        fm = self.seed_req("Source Doc", "alpha")

        type_, path, doc = resolve_source("req", fm.id)

        self.assertEqual(type_, "req")
        self.assertEqual(path, self.path_for_id("req", fm.id))
        self.assertTrue(path.exists())
        self.assertEqual(doc.frontmatter.id, fm.id)

    def test_missing_source_raises_domain_not_found(self) -> None:
        self.seed_req("Some Doc", "alpha")  # a real doc exists, but not this id

        with self.assertRaises(ReqNotFoundError):
            resolve_source("req", _MISSING_UUID)

    def test_adr_source_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_source("adr", _MISSING_UUID)

    def test_unknown_source_type_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_source("bogus", _MISSING_UUID)

    def test_wrong_format_id_rejected(self) -> None:
        # A feat-NNN-slug is not a valid req id.
        with self.assertRaises(ValueError):
            resolve_source("req", "feat-36-delete")

    def test_traversal_id_rejected_before_filesystem_access(self) -> None:
        missing = Path(self.enterContext(tempfile.TemporaryDirectory())) / "does-not-exist"
        with mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(missing)}):
            with self.assertRaises(ValueError):
                resolve_source("req", "../x")


class TestIsParseable(SimilarityTestCase):
    """REQ-009: the per-candidate parseability decision runs the domain's own text parser."""

    def test_valid_document_is_parseable(self) -> None:
        fm = self.seed_req("Parseable Doc", "alpha")
        text = self.path_for_id("req", fm.id).read_text(encoding="utf-8")

        self.assertTrue(is_parseable("req", text))

    def test_malformed_frontmatter_is_not_parseable(self) -> None:
        self.assertFalse(is_parseable("req", _UNPARSEABLE_REQ))


class TestCandidateSimilarityText(SimilarityTestCase):
    """REQ-005/REQ-009: parseable documents yield metadata, unparseable ones yield the marker row."""

    def test_parseable_yields_title_id_status_and_embedding_text(self) -> None:
        fm = self.seed_req("Metadata Doc", "alpha beta gamma")
        text = self.path_for_id("req", fm.id).read_text(encoding="utf-8")

        result = candidate_similarity_text("req", text)

        self.assertEqual(result.title, "Metadata Doc")
        self.assertEqual(result.id_, fm.id)
        self.assertEqual(result.status, "draft")
        self.assertIn("Metadata Doc", result.embedding_text)
        self.assertIn("alpha beta gamma", result.embedding_text)

    def test_unparseable_yields_marker_row_with_full_raw_text(self) -> None:
        result = candidate_similarity_text("req", _UNPARSEABLE_REQ)

        self.assertEqual(result.title, FAILED_TO_PARSE_MARKER)
        self.assertEqual(result.status, FAILED_TO_PARSE_MARKER)
        self.assertIsNone(result.id_)
        self.assertEqual(result.embedding_text, _UNPARSEABLE_REQ)


if __name__ == "__main__":
    unittest.main()
