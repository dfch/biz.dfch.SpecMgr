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

"""Deterministic, tests-space-only ``feat`` fixture-corpus generator (feat-187-list-feat-timeout, Phase 120).

Not itself a ``test_*.py`` module -- imported by ``tests/feat/tools/
test_list_feat_timeout.py`` (ACC-001..005) and by the ACC-009 lifespan test
in ``tests/general/tools/test__similarity_search.py``.

Per the feature's own round-2 review decision (G3): the corpus must only
ever live in the tests space, never in the same directory as the live/prod
``.specmgr/feat`` docs -- it is committed nowhere; :func:`generate_fixture_corpus`
materializes it fresh, directly to disk (bypassing ``create_feat``/the MCP
tool layer entirely -- pure filesystem writes, since several of the
lettered shapes below are deliberately invalid documents ``create_feat``
would reject), into whatever ``base_dir`` the caller points at (typically a
per-test ``tempfile.TemporaryDirectory()`` with ``SPECMGR_FEAT_DIR`` set to
it).

**The corpus shape.** ``num_healthy`` (default 57) plain, healthy,
``_HEALTHY_BODY``-derived folders (varied title/overview text per folder,
simple loop, not byte-identical -- "mirrors the measured profile" is
directional, not a hard byte-count target) plus exactly one folder per
ACC-002 lettered shape (a)-(m) (13 folders) -- 70 folders total with the
defaults, matching ACC-001's ``total == 70`` assertion. Generation itself
is pure, fast, in-process file I/O (a few dozen ``Path.write_text`` calls)
-- well under the 5 s budget ACC-001's own timing assertion excludes it
from.

**The lettered shapes, and the three-tier contract they exercise (REQ-004,
ACC-002):**

- **(a) malformed YAML frontmatter** -- tier 1: fails at the dirty stage's
  own ``parse_frontmatter`` call with a ``yaml.YAMLError``, byte-identical
  to ``get_feat``'s from call one (both stages run the identical call).
- **(b) missing H1** -- tier 2: the body carries no level-1 heading at all;
  the dirty stage's own ``first_h1`` scan returns ``None``, raising a
  dirty-stage-specific ``AssertionError`` that differs from the full-parse
  error until the clean stage passes this file.
- **(c) wrong-shape H1** -- tier 2: a real H1 that fails the
  ``^Feature: .+$`` alias (e.g. ``# My Widget``) -- same convergence shape
  as (b), different dirty-stage message.
- **(d) legacy Requirements shape** -- tier 3: a ``### Requirements``
  bullet missing its ``REQ-NNN: `` prefix. Frontmatter + H1 are both valid,
  so the dirty stage reports this folder as *healthy* until the clean
  stage's full body parse passes it.
- **(e) missing Task List** -- tier 3: the mandatory ``### Task List``
  section is entirely absent.
- **(f) legacy task-item shape** -- tier 3: a ``#### Phase NNN: ...``
  checklist item missing its ``Task NNN.MMM: `` prefix.
- **(g) legacy Updates timestamp form** -- tier 3: an ``### Updates``
  entry heading using a bare date (no time component), failing
  ``UpdateEntry``'s full ISO 8601 date+time alias.
- **(h) raw-HTML inline token** -- tier 3: a bare ``<generic-tag>`` token
  in the ``### Overview`` free text, parsed as ``html_inline`` by
  markdown-it and rejected by the engine's raw-HTML guard (REQ-005) --
  only a full body parse (which this document's dirty stage never
  performs) ever tokenizes the body at all, so this is unreachable by the
  dirty stage by construction.
- **(i) a stray CommonMark list marker leaving unconsumed text** -- tier 3:
  a representative instance of the "text left over after processing all
  fields" defect class (GitHub issue #27; the historical, now-fixed
  ``feat-180-updates`` trigger this letter is named after, per the
  feature's own Design Notes). **Not a byte-for-byte reproduction of
  ``feat-180-updates``'s own historical file shape** -- that document's
  ``UpdateEntry.content`` field has since become immune to this trigger by
  design (feat-180's own "any markdown content" change makes ``content``
  a true catch-all for everything within its own entry's heading-bound
  extent, confirmed empirically against this worktree's current code
  during this phase's own investigation). This fixture instead places an
  equivalent stray, unindented bullet-list fragment directly inside
  ``### Task List``'s own ``#### Phase NNN: ...`` container, immediately
  after its last checked-off task item, separated by an intervening plain
  paragraph (so the fragment forms a genuinely new, separate CommonMark
  list rather than merging into the checklist's own bullet list) -- this
  reliably reproduces the identical failure *class* (an
  ``AssertionError`` naming "text left over after processing all fields"
  for the ``Phase`` container, the same message family the real
  historical defect raised, just scoped one level differently) while
  staying within the still-valid overall document shape every other
  lettered fixture also uses.
- **(j) healthy** -- the baseline: a plain, valid document, healthy at
  every tier, in both the pre- and post-convergence state.
- **(k) setext H1 over a ``===`` underline** -- healthy, not tier 2: both
  ``first_h1`` and markdown-it's own ``h1`` token recognize a setext-style
  H1 identically.
- **(l) H1 only inside a leading fenced code block** -- tier 2: the body's
  *only* ``# Feature: X``-shaped line sits inside a fenced code block;
  both the fence-aware dirty-stage scan and the full markdown-it parse
  correctly treat the document as having no real H1 at all (so, unlike
  (b)/(c), *both* stages fail from call one -- with different message
  text, converging once the clean stage passes it).
- **(m) a 0-3-space-indented ATX H1** -- healthy, not tier 2: CommonMark's
  own indent tolerance (and both scanners' matching tolerance of it) means
  a heading indented by up to 3 spaces is still a genuine H1.

Every lettered document's frontmatter ``id`` matches its own containing
folder name (mirroring a real, correctly-authored feature folder) except
(a), whose frontmatter never successfully parses at all.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from biz.dfch.specmgr.feat.tools._paths import README_FILENAME

__all__ = [
    "SHAPE_LETTERS",
    "FixtureCorpus",
    "generate_fixture_corpus",
    "healthy_id",
    "shape_id",
]

#: Every ACC-002 lettered shape, in order.
SHAPE_LETTERS: tuple[str, ...] = tuple("abcdefghijklm")

#: The lettered shapes' own id prefix (distinct from the healthy bulk filler's own prefix, so
#: neither numbering range ever collides).
_SHAPE_ID_PREFIX = "feat-800-shape-"

#: The healthy bulk filler folders' own id prefix.
_HEALTHY_ID_PREFIX = "feat-700-synthetic-"

#: A fixed frontmatter block template; ``{id}``/``{status}`` are substituted per folder. Every
#: lettered/healthy folder shares the same ``created``/``updated`` timestamps (irrelevant to any
#: ACC-001..005/009 assertion) -- only ``id``/``status`` ever vary.
_FRONTMATTER_TEMPLATE = """\
---
classification: null
created: '2026-08-30T10:00:00.000+02:00'
id: {id}
status: {status}
type: feat
updated: '2026-08-30T10:00:00.000+02:00'
version: 1.0.0
---

"""

#: The malformed-YAML frontmatter block (a) uses instead -- an unterminated flow sequence,
#: proven to raise ``yaml.YAMLError`` from ``parse_frontmatter`` (any of the three cacheable
#: parse-failure channels).
_MALFORMED_FRONTMATTER = """\
---
classification: null
created: '2026-08-30T10:00:00.000+02:00'
id: [this frontmatter flow sequence is never closed
status: planning
type: feat
updated: '2026-08-30T10:00:00.000+02:00'
version: 1.0.0
---

"""

#: The tail every lettered/healthy body shares: a valid ``## Progress`` with a single ``### Updates``
#: entry. Kept separate from ``### Plan`` so individual shapes can vary only their own Plan-side
#: section without duplicating this tail everywhere.
_PROGRESS_TAIL = textwrap.dedent(
    """\
    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

#: The valid ``### Scope``/``### Task List`` section every shape except (e)/(i) shares verbatim.
_NORMAL_SCOPE_AND_TASK_LIST = textwrap.dedent(
    """\
    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 100: Scaffolding

    - [x] Task 100.100: Create branch and package skeleton

    """
)


def _healthy_plan(overview: str, requirement: str = "- REQ-001: The widget must render within 200ms.") -> str:
    """The shared, valid ``## Plan`` body (minus the leading ``# Feature: ...`` H1), parameterized
    by its own ``### Overview``/``### Requirements`` text so the bulk filler folders vary slightly."""
    result = (
        "## Plan\n\n"
        "### Overview\n\n"
        f"{overview}\n\n"
        "### Requirements\n\n"
        f"{requirement}\n\n"
        "### Acceptance Criteria\n\n"
        "- [ ] ACC-001: Render time stays below 200ms.\n\n"
    ) + _NORMAL_SCOPE_AND_TASK_LIST
    return result


def _document(h1_line: str, plan: str, progress: str = _PROGRESS_TAIL) -> str:
    """Join an H1 line, a ``## Plan`` block, and a ``## Progress`` block into one full body."""
    result = f"{h1_line}\n\n{plan}{progress}"
    return result


def _healthy_body(title: str, overview: str) -> str:
    """A plain, valid feature body (letter (j)'s own shape, and every bulk filler folder's)."""
    result = _document(f"# Feature: {title}", _healthy_plan(overview))
    return result


def _shape_body_a() -> str:
    """(a) malformed YAML frontmatter -- the frontmatter block alone is enough; the body never parses."""
    result = _healthy_body("Malformed Frontmatter", "Short description.")
    return result


def _shape_body_b() -> str:
    """(b) missing H1 -- the body starts directly with ``## Plan``, no H1 line at all."""
    result = _healthy_plan("Short description.") + _PROGRESS_TAIL
    return result


def _shape_body_c() -> str:
    """(c) wrong-shape H1 -- a real H1, but without the mandatory ``Feature: `` prefix."""
    result = _document("# Widget Without The Feature Prefix", _healthy_plan("Short description."))
    return result


def _shape_body_d() -> str:
    """(d) legacy Requirements shape -- a bullet missing its ``REQ-NNN: `` prefix."""
    result = _document(
        "# Feature: Legacy Requirements Shape",
        _healthy_plan("Short description.", requirement="- Just a bullet without the REQ marker."),
    )
    return result


def _shape_body_e() -> str:
    """(e) missing Task List -- the mandatory ``### Task List`` section is entirely absent."""
    plan = (
        "## Plan\n\n"
        "### Overview\n\n"
        "Short description.\n\n"
        "### Requirements\n\n"
        "- REQ-001: The widget must render within 200ms.\n\n"
        "### Acceptance Criteria\n\n"
        "- [ ] ACC-001: Render time stays below 200ms.\n\n"
        "### Scope\n\n"
        "#### Included\n\n"
        "- The widget component itself.\n\n"
        "#### Explicitly Out Of Scope\n\n"
        "- Mobile touch gestures.\n\n"
    )
    result = _document("# Feature: Missing Task List", plan)
    return result


def _shape_body_f() -> str:
    """(f) legacy task-item shape -- a checklist item missing its ``Task NNN.MMM: `` prefix."""
    plan = (
        "## Plan\n\n"
        "### Overview\n\n"
        "Short description.\n\n"
        "### Requirements\n\n"
        "- REQ-001: The widget must render within 200ms.\n\n"
        "### Acceptance Criteria\n\n"
        "- [ ] ACC-001: Render time stays below 200ms.\n\n"
        "### Scope\n\n"
        "#### Included\n\n"
        "- The widget component itself.\n\n"
        "#### Explicitly Out Of Scope\n\n"
        "- Mobile touch gestures.\n\n"
        "### Task List\n\n"
        "#### Phase 100: Scaffolding\n\n"
        "- [x] Legacy task item without the Task NNN.MMM prefix\n\n"
    )
    result = _document("# Feature: Legacy Task Item Shape", plan)
    return result


def _shape_body_g() -> str:
    """(g) legacy Updates timestamp form -- a bare date (no time component) Updates heading."""
    result = _document(
        "# Feature: Legacy Updates Timestamp",
        _healthy_plan("Short description."),
        progress=(
            "## Progress\n\n"
            "### Current Status\n\n"
            "**As of 2026-08-30**: free-form narrative.\n\n"
            "### Updates\n\n"
            "#### 2026-08-30 - Paused for review\n\n"
            "Free-form prose describing what happened in this update.\n"
        ),
    )
    return result


def _shape_body_h() -> str:
    """(h) raw-HTML inline token -- a bare ``<generic-tag>`` token in the Overview free text."""
    result = _document(
        "# Feature: Raw HTML Inline Token", _healthy_plan("Short description with a bare <generic-tag> inline token.")
    )
    return result


def _shape_body_i() -> str:
    """(i) a stray CommonMark list marker leaving unconsumed text (see the module docstring's own
    letter (i) entry for why this is a representative, not byte-identical, reproduction)."""
    plan = (
        "## Plan\n\n"
        "### Overview\n\n"
        "Short description.\n\n"
        "### Requirements\n\n"
        "- REQ-001: The widget must render within 200ms.\n\n"
        "### Acceptance Criteria\n\n"
        "- [ ] ACC-001: Render time stays below 200ms.\n\n"
        "### Scope\n\n"
        "#### Included\n\n"
        "- The widget component itself.\n\n"
        "#### Explicitly Out Of Scope\n\n"
        "- Mobile touch gestures.\n\n"
        "### Task List\n\n"
        "#### Phase 100: Scaffolding\n\n"
        "- [x] Task 100.100: Create branch and package skeleton\n\n"
        "Closing remark before the next section begins:\n\n"
        "- stray fragment one, not a new phase heading.\n"
        "- stray fragment two.\n\n"
    )
    result = _document("# Feature: Stray List Marker", plan)
    return result


def _shape_body_j() -> str:
    """(j) healthy baseline -- a plain, valid document."""
    result = _healthy_body("Healthy Baseline", "Short description.")
    return result


def _shape_body_k() -> str:
    """(k) setext H1 -- ``Feature: X`` over a ``===`` underline instead of ``# Feature: X``."""
    result = _document("Feature: Setext Title\n======================", _healthy_plan("Short description."))
    return result


def _shape_body_l() -> str:
    """(l) H1 only inside a leading fenced code block -- no real H1 exists anywhere in the body."""
    fenced = "```\n# Feature: Inside Fence\n```\n\n"
    result = fenced + _healthy_plan("Short description.") + _PROGRESS_TAIL
    return result


def _shape_body_m() -> str:
    """(m) a 0-3-space-indented ATX H1 -- CommonMark's own indent tolerance still recognizes it."""
    result = _document("   # Feature: Indented Title", _healthy_plan("Short description."))
    return result


#: One body-builder per lettered shape, in :data:`SHAPE_LETTERS` order.
_SHAPE_BODY_BUILDERS: dict[str, "object"] = {
    "a": _shape_body_a,
    "b": _shape_body_b,
    "c": _shape_body_c,
    "d": _shape_body_d,
    "e": _shape_body_e,
    "f": _shape_body_f,
    "g": _shape_body_g,
    "h": _shape_body_h,
    "i": _shape_body_i,
    "j": _shape_body_j,
    "k": _shape_body_k,
    "l": _shape_body_l,
    "m": _shape_body_m,
}

assert set(_SHAPE_BODY_BUILDERS) == set(SHAPE_LETTERS), "every SHAPE_LETTERS entry must have a body builder"


def shape_id(letter: str) -> str:
    """The folder id for ACC-002 lettered shape ``letter`` (e.g. ``"feat-800-shape-a"``).

    Parameters
    ----------
    letter:
        One of :data:`SHAPE_LETTERS`.

    Returns
    -------
    str
        The folder id.
    """
    assert letter in SHAPE_LETTERS, letter
    result = f"{_SHAPE_ID_PREFIX}{letter}"
    return result


def healthy_id(index: int) -> str:
    """The folder id for bulk healthy filler folder number ``index`` (0-based).

    Parameters
    ----------
    index:
        The folder's 0-based position among the bulk healthy filler set.

    Returns
    -------
    str
        The folder id.
    """
    assert index >= 0, index
    result = f"{_HEALTHY_ID_PREFIX}{index}"
    return result


def write_feat_folder(base_dir: Path, folder_id: str, full_text: str) -> Path:
    """Write ``full_text`` to ``<base_dir>/<folder_id>/README.md`` directly (bypassing ``create_feat``).

    Parameters
    ----------
    base_dir:
        The feature base directory (e.g. a per-test temp dir pointed at by
        ``SPECMGR_FEAT_DIR``).
    folder_id:
        The folder's own name (and, for a well-formed document, its
        frontmatter ``id``).
    full_text:
        The complete file content (frontmatter + body) to write verbatim.

    Returns
    -------
    Path
        The written ``README.md`` path.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(folder_id, str) and folder_id, folder_id
    assert isinstance(full_text, str), type(full_text)

    folder = base_dir / folder_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / README_FILENAME
    path.write_text(full_text, encoding="utf-8")
    result = path
    return result


@dataclass(frozen=True)
class FixtureCorpus:
    """The generated fixture corpus's own structure, for precise, letter-specific test assertions.

    Attributes:
        base_dir: The base directory the corpus was generated into.
        shape_paths: Maps each :data:`SHAPE_LETTERS` entry to its generated ``README.md`` path.
        shape_ids: Maps each :data:`SHAPE_LETTERS` entry to its folder id (== :func:`shape_id`).
        healthy_ids: The bulk healthy filler folders' own ids, in generation order.
        total: The total folder count (``len(shape_paths) + len(healthy_ids)``).
    """

    base_dir: Path
    shape_paths: dict[str, Path] = field(default_factory=dict)
    shape_ids: dict[str, str] = field(default_factory=dict)
    healthy_ids: list[str] = field(default_factory=list)
    total: int = 0


def generate_fixture_corpus(base_dir: Path, *, num_healthy: int = 57) -> FixtureCorpus:
    """Materialize the deterministic ACC-001..005 fixture corpus directly under ``base_dir``.

    Generation is pure, fast, in-process file I/O (a few dozen
    ``Path.write_text`` calls) -- well under the 5 s budget ACC-001's own
    timing assertion excludes it from. Every folder is written directly to
    disk (``Path.mkdir``/``Path.write_text``), bypassing ``create_feat``/the
    MCP tool layer entirely, since several of the lettered shapes are
    deliberately invalid documents ``create_feat`` would reject.

    Parameters
    ----------
    base_dir:
        The feature base directory to generate the corpus into (typically
        a per-test temp dir, with ``SPECMGR_FEAT_DIR`` pointed at it).
    num_healthy:
        The number of bulk, healthy filler folders to generate, in addition
        to the 13 ACC-002 lettered shapes. Defaults to 57 (57 + 13 = 70,
        matching ACC-001's ``total == 70`` assertion).

    Returns
    -------
    FixtureCorpus
        The generated corpus's own structure.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert num_healthy >= 0, num_healthy

    base_dir.mkdir(parents=True, exist_ok=True)

    shape_paths: dict[str, Path] = {}
    shape_ids: dict[str, str] = {}
    for letter in SHAPE_LETTERS:
        folder_id = shape_id(letter)
        body = _SHAPE_BODY_BUILDERS[letter]()  # type: ignore[operator]
        frontmatter = (
            _MALFORMED_FRONTMATTER if letter == "a" else _FRONTMATTER_TEMPLATE.format(id=folder_id, status="planning")
        )
        full_text = frontmatter + body
        shape_paths[letter] = write_feat_folder(base_dir, folder_id, full_text)
        shape_ids[letter] = folder_id

    healthy_ids: list[str] = []
    for index in range(num_healthy):
        folder_id = healthy_id(index)
        title = f"Synthetic Filler Widget {index:03d}"
        overview = (
            f"This is synthetic filler folder number {index:03d}, generated by the Phase 120 "
            "fixture-corpus helper to approximate a realistic corpus size. It carries a few "
            "sentences of lorem-ipsum-style filler text in its own Overview section so that "
            "every bulk folder's own content differs slightly from its siblings, mirroring a "
            "real, hand-authored corpus rather than a byte-identical stamped-out one. Lorem "
            "ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua."
        )
        body = _healthy_body(title, overview)
        full_text = _FRONTMATTER_TEMPLATE.format(id=folder_id, status="planning") + body
        write_feat_folder(base_dir, folder_id, full_text)
        healthy_ids.append(folder_id)

    total = len(shape_paths) + len(healthy_ids)
    result = FixtureCorpus(
        base_dir=base_dir,
        shape_paths=shape_paths,
        shape_ids=shape_ids,
        healthy_ids=healthy_ids,
        total=total,
    )
    return result
