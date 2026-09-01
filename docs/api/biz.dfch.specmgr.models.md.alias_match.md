# `biz.dfch.specmgr.models.md.alias_match`

Match a parsed heading's actual text against a class's declared `@alias`.

Encapsulates the comparison logic so `MarkdownSection.from_text` can assert
that the heading it just parsed is actually the one the class claims to
represent, instead of leaving `@alias`'s `_alias_metadata` as inert,
never-checked class data.

## Functions

### `describe_alias(cls: 'type') -> 'str'`

Return a human-readable description of `cls`'s effective `@alias` (REQ-003).

Mirrors `match_alias`'s own default/LITERAL/SPACE_SEPARATED/REGEX
handling, for use in error messages (alias mismatch, and the
missing-mandatory-section case of "expected ..., found no match") that
need to state what heading text was actually expected, not just a bare
class name.

Args:
    cls: A `MarkdownSection` subclass, possibly decorated with `@alias`.

Returns:
    `"heading '<literal text>'"` for `LITERAL` (or the no-`@alias`
    default/`SPACE_SEPARATED`, which both derive the same literal text
    from `cls.__name__`), or `"heading matching regex '<pattern>'"` for
    `REGEX`.


### `match_alias(cls: 'type', heading_text: 'str') -> 'bool'`

Return whether `heading_text` satisfies `cls`'s declared `@alias`.

A class with no `_alias_metadata` at all (no `@alias` decorator applied,
directly or inherited) defaults to `AliasType.SPACE_SEPARATED`'s own
derivation of `cls.__name__` -- equivalent to an implicit
`@alias(type=AliasType.SPACE_SEPARATED)` -- rather than accepting any
heading text (see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0; a
literal match against `cls.__name__` verbatim was v1.2.0/v1.3.0/v1.3.1's
incorrect specification of this same default, corrected in v1.4.0).
`@alias` is opt-in for *customizing* the comparison away from that
default (a literal value with different wording/casing/suffixes/
formatting, or a regex), not for enabling matching in the first place:
an undecorated `MarkdownSection` subclass is always checked against
something. A class whose heading text is data rather than a fixed
schema label (e.g. a document's own H1 title) should declare an
explicit `@alias(value=".+", type=AliasType.REGEX)` to accept any
non-empty heading text (v1.3.1) -- there is no separate opt-out of alias
matching for this case; the `SPACE_SEPARATED` default alone would still
pin such a title to a fixed, class-name-derived value.

Args:
    cls: A `MarkdownSection` subclass, possibly decorated with `@alias`.
    heading_text: The heading's actual inline content, as parsed by
        `MarkdownSection.from_text` (e.g. `t_mid.content.strip()`).

Returns:
    `True` if `heading_text` satisfies the effective `@alias` -- either
    the declared one, or the implicit `SPACE_SEPARATED`-derived default
    when none is declared -- under the applicable `AliasType`:
    - `LITERAL`: `heading_text` equals the declared value exactly
      (case-sensitive, no normalization).
    - `SPACE_SEPARATED`: `heading_text` equals `cls.__name__` converted
      via `space_separated_name`.
    - `REGEX`: `heading_text` fully matches the declared value as a
      regular expression pattern.
    `False` otherwise.


### `space_separated_name(class_name: 'str') -> 'str'`

Convert a PascalCase class name to space-separated title case.

E.g. `"GoalInContext"` -> `"Goal In Context"`, `"SectionLevel1"` ->
`"Section Level 1"`. This is `AliasType.SPACE_SEPARATED`'s
auto-derivation rule -- an explicit, opt-in alternative for a class
whose natural heading text differs from its bare class name (see
`match_alias`; this is no longer the fallback for a class with no
`@alias` metadata at all).

Args:
    class_name: A class's `__name__`, e.g. `"GoalInContext"`.

Returns:
    `class_name` with a space inserted before every non-leading
    uppercase letter, and at every letter<->digit boundary in either
    direction (e.g. `"SectionLevel1"` -> `"Section Level 1"`,
    `"Level1abc"` -> `"Level 1 abc"`). A run of consecutive digits
    (`"Level123"` -> `"Level 123"`) or consecutive uppercase letters is
    never split internally by this rule.

