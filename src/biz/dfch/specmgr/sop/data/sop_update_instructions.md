You are revising an existing Standard Operating Procedure (SOP) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below. `sop` has no
per-domain `update_sop`/`set_status_sop` tools: every body change goes
through the generic `update` tool called with `type="sop"`, and every
status change goes through the generic `set_status` tool called with
`type="sop"`.

## 1. Read current state first

Call `get_sop(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which sections are present and which are empty

Show the user which of the sections -- the mandatory `## Purpose` and
`## Procedure` (always present), and the optional `## Scope`, `##
Definitions`, `## Roles and Responsibilities`, `## Safety and
Precautions`, `## Related Artifacts`, `## More Information`, `##
Updates` -- are already present with content and which are still
absent. Use the `question` tool to ask which ones (if any) they want to
add to or revise.

## 4. Read the RASCI role definitions before revising `## Roles and Responsibilities`

If the requested change touches `## Roles and Responsibilities` (adding
it, or editing the existing RASCI assignment), fetch the cross-cutting
`specmgr://rasci` resource first and read the generic RASCI
(Responsible/Accountable/Support/Consulted/Informed) role definitions.
The `sop` schema does not duplicate those definitions -- use the
resource as the single source of truth for what each role means, then
map the SOP's actual people/teams onto the five roles following the
binding sub-section order (Accountable, Responsible, Support, Consulted,
Informed) and the structural rules (Accountable is a single paragraph;
Responsible needs at least one bullet; Support/Consulted/Informed may
each be present with zero items). Skip this step if the change does not
touch the roles section.

## 5. Map the requested change to the right tool

- A change to the body -- the `purpose`, `scope`, `definitions`,
  `roles_and_responsibilities` (Accountable/Responsible/Support/
  Consulted/Informed), `safety_and_precautions`, `procedure` steps,
  `related_artifacts` sub-lists, `more_information`, or `updates`
  entries -- -> the generic `update` tool called with `type="sop"`: a
  **line-range replace** for a localized change, or a **whole-body
  replace** otherwise. `content` is body markdown only (no frontmatter
  block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_sop(id, raw=True)` to see the exact
    body text, identify the 1-based line to start at and how many lines
    to replace -- `offset` is the first body line, `limit` the number of
    lines (`offset`..`offset+limit-1`); `limit` omitted replaces through
    the last body line, `limit=0` is a pure insert, and the `N+1`
    position is end-of-body: `offset = N+1` appends after the last line
    -- and call `update(id, type="sop", content, offset=..., limit=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call
    `update(id, type="sop", content)` with no `offset`/`limit` --
    `content` is then the full replacement body: read the current body
    first (step 1) and carry forward every section you are not
    intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="sop", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, review, approved, active, retired. Mention this as a
  separate, optional follow-up -- e.g. `review` once the draft is ready
  for sign-off, `approved` once it has been signed off, `active` once it
  is in force and staff must follow it, `retired` once it is no longer
  in force and kept only for reference -- do not call `set_status`
  unless the user actually asks for a status change.

## 6. Check the schema, and validate before writing if useful

Fetch `specmgr://sop/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_sop(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.
