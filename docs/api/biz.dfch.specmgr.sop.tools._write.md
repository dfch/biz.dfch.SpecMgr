# `biz.dfch.specmgr.sop.tools._write`

Shared frontmatter+body composition/write helper for ``create_sop`` and
the generic ``update`` tool in ``general.tools`` (``type="sop"``).

Deliberately **not** part of ``sop.tools._io`` -- that module's own docstring
rules out a ``write_sop``/``render_sop`` counterpart to ``read_sop``, since
neither ``create_sop`` nor the generic ``update`` tool in ``general.tools``
ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.sop.models.v1.SopDocument` model. What
:func:`write_sop_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.sop.models.v1.SopFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_sop.py`` into its own module so the generic
``update`` and ``set_status`` tools in ``general.tools`` (``type="sop"``)
do not have to duplicate it. Mirrors ``dec.tools._write`` file-for-file.

## Functions

### `write_sop_file(path: 'Path', frontmatter_: 'SopFrontmatter', content: 'str') -> 'None'`

Compose a full SOP file (frontmatter + body) and write it to ``path``.

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

