# `biz.dfch.specmgr.rsk.models.v1`

Risk (RSK) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``tsk/models/v1`` layout: a free-function ``parse_rsk`` entry
point, document-level ``RskDocument(frontmatter, body)`` wrapper, and a
one-line ``RskSummary`` for the paged ``list_rsk`` tool, with frontmatter and
body subclasses under this same package. Body classes map directly to heading
sections in an ``rsk`` markdown file -- see ``body.py``/``assessment.py`` for
the full hierarchy.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-003/REQ-004):

- :func:`parse_tara`/:class:`Tara` -- parses the TARA risk-response-
  strategy guidance document (``rsk/data/rsk_tara.md``) backing
  ``specmgr://rsk/tara``, purely to fail fast on structural drift (the
  parsed result is discarded by the resource itself).
- :func:`parse_risk_matrix`/:class:`RiskMatrix` -- parses the 5x5
  risk-matrix guidance document (``rsk/data/rsk_risk_matrix.md``) backing
  ``specmgr://rsk/risk-matrix``, purely to fail fast on structural drift
  in the "Product thresholds" list (the parsed result is discarded by the
  resource itself).
