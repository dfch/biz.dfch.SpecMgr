# `biz.dfch.specmgr.uc.tools.get_uc_sequence_skeleton`

``@mcp.tool()`` wrapper: get_uc_sequence_skeleton (feat-185-uc-diagrams, Phase 120).

Read-only, id-based diagram tool: renders one use case's deterministic
PlantUML sequence-diagram **skeleton** (rulebook ``specmgr://uc/plantuml``
§2.9 -- participants, the preconditions note, the trigger as virtual step 0
with receiver fixed to the system, the ordinal steps, the ``alt`` fragments,
the final notes, and every message the §2.9.3 attribution rule cannot
pre-fill as one of the three frozen ``UNATTRIBUTED`` marker lines). Thin
wrapper: the id resolution mirrors ``get_uc`` exactly (``_path_safety``-
guarded, cache-aware via ``load_by_id``; a truly-absent id raises the
domain's not-found error, an existing-but-broken document returns the
non-raising ``ParseFailureResult`` per the feat-150 precedent), and the
rendering is the pure ``uc.models.v2.renderer.render_uc_sequence_skeleton``
(Phase 110).

The skeleton is the deterministic starting point of the
``generate_uc_sequence_diagram`` prompt flow: the agent attributes the
``UNATTRIBUTED`` markers (and may correct any pre-filled arrow) and writes
the ``.puml`` file host-native -- no specmgr tool writes ``.puml``.

## Functions

### `get_uc_sequence_skeleton(id: 'str') -> 'str | ParseFailureResult'`

Render and return the sequence skeleton for the use case ``id``.

Parameters
----------
id:
    The use case document's specmgr-assigned identifier.

Returns
-------
str | ParseFailureResult
    The skeleton text (``@startuml ...`` through ``@enduml``, one
    trailing newline) -- byte-stable per the rulebook §2.9, carrying
    ``UNATTRIBUTED`` marker lines where the attribution rule cannot
    pre-fill a message. When the document exists but fails to parse, a
    :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
    (``error``/``path``/``id``) is returned instead of raising (the
    feat-150 precedent, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c).
    Raises :class:`._paths.UcNotFoundError` if no use case has this id.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not a well-formed id for this
    domain (raised before any filesystem access).

