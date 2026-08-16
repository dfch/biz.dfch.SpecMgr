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
``specmgr://tsk/{id}`` resource to begin with). ``create_tsk`` assigns a
fresh id, builds the frontmatter itself, and writes a new document (body
markdown only, no frontmatter) under the task list base directory
(``tsk.tools._paths``/``_io``). ``update_tsk`` replaces an existing
document's body the same way, preserving every frontmatter field except
``updated``. ``set_status_tsk`` is the only path that changes ``status``,
also bumping ``updated``, leaving the body untouched. ``delete_tsk`` is a
registered stub -- always raises ``NotImplementedError``, reserving the
name for a future real implementation. ``validate_tsk`` is a disk-free,
id-free dry run against a submitted ``content`` string, independent of the
other tools. Import this package to register all task list tools at once::

    from biz.dfch.specmgr.tsk import tools  # noqa: F401 (side-effects only)
