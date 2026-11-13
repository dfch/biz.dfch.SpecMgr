---
classification: null
created: '2026-11-01T11:05:16.812+01:00'
id: 4a09922d-bc32-4c03-86ba-d30ebc34e0b8
status: draft
type: txt
updated: '2026-11-01T11:05:16.812+01:00'
version: 1.0.0
---

# Structurizr and C4 for specmgr: Spike Findings and Design Suggestions

Write-up of a planning and tooling spike (2026-11-01) on using Structurizr DSL and C4 to model (A) specmgr itself and (B) other projects that use specmgr. It covers what the spike tested, what it found, and what it suggests for the design. It is a discussion record, not a decision: nothing here is frozen, and no repository code was changed. The spike files were scratch files under `/tmp/opencode/c4-spike/` and are not part of the repository, so every result below is reproducible only by rerunning the steps.

Related existing artifact (the PlantUML support package whose validation chain this spike exercised):

DEC 7a626b12-b189-4561-a51d-ffb2e9e193b4: Add an in-package, import-free plantuml package with a strict first-set-wins validation-source chain

## Scope and decisions taken in the discussion

- Goal: BOTH (A) model specmgr itself and (B) support other system and software projects.
- Each repository that uses specmgr holds its own source of truth for its architecture.
- Rendering route preferred: DSL, then PlantUML, then SVG. The PlantUML look is sufficient, no custom Structurizr look is needed.
- Structurizr Lite is end of life and is not used.
- The Structurizr `!adrs` importer is out of scope (see Finding 9).
- Generation of DSL from specmgr artifacts should be automated and deterministic, preferably by a tool alone without an agent.

## Tool versions used

- Structurizr MCP: `structurizr/mcp:2026.04.20`.
- Structurizr CLI container: `structurizr/structurizr:2026.10.26-noble`, plus the `-playwright` image of the same release for browser SVG export.
- PlantUML targets: host jar 1.2026.8 (no Graphviz installed), `plantuml-cli` container 1.2026.8 with Graphviz 14.0.1, jetty server on port 8080 (1.2026.8), tomcat server on port 9898 (1.2026.9), public plantuml.com (1.2026.9beta4).
- The MCP and the CLI are about six months apart in release date. They produced identical results on this model.

## Finding 1: The reference graph itself is not a C4 model

C4 describes software structure: person, software system, container, component, code. The existing reference graph relates documents (REQ, DEC, UC, VCR and others) with untyped edges. Drawing documents as C4 `System` or `Component` boxes would produce a misleading diagram.

Structurizr as a tool is not limited to C4 notation: custom elements and the `custom` view exist for non-C4 content. A reference graph of documents can be modelled that way (tested: valid and readable), but it adds a layer without adding a diagram, and it loses features the existing renderer has: byte-stable output by explicit spec, cycle detection with red arrows, unresolved-reference nodes. Suggestion: keep the existing deterministic reference graph as it is.

C4 fits in two other places:

- Modelling specmgr itself: level 1 (context) and level 2 (container) are useful, level 3 (component) is useful for the MCP server only, level 4 (code) is skipped because `docs/api/` already covers it.
- Allocation: linking documents to architecture elements (which container implements REQ X, which component a decision applies to). That cross-link is the new capability neither the reference graph nor C4 provides alone.

## Finding 2: Validity of generated PlantUML

All exports of the spike model were valid on all five PlantUML targets: 3 C4-PlantUML views (15 of 15 combinations) and 3 Structurizr-flavour views plus their legend files (30 of 30). Validity was judged on the rendered SVG, because PlantUML servers answer HTTP 200 for some failures. Four deliberately broken files failed on all five targets (servers answered HTTP 400 with an `X-PlantUML-Diagram-Error` header).

Specmgr's own chain behaves as designed but has a consequence for architecture files:

- With no `SPECMGR_PLANTUML_*` source configured, the chain returned `valid=None` for all four broken files. Structure-only mode catches none of them, including an unclosed macro.
- With the jar or a server URL configured, verdicts were correct.
- Rule for architecture artifacts: `checked_by=structure` must count as not validated, never as a pass. The structure checker lints only the subset specmgr's own renderers emit. On a foreign Structurizr-style export it warned in preflight mode and failed with 4 errors in standalone mode, so it is the wrong gate for Structurizr output.

Suggested pipeline: `structurizr validate`, then a policy lint, then export, then the real PlantUML parser, then SVG, then a drift check of committed outputs.

## Finding 3: Structurizr MCP versus CLI

- The MCP offers six stateless tools over DSL text: validate, inspect, parse and three exporters (PlantUML, C4-PlantUML, Mermaid). Tools run in the spike: validate, inspect, export-plantuml, export-c4plantuml.
- Results for validate, inspect and the C1, C2 and C3 C4-PlantUML exports were identical to the CLI container, apart from a trailing newline.
- The MCP is sandboxed: `!include` and `!docs` are refused ("feature … is not enabled"). It can only check single-file models.
- The CLI container handles `!include` and split models, validated and exported in the spike. The Java `.war` is a second official binary, untested here (the host has Java 11, the `.war` needs Java 21).
- `inspect` reports policy findings (missing description, missing technology, no scope, no documentation, no decisions). Setting `configuration { scope softwaresystem }` and adding `!docs` cleared the first three kinds; "missing decisions" remained.
- Exports are deterministic (two runs byte-identical), so a drift check is feasible if versions are pinned.

## Finding 4: C4-PlantUML versus Structurizr flavour

| Aspect | `plantuml/c4plantuml` | `plantuml/structurizr` |
|---|---|---|
| Architecture elements | complete | complete |
| Custom elements (REQ, DEC, GOL) | silently dropped, no warning | drawn |
| Source size (C2 view) | 54 lines, 3.6 KB | 142 lines, 8.0 KB |
| Source readability | short, C4 macros | a style block of about 20 classes with base64 names |
| Legend | inline | separate `-key.puml` file |

The C4 export also drops elements pulled in by `include *`: in the C3 view two DEC elements were included by the wildcard and silently omitted. A parser check cannot catch this. A completeness check can: map the rendered SVG links back to element names and compare with the model relationships. This check passed for all three C4 views (6 of 6, 10 of 10, 15 of 15 edges).

By default the C4 export drops tags and styles (`$tags=""`). The view properties `c4plantuml.tags "true"` and `c4plantuml.elementProperties "true"` restore tags, colours and element properties. Trap: with tags on, the default `Element` tag needs an explicit background colour, otherwise the output is valid but unreadable (white text on white).

Preference stated in the discussion: less noise. Suggestion: C4-PlantUML for architecture views, with artifacts kept out of those views (explicit include lists instead of `include *`, untested), and the Structurizr flavour or the static site where artifacts must be shown.

## Finding 5: Traceability between DSL and specmgr artifacts

- Specmgr's reference pattern matches `REQ <uuid>` style tags anywhere in text. It matched them in DSL comments, property values and perspective text. A bare uuid does not match. `list_references` does not scan `.dsl` files today.
- Structurizr has no dedicated annotation element. Three structured fields work and survive JSON export: `properties`, `perspectives`, `url`. Only `properties` (with `c4plantuml.elementProperties`) and `url` show in a C4-PlantUML diagram.
- Comments are plain text and cannot be tied to an element by the regex alone. Structured properties are more reliable, but reading them needs the Structurizr JSON export.

## Finding 6: Allocation spike with real documents

A generator read 3 REQs and 2 ADRs from `docs/` (plus 5 referenced documents) and emitted DSL elements deterministically. Mapping: box title is the document title, the metadata line (where `[…]` appears) is `REQ <uuid>`, the description is the first paragraph truncated, the perspective "Text" holds the full body, the element `url` points to the original markdown under `docs/<type>/`. Reference edges came from the existing reference scan. Allocation edges were hand-written. The generator output was byte-identical across two runs.

Constraints found:

- A `custom` view cannot contain containers or components. Artifacts must be added with an extra `include` to a container or component view.
- The DSL rejects relative `url` values. Workaround: a placeholder host, then a post-step rewriting the URL in the exported `workspace.js`, which is base64-encoded JSON.
- A triple-quoted text block needs the opening quotes alone on their line.
- Every relationship needs a technology or `inspect` complains.
- Not verified: behaviour in a browser when the link opens a `.md` file.

## Finding 7: Static HTML and SVG export

- `export -format static` produced a clickable site (the user confirmed all diagrams rendered as clickable diagrams). Diagrams are drawn by JavaScript. Documentation and ADRs are removed from the static export. One site covers one workspace.
- `export -format svg` works in the `-playwright` image (about 2 seconds, byte-identical across two runs). It needs headless Chromium and is not in the plain image.
- No Structurizr command produces a page that joins diagrams, images and documentation in one step.

## Finding 8: Scale

- 20, 60 and 150 generated components: all valid on local targets. plantuml.com answered HTTP 509 (Cloudflare, empty body, reproducible) for the 150-component view. Cause not investigated.
- The 150-component SVG was 29,664 pixels wide, unusable as a diagram. Practical bound: about 20 elements per view.

## Finding 9: Structurizr decision-record import is unsuitable for the repository's decision records

- A uuid-prefixed file name imports zero decisions without any error. A numeric prefix such as `0001-` is needed.
- A quoted `date: '2026-09-04'` key makes the importer throw, and one bad file aborts the whole export. 25 of 46 ADRs have a `date:` key and failed individually; 21 passed.
- Decision: `!adrs` is skipped. Use specmgr references instead.

## Suggestions

1. Keep the existing deterministic reference graph. Do not model documents as C4 elements for dependency diagrams.
2. Architecture route: DSL, C4-PlantUML export with the tags and properties switches on, real PlantUML parser, SVG. Pin the Structurizr and PlantUML versions.
3. Convention rules the data supports: require a real parser source (`checked_by` not `structure`); give the default `Element` tag explicit colours; keep views to about 20 elements; run a completeness check of each rendered view against the model, because the C4 export drops elements silently.
4. Carry specmgr ids in the DSL as `properties` entries in the `REQ <uuid>` form so they are visible and machine-checkable, and let a specmgr tool check them for dangling ids.
5. Automate artifact elements as a pure function from documents to DSL (sorted, no timestamps) in a specmgr CLI step, not an agent. The agent's remaining judgment: which artifacts to include and the allocation edges. Have the tool refuse C4-PlantUML export for views that contain artifacts.
6. Convention home: a specmgr resource (generic C4 and Structurizr usage rules, applies to every repo), per-repo deviations recorded in that repo's own decision documents, an optional MCP prompt, and at most a thin OpenCode skill pointing at them. Not under `docs/`.
7. File layout options still open: DSL, PUML and SVG as same-name siblings, or a separate image directory. Structurizr exports one file per view, so siblings would be per view. Non-markdown files are already ignored by specmgr listing. Metadata without frontmatter is also open: a header comment, workspace properties, or a companion markdown artifact (lowest risk, because list, status, references and lint then work unchanged).
8. Provisioning of the PlantUML jar and the Structurizr CLI: do not bundle the roughly 30 MB jar in the wheel. An opt-in, hash-verified fetcher or documentation is the lighter choice. PyPI has no official PlantUML jar.

## Not tested

- Large-model layout quality beyond the sizes above, and the public server's limits.
- Dynamic and deployment views.
- Opening the linked `.md` in a browser from the static site.
- The Java `.war` binary and the Mermaid export.
- Version skew: three PlantUML builds agreed on one model, which is not a guarantee.
- View filtering to keep C4 views free of artifacts.

## Open questions

- Is an `arc` document a workspace (one model, many views) or a single view?
- Which metadata option (header comment, workspace properties, companion markdown)?
- Should specmgr ship a checking CLI, or only document the pipeline?
- Which flavour is the default for views that contain artifacts?

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-01 08:40:00.000Z - Created

Initial write-up of the Structurizr and C4 spike findings and suggestions.
