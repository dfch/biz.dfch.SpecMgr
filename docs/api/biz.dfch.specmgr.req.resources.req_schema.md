# `biz.dfch.specmgr.req.resources.req_schema`

Resource: specmgr://req/schema (Task 3.5).

Reads the already-persisted ``docs/req_schema.json`` directly from disk --
trusts the ``specmgr-schema`` pre-commit hook (and its CI step) to keep it
current, the same trust model ``adr-toc``'s ``docs/adr/README.md`` already
relies on. Deliberately does not import
``commands.schema.generate_req_schema()`` (which would leak the ``cli``
extra's ``typer`` dependency into the ``mcp`` extra's import graph), nor
regenerate the file on the fly -- this is a plain, read-only disk read.

The resource's URI is deliberately unversioned (no ``/v1``) even though the
file it reads is a ``req/models/v1``-derived artifact -- see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made.

## Functions

### `req_schema() -> 'dict[str, Any]'`

Return the parsed contents of ``docs/req_schema.json``.

Reads the file fresh on every call (no in-memory cache, consistent with
every other resource/tool in this codebase) but never regenerates it --
schema presence is guaranteed at build time by the ``specmgr-schema``
pre-commit hook and CI step, so a missing or corrupted file is treated
as a hard failure rather than defensively handled.

Returns
-------
dict[str, Any]
    The parsed JSON Schema document (top-level keys include
    ``$schema``, ``$comment``, ``$defs``, ``properties``, ...).

Raises
------
FileNotFoundError
    If ``docs/req_schema.json`` does not exist.
json.JSONDecodeError
    If the on-disk file is not valid JSON.

