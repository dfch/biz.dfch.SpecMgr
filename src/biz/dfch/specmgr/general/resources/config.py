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

"""Resource: specmgr://config -- resolved base directory diagnostics (feat-51-mcp-cwd).

The MCP server resolves every per-domain base directory relative to its own
process's current working directory unless a domain's own ``SPECMGR_*_DIR``
env var (or the shared ``SPECMGR_DOCS_DIR`` root most domains share) is
explicitly set. This resource lets a client self-diagnose
"am I pointed where I think I am?" by reporting, for every domain,
the resolved *absolute* base directory and whether the relevant env var was
explicitly set -- without requiring shell access to the server's host
(REQ-001/ACC-001).

**Never discloses arbitrary environment variables (REQ-002/ACC-002).** Only
the known ``SPECMGR_*_DIR`` env var *names* are read here, and only
their *presence* (``os.environ.get(name) is not None``), never their value
and never any other environment variable -- this module never iterates over
or dumps ``os.environ`` wholesale. Two deliberate, user-requested additions
for the similarity section (feat-134 Phase 7, REQ-013): the *presence* of
``SPECMGR_SIMILARITY_DISABLED`` is likewise reported (flag only, never its
value, the same convention), and ``FASTEMBED_CACHE_PATH`` is read to report
the *resolved* model cache directory (a path, by design -- the client needs
to know where the model is cached; unset or empty falls back to the default
``<tempdir>/fastembed_cache``). A third presence flag,
``SPECMGR_FEAT_WARMUP_DISABLED`` (feat-187-list-feat-timeout, Task 110.120,
ADR 3982712a-a46b-4b2b-809f-9c6925a49b44), is reported the same way --
whether the unified startup warmup's ``feat`` frontmatter/full-parse phases
are disabled.

Read-only, like every other domain's own ``*_base_dir()`` -- this resource
never creates a directory as a side effect of being read (it never calls any
``ensure_*_base_dir()``), and it never imports ``fastembed`` (the
``similarity`` extra may not be installed; the extra-installed check is a
``importlib.util.find_spec`` spec lookup only, ACC-018).

**Static similarity section (feat-134 Phase 7, REQ-013).** The payload
additionally carries a ``similarity`` section (``SimilarityConfig``):
whether the ``similarity`` extra (``fastembed``) is installed, whether the
presence-based ``SPECMGR_SIMILARITY_DISABLED`` opt-out flag is set, the
fixed model name (the shared ``SIMILARITY_MODEL_NAME`` constant, the same
single source ``get_default_provider()`` reads, ACC-020), and the resolved
model cache directory. Static configuration only: the tools' own dynamic
runtime availability (whether the model is loaded/usable right now) is
their structured ``{available, reason, message}`` result, not part of this
resource -- it deliberately reports no ``loaded`` or other runtime state.

**Static plantuml section (feat-185-uc-diagrams Phase 120).** The payload
additionally carries a ``plantuml`` section (``PlantumlConfig``): the
**presence-only** state of the exactly-three PlantUML validation-source env
vars (``SPECMGR_PLANTUML_JAR``/``SPECMGR_PLANTUML_BIN``/
``SPECMGR_PLANTUML_URL`` -- rulebook §3.1; each reported as ``{set: bool}``,
never its value: a jar path, a bin path, or a server URL would be a
disclosure violation of REQ-002's own contract), plus ``selected`` -- the
first-set-wins selection over the three (rulebook §3.2, derived from
``plantuml.chain.select_source``; ``"none"`` when all are unset, the
structure-only floor). Static configuration only, like ``similarity``:
whether the selected source actually *answers its canary right now* is the
``validate_plantuml`` tool's own ``source_state``/``available`` result, not
part of this resource.
"""

from __future__ import annotations

import os
import tempfile
from importlib.util import find_spec
from pathlib import Path

from ... import _envregistry
from ...adr.tools._paths import ADR_DIR_ENV_VAR, adr_base_dir
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from ...general.tools._doc_paths import DOCS_DIR_ENV_VAR
from ...general.tools._domains import ALL_DOMAINS
from ...general.tools._embedding import SIMILARITY_DISABLED_ENV_VAR, SIMILARITY_MODEL_NAME
from ...general.tools._startup_warmup import FEAT_WARMUP_DISABLED_ENV_VAR
from ...gol.tools._paths import gol_base_dir
from ...models import ConfigInfo, DomainConfig, PlantumlConfig, PlantumlSourceConfig, SimilarityConfig
from ...plantuml.chain import ENV_VAR_BIN, ENV_VAR_JAR, ENV_VAR_URL, select_source
from ...prb.tools._paths import prb_base_dir
from ...qa.tools._paths import qa_base_dir
from ...req.tools._paths import req_base_dir
from ...rsk.tools._paths import rsk_base_dir
from ...server import mcp
from ...sop.tools._paths import sop_base_dir
from ...sysrs.tools._paths import sysrs_base_dir
from ...tsk.tools._paths import tsk_base_dir
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._paths import vcr_base_dir


#: The third-party environment variable that overrides the similarity
#: feature's model cache directory (``fastembed``'s own
#: ``FASTEMBED_CACHE_PATH``), read by :func:`_similarity_cache_dir` below.
FASTEMBED_CACHE_PATH_ENV_VAR = "FASTEMBED_CACHE_PATH"

# The registry record for :data:`FASTEMBED_CACHE_PATH_ENV_VAR` (feat-208,
# Phase 110), registered at its read site: the default is the code's own
# fallback expression, evaluated at registration -- an unset or empty
# value falls back to ``<tempdir>/fastembed_cache`` (the
# ``empty_falls_back_to_default`` flag; one of the four empty-fallback
# variables, the user-approved Option A decision recorded in the feature
# plan's 2026-10-10 update entry).
_envregistry.register(
    FASTEMBED_CACHE_PATH_ENV_VAR,
    default=str(Path(tempfile.gettempdir()) / "fastembed_cache"),
    description=(
        "Cache directory for the semantic-similarity feature's embedding model (the fastembed "
        "BAAI/bge-small-en-v1.5): set to a directory to cache the model there; an unset or empty "
        "value falls back to the default <tempdir>/fastembed_cache. Unset by default. The resolved "
        "directory is reported by the similarity section of the specmgr://config resource."
    ),
    owner="general/similarity",
    format="filepath",
    empty_falls_back_to_default=True,
)


def _similarity_cache_dir() -> str:
    """The resolved similarity model cache directory the resource reports (feat-134 Phase 7, REQ-013).

    Mirrors ``fastembed.common.utils.define_cache_dir``'s own resolution
    algorithm -- ``FASTEMBED_CACHE_PATH`` if set, else
    ``<tempdir>/fastembed_cache`` -- minus its ``mkdir(parents=True,
    exist_ok=True)`` side effect: reading ``specmgr://config`` must never
    create a directory (the resource's own no-side-effects contract,
    ACC-018). The duplication is deliberate, since this module must not
    import ``fastembed`` (the ``similarity`` extra may not even be
    installed); it is also the drift watchpoint -- a future ``fastembed``
    release that changes ``define_cache_dir``'s resolution logic would
    silently desync this helper, so keep the two in step on a
    ``fastembed`` version bump.

    Returns:
        The cache directory as an absolute path string (an unset or
        empty ``FASTEMBED_CACHE_PATH`` falls back to the default, so the
        result is always absolute); the directory is never created here.
    """
    cache_dir = os.environ.get("FASTEMBED_CACHE_PATH") or str(Path(tempfile.gettempdir()) / "fastembed_cache")
    result = str(Path(cache_dir).resolve())
    return result


@mcp.resource(
    "specmgr://config",
    name="config",
    title="SpecMgr Resolved Base Directory Configuration",
    description=(
        "For every document domain ("
        f"{', '.join(ALL_DOMAINS)}), the resolved absolute base directory and whether the domain's "
        "SPECMGR_*_DIR environment variable is explicitly set, plus a static `similarity` section for "
        "the semantic-similarity feature (feat-134): whether the `similarity` extra (fastembed) is "
        "installed (a spec lookup, never an import), whether the presence-based SPECMGR_SIMILARITY_DISABLED "
        "opt-out flag is set, the fixed model name, and the resolved model cache directory "
        "(FASTEMBED_CACHE_PATH if set, else <tempdir>/fastembed_cache, reported but never created), plus "
        "whether the presence-based SPECMGR_FEAT_WARMUP_DISABLED opt-out flag is set (the unified startup "
        "warmup's feat frontmatter/full-parse phases, feat-187-list-feat-timeout), and a static `plantuml` "
        "section for the PlantUML validation source (feat-185-uc-diagrams Phase 120): the presence-only "
        "state of the exactly-three source env vars "
        "(SPECMGR_PLANTUML_JAR/SPECMGR_PLANTUML_BIN/SPECMGR_PLANTUML_URL, each {set: bool}, never a "
        'value) plus `selected` -- the first-set-wins selection over them ("jar"/"bin"/"url"/'
        '"none"). Static configuration only -- the tools\' own dynamic runtime availability is '
        "their structured {available, reason, message} result, not part of this resource. Never "
        "discloses the value of any environment variable except the resolved cache path, only "
        "whether the relevant directory-path/opt-out env vars are present."
    ),
    mime_type="application/json",
)
def config_info() -> ConfigInfo:
    """
    Return the resolved base directory and env-var-set flag for every domain, plus the similarity and
    plantuml sections and the feat_warmup_disabled flag.

    Explicitly enumerates the known ``SPECMGR_*_DIR`` env var names and
    reads only those from the environment (REQ-002) -- ``adr`` and ``feat``
    each have their own dedicated env var; every other domain (``req``,
    ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
    ``vcr``, ``sysrs``) shares the one root ``SPECMGR_DOCS_DIR`` env var,
    so their ``env_var``/``env_var_set`` fields are identical by design, not
    a bug.

    The ``similarity`` section (feat-134 Phase 7, REQ-013) is static
    configuration only: ``find_spec("fastembed")`` (a spec lookup, never an
    import) for ``extra_installed``, the presence-based
    ``SPECMGR_SIMILARITY_DISABLED`` flag for ``disabled``, the shared
    ``SIMILARITY_MODEL_NAME`` constant for ``model_name``, and
    :func:`_similarity_cache_dir` for ``cache_dir`` -- reported, never
    created (ACC-018). The tools' own dynamic availability (whether the
    model is loaded/usable right now) is deliberately not part of this
    payload; it is their structured ``{available, reason, message}``
    result.

    The ``plantuml`` section (feat-185-uc-diagrams Phase 120) is static
    configuration only: the **presence** of each of the exactly-three
    validation-source env vars (``os.environ.get(var) is not None`` --
    never a value), plus ``selected``, derived from
    ``plantuml.chain.select_source`` (the rulebook §3.2 first-set-wins
    order JAR → BIN → URL; ``"none"`` when all three are unset). The
    ``validate_plantuml`` tool's own dynamic availability (whether the
    selected source answers its canary right now) is deliberately not part
    of this payload; it is that tool's ``source_state``/``available``
    result.

    ``feat_warmup_disabled`` (feat-187-list-feat-timeout, Task 110.120, ADR
    3982712a-a46b-4b2b-809f-9c6925a49b44) follows the same presence-only
    convention: whether ``SPECMGR_FEAT_WARMUP_DISABLED`` is set, gating the
    unified startup warmup thread's ``feat`` frontmatter/full-parse phases.

    Returns
    -------
    ConfigInfo
        The resolved base directory configuration for every domain, plus
        the static similarity section, the static plantuml section, and
        the feat_warmup_disabled flag.
    """
    docs_dir_set = os.environ.get(DOCS_DIR_ENV_VAR) is not None

    domains = {
        "adr": DomainConfig(
            base_dir=str(adr_base_dir().resolve()),
            env_var=ADR_DIR_ENV_VAR,
            env_var_set=os.environ.get(ADR_DIR_ENV_VAR) is not None,
        ),
        "req": DomainConfig(
            base_dir=str(req_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "uc": DomainConfig(
            base_dir=str(uc_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "tsk": DomainConfig(
            base_dir=str(tsk_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "qa": DomainConfig(
            base_dir=str(qa_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "prb": DomainConfig(
            base_dir=str(prb_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "gol": DomainConfig(
            base_dir=str(gol_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "rsk": DomainConfig(
            base_dir=str(rsk_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "dec": DomainConfig(
            base_dir=str(dec_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "sop": DomainConfig(
            base_dir=str(sop_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "feat": DomainConfig(
            base_dir=str(feat_base_dir().resolve()),
            env_var=FEAT_DIR_ENV_VAR,
            env_var_set=os.environ.get(FEAT_DIR_ENV_VAR) is not None,
        ),
        "vcr": DomainConfig(
            base_dir=str(vcr_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
        "sysrs": DomainConfig(
            base_dir=str(sysrs_base_dir().resolve()),
            env_var=DOCS_DIR_ENV_VAR,
            env_var_set=docs_dir_set,
        ),
    }

    assert set(domains) == set(ALL_DOMAINS), (
        "the specmgr://config domains dict drifted from the shared general.tools._domains.ALL_DOMAINS "
        "source -- add or remove the domain in both places (feat-125-domain-lists, REQ-007)"
    )

    similarity = SimilarityConfig(
        extra_installed=find_spec("fastembed") is not None,
        disabled=os.environ.get(SIMILARITY_DISABLED_ENV_VAR) is not None,
        model_name=SIMILARITY_MODEL_NAME,
        cache_dir=_similarity_cache_dir(),
    )

    # the static plantuml section (feat-185-uc-diagrams Phase 120): presence-only
    # over the exactly-three source env vars, `selected` per the rulebook §3.2
    # first-set-wins order (select_source returns (kind, value); only the kind
    # is reported -- the value would be a disclosure violation, REQ-002).
    selected = select_source()
    plantuml = PlantumlConfig(
        jar=PlantumlSourceConfig(set=os.environ.get(ENV_VAR_JAR) is not None),
        bin=PlantumlSourceConfig(set=os.environ.get(ENV_VAR_BIN) is not None),
        url=PlantumlSourceConfig(set=os.environ.get(ENV_VAR_URL) is not None),
        selected=selected[0] if selected is not None else "none",
    )

    result = ConfigInfo(
        domains=domains,
        similarity=similarity,
        plantuml=plantuml,
        feat_warmup_disabled=os.environ.get(FEAT_WARMUP_DISABLED_ENV_VAR) is not None,
    )
    return result
