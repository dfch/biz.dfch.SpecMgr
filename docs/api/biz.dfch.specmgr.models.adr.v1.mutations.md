# `biz.dfch.specmgr.models.adr.v1.mutations`

Structured edit operations on an :class:`Adr` (plan §4, §5, §8).

This is the model-layer half of the future MCP tool surface's
``update_section``/``option_*``/``set_status`` tools (plan §8): it implements
their semantics against an in-memory :class:`Adr`, deliberately excluding any
file I/O (reading/writing/finding a document by id) -- that belongs to a
future ``tools/`` package, not here. Every function here is pure: it takes an
:class:`Adr` and returns a *new* one (or, for read-only lookups, plain data),
never mutating its argument, so the tool layer's own "re-read, re-parse,
re-render, re-write" cycle around each call (plan §7's "source of truth is
the file on disk") stays simple and race-free.

Two error channels, mirroring :mod:`parser`'s split between structural and
field-value problems:

- :class:`AdrSectionError` -- ``update_section`` given a ``key`` that is not
  a whole-section field (e.g. ``"options"``, or a typo), or a deletion
  sentinel (blank string or the literal ``"REMOVE"``, case-insensitive)
  targeting a *mandatory* section (plan §4).
- :class:`AdrOptionNotFoundError` -- an ``option_*`` function given a
  ``full_title`` that does not match any current option.

Everything else -- a non-sentinel value that still fails a field's own
validator (e.g. a blank ``status`` after composing ``set_status``'s
"superseded by ..." string, though that specific case cannot actually occur)
-- surfaces as the normal ``pydantic.ValidationError`` from reconstructing
the affected model, exactly like ``parser.parse_adr`` (plan §7/§8's "one
schema-driven validate_adr check, shared identically between LLM tool calls
and human edits").

## Classes

### `AdrOptionNotFoundError`

No current option matches the given ``full_title`` (plan §5, §8).

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `AdrSectionError`

``update_section`` was given an unusable ``key`` or ``value``.

Raised both for a ``key`` that is not a whole-section field (``options``
or an unrecognized name) and for a deletion sentinel targeting a
mandatory section (plan §4) -- as opposed to ``pydantic.ValidationError``,
raised when a non-sentinel value fails the field's own validator.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_find_option(adr: 'Adr', full_title: 'str') -> 'AdrOption'`


### `_is_deletion_sentinel(value: 'str') -> 'bool'`

A blank/whitespace-only string or the literal ``"REMOVE"`` (plan §4).


### `option_create(adr: 'Adr', partial_title: 'str', value: 'str') -> 'tuple[Adr, str]'`

Append a new option (plan §5, §8).

``number`` is assigned as one past the current highest option number
(``0`` if there are none yet) -- monotonically increasing and never
reused, even across deletions, per plan §5.

Parameters
----------
adr:
    The document to update. Never mutated.
partial_title:
    The ``{title}`` portion after ``"Option {number}: "``.
value:
    The new option's content.

Returns
-------
tuple[Adr, str]
    The new document, and the assigned full title (e.g.
    ``"Option 3: A title"``).


### `option_delete(adr: 'Adr', full_title: 'str') -> 'tuple[Adr, list[str]]'`

Remove the option named ``full_title`` (plan §5, §8).

Does not renumber or reorder the remaining options -- deleting one
leaves a gap in the numbering (plan §5). Raises
:class:`AdrOptionNotFoundError` if no option matches; ``adr`` is left
untouched in that case.

Returns
-------
tuple[Adr, list[str]]
    The new document, and the remaining options' full titles, in their
    original order.


### `option_list(adr: 'Adr') -> 'list[str]'`

Full titles of every current option, in document order (plan §5, §8).


### `option_read(adr: 'Adr', full_title: 'str') -> 'str'`

The current content of the option named ``full_title`` (plan §8).

Raises :class:`AdrOptionNotFoundError` if no option matches.


### `option_update(adr: 'Adr', full_title: 'str', value: 'str') -> 'tuple[Adr, str]'`

Full-content replace of the option named ``full_title`` (plan §5, §8).

Raises :class:`AdrOptionNotFoundError` if no option matches; ``adr`` is
left untouched in that case.

Returns
-------
tuple[Adr, str]
    The new document, and the option's new content (i.e. ``value``).


### `set_status(adr: 'Adr', status: 'str', superseded_by: 'str | None' = None) -> 'Adr'`

Replace ``frontmatter.status`` (plan §8's narrow convenience wrapper).

Parameters
----------
adr:
    The document to update. Never mutated.
status:
    The new status. Ignored if ``superseded_by`` is given (superseded-by
    composes its own status string).
superseded_by:
    When given, ``status`` is composed as ``f"superseded by
    {superseded_by}"`` instead of using ``status`` verbatim.

Returns
-------
Adr
    A new instance with the status replaced.


### `update_section(adr: 'Adr', key: 'str', value: 'str') -> 'Adr'`

Replace one whole-section :class:`AdrBody` field (plan §4).

``value`` being a deletion sentinel (blank/whitespace-only, or the
literal ``"REMOVE"``, case-insensitively) clears the section -- unless
``key`` names a mandatory field (:data:`body.MANDATORY_SECTION_FIELDS`),
in which case this raises :class:`AdrSectionError` and leaves ``adr``
untouched, matching plan §4's "errors immediately and does not write".

Parameters
----------
adr:
    The document to update. Never mutated.
key:
    An :class:`AdrBody` field name, e.g. ``"decision_drivers"``.
    ``"options"`` is rejected -- use the ``option_*`` functions instead.
value:
    The new section text, or a deletion sentinel.

Returns
-------
Adr
    A new instance with the section replaced.

