# `biz.dfch.specmgr.qa.tools._write`

Shared frontmatter+body composition/write helper for ``create_qa`` and
the generic ``update`` tool in ``general.tools`` (``type="qa"``).

Deliberately **not** part of ``qa.tools._io`` -- that module's own docstring
rules out a ``write_qa``/``render_qa`` counterpart to ``read_qa``, since this
design never renders a body back out from a parsed
:class:`~biz.dfch.specmgr.qa.models.v2.QaDocument` model (unlike
``adr.tools._io.write_adr``, which does via ``render_adr``). What
:func:`write_qa_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.qa.models.v2.QaFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_qa.py`` into its own module so the generic
``update`` tool in ``general.tools`` does not have to duplicate it. 1:1
port of ``req.tools._write``.

## Functions

### `write_qa_file(path: 'Path', frontmatter_: 'QaFrontmatter', content: 'str') -> 'None'`

Compose a full QA file (frontmatter + body) and write it to ``path``.

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

