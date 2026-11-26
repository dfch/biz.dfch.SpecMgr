---
name: uc-diagram
description: Use when generating, regenerating, or validating PlantUML diagrams from a specmgr UC (use case) document -- a per-UC use case diagram, the multi-UC package diagram, or the agent-owned sequence diagram (the generate_uc_sequence_diagram prompt flow: skeleton, UNATTRIBUTED attribution, the question tool, the validate_plantuml loop) -- whether surfaced by an explicit /uc-diagram request or organically while working with specmgr use cases and diagrams.
---

# UC Diagram

You are turning a specmgr use case document (`uc`) into PlantUML. Three
artifact kinds exist (rulebook §1): the **deterministic, CLI-regenerable**
per-UC `<id>.usecase.puml` and multi-UC `package.puml` (rulebook §2.5–§2.8,
§2.10), and the **agent-owned** `<id>.sequence.puml` (rulebook §2.9, §2.10)
— the deterministic skeleton plus agent attribution, which no CLI can
reproduce.

## How

1. **Read the rulebook first**: `specmgr://uc/plantuml` — the frozen UC →
   PlantUML mapping and validation rulebook. Do not proceed on memory of
   the mapping; where anything below and the rulebook differ, the rulebook
   wins.
2. **A sequence diagram → run the `generate_uc_sequence_diagram` MCP
   prompt** for the UC's id — the narrated rulebook §3.8 flow: `TodoWrite`
   plan, `get_uc` (a `ParseFailureResult` stops the flow), the §2.11
   Subfunction judgment, `get_uc_sequence_skeleton`, attribution of every
   `UNATTRIBUTED` marker by understanding the free text (the `question`
   tool MUST be used whenever not confident; pre-filled arrows are
   positional, not semantic, and may be corrected), the zero-marker rule,
   the `validate_plantuml` loop (green at the highest available layer
   before writing), the host-native write to
   `diagrams/uc/<id>.sequence.puml` (no specmgr tool writes `.puml`), and
   never commit. This is the only sanctioned path for a sequence diagram.
3. **Usecase / package diagrams → the deterministic-only CLI** (or the
   `get_uc_diagram` / `get_use_case_package_diagram` MCP tools):
   - `specmgr diagram uc <id>|all --out <dir>` — writes exactly the
     per-UC usecase + `package.puml` files; it never creates, overwrites,
     or diffs `<id>.sequence.puml`.
   - `specmgr diagram uc <id>|all --out <dir> --check` — the CI drift
     check (regenerate in memory, byte-diff usecase + package only).
   - `specmgr plantuml-check <path...>` — validates any `.puml` (agent-
     owned sequence files included) through the strict chain.
   - `specmgr plantuml-encode <path|->` — the offline classic-encoding
     URL payload.
4. **plantuml-mcp watch note**: if your host configures a plantuml MCP
   server with a check/render tool, prefer it for validating diagrams.
   specmgr has **no dependency** on plantuml-mcp — it ships its own
   import-free validation chain (`plantuml/`, rulebook §3) behind
   `validate_plantuml` and the CLI.

Ask the user (via your host's question mechanism) rather than guessing
whenever an `UNATTRIBUTED` marker's attribution is not clear from the free
text. Never commit as part of a diagram flow.
