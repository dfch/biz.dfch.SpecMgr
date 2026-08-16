# `biz.dfch.specmgr.uc.tools`

MCP tool wrappers for use cases (mirrors ``req/tools/``'s own shape).

``parse_uc`` reads a raw filepath, parses, and validates it into a structured
document model (added ahead of Task 3.1's full specification; unchanged).
``get_uc_example`` returns a complete, valid sample use-case document as raw
markdown (Task 3.1.2); ``get_uc_template`` returns a document with every
field present but populated with short placeholder ("blind text") content
instead (Task 3.1.3) -- both read a packaged, build-guaranteed data file
rather than anything on the caller's filesystem. ``get_uc`` (Task 3.1.5)
reads, parses, and returns a full use-case document by id -- the sole
id-based read path for UC. ``create_uc`` (Task 3.1.5) assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the use-case base directory (``uc.tools._paths``/
``_io``). ``update_uc`` (Task 3.1.5) replaces an existing document's body
the same way, preserving every frontmatter field except ``updated``.
``set_status_uc`` (Task 3.1.5) is the only path that changes ``status``,
also bumping ``updated``, leaving the body untouched. ``delete_uc`` (Task
3.1.5) is a registered stub -- always raises ``NotImplementedError``,
reserving the name for a future real implementation. ``validate_uc`` (Task
3.1.5) is a disk-free, id-free dry run against a submitted ``content``
string, independent of the other tools. Import this package to register all
use-case tools at once::

    from biz.dfch.specmgr.uc import tools  # noqa: F401 (side-effects only)
