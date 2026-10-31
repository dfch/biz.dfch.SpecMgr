---
classification: null
created: '2026-10-30T10:21:03.414+01:00'
id: 68f17a5c-f530-4fab-82e5-eaa62716cfc2
status: active
type: tsk
updated: '2026-10-30T19:17:09.938+01:00'
version: 1.0.0
---

# Spike: Render Structurizr C4 Diagrams Inline in Markdown

<!-- CONTEXT FOR A FRESH AGENT. Repo: biz.dfch.SpecMgr (specmgr MCP server, see AGENTS.md). Specmgr uses PlantUML today for UC and reference-graph diagrams. Drawbacks: no Python parser, validation needs a jar/container, no inline rendering in markdown, extra puml/svg files. The user wants diagrams for system and software architecture (component, class, UC, sequence, deployment), rendered inline in markdown in VS Code, GitHub, GitLab and Forgejo (no dependency on one git platform), and built in a CI pipeline. Java and Docker are allowed. The user prefers a single source of truth and is considering a new specmgr artifact type (working name str) that holds Structurizr DSL (C4 model as code) in a fenced block and is referenced from other specmgr documents.

FINDINGS SO FAR (from docs, NOT verified by experiment). Structurizr (structurizr/structurizr, Apache-2.0, Docker image structurizr/structurizr, tags latest, noble for CI, playwright for PNG/SVG export; Java 21 war also exists) has commands validate, inspect, export, local, playground; only the server command needs a paid licence and must NOT be used. Export formats: mermaid, plantuml, plantuml/c4plantuml, static, png, svg, json. The Structurizr Mermaid export page says Mermaid needs securityLevel loose to render correctly; GitHub, GitLab and Forgejo control that setting, so rendering there is UNVERIFIED. Dynamic views export to a sequence diagram with the view property mermaid.sequenceDiagram true (or plantuml.sequenceDiagram true); default is a collaboration diagram. Structurizr has no class diagram and no real UML use case diagram (custom elements and custom view only, and Mermaid export does not list custom views). The structurizr/mcp image (Docker, stateless HTTP) offers tools to validate DSL, parse DSL to JSON, and export a view to Mermaid, PlantUML or C4-PlantUML; each takes DSL as an inline string. Kroki (yuzutech/kroki) renders a structurizr diagram type but its default SECURE mode disables !include, !docs and !adrs for Structurizr. Local !include paths must be in the parent file directory or a subdirectory. The DSL has comment syntax (double slash, hash, block comments) and no documented YAML frontmatter support.

RULES FOR THIS SPIKE. Read-only toward the repository. Write all artifacts ONLY under /tmp/structurizr-spike. Do not commit, do not edit any repo file. Do not use the Structurizr server command. Do not send diagram content to public services (kroki.io, mermaid.ink, mcp.structurizr.com). Record every command you ran and its real output. Mark anything you could not test as NOT TESTED, never guess. Ask the user via the question tool for the manual checks on GitHub, GitLab and Forgejo. Finish with a report as a markdown file at /tmp/structurizr-spike/REPORT.md and a short summary to the user. Use specmgr tools (list_tsk, get_tsk, update) only to tick items and add Recent Updates entries in THIS task list. -->

- [x] Task 1: Pull the docker image structurizr/structurizr (tags latest and noble) and confirm the version of each with the docker run command and no arguments or the help output; record both versions

- [x] Task 2: Create /tmp/structurizr-spike/workspace.dsl with one person, two software systems, one system with a web container and a database container, relationships, a systemContext view, a container view, a deployment environment Live with nested deployment nodes and container instances plus a deployment view, and a dynamic view named Checkout with three numbered steps

- [x] Task 3: Run the validate command on workspace.dsl via docker with /tmp/structurizr-spike mounted at /usr/local/structurizr and record the output; then introduce one deliberate syntax error and record the error message format and exit code

- [x] Task 4: Export workspace.dsl with format mermaid into /tmp/structurizr-spike/out-mermaid and list the files produced (one per view); record the first 40 lines of each

- [x] Task 5: Set the view property mermaid.sequenceDiagram to true on the dynamic view, export again, and compare the collaboration output with the sequence output

- [x] Task 6: Export with format plantuml and with format plantuml/c4plantuml into separate folders under /tmp/structurizr-spike and record which view types were produced

- [x] Task 7: Export with format static into /tmp/structurizr-spike/out-static and note what it needs to be viewed (plain files or a web server)

- [x] Task 8: Try to export format svg and format png with the playwright image tag; record whether it works headless in CI, the image size, and the time taken

- [x] Task 9: Build /tmp/structurizr-spike/mermaid-test.md that embeds each exported Mermaid output in a fenced mermaid block, one heading per view, and tell the user to open it in VS Code with the built-in preview and with the Markdown Preview Enhanced and Mermaid extensions; record what renders and what is broken

- [x] Task 10: Ask the user via the question tool to push mermaid-test.md and an svg-test.md (each exported SVG from Task 8 embedded as a markdown image, one heading per view) to a scratch repository or paste them into an issue or wiki on GitHub, on a GitLab instance and on a Forgejo instance, and report per platform which views render, which fail, and the exact error text; record the Mermaid version each platform uses (a fenced mermaid block containing only the word info shows it)

- [x] Task 11: Test inline viewing through Kroki: run the docker image yuzutech/kroki locally on port 8080 with default settings, POST the DSL with a self-contained workspace to the structurizr diagram type with svg output, and record the result including how the view-key option selects one view; then repeat with a workspace that uses an include directive and confirm it fails in SECURE mode

- [x] Task 12: Test the include directive with the Structurizr CLI: create a model fragment in a subdirectory, include it from workspace.dsl, validate, then move the fragment to a sibling directory and record the error; also test an https include from a raw file on the user's own GitLab or Forgejo instance only if the user agrees

- [x] Task 13: Test extracting a fenced structurizr block from a markdown file into a temporary directory, validating it and exporting it, using only shell tools; record whether a few lines of shell are enough for a CI step

- [x] Task 14: Test whether the Structurizr parser accepts a file that starts with a YAML frontmatter block between triple dash lines, and whether the workspace properties block can carry metadata such as id and status; record the exact errors

- [x] Task 15: Test the structurizr/mcp image: run it on a local port, call the validate and export tools over HTTP or with an MCP client passing the DSL as an inline string, and record whether it works offline and how a client such as OpenCode would be configured

- [x] Task 16: Test how a UC-like diagram can be approximated with custom elements and a custom view, export it to PlantUML and to the static site, and record what the result looks like and what UML notation is missing

- [x] Task 17: Test how a class-like diagram can be approximated with custom elements and a custom view (three classes with attributes and associations), export it to PlantUML and to the static site, and record whether the result is usable as a class diagram or confirms the no-class-diagram finding experimentally

- [x] Task 18: Test determinism: run each export twice and compare the output with diff; record whether the Mermaid and PlantUML output is byte-identical between runs, since CI drift checks need this

- [x] Task 19: Write /tmp/structurizr-spike/REPORT.md with a results table per platform and per view type, the exact commands, known limits, whether the two-layer design (DSL as source, generated Mermaid block committed and drift-checked in CI) works, and a clear recommendation among Mermaid export, Kroki, pre-rendered SVG, or dropping Structurizr; list everything NOT TESTED

- [x] Task 20: Summarise the report to the user and wait for the decision; do not start designing or implementing a str domain in specmgr

## Recent Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-30 19:14:00.000+01:00 - Tasks 9-20 done: spike complete, report written

Manual checks (user): GitHub.com mermaid 12.2.0 rendered mermaid-test.md sections 1-5 (all view types incl. the sequence variant) and displayed all 4 pre-rendered SVGs; VS Code mermaid 11.17.0 rendered sections 1-4 (section 5 not reported; preview variant not specified). The documented securityLevel-loose caveat did not prevent rendering on either platform. REPORT.md written at /tmp/structurizr-spike/REPORT.md: platform x view-type table, export-format table, 10 key findings (v2 DSL breaking change, weak validate gate, workspace-properties metadata, permissive CLI includes, Kroki POST-only + ~1170 B limit + first-view-only, mcp image validate/parse/inspect only with no export tools and offline operation, UC/class approximation limits, docker root-owned bind-mount gotcha, shipped cloud themes, svg/png timestamp non-determinism), two-layer design verdict (works with explicit view keys + validate + inspect gate + diff drift check), recommendation (adopt Structurizr with Mermaid export for C4 views, keep PlantUML for UML use case/class diagrams; Kroki and pre-rendered SVG rejected as primary), and the NOT TESTED list (GitLab/Forgejo, https includes, VS Code section 5, browser static-site check, real-CI playwright run, OpenCode mcp client, dark/animation, -url export variant). Waiting on the user's decision - no str domain design or implementation started.

### 2026-10-30 16:00:40.000+01:00 - Tasks 1-8 executed: v2 DSL, all export formats verified

Executed Tasks 1-8 on the consolidated `structurizr/structurizr:2026.10.26-noble` image (v2026.10.26). Critical discovery: the image ships the NEW v2 DSL grammar, so the original classic-DSL workspace failed validation ("View keys can only contain a-zA-Z0-9_-"); rewrote workspace.dsl per docs.structurizr.com/dsl/language (deploymentEnvironment moved into model, views take [key] [description], dynamic steps are ordered plain lines, deployment view needs explicit include *). All export formats produced and content-verified: mermaid (one .mmd per view; labels are HTML `<div>` fragments - needs securityLevel loose at render time), mermaid sequence variant (mermaid.sequenceDiagram true -> sequenceDiagram, only `<br />`), plantuml (self-contained .puml + separate -key legend .puml) and plantuml/c4plantuml (single .puml using !include <C4/C4>), static (25-file self-contained JointJS site, client-side rendering), and svg+png via the 6.31 GB :playwright tag (headless works, ~3.5 s, but the SVG embeds a timestamp so output is NOT byte-stable between runs - relevant to Task 18). validate is silent on success (exit 0) and prints a single ERROR line with "at line N of path: text" on failure (exit 1); an unterminated string is silently truncated, not caught. Every command and real output is logged in /tmp/structurizr-spike/COMMANDS.md. Next: Task 9 (mermaid-test.md) then the user's manual VS Code / GitHub checks.

### 2026-10-30 15:16:00.000+01:00 - Execution prep: environment check and agreed adjustments

Environment verified (docker 29.1.3, ports 8080/8081 already in use, 8090 free, ~1.3 TB free disk, curl/jq/gh present). Agreed adjustments before execution starts: (1) Task 1 -- the Docker Hub registry has no bare `noble` tag for structurizr/structurizr; pull `latest` plus the dated `2026.10.26-noble` (the CI pin) and record both versions; Task 8 uses the dated `2026.10.26-playwright` tag. (2) Task 10 -- the manual platform check runs on GitHub.com only; the GitLab and Forgejo rows are NOT TESTED. (3) Task 12 -- the https-include sub-part is skipped by user decision and is NOT TESTED. (4) New setup step before Task 1 -- adjust ~/docker/structurizr/docker-compose.yml per user: replace the EOL `structurizr/lite` service with `structurizr/structurizr:2026.10.26-noble` running `command: local` (keeps the web UI on 9797), keep the `plantuml-server` on 9898 for local render-verification of the PlantUML exports (tasks 6/16/17); the web service and one-shot CLI runs are both used. (5) Kroki (task 11) and structurizr/mcp (task 15) run on port 8090, not 8080. Status set to active.

### 2026-10-30 13:31:12.000+01:00 - Refined after review

Added Task 17 (class-diagram approximation experiment) after the review of this plan; old Tasks 17-19 renumbered to 18-20. Task 10 now also verifies the pre-rendered SVG route on GitHub, GitLab and Forgejo (svg-test.md). Task 1 records the noble tag version as well, Task 3 names the mount source explicitly, Task 8 adds png, Task 12 names the https include source, and Task 15 corrects the structurizr/mcp usage to inline-DSL tool calls. Status set to draft until execution starts.

### 2026-10-30 00:00:00.000Z - Created

Created from a research discussion about replacing or complementing PlantUML. The spike checks by experiment what the documentation only claims about Structurizr export, inline rendering and include handling.
