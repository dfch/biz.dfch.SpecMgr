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

"""Question and Answer (QA) v2 models -- adjacent question/answer pairs, no per-question heading.

This package models a QA body where many question/answer pairs can appear
directly one after another inside a single ISO/IEC 25010:2023 characteristic
section -- see `.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md` for the
full design. As of feat-14 Phase 8, this is QA's only schema: the earlier
`qa/models/v1/` package (one `### {heading}` H3 per question/answer pair) has
been removed entirely now that every QA MCP tool/resource/prompt is
repointed at v2.

`question_answer.py`'s `QaAnswer`/`QaQuestionAnswer`, `body.py`'s
`General`/`Introduction`/`RawRequirements`/`MoreInformation`/
`ElicitationContext`/the 9 ISO/IEC 25010:2023 characteristic subclasses/`Qa`,
`frontmatter.py`'s `QaFrontmatter`, `summary.py`'s `QaSummary`,
`document.py`'s `QaDocument` (pairing `Qa` with `QaFrontmatter`), and
`parser.py`'s `parse_qa` -- the shared QA parsing entry point -- are all
implemented and exported here (`_QaCategory` stays private/un-exported).

**No `version`-based dispatch/gate exists** (REQ-004/ACC-004 revised
2026-08-23, see the feature README's Decisions Made): `QaFrontmatter.version`
was found to encode the shared `models.md` parsing engine's own schema
version (hardcoded to major 1), not a per-document-type body-schema version,
so no major-2 dispatch is possible. `parse_qa` mirrors
`uc/models/v2/parser.py::parse_uc`'s unconditional-v2-parsing shape exactly
instead -- a v1-shaped document simply fails naturally with whatever
structural error `Qa.from_text`/`QaFrontmatter.model_validate` raises on its
own.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    Compatibility,
    ElicitationContext,
    Flexibility,
    FunctionalSuitability,
    General,
    InteractionCapability,
    Introduction,
    Maintainability,
    MoreInformation,
    PerformanceEfficiency,
    Qa,
    RawRequirements,
    Reliability,
    Safety,
    Security,
)
from .document import QaDocument
from .frontmatter import QaFrontmatter
from .parser import parse_qa
from .question_answer import QaAnswer, QaQuestionAnswer
from .summary import QaSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "Compatibility",
    "ElicitationContext",
    "Flexibility",
    "FunctionalSuitability",
    "General",
    "InteractionCapability",
    "Introduction",
    "Maintainability",
    "MoreInformation",
    "PerformanceEfficiency",
    "Qa",
    "QaAnswer",
    "QaDocument",
    "QaFrontmatter",
    "QaQuestionAnswer",
    "QaSummary",
    "RawRequirements",
    "Reliability",
    "Safety",
    "Security",
    "parse_qa",
]
