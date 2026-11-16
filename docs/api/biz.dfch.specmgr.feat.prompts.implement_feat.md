# `biz.dfch.specmgr.feat.prompts.implement_feat`

``@mcp.prompt()``: implement_feat (feat-263-delegation-prompts, Phase 110).

Returns instructional text -- not itself a tool call -- that guides an
LLM through implementing an existing Feature (FEAT) plan, phase by
phase, under the orchestrator discipline the plan's own structure is
built for: reading the plan in full, building a phase-by-phase
``TodoWrite`` list, delegating each phase to a fresh subagent via the
host's task-delegation tool when available, independently verifying
each subagent's result BEFORE advancing (re-running the phase's quality
gate, inspecting the diff, confirming the phase's acceptance criteria),
and never writing or editing code files itself -- all implementation is
delegated.

The delegation is narrated as OPTIONAL, per DEC
4481b1fd-26e5-46bc-8f1b-236b638385b2 (the first exercise of the
portable-prompt-narrates-optional-delegation pattern): the text refers
to "your host's task-delegation tool, if one exists" -- never assuming
the tool is present -- and always carries the explicit fallback to
direct single-session implementation, phase by phase, when no such tool
exists (never a hard failure). After the plan's final verification
phase (the feature at ``review``, not yet ``done``), the narration
describes the capped review-fix loop: run the reviewer, resolve any
``[NEEDS DECISION]`` items with the user via ``question``, delegate the
reviewer's proposed fix phase to one more subagent cycle (the
implementer appends the ready-to-paste block to the plan's Task List,
since the orchestrator cannot edit files), and repeat until no
Errors/Gaps/Discrepancies remain -- capped at 3 review-fix cycles, the
``done`` closeout only after a clean loop exit.

Unlike every other domain in this codebase, ``id`` is a
``feat-NNN-slug`` (the containing folder's own name), not a UUID -- a
blank or malformed id fails fast with ``ValueError`` (the shared
``general.tools._path_safety.assert_feat_id`` guard, the same one every
``feat`` tool applies) before any packaged data is read.

This prompt only ever *narrates* the implement-and-verify flow -- it
never calls ``get_feat``/``question``/``set_status`` itself, exactly
like every other prompt in this codebase (see
``general.prompts.repair``'s own docstring for the same contract).
``implement_feat`` is the portable counterpart of the OpenCode-native
``phase-orchestrator`` agent (``.opencode/agent/phase-orchestrator.md``)
and the ``/implement-feature`` command
(``.opencode/command/implement-feature.md``), which carry the same
workflow with real file and tool access.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_implement_instructions.md``, read fresh on every call
via ``general.tools._packaged_data.read_packaged_text``. Placeholders
use ``string.Template`` (``$id``), not ``str.format``, so the
instructions file itself is free to use plain, unescaped ``{...}``
braces.

## Functions

### `implement_feat(id: 'str') -> 'str'`

Return instructional text for implementing the feature plan ``id``.

Parameters
----------
id:
    The feature's ``feat-NNN-slug`` identifier (the containing
    folder's own name, e.g. ``feat-36-delete``).

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call. This function never calls
    ``get_feat``, ``question``, or ``set_status`` itself -- it only
    narrates that sequence for the LLM to carry out.

Raises
------
ValueError
    If ``id`` is a blank/whitespace-only string, or not a
    well-formed ``feat-NNN-slug`` folder name.

