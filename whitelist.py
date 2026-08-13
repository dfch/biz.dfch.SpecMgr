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
_._optional_blank_to_none
_._required_non_blank
_._validate_partial_title
_._validate_status
_._validate_type_non_blank
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
related_artifacts
related_information
related_use_cases
requirements
scope
source
specmgr
statement
success_end_condition
tags
trigger
precondition
intro

# --- MCP `@mcp.resource(...)`/`@mcp.tool()` entry points -------------------------
# Invoked by the MCP framework once registered, not called directly in `src/`.
version_info
