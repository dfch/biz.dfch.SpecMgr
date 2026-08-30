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

"""MCP tool wrappers for features (mirrors ``dec/tools/``'s own shape).

Bespoke, folder-per-document addressing (``_paths.py``, ``_io.py``,
``_lock.py``, ``_write.py`` -- *not* built on
``general/tools/_doc_paths.py``, since ``feat`` documents live one per
folder at ``<base>/<id>/README.md`` with a non-UUID id) underpins the eight
lifecycle tools below.

``parse_feat`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_feat_example`` returns a complete, valid
sample feature document as raw markdown; ``get_feat_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (the packaged
files themselves are Phase 3's job -- see each tool's own module docstring).
``get_feat`` reads, parses, and returns a full feature document by id -- the
sole id-based read path for FEAT (there is no ``specmgr://feat/{id}``
resource, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_feat`` returns
one page of id/title/status/ref/path summaries of every feature, shipped as
a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
``create_feat`` assigns the next ``feat-NNN-slug`` id, builds the
frontmatter itself, and writes a new document (body markdown only, no
frontmatter) under ``<base>/<id>/README.md`` (``feat.tools._paths``/
``_lock``/``_io``/``_write``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="feat"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="feat"``), also
bumping ``updated``, leaving the body untouched. There is no
``update_feat``/``set_status_feat`` tool of ``feat``'s own.
``delete_feat`` is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_feat`` is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all feature tools at once::

    from biz.dfch.specmgr.feat import tools  # noqa: F401 (side-effects only)
"""

from .create_feat import create_feat
from .delete_feat import delete_feat
from .get_feat import get_feat
from .get_feat_example import get_feat_example
from .get_feat_template import get_feat_template
from .list_feat import list_feat
from .parse_feat import parse_feat
from .validate_feat import validate_feat

__all__ = [
    "create_feat",
    "delete_feat",
    "get_feat",
    "get_feat_example",
    "get_feat_template",
    "list_feat",
    "parse_feat",
    "validate_feat",
]
