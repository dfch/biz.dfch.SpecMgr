# `biz.dfch.specmgr.general.prompts`

MCP prompt registrations that are not specific to any single document
domain (Various improvements, Task 0.21).

``compact_history`` guides rotating older ``### Recent Updates`` entries out
of any `.specmgr` feature folder's ``README.md`` into an optional sibling
``history.md``. Domain-specific prompts (e.g. ``create_adr``/``refine``)
live under their own domain package instead. Import this package to
register all general prompts against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.general import prompts  # noqa: F401 (side-effects only)
