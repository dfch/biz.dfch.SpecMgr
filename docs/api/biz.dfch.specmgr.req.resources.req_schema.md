# `biz.dfch.specmgr.req.resources.req_schema`

Resource: specmgr://req/schema (Task 3.5, packaged data since Task 3.8).

Reads REQ's generated JSON Schema from the packaged data copy
(``req/resources/data/req_schema.json``, via ``req._data.read_req_schema_text``)
rather than ``docs/req_schema.json`` directly -- the latter is only readable
from an editable/source checkout (``_paths.DOCS_DIR``'s own docstring
documents this), which would break for a real, non-editable ``pip install``.
The packaged copy is kept in sync with ``docs/req_schema.json`` by a
dedicated pre-commit hook/CI step that runs
``specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/resources/data``
-- the same generator as ``docs/req_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_req_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``req/models/v1``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made.

## Functions

### `req_schema() -> 'dict[str, Any]'`

Return the parsed contents of REQ's packaged JSON Schema.

Reads the packaged copy (``req/resources/data/req_schema.json``) fresh
on every call (no in-memory cache, consistent with every other
resource/tool in this codebase) but never regenerates it -- its
presence is guaranteed at build time (real package data, kept in sync
with ``docs/req_schema.json`` by a dedicated pre-commit hook/CI step),
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
    If the packaged ``req_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

