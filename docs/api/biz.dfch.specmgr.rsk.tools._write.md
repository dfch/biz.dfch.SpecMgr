# `biz.dfch.specmgr.rsk.tools._write`

Shared frontmatter+body composition/write helper for ``create_rsk`` and
the generic ``update`` tool in ``general.tools`` (``type="rsk"``).

Deliberately **not** part of ``rsk.tools._io`` -- that module's own docstring
rules out a ``write_rsk``/``render_rsk`` counterpart to ``read_rsk``, since
neither ``create_rsk`` nor the generic ``update`` tool in ``general.tools``
ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument` model. What
:func:`write_rsk_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.rsk.models.v1.RskFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_rsk.py`` into its own module so the generic
``update`` tool in ``general.tools`` does not have to duplicate it.
Mirrors ``tsk.tools._write`` file-for-file.

## Functions

### `write_rsk_file(path: 'Path', frontmatter_: 'RskFrontmatter', content: 'str') -> 'None'`

Compose a full risk file (frontmatter + body) and write it to ``path``.

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

