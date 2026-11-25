# License notice

This skill adapts text from two MIT-licensed sources:

- `jrjsmrtn/c4-skills` — the `structurizr-dsl` skill
  - Commit: `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b` (pinned and
    verified)
  - License: MIT
  - Copyright (c) 2026 Georges Martin
- `structurizr/structurizr.github.io` — the Structurizr DSL documentation
  - Commit: `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (pinned and
    verified)
  - License: MIT (per the repository's LICENSE; the boilerplate
    copyright line reads "Copyright (c) 2022 just-the-docs", the Jekyll
    theme the documentation site is built on)

## Which local files adapt which source files

| Local file | Source file(s) at the pinned commits |
|---|---|
| `references/syntax.md` | `jrjsmrtn/c4-skills` `skills/structurizr-dsl/SKILL.md` (the Syntax Fundamentals, Constants and Variables, Workspace Structure, Model Elements, Relationships + Uniqueness, and Identifiers sections; the `!docs`/`!adrs` lines inside the element blocks and the "recommended" wording of `!identifiers hierarchical` kept as-is) and `structurizr/structurizr.github.io` `docs/dsl/03-basics.md` (the `""` placeholder, comma-separated tags, brace and comment rules) and `docs/dsl/05-identifiers.md` (anonymous elements, identifier characters, relationship identifiers, the duplicate-`api` example, the groups caveat) |
| `references/views-and-styles.md` | `jrjsmrtn/c4-skills` `skills/structurizr-dsl/SKILL.md` (the Views, AutoLayout, Include/Exclude with Expressions, Styles, Themes, Terminology, Configuration, Directives, and the two non-multi-file Common Patterns sections; the URL-bearing `themes` example reduced to `theme default`, the image view dropped, and the multi-file pattern dropped) |
| `references/gotchas.md` | `jrjsmrtn/c4-skills` `skills/structurizr-dsl/SKILL.md` (the Troubleshooting table — its error strings rewritten to the pinned CLI's own output) and `structurizr/structurizr.github.io` `docs/dsl/91-faq.md` (the no-forward-referencing explanation and the `this` keyword), `docs/dsl/03-basics.md` (the quoting and brace rules), `docs/dsl/05-identifiers.md` (flat scope), `docs/dsl/07-implied-relationships.md` (implied relationships and `!impliedRelationships`), and `docs/dsl/cookbook/custom-elements/` (the `element` keyword and its metadata) |

`SKILL.md` adapts no text (ideas only — its authoring rules are written
from the two sources' structure plus this repo's requirements
(REQ-006/REQ-011) and the pinned CLI's observed error output; the
upstream Docker-CLI "Validation" section, the `!include`/`!docs`/
`!adrs` directives, the workspace-extension and multiple-workspaces
content, and all Elixir/OTP/Phoenix/Ash/Oban/umbrella patterns were
dropped), so it carries no attribution line.

## MIT License (jrjsmrtn/c4-skills)

```text
MIT License

Copyright (c) 2026 Georges Martin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## MIT License (structurizr/structurizr.github.io)

```text
MIT License

Copyright (c) 2022 just-the-docs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
