# `biz.dfch.specmgr.plantuml.structure`

The two-mode PlantUML structure checker (rulebook §6) + the shared UNATTRIBUTED marker constant.

A line-oriented subset linter — **not** a grammar engine. It lints exactly the
subset of PlantUML the specmgr renderers emit (plus the agent's attributed
sequence files): ``@startuml``/``@enduml`` presence,
actor/participant/usecase/component declarations (quoted or bare labels,
``as`` aliases — a bare identifier or, since the 2026-10-10 amendment, a
bracketed ``[...]`` token recorded unbracketed — ``<<stereotypes>>``),
usecase associations (``-->``), package edges (``..>``), sequence messages
(``->``/``-->``/self), note blocks, the fragment stack (``alt``/``opt``/
``loop``/``group``/``box``/``rectangle``/``package`` with ``end``), quote
sanitisation (the ``#quot;`` convention), and ``'`` comment lines — including
UNATTRIBUTED-marker detection.

Each ``@startuml``…``@enduml`` block is an **independent linting unit**
(the 2026-10-08 amendment): the block-scoped state — the declaration table,
the undeclared-name dedup table, the fragment stack, and the note state —
resets at every block boundary (an ``@enduml``, a stray ``@enduml``, or the
next ``@startuml`` closing a block that is missing its ``@enduml``). A
lenient finding (e.g. an unclosed fragment) is attributed within the block it
belongs to, and lines outside any block (before the first ``@startuml``, or
between two blocks) carry no findings. The parser is authoritative for
multi-block files — it accepts them (verified against 1.2026.8, including
the missing-``@enduml``-then-next-``@startuml`` shape); the packaged shape
is a single block.

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
``@startuml`` is an error in **both** modes (the emitted subset always
starts with ``@startuml`` — the normative rule is the emitted-subset
contract, not the server's own behaviour for such payloads, which drifts
between builds: rulebook §5.2 drift note (a), re-probed 2026-10-06).
UNATTRIBUTED markers are warnings in both
modes (deliberate placeholders — syntactically ``'`` comments the real parser
accepts; the zero-marker rule is enforced by the agent flow, not here).

The 2026-10-15 tripwire amendment (feat-214-rel-invalid-diag, the reference-
graph rulebook §7.1): the ``never rejects what the parser accepts`` invariant
forbids false positives, not false negatives — and the demonstrated gap was a
false negative (the pre-amendment checker reported zero findings in both
modes over the parser-rejected braceless ``package "TYPE" … end package``
grouping of component declarations). The amendment is the reverse direction:
a ``package`` fragment that COLLECTS component declarations (a ``component``
keyword declaration line or a short-form ``[X]`` line) must close with a
``}`` line — a named ``end package`` close (after a braceless-open or a
curly-open) and an unclosed such fragment at a block boundary are errors in
BOTH modes, with a fix hint naming the curly-brace group form
(``component "TYPE" { … }``). The rule is content-conditional: ``package``
fragments holding sequence content (participants — the UC subset,
parser-verified in feat-185) collect no component declaration and stay
exactly as before.

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


### `_FragmentState`

One open fragment on the checker's line-oriented stack (internal state).

The 2026-10-15 tripwire amendment extends the pre-amendment
``(kind, open line)`` tuple with two recorded facts: :attr:`curly_open`
(the open line ends with ``{``) and :attr:`has_component` (the fragment
collected a component declaration — a ``component`` keyword line or a
short-form ``[X]`` line — since the open). Only ``package`` fragments are
subject to the tripwire; the fields are recorded for every fragment kind.

Attributes:
    kind: the fragment keyword (``alt``/``opt``/``loop``/``group``/
        ``box``/``rectangle``/``package``).
    open_line: the 1-based line of the fragment open.
    curly_open: ``True`` when the open line ends with ``{``.
    has_component: ``True`` once the fragment collected a component
        declaration (the tripwire's content condition).


## Functions

### `_declaration_parts(rest: 'str') -> 'tuple[str, str | None, str | None, list[Finding]]'`

Split a declaration's ``rest`` into (label, alias, stereotype_tail).

Returns the parts plus local findings (unbalanced quote / stereotype).
The label is the quoted substring's content or the bare token; the alias
only from an ``as <alias>`` (a bare identifier or, since the 2026-10-10
amendment, a bracketed ``[...]`` token — recorded unbracketed); a
trailing balanced ``<<…>>`` run is the stereotype tail — with or without
the alias in between (the 2026-10-08 amendment). A bracket shape that is
NOT the frozen one is an unbalanced ``<<stereotype>>`` error (the
negative control ``participant A <<user`` — the real parser answers it
400 — errors in both modes).


### `_declaration_parts_legacy(rest: 'str') -> 'tuple[str, str | None, str | None, list[Finding]]'`

The pre-2026-10-08 ``_declaration_parts`` walk, kept for the shapes the
frozen-form regexes above do not cover (byte-identical behavior for
every shape the legacy path handles).


### `_mark_component_fragment(fragments: 'list[_FragmentState]') -> 'None'`

Record a component declaration on the innermost open ``package`` fragment (internal state).

The 2026-10-15 tripwire's content condition: a component declaration
(a ``component`` keyword line or a short-form ``[X]`` line) marks the
nearest enclosing ``package`` fragment as component-collecting. A
declaration outside any ``package`` fragment (top-level, or inside a
non-package fragment) is a no-op — the tripwire is scoped to ``package``
fragments only (the reference-graph rulebook §7.1).


### `_strip_operand(token: 'str') -> 'str'`

Unwrap a quoted or fully-bracketed operand and undo the ``#quot;`` sanitisation.

The bracket unwrap (the 2026-10-10 amendment, rulebook §6.1) makes a
bracketed edge operand (e.g. ``[REQ-{uuid}]``) compare identically to the
unbracketed name a declaration's bracketed ``as`` alias records.


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

Detection is by the shared :data:`UNATTRIBUTED_MARKER_PREFIX` on a
comment line only — deliberately prefix-only, no tail-grammar
validation: a marker line is a comment and its tail is free text the
agent will replace, so strictness here would create false negatives for
nothing.


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

