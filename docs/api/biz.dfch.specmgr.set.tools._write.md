# `biz.dfch.specmgr.set.tools._write`

Shared frontmatter+body composition/write helper for ``create_set`` and
the generic ``update`` tool in ``general.tools`` (``type="set"``).

Deliberately **not** part of ``set.tools._io`` -- that module's own
docstring rules out a ``write_set``/``render_set`` counterpart to
``read_set``, since neither ``create_set`` nor the generic ``update`` tool
in ``general.tools`` ever render a body back out from a parsed
:class:`~biz.dfch.specmgr.set.models.v1.SetDocument` model. What
:func:`write_set_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.set.models.v1.SetFrontmatter` with the caller's
own already-validated *raw* body text (never reformatted/re-rendered) into
one file. Factored out of ``create_set.py`` into its own module so the
generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="set"``) do not have to duplicate it. Mirrors ``vcr.tools._write``
file-for-file.

## Functions

### `write_set_file(path: 'Path', frontmatter_: 'SetFrontmatter', content: 'str') -> 'None'`

Compose a full set document file (frontmatter + body) and write it to ``path``.

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

