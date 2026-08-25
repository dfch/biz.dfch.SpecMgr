# `biz.dfch.specmgr.rsk.resources.rsk_schema`

Resource: specmgr://rsk/schema (Task 3.10).

Reads RSK's generated JSON Schema from the packaged data copy
(``rsk/data/rsk_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/rsk_schema.json`` directly -- the latter is only readable
from an editable/source checkout (``_paths.DOCS_DIR``'s own docstring
documents this), which would break for a real, non-editable ``pip install``.
The packaged copy is kept in sync with ``docs/rsk_schema.json`` by a
dedicated pre-commit hook/CI step that runs
``specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data`` --
the same generator as ``docs/rsk_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_rsk_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. Mirrors
``req.resources.req_schema`` exactly.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``rsk/models/v1``-derived artifact -- see
``req.resources.req_schema``'s own precedent.

## Functions

### `rsk_schema() -> 'dict[str, Any]'`

Return the parsed contents of RSK's packaged JSON Schema.

Reads the packaged copy (``rsk/data/rsk_schema.json``) fresh
on every call (no in-memory cache, consistent with every other
resource/tool in this codebase) but never regenerates it -- its
presence is guaranteed at build time (real package data, kept in sync
with ``docs/rsk_schema.json`` by a dedicated pre-commit hook/CI step),
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
    If the packaged ``rsk_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

