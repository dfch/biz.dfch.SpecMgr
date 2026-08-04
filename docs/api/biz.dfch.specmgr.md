# `biz.dfch.specmgr`

The main library init file.

This module intentionally has no imports of its own: the ``cli`` and
``server`` submodules pull in the ``cli``/``mcp`` optional-dependency
extras respectively, and importing them here would force those extras
onto every consumer of the base library.
