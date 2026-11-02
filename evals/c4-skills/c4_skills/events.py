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

"""Parser for `opencode run --format json` NDJSON event streams.

OpenCode emits one JSON object per line. The shapes are version-dependent
(opencode 2.2.5 at pin time); the parser is deliberately lenient:

- it indexes every event by its top-level `type` token and keeps the raw
  objects (the committed fixture
  ``tests/evals/fixtures/events/smoke-hello.ndjson`` pins the exact schema);
- it recognises part-level types (`step-start`/`step`, `text`, `tool`,
  `reasoning`) wherever they appear under `part`, so a rename of one token
  degrades to an `unknown` count instead of a crash;
- token/cost figures are summed from every `step`-kind part that carries a
  `tokens` block, whatever the event type around it.

Unknown event types are counted, never dropped: a schema drift shows up in
`ParsedTrial.unknown_types` and in the report.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

#: The part-level type tokens the parser indexes (opencode 2.2.5).
PART_TYPE_STEP_START = "step-start"
PART_TYPE_STEP_FINISH = "step-finish"
PART_TYPE_STEP = "step"
PART_TYPE_TEXT = "text"
PART_TYPE_TOOL = "tool"
PART_TYPE_REASONING = "reasoning"

#: The event-level type tokens.
EVENT_TYPE_FINISH = "finish"
EVENT_TYPE_ERROR = "error"
EVENT_TYPE_STEP_FINISH = "step_finish"

#: Tool call statuses.
TOOL_STATUS_COMPLETED = "completed"
TOOL_STATUS_ERROR = "error"
TOOL_STATUS_PENDING = "pending"

#: The MCP validate tool's success marker (the spike: `validate` answers the
#: plain text `OK` on a valid workspace, the error text otherwise).
VALIDATE_OK_MARKER = "OK"


@dataclass
class ToolCall:
    """One tool invocation as reported by the event stream.

    Attributes:
        name: The tool name exactly as reported (MCP tools carry the server
            prefix, e.g. `structurizr_validate`).
        status: `completed`, `error` or `pending`.
        input: The tool's input arguments (dict, empty when unknown).
        output: The tool's output text (empty for pending calls).
        title: The optional short title opencode attaches.
        started_ms: The state start timestamp (ms since epoch), if any.
        finished_ms: The state end timestamp (ms since epoch), if any.
    """

    name: str
    status: str
    input: dict
    output: str
    title: str
    started_ms: int | None
    finished_ms: int | None


@dataclass
class ParsedTrial:
    """The parsed view of one trial's event stream.

    Attributes:
        events: Every raw event object, in stream order.
        steps: Number of step-start events.
        text_parts: Every assistant text part, in stream order.
        tool_calls: Every tool call, in stream order (all statuses).
        tokens: Summed token figures
            (`input`/`output`/`reasoning`/`cache_read`/`cache_write`).
        cost: Summed cost figures.
        session_id: The session id from the first event that carries one.
        first_ts: The first event timestamp (ms), if any.
        last_ts: The last event timestamp (ms), if any.
        finish_seen: Whether a `finish` event closed the stream.
        errors: Every `error` event object.
        unknown_types: Count of event types the parser does not index.
    """

    events: list[dict] = field(default_factory=list)
    steps: int = 0
    text_parts: list[dict] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    tokens: dict[str, float] = field(
        default_factory=lambda: {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    )
    cost: float = 0.0
    session_id: str | None = None
    first_ts: int | None = None
    last_ts: int | None = None
    finish_seen: bool = False
    errors: list[dict] = field(default_factory=list)
    unknown_types: Counter = field(default_factory=Counter)

    def final_text(self) -> str:
        """Return the last assistant text part's content (empty if none)."""
        if not self.text_parts:
            return ""
        part = self.text_parts[-1]
        result = str(part.get("text") or "")
        return result

    def completed_tool_calls(self) -> list[ToolCall]:
        """Return every tool call that reached a terminal status."""
        result = [c for c in self.tool_calls if c.status in (TOOL_STATUS_COMPLETED, TOOL_STATUS_ERROR)]
        return result

    def calls_named(self, suffix: str) -> list[ToolCall]:
        """Return terminal tool calls whose name ends with `suffix`.

        MCP tool names carry a server prefix (`structurizr_validate`), so the
        classification matches on the suffix after that prefix.
        """
        assert isinstance(suffix, str) and suffix
        result = [
            c
            for c in self.completed_tool_calls()
            if c.name == suffix or c.name.endswith("_" + suffix) or c.name.endswith("-" + suffix)
        ]
        return result

    def wall_time_s(self) -> float | None:
        """Return the stream's wall time in seconds, or None if unknown."""
        if self.first_ts is None or self.last_ts is None or self.last_ts <= self.first_ts:
            return None
        result = (self.last_ts - self.first_ts) / 1000.0
        return result


def _index_tokens(parsed: ParsedTrial, part: dict) -> None:
    """Sum a `tokens` block from one step-kind part into `parsed.tokens`."""
    tokens = part.get("tokens")
    if not isinstance(tokens, dict):
        return
    for key in ("input", "output", "reasoning"):
        value = tokens.get(key)
        if isinstance(value, (int, float)):
            parsed.tokens[key] += value
    cache = tokens.get("cache")
    if isinstance(cache, dict):
        for src, dst in (("read", "cache_read"), ("write", "cache_write")):
            value = cache.get(src)
            if isinstance(value, (int, float)):
                parsed.tokens[dst] += value
    cost = part.get("cost")
    if isinstance(cost, (int, float)):
        parsed.cost += cost


def _index_tool(parsed: ParsedTrial, part: dict) -> None:
    """Index one tool part into `parsed.tool_calls`."""
    name = str(part.get("tool") or "")
    state = part.get("state")
    if not isinstance(state, dict):
        return
    status = str(state.get("status") or TOOL_STATUS_PENDING)
    tool_input = state.get("input")
    output_raw = state.get("output")
    if isinstance(output_raw, dict):
        # some tool states carry {output: ...} or {error: ...}
        output_text = str(output_raw.get("output") or output_raw.get("error") or "")
    elif isinstance(output_raw, str):
        output_text = output_raw
    else:
        output_text = ""
    time_block = state.get("time")
    started = time_block.get("start") if isinstance(time_block, dict) else None
    finished = time_block.get("end") if isinstance(time_block, dict) else None
    call = ToolCall(
        name=name,
        status=status,
        input=tool_input if isinstance(tool_input, dict) else {},
        output=output_text,
        title=str(state.get("title") or ""),
        started_ms=int(started) if isinstance(started, (int, float)) else None,
        finished_ms=int(finished) if isinstance(finished, (int, float)) else None,
    )
    parsed.tool_calls.append(call)


def parse_event(event: dict, parsed: ParsedTrial) -> None:
    """Fold one raw event object into `parsed` (single-event entry point).

    Args:
        event: One decoded NDJSON line (a JSON object).
        parsed: The accumulator to update in place.
    """
    assert isinstance(event, dict)
    parsed.events.append(event)
    event_type = str(event.get("type") or "")
    ts = event.get("timestamp")
    if isinstance(ts, (int, float)):
        if parsed.first_ts is None:
            parsed.first_ts = int(ts)
        parsed.last_ts = int(ts)
    session_id = event.get("sessionID")
    if parsed.session_id is None and isinstance(session_id, str) and session_id:
        parsed.session_id = session_id

    part = event.get("part")
    part_is_dict = isinstance(part, dict)
    part_type = str(part.get("type") or "") if part_is_dict else ""

    if event_type == EVENT_TYPE_FINISH:
        parsed.finish_seen = True
        return
    if event_type == EVENT_TYPE_ERROR:
        parsed.errors.append(event)
        return

    if part_is_dict and part_type in (PART_TYPE_STEP_START, "step_start"):
        parsed.steps += 1
        return
    if part_is_dict and part_type in (PART_TYPE_TEXT, "text"):
        parsed.text_parts.append(part)
        return
    if part_is_dict and part_type in (PART_TYPE_TOOL, "tool"):
        _index_tool(parsed, part)
        return
    if part_is_dict and part_type in (PART_TYPE_REASONING, "reasoning"):
        return
    if part_is_dict and part_type in (PART_TYPE_STEP_FINISH, PART_TYPE_STEP, "step", "step_finish"):
        _index_tokens(parsed, part)
        return
    # step_finish and friends: index tokens whenever the part carries them
    if part_is_dict and isinstance(part.get("tokens"), dict):
        _index_tokens(parsed, part)
        return
    parsed.unknown_types[event_type or "<no-type>"] += 1


def parse_event_stream(lines: list[str]) -> ParsedTrial:
    """Parse a full NDJSON event stream into a ParsedTrial.

    Blank lines and non-JSON lines are counted as unknown, never raised: a
    truncated stream (a killed trial) must still parse for the metrics.

    Args:
        lines: The raw stream lines (trailing newlines optional).

    Returns:
        The ParsedTrial.
    """
    assert isinstance(lines, list)
    parsed = ParsedTrial()
    for line in lines:
        assert isinstance(line, str)
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            parsed.unknown_types["<unparseable-line>"] += 1
            continue
        if not isinstance(event, dict):
            parsed.unknown_types["<non-object-line>"] += 1
            continue
        parse_event(event, parsed)
    return parsed


def parse_events_file(path: Path) -> ParsedTrial:
    """Parse one `opencode run --format json` output file (NDJSON).

    Args:
        path: The event stream file.

    Returns:
        The ParsedTrial.
    """
    assert path.is_file()
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result = parse_event_stream(lines)
    return result
