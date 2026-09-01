# `biz.dfch.specmgr.prb.tools`

MCP tool wrappers for problem statements (mirrors ``tsk/tools/``'s own shape).

``parse_prb`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_prb_example`` returns a complete, valid
sample problem statement document as raw markdown; ``get_prb_template``
returns a document with every field present but populated with short
placeholder ("blind text") content instead -- both read a packaged,
build-guaranteed data file rather than anything on the caller's filesystem.
``get_prb`` reads, parses, and returns a full problem statement document by
id -- the sole id-based read path for PRB (there is no
``specmgr://prb/{id}`` resource). ``list_prb`` returns one page of
id/title/status/ref summaries of every problem statement, shipped as a
paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
``create_prb`` assigns a fresh id, builds the frontmatter itself, and
writes a new document (body markdown only, no frontmatter) under the
problem statement base directory (``prb.tools._paths``/``_io``).
Whole-body and line-range updates of an existing document go through the
generic ``update`` tool in ``general.tools`` (``type="prb"``), preserving
every frontmatter field except ``updated``. Status changes of an existing
document go through the generic ``set_status`` tool in ``general.tools``
(``type="prb"``), also bumping ``updated``, leaving the body untouched.
Deletion of ``prb`` documents goes through the generic ``delete`` tool in
``general.tools`` (``type="prb"``). ``validate_prb`` is a disk-free,
id-free dry run against a submitted ``content`` string, independent of the
other tools. Import this package to register all problem statement tools at
once::

    from biz.dfch.specmgr.prb import tools  # noqa: F401 (side-effects only)
