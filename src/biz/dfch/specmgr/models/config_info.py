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

"""Pydantic models for the ``specmgr://config`` resource (feat-51-mcp-cwd REQ-001).

Also carries the static ``similarity`` section the resource reports for the
semantic-similarity feature (feat-134 Phase 7, REQ-013): :class:`SimilarityConfig`.
"""

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
        for the other domains rooted under it).
    env_var_set:
        Whether ``env_var`` is explicitly set in the current process
        environment (``os.environ.get(env_var) is not None``) -- never the
        env var's *value*, only whether it is present (REQ-002).
    """

    base_dir: str
    env_var: str
    env_var_set: bool


class SimilarityConfig(BaseModel):
    """Static configuration of the semantic-similarity feature (feat-134 Phase 7, REQ-013).

    Static facts only: the two similarity tools' own *dynamic*
    runtime availability (whether the model is loaded/usable right now)
    is their structured ``{available, reason, message}`` result, not part
    of this model -- the resource deliberately reports no ``loaded`` or
    other runtime state (keeping ``specmgr://config`` side-effect-free).

    Parameters
    ----------
    extra_installed:
        Whether the ``similarity`` extra (the ``fastembed`` backend
        package) is installed -- checked via ``importlib.util.find_spec``
        (a spec lookup, never an import of ``fastembed`` itself).
    disabled:
        Whether the presence-based ``SPECMGR_SIMILARITY_DISABLED`` opt-out
        flag is set in the current process environment (any value;
        presence-based, never the value -- the repo's own env-flag
        convention).
    model_name:
        The fixed embedding model name -- read from the shared
        ``general.tools._embedding.SIMILARITY_MODEL_NAME`` constant, the
        single source both ``get_default_provider()`` and this field use
        (ACC-020).
    cache_dir:
        The resolved model cache directory (``FASTEMBED_CACHE_PATH`` if
        set, else ``<tempdir>/fastembed_cache``) as an absolute path
        string -- reported, never created (reading the resource is
        side-effect-free, ACC-018).
    """

    extra_installed: bool
    disabled: bool
    model_name: str
    cache_dir: str


class ConfigInfo(BaseModel):
    """Resolved base directory configuration for every document domain, plus the similarity section.

    Parameters
    ----------
    domains:
        A mapping of domain name (``"adr"``, ``"req"``, ``"uc"``, ``"tsk"``,
        ``"qa"``, ``"prb"``, ``"gol"``, ``"rsk"``, ``"dec"``, ``"sop"``,
        ``"feat"``, ``"vcr"``, ``"sysrs"``) to that domain's :class:`DomainConfig`.
    similarity:
        The static configuration of the semantic-similarity feature
        (feat-134 Phase 7, REQ-013): :class:`SimilarityConfig`.
    """

    domains: dict[str, DomainConfig]
    similarity: SimilarityConfig
