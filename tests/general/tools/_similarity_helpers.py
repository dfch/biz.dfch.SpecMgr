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

"""Shared fixtures for the feat-134 similarity-engine test modules.

Not itself a ``test_*.py`` module -- imported by the individual
``test__<module>.py`` / ``test_find_<tool>.py`` files under this directory so
the deterministic fake :class:`FakeProvider`, the ``fastembed`` import
boundaries (missing-extra / model-load-failure simulation), and the
temp-dir / env-var / cache-reset fixture are not duplicated across them.

**Determinism contract.** :class:`FakeProvider` maps each input to an
L2-normalized bag-of-*whole-words* vector over the fixed :data:`VOCAB`
vocabulary, so every expected cosine in the test suite is hand-computable
(no real model, no network, no ``numpy``). The document bodies the seed
helpers write keep their vocabulary words out of every structural section
(title, EARS statement, the ``## Characteristics``/``## Level``/``## Source``
words), so a document's vector is determined solely by the words its seed
call places in the free-text section.
"""

from __future__ import annotations

import math
import os
import re
import sys
import tempfile
import textwrap
import types
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.tools import _embedding as embedding_module
from biz.dfch.specmgr.general.tools._embedding import reset_default_provider
from biz.dfch.specmgr.general.tools._embedding_cache import reset_embedding_cache
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR

#: The fixed vocabulary the fake provider scores against, in vector order.
VOCAB: tuple[str, ...] = ("alpha", "beta", "gamma")

#: The ``fastembed`` module name (and its submodule prefix) the import
#: boundaries simulate.
_FASTEMBED = "fastembed"


def _whole_word_count(text: str, word: str) -> int:
    """Count whole-word occurrences of ``word`` in ``text`` (case-insensitive)."""
    pattern = re.compile(r"\b" + re.escape(word) + r"\b")
    result = len(pattern.findall(text.lower()))
    return result


class FakeProvider:
    """A deterministic, call-counting :class:`EmbeddingProvider` fake.

    Attributes:
        vocab: The whole-word vocabulary the vectors score against.
        raise_after: When set, the :meth:`embed` call that would exceed this
            many *inputs* raises (a simulated mid-warmup provider failure);
            ``None`` (the default) never raises.
        embed_calls: Total document-side inputs handed to :meth:`embed`.
        embed_query_calls: Total query-side inputs handed to :meth:`embed_query`.
        embed_inputs: The document-side input strings, in call order.
        embed_query_inputs: The query-side input strings, in call order.
    """

    def __init__(self, vocab: tuple[str, ...] = VOCAB, *, raise_after: int | None = None) -> None:
        assert isinstance(vocab, tuple)
        assert all(isinstance(word, str) and word for word in vocab)
        assert raise_after is None or (isinstance(raise_after, int) and raise_after >= 0)
        self.vocab: tuple[str, ...] = vocab
        self.raise_after: int | None = raise_after
        self.embed_calls: int = 0
        self.embed_query_calls: int = 0
        self.embed_inputs: list[str] = []
        self.embed_query_inputs: list[str] = []

    def vector(self, text: str) -> list[float]:
        """The L2-normalized whole-word count vector of ``text`` over :attr:`vocab`."""
        counts = [_whole_word_count(text, word) for word in self.vocab]
        norm = math.sqrt(sum(count * count for count in counts))
        if norm == 0.0:
            result: list[float] = [0.0] * len(self.vocab)
            return result
        result = [count / norm for count in counts]
        return result

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed document-side inputs (one normalized vector per input)."""
        assert isinstance(texts, list), type(texts)
        self.embed_calls += len(texts)
        if self.raise_after is not None and self.embed_calls > self.raise_after:
            raise RuntimeError("simulated provider failure (raise_after)")
        self.embed_inputs.extend(texts)
        result = [self.vector(text) for text in texts]
        return result

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        """Embed query-side inputs (one normalized vector per input)."""
        assert isinstance(texts, list), type(texts)
        self.embed_query_calls += len(texts)
        self.embed_query_inputs.extend(texts)
        result = [self.vector(text) for text in texts]
        return result


def install_fake_provider(raise_after: int | None = None) -> FakeProvider:
    """Install a fresh :class:`FakeProvider` as the process default provider.

    Sets ``_embedding._default_provider`` directly, so both
    ``_similarity_availability`` and every tool's own ``get_default_provider``
    reference observe it (they all call the one shared function, which reads
    that module global). Tests that need it call this after ``setUp`` has
    already reset the provider to ``None``.
    """
    fake = FakeProvider(raise_after=raise_after)
    embedding_module._default_provider = fake  # pylint: disable=protected-access
    return fake


@contextmanager
def block_fastembed_import() -> Iterator[None]:
    """Simulate the ``similarity`` extra not being installed (REQ-003/ACC-003).

    Removes any cached ``fastembed`` module(s) from ``sys.modules`` and
    installs a ``sys.meta_path`` finder whose ``find_spec`` raises
    ``ImportError`` for ``fastembed`` and its submodules (Python 3.13 removed
    the legacy ``find_module`` hook, so ``find_spec`` is the only seam), so
    ``get_default_provider``'s own lazy ``import fastembed`` fails. Everything
    is restored on exit.
    """
    saved: dict[str, Any] = {
        name: module for name, module in sys.modules.items() if name == _FASTEMBED or name.startswith(_FASTEMBED + ".")
    }
    for name in list(saved):
        del sys.modules[name]

    class _Blocker:
        """A meta-path finder that raises ``ImportError`` for ``fastembed*``."""

        def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> Any:
            if fullname == _FASTEMBED or fullname.startswith(_FASTEMBED + "."):
                raise ImportError(f"blocked import of {fullname!r} (simulating a missing `similarity` extra)")
            result = None
            return result

    blocker = _Blocker()
    sys.meta_path.insert(0, blocker)
    try:
        yield
    finally:
        sys.meta_path.remove(blocker)
        sys.modules.update(saved)


@contextmanager
def fail_fastembed_model_load() -> Iterator[None]:
    """Simulate the extra installed but the model failing to load (ACC-009).

    Installs a stub ``fastembed`` module in ``sys.modules`` whose
    ``TextEmbedding`` constructor raises, so ``get_default_provider``'s import
    succeeds but ``fastembed.TextEmbedding(_DEFAULT_MODEL_NAME)`` does not. The
     previous ``sys.modules["fastembed"]`` entry (if any) is restored on exit.
    """
    saved: Any = sys.modules.get(_FASTEMBED)
    stub = types.ModuleType(_FASTEMBED)

    class _Boom:
        """A stand-in ``TextEmbedding`` whose constructor always fails."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("simulated model load failure")

    stub.TextEmbedding = _Boom  # type: ignore[attr-defined]
    sys.modules[_FASTEMBED] = stub
    try:
        yield
    finally:
        if saved is not None:
            sys.modules[_FASTEMBED] = saved
        else:
            sys.modules.pop(_FASTEMBED, None)


# --- seed helpers (parse-safe, vocabulary-controlled document bodies) ----------

#: A minimal, valid ``req`` body: the vocabulary words live ONLY in the
#: ``## Description`` free-text section; the title, the EARS statement, and
#: every structural word are vocabulary-neutral, so a document's vector is
#: determined solely by its ``description``.
_REQ_TEMPLATE = textwrap.dedent(
    """\
    # {title}

    WHILE the engine is running, THE temperature must be a maximum of 80 °C.

    ## Description

    {description}

    ## Characteristics

    1. Safety

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

#: A minimal, valid ``gol`` body: vocabulary words live ONLY in the top-level
#: goal statement (the paragraph between the H1 and ``## Source``).
_GOL_TEMPLATE = textwrap.dedent(
    """\
    # {title}

    {statement}

    ## Source

    The vehicle program's 2027 market analysis
    """
)

#: A minimal, valid ``dec`` body: vocabulary words live ONLY in the
#: ``## Context and Problem Statement`` section. The now-mandatory
#: ``## Roles and Responsibilities`` (``### Accountable`` single paragraph +
#: ``### Responsible`` bullet list, feat-29-dec-source-roles, GitHub issue
#: #29) and ``## Source`` sections are vocabulary-neutral, so a document's
#: vector is still determined solely by its ``{context}``.
_DEC_TEMPLATE = textwrap.dedent(
    """\
    # {title}

    ## Context and Problem Statement

    {context}

    ## Decision Outcome

    We chose the structured arrangement.

    ## Roles and Responsibilities

    ### Accountable

    The platform architecture lead.

    ### Responsible

    - The order service team.

    ## Source

    The customer dashboard latency incident review meeting.
    """
)

#: A minimal, valid ``feat`` body (the folder-per-document domain); vocabulary-neutral,
#: used to seed a ``feat`` document for the corpus-walk and ``set_feat_id`` tests.
_FEAT_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


#: A vocabulary-neutral ``req`` document whose frontmatter YAML is malformed
#: (an unterminated flow sequence) -- proven to raise ``yaml.YAMLError`` out
#: of ``parse_req`` (any of the three parse-failure channels, REQ-009), so it
#: is an unparseable candidate: a ``<failed to parse>`` marker row,
#: ``id = None``, embedded from its full raw text (which carries no vocabulary
#: words, so its vector is the zero vector).
_UNPARSEABLE_REQ = textwrap.dedent(
    """\
    ---
    id: [this frontmatter flow sequence is never closed
    type: req
    version: 1.0.0
    status: draft
    ---

    # Broken Document

    This document is intentionally broken.
    """
)


class SimilarityTestCase(unittest.TestCase):
    """Common fixture: temp docs/feat dirs, clean cache, reset provider.

    Points ``SPECMGR_DOCS_DIR`` at a temp dir (every flat domain's base dir is
    a subdir of it) and ``SPECMGR_FEAT_DIR`` at its own temp dir (mirroring the
    ``test_delete.py``/``test_set_status.py``/``test_update.py`` fixture
    convention), clears the ``SPECMGR_SIMILARITY_DISABLED`` flag (restoring it
    on teardown if it was set), and resets both the process embedding cache and
    the default-provider singleton in ``setUp``/``tearDown`` so no test
    observes another test's cached entries or provider (the suite runs under
    ``pytest-xdist``/``-n auto``: the real risk is cross-test contamination
    within one worker process).
    """

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), FEAT_DIR_ENV_VAR: str(self.feat_dir)},
            )
        )
        self._saved_disabled = os.environ.pop("SPECMGR_SIMILARITY_DISABLED", None)
        reset_embedding_cache()
        reset_default_provider()
        self.fake: FakeProvider | None = None

    def tearDown(self) -> None:
        reset_embedding_cache()
        reset_default_provider()
        if self._saved_disabled is not None:
            os.environ["SPECMGR_SIMILARITY_DISABLED"] = self._saved_disabled

    def install_fake(self, raise_after: int | None = None) -> FakeProvider:
        """Install a fresh :class:`FakeProvider` as the default provider and remember it."""
        self.fake = install_fake_provider(raise_after)
        return self.fake

    def set_disabled(self, value: str = "1") -> None:
        """Set the presence-based ``SPECMGR_SIMILARITY_DISABLED`` flag to ``value``."""
        os.environ["SPECMGR_SIMILARITY_DISABLED"] = value

    def seed_req(self, title: str, description: str) -> Any:
        """Create a real ``req`` document with vocabulary only in ``## Description``; return its frontmatter."""
        from biz.dfch.specmgr.req.tools.create_req import create_req

        body = _REQ_TEMPLATE.format(title=title, description=description)
        result = create_req(body)
        return result

    def seed_gol(self, title: str, statement: str) -> Any:
        """Create a real ``gol`` document with vocabulary only in the goal statement; return its frontmatter."""
        from biz.dfch.specmgr.gol.tools.create_gol import create_gol

        body = _GOL_TEMPLATE.format(title=title, statement=statement)
        result = create_gol(body)
        return result

    def seed_dec(self, title: str, context: str) -> Any:
        """Create a real ``dec`` document with vocabulary only in its context; return its frontmatter."""
        from biz.dfch.specmgr.dec.tools.create_dec import create_dec

        body = _DEC_TEMPLATE.format(title=title, context=context)
        result = create_dec(body)
        return result

    def seed_feat(self, body: str) -> Any:
        """Create a real ``feat`` document from ``body``; return its frontmatter."""
        from biz.dfch.specmgr.feat.tools.create_feat import create_feat

        result = create_feat(body)
        return result

    def seed_unparseable_req(self, filename: str = "zz-broken.md") -> Path:
        """Write the vocabulary-neutral, malformed-frontmatter ``req`` doc; return its path."""
        from biz.dfch.specmgr.req.tools._paths import req_base_dir

        base_dir = req_base_dir()
        base_dir.mkdir(parents=True, exist_ok=True)
        path = base_dir / filename
        path.write_text(_UNPARSEABLE_REQ, encoding="utf-8")
        result = path
        return result

    def path_for_id(self, domain: str, doc_id: str) -> Path:
        """The on-disk path of the parseable ``domain`` document with frontmatter ``id == doc_id``.

        Scans ``<docs_root>/<domain>/*.md`` (the flat domains' shape) and matches the
        frontmatter ``id``; unparseable files (e.g. the malformed-frontmatter seed) are
        skipped. Raises ``AssertionError`` if no parseable document matches.
        """
        import frontmatter

        base_dir = self.docs_root / domain
        for path in sorted(base_dir.glob("*.md")):
            try:
                post = frontmatter.loads(path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 -- an unparseable seed file is simply not the target
                continue
            if post.get("id") == doc_id:
                result = path
                return result
        raise AssertionError(f"no parseable {domain} document with id {doc_id!r} under {base_dir}")
