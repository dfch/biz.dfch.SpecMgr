#!/usr/bin/env python3
"""feat-128 Phase 100: parse opencode run --format json event streams into
per-run metrics (Task 100.120).

Usage: python3 parse_events.py <run-id> <event-stream.json> [run-dir]
Prints a metrics block for the manifest.

opencode tool-surface notes (verified on the smoke + formal runs):
- MCP tools appear as `specmgr_<toolname>` (server prefix + underscore).
- MCP prompts are NOT exposed (probe run: NO_PROMPT_TOOL).
- MCP resources are exposed via host-level `list_mcp_resources` /
  `read_mcp_resource` tools, server-scoped; a schema fetch is a
  `read_mcp_resource` call whose uri ends in `/schema`.
- `get_<d>_template` / `get_<d>_example` are MCP TOOLS (not resources) and
  return the same packaged text as the corresponding resources.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MODEL = "vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2"


def main() -> None:
    run_id = sys.argv[1]
    stream = Path(sys.argv[2])
    run_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    events: list[dict] = []
    for line in stream.read_text().splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))

    tool_calls: list[dict] = []
    texts: list[str] = []
    ts_first = None
    ts_last = None
    total_input_tokens = 0
    total_output_tokens = 0
    steps = 0
    for ev in events:
        ts = ev.get("timestamp")
        if ts is not None:
            ts_first = ts if ts_first is None else min(ts_first, ts)
            ts_last = ts if ts_last is None else max(ts_last, ts)
        et = ev.get("type")
        part = ev.get("part") or {}
        if et == "tool_use":
            state = part.get("state") or {}
            tool_calls.append(
                {
                    "tool": part.get("tool"),
                    "input": state.get("input"),
                    "status": state.get("status"),
                    "error": (state.get("error") or "")[:300],
                    "time": state.get("time"),
                }
            )
        elif et == "text":
            texts.append(part.get("text", ""))
        elif et == "step_finish":
            steps += 1
            tokens = part.get("tokens") or {}
            total_input_tokens += tokens.get("input", 0)
            total_output_tokens += tokens.get("output", 0)

    wall_ms = (ts_last - ts_first) if (ts_first and ts_last) else None

    specmgr_calls = [tc for tc in tool_calls if str(tc["tool"]).startswith("specmgr_")]
    non_specmgr = [tc for tc in tool_calls if not str(tc["tool"]).startswith("specmgr_")]
    resource_reads = [tc for tc in tool_calls if str(tc["tool"]) in ("read_mcp_resource", "list_mcp_resources")]
    schema_fetches = [tc for tc in resource_reads if str((tc["input"] or {}).get("uri", "")).endswith("/schema")]
    template_fetches = [
        tc
        for tc in tool_calls
        if str(tc["tool"]).endswith("_template") or str((tc["input"] or {}).get("uri", "")).endswith("/template")
    ]
    example_fetches = [
        tc
        for tc in tool_calls
        if str(tc["tool"]).endswith("_example") or str((tc["input"] or {}).get("uri", "")).endswith("/example")
    ]
    prompt_calls = [tc for tc in tool_calls if "prompt" in str(tc["tool"]).lower()]
    validate_calls = [tc for tc in specmgr_calls if str(tc["tool"]) == "specmgr_validate"]
    failed = [tc for tc in tool_calls if tc["status"] not in ("completed", None) or tc["error"]]

    out = {
        "run_id": run_id,
        "model": MODEL,
        "events": len(events),
        "steps": steps,
        "wall_seconds": round(wall_ms / 1000, 1) if wall_ms else None,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tool_calls": len(tool_calls),
        "specmgr_tool_calls": len(specmgr_calls),
        "non_specmgr_tool_calls": len(non_specmgr),
        "non_specmgr_tools": [tc["tool"] for tc in non_specmgr],
        "failed_or_error_calls": len(failed),
        "failed_calls": [{"tool": tc["tool"], "status": tc["status"], "error": tc["error"]} for tc in failed],
        "schema_fetches": [str(tc["input"].get("uri")) for tc in schema_fetches],
        "schema_fetch_count": len(schema_fetches),
        "template_fetches": [tc["tool"] or str(tc["input"].get("uri")) for tc in template_fetches],
        "template_fetch_count": len(template_fetches),
        "example_fetches": [tc["tool"] or str(tc["input"].get("uri")) for tc in example_fetches],
        "example_fetch_count": len(example_fetches),
        "list_mcp_resources_calls": sum(1 for tc in tool_calls if tc["tool"] == "list_mcp_resources"),
        "prompt_calls": [tc["tool"] for tc in prompt_calls],
        "validate_calls": len(validate_calls),
        "ordered_tool_calls": [
            {
                "n": i + 1,
                "tool": tc["tool"],
                "status": tc["status"],
                "input": tc["input"],
                "error": tc["error"],
            }
            for i, tc in enumerate(tool_calls)
        ],
        "final_text": "\n".join(texts)[-2000:],
    }
    if run_dir is not None:
        files = sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob("*") if p.is_file())
        out["files_on_disk"] = files

    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
