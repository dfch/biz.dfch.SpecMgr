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

"""System Requirements Specification (SYSRS) models -- Pydantic schema and parser powered by the generic
``models/md`` engine.

Mirrors ``sop/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``sysrs`` documents, and the one-line ``SysrsSummary`` for the paged
``list_sysrs`` tool.
"""

from .v1 import (
    SCHEMA_COMMENT_VERSION,
    Appendix,
    AssumptionsAndDependencies,
    BusinessContext,
    BusinessContextAndGoals,
    Compatibility,
    Decisions,
    DefinitionsAndAcronyms,
    EnvironmentalConditions,
    Flexibility,
    FunctionalSuitability,
    Goals,
    InformationManagement,
    InteractionCapability,
    Maintainability,
    MoreInformation,
    OperationalConceptAndScenarios,
    OtherCharacteristics,
    PackagingHandlingShippingAndTransportation,
    PerformanceEfficiency,
    PhysicalCharacteristics,
    PolicyAndRegulation,
    ProblemStatement,
    References,
    Reliability,
    Requirements,
    Risks,
    Safety,
    Security,
    StakeholderNeedsAndElicitation,
    SystemContext,
    SystemFunctions,
    SystemIntegration,
    SystemLifeCycleSustainment,
    SystemModesAndStates,
    SystemOverview,
    SystemPurpose,
    SystemScope,
    Sysrs,
    SysrsDocument,
    SysrsFrontmatter,
    SysrsSummary,
    UpdateEntry,
    Updates,
    UserCharacteristics,
    Verification,
    parse_sysrs,
)

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "Appendix",
    "AssumptionsAndDependencies",
    "BusinessContext",
    "BusinessContextAndGoals",
    "Compatibility",
    "Decisions",
    "DefinitionsAndAcronyms",
    "EnvironmentalConditions",
    "Flexibility",
    "FunctionalSuitability",
    "Goals",
    "InformationManagement",
    "InteractionCapability",
    "Maintainability",
    "MoreInformation",
    "OperationalConceptAndScenarios",
    "OtherCharacteristics",
    "PackagingHandlingShippingAndTransportation",
    "PerformanceEfficiency",
    "PhysicalCharacteristics",
    "PolicyAndRegulation",
    "ProblemStatement",
    "References",
    "Reliability",
    "Requirements",
    "Risks",
    "Safety",
    "Security",
    "StakeholderNeedsAndElicitation",
    "SystemContext",
    "SystemFunctions",
    "SystemIntegration",
    "SystemLifeCycleSustainment",
    "SystemModesAndStates",
    "SystemOverview",
    "SystemPurpose",
    "SystemScope",
    "Sysrs",
    "SysrsDocument",
    "SysrsFrontmatter",
    "SysrsSummary",
    "UpdateEntry",
    "Updates",
    "UserCharacteristics",
    "Verification",
    "parse_sysrs",
]
