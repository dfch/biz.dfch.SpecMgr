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

The 2026-10-17 fix (feat-214-rel-invalid-diag Phase 140, E1) corrects a
false positive the pre-fix implementation introduced against its own rule:
a ``}`` line was silently skipped by the line grammar and never popped the
fragment stack, so a curly-opened ``package "X" {`` fragment that collected
a component declaration and was closed with the rule's OWN required close
(a ``}`` line — real-parser-accepted, verified against the pinned 1.2026.8)
was reported at the block boundary as "never closed with '}'" — an error in
BOTH modes and a factually wrong diagnosis (the close was present). A
``}`` line now closes (pops) the innermost curly-open fragment, with no
finding on the pop itself; the tripwire fires only on a named ``end
package`` close over a component-collecting fragment and on such a fragment
still open at a block boundary (where the diagnostic's "never closed"
wording is factually correct again). A ``}`` with no curly-open fragment
open (the curly ``component "TYPE" { … }`` domain groups and the ``skinparam
component { … }`` block — declarations/skinparam, not fragments) stays
silently accepted, exactly as before.

The 2026-10-18 fix (feat-214-rel-invalid-diag Phase 150, E1/E2/I1) corrects
the two tripwire firing sites the 2026-10-15 amendment froze WITHOUT a
parser verdict (the 2026-10-15 isolation matrix verified only the NAMED-
CLOSE shapes): a component-collecting ``package`` fragment UNCLOSED AT THE
BLOCK BOUNDARY (every open shape) and one closed by a BARE ``@end`` (every
open shape) are parser-ACCEPTED by the pinned 1.2026.8 (file- and
pipe-form, recorded in the feature plan's More Information matrix). The
block-boundary site is therefore a LENIENT finding — mirroring the generic
else branch: a warning in preflight, promoted to an error in standalone, a
content-conditional variant of the "unclosed fragment at EOF" lenient case;
the 2026-10-15 comment's claim that "the parser does not implicitly close
such a block into a valid diagram" was empirically false for these shapes.
The bare-``@end`` site emits the tripwire's own lenient finding (a
content-conditional variant of the "bare ``@end``" lenient case) instead of
the generic name-omission finding — whose hint would steer the author to
the parser-rejected named close. The NAMED-CLOSE site (an ``end package``
over a component declaration, both open shapes) STAYS an error in BOTH
modes — parser-rejected, re-verified 2026-10-18. The fix hint is split by
the CLOSE KIND (the firing site; axis corrected in Phase 160 — the
2026-10-18 open-shape split proved precise for only 2 of the 6 site ×
open-shape combinations, because the remedy depends on which close line
exists, not how the block opened; the open shape stays named in all three
sites' messages): named close — replace the ``end package`` close with a
``}`` line; unclosed at boundary — add the missing ``}`` line; bare
``@end`` close — replace the bare ``@end`` close with a ``}`` line; each
variant keeps the common tail "or convert the group to the ``component
"TYPE" { … }`` domain-group form" — the 2026-10-15 single hint's "an
unclosed block over component declarations is a parser syntax error"
clause was factually false for the accepted shapes.

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


### `_package_component_fix(close_kind: 'str') -> 'str'`

The tripwire fix hint, keyed by the close kind — the firing site (2026-10-18, I1; axis corrected in Phase 160).

The 2026-10-15 single hint conflated the remedies and was
factually false for the parser-accepted unclosed shapes (its "an
unclosed block over component declarations is a parser syntax error"
clause — the pinned 1.2026.8 accepts every unclosed-at-boundary
variant and the bare-``@end`` close, file- and pipe-form; the
reference-graph rulebook §7.1 Phase 150 note). The Phase 150 split
keyed the remedy on the recorded OPEN SHAPE — precise for only 2 of
the 6 site × open-shape combinations (a braceless open at the
named-close site has nothing missing to add: its block IS closed, by
the parser-rejected ``end package`` line; a curly open at the
block-boundary site has no ``end package`` line to replace). The
remedy depends on which CLOSE LINE exists at the firing site, so the
axis is the close kind (the open shape stays named in all three
sites' messages — no information lost):

- ``named-close`` — the ``end package`` close is parser-rejected:
  REPLACE it with a ``}`` line (→ one of the parser-verified
  ACCEPTED ``}``-close shapes, re-probed Phase 160, both open
  shapes, pipe-form rc=0).
- ``block-boundary`` — no close line exists (the parser closes the
  block implicitly): ADD the missing ``}`` line (→ the same
  verified shapes).
- ``bare-@end`` — the bare ``@end`` close is parser-accepted but
  names no fragment: REPLACE it with a ``}`` line (→ the same
  verified shapes).

``close_kind`` is the firing site's own vocabulary (``"named-close"``
/ ``"block-boundary"`` / ``"bare-@end"`` — the same strings the call
sites pass); every variant keeps the common tail naming the
curly-brace domain-group form the real parser accepts for a
component-diagram group holding component declarations.


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

