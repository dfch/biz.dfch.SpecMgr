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

"""``harness-bundle`` -- regenerate the packaged harness bundle from the repo-root ``.opencode/`` tree.

Like ``specmgr docs``/``specmgr adr-toc`` regenerate committed documentation
from the codebase, this command regenerates the single committed package-data
bundle from the repo layout -- read from the current working directory, so
the repo root must be the CWD (a missing ``.opencode/`` directory is a usage
error, exit 2, nothing written).

It enumerates every ``*.md`` file recursively under exactly
``.opencode/{agent,command,skill}/`` -- exact top-level directory-name
match, singular names (``skill/`` holds one subfolder per skill, the only
nested layout) -- and serializes them, sorted by their ``.opencode/``-relative
``path``, into ``src/biz/dfch/specmgr/general/data/general_harness_bundle.json``
under the repo root, of shape ``{"instructions": <module constant>, "files":
[{"path", "sha256", "content"}]}`` where ``content`` is the file's verbatim
text and ``sha256`` the hex digest of that text. The serialization is
``json.dumps(indent=2, ensure_ascii=False)`` plus a trailing newline and no
timestamps, so two runs over an unchanged tree are byte-identical.

The top-level ``instructions`` field is the module constant
:data:`INSTRUCTIONS` -- the complete agent-driven install protocol
(feat-167-mcp-lifecycle-commands-2 Phase 130, REQ-008). The bundle is served
verbatim by the ``specmgr://harness-bundle`` MCP resource (the ``rasci.py``
pattern over ``read_packaged_text("general", "harness_bundle", "json")``),
and the consumer of that resource is an agent session of some harness
(OpenCode, Claude Code, ...) that installs the files into its own
configuration root per the protocol -- there is deliberately no install CLI.

A stray ``*.md`` at the ``.opencode/`` top level or under a non-scoped
directory (``node_modules/``, a similarly-named directory such as the
former ``zZz-skill/``) warns on stderr and is never bundled. This module is
``[cli]``-only: no ``mcp`` import, no server import.

Run this after adding/removing/editing any bundled ``.opencode/`` markdown
file and commit the result -- the ``specmgr-harness-bundle`` pre-commit hook
and the CI parity check (Python 3.13, alongside the ``specmgr
docs``/``adr-toc``/``mcp-docs`` steps) fail on drift.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import typer

#: The exact top-level directory names under ``.opencode/`` whose markdown
#: files the bundle carries (singular names; exact match, nothing else
#: under ``.opencode/`` is bundled).
_SCOPED_DIRS = ("agent", "command", "skill")

#: The markdown extension the enumeration bundles.
_MD_SUFFIX = ".md"

#: The bundle's own path, relative to the repo root (the packaged-data
#: convention: ``general/data/general_harness_bundle.json``, read back by
#: the ``specmgr://harness-bundle`` resource via
#: ``read_packaged_text("general", "harness_bundle", "json")``).
_BUNDLE_RELPATH = Path("src") / "biz" / "dfch" / "specmgr" / "general" / "data" / "general_harness_bundle.json"

#: The harness bundle's top-level ``instructions`` field: the complete
#: agent-driven install protocol, emitted verbatim into every generated
#: bundle (feat-167-mcp-lifecycle-commands-2 Phase 130, REQ-008). The
#: audience is an agent session of the active harness that reads the
#: ``specmgr://harness-bundle`` resource; the text is imperative protocol
#: for that agent to follow, not a comment about it.
INSTRUCTIONS = """Install the specmgr harness files -- the agents, commands, and skills this bundle carries --
into the configuration root of the harness you are running in. This bundle is
self-contained: every file to install is an entry of this bundle's "files" array,
carrying its "path" (relative to the .opencode/ directory this bundle was generated
from), its "sha256", and its verbatim "content". Follow these steps for every entry,
in order.

1. Pick the harness configuration root using the harness's own configuration skill
   (for OpenCode: the customize-opencode skill). The root is either the
   project-level .opencode/ directory of the current project or the global
   ~/.config/opencode/ directory. Do not guess: apply your harness's own
   configuration rules, and ask the user if they are unclear.

2. For each entry of "files", compute the target path:
   - Start with <root>/<path> (for example <root>/agent/phase-orchestrator.md,
     <root>/command/refs.md, <root>/skill/specmgr-refs/SKILL.md).
   - If the root already contains a plural-variant of the first path segment
     (for example agents/ where <path> starts with agent/, or skills/ where it
     starts with skill/), use that existing plural-variant directory in the target
     instead, so no file is registered twice under both spellings.

3. Install the file at its target:
   - The target does not exist: create its parent directories and write "content"
     byte-exact. Never reformat, rewrap, re-encode, re-indent, or lint the content.
   - The target exists and its sha256 equals the entry's "sha256": skip the file;
     it is already up to date.
   - The target exists but differs: ask the user before overwriting it (for
     OpenCode: the question tool). Write "content" byte-exact only on approval;
     otherwise leave the file untouched and report it as failed.

4. After every write, re-read the file from disk and verify that its sha256 equals
   the entry's "sha256". A write that cannot be verified this way is a failure for
   that file, not a success.

5. When all entries are processed, report the outcome per file: installed, skipped,
   updated, or failed (with the reason).

6. Never read, write, or merge opencode.json (or any other harness configuration
   file). The MCP server configuration is the user's own setup, done per the
   specmgr README's "Add to OpenCode" section; this install only adds or updates
   the files listed in "files".
"""


def _scoped_markdown_files(opencode_dir: Path) -> list[Path]:
    """Every ``*.md`` file under the scoped top-level directories, sorted by bundle ``path``.

    Exact top-level directory-name match on :data:`_SCOPED_DIRS` (recursive
    beneath each); a scoped directory that does not exist contributes
    nothing. Sorting is by the ``.opencode/``-relative POSIX path string,
    which is the bundle's own ``path`` field.
    """
    files: list[Path] = []
    for name in _SCOPED_DIRS:
        scoped_dir = opencode_dir / name
        if not scoped_dir.is_dir():
            continue
        files.extend(path for path in scoped_dir.rglob(f"*{_MD_SUFFIX}") if path.is_file())
    result = sorted(files, key=lambda path: path.relative_to(opencode_dir).as_posix())
    return result


def _stray_markdown_warnings(opencode_dir: Path) -> list[str]:
    """One deterministic warning per stray markdown entry outside the bundled scope.

    A stray is a ``*.md`` file directly under ``.opencode/`` (top-level) or
    any ``*.md`` file under a direct subdirectory whose name is not one of
    the scoped directory names (``node_modules/``, a similarly-named
    directory such as the former ``zZz-skill/``); each non-scoped directory
    yields at most one warning (with its recursive markdown count), so the
    warning list stays bounded regardless of how large ``node_modules/``
    is. Strays are never bundled.
    """
    warnings: list[str] = []
    for entry in sorted(opencode_dir.iterdir(), key=lambda path: path.name):
        if entry.is_file():
            if entry.suffix == _MD_SUFFIX:
                warnings.append(
                    f".opencode/{entry.name}: stray markdown file at the .opencode/ top level; "
                    "outside the bundled scope (agent/, command/, skill/) and never bundled"
                )
        elif entry.is_dir() and entry.name not in _SCOPED_DIRS:
            count = len([path for path in entry.rglob(f"*{_MD_SUFFIX}") if path.is_file()])
            if count > 0:
                warnings.append(
                    f".opencode/{entry.name}/: {count} markdown file(s) under a directory outside the "
                    "bundled scope (agent/, command/, skill/); none of them are bundled"
                )
    result = warnings
    return result


def generate_bundle_text(opencode_dir: Path) -> str:
    """Serialize the harness bundle over ``opencode_dir``'s scoped markdown tree.

    Pure: reads the tree, writes nothing. The returned text is exactly what
    the command writes to disk -- ``json.dumps(indent=2, ensure_ascii=False)``
    plus a trailing newline, no timestamps -- so two calls over an unchanged
    tree are byte-identical.
    """
    files: list[dict[str, str]] = []
    for path in _scoped_markdown_files(opencode_dir):
        content = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        rel_path = path.relative_to(opencode_dir).as_posix()
        files.append({"path": rel_path, "sha256": digest, "content": content})
    payload: dict[str, Any] = {"instructions": INSTRUCTIONS, "files": files}
    result = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    return result


def harness_bundle() -> None:
    """Regenerate ``general/data/general_harness_bundle.json`` from the repo-root ``.opencode/`` tree.

    Reads the repo layout from the current working directory (which must be
    the repo root): enumerates every ``*.md`` under exactly
    ``.opencode/{agent,command,skill}/`` (sorted by ``.opencode/``-relative
    path), warns on stderr for every stray markdown file outside that scope
    (never bundled), and writes the deterministic bundle
    (``{"instructions", "files": [{"path", "sha256", "content"}]}``,
    ``json.dumps(indent=2, ensure_ascii=False)`` + trailing newline, no
    timestamps) to ``src/biz/dfch/specmgr/general/data/general_harness_bundle.json``
    under the repo root. A missing ``.opencode/`` directory is a usage
    error (exit 2, nothing written). Prints a summary line (file count,
    total bytes, output path). Run this after any change to a bundled
    ``.opencode/`` markdown file and commit the result (the
    ``specmgr-harness-bundle`` pre-commit hook and the CI parity check fail
    on drift).
    """
    repo_root = Path.cwd()
    opencode_dir = repo_root / ".opencode"
    if not opencode_dir.is_dir():
        typer.echo(
            f"error: {opencode_dir} not found -- `specmgr harness-bundle` reads the repo-root layout "
            "from the current working directory; run it from a checkout that carries the .opencode/ "
            "directory (nothing was written).",
            err=True,
        )
        raise typer.Exit(2)

    for warning in _stray_markdown_warnings(opencode_dir):
        typer.echo(f"⚠ {warning}", err=True)

    text = generate_bundle_text(opencode_dir)
    file_count = len(_scoped_markdown_files(opencode_dir))
    output_path = repo_root / _BUNDLE_RELPATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    byte_count = len(text.encode("utf-8"))
    typer.echo(f"✓ Wrote {file_count} harness file(s) ({byte_count} bytes) to {output_path}")
