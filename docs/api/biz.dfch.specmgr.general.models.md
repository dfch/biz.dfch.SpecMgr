# `biz.dfch.specmgr.general.models`

Shared, cross-domain Pydantic models with no document-type-specific content.

Backs feat-13's ``<domain>_list`` -> ``list_<domain>`` pagination rollout
(``.specmgr/feat/feat-13-list-paging/README.md`` Task 1.1/Task 1.3):

- :class:`PagedResult` -- a generic ``{total, offset, max_results, truncated,
  results}`` page wrapper, shared by every domain's ``list_<domain>`` tool.
- :class:`DocSummary` -- the common ``id``/``title``/``status``/``ref`` field
  set that every domain's own ``*Summary`` model (``ReqSummary``,
  ``UcSummary``, ``TskSummary``, ``QaSummary``) subclasses.

Also backs feat-81-83-validation Phase 2's generic ``validate`` tool
(REQ-004):

- :class:`ValidateResult`/:class:`ValidationErrorEntry` -- the non-raising,
  structured ``{valid, errors}`` result the generic ``validate`` tool
  (``general.tools.validate``) returns for a content-validation failure
  instead of letting the exception propagate.

Also backs feat-103-set-status-error's narrow extension of that same
non-raising workaround to the generic ``set_status`` tool's own single
failure mode (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014):

- :class:`InvalidStatusResult` -- the non-raising, structured result the
  generic ``set_status`` tool (``general.tools.set_status``) returns for an
  out-of-vocabulary ``status`` value, instead of letting
  ``pydantic.ValidationError`` propagate. Distinct from
  :class:`ValidateResult` -- a different tool's own model.

Also backs feat-134-related-artifact-similarity's (Phase 3) two generic
similarity tools' shared runtime-unavailability contract (REQ-003, ADR
750842b2-aca4-4649-ba0c-855ec8e1f505):

- :class:`SimilarityUnavailableResult` -- the non-raising, structured
  ``{available, reason, message}`` result the ``find_related``/
  ``find_similar_text`` tools return whenever the embedding backend is
  unavailable (the ``SPECMGR_SIMILARITY_DISABLED`` opt-out env var is
  present, or the backend fails to import or the model fails to load),
  instead of raising. Mirrors :class:`InvalidStatusResult`'s own
  non-raising precedent -- a different tool surface's own model.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-002/REQ-005/REQ-006):

- :func:`parse_dtais`/:class:`Dtais` -- parses the DTAIS verification-
  methods guidance document (``general/data/general_dtais.md``) backing
  ``specmgr://dtais``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).
- :func:`parse_rasci`/:class:`Rasci` -- parses the RASCI responsibility-
  assignment guidance document (``general/data/general_rasci.md``) backing
  ``specmgr://rasci``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).
- :func:`parse_ears`/:class:`Ears` -- parses the EARS requirement-
  phrasing-templates guidance document (``general/data/general_ears.md``)
  backing ``specmgr://ears``, purely to fail fast on structural drift (the
  parsed result is discarded by the resource itself).

Import this package to use either model directly::

    from biz.dfch.specmgr.general.models import DocSummary, PagedResult
