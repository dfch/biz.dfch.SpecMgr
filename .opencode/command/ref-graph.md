---
description: Render the deterministic reference-graph PlantUML diagram via the `specmgr diagram refs` CLI -- $1 is a `<type> <id>` pair (for `feat` the full `feat-NNN-slug`), optionally followed by a `depth` (1..5) and/or the `--reverse` / `--no-feat` flags, or the literal `all` for the registry-wide graph.
---

Render the reference-graph diagram for my input -- deterministic, CLI-only (no agent attribution, no prompt flow):

- `$1` (required): either a `<type> <id>` pair naming the source document (e.g. `req 3f2a1b3c-...`, `dec 9c1f...`, or `feat feat-144-ref-artifact` -- for `feat` the full `feat-NNN-slug`, use `list_feat` to discover the exact id; a bare `feat-NNN` is rejected), optionally followed by `depth` (1..5, the forward BFS depth) and/or the `--reverse` and/or `--no-feat` flags; or the literal `all` for the registry-wide graph. If it is missing or malformed, ask me for a clean input with the `question` tool rather than guessing.

1. Run the deterministic CLI, mapping my input onto its own flags one-to-one (never restate or reinterpret the frozen rulebook `specmgr://reference-graph` -- where anything and it differ, it wins):
   - scoped: `specmgr diagram refs <type> <id> [--depth N] [--reverse] [--no-feat]` -- writes `<id>.refs.puml` under `diagrams/refs/` (CWD-relative);
   - registry-wide: `specmgr diagram refs all [--no-feat]` -- writes `reference-graph.puml`.
2. Report the written path (the CLI's `Wrote` line) and the validation verdict: run `specmgr plantuml-check` over the written file (or the `validate_plantuml` MCP tool over its source) and report `checked_by`/`valid`/`source_state` + every finding (exit 0 valid / 1 invalid / 2 source misconfigured-or-unavailable / 3 inconclusive). If the CLI itself exits 1 (the `mcp` extra is missing -- report its install hint) or 2 (a usage-or-resolution error: wrong-format `type`/`id`/`depth`, a missing source, an existing-but-broken source), report its stderr verbatim and stop -- do not paper over it.
3. Do not edit, write, or commit anything beyond the CLI's own `.puml` artifact, and do not touch any other file. Never commit.
