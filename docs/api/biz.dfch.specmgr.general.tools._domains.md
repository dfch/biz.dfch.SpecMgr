# `biz.dfch.specmgr.general.tools._domains`

The single source of truth for the document-type domain names (feat-125-domain-lists, REQ-001).

Every other module that names a set of document types imports the names from
here instead of hand-listing them itself (the feat-125 sweep ruling: no
other ``src/`` or ``tests/`` module may hand-list a domain-name set).

:data:`WHOLE_BODY_DOMAINS` is the only hand-listed tuple in the module --
the whole-body document types in the canonical order ``req``, ``uc``,
``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
``vcr``, ``sysrs`` -- and every other tuple is derived from it, never
hand-listed a second time: :data:`WHOLE_BODY_NO_FEAT_DOMAINS` is the
whole-body domains without ``feat``, :data:`UUID_DOMAINS` is those plus
``adr``, and :data:`ALL_DOMAINS` is ``adr`` prefixed to the whole-body
domains. :data:`ADR` and :data:`FEAT` are the two name singletons. A new
document type registers its name in :data:`WHOLE_BODY_DOMAINS` once, and
every derived tuple picks it up by construction.
