# `biz.dfch.specmgr._paths`

Private, dependency-free repo-root-relative path constants.

This module imports nothing beyond the standard library (``pathlib``), so
both the ``cli`` extra (``commands/schema.py``, ``commands/docs.py``, ...)
and the ``mcp`` extra (e.g. ``req/resources/req_schema.py``) can share it
without either extra's optional dependencies (``typer``, ``mcp``) leaking
into the other's import graph -- unlike importing ``commands.schema``
directly (pulls in ``typer``) or the ``general`` package (whose
``__init__.py`` side-effect-imports ``mcp``-dependent tools).

``REPO_ROOT``/``DOCS_DIR`` only resolve correctly when this package is used
from an editable/source checkout (the layout ``uv run`` and CI use) -- a
built, non-editable installation (e.g. a plain ``pip install`` from PyPI)
does not ship ``docs/`` as package data, so climbing from ``__file__``
would land somewhere inside ``site-packages`` with no ``docs/`` directory
at all. This is an accepted, currently-out-of-scope limitation (see
`.specmgr/feat/feat-6-requirement-artifact/README.md`'s Decisions Made) --
every current caller of ``DOCS_DIR`` is either a dev/CI-only CLI command or
a resource whose backing file is guaranteed present at build time.
