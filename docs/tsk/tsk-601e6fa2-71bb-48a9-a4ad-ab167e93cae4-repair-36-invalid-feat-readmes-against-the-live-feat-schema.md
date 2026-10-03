---
classification: null
created: '2026-09-27T18:26:32.253+02:00'
id: 601e6fa2-71bb-48a9-a4ad-ab167e93cae4
status: active
type: tsk
updated: '2026-10-01T07:15:00.000Z'
version: 1.0.0
---

# Repair 36 Invalid FEAT READMEs Against the Live feat Schema (0.33.0)

<!-- Inventory + repair tracker for the 36 feat READMEs under .specmgr/feat/ that fail to parse against the live specmgr MCP server v0.33.0 feat schema (list_feat error_count=36 of 62, inventoried 2026-09-27). One task per document; body line numbers are 1-based into the frontmatter-stripped body at inventory time. Tasks 7, 16, 24, 25, 29 are structural (class G) and deferred pending a decision on where misplaced content belongs; the other 31 are mechanical (classes A-F) and are repaired sequentially, one fresh sub-agent per README. -->

- [x] Task 1: Repair feat-10-add-artifact-type-tasklist — soft-wrapped REQ item (body line 19)
- [x] Task 2: Repair feat-103-set-status-error — soft-wrapped ACC item (body line 34)
- [x] Task 3: Repair feat-107-doc-cache — REQ-007 parenthetical before colon (body line 20)
- [x] Task 4: Repair feat-110-truncate-validation-errors — Updates entries not newest-first
- [x] Task 5: Repair feat-12-qa-artifact — soft-wrapped REQ item (body line 18)
- [x] Task 6: Repair feat-13-list-paging — soft-wrapped REQ item (body line 20)
- [ ] Task 7: Repair feat-132-prb-update — blockquote inside Updates (body line 331) (deferred, structural)
- [x] Task 8: Repair feat-14-qa-v2-adjacent-qa — soft-wrapped REQ item (body line 34)
- [x] Task 9: Repair feat-15-add-artifact-type-risk — soft-wrapped REQ item (body line 18)
- [x] Task 10: Repair feat-16-problem-statement — soft-wrapped REQ item (body line 28)
- [x] Task 11: Repair feat-18-goal — soft-wrapped REQ item (body line 23)
- [x] Task 12: Repair feat-21-decision — ACC-001 (REQ-001) parenthetical before colon (body line 22)
- [x] Task 13: Repair feat-22-consolidate-mutation-tools — soft-wrapped REQ item (body line 33)
- [x] Task 14: Repair feat-27-validation — Updates entry heading level and separator (body line 124)
- [x] Task 15: Repair feat-28-get-update — Updates entry heading level, separator, missing time (body line 207)
- [ ] Task 16: Repair feat-29-dec-source-roles — missing Task List heading (body line 102) (deferred, structural)
- [x] Task 17: Repair feat-30-sop — soft-wrapped REQ item (body line 19)
- [x] Task 18: Repair feat-31-feature — raw HTML token (body line 2167)
- [x] Task 19: Repair feat-32-sysrs — soft-wrapped REQ item (body line 21)
- [x] Task 20: Repair feat-33-vcr — soft-wrapped REQ item (body line 21)
- [x] Task 21: Repair feat-4-use-cases — bold paragraph instead of Included heading (body line 24)
- [x] Task 22: Repair feat-40-docs-prune — soft-wrapped REQ item (body line 23)
- [x] Task 23: Repair feat-48-feat-id — Updates entry heading level and separator (body line 138)
- [ ] Task 24: Repair feat-5-md-model-parser — note paragraph where REQ list expected (body line 26) (deferred, structural)
- [ ] Task 25: Repair feat-50-confluence — prose paragraph inside a Phase (body line 162) (deferred, structural)
- [x] Task 26: Repair feat-51-mcp-cwd — Updates entry heading level, separator, missing time (body line 71)
- [x] Task 27: Repair feat-56-classification-attribute-in-frontmatter — Updates entry heading level and separator (body line 178)
- [x] Task 28: Repair feat-57-uc-commands — Updates entry heading level and separator (body line 115)
- [ ] Task 29: Repair feat-6-requirement-artifact — checkbox prefix on REQ-001 item (body line 8) (deferred, structural)
- [x] Task 30: Repair feat-69-update-context — raw HTML token (body line 393)
- [x] Task 31: Repair feat-7-various-improvements — raw HTML token (body line 756)
- [x] Task 32: Repair feat-8-coverage-badge — bold paragraph instead of Included heading (body line 33)
- [x] Task 33: Repair feat-81-83-validation — REQ-009 parenthetical before colon (body line 24)
- [x] Task 34: Repair feat-9-doc-in-specmgr — bold paragraph instead of Included heading (body line 32)
- [x] Task 35: Repair feat-92-resources — soft-wrapped Task item (body line 112)
- [x] Task 36: Repair feat-94-frontmatter-schema — Updates entry heading level, missing time (body line 129)

## Recent Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-10-01 07:15:00.000Z - Session 2 closeout: 21 of the 26 open tasks complete; 4 structural docs remain (tasks 7, 16, 24, 25)

Session continued per the 2026-09-29 handoff (both TSKs read, feat-numbering skill loaded). Completed: (1) the 34-doc renumbering-only wave by script -- tracked in sibling tsk-2687d267 as Tasks 34-65 plus its Tasks 27/29, convention per the feat-18 worked example (NNN = 100+10*(phase-1), MMM = 100+10*(task-1), phase-0 docs positional, non-numeric/3-part labels positional, prose cross-references left legacy, plus 14 parenthetical-annotation task items fixed by moving the annotation after the colon per feat-134's own precedent); (2) the 21 structural repairs above -- doc-repairer sub-agents (one per doc, sequential) for the old full-shape documents (feat-6, feat-4, feat-8, feat-9, feat-21, feat-22, feat-30, feat-32) and targeted scripted fixes for the mechanical defect classes (em-dash entry-heading separators, date-only entry headings synthesized with order-preserving timestamps, 6-digit-microsecond truncation to .fff, entry bodies reflowed to exactly one lead paragraph, decision bullets converted to entries, soft-wrapped REQ/ACC items joined with parentheticals moved after the colon, Scope/Dependencies bold lead-ins to the mandatory H4s, Related ADRs to Related Decisions, Recent Updates to Updates, Task List intro/Note paragraphs relocated to Design Notes, bare raw-HTML tokens code-spanned, `* [x]`-bullet task item renumbered in-between). All 21 verified live: specmgr_list_feat error_count 60 -> 4 (note: 3 new feat docs -- feat-162-doc-cache-exception-footer, feat-177-list-ref-feat, feat-180-updates -- were created mid-session by other work and parse clean; fleet total 68). The 4 remaining docs are the previously-deferred structural ones (de-parked 2026-09-30); each has exactly one determined fix, no open judgment: Task 7 feat-132-prb-update -- a blockquote note inside `### Updates` (normalized line 331, `> **Note (Task 6.2, REQ-017, added 2026-09-19):** the five entries below dated ...`): strip the `> ` markers, join the note into one prose paragraph, and prepend it to the lead paragraph of the first entry it introduces (the first of the five 2026-09-19 entries), every word preserved. Task 16 feat-29-dec-source-roles -- `### Known Limitations` (normalized line 102) is an unknown `## Plan` H3 sitting before `### Task List`: fold its content into `### Design Notes` (keep "Known Limitations" as a bold lead-in), every word preserved. Task 24 feat-5-md-model-parser -- `### Requirements` starts with the `**Note (2026-08-11 reconciliation):**` prose paragraph (normalized line 26): move it verbatim into `### Design Notes`; also relocate the two non-task lines in the Task List (the struck-through `- [x] ~~Task 1.5: ...~~ -- **removed 2026-08-11**` line and the `- **Note (rescoped 2026-08-11):** ...` line) into Design Notes as prose. Task 25 feat-50-confluence -- a prose paragraph inside `#### Phase 100` (normalized line 162, "A post-completion, real-instance follow-up test ..."): move it verbatim into `### Design Notes` (or `### More Information`). Next session: read this TSK + tsk-2687d267, load the feat-numbering skill, apply the four fixes, verify specmgr_get_feat + specmgr_list_feat error_count 0 across all docs, check off the remaining tasks here and tasks 19/20 in tsk-2687d267, then set both TSKs status to done. No git commit was run in this wave -- every change is an uncommitted working-tree edit.

### 2026-09-30 05:47:02.000Z - Session started per the 2026-09-29 handoff; 34-doc renumbering wave done; 26 structural docs being repaired one sub-agent at a time

Read both TSKs, loaded the feat-numbering skill, confirmed live state (65 feat docs, 60 failing), and completed the 34-doc renumbering-only wave with a script scoped strictly to each doc's `### Task List` section: `#### Phase N:` -> `#### Phase NNN:` and `Task X.M:` -> `Task NNN.MMM:` per the feat-18 worked example (NNN = 100+10*(phase-1), MMM = 100+10*(task-1); docs whose first phase is `Phase 0` map positionally so the first phase is `Phase 100`; non-numeric labels like `Task 1a.8` and 3-part labels like `Task 3.1.1` fall back to document-order positional numbering), every prose cross-reference left legacy per feat-163's no-migration policy, plus a second script pass that fixed 14 task items carrying a parenthetical annotation between the label and the colon by moving the annotation to directly after the colon (precedent: feat-134's own `Task 160.160: (Added after author review 2026-09-28, ...) ...`). Wave verified clean by the repo's own `parse_feat` and by the live server (`specmgr_list_feat`: 60 -> 26 failing); tracked in tsk-2687d267 as Tasks 34-65 (plus its already-existing Tasks 27/29 for feat-73-74-76/feat-80-feat-id, which only ever needed renumbering and are now closed there). This TSK's open tasks 1-6/8-11 docs (feat-10, feat-103, feat-107, feat-110, feat-12, feat-13, feat-14, feat-15, feat-16) are therefore fully done; the 26 open tasks (7, 12-36) each still need their listed structural fix -- their Task Lists are already renumbered, so no numbering work remains. The 5 previously-deferred structural tasks (7, 16, 24, 25, 29) are de-parked as part of this wave: the 2026-09-29 verification gate (error_count 0 across all 65) requires them, and the fix for each is fully determined by the schema (relocate the misplaced content, preserve every word) -- no further decision is outstanding. Repair proceeds sequentially, one fresh doc-repairer sub-agent per README, checking tasks off as each verifies clean against the live server.

### 2026-09-29 21:40:46.000Z - Live server upgraded to 3-digit feat numbering (feat-163); scope reassessed, handoff for fresh session

The specmgr MCP was reloaded on the v0.34.0-generation schema (feat-163 'FEAT Phase/Task Numbering Scheme', commit 14b2517): the feat TaskList now requires '#### Phase NNN: {title}' headings (3-digit) and 'Task NNN.MMM: ' item prefixes, enforced per the feat-numbering skill (start 100, step 10, permanent numbers). New specmgr_list_feat against the live server: 65 feat docs, 60 failing. Consequences: (1) 9 of this TSK's 10 structurally-migrated docs (tasks 1-6, 8-11 minus feat-18) now fail on numbering alone and need the Phase NNN / Task NNN.MMM renumbering; feat-18 (task 11) was migrated already renumbered and is the only doc from this TSK that parses on the new server. (2) The 26 open tasks (12-36) now need structural migration PLUS 3-digit renumbering. (3) 34 further docs that were valid under v0.33.0 (25 previously-valid + the 9 above) fail numbering-only; they are not tracked by this TSK's 36 tasks. Coordination: the feat-163 follow-up TSK tsk-2687d267-b1f7-4bf6-96f1-2bbf70e19b84 ('Fix Remaining feat-* README.md Documents to Validate Against the Current FEAT Schema') carries the how-to method (required shape incl. 3-digit numbering, why direct file read/write instead of specmgr_update, the validate loop) and tracks 33 of the structural docs; a cross-entry was posted there too. Handoff for a fresh session: read both TSKs, load the feat-numbering skill, then work the 26 open tasks here (structural + renumber, one fresh sub-agent per doc, sequential) and the 34 renumbering-only wave (per tsk-2687d267). Verification gate: specmgr_list_feat error_count 0 across all 65.

### 2026-09-27 16:22:15.000Z - Created

Inventoried 62 feat documents via list_feat against the live specmgr MCP server v0.33.0; 36 fail to parse (error_count=36). The 31 mechanical failures (soft-wrapped list items, parenthetical-before-colon markers, raw HTML tokens, malformed Updates entry headings, out-of-order Updates, bold paragraphs instead of Scope H4 headings) are repaired sequentially, one fresh sub-agent per README. The 5 structural failures (tasks 7, 16, 24, 25, 29) are deferred pending a decision on where misplaced content belongs.
