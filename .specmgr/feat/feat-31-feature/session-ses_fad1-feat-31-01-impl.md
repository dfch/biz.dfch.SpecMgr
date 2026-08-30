# feat-31 orchestrated implementation

**Session ID:** ses_fad147d41ffeTLTemSOE6SWkzK
**Created:** 8/30/2026, 3:46:01 PM
**Updated:** 8/30/2026, 7:25:06 PM

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '1,220p' src/biz/dfch/specmgr/feat/tools/_paths.py"
}
```

**Output:**

```
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

"""Feature (FEAT) base directory resolution and id -> path lookup (Task 2.1).

**Hand-rolled, ADR-style** (mirrors ``adr.tools._paths``), deliberately
**not** built on the shared, flat-file ``general.tools._doc_paths`` --
that module assumes one file per document directly under the base
directory (``<base>/<type>-<uuid>-<slug>.md``); ``feat`` is folder-per-
document instead (``<base>/<id>/README.md``, a fixed filename), and
``id`` is a chosen ``feat-NNN-slug`` string, not a server-generated UUID.
See ``.specmgr/feat/feat-31-feature/README.md`` Design Notes
("Addressing") for the full rationale.

Mirrors ``adr.tools._paths``'s read-only/write split: :func:`feat_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_feat_base_dir` does, for ``create_feat``. There
is deliberately no in-memory id -> path cache either -- every lookup
re-reads whatever is currently on disk, matching this codebase's "the
on-disk file is the sole source of truth" design.

**The key behavioral divergence from every other (UUID-addressed) domain**:
since ``id`` *is* the containing folder's own name by convention (REQ-004),
:func:`find_feat_path_by_id` shortcuts directly to ``<base>/<id_>/README.md``
instead of scanning every document under the base directory and comparing
each one's parsed ``frontmatter.id`` -- there is no directory scan, and
therefore no partial-id-match support either (a bare ``"feat-31"`` never
resolves to ``"feat-31-feature"``; see this feature's own Decisions Made log
for why that was considered and explicitly rejected).

**Parse-failure handling on the shortcut read.** Every other domain's
``find_*_path`` scans multiple files and *skips* a file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) so one broken file never
blocks lookup of a different, valid id -- there is no "different file" to
fall back to here, since the shortcut only ever reads one path. A parse
failure on that single target file is therefore treated the same as the
file not existing at all: both raise :class:`FeatNotFoundError`, just with
a message that distinguishes "the folder/file is missing" from "the folder
exists but its content is unparseable, or its frontmatter ``id`` does not
match the folder name it lives in" -- so ``load_by_id``/``get_feat``/every
mutating tool built on this module gets one single, consistent
not-found-shaped error to handle, without needing to separately catch
``AssertionError``/``ValidationError`` themselves.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from ...general.tools._doc_paths import slugify
from ..models.v1 import parse_feat

__all__ = [
    "DEFAULT_FEAT_DIR",
    "FEAT_DIR_ENV_VAR",
    "FEAT_TYPE_NAME",
    "README_FILENAME",
    "FeatNotFoundError",
    "ensure_feat_base_dir",
    "feat_base_dir",
    "feature_title",
    "find_feat_path_by_id",
    "iter_feat_paths",
    "slugify",
]

#: Environment variable that overrides the feature base directory. Mandatory-
#: equivalent, like every other domain's own env var (``SPECMGR_ADR_DIR``,
#: the shared ``SPECMGR_DOCS_DIR``) -- without it, tests would have no way
#: to avoid reading/writing the real ``.specmgr/feat/`` (this very feature
#: plan's own folder).
FEAT_DIR_ENV_VAR = "SPECMGR_FEAT_DIR"

#: Default feature base directory, relative to the current working
#: directory -- the same folder this feature's own plan file lives in, in
#: production.
DEFAULT_FEAT_DIR = Path(".specmgr/feat")

#: The doc-type name, for symmetry with every other domain's own
#: ``<D>_TYPE_NAME`` constant (e.g. ``dec.tools._paths.DEC_TYPE_NAME``),
#: even though it plays no role in path construction here (unlike the
#: generic ``general.tools._doc_paths`` domains, ``feat``'s base directory
#: is not ``{docs root}/feat`` -- it *is* the configured base directory
#: itself).
FEAT_TYPE_NAME = "feat"

#: The fixed filename every feature document is stored under, inside its
#: own ``<base>/<id>/`` folder.
README_FILENAME = "README.md"

#: The literal prefix every well-formed ``Feature`` H1 heading carries.
#: ``Feature.text`` (inherited from ``MarkdownSection``) always returns the
#: *whole* heading line, e.g. ``"Feature: My Title"`` -- not just the
#: free-form title after the colon -- because `Feature`'s own ``@alias``
#: regex (``"^Feature: .+$"``) matches the entire line, and `Feature`
#: declares no ``title`` computed field of its own (unlike `Phase`/
#: `UpdateEntry`/`DecisionEntry`, each of which does). Both `create_feat`
#: (folder-name slug derivation) and `list_feat` (`FeatSummary.title`) need
#: just the free-form part, so :func:`feature_title` strips it once here
#: rather than duplicating the same two lines in both tools.
_TITLE_PREFIX = "Feature: "

#: Matches a ``feat-NNN-...`` folder name, capturing the numeric ``NNN``
#: part (unpadded, matching this very plan's own "Phase 0".."Phase 5"
#: numbering convention). Used by ``create_feat`` to derive the next id.
FEAT_FOLDER_PATTERN = re.compile(r"^feat-(\d+)-")


class FeatNotFoundError(LookupError):
    """No feature folder/document found matching the given id.

    Raised both when ``<base>/<id_>/README.md`` does not exist at all, and
    when it exists but fails to parse or its frontmatter ``id`` does not
    match the folder name it was found under -- see this module's own
    docstring for why both cases collapse to the same exception type here.
    """


def feat_base_dir() -> Path:
    """Return the configured feature base directory, without creating it.

    Reads :data:`FEAT_DIR_ENV_VAR` from the environment, falling back to
    :data:`DEFAULT_FEAT_DIR`. Read-only tools (``get_feat``, ``list_feat``,
    ...) use this so merely reading never has the side effect of creating
    the directory -- see :func:`ensure_feat_base_dir` for the write path.

    Returns
    -------
    Path
        The resolved feature base directory.
    """
    value = os.environ.get(FEAT_DIR_ENV_VAR)
    result = Path(value) if value else DEFAULT_FEAT_DIR
    return result


def ensure_feat_base_dir() -> Path:
    """Return the configured feature base directory, creating it if missing.

    Only ``create_feat`` should call this -- every other tool uses the
    read-only :func:`feat_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist feature base directory.
    """
    path = feat_base_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def feature_title(text: str) -> str:
    """Strip the literal ``"Feature: "`` prefix off a ``Feature.text`` heading value.

    Parameters
    ----------
    text:
        A ``Feature.text`` value, e.g. ``"Feature: My Title"``.

    Returns
    -------
    str
        ``text`` with the literal ``"Feature: "`` prefix removed, if
        present (it always is for any ``Feature`` that parsed
        successfully, since the prefix is enforced by `Feature`'s own
        ``@alias`` regex) -- returned unchanged otherwise.
    """
    assert isinstance(text, str), type(text)

    result = text.removeprefix(_TITLE_PREFIX)
    return result


def iter_feat_paths(base_dir: Path) -> Iterator[Path]:
    """Yield every ``<base_dir>/*/README.md`` path, sorted by folder name.

    Unlike every generic-``_doc_paths``-based domain's ``iter_*_paths``
    (which globs ``*.md`` directly under the base directory), this globs
    one level deeper -- ``*/README.md`` -- since ``feat`` is folder-per-
    document, not flat-file. Yields nothing (rather than raising) if
    ``base_dir`` does not exist.

    Parameters
    ----------
    base_dir:
        The feature base directory to scan (typically :func:`feat_base_dir`'s
        return value).

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    assert isinstance(base_dir, Path), type(base_dir)

    if not base_dir.exists():
        return iter(())
    result = iter(sorted(base_dir.glob(f"*/{README_FILENAME}")))
    return result


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

This looks solid and well-reasoned. Let's check `find_feat_path_by_id`, `create_feat.py`, and the `general/tools` adapters.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '220,280p' src/biz/dfch/specmgr/feat/tools/_paths.py"
}
```

**Output:**

```


def find_feat_path_by_id(base_dir: Path, id_: str) -> Path:
    """Resolve ``id_`` to its on-disk ``README.md`` path under ``base_dir``.

    Shortcuts directly to ``<base_dir>/<id_>/README.md`` -- since ``id`` is,
    by REQ-004's addressing convention, the containing folder's own name,
    there is no need (and deliberately no support) for a full directory
    scan or partial-id matching (see this module's own docstring).

    Parameters
    ----------
    base_dir:
        The feature base directory (typically :func:`feat_base_dir`'s
        return value).
    id_:
        The id to look up -- must be the *exact* folder name, e.g.
        ``"feat-31-feature"``, not a bare ``"feat-31"`` prefix.

    Returns
    -------
    Path
        The resolved ``README.md`` path.

    Raises
    ------
    FeatNotFoundError
        If ``<base_dir>/<id_>/README.md`` does not exist, if it exists but
        fails to parse (``AssertionError``/``pydantic.ValidationError``),
        or if it parses but its frontmatter ``id`` does not match ``id_``
        (a folder/frontmatter mismatch, surfaced rather than silently
        worked around).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = base_dir / id_ / README_FILENAME
    if not path.exists():
        raise FeatNotFoundError(
            f"no feature found with id {id_!r}: {path} does not exist. The id must be the exact "
            f"containing folder's name (e.g. 'feat-31-feature'), not a bare prefix like 'feat-31' -- "
            f"use list_feat to discover the exact id first."
        )

    try:
        doc = parse_feat(path.read_text(encoding="utf-8"))
    except (AssertionError, ValidationError) as ex:
        raise FeatNotFoundError(
            f"feature folder {id_!r} exists at {path}, but its content could not be parsed as a valid "
            f"feature document ({type(ex).__name__}: {ex})."
        ) from ex

    if doc.frontmatter.id != id_:
        raise FeatNotFoundError(
            f"feature folder {id_!r} exists at {path}, but its frontmatter id ({doc.frontmatter.id!r}) "
            f"does not match the containing folder's own name ({id_!r}) -- the folder was likely "
            f"renamed or copied without updating its frontmatter."
        )

    result = path

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.5s)

Reasonable and well-documented. Now let's check `create_feat.py` and the generic dispatch adapters.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/tools/create_feat.py"
}
```

**Output:**

```
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

"""``@mcp.tool()`` wrapper: create_feat (Task 2.3).

Unlike every other domain's ``create_<d>`` (a fresh server-generated UUID,
always assignable without coordinating with any other in-flight create),
``create_feat`` derives its id (``feat-NNN-slug``) by scanning existing
``feat-*`` folder names for the highest ``NNN`` and adding one, under the
**global** :func:`~biz.dfch.specmgr.feat.tools._lock.feat_create_lock` --
see that module's docstring for why a global (not per-id) lock is needed
here. ``content`` is body markdown only (no frontmatter block), same shape
as ``create_dec``/``create_gol``: the caller's own already-validated body is
persisted byte-for-byte, and only the small, code-constructed frontmatter
YAML block is (re)generated.

**Timestamp format is a deliberate ``feat``-only divergence.** Every other
domain's ``create_<d>`` sets ``created``/``updated`` to
``datetime.now().isoformat(timespec="microseconds")``; `feat`'s own
frontmatter keeps plain ``YYYY-MM-DD`` dates instead
(``datetime.now().date().isoformat()``), matching every one of the 17
pre-existing hand-authored feature files and ADR
e369ee2e-3353-4f92-991c-6367d76d832e's own template -- see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Frontmatter").
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import FeatDocument, FeatFrontmatter, Feature
from ._lock import feat_create_lock
from ._paths import FEAT_FOLDER_PATTERN, README_FILENAME, ensure_feat_base_dir, feature_title, slugify
from ._write import write_feat_file


@mcp.tool(
    name="create_feat",
    title="Create feature",
    description=(
        "Create a new feature: assigns a fresh id, derives a filename from the body's H1 title, "
        "validates the submitted body-only content, and writes the new document to the feature base "
        "directory."
    ),
)
def create_feat(content: str) -> FeatDocument:
    """Create and write a new feature document.

    ``content`` is body markdown only (the ``Feature`` H1 and its sections)
    -- it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh ``feat-NNN-slug`` id (see this module's
    docstring), ``type="feat"``, ``status="planning"`` (always, never
    caller-supplied on create -- `feat`'s own default lifecycle state),
    ``created``/``updated`` both set to today's plain ``YYYY-MM-DD`` date,
    and ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.feat.models.v1.Feature` from it
    (``Feature.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both uncaught -- nothing is written in
    either case, and neither the base directory nor any new folder is
    touched (validation happens before the create lock is even acquired).

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    FeatDocument
        The newly created document, with its assigned ``feat-NNN-slug`` id
        in ``frontmatter.id``.
    """
    body = Feature.from_text(format_text(content))
    slug = slugify(feature_title(body.text))

    with feat_create_lock():
        base_dir = ensure_feat_base_dir()
        new_id = f"feat-{_next_feat_number(base_dir)}-{slug}"

        today = datetime.now().date().isoformat()
        new_frontmatter = FeatFrontmatter(
            id=new_id,
            type="feat",
            status="planning",
            created=today,
            updated=today,
            version=CURRENT_SCHEMA_VERSION,
        )
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)

        write_feat_file(base_dir / new_id / README_FILENAME, new_frontmatter, content)
    return new_doc


def _next_feat_number(base_dir: Path) -> int:
    """Return one past the highest existing ``feat-NNN-...`` folder number under ``base_dir``.

    Scans only folder *names* (not their content) directly under
    ``base_dir`` -- a folder that fails to parse as a feature document still
    counts toward the ``NNN`` derivation, since its name alone is enough to
    reserve that number. Returns ``1`` if ``base_dir`` holds no matching
    folder yet.
    """
    assert isinstance(base_dir, Path), type(base_dir)

    existing = [
        int(match.group(1))
        for entry in base_dir.iterdir()
        if entry.is_dir() and (match := FEAT_FOLDER_PATTERN.match(entry.name))
    ]
    result = max(existing, default=0) + 1
    return result

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

This is correct and matches the design precisely. Now let's check the `general/tools/update.py`/`set_status.py` additions and run the quality gate myself.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"feat\" src/biz/dfch/specmgr/general/tools/update.py | head -40"
}
```

**Output:**

```
18:"""``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).
22:``gol``/``rsk``/``dec``/``feat``). It dispatches on the explicit ``type``
40:``feat`` is the one domain whose adapter (``_update_feat``) diverges in two
43:others' microsecond timestamp, matching ``create_feat``'s own frontmatter
44:convention (see ``.specmgr/feat/feat-31-feature/README.md`` Design Notes,
45:"Frontmatter"); and it resolves ``id`` via ``feat.tools._paths``'s bespoke
47:feature's Design Notes, "Addressing").
65:from ...feat.models.v1 import FeatDocument, FeatFrontmatter, Feature
66:from ...feat.tools._io import load_by_id as load_feat_by_id
67:from ...feat.tools._lock import feat_lock
68:from ...feat.tools._paths import feat_base_dir
69:from ...feat.tools._write import write_feat_file
131:    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
174:    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
213:    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
252:    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
291:    ``PrbNotFoundError``; that per-domain tool was retired in feat-22
330:    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
369:    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
408:    that per-domain tool was retired in feat-22 Phase 8, when the DEC
443:def _update_feat(id_: str, content: str, begin: int | None, end: int | None) -> FeatDocument:
444:    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).
446:    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
447:    ``write_feat_file``, ``FeatNotFoundError``) with two feat-only
449:    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
450:    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan; and
453:    microsecond timestamp, matching ``create_feat``'s own frontmatter
459:        base_dir = feat_base_dir()
460:        with feat_lock(id_):
461:            path, existing = load_feat_by_id(base_dir, id_)
469:            write_feat_file(path, new_frontmatter, spliced)
474:    base_dir = feat_base_dir()
475:    with feat_lock(id_):
476:        path, existing = load_feat_by_id(base_dir, id_)
482:        write_feat_file(path, new_frontmatter, content)
496:    "feat": _update_feat,
505:        "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving "
516:    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat"],
524:    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``);
565:        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

Good, this is thorough. Let's view the actual `_update_feat` body and the plain-date timestamp usage.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '443,483p' src/biz/dfch/specmgr/general/tools/update.py"
}
```

**Output:**

```
def _update_feat(id_: str, content: str, begin: int | None, end: int | None) -> FeatDocument:
    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
    ``write_feat_file``, ``FeatNotFoundError``) with two feat-only
    divergences (see the module docstring): ``id_`` resolves via
    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan; and
    ``updated`` is bumped to a plain ``YYYY-MM-DD`` date
    (``datetime.now().date().isoformat()``), not the other eight domains'
    microsecond timestamp, matching ``create_feat``'s own frontmatter
    convention.
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = feat_base_dir()
        with feat_lock(id_):
            path, existing = load_feat_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Feature.from_text(format_text(spliced))
            today = datetime.now().date().isoformat()
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = today
            new_frontmatter = FeatFrontmatter(**fm_data)
            new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
            write_feat_file(path, new_frontmatter, spliced)
        return new_doc

    body = Feature.from_text(format_text(content))

    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        today = datetime.now().date().isoformat()
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = today
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
        write_feat_file(path, new_frontmatter, content)
    return new_doc

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.6s)

Correct and matches the spec exactly. Now let's independently run the full quality gate.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===\" && uv run --frozen ruff check 2>&1 | tail -10"
}
```

**Output:**

```
1255 files already formatted
===
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.6s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -30; echo \"EXIT:$?\""
}
```

**Output:**

```
EXIT:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 62.1s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(Ran|OK|FAILED|ERROR)\""
}
```

**Output:**

```
Range mode must raise the domain's own not-found error for an unknown id. ... ok
Ran 2179 tests in 58.656s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

All green: 2179 tests OK (up from 2106), ruff clean, vulture clean. Let's check the concurrent-create test and the integration test briefly to confirm it exercises the required scenarios.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"def test_\" tests/feat/tools/test_integration.py"
}
```

**Output:**

```
178:    def test_full_lifecycle_roundtrip(self) -> None:
271:    def test_set_status_rejects_status_outside_the_closed_four_set(self) -> None:
282:    def test_validate_rejects_malformed_body_and_wrong_full_shape(self) -> None:
295:    def test_many_concurrent_create_feat_calls_never_collide(self) -> None:

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.2s)

Good. Let's spot check that concurrent test.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '295,340p' tests/feat/tools/test_integration.py"
}
```

**Output:**

```
    def test_many_concurrent_create_feat_calls_never_collide(self) -> None:
        """20 threads hammering create_feat concurrently must all end up with distinct, valid ids."""
        results: list[FeatDocument] = []
        errors: list[BaseException] = []
        lock = threading.Lock()
        thread_count = 20

        def worker(index: int) -> None:
            body = _INITIAL_BODY.replace("Example Widget", f"Concurrent Widget {index:02d}")
            try:
                doc = create_feat(body)
            except BaseException as ex:  # noqa: BLE001 - captured for the assertion below
                with lock:
                    errors.append(ex)
                return
            with lock:
                results.append(doc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(thread_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), thread_count)

        ids = [doc.frontmatter.id for doc in results]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids created: {ids}")

        # Every created id must also be independently resolvable via list_feat/get_feat.
        page = list_feat(max_results=thread_count)
        self.assertEqual(page.total, thread_count)
        listed_ids = {summary.id for summary in page.results}
        self.assertEqual(listed_ids, set(ids))
        for id_ in ids:
            self.assertEqual(get_feat(id_).frontmatter.id, id_)


if __name__ == "__main__":
    unittest.main()

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.8s)

This is a solid test. Verification passes. Let's check the plan README update and then commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff --cached .specmgr/feat/feat-31-feature/README.md | grep -A5 \"^@@\" | head -60"
}
```

**Output:**

```
@@ -3,7 +3,7 @@ created: 2026-08-30
 id: feat-31-feature
 status: in-progress
 updated: 2026-08-30
-version: 1.7.0
+version: 1.8.0
--
@@ -632,30 +632,53 @@ discipline.
 
 #### Phase 2: Tools (`feat/tools/`) — bespoke addressing
 
-- [ ] Task 2.1: `_paths.py` (`feat_base_dir`, `iter_feat_paths`,
+- [x] Task 2.1: `_paths.py` (`feat_base_dir`, `iter_feat_paths`,
--
@@ -778,14 +801,45 @@ child section class), `document.py` (`FeatDocument`), `parser.py`
 (two small, content-preserving adjustments — loose lists, one shortened
 task item — see Task 1.5/Decisions Made). 99 new tests
 (`test_frontmatter.py`/`test_body.py`/`test_parser.py`) all green. Full
-quality gate green: `ruff format --check`/`ruff check` clean, `vulture
-src/ whitelist.py --min-confidence 60` clean (after adding the new
--
@@ -800,6 +854,68 @@ Phase 2 (`feat/tools/`) is next.
 
 ### Recent Updates
 
+#### Update 2026-08-30 (Phase 2 complete — tools, bespoke addressing)
+
--
@@ -1259,8 +1375,7 @@ Phase 2 (`feat/tools/`) is next.
   exactly, even though Design Notes' text for these three classes only
   says the computed field itself "raises `AssertionError` on a malformed
   item" without spelling out *when* that check fires. Without an eager
-  validator, `RequirementItem.description`/`AcceptanceCriterionItem.
-  criterion_description`/`TaskItem.checked` (all `@computed_field`s) would
--
@@ -1277,9 +1392,7 @@ Phase 2 (`feat/tools/`) is next.
   round-trips to a structurally-equivalent loose list rather than
   byte-exact" limitation — `dec`'s own `_REFERENCE_TEXT` already uses this
   same loose-list workaround, so this isn't a new pattern. (2) Task 0.1's
-  item text (`"Create branch and package skeleton — status: completed
-  (2026-08-30)"` in `example.md`) had its trailing `— status: completed
--
@@ -1288,20 +1401,78 @@ Phase 2 (`feat/tools/`) is next.
   accommodate them.
 - **2026-08-30 (Phase 1)**: `feat_reference.md` lives at
   `tests/feat/models/v1/data/feat_reference.md` (a real file on disk), not
-  inlined as a `format_text("""...""")` string constant the way `tests/dec/
-  models/v1/test_body.py`'s own `_REFERENCE_TEXT`/`test_parser.py`'s

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 119.5s)

This all looks appropriate and comprehensive. Now committing Phase 2.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git commit -m \"feat(feat-31): implement Feature (feat) tools (Phase 2)\n\n- feat/tools/: _paths.py (bespoke folder-per-document addressing,\n  find_feat_path_by_id shortcut, no partial-id-match), _lock.py\n  (per-id feat_lock + global feat_create_lock), _io.py, _write.py,\n  and 8 tool modules (create_feat, parse_feat, list_feat, get_feat,\n  get_feat_example, get_feat_template, delete_feat stub, validate_feat)\n- general/tools/update.py, set_status.py: add _update_feat/\n  _set_status_feat adapters + type=\\\"feat\\\" dispatch entries\n- Tests: tests/feat/tools/ (73 new tests incl. concurrent-create\n  NNN-collision simulation, full lifecycle round-trip)\" -q && git log --oneline -3"
}
```

**Output:**

```
...output truncated...

Full output saved to: /home/user/.local/share/opencode/tool-output/tool_05374c265001fovl7MlmL0GJwr

+      deep: If True, the values of fields that are Pydantic models will be deep-copied.
+
+  Returns:
+      A copy of the model with included, excluded and updated fields as specified.
+
+- `dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]'`
+
+- `from_orm(obj: 'Any') -> 'Self'`
+
+- `json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str'`
+
+- `model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
+  Creates a new instance of the `Model` class with validated data.
+
+  Creates a new model setting `__dict__` and `__pydantic_fields_set__` from trusted or pre-validated data.
+  Default values are respected, but no other validation is performed.
+
+  !!! note
+      `model_construct()` generally respects the `model_config.extra` setting on the provided model.
+      That is, if `model_config.extra == 'allow'`, then all extra passed values are added to the model instance's `__dict__`
+      and `__pydantic_extra__` fields. If `model_config.extra == 'ignore'` (the default), then all extra passed values are ignored.
+      Because no validation is performed with a call to `model_construct()`, having `model_config.extra == 'forbid'` does not result in
+      an error if extra values are passed, but they will be ignored.
+
+  Args:
+      _fields_set: A set of field names that were originally explicitly set during instantiation. If provided,
+          this is directly used for the [`model_fields_set`][pydantic.BaseModel.model_fields_set] attribute.
+          Otherwise, the field names from the `values` argument will be used.
+      values: Trusted or pre-validated data dictionary.
+
+  Returns:
+      A new instance of the `Model` class with validated data.
+
+- `model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'`
+  !!! abstract "Usage Documentation"
+      [`model_copy`](../concepts/models.md#model-copy)
+
+  Returns a copy of the model.
+
+  !!! note
+      The underlying instance's [`__dict__`][object.__dict__] attribute is copied. This
+      might have unexpected side effects if you store anything in it, on top of the model
+      fields (e.g. the value of [cached properties][functools.cached_property]).
+
+  Args:
+      update: Values to change/add in the new model. Note: the data is not validated
+          before creating the new model. You should trust this data.
+      deep: Set to `True` to make a deep copy of the model.
+
+  Returns:
+      New model instance.
+
+- `model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'dict[str, Any]'`
+  !!! abstract "Usage Documentation"
+      [`model_dump`](../concepts/serialization.md#python-mode)
+
+  Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
+
+  Args:
+      mode: The mode in which `to_python` should run.
+          If mode is 'json', the output will only contain JSON serializable types.
+          If mode is 'python', the output may contain non-JSON-serializable Python objects.
+      include: A set of fields to include in the output.
+      exclude: A set of fields to exclude from the output.
+      context: Additional context to pass to the serializer.
+      by_alias: Whether to use the field's alias in the dictionary key if defined.
+      exclude_unset: Whether to exclude fields that have not been explicitly set.
+      exclude_defaults: Whether to exclude fields that are set to their default value.
+      exclude_none: Whether to exclude fields that have a value of `None`.
+      exclude_computed_fields: Whether to exclude computed fields.
+          While this can be useful for round-tripping, it is usually recommended to use the dedicated
+          `round_trip` parameter instead.
+      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
+      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
+          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
+      fallback: A function to call when an unknown value is encountered. If not provided,
+          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
+      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
+      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.
+
+  Returns:
+      A dictionary representation of the model.
+
+- `model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'str'`
+  !!! abstract "Usage Documentation"
+      [`model_dump_json`](../concepts/serialization.md#json-mode)
+
+  Generates a JSON representation of the model using Pydantic's `to_json` method.
+
+  Args:
+      indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
+      ensure_ascii: If `True`, the output is guaranteed to have all incoming non-ASCII characters escaped.
+          If `False` (the default), these characters will be output as-is.
+      include: Field(s) to include in the JSON output.
+      exclude: Field(s) to exclude from the JSON output.
+      context: Additional context to pass to the serializer.
+      by_alias: Whether to serialize using field aliases.
+      exclude_unset: Whether to exclude fields that have not been explicitly set.
+      exclude_defaults: Whether to exclude fields that are set to their default value.
+      exclude_none: Whether to exclude fields that have a value of `None`.
+      exclude_computed_fields: Whether to exclude computed fields.
+          While this can be useful for round-tripping, it is usually recommended to use the dedicated
+          `round_trip` parameter instead.
+      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
+      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
+          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
+      fallback: A function to call when an unknown value is encountered. If not provided,
+          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
+      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
+      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.
+
+  Returns:
+      A JSON string representation of the model.
+
+- `model_json_schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', schema_generator: 'type[GenerateJsonSchema]' = <class 'pydantic.json_schema.GenerateJsonSchema'>, mode: 'JsonSchemaMode' = 'validation', *, union_format: "Literal['any_of', 'primitive_type_array']" = 'any_of') -> 'dict[str, Any]'`
+  Generates a JSON schema for a model class.
+
+  Args:
+      by_alias: Whether to use attribute aliases or not.
+      ref_template: The reference template.
+      union_format: The format to use when combining schemas from unions together. Can be one of:
+
+          - `'any_of'`: Use the [`anyOf`](https://json-schema.org/understanding-json-schema/reference/combining#anyOf)
+          keyword to combine schemas (the default).
+          - `'primitive_type_array'`: Use the [`type`](https://json-schema.org/understanding-json-schema/reference/type)
+          keyword as an array of strings, containing each type of the combination. If any of the schemas is not a primitive
+          type (`string`, `boolean`, `null`, `integer` or `number`) or contains constraints/metadata, falls back to
+          `any_of`.
+      schema_generator: To override the logic used to generate the JSON schema, as a subclass of
+          `GenerateJsonSchema` with your desired modifications
+      mode: The mode in which to generate the schema.
+
+  Returns:
+      The JSON schema for the given model class.
+
+- `model_parametrized_name(params: 'tuple[type[Any], ...]') -> 'str'`
+  Compute the class name for parametrizations of generic classes.
+
+  This method can be overridden to achieve a custom naming scheme for generic BaseModels.
+
+  Args:
+      params: Tuple of types of the class. Given a generic class
+          `Model` with 2 type variables and a concrete model `Model[str, int]`,
+          the value `(str, int)` would be passed to `params`.
+
+  Returns:
+      String representing the new class where `params` are passed to `cls` as type variables.
+
+  Raises:
+      TypeError: Raised when trying to generate concrete names for non-generic models.
+
+- `model_post_init(self, context: 'Any', /) -> 'None'`
+  Override this method to perform additional initialization after `__init__` and `model_construct`.
+  This is useful if you want to do some validation that requires the entire model to be initialized.
+
+- `model_rebuild(*, force: 'bool' = False, raise_errors: 'bool' = True, _parent_namespace_depth: 'int' = 2, _types_namespace: 'MappingNamespace | None' = None) -> 'bool | None'`
+  Try to rebuild the pydantic-core schema for the model.
+
+  This may be necessary when one of the annotations is a ForwardRef which could not be resolved during
+  the initial attempt to build the schema, and automatic rebuilding fails.
+
+  Args:
+      force: Whether to force the rebuilding of the model schema, defaults to `False`.
+      raise_errors: Whether to raise errors, defaults to `True`.
+      _parent_namespace_depth: The depth level of the parent namespace, defaults to 2.
+      _types_namespace: The types namespace, defaults to `None`.
+
+  Returns:
+      Returns `None` if the schema is already "complete" and rebuilding was not required.
+      If rebuilding _was_ required, returns `True` if rebuilding was successful, otherwise `False`.
+
+- `model_validate(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, from_attributes: 'bool | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  Validate a pydantic model instance.
+
+  Args:
+      obj: The object to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      from_attributes: Whether to extract data from object attributes.
+      context: Additional context to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Raises:
+      ValidationError: If the object could not be validated.
+
+  Returns:
+      The validated model instance.
+
+- `model_validate_json(json_data: 'str | bytes | bytearray', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  !!! abstract "Usage Documentation"
+      [JSON Parsing](../concepts/json.md#json-parsing)
+
+  Validate the given JSON data against the Pydantic model.
+
+  Args:
+      json_data: The JSON data to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      context: Extra variables to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Returns:
+      The validated Pydantic model.
+
+  Raises:
+      ValidationError: If `json_data` is not a JSON string or the object could not be validated.
+
+- `model_validate_strings(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  Validate the given object with string data against the Pydantic model.
+
+  Args:
+      obj: The object containing string data to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      context: Extra variables to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Returns:
+      The validated Pydantic model.
+
+- `parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `parse_obj(obj: 'Any') -> 'Self'`
+
+- `parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`
+
+- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`
+
+- `update_forward_refs(**localns: 'Any') -> 'None'`
+
+- `validate(value: 'Any') -> 'Self'`
+
+
 ### `PagedResult[GolSummary]`
 
 One page of results plus the paging metadata needed to fetch the next page.
diff --git a/docs/api/biz.dfch.specmgr.general.tools.set_status.md b/docs/api/biz.dfch.specmgr.general.tools.set_status.md
index 6a29e54..10418f4 100644
--- a/docs/api/biz.dfch.specmgr.general.tools.set_status.md
+++ b/docs/api/biz.dfch.specmgr.general.tools.set_status.md
@@ -2,8 +2,8 @@
 
 ``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).
 
-The generic, cross-domain status-change tool for all nine document types
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``adr``).
+The generic, cross-domain status-change tool for all ten document types
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``).
 It dispatches on the explicit ``type`` parameter to a private per-domain
 adapter (``_set_status_<d>``), each a **verbatim port** of the
 corresponding per-domain status tool's function body (same domain lock,
@@ -18,14 +18,22 @@ previous per-domain ADR status tool's function body (same ``adr_lock``,
 ``models.adr.v1.mutations.set_status``, which composes ``status`` as
 ``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
 
+The ``feat`` adapter (``_set_status_feat``) diverges from the other eight
+whole-body domains' identical shape in the same two ways ``_update_feat``
+(in ``update.py``) does: it bumps ``updated`` to a plain ``YYYY-MM-DD``
+date, not the others' microsecond timestamp; and it resolves ``id`` via
+``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
+flat-file directory scan (see
+``.specmgr/feat/feat-31-feature/README.md`` Design Notes).
+
 The parameter is intentionally named ``type`` (it matches the frontmatter
 field vocabulary the client already knows); no enabled ruff rule objects
-to the builtin shadow. The 9-way union return type is annotation-only --
+to the builtin shadow. The 10-way union return type is annotation-only --
 the MCP input schema is built from the parameters, and the SDK
 serializes whichever concrete document is returned.
 
 ``superseded_by`` is accepted only for ``type="adr"``: the
-``"superseded by X"`` status pattern is ADR-specific (no other domain's
+"superseded by X" status pattern is ADR-specific (no other domain's
 ``XFrontmatter.status`` accepts it). The public :func:`set_status`
 rejects it for any other ``type`` with a ``ValueError`` before any file
 access.
@@ -64,6 +72,20 @@ old per-domain mechanism -- was converted to the generic tools) --
 see :func:`_set_status_req` for the full semantics.
 
 
+### `_set_status_feat(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'FeatDocument'`
+
+Replace the status of the feature identified by ``id_``.
+
+Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
+``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
+:func:`_set_status_req` for the full semantics -- with the same two
+feat-only divergences ``_update_feat`` (in ``update.py``) documents:
+``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
+shortcut, not a flat-file directory scan; and ``updated`` is bumped to
+a plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``),
+not the other eight domains' microsecond timestamp.
+
+
 ### `_set_status_gol(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'GolDocument'`
 
 Replace the status of the goal identified by ``id_``.
@@ -140,20 +162,21 @@ function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
 Phase 4) -- see :func:`_set_status_req` for the full semantics.
 
 
-### `set_status(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'adr']", status: 'str', superseded_by: 'str | None' = None) -> '_SetStatusDocument'`
+### `set_status(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat', 'adr']", status: 'str', superseded_by: 'str | None' = None) -> '_SetStatusDocument'`
 
-Replace the status of an existing document, across all nine domains.
+Replace the status of an existing document, across all ten domains.
 
 Cross-domain generic for every document type
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``adr``);
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``);
 dispatches on ``type`` to the domain's own ported adapter (same lock,
 same id resolution, same body handling, same domain not-found error).
 
-For the eight whole-body domains the existing file's frontmatter is
+For the nine whole-body domains the existing file's frontmatter is
 carried over with every field preserved except ``status`` (replaced)
-and ``updated`` (bumped to the current microsecond timestamp); the
-body is never touched -- its raw, on-disk markdown (not a render of
-the parsed model) is re-read and re-persisted verbatim. For
+and ``updated`` (bumped to the current timestamp -- a plain
+``YYYY-MM-DD`` date for ``feat``, a microsecond timestamp for the other
+eight); the body is never touched -- its raw, on-disk markdown (not a
+render of the parsed model) is re-read and re-persisted verbatim. For
 ``type="adr"`` the change delegates to
 ``models.adr.v1.mutations.set_status`` (which composes ``status`` as
 ``"superseded by {superseded_by}"`` when ``superseded_by`` is given)
@@ -163,7 +186,7 @@ The new ``status`` must be in the domain's own closed vocabulary: the
 frontmatter is reconstructed through the domain's own
 ``XFrontmatter`` constructor, so the domain's own validator enforces
 its set. Where that set lives is documented per domain -- see each
-``XFrontmatter.status`` field (the eight whole-body domains'
+``XFrontmatter.status`` field (the nine whole-body domains'
 ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
 rather than any list in this docstring.
 
@@ -173,7 +196,7 @@ id:
     The document's specmgr-assigned identifier.
 type:
     The document type / domain: one of ``req``, ``uc``, ``tsk``,
-    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``adr``.
+    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``adr``.
 status:
     The new status. Must be one of the dispatched domain's own
     accepted values (see its ``XFrontmatter.status`` field). For
@@ -186,7 +209,7 @@ superseded_by:
 Returns
 -------
 ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
-GolDocument | RskDocument | DecDocument | Adr
+GolDocument | RskDocument | DecDocument | FeatDocument | Adr
     The updated document of the dispatched domain type.
 
 Raises
@@ -200,7 +223,7 @@ pydantic.ValidationError
     ``"superseded by ..."`` string). Nothing is written.
 ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
 PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
-AdrNotFoundError
+FeatNotFoundError / AdrNotFoundError
     No document of the dispatched ``type`` has this id -- the
     domain's own not-found error, unchanged from the per-domain tools.
 
diff --git a/docs/api/biz.dfch.specmgr.general.tools.update.md b/docs/api/biz.dfch.specmgr.general.tools.update.md
index 7f823a0..722a874 100644
--- a/docs/api/biz.dfch.specmgr.general.tools.update.md
+++ b/docs/api/biz.dfch.specmgr.general.tools.update.md
@@ -3,9 +3,10 @@
 ``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).
 
 The generic, cross-domain whole-body *and* line-range replace tool for the
-eight whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
-``gol``/``rsk``/``dec``). It dispatches on the explicit ``type`` parameter to a
-private per-domain adapter (``_update_<d>``), each a **verbatim port** of
+nine whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
+``gol``/``rsk``/``dec``/``feat``). It dispatches on the explicit ``type``
+parameter to
+a private per-domain adapter (``_update_<d>``), each a **verbatim port** of
 the corresponding per-domain ``update_<d>`` tool's function body (same
 domain lock, same ``load_by_id``, same frontmatter carry-over with only
 ``updated`` bumped, same verbatim persistence via the domain's own
@@ -17,10 +18,19 @@ verbatim instead of the raw fragment.
 
 The parameter is intentionally named ``type`` (it matches the frontmatter
 field vocabulary the client already knows); no enabled ruff rule objects to
-the builtin shadow. The 8-way union return type is annotation-only -- the
+the builtin shadow. The 9-way union return type is annotation-only -- the
 MCP input schema is built from the parameters, and the SDK serializes
 whichever concrete document is returned.
 
+``feat`` is the one domain whose adapter (``_update_feat``) diverges in two
+ways from the other eight's identical shape: it bumps ``updated`` to a
+plain ``YYYY-MM-DD`` date (``datetime.now().date().isoformat()``), not the
+others' microsecond timestamp, matching ``create_feat``'s own frontmatter
+convention (see ``.specmgr/feat/feat-31-feature/README.md`` Design Notes,
+"Frontmatter"); and it resolves ``id`` via ``feat.tools._paths``'s bespoke
+folder-per-document shortcut, not a flat-file directory scan (see that
+feature's Design Notes, "Addressing").
+
 ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
 contract (``update_frontmatter``/``update_section``/``option_*``) has no
 whole-body replace by design.
@@ -40,6 +50,21 @@ domain -- merged from dev while still on the old per-domain mechanism
 (see :func:`_update_req`).
 
 
+### `_update_feat(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'FeatDocument'`
+
+Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).
+
+Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
+``write_feat_file``, ``FeatNotFoundError``) with two feat-only
+divergences (see the module docstring): ``id_`` resolves via
+``feat.tools._paths``'s bespoke folder-per-document shortcut (through
+``load_by_id``/``feat_base_dir``), not a flat-file directory scan; and
+``updated`` is bumped to a plain ``YYYY-MM-DD`` date
+(``datetime.now().date().isoformat()``), not the other eight domains'
+microsecond timestamp, matching ``create_feat``'s own frontmatter
+convention.
+
+
 ### `_update_gol(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'GolDocument'`
 
 Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).
@@ -121,12 +146,12 @@ per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
 branch (see :func:`_update_req`).
 
 
-### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec']", content: 'str', begin: 'int | None' = None, end: 'int | None' = None) -> '_UpdateDocument'`
+### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat']", content: 'str', begin: 'int | None' = None, end: 'int | None' = None) -> '_UpdateDocument'`
 
 Replace the body of an existing document, in whole-body or line-range mode.
 
-Cross-domain generic for the eight whole-body document types
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``);
+Cross-domain generic for the nine whole-body document types
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``);
 dispatches on ``type`` to the domain's own ported adapter (same lock,
 same id resolution, same frontmatter carry-over, same verbatim
 persistence, same domain not-found error).
@@ -167,7 +192,7 @@ id:
     The document's specmgr-assigned identifier.
 type:
     The document type / domain: one of ``req``, ``uc``, ``tsk``,
-    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``.
+    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``.
 content:
     Whole-body mode: the replacement body markdown, with no
     frontmatter block. Range mode: the replacement fragment for lines
@@ -183,7 +208,7 @@ end:
 Returns
 -------
 ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
-GolDocument | RskDocument | DecDocument
+GolDocument | RskDocument | DecDocument | FeatDocument
     The updated document of the dispatched domain type.
 
 Raises
@@ -201,7 +226,8 @@ pydantic.ValidationError
     A field/cross-field validation failure in the (spliced) body (e.g.
     a range producing an out-of-vocabulary value). Nothing is written.
 ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
-PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError
+PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
+FeatNotFoundError
     No document of the dispatched ``type`` has this id -- the
     domain's own not-found error, unchanged from the per-domain tools.

specmgr mcp-docs.........................................................Failed
- hook id: specmgr-mcp-docs
- exit code: 1
- files were modified by this hook

✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/MCP.md
diff --git a/docs/MCP.md b/docs/MCP.md
index b55ee9f..5926f96 100644
--- a/docs/MCP.md
+++ b/docs/MCP.md
@@ -3,7 +3,7 @@
 Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
 do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 
-28 resource(s), 1 resource template(s), 79 tool(s), 21 prompt(s).
+28 resource(s), 1 resource template(s), 87 tool(s), 21 prompt(s).
 
 ## Table of Contents
 
@@ -260,6 +260,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | --- | --- |
 | [`create_adr`](#tool-create_adr) | Create a new ADR: assigns a fresh id, derives a filename from the title, validates, renders, and writes the new document to the ADR base directory. |
 | [`create_dec`](#tool-create_dec) | Create a new decision: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the decision base directory. |
+| [`create_feat`](#tool-create_feat) | Create a new feature: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the feature base directory. |
 | [`create_gol`](#tool-create_gol) | Create a new goal: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the goal base directory. |
 | [`create_prb`](#tool-create_prb) | Create a new Problem Statement: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the problem statement base directory. |
 | [`create_qa`](#tool-create_qa) | Create a new Question and Answer (QA) document: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the QA base directory. |
@@ -268,6 +269,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`create_tsk`](#tool-create_tsk) | Create a new task list: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the task list base directory. |
 | [`create_uc`](#tool-create_uc) | Create a new use case: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the use-case base directory. |
 | [`delete_dec`](#tool-delete_dec) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
+| [`delete_feat`](#tool-delete_feat) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_gol`](#tool-delete_gol) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_prb`](#tool-delete_prb) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_qa`](#tool-delete_qa) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
@@ -279,6 +281,9 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`get_dec`](#tool-get_dec) | Read, parse, and return a full decision document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
 | [`get_dec_example`](#tool-get_dec_example) | Return a complete, valid sample decision document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`get_dec_template`](#tool-get_dec_template) | Return a DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision. |
+| [`get_feat`](#tool-get_feat) | Read, parse, and return a full feature document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
+| [`get_feat_example`](#tool-get_feat_example) | Return a complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
+| [`get_feat_template`](#tool-get_feat_template) | Return a FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature. |
 | [`get_gol`](#tool-get_gol) | Read, parse, and return a full goal document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
 | [`get_gol_example`](#tool-get_gol_example) | Return a complete, valid sample goal document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`get_gol_template`](#tool-get_gol_template) | Return a GOL document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new goal. |
@@ -302,6 +307,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`get_uc_template`](#tool-get_uc_template) | Return a UC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new use case. |
 | [`list_adr`](#tool-list_adr) | Ids, titles, statuses, and refs of ADRs in the configured ADR base directory (SPECMGR_ADR_DIR), one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use get_adr with it instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_dec`](#tool-list_dec) | Ids, titles, statuses, and refs of decisions in the configured decision base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_dec tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
+| [`list_feat`](#tool-list_feat) | Ids, titles, statuses, and refs of features in the configured feature base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_feat tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_gol`](#tool-list_gol) | Ids, titles, statuses, and refs of goals in the configured goal base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_gol tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_prb`](#tool-list_prb) | Ids, titles, statuses, and refs of problem statements in the configured problem statement base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_prb tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_qa`](#tool-list_qa) | Ids, titles, statuses, and refs of QA documents in the configured QA base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_qa tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
@@ -316,6 +322,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`option_read`](#tool-option_read) | Return the current content of the option named full_title (plan §5). |
 | [`option_update`](#tool-option_update) | Full-content replace of the option named full_title (plan §5), returning the new content. |
 | [`parse_dec`](#tool-parse_dec) | Parse a decision markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument`. |
+| [`parse_feat`](#tool-parse_feat) | Parse a feature markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.feat.models.v1.FeatDocument`. |
 | [`parse_gol`](#tool-parse_gol) | Parse a goal markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.gol.models.v1.GolDocument`. |
 | [`parse_prb`](#tool-parse_prb) | Parse a problem statement markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.prb.models.v1.PrbDocument`. |
 | [`parse_qa`](#tool-parse_qa) | Parse a QA document markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.qa.models.v2.QaDocument`. |
@@ -323,12 +330,13 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`parse_rsk`](#tool-parse_rsk) | Parse a risk markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument`. |
 | [`parse_tsk`](#tool-parse_tsk) | Parse a task list markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument`. |
 | [`parse_uc`](#tool-parse_uc) | Parse a use-case markdown file (YAML frontmatter + body) from disk into a structured document. |
-| [`set_status`](#tool-set_status) | Replace the status of an existing document across all nine domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, adr), also bumping `updated` (the eight whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point. |
-| [`update`](#tool-update) | Whole-body or line-range replace of an existing document's content across the eight whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool. |
+| [`set_status`](#tool-set_status) | Replace the status of an existing document across all ten domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr), also bumping `updated` (the nine whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point. |
+| [`update`](#tool-update) | Whole-body or line-range replace of an existing document's content across the nine whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool. |
 | [`update_frontmatter`](#tool-update_frontmatter) | Whole-object replace of an ADR's frontmatter (plan §3), preserving its existing id. |
 | [`update_section`](#tool-update_section) | Whole-section replace/delete of one AdrBody field (plan §4). |
 | [`validate_adr`](#tool-validate_adr) | Re-read and re-parse an ADR by id, letting the models' own Pydantic validators run. |
 | [`validate_dec`](#tool-validate_dec) | Disk-free, id-free dry run validating decision content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
+| [`validate_feat`](#tool-validate_feat) | Disk-free, id-free dry run validating feature content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`validate_gol`](#tool-validate_gol) | Disk-free, id-free dry run validating goal content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`validate_prb`](#tool-validate_prb) | Disk-free, id-free dry run validating problem statement content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`validate_qa`](#tool-validate_qa) | Disk-free, id-free dry run validating QA document content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
@@ -359,6 +367,16 @@ Create a new decision: assigns a fresh id, derives a filename from the body's H1
 | --- | --- | --- |
 | `content` | `string` | Yes |
 
+### Tool: create_feat
+
+**Create feature**
+
+Create a new feature: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the feature base directory.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `content` | `string` | Yes |
+
 ### Tool: create_gol
 
 **Create goal**
@@ -439,6 +457,16 @@ Stub only -- always raises NotImplementedError. Reserves the name for a future i
 | --- | --- | --- |
 | `id` | `string` | Yes |
 
+### Tool: delete_feat
+
+**Delete feature (not yet implemented)**
+
+Stub only -- always raises NotImplementedError. Reserves the name for a future implementation.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `id` | `string` | Yes |
+
 ### Tool: delete_gol
 
 **Delete goal (not yet implemented)**
@@ -542,6 +570,29 @@ Return a complete, valid sample decision document as raw markdown -- frontmatter
 
 Return a DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision.
 
+### Tool: get_feat
+
+**Get feature**
+
+Read, parse, and return a full feature document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `id` | `string` | Yes |
+| `raw` | `boolean` | No |
+
+### Tool: get_feat_example
+
+**Get FEAT example**
+
+Return a complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.
+
+### Tool: get_feat_template
+
+**Get FEAT template**
+
+Return a FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature.
+
 ### Tool: get_gol
 
 **Get goal**
@@ -725,6 +776,17 @@ Ids, titles, statuses, and refs of decisions in the configured decision base dir
 | `max_results` | `integer | None` | No |
 | `offset` | `integer | None` | No |
 
+### Tool: list_feat
+
+**List features**
+
+Ids, titles, statuses, and refs of features in the configured feature base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_feat tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `max_results` | `integer | None` | No |
+| `offset` | `integer | None` | No |
+
 ### Tool: list_gol
 
 **List goals**
@@ -878,6 +940,16 @@ Parse a decision markdown file (YAML frontmatter + body) from disk into a struct
 | --- | --- | --- |
 | `path` | `string` | Yes |
 
+### Tool: parse_feat
+
+**Parse feature**
+
+Parse a feature markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.feat.models.v1.FeatDocument`.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `path` | `string` | Yes |
+
 ### Tool: parse_gol
 
 **Parse goal**
@@ -952,12 +1024,12 @@ Parse a use-case markdown file (YAML frontmatter + body) from disk into a struct
 
 **Set document status**
 
-Replace the status of an existing document across all nine domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, adr), also bumping `updated` (the eight whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point.
+Replace the status of an existing document across all ten domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr), also bumping `updated` (the nine whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point.
 
 | Parameter | Type | Required |
 | --- | --- | --- |
 | `id` | `string` | Yes |
-| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, adr)` | Yes |
+| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr)` | Yes |
 | `status` | `string` | Yes |
 | `superseded_by` | `string | None` | No |
 
@@ -965,12 +1037,12 @@ Replace the status of an existing document across all nine domains (`type` is on
 
 **Update document**
 
-Whole-body or line-range replace of an existing document's content across the eight whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool.
+Whole-body or line-range replace of an existing document's content across the nine whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool.
 
 | Parameter | Type | Required |
 | --- | --- | --- |
 | `id` | `string` | Yes |
-| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec)` | Yes |
+| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat)` | Yes |
 | `content` | `string` | Yes |
 | `begin` | `integer | None` | No |
 | `end` | `integer | None` | No |
@@ -1019,6 +1091,17 @@ Disk-free, id-free dry run validating decision content. `full=False` (default) v
 | `content` | `string` | Yes |
 | `full` | `boolean` | No |
 
+### Tool: validate_feat
+
+**Validate feature content**
+
+Disk-free, id-free dry run validating feature content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body).
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `content` | `string` | Yes |
+| `full` | `boolean` | No |
+
 ### Tool: validate_gol
 
 **Validate goal content**

specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

The pre-commit hook regenerated docs again (drift from new tools registering). Let's stage those and re-commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short | grep -v \"^A\\|^M  src\\|^M  tests\\|^M  \\.specmgr\""
}
```

**Output:**

```
 M docs/GENERATED.md
 M docs/MCP.md
 M docs/api/README.md
 M docs/api/biz.dfch.specmgr.feat.md
 M docs/api/biz.dfch.specmgr.feat.tools.md
 M docs/api/biz.dfch.specmgr.general.models.paged_result.md
 M docs/api/biz.dfch.specmgr.general.tools.set_status.md
 M docs/api/biz.dfch.specmgr.general.tools.update.md
?? docs/api/biz.dfch.specmgr.feat.tools._io.md
?? docs/api/biz.dfch.specmgr.feat.tools._lock.md
?? docs/api/biz.dfch.specmgr.feat.tools._paths.md
?? docs/api/biz.dfch.specmgr.feat.tools._write.md
?? docs/api/biz.dfch.specmgr.feat.tools.create_feat.md
?? docs/api/biz.dfch.specmgr.feat.tools.delete_feat.md
?? docs/api/biz.dfch.specmgr.feat.tools.get_feat.md
?? docs/api/biz.dfch.specmgr.feat.tools.get_feat_example.md
?? docs/api/biz.dfch.specmgr.feat.tools.get_feat_template.md
?? docs/api/biz.dfch.specmgr.feat.tools.list_feat.md
?? docs/api/biz.dfch.specmgr.feat.tools.parse_feat.md
?? docs/api/biz.dfch.specmgr.feat.tools.validate_feat.md

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 121.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): implement Feature (feat) tools (Phase 2)\n\n- feat/tools/: _paths.py (bespoke folder-per-document addressing,\n  find_feat_path_by_id shortcut, no partial-id-match), _lock.py\n  (per-id feat_lock + global feat_create_lock), _io.py, _write.py,\n  and 8 tool modules (create_feat, parse_feat, list_feat, get_feat,\n  get_feat_example, get_feat_template, delete_feat stub, validate_feat)\n- general/tools/update.py, set_status.py: add _update_feat/\n  _set_status_feat adapters + type=\\\"feat\\\" dispatch entries\n- Tests: tests/feat/tools/ (73 new tests incl. concurrent-create\n  NNN-collision simulation, full lifecycle round-trip)\n- Regenerate docs/api + docs/GENERATED.md + docs/MCP.md\" -q && git log --oneline -3"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

Phase 2 committed (`a2473ab`). Moving on to Phase 3.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Scaffolding (already complete, verify only)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models + parser (feat/models/v1/)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources + packaged data + schema",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 4: Prompts",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 5: Cross-cutting registration + final verification",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Scaffolding (already complete, verify only)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models + parser (feat/models/v1/)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources + packaged data + schema",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 4: Prompts",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 5: Cross-cutting registration + final verification",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && find src/biz/dfch/specmgr/dec/resources src/biz/dfch/specmgr/dec/data -type f | sort"
}
```

**Output:**

```
src/biz/dfch/specmgr/dec/data/dec_create_instructions.md
src/biz/dfch/specmgr/dec/data/dec_example.md
src/biz/dfch/specmgr/dec/data/dec_schema.json
src/biz/dfch/specmgr/dec/data/dec_template.md
src/biz/dfch/specmgr/dec/data/dec_update_instructions.md
src/biz/dfch/specmgr/dec/resources/dec_example.py
src/biz/dfch/specmgr/dec/resources/dec_schema.py
src/biz/dfch/specmgr/dec/resources/dec_template.py
src/biz/dfch/specmgr/dec/resources/__init__.py
src/biz/dfch/specmgr/dec/resources/__pycache__/dec_example.cpython-313.pyc
src/biz/dfch/specmgr/dec/resources/__pycache__/dec_schema.cpython-313.pyc
src/biz/dfch/specmgr/dec/resources/__pycache__/dec_template.cpython-313.pyc
src/biz/dfch/specmgr/dec/resources/__pycache__/__init__.cpython-313.pyc

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.3s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/dec/resources/dec_schema.py src/biz/dfch/specmgr/dec/resources/dec_example.py src/biz/dfch/specmgr/dec/resources/__init__.py"
}
```

**Output:**

```
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

"""Resource: specmgr://dec/schema (feat-21 Task 3.4, packaged data).

Reads DEC's generated JSON Schema from the packaged data copy
(``dec/data/dec_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/dec_schema.json`` directly -- the latter is only readable
from an editable/source checkout (``general.tools._doc_paths``'s own
docstring documents this), which would break for a real, non-editable
``pip install``. The packaged copy is kept in sync with
``docs/dec_schema.json`` by a dedicated pre-commit hook/CI step that runs
``specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data``
-- the same generator as ``docs/dec_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_dec_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. Mirrors
``gol.resources.gol_schema`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``dec/models/v1``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made for
the original precedent.
"""

from __future__ import annotations

import json
from typing import Any

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dec/schema",
    name="dec_schema",
    title="Decision (DEC) JSON Schema",
    description=(
        "The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` and "
        "kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version "
        "marker for detecting a shape change without diffing the whole document."
    ),
    mime_type="application/json",
)
def dec_schema() -> dict[str, Any]:
    """Return the parsed contents of DEC's packaged JSON Schema.

    Reads the packaged copy (``dec/data/dec_schema.json``) fresh
    on every call (no in-memory cache, consistent with every other
    resource/tool in this codebase) but never regenerates it -- its
    presence is guaranteed at build time (real package data, kept in sync
    with ``docs/dec_schema.json`` by a dedicated pre-commit hook/CI step),
    so a missing or corrupted file is treated as a hard failure rather than
    defensively handled.

    Returns
    -------
    dict[str, Any]
        The parsed JSON Schema document (top-level keys include
        ``$schema``, ``$comment``, ``$defs``, ``properties``, ...).

    Raises
    ------
    FileNotFoundError
        If the packaged ``dec_schema.json`` is missing.
    json.JSONDecodeError
        If the packaged file is not valid JSON.
    """
    result: dict[str, Any] = json.loads(read_packaged_text("dec", "schema", "json"))
    return result
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

"""Resource: specmgr://dec/example (feat-21 Task 3.4).

Read-only, addressable counterpart of the ``get_dec_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``dec.tools`` (nor vice versa): both this resource and the ``get_dec_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``gol.resources.gol_example`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://dec/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dec/example",
    name="dec_example",
    title="Decision (DEC) Example",
    description=(
        "A complete, valid sample decision document as raw markdown -- frontmatter and "
        "body -- exercising every section, for use as a learning example."
    ),
    mime_type="text/markdown",
)
def dec_example() -> str:
    """Return the packaged DEC example's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as ``dec.tools.get_dec_example.get_dec_example`` -- this is simply
    that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "example")
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

"""MCP resource registrations for Decision (DEC) documents (feat-21 Task 3.4).

``dec_schema`` registers the persisted-JSON-Schema resource
(``specmgr://dec/schema``). ``dec_example`` registers the packaged sample
decision document resource (``specmgr://dec/example``). ``dec_template``
registers the packaged decision template resource (``specmgr://dec/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_dec`` (the RSK precedent).
Import this package to register all decision resources against the shared
``mcp`` application instance::

    from biz.dfch.specmgr.dec import resources  # noqa: F401 (side-effects only)

Like GOL, DEC has no by-id single-document *resource* -- id-based reads go
through the ``get_dec`` tool only (``dec.tools.get_dec``), and no
``specmgr://dec/list`` resource either -- listing goes through the
``list_dec`` ``@mcp.tool()`` (``dec.tools.list_dec``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
"""

from . import dec_example, dec_schema, dec_template  # noqa: F401

__all__ = [
    "dec_example",
    "dec_schema",
    "dec_template",
]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

Now let's check `commands/schema.py` for the `generate_dec_schema` generator and pyproject.toml's dec package-data entry.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"dec\\b\\|_GENERATORS\\|generate_dec_schema\" src/biz/dfch/specmgr/commands/schema.py | head -40"
}
```

**Output:**

```
22:``_GENERATORS`` below, keyed by its short doc-type name (``"req"``, ``"uc"``).
50:from ..dec.models.v1 import SCHEMA_COMMENT_VERSION as DEC_SCHEMA_COMMENT_VERSION
51:from ..dec.models.v1.document import DecDocument
204:def generate_dec_schema() -> str:
207:    Mirrors :func:`generate_req_schema` exactly, but for ``dec.models.v1``:
209:    default), and ``"$comment"`` holds ``dec.models.v1.SCHEMA_COMMENT_VERSION``
225:_GENERATORS: dict[str, Callable[[], str]] = {
226:    "dec": generate_dec_schema,
242:            help=f"Restrict generation to one registered doc type ({', '.join(sorted(_GENERATORS))}). "
264:    if type_ is not None and type_ not in _GENERATORS:
265:        valid = ", ".join(sorted(_GENERATORS))
269:    selected = {type_: _GENERATORS[type_]} if type_ is not None else dict(_GENERATORS)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.4s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/commands/schema.py",
  "offset": 180,
  "limit": 50
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/commands/schema.py</path>
<type>file</type>
<content>
180:     schema_dict = GolDocument.model_json_schema()
181:     schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
182:     schema_dict["$comment"] = GOL_SCHEMA_COMMENT_VERSION
183:     return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"
184: 
185: 
186: def generate_rsk_schema() -> str:
187:     """Generate RSK's JSON Schema (2020-12 dialect) from ``RskDocument.model_json_schema()``.
188: 
189:     Mirrors :func:`generate_req_schema` exactly, but for ``rsk.models.v1``:
190:     the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
191:     default), and ``"$comment"`` holds ``rsk.models.v1.SCHEMA_COMMENT_VERSION``
192:     (currently ``"v1"``) instead of REQ's own version token.
193: 
194:     Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
195:     the same byte-identical-output/drift-detection reason as
196:     :func:`generate_req_schema`.
197:     """
198:     schema_dict = RskDocument.model_json_schema()
199:     schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
200:     schema_dict["$comment"] = RSK_SCHEMA_COMMENT_VERSION
201:     return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"
202: 
203: 
204: def generate_dec_schema() -> str:
205:     """Generate DEC's JSON Schema (2020-12 dialect) from ``DecDocument.model_json_schema()``.
206: 
207:     Mirrors :func:`generate_req_schema` exactly, but for ``dec.models.v1``:
208:     the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
209:     default), and ``"$comment"`` holds ``dec.models.v1.SCHEMA_COMMENT_VERSION``
210:     (currently ``"v1"``) instead of REQ's own version token.
211: 
212:     Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
213:     the same byte-identical-output/drift-detection reason as
214:     :func:`generate_req_schema`.
215:     """
216:     schema_dict = DecDocument.model_json_schema()
217:     schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
218:     schema_dict["$comment"] = DEC_SCHEMA_COMMENT_VERSION
219:     return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"
220: 
221: 
222: #: Registry mapping a doc-type name (as accepted by ``--type``) to its
223: #: ``generate_x() -> str`` function. Add an entry here when a new document
224: #: type's schema generator is implemented (e.g. ``"adr"``).
225: _GENERATORS: dict[str, Callable[[], str]] = {
226:     "dec": generate_dec_schema,
227:     "gol": generate_gol_schema,
228:     "prb": generate_prb_schema,
229:     "qa": generate_qa_schema,

(Showing lines 180-229 of 288. Use offset=230 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

Good, clear pattern. Now check pyproject.toml package-data and pre-commit config for dec.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"dec\\b\" pyproject.toml .pre-commit-config.yaml .github/workflows/ci.yml"
}
```

**Output:**

```
pyproject.toml:123:"biz.dfch.specmgr.dec" = [
.pre-commit-config.yaml:91:          -- always runs with no `--type` (all registered types), currently `dec`,
.pre-commit-config.yaml:100:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:117:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:134:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:151:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:168:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:185:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:202:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:218:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.pre-commit-config.yaml:220:      - id: specmgr-schema-dec-package
.pre-commit-config.yaml:221:        name: specmgr schema (dec package copy)
.pre-commit-config.yaml:224:          (src/biz/dfch/specmgr/dec/data/dec_schema.json), read by the
.pre-commit-config.yaml:225:          `specmgr://dec/schema` MCP resource via `importlib.resources` so it
.pre-commit-config.yaml:232:        entry: uv run --frozen specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data
.pre-commit-config.yaml:235:        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
.github/workflows/ci.yml:90:      # (dec, gol, prb, qa, req, rsk, tsk, uc) in a single run, and the command itself
.github/workflows/ci.yml:181:    - name: Make sure `src/biz/dfch/specmgr/dec/data/dec_schema.json` is correct
.github/workflows/ci.yml:182:      # Packaged copy of the same schema, read by the `specmgr://dec/schema` MCP resource
.github/workflows/ci.yml:187:        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data || {
.github/workflows/ci.yml:188:          echo "::error::src/biz/dfch/specmgr/dec/data/dec_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data' and commit the result (see AGENTS.md)."

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 8.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '100,140p' pyproject.toml"
}
```

**Output:**

```

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["E501"]
# vulture whitelist: bare name/attribute references are intentional (see whitelist.py).
"whitelist.py" = ["F821"]

[tool.pylint.format]
max-line-length = 120

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
namespaces = true

[tool.setuptools.package-data]
"biz.dfch.specmgr" = [
    "py.typed"
]
"biz.dfch.specmgr.adr" = [
    "data/*.md"
]
"biz.dfch.specmgr.dec" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.gol" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.prb" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.qa" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.req" = [
    "data/*.md",

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/general/tools/_packaged_data.py"
}
```

**Output:**

```
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

"""Generic, doc-type-agnostic access to packaged example/template/schema data
files (plan Task 5.3), generalizing ``req/_data.py``'s formerly REQ-only
shape so a future artifact domain (UC, goal, acc, ...) never needs its own
copy of this module.

Fixed on-disk convention: ``{type_name}/data/{type_name}_{kind}.{ext}`` (e.g.
``req/data/req_example.md``, a future ``uc/data/uc_example.md``) -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Task 5.2 design note
for the full discussion. Files under this convention are real *package
data* -- declared per-package under ``[tool.setuptools.package-data]``
(that declaration itself is **not** generalizable across packages; a new
artifact type still needs its own entry there, plus its own pre-commit
hook/CI step for any packaged schema copy) -- loaded via
:mod:`importlib.resources` so their presence is a genuine build-time
guarantee, surviving a real, non-editable ``pip install`` too, not just a
dev checkout.

Deliberately function-based, not a per-type cached ``Traversable`` constant:
:func:`packaged_data_path` is the single seam every caller (and every test)
goes through, regardless of how many artifact domains exist -- replacing the
old one-constant-per-file shape (``_EXAMPLE_PATH``/``_TEMPLATE_PATH``/
``_SCHEMA_PATH``) that ``req/_data.py`` used to declare. Tests patch this one
function (via ``mock.patch.object``) to redirect a read at a temporary file,
instead of patching a different constant per domain/kind.

Placed under ``general/tools/`` (not a top-level ``general/`` module),
mirroring ``general.tools._doc_paths``'s own placement (Task 3.10) -- neither
is an ``@mcp.tool()`` itself, both are private, unexported plumbing that
domain ``tools``/``resources`` sub-packages import directly.

Only imports the standard library (``importlib.resources``), so importing
this module never pulls in the ``cli``/``mcp`` extras.
"""

from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable

__all__ = [
    "packaged_data_path",
    "read_packaged_text",
]


def packaged_data_path(type_name: str, kind: str, ext: str = "md") -> Traversable:
    """Return the ``Traversable`` for ``{type_name}/data/{type_name}_{kind}.{ext}``.

    The anchor package is ``biz.dfch.specmgr.{type_name}`` -- e.g. for
    ``type_name="req"``, ``kind="example"``, ``ext="md"`` (the default),
    this resolves to package ``biz.dfch.specmgr.req``'s packaged
    ``data/req_example.md``. Never reads the file or checks its existence --
    purely a path computation, so callers (and tests) can redirect every
    read by patching this one function, without touching the filesystem or
    ``importlib.resources`` itself.

    Parameters
    ----------
    type_name:
        The artifact domain's package/type name (e.g. ``"req"``), matching
        its top-level package name under ``biz.dfch.specmgr``.
    kind:
        The packaged file's role within that domain (e.g. ``"example"``,
        ``"template"``, ``"schema"``).
    ext:
        The file extension, without a leading dot. Defaults to ``"md"``.

    Returns
    -------
    Traversable
        A lazily-resolved path-like handle; nothing is read yet.
    """
    anchor = f"biz.dfch.specmgr.{type_name}"
    result: Traversable = resources.files(anchor) / "data" / f"{type_name}_{kind}.{ext}"
    return result


def read_packaged_text(type_name: str, kind: str, ext: str = "md") -> str:
    """Return the packaged data file's full text content, verbatim.

    Reads the file fresh on every call (no in-memory cache, consistent with
    every other resource/tool in this codebase). The file's presence is a
    build-time guarantee (declared package data), so a missing or corrupted
    file is a hard, uncaught failure -- there is no defensive handling here.

    Parameters
    ----------
    type_name:
        See :func:`packaged_data_path`.
    kind:
        See :func:`packaged_data_path`.
    ext:
        See :func:`packaged_data_path`.

    Returns
    -------
    str
        The packaged file's raw text, exactly as committed on disk.

    Raises
    ------
    FileNotFoundError
        If the packaged file is missing (should never happen outside a
        broken installation).
    """
    result: str = packaged_data_path(type_name, kind, ext).read_text(encoding="utf-8")
    return result

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 749.4s)

_Thinking:_

**Tool: task**

**Input:**

````json
{
  "description": "Implement feat-31 Phase 3: resources+data+schema",
  "subagent_type": "phase-implementer",
  "prompt": "Implement **Phase 3: Resources + packaged data + schema** of the feature plan at:\n\n`/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md`\n\nRead that entire README.md first (Overview, REQ-007/REQ-009, ACC-005/ACC-007, Design Notes). Phases 0-2 are complete and committed: `feat/models/v1/` (full schema/parser) and `feat/tools/` (bespoke folder-per-document addressing, all 8 tools, generic `update`/`set_status` dispatch entries for `type=\"feat\"`) both exist and are fully tested. Do not touch `feat/models/`, `feat/tools/`, `feat/prompts/`, or anything under Phase 4/5 (server.py registration, pre-commit config, CI, AGENTS.md, root README.md are all explicitly Phase 5's job — do NOT touch them in this phase, even though `commands/schema.py` is in scope here).\n\n### Phase 3 tasks (verbatim from the plan's Task List)\n\n- Task 3.1: `feat/data/feat_example.md` (byte-identical copy of `feat_reference.md`, DEC/GOL precedent) — depends on: Task 2.6.\n- Task 3.2: `feat/data/feat_template.md` — all-sections placeholder skeleton, `status: planning`; must round-trip through `parse_feat` — depends on: Task 2.6.\n- Task 3.3: `feat/data/feat_create_instructions.md` + `feat_update_instructions.md` — depends on: Task 2.6.\n- Task 3.4: `commands/schema.py` — `generate_feat_schema()` + `_GENERATORS[\"feat\"]`; run `specmgr schema --type feat` (writes `docs/feat_schema.json`) and the packaged-copy variant — depends on: Task 1.4.\n- Task 3.5: `feat/resources/` — `feat_schema.py`, `feat_example.py`, `feat_template.py`, `__init__.py` — depends on: Task 3.1, Task 3.2, Task 3.4.\n- Task 3.6: Tests `tests/feat/resources/` (ACC-005/ACC-007) — depends on: Task 3.5.\n- Task 3.7: Phase-end quality gate + commit + comment on issue #31 — depends on: Task 3.6. **Do NOT commit yourself and do NOT post the GitHub comment** — the orchestrator (me) will do both after independently verifying your work. Just run the quality gate and report the evidence.\n\n### Precedent to mirror closely (read these directly, they are your primary reference)\n\n- `src/biz/dfch/specmgr/dec/data/dec_example.md`, `dec_template.md`, `dec_create_instructions.md`, `dec_update_instructions.md` — read all four for shape/tone/length precedent. `dec_example.md` is a byte-identical copy of whatever `dec`'s reference fixture is. For `feat`, **`feat/data/feat_example.md` must be a byte-identical copy of `tests/feat/models/v1/data/feat_reference.md`** (the fixture Phase 1 created, itself seeded from `.specmgr/feat/feat-31-feature/example.md`) — do not re-derive it.\n- `feat_template.md`: build a template that exercises every section (all mandatory + every optional section present: `### Dependencies` with both `#### Depends On`/`#### Blocks`, `### Design Notes`, `### Related Decisions`, `### Blockers`, `### Decisions Made`, `### Related PRs / Commits`, `### More Information`), `status: planning` in frontmatter, short placeholder (\"blind text\") content per section — it must successfully parse via `parse_feat` (structurally and field-valid), but is NOT required to be a \"realistic\" example — that's what `feat_example.md` is for. Look at `dec_template.md`/`gol_template.md` for the placeholder-content tone/style (e.g. \"Lorem ipsum\"-style or plain \"Placeholder text for X\" style — check what `dec`/`gol` actually use).\n- `src/biz/dfch/specmgr/dec/resources/{dec_schema,dec_example,dec_template,__init__}.py` — mirror each 1:1 for `feat_schema.py`/`feat_example.py`/`feat_template.py`/`__init__.py`, adjusting only domain name/URI (`specmgr://feat/schema`, `specmgr://feat/example`, `specmgr://feat/template`) and imports (`FeatDocument`, `SCHEMA_COMMENT_VERSION` from `feat.models.v1`).\n- `src/biz/dfch/specmgr/commands/schema.py` — read the whole file to see `generate_req_schema`/`generate_dec_schema` and the `_GENERATORS` dict at the bottom. Add `generate_feat_schema()` (mirroring `generate_dec_schema()` exactly, but importing `FeatDocument`/`SCHEMA_COMMENT_VERSION as FEAT_SCHEMA_COMMENT_VERSION` from `..feat.models.v1`) plus a new `\"feat\": generate_feat_schema` entry in `_GENERATORS` (keep the dict's existing key order/style — check whether it's alphabetical or something else, and insert consistently).\n- `general/tools/_packaged_data.py::read_packaged_text`/`packaged_data_path` — used by all three new resource modules and (already, from Phase 2) `get_feat_example`/`get_feat_template`. **Note: Phase 2's `get_feat_example`/`get_feat_template` tools already call `read_packaged_text(\"feat\", \"example\"/\"template\")` but currently raise `FileNotFoundError`** since the packaged files didn't exist yet — once you add `feat/data/feat_example.md`/`feat_template.md` in this phase, those two Phase-2 tools will start working correctly for the first time; if Phase 2 left placeholder/skip markers in `tests/feat/tools/test_get_feat_example.py`/`test_get_feat_template.py` expecting `FileNotFoundError`, **update those two test files now** to assert the real happy-path content instead (read them first to see exactly what Phase 2 left there).\n\n### Generating `docs/feat_schema.json` and the packaged copy\n\nAfter adding `generate_feat_schema()`/`_GENERATORS[\"feat\"]`, run:\n\n```\nuv run --frozen specmgr schema --type feat\nuv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data\n```\n\n(check the exact CLI flag names/defaults by reading `commands/schema.py`'s Typer command definition first — mirror exactly how `dec`'s own two-invocation pattern is documented in `.pre-commit-config.yaml`'s `specmgr-schema-dec-package` hook entry, i.e. `specmgr schema --type dec` alone writes `docs/dec_schema.json`, and `--output-dir src/biz/dfch/specmgr/dec/data` is the second, packaged-copy variant). Do **not** wire a pre-commit hook or CI step for this yet — that is explicitly Phase 5 Task 5.2's job, not yours. Just generate both files once now, by hand, and commit them as regular tracked files.\n\n### Test coverage required (mirror `tests/dec/resources/`'s layout and depth — check that directory first)\n\n`tests/feat/resources/`: tests for `feat_schema` (returns parsed JSON, matches `docs/feat_schema.json`'s content, has the right `$comment`/`$schema` keys), `feat_example` (returns the packaged example text, and that text round-trips through `parse_feat` byte-exact per ACC-001's own requirement — re-verify this here too since it's directly relevant to ACC-005/ACC-007), `feat_template` (returns the packaged template text, and that it successfully parses via `parse_feat` even though it's not a \"realistic\" document).\n\n### Quality gate for this phase (run yourself, report the actual command output back to me)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\n\nAlso run `uv run --frozen specmgr unused-code` and report its output.\n\n### Also required\n\n- Update the plan README's Progress section (Current Status, a new dated Recent Updates entry, Decisions Made for any judgment calls) — edit `/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md` directly, and flip Task 3.1–3.7's checkboxes/status fields in the Task List to reflect completion.\n- Do NOT commit. Do NOT post to GitHub issue #31. Stop after the quality gate is green and the plan README is updated, and report back a summary including: files created, key design/judgment calls, and the full quality gate command output/evidence.\n- If you hit anything genuinely blocking, STOP immediately and report back rather than improvising a workaround.\n"
}
````

**Output:**

```
<task id="ses_fac885325ffe1576oSx4SrcYjK" state="completed">
<task_result>
Working tree is clean of anything unexpected, nothing staged/committed, exactly as required.

## Summary

**Phase 3 (Resources + packaged data + schema) complete.** All 7 tasks (3.1–3.7) done.

### Files created
- `src/biz/dfch/specmgr/feat/data/feat_example.md` — byte-identical copy of `tests/feat/models/v1/data/feat_reference.md` (verified via `diff`)
- `src/biz/dfch/specmgr/feat/data/feat_template.md` — all-sections placeholder skeleton, `status: planning`, verified round-trips through `parse_feat`
- `src/biz/dfch/specmgr/feat/data/feat_create_instructions.md` / `feat_update_instructions.md` — narrated instruction bodies mirroring `dec`'s two files, tailored to `feat`'s actual schema/status set/generic-dispatch MCP surface
- `src/biz/dfch/specmgr/feat/data/feat_schema.json` — packaged copy, byte-identical to `docs/feat_schema.json`
- `src/biz/dfch/specmgr/feat/resources/feat_schema.py`, `feat_example.py`, `feat_template.py` — 1:1 mirrors of `dec.resources`'s equivalents
- `tests/feat/resources/test_feat_schema.py`, `test_feat_example.py`, `test_feat_template.py` — 20 new tests

### Files modified
- `src/biz/dfch/specmgr/commands/schema.py` — added `generate_feat_schema()` + `"feat"` entry in `_GENERATORS` (inserted alphabetically between `"dec"` and `"gol"`)
- `src/biz/dfch/specmgr/feat/resources/__init__.py` — now imports/registers the three resource modules
- `src/biz/dfch/specmgr/feat/__init__.py` — docstring updated to reflect Phase 3 completion
- `tests/feat/tools/test_get_feat_example.py` / `test_get_feat_template.py` — replaced Phase-2 `FileNotFoundError`-only placeholder tests with real happy-path assertions now that the packaged files exist
- `docs/feat_schema.json` — new (generated, untracked)
- `.specmgr/feat/feat-31-feature/README.md` — Task List checkboxes flipped, Current Status/Recent Updates/Decisions Made updated, version bumped 1.8.0→1.9.0

### Design/judgment calls (recorded in README Decisions Made)
1. `feat_template.md`'s placeholder `id` is `feat-0-template` (a `feat-NNN-slug`-shaped placeholder, not a UUID-shaped one like GOL/DEC use) — matches `feat`'s own folder-name addressing convention; `parse_feat` has no path/folder check at the model layer so this is valid.
2. `_GENERATORS` insertion confirmed alphabetical before inserting `"feat"` between `"dec"`/`"gol"`.
3. `feat_template.md` uses one entry each for `Updates`/`Decisions Made` (not two like the example/reference) — enough to prove round-trip while keeping it a short skeleton, matching DEC/GOL's own template precedent.

### Quality gate (all green)
```

uv run --frozen ruff format --check → 1277 files already formatted
uv run --frozen ruff check → All checks passed!
uv run --frozen vulture src/ whitelist.py --min-confidence 60 → clean, no output
uv run --frozen python -m unittest discover -v -s tests -t . -p "test\_\*.py" → Ran 2199 tests, OK (up from 2179)
uv run --frozen specmgr unused-code → No unused code found

```

Nothing committed, nothing staged — working tree left as-is for your review. Ready for Phase 4 (`feat/prompts/`) once you're satisfied.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

Let's verify.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short"
}
```

**Output:**

```
 M .specmgr/feat/feat-31-feature/README.md
 M src/biz/dfch/specmgr/commands/schema.py
 M src/biz/dfch/specmgr/feat/__init__.py
 M src/biz/dfch/specmgr/feat/resources/__init__.py
 M tests/feat/tools/test_get_feat_example.py
 M tests/feat/tools/test_get_feat_template.py
?? docs/feat_schema.json
?? src/biz/dfch/specmgr/feat/data/
?? src/biz/dfch/specmgr/feat/resources/feat_example.py
?? src/biz/dfch/specmgr/feat/resources/feat_schema.py
?? src/biz/dfch/specmgr/feat/resources/feat_template.py
?? tests/feat/resources/test_feat_example.py
?? tests/feat/resources/test_feat_schema.py
?? tests/feat/resources/test_feat_template.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.8s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && diff src/biz/dfch/specmgr/feat/data/feat_example.md tests/feat/models/v1/data/feat_reference.md && echo IDENTICAL\ndiff docs/feat_schema.json src/biz/dfch/specmgr/feat/data/feat_schema.json && echo IDENTICAL2"
}
```

**Output:**

```
IDENTICAL
IDENTICAL2

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.7s)

Both byte-identical as required. Let's check `feat_template.md` parses and view resource modules briefly.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/data/feat_template.md"
}
```

**Output:**

```
---
created: 2026-08-30
id: feat-0-template
status: planning
type: feat
updated: 2026-08-30
version: 1.0.0
---

# Feature: Level 1 Heading is the Title of the Feature

## Plan

### Overview

A short description of what this feature is and why it exists.

### Requirements

- REQ-001: A short, verifiable description of one specific requirement this feature must satisfy.

### Acceptance Criteria

- [ ] ACC-001: A short, verifiable description of how you know this requirement has been met.

### Scope

#### Included

- A bullet list of what this feature covers.

#### Explicitly Out Of Scope

- A bullet list of what this feature deliberately does not cover.

### Dependencies

#### Depends On

- A bullet list of things this feature needs first. Optional.

#### Blocks

- A bullet list of things that cannot start until this feature ships. Optional.

### Design Notes

Free-form design rationale, schema sketches, etc. Optional.

### Related Decisions

- A bullet list of related ADR or DEC ids, each with a short description. Optional.

### Task List

#### Phase 1: Placeholder Phase

- [ ] Task 1.1: A short description of one task in this phase.

## Progress

### Current Status

**As of 2026-08-30**: A short, free-form narrative of where things stand.

### Blockers

- A short description of an open blocker. Optional.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-30 00:00:00.000Z — Created

A short lead paragraph describing this update.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-30 00:00:00.000Z — Placeholder decision

A short lead paragraph describing the decision and its rationale.

### Related PRs / Commits

- A bullet list of related pull requests or commits. Optional.

### More Information

This optional section can contain additional information. There is no defined format for this section.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo === && uv run --frozen ruff check 2>&1 | tail -5"
}
```

**Output:**

```
1277 files already formatted
===
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -20; echo EXIT:$?"
}
```

**Output:**

```
EXIT:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 83.7s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(Ran|OK|FAILED|ERROR)\""
}
```

**Output:**

```
Range mode must raise the domain's own not-found error for an unknown id. ... ok
Ran 2199 tests in 79.927s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.8s)

All green: 2199 tests, ruff clean, vulture clean. Let's double check `commands/schema.py` insertion and the resource modules quickly.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"\\\"feat\\\"\\|generate_feat_schema\" src/biz/dfch/specmgr/commands/schema.py"
}
```

**Output:**

```
224:def generate_feat_schema() -> str:
247:    "feat": generate_feat_schema,

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 124.7s)

Good. Let's commit Phase 3.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)\n\n- feat/data/: feat_example.md (byte-identical to feat_reference.md),\n  feat_template.md (all-sections placeholder, round-trips via parse_feat),\n  feat_create_instructions.md, feat_update_instructions.md,\n  feat_schema.json (packaged copy)\n- commands/schema.py: generate_feat_schema() + _GENERATORS[\\\"feat\\\"]\n- docs/feat_schema.json (generated)\n- feat/resources/: feat_schema.py, feat_example.py, feat_template.py\n- Tests: tests/feat/resources/ (20 new tests); updated\n  tests/feat/tools/test_get_feat_example.py/test_get_feat_template.py\n  to assert real happy-path content now that packaged files exist\" -q && git log --oneline -3"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................

<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -3 && git status --short"
}
```

**Output:**

```
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript
M  .specmgr/feat/feat-31-feature/README.md
A  docs/feat_schema.json
M  src/biz/dfch/specmgr/commands/schema.py
M  src/biz/dfch/specmgr/feat/__init__.py
A  src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
A  src/biz/dfch/specmgr/feat/data/feat_example.md
A  src/biz/dfch/specmgr/feat/data/feat_schema.json
A  src/biz/dfch/specmgr/feat/data/feat_template.md
A  src/biz/dfch/specmgr/feat/data/feat_update_instructions.md
M  src/biz/dfch/specmgr/feat/resources/__init__.py
A  src/biz/dfch/specmgr/feat/resources/feat_example.py
A  src/biz/dfch/specmgr/feat/resources/feat_schema.py
A  src/biz/dfch/specmgr/feat/resources/feat_template.py
A  tests/feat/resources/test_feat_example.py
A  tests/feat/resources/test_feat_schema.py
A  tests/feat/resources/test_feat_template.py
M  tests/feat/tools/test_get_feat_example.py
M  tests/feat/tools/test_get_feat_template.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 125.6s)

The commit didn't complete (still staged) — it timed out during the pre-commit unittest hook. Let's retry with a longer timeout.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git commit -m \"feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)\n\n- feat/data/: feat_example.md (byte-identical to feat_reference.md),\n  feat_template.md (all-sections placeholder, round-trips via parse_feat),\n  feat_create_instructions.md, feat_update_instructions.md,\n  feat_schema.json (packaged copy)\n- commands/schema.py: generate_feat_schema() + _GENERATORS[\\\"feat\\\"]\n- docs/feat_schema.json (generated)\n- feat/resources/: feat_schema.py, feat_example.py, feat_template.py\n- Tests: tests/feat/resources/ (20 new tests); updated\n  tests/feat/tools/test_get_feat_example.py/test_get_feat_template.py\n  to assert real happy-path content now that packaged files exist\" -q"
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................

<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.0s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && ps aux | grep -E \"git|pytest|unittest\" | grep -v grep; ls -la .git/index.lock 2>/dev/null; git status --short | head -5; git log --oneline -3"
}
```

**Output:**

```
user       14277  0.0  0.2 1518516432 262424 ?   Sl   09:57   0:01 /usr/share/code/code /usr/share/code/resources/app/node_modules.asar.unpacked/@github/copilot-linux-x64/index.js --headless --no-auto-update --log-level info --stdio --no-auto-login
M  .specmgr/feat/feat-31-feature/README.md
A  docs/feat_schema.json
M  src/biz/dfch/specmgr/commands/schema.py
M  src/biz/dfch/specmgr/feat/__init__.py
A  src/biz/dfch/specmgr/feat/data/feat_create_instructions.md
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 178.3s)

No lock file, no running processes — the earlier commit attempt was killed by the shell timeout, and the tree is still staged. Let's retry with a much larger timeout since the full unittest suite is now slower (~80s) plus other hooks.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git commit -m \"feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)\n\n- feat/data/: feat_example.md (byte-identical to feat_reference.md),\n  feat_template.md (all-sections placeholder, round-trips via parse_feat),\n  feat_create_instructions.md, feat_update_instructions.md,\n  feat_schema.json (packaged copy)\n- commands/schema.py: generate_feat_schema() + _GENERATORS[\\\"feat\\\"]\n- docs/feat_schema.json (generated)\n- feat/resources/: feat_schema.py, feat_example.py, feat_template.py\n- Tests: tests/feat/resources/ (20 new tests); updated\n  tests/feat/tools/test_get_feat_example.py/test_get_feat_template.py\n  to assert real happy-path content now that packaged files exist\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Failed
- hook id: specmgr-docs
- exit code: 1
- files were modified by this hook

✓ Wrote 361 module file(s) to /home/user/src/biz.dfch.SpecMgr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/GENERATED.md
diff --git a/docs/GENERATED.md b/docs/GENERATED.md
index 6665fd9..4d70aa1 100644
--- a/docs/GENERATED.md
+++ b/docs/GENERATED.md
@@ -100,7 +100,10 @@ First-line docstrings from each module, organized by domain:
 - `feat/models/v1/parser.py` — Parse raw feature (FEAT) ``.md`` text into a :class:`FeatDocument`.
 - `feat/models/v1/summary.py` — Pydantic model for one line of FEAT listing output (Phase 2, ``list_feat``).
 - `feat/prompts/__init__.py` — Feature (FEAT) MCP prompts.
-- `feat/resources/__init__.py` — Feature (FEAT) MCP resources.
+- `feat/resources/__init__.py` — MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).
+- `feat/resources/feat_example.py` — Resource: specmgr://feat/example (feat-31 Task 3.5).
+- `feat/resources/feat_schema.py` — Resource: specmgr://feat/schema (feat-31 Task 3.5, packaged data).
+- `feat/resources/feat_template.py` — Resource: specmgr://feat/template (feat-31 Task 3.5).
 - `feat/tools/__init__.py` — MCP tool wrappers for features (mirrors ``dec/tools/``'s own shape).
 - `feat/tools/_io.py` — Thin file read helpers over ``parse_feat`` (Task 2.2).
 - `feat/tools/_lock.py` — Per-document and global in-process locks guarding feature mutations (Task 2.2).
@@ -422,4 +425,4 @@ First-line docstrings from each module, organized by domain:
 
 ## Test Coverage
 
-**Test files**: 278
+**Test files**: 281
diff --git a/docs/api/README.md b/docs/api/README.md
index 74f5d3d..d76f604 100644
--- a/docs/api/README.md
+++ b/docs/api/README.md
@@ -83,7 +83,10 @@ Auto-generated API documentation for `biz.dfch.specmgr`.
 - [`biz.dfch.specmgr.feat.models.v1.parser`](biz.dfch.specmgr.feat.models.v1.parser.md) — Parse raw feature (FEAT) ``.md`` text into a :class:`FeatDocument`.
 - [`biz.dfch.specmgr.feat.models.v1.summary`](biz.dfch.specmgr.feat.models.v1.summary.md) — Pydantic model for one line of FEAT listing output (Phase 2, ``list_feat``).
 - [`biz.dfch.specmgr.feat.prompts`](biz.dfch.specmgr.feat.prompts.md) — Feature (FEAT) MCP prompts.
-- [`biz.dfch.specmgr.feat.resources`](biz.dfch.specmgr.feat.resources.md) — Feature (FEAT) MCP resources.
+- [`biz.dfch.specmgr.feat.resources`](biz.dfch.specmgr.feat.resources.md) — MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).
+- [`biz.dfch.specmgr.feat.resources.feat_example`](biz.dfch.specmgr.feat.resources.feat_example.md) — Resource: specmgr://feat/example (feat-31 Task 3.5).
+- [`biz.dfch.specmgr.feat.resources.feat_schema`](biz.dfch.specmgr.feat.resources.feat_schema.md) — Resource: specmgr://feat/schema (feat-31 Task 3.5, packaged data).
+- [`biz.dfch.specmgr.feat.resources.feat_template`](biz.dfch.specmgr.feat.resources.feat_template.md) — Resource: specmgr://feat/template (feat-31 Task 3.5).
 - [`biz.dfch.specmgr.feat.tools`](biz.dfch.specmgr.feat.tools.md) — MCP tool wrappers for features (mirrors ``dec/tools/``'s own shape).
 - [`biz.dfch.specmgr.feat.tools._io`](biz.dfch.specmgr.feat.tools._io.md) — Thin file read helpers over ``parse_feat`` (Task 2.2).
 - [`biz.dfch.specmgr.feat.tools._lock`](biz.dfch.specmgr.feat.tools._lock.md) — Per-document and global in-process locks guarding feature mutations (Task 2.2).
diff --git a/docs/api/biz.dfch.specmgr.commands.schema.md b/docs/api/biz.dfch.specmgr.commands.schema.md
index 101395f..cc376ab 100644
--- a/docs/api/biz.dfch.specmgr.commands.schema.md
+++ b/docs/api/biz.dfch.specmgr.commands.schema.md
@@ -39,6 +39,20 @@ the same byte-identical-output/drift-detection reason as
 :func:`generate_req_schema`.
 
 
+### `generate_feat_schema() -> str`
+
+Generate FEAT's JSON Schema (2020-12 dialect) from ``FeatDocument.model_json_schema()``.
+
+Mirrors :func:`generate_req_schema` exactly, but for ``feat.models.v1``:
+the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
+default), and ``"$comment"`` holds ``feat.models.v1.SCHEMA_COMMENT_VERSION``
+(currently ``"v1"``) instead of REQ's own version token.
+
+Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
+the same byte-identical-output/drift-detection reason as
+:func:`generate_req_schema`.
+
+
 ### `generate_gol_schema() -> str`
 
 Generate GOL's JSON Schema (2020-12 dialect) from ``GolDocument.model_json_schema()``.
diff --git a/docs/api/biz.dfch.specmgr.feat.md b/docs/api/biz.dfch.specmgr.feat.md
index b71f139..fb30318 100644
--- a/docs/api/biz.dfch.specmgr.feat.md
+++ b/docs/api/biz.dfch.specmgr.feat.md
@@ -14,15 +14,18 @@ under the base directory -- see ``feat/tools/_paths.py`` (added in Phase 2)
 for the bespoke addressing this requires, in contrast to every other
 domain's shared ``general/tools/_doc_paths.py``.
 
-**Current status: Phase 2 (tools) complete.** ``models/v1/`` (Phase 1) and
-``tools/`` (Phase 2) are fully implemented; ``resources`` and ``prompts``
-remain empty sub-packages, built out in Phases 3-4 of the linked feature
-plan. ``feat`` already follows the ``sop``-style generic-dispatch MCP
-surface (ADR 36905d5b-8057-4294-8665-c7eed5534db0): ``create_feat``,
-``parse_feat``, ``list_feat``, ``get_feat``, ``get_feat_example``,
-``get_feat_template``, ``delete_feat`` (stub), ``validate_feat``, plus
-``type="feat"`` entries in the generic ``update``/``set_status`` tools --
-no ``update_feat``/``set_status_feat`` of its own.
+**Current status: Phase 3 (resources + packaged data + schema) complete.**
+``models/v1/`` (Phase 1), ``tools/`` (Phase 2), ``data/`` and ``resources``
+(Phase 3) are fully implemented; ``prompts`` remains an empty sub-package,
+built out in Phase 4 of the linked feature plan. ``feat`` already follows
+the ``sop``-style generic-dispatch MCP surface (ADR
+36905d5b-8057-4294-8665-c7eed5534db0): ``create_feat``, ``parse_feat``,
+``list_feat``, ``get_feat``, ``get_feat_example``, ``get_feat_template``,
+``delete_feat`` (stub), ``validate_feat``, plus ``type="feat"`` entries in
+the generic ``update``/``set_status`` tools -- no ``update_feat``/
+``set_status_feat`` of its own. Resources: ``specmgr://feat/schema``,
+``specmgr://feat/example``, ``specmgr://feat/template`` (no ``/{id}``, no
+``/list``).
 
 Import this package to register every feature tool/prompt/resource against
 the shared ``mcp`` application instance at once::
diff --git a/docs/api/biz.dfch.specmgr.feat.resources.md b/docs/api/biz.dfch.specmgr.feat.resources.md
index 6261709..68b4890 100644
--- a/docs/api/biz.dfch.specmgr.feat.resources.md
+++ b/docs/api/biz.dfch.specmgr.feat.resources.md
@@ -1,10 +1,21 @@
 # `biz.dfch.specmgr.feat.resources`
 
-Feature (FEAT) MCP resources.
-
-**Phase 0 scaffolding only.** Populated in Phase 3 of
-``.specmgr/feat/feat-31-feature/README.md``: ``specmgr://feat/schema``,
-``specmgr://feat/example``, ``specmgr://feat/template`` -- no ``/{id}``
-(id-based reads are ``get_feat``-only, ADR
-ddfb1109-422d-4507-8dbc-dc5e4bec9614) and no ``/list`` (``list_feat`` ships
-as a paged tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
+MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).
+
+``feat_schema`` registers the persisted-JSON-Schema resource
+(``specmgr://feat/schema``). ``feat_example`` registers the packaged sample
+feature document resource (``specmgr://feat/example``). ``feat_template``
+registers the packaged feature template resource (``specmgr://feat/template``)
+-- every section present, populated with short placeholder ("blind text")
+content that still round-trips through ``parse_feat`` (the DEC/RSK
+precedent). Import this package to register all feature resources against
+the shared ``mcp`` application instance::
+
+    from biz.dfch.specmgr.feat import resources  # noqa: F401 (side-effects only)
+
+Like DEC/GOL, FEAT has no by-id single-document *resource* -- id-based reads
+go through the ``get_feat`` tool only (``feat.tools.get_feat``), and no
+``specmgr://feat/list`` resource either -- listing goes through the
+``list_feat`` ``@mcp.tool()`` (``feat.tools.list_feat``) from the start, per
+ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
+(``max_results``/``offset``) could be accepted.

specmgr mcp-docs.........................................................Failed
- hook id: specmgr-mcp-docs
- exit code: 1
- files were modified by this hook

✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/MCP.md
diff --git a/docs/MCP.md b/docs/MCP.md
index 5926f96..131193b 100644
--- a/docs/MCP.md
+++ b/docs/MCP.md
@@ -3,7 +3,7 @@
 Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
 do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 
-28 resource(s), 1 resource template(s), 87 tool(s), 21 prompt(s).
+31 resource(s), 1 resource template(s), 87 tool(s), 21 prompt(s).
 
 ## Table of Contents
 
@@ -19,6 +19,9 @@ do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 | [`specmgr://dec/example`](#resource-dec_example) | A complete, valid sample decision document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`specmgr://dec/schema`](#resource-dec_schema) | The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document. |
 | [`specmgr://dec/template`](#resource-dec_template) | A DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision. |
+| [`specmgr://feat/example`](#resource-feat_example) | A complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
+| [`specmgr://feat/schema`](#resource-feat_schema) | The generated FEAT JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document. |
+| [`specmgr://feat/template`](#resource-feat_template) | A FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature. |
 | [`specmgr://gol/example`](#resource-gol_example) | A complete, valid sample goal document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`specmgr://gol/schema`](#resource-gol_schema) | The generated GOL JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document. |
 | [`specmgr://gol/template`](#resource-gol_template) | A GOL document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new goal. |
@@ -66,6 +69,27 @@ The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` a
 
 A DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision.
 
+### Resource: feat_example
+
+- **URI:** `specmgr://feat/example`
+- **MIME type:** `text/markdown`
+
+A complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.
+
+### Resource: feat_schema
+
+- **URI:** `specmgr://feat/schema`
+- **MIME type:** `application/json`
+
+The generated FEAT JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document.
+
+### Resource: feat_template
+
+- **URI:** `specmgr://feat/template`
+- **MIME type:** `text/markdown`
+
+A FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature.
+
 ### Resource: gol_example
 
 - **URI:** `specmgr://gol/example`

specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 172.5s)

Docs drift again — let's stage and re-commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)\n\n- feat/data/: feat_example.md (byte-identical to feat_reference.md),\n  feat_template.md (all-sections placeholder, round-trips via parse_feat),\n  feat_create_instructions.md, feat_update_instructions.md,\n  feat_schema.json (packaged copy)\n- commands/schema.py: generate_feat_schema() + _GENERATORS[\\\"feat\\\"]\n- docs/feat_schema.json (generated)\n- feat/resources/: feat_schema.py, feat_example.py, feat_template.py\n- Tests: tests/feat/resources/ (20 new tests); updated\n  tests/feat/tools/test_get_feat_example.py/test_get_feat_template.py\n  to assert real happy-path content now that packaged files exist\n- Regenerate docs/api + docs/GENERATED.md + docs/MCP.md\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -4"
}
```

**Output:**

```
c6f8b9c feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

Phase 3 committed (`c6f8b9c`). Moving on to Phase 4.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Scaffolding (already complete, verify only)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models + parser (feat/models/v1/)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources + packaged data + schema",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Prompts",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 5: Cross-cutting registration + final verification",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Scaffolding (already complete, verify only)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models + parser (feat/models/v1/)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources + packaged data + schema",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Prompts",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 5: Cross-cutting registration + final verification",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

Let's check `dec/prompts/` precedent before writing the Phase 4 prompt.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && find src/biz/dfch/specmgr/dec/prompts -type f -name \"*.py\" | sort && echo --- && cat src/biz/dfch/specmgr/dec/prompts/create_dec.py"
}
```

**Output:**

```
src/biz/dfch/specmgr/dec/prompts/create_dec.py
src/biz/dfch/specmgr/dec/prompts/__init__.py
src/biz/dfch/specmgr/dec/prompts/update_dec.py
---
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

"""``@mcp.prompt()``: create_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Decision (DEC) document using the existing
``dec/tools/``/``dec/resources/`` surface (``list_dec``,
``specmgr://dec/template``/``specmgr://dec/example``,
``specmgr://dec/schema``, ``create_dec``, ``validate_dec``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_dec`` builds the entire DEC frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body keeps the ADR's
general structure (context, drivers, considered options, outcome, related
artifacts, pros/cons, more information, updates) but is narrated through
DEC's own section names, with ``## Pros and Cons`` -- not ADR's
``## Pros and Cons of the Options`` -- as the options container.

Naming note: this prompt is named ``create_dec``, the same name as the
``@mcp.tool()`` in ``dec/tools/create_dec.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.create_gol``/``req.prompts.create_req``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_dec``, building a ``TodoWrite`` list, eliciting the
mandatory context and outcome plus each optional section via the
``question`` tool, then calling ``create_dec``) -- it never calls
``TodoWrite``/``question``/``list_dec``/``create_dec`` itself, exactly like
every other prompt in this codebase (see ``tsk.prompts.implement_task``'s
own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``dec/data/dec_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the DEC
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_dec",
    title="Create a decision",
    description=(
        "Guides the LLM through checking for an existing similar decision, gathering the "
        "required information, and driving create_dec/validate_dec to author a new DEC document."
    ),
)
def create_dec(topic: str) -> str:
    """Return instructional text for drafting a new decision about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the decision to be drafted -- becomes
        the seed for the document's title and context.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_dec``, or ``create_dec``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("dec", "create_instructions", "md"))
    return template.substitute(topic=topic)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/dec/prompts/update_dec.py src/biz/dfch/specmgr/dec/prompts/__init__.py"
}
```

**Output:**

```
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

"""``@mcp.prompt()``: update_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Decision (DEC) document by id, using the
existing ``dec/tools/`` surface (``get_dec``, ``validate_dec``) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="dec"``; ``get_dec``'s ``raw=True`` parameter serves the line-range
flow's line numbers). There is no ``specmgr://dec/{id}`` resource to point
at -- id-based reads always go through the ``get_dec`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: DEC's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="dec"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="dec"``) -- mirroring
``req.prompts.update_req``/``rsk.prompts.update_risk``.

Like ``req.prompts.update_req``/``rsk.prompts.update_risk`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via `get_dec`, showing which sections are present vs. empty, eliciting
revisions via the `question` tool, then calling the generic `update` tool
with `type="dec"`, with the generic `set_status` tool with `type="dec"`
mentioned as a separate, optional follow-up) -- it never calls
``get_dec``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``dec/data/dec_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the DEC markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_dec",
    title="Update a decision",
    description=(
        "Guides the LLM through revising an existing decision by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_dec(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the decision identified by ``id``.

    Parameters
    ----------
    id:
        The existing document's specmgr-assigned identifier.
    instructions:
        Free-text description of the requested change. When absent, the
        returned instructions tell the LLM to ask the user first rather
        than guessing.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``get_dec``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("dec", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
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

"""MCP prompt wrappers for Decisions (Task 4.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``dec/tools/``/``dec/resources/`` surface in the right order --
one module per prompt, mirroring ``gol/prompts/``'s own one-module-per-
prompt split. Import this package to register all decision prompts at
once::

    from biz.dfch.specmgr.dec import prompts  # noqa: F401 (side-effects only)
"""

from .create_dec import create_dec
from .update_dec import update_dec

__all__ = [
    "create_dec",
    "update_dec",
]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/data/feat_create_instructions.md"
}
```

**Output:**

```
You are drafting a new Feature (FEAT) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_feat` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_feat` builds
id/type/status/created/updated/version automatically -- a fresh
`feat-NNN-slug` id, `status="planning"` always (never caller-supplied on
create), and plain `YYYY-MM-DD` dates (not the microsecond timestamp most
other domains use).

Make a todo list and use the question tool.

## 0. Check for an existing feature on this topic first

Call the `list_feat` tool before creating anything. If a feature with a
similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_feat` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new feature.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# Feature: {title}` -- H1, mandatory, free-form title after the fixed
  `Feature: ` prefix.
- `## Plan` -- mandatory container, no own text:
  - `### Overview` -- mandatory prose: what this feature is and why it
    exists.
  - `### Requirements` -- mandatory bullet list, at least one item, each
    line `REQ-NNN: {text}`.
  - `### Acceptance Criteria` -- mandatory checklist, at least one item,
    each line `- [ ] ACC-NNN: {text}` (or `- [x] ...` once verified).
  - `### Scope` -- mandatory container, no own text, holding two
    mandatory leaves: `#### Included` and `#### Explicitly Out Of Scope`.
  - `### Dependencies` -- optional container, no own text, holding two
    independently optional leaves: `#### Depends On` and `#### Blocks`.
  - `### Design Notes` -- optional prose.
  - `### Related Decisions` -- optional bullet list of related ADR/DEC
    ids with a short description each.
  - `### Task List` -- mandatory container, no own text, holding at
    least one `#### Phase N: {title}` entry (unpadded phase number, e.g.
    "Phase 1"), each with its own flat checklist of at least one
    `- [ ] .../- [x] ...` task item.
- `## Progress` -- mandatory container, no own text:
  - `### Current Status` -- mandatory prose: where things stand today.
  - `### Blockers` -- optional prose/list of open blockers.
  - `### Updates` -- mandatory, an optional leading HTML comment (e.g. an
    ordering hint) followed by at least one `#### {timestamp} — {title}`
    entry, newest-first, where `{timestamp}` is
    `yyyy-MM-dd HH:mm:ss.fff±HH:mm` (or `Z` for UTC), each with a lead
    paragraph.
  - `### Decisions Made` -- optional, same shape as `### Updates` (same
    timestamp format, same newest-first ordering, at least one entry once
    the section is present at all).
  - `### Related PRs / Commits` -- optional freeform list.
  - `### More Information` -- optional freeform supplementary text.

Section order is binding, exactly as listed above. There is no
`update_feat`/`set_status_feat` tool of its own -- later changes go
through the generic `update`/`set_status` tools with `type="feat"` (see
step 5).

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `Overview`,
`Requirements`, `Acceptance Criteria`, `Scope` (both `Included` and
`Explicitly Out Of Scope`), `Task List`, `Current Status`, `Updates`, and
each optional section (`Dependencies`, `Design Notes`,
`Related Decisions`, `Blockers`, `Decisions Made`,
`Related PRs / Commits`, `More Information`). Then use the `question`
tool to elicit the mandatory fields first, then each optional field in
turn, explicitly telling the user they may skip any optional field they
cannot or do not want to answer yet.

## 3. Use the template/example/schema as references

Fetch `specmgr://feat/template` or `specmgr://feat/example` as a
starting point/style reference, then check `specmgr://feat/schema` (the
generated JSON Schema) to confirm field names and constraints before
drafting the body. Do not invent field names or section headings that
are not present there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_feat(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically, including the
   `feat-NNN-slug` id derived from the H1 title. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_feat(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_feat`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this feature should go through the `update_feat`
prompt (or directly through the generic `update(id, type="feat", content)`
and `set_status(id, type="feat", status)` tools), not by re-running this
prompt.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

This is thorough and already exists. Let's check the update instructions file too, briefly.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/data/feat_update_instructions.md"
}
```

**Output:**

```
You are revising an existing Feature (FEAT) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below. There is no
`update_feat`/`set_status_feat` tool of its own -- `feat` uses the
generic `update`/`set_status` tools with `type="feat"` from day one.

## 1. Read current state first

Call `get_feat(id)` to load the document's current frontmatter and
body. Never assume prior state -- the on-disk `README.md` file is
always the source of truth and may have been hand-edited since you last
saw it -- direct hand/agent editing of `.specmgr/feat/<id>/README.md` is
the normal, sanctioned workflow for this domain, not just an MCP-tool
convenience.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which sections are present and which are empty

Show the user which of the sections -- the mandatory `Overview`,
`Requirements`, `Acceptance Criteria`, `Scope` (`Included` and
`Explicitly Out Of Scope`), `Task List`, `Current Status`, and `Updates`
(always present), and the optional `Dependencies` (`Depends On`/
`Blocks`), `Design Notes`, `Related Decisions`, `Blockers`,
`Decisions Made`, `Related PRs / Commits`, and `More Information` --
are already present with content and which are still absent. Use the
`question` tool to ask which ones (if any) they want to add to or
revise.

## 4. Map the requested change to the right tool

- A change to the body -- any of the sections listed in step 3 -- ->
  the generic `update` tool called with `type="feat"`: a
  **line-range replace** for a localized change, or a **whole-body replace**
  otherwise. `content` is body markdown only (no frontmatter block) in
  both cases.
  - **Line-range replace** (a localized change -- one paragraph, list
    item, or section): first call `get_feat(id, raw=True)` to see the
    exact body text, identify the 1-based, inclusive line range to
    replace -- the `N+1` position is end-of-body: `begin = end = N+1`
    appends after the last line, `end = N+1` extends the range through
    the last line -- and call `update(id, type="feat", content, begin=..., end=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical. Adding a new `### Updates`/`### Decisions Made` entry
    is typically a line-range insert directly below the section's
    optional leading comment (or directly below the `### Updates`/
    `### Decisions Made` heading if no comment is present) -- new entries
    go first, since both sections are newest-first, enforced.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="feat", content)`
    with no `begin`/`end` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes (a plain
    `YYYY-MM-DD` date, not the microsecond timestamp most other domains
    use).
- A change to `status` -> `set_status(id, type="feat", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: planning, progress, review, done (no hyphens -- `progress`, not
  `in-progress`). Mention this as a separate, optional follow-up -- e.g.
  `progress` once implementation starts, `review` once implementation is
  done and pending verification, `done` once shipped -- do not call
  `set_status` unless the user actually asks for a status change.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://feat/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_feat(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 563.7s)

Excellent, both instruction files are already high quality. Now let's delegate Phase 4.

**Tool: task**

**Input:**

````json
{
  "description": "Implement feat-31 Phase 4: prompts",
  "subagent_type": "phase-implementer",
  "prompt": "Implement **Phase 4: Prompts** of the feature plan at:\n\n`/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md`\n\nRead that entire README.md first (Overview, REQ-008, ACC-006, Design Notes' \"Prompts are narrated instructions only\" paragraph). Phases 0-3 are complete and committed: `feat/models/v1/`, `feat/tools/` (bespoke folder-per-document addressing, all 8 tools, generic `update`/`set_status` dispatch for `type=\"feat\"`), and `feat/resources/` + `feat/data/` (including the already-written `feat/data/feat_create_instructions.md` and `feat/data/feat_update_instructions.md` — these two packaged instruction files ALREADY EXIST from Phase 3 and are complete/correct; read them, don't rewrite them) are all fully implemented and tested. Do not touch `feat/models/`, `feat/tools/`, `feat/resources/`, `feat/data/`, or anything under Phase 5.\n\n### Phase 4 tasks (verbatim from the plan's Task List)\n\n- Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`), `update_feat.py` (`update_feat(id, instructions=None)`), `__init__.py` — depends on: Task 3.3.\n- Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task 4.1.\n- Task 4.3: Phase-end quality gate + commit + comment on issue #31 — depends on: Task 4.2. **Do NOT commit yourself and do NOT post the GitHub comment** — the orchestrator (me) will do both after independently verifying your work. Just run the quality gate and report the evidence.\n\n### Precedent to mirror closely (read these directly, they are your primary reference)\n\n- `src/biz/dfch/specmgr/dec/prompts/create_dec.py`, `update_dec.py`, `__init__.py` — mirror each 1:1 for `feat`'s equivalents. Both are thin wrappers: read the already-existing packaged instructions file via `general.tools._packaged_data.read_packaged_text(\"feat\", \"create_instructions\"/\"update_instructions\", \"md\")`, substitute via `string.Template` (`$topic` for create, `$id`/`$instructions` for update), and return the result. Neither prompt calls `TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/`update`/`set_status` itself — they only narrate that the calling LLM should (same contract every existing prompt in this codebase follows).\n- `feat/data/feat_create_instructions.md` and `feat/data/feat_update_instructions.md` (already exist, Phase 3) use `$topic` and `$id`/`$instructions` placeholders respectively — confirm the exact placeholder names by reading both files, then match them exactly in your `Template.substitute(...)` calls.\n- `update_dec.py`'s fallback text pattern for a missing `instructions` argument (`instructions or \"(not given -- ask the user before making any change)\"`) — `feat_update_instructions.md` already says `Requested change: $instructions` and later checks for the literal string `\"(not given)\"` in step 2's prose (\"If 'Requested change' above says '(not given)'...\") — read that file's exact wording and make sure your fallback string matches word-for-word what the instructions file checks for (it may be `\"(not given)\"` alone rather than DEC's longer fallback text — verify and use whatever `feat_update_instructions.md` actually expects, not DEC's own wording, since these can differ between domains).\n\n### Test coverage required (mirror `tests/dec/prompts/`'s layout and depth — check that directory first)\n\n`tests/feat/prompts/`: `test_create_feat.py` (returns a string, `$topic` substituted correctly, mentions the expected tool-call sequence), `test_update_feat.py` (returns a string, `$id` substituted correctly, `instructions=None` produces the expected \"not given\" fallback text, a given `instructions` value is substituted verbatim). Per ACC-006 (\"verified by walking both packaged instruction files end to end against a real document, not just asserting their static text\"), also write at least one test per prompt that goes further than a bare string-contains check — e.g. actually exercise the narrated tool sequence against a real temp `SPECMGR_FEAT_DIR` (create a feature via `create_feat`, then follow what `update_feat`'s instructions say to do via `get_feat`/`update`/`set_status`, asserting the end state is correct) to prove the narration is not just plausible text but an actually-followable, correct sequence — check `tests/dec/prompts/` for whether it already does this kind of \"walk the instructions\" test and mirror that approach if so; if `tests/dec/prompts/` only does static-text assertions, do the deeper walk-through test yourself for `feat` anyway, since ACC-006 explicitly requires it for this feature.\n\n### Quality gate for this phase (run yourself, report the actual command output back to me)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\n\nAlso run `uv run --frozen specmgr unused-code` and report its output.\n\n### Also required\n\n- Update the plan README's Progress section (Current Status, a new dated Recent Updates entry, Decisions Made for any judgment calls) — edit `/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md` directly, and flip Task 4.1–4.3's checkboxes/status fields in the Task List to reflect completion.\n- Do NOT commit. Do NOT post to GitHub issue #31. Stop after the quality gate is green and the plan README is updated, and report back a summary including: files created, key design/judgment calls, and the full quality gate command output/evidence.\n- If you hit anything genuinely blocking, STOP immediately and report back rather than improvising a workaround.\n"
}
````

**Output:**

```
<task id="ses_fac71e79dffeALJkd3N91IDDLX" state="completed">
<task_result>
## Phase 4 (Prompts) — Complete

### Tasks completed
- **Task 4.1**: `feat/prompts/create_feat.py`, `update_feat.py`, `__init__.py` — 1:1 mirrors of `dec.prompts.create_dec`/`update_dec`. Both are thin `string.Template` wrappers around the already-existing Phase-3 packaged instruction files; neither calls any tool itself.
- **Task 4.2**: `tests/feat/prompts/test_create_feat.py`, `test_update_feat.py` — 29 new tests, all green.
- **Task 4.3**: Phase-end quality gate run (below). No commit made, no GitHub comment posted (left to orchestrator per your instructions).

### Files changed
- New: `src/biz/dfch/specmgr/feat/prompts/create_feat.py`, `src/biz/dfch/specmgr/feat/prompts/update_feat.py`, `tests/feat/prompts/test_create_feat.py`, `tests/feat/prompts/test_update_feat.py` (staged with `git add`)
- Modified: `src/biz/dfch/specmgr/feat/prompts/__init__.py` (now imports/exports both prompts), `src/biz/dfch/specmgr/feat/__init__.py` (docstring updated to reflect Phase 4 complete), `.specmgr/feat/feat-31-feature/README.md` (Task List checkboxes, Current Status, new Recent Updates entry, two new Decisions Made entries, version bump 1.9.0 → 1.10.0)

### Design/judgment calls made
1. **`update_feat`'s missing-`instructions` fallback is exactly `"(not given)"`**, not DEC's longer `"(not given -- ask the user before making any change)"` — verified `feat_update_instructions.md`'s step 2 literally checks for the substring `"(not given)"` with a closing paren immediately after "given"; DEC's own phrasing would *not* satisfy that literal check (its own paren closes only at the end of the whole clause). Recorded as a Decisions Made entry.
2. **Added the ACC-006-required "walk the instructions end to end" tests** beyond `tests/dec/prompts/`'s static-text-only depth — confirmed `tests/dec/prompts/` (test_create_dec.py/test_update_dec.py) does *not* do this, so I added `TestCreateFeatInstructionsWalkthrough`/`TestUpdateFeatInstructionsWalkthrough`, which drive the real `create_feat`/`get_feat`/`list_feat`/`update`/`set_status` tools against a temp `SPECMGR_FEAT_DIR`, following the packaged instructions' narrated steps literally (dedup-check → create; get → line-range update → whole-body update → set_status). Recorded as a Decisions Made entry.

### Quality gate (all commands run from repo root)
```

uv run --frozen ruff format --check → "1284 files already formatted"
uv run --frozen ruff check → "All checks passed!"
uv run --frozen vulture src/ whitelist.py --min-confidence 60 → (no output = clean)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test\_\*.py"
→ Ran 2228 tests ... OK (up from 2199 after Phase 3, +29 new)
uv run --frozen specmgr unused-code → "No unused code found in .../src."

```

### For the orchestrator to verify
- Please independently confirm the fallback-string reasoning (`"(not given)"` vs DEC's phrase) since it's a literal-substring judgment call.
- Working tree is clean of anything unexpected — only the 4 new files (staged) and 3 modified files listed above. No commit made, no issue comment posted.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.9s)

Let's verify.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short"
}
```

**Output:**

```
 M .specmgr/feat/feat-31-feature/README.md
 M src/biz/dfch/specmgr/feat/__init__.py
 M src/biz/dfch/specmgr/feat/prompts/__init__.py
A  src/biz/dfch/specmgr/feat/prompts/create_feat.py
A  src/biz/dfch/specmgr/feat/prompts/update_feat.py
A  tests/feat/prompts/test_create_feat.py
A  tests/feat/prompts/test_update_feat.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.1s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && cat src/biz/dfch/specmgr/feat/prompts/update_feat.py"
}
```

**Output:**

```
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

"""``@mcp.prompt()``: update_feat (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Feature (FEAT) document by id, using the
existing ``feat/tools/`` surface (``get_feat``, ``validate_feat``) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="feat"``; ``get_feat``'s ``raw=True`` parameter serves the
line-range flow's line numbers). There is no ``specmgr://feat/{id}``
resource to point at -- id-based reads always go through the ``get_feat``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ADR's ``update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: FEAT's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="feat"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="feat"``) -- mirroring
``dec.prompts.update_dec``/``req.prompts.update_req``. There is no
``update_feat``/``set_status_feat`` tool of FEAT's own (REQ-006, ADR
36905d5b-8057-4294-8665-c7eed5534db0).

Like ``dec.prompts.update_dec``/``req.prompts.update_req`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing -- matching
the literal ``"(not given)"`` string that
``feat/data/feat_update_instructions.md`` itself checks for in its own
step 2 ("If 'Requested change' above says '(not given)', ask the user...").

This prompt only ever *narrates* the revision flow (reading current state
via ``get_feat``, showing which sections are present vs. empty, eliciting
revisions via the ``question`` tool, then calling the generic ``update``
tool with ``type="feat"``, with the generic ``set_status`` tool with
``type="feat"`` mentioned as a separate, optional follow-up) -- it never
calls ``get_feat``/``question``/``update``/``set_status`` itself, exactly
like every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the FEAT markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_feat",
    title="Update a feature",
    description=(
        "Guides the LLM through revising an existing feature by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_feat(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the feature identified by ``id``.

    Parameters
    ----------
    id:
        The existing document's ``feat-NNN-slug`` identifier (the
        containing folder's own name).
    instructions:
        Free-text description of the requested change. When absent, the
        returned instructions tell the LLM to ask the user first rather
        than guessing.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``get_feat``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("feat", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given)",
    )

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

The fallback string `"(not given)"` correctly matches the instructions file's literal check. Now let's run the quality gate independently.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo === && uv run --frozen ruff check 2>&1 | tail -5"
}
```

**Output:**

```
1284 files already formatted
===
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.1s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -20; echo EXIT:$?"
}
```

**Output:**

```
EXIT:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 66.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(Ran|OK|FAILED|ERROR)\""
}
```

**Output:**

```
Range mode must raise the domain's own not-found error for an unknown id. ... ok
Ran 2228 tests in 62.576s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

All green: 2228 tests. Let's check the walkthrough tests briefly.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"class \\|def test_\" tests/feat/prompts/test_create_feat.py tests/feat/prompts/test_update_feat.py"
}
```

**Output:**

```
tests/feat/prompts/test_create_feat.py:50:class TestCreateFeatPrompt(unittest.TestCase):
tests/feat/prompts/test_create_feat.py:53:    def test_returns_substituted_instruction_text(self):
tests/feat/prompts/test_create_feat.py:60:    def test_instructions_match_packaged_file(self):
tests/feat/prompts/test_create_feat.py:66:    def test_mentions_duplicate_check_tool(self):
tests/feat/prompts/test_create_feat.py:71:    def test_mentions_todowrite_list(self):
tests/feat/prompts/test_create_feat.py:96:    def test_mentions_question_tool(self):
tests/feat/prompts/test_create_feat.py:101:    def test_mentions_allowing_skip_for_optional_sections(self):
tests/feat/prompts/test_create_feat.py:106:    def test_mentions_starting_point_resources(self):
tests/feat/prompts/test_create_feat.py:113:    def test_mentions_tool_sequence_in_order(self):
tests/feat/prompts/test_create_feat.py:127:    def test_mentions_no_frontmatter_to_draft(self):
tests/feat/prompts/test_create_feat.py:134:    def test_mentions_update_feat_for_later_revisions(self):
tests/feat/prompts/test_create_feat.py:142:    def test_instructions_loaded_from_packaged_data_file(self):
tests/feat/prompts/test_create_feat.py:157:    def test_raises_file_not_found_when_instructions_missing(self):
tests/feat/prompts/test_create_feat.py:216:class TempFeatDirTestCase(unittest.TestCase):
tests/feat/prompts/test_create_feat.py:225:class TestCreateFeatInstructionsWalkthrough(TempFeatDirTestCase):
tests/feat/prompts/test_create_feat.py:234:    def test_dedup_check_then_create_produces_a_real_document(self) -> None:
tests/feat/prompts/test_update_feat.py:54:class TestUpdateFeatPrompt(unittest.TestCase):
tests/feat/prompts/test_update_feat.py:57:    def test_returns_substituted_id(self):
tests/feat/prompts/test_update_feat.py:64:    def test_instructions_interpolated_when_given(self):
tests/feat/prompts/test_update_feat.py:71:    def test_prompts_for_input_when_instructions_absent(self):
tests/feat/prompts/test_update_feat.py:78:    def test_instructions_match_packaged_file(self):
tests/feat/prompts/test_update_feat.py:84:    def test_mentions_get_feat_tool_first(self):
tests/feat/prompts/test_update_feat.py:91:    def test_mentions_both_generic_mutation_tools(self):
tests/feat/prompts/test_update_feat.py:98:    def test_mentions_range_update_flow(self):
tests/feat/prompts/test_update_feat.py:116:    def test_mentions_showing_which_sections_are_present(self):
tests/feat/prompts/test_update_feat.py:142:    def test_mentions_eliciting_revisions_via_question_tool(self):
tests/feat/prompts/test_update_feat.py:147:    def test_mentions_whole_body_replace_warning(self):
tests/feat/prompts/test_update_feat.py:152:    def test_mentions_status_never_via_update(self):
tests/feat/prompts/test_update_feat.py:157:    def test_mentions_closed_status_set_no_hyphens(self):
tests/feat/prompts/test_update_feat.py:163:    def test_mentions_set_status_as_separate_optional_followup(self):
tests/feat/prompts/test_update_feat.py:170:    def test_instructions_loaded_from_packaged_data_file(self):
tests/feat/prompts/test_update_feat.py:185:    def test_raises_file_not_found_when_instructions_missing(self):
tests/feat/prompts/test_update_feat.py:244:class TempFeatDirTestCase(unittest.TestCase):
tests/feat/prompts/test_update_feat.py:253:class TestUpdateFeatInstructionsWalkthrough(TempFeatDirTestCase):
tests/feat/prompts/test_update_feat.py:262:    def test_get_then_range_update_then_whole_body_then_set_status(self) -> None:

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

Thorough coverage with a real end-to-end walkthrough test satisfying ACC-006. Let's check the README update and commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff --cached .specmgr/feat/feat-31-feature/README.md | head -30"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.7s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .specmgr/feat/feat-31-feature/README.md | head -60"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-31-feature/README.md b/.specmgr/feat/feat-31-feature/README.md
index 90c44ed..3c8cdf8 100644
--- a/.specmgr/feat/feat-31-feature/README.md
+++ b/.specmgr/feat/feat-31-feature/README.md
@@ -3,7 +3,7 @@ created: 2026-08-30
 id: feat-31-feature
 status: in-progress
 updated: 2026-08-30
-version: 1.9.0
+version: 1.10.0
 ---
 
 # Feature: Formalize the Feature artifact type ("feat")
@@ -715,13 +715,23 @@ discipline.
 
 #### Phase 4: Prompts
 
-- [ ] Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`),
+- [x] Task 4.1: `feat/prompts/` — `create_feat.py` (`create_feat(topic)`),
   `update_feat.py` (`update_feat(id, instructions=None)`), `__init__.py`
-  — depends on: Task 3.3 — status: not-started
-- [ ] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
-  4.1 — status: not-started
-- [ ] Task 4.3: Phase-end quality gate + commit + comment on issue #31 —
-  depends on: Task 4.2 — status: not-started
+  — depends on: Task 3.3 — status: completed (2026-08-30). Both are thin
+  `string.Template` wrappers around the Phase-3 packaged instructions
+  files, 1:1 mirrors of `dec.prompts.create_dec`/`update_dec` — neither
+  calls `TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/
+  `update`/`set_status` itself.
+- [x] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
+  4.1 — status: completed (2026-08-30), 29 new tests
+  (`test_create_feat.py`/`test_update_feat.py`), including a real
+  "walk the instructions end to end" test per prompt (ACC-006) against a
+  temporary `SPECMGR_FEAT_DIR` — see Decisions Made for the fallback
+  string judgment call.
+- [x] Task 4.3: Phase-end quality gate + commit + comment on issue #31 —
+  depends on: Task 4.2 — status: completed (2026-08-30) — quality gate
+  green; **commit and issue comment left to the orchestrator**, per this
+  phase's own task instructions (implementer runs the gate only).
 
 #### Phase 5: Cross-cutting registration
 
@@ -877,6 +887,41 @@ gate green: `ruff format --check`/`ruff check` clean, `vulture src/ whitelist.py
 `specmgr unused-code` clean, full `unittest` suite green (2199 tests, up
 from 2179 after Phase 2). Phase 4 (`feat/prompts/`) is next.
 
+**As of 2026-08-30 (Phase 4 complete)**: `feat/prompts/` is fully
+implemented — `create_feat.py` (`create_feat(topic)`), `update_feat.py`
+(`update_feat(id, instructions=None)`), `__init__.py`, each a 1:1 mirror
+of `dec.prompts.create_dec`/`update_dec`: thin `string.Template` wrappers
+that read the already-existing Phase-3 packaged instructions files
+(`feat_create_instructions.md`/`feat_update_instructions.md`) and
+substitute `$topic` / `$id`+`$instructions`, never calling
+`TodoWrite`/`question`/`list_feat`/`get_feat`/`create_feat`/`update`/
+`set_status` themselves. `update_feat`'s missing-`instructions` fallback
+is the literal string `"(not given)"` (not DEC's longer
+`"(not given -- ask the user before making any change)"`), matching
+`feat_update_instructions.md`'s own step 2 check verbatim (`If "Requested
+change" above says "(not given)"...`). 29 new tests across

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 147.5s)

This looks solid — README correctly updated (unstaged, needs adding). Let's commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): implement Feature (feat) prompts (Phase 4)\n\n- feat/prompts/: create_feat.py (create_feat(topic)), update_feat.py\n  (update_feat(id, instructions=None)) -- 1:1 mirrors of\n  dec.prompts.create_dec/update_dec, thin string.Template wrappers\n  around the Phase-3 packaged instructions files\n- Tests: tests/feat/prompts/ (29 new tests, incl. end-to-end\n  instructions-walkthrough tests per ACC-006)\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Failed
- hook id: specmgr-docs
- exit code: 1
- files were modified by this hook

✓ Wrote 363 module file(s) to /home/user/src/biz.dfch.SpecMgr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/GENERATED.md
diff --git a/docs/GENERATED.md b/docs/GENERATED.md
index 4d70aa1..450b6ea 100644
--- a/docs/GENERATED.md
+++ b/docs/GENERATED.md
@@ -99,7 +99,9 @@ First-line docstrings from each module, organized by domain:
 - `feat/models/v1/frontmatter.py` — Feature (FEAT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
 - `feat/models/v1/parser.py` — Parse raw feature (FEAT) ``.md`` text into a :class:`FeatDocument`.
 - `feat/models/v1/summary.py` — Pydantic model for one line of FEAT listing output (Phase 2, ``list_feat``).
-- `feat/prompts/__init__.py` — Feature (FEAT) MCP prompts.
+- `feat/prompts/__init__.py` — MCP prompt wrappers for Features (Task 4.1).
+- `feat/prompts/create_feat.py` — ``@mcp.prompt()``: create_feat (Task 4.1).
+- `feat/prompts/update_feat.py` — ``@mcp.prompt()``: update_feat (Task 4.1).
 - `feat/resources/__init__.py` — MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).
 - `feat/resources/feat_example.py` — Resource: specmgr://feat/example (feat-31 Task 3.5).
 - `feat/resources/feat_schema.py` — Resource: specmgr://feat/schema (feat-31 Task 3.5, packaged data).
@@ -425,4 +427,4 @@ First-line docstrings from each module, organized by domain:
 
 ## Test Coverage
 
-**Test files**: 281
+**Test files**: 283
diff --git a/docs/api/README.md b/docs/api/README.md
index d76f604..934084d 100644
--- a/docs/api/README.md
+++ b/docs/api/README.md
@@ -82,7 +82,9 @@ Auto-generated API documentation for `biz.dfch.specmgr`.
 - [`biz.dfch.specmgr.feat.models.v1.frontmatter`](biz.dfch.specmgr.feat.models.v1.frontmatter.md) — Feature (FEAT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
 - [`biz.dfch.specmgr.feat.models.v1.parser`](biz.dfch.specmgr.feat.models.v1.parser.md) — Parse raw feature (FEAT) ``.md`` text into a :class:`FeatDocument`.
 - [`biz.dfch.specmgr.feat.models.v1.summary`](biz.dfch.specmgr.feat.models.v1.summary.md) — Pydantic model for one line of FEAT listing output (Phase 2, ``list_feat``).
-- [`biz.dfch.specmgr.feat.prompts`](biz.dfch.specmgr.feat.prompts.md) — Feature (FEAT) MCP prompts.
+- [`biz.dfch.specmgr.feat.prompts`](biz.dfch.specmgr.feat.prompts.md) — MCP prompt wrappers for Features (Task 4.1).
+- [`biz.dfch.specmgr.feat.prompts.create_feat`](biz.dfch.specmgr.feat.prompts.create_feat.md) — ``@mcp.prompt()``: create_feat (Task 4.1).
+- [`biz.dfch.specmgr.feat.prompts.update_feat`](biz.dfch.specmgr.feat.prompts.update_feat.md) — ``@mcp.prompt()``: update_feat (Task 4.1).
 - [`biz.dfch.specmgr.feat.resources`](biz.dfch.specmgr.feat.resources.md) — MCP resource registrations for Feature (FEAT) documents (feat-31 Task 3.5).
 - [`biz.dfch.specmgr.feat.resources.feat_example`](biz.dfch.specmgr.feat.resources.feat_example.md) — Resource: specmgr://feat/example (feat-31 Task 3.5).
 - [`biz.dfch.specmgr.feat.resources.feat_schema`](biz.dfch.specmgr.feat.resources.feat_schema.md) — Resource: specmgr://feat/schema (feat-31 Task 3.5, packaged data).
diff --git a/docs/api/biz.dfch.specmgr.feat.md b/docs/api/biz.dfch.specmgr.feat.md
index fb30318..05eb67e 100644
--- a/docs/api/biz.dfch.specmgr.feat.md
+++ b/docs/api/biz.dfch.specmgr.feat.md
@@ -14,18 +14,19 @@ under the base directory -- see ``feat/tools/_paths.py`` (added in Phase 2)
 for the bespoke addressing this requires, in contrast to every other
 domain's shared ``general/tools/_doc_paths.py``.
 
-**Current status: Phase 3 (resources + packaged data + schema) complete.**
+**Current status: Phase 4 (prompts) complete.**
 ``models/v1/`` (Phase 1), ``tools/`` (Phase 2), ``data/`` and ``resources``
-(Phase 3) are fully implemented; ``prompts`` remains an empty sub-package,
-built out in Phase 4 of the linked feature plan. ``feat`` already follows
-the ``sop``-style generic-dispatch MCP surface (ADR
+(Phase 3), and ``prompts`` (Phase 4) are all fully implemented; only Phase 5
+(cross-cutting registration) of the linked feature plan remains. ``feat``
+already follows the ``sop``-style generic-dispatch MCP surface (ADR
 36905d5b-8057-4294-8665-c7eed5534db0): ``create_feat``, ``parse_feat``,
 ``list_feat``, ``get_feat``, ``get_feat_example``, ``get_feat_template``,
 ``delete_feat`` (stub), ``validate_feat``, plus ``type="feat"`` entries in
 the generic ``update``/``set_status`` tools -- no ``update_feat``/
 ``set_status_feat`` of its own. Resources: ``specmgr://feat/schema``,
 ``specmgr://feat/example``, ``specmgr://feat/template`` (no ``/{id}``, no
-``/list``).
+``/list``). Prompts: ``create_feat(topic)``/``update_feat(id, instructions=None)`` -- narrated instruction flows only,
+reading packaged instructions data from ``feat/data/``.
 
 Import this package to register every feature tool/prompt/resource against
 the shared ``mcp`` application instance at once::
diff --git a/docs/api/biz.dfch.specmgr.feat.prompts.md b/docs/api/biz.dfch.specmgr.feat.prompts.md
index dc4b666..48822cb 100644
--- a/docs/api/biz.dfch.specmgr.feat.prompts.md
+++ b/docs/api/biz.dfch.specmgr.feat.prompts.md
@@ -1,9 +1,12 @@
 # `biz.dfch.specmgr.feat.prompts`
 
-Feature (FEAT) MCP prompts.
+MCP prompt wrappers for Features (Task 4.1).
 
-**Phase 0 scaffolding only.** Populated in Phase 4 of
-``.specmgr/feat/feat-31-feature/README.md``: ``create_feat(topic)`` and
-``update_feat(id, instructions=None)`` -- narrated instruction flows only
-(no tool calls of their own), reading packaged instructions data from
-``feat/data/``.
+Each returns plain instructional text (auto-wrapped as a single
+``UserMessage`` by the SDK) that guides an LLM through driving the
+existing ``feat/tools/``/``feat/resources/`` surface in the right order --
+one module per prompt, mirroring ``dec/prompts/``'s own one-module-per-
+prompt split. Import this package to register all feature prompts at
+once::
+
+    from biz.dfch.specmgr.feat import prompts  # noqa: F401 (side-effects only)

specmgr mcp-docs.........................................................Failed
- hook id: specmgr-mcp-docs
- exit code: 1
- files were modified by this hook

✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/MCP.md
diff --git a/docs/MCP.md b/docs/MCP.md
index 131193b..c5bed8e 100644
--- a/docs/MCP.md
+++ b/docs/MCP.md
@@ -3,7 +3,7 @@
 Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
 do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 
-31 resource(s), 1 resource template(s), 87 tool(s), 21 prompt(s).
+31 resource(s), 1 resource template(s), 87 tool(s), 23 prompt(s).
 
 ## Table of Contents
 
@@ -1221,6 +1221,7 @@ Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the c
 | [`create_adr`](#prompt-create_adr) | Guides the LLM through checking for an existing similar ADR, gathering the required information, and driving create_adr/option_create/set_status/validate_adr to author a new MADR-4.0.0-based Architecture Decision Record. |
 | [`create_adr_test`](#prompt-create_adr_test) | Experimental, strictly step-gated variant of create_adr for A/B comparison: the same MADR-4.0.0 structure and create_adr/option_create/set_status/validate_adr tool sequence, rewritten as hard numbered gates instead of narrated steps. |
 | [`create_dec`](#prompt-create_dec) | Guides the LLM through checking for an existing similar decision, gathering the required information, and driving create_dec/validate_dec to author a new DEC document. |
+| [`create_feat`](#prompt-create_feat) | Guides the LLM through checking for an existing similar feature, gathering the required information, and driving create_feat/validate_feat to author a new FEAT document. |
 | [`create_gol`](#prompt-create_gol) | Guides the LLM through checking for an existing similar goal, gathering the required information, and driving create_gol/validate_gol to author a new GOL document. |
 | [`create_prb`](#prompt-create_prb) | Guides the LLM through checking for an existing similar problem statement, interviewing the user for the 5W2H current-state questions, synthesizing the Summary and Gap, and driving create_prb/validate_prb to author a new PRB document. |
 | [`create_qa`](#prompt-create_qa) | Guides the LLM through checking for an existing similar QA document, gathering answers to ISO/IEC 25010:2023 characteristic-relevant questions, and driving create_qa/validate_qa to author a new QA document. |
@@ -1232,6 +1233,7 @@ Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the c
 | [`update_adr`](#prompt-update_adr) | Guides the LLM through revising an existing ADR by id: reading current state, applying the requested change with the right tool, and validating. |
 | [`update_adr_test`](#prompt-update_adr_test) | Experimental, strictly step-gated variant of update_adr for A/B comparison: the same read-first/map-to-tool/validate-last flow, rewritten as hard numbered gates instead of narrated steps. |
 | [`update_dec`](#prompt-update_dec) | Guides the LLM through revising an existing decision by id: reading current state, applying the requested change with the right tool, and validating. |
+| [`update_feat`](#prompt-update_feat) | Guides the LLM through revising an existing feature by id: reading current state, applying the requested change with the right tool, and validating. |
 | [`update_gol`](#prompt-update_gol) | Guides the LLM through revising an existing goal by id: reading current state, showing which sections are present vs. empty, eliciting revisions, applying the change with the right tool, and validating. |
 | [`update_prb`](#prompt-update_prb) | Guides the LLM through revising an existing problem statement by id: reading current state, showing which of the 7 5W2H questions are answered, eliciting revisions, re-synthesizing Summary/Gap, applying the change with the right tool, and validating. |
 | [`update_qa`](#prompt-update_qa) | Guides the LLM through revising an existing QA document by id: reading current state, applying the requested change with the right tool, and validating. |
@@ -1278,6 +1280,14 @@ Guides the LLM through checking for an existing similar decision, gathering the
 | --- | --- | --- |
 | `topic` | Yes |  |
 
+### Prompt: create_feat
+
+Guides the LLM through checking for an existing similar feature, gathering the required information, and driving create_feat/validate_feat to author a new FEAT document.
+
+| Argument | Required | Description |
+| --- | --- | --- |
+| `topic` | Yes |  |
+
 ### Prompt: create_gol
 
 Guides the LLM through checking for an existing similar goal, gathering the required information, and driving create_gol/validate_gol to author a new GOL document.
@@ -1370,6 +1380,15 @@ Guides the LLM through revising an existing decision by id: reading current stat
 | `id` | Yes |  |
 | `instructions` | No |  |
 
+### Prompt: update_feat
+
+Guides the LLM through revising an existing feature by id: reading current state, applying the requested change with the right tool, and validating.
+
+| Argument | Required | Description |
+| --- | --- | --- |
+| `id` | Yes |  |
+| `instructions` | No |  |
+
 ### Prompt: update_gol
 
 Guides the LLM through revising an existing goal by id: reading current state, showing which sections are present vs. empty, eliciting revisions, applying the change with the right tool, and validating.

specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 142.8s)

Docs drift again, expected. Stage and re-commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): implement Feature (feat) prompts (Phase 4)\n\n- feat/prompts/: create_feat.py (create_feat(topic)), update_feat.py\n  (update_feat(id, instructions=None)) -- 1:1 mirrors of\n  dec.prompts.create_dec/update_dec, thin string.Template wrappers\n  around the Phase-3 packaged instructions files\n- Tests: tests/feat/prompts/ (29 new tests, incl. end-to-end\n  instructions-walkthrough tests per ACC-006)\n- Regenerate docs/api + docs/GENERATED.md + docs/MCP.md\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -5"
}
```

**Output:**

```
b974b63 feat(feat-31): implement Feature (feat) prompts (Phase 4)
c6f8b9c feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

Phase 4 committed (`b974b63`). Now moving to Phase 5 — the final, cross-cutting phase.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Scaffolding (already complete, verify only)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models + parser (feat/models/v1/)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources + packaged data + schema",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Prompts",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 5: Cross-cutting registration + final verification",
      "status": "in_progress",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Scaffolding (already complete, verify only)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models + parser (feat/models/v1/)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources + packaged data + schema",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Prompts",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 5: Cross-cutting registration + final verification",
    "status": "in_progress",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '1,50p' src/biz/dfch/specmgr/server.py | head -60"
}
```

**Output:**

```
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

"""MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

Registers the following resources and tools so far (plan §8, §9a):

Resources
---------
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/req_schema.json``) so it works from a
                        real, non-editable install.
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/uc_schema.json``) so it works from a
                        real, non-editable install.
specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
specmgr://uc/template -- A use-case template (every field present, placeholder text)
                          as raw markdown.
specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/tsk_schema.json``) so it works from a
                        real, non-editable install.
specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
specmgr://tsk/template -- A task list template (every field present, placeholder text)
                          as raw markdown.
specmgr://qa/schema --  The generated QA JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/qa_schema.json``) so it works from a
                        real, non-editable install.
specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
                        markdown.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"^from \\.\\| import \\|^import \" src/biz/dfch/specmgr/server.py | tail -20"
}
```

**Output:**

```
223:from __future__ import annotations
225:from collections.abc import AsyncGenerator
226:from contextlib import asynccontextmanager
228:from mcp.server import MCPServer
251:from . import adr, dec, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"dec\" src/biz/dfch/specmgr/server.py"
}
```

**Output:**

```
79:specmgr://dec/schema -- The generated DEC JSON Schema, read from a packaged data copy
80:                        (kept in sync with ``docs/dec_schema.json``) so it works from a
82:specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
83:specmgr://dec/template -- A decision template (every field present, placeholder text)
106: ``specmgr://dec/{id}`` resource either, for the same reason -- id-based reads go
107: through the ``get_dec`` tool only, and there is also no
108: ``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged tool from
149:  Decision tools (``dec/tools/``): ``parse_dec``, ``get_dec`` (``raw=True`` returns the
150:frontmatter-stripped body text verbatim instead of the parsed document), ``list_dec``,
151:  ``get_dec_example``,
152:  ``get_dec_template``, ``create_dec``, ``delete_dec``
153:  (stub, not yet implemented), ``validate_dec``.
157:``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``; optional 1-based inclusive
161:``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``adr``), also bumping
195:Decision prompts (``dec/prompts/``): ``create_dec``, ``update_dec`` --
197:``question``-tool-driven interview flow; ``create_dec`` first checks
198:``list_dec`` for a near-duplicate decision.
207:domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and later ``ac``) is a
215:module, next to the existing ``adr``/``dec``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
217:decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, and ``dec``
248:# decorators to actually run.
251:from . import adr, dec, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

Let's view the whole relevant docstring section (lines 60-225) for full context.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py",
  "offset": 60,
  "limit": 165
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py</path>
<type>file</type>
<content>
60: specmgr://gol/schema -- The generated GOL JSON Schema, read from a packaged data copy
61:                          (kept in sync with ``docs/gol_schema.json``) so it works from a
62:                          real, non-editable install.
63: specmgr://gol/example -- A complete, valid sample goal document as raw markdown.
64: specmgr://gol/template -- A goal template (every field present,
65:                            placeholder text) as raw markdown.
66: specmgr://rsk/schema -- The generated RSK JSON Schema, read from a packaged data copy
67:                         (kept in sync with ``docs/rsk_schema.json``) so it works from a
68:                         real, non-editable install.
69: specmgr://rsk/example -- A complete, valid sample risk document as raw markdown.
70: specmgr://rsk/template -- A risk template (every field present, placeholder text)
71:                            as raw markdown.
72: specmgr://rsk/tara --     The TARA risk-response framework: what TARA is (Transfer,
73:                            Accept, Reduce, Avoid), the four valid `## Strategy` words,
74:                            and when and how to apply each -- raw markdown domain-knowledge
75:                            guidance.
76: specmgr://rsk/risk-matrix -- The 5x5 risk matrix: probability/impact scale anchors, the
77:                            zone table, and the product thresholds (what 'high risk' and
78:                            'low risk' mean) -- raw markdown domain-knowledge guidance.
79: specmgr://dec/schema -- The generated DEC JSON Schema, read from a packaged data copy
80:                         (kept in sync with ``docs/dec_schema.json``) so it works from a
81:                         real, non-editable install.
82: specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
83: specmgr://dec/template -- A decision template (every field present, placeholder text)
84:                           as raw markdown.
85: specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
86:                         characteristics (and sub-characteristics), each with a description.
87: 
88: REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
89: through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
90: UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
91: reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
92: resource either -- id-based reads go through the ``get_tsk`` tool only, and
93: there never was such a resource to remove in the first place. QA has no
94: ``specmgr://qa/{id}`` resource either, for the same reason -- id-based reads go
95: through the ``get_qa`` tool only. PRB has no ``specmgr://prb/{id}`` resource
96: either, for the same reason -- id-based reads go through the ``get_prb`` tool
97: only, and there is also no ``specmgr://prb/list`` resource -- ``list_prb``
98: ships as a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
99: GOL has no ``specmgr://gol/{id}`` resource either, for the same reason --
100: id-based reads go through the ``get_gol`` tool only, and there is also no
101:  ``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged tool from
102:  day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). RSK has no
103:  ``specmgr://rsk/{id}`` resource either, for the same reason -- id-based reads go
104:  through the ``get_rsk`` tool only, and there never was such a resource to
105:  remove in the first place. DEC has no
106:  ``specmgr://dec/{id}`` resource either, for the same reason -- id-based reads go
107:  through the ``get_dec`` tool only, and there is also no
108:  ``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged tool from
109:  day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
110: 
111: Tools
112: -----
113: ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
114: ``update_section``, ``option_list``, ``option_create``,
115: ``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
116: Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc`` (``raw=True`` returns the
117: frontmatter-stripped body text verbatim instead of the parsed document), ``list_uc``,
118: ``get_uc_example``,
119: ``get_uc_template``, ``create_uc``, ``delete_uc``
120: (stub, not yet implemented), ``validate_uc``.
121: Requirement tools (``req/tools/``): ``parse_req``, ``get_req`` (``raw=True`` returns the
122: frontmatter-stripped body text verbatim instead of the parsed document), ``list_req``,
123: ``get_req_example``,
124: ``get_req_template``, ``create_req``, ``delete_req``
125: (stub, not yet implemented), ``validate_req``.
126: Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk`` (``raw=True`` returns the
127: frontmatter-stripped body text verbatim instead of the parsed document), ``list_tsk``,
128: ``get_tsk_example``,
129: ``get_tsk_template``, ``create_tsk``, ``delete_tsk``
130: (stub, not yet implemented), ``validate_tsk``.
131: QA tools (``qa/tools/``): ``parse_qa``, ``get_qa`` (``raw=True`` returns the
132: frontmatter-stripped body text verbatim instead of the parsed document), ``list_qa``,
133: ``get_qa_example``,
134: ``get_qa_template``, ``create_qa``, ``delete_qa``
135: (stub, not yet implemented), ``validate_qa``.
136: Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb`` (``raw=True`` returns
137: the frontmatter-stripped body text verbatim instead of the parsed document), ``list_prb``,
138: ``get_prb_example``, ``get_prb_template``, ``create_prb``,
139: ``delete_prb`` (stub, not yet implemented), ``validate_prb``.
140: Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol`` (``raw=True`` returns the
141: frontmatter-stripped body text verbatim instead of the parsed document), ``list_gol``,
142: ``get_gol_example``, ``get_gol_template``, ``create_gol``,
143:  ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
144:  Risk tools (``rsk/tools/``): ``parse_rsk``, ``get_rsk`` (``raw=True`` returns the
145: frontmatter-stripped body text verbatim instead of the parsed document), ``list_rsk``,
146:  ``get_rsk_example``,
147:  ``get_rsk_template``, ``create_rsk``, ``delete_rsk``
148:  (stub, not yet implemented), ``validate_rsk``.
149:   Decision tools (``dec/tools/``): ``parse_dec``, ``get_dec`` (``raw=True`` returns the
150: frontmatter-stripped body text verbatim instead of the parsed document), ``list_dec``,
151:   ``get_dec_example``,
152:   ``get_dec_template``, ``create_dec``, ``delete_dec``
153:   (stub, not yet implemented), ``validate_dec``.
154:   General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
155: preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
156: existing document's content across the eight whole-body domains (``type`` is one of
157: ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``; optional 1-based inclusive
158: ``begin``/``end`` body-line range with the ``N+1`` end-of-body sentinel; the spliced
159: result is validated as a whole document before anything is written); ``set_status`` --
160: replace an existing document's status across all nine domains (``type`` is one of
161: ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``adr``), also bumping
162: ``updated`` (the eight whole-body domains) and leaving the body untouched;
163: ``superseded_by`` is ``adr``-only (it composes the status as
164: ``"superseded by {superseded_by}"``);
165: ``webfetch`` -- fetch a URL over HTTP GET with a
166: bearer token, restricted to a configured base URL (``SPECMGR_WEBFETCH_BASE_URL``,
167: ``SPECMGR_WEBFETCH_BEARER``).
168: 
169: Prompts
170: -------
171: ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
172: text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
173: §11).
174: Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
175: instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
176: Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
177: text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
178: reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
179: items, and uses the ``question`` tool to resolve ambiguity before proceeding.
180: QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
181: appends a fresh batch of unanswered interview questions (each with an empty
182: `_(awaiting response)_` placeholder) to an existing QA document, for
183: ``Elicitation Context`` or one or more of the nine ISO/IEC 25010:2023 quality
184: characteristics.
185: Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
186: instructional text guiding an LLM through a ``TodoWrite`` + ``question``-tool-
187: driven 5W2H interview flow, including agent-synthesized ``Summary``/``Gap``
188: text.
189: Goal prompts (``gol/prompts/``): ``create_gol``, ``update_gol`` --
190: instructional text guiding an LLM through a ``TodoWrite`` +
191: ``question``-tool-driven interview flow over the goal's mandatory
192: ``statement``/``Source`` fields and its optional sections.
193: Risk prompts (``rsk/prompts/``): ``create_risk``, ``update_risk`` -- instructional
194: text guiding an LLM through the RSK tool sequence above.
195: Decision prompts (``dec/prompts/``): ``create_dec``, ``update_dec`` --
196: instructional text guiding an LLM through a ``TodoWrite`` +
197: ``question``-tool-driven interview flow; ``create_dec`` first checks
198: ``list_dec`` for a near-duplicate decision.
199: General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
200: older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
201: ``README.md`` into an optional sibling ``history.md``, per ADR
202: e369ee2e-3353-4f92-991c-6367d76d832e.
203: 
204: Modules are grouped domain-first
205: (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
206: document-type domain"): each document
207: domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and later ``ac``) is a
208: top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
209: self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
210: tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
211: the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
212: ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
213: Add a new domain by
214: creating its top-level package and importing it at the bottom of this
215: module, next to the existing ``adr``/``dec``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
216: imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
217: decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, and ``dec``
218: each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
219: registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
220: has no ``prompts`` sub-package yet.
221: """
222: 
223: from __future__ import annotations
224: 

(Showing lines 60-224 of 251. Use offset=225 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.8s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.pre-commit-config.yaml",
  "offset": 80,
  "limit": 160
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.pre-commit-config.yaml</path>
<type>file</type>
<content>
80:           -- standard formatter-hook UX: review and `git add` the regenerated
81:           file, then commit again.
82:         entry: bash -c 'uv run --frozen specmgr adr-toc && git diff --exit-code -- docs/adr/README.md'
83:         language: system
84:         pass_filenames: false
85:         files: ^docs/adr/.*\.md$
86: 
87:       - id: specmgr-schema
88:         name: specmgr schema
89:         description: >-
90:           Regenerate every registered doc-type JSON Schema (docs/{type}_schema.json)
91:           -- always runs with no `--type` (all registered types), currently `dec`,
92:           `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`. `specmgr schema` itself exits
93:           non-zero when the
94:           regenerated content differs from what was already on disk, so no separate
95:           `git diff --exit-code` is needed here, unlike the other `specmgr-*` hooks
96:           above.
97:         entry: uv run --frozen specmgr schema
98:         language: system
99:         pass_filenames: false
100:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
101: 
102:       - id: specmgr-schema-req-package
103:         name: specmgr schema (req package copy)
104:         description: >-
105:           Regenerate the packaged copy of REQ's JSON Schema
106:           (src/biz/dfch/specmgr/req/data/req_schema.json), read by the
107:           `specmgr://req/schema` MCP resource via `importlib.resources` so it
108:           works from a real, non-editable install (unlike `docs/req_schema.json`,
109:           which only resolves from an editable/source checkout). Same generator
110:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
111:           bespoke copy logic exists in `commands/schema.py`. Kept as an
112:           independent hook (not chained into `specmgr-schema`) so each artifact's
113:           drift check is its own clean gate.
114:         entry: uv run --frozen specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data
115:         language: system
116:         pass_filenames: false
117:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
118: 
119:       - id: specmgr-schema-uc-package
120:         name: specmgr schema (uc package copy)
121:         description: >-
122:           Regenerate the packaged copy of UC's JSON Schema
123:           (src/biz/dfch/specmgr/uc/data/uc_schema.json), read by the
124:           `specmgr://uc/schema` MCP resource via `importlib.resources` so it
125:           works from a real, non-editable install (unlike `docs/uc_schema.json`,
126:           which only resolves from an editable/source checkout). Same generator
127:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
128:           bespoke copy logic exists in `commands/schema.py`. Kept as an
129:           independent hook (not chained into `specmgr-schema`) so each artifact's
130:           drift check is its own clean gate.
131:         entry: uv run --frozen specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data
132:         language: system
133:         pass_filenames: false
134:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
135: 
136:       - id: specmgr-schema-tsk-package
137:         name: specmgr schema (tsk package copy)
138:         description: >-
139:           Regenerate the packaged copy of TSK's JSON Schema
140:           (src/biz/dfch/specmgr/tsk/data/tsk_schema.json), read by the
141:           `specmgr://tsk/schema` MCP resource via `importlib.resources` so it
142:           works from a real, non-editable install (unlike `docs/tsk_schema.json`,
143:           which only resolves from an editable/source checkout). Same generator
144:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
145:           bespoke copy logic exists in `commands/schema.py`. Kept as an
146:           independent hook (not chained into `specmgr-schema`) so each artifact's
147:           drift check is its own clean gate.
148:         entry: uv run --frozen specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data
149:         language: system
150:         pass_filenames: false
151:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
152: 
153:       - id: specmgr-schema-rsk-package
154:         name: specmgr schema (rsk package copy)
155:         description: >-
156:           Regenerate the packaged copy of RSK's JSON Schema
157:           (src/biz/dfch/specmgr/rsk/data/rsk_schema.json), read by the
158:           `specmgr://rsk/schema` MCP resource via `importlib.resources` so it
159:           works from a real, non-editable install (unlike `docs/rsk_schema.json`,
160:           which only resolves from an editable/source checkout). Same generator
161:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
162:           bespoke copy logic exists in `commands/schema.py`. Kept as an
163:           independent hook (not chained into `specmgr-schema`) so each artifact's
164:           drift check is its own clean gate.
165:         entry: uv run --frozen specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data
166:         language: system
167:         pass_filenames: false
168:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
169: 
170:       - id: specmgr-schema-qa-package
171:         name: specmgr schema (qa package copy)
172:         description: >-
173:           Regenerate the packaged copy of QA's JSON Schema
174:           (src/biz/dfch/specmgr/qa/data/qa_schema.json), read by the
175:           `specmgr://qa/schema` MCP resource via `importlib.resources` so it
176:           works from a real, non-editable install (unlike `docs/qa_schema.json`,
177:           which only resolves from an editable/source checkout). Same generator
178:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
179:           bespoke copy logic exists in `commands/schema.py`. Kept as an
180:           independent hook (not chained into `specmgr-schema`) so each artifact's
181:           drift check is its own clean gate.
182:         entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data
183:         language: system
184:         pass_filenames: false
185:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
186: 
187:       - id: specmgr-schema-prb-package
188:         name: specmgr schema (prb package copy)
189:         description: >-
190:           Regenerate the packaged copy of PRB's JSON Schema
191:           (src/biz/dfch/specmgr/prb/data/prb_schema.json), read by the
192:           `specmgr://prb/schema` MCP resource via `importlib.resources` so it
193:           works from a real, non-editable install (unlike `docs/prb_schema.json`,
194:           which only resolves from an editable/source checkout). Same generator
195:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
196:           bespoke copy logic exists in `commands/schema.py`. Kept as an
197:           independent hook (not chained into `specmgr-schema`) so each artifact's
198:           drift check is its own clean gate.
199:         entry: uv run --frozen specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data
200:         language: system
201:         pass_filenames: false
202:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
203:       - id: specmgr-schema-gol-package
204:         name: specmgr schema (gol package copy)
205:         description: >-
206:           Regenerate the packaged copy of GOL's JSON Schema
207:           (src/biz/dfch/specmgr/gol/data/gol_schema.json), read by the
208:           `specmgr://gol/schema` MCP resource via `importlib.resources` so it
209:           works from a real, non-editable install (unlike `docs/gol_schema.json`,
210:           which only resolves from an editable/source checkout). Same generator
211:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
212:           bespoke copy logic exists in `commands/schema.py`. Kept as an
213:           independent hook (not chained into `specmgr-schema`) so each artifact's
214:           drift check is its own clean gate.
215:         entry: uv run --frozen specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data
216:         language: system
217:         pass_filenames: false
218:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
219: 
220:       - id: specmgr-schema-dec-package
221:         name: specmgr schema (dec package copy)
222:         description: >-
223:           Regenerate the packaged copy of DEC's JSON Schema
224:           (src/biz/dfch/specmgr/dec/data/dec_schema.json), read by the
225:           `specmgr://dec/schema` MCP resource via `importlib.resources` so it
226:           works from a real, non-editable install (unlike `docs/dec_schema.json`,
227:           which only resolves from an editable/source checkout). Same generator
228:           as the `specmgr-schema` hook above, just a second `--output-dir` -- no
229:           bespoke copy logic exists in `commands/schema.py`. Kept as an
230:           independent hook (not chained into `specmgr-schema`) so each artifact's
231:           drift check is its own clean gate.
232:         entry: uv run --frozen specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data
233:         language: system
234:         pass_filenames: false
235:         files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$

(End of file - total 235 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.5s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '75,200p' .github/workflows/ci.yml"
}
```

**Output:**

```
          echo "::error::docs/adr/README.md is out of date -- run 'uv run --frozen --all-extras specmgr adr-toc' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `docs/MCP.md` is correct
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr mcp-docs
        git diff --exit-code -- docs/MCP.md || {
          echo "::error::docs/MCP.md is out of date -- run 'uv run --frozen --all-extras specmgr mcp-docs' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `docs/*_schema.json` is correct
      # `specmgr schema` without --type regenerates/checks ALL registered doc types
      # (dec, gol, prb, qa, req, rsk, tsk, uc) in a single run, and the command itself
      # exits 1 when the regenerated content differs from what was already on disk
      # (or the file didn't exist yet), so no separate `git diff --exit-code` step
      # is needed here, unlike the `docs/`/`docs/adr/README.md` checks above.
      # One step covers every `docs/<type>_schema.json` -- including `tsk` and
      # `rsk`, which never got their own dedicated step (their docs copies are
      # checked incidentally via this run).
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema || {
          echo "::error::docs/*_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/req/data/req_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://req/schema` MCP resource
      # via importlib.resources (Task 3.8) so it works from a real, non-editable install.
      # Same generator as the step above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data || {
          echo "::error::src/biz/dfch/specmgr/req/data/req_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/uc/data/uc_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://uc/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the step above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data || {
          echo "::error::src/biz/dfch/specmgr/uc/data/uc_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://tsk/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data || {
          echo "::error::src/biz/dfch/specmgr/tsk/data/tsk_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/rsk/data/rsk_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://rsk/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data || {
          echo "::error::src/biz/dfch/specmgr/rsk/data/rsk_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://qa/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data || {
          echo "::error::src/biz/dfch/specmgr/qa/data/qa_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/prb/data/prb_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://prb/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data || {
          echo "::error::src/biz/dfch/specmgr/prb/data/prb_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/gol/data/gol_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://gol/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data || {
          echo "::error::src/biz/dfch/specmgr/gol/data/gol_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `src/biz/dfch/specmgr/dec/data/dec_schema.json` is correct
      # Packaged copy of the same schema, read by the `specmgr://dec/schema` MCP resource
      # via importlib.resources so it works from a real, non-editable install.
      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data || {
          echo "::error::src/biz/dfch/specmgr/dec/data/dec_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data' and commit the result (see AGENTS.md)."
          exit 1
        }

    - name: Make sure `docs/coverage.svg` is correct
      if: matrix.python-version == '3.13'
      run: |
        uv run --frozen --all-extras --python 3.13.13 specmgr coverage-badge
        git diff --exit-code -- docs/coverage.svg || {
          echo "::error::docs/coverage.svg is out of date -- run 'uv run --frozen --all-extras specmgr coverage-badge' and commit the result (see AGENTS.md)."
          exit 1
        }

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.7s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n -i \"decision (DEC)\\|artifact type\\|Requirement (REQ)\\|Use Case (UC)\\|Goal (GOL)\\|Risk (RSK)\" README.md | head -30"
}
```

**Output:**

```
22:- Decision (DEC)
23:- Goal (GOL)
26:- Requirement (REQ)
28:- Use Case (UC)
30:- Risk (RSK)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 1.7s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && sed -n '1,40p' README.md"
}
```

**Output:**

```
# biz.dfch.SpecMgr

<!-- mcp-name: io.github.dfch/biz-dfch-specmgr -->

[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
[![Lint and Test](https://github.com/dfch/biz.dfch.SpecMgr/actions/workflows/ci.yml/badge.svg)](https://github.com/dfch/biz.dfch.SpecMgr/actions/workflows/ci.yml)
![Coverage](docs/coverage.svg)
[![TestPyPI version](https://img.shields.io/badge/dynamic/json?url=https://test.pypi.org/pypi/biz-dfch-specmgr/json&label=TestPyPI&query=$.info.version&color=orange)](https://test.pypi.org/project/biz-dfch-specmgr/)
[![PyPI version](https://img.shields.io/badge/dynamic/json?url=https://pypi.org/pypi/biz-dfch-specmgr/json&label=PyPI&query=$.info.version&color=blue)](https://pypi.org/project/biz-dfch-specmgr/)
[![PyPI downloads](https://img.shields.io/pypi/dm/biz-dfch-specmgr.svg)](https://pypistats.org/packages/biz-dfch-specmgr)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.dfch%2Fbiz--dfch--specmgr-8A2BE2.svg)](https://registry.modelcontextprotocol.io/?q=io.github.dfch/biz-dfch-specmgr)

An artifact manager for system specifications.

This project is an **MCP server** that you can use to manage different
specification artifacts.

At this time, we have these artifact:

- Architecture Decision Record (ADR)
- Decision (DEC)
- Goal (GOL)
- Problem Statement (PRB)
- Question and Answer (QA)
- Requirement (REQ)
- Task List (TSK)
- Use Case (UC)
<!-- 
- Risk (RSK)
- Acceptance Criterium (ACC)
- Feature (FTR)
-->

See [MCP Server](#mcp-server) and [docs/MCP.md](docs/MCP.md) for details.

The **MCP server** (and the management **CLI**) are optional. You install
them as "extras" (see [Installation](#installation)).

## Table of Contents

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 12.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "which gh && gh auth status 2>&1 | head -5"
}
```

**Output:**

```
/usr/bin/gh
github.com
  ✓ Logged in to github.com account dfch (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && gh issue view 31 --comments 2>&1 | tail -60"
}
```

**Output:**

```
GraphQL: Projects (classic) is being deprecated in favor of the new Projects experience, see: https://github.blog/changelog/2024-05-23-sunset-notice-projects-classic/. (repository.issue.projectCards)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && gh api repos/dfch/biz.dfch.SpecMgr/issues/31/comments --jq '.[] | {created_at, body: .body[0:400]}'"
}
```

**Output:**

```
{"body":"Phase 0 (Scaffolding) complete: commit 31c5c30 — feature plan written (`.specmgr/feat/feat-31-feature/README.md`), package skeleton for `feat/{models/v1,tools,resources,prompts}` + `tests/feat/`, and backlog Task 0.31 added to `feat-7-various-improvements` (existing-folder migration, deliberately deferred). Branch: `feat-31-feature`.","created_at":"2026-08-30T11:18:51Z"}

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 14.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && gh issue comment 31 --body \"Phase 1 (Models + parser) complete: commit d2bbf0c — \\`feat/models/v1/\\` fully implemented (\\`FeatFrontmatter\\`, \\`Feature\\`/\\`Plan\\`/\\`Progress\\` body hierarchy, \\`FeatDocument\\`, \\`parse_feat\\`, \\`FeatSummary\\`); reference fixture \\`tests/feat/models/v1/data/feat_reference.md\\` seeded from \\`example.md\\`; 99 new tests. Quality gate green (2106 tests).\"\ngh issue comment 31 --body \"Phase 2 (Tools) complete: commit a2473ab — \\`feat/tools/\\` (bespoke folder-per-document addressing, \\`find_feat_path_by_id\\` shortcut, no partial-id-match, per-id + global create locks) and all 8 tools (\\`create_feat\\`, \\`parse_feat\\`, \\`list_feat\\`, \\`get_feat\\`, \\`get_feat_example\\`, \\`get_feat_template\\`, \\`delete_feat\\` stub, \\`validate_feat\\`); \\`general/tools/update.py\\`/\\`set_status.py\\` gained \\`type=\\\"feat\\\"\\` dispatch entries. 73 new tests incl. concurrent-create NNN-collision simulation. Quality gate green (2179 tests).\"\ngh issue comment 31 --body \"Phase 3 (Resources + packaged data + schema) complete: commit c6f8b9c — \\`feat/data/\\` (example, template, create/update instructions, packaged schema copy), \\`commands/schema.py\\` gained \\`generate_feat_schema()\\`, \\`feat/resources/\\` (\\`specmgr://feat/schema\\`, \\`/example\\`, \\`/template\\`). 20 new tests. Quality gate green (2199 tests).\"\ngh issue comment 31 --body \"Phase 4 (Prompts) complete: commit b974b63 — \\`feat/prompts/\\` (\\`create_feat(topic)\\`, \\`update_feat(id, instructions=None)\\`), thin \\`string.Template\\` wrappers around the Phase-3 packaged instructions files. 29 new tests incl. end-to-end instructions-walkthrough tests. Quality gate green (2228 tests).\""
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/31#issuecomment-5470046705
https://github.com/dfch/biz.dfch.SpecMgr/issues/31#issuecomment-5470046912
https://github.com/dfch/biz.dfch.SpecMgr/issues/31#issuecomment-5470047022
https://github.com/dfch/biz.dfch.SpecMgr/issues/31#issuecomment-5470047137

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 830.1s)

Caught up on issue comments for Phases 1–4. Now let's delegate Phase 5, the final cross-cutting phase.

**Tool: task**

**Input:**

````json
{
  "description": "Implement feat-31 Phase 5: cross-cutting registration",
  "subagent_type": "phase-implementer",
  "prompt": "Implement **Phase 5: Cross-cutting registration** of the feature plan at:\n\n`/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md`\n\nRead that entire README.md first (Overview, REQ-010, ACC-008, ACC-001..ACC-009 in full, Design Notes' \"Cross-cutting wiring\" and \"Backlog housekeeping\" paragraphs). Phases 0-4 are ALL complete and committed: the full `feat` domain (models, tools, resources, packaged data, prompts) exists and is fully tested (2228 tests passing as of the last commit). This is the FINAL phase — after this, the feature should be fully done and ready to merge.\n\n### Phase 5 tasks (verbatim from the plan's Task List)\n\n- Task 5.1: `server.py` — add `feat` to the domain import line + module docstring — depends on: Task 4.3.\n- Task 5.2: `pyproject.toml` package-data entry; `.pre-commit-config.yaml` (`feat/models/v1` added to schema-hook globs + new `specmgr-schema-feat-package` hook); `.github/workflows/ci.yml` (new packaged-copy drift step) — depends on: Task 3.4.\n- Task 5.3: `AGENTS.md` — new `feat/` bullet documenting the addressing deviation explicitly (non-UUID id, folder-per-document, bespoke `_paths.py`); update the domain-enumeration sentences; decide (and note) whether root `README.md`'s artifact list gains `Feature (FEAT)` — depends on: Task 5.1.\n- Task 5.4: Regenerate `docs/MCP.md`/`docs/GENERATED.md`/`docs/api/`/`docs/feat_schema.json`; confirm all idempotent on a second run — depends on: Task 5.1, Task 5.2.\n- Task 5.5: Final verification pass — walk every ACC-001..009 with concrete evidence; full quality gate end to end; set feature status to `done` — depends on: Phase 0-4 complete, Task 5.4.\n- Task 5.6: Final commit + comment on issue #31; update this README's Progress section — depends on: Task 5.5. **Do NOT commit yourself and do NOT post the GitHub comment** — the orchestrator (me) will do both after independently verifying your work. Just do everything else (README Progress update, setting frontmatter status to `done`) and report back full evidence.\n\n### Task 5.1 — `server.py`\n\n- Add `feat` to the domain import line at the bottom of the file: `from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401` (alphabetical order, `feat` goes between `dec` and `general`).\n- Add a `specmgr://feat/schema`/`specmgr://feat/example`/`specmgr://feat/template` block to the module docstring's \"Resources\" section, mirroring the `dec` block's exact format (see the existing `specmgr://dec/schema`/`/example`/`/template` lines) — insert it in the same relative position as `feat` sits in the domain-enumeration elsewhere (check where `dec` sits in that list and place `feat` consistently, likely right after the `dec` block or wherever alphabetical/chronological order is used elsewhere in the file — check the existing ordering convention first, don't just guess).\n- Add a \"FEAT has no `specmgr://feat/{id}` resource either, ... no `specmgr://feat/list` resource either\" sentence to the \"REQ has no...\" paragraph, mirroring the `DEC` sentence's exact wording/structure.\n- Add a \"Feature tools (`feat/tools/`): ...\" paragraph to the \"Tools\" section, mirroring the `Decision tools (dec/tools/)` paragraph's exact structure, but note `feat`'s own divergences (no `raw=True`... wait, actually check: does `get_feat` have `raw=True`? Read `feat/tools/get_feat.py` to confirm before writing this paragraph — don't assume it matches `dec` exactly). Update the `general.tools.update`/`set_status` paragraphs' domain-list enumerations (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec` → add `feat`; the eight/nine-whole-body-domain counts throughout need bumping too, same as `general/tools/update.py`'s own docstring update in Phase 2 — check that file's current wording for the exact counting convention already established there).\n- Add a \"Feature prompts (`feat/prompts/`): `create_feat`, `update_feat` -- ...\" paragraph to the \"Prompts\" section, mirroring the `Decision prompts (dec/prompts/)` paragraph's exact structure.\n- Update the \"Modules are grouped domain-first...\" paragraph's domain-enumeration sentence (`adr`, `uc`, `req`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, and later `ac` → insert `feat` in the list; also check if it should still say \"and later `ac`\" or needs adjusting) and the \"Add a new domain by creating...\" sentence listing existing domain imports (`adr`/`dec`/`general`/`gol`/`prb`/`qa`/`req`/`rsk`/`tsk`/`uc` → insert `feat` alphabetically) and the final \"`req`, `tsk`, `qa`, `prb`, `gol`, `rsk`, and `dec` each register `tools`, `resources`, and `prompts`; ... `uc` registers `tools` and `resources` only\" sentence (add `feat` to the \"each register all three\" list).\n\n### Task 5.2 — `pyproject.toml` / `.pre-commit-config.yaml` / `.github/workflows/ci.yml`\n\n- `pyproject.toml`: add a `\"biz.dfch.specmgr.feat\" = [\"data/*.md\", \"data/*.json\"]` entry under `[tool.setuptools.package-data]`, in the same alphabetical position as the other domain entries (check exact ordering — likely alphabetical, `feat` goes between `dec` and `gol`).\n- `.pre-commit-config.yaml`: this file has ONE combined regex `files:` glob repeated verbatim across the `specmgr-schema` hook and every `specmgr-schema-<domain>-package` hook — e.g. `^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\\.py$`. Add `feat/models/v1` to that alternation (in the same alphabetical position, between `dec/models/v1` and `gol/models/v1`) in EVERY occurrence of this glob in the file (there are ~9 occurrences — use a global find/replace, but verify the count matches before/after). Then add a brand-new `specmgr-schema-feat-package` hook entry, mirroring `specmgr-schema-dec-package`'s exact structure (id/name/description/entry/language/pass_filenames/files), with `entry: uv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data` — place it in the same relative position/style as the existing per-domain hooks (check whether they're in any particular order, e.g. alphabetical or insertion order, and match it).\n- `.github/workflows/ci.yml`: add a new `\"Make sure \\`src/biz/dfch/specmgr/feat/data/feat_schema.json\\` is correct\"` step, mirroring the existing `dec` step's exact structure (same `if: matrix.python-version == '3.13'` guard, same error-message format), placed among the other per-domain schema-package steps.\n\n### Task 5.3 — `AGENTS.md`\n\n- Add a new `**\\`feat/\\`**` bullet to the per-domain enumeration list (in `AGENTS.md`'s \"Status: domain packages implemented\" section), in the same style/depth as the existing `**\\`dec/\\`**` bullet, but describing `feat`'s own genuinely-divergent shape: bespoke folder-per-document addressing (`feat/tools/_paths.py`, NOT built on the shared `general/tools/_doc_paths.py`), non-UUID `id` (a chosen `feat-NNN-slug`, the containing folder's own name), `SPECMGR_FEAT_DIR` env var, all 8 tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`, `get_feat_example`, `get_feat_template`, `delete_feat` stub, `validate_feat`), the generic `update`/`set_status` dispatch (`type=\"feat\"`, no `update_feat`/`set_status_feat` of its own), resources (`specmgr://feat/schema`/`/example`/`/template`, no `/{id}`, no `/list`), and prompts (`create_feat`/`update_feat`). Its schema lives at `feat/models/v1/`, inside the domain package (not top-level `models/`).\n- Update `AGENTS.md`'s other domain-enumeration sentences that list all current domains (check the \"Still genuinely missing\" section, the \"MCP server (server.py)\" section's own domain-import-line description, and any other place `AGENTS.md` enumerates the full domain list) to include `feat`.\n- **Decision on root `README.md`'s artifact list**: I've already checked — `README.md` currently has a commented-out placeholder block reading:\n  ```\n  <!-- \n  - Risk (RSK)\n  - Acceptance Criterium (ACC)\n  - Feature (FTR)\n  -->\n  ```\n  (note: that placeholder uses the abbreviation \"FTR\", but the actual implemented abbreviation everywhere in code/docs is \"FEAT\", not \"FTR\"). Since `feat` is now a fully schema-backed, MCP-tool-addressable artifact type exactly like every other one in the active list (not a purely internal/meta concept anymore), **add \"Feature (FEAT)\" to the active bulleted list** (in alphabetical-by-full-name order — it goes between \"Decision (DEC)\" and \"Goal (GOL)\"), and **remove the \"Feature (FTR)\" line from the commented-out placeholder block** (leaving `Risk (RSK)`/`Acceptance Criterium (ACC)` there, since RSK is already actually implemented too — check if RSK should also move to the active list while you're at it, since RSK long since shipped as a real domain; if RSK is already implemented per `AGENTS.md`, move it to the active list too as a drive-by fix, otherwise leave it commented). Document this decision in the plan README's Decisions Made log with your reasoning.\n\n### Task 5.4 — Regenerate everything\n\n```\nuv run --frozen specmgr docs\nuv run --frozen specmgr mcp-docs\nuv run --frozen specmgr schema\nuv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data\n```\n\nRun each command TWICE in a row and confirm the second run produces no `git diff` (idempotent) before moving on. Report the diffs from each command's first run.\n\n### Task 5.5 — Final verification pass (walk every ACC with concrete evidence)\n\nFor each of ACC-001 through ACC-009 (read their exact text in the README's Acceptance Criteria section), find and report concrete evidence it is satisfied — cite the specific test(s), file(s), or command output that proves it, not just \"yes this is done\". Then run the full quality gate:\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\nuv run --frozen specmgr unused-code\n```\n\nThen set this feature's own frontmatter `status` from `in-progress` to `done` in `.specmgr/feat/feat-31-feature/README.md`'s YAML frontmatter block (hand-edit it directly — this is a `.specmgr` planning document, not a `feat`-schema document itself, so there's no `set_status` MCP tool call needed here, just edit the YAML).\n\n### Also required\n\n- Update the plan README's Progress section (Current Status, a new dated Recent Updates entry declaring the feature complete, Decisions Made for the README.md artifact-list judgment call and any others) — edit `/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md` directly, and flip Task 5.1–5.6's checkboxes/status fields in the Task List to reflect completion.\n- Do NOT commit. Do NOT post to GitHub issue #31. Stop after the quality gate is green and the plan README is updated, and report back a full summary including: files created/modified, key design/judgment calls (especially the README.md artifact-list decision and the RSK drive-by-fix decision if you made one), the full quality gate command output/evidence, and your ACC-001..009 evidence walkthrough.\n- If you hit anything genuinely blocking, STOP immediately and report back rather than improvising a workaround.\n"
}
````

**Output:**

```
<task id="ses_fac61f69effec22t6ceGhZx8Tz" state="completed">
<task_result>
All green: 2228 tests pass, ruff/vulture/unused-code clean. Phase 5 is complete.

## Summary

**Tasks completed (5.1–5.6):**

- **Task 5.1** — `src/biz/dfch/specmgr/server.py`: added `feat` to the domain import line (alphabetical order) and updated the module docstring: new `specmgr://feat/schema`/`/example`/`/template` Resources block, a "FEAT has no `/{id}`/no `/list`" sentence, a new "Feature tools" paragraph (verified `get_feat` has `raw=True` by reading `feat/tools/get_feat.py` first), bumped `update`/`set_status` domain counts (eight→nine, nine→ten), a new "Feature prompts" paragraph, and `feat` inserted into all domain-enumeration sentences.
- **Task 5.2** — `pyproject.toml` (new `biz.dfch.specmgr.feat` package-data entry between `dec`/`gol`); `.pre-commit-config.yaml` (`feat/models/v1` added to all 9 pre-existing occurrences of the shared schema-hook glob, verified 9→9, plus a new `specmgr-schema-feat-package` hook mirroring `dec`'s exactly); `.github/workflows/ci.yml` (new `feat_schema.json` drift step mirroring the `dec` step).
- **Task 5.3** — `AGENTS.md`: new `feat/` bullet (addressing deviation, `SPECMGR_FEAT_DIR`, 8 tools, generic dispatch, resources, prompts, `FeatSummary.path`), bumped domain counts, updated "Still genuinely missing"/"MCP server" enumerations. `README.md`: added `Feature (FEAT)` to the active list (alphabetical, between DEC/GOL); removed `Feature (FTR)` from the commented placeholder; **drive-by fix**: moved `Risk (RSK)` into the active list too since it's already fully implemented, leaving only `Acceptance Criterium (ACC)` commented out.
- **Task 5.4** — Ran `specmgr docs`, `mcp-docs`, `schema`, `schema --type feat ...` each twice; all idempotent. Only `docs/api/biz.dfch.specmgr.server.md` changed (from the docstring edits); `docs/MCP.md` had zero diff (FEAT was already fully registered).
- **Task 5.5** — Walked ACC-001..009 with concrete test/file/command evidence (see plan README's new Recent Updates entry for the full per-ACC breakdown). Full quality gate: `ruff format --check` (1286 files formatted), `ruff check` (pass), `vulture` (clean), `unittest` (2228 tests, OK), `specmgr unused-code` (clean). Frontmatter `status` → `done`.
- **Task 5.6** — Updated plan README's Progress section (Current Status, new dated Recent Updates entry, new Decisions Made entry for the README artifact-list/RSK drive-by judgment call), flipped all ACC/Task checkboxes. **No commit made, no issue comment posted**, per instructions.

**Files modified:** `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `AGENTS.md`, `README.md`, `docs/api/biz.dfch.specmgr.server.md`, `pyproject.toml`, `src/biz/dfch/specmgr/server.py`, `.specmgr/feat/feat-31-feature/README.md`.

**Quality gate:** all commands green as listed above — no failures encountered, nothing left red.

**For your independent verification:** `git status --short` shows exactly these 8 files changed, no stray files; all edits are additive/cross-cutting registration only — no `src/biz/dfch/specmgr/feat/` or `tests/feat/` code was touched this phase.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.6s)

Let's verify independently.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short"
}
```

**Output:**

```
 M .github/workflows/ci.yml
 M .pre-commit-config.yaml
 M .specmgr/feat/feat-31-feature/README.md
 M AGENTS.md
 M README.md
 M docs/api/biz.dfch.specmgr.server.md
 M pyproject.toml
 M src/biz/dfch/specmgr/server.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.0s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff README.md"
}
```

**Output:**

```
diff --git a/README.md b/README.md
index 6f03f59..b8e4d31 100644
--- a/README.md
+++ b/README.md
@@ -20,16 +20,16 @@ At this time, we have these artifact:
 
 - Architecture Decision Record (ADR)
 - Decision (DEC)
+- Feature (FEAT)
 - Goal (GOL)
 - Problem Statement (PRB)
 - Question and Answer (QA)
 - Requirement (REQ)
+- Risk (RSK)
 - Task List (TSK)
 - Use Case (UC)
 <!-- 
-- Risk (RSK)
 - Acceptance Criterium (ACC)
-- Feature (FTR)
 -->
 
 See [MCP Server](#mcp-server) and [docs/MCP.md](docs/MCP.md) for details.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.0s)

This is exactly right, both the FEAT addition and the RSK drive-by fix. Let's check the pre-commit glob change count and server.py diff.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -c \"feat/models/v1\" .pre-commit-config.yaml && grep -c \"specmgr-schema-feat-package\" .pre-commit-config.yaml"
}
```

**Output:**

```
10
1

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.6s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .pre-commit-config.yaml | head -80"
}
```

**Output:**

```
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index cf9605e..1ea56d3 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -89,7 +89,7 @@ repos:
         description: >-
           Regenerate every registered doc-type JSON Schema (docs/{type}_schema.json)
           -- always runs with no `--type` (all registered types), currently `dec`,
-          `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`. `specmgr schema` itself exits
+          `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`. `specmgr schema` itself exits
           non-zero when the
           regenerated content differs from what was already on disk, so no separate
           `git diff --exit-code` is needed here, unlike the other `specmgr-*` hooks
@@ -97,7 +97,7 @@ repos:
         entry: uv run --frozen specmgr schema
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-req-package
         name: specmgr schema (req package copy)
@@ -114,7 +114,7 @@ repos:
         entry: uv run --frozen specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-uc-package
         name: specmgr schema (uc package copy)
@@ -131,7 +131,7 @@ repos:
         entry: uv run --frozen specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-tsk-package
         name: specmgr schema (tsk package copy)
@@ -148,7 +148,7 @@ repos:
         entry: uv run --frozen specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-rsk-package
         name: specmgr schema (rsk package copy)
@@ -165,7 +165,7 @@ repos:
         entry: uv run --frozen specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-qa-package
         name: specmgr schema (qa package copy)
@@ -182,7 +182,7 @@ repos:
         entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-prb-package
         name: specmgr schema (prb package copy)
@@ -199,7 +199,7 @@ repos:
         entry: uv run --frozen specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
       - id: specmgr-schema-gol-package
         name: specmgr schema (gol package copy)
         description: >-
@@ -215,7 +215,7 @@ repos:
         entry: uv run --frozen specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data
         language: system
         pass_filenames: false

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.5s)

All 9 pre-existing occurrences updated + 1 new hook = 10 total mentions. Let's check the new hook entry and CI workflow addition.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .pre-commit-config.yaml | tail -40"
}
```

**Output:**

```
         entry: uv run --frozen specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
       - id: specmgr-schema-gol-package
         name: specmgr schema (gol package copy)
         description: >-
@@ -215,7 +215,7 @@ repos:
         entry: uv run --frozen specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
 
       - id: specmgr-schema-dec-package
         name: specmgr schema (dec package copy)
@@ -232,4 +232,21 @@ repos:
         entry: uv run --frozen specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+
+      - id: specmgr-schema-feat-package
+        name: specmgr schema (feat package copy)
+        description: >-
+          Regenerate the packaged copy of FEAT's JSON Schema
+          (src/biz/dfch/specmgr/feat/data/feat_schema.json), read by the
+          `specmgr://feat/schema` MCP resource via `importlib.resources` so it
+          works from a real, non-editable install (unlike `docs/feat_schema.json`,
+          which only resolves from an editable/source checkout). Same generator
+          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
+          bespoke copy logic exists in `commands/schema.py`. Kept as an
+          independent hook (not chained into `specmgr-schema`) so each artifact's
+          drift check is its own clean gate.
+        entry: uv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data
+        language: system
+        pass_filenames: false
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

Correctly appended and formatted. Now let's check ci.yml and pyproject.toml.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .github/workflows/ci.yml pyproject.toml"
}
```

**Output:**

```
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 4fefdc9..32da708 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -87,7 +87,7 @@ jobs:
 
     - name: Make sure `docs/*_schema.json` is correct
       # `specmgr schema` without --type regenerates/checks ALL registered doc types
-      # (dec, gol, prb, qa, req, rsk, tsk, uc) in a single run, and the command itself
+      # (dec, feat, gol, prb, qa, req, rsk, tsk, uc) in a single run, and the command itself
       # exits 1 when the regenerated content differs from what was already on disk
       # (or the file didn't exist yet), so no separate `git diff --exit-code` step
       # is needed here, unlike the `docs/`/`docs/adr/README.md` checks above.
@@ -189,6 +189,17 @@ jobs:
           exit 1
         }
 
+    - name: Make sure `src/biz/dfch/specmgr/feat/data/feat_schema.json` is correct
+      # Packaged copy of the same schema, read by the `specmgr://feat/schema` MCP resource
+      # via importlib.resources so it works from a real, non-editable install.
+      # Same generator as the `docs/*_schema.json` steps above, just a second --output-dir.
+      if: matrix.python-version == '3.13'
+      run: |
+        uv run --frozen --all-extras --python 3.13.13 specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data || {
+          echo "::error::src/biz/dfch/specmgr/feat/data/feat_schema.json is out of date -- run 'uv run --frozen --all-extras specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data' and commit the result (see AGENTS.md)."
+          exit 1
+        }
+
     - name: Make sure `docs/coverage.svg` is correct
       if: matrix.python-version == '3.13'
       run: |
diff --git a/pyproject.toml b/pyproject.toml
index 148d1da..7c32628 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -124,6 +124,10 @@ namespaces = true
     "data/*.md",
     "data/*.json"
 ]
+"biz.dfch.specmgr.feat" = [
+    "data/*.md",
+    "data/*.json"
+]
 "biz.dfch.specmgr.gol" = [
     "data/*.md",
     "data/*.json"

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

Correct. Now let's check `server.py` and `AGENTS.md` diffs.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff src/biz/dfch/specmgr/server.py | head -150"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/server.py b/src/biz/dfch/specmgr/server.py
index fded6eb..dadf610 100644
--- a/src/biz/dfch/specmgr/server.py
+++ b/src/biz/dfch/specmgr/server.py
@@ -82,6 +82,12 @@ specmgr://dec/schema -- The generated DEC JSON Schema, read from a packaged data
 specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
 specmgr://dec/template -- A decision template (every field present, placeholder text)
                           as raw markdown.
+specmgr://feat/schema -- The generated FEAT JSON Schema, read from a packaged data copy
+                        (kept in sync with ``docs/feat_schema.json``) so it works from a
+                        real, non-editable install.
+specmgr://feat/example -- A complete, valid sample feature document as raw markdown.
+specmgr://feat/template -- A feature template (every field present, placeholder text)
+                          as raw markdown.
 specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                         characteristics (and sub-characteristics), each with a description.
 
@@ -106,7 +112,11 @@ id-based reads go through the ``get_gol`` tool only, and there is also no
  ``specmgr://dec/{id}`` resource either, for the same reason -- id-based reads go
  through the ``get_dec`` tool only, and there is also no
  ``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged tool from
- day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
+ day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). FEAT has no
+ ``specmgr://feat/{id}`` resource either, for the same reason -- id-based
+ reads go through the ``get_feat`` tool only, and there is also no
+ ``specmgr://feat/list`` resource either -- ``list_feat`` ships as a paged
+ tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
 
 Tools
 -----
@@ -151,15 +161,26 @@ frontmatter-stripped body text verbatim instead of the parsed document), ``list_
   ``get_dec_example``,
   ``get_dec_template``, ``create_dec``, ``delete_dec``
   (stub, not yet implemented), ``validate_dec``.
+  Feature tools (``feat/tools/``): ``parse_feat``, ``get_feat`` (``raw=True`` returns the
+frontmatter-stripped body text verbatim instead of the parsed document), ``list_feat``,
+  ``get_feat_example``,
+  ``get_feat_template``, ``create_feat``, ``delete_feat``
+  (stub, not yet implemented), ``validate_feat``. Unlike every other domain here, ``feat``
+  uses bespoke, folder-per-document addressing (``feat/tools/_paths.py``, not the shared
+  ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
+  its own -- it dispatches through the generic ``update``/``set_status`` tools below from
+  day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), same as every other domain.
   General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
 preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
-existing document's content across the eight whole-body domains (``type`` is one of
-``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``; optional 1-based inclusive
+existing document's content across the nine whole-body domains (``type`` is one of
+``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``; optional 1-based
+inclusive
 ``begin``/``end`` body-line range with the ``N+1`` end-of-body sentinel; the spliced
 result is validated as a whole document before anything is written); ``set_status`` --
-replace an existing document's status across all nine domains (``type`` is one of
-``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``adr``), also bumping
-``updated`` (the eight whole-body domains) and leaving the body untouched;
+replace an existing document's status across all ten domains (``type`` is one of
+``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``), also
+bumping
+``updated`` (the nine whole-body domains) and leaving the body untouched;
 ``superseded_by`` is ``adr``-only (it composes the status as
 ``"superseded by {superseded_by}"``);
 ``webfetch`` -- fetch a URL over HTTP GET with a
@@ -196,6 +217,10 @@ Decision prompts (``dec/prompts/``): ``create_dec``, ``update_dec`` --
 instructional text guiding an LLM through a ``TodoWrite`` +
 ``question``-tool-driven interview flow; ``create_dec`` first checks
 ``list_dec`` for a near-duplicate decision.
+Feature prompts (``feat/prompts/``): ``create_feat``, ``update_feat`` --
+narrated instruction flows guiding an LLM through the FEAT tool sequence
+above; ``create_feat`` first checks ``list_feat`` for a near-duplicate
+feature.
 General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
 older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
 ``README.md`` into an optional sibling ``history.md``, per ADR
@@ -204,7 +229,8 @@ e369ee2e-3353-4f92-991c-6367d76d832e.
 Modules are grouped domain-first
 (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
 document-type domain"): each document
-domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and later ``ac``) is a
+domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``,
+and later ``ac``) is a
 top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
 self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
 tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
@@ -212,9 +238,10 @@ the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-lev
 ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
 Add a new domain by
 creating its top-level package and importing it at the bottom of this
-module, next to the existing ``adr``/``dec``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
+module, next to the existing
+``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
 imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
-decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, and ``dec``
+decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and ``feat``
 each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
 registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
 has no ``prompts`` sub-package yet.
@@ -248,4 +275,4 @@ mcp = MCPServer(
 # decorators to actually run.
 # ---------------------------------------------------------------------------
 
-from . import adr, dec, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401
+from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

This is comprehensive and correct. Let's check `AGENTS.md` diff.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff AGENTS.md"
}
```

**Output:**

```
diff --git a/AGENTS.md b/AGENTS.md
index 07d3154..60bce34 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -191,19 +191,58 @@ type or cross-cutting:
   `models/md` parser with the GOL/RSK/QA simple surface — no
   fine-grained mutation tools, no renderer: writes persist the
   caller's raw validated body byte-for-byte.
+- **`feat/`** (Feature) — formalizes the ad hoc `.specmgr/feat/<id>/
+  README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e) into a
+  real, schema-backed domain, and is the one domain in this codebase whose
+  own addressing genuinely deviates from every other domain's precedent
+  (ADR 8cf940c5-3100-485c-a12d-14b59b631712): `id` is a chosen
+  `feat-NNN-slug` — the containing folder's own name, not a
+  server-generated UUID — and documents live one-per-folder as
+  `<base>/<id>/README.md` (a fixed filename), not flat files directly
+  under the base directory. This bespoke, folder-per-document addressing
+  is hand-rolled in `feat/tools/_paths.py` (ADR-style, like `adr/tools/
+  _paths.py`), **not** built on the shared flat-file
+  `general/tools/_doc_paths.py` every other whole-body domain uses;
+  `SPECMGR_FEAT_DIR` overrides the base directory (mandatory-in-spirit
+  test-isolation env var, same as every other domain's own equivalent).
+  All 8 tools (`create_feat`, `parse_feat`, `list_feat`, `get_feat`,
+  `get_feat_example`, `get_feat_template`, `delete_feat` stub,
+  `validate_feat`); whole-body and line-range updates go through the
+  generic `update` tool in `general/tools/` (`type="feat"`), status
+  changes through the generic `set_status` tool (`type="feat"`) — no
+  `update_feat`/`set_status_feat` of its own — and the `get_feat` tool
+  takes `raw: bool = False` — `raw=True` returns the frontmatter-stripped
+  body text as-is (the text `update`'s `begin`/`end` index into);
+  `feat/resources/` (`specmgr://feat/schema`, `specmgr://feat/example`,
+  `specmgr://feat/template`; no `specmgr://feat/{id}` — id-based reads
+  are `get_feat`-only, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614; no
+  `specmgr://feat/list` — `list_feat` ships as a paged tool from day
+  one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13); `feat/prompts/`
+  (`create_feat`/`update_feat`, narrated instruction flows; `create_feat`
+  first checks `list_feat` for a near-duplicate feature). Its schema
+  lives at `feat/models/v1/`, inside the domain package, not top-level
+  `models/`. `FeatSummary` adds one extra field beyond every other
+  domain's summary, `path: str` (the real filesystem path to the
+  document's `README.md`) — a deliberate divergence, since direct
+  hand/agent editing of `.specmgr/feat/<id>/README.md` remains the
+  domain's own normal, sanctioned workflow even after its MCP tools
+  exist, unlike every other domain's summary, whose `ref` field is
+  deliberately *not* a path. See
+  `.specmgr/feat/feat-31-feature/README.md` for the full design.
   - **`general/`** — cross-cutting, non-domain-specific package:
     `general/tools/` (`mdformat`, formats a markdown file in place while
     preserving YAML frontmatter blocks; `update`, the generic whole-body
-    *and* line-range replace for the eight whole-body domains — `type` is
-    one of req/uc/tsk/qa/prb/gol/rsk/dec, optional 1-based inclusive body-line
+    *and* line-range replace for the nine whole-body domains — `type` is
+    one of req/uc/tsk/qa/prb/gol/rsk/dec/feat, optional 1-based inclusive
+    body-line
     `begin`/`end` with the `N+1` end-of-body sentinel, splice-then-
-    validate-whole; `set_status`, the generic status change for all nine
+    validate-whole; `set_status`, the generic status change for all ten
     domains incl. adr — `superseded_by` is ADR-only, composing
     `"superseded by X"`), `general/resources/`
    (`specmgr://version`, `specmgr://iso25010` — the ISO/IEC 25010:2023
    quality model), and `general/prompts/` (`compact_history` — rotates
     older `Recent Updates` entries out of any feature folder's `README.md`
-    into a sibling `history.md`). The eight `get_<d>` tools additionally
+    into a sibling `history.md`). The nine `get_<d>` tools additionally
     take a `raw: bool = False` parameter — `raw=True` returns the
     frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
     index into).
@@ -230,13 +269,14 @@ mirror of that same registration and must never be hand-edited.
 Still genuinely missing / not yet done (don't assume otherwise):
 - No `validate_adr` (or `validate_req`/`validate_uc`/`validate_tsk`/
   `validate_qa`/`validate_prb`/`validate_gol`/`validate_rsk`/
-  `validate_dec`) tool runs
+  `validate_dec`/`validate_feat`) tool runs
   over the repo's
   own documents yet via pre-commit or CI. (ADR
   9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
   locally via pre-commit hook, not just CI")
 - `delete_req`/`delete_uc`/`delete_tsk`/`delete_qa`/`delete_prb`/
-  `delete_gol`/`delete_rsk`/`delete_dec` are stubs, not yet implemented.
+  `delete_gol`/`delete_rsk`/`delete_dec`/`delete_feat` are stubs, not yet
+  implemented.
 - No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
   docstring already reserving a spot for it ("... and later `ac`") — the
   convention for adding it (or any future domain) is fixed by ADR
@@ -244,7 +284,7 @@ Still genuinely missing / not yet done (don't assume otherwise):
   two generic tools in `general/tools/` (`update`'s `type`,
   `set_status`'s `type`) plus a `raw` parameter on the new `get_<d>` tool
   — not new `update_<d>`/`set_status_<d>` tools.
-- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec` each register `tools`,
+- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`feat` each register `tools`,
   `resources`, and `prompts`; `uc` registers `tools` and `resources`
   only — it has no `prompts` sub-package yet.
 
@@ -384,9 +424,9 @@ consumer of the base library.
 ## MCP server (`server.py`)
 
 - Builds the `MCPServer` instance (`mcp` object) and a no-op `_lifespan`,
-  then imports every domain package (`adr`, `dec`, `general`, `gol`,
-  `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`) as its last line purely for the
-  side effect of
+  then imports every domain package (`adr`, `dec`, `feat`, `general`,
+  `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`) as its last line purely for
+  the side effect of
   running their `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` decorators.
   When adding a new domain, add its import to that same last line —
   forgetting it means the new tools/resources/prompts silently never

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.3s)

Excellent, thorough and matches the codebase's existing style precisely. Now let's run the full quality gate independently to verify.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo === && uv run --frozen ruff check 2>&1 | tail -5"
}
```

**Output:**

```
1286 files already formatted
===
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -20; echo EXIT:$?"
}
```

**Output:**

```
EXIT:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 81.1s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(Ran|OK|FAILED|ERROR)\""
}
```

**Output:**

```
Range mode must raise the domain's own not-found error for an unknown id. ... ok
Ran 2228 tests in 76.277s
OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.9s)

All green. Now let's independently confirm the docs regeneration is idempotent (no drift) and check `docs/api/biz.dfch.specmgr.server.md` update.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen specmgr docs 2>&1 | tail -10 && git status --short docs/"
}
```

**Output:**

```
✓ Wrote 363 module file(s) to /home/user/src/biz.dfch.SpecMgr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/GENERATED.md
 M docs/api/biz.dfch.specmgr.server.md

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.0s)

No new diff beyond what's already staged/modified — idempotent as claimed. Let's check `mcp-docs` and `schema` too.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen specmgr mcp-docs 2>&1 | tail -5 && git status --short docs/MCP.md\nuv run --frozen specmgr schema 2>&1 | tail -10 && git status --short docs/*.json\nuv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data 2>&1 | tail -5 && git status --short src/biz/dfch/specmgr/feat/data/"
}
```

**Output:**

```
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/MCP.md
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/dec_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/feat_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/gol_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/prb_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/qa_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/req_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/rsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/tsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr/docs/uc_schema.json (unchanged)
✓ Wrote src/biz/dfch/specmgr/feat/data/feat_schema.json (unchanged)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

Everything is idempotent, no drift. Let's confirm the README's frontmatter status is `done` and view the final Progress section.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && head -10 .specmgr/feat/feat-31-feature/README.md"
}
```

**Output:**

```
---
created: 2026-08-30
id: feat-31-feature
status: done
updated: 2026-08-30
version: 1.11.0
---

# Feature: Formalize the Feature artifact type ("feat")


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"ACC-00\" .specmgr/feat/feat-31-feature/README.md | head -20"
}
```

**Output:**

```
132:- [x] ACC-001: Verifies REQ-001/002 — schema documented
145:- [x] ACC-002: Verifies REQ-003/004 — a document whose frontmatter `id`
151:- [x] ACC-003: Verifies REQ-005 — every listed tool is implemented,
155:- [x] ACC-004: Verifies REQ-006 — `update(type="feat", ...)` and
159:- [x] ACC-005: Verifies REQ-007 — every listed resource is implemented and
161:- [x] ACC-006: Verifies REQ-008 — both prompts narrate the full
165:- [x] ACC-007: Verifies REQ-009 — `specmgr schema --type feat` and the
168:- [x] ACC-008: Verifies REQ-010 — `specmgr docs`/`specmgr mcp-docs`/
173:- [x] ACC-009: Verifies REQ-011 — full unittest suite green; ruff
625:  field combinations), `test_parser.py` (ACC-001 matrix + round-trip) —
670:  tests + `test_integration.py` (ACC-003/ACC-004, incl. concurrent-create
703:- [x] Task 3.6: Tests `tests/feat/resources/` (ACC-005/ACC-007) — depends
725:- [x] Task 4.2: Tests `tests/feat/prompts/` (ACC-006) — depends on: Task
728:  "walk the instructions end to end" test per prompt (ACC-006) against a
801:- [x] Task 5.5: Final verification pass — walk every ACC-001..009 with
964:end" test per prompt (ACC-006) that drives the real
974:depth introduced for `feat` specifically, per ACC-006's explicit
1001:registered before this phase. Every ACC-001..009 was walked with concrete
1109:- **Final verification (Task 5.5)** — ACC-001..009 walked with concrete
1111:  - ACC-001: `tests/feat/models/v1/test_parser.py` exercises the full

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 151.2s)

All acceptance criteria checked off. Everything is verified. Let's commit Phase 5.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"feat(feat-31): cross-cutting registration for Feature (feat) domain (Phase 5)\n\n- server.py: add feat to the domain import line + module docstring\n  (resources, tools, prompts sections)\n- pyproject.toml: package-data entry for biz.dfch.specmgr.feat\n- .pre-commit-config.yaml: feat/models/v1 added to schema-hook globs,\n  new specmgr-schema-feat-package hook\n- .github/workflows/ci.yml: new feat_schema.json packaged-copy drift step\n- AGENTS.md: new feat/ bullet documenting the addressing deviation,\n  updated domain-enumeration sentences\n- README.md: add Feature (FEAT) to the artifact list; move Risk (RSK)\n  out of the commented placeholder (already implemented); drop the\n  stale Feature (FTR) placeholder line\n- Regenerate docs/api/biz.dfch.specmgr.server.md\n\nFeature complete: all 5 phases (models, tools, resources, prompts,\ncross-cutting registration) implemented and tested (2228 tests green).\nFeature status set to done.\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -7"
}
```

**Output:**

```
ae53f51 feat(feat-31): cross-cutting registration for Feature (feat) domain (Phase 5)
b974b63 feat(feat-31): implement Feature (feat) prompts (Phase 4)
c6f8b9c feat(feat-31): implement Feature (feat) resources, packaged data, schema (Phase 3)
a2473ab feat(feat-31): implement Feature (feat) tools (Phase 2)
d2bbf0c feat(feat-31): implement Feature (feat) models and parser (Phase 1)
cc9c254 docs(feat-31): update design, add example, add session transcript
8647567 docs(feat-31): add session transcript

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.1s)

Phase 5 committed (`ae53f51`). Let's post the final GitHub issue comment and update the todo list.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && gh issue comment 31 --body \"Phase 5 (Cross-cutting registration) complete: commit ae53f51 — \\`server.py\\` domain import + docstring, \\`pyproject.toml\\` package-data entry, \\`.pre-commit-config.yaml\\`/\\`.github/workflows/ci.yml\\` schema-drift wiring, \\`AGENTS.md\\` new \\`feat/\\` bullet, \\`README.md\\` gains \\`Feature (FEAT)\\` (and \\`Risk (RSK)\\` moved out of the commented placeholder as a drive-by fix, since it was already implemented). All 5 phases now complete — full quality gate green (2228 tests, ruff/vulture/unused-code clean), docs regeneration confirmed idempotent, every ACC-001..009 verified with concrete evidence. Feature status set to \\`done\\`. Ready for review/merge.\""
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/31#issuecomment-5470144350

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Scaffolding (already complete, verify only)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models + parser (feat/models/v1/)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources + packaged data + schema",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Prompts",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 5: Cross-cutting registration + final verification",
      "status": "completed",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Scaffolding (already complete, verify only)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models + parser (feat/models/v1/)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (feat/tools/) — bespoke addressing",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources + packaged data + schema",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Prompts",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 5: Cross-cutting registration + final verification",
    "status": "completed",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 13.6s)

## Summary

Feature **feat-31-feature** ("Formalize the Feature artifact type") is now fully implemented, verified, and committed on branch `feat-31-feature`. All 5 phases (plus the already-complete Phase 0) were driven to completion via dedicated `phase-implementer` subagents, with independent verification of each phase's quality gate, git diff, and acceptance criteria before committing:

| Phase | Commit | Highlights |
|---|---|---|
| 0 (pre-existing) | `31c5c30`/`164182e` | Package skeleton, backlog housekeeping |
| 1 — Models | `d2bbf0c` | `feat/models/v1/` schema/parser, 99 new tests |
| 2 — Tools | `a2473ab` | Bespoke folder-per-document addressing, 8 tools, generic `update`/`set_status` dispatch, 73 new tests |
| 3 — Resources | `c6f8b9c` | Packaged data, `specmgr://feat/*` resources, JSON Schema generator, 20 new tests |
| 4 — Prompts | `b974b63` | `create_feat`/`update_feat` narrated prompts, 29 new tests |
| 5 — Cross-cutting | `ae53f51` | `server.py`, `pyproject.toml`, pre-commit/CI wiring, `AGENTS.md`, `README.md` |

**Final state:**

- 2228 tests passing, `ruff format`/`ruff check`/`vulture`/`specmgr unused-code` all clean
- All ACC-001–009 verified with concrete evidence
- Docs (`docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`, `docs/feat_schema.json`) regenerated and confirmed idempotent
- Feature plan's own frontmatter `status` set to `done`
- GitHub issue #31 has a comment recording each phase's commit hash and evidence, including catch-up comments for phases where the subagent correctly deferred commenting to me

**Notable judgment calls made along the way** (all documented in the plan's Decisions Made log):

- In-process `threading.Lock` for `feat_create_lock()` (not a literal lock file, per the plan's loose prose) — matches every other domain's precedent
- `find_feat_path_by_id` parse failures collapse to `FeatNotFoundError` (no scan fallback exists to distinguish cases)
- `feat`'s frontmatter `created`/`updated` use plain `YYYY-MM-DD` (not the other domains' microsecond timestamp) — threaded consistently through `create_feat` and the generic `update`/`set_status` adapters
- Root `README.md`: added `Feature (FEAT)` to the active artifact list, and as a drive-by fix moved `Risk (RSK)` out of the stale commented-out placeholder since it was already fully implemented

Nothing was pushed, per your instructions. The branch `feat-31-feature` is ready for review/PR whenever you want.

______________________________________________________________________

## User

add a new phase. Add a new task: feat frontmatter created and updated must use microseconds as the other timestamps.

Do not implement. Just record the task.

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 27.8s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md",
  "offset": 1,
  "limit": 10
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-30
3: id: feat-31-feature
4: status: done
5: updated: 2026-08-30
6: version: 1.11.0
7: ---
8: 
9: # Feature: Formalize the Feature artifact type ("feat")
10: 

(Showing lines 1-10 of 1984. Use offset=11 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -n \"^#### Phase\\|^## Progress\\|^### Current Status\\|^\\*\\*Note:\\*\\*\" .specmgr/feat/feat-31-feature/README.md | head -20"
}
```

**Output:**

```
280:## Progress                                    REQUIRED (LITERAL alias, composite)
550:#### Phase 0: Scaffolding
569:#### Phase 1: Models + parser (`feat/models/v1/`)
633:#### Phase 2: Tools (`feat/tools/`) — bespoke addressing
683:#### Phase 3: Resources + packaged data + schema
716:#### Phase 4: Prompts
736:#### Phase 5: Cross-cutting registration
816:**Note:** If a task's scope changes mid-flight, edit its description in
820:## Progress
822:### Current Status

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md",
  "offset": 736,
  "limit": 85
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
736: #### Phase 5: Cross-cutting registration
737: 
738: - [x] Task 5.1: `server.py` — add `feat` to the domain import line +
739:   module docstring — depends on: Task 4.3 — status: completed
740:   (2026-08-30). Alphabetical import order (`adr, dec, feat, general, gol,
741:   prb, qa, req, rsk, tsk, uc`); the module docstring gained a
742:   `specmgr://feat/schema`/`/example`/`/template` Resources block (same
743:   position as `dec`'s own block, right before it in the file), a "FEAT has
744:   no `specmgr://feat/{id}` ... no `specmgr://feat/list`" sentence appended
745:   to the "DEC has no ..." paragraph, a new "Feature tools (`feat/tools/`)"
746:   paragraph in Tools (mirroring "Decision tools", plus one extra sentence
747:   noting `feat`'s bespoke addressing and its lack of
748:   `update_feat`/`set_status_feat` of its own), the `update`/`set_status`
749:   paragraphs' domain counts bumped from eight/nine to nine/ten
750:   whole-body/total domains (matching `general/tools/update.py`'s/
751:   `set_status.py`'s own docstrings, both already updated in Phase 2), a
752:   new "Feature prompts (`feat/prompts/`)" paragraph in Prompts (mirroring
753:   "Decision prompts"), and `feat` inserted into both domain-enumeration
754:   sentences ("Modules are grouped domain-first ..." and "Add a new domain
755:   by ...") plus the final "each register `tools`, `resources`, and
756:   `prompts`" sentence.
757: - [x] Task 5.2: `pyproject.toml` package-data entry; `.pre-commit-config.yaml`
758:   (`feat/models/v1` added to schema-hook globs + new
759:   `specmgr-schema-feat-package` hook); `.github/workflows/ci.yml` (new
760:   packaged-copy drift step) — depends on: Task 3.4 — status: completed
761:   (2026-08-30). `"biz.dfch.specmgr.feat" = ["data/*.md", "data/*.json"]`
762:   added alphabetically between `dec` and `gol`. `feat/models/v1` added to
763:   the one shared `files:` regex glob in all 9 pre-existing occurrences
764:   (verified 9 before, 9 after) plus a new 10th occurrence in the new
765:   `specmgr-schema-feat-package` hook itself (mirroring
766:   `specmgr-schema-dec-package` verbatim, placed last, matching this
767:   file's insertion-order — not alphabetical — convention for per-domain
768:   hooks). CI gained a `` `src/biz/dfch/specmgr/feat/data/feat_schema.json` ``
769:   drift step, same `if: matrix.python-version == '3.13'` guard and error-
770:   message format as the `dec` step, placed immediately after it.
771: - [x] Task 5.3: `AGENTS.md` — new `feat/` bullet documenting the addressing
772:   deviation explicitly (non-UUID id, folder-per-document, bespoke
773:   `_paths.py`); update the domain-enumeration sentences; decide (and note)
774:   whether root `README.md`'s artifact list gains `Feature (FEAT)` — depends
775:   on: Task 5.1 — status: completed (2026-08-30). New `feat/` bullet added
776:   between the `dec/` and `general/` bullets, same depth/style as `dec/`'s
777:   own; the `general/` bullet's domain counts bumped eight→nine/nine→ten;
778:   `delete_*`/`validate_*` enumeration lists, the domain-register-all-three
779:   sentence, and the `server.py`-description sentence in "MCP server
780:   (server.py)" all gained `feat`/`delete_feat`/`validate_feat`. Root
781:   `README.md`: added `Feature (FEAT)` to the active bulleted list
782:   (alphabetically between `Decision (DEC)` and `Goal (GOL)`), removed
783:   `Feature (FTR)` from the commented-out placeholder (wrong abbreviation
784:   besides being redundant now), and moved `Risk (RSK)` — already a fully
785:   implemented domain per `AGENTS.md`'s own `rsk/` bullet — from the
786:   placeholder into the active list as a drive-by fix, leaving only
787:   `Acceptance Criterium (ACC)` (not yet implemented) commented out. See
788:   Decisions Made for the full reasoning.
789: - [x] Task 5.4: Regenerate `docs/MCP.md`/`docs/GENERATED.md`/`docs/api/`/
790:   `docs/feat_schema.json`; confirm all idempotent on a second run — depends
791:   on: Task 5.1, Task 5.2 — status: completed (2026-08-30). `specmgr docs`
792:   changed only `docs/api/biz.dfch.specmgr.server.md` (the Task 5.1
793:   docstring changes); `specmgr mcp-docs` produced no diff at all (FEAT's
794:   tools/resources/prompts were already fully registered before this
795:   phase, so `docs/MCP.md` was already current); `specmgr schema` (all
796:   types) and `specmgr schema --type feat --output-dir
797:   src/biz/dfch/specmgr/feat/data` both reported every file "unchanged".
798:   Every one of the four commands was run a second time immediately after
799:   and produced byte-identical output/no further `git diff` — confirmed
800:   idempotent.
801: - [x] Task 5.5: Final verification pass — walk every ACC-001..009 with
802:   concrete evidence; full quality gate end to end; set feature status to
803:   `done` — depends on: Phase 0-4 complete, Task 5.4 — status: completed
804:   (2026-08-30). Full quality gate green: `ruff format --check` (1286
805:   files already formatted), `ruff check` (all checks passed), `vulture
806:   src/ whitelist.py --min-confidence 60` (clean), full `unittest` suite
807:   (2228 tests, OK; 221 of them under `tests/feat/` specifically), `specmgr
808:   unused-code` (no unused code found). See Recent Updates for the
809:   ACC-by-ACC evidence walkthrough. Frontmatter `status` set to `done`.
810: - [x] Task 5.6: Final commit + comment on issue #31; update this README's
811:   Progress section — depends on: Task 5.5 — status: **README Progress
812:   section updated by the implementing agent (2026-08-30); commit and
813:   issue #31 comment intentionally left to the orchestrator**, per this
814:   task's own instructions to the implementing agent.
815: 
816: **Note:** If a task's scope changes mid-flight, edit its description in
817: place; rely on git history (`git log -p` on this file) to recover what was
818: originally planned, rather than keeping a second copy of the task around.
819: 
820: ## Progress

(Showing lines 736-820 of 1984. Use offset=821 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.1s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md",
  "offset": 820,
  "limit": 60
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md</path>
<type>file</type>
<content>
820: ## Progress
821: 
822: ### Current Status
823: 
824: **As of 2026-08-30**: Phase 0 (Scaffolding) committed — GitHub issue #31
825: filed, branch `feat-31-feature` created off `dev`, this plan written and
826: reviewed with the user across several rounds (body-modeling depth,
827: addressing scheme, frontmatter `version` semantics, status vocabulary,
828: `Updates` shape/naming, MCP surface scope, no-migration decision, branch
829: naming, feat-7 backlog entry); package skeleton
830: (`feat/{models/v1,tools,resources,prompts}`, `tests/feat/{models/v1, tools,resources,prompts}`) in place; `feat-7-various-improvements` Task 0.31
831: added and Task 0.30 extended. Full quality gate green (2007 tests, ruff
832: format/check clean, vulture clean). Committed as 31c5c30/164182e. **Paused
833: here, deliberately**: implementation was not what was asked for at this
834: point — the design (schema, addressing scheme, MCP surface) needs a review
835: pass by the user first, who may request adjustments, before Phase 1 (or any
836: further phase) starts. See Blockers.
837: 
838: A second design-review round produced a full worked example of the
839: proposed document structure, refined through two further review rounds
840: (ordering/comment/hyperlink questions; LITERAL-alias elimination) into
841: `.specmgr/feat/feat-31-feature/example.md` — not consumed by any code.
842: That round's resolved questions are folded into this plan's Design
843: Notes/Decisions Made above; the Blocker below still applies (no
844: `src`/`tests` code yet, but the Design Notes themselves have now had
845: four review passes).
846: 
847: **`.specmgr/feat/feat-31-feature/example.md` is the canonical,
848: implementation-ready worked example** — every design decision through the
849: fourth review round is reflected in it, and it has been cross-checked
850: against the live `models/md` engine (not just eyeballed): every implicit
851: `SPACE_SEPARATED` heading alias in the design was run through
852: `space_separated_name()` directly, which is what caught the three
853: `RelatedAdrs`/`ExplicitlyOutOfScope`/`DependsOn` issues recorded in
854: Decisions Made above. **Task 1.5 in the Task List explicitly instructs
855: the implementing agent to seed `feat_reference.md` from this file** —
856: this is a load-bearing pointer, not just narrative context, since Task
857: 1.5 is what an agent executing Phase 1 actually follows. The two
858: superseded review-process drafts (`example-initial.md`,
859: `example-revised.md`) have been removed — this is now the only example
860: file in this feature's own folder.
861: 
862: **Design review is complete, as of 2026-08-30, after five review
863: rounds.** The Blocker below is resolved — Phase 1 is authorized to
864: start. Frontmatter `status` moved from `planning` to `in-progress`
865: accordingly. **Implementation itself is explicitly deferred to a
866: separate session/agent (e.g. a Phase-Orchestrator-style agent driving
867: the Task List phase by phase)** — this design-review session closes
868: here without touching any `src`/`tests` code; Phase 0's committed
869: scaffold (`31c5c30`, `164182e`) stays exactly as-is, untouched, ready
870: for whichever agent picks up Task 1.1 next.
871: 
872: **As of 2026-08-30 (Phase 1 complete)**: `feat/models/v1/` is fully
873: implemented per Design Notes — `_util.py`, `frontmatter.py`
874: (`FeatFrontmatter`), `body.py` (`Feature`/`Plan`/`Progress` and every
875: child section class), `document.py` (`FeatDocument`), `parser.py`
876: (`parse_feat`), `summary.py` (`FeatSummary`), plus `models/v1/__init__.py`/
877: `models/__init__.py` exports. Reference fixture
878: `tests/feat/models/v1/data/feat_reference.md` seeded from `example.md`
879: (two small, content-preserving adjustments — loose lists, one shortened

(Showing lines 820-879 of 1984. Use offset=880 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 72.7s)

_Thinking:_

**Tool: task**

**Input:**

```json
{
  "description": "Add Phase 6 task to feat-31 plan",
  "subagent_type": "general",
  "prompt": "This is a documentation-only task. Do NOT write, edit, or touch any file under `src/` or `tests/` — this task is purely about editing one planning markdown file.\n\nEdit `/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md` (the feat-31-feature plan/progress document) to record a new, not-yet-implemented phase and task. Do NOT implement the actual change described by the task — only record it in the plan.\n\nThe new task to record: **`feat` frontmatter's `created`/`updated` fields must be changed to use microsecond timestamps, matching the format every other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`) already uses** (`datetime.now().isoformat(timespec=\"microseconds\")`), reversing this feature's own earlier deliberate divergence (plain `YYYY-MM-DD` dates), which is documented in this same file's Design Notes (\"Frontmatter\" section) and Decisions Made log, and implemented in `create_feat.py` and the `_update_feat`/`_set_status_feat` adapters in `general/tools/update.py`/`set_status.py`.\n\n### What to do\n\n1. **Read the whole file first** (`.specmgr/feat/feat-31-feature/README.md`) to understand its current structure: frontmatter (currently `status: done`, `version: 1.11.0`), the `### Task List` section's existing `#### Phase 0` through `#### Phase 5` (all marked complete), the `## Progress` section's `### Current Status`/`### Blockers`/`### Updates`/`### Recent Updates`/`### Decisions Made`.\n\n2. **Add a new `#### Phase 6: ...` section** to the `### Task List`, immediately after the existing `#### Phase 5: Cross-cutting registration` section and before the \"**Note:** If a task's scope changes mid-flight...\" closing note. Give it a descriptive title, e.g. `#### Phase 6: Frontmatter timestamp format fix`. Add exactly one task under it (number it `Task 6.1`, matching this plan's existing `Task N.M` numbering convention), phrased along these lines (adjust wording/detail as you see fit, but keep it accurate and specific about the affected files):\n\n   - Task 6.1: Change `feat` frontmatter's `created`/`updated` fields from plain `YYYY-MM-DD` dates to microsecond timestamps (`datetime.now().isoformat(timespec=\"microseconds\")`), matching every other whole-body domain's own convention. Affects `feat/tools/create_feat.py` (frontmatter construction), `general/tools/update.py`'s `_update_feat` adapter, `general/tools/set_status.py`'s `_set_status_feat` adapter, the Design Notes' \"Frontmatter\" section (which currently documents the plain-date divergence as deliberate), and any tests asserting the plain-date format (`tests/feat/tools/test_create_feat.py`, `tests/feat/tools/test_integration.py`, `tests/general/tools/` equivalents if any). This reverses this feature's own earlier deliberate design decision (see Decisions Made) — reversing it needs the same care as the original decision: update the Decisions Made log with a new entry explaining why, not just silently change the code. — depends on: Phase 5 complete — status: not-started\n\n   Mark the task `not-started` — do not implement it, do not touch any `src`/`tests` file.\n\n3. **Update the plan's own frontmatter**: since there is now new, unstarted work, change `status` from `done` back to `in-progress` (this file's own frontmatter status vocabulary is `planning`/`in-progress`/`review`/`done`, per ADR e369ee2e-3353-4f92-991c-6367d76d832e's convention — NOT `feat`'s own schema's 4-value set, this is a different, pre-existing document type). Bump `version` by one minor version (e.g. `1.11.0` -> `1.12.0`) and update `updated` to today's date if you can determine it, otherwise leave it as the file's existing `updated` date (do not guess a wrong date).\n\n4. **Add a short new dated entry to `### Recent Updates`** (at the top, above the existing entries, matching this section's own existing newest-first convention) noting that Phase 6 was added, describing the task, and stating explicitly that this is planning/recording only -- no `src`/`tests` code was touched.\n\n5. **Update `### Current Status`** with one short sentence noting that a new Phase 6 (frontmatter timestamp format fix) has been added to the Task List as a not-yet-started follow-up item, and that the feature's `done` status has reverted to `in-progress` to reflect this.\n\n6. Do NOT add a new Acceptance Criteria entry, do NOT change the Requirements section, do NOT touch Scope/Dependencies/Design Notes' body text beyond what's described above — keep this a minimal, focused planning edit. Do NOT run any quality gate commands, do NOT commit, do NOT touch GitHub issue #31 — the orchestrator will handle verification and committing.\n\nReport back: the exact diff/summary of what you changed (file, line ranges, new content), confirming no `src/`/`tests/` files were touched.\n"
}
```

**Output:**

```
<task id="ses_fac4d0026ffeosB38MKaOQwYMM" state="completed">
<task_result>
## Summary

I edited `/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-31-feature/README.md` only (confirmed via `git status --porcelain` — no `src/` or `tests/` files touched). Changes, in file order:

1. **Frontmatter (lines 1–7)**: `status: done` → `status: in-progress`; `version: 1.11.0` → `version: 1.12.0`; `updated`/`created` left as `2026-08-30` (already today's date).

2. **Task List — new `#### Phase 6: Frontmatter timestamp format fix`** inserted immediately after Phase 5's Task 5.6 and before the "**Note:** If a task's scope changes mid-flight..." closing note. Contains exactly one unchecked (`- [ ]`) task, **Task 6.1**, describing the switch of `feat` frontmatter `created`/`updated` from plain `YYYY-MM-DD` dates to microsecond `datetime.now().isoformat(timespec="microseconds")` timestamps, naming the affected files (`create_feat.py`, `_update_feat`/`_set_status_feat` adapters, Design Notes' Frontmatter section, relevant tests) and noting the Decisions Made log must be updated when implemented — `status: not-started`, `depends on: Phase 5 complete`.

3. **`### Current Status`**: added a new paragraph at the top noting Phase 6 was added as a not-yet-started follow-up, that this is planning/recording only, and that feature status reverted from `done` to `in-progress`.

4. **`### Recent Updates`**: added a new newest-first entry `#### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)` at the top, summarizing the new Phase 6/Task 6.1, the frontmatter status/version bump, and explicitly stating no `src`/`tests` code was touched.

No changes were made to Requirements, Acceptance Criteria, Scope, Dependencies, Design Notes body text, or the Decisions Made log itself — only the plan/progress bookkeeping described above.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 2.9s)

Let's verify.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git status --short"
}
```

**Output:**

```
 M .specmgr/feat/feat-31-feature/README.md

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.2s)

Good, only the plan file touched. Let's review the diff in full.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git diff .specmgr/feat/feat-31-feature/README.md"
}
```

**Output:**

```
diff --git a/.specmgr/feat/feat-31-feature/README.md b/.specmgr/feat/feat-31-feature/README.md
index efd3a4c..ea03fff 100644
--- a/.specmgr/feat/feat-31-feature/README.md
+++ b/.specmgr/feat/feat-31-feature/README.md
@@ -1,9 +1,9 @@
 ---
 created: 2026-08-30
 id: feat-31-feature
-status: done
+status: in-progress
 updated: 2026-08-30
-version: 1.11.0
+version: 1.12.0
 ---
 
 # Feature: Formalize the Feature artifact type ("feat")
@@ -813,6 +813,25 @@ discipline.
   issue #31 comment intentionally left to the orchestrator**, per this
   task's own instructions to the implementing agent.
 
+#### Phase 6: Frontmatter timestamp format fix
+
+- [ ] Task 6.1: Change `feat` frontmatter's `created`/`updated` fields
+  from plain `YYYY-MM-DD` dates to microsecond timestamps
+  (`datetime.now().isoformat(timespec="microseconds")`), matching every
+  other whole-body domain's own convention (`req`/`uc`/`tsk`/`qa`/`prb`/
+  `gol`/`rsk`/`dec`). Affects `feat/tools/create_feat.py` (frontmatter
+  construction), `general/tools/update.py`'s `_update_feat` adapter,
+  `general/tools/set_status.py`'s `_set_status_feat` adapter, the Design
+  Notes' "Frontmatter" section (which currently documents the plain-date
+  divergence as deliberate), and any tests asserting the plain-date
+  format (`tests/feat/tools/test_create_feat.py`,
+  `tests/feat/tools/test_integration.py`, `tests/general/tools/`
+  equivalents if any). This reverses this feature's own earlier
+  deliberate design decision (see Decisions Made) — reversing it needs
+  the same care as the original decision: update the Decisions Made log
+  with a new entry explaining why, not just silently change the code —
+  depends on: Phase 5 complete — status: not-started
+
 **Note:** If a task's scope changes mid-flight, edit its description in
 place; rely on git history (`git log -p` on this file) to recover what was
 originally planned, rather than keeping a second copy of the task around.
@@ -821,6 +840,16 @@ originally planned, rather than keeping a second copy of the task around.
 
 ### Current Status
 
+**As of 2026-08-30 (Phase 6 recorded, not started)**: A new `#### Phase
+6: Frontmatter timestamp format fix` has been added to the Task List
+(Task 6.1, not-started) to reverse this feature's own earlier deliberate
+divergence and switch `feat` frontmatter's `created`/`updated` fields
+from plain `YYYY-MM-DD` dates to microsecond timestamps, matching every
+other whole-body domain. This is planning/recording only — no
+`src`/`tests` code has been touched. The feature's frontmatter `status`
+has reverted from `done` to `in-progress` to reflect this new,
+not-yet-started follow-up work.
+
 **As of 2026-08-30**: Phase 0 (Scaffolding) committed — GitHub issue #31
 filed, branch `feat-31-feature` created off `dev`, this plan written and
 reviewed with the user across several rounds (body-modeling depth,
@@ -1025,6 +1054,30 @@ implementing agent's.
 
 ### Recent Updates
 
+#### Update 2026-08-30 (Phase 6 recorded — frontmatter timestamp format fix)
+
+- Added a new `#### Phase 6: Frontmatter timestamp format fix` to the
+  Task List, with one new task, **Task 6.1** (not-started): change
+  `feat` frontmatter's `created`/`updated` fields from plain
+  `YYYY-MM-DD` dates to microsecond timestamps
+  (`datetime.now().isoformat(timespec="microseconds")`), matching every
+  other whole-body domain (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/
+  `dec`) already in use — reversing this feature's own earlier
+  deliberate divergence documented in Design Notes' "Frontmatter"
+  section and in Decisions Made. The task calls out the affected files
+  (`feat/tools/create_feat.py`, `general/tools/update.py`'s
+  `_update_feat` adapter, `general/tools/set_status.py`'s
+  `_set_status_feat` adapter, the Design Notes prose, and the tests
+  asserting the plain-date format) and requires a new Decisions Made
+  entry when the reversal is actually implemented, not a silent code
+  change.
+- Frontmatter `status` reverted from `done` to `in-progress` and
+  `version` bumped from `1.11.0` to `1.12.0` to reflect this new,
+  not-yet-started follow-up item.
+- **This is planning/recording only — no `src`/`tests` code was
+  touched.** Task 6.1 remains not-started; implementation is deferred to
+  a future session.
+
 #### Update 2026-08-30 (Phase 5 complete — cross-cutting registration; feature done)
 
 - **`server.py` (Task 5.1)**: added `feat` to the domain import line

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

This edit is exactly what was asked: minimal, focused, planning-only, no code touched. Let's run the (very lightweight) quality gate sanity check just to be safe, then commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff format --check 2>&1 | tail -3 && uv run --frozen ruff check 2>&1 | tail -3"
}
```

**Output:**

```
1286 files already formatted
All checks passed!

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.6s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git add -A && git commit -m \"docs(feat-31): record Phase 6 task -- feat frontmatter must use microsecond timestamps\n\nAdds Task 6.1 (not-started): change feat frontmatter created/updated\nfrom plain YYYY-MM-DD dates to microsecond timestamps, matching every\nother whole-body domain. Reverses this feature's own earlier deliberate\ndivergence -- recorded only, not implemented.\n\nFeature status reverted from done to in-progress to reflect the new,\nnot-yet-started follow-up item.\" -q",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...........................................(no files to check)Skipped
vulture..............................................(no files to check)Skipped
unittest.............................................(no files to check)Skipped
specmgr coverage-badge...............................(no files to check)Skipped
specmgr docs.........................................(no files to check)Skipped
specmgr mcp-docs.....................................(no files to check)Skipped
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

Committed successfully — since it's a `.specmgr/` markdown-only change, all the `src`/`tests`-scoped hooks correctly skipped.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -3"
}
```

**Output:**

```
ab2b5ab docs(feat-31): record Phase 6 task -- feat frontmatter must use microsecond timestamps
ae53f51 feat(feat-31): cross-cutting registration for Feature (feat) domain (Phase 5)
b974b63 feat(feat-31): implement Feature (feat) prompts (Phase 4)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.6s)

Done. I recorded a new **Phase 6: Frontmatter timestamp format fix** in `.specmgr/feat/feat-31-feature/README.md` with a single not-started task (Task 6.1): change `feat`'s frontmatter `created`/`updated` fields from plain `YYYY-MM-DD` dates to microsecond timestamps, matching every other whole-body domain — reversing this feature's own earlier deliberate divergence. Per your instruction, this was recording only:

- No `src/`/`tests/` files were touched (verified via `git status`/diff).
- The plan's frontmatter `status` reverted from `done` to `in-progress` and `version` bumped `1.11.0` → `1.12.0` to reflect the new, unstarted follow-up work.
- A dated `Recent Updates` entry and a `Current Status` note were added, consistent with this plan's existing bookkeeping conventions.
- Committed as `ab2b5ab` (docs-only commit; all code-scoped pre-commit hooks correctly skipped since nothing under `src/`/`tests/` changed).

Task 6.1 remains `not-started` and is ready to be picked up by a future implementation session/phase.

______________________________________________________________________
