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

"""Shared Confluence base-URL/bearer-token configuration, used by both
``confluence_fetch`` and (later) ``confluence_update``.

Extracted out of the former ``webfetch.py`` (ADR
a156fdf9-052c-4f43-93a2-eeec04a91eac) so both Confluence tools read the same
two environment variables (:data:`CONFLUENCE_BASE_URL_ENV_VAR`,
:data:`CONFLUENCE_BEARER_ENV_VAR`) through one place, mirroring this
codebase's existing ``_doc_paths.py``/``_path_safety.py``/``_splice.py``
shared-private-helper convention -- no ``pydantic-settings``, no in-memory
caching.
"""

from __future__ import annotations

import os

__all__ = [
    "CONFLUENCE_BASE_URL_ENV_VAR",
    "CONFLUENCE_BEARER_ENV_VAR",
    "ConfluenceNotConfiguredError",
    "confluence_config",
]

#: Environment variable holding the base URL that requested URLs must match.
CONFLUENCE_BASE_URL_ENV_VAR = "SPECMGR_CONFLUENCE_BASE_URL"

#: Environment variable holding the bearer token sent as the ``Authorization`` header.
CONFLUENCE_BEARER_ENV_VAR = "SPECMGR_CONFLUENCE_BEARER"


class ConfluenceNotConfiguredError(RuntimeError):
    """:data:`CONFLUENCE_BASE_URL_ENV_VAR` and/or :data:`CONFLUENCE_BEARER_ENV_VAR` are not set."""


def confluence_config() -> tuple[str, str]:
    """Return the configured ``(base_url, bearer_token)`` pair.

    Reads :data:`CONFLUENCE_BASE_URL_ENV_VAR` and :data:`CONFLUENCE_BEARER_ENV_VAR`
    directly from the environment on every call -- no caching, consistent with
    this codebase's "the environment is the sole source of truth" config
    style (mirrors ``adr.tools._paths.adr_base_dir``).

    Returns
    -------
    tuple[str, str]
        The configured ``(base_url, bearer_token)`` pair.

    Raises
    ------
    ConfluenceNotConfiguredError
        If either environment variable is unset or blank.
    """
    base_url = os.environ.get(CONFLUENCE_BASE_URL_ENV_VAR)
    bearer_token = os.environ.get(CONFLUENCE_BEARER_ENV_VAR)
    if not base_url or not bearer_token:
        raise ConfluenceNotConfiguredError(
            f"Confluence is not configured: both {CONFLUENCE_BASE_URL_ENV_VAR!r} and "
            f"{CONFLUENCE_BEARER_ENV_VAR!r} must be set as environment variables."
        )
    return base_url, bearer_token
