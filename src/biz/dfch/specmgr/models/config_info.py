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
semantic-similarity feature (feat-134 Phase 7, REQ-013): :class:`SimilarityConfig`
-- and, since feat-185-uc-diagrams Phase 120, the static ``plantuml`` section
(the presence-only state of the exactly-three validation-source env vars plus
the first-set-wins ``selected`` source): :class:`PlantumlConfig`.

feat-187-list-feat-timeout, Task 110.120: :class:`ConfigInfo` additionally
carries ``feat_warmup_disabled``, the presence of the new
``SPECMGR_FEAT_WARMUP_DISABLED`` opt-out flag (ADR
3982712a-a46b-4b2b-809f-9c6925a49b44) -- a single top-level boolean field,
not a new nested model, since it is the one additional fact this feature
needs to report and does not warrant its own section the way the
similarity feature's richer static configuration did.
"""

from __future__ import annotations

from typing import Literal

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


class PlantumlSourceConfig(BaseModel):
    """One of the exactly-three PlantUML validation-source env vars (feat-185-uc-diagrams Phase 120).

    Presence-only, mirroring :class:`DomainConfig`'s ``env_var_set``
    convention (the resource's own no-disclosure contract, feat-51-mcp-cwd
    REQ-002): whether the variable is set in the current process
    environment (``os.environ.get(name) is not None``) -- never its *value*
    (a jar path, a bin path, or a server URL would be disclosed by it).

    Parameters
    ----------
    set:
        Whether the env var is present (any value; presence-based, never
        the value).
    """

    set: bool


class PlantumlConfig(BaseModel):
    """The static ``plantuml`` section of ``specmgr://config`` (feat-185-uc-diagrams Phase 120).

    The presence-only state of the exactly-three validation-source env vars
    (rulebook §3.1: ``SPECMGR_PLANTUML_JAR`` → ``SPECMGR_PLANTUML_BIN`` →
    ``SPECMGR_PLANTUML_URL``) plus :data:`selected`, the first-set-wins
    selection over them (rulebook §3.2, ``plantuml.chain.select_source``) --
    ``"none"`` when all three are unset (the structure-only floor).
    Presence-only throughout: no value of any of the three vars is ever
    reported.

    Parameters
    ----------
    jar:
        The presence of ``SPECMGR_PLANTUML_JAR``: :class:`PlantumlSourceConfig`.
    bin:
        The presence of ``SPECMGR_PLANTUML_BIN``: :class:`PlantumlSourceConfig`.
    url:
        The presence of ``SPECMGR_PLANTUML_URL``: :class:`PlantumlSourceConfig`.
    selected:
        The selected validation source per the §3.2 first-set-wins order:
        ``"jar"``, ``"bin"``, ``"url"``, or ``"none"`` (all unset).
    """

    jar: PlantumlSourceConfig
    bin: PlantumlSourceConfig
    url: PlantumlSourceConfig
    selected: Literal["jar", "bin", "url", "none"]


class ConfigInfo(BaseModel):
    """Resolved base directory configuration for every document domain, plus the similarity and plantuml
    sections and the feat_warmup_disabled flag.

    Parameters
    ----------
    domains:
        A mapping of domain name (``"adr"``, ``"req"``, ``"uc"``, ``"tsk"``,
        ``"qa"``, ``"prb"``, ``"gol"``, ``"rsk"``, ``"dec"``, ``"sop"``,
        ``"feat"``, ``"vcr"``, ``"sysrs"``) to that domain's :class:`DomainConfig`.
    similarity:
        The static configuration of the semantic-similarity feature
        (feat-134 Phase 7, REQ-013): :class:`SimilarityConfig`.
    plantuml:
        The static configuration of the PlantUML validation source
        (feat-185-uc-diagrams Phase 120): :class:`PlantumlConfig` --
        presence-only (never a value of the three env vars).
    feat_warmup_disabled:
        Whether the presence-based ``SPECMGR_FEAT_WARMUP_DISABLED`` opt-out
        flag is set in the current process environment (any value;
        presence-based, never the value -- the same convention
        ``SimilarityConfig.disabled`` already follows). When set, the
        unified startup warmup thread's ``feat`` frontmatter/full-parse
        phases never run (feat-187-list-feat-timeout, Task 110.120, ADR
        3982712a-a46b-4b2b-809f-9c6925a49b44).
    """

    domains: dict[str, DomainConfig]
    similarity: SimilarityConfig
    plantuml: PlantumlConfig
    feat_warmup_disabled: bool
