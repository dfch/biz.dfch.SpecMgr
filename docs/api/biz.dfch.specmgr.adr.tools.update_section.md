# `biz.dfch.specmgr.adr.tools.update_section`

``@mcp.tool()`` wrapper: update_section (plan §4, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over
``models.adr.v1.mutations.update_section``: re-reads and re-parses the
current on-disk state, then re-renders and re-writes the full file; there
is no in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md``
file itself is always the source of truth. The whole sequence runs
under ``_lock.adr_lock(id)`` so a concurrent mutation against the same
id cannot interleave with it and cause a lost update.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `update_section(id: 'str', key: 'str', value: 'str') -> 'Adr'`

Replace (or, via a deletion sentinel, clear) one whole-section field.

Delegates to ``models.adr.v1.mutations.update_section`` (plan §4):
``value`` being blank/whitespace-only or the literal ``"REMOVE"``
(case-insensitive) clears the section, unless ``key`` names a
mandatory field, in which case ``AdrSectionError`` is raised and
nothing is written. Lets ``AdrSectionError``/``pydantic.ValidationError``
propagate unmodified -- this tool does not catch or wrap them.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
key:
    An ``AdrBody`` field name, e.g. ``"decision_drivers"``. ``"options"``
    is rejected -- use the ``option_*`` tools instead.
value:
    The new section text, or a deletion sentinel.

Returns
-------
Adr
    The updated document.

