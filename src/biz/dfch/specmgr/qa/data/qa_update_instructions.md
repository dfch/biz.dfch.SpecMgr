You are revising an existing Question and Answer (QA) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_qa` -- every change to the
document goes through the specmgr MCP tools listed below.

## 1. Read current state first
Call `get_qa(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified
If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Map the requested change to the right tool
- A change to the body -- the introduction, raw requirements, any of the
  ten fixed category sections (`Elicitation Context` -- QA-schema-specific,
  not one of the ISO/IEC 25010:2023 characteristics -- plus the nine
  ISO/IEC 25010:2023 category sections themselves: `Functional
  Suitability`, `Performance Efficiency`, `Compatibility`, `Interaction
  Capability`, `Reliability`, `Security`, `Maintainability`,
  `Flexibility`, `Safety`), a Q&A pair's `comment`/`question`/`answer`, or
  `more_information` -- -> `update_qa(id, content)`. `content` is body
  markdown only (no frontmatter block) and is a **whole-body replace**:
  read the current body first (step 1) and carry forward every section you
  are not intentionally changing, or it will be dropped, including the
  ten fixed category headings even when you have nothing new to add
  under a given one. `id`/`type`/`status`/`created`/`version` are
  preserved automatically regardless of what you submit; only `updated`
  changes.
- A change to `status` -> `set_status_qa(id, status)` instead --
  `update_qa` never accepts or changes `status`. `status` must be one
  of: draft, active, done, cancelled.

## 4. Check the schema, and validate before writing if useful
Fetch `specmgr://qa/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_qa(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update_qa` already performs the same
validation internally, so this step is never required, only a
convenience.
