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

"""Markdown section starting with h4 heading."""

from __future__ import annotations

from .markdown_section import MarkdownSection
from .markdown import markdown


@markdown(type="heading_open", tag="h4")
class MarkdownSection4(MarkdownSection):
    """Markdown content starting with an h4 heading.

    A heading deeper than h4 (level > 4, a nested subsection) is allowed
    and silently retained inside the section's extent, while a heading of
    the same or a higher level (level <= 4) ends the section. This is
    enforced procedurally by `MarkdownSection.get_extent`'s own stop
    condition plus `MarkdownStr.from_text`'s trailing-completeness check,
    not by any model validator (none exists).
    """
