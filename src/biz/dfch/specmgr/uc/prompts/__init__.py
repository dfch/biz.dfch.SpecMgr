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

"""MCP prompt wrappers for Use Cases (feat-57-uc-commands).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``uc/tools/``/``uc/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. ``generate_uc_sequence_diagram`` (feat-185-uc-diagrams,
Phase 120) narrates the rulebook §3.8 agent flow for one use case's
sequence diagram: read-first rulebook, ``TodoWrite`` plan, ``get_uc``
(a ``ParseFailureResult`` stops the flow), the §2.11 Subfunction
judgment, ``get_uc_sequence_skeleton``, attribution of every
``UNATTRIBUTED`` marker (``question`` tool whenever not confident;
pre-filled arrows may be corrected), the zero-marker rule, the
``validate_plantuml`` loop (green at the highest available layer before
writing; ``source_state != ok`` with a source set => report and do not
write; all unset => the ``' validated: structure-only`` header), the
host-native ``diagrams/uc/<id>.sequence.puml`` write (no specmgr tool
writes ``.puml``), and never commit.
Import this package to register all UC prompts at once::

    from biz.dfch.specmgr.uc import prompts  # noqa: F401 (side-effects only)
"""

from .create_uc import create_uc
from .generate_uc_sequence_diagram import generate_uc_sequence_diagram
from .update_uc import update_uc

__all__ = [
    "create_uc",
    "generate_uc_sequence_diagram",
    "update_uc",
]
