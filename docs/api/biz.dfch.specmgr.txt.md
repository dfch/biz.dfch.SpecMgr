# `biz.dfch.specmgr.txt`

Free-Form Text (TXT) domain -- a generic, minimally structured catch-all for unstructured markdown text.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
mirroring ``vcr``'s layout, containing models, tools, prompts, and resources
for managing ``txt`` documents. A ``txt`` document is a generic, minimally
structured catch-all for unstructured markdown text that does not warrant a
dedicated domain (ad hoc notes, meeting minutes, review/audit write-ups,
scratch analysis): a single ``# {title}`` H1, a mandatory free-form opaque
body (any markdown, including H2 to H6 headings), and a mandatory newest-first
``## Updates`` log. See `.specmgr/feat/feat-229-txt/README.md` for the full
design.

It is built on the generic ``models/md`` parser with the VCR simple surface --
dispatch-only from day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0): no
per-domain ``update_txt``/``set_status_txt``/``validate_txt``/``delete_txt``
tools, no renderer -- writes persist the caller's raw validated body
byte-for-byte.

Import this package to register all free-form text tools against the shared
``mcp`` application instance at once::

    from biz.dfch.specmgr import txt  # noqa: F401 (side-effects only)

``tools`` (``create_txt``, ``parse_txt``, ``list_txt``, ``get_txt``
(``raw``/``offset``/``limit``/``numbered``), ``get_txt_example``,
``get_txt_template``, ``get_txt_schema``) are implemented; whole-body and
line-range updates of an existing document go through the generic ``update``
tool in ``general.tools`` (``type="txt"``), status changes through the
generic ``set_status`` tool in ``general.tools`` (``type="txt"``), and
disk-free, id-free dry-run content validation through the generic
``validate`` tool in ``general.tools`` (``type="txt"``) -- the
generic-tool registration of those dispatches lands with this feature's
Phase 130. Like VCR, TXT has no ``specmgr://txt/{id}`` resource --
id-based reads go through the ``get_txt`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://txt/list`` resource -- ``list_txt`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

Phase 120 state: the ``models`` sub-package (Phase 100), the ``tools``
sub-package (Phase 110), the ``resources`` sub-package (``specmgr://
txt/example``, ``specmgr://txt/template``; Phase 120), and the ``prompts``
sub-package (``create_txt``/``update_txt``; Phase 120) are implemented. As
with the ``qa``/``vcr`` precedent, importing this package registers
whatever the sub-packages currently expose; the ``server.py``
bottom-of-file import that makes the server itself load the package lands
with Phase 160.
