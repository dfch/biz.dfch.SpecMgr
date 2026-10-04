# `biz.dfch.specmgr.plantuml.structure`

The two-mode PlantUML structure checker (rulebook §6) + the shared UNATTRIBUTED marker constant.

A line-oriented subset linter — **not** a grammar engine. It lints exactly the
subset of PlantUML the specmgr renderers emit (plus the agent's attributed
sequence files): ``@startuml``/``@enduml`` presence, actor/participant/usecase
declarations (quoted or bare labels, ``as`` aliases, ``<<stereotypes>>``),
usecase associations (``-->``), package edges (``..>``), sequence messages
(``->``/``-->``/self), note blocks, the fragment stack (``alt``/``opt``/
``loop``/``group``/``box``/``rectangle``/``package`` with ``end``), quote
sanitisation (the ``#quot;`` convention), and ``'`` comment lines — including
UNATTRIBUTED-marker detection.

Every finding carries a **1-based line number + cause + fix hint** (the
feat-27 actionable-error convention). Findings split into ``errors`` and
``warnings`` by mode:

- :data:`MODE_PREFLIGHT` — an authoritative validation source is available:
  the verified parser-lenient set (:data:`_LENIENT` findings) is reported as
  warnings (non-blocking).
- :data:`MODE_STANDALONE` — no source is configured: the same set is promoted
  to errors.

The checker **never rejects what the real parser accepts**: every lenient case
was verified to render OK against the real parser (rulebook §6.4 — the exact
five: unclosed fragment at EOF, missing ``@enduml``, bare ``@end``, dangling
arrow, undeclared participant in a sequence message). A missing
``@startuml`` is an error in **both** modes (the server classifies such
payloads as nothing-extractable). UNATTRIBUTED markers are warnings in both
modes (deliberate placeholders — syntactically ``'`` comments the real parser
accepts; the zero-marker rule is enforced by the agent flow, not here).

Import-free and stdlib-only (ADR 7a626b12): no specmgr imports. The
UNATTRIBUTED marker prefix lives here as ONE shared constant used by both the
renderer (``uc/models/v2/renderer.py``) and this checker, so the two cannot
drift (rulebook §2.9.4).

## Classes

### `Finding`

One actionable checker finding (feat-27 convention: line + cause + fix hint).

Attributes:
    line: 1-based line number in the checked source.
    message: the cause, plain and direct.
    fix_hint: the concrete fix for the author/agent.


### `StructureCheckResult`

The outcome of :func:`check_structure`.

Attributes:
    ok: ``True`` when :attr:`errors` is empty (warnings never block).
    errors: the blocking findings (mode-dependent for the lenient set).
    warnings: the non-blocking findings (both modes for UNATTRIBUTED
        markers and raw-quote notices; the lenient set in preflight).


## Functions

### `_declaration_parts(rest: 'str') -> 'tuple[str, str | None, str | None, list[Finding]]'`

Split a declaration's ``rest`` into (label, alias, stereotype_tail).

Returns the parts plus local findings (unbalanced quote / stereotype).
The label is the quoted substring's content or the bare run up to
`` as ``/`` <<``; the alias only from a trailing ``as <ident>``.


### `_strip_operand(token: 'str') -> 'str'`

Unwrap a quoted operand and undo the ``#quot;`` sanitisation.


### `check_structure(text: 'str', mode: 'str' = 'standalone') -> 'StructureCheckResult'`

Lint ``text`` as the emitted PlantUML subset (rulebook §6).

Parameters
----------
text:
    The full diagram source (one or more ``@startuml`` ... ``@enduml``
    blocks; the packaged shape is a single block).
mode:
    :data:`MODE_PREFLIGHT` (lenient set = warnings) or
    :data:`MODE_STANDALONE` (lenient set = errors). See the module
    docstring for the contract.

Returns
-------
StructureCheckResult
    ``ok`` plus the ``errors``/``warnings`` findings (1-based line +
    cause + fix hint each). Never raises on diagram content.


### `is_unattributed_marker(line: 'str') -> 'bool'`

Return ``True`` if ``line`` is an UNATTRIBUTED marker comment line.

Detection is by the shared :data:`UNATTRIBUTED_MARKER_PREFIX` plus the
frozen grammar tail (one of the three forms); a comment line carrying the
prefix but a malformed tail still matches (the checker warns on any
``' UNATTRIBUTED ``-led line — the agent flow owns the zero-marker rule).


### `unattributed_ext_marker(extension_ref: 'str', item: 'int', text: 'str') -> 'str'`

Build the extension-item marker form: ``' UNATTRIBUTED ext {N}{a} step {M}: <text>``.

``extension_ref`` is the extension's anchored reference with its optional
letter concatenated (e.g. ``"3a"``); ``item`` the 1-based item ordinal
within the extension; ``text`` as in :func:`unattributed_step_marker`.


### `unattributed_step_marker(step: 'int', text: 'str') -> 'str'`

Build the main-step marker form: ``' UNATTRIBUTED step {N}: <text>``.

``step`` is the 1-based step ordinal; ``text`` the message text
(single-line-escaped by the caller per rulebook §2.4 — a marker is one
PlantUML line).


### `unattributed_trigger_marker(text: 'str') -> 'str'`

Build the trigger marker form: ``' UNATTRIBUTED trigger: <text>``.

