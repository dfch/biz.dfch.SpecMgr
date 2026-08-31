# `biz.dfch.specmgr.vcr.tools`

MCP tool wrappers for verification case records (mirrors ``dec/tools/``'s own shape).

``parse_vcr`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_vcr_example`` returns a complete, valid
sample verification case record document as raw markdown; ``get_vcr_template``
returns a document with every field present but populated with short
placeholder ("blind text") content instead -- both read a packaged,
build-guaranteed data file rather than anything on the caller's filesystem
(Task 2.1). ``get_vcr`` reads, parses, and returns a full verification case
record document by id -- the sole id-based read path for VCR (there is no
``specmgr://vcr/{id}`` resource, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
``list_vcr`` returns one page of id/title/status/ref summaries of every
verification case record, shipped as a paged tool from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_vcr`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the verification case record base directory
(``vcr.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="vcr"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="vcr"``), also
bumping ``updated``, leaving the body untouched. Deletion of ``vcr``
documents goes through the generic ``delete`` tool in ``general.tools``
(``type="vcr"``). ``validate_vcr`` is a disk-free, id-free dry run against
a submitted ``content`` string, independent of the other tools. Import this
package to register all verification case record tools at once::

    from biz.dfch.specmgr.vcr import tools  # noqa: F401 (side-effects only)
