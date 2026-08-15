# `biz.dfch.specmgr.general.tools._packaged_data`

Generic, doc-type-agnostic access to packaged example/template/schema data
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

## Functions

### `packaged_data_path(type_name: 'str', kind: 'str', ext: 'str' = 'md') -> 'Traversable'`

Return the ``Traversable`` for ``{type_name}/data/{type_name}_{kind}.{ext}``.

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


### `read_packaged_text(type_name: 'str', kind: 'str', ext: 'str' = 'md') -> 'str'`

Return the packaged data file's full text content, verbatim.

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

