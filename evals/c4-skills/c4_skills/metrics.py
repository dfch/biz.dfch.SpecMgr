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

"""Trial metrics (Task 100.140).

The metrics combine the parsed event stream (agent behaviour) with the
grader inputs (the real CLI facts about the produced workspace). Everything
here is pure -- the runner calls :func:`compute_metrics` once per trial.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from .events import VALIDATE_OK_MARKER, ParsedTrial, ToolCall
from .graders import GraderInputs, relationship_technology_coverage

# ---------------------------------------------------------------------------
# classification constants
# ---------------------------------------------------------------------------

#: The MCP tool suffixes the metrics count (the server prefix is variable).
SUFFIX_PARSE = "parse"
SUFFIX_VALIDATE = "validate"
SUFFIX_INSPECT = "inspect"
SUFFIX_EXPORT = "export"

#: Findings that cannot be cleared under the MCP (it refuses `!docs`/
#: `!adrs`, the spike): triaged as `expected`, they never block.
EXPECTED_FINDING_MARKERS: tuple[str, ...] = (
    "missing documentation",
    "missing decisions",
)

#: The triage labels (REQ-003: fix / expected / reported).
TRIAGE_FIX = "fix"
TRIAGE_EXPECTED = "expected"
TRIAGE_REPORTED = "reported"
TRIAGE_UNTRIAGED = "untriaged"

#: The tool names whose calls count as a file edit (for fix triage).
EDIT_TOOL_NAMES: frozenset[str] = frozenset({"edit", "write", "apply_patch", "patch"})

#: A fenced code block in the final text.
_FENCE_RE = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.DOTALL)


@dataclass
class TrialMetrics:
    """The computed metrics of one trial (see the Measurement section).

    Attributes:
        validated_before_return: True iff the final on-disk workspace DSL
            (or the DSL the final message returns) is byte-identical to the
            exact text that got `OK` from a `validate` tool call in the same
            trial. A parsed-only or only-reported result is NOT validated.
        validated_by_file: The sub-check for the on-disk file.
        validated_by_final_text: The sub-check for the final message text.
        skills_loaded: The skill names the agent loaded (order of first
            load).
        parse_calls: Completed calls to a `parse`-suffixed tool.
        validate_calls: Completed calls to a `validate`-suffixed tool.
        inspect_calls: Completed calls to an `inspect`-suffixed tool.
        export_calls: Completed calls to an `export`-suffixed tool.
        validate_ok_calls: `validate` calls whose output is the OK marker.
        inspect_findings: The `inspect` findings (stream and CLI merged,
            first-occurrence order).
        inspect_triage: finding text -> triage label.
        relationship_technology_coverage: 0.0-1.0 or None (no relationships).
        steps: The agent's step count.
        tool_calls: Every completed tool call count.
        tokens: The summed token figures.
        cost: The summed cost figures.
        wall_time_s: Stream wall time, or None.
        timeout: The runner's per-trial timeout fired.
        contended: Another client ran while this trial ran (flagged, not
            failed).
        final_dsl: The DSL extracted from the final message, or None.
        workdir_dsl: The on-disk workspace DSL text, or None.
    """

    validated_before_return: bool
    validated_by_file: bool
    validated_by_final_text: bool
    skills_loaded: list[str]
    parse_calls: int
    validate_calls: int
    inspect_calls: int
    export_calls: int
    validate_ok_calls: int
    inspect_findings: list[str]
    inspect_triage: dict[str, str]
    relationship_technology_coverage: float | None
    steps: int
    tool_calls: int
    tokens: dict[str, float]
    cost: float
    wall_time_s: float | None
    timeout: bool
    contended: bool
    final_dsl: str | None
    workdir_dsl: str | None

    def to_json(self) -> dict:
        """Return a JSON-serialisable copy of the metrics."""
        result = asdict(self)
        return result


def _validate_ok(call: ToolCall) -> bool:
    """Return True iff this validate call answered the OK marker."""
    return call.status == "completed" and call.output.strip() == VALIDATE_OK_MARKER


def _validated_texts(parsed: ParsedTrial) -> set[str]:
    """Return the exact texts that got OK from a validate call (stream)."""
    result: set[str] = set()
    for call in parsed.calls_named(SUFFIX_VALIDATE):
        if _validate_ok(call):
            dsl = call.input.get("dsl")
            if isinstance(dsl, str):
                result.add(dsl)
    return result


def extract_final_dsl(final_text: str) -> str | None:
    """Return the DSL the final message returns, or None.

    The candidate is the LAST fenced code block of the final text that
    carries a `workspace` keyword, taken verbatim (no whitespace
    normalization -- the `validated_before_return` metric is a strict
    byte-identity check by design); an unfenced final text that itself
    looks like a workspace DSL is the candidate too.
    """
    assert isinstance(final_text, str)
    candidates: list[str] = []
    for match in _FENCE_RE.finditer(final_text):
        block = match.group(1)
        if "workspace" in block:
            candidates.append(block)
    if not candidates:
        stripped = final_text.strip()
        if stripped.startswith("workspace") and "{" in stripped:
            candidates.append(stripped)
    result: str | None = candidates[-1] if candidates else None
    return result


def _stream_findings(parsed: ParsedTrial) -> list[str]:
    """Return the inspect findings from the event stream, in order."""
    findings: list[str] = []
    for call in parsed.calls_named(SUFFIX_INSPECT):
        text = call.output.strip()
        if not text:
            continue
        items: list[str] | None = None
        try:
            loaded = json.loads(text)
            if isinstance(loaded, list):
                items = [str(item) for item in loaded]
        except json.JSONDecodeError:
            items = None
        if items is None:
            items = [line.strip() for line in text.splitlines() if line.strip()]
        for item in items:
            if item not in findings:
                findings.append(item)
    return findings


def _edited_after_inspect(parsed: ParsedTrial) -> bool:
    """Return True iff a file edit happened after the last inspect call."""
    last_inspect_idx = -1
    for idx, call in enumerate(parsed.tool_calls):
        if call.name.endswith(SUFFIX_INSPECT) or call.name == SUFFIX_INSPECT:
            last_inspect_idx = idx
    if last_inspect_idx < 0:
        return False
    for call in parsed.tool_calls[last_inspect_idx + 1 :]:
        if call.status != "completed":
            continue
        base = call.name.rsplit("_", 1)[-1]
        if base in EDIT_TOOL_NAMES:
            return True
    result = False
    return result


def triage_findings(findings: list[str], parsed: ParsedTrial) -> dict[str, str]:
    """Assign each finding its triage label (REQ-003).

    `expected` under the MCP limits wins first (documentation/decisions),
    then `fix` (a file edit after the last inspect call), then `reported`
    (the finding's text or its element name is mentioned in the final
    message), otherwise `untriaged`.
    """
    assert isinstance(findings, list)
    final_text = parsed.final_text()
    edited = _edited_after_inspect(parsed)
    result: dict[str, str] = {}
    for finding in findings:
        lowered = finding.lower()
        if any(marker in lowered for marker in EXPECTED_FINDING_MARKERS):
            result[finding] = TRIAGE_EXPECTED
        elif edited:
            result[finding] = TRIAGE_FIX
        elif finding in final_text:
            result[finding] = TRIAGE_REPORTED
        else:
            result[finding] = TRIAGE_UNTRIAGED
    return result


def skills_loaded(parsed: ParsedTrial) -> list[str]:
    """Return the skill names the agent loaded, first-load order.

    The `skill` tool takes the identifier as `id` in the pinned opencode
    image (verified against a live probe); `name` is accepted as a
    fallback for schema drift.
    """
    seen: list[str] = []
    for call in parsed.tool_calls:
        if call.name != "skill" or call.status != "completed":
            continue
        ident = call.input.get("id")
        if not isinstance(ident, str) or not ident:
            ident = call.input.get("name")
        if isinstance(ident, str) and ident and ident not in seen:
            seen.append(ident)
    result = seen
    return result


def compute_metrics(
    parsed: ParsedTrial,
    inputs: GraderInputs,
    *,
    timeout: bool = False,
    contended: bool = False,
) -> TrialMetrics:
    """Compute the full metric set of one trial (pure).

    Args:
        parsed: The parsed event stream.
        inputs: The grader inputs (the real CLI facts).
        timeout: The runner's per-trial timeout fired.
        contended: Another client ran while this trial ran.

    Returns:
        The TrialMetrics.
    """
    assert isinstance(parsed, ParsedTrial)
    assert isinstance(inputs, GraderInputs)

    ok_texts = _validated_texts(parsed)
    final_text = parsed.final_text()
    final_dsl = extract_final_dsl(final_text)

    validated_by_file = inputs.dsl_text is not None and inputs.dsl_text in ok_texts
    validated_by_final = final_dsl is not None and final_dsl in ok_texts
    validated_before_return = validated_by_file or validated_by_final

    stream_findings = _stream_findings(parsed)
    findings: list[str] = list(stream_findings)
    for finding in inputs.inspect_findings:
        if finding not in findings:
            findings.append(finding)

    parse_calls = len(parsed.calls_named(SUFFIX_PARSE))
    validate_calls = len(parsed.calls_named(SUFFIX_VALIDATE))
    inspect_calls = len(parsed.calls_named(SUFFIX_INSPECT))
    export_calls = len(parsed.calls_named(SUFFIX_EXPORT))
    validate_ok_calls = sum(1 for c in parsed.calls_named(SUFFIX_VALIDATE) if _validate_ok(c))

    result = TrialMetrics(
        validated_before_return=validated_before_return,
        validated_by_file=validated_by_file,
        validated_by_final_text=validated_by_final,
        skills_loaded=skills_loaded(parsed),
        parse_calls=parse_calls,
        validate_calls=validate_calls,
        inspect_calls=inspect_calls,
        export_calls=export_calls,
        validate_ok_calls=validate_ok_calls,
        inspect_findings=findings,
        inspect_triage=triage_findings(findings, parsed),
        relationship_technology_coverage=relationship_technology_coverage(inputs.export_json),
        steps=parsed.steps,
        tool_calls=len(parsed.completed_tool_calls()),
        tokens=dict(parsed.tokens),
        cost=parsed.cost,
        wall_time_s=parsed.wall_time_s(),
        timeout=timeout,
        contended=contended,
        final_dsl=final_dsl,
        workdir_dsl=inputs.dsl_text,
    )
    return result
