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

"""Markdown base models."""

from .alias_type import AliasType
from .markdown import markdown
from .alias import alias
from .markdown_str import MarkdownStr
from .markdown_section import MarkdownSection
from .markdown_section1 import MarkdownSection1
from .markdown_section2 import MarkdownSection2
from .markdown_section3 import MarkdownSection3
from .markdown_section4 import MarkdownSection4
from .markdown_section5 import MarkdownSection5
from .markdown_section6 import MarkdownSection6

__all__ = [
    "markdown",
    "alias",
    "AliasType",
    "MarkdownStr",
    "MarkdownSection",
    "MarkdownSection1",
    "MarkdownSection2",
    "MarkdownSection3",
    "MarkdownSection4",
    "MarkdownSection5",
    "MarkdownSection6",
]
