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
env var (or the shared ``SPECMGR_DOCS_DIR`` root ten of the twelve domains
share) is explicitly set. This resource lets a client self-diagnose "am I
pointed where I think I am?" by reporting, for all twelve domains, the
resolved *absolute* base directory and whether the relevant env var was
explicitly set -- without requiring shell access to the server's host
(REQ-001/ACC-001).

**Never discloses arbitrary environment variables (REQ-002/ACC-002).** Only
the twelve known ``SPECMGR_*_DIR`` env var *names* are read here, and only
their *presence* (``os.environ.get(name) is not None``), never their value
and never any other environment variable -- this module never iterates over
or dumps ``os.environ`` wholesale.

Read-only, like every other domain's own ``*_base_dir()`` -- this resource
never creates a directory as a side effect of being read (it never calls any
``ensure_*_base_dir()``).
"""

from __future__ import annotations

import os

from ...adr.tools._paths import ADR_DIR_ENV_VAR, adr_base_dir
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from ...general.tools._doc_paths import DOCS_DIR_ENV_VAR
from ...gol.tools._paths import gol_base_dir
from ...models import ConfigInfo, DomainConfig
from ...prb.tools._paths import prb_base_dir
from ...qa.tools._paths import qa_base_dir
from ...req.tools._paths import req_base_dir
from ...rsk.tools._paths import rsk_base_dir
from ...server import mcp
from ...sop.tools._paths import sop_base_dir
from ...tsk.tools._paths import tsk_base_dir
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._paths import vcr_base_dir


@mcp.resource(
    "specmgr://config",
    name="config",
    title="SpecMgr Resolved Base Directory Configuration",
    description=(
        "For all twelve document domains (adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, "
        "vcr), the resolved absolute base directory and whether the domain's SPECMGR_*_DIR "
        "environment variable is explicitly set. Never discloses the value of any environment "
        "variable, only whether the relevant directory-path env var is present."
    ),
    mime_type="application/json",
)
def config_info() -> ConfigInfo:
    """
    Return the resolved base directory and env-var-set flag for every domain.

    Explicitly enumerates the known ``SPECMGR_*_DIR`` env var names and
    reads only those from the environment (REQ-002) -- ``adr`` and ``feat``
    each have their own dedicated env var; the other ten domains (``req``,
    ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
    ``vcr``) all share the one root ``SPECMGR_DOCS_DIR`` env var, so their
    ``env_var``/``env_var_set`` fields are identical by design, not a bug.

    Returns
    -------
    ConfigInfo
        The resolved base directory configuration for all twelve domains.
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
    }

    result = ConfigInfo(domains=domains)
    return result
