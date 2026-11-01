# Spike Report: Render Structurizr C4 Diagrams Inline in Markdown

TSK: `68f17a5c-f530-4fab-82e5-eaa62716cfc2` — executed 2026-10-30 on
`biz.dfch.SpecMgr` dev machine (Docker 29.1.3, Linux).
Full command log with real outputs: `COMMANDS.md` (same directory).
Artifacts: all exports under `/tmp/structurizr-spike/out-*`.

## 1. Executive summary

The consolidated `structurizr/structurizr` image (v2026.10.26) can be used as a
single-source-of-truth architecture DSL with a CI-friendly export story:

- **Mermaid export works for inline rendering**: the two-layer design (DSL in a
  fenced block as source, generated Mermaid blocks committed and drift-checked
  in CI) is viable. GitHub (mermaid 12.2.0) and VS Code (mermaid 11.17.0) both
  render all tested views, including the sequence variant. All text exports
  (mermaid, plantuml, c4plantuml, static, json) are **byte-identical between
  runs** — a CI drift check is reliable.
- **Kroki is not viable** for this goal: the structurizr diagram type is
  **POST-only** (no GET image URL, so no markdown embedding), the default
  settings cap the POST body at **~1170 bytes**, it renders only the **first
  view** (no view-key option; the DSL `default` statement is ignored), and
  SECURE mode blocks `!include`.
- **Pre-rendered SVG/PNG works** (GitHub displays them) but needs the
  6.31 GB `:playwright` image in CI and the output is **not byte-stable**
  (a minute-granularity UTC timestamp is baked into every diagram) — committed
  SVGs would fail a drift check every minute.
- **Structurizr does not do UML use case or class diagrams** (experimentally
  confirmed): custom elements approximate them as labelled boxes; the PlantUML
  export even maps the Ellipse shape to a `storage` cylinder.

Recommendation: **adopt Structurizr with Mermaid export (two-layer design)**
for C4 views (system context, container, component, deployment, dynamic/
sequence), keep PlantUML (specmgr's existing surface) for UML use case and
class diagrams. Full recommendation in section 7.

## 2. Environment

| Item | Value |
|---|---|
| CLI image | `structurizr/structurizr:latest` = `:2026.10.26-noble` = structurizr **2026.10.26**, structurizr-* 6.2.4, Java 21 |
| Playwright image | `structurizr/structurizr:2026.10.26-playwright` (6.31 GB; Chromium prebundled, no runtime download) |
| MCP image | `structurizr/mcp:latest` = v2026.04.20 (lags the CLI line) |
| Kroki | `yuzutech/kroki:0.34.0`, default settings, port 8090 |
| Local PlantUML server | `plantuml/plantuml-server:tomcat`, port 9898, render endpoint `/svg/<enc>` (pure SVG) — used only to verify .puml outputs render |
| Web UI | `structurizr/structurizr:2026.10.26-noble` with `command: local` on port 9797 (compose adjustment per user) |
| GitHub | mermaid **12.2.0** (section 0 `info` probe) |
| VS Code | mermaid **11.17.0** (section 0 `info` probe) |

Note: there is no bare `noble`/`playwright` tag on Docker Hub — only dated
`2026.10.26-noble` / `2026.10.26-playwright` (Task 1's "noble" adjusted
accordingly). `latest` equals the 2026.10.26 release.

## 3. Results: platforms × view types

User-verified manual checks (mermaid-test.md / svg-test.md, section 0 = version probe):

| Platform | renderer | System context | Container | Deployment | Dynamic (collaboration) | Dynamic (sequence) | Pre-rendered SVG |
|---|---|---|---|---|---|---|---|
| GitHub.com | mermaid 12.2.0 | renders | renders | renders | renders | renders | displays (4/4 views) |
| VS Code | mermaid 11.17.0 | renders | renders | renders | renders | NOT REPORTED | — (local files) |
| GitLab | — | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| Forgejo | — | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

Kroki (local, all four view types in one workspace): renders only the **first
view in document order**, single-view workspaces ≤ ~1170 B → SVG; multi-view
or larger → HTTP 400. Not embeddable in markdown (no GET URL form).

## 4. Results: export formats (CLI, v2026.10.26)

| Format | Command | Output | Views covered | Byte-stable across runs | Notes |
|---|---|---|---|---|---|
| mermaid | `export -f mermaid -o <dir>` | `structurizr-<viewkey>.mmd` per view | context, container, dynamic (collab or sequence), deployment, **custom** | YES | Node/edge labels are HTML `<div>` fragments; docs say renderers need `securityLevel: "loose"` — GitHub 12.2.0 / VS Code 11.17.0 rendered them anyway (user-verified). No `%%{init}%%` emitted. `properties { mermaid.sequenceDiagram true }` switches a dynamic view to `sequenceDiagram` (only `<br />` tags). |
| plantuml | `export -f plantuml -o <dir>` | `structurizr-<key>.puml` **+** `structurizr-<key>-key.puml` (legend) per view | same as mermaid | YES | Self-contained (`<style>` block, no includes); `shape Person` → `person` node, `shape Ellipse` → `storage` (wrong); relationships dashed by default. |
| plantuml/c4plantuml | `export -f plantuml/c4plantuml -o <dir>` | one `structurizr-<key>.puml` per view | same as mermaid | YES | Compact C4-PlantUML with `!include <C4/C4>` — needs a PlantUML server that can resolve the C4 library (worked on the local server with internet; offline CI must provision it). |
| static | `export -f static -o <dir>` | 25 files, 2.4 MB: index.html + workspace.js (base64 JSON) + vendored JS/CSS | all views + interactive navigation | YES | Client-side JointJS rendering (JS required); fully relative paths (no remote fetch); serve with any static server; browser/file:// behaviour NOT TESTED. |
| json | `export -f json -o <dir>` | one workspace JSON | — | YES | Useful for CI assertions; auto-carries `structurizr.dsl` (base64 source) + inspection counters. |
| svg | `export -f svg -o <dir>` (playwright image) | `<key>.svg` + `<key>-key.svg` per view | all | **NO** — timestamp "Friday, October 30, 2026 at H:MM PM Coordinated Universal Time" (UTC, minute granularity) baked in as a text node | Headless works (~3.6 s incl. JVM start); can also target a running local/server instance via `-url <diagrams page>`. |
| png | `export -f png -o <dir>` (playwright image) | `<key>.png` + `<key>-key.png` per view | all | **NO** — timestamp rendered into pixels (20 kB of a 99 kB file differed across minutes) | ~3.4 s; 33–164 kB per view. |

Dynamic view numbering: steps declared in order get `order` 1..N in the model
(rendered as "1. …" labels in the collaboration diagram, message order in the
sequence diagram).

## 5. Key findings

1. **v2 DSL is a breaking grammar change.** The consolidated image rejects the
   classic DSL (`systemContext ss "Name" "Desc"` fails with
   `View keys can only contain the following characters: a-zA-Z0-9_-`). v2:
   views take `[key] [description]` (key charset `a-zA-Z0-9_-`; auto-generated
   keys are explicitly *not stable* — mandate explicit keys for stable export
   filenames), `deploymentEnvironment` lives in `model`, deployment views need
   explicit `include *` (empty view otherwise), dynamic steps are plain
   ordered lines. Reference: docs.structurizr.com/dsl/language.
2. **validate is a weak gate.** Silent success (exit 0); single-line errors
   `ERROR ... -- <message> [at line N of <path>: <line>]` (exit 1). An
   **unterminated string is silently truncated** (not caught). `inspect` adds
   an opinionated lint (scope, `noview`, empty views, missing technologies —
   `ERROR | rule | message` lines) — use both in CI.
3. **Metadata goes in workspace `properties`**, not YAML frontmatter
   (frontmatter → `Unexpected tokens (expected: workspace) at line 1: ---`).
   `properties { id "..." status "..." }` round-trips into the JSON export.
4. **`!include` is permissive in the CLI**: subdirectory and sibling-subdir
   fragments work, and a `../` escape outside the parent directory tree also
   works (contradicting the docs' "must be in the parent file directory or a
   subdirectory" claim). Fragments splice in verbatim at the include point
   (no wrapping `model{}` inside a fragment included into a model). Errors are
   cascaded (fragment line + include line).
5. **Kroki structurizr type**: POST-only (GET base64 URL form rejected for all
   encodings), default POST body limit ≈ 1170 B (1160 OK / 1180 400,
   `TooLongFormFieldException`), first view only (no query-param view key, DSL
   `default` ignored), SECURE mode: `!include <file> is not permitted (feature
   structurizr.feature.dsl.filesystem is not enabled)`.
6. **structurizr/mcp** (v2026.04.20): stateless streamable-HTTP at `POST /mcp`;
   tools `validate`, `parse`, `inspect` — each takes one inline `dsl` string;
   **no export tools** (contrary to the research notes); failures return error
   text with `isError: false` (read the text, not the flag); fully offline
   (`--network none` verified). OpenCode config:
   `{"mcp": {"structurizr": {"type": "remote", "url": "http://localhost:8091/mcp", "enabled": true}}}`.
7. **UC approximation** (custom elements + custom view + element styles):
   exports to plantuml/mermaid/static; person shape OK, Ellipse → storage; no
   usecase nodes, no `<<include>>`/`<<extend>>` stereotypes, dashed
   relationships — a recognisable labelled graph, not UML.
8. **Class approximation** (attributes in element metadata, multiplicities as
   relationship labels): labelled rectangles with bracketed attribute text —
   experimentally confirms there is no class-diagram notation (no
   compartments, visibility glyphs, stereotypes, association ends).
9. **Docker gotcha for CI**: `-v` to a non-existent host path auto-creates it
   as a **root-owned** file/dir — pre-create the workspace directory.
10. **Cloud themes ship in the image** (`/usr/local/structurizr-themes/`:
    AWS, Azure, GCP, OCI, Kubernetes, light/dark) — usable via `theme <name>`.

## 6. Two-layer design verdict (DSL source → committed generated Mermaid → CI drift check)

**Works**, with these operational rules (all empirically grounded):

- Extract the fenced block in 2 lines of shell:
  `sed -n '/^```structurizr$/,/^```$/p' <file> | sed '1d;$d' > /tmp/ws.dsl`
  (needs a unique fence language; validated end-to-end in Task 13).
- Gate with `validate` **and** `inspect` (validate alone misses e.g. unterminated
  strings; inspect flags structural smells).
- Export with `-f mermaid` into a deterministic filename derived from an
  **explicit view key** (auto keys like `SystemContext-001` are unstable).
- Drift check = `diff` of the committed `.mmd` (byte-stable, verified).
- Fragility to watch: the div-label output depends on the renderer's mermaid
  version/config (GitHub 12.2.0 and VS Code 11.17.0 passed today; the
  documented `securityLevel: loose` requirement means a stricter future
  renderer could strip labels without a syntax error). Mitigation: keep the
  `.mmd` in the repo (diff catches content change even if a renderer degrades
  display), optionally render-verify in CI via a headless mermaid check.
- SVG/PNG committed artifacts are **not** drift-checkable as-is (timestamp);
  if ever needed, strip the timestamp text node (svg) or compare dimensions
  only (png).

## 7. Recommendation

**Adopt Structurizr for C4-style architecture views with Mermaid export
(two-layer design); keep PlantUML for UML use case and class diagrams.**

Rationale per candidate:

- **Mermaid export (recommended)**: single-source DSL, byte-stable generated
  text, renders on the target platforms today (GitHub + VS Code verified),
  no binary artifacts, trivial CI (docker CLI, ~1 s per export), sequence
  variant for dynamic views, custom views export too.
- **Kroki (rejected for this goal)**: POST-only + ~1.2 kB default limit +
  first-view-only + no markdown URL embed.
- **Pre-rendered SVG (not recommended as primary)**: displays everywhere
  (GitHub verified) but 6.3 GB CI image, non-deterministic bytes, static
  images, repo bloat. Keep as an optional output for non-mermaid consumers.
- **Dropping Structurizr (not recommended)**: the C4 coverage (context /
  container / deployment / dynamic-sequence from one model) plus the
  deterministic text exports and the offline MCP validator are a genuine
  complement to specmgr's PlantUML-only diagram surface; the gaps (UC/class
  UML notation) are exactly where PlantUML stays.

Practical split: `str`-style artifacts hold the Structurizr DSL (workspace
`properties` carrying the specmgr `id`/`status` metadata); CI extracts,
validates (`validate` + `inspect`), exports mermaid, drift-checks the committed
`.mmd` blocks; UML use case and class diagrams remain PlantUML-rendered as
today.

## 8. NOT TESTED / unverified

- GitLab and Forgejo rendering (user scope: GitHub.com only) — incl. their
  mermaid versions.
- VS Code section 5 (sequence variant) — user reported 1–4 only; the exact
  VS Code preview used (built-in / Markdown Preview Enhanced / Mermaid
  extension) was not specified.
- Whether the div labels render **with full label text** or degrade gracefully
  (user reported "rendered diagrams" for all sections; no per-label
  screenshot comparison was made).
- `!include` via **https** URL (CLI and otherwise) — skipped by user decision.
- Static site behaviour in a real browser (incl. `file://`) — file structure,
  relative paths and serialized JSON verified only.
- Playwright svg/png export on an actual CI runner (verified headless on this
  machine's Docker; "works in CI" is inferred from the self-contained image).
- `export -f svg|png -url <running local instance>` variant (only the
  `-workspace` variant was exercised).
- `structurizr/mcp` through a real OpenCode MCP client (raw JSON-RPC over HTTP
  tested, incl. offline); the suggested `opencode.json` snippet is untested.
- Dark mode (`-mode dark`), animation export (`-animation true`), the
  `playground` command, `websequencediagrams`/`theme`/`fqcn` formats,
  `workspace extends <url>`.
- Whether GitHub renders the mermaid `info` probe identically in issues/wikis
  vs. repository files (user pushed a repo; wiki/issue rendering not checked).

## 9. Exact commands (abridged; full log in COMMANDS.md)

```bash
# one-shot CLI (all export/validate/inspect calls use this shape)
docker run --rm -v /tmp/structurizr-spike:/usr/local/structurizr \
  structurizr/structurizr:2026.10.26-noble validate -w workspace.dsl
docker run --rm -v /tmp/structurizr-spike:/usr/local/structurizr \
  structurizr/structurizr:2026.10.26-noble export -w workspace.dsl -f mermaid -o out-mermaid
docker run --rm -v /tmp/structurizr-spike:/usr/local/structurizr \
  structurizr/structurizr:2026.10.26-playwright export -w workspace.dsl -f svg -o out-svg
docker run -d --name kroki-spike -p 8090:8000 yuzutech/kroki:0.34.0
curl -s -X POST --data-binary @workspace.dsl http://localhost:8090/structurizr/svg
docker run -d --name mcp-spike -p 8091:8080 structurizr/mcp:latest   # POST /mcp JSON-RPC
# fenced-block extraction (2 lines)
sed -n '/^```structurizr$/,/^```$/p' arch.md | sed '1d;$d' > extracted.dsl
```
