# `biz.dfch.specmgr.feat.tools`

Feature (FEAT) MCP tools.

**Phase 0 scaffolding only.** Populated in Phase 2 of
``.specmgr/feat/feat-31-feature/README.md``: bespoke, folder-per-document
addressing (``_paths.py``, ``_io.py``, ``_lock.py``, ``_write.py`` -- *not*
built on ``general/tools/_doc_paths.py``, since ``feat`` documents live one
per folder at ``<base>/<id>/README.md`` with a non-UUID id) plus the eight
lifecycle tools (``create_feat``, ``parse_feat``, ``list_feat``,
``get_feat``, ``get_feat_example``, ``get_feat_template``, ``delete_feat``,
``validate_feat``). No ``update_feat``/``set_status_feat`` -- those go
through the generic ``update``/``set_status`` tools in ``general.tools``
(``type="feat"``, added in the same phase).
