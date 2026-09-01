# `biz.dfch.specmgr.dec.tools`

MCP tool wrappers for decisions (mirrors ``gol/tools/``'s own shape).

``parse_dec`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_dec_example`` returns a complete, valid
sample decision document as raw markdown; ``get_dec_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (Task 2.2).
``get_dec`` reads, parses, and returns a full decision document by id -- the
sole id-based read path for DEC (there is no ``specmgr://dec/{id}`` resource,
ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_dec`` returns one page of
id/title/status/ref summaries of every decision, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_dec``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the decision base directory
(``dec.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``), also
bumping ``updated``, leaving the body untouched. Deletion of ``dec``
documents goes through the generic ``delete`` tool in ``general.tools``
(``type="dec"``). ``validate_dec`` is a disk-free, id-free dry run against
a submitted ``content`` string, independent of the other tools. Import this
package to register all decision tools at once::

    from biz.dfch.specmgr.dec import tools  # noqa: F401 (side-effects only)
