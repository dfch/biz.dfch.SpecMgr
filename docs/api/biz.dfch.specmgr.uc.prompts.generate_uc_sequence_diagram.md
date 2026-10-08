# `biz.dfch.specmgr.uc.prompts.generate_uc_sequence_diagram`

``@mcp.prompt()``: generate_uc_sequence_diagram (feat-185-uc-diagrams, Phase 120).

Returns instructional text -- not itself a tool call -- that guides an LLM
through the rulebook §3.8 agent flow for one use case's sequence diagram:
read the frozen rulebook ``specmgr://uc/plantuml`` first, build a
``TodoWrite`` plan, read the UC via ``get_uc`` (a ``ParseFailureResult``
stops the flow -- the document must be repaired first), apply the §2.11
Subfunction judgment (a ``Subfunction``-level UC gets its own diagram only
when it adds interactions beyond its user goal's), fetch the deterministic
skeleton via ``get_uc_sequence_skeleton``, attribute every ``UNATTRIBUTED``
marker by understanding the free text (pre-filled arrows are positional,
not semantic -- they may be corrected; the ``question`` tool MUST be used
whenever not confident), enforce the zero-marker rule, loop
``validate_plantuml`` until green at the highest available layer
(``source_state != ok`` with a source set => report ``reason``/``fix_hint``
and do not write; all unset => write with the
``' validated: structure-only`` header), write the ``.puml`` file
host-native at ``diagrams/uc/<id>.sequence.puml`` (no specmgr tool writes
``.puml``), and never commit.

The actual instructional text lives in its own packaged data file,
``uc/data/uc_generate_uc_sequence_diagram_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text`` -- the
same convention as ``create_uc``'s ``uc_create_instructions.md`` and
``general``'s ``repair``. Placeholders use ``string.Template`` (``$id``),
not ``str.format``, so the instructions file is free to use plain,
unescaped ``{...}`` braces of its own.

## Functions

### `generate_uc_sequence_diagram(id: 'str') -> 'str'`

Return the §3.8 agent-flow instructions for the use case ``id``.

Parameters
----------
id:
    The use case document's specmgr-assigned identifier (the diagram's
    ``diagrams/uc/<id>.sequence.puml`` file name derives from it).

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

Raises
------
ValueError
    ``id`` is blank/whitespace-only (pass a real id; the flow's own
    ``get_uc`` call enforces the well-formed shape).

