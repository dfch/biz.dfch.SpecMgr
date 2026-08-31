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

"""Verification Case Record (VCR) domain -- how a REQ/UC is verified.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
still under construction: only ``vcr.models`` exists so far (Phase 1 --
``.specmgr/feat/feat-33-vcr/README.md``). Deliberately does **not** yet import
``tools``/``resources``/``prompts`` sub-packages -- those, and the resulting
``from biz.dfch.specmgr import vcr  # noqa: F401`` domain-registration
side-effect import, are Phase 2/3/4's job, not Phase 1's.
"""
