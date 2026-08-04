# `biz.dfch.specmgr.adr.tools.option_read`

``@mcp.tool()`` wrapper: option_read (plan §5, §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.option_read``:
re-reads and re-parses the current on-disk state; there is no in-memory
cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file itself is
always the source of truth.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.

## Functions

### `option_read(id: 'str', full_title: 'str') -> 'str'`

Return the content of one option on the ADR identified by ``id``.

Read-only -- does not write. Lets
:class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError` propagate
if no option matches ``full_title``.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
full_title:
    The option's full title, e.g. ``"Option 1: A title"``.

Returns
-------
str
    The option's current content.

