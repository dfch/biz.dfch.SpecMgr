# `biz.dfch.specmgr.sysrs.tools`

MCP tool wrappers for System Requirements Specification (SYSRS) documents (mirrors ``vcr/tools/``'s own shape).

``parse_sysrs`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_sysrs_example`` returns a complete, valid
sample System Requirements Specification document as raw markdown;
``get_sysrs_template`` returns a document with every field present but
populated with short placeholder ("blind text") content instead -- both
read a packaged, build-guaranteed data file rather than anything on the
caller's filesystem (Task 3.2; the real packaged data files themselves
arrive in Phase 4, so both tools raise ``FileNotFoundError`` until then).
``get_sysrs`` reads, parses, and returns a full System Requirements
Specification document by id -- the sole id-based read path for SYSRS
(there is no ``specmgr://sysrs/{id}`` resource, ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_sysrs`` returns one page of
id/title/status/ref summaries of every System Requirements Specification,
shipped as a paged tool from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_sysrs`` assigns a fresh id,
builds the frontmatter itself, and writes a new document (body markdown
only, no frontmatter) under the System Requirements Specification base
directory (``sysrs.tools._paths``/``_io``). Whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="sysrs"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="sysrs"``), also
bumping ``updated``, leaving the body untouched. Classification changes go
through the generic ``set_classification`` tool in ``general.tools``
(``type="sysrs"``). Deletion of ``sysrs`` documents goes through the
generic ``delete`` tool in ``general.tools`` (``type="sysrs"``).
Disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="sysrs"``) -- the former
``validate_sysrs`` tool was removed in favor of it (feat-81-83-validation
Phase 2). There is **no** per-domain
``update_sysrs``/``set_status_sysrs``/``delete_sysrs``/``validate_sysrs``
tool -- dispatch-only from day one, ADR
36905d5b-8057-4294-8665-c7eed5534db0. Import this package to register all
System Requirements Specification tools at once::

    from biz.dfch.specmgr.sysrs import tools  # noqa: F401 (side-effects only)
