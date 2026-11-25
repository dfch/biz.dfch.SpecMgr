# License notice

This skill adapts text from two MIT-licensed sources:

- `jrjsmrtn/c4-skills` — the `c4-model` skill
  - Commit: `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b` (pinned and
    verified)
  - License: MIT
  - Copyright (c) 2026 Georges Martin
- `structurizr/structurizr.github.io` — the Structurizr DSL documentation
  - Commit: `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (pinned and
    verified)
  - License: MIT
  - Copyright (c) 2022 just-the-docs (the Jekyll theme's boilerplate
    line)

## Which local files adapt which source files

| Local file | Source file(s) at the pinned commit |
|---|---|
| `references/view-selection.md` | `jrjsmrtn/c4-skills` `skills/c4-model/SKILL.md` (the "Diagram Types" tables and the "Diagram Selection Guide" questions, near-verbatim) + `structurizr/structurizr.github.io` `docs/dsl/cookbook/{system-context-view,container-view,component-view,dynamic-view,deployment-view,filtered-view,groups,custom-view}/index.md` (restated as ideas only — the view-kind list, the when-to-use guidance and the groups/filtered readability notes copy no text) |

`SKILL.md` adapts no text (ideas only — its rules are written from the
upstream skill's Diagram Types / Diagram Selection Guide structure plus
this repo's requirements (REQ-004, REQ-006, REQ-011), the spike TXT
4a09922d-bc32-4c03-86ba-d30ebc34e0b8 findings and the pinned CLI's
observed facts), so it carries no attribution line. Neither do
`references/view-size-and-keys.md` (ideas only + observed spike and
pinned-CLI facts) or `references/c4-plantuml-gotchas.md` (observed spike
facts — the spike is this repo's own document, not a licensed external
source).

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
