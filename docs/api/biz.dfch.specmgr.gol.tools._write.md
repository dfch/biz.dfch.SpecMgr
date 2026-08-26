# `biz.dfch.specmgr.gol.tools._write`

Shared frontmatter+body composition/write helper for ``create_gol``/``update_gol``.

Deliberately **not** part of ``gol.tools._io`` -- that module's own docstring
rules out a ``write_gol``/``render_gol`` counterpart to ``read_gol``, since
neither ``create_gol`` nor ``update_gol`` ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.gol.models.v1.GolDocument` model. What
:func:`write_gol_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.gol.models.v1.GolFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_gol.py`` into its own module so
``update_gol.py``/``set_status_gol.py`` do not have to duplicate it. Mirrors
``prb.tools._write`` file-for-file.

## Functions

### `write_gol_file(path: 'Path', frontmatter_: 'GolFrontmatter', content: 'str') -> 'None'`

Compose a full goal file (frontmatter + body) and write it to ``path``.

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

