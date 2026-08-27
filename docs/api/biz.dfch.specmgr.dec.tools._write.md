# `biz.dfch.specmgr.dec.tools._write`

Shared frontmatter+body composition/write helper for ``create_dec`` and
the generic ``update`` tool in ``general.tools`` (``type="dec"``).

Deliberately **not** part of ``dec.tools._io`` -- that module's own docstring
rules out a ``write_dec``/``render_dec`` counterpart to ``read_dec``, since
neither ``create_dec`` nor the generic ``update`` tool in ``general.tools``
ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument` model. What
:func:`write_dec_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_dec.py`` into its own module so the generic
``update`` and ``set_status`` tools in ``general.tools`` (``type="dec"``)
do not have to duplicate it. Mirrors ``gol.tools._write`` file-for-file.

## Functions

### `write_dec_file(path: 'Path', frontmatter_: 'DecFrontmatter', content: 'str') -> 'None'`

Compose a full decision file (frontmatter + body) and write it to ``path``.

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

