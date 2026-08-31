# `biz.dfch.specmgr.tsk.tools`

MCP tool wrappers for task lists (mirrors ``req/tools/``'s own shape).

``parse_tsk`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_tsk_example`` returns a complete, valid
sample task list document as raw markdown; ``get_tsk_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem. ``get_tsk``
reads, parses, and returns a full task list document by id -- the sole
id-based read path for TSK (there never was a
``specmgr://tsk/{id}`` resource to begin with). ``list_tsk``
(feat-13-list-paging Task 2.4) returns one page of id/title/status/ref
summaries of every task list, replacing the former ``specmgr://tsk/list``
resource so that ``max_results``/``offset`` paging parameters could be
accepted (see ``.specmgr/feat/feat-13-list-paging/README.md``).
``create_tsk`` assigns a fresh id, builds the frontmatter itself, and
writes a new document (body markdown only, no frontmatter) under the task
list base directory (``tsk.tools._paths``/``_io``). Whole-body and
line-range updates of an existing document go through the generic
``update`` tool in ``general.tools`` (``type="tsk"``), preserving every
frontmatter field except ``updated``. Status changes of an existing
document go through the generic ``set_status`` tool in ``general.tools``
(``type="tsk"``), also bumping ``updated``, leaving the body untouched.
Deletion of ``tsk`` documents goes through the generic ``delete`` tool in
``general.tools`` (``type="tsk"``). ``validate_tsk`` is a
disk-free, id-free dry run against a submitted ``content`` string,
independent of the other tools. Import this package to register all task
list tools at once::

    from biz.dfch.specmgr.tsk import tools  # noqa: F401 (side-effects only)
