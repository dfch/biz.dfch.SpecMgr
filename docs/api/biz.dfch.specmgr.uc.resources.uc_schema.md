# `biz.dfch.specmgr.uc.resources.uc_schema`

Resource: specmgr://uc/schema (Task 3.1.4).

Reads UC's generated JSON Schema from the packaged data copy
(``uc/data/uc_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/uc_schema.json`` directly -- the latter is only readable
from an editable/source checkout, which would break for a real,
non-editable ``pip install``. The packaged copy is kept in sync with
``docs/uc_schema.json`` by a dedicated pre-commit hook/CI step that runs
``specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data`` --
the same generator as ``docs/uc_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_uc_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. Mirrors
``req.resources.req_schema``.

The resource's URI is deliberately unversioned (no ``/v2``) even though the
file it reads is a ``uc/models/v2``-derived artifact -- see
``req.resources.req_schema``'s own precedent.

## Functions

### `uc_schema() -> 'dict[str, Any]'`

Return the parsed contents of UC's packaged JSON Schema.

Reads the packaged copy (``uc/data/uc_schema.json``) fresh on every call
(no in-memory cache, consistent with every other resource/tool in this
codebase) but never regenerates it -- its presence is guaranteed at
build time (real package data, kept in sync with ``docs/uc_schema.json``
by a dedicated pre-commit hook/CI step), so a missing or corrupted file
is treated as a hard failure rather than defensively handled.

Returns
-------
dict[str, Any]
    The parsed JSON Schema document (top-level keys include
    ``$schema``, ``$comment``, ``$defs``, ``properties``, ...).

Raises
------
FileNotFoundError
    If the packaged ``uc_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

