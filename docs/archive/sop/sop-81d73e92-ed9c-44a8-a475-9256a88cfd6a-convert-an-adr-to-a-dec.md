---
classification: null
created: '2026-10-19T07:35:55.948+02:00'
id: 81d73e92-ed9c-44a8-a475-9256a88cfd6a
status: draft
type: sop
updated: '2026-11-01T07:28:30.000+01:00'
version: 1.0.0
---

# Convert an ADR to a DEC

## Purpose

Convert ADR documents (in `docs/adr/`) into DEC documents (in `docs/dec/`) that fully parse under the `dec` schema, reusing each ADR's UUID as the DEC's id and its file name stem as the DEC's file name stem. This keeps existing cross-references to a decision valid by UUID after the ADR artifact type is removed (GitHub issue #46). The conversion is mechanical and script-assisted: the throw-away scripts in the feat-46 folder's `bin/` directory implement the rules below, and this SOP is the authority they implement.

## Scope

This SOP covers converting ADRs into DECs: the survey and the frozen manifest, the frontmatter mapping, the body transformation (verbatim pass-through plus a small, fixed set of mechanical changes), the host-native file write, and the verification gates. It covers the whole set of ADRs; every step also works for a single ADR.

Out of scope: modifying or deleting any ADR file (ADRs stay untouched until the later removal phase of issue #46); retagging `ADR <uuid>` references to `DEC <uuid>` in other documents, code, or the generated ADR table of contents (a separate step with its own scripts, run only after every ADR is converted and verified); removing the `adr` artifact type itself; any change to the `dec` schema other than the multi-block Decision Outcome relaxation of GitHub issue #247, which is a prerequisite and not part of this SOP.

## Definitions

- **ADR**: a document in `docs/adr/` carrying a UUID `id` in its frontmatter, parsed by `models/adr/v1` (MADR 4.0.0 based).
- **DEC**: a document in `docs/dec/` carrying a UUID `id` and `type: dec` in its frontmatter, parsed by `dec/models/v1`.
- **UUID reuse**: the DEC's frontmatter `id` equals the ADR's frontmatter `id`, and the DEC's file name equals the ADR's file name (`<uuid>-<slug>.md`, without the `dec-` prefix `create_dec` would add).
- **Manifest**: `adr-manifest.json` in the feat-46 folder, written once by the survey script. It freezes, per ADR, the git-derived `created`/`updated`, the derived `Source` and RASCI values, the supersession links, and the bare-token runs to wrap. Conversion and verification read the manifest, never git directly.
- **Supersession**: an ADR with `status: superseded by <uuid2>` becomes a DEC with `status: superseded` and no outbound reference. The superseding DEC (`<uuid2>`) records the link: a bullet `- DEC <uuid>: <title>` under `## Related Artifacts` → `### Decisions`.
- **Verbatim**: byte-identical to the ADR source apart from the mechanical changes listed in Step 4; the verification gate checks this by undoing exactly those changes.
- **Blocked by #247**: an ADR whose `## Decision Outcome` has more than one block before its first `###` sub-section; the `dec` parser rejects it until GitHub issue #247 is released.

## Roles and Responsibilities

### Accountable

dfch

### Responsible

- the agent executing this SOP (OpenCode)
- the human reviewer confirming the conversions the scripts flag for judgment

## Safety and Precautions

- Never modify or delete anything under `docs/adr/`. The ADR files are the sole source for the conversion and for the manifest dates.
- Capture the manifest (Step 2) before any commit touches `docs/adr/`: the DEC `created`/`updated` come from the ADR file's git history, which later retag or archive commits would overwrite. Never refresh the frozen dates (`--refresh-dates`) after the first capture.
- A DEC file is written only when its candidate text parses; nothing is written for a failing candidate and an existing DEC is never overwritten.
- DEC `created`/`updated` must equal the manifest values and must not move: never use the MCP `update`, `edit`, `set_status`, or `set_classification` tools on a converted DEC before the migration is finished (they bump `updated`). Any later change to a converted DEC is host-native and leaves the frontmatter untouched.
- Do not improvise: when a script exits 2 (a conversion needing judgment), stop, record the case in the feat-46 plan's Decisions Made, extend the script rule, and re-run. Do not hand-edit a candidate silently.
- The `dec` parser enforces strict section order; never reorder sections.
- Freeze: from the start of the rollout no new ADR may be created; new decisions are DEC documents.

## Procedure

### Step 1: Check the prerequisites

The ADR set and the DEC schema must be in the expected state: GitHub issue #247 (multi-block Decision Outcome) is released, or the ADRs it blocks are explicitly deferred; the freeze rule is announced; the working tree has no uncommitted change under `docs/adr/`. Run `100-110-survey-adrs.sh` without options: its table must show no ADR classified `needs-judgment`; ADRs classified `blocked-by-247` are converted only after the prerequisite.

### Step 2: Survey and freeze the manifest

Run `100-110-survey-adrs.sh --write`. The table shows, per ADR, the class (`clean`, `blocked-by-247`, `needs-judgment`), the status, the `decision-makers` value, the derived `Source`, the number of bare-token runs to wrap, the applied defaults, and supersession links; the script also flags ADRs naming several issues (the first-mentioned issue is used) and unknown `decision-makers` elements. Commit the manifest. An existing manifest is never overwritten without `--force`.

### Step 3: Map the frontmatter

The script writes the YAML frontmatter with exactly these keys, in this order:

| DEC key | Rule |
| --- | --- |
| `classification` | `null` |
| `created` | first-commit date of the ADR file (manifest), full ISO 8601 with `.000` milliseconds and the committer's offset |
| `id` | the ADR `id` verbatim |
| `status` | the ADR status; for `superseded by <uuid2>` the value `superseded` |
| `type` | the literal `dec` |
| `updated` | last-commit date of the ADR file (manifest); the ADR `date` key is not used |
| `version` | `1.0.0` |

The ADR keys `decision-makers`, `consulted`, and `informed` are not carried into the frontmatter.

### Step 4: Transform the body

Everything not listed here passes through unchanged, in order: `# {title}`, `## Context and Problem Statement`, `## Decision Drivers`, `## Considered Options`, `## Decision Outcome` (lead prose and `### Consequences`/`### Confirmation`), `## More Information`. The mechanical changes are:

1. Wrap each bare `<token>` run (for example `<d>`, `get_<d>_schema`, `docs/<type>/`) outside fenced code and existing code spans in a code span, because the DEC parser rejects raw HTML. The wrapped runs are recorded in the manifest; a title containing one changes by the backticks only.
2. Rename `## Pros and Cons of the Options` to `## Pros and Cons`; the `### Option N: {title}` entries stay unchanged.
3. Insert `## Roles and Responsibilities` at the boundary immediately after the `## Decision Outcome` section (before the next `## ` heading, or at the end if there is none): `### Accountable` is the single paragraph `dfch` for every ADR; `### Responsible` is a bullet list with one bullet per element of the ADR `decision-makers` value split on ` + `, where the element `user decision` is replaced by `dfch` and duplicates are removed (`dfch` gives `dfch`; `OpenCode agent + user decision` gives `OpenCode agent` and `dfch`); an ADR without `decision-makers` gets the single bullet `dfch`, recorded in the manifest as the applied default `decision-makers`; an element that is neither `dfch`, `OpenCode agent`, nor `user decision` is reported as `unknown_makers` and needs a decision before conversion.
4. Insert `## Source` right after it: a single line `GitHub issue #NN` when the ADR's `## Context and Problem Statement` names a GitHub issue (the first-mentioned issue if several), otherwise `dfch` (recorded as the applied default `source`).
5. For a superseding DEC (the survey's `supersedes` list), insert `## Related Artifacts` after `## Source`, with a `### Decisions` sub-section holding one bullet `- DEC <older uuid>: <older title>` per superseded ADR. The superseded DEC carries no reference to its superseder.
6. Append `## Updates` as the last section with exactly one entry: the heading `### {updated} - Converted from ADR`, dated equal to the frontmatter `updated`, followed by the lead paragraph `Converted from ADR {uuid} per the "Convert an ADR to a DEC" SOP (GitHub issue #46).`

The resulting section order is the one the `dec` parser enforces: `# {title}` → `## Context and Problem Statement` → `## Decision Drivers` → `## Considered Options` → `## Decision Outcome` → `## Roles and Responsibilities` → `## Source` → `## Related Artifacts` → `## Pros and Cons` → `## More Information` → `## Updates`, with absent sections omitted.

### Step 5: Convert (dry run, then write)

Run `200-110-convert-adr.sh <uuid-or-prefix>...` (or `--all`) for the dry run: one verdict per ADR from the real `parse_dec`; add `--show` with a single ADR to print the candidate. Exit code 0 means every selected ADR converts, 1 means at least one is blocked by #247, 2 means at least one needs judgment. Review the dry-run output of the first ADR of each kind (clean, with wrapped tokens, superseding, superseded, blocked) before writing. Then run the same command with `--write`: it writes `docs/dec/<uuid>-<slug>.md` host-native (creating `docs/dec/` if needed), only for candidates that parse. No specmgr tool can create a DEC with a caller-chosen id (`create_dec` always assigns a fresh UUID), which is why the write is host-native.

### Step 6: Gate 1 - verify the converted documents

Run `200-120-verify-converted.sh`. It must report zero failing documents. Per DEC it checks: file name equals the ADR file name; the document parses; frontmatter `id`, `type`, `status`, `created`, `updated`, and `version` equal the manifest; the H1 equals the ADR title (modulo wrapped tokens); the migration `## Updates` entry is dated equal to `updated`; fidelity (undoing exactly the Step 4 changes reproduces the ADR body, compared after trailing-whitespace and blank-run normalisation); the supersession rule; and finally `specmgr lint --type dec` over all DECs. Pending ADRs are listed but are not failures; `--require-all` turns them into failures and is the final gate of the rollout.

### Step 7: Gate 2 - read-back through the MCP tools

For the first converted DEC of each kind, call `get_dec(<uuid>)`: it must return a parsed document (not a parse-failure result) with the expected H1, `id`, and `status`. Call `list_dec`: every converted row must be healthy (real title and status, no `<failed to parse>` marker) and `error_count` must be `0`. Read-only tools do not change `updated`.

### Step 8: Gate 3 - supersession (superseding documents only)

For each superseding DEC call `list_references(type="dec", id="<uuid>")`: the row for the superseded DEC must resolve with non-null `title` and `path`. Both documents are written by Step 5 independently of order, so the gate may run once both exist.

### Step 9: Record deviations

Applied defaults (`decision-makers`, `source`), the multi-issue flag, and any wrapped title are recorded in the manifest by the survey; nothing is appended to this SOP per document. A conversion needing a human judgment is recorded as a decision in the feat-46 plan and as a new script rule. The final state of the rollout is the green output of `200-120-verify-converted.sh --require-all`.

## More Information

The DEC body schema covers every ADR body section; with the Decision Outcome relaxation of GitHub issue #247 no ADR needs a content rewrite. A corpus survey of 2026-11-01 (46 ADRs, the manifest holds the authoritative per-ADR values) found: `date` in 25 (not used), `decision-makers` in 41 (26 `dfch`, 15 `OpenCode agent + user decision`, 5 absent), `## Pros and Cons of the Options` in 28, bare `<token>` runs in 13 ADRs (26 runs), a GitHub issue named in Context in 20 (4 name several), `status: superseded by <uuid>` in 1 (`a156fdf9-052c-4f43-93a2-eeec04a91eac`, superseded by `92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c`), and a multi-block `## Decision Outcome` in 20 (classified `blocked-by-247`; the other 26 convert and parse today). Seven other ADRs contain the words "superseded by" in prose; only the frontmatter status counts. Lessons from the pilot: bare `<token>` runs must be wrapped as whole whitespace-delimited runs (a lone `<d>` inside `get_<d>_schema` would leave the identifier split), and the trial must run through the real `parse_dec` because an ADR's own parse says nothing about DEC acceptance.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-11-01T07:28:30.000+01:00 - Revised for script-assisted conversion

Revised after a trial conversion of all 46 ADRs through the real `parse_dec` showed that the original "verbatim, no schema change" premise did not hold: 20 ADRs fail on the multi-block Decision Outcome (resolved by GitHub issue #247) and 13 carry bare `<token>` runs that the DEC parser rejects (resolved by wrapping). Supersession is now recorded on the superseding DEC only, `created`/`updated` come from the ADR file's git history frozen in a manifest, the Accountable value is `dfch` for every ADR, the migration entry is dated equal to `updated`, conversion and verification are done by scripts, and deviations live in the manifest instead of this document.

### 2026-10-19T05:34:18.000Z - Created

SOP drafted for GitHub issue #46 ("Remove adr artifact type"), after the ADR → DEC field gap analysis concluded that no `dec` schema change is required: supersession is recorded as a back-reference (DEC `status: superseded` plus a `### Decisions` bullet), UUID reuse keeps every existing reference valid, and the host-native write in Step 5 is necessary because `create_dec` assigns a fresh UUID. Pilots and the rollout over the remaining ADR set are out of scope for this creation.
