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
(file path + parse error), not just the first (REQ-001). The whole-body
domains are parsed through the domain registry's own ``parse_text``
adapters (the ``<d>.models`` package's pure text parsers -- ``parse_req``,
``parse_uc``, ... -- no file I/O, no ``DocCache``, no ``list_<d>``, no MCP
tool), ADR through the top-level ``models.adr`` package's own ``parse_adr``.
The parse-failure channels are the repo's existing ones, imported rather
than re-listed: ``general.models.validate_result._CAUGHT_EXCEPTIONS``
(``AssertionError``, ``pydantic.ValidationError``, ``yaml.YAMLError``) plus
``AdrParseError`` (a ``ValueError`` subclass, the same also-catch the
``validate_adr`` tool uses) plus UTF-8 decode errors -- caught per file so
one bad file cannot abort the aggregate report. Full parses only, never
the listing path (REQ-003): the ``list_feat`` dirty stage (frontmatter+H1
only, ADR 3982712a) is precisely the masking that hid the feat-214 defect
for three consecutive commits.

Three scopes, so the cost scales with the size of a change and never with
the size of the corpus (REQ-004):

* **Path mode** -- explicit ``PATHS`` on the command line. Each path's
  type is inferred from the path layout ALONE (REQ-005: the containing
  directory is named after a type, as in ``docs/req/x.md``, or the path
  has the ``feat/<id>/README.md`` shape), independent of every
  ``SPECMGR_*_DIR`` variable. ``--type`` overrides inference; an
  unrecognized layout is a usage error (exit 2) unless
  ``--skip-unrecognized`` is given, in which case the path is skipped
  and counted.
* **Type sweep** -- ``--type T`` with no paths sweeps every document of
  that type from its base directory: the explicit ``--dir`` argument
  (valid with ``--type`` ONLY) if given, otherwise the domain's
  registered base-dir resolver (REQ-006). ``--type T`` against an empty
  or missing base directory exits 0 with a 0-document summary: a
  registered-but-empty domain is not a misconfiguration.
* **All sweep** -- ``--all`` sweeps every registered type. Explicit
  paths combined with ``--all`` is a usage error; ``--all`` that finds
  zero documents in total is a probable misconfiguration (exit 2).

The ADR README exclusion (REQ-007) is unconditional, in path mode and
sweep mode, with or without ``--skip-unrecognized``: a file is excluded
-- never parsed and never counted as a failure -- when its resolved type
is ``adr`` (inferred from the layout or given by ``--type adr``) and its
base name is ``README.md``, in whichever directory. It is type-specific:
``feat/<id>/README.md`` is a real feat artifact and is never excluded.

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
but this module no longer contributes to that. The one module-level
specmgr import is the ADR text parser
(``models.adr`` -- mcp-free by construction and verified import-safe;
the registry's ``--type`` acceptance set is deliberately NOT derived at
import time, so no Typer ``choices``).

Exit codes (pinned, REQ-008 -- the plantuml-check family):

* ``0`` -- every document parsed. Includes a run in which every given
  path was skipped or excluded (0-linted summary), and ``--type T``
  against an empty or missing base directory (0-document summary).
* ``1`` -- at least one document failed to parse, or the ``mcp`` extra
  is missing.
* ``2`` -- usage or resolution error: no paths and no sweep flag; an
  unreadable or missing path; an unrecognized layout without
  ``--skip-unrecognized``; ``--dir`` without ``--type``; explicit paths
  combined with ``--all``; an unknown ``--type``; ``--all`` that finds
  zero documents in total.

Report: every failing ``(path, error)`` pair is printed (the error is
the caught exception's own text, verbatim), each followed by its
per-type repair pointer: whole-body domains ``/repair {type} {id}`` with
the id derived from the path (the ``feat/<id>/README.md`` folder name
for ``feat``; the canonical UUID embedded in the file name for the
others, printed lowercased -- ids are case-insensitive on read and
lowercase is the canonical form), falling back to ``/repair {type}``
when no id can be derived; ADR -- which the repair flow does not cover
-- a line saying so, with the file to be fixed manually from the
reported error. One summary per invocation:
``summary: linted=N failed=N skipped=N excluded=N``, where ``linted`` is
the number of documents the gate took on (parse attempted) and ``failed``
the subset that failed to parse.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import typer

from ..models.adr import AdrParseError, parse_adr

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

#: The base name the feat folder shape and the ADR exclusion rule compare
#: against (the feat fixed filename, and the generated ADR table of
#: contents' name).
_README_BASENAME = "README.md"

#: A canonical (8-4-4-4-12 hex) UUID, searched for in a file name to
#: derive the repair pointer's id (ids are case-insensitive on read; the
#: match is printed lowercased -- the canonical form).
_UUID_PATTERN = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


@dataclass(frozen=True)
class _RegistryBacked:
    """The registry-backed names this module loads lazily (see :func:`_registry_backed`).

    Attributes:
        adr:
            The ``adr`` domain name (``general.tools._domains.ADR``).
        feat:
            The ``feat`` domain name (``general.tools._domains.FEAT``) --
            the one whole-body domain whose path shape is
            ``<base>/<id>/README.md``.
        all_domains:
            Every registered document type (``general.tools._domains.
            ALL_DOMAINS``: ``adr`` plus the whole-body domains) -- the
            ``--type`` acceptance set, derived, never hand-listed.
        whole_body_domain:
            The name -> ``WholeBodyDomain`` registry lookup (``general.
            tools._domains.whole_body_domain``) -- the source of each
            whole-body domain's ``base_dir``/``iter_paths``/``parse_text``
            adapters.
        caught_exceptions:
            The whole-body parse-failure channels (``general.models.
            validate_result._CAUGHT_EXCEPTIONS``: ``AssertionError``,
            ``pydantic.ValidationError``, ``yaml.YAMLError``).
        adr_base_dir:
            The ADR base-dir resolver (``adr.tools._paths.adr_base_dir``).
        iter_adr_paths:
            The ADR path iterator (``adr.tools._paths.iter_adr_paths`` --
            every ``*.md`` under the base directory, incl. the generated
            ``README.md`` table of contents, which the exclusion rule
            filters).
    """

    adr: str
    feat: str
    all_domains: tuple[str, ...]
    whole_body_domain: Callable[[str], Any]
    caught_exceptions: tuple[type[Exception], ...]
    adr_base_dir: Callable[[], Path]
    iter_adr_paths: Callable[[Path], Iterator[Path]]


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
    """

    path: Path
    doc_type: str
    text: str | None


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


def _registry_backed() -> _RegistryBacked:
    """The registry-backed names, imported lazily (they require the ``mcp`` extra).

    Every name below lives in a package whose import chain reaches
    ``server.py`` (the ``general``/``adr``/domain-package ``__init__``s
    eagerly import their ``tools``/``prompts`` sub-packages; the
    ``tools`` packages import the shared ``mcp`` application instance) --
    see the module docstring's Task 100.100 import-test finding. The
    caller catches the resulting ``ImportError`` as the missing-extra
    condition (exit 1).

    Returns:
        The :class:`_RegistryBacked` bundle of registry-backed names.
    """
    from ..adr.tools._paths import adr_base_dir, iter_adr_paths  # noqa: PLC0415
    from ..general.models.validate_result import _CAUGHT_EXCEPTIONS  # noqa: PLC0415
    from ..general.tools._domains import ADR, ALL_DOMAINS, FEAT, whole_body_domain  # noqa: PLC0415

    result = _RegistryBacked(
        adr=ADR,
        feat=FEAT,
        all_domains=ALL_DOMAINS,
        whole_body_domain=whole_body_domain,
        caught_exceptions=_CAUGHT_EXCEPTIONS,
        adr_base_dir=adr_base_dir,
        iter_adr_paths=iter_adr_paths,
    )
    return result


def _infer_type(path: Path, reg: _RegistryBacked) -> str | None:
    """The document type from the path layout ALONE (REQ-005).

    Two rules, in order: (1) the containing directory's name is a member
    of the registry's ``ALL_DOMAINS`` (e.g. ``docs/req/x.md``,
    ``docs/adr/x.md``); (2) the path has the ``feat/<id>/README.md``
    shape -- base name ``README.md`` with exactly one non-``README.md``
    path segment between a directory named after the ``feat`` domain and
    the file (e.g. ``.specmgr/feat/feat-1-x/README.md``). Independent of
    every ``SPECMGR_*_DIR`` variable.

    Args:
        path: The document's path.
        reg: The registry-backed names (the ``ALL_DOMAINS`` membership
            set, the ``feat`` domain name).

    Returns:
        The inferred type, or ``None`` when no rule matches (the
        unrecognized-layout case).
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if path.parent.name in reg.all_domains:
        result: str | None = path.parent.name
        return result
    if (
        path.name == _README_BASENAME
        and path.parent.name not in ("", _README_BASENAME)
        and path.parent.parent.name == reg.feat
    ):
        result = reg.feat
        return result
    result = None
    return result


def _is_excluded(doc_type: str, path: Path, reg: _RegistryBacked) -> bool:
    """The ADR README exclusion (REQ-007).

    A file is excluded when its resolved type is ``adr`` (inferred from
    the layout or given by ``--type adr``) and its base name is
    ``README.md``, in whichever directory. Unconditional (path mode and
    sweep mode, with or without ``--skip-unrecognized``); type-specific --
    ``feat/<id>/README.md`` (type ``feat``) is never excluded.

    Args:
        doc_type: The document's resolved type.
        path: The document's path.
        reg: The registry-backed names (the ``adr`` domain name).

    Returns:
        ``True`` when the file is excluded (never parsed, never failed).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(path, Path), type(path)
    assert isinstance(reg, _RegistryBacked), type(reg)
    result = doc_type == reg.adr and path.name == _README_BASENAME
    return result


def _base_dir_for(doc_type: str, reg: _RegistryBacked) -> Path:
    """The sweep base directory for one type (REQ-006: the registered resolver).

    Args:
        doc_type: The document type to sweep.
        reg: The registry-backed names (the ADR base-dir resolver, the
            whole-body registry lookup).

    Returns:
        The type's registered base directory (reading its own
        ``SPECMGR_*_DIR`` env var with its own default).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if doc_type == reg.adr:
        result: Path = reg.adr_base_dir()
        return result
    result = reg.whole_body_domain(doc_type).base_dir()
    return result


def _iter_paths_for(doc_type: str, base_dir: Path, reg: _RegistryBacked) -> Iterator[Path]:
    """The sweep path iterator for one type under a given base directory.

    The whole-body domains' registered ``iter_paths`` adapter (the shared
    flat-file ``*.md`` enumeration, the ``feat/<id>/README.md`` folder
    enumeration for ``feat``), the ADR ``*.md`` enumeration for ``adr``
    (which yields the generated ``README.md`` table of contents too --
    the exclusion rule filters it).

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
    if doc_type == reg.adr:
        result: Iterator[Path] = reg.iter_adr_paths(base_dir)
        return result
    result = reg.whole_body_domain(doc_type).iter_paths(base_dir)
    return result


def _parse_document(doc_type: str, text: str, reg: _RegistryBacked) -> None:
    """The model-level FULL parse of one document's exact text (REQ-003).

    Whole-body domains: the registry's own ``parse_text`` adapter (the
    domain's pure text parser -- no file I/O, no ``DocCache``, no
    ``list_<d>``, no MCP tool). ADR: the top-level ``models.adr``
    package's ``parse_adr``. The parsed document is discarded -- the gate
    only cares whether the parse raised.

    Args:
        doc_type: The document's resolved type.
        text: The complete file content, frontmatter and body together.
        reg: The registry-backed names (the whole-body registry lookup).

    Raises:
        Exception:
            The domain's parse-failure channels (the caller catches
            ``_CAUGHT_EXCEPTIONS`` plus ``AdrParseError``).
    """
    assert isinstance(doc_type, str), type(doc_type)
    assert isinstance(text, str), type(text)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if doc_type == reg.adr:
        parse_adr(text)
        return
    reg.whole_body_domain(doc_type).parse_text(text)


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
        if (
            path.name == _README_BASENAME
            and path.parent.name not in ("", _README_BASENAME)
            and path.parent.parent.name == reg.feat
        ):
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


def _repair_pointer(failure: _Failure, reg: _RegistryBacked) -> str:
    """The per-type repair pointer for one failing document (REQ-008).

    Whole-body domains: ``/repair {type} {id}`` with the path-derived id,
    falling back to ``/repair {type}`` when none can be derived. ADR: the
    repair flow is whole-body-only, so the pointer says ADR is not
    covered and the file is to be fixed manually from the reported error.

    Args:
        failure: The failing document.
        reg: The registry-backed names (the ``adr``/``feat`` domain
            names).

    Returns:
        The pointer line (indented to follow its failure line).
    """
    assert isinstance(failure, _Failure), type(failure)
    assert isinstance(reg, _RegistryBacked), type(reg)
    if failure.doc_type == reg.adr:
        result = "  ADR is not covered by the repair flow; fix the file manually from the error above."
        return result
    doc_id = _derive_id(failure.doc_type, failure.path, reg)
    if doc_id is None:
        result = f"  repair via: /repair {failure.doc_type}"
    else:
        result = f"  repair via: /repair {failure.doc_type} {doc_id}"
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
            "unless --type is given (which overrides); unrecognized layouts are a usage error unless "
            "--skip-unrecognized is given. Linted regardless of any SPECMGR_*_DIR variable."
        ),
    ] = None,
    type: Annotated[
        str | None,
        typer.Option(
            "--type",
            help="The document type (one of the registered domains -- a plain value validated at "
            "run time, not a fixed choice list). With paths: overrides the per-path layout inference. "
            "Without paths: sweeps every document of that type (from --dir if given, else the domain's "
            "registered base directory).",
        ),
    ] = None,  # pylint: disable=redefined-builtin  # type intentionally shadows the builtin: public CLI API
    all: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Sweep every registered document type. Cannot be combined with explicit paths; "
            "exits 2 when zero documents are found in total (a probable misconfiguration).",
        ),
    ] = False,  # pylint: disable=redefined-builtin  # all intentionally shadows the builtin: public CLI API
    dir: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="The base directory to sweep instead of the domain's registered one (valid with --type only)."
        ),
    ] = None,  # pylint: disable=redefined-builtin  # dir intentionally shadows the builtin: public CLI API
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
    registered type (``--all``). Reports every failing ``(path, error)``
    pair with its per-type repair pointer and one summary:
    ``summary: linted=N failed=N skipped=N excluded=N``.

    Exit codes (REQ-008): ``0`` every document parsed (incl. a run where
    every path was skipped or excluded, and ``--type T`` against an empty
    or missing base directory); ``1`` at least one document failed to
    parse (or the ``mcp`` extra is missing); ``2`` usage or resolution
    error (see the module docstring for the full list).
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
    # usage error; the layout inference and the exclusion run on the path
    # alone; a UTF-8 decode failure is a per-file parse failure).
    items: list[_WorkItem] = []
    pre_failures: list[_Failure] = []
    skipped = 0
    excluded = 0
    path_errors: list[str] = []
    for path_str in paths if paths is not None else []:
        path = Path(path_str)
        if not path.is_file():
            path_errors.append(f"{path_str}: no such file or not a regular file")
            continue
        doc_type = type if type is not None else _infer_type(path, reg)
        if doc_type is None:
            if skip_unrecognized:
                skipped += 1
            else:
                path_errors.append(
                    f"{path_str}: unrecognized layout (expected a path under a directory named after a "
                    "registered type, or feat/<id>/README.md); use --type to override or "
                    "--skip-unrecognized to skip"
                )
            continue
        if _is_excluded(doc_type, path, reg):
            excluded += 1
            continue
        try:
            text = path.read_text(encoding=_ENCODING)
        except OSError as ex:
            path_errors.append(f"{path_str}: unreadable ({ex})")
            continue
        except UnicodeDecodeError as ex:
            pre_failures.append(_Failure(path, doc_type, f"not valid {_ENCODING}: {ex}"))
            continue
        items.append(_WorkItem(path, doc_type, text))
    if path_errors:
        _fail_usage(path_errors)

    # Sweep mode: --type T (no paths) or --all (the shape guards above
    # keep the two apart), over the --dir override or each domain's
    # registered base directory; the ADR README exclusion applies here
    # too (iter_adr_paths yields the generated README.md).
    sweep_types: tuple[str, ...] = ()
    if all:
        sweep_types = reg.all_domains
    elif type is not None and not paths:
        sweep_types = (type,)
    for doc_type in sweep_types:
        base_dir = dir if dir is not None else _base_dir_for(doc_type, reg)
        for path in _iter_paths_for(doc_type, base_dir, reg):
            if _is_excluded(doc_type, path, reg):
                excluded += 1
                continue
            items.append(_WorkItem(path, doc_type, None))

    # The --all zero-documents guard (a probable misconfiguration; a
    # single empty/missing --type base directory is NOT one).
    if all and not items:
        _fail_usage(["--all found zero documents in total (check the SPECMGR_*_DIR configuration)"])

    # Parse every work item (full model-level parse, REQ-003); per-file
    # catch of the repo's existing parse-failure channels plus AdrParseError
    # plus read/decode errors, so one bad file cannot abort the report.
    parse_failures: list[_Failure] = []
    for item in items:
        text = item.text
        if text is None:
            try:
                text = item.path.read_text(encoding=_ENCODING)
            except (OSError, UnicodeDecodeError) as ex:
                parse_failures.append(_Failure(item.path, item.doc_type, f"unreadable: {ex}"))
                continue
        try:
            _parse_document(item.doc_type, text, reg)
        except (*reg.caught_exceptions, AdrParseError) as ex:
            parse_failures.append(_Failure(item.path, item.doc_type, str(ex)))

    # Report: every failing (path, error) pair with its per-type repair
    # pointer, then the one summary per invocation.
    failures = pre_failures + parse_failures
    for failure in failures:
        typer.echo(f"✗ {failure.path} ({failure.doc_type}): {failure.error}")
        typer.echo(_repair_pointer(failure, reg))
    linted = len(items) + len(pre_failures)
    typer.echo(f"summary: linted={linted} failed={len(failures)} skipped={skipped} excluded={excluded}")
    if failures:
        raise typer.Exit(EXIT_LINT_FAILURE)
    raise typer.Exit(EXIT_OK)
