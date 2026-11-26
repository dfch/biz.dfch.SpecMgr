# License notice

This skill adapts text from the `structurizr` skill of the
[passionsplay/structurizr-skill](https://github.com/passionsplay/structurizr-skill)
repository:

- Commit: `5e45154e1c266e0517d456855b415ba770412f16` (pinned and
  verified)
- License: MIT
- Copyright (c) 2026 Benjamin Turner

## Which local files adapt which source files

| Local file | Source file(s) at the pinned commit |
|---|---|
| `references/validate-vs-inspect.md` | `skills/structurizr/references/validate-vs-inspect.md` (the opening, the two-tool table, both error/finding tables, the closing report paragraph — the `!docs`/`!adrs` fix advice is inverted to "expected under the MCP limits" per this repo's locked adaptation rule) and `skills/structurizr/SKILL.md` (the "Validate and inspect are different tools" gotcha, folded into the table's blocking row) |
| `references/dsl-gotchas.md` | `skills/structurizr/references/dsl-best-practices.md` (the flat-identifiers, declaration-order, and descriptions-and-technology sections), `skills/structurizr/SKILL.md` (the "DSL rules that prevent most failures" and gotchas bullets those sections merge), and `skills/structurizr/references/validate-vs-inspect.md` (the error messages that name the failure modes) |

`SKILL.md` adapts no text (ideas only — its loop is written from the
spike findings of TXT `4a09922d-bc32-4c03-86ba-d30ebc34e0b8` and this
repo's requirements; the upstream Docker-CLI workflow,
`scripts/structurizr.sh`, and Claude-specific setup were dropped), so it
carries no attribution line. The upstream
`skills/structurizr/references/mcp.md` was read for the MCP tool
enumeration only; its run/connect content is Docker/Claude-specific and
was dropped without copying text.

## MIT License

```text
MIT License

Copyright (c) 2026 Benjamin Turner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
```
