# `biz.dfch.specmgr.sysrs.resources.sysrs_schema`

Resource: specmgr://sysrs/schema (Task 4.5, packaged data).

Reads SYSRS's generated JSON Schema from the packaged data copy
(``sysrs/data/sysrs_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/sysrs_schema.json`` directly -- the latter is only readable
from an editable/source checkout (``general.tools._doc_paths``'s own
docstring documents this), which would break for a real, non-editable
``pip install``. The packaged copy is kept in sync with
``docs/sysrs_schema.json`` by a dedicated pre-commit hook/CI step that runs
``specmgr schema --type sysrs --output-dir src/biz/dfch/specmgr/sysrs/data``
-- the same generator as ``docs/sysrs_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_sysrs_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. Mirrors
``sop.resources.sop_schema``/``vcr.resources.vcr_schema`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``sysrs/models/v1``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made for
the original precedent.

## Functions

### `sysrs_schema() -> 'dict[str, Any]'`

Return the parsed contents of SYSRS's packaged JSON Schema.

Reads the packaged copy (``sysrs/data/sysrs_schema.json``) fresh
on every call (no in-memory cache, consistent with every other
resource/tool in this codebase) but never regenerates it -- its
presence is guaranteed at build time (real package data, kept in sync
with ``docs/sysrs_schema.json`` by a dedicated pre-commit hook/CI step),
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
    If the packaged ``sysrs_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

