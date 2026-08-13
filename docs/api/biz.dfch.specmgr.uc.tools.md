# `biz.dfch.specmgr.uc.tools`

MCP tool wrappers for use cases (mirrors ``adr/tools/``'s own shape).

Currently just ``parse_uc`` -- a single, narrowly-scoped tool added ahead of
the full Phase 3 (``.specmgr/feat/feat-4-use-cases/README.md``) tool
specification/sequencing, at the repo owner's explicit request. Unlike
``adr/tools/``, there is no id-based file storage layer for use cases yet
(no ``uc_base_dir``/``_paths.py``/``_io.py`` equivalent), so this tool takes
raw markdown text directly rather than resolving an id to an on-disk file.
Import this package to register all use-case tools at once::

    from biz.dfch.specmgr.uc import tools  # noqa: F401 (side-effects only)
