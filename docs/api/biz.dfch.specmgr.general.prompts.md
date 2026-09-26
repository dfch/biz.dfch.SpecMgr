# `biz.dfch.specmgr.general.prompts`

MCP prompt registrations that are not specific to any single document
domain (Various improvements, Task 0.21; repair: feat-150-mcp-lifecycle-
commands, Phase 1).

``compact_history`` guides rotating older ``### Recent Updates`` entries out
of any `.specmgr` feature folder's ``README.md`` into an optional sibling
``history.md``. ``repair`` (cross-cutting: takes ``type`` + an optional
``id``, ADR excluded) guides repairing a whole-body document that fails to
parse via a host-native raw read, a ``validate(full=True)`` loop, a raw
write-back, and a post-write ``get_<d>``/``list_<d>`` confirmation.
Domain-specific prompts (e.g. ``create_adr``/``refine``) live under their
own domain package instead. Import this package to register all general
prompts against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.general import prompts  # noqa: F401 (side-effects only)
