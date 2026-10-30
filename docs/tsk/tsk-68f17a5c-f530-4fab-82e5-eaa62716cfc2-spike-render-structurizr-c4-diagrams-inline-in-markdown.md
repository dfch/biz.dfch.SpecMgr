---
classification: null
created: '2026-10-30T10:21:03.414+01:00'
id: 68f17a5c-f530-4fab-82e5-eaa62716cfc2
status: draft
type: tsk
updated: '2026-10-30T13:33:21.775+01:00'
version: 1.0.0
---

# Spike: Render Structurizr C4 Diagrams Inline in Markdown

<!-- CONTEXT FOR A FRESH AGENT. Repo: biz.dfch.SpecMgr (specmgr MCP server, see AGENTS.md). Specmgr uses PlantUML today for UC and reference-graph diagrams. Drawbacks: no Python parser, validation needs a jar/container, no inline rendering in markdown, extra puml/svg files. The user wants diagrams for system and software architecture (component, class, UC, sequence, deployment), rendered inline in markdown in VS Code, GitHub, GitLab and Forgejo (no dependency on one git platform), and built in a CI pipeline. Java and Docker are allowed. The user prefers a single source of truth and is considering a new specmgr artifact type (working name str) that holds Structurizr DSL (C4 model as code) in a fenced block and is referenced from other specmgr documents.

FINDINGS SO FAR (from docs, NOT verified by experiment). Structurizr (structurizr/structurizr, Apache-2.0, Docker image structurizr/structurizr, tags latest, noble for CI, playwright for PNG/SVG export; Java 21 war also exists) has commands validate, inspect, export, local, playground; only the server command needs a paid licence and must NOT be used. Export formats: mermaid, plantuml, plantuml/c4plantuml, static, png, svg, json. The Structurizr Mermaid export page says Mermaid needs securityLevel loose to render correctly; GitHub, GitLab and Forgejo control that setting, so rendering there is UNVERIFIED. Dynamic views export to a sequence diagram with the view property mermaid.sequenceDiagram true (or plantuml.sequenceDiagram true); default is a collaboration diagram. Structurizr has no class diagram and no real UML use case diagram (custom elements and custom view only, and Mermaid export does not list custom views). The structurizr/mcp image (Docker, stateless HTTP) offers tools to validate DSL, parse DSL to JSON, and export a view to Mermaid, PlantUML or C4-PlantUML; each takes DSL as an inline string. Kroki (yuzutech/kroki) renders a structurizr diagram type but its default SECURE mode disables !include, !docs and !adrs for Structurizr. Local !include paths must be in the parent file directory or a subdirectory. The DSL has comment syntax (double slash, hash, block comments) and no documented YAML frontmatter support.

RULES FOR THIS SPIKE. Read-only toward the repository. Write all artifacts ONLY under /tmp/structurizr-spike. Do not commit, do not edit any repo file. Do not use the Structurizr server command. Do not send diagram content to public services (kroki.io, mermaid.ink, mcp.structurizr.com). Record every command you ran and its real output. Mark anything you could not test as NOT TESTED, never guess. Ask the user via the question tool for the manual checks on GitHub, GitLab and Forgejo. Finish with a report as a markdown file at /tmp/structurizr-spike/REPORT.md and a short summary to the user. Use specmgr tools (list_tsk, get_tsk, update) only to tick items and add Recent Updates entries in THIS task list. -->

- [ ] Task 1: Pull the docker image structurizr/structurizr (tags latest and noble) and confirm the version of each with the docker run command and no arguments or the help output; record both versions

- [ ] Task 2: Create /tmp/structurizr-spike/workspace.dsl with one person, two software systems, one system with a web container and a database container, relationships, a systemContext view, a container view, a deployment environment Live with nested deployment nodes and container instances plus a deployment view, and a dynamic view named Checkout with three numbered steps

- [ ] Task 3: Run the validate command on workspace.dsl via docker with /tmp/structurizr-spike mounted at /usr/local/structurizr and record the output; then introduce one deliberate syntax error and record the error message format and exit code

- [ ] Task 4: Export workspace.dsl with format mermaid into /tmp/structurizr-spike/out-mermaid and list the files produced (one per view); record the first 40 lines of each

- [ ] Task 5: Set the view property mermaid.sequenceDiagram to true on the dynamic view, export again, and compare the collaboration output with the sequence output

- [ ] Task 6: Export with format plantuml and with format plantuml/c4plantuml into separate folders under /tmp/structurizr-spike and record which view types were produced

- [ ] Task 7: Export with format static into /tmp/structurizr-spike/out-static and note what it needs to be viewed (plain files or a web server)

- [ ] Task 8: Try to export format svg and format png with the playwright image tag; record whether it works headless in CI, the image size, and the time taken

- [ ] Task 9: Build /tmp/structurizr-spike/mermaid-test.md that embeds each exported Mermaid output in a fenced mermaid block, one heading per view, and tell the user to open it in VS Code with the built-in preview and with the Markdown Preview Enhanced and Mermaid extensions; record what renders and what is broken

- [ ] Task 10: Ask the user via the question tool to push mermaid-test.md and an svg-test.md (each exported SVG from Task 8 embedded as a markdown image, one heading per view) to a scratch repository or paste them into an issue or wiki on GitHub, on a GitLab instance and on a Forgejo instance, and report per platform which views render, which fail, and the exact error text; record the Mermaid version each platform uses (a fenced mermaid block containing only the word info shows it)

- [ ] Task 11: Test inline viewing through Kroki: run the docker image yuzutech/kroki locally on port 8080 with default settings, POST the DSL with a self-contained workspace to the structurizr diagram type with svg output, and record the result including how the view-key option selects one view; then repeat with a workspace that uses an include directive and confirm it fails in SECURE mode

- [ ] Task 12: Test the include directive with the Structurizr CLI: create a model fragment in a subdirectory, include it from workspace.dsl, validate, then move the fragment to a sibling directory and record the error; also test an https include from a raw file on the user's own GitLab or Forgejo instance only if the user agrees

- [ ] Task 13: Test extracting a fenced structurizr block from a markdown file into a temporary directory, validating it and exporting it, using only shell tools; record whether a few lines of shell are enough for a CI step

- [ ] Task 14: Test whether the Structurizr parser accepts a file that starts with a YAML frontmatter block between triple dash lines, and whether the workspace properties block can carry metadata such as id and status; record the exact errors

- [ ] Task 15: Test the structurizr/mcp image: run it on a local port, call the validate and export tools over HTTP or with an MCP client passing the DSL as an inline string, and record whether it works offline and how a client such as OpenCode would be configured

- [ ] Task 16: Test how a UC-like diagram can be approximated with custom elements and a custom view, export it to PlantUML and to the static site, and record what the result looks like and what UML notation is missing

- [ ] Task 17: Test how a class-like diagram can be approximated with custom elements and a custom view (three classes with attributes and associations), export it to PlantUML and to the static site, and record whether the result is usable as a class diagram or confirms the no-class-diagram finding experimentally

- [ ] Task 18: Test determinism: run each export twice and compare the output with diff; record whether the Mermaid and PlantUML output is byte-identical between runs, since CI drift checks need this

- [ ] Task 19: Write /tmp/structurizr-spike/REPORT.md with a results table per platform and per view type, the exact commands, known limits, whether the two-layer design (DSL as source, generated Mermaid block committed and drift-checked in CI) works, and a clear recommendation among Mermaid export, Kroki, pre-rendered SVG, or dropping Structurizr; list everything NOT TESTED

- [ ] Task 20: Summarise the report to the user and wait for the decision; do not start designing or implementing a str domain in specmgr

## Recent Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-30 13:31:12.000+01:00 - Refined after review

Added Task 17 (class-diagram approximation experiment) after the review of this plan; old Tasks 17-19 renumbered to 18-20. Task 10 now also verifies the pre-rendered SVG route on GitHub, GitLab and Forgejo (svg-test.md). Task 1 records the noble tag version as well, Task 3 names the mount source explicitly, Task 8 adds png, Task 12 names the https include source, and Task 15 corrects the structurizr/mcp usage to inline-DSL tool calls. Status set to draft until execution starts.

### 2026-10-30 00:00:00.000Z - Created

Created from a research discussion about replacing or complementing PlantUML. The spike checks by experiment what the documentation only claims about Structurizr export, inline rendering and include handling.
