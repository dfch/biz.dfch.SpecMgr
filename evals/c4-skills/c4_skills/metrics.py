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

"""Trial metrics (Task 100.140; Code Mode detection, Phase 110 locked harness fix).

The metrics combine the parsed event stream (agent behaviour) with the
grader inputs (the real CLI facts about the produced workspace). Everything
here is pure -- the runner calls :func:`compute_metrics` once per trial.

The pinned opencode image (2.2.5) exposes no remote-MCP tools natively;
the Structurizr MCP is reached through Code Mode (`execute` blocks
invoking `tools.<server>.<tool>({...})`). Every stream-derived metric and
gate therefore counts over the NORMALIZED MCP-CALL VIEW
(:func:`normalized_mcp_calls`): one entry per terminal native MCP call
(exactly the pre-fix semantics) plus one entry per MCP-family reference
in a terminal `execute` block (the conservative extraction rules live in
the detection layer :mod:`c4_skills.codemode`).

Phase 125 (the deferred Phase 110 review findings G2/I1/I2) changed the
finding extraction and the `fix` triage label:

- I1: the stream finding extraction's line fallback applies to
  SINGLE-LINE non-JSON-array outputs only (a multi-line bundled Code
  Mode object answer yields no findings, not one per line);
- I2: the stream/CLI finding merge dedupes on the severity-prefix-
  NORMALIZED finding text (:func:`normalize_finding`), so the same
  finding under its `ERROR:`-prefixed stream form and its bare CLI form
  merges to one entry (first-occurrence order, first-seen form kept);
- G2: the `fix` triage label is truth-anchored to the grader's own
  FINAL CLI `inspect` findings (:func:`final_inspect_findings_set`): a
  post-inspect edit earns it for a finding only when that finding is
  absent from that set (a clean final inspect makes every finding
  absent; a final inspect that could not run or that met a broken
  workspace makes no `fix` label valid). The edit signal alone no
  longer suffices.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

from .codemode import (
    EXECUTE_TOOL_NAME,
    FAMILY_EXPORT,
    FAMILY_INSPECT,
    FAMILY_PARSE,
    FAMILY_VALIDATE,
    MCP_FAMILIES,
    analyze_execute_block,
)
from .events import TOOL_STATUS_COMPLETED, TOOL_STATUS_ERROR, VALIDATE_OK_MARKER, ParsedTrial, ToolCall
from .graders import GraderInputs, relationship_technology_coverage

# ---------------------------------------------------------------------------
# classification constants
# ---------------------------------------------------------------------------

# The MCP family vocabulary (parse/validate/inspect/export) is defined
# in the detection layer `codemode` and imported above as FAMILY_*.

#: The `source` values of the normalized MCP-call view.
SOURCE_NATIVE = "native"
SOURCE_CODEMODE = "codemode"

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

#: The tool names whose calls count as a file edit (the `fix` triage
#: signal). Coarse and informational about the agent's edit activity
#: (what it edited is not checked) -- and, since Task 125.100/G2, NOT
#: SUFFICIENT ON ITS OWN: a post-inspect edit earns the `fix` label for
#: a finding only when that finding is absent from the grader's own
#: final CLI `inspect` findings (the truth anchor,
#: :func:`final_inspect_findings_set`), which corroborates the edit; the
#: label it derives feeds the locked `triage_complete` gate (which
#: accepts `fix`/`expected`/`reported`). The pinned opencode image
#: (2.2.5) reports its command-execution tools as `shell` (a `command`
#: input) and `execute` (a `code` input), and the committed smoke
#: streams show agents mutating files through both (e.g. heredoc
#: writes, `sed`-style fixes); the dedicated editors are `edit`/`write`,
#: plus the `apply_patch`/`patch` names of other agent CLIs (kept for
#: schema drift). A call to a name here after the last inspect counts
#: as "edited".
EDIT_TOOL_NAMES: frozenset[str] = frozenset({"edit", "write", "apply_patch", "patch", "shell", "execute"})

#: A fenced code block in the final text.
_FENCE_RE = re.compile(r"```[a-zA-Z0-9_-]*\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class McpInvocation:
    """One normalized MCP invocation (native or Code Mode).

    The unit the stream-derived metrics and gates count over: a native
    entry is one terminal native MCP `tool_use` call (classified exactly
    as `ParsedTrial.calls_named` did before the Code Mode fix); a Code
    Mode entry is one MCP-family reference inside a terminal `execute`
    block (the block's status/output ride along -- a block's output is
    the value of the block's `return`, not of any single call inside it).

    Attributes:
        source: `"native"` or `"codemode"`.
        family: The MCP family (`parse`/`validate`/`inspect`/`export`).
        tool: The tool name (native: the call name as reported; Code
            Mode: the referenced `<tool>` token).
        status: The owning call's terminal status
            (`completed`/`error`).
        dsl: The DSL input text, or None when unattributable (Code Mode:
            only a plain inline literal at the call site).
        output: The output text (native: the call's output; Code Mode:
            the block's output).
        ok: Whether this entry "answered OK" (validate family only, per
            the locked attribution rules).
        position: The owning tool call's index in
            `ParsedTrial.tool_calls` (the triage-ordering coordinate).
    """

    source: str
    family: str
    tool: str
    status: str
    dsl: str | None
    output: str
    ok: bool
    position: int


@dataclass
class TrialMetrics:
    """The computed metrics of one trial (see the Measurement section).

    Attributes:
        validated_before_return: True iff the final on-disk workspace DSL
            (or the DSL the final message returns) is byte-identical to the
            exact text that got `OK` from a `validate`-family MCP
            invocation (a native call, or an attributed Code Mode
            reference) in the same trial. A parsed-only or only-reported
            result is NOT validated.
        validated_by_file: The sub-check for the on-disk file.
        validated_by_final_text: The sub-check for the final message text.
        skills_loaded: The skill names the agent loaded (order of first
            load).
        parse_calls: Terminal `parse`-family MCP invocations (native +
            Code Mode).
        validate_calls: Terminal `validate`-family MCP invocations
            (native + Code Mode).
        inspect_calls: Terminal `inspect`-family MCP invocations (native
            + Code Mode).
        export_calls: Terminal `export`-family MCP invocations (native +
            Code Mode; the hyphenated export tools count for the family).
        validate_ok_calls: `validate` invocations that answered the OK
            marker (native: the strict output check; Code Mode: the
            locked attribution rule).
        inspect_findings: The `inspect` findings (stream and CLI merged
            on the severity-prefix-normalized finding text,
            first-occurrence order, first-seen form kept -- Task
            125.120/I2).
        inspect_triage: finding text -> triage label (`fix` requires a
            post-inspect edit AND the finding's absence from the final
            CLI `inspect` findings -- Task 125.100/G2).
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


def native_family(name: str) -> str | None:
    """Return the MCP family a native tool call name classifies as.

    The locked native classification (the `ParsedTrial.calls_named`
    rule, per family): the name equals the family or ends with `_` or
    `-` plus the family (MCP names carry a server prefix, e.g.
    `structurizr_validate`).
    """
    for family in MCP_FAMILIES:
        if name == family or name.endswith("_" + family) or name.endswith("-" + family):
            return family
    result: str | None = None
    return result


def normalized_mcp_calls(parsed: ParsedTrial) -> list[McpInvocation]:
    """Return the normalized MCP-call view of one trial (pure, ordered).

    One entry per terminal native MCP call plus one entry per
    (terminal `execute` block, MCP-family reference), in
    `ParsedTrial.tool_calls` order (the Code Mode entries of one block
    in text order of their references). This is the counting unit of
    every stream-derived metric and gate: native entries keep exactly
    the pre-fix semantics (terminal status, the `calls_named` name
    rule, the strict OK check); Code Mode entries follow the locked
    conservative rules of the detection layer `codemode` (a reference
    is the textual `tools.<server>.<tool>(` pattern; the `dsl` input
    only for a plain inline literal; OK attribution only for a single
    completed reference answering exactly the OK marker).
    """
    assert isinstance(parsed, ParsedTrial)
    result: list[McpInvocation] = []
    for idx, call in enumerate(parsed.tool_calls):
        if call.status not in (TOOL_STATUS_COMPLETED, TOOL_STATUS_ERROR):
            continue
        if call.name == EXECUTE_TOOL_NAME:
            code = call.input.get("code")
            if not isinstance(code, str) or not code:
                continue
            for entry in analyze_execute_block(code, call.status, call.output):
                result.append(
                    McpInvocation(
                        source=SOURCE_CODEMODE,
                        family=entry.family,
                        tool=entry.tool,
                        status=call.status,
                        dsl=entry.dsl,
                        output=call.output,
                        ok=entry.ok,
                        position=idx,
                    )
                )
            continue
        family = native_family(call.name)
        if family is None:
            continue
        dsl = call.input.get("dsl")
        result.append(
            McpInvocation(
                source=SOURCE_NATIVE,
                family=family,
                tool=call.name,
                status=call.status,
                dsl=dsl if isinstance(dsl, str) else None,
                output=call.output,
                ok=family == FAMILY_VALIDATE and _validate_ok(call),
                position=idx,
            )
        )
    return result


def validated_texts(parsed: ParsedTrial) -> set[str]:
    """Return the exact texts that got OK from a validate invocation (stream).

    The set of `dsl` inputs of every `validate`-family invocation that
    answered the OK marker: native calls (the strict output check, the
    `dsl` input as reported) plus Code Mode references attributed OK
    under the locked rule whose `dsl` argument was a plain inline
    literal (unattributable references add nothing -- the
    `validated_before_return` byte-identity gate then fails for that
    trial, conservative by design). The reference set of the
    `validated_before_return` metric and the same-named gate (the gate
    reuses it for its detail strings).
    """
    result: set[str] = set()
    for entry in normalized_mcp_calls(parsed):
        if entry.family != FAMILY_VALIDATE or not entry.ok:
            continue
        if entry.dsl is not None:
            result.add(entry.dsl)
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


def _findings_from_output(text: str) -> list[str]:
    """Return the findings one `inspect` output text carries, in order.

    A JSON array of items is the extraction (the MCP `inspect` answers
    a JSON array of finding strings, single- or multi-line -- the JSON
    array path is exactly the pre-I1 one). When the text is not a JSON
    array, the line-based fallback applies to SINGLE-LINE outputs only
    (its one line is the finding): a multi-line non-array output -- e.g.
    a bundled Code Mode object answer -- yields NO findings (Task
    125.110/I1; before, every non-blank line of such an answer became a
    spurious finding, e.g. the JSON lines of the object itself).
    """
    stripped = text.strip()
    if not stripped:
        result: list[str] = []
        return result
    try:
        loaded = json.loads(stripped)
    except json.JSONDecodeError:
        loaded = None
    if isinstance(loaded, list):
        result = [str(item) for item in loaded]
        return result
    if "\n" in stripped:
        result = []
        return result
    result = [stripped]
    return result


#: The leading severity tokens the finding extraction normalizes away
#: before the stream/CLI merge (Task 125.120/I2) and before the `fix`
#: label's final-CLI-absence check (Task 125.100/G2): the MCP `inspect`
#: answers findings `ERROR:`-prefixed, while the CLI `inspect` finding
#: lines parse to their bare message (the pipe form is split in
#: `collect_inputs`) or keep an `ERROR`/`WARNING` prefix (the non-pipe
#: form). The same finding in both forms must merge to one entry.
_SEVERITY_PREFIX_RE = re.compile(r"^(?:ERROR|WARNING|INFO|IGNORE)(?::[ \t]*|[ \t]+)")


def normalize_finding(text: str) -> str:
    """Return the finding text without its leading severity prefix.

    The merge key of the stream/CLI finding merge (Task 125.120/I2) and
    of the `fix` label's absence check (Task 125.100/G2): `ERROR: X`,
    `ERROR X`, `WARNING: X`, `INFO X` and `IGNORE X` all normalize to
    the bare `X`. The prefix is a whole severity token followed by a
    colon or whitespace, so a finding that starts with a longer word
    (e.g. `ERRORS in the model`) or with the token without such a
    delimiter keeps its text.
    """
    result = _SEVERITY_PREFIX_RE.sub("", text.strip(), count=1)
    return result


def _stream_findings(parsed: ParsedTrial) -> list[str]:
    """Return the inspect findings from the event stream, in order.

    Counts over the normalized view: every `inspect`-family invocation
    (native calls exactly as before, plus Code Mode `execute` blocks at
    their position in the stream) feeds the same findings extraction
    over its output text.
    """
    findings: list[str] = []
    for entry in normalized_mcp_calls(parsed):
        if entry.family != FAMILY_INSPECT:
            continue
        for item in _findings_from_output(entry.output):
            if item not in findings:
                findings.append(item)
    return findings


def _edited_after_inspect(parsed: ParsedTrial) -> bool:
    """Return True iff a file edit happened after the last inspect invocation.

    The last inspect's position is the maximum `tool_calls` index of
    every `inspect`-family entry of the normalized view (native and
    Code Mode alike -- a Code Mode inspect participates in the call
    ORDER at its `execute` event's position); the edit scan over the
    subsequent calls is the pre-fix one (completed calls whose base
    name is in `EDIT_TOOL_NAMES`).
    """
    last_inspect_idx = -1
    for entry in normalized_mcp_calls(parsed):
        if entry.family == FAMILY_INSPECT and entry.position > last_inspect_idx:
            last_inspect_idx = entry.position
    if last_inspect_idx < 0:
        return False
    for call in parsed.tool_calls[last_inspect_idx + 1 :]:
        if call.status != TOOL_STATUS_COMPLETED:
            continue
        base = call.name.rsplit("_", 1)[-1]
        if base in EDIT_TOOL_NAMES:
            return True
    result = False
    return result


def final_inspect_findings_set(inputs: GraderInputs) -> set[str] | None:
    """Return the final-CLI-findings set the `fix` triage label anchors to.

    Task 125.100/G2: the truth anchor is the grader's own final CLI
    `inspect` run over the final workspace, never the agent's claim. The
    pinned CLI `inspect` answers rc=0 with no output on a finding-free
    workspace and rc=1 on a workspace it inspected that carries findings
    (the pipe-form finding lines), so the set is trustworthy iff:

    - `inspect_rc` is 0 -- a clean workspace, the empty set (every
      finding is absent from it);
    - `inspect_rc` is non-zero AND a non-empty findings list parsed --
      the inspected workspace's findings (normalized to the merge key).

    and not trustworthy (None) iff:

    - `inspect_rc` is None (no DSL file -- the CLI never ran);
    - `inspect_rc` is non-zero with NO parsed finding (a broken
      workspace whose error line carries no finding, e.g. a missing
      `!include` target -- nothing is demonstrably fixed).

    When the set is None, no `fix` label is valid at all.
    """
    if inputs.inspect_rc is None:
        result: set[str] | None = None
        return result
    if inputs.inspect_rc == 0:
        result = set()
        return result
    if not inputs.inspect_findings:
        result = None
        return result
    result = {normalize_finding(finding) for finding in inputs.inspect_findings}
    return result


def triage_findings(findings: list[str], parsed: ParsedTrial, inputs: GraderInputs) -> dict[str, str]:
    """Assign each finding its triage label (REQ-003).

    Priority: `expected` (the MCP-limits markers) first, then `fix` --
    a completed file edit after the last inspect AND the finding absent
    from the final CLI `inspect` findings (the truth anchor of Task
    125.100/G2: the edit signal alone no longer suffices, and when the
    final CLI inspect could not run or the workspace is broken, no
    `fix` label is granted at all), then `reported` (the finding's text
    is mentioned in the final message), otherwise `untriaged`.
    """
    assert isinstance(findings, list)
    final_text = parsed.final_text()
    edited = _edited_after_inspect(parsed)
    final_set = final_inspect_findings_set(inputs)
    result: dict[str, str] = {}
    for finding in findings:
        lowered = finding.lower()
        if any(marker in lowered for marker in EXPECTED_FINDING_MARKERS):
            result[finding] = TRIAGE_EXPECTED
        elif edited and final_set is not None and normalize_finding(finding) not in final_set:
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

    ok_texts = validated_texts(parsed)
    final_text = parsed.final_text()
    final_dsl = extract_final_dsl(final_text)

    validated_by_file = inputs.dsl_text is not None and inputs.dsl_text in ok_texts
    validated_by_final = final_dsl is not None and final_dsl in ok_texts
    validated_before_return = validated_by_file or validated_by_final

    stream_findings = _stream_findings(parsed)
    findings: list[str] = list(stream_findings)
    seen: set[str] = {normalize_finding(finding) for finding in findings}
    for finding in inputs.inspect_findings:
        key = normalize_finding(finding)
        if key not in seen:
            seen.add(key)
            findings.append(finding)

    calls = normalized_mcp_calls(parsed)
    parse_calls = sum(1 for entry in calls if entry.family == FAMILY_PARSE)
    validate_calls = sum(1 for entry in calls if entry.family == FAMILY_VALIDATE)
    inspect_calls = sum(1 for entry in calls if entry.family == FAMILY_INSPECT)
    export_calls = sum(1 for entry in calls if entry.family == FAMILY_EXPORT)
    validate_ok_calls = sum(1 for entry in calls if entry.ok)

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
        inspect_triage=triage_findings(findings, parsed, inputs),
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
