# `biz.dfch.specmgr.req.tools`

MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).

``parse_req`` reads a raw filepath, parses, and validates it into a structured
document model. ``get_req_example`` returns a complete, valid sample requirement
document as raw markdown (Task 3.6); ``get_req_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead (Task 3.7) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. ``get_req`` (feat-7-various-
improvements Task 0.9) reads, parses, and returns a full requirement document
by id -- the sole id-based read path for REQ, replacing the former
``specmgr://req/{id}`` resource (see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
``list_req`` (feat-13-list-paging Task 2.2) returns one page of id/title/
status/ref summaries of every requirement, replacing the former
``specmgr://req/list`` resource so that ``max_results``/``offset`` paging
parameters could be accepted (see
``.specmgr/feat/feat-13-list-paging/README.md``). ``create_req`` (Task 3.12)
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the requirement base directory
(``req.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in ``general.tools``
(``type="req"``), preserving every frontmatter field except ``updated``.
``set_status_req`` (Task 3.14) is the only path that
changes ``status``, also bumping ``updated``, leaving the body untouched.
``delete_req`` (Task 3.15) is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_req`` (Task 3.16) is a disk-free, id-free dry
run against a submitted ``content`` string, independent of the other
tools. Import this package to register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
