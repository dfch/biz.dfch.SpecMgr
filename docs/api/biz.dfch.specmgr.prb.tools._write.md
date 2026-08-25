# `biz.dfch.specmgr.prb.tools._write`

Shared frontmatter+body composition/write helper for ``create_prb``/``update_prb``.

Deliberately **not** part of ``prb.tools._io`` -- that module's own docstring
rules out a ``write_prb``/``render_prb`` counterpart to ``read_prb``, since
neither ``create_prb`` nor ``update_prb`` ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.prb.models.v1.PrbDocument` model. What
:func:`write_prb_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.prb.models.v1.PrbFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_prb.py`` into its own module so
``update_prb.py``/``set_status_prb.py`` do not have to duplicate it. Mirrors
``tsk.tools._write`` file-for-file.

## Functions

### `write_prb_file(path: 'Path', frontmatter_: 'PrbFrontmatter', content: 'str') -> 'None'`

Compose a full problem statement file (frontmatter + body) and write it to ``path``.

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

