# Structurizr Spike - Command Log

Running log of every command executed and its real output. Task 19 assembles REPORT.md from this.

## Phase 0: container adjustment (~/docker/structurizr)

- `docker compose up -d` -> recreated structurizr service on `structurizr/structurizr:2026.10.26-noble` with `command: local` (was EOL `structurizr/lite`); plantuml-server kept on 9898.
- Web UI check: `curl http://localhost:9797/` -> 302 (redirect into the local app); log shows `com.structurizr.server.Local` started, created stub `workspace.dsl` in the mounted dir.
- PlantUML server render endpoint: `curl http://localhost:9898/svg/<enc>` -> 200 image/svg+xml (verified with a Bob->Alice test diagram; encoding cross-checked against the specmgr plantuml_encode tool).

## Task 1: pull images and record versions

- `docker pull structurizr/structurizr:latest` -> ok (digest sha256:8aebde645a7cc8...); `:2026.10.26-noble` already pulled by `docker compose up -d`.
- `docker run --rm structurizr/structurizr:latest` (no args) -> prints usage only: `Usage: playground|local|server|push|pull|lock|unlock|branches|create|delete|regenerate-apikey|export|generate|merge|validate|inspect|list|version|help [arguments]` (exit 0, no version).
- `docker run --rm structurizr/structurizr:latest version` -> structurizr: 2026.10.26, structurizr-*: 6.2.4, Java 21.0.13 (Temurin), Linux amd64.
- `docker run --rm structurizr/structurizr:2026.10.26-noble version` -> structurizr: 2026.10.26, structurizr-*: 6.2.4, Java 21.0.12.1, Linux amd64.
- NOTE: `latest` == the 2026.10.26 release; no bare `noble`/`playwright` tags exist (verified on Docker Hub API). Task 8 will use `2026.10.26-playwright`.

## Task 2: workspace.dsl

- First draft in classic v1 DSL failed validation with: `ERROR com.structurizr.command.ValidateCommand -- View keys can only contain the following characters: a-zA-Z0-9_- at line 19 ...` -> the consolidated image (2026.10.26) ships a NEW v2 DSL grammar; v1 view syntax (`systemContext ss "Name" "Description"`) is not accepted.
- Consulted https://docs.structurizr.com/dsl/language (v2 reference): views take `[key] [description]` (key charset a-zA-Z0-9_-), `deploymentEnvironment` moved into `model`, dynamic steps are plain ordered `<src> -> <dst> "description"` lines (optional `[order:]` prefix), explicit view keys recommended (auto-generated keys are "not guaranteed to be stable").
- Rewrote workspace.dsl in v2 grammar: person Alice; software systems Shop (containers Web App + Database, web->db SQL) and Payment Provider; relationships alice->web HTTPS, web->payment HTTPS/JSON; deploymentEnvironment "Live" with App Server (containerInstance web) + DB Server (containerInstance db); views: systemContext (key shop-system-context), container (key shop-containers), deployment (key live-deployment, needs explicit `include *` - without it the view is empty, inspect reports `views.view.empty`), dynamic (key checkout, title "Checkout", 3 steps).
- `export -f json` confirmed: dynamic view relationships carry order 1/2/3 with the step descriptions; deployment view has 4 elements (2 nodes + 2 container instances) and 1 relationship.

## Task 3: validate behaviour

- `validate -w workspace.dsl` (clean) -> NO output, exit 0.
- broken variant 1 (unterminated string on dynamic step line `alice -> web "Submits the order`) -> NO output, exit 0 (!). JSON export of the broken file shows the description silently truncated to `Submits the order` - this typo class is NOT caught by validate.
- broken variant 2 (missing closing braces, last 2 lines removed) -> `ERROR com.structurizr.command.ValidateCommand -- Unexpected end of DSL content - are one or more closing curly braces missing?`, exit 1.
- broken variant 3 (unknown keyword `titel`) -> `ERROR com.structurizr.command.ValidateCommand -- The relationship "titel" does not exist at line 43 of /usr/local/structurizr/workspace-broken3.dsl: titel "Checkout"`, exit 1.
- Error format: single line `HH:MM:SS.mmm [main] ERROR com.structurizr.command.ValidateCommand -- <message> [at line <N> of <absolute path>: <offending line text>]`, exit code 1; success is silent, exit 0.
- `inspect -w <file>` additionally runs a lint (workspace scope, documentation, deployment node technology, `model.element.noview`, `views.view.empty` findings, `ERROR | <rule> | <message>` lines) - a second, more opinionated gate.
- CLI notes: consolidated image requires `-w/--workspace` (positional arg fails with `Missing required option: w`, exit 1); `version` command prints structurizr: 2026.10.26 / structurizr-*: 6.2.4.

## Task 4: mermaid export

- `export -w workspace.dsl -f mermaid -o out-mermaid` -> 4 files, one per view: `structurizr-<viewkey>.mmd` (16-24 lines each): structurizr-shop-system-context.mmd, structurizr-shop-containers.mmd, structurizr-checkout.mmd, structurizr-live-deployment.mmd. Exit 0. Full contents of each recorded in this log below (all < 40 lines).
- KEY FINDING: node labels are HTML `<div>` fragments (`1["<div style='font-weight: bold'>Alice</div><div style='font-size: 70%'>[Person]</div>..."]`), edge labels use `<div>` too, files start with `graph LR` / `sequenceDiagram` and contain NO `%%{init}%%` securityLevel directive. Docs (docs.structurizr.com/export/mermaid) state: "Your Mermaid configuration will need to include securityLevel: loose to render the diagrams correctly." GitHub/GitLab/VS Code default to strict -> divs are sanitized; this is the central inline-rendering risk (to be confirmed in tasks 9/10).
- View property `mermaid.title` (default true) and `mermaid.sequenceDiagram` (default false = collaboration) can be set per view or on the view set (`properties { mermaid.sequenceDiagram true }`).
- Files have no trailing newline; node ids are numeric element ids (1,2,3,6,11,12...), subgraphs for boundaries ("Shop"), dotted edges `-. "label" .->`.

## Task 5: sequenceDiagram property

- Created workspace-seq.dsl = workspace.dsl + `properties { mermaid.sequenceDiagram true }` inside the checkout dynamic view; exported to out-mermaid-seq.
- The three non-dynamic views are byte-identical between the two exports (per-view property isolation confirmed).
- checkout COLLABORATION: `graph LR` with numbered step edge labels "1. Submits the order" etc.
- checkout SEQUENCE: proper `sequenceDiagram` with `participant 1 as Alice<br />[Person]` (4 participants) and messages `1->>3: Submits the order<br />[HTTPS]` - only `<br />` HTML, no divs. Numbered steps appear in message order (1,2,3 as declared).

## Task 6: plantuml + c4plantuml exports

- `export -f plantuml -o out-plantuml` -> TWO files per view: `structurizr-<key>.puml` (self-contained: @startuml, title, `left to right direction`, `<style>` block with per-element-type styling, `hide stereotype`, rectangle labels with `==` prefix which PlantUML strips at render, dashed relationship lines) + `structurizr-<key>-key.puml` (the legend/key diagram: same styles plus a transparent-element legend explaining element/relationship markings).
- `export -f plantuml/c4plantuml -o out-c4plantuml` -> ONE file per view, compact C4-PlantUML: `!include <C4/C4>` + `!include <C4/C4_Context>` / `C4_Container` as needed, System_Boundary/Container/Person/System/Rel macros, `SHOW_LEGEND(true)`.
- Render-verified both against the local plantuml-server (http://localhost:9898/svg/<enc>): plain puml renders standalone; c4plantuml `!include <C4/C4>` ALSO resolved on the local server (server fetched the C4 library - works here because the machine has internet; in an offline CI this dependency must be considered). No syntax errors, labels clean (no stray `==` glyphs in output).
- View types produced: system context, container, dynamic (checkout), deployment - i.e. all 4 views in the workspace, same coverage as mermaid.

## Task 7: static export

- `export -w workspace.dsl -f static -o out-static` -> 25 files, 2.4 MB: index.html + workspace.js (base64-encoded workspace JSON `const jsonAsString = 'eyJ...'`) + css (bootstrap 5.3.7, structurizr.css, light/dark static css) + js (jquery, bootstrap, crypto-js, dagre, graphlib, jointjs, structurizr-*.js) + img (favicon, banners).
- ALL references are relative (./js/..., ./img/...) - fully self-contained, no remote fetches. Diagrams are rendered CLIENT-SIDE by JointJS+dagre (JS required; not pre-rendered images). Viewing: any static web server (e.g. `python3 -m http.server` in out-static), or open index.html directly in a browser (file:// - untested in a browser here).

## Task 8: svg + png via playwright tag

- Pulled `structurizr/structurizr:2026.10.26-playwright` (6.31 GB image vs 912 MB noble - Chromium + OS deps bundled; docs say the plain prebuilt image does NOT support this, the :playwright tag does).
- `export -w workspace.dsl -f svg -o out-svg`: writes the static site to a temp dir, drives headless Chromium at `file:///tmp/structurizrNNN/index.html` (Prebundled - no browser download at runtime), captures per view. Result: `<viewkey>.svg` + `<viewkey>-key.svg` (8 files, 922 B - 16 KB), exit 0, wall time 3.6 s (incl. JVM start).
- `export -w workspace.dsl -f png -o out-png`: same flow, `<viewkey>.png` + `-key.png` (8 files, 33 KB - 164 KB; e.g. shop-system-context.png = 2430x700 RGBA), wall time 3.4 s.
- Content verified: SVGs carry the full JointJS rendering (title, element labels+metadata, relationship labels, icons as <image>).
- KEY FINDING: the exported SVG embeds a timestamp text node ("Friday, October 30, 2026 at 2:56 PM Coordinated Universal Time") -> svg/png export is NOT byte-stable between runs (task 18 will confirm; committed SVG artifacts would drift on every CI run unless the timestamp is stripped).
- Docs note: PNG/SVG export can also target a running local/server instance via `-url <diagrams page>` (e.g. http://localhost:9797/workspace/1/diagrams) instead of `-workspace`.

## Task 11: Kroki (yuzutech/kroki:0.34.0, default settings, port 8090)

- `docker run -d --name kroki-spike -p 8090:8000 yuzutech/kroki:0.34.0`; `GET /health` -> 200.
- POST DSL to `http://localhost:8090/structurizr/svg` (raw body, curl --data-binary):
  - minimal single-view workspace (204 B) -> 200, image/svg+xml, 2962 B, correct System Context rendered.
  - full 4-view workspace (1635 B) -> 400 "Error 400: Internal Server Error"; server log: `TooLongFormFieldException`. Size narrowed by padding tests: 1160 B -> 200, 1180 B -> 400. DEFAULT-SETTINGS POST BODY LIMIT ~= 1170 BYTES - a severe constraint for API consumers.
  - two-view workspace (376 B) -> 200: Kroki renders the FIRST view in document order. Adding the `default` statement to the second view does NOT change that (still first view, byte-identical output). There is NO view-key query option (`?view=`, `?key=`, `?viewKey=` all 400 with the same size error on the big file; on small files they are ignored and the first view renders).
- GET form `http://localhost:8090/structurizr/svg/<base64>` is NOT supported for the structurizr type: standard base64 -> 400 "Unable to decode the source. The source is not in valid Base64 scheme"; urlsafe base64 -> 400 "Unable to decode the source." (fails even for a 204 B source). Conclusion: the structurizr type is POST-only, so it CANNOT be embedded in markdown via a kroki image URL.
- SECURE mode include test: workspace with `!include ./kroki-frag.dsl` -> 400: `Unable to parse the Structurizr DSL. !include <file> is not permitted (feature structurizr.feature.dsl.filesystem is not enabled) at line 2: !include ./kroki-frag.dsl.` - confirms the context finding; the feature gate name is `structurizr.feature.dsl.filesystem`.
- Error format: plain text `Error 400: <message>`, with DSL parse errors carrying `at line N: <line text>`.

## Task 13 (prepared files for task 9/10)

- mermaid-test.md: sections 0-5 (info version probe + 4 exported collaboration views + sequence variant), verbatim .mmd content in fenced mermaid blocks.
- svg-test.md: 4 headings, each embedding out-svg/<viewkey>.svg as a markdown image (relative paths).
- github-push/: self-contained copy (mermaid-test.md, svg-test.md, out-svg/*.svg) for the user's GitHub scratch repo.
## Task 12: include directive with the CLI

- Test workspaces: workspace-inc.dsl (!include of a fragment), workspace-inc-sib2.dsl (sibling subdir), workspace-inc-out.dsl (../ escape, second mount).
- (a) `!include ./includes/frag.dsl` INSIDE the model block, fragment in a subdirectory -> validate exit 0 (works).
- (b) fragment moved to sibling/ (still under the parent dir) -> exit 0 (works).
- (c) `!include ../sibling/frag.dsl` with the file OUTSIDE the parent dir tree (mounted at /usr/local/sibling) -> exit 0 (WORKS - the docs claim "local !include paths must be in the parent file directory or a subdirectory" is NOT enforced by the v2026.10.26 CLI; resolution is plain filesystem-relative from the including file).
- Error formats recorded:
  - fragment content at the wrong nesting level: `Unexpected tokens (expected: name, description, properties, !docs, !decisions, !identifiers, !impliedRelationships, model, views, configuration) at line 1 of /usr/local/structurizr/./includes/frag.dsl: <line> at line 2 of /usr/local/structurizr/workspace-inc.dsl: !include ./includes/frag.dsl` (cascaded: included-file location + include-statement location)
  - fragment carrying its own `model {}`: `Multiple models are not permitted in a DSL definition at line 3 of <parent>`
  - missing file: `/usr/local/sibling/frag.dsl could not be found at line 2 of <parent>: !include ../sibling/frag.dsl`
- https include: NOT TESTED (skipped by user decision).
- NOTE: fragments are spliced in verbatim at the include point - they must carry statements valid at that nesting level (no wrapping model{} block).

## Task 13: fenced-block extraction with shell tools

- arch.md carries a ```structurizr fenced block (16 lines incl. fences).
- Extraction (2 lines): `sed -n '/^```structurizr$/,/^```$/p' arch.md | sed '1d;$d' > extracted.dsl` -> 14-line DSL.
- `validate -w extracted.dsl` -> exit 0; `export -f mermaid -o out-extract` -> 1 file `structurizr-SystemContext-001.mmd`.
- Verdict: A FEW LINES OF SHELL ARE ENOUGH for a CI step (extract -> validate -> export -> drift-check), provided the fence marker is unique (```structurizr) and the block is the only one of that language. Caveats: (1) docker -v auto-creates missing host bind-mount paths as ROOT-owned files/dirs - pre-create the workspace dir in CI; (2) without explicit view keys the exporter generates unstable keys (SystemContext-001) - mandate explicit keys for stable filenames in a two-layer design.

## Task 14: YAML frontmatter + workspace properties

- (A) File starting with a `---` YAML frontmatter block before `workspace`: REJECTED - `Unexpected tokens (expected: workspace) at line 1 of /usr/local/structurizr/fm-test.dsl: ---`, exit 1. No frontmatter support, ever.
- (B) `properties { id "12345678-..." status "active" }` block directly under `workspace`: ACCEPTED (exit 0); the exported JSON's workspace `properties` map carries `id` and `status` verbatim, plus auto-added `structurizr.dsl` (base64 of the DSL source) and `structurizr.inspection.{info,warning,error}` counters. Metadata belongs in workspace properties, not frontmatter.

## Task 15: structurizr/mcp image

- `structurizr/mcp:latest` = v2026.04.20 (image lags the CLI line - 2026.04 vs 2026.10). Stateless streamable-HTTP MCP server; endpoint `POST /mcp` (GET / -> 302 to docs.structurizr.com/ai/mcp; GET /mcp -> 405). No session id required (Mcp-Session-Id absent).
- Tools (discovered via tools/list): `validate`, `parse`, `inspect` - each takes exactly one `dsl` string parameter (inline DSL). NO export tool exists in the image (the research notes claiming mermaid/plantuml/c4plantuml export tools do not match v2026.04.20).
- Calls: validate(valid) -> {"content":[{"type":"text","text":"OK"}],"isError":false}; validate(bad) -> the error text (e.g. `Unexpected tokens (expected: ...) at line N: <line>`) is returned with isError:FALSE - failure detection requires reading the text, not the isError flag. parse(valid) -> the full workspace JSON inline (1333 bytes for the minimal workspace).
- OFFLINE: container started and served requests with `--network none` (tested via a curl container sharing its network namespace) - validate returned "OK". Fully self-contained; no model/registry calls.
- OpenCode client config example (opencode.json): {"mcp": {"structurizr": {"type": "remote", "url": "http://localhost:8091/mcp", "enabled": true}}} (with `docker run -d -p 8091:8080 structurizr/mcp:latest`).
## Task 16: UC approximation (custom elements + custom view)

- uc-approx.dsl: three custom `element`s (Customer tagged Actor; Place Order, Pay tagged UseCase) + relationships (performs x2, includes x1); `custom "uc-view"` view with include + autoLayout; element styles shape Person / shape Ellipse.
- validate exit 0; export works for plantuml (2 files incl. -key legend), mermaid (1 file - the context note "Mermaid export does not list custom views" is WRONG for v2026.10.26) and static.
- PlantUML output: `person "==Customer\n<size:16>[An actor of the shop]</size>"` (shape Person -> PlantUML person node, OK) but `storage "==Place Order..."` (shape Ellipse -> PlantUML storage/cylinder, WRONG - there is no usecase mapping). Relationships are dashed (`LineStyle: 10-10`) plain arrows with text labels; no `<<include>>`/`<<extend>>` stereotypes, no solid actor associations, no system boundary ellipse.
- Rendered locally against plantuml-server: 200, content correct.
- Mermaid output: plain graph LR rectangles with div labels, no actor/usecase shapes (mermaid flowchart has none).
- Static site: shapes Person/Ellipse survive into the serialized workspace JSON (rendered client-side by JointJS; NOT visually verified in a browser here).
- Missing UML notation verdict: usecase ellipse (PlantUML export maps it to a cylinder), include/extend stereotyped arrows, actor association style, multiplicity - i.e. the UC diagram is recognisable as a labelled graph, not UML.

## Task 17: class approximation (three classes)

- class-approx.dsl: elements Order/OrderLine/Customer tagged Class; attribute+method lists carried in the element `metadata` string (e.g. "- id: string\n- total: decimal\nplace()"); associations with multiplicity labels (1..*, 0..*); style shape Box + metadata true.
- validate exit 0; plantuml export (2 files) + static export (25 files) produced.
- PlantUML output: three `rectangle` nodes, attributes rendered as bracketed small-font label text `==Order\n<size:16>[- id: string\n- total: decimal\nplace()]</size>`; associations are dashed arrows with the multiplicity as an edge label (`1 --> 2 : "1..*"`).
- Rendered locally: 200, readable.
- Verdict: EXPERIMENTALLY CONFIRMS no-class-diagram - no class compartments (attribute/method sections), no visibility glyphs, no <<class>> stereotype, no UML association ends (multiplicity is just an edge label), no aggregation/composition diamonds. It is a labelled-box diagram that a reader can interpret as classes, not a UML class diagram.

## Task 18: determinism

- Each export run twice (separate output dirs, separate containers), diff -r:
  - mermaid: BYTE-IDENTICAL
  - plantuml: BYTE-IDENTICAL (incl. -key legend files)
  - plantuml/c4plantuml: BYTE-IDENTICAL
  - json: BYTE-IDENTICAL
  - static: BYTE-IDENTICAL (25 files incl. workspace.js)
  - svg: byte-identical only when both runs land in the same minute; across a minute boundary 4 of 8 files differ - the ONLY difference is the baked-in timestamp text node "Friday, October 30, 2026 at H:MM PM Coordinated Universal Time" (UTC, minute granularity, top-left of the diagram)
  - png: likewise differs across a minute (20,296 bytes from offset 78571, no tEXt metadata - the timestamp is rendered into pixels); -key legend PNGs identical
- CI drift-check verdict: the two-layer design (DSL source + committed generated artifacts) is viable for the TEXT formats (mermaid .mmd, plantuml .puml, c4plantuml .puml, static site, json) - all byte-stable. For committed svg/png, the timestamp must be stripped (single text node in svg; for png: exclude from diff or compare pixel-dimensions only) or the drift check must normalise it.
## Tasks 9-10: manual render checks (user report, 2026-10-30)

- GitHub.com (mermaid 12.2.0, via section 0 `info` probe): mermaid-test.md sections 1-5 ALL render as diagrams (system context, container, deployment, checkout collaboration, checkout sequence) - no error reported. svg-test.md: all 4 pre-rendered SVG images display.
- VS Code (mermaid 11.17.0, via section 0 probe): mermaid-test.md sections 1-4 render as diagrams; section 5 (sequence variant) NOT REPORTED by the user. Which preview (built-in / MPE / Mermaid extension) was NOT specified.
- Implication: the documented "securityLevel loose required" caveat did NOT prevent rendering on GitHub mermaid 12.2.0 or VS Code mermaid 11.17.0 - the div-based labels render (or degrade gracefully without visible breakage, per user observation). Still a fragility point: renderer-side config is outside our control.

