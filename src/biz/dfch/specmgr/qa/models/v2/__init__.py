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

Alongside (not replacing on disk) `qa/models/v1/`, this package models a QA
body where many question/answer pairs can appear directly one after another
inside a single ISO/IEC 25010:2023 characteristic section -- see
`.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md` for the full design.

As of Phase 2, `question_answer.py`'s `QaAnswer`/`QaQuestionAnswer` and
`body.py`'s `General`/`Introduction`/`RawRequirements`/`MoreInformation`/
`ElicitationContext`/the 9 ISO/IEC 25010:2023 characteristic subclasses/`Qa`
are implemented and exported here (`_QaCategory` stays private/un-exported,
mirroring `qa/models/v1/__init__.py`'s own choice). Later phases extend this
package (and this `__init__.py`) with the version gate and a `QaFrontmatter`
re-export (imported unchanged from `qa/models/v1/`).
"""

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
from .question_answer import QaAnswer, QaQuestionAnswer

__all__ = [
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
    "QaQuestionAnswer",
    "RawRequirements",
    "Reliability",
    "Safety",
    "Security",
]
