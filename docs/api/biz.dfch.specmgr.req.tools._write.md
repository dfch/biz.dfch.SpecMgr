# `biz.dfch.specmgr.req.tools._write`

Shared frontmatter+body composition/write helper for ``create_req`` and
the generic ``update`` tool in ``general.tools`` (``type="req"``).

Deliberately **not** part of ``req.tools._io`` -- that module's own docstring
rules out a ``write_req``/``render_req`` counterpart to ``read_req``, since
Task 3.9's design never renders a body back out from a parsed
:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` model (unlike
``adr.tools._io.write_adr``, which does via ``render_adr``). What
:func:`write_req_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_req.py`` into its own module so the generic
``update`` tool in ``general.tools`` does not have to duplicate it.

## Functions

### `write_req_file(path: 'Path', frontmatter_: 'ReqFrontmatter', content: 'str') -> 'None'`

Compose a full requirement file (frontmatter + body) and write it to ``path``.

``content`` is embedded verbatim -- it is never reformatted/re-rendered
here. One caveat inherent to the underlying ``python-frontmatter``
library, not specially handled here: its ``YAMLHandler`` strips trailing
whitespace from ``content`` when serializing, so the written body may
differ from ``content`` by trailing whitespace only, never in substance.

Parameters
----------
path:
    The destination file path.
frontmatter_:
    The already-constructed, already-validated frontmatter to serialize
    as the file's YAML block.
content:
    The raw body markdown, exactly as submitted by the caller.

