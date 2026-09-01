# `biz.dfch.specmgr.qa.tools`

MCP tool wrappers for Question and Answer (QA) documents (mirrors ``req/tools/``'s own shape).

``parse_qa`` reads a raw filepath, parses, and validates it into a structured
document model. ``get_qa_example`` returns a complete, valid sample QA
document as raw markdown; ``get_qa_template`` returns a document with every
field present but populated with short placeholder ("blind text") content
instead -- both read a packaged, build-guaranteed data file rather than
anything on the caller's filesystem. ``get_qa`` reads, parses, and returns a
full QA document by id -- the sole id-based read path for QA, mirroring
REQ's own choice (see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_qa``
(feat-13-list-paging Task 2.5) returns one page of id/title/status/ref
summaries of every QA document, replacing the former ``specmgr://qa/list``
resource so that ``max_results``/``offset`` paging parameters could be
accepted (see ``.specmgr/feat/feat-13-list-paging/README.md``). ``create_qa``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the QA base directory
(``qa.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in ``general.tools``
(``type="qa"``), preserving every frontmatter field except ``updated``.
Status changes of an existing document go through the generic
``set_status`` tool in ``general.tools`` (``type="qa"``), also bumping
``updated``, leaving the body untouched. Deletion of ``qa`` documents goes
through the generic ``delete`` tool in ``general.tools`` (``type="qa"``).
``validate_qa`` is a disk-free, id-free dry run against
a submitted ``content`` string, independent of the other tools. Import this
package to register all QA tools at once::

    from biz.dfch.specmgr.qa import tools  # noqa: F401 (side-effects only)
