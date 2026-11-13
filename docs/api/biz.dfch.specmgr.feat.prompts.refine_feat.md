# `biz.dfch.specmgr.feat.prompts.refine_feat`

``@mcp.prompt()``: refine_feat (feat-167-mcp-lifecycle-commands-2, Phase 100).

Returns instructional text -- not itself a tool call -- that guides an
LLM through a pre-implementation plan-readiness review of an existing
Feature (FEAT) document, fully over the MCP-native path: reading the
plan via ``get_feat`` with ``raw=True`` (and ``raw=True, numbered=True``
for the edit coordinates -- never from a raw file read), assessing it
against the four readiness checklist areas (testable acceptance
criteria, phase ordering and dependencies, scope clarity, unresolved
decisions), asking the user which findings to apply via the ``question``
tool, applying each approved fix with the generic ``update`` tool with
``type="feat"`` (line-range replace preferred, so unchanged regions stay
byte-identical), and re-checking with the generic ``validate`` tool with
``type="feat"`` and ``full=True``. Host file tools are only a fallback
for hosts that cannot reach those specmgr tools.

Unlike every other domain in this codebase, ``id`` is a
``feat-NNN-slug`` (the containing folder's own name), not a UUID -- a
blank or malformed id fails fast with ``ValueError`` (the shared
``general.tools._path_safety.assert_feat_id`` guard, the same one every
``feat`` tool applies) before any packaged data is read.

This prompt only ever *narrates* the review-and-edit flow -- it never
calls ``get_feat``/``question``/``update``/``validate`` itself, exactly
like every other prompt in this codebase (see
``general.prompts.repair``'s own docstring for the same contract).
``refine_feat`` is distinct from the pre-existing, read-only
``feat-refiner`` OpenCode agent (which reports findings and never
edits): this prompt -- and the ``feat-planner`` subagent /
``/plan-feature`` command that carry the same workflow on OpenCode --
apply the user-approved fixes to the plan itself.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_refine_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``. Placeholders use
``string.Template`` (``$id``), not ``str.format``, so the instructions
file itself is free to use plain, unescaped ``{...}`` braces.

## Functions

### `refine_feat(id: 'str') -> 'str'`

Return instructional text for a plan-readiness review of the feature ``id``.

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
    ``get_feat``, ``question``, ``update``, or ``validate`` itself
    -- it only narrates that sequence for the LLM to carry out.

Raises
------
ValueError
    If ``id`` is a blank/whitespace-only string, or not a
    well-formed ``feat-NNN-slug`` folder name.

