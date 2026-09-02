# `biz.dfch.specmgr.sysrs.tools._write`

Shared frontmatter+body composition/write helper for ``create_sysrs`` and
the generic ``update`` tool in ``general.tools`` (``type="sysrs"``).

Deliberately **not** part of ``sysrs.tools._io`` -- that module's own docstring
rules out a ``write_sysrs``/``render_sysrs`` counterpart to ``read_sysrs``, since
neither ``create_sysrs`` nor the generic ``update`` tool in ``general.tools``
ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.sysrs.models.v1.SysrsDocument` model. What
:func:`write_sysrs_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.sysrs.models.v1.SysrsFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_sysrs.py`` into its own module so the generic
``update`` and ``set_status`` tools in ``general.tools`` (``type="sysrs"``)
do not have to duplicate it. Mirrors ``vcr.tools._write``/``dec.tools._write``
file-for-file.

## Functions

### `write_sysrs_file(path: 'Path', frontmatter_: 'SysrsFrontmatter', content: 'str') -> 'None'`

Compose a full System Requirements Specification file (frontmatter + body) and write it to ``path``.

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

