# `biz.dfch.specmgr.gol.resources.gol_schema`

Resource: specmgr://gol/schema (Task 3.11, packaged data).

Reads GOL's generated JSON Schema from the packaged data copy
(``gol/data/gol_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/gol_schema.json`` directly -- the latter is only readable
from an editable/source checkout (``general.tools._doc_paths``'s own
docstring documents this), which would break for a real, non-editable
``pip install``. The packaged copy is kept in sync with
``docs/gol_schema.json`` by a dedicated pre-commit hook/CI step that runs
``specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data``
-- the same generator as ``docs/gol_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_gol_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. Mirrors
``prb.resources.prb_schema`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``gol/models/v1``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made for
the original precedent.

## Functions

### `gol_schema() -> 'dict[str, Any]'`

Return the parsed contents of GOL's packaged JSON Schema.

Reads the packaged copy (``gol/data/gol_schema.json``) fresh
on every call (no in-memory cache, consistent with every other
resource/tool in this codebase) but never regenerates it -- its
presence is guaranteed at build time (real package data, kept in sync
with ``docs/gol_schema.json`` by a dedicated pre-commit hook/CI step),
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
    If the packaged ``gol_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

