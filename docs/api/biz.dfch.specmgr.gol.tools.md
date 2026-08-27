# `biz.dfch.specmgr.gol.tools`

MCP tool wrappers for goals (mirrors ``prb/tools/``'s own shape).

``parse_gol`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_gol_example`` returns a complete, valid
sample goal document as raw markdown; ``get_gol_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead -- both read a packaged, build-guaranteed data file rather
than anything on the caller's filesystem (Task 3.10). ``get_gol`` (Task 3.8)
reads, parses, and returns a full goal document by id -- the sole id-based
read path for GOL (there is no ``specmgr://gol/{id}`` resource, ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_gol`` (Task 3.9) returns one
page of id/title/status/ref summaries of every goal, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_gol``
(Task 3.3) assigns a fresh id, builds the frontmatter itself, and writes a
new document (body markdown only, no frontmatter) under the goal base
directory (``gol.tools._paths``/``_io``). Whole-body and line-range updates
of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="gol"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="gol"``), also
bumping ``updated``, leaving the body untouched.
``delete_gol`` (Task 3.6) is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_gol`` (Task 3.7) is a disk-free, id-free dry run
against a submitted ``content`` string, independent of the other tools.
Import this package to register all goal tools at once::

    from biz.dfch.specmgr.gol import tools  # noqa: F401 (side-effects only)
