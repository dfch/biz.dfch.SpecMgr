# `biz.dfch.specmgr._paths`

Private, dependency-free repo-root-relative path constants.

This module imports nothing beyond the standard library (``pathlib``), so
both the ``cli`` extra (``commands/schema.py``, ``commands/docs.py``, ...)
and, potentially, the ``mcp`` extra can share it without either extra's
optional dependencies (``typer``, ``mcp``) leaking into the other's import
graph -- unlike importing ``commands.schema`` directly (pulls in ``typer``)
or the ``general`` package (whose ``__init__.py`` side-effect-imports
``mcp``-dependent tools).

``REPO_ROOT``/``DOCS_DIR`` only resolve correctly when this package is used
from an editable/source checkout (the layout ``uv run`` and CI use) -- a
built, non-editable installation (e.g. a plain ``pip install`` from PyPI)
does not ship ``docs/`` as package data, so climbing from ``__file__``
would land somewhere inside ``site-packages`` with no ``docs/`` directory
at all. This is why ``req/resources/req_schema.py`` (Task 3.8) deliberately
does **not** import this module -- it reads a packaged-data copy via
``req._data`` instead, so the ``specmgr://req/schema`` MCP resource keeps
working from a non-editable install too. Every current caller of
``DOCS_DIR`` is a dev/CI-only CLI command (``commands/schema.py``,
``commands/docs.py``, ``commands/adr_toc.py``); it is not meant for
resources/tools that must survive a real, non-editable install -- use
``importlib.resources``-backed package data for those instead (see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made).
