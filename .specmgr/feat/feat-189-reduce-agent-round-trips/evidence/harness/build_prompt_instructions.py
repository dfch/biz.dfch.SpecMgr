#!/usr/bin/env python3
"""feat-189 Phase 130 (Task 130.100/130.110): rebuild the 4 prompt-cell
instruction files.

The outer wrapper + BEGIN/END markers + trailing "Task:" text are taken
BYTE-IDENTICAL from the feat-128 baseline instruction files; only the
rendered prompt output between the markers is re-fetched -- from the
WORKTREE server (evidence/prompts/<name>.rendered.txt, captured via
harness/mcp_probe_wt.py get_prompt with the baseline's exact render
arguments, see the feature README Design Notes).

Byte layout (verified against all 4 baseline files):
  file = prefix + begin_line + inner + suffix
  where prefix ends with the "Use only the specmgr MCP tools ..."
  paragraph's blank line, begin_line is the "=== BEGIN ... ===" line,
  inner = rendered_bytes minus exactly one trailing newline (the baseline
  rendered.txt files end with a blank line; the instruction inlines the
  text without that final blank line), and suffix starts with the blank
  line after the "=== END ... ===" marker, then "Task:" + task text.

Usage: python3 build_prompt_instructions.py
Prints one shasum line per written file.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent.parent.parent / "feat-128-schema-not-used" / "evidence"

CELLS: dict[str, str] = {
    "create_task": "tsk-create-prompt",
    "create_prb": "prb-create-prompt",
    "update_task": "tsk-update-prompt",
    "update_prb": "prb-update-prompt",
}


def build(name: str, cell: str) -> None:
    base_instr = (BASELINE / "instructions" / f"{cell}.txt").read_bytes()
    rendered = (HERE.parent / "prompts" / f"{name}.rendered.txt").read_bytes()
    begin = f"=== BEGIN pre-invoked prompt '{name}' output ===\n".encode()
    end = f"=== END pre-invoked prompt '{name}' output ===\n".encode()
    bi = base_instr.find(begin)
    ei = base_instr.find(end)
    if bi < 0 or ei < 0 or ei < bi:
        raise SystemExit(f"markers not found in baseline {cell}")
    prefix, suffix = base_instr[:bi], base_instr[ei + len(end) :]
    if not rendered.endswith(b"\n"):
        raise SystemExit(f"rendered {name} does not end with a newline")
    inner = rendered[:-1]
    out = prefix + begin + inner + end + suffix
    # sanity: baseline inner = baseline rendered minus one newline
    base_rendered = (BASELINE / "prompts" / f"{name}.rendered.txt").read_bytes()
    if base_instr[bi + len(begin) : ei] != base_rendered[:-1]:
        raise SystemExit(f"baseline layout assumption broken for {cell}")
    dest = HERE.parent / "instructions" / f"{cell}.txt"
    dest.write_bytes(out)
    print(f"{hashlib.sha256(out).hexdigest()}  {dest.name}")


def main() -> None:
    for name, cell in CELLS.items():
        build(name, cell)
    return


if __name__ == "__main__":
    sys.exit(main())
