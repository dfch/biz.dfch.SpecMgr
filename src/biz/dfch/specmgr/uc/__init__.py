"""Use Case (UC) domain — Cockburn-based use case specification and validation.

This is a domain-first package containing models, tools, prompts, and resources
for managing use case documents.

Import this package to register all use-case tools/prompts/resources against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import uc  # noqa: F401 (side-effects only)

Currently only ``tools`` (``parse_uc``) exists; ``prompts``/``resources`` are
not implemented yet (see ``.specmgr/feat/feat-4-use-cases/README.md`` Phase 3).
"""

from . import tools  # noqa: F401

__all__ = [
    "tools",
]
