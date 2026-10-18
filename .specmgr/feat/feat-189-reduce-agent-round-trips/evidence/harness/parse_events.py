#!/usr/bin/env python3
"""feat-189 Phase 130 (Task 130.100): parse opencode run --format json event
streams into per-run metrics.

Extended from the feat-128 Phase 100 baseline (evidence/harness/parse_events.py)
-- the extension is the schema-fetch metric (baseline counted only
`read_mcp_resource` calls whose uri ends in `/schema`, the resource route).
On the worktree surface the schema is a TOOL, so schema fetches ALSO count
tool calls named `specmgr_get_<d>_schema` (any domain). The resource-route
counting is kept (it will be 0); both are reported as
schema_fetches_tool / schema_fetches_resource. All other baseline metrics
(specmgr call count, failed calls, wall clock, tokens, ordered calls) are
unchanged.

Usage: python3 parse_events.py <run-id> <event-stream.json> [run-dir] [seed-uuid]
Prints a metrics block (JSON) for the digest file.

opencode tool-surface notes (verified on the baseline smoke + formal runs,
re-verified on the feat-189 smoke):
- MCP tools appear as `specmgr_<toolname>` (server prefix + underscore).
- MCP prompts are NOT exposed (baseline probe run: NO_PROMPT_TOOL).
- MCP resources are exposed via host-level `list_mcp_resources` /
  `read_mcp_resource` tools, server-scoped; a schema fetch on the resource
  route is a `read_mcp_resource` call whose uri ends in `/schema`.
- `get_<d>_template` / `get_<d>_example` are MCP TOOLS (not resources) and
  return the same packaged text as the corresponding resources.
- On the worktree surface (Phase 105+), `get_<d>_schema` is also an MCP
  TOOL; the 12 `specmgr://<d>/schema` resources are gone.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MODEL = "vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2"

SCHEMA_TOOL_RE = re.compile(r"^specmgr_get_[a-z0-9]+_schema$")
CREATE_TOOL_RE = re.compile(r"^specmgr_create_(tsk|prb)$")


def main() -> None:
    run_id = sys.argv[1]
    stream = Path(sys.argv[2])
    run_dir = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
    seed_uuid = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None

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
    # baseline resource-route metric (0 on the worktree surface: no schema resources)
    schema_fetches_resource = [
        tc for tc in resource_reads if str((tc["input"] or {}).get("uri", "")).endswith("/schema")
    ]
    # worktree extension: the schema tools (any domain)
    schema_fetches_tool = [tc for tc in specmgr_calls if SCHEMA_TOOL_RE.match(str(tc["tool"]))]
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
    # the create_<d> call sequence (T1 first-try check: the first create
    # call's status, and whether a failed create was retried)
    create_calls = [
        {"n": i + 1, "tool": tc["tool"], "status": tc["status"], "error": tc["error"]}
        for i, tc in enumerate(tool_calls)
        if CREATE_TOOL_RE.match(str(tc["tool"]))
    ]

    out = {
        "run_id": run_id,
        "model": MODEL,
        "seed_uuid": seed_uuid,
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
        "schema_fetches_tool": [str(tc["tool"]) for tc in schema_fetches_tool],
        "schema_fetches_tool_count": len(schema_fetches_tool),
        "schema_fetches_resource": [str(tc["input"].get("uri")) for tc in schema_fetches_resource],
        "schema_fetches_resource_count": len(schema_fetches_resource),
        "schema_fetch_count": len(schema_fetches_tool) + len(schema_fetches_resource),
        "template_fetches": [tc["tool"] or str(tc["input"].get("uri")) for tc in template_fetches],
        "template_fetch_count": len(template_fetches),
        "example_fetches": [tc["tool"] or str(tc["input"].get("uri")) for tc in example_fetches],
        "example_fetch_count": len(example_fetches),
        "list_mcp_resources_calls": sum(1 for tc in tool_calls if tc["tool"] == "list_mcp_resources"),
        "prompt_calls": [tc["tool"] for tc in prompt_calls],
        "validate_calls": len(validate_calls),
        "create_call_sequence": create_calls,
        "create_first_try_success": bool(create_calls) and create_calls[0]["status"] == "completed",
        "create_failure_retries": sum(1 for c in create_calls if c["status"] != "completed"),
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
