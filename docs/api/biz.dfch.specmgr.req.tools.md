# `biz.dfch.specmgr.req.tools`

MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).

``parse_req`` reads a raw filepath, parses, and validates it into a structured
document model. ``get_req_example`` returns a complete, valid sample requirement
document as raw markdown (Task 3.6); ``get_req_template`` returns a document
with every field present but populated with short placeholder ("blind text")
content instead (Task 3.7) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. ``create_req`` (Task 3.12)
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the requirement base directory
(``req.tools._paths``/``_io``). ``update_req`` (Task 3.13) replaces an
existing document's body the same way, preserving every frontmatter field
except ``updated``. ``set_status_req`` (Task 3.14) is the only path that
changes ``status``, also bumping ``updated``, leaving the body untouched.
``validate_req`` (Task 3.16) is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all requirement tools at once::

    from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
