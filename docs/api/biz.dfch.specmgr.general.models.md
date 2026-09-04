# `biz.dfch.specmgr.general.models`

Shared, cross-domain Pydantic models with no document-type-specific content.

Backs feat-13's ``<domain>_list`` -> ``list_<domain>`` pagination rollout
(``.specmgr/feat/feat-13-list-paging/README.md`` Task 1.1/Task 1.3):

- :class:`PagedResult` -- a generic ``{total, offset, max_results, truncated,
  results}`` page wrapper, shared by every domain's ``list_<domain>`` tool.
- :class:`DocSummary` -- the common ``id``/``title``/``status``/``ref`` field
  set that every domain's own ``*Summary`` model (``ReqSummary``,
  ``UcSummary``, ``TskSummary``, ``QaSummary``) subclasses.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-002/REQ-005):

- :func:`parse_dtais`/:class:`Dtais` -- parses the DTAIS verification-
  methods guidance document (``general/data/general_dtais.md``) backing
  ``specmgr://dtais``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).
- :func:`parse_rasci`/:class:`Rasci` -- parses the RASCI responsibility-
  assignment guidance document (``general/data/general_rasci.md``) backing
  ``specmgr://rasci``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).

Import this package to use either model directly::

    from biz.dfch.specmgr.general.models import DocSummary, PagedResult
