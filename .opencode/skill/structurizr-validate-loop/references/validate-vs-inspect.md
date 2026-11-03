# validate vs inspect

Two tools, two questions. Users who ask "is this valid?" want
`validate`. Users who ask "is this complete?" or "is this a good
model?" want `inspect`.

| | `validate` | `inspect` |
|---|---|---|
| Question | Will this parse into a workspace? | Does this follow C4 and Structurizr recommendations? |
| Output on success | `OK` | List of findings, or nothing |
| Output on problems | `ERROR ... at line N of workspace.dsl: <source line>` | One line per finding: `ERROR \| <rule id> \| <message>` |
| Blocking? | Yes. Nothing is valid until it answers `OK`. | No. Findings are recommendations. Never treat a finding list like a failed validate: a workspace can validate cleanly and have dozens of inspect findings. |

## Common validate errors

| Message | Cause | Fix |
|---|---|---|
| `The destination element "x" does not exist` | Typo, missing element, or relationship declared before the element | Check the identifier; move the relationship below the element's definition |
| `The source element "x" does not exist` | Same as above, for the left side | Same |
| `Unexpected tokens` / parse errors | Unbalanced braces or unquoted strings with spaces | Quote every name, description, and technology |

## Common inspect findings

| Rule id | Meaning | Triage |
|---|---|---|
| `workspace.scope` | No workspace scope set | fix — add `configuration { scope softwaresystem }` (one detailed system) or `scope landscape` |
| `model.relationship.technology` | A relationship has no technology | fix — add a third string: `a -> b "Calls" "HTTPS/JSON"`; use `"In-process call"` between components |
| `model.relationship.description` | A relationship has no description | fix — add a verb phrase: `"Reads orders from"` |
| `model.softwaresystem.documentation` | A system with containers has no docs | expected under the MCP limits — the MCP refuses `!docs`; do not add it. Report the finding as expected in the final answer |
| `model.softwaresystem.decisions` | A system with containers has no ADRs | expected under the MCP limits — the MCP refuses `!adrs`; do not add it. Report the finding as expected in the final answer |
| `views.view.key` / `views.view.layout` | A view has an auto-generated key | fix — give every view an explicit key: `container system "Containers" { ... }` |
| `model.*.description` | An element has no description | fix — add the description string after the name |

Report inspect findings grouped by rule id with counts, and say which
ones are worth fixing. Do not describe the workspace as broken because
of them.
