---
description: Generate the agent-owned PlantUML sequence diagram for a specmgr use case -- $1 is the UC document id (a lowercase-hex uuid).
---

Generate the sequence diagram for a use case. My input:

- `$1` (required): the use case document's id (a lowercase-hex uuid). If it
  is missing or malformed, ask me for a clean id with the `question` tool
  rather than guessing.

1. Run the `generate_uc_sequence_diagram` MCP prompt flow for `$1` exactly
   as narrated: read `specmgr://uc/plantuml` first, build the `TodoWrite`
   plan, `get_uc` (a `ParseFailureResult` stops the flow), the §2.11
   Subfunction judgment, `get_uc_sequence_skeleton`, attribution of every
   `UNATTRIBUTED` marker by understanding the free text (the `question`
   tool whenever not confident; pre-filled arrows may be corrected), the
   zero-marker rule, the `validate_plantuml` loop (green at the highest
   available layer before writing), and the host-native write to
   `diagrams/uc/$1.sequence.puml` — no specmgr tool writes `.puml`.
2. Report per the flow's step 10: the written path, the validation outcome
   (`checked_by`, `valid`/`rendered`, `source_state`), every `question` you
   asked and its answer, and any pre-filled arrow you corrected, with the
   reasoning for each. Do not commit, and do not touch any other file.
