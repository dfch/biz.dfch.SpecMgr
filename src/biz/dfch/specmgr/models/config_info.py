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

"""Pydantic models for the ``specmgr://config`` resource (feat-51-mcp-cwd REQ-001)."""

from __future__ import annotations

from pydantic import BaseModel


class DomainConfig(BaseModel):
    """Resolved base directory configuration for a single document domain.

    Parameters
    ----------
    base_dir:
        The domain's resolved, absolute base directory path.
    env_var:
        The name of the environment variable that can override ``base_dir``
        (e.g. ``"SPECMGR_ADR_DIR"``, or the shared ``"SPECMGR_DOCS_DIR"``
        for the ten domains rooted under it).
    env_var_set:
        Whether ``env_var`` is explicitly set in the current process
        environment (``os.environ.get(env_var) is not None``) -- never the
        env var's *value*, only whether it is present (REQ-002).
    """

    base_dir: str
    env_var: str
    env_var_set: bool


class ConfigInfo(BaseModel):
    """Resolved base directory configuration for every document domain.

    Parameters
    ----------
    domains:
        A mapping of domain name (``"adr"``, ``"req"``, ``"uc"``, ``"tsk"``,
        ``"qa"``, ``"prb"``, ``"gol"``, ``"rsk"``, ``"dec"``, ``"sop"``,
        ``"feat"``, ``"vcr"``) to that domain's :class:`DomainConfig`.
    """

    domains: dict[str, DomainConfig]
