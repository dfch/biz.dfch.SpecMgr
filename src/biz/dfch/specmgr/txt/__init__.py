# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Free-Form Text (TXT) domain -- a generic, minimally structured catch-all for unstructured markdown text.

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

Phase 110 state: the ``models`` sub-package (Phase 100) and the ``tools``
sub-package (Phase 110) are implemented; the ``resources`` (``specmgr://
txt/example``, ``specmgr://txt/template``) and ``prompts``
(``create_txt``/``update_txt``) sub-packages are still empty placeholders
for Phase 120. As with the ``qa``/``vcr`` precedent, importing this package
registers whatever the sub-packages currently expose; the ``server.py``
bottom-of-file import that makes the server itself load the package lands
with Phase 160.
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
