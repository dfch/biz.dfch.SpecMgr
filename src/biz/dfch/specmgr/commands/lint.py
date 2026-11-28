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

"""``lint`` -- the in-tree spec artifact parseability gate (feat-218, Phase 100).

Runs the model-level FULL parse of each document's own domain over the
document's complete on-disk text and reports every unparseable document
(file path + parse error), not just the first (REQ-001). Every domain is
parsed through the domain registry's own ``parse_text`` adapters (the
``<d>.models`` package's pure text parsers -- ``parse_req``, ``parse_uc``,
... -- no file I/O, no ``DocCache``, no ``list_<d>``, no MCP tool). The
parse-failure channels are the repo's existing ones, imported rather than
re-listed: ``general.models.validate_result._CAUGHT_EXCEPTIONS``
(``AssertionError``, ``pydantic.ValidationError``, ``yaml.YAMLError``)
plus UTF-8 decode errors -- caught per file so one bad file cannot abort
the aggregate report. Full parses only, never the listing path (REQ-003):
the ``list_feat`` dirty stage (frontmatter+H1 only, DEC 3982712a) is
precisely the masking that hid the feat-214 defect for three consecutive
commits. The content parse of a sharded ``docs/<type>/<lang>/<shard>/``
file is LANGUAGE-AWARE (feat-245 Phase 120): the language is the path's
own shape-valid language dir (``en`` = the canonical parse, byte-
identical to today's EN path) -- derived from the ``docs`` anchor or,
root-name-independently, the sharded shape's own position in path mode
(feat-245 Phase 180, G2), and POSITION-RELATIVE to the domain's configured
base directory in sweep mode (root-name-independent: the sweep
behaves identically under any ``SPECMGR_DOCS_DIR`` root, not only one
named ``docs`` -- feat-245 Phase 160, D9) -- and a shape-valid language
dir WITHOUT a packaged heading-mapping table fails the file with the
table loader's own actionable ``ValueError`` (the existing no-table
content error, exit 1 -- the placement itself is valid, so it is NOT a
layout violation).

Three scopes, so the cost scales with the size of a change and never with
the size of the corpus (REQ-004):

* **Path mode** -- explicit ``PATHS`` on the command line. Each path's
  type is inferred from the path layout ALONE (REQ-005), independent of
  every ``SPECMGR_*_DIR`` variable, with four rules, in order: the
  docs-anchored sharded valid shape ``docs/<type>/<lang>/<2-hex-shard>/
  <file>.md`` (``type`` one of the thirteen UUID domains -- feat-245
  Phase 120, REQ-006); the root-name-independent sharded shape
  ``<type>/<lang>/<2-hex>/<file>.md`` by shape alone, under a docs root
  of ANY name (``specdocs/req/en/ab/x.md`` -- feat-245 Phase 180, G2;
  the path-mode parse language is derived from that same position, so a
  table-closed variant parses with its own table, also under
  ``--type``); the containing directory named after a type (a non-docs-
  anchored position, e.g. ``<base>/req/x.md``); the ``feat/<id>/
  README.md`` shape (unchanged for every position, ``docs/<feat>``
  anchored included). The ``docs`` anchor (final rule, feat-245 Phase 200)
  is a pure function of the resolved path, the resolved working directory
  and the path's repo roots (EVERY ancestor directory that holds a
  ``.git`` entry, not only the nearest). (1) Root candidates, in order:
  the working directory -- only when the path lies under it and it is
  inside one of those repo roots, or no repo exists -- then every repo
  root, from the outermost inward; a candidate anchors the path when
  ``docs`` is the FIRST segment of the path relative to it. (2) A
  candidate's anchor is ROOTED unless another repo root lies strictly
  inside the anchoring ``docs`` directory (a repo cloned or vendored into
  a docs tree; a ``docs`` directory that is itself a repo root stays
  rooted); the first rooted anchor wins, and an anchor that is not rooted
  is taken only when no later candidate gives a rooted one. (3) When no
  candidate anchors, the LAST ``docs`` segment anchors, un-rooted --
  searched inside the outermost repo root, or over the whole path when no
  repo exists. A registered UUID domain under ANY anchor is
  placement-validated; a rooted anchor's non-domain skip is unconditional,
  an un-rooted anchor's applies only when no other rule matches.
  Consequences: a working directory above every repo and a ``docs``-named
  directory above the outermost repo root never anchor; a ``docs`` tree
  that is itself a repo (a submodule) and a vendored repo's own ``docs/``
  are gated; a nested project (``mono/.git``, docs at ``mono/proj/docs/``)
  is placement-gated from every working directory, but its non-domain
  ``docs/<dir>/`` files are skipped unconditionally only when lint runs
  from inside the project -- from ``mono/``,
  ``proj/docs/archive/sop/README.md`` is linted as ``sop`` (its
  parent-name rule matches); without any repo, a ``docs``-named ancestor
  of the project can anchor (nothing marks where the project starts).
  ``--type`` overrides inference for the parse, but
  it never rescues a misplaced ``docs/<type>/`` file -- the placement
  violation stands. A file anchored under ``docs/<uuid-domain>/`` that
  misses the sharded placement (missing language dir, missing or
  invalid language dir, missing shard dir, non-hex shard, deeper than
  one shard level) is a LAYOUT VIOLATION: it is never parsed, reported
  with its own block naming the defect and the correct path, counted in
  the summary's own ``layout`` counter, and fails the run with exit 2
  (REQ-006 -- ahead of any parse failure in the same run). A file
  anchored under ``docs/<dir>/`` where ``<dir>`` is not a registered
  domain (``docs/archive/adr/x.md`` at depth >= 3, ``docs/api/x/y.md``)
  is SKIPPED and counted (exit 0) -- the non-domain-dir behavior. A
  file directly under a ``docs`` directory (``docs/x.md``) is not
  anchored: it keeps the legacy rules. Any other unrecognized layout is
  a usage error (exit 2) unless ``--skip-unrecognized`` is given, in
  which case the path is skipped and counted.
* **Type sweep** -- ``--type T`` with no paths sweeps every document of
  that type: for the thirteen sharded UUID domains, the domain-wide
  union of every language directory's sharded listing (``en/`` plus
  every variant ``{language}/`` directory under the domain's base --
  Task 150.155: a variant document is linted exactly like its EN file);
  for ``feat``, its registered base directory's folder-per-document
  listing (unchanged -- the single-language domain). The explicit
  ``--dir`` argument (valid with ``--type`` ONLY, and without explicit
  paths) narrows the sweep to exactly that one directory's sharded (or
  ``feat`` folder) listing (REQ-006). Each sweep item's parse language
  is derived POSITION-RELATIVE to the domain's configured base
  directory (``language_for_doc_path`` over ``doc_domain_base_dir`` --
  root-name-independent, Phase 160, D9: the sweep behaves identically
  under any ``SPECMGR_DOCS_DIR`` root; path mode derives it from the
  path's own docs anchor or sharded-shape position, root-name-
  independent too since Phase 180, G2). ``--type T`` against an empty
  or missing base directory exits 0 with a 0-document summary: a
  registered-but-empty domain is not a misconfiguration.
* **All sweep** -- ``--all`` sweeps every registered type, each with
  the same default enumeration as its ``--type`` sweep (the all-
  languages union for the thirteen sharded UUID domains, the folder
  listing for ``feat``). Explicit paths combined with ``--all`` is a
  usage error; ``--all`` that discovers no document at all is a
  probable misconfiguration (exit 2).

Import safety (REQ-002): this module has NO module-level import of the
domain registry (``general.tools._domains``) or of any ``tools`` package.
``cli.py`` imports every ``commands/*`` module at module level, and any
such import would eagerly run the package's own ``__init__`` and drag in
the ``mcp`` extra -- verified by Task 100.100's real import test (with
``mcp`` blocked, ``commands.diagram`` and ``cli.py`` both fail to import
already; only the top-level ``models.*`` packages, ``_envregistry``, and
``plantuml.*`` import cleanly without the extra). Everything
registry-backed is therefore loaded inside the command body by
:func:`_registry_backed`, behind the ``ImportError`` -> exit 1 guard that
mirrors ``specmgr mcp`` and ``specmgr diagram``: the guard turns the
missing-extra condition into the clear exit-1 message whenever the CLI
is importable but the registry-backed chain is not -- in today's
``[cli]``-only install the sibling commands' pre-existing
package-init tangles block the CLI import first (issue #238 territory),
but this module no longer contributes to that. There is no module-level
specmgr import at all (the registry's ``--type`` acceptance set is
deliberately NOT derived at import time, so no Typer ``choices``).

Exit codes (pinned, REQ-008 -- the plantuml-check family):

* ``0`` -- every document parsed. Includes a run in which every given
  path was skipped (0-linted summary), and ``--type T`` against an empty
  or missing base directory (0-document summary).
* ``1`` -- at least one document failed to parse, or the ``mcp`` extra
  is missing.
* ``2`` -- usage or resolution error: no paths and no sweep flag; an
  unreadable or missing path; an unrecognized layout without
  ``--skip-unrecognized``; ``--dir`` without ``--type``; ``--dir``
  combined with explicit paths; explicit paths combined with ``--all``;
  an unknown ``--type``; ``--all`` that discovers no document at all;
  at least one LAYOUT VIOLATION (a file anchored under a registered
  UUID domain's ``docs`` directory that misses the sharded placement --
  feat-245 Phase 120, REQ-006's own exit-2 member; it outranks a parse
  failure in the same run, which is reported too).

Report: the layout violations first (one block each: the file named with
``layout violation: <defect>; correct path: <path>`` -- the correct path
is concrete, ``docs/<type>/<lang>/<shard>/<file>.md``, when the file
name carries a canonical uuid, shape-level with the ``<2-hex-shard>``
placeholder otherwise -- followed by the file's own repair pointer),
then every failing ``(path, error)`` pair is printed (the error is the
caught exception's own text, verbatim), each followed by its repair
pointer: ``/repair {type} {id}`` with the id derived from the path (the
``feat/<id>/README.md`` folder name for ``feat``; the canonical UUID
embedded in the file name for the others, printed lowercased -- ids are
case-insensitive on read and lowercase is the canonical form), falling
back to ``/repair {type}`` when no id can be derived. One summary per
invocation: ``summary: linted=N failed=N skipped=N layout=N``, where
``linted`` is the number of documents the gate took on (parse
attempted), ``failed`` the subset that failed to parse, ``skipped`` the
non-domain-dir and unrecognized-layout skips, and ``layout`` the layout
violations (never parsed, never in ``linted``).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import typer

__all__ = [
    "EXIT_LINT_FAILURE",
    "EXIT_OK",
    "EXIT_USAGE",
    "lint",
]

#: The pinned exit codes (see the module docstring for the full table).
EXIT_OK = 0
EXIT_LINT_FAILURE = 1
EXIT_USAGE = 2

#: The encoding every document is read with (a decode failure is a
#: per-file parse failure, not a usage error).
_ENCODING = "utf-8"

#: The base name the feat folder shape compares against (the feat fixed
#: filename).
_README_BASENAME = "README.md"

#: A canonical (8-4-4-4-12 hex) UUID, searched for in a file name to
#: derive the repair pointer's id (ids are case-insensitive on read; the
#: match is printed lowercased -- the canonical form).
_UUID_PATTERN = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")

#: The language-dir shape the sharded placement requires (the mirror of
#: ``general.tools._path_safety.LANGUAGE_PATTERN``, fullmatch
#: ``^[a-z]{2}$`` -- the open set the shape guard passes; whether the
#: language carries a packaged heading table is the CONTENT error's
#: business, never the placement's). An import-safe mirror (no module-level
#: specmgr import, see the module docstring), drift-pinned to its source by
#: ``tests/commands/test_lint.py`` (feat-245 Phase 180, S2).
_LANG_DIR_PATTERN = re.compile(r"^[a-z]{2}$")

#: The shard width (the import-safe mirror of ``general.tools._doc_paths.
#: SHARD_DIGITS``, drift-pinned to it by ``tests/commands/test_lint.py`` --
#: feat-245 Phase 180, S2): the ONE constant both the shard-dir shape
#: (:data:`_SHARD_DIR_PATTERN`) and a layout violation's concrete correct
#: path (:func:`_correct_sharded_path`) derive from, so validation and
#: correction cannot disagree.
_SHARD_DIGITS = 2

#: The shard-dir shape the sharded placement requires: exactly
#: :data:`_SHARD_DIGITS` lowercase hex digits (a document uuid's first
#: characters -- uuid digits are hex), derived from the mirrored constant.
_SHARD_DIR_PATTERN = re.compile(rf"^[0-9a-f]{{{_SHARD_DIGITS}}}$")

#: The placeholder a layout violation's correct path uses for the shard
#: when the file name carries no canonical uuid to make it concrete.
_SHARD_PLACEHOLDER = "<2-hex-shard>"

#: The default language dir (the import-safe mirror of ``general.models.
#: heading_table.DEFAULT_LANGUAGE``, drift-pinned to it -- feat-245 Phase
#: 180, S2): the fallback a correct path names when the misplaced file's
#: own path carries no shape-valid language dir.
_DEFAULT_LANGUAGE = "en"

#: The name of the version-control marker: every ancestor directory of a
#: path that holds this entry (a ``.git`` directory, or the ``.git`` file of
#: a worktree or submodule) is a repo root the docs anchor may be taken
#: relative to (feat-245 Phase 180, E2; every such ancestor, not only the
#: nearest, since Phase 200, E1).
_REPO_ROOT_MARKER = ".git"

#: The directory name a docs anchor is made of.
_DOCS_DIR_NAME = "docs"


@dataclass(frozen=True)
class _RegistryBacked:
    """The registry-backed names this module loads lazily (see :func:`_registry_backed`).

    Attributes:
        feat:
            The ``feat`` domain name (``general.tools._domains.FEAT``) --
            the one whole-body domain whose path shape is
            ``<base>/<id>/README.md``.
        all_domains:
            Every registered document type (``general.tools._domains.
            ALL_DOMAINS``: the whole-body domains) -- the ``--type``
            acceptance set, derived, never hand-listed.
        uuid_domains:
            The thirteen UUID-shaped domains (``general.tools._domains.
            UUID_DOMAINS``) -- the domains the sharded placement
            validates (feat-245 Phase 120, REQ-006; ``feat`` keeps its
            folder shape and is never placement-validated).
        whole_body_domain:
            The name -> ``WholeBodyDomain`` registry lookup (``general.
            tools._domains.whole_body_domain``) -- the source of each
            whole-body domain's ``base_dir``/``iter_paths``/``parse_text``
            adapters.
        domain_base_dir:
            The sharded domains' domain-base resolver (``general.tools.
            _doc_paths.doc_domain_base_dir``): the ``docs/<type>/``
            parent of every per-language directory -- the base the
            all-languages default sweep enumerates over (Task 150.155).
        iter_all_languages:
            The sharded domains' all-languages listing (``general.tools.
            _doc_paths.iter_doc_paths_all_languages``): the union of the
            sharded listings of ``en/`` plus every shape-valid language
            directory under the domain base (Task 150.155).
        language_for_doc_path:
            The position-relative language derivation (``general.tools.
            _doc_paths.language_for_doc_path``): the path's first
            subdirectory under a given domain base, a shape-valid
            two-letter code, ``None`` otherwise -- the sweep items'
            parse-language source (Task 160.100, D9: root-name-
            independent, unlike the path-mode docs-anchor derivation).
        caught_exceptions:
            The whole-body parse-failure channels (``general.models.
            validate_result._CAUGHT_EXCEPTIONS``: ``AssertionError``,
            ``pydantic.ValidationError``, ``yaml.YAMLError``).
    """

    feat: str
    all_domains: tuple[str, ...]
    uuid_domains: tuple[str, ...]
    whole_body_domain: Callable[[str], Any]
    domain_base_dir: Callable[[str], Path]
    iter_all_languages: Callable[[Path], Iterator[Path]]
    language_for_doc_path: Callable[[Path, Path], str | None]
    caught_exceptions: tuple[type[Exception], ...]


@dataclass(frozen=True)
class _WorkItem:
    """One document the gate took on: its path, its resolved type, its text.

    Attributes:
        path:
            The document's on-disk path (as given, or as enumerated in
            sweep mode).
        doc_type:
            The resolved document type (layout-inferred or ``--type``).
        text:
            The complete file text for path-mode items (read during
            resolution; a read failure there is a usage error or a
            pre-recorded decode failure). ``None`` for sweep items --
            their text is read at parse time, where a read failure is a
            per-file parse failure (the file was enumerated by the
            registry, not named by the user).
        sweep:
            ``True`` for sweep-enumerated items, ``False`` for user-named
            path-mode items (Task 160.100, D9): the two modes derive the
            parse language differently -- path mode from the path's own
            docs anchor or sharded-shape position (:func:`_parse_language`),
            the sweep position-relative to the configured domain base
            (:func:`_sweep_parse_language`, root-name-independent).
        anchor:
            The path-mode item's docs anchor, computed once per path
            during resolution and reused for the parse-language
            derivation (feat-245 Phase 190, S1). ``None`` for sweep items.
    """

    path: Path
    doc_type: str
    text: str | None
    sweep: bool
    anchor: _Anchor | None = None


@dataclass(frozen=True)
class _Failure:
    """One document that failed the gate: its path, its type, the error text.

    Attributes:
        path:
            The document's on-disk path.
        doc_type:
            The resolved document type (drives the repair pointer's shape).
        error:
            The caught exception's own text, verbatim (UTF-8 decode
            failures carry a short ``not valid utf-8: ...`` prefix).
    """

    path: Path
    doc_type: str
    error: str


@dataclass(frozen=True)
class _LayoutViolation:
    """One file placed outside the sharded layout (feat-245 Phase 120, REQ-006).

    A layout violation is its own lint result class: neither a usage
    error (the file exists and is readable) nor a content-parse failure
    (the file is never parsed). It fails the run with exit 2 -- the
    usage/resolution code, REQ-006's own enumeration -- ahead of any
    parse failure in the same run.

    Attributes:
        path:
            The file's on-disk path (as given).
        doc_type:
            The registered UUID domain the file is anchored under (drives
            the repair pointer's shape).
        kind:
            The placement defect: ``missing language directory``,
            ``missing (valid) language directory``, ``missing shard
            directory``, ``non-hex shard``, or ``deeper than one shard
            level``.
        correct_path:
            The path the file SHOULD live at: concrete
            (``docs/<type>/<lang>/<shard>/<file>.md``) when the file name
            carries a canonical uuid, shape-level (the
            ``<2-hex-shard>`` placeholder) otherwise.
    """

    path: Path
    doc_type: str
    kind: str
    correct_path: str


def _registry_backed() -> _RegistryBacked:
    """The registry-backed names, imported lazily (they require the ``mcp`` extra).

    Every name below lives in a package whose import chain reaches
    ``server.py`` (the ``general``/domain-package ``__init__``s eagerly
    import their ``tools``/``prompts`` sub-packages; the ``tools`` packages
    import the shared ``mcp`` application instance) -- see the module
    docstring's Task 100.100 import-test finding. The caller catches the
    resulting ``ImportError`` as the missing-extra condition (exit 1).

    Returns:
        The :class:`_RegistryBacked` bundle of registry-backed names.
    """
    from ..general.models.validate_result import _CAUGHT_EXCEPTIONS  # noqa: PLC0415
    from ..general.tools._doc_paths import (  # noqa: PLC0415
        doc_domain_base_dir,
        iter_doc_paths_all_languages,
        language_for_doc_path,
    )
    from ..general.tools._domains import ALL_DOMAINS, FEAT, UUID_DOMAINS, whole_body_domain  # noqa: PLC0415

    result = _RegistryBacked(
        feat=FEAT,
        all_domains=ALL_DOMAINS,
        uuid_domains=UUID_DOMAINS,
        whole_body_domain=whole_body_domain,
        domain_base_dir=doc_domain_base_dir,
        iter_all_languages=iter_doc_paths_all_languages,
        language_for_doc_path=language_for_doc_path,
        caught_exceptions=_CAUGHT_EXCEPTIONS,
    )
    return result


def _is_feat_folder_shape(path: Path, reg: _RegistryBacked) -> bool:
    """The ``feat/<id>/README.md`` folder shape (the ``feat`` path rule).

    Base name ``README.md`` with exactly one non-``README.md`` path
    segment (the feature's id) between a directory named after the
    ``feat`` domain and the file (e.g. ``.specmgr/feat/feat-1-x/README.md``).
    The one predicate shared by BOTH the path-layout type inference
    (:func:`_infer_type`) and the repair pointer's id derivation
    (:func:`_derive_id`), so the two cannot drift apart (Phase 160, I1).

    Args:
        path: The document's path.
        reg: The registry-backed names (the ``feat`` domain name).

    Returns:
        ``True`` when the path has the ``feat`` folder shape.
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = (
        path.name == _README_BASENAME
        and path.parent.name not in ("", _README_BASENAME)
        and path.parent.parent.name == reg.feat
    )
    return result


@dataclass(frozen=True)
class _Anchor:
    """A path-mode path's docs anchor, computed ONCE per path (feat-245 Phase 180, E2; Phase 190, S1; Phase 200).

    The placement classifier's own anchor (feat-245 Phase 120, REQ-006):
    a path is docs-anchored when it carries a ``docs`` directory segment
    with at least one directory and the file after it
    (``docs/<dir>/…/<file>``). WHICH ``docs`` segment anchors, and whether
    the anchor is rooted, is decided by :func:`_anchor_rule` (the final
    rule, Phase 200 -- stated in full in the module docstring). A file
    directly under a ``docs`` directory (``docs/x.md``) is NOT anchored --
    it keeps the legacy inference rules.

    Attributes:
        layout:
            ``(first segment, inner directory segments)`` -- the first
            segment under the anchoring ``docs`` dir plus the tuple of
            DIRECTORY segments between it and the file (``()`` for a file
            directly in the anchored directory, ``(lang, shard)`` for the
            valid sharded placement, longer for the misplaced depths) --
            or ``None`` when the path is not docs-anchored.
        rooted:
            Whether the anchor is a ROOTED one: ``docs`` is the first
            segment relative to a root candidate (the working directory
            or a repo root) and no other repo root lies strictly inside
            that ``docs`` directory. A rooted anchor is trustworthy: a
            file under a rooted ``docs/<dir>/`` with a non-domain
            ``<dir>`` is skipped unconditionally (the real
            ``docs/archive/sop/README.md`` stays skipped even though its
            parent is named after a type). An un-rooted anchor (a
            candidate's ``docs`` directory that holds a nested repo, or
            the last-``docs`` fallback) may be an unrelated directory, so
            the gate skips such a file only when no other inference rule
            matches -- by design an un-rooted anchor therefore accepts
            ``docs/archive/sop/README.md`` as ``sop`` (its parent-name
            rule matches; Decisions Made 2026-11-27). Always ``False``
            when ``layout`` is ``None``.
    """

    layout: tuple[str, tuple[str, ...]] | None
    rooted: bool


def _git_ancestors(resolved: Path) -> frozenset[Path]:
    """Every ancestor directory of a resolved path that holds a ``.git`` entry (feat-245 Phase 200, E1).

    The one filesystem read of the docs-anchor rule, kept apart from the
    pure rule itself (:func:`_anchor_rule`): EVERY such ancestor is a repo
    root, not only the nearest -- a superproject above a submodule or a
    vendored repo included (:data:`_REPO_ROOT_MARKER`: a directory, or the
    ``.git`` file of a worktree or submodule).

    Args:
        resolved: The document's resolved (absolute) path.

    Returns:
        The repo roots among the path's ancestor directories (empty when
        the path is in no repo).
    """
    assert isinstance(resolved, Path), type(resolved)
    result = frozenset(ancestor for ancestor in resolved.parents if (ancestor / _REPO_ROOT_MARKER).exists())
    return result


def _anchor_layout(parts: tuple[str, ...], index: int) -> tuple[str, tuple[str, ...]]:
    """The :attr:`_Anchor.layout` of the ``docs`` segment at ``parts[index]``.

    Args:
        parts: The path segments (the file name last).
        index: The index of the anchoring ``docs`` segment (at least one
            directory and the file follow it).

    Returns:
        ``(first segment, inner directory segments)``.
    """
    assert isinstance(parts, tuple), type(parts)
    assert 0 <= index <= len(parts) - 3, (index, parts)
    result = (parts[index + 1], tuple(parts[index + 2 : -1]))
    return result


def _anchor_rule(resolved: Path, cwd: Path, git_roots: frozenset[Path]) -> _Anchor:
    """The docs-anchor rule (feat-245 Phase 200 -- the final rule), a PURE function of its three arguments.

    No filesystem access and no working-directory read: the rule is
    decided from the resolved path, the resolved working directory and the
    path's repo roots alone, so every layout is one row of the table test
    (``tests/commands/test_lint.py``). In order:

    1. **Root candidates**: the working directory -- only when the path
       lies under it AND it is inside one of the repo roots (or no repo
       exists), so a working directory ABOVE every repo is never a root
       (the Phase 180 E2 case) -- then EVERY repo root, from the outermost
       inward. A candidate anchors the path when ``docs`` is the first
       segment of the path relative to it, with at least one directory
       and the file after it.
    2. **Rooted or not**: a candidate's anchor is ROOTED unless another
       repo root lies strictly inside the anchoring ``docs`` directory (a
       repo cloned or vendored into a docs tree, e.g. a dotfiles
       ``~/.git`` above ``~/docs/repo/.git``; a ``docs`` directory that is
       itself a repo root stays rooted). The first rooted anchor in
       candidate order wins; a candidate anchor that is not rooted is
       taken, un-rooted, only when no later candidate gives a rooted one.
    3. **Fallback**: when no candidate anchors, the LAST ``docs`` segment
       anchors, un-rooted -- searched inside the outermost repo root (a
       ``docs``-named directory above every repo never anchors), or over
       the whole path when no repo exists.

    Args:
        resolved: The document's resolved (absolute) path.
        cwd: The resolved working directory of the ``lint`` invocation.
        git_roots: The path's ancestor directories that hold a ``.git``
            entry (:func:`_git_ancestors`).

    Returns:
        The :class:`_Anchor` (its ``layout`` and ``rooted`` flag).
    """
    assert isinstance(resolved, Path), type(resolved)
    assert isinstance(cwd, Path), type(cwd)
    assert isinstance(git_roots, frozenset), type(git_roots)
    repo_roots = sorted(git_roots, key=lambda root: len(root.parts))
    candidates: list[Path] = []
    if resolved.is_relative_to(cwd) and (not repo_roots or any(cwd.is_relative_to(root) for root in repo_roots)):
        candidates.append(cwd)
    candidates.extend(root for root in repo_roots if root not in candidates)
    unrooted: _Anchor | None = None
    for candidate in candidates:
        parts = resolved.relative_to(candidate).parts
        if len(parts) < 3 or parts[0] != _DOCS_DIR_NAME:
            continue
        docs_dir = candidate / _DOCS_DIR_NAME
        if not any(root != docs_dir and root.is_relative_to(docs_dir) for root in repo_roots):
            result = _Anchor(layout=_anchor_layout(parts, 0), rooted=True)
            return result
        if unrooted is None:
            unrooted = _Anchor(layout=_anchor_layout(parts, 0), rooted=False)
    if unrooted is not None:
        result = unrooted
        return result
    parts = resolved.relative_to(repo_roots[0]).parts if repo_roots else resolved.parts
    for index in range(len(parts) - 3, -1, -1):
        if parts[index] == _DOCS_DIR_NAME:
            result = _Anchor(layout=_anchor_layout(parts, index), rooted=False)
            return result
    result = _Anchor(layout=None, rooted=False)
    return result


def _docs_anchor(path: Path, cwd: Path) -> _Anchor:
    """The path's docs anchor (see :func:`_anchor_rule` for the rule), computed once per path-mode path.

    The thin filesystem half of the rule: resolves the path and collects
    its repo roots (:func:`_git_ancestors`), then defers to the pure
    :func:`_anchor_rule`.

    Args:
        path: The document's path (as given; relative to the working
            directory or absolute).
        cwd: The resolved working directory, read ONCE per ``lint``
            invocation by the path-mode loop and passed down (feat-245
            Phase 200, I1).

    Returns:
        The :class:`_Anchor` (its ``layout`` and ``rooted`` flag).
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(cwd, Path), type(cwd)
    resolved = path.resolve()
    result = _anchor_rule(resolved, cwd, _git_ancestors(resolved))
    return result


def _sharded_shape(path: Path, reg: _RegistryBacked) -> tuple[str, str] | None:
    """The root-name-independent sharded shape ``<domain>/<lang>/<2-hex>/<file>.md`` (feat-245 Phase 180, G2).

    Matches the path's last four segments by SHAPE alone -- the domain
    name one of the registry's thirteen UUID domains, the language dir a
    shape-valid two-letter code, the shard dir exactly
    :data:`_SHARD_DIGITS` lowercase hex characters, a ``.md`` file --
    independent of what the docs root is NAMED (``specdocs/req/en/ab/
    x.md`` matches like ``docs/req/en/ab/x.md``): the root-name-
    independence principle of the Phase 160 D9 decision, extended to path
    mode.

    Args:
        path: The document's path.
        reg: The registry-backed names (the UUID-domain set).

    Returns:
        ``(domain, language)`` when the shape matches, ``None`` otherwise.
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    parts = path.parts
    if (
        len(parts) >= 4
        and path.suffix == ".md"
        and parts[-4] in reg.uuid_domains
        and _LANG_DIR_PATTERN.fullmatch(parts[-3]) is not None
        and _SHARD_DIR_PATTERN.fullmatch(parts[-2]) is not None
    ):
        result: tuple[str, str] | None = (parts[-4], parts[-3])
        return result
    result = None
    return result


def _is_valid_sharded_placement(inner: tuple[str, ...]) -> bool:
    """The single valid sharded placement (feat-245 REQ-006): exactly one shape-valid two-letter language dir
    plus one two-lowercase-hex shard dir between the domain dir and the file (``<lang>/<2-hex>/``).

    Args:
        inner: The docs anchor's inner directory segments.

    Returns:
        ``True`` for the valid placement, ``False`` for every misplaced depth.
    """
    assert isinstance(inner, tuple), type(inner)
    result = (
        len(inner) == 2
        and _LANG_DIR_PATTERN.fullmatch(inner[0]) is not None
        and _SHARD_DIR_PATTERN.fullmatch(inner[1]) is not None
    )
    return result


def _placement_defect(inner: tuple[str, ...]) -> str | None:
    """The placement defect of the docs anchor's inner segments (feat-245 REQ-006), or ``None`` for the valid shape.

    Args:
        inner: The docs anchor's inner directory segments (``()`` for a
            file directly in the domain dir).

    Returns:
        The defect kind, or ``None`` when the placement is valid.
    """
    assert isinstance(inner, tuple), type(inner)
    if len(inner) == 0:
        result: str | None = "missing language directory"
    elif len(inner) == 1:
        if _LANG_DIR_PATTERN.fullmatch(inner[0]) is not None:
            result = "missing shard directory"
        else:
            result = "missing (valid) language directory"
    elif len(inner) == 2:
        if _LANG_DIR_PATTERN.fullmatch(inner[0]) is None:
            result = "missing (valid) language directory"
        elif _SHARD_DIR_PATTERN.fullmatch(inner[1]) is None:
            result = "non-hex shard"
        else:
            result = None
    else:
        result = "deeper than one shard level"
    return result


def _correct_sharded_path(doc_type: str, inner: tuple[str, ...], file_name: str, doc_id: str | None) -> str:
    """The path a misplaced file SHOULD live at (feat-245 REQ-006): the sharded shape under the file's own domain.

    Concrete when the file name carries a canonical uuid (the shard is
    the uuid's first :data:`_SHARD_DIGITS` characters -- the same mirrored
    constant :data:`_SHARD_DIR_PATTERN` is derived from -- the file name kept
    verbatim), shape-level (the ``<2-hex-shard>`` placeholder)
    otherwise. The language is the misplaced path's own shape-valid
    language dir (a ``de/foo.md``-shaped miss keeps ``de``), or the
    default language when the path carries none.

    Args:
        doc_type: The registered UUID domain the file is anchored under.
        inner: The docs anchor's inner directory segments.
        file_name: The file's own name (kept verbatim).
        doc_id: The file-name-derived id (``None`` when the name
            carries no canonical uuid).

    Returns:
        The correct path (``docs/<type>/<lang>/<shard>/<file>.md``).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(inner, tuple), type(inner)
    assert isinstance(file_name, str), type(file_name)
    assert doc_id is None or isinstance(doc_id, str), type(doc_id)
    language = inner[0] if inner and _LANG_DIR_PATTERN.fullmatch(inner[0]) is not None else _DEFAULT_LANGUAGE
    if doc_id is None:
        result = f"docs/{doc_type}/{language}/{_SHARD_PLACEHOLDER}/{file_name}"
    else:
        result = f"docs/{doc_type}/{language}/{doc_id[:_SHARD_DIGITS]}/{file_name}"
    return result


def _layout_violation(doc_type: str, path: Path, anchor: _Anchor, reg: _RegistryBacked) -> _LayoutViolation | None:
    """The layout violation for a docs-anchored UUID-domain file (feat-245 REQ-006), or ``None`` when valid.

    Args:
        doc_type: The registered UUID domain the file is anchored under.
        path: The file's path (as given).
        anchor: The path's docs anchor (computed once per path, Phase 190, S1).
        reg: The registry-backed names.

    Returns:
        The violation (the defect kind plus the correct path), or
        ``None`` for the valid sharded placement.
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(anchor, _Anchor), type(anchor)
    assert isinstance(reg, _RegistryBacked), type(reg)
    layout = anchor.layout
    assert layout is not None and layout[0] == doc_type, (layout, doc_type)
    inner = layout[1]
    defect = _placement_defect(inner)
    if defect is None:
        result: _LayoutViolation | None = None
    else:
        result = _LayoutViolation(
            path=path,
            doc_type=doc_type,
            kind=defect,
            correct_path=_correct_sharded_path(doc_type, inner, path.name, _derive_id(doc_type, path, reg)),
        )
    return result


def _infer_type(path: Path, anchor: _Anchor, reg: _RegistryBacked) -> str | None:
    """The document type from the path layout ALONE (REQ-005).

    Four rules, in order: (1) the docs-anchored sharded valid shape
    ``docs/<type>/<lang>/<2-hex>/<file>.md`` (``type`` one of the
    thirteen UUID domains -- feat-245 Phase 120, REQ-006); a
    docs-anchored UUID-domain file that MISSES the sharded placement
    returns ``None`` here -- the gate's placement validator reports it
    as a layout violation (and a docs-anchored NON-domain file is
    skipped by the gate, both before this function decides the type,
    unless -- for an un-rooted anchor only -- a later rule matches);
    (2) the root-name-independent sharded shape ``<domain>/<lang>/
    <2-hex>/<file>.md`` by shape alone (:func:`_sharded_shape` --
    feat-245 Phase 180, G2: ``specdocs/req/en/ab/x.md`` is ``req``
    under a ``SPECMGR_DOCS_DIR`` root of any name); (3) the containing
    directory's name is a member of the registry's ``ALL_DOMAINS`` (a
    non-docs-anchored position, e.g. ``<base>/req/x.md``); (4) the path
    has the ``feat/<id>/README.md`` shape (see
    :func:`_is_feat_folder_shape`) -- unchanged for every position,
    docs-anchored ``feat`` included. Independent of every
    ``SPECMGR_*_DIR`` variable.

    Args:
        path: The document's path.
        anchor: The path's docs anchor (computed once per path, Phase 190, S1).
        reg: The registry-backed names (the domain membership sets, the
            ``feat`` domain name).

    Returns:
        The inferred type, or ``None`` when no rule matches (the
        unrecognized-layout case, or the misplaced-docs-domain case).
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(anchor, _Anchor), type(anchor)
    assert isinstance(reg, _RegistryBacked), type(reg)
    layout = anchor.layout
    if layout is not None and layout[0] in reg.uuid_domains:
        if _is_valid_sharded_placement(layout[1]):
            result: str | None = layout[0]
            return result
        result = None
        return result
    shape = _sharded_shape(path, reg)
    if shape is not None:
        result = shape[0]
        return result
    if path.parent.name in reg.all_domains:
        result = path.parent.name
        return result
    if _is_feat_folder_shape(path, reg):
        result = reg.feat
        return result
    result = None
    return result


def _base_dir_for(doc_type: str, reg: _RegistryBacked) -> Path:
    """The sweep base directory for the ``feat`` type (REQ-006: the registered resolver).

    Since Task 150.155, only ``feat``'s default sweep takes this path:
    the thirteen sharded domains' default sweep is the all-languages
    union of :func:`_all_languages_paths_for` instead (their registered
    ``base_dir`` adapter resolves the ``en/`` directory only, which
    would make the sweep language-blind again).

    Args:
        doc_type: The document type to sweep (``feat``).
        reg: The registry-backed names (the whole-body registry lookup).

    Returns:
        The type's registered base directory (reading its own
        ``SPECMGR_*_DIR`` env var with its own default).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = reg.whole_body_domain(doc_type).base_dir()
    return result


def _all_languages_paths_for(doc_type: str, reg: _RegistryBacked) -> Iterator[Path]:
    """The all-languages default sweep enumeration for one sharded type (Task 150.155).

    The domain-wide union: ``iter_doc_paths_all_languages`` over the
    domain's own base directory (``doc_domain_base_dir`` -- the
    ``docs/<type>/`` parent of every per-language directory), i.e. the
    sharded listing of ``en/`` plus the sharded listing of every other
    shape-valid ``{language}/`` directory under it. A variant document
    in any language directory is therefore linted by the ``--type T``/
    ``--all`` sweep exactly like its EN file (each sweep item parsed in
    its own language, derived position-relative to the domain's
    configured base -- root-name-independent, Phase 160, D9 -- see
    :func:`_sweep_parse_language`), and the union's own dedup semantics
    keep a single EN document counted exactly once (``en/`` is listed
    once, explicitly). Shard-only at the language
    level, like every other scan: a flat file directly inside a
    language directory is not part of the live listing (the placement
    gate remains path mode's job). ``feat`` (folder-per-document,
    single-language) never takes this path.

    Args:
        doc_type: The sharded document type to enumerate (one of the
            thirteen UUID domains).
        reg: The registry-backed names.

    Returns:
        The iterator over the type's document paths across every
        language directory (sorted by path; empty for a missing base
        directory).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = reg.iter_all_languages(reg.domain_base_dir(doc_type))
    return result


def _iter_paths_for(doc_type: str, base_dir: Path, reg: _RegistryBacked) -> Iterator[Path]:
    """The single-directory sweep path iterator for one type (Task 150.155).

    The whole-body domains' registered ``iter_paths`` adapter: the
    shared sharded ``*.md`` enumeration (``<base>/*/*.md`` under a
    language directory) for every domain other than ``feat``, the
    ``feat/<id>/README.md`` folder enumeration for ``feat``. Since
    Task 150.155 this is the sweep's enumeration for the ``--dir``
    override (which narrows a sharded domain's sweep to exactly that
    one directory's sharded listing) and for ``feat``'s default sweep
    (its registered base directory); the thirteen sharded domains'
    default sweep (no ``--dir``) is the all-languages union of
    :func:`_all_languages_paths_for` instead.

    Args:
        doc_type: The document type to enumerate.
        base_dir: The base directory to enumerate under (``--dir`` or the
            registered resolver's result).
        reg: The registry-backed names.

    Returns:
        The iterator over the type's document paths (sorted by name;
        empty for a missing base directory).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = reg.whole_body_domain(doc_type).iter_paths(base_dir)
    return result


def _parse_language(doc_type: str, path: Path, anchor: _Anchor, reg: _RegistryBacked) -> str | None:
    """The parse language for one PATH-MODE work item (feat-245 Phase 120; Phase 180, G2).

    Path mode ONLY since Phase 160, D9 (SWEEP work items use
    :func:`_sweep_parse_language` instead, position-relative to the
    configured domain base; the dispatch is :func:`_item_parse_language`).
    For the thirteen UUID domains: the shape-valid language dir the path
    sits in when it carries the valid sharded placement under its OWN
    ``docs/<domain>/`` anchor, else -- root-name-independent (Phase 180,
    G2, the D9 principle extended to path mode) -- the language dir of
    the root-name-independent sharded shape ``<domain>/<lang>/<2-hex>/
    <file>.md`` (:func:`_sharded_shape`) whose domain is the item's own
    type, so a ``specdocs/dec/de/ab/x.md`` variant parses with the ``de``
    table, also under ``--type dec`` (``en`` resolves to the canonical
    parse, byte-identical to ``None`` -- the shared table resolver treats
    the two the same). ``None`` otherwise: every ``feat`` item (no
    language dimension at all), a non-sharded position, and a ``--type``
    override whose value disagrees with the path's own domain segment.

    Args:
        doc_type: The item's resolved document type.
        path: The item's on-disk path.
        anchor: The item's docs anchor (computed once per path, Phase 190, S1).
        reg: The registry-backed names (the UUID-domain set).

    Returns:
        The parse language, or ``None`` for the canonical parse.
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(anchor, _Anchor), type(anchor)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if doc_type not in reg.uuid_domains:
        result: str | None = None
        return result
    layout = anchor.layout
    if layout is not None and layout[0] == doc_type and _is_valid_sharded_placement(layout[1]):
        result = layout[1][0]
        return result
    shape = _sharded_shape(path, reg)
    if shape is not None and shape[0] == doc_type:
        result = shape[1]
        return result
    result = None
    return result


def _sweep_parse_language(doc_type: str, path: Path, reg: _RegistryBacked) -> str | None:
    """The parse language for one SWEEP work item (Task 160.100, D9): POSITION-RELATIVE to the
    domain's configured base.

    ``language_for_doc_path`` over ``doc_domain_base_dir(doc_type)`` --
    the domain's own base directory under whatever the configured
    ``SPECMGR_DOCS_DIR`` root is NAMED (root-name-independent, like
    the path-mode derivation of :func:`_parse_language` since Phase 180,
    G2, which works from the path alone rather than the configured base):
    the path's first subdirectory under the domain base, a shape-valid
    two-letter code (``en`` resolves to the canonical parse via the
    shared table resolver, like ``None``), ``None`` for every other
    position (a ``--dir`` tree outside the configured base, a
    non-sharded position). ``feat`` (no language dimension at all) is
    always ``None``. This is what makes the sweep's unconditional
    contract -- a variant document is linted exactly like its EN file,
    in its own path-derived language -- hold under any docs root, not
    only a root literally named ``docs``.

    Args:
        doc_type: The item's resolved document type.
        path: The item's on-disk path.
        reg: The registry-backed names.

    Returns:
        The parse language, or ``None`` for the canonical parse.
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if doc_type == reg.feat:
        result: str | None = None
    else:
        result = reg.language_for_doc_path(reg.domain_base_dir(doc_type), path)
    return result


def _item_parse_language(item: _WorkItem, reg: _RegistryBacked) -> str | None:
    """The parse language for one work item, by its mode (Task 160.100, D9).

    Path-mode items take the docs-anchor / sharded-shape derivation
    (:func:`_parse_language` -- root-name-independent since Phase 180,
    G2); sweep items take the
    position-relative derivation (:func:`_sweep_parse_language`,
    root-name-independent).

    Args:
        item: The work item.
        reg: The registry-backed names.

    Returns:
        The parse language, or ``None`` for the canonical parse.
    """
    assert isinstance(item, _WorkItem), type(item)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if item.sweep:
        result: str | None = _sweep_parse_language(item.doc_type, item.path, reg)
    else:
        assert item.anchor is not None, item
        result = _parse_language(item.doc_type, item.path, item.anchor, reg)
    return result


def _parse_document(doc_type: str, text: str, language: str | None, reg: _RegistryBacked) -> None:
    """The model-level FULL parse of one document's exact text (REQ-003), in the item's own language.

    Every domain: the registry's own ``parse_text`` adapter (the domain's
    pure text parser -- no file I/O, no ``DocCache``, no ``list_<d>``,
    no MCP tool), handed the item's parse language as the parser's own
    ``language`` keyword (feat-245 Phase 120: ``None``/omitted or ``en``
    = the canonical parse, a table-closed language = the fence-aware
    heading-normalization pre-pass before the unchanged engine). The
    parsed document is discarded -- the gate only cares whether the parse
    raised.

    Args:
        doc_type: The document's resolved type.
        text: The complete file content, frontmatter and body together.
        language: The item's parse language (see
            :func:`_item_parse_language` -- the mode dispatch over the
            path-mode and sweep derivations); ``None`` = canonical.
        reg: The registry-backed names (the whole-body registry lookup).

    Raises:
        Exception:
            The domain's parse-failure channels (the caller catches
            ``_CAUGHT_EXCEPTIONS``), plus the table loader's actionable
            ``ValueError`` for a shape-valid language without a packaged
            heading-mapping table (the caller catches it as the no-table
            content error).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(text, str), type(text)
    assert language is None or isinstance(language, str), type(language)
    assert isinstance(reg, _RegistryBacked), type(reg)
    domain = reg.whole_body_domain(doc_type)
    if language is None:
        domain.parse_text(text)
    else:
        domain.parse_text(text, language=language)


def _derive_id(doc_type: str, path: Path, reg: _RegistryBacked) -> str | None:
    """The repair pointer's id, derived from the path alone (REQ-008).

    ``feat``: the folder name of the ``feat/<id>/README.md`` shape (the
    feature's own id). The UUID-shaped types: the canonical UUID embedded
    in the file name, printed lowercased -- ids are case-insensitive on
    read, and lowercase is the canonical form.

    Args:
        doc_type: The document's resolved type.
        path: The document's on-disk path.
        reg: The registry-backed names (the ``feat`` domain name).

    Returns:
        The derived id, or ``None`` when no id can be derived (the
        pointer falls back to ``/repair {type}``).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if doc_type == reg.feat:
        if _is_feat_folder_shape(path, reg):
            result: str | None = path.parent.name
            return result
        result = None
        return result
    match = _UUID_PATTERN.search(path.name)
    if match is None:
        result = None
    else:
        result = match.group(0).lower()
    return result


def _repair_pointer_line(doc_type: str, path: Path, reg: _RegistryBacked) -> str:
    """The repair-pointer line for one failing document (REQ-008).

    ``/repair {type} {id}`` with the path-derived id, falling back to
    ``/repair {type}`` when none can be derived. Shared by the parse-
    failure report and the layout-violation report (feat-245 Phase 120),
    so the two blocks can never drift apart.

    Args:
        doc_type: The document's resolved type.
        path: The document's on-disk path.
        reg: The registry-backed names (the ``feat`` domain name).

    Returns:
        The pointer line (indented to follow its failure line).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    doc_id = _derive_id(doc_type, path, reg)
    if doc_id is None:
        result = f"  repair via: /repair {doc_type}"
    else:
        result = f"  repair via: /repair {doc_type} {doc_id}"
    return result


def _repair_pointer(failure: _Failure, reg: _RegistryBacked) -> str:
    """The repair pointer for one failing document (REQ-008).

    ``/repair {type} {id}`` with the path-derived id, falling back to
    ``/repair {type}`` when none can be derived.

    Args:
        failure: The failing document.
        reg: The registry-backed names (the ``feat`` domain name).

    Returns:
        The pointer line (indented to follow its failure line).
    """
    assert isinstance(failure, _Failure), type(failure)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = _repair_pointer_line(failure.doc_type, failure.path, reg)
    return result


def _fail_usage(errors: list[str]) -> None:
    """Report usage/resolution errors (stderr, one line each) and exit 2.

    Args:
        errors: The usage-error messages (without the ``error: `` prefix).
    """
    assert isinstance(errors, list), type(errors)
    for error in errors:
        typer.echo(f"error: {error}", err=True)
    raise typer.Exit(EXIT_USAGE)


def lint(
    paths: Annotated[
        list[str] | None,
        typer.Argument(
            help="Document paths to lint (path mode). Each path's type is inferred from its layout "
            "unless --type is given (which overrides the parse); a docs/<type>/ file missing the sharded "
            "placement is a layout violation (exit 2, the correct path named); docs/<non-domain>/ files "
            "are skipped and counted; other unrecognized layouts are a usage error unless --skip-unrecognized "
            "is given. Linted regardless of any SPECMGR_*_DIR variable."
        ),
    ] = None,
    type: Annotated[  # pylint: disable=redefined-builtin  # type intentionally shadows the builtin: public CLI API
        str | None,
        typer.Option(
            "--type",
            help="The document type (one of the registered domains -- a plain value validated at "
            "run time, not a fixed choice list). With paths: overrides the per-path layout inference. "
            "Without paths: sweeps every document of that type -- for the sharded domains, every "
            "language directory (EN + every variant); --dir narrows the sweep to that one directory's "
            "sharded listing (feat: its registered base directory's folder listing).",
        ),
    ] = None,
    all: Annotated[  # pylint: disable=redefined-builtin  # all intentionally shadows the builtin: public CLI API
        bool,
        typer.Option(
            "--all",
            help="Sweep every registered document type (for the sharded domains, every language "
            "directory -- EN + every variant). Cannot be combined with explicit paths; "
            "exits 2 when nothing at all is discovered (a probable misconfiguration).",
        ),
    ] = False,
    dir: Annotated[  # pylint: disable=redefined-builtin  # dir intentionally shadows the builtin: public CLI API
        Path | None,
        typer.Option(
            "--dir",
            help="The directory to sweep instead of the default: narrows the sweep to exactly that one "
            "directory's sharded listing (for sharded domains, whose default sweep is the all-language "
            "directories; feat keeps its folder listing). Valid only with --type and without explicit "
            "paths: it applies to the --type sweep only.",
        ),
    ] = None,
    skip_unrecognized: Annotated[
        bool,
        typer.Option(
            "--skip-unrecognized",
            help="Skip (and count in the summary) paths whose layout matches no type, instead of a usage error.",
        ),
    ] = False,
) -> None:
    """Lint specmgr artifacts: the model-level full parse, every failure reported.

    Runs the document's own domain's model-level parser (REQ-003: full
    parses only, never the listing/cache path) over the given paths
    (path mode), every document of ``--type T`` (type sweep), or every
    registered type (``--all``). Reports every layout violation (the
    defect plus the correct path, feat-245 Phase 120) and every failing
    ``(path, error)`` pair with its repair pointer and one summary:
    ``summary: linted=N failed=N skipped=N layout=N``.

    Exit codes (REQ-008): ``0`` every document parsed (incl. a run where
    every path was skipped, and ``--type T`` against an empty or missing
    base directory); ``1`` at least one document failed to
    parse (or the ``mcp`` extra is missing); ``2`` usage or resolution
    error (see the module docstring for the full list) or at least one
    layout violation (a docs-anchored UUID-domain file missing the
    sharded placement -- it outranks a parse failure in the same run).
    """
    # Argument-shape usage errors first (registry-free, before any file
    # access): the alternative-mode guards (paths and the sweep flags are
    # alternative modes; the two sweep flags are alternatives of each
    # other too -- combining them would silently narrow a requested
    # full sweep, a worse failure for a gate than an error).
    shape_errors: list[str] = []
    if all and paths:
        shape_errors.append("explicit paths cannot be combined with --all")
    if all and type is not None:
        shape_errors.append("--type and --all are both sweep flags and cannot be combined")
    if dir is not None and type is None:
        shape_errors.append("--dir is only valid together with --type")
    if dir is not None and paths:
        shape_errors.append("--dir cannot be combined with explicit paths (it applies to the --type sweep only)")
    if not paths and type is None and not all:
        shape_errors.append("give one or more document paths, or --type T, or --all")
    if shape_errors:
        _fail_usage(shape_errors)

    # The registry-backed names (they require the mcp extra -- the
    # diagram/mcp.py missing-extra precedent).
    try:
        reg = _registry_backed()
    except ImportError as ex:
        typer.echo("You must install the `mcp` extra to use this command (`biz-dfch-specmgr[mcp]`).", err=True)
        raise typer.Exit(EXIT_LINT_FAILURE) from ex

    # --type is validated against the registry's own ALL_DOMAINS (derived,
    # never hand-listed; no Typer choices -- see the module docstring).
    if type is not None and type not in reg.all_domains:
        _fail_usage([f"unknown --type {type!r}; expected one of {', '.join(reg.all_domains)}"])

    # Path mode: resolve each explicit path (existence/readability is a
    # usage error; the layout inference runs on the path alone; a UTF-8
    # decode failure is a per-file parse failure). A docs-anchored UUID-
    # domain file that misses the sharded placement is a layout violation
    # (its own result class, exit 2, never parsed -- feat-245 Phase 120,
    # REQ-006); a docs-anchored NON-domain file is skipped and counted
    # (exit 0) -- the non-domain-dir behavior at every depth.
    items: list[_WorkItem] = []
    pre_failures: list[_Failure] = []
    layout_violations: list[_LayoutViolation] = []
    skipped = 0
    path_errors: list[str] = []
    # the working directory, resolved ONCE per invocation and passed down
    # to the docs-anchor rule (feat-245 Phase 200, I1)
    cwd = Path.cwd().resolve()
    for path_str in paths if paths is not None else []:
        path = Path(path_str)
        if not path.is_file():
            path_errors.append(f"{path_str}: no such file or not a regular file")
            continue
        doc_type: str | None = None
        # the docs anchor, computed ONCE per path and passed down
        # (feat-245 Phase 190, S1)
        anchor = _docs_anchor(path, cwd)
        if anchor.layout is not None:
            first, _inner = anchor.layout
            if first in reg.uuid_domains:
                violation = _layout_violation(first, path, anchor, reg)
                if violation is not None:
                    layout_violations.append(violation)
                    continue
                doc_type = first if type is None else type
            elif first not in reg.all_domains and (anchor.rooted or _infer_type(path, anchor, reg) is None):
                # The non-domain-dir skip: unconditional under a rooted
                # anchor; under an un-rooted anchor only when no other
                # inference rule matches (feat-245 Phase 180, E2).
                skipped += 1
                continue
        if doc_type is None:
            doc_type = type if type is not None else _infer_type(path, anchor, reg)
            if doc_type is None:
                if skip_unrecognized:
                    skipped += 1
                else:
                    path_errors.append(
                        f"{path_str}: unrecognized layout (expected the sharded shape docs/<type>/<lang>/"
                        "<2-hex>/<file>.md, a path under a directory named after a registered type, or "
                        "feat/<id>/README.md); use --type to override or --skip-unrecognized to skip"
                    )
                continue
        try:
            text = path.read_text(encoding=_ENCODING)
        except OSError as ex:
            path_errors.append(f"{path_str}: unreadable ({ex})")
            continue
        except UnicodeDecodeError as ex:
            pre_failures.append(_Failure(path, doc_type, f"not valid {_ENCODING}: {ex}"))
            continue
        items.append(_WorkItem(path, doc_type, text, sweep=False, anchor=anchor))
    if path_errors:
        _fail_usage(path_errors)

    # Sweep mode: --type T (no paths) or --all (the shape guards above
    # keep the two apart), over the --dir override or the default
    # enumeration: the all-languages union for the thirteen sharded
    # domains (Task 150.155), the registered base directory for feat.
    sweep_types: tuple[str, ...] = ()
    if all:
        sweep_types = reg.all_domains
    elif type is not None and not paths:
        sweep_types = (type,)
    for doc_type in sweep_types:
        if dir is not None:
            # --dir narrows the sweep to exactly that one directory's
            # sharded (feat: folder) listing -- a single language
            # directory for a sharded domain, never the whole-domain
            # union.
            for path in _iter_paths_for(doc_type, dir, reg):
                items.append(_WorkItem(path, doc_type, None, sweep=True))
        elif doc_type == reg.feat:
            for path in _iter_paths_for(doc_type, _base_dir_for(doc_type, reg), reg):
                items.append(_WorkItem(path, doc_type, None, sweep=True))
        else:
            # the domain-wide union of every language directory's
            # sharded listing (en/ + every variant language dir)
            for path in _all_languages_paths_for(doc_type, reg):
                items.append(_WorkItem(path, doc_type, None, sweep=True))

    # The --all zero-documents guard (a probable misconfiguration; a
    # single empty/missing --type base directory is NOT one). It fires
    # only when NOTHING was discovered.
    if all and not items:
        _fail_usage(["--all found zero documents in total (check the SPECMGR_*_DIR configuration)"])

    # Parse every work item (full model-level parse, REQ-003) in the
    # item's own language (by mode -- Task 160.100, D9: the docs-anchor
    # derivation for path-mode items, the position-relative derivation
    # for sweep items); per-file catch of the repo's existing
    # parse-failure channels, the
    # table loader's no-table ValueError (a shape-valid language dir
    # without a packaged heading table: the existing no-table CONTENT
    # error, exit 1 -- the placement is valid, so NOT a layout
    # violation), plus read/decode errors, so one bad file cannot abort
    # the report.
    parse_failures: list[_Failure] = []
    for item in items:
        text = item.text
        if text is None:
            try:
                text = item.path.read_text(encoding=_ENCODING)
            except OSError as ex:
                parse_failures.append(_Failure(item.path, item.doc_type, f"unreadable: {ex}"))
                continue
            except UnicodeDecodeError as ex:
                # the same per-file decode-failure text path mode prints
                # (Phase 160, I3: the two read-failure channels were
                # asymmetric before -- sweep said "unreadable" for a
                # UnicodeDecodeError, path mode said "not valid utf-8")
                parse_failures.append(_Failure(item.path, item.doc_type, f"not valid {_ENCODING}: {ex}"))
                continue
        language = _item_parse_language(item, reg)
        try:
            _parse_document(item.doc_type, text, language, reg)
        except reg.caught_exceptions as ex:
            parse_failures.append(_Failure(item.path, item.doc_type, str(ex)))
        except ValueError as ex:
            # the no-table content error (the table loader's actionable
            # ValueError -- feat-245 Phase 120, REQ-006)
            parse_failures.append(_Failure(item.path, item.doc_type, str(ex)))

    # Report: the layout violations first (each its own block: the defect
    # plus the correct path, then the file's own repair pointer), then
    # every failing (path, error) pair with its per-type repair pointer,
    # then the one summary per invocation.
    # Failure order: decode failures first (path mode), then parse failures in encounter order.
    failures = pre_failures + parse_failures
    for violation in layout_violations:
        typer.echo(
            f"✗ {violation.path} ({violation.doc_type}): layout violation: {violation.kind}; "
            f"correct path: {violation.correct_path}"
        )
        typer.echo(_repair_pointer_line(violation.doc_type, violation.path, reg))
    for failure in failures:
        typer.echo(f"✗ {failure.path} ({failure.doc_type}): {failure.error}")
        typer.echo(_repair_pointer(failure, reg))
    linted = len(items) + len(pre_failures)
    typer.echo(f"summary: linted={linted} failed={len(failures)} skipped={skipped} layout={len(layout_violations)}")
    if layout_violations:
        # the layout violation is the usage/resolution exit (2) and
        # outranks a parse failure in the same run (both are reported)
        raise typer.Exit(EXIT_USAGE)
    if failures:
        raise typer.Exit(EXIT_LINT_FAILURE)
    raise typer.Exit(EXIT_OK)
