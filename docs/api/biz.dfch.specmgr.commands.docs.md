# `biz.dfch.specmgr.commands.docs`

``docs`` -- regenerate ``docs/api/`` and ``docs/GENERATED.md`` from the codebase.

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

## Functions

### `_collect_all_modules(package_name: str) -> list[str]`

Recursively collect all module names in a package.


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


### `_generate_api_docs(api_dir: pathlib.Path, package: str) -> int`

Write one Markdown file per module of ``package`` under ``api_dir``, plus a README index.

Returns the number of module files written.


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


### `_stable_signature_str(func: Any) -> str | None`

Render ``func``'s signature as a string, stable across repeated runs and Python versions.

``str(inspect.signature(func))`` already includes the surrounding
parentheses. Two things make this otherwise non-reproducible, breaking
the pre-commit hook / CI drift check for ``docs/api/*.md``:

* Parameters annotated via ``Annotated[T, typer.Option(...)]`` (as every
  Typer command uses) render that metadata's default ``repr()``, which
  embeds the object's memory address -- different on every run.
* A type's qualified name can include a private submodule that varies by
  Python version (see ``_PRIVATE_SUBMODULE_RE`` above).


### `docs(output: Annotated[pathlib.Path | None, <typer.models.OptionInfo object>] = None) -> None`

Regenerate ``api/`` and ``GENERATED.md`` from the codebase.

Defaults to the repo's ``docs/`` directory so the pre-commit hook and CI
backstop (both run with no ``--output``) produce reproducible output for
an unchanged tree. Pass ``--output`` to write elsewhere instead, without
touching the real ``docs/`` tree. Run this after any structural change
and commit the result (see ``AGENTS.md``).


### `generate_generated_md() -> str`

Generate the full contents of ``docs/GENERATED.md``.


### `generate_module_reference() -> str`

Generate the 'Module Reference' section from first-line docstrings.

