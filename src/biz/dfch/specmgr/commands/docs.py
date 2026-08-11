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

"""``docs`` -- regenerate ``docs/api/`` and ``docs/GENERATED.md`` from the codebase.

Defaults to writing into the repo's ``docs/`` directory, so pre-commit hook
and CI backstop invocations (no ``--output``) produce byte-identical output
for an unchanged tree. Pass ``--output`` to write elsewhere instead (e.g. a
scratch directory) without touching the real ``docs/`` tree. Writes two
things under the chosen base directory:

* ``api/*.md`` -- one Markdown API reference per module (plus a
  ``api/README.md`` index); the default ``docs/api/`` is committed to the
  repo so it browses directly on GitHub without a build step.
* ``GENERATED.md`` -- implemented-domain list, first-line module docstrings
  grouped by domain, and a test-file count; the machine-generated
  counterpart that ``AGENTS.md`` points to instead of embedding.

Run this after any structural change (new module, new domain, new test
file) and commit the result -- see ``AGENTS.md`` "Developer Commands".
"""

import ast
import importlib
import inspect
import pkgutil
import re
from pathlib import Path
from typing import Annotated, Any

import typer

# __file__ = src/biz/dfch/specmgr/commands/docs.py
_SRC_ROOT = Path(__file__).resolve().parent.parent  # src/biz/dfch/specmgr
_REPO_ROOT = _SRC_ROOT.parent.parent.parent.parent  # repo root
_DOCS_DIR = _REPO_ROOT / "docs"
_PACKAGE = "biz.dfch.specmgr"


# ---------------------------------------------------------------------------
# docs/GENERATED.md -- domain list, module docstrings, test-file count
# ---------------------------------------------------------------------------


def _extract_module_docstring(file_path: Path) -> str | None:
    """Extract the first docstring from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        return ast.get_docstring(tree)
    except (SyntaxError, OSError):
        return None


def _collect_module_docs_by_domain() -> dict[str, list[tuple[str, str]]]:
    """Collect first-line module docstrings, grouped by top-level domain package."""
    domain_modules: dict[str, list[tuple[str, str]]] = {}

    for py_file in sorted(_SRC_ROOT.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue

        docstring = _extract_module_docstring(py_file)
        if not docstring:
            continue

        rel_path = py_file.relative_to(_SRC_ROOT)
        parts = rel_path.parts
        if len(parts) > 1:
            domain = parts[0]
            first_line = docstring.split("\n")[0].strip()
            domain_modules.setdefault(domain, []).append((str(rel_path), first_line))

    return domain_modules


def _count_test_files() -> int:
    """Count ``test_*.py`` files under ``tests/`` -- static, no subprocess."""
    tests_dir = _REPO_ROOT / "tests"
    if not tests_dir.exists():
        return 0
    return len(list(tests_dir.rglob("test_*.py")))


def _list_domain_packages() -> dict[str, list[str]]:
    """List domain packages and their subpackages (``models/``, ``adr/``)."""
    result: dict[str, list[str]] = {}

    models_dir = _SRC_ROOT / "models"
    if models_dir.exists():
        models = [
            d.name
            for d in models_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_") and d.name != "__pycache__"
        ]
        if models:
            result["models"] = sorted(models)

    adr_dir = _SRC_ROOT / "adr"
    if adr_dir.exists():
        adr_subs = [
            d.name for d in adr_dir.iterdir() if d.is_dir() and not d.name.startswith("_") and d.name != "__pycache__"
        ]
        if adr_subs:
            result["adr_subpackages"] = sorted(adr_subs)

    return result


def _count_py_files(subdir: Path) -> int:
    """Count non-private, non-``__init__`` ``.py`` files directly under ``subdir``."""
    if not subdir.exists():
        return 0
    return len([f for f in subdir.glob("*.py") if not f.name.startswith("_") and f.name != "__init__.py"])


def _count_mcp_features() -> dict[str, int]:
    """Count MCP tools, resources, and prompt modules under ``adr/``."""
    return {
        "tools": _count_py_files(_SRC_ROOT / "adr" / "tools"),
        "resources": _count_py_files(_SRC_ROOT / "adr" / "resources"),
        "prompts": _count_py_files(_SRC_ROOT / "adr" / "prompts"),
    }


def generate_module_reference() -> str:
    """Generate the 'Module Reference' section from first-line docstrings."""
    domain_modules = _collect_module_docs_by_domain()

    lines = [
        "## Module Reference",
        "",
        "First-line docstrings from each module, organized by domain:",
        "",
    ]

    for domain in sorted(domain_modules.keys()):
        lines.append(f"**{domain}/**")
        lines.append("")
        for rel_path, first_line in domain_modules[domain]:
            lines.append(f"- `{rel_path}` — {first_line}")
        lines.append("")

    return "\n".join(lines)


def generate_generated_md() -> str:
    """Generate the full contents of ``docs/GENERATED.md``."""
    domains = _list_domain_packages()
    features = _count_mcp_features()
    test_count = _count_test_files()

    lines = [
        "# Generated Documentation",
        "",
        "Auto-generated by `specmgr docs` (source tree scan). Do not hand-edit --",
        "regenerate with `uv run --frozen specmgr docs` and commit the result.",
        "",
        "## Implemented Domains",
        "",
    ]

    if "models" in domains:
        lines.append(f"**Models** — schema definitions: {', '.join(domains['models'])}")
        lines.append("")

    if "adr_subpackages" in domains:
        lines.append(f"**ADR domain** — subpackages: {', '.join(domains['adr_subpackages'])}")
        if features["tools"] > 0:
            lines.append(f"  - {features['tools']} MCP tools")
        if features["resources"] > 0:
            lines.append(f"  - {features['resources']} MCP resources")
        if features["prompts"] > 0:
            lines.append(f"  - {features['prompts']} prompt modules")
        lines.append("")

    lines.append(generate_module_reference())

    lines.append("## Test Coverage")
    lines.append("")
    lines.append(f"**Test files**: {test_count}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# docs/api/*.md -- per-module Markdown API reference (+ README.md index)
# ---------------------------------------------------------------------------


def _collect_all_modules(package_name: str) -> list[str]:
    """Recursively collect all module names in a package."""
    modules = [package_name]
    try:
        package = importlib.import_module(package_name)
        if hasattr(package, "__path__"):
            for _importer, modname, _ispkg in pkgutil.walk_packages(
                path=package.__path__,
                prefix=package_name + ".",
            ):
                modules.append(modname)
    except (ImportError, AttributeError):
        pass
    return modules


def _get_module_doc(module: Any) -> str:
    """Extract module docstring."""
    return inspect.getdoc(module) or "No documentation available."


def _get_classes(module: Any) -> list[tuple[str, Any]]:
    """Get all classes defined (not merely imported) in a module."""
    return [
        (name, obj) for name, obj in inspect.getmembers(module, inspect.isclass) if obj.__module__ == module.__name__
    ]


def _get_functions(module: Any) -> list[tuple[str, Any]]:
    """Get all functions defined (not merely imported) in a module."""
    return [
        (name, obj) for name, obj in inspect.getmembers(module, inspect.isfunction) if obj.__module__ == module.__name__
    ]


_OBJECT_ADDRESS_RE = re.compile(r" at 0x[0-9a-fA-F]+")

# Collapses a single private submodule segment out of a qualified name, e.g.
# ``pathlib._local.Path`` -> ``pathlib.Path``. Needed because Python 3.13
# moved ``pathlib.Path`` to live in a private ``pathlib._local`` submodule
# (``Path.__module__ == "pathlib._local"``), while 3.11/3.12 report plain
# ``pathlib`` -- so an un-normalized signature for any ``Path``-typed
# parameter renders differently per interpreter, and the CI matrix
# (3.11/3.12/3.13) would flag its own byte-identical output as drift.
_PRIVATE_SUBMODULE_RE = re.compile(r"\b([A-Za-z_]\w*)\._[A-Za-z]\w*\.([A-Za-z_]\w*)\b")

# Normalizes absolute PosixPath/WindowsPath representations in signatures by replacing
# full absolute paths with just the final path component. This avoids CI drift when the
# same repo is cloned to different paths (e.g. /home/user/... vs /home/runner/...).
# Matches patterns like ``PosixPath('/home/user/src/biz.dfch.SpecMgr/src')`` and
# replaces them with ``PosixPath('/src')`` (just the innermost directory).
_ABSOLUTE_PATH_RE = re.compile(r"(PosixPath|WindowsPath|Path)\('([^']+)'\)", re.MULTILINE)


def _stable_signature_str(func: Any) -> str | None:
    """Render ``func``'s signature as a string, stable across repeated runs and Python versions.

    ``str(inspect.signature(func))`` already includes the surrounding
    parentheses. Three things make this otherwise non-reproducible, breaking
    the pre-commit hook / CI drift check for ``docs/api/*.md``:

    * Parameters annotated via ``Annotated[T, typer.Option(...)]`` (as every
      Typer command uses) render that metadata's default ``repr()``, which
      embeds the object's memory address -- different on every run.
    * A type's qualified name can include a private submodule that varies by
      Python version (see ``_PRIVATE_SUBMODULE_RE`` above).
    * Absolute paths in default ``Path`` parameters vary by checkout location
      (e.g. ``/home/user/...`` vs ``/home/runner/...`` in CI), so they are
      normalized to just the final path component (see ``_ABSOLUTE_PATH_RE``).
    """
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return None
    text = _OBJECT_ADDRESS_RE.sub("", str(sig))
    text = _PRIVATE_SUBMODULE_RE.sub(r"\1.\2", text)

    # Normalize absolute paths: extract just the innermost directory name
    # from patterns like PosixPath('/home/user/src/biz.dfch.SpecMgr/src')
    def normalize_path(match: Any) -> str:
        path_type = match.group(1)
        path_str = match.group(2)
        basename = Path(path_str).name
        return f"{path_type}('/{basename}')"

    text = _ABSOLUTE_PATH_RE.sub(normalize_path, text)
    return text


def _format_signature(func: Any) -> str:
    """Format a function signature, tolerating uninspectable callables."""
    sig = _stable_signature_str(func)
    return sig if sig is not None else "()"


def _generate_module_markdown(module_name: str) -> str | None:
    """Generate Markdown documentation for a single module, or ``None`` if unimportable."""
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None

    lines = [f"# `{module_name}`", "", _get_module_doc(module), ""]

    classes = _get_classes(module)
    if classes:
        lines.append("## Classes")
        lines.append("")
        for class_name, cls in classes:
            lines.append(f"### `{class_name}`")
            lines.append("")
            class_doc = inspect.getdoc(cls)
            if class_doc:
                lines.append(class_doc)
                lines.append("")

            methods = [
                (name, method) for name, method in inspect.getmembers(cls, inspect.ismethod) if not name.startswith("_")
            ]
            functions = [
                (name, func)
                for name, func in inspect.getmembers(cls)
                if callable(func) and not name.startswith("_") and not isinstance(func, type)
            ]

            if methods or functions:
                lines.append("**Methods:**")
                lines.append("")
                for method_name, method in methods + functions:
                    sig = _stable_signature_str(method)
                    if sig is None:
                        lines.append(f"- `{method_name}(...)`")
                        lines.append("")
                        continue
                    lines.append(f"- `{method_name}{sig}`")
                    method_doc = inspect.getdoc(method)
                    if method_doc:
                        for doc_line in method_doc.split("\n"):
                            lines.append(f"  {doc_line}" if doc_line.strip() else "")
                    lines.append("")
            lines.append("")

    functions = _get_functions(module)
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func_name, func in functions:
            lines.append(f"### `{func_name}{_format_signature(func)}`")
            lines.append("")
            func_doc = inspect.getdoc(func)
            if func_doc:
                lines.append(func_doc)
                lines.append("")
            lines.append("")

    return "\n".join(lines)


def _generate_api_docs(api_dir: Path, package: str) -> int:
    """Write one Markdown file per module of ``package`` under ``api_dir``, plus a README index.

    Returns the number of module files written.
    """
    api_dir.mkdir(parents=True, exist_ok=True)

    modules = _collect_all_modules(package)
    index_entries: list[tuple[str, str, str | None]] = []

    for module_name in sorted(modules):
        markdown = _generate_module_markdown(module_name)
        if markdown is None:
            continue
        filename = f"{module_name}.md"
        (api_dir / filename).write_text(markdown, encoding="utf-8")

        # Extract first-line docstring for the index
        try:
            module = importlib.import_module(module_name)
            module_doc = _get_module_doc(module)
            first_line = module_doc.split("\n")[0].strip() if module_doc else None
        except (ImportError, AttributeError):
            first_line = None

        index_entries.append((module_name, filename, first_line))

    if index_entries:
        index_lines = [
            "# API Documentation Index",
            "",
            f"Auto-generated API documentation for `{package}`.",
            "",
            "## Modules",
            "",
        ]

        domains: dict[str, list[tuple[str, str, str | None]]] = {}
        for module_name, filename, first_line in index_entries:
            parts = module_name.split(".")
            domain = parts[0] if len(parts) > 1 else "root"
            domains.setdefault(domain, []).append((module_name, filename, first_line))

        for domain in sorted(domains.keys()):
            if domain != "root":
                index_lines.append(f"### {domain.capitalize()}")
                index_lines.append("")
            for module_name, filename, first_line in sorted(domains[domain]):
                if first_line:
                    index_lines.append(f"- [`{module_name}`]({filename}) — {first_line}")
                else:
                    index_lines.append(f"- [`{module_name}`]({filename})")
            index_lines.append("")

        (api_dir / "README.md").write_text("\n".join(index_lines), encoding="utf-8")

    return len(index_entries)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def docs(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Base directory to write api/ and GENERATED.md into (default: docs/ at the repo root).",
        ),
    ] = None,
) -> None:
    """Regenerate ``api/`` and ``GENERATED.md`` from the codebase.

    Defaults to the repo's ``docs/`` directory so the pre-commit hook and CI
    backstop (both run with no ``--output``) produce reproducible output for
    an unchanged tree. Pass ``--output`` to write elsewhere instead, without
    touching the real ``docs/`` tree. Run this after any structural change
    and commit the result (see ``AGENTS.md``).
    """
    docs_dir = output if output is not None else _DOCS_DIR

    api_dir = docs_dir / "api"
    module_count = _generate_api_docs(api_dir, _PACKAGE)
    typer.echo(f"✓ Wrote {module_count} module file(s) to {api_dir}")

    generated_md_path = docs_dir / "GENERATED.md"
    generated_md_path.write_text(generate_generated_md(), encoding="utf-8")
    typer.echo(f"✓ Wrote {generated_md_path}")
