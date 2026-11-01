---
classification: null
created: '2026-10-19T07:35:55.948+02:00'
id: 81d73e92-ed9c-44a8-a475-9256a88cfd6a
status: draft
type: sop
updated: '2026-10-19T07:35:55.948+02:00'
version: 1.0.0
---

# Convert an ADR to a DEC

## Purpose

Convert one ADR document (in `docs/adr/`) into one DEC document (in `docs/dec/`) that fully parses under the `dec` schema, reusing the ADR's UUID as the DEC's id. This keeps existing cross-references to the decision valid by UUID after the ADR artifact type is removed (GitHub issue #46), without any schema change to any domain.

## Scope

This SOP covers converting one ADR into one DEC: the frontmatter mapping, the body transformation (verbatim pass-through, one heading rename, insertion of the sections the DEC schema mandates, one migration `## Updates` entry), the host-native file write, and the verification gates.

Out of scope: modifying or deleting the source ADR file (ADRs stay untouched until the later removal phase of issue #46); retagging `ADR <uuid>` references to `DEC <uuid>` in other documents, code, or the generated ADR table of contents; orchestrating the rollout over the whole ADR set; any schema change to `dec` or any other domain.

## Definitions

- **ADR**: a document in `docs/adr/` carrying a UUID `id` in its frontmatter, parsed by `models/adr/v1` (MADR 4.0.0 based).
- **DEC**: a document in `docs/dec/` carrying a UUID `id` and `type: dec` in its frontmatter, parsed by `dec/models/v1`.
- **UUID reuse**: the DEC's frontmatter `id` equals the ADR's frontmatter `id`, and the DEC's filename reuses the ADR's filename stem (`<uuid>-<slug>.md`).
- **Supersession back-reference**: the DEC-side record of an ADR's `status: superseded by <uuid>`: the DEC gets `status: superseded` plus a bullet `- DEC <uuid>: <title>` under `## Related Artifacts` → `### Decisions`.
- **Verbatim**: byte-identical to the ADR source, including surrounding blank lines, except where this SOP explicitly renames, inserts, or appends.

## Roles and Responsibilities

### Accountable

dfch

### Responsible

- the agent executing this SOP (OpenCode)
- the human reviewer confirming deviations from the mapping rules

## Safety and Precautions

- Never modify or delete anything under `docs/adr/`. The ADR file is the sole source for this conversion until the later removal phase of issue #46.
- No schema change: if a mapping rule below is insufficient for the ADR at hand, stop and record the gap -- do not improvise silently and do not extend the `dec` schema to fit one document.
- A DEC file is written only after Gate 1 (Step 4) returns `valid: true`; nothing is written on a failed gate.
- The `dec` parser enforces strict section order (the `Decision` model's field declaration order); never reorder sections.
- Every deviation from the mapping rules (an applied default, a judgment call) must be recorded in this SOP's own `## Updates` (newest first) before the next document is converted.

## Procedure

### Step 1: Read the ADR

Call `get_adr(<uuid>)` for the structured frontmatter and body, and read the raw file `docs/adr/<uuid>-<slug>.md` -- all verbatim pass-through in Step 3 uses the raw file's bytes, not a re-rendering. Note which frontmatter keys are present (`status`, `date`, `decision-makers`, `consulted`, `informed`) and which body sections are present (`## Decision Drivers`, `## Considered Options`, `## Pros and Cons of the Options`, `### Consequences`, `### Confirmation`, `## More Information`).

### Step 2: Build the DEC frontmatter

Generate the YAML frontmatter block with exactly these keys:

| ADR key | DEC key | Rule |
| --- | --- | --- |
| `id` | `id` | copy verbatim (UUID reuse) |
| -- | `type` | the literal `dec` |
| `status` | `status` | the same value for `draft`/`proposed`/`accepted`/`rejected`/`superseded`/`deprecated`; if the ADR status is `superseded by <uuid>`, write `status: superseded` and remember `<uuid>` for the Step 3 back-reference |
| `date` | `created`, `updated` | append `T00:00:00.000Z` to the ADR `date` value (`YYYY-MM-DD` becomes `YYYY-MM-DDT00:00:00.000Z`); if the ADR has no `date`, use the current full ISO 8601 timestamp (`yyyy-MM-ddTHH:mm:ss.SSSZ`) for both |
| -- | `version` | `1.0.0` |

The ADR keys `decision-makers`, `consulted`, and `informed` are NOT carried into the frontmatter; they map to body sections in Step 3. The DEC `classification` key is omitted.

### Step 3: Transform the body

1. Pass through verbatim, in this order, only those that exist: `# {title}`; `## Context and Problem Statement`; `## Decision Drivers`; `## Considered Options`; `## Decision Outcome` including its lead prose before the first H3; `### Consequences`; `### Confirmation`.
2. Insert `## Roles and Responsibilities` at the boundary immediately after the `## Decision Outcome` section (after its `### Consequences`/`### Confirmation` if present, else after its lead prose; before the next `## ` heading, or at end of file if there is none):
   - `### Accountable` -- a single paragraph (never bullets): the ADR `decision-makers` value. If the value contains ` + `, use only the element after the last ` + ` (the final-decision owner). If the ADR has no `decision-makers`, use `dfch` and record a deviation.
   - `### Responsible` -- a bullet list with at least one item: one bullet per element of the ADR `decision-makers` value split on ` + `. If absent, a single bullet `- dfch` and record a deviation.
   - `### Consulted` / `### Informed` -- include only if the ADR frontmatter carried `consulted`/`informed`; one bullet per name.
3. Insert `## Source` at the same boundary, after `## Roles and Responsibilities` -- a single line: if the ADR body explicitly names a GitHub issue (e.g. `GitHub issue #NN` in `## Context and Problem Statement`), write `GitHub issue #NN`; otherwise write `dfch` and record a deviation.
4. If the ADR status was `superseded by <uuid2>` (Step 2), insert `## Related Artifacts` at the same boundary, after `## Source`, with a `### Decisions` sub-section carrying exactly one bullet: `- DEC <uuid2>: <title>`, where `<title>` is the H1 of the ADR with id `<uuid2>` (the superseding decision; the back-reference resolves once that ADR is itself converted -- the prerequisite of Gate 4).
5. Rename a `## Pros and Cons of the Options` heading to `## Pros and Cons`; the `### Option N: {title}` entries below it stay unchanged.
6. Pass through `## More Information` verbatim, if present.
7. Append `## Updates` as the last section of the document, with exactly one entry -- the heading `### {current full ISO 8601 timestamp} - Converted from ADR` followed by the lead paragraph: `Converted from ADR {uuid} per the "Convert an ADR to a DEC" SOP (GitHub issue #46).`

The resulting section order is exactly the one the `dec` parser enforces: `# {title}` → `## Context and Problem Statement` → `## Decision Drivers` → `## Considered Options` → `## Decision Outcome` → `## Roles and Responsibilities` → `## Source` → `## Related Artifacts` → `## Pros and Cons` → `## More Information` → `## Updates`, with absent sections simply omitted (insertions 2--4 always sit, in that order, at the one boundary between `## Decision Outcome` and the next surviving `## ` section).

### Step 4: Gate 1 -- dry-run validation

Assemble the full candidate document text (Step 2 frontmatter block plus Step 3 body). Call the generic `validate` tool with `type="dec"`, `full=True`, and the full text as `content`. It must return `valid: true`. If it returns `valid: false`, read `errors[].message`, fix the candidate text, and re-run this gate; never write a file that fails it.

### Step 5: Write the DEC file host-native

Write the candidate text to `docs/dec/<uuid>-<slug>.md`, where `<slug>` is the ADR filename stem after the UUID (reused verbatim). Create `docs/dec/` if it does not exist. This is a host file write: no specmgr tool can create a DEC with a caller-chosen id (`create_dec` always assigns a fresh UUID, and no `set_dec_id` tool exists), which is why UUID reuse requires the host-native write.

### Step 6: Gate 2 -- read-back

Call `get_dec(<uuid>)`. It must return a parsed document (not a parse-failure result) with the H1 title equal to the ADR title, the frontmatter `id` equal to `<uuid>`, and the frontmatter `status` per the Step 2 rule.

### Step 7: Gate 3 -- list check

Call `list_dec` (optionally filtered with a glob on the UUID). The row for `<uuid>` must be healthy: real title and status, no `<failed to parse>` marker, and the listing's `error_count` is `0`.

### Step 8: Gate 4 -- supersession back-reference (superseded documents only)

If the ADR status was `superseded by <uuid2>`: call `list_references(type="dec", id="<uuid>")`. The row for `type=dec`, `id=<uuid2>` must resolve with non-null `title` and `path`. If the superseding DEC does not exist yet, record that fact and re-run this gate once it has been converted.

### Step 9: Record deviations

If any Step 2/Step 3 rule required an applied default (missing `decision-makers`, derived `Source`, ...) or a judgment call, prepend a newest-first entry to this SOP's own `## Updates` recording the converted ADR UUID, the rule applied, and the value used.

## More Information

The DEC body schema is a superset of the ADR body: every ADR body section has a DEC counterpart, and the only rename is `## Pros and Cons of the Options` → `## Pros and Cons` (the `dec` parser rejects the ADR heading). The ADR frontmatter keys without a DEC frontmatter counterpart (`date`, `decision-makers`, `consulted`, `informed`) all map: `date` → `created`/`updated`, the people keys → `## Roles and Responsibilities`. The two DEC-mandatory sections without an ADR counterpart (`## Roles and Responsibilities`, `## Source`) are filled by the Step 3 derivation rules and flagged as deviations. A corpus survey (43 ADRs, 2026-10-19) found: `date` in 22, `decision-makers` in 38, `consulted`/`informed` in 0, `## Pros and Cons of the Options` in 25, `status: superseded by <uuid>` in 1 (`a156fdf9-052c-4f43-93a2-eeec04a91eac`, superseded by `92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c`), and a `## Decision Outcome` lead prose in all 43 (so the DEC-mandatory `statement` is always satisfiable without content edits).

## Updates

### 2026-10-19T05:34:18.000Z - Created

SOP drafted for GitHub issue #46 ("Remove adr artifact type"), after the ADR → DEC field gap analysis concluded that no `dec` schema change is required: supersession is recorded as a back-reference (DEC `status: superseded` plus a `### Decisions` bullet), UUID reuse keeps every existing reference valid, and the host-native write in Step 5 is necessary because `create_dec` assigns a fresh UUID. Pilots and the rollout over the remaining ADR set are out of scope for this creation.
