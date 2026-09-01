# `biz.dfch.specmgr.commands.docs`

``docs`` -- regenerate ``docs/api/`` and ``docs/GENERATED.md`` from the codebase.

Defaults to writing into the repo's ``docs/`` directory, so pre-commit hook
and CI backstop invocations (no ``--output``) produce byte-identical output
for an unchanged tree. Pass ``--output`` to write elsewhere instead (e.g. a
scratch directory) without touching the real ``docs/`` tree. Writes two
things under the chosen base directory:

* ``api/*.md`` -- one Markdown API reference per module (plus a
  ``api/README.md`` index); the default ``docs/api/`` is committed to the
  repo so it browses directly on GitHub without a build step. Stale pages
  (modules that no longer exist in the source tree) are pruned after the
  current pages are written: every flat ``api/*.md`` file whose name is
  neither the ``README.md`` index nor a page written in this run is
  deleted. Pruning is skipped entirely whenever the run cannot be trusted
  to have written the full current set (see ``_generate_api_docs``).
* ``GENERATED.md`` -- implemented-domain list, first-line module docstrings
  grouped by domain, and a test-file count; the machine-generated
  counterpart that ``AGENTS.md`` points to instead of embedding.

Run this after any structural change (new module, new domain, new test
file) and commit the result -- see ``AGENTS.md`` "Developer Commands".

## Functions

### `_collect_all_modules(package_name: str) -> tuple[list[str], bool]`

Recursively collect all module names in a package.

Args:
    package_name: Dotted name of the package to walk.

Returns:
    ``(modules, complete)`` -- the collected module names (always
    including ``package_name`` itself) and a flag that is ``True`` only
    when the package import and the ``pkgutil.walk_packages`` walk both
    ran to completion. When either fails, the walk is aborted at the
    point of failure, the returned list is then partial, and
    ``complete`` is ``False``.


### `_collect_module_docs_by_domain() -> dict[str, list[tuple[str, str]]]`

Collect first-line module docstrings, grouped by top-level domain package.


### `_count_mcp_features() -> dict[str, int]`

Count MCP tools, resources, and prompt modules under ``adr/``.


### `_count_py_files(subdir: pathlib.Path) -> int`

Count non-private, non-``__init__`` ``.py`` files directly under ``subdir``.


### `_count_test_files() -> int`

Count ``test_*.py`` files under ``tests/`` -- static, no subprocess.


### `_extract_module_docstring(file_path: pathlib.Path) -> str | None`

Extract the first docstring from a Python file.


### `_format_signature(func: Any) -> str`

Format a function signature, tolerating uninspectable callables.


### `_generate_api_docs(api_dir: pathlib.Path, package: str) -> tuple[int, int]`

Write one Markdown file per module of ``package`` under ``api_dir``, plus a README index.

After the current pages are written, stale pages are pruned: every flat
``*.md`` file directly in ``api_dir`` whose name is neither the
``README.md`` index nor a filename written in this run is deleted.
Nested directories and files of any other type are never touched.
Pruning is skipped entirely (nothing is deleted, pruned count 0)
whenever the run cannot be trusted to have written the full current
set: zero pages written, any module failed to import mid-run, or
module collection was truncated before the walk completed.

Args:
    api_dir: Directory to write the module pages and index into.
    package: Dotted name of the package to document.

Returns:
    ``(written, pruned)`` -- the number of module files written and
    the number of stale pages pruned.


### `_generate_module_markdown(module_name: str) -> str | None`

Generate Markdown documentation for a single module, or ``None`` if unimportable.


### `_get_classes(module: Any) -> list[tuple[str, typing.Any]]`

Get all classes defined (not merely imported) in a module.


### `_get_functions(module: Any) -> list[tuple[str, typing.Any]]`

Get all functions defined (not merely imported) in a module.


### `_get_module_doc(module: Any) -> str`

Extract module docstring.


### `_list_domain_packages() -> dict[str, list[str]]`

List domain packages and their subpackages (``models/``, ``adr/``).


### `_pruning_was_skipped(module_count: int) -> bool`

Report whether the run that just wrote ``module_count`` pages must have skipped pruning.

``_generate_api_docs`` returns only ``(written, pruned)``, so the skip
state is re-derived here instead: the run was untrustworthy when module
collection was truncated, or when fewer pages were written than modules
were collected (a per-module import failure). Both checks are cheap --
every import has already been cached in ``sys.modules`` by the run
itself. A healthy run with nothing to prune passes both checks.


### `_stable_signature_str(func: Any) -> str | None`

Render ``func``'s signature as a string, stable across repeated runs and Python versions.

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


### `docs(output: Annotated[pathlib.Path | None, <typer.models.OptionInfo object>] = None) -> None`

Regenerate ``api/`` and ``GENERATED.md`` from the codebase.

Defaults to the repo's ``docs/`` directory so the pre-commit hook and CI
backstop (both run with no ``--output``) produce reproducible output for
an unchanged tree. Pass ``--output`` to write elsewhere instead, without
touching the real ``docs/`` tree. After the current pages are written,
stale ``api/*.md`` pages are pruned; the pruning count is echoed only
when non-zero, and a warning is echoed whenever pruning was skipped
because the run was untrustworthy (see ``_generate_api_docs``). Run this
after any structural change and commit the result (see ``AGENTS.md``).


### `generate_generated_md() -> str`

Generate the full contents of ``docs/GENERATED.md``.


### `generate_module_reference() -> str`

Generate the 'Module Reference' section from first-line docstrings.

