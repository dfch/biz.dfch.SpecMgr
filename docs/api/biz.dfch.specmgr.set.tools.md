# `biz.dfch.specmgr.set.tools`

MCP tool wrappers for set documents (mirrors ``txt/tools/``'s own shape).

``parse_set`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_set_example`` returns a complete, valid
sample set document as raw markdown; ``get_set_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem
(feat-173-req-iso29148-level-set Phase 180).
``get_set_schema`` returns the domain's generated JSON Schema (2020-12
dialect) as raw text, reading the same packaged, build-guaranteed data
file (SET ships the schema as a tool from day one, the feat-189 Phase 105
/ DEC 112b6498-078b-4a59-88b8-8ffb7a5041b3 precedent).
``get_set`` reads, parses, and returns a full set document by id -- the
sole id-based read path for SET (there is no ``specmgr://set/{id}``
resource, DEC ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_set`` returns
one page of id/title/status/ref summaries of every set document, shipped
as a paged tool from day one (DEC ec9f5262-9912-49d0-903f-fcfb54f28c13).
``create_set`` assigns a fresh id, builds the frontmatter itself, and
writes a new document (body markdown only, no frontmatter) under the set
base directory (``set.tools._paths``/``_io``). Whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="set"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="set"``), also
bumping ``updated``, leaving the body untouched. Deletion of ``set``
documents goes through the generic ``delete`` tool in ``general.tools``
(``type="set"``). Disk-free, id-free dry-run content validation goes
through the generic ``validate`` tool in ``general.tools`` (``type="set"``);
there is no per-domain mutation tool of this domain's own (dispatch-only
from day one, DEC 36905d5b-8057-4294-8665-c7eed5534db0).
Import this package to register all set tools at once::

    from biz.dfch.specmgr.set import tools  # noqa: F401 (side-effects only)
