# `biz.dfch.specmgr.general.models`

Shared, cross-domain Pydantic models with no document-type-specific content.

Backs feat-13's ``<domain>_list`` -> ``list_<domain>`` pagination rollout
(``.specmgr/feat/feat-13-list-paging/README.md`` Task 1.1/Task 1.3):

- :class:`PagedResult` -- a generic ``{total, offset, max_results, truncated,
  results}`` page wrapper, shared by every domain's ``list_<domain>`` tool.
- :class:`DocSummary` -- the common ``id``/``title``/``status``/``ref`` field
  set that every domain's own ``*Summary`` model (``ReqSummary``,
  ``UcSummary``, ``TskSummary``, ``QaSummary``) subclasses.

Import this package to use either model directly::

    from biz.dfch.specmgr.general.models import DocSummary, PagedResult
