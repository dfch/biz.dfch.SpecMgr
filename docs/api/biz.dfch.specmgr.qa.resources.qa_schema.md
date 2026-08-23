# `biz.dfch.specmgr.qa.resources.qa_schema`

Resource: specmgr://qa/schema (Phase 4, Task 4.2).

Reads QA's generated JSON Schema from the packaged data copy
(``qa/data/qa_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)
rather than ``docs/qa_schema.json`` directly -- the latter is only readable
from an editable/source checkout, which would break for a real,
non-editable ``pip install``. The packaged copy is kept in sync with
``docs/qa_schema.json`` by a dedicated pre-commit hook/CI step that runs
``specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data``
-- the same generator as ``docs/qa_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in ``commands/schema.py``.
Deliberately does not import ``commands.schema.generate_qa_schema()``
(which would leak the ``cli`` extra's ``typer`` dependency into the ``mcp``
extra's import graph), nor regenerate the file on the fly -- this is a
plain, read-only read of a build-time-guaranteed file. 1:1 port of
``req.resources.req_schema``.

The resource's URI is deliberately unversioned (no ``/v2``) even though the
file it reads is a ``qa/models/v2``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made for
the original rationale, reused verbatim here.

## Functions

### `qa_schema() -> 'dict[str, Any]'`

Return the parsed contents of QA's packaged JSON Schema.

Reads the packaged copy (``qa/data/qa_schema.json``) fresh
on every call (no in-memory cache, consistent with every other
resource/tool in this codebase) but never regenerates it -- its
presence is guaranteed at build time (real package data, kept in sync
with ``docs/qa_schema.json`` by a dedicated pre-commit hook/CI step),
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
    If the packaged ``qa_schema.json`` is missing.
json.JSONDecodeError
    If the packaged file is not valid JSON.

