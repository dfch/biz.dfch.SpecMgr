# `biz.dfch.specmgr.models.adr`

Pydantic models for MADR 4.0.0-based Architecture Decision Records.

- :class:`AdrFrontmatter` -- the YAML frontmatter block, including
  the specmgr schema version (``version``, a specmgr-only extension key,
  not part of the MADR 4.0.0 standard).
- :class:`AdrBody` -- the whole-section body fields plus the
  dynamic :class:`AdrOption` collection.
- :class:`AdrOption` -- one ``### Option N: {title}`` sub-section.
- :class:`Adr` -- a full ADR document (frontmatter + body).
- :func:`parse_adr` -- parses an on-disk ``.md`` file's text into an
  :class:`Adr`; :class:`AdrParseError` is its
  structural-error type (see ``v1.parser`` for the full parse-error split).
- :func:`render_adr` -- renders an :class:`Adr` back into the canonical
  on-disk ``.md`` text (the other half of the
  parse/render pipeline).

The MCP tool wrappers are a separate, later step.

**Schema versioning:** every model class lives under a ``vN``
sibling package (currently only :mod:`.v1`), one per *major* schema
version -- see :data:`SCHEMA_MAJOR_VERSION`/``CURRENT_SCHEMA_VERSION`` in
``v1._util``, and ``AdrFrontmatter.version`` in ``v1.frontmatter``. The
names re-exported here always point at the current
version's classes, so ``from biz.dfch.specmgr.models.adr import Adr``
tracks whichever ``vN`` is current without callers needing to know the
version number -- callers that specifically need an older version's
classes (e.g. a migration step) import ``biz.dfch.specmgr.models.adr.v1``
directly instead.
