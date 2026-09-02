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

"""Vulture whitelist: known false positives, grouped by why they're false positives.

Vulture (https://github.com/jendrikseipp/vulture) does pure static/AST analysis, so
it cannot see names that are only ever invoked through a framework's own decorator
or metaclass machinery (Pydantic validators, MCP resource/tool registration, Typer
callbacks) rather than a direct Python call. This file is fed to vulture alongside
``src/`` (see the ``vulture`` pre-commit hook and ``pyproject.toml``); any name
referenced here is treated as "used" everywhere it's defined in the scanned code,
by name, not by file/line -- so each name below is listed once even if several
unrelated classes each define their own method/field of that name.

Do not add a name here just to silence a finding: confirm first (grep for the
name/decorator) that it's a genuine framework false positive, not real dead code.
Genuine dead code found by vulture should be deleted instead.
"""

# --- Typer CLI callback pattern -------------------------------------------------
# Registered as `@app.callback()`, never called directly. Kept even with a single
# `@app.command()` -- see AGENTS.md's "CLI (cli.py)" section for why Typer needs it.
_callback

# --- Pydantic v2 `@field_validator`/`@model_validator` methods -------------------
# Invoked by Pydantic's validation machinery on model construction, not by any
# direct call in this codebase.
_._default_blank_status_to_draft
_._default_blank_status_to_open
_._default_blank_status_to_planning
_._optional_blank_to_none
_._validate_date_time_format
_._required_non_blank
_._validate_items_eagerly
_._validate_newest_first
_._validate_ac_numbers_unique
_._validate_option_numbers_unique
_._validate_step_numbers_unique
_._validate_partial_title
_._validate_status
_._validate_type_non_blank
_._validate_value
_._validate_version
_.validate_actions_numbered_sequentially
_.validate_heading_structure
_.validate_headings
_.validate_level
_.validate_status
_.validate_step_references_resolve_and_are_unique
_.validate_steps_numbered_contiguously

# --- Pydantic `model_config = ConfigDict(...)` class attribute -------------------
# Read by Pydantic's metaclass, never accessed directly from our code.
model_config

# --- Pydantic model fields read only via (de)serialization/rendering -------------
# Round-tripped through `model_dump()`/parsing/markdown rendering rather than
# accessed as a plain Python attribute anywhere in `src/` today.
acceptance_criteria
assumptions
channels_to_primary_actor
channels_to_secondary_actors
characteristics
classification
comment
created
decisions
failed_end_condition
frequency
goal_in_context
goals
notes
open_issues
performance_target
preconditions
priority
ref
related_artifacts
related_information
related_use_cases
requirements
results
scope
source
specmgr
statement
sub_characteristics
success_end_condition
tags
trigger
truncated
precondition
intro
checked
recent_updates
updates
cause
consequence
initial_assessment
initial_level
residual_level
residual_probability
residual_impact
residual_product
strategy
mitigation
residual_assessment
owner
answer
compatibility
elicitation_context
flexibility
functional_suitability
general
interaction_capability
introduction
maintainability
performance_efficiency
question
questions
raw_requirements
reliability
requirement
safety
security
current_state
future_state
gap
impact
question_1
question_2
question_3
question_4
question_5
question_6
question_7
summary
# dec (feat-21 Phase 1): `Decision` fields read only via (de)serialization;
# nothing in `src/` accesses them as plain attributes yet.
context
drivers
considered
outcome
# sop (feat-30 Phase 1): `Sop`/`RolesAndResponsibilities`/`RelatedArtifacts`/
# `UpdateEntry` fields (and the `UpdateEntry.timestamp` `@computed_field`) read
# only via (de)serialization; nothing in `src/` accesses them as plain
# attributes yet (the `sop` tools come in Phase 2). `timestamp` is a
# `@computed_field` evaluated only on access/serialization, like `Option.number`.
accountable
responsible
support
sops
timestamp
purpose
definitions
roles_and_responsibilities
safety_and_precautions
# feat (feat-31 Phase 1): `Feature`/`Plan`/`Progress` fields read only via
# (de)serialization; nothing in `src/` accesses them as plain attributes yet.
plan
progress
overview
dependencies
design_notes
related_decisions
task_list
included
explicitly_out_of_scope
depends_on
phases
current_status
blockers
decisions_made
related_prs_commits
# vcr (feat-33 Phase 1): `Vcr`/`AcceptanceCriterion` fields read only via
# (de)serialization; nothing in `src/` accesses them as plain attributes yet.
verifies
test_steps
# config (feat-51-mcp-cwd Phase 1): `DomainConfig` fields read only via
# (de)serialization; nothing in `src/` accesses them as plain attributes yet.
env_var
env_var_set

# --- MCP `@mcp.resource(...)`/`@mcp.tool()` entry points -------------------------
# Invoked by the MCP framework once registered, not called directly in `src/`.
version_info
config_info
