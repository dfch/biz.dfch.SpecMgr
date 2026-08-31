# `biz.dfch.specmgr.vcr`

Verification Case Record (VCR) domain -- how a single REQ/UC is verified.

This is a domain-first package, mirroring ``dec``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts, and
resources for managing ``vcr`` documents. A VCR captures a coverage
assessment plus a list of acceptance criteria, each with its own closed
DTAIS verification method (Demonstration, Test, Analysis, Inspection,
Special), for a single REQ or UC cross-reference. It is built on the
generic ``models/md`` parser with the GOL/RSK/QA/DEC simple surface -- no
fine-grained mutation tools (including no per-AC create/read/update/delete
tools), no renderer: writes persist the caller's raw validated body
byte-for-byte.

Import this package to register all verification-case-record tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import vcr  # noqa: F401 (side-effects only)

``tools`` (``create_vcr``, ``parse_vcr``,
``list_vcr``, ``get_vcr``, ``get_vcr_example``, ``get_vcr_template``,
``validate_vcr``), ``resources`` (``specmgr://vcr/schema``,
``specmgr://vcr/example``, ``specmgr://vcr/template``), and ``prompts``
(``create_vcr``, ``update_vcr``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="vcr"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="vcr"``). Like
DEC, VCR has no
``specmgr://vcr/{id}`` resource -- id-based reads go through the ``get_vcr``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://vcr/list`` resource -- ``list_vcr`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

The closed DTAIS verification-method vocabulary that this domain's
``## Acceptance Criteria`` depends on is documented by the cross-cutting
``specmgr://dtais`` resource, which lives in ``general.resources``, not
here, since it is domain-knowledge other document types may also want to
reference.
