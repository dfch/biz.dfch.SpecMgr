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

Phase 100 state: the ``models`` sub-package is implemented (see
``txt/models``); the ``tools``/``resources``/``prompts``/``data``
sub-packages are empty placeholders for the later phases. This module is a
docstring-only placeholder with no imports of its own (the ``qa``
first-phase precedent, feat-12): importing it must never force the
``mcp`` extra onto a base-library consumer, and the ``@mcp.tool()``/
``@mcp.resource()``/``@mcp.prompt()`` registrations come with the later
phases' own sub-package ``__init__`` files.
"""
