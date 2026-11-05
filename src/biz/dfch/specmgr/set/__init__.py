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

"""Set (SET) domain -- a convenience bundle of one or more artifacts of any (mixed) type.

This is a domain-first package (per DEC ece4554b-725c-4f76-bc04-5d2b760363d2),
mirroring ``txt``'s layout, containing models, tools, prompts, and resources
for managing ``set`` documents. A ``set`` document bundles one or more
already-existing specmgr artifacts of any (mixed) type via forward
references only: a single ``# {title}`` H1, a mandatory opaque free-markdown
``## Description`` introductory section (any blocks allowed), and a mandatory
``## Items`` flat bullet list (at least one ``<TAG> <uuid>: <title>`` bullet
from the shared 12-tag reference vocabulary in any mix, optional per-bullet
notes, duplicate ``(tag, id)`` pairs rejected). The items remain the source
of truth -- a set is a convenience bundle, and nothing in an item ever points
back to the set (``SET`` is not a reference tag). See
`.specmgr/feat/feat-173-req-iso29148-level-set/README.md` for the full design.

It is built on the generic ``models/md`` parser with the VCR simple surface --
dispatch-only from day one (DEC 36905d5b-8057-4294-8665-c7eed5534db0): no
per-domain ``update_set``/``set_status_set``/``validate_set``/``delete_set``
tools, no renderer -- writes persist the caller's raw validated body
byte-for-byte.

Import this package to register all set tools against the shared ``mcp``
application instance at once::

    from biz.dfch.specmgr import set  # noqa: F401 (side-effects only)

``tools`` (``create_set``, ``parse_set``, ``list_set``, ``get_set``
(``raw``/``offset``/``limit``/``numbered``), ``get_set_example``,
``get_set_template``, ``get_set_schema``) are implemented; whole-body and
line-range updates of an existing document go through the generic ``update``
tool in ``general.tools`` (``type="set"``), status changes through the
generic ``set_status`` tool in ``general.tools`` (``type="set"``), and
disk-free, id-free dry-run content validation through the generic
``validate`` tool in ``general.tools`` (``type="set"``). Like TXT, SET has
no ``specmgr://set/{id}`` resource --
id-based reads go through the ``get_set`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://set/list`` resource -- ``list_set`` ships as a paged
``@mcp.tool()`` from day one (DEC ec9f5262-9912-49d0-903f-fcfb54f28c13).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
