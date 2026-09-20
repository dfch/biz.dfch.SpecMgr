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

"""The real, non-mocked ``fastembed``/``bge-small`` backend test (feat-134, ACC-008).

Gated behind the ``embedding_model`` pytest marker and excluded from every default
pytest invocation (CI matrix step and the pre-commit hook) by ``pyproject.toml``'s
``addopts = '-m "not embedding_model"'``. Developers opt in locally with
``pytest -m embedding_model``. This is the ONLY similarity test CI excludes.

**Precondition:** the ``BAAI/bge-small-en-v1.5`` model must be downloadable or
already present in the local Hugging Face cache (first use downloads it). The test
itself is fully self-contained -- it seeds its own temp fixture documents (no
dependence on the repo's ``docs/`` tree, which differs across checkouts) -- and
asserts end-to-end ranking, including **mid-document retrieval of a >512-token
document**: a long requirement whose distinctive phrase sits in the *middle* of its
body (past the model's 512-token truncation point) is retrieved by querying that
phrase, proving the chunk + mean-pool strategy (REQ-010) works on the real backend.
It also asserts that the backend's native ``numpy`` arrays flow through the pure
ranking without an ``AssertionError`` and that a hit ``score`` is a plain Python
``float`` (the two Phase 3 real-backend fixes).
"""

from __future__ import annotations

import unittest

import pytest

from biz.dfch.specmgr.general.models import SimilarityHit
from biz.dfch.specmgr.general.tools._embedding_cache import _cache as embedding_cache_singleton
from biz.dfch.specmgr.general.tools.find_similar_text import find_similar_text

from ._similarity_helpers import _REQ_TEMPLATE, SimilarityTestCase

#: The distinctive phrase planted in the MIDDLE of the long document; the query.
_DISTINCTIVE_PHRASE = "zephyr quasar calibration manifold tolerates thermal drift"

#: Two semantically unrelated fillers (hydraulic fixtures / database indexing) that
#: bracket the distinctive phrase so it lands in a middle chunk, well past the model's
#: 512-token (~2000-character) truncation point.
_FILLER_HYDRAULIC = (
    "The hydraulic piston assembly requires torque verification at each fitting before the "
    "test stand is pressurized to its rated working load. "
) * 40
_FILLER_DATABASE = (
    "Database index selection depends on query plan cost estimation and the statistics "
    "gathered from recent transactional workloads. "
) * 40

_LONG_DESCRIPTION = _FILLER_HYDRAULIC + "\n\nThe " + _DISTINCTIVE_PHRASE + ".\n\n" + _FILLER_DATABASE

_LONG_TITLE = "Thermal Calibration Requirement"


def _long_req_body() -> str:
    """A parse-safe ``req`` body whose ``## Description`` is long (>512 tokens) with the phrase mid-body."""
    return _REQ_TEMPLATE.format(title=_LONG_TITLE, description=_LONG_DESCRIPTION)


@pytest.mark.embedding_model
class TestRealBackendSimilarity(SimilarityTestCase):
    """ACC-008: end-to-end ranking on the real ``fastembed``/``bge-small`` backend."""

    def test_mid_document_retrieval_of_a_long_document(self) -> None:
        from biz.dfch.specmgr.req.tools.create_req import create_req

        create_req(_long_req_body())
        self.seed_req("Kitchen Wiring Requirement", "The kitchen appliance wiring gauge must match the breaker rating.")
        self.seed_req(
            "Irrigation Schedule Requirement", "The garden irrigation schedule runs before dawn each weekday."
        )

        result = find_similar_text(query=_DISTINCTIVE_PHRASE)

        self.assertIsInstance(result, list)
        for hit in result:
            self.assertIsInstance(hit, SimilarityHit)
        self.assertGreaterEqual(len(result), 3)
        self.assertEqual(result[0].title, _LONG_TITLE)  # the long doc ranks #1 via its MIDDLE content
        self.assertIsInstance(result[0].score, float)
        self.assertIs(type(result[0].score), float)  # a plain Python float, not a numpy scalar
        # The long doc (chunked) must outscore both short, unrelated docs.
        self.assertGreater(result[0].score, result[1].score)
        self.assertGreater(result[0].score, result[2].score)

        # The backend's native arrays flow through the pure ranking without an AssertionError:
        # at least one cached candidate vector is a numpy.ndarray (the short docs take the
        # single-embed fast path and store the backend's own array unconverted).
        import numpy as np

        vectors = [vector for _hash, vector in embedding_cache_singleton._entries.values()]  # pylint: disable=protected-access
        self.assertTrue(any(isinstance(vector, np.ndarray) for vector in vectors))

    def test_long_document_is_actually_chunked(self) -> None:
        # Guard the premise of the retrieval test: the long body exceeds the fast-path
        # threshold (so it is chunked, not truncated) and the phrase sits past the first
        # chunk's boundary (mid-document).
        from biz.dfch.specmgr.general.tools._embedding import _CHUNK_SIZE

        body = _long_req_body()

        self.assertGreater(len(body), _CHUNK_SIZE)
        self.assertGreater(body.index(_DISTINCTIVE_PHRASE), _CHUNK_SIZE)


if __name__ == "__main__":
    unittest.main()
