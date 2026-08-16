# `biz.dfch.specmgr.uc.tools._write`

Shared frontmatter+body composition/write helper for ``create_uc``/``update_uc``
(Task 3.1.5).

Deliberately **not** part of ``uc.tools._io`` -- mirrors ``req.tools._write``:
that module's own docstring rules out a ``write_uc``/``render_uc`` counterpart
to ``read_uc``, since a use case's body markdown is never rendered back out
from a parsed :class:`~biz.dfch.specmgr.uc.models.v2.UseCase` model. What
:func:`write_uc_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.uc.models.v2.UcFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_uc.py`` into its own module so ``update_uc.py``
does not have to duplicate it.

## Functions

### `write_uc_file(path: 'Path', frontmatter_: 'UcFrontmatter', content: 'str') -> 'None'`

Compose a full use-case file (frontmatter + body) and write it to ``path``.

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

