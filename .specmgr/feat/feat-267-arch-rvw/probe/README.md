# Structurizr Probe

Task 120.110 (issue 267). A committed, repeatable probe of the Structurizr conventions of the Architecture Model TXT 30983f27, section 8. It replaces the probe of QA 0.0500, which lived in `/tmp/opencode/c4-probe/` and is lost.

## Files

| File | Purpose |
|------|---------|
| `workspace.dsl` | Probe workspace: properties on every element kind, the proposed keys `trust.level`, `safety.function`, `failure.domain.placement`, one perspective per criterion (rating on the top node, evidence below), a telemetry relationship tag with a filtered view, view properties `viewpoint`, `!docs` and `!adrs` (madr) with local folders |
| `docs/` | One documentation section for `!docs` |
| `adrs/` | Two MADR decisions (`0001-*.md`, `0002-*.md`, one links the other) and one file named like a specmgr DEC (`{uuid}-{slug}.md`) |
| `overlay/workspace.dsl` | Review overlay: `workspace extends ../workspace.dsl` with `!element` adding a perspective and a property |
| `bad/*.dsl` | Negative cases: property on a group, empty property value, duplicate perspective name, duplicate property key |
| `query.py` | Standard-library query script over the JSON export: provenance, failure domains (derived, no inheritance in JSON), replicas, placement, parent and child conflicts, vocabulary counts, trust boundaries (derived from the instances), safety functions, rating against evidence perspectives, view viewpoint property |
| `out/` | Generated exports. Not committed (`.gitignore`) |

## Reproduce

Requires Docker and the image `structurizr/structurizr:2026.10.26-noble`. No network. Run from this folder. With rootless Docker, do not pass `-u`: the container's root maps to the host user, and `-u` makes the mounted folder read-only for it. Paths must be absolute inside the container (`/w/...`).

```sh
D="docker run --rm --network none -v $PWD:/w structurizr/structurizr:2026.10.26-noble"
$D validate -w /w/workspace.dsl
$D inspect  -w /w/workspace.dsl
for f in bad/*.dsl; do $D validate -w /w/$f; done
mkdir -p out/plantuml out/c4plantuml out/mermaid out/overlay
$D export -w /w/workspace.dsl -f json                 -o /w/out
$D export -w /w/workspace.dsl -f plantuml/structurizr -o /w/out/plantuml
$D export -w /w/workspace.dsl -f plantuml/c4plantuml  -o /w/out/c4plantuml
$D export -w /w/workspace.dsl -f mermaid              -o /w/out/mermaid
$D export -w /w/overlay/workspace.dsl -f json         -o /w/out/overlay
python3 -I query.py out/workspace.json
# PlantUML exports, with a PlantUML server on 127.0.0.1:8080 (repository root as working directory):
SPECMGR_PLANTUML_URL=http://127.0.0.1:8080 uv run --frozen specmgr plantuml-check <export>.puml
```

## Results (2026-11-22, Structurizr 2026.10.26)

Confirmed from QA 0.0500 and 0.0680:

- `validate` OK. `inspect` 0 errors, once every element has a description and a technology, every element is connected, and the decisions are attached to the software system (see below).
- Negative cases: a property on a group, an empty value and a duplicate perspective name are parse errors. A duplicate property key parses, and the last value wins without a warning.
- Properties and perspectives are kept in the JSON export and dropped in the PlantUML (Structurizr and C4-PlantUML) and Mermaid exports. The JSON export is the only carrier; `query.py` is the reader.
- The JSON has no inheritance. `query.py` derives failure domains and trust boundaries from the ancestors and from the container instances.
- The same criterion ID as perspective name on several elements parses (one per element). `query.py` separates the rating (top deployment node or software system) from the evidence.

New:

- Decisions: `!adrs adrs madr` imports the two `NNNN-*.md` files, with status, date and the link between them. The file named like a specmgr DEC is ignored. With the decisions on the workspace, `inspect` still reports "missing decisions" for the software system. With `!adrs` inside the software system, the error is gone. The parser also names a `!decisions` keyword.
- `!docs` loads a local folder, on the workspace and on the software system.
- Views take a `properties` block. A view property `viewpoint` (for example `VP02`) is kept in the JSON export. This answers the open point of Architecture Model 8.4: a view records its viewpoint in a view property.
- Telemetry tag: `include *` with `exclude "relationship.tag!=Telemetry"` gives a view with only the telemetry relationships; the other elements stay in the view. `include "relationship.tag==Telemetry"` alone adds no elements and gives an empty view.
- Overlay: `workspace extends` with `!element` adds perspectives and properties to an element of the base workspace. A review can be a separate workspace on top of the architecture model.
- The proposed keys `trust.level`, `safety.function`, `failure.domain.placement` parse on containers, components, relationships and deployment nodes. They are plain properties; Structurizr checks nothing.
- DSL trap: a positional number after the technology of a deployment node is not the instance count. `deploymentNode "Web pod" "..." "Pod" 3` makes "3" a tag. Use `instances 3` in the block, or the fifth position after the tags.
- The specmgr PlantUML structure check warns "unclosed 'rectangle' fragment" on every plain `rectangle "..." <<...>> as X` line of the Structurizr PlantUML export, while the PlantUML server renders all files (`valid=true rendered=true`). The C4-PlantUML export has no warning. The warning is a false positive of `plantuml/structure.py` (already suspected in QA 0.0500).

Not tested: properties on deployment groups, the Structurizr MCP server against file-based features (it takes DSL text only and cannot read `!docs`, `!adrs` or `workspace extends`).
