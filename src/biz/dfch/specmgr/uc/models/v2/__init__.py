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

"""Use Case models v2 -- rebuilt on `feat-5-md-model-parser`'s generic `models/md` engine.

See `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py` for the design sketch this
package implements, and `uc/models/v1/` for the original, still-current
custom-parser implementation this package is not yet a drop-in replacement for
(no `parse_uc`/`render_uc_diagram`/compound-numbering validation ported yet).
"""

from .document import UcDocument
from .frontmatter import UcFrontmatter
from .use_case import (
    Assumptions,
    ChannelsToPrimaryActor,
    ChannelsToSecondaryActors,
    CharacteristicInformation,
    Extension,
    ExtensionItem,
    Extensions,
    FailedEndCondition,
    Frequency,
    GoalInContext,
    Level,
    MainSuccessScenario,
    Notes,
    OpenIssues,
    PerformanceTarget,
    Precondition,
    Priority,
    PrimaryActor,
    RelatedInformation,
    RelatedUseCases,
    Scope,
    SecondaryActors,
    SubVariation,
    SubVariations,
    SuccessEndCondition,
    Trigger,
    UseCase,
)

__all__ = [
    "Assumptions",
    "ChannelsToPrimaryActor",
    "ChannelsToSecondaryActors",
    "CharacteristicInformation",
    "Extension",
    "ExtensionItem",
    "Extensions",
    "FailedEndCondition",
    "Frequency",
    "GoalInContext",
    "Level",
    "MainSuccessScenario",
    "Notes",
    "OpenIssues",
    "PerformanceTarget",
    "Precondition",
    "Priority",
    "PrimaryActor",
    "RelatedInformation",
    "RelatedUseCases",
    "Scope",
    "SecondaryActors",
    "SubVariation",
    "SubVariations",
    "SuccessEndCondition",
    "Trigger",
    "UcDocument",
    "UcFrontmatter",
    "UseCase",
]
