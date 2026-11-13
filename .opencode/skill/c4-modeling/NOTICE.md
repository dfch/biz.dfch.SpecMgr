# License notice

This skill adapts text from one MIT-licensed source:

- `jrjsmrtn/c4-skills` — the `c4-model` skill
  - Commit: `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b` (pinned and
    verified)
  - License: MIT
  - Copyright (c) 2026 Georges Martin

## Which local files adapt which source files

| Local file | Source file(s) at the pinned commit |
|---|---|
| `references/levels-and-notation.md` | `jrjsmrtn/c4-skills` `skills/c4-model/SKILL.md` (the C4 Abstractions Levels 1–4, the Notation Rules, and the Workflow Steps 1–3; the Level 3 "Elixir" mention dropped, the component-technology example made generic, the bad-label list extended with "Talks to"/"Communicates with", one system-context line added inside Level 1, and the technology-label rule widened from inter-container to every relationship) |
| `references/modeling-decisions.md` | `jrjsmrtn/c4-skills` `skills/c4-model/SKILL.md` (the Common Modeling Decisions, the Common Mistakes #1–9, and the Diagram Staleness table; the Elixir/OTP-specific mistakes #10–13 dropped, the pinned-DSL external-system passage added from this repo's observed facts, and the shared/embedded-library trap added to mistake #2) |

`SKILL.md` adapts no text (ideas only — its decisions are written from the
upstream skill's structure plus this repo's requirements (REQ-001,
REQ-006, REQ-011) and the pinned DSL's observed facts), so it carries no attribution line.

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
